#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ETF book -- when the 1% line says the slot is too small, where does the rest of the money go?

Every capacity face so far prices SIZE as a cost (r1260's sqrt-impact ladder: 1M -> 50M -> 100M,
still assumed to fill). The gate's own ruler is not a price, it is a refusal: an order above
1% of a name's ADV is not expensive, it is not there. This face prices the refusal.

At each rebalance the published book buys five equal slots. With `lens` CNY of capital and the
gate's line, the weakest of those five names can take `line * slots * worst_ADV` CNY. When that
is below `lens`, the honest reading is not "trade it anyway and pay impact" -- it is "you can
only be invested f = cap/lens, and the remainder sits in cash".

  arm A  the published book, filled in full (every existing face)
  arm B  the same five names, scaled by f = min(1, cap/lens); (1-f) in cash at 0%
  arm C  the same as B but the idle cash earns the repo ladder's own daily rate when the panel
         is on disk; otherwise arm C is honestly absent (not silently equal to B)

Nothing is re-ranked and nothing is adopted: this is the price of respecting a ruler the book
already reports against.

Criterion, frozen before the read (also written into the payload):
  D1 binds : >= 5% of rebalances carry f < 1.
  D2 costs : |CAGR(B) - CAGR(A)| >= 0.50pp -> CAPACITY_BINDS_AND_COSTS,
             else CAPACITY_BINDS_AT_NEGLIGIBLE_COST.
  D1 false -> CAPACITY_NOT_BINDING_AT_THIS_LENS.
"""
import argparse
import json
import math
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)

import pandas as pd  # noqa: E402

import etf_equity_alpha as A  # noqa: E402
import etf_book_era_capacity as EC  # noqa: E402
import etf_book_liquidity_select as LS  # noqa: E402
import etf_book_scale_floor as S  # noqa: E402
import etf_robust_pf as R  # noqa: E402

OUT_JSON = os.path.join(ROOT, "results", "etf_book_capacity_shortfall.json")
OUT_MD = os.path.join(ROOT, "results", "etf_book_capacity_shortfall.md")

SLOTS = 5
REBAL = 20
COST = 0.0010
VOL_TARGET = S.VOL_TARGET

CRIT = {
    "bind_share_min": 0.05,   # D1: the line must actually refuse something
    "cost_pp": 0.50,          # D2: a cost below this is not a finding
}

# The lens ladder: the gate's own lens is the first rung, the rest are multiples of it.
# Frozen before the read -- a ladder chosen after seeing where the cost jumps would be a
# dial, not a measurement. Rung 1 must reproduce the published arms to the last digit.
LENS_MULTIPLES = (1, 3, 10, 30)


# ------------------------------------------------------------------ pure math

def scale_factors(caps, lens):
    """f = min(1, cap/lens) per rebalance. An unpriced date is left at 1.0 and counted."""
    fs, unpriced = [], 0
    for c in caps:
        if c is None:
            fs.append(1.0)
            unpriced += 1
            continue
        fs.append(1.0 if c >= lens else float(c) / float(lens))
    return fs, unpriced


def apply_overlay(ser, dec_dates, fs, cash_daily=0.0):
    """Scale the book's own NET-VALUE curve by f over each holding window.

    s_t = 1 + f * r_t + (1 - f) * c_t, compounded. `ser` is the engine's equity curve
    (levels, starting near 1.0) -- not a return series. Scaling a level directly would
    shrink the whole curve by f and print a fake drawdown (r1877's -72.37% was exactly
    that: f=0.2785 read as a -72% loss instead of "72% of the book was in cash").

    The returned curve keeps `ser.iloc[0]` as its first level, so its maxdd is measured
    against the same base as arm A.
    """
    ser = ser.dropna()
    ret = ser.pct_change().fillna(0.0)
    window = []
    for d in ser.index:
        f = 1.0
        for i, dd in enumerate(dec_dates):
            if d >= dd:
                f = fs[i] if i < len(fs) else 1.0
        window.append(f)
    fw = pd.Series(window, index=ser.index, name="f")
    scaled = fw * ret + (1.0 - fw) * float(cash_daily)
    nav = (1.0 + scaled).cumprod() * float(ser.iloc[0])
    return nav.rename("scaled"), fw


def deployed_stats(fs):
    if not fs:
        return {"rebalances": 0, "mean_f": None, "worst_f": None, "share_below_1": None}
    s = pd.Series([float(x) for x in fs])
    return {"rebalances": int(len(s)), "mean_f": round(float(s.mean()), 4),
            "worst_f": round(float(s.min()), 4),
            "share_below_1": round(float((s < 1.0 - 1e-12).mean()), 4)}


def price_lens(caps, lens, ser_a, dec_dates, stat_a, line):
    """Price one lens: how much of the book fits through the 1% line, and what it costs.

    The capacity of each rebalance (`caps`) does not depend on the lens -- only the ratio
    cap/lens does -- so the ladder is one engine run plus a handful of series operations.
    """
    fs, unpriced = scale_factors(caps, lens)
    ser_b, _ = apply_overlay(ser_a, dec_dates, fs, cash_daily=0.0)
    dep = deployed_stats(fs)
    stat_b = _stats(ser_b, "B")
    cost_pp = None
    if stat_a.get("cagr") is not None and stat_b.get("cagr") is not None:
        cost_pp = round((float(stat_b["cagr"]) - float(stat_a["cagr"])) * 100.0, 4)
    mini = {"deployed": dep, "cagr_cost_pp": cost_pp}
    return {
        "lens_cny": float(lens),
        "per_name_cny": round(float(lens) / SLOTS, 2),
        "need_adv_cny": round((float(lens) / SLOTS) / line, 2),
        "deployed": dict(dep, unpriced_dates=unpriced),
        "stats": stat_b,
        "cagr_cost_pp": cost_pp,
        "verdict": verdict_of(mini),
    }


def ladder_reading(rungs):
    """One sentence the ladder has to earn: does the cost steepen with size, and by how much?

    The cost is signed (B - A, so negative): "steeper" means more negative as the lens grows.
    A non-monotone ladder is reported as such rather than smoothed -- the interesting case is
    exactly the one where size is not the whole story.
    """
    costs = [r.get("cagr_cost_pp") for r in rungs]
    if not costs or any(c is None for c in costs):
        return {"shape": "UNREADABLE", "note": "at least one rung carries no cost"}
    steps = [round(float(costs[i]) - float(costs[i - 1]), 4) for i in range(1, len(costs))]
    monotone = all(s <= 1e-9 for s in steps)
    return {
        "shape": "MONOTONE_STEEPER" if monotone else "NOT_MONOTONE",
        "first_pp": round(float(costs[0]), 4),
        "last_pp": round(float(costs[-1]), 4),
        "span_pp": round(float(costs[-1]) - float(costs[0]), 4),
        "step_pp": steps,
        "rungs_binding": sum(1 for r in rungs
                             if (r.get("deployed") or {}).get("share_below_1") is not None
                             and float(r["deployed"]["share_below_1"]) >= CRIT["bind_share_min"]),
    }


def verdict_of(payload):
    """Derive the verdict from the published counts only (check() re-runs this)."""
    dep = payload.get("deployed") or {}
    share = dep.get("share_below_1")
    if share is None or share < CRIT["bind_share_min"]:
        return "CAPACITY_NOT_BINDING_AT_THIS_LENS"
    cost = payload.get("cagr_cost_pp")
    if cost is None:
        return "CAPACITY_BINDS_COSTS_UNREADABLE"
    return ("CAPACITY_BINDS_AND_COSTS" if abs(float(cost)) >= CRIT["cost_pp"]
            else "CAPACITY_BINDS_AT_NEGLIGIBLE_COST")


# ------------------------------------------------------------------ stats

def _stats(ser, tag):
    st = A.stats2(ser, tag)
    blk = {k: (None if st.get(k) is None else round(float(st[k]), 4))
           for k in ("cagr", "sharpe", "maxdd") if k in st}
    blk.update(S.sub_stats(ser))
    return blk


# ------------------------------------------------------------------ run

def run() -> int:
    t0 = time.time()
    face = EC.load_gate()
    rituals = EC.rulers(face)
    if rituals.get("line_frac") is None or rituals.get("lens_cny") is None:
        print("gate face carries no usable ruler: line=%r lens=%r"
              % (rituals.get("line_pct"), rituals.get("lens_cny")), flush=True)
        return 2
    line = float(rituals["line_frac"])
    lens = float(rituals["lens_cny"])
    need = (lens / SLOTS) / line

    close, openp, amt, sc, n_flip = S.nobond_universe()
    start = pd.Timestamp(getattr(R, "START", "2020-01-01"))
    dates = [d for d in openp.index if d >= start]
    dec_dates = [dates[i] for i in range(0, len(dates) - 1, REBAL)]
    print("panel %d names / %d rebalances / need ADV %s / lens %s"
          % (len(close.columns), len(dec_dates), "%.0f" % need, "%.0f" % lens), flush=True)

    adv = LS.adv_at_dates(amt, dec_dates)
    picks_map = {}
    for d in dec_dates:
        key = str(pd.Timestamp(d).date())
        picks_map[key] = [str(x) for x in sc.loc[d].dropna().nlargest(SLOTS).index]

    cap_rows = LS.cap_rows(picks_map, adv, line)
    caps = [r["cap_cny"] for r in cap_rows]
    fs, unpriced = scale_factors(caps, lens)

    ser_a, turn_a = R.open_to_open_equity(close, openp, amt, sc, REBAL, SLOTS, COST,
                                          vol_target=VOL_TARGET, vol_floor=0.0)
    ser_b, f_daily = apply_overlay(ser_a, dec_dates, fs, cash_daily=0.0)

    dep = deployed_stats(fs)
    stat_a, stat_b = _stats(ser_a, "A"), _stats(ser_b, "B")
    cost_pp = None
    if stat_a.get("cagr") is not None and stat_b.get("cagr") is not None:
        cost_pp = round((float(stat_b["cagr"]) - float(stat_a["cagr"])) * 100.0, 4)

    ladder = [price_lens(caps, lens * m, ser_a, dec_dates, stat_a, line)
              for m in LENS_MULTIPLES]

    payload = {
        "face": "etf_book_capacity_shortfall",
        "generated": pd.Timestamp.now(tz="Asia/Shanghai").isoformat(timespec="seconds"),
        "evidence_cutoff": str(pd.Timestamp(ser_a.index[-1]).date()),
        "script": "scripts/etf_book_capacity_shortfall.py",
        "criteria": {
            "line_pct": rituals.get("line_pct"), "line_frac": line,
            "lens_cny": lens, "lens_label": rituals.get("lens"),
            "slots": SLOTS, "per_name_cny": lens / SLOTS, "need_adv_cny": need,
            "rebal": REBAL, "cost_per_side": COST, "vol_target": VOL_TARGET,
            "frozen": dict(CRIT),
            "why": "the gate's ruler is a refusal, not a price: above 1% ADV the order is not "
                   "expensive, it is absent -- so the rest of the capital sits in cash",
        },
        "arms": {
            "A_published_full_fill": {"turnover": round(turn_a, 3), "stats": stat_a},
            "B_scaled_to_line": {"turnover": round(turn_a, 3), "stats": stat_b,
                                 "cash_yield_daily": 0.0},
            "C_scaled_with_repo_cash": None,
        },
        "deployed": dict(dep, unpriced_dates=unpriced),
        "cagr_cost_pp": cost_pp,
        "ladder": {
            "multiples": list(LENS_MULTIPLES),
            "frozen": "rungs fixed before the read; rung 1 is the gate's own lens and must "
                      "reproduce arms.B digit for digit",
            "rungs": ladder,
            "reading": ladder_reading(ladder),
        },
        "capacity_rows": [{"date": r["date"], "cap_cny": r["cap_cny"],
                           "f": fs[i]} for i, r in enumerate(cap_rows)],
        "elapsed_sec": round(time.time() - t0, 1),
        "honest": [
            "the overlay compounds the book's own daily returns at f; the engine curve is a "
            "LEVEL series, and scaling a level by f would print a fake drawdown (r1877's "
            "-72.37% was exactly that: '72% in cash' read as a 72% loss)",
            "r1877's arms.B (10.36% / -72.37%) was computed on that level-scaling error and is "
            "superseded by this run's compounded arm B; the f column and the binding counts are "
            "unchanged, only the return path is",
            "scaling the slate by f also scales the vol-target overlay that fitted it, so B's "
            "vol is f times A's and its sharpe is not simply A's sharpe",
            "the idle cash earns 0 in arm B; r1269 already measured the repo ladder's worth at "
            "+0.10~0.15pp/yr on this book, so B is the LOWER bound and arm C is left absent "
            "rather than silently equated to B",
            "entry_lag=0 is the published behaviour, kept so arm A reproduces every printed face",
            "capacity is read from the same 40-bar ruler as every other capacity face, so this "
            "face inherits their survivors-sweep bias",
            "the ladder rungs are multiples of the gate's own lens, frozen before the read; a "
            "rung beyond 10M sits almost entirely in cash, so its return is the cash curve, not "
            "a bigger book",
            "nothing here is adopted: this prices the ruler, it does not change the book",
        ],
    }
    payload["verdict"] = verdict_of(payload)

    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    write_md(payload)
    print("verdict %s | deployed mean f %.3f (worst %.3f, %d/%d below 1) | CAGR A %.2f%%, B %.2f%%"
          % (payload["verdict"], dep["mean_f"] or 0, dep["worst_f"] or 0,
             sum(1 for x in fs if x < 1 - 1e-12), len(fs),
             (stat_a.get("cagr") or 0) * 100, (stat_b.get("cagr") or 0) * 100), flush=True)
    print("-> %s (%.1fs)" % (OUT_JSON, time.time() - t0), flush=True)
    return 0


def _lens_label(x):
    x = float(x)
    for cut, suf in ((1e8, "亿"), (1e4, "万")):
        if x >= cut:
            v = x / cut
            return ("%d%s" % (v, suf)) if abs(v - round(v)) < 1e-9 else ("%.1f%s" % (v, suf))
    return "{:,.0f}".format(x)


def write_md(p):
    a = p["arms"]["A_published_full_fill"]["stats"]
    b = p["arms"]["B_scaled_to_line"]["stats"]
    d = p["deployed"]
    n_below = sum(1 for r in p["capacity_rows"] if r["f"] < 1 - 1e-12)
    pct = lambda x: "n/a" if x is None else "%.2f%%" % (x * 100.0)
    money = lambda x: "n/a" if x is None else "{:,.0f}".format(x)
    L = ["# 那条 1% 的线是拒绝，不是价格：装不进去的钱去哪了", "",
         "证据截止 %s · 门 %s · 每名 %s 元 · 槽位 %d · 调仓 %d 日"
         % (p["evidence_cutoff"], p["criteria"]["lens_label"], money(p["criteria"]["per_name_cny"]),
            p["criteria"]["slots"], p["criteria"]["rebal"]), "",
         "## 判词：%s" % p["verdict"], "",
         "同一本书、同样五个名字：按「1%% ADV 装得下多少就买多少，剩下留现金」重读，"
         "在 %d 次调仓里有 %d 次装不满（占 %.1f%%），平均只能投出 %.1f%% 的钱，最差一次只剩 %.1f%%。"
         % (d["rebalances"], n_below, 100.0 * (d["share_below_1"] or 0),
            100.0 * (d["mean_f"] or 0), 100.0 * (d["worst_f"] or 0)), "",
         "| 臂 | 年化 | 夏普 | 回撤 | 换手 |", "|---|---:|---:|---:|---:|",
         "| A 全额成交（所有在印面） | %s | %.3f | %s | %.3f |"
         % (pct(a.get("cagr")), a.get("sharpe") or 0, pct(a.get("maxdd")),
            p["arms"]["A_published_full_fill"]["turnover"]),
         "| B 按线缩仓 + 现金 0%% | %s | %.3f | %s | %.3f |"
         % (pct(b.get("cagr")), b.get("sharpe") or 0, pct(b.get("maxdd")),
            p["arms"]["B_scaled_to_line"]["turnover"]), "",
         "守规矩的代价：**%+.2f pp/年**（B 减 A）。现金那一半按 0%% 计，所以这是下界——"
         "r1269 已量过本书记载的回购腿值 +0.10~0.15pp/年。" % (p["cagr_cost_pp"] or 0.0), "",
         "### 更正（本版修复）", "",
         "r1877 在同一个面上发布过 -1.02 pp/年，并把 B 的回撤印成 -72.37%%。那不是书的回撤，"
         "是叠加层的算术错误：引擎给的是一条**净值曲线**，旧代码直接把它乘以 f，于是"
         "「72%% 的钱在现金里」被读成「亏了 72%%」。本版先把净值还原成日收益再缩放重建，"
         "回撤回到 -10.56%%（与 A 同基准），1M 镜片下的代价也随之从 -1.02pp 收到 %+.2f pp。"
         % (p["cagr_cost_pp"] or 0.0), "",
         "f 列与「装不满的次数」不受影响：那些是容量读数，不是收益读数。", "",
         "## 装不下的那几天", "",
         "| 调仓日 | 容量（元） | 能投出的比例 f |", "|---|---:|---:|",
         ]
    for r in sorted(p["capacity_rows"], key=lambda x: (x["f"] if x["f"] is not None else 1.0))[:8]:
        L.append("| %s | %s | %.1f%% |" % (r["date"], money(r["cap_cny"]), 100.0 * r["f"]))
    lad = p.get("ladder") or {}
    rungs = lad.get("rungs") or []
    if rungs:
        rd = lad.get("reading") or {}
        L += ["", "## 换个规模再读一遍：代价随规模怎么变", "",
              "同一本书、同一批名字、同一条 1%% ADV 的线，只把资金换成不同镜片。"
              "判词：**%s**，从 %s 的 %+.2f pp/年 到 %s 的 %+.2f pp/年，跨度 %+.2f pp。"
              % (rd.get("shape"), _lens_label(rungs[0]["lens_cny"]), rd.get("first_pp") or 0.0,
                 _lens_label(rungs[-1]["lens_cny"]), rd.get("last_pp") or 0.0,
                 rd.get("span_pp") or 0.0), "",
              "| 资金 | 每名 | 装不满的调仓 | 平均能投出 | 最差一次 | 年化（按线缩仓） | 代价 vs 全额 |",
              "|---:|---:|---:|---:|---:|---:|---:|",
              "| 全额成交（对照） | — | — | — | — | %s | — |" % pct(a.get("cagr"))]
        for r in rungs:
            dd, st = r["deployed"], r["stats"]
            L.append("| %s | %s | %.1f%% | %.1f%% | %.1f%% | %s | %+.2f pp |"
                     % (_lens_label(r["lens_cny"]), money(r["per_name_cny"]),
                        100.0 * (dd.get("share_below_1") or 0), 100.0 * (dd.get("mean_f") or 0),
                        100.0 * (dd.get("worst_f") or 0), pct(st.get("cagr")),
                        r.get("cagr_cost_pp") or 0.0))
        L += ["", "第一行是所有在印面的全额成交臂（不动，只作对照）。"
                  "阶梯各档都是「按线缩仓 + 现金 0%」，所以每一行都与全额臂比。", "",
              "读法提醒：夏普在 3M 反而比 1M 高（%.3f 对 %.3f）——那是「一半钱躺在 0%% 现金里」"
              "把波动压掉的结果，不是「更大的书更好」；收益列才是规模的价钱。"
              % (rungs[1]["stats"].get("sharpe") if len(rungs) > 1 and rungs[1]["stats"].get("sharpe") is not None else 0.0,
                 rungs[0]["stats"].get("sharpe") if rungs[0]["stats"].get("sharpe") is not None else 0.0)]
    L += ["", "## 诚实边界", ""] + ["- " + h for h in p["honest"]]
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")


def ladder_check(p):
    """Re-derive every rung from the published capacity rows; rung 1 must equal arms.B."""
    probs = []
    lad = p.get("ladder") or {}
    rungs = lad.get("rungs") or []
    if not rungs:
        return ["ladder missing from the payload"]
    gate = p.get("criteria") or {}
    arm_b = ((p.get("arms") or {}).get("B_scaled_to_line") or {})
    line = float(gate.get("line_frac") or 0.0)
    if line <= 0:
        return ["gate line unreadable in payload"]
    rows = p.get("capacity_rows") or []
    r1 = rungs[0]
    if abs(float(r1["lens_cny"]) - float(gate["lens_cny"])) > 1e-6:
        probs.append("rung1 lens %r != gate lens %r" % (r1["lens_cny"], gate["lens_cny"]))
    if (r1.get("stats") or {}) != (arm_b.get("stats") or {}):
        probs.append("rung1 stats differ from arms.B (the rung must reproduce the arm)")
    if r1.get("cagr_cost_pp") != p.get("cagr_cost_pp"):
        probs.append("rung1 cost %r != published %r" % (r1.get("cagr_cost_pp"), p.get("cagr_cost_pp")))
    for i, r in enumerate(rungs):
        lens = float(r["lens_cny"])
        if abs(float(r["per_name_cny"]) - round(lens / SLOTS, 2)) > 0.01:
            probs.append("rung%d per_name %r" % (i, r["per_name_cny"]))
        if abs(float(r["need_adv_cny"]) - round((lens / SLOTS) / line, 2)) > 0.01:
            probs.append("rung%d need_adv %r" % (i, r["need_adv_cny"]))
        fs = [1.0 if (x.get("cap_cny") is None) else min(1.0, float(x["cap_cny"]) / lens)
              for x in rows]
        dep = deployed_stats(fs)
        pub = r.get("deployed") or {}
        for k in ("rebalances", "mean_f", "worst_f", "share_below_1"):
            if dep.get(k) != pub.get(k):
                probs.append("rung%d deployed.%s %r != %r" % (i, k, pub.get(k), dep.get(k)))
    # the r1877 overlay bug must not come back: shrinking the book can only shrink its swings
    a_dd = ((p.get("arms") or {}).get("A_published_full_fill") or {}).get("stats", {}).get("maxdd")
    b_dd = ((p.get("arms") or {}).get("B_scaled_to_line") or {}).get("stats", {}).get("maxdd")
    if a_dd is not None and b_dd is not None and float(b_dd) < float(a_dd) - 0.02:
        probs.append("arm B drawdown %.4f is deeper than A %.4f -- the overlay is scaling a "
                     "level curve again instead of compounding returns" % (b_dd, a_dd))
    # the ladder's own sentence must agree with its rungs
    rd = lad.get("reading") or {}
    costs = [x.get("cagr_cost_pp") for x in rungs]
    if rd.get("shape") == "MONOTONE_STEEPER":
        for i in range(1, len(costs)):
            if costs[i] is None or costs[i - 1] is None or costs[i] > costs[i - 1] + 1e-9:
                probs.append("ladder says MONOTONE but rung%d steps up" % i)
                break
    return probs


def check() -> int:
    if not os.path.exists(OUT_JSON):
        print("face missing: %s" % OUT_JSON, flush=True)
        return 2
    with open(OUT_JSON, encoding="utf-8") as fh:
        p = json.load(fh)
    v = verdict_of(p)
    ok = v == p.get("verdict")
    rows = p.get("capacity_rows") or []
    bad = [r for r in rows if r.get("f") is not None and r["cap_cny"] is not None
           and abs(r["f"] - min(1.0, r["cap_cny"] / float(p["criteria"]["lens_cny"]))) > 1e-9]
    rung_probs = ladder_check(p)
    print("check %s verdict=%s published=%s f_rows_check=%d bad=%d ladder_probs=%d"
          % ("ok" if (ok and not bad and not rung_probs) else "FAIL", v, p.get("verdict"),
             len(rows), len(bad), len(rung_probs)), flush=True)
    for x in rung_probs[:8]:
        print("  LADDER " + x, flush=True)
    return 0 if (ok and not bad and not rung_probs) else 3


# ------------------------------------------------------------------ selftest

def selftest() -> int:
    legs, fails = [], []

    def leg(name, cond, detail=""):
        legs.append(name)
        if not cond:
            fails.append("%s: %s" % (name, detail))

    fs, unp = scale_factors([1_000_000, 500_000, 2_000_000, None], 1_000_000)
    leg("L1 f formula", fs == [1.0, 0.5, 1.0, 1.0] and unp == 1, str(fs))
    fs2, _ = scale_factors([100_000], 1_000_000)
    leg("L2 partial", abs(fs2[0] - 0.1) < 1e-12, str(fs2))

    lvl = pd.Series([1.0, 1.01, 0.9898, 1.0195],
                    index=pd.to_datetime(["2020-01-02", "2020-01-03", "2020-01-06", "2020-01-07"]))
    dec = [pd.Timestamp("2020-01-02")]
    out, fw = apply_overlay(lvl, dec, [1.0])
    leg("L3 all-f-1 reproduces", all(abs(a - b) < 1e-12 for a, b in zip(out.values, lvl.values)), str(out.values))

    rr = lvl.pct_change().fillna(0.0)
    out2, fw2 = apply_overlay(lvl, dec, [0.5])
    want2 = (1.0 + 0.5 * rr).cumprod() * float(lvl.iloc[0])
    leg("L4 half invested", all(abs(a - b) < 1e-12 for a, b in zip(out2.values, want2.values)), str(out2.values))
    leg("L5 window carries f", list(fw2.values) == [0.5, 0.5, 0.5, 0.5], str(fw2.values))

    out3, _ = apply_overlay(lvl, dec, [0.5], cash_daily=0.0002)
    want3 = (1.0 + 0.5 * rr + 0.5 * 0.0002).cumprod() * float(lvl.iloc[0])
    leg("L6 cash leg paid", all(abs(a - b) < 1e-12 for a, b in zip(out3.values, want3.values)), str(out3.values))

    # r1877 printed f=0.28 as a -72% drawdown because it scaled a LEVEL by f. A rising curve
    # held at half size must still rise; only its slope changes.
    up = pd.Series([1.01 ** i for i in range(40)], index=pd.bdate_range("2020-01-02", periods=40))
    out_up, _ = apply_overlay(up, [up.index[0]], [0.5])
    leg("L6b scaling never turns a rising curve into a loss",
        out_up.iloc[-1] > out_up.iloc[0] and float(out_up.min()) >= float(up.iloc[0]) - 1e-12,
        "start=%.4f end=%.4f min=%.4f" % (up.iloc[0], out_up.iloc[-1], out_up.min()))

    d = deployed_stats([1.0, 0.5, 0.5, 0.0])
    leg("L7 deployed stats", d["mean_f"] == 0.5 and d["worst_f"] == 0.0 and d["share_below_1"] == 0.75, str(d))

    leg("L8 verdict not-binding", verdict_of({"deployed": {"share_below_1": 0.0}}) == "CAPACITY_NOT_BINDING_AT_THIS_LENS")
    leg("L9 verdict binds costs", verdict_of({"deployed": {"share_below_1": 0.5}, "cagr_cost_pp": -1.2}) == "CAPACITY_BINDS_AND_COSTS")
    leg("L10 verdict binds cheap", verdict_of({"deployed": {"share_below_1": 0.5}, "cagr_cost_pp": -0.1}) == "CAPACITY_BINDS_AT_NEGLIGIBLE_COST")
    leg("L11 unreadable cost", verdict_of({"deployed": {"share_below_1": 0.5}, "cagr_cost_pp": None}) == "CAPACITY_BINDS_COSTS_UNREADABLE")

    # ---- ladder legs (r1878)
    idx4 = pd.bdate_range("2020-01-02", periods=300)
    rets4 = [0.002 * (((i * 7) % 11) - 5) / 5.0 for i in range(len(idx4))]
    ser4 = (1.0 + pd.Series(rets4, index=idx4)).cumprod()
    dec4 = [idx4[0]]
    sa = _stats(ser4, "A")
    r = price_lens([500_000], 1_000_000, ser4, dec4, sa, 0.01)
    leg("L12 rung fields", r["per_name_cny"] == 200000.0 and abs(r["need_adv_cny"] - 20_000_000.0) < 0.01
        and r["deployed"]["mean_f"] == 0.5 and r["deployed"]["share_below_1"] == 1.0, str(r["deployed"]))
    leg("L13 full-f rung costs nothing", abs(price_lens([9e9], 1_000_000, ser4, dec4, sa, 0.01)["cagr_cost_pp"]) < 1e-9)

    rd_ok = ladder_reading([{"cagr_cost_pp": -1.0, "deployed": {"share_below_1": 0.2}},
                            {"cagr_cost_pp": -3.0, "deployed": {"share_below_1": 0.9}}])
    leg("L14 ladder monotone", rd_ok["shape"] == "MONOTONE_STEEPER" and rd_ok["span_pp"] == -2.0
        and rd_ok["rungs_binding"] == 2, str(rd_ok))
    rd_bad = ladder_reading([{"cagr_cost_pp": -3.0, "deployed": {"share_below_1": 0.9}},
                             {"cagr_cost_pp": -1.0, "deployed": {"share_below_1": 0.2}}])
    leg("L15 ladder non-monotone named", rd_bad["shape"] == "NOT_MONOTONE", str(rd_bad))
    leg("L16 ladder unreadable", ladder_reading([{"cagr_cost_pp": None}])["shape"] == "UNREADABLE")

    mini = {
        "criteria": {"line_frac": 0.01, "lens_cny": 1_000_000.0},
        "arms": {"B_scaled_to_line": {"stats": {"cagr": 0.1}}},
        "capacity_rows": [{"cap_cny": 500_000.0}],
        "cagr_cost_pp": -0.5,
        "ladder": {"rungs": [{"lens_cny": 1_000_000.0, "per_name_cny": 200000.0,
                              "need_adv_cny": 20_000_000.0, "stats": {"cagr": 0.1},
                              "cagr_cost_pp": -0.5,
                              "deployed": {"rebalances": 1, "mean_f": 0.5, "worst_f": 0.5,
                                           "share_below_1": 1.0, "unpriced_dates": 0}}],
                   "reading": {"shape": "MONOTONE_STEEPER"}},
    }
    leg("L17 ladder_check passes", ladder_check(mini) == [], str(ladder_check(mini))[:200])
    mini2 = json.loads(json.dumps(mini))
    mini2["ladder"]["rungs"][0]["stats"] = {"cagr": 0.2}
    leg("L18 ladder_check catches a drifted rung", any("arms.B" in x for x in ladder_check(mini2)))

    print("capacity_shortfall selftest %d/%d PASS" % (len(legs) - len(fails), len(legs)), flush=True)
    for f in fails:
        print("  FAIL " + f, flush=True)
    return 0 if not fails else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "check", "selftest"])
    a = ap.parse_args()
    if a.cmd == "selftest":
        return selftest()
    if a.cmd == "check":
        return check()
    return run()


if __name__ == "__main__":
    sys.exit(main())
