# r931 bm-a S6 chain driver (r926 bloodline rolled one generation; past-midnight window; O-20261009-2340 thermo leg ADDED after update_etf_daily per order handoff item 2)
# update_options leg SKIPPED per CEO kill order O-20261009-1105 sec1.2 (options-collection-lane; bm-c formal disposition due 10-16; r913/r916/r918/r926 precedent) -> 39 legs.
import subprocess, json, os, sys, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root
os.chdir(ROOT)

def now():
    return datetime.datetime.now().strftime("%H:%M:%S")

LEGS = [
    ("dualrun_reconcile", [sys.executable, "scripts/pool_dualrun_reconcile.py", "run"]),
    ("compute_audit", [sys.executable, "scripts/compute_audit.py"]),
    ("py_watermark", [sys.executable, "scripts/py_watermark.py", "probe"]),
    ("update_daily", [sys.executable, "scripts/update_daily.py"]),
    ("market_regime", [sys.executable, "scripts/market_regime.py"]),
    ("strategy_scorecard", [sys.executable, "scripts/strategy_scorecard.py"]),
    ("market_clock_call", [sys.executable, "scripts/market_clock_call.py", "run"]),
    ("update_lhb", [sys.executable, "scripts/update_lhb.py"]),
    ("update_zt_pool", [sys.executable, "scripts/update_zt_pool.py"]),
    ("update_heat", [sys.executable, "scripts/update_heat.py"]),
    ("update_futures", [sys.executable, "scripts/update_futures.py"]),
    ("update_repo", [sys.executable, "scripts/update_repo.py"]),
    ("update_moneyflow", [sys.executable, "scripts/update_moneyflow.py"]),
    ("update_sina_mf", [sys.executable, "scripts/update_sina_mf.py"]),
    ("update_astock_daily", [sys.executable, "scripts/update_astock_daily.py"]),
    ("update_etf_daily", [sys.executable, "scripts/update_etf_daily.py"]),
    ("regime_thermo_build", [sys.executable, "scripts/regime_thermo_build.py"]),
    ("rev_osc_signal_export", [sys.executable, "scripts/rev_osc_signal_export.py", "run"]),
    ("update_minute_feed", [sys.executable, "scripts/update_minute_feed.py"]),
    ("update_ths_panel", [sys.executable, "scripts/update_ths_panel.py"]),
    ("ah_panel_puller", [sys.executable, "scripts/ah_panel_puller.py"]),
    ("update_fund_premium", [sys.executable, "scripts/update_fund_premium.py", "snapshot"]),
    ("update_fundamental", [sys.executable, "scripts/update_fundamental.py"]),
    ("b_layer_filter", [sys.executable, "-m", "firm.risk.b_layer_filter"]),
    ("update_fund_statements", [sys.executable, "scripts/update_fund_statements.py"]),
]

PAPER_LEGS = [
    ("live_paper", [sys.executable, "-m", "live.paper"], True),   # env REGIME_GUARD=enforce
    ("t35_open_fill_verify", [sys.executable, "scripts/t35_open_fill_verify.py"], False),
    ("t24_prospect_paper", [sys.executable, "scripts/t24_prospect_paper.py", "run"], False),
    ("t24_prospect_promotion", [sys.executable, "scripts/t24_prospect_promotion.py", "run"], False),
    ("aggressive_lab_paper", [sys.executable, "scripts/aggressive_lab.py", "paper"], False),
    ("alloc_paper", [sys.executable, "scripts/alloc_paper.py", "run"], False),
    ("grid_paper", [sys.executable, "scripts/grid_paper.py", "run"], False),
    ("system_v1_paper", [sys.executable, "scripts/system_v1_paper.py", "run"], False),
    ("t35_paper_export", [sys.executable, "scripts/t35_paper_export.py", "run"], False),
    ("daily_scorecard", [sys.executable, "scripts/daily_scorecard.py"], False),
    ("daily_report", [sys.executable, "scripts/daily_report.py", "run"], False),
    ("ceo_live_usage", [sys.executable, "scripts/ceo_live_usage.py"], False),
    ("build_status", [sys.executable, "-m", "monitor.build_status"], False),
    ("token_meter", [sys.executable, "scripts/token_meter.py"], False),
]

def run_leg(name, cmd, env_extra=None, timeout=600):
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    t0 = datetime.datetime.now()
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=timeout, env=env)
        rc = p.returncode
        out = (p.stdout or b"").decode("utf-8", errors="replace")
        err = (p.stderr or b"").decode("utf-8", errors="replace")
    except subprocess.TimeoutExpired:
        rc, out, err = -9, "", "TIMEOUT"
    dt = (datetime.datetime.now() - t0).total_seconds()
    tail = "\n".join((out.strip().splitlines() or [""])[-3:])
    print(f"[{now()}] {name}: rc={rc} ({dt:.0f}s)", flush=True)
    if rc not in (0,):
        print(f"  TAIL>> {tail[:400]}", flush=True)
        if err.strip():
            print(f"  ERR>> {err.strip().splitlines()[-1][:300]}", flush=True)
    return {"name": name, "rc": rc, "sec": round(dt, 1), "tail": tail[-600:], "err_tail": err.strip()[-300:]}

def main():
    summary = {"start": now(), "legs": []}
    def panel_tail_date():
        try:
            with open("data/daily/sh510300.csv", "rb") as f:
                data = f.read()[-200:].decode("utf-8", errors="replace").strip().splitlines()
                return data[-1].split(",")[0] if data else ""
        except Exception as e:
            return "ERR:" + str(e)[:50]
    pre_date = panel_tail_date()
    print("panel tail BEFORE:", pre_date, flush=True)

    for name, cmd in LEGS:
        summary["legs"].append(run_leg(name, cmd))

    post_date = panel_tail_date()
    print("panel tail AFTER update_daily:", post_date, flush=True)
    new_bar = post_date == "2026-10-10"
    summary["new_bar"] = new_bar
    summary["panel_pre"] = pre_date
    summary["panel_post"] = post_date

    for name, cmd, guard in PAPER_LEGS:
        env_extra = {"BIGMONEY_REGIME_GUARD": "enforce"} if guard else None
        summary["legs"].append(run_leg(name, cmd, env_extra=env_extra))

    summary["end"] = now()
    bad = [l for l in summary["legs"] if l["rc"] not in (0,)]
    summary["bad_legs"] = [(l["name"], l["rc"]) for l in bad]
    with open("results/_r931bma_s6_chain.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)
    print("SUMMARY bad_legs:", summary["bad_legs"] or "NONE", flush=True)

if __name__ == "__main__":
    main()
