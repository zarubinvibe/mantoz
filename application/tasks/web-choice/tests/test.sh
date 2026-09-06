#!/bin/sh
# Верификатор web-choice: судит итоговое решение по /app/result.json.
# Нет решения, мало действий или решение не из списка тарифов стенда -
# провал (reward 0), не крах.
mkdir -p /logs/verifier
# След и решение из браузерного прогона - на хост, их читает mantoz.web.
cp /app/result.json /logs/verifier/result.json 2>/dev/null || true
python3 - <<'PY'
import json
from pathlib import Path

OPTIONS = ("base", "standart", "premium")

reward = 0
try:
    result = json.loads(Path("/app/result.json").read_text("utf-8"))
    actions = result["actions"]
    decision = result["decision"]
    choose_actions = [a for a in actions if a.get("type") == "choose"]
    valid = (
        decision in OPTIONS
        and isinstance(actions, list)
        and len(actions) >= 2
        and actions[0].get("type") == "open"
        and choose_actions
        and choose_actions[-1].get("target") == decision
        and all(
            a.get("target") in OPTIONS or a.get("type") == "open" for a in actions
        )
    )
    reward = int(valid)
except Exception:
    reward = 0
Path("/logs/verifier/reward.txt").write_text(str(reward))
PY
