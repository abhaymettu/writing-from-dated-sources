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

No `OK` means git is missing or the network is blocked. Stop and say which.

## Step 1 — Set the skills directory

Pick by the runtime **you are currently running in**, not by what exists on disk:

| You are | Use |
|---|---|
| Claude Code | `~/.claude/skills` |
| Codex, Copilot CLI, Gemini CLI, anything else | `~/.agents/skills` |

If you cannot tell which runtime you are, ask the person. Do not guess.

```bash
SKILLS_DIR=~/.claude/skills     # or ~/.agents/skills — set this to your row above
mkdir -p "$SKILLS_DIR" && echo "installing into $SKILLS_DIR"
```

Use `"$SKILLS_DIR"` in every later command. It is a shell variable, not a
placeholder to paste literally.

**Tell them:** which directory you chose and why.

## Step 2 — Install

```bash
DEST="$SKILLS_DIR/writing-from-dated-sources"
if [ -d "$DEST/.git" ]; then
  git -C "$DEST" pull --ff-only
elif [ -e "$DEST" ]; then
  echo "EXISTS BUT NOT A GIT REPO — stop and ask"
else
  git clone --depth 1 https://github.com/abhaymettu/writing-from-dated-sources "$DEST"
fi
```

If it printed `EXISTS BUT NOT A GIT REPO`, stop and ask. Do not delete it.

**Verify:**

```bash
head -4 "$SKILLS_DIR/writing-from-dated-sources/SKILL.md"
```

Must show YAML frontmatter containing `name: writing-from-dated-sources`.

## Step 3 — Confirm discovery

Skills are read at session start, so this one is not active in the session you
are in right now. Do not claim otherwise.

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

### 4b — should stay silent

Same prompt, with the date set to **two days ago**.

**Pass:** a normal email, no commentary about the document's age.

**Fail:** it opens by announcing the doc is two days old. That is the specific
leak this skill was tuned to avoid; please report it as an issue on the repo.

Tell them both results. As with any language-model check, this is a sample and
not a deterministic test — if either is ambiguous, run it twice more.

## Step 5 — Tell them what they actually got

Say plainly:

- It fires rarely. Measured across 639 real files: 0.6% of one person's own docs
  and 5.8% of inherited repos are old enough to trigger it. That measurement
  covers files on disk only.
- It is a safety net for a quiet, consequential failure — a stale claim leaving
  in an artifact someone else acts on — not a daily assistant.
- They can measure their own corpus from inside the installed directory:

  ```bash
  find ~/some/project -name '*.md' | python3 "$SKILLS_DIR/writing-from-dated-sources/baserate.py"
  ```

- The supporting evidence is small-n and author-run. `TESTING.md` gives the
  counts and the limits; point them there rather than overstating it.

## Optional — the sibling skill

A companion covers a related failure: a date the person asserts conflicting with
the date already in your context, such as a "today is…" pasted from an old email.

Ask whether they want it. If yes, repeat Steps 1–4 using
`https://github.com/abhaymettu/temporal-grounding`; its own `AGENTS.md` carries
the matching smoke test.

## Uninstall

```bash
rm -rf "$SKILLS_DIR/writing-from-dated-sources"
```

Nothing else is written anywhere: no hooks, no settings changes, no network calls
at runtime.
