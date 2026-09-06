#!/bin/sh
# Пробы DAG-калибровки зависимостей между измерениями (T07). Вне paths исполнителя.
set -e

fail() { echo "ПРОБА ПРОВАЛЕНА: $1"; exit 1; }
d=$(mktemp -d)

# 1. Граф зависимостей на диске, машиночитаемый, без циклов.
[ -f persona/schema/dependencies.json ] || fail "нет persona/schema/dependencies.json"
python3 -c "
import json
g=json.load(open('persona/schema/dependencies.json'))
edges=g['edges'] if isinstance(g,dict) else g
assert len(edges)>=5, f'ребер всего {len(edges)} - зависимостей по существу нет'
dims={x['id'] for x in (lambda s: s['dimensions'] if isinstance(s,dict) else s)(json.load(open('persona/schema/dimensions.json')))}
adj={}
for e in edges:
    p,c=(e['parent'],e['child']) if isinstance(e,dict) else e
    assert p in dims, f'родитель {p} вне схемы'
    assert c in dims, f'потомок {c} вне схемы'
    adj.setdefault(p,[]).append(c)
# проверка ацикличности
WHITE,GREY,BLACK=0,1,2
color={}
def dfs(u):
    color[u]=GREY
    for v in adj.get(u,[]):
        assert color.get(v,WHITE)!=GREY, f'цикл в графе через {u}->{v}'
        if color.get(v,WHITE)==WHITE: dfs(v)
    color[u]=BLACK
for u in list(adj):
    if color.get(u,WHITE)==WHITE: dfs(u)
" || fail "граф зависимостей не прошел проверку (структура, принадлежность схеме или ацикличность)"

# 2. Положительный контроль: сэмплер с учетом зависимостей отрабатывает.
uv run python -m mantoz.persona sample --n 200 --seed 3 --dag --out "$d/dag.jsonl" >/dev/null 2>&1 \
  || fail "сэмплирование с --dag не отработало"
[ "$(wc -l < "$d/dag.jsonl")" -eq 200 ] || fail "выдано не 200 персон"

# 3. Персоны по-прежнему валидны по схеме (зависимости не сломали словарь значений).
python3 -c "
import json
dims=json.load(open('persona/schema/dimensions.json'))
dims=dims['dimensions'] if isinstance(dims,dict) else dims
allowed={x['id']:set(x['values']) for x in dims}
for line in open('$d/dag.jsonl'):
    a=json.loads(line); a=a.get('attributes',a)
    assert not (set(allowed)-set(a)), 'персона потеряла измерения'
    for k,v in a.items():
        if k in allowed: assert v in allowed[k], f'{k}={v!r} вне схемы'
" || fail "персоны с зависимостями не соответствуют схеме"

# 4. Суть тикета: зависимости реально меняют совместное распределение.
#    Сравниваем независимое сэмплирование и DAG на одном seed - они обязаны отличаться.
uv run python -m mantoz.persona sample --n 200 --seed 3 --out "$d/indep.jsonl" >/dev/null 2>&1
cmp -s "$d/dag.jsonl" "$d/indep.jsonl" && fail "с --dag и без него результат одинаков - зависимости ни на что не влияют"

# 5. Машинная проверка правил консистентности: заявленные графом связки не нарушаются.
uv run python -m mantoz.persona check --file "$d/dag.jsonl" >/dev/null 2>&1 \
  || fail "проверка консистентности на собственной выборке с --dag красная"

# 6. Контроль к пробе 5: та же проверка обязана ловить нарушения на независимых выборках.
#    Одна выборка может случайно оказаться чистой, поэтому пробуем несколько seed:
#    хотя бы одна обязана покраснеть, иначе проверка вырождена.
caught=0
for s in 11 12 13 14 15; do
  uv run python -m mantoz.persona sample --n 200 --seed "$s" --out "$d/i$s.jsonl" >/dev/null 2>&1 || continue
  if ! uv run python -m mantoz.persona check --file "$d/i$s.jsonl" >/dev/null 2>&1; then
    caught=1; break
  fi
done
[ "$caught" -eq 1 ] || fail "проверка консистентности зеленая на всех независимых выборках - она вырождена"

echo "пробы DAG: 6/6 ok"
