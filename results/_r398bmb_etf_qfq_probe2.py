"""r398 bm-b probe-2: qfq.js raw payload schema for ETF codes."""

import os

for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY",
          "all_proxy", "ALL_PROXY"):
    os.environ.pop(k, None)

import requests
import akshare.stock.stock_zh_a_sina as m

for sym in ("sh510300", "sh588000"):
    rq = requests.get(m.zh_sina_a_stock_qfq_url.format(sym), timeout=15)
    txt = rq.text
    print(sym, "status", rq.status_code, "len", len(txt))
    print("--- head 300 chars ---")
    print(txt[:300])
    print("--- tail 200 chars ---")
    print(txt[-200:])
    print()
