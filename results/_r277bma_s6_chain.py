# -*- coding: utf-8 -*-
"""R277 bm-a S6 maintenance chain driver (weekend face; bar-triggered legs
skip -- no new bar Saturday 2026-09-26, first-bar chain fires 09-28 Monday).
Each leg: subprocess, rc captured, full stdout/stderr to results/_r277bma_s6_logs/.
Summary JSON to results/_r277bma_s6_summary.json (dict top-level per r276 law).
"""
import json, os, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOGD = ROOT / "results" / "_r277bma_s6_logs"
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

def main():
    summary = {"round": 277, "machine": "bm-a", "ts_start": time.strftime("%Y-%m-%d %H:%M:%S"), "legs": {}}
    for name, cmd, to in LEGS:
        t0 = time.time()
        try:
            r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=to)
            rc, out = r.returncode, (r.stdout or "") + (r.stderr or "")
        except subprocess.TimeoutExpired:
            rc, out = -99, "TIMEOUT"
        (LOGD / f"{name}.log").write_text(out[-20000:], encoding="utf-8", errors="replace")
        summary["legs"][name] = {"rc": rc, "sec": round(time.time() - t0, 1),
                                 "tail": out.strip().splitlines()[-1][:200] if out.strip() else ""}
        print(f"{name}: rc={rc} {round(time.time()-t0,1)}s")
    summary["ts_end"] = time.strftime("%Y-%m-%d %H:%M:%S")
    (ROOT / "results" / "_r277bma_s6_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    bad = {k: v["rc"] for k, v in summary["legs"].items() if v["rc"] not in (0,)}
    print("NONZERO:", json.dumps(bad) if bad else "none")
    return 0

if __name__ == "__main__":
    sys.exit(main())
