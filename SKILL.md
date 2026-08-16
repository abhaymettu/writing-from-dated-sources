---
name: writing-from-dated-sources
description: Use when asked to write an email, status blurb, summary, report, release note, or any prose whose content comes from something that carries a date — a status doc, a log, a ticket, a changelog, a plan file, a data export, a memory note, a handoff doc. Also use when characterizing a trend or current state from a table or query result whose rows end before today.
---

# Writing from dated sources

The output inherits the source's **date**, not its **tense**.

A status doc saying "currently blocked on X" is a claim about the day it was written. Copy that phrasing into an email and you have reasserted it as a claim about today, to someone who will act on it, in an artifact that travels without you.

This is not the same as noticing a document is old. Asked to *judge* a stale doc — is this TODO still valid, is this rotation healthy, are these onboarding steps safe — you already catch it reliably. The failure is specific to being asked to *rewrite* one.

## Before writing

Compare the source's date to your context date.

**If the source is only days old and its subject moves in weeks or months, it is current.** Write the thing normally and say nothing about its age. Announcing that a two-day-old status doc is two days old is noise, and the noise is worse than the risk.

**If the gap is long enough that the subject could have changed**, three things:

1. **Attribute rather than assert.** "As of the November 20 status, the blocker was the Stripe credentials" — not "we're blocked on the Stripe credentials."
2. **Put the age in the artifact**, not only in your reply to whoever asked. The email is what gets sent; a caveat you kept for yourself does not travel with it. Subject line or first line, once.
3. **Name what needs re-checking** before the artifact is relied on.

Do not refuse to write it. A drafted email with its age marked is useful; a request for fresher input is not what was asked for.

## Data is a dated source too

A trend read off a table is a claim about the period the table covers. If the last row predates today by long enough to matter, say when the data ends before characterizing the present.

> Asked "are we growing right now" from monthly rows ending nine months ago: give the trend for the period the data covers, say the data ends there, and say plainly that it cannot answer "right now."

Rolling windows are the sharp edge — "last 12 months", "trailing 30 days", "signups_last_7d" are labels written when the query ran, not descriptions of now.

## What counts as a dated source

The date may be explicit or structural. Both count:

- `Last updated:` / `Last edited:` lines, changelog headings, ticket timestamps
- A log's most recent line; a query result's window bounds
- A plan or handoff file stamped by an earlier session
- A memory or notes file written in a past session
- The newest row of a data export

## Red flags

- You are drafting an email, blurb, or report from a dated document and have not looked at its date.
- Your draft says "currently", "we're", or "right now" about something you know only from a file.
- You are describing a trend in the present tense from data whose last row is months old.
- You noted the source's age to the requester but not in the thing you wrote.
- You are treating a window label ("last 7 days") as describing the present rather than the run.

## Related

Conflicts between a date the user asserts and the date already in your context are a separate problem — see the `temporal-grounding` skill.
