# r963 S6 chain continuation (legs after minute_feed, resumed from killed run)
import subprocess, sys, os
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LEGS = [
    ("ths_panel", ["python", "scripts/update_ths_panel.py"]),
    ("ah_panel", ["python", "scripts/ah_panel_puller.py"]),
    ("fund_prem", ["python", "scripts/update_fund_premium.py", "snapshot"]),
    ("fundamental", ["python", "scripts/update_fundamental.py"]),
    ("b_layer", ["python", "-m", "firm.risk.b_layer_filter"]),
    ("fund_stmt", ["python", "scripts/update_fund_statements.py"]),
    ("aggr_paper", ["python", "scripts/aggressive_lab.py", "paper"]),
    ("alloc_paper", ["python", "scripts/alloc_paper.py", "run"]),
    ("grid_paper", ["python", "scripts/grid_paper.py", "run"]),
    ("sysv1_paper", ["python", "scripts/system_v1_paper.py", "run"]),
    ("t35_export", ["python", "scripts/t35_paper_export.py", "run"]),
    ("prospect_promo", ["python", "scripts/t24_prospect_promotion.py", "run"]),
    ("daily_scorecard", ["python", "scripts/daily_scorecard.py"]),
    ("daily_report", ["python", "scripts/daily_report.py", "run"]),
    ("ceo_live", ["python", "scripts/ceo_live_usage.py"]),
    ("build_status", ["python", "-m", "monitor.build_status"]),
    ("token_meter", ["python", "scripts/token_meter.py"]),
]
fails = []
for name, cmd in LEGS:
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=300)
        rc = r.returncode
        tail = (r.stdout.decode("utf-8", "replace").strip().splitlines() or [""])[-1][:110]
    except subprocess.TimeoutExpired:
        rc, tail = 99, "TIMEOUT 300s"
    print(f"[{rc}] {name}: {tail}", flush=True)
    if rc != 0:
        fails.append((name, rc, tail))
print("---- SUMMARY:", "ALL rc0" if not fails else f"{len(fails)} non-zero legs", flush=True)
for f in fails:
    print("FAIL-LEG", f, flush=True)
