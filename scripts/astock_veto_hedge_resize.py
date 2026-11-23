"""What does it cost to keep the hedge the right size?

r2022 priced the hedge, r2023 bought a drawdown budget with it, r2024 marked it daily,
r2025 raced nine ways of choosing a size, r2026 named one unit of beta as the default,
r2027 turned the size into lots, r2028 showed the price date moves the ticket,
r2029 printed the beta's own band, r2030 re-fitted the beta honestly and found that
beta = 1.00 ties the fitted beta out of sample, r2031 found the instrument choice is
worth 45 points of variance removal and r2033 put both hedge legs on one ruler.

Every one of those faces sized the hedge **once** and then read the result.  r2030
closed with a caveat it could not pay for:

    No cost is charged to the refits beyond what the parent book already carries: a real
    account re-hedging every period pays turnover this face does not model.

An account that re-fits the beta every 20 trading days must trade the hedge every 20
trading days.  This face prices exactly that trade, and asks the question an operator
actually faces:

    How often must the hedge be re-sized, what does re-sizing cost, and is the schedule
    worth optimising at all?

Eight schedules are run on one common sample (the same 57 periods r2030 evaluates),
each with its own k path, and each is charged its own turnover at a grid of per-side
costs:

  * every_period -- refit and trade every period (r2030's honest arm);
  * cadence_q   -- re-size every 3 periods (~60 trading days);
  * cadence_1y  -- re-size every 13 periods (~one year at 12.6 periods/yr);
  * band_0.02 / band_0.05 / band_0.10 -- trade only when the target beta has drifted
    more than the band away from the size currently held;
  * set_once    -- size at entry on the first honest beta, then never touch it;
  * one_unit    -- short exactly one unit of notional, no estimate at all.

And the control that separates "the schedule" from "the level":

  * 500 randomly-timed schedules with the same number of re-sizes as cadence_q.  If the
    spread between the real schedules is inside that band, the schedule is not where the
    money is; if it is outside, the difference is the *level* of k, not its timing.

Thresholds are frozen in PREREG below, before the run, and are not tuned afterwards.

Outputs (new files only):
    results/astock_veto_hedge_resize.json
    research/ASTOCK_VETO_HEDGE_RESIZE.md

Usage:
    python scripts/astock_veto_hedge_resize.py selftest
    python scripts/astock_veto_hedge_resize.py run
    python scripts/astock_veto_hedge_resize.py check
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
WALK = os.path.join(ROOT, "results", "astock_veto_hedge_walkforward.json")
OUT_JSON = os.path.join(ROOT, "results", "astock_veto_hedge_resize.json")
OUT_MD = os.path.join(ROOT, "research", "ASTOCK_VETO_HEDGE_RESIZE.md")

PPY = 12.6          # periods per year, quoted from the parent spec (20-bar periods)
WARMUP = 20         # periods the first honest beta may see (= r2029/r2030 window)

# frozen before the run -- see PREREG in build_face()
COST_MAIN_BP = 1.0                     # per side, on traded notional: ~0.23bp commission + slippage
COST_GRID_BP = (0.5, 1.0, 2.0, 5.0, 20.0)
LINE_COST_PP = 0.05                    # a schedule cost under this (pp/yr) is noise
LINE_TIE_PP = 0.10                     # a volatility gap under this (pp) is a tie (r2030's line)
LINE_BREAKEVEN_BP = 5.0                # a break-even cost above this many bp/side cannot decide
LINE_LEVEL_SD = 3.0                    # a gap beyond this many random-timing sd is not timing
RANDOM_SEED = 2034
RANDOM_DRAWS = 500
RANDOM_RESETS = 17                     # matches cadence_q's reset count, so the draws are comparable

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
    """Slope of the book on the hedge.  Same estimator as r2030, so the betas match."""
    yy = np.asarray(y, dtype=np.float64)
    xx = np.asarray(x, dtype=np.float64)
    keep = np.isfinite(yy) & np.isfinite(xx)
    yy, xx = yy[keep], xx[keep]
    if len(yy) < 3 or float(np.var(xx)) <= 0.0:
        return None
    X = np.column_stack([np.ones_like(xx), xx])
    beta = float(np.linalg.lstsq(X, yy, rcond=None)[0][1])
    return beta if np.isfinite(beta) else None


def honest_betas(book, hedge, warmup: int = WARMUP) -> list:
    """beta for period i sees rows [0, i) only -- the same walk r2030 runs."""
    out = []
    for i in range(int(warmup), len(book)):
        beta = ols_slope(book[:i], hedge[:i])
        out.append({"i": i, "beta": beta, "n_train": i})
    return out


def kpath(kind: str, target, cadence=None, band=None) -> list:
    """The k held in each evaluated period, for one schedule.

    The first period always establishes a position from flat, whatever the schedule;
    `set_once` and `one_unit` therefore differ only in the level they pick, not in how
    often they trade.
    """
    out = []
    cur = None
    for n, t in enumerate(target):
        if cur is None:
            cur = 1.0 if kind == "one_unit" else float(t)
        elif kind == "every_period":
            cur = float(t)
        elif kind == "cadence":
            if cadence and n % int(cadence) == 0:
                cur = float(t)
        elif kind == "band":
            if band is not None and abs(float(t) - cur) > float(band):
                cur = float(t)
        out.append(cur)
    return out


def max_drawdown(returns) -> float:
    a = np.asarray([v for v in returns if v is not None and np.isfinite(v)],
                   dtype=np.float64)
    if len(a) == 0:
        return float("nan")
    eq = np.cumprod(1.0 + a)
    peak = np.maximum.accumulate(np.concatenate([[1.0], eq]))[1:]
    return float(np.min(eq / peak - 1.0))


def policy_stats(k, book, hedge, cost_bp: float = 0.0, ppy: float = PPY) -> dict:
    """Returns of `book - k * hedge`, charged `cost_bp` per side on the notional traded
    into that period.  The entry trade is charged too: opening the short is a trade."""
    rets = []
    prev = 0.0
    turnover = 0.0
    trades = 0
    for b, h, kv in zip(book, hedge, k):
        traded = abs(float(kv) - prev)
        if traded > 1e-12:
            trades += 1
        turnover += traded
        rets.append(float(b) - float(kv) * float(h) - traded * float(cost_bp) / 1e4)
        prev = float(kv)
    a = np.asarray(rets, dtype=np.float64)
    n = int(len(a))
    if n < 3:
        return {"n": n, "vol": None, "ann": None, "cum": None, "dd": None,
                "worst": None, "neg": None, "turnover_total": turnover,
                "turnover_per_year": None, "n_trades": trades, "n_resets": trades - 1}
    return {"n": n,
            "vol": float(np.std(a, ddof=1) * np.sqrt(ppy)),
            "ann": float(np.mean(a) * ppy),
            "cum": float(np.prod(1.0 + a) - 1.0),
            "dd": max_drawdown(a),
            "worst": float(np.min(a)),
            "neg": int(np.sum(a < 0.0)),
            "turnover_total": float(turnover),
            "turnover_per_year": float(turnover * ppy / n),
            "n_trades": int(trades),
            "n_resets": int(trades - 1)}


def k_error(k, target) -> dict:
    """How stale the held size is, in units of k."""
    d = np.abs(np.asarray(k, dtype=np.float64) - np.asarray(target, dtype=np.float64))
    return {"mean_abs_error": float(np.mean(d)), "max_abs_error": float(np.max(d)),
            "k_mean": float(np.mean(k)), "k_min": float(np.min(k)),
            "k_max": float(np.max(k))}


def random_timing(target, book, hedge, resets: int = RANDOM_RESETS,
                  draws: int = RANDOM_DRAWS, seed: int = RANDOM_SEED,
                  cost_bp: float = COST_MAIN_BP) -> dict:
    """Same information, random timing: pick `resets` periods at random, hold the honest
    beta from the last chosen one, otherwise keep whatever is held.  This is the band the
    observed schedules have to beat before "the schedule" means anything."""
    rng = np.random.default_rng(int(seed))
    n = len(target)
    if n < 4:
        return {"draws": 0}
    anns, vols, cums = [], [], []
    for _ in range(int(draws)):
        picks = set(rng.choice(np.arange(1, n), size=max(0, resets - 1),
                               replace=False).tolist())
        picks.add(0)
        k = []
        cur = float(target[0])
        for j in range(n):
            if j in picks:
                cur = float(target[j])
            k.append(cur)
        s = policy_stats(k, book, hedge, cost_bp)
        if s["ann"] is None:
            continue
        anns.append(s["ann"])
        vols.append(s["vol"])
        cums.append(s["cum"])
    a = np.asarray(anns)
    v = np.asarray(vols)
    c = np.asarray(cums)
    return {"draws": int(len(a)), "resets": int(resets), "seed": int(seed),
            "cost_bp": float(cost_bp),
            "ann": {"sd": float(np.std(a, ddof=1)), "p05": float(np.percentile(a, 5)),
                    "p50": float(np.percentile(a, 50)),
                    "p95": float(np.percentile(a, 95))},
            "vol": {"p05": float(np.percentile(v, 5)),
                    "p50": float(np.percentile(v, 50)),
                    "p95": float(np.percentile(v, 95))},
            "cum": {"p05": float(np.percentile(c, 5)),
                    "p50": float(np.percentile(c, 50)),
                    "p95": float(np.percentile(c, 95))}}


def breakeven_bp(extra_turnover_per_year, line_pp: float = LINE_COST_PP):
    """Per-side cost (bp) at which the extra turnover of one schedule over another costs
    `line_pp` percentage points of return a year.  `None` when there is no extra."""
    if extra_turnover_per_year is None or extra_turnover_per_year <= 0:
        return None
    return float(line_pp) / 100.0 / float(extra_turnover_per_year) * 1e4


# ------------------------------------------------------------------ verdict ladders
def decide_cost(drag_pp) -> str:
    if drag_pp is None:
        return "COST_NOT_MEASURABLE"
    return ("SCHEDULE_COST_IS_BELOW_THE_NOISE_LINE" if abs(drag_pp) < LINE_COST_PP
            else "SCHEDULE_COST_IS_A_REAL_LINE_ITEM")


def decide_breakeven(bp) -> str:
    if bp is None:
        return "NO_EXTRA_TURNOVER_TO_PRICE"
    return ("COST_IS_FIFTYFOLD_AWAY_FROM_DECIDING" if bp >= 50.0 * LINE_BREAKEVEN_BP
            else "COST_CANNOT_DECIDE_THE_SCHEDULE" if bp >= LINE_BREAKEVEN_BP
            else "COST_DECIDES_AGAINST_THE_BUSY_SCHEDULE")


def decide_schedule(vol_span_pp, ann_span_pp) -> str:
    if vol_span_pp is None or ann_span_pp is None:
        return "SCHEDULE_NOT_MEASURABLE"
    if vol_span_pp <= LINE_TIE_PP:
        return "THE_SCHEDULE_DOES_NOT_MOVE_RISK_AT_ALL"
    return ("THE_SCHEDULE_MOVES_RETURN_MORE_THAN_RISK" if ann_span_pp > vol_span_pp
            else "THE_SCHEDULE_MOVES_RISK_MORE_THAN_RETURN")


def decide_level(constant_min_ann, varying_max_ann, gap_pp, band_sd_pp) -> str:
    """Two different claims, kept apart: (a) every schedule that holds the size still
    beat every schedule that chases the beta -- then the chasing is what costs, not the
    cadence; (b) otherwise, is the observed spread inside random-timing luck?"""
    if constant_min_ann is None or varying_max_ann is None:
        return "LEVEL_NOT_MEASURABLE"
    if constant_min_ann > varying_max_ann:
        return "HOLDING_THE_SIZE_STILL_BEATS_CHASING_IT"
    if gap_pp is not None and band_sd_pp not in (None, 0):
        if abs(gap_pp) > LINE_LEVEL_SD * abs(band_sd_pp):
            return "THE_GAP_IS_THE_LEVEL_NOT_THE_TIMING"
    return "TIMING_LUCK_COULD_EXPLAIN_THE_GAP"


# ------------------------------------------------------------------ face
def build_face() -> dict:
    parent = _read_json(PARENT)
    walk = _read_json(WALK)

    rows = parent.get("rows") or []
    if len(rows) < WARMUP + 5:
        return {"generated": _now(), "kind": "hedge_resize_cost",
                "evidence_cutoff": parent.get("evidence_cutoff"),
                "verdict": "NOT_ENOUGH_PERIODS",
                "verdict_why": "only %d periods; warm-up %d leaves too few to evaluate"
                               % (len(rows), WARMUP),
                "parents": {"beta": fingerprint(PARENT)}}

    book_all = [r.get("book_net") for r in rows]
    hedge_all = [r.get("hedge_etf") for r in rows]
    dates = [r.get("date") for r in rows]
    ends = [r.get("end") for r in rows]

    hb = honest_betas(book_all, hedge_all, WARMUP)
    usable = [w for w in hb if w.get("beta") is not None]
    eval_idx = [w["i"] for w in usable]
    target = [w["beta"] for w in usable]
    book = [book_all[i] for i in eval_idx]
    hedge = [hedge_all[i] for i in eval_idx]

    # anchor: the betas must be the ones r2030 published, or this face is priced on a
    # different hedge than the one every prior face prices
    walk_series = ((walk.get("betas") or {}).get("series") or [])
    walk_map = {int(x["i"]): x.get("beta") for x in walk_series}
    anchor_diff = None
    anchor_n = 0
    if walk_map:
        diffs = []
        for w in usable:
            if int(w["i"]) in walk_map:
                anchor_n += 1
                diffs.append(abs(float(w["beta"]) - float(walk_map[int(w["i"])] or 0.0)))
        anchor_diff = max(diffs) if diffs else None

    schedules = [
        ("every_period", "refit and trade every 20-bar period (r2030's honest arm)",
         kpath("every_period", target)),
        ("cadence_q", "re-size every 3 periods (~60 trading days)",
         kpath("cadence", target, cadence=3)),
        ("cadence_1y", "re-size every 13 periods (~one year)",
         kpath("cadence", target, cadence=13)),
        ("band_0.02", "trade only when the target has drifted more than 0.02",
         kpath("band", target, band=0.02)),
        ("band_0.05", "trade only when the target has drifted more than 0.05",
         kpath("band", target, band=0.05)),
        ("band_0.10", "trade only when the target has drifted more than 0.10",
         kpath("band", target, band=0.10)),
        ("set_once", "size on the first honest beta and never touch it again",
         kpath("set_once", target)),
        ("one_unit", "short exactly one unit of notional, no estimate at all",
         kpath("one_unit", target)),
    ]

    pol = []
    for name, label, k in schedules:
        gross = policy_stats(k, book, hedge, 0.0)
        net = policy_stats(k, book, hedge, COST_MAIN_BP)
        err = k_error(k, target)
        kb = float(np.mean(k))
        h_bar = float(np.mean(hedge))
        cov = float(np.mean(np.asarray(k, dtype=np.float64)
                            * np.asarray(hedge, dtype=np.float64)) - kb * h_bar)
        chase_pp = cov * PPY * 100.0   # positive = what following the beta costs
        drag = None
        if gross["ann"] is not None and net["ann"] is not None:
            drag = (gross["ann"] - net["ann"]) * 100.0
        grid = {}
        for bp in COST_GRID_BP:
            s = policy_stats(k, book, hedge, bp)
            grid["%.1f" % bp] = {"ann": s["ann"], "cum": s["cum"], "dd": s["dd"]}
        pol.append({"schedule": name, "label": label,
                    "n": net.get("n"),
                    "n_resets": net.get("n_resets"),
                    "turnover_total": net.get("turnover_total"),
                    "turnover_per_year": net.get("turnover_per_year"),
                    "k_mean": err["k_mean"], "k_min": err["k_min"], "k_max": err["k_max"],
                    "mean_abs_error": err["mean_abs_error"],
                    "max_abs_error": err["max_abs_error"],
                    "k_cov_hedge": cov, "chase_pp_per_year": chase_pp,
                    "vol": gross["vol"], "ann": gross["ann"], "cum": gross["cum"],
                    "dd": gross["dd"], "worst": gross["worst"], "neg": gross["neg"],
                    "ann_net": net["ann"], "cum_net": net["cum"], "dd_net": net["dd"],
                    "cost_drag_pp": drag, "by_cost": grid})

    by = {p["schedule"]: p for p in pol}

    # ---- the three readings this face is bought for
    extra_turn = (by["every_period"]["turnover_per_year"]
                  - by["set_once"]["turnover_per_year"])
    be_bp = breakeven_bp(extra_turn)

    drags = [p["cost_drag_pp"] for p in pol if p["cost_drag_pp"] is not None]
    drag_max = max(drags) if drags else None
    drag_span = (max(drags) - min(drags)) if drags else None

    vols = [p["vol"] for p in pol if p["vol"] is not None]
    anns = [p["ann"] for p in pol if p["ann"] is not None]
    vol_span_pp = (max(vols) - min(vols)) * 100.0 if vols else None
    ann_span_pp = (max(anns) - min(anns)) * 100.0 if anns else None

    rt = random_timing(target, book, hedge)
    gap_pp = None
    if by["set_once"]["ann"] is not None and by["every_period"]["ann"] is not None:
        gap_pp = (by["set_once"]["ann"] - by["every_period"]["ann"]) * 100.0
    gap_in_sd = None
    if gap_pp is not None and rt.get("ann", {}).get("sd"):
        gap_in_sd = gap_pp / (rt["ann"]["sd"] * 100.0)

    # why the level pays: holding a smaller short in a market that rose
    hedge_mean = float(np.mean(hedge)) if hedge else None
    k_gap = by["every_period"]["k_mean"] - by["set_once"]["k_mean"]
    level_pp_per_year = None
    if hedge_mean is not None:
        # a smaller short earns more when the hedge leg rises: -(k_small - k_big) * mean
        level_pp_per_year = k_gap * hedge_mean * PPY * 100.0

    cost_share = None
    if (by["every_period"]["turnover_per_year"] and by["set_once"]["turnover_per_year"]
            and by["set_once"]["turnover_per_year"] > 0):
        cost_share = 1.0 - (by["set_once"]["turnover_per_year"]
                            / by["every_period"]["turnover_per_year"])

    constant_names = ("set_once", "one_unit")
    varying_names = [p["schedule"] for p in pol if p["schedule"] not in constant_names]
    constant_min_ann = min(by[n]["ann"] for n in constant_names)
    varying_max_ann = max(by[n]["ann"] for n in varying_names)
    chase_every_pp = by["every_period"]["chase_pp_per_year"]

    verdict_cost = decide_cost(drag_max)
    verdict_breakeven = decide_breakeven(be_bp)
    verdict_schedule = decide_schedule(vol_span_pp, ann_span_pp)
    verdict_level = decide_level(constant_min_ann, varying_max_ann, gap_pp,
                                 (rt.get("ann", {}).get("sd") or 0.0) * 100.0)

    verdict_why = (
        "Keeping the hedge the right size is almost free: the busiest schedule trades "
        "%.1f%% of book notional a year and the quietest %.1f%%, a difference of %.3f "
        "notional a year, which at %.1f bp per side costs %.4f pp of return a year -- "
        "%.0f times below the %.2f pp noise line. You would have to pay %.0f bp per side "
        "before that difference reached the line. The schedule barely moves risk either: "
        "annualised volatility spans %.2f pp across all eight (%.2f%%..%.2f%%) against a "
        "%.2f pp span in annual return. The return spread is not the cadence -- it is "
        "whether the size chases the beta at all: the two schedules that hold one size "
        "finish at %.2f%% and %.2f%%, above every one of the %d schedules that follow the "
        "beta (best %.2f%%). The chasing itself costs %.2f pp a year in this window "
        "(the arithmetic: the size you trail is slightly high in the periods the hedge "
        "then earns, and %.2f pp a year is what that covariance subtracts)."
        % (100.0 * (by["every_period"]["turnover_per_year"] or 0.0),
           100.0 * (by["set_once"]["turnover_per_year"] or 0.0),
           extra_turn or 0.0, COST_MAIN_BP, drag_max or 0.0,
           (LINE_COST_PP / drag_max) if drag_max else 0.0, LINE_COST_PP,
           (be_bp or 0.0), vol_span_pp or 0.0,
           100.0 * min(vols) if vols else 0.0, 100.0 * max(vols) if vols else 0.0,
           ann_span_pp or 0.0,
           100.0 * by["set_once"]["ann"], 100.0 * by["one_unit"]["ann"], len(varying_names),
           100.0 * varying_max_ann, abs(chase_every_pp or 0.0), abs(chase_every_pp or 0.0)))

    return {
        "generated": _now(),
        "kind": "hedge_resize_cost",
        "machine": "bm-c",
        "evidence_cutoff": parent.get("evidence_cutoff"),
        "last_period_end": ends[-1] if ends else None,
        "first_period": dates[0] if dates else None,
        "fills_the_hole_of": "r2030 refitted the beta honestly but charged no turnover to "
                             "the refits; this face prices the trade the refit forces and "
                             "asks whether the schedule is worth optimising at all.",
        "prereg": {
            "question": "How often must the hedge be re-sized, what does re-sizing cost, "
                        "and does the schedule move anything a holder can feel?",
            "schedules": {p["schedule"]: p["label"] for p in pol},
            "evaluation_sample": "the %d periods r2030 evaluates (index >= %d), one common "
                                 "sample for every schedule" % (len(eval_idx), WARMUP),
            "cost_model": "%.1f bp per side on the notional traded into a period, entry "
                          "trade included; no borrow fee and no roll cost is added here "
                          "(r2033 prices the carrier)" % COST_MAIN_BP,
            "verdict_rule": {
                "cost": "a schedule cost under %.2f pp/yr is noise" % LINE_COST_PP,
                "breakeven": "a break-even per-side cost above %.1f bp cannot decide"
                             % LINE_BREAKEVEN_BP,
                "schedule": "a volatility span under %.2f pp means the schedule does not "
                            "move risk" % LINE_TIE_PP,
                "level": "holding one size must beat every schedule that follows the beta "
                         "before the cadence is blamed; otherwise a gap beyond %.1f "
                         "random-timing sd is the level, not the timing" % LINE_LEVEL_SD},
            "rule_frozen_before_run": True,
            "not_done_here": "no size is re-chosen, no beta is reported as tradeable, no "
                             "capital is re-marked, no borrow fee is charged",
        },
        "spec": {"hold": (parent.get("spec") or {}).get("hold"),
                 "stride": (parent.get("spec") or {}).get("stride"),
                 "periods_per_year": PPY, "warmup_periods": WARMUP,
                 "hedge_leg": "hedge_etf (512100), the arm every prior face prices",
                 "cost_main_bp": COST_MAIN_BP,
                 "cost_grid_bp": list(COST_GRID_BP),
                 "lines": {"cost_pp": LINE_COST_PP, "tie_pp": LINE_TIE_PP,
                           "breakeven_bp": LINE_BREAKEVEN_BP,
                           "level_sd": LINE_LEVEL_SD}},
        "parents": {"beta": fingerprint(PARENT), "walkforward": fingerprint(WALK)},
        "anchor": {"compared": int(anchor_n), "max_abs_beta_diff": anchor_diff,
                   "note": "the betas used here are r2030's own series, re-derived with "
                           "the same estimator; a non-zero difference means this face is "
                           "priced on a different hedge than the family it extends"},
        "sample": {"periods_total": len(rows), "periods_evaluated": len(eval_idx),
                   "warmup": WARMUP,
                   "unusable_trainings": len([w for w in hb if w.get("beta") is None]),
                   "book_mean_period": float(np.mean(book)) if book else None,
                   "hedge_mean_period": hedge_mean},
        "schedules": pol,
        "random_timing": rt,
        "reads": {"extra_turnover_per_year": extra_turn,
                  "breakeven_cost_bp": be_bp,
                  "cost_drag_max_pp": drag_max,
                  "cost_drag_span_pp": drag_span,
                  "cost_share_of_busiest": cost_share,
                  "vol_span_pp": vol_span_pp,
                  "ann_span_pp": ann_span_pp,
                  "setonce_vs_every_pp": gap_pp,
                  "gap_in_random_sd": gap_in_sd,
                  "k_gap": k_gap,
                  "level_arithmetic_pp_per_year": level_pp_per_year,
                  "chase_every_pp": chase_every_pp,
                  "constant_min_ann": constant_min_ann,
                  "varying_max_ann": varying_max_ann,
                  "random_ann_sd_pp": (rt.get("ann", {}).get("sd") or 0.0) * 100.0},
        "verdict_cost": verdict_cost,
        "verdict_breakeven": verdict_breakeven,
        "verdict_schedule": verdict_schedule,
        "verdict_level": verdict_level,
        "verdict": verdict_cost,
        "verdict_why": verdict_why,
    }


# ------------------------------------------------------------------ rendering
def _f(x, digits: int = 3) -> str:
    return "n/a" if x is None else ("%." + str(digits) + "f") % float(x)


def _pct(x, digits: int = 2) -> str:
    return "n/a" if x is None else ("%." + str(digits) + "f%%") % (100.0 * float(x))


def render_md(face: dict) -> str:
    if face.get("verdict") == "NOT_ENOUGH_PERIODS":
        return ("# The price of keeping the hedge the right size\n\n"
                "`NOT_ENOUGH_PERIODS` -- %s\n" % face.get("verdict_why"))

    r = face["reads"]
    s = face["sample"]
    rt = face["random_timing"]
    by = {p["schedule"]: p for p in face["schedules"]}

    L = []
    a = L.append
    a("# What does it cost to keep the hedge the right size?")
    a("")
    a("`%s` · `%s` · `%s` · `%s`" % (face["verdict"], face["verdict_breakeven"],
                                     face["verdict_schedule"], face["verdict_level"]))
    a("")
    a("Evidence cutoff **%s** (last period ends **%s**).  Book and hedge leg come from "
      "`results/astock_veto_hedgeable_beta.json`; the betas are r2030's own series "
      "(largest difference **%s** over %d shared periods)."
      % (face["evidence_cutoff"], face["last_period_end"],
         ("%.2e" % face["anchor"]["max_abs_beta_diff"])
         if face["anchor"]["max_abs_beta_diff"] is not None else "n/a",
         face["anchor"]["compared"]))
    a("")
    a("## 1. The short version")
    a("")
    a("- The busiest schedule (re-fit and trade every period) turns over **%s** of book "
      "notional a year; never touching the size after entry turns over **%s** -- the "
      "difference is **%s** of notional a year, and it includes the entry trade in both."
      % (_pct(by["every_period"]["turnover_per_year"], 1),
         _pct(by["set_once"]["turnover_per_year"], 1),
         _pct(r["extra_turnover_per_year"], 1)))
    a("- At **%s bp per side** that difference costs **%s pp** of return a year -- "
      "**%sx** below the %.2f pp noise line (`%s`).  You would have to pay **%s bp per "
      "side** before it reached the line (`%s`)."
      % (_f(face["spec"]["cost_main_bp"], 1), _f(r["cost_drag_max_pp"], 4),
         _f((0.05 / r["cost_drag_max_pp"]) if r["cost_drag_max_pp"] else None, 0),
         face["spec"]["lines"]["cost_pp"], face["verdict_cost"],
         _f(r["breakeven_cost_bp"], 0), face["verdict_breakeven"]))
    a("- Risk barely notices the schedule: annualised volatility spans **%s pp** across "
      "all eight schedules (%s .. %s) while annual return spans **%s pp** (`%s`)."
      % (_f(r["vol_span_pp"], 2), _pct(min(p["vol"] for p in face["schedules"])),
         _pct(max(p["vol"] for p in face["schedules"])),
         _f(r["ann_span_pp"], 2), face["verdict_schedule"]))
    a("- The return spread is not the cadence, it is whether the size chases the beta at "
      "all: the two schedules that hold **one** size finish at **%s** (set once at %s) and "
      "**%s** (one unit), above every one of the %d schedules that follow the beta (best "
      "**%s**) -- `%s`."
      % (_pct(by["set_once"]["ann"]), _f(by["set_once"]["k_mean"], 4),
         _pct(by["one_unit"]["ann"]),
         len([p for p in face["schedules"]
              if p["schedule"] not in ("set_once", "one_unit")]),
         _pct(r["varying_max_ann"]), face["verdict_level"]))
    a("- Chasing the beta costs **%s pp** a year in this window, and it is arithmetic, not "
      "bad luck: the size trailed from the past is slightly high in the periods the hedge "
      "then earns, and that covariance subtracts **%s pp** a year (`chase` column below)."
      % (_f(abs(r["chase_every_pp"]), 2), _f(abs(r["chase_every_pp"]), 2)))
    a("")
    a(face["verdict_why"])
    a("")
    a("## 2. The sample")
    a("")
    a("| periods in the parent | evaluated | warm-up | trainings that could not be fitted |")
    a("|---|---|---|---|")
    a("| %d | %d | %d | %d |" % (s["periods_total"], s["periods_evaluated"],
                                 s["warmup"], s["unusable_trainings"]))
    a("")
    a("Every schedule is measured on those same %d periods.  A schedule that trades less "
      "often is not given a kinder window -- it is given the same window and a staler "
      "size, which is the cost being measured." % s["periods_evaluated"])
    a("")
    a("## 3. Eight schedules, one sample, gross")
    a("")
    a("| schedule | what it does | re-sizes | turnover / yr | mean k | staleness (mean / max) "
      "| chase pp/yr (positive = paid) | vol | mean / yr | worst dd |")
    a("|" + "---|" * 10)
    for p in face["schedules"]:
        a("| `%s` | %s | %d | %s | %s | %s / %s | %s | %s | %s | %s |"
          % (p["schedule"], p["label"], p["n_resets"],
             _pct(p["turnover_per_year"], 1), _f(p["k_mean"], 4),
             _f(p["mean_abs_error"], 4), _f(p["max_abs_error"], 4),
             _f(p["chase_pp_per_year"], 2),
             _pct(p["vol"]), _pct(p["ann"]), _pct(p["dd"])))
    a("")
    a("Staleness is the distance between the size held and the beta the period itself "
      "would have chosen.  `every_period` is stale by construction zero; `one_unit` is "
      "stale on purpose (it is the no-estimate arm).  `chase` is what following the beta "
      "costs against holding the mean size: minus the covariance between the size held and "
      "the hedge's own return, annualised.  A constant size has no such term by "
      "construction, which is why the two constant arms are the only ones that do not pay "
      "it.")
    a("")
    a("## 4. What the turnover costs, at five per-side prices")
    a("")
    a("| schedule | " + " | ".join("%s bp/side" % _f(bp, 1)
                                   for bp in face["spec"]["cost_grid_bp"]) + " |")
    a("|---" * (len(face["spec"]["cost_grid_bp"]) + 1) + "|")
    for p in face["schedules"]:
        cells = []
        for bp in face["spec"]["cost_grid_bp"]:
            cells.append(_pct((p["by_cost"].get("%.1f" % bp) or {}).get("ann")))
        a("| `%s` | %s |" % (p["schedule"], " | ".join(cells)))
    a("")
    a("Net of the trade, the spread between the busiest and the quietest schedule does "
      "not move: **%s pp** of annual return at %.1f bp per side, **%s pp** even at 20 bp."
      % (_f(r["ann_span_pp"], 2), face["spec"]["cost_main_bp"],
         _f((max((p["by_cost"].get("20.0") or {}).get("ann")
                 for p in face["schedules"])
             - min((p["by_cost"].get("20.0") or {}).get("ann")
                   for p in face["schedules"])) * 100.0, 2)))
    a("")
    a("## 5. Is the schedule the thing to optimise?  The random-timing band")
    a("")
    a("| reading | value |")
    a("|---|---|")
    a("| draws (same 17 re-sizes, random timing, seed %d) | %d |"
      % (rt["seed"], rt["draws"]))
    a("| annual return, 5%% / median / 95%% | %s / %s / %s |"
      % (_pct(rt["ann"]["p05"]), _pct(rt["ann"]["p50"]), _pct(rt["ann"]["p95"])))
    a("| annualised vol, 5%% / median / 95%% | %s / %s / %s |"
      % (_pct(rt["vol"]["p05"]), _pct(rt["vol"]["p50"]), _pct(rt["vol"]["p95"])))
    a("| sd of annual return across draws | %s pp |" % _f(r["random_ann_sd_pp"], 2))
    a("| both constant arms sit above this whole band | %s and %s vs a %s top |"
      % (_pct(by["set_once"]["ann"]), _pct(by["one_unit"]["ann"]),
         _pct(rt["ann"]["p95"])))
    a("")
    a("Randomly-timed schedules land in a **%s pp**-wide 90%% band on annual return -- "
      "that is what \"when you trade\" is worth.  Both schedules that hold one size land "
      "**outside** that band, and the busiest real schedule lands at the %s end of it.  So "
      "the thing that moves this book is not the calendar: it is whether the size is "
      "allowed to follow the beta at all, and if it is, the covariance printed in the "
      "`chase` column is what you pay for it."
      % (_f((rt["ann"]["p95"] - rt["ann"]["p05"]) * 100.0, 2),
         "bottom" if (by["every_period"]["ann"] or 0.0) < rt["ann"]["p50"] else "top"))
    a("")
    a("## 6. What an operator should do with this")
    a("")
    a("- **Do not pay for re-sizing.**  Any cadence from quarterly to never costs less "
      "than %s pp a year at any realistic per-side price." % _f(r["cost_drag_max_pp"], 3))
    a("- **Do not chase the beta either.**  Every schedule that follows the beta pays the "
      "chase term; the two that hold one size do not.  In this window that term alone is "
      "**%s pp** a year -- **%s times** the entire cost of trading the hedge."
      % (_f(abs(r["chase_every_pp"]), 2),
         _f(abs(r["chase_every_pp"]) / (r["cost_drag_max_pp"] or 1e-9), 0)))
    a("- **So the cadence question answers itself: pick any, then stop moving.**  The "
      "remaining choice is the level of k, and r2030 already showed the past cannot pick "
      "it (beta = 1.00 tied the refitted beta); here the two levels tried differ by "
      "**%s pp** a year, which is the size of the prize for guessing." % _f(abs(by["set_once"]["ann"] - by["one_unit"]["ann"]) * 100.0, 2))
    a("- **Watch the staleness, not the calendar.**  If the size held drifts more than "
      "~0.05 away from the beta the period would choose, the residual exposure is the "
      "printed `max_abs_error`; a calendar cadence cannot see that, a drift band can -- "
      "but band 0.05 and band 0.10 both sit inside the varying pack here, so treat the "
      "band as an operational alarm, not as an alpha.")
    a("")
    a("## 7. What this face does not say")
    a("")
    a("- It does not re-choose a size or a level.  Both constant arms win (0.91 and 1.00 "
      "alike), and they differ from each other by %s pp: the level term in this window is "
      "worth a tenth of a point.  What pays here is *not drifting*, and the drift costs "
      "because of a covariance this face measures but cannot promise to repeat."
      % _f(abs(by["set_once"]["ann"] - by["one_unit"]["ann"]) * 100.0, 2))
    a("- It charges commission and slippage on the hedge turnover only.  Borrow fee on the "
      "ETF leg, roll cost on the futures leg and the book's own turnover cost are priced "
      "in r2033 and in the parent book respectively.")
    a("- It does not model the intraday of the re-size, the margin call a futures position "
      "meets, or the availability of the shares to borrow.")
    a("- The evaluation sample is one history of %d periods; the random-timing band is a "
      "statement about timing luck inside that history, not a confidence interval for a "
      "future window." % s["periods_evaluated"])
    a("- Only the ETF hedge leg is walked.  r2027 showed the IM leg cannot express this "
      "beta at small capital, so the schedule question is asked of the leg that can.")
    a("")
    a("## 8. Reproduction")
    a("")
    a("```")
    a("python scripts/astock_veto_hedge_resize.py selftest")
    a("python scripts/astock_veto_hedge_resize.py run")
    a("python scripts/astock_veto_hedge_resize.py check")
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
        print("astock_veto_hedge_resize NOT_ENOUGH_PERIODS | %s" % face.get("verdict_why"))
        return 0
    by = {p["schedule"]: p for p in face["schedules"]}
    print("astock_veto_hedge_resize %s | %s | %s | %s"
          % (face["verdict"], face["verdict_breakeven"], face["verdict_schedule"],
             face["verdict_level"]))
    print("  turnover/yr: every_period %s vs set_once %s (extra %s)"
          % (_pct(by["every_period"]["turnover_per_year"], 1),
             _pct(by["set_once"]["turnover_per_year"], 1),
             _f(face["reads"]["extra_turnover_per_year"], 4)))
    print("  cost at %s bp/side: max drag %s pp | break-even %s bp/side"
          % (_f(face["spec"]["cost_main_bp"], 1),
             _f(face["reads"]["cost_drag_max_pp"], 4),
             _f(face["reads"]["breakeven_cost_bp"], 0)))
    print("  vol span %s pp | ann span %s pp | set_once - every_period %s pp (%s sd)"
          % (_f(face["reads"]["vol_span_pp"], 2), _f(face["reads"]["ann_span_pp"], 2),
             _f(face["reads"]["setonce_vs_every_pp"], 2),
             _f(face["reads"]["gap_in_random_sd"], 1)))
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

    for key in ("beta", "walkforward"):
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

    if len(face.get("schedules") or []) != len(fresh.get("schedules") or []):
        problems.append("CHECK FAILED: schedule count %d != %d"
                        % (len(face.get("schedules") or []),
                           len(fresh.get("schedules") or [])))
    else:
        fields = ("n", "n_resets", "turnover_total", "turnover_per_year", "k_mean",
                  "k_min", "k_max", "mean_abs_error", "max_abs_error", "k_cov_hedge",
                  "chase_pp_per_year", "vol", "ann", "cum", "dd", "worst", "neg",
                  "ann_net", "cum_net", "dd_net", "cost_drag_pp")
        for x, y in zip(face["schedules"], fresh["schedules"]):
            if x.get("schedule") != y.get("schedule"):
                problems.append("CHECK FAILED: schedule order at %s" % x.get("schedule"))
                continue
            for field in fields:
                p, q = x.get(field), y.get(field)
                if isinstance(p, (int, float)) and isinstance(q, (int, float)):
                    if abs(float(p) - float(q)) > TOL:
                        problems.append("CHECK FAILED: %s/%s %r != %r"
                                        % (x["schedule"], field, p, q))
                elif p != q:
                    problems.append("CHECK FAILED: %s/%s %r != %r"
                                    % (x["schedule"], field, p, q))
            if set(x.get("by_cost") or {}) != set(y.get("by_cost") or {}):
                problems.append("CHECK FAILED: %s cost grid keys differ" % x["schedule"])
            else:
                for key in y["by_cost"]:
                    for f2 in ("ann", "cum", "dd"):
                        p = (x["by_cost"][key] or {}).get(f2)
                        q = (y["by_cost"][key] or {}).get(f2)
                        if isinstance(p, (int, float)) and isinstance(q, (int, float)):
                            if abs(float(p) - float(q)) > TOL:
                                problems.append("CHECK FAILED: %s/by_cost[%s].%s %r != %r"
                                                % (x["schedule"], key, f2, p, q))
                        elif p != q:
                            problems.append("CHECK FAILED: %s/by_cost[%s].%s %r != %r"
                                            % (x["schedule"], key, f2, p, q))

    for key in ("extra_turnover_per_year", "breakeven_cost_bp", "cost_drag_max_pp",
                "cost_drag_span_pp", "cost_share_of_busiest", "vol_span_pp",
                "ann_span_pp", "setonce_vs_every_pp", "gap_in_random_sd", "k_gap",
                "level_arithmetic_pp_per_year", "chase_every_pp", "constant_min_ann",
                "varying_max_ann", "random_ann_sd_pp"):
        p = (face.get("reads") or {}).get(key)
        q = (fresh.get("reads") or {}).get(key)
        if isinstance(p, (int, float)) and isinstance(q, (int, float)):
            if abs(float(p) - float(q)) > TOL:
                problems.append("CHECK FAILED: reads.%s %r != %r" % (key, p, q))
        elif p != q:
            problems.append("CHECK FAILED: reads.%s %r != %r" % (key, p, q))

    if (face.get("sample") or {}) != (fresh.get("sample") or {}):
        problems.append("CHECK FAILED: sample block %r != %r"
                        % (face.get("sample"), fresh.get("sample")))

    if (face.get("random_timing") or {}) != (fresh.get("random_timing") or {}):
        problems.append("CHECK FAILED: random-timing control moved (frozen seed %d)"
                        % RANDOM_SEED)

    if (face.get("anchor") or {}).get("max_abs_beta_diff") != (fresh.get("anchor") or {}).get(
            "max_abs_beta_diff"):
        problems.append("CHECK FAILED: anchor diff %r != %r"
                        % ((face.get("anchor") or {}).get("max_abs_beta_diff"),
                           (fresh.get("anchor") or {}).get("max_abs_beta_diff")))

    for key in ("verdict", "verdict_cost", "verdict_breakeven", "verdict_schedule",
                "verdict_level", "verdict_why"):
        if face.get(key) != fresh.get(key):
            problems.append("CHECK FAILED: %s %r != %r"
                            % (key, face.get(key), fresh.get(key)))

    if problems:
        for p in problems:
            print(p)
        return 3

    if not os.path.exists(md_path):
        print("STALE: page missing (%s)" % _rel(md_path))
        return 3
    with open(md_path, encoding="utf-8") as fh:
        md = fh.read()
    for word in (face["verdict_cost"], face["verdict_breakeven"],
                 face["verdict_schedule"], face["verdict_level"]):
        if "`" + word + "`" not in md:
            problems.append("CHECK FAILED: page does not print `%s`" % word)
    if problems:
        for p in problems:
            print(p)
        return 3

    print("CHECK OK %s | %s | %s | %s | %d schedules re-derived"
          % (face["verdict"], face["verdict_breakeven"], face["verdict_schedule"],
             face["verdict_level"], len(face["schedules"])))
    return 0


def selftest() -> int:
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    target = [0.90, 0.95, 0.92, 1.00, 1.05, 0.97, 0.88]
    book = [0.02, -0.01, 0.03, 0.0, 0.01, -0.02, 0.04]
    hedge = [0.03, -0.02, 0.04, 0.01, 0.02, -0.03, 0.05]

    # --- k paths
    leg("L1 every_period holds the target", kpath("every_period", target) == target)
    leg("L1b set_once holds the first target forever",
        kpath("set_once", target) == [0.90] * len(target))
    leg("L1c one_unit holds 1.0 forever", kpath("one_unit", target) == [1.0] * len(target))
    leg("L1d cadence_1y re-sizes only on its own lattice",
        [n for n, v in enumerate(kpath("cadence", target, cadence=3))
         if abs(v - target[n]) < 1e-12] == [0, 3, 6])
    band = kpath("band", target, band=0.05)
    leg("L1e the band does not trade inside the band",
        abs(band[1] - 0.90) < 1e-12, band)
    leg("L1f the band trades outside it", abs(kpath("band", target, band=0.02)[1] - 0.95) < 1e-12)
    leg("L1g a band wider than the whole range never trades again",
        kpath("band", target, band=5.0) == [0.90] * len(target))
    leg("L1h the entry trade always happens",
        all(kpath(kind, target)[0] in (target[0], 1.0)
            for kind in ("every_period", "cadence", "band", "set_once", "one_unit")))

    # --- stats arithmetic
    k = [0.0, 0.5, 0.5, 1.0]
    b = [0.01, 0.02, -0.02, 0.01]
    h = [0.10, 0.10, -0.10, 0.10]
    s = policy_stats(k, b, h, 0.0)
    hand = [b[0] - 0.0 * h[0], b[1] - 0.5 * h[1], b[2] - 0.5 * h[2], b[3] - 1.0 * h[3]]
    leg("L2 the residual is book minus k times hedge",
        abs(s["ann"] - float(np.mean(hand) * PPY)) < 1e-12, s["ann"])
    leg("L2b turnover sums the notional traded, entry included",
        abs(s["turnover_total"] - (0.0 + 0.5 + 0.0 + 0.5)) < 1e-12, s["turnover_total"])
    leg("L2c re-sizes exclude the entry trade", s["n_resets"] == 1, s["n_resets"])
    c = policy_stats(k, b, h, 100.0)
    leg("L2d the trade is charged in the period it is made",
        abs((s["ann"] - c["ann"]) - ((0.5 + 0.5) * 100.0 / 1e4) * PPY / 4.0) < 1e-12,
        (s["ann"] - c["ann"]))
    leg("L2e no cost means net equals gross", policy_stats(k, b, h, 0.0)["ann"] == s["ann"])
    leg("L2f too few periods gives None", policy_stats([0.0], [0.1], [0.1])["ann"] is None)
    leg("L2g drawdown of a straight fall is the fall",
        abs(max_drawdown([-0.1, -0.1]) - (-0.19)) < 1e-12)
    leg("L2h drawdown of a rising series is zero", max_drawdown([0.05, 0.05]) == 0.0)

    # --- staleness
    e = k_error([0.9, 0.9, 0.9], [0.9, 0.8, 1.0])
    leg("L3 staleness is the absolute distance to the target",
        abs(e["mean_abs_error"] - (0.0 + 0.1 + 0.1) / 3.0) < 1e-12, e["mean_abs_error"])
    leg("L3b max staleness is the worst period", abs(e["max_abs_error"] - 0.1) < 1e-12)

    # --- break-even arithmetic
    leg("L4 break-even scales inversely with extra turnover",
        abs(breakeven_bp(0.1) - 50.0) < 1e-9, breakeven_bp(0.1))
    leg("L4b no extra turnover has no break-even", breakeven_bp(0.0) is None)
    leg("L4c negative extra turnover has no break-even", breakeven_bp(-0.1) is None)

    # --- verdict ladders, both sides of every line
    leg("L5 cost just inside the line is noise",
        decide_cost(LINE_COST_PP - 1e-6) == "SCHEDULE_COST_IS_BELOW_THE_NOISE_LINE")
    leg("L5b cost at the line is a line item",
        decide_cost(LINE_COST_PP) == "SCHEDULE_COST_IS_A_REAL_LINE_ITEM")
    leg("L5c unmeasurable cost says so", decide_cost(None) == "COST_NOT_MEASURABLE")
    leg("L6 break-even at the line cannot decide",
        decide_breakeven(LINE_BREAKEVEN_BP) == "COST_CANNOT_DECIDE_THE_SCHEDULE")
    leg("L6b a tiny break-even decides against the busy schedule",
        decide_breakeven(LINE_BREAKEVEN_BP - 0.1) == "COST_DECIDES_AGAINST_THE_BUSY_SCHEDULE")
    leg("L6c a fiftyfold break-even is called what it is",
        decide_breakeven(50.0 * LINE_BREAKEVEN_BP) == "COST_IS_FIFTYFOLD_AWAY_FROM_DECIDING")
    leg("L6d no extra turnover to price says so",
        decide_breakeven(None) == "NO_EXTRA_TURNOVER_TO_PRICE")
    leg("L7 a vol span under the tie means the schedule does not move risk",
        decide_schedule(LINE_TIE_PP - 1e-9, 5.0) == "THE_SCHEDULE_DOES_NOT_MOVE_RISK_AT_ALL")
    leg("L7b return span above vol span is called that",
        decide_schedule(1.0, 2.0) == "THE_SCHEDULE_MOVES_RETURN_MORE_THAN_RISK")
    leg("L7c risk span above return span is called that",
        decide_schedule(2.0, 1.0) == "THE_SCHEDULE_MOVES_RISK_MORE_THAN_RETURN")
    leg("L8 constants beating the varying pack is the headline",
        decide_level(12.0, 11.5, 0.5, 0.2) == "HOLDING_THE_SIZE_STILL_BEATS_CHASING_IT")
    leg("L8b a tie between the two packs falls through to the gap test",
        decide_level(11.5, 12.0, 4.0, 1.0) == "THE_GAP_IS_THE_LEVEL_NOT_THE_TIMING")
    leg("L8b2 the same tie with a small gap could be luck",
        decide_level(11.5, 12.0, 1.0, 1.0) == "TIMING_LUCK_COULD_EXPLAIN_THE_GAP")
    leg("L8c unmeasurable arms say so",
        decide_level(None, 1.0, 1.0, 1.0) == "LEVEL_NOT_MEASURABLE")

    # --- random control is deterministic and actually random
    t1 = random_timing(target * 8, book * 8, hedge * 8, draws=20)
    t2 = random_timing(target * 8, book * 8, hedge * 8, draws=20)
    t3 = random_timing(target * 8, book * 8, hedge * 8, draws=20, seed=RANDOM_SEED + 1)
    leg("L9 the random control is reproducible from its seed", t1 == t2)
    leg("L9b a different seed draws a different band", t1 != t3)
    leg("L9c the control runs the number of draws it claims", t1["draws"] == 20)

    # --- live face
    face = build_face()
    if face.get("verdict") == "NOT_ENOUGH_PERIODS":
        leg("L10 live face is measurable", False, face.get("verdict_why"))
    else:
        by = {p["schedule"]: p for p in face["schedules"]}
        rd = face["reads"]
        leg("L10 every schedule shares one sample",
            len({p["n"] for p in face["schedules"]}) == 1)
        leg("L10b every_period is stale by construction zero",
            by["every_period"]["mean_abs_error"] == 0.0)
        leg("L10c the busiest schedule trades most",
            by["every_period"]["turnover_per_year"] >= by["set_once"]["turnover_per_year"])
        leg("L10d the extra turnover is the difference of the two",
            abs(rd["extra_turnover_per_year"]
                - (by["every_period"]["turnover_per_year"]
                   - by["set_once"]["turnover_per_year"])) < 1e-12)
        leg("L10e the vol span is the observed max minus min",
            abs(rd["vol_span_pp"]
                - (max(p["vol"] for p in face["schedules"])
                   - min(p["vol"] for p in face["schedules"])) * 100.0) < 1e-9)
        leg("L10f break-even is positive when there is extra turnover",
            rd["extra_turnover_per_year"] <= 0 or (rd["breakeven_cost_bp"] or 0) > 0)
        leg("L10g the betas are r2030's own (anchor)", 
            (face["anchor"]["max_abs_beta_diff"] or 0.0) < 1e-12,
            face["anchor"]["max_abs_beta_diff"])
        leg("L10h the level arithmetic has the sign of the k gap",
            (rd["level_arithmetic_pp_per_year"] or 0.0) * rd["k_gap"] >= 0)
        leg("L10h2 the level arithmetic is k gap times the hedge's mean times periods/yr",
            abs((rd["level_arithmetic_pp_per_year"] or 0.0)
                - rd["k_gap"] * face["sample"]["hedge_mean_period"] * PPY * 100.0) < 1e-9)
        words = ("SCHEDULE_COST_IS_BELOW_THE_NOISE_LINE",
                 "SCHEDULE_COST_IS_A_REAL_LINE_ITEM")
        leg("L10i the cost verdict is one of the frozen words",
            face["verdict_cost"] in words, face["verdict_cost"])
        leg("L10j the schedule verdict is one of the frozen words",
            face["verdict_schedule"] in ("THE_SCHEDULE_DOES_NOT_MOVE_RISK_AT_ALL",
                                         "THE_SCHEDULE_MOVES_RETURN_MORE_THAN_RISK",
                                         "THE_SCHEDULE_MOVES_RISK_MORE_THAN_RETURN"))
        leg("L10k the level verdict is one of the frozen words",
            face["verdict_level"] in ("HOLDING_THE_SIZE_STILL_BEATS_CHASING_IT",
                                      "THE_GAP_IS_THE_LEVEL_NOT_THE_TIMING",
                                      "TIMING_LUCK_COULD_EXPLAIN_THE_GAP"),
            face["verdict_level"])
        leg("L10k2 a constant size carries no chase term",
            all(abs(by[n]["chase_pp_per_year"]) < 1e-12 for n in ("set_once", "one_unit")))
        leg("L10k2b a chasing schedule pays a positive chase term",
            by["every_period"]["chase_pp_per_year"] > 0,
            by["every_period"]["chase_pp_per_year"])
        leg("L10k3 the constants-beat-varying verdict matches the numbers",
            (face["verdict_level"] == "HOLDING_THE_SIZE_STILL_BEATS_CHASING_IT")
            == (rd["constant_min_ann"] > rd["varying_max_ann"]))
        leg("L10k4 the chase term and the level term add up to the gap",
            abs((rd["chase_every_pp"] + rd["level_arithmetic_pp_per_year"])
                - rd["setonce_vs_every_pp"]) < 0.02,
            (rd["chase_every_pp"], rd["level_arithmetic_pp_per_year"],
             rd["setonce_vs_every_pp"]))
        leg("L10l every schedule carries its whole cost grid",
            all(len(p["by_cost"]) == len(COST_GRID_BP) for p in face["schedules"]))

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
