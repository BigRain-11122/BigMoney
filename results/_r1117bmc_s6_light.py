# -*- coding: utf-8 -*-
"""r1117 bm-c S6 Monday afternoon light chain driver (10 legs, r1096-r1116 canon
clone -- same commands verbatim, zero edits; r1056/r1089/r1092-r1116 same-round law).
Log to results/_r1117bmc_s6_log.txt. MUST run under the SYSTEM python
(Python313). Every leg subprocess passes CREATE_NO_WINDOW (U060 silence law).
Leg list = the bm-c-active subset of the r1085 canon LEGS verbatim. Monday
~13:3x run -- bars cutoff 10-16 current (pre-15:30 honest: update_daily/papers
no-ops until TODAY Monday 2026-10-19 15:30); bm-a/bm-b-owned lanes not in the
light subset per R31. r1117 window: cadence-v2 leg-8 (CEO 2026-10-19 11:53
全面提速令 v2, cph4/cadence.md sec.8 v2 table, 8/8 re-freq + 2 shift
additions, read-back all OK) + REPO-SLIM leg-7 (CEO 12:21 文件库治理令:
hooksPath gate + .gitattributes + repo-slim materialized from origin blobs,
FluxGroup-RepoSlim sentinel registered daily:09:03, first pack rc=0) + D-19
opening delta consumed (15f5bbbf, 1 row kb-v1.2 zero-action)."""

import datetime
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "results", "_r1117bmc_s6_log.txt")
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
        log.write("r1117 bm-c S6 Monday afternoon light chain run %s legs=%d\n" % (started, len(LEGS)))
        log.flush()
        print("r1117 S6 light chain start %s legs=%d" % (started, len(LEGS)))
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
