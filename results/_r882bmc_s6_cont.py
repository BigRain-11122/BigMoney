# _r882bmc_s6_cont.py -- r882 bm-c S6 chain CONTINUATION (legs 25-38)
# First 24 legs landed rc=0 in _r882bmc_s6_log.txt before the shell
# 5-min zero-output auto-kill (Select-Object buffering mistake, not a
# chain fault). This appends the remaining legs to the same log files.

import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "results", "_r882bmc_s6_log.txt")
LOGL = os.path.join(ROOT, "results", "_r882bmc_s6_log.jsonl")
PY = sys.executable

LEGS = [
    ("update_fundamental", ["scripts/update_fundamental.py"], 300),
    ("b_layer_filter", ["-m", "firm.risk.b_layer_filter"], 300),
    ("update_fund_statements", ["scripts/update_fund_statements.py"], 300),
    ("aggressive_lab_paper", ["scripts/aggressive_lab.py", "paper"], 300),
    ("alloc_paper", ["scripts/alloc_paper.py", "run"], 300),
    ("grid_paper", ["scripts/grid_paper.py", "run"], 300),
    ("system_v1_paper", ["scripts/system_v1_paper.py", "run"], 300),
    ("t35_paper_export", ["scripts/t35_paper_export.py", "run"], 300),
    ("daily_scorecard", ["scripts/daily_scorecard.py"], 300),
    ("daily_report", ["scripts/daily_report.py", "run"], 300),
    ("ceo_live_usage", ["scripts/ceo_live_usage.py"], 300),
    ("build_status", ["-m", "monitor.build_status"], 300),
    ("token_meter", ["scripts/token_meter.py"], 300),
    ("queue_seed_gate_scan", ["scripts/queue_seed_gate.py", "scan"], 300),
]


def main():
    # skip legs already recorded in this round's jsonl (GBK console
    # crash mid-print left leg-25 logged-but-unfinished)
    done = set()
    if os.path.exists(LOGL):
        with open(LOGL, encoding="utf-8") as fh:
            for ln in fh:
                try:
                    done.add(json.loads(ln)["leg"])
                except Exception:
                    pass
    rows = []
    n_ok = 0
    n_bad = 0
    with open(LOG, "a", encoding="utf-8") as lh, \
            open(LOGL, "a", encoding="utf-8") as jl:
        for name, args, tmo in LEGS:
            if name in done:
                print("skip (already logged): %s" % name, flush=True)
                continue
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
            print("%s rc=%s %.1fs %s" % (name, rc, dt, tail), flush=True)
        lh.write("SUMMARY(cont) ok=%d bad=%d\n" % (n_ok, n_bad))
    print("SUMMARY(cont) ok=%d bad=%d" % (n_ok, n_bad))
    return 0 if n_bad == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
