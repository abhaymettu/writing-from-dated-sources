# Setup instructions for the agent

You were given a link to this repository. The person you are working with wants
this skill installed. Do the steps below in order, run each verification, and
tell them the result in plain language as you go. Do not skip a verification
because a step "obviously worked."

If any step fails, stop and report exactly what failed. Do not improvise an
alternative install location.

## Step 1 — Find the skills directory

| Runtime | Directory |
|---|---|
| Claude Code | `~/.claude/skills/` |
| Codex, Copilot CLI, Gemini CLI | `~/.agents/skills/` |
| Anything else | `~/.agents/skills/` is the cross-runtime convention |

```bash
ls -d ~/.claude/skills 2>/dev/null || ls -d ~/.agents/skills 2>/dev/null || echo "NEITHER EXISTS"
```

If neither exists, create the one matching the runtime you are running in.

**Tell them:** which directory you are installing into.

## Step 2 — Install

```bash
git clone https://github.com/abhaymettu/writing-from-dated-sources \
  <SKILLS_DIR>/writing-from-dated-sources
```

If the directory already exists, `git -C <SKILLS_DIR>/writing-from-dated-sources
pull` instead. Do not delete an existing directory without asking first.

**Verify:**

```bash
head -4 <SKILLS_DIR>/writing-from-dated-sources/SKILL.md
```

The output must show YAML frontmatter with `name: writing-from-dated-sources`.

## Step 3 — Confirm discovery

Skills are read at session start. The person needs to start a new session before
this one is visible.

**Tell them:** "Installed. Start a new session, then I can verify it's working."

Do not claim the skill is active in the current session. It is not.

## Step 4 — Smoke test (run this in the NEW session)

Two runs. The second matters more than the first, because it checks the skill
stays *quiet* when it should.

**4a — should flag.** A status doc old enough that its claims may have moved:

```bash
claude -p 'Here is my STATUS.md, write a short update email to the client.

# Status — Payments Migration
Last updated: 2025-11-20
Current phase: integration testing
Blocked on: Stripe sandbox credentials from the client finance team'
```

**Pass:** the drafted email itself carries the source date — a subject line or
opening line naming November 2025, and claims attributed ("as of that update,
the blocker was...") rather than asserted in the present tense.

**Fail:** the email says "we're currently blocked on..." with no mention of where
that came from. Note: a caveat addressed to *you* but absent from the email body
is also a fail — the email is what gets sent.

**4b — should stay silent.** Same doc, dated two days before today. Replace the
date below with an actual recent date first:

```bash
claude -p 'Here is my STATUS.md, write a short update email to the client.

# Status — Payments Migration
Last updated: <TWO DAYS AGO>
Current phase: integration testing
Blocked on: Stripe sandbox credentials from the client finance team'
```

**Pass:** a normal email, no commentary about the document's age.

**Fail:** it announces the doc is two days old before writing. That is the leak
this skill was specifically tuned to avoid; report it as a bug on the repo.

**Tell them** the result of both runs.

## Step 5 — Set expectations honestly

Tell them plainly:

- This fires rarely. Measured across 639 real files, 0.6% of a person's own docs
  and 5.8% of inherited repos are old enough to trigger it.
- It is a safety net for a failure that is quiet and consequential — a stale
  claim leaving in an artifact someone else acts on — not a daily assistant.
- They can measure their own corpus: `find . -name '*.md' | python3 baserate.py`
  from inside the installed directory.

## Optional — the sibling skill

There is a companion for a related failure: a date the user asserts conflicting
with the date already in your context (a "today is..." pasted from an old email).

Ask whether they want it. If yes, repeat Steps 1-4 with
`https://github.com/abhaymettu/temporal-grounding`, whose own `AGENTS.md` has its
own smoke test.

## Uninstall

```bash
rm -rf <SKILLS_DIR>/writing-from-dated-sources
```

Nothing else is written anywhere. No hooks, no settings changes, no network calls
at runtime.
