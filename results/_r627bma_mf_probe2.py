# r627 bm-a: push2his vs push2 discrimination probe (moneyflow lane R63 block diagnosis)
import json, time, datetime
import urllib.request, ssl

EVID = {"ts": datetime.datetime.now().isoformat(timespec="seconds"), "probes": []}
ctx = ssl.create_default_context()

BROWSER = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Referer": "https://data.eastmoney.com/zjlx/detail.html",
    "Accept": "*/*",
}
AK_UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"}

def probe(name, url, headers, gap=6):
    time.sleep(gap)  # respect potential token-bucket refill
    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers=headers)
        r = urllib.request.urlopen(req, timeout=10, context=ctx)
        body = r.read(200)
        EVID["probes"].append({"name": name, "ok": True, "http": r.status, "elapsed_s": round(time.time()-t0, 2)})
    except Exception as e:
        EVID["probes"].append({"name": name, "ok": False, "elapsed_s": round(time.time()-t0, 2),
                               "err": type(e).__name__ + ": " + str(e)[:180]})
    print(EVID["probes"][-1])

import time as _t
_ms = str(int(_t.time() * 1000))

# push2his exact akshare URL (secid 0.000151, full history)
his_url = ("https://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get?lmt=0&klt=101"
           "&secid=0.000151&fields1=f1,f2,f3,f7"
           "&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65"
           "&ut=b2884a393a59ad64002292a3e90d46a5&_=" + _ms)
# push2 same daykline path
p2_url = his_url.replace("push2his", "push2")

probe("his_plain_urllib", his_url, {"User-Agent": "Mozilla/5.0"})
probe("his_akshare_ua", his_url, AK_UA)
probe("his_browser_hdr", his_url, BROWSER)
probe("push2_daykline_plain", p2_url, {"User-Agent": "Mozilla/5.0"})
probe("push2_kline_small_lmt_recheck",
      "https://push2.eastmoney.com/api/qt/stock/fflow/kline/get?secid=0.000001&fields1=f1,f2,f3,f7"
      "&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65&klt=101&lmt=5",
      {"User-Agent": "Mozilla/5.0"})

json.dump(EVID, open("results/_r627bma_mf_probe2.json", "w", encoding="utf-8"), indent=1)
ok = sum(1 for p in EVID["probes"] if p["ok"])
print(f"SUMMARY: {ok}/{len(EVID['probes'])} ok")
