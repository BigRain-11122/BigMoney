"""A-share residual veto book: the one thing nobody wrote down -- how bumpy it is.

The family (r1865 and its ten follow-ups) has published the *mean* of this book
many times: research arms, executable arms, whole-lot arms, cash legs.  Every
one of those faces answers "how much per period".  Not one answers the question
a person who is about to fund it asks second: **what does the ride look like**.

So this face is a tearsheet, not a new idea:

  * for each arm (A = whole pool, B = pool minus top 20% residual) and each
    booking (fractional = the parent's, whole lots at 10,000,000 CNY), it prints
    period volatility, annualised volatility, Sharpe (excess over 0% cash),
    maximum drawdown of the compounded 20-trading-day curve, Calmar, hit rate,
    the worst single period and the worst half-year (6 consecutive periods);
  * it prices the turnover the veto rule costs: gross vs net per period, the
    cost as a share of gross, and the one-side commission at which the B-A edge
    would reach exactly zero (`breakeven_one_side_bp`) -- a physical number, not
    a threshold someone picked;
  * the verdict is a 2x2 with no invented cut-offs: does B's Sharpe beat A's,
    and is B's drawdown deeper?  Four states, both questions answered.

Reading rules that matter
-------------------------
* The drawdown is measured on the **20-trading-day period curve**, not on daily
  marks.  A daily-marks drawdown of a monthly-rebalanced book needs daily
  weights, which this family has never booked.  This face says so rather than
  printing a nicer-looking number it cannot support.
* Sharpe is excess over 0% cash.  The repo leg exists (r2013/r2014 price it at
  ~2.1 pp/yr) but it is common to both arms and shifts both Sharpe ratios up
  by roughly the same amount; it is disclosed, not folded in.
* Everything is recomputed from the panel (`astock_veto_lot_drag.build`), never
  copied from the published faces.  The published faces are used only as an
  anchor: their per-period means must come back bit-identical.
* No threshold was chosen to make a state look reachable: `SHARPE_UP` is a
  strict comparison, `DRAWDOWN_DEEPER` is a strict comparison.

Usage
-----
    python scripts/astock_veto_tearsheet.py run
    python scripts/astock_veto_tearsheet.py check
    python scripts/astock_veto_tearsheet.py selftest
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from astock_resid_veto_layer import COST_ONE_SIDE, HOLD, compound  # noqa: E402
from astock_veto_lot_drag import (  # noqa: E402
    ARMS,
    CAPITALS,
    LOT,
    VERDICT_CAPITAL,
    build,
)

OUT = os.path.join(ROOT, "results", "astock_veto_tearsheet.json")
MD = os.path.join(ROOT, "research", "ASTOCK_VETO_TEARSHEET.md")
PARENT = os.path.join(ROOT, "results", "astock_veto_lot_drag.json")

PPY = 252.0 / HOLD          # ~12.6 periods per year
ROLL_WINDOW = 6             # ~half a year of 20-bar periods
BOOKINGS = ("fractional", "lot_%d" % VERDICT_CAPITAL)
DOC_BEGIN = "<!-- BEGIN:ASTOCK-VETO-TEARSHEET -->"
DOC_END = "<!-- END:ASTOCK-VETO-TEARSHEET -->"


# ------------------------------------------------------------------ pure logic
def _finite(values) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64)
    return arr[np.isfinite(arr)]


def equity_curve(rets) -> np.ndarray:
    """Compounded wealth, starting at 1.0.  Non-finite periods are dropped, not
    treated as zero: a period we could not price is not a flat period."""
    r = _finite(rets)
    if len(r) == 0:
        return np.zeros(0)
    return np.cumprod(1.0 + r)


def _peak_curve(w: np.ndarray) -> np.ndarray:
    """Running peak that starts at the opening wealth of 1.0 -- without it a
    book that loses 10% on its FIRST period would report a 0% drawdown."""
    if len(w) == 0:
        return w
    return np.maximum.accumulate(np.concatenate(([1.0], w)))[1:]


def max_drawdown(rets):
    """Deepest peak-to-trough of the compounded curve, as a negative fraction.
    A monotone-up curve returns 0.0, never None and never a positive number."""
    w = equity_curve(rets)
    if len(w) == 0:
        return None
    return float(np.min(w / _peak_curve(w) - 1.0))


def underwater_share(rets):
    """Share of periods that closed below a previous peak -- how much of the
    book's life is spent recovering, which a drawdown number alone hides."""
    w = equity_curve(rets)
    if len(w) == 0:
        return None
    return float(np.mean(w < _peak_curve(w) - 1e-15))


def period_vol(rets):
    r = _finite(rets)
    if len(r) < 2:
        return None
    return float(np.std(r, ddof=1))


def annual_vol(rets):
    sd = period_vol(rets)
    return None if sd is None else float(sd * np.sqrt(PPY))


def sharpe(rets, rf_per_period: float = 0.0):
    """Excess of the period mean over a per-period cash rate, divided by the
    period volatility, annualised.  A flat or single-observation series has no
    Sharpe and says so (None) instead of printing 0."""
    r = _finite(rets)
    if len(r) < 2:
        return None
    sd = float(np.std(r, ddof=1))
    if sd <= 0:
        return None
    return float((float(np.mean(r)) - rf_per_period) / sd * np.sqrt(PPY))


def hit_rate(rets):
    r = _finite(rets)
    if len(r) == 0:
        return None
    return float(np.mean(r > 0))


def worst_window(rets, k: int = ROLL_WINDOW):
    """Worst compounded k-period stretch (chained, not summed).  A series
    shorter than the window has no such stretch -> None."""
    r = _finite(rets)
    if len(r) < k or k <= 0:
        return None
    windows = [float(np.prod(1.0 + r[i:i + k]) - 1.0) for i in range(len(r) - k + 1)]
    return float(min(windows))


def calmar(rets):
    cagr = compound(list(_finite(rets)))
    mdd = max_drawdown(rets)
    if cagr is None or mdd is None or mdd >= 0:
        return None
    return float(cagr / abs(mdd))


def tstat(diffs):
    d = _finite(diffs)
    if len(d) < 2:
        return None
    sd = float(np.std(d, ddof=1))
    if sd <= 0:
        return None
    return float(np.mean(d) / (sd / np.sqrt(len(d))))


def risk_verdict(sharpe_b, sharpe_a, mdd_b, mdd_a) -> str:
    """Two questions, no thresholds: did risk-adjusted return improve, and did
    the worst hole get deeper?  Both are strict comparisons."""
    vals = (sharpe_b, sharpe_a, mdd_b, mdd_a)
    if any(v is None or not np.isfinite(v) for v in vals):
        return "INSUFFICIENT_DATA"
    up = sharpe_b > sharpe_a
    deeper = mdd_b < mdd_a
    return ("SHARPE_UP_" if up else "SHARPE_DOWN_") + (
        "DRAWDOWN_DEEPER" if deeper else "DRAWDOWN_SHALLOWER")


def cost_block(gross, net) -> dict:
    """The bill: what the book earned before trading and what survived it."""
    g = _finite(gross)
    n = _finite(net)
    if len(g) == 0 or len(n) == 0:
        return {"gross_per_period_mean": None, "cost_per_period_mean": None,
                "cost_annualized": None, "cost_share_of_gross": None}
    gm = float(np.mean(g))
    nm = float(np.mean(n))
    cost = gm - nm
    return {
        "gross_per_period_mean": gm,
        "cost_per_period_mean": cost,
        "cost_annualized": float(cost * PPY),
        "cost_share_of_gross": (float(cost / gm) if gm > 0 else None),
    }


def breakeven_one_side(gross_edge, net_edge, turn_b, turn_a, cost_one_side):
    """The commission at which the B-A edge is exactly zero.

    net_edge(k) = gross_edge - k * 2c * (turn_b - turn_a), so
    k* = gross_edge / (2c * (turn_b - turn_a)) and the one-side fee at k* is
    k* * c.  Returns None when the edge is already gone, when the veto arm is
    not paying more turnover than the pool, or when the inputs are not numbers.
    """
    vals = (gross_edge, net_edge, turn_b, turn_a, cost_one_side)
    if any(v is None or not np.isfinite(v) for v in vals):
        return None
    d_turn = turn_b - turn_a
    if d_turn <= 0 or gross_edge <= 0 or cost_one_side <= 0:
        return None
    k = gross_edge / (2.0 * cost_one_side * d_turn)
    return {"k_multiple": float(k), "one_side_bp": float(k * cost_one_side * 1e4)}


def series_stats(rets) -> dict:
    r = _finite(rets)
    return {
        "periods": int(len(r)),
        "per_period_mean": float(np.mean(r)) if len(r) else None,
        "per_period_stdev": period_vol(r),
        "annualized_compound": compound(list(r)),
        "annual_vol": annual_vol(r),
        "sharpe_excess_0": sharpe(r),
        "max_drawdown": max_drawdown(r),
        "calmar": calmar(r),
        "hit_rate": hit_rate(r),
        "worst_period": float(np.min(r)) if len(r) else None,
        "best_period": float(np.max(r)) if len(r) else None,
        "worst_%d_periods" % ROLL_WINDOW: worst_window(r),
        "underwater_share": underwater_share(r),
    }


# -------------------------------------------------------------------- the face
def build_face(hold: int = HOLD, stride: int = HOLD):
    dates, symbols, rows = build(hold=hold, stride=stride)
    return dates, symbols, rows


def net_series(rows, arm, booking):
    if booking == "fractional":
        return np.array([r[arm]["net_frac"] for r in rows], dtype=np.float64)
    c = booking.split("_")[1]
    return np.array([r[arm]["by_capital"][c]["net"] for r in rows], dtype=np.float64)


def turnover_series(rows, arm):
    return np.array([r[arm]["turnover"] for r in rows], dtype=np.float64)


def gross_series(rows, arm):
    return np.array([r[arm]["gross_frac"] for r in rows], dtype=np.float64)


def summarize(rows) -> dict:
    out = {}
    for arm in ARMS:
        turn = _finite(turnover_series(rows, arm))
        share = _finite([r[arm]["by_capital"][str(VERDICT_CAPITAL)]["invested_share"]
                         for r in rows])
        out[arm] = {
            "turnover_mean": float(np.mean(turn)) if len(turn) else None,
            "turnover_median": float(np.median(turn)) if len(turn) else None,
            "turnover_max": float(np.max(turn)) if len(turn) else None,
            "invested_share_median_%s" % "lot_%d" % VERDICT_CAPITAL:
                float(np.median(share)) if len(share) else None,
            "gross": cost_block(gross_series(rows, arm), net_series(rows, arm, "fractional")),
            "bookings": {b: series_stats(net_series(rows, arm, b)) for b in BOOKINGS},
        }
    return out


def edges(rows, summary) -> dict:
    out = {"by_booking": {}}
    for b in BOOKINGS:
        d = net_series(rows, "B", b) - net_series(rows, "A", b)
        sb = summary["B"]["bookings"][b]
        sa = summary["A"]["bookings"][b]
        out["by_booking"][b] = {
            "mean_per_period": float(np.mean(_finite(d))),
            "t": tstat(d),
            "sharpe_of_the_difference": sharpe(d),
            "sharpe_b_minus_a": (None if sb["sharpe_excess_0"] is None
                                 or sa["sharpe_excess_0"] is None
                                 else float(sb["sharpe_excess_0"] - sa["sharpe_excess_0"])),
            "mdd_b_minus_a": (None if sb["max_drawdown"] is None
                              or sa["max_drawdown"] is None
                              else float(sb["max_drawdown"] - sa["max_drawdown"])),
            "verdict": risk_verdict(sb["sharpe_excess_0"], sa["sharpe_excess_0"],
                                    sb["max_drawdown"], sa["max_drawdown"]),
        }
    gb = summary["B"]["gross"]["gross_per_period_mean"]
    ga = summary["A"]["gross"]["gross_per_period_mean"]
    nb = summary["B"]["bookings"]["fractional"]["per_period_mean"]
    na = summary["A"]["bookings"]["fractional"]["per_period_mean"]
    gross_edge = None if gb is None or ga is None else float(gb - ga)
    net_edge = None if nb is None or na is None else float(nb - na)
    be = breakeven_one_side(gross_edge, net_edge,
                            summary["B"]["turnover_mean"], summary["A"]["turnover_mean"],
                            COST_ONE_SIDE)
    out["edge_tax"] = {
        "gross_edge_per_period": gross_edge,
        "net_edge_per_period": net_edge,
        "tax_per_period": (None if gross_edge is None or net_edge is None
                           else float(gross_edge - net_edge)),
        "tax_share_of_gross_edge": (None if gross_edge is None or net_edge is None
                                    or gross_edge <= 0
                                    else float((gross_edge - net_edge) / gross_edge)),
        "cost_actually_charged_one_side": COST_ONE_SIDE,
        "breakeven": be,
    }
    return out


def parent_anchor(summary) -> dict:
    """r2012's published means (fractional and at the verdict capital) and its
    turnover must come back bit-identical; this face may not re-price them."""
    try:
        with open(PARENT, "r", encoding="utf-8") as fh:
            parent = json.load(fh)
    except (OSError, ValueError) as exc:
        return {"ok": False, "why": "parent unreadable: %s" % exc, "worst_abs_diff": None}
    worst = 0.0
    for arm in ARMS:
        pairs = [
            (parent["summary"][arm]["net_frac_per_period_mean"],
             summary[arm]["bookings"]["fractional"]["per_period_mean"]),
            (parent["summary"][arm]["by_capital"][str(VERDICT_CAPITAL)]["net_per_period_mean"],
             summary[arm]["bookings"]["lot_%d" % VERDICT_CAPITAL]["per_period_mean"]),
            (parent["summary"][arm]["turnover_mean"], summary[arm]["turnover_mean"]),
        ]
        for p, mine in pairs:
            if p is None or mine is None:
                return {"ok": False, "why": "missing number arm=%s" % arm,
                        "worst_abs_diff": None}
            worst = max(worst, abs(float(p) - float(mine)))
    return {"ok": worst <= 1e-9, "worst_abs_diff": worst}


def _now() -> str:
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def _machine() -> str:
    try:
        with open(os.path.join(ROOT, "fleet", "machine.json"), "r", encoding="utf-8") as fh:
            return str(json.load(fh).get("machine_id", "unknown"))
    except (OSError, ValueError):
        return "unknown"


def _family_faces_before() -> int:
    """How many faces this family had published when this one ran -- counted,
    not hand-typed, so the doc cannot inflate the claim."""
    return len([f for f in glob.glob(os.path.join(ROOT, "results", "astock_veto_*.json"))
                if os.path.abspath(f) != os.path.abspath(OUT)])


def _rel(path: str) -> str:
    try:
        return os.path.relpath(path, ROOT).replace("\\", "/")
    except ValueError:  # path on another drive (e.g. a temp face in a control)
        return path.replace("\\", "/")


# ---------------------------------------------------------------------- doc
def _pct(x, digits=2):
    return "n/a" if x is None else "%.*f%%" % (digits, x * 100)


def _num(x, digits=2):
    return "n/a" if x is None else "%.*f" % (digits, x)


def write_md(payload) -> None:
    s, e = payload["summary"], payload["edges"]
    vc = "lot_%d" % VERDICT_CAPITAL
    key = "worst_%d_periods" % ROLL_WINDOW
    a_f, b_f = s["A"]["bookings"]["fractional"], s["B"]["bookings"]["fractional"]
    a_l, b_l = s["A"]["bookings"][vc], s["B"]["bookings"][vc]
    ef, el = e["by_booking"]["fractional"], e["by_booking"][vc]
    tax = e["edge_tax"]
    be = tax["breakeven"] or {}

    lines = [DOC_BEGIN, "",
             "# A 股残差黑名单：这本书记过十一次均值，没人记过它有多颠",
             "",
             "generated %s | evidence_cutoff **%s** | verdict **%s**"
             % (payload["generated"], payload["evidence_cutoff"], payload["verdict"]),
             "",
             "r1865 之后这条黑名单（全池剔掉残差最高 20%%）被量过 %d 遍：能不能成交、一字板要不要等、"
             "整手取整收多少税、闲钱按哪种日计数计息、装得下多少钱、2026 的亏损是市场还是排序。"
             "**这 %d 张面都在讲「每期多少」，没有一张讲「过程有多颠」。** 一个真准备把钱放进去的人，"
             % (payload["family_faces_before"], payload["family_faces_before"]) +
             "第二句问的就是这个：账面能不能扛住中间那段路。本面把波动、回撤、夏普、水下时间和成本税"
             "一次补齐，并且不新造任何阈值——两个严格比较，四个状态。",
             "",
             "## 一句话",
             "",
             "**按分数记账，黑名单臂（B）每期多挣 %+.4f 个百分点（t %s），夏普 %.2f 对 %.2f，"
             "最大回撤 %.2f%% 对 %.2f%% → `%s`。** 判词只有两格在问：风险调整后是不是更好，最深的那个坑"
             "是不是更深。"
             % (ef["mean_per_period"] * 100, _num(ef["t"]),
                b_f["sharpe_excess_0"] or float("nan"), a_f["sharpe_excess_0"] or float("nan"),
                (b_f["max_drawdown"] or 0) * 100, (a_f["max_drawdown"] or 0) * 100, ef["verdict"]),
             "",
             "## 四条曲线",
             "",
             "记账口径两档：`fractional`=父面口径（权重恰好 1/n、满仓）；`lot`=同一批名字、"
             "1,000 万元、每只只能整手买，买不起的那只空着、现金 0%。",
             "",
             "| 记账 | 臂 | 期数 | 期间均值 | 年化(复利) | 年化波动 | 夏普(超额对 0%) | 最大回撤 | Calmar | 胜率 | 水下时间 | 最差一期 | 最差半年 |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
             ]
    for booking, name in (("fractional", "分数"), (vc, "整手@1千万")):
        for arm in ARMS:
            st = s[arm]["bookings"][booking]
            lines.append("| %s | %s | %d | %+.4f%% | %s | %s | %s | %s | %s | %s | %s | %s | %s |"
                         % (name, arm, st["periods"],
                            (st["per_period_mean"] or 0) * 100,
                            _pct(st["annualized_compound"]),
                            _pct(st["annual_vol"]),
                            _num(st["sharpe_excess_0"]),
                            _pct(st["max_drawdown"]),
                            _num(st["calmar"]),
                            _pct(st["hit_rate"], 1),
                            _pct(st["underwater_share"], 1),
                            _pct(st["worst_period"]),
                            _pct(st[key])))
    lines += ["",
              "## 判词怎么读",
              "",
              "| 状态 | 意思 |",
              "|---|---|",
              "| `SHARPE_UP_DRAWDOWN_SHALLOWER` | 每一块钱的风险买到更多收益，最深的坑也更浅——没有理由不做这条排序 |",
              "| `SHARPE_UP_DRAWDOWN_DEEPER` | 夏普更好但坑更深——这是一条需要事先说好「凭什么扛」的边 |",
              "| `SHARPE_DOWN_DRAWDOWN_SHALLOWER` | 只是少亏点，收益不足以补偿波动——不构成开仓理由 |",
              "| `SHARPE_DOWN_DRAWDOWN_DEEPER` | 两头都更差——平均数的优势是别的账造出来的 |",
              "",
              "两个轴都是**严格比较**，没有「差 0.05 就算更好」这种自选宽容度；打平记 `DOWN` / `SHALLOWER`，"
              "即不改善就不算改善。",
              "",
              "## 这条边的账单",
              "",
              "| 项 | A 全池 | B 黑名单 |",
              "|---|---|---|",
              "| 平均换手（每期） | %s | %s |" % (_pct(s["A"]["turnover_mean"], 2),
                                                _pct(s["B"]["turnover_mean"], 2)),
              "| 毛收益（每期） | %+.4f%% | %+.4f%% |" % (
                  (s["A"]["gross"]["gross_per_period_mean"] or 0) * 100,
                  (s["B"]["gross"]["gross_per_period_mean"] or 0) * 100),
              "| 成本（每期） | %+.4f%% | %+.4f%% |" % (
                  (s["A"]["gross"]["cost_per_period_mean"] or 0) * 100,
                  (s["B"]["gross"]["cost_per_period_mean"] or 0) * 100),
              "| 成本年化 | %s | %s |" % (_pct(s["A"]["gross"]["cost_annualized"], 4),
                                          _pct(s["B"]["gross"]["cost_annualized"], 4)),
              "| 成本占毛收益 | %s | %s |" % (_pct(s["A"]["gross"]["cost_share_of_gross"], 1),
                                             _pct(s["B"]["gross"]["cost_share_of_gross"], 1)),
              "",
              "B 臂换手是 A 的 **%.1f 倍**（残差排名每期翻动），所以这条边在税前是 "
              "**%+.4f%%/期**，税后 **%+.4f%%/期**，**%s 的毛边交给了券商**。"
              % ((s["B"]["turnover_mean"] or 0) / (s["A"]["turnover_mean"] or float("nan")),
                 (tax["gross_edge_per_period"] or 0) * 100,
                 (tax["net_edge_per_period"] or 0) * 100,
                 _pct(tax["tax_share_of_gross_edge"], 1)),
              "",
              ("**成本耐受度**：现在收单边 %.1f bp。要让这条边的净额归零，单边成本得涨到 "
               "**%.1f bp**（%.2f 倍）。这个数不是阈值，是解出来的零点——它回答的是「这笔佣金涨多少我才"
               "白干」，不是「多少 bp 以下算安全」。"
               % (COST_ONE_SIDE * 1e4, be.get("one_side_bp", float("nan")),
                  be.get("k_multiple", float("nan"))))
              if be else "**成本耐受度**：这条边在毛上是负的或换手不高于全池，算不出零点。",
              "",
              "## 整手账里风险有没有变形",
              "",
              "| 记账 | B−A Sharpe | B−A 回撤 | 判词 |",
              "|---|---|---|---|",
              "| 分数 | %s | %s | `%s` |" % (_num(ef["sharpe_b_minus_a"], 3),
                                            _pct(ef["mdd_b_minus_a"]), ef["verdict"]),
              "| 整手@1千万 | %s | %s | `%s` |" % (_num(el["sharpe_b_minus_a"], 3),
                                                _pct(el["mdd_b_minus_a"]), el["verdict"]),
              "",
              ("两档判词一致：整手削掉的是收益水平和在场的钱，没有改变这本书的风险形状。"
               if ef["verdict"] == el["verdict"] else
               "**两档判词不一致**——整手不只是削收益，它改变了这本书的风险形状，"
               "这种情况下 1,000 万那一档的结论不能外推到分数口径。"),
              "",
              "但整手那两行的波动和回撤比分数两行小，**这不是更安全，是更闲**：1,000 万时中位 "
              "**%s** 的钱（A）/ **%s**（B）根本没买成股票，躺在 0%% 现金里。现金不涨不跌，"
              "把整条曲线的振幅一起按比例压扁了。两臂吃的是同一种稀释，所以 B 与 A 的比较仍然成立；"
              "但整手那两行的夏普不能和分数那两行直接比大小。"
              % (_pct(s["A"].get("invested_share_median_lot_%d" % VERDICT_CAPITAL), 1),
                 _pct(s["B"].get("invested_share_median_lot_%d" % VERDICT_CAPITAL), 1)),
              "",
              "## 这张面不是什么",
              "",
              "* **回撤是 20 交易日一期**的净值曲线上的回撤，不是日频 mark-to-market。日频回撤要每日权重，"
              "这个家族从来没有记过，所以本面不印一个更好看但它撑不住的数字。",
              "* 夏普的超额基准取 **0% 现金**。逆回购那条腿（r2013/r2014 定价约 2.1pp/年）两臂共享，"
              "会把两条夏普一起抬高大致相同的量，本面披露而不并入。",
              "* Calmar 用的是同一条期间曲线上的复利年化除以回撤深度，期数少（%d 期）时它对单个极端期很敏感。"
              % payload["rebalances"],
              "* 票池是现存标的（幸存者偏差，父面同），面板起于 2020-01-02；2020 年只有 7 期。",
              "* 这是风险刻画件，不是策略：无仓位规则、无容量约束、无风控，也不构成对未来的承诺。",
              "",
              "## 跨面锚",
              "",
              "本面的 `per_period_mean`（分数口径与 1,000 万整手口径）和 `turnover_mean` 必须"
              "**逐位复现** `results/astock_veto_lot_drag.json`，本次最大绝对差 **%.3e**（ok=%s）。"
              % (payload["anchor"].get("worst_abs_diff") or 0.0, payload["anchor"]["ok"]),
              "",
              "## 复现",
              "",
              "```",
              "python scripts/astock_veto_tearsheet.py selftest",
              "python scripts/astock_veto_tearsheet.py run",
              "python scripts/astock_veto_tearsheet.py check",
              "```",
              "",
              DOC_END]
    os.makedirs(os.path.dirname(MD), exist_ok=True)
    with open(MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")


# ------------------------------------------------------------------------ run
def run(hold: int = HOLD, stride: int = HOLD) -> int:
    dates, symbols, rows = build_face(hold=hold, stride=stride)
    if not rows:
        print("no rebalance rows")
        return 2
    summary = summarize(rows)
    e = edges(rows, summary)
    anchor = parent_anchor(summary)
    verdict = e["by_booking"]["fractional"]["verdict"]
    verdict_lot = e["by_booking"]["lot_%d" % VERDICT_CAPITAL]["verdict"]

    payload = {
        "generated": _now(),
        "evidence_cutoff": dates[-1],
        "machine": _machine(),
        "kind": "astock_veto_tearsheet",
        "family_faces_before": _family_faces_before(),
        "fills_the_hole_of": ("the family published the mean many times and the "
                              "ride zero times (r1865..r2014)"),
        "prereg": {
            "question": "is the veto book better risk-adjusted, or only better on average?",
            "verdict_rule": ("SHARPE_UP/SHARPE_DOWN = strict comparison of Sharpe "
                             "(excess over 0% cash) B vs A; "
                             "DRAWDOWN_DEEPER/SHALLOWER = strict comparison of the "
                             "period-curve maximum drawdown; no thresholds invented"),
            "bookings": list(BOOKINGS),
            "verdict_booking": "fractional (parent's booking); lot booking printed alongside",
            "drawdown_basis": "20-trading-day period curve, not daily marks",
            "roll_window_periods": ROLL_WINDOW,
            "cash_rate_per_period": 0.0,
            "rule_frozen_before_run": True,
        },
        "spec": {
            "hold": hold, "stride": stride, "cost_one_side": COST_ONE_SIDE,
            "lot": LOT, "verdict_capital": VERDICT_CAPITAL,
            "periods_per_year": PPY,
            "booking": "close(t) -> close(t+20) (parent's booking)",
            "arms": {"A": "whole eligible pool", "B": "A minus top 20% residual"},
        },
        "panel": {"dates": len(dates), "symbols": len(symbols),
                  "first": dates[0], "last": dates[-1]},
        "rebalances": len(rows),
        "summary": summary,
        "edges": e,
        "verdict": verdict,
        "verdict_lot_booking": verdict_lot,
        "anchor": anchor,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    write_md(payload)

    print("TEARSHEET %s | B-A net %+.4f%%/期 t=%s | anchor ok=%s"
          % (verdict, e["by_booking"]["fractional"]["mean_per_period"] * 100,
             _fmt_num(e["by_booking"]["fractional"]["t"]), anchor["ok"]))
    for b in BOOKINGS:
        for arm in ARMS:
            s = summary[arm]["bookings"][b]
            print("  %-11s %s  mean %+7.4f%%  vol %6.2f%%  sharpe %6.2f  mdd %7.2f%%  hit %5.1f%%"
                  % (b, arm, (s["per_period_mean"] or 0) * 100,
                     (s["annual_vol"] or 0) * 100, s["sharpe_excess_0"] or float("nan"),
                     (s["max_drawdown"] or 0) * 100, (s["hit_rate"] or 0) * 100))
    tax = e["edge_tax"]
    print("  turnover A %.4f B %.4f | gross edge %+.4f%%  net edge %+.4f%%  tax %+.4f%% (%.1f%% of gross)"
          % (summary["A"]["turnover_mean"], summary["B"]["turnover_mean"],
             (tax["gross_edge_per_period"] or 0) * 100, (tax["net_edge_per_period"] or 0) * 100,
             (tax["tax_per_period"] or 0) * 100, (tax["tax_share_of_gross_edge"] or 0) * 100))
    if tax["breakeven"]:
        print("  breakeven one-side fee %.1f bp (charged %.1f bp) = %.2fx"
              % (tax["breakeven"]["one_side_bp"], COST_ONE_SIDE * 1e4,
                 tax["breakeven"]["k_multiple"]))
    print("  -> %s" % _rel(OUT))
    print("  -> %s" % _rel(MD))
    return 0


def _fmt_num(x):
    return "n/a" if x is None else "%.2f" % x


# ---------------------------------------------------------------------- check
def check() -> int:
    """Re-derive, then compare.  A moved input is STALE; numbers that moved with
    the same inputs are a real defect and must not wear the STALE word."""
    try:
        with open(OUT, "r", encoding="utf-8") as fh:
            face = json.load(fh)
    except (OSError, ValueError):
        print("CHECK FAILED face missing: %s" % _rel(OUT))
        return 3

    problems = []
    dates, _symbols, rows = build_face()
    summary = summarize(rows)
    e = edges(rows, summary)

    if face.get("evidence_cutoff") != dates[-1]:
        problems.append("STALE panel moved: face %s vs panel %s"
                        % (face.get("evidence_cutoff"), dates[-1]))

    def _cmp(label, mine, theirs, tol=1e-12):
        if mine is None or theirs is None:
            if not (mine is None and theirs is None):
                problems.append("CHECK FAILED %s is None on one side" % label)
            return
        if abs(float(mine) - float(theirs)) > tol:
            problems.append("CHECK FAILED %s %r != %r" % (label, float(mine), float(theirs)))

    for arm in ARMS:
        for b in BOOKINGS:
            got = summary[arm]["bookings"][b]
            pub = face["summary"][arm]["bookings"][b]
            for key in ("per_period_mean", "per_period_stdev", "annualized_compound",
                        "annual_vol", "sharpe_excess_0", "max_drawdown", "calmar",
                        "hit_rate", "worst_period", "best_period", "underwater_share",
                        "worst_%d_periods" % ROLL_WINDOW):
                _cmp("%s/%s/%s" % (arm, b, key), got.get(key), pub.get(key))
            _cmp("%s/%s/periods" % (arm, b), got["periods"], pub.get("periods"))
        _cmp("%s/turnover_mean" % arm, summary[arm]["turnover_mean"],
             face["summary"][arm]["turnover_mean"])
        for key in ("gross_per_period_mean", "cost_per_period_mean",
                    "cost_annualized", "cost_share_of_gross"):
            _cmp("%s/gross/%s" % (arm, key), summary[arm]["gross"][key],
                 face["summary"][arm]["gross"][key])
        _cmp("%s/invested_share_median_lot" % arm,
             summary[arm]["invested_share_median_lot_%d" % VERDICT_CAPITAL],
             face["summary"][arm].get("invested_share_median_lot_%d" % VERDICT_CAPITAL))

    for b in BOOKINGS:
        for key in ("mean_per_period", "t", "sharpe_of_the_difference",
                    "sharpe_b_minus_a", "mdd_b_minus_a"):
            _cmp("edge/%s/%s" % (b, key), e["by_booking"][b][key],
                 face["edges"]["by_booking"][b][key])
        if e["by_booking"][b]["verdict"] != face["edges"]["by_booking"][b]["verdict"]:
            problems.append("CHECK FAILED edge/%s/verdict %r != %r"
                            % (b, e["by_booking"][b]["verdict"],
                               face["edges"]["by_booking"][b]["verdict"]))
    for key in ("gross_edge_per_period", "net_edge_per_period", "tax_per_period",
                "tax_share_of_gross_edge"):
        _cmp("edge_tax/%s" % key, e["edge_tax"][key], face["edges"]["edge_tax"][key])
    if (e["edge_tax"]["breakeven"] or {}).get("one_side_bp") != \
            (face["edges"]["edge_tax"]["breakeven"] or {}).get("one_side_bp"):
        problems.append("CHECK FAILED breakeven one_side_bp moved")
    if e["by_booking"]["fractional"]["verdict"] != face.get("verdict"):
        problems.append("CHECK FAILED headline verdict %r != %r"
                        % (e["by_booking"]["fractional"]["verdict"], face.get("verdict")))

    # internal sanity: a drawdown is never positive, a hit rate is a share
    for arm in ARMS:
        for b in BOOKINGS:
            s = summary[arm]["bookings"][b]
            if s["max_drawdown"] is not None and s["max_drawdown"] > 0:
                problems.append("CHECK FAILED %s/%s drawdown positive %r"
                                % (arm, b, s["max_drawdown"]))
            if s["hit_rate"] is not None and not (0.0 <= s["hit_rate"] <= 1.0):
                problems.append("CHECK FAILED %s/%s hit rate out of range %r"
                                % (arm, b, s["hit_rate"]))

    anchor = parent_anchor(summary)
    if not anchor["ok"]:
        problems.append("STALE parent anchor: %r" % (anchor,))

    if not problems:
        print("CHECK ok  (verdict %s, B-A %+.4f%%/t=%s, anchor ok=%s)"
              % (e["by_booking"]["fractional"]["verdict"],
                 e["by_booking"]["fractional"]["mean_per_period"] * 100,
                 _fmt_num(e["by_booking"]["fractional"]["t"]), anchor["ok"]))
        return 0
    for p in problems:
        print(p)
    return 3


# ------------------------------------------------------------------- selftest
_CHECKS = [0]


def _ok(cond, msg):
    _CHECKS[0] += 1
    if not cond:
        raise AssertionError("selftest leg %d failed: %s" % (_CHECKS[0], msg))


def selftest() -> int:
    # 1. equity curve compounds, does not sum
    w = equity_curve([0.10, 0.10])
    _ok(abs(w[-1] - 1.21) < 1e-12, "two +10% periods compound to 1.21")
    # 2. a price we could not observe is dropped, not read as a flat period
    w2 = equity_curve([0.10, float("nan"), 0.10])
    _ok(abs(w2[-1] - 1.21) < 1e-12, "nan period is dropped, not zero")
    # 3. monotone-up curve has zero drawdown, never None and never positive
    _ok(max_drawdown([0.01, 0.02, 0.03]) == 0.0, "monotone up -> drawdown 0.0")
    # 4. drawdown is peak-to-trough of the curve, not the worst single period
    mdd = max_drawdown([0.10, -0.20, 0.05])
    _ok(abs(mdd - (-0.20)) < 1e-12, "0.10 then -0.20 -> -20% from the peak")
    # 5. a two-step slide compounds: -19% from the peak, not -10%
    mdd2 = max_drawdown([-0.10, -0.10])
    _ok(abs(mdd2 + 0.19) < 1e-12, "two -10% steps -> -19% from the peak")
    # 6. no observations -> no drawdown, not 0
    _ok(max_drawdown([]) is None, "empty series -> None")
    # 7. volatility needs two points and is sample sd
    _ok(period_vol([0.01]) is None, "one point -> no vol")
    _ok(abs(period_vol([0.01, 0.03]) - np.std([0.01, 0.03], ddof=1)) < 1e-15,
        "vol is the sample stdev")
    # 8. annualising volatility multiplies by sqrt(periods per year)
    _ok(abs(annual_vol([0.01, 0.03]) / period_vol([0.01, 0.03]) - np.sqrt(PPY)) < 1e-12,
        "annual vol = period vol * sqrt(PPY)")
    # 9. Sharpe: mean/sd * sqrt(PPY) on a known series
    r = np.array([0.01, -0.01, 0.02, 0.00])
    _ok(abs(sharpe(r) - (np.mean(r) / np.std(r, ddof=1) * np.sqrt(PPY))) < 1e-12,
        "sharpe formula")
    # 10. Sharpe over a per-period cash rate lowers the ratio but not the sign
    _ok(sharpe(r, rf_per_period=0.001) < sharpe(r), "positive rf lowers sharpe")
    # 11. a flat series has no Sharpe (not 0, not inf)
    _ok(sharpe([0.01, 0.01, 0.01]) is None, "zero variance -> None")
    # 12. hit rate is a share of strictly positive periods
    _ok(abs(hit_rate([0.01, 0.0, -0.01, 0.02]) - 0.5) < 1e-12, "hit rate counts > 0 only")
    # 13. worst window compounds; a series shorter than the window has none
    _ok(abs(worst_window([0.10, -0.10], k=2) + 0.01) < 1e-12, "chained window, not summed")
    _ok(worst_window([0.10, -0.10], k=3) is None, "window longer than series -> None")
    # 14. Calmar is CAGR over the drawdown depth, and refuses a zero drawdown
    _ok(calmar([0.01, 0.02]) is None, "no drawdown -> no calmar")
    c = calmar([0.10, -0.20, 0.05])
    _ok(c is not None and c < 0, "a losing series has a negative calmar")
    # 15. underwater share: a series that never recovers stays underwater
    _ok(abs(underwater_share([0.10, -0.20]) - 0.5) < 1e-12, "one of two periods underwater")
    # 16. verdict 2x2 uses strict comparisons on both axes
    _ok(risk_verdict(1.2, 1.0, -0.10, -0.12) == "SHARPE_UP_DRAWDOWN_SHALLOWER",
        "better sharpe, shallower hole")
    _ok(risk_verdict(1.2, 1.0, -0.15, -0.12) == "SHARPE_UP_DRAWDOWN_DEEPER",
        "better sharpe, deeper hole")
    _ok(risk_verdict(0.8, 1.0, -0.10, -0.12) == "SHARPE_DOWN_DRAWDOWN_SHALLOWER",
        "worse sharpe, shallower hole")
    _ok(risk_verdict(0.8, 1.0, -0.15, -0.12) == "SHARPE_DOWN_DRAWDOWN_DEEPER",
        "worse sharpe, deeper hole")
    # 17. equal Sharpe or equal drawdown is not "up"/"deeper" -- it is down/shallower
    _ok(risk_verdict(1.0, 1.0, -0.12, -0.12) == "SHARPE_DOWN_DRAWDOWN_SHALLOWER",
        "ties resolve to not-up and not-deeper")
    # 18. verdict refuses NaN instead of guessing
    _ok(risk_verdict(float("nan"), 1.0, -0.1, -0.1) == "INSUFFICIENT_DATA",
        "nan -> insufficient data")
    _ok(risk_verdict(None, 1.0, -0.1, -0.1) == "INSUFFICIENT_DATA", "None -> insufficient data")
    # 19. cost block: the bill is gross minus net, and its share is of gross
    cb = cost_block([0.01, 0.02], [0.009, 0.019])
    _ok(abs(cb["cost_per_period_mean"] - 0.001) < 1e-15, "cost = gross - net")
    _ok(abs(cb["cost_annualized"] - 0.001 * PPY) < 1e-15, "cost annualised at PPY")
    _ok(abs(cb["cost_share_of_gross"] - 0.001 / 0.015) < 1e-12, "cost share of gross")
    # 20. a negative gross has no meaningful share (not a negative percentage)
    _ok(cost_block([-0.01], [-0.011])["cost_share_of_gross"] is None,
        "negative gross -> no share")
    # 21. breakeven: at k* the net edge is exactly zero
    be = breakeven_one_side(0.0030, 0.0020, 0.24, 0.05, 0.0008)
    k = be["k_multiple"]
    _ok(abs((0.0030 - k * 2 * 0.0008 * (0.24 - 0.05))) < 1e-15,
        "net edge is exactly zero at k*")
    _ok(abs(be["one_side_bp"] - k * 8.0) < 1e-12, "one-side bp = k * charged bp")
    # 22. breakeven refuses the cases that have no answer
    _ok(breakeven_one_side(0.003, -0.001, 0.24, 0.05, 0.0008) is not None,
        "a still-positive gross edge has an answer even if net is gone")
    _ok(breakeven_one_side(-0.003, -0.002, 0.24, 0.05, 0.0008) is None,
        "no gross edge -> no breakeven")
    _ok(breakeven_one_side(0.003, 0.002, 0.05, 0.24, 0.0008) is None,
        "veto arm paying less turnover -> no such breakeven")
    _ok(breakeven_one_side(0.003, 0.002, 0.24, 0.24, 0.0008) is None,
        "equal turnover -> no breakeven")
    # 23. series_stats carries the same numbers as the individual helpers
    s = series_stats([0.10, -0.20, 0.05])
    _ok(s["periods"] == 3 and abs(s["max_drawdown"] - max_drawdown([0.10, -0.20, 0.05])) < 1e-15,
        "series_stats wraps the helpers")
    _ok(s["annualized_compound"] is not None, "compound annualised is printed")
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
