"""r398 bm-b probe-3: empirical basis check of the local bootstrap face
data/daily/sh510300.csv vs sina raw (klc_kl.js) around the three windows:
(a) tail 2026-09-22 (b) 2025-06-18 dividend (u=0.123) (c) 2026-01-19 event.
Determines whether the local face is raw-basis or qfq-adjusted, and which
factor model reproduces it."""

import os

for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY",
          "all_proxy", "ALL_PROXY"):
    os.environ.pop(k, None)

import requests
import pandas as pd
from py_mini_racer import MiniRacer
import akshare.stock.stock_zh_a_sina as m

sym = "sh510300"
r = requests.get(m.zh_sina_a_stock_hist_url.format(sym), timeout=15)
js = MiniRacer()
js.eval(m.hk_js_decode)
dl = js.call("d", r.text.split("=")[1].split(";")[0].replace('"', ""))
src = pd.DataFrame(dl)
src["date"] = pd.to_datetime(src["date"], errors="coerce").dt.date.astype(str)
src = src.set_index("date")
for c in ("prevclose", "postVol", "postAmt"):
    if c in src.columns:
        del src[c]

rq = requests.get(m.zh_sina_a_stock_qfq_url.format(sym), timeout=15)
import json as _json
payload = _json.loads(rq.text.split("=", 1)[1].split("/*", 1)[0].strip())
ev = payload["data"]
print("factor events (desc):")
for e in ev[:4]:
    print("  ", e)

local = pd.read_csv("data/daily/sh510300.csv", dtype={"date": str})
local = local.set_index("date")

for probe_date in ("2026-09-22", "2026-01-16", "2026-01-19", "2026-01-20",
                   "2025-06-17", "2025-06-18", "2025-06-19", "2015-05-20"):
    if probe_date not in src.index or probe_date not in local.index:
        print(probe_date, "MISSING in", 
              "src" if probe_date not in src.index else "local")
        continue
    s_row = src.loc[probe_date]
    l_row = local.loc[probe_date]
    raw_close = float(s_row["close"])
    loc_close = float(l_row["close"])
    ratio = loc_close / raw_close if raw_close else None
    print(f"{probe_date}: src_raw_close={raw_close:.4f} "
          f"local_close={loc_close:.4f} ratio={ratio:.6f}")

# factor model reproduction: cumulative factor by date, desc events
# hypothesis: factor for dates in (prev_event, event] = product of s of
# all strictly-later events (sina desc order); dates after latest = 1.0
events = sorted(ev, key=lambda e: e["d"])
cum = 1.0
factor_by_event = {}
for e in reversed(events):          # oldest -> newest
    factor_by_event[e["d"]] = cum   # applies to dates <= this event? probe below
    cum *= float(e["s"])

def factor_for(d):
    f = 1.0
    for e in reversed(events):      # newest first
        if d < e["d"]:
            f = float(e["s"])
            break
    return f

print("model A (factor = s of latest event with event_date > d):")
for probe_date in ("2026-09-22", "2026-01-16", "2025-06-17", "2015-05-20"):
    s_row = src.loc[probe_date]
    l_row = local.loc[probe_date]
    f = factor_for(probe_date)
    adj = float(s_row["close"]) * f if f else float(s_row["close"])
    # alt: divide
    fd = 1.0 / f if f else 1.0
    print(f"  {probe_date}: raw={float(s_row['close']):.4f} "
          f"x{s!r}={adj:.4f} /f={float(s_row['close'])/f:.4f} "
          f"local={float(l_row['close']):.4f}")
