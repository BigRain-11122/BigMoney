# -*- coding: utf-8 -*-
"""R239 T-74 s1 probe-3: LHB history depth + last-day readout + fresh-48 sector momentum board.
Read-only, deterministic. Writes results/_r239_t74_probe3.json (UTF-8, script-written)."""
import glob
import json
import os

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = {}

# 1) LHB face: history depth + latest trade-day readout (columns: 上榜日/涨跌幅/龙虎榜净买额/上榜原因/名称/代码)
lhb_path = os.path.join(ROOT, "Money02", "data", "lhb", "lhb_detail.parquet")
try:
    df = pd.read_parquet(lhb_path, columns=["上榜日", "代码", "名称", "涨跌幅", "龙虎榜净买额", "上榜原因"])
    df["上榜日"] = pd.to_datetime(df["上榜日"])
    mx = df["上榜日"].max()
    mn = df["上榜日"].min()
    last = df[df["上榜日"] == mx].copy()
    top_buy = last.nlargest(5, "龙虎榜净买额")[["代码", "名称", "涨跌幅", "龙虎榜净买额"]]
    top_sell = last.nsmallest(5, "龙虎榜净买额")[["代码", "名称", "涨跌幅", "龙虎榜净买额"]]
    out["lhb"] = {
        "rows_total": int(len(df)),
        "min_date": str(mn.date()),
        "max_date": str(mx.date()),
        "last_day_rows": int(len(last)),
        "last_day_net_buy_sum": float(last["龙虎榜净买额"].sum()),
        "last_day_pctchg_mean": float(last["涨跌幅"].mean()),
        "top5_net_buy": top_buy.to_dict("records"),
        "bottom5_net_buy": top_sell.to_dict("records"),
        "reasons_top": last["上榜原因"].value_counts().head(5).to_dict(),
    }
except Exception as e:
    out["lhb"] = {"state": "FACE_ERROR", "error": repr(e)[:300]}

# 2) fresh-48 sector momentum board (asof 2026-09-24 files only)
recs = []
for f in glob.glob(os.path.join(ROOT, "data", "daily", "*.csv")):
    sym = os.path.splitext(os.path.basename(f))[0]
    try:
        px = pd.read_csv(f, usecols=[0, 4])
    except Exception:
        continue
    px.columns = ["date", "close"]
    px["date"] = pd.to_datetime(px["date"])
    px = px.sort_values("date").dropna()
    if str(px["date"].iloc[-1].date()) != "2026-09-24" or len(px) < 61:
        continue
    c = px["close"].values
    recs.append({
        "symbol": sym,
        "r5": round(float(c[-1] / c[-6] - 1), 4),
        "r20": round(float(c[-1] / c[-21] - 1), 4),
        "r60": round(float(c[-1] / c[-61] - 1), 4),
    })
recs.sort(key=lambda r: r["r20"], reverse=True)
out["fresh48_momentum"] = {"n": len(recs), "board": recs}

# 3) core48 breadth proxy: fraction with r20>0 (breadth from fresh files)
if recs:
    out["breadth_r20_pos"] = round(sum(1 for r in recs if r["r20"] > 0) / len(recs), 3)

with open(os.path.join(ROOT, "results", "_r239_t74_probe3.json"), "w", encoding="utf-8", newline="\n") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1, default=str)
print("ok n_lhb=", out.get("lhb", {}).get("rows_total"), "n_fresh=", len(recs))
