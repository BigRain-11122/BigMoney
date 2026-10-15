# r973 probe: gdhs akshare endpoint (early vs mid quarter) + sse/szse connectivity
# evidence for ext_slots backfill death diagnosis (P-1d line, bm-b lane)
import time

import akshare as ak

for q in ["20150930", "20161231"]:
    try:
        df = ak.stock_zh_a_gdhs(symbol=q)
        print(q, "OK rows=", len(df))
    except Exception as e:
        print(q, "FAIL", type(e).__name__, str(e)[:100])
    time.sleep(2.5)

import requests

for host, url, hdr in [
    ("sse", "https://query.sse.com.cn/marketdata/tradedata/queryMargin.do?tabType=mxtype",
     {"Referer": "https://www.sse.com.cn/", "User-Agent": "Mozilla/5.0"}),
    ("szse", "https://www.szse.cn/", {"User-Agent": "Mozilla/5.0"}),
]:
    try:
        r = requests.get(url, timeout=8, headers=hdr)
        print(host, "HTTP", r.status_code)
    except Exception as e:
        print(host, "FAIL", type(e).__name__, str(e)[:80])
