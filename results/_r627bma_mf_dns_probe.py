# r627 bm-a: EM push2his DNS A-record fork probe (r614 croc-relay multi-A family diagnosis)
import json, time, datetime, socket, ssl
import urllib.request

EVID = {"ts": datetime.datetime.now().isoformat(timespec="seconds"), "dns": [], "probes": []}
HOST = "push2his.eastmoney.com"

# resolve several times to collect the A-record set
ips = set()
for _ in range(6):
    try:
        infos = socket.getaddrinfo(HOST, 443, socket.AF_INET)
        ip = infos[0][4][0]
        ips.add(ip)
        EVID["dns"].append(ip)
    except Exception as e:
        EVID["dns"].append("ERR " + str(e)[:80])
    time.sleep(0.3)
print("dns round-robin seen:", sorted(ips))

_ms = str(int(time.time() * 1000))
PATH = ("/api/qt/stock/fflow/daykline/get?lmt=0&klt=101&secid=0.000151"
        "&fields1=f1,f2,f3,f7&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65"
        "&ut=b2884a393a59ad64002292a3e90d46a5&_=" + _ms)
ctx = ssl.create_default_context()

def probe_ip(ip, gap=5):
    time.sleep(gap)
    url = f"https://{ip}/{PATH}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Host": HOST})
    t0 = time.time()
    try:
        r = urllib.request.urlopen(req, timeout=8, context=ctx)
        body = r.read(150)
        EVID["probes"].append({"ip": ip, "ok": True, "http": r.status, "elapsed_s": round(time.time()-t0, 2)})
    except Exception as e:
        EVID["probes"].append({"ip": ip, "ok": False, "elapsed_s": round(time.time()-t0, 2),
                               "err": type(e).__name__ + ": " + str(e)[:150]})
    print(EVID["probes"][-1])

for ip in sorted(ips):
    probe_ip(ip)
# second pass to test consistency (same ip twice with 5s gap)
if sorted(ips):
    probe_ip(sorted(ips)[0], gap=8)

json.dump(EVID, open("results/_r627bma_mf_dns_probe.json", "w", encoding="utf-8"), indent=1)
ok = sum(1 for p in EVID["probes"] if p["ok"])
print(f"SUMMARY: {ok}/{len(EVID['probes'])} ok")
