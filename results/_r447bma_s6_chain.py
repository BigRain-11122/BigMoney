# -*- coding: utf-8 -*-
"""_r447bma_s6_chain.py -- r447 bm-a S6 data & panel maintenance chain driver.
Mandated leg order (Tools/iteration_prompt.txt S6): pool_dualrun_reconcile
BEFORE compute_audit (settle-before-evidence law), then the standing chain.
New-bar relay legs run because the 2026-09-29 bar is in-panel (freshness 0d).
Evidence -> results/_r447bma_s6_chain.json. Exit codes surfaced verbatim
(rc=2/3 reported, never masked)."""
import json
import os
import subprocess
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

OUT = "results/_r447bma_s6_chain.json"

LEG = [
    ("pool_dualrun_reconcile", ["python", "scripts/pool_dualrun_reconcile.py", "run"], {}),
    ("compute_audit", ["python", "scripts/compute_audit.py"], {}),
    ("py_watermark", ["python", "scripts/py_watermark.py", "probe"], {}),
    ("update_daily", ["python", "scripts/update_daily.py"], {}),
    ("market_regime", ["python", "scripts/market_regime.py"], {}),
    ("strategy_scorecard", ["python", "scripts/strategy_scorecard.py"], {}),
    ("market_clock_call", ["python", "scripts/market_clock_call.py", "run"], {}),
    ("update_lhb", ["python", "scripts/update_lhb.py"], {}),
    ("update_heat", ["python", "scripts/update_heat.py"], {}),
    ("update_futures", ["python", "scripts/update_futures.py"], {}),
    ("update_repo", ["python", "scripts/update_repo.py"], {}),
    ("update_options", ["python", "scripts/update_options.py"], {}),
    ("update_moneyflow", ["python", "scripts/update_moneyflow.py"], {}),
    ("update_sina_mf", ["python", "scripts/update_sina_mf.py"], {}),
    ("update_astock_daily", ["python", "scripts/update_astock_daily.py"], {}),
    ("update_etf_daily", ["python", "scripts/update_etf_daily.py"], {}),
    ("rev_osc_signal_export", ["python", "scripts/rev_osc_signal_export.py", "run"], {}),
    ("update_minute_feed", ["python", "scripts/update_minute_feed.py"], {}),
    ("update_ths_panel", ["python", "scripts/update_ths_panel.py"], {}),
    ("ah_panel_puller", ["python", "scripts/ah_panel_puller.py"], {}),
    ("update_fund_premium", ["python", "scripts/update_fund_premium.py", "snapshot"], {}),
    ("update_fundamental", ["python", "scripts/update_fundamental.py"], {}),
    ("b_layer_filter", ["python", "-m", "firm.risk.b_layer_filter"], {}),
    ("live_paper", ["python", "-m", "live.paper"], {"BIGMONEY_REGIME_GUARD": "enforce"}),
    ("t35_open_fill_verify", ["python", "scripts/t35_open_fill_verify.py"], {}),
    ("t24_prospect_paper", ["python", "scripts/t24_prospect_paper.py", "run"], {}),
    ("t24_prospect_promotion", ["python", "scripts/t24_prospect_promotion.py", "run"], {}),
    ("aggressive_lab_paper", ["python", "scripts/aggressive_lab.py", "paper"], {}),
    ("alloc_paper", ["python", "scripts/alloc_paper.py", "run"], {}),
    ("grid_paper", ["python", "scripts/grid_paper.py", "run"], {}),
    ("system_v1_paper", ["python", "scripts/system_v1_paper.py", "run"], {}),
    ("t35_paper_export", ["python", "scripts/t35_paper_export.py", "run"], {}),
    ("daily_scorecard", ["python", "scripts/daily_scorecard.py"], {}),
    ("daily_report", ["python", "scripts/daily_report.py", "run"], {}),
    ("ceo_live_usage", ["python", "scripts/ceo_live_usage.py"], {}),
    ("build_status", ["python", "-m", "monitor.build_status"], {}),
    ("token_meter", ["python", "scripts/token_meter.py"], {}),
]


def main() -> int:
    env0 = dict(os.environ)
    results = []
    n_bad = 0
    for name, cmd, extra in LEG:
        env = dict(env0)
        env.update(extra)
        env["PYTHONUTF8"] = "1"
        t0 = time.time()
        try:
            p = subprocess.run(cmd, capture_output=True, timeout=1200, env=env)
            rc = p.returncode
            tail = (p.stdout or b"").decode("utf-8", errors="replace").strip().splitlines()[-2:]
            err = (p.stderr or b"").decode("utf-8", errors="replace").strip().splitlines()[-1:]
        except subprocess.TimeoutExpired:
            rc = 99
            tail = ["TIMEOUT 1200s"]
            err = []
        dt = round(time.time() - t0, 1)
        bad = rc not in (0, 1)
        if bad:
            n_bad += 1
        results.append({"leg": name, "rc": rc, "sec": dt,
                        "tail": tail[-1] if tail else "", "err": err[-1] if err else ""})
        flag = "OK " if not bad else "BAD"
        print(f"[{flag}] {name} rc={rc} {dt}s | {results[-1]['tail'][:180]}")
    summary = {"round": "r447", "machine": "bm-a", "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
               "legs": len(LEG), "bad": n_bad, "results": results}
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=1)
    print(f"S6 chain done: {len(LEG) - n_bad}/{len(LEG)} green, evidence -> {OUT}")
    return 0 if n_bad == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
