"""r184 bm-c S6 maintenance chain runner (36 legs, r183 same convention).

Leg order mirrors the iteration prompt S6 chain; lane-guard legs (bm-a/bm-b
host faces) run through their own honest no-op paths (stdout-only, exit 0).
Legs 23-25 (live.paper / t35_open_fill_verify / t24_prospect_paper) fire
only when a NEW bar landed today (trigger condition per prompt); the new-bar
check reads the core48 510300 panel tail after update_daily.
"""
import json
import os
import subprocess
import sys
import time

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "_r184bmc_s6_chain.json")
TODAY = time.strftime("%Y-%m-%d")

LEG_RUN = "run"


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


def has_new_bar():
    p = os.path.join(ROOT, "data", "daily", "sh510300.csv")
    if not os.path.exists(p):
        return False
    df = pd.read_csv(p)
    return str(df["date"].iloc[-1]) == TODAY if "date" in df.columns \
        else str(df.iloc[-1, 0]) == TODAY


def main():
    legs = []
    def go(name, cmd, env=None):
        legs.append(run_leg(name, cmd, env))
        print(f"{name} rc={legs[-1]['rc']} ({legs[-1]['sec']}s) "
              f":: {legs[-1]['tail'][:120]}", flush=True)

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

    nb = has_new_bar()
    print(f"new-bar check: 510300 tail=={TODAY} -> {nb}", flush=True)
    if nb:
        go("live_paper", "python -m live.paper",
           env={"BIGMONEY_REGIME_GUARD": "enforce"})
        go("t35_open_fill_verify",
           "python scripts\\t35_open_fill_verify.py")
        go("t24_prospect_paper", "python scripts\\t24_prospect_paper.py run")
    else:
        for nm in ("live_paper", "t35_open_fill_verify",
                   "t24_prospect_paper"):
            legs.append({"name": nm, "rc": 0, "sec": 0.0,
                         "tail": "skipped: no new bar (trigger law)"})
            print(f"{nm} skipped (no new bar)", flush=True)
    go("t24_prospect_promotion",
       "python scripts\\t24_prospect_promotion.py run")
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

    nonzero = [l for l in legs if l["rc"] not in (0,)]
    out = {"round": 184, "machine": "bm-c", "ts": time.strftime(
        "%Y-%m-%d %H:%M:%S"), "new_bar_today": nb, "legs": legs,
        "nonzero": len(nonzero)}
    with open(OUT + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    os.replace(OUT + ".tmp", OUT)
    print(f"chain done: {len(legs)} legs, nonzero={len(nonzero)}", flush=True)
    for l in nonzero:
        print(f"  NONZERO {l['name']} rc={l['rc']}: {l['tail'][:200]}",
              flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
