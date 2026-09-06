# Agent Rules — Mantoz

Rules for any coding agent working in this repository. `CLAUDE.md`, `GEMINI.md`,
`.github/copilot-instructions.md` and `.cursor/rules/olympuz.mdc` all point here.

## What this project is

Mantoz is population-scale, persona-driven evaluation infrastructure: it generates a crowd of
personas, runs every one of them through the same task in one of four environments
(survey / chat / web / app), verifies each run with a verifier owned by the task, and aggregates
the outcome to the population and subgroup level.

## First contact with a stranger

A newcomer starts in chat, not on a page: send them to [docs/ONBOARDING-CHAT.md](docs/ONBOARDING-CHAT.md) (`docs/ONBOARDING-CHAT.ru.md`, `docs/ONBOARDING-CHAT.zh.md`) and walk it with them, one question at a time, taking no step without their yes.

## Build, run, test

```bash
uv venv --python 3.12 && uv pip install -e .   # install
uv run python -m mantoz.population run --n-runs 3 --seed 7 --task survey --out runs/first.json
uv run pytest                                   # tests
uv run ruff check .                             # lint
bash scripts/mantoz-selfcheck.sh --selftest     # offline self-check, no network, no Docker
sh evals/licence_boundary_gate.sh               # license boundary, run before every push
```

Harbor (`harbor==0.22.0`) is a declared dependency. Never vendor it, never fork it, never rename
it. Attribution lives in `LICENSE` and `NOTICE` and stays there.

## Hard rules

- **Data licenses are gates, not promises.** `data/` never enters git. A source that forbids
  redistribution is marked `local_only` in `config/grounding.json`, and nothing derived from it —
  including marginals — leaves the machine. `evals/licence_boundary_gate.sh` enforces this; if you
  change grounding, run it before you commit.
- **Only sources with written commercial permission ship as production grounding.** Today that is
  Rosstat/CBR through tochno.st, CC BY 4.0. A new source is added only after its terms are read on
  the page that actually hands out the file, not on the project description page.
- **Secrets never enter the repository.** Use `.env` or a secret manager.
- **Parity is a checklist, not a feeling.** `docs/PARITY.md` plus `uv run python -m mantoz.parity_gate`.
  A row may be absent only with an exact `OUT-NN` identifier from `queue/GOAL.md`. Prose is not a
  justification.
- **Verification stays population-scale.** Task-owned verifier, `n_runs` above one, statistical
  aggregation. Do not reduce it to one or two reviewing agents.
- **The sandbox backend stays pluggable.** At least two live implementations behind Harbor's
  `BaseEnvironment`: Docker/k3s as the free default, Modal as a paid opt-in. Do not hardcode one.
- **One planning source of truth.** EARS requirements in `queue/GOAL.md` plus `docs/DECISIONS.md`.
  Do not add a second planning tree.

## Style

- Files stay under 800 lines, functions under 50.
- Validate at the boundary, handle errors explicitly, do not swallow failures.
- Prefer the standard library and what is already installed over a new dependency.
- Before writing new code, look for it in the repository first.

## Publication

The public repository is a cut of the private one, not a mirror. Plans, prompts, runtime state and
local paths stay private. Any push to a public remote goes through the release gate; a red gate
means no push. Read `git diff` before every external action, and never change repository
visibility without an explicit instruction from the owner.
