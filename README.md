# Mantoz

Test your idea on five hundred people who do not exist.

[Русский](README.ru.md) · [中文](README.zh.md)

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE) [![Stars](https://img.shields.io/github/stars/zarubinvibe/mantoz?style=flat&color=C9A87A)](https://github.com/zarubinvibe/mantoz/stargazers) [![Status](https://img.shields.io/badge/status-working-brightgreen.svg)](https://github.com/zarubinvibe/mantoz) [![Olympuz](https://img.shields.io/badge/olympuz-family-B8D6EA.svg)](https://github.com/zarubinvibe/athena#olympuz-family)

<p align="center"><img src="docs/assets/pantheon/hero.png" alt="Manto in white marble holds an oracular bowl, a small row of marble figures stands beside her, blue threads run in along the ground and three gold bands leave for a carved tablet, next to the classical column" width="100%"></p>

<!-- owner-welcome:start -->

> Hello. My name is Filipp Zarubin. I am a lawyer, and I build software the vibe-coding way: I have far more ideas than time, and every one of them looks convincing right up to the moment somebody other than me touches it.
>
> Checking them properly is expensive. I am not a researcher and not a marketer, so if I order a survey I overpay and still ask the wrong question. So I built myself a focus group of people who do not exist, and I run every new idea past it before I spend a month on it.
>
> This does not replace real users, and I will not pretend otherwise. It cuts the ideas that fall apart on first contact. And watching five hundred invented people argue with your wording turns out to be a genuinely good time.
>
> Mantoz is one of the [Olympuz tools](https://github.com/zarubinvibe/athena#olympuz-family), and they all follow the same rules.
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

Mantoz builds you a focus group of people who are not real. Each one has an age, an income, a city, habits and things they care about, and those traits are wired to each other, so no nineteen-year-old turns up with thirty years of management behind him. Then every one of them goes through your task: fills in the form, writes to support, clicks through the page, works inside the app.

## Why It Helps

You had an idea. Testing it on real people costs weeks and money, and if you are not a researcher you will also do it badly: wrong question, wrong sample, wrong conclusion. Mantoz gives you the first pass. It will not tell you what your customers think. It shows you which sentence falls apart, which button one group never reaches, and where the forty-year-olds from a small town answer nothing like you expected.

## The Main Advantage

**Main advantage:** the answer is graded by a checker that lives inside the task, and it grades as many times as you ask.

**Why this is better:** Ask a model once and you get one answer and no spread at all. Here every person goes through the task several times, free-form answers are read by two judges, the gap between them is measured, and the raw text stays in the verdict. You look at the spread instead of one lucky reply.

## How It Works

Five steps. Each one leaves a file behind, so a run you interrupt picks up where it stopped.

<!-- workflow-diagram:start -->

<p align="center"><img src="docs/assets/pantheon/takt-en.png" alt="Five marble plates in a row, each carved with one step of the work, a single gold band running behind them from the left edge" width="100%"></p>

<!-- workflow-diagram:end -->

| Stage | What happens |
|---|---|
| 1. People | Five hundred invented people are generated from a schema |
| 2. Statistics | Real statistics make them look like a country |
| 3. Run | Every one of them goes through your task |
| 4. Verify | The task decides for itself whether an answer passed |
| 5. Report | The answers are counted up and split by group |

### Step 1: Build the people

You say how many people you want and with which seed. Mantoz builds them out of forty traits in four groups: background, psychology, capability, behaviour. A dependency graph keeps them coherent, so nobody comes out nineteen years old with thirty years of management behind him.

<p align="center"><img src="docs/assets/pantheon/stage-1-population.png" alt="A marble mould on a long table, twelve identical small marble figures already standing in rows beside it" width="100%"></p>

**You get:** a reproducible set of people on disk: the same seed always gives you the same five hundred.

### Step 2: Make them look real

People sampled out of thin air are too smooth: a real country never is. Import the shares from an open statistical source and the sampler follows those instead of its own defaults. Only sources that permit commercial use ship with the project.

<p align="center"><img src="docs/assets/pantheon/stage-2-ground.png" alt="Five marble slabs of different heights, and in front of each a group of figures whose count matches its height" width="100%"></p>

**You get:** people whose shares match published statistics, with the source and its license written next to them.

### Step 3: Send them through the task

The task lives in one of four environments: a survey form, a support chat, a web page, an app window. Every person goes through it several times, because one run of one agent is an anecdote. Execution goes through Harbor, and the sandbox is a config switch: Docker by default, Modal if you pay for it.

<p align="center"><img src="docs/assets/pantheon/stage-3-run.png" alt="A single marble doorway with a queue of identical figures walking through it, left to right along one blue thread" width="100%"></p>

**You get:** one trace per run, kept whole, including the answers that failed.

### Step 4: Let the task grade it

Each task carries its own checker, so nothing is graded by a general-purpose reviewer that never saw the rubric. Free-form answers go to two judges. The gap between them is measured, and the raw text of both is written into the verdict, so a strange score can be read instead of guessed at.

<p align="center"><img src="docs/assets/pantheon/stage-4-verify.png" alt="A marble balance weighing a carved tablet against a plain weight, with two marble seals standing guard" width="100%"></p>

**You get:** a verdict per run with the raw judge output kept, not summarised away.

### Step 5: Read it by group

Single runs are counted up to the level of everyone and of each group, with the aggregation method written into the report rather than left implicit. The thin viewer turns that report into one HTML page. No second frontend, no build step, no server.

<p align="center"><img src="docs/assets/pantheon/stage-5-report.png" alt="Nine blue threads gathering at a marble block and leaving as three gold bands that land as grooves of different length" width="100%"></p>

**You get:** one page showing how each group answered and where the groups split.

## Quickstart

You need macOS or Linux, Python 3.12 and `uv`. Docker too, if you want the task environments themselves. Three doors below, any of them works.

```bash
git clone https://github.com/zarubinvibe/mantoz.git ~/mantoz
cd ~/mantoz
python3 --version          # 3.12 или новее; установщик скажет, если у тебя старее
bash install.sh

claude                     # в Claude Code дальше набери /mantoz-setup
code .                     # или просто открой проект в редакторе

uv run python -m mantoz.population run --n-runs 3 --seed 7 --task survey --out runs/first.json
uv run python -m mantoz.viewer render --report runs/first.json --out runs/first.html
```

No Git? Download [the ZIP](https://github.com/zarubinvibe/mantoz/archive/refs/heads/main.zip), unpack it and run the same `bash install.sh` inside. Want the package without a clone? `uv pip install git+https://github.com/zarubinvibe/mantoz.git` installs it straight from the repository. First time here? Open the project in Claude Code and run `/mantoz-setup`: the install goes as a conversation, one question at a time, and nothing lands on your disk without your yes. Already installed? `/mantoz-update` brings you to the current version and shows the changes before it touches anything.

Never done this before? [The onboarding](docs/ONBOARDING.md) walks the whole first run step by step and says what you see after every command.

**You get:** a report on disk and one HTML page: how each group answered, and where the groups split.

## Simple Comparison

| Way to check | Best when | What you get | What it costs | Where it runs | Trade-off |
|---|---|---|---|---|---|
| **Mantoz** | The idea is still an idea and you need a first read | Five hundred answers with the split by age, income and city | Free, unless you switch on a live judge yourself | Your own machine | These people are invented: the loud problems surface, the quiet ones may not |
| Hiring a research agency | The decision is expensive and has to hold up in front of investors | Real behaviour of real customers, gathered by people who know how | Weeks, and a budget per wave | Out in the world | Too slow and too costly to spend on an idea you may drop on Friday |
| An A/B test in production | The feature is already built and the traffic is there | Real behaviour at real scale, no guessing | Engineering time, plus whatever a bad variant costs you | Your production servers | You find out after your users have already met the mistake |
| Asking a model once | You want a gut check on one sentence | An answer in ten seconds | Free or a few cents | Somebody else's servers | One voice, no spread, and nobody in the room who disagrees |
| MatrAIx-Persona-8B | You want the published research rig itself | The original method and a very large released corpus | Free to read, research-licensed to use | Your machine or a cluster | The persona corpus is research-only, so commercial use is not granted |
| Asking friends and colleagues | You need a sanity check today and nothing more | Honest reactions from people who know you | An hour of somebody's goodwill | A chat window or a kitchen | Five people who all resemble each other cannot disagree with each other |

## Simple Words

| Word | Simple meaning |
|---|---|
| Repository | The project folder that Git stores and versions |
| Terminal | The window where you type commands |
| Command | One instruction you give the computer |
| Branch | A separate line of changes that does not touch `main` |
| Pull Request | A request to review your change and accept it |
| Persona | One invented person: age, income, city, habits, values, wired together so they hold up |
| Population run | The same task handed to hundreds of those people, several times each |
| Verifier | A small program that belongs to the task and decides whether an answer passed |
| Marginals | The share of each answer in real statistics, used to make the invented people look like a country |

## Safety And Privacy

- Everything runs on your machine. There is no Mantoz server and no account to create.
- `data/` never enters git. A license gate refuses any commit carrying survey data, derived numbers or model weights.
- One statistical source ships with the project: Rosstat through tochno.st, CC BY 4.0, commercial use granted in writing.
- A source that forbids passing data on is marked `local_only`, and nothing derived from it leaves your machine.
- Live LLM judges are off. Until you pass `--live-provider` yourself, a free deterministic judge does the grading.
- Task environments run in Docker. The Modal backend is opt-in and it costs money.

Before any push, read `git diff` and run `sh evals/licence_boundary_gate.sh`.

## Limits

Status: the MVP is closed. Seventeen tickets, four environments running, the parity checklist green.

- These people are invented. A result is a hypothesis worth checking, not evidence you can quote.
- The statistics behind them are Russian. Another country needs a source with the same written permission.
- The four environments are deliberately plain: a form, a chat, a page, an app window. They are not your product.
- Command output and error messages are in Russian. The documentation is not.

Deeper: [the parity checklist](docs/PARITY.md) compares Mantoz line by line against the published research rig, and [the glossary](docs/CONTEXT.md) explains the words the project uses. The persona method is borrowed as research and cited: [arXiv:2608.04205](https://arxiv.org/abs/2608.04205). Agent execution goes through [Harbor](https://github.com/harbor-framework/harbor), Apache-2.0, as a dependency, see [NOTICE](NOTICE).

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
| project | Mantoz | Puts an idea in front of five hundred people who do not exist, then shows how each group answered. | [Repository](https://github.com/zarubinvibe/mantoz) · [ZIP](https://github.com/zarubinvibe/mantoz/archive/refs/heads/main.zip) |
| project | Koiz | A single lesson base for every project. Each failure is taken down to its cause, and the cause stays open until a hook, a gate or a test closes it. | [Repository](https://github.com/zarubinvibe/koiz) · [ZIP](https://github.com/zarubinvibe/koiz/archive/refs/heads/main.zip) |
<!-- pantheon-family:end -->

## License

MIT. See [LICENSE](LICENSE).
