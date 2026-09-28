# r404 bm-a S6 maintenance chain runner (r183/r184 chain-runner law:
# NEVER wrap multi-leg command chains in PowerShell cmd /c quotes -- all
# legs run via subprocess with rc + tail captured, JSON product to
# results/ for the round report). Time-boxed per leg (120s); a timeout
# is recorded honestly and the chain moves on (no masking).
import json, subprocess, sys, time, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
LEGS = [
    ("compute_audit", [PY, "scripts/compute_audit.py"], 240),
    ("py_watermark_probe", [PY, "scripts/py_watermark.py", "probe"], 180),
    ("update_daily", [PY, "scripts/update_daily.py"], 240),
    ("market_regime", [PY, "scripts/market_regime.py"], 180),
    ("strategy_scorecard", [PY, "scripts/strategy_scorecard.py"], 240),
    ("market_clock_call", [PY, "scripts/market_clock_call.py", "run"], 180),
    ("update_lhb", [PY, "scripts/update_lhb.py"], 120),
    ("update_heat", [PY, "scripts/update_heat.py"], 120),
    ("update_futures", [PY, "scripts/update_futures.py"], 120),
    ("update_repo", [PY, "scripts/update_repo.py"], 240),
    ("update_options", [PY, "scripts/update_options.py"], 120),
    ("update_moneyflow", [PY, "scripts/update_moneyflow.py"], 120),
    ("update_sina_mf", [PY, "scripts/update_sina_mf.py"], 120),
    ("update_astock_daily", [PY, "scripts/update_astock_daily.py"], 120),
    ("update_etf_daily", [PY, "scripts/update_etf_daily.py"], 120),
    ("rev_osc_signal_export", [PY, "scripts/rev_osc_signal_export.py", "run"], 120),
    ("update_minute_feed", [PY, "scripts/update_minute_feed.py"], 120),
    ("update_ths_panel", [PY, "scripts/update_ths_panel.py"], 120),
    ("ah_panel_puller", [PY, "scripts/ah_panel_puller.py"], 120),
    ("update_fund_premium", [PY, "scripts/update_fund_premium.py", "snapshot"], 120),
    ("update_fundamental", [PY, "scripts/update_fundamental.py"], 180),
    ("b_layer_filter", [PY, "-m", "firm.risk.b_layer_filter"], 120),
    ("live_paper", [PY, "-m", "live.paper"], 240),
    ("t35_open_fill_verify", [PY, "scripts/t35_open_fill_verify.py"], 180),
    ("t24_prospect_paper", [PY, "scripts/t24_prospect_paper.py", "run"], 240),
    ("t24_prospect_promotion", [PY, "scripts/t24_prospect_promotion.py", "run"], 180),
    ("aggressive_lab_paper", [PY, "scripts/aggressive_lab.py", "paper"], 240),
    ("alloc_paper", [PY, "scripts/alloc_paper.py", "run"], 180),
    ("grid_paper", [PY, "scripts/grid_paper.py", "run"], 180),
    ("system_v1_paper", [PY, "scripts/system_v1_paper.py", "run"], 240),
    ("t35_paper_export", [PY, "scripts/t35_paper_export.py", "run"], 180),
    ("daily_scorecard", [PY, "scripts/daily_scorecard.py"], 240),
    ("daily_report", [PY, "scripts/daily_report.py", "run"], 240),
    ("ceo_live_usage", [PY, "scripts/ceo_live_usage.py"], 180),
    ("build_status", [PY, "-m", "monitor.build_status"], 180),
    ("token_meter", [PY, "scripts/token_meter.py"], 120),
]

def main():
    env = dict(os.environ)
    # REGIME_GUARD v3: date gate not yet open (2026-10-01) -> honest
    # shadow downgrade handled inside live.paper itself; set nothing.
    out = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "legs": []}
    for name, cmd, tmo in LEGS:
        t0 = time.time()
        try:
            r = subprocess.run(cmd, cwd=ROOT, capture_output=True,
                               timeout=tmo, env=env)
            rc = r.returncode
            tail = (r.stdout or b"").decode(errors="replace").strip()
            if not tail:
                tail = (r.stderr or b"").decode(errors="replace").strip()
            tl = tail.splitlines()[-1][:220] if tail else "(no output)"
        except subprocess.TimeoutExpired:
            rc, tl = "TIMEOUT", f"> {tmo}s, chain moved on (honest)"
        except Exception as ex:
            rc, tl = "FAULT", str(ex)[:220]
        row = {"leg": name, "rc": rc, "sec": round(time.time() - t0, 1),
               "tail": tl}
        out["legs"].append(row)
        flag = "" if rc == 0 else "  <== NONZERO"
        print(f"{name:24s} rc={rc} {row['sec']:>6}s  {tl[:150]}{flag}",
              flush=True)
        if rc not in (0, "TIMEOUT") and rc != 2:
            pass  # rc=2 (source-fault contract) surfaces in the report verbatim
    out["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
    nz = [l["leg"] for l in out["legs"] if l["rc"] not in (0,)]
    out["nonzero_legs"] = nz
    p = os.path.join(ROOT, "results", "_r404bma_s6_chain.json")
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(f"CHAIN DONE nonzero={nz} -> {p}", flush=True)

if __name__ == "__main__":
    main()
