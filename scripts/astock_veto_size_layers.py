#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A-share residual veto, cut into size and liquidity layers.

Why this face exists
--------------------
r2003 (scripts/astock_veto_year_source.py) split the 2026 loss of the veto book
into beta and alpha and left one question open: the cross-sectional B-A edge is
+0.2428%/rebalance over the whole window (t 3.46) and +0.2657% over the first
six years (t 3.94), but in 2026 it is +0.0893% (t 0.29).  Is that the leading
edge of decay, or is the edge simply concentrated in a part of the pool that
happened to do nothing this year?

A single pooled mean cannot answer that, because an edge that lives only in
small caps and an edge that has halved uniformly produce the same pooled number.

What this face adds
-------------------
Same eligible pool, same rebalance dates, same score as the parent face (all
imported, nothing re-implemented), cut into three equal-count layers by two
different variables that a desk actually sorts on:

    liquidity   20-day mean turnover (amount), ascending
    size        log market cap (close x outstanding_share), ascending

Inside each layer the same A/B pair is formed as the parent: A is everyone in
the layer, B is everyone in the layer outside the pool's top-20% residual
quintile.  The per-rebalance difference mean(fwd | layer & B) - mean(fwd | layer)
is then tracked as its own series.

Deliberately gross
------------------
Layer differences are reported GROSS.  Cost belongs to the whole-pool B arm
(a name changing layer between rebalances is not a trade), so charging a
layer-level turnover would invent a cost that no desk pays.  The net whole-pool
number is reproduced alongside as a cross-face anchor, and the two calibres are
never subtracted from each other.

Pre-registered verdicts (frozen here, not tuned on results)
-----------------------------------------------------------
For each of the two cuts, with t_hi/t_lo = paired t of the top/bottom layer:

    EDGE_CONCENTRATED_IN_<cut>_<layer>
        the top layer clears t>=2 while the bottom one does not, AND the
        hi-minus-lo paired difference itself clears t>=2 (a real slope, not
        one noisy cell)
    EDGE_UNIFORM_<cut>
        both the top and the bottom layer clear t>=2 (the edge is not a
        small-cap or a high-turnover artefact)
    EDGE_NOT_SEPARABLE_<cut>
        neither layer clears t>=2 (the pooled 3.46 is carried by the middle)
    EDGE_WEAK_<cut>
        exactly one layer clears t>=2 but the slope does not

and one 2026 diagnostic that never becomes a verdict on its own (the year is
10 periods to 2026-11-20, i.e. partial): the 2026 layer means are printed next
to the first-six-year means so a reader can see whether the collapse is
uniform or localised.

Usage
-----
    python scripts/astock_veto_size_layers.py run
    python scripts/astock_veto_size_layers.py check
    python scripts/astock_veto_size_layers.py selftest
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

from astock_resid_veto_layer import (  # noqa: E402
    HOLD,
    LOOKBACK_BETA,
    MIN_AMOUNT_20D,
    MIN_BARS,
    COST_ONE_SIDE,
    FIRST_DATE,
    _turnover,
    beta_window,
    cross_sectional_residual,
    daily_returns,
    load_panel,
    market_return,
    rank01,
)

OUT = os.path.join(ROOT, "results", "astock_veto_size_layers.json")
MD = os.path.join(ROOT, "research", "ASTOCK_VETO_SIZE_LAYERS.md")
PARENT = os.path.join(ROOT, "results", "astock_resid_veto_layer.json")
YEAR_SOURCE = os.path.join(ROOT, "results", "astock_veto_year_source.json")

CUTS = ("liquidity", "size")
LAYERS = ("lo", "mid", "hi")
T_EDGE = 2.0
T_SLOPE = 2.0
PARENT_ANCHOR_TOL = 1e-9   # parent stores 1e-16-scale doubles; anything coarser is a rewrite


# ------------------------------------------------------------------ primitives
def score_slice(t, close, amount, shares, rets, mkt):
    """Same score as the parent, plus the two layer variables it already computed.

    Returns (idx, resid, q, fwd, amt20, logsize) over the eligible slice, or
    (idx, None, None, None, None, None) when the slice is too thin.
    """
    c0 = close[t]
    c_past = close[t - HOLD]

    with np.errstate(invalid="ignore", divide="ignore"):
        r20 = c0 / c_past - 1.0
        f20 = close[t + HOLD] / c0 - 1.0

    amt_win = amount[max(0, t - HOLD + 1):t + 1]
    with np.errstate(invalid="ignore"):
        amt20 = np.nanmean(amt_win, axis=0)

    win = rets[t - LOOKBACK_BETA + 1:t + 1]
    nbars = np.sum(np.isfinite(win), axis=0)
    beta = beta_window(win, mkt[t - LOOKBACK_BETA + 1:t + 1])
    with np.errstate(invalid="ignore", divide="ignore"):
        logsize = np.log(c0 * shares[t])

    ok = (
        np.isfinite(r20)
        & np.isfinite(beta)
        & np.isfinite(logsize)
        & (nbars >= MIN_BARS)
        & (amt20 >= MIN_AMOUNT_20D)
        & np.isfinite(f20)
        & np.isfinite(amt20)
    )
    idx = np.nonzero(ok)[0]
    if len(idx) < 60:
        return idx, None, None, None, None, None
    resid = cross_sectional_residual(r20[idx], beta[idx], logsize[idx])
    q = np.clip((rank01(resid) * 5).astype(int), 0, 4)
    return idx, resid, q, f20[idx], amt20[idx], logsize[idx]


def paired(diffs):
    """Mean, standard error and t of a paired-difference series (finite only).

    A series that is constant to floating-point resolution has no estimable
    standard error; reporting mean/se there would turn a flat line into a
    gigantic t.  The spread is compared against the series' own scale so that
    a genuinely tiny-but-nonzero edge still reports its (small) t.
    """
    d = np.array([x for x in diffs if x is not None and math.isfinite(x)], dtype=np.float64)
    n = int(len(d))
    if n < 3:
        return {"n": n, "mean": None, "se": None, "t": None}
    mean = float(d.mean())
    se = float(d.std(ddof=1) / math.sqrt(n))
    scale = max(1.0, abs(mean))
    if se <= 1e-12 * scale:
        return {"n": n, "mean": mean, "se": 0.0, "t": None}
    return {"n": n, "mean": mean, "se": se, "t": mean / se}


def by_year(rows, key):
    """Period count and TOTAL per calendar year for one series key.

    Total is the product of (1+r) inside the year, never annualised: a year is
    a year, and r2002 measured what annualising a partial year costs.
    """
    acc = {}
    for r in rows:
        v = r.get(key)
        if v is None or not math.isfinite(v):
            continue
        acc.setdefault(r["date"][:4], []).append(v)
    out = {}
    for y, v in sorted(acc.items()):
        prod = 1.0
        for x in v:
            prod *= (1.0 + x)
        out[y] = {"periods": len(v), "total": prod - 1.0}
    return out


def mean_or_nan(xs):
    v = [x for x in xs if x is not None and math.isfinite(x)]
    return float(np.mean(v)) if v else None


# ------------------------------------------------------------------ build
def build(hold=HOLD):
    """Walk the panel once; return (rows, meta)."""
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
    while t + hold < len(dates):
        idx, resid, q, fwd, amt20, logsize = score_slice(t, close, amount, shares, rets, mkt)
        if resid is None:
            t += hold
            continue

        n = len(idx)
        keep_b = q < 4

        # whole-pool net, the parent's calibre -- this is the cross-face anchor
        cur_a = set(idx.tolist())
        cur_b = set(idx[keep_b].tolist())
        turb_a = _turnover(cur_a, prev["A"])
        turb_b = _turnover(cur_b, prev["B"])
        net_a = float(np.mean(fwd)) - 2.0 * COST_ONE_SIDE * turb_a
        net_b = float(np.mean(fwd[keep_b])) - 2.0 * COST_ONE_SIDE * turb_b
        prev["A"], prev["B"] = cur_a, cur_b

        row = {
            "date": dates[t],
            "forward_end": dates[t + hold],
            "n": int(n),
            "pool_net": {"A": net_a, "B": net_b, "diff": net_b - net_a},
        }

        # per-cut layers, gross only
        for cut, var in (("liquidity", amt20), ("size", logsize)):
            share = rank01(var)
            for li, name in enumerate(LAYERS):
                lo, hi = li / 3.0, (li + 1) / 3.0
                if li == len(LAYERS) - 1:
                    m = share >= lo
                else:
                    m = (share >= lo) & (share < hi)
                if not np.any(m):
                    row["%s_%s" % (cut, name)] = None
                    continue
                a_m = mean_or_nan(fwd[m].tolist())
                b_sel = m & keep_b
                b_m = mean_or_nan(fwd[b_sel].tolist()) if np.any(b_sel) else None
                row["%s_%s" % (cut, name)] = (
                    None if (a_m is None or b_m is None) else float(b_m - a_m)
                )

        rows.append(row)
        t += hold

    meta = {
        "panel": {
            "dates": len(dates),
            "symbols": len(symbols),
            "first": dates[0],
            "last": dates[-1],
        },
        # evidence cutoff is the last bar the FORWARD window reached, not the last
        # rebalance date: a 20-day hold means the last rebalance is 20 rows back.
        "last_forward": (rows[-1]["forward_end"] if rows else None),
        "rebalances": len(rows),
    }
    return rows, meta


# ------------------------------------------------------------------ verdicts
def verdict_from(cut, hi_t, lo_t, slope_mean, slope_t):
    """The frozen decision rule, as a pure function of four published numbers.

    run() and check() both call this, so the verdict on the page is by
    construction re-derivable from the layer table next to it.
    """
    hi_ok = hi_t is not None and hi_t >= T_EDGE
    lo_ok = lo_t is not None and lo_t >= T_EDGE
    slope_ok = slope_t is not None and slope_t >= T_SLOPE
    if hi_ok and lo_ok:
        return "EDGE_UNIFORM_%s" % cut.upper()
    if hi_ok and slope_ok:
        return "EDGE_CONCENTRATED_IN_%s_hi" % cut.upper()
    if lo_ok and slope_ok and slope_mean is not None and slope_mean < 0:
        return "EDGE_CONCENTRATED_IN_%s_lo" % cut.upper()
    if not hi_ok and not lo_ok:
        return "EDGE_NOT_SEPARABLE_%s" % cut.upper()
    return "EDGE_WEAK_%s" % cut.upper()


def cut_verdict(rows, cut, layer_t):
    """Pre-registered verdict for one cut.  layer_t: name -> paired dict."""
    diff_hi_lo = []
    for r in rows:
        a = r.get("%s_hi" % cut)
        b = r.get("%s_lo" % cut)
        diff_hi_lo.append(None if (a is None or b is None) else a - b)
    slope = paired(diff_hi_lo)
    v = verdict_from(cut, layer_t["hi"]["t"], layer_t["lo"]["t"],
                     slope["mean"], slope["t"])
    return v, slope


def summarize(rows):
    pool_diff = [r["pool_net"]["diff"] for r in rows]
    out = {
        "pool_net_anchor": {
            "paired": paired(pool_diff),
            "by_year": by_year(
                [{"date": r["date"], "v": r["pool_net"]["diff"]} for r in rows], "v"),
        },
        "cuts": {},
        "verdicts": {},
    }
    for cut in CUTS:
        layer_t = {}
        for name in LAYERS:
            key = "%s_%s" % (cut, name)
            series = [r.get(key) for r in rows]
            layer_t[name] = paired(series)
            layer_t[name]["by_year"] = by_year(
                [{"date": r["date"], "v": r.get(key)} for r in rows], "v")
        v, slope = cut_verdict(rows, cut, layer_t)
        out["cuts"][cut] = {"layers": layer_t, "hi_minus_lo": slope}
        out["verdicts"][cut] = v
    return out


# ------------------------------------------------------------------ commands
def cmd_run(_args):
    rows, meta = build()
    summary = summarize(rows)
    payload = {
        "generated": datetime.now().astimezone().isoformat(timespec="seconds"),
        "evidence_cutoff": meta["last_forward"],
        "machine": _machine(),
        "kind": "astock_veto_size_layers",
        "spec": {
            "hold": HOLD,
            "layers": list(LAYERS),
            "cut_variables": {
                "liquidity": "20-day mean amount (turnover), rank percentile",
                "size": "log(close * outstanding_share), rank percentile",
            },
            "calibre": "layer differences are GROSS; the whole-pool net is the parent calibre",
            "t_edge": T_EDGE,
            "t_slope": T_SLOPE,
        },
        "panel": meta["panel"],
        "rebalances": meta["rebalances"],
        **summary,
    }
    payload["verdict"] = " | ".join(
        "%s=%s" % (k, v) for k, v in payload["verdicts"].items())
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    write_doc(payload)
    print("WROTE %s" % OUT)
    print("VERDICT %s" % payload["verdict"])
    anchor = payload["pool_net_anchor"]["paired"]
    print("ANCHOR pool net B-A: n=%s mean=%.10f t=%.4f"
          % (anchor["n"], anchor["mean"], anchor["t"]))
    for cut in CUTS:
        lt = payload["cuts"][cut]["layers"]
        print("%-9s lo mean=%+.6f t=%+.2f | mid %+.6f %+.2f | hi %+.6f %+.2f | hi-lo %+.6f t=%+.2f"
              % (cut,
                 lt["lo"]["mean"] or float("nan"), lt["lo"]["t"] or float("nan"),
                 lt["mid"]["mean"] or float("nan"), lt["mid"]["t"] or float("nan"),
                 lt["hi"]["mean"] or float("nan"), lt["hi"]["t"] or float("nan"),
                 payload["cuts"][cut]["hi_minus_lo"]["mean"] or float("nan"),
                 payload["cuts"][cut]["hi_minus_lo"]["t"] or float("nan")))
    return 0


def cmd_check(_args):
    """Freshness + parent-anchor check.  STALE when the panel has moved on."""
    if not os.path.exists(OUT):
        print("STALE face missing: %s" % OUT)
        return 3
    face = json.load(open(OUT, encoding="utf-8"))
    parent = json.load(open(PARENT, encoding="utf-8"))
    problems = []

    # 1. panel frontier: the published cutoff is the last forward end the
    #    rebalance grid can reach.  A few extra bars do not make it stale --
    #    only a full extra HOLD-row window does, because that is the first
    #    moment a new rebalance date exists.
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
    next_forward_end = (t_last + 2 * HOLD) if t_last is not None else None
    stale = next_forward_end is not None and next_forward_end <= len(dates) - 1
    if stale:
        problems.append("STALE panel moved: face cutoff %s, next full window ends %s"
                        % (face.get("evidence_cutoff"), dates[next_forward_end]))
    elif reachable is None or face.get("evidence_cutoff") != reachable:
        problems.append("CHECK FAILED cutoff %s != reachable forward end %s"
                        % (face.get("evidence_cutoff"), reachable))

    # 2. parent anchor: whole-pool B-A must reproduce the parent's net pair
    want = parent["paired_per_rebalance"]["vs_A"]
    got = face["pool_net_anchor"]["paired"]
    if got["n"] != want["n"]:
        problems.append("CHECK FAILED anchor n: %s vs parent %s" % (got["n"], want["n"]))
    elif abs(got["mean"] - want["mean"]) > PARENT_ANCHOR_TOL:
        problems.append("CHECK FAILED anchor mean: %.12f vs parent %.12f"
                        % (got["mean"], want["mean"]))
    if (got["t"] is not None and want["t"] is not None
            and abs(got["t"] - want["t"]) > 1e-6):
        problems.append("CHECK FAILED anchor t: %.10f vs parent %.10f"
                        % (got["t"], want["t"]))

    # 3. layer shape: three layers per cut, and they cannot all be the same number
    for cut in CUTS:
        layers = face.get("cuts", {}).get(cut, {}).get("layers", {})
        if sorted(layers) != sorted(LAYERS):
            problems.append("CHECK FAILED %s layers: %s" % (cut, sorted(layers)))
            continue
        means = [layers[n]["mean"] for n in LAYERS]
        if all(m is not None for m in means) and len(set(round(m, 12) for m in means)) == 1:
            problems.append("CHECK FAILED %s layers identical (cut did nothing)" % cut)
        for n in LAYERS:
            if layers[n]["n"] != face["rebalances"]:
                problems.append("CHECK FAILED %s_%s periods %s != rebalances %s"
                                % (cut, n, layers[n]["n"], face["rebalances"]))
        # 4. the verdict must be re-derivable from the table next to it
        want_v = face.get("verdicts", {}).get(cut)
        slope = face.get("cuts", {}).get(cut, {}).get("hi_minus_lo", {})
        got_v = verdict_from(cut, layers["hi"]["t"], layers["lo"]["t"],
                             slope.get("mean"), slope.get("t"))
        if want_v != got_v:
            problems.append("CHECK FAILED %s verdict %s != re-derived %s"
                            % (cut, want_v, got_v))
    if problems:
        for p in problems:
            print(p)
        return 3
    print("OK face fresh (cutoff %s), parent anchor reproduced (n=%s mean=%.10f t=%.4f)"
          % (face["evidence_cutoff"], got["n"], got["mean"], got["t"]))
    return 0


def _machine():
    try:
        with open(os.path.join(ROOT, "fleet", "machine.json"), encoding="utf-8") as fh:
            return json.load(fh).get("machine_id")
    except Exception:
        return None


def write_doc(payload):
    anchor = payload["pool_net_anchor"]["paired"]
    lines = []
    lines.append("# A 股残差黑名单：这条边是均匀的，还是只长在池子某一头")
    lines.append("")
    lines.append("- 生成：%s" % payload["generated"])
    lines.append("- 证据截断：%s ｜ 调仓 %d 次 ｜ 面板 %s..%s（%d 只）"
                 % (payload["evidence_cutoff"], payload["rebalances"],
                    payload["panel"]["first"], payload["panel"]["last"],
                    payload["panel"]["symbols"]))
    lines.append("- 机器：%s" % payload["machine"])
    lines.append("")
    lines.append("## 这一面回答什么")
    lines.append("")
    try:
        _p = json.load(open(YEAR_SOURCE, encoding="utf-8"))["sort_pairs"]
        full_ba = _p["full_BA"]
        prior_ba = _p["prior_BA"]
        year_ba = _p["year_BA"]
        asked = ("全池 B-A 全窗 %+.4f%%/期（t %.2f），前六年 %+.4f%%（t %.2f），"
                 "2026 只有 %+.4f%%（t %.2f）"
                 % (full_ba["mean"] * 100, full_ba["t"],
                    prior_ba["mean"] * 100, prior_ba["t"],
                    year_ba["mean"] * 100, year_ba["t"]))
    except Exception:
        asked = "全池 B-A 的排序口径（父面读数不可得，本页不编数）"
    lines.append("r2003 把 2026 的亏损拆成了 beta 与 alpha，留下一个没答的问题："
                 + asked + "。")
    lines.append("")
    lines.append("单一个全池均值回答不了这个问题：**「只在小盘股里有效」和「均匀变弱一半」会印出同一个数**。")
    lines.append("所以本轮把同一个池、同一个分数、同一批调仓日，按两个台面上真的会用来排序的变量各切三等分：")
    lines.append("")
    lines.append("| 切法 | 变量 | 口径 |")
    lines.append("| --- | --- | --- |")
    lines.append("| liquidity | 20 日均成交额（百分位秩） | 层内配对差，**毛** |")
    lines.append("| size | log(收盘价 × 流通股本)（百分位秩） | 层内配对差，**毛** |")
    lines.append("")
    lines.append("层内差是毛口径：成本属于整个 B 臂（一只股票换层不是一笔交易），在层里收一层换手费等于"
                 "凭空造一笔没人付的钱。全池净口径单独印在下面做跨面锚，两个口径不相减。")
    lines.append("")
    lines.append("## 全池净口径（跨面锚，应逐位复现父面 r1862）")
    lines.append("")
    lines.append("| 项 | 值 |")
    lines.append("| --- | --- |")
    lines.append("| 期数 | %s |" % anchor["n"])
    lines.append("| 每期 B-A | %+.6f%% |" % (anchor["mean"] * 100))
    lines.append("| 标准误 | %.6f%% |" % (anchor["se"] * 100))
    lines.append("| t | %.4f |" % anchor["t"])
    lines.append("")
    lines.append("## 分层读数（每期 B-A 的层内均值，毛）")
    lines.append("")
    for cut in CUTS:
        lt = payload["cuts"][cut]["layers"]
        slope = payload["cuts"][cut]["hi_minus_lo"]
        lines.append("### %s" % cut)
        lines.append("")
        lines.append("| 层 | 期数 | 每期 B-A | t | 2026 累计 | 2025 累计 |")
        lines.append("| --- | --- | --- | --- | --- | --- |")
        for name in LAYERS:
            c = lt[name]
            y26 = c["by_year"].get("2026", {}).get("total")
            y25 = c["by_year"].get("2025", {}).get("total")
            lines.append("| %s | %s | %s | %s | %s | %s |" % (
                name, c["n"],
                ("%+.6f%%" % (c["mean"] * 100)) if c["mean"] is not None else "—",
                ("%+.2f" % c["t"]) if c["t"] is not None else "—",
                ("%+.4f%%" % (y26 * 100)) if y26 is not None else "—",
                ("%+.4f%%" % (y25 * 100)) if y25 is not None else "—"))
        lines.append("")
        lines.append("最高层减最低层：%s%%，t %s ｜ 判词 **%s**" % (
            ("%+.6f" % (slope["mean"] * 100)) if slope["mean"] is not None else "—",
            ("%+.2f" % slope["t"]) if slope["t"] is not None else "—",
            payload["verdicts"][cut]))
        lines.append("")
    lines.append("## 判词")
    lines.append("")
    lines.append("```")
    for k, v in payload["verdicts"].items():
        lines.append("%s = %s" % (k, v))
    lines.append("```")
    lines.append("")
    lines.append("判据（本轮开始前冻结）：")
    lines.append("")
    lines.append("- 最高层与最低层 t 都 ≥ %.1f → EDGE_UNIFORM（不是小盘/高换手的假象）" % T_EDGE)
    lines.append("- 只有最高层过 %.1f 且 hi-lo 斜率 t ≥ %.1f → EDGE_CONCENTRATED_IN_*_hi"
                 % (T_EDGE, T_SLOPE))
    lines.append("- 只有最低层过且斜率为负 → EDGE_CONCENTRATED_IN_*_lo")
    lines.append("- 两层都不过 → EDGE_NOT_SEPARABLE（全池 3.46 由中间层扛）")
    lines.append("- 其余 → EDGE_WEAK")
    lines.append("")
    lines.append("## 诚实边界")
    lines.append("")
    lines.append("1. 三层是同一个池的子集，**不能相加**成全池数；全池数只认上面的净口径锚。")
    lines.append("2. 层内是毛口径，没有计换层成本；一只股票从 lo 跳到 hi 在真实账本里不是交易。")
    lines.append("3. 2026 只有到 %s 的残缺年，2026 的层均值只作诊断，不单独成为判词。"
                 % payload["evidence_cutoff"])
    lines.append("4. 流通股本用的是面板的 outstanding_share；停牌/送转造成的股本跳变未单独清洗。")
    lines.append("5. 票池是现存标的（幸存者偏差），与父面同。")
    lines.append("6. 本面是归因件，不是可交易策略：它回答「边在哪一层」，不回答「该买哪只」。")
    lines.append("")
    os.makedirs(os.path.dirname(MD), exist_ok=True)
    with open(MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


# ------------------------------------------------------------------ selftest
def selftest():
    """Behavioural legs.  Each one must be able to go red."""
    checks = []

    def chk(name, cond):
        checks.append((name, bool(cond)))

    # 1. pooled series: a constant edge must give a finite t and the right mean
    rows = [{"date": "2020-01-%02d" % (i + 1), "pool_net": {"A": 0.0, "B": 0.0, "diff": 0.01 + 0.001 * (i % 3)},
             "liquidity_lo": 0.01, "liquidity_mid": 0.02, "liquidity_hi": 0.03,
             "size_lo": 0.03, "size_mid": 0.02, "size_hi": 0.01} for i in range(20)]
    p = paired([r["pool_net"]["diff"] for r in rows])
    chk("paired mean is the arithmetic mean", abs(p["mean"] - np.mean([r["pool_net"]["diff"] for r in rows])) < 1e-15)
    chk("paired t is mean/se", p["t"] is not None and abs(p["t"] - p["mean"] / p["se"]) < 1e-12)

    # 2. a flat series has no t (never invents significance)
    flat = paired([0.01] * 10)
    chk("flat series has no t", flat["t"] is None)

    # 3. fewer than 3 periods gives no t
    chk("two periods give no t", paired([0.01, 0.02])["t"] is None)

    # 4. EDGE_UNIFORM when both extremes clear
    lt = {"lo": {"t": 2.5, "mean": 0.01, "n": 20, "se": 0.004, "by_year": {}},
          "mid": {"t": 3.0, "mean": 0.02, "n": 20, "se": 0.006, "by_year": {}},
          "hi": {"t": 4.0, "mean": 0.03, "n": 20, "se": 0.007, "by_year": {}}}
    # constant hi-lo -> zero variance -> t None -> not "concentrated"
    v, _ = cut_verdict([{"date": "2020-01-01", "liquidity_hi": 0.03, "liquidity_lo": 0.01}] * 5, "liquidity",
                        {"lo": lt["lo"], "mid": lt["mid"], "hi": lt["hi"]})
    chk("uniform verdict when both layers clear", v == "EDGE_UNIFORM_LIQUIDITY")

    # 5. EDGE_NOT_SEPARABLE when neither clears
    v, _ = cut_verdict([{"date": "2020-01-01", "size_hi": 0.001, "size_lo": 0.0}] * 5, "size",
                        {"lo": {"t": 0.4}, "mid": {"t": 1.0}, "hi": {"t": 0.9}})
    chk("not separable when neither layer clears", v == "EDGE_NOT_SEPARABLE_SIZE")

    # 6. EDGE_WEAK when exactly one clears but slope does not
    v, _ = cut_verdict([{"date": "2020-01-01", "size_hi": 0.001, "size_lo": 0.0}] * 5, "size",
                        {"lo": {"t": 0.4}, "mid": {"t": 1.0}, "hi": {"t": 2.5}})
    chk("weak when one layer clears but slope flat", v == "EDGE_WEAK_SIZE")

    # 7. by_year groups and compounds correctly: two +1% periods -> 2.01%
    y = by_year([{"date": "2024-06-01", "v": 0.01}, {"date": "2024-07-01", "v": 0.01}], "v")
    chk("by_year totals within the year", abs(y["2024"]["total"] - (1.01 ** 2 - 1.0)) < 1e-15)
    chk("by_year counts periods", y["2024"]["periods"] == 2)

    # 8. None values are skipped, not treated as zero
    p2 = paired([0.01, None, float("nan"), 0.01])
    chk("None/NaN dropped, not zeroed", p2["n"] == 2)

    # 9. mean_or_nan on empty is None, never 0
    chk("empty mean is None", mean_or_nan([]) is None)

    # 10. hi-minus-lo sign: a real slope must be positive here
    rows2 = [{"date": "2020-01-%02d" % (i + 1), "size_hi": 0.03 + 0.001 * i,
              "size_lo": 0.01 + 0.0005 * i} for i in range(20)]
    slopes = [r["size_hi"] - r["size_lo"] for r in rows2]
    chk("hi-minus-lo mean is positive for a rising ladder", paired(slopes)["mean"] > 0)

    # 11. anchor tolerance is tight enough to catch a rewrite
    chk("anchor tolerance is 1e-9", PARENT_ANCHOR_TOL == 1e-9)

    # 12. layer constants are the three names the verdicts reference
    chk("three layers", LAYERS == ("lo", "mid", "hi"))

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
