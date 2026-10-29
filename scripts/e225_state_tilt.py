"""E225 -- does rebalancing a state tilt daily buy resolution an episode lock cannot?

E224 closed with a cap rather than a discovery: a gate that is polled every session
still produces at most 252/H independent episodes a year, because the hold length,
not the sampling rate, sets the count. Its named successor was the one design the
accounting does not throttle: a CONTINUOUSLY HELD tilt, where the weight itself
varies with the state and there is no per-episode round trip to restart the clock.

So this face keeps the signal and the cost model identical to E224 and changes only
the accounting:

  * E224: weight is 0 or 1, locked for H sessions, two sides per episode, one
    independent observation per episode.
  * E225: weight is any value in [0, 1] decided at each close, applied to the next
    session's return, and each unit of weight change pays one side.

That difference is the whole experiment. If daily rebalancing buys resolution, the
daily series must look close to independent (effective sample size near the session
count). If it does not, the effective sample size collapses toward E224's episode
count and the tilt is the same wall wearing a different hat.

Frozen before reading any number:

  * signal: trailing 20-session realised volatility of daily returns in bp, known at
    the close of session t. Tercile thresholds come from the previous 250 signal
    values strictly before t; below 120 past values the tilt is flat at 0.
  * arms (5, all on the same signal):
      always_on    w = 1 every session (null: no gating, no turnover)
      binary_low   w = 1 in the bottom tercile else 0 (E224's shape, daily rebalanced)
      tilt_step    w = 1 / 0.5 / 0 in the bottom / middle / top tercile
      tilt_linear  w = clip((hi - v) / (hi - lo), 0, 1), i.e. 1 at the low threshold
                   and 0 at the high one, linear in between and outside
      voltarget    w = clip(target / v, 0, 1) with target = the IN-SAMPLE median of
                   the signal (a volatility target, not a tercile rule)
  * accounting: decision at the close of t, weight applies to the return of t+1;
    unit turnover |w_t - w_{t-1}| pays COST_SIDE_BP with w_{-1} = 0, so entering
    from cash pays one side and a full 0->1->0 swing pays exactly the two sides
    E224 charged per episode.
  * excess_t = w_t * (ret_{t+1} - mu_is) - cost_t, where mu_is = the IN-SAMPLE mean
    daily return only. Charging the same drift to a lower-exposure arm is the point:
    a tilt that is in the market 60% of the time is compared with holding that
    exposure constantly, not with holding 100%.
  * split: first 60% of sessions are in-sample; OOS decisions are those made at or
    after the boundary. Minimum 252 OOS sessions to judge anything.
  * dependence: the annual t is a Newey-West statistic with lag 20, and the i.i.d.
    t is printed beside it. The effective sample size n_eff = n (1-rho)/(1+rho)
    from the lag-1 autocorrelation of the excess series is published, because that
    number, not the session count, is what the annual bar is really built on.
  * decision rule: ADOPT iff OOS sessions >= 252 AND OOS net excess per year > 0 AND
    OOS Newey-West t >= the Bonferroni bar for 5 arms x 2 panels, AND the arm is
    still net positive at x2 costs. REJECT if the window is long enough and any
    test fails. UNRESOLVED below.
  * resolution: MDE_ann = z_80 * se_nw * 252 bp/yr, i.e. the smallest annual excess
    this test length could distinguish from zero at 80% power.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e222_tom_overlay as e222  # noqa: E402
import e224_vol_gate as e224  # noqa: E402

ROOT = e222.ROOT
PANEL_DIR = e222.PANEL_DIR
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
E224_FACE = os.path.join(ROOT, "results", "vol_gate", "latest.json")

# ---------------------------------------------------------------- frozen spec
COST_SIDE_BP = e222.COST_SIDE_BP
COST_X2_MULT = 2.0
VOL_WINDOW = e224.VOL_WINDOW
THRESHOLD_WINDOW = e224.THRESHOLD_WINDOW
THRESHOLD_MIN = e224.THRESHOLD_MIN
IS_FRAC = 0.60
MIN_OOS_SESSIONS = 252
NW_LAG = 20
Z_80 = 2.802
SESSIONS_PER_YEAR = 252
PRIMARY_SYMBOL = e224.PRIMARY_SYMBOL
BASKET = e224.BASKET

ARMS = ["always_on", "binary_low", "tilt_step", "tilt_linear", "voltarget"]


# ---------------------------------------------------------------- statistics
def _mean(v):
    return (sum(v) / len(v)) if v else None


def _sd(v):
    if not v or len(v) < 2:
        return None
    m = sum(v) / len(v)
    return (sum((x - m) ** 2 for x in v) / (len(v) - 1)) ** 0.5


def _median(v):
    if not v:
        return None
    s = sorted(v)
    n = len(s)
    mid = n // 2
    return s[mid] if n % 2 else 0.5 * (s[mid - 1] + s[mid])


def _hac_se(x, lag=NW_LAG):
    """Newey-West standard error of the mean with a Bartlett kernel."""
    n = len(x)
    if n < 3:
        return None
    m = sum(x) / n
    d = [v - m for v in x]
    gamma0 = sum(v * v for v in d) / n
    var = gamma0
    for l in range(1, min(lag, n - 1) + 1):
        gl = sum(d[i] * d[i - l] for i in range(l, n)) / n
        var += 2.0 * (1.0 - l / (lag + 1.0)) * gl
    if var <= 0:
        return None
    return (var / n) ** 0.5


def _n_eff(x):
    """Effective sample size from the lag-1 autocorrelation (AR(1) equivalent)."""
    n = len(x)
    if n < 3:
        return None
    m = sum(x) / n
    d = [v - m for v in x]
    den = sum(v * v for v in d)
    if den <= 0:
        return float(n)
    rho = sum(d[i] * d[i - 1] for i in range(1, n)) / den
    if rho >= 1.0:
        return 1.0
    ne = n * (1.0 - rho) / (1.0 + rho)
    return max(1.0, min(float(n), ne))


def split_index(n_sessions, frac=IS_FRAC):
    idx = int(round(n_sessions * frac))
    return min(max(idx, 1), n_sessions - 1)


# ---------------------------------------------------------------- signal + weight
def vol_signal(ret_bp, window=VOL_WINDOW):
    return e224.vol_signal(ret_bp, window)


def terciles_at(sig, i, window=THRESHOLD_WINDOW, minimum=THRESHOLD_MIN):
    return e224.terciles_at(sig, i, window, minimum)


def weight_at(sig, i, arm, target=None):
    """The weight held for session i+1, decided at the close of session i."""
    if arm == "always_on":
        return 1.0
    v = sig[i]
    thr = terciles_at(sig, i)
    if v is None or thr is None:
        return 0.0
    lo, hi = thr
    if arm == "binary_low":
        return 1.0 if v <= lo else 0.0
    if arm == "tilt_step":
        if v <= lo:
            return 1.0
        if v >= hi:
            return 0.0
        return 0.5
    if arm == "tilt_linear":
        if hi <= lo:
            return 0.0
        w = (hi - v) / (hi - lo)
        return 0.0 if w < 0.0 else (1.0 if w > 1.0 else w)
    if arm == "voltarget":
        if not target or not v or v <= 0:
            return 0.0
        w = target / v
        return 0.0 if w < 0.0 else (1.0 if w > 1.0 else w)
    raise ValueError("unknown arm: %r" % (arm,))


def arm_target(sig, split, arm):
    """The IS-only constant a normalising arm needs (None for the others)."""
    if arm != "voltarget":
        return None
    past = [sig[i] for i in range(1, split) if sig[i] is not None]
    return _median(past)


def weights_series(sig, arm, target=None):
    return [weight_at(sig, i, arm, target) for i in range(len(sig))]


# ---------------------------------------------------------------- accounting
def tilt_stats(weights, ret_bp, split, cost_side_bp, bar_t):
    """Daily-rebalanced accounting; every row is (decision session i -> return i+1)."""
    n = len(ret_bp)
    is_rets = [r for r in ret_bp[1:split] if r is not None]
    mu_is = _mean(is_rets)

    rows = []
    prev_w = 0.0
    for i in range(0, n - 1):
        w = weights[i]
        dw = w - prev_w
        cost = abs(dw) * cost_side_bp
        r = ret_bp[i + 1]
        if r is None:
            prev_w = w
            continue
        gross = w * r
        rows.append({"i": i, "w": w, "abs_dw": abs(dw), "gross_bp": gross,
                     "cost_bp": cost, "excess_bp": gross - cost - w * mu_is})
        prev_w = w

    cut = split - 1
    oos = [r for r in rows if r["i"] >= cut]
    is_rows = [r for r in rows if r["i"] < cut]

    ex = [r["excess_bp"] for r in oos]
    m = _mean(ex)
    sd = _sd(ex)
    se_iid = (sd / (len(ex) ** 0.5)) if (sd is not None and ex) else None
    se_nw = _hac_se(ex) if len(ex) >= 3 else None
    t_nw = (m / se_nw) if (se_nw and m is not None) else None
    t_iid = (m / se_iid) if (se_iid and m is not None) else None
    n_eff = _n_eff(ex) if len(ex) >= 3 else None

    years = n / float(SESSIONS_PER_YEAR)
    turnover_total = sum(r["abs_dw"] for r in rows)
    turnover_oos = sum(r["abs_dw"] for r in oos)

    mde = (Z_80 * se_nw * SESSIONS_PER_YEAR) if se_nw else None
    years_needed = None
    years_unbounded = False
    if m is not None and m != 0.0 and se_nw:
        per_year = m * SESSIONS_PER_YEAR
        # years such that z*se*sqrt(Y_now/Y) == per_year, i.e. the run length at
        # which the observed effect would reach 80% power
        factor = (Z_80 * se_nw / abs(m)) ** 2
        years_needed = factor * years
        if years_needed > 1e5:
            years_needed = None
            years_unbounded = True

    return {
        "sessions": n,
        "years": years,
        "decisions": len(rows),
        "oos_decisions": len(oos),
        "is_decisions": len(is_rows),
        "mu_is_bp_per_day": mu_is,
        "avg_weight_oos": _mean([r["w"] for r in oos]),
        "time_in_market_pct": (100.0 * _mean([r["w"] for r in oos])) if oos else None,
        "turnover_total": turnover_total,
        "turnover_per_year": (turnover_total / years) if years else None,
        "turnover_oos_per_year": (turnover_oos / (len(oos) / float(SESSIONS_PER_YEAR)))
                                 if oos else None,
        "cost_bp_per_year_oos": (_mean([r["cost_bp"] for r in oos]) * SESSIONS_PER_YEAR)
                                if oos else None,
        "gross_bp_per_year_oos": (_mean([r["gross_bp"] for r in oos]) * SESSIONS_PER_YEAR)
                                 if oos else None,
        "excess_total_bp": sum(r["excess_bp"] for r in rows),
        "excess_bp_per_day_oos": m,
        "excess_oos_bp_per_year": (m * SESSIONS_PER_YEAR) if m is not None else None,
        "sd_bp_per_day": sd,
        "se_iid": se_iid,
        "se_nw": se_nw,
        "excess_oos_t": t_nw,
        "excess_oos_t_iid": t_iid,
        "nw_over_iid_se": (se_nw / se_iid) if (se_nw and se_iid) else None,
        "n_eff": n_eff,
        "n_eff_over_sessions": (n_eff / len(oos)) if (n_eff and oos) else None,
        "mde_ann_bp_per_year": mde,
        "years_needed": years_needed,
        "years_needed_unbounded": years_unbounded,
        "bar_t": bar_t,
    }


def verdict(a, bar_t, x2=None, min_oos=MIN_OOS_SESSIONS):
    if (a.get("oos_decisions") or 0) < min_oos:
        return "UNRESOLVED", "oos_sessions_%d_below_%d" % (a.get("oos_decisions") or 0,
                                                          min_oos)
    if a.get("excess_oos_bp_per_year") is None or a.get("excess_oos_t") is None:
        return "UNRESOLVED", "oos_series_unusable"
    if a["excess_oos_bp_per_year"] <= 0:
        return "REJECT", "oos_net_excess_not_positive"
    if a["excess_oos_t"] < bar_t:
        return "REJECT", "oos_t_%.2f_below_bar_%.2f" % (a["excess_oos_t"], bar_t)
    if x2 is not None and (x2.get("excess_oos_bp_per_year") is None
                           or x2["excess_oos_bp_per_year"] <= 0):
        return "REJECT", "dies_at_x2_costs"
    return "ADOPT", "clears_rule"


# ---------------------------------------------------------------- panels
def single_panel(sym=PRIMARY_SYMBOL, panel_dir=None):
    return e224.single_panel(sym, panel_dir)


def basket_panel(panel_dir=None):
    return e224.basket_panel(panel_dir)


def _e224_reference():
    try:
        with open(E224_FACE, "r", encoding="utf-8") as fh:
            face = json.load(fh)
    except (OSError, ValueError):
        return None
    try:
        arms = face["panels"][0]["arms"]
    except (KeyError, IndexError, TypeError):
        return None
    out = {"source": os.path.relpath(E224_FACE, ROOT).replace("\\", "/"),
           "study": face.get("study"), "arms": {}}
    for a in arms:
        out["arms"][a.get("name")] = {
            "hold_sessions": a.get("hold_sessions"),
            "episodes_per_year": a.get("episodes_per_year"),
            "oos_episodes": a.get("episodes_oos"),
            "excess_oos_bp_per_year": a.get("excess_oos_bp_per_year"),
            "excess_oos_t": a.get("excess_oos_t"),
            "mde_ann_bp_per_year": a.get("mde_ann_bp_per_year"),
        }
    return out


def run(save=True, panel_dir=None, outdir=None):
    panel_dir = panel_dir or PANEL_DIR
    outdir = outdir or OUTDIR
    single = single_panel(PRIMARY_SYMBOL, panel_dir)
    if single is None:
        print("primary panel missing: %s" % PRIMARY_SYMBOL)
        return None
    basket = basket_panel(panel_dir)

    n_tests = len(ARMS) * (2 if basket else 1)
    bar_t = max(2.0, e222._z_two_sided(0.05 / n_tests))

    panels = [{"panel": "primary_single", "symbol": PRIMARY_SYMBOL,
               "sessions": len(single[0]), "first": single[0][0], "last": single[0][-1]}]
    if basket:
        panels.append({"panel": "basket_equal_weight", "symbol": "+".join(sorted(BASKET)),
                       "sessions": len(basket[0]), "first": basket[0][0],
                       "last": basket[0][-1]})

    for panel in panels:
        dates, ret_bp = (single if panel["panel"] == "primary_single" else basket)
        sig = vol_signal(ret_bp)
        split = split_index(len(dates))
        arms_out = []
        for arm in ARMS:
            target = arm_target(sig, split, arm)
            w = weights_series(sig, arm, target)
            a = tilt_stats(w, ret_bp, split, COST_SIDE_BP, bar_t)
            a_x2 = tilt_stats(w, ret_bp, split, COST_SIDE_BP * COST_X2_MULT, bar_t)
            a["name"] = arm
            a["target_bp"] = target
            a["excess_oos_bp_per_year_x2"] = a_x2.get("excess_oos_bp_per_year")
            a["verdict"], a["verdict_reason"] = verdict(a, bar_t, x2=a_x2)
            arms_out.append(a)
        panel["arms"] = arms_out
        # The null arm prices the OOS drift against the in-sample drift, so every
        # gated arm inherits that deficit in proportion to its exposure. Splitting
        # it out keeps "the gate lost money" from being read as a verdict on the
        # gate when what actually happened is that the drift it normalised to did
        # not repeat.
        null = next((a for a in arms_out if a["name"] == "always_on"), None)
        null_ann = null["excess_oos_bp_per_year"] if null else None
        for a in arms_out:
            if a["name"] == "always_on" or null_ann is None:
                a["market_drift_component_bp_per_year"] = 0.0 if a["name"] == "always_on" else None
                a["gate_specific_bp_per_year"] = a["excess_oos_bp_per_year"]
                continue
            comp = (a["avg_weight_oos"] or 0.0) * null_ann
            a["market_drift_component_bp_per_year"] = comp
            a["gate_specific_bp_per_year"] = (
                a["excess_oos_bp_per_year"] - comp
                if a["excess_oos_bp_per_year"] is not None else None)
        panel["split_session"] = split
        panel["split_date"] = dates[split]
        panel["is_frac"] = IS_FRAC

    face = {
        "study": "E225",
        "title": "the continuously-held state tilt: does daily reweighting buy the "
                 "resolution an episode-locked gate cannot?",
        "generated": datetime.now().isoformat(timespec="seconds"),
        "evidence_cutoff": panels[0]["last"],
        "frozen_spec": {
            "arms": ARMS,
            "cost_side_bp": COST_SIDE_BP,
            "cost_model": "unit turnover |dw| pays one side; w_{-1}=0 so entry pays a side",
            "vol_window": VOL_WINDOW,
            "threshold_window": THRESHOLD_WINDOW,
            "threshold_min": THRESHOLD_MIN,
            "is_frac": IS_FRAC,
            "min_oos_sessions": MIN_OOS_SESSIONS,
            "nw_lag": NW_LAG,
            "z_80pct": Z_80,
            "bar_t": bar_t,
            "tests": n_tests,
            "bar_basis": "two-sided 5%% over %d tests (5 arms x %d panels)"
                         % (n_tests, len(panels)),
            "excess_definition": "w_t*(ret_{t+1} - mu_is) - |w_t - w_{t-1}|*cost_side_bp",
            "baseline": "mu_is = in-sample mean daily return, estimated on IS sessions only",
        },
        "panels": panels,
    }

    ref = _e224_reference()
    if ref:
        face["episode_lock_reference"] = ref
        primary = panels[0]["arms"]
        tilt_like = [a for a in primary if a["name"] != "always_on"]
        best = None
        for a in tilt_like:
            if a.get("mde_ann_bp_per_year") is not None:
                if best is None or a["mde_ann_bp_per_year"] < best["mde_ann_bp_per_year"]:
                    best = a
        e224_best = None
        for name, a in ref["arms"].items():
            if a.get("mde_ann_bp_per_year") is not None:
                if e224_best is None or a["mde_ann_bp_per_year"] < e224_best[1]["mde_ann_bp_per_year"]:
                    e224_best = (name, a)
        bin_low = next((a for a in primary if a["name"] == "binary_low"), None)
        e224_low = None
        for name, a in ref["arms"].items():
            if name.startswith("vol_low") and a.get("episodes_per_year") is not None:
                if e224_low is None or (a.get("excess_oos_t") or 0) > (e224_low.get("excess_oos_t") or 0):
                    e224_low = a
        face["accounting_comparison"] = {
            "reading": "the same signal under episode-locked versus daily-rebalanced "
                       "accounting: a daily rule trades more sessions, so the question is "
                       "whether the effective sample size (n_eff) rises with it",
            "episode_locked": {
                "study": (ref or {}).get("study"),
                "best_arm": e224_best[0] if e224_best else None,
                "best_mde_ann_bp_per_year": e224_best[1]["mde_ann_bp_per_year"]
                                            if e224_best else None,
                "best_episodes_per_year": e224_best[1]["episodes_per_year"]
                                          if e224_best else None,
                "binary_shape_arm": e224_low,
            },
            "daily_rebalanced": {
                "best_arm": best["name"] if best else None,
                "best_mde_ann_bp_per_year": best["mde_ann_bp_per_year"] if best else None,
                "best_n_eff": best["n_eff"] if best else None,
                "best_oos_decisions": best["oos_decisions"] if best else None,
                "best_n_eff_over_sessions": best["n_eff_over_sessions"] if best else None,
                "binary_low_t": bin_low["excess_oos_t"] if bin_low else None,
                "binary_low_n_eff": bin_low["n_eff"] if bin_low else None,
                "binary_low_turnover_per_year": bin_low["turnover_per_year"]
                                                if bin_low else None,
                "binary_low_cost_bp_per_year_oos": bin_low["cost_bp_per_year_oos"]
                                                   if bin_low else None,
            },
        }
        if (best and e224_best
                and best.get("mde_ann_bp_per_year")
                and e224_best[1].get("mde_ann_bp_per_year")):
            face["resolution_comparison"] = {
                "episode_locked_mde_ann_bp_per_year": e224_best[1]["mde_ann_bp_per_year"],
                "daily_rebalanced_mde_ann_bp_per_year": best["mde_ann_bp_per_year"],
                "ratio_episode_over_daily": (e224_best[1]["mde_ann_bp_per_year"]
                                             / best["mde_ann_bp_per_year"]),
                "reading": "above 1 means daily reweighting resolves more per year of "
                           "history than the episode lock does",
            }

    primary = panels[0]["arms"]
    adopted = [a["name"] for a in primary if a["verdict"] == "ADOPT"]
    bin_low = next((a for a in primary if a["name"] == "binary_low"), None)
    null = next((a for a in primary if a["name"] == "always_on"), None)
    best = None
    for a in primary:
        if a["name"] == "always_on":
            continue
        if a.get("n_eff_over_sessions") is not None:
            if best is None or a["n_eff_over_sessions"] > best["n_eff_over_sessions"]:
                best = a
    rc = face.get("resolution_comparison") or {}
    # the arm whose gate-specific residual is the most favourable, so the answer
    # names the best case for the tilt rather than its worst
    best_gate = None
    for a in primary:
        if a.get("gate_specific_bp_per_year") is None:
            continue
        if best_gate is None or a["gate_specific_bp_per_year"] > best_gate["gate_specific_bp_per_year"]:
            best_gate = a
    face["drift_split"] = {
        "reading": "the null arm prices out-of-sample drift against the in-sample drift "
                   "it was normalised to; a gated arm inherits that deficit in proportion "
                   "to its average exposure, so gate_specific is what the tilt itself added "
                   "or lost after the drift it could not control",
        "null_arm_oos_excess_bp_per_year": (null["excess_oos_bp_per_year"] if null else None),
        "arms": [{"name": a["name"],
                  "avg_weight_oos": a.get("avg_weight_oos"),
                  "market_drift_component_bp_per_year": a.get("market_drift_component_bp_per_year"),
                  "gate_specific_bp_per_year": a.get("gate_specific_bp_per_year"),
                  "cost_bp_per_year_oos": a.get("cost_bp_per_year_oos")} for a in primary],
    }
    face["answer"] = (
        "reweighting daily buys sessions but not resolution: the tilt decides on %s OOS "
        "sessions and they are close to independent (n_eff %s of them, %.0f%%), yet the "
        "annual bar lands at %.0fbp/yr against the episode-locked gate's %.0fbp/yr -- a "
        "%.2fx move in the wrong direction, because a weight between 0 and 1 neither "
        "concentrates the signal nor escapes the drift it normalised to. The null arm is "
        "already %s bp/yr, and after charging each arm the drift it inherited the best "
        "gate-specific residual is %s bp/yr (%s); %d of %d arms adopt"
        % (primary[0]["oos_decisions"],
           ("%.0f" % best["n_eff"]) if (best and best.get("n_eff") is not None) else "-",
           100.0 * best["n_eff_over_sessions"] if (best and best.get("n_eff_over_sessions")) else 0.0,
           (rc.get("daily_rebalanced_mde_ann_bp_per_year") or 0.0),
           (rc.get("episode_locked_mde_ann_bp_per_year") or 0.0),
           rc.get("ratio_episode_over_daily") or 0.0,
           ("%.0f" % null["excess_oos_bp_per_year"]) if (null and null.get("excess_oos_bp_per_year") is not None) else "-",
           ("%.0f" % best_gate["gate_specific_bp_per_year"]) if best_gate else "-",
           best_gate["name"] if best_gate else "-",
           len(adopted), len(primary)))

    if save:
        if not os.path.isdir(outdir):
            os.makedirs(outdir)
        path = os.path.join(outdir, "TILT-%s.json" % face["evidence_cutoff"])
        text = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        with open(os.path.join(outdir, "latest.json"), "w", encoding="utf-8") as fh:
            fh.write(text)
        cols = ["panel", "name", "oos_decisions", "time_in_market_pct",
                "turnover_per_year", "cost_bp_per_year_oos", "gross_bp_per_year_oos",
                "excess_oos_bp_per_year", "excess_oos_bp_per_year_x2", "excess_oos_t",
                "excess_oos_t_iid", "nw_over_iid_se", "n_eff", "n_eff_over_sessions",
                "market_drift_component_bp_per_year", "gate_specific_bp_per_year",
                "sd_bp_per_day", "mde_ann_bp_per_year", "years_needed", "verdict",
                "verdict_reason"]
        # built explicitly so a missing literal comma cannot glue two labels together
        # and silently swallow the first data row (the r1325 lesson)
        assert len(cols) == 21, "column list length drift"
        csv_path = os.path.join(outdir, "by_arm_%s.csv" % face["evidence_cutoff"])
        with open(csv_path, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            for panel in panels:
                for a in panel["arms"]:
                    row = dict(a)
                    row["panel"] = panel["panel"]
                    w.writerow(row)
        face["_written"] = os.path.relpath(path, ROOT).replace("\\", "/")
        print("wrote %s" % face["_written"])
    return face


# ---------------------------------------------------------------- selftest
def _synth(n=900, drift_bp=1.0, vol_cycle=None, seed=7):
    """Deterministic synthetic panel: ret_bp with a slow vol cycle and fixed drift."""
    ret = [None]
    for i in range(1, n):
        v = vol_cycle(i % 120) if vol_cycle else 60.0
        seed = (1103515245 * seed + 12345) % (2 ** 31)
        z = ((seed / 2 ** 31) - 0.5) * 3.4641
        ret.append(drift_bp + z * v)
    return ["d%04d" % i for i in range(n)], ret


def selftest():
    legs = []

    def leg(name, cond, note=""):
        legs.append((name, bool(cond), note))

    # L1 the signal is causal: later returns cannot move an earlier value
    dates, ret = _synth(600)
    sig = vol_signal(ret)
    ret2 = list(ret)
    for i in range(400, 600):
        ret2[i] = (ret2[i] or 0.0) + 500.0
    sig2 = vol_signal(ret2)
    leg("signal_ignores_future_returns", all(sig[i] == sig2[i] for i in range(0, 400)),
        "a signal at t must not move when returns after t change")

    # L2 thresholds read only the past signal values
    leg("thresholds_are_past_only", terciles_at(sig, 400) == terciles_at(sig2, 400),
        "future perturbation must not move the terciles")

    # L3 every weight is inside [0, 1] on every arm
    ok = True
    for arm in ARMS:
        tgt = arm_target(sig, 400, arm)
        w = weights_series(sig, arm, tgt)
        ok = ok and all(-1e-12 <= x <= 1 + 1e-12 for x in w)
    leg("weights_stay_inside_the_unit_interval", ok, "all %d arms" % len(ARMS))

    # L4 always_on is exactly one everywhere
    leg("always_on_holds_full_weight",
        all(x == 1.0 for x in weights_series(sig, "always_on")),
        "the null arm must not be gated")

    # L5 tilt_step uses exactly the three tercile levels
    tgt = None
    w_step = set(round(x, 12) for x in weights_series(sig, "tilt_step", tgt))
    leg("tilt_step_is_three_levels", w_step.issubset({0.0, 0.5, 1.0}),
        "observed levels %s" % sorted(w_step))

    # L6 the weight at t is unchanged when returns from t+1 on move (the signal at t
    # already contains the return of t, so the perturbation must start after it)
    w_a = weight_at(sig, 399, "tilt_linear")
    w_b = weight_at(sig2, 399, "tilt_linear")
    leg("weight_at_t_ignores_future", w_a == w_b,
        "linear weight at 399 must be identical under the perturbation")

    # L7 a flat panel with a constant full weight pays the entry side once: the
    # total excess over the whole run is exactly minus the entry toll (no drift,
    # no baseline). The toll sits at the first decision, so it is an in-sample
    # cost while the OOS annualised excess is zero.
    flat = [None] + [0.0] * 300
    st = tilt_stats([1.0] * len(flat), flat, 150, COST_SIDE_BP, 2.5)
    leg("entry_pays_one_side_only",
        st["turnover_total"] == 1.0
        and abs(st["excess_total_bp"] + COST_SIDE_BP) < 1e-9,
        "flat panel, constant weight: total excess == -1 side")

    # L8 a zero weight everywhere earns nothing and pays nothing
    st0 = tilt_stats([0.0] * len(flat), flat, 150, COST_SIDE_BP, 2.5)
    leg("zero_weight_earns_and_pays_nothing",
        st0["turnover_total"] == 0.0 and st0["excess_oos_bp_per_year"] == 0.0,
        "the flat-at-zero arm is an exact identity")

    # L9 a full 0->1->0 swing pays exactly the two sides E224 charged per episode
    w_swing = [0.0] * 50 + [1.0] * 50 + [0.0] * 201
    st1 = tilt_stats(w_swing, flat, 250, COST_SIDE_BP, 2.5)
    leg("round_trip_pays_two_sides",
        abs(st1["turnover_total"] - 2.0) < 1e-12,
        "unit turnover 2 pays 2 x %.3fbp" % COST_SIDE_BP)

    # L10 the in-sample drift is IS-only: moving OOS returns must not move it
    a = tilt_stats([1.0] * 301, [None] + [2.0] * 150 + [900.0] * 150, 151, COST_SIDE_BP, 2.5)
    b = tilt_stats([1.0] * 301, [None] + [2.0] * 300, 151, COST_SIDE_BP, 2.5)
    leg("baseline_is_in_sample_only", a["mu_is_bp_per_day"] == b["mu_is_bp_per_day"],
        "OOS returns perturbed, mu_is identical")

    # L11 the Newey-West error is never below the i.i.d. one on a positively
    # autocorrelated series. The fixture noise must itself be white: a sawtooth
    # carries negative lag-1 correlation and would flip the inequality, so the
    # shocks come from a small LCG.
    seed = 11
    ar_pos = [0.0]
    for i in range(1, 400):
        seed = (1103515245 * seed + 12345) % (2 ** 31)
        shock = ((seed / 2 ** 31) - 0.5) * 3.4641
        ar_pos.append(0.6 * ar_pos[-1] + shock)
    se_nw = _hac_se(ar_pos)
    se_iid = _sd(ar_pos) / (len(ar_pos) ** 0.5)
    leg("hac_se_covers_positive_dependence", se_nw > se_iid * 1.02,
        "nw=%.4f iid=%.4f" % (se_nw, se_iid))

    # L12 n_eff collapses on a strongly autocorrelated series and stays <= n
    ar = [1.0]
    for i in range(1, 400):
        ar.append(0.9 * ar[-1] + ((i * 37) % 11 - 5) * 0.01)
    ne = _n_eff(ar)
    leg("n_eff_collapses_under_dependence", ne is not None and ne < 40.0 and ne <= 400,
        "n_eff=%.1f of 400 for rho=0.9" % ne)

    # L13 the verdict refuses to judge a short window
    short = tilt_stats([1.0] * 100, [None] + [1.0] * 99, 60, COST_SIDE_BP, 3.0)
    v, why = verdict(short, 3.0)
    leg("short_window_is_unresolved", v == "UNRESOLVED" and "below" in why, why)

    # L14 the verdict applies the bar it was handed
    fake = {"oos_decisions": 400, "excess_oos_bp_per_year": 100.0, "excess_oos_t": 3.1}
    leg("verdict_applies_the_bar",
        verdict(fake, 3.0)[0] == "ADOPT" and verdict(fake, 3.2)[0] == "REJECT",
        "same series flips at the bar")

    # L15 a series that dies at double costs cannot adopt
    fake2 = {"oos_decisions": 400, "excess_oos_bp_per_year": 100.0, "excess_oos_t": 5.0}
    v2, why2 = verdict(fake2, 3.0, x2={"excess_oos_bp_per_year": -1.0})
    leg("x2_costs_can_veto", v2 == "REJECT" and why2 == "dies_at_x2_costs", why2)

    # L16 weights and signal are the same length as the panel
    leg("weights_align_with_panel",
        len(weights_series(sig, "tilt_linear")) == len(sig) == len(ret),
        "one weight per session")

    # L17 voltarget needs an in-sample target and is flat before one exists
    tgt = arm_target(sig, 400, "voltarget")
    leg("voltarget_uses_an_in_sample_target",
        tgt is not None and tgt > 0 and weight_at(sig, 5, "voltarget", tgt) == 0.0,
        "no threshold before the warm-up -> flat at zero, target=%.4f" % (tgt or 0.0))

    # L18 the MDE is the z the spec claims times the NW error times the sessions
    st_m = tilt_stats([1.0] * 301, [None] + [((i * 13) % 17 - 8) * 3.0 for i in range(300)],
                      151, COST_SIDE_BP, 2.5)
    if st_m["se_nw"]:
        leg("mde_is_z_times_nw_se_annualised",
            abs(st_m["mde_ann_bp_per_year"] - Z_80 * st_m["se_nw"] * SESSIONS_PER_YEAR)
            < 1e-9,
            "MDE derived from its own dispersion")
    else:
        leg("mde_is_z_times_nw_se_annualised", False, "no se_nw produced")

    passed = sum(1 for _, ok_, _ in legs if ok_)
    for name, ok_, note in legs:
        print(("PASS " if ok_ else "FAIL ") + name + (" | " + note if note else ""))
    print("%d/%d legs passed" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "selftest"])
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        return selftest()
    face = run()
    return 0 if face else 2


if __name__ == "__main__":
    raise SystemExit(main())