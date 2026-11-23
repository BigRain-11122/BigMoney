"""Negative control for r2017's turnover-layer face (bm-c).

The question this answers: does ``astock_veto_turnover_layers.py check`` actually
*check*, or does it only print green?  Each leg poisons exactly one thing and
asserts the verdict and the wording the S6 chain relies on:

  * a moved panel (or a moved cutoff) must come back ``STALE`` so the chain pays
    for a rebuild,
  * a tampered number on unchanged inputs must come back ``CHECK FAILED`` and
    must NOT wear the word STALE, so a real defect is never explained away,
  * a broken parent anchor must be ``STALE`` (upstream is r2012's face),
  * a missing face must say ``face missing``,
  * after restoring the bytes the face must check green and be bit-identical.

The panel build (~80s) is done once and reused through ``mod.build_face``; what
that skips is the recompute cost, not the comparison logic.  The true path is
covered by legs 0 and the restored-bytes leg.

Usage
-----
    python results/_r2017bmc_turnover_layers_negative.py
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import astock_veto_turnover_layers as mod  # noqa: E402

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
    _leg(label, ok, "rc=%s out=%r" % (rc, out.strip()[:240]))


def main() -> int:
    face_path = mod.OUT
    md_path = mod.MD
    face_bytes = open(face_path, "rb").read()
    md_bytes = open(md_path, "rb").read()
    face = json.loads(face_bytes.decode("utf-8"))
    face_sha = _sha(face_path)
    md_sha = _sha(md_path)

    # one real build, reused by every leg below
    dates, symbols, rows, pool, summ = mod.build_face()
    mod.build_face = lambda hold=mod.HOLD, stride=mod.HOLD: (dates, symbols, rows, pool, summ)

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

    # 1. a face built on another day's panel -> STALE (chain rebuild)
    poison(lambda p: p.__setitem__("evidence_cutoff", "2026-01-02"),
           "moved cutoff -> STALE", want="STALE")

    # 2. a panel that has grown past the face -> STALE
    mod.build_face = lambda hold=mod.HOLD, stride=mod.HOLD: (
        dates + ["2026-11-23"], symbols, rows, pool, summ)
    rc, out = _run_check()
    _leg("panel ahead of face -> STALE", rc == 3 and "STALE" in out,
         "rc=%s out=%r" % (rc, out.strip()[:220]))
    mod.build_face = lambda hold=mod.HOLD, stride=mod.HOLD: (dates, symbols, rows, pool, summ)

    # 3-10. one tampered number each, all without the STALE word
    def _book(key, delta):
        def f(p):
            p["results"]["book"][key] += delta
        return f

    poison(_book("u_share_mean", 1e-9), "tampered U share")
    poison(_book("v_share_mean", 1e-9), "tampered V share")
    poison(_book("turnover_mean_ex_first", 1e-9), "tampered attributable turnover")
    poison(_book("identity_residual_max", 1e-6), "tampered identity residual")
    poison(_book("tax_in_edge_per_period", 1e-9), "tampered edge tax")
    poison(_book("net_if_edge_never_flapped", 1e-9), "tampered zero point")
    poison(_book("entrant_admitted_rate", 1e-6), "tampered admitted rate")
    poison(_book("crossing_total", 1.0), "tampered crossing count")
    poison(_book("crossing_per_period", 1.0), "tampered crossings per period")
    poison(_book("denominator_ratio", 1e-9), "tampered denominator ratio")

    def _flip_verdict(p):
        p["results"]["verdict"] = "CHURN_IS_MOSTLY_UNIVERSE"
    poison(_flip_verdict, "tampered verdict")

    def _drop_block(p):
        del p["results"]["book"]
    poison(_drop_block, "missing book block")

    def _move_row(p):
        p["rows"][3]["turnover"] += 1e-9
    poison(_move_row, "tampered per-period turnover -> STALE", want="STALE")

    # 11. broken parent anchor -> STALE (upstream is r2012's face)
    parent = json.load(open(mod.PARENT, "r", encoding="utf-8"))
    parent["rows"][0]["B"]["turnover"] += 1e-6
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

    # 12. missing face says so, and does not pretend to be STALE
    mod.OUT = os.path.join(tempfile.gettempdir(), "r2017_no_such_face.json")
    try:
        rc, out = _run_check()
    finally:
        mod.OUT = face_path
    _leg("missing face -> face missing", rc == 3 and "face missing" in out and "STALE" not in out,
         "rc=%s out=%r" % (rc, out.strip()[:200]))

    # 13. restored bytes are untouched and still green
    _leg("face bytes unchanged by the control", _sha(face_path) == face_sha)
    _leg("doc bytes unchanged by the control", _sha(md_path) == md_sha)
    rc, out = _run_check()
    _leg("restored face green again", rc == 0 and "CHECK ok" in out,
         "rc=%s out=%r" % (rc, out.strip()[:200]))

    # 14. the face's own selftest is still the gate for the pure logic
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = mod.selftest()
    _leg("selftest still passes", rc == 0 and "PASS" in buf.getvalue(), buf.getvalue()[:120])

    print("negative control %d/%d PASS" % (LEGS[0], LEGS[0]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
