"""Negative controls for scripts/astock_veto_fill_wait.py.

Every leg rewrites the face from the pristine bytes itself (no leg inherits the
previous leg's damage), then calls the real check() through the module's own OUT
global, so the assertions are about the shipped guard and not about a copy of it
(r1934: a guard that only recomputes itself never learns it is stale).

Each leg is labelled with what a wrong guard would print instead, so a silent
pass in the future reads as a missing leg rather than as a green tick.

Run:  python results/_r2010bmc_fill_wait_negative.py
"""
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import astock_veto_fill_wait as fw  # noqa: E402

FACE = os.path.join(ROOT, "results", "astock_veto_fill_wait.json")

fails = []
total = [0]


def leg(name, cond, detail=""):
    total[0] += 1
    if not cond:
        fails.append("%s %s" % (name, detail))
    print("  %-62s %s%s" % (name, "PASS" if cond else "FAIL",
                            ("  " + detail) if detail and not cond else ""))


def main():
    if not os.path.exists(FACE):
        print("face missing: run the face first")
        return 2
    pristine = io.open(FACE, "rb").read()
    sha0 = hashlib.sha256(pristine).hexdigest()

    td = tempfile.mkdtemp(prefix="r2010neg-")
    tmp_face = os.path.join(td, "face.json")
    real_out = fw.OUT
    try:
        def write(obj):
            with io.open(tmp_face, "w", encoding="utf-8") as fh:
                json.dump(obj, fh, ensure_ascii=False)

        def fresh():
            return json.loads(pristine.decode("utf-8"))

        def run_check():
            fw.OUT = tmp_face
            try:
                import contextlib
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    rc = fw.check()
                return rc, buf.getvalue()
            finally:
                fw.OUT = real_out

        # L1 the shipped face is clean
        write(fresh())
        rc, out = run_check()
        leg("L1 pristine face -> rc0", rc == 0, "rc=%d out=%r" % (rc, out[:120]))

        # L2 a face with no cutoff is a defect, not a staleness
        f = fresh()
        f.pop("evidence_cutoff")
        write(f)
        rc, out = run_check()
        leg("L2 missing cutoff -> rc1 and NOT stale",
            rc == 1 and "STALE" not in out, "rc=%d out=%r" % (rc, out[:120]))

        # L3 a face behind the panel is genuinely stale and may be rebuilt
        f = fresh()
        f["evidence_cutoff"] = "2026-11-19"
        write(f)
        rc, out = run_check()
        leg("L3 cutoff behind panel -> rc3 STALE", rc == 3 and "STALE" in out,
            "rc=%d out=%r" % (rc, out[:120]))

        # L4 a face claiming a bar the panel cannot reach is a defect, not staleness
        f = fresh()
        f["evidence_cutoff"] = "2026-11-23"
        write(f)
        rc, out = run_check()
        leg("L4 cutoff ahead of panel -> rc1 and NOT stale",
            rc == 1 and "STALE" not in out, "rc=%d out=%r" % (rc, out[:120]))

        # L5 flipping the wait verdict by hand must be caught, and must not be
        # dressed up as staleness (r1934: defects and drift are different words)
        f = fresh()
        f["verdict"] = "WAIT_COSTS" if f["verdict"] != "WAIT_COSTS" else "WAIT_RECOVERS"
        write(f)
        rc, out = run_check()
        leg("L5 hand-flipped wait verdict -> rc1, no STALE",
            rc == 1 and "STALE" not in out, "rc=%d out=%r" % (rc, out[:160]))

        # L6 the drop booking must still re-derive r2008's executable verdict
        f = fresh()
        f["verdict_drop"] = ("EXECUTABLE_KILLED"
                             if f["verdict_drop"] != "EXECUTABLE_KILLED"
                             else "EXECUTABLE_SURVIVES")
        write(f)
        rc, out = run_check()
        leg("L6 hand-flipped drop verdict -> rc1", rc == 1, "rc=%d out=%r" % (rc, out[:160]))

        # L7 same for the research anchor
        f = fresh()
        f["verdict_research"] = ("EXECUTABLE_DEGRADED"
                                 if f["verdict_research"] != "EXECUTABLE_DEGRADED"
                                 else "EXECUTABLE_SURVIVES")
        write(f)
        rc, out = run_check()
        leg("L7 hand-flipped research verdict -> rc1", rc == 1, "rc=%d out=%r" % (rc, out[:160]))

        # L8 the drop booking must still reproduce the parent: breaking it is a
        # real defect in the experiment, not a drifted input
        f = fresh()
        f["drop_arms"]["A"]["cagr_net"] = f["drop_arms"]["A"]["cagr_net"] + 1e-6
        f["parent_anchor"]["worst_abs_diff"] = 1e-6
        write(f)
        rc, out = run_check()
        leg("L8 drop arm A moved off the parent anchor -> rc1, no STALE",
            rc == 1 and "STALE" not in out, "rc=%d out=%r" % (rc, out[:160]))

        # L9 waiting can only ever add names back -- a wait booking smaller than
        # the drop booking means the sampler dropped names it never had
        f = fresh()
        f["wait_arms"]["B"]["mean_size"] = f["drop_arms"]["B"]["mean_size"] - 5.0
        write(f)
        rc, out = run_check()
        leg("L9 wait booking smaller than drop -> rc1", rc == 1, "rc=%d out=%r" % (rc, out[:160]))

        # L10 a missing face is a staleness (a writer exists and can rebuild it)
        fw.OUT = real_out
        if os.path.exists(tmp_face):
            os.remove(tmp_face)
        fw.OUT = tmp_face
        try:
            import contextlib
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = fw.check()
            out = buf.getvalue()
        finally:
            fw.OUT = real_out
        leg("L10 absent face -> rc3 STALE", rc == 3 and "STALE" in out,
            "rc=%d out=%r" % (rc, out[:120]))

        # L11 the restored file is byte-identical to the pristine face
        with io.open(FACE, "rb") as fh:
            back = fh.read()
        leg("L11 shipped face untouched (sha256 identical)",
            hashlib.sha256(back).hexdigest() == sha0)

        # L12 _rel must not crash on a path on another drive (a C: tempdir
        # against a K: repo hits exactly this -- r2008 shipped the bug)
        try:
            got = fw._rel(r"C:\some\other\drive\face.json")
            ok = isinstance(got, str) and got
        except Exception as exc:  # noqa: BLE001
            ok = False
            got = repr(exc)
        leg("L12 _rel across drives -> returns a string, no ValueError", ok, str(got)[:120])

        # L13 board_limit is a pure function of (code, date, st) -- pin the four
        # boundaries that a hand-edited map would silently get wrong
        ok = (abs(fw.board_limit("600001", "2024-01-02", False) - 0.10) < 1e-12
              and abs(fw.board_limit("600001", "2024-01-02", True) - 0.05) < 1e-12
              and abs(fw.board_limit("300001", "2020-08-21", False) - 0.10) < 1e-12
              and abs(fw.board_limit("300001", "2020-08-24", False) - 0.20) < 1e-12
              and abs(fw.board_limit("688001", "2020-08-24", True) - 0.20) < 1e-12
              and abs(fw.board_limit("830001", "2024-01-02", False) - 0.30) < 1e-12)
        leg("L13 board_limit boundaries (main/ST/ChiNext reform/STAR/BSE)", ok)
    finally:
        shutil.rmtree(td, ignore_errors=True)

    print()
    if fails:
        print("NEGATIVE CONTROLS FAIL %d/%d" % (len(fails), total[0]))
        for f in fails:
            print("  " + f)
        return 1
    print("NEGATIVE CONTROLS %d/%d PASS" % (total[0], total[0]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
