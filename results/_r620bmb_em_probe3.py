"""bm-b EM daykline sustained-trial probe (20 syms, collector pace, read-only).

MSG-1452 option-A evidence leg 3: discriminates '2/2 lucky' vs sustained
viability for the 5222-request full-universe pull. Zero panel writes.
"""
import json, os, time, sys, urllib.request, urllib.error, urllib.parse
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '_r620bmb_em_probe3_daykline_trial.json')
for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "all_proxy", "ALL_PROXY"):
    os.environ.pop(k, None)
DAYKLINE_URL = "https://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
           "Referer": "https://quote.eastmoney.com/"}
# 20 symbols across sh/sz from eligibility universe (deterministic sample: first 10 sh6 + first 10 sz0/3)
syms = ["600000", "600004", "600006", "600007", "600008", "600009", "600010", "600011",
        "600012", "600015", "000001", "000002", "000004", "000005", "000006", "000007",
        "000008", "000009", "000010", "300001"]


def secid(code):
    return ("1." if code.startswith("6") else ("0." if code[0] in "03" else "0.")) + code


rows = []
ok = 0
for i, code in enumerate(syms):
    params = {"lmt": 0, "klt": 101, "secid": secid(code),
              "fields1": "f1,f2,f3,f7",
              "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65"}
    qs = "&".join(f"{k}={urllib.parse.quote(str(v), safe='')}" for k, v in params.items())
    req = urllib.request.Request(DAYKLINE_URL + "?" + qs, headers=HEADERS)
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            b = r.read()
            n_json_bytes = len(b)
            rows.append({"sym": code, "ok": True, "http": r.status, "bytes": n_json_bytes,
                         "latency_s": round(time.time() - t0, 2)})
            ok += 1
    except Exception as e:
        code_h = e.code if hasattr(e, 'code') else None
        rows.append({"sym": code, "ok": False, "error": type(e).__name__, "http": code_h,
                     "detail": str(e)[:100]})
    if i < len(syms) - 1:
        time.sleep(2.5)
res = {"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "machine": "bm-b",
       "trial": {"syms_attempted": len(syms), "ok": ok,
                 "first_fail_index": next((i for i, r in enumerate(rows) if not r["ok"]), None)},
       "rows": rows}
json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(res["trial"], ensure_ascii=False))
print("latencies ok:", [r["latency_s"] for r in rows if r["ok"]])
