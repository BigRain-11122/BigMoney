# -*- coding: utf-8 -*-
"""smoke_red_triage.py -- triage the red legs of the last smoke run.

Why: `python -m smoke_test` reports N failing legs and the fix order depends on
*why* each one is red. The chain law (r1850/r1934) already encodes the two
kinds that matter:

  STALE_OR_MISSING  the leg's own words say stale / face missing / cutoff behind
                    -> the chain's run_leg will pay the writer and heal it on the
                       next refresh leg; do NOT hand-fix the face.
  CONTRADICTION     MISMATCH / DRIFT / BREACH / does not reproduce / disagree
                    -> two numbers that should agree do not; this is a code or
                       mapping defect and the chain will keep re-deriving the same
                       disagreement (r1934: a check that only re-computes itself
                       never says "I am out of date").
  EXCEPTION         KeyError / TypeError / Traceback -> defect with a stack.
  UNCLASSIFIED      none of the above words; read the leg by hand.

Read-only: consumes logs/smoke_legs.json (or --legs) and writes one face.

    python scripts/smoke_red_triage.py                     # write + table
    python scripts/smoke_red_triage.py --json-out results/smoke_red_triage.json
    python scripts/smoke_red_triage.py --selftest
"""
from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_LEGS = os.path.join(ROOT, "logs", "smoke_legs.json")
DEFAULT_OUT = os.path.join(ROOT, "results", "smoke_red_triage.json")

STALE_WORDS = ("stale", "face missing", "cutoff behind", "behind the gate",
               "upstream moved", "awaiting_upstream", "no_writer",
               "no_arms_priced", "n_arms=0", "awaiting_", "not priced")
CONTRA_WORDS = ("mismatch", "drift", "breach", "does not reproduce",
                "do not agree", "disagree", "identity_broken", "failed to reproduce",
                "re-derives to", "face says", "differently", "check_fail",
                "problems", "no longer", "does not match")
EXC_WORDS = ("keyerror", "typeerror", "nameerror", "valueerror", "traceback",
             "attributeerror", "indexerror")

ORDER = ("EXCEPTION", "SUBCHAIN_FAILED", "CONTRADICTION", "STALE_OR_MISSING", "UNCLASSIFIED")

# legs that drive another suite print a summary instead of a diagnosis; the
# real reason lives one level down and has to be read there
SUBCHAIN_RE = "pass --"


def classify(detail: str) -> str:
    """Map a smoke leg's detail text onto the fix-order class."""
    raw = detail or ""
    d = raw.lower()
    # an exception stack is always the most specific fact about the failure
    if any(w in d for w in EXC_WORDS):
        return "EXCEPTION"
    # a wrapper leg only tells you a child suite failed; do not pretend to know why
    if SUBCHAIN_RE in d and "fail" in d:
        return "SUBCHAIN_FAILED"
    # stale wording is the chain's own contract word -- check it BEFORE the
    # contradiction words, because a stale face usually also prints two
    # numbers that disagree (r1850: the drift text must self-name STALE)
    if any(w in d for w in STALE_WORDS):
        return "STALE_OR_MISSING"
    if any(w in d for w in CONTRA_WORDS):
        return "CONTRADICTION"
    return "UNCLASSIFIED"


def face_of(leg_name: str) -> str:
    """Best-effort subject of a leg: the last parenthesised hint, else the name."""
    name = (leg_name or "").strip()
    if "(" in name and name.endswith(")"):
        hint = name[name.rindex("(") + 1:-1].strip()
        if hint:
            return hint
    return name


def is_empty_detail(detail: str) -> bool:
    """exit=1 | } and friends carry no diagnosis -- say so instead of guessing."""
    d = (detail or "").strip()
    for pre in ("exit=0 |", "exit=1 |", "exit=2 |", "exit=3 |", "exit=4 |"):
        if d.startswith(pre):
            d = d[len(pre):].strip()
    return len(d.strip(" |}")) <= 2


def triage(legs: dict) -> dict:
    failed = legs.get("failed") or []
    rows = []
    for item in failed:
        if isinstance(item, dict):
            name = item.get("name", "")
            detail = item.get("detail", "")
        else:
            name, detail = str(item), ""
        rows.append({
            "leg": name,
            "subject": face_of(name),
            "class": classify(detail),
            "empty_detail": is_empty_detail(detail),
            "detail": (detail or "").strip()[:400],
        })
    counts = {k: 0 for k in ORDER}
    for r in rows:
        counts[r["class"]] = counts.get(r["class"], 0) + 1
    fix_order = []
    for cls in ORDER:
        for r in rows:
            if r["class"] == cls:
                fix_order.append({"class": cls, "leg": r["leg"], "detail": r["detail"]})
    return {
        "source_ts": legs.get("ts", ""),
        "legs": legs.get("legs"),
        "pass": legs.get("pass"),
        "fail": legs.get("fail"),
        "unverified": legs.get("unverified"),
        "counts": counts,
        "rows": rows,
        "fix_order": fix_order,
    }


def selftest() -> int:
    checks = []

    def ck(label, got, want):
        checks.append((label, got == want, got, want))

    ck("stale word wins over the numbers that disagree",
       classify("STALE FACE_BEHIND_GATE: cutoff 2026-11-20 vs gate 2026-11-24, "
                "values mismatch"), "STALE_OR_MISSING")
    ck("face missing is stale-family",
       classify("exit=1 | face missing results/etf_book_x.json"), "STALE_OR_MISSING")
    ck("plain mismatch is a contradiction",
       classify("exit=1 | MISMATCH verdict: receipt='A' rederive='B'"), "CONTRADICTION")
    ck("keyerror is an exception even with mismatch words",
       classify("exit=1 | KeyError: 'gap_k' while re-deriving mismatch"), "EXCEPTION")
    ck("silence is unclassified",
       classify("exit=1 | "), "UNCLASSIFIED")
    ck("a wrapper suite summary is its own class",
       classify("exit=1 | Summary: 476/477 PASS -- 1 FAIL"), "SUBCHAIN_FAILED")
    ck("re-derive disagreement is a contradiction",
       classify("exit=1 | impact_pct_at_signed re-derives to 0.958, face says 0.9"),
       "CONTRADICTION")
    ck("no arms priced is upstream-missing, not a lie",
       classify("exit=3 | [check] PROBLEMS | verdict=NO_ARMS_PRICED | n_arms=0"),
       "STALE_OR_MISSING")
    ck("bare exit code is flagged empty rather than guessed",
       (classify("exit=1 | }"), is_empty_detail("exit=1 | }")), ("UNCLASSIFIED", True))
    ck("a real sentence is not empty", is_empty_detail("exit=1 | KeyError: 'x'"), False)
    ck("subject comes from the parenthesised hint",
       face_of("product: x (lifetime re-derived)"), "lifetime re-derived")
    sample = {"ts": "t", "legs": 3, "pass": 1, "fail": 2,
              "failed": [{"name": "product: a (x)", "detail": "MISMATCH a vs b"},
                         {"name": "product: b", "detail": "STALE cutoff behind gate"}]}
    out = triage(sample)
    ck("counts per class", (out["counts"]["CONTRADICTION"], out["counts"]["STALE_OR_MISSING"]), (1, 1))
    ck("fix order puts contradictions before stale", [r["class"] for r in out["fix_order"]],
       ["CONTRADICTION", "STALE_OR_MISSING"])
    bad = [c for c in checks if not c[1]]
    for label, ok, got, want in checks:
        print(("PASS " if ok else "FAIL ") + label + ("" if ok else f"  got={got!r} want={want!r}"))
    print(f"selftest {len(checks) - len(bad)}/{len(checks)}")
    return 0 if not bad else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--legs", default=DEFAULT_LEGS)
    ap.add_argument("--json-out", default=DEFAULT_OUT)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not os.path.exists(args.legs):
        print(f"no legs face at {args.legs}")
        return 2
    with open(args.legs, "r", encoding="utf-8") as fh:
        legs = json.load(fh)
    out = triage(legs)
    out["legs_face"] = os.path.relpath(args.legs, ROOT).replace("\\", "/")
    os.makedirs(os.path.dirname(args.json_out), exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(f"smoke red triage: {out['fail']} red of {out['legs']} legs "
          f"(face ts {out['source_ts']})")
    for cls in ORDER:
        n = out["counts"].get(cls, 0)
        if n:
            print(f"  {cls}: {n}")
    for r in out["fix_order"]:
        print(f"  [{r['class']}] {r['leg']}")
    print("evidence -> " + os.path.relpath(args.json_out, ROOT).replace("\\", "/"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
