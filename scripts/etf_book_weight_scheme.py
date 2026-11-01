"""ETF book -- is the picks-to-weights rule worth anything?

Every face built so far on this book answers a question about *which* names it holds and
*when* it trades: wider/narrower width (E291), the incumbent buffer (E188), the volatility
window (E24), exposure ladders (E23), fill slicing (E27). All of them sit on top of one
unexamined line of the engine:

    w = {p: 1.0 / n_hold for p in picks}

Equal weight. Nobody has ever asked whether splitting the same picks by risk instead of by
count is worth money. That is the last structural knob left, and it is a cheap one to
price: the picks, the panel, the sizing overlay and the cost model all stay fixed; only the
weights inside the book change.

Two alternative rules are priced against it, both causal (they may only see bars <= d):

  * inv_vol -- w_i proportional to 1 / sigma_i (backward 60-bar open-to-open vol)
  * erc     -- equal risk contribution solved from the same backward covariance

Path dependence is the reason a single run cannot decide it (E188/E188-path): the weights
change turnover, turnover changes the cost paid, and the cost paid changes the path. So
every scheme is priced on

  * 3 books -- (12, 20) the production cell, (12, 10), (12, 40) (same width, other grids)
  * 4 phases -- decision grids started at four bars inside one 20-bar cycle,

and the verdict asks whether the improvement survives most cells, not whether one cell wins.

WHY THE CRITERIA SIT ABOVE THE CODE: the verdict rule is frozen as constants before the
first run and echoed into the payload, so a face built under different thresholds is RED
rather than quietly re-tuned. `--check` recomputes the verdict from the published summary
instead of trusting it.

The identity arm is the load-bearing one: the equal-weight scheme goes through the same
hook machinery as the alternatives and must reproduce the engine's own published cell
bit-for-bit. If it does not, the hook is a second engine and nothing here is measurable.

Usage:
    python scripts/etf_book_weight_scheme.py run [--out=...]
    python scripts/etf_book_weight_scheme.py --check
    python scripts/etf_book_weight_scheme.py --selftest
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import numpy as np
import pandas as pd

import etf_robust_pf as R
import etf_equity_alpha as A
import etf_book_hysteresis as H
from scripts import etf_book_production as P

OUT_JSON = ROOT / "results" / "etf_book_weight_scheme.json"
OUT_MD = ROOT / "research" / "ETF_BOOK_WEIGHT_SCHEME.md"
PRODUCTION_FACE = ROOT / "results" / "etf_book_production" / "latest.json"

SCRIPT = "scripts/etf_book_weight_scheme.py"
FACE = "results/etf_book_weight_scheme.json"

# ---------------------------------------------------------------- frozen criteria
# Written before the first run. The payload echoes these, and --check refuses a face whose
# echoed criteria differ from this file.
CONFIGS = ((12, 20), (12, 10), (12, 40))   # (n_hold, rebal): production cell + two neighbours
SCHEMES = ("equal", "inv_vol", "erc")
TESTS = ("inv_vol", "erc")                 # schemes the verdict is asked about
N_PHASES = 4
PHASE_REBAL = 20

VOL_WINDOW = 60          # backward window used by both risk rules (engine's own vol_window)
RISK_FLOOR = 1e-6        # a zero-vol name would otherwise get an infinite weight
ERC_ITERS = 200
ERC_TOL = 1e-9

SHARPE_SHARE_MIN = 0.75      # share of cells where the scheme's Sharpe >= equal
MEDIAN_SHARPE_MIN = 0.02     # median Sharpe effect must be materially positive
CAGR_SHARE_MIN = 0.80        # share of cells where CAGR must not fall
CAGR_SHARE_FLOOR_PP = -0.15  # "did not fall" = no worse than this per cell
MEDIAN_CAGR_FLOOR_PP = -0.05
MEDIAN_MAXDD_FLOOR_PP = 1.0  # median maxDD may not be worse than 1pp (delta is signed, shallow>0)

COST = H.COST
TARGET_VOL = H.TARGET_VOL
CONTROL_TOL = 0.005          # 0.5pp, r1297 law

CRITERIA = {
    "configs": [list(c) for c in CONFIGS],
    "schemes": list(SCHEMES),
    "tests": list(TESTS),
    "n_phases": N_PHASES,
    "vol_window": VOL_WINDOW,
    "sharpe_share_min": SHARPE_SHARE_MIN,
    "median_sharpe_min": MEDIAN_SHARPE_MIN,
    "cagr_share_min": CAGR_SHARE_MIN,
    "cagr_share_floor_pp": CAGR_SHARE_FLOOR_PP,
    "median_cagr_floor_pp": MEDIAN_CAGR_FLOOR_PP,
    "median_maxdd_floor_pp": MEDIAN_MAXDD_FLOOR_PP,
    "frozen": "constants above were written before the first run; --check refuses a face that echoes others",
}
VERDICTS = ("ADOPT", "REJECT")

UNITS = {
    "cagr": "fraction per year (0.0960 = 9.60%/yr)",
    "sharpe": "annualised excess over zero, per unit of vol",
    "maxdd": "negative fraction of peak (shallower = closer to 0)",
    "delta_pp": "percentage points, scheme minus equal weight in the same cell",
    "phase": "decision-grid start bar inside one rebalance cycle (4 per book)",
}


# ---------------------------------------------------------------- weight rules
def _backward_window(rets, d, window=VOL_WINDOW):
    """Returns strictly up to and including bar `d` -- the hook's only data."""
    win = rets.loc[:d].tail(window)
    return win if win.shape[0] >= 20 else None


def make_weights(scheme, rets, window=VOL_WINDOW):
    """Build a causal weight_hook for `scheme`. Falls back to equal on a degenerate window.

    The fallback is not silent: it is counted on the closure (`degenerate`), because a rule
    that quietly reverts to the baseline in half the cells is the baseline wearing a name.
    """
    state = {"degenerate": 0, "decisions": 0}

    def _equal(picks):
        return {p: 1.0 / len(picks) for p in picks}

    def hook(picks, d):
        state["decisions"] += 1
        if scheme == "equal":
            return _equal(picks)
        win = _backward_window(rets, d, window)
        if win is None or not set(picks) <= set(win.columns):
            state["degenerate"] += 1
            return _equal(picks)
        sd = win[list(picks)].std(ddof=1).to_numpy(dtype=float)
        sd = np.where(np.isfinite(sd) & (sd > RISK_FLOOR), sd, RISK_FLOOR)
        if scheme == "inv_vol":
            w = 1.0 / sd
        elif scheme == "erc":
            w = _erc(win[list(picks)].cov().to_numpy(dtype=float), sd)
        else:
            raise ValueError("unknown scheme %r" % (scheme,))
        if not np.all(np.isfinite(w)) or w.sum() <= 0 or float(np.min(w)) < 0:
            state["degenerate"] += 1
            return _equal(picks)
        w = w / w.sum()
        return {p: float(v) for p, v in zip(picks, w)}

    hook.state = state
    return hook


def _shrink(cov):
    """Ridge a sample covariance toward its diagonal.

    A singular/ill-conditioned sample covariance is the normal case for 5-12 names on 60
    bars; shrinking keeps the ERC solve defined instead of exploding. Exposed so the
    selftest measures risk contributions on the SAME matrix the solver used -- testing
    against the raw matrix would report a solver that equalises correctly as broken.
    """
    n = cov.shape[0]
    dg = np.diag(np.diag(cov))
    ridge = 1e-6 * float(np.trace(dg)) / n if np.trace(dg) > 0 else 1e-12
    return 0.5 * cov + 0.5 * dg + np.eye(n) * ridge


def _erc(cov, sd_fallback):
    """Equal risk contribution weights from a backward covariance matrix.

    Fixed point w <- 1 / (Sigma w), renormalised; it is the standard long-only ERC
    iteration and only ever sees the backward window handed to it.
    """
    n = cov.shape[0]
    if n == 0 or not np.all(np.isfinite(cov)):
        return 1.0 / sd_fallback
    cov = _shrink(cov)
    w = 1.0 / sd_fallback
    w = w / w.sum()
    for _ in range(ERC_ITERS):
        mrc = cov @ w
        # a long-only book has no negative risk contributions: a sampled covariance can hand
        # back a negative marginal contribution on a 60-bar window, and 1/negative would move
        # weight to a name with the wrong sign. Floor at RISK_FLOOR instead of taking |mrc|.
        mrc = np.where(mrc > RISK_FLOOR, mrc, RISK_FLOOR)
        nxt = 1.0 / mrc
        nxt = nxt / nxt.sum()
        if np.max(np.abs(nxt - w)) < ERC_TOL:
            w = nxt
            break
        w = nxt
    w = np.clip(w, 0.0, None)
    tot = w.sum()
    return w / tot if tot > 0 else 1.0 / sd_fallback


# ---------------------------------------------------------------- mechanics
def phase_starts(index, start=R.START, rebal=PHASE_REBAL, n=N_PHASES):
    """`n` decision-grid starts spread evenly through one rebalance cycle."""
    post = [d for d in index if d >= pd.Timestamp(start)]
    if len(post) < rebal:
        raise ValueError("panel has %d bars after %s -- need at least %d" % (len(post), start, rebal))
    step = max(1, rebal // n)
    picks, seen = [], set()
    for i in range(n):
        d = post[min(i * step, len(post) - 1)]
        if d not in seen:
            seen.add(d)
            picks.append(d)
    if len(picks) < n:
        raise ValueError("only %d distinct phases in a %d-bar cycle" % (len(picks), rebal))
    return picks


def rets_from(openp, columns):
    return openp.reindex(columns=columns).pct_change()


def arm_metrics(close, openp, amt, score, scheme, n_hold, rebal, start):
    """One (book, phase, scheme) cell through the production engine."""
    hook = make_weights(scheme, rets_from(openp, close.columns))
    diag = []
    ser, turn = R.open_to_open_equity(close, openp, amt, score, rebal, n_hold, COST,
                                      vol_target=TARGET_VOL,
                                      start=str(pd.Timestamp(start).date()),
                                      diag=diag, weight_hook=hook)
    full = A.stats2(ser, "full")
    oos = A.stats2(ser[ser.index > pd.Timestamp("2023-12-31")], "oos")
    ddates = [str(pd.Timestamp(r["date"]).date()) for r in diag]
    return {
        "scheme": scheme, "n_hold": n_hold, "rebal": rebal,
        "cagr": full.get("cagr"), "sharpe": full.get("sharpe"),
        "maxdd": full.get("maxdd"), "vol": full.get("vol"),
        "oos_cagr": oos.get("cagr"), "oos_sharpe": oos.get("sharpe"),
        "turnover_per_decision": round(float(turn), 4), "decisions": len(diag),
        "degenerate_decisions": hook.state["degenerate"],
        "first_decision": ddates[0] if ddates else None,
        "last_decision": ddates[-1] if ddates else None,
    }


def _delta(arm, base):
    return {"cagr_pp": round(100 * ((arm["cagr"] or 0.0) - (base["cagr"] or 0.0)), 4),
            "sharpe": round((arm["sharpe"] or 0.0) - (base["sharpe"] or 0.0), 4),
            "turnover": round((arm["turnover_per_decision"] or 0.0)
                              - (base["turnover_per_decision"] or 0.0), 4),
            "maxdd_pp": round(100 * ((arm["maxdd"] or 0.0) - (base["maxdd"] or 0.0)), 4)}


def summarize(cells, scheme):
    """Per-cell deltas against that cell's own equal-weight arm."""
    idx = {(c["n_hold"], c["rebal"], c["phase"], c["scheme"]): c for c in cells}
    rows = []
    for (n_hold, rebal, phase, sc) in sorted(idx):
        if sc != scheme:
            continue
        base = idx.get((n_hold, rebal, phase, "equal"))
        arm = idx[(n_hold, rebal, phase, sc)]
        if base is None:
            continue
        d = _delta(arm, base)
        rows.append({"n_hold": n_hold, "rebal": rebal, "phase": phase,
                     "base_cagr": base["cagr"], "base_sharpe": base["sharpe"],
                     "arm_cagr": arm["cagr"], "arm_sharpe": arm["sharpe"],
                     "base_turnover": base["turnover_per_decision"],
                     "arm_turnover": arm["turnover_per_decision"],
                     "degenerate_decisions": arm["degenerate_decisions"],
                     "delta_cagr_pp": d["cagr_pp"], "delta_sharpe": d["sharpe"],
                     "delta_turnover": d["turnover"], "delta_maxdd_pp": d["maxdd_pp"]})
    if not rows:
        return {"scheme": scheme, "n_cells": 0, "degraded": "no cells"}
    cagr = np.array([r["delta_cagr_pp"] for r in rows])
    sharpe = np.array([r["delta_sharpe"] for r in rows])
    maxdd = np.array([r["delta_maxdd_pp"] for r in rows])
    turn = np.array([r["delta_turnover"] for r in rows])
    return {
        "scheme": scheme, "n_cells": len(rows),
        "share_sharpe_ok": round(float((sharpe > 0).mean()), 4),
        "share_cagr_ok": round(float((cagr >= CAGR_SHARE_FLOOR_PP).mean()), 4),
        "share_cagr_up": round(float((cagr > 0).mean()), 4),
        "median_cagr_pp": round(float(np.median(cagr)), 4),
        "median_sharpe": round(float(np.median(sharpe)), 4),
        "median_maxdd_pp": round(float(np.median(maxdd)), 4),
        "median_turnover": round(float(np.median(turn)), 4),
        "worst_cagr_pp": round(float(np.min(cagr)), 4),
        "best_cagr_pp": round(float(np.max(cagr)), 4),
        "degenerate_decisions_total": int(sum(r["degenerate_decisions"] for r in rows)),
    }


def verdict(summary):
    """Recomputed from a published summary -- never read off the face."""
    if not summary or summary.get("n_cells", 0) < len(CONFIGS) * N_PHASES:
        return "REJECT", ["cells missing: %r" % (summary.get("n_cells"),)]
    reasons = []
    if summary["share_sharpe_ok"] < SHARPE_SHARE_MIN:
        reasons.append("sharpe up in only %.0f%% of cells (need %.0f%%)"
                       % (100 * summary["share_sharpe_ok"], 100 * SHARPE_SHARE_MIN))
    if summary["median_sharpe"] < MEDIAN_SHARPE_MIN:
        reasons.append("median sharpe %+.3f (need %+.3f)"
                       % (summary["median_sharpe"], MEDIAN_SHARPE_MIN))
    if summary["share_cagr_ok"] < CAGR_SHARE_MIN:
        reasons.append("cagr held in only %.0f%% of cells (need %.0f%%)"
                       % (100 * summary["share_cagr_ok"], 100 * CAGR_SHARE_MIN))
    if summary["median_cagr_pp"] < MEDIAN_CAGR_FLOOR_PP:
        reasons.append("median cagr %+.2fpp (floor %+.2f)" % (summary["median_cagr_pp"], MEDIAN_CAGR_FLOOR_PP))
    if summary["median_maxdd_pp"] < -MEDIAN_MAXDD_FLOOR_PP:
        reasons.append("median maxdd %+.2fpp (worse than %.1fpp)" % (summary["median_maxdd_pp"], MEDIAN_MAXDD_FLOOR_PP))
    return ("ADOPT" if not reasons else "REJECT"), reasons


def build():
    close, openp, amt, score, _cls, _flip = P.prep_panel()
    starts = phase_starts(close.index)

    cells = []
    for (n_hold, rebal) in CONFIGS:
        for d in starts:
            for sc in SCHEMES:
                m = arm_metrics(close, openp, amt, score, sc, n_hold, rebal, d)
                m["phase"] = str(pd.Timestamp(d).date())
                cells.append(m)

    per_phase = {}
    for c in cells:
        if (c["n_hold"], c["rebal"], c["scheme"]) == (CONFIGS[0][0], CONFIGS[0][1], "equal"):
            per_phase[c["phase"]] = {"decisions": c["decisions"],
                                     "first": c["first_decision"], "last": c["last_decision"]}
    sigs = {(v["first"], v["last"]) for v in per_phase.values()}
    activity = {"phase_decisions": per_phase,
                "distinct_calendars": len(sigs) == len(per_phase),
                "n_phases": len(per_phase),
                "note": "counts may coincide across phases; the calendar is the signature"}
    if not activity["distinct_calendars"]:
        raise RuntimeError("phases collapsed onto one decision calendar: %r" % (per_phase,))

    summaries = {sc: summarize(cells, sc) for sc in TESTS}
    verdicts = {}
    for sc in TESTS:
        label, reasons = verdict(summaries[sc])
        verdicts[sc] = {"verdict": label, "reasons": reasons}

    control = {"published": None, "measured": None, "delta_pp": None, "within_tol": None}
    if PRODUCTION_FACE.exists():
        pub = json.loads(PRODUCTION_FACE.read_text(encoding="utf-8"))
        cell = (pub.get("backtest") or {}).get("n12_vt08")
        base0 = next((c for c in cells
                      if (c["n_hold"], c["rebal"], c["scheme"]) == (12, 20, "equal")
                      and c["phase"] == min(per_phase)), None)
        if cell and base0:
            control["published"] = cell["full"]["cagr"]
            control["measured"] = base0["cagr"]
            control["delta_pp"] = round(100 * (control["measured"] - control["published"]), 3)
            control["within_tol"] = abs(control["delta_pp"]) <= 100 * CONTROL_TOL
            control["published_maxdd"] = cell["full"]["maxdd"]
            control["measured_maxdd"] = base0["maxdd"]

    return {
        "tool": "etf_book_weight_scheme",
        "script": SCRIPT,
        "face": FACE,
        "evidence_cutoff": str(close.index[-1].date()),
        "criteria": CRITERIA,
        "units": UNITS,
        "activity": activity,
        "control": control,
        "cells": cells,
        "summaries": summaries,
        "verdicts": verdicts,
        "reading": _reading(summaries, verdicts, control),
    }


def _reading(summaries, verdicts, control):
    parts = []
    for sc in TESTS:
        s = summaries.get(sc) or {}
        v = verdicts.get(sc) or {}
        if not s.get("n_cells"):
            parts.append("%s: no cells" % sc)
            continue
        parts.append("%s -> %s (sharpe %+.3f median, up in %.0f%% of %d cells; cagr %+.2fpp median, "
                     "held in %.0f%%; turnover %+.3f/decision)"
                     % (sc, v.get("verdict"), s["median_sharpe"], 100 * s["share_sharpe_ok"],
                        s["n_cells"], s["median_cagr_pp"], 100 * s["share_cagr_ok"],
                        s["median_turnover"]))
    if control.get("within_tol") is False:
        parts.append("CONTROL OFF: equal-weight arm does not reproduce the published cell "
                     "(%+.3fpp) -- the hook is a second engine, nothing here is measurable"
                     % (control.get("delta_pp") or 0.0))
    return "; ".join(parts)


def check(face=None):
    doc = face or json.loads(OUT_JSON.read_text(encoding="utf-8"))
    problems = []
    if doc.get("criteria") != CRITERIA:
        problems.append("criteria echoed in the face differ from the frozen constants")
    ctl = doc.get("control") or {}
    if ctl.get("within_tol") is False:
        problems.append("control arm outside tolerance (%r pp)" % (ctl.get("delta_pp"),))
    for sc in TESTS:
        label, reasons = verdict((doc.get("summaries") or {}).get(sc) or {})
        claimed = ((doc.get("verdicts") or {}).get(sc) or {}).get("verdict")
        if claimed != label:
            problems.append("%s: face says %r, recomputation says %r" % (sc, claimed, label))
        if claimed == "ADOPT" and reasons:
            problems.append("%s: ADOPT with reasons %r" % (sc, reasons))
    if problems:
        print("etf_book_weight_scheme --check: %d problem(s)" % len(problems))
        for p in problems:
            print("  -", p)
        return 1
    print("etf_book_weight_scheme --check: OK (%s)"
          % ", ".join("%s=%s" % (sc, (doc["verdicts"][sc]["verdict"])) for sc in TESTS))
    return 0


def render_md(doc):
    L = []
    L.append("# ETF 书：把选出来的票「按风险」还是「按数量」分钱\n")
    L.append("> 自动生成：`%s` ｜ 证据截止 %s ｜ 判据冻结于代码常量（`--check` 会拒收回显不一致的面）\n"
             % (SCRIPT, doc["evidence_cutoff"]))
    L.append("## 为什么问这个\n")
    L.append("这本书此前所有的研究都在问「持哪几只、什么时候换」（名数、缓冲、波动窗口、暴露档、成交切片），"
             "而引擎把选出来的票**一律等权**——`w = 1/n_hold` 这一行从来没被定价过。"
             "同一批票，按数量分钱和按风险分钱是不同的书：权重变了换手变，换手变成本变，成本变路径变。\n")
    L.append("## 怎么测的\n")
    L.append("- 三个书：%s（生产 cell + 两个邻格）；四个决策相位（同一 20 根周期内错开起点）。"
             % "、".join("n%d/r%d" % c for c in CONFIGS))
    L.append("- 三条规则：`equal`（基线=引擎原文）、`inv_vol`（按 1/σ 分）、"
             "`erc`（等风险贡献，来自同一条 60 根回看协方差）。")
    L.append("- 成本与波动目标不动：%.0f bp/边、%s 波动目标；两条风险规则只能用 ≤d 的数据（因果）。"
             % (COST * 1e4, TARGET_VOL))
    L.append("- **身份腿**：`equal` 走同一套钩子，必须逐位复现引擎自己发布的 cell。\n")
    ctl = doc.get("control") or {}
    if ctl.get("published") is not None:
        L.append("- 实测：发布 %s vs 复现 %s（差 %s pp，容差 0.5pp）→ %s\n"
                 % (_pct(ctl.get("published")), _pct(ctl.get("measured")), ctl.get("delta_pp"),
                    "对上" if ctl.get("within_tol") else "**对不上**"))
    L.append("## 判决\n")
    for sc in TESTS:
        s = doc["summaries"].get(sc) or {}
        v = doc["verdicts"].get(sc) or {}
        L.append("### `%s` → **%s**\n" % (sc, v.get("verdict")))
        if not s.get("n_cells"):
            L.append("无一格可判。\n")
            continue
        L.append("| 读法 | 数字 |\n|---|---|\n"
                 "| 夏普变好的格子 | %.0f%%（%d 格） |\n"
                 "| 夏普中位变化 | %+.3f |\n"
                 "| 年化中位变化 | %+.2f pp |\n"
                 "| 年化没掉的格子 | %.0f%% |\n"
                 "| 最大回撤中位变化 | %+.2f pp（正=更浅） |\n"
                 "| 每次决策换手中位变化 | %+.3f |\n"
                 "| 退化回等权的决策数 | %d |\n"
                 % (100 * s["share_sharpe_ok"], s["n_cells"], s["median_sharpe"],
                    s["median_cagr_pp"], 100 * s["share_cagr_ok"], s["median_maxdd_pp"],
                    s["median_turnover"], s["degenerate_decisions_total"]))
        if v.get("reasons"):
            L.append("没过线的原因：\n")
            for r in v["reasons"]:
                L.append("- %s" % r)
            L.append("")
    L.append("## 逐格\n")
    L.append("| 书 | 相位起点 | 规则 | 年化 | 夏普 | 回撤 | 年化Δ | 夏普Δ | 换手Δ |\n|---|---|---|---|---|---|---|---|---|")
    cells = [c for c in doc["cells"] if c["scheme"] in TESTS]
    for c in sorted(cells, key=lambda x: (x["n_hold"], x["rebal"], x["phase"], x["scheme"])):
        base = next((b for b in doc["cells"]
                     if (b["n_hold"], b["rebal"], b["phase"]) == (c["n_hold"], c["rebal"], c["phase"])
                     and b["scheme"] == "equal"), None)
        d = _delta(c, base) if base else {}
        L.append("| n%d/r%d | %s | %s | %s | %.2f | %s | %+.2f | %+.3f | %+.3f |"
                 % (c["n_hold"], c["rebal"], c["phase"], c["scheme"], _pct(c["cagr"]),
                    c["sharpe"] or 0.0, _pct(c["maxdd"]),
                    d.get("cagr_pp", 0.0), d.get("sharpe", 0.0), d.get("turnover", 0.0)))
    L.append("")
    L.append("## 边界\n")
    L.append("- 票池是现存 ETF（幸存者偏差）；收益主要集中在 2024 之后，四相位只检验了路径，没扩大样本。")
    L.append("- 两条风险规则都用 60 根回看估计；窗口本身对权重的影响未在此面分离（单独的面在 E24）。")
    L.append("- 判决只改「票选出来之后怎么分钱」，不动选券信号与出场规则。\n")
    return "\n".join(L) + "\n"


def _pct(x):
    return "—" if x is None else "%.2f%%" % (100 * x)


def run(out=None):
    doc = build()
    out = Path(out) if out else OUT_JSON
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text(render_md(doc), encoding="utf-8", newline="\n")
    print("etf_book_weight_scheme: %s -> %s" % (doc["reading"], out))
    for sc in TESTS:
        print("  %-8s %s %s" % (sc, doc["verdicts"][sc]["verdict"], doc["verdicts"][sc]["reasons"]))
    return 0 if (doc["control"].get("within_tol") is not False) else 2


# ---------------------------------------------------------------- selftest
def _fixture(n_days=400, n_names=6, seed=7):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2020-01-01", periods=n_days)
    cols = ["S%d" % i for i in range(n_names)]
    # persistent per-name vol so inv_vol has something real to separate
    vols = np.linspace(0.006, 0.030, n_names)
    steps = rng.standard_normal((n_days, n_names)) * vols
    close = pd.DataFrame(200 * np.exp(np.cumsum(steps, axis=0)), index=idx, columns=cols)
    openp = close.shift(1).bfill() * (1 + rng.standard_normal((n_days, n_names)) * 0.0005)
    amt = pd.DataFrame(1e9, index=idx, columns=cols)
    score = pd.DataFrame(rng.standard_normal((n_days, n_names)), index=idx, columns=cols)
    return close, openp, amt, score


def _leg(name, ok, detail=""):
    print("[%s] %s %s" % ("PASS" if ok else "FAIL", name, detail))
    return 0 if ok else 1


def selftest():
    fails = 0
    close, openp, amt, score = _fixture()
    rets = rets_from(openp, close.columns)
    d = close.index[200]
    picks = ["S0", "S1", "S3"]

    for sc in SCHEMES:
        w = make_weights(sc, rets)(picks, d)
        fails += _leg("%s weights sum to 1" % sc, abs(sum(w.values()) - 1) < 1e-9,
                      "%.12f" % sum(w.values()))
        fails += _leg("%s weights cover exactly the picks" % sc, set(w) == set(picks))

    w_equal = make_weights("equal", rets)(picks, d)
    fails += _leg("equal hook is 1/n on every name",
                  all(abs(v - 1.0 / 3) < 1e-12 for v in w_equal.values()))

    w_iv = make_weights("inv_vol", rets)(picks, d)
    sd = rets.loc[:d].tail(VOL_WINDOW)[picks].std(ddof=1)
    fails += _leg("inv_vol gives the calm name more than the wild one",
                  w_iv[sd.idxmin()] > w_iv[sd.idxmax()],
                  "%r" % ({k: round(v, 4) for k, v in w_iv.items()},))

    win = rets.loc[:d].tail(VOL_WINDOW)[picks]
    w_erc = make_weights("erc", rets)(picks, d)
    cov_used = _shrink(win.cov().to_numpy(dtype=float))
    wv = np.array([w_erc[p] for p in picks])
    contrib = wv * (cov_used @ wv)
    spread = float((contrib.max() - contrib.min()) / max(contrib.mean(), 1e-12))
    fails += _leg("erc risk contributions are equal (spread<5%)", spread < 0.05, "spread=%.4f" % spread)

    # a sampled covariance can hand back a negative marginal contribution; 1/negative would
    # push weight onto the wrong sign, so the solver must stay long-only on such a matrix
    neg = np.array([[4e-4, -3.9e-4, 1e-5], [-3.9e-4, 4e-4, 1e-5], [1e-5, 1e-5, 1e-4]])
    w_neg = _erc(neg, np.array([0.02, 0.02, 0.01]))
    fails += _leg("erc stays long-only on a covariance with a negative entry",
                  float(np.min(w_neg)) >= 0.0 and abs(float(np.sum(w_neg)) - 1.0) < 1e-9,
                  "%r" % [round(float(v), 4) for v in w_neg])

    # causality: poison every bar after d and require the decision at d to be unchanged
    poisoned = openp.copy()
    poisoned.loc[poisoned.index > d, :] = poisoned.loc[poisoned.index > d, :] * 3.0
    rets_p = rets_from(poisoned, close.columns)
    for sc in ("inv_vol", "erc"):
        a = make_weights(sc, rets)(picks, d)
        b = make_weights(sc, rets_p)(picks, d)
        fails += _leg("%s uses no data after the decision bar" % sc,
                      all(abs(a[k] - b[k]) < 1e-12 for k in picks))

    # degenerate window falls back to equal AND is counted
    hook = make_weights("inv_vol", rets)
    early = close.index[3]
    w_deg = hook(picks, early)
    fails += _leg("short window falls back to equal and is counted",
                  all(abs(v - 1.0 / 3) < 1e-12 for v in w_deg.values()) and hook.state["degenerate"] == 1)

    # engine identity: hook=None and the equal scheme are the same book
    common = dict(rebal=20, n_hold=6, cost=0.001, vol_target=0.08, start=str(close.index[0].date()))
    s_none, t_none = R.open_to_open_equity(close, openp, amt, score, weight_hook=None, **common)
    s_eq, t_eq = R.open_to_open_equity(close, openp, amt, score,
                                       weight_hook=make_weights("equal", rets), **common)
    fails += _leg("equal scheme is bit-identical to the engine default",
                  float(abs(s_none.iloc[-1] - s_eq.iloc[-1])) < 1e-12 and abs(t_none - t_eq) < 1e-12,
                  "%.15f vs %.15f" % (s_none.iloc[-1], s_eq.iloc[-1]))

    # and a risk scheme must actually change the path (otherwise the hook is inert)
    s_iv, _ = R.open_to_open_equity(close, openp, amt, score,
                                    weight_hook=make_weights("inv_vol", rets), **common)
    fails += _leg("inv_vol moves the equity path", float(abs(s_iv.iloc[-1] - s_none.iloc[-1])) > 1e-6)

    # weight_hook contract enforcement
    bad = lambda picks, dd: {picks[0]: 1.0}
    try:
        R.open_to_open_equity(close, openp, amt, score, weight_hook=bad, **common)
        fails += _leg("wrong-shape weights raise", False)
    except ValueError:
        fails += _leg("wrong-shape weights raise", True)
    bad_sum = lambda picks, dd: {p: 0.5 for p in picks}
    try:
        R.open_to_open_equity(close, openp, amt, score, weight_hook=bad_sum, **common)
        fails += _leg("weights that do not sum to 1 raise", False)
    except ValueError:
        fails += _leg("weights that do not sum to 1 raise", True)

    # phases must be distinct decision calendars, not distinct counts (r1261 family)
    starts = phase_starts(close.index, rebal=20, n=4)
    fails += _leg("four phases land on four distinct bars", len(set(starts)) == 4,
                  "%r" % [str(pd.Timestamp(s).date()) for s in starts])

    # verdict is a pure function of the summary: a great summary adopts, a bad one rejects
    good = {"n_cells": len(CONFIGS) * N_PHASES, "share_sharpe_ok": 0.9, "median_sharpe": 0.10,
            "share_cagr_ok": 0.9, "median_cagr_pp": 0.30, "median_maxdd_pp": 0.50}
    bad_s = dict(good, share_sharpe_ok=0.5)
    fails += _leg("verdict adopts a clean summary", verdict(good)[0] == "ADOPT")
    fails += _leg("verdict rejects a summary that loses in half the cells", verdict(bad_s)[0] == "REJECT")
    fails += _leg("missing cells are never ADOPT",
                  verdict({"n_cells": 3})[0] == "REJECT")

    print("selftest: %d FAIL" % fails)
    return 0 if fails == 0 else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=("run", "selftest"))
    ap.add_argument("--out", default=None)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.check:
        return check()
    if a.selftest or a.cmd == "selftest":
        return selftest()
    return run(a.out)


if __name__ == "__main__":
    raise SystemExit(main())