# Installing Mantoz as a conversation

This is not a page of commands, it is a conversation. Open the project in your agent CLI and say
`/mantoz-setup`. From there I do the talking: I name every step before I take it, ask one question
at a time, and attach my own recommendation to each one so agreeing takes a single word. Nothing on
your disk changes without your yes.

<!-- owner-greeting:start -->

> Hello. My name is Filipp Zarubin. I am a lawyer, and I build products the vibe-coding way.
>
> I have more ideas than time. Every one of them looks convincing right up to the moment somebody
> other than me touches it, and checking properly is expensive: I am not a researcher, so I would
> pay an agency to ask the wrong question for me.
>
> That is where Mantoz came from. It puts together a focus group of people who do not exist and runs
> an idea past them before I spend a month on it. It will not replace real users, and I am not going
> to pretend it will. It cuts the ideas that fall apart on first contact.
>
> Everything is counted on your own machine. Until you switch on a paid model yourself, nothing
> leaves it. Manto takes it from here, and she will not move a step without your consent.
>
> — Filipp Zarubin

<!-- owner-greeting:end -->

## Step 1: I look at what you already have

**What I do:** run `python3 --version`, `uv --version`, `docker --version` and `git --version`, then
say out loud what is here and what is missing. I install nothing yet.

**Why:** half of all failed installs start with nobody telling the person what the machine is
missing. They hit an unreadable error later and conclude the product is broken.

**What changes on disk:** nothing. This step reads, it does not write.

**What you get:** an honest list: this is here, this is not, and this is the part of Mantoz that
will not run without it.

**Fork:** `uv` is missing. It builds the environment and fetches Harbor, which agent execution rests
on, and it brings its own Python 3.12 without touching your system one. Without it you are left with
the offline checks of the tree. Install it, or go on without?
➡️ I recommend installing it: without `uv` neither persona generation nor runs will start.

## Step 2: I put the project on disk

**What I do:** ask where to put it, then fetch the code: `git clone` into the folder you named, or an
unpacked archive if you have no git.

**Why:** every command from here runs out of that folder, and you need to know where to come back
tomorrow. It wants its own folder: Mantoz writes run reports there, and later statistical data, which
runs into gigabytes.

**What changes on disk:** one new folder appears, `~/mantoz` by default, about twenty megabytes.
Nothing outside it is touched.

**What you get:** a working copy and a path I say out loud.

**Fork:** git or archive. A clone updates later with one `/mantoz-update`; an archive means
downloading again and moving your own files across by hand.
➡️ I recommend the clone if git is installed: updating then costs one line.

## Step 3: I set up the environment

**What I do:** run `bash install.sh`. It checks Python, builds the environment through `uv`, installs
Harbor, and finishes by running the offline check of the tree, twenty one items.

**Why:** Harbor is somebody else's Apache-2.0 project, and agent execution rests on it. We take it as
an attributed dependency rather than a copy in the repository, so it has to come off the network.

**What changes on disk:** a `.venv` with Python 3.12 and the dependencies appears inside the project
folder, a few hundred megabytes. The install does not reach outside that folder.

**What you get:** the line `all 21 checks passed`. With no network the installer says so plainly,
names the command that finishes the job later, and still runs every check of the tree.

## Step 4: I build the people

**What I do:** ask how many people you want and which seed, then build them from a schema of forty
traits with a dependency graph behind it.

**Why:** the seed makes a run repeatable. Without it a second run gives different people and any
conversation about the result becomes pointless. The number of people multiplies straight into time.

**What changes on disk:** one JSON file appears under `runs/`, usually under a megabyte.

**What you get:** a file of people you can open and read: age, income, city, habits, values. I show
one of them in full, then repeat the command with the same seed so you watch the same people come
back.

**Fork:** five hundred people or fifty. Five hundred make the groups visible; fifty finish fast and
are enough to see the mechanics.
➡️ I recommend two hundred and seed 7 for the first time.

## Step 5: I run your task, not mine

**What I do:** ask what you would want to check first, pick one of the four environments for it, and
run it several times per person.

**Why:** an example out of the documentation tells you nothing about your product. The install has to
end on your own material, or you never learn whether this thing is any use to you.

**What changes on disk:** a run report appears under `runs/`. With Docker present it builds the
environment image: the first build takes minutes and looks like a freeze, and I warn you before it
starts.

**What you get:** a report where every run keeps its own trace, including the answers that failed the
check.

**Fork:** Docker or no Docker. Without it the four environments will not start, though persona
generation and reports still work. Install Docker now, or look at what already runs?
➡️ I recommend leaving Docker for later if this is your first time here.

## Step 6: I show the result and the data boundary

**What I do:** turn the report into one HTML page, open it, and read it with you: the overall number,
the split by subgroup, the aggregation method. Then I run the license gate.

**Why:** one overall number says almost nothing; the difference between groups is the interesting
part. And the gate shows what people usually remember too late: which data you may pass on and which
you may not.

**What changes on disk:** one HTML file appears next to the report. The gate only reads.

**What you get:** a page in your browser and the line `лицензионная граница: цела`, the license
boundary intact. After that you know what Mantoz does, and you know where its boundary is.

```bash
uv run python -m mantoz.viewer render --report runs/first.json --out runs/first.html
sh evals/licence_boundary_gate.sh
```
