"""Negative control for r2019's smooth-rank face (bm-c).

The question this answers: does ``astock_veto_smooth_rank.py check`` actually
*check*, or does it only print green?  Each leg poisons exactly one thing and
asserts the verdict **and** the wording the S6 chain relies on:

  * a moved panel, a moved rebalance grid or a moved cutoff must come back
    ``STALE`` so the chain pays for a rebuild,
  * a tampered number on unchanged inputs must come back ``CHECK FAILED`` and
    must NOT wear the word STALE, so a real defect is never explained away,
  * a broken parent anchor (r2017's turnover-layer face) must be ``STALE`` --
    that is the upstream this face is anchored to,
  * a missing face must say ``face missing`` and must not pretend to be STALE,
  * after restoring the bytes the face must check green and be bit-identical.

The panel build (~2 min) is done once and reused through a patched
``mod.build_face``; what that skips is the recompute cost, not the comparison
logic.  The true path is covered by leg 0 and the restored-bytes legs.

Usage
-----
    python results/_r2019bmc_smooth_rank_negative.py
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

import astock_veto_smooth_rank as mod  # noqa: E402

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
    built = mod.build_face()
    real_build = mod.build_face

    def _build(slices=None):
        return built

    mod.build_face = _build

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

    # 2. a rebalance grid that has moved on -> STALE
    poison(lambda p: p.__setitem__("last_priced_rebalance", "2026-01-02"),
           "moved rebalance grid -> STALE", want="STALE")

    # 3. a panel that has grown past the face -> STALE
    dates, symbols, slices, arms, summ, pairs, decomp, verdicts, groups = built

    def _ahead(*_a, **_k):
        return (dates + ["2026-11-23"], symbols, slices, arms,
                summ, pairs, decomp, verdicts, groups)

    mod.build_face = _ahead
    rc, out = _run_check()
    _leg("panel ahead of face -> STALE", rc == 3 and "STALE" in out,
         "rc=%s out=%r" % (rc, out.strip()[:220]))
    mod.build_face = _build

    # 4-15. one tampered number each, all without the STALE word
    def _sum(arm, key, delta):
        def f(p):
            p["results"]["summary"][str(arm)][key] += delta
        return f

    for arm in mod.ARMS:
        poison(_sum(arm, "turnover_mean_ex_first", 1e-9), "tampered turnover K=%d" % arm)
        poison(_sum(arm, "gross_mean_ex_first", 1e-9), "tampered gross K=%d" % arm)
        poison(_sum(arm, "net_mean_ex_first", 1e-9), "tampered net K=%d" % arm)
    poison(_sum(1, "net_annualized", 1e-6), "tampered annualised K=1")
    poison(_sum(2, "size_mean", 1.0), "tampered book size K=2")
    poison(_sum(3, "partial_window_share_mean", 0.01), "tampered partial-window share K=3")

    # 16-18. the decomposition is the number the reader acts on: tamper each term
    def _dec(arm, key, delta):
        def f(p):
            p["results"]["decomposition_vs_K1"][str(arm)][key] += delta
        return f

    poison(_dec(2, "gross_effect", 1e-9), "tampered gross effect")
    poison(_dec(3, "cost_saved", 1e-9), "tampered cost saved")
    poison(_dec(4, "net_effect", 1e-9), "tampered net effect")

    def _flip_verdict(p):
        p["results"]["verdict"]["2"] = "SMOOTHING_PAYS"
    poison(_flip_verdict, "tampered verdict")

    def _drop_block(p):
        del p["results"]["summary"]
    poison(_drop_block, "missing summary block")

    def _drop_arm(p):
        del p["results"]["summary"]["3"]
    poison(_drop_arm, "missing one arm's summary")

    def _move_row(p):
        p["rows"]["2"][3]["turnover"] += 1e-9
    poison(_move_row, "tampered per-period turnover -> STALE", want="STALE")

    def _drop_row(p):
        p["rows"]["4"] = p["rows"]["4"][:-1]
    poison(_drop_row, "missing row -> STALE", want="STALE")

    # 19. broken parent anchor -> STALE (upstream is r2017's turnover-layer face)
    parent = json.load(open(mod.LAYER_PARENT, "r", encoding="utf-8"))
    parent["rows"][0]["turnover"] += 1e-6
    tmp_parent = _write_tmp(parent)
    orig_parent = mod.LAYER_PARENT
    mod.LAYER_PARENT = tmp_parent
    try:
        rc, out = _run_check()
    finally:
        mod.LAYER_PARENT = orig_parent
        os.unlink(tmp_parent)
    _leg("broken parent anchor -> STALE", rc == 3 and "STALE parent anchor" in out,
         "rc=%s out=%r" % (rc, out.strip()[:220]))

    # 20. a missing parent anchor is not "ok": the face must not claim an anchor
    #     it could not read (r1789 family: a face that cannot see upstream says so).
    mod.LAYER_PARENT = os.path.join(tempfile.gettempdir(), "r2019_no_such_layer.json")
    try:
        rc, out = _run_check()
    finally:
        mod.LAYER_PARENT = orig_parent
    _leg("unreadable parent anchor -> STALE", rc == 3 and "STALE parent anchor" in out,
         "rc=%s out=%r" % (rc, out.strip()[:220]))

    # 21. missing face says so, and does not pretend to be STALE
    mod.OUT = os.path.join(tempfile.gettempdir(), "r2019_no_such_face.json")
    try:
        rc, out = _run_check()
    finally:
        mod.OUT = face_path
    _leg("missing face -> face missing", rc == 3 and "face missing" in out and "STALE" not in out,
         "rc=%s out=%r" % (rc, out.strip()[:200]))

    # 22. restored bytes are untouched and still green
    _leg("face bytes unchanged by the control", _sha(face_path) == face_sha)
    _leg("doc bytes unchanged by the control", _sha(md_path) == md_sha)
    rc, out = _run_check()
    _leg("restored face green again", rc == 0 and "CHECK ok" in out,
         "rc=%s out=%r" % (rc, out.strip()[:200]))

    # 23. the face's own selftest is still the gate for the pure logic
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = mod.selftest()
    _leg("selftest still passes", rc == 0 and "PASS" in buf.getvalue(), buf.getvalue()[:120])

    print("negative control %d/%d PASS" % (LEGS[0], LEGS[0]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
