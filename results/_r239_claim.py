# -*- coding: utf-8 -*-
"""R239: claim T-74/T-75/T-77 (CEO immediate tickets, same-round claim per O-1730).
JSON rewrite with producer format (indent=1, ensure_ascii=False) -- format-probe first (R230 law)."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLAIM = "bm-a (OS iteration loop, round 239; CEO immediate ticket per O-20260926-0932/0940/0947 -- claim-and-start same round per O-1730; C-arm T-70/T-73 batch runs in parallel on separate faces)"
NOW = "2026-09-26 09:47"

progress = {
    "T-74": "r239: s0 canon+prereg freeze (research/MARKET_CLOCK_COMBO.md) + s1 current-market-call one-pager delivered same round; s2 full-history backtest = next slice (pool batch, O-1137 carrier), s3 results report follows",
    "T-75": "r239: firm/DECISIONS.md canon + scripts/daily_report.py v1 + today first report + selftest; wiring (15:45 scheduled) = next slice",
    "T-77": "r239: LOCAL_FIRST.md v2 routing table + token line lands inside T-75 daily report (slice d synergy); crash-fuse extension + L2 consumption extension + GPU factor lane first batch = next slices with continuation notes",
}

for tid in ("74", "75", "77"):
    p = os.path.join(ROOT, "fleet", "tasks", f"T-2026-09-26-{tid}-P1.json")
    with open(p, encoding="utf-8") as f:
        d = json.load(f)
    assert d["status"] == "open", f"{tid} not open: {d['status']}"
    d["status"] = "claimed"
    d["claimed_by"] = CLAIM
    d["claimed_at"] = NOW
    d["progress_r239"] = progress[f"T-{tid}"]
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"T-{tid} claimed")
print("claims done")
