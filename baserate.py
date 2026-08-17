#!/usr/bin/env python3
"""Base rate for the writing-from-dated-sources rule over real files.

A file "would trigger" if it makes a present-tense claim about current state AND
its effective date is old enough that the claim may no longer hold. Effective
date prefers an explicit in-file date, then the last git commit touching it,
then mtime (mtime is the weakest: checkouts and tooling rewrite it).
"""
import re, subprocess, sys, os
from datetime import date, datetime
from pathlib import Path

TODAY = date(2026, 8, 16)
STALE_DAYS = 30

CLAIM = re.compile(r"""(?ix)
    \b currently \b
  | \b right \s+ now \b
  | \b at \s+ the \s+ moment \b
  | \b blocked \s+ on \b
  | \b in \s+ progress \b
  | \b (?:we|i) ['’]? re \s
  | \b (?:we|i) \s+ are \s
  | \b working \s+ on \b
  | \b as \s+ of \s+ now \b
  | \b still \s+ (?:needs|pending|blocked|open) \b
  | \b next \s+ (?:step|up) \b
  | \b is \s+ (?:live|running|deployed) \b
""")

DATE_IN_FILE = re.compile(r"""(?ix)
    (?:last \s* (?:updated|edited|modified) | updated | date) \s* [:\-] \s*
    (\d{4}-\d{2}-\d{2})
""")
ANY_ISO = re.compile(r"\b(20\d{2}-\d{2}-\d{2})\b")


def git_date(p: Path):
    try:
        r = subprocess.run(
            ["git", "-C", str(p.parent), "log", "-1", "--format=%cs", "--", p.name],
            capture_output=True, text=True, timeout=10)
        s = r.stdout.strip()
        return datetime.strptime(s, "%Y-%m-%d").date() if s else None
    except Exception:
        return None


def effective_date(p: Path, text: str):
    m = DATE_IN_FILE.search(text)
    if m:
        try:
            return datetime.strptime(m.group(1), "%Y-%m-%d").date(), "explicit"
        except ValueError:
            pass
    g = git_date(p)
    if g:
        return g, "git"
    # newest ISO date mentioned anywhere is a decent proxy for a log/journal
    iso = ANY_ISO.findall(text)
    if iso:
        try:
            return max(datetime.strptime(d, "%Y-%m-%d").date() for d in iso), "content"
        except ValueError:
            pass
    return date.fromtimestamp(p.stat().st_mtime), "mtime"


def bucket(days):
    if days <= 7:   return "0-7d"
    if days <= 30:  return "8-30d"
    if days <= 90:  return "31-90d"
    if days <= 365: return "91-365d"
    return "365d+"


def main(paths):
    rows = []
    for f in paths:
        p = Path(f)
        try:
            text = p.read_text(errors="ignore")
        except Exception:
            continue
        if not text.strip():
            continue
        claims = CLAIM.findall(text)
        eff, src = effective_date(p, text)
        gap = (TODAY - eff).days
        rows.append((p, len(claims), eff, src, gap))

    total = len(rows)
    with_claims = [r for r in rows if r[1] > 0]
    triggers = [r for r in with_claims if r[4] > STALE_DAYS]

    print(f"files scanned:            {total}")
    print(f"make a present-state claim: {len(with_claims)}  ({100*len(with_claims)//max(total,1)}%)")
    print(f"WOULD TRIGGER (claim + >{STALE_DAYS}d old): {len(triggers)}  ({100*len(triggers)//max(total,1)}%)")
    print()

    b = {}
    for r in triggers:
        b[bucket(r[4])] = b.get(bucket(r[4]), 0) + 1
    print("triggering files by age:")
    for k in ["31-90d", "91-365d", "365d+"]:
        if k in b:
            print(f"  {k:>9}: {b[k]}")
    print()

    s = {}
    for r in triggers:
        s[r[3]] = s.get(r[3], 0) + 1
    print("how the date was determined:", dict(s))
    print()

    print("worst offenders (most claims, oldest):")
    for p, n, eff, src, gap in sorted(triggers, key=lambda r: (-r[1], -r[4]))[:12]:
        short = str(p).replace("/Users/abhay/", "~/")
        print(f"  {n:>3} claims  {gap:>4}d old ({src:8})  {short}")


if __name__ == "__main__":
    main([l.strip() for l in sys.stdin if l.strip()])
