"""R212 probe-2: characterize/unblock push2 clist RemoteDisconnected (blocked since 09-25 01:50).

Read-only network diagnostics; zero panel writes. Variants:
  A. production query, direct (confirm block reproduces)
  B. production query, via system proxy (different egress IP)
  C. production query, browser-grade headers, direct
  D. numbered CDN mirrors (1./2./3.push2 + push2delay), direct
Pace: one request per variant, ~1.5s spacing (probe etiquette, not scraping).
"""
import sys, time, json, urllib.request, os
sys.stdout.reconfigure(encoding="utf-8")

QS = ("pn=1&pz=100&po=1&np=1&fltt=2&invt=2&fid=f62"
      "&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23,m:0+t:81+s:2048"
      "&fields=f12,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87")
BASE_UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
           "Referer": "https://quote.eastmoney.com/"}
BROWSER_HEADERS = dict(BASE_UA, **{
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "Origin": "https://quote.eastmoney.com",
})

def direct_opener():
    return urllib.request.build_opener(urllib.request.ProxyHandler({}))

def proxy_opener():
    # default opener honors registry/env proxies (Clash on this LAN per fleet docs)
    return urllib.request.build_opener()

def try_variant(name, url, headers, opener, timeout=10):
    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers=headers)
        with opener.open(req, timeout=timeout) as resp:
            body = resp.read(2000)
            js = json.loads(body.decode("utf-8", errors="replace"))
            data = js.get("data") or {}
            n = len(data.get("diff") or []) if isinstance(data.get("diff"), (list, dict)) else 0
            total = data.get("total")
            ms = int((time.time() - t0) * 1000)
            print(f"{name}: HTTP {resp.status} {ms}ms total={total} rows={n} -> WORKS")
            return {"ok": True, "status": resp.status, "ms": ms, "total": total, "rows": n}
    except Exception as e:
        ms = int((time.time() - t0) * 1000)
        print(f"{name}: FAIL {type(e).__name__}: {str(e)[:90]} | {ms}ms")
        return {"ok": False, "err": f"{type(e).__name__}: {str(e)[:120]}", "ms": ms}

res = {}
prod_url = "https://push2.eastmoney.com/api/qt/clist/get?" + QS
res["A_prod_direct"] = try_variant("A_prod_direct", prod_url, BASE_UA, direct_opener())
time.sleep(1.5)
res["B_prod_via_proxy"] = try_variant("B_prod_via_proxy", prod_url, BASE_UA, proxy_opener())
time.sleep(1.5)
res["C_prod_browserhdr"] = try_variant("C_prod_browserhdr", prod_url, BROWSER_HEADERS, direct_opener())
time.sleep(1.5)
for n, host in [("D_1.push2", "https://1.push2.eastmoney.com"),
                ("D_2.push2", "https://2.push2.eastmoney.com"),
                ("D_90.push2", "https://90.push2.eastmoney.com"),
                ("D_push2delay", "https://push2delay.eastmoney.com")]:
    res[n] = try_variant(n, host + "/api/qt/clist/get?" + QS, BROWSER_HEADERS, direct_opener())
    time.sleep(1.5)

with open("results/_r212_clist_unblock_probe.json", "w", encoding="utf-8") as f:
    json.dump({"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "variants": res}, f, ensure_ascii=False, indent=1)
print("saved -> results/_r212_clist_unblock_probe.json")
