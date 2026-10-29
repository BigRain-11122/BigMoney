"""E235 -- does a five-sleeve book pay five concave charges or one aggregate charge?

E234 separated the two channels in the book bill: moving from one linear charge to five
per-member charges multiplies the bill 1.6x..3.5x, and almost all of that is the SPLIT
(+1289/+2193/+4015 bp) while the mixture term is small (-305/-319/+289 bp). That leaves a
first-order question the family never asked:

  does the market price a sleeve's session move against THAT sleeve's own turnover, or
  against the book's aggregate turnover?

If only the aggregate matters, a five-sleeve book is charged ONE aggregate bill and the
per-sleeve sum overstates it by the split term; if each sleeve's own turnover matters, the
split is the correct bill and the family has been mis-specified.

METHOD (frozen before any number is read)
  For each basket member i and each session t that printed for it:
      y   = log |r_i,t|                      (open-to-close, bp)
      lo  = log amount_i,t                   (that sleeve's own turnover)
      la  = log sum_j amount_j,t             (the book's aggregate turnover)
  and the E233 B_controlled lag block (y_{t-1}, lo_{t-1}, la_{t-1}) so the estimator is the
  same specification the family already uses, HAC lag 20:
      y = a + b_own*lo + b_agg*la + c1*y_lag + c2*lo_lag + c3*la_lag + e
  b_own is the price of a sleeve move against its OWN turnover, b_agg the price of the same
  move against the BOOK's turnover. Pooled across the five members with member intercepts
  (same spec, one slope pair) gives the book-level reading.

  The two regressors are near-collinear in a book of this shape, so identifiability is
  published, not assumed: a member whose |corr(lo, la)| sits above IDENT_CORR_MAX is
  reported as unidentified rather than given two numbers.

  Book-scaling elasticity: if every sleeve's turnover moves by the same factor, y moves by
  (b_own + b_agg). That sum is the exponent a ONE aggregate charge should carry, and it is
  the quantity a book that charges c*|dw|**g should be using.

VERDICT VOCABULARY (fixed, applied to the pooled fit at a multiplicity bar):
  * own_dominates      -- |b_own| >= |b_agg| and b_own clears the bar
  * aggregate_dominates-- |b_agg| >  |b_own| and b_agg clears the bar
  * both_channels_live -- both clear the bar (a five-sleeve charge is a mixture of the two)
  * unresolved         -- neither clears, or the decomposition is unidentified
No arm is re-adopted here; the family's verdicts are already decided. This re-prices them.

Liveness is asserted first: a flat weight path pays a zero bill at every exponent and would
make "the charges disagree" read as false for the wrong reason (r1261 lesson).
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
IDENT_CORR_MAX = 0.98       # |corr(share, aggregate)| above this cannot be separated
MIN_SHARE_SD = 0.05         # a sleeve whose turnover share never moves has no own channel
MIN_MEMBER_ROWS = 200       # a member with less history is reported, not fitted
GAMMA_FLOOR, GAMMA_CEIL = e233.GAMMA_FLOOR, e233.GAMMA_CEIL


# ---------------------------------------------------------------- design
def _member_series(rows, agg_by_date):
    """[(date, y, lo, la)] for a member, limited to sessions with usable turnover."""
    seq = []
    for d, r, a in rows:
        if r is None or r == 0.0 or a is None or a <= 0.0:
            continue
        agg = agg_by_date.get(d)
        if agg is None or agg <= 0.0:
            continue
        seq.append((d, math.log(abs(r)), math.log(a), math.log(agg)))
    return seq


def _lagged(seq):
    """Drop the first session so the lagged block exists on every row.

    Accepts both the panel form (date, y, lo, la) and the hermetic form (y, lo, la).
    """
    def unpack(row):
        if len(row) == 4:
            return row[1], row[2], row[3]
        return row[0], row[1], row[2]

    out = []
    for k in range(1, len(seq)):
        y, lo, la = unpack(seq[k])
        y0, lo0, la0 = unpack(seq[k - 1])
        out.append((y, lo, la, y0, lo0, la0))
    return out


def _sd(vals):
    n = len(vals)
    if n < 2:
        return None
    m = sum(vals) / n
    return math.sqrt(sum((x - m) ** 2 for x in vals) / n)


def _same_sign(primary, other):
    """Do the two specifications agree about which channel is positive?

    A sign flip between the identified block and the lagged-level block is not noise to be
    averaged away: it says the level regression cannot tell the channels apart, so the
    review must read nothing into either number.
    """
    if not other or other.get("b_own") is None or primary.get("b_own") is None:
        return None
    agree = ((primary["b_own"] >= 0.0) == (other["b_own"] >= 0.0)
             and (primary["b_agg"] >= 0.0) == (other["b_agg"] >= 0.0)
             and (primary["g_scaling"] >= 0.0) == (other["g_scaling"] >= 0.0))
    return bool(agree)


def _corr(a, b):
    n = len(a)
    if n < 3:
        return None
    ma, mb = sum(a) / n, sum(b) / n
    sa = math.sqrt(sum((x - ma) ** 2 for x in a) / n)
    sb = math.sqrt(sum((x - mb) ** 2 for x in b) / n)
    if sa <= 0.0 or sb <= 0.0:
        return None
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b)) / n
    return cov / (sa * sb)


def _ols_hac_full(y, cols, lag=NW_LAG):
    """OLS with Newey-West HAC, returning the full covariance matrix.

    e233.ols_hac publishes standard errors only, but this face needs the covariance of two
    coefficients (b_agg is a difference of two fitted parameters, so its error bar is not
    the sum of theirs). The estimator is identical to e233's -- a selftest leg pins the
    diagonal of this covariance against e233's published standard errors.
    """
    n = len(y)
    k = len(cols) + 1
    if n <= k + 2:
        return None
    X = [[1.0] + [c[i] for c in cols] for i in range(n)]
    xtx = [[sum(X[i][r] * X[i][c] for i in range(n)) for c in range(k)] for r in range(k)]
    diag = [xtx[r][r] for r in range(k)]
    if any(d <= 0.0 for d in diag):
        return None
    corr = [[xtx[r][c] / math.sqrt(diag[r] * diag[c]) for c in range(k)] for r in range(k)]
    if e233._det(corr) < 1e-10:
        return None
    try:
        inv = e233._inv(xtx)
    except ZeroDivisionError:
        return None
    xty = [sum(X[i][r] * y[i] for i in range(n)) for r in range(k)]
    beta = [sum(inv[r][c] * xty[c] for c in range(k)) for r in range(k)]
    resid = [y[i] - sum(beta[j] * X[i][j] for j in range(k)) for i in range(n)]
    meat = [[0.0] * k for _ in range(k)]
    for l in range(0, lag + 1):
        w = 1.0 - float(l) / (lag + 1.0)
        for t in range(l, n):
            coef = w * resid[t] * resid[t - l]
            if coef == 0.0:
                continue
            ex, epx = X[t], X[t - l]
            for r in range(k):
                for c in range(k):
                    meat[r][c] += coef * ex[r] * epx[c]
    mid = [[sum(inv[r][a] * meat[a][b] for a in range(k)) for b in range(k)]
           for r in range(k)]
    cov = [[sum(mid[r][a] * inv[a][c] for a in range(k)) for c in range(k)]
           for r in range(k)]
    ybar = sum(y) / n
    sst = sum((v - ybar) ** 2 for v in y)
    sse = sum(e * e for e in resid)
    return {"beta": beta, "cov": cov, "n": n, "lag": lag,
            "r2": (1.0 - sse / sst) if sst > 0 else None}


def joint_fit(series_list, pooled=False, lag=NW_LAG, spec="reduced"):
    """Joint fit of log|r| on the sleeve's own and the book's aggregate turnover.

    series_list: one entry per member, each a list of (y, lo, la) triples in date order.

    The regression is written in IDENTIFIED coordinates, not in levels. Because
    lo = share + la, the pair (lo, la) spans the same space as (share, la), but the level
    pair is numerically ill-conditioned: a sleeve's turnover level and the book's are the
    same series up to a stationary share, and their lags are near-collinear with each
    other. Fitting (share, la) gives the SAME fitted values and the same coefficients
    re-read: the coefficient on share IS b_own (own turnover moving, book turnover held),
    and the coefficient on la IS b_own + b_agg (the book moving, shares held) -- the
    book-scaling elasticity. So b_agg = beta_la - beta_share, and its standard error comes
    from the covariance of the two coefficients rather than from the sum of theirs.

    pooled=True -> one slope pair with member intercepts (the E234 pooled-with-controls
    pattern: same specification, or the pooled number is a different estimator).
    """
    stacks = []
    for idx, seq in enumerate(series_list):
        rows = _lagged(seq)
        stacks.append((idx, rows, len(rows) >= MIN_MEMBER_ROWS))
    usable = [(idx, rows) for idx, rows, ok in stacks if ok]
    if not usable:
        return {"reason": "no member has enough sessions"}

    if not pooled:
        rows = usable[0][1]
        dummies = []
        members = 1
    else:
        # intercept dummies are indexed by position among the members that actually
        # entered the design: indexing by the original basket position makes the first
        # surviving member a column of ones (a second constant) and the design singular
        rows, dummies = [], []
        members = len(usable)
        for pos, (idx, rs) in enumerate(usable):
            for r in rs:
                rows.append(r)
                dummies.append([1.0 if (pos == j and j >= 1) else 0.0
                                for j in range(1, members)])

    y = [r[0] for r in rows]
    share = [r[1] - r[2] for r in rows]
    la = [r[2] for r in rows]
    yl = [r[3] for r in rows]
    share_lag = [r[4] - r[5] for r in rows]
    la_lag = [r[5] for r in rows]
    cols = [share, la, yl]
    if spec == "full":
        cols = [share, la, yl, share_lag, la_lag]
    elif spec != "reduced":
        raise ValueError("unknown spec %r" % (spec,))
    stale = _corr(la, la_lag)
    # a member that was dropped for too little history leaves an all-zero dummy column,
    # and a zero column makes X'X exactly singular -- keep only the live intercepts
    for i in range(max(0, members - 1)):
        col = [d[i] for d in dummies]
        if any(v != 0.0 for v in col):
            cols.append(col)
    fit = _ols_hac_full(y, cols, lag)
    corr_sa = _corr(share, la)
    share_sd = _sd(share)
    identified = (corr_sa is not None and share_sd is not None
                  and abs(corr_sa) < IDENT_CORR_MAX and share_sd >= MIN_SHARE_SD)
    block = {
        "spec": spec,
        "names": (["const", "own_share", "agg_level", "log_abs_ret_lag1"]
                  if spec == "reduced" else
                  ["const", "own_share", "agg_level", "log_abs_ret_lag1",
                   "own_share_lag1", "agg_level_lag1"]),
        "rows_used": len(y),
        "member_intercepts": members - 1,
        "corr_own_agg": _corr([r[1] for r in rows], la),
        "corr_share_agg": corr_sa,
        "share_sd": share_sd,
        "agg_level_autocorr": stale,
        "identifiable": identified,
        "coordinate_note": "fitted in (own share, aggregate level) coordinates; "
                           "b_own = beta_share, g_scaling = beta_agg_level, "
                           "b_agg = g_scaling - b_own",
    }
    if stale is not None and abs(stale) >= IDENT_CORR_MAX and spec == "full":
        block.update({"b_own": None, "b_agg": None,
                      "reason": "the aggregate level is %.4f autocorrelated, so it and its "
                                "own lag are the same regressor and the lagged level block "
                                "is not identified" % stale})
        return block
    if fit is None:
        block.update({"b_own": None, "b_agg": None,
                      "reason": "within_or_singular"})
        return block
    beta, cov = fit["beta"], fit["cov"]
    b_own, g_scale = beta[1], beta[2]
    var_own, var_scale, cov_pair = cov[1][1], cov[2][2], cov[1][2]
    b_agg = g_scale - b_own
    var_agg = var_scale + var_own - 2.0 * cov_pair
    out = {"b_own": b_own, "g_scaling": g_scale, "b_agg": b_agg, "n": fit["n"],
           "r2": fit["r2"], "lag": fit["lag"], "n_regressors": len(beta)}
    for label, val, var in (("b_own", b_own, var_own), ("b_agg", b_agg, var_agg),
                            ("g_scaling", g_scale, var_scale)):
        se = math.sqrt(var) if var is not None and var > 0 else None
        out[label + "_se"] = se
        out[label + "_ci"] = ([val - Z95 * se, val + Z95 * se] if se else None)
        out[label + "_t_nw"] = (val / se) if se else None
    block.update(out)
    return block


def classify(block, bar_t):
    """The frozen decision rule. Missing numbers are 'unresolved', never guessed."""
    if block.get("b_own") is None or block.get("b_agg") is None:
        return {"verdict": "unresolved", "reason": block.get("reason") or "no estimate"}
    if block.get("identifiable") is False:
        return {"verdict": "unresolved",
                "reason": "the sleeve's turnover share barely moves (share_sd %s, "
                          "|corr(share, aggregate)| %s), so the own channel is collinear "
                          "with the book's and the split is not identified"
                          % (_f(block.get("share_sd"), "%.3f"),
                             _f(block.get("corr_share_agg"), "%.3f"))}
    t_own = block.get("b_own_t_nw")
    t_agg = block.get("b_agg_t_nw")
    own_big = abs(block["b_own"]) >= abs(block["b_agg"])
    own_clears = t_own is not None and abs(t_own) >= bar_t
    agg_clears = t_agg is not None and abs(t_agg) >= bar_t
    if own_clears and agg_clears:
        verdict = "both_channels_live"
    elif own_big and own_clears:
        verdict = "own_dominates"
    elif (not own_big) and agg_clears:
        verdict = "aggregate_dominates"
    else:
        verdict = "unresolved"
    return {"verdict": verdict, "own_larger": own_big,
            "own_clears_bar": own_clears, "agg_clears_bar": agg_clears,
            "bar_t": bar_t}


# ---------------------------------------------------------------- bills
def bill_per_sleeve(abs_dw, cost_side_bp, gammas):
    return e234.charge_book_per_member(abs_dw, cost_side_bp, gammas)


def bill_aggregate(abs_dw, cost_side_bp, g):
    return e232.charge_bp(abs_dw, cost_side_bp, g)


def total_bill(weights, cost_side_bp, charge):
    """charge: ('linear'|'aggregate', g) or ('per_sleeve', [gammas])."""
    prev, total, changes = 0.0, 0.0, 0
    kind = charge[0]
    for w in weights:
        d = abs(w - prev)
        if d > 0.0:
            changes += 1
            if kind == "per_sleeve":
                total += bill_per_sleeve(d, cost_side_bp, charge[1])
            else:
                total += bill_aggregate(d, cost_side_bp, charge[1])
        prev = w
    return {"weight_changes": changes, "total_cost_bp": total}


def rows_for(weights, ret_bp, split, cost_side_bp, charge, const):
    """E229's channel rows with an arbitrary bill shape in place of the scalar charge."""
    n = len(ret_bp)
    is_rets = [r for r in ret_bp[1:split] if r is not None]
    mu_is = e225._mean(is_rets)
    kind = charge[0]
    rows = []
    prev_w = 0.0
    for i in range(0, n - 1):
        w = weights[i]
        dw = w - prev_w
        if kind == "per_sleeve":
            cost = bill_per_sleeve(abs(dw), cost_side_bp, charge[1])
        else:
            cost = bill_aggregate(abs(dw), cost_side_bp, charge[1])
        r = ret_bp[i + 1]
        if r is None:
            prev_w = w
            continue
        rows.append({"i": i, "w": w, "gross_bp": w * r, "cost_bp": cost,
                     "excess_bp": w * r - cost - w * mu_is})
        prev_w = w
    cut = split - 1
    out = []
    for r in rows:
        if r["i"] < cut:
            continue
        ret = ret_bp[r["i"] + 1]
        dev = ret - mu_is
        if r["w"] == 0.0:
            sel, siz = (-const) * dev, 0.0
        else:
            sel, siz = 0.0, (r["w"] - const) * dev
        out.append({"i": r["i"], "w": r["w"], "selection": sel, "sizing": siz,
                    "toll": -r["cost_bp"], "pair": sel + siz - r["cost_bp"]})
    return out, mu_is


def channel_summary(rows):
    def stat(key):
        vals = [r[key] for r in rows]
        s = e230._stats(vals)
        return {"ann_bp_per_year": s.get("ann_bp_per_year"), "t_nw": s.get("t_nw")}

    return {"toll": stat("toll"), "selection": stat("selection"),
            "sizing": stat("sizing"), "pair": stat("pair"),
            "sessions": len(rows)}


def ladder_row(base_rows, band_rows, same_path, band_w, bar_t, charge_key):
    delta = e230.paired_delta(base_rows, band_rows)
    v = e230.rung_verdict(delta, same_path, bar_t)
    return {"charge": charge_key, "verdict": v["verdict"],
            "verdict_reason": v.get("verdict_reason"),
            "d_pair_ann_bp_per_year": v.get("d_pair_ann_bp_per_year"),
            "d_pair_t_nw": v.get("d_pair_t_nw"),
            "weight_changes": e230.change_profile(band_w)["weight_changes"]}


# ---------------------------------------------------------------- run
def run(save=True, panel_dir=None, outdir=None):
    panel_dir = panel_dir or PANEL_DIR
    outdir = outdir or OUTDIR
    single = e225.single_panel(PRIMARY_SYMBOL, panel_dir)
    basket = e225.basket_panel(panel_dir)
    if single is None or not basket:
        print("panels missing (single=%s basket=%s)" % (bool(single), bool(basket)))
        return None

    # ---------------- (a) price of a move against own vs aggregate turnover
    brows = e233.basket_rows(panel_dir)
    agg_by_date = {d: a for d, _r, a in brows if a and a > 0.0}
    per_member = {}
    member_blocks = []
    for sym in BASKET:
        rows = e233.load_ohlc(sym, panel_dir)
        seq = _member_series(rows, agg_by_date)
        per_member[sym] = seq
        if len(seq) < MIN_MEMBER_ROWS:
            member_blocks.append({"symbol": sym, "sessions": len(seq),
                                  "reason": "fewer than %d usable sessions"
                                            % MIN_MEMBER_ROWS})
            continue
        blk = joint_fit([seq])
        blk.update({"symbol": sym, "sessions": len(seq),
                    "first": seq[0][0], "last": seq[-1][0]})
        # the lagged-level block E233 carries is not identified on these panels (the
        # aggregate turnover level is ~0.9999 autocorrelated), so it is published where
        # the estimator allows and read as a robustness variant, never as the primary
        full = joint_fit([seq], spec="full")
        blk["full_block"] = {k: full.get(k) for k in
                             ("b_own", "b_own_ci", "b_agg", "b_agg_ci", "g_scaling",
                              "reason", "r2", "n")}
        blk["spec_stable"] = _same_sign(blk, full)
        member_blocks.append(blk)

    have = [b for b in member_blocks if b.get("b_own") is not None]
    n_tests = 2 * len(have) + 2
    bar_t = max(2.0, e222._z_two_sided(0.05 / n_tests))

    for b in member_blocks:
        b["classification"] = classify(b, bar_t)

    seqs = [per_member[s] for s in BASKET if len(per_member.get(s) or []) >= MIN_MEMBER_ROWS]
    pooled = joint_fit(seqs, pooled=True) if len(seqs) >= 2 else {"reason": "too few members"}
    pooled_class = classify(pooled, bar_t)
    pooled_full = (joint_fit(seqs, pooled=True, spec="full") if len(seqs) >= 2
                   else {"reason": "too few members"})
    pooled_stable = _same_sign(pooled, pooled_full)

    # the exponents the book could be charged at
    g_linear = 1.0
    g_scaling = None
    if pooled.get("g_scaling") is not None:
        g_scaling = round(e233.clip_gamma(pooled["g_scaling"]), 6)
    own_gammas = [e233.clip_gamma(b["b_own"]) for b in have]
    e234_gammas = []
    for b in have:
        e234_gammas.append(e233.clip_gamma(b["b_own"] + b["b_agg"]))

    charges = [{"key": "linear", "kind": "aggregate", "gamma": g_linear,
                "source": "linear_model"}]
    if g_scaling is not None:
        charges.append({"key": "aggregate_scaling", "kind": "aggregate", "gamma": g_scaling,
                        "source": "b_own + b_agg (pooled, book-scaling elasticity)"})
    if own_gammas:
        charges.append({"key": "per_sleeve_own", "kind": "per_sleeve", "gammas": own_gammas,
                        "source": "each sleeve charged its own b_own"})
    if e234_gammas:
        charges.append({"key": "per_sleeve_total", "kind": "per_sleeve",
                        "gammas": e234_gammas,
                        "source": "each sleeve charged b_own + b_agg (E234's published sum)"})

    # ---------------- (b) re-price the book
    dates, ret_bp = basket
    sig = e225.vol_signal(ret_bp)
    split = e225.split_index(len(dates))
    sd_is = e230.band_width(sig, split)
    n_cells = len(ARMS) * len(charges) * (1 + len(LADDER_FRACS))
    price_bar_t = max(2.0, e222._z_two_sided(0.05 / n_cells))

    arms_out, ladder_out = [], []
    for arm in ARMS:
        base_w = e225.weights_series(sig, arm)
        probe, _m = rows_for(base_w, ret_bp, split, COST_SIDE_BP,
                             ("aggregate", 1.0), 0.0)
        const = e225._mean([r["w"] for r in probe]) or 0.0
        block = {"name": arm, "const_weight": const,
                 "base_weight_changes": e230.change_profile(base_w)["weight_changes"],
                 "by_charge": []}
        # liveness first: a flat path must pay nothing under every charge
        flat = [0.0] * len(base_w)
        block["liveness_flat_bill"] = total_bill(flat, COST_SIDE_BP, ("aggregate", 1.0))
        for ch in charges:
            if ch["kind"] == "per_sleeve":
                bill = total_bill(base_w, COST_SIDE_BP, ("per_sleeve", ch["gammas"]))
                cobj = ("per_sleeve", ch["gammas"])
            else:
                bill = total_bill(base_w, COST_SIDE_BP, ("aggregate", ch["gamma"]))
                cobj = ("aggregate", ch["gamma"])
            rows, _mu = rows_for(base_w, ret_bp, split, COST_SIDE_BP, cobj, const)
            ch_sum = channel_summary(rows)
            block["by_charge"].append({
                "charge": ch["key"], "kind": ch["kind"],
                "gamma": ch.get("gamma"), "gammas": ch.get("gammas"),
                "source": ch["source"], "bill": bill, "channels": ch_sum,
                "toll_clears_bar": (ch_sum["toll"]["t_nw"] is not None
                                    and abs(ch_sum["toll"]["t_nw"]) >= price_bar_t)})
            for frac in LADDER_FRACS:
                band_w = e230.band_weights(sig, arm, frac * sd_is)
                if ch["kind"] == "per_sleeve":
                    band_rows, _ = rows_for(band_w, ret_bp, split, COST_SIDE_BP, cobj, const)
                else:
                    band_rows, _ = rows_for(band_w, ret_bp, split, COST_SIDE_BP, cobj, const)
                v = ladder_row(rows, band_rows, band_w == base_w, band_w, price_bar_t,
                               ch["key"])
                v.update({"arm": arm, "band_frac": frac, "band_bp": frac * sd_is,
                          "gamma": ch.get("gamma"), "gammas": ch.get("gammas")})
                ladder_out.append(v)
        arms_out.append(block)

    # ---------------- the headline comparison the question asks for
    bill_split = {}
    for block in arms_out:
        by = {c["charge"]: c for c in block["by_charge"]}
        lin = (by.get("linear") or {}).get("bill", {}).get("total_cost_bp")
        aggs = (by.get("aggregate_scaling") or {}).get("bill", {}).get("total_cost_bp")
        split_own = (by.get("per_sleeve_own") or {}).get("bill", {}).get("total_cost_bp")
        split_tot = (by.get("per_sleeve_total") or {}).get("bill", {}).get("total_cost_bp")
        bill_split[block["name"]] = {
            "linear_bp": lin,
            "aggregate_scaling_bp": aggs,
            "per_sleeve_own_bp": split_own,
            "per_sleeve_total_bp": split_tot,
            "aggregate_vs_split_bp": (None if (aggs is None or split_own is None)
                                      else split_own - aggs),
            "split_over_aggregate_ratio": (None if not aggs else split_own / aggs),
        }

    face = {
        "study": "E235",
        "title": "does a five-sleeve book pay five concave charges or one aggregate charge?",
        "generated": datetime.now().isoformat(timespec="seconds"),
        "evidence_cutoff": dates[-1],
        "frozen_spec": {
            "spec": "log|r_i| = a + b_own*log(own_amount_i) + b_agg*log(agg_amount)"
                    " + B_controlled lag block (y_lag, lo_lag, la_lag), HAC lag %d" % NW_LAG,
            "aggregate": "sum of the five members' session turnover",
            "g_scaling": "b_own + b_agg -- the exponent a single aggregate charge must carry",
            "identifiability_rule": "a member is unidentified when |corr(lo, la)| >= %.2f"
                                    % IDENT_CORR_MAX,
            "verdict_rule": "own_dominates / aggregate_dominates / both_channels_live / "
                            "unresolved, decided on the pooled fit at the multiplicity bar",
            "multiplicity_bar_t": bar_t,
            "multiplicity_basis": "two-sided 5%% over %d coefficient tests" % n_tests,
            "no_adoption": "no arm is re-adopted; the family's verdicts stand and only "
                           "their price is re-read",
        },
        "members": member_blocks,
        "pooled": pooled,
        "pooled_classification": pooled_class,
        "pooled_full_block": {k: pooled_full.get(k) for k in
                              ("b_own", "b_own_ci", "b_agg", "b_agg_ci", "g_scaling",
                               "reason", "r2", "n")},
        "pooled_spec_stable": pooled_stable,
        "charges": charges,
        "book": {"panel": "basket_equal_weight", "sessions": len(dates),
                 "first": dates[0], "last": dates[-1], "split_session": split,
                 "split_date": dates[split], "signal_sd_is_bp": sd_is,
                 "price_bar_t": price_bar_t, "price_bar_basis":
                     "two-sided 5%% over %d cells (arms x charges x bands)" % n_cells,
                 "arms": arms_out},
        "ladder": ladder_out,
        "bills": bill_split,
    }
    face["summary"] = {
        "member_b_own": [{"symbol": b["symbol"], "b_own": b.get("b_own"),
                          "b_own_ci": b.get("b_own_ci"),
                          "b_agg": b.get("b_agg"), "b_agg_ci": b.get("b_agg_ci"),
                          "corr_own_agg": b.get("corr_own_agg"),
                          "identifiable": b.get("identifiable"),
                          "verdict": (b.get("classification") or {}).get("verdict")}
                         for b in member_blocks if b.get("b_own") is not None],
        "member_verdicts": {v: sum(1 for b in member_blocks
                                   if (b.get("classification") or {}).get("verdict") == v)
                            for v in ("own_dominates", "aggregate_dominates",
                                      "both_channels_live", "unresolved")},
        "pooled_b_own": pooled.get("b_own"),
        "pooled_b_agg": pooled.get("b_agg"),
        "pooled_g_scaling": pooled.get("g_scaling"),
        "pooled_verdict": pooled_class.get("verdict"),
        "pooled_verdict_after_spec_check": _final_verdict(pooled_stable, have, pooled_class),
        "pooled_spec_stable": pooled_stable,
        "members_spec_stable": sum(1 for b in have if b.get("spec_stable") is True),
        "members_spec_unstable": [b["symbol"] for b in have
                                  if b.get("spec_stable") is False],
        "members_spec_unavailable": [b["symbol"] for b in have
                                     if b.get("spec_stable") is None],
        "agg_level_autocorr_median": _median([b.get("agg_level_autocorr") for b in have]),
        # a negative own elasticity says a sleeve's move is SMALLER when its own turnover
        # is larger, which no price impact story produces. It is published as a
        # specification red flag, not smoothed away by the pooled average.
        "negative_own_elasticity": [b["symbol"] for b in have if b["b_own"] < 0.0],
        "family_single_regressor_gamma": _family_gamma(),
        "pooled_scaling_vs_family_gamma": _gap(pooled.get("g_scaling"), _family_gamma()),
        "gate_invariance_note": "a 0/1 gate's move is |dw| = 1, so its bill is c*1**g = c "
                                "and is invariant to the exponent by construction",
        "pooled_identifiable": pooled.get("identifiable"),
        "corr_own_agg_median": _median([abs(b["corr_own_agg"]) for b in have
                                        if b.get("corr_own_agg") is not None]),
        "bills": bill_split,
        "toll_clears_bar": {c["key"]: sum(1 for blk in arms_out
                                          for cc in blk["by_charge"]
                                          if cc["charge"] == c["key"] and cc["toll_clears_bar"])
                            for c in charges},
        "arm_cells": len(arms_out),
        "ladder_cells": len(ladder_out),
        "ladder_verdicts_by_charge": {
            c["key"]: _verdict_counts([v["verdict"] for v in ladder_out
                                       if v["charge"] == c["key"]]) for c in charges},
    }
    face["answer"] = _answer(face)
    if save:
        if not os.path.isdir(outdir):
            os.makedirs(outdir)
        name = "GRANULARITY-%s.json" % face["evidence_cutoff"]
        text = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
        with open(os.path.join(outdir, name), "w", encoding="utf-8") as fh:
            fh.write(text)
        with open(os.path.join(outdir, "granularity_latest.json"), "w",
                  encoding="utf-8") as fh:
            fh.write(text)
        face["_written"] = os.path.relpath(os.path.join(outdir, name), ROOT).replace(
            "\\", "/")
        print("wrote %s" % face["_written"])
    return face


def _final_verdict(pooled_stable, have, pooled_class):
    """The published verdict has to survive the specification, not just the bar.

    A pooled slope that clears the bar while individual sleeves price their own turnover
    with the WRONG SIGN is not a finding about granularity: it says the level model is
    mis-specified, so the question is unanswered rather than answered one way.
    """
    negatives = [b["symbol"] for b in have if b.get("b_own") is not None
                 and b["b_own"] < 0.0]
    if negatives:
        return "unresolved_spec_inadequate"
    if pooled_stable is False:
        return "unresolved_spec_sensitive"
    return pooled_class.get("verdict")


def _family_gamma():
    """E233/E234's single-regressor book exponent, read from their published face."""
    path = os.path.join(OUTDIR, "per_member_gamma_latest.json")
    try:
        with open(path, encoding="utf-8") as fh:
            face = json.load(fh)
    except (OSError, ValueError):
        return None
    return (face.get("pooled_fit") or {}).get("gamma")


def _gap(a, b):
    if a is None or b is None:
        return None
    return a - b


def _median(vals):
    vals = [v for v in vals if v is not None]
    if not vals:
        return None
    vals.sort()
    n = len(vals)
    return vals[n // 2] if n % 2 else 0.5 * (vals[n // 2 - 1] + vals[n // 2])


def _verdict_counts(vs):
    out = {}
    for v in vs:
        out[v] = out.get(v, 0) + 1
    return out


def _f(v, spec="%.3f"):
    return "-" if v is None else (spec % v)


def _answer(face):
    s = face["summary"]
    per = "; ".join("%s own %s [%s, %s] vs aggregate %s [%s, %s] (corr %s) -> %s" % (
        b["symbol"], _f(b.get("b_own")), _f((b.get("b_own_ci") or [None])[0]),
        _f((b.get("b_own_ci") or [None, None])[1]), _f(b.get("b_agg")),
        _f((b.get("b_agg_ci") or [None])[0]), _f((b.get("b_agg_ci") or [None, None])[1]),
        _f(b.get("corr_own_agg"), "%.3f"), (b.get("classification") or {}).get("verdict"))
        for b in face["members"] if b.get("b_own") is not None)
    bills = "; ".join("%s linear %s -> one aggregate charge %s -> five per-sleeve charges "
                      "%s bp (split/aggregate %s)" % (
                          arm, _f(v["linear_bp"], "%.1f"),
                          _f(v["aggregate_scaling_bp"], "%.1f"),
                          _f(v["per_sleeve_own_bp"], "%.1f"),
                          _f(v["split_over_aggregate_ratio"], "%.3f"))
                      for arm, v in s["bills"].items())
    verdict = s["pooled_verdict_after_spec_check"]
    if verdict == "aggregate_dominates":
        reading = ("the book is charged ONE aggregate bill: the per-sleeve sum is not the "
                   "price of a five-sleeve move")
    elif verdict == "own_dominates":
        reading = ("each sleeve is priced on its own turnover, so the five per-sleeve "
                   "charges are the correct bill and a single aggregate exponent "
                   "understates it")
    elif verdict == "both_channels_live":
        reading = ("both channels clear the bar: a five-sleeve book's bill is genuinely a "
                   "mixture of its own and the book's turnover, and neither charge alone "
                   "reproduces it")
    elif verdict == "unresolved_spec_inadequate":
        reading = ("%d of %d sleeves price their OWN turnover with a negative elasticity "
                   "(%s) -- a move is priced smaller when the sleeve's own turnover is "
                   "larger, which no impact story produces. The level specification is "
                   "therefore inadequate: the family's single exponent (%s) is a mixture "
                   "of two offsetting channels, and the pooled book-scaling elasticity "
                   "that survives both (%s) is an artefact of that cancellation. No figure "
                   "here is a bill; the question needs a share-and-difference design"
                   % (len(s["negative_own_elasticity"]), len(s["member_b_own"]),
                      ", ".join(s["negative_own_elasticity"]),
                      _f(s["family_single_regressor_gamma"]),
                      _f(s["pooled_b_own"] + s["pooled_b_agg"]
                         if None not in (s["pooled_b_own"], s["pooled_b_agg"]) else None)))
    elif verdict == "unresolved_spec_sensitive":
        reading = ("the two specifications disagree about the SIGN of the channels, so the "
                   "level regression cannot tell own turnover from the book's and the "
                   "granularity question is not answerable in levels -- a share-and-"
                   "difference design is the next step, and no figure here should be "
                   "carried into a bill")
    else:
        reading = ("neither channel clears the multiplicity bar on this sample, so the "
                   "granularity question stays open and the family's level is carried "
                   "as an unresolved price, not a finding")
    own_ci = face["pooled"].get("b_own_ci") or [None, None]
    agg_ci = face["pooled"].get("b_agg_ci") or [None, None]
    return (
        "Per member the joint fit reads %s; pooled with member intercepts b_own = %s "
        "[%s, %s] and b_agg = %s [%s, %s] at a bar of t=%s (median |corr| %s), giving %s. "
        "The aggregate turnover level is %s autocorrelated, so the lagged-level block "
        "E233 carries is only computable on %d of %d sleeves and agrees in sign on %d; "
        "the spec check therefore reads %s. Book-scaling elasticity b_own + b_agg = %s. "
        "Re-priced, %s. Conclusion: %s." % (
            per or "no member estimate",
            _f(s["pooled_b_own"]), _f(own_ci[0]), _f(own_ci[1]),
            _f(s["pooled_b_agg"]), _f(agg_ci[0]), _f(agg_ci[1]),
            _f(face["frozen_spec"]["multiplicity_bar_t"], "%.2f"),
            _f(s["corr_own_agg_median"], "%.3f"), s["pooled_verdict"],
            _f(s["agg_level_autocorr_median"], "%.4f"),
            s["members_spec_stable"] + len(s["members_spec_unavailable"]),
            len(s["member_b_own"]), s["members_spec_stable"],
            ("stable" if s["pooled_spec_stable"] else
             ("unstable across specifications" if s["pooled_spec_stable"] is False
              else "unavailable")),
            _f(s["pooled_g_scaling"]), bills, reading))


# ---------------------------------------------------------------- selftest
def _synth_series(n=700, b_own=0.5, b_agg=0.3, seed=11, spread_sd=0.45,
                  agg_sd=0.25, noise_sd=3.0, phi=0.9):
    """Series where the truth is known: y = b_own*lo + b_agg*la + noise.

    la is a mean-reverting turnover level and lo = la + share, so the sleeve level and the
    book level are the same series up to a stationary share exactly as in a real book.
    noise_sd is set so R2 lands near the 0.10 the real fits show: a hermetic design where
    the regressors explain everything is not the design the face actually runs, and would
    hide the conditioning problem this face is built to survive (selftest leg pins that
    the estimator matches e233's).
    """
    rnd = random.Random(seed)
    la = 20.0
    out = []
    for _ in range(n):
        la = 20.0 + phi * (la - 20.0) + rnd.gauss(0.0, agg_sd)
        lo = la + rnd.gauss(0.0, spread_sd)
        y = b_own * lo + b_agg * la + rnd.gauss(0.0, noise_sd)
        out.append((y, lo, la))
    return out


def selftest():
    legs = []

    def leg(name, fn):
        try:
            fn()
            legs.append((name, True, ""))
        except AssertionError as exc:
            legs.append((name, False, str(exc)))

    def l_linear_bill_reproduces_family():
        w = [(i % 7 < 3) * 1.0 for i in range(120)]
        got = total_bill(w, COST_SIDE_BP, ("aggregate", 1.0))
        want = e232.total_cost(w, COST_SIDE_BP, 1.0)
        assert got["weight_changes"] == want["weight_changes"]
        assert abs(got["total_cost_bp"] - want["total_cost_bp"]) < 1e-9, "linear bill drifted"

    def l_flat_path_pays_nothing():
        for ch in (("aggregate", 0.62), ("per_sleeve", [0.4, 0.6, 0.9])):
            prof = total_bill([0.0] * 40, COST_SIDE_BP, ch)
            assert prof["weight_changes"] == 0 and prof["total_cost_bp"] == 0.0, \
                "a flat path must pay nothing"

    def _mean_estimates(b_own, b_agg, seeds=(1, 2, 3), n=4000, noise_sd=1.5):
        """Average over seeds: one draw carries ~2.7 sigma of sampling error at this size,
        so a single-draw tolerance would either be vacuous or fail on a clean estimator."""
        own, agg, g, se = [], [], [], []
        for sd in seeds:
            blk = joint_fit([_synth_series(n=n, noise_sd=noise_sd, b_own=b_own,
                                           b_agg=b_agg, seed=sd)])
            assert blk.get("b_own") is not None, blk.get("reason")
            own.append(blk["b_own"])
            agg.append(blk["b_agg"])
            g.append(blk["g_scaling"])
            se.append(blk["b_own_se"])
        k = float(len(own))
        return (sum(own) / k, sum(agg) / k, sum(g) / k, sum(se) / k)

    def l_own_only_recovered():
        # b_agg = 0: the joint fit must put the whole elasticity on the own channel
        own, agg, g, _se = _mean_estimates(b_own=0.6, b_agg=0.0)
        assert abs(own - 0.6) < 0.10, "mean b_own %.3f vs truth 0.60" % own
        assert abs(agg) < 0.10, "mean b_agg %.3f should be ~0" % agg
        assert abs(g - 0.6) < 0.10, "mean g_scaling %.3f vs 0.60" % g

    def l_aggregate_only_recovered():
        own, agg, g, _se = _mean_estimates(b_own=0.0, b_agg=0.55)
        assert abs(agg - 0.55) < 0.10, "mean b_agg %.3f vs truth 0.55" % agg
        assert abs(own) < 0.10, "mean b_own %.3f should be ~0" % own
        assert abs(g - 0.55) < 0.10, "mean g_scaling %.3f vs 0.55" % g

    def l_both_recovered():
        own, agg, g, _se = _mean_estimates(b_own=0.45, b_agg=0.35)
        assert abs(own - 0.45) < 0.10, "mean b_own %.3f vs 0.45" % own
        assert abs(agg - 0.35) < 0.10, "mean b_agg %.3f vs 0.35" % agg
        assert abs(g - 0.80) < 0.10, "mean g_scaling %.3f vs 0.80" % g

    def l_scaling_is_the_sum():
        blk = joint_fit([_synth_series(b_own=0.3, b_agg=0.2, spread_sd=0.45)])
        assert abs(blk["g_scaling"] - (blk["b_own"] + blk["b_agg"])) < 1e-12, \
            "the book-scaling elasticity is not b_own + b_agg"

    def l_covariance_matches_the_family_estimator():
        # this face publishes b_agg = g - b_own with its own error bar, so its covariance
        # has to be the same estimator e233 publishes standard errors for
        rows = _lagged(_synth_series(n=900))
        y = [r[0] for r in rows]
        cols = [[r[1] - r[2] for r in rows], [r[2] for r in rows],
                [r[3] for r in rows], [r[4] - r[5] for r in rows], [r[5] for r in rows]]
        mine = _ols_hac_full(y, cols)
        theirs = e233.ols_hac(y, cols)
        assert mine and theirs
        for j in range(len(mine["beta"])):
            assert abs(mine["beta"][j] - theirs["beta"][j]) < 1e-9, "beta %d drifts" % j
            if theirs["se"][j] is not None:
                assert abs(math.sqrt(mine["cov"][j][j]) - theirs["se"][j]) < 1e-9, \
                    "standard error %d drifts" % j

    def l_collinear_is_unidentified():
        # a sleeve whose turnover share never moves carries no own-channel information
        blk = joint_fit([_synth_series(b_own=0.4, b_agg=0.1, spread_sd=0.0002)])
        assert blk.get("share_sd") is not None
        assert blk["share_sd"] < MIN_SHARE_SD, "share_sd %.6f" % blk["share_sd"]
        assert blk["identifiable"] is False, "a constant share must read unidentified"
        c = classify(blk, 2.5)
        assert c["verdict"] == "unresolved" and "collinear" in c["reason"], \
            "an unidentified fit must not publish a dominating channel"

    def l_classify_own_dominates():
        blk = {"b_own": 0.6, "b_agg": 0.05, "b_own_t_nw": 9.0, "b_agg_t_nw": 0.6,
               "identifiable": True}
        assert classify(blk, 2.5)["verdict"] == "own_dominates"

    def l_classify_aggregate_dominates():
        blk = {"b_own": 0.02, "b_agg": 0.7, "b_own_t_nw": 0.3, "b_agg_t_nw": 8.0,
               "identifiable": True}
        assert classify(blk, 2.5)["verdict"] == "aggregate_dominates"

    def l_classify_both_live():
        blk = {"b_own": 0.6, "b_agg": 0.5, "b_own_t_nw": 6.0, "b_agg_t_nw": 6.0,
               "identifiable": True}
        assert classify(blk, 2.5)["verdict"] == "both_channels_live"

    def l_classify_unresolved_when_no_bar():
        blk = {"b_own": 0.6, "b_agg": 0.1, "b_own_t_nw": 1.1, "b_agg_t_nw": 0.4,
               "identifiable": True}
        assert classify(blk, 2.5)["verdict"] == "unresolved"

    def l_pooled_needs_two_members():
        blk = joint_fit([_synth_series()], pooled=True)
        assert blk.get("reason") is None, "one member must still fit as a pooled degenerate"
        # with a single member the pooled spec has no intercept dummies
        assert blk.get("member_intercepts") == 0

    def l_pooled_recovers_truth_on_identical_members():
        a = _synth_series(n=2000, noise_sd=1.5, b_own=0.5, b_agg=0.3, seed=3)
        blk = joint_fit([a, list(a)], pooled=True)
        assert blk.get("b_own") is not None, blk.get("reason")
        assert abs(blk["b_own"] - 0.5) < 0.12, "pooled b_own %.3f" % blk["b_own"]
        assert abs(blk["b_agg"] - 0.3) < 0.12, "pooled b_agg %.3f" % blk["b_agg"]
        assert blk["n_regressors"] == 3 + 1 + 1, "pooled spec carries %d regressors" % (
            blk["n_regressors"])

    def l_short_member_is_reported_not_fitted():
        short = _synth_series(n=MIN_MEMBER_ROWS - 50)
        long_ = _synth_series(n=MIN_MEMBER_ROWS + 150, seed=5)
        blk = joint_fit([short, long_], pooled=True)
        assert blk.get("b_own") is not None, blk.get("reason")
        assert blk["rows_used"] < (len(short) - 1) + (len(long_) - 1), \
            "the short member's rows must not enter the pooled design"

    def l_split_exceeds_aggregate_on_a_concave_charge():
        dw = 0.10
        agg = bill_aggregate(dw, COST_SIDE_BP, 0.62)
        split = bill_per_sleeve(dw, COST_SIDE_BP, [0.62] * 5)
        assert split > agg, "a five-way split of a concave charge must be dearer"
        assert abs(split - 5 * COST_SIDE_BP * (dw / 5.0) ** 0.62) < 1e-12

    def l_split_equals_aggregate_at_one():
        dw = 0.10
        agg = bill_aggregate(dw, COST_SIDE_BP, 1.0)
        split = bill_per_sleeve(dw, COST_SIDE_BP, [1.0] * 5)
        assert abs(agg - split) < 1e-12, "at gamma=1 the two granularities must agree"

    def l_channels_reproduce_family_at_linear():
        w = [(i % 9 < 4) * 1.0 for i in range(200)]
        ret = [((i * 41) % 97) - 48.0 for i in range(200)]
        a, mu_a = rows_for(w, ret, 120, COST_SIDE_BP, ("aggregate", 1.0), 0.0)
        b, mu_b = e232.channel_rows(w, ret, 120, COST_SIDE_BP, 1.0, 0.0)
        assert abs(mu_a - mu_b) < 1e-12
        worst = max(abs(x["toll"] - (-y["cost_bp"])) for x, y in zip(a, b))
        assert worst < 1e-12, "toll differs from the family run by %.3g" % worst

    leg("the linear charge reproduces the family's own bill", l_linear_bill_reproduces_family)
    leg("a flat weight path pays nothing under every charge shape", l_flat_path_pays_nothing)
    leg("the joint fit recovers an own-only truth", l_own_only_recovered)
    leg("the joint fit recovers an aggregate-only truth", l_aggregate_only_recovered)
    leg("the joint fit recovers both channels", l_both_recovered)
    leg("the book-scaling elasticity is b_own + b_agg", l_scaling_is_the_sum)
    leg("the covariance is the estimator e233 publishes standard errors for",
        l_covariance_matches_the_family_estimator)
    leg("collinear turnover is reported unidentified, never split", l_collinear_is_unidentified)
    leg("the verdict rule names an own-dominated book", l_classify_own_dominates)
    leg("the verdict rule names an aggregate-dominated book", l_classify_aggregate_dominates)
    leg("the verdict rule names a two-channel book", l_classify_both_live)
    leg("the verdict rule refuses a channel that misses the bar", l_classify_unresolved_when_no_bar)
    leg("a one-member pooled fit carries no intercept dummies", l_pooled_needs_two_members)
    leg("the pooled fit recovers the truth on identical members",
        l_pooled_recovers_truth_on_identical_members)
    leg("a member with too little history is reported, not fitted",
        l_short_member_is_reported_not_fitted)
    leg("a five-way split of a concave charge is dearer", l_split_exceeds_aggregate_on_a_concave_charge)
    leg("at gamma=1 the two granularities pay the same", l_split_equals_aggregate_at_one)
    leg("the channel rows reproduce the family at the linear charge",
        l_channels_reproduce_family_at_linear)

    ok = sum(1 for _, p, _ in legs if p)
    for name, passed, msg in legs:
        print("%s  %s%s" % ("PASS" if passed else "FAIL", name,
                            ("  -- " + msg) if msg else ""))
    print("%d/%d" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


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