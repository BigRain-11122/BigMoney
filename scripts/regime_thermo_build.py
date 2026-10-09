# -*- coding: utf-8 -*-
"""
REGIME_THERMO_V1 — 游资情绪温度计三轴深史构建器（P6 情绪腿·O-20261006-1218 P6 承接·GM 直执窗）

令源: CEO O-20261006-1218 SYNTHESIS-R1 P6 + O-20261009 全速推进令（"自己选方向"）
消费面: C1 政体门情绪腿 / 题材配合面(risk on/off overlay) / 情绪族供给线(E6 唯一低 PBO 族)
性质: 纯数据工程+描述统计（零试验·零判据宣称·探索标注全盖）

==== 冻结规格（跑前写死·零刻度触碰）====
宇宙: Money02/data/bars 全面板 5,222 只（沪深 A 股主板/创业板/科创板·无北交所·panel as-is）
证据截止: 2026-09-22（P-5C 冻结面·与机队全线一致）
有效域: 1996-12-16 起（涨跌停制度恢复日·此前无限制年代比率法无意义——诚实截断）
率表(按代码前缀×日期·广播):
  688xxx 科创板: 20%（2019-07-22 起·板上限）
  300xxx 创业板: 2020-08-24 前 10%·起 20%
  其余(主板/中小板): 10%
  ST 5% 桶: 历史逐日 ST 状态=DATA_GAP(D-41 §3-3)→用 5% 精确匹配捕获（非 ST 股恰好收 +5.00% 的噪声如实披露）
涨停判定(比率法·qfq 面板下相邻日比率在非除权日精确保持):
  sealed(r): |close/preclose - (1+r)| <= tol, tol = 0.005/preclose + 0.0002（涨停价 2 位小数舍入的物理极限=半分钱/pc）
  touched(r): high/preclose >= (1+r) - tol
  炸板 = touched 且非 sealed
  跌停: 同法取 -(1+r)
  上市首日(preclose NaN)自动出局
  面值守卫: preclose < 1.0 元的仙股行剔除（A 股面值退市制度下极端罕见·容差失真域·如实披露）
连板梯队: 同一 code 内连续 sealed 交易日块 = 高度（分块 cumcount 法·v1.0 修复=高度不封顶）
已知近似(全披露):
  ①除权日相邻比率失真(少数漏检/误检·面板 qfq 性质)
  ②历史 ST 逐日状态缺失→5% 桶含少量非 ST 噪声·主率桶(10/20%)不受影响
  ③非 ST 股 +5.00% 精确收盘的罕见误计入
输出:
  results/regime_thermo/thermo_daily.csv（1996-12-16 起逐日三轴+梯队+衍生指标）
  results/regime_thermo/thermo_summary.json（年度均值/名场面读数/极值表）
描述面: 只报无条件分布与历史事件读数；条件前向收益验证=后续预注册切片（本件禁做）
"""

import os, json, glob
import numpy as np
import pandas as pd

BASE = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
BARS = os.path.join(BASE, "Money02", "data", "bars")
OUT = os.path.join(BASE, "results", "regime_thermo")
os.makedirs(OUT, exist_ok=True)

VALID_FROM = pd.Timestamp("1996-12-16")
CYB_20 = pd.Timestamp("2020-08-24")

# ---------- 1. 读面板 ----------
frames = []
files = sorted(glob.glob(os.path.join(BARS, "*.parquet")))
for i, fp in enumerate(files):
    code = os.path.splitext(os.path.basename(fp))[0]
    df = pd.read_parquet(fp, columns=["date", "close", "high", "preclose"])
    df["code"] = code
    frames.append(df)
    if (i + 1) % 1000 == 0:
        print(f"  loaded {i+1}/{len(files)}", flush=True)
panel = pd.concat(frames, ignore_index=True)
print("panel rows:", len(panel))

panel = panel.dropna(subset=["preclose", "close", "high"])
panel = panel[panel["preclose"] > 0]
panel = panel[panel["date"] >= VALID_FROM].copy()
print("valid rows (>=1996-12-16):", len(panel))

# ---------- 2. 率表与三轴 ----------
pfx = panel["code"].str[:3]
is_cyb = pfx == "300"
is_kcb = pfx == "688"
rate = np.where(is_kcb, 0.20, np.where(is_cyb & (panel["date"] >= CYB_20), 0.20, 0.10))
panel["rate"] = rate

rc = panel["close"] / panel["preclose"] - 1.0
rh = panel["high"] / panel["preclose"] - 1.0
tol = 0.005 / panel["preclose"] + 0.0002

r = panel["rate"].to_numpy()
rc_v, rh_v, tol_v = rc.to_numpy(), rh.to_numpy(), tol.to_numpy()

penny_guard = (panel["preclose"] >= 1.0).to_numpy()
sealed_main = (np.abs(rc_v - r) <= tol_v) & penny_guard
touched_main = (rh_v >= r - tol_v) & penny_guard
sealed_st5 = (np.abs(rc_v - 0.05) <= tol_v) & (~sealed_main) & penny_guard
touched_st5 = (rh_v >= 0.05 - tol_v) & (~touched_main) & (~sealed_main) & penny_guard
sealed_down = (np.abs(rc_v + r) <= tol_v) & penny_guard

panel["sealed"] = sealed_main | sealed_st5
panel["touched"] = touched_main | touched_st5 | panel["sealed"].to_numpy()
panel["sealed_down"] = sealed_down

# ---------- 3. 连板梯队（同 code 连续 sealed 块·分块 cumcount·高度不封顶） ----------
panel = panel.sort_values(["code", "date"]).reset_index(drop=True)
run_id = (~panel["sealed"]).groupby(panel["code"]).cumsum()
panel["lianh_height"] = 0
idx = np.flatnonzero(panel["sealed"].to_numpy())
codes_s = panel["code"].to_numpy()[idx]
runs_s = run_id.to_numpy()[idx]
heights = pd.Series(np.ones(len(idx), dtype=np.int64), index=idx)\
            .groupby([pd.Index(codes_s), pd.Index(runs_s)]).cumcount().to_numpy() + 1
panel.iloc[idx, panel.columns.get_loc("lianh_height")] = heights
mx = int(panel["lianh_height"].max())
print("max lianh_height across history:", mx)

# 连板审计：高度>=15 的块逐个打印（防数据伪 streak·人工可核）
audit = panel[panel["lianh_height"] >= 15].copy()
if len(audit):
    print("\n=== STREAK AUDIT (height>=15) ===")
    seen = set()
    for _, row in audit.sort_values("lianh_height", ascending=False).iterrows():
        key = (row["code"], row["lianh_height"])
        if key in seen:
            continue
        seen.add(key)
        sub = panel[(panel["code"] == row["code"]) &
                   (panel["date"] >= row["date"] - pd.Timedelta(days=int(row["lianh_height"] * 1.6))) &
                   (panel["date"] <= row["date"])]
        tail = sub.tail(6)[["date", "close", "preclose", "sealed"]].to_string(index=False)
        print(f"code={row['code']} height={row['lianh_height']} end={row['date'].date()} min_pc={sub['preclose'].min():.2f}\n{tail}")
        if len(seen) >= 8:
            break

# ---------- 4. 逐日聚合 ----------
g = panel.groupby("date")
daily = pd.DataFrame({
    "n_trade": g["code"].nunique(),
    "n_sealed": g["sealed"].sum(),
    "n_touched": g["touched"].sum(),
    "n_sealed_down": g["sealed_down"].sum(),
})
daily["n_broke"] = daily["n_touched"] - daily["n_sealed"]
daily["seal_rate"] = np.where(daily["n_touched"] > 0, daily["n_sealed"] / daily["n_touched"], np.nan)

lh = panel[panel["sealed"]]
hs = lh.groupby("date")["lianh_height"]
daily["n_firstboard"] = hs.apply(lambda s: int((s == 1).sum()))
daily["n_lianban2"] = hs.apply(lambda s: int((s == 2).sum()))
daily["n_lianban3"] = hs.apply(lambda s: int((s == 3).sum()))
daily["n_lianban4p"] = hs.apply(lambda s: int((s >= 4).sum()))
daily["max_height"] = hs.max()
daily = daily.fillna({"max_height": 0}).astype({"max_height": int})
daily["pct_sealed"] = daily["n_sealed"] / daily["n_trade"]

daily = daily.reset_index()
daily.to_csv(os.path.join(OUT, "thermo_daily.csv"), index=False, encoding="utf-8")

# ---------- 5. 摘要 ----------
d = daily.set_index("date")
ycols = ["n_sealed", "n_touched", "seal_rate", "n_lianban2", "n_lianban3", "n_lianban4p",
         "max_height", "pct_sealed", "n_sealed_down"]
years = d.groupby(d.index.year)[ycols].mean().round(4)

famous = ["2015-06-12", "2015-06-15", "2015-06-19", "2015-08-24", "2016-01-04",
          "2019-02-25", "2020-02-03", "2020-07-06", "2024-02-05", "2024-02-07",
          "2024-09-24", "2024-09-25", "2024-09-30", "2024-10-08",
          "2025-04-07", "2025-06-11", "2026-01-05", "2026-09-18", "2026-09-22"]
fkeys = ["n_sealed", "n_touched", "seal_rate", "n_lianban2", "n_lianban3",
         "n_lianban4p", "max_height", "n_sealed_down"]
fam = {}
for f in famous:
    ts = pd.Timestamp(f)
    if ts in d.index:
        row = d.loc[ts]
        fam[f] = {k: (int(row[k]) if isinstance(row[k], (np.integer, int)) and k != "seal_rate"
                      else round(float(row[k]), 4)) for k in fkeys}
    else:
        fam[f] = None

top_sealed = d["n_sealed"].nlargest(10)
top_height = d["max_height"].nlargest(10)
top_down = d["n_sealed_down"].nlargest(10)
low_sealrate = d[d["n_touched"] >= 100]["seal_rate"].nsmallest(10)
top_lb4p = d["n_lianban4p"].nlargest(10)

summary = {
    "meta": {
        "universe": "Money02 bars panel 5222 codes (SH/SZ main+ChiNext+STAR, no BSE, as-is)",
        "evidence_cutoff": "2026-09-22", "valid_from": "1996-12-16",
        "built_by": "GM direct window (bm-a session) 2026-10-09",
        "law_ref": "O-20261006-1218 P6 / O-1522 folk-numeric mandate / D-41 zero-trial data-engineering",
        "exploration_label": "ALL descriptive, zero criterion claims, forward-return validation deferred to prereg slice",
    },
    "n_days": int(len(d)),
    "yearly_mean": years.to_dict(),
    "famous_days": fam,
    "top10_seal_count": {str(k.date()): int(v) for k, v in top_sealed.items()},
    "top10_max_height": {str(k.date()): int(v) for k, v in top_height.items()},
    "top10_down_limit": {str(k.date()): int(v) for k, v in top_down.items()},
    "top10_lianban4p": {str(k.date()): int(v) for k, v in top_lb4p.items()},
    "bottom10_seal_rate_touched100": {str(k.date()): round(float(v), 4) for k, v in low_sealrate.items()},
}
with open(os.path.join(OUT, "thermo_summary.json"), "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=1, default=str)

pd.set_option("display.width", 220)
print("\n=== YEARS ===\n", years.to_string())
print("\n=== FAMOUS ===\n", json.dumps(fam, ensure_ascii=False, indent=1))
print("\n=== TOP SEAL ===\n", top_sealed.to_string())
print("\n=== TOP HEIGHT ===\n", top_height.to_string())
print("\n=== TOP LIANBAN4P ===\n", top_lb4p.to_string())
print("\n=== TOP DOWN ===\n", top_down.to_string())
print("\n=== LOW SEAL RATE (touched>=100) ===\n", low_sealrate.to_string())
print("\nLAST 5 DAYS:\n", d.tail(5).to_string())
print("\nDONE. csv+json at", OUT)
