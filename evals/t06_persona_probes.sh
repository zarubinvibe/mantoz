#!/bin/sh
# Пробы персона-таксономии и сэмплера (T06). Вне paths исполнителя.
# У каждой отрицательной пробы есть положительный контроль.
set -e

fail() { echo "ПРОБА ПРОВАЛЕНА: $1"; exit 1; }
d=$(mktemp -d)

# 1. Схема лежит на диске машиночитаемой и непустой.
[ -f persona/schema/dimensions.json ] || fail "нет persona/schema/dimensions.json"
python3 -c "
import json,sys
d=json.load(open('persona/schema/dimensions.json'))
dims=d['dimensions'] if isinstance(d,dict) else d
assert len(dims)>=30, f'измерений всего {len(dims)} - схема урезана'
for x in dims:
    assert x.get('id'), 'у измерения нет id'
    assert x.get('category'), f\"у {x.get('id')} нет категории\"
    vs=x.get('values') or []
    assert len(vs)>=2, f\"у {x.get('id')} меньше двух значений\"
    assert len(set(vs))==len(vs), f\"у {x.get('id')} повторяются значения\"
ids=[x['id'] for x in dims]
assert len(set(ids))==len(ids), 'id измерений повторяются'
" || fail "схема измерений не прошла структурную проверку"

# 2. Положительный контроль: сэмплер выдаёт запрошенное число валидных персон.
uv run python -m mantoz.persona sample --n 20 --seed 1 --out "$d/p.jsonl" >/dev/null 2>&1 \
  || fail "сэмплер не отработал"
[ "$(wc -l < "$d/p.jsonl")" -eq 20 ] || fail "выдано не 20 персон"

# 3. Каждая персона покрывает все измерения схемы и только допустимыми значениями.
python3 -c "
import json
dims=json.load(open('persona/schema/dimensions.json'))
dims=dims['dimensions'] if isinstance(dims,dict) else dims
allowed={x['id']:set(x['values']) for x in dims}
for line in open('$d/p.jsonl'):
    p=json.loads(line)
    a=p.get('attributes',p)
    miss=set(allowed)-set(a)
    assert not miss, f'персона без измерений: {sorted(miss)[:3]}'
    for k,v in a.items():
        if k in allowed:
            assert v in allowed[k], f'{k}={v!r} вне списка значений схемы'
" || fail "персоны не соответствуют схеме"

# 4. Один seed - один результат (воспроизводимость).
uv run python -m mantoz.persona sample --n 20 --seed 1 --out "$d/q.jsonl" >/dev/null 2>&1
cmp -s "$d/p.jsonl" "$d/q.jsonl" || fail "тот же seed дал другой результат - воспроизводимости нет"

# 5. Разный seed - разный результат (сэмплер не константа). Контроль к пробе 4.
uv run python -m mantoz.persona sample --n 20 --seed 2 --out "$d/r.jsonl" >/dev/null 2>&1
cmp -s "$d/p.jsonl" "$d/r.jsonl" && fail "разные seed дали одинаковый результат - сэмплер вырожден"

# 6. Persona1M MatrAIx не утёк в продакшн-путь (LIM-08).
if grep -rniE "persona[_-]?1m|MatrAIx_Persona" src/mantoz/persona.py persona/schema 2>/dev/null | grep -qv "^Binary"; then
  fail "ссылка на Persona1M в продакшн-пути - нарушение LIM-08"
fi

echo "пробы персон: 6/6 ok"
