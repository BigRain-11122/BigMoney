"""R295 bm-a probe: FUSION_GRID_P1 (T-85 s2/s3) design facts -- MEMBER/REGIME faces only.

ZERo judged-cell values computed here (no cell NAV, no cell Sharpe) -- freeze-first law.
Facts frozen into prereg sec.2:
  F1 member census + NAV grid alignment (from s1 frozen product, sha-pinned manifest)
  F2 x1 full-history pairwise corr census + static dedup cluster count (0.95 single-linkage)
  F3 trailing-252 selection warmup boundary
  F4 v3 regime state series recompute shares over NAV window (state known at t-1)
  F5 x2 stress face presence (parallel lane availability)
"""
import json
import numpy as np
import pandas as pd

OUT = "results/fusion_grid_probe.json"
NAV = "results/fusion_p1/navs.jsonl"

lines = [json.loads(l) for l in open(NAV, encoding="utf-8")]
x1 = [l for l in lines if l["cost_face"] == "x1"]
x2c = [l for l in lines if l["cost_face"] == "x2"]
assert len(x1) == 32 and len(x2c) == 32, (len(x1), len(x2c))

base = [l for l in x1 if ":" not in l["member"]]
ovly = [l for l in x1 if ":" in l["member"]]
dates = base[0]["dates"]
for l in base:
    assert l["dates"] == dates, l["member"]
for l in ovly:
    # overlay lines self-declare a later basis (r251) -- common-grid truncation face
    assert l["dates"][:len(dates)] == dates, l["member"]
    l["dates"] = l["dates"][:len(dates)]
    l["eq"] = l["eq"][:len(dates)]
for l in x2c:
    l["dates"] = l["dates"][:len(dates)]
    l["eq"] = l["eq"][:len(dates)]
R = np.array([l["eq"] for l in x1], dtype=float)          # 32 x T NAV levels (common grid)
T = R.shape[1]
rets = R[:, 1:] / R[:, :-1] - 1.0                          # 32 x (T-1) daily returns
members = [l["member"] for l in x1]
sharpe = {l["member"]: l["sharpe_full"] for l in x1}

# F2 pairwise corr census (full-history x1)
C = np.corrcoef(rets)
iu = np.triu_indices(32, k=1)
pv = C[iu]
order = np.argsort(-pv)
pairs_ge_95 = int((pv >= 0.95).sum())
pairs_ge_70 = int((pv >= 0.70).sum())

# static dedup: single-linkage at |corr|>=0.95 on full-history, rep = higher sharpe_full
parent = list(range(32))
def find(a):
    while parent[a] != a:
        parent[a] = parent[parent[a]]
        a = parent[a]
    return a
for a, b in zip(*iu):
    if abs(C[a, b]) >= 0.95:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
clusters = {}
for i in range(32):
    clusters.setdefault(find(i), []).append(i)
dedup_pool = []
for root, idxs in clusters.items():
    best = max(idxs, key=lambda i: (sharpe[members[i]], -i))
    dedup_pool.append(members[best])
dedup_pool.sort()
multi_clusters = {members[i]: [members[j] for j in idxs] for root, idxs in clusters.items() if len(idxs) > 1 for i in [idxs[0]]}

# F4 regime recompute over NAV window (v3 machine, state known at t-1)
import sys
sys.path.insert(0, "scripts")
import market_regime as mr
bench = mr.load_bench()  # 510300 close series
bd_all = mr.bench_dims(bench)
br_all = mr.breadth_dims(bench)
# daily state series via v3 raw + resolve, aligned to bench index
states = {}
prev, streak = "GREEN", 0
bear = False
for d in bench.index:
    bd = {k: (v.loc[d] if hasattr(v, "loc") else v) for k, v in bd_all.items() if not (hasattr(v, "loc") and d not in v.index)}
    raw = mr.raw_level_v3(bd_all, br_all, bear) if False else None
    break
# NOTE: bd_all entries are scalars-at-end in this module (probe() runs on last date);
# full-history recompute requires per-date recompute -- do it directly:
from config import PATHS
p510 = pd.read_csv(f"{PATHS.daily_dir}/510300.csv")
p510.columns = [c.strip() for c in p510.columns]
dtcol = "date" if "date" in p510.columns else p510.columns[0]
p510[dtcol] = p510[dtcol].astype(str).str.slice(0, 10)
close = pd.Series(p510["close"].values, index=pd.to_datetime(p510[dtcol]))
core_files = [f for f in __import__("os").listdir(PATHS.daily_dir)
              if f.endswith(".csv") and not f.startswith(("511", "510", "159", "512", "518"))]
# breadth = share of core48 below MA20 -> use the 48 ETF closes
import glob, os
etf_files = sorted(glob.glob(f"{PATHS.daily_dir}/*.csv"))
panel = {}
for f in etf_files:
    code = os.path.basename(f)[:-4]
    if code in ("511880", "511010"):
        continue  # cash/money-market legs excluded from breadth face
    df = pd.read_csv(f)
    df.columns = [c.strip() for c in df.columns]
    dc = "date" if "date" in df.columns else df.columns[0]
    df[dc] = df[dc].astype(str).str.slice(0, 10)
    s = pd.Series(df["close"].values, index=pd.to_datetime(df[dc]))
    panel[code] = s
P = pd.DataFrame(panel).sort_index().ffill()
nav_idx = pd.to_datetime(dates)
Pw = P.reindex(nav_idx).ffill()
cl = close.reindex(nav_idx).ffill()
ma20 = Pw.rolling(20, min_periods=20).mean()
below = (Pw < ma20).sum(axis=1) / Pw.notna().sum(axis=1)
ma200 = cl.rolling(200, min_periods=200).mean()
r1 = cl.pct_change()
r10 = cl.pct_change(10)
rv20 = r1.rolling(20).std() * np.sqrt(252)
rv_p95 = rv20.rolling(756, min_periods=252).quantile(0.95)
rv_p80 = rv20.rolling(756, min_periods=252).quantile(0.80)

state_ser = []
prev, streak = "GREEN", 0
for i, d in enumerate(nav_idx):
    raw = "GREEN"
    if r10.loc[d] <= -0.12 or r1.loc[d] <= -0.05:
        raw = "RED"
    else:
        if r10.loc[d] <= -0.08:
            raw = "ORANGE"
        if pd.notna(rv_p95.loc[d]) and rv20.loc[d] > rv_p95.loc[d] and raw != "ORANGE":
            raw = "ORANGE"
        if below.loc[d] >= 0.80 and raw != "ORANGE":
            raw = "ORANGE"
        if pd.notna(ma200.loc[d]) and cl.loc[d] < ma200.loc[d] and raw != "ORANGE":
            raw = "ORANGE"
        if raw == "GREEN":
            if r10.loc[d] <= -0.05:
                raw = "YELLOW"
            if pd.notna(rv_p80.loc[d]) and rv20.loc[d] > rv_p80.loc[d] and raw != "YELLOW":
                raw = "YELLOW"
            if below.loc[d] >= 0.65 and raw != "YELLOW":
                raw = "YELLOW"
    prev, streak = mr.resolve_state_v3(prev, streak, raw)
    state_ser.append(prev)
state_counts = pd.Series(state_ser).value_counts().to_dict()

probe = {
    "batch": "FUSION_GRID_P1",
    "ticket_ref": "T-2026-09-26-85 s2/s3 (O-20260926-2320)",
    "evidence_cutoff": "2026-09-22",
    "cutoff_note": "per-member frozen caliber pin (s1 navs exclude post-09-22 bars); panel 2026-09-24 availability disclosed",
    "F1_members": {
        "n_members": 32, "families": {"CE6": 6, "PROSPECT": 22, "OVERLAY_WIRED": 4},
        "bars": T, "date_first": dates[0], "date_last": dates[-1],
        "x1_lines": len(x1), "x2_lines": len(x2c),
        "member_list": members,
        "common_grid_note": "overlay-wired faces self-declare basis to 2026-09-24 (r251); common grid = 28 base members 2020-01-02..2026-09-22 (1631 bars); overlay lines truncated to common grid (extra 2 bars dropped, disclosed)",
    },
    "F2_corr_census_x1_full": {
        "median_pair_corr": round(float(np.median(pv)), 4),
        "p95_pair_corr": round(float(np.percentile(pv, 95)), 4),
        "max_pair_corr": round(float(pv.max()), 4),
        "min_pair_corr": round(float(pv.min()), 4),
        "pairs_ge_0.95": pairs_ge_95, "pairs_ge_0.70": pairs_ge_70, "n_pairs": int(pv.size),
        "top5_pairs": [
            {"a": members[a], "b": members[b], "corr": round(float(C[a, b]), 4)}
            for a, b in zip(iu[0][order[:5]], iu[1][order[:5]])
        ],
        "static_dedup_clusters_n": len(clusters),
        "static_dedup_pool": dedup_pool,
        "collapsed_multi_clusters": [
            {"rep": members[idxs[0]], "members": [members[j] for j in idxs]}
            for root, idxs in sorted(clusters.items(), key=lambda kv: -len(kv[1])) if len(idxs) > 1
        ],
    },
    "F3_warmup": {
        "lookback_bars": 252, "rebalance_every": 21,
        "first_rebalance_bar": 252, "cell_window_bars": T - 252,
        "cell_window_first_date": dates[252], "cell_window_last_date": dates[-1],
    },
    "F4_regime_v3_recompute": {
        "rule": "market_regime.py v3 thresholds verbatim (RED crash/panic; ORANGE 10d<=-8%|rv20>p95|breadth>=0.80|510300<MA200; YELLOW 10d<=-5%|rv20>p80|breadth>=0.65; hysteresis 2-GREEN)",
        "state_counts": {k: int(v) for k, v in state_counts.items()},
        "n_days": len(state_ser),
        "cap_ladder_frozen": {"GREEN": 0.80, "YELLOW": 0.65, "ORANGE": 0.50, "RED": 0.20},
        "yellow_note": "YELLOW 0.65 = engineering-frozen interpolation (L5 canon has RED20/ORANGE50/GREEN80 only), disclosed non-canon param",
    },
    "F5_x2_stress": {"x2_lines_present": len(x2c), "members": [l["member"] for l in x2c][:5]},
}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(probe, f, ensure_ascii=False, indent=1)
print(json.dumps(probe, ensure_ascii=False, indent=1)[:2600])
