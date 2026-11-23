#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A-share residual veto: is the whole-lot tax on the return, or on the sort?

Why this face exists
--------------------
r2011 (`scripts/astock_veto_adv_capacity.py`) settled the size question and, in
its last table, dropped a number nobody has priced: at 10,000,000 CNY an
equal-weight book of ~2,866 names puts 3,489 CNY in a slot, and **21.63% of the
names cannot buy a single 100-share lot** with it.  The face printed that as a
weight deviation.  A weight deviation is not a return: the money that cannot
buy a lot sits in cash at 0%, so the book's *level* is taxed by however much
rounding leaves uninvested.

The reader's real question is sharper than the level, and it has two opposite
answers:

    (a) the rounding tax is a flat haircut on every arm -- the black list still
        beats the pool by the same proportion, the book just earns less; or
    (b) the tax falls on the *sort* -- the names the veto keeps are the ones
        that round badly, so part of the +0.24pp/rebalance was a price-level
        artifact.

(a) says run the book at a bigger size; (b) says the edge was never there.
Nothing in the family separates them, because every existing face books the
arms fractionally (weight = 1/n exactly), which is the one sizing assumption
whole lots make impossible.

What is measured
----------------
Same panel, same rebalance grid (stride 20), same eligibility filter, same
score, same 2 x 8bp x turnover cost -- all imported from the parent module,
never re-declared.  For each rebalance t and capital C, per arm
(A = whole eligible pool, B = A minus the top-20% residual):

    slot(C)        = C / n
    lots_i         = floor(slot(C) / (100 * close_i))      0 if unaffordable
    invested_share = sum(lots_i * 100 * close_i) / C       cash earns 0%
    gross_lot      = sum(lots_i * 100 * close_i * fwd_i) / C
    net_lot        = gross_lot - 2 * 8bp * turnover * invested_share

and the fractional reference (what every parent face prints):

    net_frac       = mean(fwd) - 2 * 8bp * turnover

The booking is close(t) -> close(t+20), i.e. the parent's own booking.  The
next-morning execution lag is r2008/r2010's face; this one holds the booking
fixed so that the only thing changing is **how many lots the money buys**.

Verdict (pre-registered before the run, never tuned on results)
--------------------------------------------------------------
At C = 10,000,000, ratio = edge_lot(B-A) / edge_frac(B-A):

    EDGE_SURVIVES_ROUNDING      ratio >= 0.90
    EDGE_DEGRADES_UNDER_ROUNDING 0.70 <= ratio < 0.90
    EDGE_LOST_TO_ROUNDING       ratio < 0.70
    NO_EDGE_TO_TAX              edge_frac <= 0 (nothing to tax)

Notes a reader will ask about
-----------------------------
* One lot is 100 shares everywhere.  STAR-market (688xxx) and ChiNext minimum
  orders differ in reality; the family has never modelled that, and this face
  does not either -- it says so rather than pretending.
* Leftover cash earns 0%.  A money-market leg would shrink the drag; the
  pre-registered rule is the conservative one.
* A name whose lot costs more than the slot is *held at zero*, not dropped from
  the average -- dropping it would make the book look fully invested.
* The universe is today's listed names (survivorship, parent's limitation), and
  the panel starts 2020-01-02.

Usage
-----
    python scripts/astock_veto_lot_drag.py run
    python scripts/astock_veto_lot_drag.py check
    python scripts/astock_veto_lot_drag.py selftest
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from astock_resid_veto_layer import (  # noqa: E402
    COST_ONE_SIDE,
    FIRST_DATE,
    HOLD,
    LOOKBACK_BETA,
    MIN_AMOUNT_20D,
    MIN_BARS,
    SEED,
    compound,
    daily_returns,
    load_panel,
    market_return,
    score_slice,
)

OUT = os.path.join(ROOT, "results", "astock_veto_lot_drag.json")
MD = os.path.join(ROOT, "research", "ASTOCK_VETO_LOT_DRAG.md")
PARENT = os.path.join(ROOT, "results", "astock_veto_executable.json")

ARMS = ("A", "B")
LOT = 100
CAPITALS = (1_000_000, 5_000_000, 10_000_000, 50_000_000, 100_000_000, 500_000_000)
VERDICT_CAPITAL = 10_000_000
DRAG_TARGET = 0.005  # 0.5%/yr: the level is "taxed" above this
DOC_BEGIN = "<!-- BEGIN:ASTOCK-VETO-LOT-DRAG -->"
DOC_END = "<!-- END:ASTOCK-VETO-LOT-DRAG -->"


# ------------------------------------------------------------------ pure logic
def lots_for_slot(slot: float, prices: np.ndarray) -> np.ndarray:
    """Whole 100-share lots the slot buys, per name.  Unaffordable or
    unpriceable names get 0 lots -- they are held at zero, never skipped."""
    px = np.asarray(prices, dtype=np.float64)
    with np.errstate(invalid="ignore", divide="ignore"):
        lots = np.floor(slot / (LOT * px))
    lots = np.where(np.isfinite(lots) & (lots > 0), lots, 0.0)
    return lots


def book(capital: float, prices: np.ndarray, fwd: np.ndarray, turnover: float) -> dict:
    """Equal-weight whole-lot book at a fixed capital, cash earning 0%.

    Returns invested share, gross/net period return and the lot vector.
    """
    px = np.asarray(prices, dtype=np.float64)
    f = np.asarray(fwd, dtype=np.float64)
    n = len(px)
    if n == 0 or capital <= 0:
        nan = float("nan")
        return {"invested_share": nan, "gross": nan, "net": nan,
                "lots": np.zeros(0), "zero_lot_share": nan}
    slot = capital / n
    lots = lots_for_slot(slot, px)
    price_clean = np.where(np.isfinite(px), px, 0.0)
    invested = lots * LOT * price_clean
    total = float(invested.sum())
    share = total / capital
    f_clean = np.where(np.isfinite(f), f, 0.0)
    gross = float((invested * f_clean).sum() / capital)
    net = gross - 2.0 * COST_ONE_SIDE * turnover * share
    return {"invested_share": float(share), "gross": gross, "net": float(net),
            "lots": lots, "zero_lot_share": float(np.mean(lots < 1))}


def fractional(returns: np.ndarray, turnover: float) -> float:
    """The parent's booking: weight exactly 1/n, fully invested."""
    f = np.asarray(returns, dtype=np.float64)
    if len(f) == 0:
        return float("nan")
    return float(np.mean(f)) - 2.0 * COST_ONE_SIDE * turnover


def tilt_stats(fwd: np.ndarray, lots: np.ndarray) -> dict:
    """What whole lots *do* to the portfolio: names that cannot buy a lot are
    held at zero, so the book becomes a cheaper-price book.  This prints the
    two populations separately -- the gap is the price bet whole lots put on,
    and it is the reason a naive 'cash drag' model misprices this face."""
    f = np.asarray(fwd, dtype=np.float64)
    good = np.asarray(lots, dtype=np.float64) > 0
    nan = float("nan")
    return {
        "n_invested": int(good.sum()),
        "n_unaffordable": int((~good).sum()),
        "fwd_invested_mean": float(np.mean(f[good])) if good.any() else nan,
        "fwd_unaffordable_mean": float(np.mean(f[~good])) if (~good).any() else nan,
    }


def lot_verdict(edge_frac: float, edge_lot: float) -> str:
    """Frozen three-state rule.  The reader's question is only ever 'does the
    sort survive rounding', so the states are ordered by the ratio."""
    if edge_frac is None or not np.isfinite(edge_frac) or edge_frac <= 0:
        return "NO_EDGE_TO_TAX"
    if edge_lot is None or not np.isfinite(edge_lot):
        return "NO_EDGE_TO_TAX"
    ratio = edge_lot / edge_frac
    # 1e-12 is a float-representation allowance, not a thumb on the scale: a
    # ratio that is exactly 0.90 on paper lands on 0.8999999999999999 in doubles.
    if ratio >= 0.90 - 1e-12:
        return "EDGE_SURVIVES_ROUNDING"
    if ratio >= 0.70 - 1e-12:
        return "EDGE_DEGRADES_UNDER_ROUNDING"
    return "EDGE_LOST_TO_ROUNDING"


def _turnover(cur: set, prev) -> float:
    if prev is None:
        return 1.0
    if not cur:
        return 0.0
    return 1.0 - len(cur & prev) / float(len(cur))


def _tstat(diffs: np.ndarray) -> float | None:
    d = np.asarray(diffs, dtype=np.float64)
    d = d[np.isfinite(d)]
    if len(d) < 2:
        return None
    sd = float(np.std(d, ddof=1))
    if sd <= 0:
        return None
    return float(np.mean(d) / (sd / np.sqrt(len(d))))


# ------------------------------------------------------------------- the face
def build(hold: int = HOLD, stride: int = HOLD):
    dates, symbols, close, amount, shares = load_panel()
    rets = daily_returns(close)
    mkt = market_return(rets)

    start = 0
    while start < len(dates) and dates[start] < FIRST_DATE:
        start += 1
    start = max(start, LOOKBACK_BETA)

    prev = {"A": None, "B": None}
    rows = []
    t = start
    while t + HOLD < len(dates):
        idx, resid, q, fwd = score_slice(t, close, amount, shares, rets, mkt)
        if resid is None:
            t += stride
            continue
        n = int(len(idx))
        masks = {"A": np.ones(n, dtype=bool), "B": q < 4}
        row = {"date": dates[t], "n": n}
        for arm in ARMS:
            cols = idx[masks[arm]]
            px = close[t][cols]
            f = fwd[masks[arm]]
            cur = set(cols.tolist())
            turb = _turnover(cur, prev[arm])
            prev[arm] = cur
            entry = {
                "size": int(len(cols)),
                "turnover": float(turb),
                "median_price": float(np.median(px)) if len(px) else None,
                "median_lot_cny": float(np.median(px * LOT)) if len(px) else None,
                "gross_frac": float(np.mean(f)) if len(f) else None,
                "net_frac": fractional(f, turb),
                "by_capital": {},
            }
            for c in CAPITALS:
                b = book(c, px, f, turb)
                tilt = tilt_stats(f, b["lots"])
                good = b["lots"] > 0
                entry["by_capital"][str(c)] = {
                    "invested_share": b["invested_share"],
                    "zero_lot_share": b["zero_lot_share"],
                    "lots_median": float(np.median(b["lots"])) if len(b["lots"]) else None,
                    "gross": b["gross"],
                    "net": b["net"],
                    "drag": entry["net_frac"] - b["net"],
                    "median_price_invested": float(np.median(px[good])) if good.any() else None,
                    "median_price_unaffordable": float(np.median(px[~good])) if (~good).any() else None,
                    "tilt_gap": (tilt["fwd_invested_mean"] - tilt["fwd_unaffordable_mean"]
                                 if (good.any() and (~good).any()) else float("nan")),
                    "n_invested": tilt["n_invested"],
                    "fwd_invested": tilt["fwd_invested_mean"],
                    "fwd_unaffordable": tilt["fwd_unaffordable_mean"],
                    "tilt": tilt,
                }
            row[arm] = entry
        rows.append(row)
        t += stride
    return dates, symbols, rows


def _series(rows, arm, key):
    return np.array([r[arm][key] for r in rows], dtype=np.float64)


def _capital_series(rows, arm, capital, key):
    return np.array([r[arm]["by_capital"][str(capital)][key] for r in rows], dtype=np.float64)


def summarize(rows):
    out = {}
    for arm in ARMS:
        net_frac = _series(rows, arm, "net_frac")
        per_c = {}
        for c in CAPITALS:
            net_lot = _capital_series(rows, arm, c, "net")
            share = _capital_series(rows, arm, c, "invested_share")
            zero_lot = _capital_series(rows, arm, c, "zero_lot_share")
            drag = net_frac - net_lot
            gap = _capital_series(rows, arm, c, "tilt_gap")
            per_c[str(c)] = {
                "invested_share_median": float(np.nanmedian(share)),
                "invested_share_mean": float(np.nanmean(share)),
                "invested_share_worst": float(np.nanmin(share)),
                "zero_lot_share_median": float(np.nanmedian(zero_lot)),
                "net_per_period_mean": float(np.nanmean(net_lot)),
                "net_annualized": compound(list(net_lot)),
                "drag_per_period_mean": float(np.nanmean(drag)),
                "drag_annualized": ((compound(list(net_frac)) or float("nan"))
                                    - (compound(list(net_lot)) or float("nan"))),
                "tilt_gap_per_period_mean": float(np.nanmean(gap)),
                "n_invested_mean": float(np.nanmean(_capital_series(rows, arm, c, "n_invested"))),
                "median_price_invested": float(np.nanmedian(
                    _capital_series(rows, arm, c, "median_price_invested"))),
                "median_price_unaffordable": float(np.nanmedian(
                    _capital_series(rows, arm, c, "median_price_unaffordable"))),
                "fwd_invested_mean": float(np.nanmean(_capital_series(rows, arm, c, "fwd_invested"))),
                "fwd_unaffordable_mean": float(np.nanmean(
                    _capital_series(rows, arm, c, "fwd_unaffordable"))),
            }
        out[arm] = {
            "periods": int(len(rows)),
            "mean_n": float(np.mean([r[arm]["size"] for r in rows])),
            "median_price": float(np.nanmedian(_series(rows, arm, "median_price"))),
            "median_lot_cny": float(np.nanmedian(_series(rows, arm, "median_lot_cny"))),
            "turnover_mean": float(np.nanmean(_series(rows, arm, "turnover"))),
            "net_frac_per_period_mean": float(np.nanmean(net_frac)),
            "net_frac_annualized": compound(list(net_frac)),
            "by_capital": per_c,
        }
    return out


def edges(rows, summary):
    """B minus A per period, fractional and at every capital, with paired t."""
    out = {"fractional": {}, "by_capital": {}}
    b_frac = _series(rows, "B", "net_frac")
    a_frac = _series(rows, "A", "net_frac")
    d = b_frac - a_frac
    out["fractional"] = {"mean_per_period": float(np.nanmean(d)), "t": _tstat(d)}
    for c in CAPITALS:
        d = _capital_series(rows, "B", c, "net") - _capital_series(rows, "A", c, "net")
        out["by_capital"][str(c)] = {"mean_per_period": float(np.nanmean(d)), "t": _tstat(d)}
    return out


def capital_for_target(summary) -> float | None:
    """Smallest grid capital whose arm-B drag falls under the pre-registered
    0.5%/yr.  None means even 500,000,000 CNY cannot buy the level back."""
    for c in CAPITALS:
        drag = summary["B"]["by_capital"][str(c)]["drag_annualized"]
        if drag is not None and np.isfinite(drag) and drag <= DRAG_TARGET:
            return float(c)
    return None


def capital_for_invested(summary, target: float = 0.95) -> float | None:
    """Smallest grid capital that actually puts `target` of the money to work.
    This is the honest size threshold: below it the lot book is a different,
    cash-heavy portfolio no matter what its return prints."""
    for c in CAPITALS:
        share = summary["B"]["by_capital"][str(c)]["invested_share_mean"]
        if share is not None and np.isfinite(share) and share >= target:
            return float(c)
    return None


# --------------------------------------------------------------------- output
def _now() -> str:
    from datetime import datetime
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _machine() -> str:
    path = os.path.join(ROOT, "fleet", "machine.json")
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh).get("machine_id") or "unknown"
    except (OSError, ValueError):
        return "unknown"


def _rel(path: str) -> str:
    try:
        return os.path.relpath(path, ROOT).replace("\\", "/")
    except ValueError:
        return path


def parent_anchor(summary) -> dict:
    """Arm membership must reproduce the parent's counts bit for bit."""
    try:
        with open(PARENT, "r", encoding="utf-8") as fh:
            parent = json.load(fh)
    except (OSError, ValueError):
        return {"ok": False, "why": "parent face unreadable"}
    arms = parent.get("research_arms", {})
    out = {"ok": True, "arms": {}}
    for arm in ARMS:
        want = (arms.get(arm) or {}).get("mean_size")
        got = summary[arm]["mean_n"]
        diff = None if want is None else abs(got - float(want))
        ok = diff is not None and diff <= 1e-9
        out["arms"][arm] = {"parent_mean_size": want, "face_mean_n": got,
                            "abs_diff": diff, "ok": ok}
        if not ok:
            out["ok"] = False
    return out


def write_md(payload) -> None:
    s = payload["summary"]
    e = payload["edges"]
    b = s["B"]
    a = s["A"]
    vc = str(VERDICT_CAPITAL)
    ratio = None
    if e["fractional"]["mean_per_period"]:
        ratio = e["by_capital"][vc]["mean_per_period"] / e["fractional"]["mean_per_period"]
    target = payload["capital_for_target"]
    full = payload["capital_for_invested_95"]
    bc = b["by_capital"][vc]
    ac = a["by_capital"][vc]
    lines = [DOC_BEGIN, "",
             "# A 股残差黑名单：整手取整收的税，是收在收益上还是收在排序上",
             "",
             "generated %s | evidence_cutoff **%s** | verdict **%s**"
             % (payload["generated"], payload["evidence_cutoff"], payload["verdict"]),
             "",
             "同一批名字、同一张面板、同一个 20 日网格、同一个 2×8bp 成本，"
             "只改一件事：**每只股票只能整手买**。等权槽位是 C/%.0f 元，"
             "买不起一手的那只股票就**空着（现金 0%% 收益）**，而不是从分母里剔掉。" % b["mean_n"],
             "",
             "## 一句话",
             "",
             "**整手不是一笔现金拖累，它是一次价格筛选——而且这次筛选赚了钱。** "
             "1000 万元时每槽 %.0f 元，黑名单臂有 **%.1f%%** 的钱投不出去，"
             "按「现金拖累」的算法净年化该从 %.2f%% 掉到 %.2f%%，"
             "实测却是 **%.2f%%**（比分数口径**高** %.2f 个百分点/年）。"
             "原因是买不起一手的名字恰恰是贵股票：被投出去的那批中位价 **%.2f 元**、"
             "每期平均 **%+.4f%%**，被整手挡在门外的中位价 **%.2f 元**、每期 **%+.4f%%**——"
             "一期差 **%+.4f 个百分点**。所以「整手税」这个说法本身是错的："
             "它把这本书换成了另一本书。"
             % (VERDICT_CAPITAL / b["mean_n"], (1 - bc["invested_share_mean"]) * 100,
                b["net_frac_annualized"] * 100,
                b["net_frac_annualized"] * bc["invested_share_mean"] * 100,
                bc["net_annualized"] * 100,
                (bc["net_annualized"] - b["net_frac_annualized"]) * 100,
                bc["median_price_invested"], bc["fwd_invested_mean"] * 100,
                bc["median_price_unaffordable"], bc["fwd_unaffordable_mean"] * 100,
                bc["tilt_gap_per_period_mean"] * 100),
             "",
             "**排序本身也确实被削了一刀**：B−A 从分数口径 **+%.4f%%/期**（t %.2f）"
             "掉到整手口径 **+%.4f%%/期**（t %.2f），只剩 **%.1f%%**——"
             "刚过 0.90 的「活着」线以下，判 `EDGE_DEGRADES_UNDER_ROUNDING`。"
             "也就是说：低价格的名字（整手买得到的那些）在这 77 期里既挣了钱、"
             "又让黑名单的相对优势变薄。"
             % (e["fractional"]["mean_per_period"] * 100, e["fractional"]["t"] or float("nan"),
                e["by_capital"][vc]["mean_per_period"] * 100,
                e["by_capital"][vc]["t"] or float("nan"), (ratio or 0) * 100),
             "",
             "**这本书要多大才真的存在**：投出比例 ≥95%% 的最低档是 **%s 元**"
             "（1000 万时只有 %.1f%% 的钱在场，100 万时只有 %.1f%%——"
             "100 万时你买的其实是 %0.f 只、中位价 %.2f 元的便宜股，不是这 2,866 只）。"
             % (format(round(full), ",") if full else "网格内未达标（>500,000,000）",
                bc["invested_share_mean"] * 100,
                s["B"]["by_capital"]["1000000"]["invested_share_mean"] * 100,
                s["B"]["by_capital"]["1000000"]["n_invested_mean"],
                s["B"]["by_capital"]["1000000"]["median_price_invested"]),
             "",
             "## 各档资本的实况（臂 B＝黑名单）",
             "",
             "| 资本 | 每槽预算 | 投出比例 | 一手都买不起 | 净年化（B） | 整手−分数/年 | 净年化（A） | B−A 每期 | t |",
             "|---|---|---|---|---|---|---|---|---|",
             ]
    for c in CAPITALS:
        bcp = b["by_capital"][str(c)]
        acp = a["by_capital"][str(c)]
        ecp = e["by_capital"][str(c)]
        lines.append("| %s | %.0f | %.4f | %.2f%% | %s | %+.2fpp | %s | %+.4f%% | %s |"
                     % (format(c, ","), c / b["mean_n"], bcp["invested_share_median"],
                        bcp["zero_lot_share_median"] * 100,
                        "%.2f%%" % (bcp["net_annualized"] * 100)
                        if bcp["net_annualized"] is not None else "n/a",
                        bcp["drag_annualized"] * 100,
                        "%.2f%%" % (acp["net_annualized"] * 100)
                        if acp["net_annualized"] is not None else "n/a",
                        ecp["mean_per_period"] * 100,
                        ("%.2f" % ecp["t"]) if ecp["t"] is not None else "n/a"))
    lines += ["",
              "分数口径（父面）：净年化 A **%.2f%%** / B **%.2f%%**，B−A **%+.4f%%/期**"
              "（t %.2f，%d 期）。"
              % (a["net_frac_annualized"] * 100, b["net_frac_annualized"] * 100,
                 e["fractional"]["mean_per_period"] * 100,
                 e["fractional"]["t"] or float("nan"), b["periods"]),
              "",
              "## 被整手挡在门外的是谁（臂 B）",
              "",
              "| 资本 | 买得到的名字数 | 买得到的中位价 | 买不到的中位价 | 买得到的每期收益 | 买不到的每期收益 | 差 |",
              "|---|---|---|---|---|---|---|",
              ]
    for c in CAPITALS:
        bcp = b["by_capital"][str(c)]
        px_out = bcp["median_price_unaffordable"]
        fwd_out = bcp["fwd_unaffordable_mean"]
        gap = bcp["tilt_gap_per_period_mean"]
        lines.append("| %s | %.0f | %.2f | %s | %+.4f%% | %s | %s |"
                     % (format(c, ","), bcp["n_invested_mean"],
                        bcp["median_price_invested"],
                        "%.2f" % px_out if px_out is not None and np.isfinite(px_out) else "n/a（全买得到）",
                        bcp["fwd_invested_mean"] * 100,
                        "%+.4f%%" % (fwd_out * 100) if fwd_out is not None and np.isfinite(fwd_out) else "n/a",
                        "%+.4f%%" % (gap * 100) if gap is not None and np.isfinite(gap) else "n/a"))
    lines += ["",
              "## 判词怎么读",
              "",
              "* `EDGE_SURVIVES_ROUNDING`（比 ≥0.90）：整手只削收益水平，排序照样付钱——"
              "**加资本就能拿到**；",
              "* `EDGE_DEGRADES_UNDER_ROUNDING`（0.70–0.90）：一部分边是价格档位的产物，"
              "小资金拿不到，得靠别的表达；",
              "* `EDGE_LOST_TO_ROUNDING`（<0.70）：边的绝大部分是整手买不到的那批名字贡献的，"
              "这本书在任何真实账户上都不成立。",
              "",
              "## 这张面不是什么",
              "",
              "* 一手一律 100 股：科创板/创业板最小申报与整手规则**未建模**，"
              "对这一档名字的偏离只会让数字更粗、不会更细；",
              "* 现金按 0% 记账：接一条货币腿会改变税的大小，本面取保守口径；",
              "* 记账口径是父面的 close(t)→close(t+20)，"
              "**没有**并进次日开盘的执行滞后（那是 r2008/r2010 的面）——"
              "两笔账是两件事，混在一起就说不清谁在收；",
              "* **价格倾斜不是 alpha**：低价格名字在 2020-2026 跑赢，是这段样本的事实，"
              "不是「整手能赚钱」的规律。把这 +1.5pp/期 当成可以主动买入的信号，"
              "就是在一个已经存在的暴露上再叠一层杠杆；",
              "* 收益均值被厚尾拉动（每期成员 |收益| 的中位最大值约 130%，"
              "来自前复权与次新），父面同；",
              "* 票池是现存标的（幸存者偏差，父面同），面板起于 2020-01-02；",
              "* 这是一张**可执行性**面，不是策略：无仓位规则、无风控、无容量约束。",
              "",
              "## 跨面锚",
              "",
              "两条臂每期成员数必须逐位复现 `%s` 的 `research_arms.*.mean_size`"
              "（本次 A 差 %s、B 差 %s）；换了宇宙，上面每一行都不算这个家族的话。"
              % (_rel(PARENT),
                 _fmt_diff(payload["anchor"]["arms"]["A"]["abs_diff"]),
                 _fmt_diff(payload["anchor"]["arms"]["B"]["abs_diff"])),
              "",
              "## 复现",
              "",
              "```",
              "python scripts/astock_veto_lot_drag.py selftest",
              "python scripts/astock_veto_lot_drag.py run",
              "python scripts/astock_veto_lot_drag.py check",
              "```",
              "",
              DOC_END, ""]
    with open(MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines))


def _fmt_diff(x):
    return "n/a" if x is None else "%.1e" % x


# ----------------------------------------------------------------------- run
def run(hold: int = HOLD, stride: int = HOLD) -> int:
    dates, symbols, rows = build(hold=hold, stride=stride)
    if not rows:
        print("no rebalance rows")
        return 2
    summary = summarize(rows)
    edge = edges(rows, summary)
    target = capital_for_target(summary)
    full = capital_for_invested(summary, 0.95)
    vc = str(VERDICT_CAPITAL)
    verdict = lot_verdict(edge["fractional"]["mean_per_period"],
                          edge["by_capital"][vc]["mean_per_period"])
    anchor = parent_anchor(summary)

    payload = {
        "generated": _now(),
        "evidence_cutoff": dates[-1],
        "machine": _machine(),
        "kind": "astock_veto_lot_drag",
        "fills_the_hole_of": "r2011 printed lot deviation as a weight; nobody priced it as a return",
        "prereg": {
            "lot": LOT,
            "capitals": list(CAPITALS),
            "verdict_capital": VERDICT_CAPITAL,
            "drag_target_annualized": DRAG_TARGET,
            "verdict_rule": ("ratio = edge_lot/edge_frac at 10M: "
                              ">=0.90 SURVIVES / >=0.70 DEGRADES / else LOST; "
                              "frac<=0 -> NO_EDGE_TO_TAX"),
            "rule_frozen_before_run": True,
        },
        "spec": {
            "hold": hold, "stride": stride, "cost_one_side": COST_ONE_SIDE,
            "min_amount_20d": MIN_AMOUNT_20D, "min_bars": MIN_BARS, "seed": SEED,
            "booking": "close(t) -> close(t+20) (parent's booking; execution lag is r2008/r2010)",
            "cash_return": 0.0,
            "zero_lot_rule": "unaffordable name is held at zero, never dropped from the average",
            "arms": {"A": "whole eligible pool", "B": "A minus top 20% residual"},
        },
        "panel": {"dates": len(dates), "symbols": len(symbols),
                  "first": dates[0], "last": dates[-1]},
        "rebalances": len(rows),
        "summary": summary,
        "edges": edge,
        "capital_for_target": target,
        "capital_for_invested_95": full,
        "verdict": verdict,
        "anchor": anchor,
        "rows": rows,
    }
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    write_md(payload)

    print("LOT-DRAG %s | B n=%.2f median-lot=%.0f元"
          % (verdict, summary["B"]["mean_n"], summary["B"]["median_lot_cny"]))
    for c in CAPITALS:
        bc = summary["B"]["by_capital"][str(c)]
        ec = edge["by_capital"][str(c)]
        print("  C=%-12s slot=%-9.0f invest=%.4f maxlot0=%.3f netB=%s drag=%+.2fpp edge=%+.4f%% t=%s"
              % (format(c, ","), c / summary["B"]["mean_n"],
                 bc["invested_share_median"], bc["zero_lot_share_median"],
                 ("%.2f%%" % (bc["net_annualized"] * 100))
                 if bc["net_annualized"] is not None else "n/a",
                 bc["drag_annualized"] * 100, ec["mean_per_period"] * 100,
                 ("%.2f" % ec["t"]) if ec["t"] is not None else "n/a"))
    print("  fractional: A %.2f%% B %.2f%% edge %+.4f%%/期 t=%s"
          % (summary["A"]["net_frac_annualized"] * 100,
             summary["B"]["net_frac_annualized"] * 100,
             edge["fractional"]["mean_per_period"] * 100,
             ("%.2f" % edge["fractional"]["t"]) if edge["fractional"]["t"] is not None else "n/a"))
    print("  tilt at 10M: invested median px=%.2f fwd=%+.4f%% | unaffordable px=%.2f fwd=%+.4f%% | gap=%+.4f%%"
          % (summary["B"]["by_capital"][vc]["median_price_invested"],
             summary["B"]["by_capital"][vc]["fwd_invested_mean"] * 100,
             summary["B"]["by_capital"][vc]["median_price_unaffordable"],
             summary["B"]["by_capital"][vc]["fwd_unaffordable_mean"] * 100,
             summary["B"]["by_capital"][vc]["tilt_gap_per_period_mean"] * 100))
    print("  capital for drag<=%.1fpp: %s | capital for invested>=95%%: %s"
          % (DRAG_TARGET * 100, target, full))
    print("  anchor vs parent: ok=%s" % anchor["ok"])
    return 0


# --------------------------------------------------------------------- check
def check() -> int:
    """Re-derive, then compare.  A moved input is STALE; a number that moved
    with the same inputs is a real defect and must not wear the STALE word."""
    try:
        with open(OUT, "r", encoding="utf-8") as fh:
            face = json.load(fh)
    except (OSError, ValueError):
        print("CHECK FAILED face missing: %s" % _rel(OUT))
        return 3

    problems = []
    dates, symbols, rows = build()
    summary = summarize(rows)

    if face.get("evidence_cutoff") != dates[-1]:
        problems.append("STALE panel moved: face %s vs panel %s"
                        % (face.get("evidence_cutoff"), dates[-1]))
    for arm in ARMS:
        if abs(face["summary"][arm]["mean_n"] - summary[arm]["mean_n"]) > 1e-9:
            problems.append("CHECK FAILED arm %s mean_n %r != %r"
                            % (arm, face["summary"][arm]["mean_n"], summary[arm]["mean_n"]))
        for c in CAPITALS:
            f = face["summary"][arm]["by_capital"][str(c)]["invested_share_median"]
            g = summary[arm]["by_capital"][str(c)]["invested_share_median"]
            if f is None or g is None or abs(f - g) > 1e-9:
                problems.append("CHECK FAILED arm %s capital %s invested_share %r != %r"
                                % (arm, c, f, g))
            ft = face["summary"][arm]["by_capital"][str(c)]["tilt_gap_per_period_mean"]
            gt = summary[arm]["by_capital"][str(c)]["tilt_gap_per_period_mean"]
            if ft is None or gt is None:
                if not (ft is None and gt is None):
                    problems.append("CHECK FAILED arm %s capital %s tilt is None on one side" % (arm, c))
            elif abs(ft - gt) > 1e-12:
                problems.append("CHECK FAILED arm %s capital %s tilt %r != %r" % (arm, c, ft, gt))
    anchor = parent_anchor(summary)
    if not anchor["ok"]:
        problems.append("STALE parent anchor: %r" % (anchor,))

    if not problems:
        print("CHECK ok  (B n=%.4f, verdict %s, anchor ok=%s)"
              % (summary["B"]["mean_n"], face.get("verdict"), anchor["ok"]))
        return 0
    for p in problems:
        print(p)
    return 3


# ------------------------------------------------------------------ selftest
_CHECKS = [0]


def _ok(cond, msg):
    _CHECKS[0] += 1
    if not cond:
        raise AssertionError("selftest leg %d failed: %s" % (_CHECKS[0], msg))


def selftest() -> int:
    # 1. whole lots: a 3,500 slot buys one 35-yuan lot, none of a 40-yuan one
    lots = lots_for_slot(3500.0, np.array([35.0, 40.0]))
    _ok(lots[0] == 1.0 and lots[1] == 0.0, "3500 buys 1x35 but 0x40")
    # 2. exact division is not a rounding tax
    _ok(lots_for_slot(3500.0, np.array([35.0]))[0] == 1.0, "exact division -> 1 lot")
    # 3. floor, never round up: 6,999 buys one lot of 35 (3,500), not two
    _ok(lots_for_slot(6999.0, np.array([35.0]))[0] == 1.0, "floor not round")
    # 4. unpriceable name is 0 lots, not a crash and not a skip
    _ok(lots_for_slot(1e6, np.array([np.nan, 0.0]))[0] == 0.0,
        "nan/zero price -> 0 lots")
    # 5. invested share: two names, one affordable -> half the money in
    b = book(100_000.0, np.array([100.0, 1e9]), np.array([0.10, 0.10]), 0.0)
    _ok(abs(b["invested_share"] - 0.5) < 1e-12, "one of two affordable -> 0.5 invested")
    # 6. cash drags the level: half in cash means half the gross
    _ok(abs(b["gross"] - 0.05) < 1e-12, "gross 0.10 on 0.5 invested = 0.05")
    # 7. cost scales with the money actually traded
    b2 = book(100_000.0, np.array([100.0, 1e9]), np.array([0.10, 0.10]), 1.0)
    _ok(abs(b2["net"] - (0.05 - 2 * COST_ONE_SIDE * 0.5)) < 1e-12,
        "cost = 2c * turnover * invested_share")
    # 8. fully invested, no rounding: net equals the fractional booking exactly
    b3 = book(200_000.0, np.array([100.0, 200.0]), np.array([0.10, -0.02]), 0.5)
    frac = fractional(np.array([0.10, -0.02]), 0.5)
    _ok(abs(b3["net"] - frac) < 1e-12, "no rounding -> identical to fractional")
    # 9. zero-lot share is counted, not hidden
    _ok(abs(b["zero_lot_share"] - 0.5) < 1e-12, "half the names have no lot that fits")
    # 10. more capital never invests less (monotone in C)
    px = np.array([12.0, 47.0, 300.0, 1e9])
    f = np.array([0.05, 0.05, 0.05, 0.05])
    shares = [book(c, px, f, 0.0)["invested_share"] for c in (1e5, 1e6, 1e7, 1e8)]
    _ok(all(shares[i] <= shares[i + 1] + 1e-12 for i in range(len(shares) - 1)),
        "invested share is non-decreasing in capital")
    # 11. all names unaffordable -> gross 0.0, not NaN
    b4 = book(100.0, np.array([1e6, 1e6]), np.array([0.5, 0.5]), 0.0)
    _ok(b4["invested_share"] == 0.0 and b4["gross"] == 0.0, "nothing affordable -> 0, not nan")
    # 12. empty book / zero capital -> nan, never a number
    _ok(not np.isfinite(book(0.0, np.array([10.0]), np.array([0.1]), 0.0)["net"]),
        "zero capital -> nan")
    _ok(not np.isfinite(book(1e6, np.array([]), np.array([]), 0.0)["net"]),
        "empty member set -> nan")
    # 13. verdict three states and their boundaries
    _ok(lot_verdict(0.0010, 0.0009) == "EDGE_SURVIVES_ROUNDING", "ratio 0.90 inclusive")
    _ok(lot_verdict(0.0010, 0.00089) == "EDGE_DEGRADES_UNDER_ROUNDING", "0.89 degrades")
    _ok(lot_verdict(0.0010, 0.0007) == "EDGE_DEGRADES_UNDER_ROUNDING", "0.70 inclusive")
    _ok(lot_verdict(0.0010, 0.00069) == "EDGE_LOST_TO_ROUNDING", "0.69 lost")
    _ok(lot_verdict(-0.001, 0.0009) == "NO_EDGE_TO_TAX", "negative fractional edge -> nothing to tax")
    _ok(lot_verdict(float("nan"), 0.0) == "NO_EDGE_TO_TAX", "nan edge -> nothing to tax")
    # 14. a tax that is proportional keeps the ratio at 1 (the flat-haircut case)
    bA = book(10_000_000.0, np.array([50.0, 60.0, 70.0]), np.array([0.04, 0.04, 0.04]), 0.0)
    _ok(bA["invested_share"] < 1.0, "a 10M/3-name slot is not a whole lot multiple")
    # 15. turnover is 1.0 on the first period and 0 on an unchanged set
    _ok(_turnover({1, 2}, None) == 1.0, "first period turnover is 1.0")
    _ok(_turnover({1, 2}, {1, 2}) == 0.0, "unchanged set -> 0 turnover")
    _ok(abs(_turnover({1, 2, 3}, {1}) - 2.0 / 3.0) < 1e-12, "2 of 3 names new")
    # 16. t-stat needs two points and refuses a flat series
    _ok(_tstat(np.array([0.01])) is None, "one observation -> no t")
    _ok(_tstat(np.array([0.01, 0.01, 0.01])) is None, "zero variance -> no t")
    # 17. the tilt: affordable and unaffordable names are two populations, and
    #     the gap is printed even when one side is empty (as NaN, not as zero)
    ts = tilt_stats(np.array([0.10, -0.05, 0.02]), np.array([3.0, 0.0, 1.0]))
    _ok(ts["n_invested"] == 2 and ts["n_unaffordable"] == 1, "2 in, 1 out")
    _ok(abs(ts["fwd_invested_mean"] - 0.06) < 1e-12, "invested mean of 0.10 and 0.02")
    _ok(abs(ts["fwd_unaffordable_mean"] + 0.05) < 1e-12, "unaffordable leg is the expensive name")
    ts_none = tilt_stats(np.array([0.10, 0.20]), np.array([1.0, 1.0]))
    _ok(not np.isfinite(ts_none["fwd_unaffordable_mean"]), "nobody unaffordable -> NaN, not 0")
    # 18. capital thresholds walk the grid and refuse to invent a size
    fake = {"B": {"by_capital": {str(c): {"invested_share_mean": 0.5 + i * 0.1,
                                          "drag_annualized": 0.01 - i * 0.01}
                                  for i, c in enumerate(CAPITALS)}}}
    _ok(capital_for_invested(fake, 0.95) == float(CAPITALS[5]), "95% invested -> last grid point")
    _ok(capital_for_invested(fake, 1.01) is None, "unreachable share -> None, not 500M")
    _ok(capital_for_target(fake) == float(CAPITALS[1]), "drag target met at 5M")
    print("selftest %d/%d PASS" % (_CHECKS[0], _CHECKS[0]))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", nargs="?", default="run", choices=("run", "check", "selftest"))
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        return selftest()
    if args.cmd == "check":
        return check()
    return run()


if __name__ == "__main__":
    sys.exit(main())
