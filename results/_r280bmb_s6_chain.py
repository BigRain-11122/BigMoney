# -*- coding: utf-8 -*-
"""r280 bm-b S6 maintenance chain driver (weekend face: no new bar Saturday 2026-09-26,
Friday 09-25 Mid-Autumn closed, panel cutoff 2026-09-24; paper family bar-gated ->
honest skip; monthly trio not month-first; quarterly slot discharged 09-26 per T-83
instance ledger). NEW LEG: update_astock_daily (T-87 supply lane, wired r280).
Logs to results/_r280bmb_s6_logs/."""
import json, os, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOGD = ROOT / "results" / "_r280bmb_s6_logs"
LOGD.mkdir(exist_ok=True)

LEGS = [
    ("compute_audit", [sys.executable, "scripts/compute_audit.py"], 600),
    ("py_watermark", [sys.executable, "scripts/py_watermark.py", "probe"], 300),
    ("update_daily", [sys.executable, "scripts/update_daily.py"], 900),
    ("market_regime", [sys.executable, "scripts/market_regime.py"], 300),
    ("strategy_scorecard", [sys.executable, "scripts/strategy_scorecard.py"], 900),
    ("market_clock_call", [sys.executable, "scripts/market_clock_call.py", "run"], 300),
    ("update_lhb", [sys.executable, "scripts/update_lhb.py"], 600),
    ("update_heat", [sys.executable, "scripts/update_heat.py"], 600),
    ("update_futures", [sys.executable, "scripts/update_futures.py"], 600),
    ("update_options", [sys.executable, "scripts/update_options.py"], 600),
    ("update_moneyflow", [sys.executable, "scripts/update_moneyflow.py"], 600),
    ("update_sina_mf", [sys.executable, "scripts/update_sina_mf.py"], 600),
    ("update_astock_daily", [sys.executable, "scripts/update_astock_daily.py"], 600),
    ("update_ths_panel", [sys.executable, "scripts/update_ths_panel.py"], 600),
    ("ah_panel_puller", [sys.executable, "scripts/ah_panel_puller.py"], 600),
    ("update_fund_premium", [sys.executable, "scripts/update_fund_premium.py", "snapshot"], 600),
    ("update_fundamental", [sys.executable, "scripts/update_fundamental.py"], 900),
    ("b_layer_filter", [sys.executable, "-m", "firm.risk.b_layer_filter"], 600),
    ("daily_scorecard", [sys.executable, "scripts/daily_scorecard.py"], 900),
    ("daily_report", [sys.executable, "scripts/daily_report.py", "run"], 900),
    ("monitor_build_status", [sys.executable, "-m", "monitor.build_status"], 900),
    ("token_meter", [sys.executable, "scripts/token_meter.py"], 300),
]

PAPER_GATED = ["live.paper(REGIME_GUARD)", "t35_open_fill_verify", "t24_prospect_paper",
               "t24_prospect_promotion", "aggressive_lab paper", "alloc_paper", "grid_paper", "t35_paper_export"]

def main():
    summary = {"round": 280, "machine": "bm-b", "ts_start": time.strftime("%Y-%m-%d %H:%M:%S"),
               "legs": {}, "paper_family": {k: "skip: no new bar (Saturday, panel cutoff 2026-09-24 unchanged)" for k in PAPER_GATED},
               "monthly_trio": "skip: not month-first round (next=2026-10-01)",
               "quarterly_governance": "skip: Q4-2026 slot discharged 2026-09-26 per T-83 instance ledger"}
    for name, cmd, to in LEGS:
        t0 = time.time()
        try:
            r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=to, encoding="utf-8", errors="replace")
            rc, out = r.returncode, (r.stdout or "") + (r.stderr or "")
        except subprocess.TimeoutExpired:
            rc, out = -99, "TIMEOUT"
        (LOGD / f"{name}.log").write_text(out[-20000:], encoding="utf-8", errors="replace")
        summary["legs"][name] = {"rc": rc, "sec": round(time.time() - t0, 1),
                                 "tail": out.strip().splitlines()[-1][:200] if out.strip() else ""}
        print(f"{name}: rc={rc} {round(time.time()-t0,1)}s", flush=True)
    summary["ts_end"] = time.strftime("%Y-%m-%d %H:%M:%S")
    (ROOT / "results" / "_r280bmb_s6_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    bad = {k: v["rc"] for k, v in summary["legs"].items() if v["rc"] != 0}
    print("NONZERO:", json.dumps(bad, ensure_ascii=False) if bad else "none")
    return 0

if __name__ == "__main__":
    sys.exit(main())
