"""LHB T+1 open-entry realism probe (r680 bm-a).

The static EM 上榜后N日 columns are close(T)-anchored; a real strategy enters at
open(T+1) (O-1132 conservative proxy). This probe measures, on in-house per-stock
bars (Money02/data/bars/<code>.parquet):
  gap  = open(T+1)/close(T) - 1          (the leg the static column hides)
  ret1 = close(T+1)/open(T+1) - 1        (capturable 1d hold, gross)
  ret5 = close(T+5)/open(T+1) - 1        (capturable 5d hold, gross)
Faces: all-LHB baseline + netbuy>=5000w. Net at cost x1 13.041bp/side.
Entry = first bar strictly after 上榜日 (suspension-delayed entries counted, gap_days reported).
Read-only. Output: results/_r680bma_lhb_openentry.json
"""
import json
import numpy as np
import pandas as pd

OUT = "results/_r680bma_lhb_openentry.json"
COST_SIDE = 0.0013041  # x1 cost spec per side


def stats(arr: np.ndarray) -> dict:
    s = pd.Series(arr).dropna()
    if len(s) < 100:
        return {"n": int(len(s)), "skip": "n<100"}
    return {
        "n": int(len(s)),
        "mean_pct": float(s.mean() * 100),
        "median_pct": float(s.median() * 100),
        "win_rate": float((s > 0).mean()),
        "p10_pct": float(s.quantile(0.10) * 100),
        "p90_pct": float(s.quantile(0.90) * 100),
        "mean_net_pct": float((s - 2 * COST_SIDE).mean() * 100),
    }


def main() -> int:
    df = pd.read_parquet("Money02/data/lhb/lhb_detail.parquet")
    df["day"] = pd.to_datetime(df["上榜日"])
    df["net_buy"] = pd.to_numeric(df["龙虎榜净买额"], errors="coerce")
    dd = df.sort_values("序号").drop_duplicates(subset=["代码", "day"], keep="first").copy()
    dd["code"] = dd["代码"].astype(str).str.zfill(6)

    faces = {
        "all_lhb": dd,
        "netbuy_ge5000w": dd[dd["net_buy"] >= 5e7],
    }

    out = {"probe": "LHB T+1 open-entry realism", "cost_side_x1": COST_SIDE, "faces": {}}
    for fname, sub in faces.items():
        gaps, ret1, ret5, delay = [], [], [], []
        missing = 0
        for code, grp in sub.groupby("code"):
            path = f"Money02/data/bars/{code}.parquet"
            try:
                b = pd.read_parquet(path, columns=["date", "open", "close"])
            except Exception:
                missing += len(grp)
                continue
            b["date"] = pd.to_datetime(b["date"])
            b = b.dropna(subset=["open", "close"])
            if not len(b):
                missing += len(grp)
                continue
            dts = b["date"].values
            opens = b["open"].values
            closes = b["close"].values
            for day in grp["day"].values:
                i = np.searchsorted(dts, np.datetime64(day), side="right")
                if i >= len(b):
                    continue  # beyond bar coverage (e.g. 2026-09 rows at panel edge)
                if i == 0:
                    continue
                o = opens[i]
                delay.append(0 if (dts[i] - np.datetime64(day)).astype("timedelta64[D]").astype(int) <= 4 else 1)
                gaps.append(o / closes[i - 1] - 1)
                ret1.append(closes[i] / o - 1)
                j = min(i + 4, len(b) - 1)
                ret5.append(closes[j] / o - 1)
        out["faces"][fname] = {
            "rows_in_face": int(len(sub)),
            "bar_missing_codes_rows": int(missing),
            "gap_openT1_over_closeT": stats(np.array(gaps)),
            "ret1_openT1_to_closeT1_gross": stats(np.array(ret1)),
            "ret5_openT1_to_closeT5_gross": stats(np.array(ret5)),
            "delayed_entry_gt4d_share": float(np.mean(delay)) if delay else None,
        }
        print(fname, json.dumps(out["faces"][fname], ensure_ascii=False)[:400])

    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
