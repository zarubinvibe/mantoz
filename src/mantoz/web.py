"""Среда Web: персона проходит сценарий выбора тарифа в браузере.

Дефолт — без вызова модели: план действий (что осмотреть, что выбрать)
выводится правилами из признаков персоны на хосте и запекается в
solution/solve.sh копии задачи; сам проход - клики по странице-стенду в
настоящем Chromium - исполняется внутри контейнера Harbor, а итоговое
решение читается из DOM и судится верификатором контейнера.
"""

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

TASK_DIR = Path(__file__).resolve().parents[2] / "application" / "tasks" / "web-choice"

OPTIONS = ("base", "standart", "premium")
INSPECT_COUNT_BY_STYLE = {"интуитивный": 1, "сбалансированный": 2, "аналитический": 3}
PREMIUM_VALUES = {"достижение", "новизна"}
BASE_VALUES = {"самостоятельность"}


def completes_scenario(attributes: dict) -> bool:
    """Уход без выбора - тоже следствие персоны: бросающие не доходят до кнопки."""
    return not (
        attributes["follow_through"] == "часто бросает"
        and (
            attributes["conscientiousness"] == "низкая"
            or attributes["digital_literacy"] == "базовая"
        )
    )


def plan_actions(attributes: dict) -> dict:
    """Строит план сценария из признаков персоны, детерминированно."""
    if not completes_scenario(attributes):
        # Персона осматривает один тариф и уходит без выбора.
        return {"inspect": [OPTIONS[0]], "choose": None}
    if attributes["income_stability"] == "нестабильный":
        choose = "base"
    elif attributes["value_priority"] in PREMIUM_VALUES:
        choose = "premium"
    elif attributes["value_priority"] in BASE_VALUES:
        choose = "base"
    else:
        choose = "standart"
    # Сколько тарифов осмотреть до выбора - стиль решений; выбранный первым.
    count = INSPECT_COUNT_BY_STYLE[attributes["decision_style"]]
    rest = [option for option in OPTIONS if option != choose]
    return {"inspect": [choose, *rest][:count], "choose": choose}


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
        errors.append(f"решение {decision!r} вне списка тарифов")
    choose_actions = [a for a in actions if isinstance(a, dict) and a.get("type") == "choose"]
    if decision is not None and (
        not choose_actions or choose_actions[-1].get("target") != decision
    ):
        errors.append("решение не совпадает с последним действием choose")
    return errors


async def run_persona_trial(
    attributes: dict, jobs_root: Path, simulate_broken: bool = False
) -> dict:
    """Прогоняет web-задачу одной персоной ЧЕРЕЗ Harbor.

    План действий выводится детерминированно из признаков на хосте (без
    платной модели), запекается в solution/solve.sh копии задачи; браузерный
    проход и вердикт - настоящий прогон Harbor в контейнере.
    simulate_broken - имитация поломки: сценарий намеренно недоступен
    внутри трайла, прогон обязан упасть для любой персоны.
    """
    plan = plan_actions(attributes)
    jobs_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="web-", dir=jobs_root) as tmp:
        task_dir = Path(tmp) / "task"
        shutil.copytree(TASK_DIR, task_dir)
        solution_dir = task_dir / "solution"
        solution_dir.mkdir()
        payload = json.dumps(plan, ensure_ascii=False, indent=2)
        scenario_call = (
            # Имитация дефекта «run_scenario.py отсутствует в образе».
            "rm -f /app/run_scenario.py\npython3 /app/run_scenario.py\n"
            if simulate_broken
            else "python3 /app/run_scenario.py\n"
        )
        (solution_dir / "solve.sh").write_text(
            "#!/bin/sh\n"
            "# План персоны, запечённый хостом (детерминированный режим).\n"
            "cat > /app/plan.json <<'PLAN'\n"
            f"{payload}\n"
            "PLAN\n"
            f"{scenario_call}",
            encoding="utf-8",
        )
        trial = await run_trial_result("oracle", Path(tmp) / "jobs", task_dir)
        # След и решение - настоящие, из браузерного прогона: верификатор
        # контейнера копирует /app/result.json в /logs/verifier, смонтированный
        # на хост. Читать обязательно до выхода из with - каталог временный.
        container_result = _read_container_result(trial)
    passed, detail = judge_trial(trial)
    # Поломка != исход персоны. Признак поломки - ДОКАЗАТЕЛЬСТВО, что сценарий
    # исполнялся: честный проход (включая воздержание) всегда оставляет след
    # прогона result.json. Нет следа - прогон не состоялся, это инфраструктурный
    # сбой для ЛЮБОЙ персоны, а не «персона ничего не выбрала».
    if container_result is None:
        infrastructure_failure = True
        detail = "сценарий в контейнере не исполнялся: нет следа прогона (result.json)"
    else:
        # Крах трайла, либо отрицательный вердикт при плане С выбором (честный
        # проход валиден по построению, значит контейнер потерял результат).
        # Честный провал - только уход без выбора (choose: null).
        infrastructure_failure = not passed and (
            detail.startswith("крах прогона:") or plan["choose"] is not None
        )
    return {
        "actions": (container_result or {}).get("actions", []),
        "decision": (container_result or {}).get("decision"),
        "passed": passed,
        "reward": _reward(trial),
        "detail": detail,
        "infrastructure_failure": infrastructure_failure,
        "trial_id": str(trial.id),
        "agent": trial.agent_info.name if trial.agent_info else "oracle",
        "backend": resolve_backend().value,
    }


def _read_container_result(trial) -> dict | None:
    """Читает result.json, скопированный верификатором контейнера на хост."""
    verifier_dir = Path(trial.trial_uri.removeprefix("file://")) / "verifier"
    try:
        return json.loads((verifier_dir / "result.json").read_text("utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _reward(trial) -> float:
    rewards = (trial.verifier_result.rewards if trial.verifier_result else None) or {}
    return float(rewards.get("reward", 0.0))


def run(persona_seed: int, out: Path, simulate_broken: bool = False) -> int:
    with tempfile.TemporaryDirectory(prefix="web-persona-") as tmp:
        personas_path = Path(tmp) / "persona.jsonl"
        sample(1, persona_seed, personas_path, dag=True)
        attributes = json.loads(
            personas_path.read_text(encoding="utf-8").splitlines()[0]
        )["attributes"]
    # jobs_dir обязан лежать под $HOME - см. комментарий в mantoz.calibrate.
    outcome = asyncio.run(
        run_persona_trial(attributes, Path.home() / ".cache" / "mantoz", simulate_broken)
    )
    # Контейнер не вернул след вообще - прогон не считается состоявшимся,
    # локальную реконструкцию вместо настоящего следа не подсовываем.
    if not outcome["actions"] and outcome["passed"]:
        outcome["infrastructure_failure"] = True
        outcome["detail"] = "контейнер не вернул след действий"
    result = {
        "task": "web-choice",
        "environment": "web",
        "persona_seed": persona_seed,
        "persona": attributes,
        **outcome,
    }
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # Тихий откат запрещён: инфраструктурный сбой - провал команды с названной
    # причиной. Уход персоны без выбора - честный исход, код не меняется.
    if outcome["infrastructure_failure"]:
        print(f"прогон web не состоялся: {outcome['detail']}", file=sys.stderr)
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
    parser = argparse.ArgumentParser(prog="mantoz.web")
    commands = parser.add_subparsers(dest="command", required=True)
    run_parser = commands.add_parser("run")
    run_parser.add_argument("--persona-seed", required=True, type=int)
    run_parser.add_argument("--out", required=True, type=Path)
    run_parser.add_argument(
        "--simulate-broken-scenario",
        action="store_true",
        help="имитация поломки: сценарий недоступен внутри трайла, прогон обязан упасть",
    )
    verify_parser = commands.add_parser("verify")
    verify_parser.add_argument("--file", required=True, type=Path)
    args = parser.parse_args()
    if args.command == "run":
        sys.exit(run(args.persona_seed, args.out, args.simulate_broken_scenario))
    else:
        sys.exit(verify(args.file))


if __name__ == "__main__":
    main()
