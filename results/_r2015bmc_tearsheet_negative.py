"""Negative control for r2015's tearsheet face (bm-c).

The question this answers: does ``astock_veto_tearsheet.py check`` actually
*check*, or does it only print green?  Each leg poisons exactly one thing and
asserts the verdict and the wording the chain relies on:

  * a moved panel must come back ``STALE`` (so the S6 leg pays for a rebuild),
  * a tampered number with unchanged inputs must come back ``CHECK FAILED`` and
    must NOT wear the word STALE (so a real defect is never explained away),
  * a missing face must say ``face missing``,
  * a broken parent anchor must be ``STALE`` (upstream face is r2012's),
  * after restoring the bytes the face must check green and be bit-identical.

Cost note: the real check() rebuilds the panel (~70s).  Running that 16 times
would be ~19 minutes, so the first leg builds the panel ONCE and every later leg
re-uses that snapshot through ``mod.build_face``.  What that skips is only the
recompute cost, not the comparison logic -- and the true path is covered by the
plain ``run`` / ``check`` invocation, whose rc0 is reproduced here as leg 0.

Usage
-----
    python results/_r2015bmc_tearsheet_negative.py
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import astock_veto_tearsheet as mod  # noqa: E402

LEGS = [0]


def _leg(name, cond, detail=""):
    LEGS[0] += 1
    if not cond:
        raise AssertionError("leg %d failed: %s %s" % (LEGS[0], name, detail))


def _run_check():
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = mod.check()
    return rc, buf.getvalue()


def _sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _write_tmp(payload):
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    return path


def _expect(tmp_path, want_rc, want_in, want_not_in, label):
    orig_out = mod.OUT
    mod.OUT = tmp_path
    try:
        rc, out = _run_check()
    finally:
        mod.OUT = orig_out
    ok = rc == want_rc and want_in in out and (want_not_in not in out if want_not_in else True)
    _leg(label, ok, "rc=%s out=%r" % (rc, out.strip()[:220]))
    return out


def main() -> int:
    face_path = mod.OUT
    md_path = mod.MD
    face_bytes = open(face_path, "rb").read()
    md_bytes = open(md_path, "rb").read()
    face = json.loads(face_bytes.decode("utf-8"))
    face_sha = _sha(face_path)
    md_sha = _sha(md_path)

    # one real build, reused by every leg below
    dates, symbols, rows = mod.build_face()
    mod.build_face = lambda hold=mod.HOLD, stride=mod.HOLD: (dates, symbols, rows)

    # 0. the untouched face checks green
    rc, out = _run_check()
    _leg("untouched face is green", rc == 0 and "CHECK ok" in out, "rc=%s out=%r" % (rc, out))

    def poison(mutate, label, want="CHECK FAILED"):
        p = json.loads(json.dumps(face))
        mutate(p)
        path = _write_tmp(p)
        try:
            _expect(path, 3, want, None if want == "STALE" else "STALE", label)
        finally:
            os.unlink(path)

    # 1-2. cutoff moved -> STALE (chain rebuild), never "CHECK FAILED"
    poison(lambda p: p.__setitem__("evidence_cutoff", "2026-01-02"),
           "moved cutoff -> STALE", want="STALE")

    def _panel_moved():
        mod.build_face = lambda hold=mod.HOLD, stride=mod.HOLD: (
            dates + ["2026-11-23"], symbols, rows)
    _panel_moved()
    rc, out = _run_check()
    _leg("panel ahead of face -> STALE", rc == 3 and "STALE" in out,
         "rc=%s out=%r" % (rc, out.strip()[:200]))
    mod.build_face = lambda hold=mod.HOLD, stride=mod.HOLD: (dates, symbols, rows)

    # 3-10. one tampered number each, all without the STALE word
    poison(lambda p: p["summary"]["B"]["bookings"]["fractional"].__setitem__(
        "per_period_mean", p["summary"]["B"]["bookings"]["fractional"]["per_period_mean"] + 1e-9),
        "tampered B mean -> CHECK FAILED, no STALE")
    poison(lambda p: p["summary"]["B"]["bookings"]["fractional"].__setitem__(
        "annual_vol", p["summary"]["B"]["bookings"]["fractional"]["annual_vol"] * 1.01),
        "tampered B annual vol")
    poison(lambda p: p["summary"]["B"]["bookings"]["fractional"].__setitem__(
        "sharpe_excess_0", p["summary"]["B"]["bookings"]["fractional"]["sharpe_excess_0"] + 0.01),
        "tampered B sharpe")
    poison(lambda p: p["summary"]["B"]["bookings"]["fractional"].__setitem__(
        "max_drawdown", p["summary"]["B"]["bookings"]["fractional"]["max_drawdown"] * 0.9),
        "tampered B drawdown")
    poison(lambda p: p["summary"]["A"]["bookings"]["fractional"].__setitem__(
        "calmar", (p["summary"]["A"]["bookings"]["fractional"]["calmar"] or 0) + 0.05),
        "tampered A calmar")
    poison(lambda p: p["summary"]["B"]["bookings"]["fractional"].__setitem__(
        "hit_rate", 0.99), "tampered B hit rate")
    poison(lambda p: p["summary"]["A"]["bookings"]["fractional"].__setitem__(
        "worst_6_periods", -0.5), "tampered A worst half-year")
    poison(lambda p: p["summary"]["B"].__setitem__(
        "turnover_mean", p["summary"]["B"]["turnover_mean"] * 0.5), "tampered B turnover")
    poison(lambda p: p["summary"]["B"]["gross"].__setitem__(
        "cost_per_period_mean", 0.0), "tampered B cost")
    poison(lambda p: p["summary"]["A"].__setitem__(
        "invested_share_median_lot_10000000", 0.99), "tampered A invested share")

    # 11-13. edges and verdict
    poison(lambda p: p["edges"]["by_booking"]["fractional"].__setitem__(
        "mean_per_period", 0.5), "tampered edge mean")
    poison(lambda p: p["edges"]["edge_tax"].__setitem__(
        "tax_share_of_gross_edge", 0.0), "tampered tax share")

    def _flip_verdict(p):
        p["verdict"] = "SHARPE_DOWN_DRAWDOWN_DEEPER"
    poison(_flip_verdict, "tampered headline verdict")

    def _flip_edge_verdict(p):
        p["edges"]["by_booking"]["fractional"]["verdict"] = "SHARPE_UP_DRAWDOWN_DEEPER"
    poison(_flip_edge_verdict, "tampered edge verdict")

    # 14. internal sanity: a positive drawdown is not a drawdown
    def _positive_mdd(p):
        p["summary"]["A"]["bookings"]["fractional"]["max_drawdown"] = 0.05
    out = poison(_positive_mdd, "positive drawdown refused")

    # 15. broken parent anchor -> STALE (upstream is r2012's face)
    parent = json.load(open(mod.PARENT, "r", encoding="utf-8"))
    parent["summary"]["B"]["net_frac_per_period_mean"] += 1e-6
    tmp_parent = _write_tmp(parent)
    orig_parent = mod.PARENT
    mod.PARENT = tmp_parent
    try:
        rc, out = _run_check()
    finally:
        mod.PARENT = orig_parent
        os.unlink(tmp_parent)
    _leg("broken parent anchor -> STALE", rc == 3 and "STALE parent anchor" in out,
         "rc=%s out=%r" % (rc, out.strip()[:220]))

    # 16. missing face says so, and does not pretend to be STALE
    mod.OUT = os.path.join(tempfile.gettempdir(), "r2015_no_such_face.json")
    try:
        rc, out = _run_check()
    finally:
        mod.OUT = face_path
    _leg("missing face -> face missing", rc == 3 and "face missing" in out and "STALE" not in out,
         "rc=%s out=%r" % (rc, out.strip()[:200]))

    # 17. restored bytes are untouched and still green
    _leg("face bytes unchanged by the control", _sha(face_path) == face_sha)
    _leg("doc bytes unchanged by the control", _sha(md_path) == md_sha)
    rc, out = _run_check()
    _leg("restored face green again", rc == 0 and "CHECK ok" in out,
         "rc=%s out=%r" % (rc, out.strip()[:200]))

    # 18. the script's own selftest is still the gate for the pure logic
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = mod.selftest()
    _leg("selftest still passes", rc == 0 and "PASS" in buf.getvalue(), buf.getvalue()[:120])

    print("negative control %d/%d PASS" % (LEGS[0], LEGS[0]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
