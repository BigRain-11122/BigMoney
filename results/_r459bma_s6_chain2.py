# -*- coding: utf-8 -*-
"""_r459bma_s6_chain2.py -- r459 bm-a S6 stage 2: paper chain + daily faces."""
import subprocess

LEGS = [
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

fails = []
for leg in LEGS:
    name = " ".join(leg[1:])
    try:
        p = subprocess.run(leg, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=900)
        rc, out = p.returncode, (p.stdout or "").strip().splitlines()
    except subprocess.TimeoutExpired:
        rc, out = 124, ["TIMEOUT 900s"]
    tail = out[-1][:220] if out else "(no stdout)"
    print(f"RC={rc} | {name} | {tail}", flush=True)
    if rc != 0:
        fails.append((name, rc))
print("STAGE2_FAILS:", fails if fails else "none")
