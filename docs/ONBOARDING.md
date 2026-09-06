# Onboarding: your first Mantoz run

<p align="center"><img src="assets/pantheon/doc-onboarding.png" alt="Marble bowl on a low step under daylight, one small marble figure standing in front of it with a single blue thread on the floor, the family column to the right" width="100%"></p>

Written for someone who has never done this before. Every step says what to type and what shows up
on screen afterwards. Fifteen minutes end to end, most of it waiting for downloads.

You will finish with a report about a crowd of a few hundred generated people who all filled in the
same survey, and one HTML page that shows how each group answered.

---

## Step 1. Open the terminal

On macOS press `Cmd + Space`, type `Terminal`, press Enter. On Linux open your terminal app.

**On screen:** a window with a prompt, ending in `$` or `%`. That is where the commands go.

## Step 2. Check that Python is there

```bash
python3 --version
```

**On screen:** something like `Python 3.12.4`. If the number is lower than 3.12, keep going anyway.
Step 4 installs the right version without touching your system Python. If the command is not found
at all, install Python from [python.org](https://www.python.org/downloads/) first.

## Step 3. Get the code

```bash
git clone https://github.com/zarubinvibe/mantoz.git ~/mantoz
cd ~/mantoz
```

**On screen:** a few lines counting objects, then `Resolving deltas: 100%`. After `cd` the prompt
usually shows `mantoz`.

No Git on the machine? Download
[the ZIP](https://github.com/zarubinvibe/mantoz/archive/refs/heads/main.zip), unpack it, and `cd`
into the unpacked folder instead.

## Step 4. Install uv

`uv` is the tool that builds the environment and fetches Harbor.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**On screen:** a progress line, then `installed uv`. Close the terminal and open it again, or run
`source ~/.bashrc`, so the shell finds the new command. Check it with `uv --version`.

## Step 5. Run the installer

```bash
bash install.sh
```

**On screen:** the version of Python it found, then `dependencies installed, Harbor included`, then
a list of checks, each starting with `ok`, and finally `all 21 checks passed`.

If a line starts with `!!`, read it: the installer names exactly what is missing and the command
that finishes the job. A missing Docker is fine for now.

## Step 6. Generate a crowd and look at it

```bash
uv run python -m mantoz.persona sample --n 200 --seed 7 --dag --out runs/people.json
```

**On screen:** nothing, which means it worked. The file `runs/people.json` now holds two hundred
generated people. Open it, or count them:

```bash
python3 -c "import json;print(len(json.load(open('runs/people.json'))))"
```

**On screen:** `200`.

The `--seed 7` part matters: run the same command again and you get exactly the same two hundred
people. Change the seed and you get a different crowd.

## Step 7. Send the crowd through a survey

```bash
uv run python -m mantoz.population run --n-runs 3 --seed 7 --task survey --out runs/first.json
```

**On screen:** progress lines while the runs go through, then the command ends. `--n-runs 3` means
every persona answers three times, because one answer proves nothing about a person, let alone a
population.

**If it stops with a Docker error:** the survey environment needs Docker. Install
[Docker Desktop](https://www.docker.com/products/docker-desktop/), start it, and run the command
again.

## Step 8. Turn the report into a page

```bash
uv run python -m mantoz.viewer render --report runs/first.json --out runs/first.html
open runs/first.html
```

On Linux use `xdg-open runs/first.html`.

**On screen:** a page in your browser with the aggregate result, the split by subgroup, and the
method used to aggregate written out rather than assumed.

## Step 9. Check the license boundary before you commit anything

```bash
sh evals/licence_boundary_gate.sh
```

**On screen:** `лицензионная граница: цела`. That gate refuses to let survey data, derived
marginals or model weights reach git. Run it before every push, especially if you added a data
source of your own.

## Step 10. Try another environment

The survey is one of four. Swap the task and the same crowd goes through a support chat, a web
page, or a desktop app:

```bash
uv run python -m mantoz.population run --n-runs 3 --seed 7 --task chat --out runs/chat.json
```

**On screen:** the same shape of output, from a different environment.

---

## Keeping it current

A new version lands every so often. In Claude Code, run `/mantoz-update`: it shows what changed
before touching anything, pulls fast-forward only, leaves your `data/`, your runs and your `.env`
alone, and re-runs both checks afterwards. Without an agent, the same thing by hand:

```bash
cd ~/mantoz
git pull --ff-only origin main
uv pip install -e .
bash scripts/mantoz-selfcheck.sh --selftest
```

**On screen:** the list of commits that arrived, then the checks passing again.

## Where to go next

- [The parity checklist](PARITY.md) — what Mantoz has, line by line, and what it deliberately does not.
- [The decisions](DECISIONS.md) — why the sandbox is pluggable, why Harbor is a dependency, why one
  data source was thrown out after its terms were read properly.
- [The glossary](CONTEXT.md) — the words used across the project.

## If it was useful

Give the project a star: [https://github.com/zarubinvibe/mantoz](https://github.com/zarubinvibe/mantoz).
It takes a second and it decides whether anyone else ever finds it.

Want to change something? The path is short: fork the repository, create a branch, commit your
change, push the branch, then open a Pull Request. Do not push directly to `main`; the release gate
rejects it. Details in [CONTRIBUTING.md](../CONTRIBUTING.md).

Found a problem instead? Open an issue at
[https://github.com/zarubinvibe/mantoz/issues](https://github.com/zarubinvibe/mantoz/issues) and
say what you ran and what happened.
