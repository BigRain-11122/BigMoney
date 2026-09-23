"""Seat-level LHB data source feasibility probe v2 (P-A line continuation,
R15 pointer item 5; claim chain: MSG-20260923-1937 lane family).

v1 lessons (honest record, kept in pa_seat_source_probe.json history):
  - akshare vendor stock_lhb_stock_detail_em: (a) expects date="YYYYMMDD",
    v1 passed ISO ("2026-09-21") -> TRADE_DATE filter mangled; (b) vendor
    sends no User-Agent -> datacenter-web push2 family rate-limits this
    network (R16 update_fundamental.py diagnosed the same pattern), json
    result=None -> TypeError.
  - stock_lhb_stock_detail_sina: absent in installed akshare 1.18.96.

v2 (this run) probes:
  1. vendor retry with CORRECT YYYYMMDD date (isolates the date-format bug)
  2. DIRECT requests with browser UA to datacenter-web.eastmoney.com
     (R16-proven workaround), reportName RPT_BILLBOARD_DAILYDETAILSBUY /
     ...SELL, filter TRADE_DATE + SECURITY_CODE
Depth tested: latest in-house LHB date + 2015-06-15 (history depth).

Read-only network probe. Output: results/shortline/pa_seat_source_probe.json
(overwrites v1; v1 facts preserved in this docstring + git history).
Zero IC, zero engine runs, ledger N untouched.
"""
import json
import os
import sys
import time
import warnings

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LHB_PATH = os.path.join(ROOT, "Money02", "data", "lhb", "lhb_detail.parquet")
OUT_PATH = os.path.join(ROOT, "results", "shortline",
                        "pa_seat_source_probe.json")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

warnings.filterwarnings("ignore")


def pick_pairs(lhb: pd.DataFrame):
    pairs = []
    latest = pd.to_datetime(lhb["上榜日"]).max()
    recent = lhb[pd.to_datetime(lhb["上榜日"]) == latest]
    for _, r in recent.sort_values("龙虎榜成交额", ascending=False).head(2).iterrows():
        pairs.append({"code": str(r["代码"]),
                      "date": str(pd.Timestamp(r["上榜日"]).date()),
                      "lhb_turnover": float(r["龙虎榜成交额"]),
                      "era": "latest"})
    jun15 = lhb[pd.to_datetime(lhb["上榜日"]) == pd.Timestamp("2015-06-15")]
    if len(jun15):
        seen = set()
        for _, r in jun15.sort_values("龙虎榜成交额",
                                      ascending=False).head(2).iterrows():
            if r["代码"] not in seen:
                seen.add(r["代码"])
                pairs.append({"code": str(r["代码"]),
                              "date": str(pd.Timestamp(r["上榜日"]).date()),
                              "lhb_turnover": float(r["龙虎榜成交额"]),
                              "era": "2015-06-15"})
    else:
        pairs.append({"code": "", "date": "2015-06-15",
                      "lhb_turnover": None, "era": "2015-06-15",
                      "note": "no in-house rows that day"})
    return pairs


def probe_vendor(code, date_iso):
    t0 = time.time()
    try:
        import akshare as ak
        d8 = date_iso.replace("-", "")
        rows = {}
        for flag in ("买入", "卖出"):
            df = ak.stock_lhb_stock_detail_em(symbol=code, date=d8, flag=flag)
            rows[flag] = int(len(df))
        return {"iface": "vendor stock_lhb_stock_detail_em (YYYYMMDD)",
                "ok": True, "buy_rows": rows["买入"],
                "sell_rows": rows["卖出"],
                "elapsed_s": round(time.time() - t0, 1)}
    except Exception as ex:
        return {"iface": "vendor stock_lhb_stock_detail_em (YYYYMMDD)",
                "ok": False,
                "err": f"{type(ex).__name__}: {str(ex)[:200]}",
                "elapsed_s": round(time.time() - t0, 1)}


def probe_direct(code, date_iso):
    import requests
    t0 = time.time()
    d8 = date_iso.replace("-", "")
    url = "https://datacenter-web.eastmoney.com/api/data/v1/get"
    out = {"iface": "direct datacenter-web + browser UA", "ok": True}
    try:
        heads = {}
        for flag, report, sort_col in (
                ("buy", "RPT_BILLBOARD_DAILYDETAILSBUY", "BUY"),
                ("sell", "RPT_BILLBOARD_DAILYDETAILSSELL", "SELL")):
            params = {
                "reportName": report, "columns": "ALL",
                "filter": (f"(TRADE_DATE='{d8[:4]}-{d8[4:6]}-{d8[6:]}')"
                           f'(SECURITY_CODE="{code}")'),
                "pageNumber": "1", "pageSize": "500", "sortTypes": "-1",
                "sortColumns": sort_col, "source": "WEB", "client": "WEB",
            }
            r = requests.get(url, params=params,
                             headers={"User-Agent": UA}, timeout=20)
            j = r.json()
            data = (j.get("result") or {}).get("data")
            heads[flag] = {"n": len(data) if data else 0,
                            "http": r.status_code,
                            "head": (data or [])[:2]}
        out["buy_rows"] = heads["buy"]["n"]
        out["sell_rows"] = heads["sell"]["n"]
        out["head_buy"] = heads["buy"]["head"]
        out["ok"] = out["buy_rows"] > 0 or out["sell_rows"] > 0
        out["elapsed_s"] = round(time.time() - t0, 1)
        return out
    except Exception as ex:
        out["ok"] = False
        out["err"] = f"{type(ex).__name__}: {str(ex)[:200]}"
        out["elapsed_s"] = round(time.time() - t0, 1)
        return out


def main():
    t0 = time.time()
    lhb = pd.read_parquet(LHB_PATH)
    pairs = pick_pairs(lhb)
    print(f"probe pairs: {[(p['code'], p['date']) for p in pairs]}",
          flush=True)
    results = []
    for p in pairs:
        if not p["code"]:
            continue
        v = probe_vendor(p["code"], p["date"])
        print(f"  {p['code']}@{p['date']} vendor ok={v['ok']}", flush=True)
        d = probe_direct(p["code"], p["date"])
        print(f"  {p['code']}@{p['date']} direct ok={d['ok']} "
              f"buy={d.get('buy_rows')} sell={d.get('sell_rows')}",
              flush=True)
        results.append({"pair": p, "vendor": v, "direct": d})
    latest_direct_ok = any(r["direct"]["ok"] and r["pair"]["era"] == "latest"
                           for r in results)
    hist_direct_ok = any(r["direct"]["ok"] and r["pair"]["era"] == "2015-06-15"
                         for r in results)
    vendor_ok = any(r["vendor"]["ok"] for r in results)
    if latest_direct_ok and hist_direct_ok:
        verdict = "FEASIBLE via direct+UA (recent + 2015 history served)"
    elif latest_direct_ok:
        verdict = ("PARTIAL (recent served, 2015 history NOT served -> "
                   "seat factor era truncated)")
    else:
        verdict = "INFEASIBLE (vendor no-UA rate-limited AND direct failed)"
    out = {"meta": {"probe": "seat-level LHB source feasibility v2",
                    "v1_lessons": "vendor expects YYYYMMDD (v1 passed ISO) "
                                  "+ no-UA rate limit (R16 pattern); "
                                  "stock_lhb_stock_detail_sina absent in "
                                  "akshare 1.18.96",
                    "lane": "P-A pointer item 5 (revive lhb_seat_top5_conc)",
                    "claim_family": "MSG-20260923-1937",
                    "date": time.strftime("%Y-%m-%d %H:%M"),
                    "akshare_version": "1.18.96",
                    "ledger_note": "read-only source probe: N untouched, "
                                   "zero engine runs, zero IC"},
           "pairs": results,
           "vendor_with_correct_date_ok": vendor_ok,
           "verdict": verdict,
           "implication": ("FEASIBLE -> separate historical-pull data-source "
                           "batch (write-domain its own; Money02/lhb_download"
                           ".py precedent; direct+UA or vendor-with-YYYYMMDD"
                           " per this probe); seat factor batch only AFTER "
                           "data lands + preregistration"),
           "audit": {"elapsed_sec": round(time.time() - t0, 1)}}
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False, default=str)
    print(f"verdict: {verdict} (vendor_ok={vendor_ok}) "
          f"({time.time()-t0:.0f}s)", flush=True)
    print(f"saved: {OUT_PATH}", flush=True)


if __name__ == "__main__":
    sys.exit(main())
