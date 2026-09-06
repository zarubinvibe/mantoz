#!/bin/sh
# Task-owned рубричный верификатор. Два разных профиля, сырьё и
# расхождение
# сохраняются рядом с reward для последующего спора по вердикту.
mkdir -p /logs/verifier
python3 - <<'PY'
import json
import re
from pathlib import Path

# ponytail: файл рубрики продублирован: Harbor монтирует только tests/;
# убрать копию, когда verifier получит read-only mount корня задачи.
rubric = json.loads(Path("/tests/rubric.yaml").read_text("utf-8"))


def opinion(judge_id, answer, stem_mode=False):
    text = " ".join(answer.casefold().split())
    score = 0
    passed, missed = [], []
    for criterion in rubric["criteria"]:
        criterion_id = criterion["id"]
        terms, stems = criterion["terms"], criterion["stems"]
        if stem_mode:
            found = all(stem in text for stem in stems)
        else:
            found = any(
                re.search(rf"(?<!\w){re.escape(term)}(?!\w)", text)
                for term in terms
            )
        (passed if found else missed).append(criterion_id)
        score += criterion["weight"] if found else 0
    rationale = (
        f"найдены: {', '.join(passed) or 'нет'}; "
        f"не найдены: {', '.join(missed) or 'нет'}"
    )
    raw = json.dumps(
        {"judge": judge_id, "score": score, "rationale": rationale},
        ensure_ascii=False,
    )
    return {"id": judge_id, "score": score, "rationale": rationale, "raw": raw}


try:
    answer = Path("/app/answer.txt").read_text("utf-8").strip()
except (OSError, UnicodeDecodeError):
    answer = ""
judges = [opinion("rules-exact-v1", answer), opinion("rules-stem-v1", answer, True)]
scores = [judge["score"] for judge in judges]
score = sum(scores) / len(scores)
disagreement = max(scores) - min(scores)
verdict = {
    "score": score,
    "rationale": (
        f"Среднее {score:g} по {len(judges)} судьям; "
        f"диапазон расхождения {disagreement:g}."
    ),
    "raw": "\n".join(judge["raw"] for judge in judges),
    "judges": judges,
    "disagreement": disagreement,
    "aggregation_method": "arithmetic_mean",
}
Path("/logs/verifier/verdict.json").write_text(
    json.dumps(verdict, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
Path("/logs/verifier/reward.txt").write_text(
    "1" if score >= rubric["pass_score"] else "0"
)
PY
