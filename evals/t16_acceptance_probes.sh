#!/bin/sh
# Пробы финальной приёмки MVP (T16). Вне paths исполнителя.
# Это ворота REQ-01: чек-лист паритета обязан быть закрыт честно, а не подогнан под ноль.
set -e

fail() { echo "ПРОБА ПРОВАЛЕНА: $1"; exit 1; }

# 1. Гейт паритета зелёный: ноль строк «отсутствует без обоснования».
uv run python -m mantoz.parity_gate >/dev/null 2>&1 \
  || fail "гейт паритета красный - есть незакрытые строки чек-листа"

# 2. Гейт по-прежнему НЕ вырожден: собственные пробы прибора зелёные.
sh evals/t02_gate_probes.sh >/dev/null 2>&1 \
  || fail "прибор паритета сам не проходит свои пробы - его зелёный ничего не значит"

# 3. Чек-лист покрывает все семь подсистем аудита.
python3 -c "
import re
t=open('docs/PARITY.md',encoding='utf-8').read().lower()
for sub in ('persona','task-contract','harbor','playground','packages','deployment','testing'):
    assert sub in t, f'в чек-листе нет подсистемы {sub}'
rows=[l for l in t.splitlines() if l.startswith('| ') and '---' not in l]
assert len(rows)>=7, f'строк в таблице всего {len(rows)}'
" || fail "чек-лист не покрывает семь подсистем"

# 4. Обоснованные отсутствия ссылаются на реальные OUT-ID из цели (не на REQ, не прозой).
python3 -c "
import re
goal=open('queue/GOAL.md',encoding='utf-8').read()
valid=set(re.findall(r'OUT-\d{2}', goal))
assert valid, 'в цели нет ни одного OUT-ID'
bad=[]
for l in open('docs/PARITY.md',encoding='utf-8'):
    if 'обоснованно' in l.lower():
        ids=set(re.findall(r'OUT-\d{2}', l))
        if not ids or not (ids & valid): bad.append(l.strip()[:90])
assert not bad, f'строки обоснованы без настоящего OUT-ID: {bad[:3]}'
" || fail "есть обоснования без ссылки на реальный OUT-ID"

# 5. Все четыре среды реально работают на дату приёмки (REQ-08).
for t in survey chat web app; do
  uv run python -m mantoz.population run --n-runs 3 --seed 11 --task "$t" --out "/tmp/acc_$t.json" >/dev/null 2>&1 \
    || fail "среда $t не отработала population-прогон на приёмке"
done

# 6. Отчёты сред несут population-агрегацию, а не список прогонов.
python3 -c "
import json
for t in ('survey','chat','web','app'):
    r=json.load(open(f'/tmp/acc_{t}.json'))
    for k in ('n_runs','aggregation_method','subgroup_breakdown'):
        assert r.get(k) is not None, f'{t}: в отчёте нет {k}'
    assert r['subgroup_breakdown'], f'{t}: разбивка по подгруппам пуста'
" || fail "отчёты сред не несут population-агрегации"

# 7. Юридические границы держатся: запрещённых источников нет среди коммерчески разрешённых.
python3 -c "
import json
g=json.load(open('config/grounding.json'))
src=g['sources'] if isinstance(g,dict) else g
ids=' '.join(str(s.get('id',''))+str(s.get('name','')) for s in src if s.get('commercial_use') is True).lower()
for bad in ('wvs','левада','levada','рмэз','rlms'):
    assert bad not in ids, f'источник с некоммерческой лицензией помечен коммерчески разрешённым: {bad}'
" || fail "нарушены юридические границы граунда"

# 8. Persona1M не просочился в продакшн-путь (LIM-08).
grep -rniE "persona[_-]?1m|MatrAIx_Persona" src/mantoz/*.py 2>/dev/null | grep -viE "dev|test|bootstrap" | grep -q . \
  && fail "Persona1M в продакшн-пути - нарушение LIM-08"

# 9. Harbor остаётся зависимостью, а не вендоренной копией (LIM-05).
grep -q 'harbor' pyproject.toml || fail "Harbor исчез из зависимостей"
find . -iname 'harbor' -type d -not -path './.venv/*' -not -path './.git/*' | grep -q . \
  && fail "в дереве появилась вендоренная копия Harbor"

# 10. Один фронтенд, а не два SPA (REQ-06).
n=$(find . -name package.json -not -path "./node_modules/*" -not -path "./.venv/*" | wc -l | tr -d ' ')
[ "$n" -le 1 ] || fail "фронтенд-пакетов $n - обязан быть один"

# 11. Композиция: population по умолчанию гонит персон ЧЕРЕЗ DAG и гейт качества.
#     Модули T07/T08 обязаны быть в боевом пути, а не лежать рядом (LIM-10).
py_check=$(cat <<'PYEOF'
import json,subprocess,sys,tempfile,os
d=tempfile.mkdtemp()
out=os.path.join(d,'pop.json')
r=subprocess.run(["uv","run","python","-m","mantoz.population","run","--n-runs","6","--seed","5","--task","survey","--out",out],
                 capture_output=True,text=True)
assert r.returncode==0, "population не отработал: "+r.stderr[-300:]
rep=json.load(open(out))
prov=rep.get("persona_provenance") or rep.get("cohort") or {}
assert prov.get("dag") is True, "population сэмплит без DAG - персоны могут быть противоречивы (T07 не в пути)"
assert prov.get("quality_gated") is True, "выборка не прошла гейт качества перед прогоном (T08 не в пути)"
PYEOF
)
python3 -c "$py_check" || fail "population гонит эвалы на некалиброванных персонах - модули есть, композиции нет (LIM-10)"

echo "приёмка MVP: 11/11 ok"
