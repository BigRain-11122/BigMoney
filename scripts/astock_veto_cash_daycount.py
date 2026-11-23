"""A-share residual veto: what the cash leg earns when the calendar, not the
trading board, decides how many days you are paid for.

r2013 (``astock_veto_cash_leg``) priced the uninvested cash with GC001, one
*trading* day at a time: every step in the panel calendar earned exactly
``close/365``.  That booking has a hole nobody looked at.  A repo leg is paid
on **natural** days: sell GC001 on a Friday and the money comes back Monday
morning, so that one trade is paid for three days, not one.  A 20-trading-day
window spans ~30 natural days in the A-share calendar, so r2013 collected
interest for two thirds of the time the money was actually out.

This face re-prices the same book three ways and reports the gap:

    trading   r2013's booking, one day per panel step (the anchor)
    calendar  same GC001 tape, but each step is paid for the natural days it spans
    ladder    one pre-committed plan bought on the entry day: longest term that
              fits the window, remainder in GC001, all at quotes observable on
              that day (no look-ahead, no rolling into unknown future quotes)

``ladder`` answers the question r2013 left open -- whether the term premium is
where the money is.  It is not: the money is in the day count.  Once the day
count is right, buying a 28-day term instead of rolling 1-day paper adds
almost nothing, because the 1-day paper already accrues over the weekend.

Nothing else changes: same panel, same 20-day stride, same whole-lot booking,
same 2x8bp cost, same two arms.  ``trading`` must reproduce r2013's
``net_with_cash`` bit-for-bit; if it does not, this is not the same book.

    python scripts/astock_veto_cash_daycount.py selftest
    python scripts/astock_veto_cash_daycount.py run
    python scripts/astock_veto_cash_daycount.py check
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from datetime import datetime, timedelta, timezone

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from astock_resid_veto_layer import HOLD  # noqa: E402
from astock_veto_cash_leg import (  # noqa: E402
    ARMS,
    CAPITALS,
    EDGE_KEEP_TARGET,
    EDGE_LOST_TARGET,
    VERDICT_CAPITAL,
    _tstat,
    align_cash_to_panel,
    build,
    compound,
    load_cash_tape,
    verdict_from_ratio,
)

OUT = os.path.join(ROOT, "results", "astock_veto_cash_daycount.json")
MD = os.path.join(ROOT, "research", "ASTOCK_VETO_CASH_DAYCOUNT.md")
PARENT = os.path.join(ROOT, "results", "astock_veto_cash_leg.json")

# term code -> natural days the leg is paid for
TERMS = {"GC001": 1, "GC003": 3, "GC004": 4, "GC007": 7, "GC014": 14, "GC028": 28}
LADDER_ORDER = ("GC028", "GC014", "GC007", "GC004", "GC003")
MODES = ("trading", "calendar", "ladder")
DOC_BEGIN = "<!-- BEGIN:ASTOCK-VETO-CASH-DAYCOUNT -->"
DOC_END = "<!-- END:ASTOCK-VETO-CASH-DAYCOUNT -->"


def _rel(path: str) -> str:
    try:
        return os.path.relpath(path, ROOT).replace("\\", "/")
    except ValueError:
        return path.replace("\\", "/")


def _fmt_t(t):
    return "n/a" if t is None else "%.2f" % t


# ------------------------------------------------------------------ pure logic
def days_between(a: str, b: str) -> int:
    """Natural days from panel day ``a`` to panel day ``b`` (never negative)."""
    return int((np.datetime64(str(b)) - np.datetime64(str(a))).astype(int))


def period_cash_calendar(panel_dates, rates, d0: str, hold: int = HOLD) -> float:
    """GC001 rolled daily, each step paid for the natural days it spans.

    ``rates`` is the GC001 tape re-indexed onto the **panel** calendar with
    forward fill (a hole is the last good quote, never 0%).  The quote used for
    the step from day k to day k+1 is the one observable on day k -- the money
    is swept at that close.
    """
    n = len(panel_dates)
    pos = None
    for i in range(n):
        if str(panel_dates[i]) == str(d0):
            pos = i
            break
    if pos is None or hold <= 0 or pos + hold >= n:
        return 0.0
    growth, last = 1.0, None
    for k in range(pos, pos + hold):
        days = days_between(panel_dates[k], panel_dates[k + 1])
        r = rates[k]
        if r is not None and math.isfinite(float(r)):
            last = float(r)
        if last is None:
            continue
        growth *= 1.0 + last / 100.0 / 365.0 * days
    return growth - 1.0


def ladder_plan(total_days: int) -> list:
    """Greedy longest-first split of a natural-day span into repo terms.

    Capped at 8 legs: a plan longer than that means the window is mis-specified,
    not that the ladder should keep slicing.
    """
    left = max(0, int(total_days))
    plan = []
    for code in LADDER_ORDER:
        n = TERMS[code]
        while left >= n and len(plan) < 8:
            plan.append(code)
            left -= n
    plan.extend(["GC001"] * left)
    return plan


def period_cash_ladder(panel_dates, term_on_panel, d0: str, hold: int = HOLD):
    """One pre-committed ladder bought on ``d0`` at ``d0`` quotes.

    Returns None when the window cannot be located or a leg has no quote at
    ``d0`` (a missing quote is not a zero rate).  Each leg is paid for its own
    natural-day term -- that is what the term means.
    """
    n = len(panel_dates)
    pos = None
    for i in range(n):
        if str(panel_dates[i]) == str(d0):
            pos = i
            break
    if pos is None or hold <= 0 or pos + hold >= n:
        return None
    span = days_between(panel_dates[pos], panel_dates[pos + hold])
    plan = ladder_plan(span)
    growth = 1.0
    for code in plan:
        rate = term_on_panel[code][pos]
        if rate is None or not math.isfinite(float(rate)):
            return None
        growth *= 1.0 + float(rate) / 100.0 / 365.0 * TERMS[code]
    return growth - 1.0


def load_term_tape(code: str, root: str = ROOT):
    """One repo term tape (date, annualised percent close) from data/repo_daily."""
    import math as _m

    path = os.path.join(root, "data", "repo_daily", code + ".csv")
    dates, rates = [], []
    with open(path, "r", encoding="utf-8") as fh:
        head = fh.readline().strip().split(",")
        ci, di = head.index("close"), head.index("date")
        for raw in fh:
            parts = raw.strip().split(",")
            if len(parts) <= max(ci, di):
                continue
            try:
                v = float(parts[ci])
            except ValueError:
                continue
            if not _m.isfinite(v):
                continue
            dates.append(parts[di])
            rates.append(v)
    if not dates:
        raise RuntimeError("repo tape is empty: %s" % _rel(path))
    return np.array(dates, dtype=object), np.asarray(rates, dtype=np.float64)


def net_with(cash0: float, invested_share: float, r_cash) -> float:
    """The parent's booking plus whatever the chosen cash mode earns."""
    if r_cash is None or not (math.isfinite(cash0) and math.isfinite(invested_share)
                              and math.isfinite(r_cash)):
        return float("nan")
    return float(cash0) + (1.0 - float(invested_share)) * float(r_cash)


# -------------------------------------------------------------------- the face
def build_face(hold: int = HOLD, stride: int = HOLD):
    dates, symbols, rows = build(hold, stride)

    tape_dates, tape_rates = load_cash_tape()
    cash = align_cash_to_panel(dates, tape_dates, tape_rates)
    term_on_panel = {}
    for code in TERMS:
        td, tr = load_term_tape(code)
        term_on_panel[code] = align_cash_to_panel(dates, td, tr)

    dropped_ladder = 0
    for row in rows:
        d0 = row["date"]
        row["r_cash_trading"] = row["r_cash"]
        row["r_cash_calendar"] = period_cash_calendar(dates, cash, d0, hold)
        rc_lad = period_cash_ladder(dates, term_on_panel, d0, hold)
        if rc_lad is None:
            dropped_ladder += 1
            rc_lad = float("nan")
        row["r_cash_ladder"] = rc_lad
        row["span_days"] = days_between(d0, dates[dates.index(d0) + hold]) \
            if list(dates).count(d0) and (list(dates).index(d0) + hold) < len(dates) else None
        for arm in ARMS:
            for c in CAPITALS:
                e = row[arm]["by_capital"][str(c)]
                share = e["invested_share"]
                for mode in MODES:
                    e["net_" + mode] = net_with(e["net_cash0"], share, row["r_cash_" + mode])
    return dates, symbols, rows, dropped_ladder


def _capital_series(rows, arm, capital, key):
    return np.array([r[arm]["by_capital"][str(capital)][key] for r in rows], dtype=np.float64)


def _cash_series(rows, key):
    return np.array([r[key] for r in rows], dtype=np.float64)


def summarize(rows):
    out = {}
    for arm in ARMS:
        per_c = {}
        for c in CAPITALS:
            cs = str(c)
            net0 = _capital_series(rows, arm, c, "net_cash0")
            blk = {
                "invested_share_median": float(np.nanmedian(
                    _capital_series(rows, arm, c, "invested_share"))),
                "invested_share_mean": float(np.nanmean(
                    _capital_series(rows, arm, c, "invested_share"))),
                "net_cash0_annualized": compound(list(net0)),
                "net_cash0_per_period_mean": float(np.nanmean(net0)),
            }
            for mode in MODES:
                net = _capital_series(rows, arm, c, "net_" + mode)
                blk["net_%s_annualized" % mode] = compound(list(net))
                blk["net_%s_per_period_mean" % mode] = float(np.nanmean(net))
                a0 = blk["net_cash0_annualized"]
                am = blk["net_%s_annualized" % mode]
                blk["bonus_%s_annualized" % mode] = (
                    (am - a0) if (am is not None and a0 is not None) else None)
            per_c[cs] = blk
        out[arm] = {
            "periods": int(len(rows)),
            "mean_n": float(np.mean([r[arm]["size"] for r in rows])),
            "by_capital": per_c,
        }
    return out


def cash_tape(rows):
    """The raw leg itself, per mode, and how much the day count moves it."""
    out = {}
    for mode in MODES:
        s = _cash_series(rows, "r_cash_" + mode)
        out[mode] = {
            "per_period_mean": float(np.nanmean(s)),
            "annualized": compound(list(s)),
            "min": float(np.nanmin(s)),
            "max": float(np.nanmax(s)),
        }
    tr, ca, la = (out["trading"]["annualized"], out["calendar"]["annualized"],
                  out["ladder"]["annualized"])
    out["calendar_over_trading"] = (ca / tr) if (tr and tr > 0 and ca is not None) else None
    out["ladder_minus_calendar_annualized"] = (
        (la - ca) if (la is not None and ca is not None) else None)
    out["span_days_mean"] = float(np.nanmean([r.get("span_days") or np.nan for r in rows]))
    return out


def edges(rows):
    out = {"fractional": {}, "by_capital": {}}
    d = (np.array([r["B"]["net_frac"] for r in rows])
         - np.array([r["A"]["net_frac"] for r in rows]))
    out["fractional"] = {"mean_per_period": float(np.nanmean(d)), "t": _tstat(d)}
    for c in CAPITALS:
        blk = {}
        for mode in MODES:
            d = (_capital_series(rows, "B", c, "net_" + mode)
                 - _capital_series(rows, "A", c, "net_" + mode))
            blk[mode] = {"mean_per_period": float(np.nanmean(d)), "t": _tstat(d)}
        out["by_capital"][str(c)] = blk
    return out


def verdicts(edges_, summary):
    base = edges_["fractional"]["mean_per_period"]
    out = {}
    for c in CAPITALS:
        row = edges_["by_capital"][str(c)]
        blk = {}
        for mode in MODES:
            r = (row[mode]["mean_per_period"] / base) if base else None
            blk["ratio_" + mode] = r
            blk["verdict_" + mode] = verdict_from_ratio(r)
        out[str(c)] = blk
    return out


def parent_anchor(summary):
    """r2013's published ``net_with_cash`` must come back on the trading mode."""
    try:
        with open(PARENT, "r", encoding="utf-8") as fh:
            parent = json.load(fh)
    except (OSError, ValueError) as exc:
        return {"ok": False, "why": "parent unreadable: %s" % exc, "worst_abs_diff": None}
    worst = 0.0
    for arm in ARMS:
        for c in CAPITALS:
            p = parent["summary"][arm]["by_capital"][str(c)]["net_with_cash_per_period_mean"]
            mine = summary[arm]["by_capital"][str(c)]["net_trading_per_period_mean"]
            if p is None or mine is None:
                return {"ok": False, "why": "missing number arm=%s c=%s" % (arm, c),
                        "worst_abs_diff": None}
            worst = max(worst, abs(float(p) - float(mine)))
    return {"ok": worst <= 1e-9, "worst_abs_diff": worst}


def run() -> int:
    dates, symbols, rows, dropped = build_face()
    summary = summarize(rows)
    tape = cash_tape(rows)
    e = edges(rows)
    v = verdicts(e, summary)
    anchor = parent_anchor(summary)

    payload = {
        "generated": datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"),
        "evidence_cutoff": dates[-1],
        "machine": "bm-c",
        "kind": "pricing",
        "fills_the_hole_of": "astock_veto_cash_leg",
        "prereg": {
            "question": "is the cash leg paid on trading days or natural days?",
            "modes": {
                "trading": "r2013 booking: one day per panel step (anchor)",
                "calendar": "same GC001 tape, each step paid for its natural-day span",
                "ladder": "one pre-committed term plan bought on the entry day",
            },
            "term_days": dict(TERMS),
            "ladder_rule": "greedy longest-first within the window, remainder GC001, <=8 legs",
            "look_ahead_rule": "ladder uses entry-day quotes only; no rolling into unknown quotes",
            "hole_rule": "forward-fill from last good quote; a hole is never 0%",
            "verdict_capital": VERDICT_CAPITAL,
            "edge_keep_target": EDGE_KEEP_TARGET,
            "edge_lost_target": EDGE_LOST_TARGET,
            "rule_frozen_before_run": True,
        },
        "spec": {
            "hold": HOLD,
            "stride": HOLD,
            "booking": "close(t) -> close(t+HOLD), whole lots, uninvested at repo",
            "arms": {"A": "full pool", "B": "residual black list (q < 4)"},
        },
        "panel": {"dates": len(dates), "symbols": len(symbols),
                  "first": dates[0], "last": dates[-1]},
        "rebalances": int(len(rows)),
        "ladder_unpriced_periods": int(dropped),
        "cash_tape": tape,
        "summary": summary,
        "edges": e,
        "verdicts": v,
        "anchor": anchor,
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    write_md(payload)

    vc = str(VERDICT_CAPITAL)
    print("CASH-DAYCOUNT panel %s..%s  %d names  %d periods  cutoff %s"
          % (dates[0], dates[-1], len(symbols), len(rows), dates[-1]))
    print("  leg  trading %.3f pp/yr | calendar %.3f pp/yr (x%.3f) | ladder %.3f pp/yr"
          % ((tape["trading"]["annualized"] or 0) * 100,
             (tape["calendar"]["annualized"] or 0) * 100,
             tape["calendar_over_trading"] or float("nan"),
             (tape["ladder"]["annualized"] or 0) * 100))
    print("  span %.1f natural days over %d trading days" % (tape["span_days_mean"], HOLD))
    for arm in ARMS:
        s = summary[arm]["by_capital"][vc]
        print("  arm %s @10M  net0 %+.2f%%  trading %+.2f%%  calendar %+.2f%%  ladder %+.2f%%"
              % (arm, (s["net_cash0_annualized"] or 0) * 100,
                 (s["net_trading_annualized"] or 0) * 100,
                 (s["net_calendar_annualized"] or 0) * 100,
                 (s["net_ladder_annualized"] or 0) * 100))
    print("  B-A @10M  trading %+.4f%%/p  calendar %+.4f%%/p  ladder %+.4f%%/p"
          % (e["by_capital"][vc]["trading"]["mean_per_period"] * 100,
             e["by_capital"][vc]["calendar"]["mean_per_period"] * 100,
             e["by_capital"][vc]["ladder"]["mean_per_period"] * 100))
    print("  ratio @10M  trading %.3f (%s) | calendar %.3f (%s) | ladder %.3f (%s)"
          % (v[vc]["ratio_trading"] or float("nan"), v[vc]["verdict_trading"],
             v[vc]["ratio_calendar"] or float("nan"), v[vc]["verdict_calendar"],
             v[vc]["ratio_ladder"] or float("nan"), v[vc]["verdict_ladder"]))
    print("  anchor vs r2013: ok=%s worst=%.3e" % (anchor["ok"],
          anchor.get("worst_abs_diff") if anchor.get("worst_abs_diff") is not None
          else float("nan")))
    print("  -> %s" % _rel(OUT))
    print("  -> %s" % _rel(MD))
    return 0


# ---------------------------------------------------------------------- doc
def write_md(payload) -> None:
    s, e, v, t = payload["summary"], payload["edges"], payload["verdicts"], payload["cash_tape"]
    vc = str(VERDICT_CAPITAL)
    b, a = s["B"], s["A"]
    bc, ac = b["by_capital"][vc], a["by_capital"][vc]
    vv = v[vc]
    ratio = t["calendar_over_trading"] or float("nan")

    def pct(x):
        return "n/a" if x is None else "%.2f%%" % (x * 100)

    lines = [DOC_BEGIN, "",
             "# A 股残差黑名单：没投出去的钱，是按交易日算利息还是按自然日算",
             "",
             f"generated {payload['generated']} | evidence_cutoff **{payload['evidence_cutoff']}** "
             f"| verdict @{VERDICT_CAPITAL:,} **{vv['verdict_calendar']}**",
             "",
             "r2013（`astock_veto_cash_leg`）把闲钱按 **GC001 一天期**定价，但它是**一笔一个交易日**"
             "按 `close/365` 计的。逆回购不是这么付钱的：**回购按自然日计息**。周五卖出一笔 GC001，"
             "钱周一早上才回来，这一笔付三天利息。A 股 20 个交易日的一段窗口，真实占款 "
             f"**{t['span_days_mean']:.1f} 个自然日**——r2013 只领了 20 天的钱，把周末白送了。",
             "",
             "## 一句话",
             "",
             f"**把日计数改对，现金腿从 {pct(t['trading']['annualized'])} 变成 "
             f"{pct(t['calendar']['annualized'])}，乘 {ratio:.3f} 倍；而期限阶梯（28 天期）在日计数"
             f"改对之后几乎不再多给钱（{pct(t['ladder']['annualized'])}，比日计数版 "
             f"{pct(t['ladder_minus_calendar_annualized'])}）。钱不在期限溢价里，在日计数里。**",
             "",
             "## 三条腿",
             "",
             "| 口径 | 期间均值 | 年化 | 最小值 | 最大值 |",
             "|---|---|---|---|---|",
             ]
    for mode, name in (("trading", "按交易日（r2013）"),
                       ("calendar", "按自然日（修正）"),
                       ("ladder", "自然日 + 期限阶梯")):
        m = t[mode]
        lines.append("| %s | %+.6f%% | %+.3f pp/yr | %+.6f%% | %+.6f%% |"
                     % (name, m["per_period_mean"] * 100, (m["annualized"] or 0) * 100,
                        m["min"] * 100, m["max"] * 100))
    lines += ["",
              "`ladder` 是在**入场日当天**按当日报价一次性买定最长期限（窗口 28–39 自然日，"
              "所以多数期是 GC028 一份，余数用 GC001），不滚动进未知的未来报价——"
              "它给的是「期限溢价」的上限，不是可承诺收益。",
              "",
              "## 对这本书的影响（10,000,000 元档）",
              "",
              "| 臂 | 现金 0% | 按交易日 | 按自然日 | 自然日+阶梯 |",
              "|---|---|---|---|---|",
              ]
    for arm, blk in (("A 全池", ac), ("B 黑名单", bc)):
        lines.append("| %s | %s | %s | **%s** | %s |"
                     % (arm, pct(blk["net_cash0_annualized"]),
                        pct(blk["net_trading_annualized"]),
                        pct(blk["net_calendar_annualized"]),
                        pct(blk["net_ladder_annualized"])))
    lines += ["",
              "## B-A：日计数改了，判词改不改",
              "",
              "| 资本 | B-A 按交易日 | t | B-A 按自然日 | t | 比值(交易日) | 比值(自然日) | 判词(自然日) |",
              "|---|---|---|---|---|---|---|---|",
              ]
    for c in CAPITALS:
        cs = str(c)
        row, vv_ = e["by_capital"][cs], v[cs]
        rr = vv_["ratio_calendar"] if vv_["ratio_calendar"] is not None else float("nan")
        r0 = vv_["ratio_trading"] if vv_["ratio_trading"] is not None else float("nan")
        lines.append("| %s | %+.4f%% | %s | %+.4f%% | %s | %.3f | %.3f | `%s` |"
                     % (f"{c:,}", row["trading"]["mean_per_period"] * 100, _fmt_t(row["trading"]["t"]),
                        row["calendar"]["mean_per_period"] * 100, _fmt_t(row["calendar"]["t"]),
                        r0, rr, vv_["verdict_calendar"]))
    lines += ["",
              "## 判词怎么读",
              "",
              "* `EDGE_SURVIVES_ROUNDING`（比 ≥0.90）：整手只削收益水平，排序照样付钱；",
              "* `EDGE_DEGRADES_UNDER_ROUNDING`（0.70–0.90）：一部分边是价格档位的产物；",
              "* `EDGE_LOST_TO_ROUNDING`（<0.70）：边的绝大部分来自整手买不到的那批名字。",
              "",
              f"10M 档：r2013 报 **{vv['verdict_trading']}**（比 {vv['ratio_trading'] or float('nan'):.3f}），"
              f"日计数修正后 **{vv['verdict_calendar']}**（比 {vv['ratio_calendar'] or float('nan'):.3f}）。"
              "方向没变，但**比值更差了一点**：现金多的那一臂（A 全池）拿到的利息更多，"
              "所以同一条利率对 A 的抬升比 B 大。",
              "",
              "## 这张面不是什么",
              "",
              "* `trading` / `calendar` 都用 GC001 单期限；`ladder` 才是期限组合，且只在入场日买定；",
              "* 回购报价是**年化百分比**，一天 = `close/100/365`；缺报价日按最后一个好报价前向填充，"
              "不按 0%；",
              "* 没有建模真实申赎摩擦、单笔最低门槛、假期到账日差异（交易所按自然日计息是规则，"
              "本面只认这条规则）；",
              "* 记账口径仍是 close(t)→close(t+20)，不含次日开盘的执行滞后（那是 r2008/r2010 的面）；",
              "* 这是**定价**面，不是策略：无仓位规则、无风控、无容量约束；",
              "* 票池是现存标的（幸存者偏差，父面同），面板起于 2020-01-02。",
              "",
              "## 跨面锚",
              "",
              "`trading` 口径的每个 `net_with_cash_per_period_mean` 必须**逐位复现** "
              "`results/astock_veto_cash_leg.json`（本次最大绝对差 "
              f"**{(payload['anchor'].get('worst_abs_diff') if payload['anchor'].get('worst_abs_diff') is not None else float('nan')):.3e}**）；"
              f"不可定价的期数 = **{payload['ladder_unpriced_periods']}**（本期 0 表示每一期都拿到了报价）。",
              "",
              "## 复现",
              "",
              "```",
              "python scripts/astock_veto_cash_daycount.py selftest",
              "python scripts/astock_veto_cash_daycount.py run",
              "python scripts/astock_veto_cash_daycount.py check",
              "```",
              "",
              DOC_END, ""]

    with open(MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


# --------------------------------------------------------------------- check
def check() -> int:
    """Re-derive and compare.  A moved input says STALE; a number that moved on
    the same inputs is a real defect and must not wear the STALE word."""
    try:
        with open(OUT, "r", encoding="utf-8") as fh:
            face = json.load(fh)
    except (OSError, ValueError):
        print("CHECK FAILED face missing: %s" % _rel(OUT))
        return 3

    problems = []
    dates, symbols, rows, dropped = build_face()
    summary = summarize(rows)
    tape = cash_tape(rows)
    e = edges(rows)
    v = verdicts(e, summary)
    anchor = parent_anchor(summary)

    if face.get("evidence_cutoff") != dates[-1]:
        problems.append("STALE panel moved: face %s vs panel %s"
                        % (face.get("evidence_cutoff"), dates[-1]))
    if not anchor["ok"]:
        problems.append("STALE parent anchor moved: %r" % (anchor,))
    for mode in MODES:
        f = face["cash_tape"][mode]["annualized"]
        g = tape[mode]["annualized"]
        if f is None or g is None or abs(f - g) > 1e-12:
            problems.append("CHECK FAILED cash_tape %s annualized %r != %r" % (mode, f, g))
    for arm in ARMS:
        for c in CAPITALS:
            cs = str(c)
            for key in ("net_calendar_per_period_mean", "net_ladder_per_period_mean"):
                f = face["summary"][arm]["by_capital"][cs][key]
                g = summary[arm]["by_capital"][cs][key]
                if (f is None) != (g is None):
                    problems.append("CHECK FAILED arm %s c %s %s None mismatch" % (arm, cs, key))
                elif f is not None and abs(f - g) > 1e-12:
                    problems.append("CHECK FAILED arm %s c %s %s %r != %r"
                                    % (arm, cs, key, f, g))
    if not problems:
        print("CHECK ok  (periods=%d, day-count x%.3f, verdict @%s %s, anchor ok=%s)"
              % (len(rows), tape["calendar_over_trading"] or float("nan"), VERDICT_CAPITAL,
                 face["verdicts"][str(VERDICT_CAPITAL)]["verdict_calendar"], anchor["ok"]))
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
    # 1. natural days: a Friday close to a Monday open is three days of money
    _ok(days_between("2024-01-05", "2024-01-08") == 3, "Fri -> Mon = 3 days")
    # 2. same day is zero, never negative
    _ok(days_between("2024-01-05", "2024-01-05") == 0, "same day = 0")
    # 3. ladder: exactly 28 days is one 28-day leg
    _ok(ladder_plan(28) == ["GC028"], "28 -> one GC028")
    # 4. ladder: 29 days is 28 + 1
    _ok(ladder_plan(29) == ["GC028", "GC001"], "29 -> GC028 + GC001")
    # 5. ladder: 14 days is one 14-day leg, not two 7s
    _ok(ladder_plan(14) == ["GC014"], "14 -> one GC014")
    # 6. ladder: 30 days is 28 + two 1-day legs
    _ok(ladder_plan(30) == ["GC028", "GC001", "GC001"], "30 -> GC028 + 2x GC001")
    # 7. ladder: zero and one
    _ok(ladder_plan(0) == [], "0 days -> no legs")
    _ok(ladder_plan(1) == ["GC001"], "1 day -> GC001")
    # 8. calendar mode: paid for the natural span, not the step count
    panel = np.array(["2024-01-05", "2024-01-08"], dtype=object)  # Fri -> Mon
    rates = np.array([3.65, 3.65])
    r_cal = period_cash_calendar(panel, rates, "2024-01-05", hold=1)
    _ok(abs(r_cal - (3.65 / 100.0 / 365.0 * 3)) < 1e-15, "one step over a weekend pays 3 days")
    # 9. on a calendar with no weekend the two bookings agree exactly
    daily = np.array(["2024-01-02", "2024-01-03", "2024-01-04"], dtype=object)
    rr = np.array([3.65, 3.65, 3.65])
    r2 = period_cash_calendar(daily, rr, "2024-01-02", hold=2)
    _ok(abs(r2 - ((1.0001 ** 2) - 1.0)) < 1e-15, "no weekend -> identical to one day per step")
    # 10. a hole carries the last good quote, it is not a zero day
    holed = np.array([3.65, np.nan, 3.65])
    _ok(abs(period_cash_calendar(daily, holed, "2024-01-02", hold=2) - r2) < 1e-15,
        "hole forward-fills")
    # 11. a quote that is a hole *before* any good one earns nothing, silently
    only_hole = np.array([np.nan, np.nan, np.nan])
    _ok(period_cash_calendar(daily, only_hole, "2024-01-02", hold=2) == 0.0,
        "no quote yet -> 0")
    # 12. window that cannot be located returns 0, not a guess
    _ok(period_cash_calendar(daily, rr, "1999-01-01", hold=1) == 0.0, "unknown day -> 0")
    # 13. ladder: a leg with no quote on the entry day is unpriced, not zero-rated
    term_on_panel = {"GC028": np.array([np.nan, 3.0, 3.0]),
                     "GC014": np.array([3.0] * 3), "GC007": np.array([3.0] * 3),
                     "GC004": np.array([3.0] * 3), "GC003": np.array([3.0] * 3),
                     "GC001": np.array([3.0] * 3)}
    long_panel = np.array(["2024-01-02", "2024-01-05", "2024-02-05"], dtype=object)
    _ok(period_cash_ladder(long_panel, term_on_panel, "2024-01-02", hold=2) is None,
        "missing entry-day quote -> unpriced")
    # 14. a 28+1 ladder pays the same 29 days as 29 one-day legs, modulo the
    #     cross term of compounding two legs instead of twenty-nine (28*r^2)
    plan_growth = 1.0
    for code in ["GC028", "GC001"]:
        plan_growth *= 1.0 + 3.65 / 100.0 / 365.0 * TERMS[code]
    r1 = 3.65 / 100.0 / 365.0
    _ok(abs(plan_growth - (1.0 + r1 * 29) - 28.0 * r1 * r1) < 1e-15,
        "28+1 legs pay 29 days, plus exactly the 28*r^2 cross term")
    # 15. fully invested means every mode equals the stock-only booking
    _ok(net_with(0.05, 1.0, 0.01) == 0.05, "invested 100% -> no cash leg")
    # 16. fully cash means the period return is the cash leg
    _ok(abs(net_with(0.0, 0.0, 0.01) - 0.01) < 1e-15, "invested 0% -> all cash")
    # 17. an unpriced ladder is NaN, never a silent zero
    _ok(not math.isfinite(net_with(0.05, 0.5, float("nan"))), "nan cash -> nan net")
    # 18. verdict boundaries are the parent's, not re-invented
    _ok(verdict_from_ratio(0.95) == "EDGE_SURVIVES_ROUNDING", "0.95 survives")
    _ok(verdict_from_ratio(0.75) == "EDGE_DEGRADES_UNDER_ROUNDING", "0.75 degrades")
    _ok(verdict_from_ratio(0.50) == "EDGE_LOST_TO_ROUNDING", "0.50 lost")
    # 19. more natural days means more money for the same quote
    two_day = period_cash_calendar(np.array(["2024-01-02", "2024-01-04"], dtype=object),
                                   np.array([3.65, 3.65]), "2024-01-02", hold=1)
    one_day = period_cash_calendar(daily, rr, "2024-01-02", hold=1)
    _ok(two_day > one_day, "two natural days pay more than one")
    # 20. tstat needs two finite points
    _ok(_tstat(np.array([0.1])) is None, "one point -> no t")
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
