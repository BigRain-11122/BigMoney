# -*- coding: utf-8 -*-
"""E18 基本面温度计 v0 描述探针（fund_thermo_probe.py）

P3 explore 队列 E18（seed gate hits=[] + T-18 CLEAR 同轮·登记认领同轮·E13/E14 先例）。
消费面=data/fund_statement_export/ 三 parquet（FUND_STATEMENT_PANEL as-collected 冻结面）。
产出=results/fund_thermo/fund_thermo.csv + fund_thermo.json（年频全史中位温度行 + 最新 H1 当前读数行）。

纪律（零判据零 prereg 零网络零 marks）：
- 纯描述面：只输出中位数/分位/份额类温度读数，不含任何判据、门槛、prereg 面。
- as-collected 修订局限（FUND_STATEMENT_PANEL §4）：EM 按期接口返回采集时点最新修订值，
  历史行含重述污染——本探针只作年代变迁描述，不作品质宣称。
- 宇宙=面板原样（含已退市代码·income 面 11,757 员）；列值=EM as-disclosed 原文口径。
- Sloan 楔子=(CFO−NI)/|NI| 消费侧纯派生；cashflow 面覆盖 5,257 员<income 面，
  join 损耗逐行诚实披露（n_join vs n_income）。
- 确定性：同面板字节→同输出字节（零墙钟字段入数据行；generated 戳仅入 envelope）。

用法：
  python scripts/fund_thermo_probe.py run        # 产出 csv+json
  python scripts/fund_thermo_probe.py selftest   # 离线合成面自检
"""
import io
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PANEL_DIR = os.path.join(ROOT, "data", "fund_statement_export")
OUT_DIR = os.path.join(ROOT, "results", "fund_thermo")

INC_COLS = ["code", "period_end", "净利润-同比增长", "营业总收入-同比增长", "净资产收益率", "销售毛利率", "净利润-净利润"]
BAL_COLS = ["code", "period_end", "资产负债率"]
CF_COLS = ["code", "period_end", "经营性现金流-现金流量净额"]

THERMO_COLS = [
    "period", "n_income", "n_balance", "n_join",
    "roe_med_pct", "profit_growth_med_pct", "rev_growth_med_pct",
    "margin_med_pct", "lev_med_pct", "wedge_med", "wedge_neg_share",
    "ni_pos_share",
]


def _med(s: pd.Series) -> float:
    x = pd.to_numeric(s, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
    if len(x) == 0:
        return float("nan")
    return float(np.median(x))


def _share(s: pd.Series, cond) -> float:
    x = pd.to_numeric(s, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
    if len(x) == 0:
        return float("nan")
    return float(cond(x).mean())


def thermo_row(period: str, inc: pd.DataFrame, bal: pd.DataFrame, cf: pd.DataFrame) -> dict:
    """单期温度行：三面逐期切片中位读数（EM as-disclosed 原文口径）。"""
    i = inc[inc["period_end"] == period]
    b = bal[bal["period_end"] == period]
    c = cf[cf["period_end"] == period]
    j = i[["code", "净利润-净利润"]].merge(
        c[["code", "经营性现金流-现金流量净额"]], on="code", how="inner"
    )
    ni = pd.to_numeric(j["净利润-净利润"], errors="coerce")
    cfo = pd.to_numeric(j["经营性现金流-现金流量净额"], errors="coerce")
    ok = ni.notna() & cfo.notna() & (ni.abs() > 0)
    wedge = ((cfo - ni) / ni.abs())[ok]
    return {
        "period": period,
        "n_income": int(len(i)),
        "n_balance": int(len(b)),
        "n_join": int(ok.sum()),
        "roe_med_pct": _med(i["净资产收益率"]),
        "profit_growth_med_pct": _med(i["净利润-同比增长"]),
        "rev_growth_med_pct": _med(i["营业总收入-同比增长"]),
        "margin_med_pct": _med(i["销售毛利率"]),
        "lev_med_pct": _med(b["资产负债率"]),
        "wedge_med": _med(wedge),
        "wedge_neg_share": _share(wedge, lambda x: x < 0),
        "ni_pos_share": _share(i["净利润-净利润"], lambda x: x > 0),
    }


def build_rows(inc: pd.DataFrame, bal: pd.DataFrame, cf: pd.DataFrame) -> pd.DataFrame:
    """年频面（各年 12-31 年报期）+ 最新 H1 当前读数行。"""
    periods = sorted(p for p in inc["period_end"].dropna().unique() if str(p).endswith("-12-31"))
    latest_h1 = sorted(p for p in inc["period_end"].dropna().unique() if str(p).endswith("-06-30"))
    rows = [thermo_row(p, inc, bal, cf) for p in periods]
    if latest_h1:
        rows.append(thermo_row(latest_h1[-1], inc, bal, cf))
    return pd.DataFrame(rows, columns=THERMO_COLS)


def _load_faces(panel_dir: str):
    inc = pd.read_parquet(os.path.join(panel_dir, "income_faces.parquet"))[INC_COLS]
    bal = pd.read_parquet(os.path.join(panel_dir, "balance_faces.parquet"))[BAL_COLS]
    cf = pd.read_parquet(os.path.join(panel_dir, "cashflow_faces.parquet"))[CF_COLS]
    return inc, bal, cf


def cmd_run() -> int:
    inc, bal, cf = _load_faces(PANEL_DIR)
    df = build_rows(inc, bal, cf)
    os.makedirs(OUT_DIR, exist_ok=True)
    csv_path = os.path.join(OUT_DIR, "fund_thermo.csv")
    json_path = os.path.join(OUT_DIR, "fund_thermo.json")
    df.to_csv(csv_path, index=False, encoding="utf-8")
    cutoff = str(inc["period_end"].max())
    payload = {
        "evidence_cutoff": cutoff,
        "method": {
            "faces": "income/balance/cashflow as-collected (FUND_STATEMENT_PANEL spec sec.4 latest-revision face)",
            "universe": "panel-verbatim incl. delisted codes",
            "wedge": "derived (CFO-NI)/|NI| per (code,period) inner join; join loss disclosed per row",
            "stats": "median/share only; zero thresholds; zero prereg faces",
        },
        "honest_faces": [
            "as-collected revision taint: historical rows carry latest restatement as of collection (EM per-period interface)",
            "cashflow face covers fewer codes than income face (mainboard-heavy); n_join < n_income per row",
            "EM as-disclosed column semantics (ROE/growth/margin percent-scale) taken verbatim",
        ],
        "rows": json.loads(df.to_json(orient="records", force_ascii=True)),
    }
    with io.open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
        f.write("\n")
    cur = df.iloc[-1]
    print(f"rows={len(df)} cutoff={cutoff}")
    print(f"latest: period={cur['period']} n={cur['n_income']} join={cur['n_join']} roe_med={cur['roe_med_pct']:.2f} "
          f"pg_med={cur['profit_growth_med_pct']:.2f} margin_med={cur['margin_med_pct']:.2f} "
          f"lev_med={cur['lev_med_pct']:.2f} wedge_med={cur['wedge_med']:.2f} cfo_lt_ni={cur['wedge_neg_share']:.3f}")
    print("RUN-OK")
    return 0


def _synthetic_faces():
    periods = ["2019-12-31", "2020-12-31", "2020-06-30"]
    inc = pd.DataFrame({
        "code": ["000001", "000002", "000003"] * 3,
        "period_end": [p for p in periods for _ in range(3)],
        "净利润-同比增长": [10.0, 20.0, 30.0, 5.0, 15.0, 25.0, 1.0, 2.0, 3.0],
        "营业总收入-同比增长": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0],
        "净资产收益率": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0],
        "销售毛利率": [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0],
        "净利润-净利润": [100.0, 200.0, -300.0, 400.0, 500.0, 600.0, 700.0, 800.0, 900.0],
    })
    bal = pd.DataFrame({
        "code": ["000001", "000002", "000003"] * 3,
        "period_end": [p for p in periods for _ in range(3)],
        "资产负债率": [40.0, 50.0, 60.0, 44.0, 55.0, 66.0, 10.0, 11.0, 12.0],
    })
    cf = pd.DataFrame({
        "code": ["000001", "000002", "000003"] * 3,
        "period_end": [p for p in periods for _ in range(3)],
        "经营性现金流-现金流量净额": [150.0, 100.0, -350.0, 300.0, 400.0, 300.0, 350.0, 400.0, 450.0],
    })
    return inc, bal, cf


def cmd_selftest() -> int:
    ok = 0

    def check(name, cond):
        nonlocal ok
        assert cond, f"SELFTEST-FAIL: {name}"
        ok += 1

    inc, bal, cf = _synthetic_faces()
    df = build_rows(inc, bal, cf)
    # T1 行数=年频 2 行+H1 1 行
    check("row_count", len(df) == 3)
    # T2 周期序
    check("period_order", df["period"].tolist() == ["2019-12-31", "2020-12-31", "2020-06-30"])
    # T3 中位=合成均值位
    r19 = df[df["period"] == "2019-12-31"].iloc[0]
    check("roe_med_2019", abs(r19["roe_med_pct"] - 2.0) < 1e-9)
    check("lev_med_2019", abs(r19["lev_med_pct"] - 50.0) < 1e-9)
    # T4 join 损耗与楔子：2019 三员全 join，wedge=(CFO-NI)/|NI| → [0.5,-0.5,-1/6] 中位=-1/6
    check("join_n_2019", r19["n_join"] == 3)
    w = sorted([0.5, -0.5, (-350.0 - (-300.0)) / 300.0])
    check("wedge_med_2019", abs(r19["wedge_med"] - w[1]) < 1e-9)
    # T5 CFO<NI 份额：150<100 F / 100<200 T / -350<-300 T → 2/3
    check("wedge_neg_share_2019", abs(r19["wedge_neg_share"] - 2.0 / 3.0) < 1e-9)
    # T6 盈利面覆盖率（NI>0 份额）
    check("ni_pos_share_2019", abs(r19["ni_pos_share"] - 2.0 / 3.0) < 1e-9)
    # T7 H1 行独立切片（不与年频混合）
    rh1 = df[df["period"] == "2020-06-30"].iloc[0]
    check("h1_n", rh1["n_income"] == 3)
    check("h1_roe_med", abs(rh1["roe_med_pct"] - 8.0) < 1e-9)
    # T8 join 缺员诚实：2020H1 现金流全员在场=3
    check("h1_join_n", rh1["n_join"] == 3)
    # T9 面板在位（真实面列校验·read-only）
    for f, cols in (("income_faces.parquet", INC_COLS), ("balance_faces.parquet", BAL_COLS), ("cashflow_faces.parquet", CF_COLS)):
        head = pd.read_parquet(os.path.join(PANEL_DIR, f))
        check(f"real_cols_{f.split('_')[0]}", all(c in head.columns for c in cols))
    print(f"selftest {ok}/{ok} PASS")
    return 0


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] not in ("run", "selftest"):
        print("usage: fund_thermo_probe.py run|selftest")
        return 2
    return cmd_run() if sys.argv[1] == "run" else cmd_selftest()


if __name__ == "__main__":
    sys.exit(main())
