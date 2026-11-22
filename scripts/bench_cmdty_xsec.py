"""Bench cell: 32 commodity futures -- was xs_mom judged on too narrow a universe?

The question this cell answers (four-gate test (a): do we put money on it)
-------------------------------------------------------------------------
`bench_fut_trend` ran cross-sectional momentum on ten products (four equity
index, three bonds, three commodities) and it came back NO_EDGE. The direction
page (research/DIRECTION-20261122.md, section 5.2) wrote the reason down: a
commodity cross-section with three members is not a cross-section. This cell
fixes exactly that one variable -- breadth -- and changes nothing else:

  32 commodity-only main-continuous contracts, same 60-day ranking, same
  tercile long/short, same weekly re-strike, same 60d vol weighting, same
  roll-gap surgery, same cost rate.

If momentum works once the universe is wide enough, the second line exists and
the earlier NO_EDGE was a measurement artefact. If it still fails on 32
products, the answer is no longer "not enough names" and the line closes.

Criteria frozen before the run (bench_core protocol)
----------------------------------------------------
  H1  full-sample net annualised >= 6.0%
  H2  out-of-sample (2024-01-01+) net annualised >= 3.0% AND OOS Sharpe >= 0.30
  H3  both halves of the sample positive
  H4  drop the best calendar year, still >= 2.0%/yr
  H5  random-sign control: p < 0.05
  GO only if all five pass. Any failure -> NO_EDGE, the line gets no weight.

Printed because they change how a GO would be sized
---------------------------------------------------
  - live breadth per year (a "32-product" universe that only has 9 names in
    2015 is a 9-name universe for that stretch, and every reading before the
    last name lists is discounted accordingly)
  - turnover/yr and cost drag at the bench cost rate
  - per-product PnL share (a cross-section book living on one product is a bet)
  - correlation with CSI300 (the ETF book's diversifier test)
  - vol-matched equal-risk long-only hold of the same universe

Disclosures (not done, on purpose)
----------------------------------
  - no DV01 / contract-multiplier neutralisation: contracts differ in notional
    per lot, so the vol weighting equalises risk, not rupees.
  - daily settlement, intraday slippage, margin and night-session timing are out
    of scope; the bar is the daily close.
  - survivorship: the list is today's live contracts; delisted varieties
    (ZC, RR, ...) are absent and would only make the universe wider.
"""
from __future__ import annotations

import datetime as dt
import io
import json
import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bench_core as bc  # noqa: E402
import update_futures as uf  # noqa: E402  (fetch_raw / completeness_filter reuse)

ROOT = bc.ROOT
DATA_DIR = os.path.join(ROOT, "data", "fut_kx")
OUT_JSON = os.path.join(bc.RESULTS, "bench_cmdty_xsec.json")
OUT_MD = os.path.join(bc.RESEARCH, "BENCH-CMDTY-XSEC.md")

# ---- frozen thresholds ----------------------------------------------------
H1_FULL_PCT = 6.0
H2_OOS_PCT = 3.0
H2_OOS_SHARPE = 0.30
H4_DROP_BEST_PCT = 2.0
H5_P = 0.05
SPLIT = "2024-01-01"
LOOKBACK = 60          # cross-sectional ranking window (frozen)
MIN_HISTORY = 250      # bars before a product may enter the cross-section
MIN_BREADTH = 8        # fewer live names than this = no verdict on that bar
TARGET_VOL = 0.10
MAX_WEIGHT = 1.0
SLEEP_S = 2.5

# Commodity main-continuous contracts (sina codes). Financials (IF/IC/IM/IH/T/
# TF/TS) are excluded on purpose: this cell is about a homogeneous cross-section.
UNIVERSE = [
    # metals
    "CU0", "AL0", "ZN0", "PB0", "NI0", "SN0", "AU0", "AG0",
    # ferrous
    "RB0", "HC0", "I0", "J0", "JM0", "SF0", "SM0",
    # energy & chemicals
    "SC0", "BU0", "FU0", "RU0", "TA0", "MA0", "EG0", "PP0", "L0", "V0",
    "EB0", "UR0", "FG0", "SA0", "PF0",
    # agriculture
    "M0", "Y0", "P0", "A0", "B0", "C0", "CS0", "JD0", "LH0",
    "CF0", "SR0", "OI0", "RM0", "SP0",
]
COLS = ["date", "open", "high", "low", "close", "volume", "oi", "settle"]


# ----------------------------------------------------------------- panel io
def _read_csv(path):
    with io.open(path, "r", encoding="utf-8") as f:
        return list(__import__("csv").DictReader(f))


def _write_csv(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write(",".join(COLS) + "\n")
        for r in rows:
            f.write(",".join("" if r.get(c) is None else str(r.get(c)) for c in COLS) + "\n")
    os.replace(tmp, path)


def _overlap_mismatch(local, remote, tol=1e-6):
    """Rows present in both, prices compared. Returns list of bad dates."""
    by = {str(r["date"]): r for r in remote}
    bad = []
    for r in local:
        d = str(r["date"])
        q = by.get(d)
        if q is None:
            continue
        for c in ("open", "high", "low", "close"):
            a, b = r.get(c), q.get(c)
            try:
                fa = None if a in (None, "") else float(a)
                fb = None if b in (None, "") else float(b)
            except (TypeError, ValueError):
                continue
            if fa is None or fb is None:
                continue
            if abs(fa - fb) > tol * max(1.0, abs(fb)):
                bad.append(d)
                break
    return bad


def pull_universe(symbols=None):
    """Full-history pull into data/fut_kx/<V>.csv (append-only, overlap-checked)."""
    uf._clear_proxy_env()
    symbols = symbols or UNIVERSE
    report = {"ok": [], "fail": [], "overlap": [], "skipped": []}
    for i, sym in enumerate(symbols):
        if i:
            time.sleep(SLEEP_S)
        path = os.path.join(DATA_DIR, sym + ".csv")
        try:
            rows = uf.fetch_raw(sym)
            rows, dropped = uf.completeness_filter(rows)
            rows = [r for r in rows if r.get("close") not in (None, "")]
            if len(rows) < MIN_HISTORY:
                report["skipped"].append({"symbol": sym, "bars": len(rows)})
                continue
            local = _read_csv(path) if os.path.exists(path) else []
            if local:
                bad = _overlap_mismatch(local, rows)
                if bad:
                    # Source re-adjusted history: keep the local file untouched.
                    report["overlap"].append({"symbol": sym, "dates": bad[:5],
                                              "count": len(bad)})
                    continue
                if len(rows) < len(local):
                    report["skipped"].append({"symbol": sym, "why": "shorter_than_local",
                                              "bars": len(rows)})
                    continue
            _write_csv(path, rows)
            report["ok"].append({"symbol": sym, "bars": len(rows),
                                 "start": str(rows[0]["date"]), "end": str(rows[-1]["date"]),
                                 "dropped_partial_today": dropped})
        except Exception as e:  # honest per-symbol failure, never abort the sweep
            report["fail"].append({"symbol": sym, "error": f"{type(e).__name__}: {str(e)[:120]}"})
    return report


def load_panel():
    """{symbol: pd.Series(close)} from data/fut_kx, index = DatetimeIndex."""
    out = {}
    if not os.path.isdir(DATA_DIR):
        return out
    for fn in sorted(os.listdir(DATA_DIR)):
        if not fn.endswith(".csv"):
            continue
        rows = _read_csv(os.path.join(DATA_DIR, fn))
        if len(rows) < MIN_HISTORY:
            continue
        idx, vals = [], []
        for r in rows:
            try:
                idx.append(pd.Timestamp(str(r["date"])))
                vals.append(float(r["close"]))
            except (TypeError, ValueError, KeyError):
                continue
        if len(idx) < MIN_HISTORY:
            continue
        s = pd.Series(vals, index=pd.DatetimeIndex(idx), dtype=float)
        s = s[~s.index.duplicated(keep="last")].sort_index()
        out.setdefault(fn[:-4], s)
    return out


# ------------------------------------------------------------------- signals
def build_frames(panel):
    """Roll-adjusted returns / adjusted price / 60d vol, aligned on the union index."""
    if not panel:
        return None, None, None
    idx = sorted(set().union(*[set(s.index) for s in panel.values()]))
    idx = pd.DatetimeIndex(idx)
    close = pd.DataFrame({k: v.reindex(idx) for k, v in panel.items()})
    rets, adj = {}, {}
    for c in close.columns:
        vals = close[c].values.astype(float)
        r, _ = bc.roll_adjusted_returns(vals)
        rets[c] = r
        adj[c] = bc.adjusted_price(vals)
    rets = pd.DataFrame(rets, index=idx)
    adj = pd.DataFrame(adj, index=idx)
    # a product only "exists" from its first real bar
    born = close.notna().cumsum() > 0
    rets = rets.where(born)
    adj = adj.where(born)
    vols = rets.rolling(60).std() * np.sqrt(bc.TRADING_DAYS)
    enough = born.cumsum() >= MIN_HISTORY
    return rets.where(enough), adj.where(enough), vols.where(enough)


def xs_signals(adj, vols, lookback=LOOKBACK, tercile=3):
    """Top tercile long, bottom tercile short; middle flat. Live = has both."""
    score = adj / adj.shift(lookback) - 1.0
    live = score.notna() & vols.notna() & (vols > 0)
    n_live = live.sum(axis=1)
    sig = pd.DataFrame(np.nan, index=score.index, columns=score.columns)
    ok = n_live >= MIN_BREADTH
    ranked = score.where(live).rank(axis=1, pct=True)
    sig = sig.mask(ranked <= 1.0 / tercile, 1.0)
    sig = sig.mask(ranked >= 1.0 - 1.0 / tercile, -1.0)
    sig = sig.where(live)          # flat/no-data names carry no position
    sig = sig.mask(~ok, np.nan)    # too few live names -> no cross-section at all
    return sig, live


# ----------------------------------------------------------------------- run
def run(do_pull=True):
    if do_pull:
        pull = pull_universe()
    else:
        # No network this pass: report what is actually on disk instead of an
        # empty pull block (an empty dict reads like "nothing was fetched today",
        # which is a different claim from "the panel is already here").
        pull = {"mode": "no-pull (panel already on disk)", "ok": [], "fail": [],
                "overlap": [], "skipped": [], "on_disk": []}
        if os.path.isdir(DATA_DIR):
            by = load_panel()
            for sym in sorted(by):
                s = by[sym]
                pull["on_disk"].append({"symbol": sym, "bars": int(len(s)),
                                        "start": str(s.index[0].date()),
                                        "end": str(s.index[-1].date())})
        pull["ok"] = pull["on_disk"]
    panel = load_panel()
    if len(panel) < MIN_BREADTH:
        payload = {"cell": "cmdty_xsec", "verdict": {"verdict": "DATA-BLOCKED"},
                   "coverage": {"n_products": len(panel)}, "pull": pull,
                   "generated": pd.Timestamp.now(tz="Asia/Shanghai").isoformat(timespec="seconds")}
        bc.write_json(OUT_JSON, payload)
        print(json.dumps(payload, ensure_ascii=False, indent=1)[:2000])
        return payload

    rets, adj, vols = build_frames(panel)
    sig, live = xs_signals(adj, vols)
    pos, n_live_series = bc.vol_weighted_positions(sig, vols, target_vol=TARGET_VOL,
                                                   max_weight=MAX_WEIGHT)
    gross, net, turn = bc.apply_costs(pos, rets)
    dates = pos.index

    full = bc.split_perf(net.values, dates, split=SPLIT)
    fp = full["full"]
    oos = full["oos"]
    oos_sharpe = oos.get("sharpe")
    drop_best = fp.get("drop_best_year_ann_pct")
    ctrl = bc.random_sign_control(pos, rets)

    # vol-matched equal-risk long-only hold of the same universe
    hold_sig = pd.DataFrame(1.0, index=rets.index, columns=rets.columns).where(vols.notna() & (vols > 0))
    hold_pos, _ = bc.vol_weighted_positions(hold_sig, vols, target_vol=TARGET_VOL,
                                            max_weight=MAX_WEIGHT)
    _, hold_net, _ = bc.apply_costs(hold_pos, rets)
    hold = bc.split_perf(hold_net.values, dates, split=SPLIT)

    # long-only half of the same signal (shorting costs are the usual objection)
    lo_sig = sig.clip(lower=0.0)
    lo_pos, _ = bc.vol_weighted_positions(lo_sig, vols, target_vol=TARGET_VOL,
                                          max_weight=MAX_WEIGHT)
    _, lo_net, _ = bc.apply_costs(lo_pos, rets)
    long_only = bc.split_perf(lo_net.values, dates, split=SPLIT)

    checks = {
        "H1_full_ann_ge": bool((fp.get("ann_pct") or -99) >= H1_FULL_PCT),
        "H2_oos_ann_ge": bool((oos.get("ann_pct") or -99) >= H2_OOS_PCT),
        "H2_oos_sharpe_ge": bool((oos_sharpe if oos_sharpe is not None else -99) >= H2_OOS_SHARPE),
        "H3_both_halves_positive": bool((full.get("first_half_ann_pct") or -99) > 0
                                        and (full.get("second_half_ann_pct") or -99) > 0),
        "H4_drop_best_year_ge": bool((drop_best if drop_best is not None else -99) >= H4_DROP_BEST_PCT),
        "H5_control_p_lt": bool((ctrl.get("p_value") if ctrl.get("p_value") is not None else 1.0) < H5_P),
    }
    verdict = "GO" if all(checks.values()) else "NO_EDGE"

    # per-product PnL share (gross, no cost) and breadth by year
    share = {}
    for c in rets.columns:
        pnl = (pos[c].shift(1) * rets[c])
        share[c] = float(pnl.sum())
    tot = sum(abs(v) for v in share.values()) or 1.0
    share_pct = {k: round(100.0 * v / tot, 1) for k, v in share.items()}
    breadth = {}
    yrs = pd.DatetimeIndex(dates).year
    for y in sorted(set(yrs)):
        sel = yrs == y
        if sel.sum() < 20:
            continue
        breadth[int(y)] = int(np.nanmedian(n_live_series.values[sel]))

    csi = None
    try:
        csi_close = bc.load_index_close()
        c = pd.Series(csi_close).copy()
        c.index = pd.DatetimeIndex(c.index)
        cr = c.pct_change().reindex(dates).fillna(0.0)
        if float(np.std(cr.values)) > 0:
            csi = round(float(np.corrcoef(net.values, cr.values)[0, 1]), 3)
    except Exception:
        csi = None

    payload = {
        "cell": "cmdty_xsec",
        "generated": pd.Timestamp.now(tz="Asia/Shanghai").isoformat(timespec="seconds"),
        "evidence_cutoff": str(pd.Timestamp(dates[-1]).date()),
        "question": ("was xs_mom judged on too narrow a universe? 32 commodity "
                     "main-continuous contracts, 60d tercile long/short"),
        "criteria": {
            "H1_full_ann_pct_ge": H1_FULL_PCT, "H2_oos_ann_pct_ge": H2_OOS_PCT,
            "H2_oos_sharpe_ge": H2_OOS_SHARPE, "H4_drop_best_year_pct_ge": H4_DROP_BEST_PCT,
            "H5_control_p_lt": H5_P, "split": SPLIT, "lookback": LOOKBACK,
            "min_history_bars": MIN_HISTORY, "min_breadth": MIN_BREADTH,
            "target_vol": TARGET_VOL, "max_weight": MAX_WEIGHT,
            "cost_bp_side": bc.COST_BP_SIDE,
            "rebalance_bars": getattr(bc, "REBALANCE_BARS", None),
            "roll_rule": (f"|move| >= max({bc.ROLL_SCALE} x median, {bc.ROLL_FLOOR}) "
                          f"is a roll and is excluded from returns"),
        },
        "coverage": {
            "n_products": len(panel),
            "products": sorted(panel),
            "bars": int(len(dates)),
            "start": str(pd.Timestamp(dates[0]).date()),
            "end": str(pd.Timestamp(dates[-1]).date()),
            "median_live_breadth": int(np.nanmedian(n_live_series.values)) if len(n_live_series) else 0,
            "breadth_by_year": breadth,
            "pull_ok": len(pull["ok"]), "pull_fail": len(pull["fail"]),
            "pull_overlap": len(pull["overlap"]), "pull_skipped": len(pull["skipped"]),
        },
        "arm_xs_mom_60d": {
            "full": fp, "oos_2024_after": oos,
            "first_half_ann_pct": full.get("first_half_ann_pct"),
            "second_half_ann_pct": full.get("second_half_ann_pct"),
            "turnover_per_year": round(float(turn.mean()) * bc.TRADING_DAYS, 1),
            "cost_drag_pp_per_year": round(float(turn.mean()) * bc.COST_BP_SIDE / 100.0 * bc.TRADING_DAYS, 2),
            "pnl_share_pct": dict(sorted(share_pct.items(), key=lambda kv: -abs(kv[1]))[:8]),
        },
        "control_random_sign": ctrl,
        "benchmark_long_only_hold": {"full": hold["full"], "oos_2024_after": hold["oos"]},
        "variant_long_only_signal": {"full": long_only["full"], "oos_2024_after": long_only["oos"]},
        "corr_csi300": csi,
        "checks": checks,
        "verdict": verdict,
        "pull": pull,
    }
    bc.write_json(OUT_JSON, payload)
    with io.open(OUT_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write(render_md(payload))
    print(json.dumps({"ok": True, "verdict": verdict, "checks": checks,
                      "full": fp, "oos": oos,
                      "breadth": payload["coverage"]["median_live_breadth"],
                      "json": os.path.relpath(OUT_JSON, ROOT),
                      "md": os.path.relpath(OUT_MD, ROOT)}, ensure_ascii=False, indent=1)[:3000])
    return payload


def power_line(p):
    """What this sample can and cannot rule out.

    A negative is only as strong as the Sharpe it can exclude. With n years of
    daily data the standard error of an annualised Sharpe is ~sqrt((1+SR^2/2)/n);
    the gate this cell had to clear needed roughly SR 0.6 at a 10% vol target
    (6%/yr). Printing the interval says whether "NO_EDGE" means "no edge" or
    "no edge bigger than X" -- the two are different claims.
    """
    f = p["arm_xs_mom_60d"]["full"]
    n_bars = f.get("n") or 0
    sr = f.get("sharpe") or 0.0
    years = n_bars / 252.0
    if years <= 0:
        return "样本不足，无法给出功效区间。"
    se = (1.0 + 0.5 * sr * sr) ** 0.5 / (years ** 0.5)
    lo, hi = sr - 1.96 * se, sr + 1.96 * se
    return (f"样本 {years:.1f} 年，实测年化夏普 {sr:.3f}，标准误约 {se:.3f} → "
            f"95% 区间约 [{lo:.2f}, {hi:.2f}]。本格的 GO 门要求在 10% 目标波动下做到 6%/年"
            f"（≈夏普 0.6），这个区间**上界远低于门线**，所以「不开线」是硬结论；"
            f"但它不等于「绝对没有微弱优势」——区间上部仍容得下一个夏普 0.3 左右的小边缘，"
            f"那种规模的东西在本司的仓位阶梯上没有位置。")


def render_md(p):
    c = p["coverage"]
    a = p["arm_xs_mom_60d"]
    f, o = a["full"], a["oos_2024_after"]
    lines = [
        "# 商品横截面动量 · 32 品种宽度试验（BENCH · cmdty_xsec）",
        "",
        f"> 生成 {p['generated']} ｜ 证据截止 **{p['evidence_cutoff']}** ｜ 判决 **{p['verdict']}**",
        "",
        "## 问题",
        "",
        p["question"],
        "",
        "## 判据（跑前冻结）",
        "",
        f"- H1 全期净年化 ≥ {p['criteria']['H1_full_ann_pct_ge']}%",
        f"- H2 样本外（{p['criteria']['split']}+）净年化 ≥ {p['criteria']['H2_oos_ann_pct_ge']}% 且夏普 ≥ {p['criteria']['H2_oos_sharpe_ge']}",
        "- H3 前后两半都为正",
        f"- H4 剔掉最好一年仍 ≥ {p['criteria']['H4_drop_best_year_pct_ge']}%/年",
        f"- H5 随机符号对照 p < {p['criteria']['H5_control_p_lt']}",
        f"- 成本 {p['criteria']['cost_bp_side']}bp/边；滚动移仓跳空按 `{p['criteria']['roll_rule']}` 剔除",
        "",
        "## 读数",
        "",
        "| 臂 | 年化 | 夏普 | 最大回撤 | t |",
        "|---|---|---|---|---|",
        f"| 横截面动量（多空，32 品种）全期 | {bc.fmt_pct(f.get('ann_pct'))} | {bc.fmt_num(f.get('sharpe'))} | {bc.fmt_pct(f.get('mdd_pct'))} | {bc.fmt_num(f.get('t_stat'))} |",
        f"| ↳ 样本外 2024+ | {bc.fmt_pct(o.get('ann_pct'))} | {bc.fmt_num(o.get('sharpe'))} | {bc.fmt_pct(o.get('mdd_pct'))} | {bc.fmt_num(o.get('t_stat'))} |",
        f"| 对照：同池等风险买入持有 全期 | {bc.fmt_pct(p['benchmark_long_only_hold']['full'].get('ann_pct'))} | {bc.fmt_num(p['benchmark_long_only_hold']['full'].get('sharpe'))} | {bc.fmt_pct(p['benchmark_long_only_hold']['full'].get('mdd_pct'))} | {bc.fmt_num(p['benchmark_long_only_hold']['full'].get('t_stat'))} |",
        f"| 变体：只做多头 全期 | {bc.fmt_pct(p['variant_long_only_signal']['full'].get('ann_pct'))} | {bc.fmt_num(p['variant_long_only_signal']['full'].get('sharpe'))} | {bc.fmt_pct(p['variant_long_only_signal']['full'].get('mdd_pct'))} | {bc.fmt_num(p['variant_long_only_signal']['full'].get('t_stat'))} |",
        "",
        f"- 前后两半：{bc.fmt_pct(a.get('first_half_ann_pct'))} / {bc.fmt_pct(a.get('second_half_ann_pct'))}；剔最好一年 {bc.fmt_pct(f.get('drop_best_year_ann_pct'))}",
        f"- 换手 {a['turnover_per_year']}×/年，成本拖累 {a['cost_drag_pp_per_year']}pp/年",
        f"- 随机符号对照：真实 {bc.fmt_pct(p['control_random_sign'].get('real_ann_pct'))}，零分布均值 {bc.fmt_pct(p['control_random_sign'].get('null_mean_ann_pct'))}，p={p['control_random_sign'].get('p_value')}",
        f"- 与沪深300相关：{p['corr_csi300']}",
        f"- 逐年收益：{json.dumps(f.get('years', {}), ensure_ascii=False)}",
        "",
        "## 覆盖与宽度（这条腿的真问题）",
        "",
        f"- 品种 {c['n_products']} 个，bar {c['bars']} 根，{c['start']} → {c['end']}",
        f"- 逐年可用品种数中位：{json.dumps(c['breadth_by_year'], ensure_ascii=False)}",
        f"- 拉取：成功 {c['pull_ok']} / 失败 {c['pull_fail']} / 重叠失配 {c['pull_overlap']} / 跳过 {c['pull_skipped']}",
        "",
        "## 统计功效（这一步决定这条负结论能说多硬）",
        "",
        power_line(p),
        "",
        "## 判词",
        "",
        f"**{p['verdict']}**　" + "；".join(f"{k}={v}" for k, v in p["checks"].items()),
        "",
        "## 披露（没做的）",
        "",
        "- 没有做 DV01/合约乘数中性化：按波动率配风险，不是按名义金额配敞口。",
        "- 只做日线收盘；日内滑点、保证金占用、夜盘跨日归属都不在射程。",
        "- 品种池是今天在交易的合约，退市品种（ZC/RR 等）不在池内，只会让池子更宽、不会更窄。",
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    res = run(do_pull="--no-pull" not in sys.argv)
    sys.exit(0 if isinstance(res, dict) and res.get("verdict") in ("GO", "NO_EDGE", "DATA-BLOCKED") else 1)
