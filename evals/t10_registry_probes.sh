#!/bin/sh
# Пробы реестра агентов (T10). Вне paths исполнителя.
set -e

fail() { echo "ПРОБА ПРОВАЛЕНА: $1"; exit 1; }

# 1. Реестр на диске, машиночитаемый, не меньше 10 записей.
[ -f config/agents.json ] || fail "нет config/agents.json"
python3 -c "
import json
r=json.load(open('config/agents.json'))
a=r['agents'] if isinstance(r,dict) else r
assert len(a)>=10, f'записей всего {len(a)}, требуется не менее 10'
ids=[x['id'] for x in a]
assert len(set(ids))==len(ids), 'id агентов повторяются'
for x in a:
    assert x.get('harbor_agent'), f\"у {x['id']} не указан агент Harbor\"
    assert 'installed' in x, f\"у {x['id']} нет поля installed\"
" || fail "реестр не прошел структурную проверку"

# 2. Реестр честен про установленное: заявленное installed=true обязано находиться в системе.
python3 - <<'PY' || exit 1
import json, shutil, sys
r = json.load(open('config/agents.json'))
agents = r['agents'] if isinstance(r, dict) else r
for x in agents:
    if x.get('installed') is True:
        b = x.get('binary') or x['id']
        if shutil.which(b) is None:
            print(f"ПРОБА ПРОВАЛЕНА: {x['id']} помечен installed=true, но бинаря '{b}' в системе нет")
            sys.exit(1)
PY

# 3. Положительный контроль: три живых CLI владельца присутствуют и помечены установленными.
for c in claude codex kimi; do
  python3 -c "
import json,sys
r=json.load(open('config/agents.json'))
a=r['agents'] if isinstance(r,dict) else r
m=[x for x in a if x['id']=='$c' or x.get('binary')=='$c']
sys.exit(0 if m and m[0].get('installed') is True else 1)" || fail "$c нет в реестре или не помечен установленным"
done

# 4. Отрицательная сторона: неизвестный агент отвергается, не подставляется дефолт.
if uv run python -m mantoz.agents resolve --id выдумка >/dev/null 2>&1; then
  fail "неизвестный агент принят вместо отказа"
fi

# 5. Контроль к пробе 4: известный агент разрешается и печатает свой Harbor-агент.
out=$(uv run python -m mantoz.agents resolve --id claude 2>&1) || fail "известный агент не разрешился: $out"
echo "$out" | grep -qiE "persona|claude" || fail "разрешение не назвало агента Harbor: '$out'"

# 6. Список печатает установленные и неустановленные раздельно, без вранья.
out=$(uv run python -m mantoz.agents list 2>&1) || fail "список не отработал"
echo "$out" | grep -qiE "установлен|installed" || fail "в списке не видно статуса установки"

echo "пробы реестра: 6/6 ok"
