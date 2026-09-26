# -*- coding: utf-8 -*-
"""R239 T-74 s1 probe: heat-face + sector readouts for the current market call one-pager.
Deterministic, read-only, local. Output JSON to stdout (utf-8)."""
import json
import os
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = {}

# 1) LHB face: board height / limit-up count proxy / net-buy aggregate for latest trade date
lhb_path = os.path.join(ROOT, "Money02", "data", "lhb", "lhb_detail.parquet")
try:
    df = pd.read_parquet(lhb_path)
    df["交易日期"] = pd.to_datetime(df["交易日期"])
    mx = df["交易日期"].max()
    last = df[df["交易日期"] == mx]
    cols = list(df.columns)
    net_col = next((c for c in cols if "净买额" in c), None)
    net = float(last[net_col].sum()) if net_col else None
    out["lhb"] = {
        "asof": str(mx.date()),
        "rows_last_day": int(len(last)),
        "lhb_net_buy_sum_yuan": net,
        "columns": cols,
    }
except Exception as e:  # honest face-state label, never fabricate
    out["lhb"] = {"state": "FACE_ERROR", "error": repr(e)[:200]}

# 2) Heat popularity snapshots (data/heat/popularity/YYYYMMDD.json)
heat_dir = os.path.join(ROOT, "data", "heat", "popularity")
try:
    snaps = sorted(os.listdir(heat_dir))
    latest = snaps[-1]
    d = json.load(open(os.path.join(heat_dir, latest), encoding="utf-8"))
    out["heat"] = {"snapshots": len(snaps), "latest_file": latest, "latest": d}
except Exception as e:
    out["heat"] = {"state": "FACE_ERROR", "error": repr(e)[:200]}

# 3) Regime v3 full snapshot (already known ORANGE; include dims for the one-pager)
try:
    out["regime"] = json.load(open(os.path.join(ROOT, "results", "regime_state.json"), encoding="utf-8"))
except Exception as e:
    out["regime"] = {"state": "FACE_ERROR", "error": repr(e)[:200]}

# 4) Sector ETF momentum: daily panel 48 symbols, 20d/60d returns + 5d, latest date
try:
    import glob
    recs = []
    for f in glob.glob(os.path.join(ROOT, "data", "daily", "*.csv")):
        sym = os.path.splitext(os.path.basename(f))[0]
        try:
            px = pd.read_csv(f, usecols=[0, 4])  # date, close
        except Exception:
            continue
        px.columns = ["date", "close"]
        px["date"] = pd.to_datetime(px["date"])
        px = px.sort_values("date").dropna()
        if len(px) < 61:
            continue
        c = px["close"].values
        r5 = c[-1] / c[-6] - 1 if len(c) >= 6 else None
        r20 = c[-1] / c[-21] - 1 if len(c) >= 21 else None
        r60 = c[-1] / c[-61] - 1 if len(c) >= 61 else None
        recs.append({"symbol": sym, "asof": str(px["date"].iloc[-1].date()),
                     "r5": round(float(r5), 4), "r20": round(float(r20), 4), "r60": round(float(r60), 4)})
    recs.sort(key=lambda r: r["r20"], reverse=True)
    out["sector_momentum"] = {"n": len(recs), "top10_by_r20": recs[:10], "bottom5_by_r20": recs[-5:]}
except Exception as e:
    out["sector_momentum"] = {"state": "FACE_ERROR", "error": repr(e)[:200]}

# 5) moneyflow face state (EM collector mirror only, read-only)
try:
    st = json.load(open(os.path.join(ROOT, "results", "update_status.json"), encoding="utf-8"))
    out["moneyflow_gate_mirror"] = {k: st.get(k) for k in ("data_cutoff", "updated", "total_new_rows")}
except Exception as e:
    out["moneyflow_gate_mirror"] = {"state": "FACE_ERROR", "error": repr(e)[:200]}

with open(os.path.join(ROOT, "results", "_r239_t74_s1_probe.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(out, f, ensure_ascii=False, indent=1, default=str)
print("probe done -> results/_r239_t74_s1_probe.json")
