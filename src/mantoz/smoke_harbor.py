import asyncio
import shlex
import tempfile
from pathlib import Path
from typing import override

from harbor.agents.base import BaseAgent
from harbor.environments.base import BaseEnvironment
from harbor.job import Job
from harbor.models.agent.context import AgentContext
from harbor.models.job.config import JobConfig
from harbor.models.trial.config import (
    AgentConfig,
    EnvironmentConfig,
    TaskConfig,
    VerifierConfig,
)

from mantoz.sandbox import resolve_backend

RESULT = "persona-stub completed Harbor task"


class StubPersona(BaseAgent):
    @staticmethod
    @override
    def name() -> str:
        return "persona-stub"

    @override
    def version(self) -> str:
        return "1"

    @override
    async def setup(self, environment: BaseEnvironment) -> None:
        pass

    @override
    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        result = await environment.exec(
            command=f"printf '%s\\n' {shlex.quote(RESULT + ': ' + instruction.strip())}"
        )
        if result.return_code != 0:
            raise RuntimeError(
                "persona command failed: "
                f"return_code={result.return_code}, "
                f"stdout={result.stdout!r}, stderr={result.stderr!r}"
            )
        context.metadata = {"stdout": result.stdout}


async def smoke() -> str:
    with tempfile.TemporaryDirectory(prefix="mantoz-harbor-") as tmp:
        root = Path(tmp)
        task = root / "smoke-task"
        (task / "environment").mkdir(parents=True)
        (task / "environment" / "Dockerfile").write_text(
            "FROM alpine:3.23.4@sha256:"
            "5b10f432ef3da1b8d4c7eb6c487f2f5a8f096bc91145e68878dd4a5019afde11\n"
            "# ponytail: POSIX smoke only; install bash if commands need bash syntax.\n"
            "RUN printf '#!/bin/sh\\nexec /bin/sh \"$@\"\\n' > /bin/bash "
            "&& chmod +x /bin/bash\n"
        )
        (task / "instruction.md").write_text("answer as the smoke persona")
        (task / "task.toml").write_text(
            'schema_version = "1.4"\n\n[environment]\n'
        )

        job = await Job.create(
            JobConfig(
                job_name="mantoz-smoke",
                jobs_dir=root / "jobs",
                n_concurrent_trials=1,
                quiet=True,
                environment=EnvironmentConfig(type=resolve_backend()),
                verifier=VerifierConfig(disable=True),
                agents=[
                    AgentConfig(import_path="mantoz.smoke_harbor:StubPersona")
                ],
                tasks=[TaskConfig(path=task)],
            )
        )
        result = await job.run()
        trial = result.trial_results[0]
        if trial.exception_info:
            raise RuntimeError(trial.exception_info.exception_message)
        if trial.agent_result is None:
            raise RuntimeError("Harbor returned no agent result")
        output = (trial.agent_result.metadata or {}).get("stdout", "") or ""
        if RESULT not in output:
            raise RuntimeError(f"unexpected Harbor result: {output!r}")
        return output.strip()


def main() -> None:
    print(asyncio.run(smoke()))


if __name__ == "__main__":
    main()
