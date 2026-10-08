"""r779 bm-c S6 POST-HEAL completion driver (21:4x window).

Context: prior r779 session ran the full 40-leg S6 chain at 21:23-21:24
(aggressive_lab rc=2 honest red: 12 SZ members stale). Targeted in-round
retry at 21:48 landed the 12 lagging SZ members (update_daily new rows=12)
-> live.paper hook stale-takeover derive + aggressive_lab rc=0 (20/20 AGGR
marks through 2026-10-08) already executed in-round. This driver re-runs
the new-bar-affected completion legs so CEO faces reflect the healed panel
(same-leg canon, lane_io guards decide takeover/skip per law).

Clone credit: Tools/_r779bmc_s6.py (r779 canonical chain driver).
MUST run under the SYSTEM python (Python313): sys.executable inherited by
every leg (r516 embedded-python import-crash law).
"""
import datetime
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "results", "_r779bmc_s6_log.txt")
PY = sys.executable

LEGS = [
    ("update_fund_premium", [PY, "scripts/update_fund_premium.py", "snapshot"]),
    ("strategy_scorecard", [PY, "scripts/strategy_scorecard.py"]),
    ("market_clock_call", [PY, "scripts/market_clock_call.py", "run"]),
    ("t35_open_fill_verify", [PY, "scripts/t35_open_fill_verify.py"]),
    ("t24_prospect_paper", [PY, "scripts/t24_prospect_paper.py", "run"]),
    ("t24_prospect_promotion", [PY, "scripts/t24_prospect_promotion.py", "run"]),
    ("grid_paper", [PY, "scripts/grid_paper.py", "run"]),
    ("t35_paper_export", [PY, "scripts/t35_paper_export.py", "run"]),
    ("daily_scorecard", [PY, "scripts/daily_scorecard.py"]),
    ("daily_report", [PY, "scripts/daily_report.py", "run"]),
    ("ceo_live_usage", [PY, "scripts/ceo_live_usage.py"]),
    ("build_status", [PY, "-m", "monitor.build_status"]),
    ("token_meter", [PY, "scripts/token_meter.py"]),
]


def main():
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    started = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    results = []
    with open(LOG, "a", encoding="utf-8") as log:
        log.write("\n\nr779 bm-c S6 POST-HEAL completion legs %s legs=%d\n"
                  % (started, len(LEGS)))
        log.write("prelude: 21:48 targeted retry landed 12 SZ members "
                  "(update_daily new rows=12) -> live.paper stale-takeover "
                  "derive (hook) + aggressive_lab rc=0 (20/20 AGGR marks "
                  "through 2026-10-08) already executed in-round\n")
        for name, cmd in LEGS:
            log.write("\n===== POST-HEAL: %s =====\n" % name)
            log.write("$ %s\n" % " ".join(cmd))
            log.flush()
            proc = subprocess.run(cmd, cwd=ROOT, env=env,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
            out = proc.stdout.decode("utf-8", errors="replace")
            if out:
                log.write(out.rstrip() + "\n")
            log.write("\n[rc=%d]\n" % proc.returncode)
            results.append((name, proc.returncode))
            print("[%s rc=%d]" % (name, proc.returncode))
        rc0 = sum(1 for _, rc in results if rc == 0)
        done = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        log.write("\nPOST-HEAL DONE %s legs=%d rc0=%d nonzero=%d\n"
                  % (done, len(results), rc0, len(results) - rc0))
    print("POSTHEAL_LEGS=%d RC0=%d NONZERO=%d"
          % (len(results), rc0, len(results) - rc0))
    if any(rc != 0 for _, rc in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
