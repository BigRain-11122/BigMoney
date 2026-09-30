# r504 bm-a S6 chain runner (explicit array per r495 splat-char-explode pit law)
# holiday 10-01: no new bar expected (cutoff 2026-09-30 processed r494) -> gated live.paper group legitimately skipped
import subprocess, time, sys

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
    ["python", "-m", "firm.risk.b_layer_filter"],
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

fails = []
for i, leg in enumerate(LEGS, 1):
    t0 = time.time()
    try:
        r = subprocess.run(leg, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=900)
        rc, out = r.returncode, (r.stdout or "") + (r.stderr or "")
    except subprocess.TimeoutExpired:
        rc, out = 99, "TIMEOUT 900s"
    tail = [l for l in out.strip().splitlines() if l.strip()][-2:]
    print("[%02d/%d] rc=%d %.1fs %s" % (i, len(LEGS), rc, time.time() - t0, " ".join(leg[1:])), flush=True)
    for l in tail:
        print("      | " + l[:150], flush=True)
    if rc not in (0,):
        fails.append((i, " ".join(leg), rc))

print("SUMMARY: %d legs, %d non-zero rc" % (len(LEGS), len(fails)), flush=True)
for f in fails:
    print("  NONZERO: leg%02d rc=%d %s" % (f[0], f[2], f[1]), flush=True)
sys.exit(1 if fails else 0)
