"""Seat-pull first-window gate miss diagnostic (LHB_SEAT_PULL SS3,
gate measured code overlap 0.889 < 0.90 on 2026-09-11..21).

Questions (facts only, no gate change here):
  A. which in-house event codes are missing from the BUY-report window?
  B. what LHB criteria (jie-du) do those missing events carry in-house?
  C. does the SELL report (RPT_BILLBOARD_DAILYDETAILSSELL) cover them?
  D. does EM know the events at all (per-stock detail / date list)?

Read-only network + local parquet. Output: console facts (committed as
the evidence base for any prereg amendment).
"""
import json
import os
import time

import pandas as pd
import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LHB_PATH = os.path.join(ROOT, "Money02", "data", "lhb", "lhb_detail.parquet")
URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
WS, WE = "2026-09-11", "2026-09-21"


def fetch(report, extra_filter=""):
    rows, page = [], 1
    while page <= 500:
        params = {"reportName": report, "columns": "ALL",
                  "filter": f"(TRADE_DATE>='{WS}')(TRADE_DATE<'{WE}')"
                            + extra_filter,
                  "pageNumber": str(page), "pageSize": "500",
                  "sortTypes": "1", "sortColumns": "TRADE_DATE",
                  "source": "WEB", "client": "WEB"}
        r = requests.get(URL, params=params, headers={"User-Agent": UA},
                         timeout=20)
        data = (r.json().get("result") or {}).get("data")
        if not data:
            break
        rows.extend(data)
        if len(data) < 500:
            break
        page += 1
        time.sleep(0.4)
    return rows


def main():
    lhb = pd.read_parquet(LHB_PATH)
    d = pd.to_datetime(lhb["上榜日"])
    m = (d >= WS) & (d < WE)
    win = lhb[m]
    in_codes = set(win["代码"].astype(str))
    print(f"in-house window events: {len(win)} rows, {len(in_codes)} codes")

    buy = fetch("RPT_BILLBOARD_DAILYDETAILSBUY")
    buy_codes = {str(r["SECURITY_CODE"]) for r in buy}
    print(f"BUY report rows: {len(buy)}, codes: {len(buy_codes)}")
    missing = sorted(in_codes - buy_codes)
    print(f"missing from BUY: {len(missing)} -> {missing[:30]}")

    print("\nB. criteria of missing events (in-house jie-du counts):")
    mw = win[win["代码"].astype(str).isin(missing)]
    print(mw["解读"].value_counts().to_string())

    print("\nC. SELL report coverage of the missing codes:")
    sell = fetch("RPT_BILLBOARD_DAILYDETAILSSELL")
    sell_codes = {str(r["SECURITY_CODE"]) for r in sell}
    print(f"SELL report rows: {len(sell)}, codes: {len(sell_codes)}")
    cov_sell = sum(1 for c in missing if c in sell_codes)
    print(f"missing codes covered by SELL: {cov_sell}/{len(missing)}")
    union = buy_codes | sell_codes
    print(f"union BUY|SELL codes: {len(union)}, "
          f"in-house overlap: "
          f"{len(in_codes & union) / len(in_codes):.4f}")

    print("\nD. per-stock probe for up to 3 missing codes (vendor date "
          "list + detail):")
    import akshare as ak
    for code in missing[:3]:
        try:
            dd = ak.stock_lhb_stock_detail_date_em(symbol=code)
            dates = [str(x) for x in dd.iloc[:, 0].tolist()][:5]
            print(f"  {code}: EM knows appearance dates {dates}")
        except Exception as ex:
            print(f"  {code}: date-list err {type(ex).__name__} {str(ex)[:80]}")


if __name__ == "__main__":
    main()
