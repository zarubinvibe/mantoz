#!/bin/sh
# Пробы среды Chat (T12). Вне paths исполнителя.
# Включает три пробы сквозного пути через Harbor - класс дефекта, найденный судьёй на T11.
set -e

fail() { echo "ПРОБА ПРОВАЛЕНА: $1"; exit 1; }
d=$(mktemp -d)

# 1. Контракт chat-задачи на месте.
[ -f application/tasks/chat-support/task.toml ] || fail "нет контракта chat-задачи"
ls application/tasks/chat-support/tests/* >/dev/null 2>&1 || fail "нет верификатора chat-задачи"

# 2. Положительный контроль: прогон одной персоной даёт транскрипт диалога.
uv run python -m mantoz.chat run --persona-seed 1 --out "$d/one.json" >/dev/null 2>&1 \
  || fail "прогон chat одной персоной не отработал"
python3 -c "
import json
r=json.load(open('$d/one.json'))
t=r.get('transcript') or r.get('turns') or r.get('messages')
assert t, 'в результате нет транскрипта диалога'
assert len(t)>=3, f'реплик всего {len(t)} - диалог вырожден'
roles={(m.get('role') if isinstance(m,dict) else None) for m in t}
assert len(roles-{None})>=2, 'в транскрипте одна роль - это монолог, а не диалог'
" || fail "результат chat не содержит осмысленного диалога"

# 3. Верификатор судит исход диалога: полный транскрипт проходит.
uv run python -m mantoz.chat verify --file "$d/one.json" >/dev/null 2>&1 \
  || fail "верификатор красный на честном транскрипте"

# 4. Отрицательная сторона: обрезанный диалог обязан краснеть.
python3 -c "
import json
r=json.load(open('$d/one.json'))
k=[x for x in ('transcript','turns','messages') if x in r][0]
r[k]=r[k][:1]
json.dump(r,open('$d/bad.json','w'),ensure_ascii=False)
"
if uv run python -m mantoz.chat verify --file "$d/bad.json" >/dev/null 2>&1; then
  fail "верификатор принял оборванный диалог"
fi

# 5. Персона влияет на ход диалога: разные персоны - разные транскрипты.
uv run python -m mantoz.chat run --persona-seed 2 --out "$d/two.json" >/dev/null 2>&1
python3 -c "
import json
a=json.load(open('$d/one.json')); b=json.load(open('$d/two.json'))
k=[x for x in ('transcript','turns','messages') if x in a][0]
assert a[k]!=b[k], 'две разные персоны дали одинаковый диалог - персона ни на что не влияет'
" || fail "персона не влияет на диалог"

# 6. Задача самодостаточна для Harbor: материалы диалога попадают в контейнер.
ls application/tasks/chat-support/environment/* >/dev/null 2>&1 \
  || fail "в задаче нет каталога environment - Harbor не соберёт образ"

# 7. Прогон идёт ЧЕРЕЗ Harbor: в результате есть след настоящего прогона.
python3 -c "
import json
r=json.load(open('$d/one.json'))
assert set(r) & {'trial_id','trial','agent','environment','harbor'}, \
    'нет следа прогона Harbor - задача выполнена мимо песочницы'
" || fail "chat выполняется мимо Harbor"

# 8. Population по среде идёт через задачу, а не зовёт внутренности напрямую.
grep -qE "run_dialogue|validate_transcript|answer_questionnaire" src/mantoz/population.py 2>/dev/null \
  && fail "population зовёт внутренности среды напрямую - настоящая задача не запускается"

# 9. Population-прогон по chat даёт разбивку.
uv run python -m mantoz.population run --n-runs 12 --seed 9 --task chat --out "$d/pop.json" >/dev/null 2>&1 \
  || fail "population-прогон по chat не отработал"
python3 -c "
import json
r=json.load(open('$d/pop.json'))
assert r.get('subgroup_breakdown'), 'в отчёте нет разбивки по подгруппам'
assert r.get('n_runs')==12, 'n_runs в отчёте не совпадает с запрошенным'
" || fail "population-отчёт по chat неполон"

# 10. Прогон обязан нести НАСТОЯЩИЙ исход верификатора из контейнера, а не факт наличия полей.
python3 -c "
import json
r=json.load(open('$d/one.json'))
v=r.get('reward', r.get('passed', r.get('verified')))
assert v is not None, 'в результате нет исхода верификации (reward/passed) - прогон в контейнере не судился'
assert v not in (False,0), f'исход верификации отрицательный ({v!r}) - задача в контейнере не отработала'
" || fail "нет доказанного исхода верификации из контейнера"

# 11. Образ задачи пригоден для Harbor: bash есть (Harbor оборачивает команды в bash -c).
grep -qE "bash" application/tasks/chat-support/environment/Dockerfile \
  || fail "в Dockerfile задачи нет bash, а Harbor запускает команды через bash -c - solve.sh не стартует"

# 12. Тихий откат на локальный результат запрещён: при сломанном Harbor прогон обязан падать.
out=$(MANTOZ_SANDBOX=выдумка uv run python -m mantoz.chat run --persona-seed 1 --out "$d/z.json" 2>&1) && rc=0 || rc=$?
[ "$rc" -ne 0 ] || fail "при нерабочем бэкенде прогон завершился успешно - есть тихий откат на локальный результат"

echo "пробы chat: 12/12 ok"
