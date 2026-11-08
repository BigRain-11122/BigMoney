#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""should the book move to a 10-bar decision grid? price the rule, not the one lucky sequence

WHY THIS FILE EXISTS
--------------------
r1461 priced three knobs against the frozen year gate and found exactly one arm that
passes Y4: rebalance 10 bars (ADMIT, 12.17%/yr, top-2 0.6846 against the 70% line). The
same receipt then said the arm is CONDITIONAL at 20bp/side, and its own footer asked for
this round to do two things before anyone changes the production cell: re-verify at
double cost, and put the candidate through an adoption round.

An adoption round means the arm has to survive the thing that killed the last three
"improvements": r1325 showed a rule that looked free on one decision sequence reversed
sign on three of four other phases, and r1426/r1449 showed a single phase's verdict is not
a verdict. So this file prices the RULE (20 bars -> 10 bars) on a phase grid, at two cost
assumptions, with the criteria frozen in code before the run.

WHAT IT DOES NOT DO
-------------------
It does not change the production cell. It publishes a verdict on the change:
  ADOPT              pass survives phases AND cost; the desk may switch
  COST_DEPENDENT     pass exists only at the 10bp assumption -> the knob is a cost bet
  PHASE_DEPENDENT    pass exists only on some decision calendars -> not a rule
  WITHIN_NOISE       the pass margin is smaller than the book's own phase spread
  REJECT             the change gives back return or risk-adjusted return
  NOT_ASSESSED       the grid is too thin to say anything (never read as a pass)
  CONTROL_FAILED     the control arm did not reproduce the published book

self  python scripts/etf_book_rebal_adoption.py selftest    # synthetic, fast
run   python scripts/etf_book_rebal_adoption.py run         # real panel, ~2 min
check python scripts/etf_book_rebal_adoption.py check       # re-derive from receipt
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
import candidate_year_gate as G
import etf_book_year_gate as YG               # the published calendar-year definition
import etf_book_concentration_levers as CL    # yearly_rows / cohorts_of / gate_of: one copy
from etf_book_buffer_adoption import phase_starts   # the phase ruler: one copy

OUT = os.path.join(ROOT, "results", "etf_book_rebal_adoption.json")
OUT_MD = os.path.join(ROOT, "research", "ETF_BOOK_REBAL_ADOPTION.md")
CONTROL_RECEIPT = os.path.join(ROOT, "results", "etf_nobond_vt.json")
YEAR_GATE_RECEIPT = os.path.join(ROOT, "results", "etf_book_year_gate", "YEAR-GATE.json")

# ---------------------------------------------------------------- frozen criteria
# Written before the first run. The receipt echoes them and `check` refuses a face that
# echoes different numbers, so a later "small adjustment" cannot be mistaken for the rule.
CONTROL = {"rebal": 20, "n_hold": 5, "cost": 0.0010, "vol_target": 0.08}
CANDIDATE_REBAL = 10
PHASE_REBAL = CANDIDATE_REBAL     # phases spread across the candidate's own cycle
N_PHASES = 5
COSTS = (0.0010, 0.0020)          # 10bp = the free band; 20bp = the stress assumption
COST_TOL = 5e-4                   # control CAGR reproduction tolerance (0.05pp)
PASS_SHARE_MIN = 0.60             # the gate must pass on at least this share of phases
RETURN_SHARE_MIN = 0.75           # share of cells where return may not fall materially
RETURN_FLOOR_PP = -0.15           # "materially" = worse than this per cell
MEDIAN_FLOOR_PP = -0.25           # median effect floor before the change is a toll
MIN_PHASES_PER_COST = 3           # below this a cost row is NOT_ASSESSED, never a pass

CRITERIA = {
    "control": CONTROL,
    "candidate_rebal": CANDIDATE_REBAL,
    "phase_rebal": PHASE_REBAL,
    "n_phases": N_PHASES,
    "costs_bp": [int(round(c * 10000)) for c in COSTS],
    "pass_share_min": PASS_SHARE_MIN,
    "return_share_min": RETURN_SHARE_MIN,
    "return_floor_pp": RETURN_FLOOR_PP,
    "median_floor_pp": MEDIAN_FLOOR_PP,
    "min_phases_per_cost": MIN_PHASES_PER_COST,
    "frozen": "written before the first run; `check` refuses a face that echoes other numbers",
}
VERDICTS = ("ADOPT", "COST_DEPENDENT", "PHASE_DEPENDENT", "WITHIN_NOISE",
            "REJECT", "NOT_ASSESSED", "CONTROL_FAILED")

UNITS = {
    "cagr_pct": "percent per year",
    "turnover": "sum |dw| per rebalance, fraction of book",
    "delta_cagr_pp": "percentage points of CAGR, candidate minus control on the same phase and cost",
    "top2_distance_pp": "(top-2 share - 0.70) * 100: positive means the gate is failed",
    "phase": "decision-grid start bar inside one 10-bar cycle",
}


# ---------------------------------------------------------------- mechanics

def burn(close, openp, amt, score, rebal, cost, start):
    """One (rule, phase, cost) cell through the production engine, plus its own years."""
    diag = []
    ser, turn = R.open_to_open_equity(close, openp, amt, score, rebal, CONTROL["n_hold"],
                                      cost, vol_target=CONTROL["vol_target"],
                                      start=str(pd.Timestamp(start).date()), diag=diag)
    st = A.stats2(ser, "cell")
    yrs = max(1e-9, (ser.index[-1] - ser.index[0]).days / 365.25)
    # The engine returns the MEAN |dw| per decision. Doubling the decision frequency
    # halves that mean and doubles the count, so a per-decision mean can read as "trades
    # less" while the book pays twice the fees. Both are published, named for what they are.
    per_decision = float(turn)
    decisions = len(diag)
    total_turnover = per_decision * decisions
    years = CL.yearly_rows(ser)
    g = CL.gate_of(years)
    top2 = g["metrics"].get("top2_share")
    return {
        "cagr_pct": round(float(st.get("cagr", float("nan"))) * 100.0, 4),
        "sharpe": round(float(st.get("sharpe", float("nan"))), 4),
        "maxdd_pct": round(float(st.get("maxdd", float("nan"))) * 100.0, 4),
        "turnover_per_decision": round(per_decision, 6),
        "decisions": decisions,
        "turnover_total": round(total_turnover, 4),
        "turnover_per_year": round(total_turnover / yrs, 4),
        "verdict": g["verdict"],
        "checks": g["checks"],
        "top2_share": (None if top2 is None else round(float(top2), 4)),
        "top2_distance_pp": (None if top2 is None
                             else round((float(top2) - G.TOP2_SHARE_MAX) * 100.0, 4)),
        "years": g["years"],
    }


def _key(cost: float) -> str:
    """The by-cost key, derived once: 0.0010 -> "10". Never spelled by hand."""
    return str(int(round(cost * 10000)))


def _by(cells, rule, cost):
    return sorted([c for c in cells if c["rule"] == rule and abs(c["cost"] - cost) < 1e-9],
                  key=lambda c: c["phase"])


def _iqr(values):
    v = [x for x in values if x is not None]
    if len(v) < 2:
        return None
    return float(np.subtract(*np.percentile(v, [75, 25])))


def summarize(cells, control_reproduces=True):
    """Per-cost pass shares, per-phase deltas, and the phase spread of the candidate."""
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
                "cand_cagr_pct": a["cagr_pct"], "ctrl_cagr_pct": b["cagr_pct"],
                "delta_cagr_pp": round(a["cagr_pct"] - b["cagr_pct"], 4),
                "delta_sharpe": round(a["sharpe"] - b["sharpe"], 4),
                "cand_verdict": a["verdict"], "ctrl_verdict": b["verdict"],
                "cand_top2_share": a["top2_share"], "cand_top2_distance_pp": a["top2_distance_pp"],
                "cand_turnover_per_decision": a["turnover_per_decision"],
                "ctrl_turnover_per_decision": b["turnover_per_decision"],
                "cand_turnover_per_year": a["turnover_per_year"],
                "ctrl_turnover_per_year": b["turnover_per_year"],
                "delta_turnover_per_decision": round(a["turnover_per_decision"]
                                                     - b["turnover_per_decision"], 6),
                "delta_turnover_per_year": round(a["turnover_per_year"]
                                                 - b["turnover_per_year"], 4),
            })
        n = len(rows)
        block = {
            "cost_bp": int(round(cost * 10000)),
            "n_phases": n,
            "assessed": n >= MIN_PHASES_PER_COST,
            "pass_share": (round(float(np.mean([r["cand_verdict"] == "ADMIT" for r in rows])), 4)
                           if n else None),
            "ctrl_pass_share": (round(float(np.mean([r["ctrl_verdict"] == "ADMIT" for r in rows])), 4)
                                if n else None),
            "median_delta_cagr_pp": (round(float(np.median([r["delta_cagr_pp"] for r in rows])), 4)
                                     if n else None),
            "worst_delta_cagr_pp": (round(float(min(r["delta_cagr_pp"] for r in rows)), 4)
                                    if n else None),
            "share_cagr_ok": (round(float(np.mean([r["delta_cagr_pp"] >= RETURN_FLOOR_PP
                                                   for r in rows])), 4) if n else None),
            "share_cagr_up": (round(float(np.mean([r["delta_cagr_pp"] > 0 for r in rows])), 4)
                              if n else None),
            "median_delta_sharpe": (round(float(np.median([r["delta_sharpe"] for r in rows])), 4)
                                    if n else None),
            "median_delta_turnover_per_decision": (
                round(float(np.median([r["delta_turnover_per_decision"] for r in rows])), 6)
                if n else None),
            "median_delta_turnover_per_year": (
                round(float(np.median([r["delta_turnover_per_year"] for r in rows])), 4)
                if n else None),
            "cand_top2_iqr": (round(_iqr([r["cand_top2_share"] for r in rows]), 4)
                              if _iqr([r["cand_top2_share"] for r in rows]) is not None else None),
            "cand_median_top2_distance_pp": (
                round(float(np.median([r["cand_top2_distance_pp"] for r in rows
                                       if r["cand_top2_distance_pp"] is not None])), 4)
                if any(r["cand_top2_distance_pp"] is not None for r in rows) else None),
            "rows": rows,
        }
        out["by_cost"][_key(cost)] = block
    # The fee the faster grid pays is not an assumption, it is arithmetic: extra units of
    # trading per year times the cost step between the two assumptions. Printing it next to
    # the measured CAGR shift lets a reader see whether they are the same size.
    free = out["by_cost"].get(_key(COSTS[0])) or {}
    paid = out["by_cost"].get(_key(COSTS[1])) or {}
    if (free.get("median_delta_turnover_per_year") is not None
            and free.get("median_delta_cagr_pp") is not None
            and paid.get("median_delta_cagr_pp") is not None):
        step = COSTS[1] - COSTS[0]
        extra_fee_pp = free["median_delta_turnover_per_year"] * step * 100.0
        out["cost_arithmetic"] = {
            "delta_turnover_per_year_median": free["median_delta_turnover_per_year"],
            "cost_step_bp": int(round(step * 10000)),
            "extra_fee_pp": round(extra_fee_pp, 4),
            "measured_cagr_shift_pp": round(free["median_delta_cagr_pp"]
                                            - paid["median_delta_cagr_pp"], 4),
            "edge_pp_at_10bp": free["median_delta_cagr_pp"],
            "fee_exceeds_edge": bool(extra_fee_pp >= abs(free["median_delta_cagr_pp"])),
        }
    return out


def verdict_of(summary, control_reproduces=True):
    """The frozen decision rule. Returns (label, reasons)."""
    if not control_reproduces:
        return "CONTROL_FAILED", ["the control arm did not reproduce the published book; nothing is claimed"]
    if not summary.get("n_cells"):
        return "NOT_ASSESSED", ["no cells -- an empty grid cannot support a verdict"]
    free = summary["by_cost"].get(_key(COSTS[0]))     # 10bp: the assumption the pass was found under
    paid = summary["by_cost"].get(_key(COSTS[1]))     # 20bp: the stress assumption
    if not free or not free["assessed"]:
        return "NOT_ASSESSED", ["fewer than %d phases at 10bp -- not a measurement"
                                % MIN_PHASES_PER_COST]
    reasons = []
    # 1) the change may not give back return or risk-adjusted return
    if (free["median_delta_cagr_pp"] is not None
            and free["median_delta_cagr_pp"] < MEDIAN_FLOOR_PP):
        return "REJECT", reasons + ["median return effect %+.2fpp is a toll (floor %+.2fpp)"
                                    % (free["median_delta_cagr_pp"], MEDIAN_FLOOR_PP)]
    if free["share_cagr_ok"] is not None and free["share_cagr_ok"] < RETURN_SHARE_MIN:
        return "REJECT", reasons + ["return falls in %.0f%% of phase cells (need no-worse in %.0f%%)"
                                    % (100 * (1 - free["share_cagr_ok"]),
                                       100 * RETURN_SHARE_MIN)]
    if free["median_delta_sharpe"] is not None and free["median_delta_sharpe"] < 0:
        return "REJECT", reasons + ["median Sharpe effect %+.3f: the pass is bought with risk"
                                    % free["median_delta_sharpe"]]
    # 2) the gate has to pass on more than one decision calendar
    if free["pass_share"] is None or free["pass_share"] < PASS_SHARE_MIN:
        # Two readings that must not be merged (E293): the LEVER may work in every cell
        # while the GATE PASS appears in only some of them. Say both.
        extra = ["the gate passes on only %.0f%% of %d phase cells (floor %.0f%%); the control "
                 "book passes %.0f%% of the same calendars, so the verdict word itself moves "
                 "with the phase"
                 % (100 * (free["pass_share"] or 0.0), free["n_phases"], 100 * PASS_SHARE_MIN,
                    100 * (free.get("ctrl_pass_share") or 0.0))]
        if free.get("share_cagr_up") is not None:
            extra.append("the return effect itself is %+.2fpp median and positive in %.0f%% of "
                         "cells, so the lever is not what fails -- the gate pass is"
                         % (free["median_delta_cagr_pp"], 100 * free["share_cagr_up"]))
        if paid and paid.get("median_delta_cagr_pp") is not None:
            extra.append("at 20bp/side the same change is %+.2fpp median, so the return edge is "
                         "a cost assumption as well" % paid["median_delta_cagr_pp"])
        ca = summary.get("cost_arithmetic")
        if ca:
            extra.append("the faster grid trades %+.2f more units per year, which at the %dbp "
                         "step costs %.2fpp -- against an edge of %+.2fpp (%s)"
                         % (ca["delta_turnover_per_year_median"], ca["cost_step_bp"],
                            ca["extra_fee_pp"], ca["edge_pp_at_10bp"],
                            "the fee is the same size as the edge"
                            if ca["fee_exceeds_edge"] else "the edge survives the extra fee"))
        return "PHASE_DEPENDENT", reasons + extra
    # 3) the margin has to be bigger than the book's own phase spread (E188/E433 ruler)
    if (free["cand_median_top2_distance_pp"] is not None
            and free["cand_top2_iqr"] is not None
            and free["cand_median_top2_distance_pp"] > -free["cand_top2_iqr"]):
        return "WITHIN_NOISE", reasons + [
            "median margin %.2fpp inside the phase spread %.4f (top-2 IQR)"
            % (free["cand_median_top2_distance_pp"], free["cand_top2_iqr"])]
    # 4) a pass that only exists at the low cost assumption is a bet, not a knob
    if paid is None or not paid["assessed"]:
        return "NOT_ASSESSED", reasons + ["no 20bp grid -- the cost dependence cannot be read"]
    if paid["pass_share"] is None or paid["pass_share"] < PASS_SHARE_MIN:
        return "COST_DEPENDENT", reasons + [
            "passes %.0f%% of phases at 10bp but only %.0f%% at 20bp/side"
            % (100 * free["pass_share"], 100 * (paid["pass_share"] or 0.0))]
    reasons.append("passes %.0f%% of phases at 10bp and %.0f%% at 20bp, median effect %+.2fpp, "
                   "median Sharpe %+.3f"
                   % (100 * free["pass_share"], 100 * paid["pass_share"],
                      free["median_delta_cagr_pp"], free["median_delta_sharpe"]))
    return "ADOPT", reasons


# ---------------------------------------------------------------- render

def render_md(payload) -> str:
    c = payload["control"]
    s = payload["summary"]
    srow = payload["verdict"]
    lines = [
        "# 把调仓改成 10 日？——先给这条规则做采纳轮",
        "",
        "> 面：`results/etf_book_rebal_adoption.json` ｜ 脚本：`scripts/etf_book_rebal_adoption.py`"
        " ｜ 面板截止：%s ｜ 判据在首跑前冻结" % payload["evidence_cutoff"],
        "",
        "## 一句话",
        "",
        "%s —— %s" % (srow["label"], "；".join(srow["reasons"])),
        "",
        "## 控制臂复现",
        "",
        "| 项 | 值 |",
        "| --- | --- |",
        "| 本轮控制臂 CAGR | %.4f%% |" % c["cagr_pct"],
        "| 已发布 nobond_vt08 | %s |" % (("%.4f%%" % c["published_cagr_pct"])
                                           if c.get("published_cagr_pct") is not None else "不可读"),
        "| 逐年行逐位相等 | %s |" % ("是" if not c.get("published_year_gaps_pp") else
                                     "否 %r" % c["published_year_gaps_pp"]),
        "",
        "## 相位 × 成本网格",
        "",
        "| 成本 | 相位数 | 候选过 Y4 占比 | 控制过 Y4 占比 | 中位 ΔCAGR | 最差 ΔCAGR "
        "| 收益不降占比 | 中位 ΔSharpe | 中位 Δ年换手 | 中位 Δ每决策换手 "
        "| 候选 top-2 相位 IQR | 中位到线距离 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for k in sorted(s.get("by_cost", {})):
        b = s["by_cost"][k]
        def pc(v):
            return "—" if v is None else ("%.0f%%" % (100 * v))
        lines.append("| %sbp | %d | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            b["cost_bp"], b["n_phases"], pc(b["pass_share"]), pc(b["ctrl_pass_share"]),
            "—" if b["median_delta_cagr_pp"] is None else "%+.2fpp" % b["median_delta_cagr_pp"],
            "—" if b["worst_delta_cagr_pp"] is None else "%+.2fpp" % b["worst_delta_cagr_pp"],
            pc(b["share_cagr_ok"]),
            "—" if b["median_delta_sharpe"] is None else "%+.3f" % b["median_delta_sharpe"],
            "—" if b["median_delta_turnover_per_year"] is None
            else "%+.3f" % b["median_delta_turnover_per_year"],
            "—" if b["median_delta_turnover_per_decision"] is None
            else "%+.4f" % b["median_delta_turnover_per_decision"],
            "—" if b["cand_top2_iqr"] is None else "%.4f" % b["cand_top2_iqr"],
            "—" if b["cand_median_top2_distance_pp"] is None
            else "%+.2fpp" % b["cand_median_top2_distance_pp"]))
    ca = s.get("cost_arithmetic")
    if ca:
        lines += ["", "**成本算术**：更快的网格每年多交易 %+.2f 个单位，按 %dbp 的假设差就是 "
                  "%.2fpp——而这条规则在 10bp 下的中位收益优势是 %+.2fpp（%s）；实测两档成本间的"
                  "中位 CAGR 位移是 %+.2fpp。"
                  % (ca["delta_turnover_per_year_median"], ca["cost_step_bp"],
                     ca["extra_fee_pp"], ca["edge_pp_at_10bp"],
                     "手续费与优势同量级" if ca["fee_exceeds_edge"] else "优势盖过手续费",
                     ca["measured_cagr_shift_pp"])]
    lines += ["", "逐相位行见 JSON 的 `summary.by_cost.<bp>.rows`。", "",
              "## 判据（首跑前冻结）", ""]
    for k, v in payload["rule"].items():
        if k in ("control",):
            lines.append("- `%s` = %r" % (k, v))
            continue
        lines.append("- `%s` = %r" % (k, v))
    lines += ["", "## 这份回执不主张什么", ""]
    lines += ["- %s" % h for h in payload["honest"]]
    lines += ["", "## 结论对票面的意义", "",
              payload["desk_sentence"], ""]
    return "\n".join(lines)


# ---------------------------------------------------------------- run

def run() -> int:
    t0 = time.time()
    close, openp, amt, feats = E.build_panel()
    close, openp, n_flip = A.repair_flips(close, openp)
    cmap = A.load_class_map()
    cls = A.classify(close.columns, cmap, close)
    want = ("equity", "commodity", "convertible")     # the adopted book is bond-free
    cols = [c for c in close.columns if cls[c] in want]
    sc = E.build_score(close[cols], amt[cols], feats)
    print("bond-free universe %d (flips repaired %d)" % (len(cols), n_flip), flush=True)

    starts = phase_starts(close.index, rebal=PHASE_REBAL, n=N_PHASES)
    print("phases: %s" % [str(pd.Timestamp(d).date()) for d in starts], flush=True)

    cells = []
    for cost in COSTS:
        for start in starts:
            for rule, rebal in (("control", CONTROL["rebal"]),
                                ("candidate", CANDIDATE_REBAL)):
                r = burn(close[cols], openp[cols], amt[cols], sc, rebal, cost, start)
                r.update({"rule": rule, "rebal": rebal, "cost": cost,
                          "phase": str(pd.Timestamp(start).date())})
                cells.append(r)
                print("  %-9s %sbp %s cagr %7.4f sharpe %5.3f top2 %s %s"
                      % (rule, int(round(cost * 10000)), r["phase"], r["cagr_pct"],
                         r["sharpe"], r["top2_share"], r["verdict"]), flush=True)

    # ---- control reproduction on the published definition, before anything is claimed
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
    pub_years = CL.published_yearly_rows() if os.path.exists(YEAR_GATE_RECEIPT) else None
    gaps = {}
    if ctrl is not None:
        for y, want_pct in (pub_years or {}).items():
            got = next((r["net_pct"] for r in ctrl["years"] if r["year"] == y), None)
            if got is None:
                gaps[y] = None
            elif abs(got - want_pct) > 1e-2:
                gaps[y] = round(got - want_pct, 4)
        ctrl.update({"published_cagr_pct": published_cagr,
                     "published_yearly_pct": pub_years,
                     "published_year_gaps_pp": gaps})
        ctrl["reproduces_published"] = bool(
            published_cagr is not None
            and abs(ctrl["cagr_pct"] - published_cagr) <= COST_TOL * 100
            and pub_years and not gaps)
    reproduces = bool(ctrl and ctrl.get("reproduces_published"))
    print("control cagr %.4f vs published %r reproduces=%s"
          % ((ctrl or {}).get("cagr_pct", float("nan")), published_cagr, reproduces), flush=True)

    s = summarize(cells, control_reproduces=reproduces)
    label, reasons = verdict_of(s, control_reproduces=reproduces)

    free = s.get("by_cost", {}).get(_key(COSTS[0])) or {}
    paid = s.get("by_cost", {}).get(_key(COSTS[1])) or {}
    desk = {
        "ADOPT": "对票面：可以改 10 日调仓，但改的是排程常数，不是额度；11-11 前改需重跑 floor_ledger。",
        "COST_DEPENDENT": ("对票面：不改。这条 pass 只在 10bp/边下存在，20bp/边就掉线——"
                           "真实成交成本一旦接近 20bp，它是收益错觉。"),
        "PHASE_DEPENDENT": ("对票面：不改。pass 只在部分决策日历上出现，换一个月末起点就消失，"
                            "那不是规则。"),
        "WITHIN_NOISE": "对票面：不改。阈值线让出的距离小于这本书自己的相位噪度，读数不可分。",
        "REJECT": "对票面：不改，且这条建议从候选池划线为已定价失败。",
        "NOT_ASSESSED": "对票面：不改，也不下结论——网格太薄。",
        "CONTROL_FAILED": "对票面：不改，本轮控制臂都没复现，什么都别说。",
    }.get(label, "对票面：不改。")

    payload = {
        "face": "etf_book_rebal_adoption",
        "asof": pd.Timestamp.now(tz="Asia/Shanghai").isoformat(timespec="seconds"),
        "evidence_cutoff": str(close.index[-1].date()),
        "question": "does moving the decision grid from 20 to 10 bars survive a phase grid and a cost shock?",
        "rule": dict(CRITERIA, units=UNITS),
        "control": ctrl,
        "cells": cells,
        "summary": s,
        "verdict": {"label": label, "reasons": reasons},
        "desk_sentence": desk,
        "honest": [
            "no cell is a forecast: every yearly row is that cell's own realised return",
            "the 2026 row is partial and counted raw by the frozen gate (r1418 convention)",
            "phases shift the decision calendar only; the judged window is the same panel",
            "10bp and 20bp are two assumptions, not two realities: the pass share at each cost is printed side by side",
            "the change is a schedule constant, not a size: the permission/floor arc is untouched",
            ("the control book itself passes Y4 on %.0f%% of the same calendars: a verdict word "
             "about this gate is a phase draw before it is a property of a book"
             % (100 * (free.get("ctrl_pass_share") or 0.0))),
        ],
        "elapsed_sec": round(time.time() - t0, 1),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    with io.open(OUT_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write(render_md(payload))
    print("[run] %s | %s" % (label, reasons), flush=True)
    print("saved", OUT, flush=True)
    return 0 if reproduces else 1


def check() -> int:
    """Re-derive the verdict, the frozen criteria echo and every cell verdict."""
    if not os.path.exists(OUT):
        print("[check] no receipt at %s" % OUT)
        return 1
    with io.open(OUT, encoding="utf-8") as f:
        rec = json.load(f)
    errs = []
    for k, v in CRITERIA.items():
        if rec.get("rule", {}).get(k) != v:
            errs.append("criteria %s = %r != frozen %r" % (k, rec.get("rule", {}).get(k), v))
    for c in rec.get("cells", []):
        g = CL.gate_of({r["year"]: {"net_pct": r["net_pct"], "cohorts": r["cohorts"]}
                        for r in c["years"]})
        if g["verdict"] != c["verdict"]:
            errs.append("%s/%sbp/%s: verdict %s != re-derived %s"
                        % (c["rule"], int(round(c["cost"] * 10000)), c["phase"],
                           c["verdict"], g["verdict"]))
        for k, v in g["checks"].items():
            if bool(v) != bool(c["checks"][k]):
                errs.append("%s/%sbp/%s: %s %r != re-derived %r"
                            % (c["rule"], int(round(c["cost"] * 10000)), c["phase"], k,
                               c["checks"][k], v))
    reproduces = bool((rec.get("control") or {}).get("reproduces_published"))
    s2 = summarize(rec["cells"], control_reproduces=reproduces)
    label2, _r = verdict_of(s2, control_reproduces=reproduces)
    if label2 != rec["verdict"]["label"]:
        errs.append("verdict %s != re-derived %s" % (rec["verdict"]["label"], label2))
    if not reproduces:
        errs.append("control did not reproduce the published book")
    if errs:
        for e in errs:
            print("[check] DRIFT", e)
        return 1
    ca_pub = rec["summary"].get("cost_arithmetic")
    ca_new = s2.get("cost_arithmetic")
    if bool(ca_pub) != bool(ca_new):
        errs.append("cost arithmetic present in one derivation only")
    elif ca_pub:
        for k in ca_pub:
            if ca_pub[k] != ca_new.get(k):
                errs.append("cost_arithmetic %s %r != re-derived %r"
                            % (k, ca_pub[k], ca_new.get(k)))
    free = s2["by_cost"][_key(COSTS[0])]
    print("[check] CHECK_OK  verdict=%s  cells=%d  phases=%d  pass_share_10bp=%.2f"
          % (label2, len(rec["cells"]), free["n_phases"], free["pass_share"] or 0.0))
    return 0


# ---------------------------------------------------------------- selftest

def _cell(rule, phase, cost, verdict="ADMIT", cagr=12.0, sharpe=1.16, top2=0.66,
          turnover=0.20, decisions=60):
    """Synthetic cell. `turnover` is per decision; the total is derived the same way the
    engine's caller derives it, so a fixture cannot invent a total the real face lacks."""
    return {"rule": rule, "phase": phase, "cost": cost, "verdict": verdict,
            "cagr_pct": cagr, "sharpe": sharpe, "maxdd_pct": -11.0,
            "turnover_per_decision": turnover, "decisions": decisions,
            "turnover_total": round(turnover * decisions, 4),
            "turnover_per_year": round(turnover * decisions / 5.8, 4),
            "top2_share": top2,
            "top2_distance_pp": round((top2 - G.TOP2_SHARE_MAX) * 100.0, 4),
            "checks": {}, "years": []}


def selftest() -> int:
    legs = []

    def leg(name, ok, extra=""):
        legs.append((name, bool(ok), extra))

    # A the phase ruler really moves the decision calendar
    idx = pd.date_range("2020-01-01", periods=60, freq="B")
    st = phase_starts(idx, start="2020-01-01", rebal=10, n=5)
    leg("A five distinct phases inside a 10-bar cycle", len(st) == 5 and len(set(st)) == 5,
        [str(pd.Timestamp(x).date()) for x in st])
    leg("A2 they are spread, not collapsed on bar 0", st[0] != st[1] and st[-1] > st[0], st[-1])

    # B a clean grid where the candidate passes everywhere at both costs reads ADOPT
    cells = []
    for cost in COSTS:
        for i in range(5):
            cells.append(_cell("control", "p%d" % i, cost, verdict="CONDITIONAL", cagr=11.5,
                               sharpe=1.10, top2=0.72))
            cells.append(_cell("candidate", "p%d" % i, cost, verdict="ADMIT", cagr=12.2,
                               sharpe=1.16, top2=0.66))
    s = summarize(cells)
    leg("B clean grid reads ADOPT", verdict_of(s)[0] == "ADOPT", verdict_of(s))

    # C the same pass that disappears at 20bp is a cost bet, not a knob
    cells_c = []
    for cost in COSTS:
        for i in range(5):
            v = "ADMIT" if cost < 0.0015 else "CONDITIONAL"
            cells_c.append(_cell("control", "p%d" % i, cost, verdict="CONDITIONAL", cagr=11.5,
                                 sharpe=1.10, top2=0.72))
            cells_c.append(_cell("candidate", "p%d" % i, cost, verdict=v, cagr=12.2,
                                 sharpe=1.16, top2=0.66 if v == "ADMIT" else 0.77))
    leg("C pass only at 10bp reads COST_DEPENDENT",
        verdict_of(summarize(cells_c))[0] == "COST_DEPENDENT", verdict_of(summarize(cells_c)))

    # D a pass on 2 of 5 calendars is not a rule
    cells_d = []
    for cost in COSTS:
        for i in range(5):
            v = "ADMIT" if i < 2 else "CONDITIONAL"
            cells_d.append(_cell("control", "p%d" % i, cost, verdict="CONDITIONAL", cagr=11.5,
                                 sharpe=1.10, top2=0.72))
            cells_d.append(_cell("candidate", "p%d" % i, cost, verdict=v, cagr=12.2,
                                 sharpe=1.16, top2=0.66 if v == "ADMIT" else 0.74))
    leg("D partial pass share reads PHASE_DEPENDENT",
        verdict_of(summarize(cells_d))[0] == "PHASE_DEPENDENT", verdict_of(summarize(cells_d)))

    # E return that falls in most cells is a toll, whatever the gate says
    cells_e = []
    for cost in COSTS:
        for i in range(5):
            cells_e.append(_cell("control", "p%d" % i, cost, verdict="ADMIT", cagr=12.0,
                                 sharpe=1.10, top2=0.66))
            cells_e.append(_cell("candidate", "p%d" % i, cost, verdict="ADMIT", cagr=10.5,
                                 sharpe=1.05, top2=0.60))
    leg("E a 1.5pp/yr toll reads REJECT", verdict_of(summarize(cells_e))[0] == "REJECT",
        verdict_of(summarize(cells_e)))

    # F a pass bought with risk-adjusted return is a rejection too
    cells_f = []
    for cost in COSTS:
        for i in range(5):
            cells_f.append(_cell("control", "p%d" % i, cost, verdict="CONDITIONAL", cagr=11.9,
                                 sharpe=1.20, top2=0.72))
            cells_f.append(_cell("candidate", "p%d" % i, cost, verdict="ADMIT", cagr=12.1,
                                 sharpe=1.02, top2=0.66))
    leg("F lower Sharpe reads REJECT", verdict_of(summarize(cells_f))[0] == "REJECT",
        verdict_of(summarize(cells_f)))

    # G a margin thinner than the book's own phase spread is not a measurement
    cells_g = []
    for cost in COSTS:
        for i in range(5):
            cells_g.append(_cell("control", "p%d" % i, cost, verdict="CONDITIONAL", cagr=11.5,
                                 sharpe=1.10, top2=0.72))
            cells_g.append(_cell("candidate", "p%d" % i, cost, verdict="ADMIT", cagr=12.2,
                                 sharpe=1.16, top2=0.69 + 0.02 * i))
    leg("G margin inside the phase spread reads WITHIN_NOISE",
        verdict_of(summarize(cells_g))[0] == "WITHIN_NOISE", verdict_of(summarize(cells_g)))

    # H an empty or thin grid is never a pass
    leg("H empty grid is NOT_ASSESSED", verdict_of(summarize([]))[0] == "NOT_ASSESSED",
        verdict_of(summarize([])))
    thin = [c for c in cells if c["phase"] in ("p0", "p1")]
    leg("H2 two phases are not a measurement",
        verdict_of(summarize(thin))[0] == "NOT_ASSESSED", verdict_of(summarize(thin)))

    # I a control that did not reproduce wins over every other reading
    leg("I control failure wins", verdict_of(s, control_reproduces=False)[0] == "CONTROL_FAILED")

    # J a same-frequency pair reports zero trading change in both units
    j = summarize(cells)["by_cost"][_key(COSTS[0])]
    leg("J equal books show no trading change",
        j["median_delta_turnover_per_decision"] == 0.0
        and j["median_delta_turnover_per_year"] == 0.0,
        [j["median_delta_turnover_per_decision"], j["median_delta_turnover_per_year"]])

    # K a faster grid halves the per-decision move while DOUBLING the yearly one: the
    # two units must disagree, that is what makes printing only the first one a lie.
    cells_k = []
    for cost in COSTS:
        for i in range(5):
            cells_k.append(_cell("control", "p%d" % i, cost, verdict="CONDITIONAL", cagr=11.5,
                                 sharpe=1.10, top2=0.72, turnover=0.20, decisions=60))
            cells_k.append(_cell("candidate", "p%d" % i, cost, verdict="ADMIT", cagr=12.2,
                                 sharpe=1.16, top2=0.66, turnover=0.11, decisions=120))
    ck = summarize(cells_k)["by_cost"][_key(COSTS[0])]
    leg("K a faster grid trades less per decision and more per year",
        ck["median_delta_turnover_per_decision"] < 0
        and ck["median_delta_turnover_per_year"] > 0,
        [ck["median_delta_turnover_per_decision"], ck["median_delta_turnover_per_year"]])

    # L the fee arithmetic is arithmetic: a grid that trades 2 units/yr more at a 10bp
    # step pays 0.20pp, and the flag says whether that is as large as the measured edge.
    cells_l = []
    for cost in COSTS:
        for i in range(5):
            cells_l.append(_cell("control", "p%d" % i, cost, verdict="CONDITIONAL", cagr=11.5,
                                 sharpe=1.10, top2=0.72, turnover=0.20, decisions=60))
            cells_l.append(_cell("candidate", "p%d" % i, cost, verdict="ADMIT", cagr=12.1,
                                 sharpe=1.16, top2=0.66, turnover=0.20, decisions=66))
    al = summarize(cells_l).get("cost_arithmetic") or {}
    leg("L extra turnover is priced against the measured edge",
        al and al["extra_fee_pp"] > 0
        and al["fee_exceeds_edge"] == (al["extra_fee_pp"] >= abs(al["edge_pp_at_10bp"])),
        al)

    ok = sum(1 for _n, o, _e in legs if o)
    for name, o, extra in legs:
        if not o:
            print("[FAIL] %s %s" % (name, extra))
    print("selftest: %d/%d PASS" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


def main(argv) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", nargs="?", default="selftest", choices=["run", "check", "selftest"])
    a = ap.parse_args(argv)
    if a.cmd == "run":
        return run()
    if a.cmd == "check":
        return check()
    return selftest()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))