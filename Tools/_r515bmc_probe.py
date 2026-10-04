# -*- coding: utf-8 -*-
"""r515 bm-c HANDOVER probe: ledger head + pool judge faces count. Read-only."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

d = json.load(open(os.path.join(ROOT, "results", "mass_trial", "w3_judge.json"),
                  encoding="utf-8-sig"))
print("W3JUDGE_TOTAL", d.get("trials_ledger", {}).get("total"))

pool = json.load(open(os.path.join(ROOT, "results", "runnable_pool.json"),
                     encoding="utf-8-sig"))
entries = pool.get("entries", pool) if isinstance(pool, dict) else pool
if isinstance(entries, dict):
    entries = list(entries.values())
n2 = [e for e in entries if "N2-W15" in str(e.get("id", ""))]
print("N2_ENTRIES", len(n2), "STATES", {str(e.get("status")) for e in n2})
fund = [e for e in entries if "FUND-" in str(e.get("id", ""))]
print("FUND_ENTRIES", len(fund), "STATES",
      {str(e.get("status")) for e in fund})

# results latest receipts presence
for f in ("docs/daily_report/REPORT-2026-10-05.md",
          "docs/live_usage/LIVE-2026-10-05.md",
          "docs/trial_labor/CEO-REPORT-MASSW3-20261005.md",
          "Tools/_r514bmc_s6.py"):
    p = os.path.join(ROOT, *f.split("/"))
    print("EXISTS" if os.path.exists(p) else "MISSING", f,
          int(os.path.getmtime(p)) if os.path.exists(p) else 0)
