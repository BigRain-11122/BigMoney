"""Bench cell 1: five styles x ten futures -- is any of them a book we lack?

The question this cell answers (four-gate test (a): do we put money on it)
--------------------------------------------------------------------------
We hold one strategy on one asset class. Before adding a second line, the
cheapest thing that can change a decision is to find out whether the classic
systematic styles, run on the ten futures we already have real bars for, produce
a return stream the ETF book does not have. If they do, the second line gets a
weight; if they do not, the queue moves on and we stop asking this question.

Styles (one arm each, fixed parameters -- no per-universe tuning, because a
tuned grid on ten products is how you buy noise):
  tsmom     12-month total return, skipping the last month, sign of it
  ma_cross  50d above 200d mean -> long, below -> short
  donchian  55-bar high/low breakout with a 20-bar opposite channel to flip
  reversal  5-day sign flipped (the deliberate anti-trend arm)
  xs_mom    60-day cross-sectional: top tercile long, bottom tercile short

Instruments: IC IF IH IM (equity index), T TF TS (bonds), AU RB SC (commodities).

Criteria frozen before the run (see bench_core for the shared protocol):
  H1  full-sample net annualised >= 6.0%
  H2  out-of-sample (2024-01-01+) net annualised >= 4.0% AND OOS Sharpe >= 0.50
  H3  both halves of the sample positive
  H4  drop the best calendar year, still >= 2.0%/yr
  H5  random-sign control: p < 0.05 (the arm must beat shuffled signs, not just
      the vol asymmetry of the universe)
  GO only if all five pass. Any failure -> NO_EDGE, and the line does not get a
  weight. A NO_EDGE here is a result, not a failure.

Also printed, because they change how a GO would be sized:
  - turnover per year and cost drag at 3bp/side
  - per-instrument PnL share (a trend book that lives on one product is a bet)
  - correlation with CSI300 and with each other (the ETF book's diversifier test)
  - equal-weight buy-and-hold of the same ten products, vol-targeted
"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bench_core as bc  # noqa: E402

OUT_JSON = os.path.join(bc.RESULTS, "bench_fut_trend.json")
OUT_MD = os.path.join(bc.RESEARCH, "BENCH-FUT-TREND.md")
EVIDENCE_CUTOFF_FALLBACK = "unknown"

# ---- frozen thresholds ----------------------------------------------------
H1_FULL_PCT = 6.0
H2_OOS_PCT = 4.0
H2_OOS_SHARPE = 0.50
H4_DROP_BEST_PCT = 2.0
H5_P = 0.05
SPLIT = "2024-01-01"

STYLES = ["tsmom", "ma_cross", "donchian", "reversal", "xs_mom"]


# --------------------------------------------------------------------------
# signals
# --------------------------------------------------------------------------
def sig_tsmom(closes, lookback=252, skip=21):
    out = {}
    for c, s in closes.items():
        past = s.shift(lookback + skip)
        out[c] = np.sign(s / past - 1.0).where((s.notna()) & (past.notna()))
    return out


def sig_ma_cross(closes, fast=50, slow=200):
    out = {}
    for c, s in closes.items():
        f, sl = s.rolling(fast).mean(), s.rolling(slow).mean()
        out[c] = np.sign(f - sl).where(sl.notna())
    return out


def sig_donchian(closes, highs, lows, entry=55, exit_=20):
    out = {}
    for c, s in closes.items():
        hi = highs[c].reindex(s.index).rolling(entry).max().shift(1)
        lo = lows[c].reindex(s.index).rolling(exit_).min().shift(1)
        state, arr = 0, []
        for price, h, l in zip(s.values, hi.values, lo.values):
            if not np.isfinite(price) or not np.isfinite(h) or not np.isfinite(l):
                arr.append(np.nan)
                continue
            if state == 0:
                state = 1 if price > h else (-1 if price < l else 0)
            elif state == 1 and price < l:
                state = -1
            elif state == -1 and price > h:
                state = 1
            arr.append(float(state))
        out[c] = pd.Series(arr, index=s.index).replace(0.0, np.nan)
    return out


def sig_reversal(closes, window=5):
    out = {}
    for c, s in closes.items():
        past = s.shift(window)
        out[c] = (-np.sign(s / past - 1.0)).where((s.notna()) & (past.notna()))
    return out


def sig_xs_mom(closes, window=60, tercile=1.0 / 3.0):
    frame = pd.DataFrame({c: s for c, s in closes.items()})
    ret = frame / frame.shift(window) - 1.0
    ranks = ret.rank(axis=1, pct=True)
    sig = pd.DataFrame(np.nan, index=frame.index, columns=frame.columns)
    sig[ranks >= 1.0 - tercile] = 1.0
    sig[ranks <= tercile] = -1.0
    return {c: sig[c] for c in frame.columns}


# --------------------------------------------------------------------------
# one arm
# --------------------------------------------------------------------------
def run_arm(name, signals, dates, closes, rets, vols, csi, common_start):
    pos, live = bc.vol_weighted_positions(signals, vols, target_vol=0.10)
    if pos is None or not pos.notna().any().any():
        return None
    gross, net, turn = bc.apply_costs(pos, rets)
    net = net.reindex(dates).fillna(0.0)
    gross = gross.reindex(dates).fillna(0.0)
    turn = turn.reindex(dates).fillna(0.0)

    common = net.index >= common_start
    reading_full = bc.split_perf(net.values, dates, split=SPLIT)
    reading = bc.split_perf(net.values[common], dates[common], split=SPLIT)
    ctrl = bc.random_sign_control(pos[pos.index >= common_start],
                                  pd.DataFrame(rets).reindex(pos.index)[pos.index >= common_start],
                                  draws=120)

    per_product = {}
    rframe = pd.DataFrame(rets).reindex(pos.index)
    contrib = (pos.shift(1) * rframe)[pos.index >= common_start].sum()
    total_abs = float(contrib.abs().sum()) or 1.0
    for c in contrib.index:
        per_product[c] = round(float(contrib[c]) / total_abs * 100.0, 1)

    corr_csi = None
    if csi is not None:
        idx_ret = csi.reindex(dates).pct_change()
        pair = pd.concat([net, idx_ret], axis=1)[common].dropna()
        if len(pair) > 60 and pair.iloc[:, 0].std() > 0 and pair.iloc[:, 1].std() > 0:
            corr_csi = round(float(pair.iloc[:, 0].corr(pair.iloc[:, 1])), 3)

    checks = {
        "H1_full_ge_6pct": bool(reading["full"]["ann_pct"] is not None
                                and reading["full"]["ann_pct"] >= H1_FULL_PCT),
        "H2_oos_ge_4pct_and_sr_ge_0.5": bool(
            reading["oos"]["ann_pct"] is not None
            and reading["oos"]["ann_pct"] >= H2_OOS_PCT
            and (reading["oos"]["sharpe"] or -9) >= H2_OOS_SHARPE),
        "H3_both_halves_positive": bool(
            reading.get("first_half_ann_pct") is not None
            and reading.get("second_half_ann_pct") is not None
            and reading["first_half_ann_pct"] > 0
            and reading["second_half_ann_pct"] > 0),
        "H4_drop_best_year_ge_2pct": bool(
            reading["full"]["drop_best_year_ann_pct"] is not None
            and reading["full"]["drop_best_year_ann_pct"] >= H4_DROP_BEST_PCT),
        "H5_control_p_lt_0.05": bool(ctrl["p_value"] is not None and ctrl["p_value"] < H5_P),
    }

    return {
        "style": name,
        "verdict": bc.verdict_of(checks),
        "checks": checks,
        "common_window": reading["full"],
        "common_is_before_2024": reading["is"],
        "oos_2024_after": reading["oos"],
        "first_half_ann_pct": reading.get("first_half_ann_pct"),
        "second_half_ann_pct": reading.get("second_half_ann_pct"),
        "full_sample_context": reading_full["full"],
        "gross_ann_pct": round(float(np.mean(gross.values[common])) * bc.TRADING_DAYS * 100, 2),
        "turnover_per_year": round(float(turn.values[common].sum()) * bc.TRADING_DAYS
                                   / max(int(common.sum()), 1), 2),
        "cost_drag_ann_pct": round((float(np.mean(gross.values[common]))
                                    - float(np.mean(net.values[common])))
                                   * bc.TRADING_DAYS * 100, 2),
        "avg_live_instruments": round(float(live.reindex(dates)[common].mean()), 1),
        "control": ctrl,
        "corr_csi300": corr_csi,
        "per_product_pnl_share_pct": per_product,
        "series": {"net": net[common], "dates": dates[common]},
    }


def buy_and_hold(dates, closes, rets, vols, common_start):
    """Equal-risk long-only arm: the honest 'just hold them' benchmark."""
    sig = {c: pd.Series(1.0, index=s.index).where(s.notna()) for c, s in closes.items()}
    pos, live = bc.vol_weighted_positions(sig, vols, target_vol=0.10)
    if pos is None:
        return None
    gross, net, turn = bc.apply_costs(pos, rets)
    net = net.reindex(dates).fillna(0.0)
    common = net.index >= common_start
    reading = bc.split_perf(net.values[common], dates[common], split=SPLIT)
    return {
        "style": "buy_and_hold_equal_risk",
        "common_window": reading["full"],
        "common_is_before_2024": reading["is"],
        "oos_2024_after": reading["oos"],
        "turnover_per_year": round(float(turn.values[common].sum()) * bc.TRADING_DAYS
                                   / max(int(common.sum()), 1), 2),
        "series": {"net": net[common], "dates": dates[common]},
    }


# --------------------------------------------------------------------------
# report
# --------------------------------------------------------------------------
def render_md(payload):
    cov = payload["coverage"]
    lines = [
        "# 期货多风格试验（bench cell 1）",
        "",
        f"evidence cutoff {payload.get('evidence_cutoff')} | generated {payload['generated']} | "
        f"bar 数 {cov['bars']}（{cov['start']} → {cov['end']}）| 品种 {cov['n_products']}",
        "",
        "判据（开跑前写死）：H1 全期净年化 ≥6%；H2 样本外(2024+) ≥4% 且夏普 ≥0.5；"
        "H3 前后两半都为正；H4 剔除最好一年仍 ≥2%/年；H5 随机符号对照 p<0.05。全过才是 GO。",
        "",
        "## 结论",
        "",
        "| 风格 | 判决 | 全期年化 | 夏普 | 回撤 | 样本外年化 | 样本外夏普 | 剔除最好一年 | 对照p | 换手/年 |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for arm in payload["arms"]:
        f = arm["common_window"]
        o = arm["oos_2024_after"]
        lines.append(
            f"| {arm['style']} | **{arm['verdict']}** | {bc.fmt_pct(f['ann_pct'])} | "
            f"{bc.fmt_num(f['sharpe'])} | {bc.fmt_pct(f['mdd_pct'])} | "
            f"{bc.fmt_pct(o['ann_pct'])} | {bc.fmt_num(o['sharpe'])} | "
            f"{bc.fmt_pct(f['drop_best_year_ann_pct'])} | {arm['control']['p_value']} | "
            f"{arm['turnover_per_year']} |")
    bh = payload.get("benchmark_buy_and_hold")
    if bh:
        f, o = bh["common_window"], bh["oos_2024_after"]
        lines.append(f"| 等风险买入持有（对照） | — | {bc.fmt_pct(f['ann_pct'])} | "
                     f"{bc.fmt_num(f['sharpe'])} | {bc.fmt_pct(f['mdd_pct'])} | "
                     f"{bc.fmt_pct(o['ann_pct'])} | {bc.fmt_num(o['sharpe'])} | — | — | "
                     f"{bh['turnover_per_year']} |")

    lines += ["", "## 逐年（净，%）", ""]
    years = sorted({int(y) for arm in payload["arms"] for y in arm["common_window"]["years"]})
    head = "| 风格 | " + " | ".join(str(y) for y in years) + " |"
    lines += [head, "|" + "---|" * (len(years) + 1)]
    for arm in payload["arms"]:
        cells = [str(arm["common_window"]["years"].get(str(y), arm["common_window"]["years"].get(y, "—")))
                 for y in years]
        lines.append(f"| {arm['style']} | " + " | ".join(cells) + " |")

    lines += ["", "## 各风格的钱从哪来（PnL 占比 %）与分散度", ""]
    for arm in payload["arms"]:
        top = sorted(arm["per_product_pnl_share_pct"].items(), key=lambda kv: -abs(kv[1]))[:4]
        lines.append(f"- **{arm['style']}**（{arm['verdict']}）：" +
                     "、".join(f"{k} {v:+.0f}%" for k, v in top) +
                     f"；与沪深300相关 {bc.fmt_num(arm['corr_csi300'])}；"
                     f"成本拖累 {arm['cost_drag_ann_pct']}pp/年")
    lines += ["", "## 风格间相关（日收益）", ""]
    corr = payload.get("style_correlation") or {}
    if corr:
        names = list(corr)
        lines.append("| | " + " | ".join(names) + " |")
        lines.append("|" + "---|" * (len(names) + 1))
        for a in names:
            lines.append(f"| {a} | " + " | ".join(f"{corr[a][b]:+.2f}" for b in names) + " |")
    else:
        lines.append("（样本不足以估计）")

    lines += ["", "## 这次没有回答的问题", "",
              "- 没有做参数网格：十品种上跑网格买的是噪声；若要换参数，应在另一段样本上预先登记。",
              "- 没有把基差/展期接进来：股指基差已在 `idx_fut_basis` 判过（IC 净 +4.15pp/IM +5.89pp），"
              "本cell只看价格趋势。",
              "- 没有日内数据：全部用日线收盘，成交假设是次日开盘可成交（未建模开盘滑点，扣 3bp/边已含保守度）。"]
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------
def run():
    bc.weight_priority()
    panel = bc.load_futures_products()
    if len(panel) < 5:
        return {"ok": False, "error": f"only {len(panel)} futures files usable"}
    dates, closes, rets, vols = bc.align_futures(panel)
    highs, lows = bc.align_highs_lows(panel, closes)
    csi = bc.load_index_close("sh000300")

    signals = {
        "tsmom": sig_tsmom(closes),
        "ma_cross": sig_ma_cross(closes),
        "donchian": sig_donchian(closes, highs, lows),
        "reversal": sig_reversal(closes),
        "xs_mom": sig_xs_mom(closes),
    }

    # Verdict window = the bars on which a real book could hold this universe:
    # at least five instruments carry a usable 60d vol. Before that the
    # "portfolio" was two commodities and a different strategy in disguise.
    vol_frame = pd.DataFrame(vols)
    live_count = vol_frame.notna().sum(axis=1)
    eligible = live_count[live_count >= 5].index
    common_start = eligible.min() if len(eligible) else dates[0]

    arms = []
    for style in STYLES:
        arm = run_arm(style, signals[style], dates, closes, rets, vols, csi, common_start)
        if arm:
            arms.append(arm)

    corr = {}
    if len(arms) >= 2:
        frame = pd.DataFrame({a["style"]: a["series"]["net"] for a in arms}).dropna(how="all")
        c = frame.corr()
        corr = {a: {b: round(float(c.loc[a, b]), 2) for b in c.columns} for a in c.index}

    bh = buy_and_hold(dates, closes, rets, vols, common_start)
    bh.pop("series", None)

    # Decision layer (disclosed addendum, see criteria_addendum): a style that
    # merely re-packages long beta does not change a decision. It must beat
    # vol-matched holding of the same basket by >= 2pp/yr to count.
    vs_hold = {}
    for a in arms:
        if not bh:
            break
        excess = round(a["common_window"]["ann_pct"] - bh["common_window"]["ann_pct"], 2)
        vs_hold[a["style"]] = {
            "excess_ann_pp": excess,
            "beats_hold_by_2pp": bool(excess >= 2.0),
            "sharpe": a["common_window"]["sharpe"],
            "hold_sharpe": bh["common_window"]["sharpe"],
        }
        if a["verdict"] == "GO" and excess < 2.0:
            a["verdict"] = "NO_EDGE_REPACKAGES_BETA"

    # ensemble of the arms that passed all five checks, if two or more
    passed = [a for a in arms if a["verdict"] == "GO"]
    ensemble = None
    if len(passed) >= 2:
        frame = pd.DataFrame({a["style"]: a["series"]["net"] for a in passed}).dropna()
        ens = frame.mean(axis=1)
        reading = bc.split_perf(ens.values, ens.index, split=SPLIT)
        ensemble = {"styles": [a["style"] for a in passed],
                    "common_window": reading["full"], "oos_2024_after": reading["oos"],
                    "first_half_ann_pct": reading.get("first_half_ann_pct"),
                    "second_half_ann_pct": reading.get("second_half_ann_pct")}

    for a in arms:
        a.pop("series", None)

    last = dates[-1]
    payload = {
        "cell": "fut_trend",
        "generated": pd.Timestamp.now(tz="Asia/Shanghai").isoformat(timespec="seconds"),
        "evidence_cutoff": str(pd.Timestamp(last).date()),
        "criteria": {
            "H1_full_ann_pct_ge": H1_FULL_PCT,
            "H2_oos_ann_pct_ge": H2_OOS_PCT,
            "H2_oos_sharpe_ge": H2_OOS_SHARPE,
            "H4_drop_best_year_pct_ge": H4_DROP_BEST_PCT,
            "H5_control_p_lt": H5_P,
            "split": SPLIT,
            "verdict_window": "bars with >=5 instruments carrying a usable 60d vol",
            "cost_bp_side": bc.COST_BP_SIDE,
            "target_vol": 0.10,
            "roll_rule": f"|move| >= max({bc.ROLL_SCALE} x median, {bc.ROLL_FLOOR}) is a roll and is excluded from returns",
        },
        "coverage": {
            "bars": int(len(dates)),
            "start": str(pd.Timestamp(dates[0]).date()),
            "end": str(pd.Timestamp(dates[-1]).date()),
            "verdict_window_start": str(pd.Timestamp(common_start).date()),
            "verdict_window_bars": int((dates >= common_start).sum()),
            "n_products": len(panel),
            "products": sorted(panel),
        },
        "arms": arms,
        "benchmark_buy_and_hold": bh,
        "vs_hold": vs_hold,
        "criteria_addendum": {
            "rule": "a GO must also beat vol-matched buy-and-hold of the same basket by >= 2.0pp/yr",
            "why": "run #1 showed ma_cross at +0.7pp over holding: statistically real (p=0.0) but not a second line -- it is the long beta in a trend costume",
            "disclosure": "added after run #1 was read; H1-H5 thresholds were not touched, and this rule is printed so a reader can discount it",
        },
        "ensemble_of_passing": ensemble,
        "style_correlation": corr,
        "verdict": {a["style"]: a["verdict"] for a in arms},
        "go_count": len(passed),
    }

    os.makedirs(bc.BENCH_OUT, exist_ok=True)
    bc.write_json(OUT_JSON, payload)
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write(render_md(payload))

    print(json.dumps({"ok": True, "verdicts": payload["verdict"],
                      "coverage": payload["coverage"],
                      "json": os.path.relpath(OUT_JSON, bc.ROOT),
                      "md": os.path.relpath(OUT_MD, bc.ROOT)}, ensure_ascii=False, indent=1))
    return payload


if __name__ == "__main__":
    res = run()
    sys.exit(0 if isinstance(res, dict) and res.get("ok", True) else 1)
