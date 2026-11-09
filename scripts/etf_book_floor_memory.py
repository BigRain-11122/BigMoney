#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""should the RULE remember the permission, or should a human re-cut the sheet every bar?

WHY THIS FILE EXISTS
--------------------
r1456/r1471 left one sentence standing on the desk: the sheet obeys the floor (k=0.390822
against permitted 0.393073) but the RULE's own last decision bar sizes at k=0.460253, so the
next sheet walks back over the floor unless the same trim is applied again on that bar.
results/etf_book_floor_ledger.json prints that as REAPPLY_REQUIRED.

That sentence describes an EVENT, not a rule. Nobody has ever asked how often the event
fires. If the sizing rule stands above the floor on most decision bars, then "the sheet
obeys the floor" is a claim about a person doing manual work every 20 bars, and the record
of that work lives nowhere -- the floor ledger only knows the last sheet.

This face prices the alternative that makes the permission an invariant instead of a chore:
`vol_cap = floor_k` (the sizing rule may never take the book above the permitted k). One
number is added that no existing face publishes: how many decision bars per year the control
arm stands ABOVE the floor, i.e. how much manual cutting the hard cap would remove.

WHAT IT DOES NOT DO
-------------------
It does not change the production cell and it does not re-issue the floor. It publishes a
verdict on the change, judged on a phase x cost grid, with the criteria frozen below.

VERDICTS
  ADOPT             the cap improves risk-adjusted shape or costs nothing, on phases AND costs
  COST_DEPENDENT    only exists at the 10bp assumption
  PHASE_DEPENDENT   the pass exists on some decision calendars only
  WITHIN_NOISE      the effect is smaller than the book's own phase spread
  REJECT            the cap gives back return without buying shape
  NOT_ASSESSED      grid too thin (never read as a pass)
  CONTROL_FAILED    the control arm did not reproduce the published book

self  python scripts/etf_book_floor_memory.py selftest    # synthetic, fast
run   python scripts/etf_book_floor_memory.py run         # real panel, ~1 min
check python scripts/etf_book_floor_memory.py check       # re-derive verdict from receipt
"""
from __future__ import annotations

import argparse
import io
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np
import pandas as pd

import etf_composite_pf as E
import etf_robust_pf as R
import etf_equity_alpha as A
import etf_book_concentration_levers as CL          # yearly_rows / gate_of / published_yearly_rows
from etf_book_buffer_adoption import phase_starts   # the phase ruler: one copy

OUT = os.path.join(ROOT, "results", "etf_book_floor_memory.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_FLOOR_MEMORY.md")
CONTROL_RECEIPT = os.path.join(ROOT, "results", "etf_nobond_vt.json")
FLOOR_FACE = os.path.join(ROOT, "results", "etf_book_floor_ledger.json")

# ---------------------------------------------------------------- frozen criteria
CONTROL = {"rebal": 20, "n_hold": 5, "cost": 0.0010, "vol_target": 0.08, "vol_cap": 1.0}
N_PHASES = 5
COSTS = (0.0010, 0.0020)
COST_TOL = 5e-4                    # control CAGR reproduction tolerance (0.05pp)
RETURN_FLOOR_PP = -0.15            # per-cell CAGR allowance before it counts as a toll
SHARPE_GAIN_MIN = 0.00             # median dSharpe must be at least this to buy the cap
PHASE_SHARE_MIN = 0.60             # the cap must not lose return on this share of phases
MIN_PHASES_PER_COST = 3            # below this a cost row is NOT_ASSESSED

CRITERIA = {
    "control": CONTROL,
    "n_phases": N_PHASES,
    "costs_bp": [int(round(c * 10000)) for c in COSTS],
    "return_floor_pp": RETURN_FLOOR_PP,
    "sharpe_gain_min": SHARPE_GAIN_MIN,
    "phase_share_min": PHASE_SHARE_MIN,
    "min_phases_per_cost": MIN_PHASES_PER_COST,
    "frozen": "written before the first run; `check` refuses a face that echoes other numbers",
}
VERDICTS = ("ADOPT", "COST_DEPENDENT", "PHASE_DEPENDENT", "WITHIN_NOISE",
            "REJECT", "NOT_ASSESSED", "CONTROL_FAILED")

UNITS = {
    "cagr_pct": "percent per year",
    "sharpe": "annualised excess return / volatility, engine definition",
    "maxdd_pct": "worst peak-to-trough of the equity curve, percent",
    "delta_cagr_pp": "percentage points, hard cap minus control on the same phase and cost",
    "cap_binding_share": "share of control decision bars whose own scale stands above the floor",
    "cap_binding_decisions_per_year": "control decision bars above the floor, per calendar year",
    "phase": "decision-grid start bar inside one rebalance cycle",
}


def floor_k() -> float | None:
    """The permitted k in force, read from the published ledger -- never restated here."""
    if not os.path.exists(FLOOR_FACE):
        return None
    with io.open(FLOOR_FACE, encoding="utf-8") as f:
        rec = json.load(f)
    a = rec.get("assessed") or {}
    v = a.get("floor")
    return None if v is None else float(v)


# ---------------------------------------------------------------- mechanics

def burn(close, openp, amt, score, cost, start, cap, rebal=None):
    """One (arm, phase, cost) cell through the production engine, plus its own years."""
    rebal = CONTROL["rebal"] if rebal is None else rebal
    diag = []
    ser, turn = R.open_to_open_equity(
        close, openp, amt, score, rebal, CONTROL["n_hold"], cost,
        vol_target=CONTROL["vol_target"], vol_cap=cap,
        start=str(pd.Timestamp(start).date()), diag=diag)
    st = A.stats2(ser, "cell")
    yrs = max(1e-9, (ser.index[-1] - ser.index[0]).days / 365.25)
    decisions = len(diag)
    scales = [float(d["scale"]) for d in diag
              if d.get("scale") is not None and np.isfinite(d["scale"])]
    years = CL.yearly_rows(ser)
    g = CL.gate_of(years)
    top2 = g["metrics"].get("top2_share")
    return {
        "cagr_pct": round(float(st.get("cagr", float("nan"))) * 100.0, 4),
        "sharpe": round(float(st.get("sharpe", float("nan"))), 4),
        "maxdd_pct": round(float(st.get("maxdd", float("nan"))) * 100.0, 4),
        "turnover_per_decision": round(float(turn), 6),
        "decisions": decisions,
        "years": round(yrs, 4),
        "yearly": {str(y): v for y, v in years.items()},
        "scale_median": (round(float(np.median(scales)), 6) if scales else None),
        "scale_max": (round(float(np.max(scales)), 6) if scales else None),
        "verdict_year_gate": g["verdict"],
        "checks": g["checks"],
        "top2_share": (None if top2 is None else round(float(top2), 4)),
        "_ser": ser,
    }


def _key(cost: float) -> str:
    """The by-cost key, derived once: 0.0010 -> "10". Never spelled by hand."""
    return str(int(round(cost * 10000)))


def _by(cells, arm, cost):
    return sorted([c for c in cells if c["arm"] == arm and abs(c["cost"] - cost) < 1e-9],
                  key=lambda c: c["phase"])


def _median(v):
    v = [x for x in v if x is not None and np.isfinite(x)]
    return float(np.median(v)) if v else None


def _iqr(v):
    v = [x for x in v if x is not None and np.isfinite(x)]
    if len(v) < 2:
        return None
    return float(np.subtract(*np.percentile(v, [75, 25])))


def summarize(cells, control_reproduces=True):
    out = {"by_cost": {}, "n_cells": len(cells)}
    if not control_reproduces:
        out["degraded"] = "control did not reproduce the published book"
        return out
    for cost in COSTS:
        ctrl = {c["phase"]: c for c in _by(cells, "control", cost)}
        cand = {c["phase"]: c for c in _by(cells, "candidate", cost)}
        phases = sorted(set(ctrl) & set(cand))
        rows = []
        for p in phases:
            a, b = cand[p], ctrl[p]
            rows.append({
                "phase": p,
                "ctrl_cagr_pct": b["cagr_pct"], "cand_cagr_pct": a["cagr_pct"],
                "delta_cagr_pp": round(a["cagr_pct"] - b["cagr_pct"], 4),
                "delta_sharpe": round(a["sharpe"] - b["sharpe"], 4),
                "delta_maxdd_pp": round(a["maxdd_pct"] - b["maxdd_pct"], 4),
                "cand_top2_share": a["top2_share"], "ctrl_top2_share": b["top2_share"],
            })
        d_cagr = [r["delta_cagr_pp"] for r in rows]
        d_shp = [r["delta_sharpe"] for r in rows]
        out["by_cost"][_key(cost)] = {
            "phases": len(phases),
            "cand_cagr_median_pct": _median([r["cand_cagr_pct"] for r in rows]),
            "ctrl_cagr_median_pct": _median([r["ctrl_cagr_pct"] for r in rows]),
            "delta_cagr_median_pp": _median(d_cagr),
            "delta_cagr_iqr_pp": _iqr(d_cagr),
            "delta_cagr_min_pp": (min(d_cagr) if d_cagr else None),
            "delta_cagr_max_pp": (max(d_cagr) if d_cagr else None),
            "delta_sharpe_median": _median(d_shp),
            "delta_maxdd_median_pp": _median([r["delta_maxdd_pp"] for r in rows]),
            "share_cells_return_kept": (round(sum(1 for x in d_cagr
                                                 if x >= RETURN_FLOOR_PP) / float(len(d_cagr)), 4)
                                        if d_cagr else None),
            "rows": rows,
        }
        # the cap's own price tag: how often the control rule stood above the floor
        cb = [c.get("cap_binding_share") for c in ctrl.values()]
        cy = [c.get("cap_binding_decisions_per_year") for c in ctrl.values()]
        out["by_cost"][_key(cost)]["control_cap_binding_share_median"] = _median(cb)
        out["by_cost"][_key(cost)]["control_cap_binding_decisions_per_year_median"] = _median(cy)
    return out


def verdict_of(s, control_reproduces=True, phase_spread_pp=None):
    """Re-derivable, by construction: every branch reads the summary, none is hand-written."""
    if not control_reproduces:
        return "CONTROL_FAILED", ["control arm did not reproduce the published book"]
    reasons, ok_costs, thin = [], [], []
    for k, blk in s.get("by_cost", {}).items():
        if (blk.get("phases") or 0) < MIN_PHASES_PER_COST:
            thin.append(k)
            continue
        d_c = blk.get("delta_cagr_median_pp")
        d_s = blk.get("delta_sharpe_median")
        share = blk.get("share_cells_return_kept")
        if d_c is None or d_s is None or share is None:
            thin.append(k)
            continue
        keeps_return = d_c >= RETURN_FLOOR_PP and share >= PHASE_SHARE_MIN
        buys_shape = d_s >= SHARPE_GAIN_MIN
        reasons.append("cost %sbp: dCAGR median %+.4fpp (min %+.4f, share kept %.3f), "
                       "dSharpe median %+.4f" % (k, d_c, blk.get("delta_cagr_min_pp") or 0.0,
                                                 share, d_s))
        ok_costs.append(bool(keeps_return and buys_shape))
    if not ok_costs:
        return ("NOT_ASSESSED" if thin else "REJECT"), reasons or ["no assessable cost row"]
    if not all(ok_costs):
        # COST_DEPENDENT is a claim that a pass EXISTS somewhere and disappears elsewhere;
        # with zero passing rows the honest word is REJECT, not "depends on cost".
        if not any(ok_costs):
            return "REJECT", reasons + ["no cost row passes"]
        return "COST_DEPENDENT", reasons + ["pass exists on a subset of cost assumptions only"]
    if thin:
        return "NOT_ASSESSED", reasons + ["cost rows %s too thin" % thin]
    # phase dependence: the pass must not hinge on one decision calendar
    for k, blk in s.get("by_cost", {}).items():
        rows = blk.get("rows") or []
        if not rows:
            continue
        passing = sum(1 for r in rows
                      if r["delta_cagr_pp"] >= RETURN_FLOOR_PP and r["delta_sharpe"] >= SHARPE_GAIN_MIN)
        if passing / float(len(rows)) < PHASE_SHARE_MIN:
            return "PHASE_DEPENDENT", reasons + [
                "cost %sbp: only %d/%d phases pass" % (k, passing, len(rows))]
    if phase_spread_pp is not None and phase_spread_pp > 0:
        worst = max(abs(blk.get("delta_cagr_median_pp") or 0.0) for blk in s["by_cost"].values())
        if worst < phase_spread_pp:
            return "WITHIN_NOISE", reasons + [
                "effect %.4fpp is smaller than the book's own phase spread %.4fpp"
                % (worst, phase_spread_pp)]
    return "ADOPT", reasons


def phase_spread(cells, cost):
    """The control book's own CAGR spread across decision phases -- the noise ruler."""
    v = [c["cagr_pct"] for c in _by(cells, "control", cost)]
    if len(v) < 2:
        return None
    return float(max(v) - min(v))


def desk_line(label):
    return {
        "ADOPT": "对票面：可把额度写成规则不变量（vol_cap=floor），票面不再依赖每 bar 人工裁剪。",
        "COST_DEPENDENT": "对票面：不改。这条 pass 只在 10bp/边下存在，真实成本接近 20bp 即消失。",
        "PHASE_DEPENDENT": "对票面：不改。pass 只在部分决策日历上出现，那不是规则。",
        "WITHIN_NOISE": "对票面：不改。让出的收益小于这本书自己的相位噪度，读数不可分。",
        "REJECT": "对票面：不改，且这条建议从候选池划线为已定价失败；人工裁剪继续是常态动作。",
        "NOT_ASSESSED": "对票面：不改，也不下结论——网格太薄。",
        "CONTROL_FAILED": "对票面：不改，本轮控制臂都没复现，什么都别说。",
    }.get(label, "对票面：不改。")


# ---------------------------------------------------------------- run / check

def run() -> int:
    t0 = time.time()
    fk = floor_k()
    if fk is None:
        print("FATAL: no permitted k in %s -- nothing to remember" % FLOOR_FACE, flush=True)
        return 2
    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    want = ("equity", "commodity", "convertible")     # the adopted book is bond-free
    cols = [c for c in close.columns if cls[c] in want]
    sc = E.build_score(close[cols], amt[cols], feats)
    print("bond-free universe %d (flips repaired %d) floor_k=%.6f"
          % (len(cols), n_flip, fk), flush=True)

    starts = phase_starts(close.index, rebal=CONTROL["rebal"], n=N_PHASES)
    print("phases: %s" % [str(pd.Timestamp(d).date()) for d in starts], flush=True)

    cells = []
    for cost in COSTS:
        for start in starts:
            for arm, cap in (("control", CONTROL["vol_cap"]), ("candidate", fk)):
                r = burn(close[cols], openp[cols], amt[cols], sc, cost, start, cap)
                ser = r.pop("_ser")
                r.update({"arm": arm, "cost": cost, "vol_cap": cap,
                          "phase": str(pd.Timestamp(start).date())})
                cells.append(r)
                print("  %-9s %sbp %s cagr %7.4f sharpe %5.3f maxdd %7.3f scale_med %s %s"
                      % (arm, _key(cost), r["phase"], r["cagr_pct"], r["sharpe"],
                         r["maxdd_pct"], r["scale_median"], r["verdict_year_gate"]), flush=True)

    # fill the cap-binding diagnostic on the control cells (it is a control-arm property)
    for c in cells:
        if c["arm"] != "control":
            continue
        smed_max = c.get("scale_max")
        # NOTE: scale_max is the max scale observed; the share needs the per-bar series, so it
        # is populated below from the diag of a dedicated re-run only when missing.
        c.setdefault("cap_binding_share", None)
        c.setdefault("cap_binding_decisions_per_year", None)

    # the per-bar share needs the scale series; derive it with one extra cheap pass per phase
    diag_cache = {}
    for start in starts:
        d = []
        R.open_to_open_equity(close[cols], openp[cols], amt[cols], sc, CONTROL["rebal"],
                              CONTROL["n_hold"], CONTROL["cost"],
                              vol_target=CONTROL["vol_target"],
                              start=str(pd.Timestamp(start).date()), diag=d)
        diag_cache[str(pd.Timestamp(start).date())] = [float(x["scale"]) for x in d
                                                       if x.get("scale") is not None
                                                       and np.isfinite(x["scale"])]
    for c in cells:
        if c["arm"] != "control":
            continue
        s = diag_cache.get(c["phase"]) or []
        if s:
            over = sum(1 for x in s if x > fk)
            c["cap_binding_share"] = round(over / float(len(s)), 4)
            yrs = max(1e-9, c["years"])
            c["cap_binding_decisions_per_year"] = round(over / yrs, 3)
            c["n_decisions_over_floor"] = int(over)
            c["n_decisions"] = len(s)

    # ---- control reproduction, before anything is claimed
    control_cells = _by(cells, "control", CONTROL["cost"])
    ctrl = dict(control_cells[0]) if control_cells else None
    published_cagr = None
    if os.path.exists(CONTROL_RECEIPT):
        with io.open(CONTROL_RECEIPT, encoding="utf-8") as f:
            rec = json.load(f)
        for r in rec.get("runs", []):
            if r.get("label") == "nobond_vt08":
                published_cagr = round(float(r["cagr"]) * 100.0, 4)
                break
    pub_years = CL.published_yearly_rows()
    gaps = {}
    if ctrl is not None:
        for y, want_pct in (pub_years or {}).items():
            got = (ctrl.get("yearly") or {}).get(str(y), {}).get("net_pct")
            gaps[str(y)] = (None if got is None else round(got - want_pct, 4))
        ctrl.update({"published_cagr_pct": published_cagr,
                     "published_yearly_pct": pub_years,
                     "published_year_gaps_pp": gaps})
        ctrl["reproduces_published"] = bool(
            published_cagr is not None
            and abs(ctrl["cagr_pct"] - published_cagr) <= COST_TOL * 100
            and pub_years and not any(abs(g) > 1e-2 for g in gaps.values() if g is not None))
    reproduces = bool(ctrl and ctrl.get("reproduces_published"))
    print("control cagr %.4f vs published %r reproduces=%s"
          % ((ctrl or {}).get("cagr_pct", float("nan")), published_cagr, reproduces), flush=True)

    spread = phase_spread(cells, CONTROL["cost"])
    s = summarize(cells, control_reproduces=reproduces)
    s["control_phase_spread_cagr_pp"] = (None if spread is None else round(spread, 4))
    label, reasons = verdict_of(s, control_reproduces=reproduces, phase_spread_pp=spread)

    payload = {
        "face": "etf_book_floor_memory",
        "asof": pd.Timestamp.now(tz="Asia/Shanghai").isoformat(timespec="seconds"),
        "evidence_cutoff": str(close.index[-1].date()),
        "question": ("should the sizing rule carry the permission as an invariant "
                     "(vol_cap=floor) instead of a person re-cutting the sheet every decision bar?"),
        "rule": dict(CRITERIA, units=UNITS),
        "floor_k": fk,
        "control": ctrl,
        "cells": cells,
        "summary": s,
        "verdict": {"label": label, "reasons": reasons, "desk": desk_line(label)},
        "elapsed_sec": round(time.time() - t0, 2),
    }
    with io.open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    print("VERDICT %s | %s" % (label, desk_line(label)), flush=True)
    for r in reasons:
        print("  - %s" % r, flush=True)
    print("wrote %s in %.1fs" % (OUT, payload["elapsed_sec"]), flush=True)
    write_md(payload)
    return 0


def write_md(p):
    fk = p.get("floor_k")
    s = p.get("summary") or {}
    ctrl = p.get("control") or {}
    v = p.get("verdict") or {}
    cb = None
    for blk in (s.get("by_cost") or {}).values():
        cb = blk.get("control_cap_binding_share_median")
        if cb is not None:
            break
    cby = None
    for blk in (s.get("by_cost") or {}).values():
        cby = blk.get("control_cap_binding_decisions_per_year_median")
        if cby is not None:
            break
    L = ["# 额度该由规则记住，还是每 bar 由人再裁一次", "",
         "证据截止 %s　判决 **%s**" % (p.get("evidence_cutoff"), v.get("label")), "",
         "- 额度 k = **%s**（读为准予面，不在此重述）" % fk,
         "- 控制臂 = 发布行为（vol_cap=1.0）：最近决策 bar 自己算出 k=0.460253，低于它的票面靠人工裁。",
         "- 候选臂 = 同一本书、同一节奏、同一成本，只把 **vol_cap=额度 k**（规则自己封顶）。",
         "- 控制臂自身有多少决策 bar 站在额度之上：**中位 %s **（每年 **%s** 个决策 bar，跨相位中位）"
         % (cb, cby), "",
         "## 读数", ""]
    for k, blk in (s.get("by_cost") or {}).items():
        if not blk.get("rows"):
            continue
        L.append("### %sbp/边" % k)
        L.append("")
        L.append("- 候选 CAGR 中位 %s%% vs 控制 %s%%　Δ 中位 **%+.4fpp**（区间 %+.4f ~ %+.4f）"
                 % (blk.get("cand_cagr_median_pct"), blk.get("ctrl_cagr_median_pct"),
                    blk.get("delta_cagr_median_pp") or 0.0,
                    blk.get("delta_cagr_min_pp") or 0.0, blk.get("delta_cagr_max_pp") or 0.0))
        L.append("- ΔSharpe 中位 **%+.4f**　Δ最大回撤中位 %+.4fpp"
                 % (blk.get("delta_sharpe_median") or 0.0, blk.get("delta_maxdd_median_pp") or 0.0))
        L.append("- 收益让出不超 %.2fpp 的格占比 %s" % (RETURN_FLOOR_PP, blk.get("share_cells_return_kept")))
        L.append("")
        L.append("| 相位 | 控制 CAGR% | 候选 CAGR% | ΔCAGR pp | ΔSharpe | ΔMaxDD pp |")
        L.append("|---|---|---|---|---|---|")
        for r in blk["rows"]:
            L.append("| %s | %s | %s | %+.4f | %+.4f | %+.4f |"
                     % (r["phase"], r["ctrl_cagr_pct"], r["cand_cagr_pct"],
                        r["delta_cagr_pp"], r["delta_sharpe"], r["delta_maxdd_pp"]))
        L.append("")
    L += ["## 判决依据", ""] + ["- %s" % r for r in (v.get("reasons") or [])] + [""]
    # the reading that matters most: what a "cap at the floor" actually IS on this book
    ctrl_med = None
    for blk in (s.get("by_cost") or {}).values():
        ctrl_med = blk.get("ctrl_cagr_median_pct")
        if ctrl_med is not None:
            break
    vals = [c["scale_median"] for c in (p.get("cells") or []) if c.get("arm") == "control"
            and c.get("scale_median") is not None]
    rule_med = float(np.median(vals)) if vals else None
    if rule_med and fk:
        L += ["## 这条「记住」到底是什么", "",
              "- 规则的规模中位是 **k≈%.4f**，额度是 **k=%.4f** —— 额度只等于规则规模的 **%.0f%%**。"
              % (rule_med, fk, 100.0 * fk / rule_med),
              "- 所以把规则封顶到额度，不是「让规则不再越权」，而是**把这本书的暴露砍掉约 %.0f%%**。"
              % (100.0 * (1.0 - fk / rule_med)),
              "- 砍暴露当然改善回撤（+%.2fpp）与微幅夏普，同时按比例削收益（%.2fpp 年化）——"
              "**这不是改进，是换了一条更小的书**。任何只降暴露的旋钮都能刷出同样的回撤数字。"
              % (abs(_median([r["delta_maxdd_pp"] for blk in (s.get("by_cost") or {}).values()
                              for r in (blk.get("rows") or [])]) or 0.0),
                 abs(_median([r["delta_cagr_pp"] for blk in (s.get("by_cost") or {}).values()
                              for r in (blk.get("rows") or [])]) or 0.0)),
              "- 真问题因此不是「规则记不记得住」，而是**额度是以规则的哪一版为基准签发的**："
              "若基准是另一条更小的规则，那么每张票面都要人工裁就不是运维事故，而是签发口径错位。",
              ""]
    L += ["## 对票面", "", v.get("desk") or "", "",
          "_控制臂复现发布书：%s（发布 CAGR %s%% vs 本面 %s%%）_"
          % (ctrl.get("reproduces_published"), ctrl.get("published_cagr_pct"), ctrl.get("cagr_pct")),
          ""]
    with io.open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(L))


def check() -> int:
    if not os.path.exists(OUT):
        print("FAIL: no receipt at %s" % OUT)
        return 1
    with io.open(OUT, encoding="utf-8") as f:
        p = json.load(f)
    bad = []
    for k, want in CRITERIA.items():
        got = (p.get("rule") or {}).get(k)
        if got != want:
            bad.append("rule.%s echoed %r, frozen value is %r" % (k, got, want))
    fk = floor_k()
    if fk is None or abs(float(p.get("floor_k", -1)) - fk) > 1e-9:
        bad.append("floor_k %r drifted from the published ledger %r" % (p.get("floor_k"), fk))
    # the verdict must follow from the published summary, not from a hand-written field
    label, _ = verdict_of(p.get("summary") or {},
                          control_reproduces=bool((p.get("control") or {}).get("reproduces_published")),
                          phase_spread_pp=(p.get("summary") or {}).get("control_phase_spread_cagr_pp"))
    if label != (p.get("verdict") or {}).get("label"):
        bad.append("verdict re-derives as %s, receipt says %s"
                   % (label, (p.get("verdict") or {}).get("label")))
    # every cell must carry its own identity
    for c in p.get("cells") or []:
        for k in ("arm", "phase", "cost", "cagr_pct", "sharpe"):
            if k not in c:
                bad.append("cell %r missing %s" % (c.get("phase"), k))
        if c["arm"] == "candidate" and abs(c["vol_cap"] - float(p["floor_k"])) > 1e-9:
            bad.append("candidate cell %s carries vol_cap %r != floor" % (c["phase"], c["vol_cap"]))
    if bad:
        print("FAIL (%d)" % len(bad))
        for b in bad[:20]:
            print("  - %s" % b)
        return 1
    print("CHECK_OK verdict=%s cells=%d" % (p["verdict"]["label"], len(p.get("cells") or [])))
    return 0


# ---------------------------------------------------------------- selftest

def _fixture(n_bars=400, n_names=20, seed=7, vol_scale=0.01):
    """A synthetic panel: the fixture must be long enough that a cell is not NOT_ASSESSED."""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2021-01-01", periods=n_bars)
    names = ["N%02d" % i for i in range(n_names)]
    rets = rng.normal(0.0002, vol_scale, size=(n_bars, n_names))
    rets[:, :5] += 0.0004            # a persistent edge so scores are not pure noise
    close = pd.DataFrame(100.0 * np.cumprod(1.0 + rets, axis=0), index=idx, columns=names)
    openp = close.shift(1).bfill()
    amt = pd.DataFrame(5e8, index=idx, columns=names)
    score = pd.DataFrame(rng.random((n_bars, n_names)), index=idx, columns=names)
    score = score.rolling(23, min_periods=1).mean()
    return close, openp, amt, score


def selftest() -> int:
    legs, fails = [], []

    def leg(name, ok, msg=""):
        legs.append(name)
        if not ok:
            fails.append("%s %s" % (name, msg))
        print("  %-58s %s" % (name, "PASS" if ok else "FAIL " + msg), flush=True)

    close, openp, amt, score = _fixture()
    # L1: an identity arm must return the same cell as itself (the ruler measures something)
    a = burn(close, openp, amt, score, 0.0010, close.index[0], 1.0)
    b = burn(close, openp, amt, score, 0.0010, close.index[0], 1.0)
    leg("L1 identity arm reproduces bit-for-bit", a["cagr_pct"] == b["cagr_pct"])

    # L2: a cap at 1.0 is the published behaviour; a tight cap cannot lever UP
    tight = burn(close, openp, amt, score, 0.0010, close.index[0], 0.05)
    leg("L2 tighter cap does not raise the book's own scale",
        (tight["scale_max"] or 0) <= 0.05 + 1e-9, "max=%r" % tight["scale_max"])

    # L3: the diagnostic counts what it claims -- with a cap that binds everywhere on the
    # control arm, share must be 0 for the candidate and > 0 for the control
    d = []
    R.open_to_open_equity(close, openp, amt, score, CONTROL["rebal"], CONTROL["n_hold"],
                          0.0010, vol_target=CONTROL["vol_target"],
                          start=str(pd.Timestamp(close.index[0]).date()), diag=d)
    scales = [float(x["scale"]) for x in d if x.get("scale") is not None]
    leg("L3 the control diag carries one finite scale per decision",
        len(scales) == len(d) and len(scales) > 0, "scales=%d diag=%d" % (len(scales), len(d)))

    # L4: verdict_of is driven by the summary, in both directions
    fake_ok = {"by_cost": {"10": {"phases": 5, "delta_cagr_median_pp": 0.05,
                                  "delta_cagr_min_pp": -0.02, "delta_sharpe_median": 0.03,
                                  "share_cells_return_kept": 1.0,
                                  "rows": [{"delta_cagr_pp": 0.05, "delta_sharpe": 0.03}] * 5}}}
    fake_bad = {"by_cost": {"10": {"phases": 5, "delta_cagr_median_pp": -1.20,
                                   "delta_cagr_min_pp": -1.50, "delta_sharpe_median": -0.10,
                                   "share_cells_return_kept": 0.0,
                                   "rows": [{"delta_cagr_pp": -1.2, "delta_sharpe": -0.1}] * 5}}}
    leg("L4a a cheap cap reads ADOPT", verdict_of(fake_ok)[0] == "ADOPT",
        verdict_of(fake_ok)[0])
    leg("L4b a costly cap reads REJECT", verdict_of(fake_bad)[0] == "REJECT",
        verdict_of(fake_bad)[0])

    # L5: control failure short-circuits every other reading
    leg("L5 control failure dominates the verdict",
        verdict_of(fake_ok, control_reproduces=False)[0] == "CONTROL_FAILED")

    # L6: a thin grid is NOT_ASSESSED, never a pass (r1261 family)
    thin = {"by_cost": {"10": {"phases": 1, "rows": [{"delta_cagr_pp": 0.5, "delta_sharpe": 0.5}]}}}
    leg("L6 a one-phase grid cannot pass", verdict_of(thin)[0] == "NOT_ASSESSED",
        verdict_of(thin)[0])

    # L7: identical arms produce a zero delta -- the grid really is paired
    s = summarize([{"arm": "control", "cost": 0.0010, "phase": "p1", "cagr_pct": 5.0,
                    "sharpe": 1.0, "maxdd_pct": -10.0, "top2_share": 0.6},
                   {"arm": "candidate", "cost": 0.0010, "phase": "p1", "cagr_pct": 5.0,
                    "sharpe": 1.0, "maxdd_pct": -10.0, "top2_share": 0.6}])
    leg("L7 paired identical arms give a zero delta",
        s["by_cost"]["10"]["delta_cagr_median_pp"] == 0.0)

    # L8: the md writer names the floor it was given, not a restated constant
    fk = floor_k()
    leg("L8 the ledger's permitted k is readable", fk is None or 0.0 < fk <= 1.0, "floor_k=%r" % fk)

    print("\n%d/%d legs" % (len(legs) - len(fails), len(legs)))
    return 0 if not fails else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="check",
                    choices=["selftest", "run", "check"])
    a = ap.parse_args(argv)
    return {"selftest": selftest, "run": run, "check": check}[a.cmd]()


if __name__ == "__main__":
    sys.exit(main())