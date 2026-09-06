#!/bin/sh
# Пробы калибровки верификатора (T04). Вне paths исполнителя.
# Суть: верификатор доказан только когда обе стороны проверены - эталон проходит, пустышка падает.
set -e

fail() { echo "ПРОБА ПРОВАЛЕНА: $1"; exit 1; }

# 1. Контракт задачи лежит на диске целиком.
[ -f application/tasks/smoke-choice/task.toml ] || fail "нет task.toml контракта задачи"
[ -f application/tasks/smoke-choice/instruction.md ] || fail "нет instruction.md"
ls application/tasks/smoke-choice/solution/solve.* >/dev/null 2>&1 || fail "нет эталонного решения в solution/"
ls application/tasks/smoke-choice/tests/* >/dev/null 2>&1 || fail "нет верификатора в tests/"

# 2. Положительная сторона: эталонное решение проходит верификатор.
uv run python -m mantoz.calibrate --agent oracle >/dev/null 2>&1 || fail "эталон (oracle) НЕ прошел верификатор - верификатор сломан или задача нерешаема"

# 3. Отрицательная сторона: пустышка не проходит.
if uv run python -m mantoz.calibrate --agent nop >/dev/null 2>&1; then
  fail "пустышка (nop) прошла верификатор - он принимает что угодно, калибровки нет"
fi

# 4. Отказ пустышки - именно вердикт верификатора, а не крах прогона.
out=$(uv run python -m mantoz.calibrate --agent nop 2>&1 || true)
echo "$out" | grep -qiE "verif|верифик|reward|провал|fail" || fail "отказ пустышки не назван вердиктом верификатора: '$out'"
echo "$out" | grep -qiE "traceback|exception|no such file" && fail "пустышка упала крахом, а не вердиктом: '$out'"

# 5. Обе стороны прогнаны в одном вызове и различены машиной.
out=$(uv run python -m mantoz.calibrate --both 2>&1) || fail "парный прогон --both не отработал: $out"
echo "$out" | grep -qi oracle || fail "в парном отчете нет строки про oracle"
echo "$out" | grep -qi nop || fail "в парном отчете нет строки про nop"

# 6. Верификатор судит строго: лишняя пустая строка - не тот ответ.
uv run python -m mantoz.calibrate --agent oracle --mutate-output-extra-blank >/dev/null 2>&1 \
  && fail "верификатор принял ответ с лишней пустой строкой - контракт неполон" || true

# 7. Прогон не зависит от рантайм-каталога .helioz (в свежем клоне его нет).
h=$(mktemp -d)/nohelioz
mkdir -p "$h" && cp -R src pyproject.toml application "$h/" 2>/dev/null || true
( cd "$h" && [ ! -d .helioz ] && uv run python -m mantoz.calibrate --agent oracle >/dev/null 2>&1 ) \
  || fail "калибровка не работает без каталога .helioz - завязана на рантайм-мусор"

echo "пробы калибровки: 7/7 ok"
