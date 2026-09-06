# Mantoz

Test a product on a generated crowd before real people see it.

[Русский](README.ru.md) · [中文](README.zh.md)

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE) [![Stars](https://img.shields.io/github/stars/zarubinvibe/mantoz?style=flat&color=C9A87A)](https://github.com/zarubinvibe/mantoz/stargazers) [![Status](https://img.shields.io/badge/status-working-brightgreen.svg)](https://github.com/zarubinvibe/mantoz) [![Olympuz](https://img.shields.io/badge/olympuz-family-B8D6EA.svg)](https://github.com/zarubinvibe/athena#olympuz-family)

<p align="center"><img src="docs/assets/pantheon/hero.png" alt="Manto in white marble holds an oracular bowl beside a small marble crowd; blue threads run in along the ground and three gold bands leave for a tablet, next to the classical column" width="100%"></p>

<!-- owner-welcome:start -->

> Hello. I am a lawyer with two daughters and a coffee business, so I build in the evening and I cannot run a research round for every idea I have.
>
> Mantoz came out of that. It gives me a first read from a crowd before I spend anybody's time, my own included. It will not tell you what your customers think. It will tell you which of your ideas falls apart the moment a hundred different people touch it.
>
> It sits in the Olympuz family of tools: https://github.com/zarubinvibe/athena#olympuz-family
>
> — Filipp Zarubin

<!-- owner-welcome:end -->

## Contents

- [What This Is](#what-this-is)
- [Why It Helps](#why-it-helps)
- [The Main Advantage](#the-main-advantage)
- [How It Works](#how-it-works)
- [Quickstart](#quickstart)
- [Simple Comparison](#simple-comparison)
- [Simple Words](#simple-words)
- [Safety And Privacy](#safety-and-privacy)
- [Limits](#limits)
- [Star And Contribute](#star-and-contribute)

<!-- beginner-readme:start -->

## What This Is

Mantoz builds a crowd of made-up people, sends every one of them through the same task, and shows how each group answered. The people are generated: age, income, city, habits, what they care about. The task is real work. A survey form, a support chat, a web page, a desktop app. Nothing leaves your machine until you switch on a paid model yourself.

## Why It Helps

You can ship a form and learn a month later that nobody over fifty finished it. Asking real users first costs weeks and a budget you may not have yet. A generated crowd does not replace them. It catches the loud breakages early: the question nobody understood, the button one group never reached, the wording that reads fine to you and to no one else.

## The Main Advantage

**Main advantage:** the verdict comes from a checker that belongs to the task, and it is written many times over, not once.

**Why this is better:** One run of one agent says nothing about a population. Mantoz puts every persona through the task several times, each task carries its own verifier, and free-form answers go to two judges whose disagreement is measured and kept next to the raw text. You read the spread instead of one lucky answer.

## How It Works

Five steps. Each one leaves a file on disk, so a run you interrupt continues from what is already written.

<!-- workflow-diagram:start -->

<p align="center"><img src="docs/assets/pantheon/takt-en.png" alt="Five marble plates in a row, each carved with one step of the work, a single gold band running behind them from the left edge" width="100%"></p>

<!-- workflow-diagram:end -->

| Stage | What happens |
|---|---|
| 1. Crowd | A crowd of personas is generated from a schema |
| 2. Ground | Real statistics pull the crowd toward reality |
| 3. Run | Everyone goes through the same task |
| 4. Verify | The task decides for itself whether an answer passed |
| 5. Report | The runs are aggregated and split by subgroup |

### Step 1: Build the crowd

You say how many people you want and with which seed. Mantoz builds them from a schema of forty dimensions in four groups: background, psychology, capability, behaviour. A dependency graph keeps them coherent, so a nineteen-year-old does not come out with thirty years of management behind him.

**You get:** a reproducible crowd on disk: the same seed always gives the same people.

### Step 2: Pull it toward real statistics

A crowd sampled out of thin air is smooth in a way real populations never are. Import marginals from an open statistical source and the sampler follows those shares instead of its own defaults. Only sources that allow commercial use ship with the project.

**You get:** a crowd whose shares match published statistics, with the source and its license written next to it.

### Step 3: Send everyone through the task

The task lives in one of four environments: a survey form, a support chat, a web page, a desktop app. Every persona goes through it several times, because one run of one agent is an anecdote. Execution goes through Harbor, and the sandbox backend is a config switch: Docker by default, Modal if you pay for it.

**You get:** one trace per run, kept whole, including the answers that failed.

### Step 4: Let the task judge itself

Each task carries its own verifier, so nothing is judged by a general-purpose reviewer that never saw the rubric. Free-form answers go to two judges. Their disagreement is measured, and the raw text of both is written into the verdict, so a strange score can be read rather than guessed at.

**You get:** a verdict per run with the raw judge output kept, not summarised away.

### Step 5: Read it by subgroup

Single runs are counted up to the level of the whole population and of each subgroup, with the aggregation method written into the report rather than left implicit. The thin viewer turns that report into one HTML page. No second frontend, no build step, no server.

**You get:** one page showing how each group answered and where the groups disagree.

## Quickstart

You need macOS or Linux, Python 3.12 and `uv`. Docker as well if you want the sandboxed environments. Three doors below, any of them works.

```bash
git clone https://github.com/zarubinvibe/mantoz.git ~/mantoz
cd ~/mantoz
python3 --version          # 3.12 or newer; the installer says so if yours is older
bash install.sh

claude                     # in Claude Code, then type /mantoz-setup
code .                     # or just open the project in your editor

uv run python -m mantoz.population run --n-runs 3 --seed 7 --task survey --out runs/first.json
uv run python -m mantoz.viewer render --report runs/first.json --out runs/first.html
```

No Git? Download [the ZIP](https://github.com/zarubinvibe/mantoz/archive/refs/heads/main.zip), unpack it, and run the same `bash install.sh` inside. Want the package without a clone? `uv pip install git+https://github.com/zarubinvibe/mantoz.git` installs it straight from the repository. First time here? Open the project in Claude Code and run `/mantoz-setup`: the install goes as a conversation, one question at a time, and nothing is installed without your yes. Already have it? `/mantoz-update` brings it to the current version and shows the changes before touching anything.

Never done this before? [The onboarding](docs/ONBOARDING.md) walks the whole first run step by step and says what you see after every command.

**You get:** a population report on disk and one HTML page you open in a browser, with the split by subgroup already counted.

## Simple Comparison

| Choice | Best when | What you get | What it costs | Where it runs | Trade-off |
|---|---|---|---|---|---|
| **Mantoz** | A whole population has to answer and you do not have one | A generated crowd, task-owned verifiers, a subgroup split | Free; only a live LLM judge costs money | Your own machine | Generated people are not people: loud problems show, quiet ones may not |
| Real user research | The decision is expensive and needs actual humans | What real customers do, with all the surprises | Weeks of work and an agency or panel budget | Out in the world | Too slow and too costly to run on every idea |
| An A/B test in production | The feature already exists and traffic is large | Real behaviour at real scale | Engineering time, plus the cost of shipping a bad variant | Your production servers | You learn after users have already met the mistake |
| Asking one chatbot | You want a quick read on the wording | An answer in ten seconds | Free or a few cents | Somebody else's servers | One voice, no distribution, nobody to disagree |
| MatrAIx-Persona-8B | You want the published research setup itself | The original method and a very large released corpus | Free to read; the corpus is research-licensed | Your machine or a cluster | The persona corpus is research-only, so commercial use is not granted |
| Asking friends and colleagues by hand | You need a sanity check today and nothing more | Honest reactions from people who know you | An hour of somebody's goodwill | A chat window or a kitchen | Five people who all resemble each other are not a population |

## Simple Words

| Word | Simple meaning |
|---|---|
| Repository | The project folder that Git stores and versions |
| Terminal | The window where you type commands |
| Command | One instruction you give the computer |
| Branch | A separate line of changes that does not touch `main` |
| Pull Request | A request to review your change and accept it |
| Persona | One generated person: age, income, city, habits, values |
| Population run | The same task handed to many personas, several times each |
| Verifier | A small program that belongs to the task and decides whether an answer passed |
| Marginals | The share of each answer in real statistics, used to pull the crowd toward reality |

## Safety And Privacy

- Everything runs on your machine. There is no Mantoz server and no account to create.
- `data/` never enters git. A license gate refuses any commit carrying survey data, derived marginals or model weights.
- Grounding ships with one source: Rosstat through tochno.st, CC BY 4.0, commercial use granted in writing.
- A source that forbids redistribution stays marked `local_only`, and nothing derived from it leaves the machine.
- LLM judges are off by default. A free deterministic judge runs unless you pass `--live-provider` yourself.
- Task environments run in Docker. The Modal backend is opt-in and it costs money.

Before any push, read `git diff` and run `sh evals/licence_boundary_gate.sh`.

## Limits

Status: the MVP is closed. Seventeen tickets, all four environments running, the parity checklist green.

- Generated people are not real users. A result is a hypothesis worth checking, not evidence.
- Grounding covers Russian statistics today. Another country needs a source with the same written permission.
- The four environments are deliberately plain: a form, a chat, a page, a desktop window. They are not your product.
- Command output and error messages are in Russian. The documentation is not.

Deeper: [the parity checklist](docs/PARITY.md) compares Mantoz line by line against the published research setup, and [the glossary](docs/CONTEXT.md) explains the words the project uses. The persona method is borrowed as research and cited: [arXiv:2608.04205](https://arxiv.org/abs/2608.04205). Agent execution goes through [Harbor](https://github.com/harbor-framework/harbor), Apache-2.0, as a dependency, see [NOTICE](NOTICE).

## Star And Contribute

Useful? Give Mantoz a star: [https://github.com/zarubinvibe/mantoz](https://github.com/zarubinvibe/mantoz). It takes a second and it decides whether other people ever find the project.

Want to change something? The path is short: fork the repository, create a branch, commit your change, push the branch, then open a Pull Request. Do not push directly to `main`; the release gate rejects it.

Found a problem instead? Open an issue at [https://github.com/zarubinvibe/mantoz/issues](https://github.com/zarubinvibe/mantoz/issues) and say what you ran and what happened.

<!-- beginner-readme:end -->

<!-- pantheon-family:start -->
## Olympuz family

This is one of the public [Olympuz projects](https://github.com/zarubinvibe/athena#olympuz-family). Each row opens the repository or downloads its source as a ZIP.

| Type | Name | What it does | Source |
|---|---|---|---|
| project | Athena | Portable agent OS that restores a complete Claude and Codex setup on a new Mac. | [Repository](https://github.com/zarubinvibe/athena) · [ZIP](https://github.com/zarubinvibe/athena/archive/refs/heads/main.zip) |
| project | Helioz | 24/7 agent work conveyor with verified completion markers and goal-based overnight decisions. | [Repository](https://github.com/zarubinvibe/helioz) · [ZIP](https://github.com/zarubinvibe/helioz/archive/refs/heads/main.zip) |
| project | Mnemazine | Local-first memory system that turns raw inputs into verified reusable knowledge. | [Repository](https://github.com/zarubinvibe/mnemazine) · [ZIP](https://github.com/zarubinvibe/mnemazine/archive/refs/heads/main.zip) |
| project | Themiz | Multi-agent assistant for Russian litigation with local OCR and review by a five-jurist council. | [Repository](https://github.com/zarubinvibe/themiz) · [ZIP](https://github.com/zarubinvibe/themiz/archive/refs/heads/main.zip) |
| project | Zeuz | Factory that turns an idea into a governed multi-agent workflow with gates, observability, and replay. | [Repository](https://github.com/zarubinvibe/zeuz) · [ZIP](https://github.com/zarubinvibe/zeuz/archive/refs/heads/main.zip) |
| project | Lynceuz | Collects public web evidence at zero cost and stops with an honest reason when the safe routes end. | [Repository](https://github.com/zarubinvibe/lynceuz) · [ZIP](https://github.com/zarubinvibe/lynceuz/archive/refs/heads/main.zip) |
| project | Iriz | macOS menu-bar dictation that decodes speech on your own Mac, fixes wrong keyboard layouts, and turns dictation into a ready task for an agent. | [Repository](https://github.com/zarubinvibe/iriz) · [ZIP](https://github.com/zarubinvibe/iriz/archive/refs/heads/main.zip) |
| project | Mantoz | Runs a product past thousands of generated people before real ones see it, and reports how each group answered. | [Repository](https://github.com/zarubinvibe/mantoz) · [ZIP](https://github.com/zarubinvibe/mantoz/archive/refs/heads/main.zip) |
| project | Koiz | A single lesson base for every project. Each failure is taken down to its cause, and the cause stays open until a hook, a gate or a test closes it. | [Repository](https://github.com/zarubinvibe/koiz) · [ZIP](https://github.com/zarubinvibe/koiz/archive/refs/heads/main.zip) |
<!-- pantheon-family:end -->

## License

MIT. See [LICENSE](LICENSE).
