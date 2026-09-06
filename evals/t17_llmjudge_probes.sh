#!/bin/sh
# Пробы LLM-judge верификатора (T17). Вне paths исполнителя.
# Строим лучше оригинала: у MatrAIx один вызов судьи без сохранения сырого ответа
# и без замера расхождения между судьями - аудит назвал это незащитимым при споре.
set -e

fail() { echo "ПРОБА ПРОВАЛЕНА: $1"; exit 1; }
d=$(mktemp -d)

# 1. Контракт задачи со свободным ответом на месте.
[ -f application/tasks/open-answer/task.toml ] || fail "нет контракта задачи со свободным ответом"
ls application/tasks/open-answer/tests/* >/dev/null 2>&1 || fail "нет верификатора задачи"

# 2. Детерминированный режим судьи работает без сети и без ключей (дефолт).
uv run python -m mantoz.judge verify --answer "Кофе горький, потому что в нём кофеин и хлорогеновые кислоты" \
  --rubric application/tasks/open-answer/rubric.yaml --out "$d/ok.json" >/dev/null 2>&1 \
  || fail "судья не отработал в детерминированном режиме"

# 3. Вердикт машиночитаемый: оценка, обоснование, и СЫРОЙ ответ судьи сохранён.
python3 -c "
import json
r=json.load(open('$d/ok.json'))
for k in ('score','rationale','raw'):
    assert r.get(k) is not None, f'в вердикте нет поля {k}'
assert isinstance(r['score'],(int,float)), 'оценка не число'
assert r['raw'], 'сырой ответ судьи не сохранён - вердикт неоспорим постфактум'
" || fail "вердикт судьи неполон"

# 4. Судья различает хороший и явно негодный ответ.
uv run python -m mantoz.judge verify --answer "не знаю" \
  --rubric application/tasks/open-answer/rubric.yaml --out "$d/bad.json" >/dev/null 2>&1
python3 -c "
import json
a=json.load(open('$d/ok.json')); b=json.load(open('$d/bad.json'))
assert b['score'] < a['score'], f\"негодный ответ получил не меньшую оценку ({b['score']} против {a['score']})\"
" || fail "судья не различает годный и негодный ответ"

# 5. ЛУЧШЕ ОРИГИНАЛА: судей минимум два, расхождение измеряется и попадает в вердикт.
python3 -c "
import json
r=json.load(open('$d/ok.json'))
j=r.get('judges')
assert j and len(j)>=2, f'судей {len(j) if j else 0} - у MatrAIx один вызов без второго мнения, мы обязаны быть строже'
assert r.get('disagreement') is not None, 'расхождение между судьями не измерено'
" || fail "нет второго судьи или замера расхождения"

# 6. Расхождение не прячется: при разошедшихся судьях это видно в вердикте.
uv run python -m mantoz.judge verify --answer "Кофе горький" --rubric application/tasks/open-answer/rubric.yaml \
  --simulate-disagreement --out "$d/dis.json" >/dev/null 2>&1 \
  || fail "режим проверки расхождения не отработал"
python3 -c "
import json
r=json.load(open('$d/dis.json'))
assert r['disagreement'] > 0, 'расхождение симулировано, но в вердикте ноль - оно теряется'
" || fail "расхождение судей теряется в вердикте"

# 7. Задача со свободным ответом проходит population-прогон.
uv run python -m mantoz.population run --n-runs 4 --seed 5 --task open-answer --out "$d/pop.json" >/dev/null 2>&1 \
  || fail "population-прогон по задаче со свободным ответом не отработал"

# 8. Платный вызов модели не становится дефолтом (правило владельца).
grep -qiE "default.*(gpt|claude|anthropic|openai)|model *= *[\"'](gpt|claude)" src/mantoz/judge.py 2>/dev/null \
  && fail "платная модель зашита дефолтом - детерминированный режим обязан быть дефолтом"

echo "пробы LLM-judge: 8/8 ok"
