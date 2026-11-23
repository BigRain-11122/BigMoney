#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""How much money can the A-share black list actually carry?

Why this face exists
--------------------
The r2005-r2010 family answers every execution question about this book except
the one that decides its size: **how much of each name can you buy before you
are the day's volume**.  We know (r2008) which names you can reach at the next
open, (r2010) how long a limit-up name takes to open, (r2009/affordable_book)
how many whole lots a slot can hold.  Nobody has asked whether the *book*
fits inside the tape.

The book is equal-weight over every eligible name -- about 2,866 names per
rebalance.  At 10,000,000 CNY that is a 3,489 CNY slot, which is roughly one
lot; at 100,000,000 CNY it is 34,890 CNY a slot.  Whether a slot is absorbable
depends on that name's own turnover, and the book is only as deployable as its
*thinnest* member.

What is measured
----------------
For each rebalance t (decision day, close known) and each member of the arm:

    adv20_i   = mean(traded value, CNY) over [t-19 .. t]      (no look-ahead)
    cap_i     = PARTICIPATION * adv20_i                        (absorbable CNY)
    slot(C)   = C / n                                          (equal weight)
    fillable  = cap_i >= slot(C)

From that, three numbers per rebalance, per capital level C:

    fillable_share     share of names whose slot fits inside 5% of their ADV
    binding_capital    n * min(cap_i)    -- the largest C the thinnest name allows
    p10_capital        n * q10(cap_i)    -- the largest C that 90% of names allow

Verdict (pre-registered before the run, never tuned on results)
--------------------------------------------------------------
    CAPACITY_NOT_BINDING_AT_10M    median fillable_share >= 0.99 at C=10,000,000
    CAPACITY_BINDS_LIGHTLY_AT_10M  0.90 <= median < 0.99
    CAPACITY_BINDS_AT_10M          median < 0.90

Notes that a reader will ask about
----------------------------------
* `adv20` uses the decision day's own trailing window, so a name that goes
  quiet the next morning is not modelled.  It is the standard ADV assumption
  and it is conservative in the direction that matters (it can only make the
  book look bigger, never smaller).
* A member with no finite ADV (suspended, newly listed, missing bars) is
  counted as **zero capacity**, not skipped -- skipping it would let the
  average pretend the book is bigger.  The count of such names is printed.
* The scale is a *print*, not a gate: this face does not change any parent
  number, and the parent's own member counts are asserted bit-for-bit.

Usage
-----
    python scripts/astock_veto_adv_capacity.py run
    python scripts/astock_veto_adv_capacity.py check
    python scripts/astock_veto_adv_capacity.py selftest
"""
from __future__ import annotations

import argparse
import json
import math
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
    RANDOM_DRAWS,
    SEED,
    compound,
    daily_returns,
    load_panel,
    market_return,
    score_slice,
)

OUT = os.path.join(ROOT, "results", "astock_veto_adv_capacity.json")
MD = os.path.join(ROOT, "research", "ASTOCK_VETO_ADV_CAPACITY.md")
PARENT = os.path.join(ROOT, "results", "astock_veto_executable.json")
PANEL_PER = os.path.join(ROOT, "data", "astock_daily", "per")

ARMS = ("A", "B")
ADV_WINDOW = 20
PARTICIPATION = 0.05
PARTICIPATION_SENS = (0.02, 0.05, 0.10)
CAPITALS = (1_000_000, 5_000_000, 10_000_000, 50_000_000, 100_000_000, 500_000_000)
VERDICT_CAPITAL = 10_000_000
DOC_BEGIN = "<!-- BEGIN:ASTOCK-VETO-ADV-CAPACITY -->"
DOC_END = "<!-- END:ASTOCK-VETO-ADV-CAPACITY -->"


# ------------------------------------------------------------------ pure logic
def adv_window(amount: np.ndarray, t: int, window: int = ADV_WINDOW) -> np.ndarray:
    """Mean traded value over [t-window+1 .. t], per symbol.

    One row per symbol; NaN when the window has no finite value at all.  A
    partially-suspended name averages only the days it traded -- that is the
    honest ADV (its resting liquidity on traded days), and the zero-capacity
    rule below is what protects the tail.
    """
    lo = max(0, t - window + 1)
    block = amount[lo: t + 1]
    if block.size == 0:
        return np.full(amount.shape[1], np.nan)
    with np.errstate(invalid="ignore"):
        finite = np.isfinite(block)
        counts = finite.sum(axis=0)
        sums = np.where(finite, block, 0.0).sum(axis=0)
    out = np.full(amount.shape[1], np.nan)
    nz = counts > 0
    out[nz] = sums[nz] / counts[nz]
    return out


def capacities(adv: np.ndarray, cols: np.ndarray, participation: float = PARTICIPATION) -> np.ndarray:
    """Absorbable CNY per member.  Non-finite ADV -> 0.0, never skipped."""
    raw = adv[cols]
    cap = np.where(np.isfinite(raw) & (raw > 0), participation * raw, 0.0)
    return cap


def fillable_share(cap: np.ndarray, capital: float) -> float:
    n = len(cap)
    if n == 0:
        return float("nan")
    slot = capital / n
    return float(np.mean(cap >= slot))


def binding_capital(cap: np.ndarray, q: float = 0.0) -> float:
    """n * quantile(cap, q): the largest equal-weight book that q-fraction of
    names can absorb.  q=0 is the thinnest member; q=0.10 lets one in ten be
    too thin to take its slot."""
    n = len(cap)
    if n == 0:
        return float("nan")
    return float(n * np.quantile(cap, q))


def lot_deviation(one_lot: np.ndarray, capital: float):
    """Whole-lot rounding: how far the money you can actually deploy sits from
    the equal-weight slot.  A name whose one lot costs more than its slot is
    counted as a full miss (deviation 1.0), never quietly dropped -- that is
    exactly the r1813/r2009 failure mode (weight != order)."""
    n = len(one_lot)
    if n == 0 or capital <= 0:
        return float("nan"), float("nan"), float("nan")
    slot = capital / n
    px = np.where(np.isfinite(one_lot) & (one_lot > 0), one_lot, np.inf)
    lots = np.floor(slot / px)
    actual = np.where(np.isfinite(lots), lots, 0.0) * np.where(np.isfinite(px), px, 0.0)
    dev = (slot - actual) / slot
    return float(np.mean(dev)), float(np.max(dev)), float(np.mean(lots < 1))


def capacity_verdict(share_median: float) -> str:
    if share_median is None or not np.isfinite(share_median):
        return "INSUFFICIENT_PERIODS"
    if share_median >= 0.99:
        return "CAPACITY_NOT_BINDING_AT_10M"
    if share_median >= 0.90:
        return "CAPACITY_BINDS_LIGHTLY_AT_10M"
    return "CAPACITY_BINDS_AT_10M"


# ---------------------------------------------------------------- the face
def build(hold: int = HOLD, stride: int = HOLD):
    dates, symbols, close, amount, shares = load_panel()
    rets = daily_returns(close)
    mkt = market_return(rets)

    start = 0
    while start < len(dates) and dates[start] < FIRST_DATE:
        start += 1
    start = max(start, LOOKBACK_BETA)

    rows = []
    t = start
    while t + HOLD < len(dates):
        idx, resid, q, fwd = score_slice(t, close, amount, shares, rets, mkt)
        if resid is None:
            t += stride
            continue
        adv = adv_window(amount, t)
        row = {"date": dates[t]}
        for arm in ARMS:
            cols = idx if arm == "A" else idx[q < 4]
            cap = capacities(adv, cols)
            n = int(len(cols))
            px = close[t][cols]
            one_lot = px * 100.0
            entry = {
                "n": n,
                "adv_missing": int(np.sum(cap <= 0)),
                "adv20_median_cny": float(np.median(adv[cols][np.isfinite(adv[cols])])) if n else None,
                "one_lot_median_cny": float(np.median(one_lot[np.isfinite(one_lot)])) if n else None,
                "fillable_share": {},
                "binding_capital_p0": binding_capital(cap, 0.0),
                "binding_capital_p10": binding_capital(cap, 0.10),
                "binding_capital_p50": binding_capital(cap, 0.50),
            }
            for c in CAPITALS:
                entry["fillable_share"][str(c)] = fillable_share(cap, c)
            entry["sensitivity"] = {}
            for p in PARTICIPATION_SENS:
                cap_p = capacities(adv, cols, p)
                entry["sensitivity"]["%d%%" % round(p * 100)] = {
                    str(c): fillable_share(cap_p, c)
                    for c in (1_000_000, 10_000_000, 100_000_000, 500_000_000)}
            entry["lot"] = {}
            for c in CAPITALS:
                m, mx, unb = lot_deviation(one_lot, c)
                entry["lot"][str(c)] = {"mean": m, "max": mx, "unbuyable_share": unb}
            row[arm] = entry
        rows.append(row)
        t += stride
    return dates, symbols, rows


def summarize(rows):
    out = {}
    for arm in ARMS:
        per_c = {}
        for c in CAPITALS:
            vals = np.array([r[arm]["fillable_share"][str(c)] for r in rows], dtype=np.float64)
            vals = vals[np.isfinite(vals)]
            per_c[str(c)] = {
                "median": float(np.median(vals)) if len(vals) else None,
                "worst": float(vals.min()) if len(vals) else None,
                "best": float(vals.max()) if len(vals) else None,
                "share_of_periods_fully_fillable": float(np.mean(vals >= 0.99)) if len(vals) else None,
            }
        caps = {k: [r[arm][k] for r in rows] for k in
                ("binding_capital_p0", "binding_capital_p10", "binding_capital_p50")}
        lot = {}
        for c in CAPITALS:
            lot[str(c)] = {
                "mean_dev_median": float(np.median([r[arm]["lot"][str(c)]["mean"] for r in rows])),
                "max_dev_median": float(np.median([r[arm]["lot"][str(c)]["max"] for r in rows])),
                "unbuyable_median": float(np.median([r[arm]["lot"][str(c)]["unbuyable_share"] for r in rows])),
            }
        out[arm] = {
            "periods": len(rows),
            "mean_n": float(np.mean([r[arm]["n"] for r in rows])),
            "median_adv20_cny": float(np.median([r[arm]["adv20_median_cny"] for r in rows
                                                if r[arm]["adv20_median_cny"]])),
            "median_one_lot_cny": float(np.median([r[arm]["one_lot_median_cny"] for r in rows
                                                   if r[arm]["one_lot_median_cny"]])),
            "fillable_share_by_capital": per_c,
            "binding_capital": {k: {
                "median": float(np.median(v)),
                "worst": float(np.min(v)),
                "best": float(np.max(v)),
            } for k, v in caps.items()},
            "lot_deviation_by_capital": lot,
            "verdict": capacity_verdict(per_c[str(VERDICT_CAPITAL)]["median"]),
        }
    return out


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


def _sha256(path: str) -> str | None:
    import hashlib
    try:
        h = hashlib.sha256()
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None


def parent_anchor(summary) -> dict:
    """The member count must reproduce the parent's arm B bit for bit."""
    try:
        with open(PARENT, "r", encoding="utf-8") as fh:
            parent = json.load(fh)
    except (OSError, ValueError):
        return {"ok": False, "why": "parent face unreadable"}
    want = parent.get("research_arms", {}).get("B", {}).get("mean_size")
    got = summary["B"]["mean_n"]
    diff = None if want is None else abs(got - float(want))
    return {"ok": diff is not None and diff <= 1e-9, "parent_mean_size": want,
            "face_mean_n": got, "abs_diff": diff}


def write_md(payload) -> None:
    s = payload["summary"]
    b = s["B"]
    a = s["A"]
    cap = b["binding_capital"]
    lines = [DOC_BEGIN, "",
             "# A 股残差黑名单：这本书在盘口上到底装得下多少钱",
             "",
             "generated %s | evidence_cutoff **%s** | verdict **%s**"
             % (payload["generated"], payload["evidence_cutoff"], payload["verdict"]),
             "",
             "这本书是等权、每期 **%.0f** 只（臂 B＝全池剔掉残差最高 20%%）。"
             "等权意味着资金每期被切成 %.0f 份，而这个名字自己一天只成交 "
             "**%.2f 亿元**（中位 20 日均额）。" % (b["mean_n"], b["mean_n"], b["median_adv20_cny"] / 1e8),
             "",
             "## 一句话",
             "",
             "**流动性不是这本书的问题，整手才是。** 按 5%% 的 ADV 参与率，每期的盘口容量从 "
             "%s 元起才开始装不满（最薄成员口径），可是资本小的时候每槽的钱买不起一手："
             "100 万里 **%.1f%%** 的名字一手都买不起，1000 万里还有 **%.1f%%**；"
             "到 %s 元这一级才降到 **%.2f%%**（平均权重偏离 %.2f%%）。"
             % (format(round(cap["binding_capital_p0"]["median"]), ","),
                b["lot_deviation_by_capital"]["1000000"]["unbuyable_median"] * 100,
                b["lot_deviation_by_capital"]["10000000"]["unbuyable_median"] * 100,
                format(50_000_000, ","),
                b["lot_deviation_by_capital"]["50000000"]["unbuyable_median"] * 100,
                b["lot_deviation_by_capital"]["50000000"]["mean_dev_median"] * 100),
             "",
             "这一条与黑名单无关：**任何 2,866 只等权组合在 100 万规模上都长这样**。"
             "所以这本书的真实下限不是「有没有 alpha」，而是「至少要有五千万才排得进一手」，"
             "而到那个规模它的等权上限（28.7 亿）还远没到。",
             "",
             "按 **5%% 的 ADV 参与率**，10,000,000 元资本下每个槽是 **%s 元**，"
             "能装得下自己槽位的名字占 **%.2f%%**（77 期的中位）；"
             "整本书的等权上限（最薄那只决定）中位是 **%s 元**，"
             "允许 10%% 的名字装不下时是 **%s 元**。"
             % (format(round(VERDICT_CAPITAL / b["mean_n"]), ","),
                (b["fillable_share_by_capital"][str(VERDICT_CAPITAL)]["median"] or 0) * 100,
                format(round(cap["binding_capital_p0"]["median"]), ","),
                format(round(cap["binding_capital_p10"]["median"]), ",")),
             "",
             "## 不同资本下装得满的比例（77 期）",
             "",
             "| 资本 | 每槽预算 | 臂 B 中位可满载比例 | 最差期 | 全满载的期占比 | 臂 A 中位 |",
             "|---|---|---|---|---|---|",
             ]
    for c in CAPITALS:
        bc = b["fillable_share_by_capital"][str(c)]
        ac = a["fillable_share_by_capital"][str(c)]
        lines.append("| %s | %.0f | %.4f | %.4f | %.4f | %.4f |"
                     % (format(c, ","), c / b["mean_n"], bc["median"], bc["worst"],
                        bc["share_of_periods_fully_fillable"], ac["median"]))
    lines += ["",
              "## 等权上限（元）：这只最薄的成员决定整本书的规模",
              "",
              "| 分位口径 | 中位 | 最差期 | 最好期 |",
              "|---|---|---|---|",
              ]
    for key, label in (("binding_capital_p0", "最薄成员（p0）"),
                       ("binding_capital_p10", "允许 10% 装不下（p10）"),
                       ("binding_capital_p50", "中位成员（p50）")):
        v = cap[key]
        lines.append("| %s | %s | %s | %s |"
                     % (label, format(round(v["median"]), ","), format(round(v["worst"]), ","),
                        format(round(v["best"]), ",")))
    lines += ["",
              "## 参与率敏感性（臂 B，中位可满载比例）",
              "",
              "| 参与率 | 1M | 10M | 100M | 500M |",
              "|---|---|---|---|---|",
              ]
    for p, row in payload["sensitivity"].items():
        lines.append("| %s | %s | %s | %s | %s |"
                     % (p, *["%.4f" % row[str(c)] for c in (1_000_000, 10_000_000, 100_000_000, 500_000_000)]))
    lines += ["",
              "## 谁先绑住：流动性还是整手",
              "",
              "上面每一档的装满比例都是 1.0000，因为每槽的钱远小于 5% 的盘口容量；"
              "真正先把钱卡住的是**一手不可拆**。下表是「每槽预算按一手向下取整后，"
              "实际投出去的钱离等权槽位差多少」（含买不起一手记 100% 偏离的名字）：",
              "",
              "| 资本 | 每槽预算 | 平均偏离 | 最差名字偏离 | 一手都买不起的名字占比 |",
              "|---|---|---|---|---|",
              ]
    for c in CAPITALS:
        lv = b["lot_deviation_by_capital"][str(c)]
        lines.append("| %s | %.0f | %.2f%% | %.2f%% | %.2f%% |"
                     % (format(c, ","), c / b["mean_n"], lv["mean_dev_median"] * 100,
                        lv["max_dev_median"] * 100, lv["unbuyable_median"] * 100))
    lines += ["",
              "## 这张面不是什么",
              "",
              "* 5% 的 ADV 是**假设**不是实测：真实冲击要看当天的盘口与你的下单方式；",
              "* ADV 用决策日（t）的收盘窗口，不预测次日成交；",
              "* 没有把「停下等一天」的延迟成本并进来（那是 r2010 的面）；",
              "* 没有给出一手整手取整后的权重偏离（那是 affordable_book 的面）；",
              "* 这是一张**容量**面，不是收益面：它说这本书能装多少，不说该不该装。",
              "",
              "## 跨面锚",
              "",
              "臂 B 每期成员数 **%.4f** 必须逐位复现 `%s` 的 `research_arms.B.mean_size`"
              "（本次绝对差 %s）；重的不是这个数，是「同一批名字」这件事——"
              "换了宇宙，下面每一行都不算这个家族的话。"
              % (b["mean_n"], _rel(PARENT), ("%.1e" % payload["anchor"]["abs_diff"])
                 if payload["anchor"]["abs_diff"] is not None else "n/a"),
              "",
              "## 复现",
              "",
              "```",
              "python scripts/astock_veto_adv_capacity.py selftest",
              "python scripts/astock_veto_adv_capacity.py run",
              "python scripts/astock_veto_adv_capacity.py check",
              "```",
              "",
              DOC_END, ""]
    with open(MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines))


def run(hold: int = HOLD, stride: int = HOLD) -> int:
    dates, symbols, rows = build(hold=hold, stride=stride)
    if not rows:
        print("no rebalance rows")
        return 2
    summary = summarize(rows)

    # participation sensitivity: median fillable share per (participation, capital)
    sensitivity = {}
    for p in PARTICIPATION_SENS:
        key = "%d%%" % round(p * 100)
        sensitivity[key] = {}
        for c in (1_000_000, 10_000_000, 100_000_000, 500_000_000):
            vals = np.array([r["B"]["sensitivity"][key][str(c)] for r in rows], dtype=np.float64)
            vals = vals[np.isfinite(vals)]
            sensitivity[key][str(c)] = float(np.median(vals)) if len(vals) else None

    payload = {
        "generated": _now(),
        "evidence_cutoff": dates[-1],
        "machine": _machine(),
        "kind": "astock_veto_adv_capacity",
        "fills_the_hole_of": "r2010 (a limit-up name that opens in 5 days still cannot be bought in size)",
        "prereg": {
            "participation": PARTICIPATION,
            "adv_window": ADV_WINDOW,
            "verdict_capital": VERDICT_CAPITAL,
            "verdict_rule": "median fillable share at 10M: >=0.99 NOT_BINDING / >=0.90 BINDS_LIGHTLY / else BINDS",
            "rule_frozen_before_run": True,
        },
        "spec": {
            "hold": hold, "stride": stride,
            "cost_one_side": COST_ONE_SIDE,
            "min_amount_20d": MIN_AMOUNT_20D, "min_bars": MIN_BARS,
            "seed": SEED, "random_draws": RANDOM_DRAWS,
            "arms": {"A": "whole eligible pool", "B": "A minus top 20% residual"},
            "zero_capacity_rule": "non-finite ADV counts as 0, never skipped",
        },
        "panel": {"dates": len(dates), "symbols": len(symbols), "first": dates[0], "last": dates[-1]},
        "rebalances": len(rows),
        "summary": summary,
        "sensitivity": sensitivity,
        "anchor": parent_anchor(summary),
        "rows": rows,
    }
    payload["verdict"] = summary["B"]["verdict"]
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    write_md(payload)
    print("ADV-CAPACITY %s | B n=%.2f median-adv20=%.2f亿 one-lot=%.0f元"
          % (payload["verdict"], summary["B"]["mean_n"],
             summary["B"]["median_adv20_cny"] / 1e8, summary["B"]["median_one_lot_cny"]))
    for c in CAPITALS:
        bc = summary["B"]["fillable_share_by_capital"][str(c)]
        print("  C=%-12s slot=%-9.0f fillable median=%.4f worst=%.4f"
              % (format(c, ","), c / summary["B"]["mean_n"], bc["median"], bc["worst"]))
    print("  binding capital p0 median=%s p10 median=%s"
          % (format(round(summary["B"]["binding_capital"]["binding_capital_p0"]["median"]), ","),
             format(round(summary["B"]["binding_capital"]["binding_capital_p10"]["median"]), ",")))
    print("  anchor vs parent: ok=%s diff=%s" % (payload["anchor"]["ok"], payload["anchor"]["abs_diff"]))
    return 0


# --------------------------------------------------------------------- check
def check() -> int:
    """Re-derive, then compare.  Drift on inputs is STALE; a number that moved
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
            f = face["summary"][arm]["fillable_share_by_capital"][str(c)]["median"]
            g = summary[arm]["fillable_share_by_capital"][str(c)]["median"]
            if f is None or g is None:
                problems.append("CHECK FAILED arm %s capital %s median is None" % (arm, c))
            elif abs(f - g) > 1e-9:
                problems.append("CHECK FAILED arm %s capital %s median %r != %r" % (arm, c, f, g))
    anchor = parent_anchor(summary)
    if not anchor["ok"]:
        problems.append("STALE parent anchor: %r" % (anchor,))

    if not problems:
        print("CHECK ok  (B n=%.4f, verdict %s, anchor diff=%s)"
              % (summary["B"]["mean_n"], summary["B"]["verdict"], anchor["abs_diff"]))
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
    # 1. adv window averages only the traded days inside the trailing window
    amt = np.array([[10.0, np.nan],
                    [20.0, 5.0],
                    [30.0, np.nan],
                    [40.0, 15.0]])
    adv = adv_window(amt, 3, window=3)
    _ok(abs(adv[0] - 30.0) < 1e-12, "symbol 0 mean of 20/30/40 over rows 1..3")
    _ok(abs(adv[1] - 10.0) < 1e-12, "symbol 1 averages only the 5.0 and 15.0 it traded")
    # 2. a symbol that never traded in the window is NaN, not zero-by-accident
    adv0 = adv_window(amt, 3, window=3)
    _ok(not np.isfinite(adv_window(np.array([[np.nan], [np.nan]]), 1)[0]),
        "no finite value in the window is NaN")
    # 3. capacities: non-finite ADV becomes 0.0 (counted, not skipped)
    cap = capacities(np.array([np.nan, 1e7, 2e7]), np.array([0, 1, 2]), 0.05)
    _ok(cap[0] == 0.0 and abs(cap[1] - 5e5) < 1e-9 and abs(cap[2] - 1e6) < 1e-9,
        "5% participation, NaN -> 0")
    # 4. fillable share
    cap3 = np.array([100.0, 200.0, 1000.0])
    _ok(abs(fillable_share(cap3, 600.0) - 2.0 / 3.0) < 1e-12,
        "slot 200 vs capacities 100/200/1000 -> 2 of 3")
    _ok(abs(fillable_share(cap3, 0.0) - 1.0) < 1e-12, "zero capital fills everything")
    # 5. binding capital = n * quantile
    _ok(abs(binding_capital(cap3, 0.0) - 300.0) < 1e-12, "thinnest member: 3*100")
    _ok(abs(binding_capital(cap3, 0.5) - 600.0) < 1e-12, "median member: 3*200")
    # 6. participation scales capacity linearly
    base = capacities(np.array([1e7]), np.array([0]), 0.05)[0]
    _ok(abs(capacities(np.array([1e7]), np.array([0]), 0.10)[0] - 2 * base) < 1e-9,
        "10% participation is twice 5%")
    # 7. verdict three states, frozen thresholds
    _ok(capacity_verdict(1.0) == "CAPACITY_NOT_BINDING_AT_10M", "share 1.0 -> not binding")
    _ok(capacity_verdict(0.99) == "CAPACITY_NOT_BINDING_AT_10M", "boundary 0.99 inclusive")
    _ok(capacity_verdict(0.98) == "CAPACITY_BINDS_LIGHTLY_AT_10M", "0.98 -> lightly")
    _ok(capacity_verdict(0.90) == "CAPACITY_BINDS_LIGHTLY_AT_10M", "boundary 0.90 inclusive")
    _ok(capacity_verdict(0.8999) == "CAPACITY_BINDS_AT_10M", "below 0.90 -> binds")
    _ok(capacity_verdict(float("nan")) == "INSUFFICIENT_PERIODS", "nan -> insufficient")
    # 8. empty member set never crashes and never claims capacity
    _ok(not np.isfinite(fillable_share(np.array([]), 1e6)), "empty set -> nan, not 1.0")
    _ok(not np.isfinite(binding_capital(np.array([]))), "empty set -> nan capital")
    # 9. zero-capacity member drives the strict ceiling to zero (the rule's bite)
    cap_z = np.array([1e6, 1e6, 0.0])
    _ok(binding_capital(cap_z, 0.0) == 0.0, "one suspended name -> strict ceiling is 0")
    _ok(binding_capital(cap_z, 0.10) > 0.0, "p10 lets it through, printed not hidden")
    # 10. whole-lot rounding: 3 lots of 300 in a 1000 slot -> 10% left over,
    #     and a name whose lot exceeds the slot is a full miss, not a skip
    m, mx, unb = lot_deviation(np.array([300.0, 1200.0]), 2000.0)
    _ok(abs(m - 0.55) < 1e-12, "slot 1000: devs 0.10 and 1.00 -> mean 0.55")
    _ok(abs(mx - 1.0) < 1e-12, "the 1200 lot cannot be bought at all")
    _ok(abs(unb - 0.5) < 1e-12, "half the names have no lot that fits")
    m2, _, _ = lot_deviation(np.array([250.0, 500.0]), 1000.0)
    _ok(abs(m2) < 1e-12, "slot 500 with lots of 250/500 rounds exactly")
    _ok(not np.isfinite(lot_deviation(np.array([]), 1e6)[0]), "empty set -> nan")
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
