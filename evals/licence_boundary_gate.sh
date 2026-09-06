#!/bin/sh
# Гейт лицензионной границы. Источники с ограничением на передачу (РМЭЗ и подобные)
# разрешены для локальной работы владельца, но НИЧЕГО производного от них
# не должно попадать в git и уезжать наружу. Правило живёт в воротах, не в обещании.
set -e
fail() { echo "ГРАНИЦА НАРУШЕНА: $1"; exit 1; }

# 1. Каталог с несвободными данными не отслеживается git.
git ls-files data/ 2>/dev/null | grep -q . && fail "файлы из data/ попали под контроль версий"
git check-ignore -q data 2>/dev/null || fail "data/ не в .gitignore"

# 2. Производные артефакты несвободных источников не отслеживаются.
for pat in "*.marginals.json" "*rlms*" "*рмэз*" "*.model" "*.weights" "*.safetensors" "*.ckpt"; do
  git ls-files 2>/dev/null | grep -i -- "${pat#\*}" | grep -vE "^(evals/|queue/|docs/|config/grounding.json)" | grep -q . \
    && fail "в git есть артефакт несвободного источника по шаблону $pat"
done

# 3. Реестр честно помечает, что можно отдавать наружу, а что нет.
python3 -c "
import json
g=json.load(open('config/grounding.json'))
src=g['sources'] if isinstance(g,dict) else g
for s in src:
    assert 'redistribution' in s or 'commercial_use' in s, f\"у источника {s.get('id')} не указан режим передачи\"
    if s.get('commercial_use') is not True:
        assert s.get('local_only') is True, f\"источник {s.get('id')} с ограниченной лицензией не помечен local_only\"
" || fail "реестр источников не различает, что можно отдавать наружу"

echo "лицензионная граница: цела"
