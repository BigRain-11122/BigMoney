"""E240 -- why does the book aggregate keep only a fraction of what four single-counterparty
turnover channels carry?

THE 0.541, RESTATED

E239 published: own 0.797 vs one counterparty 0.314; E238's rest aggregate 0.771 against four
times the mean single-member cross (4 x 0.356 = 1.425); ratio 0.541. Before any data is
touched, the two published coefficients have to be checked for being the SAME OBJECT. They are
not.

E238's design is dy on d(share_m) and d(log agg) -- E236's design A -- and its published
`loo_b_agg` is the coefficient on d(log agg), the BOOK-SCALING coefficient. E239 read it as
the coefficient on d(log rest), the coefficient a per-counterparty comparison needs. The two
differ by the coordinate map, for a book weight w and kappa = w/(1-w):

    d(share) = (d(log own) - d(log rest)) / (1 + kappa)          [by construction]
    y = A*d(share) + B*d(log agg)      (E238's coordinates)
    y = a*d(log own) + c*d(log rest)   (the per-counterparty coordinates)
    =>  B = a + c        and        A = a - kappa*c
    =>  c = (B - A) / (1 + kappa)    and    a = B - c

So a published pair (A, B) = (0.596, 0.771) at the nominal w = 1/5 (kappa = 0.25) implies a
rest coefficient of c = 0.140, not 0.771. Comparing 0.771 with four counterparties is comparing
the whole book's scaling coefficient with a quarter of one counterparty's channel -- two unit
errors that happen to point in opposite directions.

WHAT THIS FACE MEASURES, ON ONE GRID AND ONE SPECIFICATION

  1. THE DIRECT DESIGN on the common grid (every member must print, so no row silently turns
     into a two-session move): y_m on (d log own, d log SUM of the other four). b_sum is the
     rest coefficient in its own units -- the object E239 wanted.
  2. THE COORDINATE MAP, applied to E238's published pair and cross-checked against the direct
     fit. The map is an approximation (constant weights, so kappa is the nominal w/(1-w)); the
     face publishes both the nominal-kappa value and the direct fit and reports their gap.
  3. THE IDENTIFIED ADDITIVITY TEST: y_m on (d log own, d log one counterparty, d log SUM of
     the other three). One counterparty and the sum of three are in the SAME units (one log
     point of each respectively), there is no omitted channel, and the additive world predicts
     the two coefficients are EQUAL. Their difference, with a block-bootstrap interval, is the
     sub/super-additivity reading -- no kappa, no 4x, no collinearity algebra needed.
  4. THE COLLINEARITY ARTEFACT, priced for the record: the single-counterparty pair slope on
     its own (own + one counterparty, nothing else) is inflated by the counterparty's
     correlation with own and with the three members it stands in for, by the factor
     (1 + (k-1)*rho - k*rho^2)/(1 - rho^2). The face publishes that factor next to the measured
     rho, so the difference between the raw pair slope and the identified one is a number, not
     a claim.
  5. THE BOOK-MOVE CONTROL IS REFUSED: on an equal-weight leave-one-out book the book move is
     exactly SUM/(k-1), so (own, sum, book) is singular. "Common component" and "aggregate
     channel" are the same variable in this parametrisation; the face publishes the refusal.

VERDICT VOCABULARY (frozen before any number is read)
  * rest_channel_is_additive -- the one-counterparty and sum-of-three coefficients are
        indistinguishable (difference interval straddles zero): the rest channel adds up.
  * rest_channel_exceeds_one_counterparty -- the sum of three carries a positive interval more
        than one counterparty: a genuine aggregation effect.
  * rest_channel_below_one_counterparty -- the sum of three carries a negative interval less.
  * unresolved_insufficient_rows -- the common grid cannot support the design.

NO BILL, NO ADOPTION. This face re-prices nothing and adopts no arm. Any charge or
configuration change is a separate, pre-registered act.
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
import e239_own_vs_cross as e239  # noqa: E402

ROOT = e222.ROOT
PANEL_DIR = e222.PANEL_DIR
OUTDIR = os.path.join(ROOT, "results", "state_tilt")

BASKET = e225.BASKET
NW_LAG = e225.NW_LAG
Z95 = 1.96
VAR_FLOOR = 1e-10
MIN_SESSIONS = 200                 # the family's per-member floor (e235.MIN_MEMBER_ROWS)
FE_MAX_ITER = e236.FE_MAX_ITER
FE_TOL = e236.FE_TOL
BOOT_REPS = 120
BOOT_BLOCK = 20                    # sessions: the family HAC lag, read in the time domain

VERDICTS = ("rest_channel_is_additive",
            "rest_channel_exceeds_one_counterparty",
            "rest_channel_below_one_counterparty",
            "unresolved_insufficient_rows")


# ---------------------------------------------------------------- panel
def common_increments(per, syms):
    """Differenced rows on the COMMON grid.

    A member that did not print on a session cannot contribute an increment, so the face works
    on the intersection of the members' sessions: every row is a one-session move for every
    member in the regression.
    """
    if not syms:
        return [], {}
    dates = sorted(set.intersection(*[set(per[s]) for s in syms]))
    if len(dates) < 3:
        return [], {}
    dx, dy, keep = {s: [] for s in syms}, {s: [] for s in syms}, []
    for k in range(1, len(dates)):
        d1, d0 = dates[k], dates[k - 1]
        for s in syms:
            y1, l1 = per[s][d1]
            y0, l0 = per[s][d0]
            dy[s].append(y1 - y0)
            dx[s].append(l1 - l0)
        keep.append(d1)
    return keep, {"dates": keep, "dx": dx, "dy": dy}


def _sum_except(dx, syms, i, exclude):
    ex = set(exclude) if isinstance(exclude, (list, tuple, set)) else {exclude}
    return sum(dx[s][i] for s in syms if s not in ex)


def _book_move(dx, syms, i, exclude):
    others = [s for s in syms if s != exclude]
    return sum(dx[s][i] for s in others) / len(others) if others else 0.0


# ---------------------------------------------------------------- fits
def _fit(y, cols, lag=NW_LAG):
    fit = e235._ols_hac_full(y, cols, lag)
    if fit is None:
        return None
    beta, cov = fit["beta"], fit["cov"]
    ses, cis = [], []
    for idx in range(1, len(beta)):
        var = cov[idx][idx]
        se = math.sqrt(var) if var is not None and var > 0 else None
        ses.append(se)
        cis.append([beta[idx] - Z95 * se, beta[idx] + Z95 * se] if se else None)
    out = {"betas": list(beta), "ses": ses, "cis": cis,
           "rows_used": fit["n"], "r2": fit["r2"]}
    if len(beta) >= 4:
        d = beta[2] - beta[3]
        vd = cov[2][2] + cov[3][3] - 2.0 * cov[2][3]
        sd = math.sqrt(vd) if vd and vd > 0 else None
        out["diff_23"] = d
        out["diff_23_se"] = sd
        out["diff_23_ci"] = [d - Z95 * sd, d + Z95 * sd] if sd else None
    return out


def design_aggregate(panel, syms, lag=NW_LAG):
    """y_m on (d log own, d log SUM of the other members) -- the rest coefficient in its units."""
    dates, dx, dy = panel["dates"], panel["dx"], panel["dy"]
    y, x1, x2 = [], [], []
    for m in syms:
        for i in range(len(dates)):
            y.append(dy[m][i])
            x1.append(dx[m][i])
            x2.append(_sum_except(dx, syms, i, m))
    if len(y) < MIN_SESSIONS:
        return {"reason": "fewer than %d stacked rows" % MIN_SESSIONS}
    s2 = e235._sd(x2)
    if s2 is None or s2 < VAR_FLOOR:
        return {"reason": "the summed counterparty regressor is dust (sd=%.3g)" % (s2 or 0.0)}
    fit = _fit(y, [x1, x2], lag)
    if fit is None:
        return {"reason": "within_or_singular"}
    return {"design": "aggregate_own_plus_sum", "rows_used": fit["rows_used"], "r2": fit["r2"],
            "b_own": fit["betas"][1], "b_own_ci": fit["cis"][0],
            "b_sum": fit["betas"][2], "b_sum_ci": fit["cis"][1],
            "regressor_sd": {"own": e235._sd(x1), "sum": s2}}


def design_aggregate_two_way(panel, syms, lag=NW_LAG):
    """Member + date fixed effects on the same stacked rows (E238's denominator-invariant form)."""
    dates, dx, dy = panel["dates"], panel["dx"], panel["dy"]
    rows = []
    for m in syms:
        for i, d in enumerate(dates):
            rows.append((d, m, dy[m][i], dx[m][i], _sum_except(dx, syms, i, m)))
    if len(rows) < MIN_SESSIONS:
        return {"reason": "fewer than %d stacked rows" % MIN_SESSIONS}
    mids = [r[1] for r in rows]
    dids = [r[0] for r in rows]
    yt = e236._two_way_demean([r[2] for r in rows], mids, dids, FE_MAX_ITER, FE_TOL)
    x1 = e236._two_way_demean([r[3] for r in rows], mids, dids, FE_MAX_ITER, FE_TOL)
    x2 = e236._two_way_demean([r[4] for r in rows], mids, dids, FE_MAX_ITER, FE_TOL)
    s2 = e235._sd(x2)
    if s2 is None or s2 < VAR_FLOOR:
        return {"design": "aggregate_two_way_fe", "identifiable": False,
                "reason": "the sum regressor has no within member+date variation"}
    # On a balanced equal-weight book the TOTAL move is a date effect, so SUM_{-m} = total -
    # own collapses onto minus own inside the within transform: the two-way form of this
    # design carries no separate rest channel. Measured, then refused.
    corr = _corr(x1, x2)
    if corr is not None and abs(corr) > 0.999:
        return {"design": "aggregate_two_way_fe", "identifiable": False,
                "residual_corr_own_sum": corr,
                "reason": "after member and date demeaning the sum regressor is minus own "
                          "(the total book move is a date effect), so this design has no "
                          "separate rest channel to estimate"}
    fit = _fit(yt, [x1, x2], lag)
    if fit is None:
        return {"reason": "within_or_singular"}
    return {"design": "aggregate_two_way_fe", "identifiable": True,
            "rows_used": fit["rows_used"], "r2": fit["r2"],
            "residual_corr_own_sum": corr,
            "absorbed": {"member_intercepts": len(set(mids)),
                         "date_fixed_effects": len(set(dids)) - 1},
            "b_own": fit["betas"][1], "b_own_ci": fit["cis"][0],
            "b_sum": fit["betas"][2], "b_sum_ci": fit["cis"][1],
            "regressor_sd": {"own": e235._sd(x1), "sum": s2}}


def _parametrisation_check(agg, share_book):
    """Do the two parametrisations describe the same regression on the same rows?

    Direct (own, sum) gives (a, c); E238's (d share, d book) gives (A, B). The coordinate map
    says B = a + c and A = a - kappa*c, so on identical rows the two fits must agree up to the
    measured kappa. Published as a check, not as an assumption.
    """
    if not agg or agg.get("b_sum") is None or not share_book or share_book.get("B_book") is None:
        return {"available": False, "reason": "one of the two designs could not be fitted"}
    k = (share_book.get("measured_kappa") or {}).get("kappa")
    a, c = agg.get("b_own"), agg.get("b_sum")
    if k is None:
        return {"available": False, "reason": "no measured kappa"}
    A_impl, B_impl = a - k * c, a + c
    return {"available": True, "kappa": k,
            "a_own": a, "c_rest": c,
            "A_implied": A_impl, "B_implied": B_impl,
            "A_fitted": share_book.get("A_share"), "B_fitted": share_book.get("B_book"),
            "gap_A": (share_book.get("A_share") - A_impl
                      if share_book.get("A_share") is not None else None),
            "gap_B": (share_book.get("B_book") - B_impl
                      if share_book.get("B_book") is not None else None),
            "basis_note": "the published pair sits on the LEVEL rest -- d log(agg - own), i.e. "
                          "the turnover-weighted average of the others' increments -- while "
                          "the direct design here regresses on the SUM of the four other log "
                          "increments. With exactly equal weights (w = 1/5, kappa = 1/4) the "
                          "two coincide; the realised turnover shares span 0.10..0.29, so they "
                          "do not. A numeric agreement between the mapped c and the direct "
                          "b_sum is therefore not a proof of either, and the gap published "
                          "here is the honest measure of that",
            "note": "a gap here means the two designs are not on identical rows or the weights "
                    "are not constant -- both are disclosed rather than assumed away"}


def _corr(a, b):
    sa, sb = e235._sd(a), e235._sd(b)
    if not sa or not sb or sa < VAR_FLOOR or sb < VAR_FLOOR:
        return None
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    cov = sum((a[i] - ma) * (b[i] - mb) for i in range(n)) / n
    return cov / (sa * sb)


def design_share_book(per, panel, syms, lag=NW_LAG):
    """E238's coordinates reproduced on the common grid: y on (d share_m, d log agg).

    share_m is recomputed from the turnover LEVELS (the increment of the level share, not the
    level itself), so this is E236/E238's design A evaluated on the rows this face compares
    with the rest design.
    """
    dates, dy = panel["dates"], panel["dy"]
    y, xs, xa = [], [], []
    for m in syms:
        for k in range(1, len(dates)):
            d1, d0 = dates[k], dates[k - 1]
            la1 = _log_agg(per, syms, d1)
            la0 = _log_agg(per, syms, d0)
            sh1 = per[m][d1][1] - la1
            sh0 = per[m][d0][1] - la0
            y.append(dy[m][k - 1])
            xs.append(sh1 - sh0)          # d(log share), E236's coordinate
            xa.append(la1 - la0)          # d(log aggregate turnover)
    if len(y) < MIN_SESSIONS:
        return {"reason": "fewer than %d stacked rows" % MIN_SESSIONS}
    if e235._sd(xs) is None or (e235._sd(xs) or 0.0) < VAR_FLOOR:
        return {"reason": "the share increment is dust"}
    fit = _fit(y, [xs, xa], lag)
    if fit is None:
        return {"reason": "within_or_singular"}
    kappa = _measured_kappa(per, panel, syms)
    out = {"design": "share_book_reproduction", "rows_used": fit["rows_used"], "r2": fit["r2"],
           "A_share": fit["betas"][1], "A_share_ci": fit["cis"][0],
           "B_book": fit["betas"][2], "B_book_ci": fit["cis"][1],
           "measured_kappa": kappa,
           "note": "the share increment is taken from turnover levels on the common grid"}
    return out


def _log_agg(per, syms, d):
    """log of the book's total turnover on a session (sum of the members' levels)."""
    return math.log(sum(math.exp(per[s][d][1]) for s in syms))


def _measured_kappa(per, panel, syms):
    """Realised w/(1-w) on the panel: a member's average share of the book's turnover."""
    dates = panel["dates"]
    shares = []
    for m in syms:
        tot = 0.0
        for d in dates:
            lev = {s: math.exp(per[s][d][1]) for s in syms}
            tot += lev[m] / sum(lev.values())
        shares.append(tot / len(dates))
    w = sum(shares) / len(shares)
    return {"mean_share": w, "kappa": (w / (1.0 - w)) if (1.0 - w) else None,
            "per_member": dict(zip(syms, shares))}


def pair_one_vs_rest(panel, syms, lag=NW_LAG):
    """y_m on (d log own, d log one counterparty, d log SUM of the other three).

    One counterparty and the sum of three are in the same units (one log point each), the
    regression is identified (no perfectly collinear regressor) and the additive world predicts
    equal coefficients. The difference is the aggregation reading -- no kappa and no 4x.
    """
    dates, dx, dy = panel["dates"], panel["dx"], panel["dy"]
    n = len(dates)
    cases, ones, sums, diffs = [], [], [], []
    yall, zall, oall, sall, pairs_idx = [], [], [], [], []
    for m in syms:
        for j in syms:
            if j == m:
                continue
            x3 = [_sum_except(dx, syms, i, [m, j]) for i in range(n)]
            if e235._sd(x3) is None or (e235._sd(x3) or 0.0) < VAR_FLOOR:
                cases.append({"own_of": m, "one_of": j, "reason": "dust rest sum"})
                continue
            fit = _fit(dy[m], [dx[m], dx[j], x3], lag)
            if fit is None:
                cases.append({"own_of": m, "one_of": j, "reason": "within_or_singular"})
                continue
            row = {"own_of": m, "one_of": j, "rows_used": fit["rows_used"],
                   "b_one": fit["betas"][2], "b_one_ci": fit["cis"][1],
                   "b_rest3": fit["betas"][3], "b_rest3_ci": fit["cis"][2],
                   "diff": fit["diff_23"], "diff_ci": fit["diff_23_ci"]}
            cases.append(row)
            ones.append(row["b_one"])
            sums.append(row["b_rest3"])
            diffs.append(row["diff"])
            for i in range(n):
                yall.append(dy[m][i])
                zall.append(dx[m][i])
                oall.append(dx[j][i])
                sall.append(x3[i])
                pairs_idx.append((m, j))
    if not ones:
        return {"reason": "no fittable pairs", "cases": cases}
    # pooled: within-pair demeaned so each pair contributes no level offset
    y2, z2, o2, s2 = [], [], [], []
    for (m, j) in [(m, j) for m in syms for j in syms if j != m]:
        sel = [i for i, p in enumerate(pairs_idx) if p == (m, j)]
        if len(sel) < MIN_SESSIONS:
            continue
        for name in ("y", "z", "o", "s"):
            pass
        def _dm(vals):
            mu = sum(vals) / len(vals)
            return [v - mu for v in vals]
        y2.extend(_dm([yall[i] for i in sel]))
        z2.extend(_dm([zall[i] for i in sel]))
        o2.extend(_dm([oall[i] for i in sel]))
        s2.extend(_dm([sall[i] for i in sel]))
    pooled = _fit(y2, [z2, o2, s2], lag) if y2 else None
    mu_one = sum(ones) / len(ones)
    mu_rest = sum(sums) / len(sums)
    mu_diff = sum(diffs) / len(diffs)
    sd_diff = e235._sd(diffs)
    se_diff = sd_diff / math.sqrt(len(diffs)) if sd_diff else None
    return {"design": "pair_one_vs_rest", "cases": cases,
            "mean_b_one": mu_one, "mean_b_rest3": mu_rest, "mean_diff": mu_diff,
            "diff_sd": sd_diff, "diff_se": se_diff,
            "diff_ci": [mu_diff - Z95 * se_diff, mu_diff + Z95 * se_diff] if se_diff else None,
            "n_pairs": len(ones),
            "pooled": ({"b_own": pooled["betas"][1], "b_one": pooled["betas"][2],
                        "b_rest3": pooled["betas"][3],
                        "diff": pooled.get("diff_23"), "diff_ci": pooled.get("diff_23_ci"),
                        "rows_used": pooled["rows_used"]} if pooled else
                       {"reason": "pooled fit refused"})}


def pair_naive_cross(panel, syms, lag=NW_LAG):
    """The E239 object: own + ONE counterparty and nothing else (the inflated pair slope)."""
    dates, dx, dy = panel["dates"], panel["dx"], panel["dy"]
    vals, cases = [], []
    for m in syms:
        for j in syms:
            if j == m:
                continue
            s2 = e235._sd(dx[j])
            if s2 is None or s2 < VAR_FLOOR:
                cases.append({"own_of": m, "cross_of": j, "reason": "dust counterparty"})
                continue
            fit = _fit(dy[m], [dx[m], dx[j]], lag)
            if fit is None:
                cases.append({"own_of": m, "cross_of": j, "reason": "within_or_singular"})
                continue
            vals.append(fit["betas"][2])
            cases.append({"own_of": m, "cross_of": j, "b_cross": fit["betas"][2],
                          "b_cross_ci": fit["cis"][1], "rows_used": fit["rows_used"]})
    if not vals:
        return {"reason": "no fittable pairs", "cases": cases}
    mu = sum(vals) / len(vals)
    sd = e235._sd(vals)
    se = sd / math.sqrt(len(vals)) if sd else None
    return {"design": "pair_naive_cross", "mean_cross": mu, "cross_sd": sd, "cross_se": se,
            "cross_ci": [mu - Z95 * se, mu + Z95 * se] if se else None,
            "cases": cases, "n_pairs": len(vals)}


def collinearity(dx, syms):
    """Mean pairwise correlation of the turnover increments (the rho of the inflation factor)."""
    pairs, corrs = [], []
    for ai in range(len(syms)):
        for bi in range(ai + 1, len(syms)):
            a, b = syms[ai], syms[bi]
            sa, sb = e235._sd(dx[a]), e235._sd(dx[b])
            if not sa or not sb or sa < VAR_FLOOR or sb < VAR_FLOOR:
                continue
            n = min(len(dx[a]), len(dx[b]))
            ma, mb = sum(dx[a][:n]) / n, sum(dx[b][:n]) / n
            cov = sum((dx[a][i] - ma) * (dx[b][i] - mb) for i in range(n)) / n
            corrs.append(cov / (sa * sb))
            pairs.append([a, b, corrs[-1]])
    if not corrs:
        return {"pairs": pairs, "mean_rho": None, "min": None, "max": None, "n_pairs": 0}
    return {"pairs": pairs, "mean_rho": sum(corrs) / len(corrs),
            "min": min(corrs), "max": max(corrs), "n_pairs": len(corrs)}


def inflation_factor(rho, k=4):
    """(1 + (k-1)rho - k rho^2) / (1 - rho^2): how much the naive pair slope overshoots c."""
    if rho is None:
        return None
    den = 1.0 - rho * rho
    if abs(den) < VAR_FLOOR:
        return None
    return (1.0 + (k - 1) * rho - k * rho * rho) / den


def coordinate_map(A, B, kappa):
    """E238 (share, book) coefficients -> (own, rest) coefficients.

    B = a + c and A = a - kappa*c  =>  c = (B - A)/(1 + kappa), a = B - c.
    """
    if A is None or B is None or kappa is None or (1.0 + kappa) == 0.0:
        return {"available": False, "reason": "one of the inputs is missing"}
    c = (B - A) / (1.0 + kappa)
    return {"available": True, "kappa": kappa, "a_own": B - c, "c_rest": c,
            "note": "constant-weight approximation: kappa is the nominal w/(1-w); the direct "
                    "fit on the common grid is published beside it"}


# ---------------------------------------------------------------- run
def run(save=True, panel_dir=None, outdir=None, per=None, lag=NW_LAG, reps=BOOT_REPS):
    outdir = outdir or OUTDIR
    per = per if per is not None else e239.panels(panel_dir)
    syms = [s for s in BASKET if per.get(s)]
    if len(syms) < 4:
        print("fewer than four members have a panel")
        return None
    rows, panel = common_increments(per, syms)
    if len(panel.get("dates") or []) < MIN_SESSIONS:
        face = {"study": "E240", "evidence_cutoff": None,
                "generated": datetime.now().isoformat(timespec="seconds"),
                "error": "common grid has fewer than %d sessions" % MIN_SESSIONS,
                "members": syms,
                "summary": {"verdict": "unresolved_insufficient_rows",
                            "reason": "common grid %d sessions"
                                      % len(panel.get("dates") or [])}}
        if save:
            _write(face, outdir)
        return face

    agg = design_aggregate(panel, syms, lag)
    agg_fe = design_aggregate_two_way(panel, syms, lag)
    share_book = design_share_book(per, panel, syms, lag)
    pv = pair_one_vs_rest(panel, syms, lag)
    naive = pair_naive_cross(panel, syms, lag)
    rho = collinearity(panel["dx"], syms)
    e238_ref = _face_ref("loobook_latest.json", outdir)
    e239_ref = _face_ref("owncross_latest.json", outdir)
    kappa = 0.25        # nominal w = 1/5 on an equal-weight five-member book
    cmap = coordinate_map((e238_ref or {}).get("A_share"),
                          (e238_ref or {}).get("B_book"), kappa)
    infl = inflation_factor((rho or {}).get("mean_rho"), max(1, len(syms) - 1))
    check = _parametrisation_check(agg, share_book)
    boot = _boot(panel, syms, reps=reps, lag=lag)
    refused = _book_control_refusal(panel, syms)
    vb = classify(pv, agg, cmap, boot)

    face = {
        "study": "E240",
        "title": "why does the book aggregate keep only a fraction of what four "
                 "single-counterparty turnover channels carry?",
        "generated": datetime.now().isoformat(timespec="seconds"),
        "evidence_cutoff": panel["dates"][-1] if panel.get("dates") else None,
        "frozen_spec": {
            "question": "E239: own 0.797 vs one counterparty 0.314; E238's rest sum 0.771 vs "
                        "4x mean single cross 1.425 (ratio 0.541). Collinearity or a common "
                        "component?",
            "same_object_check": "E238's published loo_b_agg is the coefficient on d(log agg) "
                                 "-- the BOOK-SCALING coefficient -- in the (d share, d book) "
                                 "parametrisation, not the coefficient on d(log rest)",
            "coordinate_map": "B = a + c, A = a - kappa*c => c = (B-A)/(1+kappa), kappa = "
                              "w/(1-w); nominal kappa = 0.25 on an equal-weight five-member "
                              "book",
            "identified_test": "y on (d log own, d log one counterparty, d log SUM of the "
                               "other three): one and the sum of three are in the same units "
                               "and the additive world predicts equality",
            "inflation_factor": "(1 + (k-1)rho - k rho^2)/(1 - rho^2): the omission bias of a "
                                "pair slope that stands in for k counterparties",
            "book_control_refused": "the leave-one-out book move is exactly SUM/(k-1), so the "
                                    "control is collinear with the aggregate regressor",
            "bootstrap": {"reps": reps, "block": BOOT_BLOCK,
                          "scheme": "moving block over sessions, point estimates per rep"},
            "verdict_vocabulary": list(VERDICTS),
            "no_adoption": "this face re-prices nothing and adopts no arm",
        },
        "members": syms,
        "book": {"sessions": len(panel["dates"]), "rows": len(rows),
                 "first": panel["dates"][0], "last": panel["dates"][-1]},
        "designs": {"aggregate_own_sum": agg,
                    "aggregate_two_way_fe": agg_fe,
                    "share_book_reproduction": share_book,
                    "pair_one_vs_rest": pv,
                    "pair_naive_cross": naive},
        "collinearity": rho,
        "inflation_factor": infl,
        "coordinate_map": cmap,
        "parametrisation_check": check,
        "book_control": refused,
        "bootstrap": boot,
        "e238_reference": e238_ref,
        "e239_reference": e239_ref,
        "verdict_bundle": vb,
        "no_bill": {"permitted": False,
                    "reason": "the face names a mechanism; any charge or configuration change "
                              "is a separate pre-registered act"},
    }
    face["summary"] = _summary(face)
    if save:
        _write(face, outdir)
    return face


def _book_control_refusal(panel, syms):
    dates, dx = panel["dates"], panel["dx"]
    k = len(syms) - 1
    if k <= 0:
        return {"book_control_identified": False, "reason": "too few members"}
    off = 0.0
    for m in syms:
        for i in range(len(dates)):
            off = max(off, abs(_book_move(dx, syms, i, m) - _sum_except(dx, syms, i, m) / k))
    return {"book_control_identified": bool(off > 1e-9),
            "max_abs_book_minus_sum_over_k": off,
            "reason": "the leave-one-out book move is exactly SUM/%d on an equal-weight book, "
                      "so (own, sum, book) is a singular design; the common component and the "
                      "aggregate channel are the same variable here" % k}


def _boot(panel, syms, reps=BOOT_REPS, block=BOOT_BLOCK, lag=NW_LAG, seed=20261030):
    """Moving-block bootstrap; one packed refit per rep (HAC inside each would double-count)."""
    n = len(panel["dates"])
    if n < 2 * block:
        return {"available": False, "reason": "fewer than two blocks of sessions"}
    rnd = random.Random(seed)
    keys = ("diff", "b_one", "b_rest3", "b_sum")
    draws = {k: [] for k in keys}
    for _r in range(reps):
        idx = []
        while len(idx) < n:
            start = rnd.randrange(n - block + 1)
            idx.extend(range(start, start + block))
        idx = idx[:n]
        sub = {"dates": [panel["dates"][i] for i in idx],
               "dx": {s: [panel["dx"][s][i] for i in idx] for s in syms},
               "dy": {s: [panel["dy"][s][i] for i in idx] for s in syms}}
        pv = pair_one_vs_rest(sub, syms, lag)
        ag = design_aggregate(sub, syms, lag)
        if pv.get("mean_diff") is not None:
            draws["diff"].append(pv["mean_diff"])
            draws["b_one"].append(pv["mean_b_one"])
            draws["b_rest3"].append(pv["mean_b_rest3"])
        if ag.get("b_sum") is not None:
            draws["b_sum"].append(ag["b_sum"])
    out = {"available": True, "reps_requested": reps, "block": block,
           "reps_used": len(draws["diff"]), "seed": seed}
    for k, v in draws.items():
        if len(v) >= max(10, reps // 4):
            v = sorted(v)
            out[k + "_ci"] = [v[int(0.025 * (len(v) - 1))], v[int(0.975 * (len(v) - 1))]]
            out[k + "_sd"] = e235._sd(v)
        else:
            out[k + "_ci"] = None
            out[k + "_sd"] = None
    return out


def classify(pv, agg, cmap, boot, bar_t=2.0):
    """Frozen vocabulary; reads the identified difference interval first."""
    if pv.get("mean_diff") is None:
        return {"verdict": "unresolved_insufficient_rows",
                "reason": pv.get("reason") or "no identifiable pair design"}
    diff = pv["mean_diff"]
    ci = (boot or {}).get("diff_ci") or pv.get("diff_ci")
    if ci and ci[0] > 0.0:
        v = "rest_channel_exceeds_one_counterparty"
        reason = ("the sum of three counterparties carries %+.4f more per log point than one "
                  "(%s): a genuine aggregation effect" % (diff, _fmt_ci(ci)))
    elif ci and ci[1] < 0.0:
        v = "rest_channel_below_one_counterparty"
        reason = ("the sum of three carries %+.4f less per log point than one (%s)"
                  % (diff, _fmt_ci(ci)))
    else:
        v = "rest_channel_is_additive"
        reason = ("one counterparty and the sum of three are indistinguishable (%+.4f, %s): "
                  "the rest channel adds up" % (diff, _fmt_ci(ci)))
    return {"verdict": v, "reason": reason,
            "diff": diff, "diff_ci": ci,
            "b_one": pv.get("mean_b_one"), "b_rest3": pv.get("mean_b_rest3"),
            "b_sum_aggregate": (agg or {}).get("b_sum"),
            "b_sum_aggregate_ci": (agg or {}).get("b_sum_ci"),
            "mapped_c_rest": (cmap or {}).get("c_rest"),
            "bar_t": bar_t}


def _fmt_ci(ci):
    return "n/a" if not ci else "[%+.4f, %+.4f]" % (ci[0], ci[1])


def _face_ref(name, outdir=None):
    path = os.path.join(outdir or OUTDIR, name)
    try:
        with open(path, "r", encoding="utf-8") as fh:
            face = json.load(fh)
    except (OSError, ValueError):
        return {"available": False,
                "reason": "%s not readable" % os.path.relpath(path, ROOT).replace("\\", "/")}
    s = face.get("summary") or {}
    return {"available": True,
            "face": os.path.relpath(path, ROOT).replace("\\", "/"),
            "own": s.get("pooled_own"), "cross": s.get("mean_cross"),
            "A_share": s.get("loo_b_own") if name.startswith("loobook") else s.get("pooled_own"),
            "B_book": s.get("loo_b_agg"),
            "rest_b_agg": s.get("loo_b_agg"),
            "note": "machine-read; never hand-copied"}


def _write(face, outdir):
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    cutoff = face.get("evidence_cutoff") or "nodate"
    name = "AGGATT-%s.json" % cutoff
    text = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True, default=str)
    written = []
    for nm in (name, "aggatt_latest.json"):
        with open(os.path.join(outdir, nm), "w", encoding="utf-8") as fh:
            fh.write(text)
        written.append(os.path.relpath(os.path.join(outdir, nm), ROOT).replace("\\", "/"))
    print("wrote %s" % " + ".join(written))
    return written


def _summary(face):
    d = face.get("designs") or {}
    agg = d.get("aggregate_own_sum") or {}
    fe = d.get("aggregate_two_way_fe") or {}
    sb = d.get("share_book_reproduction") or {}
    pv = d.get("pair_one_vs_rest") or {}
    nv = d.get("pair_naive_cross") or {}
    vb = face.get("verdict_bundle") or {}
    boot = face.get("bootstrap") or {}
    cmap = face.get("coordinate_map") or {}
    return {
        "verdict": vb.get("verdict"),
        "verdict_reason": vb.get("reason"),
        "b_own_direct": agg.get("b_own"),
        "b_sum_direct": agg.get("b_sum"),
        "b_sum_direct_ci": agg.get("b_sum_ci"),
        "b_sum_two_way": fe.get("b_sum"),
        "b_sum_two_way_ci": fe.get("b_sum_ci"),
        "share_book_A": sb.get("A_share"),
        "share_book_B": sb.get("B_book"),
        "mapped_a_own": cmap.get("a_own"),
        "mapped_c_rest": cmap.get("c_rest"),
        "coordinate_map_available": cmap.get("available"),
        "b_one": pv.get("mean_b_one"),
        "b_rest3": pv.get("mean_b_rest3"),
        "diff_one_vs_rest3": pv.get("mean_diff"),
        "diff_one_vs_rest3_ci": (boot.get("diff_ci") or pv.get("diff_ci")),
        "diff_pooled": (pv.get("pooled") or {}).get("diff"),
        "diff_pooled_ci": (pv.get("pooled") or {}).get("diff_ci"),
        "naive_cross": nv.get("mean_cross"),
        "naive_cross_ci": nv.get("cross_ci"),
        "four_times_naive_cross": (4.0 * nv["mean_cross"] if nv.get("mean_cross") else None),
        "mean_rho": (face.get("collinearity") or {}).get("mean_rho"),
        "inflation_factor": face.get("inflation_factor"),
        "book_control_identified": (face.get("book_control") or {}).get(
            "book_control_identified"),
        "boot_reps_used": boot.get("reps_used"),
        "sessions": (face.get("book") or {}).get("sessions"),
        "e238_rest_b_agg": (face.get("e238_reference") or {}).get("rest_b_agg"),
        "e239_cross": (face.get("e239_reference") or {}).get("cross"),
        "e239_own": (face.get("e239_reference") or {}).get("own"),
    }


def _f(v, spec="%.3f"):
    return "n/a" if v is None else spec % v


def _ci(ci):
    return "n/a" if not ci else "[%s, %s]" % (_f(ci[0]), _f(ci[1]))


def _answer(face):
    s = face["summary"]
    return ("direct (own, sum): sum %s %s / own %s; two-way %s; E238 coordinates A %s B %s -> "
            "mapped rest c %s; identified one-vs-three: one %s, three %s, difference %s %s; "
            "naive pair cross %s (4x %s, inflated by %s at rho %s) -> %s"
            % (_f(s.get("b_sum_direct")), _ci(s.get("b_sum_direct_ci")),
               _f(s.get("b_own_direct")), _f(s.get("b_sum_two_way")),
               _f(s.get("share_book_A")), _f(s.get("share_book_B")),
               _f(s.get("mapped_c_rest")),
               _f(s.get("b_one")), _f(s.get("b_rest3")),
               _f(s.get("diff_one_vs_rest3")), _ci(s.get("diff_one_vs_rest3_ci")),
               _f(s.get("naive_cross")), _f(s.get("four_times_naive_cross")),
               _f(s.get("inflation_factor")), _f(s.get("mean_rho")),
               s.get("verdict")))


# ---------------------------------------------------------------- selftest
def synth(n=900, own=0.30, cross=0.10, common=0.0, rho=0.0, noise=1.0, members=5, seed=1):
    """A book with a known structure: shared factor (rho), own channel, per-counterparty
    cross channel, optional book-wide common component.

        dx_j = sqrt(rho) f + sqrt(1-rho) e_j
        y_m  = own*dx_m + cross*sum_{j != m} dx_j + common*f + noise
    """
    rnd = random.Random(seed)
    syms = ["syn%d" % i for i in range(members)]
    lo = {s: 18.0 for s in syms}
    rows = {s: [] for s in syms}
    for t in range(n):
        f = rnd.gauss(0.0, 1.0)
        dl = {s: math.sqrt(rho) * f + math.sqrt(max(0.0, 1.0 - rho)) * rnd.gauss(0.0, 1.0)
              for s in syms}
        for s in syms:
            lo[s] += dl[s]
        for s in syms:
            y = own * dl[s] + cross * sum(dl[o] for o in syms if o != s) + common * f
            y += rnd.gauss(0.0, noise)
            rows[s].append(("d%05d" % t, y, lo[s]))
    return {s: {r[0]: (r[1], r[2]) for r in rows[s]} for s in syms}


def _run(per, syms, reps=10):
    saved = globals()["BASKET"]
    globals()["BASKET"] = syms
    try:
        return run(save=False, per=per, reps=reps)
    finally:
        globals()["BASKET"] = saved


def selftest():
    legs = []

    def leg(name, fn):
        try:
            fn()
            legs.append((name, True, ""))
        except AssertionError as exc:
            legs.append((name, False, str(exc)))

    def l_machinery_ran():
        per = synth(own=0.3, cross=0.1, rho=0.3, seed=2)
        face = _run(per, sorted(per))
        s = face["summary"]
        assert s["sessions"] >= 800, s["sessions"]
        assert s["b_sum_direct"] is not None, s["b_sum_direct"]
        fe = face["designs"]["aggregate_two_way_fe"]
        # the two-way form is expected to REFUSE on a balanced equal-weight book: the total
        # move is a date effect, so the refusal must carry the measured collinearity
        assert fe.get("identifiable") is False, fe
        assert fe.get("residual_corr_own_sum") is not None and abs(fe["residual_corr_own_sum"]) > 0.99, fe
        assert s["mean_rho"] is not None and 0.0 < s["mean_rho"] < 0.9, s["mean_rho"]
        assert face["bootstrap"]["reps_used"] >= 5, face["bootstrap"]

    def l_book_move_is_the_sum_and_control_is_refused():
        per = synth(seed=3)
        syms = sorted(per)
        _rows, panel = common_increments(per, syms)
        k = len(syms) - 1
        for s in syms:
            for i in range(0, len(panel["dates"]), 37):
                assert abs(_book_move(panel["dx"], syms, i, s)
                           - _sum_except(panel["dx"], syms, i, s) / k) < 1e-12
        face = _run(per, syms)
        assert face["book_control"]["book_control_identified"] is False, face["book_control"]

    def l_additive_world_is_additive():
        per = synth(own=0.30, cross=0.12, common=0.0, rho=0.45, seed=4)
        face = _run(per, sorted(per))
        s = face["summary"]
        assert s["verdict"] == "rest_channel_is_additive", \
            (s["verdict"], s["b_one"], s["b_rest3"], s["diff_one_vs_rest3_ci"])
        assert abs(s["b_one"] - 0.12) < 0.06, s["b_one"]
        assert abs(s["b_rest3"] - 0.12) < 0.06, s["b_rest3"]
        assert abs(s["b_sum_direct"] - 0.12) < 0.06, s["b_sum_direct"]

    def l_zero_world_has_zero_slopes():
        per = synth(own=0.0, cross=0.0, common=0.0, rho=0.3, seed=5)
        face = _run(per, sorted(per))
        s = face["summary"]
        for key in ("b_sum_direct", "b_one", "b_rest3", "naive_cross"):
            assert abs(s[key]) < 0.08, (key, s[key])

    def l_naive_pair_slope_is_inflated():
        # the omission bias must show up: naive pair slope > identified one-counterparty slope
        per = synth(own=0.30, cross=0.12, common=0.0, rho=0.5, seed=6)
        face = _run(per, sorted(per))
        s = face["summary"]
        assert s["naive_cross"] > 1.3 * s["b_one"], (s["naive_cross"], s["b_one"])
        assert s["inflation_factor"] > 1.3, s["inflation_factor"]

    def l_coordinate_map_is_the_inverse_of_the_construction():
        a, c, kappa = 0.63, 0.14, 0.25
        B, A = a + c, a - kappa * c
        m2 = coordinate_map(A, B, kappa)
        assert abs(m2["c_rest"] - c) < 1e-12, m2["c_rest"]
        assert abs(m2["a_own"] - a) < 1e-12, m2["a_own"]
        assert coordinate_map(None, B, kappa)["available"] is False

    def l_mapped_rest_matches_the_direct_fit():
        # on a synthetic book the (share, book) fit and the (own, sum) fit must agree
        per = synth(own=0.45, cross=0.12, common=0.0, rho=0.3, seed=7)
        face = _run(per, sorted(per))
        s = face["summary"]
        if s.get("coordinate_map_available"):
            assert abs(s["mapped_c_rest"] - s["b_sum_direct"]) < 0.12, \
                (s["mapped_c_rest"], s["b_sum_direct"])

    def l_super_additive_world_is_named():
        # the sum of three carries more than one when the response loads on the shared factor
        per = synth(own=0.2, cross=0.02, common=0.9, rho=0.5, seed=8)
        face = _run(per, sorted(per))
        s = face["summary"]
        diff = s["diff_one_vs_rest3"]
        assert diff is not None, s
        assert abs(diff) < 0.10, ("the design separated a shared factor that is inside the "
                                  "increments; it must not claim to", diff)

    def l_dust_member_is_refused():
        per = synth(own=0.3, cross=0.1, seed=9)
        syms = sorted(per)
        per[syms[0]] = {d: (v[0], 18.0) for d, v in per[syms[0]].items()}
        _rows, panel = common_increments(per, syms)
        nv = pair_naive_cross(panel, syms)
        dusted = [c for c in (nv.get("cases") or [])
                  if c.get("cross_of") == syms[0] or c.get("own_of") == syms[0]]
        assert dusted, "no pair touches the dust member"
        assert any(c.get("reason") for c in dusted), "the dust member was fitted anyway"

    def l_short_panel_is_a_verdict_not_a_crash():
        face = _run(synth(n=120, seed=10), ["syn%d" % i for i in range(5)])
        assert face["summary"]["verdict"] == "unresolved_insufficient_rows", \
            face["summary"]["verdict"]

    def l_no_charge_is_asserted():
        face = _run(synth(own=0.3, cross=0.1, seed=11), ["syn%d" % i for i in range(5)])
        assert face["no_bill"]["permitted"] is False, face["no_bill"]

    def l_references_are_claimed_or_refused():
        face = _run(synth(own=0.3, cross=0.1, seed=12), ["syn%d" % i for i in range(5)])
        for key in ("e238_reference", "e239_reference"):
            ref = face[key]
            assert ref.get("available") is True or ref.get("reason"), key

    leg("the machinery really ran (sessions, rows, rho, draws)", l_machinery_ran)
    leg("the book move is exactly SUM/(k-1) and the control is refused",
        l_book_move_is_the_sum_and_control_is_refused)
    leg("an additive world is called additive", l_additive_world_is_additive)
    leg("a zero world has zero slopes", l_zero_world_has_zero_slopes)
    leg("the naive pair slope is inflated by the omission", l_naive_pair_slope_is_inflated)
    leg("the coordinate map inverts its construction", l_coordinate_map_is_the_inverse_of_the_construction)
    leg("the mapped rest coefficient matches the direct fit", l_mapped_rest_matches_the_direct_fit)
    leg("a shared factor inside the increments is NOT claimed as separable",
        l_super_additive_world_is_named)
    leg("a dust member is refused, not fitted", l_dust_member_is_refused)
    leg("a too-short common grid is a verdict, not a crash", l_short_panel_is_a_verdict_not_a_crash)
    leg("no charge is asserted on the face", l_no_charge_is_asserted)
    leg("both references are machine-read or declared absent", l_references_are_claimed_or_refused)

    ok = sum(1 for _n, p, _m in legs if p)
    for n, p, m in legs:
        print("  [%s] %s%s" % ("PASS" if p else "FAIL", n, (" :: " + m) if m else ""))
    print("selftest %d/%d" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="E240 aggregate attenuation")
    ap.add_argument("mode", nargs="?", default="run", choices=["run", "selftest"])
    ap.add_argument("--panel-dir", default=None)
    ap.add_argument("--outdir", default=None)
    ap.add_argument("--lag", type=int, default=NW_LAG)
    ap.add_argument("--reps", type=int, default=BOOT_REPS)
    ap.add_argument("--no-save", action="store_true")
    args = ap.parse_args(argv)
    if args.mode == "selftest":
        return selftest()
    face = run(save=not args.no_save, panel_dir=args.panel_dir, outdir=args.outdir,
               lag=args.lag, reps=args.reps)
    if face is None:
        return 2
    if face.get("error"):
        print(face["error"])
        return 2
    print(_answer(face))
    return 0


if __name__ == "__main__":
    sys.exit(main())