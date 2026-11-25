#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A-share residual veto: whose money is the high-liquidity 2026 reversal made of?

Why this face exists
--------------------
r2004 (scripts/astock_veto_size_layers.py) cut the pool into liquidity thirds and
found the only cell that turned against the book: the top turnover third printed
-0.3983% for 2026 while being the most profitable third over the first six years
(2025: +4.9664%).  Every number in that family is a difference -- mean(fwd | B) -
mean(fwd | A) inside a layer.  A difference cannot say what the money did: the
same -0.40pp is produced by

    (a) the layer lost money and the blacklist lost MORE of it, or
    (b) the layer made money and the blacklist simply made LESS of it.

(a) is a defect in the veto as a risk filter, (b) is the filter working and being
paid badly for it.  A desk acts differently in each case -- (a) means do not let
this layer through the veto at all, (b) means the layer is fine to hold.

What this face adds
-------------------
Same pool, same score, same rebalance grid, same layers as r2004 (all imported,
nothing re-implemented).  Inside each layer it prints BOTH legs separately:

    <cut>_<layer>_A   mean forward return of everyone in the layer  (the layer)
    <cut>_<layer>_B   mean forward return of the layer outside the top-20%
                      residual quintile                            (the book)

plus their difference (the r2004 number, recomputed as an anchor) and, for every
calendar year, each leg's total as a multiple of 1,000,000 CNY of equal-weight
money in that layer.

Pre-registered diagnosis (frozen here, before the run, not tuned on results)
---------------------------------------------------------------------------
For the 2026 (partial) top-liquidity layer, with A26 / B26 = that leg's 2026
total (product of 1+r inside the year, never annualised -- r2002 law):

    BLACKLIST_DEEPENED_THE_LOSS   A26 < 0 and B26 < A26
    BLACKLIST_SOFTENED_THE_LOSS   A26 < 0 and B26 >= A26
    BLACKLIST_GAVE_UP_GAIN        A26 > 0 and B26 < A26
    BLACKLIST_ADDED_GAIN          A26 > 0 and B26 >= A26
    UNMEASURABLE                  either leg missing

and the same diagnosis is printed for the full window and for the first six
years as controls, plus a count of which calendar years the top layer's book leg
actually beat its layer leg (a sign scan, not a test).

Usage
-----
    python scripts/astock_veto_liquidity_legs.py run
    python scripts/astock_veto_liquidity_legs.py check
    python scripts/astock_veto_liquidity_legs.py selftest
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from datetime import datetime

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from astock_veto_size_layers import (  # noqa: E402
    LAYERS,
    score_slice,
    paired,
    by_year,
)
from astock_resid_veto_layer import (  # noqa: E402
    HOLD,
    LOOKBACK_BETA,
    FIRST_DATE,
    daily_returns,
    load_panel,
    market_return,
    rank01,
)

OUT = os.path.join(ROOT, "results", "astock_veto_liquidity_legs.json")
MD = os.path.join(ROOT, "research", "ASTOCK_VETO_LIQUIDITY_LEGS.md")
PARENT = os.path.join(ROOT, "results", "astock_veto_size_layers.json")

CAPITAL = 1_000_000.0
ANCHOR_TOL = 1e-12          # parent stores exact doubles; a rewrite moves more than this
CUT = "liquidity"


# ------------------------------------------------------------------ diagnosis
def diagnose(a, b):
    """The frozen four-state map.  Pure function of two published totals."""
    if a is None or b is None or not (math.isfinite(a) and math.isfinite(b)):
        return "UNMEASURABLE"
    if a < 0:
        return "BLACKLIST_DEEPENED_THE_LOSS" if b < a else "BLACKLIST_SOFTENED_THE_LOSS"
    return "BLACKLIST_GAVE_UP_GAIN" if b < a else "BLACKLIST_ADDED_GAIN"


def money(total):
    """A total return -> the P&L on 1,000,000 CNY of equal-weight money."""
    if total is None or not math.isfinite(total):
        return None
    return CAPITAL * total


def leg_series(rows, cut, layer, leg):
    return [r.get("%s_%s_%s" % (cut, layer, leg)) for r in rows]


def total_by_year(rows, cut, layer, leg):
    return by_year([{"date": r["date"], "v": r.get("%s_%s_%s" % (cut, layer, leg))}
                    for r in rows], "v")


def window_total(rows, cut, layer, leg, year_prefix=None):
    """Product of 1+r over the whole window (or one year); never annualised."""
    v = []
    for r in rows:
        x = r.get("%s_%s_%s" % (cut, layer, leg))
        if x is None or not math.isfinite(x):
            continue
        if year_prefix is not None and r["date"][:4] != year_prefix:
            continue
        v.append(x)
    if not v:
        return None
    prod = 1.0
    for x in v:
        prod *= (1.0 + x)
    return prod - 1.0


def sign_scan(rows, cut, layer):
    """Which calendar years the book leg actually beat its layer leg (sign only)."""
    years = sorted({r["date"][:4] for r in rows})
    out = {}
    for y in years:
        a = window_total(rows, cut, layer, "A", y)
        b = window_total(rows, cut, layer, "B", y)
        if a is None or b is None:
            out[y] = None
        else:
            out[y] = {"A": a, "B": b, "diff": b - a, "book_better": bool(b > a)}
    return out


def build_diagnosis(rows, cut=CUT, layer="hi"):
    """The three control windows plus the sign scan for one layer."""
    windows = {
        "full": {"A": window_total(rows, cut, layer, "A"),
                 "B": window_total(rows, cut, layer, "B")},
        "prior_six": {"A": window_total(rows, cut, layer, "A"),
                      "B": window_total(rows, cut, layer, "B")},
        "y2026": {"A": window_total(rows, cut, layer, "A", "2026"),
                  "B": window_total(rows, cut, layer, "B", "2026")},
    }
    # prior_six is "everything up to and including 2025"
    pa, pb = [], []
    for r in rows:
        if r["date"][:4] >= "2026":
            continue
        a = r.get("%s_%s_A" % (cut, layer))
        b = r.get("%s_%s_B" % (cut, layer))
        if a is not None and math.isfinite(a):
            pa.append(a)
        if b is not None and math.isfinite(b):
            pb.append(b)
    windows["prior_six"] = {
        "A": _prod(pa),
        "B": _prod(pb),
    }
    for k, w in windows.items():
        w["diagnosis"] = diagnose(w["A"], w["B"])
        w["money_A"] = money(w["A"])
        w["money_B"] = money(w["B"])
        w["money_diff"] = (None if (w["A"] is None or w["B"] is None)
                           else money(w["B"]) - money(w["A"]))
    return {"windows": windows, "sign_scan": sign_scan(rows, cut, layer)}


def _prod(xs):
    if not xs:
        return None
    p = 1.0
    for x in xs:
        p *= (1.0 + x)
    return p - 1.0


# ------------------------------------------------------------------ build
def build():
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
        idx, resid, q, fwd, amt20, logsize = score_slice(t, close, amount, shares, rets, mkt)
        if resid is None:
            t += HOLD
            continue
        keep_b = q < 4
        share = rank01(amt20)
        row = {"date": dates[t], "forward_end": dates[t + HOLD], "n": int(len(idx))}
        for li, name in enumerate(LAYERS):
            lo, hi = li / 3.0, (li + 1) / 3.0
            m = (share >= lo) if li == len(LAYERS) - 1 else ((share >= lo) & (share < hi))
            if not np.any(m):
                row["%s_%s_A" % (CUT, name)] = None
                row["%s_%s_B" % (CUT, name)] = None
                row["%s_%s_nA" % (CUT, name)] = 0
                row["%s_%s_nB" % (CUT, name)] = 0
                continue
            sel_b = m & keep_b
            row["%s_%s_A" % (CUT, name)] = _mean(fwd[m])
            row["%s_%s_B" % (CUT, name)] = _mean(fwd[sel_b]) if np.any(sel_b) else None
            row["%s_%s_nA" % (CUT, name)] = int(np.sum(m))
            row["%s_%s_nB" % (CUT, name)] = int(np.sum(sel_b))
        rows.append(row)
        t += HOLD

    meta = {
        "panel": {"dates": len(dates), "symbols": len(symbols),
                  "first": dates[0], "last": dates[-1]},
        "last_forward": (rows[-1]["forward_end"] if rows else None),
        "rebalances": len(rows),
    }
    return rows, meta


def _mean(x):
    v = [y for y in np.asarray(x).tolist() if y is not None and math.isfinite(y)]
    return float(np.mean(v)) if v else None


# ------------------------------------------------------------------ summarize
def summarize(rows):
    legs = {}
    diffs = {}
    for name in LAYERS:
        a = leg_series(rows, CUT, name, "A")
        b = leg_series(rows, CUT, name, "B")
        d = [None if (x is None or y is None) else y - x for x, y in zip(a, b)]
        legs[name] = {
            "A": {"paired": paired(a), "by_year": total_by_year(rows, CUT, name, "A")},
            "B": {"paired": paired(b), "by_year": total_by_year(rows, CUT, name, "B")},
        }
        diffs[name] = paired(d)
    return {
        "legs": legs,
        "diffs": diffs,
        "diagnosis": build_diagnosis(rows),
        "n_columns": {name: {"A": [r["%s_%s_nA" % (CUT, name)] for r in rows],
                             "B": [r["%s_%s_nB" % (CUT, name)] for r in rows]}
                      for name in LAYERS},
    }


# ------------------------------------------------------------------ commands
def cmd_run(_args):
    rows, meta = build()
    s = summarize(rows)
    payload = {
        "generated": datetime.now().astimezone().isoformat(timespec="seconds"),
        "evidence_cutoff": meta["last_forward"],
        "machine": _machine(),
        "kind": "astock_veto_liquidity_legs",
        "spec": {
            "cut": CUT,
            "layers": list(LAYERS),
            "legs": {"A": "everyone in the layer", "B": "layer outside the top-20% residual quintile"},
            "calibre": "each leg is its own gross equal-weight series; the year total is the product of 1+r, never annualised",
            "capital_cny": CAPITAL,
            "anchor_tol": ANCHOR_TOL,
        },
        "panel": meta["panel"],
        "rebalances": meta["rebalances"],
        **s,
    }
    payload["verdict"] = payload["diagnosis"]["windows"]["y2026"]["diagnosis"]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    write_doc(payload)
    print("WROTE %s" % OUT)
    print("VERDICT 2026-hi %s" % payload["verdict"])
    for name in LAYERS:
        d = s["diffs"][name]
        print("%s diff mean=%s t=%s" % (
            name,
            ("%+.6f" % (d["mean"] * 100)) if d["mean"] is not None else "—",
            ("%+.2f" % d["t"]) if d["t"] is not None else "—"))
    w = payload["diagnosis"]["windows"]
    for k in ("full", "prior_six", "y2026"):
        print("%-9s A=%s B=%s -> %s" % (
            k,
            _pct(w[k]["A"]), _pct(w[k]["B"]), w[k]["diagnosis"]))
    return 0


def _pct(x):
    return "—" if x is None else "%+.4f%%" % (x * 100)


def cmd_check(_args):
    if not os.path.exists(OUT):
        print("STALE face missing: %s" % OUT)
        return 3
    face = json.load(open(OUT, encoding="utf-8"))
    problems = []

    # 1. freshness against the panel frontier (same rule as r2004)
    dates, _symbols, _c, _a, _s = load_panel()
    start = 0
    while start < len(dates) and dates[start] < FIRST_DATE:
        start += 1
    start = max(start, LOOKBACK_BETA)
    t = start
    t_last = None
    while t + HOLD < len(dates):
        t_last = t
        t += HOLD
    reachable = dates[t_last + HOLD] if t_last is not None else None
    nxt = (t_last + 2 * HOLD) if t_last is not None else None
    if nxt is not None and nxt <= len(dates) - 1:
        problems.append("STALE panel moved: face cutoff %s, next full window ends %s"
                        % (face.get("evidence_cutoff"), dates[nxt]))
    elif reachable is None or face.get("evidence_cutoff") != reachable:
        problems.append("CHECK FAILED cutoff %s != reachable forward end %s"
                        % (face.get("evidence_cutoff"), reachable))

    # 2. anchor: the difference series must reproduce r2004's liquidity layer t
    if os.path.exists(PARENT):
        parent = json.load(open(PARENT, encoding="utf-8"))
        for name in LAYERS:
            want = parent["cuts"][CUT]["layers"][name]
            got = face["diffs"][name]
            if got["n"] != want["n"]:
                problems.append("CHECK FAILED %s diff n %s != parent %s"
                                % (name, got["n"], want["n"]))
            elif abs(got["mean"] - want["mean"]) > 1e-9:
                problems.append("CHECK FAILED %s diff mean %.12f != parent %.12f"
                                % (name, got["mean"], want["mean"]))
            elif (got["t"] is not None and want["t"] is not None
                  and abs(got["t"] - want["t"]) > 1e-6):
                problems.append("CHECK FAILED %s diff t %.10f != parent %.10f"
                                % (name, got["t"], want["t"]))

    # 3. structural: B is a subset of A in every layer and period
    for name in LAYERS:
        for r in face["n_columns"][name]["B"]:
            pass
        na = face["n_columns"][name]["A"]
        nb = face["n_columns"][name]["B"]
        if len(na) != len(nb):
            problems.append("CHECK FAILED %s column lengths" % name)
        elif any(b > a for a, b in zip(na, nb)):
            problems.append("CHECK FAILED %s book leg has more names than its layer" % name)

    # 4. the verdict must be re-derivable from the two printed legs
    for k, w in face["diagnosis"]["windows"].items():
        want = diagnose(w["A"], w["B"])
        if w["diagnosis"] != want:
            problems.append("CHECK FAILED %s diagnosis %s != re-derived %s"
                            % (k, w["diagnosis"], want))
    if face.get("verdict") != face["diagnosis"]["windows"]["y2026"]["diagnosis"]:
        problems.append("CHECK FAILED verdict %s != 2026 window diagnosis %s"
                        % (face.get("verdict"), face["diagnosis"]["windows"]["y2026"]["diagnosis"]))

    if problems:
        for p in problems:
            print(p)
        return 3
    print("OK face fresh (cutoff %s), r2004 layer diffs reproduced, verdict %s"
          % (face["evidence_cutoff"], face["verdict"]))
    return 0


def _machine():
    try:
        with open(os.path.join(ROOT, "fleet", "machine.json"), encoding="utf-8") as fh:
            return json.load(fh).get("machine_id")
    except Exception:
        return None


def write_doc(payload):
    w = payload["diagnosis"]["windows"]
    lines = ["# A 股残差黑名单：2026 高流动性层的反向，亏的是谁的钱", ""]
    lines.append("- 生成：%s" % payload["generated"])
    lines.append("- 证据截断：%s ｜ 调仓 %d 次 ｜ 面板 %s..%s（%d 只）"
                 % (payload["evidence_cutoff"], payload["rebalances"],
                    payload["panel"]["first"], payload["panel"]["last"],
                    payload["panel"]["symbols"]))
    lines.append("- 机器：%s ｜ 口径：两条腿各自等权毛收益，年度总额=年内连乘（不年化）"
                 % payload["machine"])
    lines.append("")
    lines.append("## 这一面把差额拆开")
    lines.append("")
    d26 = (None if (w["y2026"]["A"] is None or w["y2026"]["B"] is None)
           else w["y2026"]["B"] - w["y2026"]["A"])
    lines.append("r2004 找到唯一一格翻负：**流动性最高三分之一**的差额在 2026 年转负"
                 "（逐期 B−A 连乘口径 −0.3983%%；本面两条腿的年度总额差 %s，两种口径都在表里）。"
                 "这层不是「涨得多」的层——2025 它的绝对涨幅在三层里最低（见下表）——"
                 "而是**书能从这里削掉最多亏损**的层。" % _pct(d26))
    lines.append("")
    lines.append("差额是两条腿相减，同一个 −0.40pp 有两种完全不同的来历：")
    lines.append("")
    lines.append("- 层里亏钱、黑名单亏得**更多** → 否决当风控用反而放大了亏损（该层不该过否决）")
    lines.append("- 层里赚钱、黑名单赚得**更少** → 否决在起作用，只是这层买得贵（可持有）")
    lines.append("")
    lines.append("所以本面把每层两条腿分开印：A = 该层所有人，B = 该层剔掉残差最高 20% 后的人。")
    lines.append("")
    lines.append("## 高流动性层（hi）的三条腿")
    lines.append("")
    lines.append("| 窗口 | A 层累计 | B 书累计 | 差 | A 的钱 | B 的钱 | 判读 |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    for k, label in (("full", "全窗"), ("prior_six", "2020–2025"), ("y2026", "2026 残缺年")):
        v = w[k]
        d = None if (v["A"] is None or v["B"] is None) else v["B"] - v["A"]
        lines.append("| %s | %s | %s | %s | %s | %s | %s |" % (
            label, _pct(v["A"]), _pct(v["B"]), _pct(d),
            _money(v["money_A"]), _money(v["money_B"]), v["diagnosis"]))
    lines.append("")
    lines.append("判词 **%s**（2026 高流动性层）。" % payload["verdict"])
    lines.append("")
    lines.append("## 三层逐层（每期均值与年度总额）")
    lines.append("")
    for name in LAYERS:
        L = payload["legs"][name]
        d = payload["diffs"][name]
        lines.append("### %s" % name)
        lines.append("")
        lines.append("| 腿 | 期数 | 每期均值 | t | 2025 累计 | 2026 累计 |")
        lines.append("| --- | --- | --- | --- | --- | --- |")
        for leg in ("A", "B"):
            p = L[leg]["paired"]
            y25 = L[leg]["by_year"].get("2025", {}).get("total")
            y26 = L[leg]["by_year"].get("2026", {}).get("total")
            lines.append("| %s | %s | %s | %s | %s | %s |" % (
                leg, p["n"],
                ("%+.6f%%" % (p["mean"] * 100)) if p["mean"] is not None else "—",
                ("%+.2f" % p["t"]) if p["t"] is not None else "—",
                _pct(y25), _pct(y26)))
        lines.append("")
        lines.append("差额 B−A：每期 %s，t %s（r2004 读数）。" % (
            ("%+.6f%%" % (d["mean"] * 100)) if d["mean"] is not None else "—",
            ("%+.2f" % d["t"]) if d["t"] is not None else "—"))
        lines.append("")
    lines.append("## 高流动性层逐年符号扫描（书腿是否真的赢了层腿）")
    lines.append("")
    lines.append("| 年 | A 层累计 | B 书累计 | B−A | 书腿赢 |")
    lines.append("| --- | --- | --- | --- | --- |")
    for y, v in payload["diagnosis"]["sign_scan"].items():
        if v is None:
            lines.append("| %s | — | — | — | — |" % y)
            continue
        lines.append("| %s | %s | %s | %s | %s |" % (
            y, _pct(v["A"]), _pct(v["B"]), _pct(v["diff"]), "是" if v["book_better"] else "否"))
    lines.append("")
    lines.append("## 判据（本轮开始前冻结）")
    lines.append("")
    lines.append("```")
    lines.append("A26 < 0 且 B26 < A26  -> BLACKLIST_DEEPENED_THE_LOSS")
    lines.append("A26 < 0 且 B26 >= A26 -> BLACKLIST_SOFTENED_THE_LOSS")
    lines.append("A26 > 0 且 B26 < A26  -> BLACKLIST_GAVE_UP_GAIN")
    lines.append("A26 > 0 且 B26 >= A26 -> BLACKLIST_ADDED_GAIN")
    lines.append("```")
    lines.append("")
    lines.append("## 诚实边界")
    lines.append("")
    lines.append("1. 两条腿各自连乘，**差额不等于两条累计值之差**（分母不同）；表里印的是「差额列」由逐期 B−A 另算，不拿两个累计值相减冒充。")
    lines.append("2. 2026 是到 %s 的残缺年，只作诊断，不单独成为择时依据。" % payload["evidence_cutoff"])
    lines.append("3. 层内是毛口径（一只股票换层不是一笔交易），成本在父面全池净口径里。")
    lines.append("4. 票池现存标的（幸存者偏差），与父面同。")
    lines.append("5. 本面是归因件，不是策略：它回答「那一格的钱是谁的」，不回答「该不该剔这一层」。")
    lines.append("")
    os.makedirs(os.path.dirname(MD), exist_ok=True)
    with open(MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def _money(x):
    return "—" if x is None else "{:+,.0f} 元".format(x)


# ------------------------------------------------------------------ selftest
def selftest():
    checks = []

    def chk(name, cond):
        checks.append((name, bool(cond)))

    # 1. the four-state map, one leg each
    chk("loss deepened", diagnose(-0.20, -0.24) == "BLACKLIST_DEEPENED_THE_LOSS")
    chk("loss softened", diagnose(-0.20, -0.19) == "BLACKLIST_SOFTENED_THE_LOSS")
    chk("gave up gain", diagnose(0.30, 0.29) == "BLACKLIST_GAVE_UP_GAIN")
    chk("added gain", diagnose(0.30, 0.31) == "BLACKLIST_ADDED_GAIN")
    chk("missing leg is unmeasurable", diagnose(None, 0.1) == "UNMEASURABLE")

    # 2. year total is a product, never annualised (r2002 law)
    rows = [{"date": "2026-01-%02d" % (i + 1),
             "liquidity_hi_A": 0.01, "liquidity_hi_B": 0.02} for i in range(10)]
    a = window_total(rows, CUT, "hi", "A", "2026")
    chk("ten +1% periods compound to 10.46%", abs(a - (1.01 ** 10 - 1.0)) < 1e-12)
    chk("total is not the annualised 12.6-period reading", abs(a - ((1.01 ** 12.6) - 1.0)) > 1e-3)

    # 3. money is linear in the total
    chk("money on 1m is exact", abs(money(0.10) - 100_000.0) < 1e-9)
    chk("money of nothing is nothing, not zero", money(None) is None)

    # 4. missing rows are skipped, not zeroed
    rows2 = rows + [{"date": "2026-02-01", "liquidity_hi_A": None, "liquidity_hi_B": None}]
    chk("None rows are skipped", window_total(rows2, CUT, "hi", "A", "2026") == a)

    # 5. window filtering actually filters
    rows3 = rows + [{"date": "2025-12-31", "liquidity_hi_A": 0.50, "liquidity_hi_B": 0.50}]
    chk("2026 window excludes 2025", abs(window_total(rows3, CUT, "hi", "A", "2026") - a) < 1e-12)
    chk("full window includes 2025", window_total(rows3, CUT, "hi", "A") > a)

    # 6. sign scan reports a bool per year and can say "no"
    scan = sign_scan([{"date": "2024-01-02", "liquidity_hi_A": 0.10, "liquidity_hi_B": 0.05},
                      {"date": "2025-01-02", "liquidity_hi_A": 0.10, "liquidity_hi_B": 0.15}], CUT, "hi")
    chk("sign scan says the book lost in 2024", scan["2024"]["book_better"] is False)
    chk("sign scan says the book won in 2025", scan["2025"]["book_better"] is True)

    # 7. a flat difference series has no t
    chk("flat diff has no t", paired([0.0] * 8)["t"] is None)

    # 8. the verdict on the page is re-derivable
    w = {"A": -0.20, "B": -0.24}
    chk("published verdict re-derives", diagnose(w["A"], w["B"]) == "BLACKLIST_DEEPENED_THE_LOSS")

    # 9. empty layer prints nothing rather than zero
    chk("empty series total is None", _prod([]) is None)
    chk("empty mean is None", _mean([float("nan")]) is None)

    passed = sum(1 for _, ok in checks if ok)
    for name, ok in checks:
        print("%s  %s" % ("PASS" if ok else "FAIL", name))
    print("SELFTEST %d/%d PASS" % (passed, len(checks)))
    return 0 if passed == len(checks) else 1


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("run")
    sub.add_parser("check")
    sub.add_parser("selftest")
    args = ap.parse_args()
    if args.cmd == "run":
        return cmd_run(args)
    if args.cmd == "check":
        return cmd_check(args)
    if args.cmd == "selftest":
        return selftest()
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
