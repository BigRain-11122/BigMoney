"""LHB family cheap census probe v2 (r680 bm-a, TRIAL_LABOR_LAW sec.2 廉价初筛先行).

v1 bug fixed: EM schema position 7=净买额 8=买入额 9=卖出额 (v1 used pos9 sell as net_buy).
Name-based access now. Read-only. Output: results/_r680bma_lhb_census.json (overwrite)

Faces:
  A reason buckets (per code-day-reason rows; EM lists one row per reason)
  B direction buckets on deduped (code,day): 净买额 signed
  C netbuy/mktcap ratio buckets (deduped)
  D regime leg: 510300 close vs MA200 -> bull/bear face (deduped)
Forward returns = EM as-collected static (measurement only, not a burn substitute).
"""
import json
import numpy as np
import pandas as pd

OUT = "results/_r680bma_lhb_census.json"
DAILY_510300 = "data/daily/510300.csv"

REASON_PREFIXES = [
    ("日跌幅偏离值", "down_dev"),
    ("日涨幅偏离值", "up_dev"),
    ("换手率达到", "turnover"),
    ("振幅达到", "amplitude"),
    ("连续三个交易日", "streak3d"),
]


def main() -> int:
    df = pd.read_parquet("Money02/data/lhb/lhb_detail.parquet")
    df["day"] = pd.to_datetime(df["上榜日"])
    for c in ("龙虎榜净买额", "流通市值", "上榜后1日", "上榜后2日", "上榜后5日", "上榜后10日", "涨跌幅"):
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # --- dedup to (code, day) for direction/ratio/regime faces ---
    dd = df.sort_values("序号").drop_duplicates(subset=["代码", "day"], keep="first").copy()

    base = {
        "rows_total": int(len(df)),
        "rows_dedup_code_day": int(len(dd)),
        "day_min": str(df["day"].min().date()),
        "day_max": str(df["day"].max().date()),
        "n_codes": int(df["代码"].nunique()),
        "fwd5_coverage": float(df["上榜后5日"].notna().mean()),
    }

    def cell(sub: pd.DataFrame, col="上榜后5日") -> dict:
        s = sub[col].dropna()
        if len(s) < 100:
            return {"n": int(len(s)), "skip": "n<100"}
        return {
            "n": int(len(s)),
            "mean_pct": float(s.mean()),
            "median_pct": float(s.median()),
            "win_rate": float((s > 0).mean()),
            "p10": float(s.quantile(0.10)),
            "p90": float(s.quantile(0.90)),
        }

    out = {"probe": "LHB cheap census v2 (schema-correct, sec.2 screen-first)", "base": base, "faces": {}}

    # A: reason buckets (raw rows carry per-reason duplicates; report share of rows)
    rf = {}
    used = np.zeros(len(df), dtype=bool)
    for pref, tag in REASON_PREFIXES:
        m = df["上榜原因"].astype(str).str.contains(pref, regex=False)
        used |= m.values
        rf[tag] = cell(df[m])
        rf[tag]["row_share"] = float(m.mean())
    rf["_unmatched_row_share"] = float(1 - used.mean())
    out["faces"]["A_reason"] = rf

    # B: direction buckets (deduped) on signed 净买额
    nb = dd[dd["龙虎榜净买额"].notna()]
    out["faces"]["B_direction"] = {
        "netbuy_ge5000w": cell(nb[nb["龙虎榜净买额"] >= 5e7]),
        "netbuy_1000_5000w": cell(nb[(nb["龙虎榜净买额"] >= 1e7) & (nb["龙虎榜净买额"] < 5e7)]),
        "netbuy_lt1000w": cell(nb[(nb["龙虎榜净买额"] < 1e7)]),
    }

    # C: |netbuy| / mktcap ratio (deduped)
    rr = dd[dd["流通市值"].notna() & dd["龙虎榜净买额"].notna()].copy()
    rr["ratio"] = rr["龙虎榜净买额"].abs() / rr["流通市值"]
    out["faces"]["C_amount_ratio"] = {
        "gt5pct": cell(rr[rr["ratio"] > 0.05]),
        "1to5pct": cell(rr[(rr["ratio"] > 0.01) & (rr["ratio"] <= 0.05)]),
        "lt1pct": cell(rr[rr["ratio"] <= 0.01]),
    }

    # D: regime leg (510300 close vs MA200)
    idx = pd.read_csv(DAILY_510300, encoding="utf-8")
    dcol = idx.columns[0]
    ccol = [c for c in idx.columns if "close" in c.lower() or "收盘" in c][0]
    idx[dcol] = pd.to_datetime(idx[dcol])
    idx = idx.sort_values(dcol)
    idx["ma200"] = idx[ccol].rolling(200).mean()
    idx["regime"] = np.where(idx[ccol] > idx["ma200"], "bull", "bear")
    rmap = dict(zip(idx[dcol], idx["regime"]))
    dd["regime"] = dd["day"].map(rmap)
    out["faces"]["D_regime"] = {
        "bull": cell(dd[dd["regime"] == "bull"]),
        "bear": cell(dd[dd["regime"] == "bear"]),
        "unmapped_share": float(dd["regime"].isna().mean()),
    }
    # D2: regime x direction top face (netbuy>=5000w in bull)
    b_face = dd[(dd["regime"] == "bull") & (dd["龙虎榜净买额"] >= 5e7)]
    out["faces"]["D2_bull_netbuy_ge5000w"] = cell(b_face)

    # E: fwd1 realism leg (T+1 close vs T+0 close)
    out["faces"]["E_fwd1"] = {
        "all": cell(dd, "上榜后1日"),
        "netbuy_ge5000w": cell(dd[dd["龙虎榜净买额"] >= 5e7], "上榜后1日"),
    }

    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("BASE", json.dumps(base, ensure_ascii=False))
    for k, v in out["faces"].items():
        print(k, json.dumps(v, ensure_ascii=False)[:500])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
