"""r401 bm-b S6 chain runner (68th-batch law: no inline cmd /c quoting in PS).

Per-leg subprocess, rc + last stdout line captured; products to
results/_r401bmb_s6_chain.json for the round report.
New-bar conditional legs (paper/t35/prospect/promotion/aggr/alloc/
grid_paper/system_v1/export) are gated on update_daily introducing a new
panel row vs 2026-09-28 cutoff (r398 already processed the 09-28 bar).
"""
import json
import os
import subprocess
import time

LEGS = [
    ("compute_audit", ["python", "scripts/compute_audit.py"], 120),
    ("py_watermark", ["python", "scripts/py_watermark.py", "probe"], 120),
    ("update_daily", ["python", "scripts/update_daily.py"], 180),
    ("market_regime", ["python", "scripts/market_regime.py"], 120),
    ("strategy_scorecard", ["python", "scripts/strategy_scorecard.py"], 180),
    ("market_clock_call", ["python", "scripts/market_clock_call.py", "run"], 120),
    ("update_lhb", ["python", "scripts/update_lhb.py"], 120),
    ("update_heat", ["python", "scripts/update_heat.py"], 120),
    ("update_futures", ["python", "scripts/update_futures.py"], 120),
    ("update_repo", ["python", "scripts/update_repo.py"], 180),
    ("update_options", ["python", "scripts/update_options.py"], 120),
    ("update_moneyflow", ["python", "scripts/update_moneyflow.py"], 120),
    ("update_sina_mf", ["python", "scripts/update_sina_mf.py"], 120),
    ("update_astock_daily", ["python", "scripts/update_astock_daily.py"], 120),
    ("update_etf_daily", ["python", "scripts/update_etf_daily.py"], 180),
    ("rev_osc_signal_export", ["python", "scripts/rev_osc_signal_export.py", "run"], 120),
    ("update_minute_feed", ["python", "scripts/update_minute_feed.py"], 180),
    ("update_ths_panel", ["python", "scripts/update_ths_panel.py"], 120),
    ("ah_panel_puller", ["python", "scripts/ah_panel_puller.py"], 120),
    ("update_fund_premium", ["python", "scripts/update_fund_premium.py", "snapshot"], 120),
    ("update_fundamental", ["python", "scripts/update_fundamental.py"], 180),
    ("b_layer_filter", ["python", "-m", "firm.risk.b_layer_filter"], 120),
    ("daily_scorecard", ["python", "scripts/daily_scorecard.py"], 180),
    ("daily_report", ["python", "scripts/daily_report.py", "run"], 180),
    ("ceo_live_usage", ["python", "scripts/ceo_live_usage.py"], 180),
    ("build_status", ["python", "-m", "monitor.build_status"], 120),
    ("token_meter", ["python", "scripts/token_meter.py"], 120),
]

COND_LEGS = [
    ("live_paper", ["python", "-m", "live.paper"], 300),
    ("t35_open_fill", ["python", "scripts/t35_open_fill_verify.py"], 120),
    ("t24_prospect_paper", ["python", "scripts/t24_prospect_paper.py", "run"], 180),
    ("t24_prospect_promotion", ["python", "scripts/t24_prospect_promotion.py", "run"], 120),
    ("aggressive_lab_paper", ["python", "scripts/aggressive_lab.py", "paper"], 180),
    ("alloc_paper", ["python", "scripts/alloc_paper.py", "run"], 180),
    ("grid_paper", ["python", "scripts/grid_paper.py", "run"], 180),
    ("system_v1_paper", ["python", "scripts/system_v1_paper.py", "run"], 180),
    ("t35_paper_export", ["python", "scripts/t35_paper_export.py", "run"], 180),
]


def run_leg(name, cmd, timeout):
    t0 = time.time()
    try:
        env = dict(os.environ)
        if name == "live_paper":
            env["BIGMONEY_REGIME_GUARD"] = "enforce"
        r = subprocess.run(cmd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace",
                           timeout=timeout, env=env)
        tail = (r.stdout or "").strip().splitlines()
        last = tail[-1] if tail else (r.stderr or "").strip().splitlines()[-1:][:1]
        last = last[-1][:160] if isinstance(last, list) else str(last)[:160]
        return {"rc": r.returncode, "sec": round(time.time() - t0, 1),
                "last": last}
    except subprocess.TimeoutExpired:
        return {"rc": 99, "sec": round(time.time() - t0, 1),
                "last": "TIMEOUT"}
    except Exception as exc:
        return {"rc": 98, "sec": round(time.time() - t0, 1),
                "last": repr(exc)[:160]}


def main():
    out, t0 = {}, time.time()
    for name, cmd, to in LEGS:
        out[name] = run_leg(name, cmd, to)
        print(f"{name}: rc={out[name]['rc']} {out[name]['sec']}s | {out[name]['last']}")
        if name == "update_daily":
            newbar = "no new rows" not in (out[name]["last"] or "").lower() \
                and "no-op" not in (out[name]["last"] or "").lower()
            out["_newbar"] = bool(newbar)
    if out.get("_newbar"):
        for name, cmd, to in COND_LEGS:
            out[name] = run_leg(name, cmd, to)
            print(f"[newbar] {name}: rc={out[name]['rc']}")
    else:
        out["_cond_skipped"] = "no new bar (cutoff 2026-09-28 processed r398; 09-29 pre-market)"
        print("conditional legs skipped: no new bar")
    out["_meta"] = {"round": "r401 bm-b", "wall_sec": round(time.time() - t0, 1),
                    "ts": time.strftime("%Y-%m-%dT%H:%M:%S+08:00")}
    json.dump(out, open("results/_r401bmb_s6_chain.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    nonzero = {k: v["rc"] for k, v in out.items()
               if isinstance(v, dict) and v.get("rc") not in (0,)}
    print("CHAIN DONE. nonzero legs:", nonzero if nonzero else "0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
