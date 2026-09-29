# r449 bm-a S6 chain runner -- r236 GBK law: subprocess utf-8 errors=replace capture,
# stdout reconfigured utf-8. Leg order = Tools/iteration_prompt.txt S6 fixed order.
import subprocess, sys, io, json, os, time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
os.chdir(REPO)

LEGS = [
    ("pool_dualrun_reconcile", ["scripts/pool_dualrun_reconcile.py", "run"], 240),
    ("compute_audit",           ["scripts/compute_audit.py"], 240),
    ("py_watermark",            ["scripts/py_watermark.py", "probe"], 240),
    ("update_daily",            ["scripts/update_daily.py"], 300),
    ("market_regime",           ["scripts/market_regime.py"], 240),
    ("strategy_scorecard",      ["scripts/strategy_scorecard.py"], 300),
    ("market_clock_call",       ["scripts/market_clock_call.py", "run"], 240),
    ("update_lhb",              ["scripts/update_lhb.py"], 240),
    ("update_heat",             ["scripts/update_heat.py"], 240),
    ("update_futures",          ["scripts/update_futures.py"], 240),
    ("update_repo",             ["scripts/update_repo.py"], 240),
    ("update_options",          ["scripts/update_options.py"], 240),
    ("update_moneyflow",        ["scripts/update_moneyflow.py"], 240),
    ("update_sina_mf",          ["scripts/update_sina_mf.py"], 240),
    ("update_astock_daily",     ["scripts/update_astock_daily.py"], 120),
    ("update_etf_daily",        ["scripts/update_etf_daily.py"], 120),
    ("rev_osc_signal_export",   ["scripts/rev_osc_signal_export.py", "run"], 120),
    ("update_minute_feed",      ["scripts/update_minute_feed.py"], 120),
    ("update_ths_panel",        ["scripts/update_ths_panel.py"], 240),
    ("ah_panel_puller",         ["scripts/ah_panel_puller.py"], 240),
    ("update_fund_premium",     ["scripts/update_fund_premium.py", "snapshot"], 240),
    ("update_fundamental",      ["scripts/update_fundamental.py"], 240),
    ("b_layer_filter",          ["-m", "firm.risk.b_layer_filter"], 240),
    ("live_paper",              ["-m", "live.paper"], 420),
    ("t35_open_fill_verify",    ["scripts/t35_open_fill_verify.py"], 240),
    ("t24_prospect_paper",      ["scripts/t24_prospect_paper.py", "run"], 300),
    ("t24_prospect_promotion",  ["scripts/t24_prospect_promotion.py", "run"], 300),
    ("aggressive_lab_paper",    ["scripts/aggressive_lab.py", "paper"], 300),
    ("alloc_paper",             ["scripts/alloc_paper.py", "run"], 300),
    ("grid_paper",              ["scripts/grid_paper.py", "run"], 300),
    ("system_v1_paper",         ["scripts/system_v1_paper.py", "run"], 420),
    ("t35_paper_export",        ["scripts/t35_paper_export.py", "run"], 240),
    ("daily_scorecard",         ["scripts/daily_scorecard.py"], 300),
    ("daily_report",            ["scripts/daily_report.py", "run"], 300),
    ("ceo_live_usage",          ["scripts/ceo_live_usage.py"], 300),
    ("build_status",            ["-m", "monitor.build_status"], 300),
    ("token_meter",             ["scripts/token_meter.py"], 240),
]

def main():
    env = dict(os.environ)
    env["BIGMONEY_REGIME_GUARD"] = "enforce"   # S6 contract: set when new-bar legs run (v3 date-gate honest-degrade pre 10-01)
    out = []
    for name, args, tmo in LEGS:
        cmd = [sys.executable, "-X", "utf8"] + args
        t0 = time.time()
        try:
            r = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace",
                               timeout=tmo, env=env, cwd=REPO)
            rc, txt = r.returncode, (r.stdout or "") + (r.stderr or "")
        except subprocess.TimeoutExpired:
            rc, txt = -1, f"TIMEOUT after {tmo}s"
        dur = round(time.time() - t0, 1)
        lines = [ln.strip() for ln in txt.splitlines() if ln.strip()]
        tail = lines[-1] if lines else "(no output)"
        out.append({"leg": name, "rc": rc, "sec": dur, "tail": tail[:220]})
        print(f"[{name}] rc={rc} {dur}s :: {tail[:180]}")
        sys.stdout.flush()
    bad = [o for o in out if o["rc"] not in (0,)]
    print(f"\n== S6 chain r449: {len(out)} legs, {len(out)-len(bad)} rc0, {len(bad)} non-zero ==")
    for o in bad:
        print("  !!", o["leg"], "rc=", o["rc"], o["tail"][:200])
    with open("results/_r449bma_s6_chain.json", "w", encoding="utf-8") as f:
        json.dump({"round": 449, "ts": time.strftime("%Y-%m-%d %H:%M:%S"), "legs": out}, f, ensure_ascii=False, indent=1)
    print("log -> results/_r449bma_s6_chain.json")

if __name__ == "__main__":
    main()
