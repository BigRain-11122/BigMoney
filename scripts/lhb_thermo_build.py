# -*- coding: utf-8 -*-
"""
LHB_THERMO_V1 -- 游资情绪温度计 LHB 聚合腿（explore queue E5 slice-1, bm-a lane）

E5 row (state/queue/explore.md): LHB 游资情绪因子形式化——情绪周期三轴门先例
扩展·国内打法优先事（O-20260928-1522 CEO 导向律：游资情绪周期=国内原生打法
首位）。本件=第一切片：纯描述性聚合数据面（REGIME_THERMO_V1 先例镜像），
零判据零门槛零干预；判据验证一律走后续独立预注册（thermo->T-181 先例分序）。

Demarcation (anti-dup, honest):
  r680 榜单级 + r681 席位级 = LHB 跟随族（事件级选股腿）已判负关线
  (research/digests/DIGEST-20261004-lhb-seat-axis-census.md)。本件不做
  选股/跟随/事件面——只做市场级逐日聚合情绪描述（上榜热度/资金方向/榜内
  强度三轴），与已关线的跟随族零重叠。

Faces (frozen at slice-1, pure aggregation, zero invented thresholds):
  热度轴  n_lhb            当日上榜家数（唯一 code-day）
          n_rows_raw       当日上榜条目数（每条=一上榜原因·多原因不隐藏）
  方向轴  netbuy_sum       龙虎榜净买额合计（元）
          netbuy_pos_share 净买>0 家数占比（符号分裂统计，非阈值）
          med_netbuy      净买额中位数（元）
  强度轴  netbuy_intensity 净买额合计 / 市场总成交额合计（榜内游资强度）
          amt_share        龙虎榜成交额合计 / 市场总成交额合计

Data: Money02/data/lhb/lhb_detail.parquet (read-only, bm-a-hosted panel,
in-chain freshness via update_lhb.py S6 leg). Panel carries 21 as-collected
columns; col[0] is a per-row sequence id (serial), NOT the code -- all
column addressing in this builder is BY NAME (index addressing is the
r946 probe-bug: duplicated(subset=[serial, day]) falsely reported zero).

Dedup law (frozen at slice-1, disclosed):
  A code-day may carry MULTIPLE listing rows (one per listing criterion /
  解读; e.g. 3-day deviation bucket vs 1-day turnover bucket -- each reason
  has its OWN money faces and its own aggregation window, so summing across
  reasons would double-count mixed-window trades). Builder dedups on
  (代码, 上榜日) keeping the FIRST-listed row (deterministic under the
  append-only panel law); money faces therefore ride the first-listed
  reason per code-day. Raw entry count is surfaced as n_rows_raw per day
  so nothing is hidden; dropped multi-reason rows are disclosed in the
  summary meta (38,239 rows at first build).

Output:
  results/lhb_thermo/lhb_thermo_daily.csv   (full-history daily rebuild)
  results/lhb_thermo/lhb_thermo_summary.json (yearly means + famous days
                                              + top10s, all descriptive)
Idempotency: deterministic full rebuild, no wall clock inside the data
face; identical panel -> byte-identical products (thermo same-window law:
rerun after panel advance auto-extends, otherwise zero drift).

Lane guard: Money02 LHB panel absent -> stdout-only honest no-op exit 0
(r824 thermo precedent; Money02 is bm-a-hosted).

CLI:
  python scripts/lhb_thermo_build.py           # run (default)
  python scripts/lhb_thermo_build.py selftest # offline hermetic battery
Exit codes: 0 normal/no-op, 2 mechanism fault.
"""

import io
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PANEL = os.path.join(ROOT, "Money02", "data", "lhb", "lhb_detail.parquet")
OUT_DIR = os.path.join(ROOT, "results", "lhb_thermo")

# parquet column names (Money02 LHB detail face, Chinese as-collected)
COL_DAY = "上榜日"
COL_CODE = "代码"
COL_NETBUY = "龙虎榜净买额"
COL_BUY = "龙虎榜买入额"
COL_SELL = "龙虎榜卖出额"
COL_AMT = "龙虎榜成交额"
COL_MKT_AMT = "市场总成交额"

FAMOUS_DAYS = [
    "2008-04-24", "2015-06-15", "2015-06-19", "2015-08-24", "2016-01-04",
    "2019-02-25", "2020-02-03", "2020-07-06", "2024-02-05", "2024-09-24",
    "2024-09-30", "2024-10-08", "2025-04-07", "2025-06-11", "2026-01-05",
    "2026-09-18", "2026-09-22", "2026-09-30",
]


def aggregate(df):
    """Pure aggregation core: (deduped) panel -> daily emotion face.

    Deterministic, no I/O -- shared by run mode and the hermetic selftest.
    """
    d = df.drop_duplicates(subset=[COL_CODE, COL_DAY]).copy()
    dropped = int(len(df) - len(d))
    d[COL_DAY] = d[COL_DAY].astype(str)
    g = d.groupby(COL_DAY)
    daily = pd.DataFrame({
        "n_lhb": g[COL_CODE].nunique(),
        "buy_sum": g[COL_BUY].sum(),
        "sell_sum": g[COL_SELL].sum(),
        "netbuy_sum": g[COL_NETBUY].sum(),
        "med_netbuy": g[COL_NETBUY].median(),
        "lhb_amt_sum": g[COL_AMT].sum(),
        "mkt_amt_sum": g[COL_MKT_AMT].sum(),
    })
    # raw listing entries per day (one row per listing criterion; the
    # multi-reason structure is surfaced, not hidden, by the dedup above)
    raw_rows = df.copy()
    raw_rows[COL_DAY] = raw_rows[COL_DAY].astype(str)
    daily["n_rows_raw"] = raw_rows.groupby(COL_DAY).size()
    pos = d[d[COL_NETBUY] > 0].groupby(COL_DAY)[COL_CODE].nunique()
    daily["netbuy_pos_share"] = (pos / daily["n_lhb"]).fillna(0.0)
    with np.errstate(invalid="ignore", divide="ignore"):
        daily["netbuy_intensity"] = (
            daily["netbuy_sum"] / daily["mkt_amt_sum"]).replace([np.inf, -np.inf], np.nan)
        daily["amt_share"] = (
            daily["lhb_amt_sum"] / daily["mkt_amt_sum"]).replace([np.inf, -np.inf], np.nan)
    daily = daily.sort_index().reset_index().rename(columns={COL_DAY: "date"})
    return daily, dropped


def build_summary(daily, dropped, panel_days, panel_min, panel_max):
    d = daily.set_index(pd.to_datetime(daily["date"]))
    ycols = ["n_lhb", "netbuy_sum", "netbuy_pos_share", "med_netbuy",
             "netbuy_intensity", "amt_share"]
    yearly = d.groupby(d.index.year)[ycols].mean().round(6)
    fam = {}
    for f in FAMOUS_DAYS:
        fam[f] = daily.loc[daily["date"] == f].iloc[0].to_dict() if (daily["date"] == f).any() else None
    top_n = d["n_lhb"].nlargest(10)
    top_nb = d["netbuy_sum"].nlargest(10)
    low_nb = d["netbuy_sum"].nsmallest(10)
    return {
        "meta": {
            "universe": "Money02/data/lhb/lhb_detail.parquet (akshare LHB detail, as-collected)",
            "panel_span": [panel_min, panel_max],
            "n_panel_rows": int(panel_days),
            "dedup_dropped_rows": dropped,
            "dedup_rule": "keep-first row per (code, day); multi-criterion "
                          "listings carry per-reason aggregation windows "
                          "(sum would double-count mixed windows); raw "
                          "entry count surfaced as n_rows_raw",
            "units": "CNY yuan (元) for all money faces",
            "built_by": "bm-a OS iteration loop r946 (explore queue E5 slice-1)",
            "law_ref": "O-20260928-1522 domestic-style priority / E5 row / "
                       "REGIME_THERMO_V1 descriptive-face precedent",
            "demarcation": "r680+r681 LHB follow-family (event-level stock "
                           "picking) judged-negative CLOSED; this face is "
                           "market-level aggregate emotion description only",
            "exploration_label": "ALL descriptive, zero criterion claims, "
                                 "zero thresholds invented; forward-return "
                                 "validation deferred to independent prereg",
        },
        "n_days": int(len(d)),
        "yearly_mean": {str(k): v for k, v in yearly.to_dict().items()},
        "famous_days": fam,
        "top10_n_lhb": {str(k.date()): int(v) for k, v in top_n.items()},
        "top10_netbuy_sum": {str(k.date()): float(v) for k, v in top_nb.items()},
        "bottom10_netbuy_sum": {str(k.date()): float(v) for k, v in low_nb.items()},
    }


def run(panel_path=PANEL, out_dir=OUT_DIR):
    if not os.path.isfile(panel_path):
        # lane/data guard (r824 thermo precedent): Money02 is bm-a-hosted
        print("lhb_thermo_build: Money02 LHB panel absent on this machine -- "
              "stdout-only honest no-op")
        return 0
    df = pd.read_parquet(panel_path)
    panel_min = str(df[COL_DAY].min())
    panel_max = str(df[COL_DAY].max())
    daily, dropped = aggregate(df)
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, "lhb_thermo_daily.csv")
    json_path = os.path.join(out_dir, "lhb_thermo_summary.json")
    daily.to_csv(csv_path, index=False, encoding="utf-8")
    summary = build_summary(daily, dropped, len(df), panel_min, panel_max)
    with io.open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1, default=str)
    print("lhb_thermo_build: %d days (%s..%s), dedup dropped %d rows -> %s"
          % (len(daily), daily["date"].iloc[0], daily["date"].iloc[-1],
             dropped, out_dir))
    print(daily.tail(5).to_string(index=False))
    return 0


def _selftest():
    """Hermetic offline battery: aggregation math + determinism + guards."""
    ok = 0
    fails = []

    def check(name, cond):
        nonlocal ok
        if cond:
            ok += 1
            print("[PASS] lhb_thermo selftest: %s" % name)
        else:
            fails.append(name)
            print("[FAIL] lhb_thermo selftest: %s" % name)

    # synthetic panel: 2 days, 5 code-days, one duplicate row to exercise dedup
    rows = [
        # code, name, jiedu, day,  close, chg, netbuy, buy, sell, amt, mkt_amt
        (1, "A", "x", "2024-01-02", 10.0, 0.1, 100.0, 300.0, 200.0, 500.0, 5000.0),
        (2, "B", "x", "2024-01-02", 20.0, -0.1, -50.0, 100.0, 150.0, 250.0, 4000.0),
        (3, "C", "x", "2024-01-02", 30.0, 0.05, 80.0, 200.0, 120.0, 320.0, 8000.0),
        (4, "D", "x", "2024-01-03", 40.0, 0.2, 200.0, 400.0, 200.0, 600.0, 3000.0),
        (5, "E", "x", "2024-01-03", 50.0, -0.2, -60.0, 70.0, 130.0, 200.0, 6000.0),
        (1, "A", "x", "2024-01-02", 10.0, 0.1, 100.0, 300.0, 200.0, 500.0, 5000.0),  # dup
    ]
    cols = [COL_CODE, "名称", "解读", COL_DAY, "收盘价", "涨跌幅",
            COL_NETBUY, COL_BUY, COL_SELL, COL_AMT, COL_MKT_AMT]
    df = pd.DataFrame(rows, columns=cols)

    daily, dropped = aggregate(df)
    check("dedup_drops_exact_duplicate", dropped == 1)
    check("day_count", list(daily["date"]) == ["2024-01-02", "2024-01-03"])
    r1, r2 = daily.iloc[0], daily.iloc[1]
    check("n_lhb_per_day", int(r1["n_lhb"]) == 3 and int(r2["n_lhb"]) == 2)
    check("n_rows_raw_multireason_visible",
          int(r1["n_rows_raw"]) == 4 and int(r2["n_rows_raw"]) == 2)
    check("netbuy_sum", float(r1["netbuy_sum"]) == 130.0 and float(r2["netbuy_sum"]) == 140.0)
    check("buy_sell_sums", float(r1["buy_sum"]) == 600.0 and float(r1["sell_sum"]) == 470.0)
    check("med_netbuy", float(r1["med_netbuy"]) == 80.0)
    check("pos_share", abs(float(r1["netbuy_pos_share"]) - 2.0 / 3.0) < 1e-12
          and float(r2["netbuy_pos_share"]) == 0.5)
    check("intensity", abs(float(r1["netbuy_intensity"]) - 130.0 / 17000.0) < 1e-12)
    check("amt_share", abs(float(r2["amt_share"]) - 800.0 / 9000.0) < 1e-12)

    # determinism: double aggregate -> identical frame bytes
    d2, _ = aggregate(df)
    check("determinism_double_run",
          daily.reset_index(drop=True).equals(d2.reset_index(drop=True)))

    # no-op guard: absent panel path -> run() honest no-op rc0 without writing
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        rc = run(panel_path=os.path.join(td, "absent.parquet"),
                 out_dir=os.path.join(td, "out"))
        check("absent_panel_noop_rc0", rc == 0 and not os.listdir(td))

    # end-to-end on synthetic file: csv+json land with expected faces
    with tempfile.TemporaryDirectory() as td:
        pp = os.path.join(td, "panel.parquet")
        df.to_parquet(pp)
        out = os.path.join(td, "out")
        rc = run(panel_path=pp, out_dir=out)
        daily_rt = pd.read_csv(os.path.join(out, "lhb_thermo_daily.csv"))
        with io.open(os.path.join(out, "lhb_thermo_summary.json"), encoding="utf-8") as f:
            s = json.load(f)
        check("run_rc0_products", rc == 0 and len(daily_rt) == 2
              and s["n_days"] == 2 and s["meta"]["dedup_dropped_rows"] == 1)
        # rerun idempotency: byte-identical rebuild on unchanged panel
        csv_b = open(os.path.join(out, "lhb_thermo_daily.csv"), "rb").read()
        jsn_b = open(os.path.join(out, "lhb_thermo_summary.json"), "rb").read()
        run(panel_path=pp, out_dir=out)
        check("idempotent_byte_identical",
              open(os.path.join(out, "lhb_thermo_daily.csv"), "rb").read() == csv_b
              and open(os.path.join(out, "lhb_thermo_summary.json"), "rb").read() == jsn_b)

    print("Summary: %d/%d PASS, %d FAIL" % (ok, ok + len(fails), len(fails)))
    return 0 if not fails else 1


def main(argv):
    if len(argv) > 1 and argv[1] == "selftest":
        return _selftest()
    try:
        return run()
    except Exception as exc:  # mechanism fault -> honest exit 2
        print("lhb_thermo_build: mechanism fault: %r" % (exc,))
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
