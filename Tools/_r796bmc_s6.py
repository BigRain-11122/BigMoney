"""r796 bm-c S6 chain driver: standing-leg canon, full log to
results/_r796bmc_s6_log.txt, compact per-leg rc summary to stdout.
Leg count derived at runtime (honest count, never hand-typed).
Clone credit: Tools/_r795bmc_s6.py (r795 canonical chain, 40 legs rc0,
sixteenth green).
MUST run under the SYSTEM python (Python313): sys.executable is
inherited by every leg and the embedded ComfyUI python has no
pandas/akshare (r516 first attempt = 18 import-crash reds).
Every leg subprocess passes CREATE_NO_WINDOW (zero-desktop-flash
defense-in-depth; U060/2026-10-01 silence law -- safe in ANY host
context).
r796 watch-faces: W17 screen burn RAM gate follow-up round 3 (SHARD-2
launch-claim runner pid 9260 bounded-wait since 09:17, 40min cap
~09:57 lands INSIDE this round window; deadline law = no verdict before
cap time; this window records the live read at chain time -- cap-exit
pickup or RAM release ignition lands per autofill self-continue);
autofill daemon lane stays self-continue; SLA window 10-10 00:00;
update_fund_premium TWELFTH observation window for the 10-08 NAV
first-collect (publish face = fund NAV T+1; this 09:5x window = honest
no-op expected, the 15:30+ round lands the first collect);
update_daily cutoff 10-08 complete -- zero new rows expected (next bar
10-09 15:30); marks legs at 10-08 panel cutoff -- idempotent no-op
expected; bm-a/bm-b-owned lanes honest no-op on this machine per R31
lane guards."""
import datetime
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "results", "_r796bmc_s6_log.txt")
PY = sys.executable
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

LEGS = [
    ("pool_dualrun_reconcile", [PY, "scripts/pool_dualrun_reconcile.py", "run"]),
    ("compute_audit", [PY, "scripts/compute_audit.py"]),
    ("py_watermark", [PY, "scripts/py_watermark.py", "probe"]),
    ("update_daily", [PY, "scripts/update_daily.py"]),
    ("market_regime", [PY, "scripts/market_regime.py"]),
    ("strategy_scorecard", [PY, "scripts/strategy_scorecard.py"]),
    ("market_clock_call", [PY, "scripts/market_clock_call.py", "run"]),
    ("update_lhb", [PY, "scripts/update_lhb.py"]),
    ("update_zt_pool", [PY, "scripts/update_zt_pool.py"]),
    ("update_heat", [PY, "scripts/update_heat.py"]),
    ("update_futures", [PY, "scripts/update_futures.py"]),
    ("update_repo", [PY, "scripts/update_repo.py"]),
    ("update_options", [PY, "scripts/update_options.py"]),
    ("update_moneyflow", [PY, "scripts/update_moneyflow.py"]),
    ("update_sina_mf", [PY, "scripts/update_sina_mf.py"]),
    ("update_astock_daily", [PY, "scripts/update_astock_daily.py"]),
    ("update_etf_daily", [PY, "scripts/update_etf_daily.py"]),
    ("rev_osc_signal_export", [PY, "scripts/rev_osc_signal_export.py", "run"]),
    ("update_minute_feed", [PY, "scripts/update_minute_feed.py"]),
    ("update_ths_panel", [PY, "scripts/update_ths_panel.py"]),
    ("ah_panel_puller", [PY, "scripts/ah_panel_puller.py"]),
    ("update_fund_premium", [PY, "scripts/update_fund_premium.py", "snapshot"]),
    ("update_fundamental", [PY, "scripts/update_fundamental.py"]),
    ("b_layer_filter", [PY, "-m", "firm.risk.b_layer_filter"]),
    ("update_fund_statements", [PY, "scripts/update_fund_statements.py"]),
    ("live_paper", [PY, "-m", "live.paper"],
     {"BIGMONEY_REGIME_GUARD": "enforce"}),
    ("t35_open_fill_verify", [PY, "scripts/t35_open_fill_verify.py"]),
    ("t24_prospect_paper", [PY, "scripts/t24_prospect_paper.py", "run"]),
    ("t24_prospect_promotion", [PY, "scripts/t24_prospect_promotion.py", "run"]),
    ("aggressive_lab", [PY, "scripts/aggressive_lab.py", "paper"]),
    ("alloc_paper", [PY, "scripts/alloc_paper.py", "run"]),
    ("grid_paper", [PY, "scripts/grid_paper.py", "run"]),
    ("cta_p1_paper", [PY, "scripts/cta_p1_paper.py", "run"]),
    ("system_v1_paper", [PY, "scripts/system_v1_paper.py", "run"]),
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
    with open(LOG, "w", encoding="utf-8") as log:
        log.write("r796 bm-c S6 chain run %s legs=%d\n" % (started, len(LEGS)))
        for entry in LEGS:
            name, cmd = entry[0], entry[1]
            leg_env = env
            if len(entry) > 2 and entry[2]:
                leg_env = dict(env)
                leg_env.update(entry[2])
            log.write("\n===== %s =====\n$ %s\n" % (name, " ".join(cmd)))
            log.flush()
            p = subprocess.run(cmd, cwd=ROOT, env=leg_env,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               creationflags=CNW)
            out = p.stdout.decode("utf-8", "replace")
            log.write(out)
            results.append((name, p.returncode))
            log.write("\n[rc=%d]\n" % p.returncode)
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
