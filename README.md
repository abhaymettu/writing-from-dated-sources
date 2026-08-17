# writing-from-dated-sources

A Claude skill for one specific failure: **it copies a stale document's present
tense into new prose.**

## Install it by pasting this

Give your agent this repo and it will set itself up, verify the install, and run
a smoke test with you:

```
Set up https://github.com/abhaymettu/writing-from-dated-sources — follow its AGENTS.md
```

Verified on Claude Code. `AGENTS.md` also covers the `~/.agents/skills`
convention other runtimes may read, but skill discovery there is untested. It reads [`AGENTS.md`](AGENTS.md), which walks it through
locating your skills directory, installing, verifying the frontmatter, and
running a scenario that proves the skill actually fires. Manual install is at
the bottom if you'd rather do it yourself.

```
You:  Here's my project's STATUS.md, write me a short update email
      to the client.

      # Status — Payments Migration
      Last updated: 2025-11-20        # ~9 months before "today"
      Current phase: integration testing
      Blocked on: Stripe sandbox credentials from client's finance team

Without the skill:
      Subject: Payments Migration status update

      We're in integration testing. One item is blocking us: we need
      Stripe sandbox credentials from your finance team...

      (Nine months stale. Present tense. Nothing anywhere in the email
       says where it came from. It's about to go to a client.)

With the skill:
      Subject: Payments migration — status check-in (last update Nov 20, 2025)

      Flagging up front that our last written status is from November 20,
      2025, so some of this may have moved since.

      As of that update: phase was integration testing, blocked on...
```

The output inherits the source's **date**, not its **tense**. A doc saying
"currently blocked on X" is a claim about the day it was written; copying that
phrasing forward reasserts it as a claim about today, inside an artifact that
travels without you.

## The part that surprised us

This is **not** an inability to notice old dates. Asked to *judge* stale content,
the baseline is excellent — in a 16-scenario sweep it caught an overdue TODO, a
cert rotation whose scheduled renewal had silently not run, a 16-month-old
onboarding doc, and an incident postmortem with months-overdue action items, all
unprompted and with the right month counts.

Fourteen of sixteen scenarios passed with no skill at all. The two that failed
were the only two that asked for **generation** rather than **evaluation**.

n is small throughout and the runs were author-graded. [`TESTING.md`](TESTING.md)
gives the counts, the isolation method, and a methodology error that produced a
wrong conclusion partway through.

Rewriting a document carries its voice along with its content, and the voice is
present tense.

## Honest limits

**It fires rarely.** Measured against 639 real files across two corpora:

| Corpus | Files | Would trigger (>30d) |
|---|---|---|
| Author's own docs and agent memory | 176 | **1 file** (0.6%) |
| Inherited and third-party repos | 463 | **27 files** (5.8%) |

The first row is a single document — the percentage is not hiding a population.
Staleness is a property of the corpus, not the rule: roughly 10x higher on other
people's repos. But anything under active use gets touched, and across both
corpora almost nothing is older than two months. Treat this as a safety net that
fires a few times a year, not a daily win.

**The threshold is not validated, only situated.** 30 days was a guess. Both
corpora put the median claim-bearing doc at 10–14 days with a sharp thinning
after 30, so the guess sits in a gap in the distribution rather than in the
middle of the mass — at 14 days it would fire on 12–20% of all files. That is an
argument that 30 is not obviously wrong. Nothing here measures a false-positive
or false-negative rate at 30 versus 21 versus 45, so the number remains a guess
with a plausible shape behind it.

**One case is entirely unmeasured.** Documents you *receive* — a pasted client
doc, a forwarded email, an inherited handoff — never touch your filesystem, so
nothing above covers them. They may well be staler than anything measured here.
That is a reason the numbers are a floor rather than the whole picture; it is not
evidence that the skill earns its keep there, and it should not be read as one.

[`baserate.py`](baserate.py) reruns the measurement on any corpus:

```bash
find . -name '*.md' | python3 baserate.py
```

## Staying quiet

The first version leaked. Given a status doc from two days ago it opened with
"Status doc is dated Aug 14, today is Aug 16, so it's 2 days old" before writing
the email — correct, useless, and pure added friction on the common case.

The conflict rule in the sibling skill had a silence threshold; this one didn't.
Added one: a days-old source whose subject moves in weeks or months gets written
up normally, with nothing said about its age. Two runs after the fix behaved
correctly — enough to show the change took, not enough to call it verified.

## Manual install

```bash
git clone https://github.com/abhaymettu/writing-from-dated-sources \
  ~/.claude/skills/writing-from-dated-sources
```

Claude Code discovers it automatically. For other runtimes, `~/.agents/skills/`
works as a cross-runtime alias.

## Evidence

[`TESTING.md`](TESTING.md) has the full log — the sweep that found the failure,
the GREEN runs, the leak control that forced the threshold, and the base-rate
measurements.

Built with the TDD-for-skills approach from
[obra/superpowers](https://github.com/obra/superpowers): every rule here has a
scenario behind it that failed before the rule existed. Those scenarios are 2 of
16, author-written and author-graded.

## Related

[`temporal-grounding`](https://github.com/abhaymettu/temporal-grounding) covers
the adjacent failure — a date you assert conflicting with the date already in the
model's context.
