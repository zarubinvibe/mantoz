#!/bin/sh
# Судит решение и доказательства настоящего computer-use прогона.
mkdir -p /logs/verifier/screenshots
cp /app/result.json /logs/verifier/result.json 2>/dev/null || true
cp /app/screenshots/before.png /app/screenshots/after.png /logs/verifier/screenshots/ 2>/dev/null || true
python3 - <<'PY'
import json
from pathlib import Path

OPTIONS = ("allow", "later", "deny")
PNG = b"\x89PNG\r\n\x1a\n"

reward = 0
try:
    result = json.loads(Path("/app/result.json").read_text("utf-8"))
    actions = result["actions"]
    decision = result["decision"]
    shots = [a.get("target") for a in actions if a.get("type") == "screenshot"]
    clicks = [a for a in actions if a.get("type") == "click"]
    images = [
        (Path("/app/screenshots") / name).read_bytes()
        for name in ("before.png", "after.png")
    ]
    valid = (
        decision in OPTIONS
        and isinstance(actions, list)
        and len(actions) >= 4
        and actions[0] == {"type": "open", "target": "notification-dialog"}
        and clicks
        and clicks[-1].get("target") == decision
        and shots == ["before.png", "after.png"]
        and all(len(image) > 1000 and image.startswith(PNG) for image in images)
        and images[0] != images[1]
    )
    reward = int(valid)
except Exception:
    reward = 0
Path("/logs/verifier/reward.txt").write_text(str(reward))
PY
