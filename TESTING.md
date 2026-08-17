# Evidence

Split out of the `temporal-grounding` skill once the failure it covers turned out
to be a different one. That repo's TESTING.md holds the full RED/GREEN log for
both; this file records what is specific to this skill.

All runs: Claude Code, Opus 5, isolated with

    claude -p "$PROMPT" --tools "Skill" --strict-mcp-config --mcp-config '{"mcpServers":{}}'

`--tools` alone is not isolation — MCP servers stay live and can reach the network.

## The failure

Found by a sweep of 16 scenarios across four application areas (durable
artifacts, dates inside pasted content, timezones and DST, data recency and
stale agent sessions). Fourteen passed without any skill. The two that failed
were the only two that asked for *generation* rather than *evaluation*.

**Status email from a `STATUS.md` dated 2025-11-20**, context date 2026-08-16:

> "We're in integration testing... One item is blocking us: we need Stripe
> sandbox credentials... we estimate roughly three weeks to launch."

Present tense throughout, nine months stale, no mention of the source's age
anywhere — including in the email that would have been sent to the client.

**MAU table ending 2025-11, asked "are we growing right now":** correctly refused
the trailing-12-month average for want of data, then answered "growing, but
decelerating" in the present tense, never noting the export ends nine months back.

## Why evaluation passes and generation fails

The same sweep asked the model to *judge* stale content in four other scenarios —
an overdue TODO, a cert rotation whose scheduled renewal had silently not run, a
16-month-old onboarding doc, an incident postmortem with months-overdue action
items. All four were caught unprompted, several with the exact month count.

So this is not an inability to notice old dates. It is that rewriting a document
carries its voice along with its content, and the voice is present tense.

## GREEN

Both failing scenarios pass with the skill. The status email now carries its age
in the subject line and first line, where it travels to the recipient, rather
than in a caveat to the requester. The MAU answer states the data ends 2025-11
and attributes the trend to that period before declining to characterize now.

## The leak, and the threshold it forced

A control ran the same status doc dated 2026-08-14 — two days old. The first
version of this guidance leaked onto it, opening with "Status doc is dated Aug
14, today is Aug 16, so it's 2 days old" before the email. Correct and useless:
pure added friction on the common case, which is the cost this skill exists to
avoid paying.

The conflict rule in `temporal-grounding` had a silence threshold and this did
not. Added one — days-old source whose subject moves in weeks or months means
write normally and say nothing. Re-ran: 2/2 fresh-doc runs write the email
straight, and the nine-month case still flags. Verified again after the split.

## Base rate on a real corpus

Every result above measures what happens *when* a stale source is involved.
Nothing measured how often that actually occurs.

**A correction first.** The first version of `baserate.py` used a claim regex with
an optional apostrophe — `\b(?:we|i)['’]?re\b` — which matched the plain word
"were", ordinary past tense and the opposite of a present-state claim. It also
used integer floor division for every percentage, so it could not reproduce its
own headline figures. Both are fixed; `TODAY` is no longer a hardcoded constant
either, which is an embarrassing bug for a staleness tool. Every number below is
post-fix and roughly half what was first published. Reproduce with
`BASERATE_TODAY=2026-08-16`.

Two corpora, 613 files. Corpus 1 is 68 agent memory files plus project docs
(README, DECISIONS, NEXT, STATUS, PLAN, NOTES) across 53 repos, all written and
maintained by this author. Corpus 2 is markdown from inherited and third-party
repos — another person's working-notes repo, three plugin marketplaces, a
vendored product repo, and team repos at work — where the effective date is the
upstream commit date.

| | Corpus 1 (own) | Corpus 2 (inherited) |
|---|---|---|
| files | 150 | 463 |
| make a present-state claim | 25 (16.7%) | 76 (16.4%) |
| median age of those | 15 days | 15 days |
| oldest | 113 days | 45 days |
| **would trigger (>30d)** | **1 (0.7%)** | **14 (3.0%)** |
| would trigger (>14d) | 13 (8.7%) | 40 (8.6%) |
| would trigger (>60d) | 1 (0.7%) | 0 (0%) |

Inherited repos run about **4.5x** higher, which confirms staleness is a corpus
property rather than a property of the rule. But the cliff is present in both:
past 60 days there is exactly one file in 613, and the inherited corpus tops out
at 45 days. Anything under active use gets touched.

**The threshold is situated, not validated.** 30 days was a guess. Both corpora
put the median claim-bearing doc at 15 days with sharp thinning after 30, so the
guess sits in a gap rather than in the mass — at 14 days it would fire on ~8.7%
of all files. That argues 30 is not obviously wrong. It does not measure a
false-positive or false-negative rate at 30 versus 21 versus 45, and no such
measurement exists here.

**Honest read on value.** A low-frequency safety net, not a daily win. The team
code repos contributed zero triggering files because they contain almost no prose
docs at all.

**Blind spot.** This covers files on disk that someone writes or has checked out.
The failure mode is about sources you *receive* — a client doc pasted into chat,
a forwarded email, an inherited handoff — which never appear in a filesystem
scan. Nothing here measures those, and their absence is not evidence either way.

**What this implies for collecting data from other users.** The useful signal is
not how often the skill fires. It is the age distribution of the sources people
actually write from: a histogram of integers, no content, no paths. That single
histogram is what decides the threshold, and it is the cheapest thing to collect
that is worth collecting.

## Still open

- The threshold is stated qualitatively ("only days old", "moves in weeks or
  months"). Measured at 2 days (silent) and 9 months (flags). Everything between
  is untested, and the boundary is a guess.
- Only two source types have been tested as failures: a prose status doc and a
  numeric table. Logs, tickets, changelogs, and handoff files are listed in the
  skill but were only ever tested as evaluation tasks, where baseline passes.
- Claude Code and Opus 5 only.
