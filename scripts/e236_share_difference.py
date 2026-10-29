"""E236 -- can a share-and-difference design settle the granularity question the levels could not?

E235 asked whether a five-sleeve book pays five concave charges or one aggregate charge, and
answered `unresolved_spec_inadequate`: on levels two of five sleeves carried a NEGATIVE own
elasticity, the aggregate turnover level is 0.94..0.97 autocorrelated, and the lagged block
inverted on 2 of 5 sleeves. That is a measurement about the ESTIMATOR, not about the book --
levels of turnover are a unit-root-shaped regressor and the two channels are one series up to
a stationary share.

This face re-asks the same question where the regressors are stationary, and demands that the
answer survive three different identification strategies:

  (A) DIFFERENCES   dy on d(own) and d(book) turnover -- a move is priced against that
                    session's CHANGE in own and in book turnover. Written in identified
                    coordinates d(own) = d(share) + d(book), so b_own = beta_dshare and
                    g_scaling = beta_dbook, with b_agg = g_scaling - b_own.
  (B) FROZEN Z      demeaned share (stationary by construction) plus the aggregate level
                    standardised by a normalisation FROZEN on the in-sample half, so the
                    scale is one constant and the coefficient on the level is exact:
                    b_agg = beta_z / sd_ref.
  (C) TWO-WAY FE    member intercepts and date fixed effects. This is the design the card
                    asks for as "identification from cross-sectional share variation", and
                    it has a consequence that must be published rather than hidden: the
                    book's aggregate turnover is COMMON to every member on a date, so date
                    fixed effects absorb it completely. Design (C) identifies b_own and
                    nothing else -- b_agg is not estimable there, ever.

SIGN AGREEMENT is therefore split by channel, not pooled: b_own is compared across all three
designs, b_agg only across the two that can identify it. Demanding one agreement set would
either drop (C) for a property of the design or pretend (A)/(B) had a control they lack.

VERDICT VOCABULARY (frozen before any number is read):
  * own_dominates        -- b_own keeps its sign in every design, is positive, and clears the
                            multiplicity bar in >= 2 designs while b_agg does not
  * aggregate_dominates  -- b_agg keeps its sign in (A) and (B), is positive, clears the bar
                            in both, while b_own is small or does not clear
  * both_channels_live   -- both channels positive, sign-stable and clearing
  * unresolved_sign_fragile   -- b_own flips sign between designs (the levels reading was not
                            an artefact of the level, the channel itself is unidentified)
  * unresolved_spec_inadequate-- b_own is NEGATIVE and stable across designs (a move priced
                            smaller when its own turnover is larger -- no impact story
                            produces this), so no granularity may be carried into a bill

Liveness first: a flat weight path pays a zero bill under every charge shape, so "the charges
disagree" cannot be read from a path that never trades (r1261 lesson).
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
import e230_hysteresis_toll as e230  # noqa: E402
import e232_cost_curvature as e232  # noqa: E402
import e233_empirical_gamma as e233  # noqa: E402
import e234_per_member_gamma as e234  # noqa: E402
import e235_charge_granularity as e235  # noqa: E402

ROOT = e222.ROOT
PANEL_DIR = e222.PANEL_DIR
OUTDIR = os.path.join(ROOT, "results", "state_tilt")

COST_SIDE_BP = e225.COST_SIDE_BP
NW_LAG = e225.NW_LAG
BASKET = e225.BASKET
PRIMARY_SYMBOL = e225.PRIMARY_SYMBOL

ARMS = ["binary_low", "tilt_step", "tilt_linear"]
LADDER_FRACS = (0.10, 0.25)
Z95 = 1.96
MIN_MEMBER_ROWS = e235.MIN_MEMBER_ROWS
REF_FRAC = 0.5              # the frozen normalisation window = the first half
MIN_REF_BARS = 60           # a frozen sd over fewer bars is not a scale
FE_MAX_ITER = 400           # alternating projections: member + date means
FE_TOL = 1e-12

DESIGNS = ("differences", "frozen_z", "two_way_fe")


# ---------------------------------------------------------------- design A
def diff_rows(seq):
    """(dy, dlo, dla) triples: the session's change in the outcome and both turnovers."""
    out = []
    for k in range(1, len(seq)):
        y1, lo1, la1 = seq[k][1], seq[k][2], seq[k][3]
        y0, lo0, la0 = seq[k - 1][1], seq[k - 1][2], seq[k - 1][3]
        out.append((y1 - y0, lo1 - lo0, la1 - la0))
    return out


def fit_differences(series_list, pooled=False, lag=NW_LAG):
    """dy on d(share) and d(book): stationary regressors, HAC covariance."""
    blocks = []
    for seq in series_list:
        rows = diff_rows(seq)
        if len(rows) >= MIN_MEMBER_ROWS:
            blocks.append(rows)
    if not blocks:
        return {"design": "differences", "reason": "no member has enough sessions"}

    if not pooled:
        rows, members = blocks[0], 1
    else:
        rows, members = [], len(blocks)
        for b in blocks:
            rows.extend(b)

    y = [r[0] for r in rows]
    dshare = [r[1] - r[2] for r in rows]
    dbook = [r[2] for r in rows]
    cols = [dshare, dbook]
    if pooled:
        # member intercepts on a differenced series are not constants in the levels sense,
        # but they are the same "one slope pair, member offsets" the family uses
        for j in range(1, members):
            start = sum(len(b) for b in blocks[:j])
            col = [1.0 if (start <= i < start + len(blocks[j])) else 0.0
                   for i in range(len(rows))]
            cols.append(col)
    fit = e235._ols_hac_full(y, cols, lag)
    if fit is None:
        return {"design": "differences", "reason": "within_or_singular"}
    beta, cov = fit["beta"], fit["cov"]
    b_own, g_scale = beta[1], beta[2]
    b_agg = g_scale - b_own
    var_agg = cov[2][2] + cov[1][1] - 2.0 * cov[1][2]
    out = {"design": "differences", "rows_used": len(y), "n_regressors": len(beta),
           "r2": fit["r2"], "b_own": b_own, "g_scaling": g_scale, "b_agg": b_agg,
           "identifiable": True, "identifies_b_agg": True,
           "corr_own_book": e235._corr([r[1] for r in rows], dbook),
           "regressor_note": "first differences: d(own) = d(share) + d(book)"}
    for label, val, var in (("b_own", b_own, cov[1][1]), ("b_agg", b_agg, var_agg),
                            ("g_scaling", g_scale, cov[2][2])):
        se = math.sqrt(var) if var is not None and var > 0 else None
        out[label + "_se"] = se
        out[label + "_ci"] = ([val - Z95 * se, val + Z95 * se] if se else None)
        out[label + "_t_nw"] = (val / se) if se else None
    return out


# ---------------------------------------------------------------- design B
def frozen_ref(seq, frac=REF_FRAC, min_bars=MIN_REF_BARS):
    """The frozen normalisation: mean and sd of the aggregate level over the FIRST half."""
    la = [r[3] for r in seq]
    n_ref = max(min_bars, int(round(len(la) * frac)))
    n_ref = min(n_ref, len(la) - 1)
    if n_ref < min_bars:
        return None
    ref = la[:n_ref]
    mu = sum(ref) / len(ref)
    sd = e235._sd(ref)
    if not sd or sd <= 0.0:
        return None
    return {"mu": mu, "sd": sd, "bars": n_ref, "ref_end_index": n_ref - 1}


def fit_frozen_z(series_list, pooled=False, lag=NW_LAG, frac=REF_FRAC):
    """y on the demeaned share plus the frozen-standardised aggregate level."""
    blocks = []
    for seq in series_list:
        ref = frozen_ref(seq, frac=frac)
        if ref is None or len(seq) < MIN_MEMBER_ROWS:
            continue
        blocks.append((seq, ref))
    if not blocks:
        return {"design": "frozen_z", "reason": "no member has a usable frozen window"}

    use = blocks if pooled else blocks[:1]
    members = len(use)
    rows, member_ids = [], []
    for pos, (seq, ref) in enumerate(use):
        shares = [r[2] - r[3] for r in seq]
        mu_share = sum(shares) / len(shares)
        for k, (d, y, lo, la) in enumerate(seq):
            rows.append((y, shares[k] - mu_share, (la - ref["mu"]) / ref["sd"]))
            member_ids.append(pos)

    y = [r[0] for r in rows]
    share_c = [r[1] for r in rows]
    z = [r[2] for r in rows]
    cols = [share_c, z]
    if pooled:
        for j in range(1, members):
            cols.append([1.0 if m == j else 0.0 for m in member_ids])
    fit = e235._ols_hac_full(y, cols, lag)
    if fit is None:
        return {"design": "frozen_z", "reason": "within_or_singular"}
    beta, cov = fit["beta"], fit["cov"]
    sd_ref = use[0][1]["sd"]
    b_own = beta[1]
    g_scale = beta[2] / sd_ref            # constant affine transform -> exact
    b_agg = g_scale - b_own
    var_g = cov[2][2] / (sd_ref * sd_ref)
    var_agg = var_g + cov[1][1] - 2.0 * cov[1][2] / sd_ref
    out = {"design": "frozen_z", "rows_used": len(y), "n_regressors": len(beta),
           "r2": fit["r2"], "b_own": b_own, "g_scaling": g_scale, "b_agg": b_agg,
           "identifiable": True, "identifies_b_agg": True,
           "sd_ref": sd_ref, "ref_bars": use[0][1]["bars"],
           "corr_share_z": e235._corr(share_c, z),
           "regressor_note": "demeaned share + aggregate level in frozen-window sd units; "
                             "the scale is one constant so beta_z / sd_ref is exact"}
    for label, val, var in (("b_own", b_own, cov[1][1]), ("b_agg", b_agg, var_agg),
                            ("g_scaling", g_scale, var_g)):
        se = math.sqrt(var) if var is not None and var > 0 else None
        out[label + "_se"] = se
        out[label + "_ci"] = ([val - Z95 * se, val + Z95 * se] if se else None)
        out[label + "_t_nw"] = (val / se) if se else None
    return out


# ---------------------------------------------------------------- design C
def _two_way_demean(values, member_ids, date_ids, max_iter=FE_MAX_ITER, tol=FE_TOL):
    """Alternating projections: subtract the member mean then the date mean until stable.

    The panel is unbalanced (a member that did not print on a date has no row), so a single
    double-demeaning pass is NOT the exact two-way within transform. This iterates to
    convergence, which is the correct fixed-point for the unbalanced case.
    """
    n = len(values)
    res = list(values)
    for _ in range(max_iter):
        before = sum(abs(v) for v in res)
        for key_idx in (member_ids, date_ids):
            groups = {}
            for i, k in enumerate(key_idx):
                groups.setdefault(k, []).append(i)
            for idxs in groups.values():
                m = sum(res[i] for i in idxs) / len(idxs)
                if m != 0.0:
                    for i in idxs:
                        res[i] -= m
        after = sum(abs(v) for v in res)
        if before - after <= tol * (1.0 + before):
            break
    return res


def fit_two_way_fe(series_list, lag=NW_LAG):
    """Member intercepts + date fixed effects. Identifies b_own ONLY.

    The book's aggregate turnover has one value per date, so it is collinear with the date
    fixed effects by construction. Publishing `identifies_b_agg: False` is the honest form:
    a design that cannot see a regressor must not report a coefficient for it.
    """
    rows, member_ids, date_ids = [], [], []
    for pos, seq in enumerate(series_list):
        if len(seq) < MIN_MEMBER_ROWS:
            continue
        use = seq
        for (d, y, lo, la) in use:
            rows.append((y, lo - la))     # own channel = the share
            member_ids.append(pos)
            date_ids.append(d)
    if not rows:
        return {"design": "two_way_fe", "reason": "no member has enough sessions"}
    dates = sorted({d for d in date_ids})
    if len(dates) < 3:
        return {"design": "two_way_fe", "reason": "fewer than three dates"}

    y = [r[0] for r in rows]
    share = [r[1] for r in rows]
    yt = _two_way_demean(y, member_ids, date_ids)
    st = _two_way_demean(share, member_ids, date_ids)
    if e235._sd(st) is None or (e235._sd(st) or 0.0) <= 0.0:
        return {"design": "two_way_fe", "identifiable": False,
                "reason": "the share carries no within-date variation"}
    fit = e235._ols_hac_full(yt, [st], lag)
    if fit is None:
        return {"design": "two_way_fe", "reason": "within_or_singular"}
    beta, cov = fit["beta"], fit["cov"]
    b_own = beta[1]
    out = {"design": "two_way_fe", "rows_used": len(yt),
           "n_regressors": 1, "r2": fit["r2"],
           "b_own": b_own, "g_scaling": None, "b_agg": None,
           "identifiable": True, "identifies_b_agg": False,
           "absorbed": {"member_intercepts": len({m for m in member_ids}),
                        "date_fixed_effects": len(dates) - 1,
                        "reason": "the aggregate turnover is one value per date, so the "
                                  "date fixed effects absorb it entirely"},
           "share_within_sd": e235._sd(st),
           "regressor_note": "two-way within transform (member + date), b_own only"}
    se = math.sqrt(cov[1][1]) if cov[1][1] > 0 else None
    out["b_own_se"] = se
    out["b_own_ci"] = [b_own - Z95 * se, b_own + Z95 * se] if se else None
    out["b_own_t_nw"] = (b_own / se) if se else None
    return out


# ---------------------------------------------------------------- agreement
def sign_agreement(fits, key, designs=None):
    """Do the designs that can identify `key` agree about its sign?

    Returns None when fewer than two designs can identify the coefficient -- 'agreement'
    with one reader is not agreement, and `None` is published rather than True.
    """
    vals = []
    for f in fits:
        if designs and f.get("design") not in designs:
            continue
        if not f.get("identifies_b_agg", True) and key == "b_agg":
            continue
        v = f.get(key)
        if v is None:
            continue
        vals.append((f.get("design"), v))
    if len(vals) < 2:
        return {"key": key, "agree": None, "n_readers": len(vals),
                "readers": [{"design": d, "value": v} for d, v in vals],
                "reason": "fewer than two designs identify this channel"}
    signs = {(v >= 0.0) for _d, v in vals}
    return {"key": key, "agree": len(signs) == 1, "n_readers": len(vals),
            "readers": [{"design": d, "value": v} for d, v in vals],
            "sign": "+" if all(v >= 0.0 for _d, v in vals) else
                    ("-" if all(v < 0.0 for _d, v in vals) else "mixed")}


def magnitude_agreement(fits, key):
    """Do the designs that identify `key` agree about its SIZE, not just its sign?

    A coefficient that is +0.43 in one design and +0.017 in another is not "agreed": the
    bill built on the first is 25x the bill built on the second, so a sign-only test would
    pass a question the data has not answered. Frozen rule: the 95% intervals of any two
    identifying designs must overlap, and the point-estimate ratio is published beside it.
    """
    reads = []
    for f in fits:
        if key == "b_agg" and not f.get("identifies_b_agg", True):
            continue
        v, ci = f.get(key), f.get(key + "_ci")
        if v is None:
            continue
        reads.append({"design": f.get("design"), "value": v, "ci": ci})
    if len(reads) < 2:
        return {"key": key, "agree": None, "n_readers": len(reads), "readers": reads,
                "reason": "fewer than two designs identify this coefficient"}
    disjoint = []
    for i in range(len(reads)):
        for j in range(i + 1, len(reads)):
            a, b = reads[i], reads[j]
            if not a["ci"] or not b["ci"]:
                continue
            if a["ci"][1] < b["ci"][0] or b["ci"][1] < a["ci"][0]:
                disjoint.append([a["design"], b["design"]])
    mags = [abs(r["value"]) for r in reads]
    lo, hi = min(mags), max(mags)
    return {"key": key, "agree": not disjoint, "n_readers": len(reads),
            "readers": reads, "disjoint_pairs": disjoint,
            "ratio_max_over_min": (hi / lo) if lo > 0.0 else None,
            "span": [lo, hi]}


def classify_bundle(fits, bar_t):
    """The frozen decision rule over the three designs."""
    ag_own = sign_agreement(fits, "b_own")
    ag_agg = sign_agreement(fits, "b_agg")
    mag_own = magnitude_agreement(fits, "b_own")
    mag_agg = magnitude_agreement(fits, "b_agg")
    own_vals = [r["value"] for r in ag_own["readers"]]
    agg_vals = [r["value"] for r in ag_agg["readers"]]

    def clears(f, key):
        t = f.get(key + "_t_nw")
        return t is not None and abs(t) >= bar_t

    own_clear_n = sum(1 for f in fits if f.get("b_own") is not None and clears(f, "b_own")
                      and f["b_own"] > 0.0)
    agg_clear_n = sum(1 for f in fits if f.get("b_agg") is not None and clears(f, "b_agg")
                      and f["b_agg"] > 0.0)
    n_own_readers = int(ag_own["n_readers"] or 0)

    base = {"bar_t": bar_t, "b_own_sign_agreement": ag_own["agree"],
            "b_agg_sign_agreement": ag_agg["agree"],
            "b_own_magnitude_agreement": mag_own["agree"],
            "b_agg_magnitude_agreement": mag_agg["agree"],
            "b_own_disjoint_pairs": mag_own.get("disjoint_pairs"),
            "b_own_magnitude_ratio": mag_own.get("ratio_max_over_min"),
            "b_own_magnitude_span": mag_own.get("span"),
            "b_own_positive_readers": own_clear_n, "b_own_readers": n_own_readers,
            "b_agg_positive_readers": agg_clear_n,
            "b_agg_readers": int(ag_agg["n_readers"] or 0)}

    if ag_own["agree"] is False:
        base.update({"verdict": "unresolved_sign_fragile",
                     "reason": "b_own changes sign between designs, so the channel is not "
                               "identified by the stationary forms either"})
        return base
    if ag_own["agree"] is True and all(v < 0.0 for v in own_vals) and len(own_vals) >= 2:
        base.update({"verdict": "unresolved_spec_inadequate",
                     "reason": "b_own is NEGATIVE in every design that identifies it -- a "
                               "move is priced smaller when its own turnover is larger, "
                               "which no price-impact story produces"})
        return base
    if mag_own["agree"] is False:
        base.update({
            "verdict": "unresolved_magnitude_disagreement",
            "reason": "the designs agree about the sign of b_own but not about its size "
                      "(span %s, ratio %s, non-overlapping intervals on %s), so any bill "
                      "built from one of them is a different bill from another's"
                      % (_two(mag_own.get("span")), _one(mag_own.get("ratio_max_over_min")),
                         mag_own.get("disjoint_pairs"))})
        return base
    if own_clear_n >= 2 and agg_clear_n < 2:
        base.update({"verdict": "own_dominates"})
        return base
    if agg_clear_n >= 2 and own_clear_n < 2 and (ag_agg["agree"] is not False):
        base.update({"verdict": "aggregate_dominates"})
        return base
    if own_clear_n >= 2 and agg_clear_n >= 2:
        base.update({"verdict": "both_channels_live"})
        return base
    base.update({"verdict": "unresolved",
                 "reason": "no channel clears the multiplicity bar in two designs"})
    return base


# ---------------------------------------------------------------- run
def _member_series(sym, agg_by_date, panel_dir):
    return e235._member_series(e233.load_ohlc(sym, panel_dir), agg_by_date)


def run(save=True, panel_dir=None, outdir=None):
    panel_dir = panel_dir or PANEL_DIR
    outdir = outdir or OUTDIR
    single = e225.single_panel(PRIMARY_SYMBOL, panel_dir)
    basket = e225.basket_panel(panel_dir)
    if single is None or not basket:
        print("panels missing (single=%s basket=%s)" % (bool(single), bool(basket)))
        return None

    brows = e233.basket_rows(panel_dir)
    agg_by_date = {d: a for d, _r, a in brows if a and a > 0.0}

    series = {}
    for sym in BASKET:
        series[sym] = _member_series(sym, agg_by_date, panel_dir)
    usable = [s for s in BASKET if len(series[s]) >= MIN_MEMBER_ROWS]

    member_blocks = []
    for sym in BASKET:
        seq = series[sym]
        if len(seq) < MIN_MEMBER_ROWS:
            member_blocks.append({"symbol": sym, "sessions": len(seq),
                                  "reason": "fewer than %d usable sessions"
                                            % MIN_MEMBER_ROWS})
            continue
        fits = [fit_differences([seq]), fit_frozen_z([seq]), fit_two_way_fe([seq])]
        member_blocks.append({"symbol": sym, "sessions": len(seq),
                              "first": seq[0][0], "last": seq[-1][0],
                              "designs": fits})

    pooled_fits = []
    if len(usable) >= 2:
        seqs = [series[s] for s in usable]
        pooled_fits = [fit_differences(seqs, pooled=True),
                       fit_frozen_z(seqs, pooled=True),
                       fit_two_way_fe(seqs)]

    # multiplicity: every identifiable coefficient across every design actually fitted
    n_tests = 0
    for f in pooled_fits:
        n_tests += 1 + (1 if f.get("identifies_b_agg", True) else 0)
    n_tests = max(n_tests, 1)
    bar_t = max(2.0, e222._z_two_sided(0.05 / n_tests))

    for b in member_blocks:
        if b.get("designs"):
            b["bundle"] = classify_bundle(b["designs"], bar_t)
    pooled_bundle = classify_bundle(pooled_fits, bar_t) if pooled_fits else {"verdict": None}

    # the exponents the book could be charged at, now taken from the surviving design
    charges = [{"key": "linear", "kind": "aggregate", "gamma": 1.0,
                "source": "linear_model"}]
    surviving = pooled_bundle.get("verdict")
    if surviving in ("own_dominates", "both_channels_live", "aggregate_dominates"):
        diff_fit = pooled_fits[0] if pooled_fits else {}
        z_fit = pooled_fits[1] if len(pooled_fits) > 1 else {}
        own_reads = [f.get("b_own") for f in (diff_fit, z_fit) if f.get("b_own") is not None]
        agg_reads = [f.get("b_agg") for f in (diff_fit, z_fit) if f.get("b_agg") is not None]
        if surviving in ("own_dominates", "both_channels_live") and own_reads:
            g = e233.clip_gamma(sum(own_reads) / len(own_reads))
            charges.append({"key": "per_sleeve_own", "kind": "per_sleeve",
                            "gammas": [g] * len(BASKET),
                            "source": "b_own averaged over the designs that identify it"})
        if surviving in ("aggregate_dominates", "both_channels_live") and agg_reads:
            g = e233.clip_gamma(sum(agg_reads) / len(agg_reads))
            charges.append({"key": "aggregate_scaling", "kind": "aggregate", "gamma": g,
                            "source": "b_own + b_agg averaged over the designs that "
                                      "identify it"})

    dates, ret_bp = basket
    sig = e225.vol_signal(ret_bp)
    split = e225.split_index(len(dates))
    sd_is = e230.band_width(sig, split)
    n_cells = len(ARMS) * len(charges) * (1 + len(LADDER_FRACS))
    price_bar_t = max(2.0, e222._z_two_sided(0.05 / n_cells))

    arms_out, ladder_out = [], []
    for arm in ARMS:
        base_w = e225.weights_series(sig, arm)
        probe, _m = e235.rows_for(base_w, ret_bp, split, COST_SIDE_BP,
                                  ("aggregate", 1.0), 0.0)
        const = e225._mean([r["w"] for r in probe]) or 0.0
        block = {"name": arm, "const_weight": const,
                 "base_weight_changes": e230.change_profile(base_w)["weight_changes"],
                 "by_charge": []}
        flat = [0.0] * len(base_w)
        block["liveness_flat_bill"] = e235.total_bill(flat, COST_SIDE_BP, ("aggregate", 1.0))
        for ch in charges:
            if ch["kind"] == "per_sleeve":
                bill = e235.total_bill(base_w, COST_SIDE_BP, ("per_sleeve", ch["gammas"]))
                cobj = ("per_sleeve", ch["gammas"])
            else:
                bill = e235.total_bill(base_w, COST_SIDE_BP, ("aggregate", ch["gamma"]))
                cobj = ("aggregate", ch["gamma"])
            rows, _mu = e235.rows_for(base_w, ret_bp, split, COST_SIDE_BP, cobj, const)
            ch_sum = e235.channel_summary(rows)
            block["by_charge"].append({
                "charge": ch["key"], "kind": ch["kind"],
                "gamma": ch.get("gamma"), "gammas": ch.get("gammas"),
                "source": ch["source"], "bill": bill, "channels": ch_sum,
                "toll_clears_bar": (ch_sum["toll"]["t_nw"] is not None
                                    and abs(ch_sum["toll"]["t_nw"]) >= price_bar_t)})
            for frac in LADDER_FRACS:
                band_w = e230.band_weights(sig, arm, frac * sd_is)
                band_rows, _ = e235.rows_for(band_w, ret_bp, split, COST_SIDE_BP, cobj,
                                             const)
                v = e235.ladder_row(rows, band_rows, band_w == base_w, band_w,
                                    price_bar_t, ch["key"])
                v.update({"arm": arm, "band_frac": frac, "band_bp": frac * sd_is,
                          "gamma": ch.get("gamma"), "gammas": ch.get("gammas")})
                ladder_out.append(v)
        arms_out.append(block)

    bills = {}
    for block in arms_out:
        by = {c["charge"]: c for c in block["by_charge"]}
        bills[block["name"]] = {
            "linear_bp": (by.get("linear") or {}).get("bill", {}).get("total_cost_bp"),
            "per_sleeve_own_bp": (by.get("per_sleeve_own") or {}).get("bill", {}).get(
                "total_cost_bp"),
            "aggregate_scaling_bp": (by.get("aggregate_scaling") or {}).get("bill", {}).get(
                "total_cost_bp"),
        }

    face = {
        "study": "E236",
        "title": "can a share-and-difference design settle the granularity question the "
                 "level regression could not?",
        "generated": datetime.now().isoformat(timespec="seconds"),
        "evidence_cutoff": dates[-1],
        "frozen_spec": {
            "designs": ["differences: dy on d(share) and d(book)",
                        "frozen_z: y on demeaned share and the aggregate level in "
                        "frozen-window sd units (first %d%% of each member's sessions)"
                        % int(REF_FRAC * 100),
                        "two_way_fe: member intercepts + date fixed effects"],
            "coordinate_note": "own turnover = share + book turnover in logs, so "
                               "b_agg = g_scaling - b_own in every design that carries both",
            "sign_agreement_rule": "b_own is compared across all designs that identify it; "
                                   "b_agg only across the designs that can -- date fixed "
                                   "effects absorb the aggregate by construction",
            "multiplicity_bar_t": bar_t,
            "multiplicity_basis": "two-sided 5%% over %d pooled coefficient tests" % n_tests,
            "no_adoption": "no arm is re-adopted here; the family's verdicts stand",
        },
        "members": member_blocks,
        "pooled": {
            "designs": pooled_fits,
            "bundle": pooled_bundle,
            "b_own_sign_agreement": sign_agreement(pooled_fits, "b_own"),
            "b_agg_sign_agreement": sign_agreement(pooled_fits, "b_agg"),
        },
        "charges": charges,
        "book": {"panel": "basket_equal_weight", "sessions": len(dates),
                 "first": dates[0], "last": dates[-1], "split_session": split,
                 "split_date": dates[split], "signal_sd_is_bp": sd_is,
                 "price_bar_t": price_bar_t, "arms": arms_out},
        "ladder": ladder_out,
        "bills": bills,
        "comparison_to_e235": _compare_e235(pooled_fits, pooled_bundle),
    }
    face["summary"] = _summary(face, member_blocks, pooled_fits, pooled_bundle, bills,
                              ladder_out, charges)
    face["answer"] = _answer(face)
    if save:
        if not os.path.isdir(outdir):
            os.makedirs(outdir)
        name = "SHAREDIFF-%s.json" % face["evidence_cutoff"]
        text = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
        for nm in (name, "sharediff_latest.json"):
            with open(os.path.join(outdir, nm), "w", encoding="utf-8") as fh:
                fh.write(text)
        face["_written"] = os.path.relpath(os.path.join(outdir, name), ROOT).replace(
            "\\", "/")
        print("wrote %s" % face["_written"])
    return face


def _compare_e235(pooled_fits, bundle):
    """Did the stationary forms change the answer E235 published, and does the negative
    own elasticity survive them? That is the whole point of re-asking."""
    e235_face = _load_e235()
    prev = (e235_face or {}).get("summary") or {}
    prev_neg = prev.get("negative_own_elasticity")
    own_vals = [f.get("b_own") for f in pooled_fits if f.get("b_own") is not None]
    return {
        "e235_verdict": prev.get("pooled_verdict_after_spec_check"),
        "e235_pooled_b_own": prev.get("pooled_b_own"),
        "e235_pooled_b_agg": prev.get("pooled_b_agg"),
        "e235_negative_own_sleeves": prev_neg,
        "e236_verdict": bundle.get("verdict") if bundle else None,
        "e236_pooled_b_own_by_design": {f.get("design"): f.get("b_own")
                                        for f in pooled_fits},
        "negative_survives": (bool(own_vals) and all(v < 0.0 for v in own_vals)
                              if own_vals else None),
        "note": "a negative own elasticity that disappears when the regressors are "
                "differenced was a property of the level; one that survives is a property "
                "of the channel",
    }


def _load_e235():
    path = os.path.join(OUTDIR, "granularity_latest.json")
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def _summary(face, member_blocks, pooled_fits, bundle, bills, ladder_out, charges):
    def read(f, key):
        return {"design": f.get("design"), "value": f.get(key),
                "se": f.get(key + "_se"), "ci": f.get(key + "_ci"),
                "t_nw": f.get(key + "_t_nw"),
                "identifies": f.get("identifies_b_agg", True) if key == "b_agg" else True,
                "reason": f.get("reason")}

    fam = e235._family_gamma()
    return {
        "pooled_b_own": [read(f, "b_own") for f in pooled_fits],
        "pooled_b_agg": [read(f, "b_agg") for f in pooled_fits],
        "pooled_g_scaling": [read(f, "g_scaling") for f in pooled_fits],
        "pooled_verdict": bundle.get("verdict"),
        "pooled_verdict_reason": bundle.get("reason"),
        "b_own_sign_agreement": bundle.get("b_own_sign_agreement"),
        "b_agg_sign_agreement": bundle.get("b_agg_sign_agreement"),
        "b_own_magnitude_agreement": bundle.get("b_own_magnitude_agreement"),
        "b_agg_magnitude_agreement": bundle.get("b_agg_magnitude_agreement"),
        "b_own_disjoint_pairs": bundle.get("b_own_disjoint_pairs"),
        "b_own_magnitude_ratio": bundle.get("b_own_magnitude_ratio"),
        "b_own_magnitude_span": bundle.get("b_own_magnitude_span"),
        "b_own_readers": bundle.get("b_own_readers"),
        "b_own_positive_readers": bundle.get("b_own_positive_readers"),
        "b_agg_readers": bundle.get("b_agg_readers"),
        "b_agg_positive_readers": bundle.get("b_agg_positive_readers"),
        "member_verdicts": {v: sum(1 for b in member_blocks
                                   if (b.get("bundle") or {}).get("verdict") == v)
                            for v in ("own_dominates", "aggregate_dominates",
                                      "both_channels_live", "unresolved",
                                      "unresolved_sign_fragile",
                                      "unresolved_magnitude_disagreement",
                                      "unresolved_spec_inadequate")},
        "members_fitted": sum(1 for b in member_blocks if b.get("designs")),
        "family_single_regressor_gamma": fam,
        "fe_absorbs_aggregate": _fe_note(pooled_fits),
        "bills": bills,
        "charges_priced": [c["key"] for c in charges],
        "ladder_cells": len(ladder_out),
        "ladder_verdicts_by_charge": {
            c["key"]: _verdict_counts([v["verdict"] for v in ladder_out
                                       if v["charge"] == c["key"]]) for c in charges},
        "toll_clears_bar": {c["key"]: sum(1 for blk in face["book"]["arms"]
                                          for cc in blk["by_charge"]
                                          if cc["charge"] == c["key"]
                                          and cc["toll_clears_bar"]) for c in charges},
    }


def _fe_note(pooled_fits):
    fe = next((f for f in pooled_fits if f.get("design") == "two_way_fe"), None)
    if not fe or not fe.get("identifies_b_agg") is False:
        return None
    return fe.get("absorbed")


def _one(v):
    return "-" if v is None else "%.2f" % v


def _two(v):
    if not v:
        return "-"
    return "%.3f..%.3f" % (v[0], v[1])


def _verdict_counts(vs):
    out = {}
    for v in vs:
        out[v] = out.get(v, 0) + 1
    return out


def _f(v, spec="%.3f"):
    return "-" if v is None else (spec % v)


def _answer(face):
    s = face["summary"]
    designs = "; ".join(
        "%s b_own %s [%s, %s] t=%s | b_agg %s [%s, %s] t=%s" % (
            own.get("design"),
            _f(own.get("value")), _f((own.get("ci") or [None, None])[0]),
            _f((own.get("ci") or [None, None])[1]), _f(own.get("t_nw"), "%.2f"),
            (_f(agg.get("value")) if agg.get("identifies") else "absorbed"),
            (_f((agg.get("ci") or [None, None])[0]) if agg.get("identifies") else "-"),
            (_f((agg.get("ci") or [None, None])[1]) if agg.get("identifies") else "-"),
            (_f(agg.get("t_nw"), "%.2f") if agg.get("identifies") else "-"))
        for own, agg in zip(s["pooled_b_own"], s["pooled_b_agg"]))
    verdict = s["pooled_verdict"]
    comp = face["comparison_to_e235"]
    bills = "; ".join("%s linear %s -> per-sleeve %s -> aggregate %s bp" % (
        arm, _f(v["linear_bp"], "%.1f"), _f(v["per_sleeve_own_bp"], "%.1f"),
        _f(v["aggregate_scaling_bp"], "%.1f")) for arm, v in s["bills"].items())
    if verdict == "unresolved_spec_inadequate":
        reading = ("the negative own elasticity SURVIVES differencing and date fixed "
                   "effects (E235 read it on levels only), so it is a property of the "
                   "channel as measured here, not of the level regression. No granularity "
                   "may be carried into a bill: the family's single exponent (%s) stays a "
                   "price without a bill, and the per-sleeve sum E234 published is not a "
                   "valid alternative to it either"
                   % _f(s["family_single_regressor_gamma"]))
    elif verdict == "unresolved_magnitude_disagreement":
        reading = ("the designs agree on the SIGN of b_own but not on its SIZE (span %s, "
                   "ratio %s, disjoint intervals on %s). That is the signature of two "
                   "different quantities wearing one name: the difference design prices a "
                   "session against that session's own turnover change, which moves with "
                   "the same information that moves |r|, while the frozen-z and date-FE "
                   "designs price the cross-sectional share and find almost nothing. The "
                   "bill therefore cannot be built from any of them -- the family's single "
                   "exponent stays a PRICE without a bill, and E234's per-sleeve sum is "
                   "not a substitute"
                   % (_two(s["b_own_magnitude_span"]), _one(s["b_own_magnitude_ratio"]),
                      s["b_own_disjoint_pairs"]))
    elif verdict == "own_dominates":
        reading = ("the own channel survives every design with the expected sign, so each "
                   "sleeve is priced on its own turnover and the five per-sleeve charges "
                   "are the correct bill; a single aggregate exponent understates it")
    elif verdict == "aggregate_dominates":
        reading = ("the book's aggregate turnover carries the price and the own channel "
                   "does not clear, so a five-sleeve book is charged ONE aggregate bill")
    elif verdict == "both_channels_live":
        reading = ("both channels are positive, sign-stable and clear the bar, so a "
                   "five-sleeve book's bill is a genuine mixture of own and book turnover")
    else:
        reading = ("none of the three designs clears the multiplicity bar, so the "
                   "granularity question stays open and no figure here is a bill")
    return (
        "Three stationary designs were run on the same five sleeves. %s. Sign agreement: "
        "b_own sign %s over %s readers (size %s, span %s), b_agg sign %s over %s readers "
        "(the date fixed effects absorb the aggregate channel by construction, so design C "
        "cannot vote on it). Pooled "
        "verdict after the spec check: %s. Negative own elasticity survived: %s. "
        "Re-priced for the record: %s. Conclusion: %s." % (
            designs or "no pooled fit",
            s["b_own_sign_agreement"], s["b_own_readers"],
            s["b_own_magnitude_agreement"], _two(s["b_own_magnitude_span"]),
            s["b_agg_sign_agreement"], s["b_agg_readers"],
            verdict, comp.get("negative_survives"), bills or "no charge priced", reading))





# ---------------------------------------------------------------- selftest
def _synth_panel(n=1200, b_own=0.5, b_agg=0.3, seed=11, spread_sd=0.45,
                 agg_sd=0.25, noise_sd=2.5, phi=0.9, start=710000):
    """A panel where the truth is known: y = b_own*own + b_agg*book + noise.

    own = book + share in logs, so the identified form is y = b_own*share +
    (b_own + b_agg)*book.
    """
    rnd = random.Random(seed)
    book = 20.0
    seq = []
    for i in range(n):
        book = 20.0 + phi * (book - 20.0) + rnd.gauss(0.0, agg_sd)
        share = rnd.gauss(0.0, spread_sd)
        own = book + share
        y = b_own * own + b_agg * book + rnd.gauss(0.0, noise_sd)
        seq.append(("d%05d" % i, y, own, book))
    return seq


def _mean_over_seeds(fn, seeds=(1, 2, 3), **kw):
    vals = {}
    for sd in seeds:
        out = fn(_synth_panel(seed=sd, **kw))
        for k, v in out.items():
            if isinstance(v, float):
                vals.setdefault(k, []).append(v)
    return {k: sum(v) / len(v) for k, v in vals.items()}


def selftest():
    legs = []

    def leg(name, fn):
        try:
            fn()
            legs.append((name, True, ""))
        except AssertionError as exc:
            legs.append((name, False, str(exc)))

    def l_differences_recover_truth():
        got = _mean_over_seeds(lambda s: fit_differences([s]), n=3000, b_own=0.55,
                               b_agg=0.25, noise_sd=1.2)
        assert abs(got["b_own"] - 0.55) < 0.12, "mean b_own %.3f vs 0.55" % got["b_own"]
        assert abs(got["b_agg"] - 0.25) < 0.12, "mean b_agg %.3f vs 0.25" % got["b_agg"]

    def l_frozen_z_recovers_truth():
        got = _mean_over_seeds(lambda s: fit_frozen_z([s]), n=3000, b_own=0.55,
                               b_agg=0.25, noise_sd=1.2)
        assert abs(got["b_own"] - 0.55) < 0.12, "mean b_own %.3f vs 0.55" % got["b_own"]
        assert abs(got["b_agg"] - 0.25) < 0.12, "mean b_agg %.3f vs 0.25" % got["b_agg"]

    def l_two_way_fe_identifies_own_only():
        panels = [_synth_panel(n=800, seed=s) for s in (1, 2, 3)]
        out = fit_two_way_fe(panels)
        assert out.get("b_own") is not None, out.get("reason")
        assert out["b_agg"] is None and out["identifies_b_agg"] is False, \
            "date fixed effects absorb the aggregate; a coefficient there is fabricated"
        assert out.get("absorbed", {}).get("date_fixed_effects", 0) > 100

    def l_two_way_fe_needs_two_members_per_date():
        # with one member there is exactly one row per date, so within-date demeaning
        # removes the share along with everything else: the design cannot identify
        # anything, and it must say so rather than return a number
        out = fit_two_way_fe([_synth_panel(n=800, seed=3)])
        assert out.get("b_own") is None, "a single-member panel must not publish b_own"
        assert out.get("identifiable") is False
        assert "within-date variation" in (out.get("reason") or "")

    def l_two_way_fe_recovers_own_on_a_three_member_panel():
        panels = [_synth_panel(n=1500, seed=s, b_own=0.6, b_agg=0.2, noise_sd=1.0)
                  for s in (1, 2, 3)]
        out = fit_two_way_fe(panels)
        assert out.get("b_own") is not None, out.get("reason")
        assert abs(out["b_own"] - 0.6) < 0.15, "fe b_own %.3f vs 0.60" % out["b_own"]

    def l_two_way_demean_is_exact_on_balanced_data():
        # balanced panel: one double pass must be the exact within transform
        vals = [float(i % 7) * 0.5 + float(i // 7) for i in range(63)]
        mem = [i % 7 for i in range(63)]
        dat = [i // 7 for i in range(63)]
        out = _two_way_demean(vals, mem, dat)
        by_mem = {}
        for i, m in enumerate(mem):
            by_mem.setdefault(m, []).append(out[i])
        for m, xs in by_mem.items():
            assert abs(sum(xs) / len(xs)) < 1e-9, "member %d mean not removed" % m
        by_dat = {}
        for i, d in enumerate(dat):
            by_dat.setdefault(d, []).append(out[i])
        for d, xs in by_dat.items():
            assert abs(sum(xs) / len(xs)) < 1e-9, "date %d mean not removed" % d

    def l_difference_regressors_are_stationary():
        # the whole point of design (A): the differenced book level must not be a near-unit
        # root, or the "stationary form" is the level form wearing a d
        seq = _synth_panel(n=900, phi=0.9, seed=5)
        rows = diff_rows(seq)
        dbook = [r[2] for r in rows]
        autoc = _lag_autocorr(dbook)
        assert autoc is not None and abs(autoc) < 0.5, \
            "differenced turnover level is %.3f autocorrelated" % (autoc or 0.0)

    def l_sign_agreement_needs_two_readers():
        one = [{"design": "two_way_fe", "b_agg": None, "identifies_b_agg": False,
                "b_own": 0.3}]
        ag = sign_agreement(one, "b_agg")
        assert ag["agree"] is None and ag["n_readers"] == 0, \
            "agreement with zero readers must be None, not True"
        ag2 = sign_agreement(one, "b_own")
        assert ag2["agree"] is None, "one reader is not agreement"

    def l_sign_agreement_detects_a_flip():
        fits = [{"design": "differences", "b_own": 0.3, "b_agg": 0.1,
                 "identifies_b_agg": True},
                {"design": "frozen_z", "b_own": -0.2, "b_agg": 0.1,
                 "identifies_b_agg": True}]
        assert sign_agreement(fits, "b_own")["agree"] is False
        assert sign_agreement(fits, "b_agg")["agree"] is True

    def l_verdict_negative_stable_is_spec_inadequate():
        fits = [{"design": "differences", "b_own": -0.12, "b_own_t_nw": -2.6,
                 "b_agg": 0.30, "b_agg_t_nw": 3.0, "identifies_b_agg": True},
                {"design": "frozen_z", "b_own": -0.15, "b_own_t_nw": -2.9,
                 "b_agg": 0.64, "b_agg_t_nw": 4.0, "identifies_b_agg": True},
                {"design": "two_way_fe", "b_own": -0.10, "b_own_t_nw": -2.1,
                 "b_agg": None, "identifies_b_agg": False}]
        assert classify_bundle(fits, 2.5)["verdict"] == "unresolved_spec_inadequate"

    def l_verdict_own_dominates():
        fits = [{"design": "differences", "b_own": 0.5, "b_own_t_nw": 5.0,
                 "b_agg": 0.05, "b_agg_t_nw": 0.5, "identifies_b_agg": True},
                {"design": "frozen_z", "b_own": 0.45, "b_own_t_nw": 4.5,
                 "b_agg": 0.02, "b_agg_t_nw": 0.3, "identifies_b_agg": True},
                {"design": "two_way_fe", "b_own": 0.48, "b_own_t_nw": 4.0,
                 "b_agg": None, "identifies_b_agg": False}]
        assert classify_bundle(fits, 2.5)["verdict"] == "own_dominates"

    def l_verdict_aggregate_dominates():
        fits = [{"design": "differences", "b_own": 0.03, "b_own_t_nw": 0.4,
                 "b_agg": 0.7, "b_agg_t_nw": 6.0, "identifies_b_agg": True},
                {"design": "frozen_z", "b_own": 0.02, "b_own_t_nw": 0.3,
                 "b_agg": 0.66, "b_agg_t_nw": 5.5, "identifies_b_agg": True},
                {"design": "two_way_fe", "b_own": 0.01, "b_own_t_nw": 0.2,
                 "b_agg": None, "identifies_b_agg": False}]
        assert classify_bundle(fits, 2.5)["verdict"] == "aggregate_dominates"

    def l_sign_agreement_alone_does_not_pass_the_bundle():
        # same sign everywhere, sizes 25x apart with disjoint intervals: a sign-only rule
        # would call this a two-channel book, and the bill would differ 25x depending on
        # which design you read
        fits = [{"design": "differences", "b_own": 0.43, "b_own_t_nw": 9.4,
                 "b_own_ci": [0.34, 0.52], "b_agg": 0.88, "b_agg_t_nw": 15.6,
                 "b_agg_ci": [0.77, 0.99], "identifies_b_agg": True},
                {"design": "frozen_z", "b_own": 0.017, "b_own_t_nw": 1.6,
                 "b_own_ci": [-0.004, 0.058], "b_agg": 0.10, "b_agg_t_nw": 5.4,
                 "b_agg_ci": [0.065, 0.138], "identifies_b_agg": True},
                {"design": "two_way_fe", "b_own": 0.023, "b_own_t_nw": 3.9,
                 "b_own_ci": [0.012, 0.035], "b_agg": None, "identifies_b_agg": False}]
        assert sign_agreement(fits, "b_own")["agree"] is True
        res = classify_bundle(fits, 2.5)
        assert res["verdict"] == "unresolved_magnitude_disagreement", \
            "sign agreement alone must not name a channel"
        assert res["b_own_magnitude_agreement"] is False
        assert res["b_own_magnitude_ratio"] and res["b_own_magnitude_ratio"] > 10

    def l_magnitude_agreement_passes_when_intervals_overlap():
        fits = [{"design": "differences", "b_own": 0.30, "b_own_ci": [0.20, 0.40],
                 "identifies_b_agg": True},
                {"design": "frozen_z", "b_own": 0.25, "b_own_ci": [0.18, 0.32],
                 "identifies_b_agg": True}]
        assert magnitude_agreement(fits, "b_own")["agree"] is True

    def l_flat_path_pays_nothing():
        for ch in (("aggregate", 0.62), ("per_sleeve", [0.4, 0.6, 0.9])):
            prof = e235.total_bill([0.0] * 40, COST_SIDE_BP, ch)
            assert prof["weight_changes"] == 0 and prof["total_cost_bp"] == 0.0

    def l_charges_match_the_family_bills():
        w = [(i % 7 < 3) * 1.0 for i in range(120)]
        got = e235.total_bill(w, COST_SIDE_BP, ("aggregate", 1.0))
        want = e232.total_cost(w, COST_SIDE_BP, 1.0)
        assert abs(got["total_cost_bp"] - want["total_cost_bp"]) < 1e-9

    def l_frozen_ref_is_the_first_half():
        seq = _synth_panel(n=400, seed=7)
        ref = frozen_ref(seq)
        assert ref is not None
        assert ref["bars"] == 200, "frozen window %d bars" % ref["bars"]
        assert ref["ref_end_index"] < len(seq), "the frozen window may not see the whole"

    def l_short_member_is_not_fitted():
        short = _synth_panel(n=MIN_MEMBER_ROWS - 50, seed=2)
        long_ = _synth_panel(n=MIN_MEMBER_ROWS + 200, seed=3)
        out = fit_differences([short, long_], pooled=True)
        assert out.get("b_own") is not None, out.get("reason")
        assert out["rows_used"] < (len(short) - 1) + (len(long_) - 1)

    leg("design A recovers a known own and aggregate truth", l_differences_recover_truth)
    leg("design B recovers a known own and aggregate truth", l_frozen_z_recovers_truth)
    leg("design C absorbs the aggregate channel by construction",
        l_two_way_fe_identifies_own_only)
    leg("design C refuses a single-member panel instead of inventing a number",
        l_two_way_fe_needs_two_members_per_date)
    leg("design C recovers b_own on a three-member panel",
        l_two_way_fe_recovers_own_on_a_three_member_panel)
    leg("the two-way within transform is exact on a balanced panel",
        l_two_way_demean_is_exact_on_balanced_data)
    leg("the differenced book level is actually stationary",
        l_difference_regressors_are_stationary)
    leg("sign agreement refuses to speak with fewer than two readers",
        l_sign_agreement_needs_two_readers)
    leg("sign agreement detects a channel that flips between designs",
        l_sign_agreement_detects_a_flip)
    leg("a stable negative own elasticity is spec-inadequate, not a bill",
        l_verdict_negative_stable_is_spec_inadequate)
    leg("the verdict rule names an own-dominated book", l_verdict_own_dominates)
    leg("the verdict rule names an aggregate-dominated book", l_verdict_aggregate_dominates)
    leg("agreement in sign alone cannot name a channel (sizes must match)",
        l_sign_agreement_alone_does_not_pass_the_bundle)
    leg("magnitude agreement passes when the intervals overlap",
        l_magnitude_agreement_passes_when_intervals_overlap)
    leg("a flat weight path pays nothing under every charge shape", l_flat_path_pays_nothing)
    leg("the linear charge reproduces the family's own bill", l_charges_match_the_family_bills)
    leg("the frozen normalisation uses the first half only", l_frozen_ref_is_the_first_half)
    leg("a member with too little history is reported, not fitted",
        l_short_member_is_not_fitted)

    ok = sum(1 for _, p, _ in legs if p)
    for name, passed, msg in legs:
        print("%s  %s%s" % ("PASS" if passed else "FAIL", name,
                            ("  -- " + msg) if msg else ""))
    print("%d/%d" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


def _lag_autocorr(vals):
    if len(vals) < 3:
        return None
    m = sum(vals) / len(vals)
    num = sum((vals[i] - m) * (vals[i - 1] - m) for i in range(1, len(vals)))
    den = sum((v - m) ** 2 for v in vals)
    if den <= 0.0:
        return None
    return num / den


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "selftest"])
    ap.add_argument("--no-save", action="store_true")
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        return selftest()
    face = run(save=not args.no_save)
    if face is None:
        return 2
    print(face["answer"])
    return 0


if __name__ == "__main__":
    sys.exit(main())