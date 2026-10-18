# -*- coding: utf-8 -*-
"""r1110 bm-c S6 Monday pre-market light chain driver (10 legs, r1096-r1109 canon
clone -- same commands verbatim, zero edits; r1056/r1089/r1092-r1109 same-round law).
Log to results/_r1110bmc_s6_log.txt. MUST run under the SYSTEM python
(Python313). Every leg subprocess passes CREATE_NO_WINDOW (U060 silence law).
Leg list = the bm-c-active subset of the r1085 canon LEGS verbatim. Monday
~07:2x run -- bars cutoff 10-16 current (pre-15:30 honest: update_daily/papers
no-ops until TODAY Monday 2026-10-19 15:30); bm-a/bm-b-owned lanes not in the
light subset per R31. r1110 window: W276 PREREG DERIVED + FREEZE-PUSHED origin
770a47fa1f first-try (research/PERPETUAL_N1_W276_PREREG.md 23,554B
sha256_16 5352c7cf343fc5e5 BYTE-IDENTICAL to sim pre-flight; banned_direction
gate ADMIT rc0; bands A 622_501..624_500 25th A-hop / B 624_501..624_700 26th
above-own-A per seat receipt 21b51a102 verbatim) + r1110 closeout = this
window."""

import datetime
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "results", "_r1110bmc_s6_log.txt")
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
        log.write("r1110 bm-c S6 Monday pre-market light chain run %s legs=%d\n" % (started, len(LEGS)))
        log.flush()
        print("r1110 S6 light chain start %s legs=%d" % (started, len(LEGS)))
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
