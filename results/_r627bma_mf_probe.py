# r627 bm-a: EM endpoint block diagnosis probe (moneyflow lane R63, blocked since 09-25)
# Evidence-only probe: NO writes to shared faces, results only in this file.
import json, time, datetime

EVID = {"ts": datetime.datetime.now().isoformat(timespec="seconds"), "probes": []}

def probe(name, url, headers=None, timeout=10):
    import urllib.request, urllib.error, ssl
    ctx = ssl.create_default_context()
    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers=headers or {"User-Agent": "Mozilla/5.0"})
        r = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        body = r.read(400)
        EVID["probes"].append({
            "name": name, "rc": 0, "http": r.status, "elapsed_s": round(time.time()-t0, 2),
            "body_head": body[:200].decode("utf-8", "replace")})
        return True
    except Exception as e:
        EVID["probes"].append({
            "name": name, "rc": 1, "elapsed_s": round(time.time()-t0, 2),
            "err": type(e).__name__ + ": " + str(e)[:250]})
        return False

BROWSER = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Referer": "https://quote.eastmoney.com/",
    "Accept": "*/*",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

# 1. per-stock fflow kline endpoint (what ak.stock_individual_fund_flow hits), plain UA
u1 = ("https://push2.eastmoney.com/api/qt/stock/fflow/kline/get?secid=0.000001"
      "&fields1=f1,f2,f3,f7&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65"
      "&klt=101&lmt=5")
probe("fflow_kline_plain_ua", u1)
# 2. same with full browser headers
probe("fflow_kline_browser_hdr", u1, BROWSER)
# 3. rank clist endpoint (rank lane RemoteDisconnected at 14:04)
u3 = ("https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=5&po=1&np=1"
      "&fltt=2&invt=2&fid=f62&fs=m:0+t:6&fields=f12,f14,f62")
probe("clist_rank_plain_ua", u3)
probe("clist_rank_browser_hdr", u3, BROWSER)
# 4. EM homepage reachability (control face)
probe("quote_home", "https://quote.eastmoney.com/", BROWSER)
# 5. retry fflow with small delay to see intermittent pattern
time.sleep(2)
probe("fflow_kline_retry1", u1, BROWSER)
time.sleep(2)
probe("fflow_kline_retry2", u1, BROWSER)

json.dump(EVID, open("results/_r627bma_mf_probe.json", "w", encoding="utf-8"), indent=1)
for p in EVID["probes"]:
    print(p["name"], "| rc", p["rc"], "|", p.get("http", ""), "|", p["elapsed_s"], "s",
          "|", (p.get("err") or p.get("body_head", "")[:80]))
