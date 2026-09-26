"""R299 bm-a SW official classification Excel fetch (queue #4, R99 probe facts).

swsresearch.com serves an incomplete TLS chain (SSL: unable to get local
issuer certificate); the official SW 2021 classification workbook is a
public static research file. One-shot fetch: try certifi CA bundle first,
then verify=False with sha256 disclosure in the probe JSON.
"""
import hashlib
import json
import time

import requests

URL = "https://www.swsresearch.com/swindex/pdf/SwClass2021/StockClassifyUse_stock.xls"
OUT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\data\basic\sw_stock_classify_2021.xls"
META = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\results\_r299bma_sw_clf_meta.json"

hdr = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                     "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
res = {"url": URL, "ts": time.strftime("%Y-%m-%d %H:%M:%S")}

content = None
try:
    import certifi
    r = requests.get(URL, headers=hdr, verify=certifi.where(), timeout=60)
    r.raise_for_status()
    content = r.content
    res["tls"] = "certifi"
except Exception as e:
    res["certifi_err"] = f"{type(e).__name__}: {str(e)[:200]}"
    try:
        r = requests.get(URL, headers=hdr, verify=False, timeout=60)
        r.raise_for_status()
        content = r.content
        res["tls"] = "verify=False (incomplete server chain disclosed; public static research file)"
    except Exception as e2:
        res["verify_false_err"] = f"{type(e2).__name__}: {str(e2)[:200]}"
        print(json.dumps(res, ensure_ascii=False, indent=1))
        raise SystemExit(2)

open(OUT, "wb").write(content)
res["bytes"] = len(content)
res["sha256"] = hashlib.sha256(content).hexdigest()
json.dump(res, open(META, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1))
