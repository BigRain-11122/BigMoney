"""r1221 bm-c S6 chain runner (39 legs (absorbed continuation), python -u, flush per leg)."""
import subprocess, sys, time, json

LEGS = [
    ("dualrun", ["scripts\\pool_dualrun_reconcile.py", "run"]),
    ("compute_audit", ["scripts\\compute_audit.py"]),
    ("py_watermark", ["scripts\\py_watermark.py", "probe"]),
    ("update_daily", ["scripts\\update_daily.py"]),
    ("market_regime", ["scripts\\market_regime.py"]),
    ("strategy_scorecard", ["scripts\\strategy_scorecard.py"]),
    ("market_clock_call", ["scripts\\market_clock_call.py", "run"]),
    ("update_lhb", ["scripts\\update_lhb.py"]),
    ("update_zt_pool", ["scripts\\update_zt_pool.py"]),
    ("update_heat", ["scripts\\update_heat.py"]),
    ("update_futures", ["scripts\\update_futures.py"]),
    ("update_repo", ["scripts\\update_repo.py"]),
    ("update_options", ["scripts\\update_options.py"]),
    ("update_moneyflow", ["scripts\\update_moneyflow.py"]),
    ("update_sina_mf", ["scripts\\update_sina_mf.py"]),
    ("update_astock_daily", ["scripts\\update_astock_daily.py"]),
    ("update_etf_daily", ["scripts\\update_etf_daily.py"]),
    ("regime_thermo", ["scripts\\regime_thermo_build.py"]),
    ("regime_gate_dualarm", ["scripts\\regime_gate_dualarm.py", "run"]),
    ("rev_osc_export", ["scripts\\rev_osc_signal_export.py", "run"]),
    ("update_minute_feed", ["scripts\\update_minute_feed.py"]),
    ("update_ths_panel", ["scripts\\update_ths_panel.py"]),
    ("ah_panel_puller", ["scripts\\ah_panel_puller.py"]),
    ("fund_premium", ["scripts\\update_fund_premium.py", "snapshot"]),
    ("update_fundamental", ["scripts\\update_fundamental.py"]),
    ("b_layer_filter", ["-m", "firm.risk.b_layer_filter"]),
    ("update_fund_statements", ["scripts\\update_fund_statements.py"]),
    ("t35_open_fill_verify", ["scripts\\t35_open_fill_verify.py"]),
    ("t24_prospect_paper", ["scripts\\t24_prospect_paper.py", "run"]),
    ("t24_prospect_promotion", ["scripts\\t24_prospect_promotion.py", "run"]),
    ("aggressive_lab", ["scripts\\aggressive_lab.py", "paper"]),
    ("alloc_paper", ["scripts\\alloc_paper.py", "run"]),
    ("grid_paper", ["scripts\\grid_paper.py", "run"]),
    ("system_v1_paper", ["scripts\\system_v1_paper.py", "run"]),
    ("t35_paper_export", ["scripts\\t35_paper_export.py", "run"]),
    ("daily_scorecard", ["scripts\\daily_scorecard.py"]),
    ("daily_report", ["scripts\\daily_report.py", "run"]),
    ("ceo_live_usage", ["scripts\\ceo_live_usage.py"]),
    ("build_status", ["-m", "monitor.build_status"]),
    ("token_meter", ["scripts\\token_meter.py"]),
]

receipt = {"started": time.strftime("%Y-%m-%dT%H:%M:%S"), "legs": []}
for name, args in LEGS:
    t0 = time.time()
    cmd = [sys.executable, "-u"] + args
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        rc, out, err = p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()
    except subprocess.TimeoutExpired:
        rc, out, err = 124, "", "timeout"
    dur = round(time.time() - t0, 1)
    tail = (out.splitlines()[-1] if out.splitlines() else err.splitlines()[-1] if err.splitlines() else "")
    print("[S6] %-24s rc=%d %5.1fs %s" % (name, rc, dur, tail[:220]), flush=True)
    receipt["legs"].append({"leg": name, "rc": rc, "sec": dur, "tail": tail[:400]})
    receipt["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")

ok = sum(1 for x in receipt["legs"] if x["rc"] == 0)
receipt["summary"] = "%d/%d rc0" % (ok, len(receipt["legs"]))
print("[S6] DONE %s" % receipt["summary"], flush=True)
with open("results\\_r1222bmc_s6_chain.json", "w", encoding="utf-8") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)