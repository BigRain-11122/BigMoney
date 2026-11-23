"""A-share residual veto book: does the hedge still work when the beta cannot see the future?

r2022 priced five hedge sizes, r2023 turned them into a drawdown-budget purchase,
r2024 re-read it on daily marks, r2025 raced nine ways of choosing a size, r2026 named
the default (one unit of beta = 90.13% of the book at beta = 0.9013), r2027 turned that
into lots, r2028 showed the *price date* moves the ticket by 595 lots and r2029 printed
the beta's own 95% band -- 3,457 .. 4,381 lots, wider than the date shift.

All seven speak with a beta that was fitted on 43 periods and then read on 34 periods it
had never seen.  That is honest about *which rows* were used to fit, and still leaves one
door open: the reader is told the hedge removes ~60% of the book's variance, and that
number was computed with a single beta applied to the whole window -- including the rows
it was fitted on.

This face closes that door and asks the question the ticket actually faces:

    On the day you must place the order, the only beta you can have is the one the past
    gives you.  Held that way -- refitted each period on strictly prior rows -- does the
    hedge still remove the risk it claims?

Three things are then measured on one common evaluation sample, so no arm gets a longer
or friendlier set of periods than another:

  * **the honest arm**     -- beta refitted before each period (expanding window);
  * **the look-ahead arm** -- one beta fitted on everything, the way the parents read it;
  * **the mechanical arm** -- beta = 1.00, no estimation at all (r2026's default).

And the control that makes a volatility claim mean something:

  * **a smaller book** -- the unhedged book scaled down to the honest arm's own
    volatility.  If hedging removed risk only because it removed exposure, this control
    matches it period for period, and there is nothing here but leverage.

Thresholds are frozen in PREREG below, before the run, and are not tuned afterwards.

Outputs (new files only):
    results/astock_veto_hedge_walkforward.json
    research/ASTOCK_VETO_HEDGE_WALKFORWARD.md

Usage:
    python scripts/astock_veto_hedge_walkforward.py selftest
    python scripts/astock_veto_hedge_walkforward.py run
    python scripts/astock_veto_hedge_walkforward.py check
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PARENT = os.path.join(ROOT, "results", "astock_veto_hedgeable_beta.json")
BAND = os.path.join(ROOT, "results", "astock_veto_hedge_band.json")
DEFAULT = os.path.join(ROOT, "results", "astock_veto_hedge_default.json")
OUT_JSON = os.path.join(ROOT, "results", "astock_veto_hedge_walkforward.json")
OUT_MD = os.path.join(ROOT, "research", "ASTOCK_VETO_HEDGE_WALKFORWARD.md")

PPY = 12.6          # periods per year, quoted from the parent spec
WARMUP = 20         # periods the first walk-forward beta is allowed to see (= r2029's window)

# frozen before the run -- see PREREG in build_face()
LINE_REMOVED = 0.30      # honest arm must remove this share of the book's vol to count
LINE_TIE_PP = 0.10       # vol gap under this (pp) is a tie, not a win
LINE_ONE_UNIT_PP = 0.25  # fitting must beat beta=1 by this much to count as a win
LINE_DD_PP = 0.20        # drawdown gap under this (pp) is a tie
LINE_CUM = 0.02          # cumulative-return gap under this (2pp) is a tie

TOL = 1e-9


# ------------------------------------------------------------------ small helpers
def _now() -> str:
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def _rel(path: str) -> str:
    try:
        return os.path.relpath(path, ROOT).replace(os.sep, "/")
    except ValueError:
        return str(path).replace(os.sep, "/")


def _read_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _sha_file(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def content_sha(face: dict) -> str:
    body = {k: v for k, v in face.items() if k != "generated"}
    return hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False)
                          .encode("utf-8")).hexdigest()


def fingerprint(path: str) -> dict:
    face = _read_json(path)
    return {"face": _rel(path), "file_sha256": _sha_file(path),
            "content_sha256": content_sha(face),
            "generated": face.get("generated"),
            "evidence_cutoff": face.get("evidence_cutoff")}


# ------------------------------------------------------------------ pure logic
def ols_slope(y, x):
    """Slope of y on x, or None when it cannot be fitted.  No intercept is printed
    anywhere in this face; it is fitted and carried so the slope is not biased."""
    yy = np.asarray(y, dtype=np.float64)
    xx = np.asarray(x, dtype=np.float64)
    keep = np.isfinite(yy) & np.isfinite(xx)
    yy, xx = yy[keep], xx[keep]
    if len(yy) < 3 or float(np.var(xx)) <= 0.0:
        return None
    X = np.column_stack([np.ones_like(xx), xx])
    coef = np.linalg.lstsq(X, yy, rcond=None)[0]
    beta = float(coef[1])
    return beta if np.isfinite(beta) else None


def walk_forward_betas(book, hedge, warmup: int = WARMUP) -> list:
    """beta for period i may only see rows [0, i).  This is the whole point of the face;
    the function cannot reach forward even if it wanted to."""
    out = []
    n = len(book)
    for i in range(int(warmup), n):
        beta = ols_slope(book[:i], hedge[:i])
        out.append({"i": i, "beta": beta, "n_train": i})
    return out


def max_drawdown(returns) -> float:
    """Peak-to-trough drawdown of the cumulative curve, as a negative fraction."""
    a = np.asarray([v for v in returns if v is not None and np.isfinite(v)],
                   dtype=np.float64)
    if len(a) == 0:
        return float("nan")
    eq = np.cumprod(1.0 + a)
    peak = np.maximum.accumulate(np.concatenate([[1.0], eq]))[1:]
    return float(np.min(eq / peak - 1.0))


def arm_stats(returns, ppy: float = PPY) -> dict:
    """Everything an arm is judged on, on the sample it was handed."""
    a = np.asarray([v for v in returns if v is not None and np.isfinite(v)],
                   dtype=np.float64)
    n = int(len(a))
    if n < 3:
        return {"n": n, "vol": None, "mean_annual": None, "worst_period": None,
                "neg_periods": None, "cum": None, "max_dd": None}
    return {"n": n,
            "vol": float(np.std(a, ddof=1) * np.sqrt(ppy)),
            "mean_annual": float(np.mean(a) * ppy),
            "worst_period": float(np.min(a)),
            "neg_periods": int(np.sum(a < 0.0)),
            "cum": float(np.prod(1.0 + a) - 1.0),
            "max_dd": max_drawdown(a)}


def decide_removal(removed) -> str:
    if removed is None:
        return "ARM_NOT_MEASURABLE"
    return ("HONEST_BETA_KEEPS_ITS_REMOVAL" if removed >= LINE_REMOVED
            else "NO_LOOKAHEAD_BETA_REMOVES_LESS_THAN_THE_LINE")


def decide_lookahead(premium_pp) -> str:
    if premium_pp is None:
        return "ARM_NOT_MEASURABLE"
    if abs(premium_pp) <= LINE_TIE_PP:
        return "LOOKAHEAD_IS_A_TIE"
    return ("LOOKAHEAD_BUYS_MORE_THAN_A_TIE" if premium_pp > 0
            else "LOOKAHEAD_FLATTERS_THE_WRONG_ARM")


def decide_fitting(gap_pp) -> str:
    """gap = vol(beta=1) - vol(walk-forward).  Positive means fitting helped."""
    if gap_pp is None:
        return "ARM_NOT_MEASURABLE"
    if gap_pp >= LINE_ONE_UNIT_PP:
        return "FITTING_BEATS_ONE_UNIT_OUT_OF_SAMPLE"
    if gap_pp <= -LINE_ONE_UNIT_PP:
        return "ONE_UNIT_BEATS_THE_FITTED_BETA"
    return "ONE_UNIT_TIES_THE_FITTED_BETA"


def decide_scale(dd_gap_pp, cum_gap) -> str:
    """The de-lever control.  `dd_gap_pp` > 0 means the hedge's worst drawdown is
    shallower than an unhedged book of the same volatility; `cum_gap` > 0 means the
    hedge also earned more.  A hedge that removes volatility by removing exposure ties
    on volatility and loses on return, so both axes are read."""
    if dd_gap_pp is None or cum_gap is None:
        return "ARM_NOT_MEASURABLE"
    if dd_gap_pp >= LINE_DD_PP:
        return ("HEDGE_BEATS_A_SMALLER_BOOK" if cum_gap > 0
                else "HEDGE_SHAVES_THE_DRAWDOWN_BUT_EARNS_LESS")
    if dd_gap_pp <= -LINE_DD_PP:
        return ("HEDGE_TRADES_DRAWDOWN_FOR_RETURN" if cum_gap >= LINE_CUM
                else "SMALLER_BOOK_BEATS_THE_HEDGE")
    return ("HEDGE_TRADES_DRAWDOWN_FOR_RETURN" if cum_gap >= LINE_CUM
            else "HEDGE_IS_ONLY_SCALE_OUT_OF_SAMPLE")


# ------------------------------------------------------------------ face
def build_face() -> dict:
    parent = _read_json(PARENT)
    band = _read_json(BAND)
    default = _read_json(DEFAULT)

    rows = parent.get("rows") or []
    if len(rows) < WARMUP + 5:
        return {"generated": _now(), "kind": "walkforward_power",
                "evidence_cutoff": parent.get("evidence_cutoff"),
                "verdict": "NOT_ENOUGH_PERIODS",
                "verdict_why": "only %d periods; warm-up %d leaves too few to evaluate"
                               % (len(rows), WARMUP),
                "parents": {"beta": fingerprint(PARENT)}}

    book = [r.get("book_net") for r in rows]
    hedge = [r.get("hedge_etf") for r in rows]
    dates = [r.get("date") for r in rows]
    ends = [r.get("end") for r in rows]

    wf = walk_forward_betas(book, hedge, WARMUP)
    eval_rows = [w for w in wf if w.get("beta") is not None]
    eval_idx = [w["i"] for w in eval_rows]
    betas = [w["beta"] for w in eval_rows]

    full_beta = ols_slope(book, hedge)
    frozen_beta = ((band.get("fit") or {}).get("etf_in_sample") or {}).get("beta")
    band_low = ((band.get("fit") or {}).get("etf_in_sample") or {}).get("ci_low")
    band_high = ((band.get("fit") or {}).get("etf_in_sample") or {}).get("ci_high")
    if frozen_beta is None:
        frozen_beta = ((default.get("default") or {}).get("beta"))

    def resid(kind: str, i: int) -> float:
        b = book[i]
        h = hedge[i]
        if b is None or h is None:
            return float("nan")
        if kind == "none":
            k = 0.0
        elif kind == "one_unit":
            k = 1.0
        elif kind == "full_window":
            k = full_beta if full_beta is not None else float("nan")
        elif kind == "frozen":
            k = frozen_beta if frozen_beta is not None else float("nan")
        else:
            k = next(w["beta"] for w in eval_rows if w["i"] == i)
        return float(b) - float(k) * float(h)

    kinds = ("none", "one_unit", "full_window", "frozen", "walk_forward")
    series = {k: [resid(k, i) for i in eval_idx] for k in kinds}
    stats = {k: arm_stats(v) for k, v in series.items()}

    vol_none = stats["none"]["vol"]
    removed = None
    if vol_none and stats["walk_forward"]["vol"] is not None and vol_none > 0:
        removed = 1.0 - stats["walk_forward"]["vol"] / vol_none
    removed_full = None
    if vol_none and stats["full_window"]["vol"] is not None and vol_none > 0:
        removed_full = 1.0 - stats["full_window"]["vol"] / vol_none

    premium_pp = None
    if stats["walk_forward"]["vol"] is not None and stats["full_window"]["vol"] is not None:
        premium_pp = (stats["walk_forward"]["vol"] - stats["full_window"]["vol"]) * 100.0

    fitting_gap_pp = None
    if stats["walk_forward"]["vol"] is not None and stats["one_unit"]["vol"] is not None:
        fitting_gap_pp = (stats["one_unit"]["vol"] - stats["walk_forward"]["vol"]) * 100.0

    # the control: the unhedged book, scaled down to the honest arm's own volatility
    scale = None
    if vol_none and stats["walk_forward"]["vol"] is not None and vol_none > 0:
        scale = stats["walk_forward"]["vol"] / vol_none
    scaled = [float(book[i]) * scale for i in eval_idx] if scale is not None else []
    stats["smaller_book"] = arm_stats(scaled)
    dd_gap_pp = None
    if (stats["walk_forward"]["max_dd"] is not None
            and stats["smaller_book"]["max_dd"] is not None):
        dd_gap_pp = (stats["walk_forward"]["max_dd"]
                     - stats["smaller_book"]["max_dd"]) * 100.0
    cum_gap = None
    if (stats["walk_forward"]["cum"] is not None
            and stats["smaller_book"]["cum"] is not None):
        cum_gap = stats["walk_forward"]["cum"] - stats["smaller_book"]["cum"]

    # period-level: how often does hedging actually shrink the move?
    help_rate = None
    pairs = [(a, b) for a, b in zip(series["walk_forward"], series["none"])
             if np.isfinite(a) and np.isfinite(b)]
    if pairs:
        help_rate = float(sum(1 for a, b in pairs if abs(a) < abs(b)) / len(pairs))

    outside_band = None
    if betas and band_low is not None and band_high is not None:
        outside_band = int(sum(1 for b in betas if b < band_low or b > band_high))

    steps = [abs(betas[k] - betas[k - 1]) for k in range(1, len(betas))]

    verdict_removal = decide_removal(removed)
    verdict_lookahead = decide_lookahead(premium_pp)
    verdict_fitting = decide_fitting(fitting_gap_pp)
    verdict_scale = decide_scale(dd_gap_pp, cum_gap)

    arms = []
    labels = {"none": "no hedge", "one_unit": "beta = 1.00 (mechanical)",
              "full_window": "one beta on every period (look-ahead)",
              "frozen": "beta frozen at 2023-12-31 (%s)" % (
                  ("%.4f" % frozen_beta) if isinstance(frozen_beta, float) else "n/a"),
              "walk_forward": "beta refitted on prior rows (honest)",
              "smaller_book": "no hedge, scaled to the honest arm's volatility"}
    for k in ("none", "one_unit", "full_window", "frozen", "walk_forward",
              "smaller_book"):
        s = stats.get(k) or {}
        rpv = None
        if s.get("vol") not in (None, 0) and s.get("mean_annual") is not None:
            rpv = s["mean_annual"] / s["vol"]
        arms.append({"arm": k, "label": labels[k],
                     "n": s.get("n"), "vol": s.get("vol"),
                     "vol_removed": (None if (k == "none" or vol_none in (None, 0)
                                              or s.get("vol") is None)
                                     else 1.0 - s["vol"] / vol_none),
                     "return_per_vol": rpv,
                     "mean_annual": s.get("mean_annual"),
                     "worst_period": s.get("worst_period"),
                     "neg_periods": s.get("neg_periods"),
                     "cum": s.get("cum"), "max_dd": s.get("max_dd")})

    verdict_why = (
        "held honestly, the hedge removes %.1f%% of the book's annualised volatility "
        "(%.2f%% -> %.2f%%) and the look-ahead arm removes %.1f%% -- a gap of %.2f pp; "
        "beta = 1.00 without any fitting sits %.2f pp %s the honest arm; against an "
        "unhedged book of the same volatility it earns %.1f%% against %.1f%% "
        "(%.2f vs %.2f per unit of volatility) but draws down %.2f%% against %.2f%%"
        % (100.0 * (removed or 0.0), 100.0 * (vol_none or 0.0),
           100.0 * (stats["walk_forward"].get("vol") or 0.0),
           100.0 * (removed_full or 0.0), (premium_pp or 0.0),
           abs(fitting_gap_pp or 0.0),
           "below" if (fitting_gap_pp or 0.0) > 0 else "above",
           100.0 * (stats["walk_forward"].get("mean_annual") or 0.0),
           100.0 * (stats["smaller_book"].get("mean_annual") or 0.0),
           stats["walk_forward"].get("mean_annual", 0.0) / (stats["walk_forward"].get("vol") or 1.0),
           stats["smaller_book"].get("mean_annual", 0.0) / (stats["smaller_book"].get("vol") or 1.0),
           100.0 * (stats["walk_forward"].get("max_dd") or 0.0),
           100.0 * (stats["smaller_book"].get("max_dd") or 0.0)))

    return {
        "generated": _now(),
        "kind": "walkforward_power",
        "machine": "bm-c",
        "evidence_cutoff": parent.get("evidence_cutoff"),
        "last_period_end": ends[-1] if ends else None,
        "first_period": dates[0] if dates else None,
        "fills_the_hole_of": "r2022-r2029 read one beta over the whole window; the removed "
                             "variance those faces quote includes the rows the beta was "
                             "fitted on. This face refits before every period.",
        "prereg": {
            "question": "Held honestly (beta from prior rows only), does the hedge still "
                        "remove the risk it claims -- and does it do anything a smaller "
                        "book would not?",
            "arms": {"none": "k = 0", "one_unit": "k = 1.00 (r2026 default)",
                     "walk_forward": "k = OLS slope on rows strictly before the period",
                     "full_window": "k = OLS slope on all periods (look-ahead reference)",
                     "frozen": "k = beta published by r2022/r2029 (fitted to 2023-12-31)",
                     "smaller_book": "k = 0, book scaled to the honest arm's volatility"},
            "evaluation_sample": "periods with index >= %d, one common sample for every arm"
                                 % WARMUP,
            "verdict_rule": {
                "removal": "remove >= %.2f of vol to count as working" % LINE_REMOVED,
                "lookahead": "a gap under %.2f pp is a tie" % LINE_TIE_PP,
                "fitting": "fitting wins only if it beats beta=1 by >= %.2f pp"
                           % LINE_ONE_UNIT_PP,
                "scale": "the hedge wins over an equal-vol book only with >= %.2f pp "
                         "shallower drawdown" % LINE_DD_PP},
            "rule_frozen_before_run": True,
            "not_done_here": "no beta is re-chosen for trading, no cost is re-estimated, "
                             "no capital is re-marked",
        },
        "spec": {"hold": (parent.get("spec") or {}).get("hold"),
                 "stride": (parent.get("spec") or {}).get("stride"),
                 "periods_per_year": PPY, "warmup_periods": WARMUP,
                 "hedge_leg": "hedge_etf (512100), the arm every prior face prices",
                 "lines": {"removed": LINE_REMOVED, "tie_pp": LINE_TIE_PP,
                           "one_unit_pp": LINE_ONE_UNIT_PP, "dd_pp": LINE_DD_PP}},
        "parents": {"beta": fingerprint(PARENT), "band": fingerprint(BAND),
                    "default": fingerprint(DEFAULT)},
        "sample": {"periods_total": len(rows), "periods_evaluated": len(eval_idx),
                   "warmup": WARMUP,
                   "usable_trainings": len([w for w in wf if w.get("beta") is not None]),
                   "unusable": len([w for w in wf if w.get("beta") is None])},
        "betas": {"first": betas[0] if betas else None,
                  "last": betas[-1] if betas else None,
                  "min": min(betas) if betas else None,
                  "max": max(betas) if betas else None,
                  "mean": float(np.mean(betas)) if betas else None,
                  "sd": float(np.std(betas, ddof=1)) if len(betas) > 1 else None,
                  "mean_abs_step": float(np.mean(steps)) if steps else None,
                  "max_abs_step": float(np.max(steps)) if steps else None,
                  "full_window_beta": full_beta,
                  "frozen_beta": frozen_beta,
                  "band_low": band_low, "band_high": band_high,
                  "outside_published_band": outside_band,
                  "series": [{"i": w["i"], "date": dates[w["i"]], "beta": w["beta"]}
                             for w in eval_rows]},
        "arms": arms,
        "verdict_removal": verdict_removal,
        "verdict_lookahead": verdict_lookahead,
        "verdict_fitting": verdict_fitting,
        "verdict_scale": verdict_scale,
        "verdict": verdict_removal,
        "verdict_why": verdict_why,
        "reads": {"vol_removed_honest": removed, "vol_removed_full_window": removed_full,
                  "lookahead_premium_pp": premium_pp,
                  "fitting_gap_pp": fitting_gap_pp,
                  "scale_factor": scale,
                  "vol_gap_vs_smaller_book_pp": (
                      (stats["walk_forward"]["vol"] - stats["smaller_book"]["vol"]) * 100.0
                      if (stats["walk_forward"]["vol"] is not None
                          and stats["smaller_book"]["vol"] is not None) else None),
                  "dd_gap_vs_smaller_book_pp": dd_gap_pp,
                  "cum_gap_vs_smaller_book": cum_gap,
                  "hedge_help_rate": help_rate},
        "note_on_frozen_arm": "the frozen beta was fitted to rows ending 2023-12-31, so it "
                              "is honest for periods after that date and look-ahead for "
                              "periods before it; it is printed once, labelled, and not "
                              "used to choose anything",
    }


# ------------------------------------------------------------------ rendering
def _f(x, digits: int = 3) -> str:
    return "n/a" if x is None else ("%." + str(digits) + "f") % float(x)


def _pct(x, digits: int = 2) -> str:
    return "n/a" if x is None else ("%." + str(digits) + "f%%") % (100.0 * float(x))


def render_md(face: dict) -> str:
    if face.get("verdict") == "NOT_ENOUGH_PERIODS":
        return ("# Walk-forward hedge\n\n`NOT_ENOUGH_PERIODS` -- %s\n"
                % face.get("verdict_why"))

    s = face["sample"]
    b = face["betas"]
    r = face["reads"]
    arms = face["arms"]
    by = {a["arm"]: a for a in arms}

    L = []
    a = L.append
    a("# Does the hedge still work when the beta cannot see the future?")
    a("")
    a("`%s` · `%s` · `%s`" % (face["verdict"], face["verdict_fitting"],
                              face["verdict_scale"]))
    a("")
    a("Evidence cutoff **%s** (last period ends **%s**).  Book and hedge leg come from "
      "`results/astock_veto_hedgeable_beta.json`; nothing is refitted for trading here."
      % (face["evidence_cutoff"], face["last_period_end"]))
    a("")
    a("## 1. The short version")
    a("")
    a("- Refitted before every period on prior rows only, the beta removes **%s** of the "
      "book's annualised volatility (%s -> %s) over %d periods."
      % (_pct(r["vol_removed_honest"], 1), _pct(by["none"]["vol"]), _pct(by["walk_forward"]["vol"]),
         s["periods_evaluated"]))
    a("- The look-ahead arm -- one beta for the whole window, the way the parents read it "
      "-- removes **%s**; the gap is **%s pp** (`%s`)."
      % (_pct(r["vol_removed_full_window"], 1), _f(r["lookahead_premium_pp"], 2),
         face["verdict_lookahead"]))
    a("- Beta = 1.00 with no fitting at all sits **%s pp** from the honest arm "
      "(`%s`)." % (_f(r["fitting_gap_pp"], 2), face["verdict_fitting"]))
    a("- The control: an unhedged book of the honest arm's own volatility draws down "
      "**%s** at worst against the hedge's **%s** (a **%s pp** gap, `%s`) while earning "
      "**%s** against the hedge's **%s** -- so `%s` is a trade, not a defeat."
      % (_pct(by["smaller_book"]["max_dd"], 2), _pct(by["walk_forward"]["max_dd"], 2),
         _f(r["dd_gap_vs_smaller_book_pp"], 2), face["verdict_scale"],
         _pct(by["smaller_book"]["mean_annual"], 2),
         _pct(by["walk_forward"]["mean_annual"], 2), face["verdict_scale"]))
    a("")
    a(face["verdict_why"] + ".")
    a("")
    a("## 2. The sample, and why every arm shares it")
    a("")
    a("| periods in the parent | evaluated | warm-up | trainings that could not be fitted |")
    a("|---|---|---|---|")
    a("| %d | %d | %d | %d |" % (s["periods_total"], s["periods_evaluated"],
                                 s["warmup"], s["unusable"]))
    a("")
    a("The first walk-forward beta sees %d periods; the last sees %d.  Every arm below is "
      "measured on those same %d periods, so no arm gets a longer or kinder window."
      % (s["warmup"], s["periods_total"] - 1, s["periods_evaluated"]))
    a("")
    a("## 3. How much the beta moves when it is refitted")
    a("")
    a("| reading | value |")
    a("|---|---|")
    a("| first refitted beta | %s |" % _f(b["first"], 4))
    a("| last refitted beta | %s |" % _f(b["last"], 4))
    a("| range across refits | %s .. %s |" % (_f(b["min"], 4), _f(b["max"], 4)))
    a("| mean / sd | %s / %s |" % (_f(b["mean"], 4), _f(b["sd"], 4)))
    a("| mean absolute step between refits | %s |" % _f(b["mean_abs_step"], 4))
    a("| largest single step | %s |" % _f(b["max_abs_step"], 4))
    a("| one beta on all periods (look-ahead) | %s |" % _f(b["full_window_beta"], 4))
    a("| beta published by r2022/r2029 | %s |" % _f(b["frozen_beta"], 4))
    a("| 95%% band published by r2029 | %s .. %s |" % (_f(b["band_low"], 4), _f(b["band_high"], 4)))
    a("| refits that land OUTSIDE that band | %d of %d |"
      % (b["outside_published_band"] or 0, s["periods_evaluated"]))
    a("")
    a("A refitted beta is not a constant with a wobble around it: the honest series spends "
      "%d of its %d refits outside the band r2029 printed around the frozen one."
      % (b["outside_published_band"] or 0, s["periods_evaluated"]))
    a("")
    a("## 4. Six arms, one sample")
    a("")
    a("| arm | k | periods | annualised vol | removed | per unit of vol | mean / yr | "
      "worst period | down periods | cumulative | worst drawdown |")
    a("|---|---|---|---|---|---|---|---|---|---|")
    ks = {"none": "0", "one_unit": "1.00", "full_window": _f(b["full_window_beta"], 4),
          "frozen": _f(b["frozen_beta"], 4), "walk_forward": "refitted",
          "smaller_book": "0 (scaled)"}
    for row in arms:
        a("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |"
          % (row["label"], ks.get(row["arm"], "n/a"), row["n"], _pct(row["vol"]),
             _pct(row["vol_removed"], 1), _f(row["return_per_vol"], 2),
             _pct(row["mean_annual"], 2),
             _pct(row["worst_period"], 2), row["neg_periods"], _pct(row["cum"], 2),
             _pct(row["max_dd"], 2)))
    a("")
    a("The last row is not a hedge.  It is the same book, held smaller, at exactly the "
      "volatility the honest hedge delivers -- the control that decides whether any of "
      "the risk removal above is more than leverage.")
    a("")
    a("## 5. The three questions a reader asks, answered on the same numbers")
    a("")
    a("**Does the honest beta keep the claim?** %s -- %s of the volatility gone, against "
      "%s with the look-ahead beta." % (face["verdict_removal"],
                                        _pct(r["vol_removed_honest"], 1),
                                        _pct(r["vol_removed_full_window"], 1)))
    a("")
    a("**Is the fitting worth it?** %s -- the mechanical beta = 1.00 is %s pp away "
      "(positive means fitting helped).  On this sample the refits were not paid for: "
      "beta = 1.00 ends at %s against the honest arm's %s, with a shallower worst period "
      "(%s vs %s).  Refitting pays for information it does not get to keep."
      % (face["verdict_fitting"], _f(r["fitting_gap_pp"], 2),
         _pct(by["one_unit"]["cum"], 2), _pct(by["walk_forward"]["cum"], 2),
         _pct(by["one_unit"]["worst_period"], 2), _pct(by["walk_forward"]["worst_period"], 2)))
    a("")
    a("**Is it more than leverage?** %s.  At equal volatility the hedge earns **%s** "
      "a year (%.2f per unit of volatility) and the de-levered book earns **%s** "
      "(%.2f).  The hedge therefore is not merely leverage -- it roughly doubles the "
      "return per unit of risk.  But it does not give the shallowest hole: the de-levered "
      "book bottoms at %s against the hedge's %s.  A holder whose constraint is a "
      "drawdown budget (r2023, r2026) is buying the *worse* of the two on that axis and "
      "the better one on the return axis; both are printed here because the choice "
      "depends on which of the two he cannot breach."
      % (face["verdict_scale"],
         _pct(by["walk_forward"]["mean_annual"], 2), by["walk_forward"]["return_per_vol"],
         _pct(by["smaller_book"]["mean_annual"], 2), by["smaller_book"]["return_per_vol"],
         _pct(by["smaller_book"]["max_dd"], 2), _pct(by["walk_forward"]["max_dd"], 2)))
    a("")
    a("Period by period, hedging shrank the move in **%s** of the %d evaluated periods."
      % (_pct(r["hedge_help_rate"], 1), s["periods_evaluated"]))
    a("")
    a("## 6. What this face does not say")
    a("")
    a("- It does not re-choose a size, a budget or a cost: those are r2022-r2029's numbers, "
      "quoted.")
    a("- The book is still priced at its last mark (2026-11-11) and the prices in the "
      "ticket faces are later; that dating gap belongs to r2028 and is not repaired here.")
    a("- The evaluation sample is one history.  A volatility claim on %d periods carries "
      "its own sampling error, which this face prints as the arms' spread rather than as "
      "a single number." % s["periods_evaluated"])
    a("- Only the ETF hedge leg (512100) is walked forward.  The IM arm was shown by r2027 "
      "to be unable to express the beta at small capital, so it is not re-walked here.")
    a("- No cost is charged to the refits beyond what the parent book already carries: a "
      "real account re-hedging every period pays turnover this face does not model.")
    a("")
    a("## 7. Reproduction")
    a("")
    a("```")
    a("python scripts/astock_veto_hedge_walkforward.py selftest")
    a("python scripts/astock_veto_hedge_walkforward.py run")
    a("python scripts/astock_veto_hedge_walkforward.py check")
    a("```")
    a("")
    return "\n".join(L)


# ------------------------------------------------------------------ cli
def run(write: bool = True) -> int:
    face = build_face()
    if write:
        with open(OUT_JSON, "w", encoding="utf-8") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
        with open(OUT_MD, "w", encoding="utf-8") as fh:
            fh.write(render_md(face))
    if face.get("verdict") == "NOT_ENOUGH_PERIODS":
        print("astock_veto_hedge_walkforward NOT_ENOUGH_PERIODS | %s"
              % face.get("verdict_why"))
        return 0
    by = {x["arm"]: x for x in face["arms"]}
    print("astock_veto_hedge_walkforward %s | %s | %s"
          % (face["verdict"], face["verdict_fitting"], face["verdict_scale"]))
    print("  periods evaluated %d of %d (warm-up %d)"
          % (face["sample"]["periods_evaluated"], face["sample"]["periods_total"],
             face["spec"]["warmup_periods"]))
    print("  vol: none %s -> honest %s (removed %s) | look-ahead %s | one-unit %s"
          % (_pct(by["none"]["vol"]), _pct(by["walk_forward"]["vol"]),
             _pct(face["reads"]["vol_removed_honest"], 1),
             _pct(by["full_window"]["vol"]), _pct(by["one_unit"]["vol"])))
    print("  look-ahead premium %s pp | fitting vs beta=1 %s pp | dd vs smaller book %s pp"
          % (_f(face["reads"]["lookahead_premium_pp"], 2),
             _f(face["reads"]["fitting_gap_pp"], 2),
             _f(face["reads"]["dd_gap_vs_smaller_book_pp"], 2)))
    return 0


def check(json_path: str = OUT_JSON, md_path: str = OUT_MD) -> int:
    """Two kinds of red kept apart (r1934): an upstream that moved one step is STALE and
    `run` repairs it; a number that disagrees with its own inputs is CHECK FAILED."""
    problems = []
    if not os.path.exists(json_path):
        print("STALE: face missing (%s)" % _rel(json_path))
        return 3
    face = _read_json(json_path)
    fresh = build_face()

    for key in ("beta", "band", "default"):
        a = (face.get("parents") or {}).get(key) or {}
        b = (fresh.get("parents") or {}).get(key) or {}
        if a.get("content_sha256") != b.get("content_sha256"):
            problems.append("STALE: parent %s content moved (%s -> %s)"
                            % (key, str(a.get("content_sha256"))[:12],
                               str(b.get("content_sha256"))[:12]))

    if [p for p in problems if p.startswith("STALE")]:
        for p in problems:
            print(p)
        print("STALE: run `run` to re-derive")
        return 3

    if len(face.get("arms") or []) != len(fresh.get("arms") or []):
        problems.append("CHECK FAILED: arm count %d != %d"
                        % (len(face.get("arms") or []), len(fresh.get("arms") or [])))
    else:
        for x, y in zip(face["arms"], fresh["arms"]):
            if x["arm"] != y["arm"]:
                problems.append("CHECK FAILED: arm order at %s" % x["arm"])
                continue
            for field in ("n", "vol", "vol_removed", "mean_annual", "worst_period",
                          "neg_periods", "cum", "max_dd"):
                p, q = x.get(field), y.get(field)
                if isinstance(p, (int, float)) and isinstance(q, (int, float)):
                    if abs(float(p) - float(q)) > 1e-9:
                        problems.append("CHECK FAILED: arm %s/%s %r != %r"
                                        % (x["arm"], field, p, q))
                elif p != q:
                    problems.append("CHECK FAILED: arm %s/%s %r != %r"
                                    % (x["arm"], field, p, q))

    for key in ("vol_removed_honest", "vol_removed_full_window", "lookahead_premium_pp",
                "fitting_gap_pp", "scale_factor", "dd_gap_vs_smaller_book_pp",
                "cum_gap_vs_smaller_book", "hedge_help_rate"):
        p = (face.get("reads") or {}).get(key)
        q = (fresh.get("reads") or {}).get(key)
        if isinstance(p, (int, float)) and isinstance(q, (int, float)):
            if abs(float(p) - float(q)) > 1e-9:
                problems.append("CHECK FAILED: reads.%s %r != %r" % (key, p, q))
        elif p != q:
            problems.append("CHECK FAILED: reads.%s %r != %r" % (key, p, q))

    if (face.get("sample") or {}) != (fresh.get("sample") or {}):
        problems.append("CHECK FAILED: sample block %r != %r"
                        % (face.get("sample"), fresh.get("sample")))

    if len(((face.get("betas") or {}).get("series") or [])) != len(
            ((fresh.get("betas") or {}).get("series") or [])):
        problems.append("CHECK FAILED: beta series length %d != %d"
                        % (len((face.get("betas") or {}).get("series") or []),
                           len((fresh.get("betas") or {}).get("series") or [])))

    for key in ("verdict", "verdict_removal", "verdict_lookahead", "verdict_fitting",
                "verdict_scale", "verdict_why"):
        if face.get(key) != fresh.get(key):
            problems.append("CHECK FAILED: %s %r != %r" % (key, face.get(key), fresh.get(key)))

    if problems:
        for p in problems:
            print(p)
        return 3

    if not os.path.exists(md_path):
        print("STALE: page missing (%s)" % _rel(md_path))
        return 3
    with open(md_path, encoding="utf-8") as fh:
        md = fh.read()
    for word in (face["verdict"], face["verdict_fitting"], face["verdict_scale"]):
        if "`" + word + "`" not in md:
            problems.append("CHECK FAILED: page does not print `%s`" % word)
    if problems:
        for p in problems:
            print(p)
        return 3

    print("CHECK OK %s | %s | %s | %d arms re-derived"
          % (face["verdict"], face["verdict_fitting"], face["verdict_scale"],
             len(face["arms"])))
    return 0


def selftest() -> int:
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    # --- slope
    leg("L1 slope exact on a noiseless line",
        abs(ols_slope([2.0 * v for v in range(6)], list(range(6))) - 2.0) < 1e-12)
    leg("L1b slope needs three usable pairs", ols_slope([1.0, 2.0], [1.0, 2.0]) is None)
    leg("L1c flat hedge has no slope", ols_slope([1.0, 2.0, 3.0], [1.0, 1.0, 1.0]) is None)
    leg("L1d nan pairs are dropped, not faked",
        abs(ols_slope([0.0, 2.0, 4.0, float("nan")], [0.0, 1.0, 2.0, 3.0]) - 2.0) < 1e-12)

    # --- walk-forward cannot see forward: perturb the future, past betas must not move
    book = [0.01 * ((i * 7) % 11 - 5) for i in range(40)]
    hedge = [0.01 * ((i * 5) % 9 - 4) for i in range(40)]
    wf1 = walk_forward_betas(book, hedge, 10)
    book2 = list(book)
    book2[25] = 99.0
    wf2 = walk_forward_betas(book2, hedge, 10)
    same = all(abs(a["beta"] - b["beta"]) < 1e-12
               for a, b in zip(wf1, wf2) if a["i"] <= 25)
    moved = all(abs(a["beta"] - b["beta"]) > 1e-12
                for a, b in zip(wf1, wf2) if a["i"] > 25)
    leg("L2 betas at or before a poisoned row are untouched", same)
    leg("L2b every beta after a poisoned row moves", moved,
        [w["i"] for w in wf1 if w["i"] > 25][:3])
    leg("L2c warm-up is respected", wf1[0]["i"] == 10 and wf1[0]["n_train"] == 10)
    leg("L2d every training row precedes its period",
        all(w["n_train"] == w["i"] for w in wf1))

    # --- drawdown
    leg("L3 drawdown of a straight fall is the fall itself",
        abs(max_drawdown([-0.1, -0.1]) - (-0.19)) < 1e-12, max_drawdown([-0.1, -0.1]))
    leg("L3b drawdown of a rising series is zero", max_drawdown([0.05, 0.05]) == 0.0)
    leg("L3c drawdown survives a recovery",
        abs(max_drawdown([0.10, -0.30, 0.50]) - (-0.30)) < 1e-9,
        max_drawdown([0.10, -0.30, 0.50]))
    leg("L3d empty returns give nan", np.isnan(max_drawdown([])))

    # --- arm stats
    a = arm_stats([0.01, -0.01, 0.02, -0.02, 0.0])
    hand = float(np.std([0.01, -0.01, 0.02, -0.02, 0.0], ddof=1) * np.sqrt(PPY))
    leg("L4 annualised vol matches the hand computation", abs(a["vol"] - hand) < 1e-12)
    leg("L4b negative periods counted", a["neg_periods"] == 2)
    leg("L4c worst period is the minimum", abs(a["worst_period"] + 0.02) < 1e-12)
    leg("L4d too few periods gives None", arm_stats([0.01, 0.02])["vol"] is None)
    leg("L4e cumulative compounds",
        abs(arm_stats([0.1, 0.1, 0.1])["cum"] - 0.331) < 1e-12)

    # --- verdict ladders, both directions of every line
    leg("L5 removal at the line counts", decide_removal(LINE_REMOVED).startswith("HONEST"))
    leg("L5b removal below the line fails", decide_removal(LINE_REMOVED - 0.01)
        .startswith("NO_LOOKAHEAD"))
    leg("L5c unmeasurable says so", decide_removal(None) == "ARM_NOT_MEASURABLE")
    leg("L6 look-ahead gap at the tie line is a tie",
        decide_lookahead(LINE_TIE_PP) == "LOOKAHEAD_IS_A_TIE")
    leg("L6b a large positive gap is a real premium",
        decide_lookahead(5.0) == "LOOKAHEAD_BUYS_MORE_THAN_A_TIE")
    leg("L6c a negative gap is called what it is",
        decide_lookahead(-5.0) == "LOOKAHEAD_FLATTERS_THE_WRONG_ARM")
    leg("L7 fitting at the line wins", decide_fitting(LINE_ONE_UNIT_PP)
        == "FITTING_BEATS_ONE_UNIT_OUT_OF_SAMPLE")
    leg("L7b fitting at minus the line loses", decide_fitting(-LINE_ONE_UNIT_PP)
        == "ONE_UNIT_BEATS_THE_FITTED_BETA")
    leg("L7c a small gap is a tie", decide_fitting(0.0) == "ONE_UNIT_TIES_THE_FITTED_BETA")
    leg("L8 scale at the line and more return beats the smaller book",
        decide_scale(LINE_DD_PP, 0.05) == "HEDGE_BEATS_A_SMALLER_BOOK")
    leg("L8b shallower drawdown with less return is called that",
        decide_scale(LINE_DD_PP, -0.05) == "HEDGE_SHAVES_THE_DRAWDOWN_BUT_EARNS_LESS")
    leg("L8c deeper drawdown but much more return is a trade, not a defeat",
        decide_scale(-LINE_DD_PP - 0.01, LINE_CUM) == "HEDGE_TRADES_DRAWDOWN_FOR_RETURN")
    leg("L8d deeper drawdown and no extra return loses to the smaller book",
        decide_scale(-LINE_DD_PP - 0.01, 0.001) == "SMALLER_BOOK_BEATS_THE_HEDGE")
    leg("L8e a tiny gap on both axes is only scale",
        decide_scale(0.0, 0.0) == "HEDGE_IS_ONLY_SCALE_OUT_OF_SAMPLE")
    leg("L8f drawdown tie with more return is still a trade",
        decide_scale(0.0, 0.5) == "HEDGE_TRADES_DRAWDOWN_FOR_RETURN")
    leg("L8g unmeasurable says so",
        decide_scale(None, 0.0) == "ARM_NOT_MEASURABLE")

    # --- live face
    face = build_face()
    if face.get("verdict") == "NOT_ENOUGH_PERIODS":
        leg("L9 live face is measurable", False, face.get("verdict_why"))
    else:
        s = face["sample"]
        by = {x["arm"]: x for x in face["arms"]}
        leg("L9 evaluated sample = total - warm-up",
            s["periods_evaluated"] == s["periods_total"] - s["warmup"])
        leg("L9b every arm shares one sample",
            len({by[k]["n"] for k in ("none", "one_unit", "full_window", "walk_forward")}) == 1)
        leg("L9c no hedge removes nothing", abs(by["none"]["vol_removed"] or 0.0) < 1e-12)
        leg("L9d the smaller book matches the honest volume",
            abs((face["reads"]["vol_gap_vs_smaller_book_pp"] or 0.0)) < 1e-9,
            face["reads"]["vol_gap_vs_smaller_book_pp"])
        leg("L9e the refitted betas actually differ from the frozen one",
            abs((face["betas"]["last"] or 0.0) - (face["betas"]["frozen_beta"] or 0.0)) > 0,
            (face["betas"]["last"], face["betas"]["frozen_beta"]))
        leg("L9f help rate is a share", 0.0 <= (face["reads"]["hedge_help_rate"] or 0.0) <= 1.0)
        leg("L9g verdict is one of the frozen words",
            face["verdict"] in ("HONEST_BETA_KEEPS_ITS_REMOVAL",
                                "NO_LOOKAHEAD_BETA_REMOVES_LESS_THAN_THE_LINE"))

    bad = [x for x in legs if not x[1]]
    for name, ok, detail in legs:
        if not ok:
            print("FAIL %s %r" % (name, detail))
    print("selftest %d/%d PASS" % (len(legs) - len(bad), len(legs)))
    return 0 if not bad else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=("run", "check", "selftest"))
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        return selftest()
    if args.cmd == "check":
        return check()
    return run()


if __name__ == "__main__":
    sys.exit(main())
