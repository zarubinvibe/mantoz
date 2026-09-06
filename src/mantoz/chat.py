"""Детерминированная Chat-среда: реплики зависят от признаков персоны."""

import argparse
import asyncio
import json
import shutil
import sys
import tempfile
from pathlib import Path

from mantoz.calibrate import judge_trial, run_trial_result
from mantoz.persona import sample
from mantoz.sandbox import resolve_backend

TASK_DIR = (
    Path(__file__).resolve().parents[2] / "application" / "tasks" / "chat-support"
)
ENVIRONMENT_DIR = TASK_DIR / "environment"


def load_material(name: str) -> dict:
    return json.loads((ENVIRONMENT_DIR / name).read_text(encoding="utf-8"))


def run_dialogue(attributes: dict) -> list[dict[str, str]]:
    """Строит стабильный диалог из четырёх признаков персоны."""
    scenario = load_material("scenario.json")
    replies = load_material("operator_replies.json")
    return [
        {
            "role": "customer",
            "content": scenario["openings"][attributes["feedback_style"]],
        },
        {
            "role": "operator",
            "content": replies["acknowledgements"][attributes["digital_literacy"]],
        },
        {
            "role": "customer",
            "content": scenario["details"][attributes["response_detail_preference"]],
        },
        {
            "role": "operator",
            "content": replies["resolutions"][attributes["privacy_sensitivity"]],
        },
    ]


def validate_transcript(transcript: object) -> list[str]:
    if not isinstance(transcript, list):
        return ["transcript не список"]
    errors = []
    if len(transcript) < 3:
        errors.append("меньше трёх реплик")
    expected_roles = ["customer", "operator"] * (len(transcript) // 2)
    roles = []
    for index, message in enumerate(transcript, 1):
        if not isinstance(message, dict):
            errors.append(f"реплика {index} не объект")
            continue
        roles.append(message.get("role"))
        if not isinstance(message.get("content"), str) or not message["content"].strip():
            errors.append(f"реплика {index} пуста")
    if roles != expected_roles:
        errors.append("роли должны чередоваться: customer, operator")
    return errors


async def run_persona_trial(attributes: dict, jobs_root: Path) -> dict:
    transcript = run_dialogue(attributes)
    jobs_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="chat-", dir=jobs_root) as tmp:
        task_dir = Path(tmp) / "task"
        shutil.copytree(TASK_DIR, task_dir)
        solution_dir = task_dir / "solution"
        solution_dir.mkdir()
        payload = json.dumps(
            {"transcript": transcript, "outcome": "resolved"},
            ensure_ascii=False,
            indent=2,
        )
        (solution_dir / "solve.sh").write_text(
            "#!/bin/sh\n"
            "cat > /app/transcript.json <<'TRANSCRIPT'\n"
            f"{payload}\n"
            "TRANSCRIPT\n",
            encoding="utf-8",
        )
        trial = await run_trial_result("oracle", Path(tmp) / "jobs", task_dir)
    passed, detail = judge_trial(trial)
    if not passed:
        raise RuntimeError(f"Harbor chat trial failed: {detail}")
    reward = float(trial.verifier_result.rewards["reward"])
    return {
        "transcript": transcript,
        "outcome": "resolved",
        "passed": passed,
        "reward": reward,
        "detail": detail,
        "trial_id": str(trial.id),
        "agent": trial.agent_info.name if trial.agent_info else "oracle",
        "backend": resolve_backend().value,
    }


def run(persona_seed: int, out: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="chat-persona-") as tmp:
        personas_path = Path(tmp) / "persona.jsonl"
        sample(1, persona_seed, personas_path, dag=True)
        row = personas_path.read_text(encoding="utf-8").splitlines()[0]
        attributes = json.loads(row)["attributes"]
    outcome = asyncio.run(
        run_persona_trial(attributes, Path.home() / ".cache" / "mantoz")
    )
    result = {
        "task": "chat-support",
        "environment": "chat",
        "persona_seed": persona_seed,
        "persona": attributes,
        **outcome,
    }
    out.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def verify(file: Path) -> int:
    try:
        result = json.loads(file.read_text(encoding="utf-8"))
        errors = validate_transcript(result.get("transcript"))
        if result.get("outcome") != "resolved":
            errors.append("диалог не завершён")
    except (OSError, json.JSONDecodeError, AttributeError) as exc:
        errors = [f"не удалось прочитать результат: {exc}"]
    for error in errors:
        print(f"верификатор: {error}", file=sys.stderr)
    if errors:
        return 1
    print("верификатор: диалог завершён")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(prog="mantoz.chat")
    commands = parser.add_subparsers(dest="command", required=True)
    run_parser = commands.add_parser("run")
    run_parser.add_argument("--persona-seed", required=True, type=int)
    run_parser.add_argument("--out", required=True, type=Path)
    verify_parser = commands.add_parser("verify")
    verify_parser.add_argument("--file", required=True, type=Path)
    args = parser.parse_args()
    if args.command == "run":
        run(args.persona_seed, args.out)
    else:
        sys.exit(verify(args.file))


if __name__ == "__main__":
    main()
