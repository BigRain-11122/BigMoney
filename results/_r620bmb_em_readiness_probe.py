"""bm-b EM moneyflow pull readiness probe (MSG-2026-10-03-1452 option-A evidence).

Read-only, zero writes to shared faces. Mirrors collector request shape
(scripts/update_moneyflow.py v2 rank lane: push2 clist + push2his daykline control).
Evidence only -- no lane claim, no panel touch (P1 lane-change law: GM ruling face).
"""
import json, os, time, sys, urllib.request, urllib.error

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '_r620bmb_em_readiness_probe.json')

for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "all_proxy", "ALL_PROXY"):
    os.environ.pop(k, None)

RANK_URL = "https://push2.eastmoney.com/api/qt/clist/get"
RANK_PARAMS = {
    "pn": 1, "pz": 100, "po": 1, "np": 1, "fltt": 2, "invt": 2,
    "fid": "f62",
    "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23,m:0+t:81+s:2048",
    "fields": "f12,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87",
}
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
           "Referer": "https://quote.eastmoney.com/"}
DAYKLINE_URL = "https://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get"
DAYKLINE_PARAMS = {"lmt": 0, "klt": 101, "secid": "1.600519", "fields1": "f1,f2,f3,f7",
                   "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65"}


def _get(url, params, timeout=10):
    qs = "&".join(f"{k}={urllib.parse.quote(str(v), safe='')}" for k, v in params.items())
    req = urllib.request.Request(url + "?" + qs, headers=HEADERS)
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read()
            return {"ok": True, "http": r.status, "bytes": len(body), "latency_s": round(time.time() - t0, 2)}
    except urllib.error.HTTPError as e:
        return {"ok": False, "error": "HTTPError", "http": e.code, "latency_s": round(time.time() - t0, 2)}
    except Exception as e:
        return {"ok": False, "error": type(e).__name__, "detail": str(e)[:120], "latency_s": round(time.time() - t0, 2)}


res = {"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "machine": "bm-b", "purpose":
       "MSG-2026-10-03-1452 option-A readiness evidence (read-only probe)",
       "rank_face": [], "daykline_control_face": []}

# rank face: 6 sequential pages at collector pace 2.5s (bm-a block pattern: first 1-2 ok then edge hard-block)
for pn in range(1, 7):
    p = dict(RANK_PARAMS); p["pn"] = pn
    r = _get(RANK_URL, p)
    res["rank_face"].append({"pn": pn, **r})
    if pn < 6:
        time.sleep(2.5)

# daykline face: 2 attempts, 5s apart (dead-face control)
for i in range(2):
    r = _get(DAYKLINE_URL, DAYKLINE_PARAMS)
    res["daykline_control_face"].append({"attempt": i + 1, **r})
    if i == 0:
        time.sleep(5.0)

ok_ct = sum(1 for r in res["rank_face"] if r["ok"])
res["rank_summary"] = {"pages_ok": ok_ct, "pages_total": len(res["rank_face"]),
                       "sustained_viable_80page_daily_pull": ok_ct >= 6}
res["daykline_summary"] = {"attempts_ok": sum(1 for r in res["daykline_control_face"] if r["ok"]),
                            "note": "dead face per DIGEST-20260925 control only"}
json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1)[:1500])
