#!/bin/sh
# Пробы тонкого вьювера (T15). Вне paths исполнителя.
set -e

fail() { echo "ПРОБА ПРОВАЛЕНА: $1"; exit 1; }
d=$(mktemp -d)

# 1. Ровно один фронтенд-пакет, а не два конкурирующих SPA (D-06, REQ-06).
n=$(find . -name package.json -not -path "./node_modules/*" -not -path "./.venv/*" -not -path "*/node_modules/*" | wc -l | tr -d ' ')
[ "$n" -le 1 ] || fail "фронтенд-пакетов $n - у MatrAIx два SPA, у нас обязан быть один"

# 2. Готовим отчёт population для показа.
uv run python -m mantoz.population run --n-runs 8 --seed 5 --task survey --out "$d/rep.json" >/dev/null 2>&1 \
  || fail "не удалось получить отчёт population"

# 3. Вьювер рендерит отчёт без ручных запросов к API.
uv run python -m mantoz.viewer render --report "$d/rep.json" --out "$d/out.html" >/dev/null 2>&1 \
  || fail "вьювер не отрендерил отчёт"
[ -s "$d/out.html" ] || fail "результат рендера пуст"

# 4. В выводе видно главное: число прогонов, метод свертки, подгруппы с долями.
python3 -c "
import json,re
h=open('$d/out.html',encoding='utf-8').read()
r=json.load(open('$d/rep.json'))
assert str(r['n_runs']) in h, 'в выводе нет числа прогонов'
assert r['aggregation_method'] in h, 'в выводе нет метода свертки'
sb=r['subgroup_breakdown']
keys=list(sb) if isinstance(sb,dict) else []
assert keys, 'в отчёте нет подгрупп'
hit=sum(1 for k in keys if str(k) in h)
assert hit>=max(1,len(keys)//2), f'в выводе видно лишь {hit} подгрупп из {len(keys)}'
" || fail "вывод вьювера не показывает суть отчёта"

# 5. ГЛАВНОЕ: несостоявшиеся прогоны показываются ОТДЕЛЬНО, а не тонут в общей доле.
python3 -c "
import json
r=json.load(open('$d/rep.json'))
r['failed_trials']=[{'persona_seed':99,'reason':'контейнер не поднялся'}]
json.dump(r,open('$d/withfail.json','w'),ensure_ascii=False)
"
uv run python -m mantoz.viewer render --report "$d/withfail.json" --out "$d/out2.html" >/dev/null 2>&1 \
  || fail "вьювер не отрендерил отчёт с несостоявшимися прогонами"
python3 -c "
h=open('$d/out2.html',encoding='utf-8').read()
import re
assert re.search(r'(не состоя|несостоя|failed|сбой|поломк)', h, re.I), \
    'несостоявшиеся прогоны не показаны отдельно - они утонули в общей статистике'
" || fail "вьювер прячет несостоявшиеся прогоны"

# 6. Отчёта нет - вьювер отказывает внятно, а не рисует пустоту.
uv run python -m mantoz.viewer render --report "$d/нет.json" --out "$d/x.html" >/dev/null 2>&1 \
  && fail "вьювер отрендерил несуществующий отчёт"

echo "пробы вьювера: 6/6 ok"
