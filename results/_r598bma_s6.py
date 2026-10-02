"""r598 bm-a S6 chain driver (Golden Week face).

Runs the standing S6 legs with per-leg rc logging (CREATE_NO_WINDOW,
utf-8 captured). Paper/new-bar block legally skipped (no new bar,
r588 precedent). Exit 0 if all legs rc in {0} and no leg rc in {2,3}
unreported; driver itself only REPORTS -- honest passthrough of every
nonzero rc in the summary line.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable

LEGS = [
    ("dualrun", [PY, "scripts/pool_dualrun_reconcile.py", "run"]),
    ("compute_audit", [PY, "scripts/compute_audit.py"]),
    ("wm_probe", [PY, "scripts/py_watermark.py", "probe"]),
    ("update_daily", [PY, "scripts/update_daily.py"]),
    ("market_regime", [PY, "scripts/market_regime.py"]),
    ("scorecard", [PY, "scripts/strategy_scorecard.py"]),
    ("market_clock", [PY, "scripts/market_clock_call.py", "run"]),
    ("lhb", [PY, "scripts/update_lhb.py"]),
    ("heat", [PY, "scripts/update_heat.py"]),
    ("futures", [PY, "scripts/update_futures.py"]),
    ("repo", [PY, "scripts/update_repo.py"]),
    ("options", [PY, "scripts/update_options.py"]),
    ("moneyflow", [PY, "scripts/update_moneyflow.py"]),
    ("sina_mf", [PY, "scripts/update_sina_mf.py"]),
    ("astock", [PY, "scripts/update_astock_daily.py"]),
    ("etf_daily", [PY, "scripts/update_etf_daily.py"]),
    ("rev_osc_export", [PY, "scripts/rev_osc_signal_export.py", "run"]),
    ("minute_feed", [PY, "scripts/update_minute_feed.py"]),
    ("ths_panel", [PY, "scripts/update_ths_panel.py"]),
    ("ah_panel", [PY, "scripts/ah_panel_puller.py"]),
    ("fund_premium", [PY, "scripts/update_fund_premium.py", "snapshot"]),
    ("fundamental", [PY, "scripts/update_fundamental.py"]),
    ("b_layer", [PY, "-m", "firm.risk.b_layer_filter"]),
    ("daily_scorecard", [PY, "scripts/daily_scorecard.py"]),
    ("daily_report", [PY, "scripts/daily_report.py", "run"]),
    ("ceo_live", [PY, "scripts/ceo_live_usage.py"]),
    ("build_status", [PY, "-m", "monitor.build_status"]),
    ("token_meter", [PY, "scripts/token_meter.py"]),
    ("attrition_guard", [PY, "scripts/attrition_ledger_guard.py", "scan"]),
]


def main():
    log = open(os.path.join(ROOT, "results", "_r598bma_s6.log"), "w",
               encoding="utf-8", newline="\n")
    rcs = {}
    for name, cmd in LEGS:
        try:
            r = subprocess.run(cmd, cwd=ROOT, capture_output=True,
                               encoding="utf-8", errors="replace",
                               creationflags=0x08000000, timeout=600)
            rc = r.returncode
            out = (r.stdout or "").strip().splitlines()
            tail = " | ".join(out[-2:]) if out else ""
            err = (r.stderr or "").strip().splitlines()
            etail = " | ".join(err[-2:]) if err else ""
        except subprocess.TimeoutExpired:
            rc, tail, etail = 99, "TIMEOUT", ""
        rcs[name] = rc
        log.write(f"[{name}] rc={rc} :: {tail}\n")
        if etail:
            log.write(f"[{name}] stderr :: {etail}\n")
        log.flush()
    log.close()
    bad = {k: v for k, v in rcs.items() if v not in (0,)}
    print("S6 rcs:", ";".join(f"{k}={v}" for k, v in rcs.items()))
    print("NONZERO:", bad if bad else "none")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
