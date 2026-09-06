#!/bin/sh
# Пробы среды Survey (T11). Вне paths исполнителя.
# Суть: персона обязана ВЛИЯТЬ на ответы, иначе population-разбивка бессмысленна.
set -e

fail() { echo "ПРОБА ПРОВАЛЕНА: $1"; exit 1; }
d=$(mktemp -d)

# 1. Контракт survey-задачи на месте, с анкетой.
[ -f application/tasks/survey-feedback/task.toml ] || fail "нет контракта survey-задачи"
[ -f application/tasks/survey-feedback/questionnaire.yaml ] || [ -f application/tasks/survey-feedback/input/questionnaire.yaml ] \
  || fail "нет анкеты questionnaire.yaml"
ls application/tasks/survey-feedback/tests/* >/dev/null 2>&1 || fail "нет верификатора survey-задачи"

# 2. Положительный контроль: прогон одной персоной даёт структурированные ответы.
uv run python -m mantoz.survey run --persona-seed 1 --out "$d/one.json" >/dev/null 2>&1 \
  || fail "прогон survey одной персоной не отработал"
python3 -c "
import json
r=json.load(open('$d/one.json'))
ans=r.get('answers') or r.get('responses')
assert ans, 'в результате нет ответов'
assert len(ans)>=3, f'ответов всего {len(ans)} - анкета вырождена'
" || fail "результат survey не содержит осмысленных ответов"

# 3. Верификатор судит ответы: полный набор проходит.
uv run python -m mantoz.survey verify --file "$d/one.json" >/dev/null 2>&1 \
  || fail "верификатор красный на честном результате"

# 4. Отрицательная сторона: результат с пропущенным ответом обязан краснеть.
python3 -c "
import json
r=json.load(open('$d/one.json'))
k='answers' if 'answers' in r else 'responses'
a=r[k]
if isinstance(a,dict): a.pop(list(a)[0])
else: a.pop()
json.dump(r,open('$d/bad.json','w'),ensure_ascii=False)
"
if uv run python -m mantoz.survey verify --file "$d/bad.json" >/dev/null 2>&1; then
  fail "верификатор принял неполную анкету"
fi

# 5. ГЛАВНОЕ: персона влияет на ответы. Разные персоны обязаны давать разные наборы.
uv run python -m mantoz.survey run --persona-seed 2 --out "$d/two.json" >/dev/null 2>&1
python3 -c "
import json
a=json.load(open('$d/one.json')); b=json.load(open('$d/two.json'))
ka='answers' if 'answers' in a else 'responses'
assert a[ka]!=b[ka], 'две разные персоны дали одинаковые ответы - персона ни на что не влияет'
" || fail "персона не влияет на ответы - population-разбивка была бы фикцией"

# 6. Population-прогон по среде даёт разброс, а не единицы во всех подгруппах.
uv run python -m mantoz.population run --n-runs 12 --seed 9 --task survey --out "$d/pop.json" >/dev/null 2>&1 \
  || fail "population-прогон по survey не отработал"
python3 -c "
import json
r=json.load(open('$d/pop.json'))
sb=r['subgroup_breakdown']
rates={(k if isinstance(sb,dict) else i):(v.get('pass_rate') if isinstance(v,dict) else None) for i,(k,v) in enumerate(sb.items() if isinstance(sb,dict) else enumerate(sb))}
vals=[v for v in rates.values() if v is not None]
assert vals, 'в разбивке нет pass_rate'
" || fail "population-отчёт по survey не несёт разбивки"

# 7. Задача самодостаточна для Harbor: анкета реально попадает в контейнер.
[ -f application/tasks/survey-feedback/environment/questionnaire.yaml ] \
  || grep -qE '^(COPY|ADD).*questionnaire' application/tasks/survey-feedback/environment/Dockerfile 2>/dev/null \
  || fail "анкеты нет в environment/ и Dockerfile её не копирует - в контейнере файла не будет"

# 8. Прогон идёт ЧЕРЕЗ Harbor, а не мимо: результат несёт след настоящего прогона.
python3 -c "
import json
r=json.load(open('$d/one.json'))
keys=set(r)
assert keys & {'trial_id','trial','agent','environment','harbor'}, \
    'в результате нет следа прогона Harbor - похоже, задача выполнена в своём процессе мимо песочницы'
" || fail "survey выполняется мимо Harbor"

# 9. Population по среде тоже идёт через задачу, а не зовёт функции напрямую.
grep -qE "answer_questionnaire|validate_answers" src/mantoz/population.py 2>/dev/null \
  && fail "population зовёт функции survey напрямую - настоящая задача и её верификатор не запускаются"

# 10. Настоящий исход верификатора из контейнера, а не наличие полей.
python3 -c "
import json
r=json.load(open('$d/one.json'))
v=r.get('reward', r.get('passed', r.get('verified')))
assert v is not None, 'нет исхода верификации - прогон в контейнере не судился'
assert v not in (False,0), f'исход верификации отрицательный ({v!r}) - задача в контейнере не отработала'
" || fail "нет доказанного исхода верификации из контейнера"

# 11. Образ пригоден для Harbor: bash есть (Harbor запускает команды через bash -c).
grep -qE "bash" application/tasks/survey-feedback/environment/Dockerfile \
  || fail "в Dockerfile нет bash, Harbor не сможет исполнить solve.sh"

# 12. Тихий откат запрещён: при нерабочем бэкенде прогон обязан падать.
MANTOZ_SANDBOX=выдумка uv run python -m mantoz.survey run --persona-seed 1 --out "$d/z.json" >/dev/null 2>&1 \
  && fail "при нерабочем бэкенде прогон успешен - есть тихий откат на локальный результат"

# 13. Population не заглатывает инфраструктурный сбой в статистику.
out=$(MANTOZ_SANDBOX=выдумка uv run python -m mantoz.population run --n-runs 4 --seed 1 --task survey --out "$d/pz.json" 2>&1) && rc=0 || rc=$?
[ "$rc" -ne 0 ] || fail "population при нерабочем бэкенде завершился успешно - сбой заглочен в pass_rate"

echo "пробы survey: 13/13 ok"
