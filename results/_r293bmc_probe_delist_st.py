# -*- coding: utf-8 -*-
"""r293 bm-c probe: DATA_GAP#2 (listing/delisting dates + delisted stock prices)
and DATA_GAP#3 (historical daily ST status) free-source availability.
Read-only availability evidence for D-41 sec.3 materials #2/#3 (RETAIL_QUANT_TRACK.md).
NOT an acquisition start: P1 build stays GM-gated (r292 #1 precedent).
Sample symbols: 300104 LeShi (SZ delisted 2020-07), 601558 RuiDian (SH delisted 2020),
000003 PT JinTianA (SZ delisted 2002, hardest case), 600696 ST Rock (multi-rename ST case)."""
import json, time, traceback
import akshare as ak

OUT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r293bmc_probe_delist_st_sources.json"
R = {"probe": "DATA_GAP#2 delisted universe/prices + DATA_GAP#3 historical ST status free-source availability (D-41 sec.3 items 2/3)",
     "machine": "bm-c", "akshare_version": ak.__version__,
     "probed_at": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
     "evidence_cutoff": "2026-09-30",
     "faces": {}}

def face(name, fn):
    t0 = time.time()
    try:
        df = fn()
        rec = {"ok": True, "rows": int(len(df)), "sec": round(time.time() - t0, 2),
               "columns": list(df.columns)[:14]}
        # date coverage where a plausible date column exists
        for c in list(df.columns):
            if "日期" in str(c) or "date" in str(c).lower():
                try:
                    rec["cov_" + str(c)] = f"{str(df[c].min())[:10]} -> {str(df[c].max())[:10]}"
                except Exception:
                    pass
        return df, rec
    except Exception as ex:
        return None, {"ok": False, "sec": round(time.time() - t0, 2), "error": f"{type(ex).__name__}: {str(ex)[:160]}"}

# ---- A. DATA_GAP#2: delist lists + live listing dates ----
df, rec = face("sh_delist_list", lambda: ak.stock_info_sh_delist(symbol="全部"))
R["faces"]["sh_delist_list"] = rec
if df is not None and len(df):
    R["faces"]["sh_delist_list"]["sample_tail"] = df.tail(2).to_dict("records")
    # find delisting-date column range
    for c in df.columns:
        if "终止" in str(c) or "摘牌" in str(c):
            try: R["faces"]["sh_delist_list"]["delist_date_range"] = f"{str(df[c].min())[:10]} -> {str(df[c].max())[:10]}"
            except Exception: pass

df, rec = face("sz_delist_list", lambda: ak.stock_info_sz_delist(symbol="终止上市公司"))
R["faces"]["sz_delist_list"] = rec
if df is not None and len(df):
    R["faces"]["sz_delist_list"]["sample_tail"] = df.tail(2).to_dict("records")

df, rec = face("sh_live_listing_dates", lambda: ak.stock_info_sh_name_code(symbol="主板A股"))
R["faces"]["sh_live_listing_dates"] = rec
df, rec = face("sz_live_listing_dates", lambda: ak.stock_info_sz_name_code(symbol="A股列表"))
R["faces"]["sz_live_listing_dates"] = rec

# ---- B. DATA_GAP#2: delisted daily prices, 3 symbols x 3 sources ----
DELISTED = [("sz300104", "300104 乐视网 SZ 2020-07"), ("sh601558", "601558 锐电 SH 2020"), ("sz000003", "000003 PT金田A SZ 2002")]
for txs, label in DELISTED:
    for src, fn in [
        ("tx_hist", lambda s=txs: ak.stock_zh_a_hist_tx(symbol=s, adjust="")),
        ("sina_daily", lambda s=txs: ak.stock_zh_a_daily(symbol=s)),
        ("em_hist", lambda s=txs[2:]: ak.stock_zh_a_hist(symbol=s, period="daily", start_date="19900101", end_date="20260930", adjust="")),
    ]:
        k = f"delist_price_{label.split()[0]}_{src}"
        df, rec = face(k, fn)
        if df is not None and len(df):
            rec["coverage"] = f"{str(df.iloc[0, 0])[:10]} -> {str(df.iloc[-1, 0])[:10]}"
        R["faces"][k] = rec

# ---- C. DATA_GAP#3: ST current list + name-change history derive route ----
df, rec = face("st_em_current", lambda: ak.stock_zh_a_st_em())
R["faces"]["st_em_current"] = rec

for sym, label in [("600696", "600696 ST岩石 multi-rename"), ("002450", "002450 康得新 *ST->delisted"), ("000503", "000503 default sample")]:
    k = f"name_change_{sym}"
    df, rec = face(k, lambda s=sym: ak.stock_info_change_name(symbol=s))
    if df is not None and len(df):
        rec["sample_rows"] = df.head(4).to_dict("records")
    R["faces"][k] = rec

# ---- D. honest cost estimates (from observed per-call sec) ----
def sec_of(k):
    return R["faces"].get(k, {}).get("sec")

est = {}
tx_sec = sec_of("delist_price_300104_tx_hist")
sina_sec = sec_of("delist_price_300104_sina_daily")
n_delist = (R["faces"].get("sh_delist_list", {}).get("rows") or 0) + (R["faces"].get("sz_delist_list", {}).get("rows") or 0)
est["delisted_price_backfill"] = {
    "n_delisted_from_lists": n_delist,
    "per_symbol_sec_tx": tx_sec, "per_symbol_sec_sina": sina_sec,
    "estimated_wallclock": f"~{round((n_delist * max(tx_sec or 3, sina_sec or 3)) / 3600, 2)}h for {n_delist} delisted symbols (single source, network-bound)"}
nc_sec = sec_of("name_change_600696")
est["st_history_derive"] = {
    "per_symbol_sec": nc_sec,
    "universe_live_plus_delisted": f"~5,129 live + {n_delist} delisted",
    "estimated_wallclock": f"~{round(((5129 + n_delist) * (nc_sec or 2.5)) / 3600, 2)}h full-universe name-change sweep (network-bound)"}
R["cost_estimates"] = est
R["consumers"] = ["RETAIL_QUANT_TRACK.md DATA_GAP#2 survivorship-bias fix (delisted stocks must enter backtest universe with prices)",
                  "RETAIL_QUANT_TRACK.md DATA_GAP#3 second-bias fix (historical daily ST status for b_layer_mask history-true variant)",
                  "EXCLUSION-MARGINAL-P1 family (delisting/ST exclusion rules need delisted face to be honest)"]
R["gates"] = "P1 data-source expansion -- GM signature required before any acquisition build (r292 #1 precedent; probe is read-only availability evidence only)"

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(R, f, ensure_ascii=False, indent=1, default=str)
ok = sum(1 for v in R["faces"].values() if v.get("ok"))
print(f"PROBE DONE faces={len(R['faces'])} ok={ok} out={OUT}")
