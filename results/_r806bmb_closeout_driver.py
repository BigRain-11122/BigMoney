"""r806 bm-b closeout driver (detached, r801 canon: DETACHED_PROCESS zero-window U060,
BelowNormal CEO margin law, both-redirect log, end-only result writes per family runner).

Sequential closeout chain ignited by the 23:12 r806 closeout session (wrapper-kill
budget pressure, dead r806-w1/w2 estate absorbed):
 1. trio finalize x3 (divlowvol -> quality -> value) -- THE milestone product
    (window 10-05..10-09, D 2000/2000 heal-complete 20:38, mechanical_ready=True,
    governance G-SEG PENDING -> r638 fallback insufficient-sample single-read law)
 2. S6 chain w4 verbatim reuse (dead-session _r806bmb_s6_chain.py, lineage r805;
    legs 25-28 stay skipped this run -- reopen re-arm = next-round small driver,
    honest note; leg 04 update_daily expected to pull the 10-08 reopen bar)
 3. QA pack r806 (charter 5/5, dead-session script verbatim)

Sentinel: DRIVER_DONE line with per-step rc dict. Next round absorbs products +
backfills prereg §7/§8 + verifies leg rc faces from logs.
"""
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "results", "_r806bmb_closeout_driver.log")
PY = sys.executable


def run(lf, step, args):
    lf.write("\n== %s START %s ==\n" % (step, time.strftime("%H:%M:%S")))
    lf.flush()
    rc = subprocess.call(args, cwd=ROOT, stdout=lf, stderr=subprocess.STDOUT)
    lf.write("== %s RC=%s %s ==\n" % (step, rc, time.strftime("%H:%M:%S")))
    lf.flush()
    return rc


def main():
    with open(LOG, "a", encoding="utf-8", newline="\n") as lf:
        lf.write("\n[r806 closeout driver %s pid=%s]\n"
                 % (time.strftime("%Y-%m-%dT%H:%M:%S"), os.getpid()))
        lf.flush()
        rcs = {}
        for fam in ("divlowvol", "quality", "value"):
            rcs["finalize_" + fam] = run(
                lf, "finalize_" + fam,
                [PY, "-u", "scripts/fund_%s_p1.py" % fam, "finalize"])
        rcs["s6_w4"] = run(
            lf, "s6_w4", [PY, "-u", "results/_r806bmb_s6_chain.py"])
        rcs["qa_pack"] = run(
            lf, "qa_pack", [PY, "-u", "results/_r806bmb_qa_pack.py"])
        lf.write("DRIVER_DONE " + repr(rcs) + "\n")
        lf.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
