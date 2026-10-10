import json
import akshare as ak, inspect

# --- C2: what are rate_interbank's real market_map keys?
src = inspect.getsource(ak.rate_interbank)
i = src.find("market_map")
print("MAP-SEG:", src[i:i+260])

# --- B2: chinamoney FrrHis direct, short window, raw capture
import urllib.request, urllib.parse
url = "https://www.chinamoney.com.cn/ags/ms/cm-u-bk-currency/FrrHis"
data = urllib.parse.urlencode({"lang": "CN", "startDate": "2026-09-01",
                               "endDate": "2026-10-10"}).encode()
req = urllib.request.Request(url, data=data, headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded",
})
try:
    with urllib.request.urlopen(req, timeout=45) as r:
        payload = json.loads(r.read().decode("utf-8", errors="replace"))
    print("TOP-KEYS:", list(payload.keys()))
    recs = payload.get("records")
    print("N-RECORDS:", len(recs) if recs is not None else None)
    if recs:
        print("REC0-KEYS:", list(recs[0].keys()))
        print("REC0:", json.dumps(recs[0], ensure_ascii=False)[:400])
except Exception as e:
    print("B2-ERR", type(e).__name__, str(e)[:200])
