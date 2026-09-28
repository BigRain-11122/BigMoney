"""r200 bm-c S6 maintenance chain runner (37 legs, r189/r199 convention).

Leg order mirrors the iteration prompt S6 chain; pool_dualrun_reconcile runs
FIRST (settle-heals-vacuity law, r196 wiring); lane-guard legs run through
their own honest no-op paths. Bar-pending legs are idempotent re-derivations
(r199 precedent: full run at panel cutoff -> no-op); REGIME_GUARD enforce is
set for live.paper per prompt (date gate 10-01 not yet open = honest shadow
degrade, zero behavior change).
"""
import json
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "_r200bmc_s6_chain.json")


def run_leg(name, cmd, env=None, timeout=900):
    t0 = time.time()
    try:
        e = dict(os.environ)
        if env:
            e.update(env)
        p = subprocess.run(cmd, cwd=ROOT, env=e, capture_output=True,
                           text=True, timeout=timeout, shell=True)
        rc = p.returncode
        tail = (p.stdout or "").strip().splitlines()
        last = tail[-1] if tail else (p.stderr or "").strip()[-200:]
    except subprocess.TimeoutExpired:
        rc, last = 124, "TIMEOUT"
    return {"name": name, "rc": rc, "sec": round(time.time() - t0, 1),
            "tail": str(last)[:300]}


def main():
    legs = []

    def go(name, cmd, env=None):
        legs.append(run_leg(name, cmd, env))
        print(f"{name} rc={legs[-1]['rc']} ({legs[-1]['sec']}s) "
              f":: {legs[-1]['tail'][:120]}", flush=True)

    rg = {"BIGMONEY_REGIME_GUARD": "enforce"}
    go("pool_dualrun_reconcile", "python scripts\\pool_dualrun_reconcile.py run")
    go("compute_audit", "python scripts\\compute_audit.py")
    go("py_watermark_probe", "python scripts\\py_watermark.py probe")
    go("update_daily", "python scripts\\update_daily.py")
    go("market_regime", "python scripts\\market_regime.py")
    go("strategy_scorecard", "python scripts\\strategy_scorecard.py")
    go("market_clock_call", "python scripts\\market_clock_call.py run")
    go("update_lhb", "python scripts\\update_lhb.py")
    go("update_heat", "python scripts\\update_heat.py")
    go("update_futures", "python scripts\\update_futures.py")
    go("update_repo", "python scripts\\update_repo.py")
    go("update_options", "python scripts\\update_options.py")
    go("update_moneyflow", "python scripts\\update_moneyflow.py")
    go("update_sina_mf", "python scripts\\update_sina_mf.py")
    go("update_astock_daily", "python scripts\\update_astock_daily.py")
    go("update_etf_daily", "python scripts\\update_etf_daily.py")
    go("rev_osc_signal_export", "python scripts\\rev_osc_signal_export.py run")
    go("update_minute_feed", "python scripts\\update_minute_feed.py")
    go("update_ths_panel", "python scripts\\update_ths_panel.py")
    go("ah_panel_puller", "python scripts\\ah_panel_puller.py")
    go("update_fund_premium", "python scripts\\update_fund_premium.py snapshot")
    go("update_fundamental", "python scripts\\update_fundamental.py")
    go("b_layer_filter", "python -m firm.risk.b_layer_filter")
    go("live_paper", "python -m live.paper", env=rg)
    go("t35_open_fill_verify", "python scripts\\t35_open_fill_verify.py")
    go("t24_prospect_paper", "python scripts\\t24_prospect_paper.py run")
    go("t24_prospect_promotion", "python scripts\\t24_prospect_promotion.py run")
    go("aggressive_lab_paper", "python scripts\\aggressive_lab.py paper")
    go("alloc_paper", "python scripts\\alloc_paper.py run")
    go("grid_paper", "python scripts\\grid_paper.py run")
    go("system_v1_paper", "python scripts\\system_v1_paper.py run")
    go("t35_paper_export", "python scripts\\t35_paper_export.py run")
    go("daily_scorecard", "python scripts\\daily_scorecard.py")
    go("daily_report", "python scripts\\daily_report.py run")
    go("ceo_live_usage", "python scripts\\ceo_live_usage.py")
    go("monitor_build_status", "python -m monitor.build_status")
    go("token_meter", "python scripts\\token_meter.py")

    doc = {"round": "r200", "machine": "bm-c",
           "ts": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
           "legs": legs, "nonzero_count": sum(1 for x in legs if x["rc"] != 0)}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    print(f"chain done: nonzero={doc['nonzero_count']} -> {OUT}", flush=True)


if __name__ == "__main__":
    main()
