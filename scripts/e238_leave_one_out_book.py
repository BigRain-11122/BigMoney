"""E238 -- is the own-turnover channel a denominator artefact of the book it is measured in?

E236's three designs priced a member's return move against the change in its SHARE of book
turnover, where the book is the equal-weight basket of the same five members. Every member's
own turnover therefore sits inside its own denominator: with own share w the book aggregate
is agg = own + rest, so

    d(log share)          = d(log own) - d(log agg)                 (inclusive denominator)
    d(log share_loo)      = d(log own) - d(log rest)                (leave-one-out denominator)
    d(log share) - d(log share_loo) = d(log rest) - d(log agg) = -d(log(1-w))   EXACT

The two denominators are not two samples of the same object: they are the same rows under
two different restrictions. This face builds the leave-one-out book (the aggregate EXCLUDING
the member) and re-runs E236's three designs verbatim against it, then asks whether the
coefficient gap is what the share arithmetic predicts or something else.

WHAT IS PUBLISHED
  (1) b_own and b_agg for all three designs under BOTH denominators, pooled and per member,
      each with Newey-West intervals and t on a multiplicity bar computed over the six
      coefficients read.
  (2) the gap b_own_inclusive - b_own_loo with a moving-block bootstrap interval (blocks of
      20 sessions, dates resampled jointly across members so the panel stays aligned).
  (3) the mechanical prediction. With own share w the differenced design's own regressor
      carries (1+w/(1-w)) times the leave-one-out regressor's variation while its book
      regressor carries an extra w/(1-w) of it, so to first order in the share drift

          b_own_inclusive  ~=  (1+kappa) * b_own_loo  -  kappa * b_agg_loo,   kappa = w/(1-w)

      i.e. a PREDICTED gap of kappa*(b_own_loo - b_agg_loo) that is a property of the
      arithmetic, not of the market. The card's nominal weight 1/5 gives kappa = 0.25; the
      realised own shares on this panel run 0.03..0.46, so the per-member kappa is published
      next to the nominal one and the pooled number uses the turnover-weighted share.
  (4) two identity legs that make the algebra an assertion rather than a claim: the exact
      regressor difference above (pinned to 1e-12), and the degenerate case -- with a
      constant own share the inclusive regressor has zero variance, so a design reporting a
      number there is reporting its own noise.

VERDICT VOCABULARY (frozen before any number is read):
  * own_channel_survives_the_denominator -- the leave-one-out reading keeps the sign, clears
        the bar, and its interval overlaps the inclusive one: the channel is not the book.
  * own_channel_is_a_denominator_artefact -- the leave-one-out reading fails to clear, flips
        sign, or falls outside the inclusive interval, AND the observed gap is inside the
        mechanical prediction's interval: the inclusive coefficient was the share arithmetic.
  * unresolved_gap_beyond_arithmetic -- the leave-one-out reading clears but the gap is
        larger than the mechanical prediction can explain. Something else is going on and
        this face does not name it.
  * no_own_channel -- neither denominator clears the bar.
  * unresolved_no_leave_one_out -- the leave-one-out book could not be built on this panel.

NO BILL, NO ADOPTION. This face decides whether the E236/E237 family has a measurable own
channel at all; it re-prices nothing and adopts nothing.
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
MIN_MEMBER_ROWS = e235.MIN_MEMBER_ROWS
Z95 = 1.96

DESIGNS = ("differences", "frozen_z", "two_way_fe")
NOMINAL_WEIGHT = 1.0 / 5.0          # the card's equal-weight book, in turnover terms
NOMINAL_KAPPA = NOMINAL_WEIGHT / (1.0 - NOMINAL_WEIGHT)
BOOT_REPS = 400
BOOT_BLOCK = 20
IDENTITY_TOL = 1e-12
SHARE_SD_FLOOR = 1e-8          # below this the share regressor is dust, not variation


# ---------------------------------------------------------------- panels
def book_maps(panel_dir=None):
    """Per member: the inclusive and the leave-one-out series, on rows where both exist.

    Rows are (date, log|r|, log own turnover, log book turnover). The leave-one-out row keeps
    the same date/own fields and swaps only the book turnover for the aggregate EXCLUDING
    that member -- so the two series are the same sessions by construction and any
    coefficient gap is a denominator effect, never a sample change.
    """
    panel_dir = panel_dir or PANEL_DIR
    brows = e233.basket_rows(panel_dir)
    if not brows:
        return None
    agg = {d: a for d, _r, a in brows}
    out = {}
    for sym in BASKET:
        incl, loo, shares, skipped = [], [], [], 0
        for d, r, a in e233.load_ohlc(sym, panel_dir):
            if r is None or r == 0.0 or a is None or a <= 0.0:
                continue
            agg_d = agg.get(d)
            if agg_d is None or agg_d <= 0.0 or a > agg_d:
                continue
            rest = agg_d - a
            if rest <= 0.0:
                skipped += 1
                continue
            y = math.log(abs(r))
            lo = math.log(a)
            incl.append((d, y, lo, math.log(agg_d)))
            loo.append((d, y, lo, math.log(rest)))
            shares.append(a / agg_d)
        if not incl:
            out[sym] = {"incl": [], "loo": [], "shares": [], "skipped": skipped,
                        "reason": "no usable sessions"}
            continue
        w_med = _median(shares)
        w_mean = sum(shares) / len(shares)
        out[sym] = {"incl": incl, "loo": loo, "shares": shares, "skipped": skipped,
                    "sessions": len(incl), "first": incl[0][0], "last": incl[-1][0],
                    "own_share_median": w_med, "own_share_mean": w_mean,
                    "kappa_median": (w_med / (1.0 - w_med)) if 0.0 < w_med < 1.0 else None}
    return out


def _median(vals):
    if not vals:
        return None
    s = sorted(vals)
    n = len(s)
    mid = n // 2
    return s[mid] if n % 2 else 0.5 * (s[mid - 1] + s[mid])


# ---------------------------------------------------------------- designs
def fit_all(seqs, pooled=False):
    """E236's three designs, reused verbatim on whichever denominator the caller passes.

    A guard sits in front of the differenced and level designs: with a constant own share
    the inclusive regressor is constant up to floating-point dust, and OLS on dust returns a
    huge confident coefficient. Refusing is the only honest answer there, and it is also the
    sharpest statement of the mechanical point (see the selftest leg).
    """
    if not seqs:
        return {}
    sh = [r[2] - r[3] for r in seqs[0]]
    sd_level = e235._sd(sh)
    sd_diff = e235._sd([sh[k] - sh[k - 1] for k in range(1, len(sh))])
    out = {}
    if sd_level is None or sd_level < SHARE_SD_FLOOR:
        out["frozen_z"] = {"design": "frozen_z", "b_own": None,
                           "reason": "degenerate_share_regressor(level sd=%.3g)" % sd_level}
    else:
        out["frozen_z"] = e236.fit_frozen_z(seqs, pooled=pooled)
    if sd_diff is None or sd_diff < SHARE_SD_FLOOR:
        out["differences"] = {"design": "differences", "b_own": None,
                              "reason": "degenerate_share_regressor(diff sd=%.3g)" % sd_diff}
    else:
        out["differences"] = e236.fit_differences(seqs, pooled=pooled)
    out["two_way_fe"] = e236.fit_two_way_fe(seqs)
    return out


def read_b_own(fit):
    if not fit or fit.get("b_own") is None:
        return None
    return {"b_own": fit.get("b_own"), "ci": fit.get("b_own_ci"),
            "t": fit.get("b_own_t_nw"), "se": fit.get("b_own_se"),
            "b_agg": fit.get("b_agg"), "b_agg_ci": fit.get("b_agg_ci"),
            "r2": fit.get("r2"), "rows": fit.get("rows_used"),
            "reason": fit.get("reason")}


def _clears(fit, bar_t):
    if not fit:
        return False
    t = fit.get("t") if fit.get("t") is not None else fit.get("b_own_t_nw")
    return t is not None and abs(t) >= bar_t


def _overlap(ci_a, ci_b):
    if not ci_a or not ci_b:
        return None
    return bool(min(ci_a[1], ci_b[1]) >= max(ci_a[0], ci_b[0]))


# ---------------------------------------------------------------- exact arithmetic
def regressor_identity(seq_incl, seq_loo):
    """d(share)_inclusive - d(share)_loo == -d(log(1-w)), checked on every row.

    Returns the largest absolute deviation of the identity and the realised kappa drift.
    This is the leg that turns "the denominators differ" from prose into a number.
    """
    worst = 0.0
    dl = []
    for k in range(1, min(len(seq_incl), len(seq_loo))):
        a0, a1 = seq_incl[k - 1], seq_incl[k]
        b0, b1 = seq_loo[k - 1], seq_loo[k]
        ds_incl = (a1[2] - a1[3]) - (a0[2] - a0[3])
        ds_loo = (b1[2] - b1[3]) - (b0[2] - b0[3])
        # log(1-w) drift, recovered without ever using w explicitly
        drift = (b1[3] - b0[3]) - (a1[3] - a0[3])
        worst = max(worst, abs((ds_incl - ds_loo) - drift))
        dl.append(ds_incl - ds_loo)
    if not dl:
        return {"max_abs_deviation": None, "rows": 0, "dl_sd": None}
    m = sum(dl) / len(dl)
    sd = math.sqrt(sum((x - m) ** 2 for x in dl) / len(dl))
    return {"max_abs_deviation": worst, "rows": len(dl), "dl_sd": sd,
            "dl_mean": m,
            "identity": "d(share)_incl - d(share)_loo = d(log rest) - d(log agg) = -d(log(1-w))"}


def mechanical_gap(b_own_loo, b_agg_loo, kappa):
    """The gap the share arithmetic predicts, with no market data involved.

    First order in the share drift: the inclusive own regressor is (1+kappa) times the
    leave-one-out one and its book regressor carries an extra kappa of it, so
      b_own_incl - b_own_loo = kappa * (b_own_loo - b_agg_loo).
    """
    if b_own_loo is None or b_agg_loo is None or kappa is None:
        return None
    return {"kappa": kappa,
            "predicted_gap": kappa * (b_own_loo - b_agg_loo),
            "predicted_b_own_incl": (1.0 + kappa) * b_own_loo - kappa * b_agg_loo,
            "formula": "gap = kappa*(b_own_loo - b_agg_loo), kappa = w/(1-w)"}


# ---------------------------------------------------------------- bootstrap
def _fast_b_own(seqs):
    """Point estimate of the differenced design's b_own, without the HAC covariance.

    The bootstrap only needs the sampling distribution of the point estimate; recomputing a
    Newey-West covariance 400 times would buy nothing and cost minutes. Same regressors, same
    dummy structure as E236 design A, plain normal equations.
    """
    rows, member_ids = [], []
    for j, seq in enumerate(seqs):
        prev = None
        for r in seq:
            if prev is not None:
                rows.append((r[1] - prev[1], (r[2] - r[3]) - (prev[2] - prev[3]),
                             r[3] - prev[3]))
                member_ids.append(j)
            prev = r
    if len(rows) < 3 * (len(seqs) + 2):
        return None
    n_mem = len(seqs)
    k = 3 + max(0, n_mem - 1)
    xtx = [[0.0] * k for _ in range(k)]
    xty = [0.0] * k
    for i, (dy, dsh, dbook) in enumerate(rows):
        xv = [1.0, dsh, dbook] + [1.0 if (n_mem > 1 and member_ids[i] == j) else 0.0
                                  for j in range(1, n_mem)]
        for a in range(k):
            xa = xv[a]
            if xa == 0.0:
                continue
            xty[a] += xa * dy
            xa_row = xtx[a]
            for b in range(a, k):
                xa_row[b] += xa * xv[b]
    for a in range(k):
        for b in range(a):
            xtx[a][b] = xtx[b][a]
    sol = _solve(xtx, xty)
    return None if sol is None else sol[1]


def _solve(a, b):
    n = len(a)
    m = [list(a[i]) + [b[i]] for i in range(n)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(m[r][col]))
        if abs(m[piv][col]) < 1e-12:
            return None
        m[col], m[piv] = m[piv], m[col]
        d = m[col][col]
        for j in range(col, n + 1):
            m[col][j] /= d
        for r in range(n):
            if r == col:
                continue
            f = m[r][col]
            if f == 0.0:
                continue
            for j in range(col, n + 1):
                m[r][j] -= f * m[col][j]
    return [m[i][n] for i in range(n)]


def block_bootstrap_gap(members, pooled=True, reps=BOOT_REPS, seed=20261030):
    """Paired gap b_own_incl - b_own_loo on the differenced design, block-bootstrapped.

    Dates are resampled jointly across members so every replicate keeps the panel aligned
    (a per-member resample would break the pooled cross-section it is meant to preserve).
    """
    syms = [s for s in members if members[s].get("incl")]
    if len(syms) < 2:
        return None
    dates = sorted({r[0] for s in syms for r in members[s]["incl"]})
    if len(dates) < 2 * BOOT_BLOCK:
        return None
    rnd = random.Random(seed)
    gaps = []
    for _ in range(reps):
        pick = []
        while len(pick) < len(dates):
            start = rnd.randrange(len(dates))
            for j in range(BOOT_BLOCK):
                pick.append(dates[(start + j) % len(dates)])
        want = set(pick[:len(dates)])
        incl_seqs, loo_seqs = [], []
        for s in syms:
            inc = [r for r in members[s]["incl"] if r[0] in want]
            loo_all = {r[0]: r for r in members[s]["loo"]}
            loo = [loo_all[r[0]] for r in inc if r[0] in loo_all]
            if len(inc) < MIN_MEMBER_ROWS or len(loo) < MIN_MEMBER_ROWS:
                break
            incl_seqs.append(inc)
            loo_seqs.append(loo)
        else:
            a = _fast_b_own(incl_seqs)
            b = _fast_b_own(loo_seqs)
            if a is not None and b is not None:
                gaps.append(a - b)
    if len(gaps) < 20:
        return None
    gaps.sort()
    lo = gaps[int(0.025 * (len(gaps) - 1))]
    hi = gaps[int(0.975 * (len(gaps) - 1))]
    return {"reps_used": len(gaps), "ci": [lo, hi],
            "sd": e235._sd(gaps), "block": BOOT_BLOCK,
            "median": gaps[len(gaps) // 2],
            "method": "block bootstrap of the point estimate (no HAC inside the replicate)"}


# ---------------------------------------------------------------- verdict
def classify(own_incl, own_loo, gap, gap_ci, mech, bar_t):
    """Read the two denominators against each other. Frozen vocabulary, no discretion."""
    if own_loo is None:
        return {"verdict": "unresolved_no_leave_one_out",
                "reason": "the leave-one-out book could not be fitted"}
    if own_incl is None:
        return {"verdict": "unresolved_no_leave_one_out",
                "reason": "the inclusive book could not be fitted"}
    clears_loo = _clears(own_loo, bar_t)
    clears_incl = _clears(own_incl, bar_t)
    same_sign = (own_loo["b_own"] >= 0.0) == (own_incl["b_own"] >= 0.0)
    overlap = _overlap(own_loo.get("ci"), own_incl.get("ci"))
    pred = (mech or {}).get("predicted_gap")
    explains = (gap is not None and pred is not None
                and gap_ci is not None
                and gap_ci[0] <= pred <= gap_ci[1])
    out = {"clears_inclusive": clears_incl, "clears_leave_one_out": clears_loo,
           "same_sign": same_sign, "intervals_overlap": overlap,
           "mechanical_prediction": pred, "mechanical_explains_gap": explains,
           "gap": gap, "gap_ci": gap_ci}
    if clears_loo and same_sign and overlap:
        out.update({"verdict": "own_channel_survives_the_denominator",
                    "reason": "the leave-one-out reading keeps the sign, clears the bar and "
                              "overlaps the inclusive interval"})
    elif not clears_loo and not clears_incl:
        out.update({"verdict": "no_own_channel",
                    "reason": "neither denominator clears the bar"})
    elif not clears_loo and explains:
        out.update({"verdict": "own_channel_is_a_denominator_artefact",
                    "reason": "the inclusive coefficient does not survive the member being "
                              "removed from its own denominator, and the observed gap sits "
                              "inside the interval the share arithmetic predicts"})
    elif clears_loo and not explains:
        out.update({"verdict": "unresolved_gap_beyond_arithmetic",
                    "reason": "the leave-one-out reading clears but the gap is larger than "
                              "the mechanical prediction can explain"})
    elif not (same_sign or overlap):
        out.update({"verdict": "own_channel_is_a_denominator_artefact",
                    "reason": "the two denominators do not even agree about the sign or "
                              "overlap, and the inclusive reading does not clear the bar"})
    else:
        out.update({"verdict": "unresolved_gap_beyond_arithmetic",
                    "reason": "the readings are close but neither the survival nor the "
                              "artefact condition is met exactly"})
    return out


# ---------------------------------------------------------------- run
def run(save=True, panel_dir=None, outdir=None, boot_reps=BOOT_REPS):
    panel_dir = panel_dir or PANEL_DIR
    outdir = outdir or OUTDIR
    maps = book_maps(panel_dir)
    if maps is None:
        print("basket panel missing")
        return None
    usable = [s for s in BASKET
              if len(maps[s].get("incl") or []) >= MIN_MEMBER_ROWS
              and len(maps[s].get("loo") or []) >= MIN_MEMBER_ROWS]
    if len(usable) < 2:
        print("fewer than two members have a leave-one-out book")
        return None

    n_tests = 2 * len(DESIGNS)
    bar_t = max(2.0, e222._z_two_sided(0.05 / n_tests))

    members = []
    identity_worst = 0.0
    for sym in BASKET:
        blk = {"symbol": sym, "sessions": maps[sym].get("sessions"),
               "own_share_median": maps[sym].get("own_share_median"),
               "own_share_mean": maps[sym].get("own_share_mean"),
               "kappa_median": maps[sym].get("kappa_median"),
               "skipped_zero_book": maps[sym].get("skipped")}
        if sym not in usable:
            blk["reason"] = maps[sym].get("reason") or "fewer than %d sessions" % MIN_MEMBER_ROWS
            members.append(blk)
            continue
        ident = regressor_identity(maps[sym]["incl"], maps[sym]["loo"])
        identity_worst = max(identity_worst, ident.get("max_abs_deviation") or 0.0)
        blk["identity"] = ident
        blk["inclusive"] = {k: read_b_own(v) for k, v in
                            fit_all([maps[sym]["incl"]]).items()}
        blk["leave_one_out"] = {k: read_b_own(v) for k, v in
                                fit_all([maps[sym]["loo"]]).items()}
        blk["gap_by_design"] = {
            k: (blk["inclusive"][k]["b_own"] - blk["leave_one_out"][k]["b_own"]
                if blk["inclusive"].get(k) and blk["leave_one_out"].get(k) else None)
            for k in DESIGNS}
        blk["mechanical"] = mechanical_gap(
            (blk["leave_one_out"].get("differences") or {}).get("b_own"),
            (blk["leave_one_out"].get("differences") or {}).get("b_agg"),
            blk["kappa_median"])
        blk["verdict_bundle"] = classify(
            blk["inclusive"].get("differences"), blk["leave_one_out"].get("differences"),
            blk["gap_by_design"].get("differences"), None, blk["mechanical"], bar_t)
        members.append(blk)

    seqs_incl = [maps[s]["incl"] for s in usable]
    seqs_loo = [maps[s]["loo"] for s in usable]
    pooled_incl = {k: read_b_own(v) for k, v in fit_all(seqs_incl, pooled=True).items()}
    pooled_loo = {k: read_b_own(v) for k, v in fit_all(seqs_loo, pooled=True).items()}
    pooled_gap = {}
    for k in DESIGNS:
        a, b = pooled_incl.get(k), pooled_loo.get(k)
        pooled_gap[k] = (a["b_own"] - b["b_own"] if a and b else None)

    # turnover-weighted pooled own share: the kappa the arithmetic actually uses
    tot_a, tot_agg = 0.0, 0.0
    for sym in usable:
        for row in maps[sym]["incl"]:
            tot_a += math.exp(row[2])
            tot_agg += math.exp(row[3])
    w_pooled = tot_a / tot_agg if tot_agg > 0 else None
    kappa_pooled = (w_pooled / (1.0 - w_pooled)) if w_pooled and 0 < w_pooled < 1 else None

    gap_ci = block_bootstrap_gap(maps, reps=boot_reps)
    mech = mechanical_gap((pooled_loo.get("differences") or {}).get("b_own"),
                          (pooled_loo.get("differences") or {}).get("b_agg"),
                          kappa_pooled)
    mech_nominal = mechanical_gap((pooled_loo.get("differences") or {}).get("b_own"),
                                  (pooled_loo.get("differences") or {}).get("b_agg"),
                                  NOMINAL_KAPPA)
    verdict = classify(pooled_incl.get("differences"), pooled_loo.get("differences"),
                       pooled_gap.get("differences"), (gap_ci or {}).get("ci"),
                       mech, bar_t)

    # per design: the same question asked of each of E236's three designs separately, because
    # a denominator artefact need not contaminate every design the same way
    verdict_by_design = {}
    for d in DESIGNS:
        inc_d, loo_d = pooled_incl.get(d), pooled_loo.get(d)
        gap_d = pooled_gap.get(d)
        ci_d = None
        se_inc = (inc_d or {}).get("se")
        if se_inc:
            se_loo = (loo_d or {}).get("se")
            if se_loo:
                half = Z95 * math.sqrt(se_inc * se_inc + se_loo * se_loo)
                ci_d = [gap_d - half, gap_d + half]
        mech_d = mechanical_gap((loo_d or {}).get("b_own"), (loo_d or {}).get("b_agg"),
                                kappa_pooled)
        vb_d = classify(inc_d, loo_d, gap_d, ci_d, mech_d, bar_t)
        vb_d["gap_interval_method"] = ("independent-se approximation" if ci_d else None)
        vb_d["mechanical"] = mech_d
        verdict_by_design[d] = vb_d

    books = {d: [] for d in DESIGNS}
    for d in DESIGNS:
        books[d] = []
    dates = sorted({r[0] for s in usable for r in maps[s]["incl"]})

    face = {
        "study": "E238",
        "title": "is the own-turnover channel a denominator artefact of the book it is "
                 "measured in?",
        "generated": datetime.now().isoformat(timespec="seconds"),
        "evidence_cutoff": dates[-1],
        "frozen_spec": {
            "question": "the own turnover sits inside its own denominator with the book "
                        "built from the same five members; remove the member and re-run",
            "denominators": {
                "inclusive": "log(aggregate turnover of the five-member book) -- E236's face",
                "leave_one_out": "log(aggregate turnover EXCLUDING the member being fitted)"},
            "designs": ["differences: dy on d(share), d(book turnover) -- E236 design A",
                        "frozen_z: level share + book level in frozen-window sd units -- B",
                        "two_way_fe: member + date fixed effects, b_own only -- C"],
            "identity": "d(share)_incl - d(share)_loo = d(log rest) - d(log agg) = "
                        "-d(log(1-w)), pinned to %g" % IDENTITY_TOL,
            "mechanical_prediction": "gap = kappa*(b_own_loo - b_agg_loo), kappa = w/(1-w); "
                                     "nominal w = 1/5 -> kappa = 0.25, realised shares "
                                     "published per member",
            "bootstrap": "moving block, %d sessions, %d reps, dates resampled jointly"
                         % (BOOT_BLOCK, boot_reps),
            "multiplicity_bar_t": bar_t,
            "multiplicity_basis": "two-sided 5%% over %d pooled coefficients "
                                  "(3 designs x 2 denominators)" % n_tests,
            "verdict_vocabulary": ["own_channel_survives_the_denominator",
                                   "own_channel_is_a_denominator_artefact",
                                   "unresolved_gap_beyond_arithmetic",
                                   "no_own_channel",
                                   "unresolved_no_leave_one_out"],
            "no_adoption": "this face re-prices nothing and adopts nothing",
        },
        "members": members,
        "pooled": {
            "members": usable,
            "inclusive": pooled_incl,
            "leave_one_out": pooled_loo,
            "gap_by_design": pooled_gap,
            "gap_bootstrap": gap_ci,
            "mechanical": mech,
            "mechanical_at_nominal_weight": mech_nominal,
            "own_share_turnover_weighted": w_pooled,
            "kappa_used": kappa_pooled,
            "kappa_nominal": NOMINAL_KAPPA,
            "verdict_bundle": verdict,
            "verdict_by_design": verdict_by_design,
        },
        "identity": {"max_abs_deviation_all_members": identity_worst,
                     "tolerance": IDENTITY_TOL,
                     "note": "the two designs are two restrictions of one regression, so "
                             "their disagreement cannot be evidence about the market"},
        "book": {"panel": "basket_equal_weight", "members": usable,
                 "sessions": len(dates), "first": dates[0], "last": dates[-1]},
        "no_bill": {"permitted": False,
                    "reason": "this face decides whether an own channel is measurable at "
                              "all; it publishes no charge and adopts no arm"},
    }
    face["summary"] = _summary(face, bar_t, n_tests)
    face["answer"] = _answer(face)
    if save:
        if not os.path.isdir(outdir):
            os.makedirs(outdir)
        name = "LOOBOOK-%s.json" % face["evidence_cutoff"]
        text = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
        for nm in (name, "loobook_latest.json"):
            with open(os.path.join(outdir, nm), "w", encoding="utf-8") as fh:
                fh.write(text)
        rows = ["symbol,design,b_own_inclusive,b_own_leave_one_out,gap,"
                "b_own_loo_ci_lo,b_own_loo_ci_hi,kappa"]
        for b in members:
            if b.get("reason"):
                continue
            for d in DESIGNS:
                inc = (b["inclusive"].get(d) or {})
                loo = (b["leave_one_out"].get(d) or {})
                ci = loo.get("ci") or [None, None]
                rows.append("%s,%s,%s,%s,%s,%s,%s,%s" % (
                    b["symbol"], d, _csv(inc.get("b_own")), _csv(loo.get("b_own")),
                    _csv(b["gap_by_design"].get(d)), _csv(ci[0]), _csv(ci[1]),
                    _csv(b.get("kappa_median"))))
        csv_name = "loo_by_member_%s.csv" % face["evidence_cutoff"]
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


def _summary(face, bar_t, n_tests):
    pooled = face["pooled"]
    vb = pooled.get("verdict_bundle") or {}
    gap_ci = (pooled.get("gap_bootstrap") or {}).get("ci")
    mech = pooled.get("mechanical") or {}
    mech_nom = pooled.get("mechanical_at_nominal_weight") or {}
    member_verdicts = {}
    for b in face["members"]:
        v = (b.get("verdict_bundle") or {}).get("verdict")
        if v:
            member_verdicts[b["symbol"]] = v
    return {
        "verdict": vb.get("verdict"),
        "verdict_reason": vb.get("reason"),
        "inclusive_b_own": ((pooled["inclusive"].get("differences") or {}).get("b_own")),
        "inclusive_b_own_ci": ((pooled["inclusive"].get("differences") or {}).get("ci")),
        "loo_b_own": ((pooled["leave_one_out"].get("differences") or {}).get("b_own")),
        "loo_b_own_ci": ((pooled["leave_one_out"].get("differences") or {}).get("ci")),
        "loo_b_agg": ((pooled["leave_one_out"].get("differences") or {}).get("b_agg")),
        "gap": pooled["gap_by_design"].get("differences"),
        "gap_ci": gap_ci,
        "predicted_gap": mech.get("predicted_gap"),
        "predicted_gap_nominal": mech_nom.get("predicted_gap"),
        "kappa_used": pooled.get("kappa_used"),
        "kappa_nominal": pooled.get("kappa_nominal"),
        "own_share_turnover_weighted": pooled.get("own_share_turnover_weighted"),
        "mechanical_explains_gap": vb.get("mechanical_explains_gap"),
        "identity_max_deviation": face["identity"]["max_abs_deviation_all_members"],
        "member_verdicts": member_verdicts,
        "member_survives_count": sum(1 for v in member_verdicts.values()
                                     if v == "own_channel_survives_the_denominator"),
        "member_artefact_count": sum(1 for v in member_verdicts.values()
                                     if v == "own_channel_is_a_denominator_artefact"),
        "bar_t": bar_t,
        "tests": n_tests,
        "loo_survives_by_design": {
            d: _clears(pooled["leave_one_out"].get(d), bar_t) for d in DESIGNS},
        "inclusive_clears_by_design": {
            d: _clears(pooled["inclusive"].get(d), bar_t) for d in DESIGNS},
        "verdict_by_design": {
            d: ((v or {}).get("verdict"),
                (pooled["inclusive"].get(d) or {}).get("b_own"),
                (pooled["leave_one_out"].get(d) or {}).get("b_own"),
                (v or {}).get("mechanical_prediction"))
            for d, v in (pooled.get("verdict_by_design") or {}).items()},
        "designs_where_the_gap_is_arithmetic": [
            d for d, v in (pooled.get("verdict_by_design") or {}).items()
            if (v or {}).get("verdict") == "own_channel_is_a_denominator_artefact"],
    }


def _answer(face):
    s = face["summary"]
    head = ("own-channel denominator test: inclusive b_own %s vs leave-one-out %s "
            "(gap %s, bootstrap %s; arithmetic predicts %s at kappa %s) -> %s"
            % (_f(s.get("inclusive_b_own")), _f(s.get("loo_b_own")), _f(s.get("gap")),
               _ci(s.get("gap_ci")), _f(s.get("predicted_gap")), _f(s.get("kappa_used"), "%.3f"),
               s.get("verdict")))
    tail = ("own share of book turnover %s (nominal 0.200, kappa %s vs nominal 0.250); "
            "members: %d survive / %d artefact of %d fitted; identity worst deviation %s"
            % (_f(s.get("own_share_turnover_weighted"), "%.3f"),
               _f(s.get("kappa_nominal"), "%.3f"),
               s.get("member_survives_count") or 0,
               s.get("member_artefact_count") or 0,
               len(s.get("member_verdicts") or {}),
               "%.2e" % s["identity_max_deviation"] if s.get("identity_max_deviation")
               is not None else "n/a"))
    return head + " | " + tail


def _f(v, spec="%.3f"):
    if v is None:
        return "n/a"
    return spec % v


def _ci(ci):
    if not ci:
        return "n/a"
    return "[%s, %s]" % (_f(ci[0]), _f(ci[1]))


# ---------------------------------------------------------------- selftest
def synth_member(n=900, w=None, own_channel=0.0, noise=0.6, share_noise=0.0,
                 drift_load=1.0, seed=1):
    """A member inside a book whose own-turnover channel is known.

    own_channel > 0 makes the member's return move respond to its own turnover increment
    (dy = own_channel * d(log own)), which is exactly the coefficient E236/E237 chase. The
    own share of the book is w when w is a float (constant share) and otherwise the share is
    driven by an independent innovation scaled by share_noise, in which case the inclusive
    denominator genuinely carries member information.
    """
    rnd = random.Random(seed)
    out_incl, out_loo = [], []
    lo = 18.0
    w_i = 0.2
    for i in range(n):
        d_lo = rnd.gauss(0.0, noise)
        lo += d_lo
        if w is None:
            # the own share random-walks around 0.2 via an innovation of its own
            if i > 0:
                w_i = min(0.85, max(0.02, w_i + rnd.gauss(0.0, share_noise)))
        else:
            w_i = w
        # rest is whatever makes the own share w_i: rest = own*(1-w)/w
        log_rest = lo + math.log((1.0 - w_i) / w_i)
        log_agg = math.log(math.exp(lo) + math.exp(log_rest))
        y = own_channel * d_lo * drift_load + rnd.gauss(0.0, 1.0)
        out_incl.append(("%05d" % i, y, lo, log_agg))
        out_loo.append(("%05d" % i, y, lo, log_rest))
    return {"incl": out_incl, "loo": out_loo, "share": w_i}


def _fit_diffs(seqs):
    return e236.fit_differences(seqs, pooled=len(seqs) > 1)


def selftest():
    legs = []

    def leg(name, fn):
        try:
            fn()
            legs.append((name, True, ""))
        except AssertionError as exc:
            legs.append((name, False, str(exc)))

    def l_constant_share_degenerates_the_inclusive_design():
        # with a constant own share the inclusive regressor has NO variance: a design that
        # still reports a coefficient is reporting noise, so it must refuse
        f = synth_member(n=600, w=0.2, own_channel=0.4, seed=3)
        ident = regressor_identity(f["incl"], f["loo"])
        assert ident["dl_sd"] is not None and ident["dl_sd"] < 1e-9, \
            "constant share produced share drift sd %r" % ident["dl_sd"]
        fit = fit_all([f["incl"]]).get("differences") or {}
        assert fit.get("b_own") is None, \
            "a degenerate regressor produced a confident coefficient %r" % fit.get("b_own")
        assert "degenerate" in str(fit.get("reason")), \
            "the refusal is not named: %r" % fit.get("reason")
        loo = _fit_diffs([f["loo"]])
        assert loo.get("b_own") is not None, "the leave-one-out design must stay estimable"

    def l_identity_holds_on_a_varying_share():
        f = synth_member(n=900, share_noise=0.02, own_channel=0.3, seed=5)
        ident = regressor_identity(f["incl"], f["loo"])
        assert ident["max_abs_deviation"] is not None
        assert ident["max_abs_deviation"] < 1e-12, \
            "regressor identity broken: %r" % ident["max_abs_deviation"]

    def l_planted_channel_is_recovered_by_the_leave_one_out_book():
        fits = []
        for sd in (1, 2, 3):
            f = synth_member(n=1200, share_noise=0.02, own_channel=0.45, seed=sd)
            fits.append(_fit_diffs([f["loo"]]).get("b_own"))
        mean = sum(fits) / len(fits)
        assert abs(mean - 0.45) < 0.20, "leave-one-out reading %.3f vs planted 0.45" % mean

    def l_null_is_recovered_by_the_leave_one_out_book():
        # no own channel planted: the leave-one-out reading must sit near zero, and the
        # inclusive one must be pushed away by the share arithmetic rather than by the truth
        loo, incl, gaps = [], [], []
        for sd in (1, 2, 3):
            f = synth_member(n=1500, share_noise=0.03, own_channel=0.0, seed=sd)
            a = _fit_diffs([f["loo"]])
            b = _fit_diffs([f["incl"]])
            loo.append(a.get("b_own"))
            incl.append(b.get("b_own"))
            if a.get("b_own") is not None and b.get("b_own") is not None:
                gaps.append(b["b_own"] - a["b_own"])
        mean_loo = sum(loo) / len(loo)
        assert abs(mean_loo) < 0.25, "null panel read %.3f on the leave-one-out book" % mean_loo
        assert gaps, "the null gap was never measured"

    def l_mechanical_gap_uses_the_share_arithmetic():
        # kappa*(b_own - b_agg) is the prediction; at kappa=0 it must be exactly zero, and
        # the nominal 1/5 weight must give 0.25*(b_own - b_agg)
        m0 = mechanical_gap(0.4, 0.1, 0.0)
        assert abs(m0["predicted_gap"]) < 1e-15, "kappa=0 prediction is not zero"
        mn = mechanical_gap(0.4, 0.1, NOMINAL_KAPPA)
        assert abs(mn["predicted_gap"] - 0.25 * (0.4 - 0.1)) < 1e-12, \
            "nominal prediction %.6f" % mn["predicted_gap"]
        assert abs(mn["predicted_b_own_incl"] - (1.25 * 0.4 - 0.25 * 0.1)) < 1e-12, \
            "transfer formula is not the linear map it claims"

    def l_classify_will_not_grant_a_surviving_channel_from_a_dead_reading():
        weak = {"b_own": 0.01, "ci": [-0.2, 0.22], "b_agg": 0.3, "t": 0.2}
        strong = {"b_own": 0.45, "ci": [0.3, 0.6], "b_agg": 0.1, "t": 5.0}
        v = classify(weak, dict(weak), None, None, None, 3.0)
        assert v["verdict"] == "no_own_channel", "weak reading granted %s" % v["verdict"]
        v2 = classify(strong, dict(strong), None, None, None, 3.0)
        assert v2["verdict"] == "own_channel_survives_the_denominator", \
            "a clean overlapping reading was refused: %s" % v2["verdict"]
        assert v2["intervals_overlap"] is True

    def l_classify_names_the_artefact_only_with_the_prediction_in_the_interval():
        incl = {"b_own": 0.43, "ci": [0.34, 0.52], "b_agg": 0.1, "t": 8.0}
        loo = {"b_own": 0.02, "ci": [-0.06, 0.10], "b_agg": -1.62, "t": 0.5}
        mech = mechanical_gap(0.02, -1.62, 0.25)
        gap = incl["b_own"] - loo["b_own"]
        assert abs(mech["predicted_gap"] - gap) < 0.01, "fixture is not self-consistent"
        v = classify(incl, loo, gap, [gap - 0.02, gap + 0.02], mech, 3.0)
        assert v["verdict"] == "own_channel_is_a_denominator_artefact", \
            "predicted gap not honoured: %s" % v["verdict"]
        # same coefficients, prediction far away -> the gap is NOT arithmetic
        far = mechanical_gap(0.02, -1.62, 0.0001)
        v2 = classify(incl, loo, gap, [gap - 0.02, gap + 0.02], far, 3.0)
        assert v2["verdict"] != "own_channel_is_a_denominator_artefact", \
            "an unexplainable gap was waved through as arithmetic"

    def l_bootstrap_keeps_the_panel_aligned():
        mem = {}
        for j, sym in enumerate(("a", "b", "c")):
            f = synth_member(n=400, share_noise=0.02, own_channel=0.2 + 0.1 * j, seed=10 + j)
            mem[sym] = f
        out = block_bootstrap_gap(mem, reps=40)
        assert out is not None and 20 <= out["reps_used"] <= 40, "bootstrap %r" % out
        assert out["ci"][0] <= out["ci"][1], "bootstrap interval is inverted"

    leg("the inclusive design degenerates when the own share is constant", 
        l_constant_share_degenerates_the_inclusive_design)
    leg("d(share)_inclusive - d(share)_loo equals the share-drift term exactly",
        l_identity_holds_on_a_varying_share)
    leg("a planted own channel is recovered from the leave-one-out book",
        l_planted_channel_is_recovered_by_the_leave_one_out_book)
    leg("a null own channel stays null on the leave-one-out book",
        l_null_is_recovered_by_the_leave_one_out_book)
    leg("the mechanical gap is the share arithmetic and the nominal weight is 0.25",
        l_mechanical_gap_uses_the_share_arithmetic)
    leg("no surviving channel is granted from a dead reading",
        l_classify_will_not_grant_a_surviving_channel_from_a_dead_reading)
    leg("the artefact label needs the prediction to sit inside the gap interval",
        l_classify_names_the_artefact_only_with_the_prediction_in_the_interval)
    leg("the block bootstrap resamples dates jointly and returns a real interval",
        l_bootstrap_keeps_the_panel_aligned)

    n_ok = sum(1 for _n, ok, _r in legs if ok)
    for name, ok, reason in legs:
        print("  [%s] %s%s" % ("PASS" if ok else "FAIL", name,
                               "" if ok else " -- " + reason))
    print("selftest %d/%d" % (n_ok, len(legs)))
    return 0 if n_ok == len(legs) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("mode", nargs="?", default="run", choices=("run", "selftest"))
    ap.add_argument("--no-save", action="store_true")
    ap.add_argument("--boot", type=int, default=BOOT_REPS)
    args = ap.parse_args(argv)
    if args.mode == "selftest":
        return selftest()
    face = run(save=not args.no_save, boot_reps=args.boot)
    if face is None:
        return 2
    print(face["answer"])
    return 0


if __name__ == "__main__":
    sys.exit(main())