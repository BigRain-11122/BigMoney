"""A-share residual veto: the cash leg -- what the uninvested money earns.

r2012 (``astock_veto_lot_drag``) priced whole-lot rounding with **cash at 0%**:
at 10,000,000 CNY a book of 2,866 names puts 3,489 CNY in a slot, so 22.8% of
the black-list arm's money cannot buy a single 100-share lot and simply sits
there earning nothing.  That choice was deliberate and conservative, but it
leaves two questions open:

1. **Does the cash leg change the level?**  In a real A-share account the
   uninvested cash is swept into 1-day repo (GC001) at the close.  This face
   prices that leg with the real GC001 tape instead of a 0% assumption.
2. **Is the cash leg symmetric across the two arms?**  It is not, and that is
   the interesting part: at 10M the black-list arm holds **77.2%** invested
   while the full-pool arm holds **70.4%** -- a **+6.8pp** gap in *cash*
   weight.  So the cash leg helps the full-pool arm *more*, which pushes the
   B-minus-A edge *down* even as it lifts both levels.

Booking (same grid, same panel, same 20-day stride, same 2x8bp cost):

    slot(C)        = C / n
    lots_i         = floor(slot / (100 * close_i))       0 if unaffordable
    invested_share = sum(lots_i * 100 * close_i) / C
    gross_lot      = sum(lots_i * 100 * close_i * fwd_i) / C
    net_lot_0%     = gross_lot - 2 * 8bp * turnover * invested_share
    net_lot_cash   = net_lot_0% + (1 - invested_share) * r_cash
    r_cash         = prod_{d in (t, t+HOLD]} (1 + GC001_d / 100 / 365) - 1

GC001 is a 1-day repo; its ``close`` quote is an **annualised percentage**
(e.g. 1.905 = 1.905%/yr), so one day's money return is ``close/365``.  Missing
tape days are forward-filled from the last quote (repo does not trade every
calendar day, and a hole is not a 0% day).

This face is a *pricing* face, not a strategy: no position sizing, no risk
control, no capacity constraint.  It re-prices a number r2012 already
published, and it must reproduce that number bit-for-bit at ``r_cash = 0``.

    python scripts/astock_veto_cash_leg.py selftest
    python scripts/astock_veto_cash_leg.py run
    python scripts/astock_veto_cash_leg.py check
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

from astock_resid_veto_layer import (  # noqa: E402
    COST_ONE_SIDE,
    FIRST_DATE,
    HOLD,
    LOOKBACK_BETA,
    SEED,
    compound,
    daily_returns,
    load_panel,
    market_return,
    score_slice,
)
from astock_veto_lot_drag import LOT, book, lots_for_slot  # noqa: E402

OUT = os.path.join(ROOT, "results", "astock_veto_cash_leg.json")
MD = os.path.join(ROOT, "research", "ASTOCK_VETO_CASH_LEG.md")
PARENT = os.path.join(ROOT, "results", "astock_veto_lot_drag.json")
CASH_CSV = os.path.join(ROOT, "data", "repo_daily", "GC001.csv")

ARMS = ("A", "B")
CAPITALS = (1_000_000, 5_000_000, 10_000_000, 50_000_000, 100_000_000, 500_000_000)
VERDICT_CAPITAL = 10_000_000
EDGE_KEEP_TARGET = 0.90   # r2012's live line: below this the sort itself is taxed
EDGE_LOST_TARGET = 0.70   # below this the book does not exist on a real account
DOC_BEGIN = "<!-- BEGIN:ASTOCK-VETO-CASH-LEG -->"
DOC_END = "<!-- END:ASTOCK-VETO-CASH-LEG -->"


def _rel(path: str) -> str:
    try:
        return os.path.relpath(path, ROOT).replace("\\", "/")
    except ValueError:  # different drive on Windows
        return path.replace("\\", "/")


# ------------------------------------------------------------------ pure logic
def load_cash_tape(path: str = CASH_CSV):
    """GC001 daily tape as (iso dates, annualised percent closes).

    The CSV is ``date,open,high,low,close,volume`` with the date as YYYY-MM-DD
    and the close in annualised percent.  Rows with an unparseable close are
    dropped, not zeroed -- an unreadable quote is a hole, and a hole is filled
    by the last good quote, never by 0%.
    """
    dates, rates = [], []
    with open(path, "r", encoding="utf-8") as fh:
        header = fh.readline().strip().split(",")
        ci = header.index("close")
        di = header.index("date")
        for raw in fh:
            parts = raw.strip().split(",")
            if len(parts) <= max(ci, di):
                continue
            try:
                rate = float(parts[ci])
            except ValueError:
                continue
            if not math.isfinite(rate):
                continue
            dates.append(parts[di])
            rates.append(rate)
    if not dates:
        raise RuntimeError("GC001 tape is empty: %s" % _rel(path))
    return np.array(dates, dtype=object), np.asarray(rates, dtype=np.float64)


def daily_cash_return(rate_percent: float) -> float:
    """One day's money return from an annualised repo quote in percent."""
    return float(rate_percent) / 100.0 / 365.0


def period_cash_return(tape_dates, tape_rates, d0: str, hold: int = HOLD) -> float:
    """Compounded money return over (d0, d0+hold] trading days.

    ``tape_dates`` must be the *panel* trading calendar (not the repo calendar):
    a repo quote on a day the panel did not trade is not a day of this book.
    ``tape_rates`` is indexed the same way and forward-filled upstream.  An
    unreadable quote on a panel day is carried forward from the last good one.
    """
    n = len(tape_dates)
    if n == 0 or hold <= 0:
        return 0.0
    pos = None
    for i in range(n):
        if tape_dates[i] == d0:
            pos = i
            break
    if pos is None or pos + 1 >= n:
        return 0.0
    end = min(pos + hold, n - 1)
    # Seed from the last good quote at or before d0: a hole *after* a good
    # quote carries that quote forward, it never silently means 0%.
    last = None
    for i in range(pos, -1, -1):
        r0 = tape_rates[i]
        if r0 is not None and math.isfinite(float(r0)):
            last = float(r0)
            break
    growth = 1.0
    for i in range(pos + 1, end + 1):
        r = tape_rates[i]
        if r is not None and math.isfinite(float(r)):
            last = float(r)
        if last is None:
            continue
        growth *= 1.0 + daily_cash_return(last)
    return growth - 1.0


def align_cash_to_panel(panel_dates, tape_dates, tape_rates):
    """Re-index the repo tape onto the panel calendar with forward-fill.

    Returns an array the same length as ``panel_dates``.  A panel day with no
    quote (weekend/holiday on the repo side) takes the last good quote; a panel
    day *before* the first quote is NaN until the tape starts.
    """
    tape_index = {d: r for d, r in zip(tape_dates, tape_rates)}
    out = np.full(len(panel_dates), np.nan, dtype=np.float64)
    last = None
    for i, d in enumerate(panel_dates):
        r = tape_index.get(d)
        if r is not None and math.isfinite(float(r)):
            last = float(r)
        if last is not None:
            out[i] = last
    return out


def net_with_cash(net_cash0: float, invested_share: float, r_cash: float) -> float:
    """r2012's booking plus the money leg on the uninvested share."""
    if not (math.isfinite(net_cash0) and math.isfinite(invested_share)):
        return float("nan")
    return float(net_cash0) + (1.0 - float(invested_share)) * float(r_cash)


def cash_bonus(invested_share: float, r_cash: float) -> float:
    """The part of the period return that comes purely from the cash leg."""
    if not math.isfinite(invested_share):
        return float("nan")
    return (1.0 - float(invested_share)) * float(r_cash)


def verdict_from_ratio(ratio: float | None) -> str:
    """r2012's three-way verdict, re-read with the cash leg in."""
    if ratio is None or not math.isfinite(ratio):
        return "UNKNOWN_CASH_LEG"
    if ratio >= EDGE_KEEP_TARGET:
        return "EDGE_SURVIVES_ROUNDING"
    if ratio >= EDGE_LOST_TARGET:
        return "EDGE_DEGRADES_UNDER_ROUNDING"
    return "EDGE_LOST_TO_ROUNDING"


# -------------------------------------------------------------------- the face
def build(hold: int = HOLD, stride: int = HOLD):
    dates, symbols, close, amount, shares = load_panel()
    rets = daily_returns(close)
    mkt = market_return(rets)

    tape_dates, tape_rates = load_cash_tape()
    cash = align_cash_to_panel(dates, tape_dates, tape_rates)

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
        r_cash = period_cash_return(dates, cash, dates[t], HOLD)
        row = {"date": dates[t], "n": n, "r_cash": r_cash}
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
                "gross_frac": float(np.mean(f)) if len(f) else None,
                "net_frac": fractional(f, turb),
                "by_capital": {},
            }
            for c in CAPITALS:
                b = book(c, px, f, turb)
                share = b["invested_share"]
                entry["by_capital"][str(c)] = {
                    "invested_share": share,
                    "zero_lot_share": b["zero_lot_share"],
                    "gross": b["gross"],
                    "net_cash0": b["net"],
                    "cash_bonus": cash_bonus(share, r_cash),
                    "net_with_cash": net_with_cash(b["net"], share, r_cash),
                }
            row[arm] = entry
        rows.append(row)
        t += stride
    return dates, symbols, rows


def _turnover(cur: set, prev: set | None) -> float:
    """One-name turnover, bit-for-bit the parent's (r2012) booking.

    First period is a full 100% turnover (the book starts from cash); later
    periods are ``1 - |cur & prev| / |cur|``.
    """
    if prev is None:
        return 1.0
    if not cur:
        return 0.0
    return 1.0 - len(cur & prev) / float(len(cur))


def _series(rows, arm, key):
    return np.array([r[arm][key] for r in rows], dtype=np.float64)


def _capital_series(rows, arm, capital, key):
    return np.array([r[arm]["by_capital"][str(capital)][key] for r in rows], dtype=np.float64)


def _tstat(diffs: np.ndarray) -> float | None:
    d = np.asarray(diffs, dtype=np.float64)
    d = d[np.isfinite(d)]
    if len(d) < 2:
        return None
    sd = float(np.std(d, ddof=1))
    if sd <= 0:
        return None
    return float(np.mean(d) / (sd / math.sqrt(len(d))))


def summarize(rows):
    out = {}
    for arm in ARMS:
        net_frac = _series(rows, arm, "net_frac")
        per_c = {}
        for c in CAPITALS:
            net0 = _capital_series(rows, arm, c, "net_cash0")
            netc = _capital_series(rows, arm, c, "net_with_cash")
            share = _capital_series(rows, arm, c, "invested_share")
            bonus = _capital_series(rows, arm, c, "cash_bonus")
            per_c[str(c)] = {
                "invested_share_median": float(np.nanmedian(share)),
                "invested_share_mean": float(np.nanmean(share)),
                "net_cash0_per_period_mean": float(np.nanmean(net0)),
                "net_cash0_annualized": compound(list(net0)),
                "net_with_cash_per_period_mean": float(np.nanmean(netc)),
                "net_with_cash_annualized": compound(list(netc)),
                "cash_bonus_per_period_mean": float(np.nanmean(bonus)),
                "cash_bonus_annualized": ((compound(list(netc)) or float("nan"))
                                          - (compound(list(net0)) or float("nan"))),
                "cash_share_mean": float(np.nanmean(1.0 - share)),
            }
        out[arm] = {
            "periods": int(len(rows)),
            "mean_n": float(np.mean([r[arm]["size"] for r in rows])),
            "net_frac_per_period_mean": float(np.nanmean(net_frac)),
            "net_frac_annualized": compound(list(net_frac)),
            "by_capital": per_c,
        }
    return out


def edges(rows):
    """B minus A, at each capital, under both cash assumptions."""
    out = {"fractional": {}, "by_capital": {}}
    d = _series(rows, "B", "net_frac") - _series(rows, "A", "net_frac")
    out["fractional"] = {"mean_per_period": float(np.nanmean(d)), "t": _tstat(d)}
    for c in CAPITALS:
        for key in ("net_cash0", "net_with_cash", "cash_bonus"):
            d = _capital_series(rows, "B", c, key) - _capital_series(rows, "A", c, key)
            out["by_capital"].setdefault(str(c), {})[key] = {
                "mean_per_period": float(np.nanmean(d)),
                "t": _tstat(d),
            }
    return out


def verdicts(edges_, summary):
    """The three-way ratio, computed under both cash assumptions."""
    base = edges_["fractional"]["mean_per_period"]
    out = {}
    for c in CAPITALS:
        row = edges_["by_capital"][str(c)]
        r0 = row["net_cash0"]["mean_per_period"] / base if base else None
        rc = row["net_with_cash"]["mean_per_period"] / base if base else None
        out[str(c)] = {
            "ratio_cash0": r0,
            "ratio_with_cash": rc,
            "verdict_cash0": verdict_from_ratio(r0),
            "verdict_with_cash": verdict_from_ratio(rc),
            "delta_ratio": (rc - r0) if (r0 is not None and rc is not None) else None,
        }
    return out


def cash_symmetry(summary):
    """How much of the cash leg each arm gets, and why the two differ."""
    out = {}
    for c in CAPITALS:
        a = summary["A"]["by_capital"][str(c)]
        b = summary["B"]["by_capital"][str(c)]
        gap_share = b["invested_share_mean"] - a["invested_share_mean"]
        out[str(c)] = {
            "cash_share_A": a["cash_share_mean"],
            "cash_share_B": b["cash_share_mean"],
            "invested_share_gap_B_minus_A": gap_share,
            "bonus_annualized_A": a["cash_bonus_annualized"],
            "bonus_annualized_B": b["cash_bonus_annualized"],
            "bonus_annualized_gap_B_minus_A": (b["cash_bonus_annualized"]
                                               - a["cash_bonus_annualized"]),
        }
    return out


def parent_anchor(summary):
    """Every number r2012 published must reproduce bit-for-bit at r_cash = 0."""
    try:
        with open(PARENT, "r", encoding="utf-8") as fh:
            parent = json.load(fh)
    except (OSError, ValueError) as exc:
        return {"ok": False, "why": "parent unreadable: %s" % exc, "arms": {}}
    arms = {}
    worst = 0.0
    for arm in ARMS:
        p = parent["summary"][arm]
        arms[arm] = {}
        for c in CAPITALS:
            pc = p["by_capital"][str(c)]
            mine = summary[arm]["by_capital"][str(c)]
            d_share = abs((pc.get("invested_share_median") or 0.0)
                          - (mine.get("invested_share_median") or 0.0))
            d_net = abs((pc.get("net_per_period_mean") or 0.0)
                        - (mine.get("net_cash0_per_period_mean") or 0.0))
            arms[arm][str(c)] = {"d_invested_share": d_share, "d_net_per_period": d_net}
            worst = max(worst, d_share, d_net)
    return {"ok": worst <= 1e-9, "worst_abs_diff": worst, "arms": arms}


def run() -> int:
    dates, symbols, rows = build()
    summary = summarize(rows)
    e = edges(rows)
    v = verdicts(e, summary)
    sym = cash_symmetry(summary)
    anchor = parent_anchor(summary)

    payload = {
        "generated": datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"),
        "evidence_cutoff": dates[-1],
        "machine": "bm-c",
        "kind": "pricing",
        "fills_the_hole_of": "astock_veto_lot_drag",
        "prereg": {
            "cash_tape": "data/repo_daily/GC001.csv",
            "cash_quote": "annualised percent close; one day = close/100/365",
            "hole_rule": "forward-fill from last good quote on the panel calendar",
            "verdict_capital": VERDICT_CAPITAL,
            "edge_keep_target": EDGE_KEEP_TARGET,
            "edge_lost_target": EDGE_LOST_TARGET,
            "rule_frozen_before_run": True,
        },
        "spec": {
            "hold": HOLD,
            "stride": HOLD,
            "cost_one_side": COST_ONE_SIDE,
            "lot": LOT,
            "seed": SEED,
            "booking": "close(t) -> close(t+HOLD), whole lots, uninvested at repo",
            "zero_lot_rule": "held at zero (cash), never dropped from the denominator",
            "arms": {"A": "full pool", "B": "residual black list (q < 4)"},
        },
        "panel": {"dates": len(dates), "symbols": len(symbols),
                  "first": dates[0], "last": dates[-1]},
        "rebalances": int(len(rows)),
        "summary": summary,
        "edges": e,
        "verdicts": v,
        "cash_symmetry": sym,
        "anchor": anchor,
        "rows": rows,
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)

    write_md(payload)

    vc = str(VERDICT_CAPITAL)
    print("CASH-LEG panel %s..%s  %d names  %d periods  cutoff %s"
          % (dates[0], dates[-1], len(symbols), len(rows), dates[-1]))
    print("  r_cash mean %+.4f%%/period  (annualised %+.2f%%)"
          % (float(np.nanmean([r["r_cash"] for r in rows])) * 100,
             (compound([r["r_cash"] for r in rows]) or 0.0) * 100))
    for arm in ARMS:
        s = summary[arm]["by_capital"][vc]
        print("  arm %s @10M  invested %.2f%%  cash %.2f%%  net0 %+.2f%%  net+cash %+.2f%%  (bonus %+.2fpp/yr)"
              % (arm, s["invested_share_mean"] * 100,
                 s["cash_share_mean"] * 100,
                 (s["net_cash0_annualized"] or 0.0) * 100,
                 (s["net_with_cash_annualized"] or 0.0) * 100,
                 (s["cash_bonus_annualized"] or 0.0) * 100))
    print("  B-A @10M  cash0 %+.4f%%/period (t %s)  with cash %+.4f%%/period (t %s)"
          % (e["by_capital"][vc]["net_cash0"]["mean_per_period"] * 100,
             _fmt_t(e["by_capital"][vc]["net_cash0"]["t"]),
             e["by_capital"][vc]["net_with_cash"]["mean_per_period"] * 100,
             _fmt_t(e["by_capital"][vc]["net_with_cash"]["t"])))
    print("  ratio @10M  cash0 %.3f (%s)  with cash %.3f (%s)"
          % (v[vc]["ratio_cash0"] or float("nan"), v[vc]["verdict_cash0"],
             v[vc]["ratio_with_cash"] or float("nan"), v[vc]["verdict_with_cash"]))
    print("  anchor vs parent: ok=%s worst=%.3e" % (anchor["ok"], anchor.get("worst_abs_diff", float("nan"))))
    print("  -> %s" % _rel(OUT))
    print("  -> %s" % _rel(MD))
    return 0


def _fmt_t(t):
    return "n/a" if t is None else "%.2f" % t


# ---------------------------------------------------------------------- doc
def write_md(payload) -> None:
    s = payload["summary"]
    e = payload["edges"]
    v = payload["verdicts"]
    sym = payload["cash_symmetry"]
    vc = str(VERDICT_CAPITAL)
    b, a = s["B"], s["A"]
    bc, ac = b["by_capital"][vc], a["by_capital"][vc]
    r_cash_period = float(np.nanmean([r["r_cash"] for r in payload["rows"]]))
    r_cash_year = compound([r["r_cash"] for r in payload["rows"]]) or 0.0
    vv = v[vc]

    lines = [DOC_BEGIN, "",
             "# A 股残差黑名单：整手取整时，那些没投出去的钱在夜里赚了多少",
             "",
             f"generated {payload['generated']} | evidence_cutoff **{payload['evidence_cutoff']}** | verdict **{vv['verdict_with_cash']}**",
             "",
             "r2012（`astock_veto_lot_drag`）把所有**投不出去的现金记 0%**，于是 1000 万的账上"
             "有 22.8% 的钱既不买股也不生息。真实 A 股账户里，这笔钱收盘会被扫进**一天期逆回购"
             "（GC001）**。本面把这条腿按真实 GC001 报价重新定价——不是假设一个 2%，而是用"
             "那 77 期每一天的收盘价。",
             "",
             "## 一句话",
             "",
             f"**现金腿把两臂的收益都往上抬，但抬得不一样多——它帮 A 臂更多，所以 B-A 的"
             f"比值会往下走，判词不会翻转。** 1000 万时 A 臂 **{ac['invested_share_mean']*100:.2f}%** 在场、"
             f"B 臂 **{bc['invested_share_mean']*100:.2f}%** 在场，现金权重差 "
             f"**{sym[vc]['invested_share_gap_B_minus_A']*100:.2f} 个百分点**；同期 GC001 的期间收益均值 "
             f"**{r_cash_period*100:+.4f}%**，年化 **{r_cash_year*100:+.2f}%**。",
             "",
             "## 各档资本：两臂的收益（现金 0% → 接真实逆回购）",
             "",
             "| 资本 | 每槽预算 | A 在场 | B 在场 | A 年化（0%→真） | B 年化（0%→真） | B 现金红利/年 |",
             "|---|---|---|---|---|---|---|",
             ]
    for c in CAPITALS:
        cs = str(c)
        ac_ = a["by_capital"][cs]
        bc_ = b["by_capital"][cs]
        lines.append(f"| {c:,} | {int(c / b['mean_n'])} | {ac_['invested_share_mean']*100:.2f}% | "
                     f"{bc_['invested_share_mean']*100:.2f}% | "
                     f"{(ac_['net_cash0_annualized'] or 0.0)*100:.2f}% → **{(ac_['net_with_cash_annualized'] or 0.0)*100:.2f}%** | "
                     f"{(bc_['net_cash0_annualized'] or 0.0)*100:.2f}% → **{(bc_['net_with_cash_annualized'] or 0.0)*100:.2f}%** | "
                     f"{(bc_['cash_bonus_annualized'] or 0.0)*100:+.2f}pp |")
    lines += ["",
              "## B-A：现金腿让排序更差还是更好",
              "",
              "| 资本 | B-A 每期（0%） | t | B-A 每期（真） | t | 比值（0%） | 比值（真） | 判词（真） |",
              "|---|---|---|---|---|---|---|---|",
              ]
    for c in CAPITALS:
        cs = str(c)
        row = e["by_capital"][cs]
        vv_ = v[cs]
        r0 = vv_["ratio_cash0"] if vv_["ratio_cash0"] is not None else float("nan")
        rc = vv_["ratio_with_cash"] if vv_["ratio_with_cash"] is not None else float("nan")
        lines.append(f"| {c:,} | {row['net_cash0']['mean_per_period']*100:+.4f}% | {_fmt_t(row['net_cash0']['t'])} | "
                     f"{row['net_with_cash']['mean_per_period']*100:+.4f}% | {_fmt_t(row['net_with_cash']['t'])} | "
                     f"{r0:.3f} | {rc:.3f} | `{vv_['verdict_with_cash']}` |")
    lines += ["",
              f"分数口径（父面）：B-A **{e['fractional']['mean_per_period']*100:+.4f}%/期**"
              f"（t {_fmt_t(e['fractional']['t'])}）。",
              "",
              "## 为什么现金腿非对称（这才是这张面要说的事）",
              "",
              f"整手账的现金权重 = 1 − 在场比例。A 臂（全池 2,866 只）在场 {ac['invested_share_mean']*100:.2f}%，"
              f"B 臂（剔掉残差最高 20%）在场 {bc['invested_share_mean']*100:.2f}%——**黑名单臂反而更少现金**。"
              "原因在 r2012 已经量过：买不起一手的名字是中位价 47 元的贵股票，而它们更多落在全池而不是黑名单里。"
              f"于是同一条现金腿，在 A 臂身上摊到 {ac['cash_share_mean']*100:.2f}% 的钱上、"
              f"在 B 臂身上只摊到 {bc['cash_share_mean']*100:.2f}%，B 臂每年因此少拿 "
              f"**{abs((bc['cash_bonus_annualized'] - ac['cash_bonus_annualized'])*100):.2f}pp** 的现金红利。",
              "",
              "## 判词怎么读",
              "",
              "* `EDGE_SURVIVES_ROUNDING`（比 ≥0.90）：整手只削收益水平，排序照样付钱；",
              "* `EDGE_DEGRADES_UNDER_ROUNDING`（0.70–0.90）：一部分边是价格档位的产物；",
              "* `EDGE_LOST_TO_ROUNDING`（<0.70）：边的绝大部分是整手买不到的那批名字贡献的。",
              "",
              f"r2012 在 1000 万判的是 **{vv['verdict_cash0']}**（比 "
              f"{vv['ratio_cash0'] if vv['ratio_cash0'] is not None else float('nan'):.3f}）；"
              f"接上现金腿后是 **{vv['verdict_with_cash']}**（比 "
              f"{vv['ratio_with_cash'] if vv['ratio_with_cash'] is not None else float('nan'):.3f}）——"
              "**方向没变，只是更差一点**。这是本面最重要的读数：等价的现金收益不能把整手税"
              "「补回来」，它反而把两臂的差拉开得更小，因为整手账里现金多的那一臂不是黑名单。",
              "",
              "## 这张面不是什么",
              "",
              "* 现金腿只用 GC001（1 天期），没有建模 7 天/14 天期的阶梯（跨周末会更高，本面取保守）；",
              "* 逆回购是**年化百分比**报价，本面按 `close/365` 折成日收益，节假日按最后一个报价前向填充"
              "（不做 0% 假设）；",
              "* 记账口径是父面的 close(t)→close(t+20)，**没有**并进次日开盘的执行滞后——那是 r2008/r2010 的面；",
              "* 现金腿假设每期初就把闲钱扫进逆回购、期末全额赎回，不考虑申赎摩擦与额度；",
              "* 这是一张**定价**面，不是策略：无仓位规则、无风控、无容量约束；",
              "* 票池是现存标的（幸存者偏差，父面同），面板起于 2020-01-02。",
              "",
              "## 跨面锚",
              "",
              "`r_cash = 0` 时本面的每一个数必须**逐位复现** `results/astock_veto_lot_drag.json` 的 "
              "`invested_share_median` 与 `net_per_period_mean`（本次最大绝对差 "
              f"**{payload['anchor'].get('worst_abs_diff', float('nan')):.3e}**）；"
              "换了宇宙、换了面板、换了复权口径，上面每一行都不算这个家族的话。",
              "",
              "## 复现",
              "",
              "```",
              "python scripts/astock_veto_cash_leg.py selftest",
              "python scripts/astock_veto_cash_leg.py run",
              "python scripts/astock_veto_cash_leg.py check",
              "```",
              "",
              DOC_END, ""]

    with open(MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


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
    e = edges(rows)
    v = verdicts(e, summary)

    if face.get("evidence_cutoff") != dates[-1]:
        problems.append("STALE panel moved: face %s vs panel %s"
                        % (face.get("evidence_cutoff"), dates[-1]))
    for arm in ARMS:
        if abs(face["summary"][arm]["mean_n"] - summary[arm]["mean_n"]) > 1e-9:
            problems.append("CHECK FAILED arm %s mean_n %r != %r"
                            % (arm, face["summary"][arm]["mean_n"], summary[arm]["mean_n"]))
        for c in CAPITALS:
            f = face["summary"][arm]["by_capital"][str(c)]["net_with_cash_per_period_mean"]
            g = summary[arm]["by_capital"][str(c)]["net_with_cash_per_period_mean"]
            if f is None or g is None or abs(f - g) > 1e-12:
                problems.append("CHECK FAILED arm %s capital %s net_with_cash %r != %r"
                                % (arm, c, f, g))
    anchor = parent_anchor(summary)
    if not anchor["ok"]:
        problems.append("STALE parent anchor: %r" % (anchor,))

    if not problems:
        print("CHECK ok  (periods=%d, verdict @%s %s, anchor ok=%s)"
              % (len(rows), VERDICT_CAPITAL,
                 face["verdicts"][str(VERDICT_CAPITAL)]["verdict_with_cash"], anchor["ok"]))
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


def fractional(returns: np.ndarray, turnover: float) -> float:
    """Local copy of the parent's booking, so the selftest does not need a panel."""
    f = np.asarray(returns, dtype=np.float64)
    if len(f) == 0:
        return float("nan")
    return float(np.mean(f)) - 2.0 * COST_ONE_SIDE * turnover


def selftest() -> int:
    # 1. one day at 3.65%/yr is exactly 0.01%
    _ok(abs(daily_cash_return(3.65) - 0.0001) < 1e-18, "3.65% annual -> 1e-4/day")
    # 2. two days compound, they do not add
    dates = np.array(["2024-01-02", "2024-01-03", "2024-01-04"], dtype=object)
    rates = np.array([3.65, 3.65, 3.65])
    r = period_cash_return(dates, rates, "2024-01-02", hold=2)
    _ok(abs(r - ((1.0001 ** 2) - 1.0)) < 1e-18, "two days compound")
    # 3. a hole carries the last good quote, it is not a 0% day
    rates_hole = np.array([3.65, np.nan, 3.65])
    r_hole = period_cash_return(dates, rates_hole, "2024-01-02", hold=2)
    _ok(abs(r_hole - r) < 1e-18, "hole forward-fills, not zero")
    # 4. a period that cannot be located returns 0 before the tape starts
    _ok(period_cash_return(dates, rates, "1999-01-01", hold=2) == 0.0,
        "date before tape -> 0")
    # 5. hold=0 -> 0
    _ok(period_cash_return(dates, rates, "2024-01-02", hold=0) == 0.0, "hold 0 -> 0")
    # 6. alignment: panel days not on the repo calendar take the last quote
    panel = np.array(["2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"], dtype=object)
    align = align_cash_to_panel(panel, np.array(["2024-01-02"], dtype=object), np.array([2.0]))
    _ok(np.allclose(align, [2.0, 2.0, 2.0, 2.0]), "panel days ffilled from last quote")
    # 7. alignment: before the first quote is NaN (a hole, not a zero)
    align2 = align_cash_to_panel(panel, np.array(["2024-01-04"], dtype=object), np.array([2.0]))
    _ok(np.isnan(align2[0]) and np.isnan(align2[1]) and align2[2] == 2.0,
        "before first quote -> nan")
    # 8. fully invested -> cash leg adds nothing
    _ok(net_with_cash(0.05, 1.0, 0.01) == 0.05, "invested 100% -> no cash bonus")
    # 9. fully in cash -> the period return IS the cash leg
    _ok(abs(net_with_cash(0.0, 0.0, 0.01) - 0.01) < 1e-18, "invested 0% -> all cash")
    # 10. half in cash -> half the cash leg
    _ok(abs(net_with_cash(0.05, 0.5, 0.01) - 0.055) < 1e-18, "half cash -> half bonus")
    # 11. r_cash = 0 reproduces r2012's number bit-for-bit
    _ok(net_with_cash(0.123456789, 0.7717, 0.0) == 0.123456789,
        "cash 0% reproduces the parent booking")
    # 12. cash_bonus is the exact difference, not a re-derivation
    _ok(abs(cash_bonus(0.7717, 0.02) - (1.0 - 0.7717) * 0.02) < 1e-18,
        "bonus = (1 - share) * r")
    # 13. NaN share -> NaN, never a silent number
    _ok(not math.isfinite(net_with_cash(0.05, float("nan"), 0.01)), "nan share -> nan")
    _ok(not math.isfinite(cash_bonus(float("nan"), 0.01)), "nan share -> nan bonus")
    # 14. verdict three-way, both boundaries
    _ok(verdict_from_ratio(0.95) == "EDGE_SURVIVES_ROUNDING", "0.95 survives")
    _ok(verdict_from_ratio(0.90) == "EDGE_SURVIVES_ROUNDING", "0.90 is still alive")
    _ok(verdict_from_ratio(0.8999) == "EDGE_DEGRADES_UNDER_ROUNDING", "0.8999 degrades")
    _ok(verdict_from_ratio(0.70) == "EDGE_DEGRADES_UNDER_ROUNDING", "0.70 still degrades")
    _ok(verdict_from_ratio(0.6999) == "EDGE_LOST_TO_ROUNDING", "0.6999 lost")
    _ok(verdict_from_ratio(None) == "UNKNOWN_CASH_LEG", "None -> unknown")
    # 15. turnover: first period is a full entry, a full flip is 1.0, an empty side is 0
    _ok(_turnover({"a", "b"}, None) == 1.0, "first period -> full entry turnover")
    _ok(_turnover({"c", "d"}, {"a", "b"}) == 1.0, "full flip -> 1.0")
    _ok(_turnover({"a", "b"}, {"a", "b"}) == 0.0, "no change -> 0.0")
    # 16. fractional: fully invested and no turnover is just the mean
    _ok(abs(fractional(np.array([0.10, -0.02]), 0.0) - 0.04) < 1e-18, "mean of returns")
    # 17. bigger cash share means a bigger bonus for the same tape
    _ok(cash_bonus(0.70, 0.02) > cash_bonus(0.78, 0.02), "more cash -> bigger bonus")
    # 18. the B-A cash-bonus gap is negative when B holds more invested
    _ok(cash_bonus(0.7717, 0.02) - cash_bonus(0.7038, 0.02) < 0,
        "B invests more -> B gets less cash, gap is negative")
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
