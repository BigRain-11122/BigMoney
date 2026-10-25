# -*- coding: utf-8 -*-
"""r1237 bm-c S6 chain driver: ordered legs, rc + tail-line collection.
Lane-guarded legs self-report honest no-ops on non-host machines (R31)."""
import subprocess, sys, os, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
CREAT = 0x08000000

CHAIN = [
    ("pool_dualrun_reconcile", [PY, os.path.join(ROOT, "scripts", "pool_dualrun_reconcile.py"), "run"]),
    ("compute_audit", [PY, os.path.join(ROOT, "scripts", "compute_audit.py")]),
    ("py_watermark", [PY, os.path.join(ROOT, "scripts", "py_watermark.py"), "probe"]),
    ("update_daily", [PY, os.path.join(ROOT, "scripts", "update_daily.py")]),
    ("market_regime", [PY, os.path.join(ROOT, "scripts", "market_regime.py")]),
    ("market_clock_call", [PY, os.path.join(ROOT, "scripts", "market_clock_call.py"), "run"]),
    ("update_lhb", [PY, os.path.join(ROOT, "scripts", "update_lhb.py")]),
    ("update_zt_pool", [PY, os.path.join(ROOT, "scripts", "update_zt_pool.py")]),
    ("update_heat", [PY, os.path.join(ROOT, "scripts", "update_heat.py")]),
    ("update_futures", [PY, os.path.join(ROOT, "scripts", "update_futures.py")]),
    ("update_repo", [PY, os.path.join(ROOT, "scripts", "update_repo.py")]),
    ("update_options", [PY, os.path.join(ROOT, "scripts", "update_options.py")]),
    ("update_moneyflow", [PY, os.path.join(ROOT, "scripts", "update_moneyflow.py")]),
    ("update_sina_mf", [PY, os.path.join(ROOT, "scripts", "update_sina_mf.py")]),
    ("update_astock_daily", [PY, os.path.join(ROOT, "scripts", "update_astock_daily.py")]),
    ("update_etf_daily", [PY, os.path.join(ROOT, "scripts", "update_etf_daily.py")]),
    ("regime_thermo_build", [PY, os.path.join(ROOT, "scripts", "regime_thermo_build.py")]),
    ("regime_gate_dualarm", [PY, os.path.join(ROOT, "scripts", "regime_gate_dualarm.py"), "run"]),
    ("rev_osc_signal_export", [PY, os.path.join(ROOT, "scripts", "rev_osc_signal_export.py"), "run"]),
    ("update_minute_feed", [PY, os.path.join(ROOT, "scripts", "update_minute_feed.py")]),
    ("update_ths_panel", [PY, os.path.join(ROOT, "scripts", "update_ths_panel.py")]),
    ("ah_panel_puller", [PY, os.path.join(ROOT, "scripts", "ah_panel_puller.py")]),
    ("update_fund_premium", [PY, os.path.join(ROOT, "scripts", "update_fund_premium.py"), "snapshot"]),
    ("update_fundamental", [PY, os.path.join(ROOT, "scripts", "update_fundamental.py")]),
    ("b_layer_filter", [PY, "-m", "firm.risk.b_layer_filter"]),
    ("update_fund_statements", [PY, os.path.join(ROOT, "scripts", "update_fund_statements.py")]),
    ("t24_prospect_paper", [PY, os.path.join(ROOT, "scripts", "t24_prospect_paper.py"), "run"]),
    ("t24_prospect_promotion", [PY, os.path.join(ROOT, "scripts", "t24_prospect_promotion.py"), "run"]),
    ("aggressive_lab", [PY, os.path.join(ROOT, "scripts", "aggressive_lab.py"), "paper"]),
    ("alloc_paper", [PY, os.path.join(ROOT, "scripts", "alloc_paper.py"), "run"]),
    ("grid_paper", [PY, os.path.join(ROOT, "scripts", "grid_paper.py"), "run"]),
    ("system_v1_paper", [PY, os.path.join(ROOT, "scripts", "system_v1_paper.py"), "run"]),
    ("t35_paper_export", [PY, os.path.join(ROOT, "scripts", "t35_paper_export.py"), "run"]),
    ("daily_scorecard", [PY, os.path.join(ROOT, "scripts", "daily_scorecard.py")]),
    ("daily_report", [PY, os.path.join(ROOT, "scripts", "daily_report.py"), "run"]),
    ("ceo_live_usage", [PY, os.path.join(ROOT, "scripts", "ceo_live_usage.py")]),
    ("token_meter", [PY, os.path.join(ROOT, "scripts", "token_meter.py")]),
    ("strategy_scorecard", [PY, os.path.join(ROOT, "scripts", "strategy_scorecard.py")]),
    ("build_status", [PY, "-m", "monitor.build_status"]),
]

results = []
for name, cmd in CHAIN:
    try:
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=900,
                           creationflags=CREAT)
        rc = r.returncode
        tail = (r.stdout or "").strip().splitlines()
        last = tail[-1][:150] if tail else ""
        if rc != 0:
            err = (r.stderr or "").strip().splitlines()
            last = (tail[-2:] + err[-2:])
            last = " || ".join(x[:150] for x in last) if last else ""
    except subprocess.TimeoutExpired:
        rc, last = -9, "TIMEOUT 900s"
    results.append((name, rc, last))
    print(f"{name}: rc={rc} {'(ok)' if rc == 0 else ''} {last[:170] if rc != 0 else ''}", flush=True)

bad = [r for r in results if r[1] != 0]
json.dump([{"leg": n, "rc": rc, "tail": t} for n, rc, t in results],
          open(os.path.join(ROOT, "results", "_r1238bmc_s6_chain.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(f"\nS6 chain: {len(results) - len(bad)}/{len(results)} rc0; non-zero: {[(b[0], b[1]) for b in bad] or 'NONE'}", flush=True)