"""LOWAMP-P1 s1 prereg probe (read-only anchors, bm-b r483). No simulation, no burn."""
import json, os, sys
repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, repo)
out = {}
# 1. legacy core48 face via canonical loader
from live.paper import load_core, build_panels
prices = load_core()
out["legacy_members"] = sorted(prices.keys())
out["legacy_n"] = len(prices)
c = prices["510300"]
out["legacy_510300_rows"] = int(len(c))
out["legacy_510300_start"] = str(c["date"].iloc[0]) if "date" in c.columns else str(c.index[0].date())
try:
    out["legacy_510300_end"] = str(c["date"].iloc[-1])
except Exception:
    out["legacy_510300_end"] = str(c.index[-1].date())
out["legacy_510300_cols"] = list(c.columns)[:10] if "date" in c.columns else "index=date"
# amount face availability
import pandas as pd
has_amt = {}
for k, df in prices.items():
    has_amt[k] = "amount" in df.columns
out["legacy_amount_col_members"] = int(sum(has_amt.values()))
# amt20 median distribution (liquidity floor anchor)
P = build_panels(prices)
close = P["close"]
amt = P.get("amount")
if amt is not None:
    med20 = amt.rolling(20, min_periods=20).median()
    last_med = med20.iloc[-1]
    out["amt20_last_min_mkrmb"] = round(float(last_med.min()) / 1e8, 3)
    out["amt20_last_p10_mkrmb"] = round(float(last_med.quantile(0.10)) / 1e8, 3)
    out["amt20_last_median_mkrmb"] = round(float(last_med.median()) / 1e8, 3)
    out["amt20_min_member"] = str(last_med.idxmin())
# cutoff truncation fact
out["legacy_close_last"] = str(close.index[-1].date())
# 2. adjusted view 19/19
adj_dir = os.path.join(repo, "data", "consolidation", "adjusted_view")
adj = sorted(f[:-8] for f in os.listdir(adj_dir) if f.endswith(".parquet"))
out["adjusted_view_n"] = len(adj)
out["adjusted_view_members_subset_of_legacy"] = all(a in prices for a in adj)
# 3. deep manifest
man = json.load(open(os.path.join(repo, "results", "shortline", "t18_deep_manifest.json"), encoding="utf-8"))
out["deep_manifest_verdict"] = man.get("verdict")
out["deep_panel_start"] = man.get("panel_start")
out["deep_evidence_cutoff"] = man.get("evidence_cutoff")
out["deep_members_n"] = len(man.get("members", {}))
deep_dir = os.path.join(repo, "Money02", "data", "cache", "t18_deep_panel", "ohlcv")
out["deep_ohlcv_files"] = len([f for f in os.listdir(deep_dir) if f.endswith(".parquet")]) if os.path.isdir(deep_dir) else 0
# 4. T-22 frozen start sets (census face)
t22_dir = os.path.join(repo, "results", "shortline", "t22_virtual_timepoints")
cands = []
if os.path.isdir(t22_dir):
    for root, dirs, files in os.walk(t22_dir):
        for f in files:
            if "finalize" in f or "starts" in f or "census" in f:
                cands.append(os.path.join(root, f))
out["t22_finalize_candidates"] = [os.path.relpath(p, repo) for p in cands[:10]]
print(json.dumps(out, ensure_ascii=False, indent=1, default=str))
