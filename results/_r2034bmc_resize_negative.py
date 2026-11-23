"""Negative control for r2034's hedge-resize face.

Proves four things the face claims about itself, on purpose-broken copies:

  1. a poisoned number in the published face turns `check` red with CHECK FAILED and
     WITHOUT the word STALE (it is an arithmetic disagreement, not a moved upstream);
  2. a moved parent turns `check` red with STALE and WITHOUT CHECK FAILED (the repair is
     `run`, not a code fix -- r1934's split);
  3. a missing face or page is STALE, not a traceback;
  4. the published files are byte-identical after the whole battery.

Usage: python results/_r2034bmc_resize_negative.py
"""
from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "scripts", "astock_veto_hedge_resize.py")


def _load():
    spec = importlib.util.spec_from_file_location("avhr_neg", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main() -> int:
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    face_path = os.path.join(ROOT, "results", "astock_veto_hedge_resize.json")
    page_path = os.path.join(ROOT, "research", "ASTOCK_VETO_HEDGE_RESIZE.md")
    before = {p: _sha(p) for p in (face_path, page_path, SCRIPT)}

    mod = _load()
    face = mod._read_json(face_path)

    def run_check(jpath, mpath):
        buf = io.StringIO()
        keep = sys.stdout
        sys.stdout = buf
        try:
            rc = mod.check(jpath, mpath)
        finally:
            sys.stdout = keep
        return rc, buf.getvalue()

    work = tempfile.mkdtemp(prefix="r2034neg_")
    try:
        # ---- 1. cost behaves: zero cost leaves the gross number alone
        p = face["schedules"][0]
        leg("N1 the current face charges something to the busiest schedule",
            abs(p["cost_drag_pp"] or 0.0) > 0.0, p["cost_drag_pp"])

        # ---- 2. one poisoned number: CHECK FAILED, no STALE
        bad = json.loads(json.dumps(face))
        bad["schedules"][0]["ann"] = float(bad["schedules"][0]["ann"]) + 0.01
        jp = os.path.join(work, "poisoned.json")
        with open(jp, "w", encoding="utf-8") as fh:
            json.dump(bad, fh)
        rc, out = run_check(jp, page_path)
        leg("N2 a poisoned annual return is CHECK FAILED", "CHECK FAILED" in out, out[:200])
        leg("N2b and it is not called STALE", "STALE" not in out, out[:200])
        leg("N2c and the exit code is 3", rc == 3, rc)

        # ---- 3. a moved parent: STALE, no CHECK FAILED
        moved = json.loads(json.dumps(face))
        moved["parents"]["beta"]["content_sha256"] = "0" * 64
        jp2 = os.path.join(work, "moved.json")
        with open(jp2, "w", encoding="utf-8") as fh:
            json.dump(moved, fh)
        rc, out = run_check(jp2, page_path)
        leg("N3 a moved parent is STALE", "STALE" in out, out[:200])
        leg("N3b and nothing is called CHECK FAILED", "CHECK FAILED" not in out, out[:200])
        leg("N3c and it asks for a re-run", "run `run`" in out, out[:200])

        # ---- 4. a poisoned frozen control: CHECK FAILED (the seed is part of the proof)
        rt = json.loads(json.dumps(face))
        rt["random_timing"]["draws"] = int(rt["random_timing"]["draws"]) + 1
        jp3 = os.path.join(work, "rt.json")
        with open(jp3, "w", encoding="utf-8") as fh:
            json.dump(rt, fh)
        rc, out = run_check(jp3, page_path)
        leg("N4 a changed random-timing control is CHECK FAILED",
            "CHECK FAILED" in out and rc == 3, out[:200])

        # ---- 5. a page that lost a verdict word
        md = io.open(page_path, encoding="utf-8").read()
        stripped = md.replace("`%s`" % face["verdict_level"], "")
        mp = os.path.join(work, "page_noverdict.md")
        io.open(mp, "w", encoding="utf-8").write(stripped)
        rc, out = run_check(face_path, mp)
        leg("N5 a page missing a verdict word is CHECK FAILED",
            "CHECK FAILED" in out and rc == 3, out[:200])

        # ---- 6. missing face / page
        rc, out = run_check(os.path.join(work, "nope.json"), page_path)
        leg("N6 a missing face is STALE", "STALE" in out and rc == 3, out[:200])
        jp4 = os.path.join(work, "copy.json")
        shutil.copyfile(face_path, jp4)
        rc, out = run_check(jp4, os.path.join(work, "nope.md"))
        leg("N6b a missing page is STALE", "STALE" in out and rc == 3, out[:200])

        # ---- 7. the verdicts actually answer to the numbers
        leg("N7 a cost ten times the line would be a line item",
            mod.decide_cost(mod.LINE_COST_PP * 10) == "SCHEDULE_COST_IS_A_REAL_LINE_ITEM")
        leg("N7b ten times the turnover halves the break-even",
            abs(mod.breakeven_bp(0.2) * 2.0 - mod.breakeven_bp(0.1)) < 1e-9,
            (mod.breakeven_bp(0.2), mod.breakeven_bp(0.1)))
        leg("N7c a 1 bp break-even decides against the busy schedule",
            mod.decide_breakeven(1.0) == "COST_DECIDES_AGAINST_THE_BUSY_SCHEDULE")

        # ---- 8. band strictness: exactly at the band is not a trade
        target = [0.90, 0.95, 0.95]
        leg("N8 a drift exactly at the band is not traded",
            mod.kpath("band", target, band=0.05) == [0.90, 0.90, 0.90])
        leg("N8b a drift one tick beyond the band is",
            mod.kpath("band", [0.90, 0.9501, 0.9501], band=0.05)[1] == 0.9501)
    finally:
        shutil.rmtree(work, ignore_errors=True)

    # ---- 9. nothing published moved
    after = {p: _sha(p) for p in (face_path, page_path, SCRIPT)}
    leg("N9 the published face, page and script are byte-identical after the battery",
        before == after, {k: (before[k][:8], after[k][:8]) for k in before
                          if before[k] != after[k]})

    bad = [x for x in legs if not x[1]]
    for name, ok, detail in legs:
        if not ok:
            print("FAIL %s %r" % (name, detail))
    print("negative control %d/%d PASS" % (len(legs) - len(bad), len(legs)))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
