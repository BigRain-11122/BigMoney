"""r398 bm-b step-0 probe: sina direct endpoints (hist klc_kl.js + qfq.js)
for the five-member ETF daily qfq refresh leg (candidate ticket per
ETF_OPS_BP1_PREREG S0 sec-3.2 disclosure; akshare wrapper fails on the
outstanding_share/turnover leg for ETF codes -- bypass recipe probe).

Validates: (1) hist leg decodes for sh510300, (2) qfq factor leg serves
ETF codes, (3) qfq-adjusted tail matches the frozen bootstrap face
data/daily/sh510300.csv row 2026-09-22 (open 4.6360 high 4.6580 low
4.6120 close 4.6130 vol 644587351 amount 2987237086)."""

import os

for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY",
          "all_proxy", "ALL_PROXY"):
    os.environ.pop(k, None)

import requests
import pandas as pd
from py_mini_racer import MiniRacer
import akshare.stock.stock_zh_a_sina as m

out = {}

for sym in ("sh510300", "sh510050", "sh510500", "sh512100", "sh588000"):
    rec = {}
    r = requests.get(m.zh_sina_a_stock_hist_url.format(sym), timeout=15)
    rec["hist_status"] = r.status_code
    js = MiniRacer()
    js.eval(m.hk_js_decode)
    dl = js.call("d", r.text.split("=")[1].split(";")[0].replace('"', ""))
    df = pd.DataFrame(dl)
    df.index = pd.to_datetime(df["date"], errors="coerce").dt.date
    del df["date"]
    for c in ("prevclose", "postVol", "postAmt"):
        if c in df.columns:
            del df[c]
    rec["rows"] = len(df)
    rec["raw_last"] = str(df.index[-1])

    rq = requests.get(m.zh_sina_a_stock_qfq_url.format(sym), timeout=15)
    rec["qfq_status"] = rq.status_code
    try:
        qf = pd.DataFrame(eval(rq.text.split("=")[1].split("\n")[0])["data"])
        qf.columns = ["date", "qfq_factor"]
        qf.index = pd.to_datetime(qf.date).dt.date
        del qf["date"]
        rec["qfq_rows"] = len(qf)
        rec["qfq_last_factor"] = float(qf["qfq_factor"].iloc[-1])
        adj = df.drop(columns=["amount"]).astype(float).div(
            qf["qfq_factor"], axis=0)
        adj["amount"] = df["amount"].astype(float)
        rec["adj_last"] = {
            "date": str(adj.index[-1]),
            "open": round(float(adj["open"].iloc[-1]), 4),
            "high": round(float(adj["high"].iloc[-1]), 4),
            "low": round(float(adj["low"].iloc[-1]), 4),
            "close": round(float(adj["close"].iloc[-1]), 4),
            "volume": float(adj["volume"].iloc[-1]),
            "amount": float(adj["amount"].iloc[-1]),
        }
    except Exception as e:
        rec["qfq_error"] = f"{type(e).__name__}: {e}"

    # overlap check vs local bootstrap face (2026-09-22 row)
    if sym == "sh510300":
        local = pd.read_csv("data/daily/sh510300.csv")
        rec["local_tail"] = local.tail(1).to_dict("records")
    out[sym] = rec
    print(sym, "->", {k: v for k, v in rec.items() if k != "adj_last"})
    print("   adj_last:", rec.get("adj_last"))

import json
with open("results/_r398bmb_etf_daily_probe.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1, default=str)
print("probe artifact -> results/_r398bmb_etf_daily_probe.json")
