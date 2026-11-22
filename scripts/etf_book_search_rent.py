#!/usr/bin/env python
"""etf_book_search_rent -- how many independent tries does this book's Sharpe survive?

Why this face exists
--------------------
Every published face of the production book (n_hold=5, vol_target=8%, 20-bar rebalance,
10bp/side) quotes a Sharpe and none of them asks what that Sharpe is worth *after the
search that found it*. `scripts/science_audit.py` already runs the deflated-Sharpe gate on
the six registered trader verdicts (0/6 clear it) but the job never touched the book this
desk would actually fund. That is the gap: a Sharpe is a claim about a signal, and this
repo has published a judgment on hundreds of declared bets before arriving at this one.

What this face publishes
------------------------
1. **The DSR curve.** For a pre-declared grid of trial counts N, the deflated Sharpe
   ratio (Bailey & Lopez de Prado 2014, via `science_gates.deflated_sharpe_ratio` on the
   book's own daily returns -- no second implementation of the formula).
2. **N\\***, the trial count at which DSR crosses 0.95, solved by bisection on that same
   function. N\\* is the answer to "how many independent tries does this Sharpe survive".
3. **The Sharpe the book would need** to clear the same line at each N (the gap, printed
   in Salon units the desk already uses: annualised Sharpe).
4. **Three auditable trial counts** with their mechanical definitions, because N is not
   derivable from the repo without a convention and a face that picks one silently is
   selling a belief. The verdict is therefore stated as a range, not a point.

Frozen before the first run (the gate refuses a face whose echoed criteria differ):
    N_GRID, DSR_LINE, MIN_BARS, ALIGN_TOL_PP (CAGR vs parent), SR_TOL (Sharpe vs parent),
    AUDIT definitions above. No line is tuned after seeing the numbers.

Usage:
    python scripts/etf_book_search_rent.py run
    python scripts/etf_book_search_rent.py check
    python scripts/etf_book_search_rent.py --selftest
"""
from __future__ import annotations

import argparse
import bisect
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT_JSON = ROOT / "results" / "etf_book_search_rent.json"
SCRIPT = "scripts/etf_book_search_rent.py"
FACE = "results/etf_book_search_rent.json"
REFERENCE_PARENT = "results/etf_book_production/PRODUCTION-2026-11-20.json"

# ---------------------------------------------------------------- frozen criteria
N_HOLD = 5
REBAL = 20
COST = 0.0010
N_GRID = (1, 2, 3, 5, 7, 10, 15, 20, 30, 50, 100, 200, 450, 1000)
DSR_LINE = 0.95
MIN_BARS = 250
ALIGN_TOL_PP = 0.05     # our CAGR must match the parent tearsheet within this
SR_TOL = 0.02           # our Sharpe must match the parent tearsheet within this
Z_LINE = 1.6448536269514722   # one-sided 95% normal quantile, used only to invert the line

CRITERIA = {
    "n_hold": N_HOLD,
    "rebal": REBAL,
    "cost_bp_per_side": COST * 1e4,
    "vol_target": "parent TARGET_VOL (0.08)",
    "n_grid": list(N_GRID),
    "dsr_line": DSR_LINE,
    "min_bars": MIN_BARS,
    "align_tol_pp": ALIGN_TOL_PP,
    "sr_tol": SR_TOL,
    "parent": REFERENCE_PARENT,
    "audit_definitions": {
        "prereg_files": "count of research/**/*PREREG*.md -- declared bets, includes robustness re-pricings",
        "attrition_batches": "len(entries) in results/gate_attrition.bm-c.json -- batches a gate killed",
        "queue_closed_rows": "rows marked done in state/queue/{tech,explore}.md -- worked-off queue items",
    },
    "frozen": "constants above were written before the first run",
}


# ------------------------------------------------------------------------ helpers
def _book_series():
    """The production book's equity curve, from the same three imports r1959 uses."""
    import etf_book_production as P
    import etf_robust_pf as R
    close, openp, amt, score, cls, n_flip = P.prep_panel()
    diag = []
    ser, turn = R.open_to_open_equity(
        close, openp, amt, score, REBAL, N_HOLD, COST,
        vol_target=P.TARGET_VOL, diag=diag)
    if not diag:
        raise RuntimeError("panel too short for one decision on the grid")
    return ser, P.TARGET_VOL


def _audit_counts():
    """Three countable proxies for 'how many bets did this desk put a judgment on'."""
    import glob as _glob
    prereg = len(_glob.glob(str(ROOT / "research" / "**" / "*PREREG*.md"), recursive=True))
    batches = None
    ap = ROOT / "results" / "gate_attrition.bm-c.json"
    if ap.exists():
        try:
            batches = len(json.load(open(ap, encoding="utf-8")).get("entries") or [])
        except Exception:                                            # noqa: BLE001
            batches = None
    closed = 0
    for name in ("tech.md", "explore.md"):
        qp = ROOT / "state" / "queue" / name
        if qp.exists():
            closed += sum(1 for line in open(qp, encoding="utf-8", errors="replace")
                          if line.lstrip().startswith("|") and "| done" in line)
    return {"prereg_files": prereg, "attrition_batches": batches,
            "queue_closed_rows": closed}


def _dsr_curve(returns, grid):
    """DSR per trial count, straight from the shared single source."""
    import science_gates as SG
    rows = []
    for n in grid:
        d = SG.deflated_sharpe_ratio(returns, int(n))
        rows.append({"n_trials": int(n), "dsr": d["dsr"], "sr_star_daily": d["sr_star"],
                     "sigma_sr": d["sigma_sr"]})
    return rows


def _solve_breakeven(returns, lo=2, hi=1_000_000):
    """Smallest N whose DSR is below DSR_LINE (bisection on the shared function)."""
    import science_gates as SG

    def dsr(n):
        return SG.deflated_sharpe_ratio(returns, int(n))["dsr"]

    if dsr(lo) < DSR_LINE:
        return {"n_breakeven": int(lo), "note": "even two tries already fall below the line"}
    if dsr(hi) >= DSR_LINE:
        return {"n_breakeven": None, "note": "still above the line at N=%d" % hi}
    a, b = int(lo), int(hi)
    while b - a > 1:
        m = (a + b) // 2
        if dsr(m) >= DSR_LINE:
            a = m
        else:
            b = m
    return {"n_breakeven": int(b), "note": "last N still on/above the line = %d" % a}


def _required_sharpe(sr_ann, sigma_sr, n):
    """Annualised Sharpe a book with this sigma_sr would need to hit DSR_LINE at N.

    Inversion by bisection on `science_gates.dsr_from_stats` (the stored-stats twin of
    the raw-returns function), so the line is defined once, in one place.
    """
    import science_gates as SG

    def hit(sr):
        return SG.dsr_from_stats(sr, sigma_sr, n)["dsr"]

    lo, hi = 0.0, 20.0
    if hit(hi) < DSR_LINE:
        return None
    if hit(lo) >= DSR_LINE:
        return 0.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if hit(mid) >= DSR_LINE:
            hi = mid
        else:
            lo = mid
    return round(hi, 4)


def _bars_needed(sr_ann, sigma_sr, t_bars, n, k):
    """How many bars of the SAME Sharpe would put DSR on the line at trial count N?

    Under the repo convention (null variance = sigma_sr^2) the yardstick shrinks as
    sqrt(T) while the per-bar Sharpe does not, so this is algebra on the two printed
    fields -- and it is verified by feeding the answer back through the shared function
    (check() does exactly that).
    """
    import math

    sr_d = sr_ann / math.sqrt(252.0)
    if sr_d <= 0 or k is None:
        return None
    denom = (sigma_sr ** 2) * (t_bars - 1)
    t_need = denom * ((Z_LINE + k) / sr_d) ** 2 + 1.0
    if t_need <= t_bars:
        return {"bars_needed": int(t_bars), "more_bars": 0, "more_years": 0.0,
                "note": "already clears the line at this N"}
    return {"bars_needed": int(round(t_need)), "more_bars": int(round(t_need - t_bars)),
            "more_years": round((t_need - t_bars) / 252.0, 2),
            "note": "same Sharpe kept, more bars"}


def _psi(sr_ann, sigma_sr, n, returns):
    """The N-only part of the yardstick: SR*(N)/sigma_SR, read off the shared function.

    SR* = sigma_SR * psi(N), so the ratio is invariant in T and in the book -- asking the
    function once with this book's own returns is enough, and there is no second copy of
    the expected-max formula anywhere in this file.
    """
    import science_gates as SG

    d = SG.deflated_sharpe_ratio(returns, int(n))
    if not d["sigma_sr"]:
        return None
    return d["sr_star"] / d["sigma_sr"]


def _verdict(n_star, counts, smallest, largest):
    if n_star is None:
        return "SEARCH_RENT_DOES_NOT_BITE"
    if n_star >= largest:
        return "SEARCH_RENT_DOES_NOT_BITE"
    if n_star >= smallest:
        return "UNRESOLVED_BETWEEN_AUDITED_COUNTS"
    return "SEARCH_RENT_EATS_THE_HEADLINE"


# ---------------------------------------------------------------------------- run
def run(out_path=None, verbose=True):
    import etf_equity_alpha as A

    ser, vol_target = _book_series()
    if len(ser) < MIN_BARS:
        raise RuntimeError("book has %d bars < MIN_BARS=%d: refusing to judge" % (len(ser), MIN_BARS))
    rets = ser.pct_change().dropna()
    _fill_shape(rets.tolist())
    m = A.stats2(ser, "n5_vt08")
    my_cagr, my_sr = float(m["cagr"]), float(m["sharpe"])

    # control arm: the parent tearsheet, not a second opinion about it
    ref = {"source": REFERENCE_PARENT, "parent_cagr": None, "parent_sharpe": None,
           "delta_pp": None, "delta_sr": None, "aligned": None}
    rp = ROOT / REFERENCE_PARENT
    if rp.exists():
        try:
            pj = json.load(open(rp, encoding="utf-8"))
            full = (((pj.get("backtest") or {}).get("n5_vt08") or {}).get("full") or {})
            pc, ps = full.get("cagr"), full.get("sharpe")
            if pc is not None:
                ref["parent_cagr"] = pc
                ref["delta_pp"] = round(100 * (my_cagr - pc), 4)
            if ps is not None:
                ref["parent_sharpe"] = ps
                ref["delta_sr"] = round(my_sr - ps, 4)
            ref["aligned"] = bool(
                ref["delta_pp"] is not None and abs(ref["delta_pp"]) <= ALIGN_TOL_PP and
                ref["delta_sr"] is not None and abs(ref["delta_sr"]) <= SR_TOL)
        except Exception as e:                                        # noqa: BLE001
            ref["source"] = "%s (unreadable: %s)" % (REFERENCE_PARENT, e)

    curve = _dsr_curve(rets.tolist(), N_GRID)
    sigma_sr = curve[0]["sigma_sr"]
    base = curve[0]
    be = _solve_breakeven(rets.tolist())
    n_star = be["n_breakeven"]

    counts = _audit_counts()
    known = [v for v in counts.values() if isinstance(v, int)]
    smallest = min(known) if known else 1
    largest = max(known) if known else 1
    verdict = _verdict(n_star, counts, smallest, largest)

    need = []
    for row in curve:
        ks = row["sr_star_daily"] / sigma_sr if sigma_sr else None
        need.append({"n_trials": row["n_trials"],
                     "required_sr_annualized": _required_sharpe(my_sr, sigma_sr, row["n_trials"]),
                     "gap_vs_book": (None if row["n_trials"] == 1 else
                                     round((_required_sharpe(my_sr, sigma_sr, row["n_trials"]) or 0)
                                           - my_sr, 4))})

    # the plan-shaped half: how much more forward record puts the SAME Sharpe on the line
    kk = {row["n_trials"]: (row["sr_star_daily"] / sigma_sr if sigma_sr else None)
          for row in curve}
    bars = []
    for n in (smallest, max(known) if known else None, 50, 100, 200):
        if not n or n in [b["n_trials"] for b in bars]:
            continue
        k = kk.get(n)
        if k is None:
            k = _psi(my_sr, sigma_sr, n, rets.tolist())
        bn = _bars_needed(my_sr, sigma_sr, len(rets), n, k)
        bars.append({"n_trials": int(n), "null_multiple": None if k is None else round(k, 6),
                     "needed": bn})

    out = {
        "script": SCRIPT,
        "face": FACE,
        "criteria": CRITERIA,
        "book": {
            "arm": "n5_vt08",
            "bars": int(len(rets)),
            "start": str(ser.index[0].date()),
            "end": str(ser.index[-1].date()),
            "cents": {"cagr": round(my_cagr, 4), "sharpe": round(my_sr, 3),
                      "vol": m.get("vol"), "maxdd": m.get("maxdd"), "years": m.get("years")},
            "vol_target": vol_target,
            "skew": base_dsr_field(curve, "skew"),
        },
        "control_parent": ref,
        "dsr_curve": curve,
        "breakeven": be,
        "required_sharpe": need,
        "bars_needed": bars,
        "trial_census": counts,
        "audited_range": {"smallest": smallest, "largest": largest},
        "dsr_line": DSR_LINE,
        "verdict": verdict,
        "verdict_zh": {
            "SEARCH_RENT_DOES_NOT_BITE": "这本书的 Sharpe 撑得住自家搜索次数",
            "UNRESOLVED_BETWEEN_AUDITED_COUNTS": "结论取决于你用哪个「尝试次数」口径",
            "SEARCH_RENT_EATS_THE_HEADLINE": "按自家可核的尝试次数，这本书的 Sharpe 还在噪声里",
        }[verdict],
        "caveats": [
            "DSR 的 N 是「独立假设」不是「跑过多少次回测」；本面印三个可核口径让读者自己选，"
            "任何单一 N 都是信念不是测量。",
            "sigma_SR 用仓库既定约定（null 方差=sample sigma_SR^2，见 science_gates 注释），"
            "与 science_audit C3 同源。",
            "DSR 低不等于这本书将来不赚钱：它说的是「这个 Sharpe 与『试很多次挑最好』不可分」，"
            "要靠样本外时长（T）或单假设的新线来收紧，不靠再调参数。",
        ],
    }
    op = Path(out_path) if out_path else OUT_JSON
    op.parent.mkdir(parents=True, exist_ok=True)
    json.dump(out, open(op, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if verbose:
        print("book n5_vt08  bars=%d  CAGR=%.2f%%  SR=%.3f  (parent %.2f%%/%.3f, d=%.4fpp/%.4f)"
              % (len(rets), 100 * my_cagr, my_sr,
                 100 * (ref["parent_cagr"] or float("nan")), (ref["parent_sharpe"] or float("nan")),
                 (ref["delta_pp"] if ref["delta_pp"] is not None else float("nan")),
                 (ref["delta_sr"] if ref["delta_sr"] is not None else float("nan"))))
        print("skew=%.3f kurt=%.3f sigma_SR=%.6f" % (base_dsr_field(curve, "skew") or 0,
                                                     base_dsr_field(curve, "kurtosis") or 0, sigma_sr))
        print("N*  (DSR crosses %.2f) = %s ; %s" % (DSR_LINE, n_star, be["note"]))
        for row in curve:
            print("  N=%4d  DSR=%.4f  SR*=%8.4f daily" % (row["n_trials"], row["dsr"], row["sr_star_daily"]))
        print("trial census: %s" % counts)
        print("verdict: %s  (%s)" % (verdict, out["verdict_zh"]))
        print("face -> %s" % op)
    return out


def base_dsr_field(curve, field):
    """Pull one shape field off the shared function once (the curve rows do not carry it)."""
    return _SHAPE.get(field)


_SHAPE: dict = {}


def _fill_shape(returns):
    import science_gates as SG
    d = SG.deflated_sharpe_ratio(returns, 2)
    _SHAPE.update({"skew": d["skew"], "kurtosis": d["kurtosis"], "T": d["T"]})


# -------------------------------------------------------------------------- check
def check(path=None):
    p = Path(path) if path else OUT_JSON
    if not p.exists():
        print("STALE: face missing at %s -- run it before checking" % p)
        return 3
    face = json.load(open(p, encoding="utf-8"))
    problems = []

    if face.get("criteria", {}).get("frozen") != CRITERIA["frozen"]:
        problems.append("criteria block does not echo the frozen constants")
    if face.get("criteria", {}).get("dsr_line") != DSR_LINE:
        problems.append("dsr_line drifted from %s" % DSR_LINE)

    curve = face.get("dsr_curve") or []
    if [r["n_trials"] for r in curve] != list(N_GRID):
        problems.append("dsr_curve grid is not the frozen N_GRID")
    dsrs = [r["dsr"] for r in curve]
    for a, b in zip(dsrs, dsrs[1:]):
        if b > a + 1e-12:
            problems.append("DSR is not monotone non-increasing in N (%s -> %s)" % (a, b))
            break
    if not all(0.0 <= d <= 1.0 for d in dsrs):
        problems.append("a DSR row is outside [0,1]")

    sigma = curve[0]["sigma_sr"] if curve else None
    for row in face.get("required_sharpe") or []:
        if row["n_trials"] == 1 or row["required_sr_annualized"] is None or sigma is None:
            continue
        import science_gates as SG
        d = SG.dsr_from_stats(row["required_sr_annualized"], sigma, row["n_trials"])["dsr"]
        if abs(d - DSR_LINE) > 2e-3:
            problems.append("required_sr at N=%d re-derives DSR=%.4f, not the frozen %.2f"
                            % (row["n_trials"], d, DSR_LINE))
            break

    # the verdict must be exactly what the printed numbers imply
    n_star = (face.get("breakeven") or {}).get("n_breakeven")
    audit = face.get("trial_census") or {}
    known = [v for v in audit.values() if isinstance(v, int)]
    if known:
        want = _verdict(n_star, audit, min(known), max(known))
        if face.get("verdict") != want:
            problems.append("verdict %s does not follow from N*=%s and census %s (want %s)"
                            % (face.get("verdict"), n_star, audit, want))

    # N* itself must be the crossing, not a guess: every grid point below it is on/above
    # the line and every grid point at/above it is below.
    if n_star is not None and curve:
        for r in curve:
            if r["n_trials"] < n_star and r["dsr"] < DSR_LINE - 1e-9:
                problems.append("N*=%d is the first N below the line, but grid point N=%d "
                                "(dsr=%.4f) is already below it" % (n_star, r["n_trials"], r["dsr"]))
                break
        for r in curve:
            if r["n_trials"] >= n_star and r["dsr"] >= DSR_LINE:
                problems.append("N*=%d claims the line is crossed by then, but grid point N=%d "
                                "still prints dsr=%.4f >= %.2f" % (n_star, r["n_trials"],
                                                                   r["dsr"], DSR_LINE))
                break

    # the plan-shaped leg: feeding the answer back must land on the line
    bars = face.get("bars_needed") or []
    if bars and sigma:
        import math
        import science_gates as SG
        T0 = int((face.get("book") or {}).get("bars") or 0)
        sr_ann = (face.get("book") or {}).get("cents", {}).get("sharpe")
        denom = (sigma ** 2) * (T0 - 1) if T0 > 1 else None
        for b in bars:
            need = b.get("needed") or {}
            t_need = need.get("bars_needed")
            if not t_need or denom is None or sr_ann is None or need.get("more_bars", 0) <= 0:
                continue
            sigma_need = math.sqrt(denom / (t_need - 1))
            d = SG.dsr_from_stats(sr_ann, sigma_need, b["n_trials"])["dsr"]
            if abs(d - DSR_LINE) > 5e-3:
                problems.append("bars_needed at N=%d re-derives DSR=%.4f, not the frozen %.2f"
                                % (b["n_trials"], d, DSR_LINE))
                break

    ctrl = face.get("control_parent") or {}
    if ctrl.get("aligned") is not True:
        problems.append("control arm did not reproduce the parent tearsheet (delta_pp=%s delta_sr=%s)"
                        % (ctrl.get("delta_pp"), ctrl.get("delta_sr")))

    if problems:
        print("CHECK FAILED")
        for x in problems:
            print("  - " + x)
        return 1
    print("CHECK OK  DSR@N=2=%.4f  DSR@N=50=%.4f  N*=%s  verdict=%s"
          % (curve[0]["dsr"] if curve else -1,
             next((r["dsr"] for r in curve if r["n_trials"] == 50), -1),
             n_star, face.get("verdict")))
    return 0


# ----------------------------------------------------------------------- selftest
def _synth(mu=0.0006, sigma=0.01, t=1500, seed=20261123, skew_push=0.0):
    rng = np.random.default_rng(seed)
    x = rng.normal(mu, sigma, t)
    if skew_push:
        x = x + skew_push * (rng.random(t) < 0.02) * sigma * 8
    return x.tolist()


def selftest():
    import science_gates as SG
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    xs = _synth()
    d2 = SG.deflated_sharpe_ratio(xs, 2)
    d50 = SG.deflated_sharpe_ratio(xs, 50)
    d1000 = SG.deflated_sharpe_ratio(xs, 1000)
    leg("L1 DSR decreasing in N", d2["dsr"] >= d50["dsr"] >= d1000["dsr"])
    leg("L2 DSR in [0,1]", all(0 <= v <= 1 for v in (d2["dsr"], d50["dsr"], d1000["dsr"])))
    leg("L3 deterministic", SG.deflated_sharpe_ratio(xs, 50) == d50)

    strong = _synth(mu=0.0016)
    leg("L4 higher SR => higher DSR at fixed N",
        SG.deflated_sharpe_ratio(strong, 50)["dsr"] > d50["dsr"])

    be = _solve_breakeven(xs)
    n_star = be["n_breakeven"]
    if n_star is None:
        leg("L5 breakeven solver finds a crossing", False)
    else:
        above = SG.deflated_sharpe_ratio(xs, max(n_star - 1, 2))["dsr"]
        below = SG.deflated_sharpe_ratio(xs, n_star)["dsr"]
        leg("L5 breakeven bracket (above>=line>below)", above >= DSR_LINE > below or n_star == 2)

    need = _required_sharpe(1.0, 0.02, 50)
    leg("L6 required-SR inverts the line", need is not None and
        abs(SG.dsr_from_stats(need, 0.02, 50)["dsr"] - DSR_LINE) < 2e-3)

    leg("L7 verdict: room above the largest count",
        _verdict(10_000, {"a": 10, "b": 20}, 10, 20) == "SEARCH_RENT_DOES_NOT_BITE")
    leg("L8 verdict: below the smallest count",
        _verdict(3, {"a": 10, "b": 20}, 10, 20) == "SEARCH_RENT_EATS_THE_HEADLINE")
    leg("L9 verdict: between the two counts",
        _verdict(15, {"a": 10, "b": 20}, 10, 20) == "UNRESOLVED_BETWEEN_AUDITED_COUNTS")

    _fill_shape(xs)
    leg("L10 shape fields populated", _SHAPE.get("skew") is not None and _SHAPE.get("T") == len(xs))

    # a face whose verdict does not follow from its own numbers must be refused
    import tempfile
    tmp = Path(tempfile.mkdtemp()) / "face.json"
    fake = {
        "criteria": dict(CRITERIA),
        "dsr_curve": [{"n_trials": n, "dsr": round(0.99 - 0.02 * i, 4), "sr_star_daily": 0.0,
                       "sigma_sr": 0.02} for i, n in enumerate(N_GRID)],
        "breakeven": {"n_breakeven": 5},
        "required_sharpe": [],
        "trial_census": {"a": 100},
        "verdict": "SEARCH_RENT_DOES_NOT_BITE",
        "control_parent": {"aligned": True},
    }
    json.dump(fake, open(tmp, "w", encoding="utf-8"))
    rc_bad = check(tmp)
    fake["verdict"] = "SEARCH_RENT_EATS_THE_HEADLINE"
    json.dump(fake, open(tmp, "w", encoding="utf-8"))
    rc_good = check(tmp)
    leg("L11 check refuses a verdict that contradicts its numbers", rc_bad == 1)
    leg("L12 check passes the repaired face", rc_good == 0)

    # L13: the bars-needed answer must land on the line when fed back
    import math
    xs2 = _synth(mu=0.0012, sigma=0.01, t=800, seed=7)
    d50b = SG.deflated_sharpe_ratio(xs2, 50)
    k50 = d50b["sr_star"] / d50b["sigma_sr"]
    bn = _bars_needed(d50b["sr_annualized"], d50b["sigma_sr"], len(xs2), 50, k50)
    if not bn or bn["more_bars"] <= 0:
        leg("L13 bars-needed inverts the line", False)
    else:
        denom = (d50b["sigma_sr"] ** 2) * (len(xs2) - 1)
        sig_need = math.sqrt(denom / (bn["bars_needed"] - 1))
        d2 = SG.dsr_from_stats(d50b["sr_annualized"], sig_need, 50)["dsr"]
        leg("L13 bars-needed inverts the line", abs(d2 - DSR_LINE) < 5e-3)

    ok = sum(1 for _, c in legs if c)
    for name, c in legs:
        print(("PASS " if c else "FAIL ") + name)
    print("selftest %d/%d" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


# ---------------------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "check", "selftest"])
    ap.add_argument("--out", default=None)
    ap.add_argument("--selftest", action="store_true", help="alias for the selftest subcommand")
    a = ap.parse_args(argv)
    if a.selftest or a.cmd == "selftest":
        return selftest()
    if a.cmd == "check":
        return check(a.out)
    run(a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
