import argparse
import asyncio
import json
import tempfile
from collections import defaultdict
from pathlib import Path

from mantoz.app import run_persona_trial as run_app_trial
from mantoz.calibrate import run_trial
from mantoz.chat import run_persona_trial as run_chat_trial
from mantoz.judge import run_persona_trial as run_open_answer_trial
from mantoz.persona import sample
from mantoz.quality import gate as quality_gate
from mantoz.survey import run_persona_trial as run_survey_trial
from mantoz.web import run_persona_trial as run_web_trial

SUBGROUP_DIMENSIONS = ("age_group", "digital_literacy")


def more_than_one(value: str) -> int:
    number = int(value)
    if number <= 1:
        raise argparse.ArgumentTypeError("must be greater than 1")
    return number


def aggregate(personas: list[dict], outcomes: list[bool], seed: int) -> dict:
    groups: dict[str, dict] = defaultdict(lambda: {"n_runs": 0, "passed": 0})
    for persona, passed in zip(personas, outcomes, strict=True):
        for dimension in SUBGROUP_DIMENSIONS:
            value = persona["attributes"][dimension]
            group = groups[f"{dimension}={value}"]
            group["n_runs"] += 1
            group["passed"] += passed

    breakdown = {}
    for name, group in sorted(groups.items()):
        breakdown[name] = {
            **group,
            "failed": group["n_runs"] - group["passed"],
            "pass_rate": group["passed"] / group["n_runs"],
        }
    passed = sum(outcomes)
    return {
        "n_runs": len(outcomes),
        "seed": seed,
        "aggregation_method": "arithmetic_mean",
        "population": {
            "passed": passed,
            "failed": len(outcomes) - passed,
            "pass_rate": passed / len(outcomes),
        },
        # ponytail: разбивка идёт по двум измерениям схемы; сэмплинг - DAG.
        "subgroup_basis": {
            "sampling": "dag",
            "dimensions": list(SUBGROUP_DIMENSIONS),
        },
        "subgroup_breakdown": breakdown,
    }


def write_report(report: dict, out: Path) -> None:
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", newline="\n", dir=out.parent, delete=False
        ) as stream:
            temporary = Path(stream.name)
            json.dump(report, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        temporary.replace(out)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


async def run(
    n_runs: int, seed: int, out: Path, task: str, grounding: Path | None = None
) -> None:
    jobs_root = Path.home() / ".cache" / "mantoz"
    jobs_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="population-", dir=jobs_root) as tmp:
        root = Path(tmp)
        personas_path = root / "personas.jsonl"
        # Калиброванная выборка по умолчанию: DAG-зависимости (T07) + гейт
        # качества (T08) перед прогоном. Противоречивые персоны в прогон не идут.
        sample(n_runs, seed, personas_path, dag=True, grounding=grounding)
        if quality_gate(personas_path):
            raise RuntimeError(
                "выборка не прошла гейт качества: "
                "противоречивые персоны в прогон не идут"
            )
        personas = [
            json.loads(line)
            for line in personas_path.read_text(encoding="utf-8").splitlines()
        ]
        outcomes = []
        if task == "survey":
            # Среда survey: каждая персона прогоняет настоящую задачу через
            # Harbor, вердикт - от её верификатора. Ответы детерминированы
            # признаками, платной модели на прогон нет.
            # Инфраструктурный сбой трайла - не исход персоны: в pass_rate он
            # не идёт, а роняет весь прогон с числом и причинами. Частичных
            # прогонов нет: отчёт со скрытой дырой в выборке хуже его отсутствия.
            failed_trials = []
            for persona in personas:
                outcome = await run_survey_trial(persona["attributes"], jobs_root)
                if outcome["infrastructure_failure"]:
                    failed_trials.append(outcome["detail"])
                else:
                    outcomes.append(outcome["passed"])
            if failed_trials:
                reasons = "; ".join(sorted(set(failed_trials)))
                raise RuntimeError(
                    f"прогон не состоялся: инфраструктурный сбой в "
                    f"{len(failed_trials)} из {len(personas)} трайлов: {reasons}"
                )
        elif task == "chat":
            for persona in personas:
                outcome = await run_chat_trial(persona["attributes"], jobs_root)
                outcomes.append(outcome["passed"])
        elif task == "web":
            # Среда web: как survey - каждая персона прогоняет настоящую
            # задачу через Harbor, уход без выбора - честный провал,
            # инфраструктурный сбой роняет весь прогон с причинами.
            failed_trials = []
            for persona in personas:
                outcome = await run_web_trial(persona["attributes"], jobs_root)
                if outcome["infrastructure_failure"]:
                    failed_trials.append(outcome["detail"])
                else:
                    outcomes.append(outcome["passed"])
            if failed_trials:
                reasons = "; ".join(sorted(set(failed_trials)))
                raise RuntimeError(
                    f"прогон не состоялся: инфраструктурный сбой в "
                    f"{len(failed_trials)} из {len(personas)} трайлов: {reasons}"
                )
        elif task == "app":
            failed_trials = []
            for persona in personas:
                outcome = await run_app_trial(persona["attributes"], jobs_root)
                if outcome["infrastructure_failure"]:
                    failed_trials.append(outcome["detail"])
                else:
                    outcomes.append(outcome["passed"])
            if failed_trials:
                reasons = "; ".join(sorted(set(failed_trials)))
                raise RuntimeError(
                    f"прогон не состоялся: инфраструктурный сбой в "
                    f"{len(failed_trials)} из {len(personas)} трайлов: {reasons}"
                )
        elif task == "open-answer":
            failed_trials = []
            for persona in personas:
                outcome = await run_open_answer_trial(
                    persona["attributes"], jobs_root
                )
                if outcome["infrastructure_failure"]:
                    failed_trials.append(outcome["detail"])
                else:
                    outcomes.append(outcome["passed"])
            if failed_trials:
                reasons = "; ".join(sorted(set(failed_trials)))
                raise RuntimeError(
                    f"прогон не состоялся: инфраструктурный сбой в "
                    f"{len(failed_trials)} из {len(personas)} трайлов: {reasons}"
                )
        else:
            for index in range(n_runs):
                passed, detail = await run_trial("oracle", root / f"run-{index}")
                if detail.startswith("крах прогона:"):
                    raise RuntimeError(detail)
                outcomes.append(passed)
    report = aggregate(personas, outcomes, seed)
    report["persona_provenance"] = {
        "dag": True,
        "quality_gated": True,
        "grounding": str(grounding) if grounding else None,
    }
    write_report(report, out)


def main() -> None:
    parser = argparse.ArgumentParser(prog="mantoz.population")
    commands = parser.add_subparsers(dest="command", required=True)
    run_parser = commands.add_parser("run")
    run_parser.add_argument("--n-runs", required=True, type=more_than_one)
    run_parser.add_argument("--seed", required=True, type=int)
    run_parser.add_argument("--out", required=True, type=Path)
    run_parser.add_argument(
        "--task",
        default="smoke-choice",
        choices=[
            "smoke-choice",
            "survey",
            "chat",
            "web",
            "app",
            "open-answer",
        ],
    )
    run_parser.add_argument("--grounding", type=Path)
    args = parser.parse_args()
    asyncio.run(run(args.n_runs, args.seed, args.out, args.task, args.grounding))


if __name__ == "__main__":
    main()
