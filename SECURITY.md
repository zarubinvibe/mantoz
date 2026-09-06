# Security and Privacy

<p align="center"><img src="docs/assets/pantheon/doc-security.png" alt="An unbroken marble boundary wall, a closed marble chest resting on the near side, five blue threads stopping dead at the foot of the wall" width="100%"></p>

## Reporting a vulnerability

Do not open a public issue. Write to the owner through
[a GitHub security advisory](https://github.com/zarubinvibe/mantoz/security/advisories/new).
Say what you ran, what you saw and what an attacker could do with it. Expect a first answer within
a few days.

## What Mantoz touches

| Surface | What actually happens |
|---|---|
| Files | Reads the repository and writes to the output path you pass with `--out`. Nothing else is touched. |
| Network | No calls at all in the default path. A live LLM judge reaches its provider only after you pass `--live-provider`. The Modal backend reaches Modal only when you select it. |
| Shell | Task verifiers are shell scripts inside `application/tasks/*/tests/`. They run inside the task environment, not on your host. |
| Sandbox | Task environments run in Docker containers built from the task's own `Dockerfile`. Docker is the default; Modal is opt-in and paid. |
| Secrets | Read from the environment or `.env`, never committed. `.gitignore` blocks `.env`, `*secret*`, `*credential*`, `*.pem` and private keys. |
| Telemetry | None. There is no Mantoz server, no account and no usage reporting. |
| Rollback | Every run writes a JSON report to the path you named. Delete the file and nothing remains. |

## The data boundary

This is the part worth reading twice.

Mantoz calibrates generated personas against real statistics. Statistical sources come with very
different terms, and one of them forbids passing the data on **in any form, including derived
figures**. So the boundary is a gate rather than a promise:

- `data/` is in `.gitignore` and never enters version control.
- `config/grounding.json` records, per source, whether commercial use is allowed and whether
  redistribution is allowed. A source that is not cleared for commercial use is marked
  `local_only: true`.
- `evals/licence_boundary_gate.sh` fails the build if data, derived marginals or model weights
  appear under git, if `data/` stops being ignored, or if a restricted source loses its marking.
- The only source shipped as production grounding is Rosstat/CBR through tochno.st, CC BY 4.0,
  where commercial use is granted in writing.

Run the gate before every push:

```bash
sh evals/licence_boundary_gate.sh
```

## What Mantoz does not protect you from

- A task environment you wrote yourself. Its `Dockerfile` and its verifier run with whatever you
  put in them.
- A live LLM provider you switched on. Prompts and answers go to that provider under its terms.
- Conclusions drawn from simulated people as if they came from real users.
