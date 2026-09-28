# r180 bm-c probe: MEMBER roster face + REPO calendar face (deterministic, zero-network)
# Prereg anchor facts only -- NOT results. G-ANCHOR-FACE quadruples verified per O-20260928-1712.
import json, glob, os
import pandas as pd

CUTOFF = "2026-09-22"  # P-5C binding caliber, same as all judged family since W-series

out = {"probe": "r180bmc_supply_prereg_probe", "cutoff": CUTOFF, "roster_face": {}, "repo_face": {}}

# ---- Face 1: member roster (in-ce roster frozen at prereg time) ----
roster = []
for f in sorted(glob.glob("firm/traders/*.json")):
    if os.path.basename(f) == "_template.json":
        continue  # template placeholder (id=TREND-001, entry=None) -- not a registered member
    d = json.load(open(f, encoding="utf-8"))
    if str(d.get("id", "")).startswith("PROS"):
        continue  # PROSPECT observation accounts are constructively excluded (O-2045 observation lane)
    roster.append({
        "id": d.get("id"), "level": d.get("level"),
        "entry": d.get("params", {}).get("entry"),
        "evidence_cutoff": d.get("evidence_cutoff"),
        "anchor_is_sharpe": d.get("backtest", {}).get("in_sample", {}).get("sharpe"),
        "anchor_oos_sharpe": d.get("backtest", {}).get("out_sample", {}).get("sharpe"),
    })
out["roster_face"]["members"] = roster
out["roster_face"]["n_members"] = len(roster)
out["roster_face"]["file_face"] = "firm/traders/*.json + json.load raw (non-PROS filter) + full-history + per-member warmup per engine face"

# ---- Face 2: repo panel calendar probe ----
terms = {}
for f in sorted(glob.glob("data/repo_daily/*.csv")):
    term = os.path.splitext(os.path.basename(f))[0]
    df = pd.read_csv(f)
    df["date"] = pd.to_datetime(df["date"])
    df = df[df["date"] <= CUTOFF].reset_index(drop=True)  # D2 lockbox truncate
    terms[term] = df
    terms.setdefault("_meta", {})
    terms["_meta"][term] = {"rows": int(len(df)), "first": str(df["date"].iloc[0].date()),
                            "last": str(df["date"].iloc[-1].date()),
                            "close_min": float(df["close"].min()), "close_max": float(df["close"].max()),
                            "close_median": float(df["close"].median())}
out["repo_face"]["panel_meta"] = terms.pop("_meta")

g1 = terms["GC001"].copy()
g7 = terms["GC007"].copy()

# trading calendar = GC001 dates (repo panel = local ETF trading calendar family per update_repo 15:30 law)
dates = g1["date"].tolist()

def month_end_mask(ds, n):
    # last n trading days of each calendar month
    m = pd.Series([d.month for d in ds])
    y = pd.Series([d.year for d in ds])
    mask = [False] * len(ds)
    for i in range(len(ds)):
        # count remaining days in same month after i
        j = i
        while j + 1 < len(ds) and y[j + 1] == y[i] and m[j + 1] == m[i]:
            j += 1
        if (j - i) < n:
            mask[i] = True
    return mask

def quarter_end_mask(ds, n):
    q = pd.Series([(d.month - 1) // 3 for d in ds])
    y = pd.Series([d.year for d in ds])
    mask = [False] * len(ds)
    for i in range(len(ds)):
        j = i
        while j + 1 < len(ds) and y[j + 1] == y[i] and q[j + 1] == q[i]:
            j += 1
        if (j - i) < n:
            mask[i] = True
    return mask

def pre_long_holiday_mask(ds, n, gap_days):
    # last n trading days before a calendar gap >= gap_days (long holiday window)
    mask = [False] * len(ds)
    idxs = []
    for i in range(len(ds) - 1):
        gap = (ds[i + 1] - ds[i]).days
        if gap >= gap_days:
            idxs.append(i)
    for i in idxs:
        for k in range(n):
            if i - k >= 0:
                mask[i - k] = True
    return mask

me2 = month_end_mask(dates, 2)
qe5 = quarter_end_mask(dates, 5)
ph2 = pre_long_holiday_mask(dates, 2, 4)

c1 = g1["close"]
stats = {}
for name, mask in [("month_end_last2", me2), ("quarter_end_last5", qe5), ("pre_longholiday_last2", ph2)]:
    m = pd.Series(mask)
    stats[name] = {
        "n_days": int(m.sum()),
        "gc001_close_mean": float(c1[m.values].mean()),
        "gc001_close_median": float(c1[m.values].median()),
        "gc001_close_p95": float(c1[m.values].quantile(0.95)),
    }
other = ~pd.Series(me2)
stats["non_monthend"] = {"n_days": int(other.sum()), "gc001_close_mean": float(c1[other.values].mean()),
                         "gc001_close_median": float(c1[other.values].median())}
out["repo_face"]["calendar_windows"] = stats

# term spread: GC007 - GC001 close on month-end window (proxy for term placement pickup)
al7 = g7.set_index("date")["close"]
al1 = g1.set_index("date")["close"]
mme = pd.Series(me2, index=g1["date"])
both = al1.index.intersection(al7.index)
sp = (al7 - al1).reindex(both)
mm7 = mme.reindex(both).values.astype(bool)
out["repo_face"]["spread_gc007_minus_gc001"] = {
    "month_end_last2_mean": float(sp[mm7].mean()),
    "non_monthend_mean": float(sp[~mm7].mean()),
    "all_median": float(sp.median()),
}

with open("results/_r180bmc_supply_prereg_probe_facts.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)
print(json.dumps(out["repo_face"]["calendar_windows"], ensure_ascii=False, indent=1))
print("spread:", json.dumps(out["repo_face"]["spread_gc007_minus_gc001"], ensure_ascii=False))
print("n_members:", out["roster_face"]["n_members"])
for r in roster:
    print("-", r["id"], r["level"], r["entry"], "IS", r["anchor_is_sharpe"], "OOS", r["anchor_oos_sharpe"])
