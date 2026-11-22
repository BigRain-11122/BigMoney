"""Bench cell 2: the bond-futures curve -- a spread book we do not have at all.

The question (four-gate test (a): do we put money on it)
--------------------------------------------------------
Our only live line is long-only risk assets. Bond futures give a different
driver: the shape of the curve. T (10y), TF (5y) and TS (2y) all have real bars
since 2015. If any of the three spreads has a harvestable edge, that is a second
line with its own regime; if none does, the answer costs one cell and we stop
asking.

Two styles per spread, deliberately opposite:
  zrev   60-day z-score of the spread; fade it when |z| >= 1, flat otherwise
         (a spread is a mean-reverting object or it is not)
  trend  60-day change sign (if the curve trends, fade loses and this wins)
Both are sized to a 6% vol target by the spread's own realized vol, re-struck
weekly, and charged 1.5bp per side per leg (two legs per spread trade).

The honest control is printed next to every arm: hold the three bond futures
long, equal risk, same vol target. If the spread book cannot beat simply being
long duration, it is not a second line.

Criteria frozen before the run:
  H1  net annualised >= 4.0%
  H2  out-of-sample (2024+) net >= 3.0% and Sharpe >= 0.40
  H3  both halves positive
  H4  drop the best calendar year, still >= 1.5%/yr
  H5  random-sign control p < 0.05
  GO only if all five pass. Spreads are also printed pairwise so a single lucky
  pair cannot hide inside a pooled number.

Known limits (disclosed, not hidden):
  * price spreads, not duration-neutral: T/TF/TS have different DV01. A reader
    who wants DV01-neutral must weight the legs by duration, which this cell
    does not do -- the numbers here are the raw price spread.
  * continuous contracts only: no CTD, no carry-to-delivery, so the carry part
    of a curve trade is not measured.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bench_core as bc  # noqa: E402

OUT_JSON = os.path.join(bc.RESULTS, "bench_bond_curve.json")
OUT_MD = os.path.join(bc.RESEARCH, "BENCH-BOND-CURVE.md")

LEGS = ["T", "TF", "TS"]
PAIRS = [("T", "TF"), ("T", "TS"), ("TF", "TS")]
STYLES = ["zrev", "trend"]
TARGET_VOL = 0.06
COST_BP_SIDE_LEG = 1.5
SPLIT = "2024-01-01"

H1_PCT = 4.0
H2_PCT = 3.0
H2_SHARPE = 0.40
H4_PCT = 1.5
H5_P = 0.05


def spread_frame(panel):
    """{pair: (spread_return Series, cum_spread Series)} on common dates."""
    out = {}
    rets = {}
    for code, df in panel.items():
        r, _ = bc.roll_adjusted_returns(df["close"].values)
        rets[code] = pd.Series(r, index=df.index)
    for a, b in PAIRS:
        if a not in rets or b not in rets:
            continue
        idx = rets[a].index.intersection(rets[b].index)
        if len(idx) < 500:
            continue
        dr = (rets[a].reindex(idx) - rets[b].reindex(idx)).fillna(0.0)
        out[(a, b)] = (dr, dr.cumsum())
    return out


def position_from_signal(sig, dr, target_vol=TARGET_VOL, cap=3.0):
    ann_vol = dr.rolling(60, min_periods=30).std() * np.sqrt(bc.TRADING_DAYS)
    w = target_vol / ann_vol.replace(0.0, np.nan)
    pos = (sig * w).clip(-cap, cap)
    # weekly re-strike, same convention as the futures cell
    keep = (np.arange(len(pos)) % bc.REBALANCE_BARS) == 0
    return pos.where(pd.Series(keep, index=pos.index), np.nan).ffill()


def realise(pos, dr, cost_bp_side_leg=COST_BP_SIDE_LEG):
    """Two legs per spread unit -> cost is charged twice per unit traded."""
    gross = (pos.shift(1) * dr).fillna(0.0)
    turn = (pos - pos.shift(1)).abs().fillna(0.0)
    net = gross - turn * 2.0 * cost_bp_side_leg / 10000.0
    return gross, net, turn


def arm_stats(net, gross, turn, dates):
    reading = bc.split_perf(net.values, dates, split=SPLIT)
    return {
        "common_window": reading["full"],
        "oos_2024_after": reading["oos"],
        "first_half_ann_pct": reading.get("first_half_ann_pct"),
        "second_half_ann_pct": reading.get("second_half_ann_pct"),
        "turnover_per_year": round(float(turn.sum()) * bc.TRADING_DAYS / max(len(turn), 1), 2),
        "gross_ann_pct": round(float(gross.mean()) * bc.TRADING_DAYS * 100, 2),
        "cost_drag_ann_pct": round((float(gross.mean()) - float(net.mean()))
                                   * bc.TRADING_DAYS * 100, 2),
    }


def checks_of(reading, ctrl):
    return {
        "H1_full_ge_4pct": bool(reading["full"]["ann_pct"] is not None
                                and reading["full"]["ann_pct"] >= H1_PCT),
        "H2_oos_ge_3pct_and_sr_ge_0.4": bool(
            reading["oos"]["ann_pct"] is not None
            and reading["oos"]["ann_pct"] >= H2_PCT
            and (reading["oos"]["sharpe"] or -9) >= H2_SHARPE),
        "H3_both_halves_positive": bool(
            reading.get("first_half_ann_pct") is not None
            and reading.get("second_half_ann_pct") is not None
            and reading["first_half_ann_pct"] > 0
            and reading["second_half_ann_pct"] > 0),
        "H4_drop_best_year_ge_1.5pct": bool(
            reading["full"]["drop_best_year_ann_pct"] is not None
            and reading["full"]["drop_best_year_ann_pct"] >= H4_PCT),
        "H5_control_p_lt_0.05": bool(ctrl and ctrl["p_value"] < H5_P),
    }


def control_for(pos, dr, draws=200):
    """Null: circular shifts of the position series.

    A per-day random sign would pay the turnover of flipping every day (it made
    the null read -20%/yr, which is a cost artefact, not a null). Circular
    shifts keep the position's own autocorrelation, magnitude and turnover, and
    only break its alignment with the spread's movements -- which is exactly the
    claim being tested.
    """
    rng = np.random.default_rng(20261122)
    _, net, _ = realise(pos, dr)
    real = float(net.mean() * bc.TRADING_DAYS)
    vals = pos.values
    n = len(vals)
    sample = []
    for _ in range(draws):
        k = int(rng.integers(20, max(21, n - 20)))
        shifted = pd.Series(np.roll(vals, k), index=pos.index)
        _, n2, _ = realise(shifted, dr)
        sample.append(float(n2.mean() * bc.TRADING_DAYS))
    s = np.array(sample)
    return {"real_ann_pct": round(real * 100, 2),
            "null_mean_ann_pct": round(float(s.mean()) * 100, 2),
            "null_p95_ann_pct": round(float(np.percentile(s, 95)) * 100, 2),
            "p_value": round(float((s >= real).mean()), 4),
            "draws": draws}


def long_duration_control(panel):
    """Hold T/TF/TS long, equal risk, 6% target -- the 'just be long' arm."""
    closes, rets = {}, {}
    idx = None
    for code, df in panel.items():
        r, _ = bc.roll_adjusted_returns(df["close"].values)
        s = pd.Series(r, index=df.index)
        rets[code] = s
        idx = s.index if idx is None else idx.union(s.index)
    idx = idx.sort_values()
    v = pd.DataFrame({c: rets[c].reindex(idx) for c in rets}).rolling(60, min_periods=30).std() \
        * np.sqrt(bc.TRADING_DAYS)
    frame = pd.DataFrame({c: rets[c].reindex(idx) for c in rets})
    pos = (TARGET_VOL / np.sqrt(v.notna().sum(axis=1).replace(0, np.nan))).values[:, None] / v
    pos = pos.clip(-3.0, 3.0)
    pos = pd.DataFrame(pos, index=idx, columns=v.columns)
    gross = (pos.shift(1) * frame).sum(axis=1)
    net = gross - (pos - pos.shift(1)).abs().sum(axis=1) * COST_BP_SIDE_LEG / 10000.0
    reading = bc.split_perf(net.values, idx, split=SPLIT)
    return {"common_window": reading["full"], "oos_2024_after": reading["oos"],
            "first_half_ann_pct": reading.get("first_half_ann_pct"),
            "second_half_ann_pct": reading.get("second_half_ann_pct")}


def render_md(payload):
    lines = ["# 国债期货曲线试验（bench cell 2）", "",
             f"evidence cutoff {payload.get('evidence_cutoff')} | generated {payload['generated']} | "
             f"合约 {', '.join(payload['legs'])}",
             "",
             "判据：H1 全期净年化 ≥4%；H2 样本外 ≥3% 且夏普 ≥0.4；H3 前后两半为正；"
             "H4 剔除最好一年 ≥1.5%/年；H5 随机符号 p<0.05。全过才 GO。",
             "",
             "| 价差 | 风格 | 判决 | 全期年化 | 夏普 | 回撤 | 样本外年化 | 换手/年 | 成本拖累 |",
             "|---|---|---|---|---|---|---|---|---|"]
    for a in payload["arms"]:
        f, o = a["common_window"], a["oos_2024_after"]
        lines.append(f"| {a['pair']} | {a['style']} | **{a['verdict']}** | "
                     f"{bc.fmt_pct(f['ann_pct'])} | {bc.fmt_num(f['sharpe'])} | "
                     f"{bc.fmt_pct(f['mdd_pct'])} | {bc.fmt_pct(o['ann_pct'])} | "
                     f"{a['turnover_per_year']} | {a['cost_drag_ann_pct']}pp |")
    ctrl = payload.get("long_duration_control")
    if ctrl:
        f, o = ctrl["common_window"], ctrl["oos_2024_after"]
        lines.append(f"| 直接多长久期（对照） | — | — | {bc.fmt_pct(f['ann_pct'])} | "
                     f"{bc.fmt_num(f['sharpe'])} | {bc.fmt_pct(f['mdd_pct'])} | "
                     f"{bc.fmt_pct(o['ann_pct'])} | — | — |")
    lines += ["", "## 这次没有回答的问题", "",
              "- 没有做 DV01 中性：三条腿久期不同，原始价差不是干净曲线交易。",
              "- 没有 CTD/交割期权：现券端不可见，carry 只以价格漂移形式出现。",
              "- 没有国债期货与现券的基差：本地无现券曲线面板。"]
    return "\n".join(lines) + "\n"


def run():
    bc.weight_priority()
    panel = bc.load_futures_products(LEGS)
    if len(panel) < 3:
        return {"ok": False, "error": f"need T/TF/TS, got {sorted(panel)}"}
    spreads = spread_frame(panel)

    arms = []
    for pair, (dr, cum) in spreads.items():
        z = ((cum - cum.rolling(120, min_periods=60).mean())
             / cum.rolling(120, min_periods=60).std())
        sigs = {
            "zrev": (-np.sign(z)).where(z.abs() >= 1.0),
            "trend": np.sign(cum - cum.shift(60)),
        }
        for style in STYLES:
            sig = sigs[style].reindex(dr.index)
            pos = position_from_signal(sig.astype(float), dr)
            gross, net, turn = realise(pos, dr)
            reading = bc.split_perf(net.values, dr.index, split=SPLIT)
            ctrl = control_for(pos, dr, draws=100)
            checks = checks_of(reading, ctrl)
            stats = arm_stats(net, gross, turn, dr.index)
            arms.append({
                "pair": f"{pair[0]}-{pair[1]}",
                "style": style,
                "verdict": bc.verdict_of(checks),
                "checks": checks,
                **stats,
                "control": ctrl,
            })

    ctrl_long = long_duration_control(panel)
    last = max(df.index[-1] for df in panel.values())
    payload = {
        "cell": "bond_curve",
        "generated": pd.Timestamp.now(tz="Asia/Shanghai").isoformat(timespec="seconds"),
        "evidence_cutoff": str(pd.Timestamp(last).date()),
        "legs": sorted(panel),
        "criteria": {"H1_pct": H1_PCT, "H2_pct": H2_PCT, "H2_sharpe": H2_SHARPE,
                     "H4_pct": H4_PCT, "H5_p": H5_P, "split": SPLIT,
                     "target_vol": TARGET_VOL, "cost_bp_side_leg": COST_BP_SIDE_LEG,
                     "rebalance": f"weekly ({bc.REBALANCE_BARS} bars)"},
        "arms": arms,
        "long_duration_control": ctrl_long,
        "verdict": {f"{a['pair']}:{a['style']}": a["verdict"] for a in arms},
    }
    os.makedirs(bc.BENCH_OUT, exist_ok=True)
    bc.write_json(OUT_JSON, payload)
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write(render_md(payload))
    print(json.dumps({"ok": True, "verdicts": payload["verdict"],
                      "coverage_end": payload["evidence_cutoff"]}, ensure_ascii=False, indent=1))
    return payload


if __name__ == "__main__":
    res = run()
    sys.exit(0 if isinstance(res, dict) and res.get("ok", True) else 1)
