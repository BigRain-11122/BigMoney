"""E234 -- the book holds five instruments but the family charges them one exponent.

E233 measured the charge curvature from the panel and re-read the family on the measured
interval, but it published ONE exponent per panel: sh510300 0.928 [0.830, 1.026] and the
equal-weight basket 0.917. The basket is five instruments with very different liquidity
and history (sh588000 only starts in 2020), so a book-level exponent may be a MIXTURE
being charged to four sleeves that do not share it. Question, frozen before any number:

  (a) PER MEMBER. Estimate |r_oc| = k * amount ** gamma separately for each of the five
      basket members (E233 estimator B, Newey-West lag 20). Two readings of "one number":
        * interval compatibility -- do all five 95% intervals share a point?
        * pooled fit -- one slope with five member intercepts; how many members sit
          outside the pooled interval, i.e. how many sleeves the single exponent
          mis-prices.
      Then re-price the BOOK: with member i holding w/N of a book exposure w, its traded
      amount is |dw|/N, so the book bill becomes
            cost_book(dw) = sum_i c * (|dw|/N) ** gamma_i
      which reduces to the linear bill c*|dw| when every gamma_i = 1 (selftest leg). The
      face publishes the bill under the per-member exponents beside the uniform bill at
      each E233 point, and re-derives E229's channels and E230's ladder under both.

  (b) PER ERA. E233 measured pre-2017 1.079 and 2017+ 0.883 -- a gap its own sampling
      interval does not cover. Re-derive the ladder on the 2017+ slice twice: with the
      exponent measured on that era, and with the exponent measured on the full sample.
      Count the cells whose verdict would have differed had the exponent been measured
      at the time instead of borrowed from a longer sample.

Both readings are descriptive for the already-decided family: no arm is re-adopted here.

VERDICT VOCABULARY (fixed):
  * member_compatibility = "one_exponent_holds"  if the five intervals share a point and
    every member sits inside the pooled interval; "mixture" otherwise, naming the
    members/pairs that break it.
  * book_bill_shift_bp  = per-member bill - uniform bill at the same point.
  * ladder verdicts are E230's own (BAND_PAYS / BAND_NOISE / BAND_DEAD / ...), counted,
    never averaged.

Liveness is asserted first: a path with no weight changes returns a zero bill at every
exponent and would make "bill shifted" read as false for the wrong reason (r1261 lesson).
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
import e225_state_tilt as e225  # noqa: E402
import e230_hysteresis_toll as e230  # noqa: E402
import e232_cost_curvature as e232  # noqa: E402
import e233_empirical_gamma as e233  # noqa: E402

ROOT = e222.ROOT
PANEL_DIR = e222.PANEL_DIR
OUTDIR = os.path.join(ROOT, "results", "state_tilt")

COST_SIDE_BP = e225.COST_SIDE_BP
NW_LAG = e225.NW_LAG
BASKET = e225.BASKET
PRIMARY_SYMBOL = e225.PRIMARY_SYMBOL

ARMS = ["binary_low", "tilt_step", "tilt_linear"]
LADDER_FRACS = (0.10, 0.25)
ERA_EDGE = e233.ERA_EDGE            # 2017-01-01, E190's trim edge, reused not re-invented
ESTIMATOR = e233.PRIMARY_ESTIMATOR   # B_controlled, frozen in E233 before its numbers
GAMMA_FLOOR, GAMMA_CEIL = e233.GAMMA_FLOOR, e233.GAMMA_CEIL
Z95 = 1.96


# ---------------------------------------------------------------- per-member charge
def charge_book_per_member(abs_dw, cost_side_bp, gammas):
    """Book-level bill when sleeve i trades |dw|/N at its own exponent gamma_i."""
    if not gammas:
        raise ValueError("per-member charge needs at least one member exponent")
    if abs_dw is None or abs_dw <= 0.0:
        return 0.0
    per_member = abs_dw / float(len(gammas))
    total = 0.0
    for g in gammas:
        if g is None or g <= 0.0:
            raise ValueError("every member exponent must be > 0")
        total += cost_side_bp * (per_member ** g)
    return total


def rows_for_per_member(weights, ret_bp, split, cost_side_bp, gammas):
    """e232.rows_for_gamma with the charge replaced by the per-member sum."""
    n = len(ret_bp)
    is_rets = [r for r in ret_bp[1:split] if r is not None]
    mu_is = e225._mean(is_rets)
    rows = []
    prev_w = 0.0
    for i in range(0, n - 1):
        w = weights[i]
        dw = w - prev_w
        cost = charge_book_per_member(abs(dw), cost_side_bp, gammas)
        r = ret_bp[i + 1]
        if r is None:
            prev_w = w
            continue
        rows.append({"i": i, "w": w, "abs_dw": abs(dw), "gross_bp": w * r,
                     "cost_bp": cost, "excess_bp": w * r - cost - w * mu_is})
        prev_w = w
    return rows, mu_is


def channel_rows_per_member(weights, ret_bp, split, cost_side_bp, gammas, const):
    """E229's three channels, with the per-member bill in place of the scalar charge."""
    base, mu_is = rows_for_per_member(weights, ret_bp, split, cost_side_bp, gammas)
    cut = split - 1
    rows = []
    for r in base:
        if r["i"] < cut:
            continue
        ret = ret_bp[r["i"] + 1]
        assert ret is not None, "rows_for_per_member must not emit an unpriced session"
        dev = ret - mu_is
        if r["w"] == 0.0:
            sel = (-const) * dev
            siz = 0.0
        else:
            sel = 0.0
            siz = (r["w"] - const) * dev
        toll = -r["cost_bp"]
        rows.append({"i": r["i"], "w": r["w"], "ret_bp": ret, "dev_bp": dev,
                     "selection": sel, "sizing": siz, "toll": toll,
                     "pair": sel + siz + toll, "cost_bp": r["cost_bp"],
                     "abs_dw": r["abs_dw"]})
    return rows, mu_is


def total_cost_per_member(weights, cost_side_bp, gammas):
    prev = 0.0
    total, changes = 0.0, 0
    for w in weights:
        d = abs(w - prev)
        if d > 0.0:
            changes += 1
            total += charge_book_per_member(d, cost_side_bp, gammas)
        prev = w
    return {"weight_changes": changes, "total_cost_bp": total}


# ---------------------------------------------------------------- member estimates
def member_estimates(panel_dir=None):
    panel_dir = panel_dir or PANEL_DIR
    out = []
    rows_by_sym = {}
    for sym in BASKET:
        rows = e233.load_ohlc(sym, panel_dir)
        rows_by_sym[sym] = rows
        block = e233.fit_gamma(rows, ESTIMATOR) if rows else {"estimator": ESTIMATOR,
                                                              "reason": "panel_missing"}
        if rows:
            block.update({"symbol": sym, "first": rows[0][0], "last": rows[-1][0],
                          "sessions": len(rows)})
        out.append(block)
    return out, rows_by_sym


def pooled_fit(rows_by_sym, estimator=ESTIMATOR):
    """One slope, five member intercepts: does a single exponent fit every sleeve?

    The specification must be the SAME one the member fits use, controls included: a
    pooled regression that drops the lagged magnitude/volume terms is the naive estimator
    wearing the controlled one's name, and it would report a slope several times smaller
    than every member estimate it is supposed to summarise (selftest leg pins this).
    """
    syms = [s for s in BASKET if rows_by_sym.get(s)]
    if len(syms) < 2:
        return {"reason": "fewer than two members with data"}
    y, la, ly_lag, la_lag, dummies = [], [], [], [], []
    for idx, sym in enumerate(syms):
        clean = [r for r in rows_by_sym[sym] if r[1] not in (None, 0.0) and r[2] > 0.0]
        ys = [math.log(abs(r[1])) for r in clean]
        ls = [math.log(r[2]) for r in clean]
        if len(ys) < 3:
            continue
        # drop the first session of each member so its own lags exist
        ys, ls = ys[1:], ls[1:]
        for k in range(len(ys)):
            y.append(ys[k])
            la.append(ls[k])
            ly_lag.append(ys[k - 1])
            la_lag.append(ls[k - 1])
            dummies.append([1.0 if (idx == j and j >= 1) else 0.0
                            for j in range(1, len(syms))])
    cols = [la, ly_lag, la_lag] + [[d[i] for d in dummies] for i in range(max(0, len(syms) - 1))]
    fit = e233.ols_hac(y, cols, NW_LAG)
    if fit is None:
        return {"reason": "singular", "members": syms}
    slope, se = fit["beta"][1], fit["se"][1]
    ci = [slope - Z95 * se, slope + Z95 * se] if se else None
    return {"estimator": estimator, "members": syms, "gamma": slope, "gamma_se": se,
            "gamma_ci": ci, "n": fit["n"], "r2": fit["r2"], "lag": fit["lag"],
            "n_regressors": len(cols), "controls": ["log_amount", "log_abs_ret_lag1",
                                                    "log_amount_lag1"]}


def interval_intersection(intervals):
    los = [i[0] for i in intervals if i]
    his = [i[1] for i in intervals if i]
    if not los or not his:
        return None
    lo, hi = max(los), min(his)
    return [lo, hi] if lo <= hi else None


def compatibility(members, pooled):
    have = [m for m in members if m.get("gamma_ci")]
    inter = interval_intersection([m["gamma_ci"] for m in have])
    pairwise = []
    for i in range(len(have)):
        for j in range(i + 1, len(have)):
            a, b = have[i], have[j]
            overlap = not (a["gamma_ci"][1] < b["gamma_ci"][0]
                           or b["gamma_ci"][1] < a["gamma_ci"][0])
            if not overlap:
                pairwise.append({"a": a["symbol"], "b": b["symbol"],
                                 "a_ci": a["gamma_ci"], "b_ci": b["gamma_ci"]})
    pooled_ci = (pooled or {}).get("gamma_ci")
    outside = []
    if pooled_ci:
        outside = [m["symbol"] for m in have
                   if m["gamma_ci"][1] < pooled_ci[0] or m["gamma_ci"][0] > pooled_ci[1]]
    verdict = "one_exponent_holds" if (inter and pooled_ci and not outside) else "mixture"
    return {"common_interval": inter, "pairwise_disjoint": pairwise,
            "members_outside_pooled_interval": outside,
            "members_measured": len(have), "verdict": verdict}


def member_points(members, pooled):
    """The exponents the book is re-priced at: per member, and two uniform references."""
    per = [{"symbol": m["symbol"],
            "gamma": round(e233.clip_gamma(m["gamma"]), 6) if m.get("gamma") is not None
            else None,
            "gamma_ci": m.get("gamma_ci")} for m in members if m.get("gamma") is not None]
    return per


# ---------------------------------------------------------------- ladder helper
def ladder_cell(base_rows, band_rows, weights_equal, bar_t, w_band):
    delta = e230.paired_delta(base_rows, band_rows)
    v = e230.rung_verdict(delta, weights_equal, bar_t)
    return {"verdict": v["verdict"],
            "verdict_reason": v.get("verdict_reason"),
            "d_pair_ann_bp_per_year": v.get("d_pair_ann_bp_per_year"),
            "d_pair_t_nw": v.get("d_pair_t_nw"),
            "d_toll_ann_bp_per_year": v.get("d_toll_ann_bp_per_year"),
            "weight_changes": e230.change_profile(w_band)["weight_changes"]}


def run(save=True, panel_dir=None, outdir=None):
    panel_dir = panel_dir or PANEL_DIR
    outdir = outdir or OUTDIR
    single = e225.single_panel(PRIMARY_SYMBOL, panel_dir)
    basket = e225.basket_panel(panel_dir)
    if single is None or not basket:
        print("panels missing (single=%s basket=%s)" % (bool(single), bool(basket)))
        return None

    members, rows_by_sym = member_estimates(panel_dir)
    if not any(m.get("gamma") is not None for m in members):
        print("no member exponent could be estimated")
        return None
    pooled = pooled_fit(rows_by_sym)
    compat = compatibility(members, pooled)
    per_points = member_points(members, pooled)
    per_gammas = [p["gamma"] for p in per_points if p["gamma"] is not None]
    if not per_gammas:
        print("per-member point set is empty")
        return None

    # uniform reference points: E233's basket estimate and the linear model
    basket_rows = e233.basket_rows(panel_dir)
    basket_est = e233.fit_gamma(basket_rows, ESTIMATOR) if basket_rows else None
    uniform_points = [{"gamma": 1.0, "source": "linear_model"}]
    if basket_est and basket_est.get("gamma") is not None:
        ci = basket_est.get("gamma_ci") or [basket_est["gamma"], basket_est["gamma"]]
        for g, src in ((ci[0], "basket_interval_lo"), (basket_est["gamma"], "basket_point"),
                       (ci[1], "basket_interval_hi")):
            gg = round(e233.clip_gamma(g), 6)
            if all(abs(gg - u["gamma"]) > 1e-9 for u in uniform_points):
                uniform_points.append({"gamma": gg, "source": src})

    dates, ret_bp = basket
    sig = e225.vol_signal(ret_bp)
    split = e225.split_index(len(dates))
    sd_is = e230.band_width(sig, split)

    n_cells = len(ARMS) * (len(uniform_points) + 1) * (1 + len(LADDER_FRACS))
    bar_t = max(2.0, e222._z_two_sided(0.05 / n_cells))

    arms_out, ladder_out = [], []
    for arm in ARMS:
        base_w = e225.weights_series(sig, arm)
        probe, _mu = e232.channel_rows(base_w, ret_bp, split, COST_SIDE_BP, 1.0, 0.0)
        const = e225._mean([r["w"] for r in probe]) or 0.0
        changes = e230.change_profile(base_w)["weight_changes"]
        arm_block = {"name": arm, "const_weight": const, "base_weight_changes": changes,
                     "uniform": [], "per_member": None}
        # uniform references through the family's own code path
        for up in uniform_points:
            rows, _mu2 = e232.channel_rows(base_w, ret_bp, split, COST_SIDE_BP,
                                           up["gamma"], const)
            tot = e230._totals(rows)
            tt = e230._stats([r["toll"] for r in rows])["t_nw"]
            st = e230._stats([r["selection"] for r in rows])["t_nw"]
            pt = e230._stats([r["pair"] for r in rows])["t_nw"]
            arm_block["uniform"].append({
                "gamma": up["gamma"], "source": up["source"], "totals": tot,
                "toll_t_nw": tt, "selection_t_nw": st, "pair_t_nw": pt,
                "toll_clears_bar": (tt is not None and abs(tt) >= bar_t),
                "bill": e232.total_cost(base_w, COST_SIDE_BP, up["gamma"])})
        # per-member book
        rows_pm, _mu3 = channel_rows_per_member(base_w, ret_bp, split, COST_SIDE_BP,
                                                per_gammas, const)
        tot_pm = e230._totals(rows_pm)
        tt_pm = e230._stats([r["toll"] for r in rows_pm])["t_nw"]
        st_pm = e230._stats([r["selection"] for r in rows_pm])["t_nw"]
        pt_pm = e230._stats([r["pair"] for r in rows_pm])["t_nw"]
        bill_pm = total_cost_per_member(base_w, COST_SIDE_BP, per_gammas)
        # CONTROL: the same five-sleeve formula with ONE exponent for every sleeve. Without
        # it the per-member bill conflates the mixture with the split -- splitting a book
        # move into N concave charges is dearer than the linear bill on its own (E232 pit),
        # so only this control isolates what the mixture costs.
        g_pooled = (pooled or {}).get("gamma")
        g_basket = basket_est.get("gamma") if basket_est else None
        bill_controls = {}
        for label, g in (("pooled_gamma", g_pooled), ("basket_point", g_basket)):
            if g is None:
                continue
            gg = max(GAMMA_FLOOR, min(GAMMA_CEIL, g))
            bill_controls[label] = dict(total_cost_per_member(base_w, COST_SIDE_BP,
                                                              [gg] * len(per_gammas)),
                                        gamma=gg)
        arm_block["per_member"] = {
            "gammas": per_gammas, "totals": tot_pm, "toll_t_nw": tt_pm,
            "selection_t_nw": st_pm, "pair_t_nw": pt_pm,
            "toll_clears_bar": (tt_pm is not None and abs(tt_pm) >= bar_t),
            "toll_single_channel": (tt_pm is not None and st_pm is not None
                                    and abs(tt_pm) >= bar_t and abs(st_pm) < bar_t),
            "bill": bill_pm, "bill_controls": bill_controls}
        arms_out.append(arm_block)

        # E230's ladder under per-member vs uniform
        for frac in LADDER_FRACS:
            band = frac * sd_is
            band_w = e230.band_weights(sig, arm, band)
            cell = {"arm": arm, "band_frac": frac, "band_bp": band, "by_charge": []}
            band_rows_u = {}
            for up in uniform_points:
                key = "%.6f" % up["gamma"]
                if key not in band_rows_u:
                    band_rows_u[key], _ = e232.channel_rows(band_w, ret_bp, split,
                                                             COST_SIDE_BP, up["gamma"],
                                                             const)
                base_rows, _ = e232.channel_rows(base_w, ret_bp, split, COST_SIDE_BP,
                                                 up["gamma"], const)
                v = ladder_cell(base_rows, band_rows_u[key], band_w == base_w, bar_t,
                                band_w)
                v.update({"charge": "uniform", "gamma": up["gamma"],
                          "source": up["source"]})
                cell["by_charge"].append(v)
            band_rows_pm, _ = channel_rows_per_member(band_w, ret_bp, split, COST_SIDE_BP,
                                                      per_gammas, const)
            base_rows_pm, _ = channel_rows_per_member(base_w, ret_bp, split, COST_SIDE_BP,
                                                      per_gammas, const)
            v = ladder_cell(base_rows_pm, band_rows_pm, band_w == base_w, bar_t, band_w)
            v.update({"charge": "per_member", "gamma": None, "source": "member_estimates"})
            cell["by_charge"].append(v)
            cell["verdict_moves_vs_per_member"] = sorted({
                x["source"] for x in cell["by_charge"]
                if x["verdict"] != cell["by_charge"][-1]["verdict"]})
            ladder_out.append(cell)

    # ---- (b) era: was the 2017+ conclusion an artefact of a borrowed exponent?
    era_block = None
    rows_single = e233.load_ohlc(PRIMARY_SYMBOL, panel_dir)
    if rows_single:
        full = e233.fit_gamma(rows_single, ESTIMATOR)
        post = e233.fit_gamma(e233.split_era(rows_single, "2017plus"), ESTIMATOR)
        pre = e233.fit_gamma(e233.split_era(rows_single, "pre2017"), ESTIMATOR)
        if post.get("gamma") is not None and full.get("gamma") is not None:
            sdates, sret = single
            keep = [i for i, d in enumerate(sdates) if d >= ERA_EDGE]
            if len(keep) > 200:
                e_dates = [sdates[i] for i in keep]
                e_ret = [sret[i] for i in keep]
                e_sig = e225.vol_signal(e_ret)
                e_split = e225.split_index(len(e_dates))
                e_sd = e230.band_width(e_sig, e_split)
                g_era = round(e233.clip_gamma(post["gamma"]), 6)
                g_full = round(e233.clip_gamma(full["gamma"]), 6)
                cells = []
                for arm in ARMS:
                    bw = e225.weights_series(e_sig, arm)
                    probe, _m = e232.channel_rows(bw, e_ret, e_split, COST_SIDE_BP, 1.0, 0.0)
                    c0 = e225._mean([r["w"] for r in probe]) or 0.0
                    for frac in LADDER_FRACS:
                        bandw = e230.band_weights(e_sig, arm, frac * e_sd)
                        got = {}
                        for label, g in (("era_measured", g_era),
                                         ("borrowed_full_sample", g_full)):
                            br, _ = e232.channel_rows(bw, e_ret, e_split, COST_SIDE_BP, g, c0)
                            bdr, _ = e232.channel_rows(bandw, e_ret, e_split, COST_SIDE_BP,
                                                       g, c0)
                            v = ladder_cell(br, bdr, bandw == bw, bar_t, bandw)
                            got[label] = {"gamma": g, "verdict": v["verdict"],
                                          "d_pair_ann_bp_per_year":
                                              v["d_pair_ann_bp_per_year"],
                                          "d_pair_t_nw": v["d_pair_t_nw"]}
                        cells.append({"arm": arm, "band_frac": frac,
                                      "era_measured": got["era_measured"],
                                      "borrowed_full_sample": got["borrowed_full_sample"],
                                      "verdict_differs": (got["era_measured"]["verdict"]
                                                          != got["borrowed_full_sample"]["verdict"]),
                                      "d_pair_gap_bp_per_year": (
                                          (got["era_measured"]["d_pair_ann_bp_per_year"]
                                           or 0.0)
                                          - (got["borrowed_full_sample"]
                                             ["d_pair_ann_bp_per_year"] or 0.0))})
                era_block = {
                    "edge": ERA_EDGE, "sessions": len(e_dates),
                    "first": e_dates[0], "last": e_dates[-1],
                    "gamma_full_sample": g_full,
                    "gamma_era_measured": g_era,
                    "estimate_full": {k: full.get(k) for k in
                                      ("gamma", "gamma_se", "gamma_ci", "n", "r2")},
                    "estimate_era": {k: post.get(k) for k in
                                     ("gamma", "gamma_se", "gamma_ci", "n", "r2")},
                    "estimate_pre2017": {k: pre.get(k) for k in
                                         ("gamma", "gamma_se", "gamma_ci", "n", "r2")},
                    "cells": cells,
                    "cells_differing": sum(1 for c in cells if c["verdict_differs"]),
                    "cells_total": len(cells),
                    "interval_covers_era_point": bool(
                        post.get("gamma_ci") and full.get("gamma_ci")
                        and full["gamma_ci"][0] <= post["gamma"] <= full["gamma_ci"][1]),
                }

    face = {
        "study": "E234",
        "title": "the book holds five instruments -- is the book-level exponent a mixture?",
        "generated": datetime.now().isoformat(timespec="seconds"),
        "evidence_cutoff": dates[-1],
        "frozen_spec": {
            "estimator": ESTIMATOR,
            "hac_lag": NW_LAG,
            "era_edge": ERA_EDGE,
            "members": list(BASKET),
            "book_charge": "cost_book(dw) = sum_i c*(|dw|/N)**gamma_i, which equals c*|dw| "
                           "when every gamma_i = 1 (selftest leg)",
            "arms": ARMS,
            "ladder_fracs": list(LADDER_FRACS),
            "bar_t": bar_t,
            "bar_basis": "two-sided 5%% over %d cells (arms x charges x bands)" % n_cells,
            "compatibility_rule": "one_exponent_holds only if the five 95%% intervals "
                                  "share a point AND no member sits outside the pooled "
                                  "interval; otherwise mixture, naming the breakers",
            "no_adoption": "the arms are already judged; this asks only whether the "
                           "single exponent is a property of the book or an average of it",
        },
        "member_estimates": members,
        "pooled_fit": pooled,
        "compatibility": compat,
        "per_member_points": per_points,
        "uniform_points": uniform_points,
        "book": {"panel": "basket_equal_weight", "sessions": len(dates),
                 "first": dates[0], "last": dates[-1], "split_session": split,
                 "split_date": dates[split], "signal_sd_is_bp": sd_is,
                 "arms": arms_out},
        "ladder": ladder_out,
        "era": era_block,
    }
    face["summary"] = {
        "member_gammas": [{"symbol": m["symbol"], "gamma": m.get("gamma"),
                           "gamma_ci": m.get("gamma_ci")}
                          for m in members],
        "pooled_gamma": (pooled or {}).get("gamma"),
        "pooled_ci": (pooled or {}).get("gamma_ci"),
        "compatibility_verdict": compat["verdict"],
        "common_interval": compat["common_interval"],
        "pairwise_disjoint_pairs": compat["pairwise_disjoint"],
        "members_outside_pooled_interval": compat["members_outside_pooled_interval"],
        "per_member_gammas": per_gammas,
        "span_per_member": [min(per_gammas), max(per_gammas)] if per_gammas else None,
        "bill_by_arm": [{"arm": a["name"],
                         "uniform_linear_bp": next(
                             (u["bill"]["total_cost_bp"] for u in a["uniform"]
                              if u["source"] == "linear_model"), None),
                         "uniform_point_bp": next(
                             (u["bill"]["total_cost_bp"] for u in a["uniform"]
                              if u["source"] == "basket_point"), None),
                         "per_member_bp": a["per_member"]["bill"]["total_cost_bp"],
                         "uniform_same_granularity_bp": (
                             a["per_member"]["bill_controls"].get("pooled_gamma") or {}
                         ).get("total_cost_bp"),
                         "granularity_effect_bp": (
                             ((a["per_member"]["bill_controls"].get("pooled_gamma") or {})
                              .get("total_cost_bp") or 0.0)
                             - next((u["bill"]["total_cost_bp"] for u in a["uniform"]
                                     if u["source"] == "linear_model"), 0.0)),
                         "mixture_effect_bp": (
                             a["per_member"]["bill"]["total_cost_bp"]
                             - ((a["per_member"]["bill_controls"].get("pooled_gamma") or {})
                                .get("total_cost_bp") or 0.0)),
                         "weight_changes": a["per_member"]["bill"]["weight_changes"]}
                        for a in arms_out],
        "toll_clears_bar": {
            "uniform_linear": sum(1 for a in arms_out
                                  for u in a["uniform"]
                                  if u["source"] == "linear_model" and u["toll_clears_bar"]),
            "uniform_basket_point": sum(1 for a in arms_out
                                        for u in a["uniform"]
                                        if u["source"] == "basket_point"
                                        and u["toll_clears_bar"]),
            "per_member": sum(1 for a in arms_out if a["per_member"]["toll_clears_bar"]),
            "arm_cells": len(arms_out),
        },
        "ladder_cells": len(ladder_out),
        "ladder_cells_moved_by_charge": [
            {"arm": c["arm"], "band_frac": c["band_frac"],
             "moves": c["verdict_moves_vs_per_member"]}
            for c in ladder_out if c["verdict_moves_vs_per_member"]],
        "era_cells_differing": (era_block or {}).get("cells_differing"),
        "era_cells_total": (era_block or {}).get("cells_total"),
        "era_interval_covers_point": (era_block or {}).get("interval_covers_era_point"),
    }
    face["answer"] = _answer(face)
    if save:
        if not os.path.isdir(outdir):
            os.makedirs(outdir)
        name = "PER-MEMBER-GAMMA-%s.json" % face["evidence_cutoff"]
        text = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
        with open(os.path.join(outdir, name), "w", encoding="utf-8") as fh:
            fh.write(text)
        with open(os.path.join(outdir, "per_member_gamma_latest.json"), "w",
                  encoding="utf-8") as fh:
            fh.write(text)
        face["_written"] = os.path.relpath(os.path.join(outdir, name), ROOT).replace(
            "\\", "/")
        print("wrote %s" % face["_written"])
    return face


def _f(v, spec="%.3f"):
    return "-" if v is None else (spec % v)


def _answer(face):
    s = face["summary"]
    c = face["compatibility"]
    per = ", ".join("%s %s [%s, %s]" % (m["symbol"], _f(m.get("gamma")),
                                        _f((m.get("gamma_ci") or [None])[0]),
                                        _f((m.get("gamma_ci") or [None, None])[1]))
                    for m in face["member_estimates"] if m.get("gamma") is not None)
    bills = "; ".join("%s linear %s -> same-exponent 5-sleeve %s -> per-member %s bp" % (
        b["arm"], _f(b["uniform_linear_bp"], "%.1f"),
        _f(b["uniform_same_granularity_bp"], "%.1f"), _f(b["per_member_bp"], "%.1f"))
        for b in s["bill_by_arm"])
    era = face.get("era") or {}
    parts = [
        "Measured per member rather than book-wide: %s, against a pooled slope of %s "
        "[%s, %s] with five member intercepts." % (
            per or "no member estimate", _f(s["pooled_gamma"]),
            _f((s["pooled_ci"] or [None])[0]), _f((s["pooled_ci"] or [None, None])[1])),
        "Compatibility reads %s: %s, and %d of %d members sit outside the pooled "
        "interval%s." % (
            c["verdict"],
            ("a common point exists at [%.3f, %.3f]" % tuple(c["common_interval"]))
            if c["common_interval"] else
            "%d member pairs have disjoint intervals" % len(c["pairwise_disjoint"]),
            len(c["members_outside_pooled_interval"]), c["members_measured"],
            (" (" + ", ".join(c["members_outside_pooled_interval"]) + ")")
            if c["members_outside_pooled_interval"] else ""),
        "Re-priced with each sleeve charged its own exponent the movement bill becomes "
        "%s. The split and the mixture are separated: charging the same five-sleeve "
        "formula with the pooled exponent accounts for %s of the move and the per-member "
        "exponents for %s." % (
            bills,
            ", ".join("%s %+.0f bp" % (b["arm"], b["granularity_effect_bp"] or 0.0)
                      for b in s["bill_by_arm"]),
            ", ".join("%s %+.0f bp" % (b["arm"], b["mixture_effect_bp"] or 0.0)
                      for b in s["bill_by_arm"])),
        "So the single exponent is %s at the book level." % (
            "approximately right in total" if all(
                abs(b["mixture_effect_bp"] or 0.0)
                <= 0.05 * max(1.0, abs(b["uniform_same_granularity_bp"] or 0.0))
                for b in s["bill_by_arm"]) else
            "not the book's true bill -- the sleeves do not share an exponent"),
        "The toll still clears its bar on %d of %d arms under the per-member charge "
        "(linear %d, basket point %d), and %d of %d ladder cells change verdict when the "
        "charge becomes per-member." % (
            s["toll_clears_bar"]["per_member"], s["toll_clears_bar"]["arm_cells"],
            s["toll_clears_bar"]["uniform_linear"], s["toll_clears_bar"]["uniform_basket_point"],
            len(s["ladder_cells_moved_by_charge"]), s["ladder_cells"]),
    ]
    if era:
        parts.append(
            "On the 2017+ slice the exponent measured then is %s against %s on the full "
            "sample (the full-sample interval %s that era point); re-deriving the ladder "
            "with the era's own exponent instead of the borrowed one changes %d of %d "
            "cells." % (
                _f(era.get("gamma_era_measured")), _f(era.get("gamma_full_sample")),
                "covers" if era.get("interval_covers_era_point") else "does not cover",
                era.get("cells_differing"), era.get("cells_total")))
    return " ".join(parts)


# ---------------------------------------------------------------- selftest
def _synth_impact(n=1200, gamma=0.62, seed=11):
    return e233._synth_impact(n=n, gamma=gamma, seed=seed)


def selftest():
    legs = []

    def leg(name, fn):
        try:
            fn()
            legs.append((name, True, ""))
        except AssertionError as exc:
            legs.append((name, False, str(exc)))

    def l_linear_identity():
        for gammas in ([1.0], [1.0, 1.0], [1.0] * 5):
            for dw in (0.0, 0.05, 0.37, 1.0):
                a = charge_book_per_member(dw, COST_SIDE_BP, gammas)
                b = e232.charge_bp(abs(dw), COST_SIDE_BP, 1.0)
                assert abs(a - b) < 1e-12, "per-member bill %.6f vs linear %.6f" % (a, b)

    def l_rows_match_family_at_one():
        w = [(i % 7 < 3) * 1.0 for i in range(240)]
        ret = [((i * 37) % 91) - 45.0 for i in range(240)]
        a, mu_a = rows_for_per_member(w, ret, 140, COST_SIDE_BP, [1.0] * 5)
        b, mu_b = e232.rows_for_gamma(w, ret, 140, COST_SIDE_BP, 1.0)
        assert abs(mu_a - mu_b) < 1e-12, "mu_is drifted: %.9f vs %.9f" % (mu_a, mu_b)
        assert len(a) == len(b), "row count %d vs %d" % (len(a), len(b))
        worst = max(abs(x["cost_bp"] - y["cost_bp"]) for x, y in zip(a, b))
        assert worst < 1e-12, "cost differs from the linear family by %.3g" % worst

    def l_missing_sessions_not_priced():
        w = [1.0] * 60
        ret = [None] * 60
        rows, _mu = rows_for_per_member(w, ret, 30, COST_SIDE_BP, [0.9] * 5)
        assert rows == [], "a session with no return must not be charged"

    def l_exponent_must_be_positive():
        for bad in ([0.0], [-0.5], [None]):
            try:
                charge_book_per_member(0.2, COST_SIDE_BP, bad)
            except ValueError:
                continue
            raise AssertionError("exponent %r was accepted" % (bad,))

    def l_concave_makes_small_moves_dearer_per_unit():
        # the E232 pit, re-pinned here because this face splits one book move into N
        small = charge_book_per_member(0.2, COST_SIDE_BP, [0.75] * 5) / 0.2
        large = charge_book_per_member(0.2, COST_SIDE_BP, [1.25] * 5) / 0.2
        assert small > large, "concave charge must cost more per unit on a small move"

    def l_per_member_bill_sits_between_extremes():
        lo = charge_book_per_member(0.2, COST_SIDE_BP, [0.5] * 5)
        hi = charge_book_per_member(0.2, COST_SIDE_BP, [1.5] * 5)
        mid = charge_book_per_member(0.2, COST_SIDE_BP, [1.0] * 5)
        assert lo > mid > hi, "bill is not monotone in the exponent"

    def l_intersection_and_verdict():
        ok = compatibility([{"symbol": "a", "gamma_ci": [0.8, 1.1]},
                            {"symbol": "b", "gamma_ci": [0.9, 1.3]}],
                           {"gamma_ci": [0.85, 1.2]})
        assert ok["verdict"] == "one_exponent_holds", "overlapping members read as mixture"
        assert abs(ok["common_interval"][0] - 0.9) < 1e-12
        bad = compatibility([{"symbol": "a", "gamma_ci": [0.2, 0.3]},
                             {"symbol": "b", "gamma_ci": [0.9, 1.3]}],
                            {"gamma_ci": [0.85, 1.2]})
        assert bad["verdict"] == "mixture", "disjoint members read as one exponent"
        assert bad["pairwise_disjoint"] and bad["members_outside_pooled_interval"]

    def l_fit_recovers_known_gamma():
        b = e233.fit_gamma(_synth_impact(), "B_controlled")
        assert b.get("gamma") is not None and abs(b["gamma"] - 0.62) < 0.08, \
            "controlled gamma %.4f" % (b.get("gamma") or -1)

    def l_pooled_fit_needs_two_members():
        rows = {"sh510300": _synth_impact()}
        blk = pooled_fit(rows)
        assert blk.get("reason"), "a one-member pool must refuse instead of fitting"

    def l_pooled_fit_matches_members_when_identical():
        base = _synth_impact(n=600, gamma=0.7)
        rows = {s: list(base) for s in BASKET[:2]}
        blk = pooled_fit(rows)
        assert blk.get("gamma") is not None
        assert abs(blk["gamma"] - 0.7) < 0.12, "pooled gamma %.3f on identical members" % (
            blk["gamma"])

    def l_total_cost_counts_changes_once():
        w = [0.0, 0.0, 1.0, 1.0, 0.5]
        prof = total_cost_per_member(w, COST_SIDE_BP, [1.0] * 5)
        assert prof["weight_changes"] == 2, "changes %d" % prof["weight_changes"]

    def l_flat_path_pays_nothing():
        prof = total_cost_per_member([0.0] * 50, COST_SIDE_BP, [0.9, 0.9])
        assert prof["weight_changes"] == 0 and prof["total_cost_bp"] == 0.0

    def l_pooled_fit_carries_the_member_controls():
        # a pooled fit that drops the lagged terms silently becomes the naive estimator and
        # reports a slope far below every member it is meant to summarise
        rows = {s: list(_synth_impact(n=700, gamma=0.72, seed=3 + i))
                for i, s in enumerate(BASKET[:3])}
        blk = pooled_fit(rows)
        assert blk.get("gamma") is not None, blk.get("reason")
        assert blk["n_regressors"] == len(blk["controls"]) + len(BASKET[:3]) - 1, \
            "pooled spec carries %d regressors, expected %d" % (
                blk["n_regressors"], len(blk["controls"]) + len(BASKET[:3]) - 1)
        assert abs(blk["gamma"] - 0.72) < 0.15, \
            "pooled gamma %.3f drifts from the member truth 0.72 -- controls missing?" % (
                blk["gamma"])

    def l_split_granularity_is_not_a_mixture():
        # the control that keeps this face honest: on a concave charge, splitting one book
        # move into N sleeve charges is dearer than the linear bill before any mixture is
        # considered, so the per-member bill alone must never be read as the mixture effect
        dw = 0.10
        linear = e232.charge_bp(dw, COST_SIDE_BP, 1.0)
        split_same = charge_book_per_member(dw, COST_SIDE_BP, [0.62] * 5)
        assert split_same > linear, "concave split must exceed the linear bill"
        assert abs(split_same - 5 * COST_SIDE_BP * (dw / 5.0) ** 0.62) < 1e-12, \
            "the five-sleeve bill is not N times the per-sleeve charge"
        mixed = charge_book_per_member(dw, COST_SIDE_BP, [0.414, 0.416, 0.760, 0.928, 1.456])
        assert abs(mixed - split_same) > 1e-9, "the mixture term must be measurable"

    leg("every exponent at 1.0 reproduces the linear bill", l_linear_identity)
    leg("the per-member rows reproduce the family rows at gamma=1", l_rows_match_family_at_one)
    leg("a session with no return is never charged", l_missing_sessions_not_priced)
    leg("a non-positive member exponent is refused", l_exponent_must_be_positive)
    leg("a concave charge costs more per unit on a small move", l_concave_makes_small_moves_dearer_per_unit)
    leg("the bill is monotone in the exponent", l_per_member_bill_sits_between_extremes)
    leg("interval compatibility separates one exponent from a mixture", l_intersection_and_verdict)
    leg("the split of one move across five sleeves is priced apart from the mixture",
        l_split_granularity_is_not_a_mixture)
    leg("the pooled fit carries the same controls as the member fits",
        l_pooled_fit_carries_the_member_controls)
    leg("the estimator recovers a known member elasticity", l_fit_recovers_known_gamma)
    leg("a one-member pool refuses instead of fitting", l_pooled_fit_needs_two_members)
    leg("the pooled fit recovers the truth on identical members",
        l_pooled_fit_matches_members_when_identical)
    leg("the movement bill counts each change once", l_total_cost_counts_changes_once)
    leg("a flat path pays nothing", l_flat_path_pays_nothing)

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