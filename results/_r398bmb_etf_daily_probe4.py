"""r398 bm-b probe-4: FULL overlap dry-compare, all five members, zero writes.
Prices tol 1e-6 abs; volume/amount int-round compare. If clean, the first
live fire of update_etf_daily.py cannot false-red on rounding."""

import os

for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY",
          "all_proxy", "ALL_PROXY"):
    os.environ.pop(k, None)

import requests
from py_mini_racer import MiniRacer
import akshare.stock.stock_zh_a_sina as m

MEMBERS = ["510300", "510050", "510500", "512100", "588000"]
verdict = {}
for code in MEMBERS:
    sym = "sh" + code
    r = requests.get(m.zh_sina_a_stock_hist_url.format(sym), timeout=15)
    js = MiniRacer()
    js.eval(m.hk_js_decode)
    dl = js.call("d", r.text.split("=")[1].split(";")[0].replace('"', ""))
    src = {}
    for it in dl:
        d = str(it.get("date", ""))[:10]
        src[d] = it
    local_lines = open(f"data/daily/sh{code}.csv", encoding="utf-8").read()
    local_rows = [ln.split(",") for ln in local_lines.strip().splitlines()[1:]]
    bad = 0
    first_bad = None
    for ln in local_rows:
        d = ln[0]
        if d not in src:
            first_bad = f"{d}: absent in source"
            bad += 1
            break
        s = src[d]
        try:
            for idx, key in ((1, "open"), (2, "high"), (3, "low"), (4, "close")):
                if abs(float(ln[idx]) - float(s[key])) > 1e-6:
                    raise ValueError(f"{key} {ln[idx]} vs {s[key]}")
            if abs(int(float(ln[5])) - int(round(float(s["volume"])))) > 1:
                raise ValueError(f"volume {ln[5]} vs {s['volume']}")
            if abs(int(float(ln[6])) - int(round(float(s["amount"])))) > 1:
                raise ValueError(f"amount {ln[6]} vs {s['amount']}")
        except ValueError as e:
            first_bad = f"{d}: {e}"
            bad += 1
            break
    new_rows = [d for d in sorted(src) if d > local_rows[-1][0]]
    verdict[code] = {
        "local_rows": len(local_rows), "src_rows": len(src),
        "overlap_bad": bad, "first_bad": first_bad,
        "new_dates": new_rows,
    }
    print(code, verdict[code])

import json
with open("results/_r398bmb_etf_daily_probe4.json", "w", encoding="utf-8") as f:
    json.dump(verdict, f, ensure_ascii=False, indent=1)
print("ALL CLEAN" if all(v["overlap_bad"] == 0 for v in verdict.values())
      else "MISMATCH FOUND")
