# Setup instructions for the agent

You were given a link to this repository. The person you are working with wants
this skill installed. Work through the steps in order and run every verification.
Tell them what happened at each step in plain language.

If a step fails, stop and report exactly what failed. Do not improvise an
alternative install location.

## Step 0 — Prerequisites

```bash
git --version && git ls-remote --exit-code https://github.com/abhaymettu/writing-from-dated-sources >/dev/null && echo OK
```

```bash
python3 --version
```

No `OK` from the first means git is missing or the network is blocked — stop and
say which. `python3` is only needed for the optional corpus measurement in
Step 5; note its absence but continue without it.

## Step 1 — Set the skills directory

Pick by the runtime **you are currently running in**, not by what exists on disk:

| You are | Use | Discovery |
|---|---|---|
| Claude Code | `~/.claude/skills` | verified |
| Codex, Copilot CLI, Gemini CLI, anything else | `~/.agents/skills` | **untested — see Step 3** |

If you cannot tell which runtime you are, ask the person. Do not guess.

`~/.agents/skills` is a cross-runtime convention. Nothing in this repo has been
tested on those runtimes. If that is your row, say so to the person before you
install, not after.

```bash
SKILLS_DIR=~/.claude/skills   # or ~/.agents/skills — pick from the table above
mkdir -p "$SKILLS_DIR" && echo "installing into $SKILLS_DIR"
```

**Every command block below re-declares `SKILLS_DIR` on its own first line.** That
is deliberate: shell state does not survive between tool calls, and an unset
`SKILLS_DIR` would turn the install and uninstall commands into operations on `/`.
Edit the value in each block to match what you chose here. Do not delete the
line, and do not assume it carries over.

**Tell them:** which directory you chose and why.

## Step 2 — Install

```bash
SKILLS_DIR=~/.claude/skills   # same value as Step 1
set -u
: "${SKILLS_DIR:?set SKILLS_DIR on the line above}"
DEST="$SKILLS_DIR/writing-from-dated-sources"
if [ -d "$DEST/.git" ]; then
  if [ -n "$(git -C "$DEST" status --porcelain)" ]; then
    echo "LOCAL EDITS PRESENT — stop and ask before updating"
  else
    git -C "$DEST" fetch --depth 1 origin main && git -C "$DEST" reset --hard origin/main
  fi
elif [ -e "$DEST" ]; then
  echo "EXISTS BUT NOT A GIT REPO — stop and ask"
else
  git clone --depth 1 https://github.com/abhaymettu/writing-from-dated-sources "$DEST"
fi
```

(`fetch` + `reset` rather than `pull`, because `--depth 1` clones are shallow and
`pull --ff-only` is unreliable against them.)

If it printed `LOCAL EDITS PRESENT`, someone has customised this copy — the
update would overwrite their changes. Stop and ask; do not force it.

If it printed `EXISTS BUT NOT A GIT REPO`, stop and ask. Do not delete it.

**Verify:**

```bash
SKILLS_DIR=~/.claude/skills   # same value as Step 1
head -4 "$SKILLS_DIR/writing-from-dated-sources/SKILL.md"
```

Must show YAML frontmatter containing `name: writing-from-dated-sources`.

## Step 3 — Confirm discovery

In Claude Code, skills are read at session start, so this one is not active in
the session you are in right now — do not claim otherwise.

**Only Claude Code is verified.** `~/.agents/skills` is a convention other
runtimes may read, but nothing here has been tested on Codex, Copilot CLI, or
Gemini CLI, and how they load skills is their business, not this repo's. If you
are on one of those, tell the person plainly that discovery is unverified and
point them at their runtime's own docs before running any check.

**Tell them:** "Installed. Start a new session, then paste the two checks in
Step 4."

## Step 4 — Smoke test, run by the person in a NEW session

Do not run these yourself as shell commands. Invoking your own CLI from inside a
session spends tokens, may hit a sandbox or permission prompt, and inherits
whatever `CLAUDE.md` is in the working directory. Hand them the text.

The second check matters more than the first, because it tests that the skill
stays *quiet* when it should.

### 4a — should flag

**Give them this to paste**, replacing the date with one roughly a year ago:

> Here is my STATUS.md, write a short update email to the client.
>
> \# Status — Payments Migration
> Last updated: \<A DATE ABOUT A YEAR AGO\>
> Current phase: integration testing
> Blocked on: Stripe sandbox credentials from the client finance team

**Pass:** the drafted email itself carries the source date — a subject line or
opening line naming that month, and claims attributed ("as of that update, the
blocker was…") rather than asserted in the present tense.

**Fail:** the email says "we're currently blocked on…" with nothing about where
it came from. A caveat addressed to the *user* but missing from the email body is
also a fail — the email is the thing that gets sent.

**Partial** (the most likely real outcome): the subject or opening names the
date, but the body still asserts "we're blocked on…" in the present tense. Count
that as a fail of the attribution half and say so specifically — it is the more
useful bug report.

### 4b — should stay silent

Same prompt, with the date set to **two days ago**.

**Pass:** a normal email, no commentary about the document's age.

**Fail:** it opens by announcing the doc is two days old. That is the specific
leak this skill was tuned to avoid; please report it as an issue on the repo.

These run in a session you cannot see. Ask them to paste both replies back to
you, then judge against the criteria above and tell them the verdict. Do not
report a result you have not been shown.

As with any language-model check this is a sample, not a deterministic test — if
either is ambiguous, have them run it twice more.

## Step 5 — Tell them what they actually got

Say plainly:

- It fires rarely. Measured across 613 real files: **1 file** of 150 in one
  person's own docs, and **14 of 463** in inherited repos, were old enough to
  trigger it. Quote the counts, not just the percentages — the first is a single
  document. The measurement covers files on disk only.
- It is a safety net for a quiet, consequential failure — a stale claim leaving
  in an artifact someone else acts on — not a daily assistant.
- They can measure their own corpus from inside the installed directory:

  ```bash
  find ~/some/project -name '*.md' \
    | python3 ~/.claude/skills/writing-from-dated-sources/baserate.py
  ```

  (Written out in full, since they will run this in their own shell where
  `SKILLS_DIR` was never set. Adjust the path if you installed elsewhere.)

- The supporting evidence is small-n and author-run. `TESTING.md` gives the
  counts and the limits; point them there rather than overstating it.

## Optional — the sibling skill

A companion covers a related failure: a date the person asserts conflicting with
the date already in your context, such as a "today is…" pasted from an old email.

Ask whether they want it. If yes, follow that repo's own AGENTS.md — do not reuse the commands here, they hardcode this repo's URL and directory name:
`https://github.com/abhaymettu/temporal-grounding`.

## Uninstall

```bash
SKILLS_DIR=~/.claude/skills   # same value as Step 1
rm -rf "${SKILLS_DIR:?set SKILLS_DIR first}/writing-from-dated-sources"
```

Nothing else is written anywhere: no hooks, no settings changes, no network calls
at runtime.
