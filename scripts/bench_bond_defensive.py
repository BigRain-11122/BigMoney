"""Bench cell 4: is a bond-futures sleeve a better defensive leg than cash?

The question (four-gate test (b): how big, and with what)
---------------------------------------------------------
The book's defensive half is cash + treasury ETFs earning ~1.77%/yr on GC001.
Bond futures are the same duration exposure with margin efficiency and no
funding of the full notional. If T/TF/TS held long, vol-targeted, delivers
equity-crash protection at a higher carry than cash, the defensive leg has a
better instrument; if it only adds a correlated drawdown, it does not.

What is measured
----------------
  bond arm   T/TF/TS long, equal risk, 6% vol target, weekly re-strike,
             1.5bp/side, hold to the end
  cash arm   the published repo vehicle rate (read from
             results/etf_book_idle_cash.json; never re-typed)
  equity     CSI300 daily, for correlation and for the bear years

Criteria frozen before the run:
  H1  bond arm net annualised >= 3.0%
  H2  daily correlation with CSI300 <= 0.25 (a hedge that moves with equities
      is not a hedge)
  H3  positive in BOTH of the two worst CSI300 calendar years in the sample
  H4  drop the best calendar year, still >= 2.0%/yr
  H5  beats the cash vehicle by >= 1.0pp/yr
  GO only if all five pass -- and even then the answer is "use it as the
  defensive leg", not "it is a strategy".
"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bench_core as bc  # noqa: E402

OUT_JSON = os.path.join(bc.RESULTS, "bench_bond_defensive.json")
OUT_MD = os.path.join(bc.RESEARCH, "BENCH-BOND-DEFENSIVE.md")
IDLE_CASH = os.path.join(bc.RESULTS, "etf_book_idle_cash.json")

LEGS = ["T", "TF", "TS"]
TARGET_VOL = 0.06
COST_BP_SIDE = 1.5
H1_PCT = 3.0
H2_CORR = 0.25
H4_PCT = 2.0
H5_MARGIN_PP = 1.0


def cash_rate():
    """GC001's own quoted rate (annualised %), median of the last 250 bars.

    Read from the repo lane instead of re-typing a number from a page: the same
    cash vehicle the desk already prices. None when the lane is unreadable.
    """
    path = os.path.join(bc.DATA, "repo_daily", "GC001.csv")
    if not os.path.exists(path):
        return None, "data/repo_daily/GC001.csv missing"
    try:
        df = pd.read_csv(path)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").tail(250)
        rate = float(df["close"].median())
    except Exception as e:
        return None, f"unreadable: {e}"
    if not (0.0 < rate < 30.0):
        return None, f"implausible GC001 median {rate}"
    return rate, "data/repo_daily/GC001.csv median(last 250 bars)"


def run():
    bc.weight_priority()
    panel = bc.load_futures_products(LEGS)
    if len(panel) < 3:
        return {"ok": False, "error": f"need T/TF/TS, got {sorted(panel)}"}

    dates, closes, rets, vols = bc.align_futures(panel)
    sig = {c: pd.Series(1.0, index=s.index).where(s.notna()) for c, s in closes.items()}
    pos, live = bc.vol_weighted_positions(sig, vols, target_vol=TARGET_VOL)
    frame = pd.DataFrame(rets).reindex(pos.index)
    gross = (pos.shift(1) * frame).sum(axis=1, min_count=1)
    turn = (pos - pos.shift(1)).abs().sum(axis=1).fillna(0.0)
    net = (gross - turn * COST_BP_SIDE / 10000.0).fillna(0.0)

    start = pd.Timestamp("2017-01-01")
    net = net[net.index >= start]

    csi = bc.load_index_close("sh000300")
    csi_r = csi.reindex(net.index).pct_change() if csi is not None else None

    corr = None
    if csi_r is not None:
        pair = pd.concat([net, csi_r], axis=1).dropna()
        if len(pair) > 100 and pair.iloc[:, 0].std() > 0 and pair.iloc[:, 1].std() > 0:
            corr = round(float(pair.iloc[:, 0].corr(pair.iloc[:, 1])), 3)

    reading = bc.split_perf(net.values, net.index)

    # the two worst equity years in the sample
    bear_years = []
    bond_years = reading["full"].get("years", {})
    bear_table = {}
    if csi_r is not None:
        yrs = csi_r.index.year
        eq_map = {}
        for y in sorted(set(yrs)):
            sel = yrs == y
            if sel.sum() <= 100:
                continue
            eq_map[int(y)] = round(float(np.expm1(np.log1p(csi_r[sel]).sum()) * 100), 2)
        bear_years = sorted(eq_map, key=lambda k: eq_map[k])[:2]
        bear_table = {str(y): {"csi300_pct": eq_map[y],
                               "bond_pct": bond_years.get(y, bond_years.get(str(y)))}
                      for y in bear_years}

    rate, rate_src = cash_rate()
    checks = {
        "H1_net_ge_3pct": bool(reading["full"]["ann_pct"] is not None
                               and reading["full"]["ann_pct"] >= H1_PCT),
        "H2_corr_le_0.25": bool(corr is not None and corr <= H2_CORR),
        "H3_positive_in_both_bear_years": bool(
            bear_table and all(v["bond_pct"] is not None and v["bond_pct"] > 0
                               for v in bear_table.values())),
        "H4_drop_best_ge_2pct": bool(
            reading["full"]["drop_best_year_ann_pct"] is not None
            and reading["full"]["drop_best_year_ann_pct"] >= H4_PCT),
        "H5_beats_cash_by_1pp": (None if rate is None or reading["full"]["ann_pct"] is None
                                 else bool(reading["full"]["ann_pct"] >= rate + H5_MARGIN_PP)),
    }

    payload = {
        "cell": "bond_defensive",
        "generated": pd.Timestamp.now(tz="Asia/Shanghai").isoformat(timespec="seconds"),
        "evidence_cutoff": str(net.index[-1].date()),
        "legs": sorted(panel),
        "criteria": {"H1_pct": H1_PCT, "H2_corr": H2_CORR, "H4_pct": H4_PCT,
                     "H5_margin_pp": H5_MARGIN_PP, "target_vol": TARGET_VOL,
                     "cost_bp_side": COST_BP_SIDE, "cash_rate_source": rate_src},
        "bond_arm": {"reading": reading["full"], "is_before_2024": reading["is"],
                     "oos_2024_after": reading["oos"],
                     "first_half_ann_pct": reading.get("first_half_ann_pct"),
                     "second_half_ann_pct": reading.get("second_half_ann_pct"),
                     "turnover_per_year": round(float(turn.sum()) * bc.TRADING_DAYS
                                                / max(len(turn), 1), 2)},
        "cash_rate_pct": rate,
        "corr_csi300": corr,
        "bear_year_table": bear_table,
        "verdict": bc.verdict_of(checks),
        "checks": checks,
    }
    os.makedirs(bc.BENCH_OUT, exist_ok=True)
    bc.write_json(OUT_JSON, payload)

    f = reading["full"]
    md = [
        "# 国债期货当防守腿（bench cell 4）", "",
        f"evidence cutoff {payload['evidence_cutoff']} | generated {payload['generated']}",
        "",
        f"**判决 {payload['verdict']}**",
        "",
        f"- 债券腿：{bc.fmt_pct(f['ann_pct'])}/年 · 夏普 {bc.fmt_num(f['sharpe'])} · "
        f"回撤 {bc.fmt_pct(f['mdd_pct'])} · 样本外 {bc.fmt_pct(reading['oos']['ann_pct'])}",
        f"- 现金腿（{rate_src}）：{bc.fmt_pct(rate)}/年",
        f"- 与沪深300日相关：{bc.fmt_num(corr)}",
        f"- 权益最差两年：{bear_table or '不可算'}",
        "",
        f"判据：{json.dumps(checks, ensure_ascii=False)}",
        "",
        "## 这次没有回答的问题", "",
        "- 没有做保证金占用与移仓成本的全部口径（只按 1.5bp/边计）。",
        "- 没有把现券/存单与国债期货做合成比较（本地无现券曲线）。",
    ]
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(md) + "\n")

    print(json.dumps({"ok": True, "verdict": payload["verdict"], "checks": checks,
                      "ann_pct": f["ann_pct"], "sharpe": f["sharpe"],
                      "corr_csi300": corr, "cash_rate_pct": rate}, ensure_ascii=False, indent=1))
    return payload


if __name__ == "__main__":
    res = run()
    sys.exit(0 if isinstance(res, dict) and res.get("ok", True) else 1)
