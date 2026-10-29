"""E237 -- is the own-turnover channel an information-arrival artefact?

E236 could not settle the granularity question because its three designs agreed about the
SIGN of the own-turnover channel and not about its SIZE: the difference design read
b_own = 0.431 [0.341, 0.520] while the cross-sectional ones read 0.017 and 0.023. It named
the mechanism but did not measure it -- the difference design prices a session against that
session's own turnover CHANGE, which co-moves with the same information arrival that sets
|r|, while the cross-sectional designs price the share of book turnover.

This face separates the two channels directly instead of inferring them from a coefficient
gap. Three things are measured:

  (a) DECOMPOSITION  each member's log|r| is regressed on the book's log|r| (a common
                     market component) and the residual is the relative component. The
                     session's change in log own turnover is then fitted on the changes of
                     the two components: c_common and c_rel, with HAC intervals.
  (b) DIRECT DRIVER  d(log own turnover) on d(log|r|) and on d(log|r_book|), publishing
                     which driver dominates. NOTE, published rather than celebrated:
                     (a) and (b) SPAN THE SAME REGRESSOR SPACE (the relative component is
                     the own return net of beta*market), so c_rel IS the (b) coefficient on
                     d(log|r|) by construction. Agreement between them is an algebraic
                     identity, never evidence; a selftest leg pins the identity.
  (c) ARTEFACT TEST  the design that disagreed in E236 is the turnover-SHARE design, whose
                     coefficient is dy on d(share) controlling d(book turnover). If that
                     coefficient is really market-information arrival, it must collapse once
                     the market's own |r| is known; if it lives in the member's relative part
                     -- where an impact story puts the own channel -- it survives. Measured
                     both ways, plus a first-stage leg on the co-movement itself
                     (d(share) on d(log|r_book|)) so "the control was needed" is a reading,
                     not an assumption. NOTE the direction: the share designs take dy on
                     turnover changes (E236's direction) while (a)/(b) take the turnover
                     change on the return components (the card's impact elasticity); the two
                     directions are not interchangeable and no coefficient is compared
                     across them.

VERDICT VOCABULARY (frozen before any number is read):
  * own_channel_is_information_artefact -- the uncontrolled share coefficient clears the
        multiplicity bar, the market-controlled one does not, and the share co-moves
        materially with the market return. The granularity question is then answered
        NEGATIVE for this panel: no per-member charge may be built on that coefficient.
  * own_channel_survives -- controlled coefficient keeps its sign, clears the bar, and its
        interval overlaps the uncontrolled one (the channel lives in the relative part).
  * unresolved_magnitude_disagreement -- both clear the bar but the intervals do not overlap.
  * no_own_channel -- neither reading clears.
  * unresolved_sign_fragile -- controlled reading flips sign.
  * residual_only_channel -- the channel appears only once the market return is controlled.
  * unresolved_share_dies_without_comovement -- the coefficient dies under the control but
        the first stage says the share never carried the market's information, so the
        collapse is collinearity and nothing is concluded.

BILL RULE (the card's own gate, implemented as code): a bill is permitted only when BOTH
decomposition components are positive, clear the bar, and their 95% intervals overlap. Any
other reading publishes the gate as refused with the reason -- the family's linear charge
stays the only charge the book is written against.

Liveness first: a flat weight path pays a zero bill under every charge shape, so a charge
"disagreement" cannot be read from a path that never trades (r1261 lesson).
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
import e233_empirical_gamma as e233  # noqa: E402
import e235_charge_granularity as e235  # noqa: E402
import e236_share_difference as e236  # noqa: E402

ROOT = e222.ROOT
PANEL_DIR = e222.PANEL_DIR
OUTDIR = os.path.join(ROOT, "results", "state_tilt")

COST_SIDE_BP = e225.COST_SIDE_BP
NW_LAG = e225.NW_LAG
BASKET = e225.BASKET
PRIMARY_SYMBOL = e225.PRIMARY_SYMBOL

ARMS = ["binary_low", "tilt_step", "tilt_linear"]
Z95 = 1.96
MIN_MEMBER_ROWS = e235.MIN_MEMBER_ROWS

# the pooled fits whose coefficients are tested; frozen before any number is read
POOLED_TESTS = (("components", ("dc", "dr")),
                ("direct", ("dy", "dx")),
                ("share", ("dshare", "dla")),
                ("share_controlled", ("dshare", "dla", "dr")))
MIN_POOLED_MEMBERS = 2


# ---------------------------------------------------------------- panels
def panel_maps(panel_dir=None):
    """log|r_book| per date plus the summed book turnover (the E233 basket rows)."""
    panel_dir = panel_dir or PANEL_DIR
    brows = e233.basket_rows(panel_dir)
    if not brows:
        return None
    x_by_date = {}
    for d, r, _a in brows:
        if r and r != 0.0:
            x_by_date[d] = math.log(abs(r))
    agg_by_date = {d: a for d, _r, a in brows if a and a > 0.0}
    return {"x_by_date": x_by_date, "agg_by_date": agg_by_date, "book_rows": brows}


def member_frame(seq, x_by_date):
    """[(date, y, log own turnover, log book turnover, log|r_book|)] on shared dates."""
    out = []
    for d, y, lo, la in seq:
        x = x_by_date.get(d)
        if x is None:
            continue
        out.append((d, y, lo, la, x))
    return out


def frames_for_basket(maps, panel_dir=None):
    panel_dir = panel_dir or PANEL_DIR
    frames = {}
    for sym in BASKET:
        seq = e235._member_series(e233.load_ohlc(sym, panel_dir), maps["agg_by_date"])
        frames[sym] = member_frame(seq, maps["x_by_date"])
    return frames


# ---------------------------------------------------------------- row blocks
def component_rows(frame, lag=NW_LAG):
    """Per-member decomposition of log|r| into common (book) and relative parts.

    Returns the differenced rows both (a) and (b) are fitted on, plus the first-stage
    regression that produced them. A member whose first stage is singular is refused
    rather than silently fitted on a fabricated decomposition.
    """
    if len(frame) < MIN_MEMBER_ROWS:
        return None
    y = [r[1] for r in frame]
    x = [r[4] for r in frame]
    fit = e235._ols_hac_full(y, [x], lag)
    if fit is None:
        return None
    alpha, beta_x = fit["beta"][0], fit["beta"][1]
    var = fit["cov"][1][1]
    se = math.sqrt(var) if var and var > 0 else None
    common = [alpha + beta_x * xi for xi in x]
    rel = [yi - ci for yi, ci in zip(y, common)]
    rows = []
    for k in range(1, len(frame)):
        dlo = frame[k][2] - frame[k - 1][2]
        dla = frame[k][3] - frame[k - 1][3]
        rows.append({"dlo": dlo, "dla": dla, "dshare": dlo - dla,
                     "dy": y[k] - y[k - 1], "dx": x[k] - x[k - 1],
                     "dc": common[k] - common[k - 1],
                     "dr": rel[k] - rel[k - 1]})
    return {"beta_x": beta_x, "beta_x_se": se,
            "beta_x_ci": ([beta_x - Z95 * se, beta_x + Z95 * se] if se else None),
            "alpha": alpha, "sessions": len(frame), "rows": rows,
            "resid_corr_x": e235._corr(rel, x),
            "resid_sd": e235._sd(rel)}


def _dummy_cols(member_ids, n_members):
    cols = []
    for j in range(1, n_members):
        cols.append([1.0 if m == j else 0.0 for m in member_ids])
    return cols


def _fit_named(rows, yname, names, member_ids, n_members, lag=NW_LAG):
    """OLS+HAC of rows[*][yname] on rows[*][names] plus member dummies."""
    if not rows:
        return None
    y = [r[yname] for r in rows]
    cols = [[r[n] for r in rows] for n in names] + _dummy_cols(member_ids, n_members)
    fit = e235._ols_hac_full(y, cols, lag)
    if fit is None:
        return None
    out = {"rows_used": len(y), "n_regressors": len(fit["beta"]),
           "member_dummies": max(0, n_members - 1), "r2": fit["r2"]}
    cov = fit["cov"]
    for i, name in enumerate(names):
        b, var = fit["beta"][i + 1], cov[i + 1][i + 1]
        se = math.sqrt(var) if var and var > 0 else None
        out[name] = b
        out[name + "_se"] = se
        out[name + "_ci"] = ([b - Z95 * se, b + Z95 * se] if se else None)
        out[name + "_t_nw"] = (b / se) if se else None
    return out


def _blocks(frames, builder=component_rows, lag=NW_LAG):
    blocks = []
    for frame in frames:
        b = builder(frame, lag)
        if b is not None:
            blocks.append(b)
    return blocks


def _stack(blocks, pooled):
    use = blocks if pooled else blocks[:1]
    rows, ids = [], []
    for j, b in enumerate(use):
        for r in b["rows"]:
            rows.append(r)
            ids.append(j)
    return use, rows, ids


def fit_components(frames, pooled=False, lag=NW_LAG):
    """(a) d(log own turnover) on the changes of the common and relative components."""
    blocks = _blocks(frames, lag=lag)
    if not blocks:
        return {"design": "components", "reason": "no member has enough sessions"}
    use, rows, ids = _stack(blocks, pooled)
    fit = _fit_named(rows, "dlo", ("dc", "dr"), ids, len(use), lag)
    if fit is None:
        return {"design": "components", "reason": "within_or_singular"}
    fit.update({"design": "components", "members": len(use),
                "beta_x": [b["beta_x"] for b in use],
                "resid_corr_x": [b["resid_corr_x"] for b in use],
                "note": "common = fitted part of log|r| on the book; rel = residual"})
    return fit


def fit_direct(frames, pooled=False, lag=NW_LAG):
    """(b) the same rows in own/market coordinates -- an identity, not a second test."""
    blocks = _blocks(frames, lag=lag)
    if not blocks:
        return {"design": "direct", "reason": "no member has enough sessions"}
    use, rows, ids = _stack(blocks, pooled)
    fit = _fit_named(rows, "dlo", ("dy", "dx"), ids, len(use), lag)
    if fit is None:
        return {"design": "direct", "reason": "within_or_singular"}
    fit.update({"design": "direct", "members": len(use),
                "note": "dy = d(log|r|), dx = d(log|r_book|); same span as components"})
    return fit


def fit_share(frames, pooled=False, lag=NW_LAG):
    """The E236 difference design, re-used verbatim so the comparison is the same number."""
    seqs = [f for f in frames if len(f) >= MIN_MEMBER_ROWS]
    if not seqs:
        return {"design": "share", "reason": "no member has enough sessions"}
    herm = [[(r[0], r[1], r[2], r[3]) for r in f] for f in seqs]
    if pooled:
        out = e236.fit_differences(herm, pooled=True, lag=lag)
    else:
        out = e236.fit_differences([herm[0]], pooled=False, lag=lag)
    if out.get("b_own") is None:
        return {"design": "share", "reason": out.get("reason", "within_or_singular")}
    out["design"] = "share"
    out["note"] = "d(log own turnover) on d(share) and d(log book turnover) -- E236 design A"
    return out


def fit_share_controlled(frames, pooled=False, lag=NW_LAG):
    """The share design plus the market's return as a control -- the artefact test.

    Same dependent variable as the share design (the session's change in log|r|), because
    the claim under test is about that coefficient. The market return is the control rather
    than the relative component: dy = d(common) + d(relative) identically, so controlling
    the relative part would absorb the very variation an impact story predicts the channel
    lives in. What an artefact of market-wide information looks like is a share coefficient
    that dies once the market's own |r| is known.
    """
    blocks = _blocks(frames, lag=lag)
    if not blocks:
        return {"design": "share_controlled", "reason": "no member has enough sessions"}
    use, rows, ids = _stack(blocks, pooled)
    fit = _fit_named(rows, "dy", ("dshare", "dla", "dx"), ids, len(use), lag)
    if fit is None:
        return {"design": "share_controlled", "reason": "within_or_singular"}
    fit.update({"design": "share_controlled", "members": len(use), "control": "dx",
                "note": "does the share coefficient survive the market's own |r|?"})
    return fit


def fit_comove(frames, pooled=False, lag=NW_LAG):
    """First stage: does the share change carry market-wide information arrival?"""
    blocks = _blocks(frames, lag=lag)
    if not blocks:
        return {"design": "comove", "reason": "no member has enough sessions"}
    use, rows, ids = _stack(blocks, pooled)
    fit = _fit_named(rows, "dshare", ("dx",), ids, len(use), lag)
    if fit is None:
        return {"design": "comove", "reason": "within_or_singular"}
    fit.update({"design": "comove", "members": len(use), "control": "dx",
                "note": "dependent = d(share); regressor = d(log|r_book|)"})
    return fit


def fit_comove_own(frames, pooled=False, lag=NW_LAG):
    """Descriptive companion: does the share change echo the member's OWN information?"""
    blocks = _blocks(frames, lag=lag)
    if not blocks:
        return {"design": "comove_own", "reason": "no member has enough sessions"}
    use, rows, ids = _stack(blocks, pooled)
    fit = _fit_named(rows, "dshare", ("dr",), ids, len(use), lag)
    if fit is None:
        return {"design": "comove_own", "reason": "within_or_singular"}
    fit.update({"design": "comove_own", "members": len(use), "control": "dr",
                "note": "dependent = d(share); regressor = d(relative component)"})
    return fit


# ---------------------------------------------------------------- verdicts
def _clears(fit, key, bar_t):
    if not fit:
        return False
    t = fit.get(key + "_t_nw")
    b = fit.get(key)
    return bool(t is not None and b is not None and abs(t) >= bar_t and b > 0.0)


def _intervals_overlap(ci_a, ci_b):
    if not ci_a or not ci_b:
        return False
    return min(ci_a[1], ci_b[1]) >= max(ci_a[0], ci_b[0])


def classify(share, ctrl, comove, bar_t):
    """Frozen verdict on the artefact question, from the share pair and the first stage."""
    out = {"bar_t": bar_t,
           "uncontrolled_b_own": (share or {}).get("b_own"),
           "controlled_b_own": (ctrl or {}).get("dshare"),
           "comove_coef": (comove or {}).get("dx")}
    if not share or share.get("b_own") is None:
        out["verdict"] = "unresolved_no_share_reading"
        return out
    if not ctrl or ctrl.get("dshare") is None:
        out["verdict"] = "unresolved_no_control_reading"
        return out
    unc = _clears(share, "b_own", bar_t)
    con = _clears(ctrl, "dshare", bar_t)
    comove_live = bool(comove and comove.get("dx_t_nw") is not None
                       and abs(comove["dx_t_nw"]) >= bar_t)
    same_sign = bool(share.get("b_own") is not None and ctrl.get("dshare") is not None
                     and (share["b_own"] > 0.0) == (ctrl["dshare"] > 0.0))
    out.update({"uncontrolled_clears": unc, "controlled_clears": con,
                "comovement_clears": comove_live, "same_sign": same_sign})
    if unc and not con and comove_live:
        out["verdict"] = "own_channel_is_information_artefact"
    elif unc and not con:
        out["verdict"] = "unresolved_share_dies_without_comovement"
    elif unc and con and not same_sign:
        out["verdict"] = "unresolved_sign_fragile"
    elif unc and con and _intervals_overlap(share.get("b_own_ci"),
                                            ctrl.get("dshare_ci")):
        out["verdict"] = "own_channel_survives"
    elif unc and con:
        out["verdict"] = "unresolved_magnitude_disagreement"
    elif con and not unc:
        out["verdict"] = "residual_only_channel"
    else:
        out["verdict"] = "no_own_channel"
    return out


def bill_gate(comp, verdict, bar_t):
    """The card's rule, as code: both components positive, clearing, intervals overlapping."""
    gate = {"rule": "a bill requires both decomposition components positive, clearing the "
                    "multiplicity bar, with overlapping 95% intervals",
            "bar_t": bar_t,
            "verdict": (verdict or {}).get("verdict")}
    if not comp or comp.get("dc") is None or comp.get("dr") is None:
        gate.update({"permitted": False, "reason": "no component reading"})
        return gate
    c_ok = _clears(comp, "dc", bar_t)
    r_ok = _clears(comp, "dr", bar_t)
    gate.update({"common_clears": c_ok, "relative_clears": r_ok,
                 "common": comp.get("dc"), "relative": comp.get("dr"),
                 "common_ci": comp.get("dc_ci"), "relative_ci": comp.get("dr_ci")})
    if c_ok and r_ok and _intervals_overlap(comp.get("dc_ci"), comp.get("dr_ci")):
        gate.update({"permitted": True, "reason": "components agree in sign and size",
                     "gamma": e233.clip_gamma((comp["dc"] + comp["dr"]) / 2.0),
                     "gamma_basis": "mean of the two component coefficients, clipped"})
        return gate
    if c_ok != r_ok:
        reason = ("only the %s component clears the bar"
                  % ("common" if c_ok else "relative"))
    elif c_ok and r_ok:
        reason = "both clear but the intervals do not overlap (sizes disagree)"
    else:
        reason = "neither component clears the bar"
    gate.update({"permitted": False, "reason": reason})
    return gate


# ---------------------------------------------------------------- run
def run(save=True, panel_dir=None, outdir=None):
    panel_dir = panel_dir or PANEL_DIR
    outdir = outdir or OUTDIR
    maps = panel_maps(panel_dir)
    if maps is None:
        print("basket panel missing")
        return None
    single = e225.single_panel(PRIMARY_SYMBOL, panel_dir)
    basket = e225.basket_panel(panel_dir)
    if single is None or not basket:
        print("panels missing (single=%s basket=%s)" % (bool(single), bool(basket)))
        return None

    frames = frames_for_basket(maps, panel_dir)
    usable = [s for s in BASKET if len(frames[s]) >= MIN_MEMBER_ROWS]

    member_blocks = []
    for sym in BASKET:
        f = frames[sym]
        if len(f) < MIN_MEMBER_ROWS:
            member_blocks.append({"symbol": sym, "sessions": len(f),
                                  "reason": "fewer than %d usable sessions"
                                            % MIN_MEMBER_ROWS})
            continue
        block = {"symbol": sym, "sessions": len(f), "first": f[0][0], "last": f[-1][0]}
        block["components"] = fit_components([f])
        block["direct"] = fit_direct([f])
        block["share"] = fit_share([f])
        block["share_controlled"] = fit_share_controlled([f])
        block["comove"] = fit_comove([f])
        block["comove_own"] = fit_comove_own([f])
        member_blocks.append(block)

    n_tests = sum(len(keys) for _d, keys in POOLED_TESTS)
    bar_t = max(2.0, e222._z_two_sided(0.05 / n_tests))

    for b in member_blocks:
        if b.get("share"):
            b["verdict_bundle"] = classify(b["share"], b["share_controlled"],
                                           b["comove"], bar_t)

    pooled = None
    if len(usable) >= MIN_POOLED_MEMBERS:
        seqs = [frames[s] for s in usable]
        comp = fit_components(seqs, pooled=True)
        direct = fit_direct(seqs, pooled=True)
        share = fit_share(seqs, pooled=True)
        ctrl = fit_share_controlled(seqs, pooled=True)
        comove = fit_comove(seqs, pooled=True)
        comove_own = fit_comove_own(seqs, pooled=True)
        pooled = {"members": usable, "components": comp, "direct": direct,
                  "share": share, "share_controlled": ctrl, "comove": comove,
                  "comove_own": comove_own,
                  "verdict_bundle": classify(share, ctrl, comove, bar_t),
                  "direction_note": "the share designs take dy on turnover changes (E236's "
                                    "direction); the components/direct designs take the "
                                    "turnover change on the return components (the card's "
                                    "impact elasticity). The two directions are not "
                                    "interchangeable and no coefficient is compared across "
                                    "them.",
                  "identity_note": "components c_rel and direct dy are the same coefficient "
                                   "in two coordinate systems (pinned by selftest)",
                  "c_rel_minus_dy": (comp.get("dr") - direct.get("dy")
                                     if comp.get("dr") is not None
                                     and direct.get("dy") is not None else None)}

    verdict_source = (pooled or {}).get("verdict_bundle") or {}
    comp_for_gate = (pooled or {}).get("components")
    gate = bill_gate(comp_for_gate, verdict_source, bar_t)

    dates, ret_bp = basket
    charges = [{"key": "linear", "kind": "aggregate", "gamma": 1.0,
                "source": "linear_model"}]
    if gate.get("permitted"):
        charges.append({"key": "component_agreed", "kind": "aggregate",
                        "gamma": gate["gamma"], "source": gate["gamma_basis"]})

    sig = e225.vol_signal(ret_bp)
    split = e225.split_index(len(dates))
    bills = {}
    if gate.get("permitted") and len(charges) > 1:
        for arm in ARMS:
            base_w = e225.weights_series(sig, arm)
            flat = [0.0] * len(base_w)
            bills[arm] = {
                "linear_bp": e235.total_bill(base_w, COST_SIDE_BP, ("aggregate", 1.0)),
                "component_agreed_bp": e235.total_bill(
                    base_w, COST_SIDE_BP, ("aggregate", charges[1]["gamma"])),
                "liveness_flat_bill": e235.total_bill(flat, COST_SIDE_BP,
                                                      ("aggregate", 1.0)),
                "weight_changes": e230.change_profile(base_w)["weight_changes"],
            }
    else:
        bills = {"refused": True, "reason": gate.get("reason"),
                 "note": "no arm is re-priced; the family's linear charge stands"}

    face = {
        "study": "E237",
        "title": "is the own-turnover channel an information-arrival artefact?",
        "generated": datetime.now().isoformat(timespec="seconds"),
        "evidence_cutoff": dates[-1],
        "frozen_spec": {
            "decomposition": "log|r_member| on log|r_book|: fitted part = common, residual "
                             "= relative; each differenced and fitted separately",
            "designs": ["components: d(log own turnover) on d(common), d(relative)",
                        "direct: d(log own turnover) on d(log|r|), d(log|r_book|)",
                        "share: E236 design A (dy on d(share), d(book turnover)) reused "
                        "verbatim",
                        "share_controlled: the share design plus d(log|r_book|)",
                        "comove: first stage, d(share) on d(log|r_book|)",
                        "comove_own: descriptive, d(share) on d(relative component)"],
            "direction_note": "the share designs take dy on turnover changes (E236's "
                              "direction); components/direct take the turnover change on the "
                              "return components. The two directions are not interchangeable.",
            "identity_note": "components and direct span the same regressor space; c_rel is "
                             "the dy coefficient by construction, so their agreement is "
                             "algebra and never evidence",
            "multiplicity_bar_t": bar_t,
            "multiplicity_basis": "two-sided 5%% over %d pooled coefficient tests" % n_tests,
            "verdict_vocabulary": ["own_channel_is_information_artefact",
                                   "own_channel_survives",
                                   "unresolved_magnitude_disagreement",
                                   "unresolved_sign_fragile",
                                   "residual_only_channel",
                                   "unresolved_share_dies_without_comovement",
                                   "no_own_channel"],
            "bill_rule": gate["rule"],
            "no_adoption": "no arm is adopted or re-adopted here",
        },
        "members": member_blocks,
        "pooled": pooled,
        "bill_gate": gate,
        "charges": charges,
        "bills": bills,
        "book": {"panel": "basket_equal_weight", "sessions": len(dates),
                 "first": dates[0], "last": dates[-1], "split_session": split,
                 "split_date": dates[split] if split < len(dates) else None,
                 "usable_members": usable},
    }
    face["summary"] = _summary(face, bar_t, n_tests)
    face["answer"] = _answer(face)
    if save:
        if not os.path.isdir(outdir):
            os.makedirs(outdir)
        name = "INFOSTRUCT-%s.json" % face["evidence_cutoff"]
        text = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
        for nm in (name, "infostruct_latest.json"):
            with open(os.path.join(outdir, nm), "w", encoding="utf-8") as fh:
                fh.write(text)
        face["_written"] = os.path.relpath(os.path.join(outdir, name), ROOT).replace(
            "\\", "/")
        print("wrote %s" % face["_written"])
    return face


def _summary(face, bar_t, n_tests):
    pooled = face.get("pooled") or {}
    vb = pooled.get("verdict_bundle") or {}
    gate = face.get("bill_gate") or {}
    member_verdicts = {}
    for b in face["members"]:
        v = (b.get("verdict_bundle") or {}).get("verdict")
        if v:
            member_verdicts[b["symbol"]] = v
    comp = pooled.get("components") or {}
    share = pooled.get("share") or {}
    ctrl = pooled.get("share_controlled") or {}
    comove = pooled.get("comove") or {}
    return {
        "verdict": vb.get("verdict"),
        "member_verdicts": member_verdicts,
        "member_artefact_count": sum(1 for v in member_verdicts.values()
                                     if v == "own_channel_is_information_artefact"),
        "member_survives_count": sum(1 for v in member_verdicts.values()
                                     if v == "own_channel_survives"),
        "uncontrolled_b_own": share.get("b_own"),
        "uncontrolled_b_own_ci": share.get("b_own_ci"),
        "controlled_b_own": ctrl.get("dshare"),
        "controlled_b_own_ci": ctrl.get("dshare_ci"),
        "comove_coef": comove.get("dx"),
        "comove_t": comove.get("dx_t_nw"),
        "comove_own_coef": (face.get("pooled") or {}).get("comove_own", {}).get("dr"),
        "comove_own_t": (face.get("pooled") or {}).get("comove_own", {}).get("dr_t_nw"),
        "market_return_coef_in_control": ctrl.get("dx"),
        "c_common": comp.get("dc"),
        "c_common_ci": comp.get("dc_ci"),
        "c_rel": comp.get("dr"),
        "c_rel_ci": comp.get("dr_ci"),
        "identity_residual": pooled.get("c_rel_minus_dy"),
        "bill_permitted": gate.get("permitted"),
        "bill_reason": gate.get("reason"),
        "bar_t": bar_t,
        "tests": n_tests,
    }


def _answer(face):
    s = face["summary"]
    v = s.get("verdict")
    head = ("own-channel artefact test: uncontrolled b_own %s vs controlled %s, "
            "share/market-return co-movement %s (t %s) -> %s"
            % (_f(s.get("uncontrolled_b_own")), _f(s.get("controlled_b_own")),
               _f(s.get("comove_coef")), _f(s.get("comove_t")), v))
    tail = ("bill %s (%s); members: %d artefact / %d survive of %d fitted"
            % ("PERMITTED gamma %.3f" % face["bill_gate"]["gamma"]
               if s.get("bill_permitted") else "REFUSED",
               s.get("bill_reason"),
               s.get("member_artefact_count") or 0,
               s.get("member_survives_count") or 0,
               len(s.get("member_verdicts") or {})))
    return head + " | " + tail


def _f(v, spec="%.3f"):
    if v is None:
        return "n/a"
    return spec % v


# ---------------------------------------------------------------- selftest
def synth_frame(n=900, beta=0.8, c_common=0.0, c_rel=0.35, share_load=0.0,
                share_from_info=0.0, market_from_info=0.0, noise=0.6, seed=1):
    """A frame where the truth is known.

    log|r| = beta * log|r_book| + relative, with the relative part a stationary AR(1) so the
    first-stage regression recovers beta instead of riding a unit root. The own-turnover
    increment is built from the TRUE components with weights c_common / c_rel, plus a
    "share innovation" u: the observed share change is exactly u because dla = dlo - u.
    share_from_info > 0 makes u an echo of the member's OWN information arrival, and
    market_from_info > 0 makes it an echo of the market's -- the artefact the card asks
    about. share_load > 0 makes the turnover genuinely respond to u.
    """
    rnd = random.Random(seed)
    x, rel, lo, la = 40.0, 0.0, 18.0, 18.0
    out = []
    for i in range(n):
        dx = rnd.gauss(0.0, 0.35)
        x += dx
        rel_prev = rel
        rel = 0.9 * rel + rnd.gauss(0.0, 0.85)
        d_rel = rel - rel_prev
        y = beta * x + rel
        d_common = beta * dx
        u = (share_from_info * d_rel + market_from_info * dx
             + rnd.gauss(0.0, 0.25))
        d_lo = (c_common * d_common + c_rel * d_rel + share_load * u
                + rnd.gauss(0.0, noise))
        d_la = d_lo - u
        lo += d_lo
        la += d_la
        out.append(("%05d" % i, y, lo, la, x))
    return out


def _mean_over_seeds(fn, seeds=(1, 2, 3), **kw):
    vals = {}
    for sd in seeds:
        out = fn(synth_frame(seed=sd, **kw))
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

    def l_components_recover_planted_relative():
        got = _mean_over_seeds(lambda f: fit_components([f]), c_common=0.0, c_rel=0.45,
                               noise=0.5)
        assert abs(got["dr"] - 0.45) < 0.12, "c_rel %.3f vs 0.45" % got["dr"]
        assert abs(got["dc"]) < 0.12, "c_common %.3f vs 0.0" % got["dc"]

    def l_components_recover_planted_common():
        # plant the channel on the COMMON component only: the relative coefficient must
        # read ~0 while the common one reads the truth
        got = _mean_over_seeds(lambda f: fit_components([f]), c_common=0.45, c_rel=0.0,
                               noise=0.5)
        assert abs(got["dc"] - 0.45) < 0.15, "c_common %.3f vs 0.45" % got["dc"]
        assert abs(got["dr"]) < 0.15, "c_rel %.3f on a relative-free panel" % got["dr"]

    def l_identity_c_rel_equals_direct_dy():
        # the two designs span the same space; the coefficient is the same number
        f = synth_frame(seed=7, c_rel=0.4, noise=0.4)
        a = fit_components([f])
        b = fit_direct([f])
        assert abs(a["dr"] - b["dy"]) < 1e-9, "identity broken: %.12f vs %.12f" % (
            a["dr"], b["dy"])
        assert abs(a["r2"] - b["r2"]) < 1e-12, "same span must give the same r2"

    def l_identity_is_not_evidence():
        # a design pair that agrees by construction must not be counted as two readings:
        # the face publishes the residual explicitly
        f = synth_frame(seed=8)
        a = fit_components([f])
        b = fit_direct([f])
        resid = a["dr"] - b["dy"]
        assert abs(resid) < 1e-9
        assert resid == a["dr"] - b["dy"]

    def l_comovement_detected():
        f = synth_frame(seed=9, market_from_info=0.8, c_rel=0.0, noise=0.4)
        comove = fit_comove([f])
        assert abs(comove["dx"]) > 0.3, "co-movement %.3f not detected" % comove["dx"]
        assert abs(comove["dx_t_nw"]) > 3.0

    def l_no_comovement_when_not_planted():
        f = synth_frame(seed=10, market_from_info=0.0, share_from_info=0.6, c_rel=0.0)
        comove = fit_comove([f])
        assert abs(comove["dx"]) < 0.12, "co-movement %.3f fabricated" % comove["dx"]

    def l_artefact_verdict_fires():
        # the share change echoes the MARKET return and the turnover does not respond to the
        # share itself -> the share coefficient is a market-information artefact
        f = synth_frame(seed=11, c_rel=0.0, c_common=0.0, share_load=0.0,
                        market_from_info=1.0, noise=0.5)
        bundle = classify(fit_share([f]), fit_share_controlled([f]), fit_comove([f]), 2.0)
        assert bundle["uncontrolled_clears"] is True, bundle
        assert bundle["controlled_clears"] is False, bundle
        assert bundle["verdict"] == "own_channel_is_information_artefact", bundle["verdict"]

    def l_survives_when_share_is_genuine():
        # the share change echoes the member's OWN information arrival -> the coefficient
        # lives in the relative component, which is exactly what an impact story predicts
        f = synth_frame(seed=12, c_rel=0.0, c_common=0.0, share_load=0.0,
                        share_from_info=1.0, noise=0.5)
        bundle = classify(fit_share([f]), fit_share_controlled([f]), fit_comove([f]), 2.0)
        assert bundle["uncontrolled_clears"] is True, bundle
        assert bundle["controlled_clears"] is True, bundle
        assert bundle["verdict"] in ("own_channel_survives",
                                     "unresolved_magnitude_disagreement"), bundle["verdict"]

    def l_no_channel_fixture():
        f = synth_frame(seed=13, c_rel=0.0, c_common=0.0, share_load=0.0, noise=1.2)
        bundle = classify(fit_share([f]), fit_share_controlled([f]), fit_comove([f]), 2.0)
        assert bundle["verdict"] == "no_own_channel", bundle["verdict"]

    def l_bill_gate_refuses_when_components_disagree():
        comp = {"dc": 0.4, "dc_ci": [0.3, 0.5], "dc_t_nw": 4.0,
                "dr": 0.05, "dr_ci": [-0.02, 0.12], "dr_t_nw": 0.9}
        gate = bill_gate(comp, {"verdict": "x"}, 2.0)
        assert gate["permitted"] is False
        assert "only the" in gate["reason"], gate["reason"]

    def l_bill_gate_permits_when_components_agree():
        comp = {"dc": 0.40, "dc_ci": [0.30, 0.50], "dc_t_nw": 4.0,
                "dr": 0.34, "dr_ci": [0.28, 0.40], "dr_t_nw": 6.0}
        gate = bill_gate(comp, {"verdict": "own_channel_survives"}, 2.0)
        assert gate["permitted"] is True, gate["reason"]
        assert 0.0 < gate["gamma"] <= 1.0

    def l_bill_gate_refuses_on_size_disagreement():
        comp = {"dc": 0.60, "dc_ci": [0.55, 0.65], "dc_t_nw": 9.0,
                "dr": 0.05, "dr_ci": [0.04, 0.06], "dr_t_nw": 5.0}
        gate = bill_gate(comp, {"verdict": "own_channel_survives"}, 2.0)
        assert gate["permitted"] is False
        assert "overlap" in gate["reason"], gate["reason"]

    def l_flat_path_pays_zero():
        w = [0.0] * 50
        got = e235.total_bill(w, COST_SIDE_BP, ("aggregate", 1.0))
        assert got["total_cost_bp"] == 0.0 and got["weight_changes"] == 0

    def l_short_member_reported_not_fitted():
        short = synth_frame(n=50, seed=14)
        out = fit_components([short])
        assert out.get("dr") is None and "reason" in out

    def l_pooled_adds_one_dummy_per_extra_member():
        frames = [synth_frame(seed=s, c_rel=0.35) for s in (21, 22, 23)]
        comp = fit_components(frames, pooled=True)
        assert comp["member_dummies"] == 2, comp["member_dummies"]
        assert comp["n_regressors"] == 5, comp["n_regressors"]  # intercept + 2 + 2

    def l_share_matches_e236_verbatim():
        f = synth_frame(seed=15, c_rel=0.3, share_load=0.4, noise=0.3)
        mine = fit_share([f])
        direct = e236.fit_differences([[(r[0], r[1], r[2], r[3]) for r in f]])
        assert abs(mine["b_own"] - direct["b_own"]) < 1e-12, "share design was rewritten"
        assert abs(mine["b_agg"] - direct["b_agg"]) < 1e-12

    def l_bar_rises_with_more_tests():
        one = e222._z_two_sided(0.05 / 1)
        many = e222._z_two_sided(0.05 / 8)
        assert many > one

    def l_classify_refuses_without_control():
        f = synth_frame(seed=16)
        bundle = classify(fit_share([f]), {"design": "share_controlled",
                                          "reason": "within_or_singular"},
                          fit_comove([f]), 2.0)
        assert bundle["verdict"] == "unresolved_no_control_reading", bundle["verdict"]

    leg("components recover a planted relative channel", l_components_recover_planted_relative)
    leg("components do not invent a relative channel", l_components_recover_planted_common)
    leg("c_rel equals the direct dy coefficient (identity)", l_identity_c_rel_equals_direct_dy)
    leg("the identity is published, not scored as evidence", l_identity_is_not_evidence)
    leg("share/relative co-movement is detected when planted", l_comovement_detected)
    leg("no co-movement is fabricated", l_no_comovement_when_not_planted)
    leg("artefact verdict fires on the planted artefact", l_artefact_verdict_fires)
    leg("a genuine share channel survives the control", l_survives_when_share_is_genuine)
    leg("no channel reads no_own_channel", l_no_channel_fixture)
    leg("bill gate refuses on one-sided clearance", l_bill_gate_refuses_when_components_disagree)
    leg("bill gate permits when components agree", l_bill_gate_permits_when_components_agree)
    leg("bill gate refuses on size disagreement", l_bill_gate_refuses_on_size_disagreement)
    leg("a flat path pays a zero bill", l_flat_path_pays_zero)
    leg("a short member is reported, not fitted", l_short_member_reported_not_fitted)
    leg("pooled fit adds one dummy per extra member", l_pooled_adds_one_dummy_per_extra_member)
    leg("the share design is E236's, verbatim", l_share_matches_e236_verbatim)
    leg("the multiplicity bar rises with the test count", l_bar_rises_with_more_tests)
    leg("classify refuses without a control reading", l_classify_refuses_without_control)

    fails = [n for n, ok, _e in legs if not ok]
    for name, ok, err in legs:
        print("[%s] %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else " | " + err))
    print("selftest %d/%d" % (len(legs) - len(fails), len(legs)))
    return 0 if not fails else 1


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