"""App-среда: персона решает в desktop-приложении через Harbor."""

import argparse
import asyncio
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

from mantoz.calibrate import judge_trial, run_trial_result
from mantoz.persona import sample
from mantoz.sandbox import resolve_backend

TASK_DIR = (
    Path(__file__).resolve().parents[2]
    / "application"
    / "tasks"
    / "app-decision"
)
OPTIONS = ("allow", "later", "deny")


def plan_decision(attributes: dict) -> str:
    """Детерминированно выводит решение из доверия к технологии и приватности."""
    if (
        attributes["privacy_sensitivity"] == "высокая"
        or attributes["technology_adoption"] == "избегает"
    ):
        return "deny"
    if attributes["privacy_sensitivity"] == "средняя":
        return "later"
    return "allow"


def validate_outcome(result: object) -> list[str]:
    if not isinstance(result, dict):
        return ["результат не объект"]
    errors = []
    actions = result.get("actions")
    decision = result.get("decision")
    if not isinstance(actions, list) or len(actions) < 2:
        errors.append("след действий короче двух шагов")
        actions = actions if isinstance(actions, list) else []
    if decision is None:
        errors.append("нет итогового решения")
    elif decision not in OPTIONS:
        errors.append(f"решение {decision!r} вне списка")
    clicks = [a for a in actions if isinstance(a, dict) and a.get("type") == "click"]
    if decision is not None and (not clicks or clicks[-1].get("target") != decision):
        errors.append("решение не совпадает с последним кликом")
    return errors


def _verifier_dir(trial) -> Path:
    return Path(trial.trial_uri.removeprefix("file://")) / "verifier"


def _read_container_result(trial) -> dict | None:
    try:
        result = json.loads((_verifier_dir(trial) / "result.json").read_text("utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return result if isinstance(result, dict) else None


def _screenshot_evidence(trial) -> list[dict]:
    evidence = []
    for name in ("before.png", "after.png"):
        try:
            data = (_verifier_dir(trial) / "screenshots" / name).read_bytes()
        except OSError:
            continue
        evidence.append(
            {
                "name": name,
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
    return evidence


async def run_persona_trial(attributes: dict, jobs_root: Path) -> dict:
    decision = plan_decision(attributes)
    jobs_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="app-", dir=jobs_root) as tmp:
        task_dir = Path(tmp) / "task"
        shutil.copytree(TASK_DIR, task_dir)
        solution_dir = task_dir / "solution"
        solution_dir.mkdir()
        payload = json.dumps({"choose": decision}, ensure_ascii=False)
        (solution_dir / "solve.sh").write_text(
            "#!/bin/sh\n"
            "cat > /app/plan.json <<'PLAN'\n"
            f"{payload}\n"
            "PLAN\n"
            "xvfb-run -a -s '-screen 0 1024x768x24' python3 /app/run_scenario.py\n",
            encoding="utf-8",
        )
        trial = await run_trial_result("oracle", Path(tmp) / "jobs", task_dir)
        container_result = _read_container_result(trial)
        screenshots = _screenshot_evidence(trial)
    passed, detail = judge_trial(trial)
    reward = float(
        ((trial.verifier_result.rewards if trial.verifier_result else None) or {}).get(
            "reward", 0.0
        )
    )
    return {
        "actions": (container_result or {}).get("actions", []),
        "decision": (container_result or {}).get("decision"),
        "screenshots": screenshots,
        "passed": passed,
        "reward": reward,
        "detail": detail,
        "infrastructure_failure": (
            not passed or container_result is None or len(screenshots) != 2
        ),
        "trial_id": str(trial.id),
        "agent": trial.agent_info.name if trial.agent_info else "oracle",
        "backend": resolve_backend().value,
    }


def run(persona_seed: int, out: Path) -> int:
    with tempfile.TemporaryDirectory(prefix="app-persona-") as tmp:
        personas_path = Path(tmp) / "persona.jsonl"
        sample(1, persona_seed, personas_path, dag=True)
        attributes = json.loads(personas_path.read_text("utf-8").splitlines()[0])[
            "attributes"
        ]
    outcome = asyncio.run(
        run_persona_trial(attributes, Path.home() / ".cache" / "mantoz")
    )
    result = {
        "task": "app-decision",
        "environment": "app",
        "persona_seed": persona_seed,
        "persona": attributes,
        **outcome,
    }
    out.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if outcome["infrastructure_failure"]:
        print(f"прогон app не состоялся: {outcome['detail']}", file=sys.stderr)
        return 1
    return 0


def verify(file: Path) -> int:
    try:
        result = json.loads(file.read_text(encoding="utf-8"))
        errors = validate_outcome(result)
    except (OSError, json.JSONDecodeError) as exc:
        errors = [f"не удалось прочитать результат: {exc}"]
    for error in errors:
        print(f"верификатор: {error}", file=sys.stderr)
    if errors:
        return 1
    print("верификатор: след действий и решение в формате")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(prog="mantoz.app")
    commands = parser.add_subparsers(dest="command", required=True)
    run_parser = commands.add_parser("run")
    run_parser.add_argument("--persona-seed", required=True, type=int)
    run_parser.add_argument("--out", required=True, type=Path)
    verify_parser = commands.add_parser("verify")
    verify_parser.add_argument("--file", required=True, type=Path)
    args = parser.parse_args()
    if args.command == "run":
        sys.exit(run(args.persona_seed, args.out))
    sys.exit(verify(args.file))


if __name__ == "__main__":
    main()
