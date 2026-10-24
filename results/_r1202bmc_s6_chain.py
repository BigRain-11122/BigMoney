# -*- coding: utf-8 -*-
"""r1202 bm-c: S6 data/panel chain driver (39 legs, W312 open window).

Prints each leg's rc immediately so the tool output stream never idles
(r1186 pit: buffered multi-leg drivers get cancelled by the no-output window).
Every leg is idempotent by design; re-running a leg is safe.
"""
import json
import subprocess
import sys
import time

LEGS = [
    ("dualrun", ["python", "scripts\\pool_dualrun_reconcile.py", "run"]),
    ("compute_audit", ["python", "scripts\\compute_audit.py"]),
    ("py_watermark", ["python", "scripts\\py_watermark.py", "probe"]),
    ("update_daily", ["python", "scripts\\update_daily.py"]),
    ("market_regime", ["python", "scripts\\market_regime.py"]),
    ("scorecard", ["python", "scripts\\strategy_scorecard.py"]),
    ("market_clock", ["python", "scripts\\market_clock_call.py", "run"]),
    ("update_lhb", ["python", "scripts\\update_lhb.py"]),
    ("update_zt_pool", ["python", "scripts\\update_zt_pool.py"]),
    ("update_heat", ["python", "scripts\\update_heat.py"]),
    ("update_futures", ["python", "scripts\\update_futures.py"]),
    ("update_repo", ["python", "scripts\\update_repo.py"]),
    ("update_options", ["python", "scripts\\update_options.py"]),
    ("update_moneyflow", ["python", "scripts\\update_moneyflow.py"]),
    ("update_sina_mf", ["python", "scripts\\update_sina_mf.py"]),
    ("update_astock_daily", ["python", "scripts\\update_astock_daily.py"]),
    ("update_etf_daily", ["python", "scripts\\update_etf_daily.py"]),
    ("regime_thermo", ["python", "scripts\\regime_thermo_build.py"]),
    ("regime_dualarm", ["python", "scripts\\regime_gate_dualarm.py", "run"]),
    ("rev_osc_export", ["python", "scripts\\rev_osc_signal_export.py", "run"]),
    ("minute_feed", ["python", "scripts\\update_minute_feed.py"]),
    ("ths_panel", ["python", "scripts\\update_ths_panel.py"]),
    ("ah_panel", ["python", "scripts\\ah_panel_puller.py"]),
    ("fund_premium", ["python", "scripts\\update_fund_premium.py", "snapshot"]),
    ("fundamental", ["python", "scripts\\update_fundamental.py"]),
    ("b_layer", ["python", "-m", "firm.risk.b_layer_filter"]),
    ("fund_statements", ["python", "scripts\\update_fund_statements.py"]),
    ("t24_paper", ["python", "scripts\\t24_prospect_paper.py", "run"]),
    ("t24_promote", ["python", "scripts\\t24_prospect_promotion.py", "run"]),
    ("aggr_paper", ["python", "scripts\\aggressive_lab.py", "paper"]),
    ("alloc_paper", ["python", "scripts\\alloc_paper.py", "run"]),
    ("grid_paper", ["python", "scripts\\grid_paper.py", "run"]),
    ("system_v1", ["python", "scripts\\system_v1_paper.py", "run"]),
    ("t35_export", ["python", "scripts\\t35_paper_export.py", "run"]),
    ("scorecard_daily", ["python", "scripts\\daily_scorecard.py"]),
    ("daily_report", ["python", "scripts\\daily_report.py", "run"]),
    ("ceo_live_usage", ["python", "scripts\\ceo_live_usage.py"]),
    ("build_status", ["python", "-m", "monitor.build_status"]),
    ("token_meter", ["python", "scripts\\token_meter.py"]),
]

out = []
t0 = time.time()
for name, cmd in LEGS:
    s = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=900)
        rc, txt = p.returncode, (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired:
        rc, txt = 124, "TIMEOUT 900s"
    tail = " | ".join([ln for ln in txt.strip().splitlines() if ln.strip()][-2:])[:400]
    out.append({"leg": name, "rc": rc, "tail": tail, "sec": round(time.time() - s, 1)})
    print("[S6] %-20s rc=%s %.1fs %s" % (name, rc, time.time() - s, tail[:160]), flush=True)

json.dump(out, open("results/_r1202bmc_s6_chain.json", "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
bad = [o for o in out if o["rc"] != 0]
print("[S6] DONE legs=%d nonzero=%d total=%.1fs" % (len(out), len(bad), time.time() - t0),
      flush=True)
sys.exit(0 if not bad else 1)
