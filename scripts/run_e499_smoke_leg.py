"""Run the E499 smoke leg's assertions standalone, without launching the full suite.

The suite is ~30 minutes and a round that only needs one new leg should not pay for it.  This
runner re-states the same three properties the suite leg holds, and adds the doctored arms, so the
leg's discriminating power is exercised in the window that wrote it:

  1. the stored face re-derives from its own rows (e499.tally_problems == [])
  2. every site's price is inside the vocabulary and the ladder is monotone in the counting set
  3. a doctored price, and a moved list that does not re-derive, are both caught

Usage: python scripts/run_e499_smoke_leg.py [--verbose]
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (ROOT, os.path.join(ROOT, "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import e499_helperprice as e499  # noqa: E402

FACE = os.path.join(ROOT, "results", "state_tilt", "helperprice_latest.json")


def run_leg(quiet=False):
    face = json.load(io.open(FACE, encoding="utf-8"))
    rows = []
    summary = face.get("summary") or {}

    rows.append(("the stored face re-derives from its own rows",
                 e499.tally_problems(face) == [],
                 "; ".join(e499.tally_problems(face))[:160]))

    outside = sorted({s.get("price") for r in (face.get("rows") or [])
                      for s in (r.get("sites") or [])
                      if s.get("price") not in e499.PRICE_VOCAB})
    rows.append(("every price is inside the vocabulary", not outside, repr(outside[:3])))

    ladder = summary.get("retirement_ladder") or []
    monotone = len(ladder) >= 3 and all(
        (b.get("twins_kept") or 0) >= (a.get("twins_kept") or 0)
        for a, b in zip(ladder, ladder[1:]))
    rows.append(("the retirement ladder is monotone in the counting set", monotone,
                 " | ".join("%s:%s" % (t.get("label", "")[:28], t.get("twins_kept"))
                            for t in ladder)))

    moved = summary.get("twins_moving") or []
    clean = all(not any(s.get("price") in e499.COUNTS_AS_A_READER
                        for s in ([r for r in (face.get("rows") or [])
                                   if r.get("twin") == t] or [{}])[0].get("sites") or [])
                for t in moved)
    rows.append(("no moved twin carries a counting site", clean, repr(moved)))

    bad = json.loads(json.dumps(face))
    if bad.get("rows") and bad["rows"][0].get("sites"):
        bad["rows"][0]["sites"][0]["price"] = "reads_it_somehow"
    rows.append(("a doctored price is caught", bool(e499.tally_problems(bad)), ""))

    bad2 = json.loads(json.dumps(face))
    bad2["summary"]["twins_moving"] = []
    bad2["summary"]["twins_that_move_to_retirable"] = 0
    rows.append(("a moved list that does not re-derive is caught",
                 bool(e499.tally_problems(bad2)), ""))

    if not quiet:
        done = len([r for r in rows if r[1]])
        print("%d/%d legs passed" % (done, len(rows)))
        for name, ok, detail in rows:
            if not ok:
                print("  FAIL ::", name, "|", detail)
    return rows


def main(argv):
    rows = run_leg(quiet="--quiet" in argv)
    bad = [r for r in rows if not r[1]]
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))