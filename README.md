# writing-from-dated-sources

A Claude skill for one specific failure: **it copies a stale document's present
tense into new prose.**

## Install it by pasting this

Give your agent this repo and it will set itself up, verify the install, and run
a smoke test with you:

```
Set up https://github.com/abhaymettu/writing-from-dated-sources — follow its AGENTS.md
```

That works in Claude Code, Codex, Copilot CLI, or anything else that can read a
URL and run a shell. It reads [`AGENTS.md`](AGENTS.md), which walks it through
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
| Author's own docs and agent memory | 176 | 0.6% |
| Inherited and third-party repos | 463 | 5.8% |

Staleness is a property of the corpus, not the rule — 8x higher on other
people's repos. But anything under active use gets touched, and across both
corpora almost nothing is older than two months. Treat this as a safety net that
fires a few times a year, not a daily win.

**The threshold survived contact with data.** 30 days was a guess. Both corpora
put the median claim-bearing doc at 10–14 days with a sharp thinning after 30, so
the guess landed in the valley. At 14 days it would fire on 12–20% of all files,
which is noise.

**The case it's really for can't be measured this way.** Documents you *receive* —
a pasted client doc, a forwarded email, an inherited handoff — never touch your
filesystem. That's where staleness is worst and where this most likely earns its
keep.

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
up normally, with nothing said about its age. Re-verified 2/2.

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
[obra/superpowers](https://github.com/obra/superpowers): no guidance ships
without a failing test behind it.

## Related

[`temporal-grounding`](https://github.com/abhaymettu/temporal-grounding) covers
the adjacent failure — a date you assert conflicting with the date already in the
model's context.
