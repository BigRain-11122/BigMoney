"""Negative control for scripts/astock_veto_hedge_default.py.

A self-test that has never been shown to go red on a wrong face is a printer, not a
guard.  This control takes the *published* face, breaks it one thing at a time, and
requires the real ``check()`` to name the break -- and to keep the two kinds of red
apart: a moved parent is STALE (re-run), a face that disagrees with arithmetic it
published on the same inputs is CHECK FAILED.

Nothing on disk is touched: every tampering happens on a copy in a temp directory.
Exit 0 = every leg behaved, 1 = a leg did not.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import astock_veto_hedge_default as H  # noqa: E402


def _quiet(fn, *a, **kw):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = fn(*a, **kw)
    return rc, buf.getvalue()


def main() -> int:
    ok = 0
    bad = []

    def leg(name, cond, detail=""):
        nonlocal ok
        if cond:
            ok += 1
        else:
            bad.append("%s :: %s" % (name, detail))

    face = H._read_json(H.OUT_JSON)
    md = open(H.OUT_MD, encoding="utf-8").read()

    tmpd = tempfile.mkdtemp(prefix="_r2026bmc_neg_")
    jp = os.path.join(tmpd, "face.json")
    mp = os.path.join(tmpd, "face.md")

    def put(obj, text=None):
        with open(jp, "w", encoding="utf-8") as fh:
            json.dump(obj, fh, ensure_ascii=False, indent=1)
        with open(mp, "w", encoding="utf-8") as fh:
            fh.write(H.render_md(obj) if text is None else text)

    try:
        put(face)
        rc, out = _quiet(H.check, jp, mp)
        leg("the published face is green", rc == 0 and "CHECK OK" in out, out[:100])

        # 1. a reading that this face published, contradicted
        f = json.loads(json.dumps(face))
        f["budgets"][H.BUDGET_PRIMARY]["default_oos_dd"] = 0.5
        put(f)
        rc, out = _quiet(H.check, jp, mp)
        leg("a changed drawdown is CHECK FAILED and not STALE",
            rc == 3 and "CHECK FAILED" in out and "STALE" not in out, out[:120])

        # 2. a rule verdict flipped by hand
        f = json.loads(json.dumps(face))
        name = sorted(n for n in f["rules"] if n != H.DEFAULT_RULE)[0]
        f["rules"][name]["verdict"] = "ROBUST" if f["rules"][name]["verdict"] != "ROBUST" \
            else "RETIRED"
        put(f)
        rc, out = _quiet(H.check, jp, mp)
        leg("a flipped rule verdict is CHECK FAILED",
            rc == 3 and "CHECK FAILED" in out, out[:120])

        # 3. the swap decision flipped
        f = json.loads(json.dumps(face))
        f["swap"]["earned"] = not f["swap"]["earned"]
        put(f)
        rc, out = _quiet(H.check, jp, mp)
        leg("a flipped swap decision is CHECK FAILED",
            rc == 3 and "CHECK FAILED" in out, out[:120])

        # 4. today's instruction moved by a rounding hair
        f = json.loads(json.dumps(face))
        f["today"]["hedge_notional_pct"] = f["today"]["hedge_notional_pct"] + 0.01
        put(f)
        rc, out = _quiet(H.check, jp, mp)
        leg("a hair of drift in today's notional is CHECK FAILED",
            rc == 3 and "CHECK FAILED" in out, out[:120])

        # 5. the headline verdict changed
        f = json.loads(json.dumps(face))
        f["verdict"] = "FITTING_EARNS_A_SWAP"
        put(f)
        rc, out = _quiet(H.check, jp, mp)
        leg("a changed headline verdict is CHECK FAILED",
            rc == 3 and "CHECK FAILED" in out, out[:120])

        # 6. a hand edit on the page only
        put(face, text=md.replace("The default hedge size", "The best hedge size", 1))
        rc, out = _quiet(H.check, jp, mp)
        leg("a hand-edited page is CHECK FAILED",
            rc == 3 and "page" in out, out[:120])

        # 7. the parent moved under us -- the only case that is STALE
        f = json.loads(json.dumps(face))
        f["parent"]["content_sha256"] = "f" * 64
        put(f)
        rc, out = _quiet(H.check, jp, mp)
        leg("a moved parent is STALE and says STALE",
            rc == 3 and "STALE" in out and "CHECK FAILED" not in out, out[:120])

        # 8. a missing rule is named, not a KeyError
        f = json.loads(json.dumps(face))
        gone = sorted(f["rules"])[0]
        f["rules"].pop(gone)
        put(f, text=H.render_md(face))
        rc, out = _quiet(H.check, jp, mp)
        leg("a missing rule is CHECK FAILED, never a crash",
            rc == 3 and "missing" in out, out[:140])

        # 9. an unreadable face is named, not a traceback
        rc, out = _quiet(H.check, os.path.join(tmpd, "nope.json"), mp)
        leg("an unreadable face is CHECK FAILED, never a crash",
            rc == 3 and "CHECK FAILED" in out, out[:140])
    finally:
        shutil.rmtree(tmpd, ignore_errors=True)

    # 10. the shipped face still says what the control assumed
    rc, out = _quiet(H.check)
    leg("the shipped face is still green after the control ran",
        rc == 0 and "CHECK OK" in out, out[:100])

    print("NEGATIVE-CONTROL %d/%d PASS" % (ok, ok + len(bad)))
    for b in bad:
        print("  FAIL %s" % b)
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
