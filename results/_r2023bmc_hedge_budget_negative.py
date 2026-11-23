"""Negative control for scripts/astock_veto_hedge_budget.py (r2023, bm-c).

The face's `check` has three ways to be red and they must not wear each other's
words (r1934 / r1935): a moved input is STALE, a number that moved with the same
inputs is CHECK FAILED, and a missing face is missing.  This script proves the
predicate actually behaves that way by poisoning a copy of the face one field at a
time and asking the real `check()` what it says.

Run:  python results/_r2023bmc_hedge_budget_negative.py
"""
from __future__ import annotations

import copy
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import astock_veto_hedge_budget as F  # noqa: E402

_CHECKS = [0]


def ok(cond, msg):
    _CHECKS[0] += 1
    if not cond:
        raise AssertionError("negative leg %d failed: %s" % (_CHECKS[0], msg))


def run_check_with(face_obj, md_text=None, face_path=None, parent=None):
    """Point the module at a temporary face and call the real check()."""
    orig_out, orig_md = F.OUT, F.MD
    tmp_face = face_path or os.path.join(ROOT, "results", "_r2023bmc_nc_face.json")
    tmp_md = os.path.join(ROOT, "results", "_r2023bmc_nc_page.md")
    try:
        if face_obj is not None:
            with io.open(tmp_face, "w", encoding="utf-8") as fh:
                json.dump(face_obj, fh, ensure_ascii=False, indent=1)
        elif os.path.exists(tmp_face):
            os.remove(tmp_face)
        if md_text is not None:
            with io.open(tmp_md, "w", encoding="utf-8") as fh:
                fh.write(md_text)
        F.OUT, F.MD = tmp_face, tmp_md
        orig_load = F.load_parent
        if parent is not None:
            F.load_parent = lambda: parent
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = F.check()
        return rc, buf.getvalue()
    finally:
        F.OUT, F.MD = orig_out, orig_md
        F.load_parent = orig_load
        for p in (tmp_face, tmp_md):
            if os.path.exists(p):
                os.remove(p)


def main() -> int:
    with io.open(F.OUT, "r", encoding="utf-8") as fh:
        face = json.load(fh)
    page = io.open(F.MD, "r", encoding="utf-8").read()
    parent_live = F.load_parent()

    # 1. the face as published is green
    rc, out = run_check_with(face, page)
    ok(rc == 0, "published face + page -> rc0 (got rc=%d: %s)" % (rc, out.strip()[:200]))

    # 2. one period's book return moved -> the arithmetic no longer re-derives, and
    #    that is CHECK FAILED, not STALE (the inputs never moved)
    bad = copy.deepcopy(face)
    bad["rows"][10]["book_net"] = float(bad["rows"][10]["book_net"]) + 0.01
    rc, out = run_check_with(bad, page)
    ok(rc == 3, "moved row -> rc3")
    ok("CHECK FAILED" in out, "moved row wears CHECK FAILED: %s" % out.strip()[:160])
    ok("STALE" not in out, "moved row must not wear STALE")

    # 3. one hedge return moved -> same taxonomy
    bad = copy.deepcopy(face)
    bad["rows"][20]["hedge_etf"] = float(bad["rows"][20]["hedge_etf"]) + 0.01
    rc, out = run_check_with(bad, page)
    ok(rc == 3 and "CHECK FAILED" in out and "STALE" not in out,
       "moved hedge row -> CHECK FAILED only")

    # 4. a hand-edited chosen size -> CHECK FAILED (the rule must re-derive it)
    bad = copy.deepcopy(face)
    key = "%.2f|%.2f" % (F.BUDGET_PRIMARY, F.CARRY_PRIMARY)
    bad["cells"][key]["rule_a"]["k"] = 1.0
    rc, out = run_check_with(bad, page)
    ok(rc == 3 and "CHECK FAILED" in out, "hand-edited k -> CHECK FAILED")

    # 5. a hand-edited verdict -> CHECK FAILED, both on the cell and on the primary block
    bad = copy.deepcopy(face)
    bad["cells"][key]["verdict"] = "BUDGET_MISSES_OUT_OF_SAMPLE"
    rc, out = run_check_with(bad, page)
    ok(rc == 3 and "CHECK FAILED" in out, "hand-edited cell verdict -> CHECK FAILED")
    bad = copy.deepcopy(face)
    bad["primary"]["verdict"] = "BUDGET_MISSES_OUT_OF_SAMPLE"
    rc, out = run_check_with(bad, page)
    ok(rc == 3 and "CHECK FAILED" in out, "hand-edited primary verdict -> CHECK FAILED")

    # 6. a hand-edited price cell -> CHECK FAILED
    bad = copy.deepcopy(face)
    bad["cells"][key]["rule_a"]["out_of_sample_dd"] = -0.11
    rc, out = run_check_with(bad, page)
    ok(rc == 3 and "CHECK FAILED" in out, "hand-edited OOS drawdown -> CHECK FAILED")

    # 7. the published curve is a separate leg -- k=1.50 / 2.00 are not in any cell
    bad = copy.deepcopy(face)
    for row in bad["curve"]["full"]:
        if abs(row["k"] - 1.5) < 1e-9:
            row["max_drawdown"] = -0.10
    rc, out = run_check_with(bad, page)
    ok(rc == 3 and "CHECK FAILED" in out and "curve" in out,
       "hand-edited curve row -> CHECK FAILED naming the curve")

    # 8. the page must be the render of the face: one character is enough
    rc, out = run_check_with(face, page.replace("10.80", "10.81", 1))
    ok(rc == 3 and "page is not the render" in out, "edited page -> render leg fires")

    # 9. the face's own header fields disagreeing with a byte-identical parent are OUR
    #    defect, not staleness
    bad = copy.deepcopy(face)
    bad["evidence_cutoff"] = "2026-11-19"
    rc, out = run_check_with(bad, page)
    ok(rc == 3 and "CHECK FAILED" in out, "edited face cutoff -> CHECK FAILED")
    ok("STALE" not in out, "edited face cutoff must not wear STALE")
    bad = copy.deepcopy(face)
    bad["parent"]["beta_used"] = float(bad["parent"]["beta_used"]) * 1.01
    rc, out = run_check_with(bad, page)
    ok(rc == 3 and "CHECK FAILED" in out and "beta" in out,
       "edited face beta -> CHECK FAILED")

    # 10. a parent that really moved is STALE.  The real parent is a shared face and is
    #     not touched: the loader is swapped for the duration of the call.
    moved_parent = copy.deepcopy(parent_live)
    moved_parent["rows"][5] = dict(moved_parent["rows"][5],
                                   book_net=float(moved_parent["rows"][5]["book_net"]) + 0.01)
    rc, out = run_check_with(face, page, parent=moved_parent)
    ok(rc == 3 and "STALE" in out, "moved parent row -> STALE")
    ok("CHECK FAILED" not in out, "moved parent must not wear CHECK FAILED")
    moved_beta = copy.deepcopy(parent_live)
    moved_beta["beta"] = float(moved_beta["beta"]) * 1.01
    rc, out = run_check_with(face, page, parent=moved_beta)
    ok(rc == 3 and "STALE" in out, "moved parent beta -> STALE")
    truncated = copy.deepcopy(parent_live)
    truncated["rows"] = truncated["rows"][:-5]
    rc, out = run_check_with(face, page, parent=truncated)
    ok(rc == 3 and "STALE" in out, "short parent row set -> STALE, not a traceback")

    # 12. a missing face is missing, not stale
    rc, out = run_check_with(None, page)
    ok(rc == 3 and "face missing" in out, "missing face -> face missing")

    # 13. restoring the published face turns it green again (no residue)
    rc, out = run_check_with(face, page)
    ok(rc == 0, "restored face -> rc0 again")

    # 14. the selftest still passes on the restored module
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        st = F.selftest()
    ok(st == 0 and "PASS" in buf.getvalue(), "selftest still green after the control")

    print("negative control %d/%d PASS" % (_CHECKS[0], _CHECKS[0]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
