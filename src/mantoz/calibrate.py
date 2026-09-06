import argparse
import asyncio
import shutil
import sys
import tempfile
from pathlib import Path

from harbor.job import Job
from harbor.models.job.config import JobConfig
from harbor.models.trial.config import (
    AgentConfig,
    EnvironmentConfig,
    TaskConfig,
    VerifierConfig,
)

from mantoz.sandbox import resolve_backend

TASK_DIR = Path(__file__).resolve().parents[2] / "application" / "tasks" / "smoke-choice"
PASS_REWARD = 1.0


async def run_trial_result(agent: str, jobs_dir: Path, task_dir: Path = TASK_DIR):
    """Прогоняет задачу через агента Harbor, возвращает TrialResult."""
    job = await Job.create(
        JobConfig(
            job_name=f"mantoz-calibrate-{agent}",
            jobs_dir=jobs_dir,
            n_concurrent_trials=1,
            quiet=True,
            environment=EnvironmentConfig(type=resolve_backend()),
            verifier=VerifierConfig(),
            agents=[AgentConfig(name=agent)],
            tasks=[TaskConfig(path=task_dir)],
        )
    )
    result = await job.run()
    return result.trial_results[0]


def judge_trial(trial) -> tuple[bool, str]:
    """Судит TrialResult: (прошел, строка-исход). Прошел == положительный
    ВЕРДИКТ ВЕРИФИКАТОРА, а не нулевой код агента: крах прогона (exception_info)
    и вердикт (verifier_result.rewards) различимы всегда.
    """
    if trial.exception_info is not None:
        return False, f"крах прогона: {trial.exception_info.exception_message}"
    rewards = (trial.verifier_result.rewards if trial.verifier_result else None) or {}
    reward = float(rewards.get("reward", 0.0))
    if reward >= PASS_REWARD:
        return True, f"вердикт верификатора: пройдено (reward={reward})"
    return False, f"вердикт верификатора: провал (reward={reward})"


async def run_trial(agent: str, jobs_dir: Path, task_dir: Path = TASK_DIR) -> tuple[bool, str]:
    """Прогоняет задачу через агента Harbor и судит вердикт верификатора."""
    return judge_trial(await run_trial_result(agent, jobs_dir, task_dir))


async def run(agents: list[str], mutate_output_extra_blank: bool = False) -> int:
    # jobs_dir обязан лежать под $HOME: Docker Desktop на macOS шарит только
    # /Users, и бинд-монт /logs/verifier из каталога в /var/folders (системный
    # tmp, копия дерева) остается пустым - верификатор не вернет reward.
    # ponytail: корень захардкожен в ~/.cache/mantoz; если шаринг Docker
    # расширят на /var/folders, можно вернуться к системному tempfile.
    jobs_root = Path.home() / ".cache" / "mantoz"
    jobs_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="calibrate-", dir=jobs_root) as tmp:
        task_dir = TASK_DIR
        if mutate_output_extra_blank:
            # Мутация эталона: копия задачи, где решение дописывает лишнюю
            # пустую строку. Строгий верификатор обязан ее отвергнуть.
            task_dir = Path(tmp) / "task-mutated"
            shutil.copytree(TASK_DIR, task_dir)
            (task_dir / "solution" / "solve.sh").write_text(
                "#!/bin/sh\n"
                "# Эталон + лишняя пустая строка (мутация строгости верификатора).\n"
                "printf 'yes\\n\\n' > /app/answer.txt\n"
            )
        outcomes = {}
        for agent in agents:
            passed, line = await run_trial(agent, Path(tmp) / agent, task_dir)
            outcomes[agent] = passed
            print(f"{agent}: {line}")
    if len(agents) == 1:
        return 0 if outcomes[agents[0]] else 1
    # Калибровка держится, когда эталон проходит, а пустышка - нет.
    return 0 if outcomes.get("oracle") and not outcomes.get("nop") else 1


def main() -> None:
    parser = argparse.ArgumentParser(prog="mantoz.calibrate")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--agent", choices=["oracle", "nop"])
    group.add_argument("--both", action="store_true")
    parser.add_argument(
        "--mutate-output-extra-blank",
        action="store_true",
        help="эталонный прогон, но в вывод дописывается лишняя пустая строка",
    )
    args = parser.parse_args()
    agents = ["oracle", "nop"] if args.both else [args.agent]
    sys.exit(asyncio.run(run(agents, args.mutate_output_extra_blank)))


if __name__ == "__main__":
    main()
