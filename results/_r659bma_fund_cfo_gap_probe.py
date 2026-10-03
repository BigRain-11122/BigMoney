import io, sys, json, os

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# --- r659 probe: FUND-line fundamental data face inventory for FFScore / cash-flow candidates
# Deterministic, zero-network, zero-engine. Facts only, no judgment.

facts = {"probe": "fund_cfo_gap_probe", "machine": "bm-a", "lane": "FUND supply piece-4/5 scouting"}

# 1) eligibility face columns + universe
elig_path = "data/fundamental/eligibility.csv"
with io.open(elig_path, encoding="utf-8") as f:
    head = f.readline().strip().split(",")
rows = 0
with io.open(elig_path, encoding="utf-8") as f:
    f.readline()
    for _ in f:
        rows += 1
facts["eligibility"] = {"columns": head, "n_rows": rows}
facts["eligibility_has_np"] = {"np_annual": "np_annual" in head, "np_interim": "np_interim" in head, "np_ttm": "np_ttm" in head}
facts["eligibility_cfo_absent"] = not any(("cfo" in c.lower()) or ("cash" in c.lower()) for c in head)

# 2) b_layer_mask columns
with io.open("data/fundamental/b_layer_mask.csv", encoding="utf-8") as f:
    bhead = f.readline().strip().split(",")
facts["b_layer_mask_columns"] = bhead

# 3) quality_faces.parquet schema (FUND-QUALITY line data face)
qpath = "data/fund_history_export/quality_faces.parquet"
qinfo = {"exists": os.path.exists(qpath), "size": os.path.getsize(qpath) if os.path.exists(qpath) else 0}
try:
    import pandas as pd
    df = pd.read_parquet(qpath)
    qinfo["columns"] = list(df.columns)
    qinfo["n_rows"] = int(len(df))
    qinfo["n_codes"] = int(df["code"].nunique()) if "code" in df.columns else None
    for c in df.columns:
        if c != "code" and df[c].dtype.kind in "fi":
            qinfo[f"col_{c}_nonnull"] = int(df[c].notna().sum())
except Exception as e:
    qinfo["error"] = repr(e)[:200]
facts["quality_faces"] = qinfo

# 4) fund_history_status
try:
    with io.open("data/fund_history_status.json", encoding="utf-8") as f:
        facts["fund_history_status"] = json.load(f)
except Exception as e:
    facts["fund_history_status_error"] = repr(e)[:200]

# 5) p1c_stock cache face keys (price engine panel only -- fundamental axes live outside)
facts["p1c_stock_cache"] = sorted(os.path.basename(p) for p in
                                  __import__("glob").glob("Money02/data/cache/p1c_stock/*.npy"))

# 6) FFScore 9-item dependency matrix vs in-repo faces (registry: Piotroski 2000 via Huatai 2017-02-09 replication claim)
ffscore_items = {
    "ROA_pos": "net profit + total assets -- assets face absent",
    "CFO_pos": "cash flow from operations -- CFO face absent",
    "dROA": "np_annual/np_interim present, total assets absent -- partial",
    "accrual": "CFO vs NI -- CFO absent",
    "d_leverage": "total liabilities/assets history -- absent",
    "d_liquidity": "current assets/liabilities history -- absent",
    "no_equity_issuance": "share-count or issuance events history -- absent",
    "d_gross_margin": "revenue + cogs history -- absent",
    "d_asset_turnover": "revenue + total assets history -- absent",
}
present_count = sum(1 for v in ffscore_items.values() if "absent" not in v)
facts["ffscore_dep_matrix"] = {"items_total": 9, "in_repo_full": present_count,
                               "partial": 1, "detail": ffscore_items}

# 7) Rob Ryan excess cash-flow rule dependency (SWHY 2015-10-19 master-series claim)
facts["cashflow_rule_dep"] = {"needs_CFO": "absent", "needs_market_cap": "eligibility face absent mkt cap; baidu probe r292 verified source (PE/PB/total mkt cap) -- collector leg not built",
                              "needs_NI": "np_ttm present in eligibility face (point snapshot; PIT history for np absent in-repo except quality_faces axes)"}

out = "results/_r659bma_fund_cfo_gap_probe_facts.json"
with io.open(out, "w", encoding="utf-8") as f:
    json.dump(facts, f, ensure_ascii=False, indent=1)
print("written:", out)
print(json.dumps({k: facts[k] for k in ("eligibility", "quality_faces", "ffscore_dep_matrix")}, ensure_ascii=False, indent=1)[:2600])
