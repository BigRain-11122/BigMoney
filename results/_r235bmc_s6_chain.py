"""_r235bmc_s6_chain.py -- bm-c r235 S6 maintenance chain runner (37 legs).

Canon order per DEV prompt (pool_dualrun_reconcile MUST precede compute_audit).
Host-guarded legs honest no-op per their own contracts (R31 lane law).
Per-leg rc + tail line printed; JSON evidence -> results/_r235bmc_s6_chain.json.
"""
import subprocess
import sys
import os
import json

LEGS = [
    ["python", "scripts/pool_dualrun_reconcile.py", "run"],
    ["python", "scripts/compute_audit.py"],
    ["python", "scripts/py_watermark.py", "probe"],
    ["python", "scripts/update_daily.py"],
    ["python", "scripts/market_regime.py"],
    ["python", "scripts/strategy_scorecard.py"],
    ["python", "scripts/market_clock_call.py", "run"],
    ["python", "scripts/update_lhb.py"],
    ["python", "scripts/update_heat.py"],
    ["python", "scripts/update_futures.py"],
    ["python", "scripts/update_repo.py"],
    ["python", "scripts/update_options.py"],
    ["python", "scripts/update_moneyflow.py"],
    ["python", "scripts/update_sina_mf.py"],
    ["python", "scripts/update_astock_daily.py"],
    ["python", "scripts/update_etf_daily.py"],
    ["python", "scripts/rev_osc_signal_export.py", "run"],
    ["python", "scripts/update_minute_feed.py"],
    ["python", "scripts/update_ths_panel.py"],
    ["python", "scripts/ah_panel_puller.py"],
    ["python", "scripts/update_fund_premium.py", "snapshot"],
    ["python", "scripts/update_fundamental.py"],
    [sys.executable, "-m", "firm.risk.b_layer_filter"],
    ["python", "-m", "live.paper"],
    ["python", "scripts/t35_open_fill_verify.py"],
    ["python", "scripts/t24_prospect_paper.py", "run"],
    ["python", "scripts/t24_prospect_promotion.py", "run"],
    ["python", "scripts/aggressive_lab.py", "paper"],
    ["python", "scripts/alloc_paper.py", "run"],
    ["python", "scripts/grid_paper.py", "run"],
    ["python", "scripts/system_v1_paper.py", "run"],
    ["python", "scripts/t35_paper_export.py", "run"],
    ["python", "scripts/daily_scorecard.py"],
    ["python", "scripts/daily_report.py", "run"],
    ["python", "scripts/ceo_live_usage.py"],
    ["python", "-m", "monitor.build_status"],
    ["python", "scripts/token_meter.py"],
]

TIMEOUT = 900
ENV_LEGS = {"python -m live.paper": {"BIGMONEY_REGIME_GUARD": "enforce"}}


def main():
    rcs = {}
    evidence = {"runner": "_r235bmc_s6_chain.py", "machine": "bm-c", "legs": {}}
    for leg in LEGS:
        name = " ".join(leg[:3])
        env = None
        for k, extra in ENV_LEGS.items():
            if name == k:
                env = dict(os.environ)
                env.update(extra)
        try:
            p = subprocess.run(leg, capture_output=True, text=True,
                               timeout=TIMEOUT, encoding="utf-8", errors="replace", env=env)
            rc, out = p.returncode, (p.stdout or "") + (p.stderr or "")
        except subprocess.TimeoutExpired:
            rc, out = 99, "TIMEOUT"
        tail = [ln.strip() for ln in out.strip().splitlines() if ln.strip()]
        snip = (tail[-1][:150] if tail else "")
        rcs[name] = rc
        evidence["legs"][name] = {"rc": rc, "tail": snip}
        print(f"{name} | rc={rc} | {snip}", flush=True)
    bad = {k: v for k, v in rcs.items() if v not in (0, 1)}
    print("---")
    print("NON-GREEN LEGS:", bad if bad else "NONE (rc0/rc1 only)")
    evidence["non_green"] = bad
    with open("results/_r235bmc_s6_chain.json", "w", encoding="utf-8") as f:
        json.dump(evidence, f, ensure_ascii=False, indent=1)
    print("evidence -> results/_r235bmc_s6_chain.json")


if __name__ == "__main__":
    main()
