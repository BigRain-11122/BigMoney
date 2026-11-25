#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""negative control for scripts/idx_fut_carry_ladder_risk.py.

Every leg corrupts exactly one thing in a temporary copy of the published face (or of
its inputs) and asserts the *real* `check` answers the right way.  The word is the
contract (r1850/r1934): drift in an input says STALE, a face that contradicts its own
numbers says CHECK FAILED and must not say STALE.

Run:  python results/_r2105bmc_ladder_risk_negative.py
"""
import io
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for p in (ROOT, os.path.join(ROOT, "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

import idx_fut_carry_ladder_risk as L  # noqa: E402

PASS = []
FAIL = []


def ok(cond, name, extra=""):
    (PASS if cond else FAIL).append(name)
    print("  %s %s%s" % ("ok  " if cond else "FAIL", name, (" | " + extra) if extra and not cond else ""))


def run_check(face_path, lattice_path, l1_path):
    L.OUT = face_path
    L.LATTICE = lattice_path
    L.L1_ARM = l1_path
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        rc = L.cmd_check(None)
    finally:
        sys.stdout = old
    return rc, buf.getvalue()


def main():
    real_face = os.path.join(ROOT, "results", "idx_fut_carry_ladder_risk.json")
    real_lattice = os.path.join(ROOT, "results", "policy_return_lattice.json")
    real_l1 = os.path.join(ROOT, "results", "etf_nobond_vt.json")
    if not (os.path.exists(real_face) and os.path.exists(real_lattice)):
        print("SKIP negative control: face or ladder missing")
        return 2
    face = json.load(io.open(real_face, encoding="utf-8"))
    tmp = tempfile.mkdtemp(prefix="ladder_risk_neg_")
    try:
        # N0 the published face on its own inputs must be green
        rc, out = run_check(real_face, real_lattice, real_l1)
        ok(rc == 0 and "CHECK_OK" in out, "N0 published face re-derives green", out.strip())

        # N1 a hand-edited measured vol: numbers no longer consistent -> CHECK FAILED, no STALE
        p = os.path.join(tmp, "n1.json")
        f = json.loads(json.dumps(face))
        f["measured"]["rungs"][f["engine_rung"]]["measured_vol_pct"] += 1.0
        io.open(p, "w", encoding="utf-8").write(json.dumps(f, ensure_ascii=False))
        rc, out = run_check(p, real_lattice, real_l1)
        ok(rc == 4 and "CHECK FAILED" in out and "STALE" not in out,
           "N1 tampered measured vol -> CHECK FAILED, no STALE word", out.strip())

        # N2 a rung's L2 vol no longer matches the two-asset formula -> CHECK FAILED
        p = os.path.join(tmp, "n2.json")
        f = json.loads(json.dumps(face))
        f["measured"]["rungs"]["2/2"]["l2_vol_measured_pct"] += 0.5
        io.open(p, "w", encoding="utf-8").write(json.dumps(f, ensure_ascii=False))
        rc, out = run_check(p, real_lattice, real_l1)
        ok(rc == 4 and "CHECK FAILED" in out,
           "N2 tampered L2 vol -> CHECK FAILED", out.strip())

        # N3 a flipped verdict that its own measurements contradict -> CHECK FAILED
        p = os.path.join(tmp, "n3.json")
        f = json.loads(json.dumps(face))
        f["judgment"]["declared_vs_measured_vol"] = "DECLARED_RISK_MATCHES_MEASURED"
        io.open(p, "w", encoding="utf-8").write(json.dumps(f, ensure_ascii=False))
        rc, out = run_check(p, real_lattice, real_l1)
        ok(rc == 4 and "CHECK FAILED" in out,
           "N3 flipped verdict -> CHECK FAILED", out.strip())

        # N4 the ladder face changed under the measurement -> STALE
        p = os.path.join(tmp, "n4.json")
        f = json.loads(json.dumps(face))
        f["inputs"]["lattice"]["sha256"] = "0" * 64
        io.open(p, "w", encoding="utf-8").write(json.dumps(f, ensure_ascii=False))
        rc, out = run_check(p, real_lattice, real_l1)
        ok(rc == 3 and "STALE" in out, "N4 ladder digest drift -> STALE", out.strip())

        # N5 the equity arm changed under the measurement -> STALE
        p = os.path.join(tmp, "n5.json")
        f = json.loads(json.dumps(face))
        f["inputs"]["l1_arm"]["sha256"] = "0" * 64
        io.open(p, "w", encoding="utf-8").write(json.dumps(f, ensure_ascii=False))
        rc, out = run_check(p, real_lattice, real_l1)
        ok(rc == 3 and "STALE" in out, "N5 equity arm digest drift -> STALE", out.strip())

        # N6 a leg grew a day -> STALE (freshness probe, not a defect)
        p = os.path.join(tmp, "n6.json")
        f = json.loads(json.dumps(face))
        f["inputs"]["legs"]["IC"]["days"] -= 1
        io.open(p, "w", encoding="utf-8").write(json.dumps(f, ensure_ascii=False))
        rc, out = run_check(p, real_lattice, real_l1)
        ok(rc == 3 and "STALE" in out, "N6 leg length drift -> STALE", out.strip())

        # N7 no face at all -> STALE (never a silent green)
        rc, out = run_check(os.path.join(tmp, "nope.json"), real_lattice, real_l1)
        ok(rc == 3 and "STALE" in out, "N7 missing face -> STALE", out.strip())

        # N8 a face carrying a refusal is not a green check
        p = os.path.join(tmp, "n8.json")
        io.open(p, "w", encoding="utf-8").write(json.dumps(
            {"schema": L.SCHEMA, "refusal": {"verdict": "DATA_BLOCKED", "why": "x"}}))
        rc, out = run_check(p, real_lattice, real_l1)
        ok(rc == 3 and "STALE" in out, "N8 refusal face -> STALE", out.strip())

        # N9 missing ladder -> STALE
        p = os.path.join(tmp, "n9.json")
        io.open(p, "w", encoding="utf-8").write(json.dumps(face, ensure_ascii=False))
        rc, out = run_check(p, os.path.join(tmp, "no_ladder.json"), real_l1)
        ok(rc == 3 and "STALE" in out, "N9 missing ladder -> STALE", out.strip())
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("NEGATIVE %d/%d %s" % (len(PASS), len(PASS) + len(FAIL),
                                 "ALL_CONTROLS_PASS" if not FAIL else "FAILED:" + ",".join(FAIL)))
    return 0 if not FAIL else 1


if __name__ == "__main__":
    sys.exit(main())
