"""S6 maintenance chain driver (bm-b, holiday window 2026-10-02).
Runs each leg via subprocess, captures rc, prints one compact line per leg.
No-new-bar legs (live.paper/t35/t24_prospect_paper) skipped per chain
condition (holiday: A-share closed until 2026-10-09).
"""
import subprocess, sys, os

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
    ("t24_prospect_promotion", ["python", "scripts/t24_prospect_promotion.py", "run"], None),
    ("aggressive_lab_paper", ["python", "scripts/aggressive_lab.py", "paper"], None),
    ("alloc_paper", ["python", "scripts/alloc_paper.py", "run"], None),
    ("grid_paper", ["python", "scripts/grid_paper.py", "run"], None),
    ("system_v1_paper", ["python", "scripts/system_v1_paper.py", "run"], None),
    ("t35_paper_export", ["python", "scripts/t35_paper_export.py", "run"], None),
    ("daily_scorecard", ["python", "scripts/daily_scorecard.py"], None),
    ("daily_report", ["python", "scripts/daily_report.py", "run"], None),
    ("ceo_live_usage", ["python", "scripts/ceo_live_usage.py"], None),
    ("build_status", ["python", "-m", "monitor.build_status"], None),
    ("token_meter", ["python", "scripts/token_meter.py"], None),
    ("attrition_guard_scan", ["python", "scripts/attrition_ledger_guard.py", "scan"], None),
]

def main():
    fails = []
    for name, cmd, env_extra in LEGS:
        env = os.environ.copy()
        if env_extra:
            env.update(env_extra)
        try:
            p = subprocess.run(cmd, capture_output=True, text=True,
                               encoding="utf-8", errors="replace",
                               timeout=600, env=env)
            rc = p.returncode
            out = (p.stdout or "").strip().splitlines()
            tail = out[-1][:150] if out else (p.stderr or "").strip()[:150]
        except subprocess.TimeoutExpired:
            rc, tail = 99, "TIMEOUT 600s"
        flag = "OK " if rc in (0,) else ("NOOP" if rc == 0 else "RC%d" % rc)
        status = "OK" if rc == 0 else "RC=%d" % rc
        print(f"[{status}] {name} | {tail}")
        if rc not in (0,):
            fails.append((name, rc, tail))
    print("---")
    if fails:
        print("NONZERO LEGS:", [(n, r) for n, r, _ in fails])
        return 2
    print("ALL LEGS rc=0")
    return 0

if __name__ == "__main__":
    sys.exit(main())
