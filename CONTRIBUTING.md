# Contributing to Mantoz

<p align="center"><img src="docs/assets/pantheon/doc-contributing.png" alt="Two marble plates on a low table, the left one carved with three lines and the right one blank and waiting, a gold band lying in front of it" width="100%"></p>

Thanks for looking. Small, specific changes get merged fastest.

## Set up

```bash
git clone https://github.com/zarubinvibe/mantoz.git
cd mantoz
bash install.sh
uv run pytest
uv run ruff check .
```

`install.sh` names anything it could not do instead of failing quietly. If it says uv or Docker is
missing, the offline checks still run and tell you whether the tree is sound.

## The path of a change

1. Fork the repository.
2. Create a branch: `git checkout -b fix-survey-timeout`.
3. Make the change and add a test for it.
4. Run `uv run pytest`, `uv run ruff check .` and `bash scripts/mantoz-selfcheck.sh --selftest`.
5. Run `sh evals/licence_boundary_gate.sh` if you touched anything under `config/` or grounding.
6. Commit with a `<type>: <description>` message: `fix: survey environment stops waiting after 30s`.
7. Push the branch and open a Pull Request.

Do not push to `main` directly. The release gate rejects it.

## What gets merged

- A bug fix with a test that fails before it and passes after.
- A new task in `application/tasks/` that carries its own verifier.
- A new sandbox backend behind Harbor's `BaseEnvironment`, added beside the existing ones.
- Documentation that corrects something wrong.

## What does not

- A grounding source without written permission for commercial use. Read the terms on the page that
  actually hands out the file, not the project description page, and quote them in the Pull Request.
- Anything that puts data, derived marginals or model weights under version control.
- A vendored copy of Harbor. It stays a declared dependency with attribution in `NOTICE`.
- Verification reduced to one or two reviewing agents. Verification here is task-owned and
  population-scale on purpose.
- A second planning tree. Requirements live in `queue/GOAL.md`, decisions in `docs/DECISIONS.md`.

## Reporting a problem

Open an issue and say what you ran, what you expected and what happened. Paste the command and the
first lines of the error. A run that fails in one environment but works in another is useful
information, so mention which of the four you used.

Security issues go to [SECURITY.md](SECURITY.md) instead of a public issue.
