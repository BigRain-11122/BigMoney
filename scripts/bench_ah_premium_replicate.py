"""Independent replicate of the ah_premium cell, written on a different path.

Why a second implementation
---------------------------
r1282: a published absolute number must be recomputed at least once by something
that does not share the first one's code. This script never imports the cell; it
reads the same parquet as a long table, joins formation/exit bars per pair, ranks
the premium, and reports the cheap-minus-all and cheap-minus-rich spreads with a
trimmed mean (1%/99%) instead of the cell's corporate-action repair. If the two
paths disagree on direction or order of magnitude, the cell's reading is wrong.

It prints and writes an evidence file; it never writes the cell's result.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PANEL = os.path.join(ROOT, "data", "ah_panel", "ah_premium_panel.parquet")
OUT = os.path.join(ROOT, "results", "_r2021bmc_ah_replicate.json")
HOLD = 20
QUANTILE = 0.20
PPY = 244.0 / HOLD


def run():
    df = pd.read_parquet(PANEL)
    df["date"] = pd.to_datetime(df["date"])
    dates = sorted(df["date"].unique())
    rows = []
    for i in range(HOLD, len(dates) - HOLD, HOLD):
        t, t2 = dates[i], dates[i + HOLD]
        cur = df[df["date"] == t][["a_code", "close_A", "close_H", "fx_HKD_CNY"]]
        nxt = df[df["date"] == t2][["a_code", "close_A"]]
        j = cur.set_index("a_code").join(nxt.set_index("a_code"),
                                        lsuffix="_0", rsuffix="_1", how="inner")
        j = j[(j["close_A_0"] > 0) & (j["close_A_1"] > 0)]
        if len(j) < 20:
            continue
        prem = j["close_A_0"] / (j["close_H"] * j["fx_HKD_CNY"]) - 1.0
        ret = j["close_A_1"] / j["close_A_0"] - 1.0
        q = prem.rank(pct=True)
        lo, hi = ret.quantile(0.01), ret.quantile(0.99)
        r = ret.clip(lo, hi)
        rows.append({"date": str(pd.Timestamp(t).date()),
                     "cheap": float(r[q <= QUANTILE].mean()),
                     "all": float(r.mean()),
                     "rich": float(r[q >= 1 - QUANTILE].mean()),
                     "names": int(len(j))})

    d = pd.DataFrame(rows)
    d["diff_cheap_all"] = d["cheap"] - d["all"]
    d["diff_cheap_rich"] = d["cheap"] - d["rich"]

    def stat(col):
        x = d[col].values
        se = float(np.std(x, ddof=1)) / np.sqrt(len(x))
        return {"ann_pct": round(float(x.mean()) * PPY * 100.0, 2),
                "t": round(float(x.mean()) / se, 2),
                "mde_pct": round(1.96 * se * PPY * 100.0, 2)}

    pay = {
        "replicate_of": "bench_ah_premium",
        "method": "long-table join, 1%/99% trimmed mean, no corporate-action repair",
        "periods": int(len(d)),
        "first": d["date"].iloc[0], "last": d["date"].iloc[-1],
        "diff_cheap_minus_all": stat("diff_cheap_all"),
        "diff_cheap_minus_rich": stat("diff_cheap_rich"),
        "mean_period_pct": {"cheap": round(float(d["cheap"].mean()) * 100, 3),
                            "all": round(float(d["all"].mean()) * 100, 3),
                            "rich": round(float(d["rich"].mean()) * 100, 3)},
        "years": {int(y): round(float(v) * PPY * 100.0, 1) for y, v in
                  d.assign(y=[int(x[:4]) for x in d["date"]]).groupby("y")["diff_cheap_all"].mean().items()},
        "generated": pd.Timestamp.now(tz="Asia/Shanghai").isoformat(timespec="seconds"),
    }
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(pay, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(json.dumps(pay, ensure_ascii=False, indent=1))
    return pay


if __name__ == "__main__":
    run()
    sys.exit(0)
