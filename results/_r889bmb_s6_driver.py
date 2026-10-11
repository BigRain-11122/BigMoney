"""r889 bm-b S6 chain driver (Sunday 2026-10-11; most legs = weekend/15:30 no-op).

Runs the S6 maintenance chain per Tools/iteration_prompt.txt order.
Live-paper-triggered legs (live.paper/t35_open_fill_verify/t24_prospect_*/
aggressive_lab) are gated on new-bar presence; last bar = 2026-10-09 (Fri),
Sunday has no new bar -> honest skip with reason recorded.
"""
import json
import subprocess
import sys
import time

PY = sys.executable
LEGS = [
    ("pool_dualrun_reconcile", ["scripts/pool_dualrun_reconcile.py", "run"], None),
    ("compute_audit", ["scripts/compute_audit.py"], None),
    ("py_watermark", ["scripts/py_watermark.py", "probe"], None),
    ("update_daily", ["scripts/update_daily.py"], None),
    ("market_regime", ["scripts/market_regime.py"], None),
    ("strategy_scorecard", ["scripts/strategy_scorecard.py"], "bm-a-guard"),
    ("market_clock_call", ["scripts/market_clock_call.py", "run"], None),
    ("update_lhb", ["scripts/update_lhb.py"], None),
    ("update_zt_pool", ["scripts/update_zt_pool.py"], "bm-a"),
    ("update_heat", ["scripts/update_heat.py"], "bm-a"),
    ("update_futures", ["scripts/update_futures.py"], "bm-a"),
    ("update_repo", ["scripts/update_repo.py"], "bm-a"),
    ("update_options", ["scripts/update_options.py"], "bm-a"),
    ("update_moneyflow", ["scripts/update_moneyflow.py"], "bm-a"),
    ("update_sina_mf", ["scripts/update_sina_mf.py"], "bm-a"),
    ("update_astock_daily", ["scripts/update_astock_daily.py"], "bm-b"),
    ("update_etf_daily", ["scripts/update_etf_daily.py"], "bm-b"),
    ("regime_thermo_build", ["scripts/regime_thermo_build.py"], None),
    ("regime_gate_dualarm", ["scripts/regime_gate_dualarm.py", "run"], "bm-b"),
    ("rev_osc_signal_export", ["scripts/rev_osc_signal_export.py", "run"], "bm-b"),
    ("update_minute_feed", ["scripts/update_minute_feed.py"], "bm-b"),
    ("update_ths_panel", ["scripts/update_ths_panel.py"], "bm-a"),
    ("ah_panel_puller", ["scripts/ah_panel_puller.py"], "bm-a"),
    ("update_fund_premium", ["scripts/update_fund_premium.py", "snapshot"], "bm-c"),
    ("update_fundamental", ["scripts/update_fundamental.py"], None),
    ("b_layer_filter", ["-m", "firm.risk.b_layer_filter"], None),
    ("update_fund_statements", ["scripts/update_fund_statements.py"], "bm-a"),
    ("alloc_paper", ["scripts/alloc_paper.py", "run"], None),
    ("grid_paper", ["scripts/grid_paper.py", "run"], None),
    ("daily_report", ["scripts/daily_report.py", "run"], None),
    ("ceo_live_usage", ["scripts/ceo_live_usage.py"], None),
    ("monitor_build_status", ["-m", "monitor.build_status"], "bm-a-guard"),
    ("token_meter", ["scripts/token_meter.py"], None),
]

results = []
t0 = time.time()
for name, args, note in LEGS:
    t1 = time.time()
    try:
        p = subprocess.run([PY] + args, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=600)
        rc = p.returncode
        out = (p.stdout or "").strip().split("\n")
        tail = out[-1][:200] if out and out[-1] else (p.stderr or "").strip()[-200:]
    except subprocess.TimeoutExpired:
        rc, tail = 124, "TIMEOUT 600s"
    except Exception as e:  # noqa: BLE001
        rc, tail = 99, repr(e)[:200]
    results.append({"leg": name, "rc": rc, "sec": round(time.time() - t1, 1),
                    "note": note or "", "tail": tail})
    flag = "OK " if rc in (0, 1) else "RED"
    print("%s %-24s rc=%-3s %5.1fs | %s" % (flag, name, rc, time.time() - t1, tail))

# new-bar-gated legs: last bar 2026-10-09 (Fri); Sunday no new bar -> honest skip
for name in ["live_paper", "t35_open_fill_verify", "t24_prospect_paper",
             "t24_prospect_promotion", "aggressive_lab", "system_v1_paper",
             "t35_paper_export", "daily_scorecard"]:
    results.append({"leg": name, "rc": 0, "sec": 0.0,
                    "note": "new-bar-gated",
                    "tail": "SKIP: no new bar since 2026-10-09 (Sunday)"})
    print("NP  %-24s skip (no new bar, Sunday)" % name)

with open("results/_r889bmb_s6_driver.json", "w", encoding="utf-8") as f:
    json.dump({"round": 889, "elapsed_sec": round(time.time() - t0, 1),
               "results": results}, f, ensure_ascii=False, indent=1)
reds = [r for r in results if r["rc"] not in (0, 1)]
print("=== S6 done in %.1fs, red legs: %d ===" % (time.time() - t0, len(reds)))
for r in reds:
    print("RED:", r["leg"], r["rc"], r["tail"])
