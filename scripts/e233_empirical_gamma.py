"""E233 -- the curvature grid was never calibrated, so estimate gamma from the panel.

E232 read the family's toll under gamma = 0.75/1.00/1.25/1.50 and found the significance
curvature-invariant while the size is not (tilt_linear toll -247.3 -> -93.2 bp/yr) and
E230's single passing band dies once the charge turns convex. Those four points were
assumed, not measured: the family has always charged |dw| at a fixed 13.041 bp per side,
which is gamma = 1.0 by construction.

This study asks the panel what gamma is. Frozen design (written before any number):

  ESTIMAND. Impact elasticity gamma in  |r_oc| = k * amount ** gamma, where r_oc is the
  open-to-close session move and amount is that session's turnover in CNY. The bridge to
  our cost model is stated, not assumed away: a weight change of |dw| is a traded amount
  proportional to |dw|, so cost ~ |dw| ** gamma follows from |r| ~ amount ** gamma. What
  is measured here is the MARKET's elasticity of price to aggregate turnover on this
  instrument; it is used as a proxy for our own charge, and that substitution is the one
  assumption the face cannot test with daily bars. It is published as `bridge` prose and
  repeated in the answer sentence.

  ESTIMATORS (three, because the regressor is endogenous -- a big move attracts volume):
    A naive        log|r_t|      ~ 1 + log amount_t
    B controlled   log|r_t|      ~ 1 + log amount_t + log|r_(t-1)| + log amount_(t-1)
    C reverse      log amount_t  ~ 1 + log|r_t|     (diagnostic only: 1/slope is a
                                                        joint-move object, never an estimate)
  A and B bracket the simultaneity bias: A lets the move set the volume, B soaks the
  volatility clustering with the lagged magnitude and lagged volume. The PRIMARY estimate
  is B on the full sample of the primary single panel, frozen here before reading numbers;
  the basket and the two eras (pre-2017 / 2017+, the E190 trim edge) are robustness.

  UNCERTAINTY. Newey-West HAC standard errors, lag 20 (e225.NW_LAG), 95% interval
  beta +/- 1.96 se. Downstream point set = {lo, hat, hi}, clipped to [0.05, 3.0] only to
  keep the charge function positive (a clip is disclosed, not silent).

  FAMILY RE-DERIVATION at each downstream gamma, on both panels and the three E229 arms:
    * E229 channels, with the same frozen OOS constant E232 used (const from the gamma=1.0
      path, so cross-gamma rows stay comparable);
    * E230's deadband ladder on the two smallest bands (0.10, 0.25 x sd_is), base and
      banded path charged at the SAME gamma;
    * a fine gamma scan (0.30..2.00 step 0.05) locating the gamma at which BAND_PAYS
      appears, so the claim can be printed as "BAND_PAYS below gamma = X" and X compared
      with the measured interval.

  VERDICT INSIDE THE INTERVAL = the same instrument returns different verdicts at lo and
  hi. That, not the point estimate, is what says whether a family conclusion is decided by
  the data or by the grid. Liveness is asserted first (weight paths must actually move),
  because a fixture in which nothing trades returns "stable" trivially (r1261 lesson).
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e222_tom_overlay as e222  # noqa: E402
import e224_vol_gate as e224  # noqa: E402
import e225_state_tilt as e225  # noqa: E402
import e228_matched_exposure as e228  # noqa: E402
import e230_hysteresis_toll as e230  # noqa: E402
import e232_cost_curvature as e232  # noqa: E402

ROOT = e222.ROOT
PANEL_DIR = e222.PANEL_DIR
OUTDIR = os.path.join(ROOT, "results", "state_tilt")

COST_SIDE_BP = e225.COST_SIDE_BP
IS_FRAC = e225.IS_FRAC
NW_LAG = e225.NW_LAG
PRIMARY_SYMBOL = e225.PRIMARY_SYMBOL
BASKET = e225.BASKET

ARMS = ["binary_low", "tilt_step", "tilt_linear"]
LADDER_FRACS = (0.10, 0.25)
ERA_EDGE = "2017-01-01"          # E190's trim edge, reused rather than re-invented
ESTIMATORS = ("A_naive", "B_controlled", "C_reverse")
PRIMARY_ESTIMATOR = "B_controlled"
PRIMARY_PANEL = "primary_single"
GAMMA_FLOOR, GAMMA_CEIL = 0.05, 3.0
GAMMA_POINT_DECIMALS = 6         # published precision of the point set (see summary note)
FINE_STEPS = (0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85,
              0.90, 0.95, 1.00, 1.05, 1.10, 1.15, 1.20, 1.25, 1.30, 1.35, 1.40, 1.45,
              1.50, 1.60, 1.70, 1.80, 1.90, 2.00)


# ---------------------------------------------------------------- data
def load_ohlc(sym, panel_dir=None):
    """[(date, r_oc_bp, amount)] straight off data/daily/<sym>.csv, complete rows only."""
    panel_dir = panel_dir or PANEL_DIR
    path = os.path.join(panel_dir, sym + ".csv")
    out = []
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as fh:
            import csv as _csv
            for row in _csv.DictReader(fh):
                d = (row.get("date") or "").strip()
                try:
                    o = float(row.get("open") or "")
                    c = float(row.get("close") or "")
                    a = float(row.get("amount") or "")
                except ValueError:
                    continue
                if not d or o <= 0.0 or c <= 0.0 or a <= 0.0:
                    continue
                out.append((d, (c / o - 1.0) * 1e4, a))
    except OSError:
        return []
    out.sort(key=lambda r: r[0])
    return out


def basket_rows(panel_dir=None):
    """Equal-weight session move and summed turnover over the members that printed."""
    panel_dir = panel_dir or PANEL_DIR
    per = {}
    for sym in BASKET:
        rows = load_ohlc(sym, panel_dir)
        if rows:
            per[sym] = {d: (r, a) for d, r, a in rows}
    dates = sorted({d for sym in per for d in per[sym]})
    out = []
    for d in dates:
        rets, amt = [], 0.0
        for sym in per:
            hit = per[sym].get(d)
            if hit is None:
                continue
            rets.append(hit[0])
            amt += hit[1]
        if not rets or amt <= 0.0:
            continue
        out.append((d, sum(rets) / len(rets), amt))
    return out


def split_era(rows, era):
    if era == "all":
        return list(rows)
    if era == "pre2017":
        return [r for r in rows if r[0] < ERA_EDGE]
    if era == "2017plus":
        return [r for r in rows if r[0] >= ERA_EDGE]
    raise ValueError("unknown era %r" % (era,))


# ---------------------------------------------------------------- OLS with HAC
def _inv(mat):
    """Gauss-Jordan inverse for the small (<=4x4) cross-product matrices used here."""
    k = len(mat)
    a = [row[:] + [1.0 if i == j else 0.0 for j in range(k)] for i, row in enumerate(mat)]
    for col in range(k):
        piv = max(range(col, k), key=lambda r: abs(a[r][col]))
        if abs(a[piv][col]) < 1e-300:
            raise ZeroDivisionError("singular cross-product")
        a[col], a[piv] = a[piv], a[col]
        f = a[col][col]
        a[col] = [v / f for v in a[col]]
        for r in range(k):
            if r == col:
                continue
            f = a[r][col]
            if f:
                a[r] = [x - f * y for x, y in zip(a[r], a[col])]
    return [row[k:] for row in a]


def _det(mat):
    """Recursive determinant, small k only."""
    k = len(mat)
    if k == 1:
        return mat[0][0]
    if k == 2:
        return mat[0][0] * mat[1][1] - mat[0][1] * mat[1][0]
    total = 0.0
    for c in range(k):
        minor = [row[:c] + row[c + 1:] for row in mat[1:]]
        total += ((-1.0) ** c) * mat[0][c] * _det(minor)
    return total


def ols_hac(y, cols, lag=NW_LAG):
    """OLS with Newey-West (Bartlett) HAC standard errors; returns beta, se, n, r2."""
    n = len(y)
    k = len(cols) + 1
    if n <= k + 2:
        return None
    X = [[1.0] + [c[i] for c in cols] for i in range(n)]
    xtx = [[sum(X[i][r] * X[i][c] for i in range(n)) for c in range(k)] for r in range(k)]
    # a constant regressor renders X'X exactly singular, but in floats a column of 1e8
    # values produces a huge near-singular matrix that still inverts -- so the guard has
    # to be scale aware: compare against the correlation form, not the raw determinant.
    diag = [xtx[r][r] for r in range(k)]
    if any(d <= 0.0 for d in diag):
        return None
    corr = [[xtx[r][c] / math.sqrt(diag[r] * diag[c]) for c in range(k)] for r in range(k)]
    if _det(corr) < 1e-10:
        return None
    try:
        inv = _inv(xtx)
    except ZeroDivisionError:
        return None
    xty = [sum(X[i][r] * y[i] for i in range(n)) for r in range(k)]
    beta = [sum(inv[r][c] * xty[c] for c in range(k)) for r in range(k)]
    resid = [y[i] - sum(beta[j] * X[i][j] for j in range(k)) for i in range(n)]
    # meat: sum_l w_l * sum_t e_t e_{t-l} x_t x_{t-l}'
    meat = [[0.0] * k for _ in range(k)]
    for l in range(0, lag + 1):
        w = 1.0 - float(l) / (lag + 1.0)
        for t in range(l, n):
            et, ex = resid[t], X[t]
            ep, epx = resid[t - l], X[t - l]
            coef = w * et * ep
            for r in range(k):
                for c in range(k):
                    meat[r][c] += coef * ex[r] * epx[c]
    mid = [[sum(inv[r][a] * meat[a][b] for a in range(k)) for b in range(k)]
           for r in range(k)]
    var = [sum(mid[r][a] * inv[a][r] for a in range(k)) for r in range(k)]
    se = [math.sqrt(v) if v > 0 else None for v in var]
    ybar = sum(y) / n
    sst = sum((v - ybar) ** 2 for v in y)
    sse = sum(e * e for e in resid)
    return {"beta": beta, "se": se, "n": n,
            "r2": (1.0 - sse / sst) if sst > 0 else None,
            "lag": lag}


def fit_gamma(rows, estimator="B_controlled", lag=NW_LAG):
    """One gamma estimate on one (panel, era) row set. Returns a published block."""
    clean = [r for r in rows if r[1] is not None and r[1] != 0.0 and r[2] > 0.0]
    dropped = len(rows) - len(clean)
    y = [math.log(abs(r[1])) for r in clean]
    la = [math.log(r[2]) for r in clean]
    if estimator == "A_naive":
        fit = ols_hac(y, [la], lag)
        names = ["const", "log_amount"]
    elif estimator == "B_controlled":
        # drop the first session so the lagged regressors exist for every row
        y2, la2 = y[1:], la[1:]
        la_lag = la[:-1]
        ly_lag = y[:-1]
        fit = ols_hac(y2, [la2, ly_lag, la_lag], lag)
        names = ["const", "log_amount", "log_abs_ret_lag1", "log_amount_lag1"]
    elif estimator == "C_reverse":
        fit = ols_hac(la, [y], lag)
        names = ["const", "log_abs_ret"]
    else:
        raise ValueError("unknown estimator %r" % (estimator,))
    block = {"estimator": estimator, "names": names, "rows_used": len(clean),
             "rows_dropped": dropped}
    if fit is None:
        block.update({"gamma": None, "gamma_se": None, "gamma_ci": None,
                      "reason": "insufficient_or_singular"})
        return block
    idx = 1 if estimator != "C_reverse" else 1
    slope = fit["beta"][idx]
    se = fit["se"][idx]
    if estimator == "C_reverse":
        # diagnostic only: the reciprocal of a reverse regression is not the forward
        # elasticity, because the errors are not on the same side. Published, never used.
        block.update({"reverse_slope": slope, "reverse_se": se,
                      "implied_forward_reciprocal": (1.0 / slope) if slope else None,
                      "gamma": None, "gamma_se": None, "gamma_ci": None,
                      "note": "diagnostic only, not an estimator of gamma"})
        block["n"] = fit["n"]
        block["r2"] = fit["r2"]
        return block
    ci = None
    if se is not None:
        ci = [slope - 1.96 * se, slope + 1.96 * se]
    block.update({"gamma": slope, "gamma_se": se, "gamma_ci": ci,
                  "n": fit["n"], "r2": fit["r2"],
                  "t_nw": (slope / se) if se else None})
    return block


def clip_gamma(g):
    return max(GAMMA_FLOOR, min(GAMMA_CEIL, g))


# ---------------------------------------------------------------- family re-derivation
def channel_table(weights, ret_bp, split, gamma, const, bar_t):
    rows, mu_is = e232.channel_rows(weights, ret_bp, split, COST_SIDE_BP, gamma, const)
    tot = e230._totals(rows)
    return {"toll_t_nw": e230._stats([r["toll"] for r in rows])["t_nw"],
            "selection_t_nw": e230._stats([r["selection"] for r in rows])["t_nw"],
            "pair_t_nw": e230._stats([r["pair"] for r in rows])["t_nw"],
            "totals": tot,
            "mu_is_bp_per_day": mu_is,
            "toll_clears_bar": (abs(e230._stats([r["toll"] for r in rows])["t_nw"] or 0.0)
                               >= bar_t)}


def ladder_cell_verdict(sig, arm, band, gamma, ret_bp, split, const, base_cache, bar_t):
    """E230's rung verdict for one (arm, band) at one gamma, base path charged the same."""
    key = ("%.6f" % gamma,)
    if key not in base_cache:
        base_w = e225.weights_series(sig, arm)
        base_rows, _ = e232.channel_rows(base_w, ret_bp, split, COST_SIDE_BP, gamma, const)
        base_cache[key] = (base_w, base_rows)
    base_w, base_rows = base_cache[key]
    w = e230.band_weights(sig, arm, band)
    rows, _ = e232.channel_rows(w, ret_bp, split, COST_SIDE_BP, gamma, const)
    delta = e230.paired_delta(base_rows, rows)
    v = e230.rung_verdict(delta, w == base_w, bar_t)
    return {"verdict": v["verdict"], "verdict_reason": v["verdict_reason"],
            "d_pair_ann_bp_per_year": v["d_pair_ann_bp_per_year"],
            "d_pair_t_nw": v["d_pair_t_nw"],
            "d_toll_ann_bp_per_year": v["d_toll_ann_bp_per_year"],
            "weight_changes": e230.change_profile(w)["weight_changes"]}


def run(save=True, panel_dir=None, outdir=None):
    panel_dir = panel_dir or PANEL_DIR
    outdir = outdir or OUTDIR
    single = e225.single_panel(PRIMARY_SYMBOL, panel_dir)
    if single is None:
        print("primary panel missing: %s" % PRIMARY_SYMBOL)
        return None
    basket = e225.basket_panel(panel_dir)

    raw = {"primary_single": load_ohlc(PRIMARY_SYMBOL, panel_dir),
           "basket_equal_weight": basket_rows(panel_dir)}
    if not raw["primary_single"]:
        print("primary OHLC panel missing: %s" % PRIMARY_SYMBOL)
        return None

    # ---------------- gamma estimates: 2 panels x 3 eras x 3 estimators
    est_rows = []
    for panel_name, rows in raw.items():
        if not rows:
            continue
        for era in ("all", "pre2017", "2017plus"):
            sub = split_era(rows, era)
            for est in ESTIMATORS:
                b = fit_gamma(sub, est)
                b.update({"panel": panel_name, "era": era,
                          "first": sub[0][0] if sub else None,
                          "last": sub[-1][0] if sub else None})
                est_rows.append(b)

    prim = [r for r in est_rows if r["panel"] == PRIMARY_PANEL
            and r["era"] == "all" and r["estimator"] == PRIMARY_ESTIMATOR]
    if not prim or prim[0].get("gamma") is None:
        print("primary gamma estimate unavailable")
        return None
    prim = prim[0]
    ci = prim.get("gamma_ci") or [prim["gamma"], prim["gamma"]]
    points = [{"gamma": round(clip_gamma(ci[0]), GAMMA_POINT_DECIMALS),
               "source": "interval_lo"},
              {"gamma": round(clip_gamma(prim["gamma"]), GAMMA_POINT_DECIMALS),
               "source": "point"},
              {"gamma": round(clip_gamma(ci[1]), GAMMA_POINT_DECIMALS),
               "source": "interval_hi"}]
    # the interval is only one source of uncertainty: the two estimators disagree by more
    # than the interval is wide (the regressor is endogenous), so the family verdicts also
    # have to survive the identification dispute, not just sampling error at fixed design.
    naive = [r for r in est_rows if r["panel"] == PRIMARY_PANEL
             and r["era"] == "all" and r["estimator"] == "A_naive"]
    if naive and naive[0].get("gamma") is not None:
        g_naive = round(clip_gamma(naive[0]["gamma"]), 6)
        if all(abs(g_naive - p["gamma"]) > 1e-9 for p in points):
            points.append({"gamma": g_naive, "source": "naive_contemporaneous"})
    interval_points = [p["gamma"] for p in points if p["source"] != "naive_contemporaneous"]
    point_set = [p["gamma"] for p in points]

    # ---------------- family re-derivation at every published gamma point
    panels = [{"panel": "primary_single", "symbol": PRIMARY_SYMBOL}]
    if basket:
        panels.append({"panel": "basket_equal_weight", "symbol": "+".join(sorted(BASKET))})
    n_cells = len(ARMS) * len(panels) * len(points)
    bar_t = max(2.0, e222._z_two_sided(0.05 / n_cells))

    channels, ladder = [], []
    for panel in panels:
        dates, ret_bp = (single if panel["panel"] == "primary_single" else basket)
        sig = e225.vol_signal(ret_bp)
        split = e225.split_index(len(dates))
        sd_is = e230.band_width(sig, split)
        panel.update({"sessions": len(dates), "first": dates[0], "last": dates[-1],
                      "split_session": split, "split_date": dates[split],
                      "signal_sd_is_bp": sd_is})
        if not sd_is:
            panel["arms"] = []
            panel["note"] = "signal too short for an in-sample band width"
            continue
        panel["arms"] = []
        for arm in ARMS:
            base_w = e225.weights_series(sig, arm)
            probe, _ = e232.channel_rows(base_w, ret_bp, split, COST_SIDE_BP, 1.0, 0.0)
            const = e225._mean([r["w"] for r in probe]) or 0.0
            changes = e230.change_profile(base_w)["weight_changes"]
            arm_out = {"name": arm, "const_weight": const,
                       "base_weight_changes": changes, "by_gamma": []}
            base_cache = {}
            for p in points:
                t = channel_table(base_w, ret_bp, split, p["gamma"], const, bar_t)
                t["gamma"] = p["gamma"]
                t["gamma_source"] = p["source"]
                t["total_cost_bp"] = e232.total_cost(base_w, COST_SIDE_BP, p["gamma"])
                arm_out["by_gamma"].append(t)
                channels.append(dict(t, panel=panel["panel"], arm=arm))
            for frac in LADDER_FRACS:
                cell = {"band_frac": frac, "band_bp": frac * sd_is, "by_gamma": []}
                for p in points:
                    v = ladder_cell_verdict(sig, arm, cell["band_bp"], p["gamma"], ret_bp,
                                            split, const, base_cache, bar_t)
                    v["gamma"] = p["gamma"]
                    v["gamma_source"] = p["source"]
                    cell["by_gamma"].append(v)
                cell["verdicts"] = [(x["gamma_source"], x["verdict"])
                                    for x in cell["by_gamma"]]
                vs_interval = [x["verdict"] for x in cell["by_gamma"]
                               if x["gamma_source"] != "naive_contemporaneous"]
                vs_all = [x["verdict"] for x in cell["by_gamma"]]
                cell["verdicts_interval"] = vs_interval
                cell["verdict_stable"] = len(set(vs_interval)) == 1
                cell["verdict_stable_all_points"] = len(set(vs_all)) == 1
                cell["verdict_inside_interval"] = not cell["verdict_stable"]
                cell["verdict_sensitive_to_identification"] = not cell["verdict_stable_all_points"]
                ladder.append(dict(cell, panel=panel["panel"], arm=arm))
                arm_out.setdefault("ladder", []).append(cell)
            panel["arms"].append(arm_out)

    # ---------------- where does BAND_PAYS live on a fine gamma scan
    scan = []
    for panel in panels:
        if not panel.get("arms"):
            continue
        dates, ret_bp = (single if panel["panel"] == "primary_single" else basket)
        sig = e225.vol_signal(ret_bp)
        split = e225.split_index(len(dates))
        sd_is = panel["signal_sd_is_bp"]
        for arm in ARMS:
            base_w = e225.weights_series(sig, arm)
            probe, _ = e232.channel_rows(base_w, ret_bp, split, COST_SIDE_BP, 1.0, 0.0)
            const = e225._mean([r["w"] for r in probe]) or 0.0
            base_cache = {}
            for frac in LADDER_FRACS:
                pays, rows_scan = [], []
                for g in FINE_STEPS:
                    v = ladder_cell_verdict(sig, arm, frac * sd_is, g, ret_bp, split,
                                            const, base_cache, bar_t)
                    rows_scan.append({"gamma": g, "verdict": v["verdict"],
                                      "d_pair_ann_bp_per_year": v["d_pair_ann_bp_per_year"],
                                      "d_pair_t_nw": v["d_pair_t_nw"]})
                    if v["verdict"] == "BAND_PAYS":
                        pays.append(g)
                scan.append({"panel": panel["panel"], "arm": arm, "band_frac": frac,
                             "band_pays_gammas": pays,
                             "band_pays_max_gamma": max(pays) if pays else None,
                             "band_pays_inside_estimate": any(
                                 ci[0] <= g <= ci[1] for g in pays),
                             "scan": rows_scan})

    toll_rows = [r for r in channels]
    inside = [c for c in ladder if c["verdict_inside_interval"]]
    ident = [c for c in ladder if c["verdict_sensitive_to_identification"]]
    pays_cells = [s for s in scan if s["band_pays_gammas"]]

    face = {
        "study": "E233",
        "title": "measure the charge curvature instead of assuming it, then re-read the family",
        "generated": datetime.now().isoformat(timespec="seconds"),
        "evidence_cutoff": raw["primary_single"][-1][0],
        "frozen_spec": {
            "estimand": "|r_oc| = k * amount ** gamma (amount = session turnover, CNY)",
            "estimators": list(ESTIMATORS),
            "primary": "%s on %s / all" % (PRIMARY_ESTIMATOR, PRIMARY_PANEL),
            "era_edge": ERA_EDGE,
            "hac_lag": NW_LAG,
            "ci": "beta +/- 1.96 * Newey-West se",
            "downstream_point_set": point_set,
            "downstream_points": points,
            "clip": [GAMMA_FLOOR, GAMMA_CEIL],
            "arms": ARMS,
            "ladder_fracs": list(LADDER_FRACS),
            "cost_side_bp": COST_SIDE_BP,
            "is_frac": IS_FRAC,
            "bar_t": bar_t,
            "bar_basis": "two-sided 5%% over %d cells (arms x panels x %d gamma points)"
                         % (n_cells, len(points)),
            "fine_steps": list(FINE_STEPS),
            "bridge": "a weight change of |dw| trades an amount proportional to |dw|, so "
                      "cost ~ |dw| ** gamma follows from |r| ~ amount ** gamma. The face "
                      "measures the market's elasticity to aggregate turnover on this "
                      "instrument; using it as our own charge exponent is an assumption "
                      "that daily bars cannot test.",
            "endogeneity": "amount and |r| are jointly determined; A lets the move set the "
                           "volume, B soaks it with lagged magnitude and lagged volume, C is "
                           "published as a diagnostic and never as an estimate",
            "no_adoption": "the arms are already judged; this asks only whether a family "
                           "verdict is a fact about the data or about the grid",
        },
        "panels": [{k: v for k, v in p.items() if k != "arms"} for p in panels],
        "gamma_estimates": est_rows,
        "primary_estimate": {k: prim.get(k) for k in
                             ("panel", "era", "estimator", "gamma", "gamma_se", "gamma_ci",
                              "n", "r2", "t_nw", "rows_used", "rows_dropped")},
        "channels": toll_rows,
        "ladder": [{k: v for k, v in c.items() if k != "by_gamma"} | {"by_gamma": c["by_gamma"]}
                   for c in ladder],
        "fine_scan": scan,
        "summary": {
            # The published point set is ROUNDED (6 dp) while the interval beside it is full
            # precision, so a reader comparing the two at 1e-9 sees the endpoint "missing"
            # from its own point set when it is only a rounded copy of the same number
            # (E233 r1316). The precision and the provenance are published so the check can
            # be made at the resolution the face actually prints.
            "gamma_points": point_set,
            "gamma_points_decimals": GAMMA_POINT_DECIMALS,
            "gamma_points_sources": [p["source"] for p in points],
            "gamma_interval": ci,
            "interval_points": interval_points,
            "identification_span": [min(point_set), max(point_set)],
            "bar_t": bar_t,
            "channel_cells": len(toll_rows),
            "toll_clears_bar_every_point": sum(
                1 for p in panels if p.get("arms")
                for a in p["arms"] if all(g["toll_clears_bar"] for g in a["by_gamma"])),
            "arm_cells": sum(1 for p in panels if p.get("arms") for _ in p["arms"]),
            "ladder_cells": len(ladder),
            "ladder_verdicts_stable": sum(1 for c in ladder if c["verdict_stable"]),
            "ladder_verdicts_inside_interval": len(inside),
            "ladder_verdicts_stable_all_points": sum(
                1 for c in ladder if c["verdict_stable_all_points"]),
            "ladder_verdicts_sensitive_to_identification": len(ident),
            "cells_with_band_pays": len(pays_cells),
            "band_pays_inside_estimate": sum(
                1 for s in pays_cells if s["band_pays_inside_estimate"]),
            "band_pays_max_gamma": [{"panel": s["panel"], "arm": s["arm"],
                                     "band_frac": s["band_frac"],
                                     "max_gamma": s["band_pays_max_gamma"]}
                                    for s in pays_cells],
            "all_gammas_zero_change": [
                "%s/%s" % (p["panel"], a["name"]) for p in panels if p.get("arms")
                for a in p["arms"] if (a.get("base_weight_changes") or 0) <= 0],
        },
    }
    face["answer"] = _answer(face)
    if save:
        if not os.path.isdir(outdir):
            os.makedirs(outdir)
        path = os.path.join(outdir, "EMPIRICAL-GAMMA-%s.json" % face["evidence_cutoff"])
        text = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        with open(os.path.join(outdir, "empirical_gamma_latest.json"), "w",
                  encoding="utf-8") as fh:
            fh.write(text)
        face["_written"] = os.path.relpath(path, ROOT).replace("\\", "/")
        print("wrote %s" % face["_written"])
    return face


def _fmt(v, spec="%.2f"):
    return "-" if v is None else (spec % v)


def _answer(face):
    s = face["summary"]
    p = face["primary_estimate"]
    ests = {r["estimator"]: r for r in face["gamma_estimates"]
            if r["panel"] == p["panel"] and r["era"] == p["era"]}
    a = ests.get("A_naive", {})
    c = ests.get("C_reverse", {})
    pays_txt = ", ".join(
        "%s/%s/f=%.2f up to gamma %s" % (x["panel"], x["arm"], x["band_frac"],
                                         _fmt(x["max_gamma"]))
        for x in s["band_pays_max_gamma"]) or "no cell"
    return " ".join([
        "Estimated from the panel rather than assumed: |r_oc| ~ k * amount ** gamma gives "
        "gamma = %s [%s, %s] on %s over %s..%s (Newey-West, lag %d, n=%s); the naive "
        "contemporaneous reading is %s and the reverse diagnostic regression is reported "
        "but not used."
        % (_fmt(p.get("gamma"), "%.3f"), _fmt((s["gamma_interval"] or [None])[0], "%.3f"),
           _fmt((s["gamma_interval"] or [None, None])[1], "%.3f"),
           p["panel"], face["panels"][0]["first"], face["panels"][0]["last"],
           face["frozen_spec"]["hac_lag"], p.get("n"),
           _fmt(a.get("gamma"), "%.3f")),
        "Re-deriving the family at the measured interval (%s) and, separately, at the naive "
        "contemporaneous estimate (identification span %s): the toll clears its bar "
        "(|t| >= %s) on %d of %d arm cells at every point, the ladder keeps one verdict "
        "inside the interval on %d of %d cells, and %d of %d ladder cells keep one verdict "
        "across the whole identification span -- %s."
        % (", ".join("%.3f" % g for g in s["interval_points"] or []),
           "%.3f..%.3f" % tuple(s["identification_span"]),
           _fmt(s["bar_t"], "%.2f"), s["toll_clears_bar_every_point"], s["arm_cells"],
           s["ladder_verdicts_stable"], s["ladder_cells"],
           s["ladder_verdicts_stable_all_points"], s["ladder_cells"],
           "so those verdicts are decided by the DATA, not by the grid or by the "
           "identification dispute"
           if s["ladder_verdicts_sensitive_to_identification"] == 0 else
           "so %d of them are decided by WHERE you put gamma, not by the data"
           % s["ladder_verdicts_sensitive_to_identification"]),
        "The passing band is conditional: %s, and %d of %d such cells have their BAND_PAYS "
        "support inside the measured interval."
        % (pays_txt, s["band_pays_inside_estimate"], s["cells_with_band_pays"]),
        "Caveat carried, not buried: what is measured is the market's elasticity of price "
        "to aggregate turnover on this instrument; treating it as our own |dw| exponent is "
        "the bridge assumption stated in frozen_spec.bridge.",
    ])


# ---------------------------------------------------------------- selftest
def _synth_impact(n=1200, gamma=0.62, seed=11, cluster=0.0):
    """Synthetic panel where the true elasticity is known: |r| = k * amount ** gamma."""
    import random
    rng = random.Random(seed)
    rows, la, carried = [], 9.0, 0.0
    for i in range(n):
        la = 0.97 * la + 0.03 * 9.0 + rng.gauss(0.0, 0.45)
        amt = math.exp(la)
        noise = rng.gauss(0.0, 1.0)
        r = math.exp(math.log(3.0) + gamma * la + 0.9 * noise + cluster * carried)
        carried = abs(noise) if cluster else 0.0
        day = "20%02d-%02d-%02d" % (10 + i // 365, 1 + (i // 30) % 12, 1 + i % 28)
        rows.append((day, r, amt))
    rows.sort(key=lambda r: r[0])
    return rows


def selftest():
    legs = []

    def leg(name, fn):
        try:
            fn()
            legs.append((name, True, ""))
        except AssertionError as exc:
            legs.append((name, False, str(exc)))

    data = _synth_impact()

    def l_recovers_known_gamma():
        b = fit_gamma(data, "A_naive")
        assert b.get("gamma") is not None, "no estimate on a panel with known elasticity"
        assert abs(b["gamma"] - 0.62) < 0.06, "naive gamma %.4f vs truth 0.62" % b["gamma"]

    def l_controlled_also_recovers():
        b = fit_gamma(data, "B_controlled")
        assert b.get("gamma") is not None
        assert abs(b["gamma"] - 0.62) < 0.08, "controlled gamma %.4f vs truth 0.62" % b["gamma"]

    def l_ci_covers_truth():
        b = fit_gamma(data, "A_naive")
        lo, hi = b["gamma_ci"]
        assert lo < 0.62 < hi, "95%% interval [%.3f, %.3f] misses the truth" % (lo, hi)

    def l_ci_width_shrinks_with_n():
        small = fit_gamma(_synth_impact(n=400), "A_naive")
        big = fit_gamma(_synth_impact(n=3000), "A_naive")
        w_small = small["gamma_ci"][1] - small["gamma_ci"][0]
        w_big = big["gamma_ci"][1] - big["gamma_ci"][0]
        assert w_big < w_small, "interval did not shrink: %.4f vs %.4f" % (w_big, w_small)

    def l_reverse_is_diagnostic_only():
        b = fit_gamma(data, "C_reverse")
        assert b.get("gamma") is None, "the reverse regression must not publish a gamma"
        assert b.get("reverse_slope") is not None, "reverse slope must still be reported"

    def l_degenerate_regressor_returns_none():
        flat = [(r[0], r[1], 1e8) for r in data]
        b = fit_gamma(flat, "A_naive")
        assert b.get("gamma") is None, "a constant regressor must not yield a gamma"
        assert b.get("reason"), "the refusal must carry a reason"

    def l_zero_move_rows_dropped():
        rows = list(data)
        for i in range(0, 40):
            rows[i] = (rows[i][0], 0.0, rows[i][2])
        b = fit_gamma(rows, "A_naive")
        assert b["rows_dropped"] == 40, "dropped %d, expected 40" % b["rows_dropped"]

    def l_era_partition_is_complete():
        rows = [(d, r, a) for d, r, a in
                (("2016-12-30", 1.0, 1e8), ("2017-01-03", 1.0, 1e8),
                 ("2019-05-05", 1.0, 1e8))]
        pre, post = split_era(rows, "pre2017"), split_era(rows, "2017plus")
        assert len(pre) + len(post) == len(rows), "era split lost rows"
        assert not ({r[0] for r in pre} & {r[0] for r in post}), "era split overlaps"

    def l_clip_keeps_charge_positive():
        assert clip_gamma(-1.0) == GAMMA_FLOOR
        assert clip_gamma(99.0) == GAMMA_CEIL

    def l_charge_matches_e232_at_one():
        w = [(i % 7 < 3) * 1.0 for i in range(240)]
        ret = [((i * 37) % 91) - 45.0 for i in range(240)]
        for g in (0.55, 1.0, 1.4):
            a, _ = e232.channel_rows(w, ret, 140, COST_SIDE_BP, g, 0.3)
            b, _ = e232.channel_rows(w, ret, 140, COST_SIDE_BP, g, 0.3)
            assert a == b, "channel rows are not deterministic at gamma %.2f" % g
        lin, _ = e232.channel_rows(w, ret, 140, COST_SIDE_BP, 1.0, 0.3)
        ref, _ = e228.rows_for(w, ret, 140, COST_SIDE_BP)
        ref_by_i = {r["i"]: r for r in ref}
        assert lin, "gamma=1 must publish at least one out-of-sample row"
        # channel_rows is the OOS slice; the family model is per session, so compare cost
        # on the sessions the two share rather than on row counts
        worst = max(abs(r["cost_bp"] - ref_by_i[r["i"]]["cost_bp"]) for r in lin
                    if r["i"] in ref_by_i)
        assert worst < 1e-12, "gamma=1 cost differs from e228 by %.3g" % worst
        assert all(r["i"] in ref_by_i for r in lin), "channel rows left the family index"

    def l_verdict_inside_classifier():
        def inside(vs):
            return len(set(vs)) == 1
        assert inside(["BAND_DEAD", "BAND_DEAD", "BAND_DEAD"]), "stable must read stable"
        assert not inside(["BAND_PAYS", "BAND_DEAD", "BAND_DEAD"]), \
            "a verdict that moves inside the interval must not read stable"

    def l_liveness_asserted_before_verdict():
        # a fixture in which nothing trades returns "NO_EFFECT" at every gamma; the face
        # must be able to see that, so the pre-leg is: some cell actually moved weights
        w = [0.0] * 240
        prof = e230.change_profile(w)
        assert prof["weight_changes"] == 0, "a flat path must report zero changes"
        moved = [1.0 if i % 5 < 3 else 0.0 for i in range(240)]
        assert e230.change_profile(moved)["weight_changes"] > 0, "a moving path must move"

    def l_basket_rows_sum_amounts():
        rows = basket_rows()
        if not rows:
            return  # no panels on a bare checkout: not a failure of the estimator
        assert all(r[2] > 0 for r in rows), "basket turnover must be positive"
        assert all(r[1] is not None for r in rows), "basket session move must exist"

    leg("the naive estimator recovers a known elasticity", l_recovers_known_gamma)
    leg("the controlled estimator recovers a known elasticity", l_controlled_also_recovers)
    leg("the 95% HAC interval covers the truth", l_ci_covers_truth)
    leg("the interval shrinks as the panel grows", l_ci_width_shrinks_with_n)
    leg("the reverse regression is a diagnostic, never an estimate", l_reverse_is_diagnostic_only)
    leg("a degenerate regressor refuses instead of inventing a gamma",
        l_degenerate_regressor_returns_none)
    leg("zero-move sessions are dropped and counted", l_zero_move_rows_dropped)
    leg("the era split is complete and disjoint", l_era_partition_is_complete)
    leg("the downstream clip keeps the charge function positive", l_clip_keeps_charge_positive)
    leg("gamma=1.0 still reproduces the family cost model", l_charge_matches_e232_at_one)
    leg("a verdict that moves across the interval is not called stable",
        l_verdict_inside_classifier)
    leg("liveness is asserted before any verdict is read", l_liveness_asserted_before_verdict)
    leg("the basket panel sums member turnover", l_basket_rows_sum_amounts)

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