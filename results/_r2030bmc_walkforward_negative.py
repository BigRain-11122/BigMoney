"""Negative control for scripts/astock_veto_hedge_walkforward.py (new file, r2030).

Every mutation is applied to a COPY of the published face; the published files are never
written here.  The legs assert that each defect shape is reported as CHECK FAILED (a
number that disagrees with its own inputs) and each drift shape as STALE (an upstream
moved one step), i.e. the two reds stay apart (r1934).

Usage:
    python results/_r2030bmc_walkforward_negative.py
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import astock_veto_hedge_walkforward as F  # noqa: E402

LEGS = []


def leg(name, ok, detail=""):
    LEGS.append((name, bool(ok), detail))


def sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def capture(fn, *a, **kw):
    import io
    from contextlib import redirect_stdout
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = fn(*a, **kw)
    return rc, buf.getvalue()


def main() -> int:
    if not os.path.exists(F.OUT_JSON) or not os.path.exists(F.OUT_MD):
        print("published face missing -- run `run` first")
        return 2
    before_json = sha(F.OUT_JSON)
    before_md = sha(F.OUT_MD)

    tmp = tempfile.mkdtemp(prefix="r2030wf_")
    try:
        live = json.load(open(F.OUT_JSON, encoding="utf-8"))
        page = open(F.OUT_MD, encoding="utf-8").read()

        def fresh_copy():
            j = os.path.join(tmp, "face.json")
            m = os.path.join(tmp, "page.md")
            json.dump(live, open(j, "w", encoding="utf-8"), ensure_ascii=False)
            open(m, "w", encoding="utf-8").write(page)
            return j, m

        # L1 the untouched copy is green (the control that makes the rest meaningful)
        j, m = fresh_copy()
        rc, out = capture(F.check, j, m)
        leg("L1 untouched copy is green", rc == 0 and out.startswith("CHECK OK"), out[-80:])

        # L2 a poisoned arm volatility is a defect, not drift
        j, m = fresh_copy()
        d = json.load(open(j, encoding="utf-8"))
        d["arms"][0]["vol"] = d["arms"][0]["vol"] + 0.01
        json.dump(d, open(j, "w", encoding="utf-8"))
        rc, out = capture(F.check, j, m)
        leg("L2 poisoned arm vol -> CHECK FAILED", rc == 3 and "CHECK FAILED" in out, out[:80])
        leg("L2b and it does not claim STALE", "STALE" not in out)

        # L3 a poisoned reading
        j, m = fresh_copy()
        d = json.load(open(j, encoding="utf-8"))
        d["reads"]["vol_removed_honest"] = 0.99
        json.dump(d, open(j, "w", encoding="utf-8"))
        rc, out = capture(F.check, j, m)
        leg("L3 poisoned reading -> CHECK FAILED",
            rc == 3 and "CHECK FAILED" in out and "STALE" not in out, out[:80])

        # L4 a flipped headline verdict
        j, m = fresh_copy()
        d = json.load(open(j, encoding="utf-8"))
        d["verdict"] = "SOMETHING_ELSE"
        json.dump(d, open(j, "w", encoding="utf-8"))
        rc, out = capture(F.check, j, m)
        leg("L4 flipped verdict -> CHECK FAILED",
            rc == 3 and "CHECK FAILED" in out and "STALE" not in out, out[:80])

        # L5 a flipped scale verdict
        j, m = fresh_copy()
        d = json.load(open(j, encoding="utf-8"))
        d["verdict_scale"] = "HEDGE_BEATS_A_SMALLER_BOOK"
        json.dump(d, open(j, "w", encoding="utf-8"))
        rc, out = capture(F.check, j, m)
        leg("L5 flipped scale verdict -> CHECK FAILED",
            rc == 3 and "CHECK FAILED" in out and "STALE" not in out, out[:80])

        # L6 an upstream that moved one step is drift, and is repairable
        j, m = fresh_copy()
        d = json.load(open(j, encoding="utf-8"))
        d["parents"]["beta"]["content_sha256"] = "0" * 64
        json.dump(d, open(j, "w", encoding="utf-8"))
        rc, out = capture(F.check, j, m)
        leg("L6 moved parent -> STALE", rc == 3 and "STALE" in out, out[:80])
        leg("L6b a moved parent is not called a defect", "CHECK FAILED" not in out)

        # L7 a page that lost its verdict word
        j, m = fresh_copy()
        open(m, "w", encoding="utf-8").write(page.replace("`%s`" % live["verdict_scale"], ""))
        rc, out = capture(F.check, j, m)
        leg("L7 page missing a verdict word -> CHECK FAILED",
            rc == 3 and "CHECK FAILED" in out, out[:80])

        # L8 a missing page
        j, _ = fresh_copy()
        rc, out = capture(F.check, j, os.path.join(tmp, "nope.md"))
        leg("L8 missing page -> STALE", rc == 3 and "STALE" in out, out[:80])

        # L9 a missing face
        rc, out = capture(F.check, os.path.join(tmp, "nope.json"), m)
        leg("L9 missing face -> STALE", rc == 3 and "STALE" in out, out[:80])

        # L10 nothing above disturbed the published files
        leg("L10 published face untouched", sha(F.OUT_JSON) == before_json)
        leg("L10b published page untouched", sha(F.OUT_MD) == before_md)
        rc, out = capture(F.check)
        leg("L10c published face still green", rc == 0 and out.startswith("CHECK OK"), out[-80:])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    bad = [x for x in LEGS if not x[1]]
    for name, ok, detail in LEGS:
        if not ok:
            print("FAIL %s %r" % (name, detail))
    print("negative control %d/%d PASS" % (len(LEGS) - len(bad), len(LEGS)))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
