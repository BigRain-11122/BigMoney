"""bm-b EM probe continuation: discriminate transient 502 vs edge-throttle onset."""
import json, os, time, sys, urllib.request, urllib.error, urllib.parse
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '_r620bmb_em_probe2.json')
for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "all_proxy", "ALL_PROXY"):
    os.environ.pop(k, None)
RANK_URL = "https://push2.eastmoney.com/api/qt/clist/get"
BASE = {"pz": 100, "po": 1, "np": 1, "fltt": 2, "invt": 2, "fid": "f62",
        "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23,m:0+t:81+s:2048",
        "fields": "f12,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87"}
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
           "Referer": "https://quote.eastmoney.com/"}
rows = []
for pn in range(7, 15):
    qs = "&".join(f"{k}={urllib.parse.quote(str(v), safe='')}" for k, v in {**BASE, 'pn': pn}.items())
    req = urllib.request.Request(RANK_URL + "?" + qs, headers=HEADERS)
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            rows.append({"pn": pn, "ok": True, "http": r.status, "bytes": len(r.read()), "latency_s": round(time.time()-t0, 2)})
    except Exception as e:
        code = e.code if hasattr(e, 'code') else None
        rows.append({"pn": pn, "ok": False, "error": type(e).__name__, "http": code, "detail": str(e)[:100]})
    time.sleep(2.5)
res = {"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "machine": "bm-b",
       "pages": rows, "ok_ct": sum(1 for r in rows if r["ok"])}
json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1)[:1200])
