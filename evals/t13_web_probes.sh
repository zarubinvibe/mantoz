#!/bin/sh
# Пробы среды Web (T13). Вне paths исполнителя.
# Несёт оба класса дефектов, найденных судьями на T11 и T12:
# работа мимо песочницы (пробы 6-8) и отсутствие настоящего исхода из контейнера (10-12).
set -e

fail() { echo "ПРОБА ПРОВАЛЕНА: $1"; exit 1; }
d=$(mktemp -d)

# 1. Контракт web-задачи на месте.
[ -f application/tasks/web-choice/task.toml ] || fail "нет контракта web-задачи"
ls application/tasks/web-choice/tests/* >/dev/null 2>&1 || fail "нет верификатора web-задачи"

# 2. Положительный контроль: прогон персоной даёт след действий и итоговое решение.
uv run python -m mantoz.web run --persona-seed 1 --out "$d/one.json" >/dev/null 2>&1 \
  || fail "прогон web одной персоной не отработал"
python3 -c "
import json
r=json.load(open('$d/one.json'))
acts=r.get('actions') or r.get('trace') or r.get('steps')
assert acts, 'нет следа действий в браузере'
assert len(acts)>=2, f'действий всего {len(acts)} - сценарий вырожден'
assert r.get('decision') is not None or r.get('choice') is not None, 'нет итогового решения персоны'
" || fail "результат web не содержит следа действий и решения"

# 3. Верификатор принимает честный результат.
uv run python -m mantoz.web verify --file "$d/one.json" >/dev/null 2>&1 \
  || fail "верификатор красный на честном результате"

# 4. Отрицательная сторона: результат без решения обязан краснеть.
python3 -c "
import json
r=json.load(open('$d/one.json'))
r.pop('decision',None); r.pop('choice',None)
json.dump(r,open('$d/bad.json','w'),ensure_ascii=False)
"
if uv run python -m mantoz.web verify --file "$d/bad.json" >/dev/null 2>&1; then
  fail "верификатор принял результат без решения"
fi

# 5. Персона влияет на выбор: разные персоны - разные решения или следы.
uv run python -m mantoz.web run --persona-seed 2 --out "$d/two.json" >/dev/null 2>&1
python3 -c "
import json
a=json.load(open('$d/one.json')); b=json.load(open('$d/two.json'))
same = a.get('decision')==b.get('decision') and a.get('choice')==b.get('choice') \
       and (a.get('actions') or a.get('trace'))==(b.get('actions') or b.get('trace'))
assert not same, 'две разные персоны дали одинаковый результат - персона ни на что не влияет'
" || fail "персона не влияет на поведение в браузере"

# 6. Задача самодостаточна для Harbor.
ls application/tasks/web-choice/environment/* >/dev/null 2>&1 \
  || fail "нет каталога environment - Harbor не соберёт образ"

# 7. Прогон идёт через Harbor: в результате след настоящего прогона.
python3 -c "
import json
r=json.load(open('$d/one.json'))
assert set(r) & {'trial_id','trial','agent','environment','harbor'}, 'нет следа прогона Harbor'
" || fail "web выполняется мимо Harbor"

# 8. Population не зовёт внутренности среды напрямую.
grep -qE "run_browser|validate_actions|answer_questionnaire|run_dialogue" src/mantoz/population.py 2>/dev/null \
  && fail "population зовёт внутренности среды напрямую"

# 9. Population-прогон по web даёт разбивку.
uv run python -m mantoz.population run --n-runs 8 --seed 9 --task web --out "$d/pop.json" >/dev/null 2>&1 \
  || fail "population-прогон по web не отработал"
python3 -c "
import json
r=json.load(open('$d/pop.json'))
assert r.get('subgroup_breakdown'), 'нет разбивки по подгруппам'
assert r.get('n_runs')==8, 'n_runs не совпадает с запрошенным'
" || fail "population-отчёт по web неполон"

# 10. Настоящий исход верификатора ИЗ контейнера.
python3 -c "
import json
r=json.load(open('$d/one.json'))
v=r.get('reward', r.get('passed', r.get('verified')))
assert v is not None, 'нет исхода верификации - прогон в контейнере не судился'
assert v not in (False,0), f'исход верификации отрицательный ({v!r})'
" || fail "нет доказанного исхода верификации из контейнера"

# 11. Среда действительно браузерная, а не HTTP-клиент под видом браузера.
grep -qiE "playwright|browser|chromium|firefox" application/tasks/web-choice/environment/Dockerfile \
  || fail "в образе нет браузерного рантайма - это не Web-среда"

# 12. Тихий откат запрещён.
MANTOZ_SANDBOX=выдумка uv run python -m mantoz.web run --persona-seed 1 --out "$d/z.json" >/dev/null 2>&1 \
  && fail "при нерабочем бэкенде прогон успешен - есть тихий откат"

# 13. Поломка сценария в контейнере НЕ маскируется под честный отказ персоны.
#     Проверяем на нескольких персонах, включая воздерживающихся от выбора.
for s in 1 2 3 4 5; do
  uv run python -m mantoz.web run --persona-seed "$s" --simulate-broken-scenario --out "$d/b$s.json" >/dev/null 2>&1 \
    && fail "персона seed=$s: сломанный сценарий принят за честный отказ (код 0)"
done

echo "пробы web: 13/13 ok"
