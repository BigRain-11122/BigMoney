# r627 bm-a: post-quiet-window single-call probe (bucket refill rate estimation)
import json, time, datetime
import urllib.request, ssl

EVID = {"ts": datetime.datetime.now().isoformat(timespec="seconds"), "probes": []}
ctx = ssl.create_default_context()

def probe(name, url, quiet_s):
    print(f"sleep {quiet_s}s ...", flush=True)
    time.sleep(quiet_s)
    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        r = urllib.request.urlopen(req, timeout=8, context=ctx)
        body = r.read(120)
        EVID["probes"].append({"name": name, "ok": True, "http": r.status, "elapsed_s": round(time.time()-t0, 2)})
    except Exception as e:
        EVID["probes"].append({"name": name, "ok": False, "elapsed_s": round(time.time()-t0, 2),
                               "err": type(e).__name__ + ": " + str(e)[:150]})
    print(EVID["probes"][-1], flush=True)

_ms = str(int(time.time() * 1000))
his = ("https://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get?lmt=0&klt=101&secid=0.000151"
       "&fields1=f1,f2,f3,f7&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65"
       "&ut=b2884a393a59ad64002292a3e90d46a5&_=" + _ms)
clist = ("https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=5&po=1&np=1"
         "&fltt=2&invt=2&fid=f62&fs=m:0+t:6&fields=f12,f14,f62")

# after ~90s quiet since last burst: single his call
probe("his_after_90s_quiet", his, 60)
# then 30s later: another his call (refill granularity test)
probe("his_after_+30s", his, 30)
# then 60s later: clist (different endpoint family)
probe("clist_after_+60s", clist, 60)

json.dump(EVID, open("results/_r627bma_mf_quiet_probe.json", "w", encoding="utf-8"), indent=1)
ok = sum(1 for p in EVID["probes"] if p["ok"])
print(f"SUMMARY: {ok}/{len(EVID['probes'])} ok")
