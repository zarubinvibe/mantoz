#!/bin/sh
# Судит итог диалога по файлу в песочнице и материалам из образа.
mkdir -p /logs/verifier
python3 - <<'PY'
import json
from pathlib import Path

reward = 0
try:
    result = json.loads(Path("/app/transcript.json").read_text("utf-8"))
    transcript = result["transcript"]
    scenario = json.loads(Path("/app/scenario.json").read_text("utf-8"))
    replies = json.loads(Path("/app/operator_replies.json").read_text("utf-8"))
    customer_lines = set(scenario["openings"].values()) | set(scenario["details"].values())
    operator_lines = set(replies["acknowledgements"].values()) | set(
        replies["resolutions"].values()
    )
    valid = (
        result.get("outcome") == "resolved"
        and isinstance(transcript, list)
        and len(transcript) >= 3
        and [message.get("role") for message in transcript]
            == ["customer", "operator"] * (len(transcript) // 2)
        and all(
            isinstance(message.get("content"), str) and message["content"].strip()
            for message in transcript
        )
        and all(
            message["content"]
            in (customer_lines if message["role"] == "customer" else operator_lines)
            for message in transcript
        )
        and transcript[-1]["content"] in replies["resolutions"].values()
    )
    reward = int(valid)
except Exception:
    reward = 0
Path("/logs/verifier/reward.txt").write_text(str(reward))
PY
