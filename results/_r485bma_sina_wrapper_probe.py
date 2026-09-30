"""r485 bm-a: 09-30 bar wrapper-endpoint probe (T-04 wrapper vs raw sina).

Three legs, all read-only (zero data writes):
  1. akshare wrapper fund_etf_hist_sina("sh510300") tail dates
  2. raw sina klc_kl.js endpoint (same family update_etf_daily uses)
  3. local panel tail (what update_daily would append onto)
Honest exit 0 with printed evidence; no crash on network failure.
"""
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

out = {"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "symbol": "sh510300"}

# --- leg 1: akshare wrapper tail
try:
    import akshare as ak
    df = ak.fund_etf_hist_sina(symbol="sh510300")
    out["wrapper_tail"] = [str(x) for x in df["date"].tail(3)]
    out["wrapper_rows"] = int(len(df))
except Exception as e:  # noqa: BLE001 -- honest evidence either way
    out["wrapper_error"] = f"{type(e).__name__}: {e}"[:300]

# --- leg 2: raw sina klc_kl.js (direct endpoint, same family as
# update_etf_daily's MiniRacer recipe; decoder module if importable)
try:
    import urllib.request
    url = ("https://finance.sina.com.cn/realstock/company/"
           "sh510300/hisdata/klc_kl.js")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        raw = r.read()
    out["klc_bytes"] = len(raw)
    # exact update_etf_daily recipe (fetch_member): akshare's own decoder
    # constants + MiniRacer -- single source of truth, no reimplementation
    import requests
    from scripts.update_etf_daily import fetch_member  # read-only pull
    rows = fetch_member("510300")
    out["klc_tail"] = [str(x["date"]) for x in rows[-3:]]
    out["klc_rows"] = int(len(rows))
    last = rows[-1]
    out["klc_last_bar"] = {k: last[k] for k in
                           ("date", "open", "high", "low", "close", "volume",
                            "amount")}
except Exception as e:  # noqa: BLE001
    out["klc_error"] = f"{type(e).__name__}: {e}"[:300]

# --- leg 3: local panel tail
import pandas as pd  # noqa: E402
mine = pd.read_csv(ROOT / "data/daily/510300.csv", dtype={"date": str})
out["local_tail"] = [str(x) for x in mine["date"].tail(3)]

# --- leg 4 (r485 scope probe): is the lag sina-wide?
#   a) stock face: sh600519 klc tail via same recipe
#   b) realtime face: sina hq quote for 510300 alive?
try:
    import akshare.stock.stock_zh_a_sina as m
    import requests as _rq
    hist_url, js_decode = m.zh_sina_a_stock_hist_url, m.hk_js_decode
    from py_mini_racer import MiniRacer
    for sym in ("sh600519", "sz159915"):
        r2 = _rq.get(hist_url.format(sym), timeout=15)
        js2 = MiniRacer()
        js2.eval(js_decode)
        dl2 = js2.call("d", r2.text.split("=")[1].split(";")[0].replace('"', ""))
        tail2 = sorted(str(x["date"])[:10] for x in dl2)[-3:] if dl2 else []
        # decoded dicts use day key 'd'/'o'/'h'/'l'/'v' per sina face
        out.setdefault("scope_klc_tails", {})[sym] = tail2
except Exception as e:  # noqa: BLE001
    out["scope_error"] = f"{type(e).__name__}: {e}"[:200]

try:
    import requests as _rq3
    hq = _rq3.get(
        "https://hq.sinajs.cn/list=sh510300",
        headers={"Referer": "https://finance.sina.com.cn", "User-Agent":
                 "Mozilla/5.0"}, timeout=10)
    out["hq_alive"] = bool(hq.text.strip()) and "hq_str" in hq.text
    out["hq_head"] = hq.text[:80].replace("\n", "")
except Exception as e:  # noqa: BLE001
    out["hq_error"] = f"{type(e).__name__}: {e}"[:200]

print(json.dumps(out, ensure_ascii=False, indent=1))
(Path(ROOT / "results/_r485bma_sina_wrapper_probe.json")
 ).write_text(json.dumps(out, ensure_ascii=False, indent=1), "utf-8")
