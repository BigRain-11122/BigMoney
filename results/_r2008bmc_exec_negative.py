"""Negative controls for scripts/astock_veto_executable.py.

Every leg rewrites the face from the pristine bytes itself (no leg inherits the
previous leg's damage), then calls the real check() through the module's own OUT
global, so the assertions are about the shipped guard and not about a copy of it
(r1934: a guard that only recomputes itself never learns it is stale).

Each leg is labelled with what a wrong guard would print instead, so a silent
pass in the future reads as a missing leg rather than as a green tick.

Run:  python results/_r2008bmc_exec_negative.py
"""
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import astock_veto_executable as ex  # noqa: E402

FACE = os.path.join(ROOT, "results", "astock_veto_executable.json")

fails = []
total = [0]


def leg(name, cond, detail=""):
    total[0] += 1
    if not cond:
        fails.append("%s %s" % (name, detail))
    print("  %-58s %s%s" % (name, "PASS" if cond else "FAIL", ("  " + detail) if detail and not cond else ""))


def main():
    if not os.path.exists(FACE):
        print("face missing: run the face first")
        return 2
    pristine = io.open(FACE, "rb").read()
    sha0 = hashlib.sha256(pristine).hexdigest()

    td = tempfile.mkdtemp(prefix="r2008neg-")
    tmp_face = os.path.join(td, "face.json")
    real_out = ex.OUT
    try:
        def write(obj):
            with io.open(tmp_face, "w", encoding="utf-8") as fh:
                json.dump(obj, fh, ensure_ascii=False)

        def fresh():
            return json.loads(pristine.decode("utf-8"))

        def run_check():
            ex.OUT = tmp_face
            try:
                import contextlib
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    rc = ex.check()
                return rc, buf.getvalue()
            finally:
                ex.OUT = real_out

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

        # L5 flipping the executable verdict by hand must be caught, and must not
        # be dressed up as staleness (r1934: defects and drift are different words)
        f = fresh()
        f["verdict"] = "EXECUTABLE_KILLED" if f["verdict"] != "EXECUTABLE_KILLED" else "EXECUTABLE_SURVIVES"
        write(f)
        rc, out = run_check()
        leg("L5 hand-flipped executable verdict -> rc1, no STALE",
            rc == 1 and "STALE" not in out, "rc=%d out=%r" % (rc, out[:160]))

        # L6 same for the research verdict
        f = fresh()
        f["verdict_research"] = ("EXECUTABLE_KILLED"
                                 if f["verdict_research"] != "EXECUTABLE_KILLED"
                                 else "EXECUTABLE_SURVIVES")
        write(f)
        rc, out = run_check()
        leg("L6 hand-flipped research verdict -> rc1", rc == 1, "rc=%d out=%r" % (rc, out[:160]))

        # L7 a gap that disagrees with its own two cagrs is a self-contradiction
        f = fresh()
        f["exec_gap_pp"]["B"] = f["exec_gap_pp"]["B"] + 1e-6
        write(f)
        rc, out = run_check()
        leg("L7 exec_gap_pp[B] nudged by 1e-6 -> rc1", rc == 1, "rc=%d out=%r" % (rc, out[:160]))

        # L8 the research booking must still reproduce the parent: breaking it is
        # a real defect in the experiment, not a drifted input
        f = fresh()
        f["research_arms"]["A"]["cagr_net"] = f["research_arms"]["A"]["cagr_net"] + 1e-6
        write(f)
        rc, out = run_check()
        leg("L8 research arm A moved off the parent anchor -> rc1",
            rc == 1 and "STALE" not in out, "rc=%d out=%r" % (rc, out[:160]))

        # L9 you cannot buy more names than the pool holds
        f = fresh()
        f["executable_arms"]["B"]["mean_size"] = f["research_arms"]["B"]["mean_size"] + 10.0
        write(f)
        rc, out = run_check()
        leg("L9 executable arm larger than its pool -> rc1", rc == 1, "rc=%d out=%r" % (rc, out[:160]))

        # L10 a missing face is a staleness (a writer exists and can rebuild it)
        ex.OUT = real_out
        if os.path.exists(tmp_face):
            os.remove(tmp_face)
        ex.OUT = tmp_face
        try:
            import contextlib
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = ex.check()
            out = buf.getvalue()
        finally:
            ex.OUT = real_out
        leg("L10 absent face -> rc3 STALE", rc == 3 and "STALE" in out, "rc=%d out=%r" % (rc, out[:120]))

        # L11 the restored file is byte-identical to the pristine face
        with io.open(FACE, "rb") as fh:
            back = fh.read()
        leg("L11 shipped face untouched (sha256 identical)",
            hashlib.sha256(back).hexdigest() == sha0)
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
