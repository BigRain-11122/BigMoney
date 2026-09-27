"""R381 bm-a S6 maintenance chain driver: run each leg, print rc.

Exit 0 = every leg rc==0 (or the documented no-op/ok family).
Exit 1 = any leg nonzero; the specific legs are listed on stdout.
"""
import subprocess
import sys

LEGS = [
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
    ["python", "scripts/rev_osc_signal_export.py", "run"],
    ["python", "scripts/update_ths_panel.py"],
    ["python", "scripts/ah_panel_puller.py"],
    ["python", "scripts/update_fund_premium.py", "snapshot"],
    ["python", "scripts/update_fundamental.py"],
    ["python", "-m", "firm.risk.b_layer_filter"],
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
    ["python", "-m", "monitor.build_status"],
    ["python", "scripts/token_meter.py"],
]

bad = []
for leg in LEGS:
    name = " ".join(leg[1:])
    try:
        r = subprocess.run(leg, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=900)
        rc = r.returncode
        tail = (r.stdout or "").strip().splitlines()[-1:] or [""]
        last = tail[0][:140] if tail else ""
    except Exception as ex:
        rc, last = 99, f"driver fault: {ex}"
    print(f"[rc={rc}] {name} :: {last}")
    if rc != 0:
        bad.append((name, rc))
print(f"S6 chain: {len(LEGS) - len(bad)}/{len(LEGS)} legs rc=0")
if bad:
    print("NONZERO:", bad)
    sys.exit(1)
