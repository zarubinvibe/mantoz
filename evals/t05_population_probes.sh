#!/bin/sh
# Пробы population-агрегации (T05). Вне paths исполнителя.
set -e

fail() { echo "ПРОБА ПРОВАЛЕНА: $1"; exit 1; }
d=$(mktemp -d)

# 1. Прогон с n_runs > 1 отрабатывает и пишет машиночитаемый отчет.
uv run python -m mantoz.population run --n-runs 6 --seed 1 --out "$d/rep.json" >/dev/null 2>&1 \
  || fail "прогон population с n_runs=6 не отработал"
[ -s "$d/rep.json" ] || fail "отчет пуст"

# 2. Отчет несет агрегацию, а не список прогонов: обязательные поля на месте.
python3 -c "
import json
r=json.load(open('$d/rep.json'))
for k in ('n_runs','aggregation_method','subgroup_breakdown'):
    assert k in r, f'в отчете нет поля {k}'
assert r['n_runs']==6, f\"n_runs в отчете {r['n_runs']}, а запрошено 6\"
assert r['aggregation_method'], 'aggregation_method пуст'
sb=r['subgroup_breakdown']
assert isinstance(sb,(dict,list)) and len(sb)>0, 'subgroup_breakdown пуст - разбивки по подгруппам нет'
" || fail "отчет не прошел проверку структуры агрегации"

# 3. n_runs - обязательный параметр, без него отказ (не молчаливая единица).
if uv run python -m mantoz.population run --seed 1 --out "$d/x.json" >/dev/null 2>&1; then
  fail "прогон без n_runs прошел - число прогонов подставлено молча"
fi

# 4. Отрицательная сторона: n_runs=1 отвергается, population-масштаб не имитируется одним прогоном.
if uv run python -m mantoz.population run --n-runs 1 --seed 1 --out "$d/y.json" >/dev/null 2>&1; then
  fail "n_runs=1 принят - это не population-масштаб (REQ-05 требует больше единицы)"
fi

# 5. Агрегат отличается от простого повтора: у разных персон разные исходы.
#    Контроль: отчет обязан различать подгруппы, а не выдавать одну строку на всех.
python3 -c "
import json
r=json.load(open('$d/rep.json'))
sb=r['subgroup_breakdown']
groups = sb if isinstance(sb,list) else list(sb.values())
assert len(groups)>=2, f'подгрупп всего {len(groups)} - разбивки по существу нет'
" || fail "разбивка по подгруппам вырождена"

# 6. Воспроизводимость: тот же seed - тот же агрегат.
uv run python -m mantoz.population run --n-runs 6 --seed 1 --out "$d/rep2.json" >/dev/null 2>&1
python3 -c "
import json
a=json.load(open('$d/rep.json')); b=json.load(open('$d/rep2.json'))
assert a==b, 'тот же seed дал другой агрегат - воспроизводимости нет'
" || fail "агрегация не воспроизводима по seed"

echo "пробы population: 6/6 ok"
