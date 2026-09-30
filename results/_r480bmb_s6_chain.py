# r480 bm-b S6 chain driver: fixed leg order, per-leg rc + tail, summary JSON.
# Host-guarded legs run anyway -- their in-script guards emit honest no-op stdout.
import json
import os
import subprocess
import sys
import time

LEGS = [
    ("pool_dualrun_reconcile", ["python", "scripts/pool_dualrun_reconcile.py", "run"], None),
    ("compute_audit", ["python", "scripts/compute_audit.py"], None),
    ("py_watermark_probe", ["python", "scripts/py_watermark.py", "probe"], None),
    ("update_daily", ["python", "scripts/update_daily.py"], None),
    ("market_regime", ["python", "scripts/market_regime.py"], None),
    ("strategy_scorecard", ["python", "scripts/strategy_scorecard.py"], None),
    ("market_clock_call", ["python", "scripts/market_clock_call.py", "run"], None),
    ("update_lhb", ["python", "scripts/update_lhb.py"], None),
    ("update_heat", ["python", "scripts/update_heat.py"], None),
    ("update_futures", ["python", "scripts/update_futures.py"], None),
    ("update_repo", ["python", "scripts/update_repo.py"], None),
    ("update_options", ["python", "scripts/update_options.py"], None),
    ("update_moneyflow", ["python", "scripts/update_moneyflow.py"], None),
    ("update_sina_mf", ["python", "scripts/update_sina_mf.py"], None),
    ("update_astock_daily", ["python", "scripts/update_astock_daily.py"], None),
    ("update_etf_daily", ["python", "scripts/update_etf_daily.py"], None),
    ("rev_osc_signal_export", ["python", "scripts/rev_osc_signal_export.py", "run"], None),
    ("update_minute_feed", ["python", "scripts/update_minute_feed.py"], None),
    ("update_ths_panel", ["python", "scripts/update_ths_panel.py"], None),
    ("ah_panel_puller", ["python", "scripts/ah_panel_puller.py"], None),
    ("update_fund_premium", ["python", "scripts/update_fund_premium.py", "snapshot"], None),
    ("update_fundamental", ["python", "scripts/update_fundamental.py"], None),
    ("b_layer_filter", ["python", "-m", "firm.risk.b_layer_filter"], None),
    ("live_paper", ["python", "-m", "live.paper"], {"BIGMONEY_REGIME_GUARD": "enforce"}),
    ("t35_open_fill_verify", ["python", "scripts/t35_open_fill_verify.py"], None),
    ("t24_prospect_paper", ["python", "scripts/t24_prospect_paper.py", "run"], None),
    ("t24_prospect_promotion", ["python", "scripts/t24_prospect_promotion.py", "run"], None),
    ("aggressive_lab_paper", ["python", "scripts/aggressive_lab.py", "paper"], None),
    ("alloc_paper", ["python", "scripts/alloc_paper.py", "run"], None),
    ("grid_paper", ["python", "scripts/grid_paper.py", "run"], None),
    ("system_v1_paper", ["python", "scripts/system_v1_paper.py", "run"], None),
    ("t35_paper_export", ["python", "scripts/t35_paper_export.py", "run"], None),
    ("daily_scorecard", ["python", "scripts/daily_scorecard.py"], None),
    ("daily_report", ["python", "scripts/daily_report.py", "run"], None),
    ("ceo_live_usage", ["python", "scripts/ceo_live_usage.py"], None),
    ("monitor_build_status", ["python", "-m", "monitor.build_status"], None),
    ("token_meter", ["python", "scripts/token_meter.py"], None),
]

results = []
t0 = time.time()
for name, cmd, extra_env in LEGS:
    env = dict(os.environ)
    if extra_env:
        env.update(extra_env)
    tleg = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=900, env=env)
        rc = r.returncode
        tail = (r.stdout.decode("utf-8", errors="replace").strip().splitlines() or [""])
        last = tail[-1][:180] if tail else ""
        err = r.stderr.decode("utf-8", errors="replace").strip()
        if err and rc != 0:
            last = (last + " | STDERR: " + err.splitlines()[-1][:120])[:200]
    except subprocess.TimeoutExpired:
        rc, last = 99, "timeout 900s"
    except Exception as e:
        rc, last = 98, f"driver fault {type(e).__name__}: {e}"
    dt = round(time.time() - tleg, 1)
    results.append({"leg": name, "rc": rc, "sec": dt, "tail": last})
    print(f"[{rc}] {name} ({dt}s) {last}", flush=True)

out = {
    "schema": "s6_chain_v1",
    "round": 480,
    "machine": "bm-b",
    "generated": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
    "total_sec": round(time.time() - t0, 1),
    "legs": results,
}
with open("results/_r480bmb_s6_chain.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
bad = [x for x in results if x["rc"] not in (0, 1, 3)]
print(f"CHAIN DONE total={out['total_sec']}s bad={[x['leg']+':'+str(x['rc']) for x in bad]}")
sys.exit(0 if not bad else 2)
