#!/bin/sh
# Пробы граунда персон (T09). Вне paths исполнителя.
# Данные НЕ качаются: пробы проверяют импортёр и границы, а не наличие чужого датасета.
set -e

fail() { echo "ПРОБА ПРОВАЛЕНА: $1"; exit 1; }
d=$(mktemp -d)

# 1. Реестр источников на диске, машиночитаемый.
[ -f config/grounding.json ] || fail "нет config/grounding.json"
python3 -c "
import json
g=json.load(open('config/grounding.json'))
src=g['sources'] if isinstance(g,dict) else g
assert len(src)>=1, 'реестр источников пуст'
for s in src:
    for k in ('id','name','license','url','commercial_use'):
        assert s.get(k) is not None, f\"у источника {s.get('id')} нет поля {k}\"
" || fail "реестр источников не прошёл структурную проверку"

# 2. Разрешённый источник присутствует, запрещённые отсутствуют (LIM-01..04, LIM-11, D-05, D-10).
#    РМЭЗ-ВШЭ выведен из продакшн-граунда 06.09.2026: его условия выдачи разрешают только
#    некоммерческое использование и запрещают передачу даже производной информации.
python3 -c "
import json
g=json.load(open('config/grounding.json'))
src=g['sources'] if isinstance(g,dict) else g
prod=[s for s in src if s.get('commercial_use') is True]
assert prod, 'нет ни одного источника с разрешённым коммерческим использованием'
ids=' '.join(str(s.get('id',''))+str(s.get('name','')) for s in prod).lower()
assert 'росстат' in ids or 'rosstat' in ids or 'tochno' in ids, 'нет Росстат/ЦБ - единственный подтверждённый источник'
for bad in ('wvs','world values','левада','levada','рмэз','rlms'):
    assert bad not in ids, f'источник с некоммерческой лицензией помечен как коммерчески разрешённый: {bad}'
" || fail "реестр источников нарушает юридические границы"

# 3. Импортёр отказывает внятно, когда данных на диске нет (сеть не трогаем).
out=$(uv run python -m mantoz.grounding import --source rosstat --path "$d/нет-такого" 2>&1) && rc=0 || rc=$?
[ "$rc" -ne 0 ] || fail "импортёр отработал на несуществующем пути"
echo "$out" | grep -qiE "нет|not found|отсутств" || fail "отказ импортёра не называет причину"

# 4. Импортёр НЕ ходит в сеть сам: в коде нет скачивания.
grep -qiE "requests\.get|urlopen|urlretrieve|httpx\.get|curl |wget " src/mantoz/grounding.py \
  && fail "импортёр качает данные сам - скачивание чужих данных решает владелец, не код"

# 5. Положительный контроль: на фикстуре-заглушке импортёр строит маргиналы.
python3 -c "
import json,random
random.seed(1)
rows=[{'age_group':random.choice(['18–24','25–34','35–44']),'income_level':random.choice(['низкий','средний','высокий'])} for _ in range(200)]
json.dump(rows,open('$d/fixture.json','w'),ensure_ascii=False)
"
uv run python -m mantoz.grounding import --source rosstat --path "$d/fixture.json" --out "$d/marg.json" >/dev/null 2>&1 \
  || fail "импортёр не отработал на честной фикстуре"
python3 -c "
import json
m=json.load(open('$d/marg.json'))
assert m, 'маргиналы пусты'
dims=m['dimensions'] if isinstance(m,dict) and 'dimensions' in m else m
assert len(dims)>=1, 'не построено ни одного распределения'
" || fail "импортёр не построил маргиналы"

# 6. Калибровка применяется: сэмплер с маргиналами даёт распределение ближе к ним, чем без.
uv run python -m mantoz.persona sample --n 300 --seed 7 --dag --grounding "$d/marg.json" --out "$d/g.jsonl" >/dev/null 2>&1 \
  || fail "сэмплер не принимает маргиналы через --grounding"
uv run python -m mantoz.persona sample --n 300 --seed 7 --dag --out "$d/u.jsonl" >/dev/null 2>&1
cmp -s "$d/g.jsonl" "$d/u.jsonl" && fail "с маргиналами и без результат одинаков - калибровка ни на что не влияет"

echo "пробы граунда: 6/6 ok"
