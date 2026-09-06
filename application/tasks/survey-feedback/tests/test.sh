#!/bin/sh
# Верификатор survey-feedback: судит полноту и формат /app/answers.json.
# Отсутствие файла или любой ответ вне формата - провал (reward 0), не крах.
# ponytail: ожидаемые вопросы продублированы из questionnaire.yaml; апгрейд -
# смонтировать анкету в контейнер и судить общим валидатором mantoz.survey.
mkdir -p /logs/verifier
python3 - <<'EOF'
import json
from pathlib import Path

EXPECTED = {
    "usage_frequency": ["каждый день", "несколько раз в неделю",
                        "несколько раз в месяц", "реже одного раза в месяц"],
    "usability_rating": (1, 5),
    "data_trust": (1, 5),
    "recommendation": ["да", "скорее да", "скорее нет", "нет"],
    "improvement_text": "text",
}

def ok(rule, value):
    if isinstance(rule, list):
        return value in rule
    if rule == "text":
        return isinstance(value, str) and bool(value.strip())
    low, high = rule
    return isinstance(value, int) and low <= value <= high

reward = 0
try:
    answers = json.loads(Path("/app/answers.json").read_text("utf-8"))["answers"]
    if all(qid in answers and ok(rule, answers[qid])
           for qid, rule in EXPECTED.items()):
        reward = 1
except Exception:
    reward = 0
Path("/logs/verifier/reward.txt").write_text(str(reward))
EOF
