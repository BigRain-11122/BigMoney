"""E239 -- own-turnover vs ONE counterparty's turnover, on identical footing.

E238 removed each member from its own book: the differenced design's own coefficient got
LARGER (0.437 -> 0.596) while the REST aggregate's coefficient was larger still (0.771 on
d(log rest)). Two readings survive that:

  * an economic ordering -- a member's own turnover matters less than the rest of the book's;
  * a units artefact -- the rest aggregate is the SUM of four members, so one log point of it
    is not one log point of a single participant.

Rescaling the sum to a mean changes only a constant (it multiplies the coefficient by four and
leaves every t-statistic alone), so it cannot settle the question. The apples-to-apples form is
per pair: regress dy on d(log own) and on d(log other_j) for EACH other member separately,
under the same specification, the same HAC lag, the same fixed effects, then compare the own
coefficient with the AVERAGE single-member cross coefficient.

WHAT IS PUBLISHED
  (1) per ordered pair (m, j), m != j: b_own, b_cross with Newey-West intervals.
  (2) the pooled pair design: within-pair-demeaned rows, one own slope and one cross slope,
      with the difference (b_own - b_cross) and its interval from the joint covariance.
  (3) the two-way fixed-effects form of the same pair test (member + date FE), which is
      denominator-invariant per E238.
  (4) the mean single-member cross coefficient with its dispersion, so "average cross" is a
      published number rather than a rearrangement.

VERDICT VOCABULARY (frozen before any number is read)
  * own_exceeds_a_single_counterparty -- the difference interval sits wholly above zero: the
        own channel is bigger than one counterparty's, matching an impact story.
  * own_and_single_counterparty_indistinguishable -- the difference interval straddles zero:
        the E238 ordering was the sum's units, and a common-liquidity story survives.
  * a_single_counterparty_exceeds_own -- the difference interval sits wholly below zero.
  * unresolved_no_pairs -- fewer than two members with enough overlapping sessions.

NO BILL, NO ADOPTION. This face re-prices nothing; it only asks whether the E238 ordering is
an economic statement or a unit. Same footing means: identical rows-per-pair construction,
identical HAC lag, identical demeaning, identical break bar.

Approximation disclosed: rows from different pairs of the same member are not independent, and
the HAC sandwich treats the stacked pair rows as one series. The per-pair intervals are the
honest independent object; the pooled interval is published as the tighter, more optimistic
reading and the two are compared in the summary.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e222_tom_overlay as e222  # noqa: E402
import e225_state_tilt as e225  # noqa: E402
import e233_empirical_gamma as e233  # noqa: E402
import e235_charge_granularity as e235  # noqa: E402
import e236_share_difference as e236  # noqa: E402

ROOT = e222.ROOT
PANEL_DIR = e222.PANEL_DIR
OUTDIR = os.path.join(ROOT, "results", "state_tilt")

BASKET = e225.BASKET
NW_LAG = e225.NW_LAG
MIN_PAIR_ROWS = e235.MIN_MEMBER_ROWS     # 200: the family's per-member floor
Z95 = 1.96
VAR_FLOOR = 1e-10                        # a regressor below this sd is dust, not variation
FE_MAX_ITER = e236.FE_MAX_ITER
FE_TOL = e236.FE_TOL

VERDICTS = ("own_exceeds_a_single_counterparty",
            "own_and_single_counterparty_indistinguishable",
            "a_single_counterparty_exceeds_own",
            "unresolved_no_pairs")


# ---------------------------------------------------------------- panels
def panels(panel_dir=None):
    """Per member: date -> (log|session move|, log turnover). Complete rows only."""
    panel_dir = panel_dir or PANEL_DIR
    per = {}
    for sym in BASKET:
        rows = e233.load_ohlc(sym, panel_dir)
        blk = {}
        for d, r, a in rows:
            if r is None or r == 0.0 or a is None or a <= 0.0:
                continue
            blk[d] = (math.log(abs(r)), math.log(a))
        if blk:
            per[sym] = blk
    return per


def pair_rows(per, m, j):
    """(date, dy, dlog own_m, dlog other_j) on consecutive joint sessions.

    "Consecutive" is taken on the INTERSECTION of the two members' dates, so a session the
    counterparty did not print cannot silently turn a one-day move into a two-day move.
    """
    a, b = per.get(m), per.get(j)
    if not a or not b:
        return []
    dates = sorted(set(a) & set(b))
    out = []
    for k in range(1, len(dates)):
        d1, d0 = dates[k], dates[k - 1]
        y1, l1 = a[d1]
        y0, l0 = a[d0]
        out.append((d1, y1 - y0, l1 - l0, b[d1][1] - b[d0][1]))
    return out


# ---------------------------------------------------------------- fits
def _fit(y, x1, x2, lag=NW_LAG):
    fit = e235._ols_hac_full(y, [x1, x2], lag)
    if fit is None:
        return None
    beta, cov = fit["beta"], fit["cov"]
    out = {"b_own": beta[1], "b_cross": beta[2], "rows_used": fit["n"], "r2": fit["r2"]}
    for label, idx in (("b_own", 1), ("b_cross", 2)):
        var = cov[idx][idx]
        se = math.sqrt(var) if var is not None and var > 0 else None
        out[label + "_se"] = se
        out[label + "_ci"] = ([beta[idx] - Z95 * se, beta[idx] + Z95 * se] if se else None)
        out[label + "_t_nw"] = (beta[idx] / se) if se else None
    out["diff"] = beta[1] - beta[2]
    vdiff = cov[1][1] + cov[2][2] - 2.0 * cov[1][2]
    se_diff = math.sqrt(vdiff) if vdiff > 0 else None
    out["diff_se"] = se_diff
    out["diff_ci"] = ([out["diff"] - Z95 * se_diff, out["diff"] + Z95 * se_diff]
                      if se_diff else None)
    out["diff_t_nw"] = (out["diff"] / se_diff) if se_diff else None
    return out


def _demean(vals):
    n = len(vals)
    if n == 0:
        return vals
    mu = sum(vals) / n
    return [v - mu for v in vals]


def fit_pair_blocks(blocks, lag=NW_LAG):
    """One slope pair on stacked rows, each pair block demeaned by its own mean.

    Within-pair demeaning is the pair fixed effect, so the pooled slopes carry no pair-level
    offset. Keeping k=3 (instead of 20 pair dummies) is not a shortcut in the estimate -- it
    is the same estimator written in the coordinates that make the HAC sandwich tractable.
    """
    use = [(m, j, blk) for (m, j, blk) in blocks if len(blk) >= MIN_PAIR_ROWS]
    if len(use) < 2:
        return {"reason": "fewer than two pair blocks with >= %d rows" % MIN_PAIR_ROWS}
    y, x1, x2 = [], [], []
    for _m, _j, blk in use:
        dy = _demean([r[1] for r in blk])
        d1 = _demean([r[2] for r in blk])
        d2 = _demean([r[3] for r in blk])
        if e235._sd(d2) is None or (e235._sd(d2) or 0.0) < VAR_FLOOR:
            continue
        y.extend(dy)
        x1.extend(d1)
        x2.extend(d2)
    if not y:
        return {"reason": "every pair block had a dust-level counterparty regressor"}
    fit = _fit(y, x1, x2, lag)
    if fit is None:
        return {"reason": "within_or_singular"}
    fit.update({"design": "pair_pooled", "pair_blocks": len(use),
                "within_pair_demeaned": True,
                "regressor_sd": {"own": e235._sd(x1), "cross": e235._sd(x2)},
                "note": "pair fixed effects via within-block demeaning; row overlap across "
                        "the same member's pairs is not modelled in the HAC sandwich"})
    return fit


def fit_pair_two_way(blocks, lag=NW_LAG):
    """Member + date fixed effects on the stacked pair rows. Denominator-invariant per E238."""
    rows = []
    for m, j, blk in blocks:
        for (d, dy, d1, d2) in blk:
            rows.append((d, m, dy, d1, d2))
    if len(rows) < MIN_PAIR_ROWS:
        return {"reason": "fewer than %d pair rows" % MIN_PAIR_ROWS}
    dates = sorted({r[0] for r in rows})
    if len(dates) < 3:
        return {"reason": "fewer than three dates"}
    member_ids = [r[1] for r in rows]
    date_ids = [r[0] for r in rows]
    yt = e236._two_way_demean([r[2] for r in rows], member_ids, date_ids,
                              FE_MAX_ITER, FE_TOL)
    x1 = e236._two_way_demean([r[3] for r in rows], member_ids, date_ids,
                              FE_MAX_ITER, FE_TOL)
    x2 = e236._two_way_demean([r[4] for r in rows], member_ids, date_ids,
                              FE_MAX_ITER, FE_TOL)
    if e235._sd(x2) is None or (e235._sd(x2) or 0.0) < VAR_FLOOR:
        return {"identifiable": False,
                "reason": "the counterparty regressor has no within member+date variation"}
    fit = _fit(yt, x1, x2, lag)
    if fit is None:
        return {"reason": "within_or_singular"}
    fit.update({"design": "pair_two_way_fe", "rows_used": len(yt),
                "absorbed": {"member_intercepts": len(set(member_ids)),
                             "date_fixed_effects": len(dates) - 1},
                "regressor_sd": {"own": e235._sd(x1), "cross": e235._sd(x2)}})
    return fit


# ---------------------------------------------------------------- statistics
def mean_cross(crosses):
    """Mean single-member cross coefficient with its dispersion across pairs."""
    vals = [c for c in crosses if c is not None]
    if len(vals) < 2:
        return {"n": len(vals), "mean": (vals[0] if vals else None), "sd": None,
                "se": None, "ci": None, "min": (vals[0] if vals else None),
                "max": (vals[0] if vals else None)}
    mu = sum(vals) / len(vals)
    sd = e235._sd(vals)
    se = sd / math.sqrt(len(vals))
    return {"n": len(vals), "mean": mu, "sd": sd, "se": se,
            "ci": [mu - Z95 * se, mu + Z95 * se] if se else None,
            "min": min(vals), "max": max(vals)}


def classify(fit, bar_t=2.0):
    """Frozen vocabulary. Reads only the published difference interval."""
    if not fit or fit.get("diff_ci") is None:
        return {"verdict": "unresolved_no_pairs",
                "reason": fit.get("reason") if fit else "no fitted design"}
    lo, hi = fit["diff_ci"]
    if lo > 0.0:
        v = "own_exceeds_a_single_counterparty"
    elif hi < 0.0:
        v = "a_single_counterparty_exceeds_own"
    else:
        v = "own_and_single_counterparty_indistinguishable"
    return {"verdict": v,
            "reason": "difference %+.4f with interval [%+.4f, %+.4f]"
                      % (fit["diff"], lo, hi),
            "diff": fit["diff"], "diff_ci": [lo, hi],
            "diff_t_nw": fit.get("diff_t_nw"),
            "clears_bar": (fit.get("diff_t_nw") is not None
                           and abs(fit["diff_t_nw"]) >= bar_t),
            "bar_t": bar_t}


# ---------------------------------------------------------------- run
def _e238_reference(outdir=None):
    """E238's published rest coefficient, machine-read (never hand-copied).

    E239 exists to price the same ordering in the units of ONE counterparty. If the sum's
    coefficient is not four times the mean single-member cross coefficient, the sum is not
    just a rescaling and that difference is itself a publishable reading.
    """
    path = os.path.join(outdir or OUTDIR, "loobook_latest.json")
    try:
        with open(path, "r", encoding="utf-8") as fh:
            face = json.load(fh)
    except (OSError, ValueError):
        return {"available": False,
                "reason": "E238 face not readable at %s" %
                          os.path.relpath(path, ROOT).replace("\\", "/")}
    s = face.get("summary") or {}
    b_agg = s.get("loo_b_agg")
    return {"available": b_agg is not None,
            "leave_one_out_book": os.path.relpath(path, ROOT).replace("\\", "/"),
            "rest_b_agg_loo": b_agg,
            "rest_b_agg_loo_ci": (face.get("pooled") or {})
                                 .get("leave_one_out", {}).get("differences", {})
                                 .get("b_agg_ci"),
            "note": "E238's rest coefficient is on d(log SUM of four members); one log point "
                    "of that sum is four participants' worth, so the apples-to-apples "
                    "comparison is against the published mean single-member cross below"}


def run(save=True, panel_dir=None, outdir=None, per=None, lag=NW_LAG):
    outdir = outdir or OUTDIR
    per = per if per is not None else panels(panel_dir)
    syms = [s for s in BASKET if per.get(s)]
    if len(syms) < 2:
        print("fewer than two members have a panel")
        return None

    cases, blocks, cross_vals = [], [], []
    for m in syms:
        for j in syms:
            if j == m:
                continue
            blk = pair_rows(per, m, j)
            blocks.append((m, j, blk))
            case = {"own_of": m, "cross_of": j, "rows": len(blk)}
            if len(blk) < MIN_PAIR_ROWS:
                case["reason"] = "fewer than %d overlapping sessions" % MIN_PAIR_ROWS
                cases.append(case)
                continue
            sd_cross = e235._sd([r[3] for r in blk])
            if sd_cross is None or sd_cross < VAR_FLOOR:
                case["reason"] = "counterparty regressor is dust (sd=%.3g)" % (sd_cross or 0.0)
                cases.append(case)
                continue
            fit = _fit([r[1] for r in blk], [r[2] for r in blk], [r[3] for r in blk], lag)
            if fit is None:
                case["reason"] = "within_or_singular"
                cases.append(case)
                continue
            case.update(fit)
            case["regressor_sd"] = {"own": e235._sd([r[2] for r in blk]),
                                    "cross": sd_cross}
            cross_vals.append(fit["b_cross"])
            cases.append(case)

    fitted = [c for c in cases if c.get("b_own") is not None]
    if len(fitted) < 2:
        face = {"study": "E239", "generated": datetime.now().isoformat(timespec="seconds"),
                "error": "fewer than two pairs could be fitted", "cases": cases}
        face["summary"] = {"verdict": "unresolved_no_pairs",
                          "reason": "fewer than two fittable pairs"}
        return face

    pooled = fit_pair_blocks(blocks, lag)
    two_way = fit_pair_two_way(blocks, lag)
    mc = mean_cross(cross_vals)
    bar_t = max(2.0, e222._z_two_sided(0.05 / max(1, 2 * len(fitted))))
    vb = classify(pooled, bar_t)
    vb_fe = classify(two_way, bar_t)

    # own coefficient read on the same footing as the mean cross: the pooled own slope
    own_pooled = pooled.get("b_own")
    own_vs_mean = None
    own_vs_mean_ci = None
    if own_pooled is not None and mc.get("mean") is not None and mc.get("se"):
        own_vs_mean = own_pooled - mc["mean"]
        half = Z95 * math.sqrt((pooled.get("b_own_se") or 0.0) ** 2 + mc["se"] ** 2)
        own_vs_mean_ci = [own_vs_mean - half, own_vs_mean + half]

    dates = sorted({r[0] for _m, _j, blk in blocks for r in blk})
    e238 = _e238_reference(outdir)
    if e238.get("available") and mc.get("mean") is not None:
        four = 4.0 * mc["mean"]
        e238["four_times_mean_cross"] = four
        e238["sum_implied_by_singles"] = four
        e238["ratio_published_over_four_singles"] = (
            e238["rest_b_agg_loo"] / four if four else None)
        e238["reading"] = ("if the rest coefficient were purely a rescaling of four "
                           "independent counterparties it would equal four times the mean "
                           "single-member cross; the published ratio says how much of the "
                           "sum is common variation rather than additive participant impact")

    face = {
        "study": "E239",
        "title": "is the own-turnover elasticity larger than the cross elasticity to ONE "
                 "counterparty's turnover, on identical footing?",
        "generated": datetime.now().isoformat(timespec="seconds"),
        "evidence_cutoff": dates[-1] if dates else None,
        "frozen_spec": {
            "question": "E238 found own 0.596 < rest 0.771 on d(log rest); the rest is a SUM "
                        "of four members, so one log point of it is four participants' worth. "
                        "Rescale by comparing per single counterparty instead.",
            "why_not_a_mean_rescale": "multiplying the rest regressor by 1/4 changes the "
                                      "coefficient by a constant factor and leaves every "
                                      "t-statistic unchanged -- it cannot settle units",
            "designs": ["pair_fe: within-pair-demeaned stacked rows, one own and one cross "
                        "slope (pair fixed effects in demeaned coordinates)",
                        "pair_two_way_fe: member + date fixed effects, denominator-invariant "
                        "per E238"],
            "same_footing": {"rows": "consecutive joint sessions of the two members",
                             "hac_lag": lag, "demeaning": "block mean (FE) / two-way",
                             "break_bar": bar_t},
            "multiplicity_basis": "two-sided 5%% over %d pair differences" % len(fitted),
            "verdict_vocabulary": list(VERDICTS),
            "no_adoption": "this face re-prices nothing and adopts nothing",
        },
        "members": syms,
        "pairs": cases,
        "pooled_pair_fe": pooled,
        "two_way_fe_pair_test": two_way,
        "mean_single_member_cross": mc,
        "own_pooled_vs_mean_cross": {"diff": own_vs_mean, "ci": own_vs_mean_ci,
                                     "note": "own pooled slope minus the mean per-pair cross "
                                             "slope, independent-se approximation"},
        "e238_reference": e238,
        "verdict_bundle": vb,
        "verdict_bundle_two_way": vb_fe,
        "book": {"panel": "data/daily basket (equal weight)", "members": syms,
                 "sessions": len(dates),
                 "first": dates[0] if dates else None,
                 "last": dates[-1] if dates else None},
        "no_bill": {"permitted": False,
                    "reason": "this face only asks whether the E238 ordering is an economic "
                              "statement or a unit; it publishes no charge and adopts no arm"},
    }
    face["summary"] = _summary(face)
    if save:
        if not os.path.isdir(outdir):
            os.makedirs(outdir)
        name = "OWNCROSS-%s.json" % face["evidence_cutoff"]
        text = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
        for nm in (name, "owncross_latest.json"):
            with open(os.path.join(outdir, nm), "w", encoding="utf-8") as fh:
                fh.write(text)
        rows = ["own_of,cross_of,rows,b_own,b_cross,diff,b_cross_ci_lo,b_cross_ci_hi,"
                "b_own_ci_lo,b_own_ci_hi"]
        for c in fitted:
            oci = c.get("b_own_ci") or [None, None]
            cci = c.get("b_cross_ci") or [None, None]
            rows.append("%s,%s,%d,%s,%s,%s,%s,%s,%s,%s" % (
                c["own_of"], c["cross_of"], c["rows"], _csv(c.get("b_own")),
                _csv(c.get("b_cross")), _csv(c.get("diff")), _csv(cci[0]), _csv(cci[1]),
                _csv(oci[0]), _csv(oci[1])))
        csv_name = "owncross_pairs_%s.csv" % face["evidence_cutoff"]
        with open(os.path.join(outdir, csv_name), "w", encoding="utf-8",
                  newline="\n") as fh:
            fh.write("\n".join(rows) + "\n")
        face["_written"] = [os.path.relpath(os.path.join(outdir, name), ROOT).replace(
            "\\", "/"), os.path.relpath(os.path.join(outdir, csv_name), ROOT).replace(
            "\\", "/")]
        print("wrote %s" % " + ".join(face["_written"]))
    return face


def _csv(v):
    return "" if v is None else ("%.6g" % v)


def _summary(face):
    pooled = face.get("pooled_pair_fe") or {}
    two = face.get("two_way_fe_pair_test") or {}
    mc = face.get("mean_single_member_cross") or {}
    vb = face.get("verdict_bundle") or {}
    vb2 = face.get("verdict_bundle_two_way") or {}
    fitted = [c for c in face.get("pairs") or [] if c.get("b_cross") is not None]
    return {
        "verdict": vb.get("verdict"),
        "verdict_reason": vb.get("reason"),
        "verdict_two_way": vb2.get("verdict"),
        "pooled_own": pooled.get("b_own"),
        "pooled_own_ci": pooled.get("b_own_ci"),
        "pooled_cross": pooled.get("b_cross"),
        "pooled_cross_ci": pooled.get("b_cross_ci"),
        "pooled_diff": pooled.get("diff"),
        "pooled_diff_ci": pooled.get("diff_ci"),
        "two_way_own": two.get("b_own"),
        "two_way_own_ci": two.get("b_own_ci"),
        "two_way_cross": two.get("b_cross"),
        "two_way_cross_ci": two.get("b_cross_ci"),
        "two_way_diff": two.get("diff"),
        "two_way_diff_ci": two.get("diff_ci"),
        "mean_cross": mc.get("mean"),
        "mean_cross_ci": mc.get("ci"),
        "mean_cross_min_max": [mc.get("min"), mc.get("max")],
        "pairs_fitted": len(fitted),
        "pairs_total": len(face.get("pairs") or []),
        "mean_of_pair_crosses": (sum(c["b_cross"] for c in fitted) / len(fitted)
                                 if fitted else None),
        "mean_of_pair_owns": (sum(c["b_own"] for c in fitted) / len(fitted)
                              if fitted else None),
        "pair_cross_sign_positive": sum(1 for c in fitted if c["b_cross"] > 0.0),
        "pair_own_sign_positive": sum(1 for c in fitted if c["b_own"] > 0.0),
        "own_pooled_vs_mean_cross": face.get("own_pooled_vs_mean_cross"),
        "designs_agree": (vb.get("verdict") == vb2.get("verdict")),
        "e238_rest_coefficient": (face.get("e238_reference") or {}).get("rest_b_agg_loo"),
        "four_times_mean_cross": (face.get("e238_reference") or {}).get(
            "four_times_mean_cross"),
        "ratio_published_over_four_singles": (face.get("e238_reference") or {}).get(
            "ratio_published_over_four_singles"),
        "bar_t": vb.get("bar_t"),
    }


def _f(v, spec="%.3f"):
    return "n/a" if v is None else spec % v


def _ci(ci):
    return "n/a" if not ci else "[%s, %s]" % (_f(ci[0]), _f(ci[1]))


def _answer(face):
    s = face["summary"]
    return ("own vs one counterparty: own %s %s vs cross %s %s (difference %s %s; two-way FE "
            "same test: own %s / cross %s / difference %s %s; mean single-member cross %s over "
            "%d pairs, range [%s, %s]) -> %s (two-way: %s)"
            % (_f(s.get("pooled_own")), _ci(s.get("pooled_own_ci")),
               _f(s.get("pooled_cross")), _ci(s.get("pooled_cross_ci")),
               _f(s.get("pooled_diff")), _ci(s.get("pooled_diff_ci")),
               _f(s.get("two_way_own")), _f(s.get("two_way_cross")),
               _f(s.get("two_way_diff")), _ci(s.get("two_way_diff_ci")),
               _f(s.get("mean_cross")), s.get("pairs_fitted") or 0,
               _f((s.get("mean_cross_min_max") or [None])[0]),
               _f((s.get("mean_cross_min_max") or [None, None])[1]),
               s.get("verdict"), s.get("verdict_two_way")))


# ---------------------------------------------------------------- selftest
def synth_panel(n=700, own=0.0, cross=0.0, noise=1.0, dlo_sd=0.6, members=5, seed=1):
    """A book where each member's move responds to its OWN turnover increment and to EACH
    other member's increment separately -- exactly the per-pair specification.

    own and cross are planted coefficients in units of one log point of one member's
    turnover, so `mean single-member cross` must recover `cross` (the increments are
    independent across members, so a single counterparty's slope is the planted value).
    """
    rnd = random.Random(seed)
    syms = ["syn%d" % i for i in range(members)]
    lo = {s: 18.0 for s in syms}
    rows = {s: [] for s in syms}
    for t in range(n):
        dl = {s: rnd.gauss(0.0, dlo_sd) for s in syms}
        for s in syms:
            lo[s] += dl[s]
        for s in syms:
            y = own * dl[s] + cross * sum(dl[o] for o in syms if o != s)
            y += rnd.gauss(0.0, noise)
            rows[s].append(("d%05d" % t, y, lo[s], dl[s]))
    per = {}
    for s in syms:
        per[s] = {r[0]: (r[1], r[2]) for r in rows[s]}
    return per, syms


def _panel_from_rows(rows_by_sym):
    """synth rows carry (date, y, log levels, increments); rebuild the (y, log_amt) panel."""
    return {s: {d: (y, lo) for (d, y, lo, _dl) in rows} for s, rows in rows_by_sym.items()}


def selftest():
    legs = []

    def leg(name, fn):
        try:
            fn()
            legs.append((name, True, ""))
        except AssertionError as exc:
            legs.append((name, False, str(exc)))

    def _run(**kw):
        per, syms = synth_panel(**kw)
        import builtins
        saved = globals()["BASKET"]
        globals()["BASKET"] = syms
        try:
            face = run(save=False, per=per)
        finally:
            globals()["BASKET"] = saved
        return face

    def l_planted_own_dominates():
        face = _run(own=0.60, cross=0.10, seed=3)
        assert face["summary"]["verdict"] == "own_exceeds_a_single_counterparty", \
            "verdict %r" % (face["summary"]["verdict"],)
        assert face["summary"]["verdict_two_way"] == "own_exceeds_a_single_counterparty", \
            "two-way verdict %r" % (face["summary"]["verdict_two_way"],)

    def l_planted_equal_is_indistinguishable():
        face = _run(own=0.30, cross=0.30, seed=4)
        assert face["summary"]["verdict"] == \
            "own_and_single_counterparty_indistinguishable", \
            "verdict %r" % (face["summary"]["verdict"],)

    def l_planted_cross_dominates():
        face = _run(own=0.10, cross=0.60, seed=5)
        assert face["summary"]["verdict"] == "a_single_counterparty_exceeds_own", \
            "verdict %r" % (face["summary"]["verdict"],)

    def l_mechanism_really_happened():
        # r1261 law: prove the machinery ran before trusting any equality
        face = _run(own=0.5, cross=0.2, seed=6)
        s = face["summary"]
        assert s["pairs_fitted"] == s["pairs_total"] == 20, (s["pairs_fitted"], s["pairs_total"])
        assert (face["pooled_pair_fe"].get("rows_used") or 0) > 5000, \
            "pooled rows %r" % (face["pooled_pair_fe"].get("rows_used"),)
        for k, v in (face["pooled_pair_fe"].get("regressor_sd") or {}).items():
            assert v is not None and v > 1e-6, "regressor %s sd %r" % (k, v)
        assert s["pair_cross_sign_positive"] >= 15, s["pair_cross_sign_positive"]

    def l_mean_cross_recovers_the_planted_value():
        face = _run(own=0.1, cross=0.45, seed=7)
        mc = face["mean_single_member_cross"]
        assert abs(mc["mean"] - 0.45) < 0.15, "mean cross %.3f vs planted 0.45" % mc["mean"]
        # and the published mean equals the mean of the published per-pair numbers
        fitted = [c["b_cross"] for c in face["pairs"] if c.get("b_cross") is not None]
        assert abs(sum(fitted) / len(fitted) - mc["mean"]) < 1e-9, "mean mismatch"

    def l_own_slope_recovers_the_planted_value():
        face = _run(own=0.55, cross=0.05, seed=8)
        assert abs(face["pooled_pair_fe"]["b_own"] - 0.55) < 0.2, \
            "own %.3f vs planted 0.55" % face["pooled_pair_fe"]["b_own"]

    def l_dust_counterparty_regressor_is_refused():
        # a counterparty that never trades has no cross variation: refuse, do not fit
        per, syms = synth_panel(own=0.4, cross=0.2, seed=9)
        frozen = syms[-1]
        per[frozen] = {d: (v[0], 18.0) for d, v in per[frozen].items()}
        saved = globals()["BASKET"]
        globals()["BASKET"] = syms
        try:
            face = run(save=False, per=per)
        finally:
            globals()["BASKET"] = saved
        bad = [c for c in face["pairs"] if c["cross_of"] == frozen or c["own_of"] == frozen]
        assert bad, "no cases reference the frozen member"
        assert any(c.get("reason") for c in bad), "dust rows were fitted anyway"

    def l_difference_interval_contains_its_point():
        face = _run(own=0.4, cross=0.2, seed=10)
        for name in ("pooled_pair_fe", "two_way_fe_pair_test"):
            fit = face[name]
            assert fit.get("diff_ci") and fit.get("diff") is not None, name
            lo, hi = fit["diff_ci"]
            assert lo <= fit["diff"] <= hi, "%s interval does not contain its point" % name
            assert hi - lo > 0.0, "%s zero-width interval" % name

    def l_zero_pairs_is_a_verdict_not_a_crash():
        per, syms = synth_panel(n=50, seed=11)     # below MIN_PAIR_ROWS
        saved = globals()["BASKET"]
        globals()["BASKET"] = syms
        try:
            face = run(save=False, per=per)
        finally:
            globals()["BASKET"] = saved
        assert face["summary"]["verdict"] == "unresolved_no_pairs", \
            face["summary"]["verdict"]

    def l_no_charge_is_asserted():
        face = _run(own=0.3, cross=0.1, seed=12)
        assert face["no_bill"]["permitted"] is False, face["no_bill"]

    def l_e238_reference_is_claimed_or_refused():
        # the cross-check must either machine-read E238 or say plainly it could not
        face = _run(own=0.3, cross=0.1, seed=13)
        ref = face["e238_reference"]
        assert ref.get("available") is True or ref.get("reason"), \
            "the E238 cross-check neither read a file nor declared its absence"
        if ref.get("available"):
            assert ref.get("four_times_mean_cross") is not None
            assert ref.get("ratio_published_over_four_singles") is not None

    leg("a planted own channel above the cross channel is called", l_planted_own_dominates)
    leg("a planted equal pair is called indistinguishable", l_planted_equal_is_indistinguishable)
    leg("a planted cross channel above own is called", l_planted_cross_dominates)
    leg("the machinery really ran (pairs, rows, regressor variance)", l_mechanism_really_happened)
    leg("the mean single-member cross recovers the planted value", l_mean_cross_recovers_the_planted_value)
    leg("the own slope recovers the planted value", l_own_slope_recovers_the_planted_value)
    leg("a dust counterparty regressor is refused, not fitted", l_dust_counterparty_regressor_is_refused)
    leg("every difference interval contains its point", l_difference_interval_contains_its_point)
    leg("no fittable pairs is a verdict, not a crash", l_zero_pairs_is_a_verdict_not_a_crash)
    leg("no charge is asserted on the face", l_no_charge_is_asserted)
    leg("the E238 cross-check is machine-read or declared absent", l_e238_reference_is_claimed_or_refused)

    ok = sum(1 for _n, p, _m in legs if p)
    for n, p, m in legs:
        print("  [%s] %s%s" % ("PASS" if p else "FAIL", n, (" :: " + m) if m else ""))
    print("selftest %d/%d" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="E239 own vs single counterparty turnover")
    ap.add_argument("mode", nargs="?", default="run", choices=["run", "selftest"])
    ap.add_argument("--panel-dir", default=None)
    ap.add_argument("--outdir", default=None)
    ap.add_argument("--lag", type=int, default=NW_LAG)
    ap.add_argument("--no-save", action="store_true")
    args = ap.parse_args(argv)
    if args.mode == "selftest":
        return selftest()
    face = run(save=not args.no_save, panel_dir=args.panel_dir, outdir=args.outdir,
               lag=args.lag)
    if face is None:
        return 2
    if face.get("error"):
        print(face["error"])
        return 2
    print(_answer(face))
    return 0


if __name__ == "__main__":
    sys.exit(main())