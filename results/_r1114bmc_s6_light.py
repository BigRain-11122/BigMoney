# -*- coding: utf-8 -*-
"""r1114-continuation bm-c S6 Monday mid-morning light chain driver (10 legs, r1096-r1111 canon
clone -- same commands verbatim, zero edits; r1056/r1089/r1092-r1109 same-round law).
Log to results/_r1114bmc_s6_log.txt. MUST run under the SYSTEM python
(Python313). Every leg subprocess passes CREATE_NO_WINDOW (U060 silence law).
Leg list = the bm-c-active subset of the r1085 canon LEGS verbatim. Monday
~10:5x run -- bars cutoff 10-16 current (pre-15:30 honest: update_daily/papers
no-ops until TODAY Monday 2026-10-19 15:30); bm-a/bm-b-owned lanes not in the
light subset per R31. r1114-continuation window: W277 FULL CYCLE one-window (splice 9e53371814 CLEAN-AT-BIRTH 10th
+ engine self-burn 12/12 0df07c846b+644b4f8459 + sixgate PRE-FINALIZE 40th
+ finalize one-pass ledger 1,031,535+2,200=1,033,735 / K 605,120+2,200=607,320
EXACT + fivekeys 6/6 ALL PASS + sec.7/8 backfill zero-placeholder; bands A 624_701..626_700
26th A-hop / B 626_701..626_900 27th above-own-A per seat receipt verbatim + W278 SEAT
PUBLISHED b187aa6214 (A 626_901..628_900 27th A-hop / B 628_901..629_100 28th above-own-A);
r1114-continuation closeout = this window."""

import datetime
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "results", "_r1114bmc_s6_log.txt")
PY = sys.executable
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

LEGS = [
    ("pool_dualrun_reconcile", [PY, "scripts/pool_dualrun_reconcile.py", "run"]),
    ("compute_audit", [PY, "scripts/compute_audit.py"]),
    ("py_watermark", [PY, "scripts/py_watermark.py", "probe"]),
    ("update_daily", [PY, "scripts/update_daily.py"]),
    ("market_regime", [PY, "scripts/market_regime.py"]),
    ("market_clock_call", [PY, "scripts/market_clock_call.py", "run"]),
    ("update_fund_premium", [PY, "scripts/update_fund_premium.py", "snapshot"]),
    ("b_layer_filter", [PY, "-m", "firm.risk.b_layer_filter"]),
    ("daily_report", [PY, "scripts/daily_report.py", "run"]),
    ("token_meter", [PY, "scripts/token_meter.py"]),
]


def main():
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    started = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    results = []
    with open(LOG, "w", encoding="utf-8") as log:
        log.write("r1114-continuation bm-c S6 Monday mid-morning light chain run %s legs=%d\n" % (started, len(LEGS)))
        log.flush()
        print("r1114-continuation S6 light chain start %s legs=%d" % (started, len(LEGS)))
        for name, cmd in LEGS:
            log.write("\n===== %s =====\n$ %s\n" % (name, " ".join(cmd)))
            log.flush()
            p = subprocess.run(cmd, cwd=ROOT, env=env,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,
                              creationflags=CNW)
            out = p.stdout.decode("utf-8", "replace")
            log.write(out)
            results.append((name, p.returncode))
            log.write("\n[rc=%d]\n" % p.returncode)
            log.flush()
            print("leg %s rc=%d" % (name, p.returncode))
        log.write("\nDONE %s\n" % datetime.datetime.now().astimezone().isoformat(
            timespec="seconds"))
    bad = [(n, rc) for n, rc in results if rc != 0]
    print("S6 legs=%d rc0=%d nonzero=%d" % (len(results), len(results) - len(bad),
                                            len(bad)))
    for n, rc in results:
        print("%-26s rc=%d" % (n, rc))
    return 2 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
