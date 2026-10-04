# r670 bm-b S6 chain driver: run data/panel maintenance chain, compact rc table, full log to file
import json, os, subprocess, sys

LOG = open("results/_r670bmb_s6_log.txt", "w", encoding="utf-8", newline="\n")

def run(label, args, env_extra=None):
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    p = subprocess.run(args, capture_output=True, env=env)
    out = (p.stdout or b"") + (p.stderr or b"")
    txt = out.decode("utf-8", "replace")
    LOG.write("=== %s rc=%d ===\n%s\n" % (label, p.returncode, txt))
    last = ""
    for ln in reversed(txt.strip().splitlines()):
        last = ln.strip()
        if last:
            break
    print("%-34s rc=%d %s" % (label, p.returncode, last[:90]))
    return p.returncode

def daily_tail_date():
    try:
        with open("data/daily/sh510300.csv", "rb") as f:
            lines = f.read().decode("utf-8", "replace").strip().splitlines()
        return lines[-1].split(",")[0] if lines else "?"
    except OSError:
        return "?"

pre_bar = daily_tail_date()
results = []

# --- unconditional chain (S6 order per round prompt) ---
results.append(("pool_dualrun_reconcile", run("pool_dualrun_reconcile", ["python", "scripts/pool_dualrun_reconcile.py", "run"])))
results.append(("compute_audit", run("compute_audit", ["python", "scripts/compute_audit.py"])))
results.append(("py_watermark", run("py_watermark", ["python", "scripts/py_watermark.py", "probe"])))
results.append(("update_daily", run("update_daily", ["python", "scripts/update_daily.py"])))
results.append(("market_regime", run("market_regime", ["python", "scripts/market_regime.py"])))
results.append(("strategy_scorecard", run("strategy_scorecard", ["python", "scripts/strategy_scorecard.py"])))
results.append(("market_clock_call", run("market_clock_call", ["python", "scripts/market_clock_call.py", "run"])))
results.append(("update_lhb", run("update_lhb", ["python", "scripts/update_lhb.py"])))
results.append(("update_heat", run("update_heat", ["python", "scripts/update_heat.py"])))
results.append(("update_futures", run("update_futures", ["python", "scripts/update_futures.py"])))
results.append(("update_repo", run("update_repo", ["python", "scripts/update_repo.py"])))
results.append(("update_options", run("update_options", ["python", "scripts/update_options.py"])))
results.append(("update_moneyflow", run("update_moneyflow", ["python", "scripts/update_moneyflow.py"])))
results.append(("update_sina_mf", run("update_sina_mf", ["python", "scripts/update_sina_mf.py"])))
results.append(("update_astock_daily", run("update_astock_daily", ["python", "scripts/update_astock_daily.py"])))
results.append(("update_etf_daily", run("update_etf_daily", ["python", "scripts/update_etf_daily.py"])))
results.append(("rev_osc_signal_export", run("rev_osc_signal_export", ["python", "scripts/rev_osc_signal_export.py", "run"])))
results.append(("update_minute_feed", run("update_minute_feed", ["python", "scripts/update_minute_feed.py"])))
results.append(("update_ths_panel", run("update_ths_panel", ["python", "scripts/update_ths_panel.py"])))
results.append(("ah_panel_puller", run("ah_panel_puller", ["python", "scripts/ah_panel_puller.py"])))
results.append(("update_fund_premium", run("update_fund_premium", ["python", "scripts/update_fund_premium.py", "snapshot"])))
results.append(("update_fundamental", run("update_fundamental", ["python", "scripts/update_fundamental.py"])))
results.append(("b_layer_filter", run("b_layer_filter", ["python", "-m", "firm.risk.b_layer_filter"])))
results.append(("update_fund_statements", run("update_fund_statements", ["python", "scripts/update_fund_statements.py"])))

post_bar = daily_tail_date()
new_bar = post_bar != pre_bar
print("NEW_BAR %s (pre=%s post=%s)" % (new_bar, pre_bar, post_bar))

# --- conditional legs: only on new bar (round prompt) ---
if new_bar:
    results.append(("live.paper", run("live.paper", ["python", "-m", "live.paper"], {"BIGMONEY_REGIME_GUARD": "enforce"})))
    results.append(("t35_open_fill_verify", run("t35_open_fill_verify", ["python", "scripts/t35_open_fill_verify.py"])))
    results.append(("t24_prospect_paper", run("t24_prospect_paper", ["python", "scripts/t24_prospect_paper.py", "run"])))
    results.append(("t24_prospect_promotion", run("t24_prospect_promotion", ["python", "scripts/t24_prospect_promotion.py", "run"])))
else:
    print("live.paper/t35/t24 legs: SKIPPED (no new bar, Sunday no-op window)")

# --- paper/aggregate/report faces (idempotent, self-gating) ---
results.append(("aggressive_lab", run("aggressive_lab", ["python", "scripts/aggressive_lab.py", "paper"])))
results.append(("alloc_paper", run("alloc_paper", ["python", "scripts/alloc_paper.py", "run"])))
results.append(("grid_paper", run("grid_paper", ["python", "scripts/grid_paper.py", "run"])))
results.append(("system_v1_paper", run("system_v1_paper", ["python", "scripts/system_v1_paper.py", "run"])))
results.append(("t35_paper_export", run("t35_paper_export", ["python", "scripts/t35_paper_export.py", "run"])))
results.append(("daily_scorecard", run("daily_scorecard", ["python", "scripts/daily_scorecard.py"])))
results.append(("daily_report", run("daily_report", ["python", "scripts/daily_report.py", "run"])))
results.append(("ceo_live_usage", run("ceo_live_usage", ["python", "scripts/ceo_live_usage.py"])))
results.append(("build_status", run("build_status", ["python", "-m", "monitor.build_status"])))
results.append(("token_meter", run("token_meter", ["python", "scripts/token_meter.py"])))

LOG.close()
bad = [(n, rc) for n, rc in results if rc not in (0,)]
json.dump({"round": "r670", "machine": "bm-b", "items": results, "new_bar": new_bar,
           "rc_nonzero": bad}, open("results/_r670bmb_s6_summary.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("SUMMARY total=%d rc_nonzero=%s" % (len(results), bad if bad else "NONE"))
