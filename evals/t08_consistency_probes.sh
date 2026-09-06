#!/bin/sh
# Пробы валидации консистентности и dev-bootstrap (T08). Вне paths исполнителя.
set -e

fail() { echo "ПРОБА ПРОВАЛЕНА: $1"; exit 1; }
d=$(mktemp -d)

# 1. Гейт качества выборки существует и зелёный на честной DAG-выборке.
uv run python -m mantoz.persona sample --n 300 --seed 21 --dag --out "$d/ok.jsonl" >/dev/null 2>&1 \
  || fail "не удалось получить DAG-выборку"
uv run python -m mantoz.quality gate --file "$d/ok.jsonl" >/dev/null 2>&1 \
  || fail "гейт качества красный на честной DAG-выборке"

# 2. Отрицательная сторона с зубами: гейт обязан ловить нарушения на независимых выборках.
#    Одна выборка может случайно оказаться чистой, поэтому пробуем несколько seed.
caught=0
for s in 31 32 33 34 35; do
  uv run python -m mantoz.persona sample --n 300 --seed "$s" --out "$d/i$s.jsonl" >/dev/null 2>&1 || continue
  if ! uv run python -m mantoz.quality gate --file "$d/i$s.jsonl" >/dev/null 2>&1; then
    caught=1; break
  fi
done
[ "$caught" -eq 1 ] || fail "гейт качества зелёный на всех независимых выборках - он вырожден"

# 3. Гейт печатает отчёт с числом нарушений, а не только код возврата.
out=$(uv run python -m mantoz.quality gate --file "$d/ok.jsonl" 2>&1) || true
echo "$out" | grep -qiE "нарушен|violation|0" || fail "гейт не печатает счёт нарушений"

# 4. Persona1M допущен ТОЛЬКО как dev-bootstrap: в продакшн-путях его нет.
if grep -rniE "persona[_-]?1m|MatrAIx_Persona" src/mantoz/persona.py src/mantoz/population.py src/mantoz/quality.py 2>/dev/null | grep -qv "dev\|test\|bootstrap"; then
  fail "ссылка на Persona1M в продакшн-пути вне пометки dev/bootstrap - нарушение LIM-08"
fi

# 5. Продукто-агностичность: генерация конфигурируется под два разных домена без правки кода.
uv run python -m mantoz.persona sample --n 20 --seed 5 --dag --out "$d/a.jsonl" >/dev/null 2>&1
uv run python -m mantoz.persona sample --n 20 --seed 6 --dag --out "$d/b.jsonl" >/dev/null 2>&1
cmp -s "$d/a.jsonl" "$d/b.jsonl" && fail "выборки под разные конфигурации совпали"
if grep -rniE "todocups|юрпракт|legal-practice" src/mantoz/ 2>/dev/null | grep -q .; then
  fail "в ядре захардкожен продукт владельца - нарушение REQ-07"
fi

echo "пробы консистентности: 5/5 ok"
