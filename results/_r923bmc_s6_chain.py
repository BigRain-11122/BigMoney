# _r923bmc_s6_chain.py -- r921 bm-c S6 evidence-legs chain (r919 absorb-window
# precedent: full 38-leg chain ran r914 window 06:43-06:48 + panels 08:03-08:07
# r916 same morning; intraday-gated legs would be identical no-ops at 10:2x --
# re-run the evidence legs per r919: pool_dualrun FIRST law + compute_audit +
# py_watermark + token_meter. Monday new-bar full chain = 15:30+ window today.)
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "results", "_r923bmc_s6_log.txt")
LOGL = os.path.join(ROOT, "results", "_r923bmc_s6_log.jsonl")
PY = sys.executable

LEGS = [
    ("pool_dualrun", ["scripts/pool_dualrun_reconcile.py", "run"], 300),
    ("compute_audit", ["scripts/compute_audit.py"], 300),
    ("py_watermark", ["scripts/py_watermark.py", "probe"], 300),
    ("token_meter", ["scripts/token_meter.py"], 300),
]

SKIPPED = [
    ("full_38_leg_chain", "ran r914 window 06:43-06:48 + panels r916 08:03-08:07 this morning; intraday no-op legs identical; Monday new-bar full chain = 15:30+ window today"),
    ("live_paper", "no new bar (Friday 2026-10-09 processed; Monday 10:2x intraday, new bar 15:30 today)"),
    ("t35_open_fill_verify", "same trigger: no new bar"),
    ("t24_prospect_paper", "same trigger: no new bar"),
    ("t24_prospect_promotion", "same trigger: no new bar"),
    ("science_audit", "monthly first-round leg; 10-12 is not month-first"),
    ("monthly_briefing", "monthly first-round leg"),
    ("self_review", "monthly first-round leg"),
]


def main():
    rows = []
    n_ok = 0
    n_bad = 0
    with open(LOG, "w", encoding="utf-8") as lh, \
            open(LOGL, "w", encoding="utf-8") as jl:
        lh.write("r921 bm-c S6 evidence-legs start %s\n"
                 % time.strftime("%Y-%m-%d %H:%M:%S"))
        for name, args, tmo in LEGS:
            t0 = time.time()
            try:
                p = subprocess.run([PY] + args, capture_output=True,
                                  text=True, timeout=tmo, cwd=ROOT,
                                  encoding="utf-8", errors="replace")
                rc = p.returncode
                out = ((p.stdout or "") + (p.stderr or "")).strip()
            except subprocess.TimeoutExpired:
                rc = -9
                out = "TIMEOUT after %ss" % tmo
            tail = out.splitlines()[-1][:200] if out else ""
            dt = round(time.time() - t0, 1)
            bad = rc not in (0,)
            n_bad += 1 if bad else 0
            n_ok += 0 if bad else 1
            lh.write("%-22s rc=%-3s %6.1fs %s\n" % (name, rc, dt, tail))
            lh.flush()
            jl.write(json.dumps({"leg": name, "rc": rc, "sec": dt,
                                 "tail": tail}) + "\n")
            jl.flush()
            print("%s rc=%s %.1fs" % (name, rc, dt), flush=True)
        for name, why in SKIPPED:
            lh.write("%-22s SKIP  %s\n" % (name, why))
            jl.write(json.dumps({"leg": name, "rc": "SKIP",
                                 "why": why}) + "\n")
        lh.write("SUMMARY ok=%d bad=%d skipped=%d\n"
                 % (n_ok, n_bad, len(SKIPPED)))
    print("SUMMARY ok=%d bad=%d skipped=%d" % (n_ok, n_bad, len(SKIPPED)))
    return 0 if n_bad == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
