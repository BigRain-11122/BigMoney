# -*- coding: utf-8 -*-
"""E19 双温度计对照描述探针（dual_thermo_probe.py）

P3 explore 队列 E19（seed gate hits=[] + T-18 CLEAR 同轮·登记认领同轮·E18 digest 指针消费面）。
消费面=results/regime_thermo/thermo_daily.csv（P6 情绪温度计·日频·REGIME_THERMO_V1 冻结容差率表）
        + results/fund_thermo/fund_thermo.csv（E18 基本面温度计·年频中位五轴+Sloan 楔子）。
产出=results/dual_thermo/dual_thermo.csv + dual_thermo.json（年度对照表 + 关键面相关读数）。

纪律（零判据零 prereg 零网络零 marks）：
- 纯描述面：只输出均值/计数/相关类对照读数，不含任何判据、门槛、prereg 面。
- 双温度计语义对照：基本面年报（Y 年 12-31 期）=Y 年经营实况（采集时点最新修订·as-collected）；
  情绪面（Y 日历年聚合）=Y 年市场实况。join=「同域年对照」非先行滞后宣称；领先滞后面不在本探针射程。
- 趋势伪相关诚实面：双族均有长程漂移（ROE 20 年斜坡/封住率 31 年衰减），水平相关受共同趋势污染——
  水平与一阶差分（YoY Δ）相关双面并报，差分面为趋势稳健读数。
- 小样本诚实：全史对照 n=21 全年（2005-2025），相关读数仅描述性；无任何显著性宣称。
- 窗口语义：2026 行=基本面 H1（06-30）×情绪面 09-22 截断的部分年——窗不对齐行如实带
  is_half_year 旗标，不进相关面。
- 确定性：同面板字节→同输出字节（零墙钟字段·幂等重跑字节恒等）。

用法：
  python scripts/dual_thermo_probe.py run        # 产出 csv+json
  python scripts/dual_thermo_probe.py selftest   # 离线合成面自检
"""
import io
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THERMO_DAILY = os.path.join(ROOT, "results", "regime_thermo", "thermo_daily.csv")
FUND_THERMO = os.path.join(ROOT, "results", "fund_thermo", "fund_thermo.csv")
OUT_DIR = os.path.join(ROOT, "results", "dual_thermo")

SENT_AGG_COLS = [
    "n_days", "seal_rate_mean", "pct_sealed_mean", "n_sealed_mean",
    "n_sealed_down_mean", "max_height_mean", "n_lianban4p_mean", "panic_days",
]
FUND_JOIN_COLS = [
    "n_join", "roe_med_pct", "profit_growth_med_pct", "rev_growth_med_pct",
    "margin_med_pct", "lev_med_pct", "wedge_med", "wedge_neg_share", "ni_pos_share",
]
JOINT_COLS = ["year", "is_half_year"] + SENT_AGG_COLS + FUND_JOIN_COLS

CORR_FUND_COLS = ["roe_med_pct", "margin_med_pct", "lev_med_pct", "wedge_med", "ni_pos_share"]
CORR_SENT_COLS = ["seal_rate_mean", "n_sealed_mean", "n_sealed_down_mean", "max_height_mean", "panic_days"]

PANIC_LINE = 1000  # n_sealed_down >= 1000 panic-day convention (REGIME_AXIS family face)


def _year_of(d) -> int:
    return int(str(d)[:4])


def sentiment_annual(daily: pd.DataFrame) -> pd.DataFrame:
    """情绪日面→日历年聚合（均值/计数·NaN 域按日跳过·诚实 n_days）。"""
    df = daily.copy()
    df["year"] = df["date"].map(_year_of)
    rows = []
    for y, g in df.groupby("year"):
        rows.append({
            "year": y,
            "n_days": int(len(g)),
            "seal_rate_mean": float(pd.to_numeric(g["seal_rate"], errors="coerce").mean()),
            "pct_sealed_mean": float(pd.to_numeric(g["pct_sealed"], errors="coerce").mean()),
            "n_sealed_mean": float(pd.to_numeric(g["n_sealed"], errors="coerce").mean()),
            "n_sealed_down_mean": float(pd.to_numeric(g["n_sealed_down"], errors="coerce").mean()),
            "max_height_mean": float(pd.to_numeric(g["max_height"], errors="coerce").mean()),
            "n_lianban4p_mean": float(pd.to_numeric(g["n_lianban4p"], errors="coerce").mean()),
            "panic_days": int((pd.to_numeric(g["n_sealed_down"], errors="coerce") >= PANIC_LINE).sum()),
        })
    return pd.DataFrame(rows, columns=["year"] + SENT_AGG_COLS)


def joint_table(fund: pd.DataFrame, sent: pd.DataFrame) -> pd.DataFrame:
    """同域年对照：基本面年频行（12-31 期）×情绪年聚合；H1 期行带半窗旗标。"""
    fund = fund.copy()
    fund["year"] = fund["period"].map(_year_of)
    fund["is_half_year"] = ~fund["period"].astype(str).str.endswith("-12-31")
    j = fund.merge(sent, on="year", how="left")
    return j[JOINT_COLS].sort_values("year").reset_index(drop=True)


def _corr_pair(a: pd.Series, b: pd.Series) -> dict:
    x = pd.to_numeric(a, errors="coerce")
    y = pd.to_numeric(b, errors="coerce")
    ok = x.notna() & y.notna()
    x, y = x[ok], y[ok]
    if len(x) < 3:
        return {"n": int(len(x)), "pearson": None, "spearman": None}
    pr = float(np.corrcoef(x, y)[0, 1]) if len(np.unique(x)) > 1 else None
    if len(np.unique(y)) > 1 and pr is not None:
        sp = float(x.rank().corr(y.rank()))
    else:
        sp = None
    return {"n": int(len(x)), "pearson": pr, "spearman": sp}


def correlation_faces(joint: pd.DataFrame) -> dict:
    """关键面相关读数：水平+一阶差分双面（仅全年行·趋势稳健差分面并报）。"""
    full = joint[~joint["is_half_year"]].copy()
    out = {"n_full_years": int(len(full)), "level": {}, "yoy_diff": {}}
    for fc in CORR_FUND_COLS:
        out["level"][fc] = {}
        out["yoy_diff"][fc] = {}
        for sc in CORR_SENT_COLS:
            out["level"][fc][sc] = _corr_pair(full[fc], full[sc])
            fd = pd.to_numeric(full[fc], errors="coerce").diff()
            sd = pd.to_numeric(full[sc], errors="coerce").diff()
            out["yoy_diff"][fc][sc] = _corr_pair(fd, sd)
    return out


def extreme_colocation(joint: pd.DataFrame) -> dict:
    """极端年共位读数：各面 top/bottom 年对照（确定性·纯描述）。"""
    full = joint[~joint["is_half_year"]].copy()
    faces = {}
    for col in ("roe_med_pct", "wedge_med", "seal_rate_mean", "n_sealed_mean", "panic_days"):
        v = pd.to_numeric(full[col], errors="coerce")
        top = full.loc[v.idxmax()]
        bot = full.loc[v.idxmin()]
        faces[col] = {
            "top_year": int(top["year"]), "top_val": float(top[col]),
            "bottom_year": int(bot["year"]), "bottom_val": float(bot[col]),
        }
    return faces


def cmd_run() -> int:
    daily = pd.read_csv(THERMO_DAILY)
    fund = pd.read_csv(FUND_THERMO)
    sent = sentiment_annual(daily)
    joint = joint_table(fund, sent)
    os.makedirs(OUT_DIR, exist_ok=True)
    csv_path = os.path.join(OUT_DIR, "dual_thermo.csv")
    json_path = os.path.join(OUT_DIR, "dual_thermo.json")
    joint.to_csv(csv_path, index=False, encoding="utf-8")
    corr = correlation_faces(joint)
    payload = {
        "evidence_cutoff": {
            "sentiment_thermo": str(daily["date"].max()),
            "fundamental_thermo": str(fund["period"].max()),
        },
        "method": {
            "join": "same-domain year: fund annual report (period Y-12-31, as-collected) x sentiment calendar-year aggregate (daily mean faces)",
            "sentiment_aggregates": "calendar-year mean over daily rows; panic_days = count(n_sealed_down>=1000)",
            "correlations": "level + first-difference (YoY) double face, full years only; Spearman + Pearson; descriptive only",
            "stats": "zero thresholds; zero prereg faces; zero lead-lag claims",
        },
        "honest_faces": [
            "trend spuriousness: both families carry long drifts (ROE 20y slope / seal_rate 31y decay); level correlations co-trend contaminated, yoy_diff face is the trend-robust reading",
            "small sample: n=21 full years (2005-2025); all correlations descriptive, no significance claims",
            "as-collected revision taint inherited from E18 (EM per-period latest-revision face)",
            "sentiment thermo known-approximation inherited (REGIME_THERMO_V1: ex-div ratio distortion / historical ST daily-state gap)",
            "2026 half-year window mismatch: fund face 2026-06-30 vs sentiment face 2026-09-22 cutoff; flagged is_half_year, excluded from correlation faces",
            "timing semantics: annual report of year Y describes year-Y operations though published in Y+1; join is same-domain co-location, NOT a lead/lag claim",
        ],
        "correlations": corr,
        "extreme_colocation": extreme_colocation(joint),
        "rows": json.loads(joint.to_json(orient="records", force_ascii=True)),
    }
    with io.open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"rows={len(joint)} full_years={corr['n_full_years']} sent_cutoff={payload['evidence_cutoff']['sentiment_thermo']}")
    ec = payload["extreme_colocation"]
    print(f"colocation: roe top={ec['roe_med_pct']['top_year']} bot={ec['roe_med_pct']['bottom_year']}; "
          f"seal_rate top={ec['seal_rate_mean']['top_year']} bot={ec['seal_rate_mean']['bottom_year']}; "
          f"wedge top={ec['wedge_med']['top_year']} bot={ec['wedge_med']['bottom_year']}")
    print("RUN-OK")
    return 0


def _synthetic_faces():
    daily = pd.DataFrame({
        "date": ["2005-01-03", "2005-01-04", "2006-01-05", "2006-01-06", "2006-01-07"],
        "n_trade": [100, 100, 100, 100, 100],
        "n_sealed": [10, 20, 5, 15, 25],
        "n_touched": [1, 2, 3, 4, 5],
        "n_sealed_down": [1500, 500, 900, 1200, 300],
        "n_broke": [1, 2, 3, 4, 5],
        "seal_rate": [0.5, 0.7, 0.2, 0.4, 0.6],
        "n_firstboard": [5, 6, 7, 8, 9],
        "n_lianban2": [1, 2, np.nan, 4, 5],
        "n_lianban3": [1, 2, 3, 4, 5],
        "n_lianban4p": [np.nan, 1, np.nan, 2, np.nan],
        "max_height": [2, 3, 4, 5, 6],
        "pct_sealed": [0.1, 0.2, 0.3, 0.4, 0.5],
    })
    fund = pd.DataFrame({
        "period": ["2005-12-31", "2006-12-31"],
        "n_income": [10, 20], "n_balance": [10, 20], "n_join": [9, 18],
        "roe_med_pct": [6.0, 9.0],
        "profit_growth_med_pct": [4.0, 29.0],
        "rev_growth_med_pct": [13.0, 19.0],
        "margin_med_pct": [20.0, 21.0],
        "lev_med_pct": [55.0, 56.0],
        "wedge_med": [0.88, 0.62],
        "wedge_neg_share": [0.27, 0.33],
        "ni_pos_share": [0.82, 0.87],
    })
    return daily, fund


def cmd_selftest() -> int:
    ok = 0

    def check(name, cond):
        nonlocal ok
        assert cond, f"SELFTEST-FAIL: {name}"
        ok += 1

    daily, fund = _synthetic_faces()
    sent = sentiment_annual(daily)
    # T1 情绪年聚合行数=2 年
    check("sent_years", sent["year"].tolist() == [2005, 2006])
    # T2 均值聚合手算：2005 seal_rate=(0.5+0.7)/2=0.6；n_sealed_mean=15
    s05 = sent[sent["year"] == 2005].iloc[0]
    check("seal_rate_mean_2005", abs(s05["seal_rate_mean"] - 0.6) < 1e-12)
    check("n_sealed_mean_2005", abs(s05["n_sealed_mean"] - 15.0) < 1e-12)
    # T3 panic 日计数：2005 一日 1500>=1000 → 1；2006 一日 1200 → 1
    check("panic_days_2005", int(s05["panic_days"]) == 1)
    s06 = sent[sent["year"] == 2006].iloc[0]
    check("panic_days_2006", int(s06["panic_days"]) == 1)
    # T4 NaN 域跳过：2006 n_lianban4p=[nan,2,nan] → mean=2
    check("lianban4p_nan_skip", abs(s06["n_lianban4p_mean"] - 2.0) < 1e-12)
    # T5 联合表 join+年序
    joint = joint_table(fund, sent)
    check("joint_rows", len(joint) == 2)
    check("joint_years", joint["year"].tolist() == [2005, 2006])
    # T6 H1 旗标面：合成面无 H1 行→恒 False
    check("no_half_flag", bool(~joint["is_half_year"].any()))
    # T7 半窗旗标腿：补一行 H1 期行（2025-06-30）→ 旗标单亮+情绪空行诚实 NaN
    fund_h1 = pd.concat([fund, pd.DataFrame([{
        "period": "2025-06-30", "n_income": 1, "n_balance": 1, "n_join": 1,
        "roe_med_pct": 1.0, "profit_growth_med_pct": 1.0, "rev_growth_med_pct": 1.0,
        "margin_med_pct": 1.0, "lev_med_pct": 1.0, "wedge_med": 1.0,
        "wedge_neg_share": 1.0, "ni_pos_share": 1.0,
    }])], ignore_index=True)
    joint_h1 = joint_table(fund_h1, sent)
    check("half_flag_single", joint_h1["is_half_year"].tolist() == [False, False, True])
    check("half_n_days_nan", bool(pd.isna(joint_h1.iloc[-1]["n_days"])))
    # T8 相关面：完美线性对→pearson=1·spearman=1；H1 行排除
    lin_fund = pd.DataFrame({
        "period": [f"{y}-12-31" for y in range(2010, 2016)],
        "n_income": 1, "n_balance": 1, "n_join": 1,
        "roe_med_pct": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
        "profit_growth_med_pct": 1.0, "rev_growth_med_pct": 1.0,
        "margin_med_pct": 1.0, "lev_med_pct": 1.0,
        "wedge_med": 1.0, "wedge_neg_share": 1.0, "ni_pos_share": 1.0,
    })
    lin_sent = pd.DataFrame({
        "year": list(range(2010, 2016)),
        "n_days": 1, "seal_rate_mean": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6],
        "pct_sealed_mean": 0.0, "n_sealed_mean": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
        "n_sealed_down_mean": 0.0, "max_height_mean": 0.0, "n_lianban4p_mean": 0.0,
        "panic_days": 0,
    })
    corr = correlation_faces(joint_table(lin_fund, lin_sent))
    check("corr_n", corr["n_full_years"] == 6)
    c = corr["level"]["roe_med_pct"]["seal_rate_mean"]
    check("pearson_perfect", c["pearson"] is not None and abs(c["pearson"] - 1.0) < 1e-9)
    check("spearman_perfect", c["spearman"] is not None and abs(c["spearman"] - 1.0) < 1e-9)
    # T9 差分面：常数水平+一次跳变→差分相关受跳变驱动（非 None·n=5）
    d = corr["yoy_diff"]["roe_med_pct"]["n_sealed_mean"]
    check("diff_n", d["n"] == 5)
    # T10 极端共位：roe top=2015 bot=2010
    ec = extreme_colocation(joint_table(lin_fund, lin_sent))
    check("extreme_top", ec["roe_med_pct"]["top_year"] == 2015)
    check("extreme_bottom", ec["roe_med_pct"]["bottom_year"] == 2010)
    # T11 真实双面在位（read-only 列校验）
    rd = pd.read_csv(THERMO_DAILY, nrows=2)
    check("real_thermo_cols", "seal_rate" in rd.columns and "date" in rd.columns)
    rf = pd.read_csv(FUND_THERMO, nrows=2)
    check("real_fund_cols", "roe_med_pct" in rf.columns and "period" in rf.columns)
    print(f"selftest {ok}/{ok} PASS")
    return 0


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] not in ("run", "selftest"):
        print("usage: dual_thermo_probe.py run|selftest")
        return 2
    return cmd_run() if sys.argv[1] == "run" else cmd_selftest()


if __name__ == "__main__":
    sys.exit(main())
