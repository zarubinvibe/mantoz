#!/bin/sh
# Пробы выбора sandbox-бэкенда (T03). Вне paths исполнителя: свой гейт он ослабить не может.
# У каждой отрицательной пробы есть положительный контроль.
set -e

d=$(mktemp -d)
fail() { echo "ПРОБА ПРОВАЛЕНА: $1"; exit 1; }

# 1. Дефолт без конфига - бесплатный self-hosted docker, не платный сервис.
out=$(uv run python -m mantoz.sandbox --show 2>&1) || fail "показ дефолтного бэкенда упал: $out"
echo "$out" | grep -qi docker || fail "дефолт не docker, а '$out' - бесплатный вариант обязан быть дефолтом"
echo "$out" | grep -qi modal && fail "дефолт указывает на платный modal"

# 2. Положительный контроль: явный docker реально гоняет задачу через Harbor.
MANTOZ_SANDBOX=docker uv run python -m mantoz.smoke_harbor >/dev/null 2>&1 || fail "явный docker не отработал живой прогон"

# 3. Неизвестное имя бэкенда - отказ fail-closed, не молчаливый docker.
if MANTOZ_SANDBOX=выдумка uv run python -m mantoz.sandbox --show >/dev/null 2>&1; then
  fail "неизвестный бэкенд принят вместо отказа"
fi

# 4. modal без учетки - отказ, называющий причину; НЕ тихий откат на docker.
out=$(MANTOZ_SANDBOX=modal uv run python -m mantoz.sandbox --show 2>&1) && rc=0 || rc=$?
[ "$rc" -ne 0 ] || fail "modal без учетной записи не дал отказа (вероятен тихий откат)"
echo "$out" | grep -qi modal || fail "отказ не называет modal: '$out'"
echo "$out" | grep -qiE "учет|credential|token|ключ" || fail "отказ не называет причину (нет учетных данных): '$out'"
echo "$out" | grep -qi "docker" && fail "в отказе упомянут docker - похоже на тихий откат"

# 5. Положительный контроль к пробе 4: modal разрешается как ИМЯ бэкенда, а не отвергается как неизвестный.
#    Отказ обязан отличаться от отказа пробы 3 (неизвестное имя).
out3=$(MANTOZ_SANDBOX=выдумка uv run python -m mantoz.sandbox --show 2>&1 || true)
[ "$out" != "$out3" ] || fail "modal и выдуманное имя дают одинаковый отказ - modal не зарегистрирован как бэкенд"

echo "пробы бэкенда: 5/5 ok"
