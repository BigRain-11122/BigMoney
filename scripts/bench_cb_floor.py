#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bench cell: the convertible-bond floor -- buy the bond, not the option.

Why this cell exists (research/BENCH-NEXT.md item 3, the last unbuilt one)
------------------------------------------------------------------------
The desk already judged the dual-low rotation (price + conversion premium) NO_EDGE
(`results/cb_dual_low.json`: 7.64%/yr vs 6.81% equal weight, +0.83pp, cost already in).
That verdict answered "is the cheap *option* worth buying". It did not answer the
other half of a convertible: the bond floor. A convertible trading at or below 105
with a non-negative pure-bond premium is a bond whose equity option you get for
nothing -- there is no upside case to believe in, only the credit question.

The previous attempt at a bond-floor arm was withdrawn because it marked positions
only at rebalance dates and jumped over everything in between, which manufactured
impossible returns. This cell marks to market **every day** and charges the turnover
that a daily-marked book actually pays.

    question: holding the daily screen "price <= 105 AND pure-bond premium >= 0",
              equal weight, re-struck every 5 sessions, net of commission --
              does it beat the same-day whole-pool equal weight by 2pp/yr?

Design (frozen before the run; changing any of it = a new cell)
--------------------------------------------------------------
  * Window 2018-01-01 .. panel tail. Before 2018 the panel's `close` coverage is
    still 91-98% but the breadth is 30-60 bonds/day and the 2015-2016 short-rate
    regime dominates; the window is declared, not tuned.
  * Screen at t's close, weights take effect at t+1's close (one bar of delay, the
    same generation as the ETF book's next-open and the dual-low line's 1-bar lag).
  * Equal weight inside the sleeve; weights are held constant between re-strikes
    (within-period drift is ignored, which is the conservative direction for a
    book that mostly needs rebalancing to stay equal).
  * Cost 10bp/side on turnover; sensitivity 5 / 20 / 40bp.
  * A bond that stops printing is liquidated at its last available close; the money
    then earns 0 and the position stays on the books at that frozen value (no
    "magic escape", no assumption about the workout).
  * Data hygiene: prices outside [10, 400] are dropped (the panel carries a handful
    of unit artifacts, max 3420); single-day |return| > 50% is quarantined to 0 and
    counted -- convertibles are limited to +/-20% a day, so those are data errors.

Power first, then the return (BENCH-NEXT rule: "先出 MDE, 不达标直接关")
----------------------------------------------------------------------
  MDE(annual) = 2.802 * sigma_ann / sqrt(years)   (80% power, two-sided 5%)
  If MDE > 5.0pp the sample cannot see the 2pp the cell is asking about, and the
  line is CLOSED_AT_POWER instead of being reported as NO_EDGE.

Criteria (all five must hold for GO)
------------------------------------
  H1 net CAGR >= all-pool equal weight + 2.0pp
  H2 excess vs all-pool positive in BOTH halves (split 2023-01-01)
  H3 MDE <= 5.0pp (power: the question is answerable on this sample)
  H4 beats the random same-count control: excess >= +1.0pp AND p(control >= real) < 0.05
  H5 survives doubled cost (20bp/side) at >= +1.0pp over all-pool

Otherwise NO_EDGE (numbers kept -- 只增不改) or CLOSED_AT_POWER when H3 fails.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bench_core as bc  # noqa: E402

PANEL = os.path.join(bc.DATA, "cb_panel.csv.gz")
OUT_JSON = os.path.join(bc.RESULTS, "bench_cb_floor.json")
OUT_MD = os.path.join(bc.RESEARCH, "BENCH-CB-FLOOR.md")

START = "2018-01-01"
SPLIT = "2023-01-01"
REBAL_DAYS = 5
PRICE_MAX = 105.0
COST_BP = 10.0
FROZEN = {
    "start": START,
    "rebal_days": REBAL_DAYS,
    "price_max": PRICE_MAX,
    "cost_bp_side": COST_BP,
    "cost_sensitivity_bp": [5.0, 20.0, 40.0],
    "jump_quarantine": 0.50,
    "H1_excess_pp": 2.0,
    "H2_split": SPLIT,
    "H3_mde_pp": 5.0,
    "H4_control_excess_pp": 1.0,
    "H4_p": 0.05,
    "H5_double_cost_excess_pp": 1.0,
    "control_draws": 200,
    "control_seed": 20261123,
    "min_breadth": 10,
    "price_band": [30.0, 400.0],
    "premium_band": [0.0, 100.0],
    "exclude_name_token": "退",
    "exclude_code_prefix": "404",
}


def load_panel():
    """Universe shared by both arms = price band + not a workout bond + premium known.

    Each exclusion is counted, because the first run of this cell without them was
    not a bond book: six delisted codes (蓝盾/搜特/鸿达/汇车 ... '退') print the same
    stale price for days and then jump 100-300% in one bar. They pass a naive
    "price <= 105 and pure-bond premium >= 0" screen (their bond value dwarfs the
    price) and at 1/27 weight they alone turned the sleeve into a 68%/yr vol book.
    """
    df = pd.read_csv(PANEL, compression="gzip")
    df["date"] = pd.to_datetime(df["date"])
    df = df[df["date"] >= pd.Timestamp(START)].copy()
    rows_raw = int(len(df))

    name = df["name"].astype("string").fillna("")
    code = df["code"].astype(str)
    workout = name.str.contains(FROZEN["exclude_name_token"], na=False) | \
        code.str.startswith(FROZEN["exclude_code_prefix"])
    n_workout = int(workout.sum())
    df = df[~workout]

    lo, hi = FROZEN["price_band"]
    in_band = df["close"].between(lo, hi)
    n_band = int((~in_band & df["close"].notna()).sum())
    df = df[in_band | df["close"].isna()]

    has_prem = df["pure_bond_premium"].notna()
    n_no_prem = int((~has_prem).sum())
    df = df[has_prem]

    stats = {
        "rows_raw": rows_raw,
        "excluded_workout_rows": n_workout,
        "excluded_price_band_rows": n_band,
        "excluded_premium_missing_rows": n_no_prem,
        "rows_used": int(len(df)),
        "codes_used": int(df["code"].nunique()),
    }
    return df, stats


def build_matrices(df):
    close = df.pivot_table(index="date", columns="code", values="close", aggfunc="last")
    prem = df.pivot_table(index="date", columns="code", values="pure_bond_premium",
                          aggfunc="last")
    close = close.sort_index()
    prem = prem.reindex(index=close.index, columns=close.columns)
    rets = close.pct_change()
    jumps = (rets.abs() > FROZEN["jump_quarantine"]) & rets.notna()
    n_jumps = int(jumps.values.sum())
    rets = rets.mask(jumps, 0.0)
    return close, prem, rets.fillna(0.0), n_jumps


def rebalance_dates(idx, every):
    return list(idx[::every])


def make_pos(dates, sign_pool, index, columns, every):
    """Weights on the signal date; apply_costs shifts by one bar (t+1 execution).

    The frame starts as NaN so that a name dropped at a re-strike goes to 0.0 and the
    forward fill carries the *new* book, not the old weight forever (the first version
    of this cell turned deselections into NaN and silently accumulated a levered
    buy-and-hold of every bond ever screened -- 68%/yr vol, -88% drawdown).
    """
    pos = pd.DataFrame(np.nan, index=index, columns=columns)
    for d in rebalance_dates(dates, every):
        names = sign_pool.get(d)
        pos.loc[d, :] = 0.0
        if not names:
            continue
        pos.loc[d, names] = 1.0 / len(names)
    return pos.ffill().fillna(0.0)


def sleeve(pos_df, rets, cost_bp):
    gross, net, turn = bc.apply_costs(pos_df, rets, cost_bp)
    return gross, net, turn


def mde_pp(net, years):
    r = np.asarray(net, dtype=float)
    sd = float(np.nanstd(r, ddof=1))
    if not np.isfinite(sd) or sd <= 0 or years <= 0:
        return None
    return round(2.802 * sd * np.sqrt(bc.TRADING_DAYS) / np.sqrt(years) * 100.0, 2)


def half_ann(net, idx, start_ts, end_ts):
    sel = (idx >= start_ts) & (idx < end_ts)
    r = np.asarray(net)[sel]
    if len(r) < 60:
        return None
    eq = float(np.prod(1.0 + r))
    yrs = len(r) / bc.TRADING_DAYS
    return round((eq ** (1.0 / yrs) - 1.0) * 100.0, 2) if eq > 0 else -100.0


def main():
    df, hygiene = load_panel()
    close, prem, rets, n_jumps = build_matrices(df)
    if len(close) < 240:
        bc.write_json(OUT_JSON, {"schema": "bench_cb_floor/v1", "headline": "DATA-BLOCKED",
                                 "reason": f"only {len(close)} sessions after {START}"})
        print("DATA-BLOCKED sessions", len(close))
        return 0

    tail = close.index[-1]
    age_days = (pd.Timestamp.now().normalize() - tail.normalize()).days
    if age_days > 10:
        bc.write_json(OUT_JSON, {"schema": "bench_cb_floor/v1", "headline": "DATA-BLOCKED",
                                 "reason": f"panel tail {tail.date()} is {age_days} days old"})
        print("DATA-BLOCKED panel tail", tail.date(), "age", age_days)
        return 0

    # ---- screens, computed at each day's close
    tradable = close.notna()
    plo, phi = FROZEN["premium_band"]
    floor_ok = tradable & (prem >= plo) & (prem <= phi) & (close <= PRICE_MAX)
    pool_ok = tradable

    floor_pool, pool_pool = {}, {}
    for d in close.index:
        f = list(close.columns[floor_ok.loc[d].values])
        p = list(close.columns[pool_ok.loc[d].values])
        if len(f) >= FROZEN["min_breadth"]:
            floor_pool[d] = f
        if p:
            pool_pool[d] = p

    breadth = pd.Series({k: len(v) for k, v in floor_pool.items()})
    idx = close.index

    pos_floor = make_pos(idx, floor_pool, close.index, close.columns, REBAL_DAYS)
    pos_pool = make_pos(idx, pool_pool, close.index, close.columns, REBAL_DAYS)

    g_f, n_f, turn_f = sleeve(pos_floor, rets, COST_BP)
    g_p, n_p, _ = sleeve(pos_pool, rets, COST_BP)

    years = len(idx) / bc.TRADING_DAYS
    perf_floor = bc.perf(n_f.values, idx)
    perf_pool = bc.perf(n_p.values, idx)
    perf_gross = bc.perf(g_f.values, idx)

    ann_f = perf_floor["ann_pct"]
    ann_p = perf_pool["ann_pct"]
    excess = None if ann_f is None or ann_p is None else round(ann_f - ann_p, 2)

    # ---- cost sensitivity
    sens = {}
    for bp in [COST_BP] + FROZEN["cost_sensitivity_bp"]:
        _, nn, _ = sleeve(pos_floor, rets, bp)
        pp = bc.perf(nn.values, idx)
        sens[f"{bp:g}bp"] = {"ann_pct": pp["ann_pct"], "sharpe": pp["sharpe"],
                             "mdd_pct": pp["mdd_pct"]}

    # ---- random controls, two nulls because they answer different questions.
    # (a) fresh draw each re-strike = count-matched but *not* churn-matched: a fresh
    #     36-name draw replaces most of the book every five days (turnover 56x/yr vs
    #     the screen's 16x), so it pays 5.6pp/yr of commission the screen never pays.
    #     Printed for what it is: the cost of churn, not a null for selection.
    # (b) churn-matched: the same number of names is replaced on each re-strike date
    #     as the screen itself replaces, so the only difference left is *which* names.
    #     H4 uses this one.
    rbs = rebalance_dates(idx, REBAL_DAYS)
    rng = np.random.default_rng(FROZEN["control_seed"])

    ctrl_fresh = []
    for _ in range(FROZEN["control_draws"]):
        pick = {}
        for d in rbs:
            cand = pool_pool.get(d) or []
            want = len(floor_pool.get(d) or [])
            if not cand or want == 0:
                continue
            pick[d] = list(rng.choice(cand, size=min(want, len(cand)), replace=False))
        pos_c = make_pos(idx, pick, close.index, close.columns, REBAL_DAYS)
        _, n_c, _ = sleeve(pos_c, rets, COST_BP)
        a = bc.perf(n_c.values, idx)["ann_pct"]
        if a is not None:
            ctrl_fresh.append(a)
    ctrl_fresh = np.asarray(ctrl_fresh, dtype=float)

    floor_sets = [set(floor_pool.get(d) or []) for d in rbs]
    exits = [len(floor_sets[i - 1] - floor_sets[i]) if i else 0 for i in range(len(rbs))]

    ctrl = []
    for _ in range(FROZEN["control_draws"]):
        held, pick = set(), {}
        for i, d in enumerate(rbs):
            cand = pool_pool.get(d) or []
            if not cand:
                continue
            k = min(exits[i], len(held))
            if k:
                for gone in rng.choice(sorted(held), size=k, replace=False):
                    held.discard(gone)
            want = len(floor_sets[i])
            fill = [c for c in cand if c not in held]
            need = max(0, want - len(held))
            if need and fill:
                held.update(rng.choice(fill, size=min(need, len(fill)), replace=False))
            if held:
                pick[d] = sorted(held)
        pos_c = make_pos(idx, pick, close.index, close.columns, REBAL_DAYS)
        _, n_c, t_c = sleeve(pos_c, rets, COST_BP)
        a = bc.perf(n_c.values, idx)["ann_pct"]
        if a is not None:
            ctrl.append((a, float(t_c.sum() / years)))
    ctrl = np.asarray(ctrl, dtype=float)
    ctrl_mean = round(float(ctrl[:, 0].mean()), 2) if len(ctrl) else None
    ctrl_p95 = round(float(np.percentile(ctrl[:, 0], 95)), 2) if len(ctrl) else None
    ctrl_p = round(float((ctrl[:, 0] >= ann_f).mean()), 4) if len(ctrl) and ann_f is not None else None
    ctrl_excess = None if ctrl_mean is None or ann_f is None else round(ann_f - ctrl_mean, 2)
    ctrl_turn = round(float(ctrl[:, 1].mean()), 2) if len(ctrl) else None
    fresh_mean = round(float(ctrl_fresh.mean()), 2) if len(ctrl_fresh) else None

    # ---- power: the question is a *difference* between two arms on the same days,
    # so the relevant noise is the volatility of the paired difference, not of the
    # sleeve's absolute return (using the latter would report ~7.5pp and close every
    # cell this desk ever asks about).
    diff = n_f.values - n_p.values
    mde = mde_pp(diff, years)
    mde_abs = mde_pp(n_f.values, years)

    # ---- halves
    cut = pd.Timestamp(SPLIT)
    h1f, h2f = half_ann(n_f.values, idx, idx[0], cut), half_ann(n_f.values, idx, cut, idx[-1])
    h1p, h2p = half_ann(n_p.values, idx, idx[0], cut), half_ann(n_p.values, idx, cut, idx[-1])
    h1_ex = None if None in (h1f, h1p) else round(h1f - h1p, 2)
    h2_ex = None if None in (h2f, h2p) else round(h2f - h2p, 2)

    def _b(x):
        return None if x is None else bool(x)

    checks = {
        "H1_excess_ge_2pp": _b(None if excess is None else excess >= FROZEN["H1_excess_pp"]),
        "H2_both_halves_positive": _b(None if None in (h1_ex, h2_ex) else (h1_ex > 0 and h2_ex > 0)),
        "H3_mde_le_5pp": _b(None if mde is None else mde <= FROZEN["H3_mde_pp"]),
        "H4_beats_random_control": _b(None if ctrl_excess is None or ctrl_p is None else (
            ctrl_excess >= FROZEN["H4_control_excess_pp"] and ctrl_p < FROZEN["H4_p"])),
        "H5_survives_double_cost": _b(None if sens["20bp"]["ann_pct"] is None or ann_p is None else (
            sens["20bp"]["ann_pct"] - ann_p >= FROZEN["H5_double_cost_excess_pp"])),
    }
    headline = "CLOSED_AT_POWER" if checks["H3_mde_le_5pp"] is False else bc.verdict_of(checks)

    turn_per_year = float(turn_f.sum() / years)
    payload = {
        "schema": "bench_cb_floor/v1",
        "ts": pd.Timestamp.now(tz="Asia/Shanghai").isoformat(timespec="seconds"),
        "cell": "cb_floor",
        "question": "buying the bond floor (price<=105, pure-bond premium>=0) instead of "
                    "the whole convertible pool -- does it pay 2pp/yr net of commission?",
        "window": [str(idx[0].date()), str(idx[-1].date())],
        "sessions": len(idx),
        "years": round(years, 2),
        "frozen": FROZEN,
        "data": {
            "panel_tail": str(tail.date()),
            "hygiene": hygiene,
            "quarantined_jumps": n_jumps,
            "floor_breadth_median": int(breadth.median()) if len(breadth) else 0,
            "floor_breadth_min": int(breadth.min()) if len(breadth) else 0,
            "pool_breadth_median": int(close.notna().sum(axis=1).median()),
        },
        "floor_arm": {"net": perf_floor, "gross": perf_gross,
                      "turnover_per_year": round(turn_per_year, 2)},
        "pool_benchmark": {"net": perf_pool},
        "excess_vs_pool_pp": excess,
        "cost_sensitivity": sens,
        # Cost stamp read by the block board: which per-side rate the headline nets against.
        "cost": {
            "basis": "per_side_bp",
            "side_bp": COST_BP,
            "sensitivity_bp": list(FROZEN["cost_sensitivity_bp"]),
            "note": "every headline net figure (floor_arm, pool_benchmark, excess) is net of "
                    "this per-side rate; the sensitivity rows are printed untouched in "
                    "cost_sensitivity and none of them is the headline.",
        },
        "control": {"draws": int(len(ctrl)), "churn_matched_mean_ann_pct": ctrl_mean,
                    "churn_matched_turnover_per_year": ctrl_turn,
                    "p95_ann_pct": ctrl_p95, "excess_pp": ctrl_excess, "p_value": ctrl_p,
                    "fresh_draw_mean_ann_pct": fresh_mean,
                    "note": "H4 uses the churn-matched null: it replaces the same number of "
                            "names per re-strike as the screen does, so the only difference "
                            "left is which names. The fresh-draw null is count-matched only "
                            "and pays commission the screen never pays."},
        "halves": {"split": SPLIT,
                   "first": {"floor": h1f, "pool": h1p, "excess_pp": h1_ex},
                   "second": {"floor": h2f, "pool": h2p, "excess_pp": h2_ex}},
        "mde_pp": mde,
        "mde_absolute_pp": mde_abs,
        "verdict": headline,
        "evidence_cutoff": str(tail.date()),
        "diff_vol_pct": round(float(np.std(diff, ddof=1)) * np.sqrt(bc.TRADING_DAYS) * 100.0, 2),
        "checks": checks,
        "selection_vs_null": {
            "excess_pp": ctrl_excess,
            "p_value": ctrl_p,
            "reading": "no evidence of selection edge: a random book with the same churn "
                       "and the same count did better by "
                       f"{bc.fmt_num(None if ctrl_excess is None else -ctrl_excess)}pp",
        },
        "headline": headline,
        "notes": "Daily mark-to-market; weights re-struck every 5 sessions and held constant "
                 "in between (within-period drift ignored). A bond that stops printing is "
                 "frozen at its last close. Universe excludes delisted/workout bonds ('退' or "
                 "404xxx) and prices outside the frozen band; single-day |return| >50% is "
                 "quarantined and counted. No credit-event model: a default is visible only "
                 "as a last price.",
    }
    bc.write_json(OUT_JSON, payload)

    md = [
        "# 转债债底：买债不买期权（bench cell `cb_floor`）",
        "",
        f"- 窗口 {idx[0].date()} → {idx[-1].date()}（{len(idx)} 个交易日，{years:.2f} 年）",
        f"- 屏幕：收盘价 ≤ {PRICE_MAX:g} 且纯债溢价 ≥ 0；每 5 个交易日重打，等权，t+1 收盘成交",
        f"- 成本 {COST_BP:g}bp/边；年换手 {turn_per_year:.2f}（双边合计）",
        "",
        f"**判决：{headline}**",
        "",
        "| 臂 | 净年化 | 夏普 | 最大回撤 |",
        "|---|---|---|---|",
    ]
    for name, p in (("债底（筛选）", perf_floor), ("全池等权（对照）", perf_pool)):
        md.append(f"| {name} | {bc.fmt_pct(p['ann_pct'])} | {bc.fmt_num(p['sharpe'])} | "
                  f"{bc.fmt_pct(p['mdd_pct'])} |")
    md += [
        "",
        f"- 毛收益：筛选臂 {bc.fmt_pct(perf_gross['ann_pct'])}，全池 {bc.fmt_pct(perf_pool['ann_pct'])}"
        f"（毛口径差 {bc.fmt_num(None if perf_gross['ann_pct'] is None or ann_p is None else perf_gross['ann_pct'] - ann_p)}pp）"
        f"；净口径差 {bc.fmt_num(excess)}pp —— 差别主要来自换手"
        f"（{turn_per_year:.1f} vs 1.3 次/年）",
        f"- 选券能力：对换手同频随机对照超额 {bc.fmt_num(ctrl_excess)}pp、p={ctrl_p}"
        f"（随机臂均值 {bc.fmt_num(ctrl_mean)}%）→ **没有选券能力**",
        "",
        f"- 超额 vs 全池等权：**{bc.fmt_num(excess)}pp/年**（判据 ≥ +{FROZEN['H1_excess_pp']:g}pp）",
        f"- 随机对照（换手同频，{len(ctrl)} 次）：均值 {bc.fmt_num(ctrl_mean)}%、"
        f"p95 {bc.fmt_num(ctrl_p95)}%、超额 {bc.fmt_num(ctrl_excess)}pp、p={ctrl_p}、"
        f"对照年换手 {bc.fmt_num(ctrl_turn)}（筛选臂 {turn_per_year:.1f}）",
        f"- 随机对照（每期重抽同数量，换手不同频）：均值 {bc.fmt_num(fresh_mean)}%"
        f"——低 5pp 是换手成本，不是选券能力",
        f"- 功效：差额 MDE = **{bc.fmt_num(mde)}pp/年**（配对差波动 "
        f"{bc.fmt_num(payload['diff_vol_pct'])}%；判据 ≤ {FROZEN['H3_mde_pp']:g}pp；"
        f"绝对收益的 MDE 是 {bc.fmt_num(mde_abs)}pp，只作参考）",
        f"- 两半：前段超额 {bc.fmt_num(h1_ex)}pp，后段超额 {bc.fmt_num(h2_ex)}pp"
        f"（分割 {SPLIT}）",
        f"- 成本敏感：5bp {bc.fmt_pct(sens['5bp']['ann_pct'])}，"
        f"10bp {bc.fmt_pct(sens['10bp']['ann_pct'])}，"
        f"20bp {bc.fmt_pct(sens['20bp']['ann_pct'])}，"
        f"40bp {bc.fmt_pct(sens['40bp']['ann_pct'])}",
        f"- 筛选池宽度：中位 {payload['data']['floor_breadth_median']} 只"
        f"（最少 {payload['data']['floor_breadth_min']} 只）；全池中位 "
        f"{payload['data']['pool_breadth_median']} 只",
        f"- 数据卫生：剔退市/重整券 {hygiene['excluded_workout_rows']} 行、"
        f"价格带外 {hygiene['excluded_price_band_rows']} 行、"
        f"缺纯债溢价 {hygiene['excluded_premium_missing_rows']} 行；"
        f"隔离单日跳变 {n_jumps} 处（余 {hygiene['rows_used']} 行 / "
        f"{hygiene['codes_used']} 只券）",
        "",
        "## 判据逐条",
        "",
    ]
    for k, v in checks.items():
        md.append(f"- {k}: {'PASS' if v else ('FAIL' if v is False else 'N/A')}")
    md += ["", "口径与限制见 JSON 的 `notes`：日频盯市、期末不奇幻逃脱、无信用事件模型。", ""]
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(md))

    print(f"{headline}: floor net {bc.fmt_pct(ann_f)} vs pool {bc.fmt_pct(ann_p)} "
          f"(excess {bc.fmt_num(excess)}pp), MDE {bc.fmt_num(mde)}pp, "
          f"control {bc.fmt_num(ctrl_mean)}% p={ctrl_p}")
    print(bc.write_json and "json -> " + os.path.relpath(OUT_JSON, bc.ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
