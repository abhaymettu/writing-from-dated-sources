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

## Still open

- The threshold is stated qualitatively ("only days old", "moves in weeks or
  months"). Measured at 2 days (silent) and 9 months (flags). Everything between
  is untested, and the boundary is a guess.
- Only two source types have been tested as failures: a prose status doc and a
  numeric table. Logs, tickets, changelogs, and handoff files are listed in the
  skill but were only ever tested as evaluation tasks, where baseline passes.
- Claude Code and Opus 5 only.
