# -*- coding: utf-8 -*-
"""_r247bmc_s6_chain.py -- S6 maintenance chain driver for bm-c r247.
Runs the standing chain in order (pool_dualrun FIRST per T-116 s3 law),
captures per-leg rc + tail line, writes results/_r247bmc_s6_chain.json.
Lane guards are internal to each script (honest no-op stdout for
non-host machines). Zero output suppression: rc is the contract."""
import json
import subprocess
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

CHAIN = [
    ("pool_dualrun_reconcile", ["scripts/pool_dualrun_reconcile.py", "run"]),
    ("compute_audit", ["scripts/compute_audit.py"]),
    ("py_watermark", ["scripts/py_watermark.py", "probe"]),
    ("update_daily", ["scripts/update_daily.py"]),
    ("market_regime", ["scripts/market_regime.py"]),
    ("strategy_scorecard", ["scripts/strategy_scorecard.py"]),
    ("market_clock_call", ["scripts/market_clock_call.py", "run"]),
    ("update_lhb", ["scripts/update_lhb.py"]),
    ("update_heat", ["scripts/update_heat.py"]),
    ("update_futures", ["scripts/update_futures.py"]),
    ("update_repo", ["scripts/update_repo.py"]),
    ("update_options", ["scripts/update_options.py"]),
    ("update_moneyflow", ["scripts/update_moneyflow.py"]),
    ("update_sina_mf", ["scripts/update_sina_mf.py"]),
    ("update_astock_daily", ["scripts/update_astock_daily.py"]),
    ("update_etf_daily", ["scripts/update_etf_daily.py"]),
    ("rev_osc_signal_export", ["scripts/rev_osc_signal_export.py", "run"]),
    ("update_minute_feed", ["scripts/update_minute_feed.py"]),
    ("update_ths_panel", ["scripts/update_ths_panel.py"]),
    ("ah_panel_puller", ["scripts/ah_panel_puller.py"]),
    ("update_fund_premium", ["scripts/update_fund_premium.py", "snapshot"]),
    ("update_fundamental", ["scripts/update_fundamental.py"]),
    ("b_layer_filter", ["-m", "firm.risk.b_layer_filter"]),
    ("live_paper", ["-m", "live.paper"]),
    ("t35_open_fill_verify", ["scripts/t35_open_fill_verify.py"]),
    ("t24_prospect_paper", ["scripts/t24_prospect_paper.py", "run"]),
    ("t24_prospect_promotion", ["scripts/t24_prospect_promotion.py", "run"]),
    ("aggressive_lab", ["scripts/aggressive_lab.py", "paper"]),
    ("alloc_paper", ["scripts/alloc_paper.py", "run"]),
    ("grid_paper", ["scripts/grid_paper.py", "run"]),
    ("system_v1_paper", ["scripts/system_v1_paper.py", "run"]),
    ("t35_paper_export", ["scripts/t35_paper_export.py", "run"]),
    ("daily_scorecard", ["scripts/daily_scorecard.py"]),
    ("daily_report", ["scripts/daily_report.py", "run"]),
    ("ceo_live_usage", ["scripts/ceo_live_usage.py"]),
    ("build_status", ["-m", "monitor.build_status"]),
    ("token_meter", ["scripts/token_meter.py"]),
]

out = {"round": "r247", "machine": "bm-c", "started": time.strftime(
    "%Y-%m-%dT%H:%M:%S+08:00"), "legs": []}
n_green = 0
for name, args in CHAIN:
    t0 = time.time()
    try:
        r = subprocess.run([sys.executable] + args,
                           capture_output=True, text=True,
                           encoding="utf-8", errors="replace",
                           timeout=600)
        rc = r.returncode
        tail = (r.stdout or "").strip().splitlines()[-1:] or [""]
        tail = tail[0][:160]
        err_tail = (r.stderr or "").strip().splitlines()[-1:] or [""]
        err_tail = err_tail[0][:160] if rc != 0 else ""
    except subprocess.TimeoutExpired:
        rc, tail, err_tail = 124, "TIMEOUT", ""
    except Exception as e:  # mechanism fault face
        rc, tail, err_tail = 2, "", str(e)[:160]
    leg = {"leg": name, "rc": rc, "sec": round(time.time() - t0, 1),
           "tail": tail}
    if err_tail:
        leg["err_tail"] = err_tail
    out["legs"].append(leg)
    if rc == 0:
        n_green += 1
    print("%-24s rc=%s %5.1fs %s" % (name, rc, leg["sec"], tail[:110]))

out["n_green"] = n_green
out["n_total"] = len(CHAIN)
out["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
with open("results/_r247bmc_s6_chain.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
nongreen = [(l["leg"], l["rc"]) for l in out["legs"] if l["rc"] != 0]
print("CHAIN: %d/%d green; non-green: %s" % (n_green, len(CHAIN), nongreen))
