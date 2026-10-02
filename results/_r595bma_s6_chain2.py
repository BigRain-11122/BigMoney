# -*- coding: utf-8 -*-
"""r592 bm-a S6 chain part 2: paper lane + panels + token + attrition guard."""
import subprocess, sys

LEGS = [
    ("live.paper", [sys.executable, "-m", "live.paper"]),
    ("t35_open_fill_verify", [sys.executable, "scripts/t35_open_fill_verify.py"]),
    ("t24_prospect_paper", [sys.executable, "scripts/t24_prospect_paper.py", "run"]),
    ("t24_prospect_promotion", [sys.executable, "scripts/t24_prospect_promotion.py", "run"]),
    ("aggressive_lab", [sys.executable, "scripts/aggressive_lab.py", "paper"]),
    ("alloc_paper", [sys.executable, "scripts/alloc_paper.py", "run"]),
    ("grid_paper", [sys.executable, "scripts/grid_paper.py", "run"]),
    ("system_v1_paper(bm-a lane)", [sys.executable, "scripts/system_v1_paper.py", "run"]),
    ("t35_paper_export", [sys.executable, "scripts/t35_paper_export.py", "run"]),
    ("daily_scorecard(host bm-a)", [sys.executable, "scripts/daily_scorecard.py"]),
    ("daily_report", [sys.executable, "scripts/daily_report.py", "run"]),
    ("ceo_live_usage", [sys.executable, "scripts/ceo_live_usage.py"]),
    ("build_status(host bm-a)", [sys.executable, "-m", "monitor.build_status"]),
    ("token_meter", [sys.executable, "scripts/token_meter.py"]),
    ("attrition_ledger_guard", [sys.executable, "scripts/attrition_ledger_guard.py", "scan"]),
]

for name, cmd in LEGS:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           creationflags=0x08000000, timeout=900)
        tail = (r.stdout or "").strip().splitlines()
        last = tail[-1][:110] if tail else (r.stderr or "").strip()[-110:]
        print(f"{name} | rc={r.returncode} | {last}")
    except Exception as e:
        print(f"{name} | EXC | {e}")
