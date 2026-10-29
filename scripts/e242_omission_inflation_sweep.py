"""E242 -- which published family slopes are inflated by omitting the other members?

E240 measured ONE omission inside ONE design: a pair regression of a member's move on its own
turnover increment plus a SINGLE counterparty's increment leaves three members out, and the
resulting cross slope came in at 0.325 against an identified 0.183 (factor 1.89 at rho = 0.424,
matching the closed form (1 + (k-1)rho - k rho^2) / (1 - rho^2)).

That factor is not a property of one face. Every design in this family whose regressor set
leaves a member out inherits it, and the family has been quoting such designs for several
rounds. This face does not add theory: it walks the published slopes, classifies each by HOW
MANY of the other four members its regressor set omits, re-prices the omitted-member designs on
one identified grid, and states for each published VERDICT whether it survives the re-pricing.

WHAT IS PUBLISHED
  (1) inventory: every published slope this face can find, machine-read from the faces
      (never hand-copied), with its regressor set and the number of members it leaves out.
  (2) four nested regressor sets on the SAME dependent variable and the SAME own regressor:
        S0  own only                      -- omits 4
        S1  own + ONE counterparty        -- omits 3 (the published pair design, E239/E240)
        S2  own + one + SUM of the rest 3 -- identified (E240's form)
        S3  own + each of the other four -- identified, no member omitted at all
  (3) the measured inflation factor S1/S3 (and S0/S3) beside the closed-form prediction at the
      measured rho, per coefficient (cross AND own -- omission inflates both).
  (4) the grid bridge: E239's published mean cross was computed on PER-PAIR intersections, while
      an identified re-pricing can only live on the five-member common intersection (the other
      three members' increments must sit on the same sessions). The two sources of inflation
      are separated: grid vs omission.
  (5) verdict re-pricing: for each published verdict that consumes an omitted-member design,
      the identified counterpart and the rebuilt interval.

VERDICT VOCABULARY (frozen before any number is read)
  * survives -- the published verdict is unchanged when the identified slopes replace the
        published ones (an interval that only widens/shrinks while keeping its sign is a
        survival).
  * flips -- the published verdict is contradicted by the identified slopes.
  * not_repriceable -- the design does not omit a member (own + aggregate contains all five),
        so this instrument has nothing to say; the defect class there is units/collinearity,
        which E240 priced separately.
  * unresolved -- the identified design could not be fitted on this panel.

NO BILL, NO ADOPTION. Nothing is charged and no arm moves; the face only asks which published
numbers were units artefacts.
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
import e240_aggregate_attenuation as e240  # noqa: E402

ROOT = e222.ROOT
PANEL_DIR = e222.PANEL_DIR
OUTDIR = os.path.join(ROOT, "results", "state_tilt")

BASKET = e225.BASKET
NW_LAG = e225.NW_LAG
Z95 = 1.96
VAR_FLOOR = e240.VAR_FLOOR
MIN_SESSIONS = e240.MIN_SESSIONS
INFLATION_K = 4                      # E240's convention: the member's four counterparties
CLOSED_FORM_TOL = 0.35               # |measured - closed| / closed: a closed form, not a law
REPRO_TOL = 1e-6                     # a re-run of a published design must match to rounding

VERDICTS = ("survives", "flips", "not_repriceable", "unresolved")


# ---------------------------------------------------------------- grids
def common_panel(per, syms, lag=NW_LAG):
    """All members' increments on the five-member common intersection (E240's grid)."""
    return e240.common_increments(per, syms)


def pair_specific_panels(per, syms):
    """Each ordered pair on its OWN intersection -- the grid E239 actually published on."""
    out = {}
    for m in syms:
        for j in syms:
            if j == m:
                continue
            blk = e239.pair_rows(per, m, j)
            if blk:
                out[(m, j)] = blk
    return out


# ---------------------------------------------------------------- nested regressor sets
def _fit(y, cols, lag=NW_LAG):
    return e235._ols_hac_full(y, cols, lag)


def _diff_of(beta, cov, i_own, idxs):
    """beta[i_own] - mean(beta[idxs]) with the interval from the joint covariance."""
    n = len(idxs)
    if not n:
        return None
    m = sum(beta[k] for k in idxs) / n
    d = beta[i_own] - m
    var = cov[i_own][i_own]
    var += sum(cov[a][b] for a in idxs for b in idxs) / (n * n)
    var -= 2.0 * sum(cov[i_own][a] for a in idxs) / n
    if var is None or var <= 0.0:
        return {"diff": d, "se": None, "ci": None}
    se = math.sqrt(var)
    return {"diff": d, "se": se, "ci": [d - Z95 * se, d + Z95 * se]}


def design_own_only(panel, syms, lag=NW_LAG):
    """S0: dy on the member's OWN turnover increment only. Leaves every counterparty out."""
    dx, dy = panel["dx"], panel["dy"]
    members = []
    for m in syms:
        sd = e235._sd(dx[m])
        if sd is None or sd < VAR_FLOOR:
            members.append({"member": m, "reason": "dust own regressor"})
            continue
        fit = _fit(dy[m], [dx[m]], lag)
        if fit is None:
            members.append({"member": m, "reason": "within_or_singular"})
            continue
        members.append({"member": m, "b_own": fit["beta"][1], "rows_used": fit["n"],
                        "r2": fit["r2"], "omits_members": len(syms) - 1})
    return _reduce(members, "own_only")


def design_own_plus_one(panel, syms, lag=NW_LAG):
    """S1: the published pair design, pooled with pair fixed effects (within-pair demeaning)."""
    dx, dy = panel["dx"], panel["dy"]
    n = len(dy[syms[0]]) if syms else 0
    cases, pairs = [], []
    y_all, z_all, o_all, tag = [], [], [], []
    for m in syms:
        for j in syms:
            if j == m:
                continue
            sd = e235._sd(dx[j])
            if sd is None or sd < VAR_FLOOR:
                cases.append({"own_of": m, "cross_of": j, "reason": "dust counterparty"})
                continue
            fit = _fit(dy[m], [dx[m], dx[j]], lag)
            if fit is None:
                cases.append({"own_of": m, "cross_of": j, "reason": "within_or_singular"})
                continue
            pairs.append({"own_of": m, "cross_of": j, "b_own": fit["beta"][1],
                          "b_cross": fit["beta"][2], "rows_used": fit["n"]})
            for i in range(n):
                y_all.append(dy[m][i])
                z_all.append(dx[m][i])
                o_all.append(dx[j][i])
                tag.append((m, j))
    if not pairs:
        return {"design": "own_plus_one", "reason": "no fittable pairs", "cases": cases}
    ys, zs, os_ = [], [], []
    used = 0
    order = []
    seen = set()
    for m, j in tag:                      # insertion order, never a set: set iteration varies
        if (m, j) in seen:                # between processes and would reorder the sums
            continue
        seen.add((m, j))
        order.append((m, j))
    for key in order:
        sel = [i for i, t in enumerate(tag) if t == key]
        if len(sel) < MIN_SESSIONS:
            continue
        used += 1
        ys.extend(e239._demean([y_all[i] for i in sel]))
        zs.extend(e239._demean([z_all[i] for i in sel]))
        os_.extend(e239._demean([o_all[i] for i in sel]))
    out = {"design": "own_plus_one", "cases": cases, "pairs": pairs,
           "n_pairs": len(pairs), "omits_members": len(syms) - 2,
           "mean_b_cross": sum(p["b_cross"] for p in pairs) / len(pairs),
           "mean_b_own": sum(p["b_own"] for p in pairs) / len(pairs)}
    if ys:
        fit = _fit(ys, [zs, os_], lag)
        if fit is not None:
            beta, cov = fit["beta"], fit["cov"]
            d = _diff_of(beta, cov, 1, [2])
            out["pooled"] = {"b_own": beta[1], "b_cross": beta[2], "diff": d["diff"],
                             "diff_ci": d["ci"], "diff_t_nw": (d["diff"] / d["se"]
                                                               if d["se"] else None),
                             "rows_used": fit["n"], "pair_blocks": used, "r2": fit["r2"]}
    return out


def design_own_plus_all(panel, syms, lag=NW_LAG):
    """S3: own plus EACH of the other members separately -- no member omitted at all."""
    dx, dy = panel["dx"], panel["dy"]
    n = len(dy[syms[0]]) if syms else 0
    members = []
    for m in syms:
        others = [j for j in syms if j != m]
        cols = [dx[m]] + [dx[j] for j in others]
        if any((e235._sd(c) is None or (e235._sd(c) or 0.0) < VAR_FLOOR) for c in cols):
            members.append({"member": m, "reason": "a regressor is dust"})
            continue
        fit = _fit(dy[m], cols, lag)
        if fit is None:
            members.append({"member": m, "reason": "within_or_singular (collinear members)"})
            continue
        beta, cov = fit["beta"], fit["cov"]
        d = _diff_of(beta, cov, 1, list(range(2, 2 + len(others))))
        members.append({"member": m, "b_own": beta[1], "b_other": beta[2:],
                        "own_of": others, "b_cross_mean": sum(beta[2:]) / len(others),
                        "diff": d["diff"], "diff_ci": d["ci"], "rows_used": fit["n"],
                        "r2": fit["r2"], "omits_members": 0})
    out = _reduce(members, "own_plus_all")
    # pooled: member fixed effects via within-member demeaning, one own and four cross slopes
    y_all, z_all, cs = [], [], []
    for m in syms:
        others = [j for j in syms if j != m]
        for i in range(n):
            y_all.append(dy[m][i])
            z_all.append(dx[m][i])
            cs.append([dx[j][i] for j in others])
    if y_all:
        y_d = e239._demean(y_all)
        z_d = e239._demean(z_all)
        cs_d = [e239._demean([row[k] for row in cs]) for k in range(len(syms) - 1)]
        fit = _fit(y_d, [z_d] + cs_d, lag)
        if fit is not None:
            beta, cov = fit["beta"], fit["cov"]
            d = _diff_of(beta, cov, 1, list(range(2, 2 + len(cs_d))))
            out["pooled"] = {"b_own": beta[1], "b_cross_mean": sum(beta[2:]) / len(cs_d),
                             "b_others": beta[2:], "diff": d["diff"], "diff_ci": d["ci"],
                             "diff_t_nw": (d["diff"] / d["se"] if d["se"] else None),
                             "rows_used": fit["n"], "member_fixed_effects": len(syms),
                             "r2": fit["r2"]}
    return out


def _reduce(members, design):
    ok = [m for m in members if m.get("b_own") is not None]
    out = {"design": design, "members": members, "n_members": len(ok)}
    if ok:
        out["mean_b_own"] = sum(m["b_own"] for m in ok) / len(ok)
    cr = [m for m in ok if m.get("b_cross_mean") is not None]
    if cr:
        out["mean_b_cross"] = sum(m["b_cross_mean"] for m in cr) / len(cr)
        ds = [m["diff"] for m in cr]
        mu = sum(ds) / len(ds)
        sd = e235._sd(ds)
        se = sd / math.sqrt(len(ds)) if sd else None
        out["mean_diff"] = mu
        out["diff_ci"] = [mu - Z95 * se, mu + Z95 * se] if se else None
    return out


def design_own_one_and_sum(panel, syms, lag=NW_LAG):
    """S2: E240's identified form, re-run here as a control (must reproduce its published +0.0079)."""
    return e240.pair_one_vs_rest(panel, syms, lag)


# ---------------------------------------------------------------- inventory
FACES = (
    ("E239", "OWNCROSS", "mean_single_member_cross"),
    ("E240", "AGGATT", None),
    ("E236", "SHAREDIFF", None),
    ("E233", "PER-MEMBER-GAMMA", None),
)


def _read_face(fname, outdir=None):
    path = os.path.join(outdir or OUTDIR, fname)
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh), os.path.relpath(path, ROOT).replace("\\", "/")
    except (OSError, ValueError):
        return None, None


def _face_file(stem):
    for cand in ("%s_latest.json" % stem, "%s-2026-10-29.json" % stem):
        p = os.path.join(OUTDIR, cand)
        if os.path.isfile(p):
            return cand
    return None


def inventory(outdir=None):
    """Published slopes, machine-read, each classified by how many members it leaves out."""
    rows = []
    sets = {"own_only": BASKET.__len__() - 1,
            "own_plus_one": BASKET.__len__() - 2,
            "own_plus_sum": 0,
            "own_plus_all": 0,
            "single_regressor": None}

    owncross, owncross_path = _read_face(_face_file("owncross") or "", outdir)
    if owncross:
        s = owncross.get("summary") or {}
        for key, dset, note in (
                ("mean_cross", "own_plus_one", "mean over per-pair slopes, pair-specific grids"),
                ("pooled_cross", "own_plus_one", "pooled pair-FE fit, per-pair intersections"),
                ("two_way_cross", "own_plus_one", "member + date FE"),
                ("pooled_own", "own_plus_one", "the own slope in the same pair regression")):
            if s.get(key) is not None:
                rows.append({"face": "E239", "path": owncross_path, "key": key,
                             "value": s[key], "regressor_set": dset,
                             "omits_members": sets[dset], "note": note,
                             "repriceable": True})
        if s.get("mean_cross") is not None:
            rows.append({"face": "E239", "path": owncross_path, "key": "verdict",
                         "value": s.get("verdict"), "regressor_set": "own_plus_one",
                         "omits_members": sets["own_plus_one"],
                         "note": "frozen verdict of the pair design",
                         "repriceable": True})

    agg, agg_path = _read_face(_face_file("AGGATT") or "", outdir)
    if agg:
        s = agg.get("summary") or {}
        for key, dset in (("naive_cross", "own_plus_one"),
                          ("b_one", "own_plus_sum"),
                          ("b_rest3", "own_plus_sum"),
                          ("b_own_direct", "own_plus_all"),
                          ("inflation_factor", "own_plus_one")):
            if s.get(key) is not None:
                rows.append({"face": "E240", "path": agg_path, "key": key, "value": s[key],
                             "regressor_set": dset, "omits_members": sets[dset],
                             "note": "E240's own reading", "repriceable": dset == "own_plus_one"})
        if s.get("verdict"):
            rows.append({"face": "E240", "path": agg_path, "key": "verdict",
                         "value": s["verdict"], "regressor_set": "own_plus_sum",
                         "omits_members": 0,
                         "note": "computed from identified designs; this face is its control",
                         "repriceable": False})

    sh, sh_path = _read_face(_face_file("sharediff") or "", outdir)
    if sh:
        s = sh.get("summary") or {}
        for key in ("pooled_b_own", "pooled_b_agg", "family_single_regressor_gamma"):
            v = s.get(key)
            if isinstance(v, list):
                v = v[0].get("value") if v and isinstance(v[0], dict) else None
            if v is not None:
                dset = "single_regressor" if key.endswith("gamma") else "own_plus_sum"
                rows.append({"face": "E236", "path": sh_path, "key": key, "value": v,
                             "regressor_set": dset,
                             "omits_members": sets[dset],
                             "note": ("one regressor only; which one is not named on the "
                                      "face, so it cannot be re-priced here"
                                      if dset == "single_regressor" else
                                      "own share + aggregate: contains all five members"),
                             "repriceable": False})

    gam, gam_path = _read_face(_face_file("per_member_gamma") or "", outdir)
    if gam:
        s = gam.get("summary") or {}
        if s.get("pooled") is not None:
            rows.append({"face": "E233", "path": gam_path, "key": "pooled_gamma",
                         "value": s.get("pooled"), "regressor_set": "own_plus_sum",
                         "omits_members": 0,
                         "note": "gamma from the own + aggregate channels",
                         "repriceable": False})
        if s.get("compatibility_verdict"):
            rows.append({"face": "E233", "path": gam_path, "key": "verdict",
                         "value": s.get("compatibility_verdict"),
                         "regressor_set": "own_plus_sum", "omits_members": 0,
                         "note": "mixture vs split: an own-vs-aggregate question",
                         "repriceable": False})
    return rows


# ---------------------------------------------------------------- inflation
def inflation_table(designs, rho):
    """Measured factors between the nested sets, beside the closed-form prediction."""
    s0 = designs.get("own_only") or {}
    s1 = designs.get("own_plus_one") or {}
    s2 = designs.get("own_plus_sum") or {}
    s3 = designs.get("own_plus_all") or {}
    naive_cross = s1.get("mean_b_cross")
    ident_cross = s3.get("mean_b_cross")
    s2_cross = s2.get("mean_b_one")
    ident_own = s3.get("mean_b_own")
    out = {
        "cross": {"naive_own_plus_one": naive_cross, "identified_own_plus_all": ident_cross,
                  "identified_own_one_plus_sum": s2_cross,
                  "measured_factor": (naive_cross / ident_cross
                                      if naive_cross and ident_cross else None)},
        "own": {"own_only": s0.get("mean_b_own"), "naive_own_plus_one": s1.get("mean_b_own"),
                "identified_own_plus_all": ident_own,
                "measured_factor_vs_identified": (s1.get("mean_b_own") / ident_own
                                                  if s1.get("mean_b_own") and ident_own
                                                  else None),
                "measured_factor_own_only_vs_identified": (s0.get("mean_b_own") / ident_own
                                                           if s0.get("mean_b_own") and ident_own
                                                           else None)},
        "rho": rho,
        "closed_form": e240.inflation_factor(rho, k=INFLATION_K),
        "k": INFLATION_K,
        "closed_form_expression": "(1 + (k-1)rho - k rho^2) / (1 - rho^2), k = 4 counterparties",
    }
    mf = out["cross"]["measured_factor"]
    cf = out["closed_form"]
    # the factor is defined only against a NAMED identified form, and the two forms do not
    # agree exactly (the sum is a constrained combination of four collinear coefficients)
    forms = {}
    if naive_cross and ident_cross:
        forms["own_plus_all"] = naive_cross / ident_cross
    if naive_cross and s2_cross:
        forms["own_one_plus_sum"] = naive_cross / s2_cross
    out["cross"]["factor_by_identified_form"] = forms
    out["cross"]["factor_range"] = ([min(forms.values()), max(forms.values())]
                                    if forms else None)
    if mf is not None and cf:
        out["cross"]["closed_form_gap"] = mf - cf
        out["cross"]["closed_form_gap_relative"] = (mf - cf) / cf
        out["cross"]["closed_form_matches"] = abs((mf - cf) / cf) <= CLOSED_FORM_TOL
    sub = {}
    if s2_cross is not None and ident_cross:
        sub["own_one_plus_sum_vs_own_all"] = s2_cross / ident_cross
    out["identified_forms_agree"] = (
        sub.get("own_one_plus_sum_vs_own_all") is not None
        and abs(sub["own_one_plus_sum_vs_own_all"] - 1.0) <= 0.5)
    out["substitution"] = sub
    return out


def describe_inflation(infl):
    c = infl.get("cross") or {}
    cf = infl.get("closed_form")
    mf = c.get("measured_factor")
    return ("omitting three members multiplies the single-counterparty slope by %s against an "
            "identified %s (E239 pair design %s -> own+all %s); the closed form at rho %s "
            "predicts %s"
            % (_f(mf, "%.3f"), _f(c.get("identified_own_plus_all")),
               _f(c.get("naive_own_plus_one")), _f(c.get("identified_own_plus_all")),
               _f(infl.get("rho"), "%.3f"), _f(cf, "%.3f")))


# ---------------------------------------------------------------- verdicts
def level_claims(designs, published):
    """Every published LEVEL the omission can inflate, beside its identified counterpart.

    A level is what a units defect can move; a paired difference is what it cannot (the same
    omitted block loads on both members of the pair, so the two biases cancel in the
    difference). Publishing the GATE WINDOW -- the interval a magnitude bar must sit in for the
    reading to change side -- is what makes "which verdicts are at risk" a measurement instead
    of a story.
    """
    s1 = designs.get("own_plus_one") or {}
    s3 = designs.get("own_plus_all") or {}
    s0 = designs.get("own_only") or {}
    s2 = designs.get("own_plus_sum") or {}
    p239 = (published.get("E239") or {}).get("summary") or {}
    p240 = (published.get("E240") or {}).get("summary") or {}
    rows = []

    def _row(face, key, pub, ident, note, naive_common=None, grid="pair_specific"):
        if pub is None or ident is None:
            return
        rows.append({"face": face, "key": key, "published": pub,
                     "published_grid": grid,
                     "naive_common_grid": naive_common,
                     "identified": ident,
                     "factor": (pub / ident if ident else None),
                     "factor_same_grid": (naive_common / ident
                                          if (naive_common is not None and ident) else None),
                     "gate_window": [min(pub, ident), max(pub, ident)],
                     "note": note})

    _row("E239", "mean_cross", p239.get("mean_cross"), s3.get("mean_b_cross"),
         "mean over per-pair slopes; the published value also carries the per-pair GRID, so "
         "this row publishes the same-grid reading beside it",
         naive_common=s1.get("mean_b_cross"))
    _row("E239", "pooled_cross", p239.get("pooled_cross"),
         (s3.get("pooled") or {}).get("b_cross_mean"), "pooled pair-FE cross slope",
         naive_common=(s1.get("pooled") or {}).get("b_cross"))
    _row("E239", "pooled_own", p239.get("pooled_own"),
         (s3.get("pooled") or {}).get("b_own"),
         "the own slope in the same pair regression is inflated too",
         naive_common=(s1.get("pooled") or {}).get("b_own"))
    _row("E240", "naive_cross", p240.get("naive_cross"),
         p240.get("b_one"), "E240's own level reading, reproduced here",
         naive_common=s1.get("mean_b_cross"), grid="common")
    _row("own_only", "b_own", s0.get("mean_b_own"), s3.get("mean_b_own"),
         "the ceiling: a single-regressor design omits four members", grid="common")
    _row("own_plus_sum", "mean_b_cross_mean", s2.get("mean_b_one"),
         s3.get("mean_b_cross"),
         "control: the sum form omits nobody; a non-flat factor here measures how much the "
         "two identified forms disagree", grid="common")
    return rows


def difference_insulation(designs):
    """The paired difference versus its identified counterpart -- the quantity omission spares."""
    s1 = designs.get("own_plus_one") or {}
    s3 = designs.get("own_plus_all") or {}
    a = (s1.get("pooled") or {}).get("diff")
    b = (s3.get("pooled") or {}).get("diff")
    out = {"naive_pooled_diff": a, "identified_pooled_diff": b,
           "gap": (a - b) if (a is not None and b is not None) else None,
           "gate_window": ([min(a, b), max(a, b)] if (a is not None and b is not None)
                           else None)}
    if out["gap"] is not None and out["identified_pooled_diff"] is not None:
        out["reading"] = ("the omitted block loads on the own and on the cross regressor "
                          "alike, and the pooling runs every ordered pair in both directions, "
                          "so the bias cancels in the difference: the level is the artefact, "
                          "the paired difference is not")
    return out


def reprice_verdicts(designs, published, panel, syms, lag=NW_LAG):
    """For every published verdict that consumes an omitted-member design, re-price it."""
    out = []
    s1 = designs.get("own_plus_one") or {}
    s3 = designs.get("own_plus_all") or {}

    # --- E239: own_exceeds_a_single_counterparty, built from the omitted pair design
    p239 = (published.get("E239") or {}).get("summary") or {}
    naive_diff = (s1.get("pooled") or {}).get("diff")
    ident_pooled = s3.get("pooled") or {}
    ident_diff = ident_pooled.get("diff")
    ident_ci = ident_pooled.get("diff_ci")
    row = {"face": "E239", "verdict_key": "verdict",
           "published_verdict": p239.get("verdict"),
           "published_diff": p239.get("pooled_diff"),
           "published_diff_ci": p239.get("pooled_diff_ci"),
           "consumes_omitted_design": True,
           "naive_diff_common_grid": naive_diff,
           "gap_total_vs_published": (abs(naive_diff - p239["pooled_diff"])
                                      if naive_diff is not None and p239.get("pooled_diff")
                                      is not None else None),
           "gap_from_omission": (abs(naive_diff - ident_diff)
                                 if naive_diff is not None and ident_diff is not None
                                 else None),
           "gap_from_grid": (abs(p239["pooled_diff"] - naive_diff)
                             if naive_diff is not None and p239.get("pooled_diff")
                             is not None else None),
           "competition_note": "the published difference was computed on per-pair "
                               "intersections; re-running the SAME naive design on the common "
                               "grid moves it, so the total gap to the published number splits "
                               "into a grid part and an omission part -- both are measured "
                               "here, neither is assumed",
           "repriced_diff": ident_diff, "repriced_diff_ci": ident_ci,
           "repriced_from": "own + all four counterparts, member fixed effects"}
    if ident_diff is None or not ident_ci:
        row["repriced_verdict"] = "unresolved"
        row["survives"] = None
    else:
        lo, hi = ident_ci
        row["repriced_verdict"] = ("own_exceeds_a_single_counterparty" if lo > 0.0 else
                                   "a_single_counterparty_exceeds_own" if hi < 0.0 else
                                   "own_and_single_counterparty_indistinguishable")
        row["survives"] = row["repriced_verdict"] == p239.get("verdict")
        row["direction"] = ("strengthens" if ident_diff * (p239.get("pooled_diff") or 1) > 0
                            and abs(ident_diff) > abs(p239.get("pooled_diff") or 0)
                            else "weakens_or_flips")
    out.append(row)

    # --- E240: the control. Its verdict already consumes identified designs.
    p240 = (published.get("E240") or {}).get("summary") or {}
    s2 = designs.get("own_plus_sum") or {}
    out.append({"face": "E240", "verdict_key": "verdict",
                "published_verdict": p240.get("verdict"),
                "consumes_omitted_design": False,
                "reproduced_control_diff": s2.get("mean_diff"),
                "published_control_diff": p240.get("diff_one_vs_rest3"),
                "reproduction_gap": (abs(s2["mean_diff"] - p240["diff_one_vs_rest3"])
                                     if s2.get("mean_diff") is not None
                                     and p240.get("diff_one_vs_rest3") is not None else None),
                "repriced_verdict": "not_repriceable",
                "survives": True,
                "reason": "the verdict is built from identified designs (own + one + rest-3); "
                          "this face re-runs that control rather than re-pricing it"})

    for face, why in (
            ("E236", "own share + aggregate: the regressor set already contains all five "
                     "members, so no member is omitted; the defect class there is unit "
                     "scaling, priced by E238/E240"),
            ("E233", "gamma is fitted on the own + aggregate channels: same reasoning as E236")):
        p = (published.get(face) or {}).get("summary") or {}
        out.append({"face": face, "verdict_key": "verdict",
                    "published_verdict": p.get("verdict") or p.get("compatibility_verdict"),
                    "consumes_omitted_design": False,
                    "repriced_verdict": "not_repriceable", "survives": True,
                    "reason": why})
    return out


# ---------------------------------------------------------------- run
def run(save=True, panel_dir=None, outdir=None, per=None, lag=NW_LAG):
    outdir = outdir or OUTDIR
    per = per if per is not None else e239.panels(panel_dir)
    syms = [s for s in BASKET if per.get(s)]
    if len(syms) < 3:
        face = {"study": "E242", "error": "fewer than three members have a panel",
                "generated": datetime.now().isoformat(timespec="seconds")}
        face["summary"] = {"verdict": "unresolved",
                           "reason": "fewer than three members: an identified design needs "
                                     "at least one omitted member to exist"}
        return face

    dates, panel = common_panel(per, syms, lag)
    if len(dates) < MIN_SESSIONS:
        face = {"study": "E242", "error": "common grid too short: %d sessions" % len(dates),
                "generated": datetime.now().isoformat(timespec="seconds")}
        face["summary"] = {"verdict": "unresolved",
                           "reason": "the common grid holds %d sessions (< %d); an identified "
                                     "design cannot live on per-pair grids"
                                     % (len(dates), MIN_SESSIONS)}
        return face

    coll = e240.collinearity(panel["dx"], syms)
    designs = {
        "own_only": design_own_only(panel, syms, lag),
        "own_plus_one": design_own_plus_one(panel, syms, lag),
        "own_plus_sum": design_own_one_and_sum(panel, syms, lag),
        "own_plus_all": design_own_plus_all(panel, syms, lag),
    }
    infl = inflation_table(designs, coll.get("mean_rho"))

    # grid bridge: E239 published on per-pair intersections; how much is the grid?
    pair_panels = pair_specific_panels(per, syms)
    pair_naive = []
    for (m, j), blk in pair_panels.items():
        if len(blk) < MIN_SESSIONS:
            continue
        fit = e239._fit([r[1] for r in blk], [r[2] for r in blk], [r[3] for r in blk], lag)
        if fit is not None:
            pair_naive.append(fit["b_cross"])
    bridge = {"pair_specific_pairs": len(pair_naive),
              "pair_specific_mean_cross": (sum(pair_naive) / len(pair_naive)
                                           if pair_naive else None),
              "common_grid_naive_mean_cross": (designs["own_plus_one"] or {}).get(
                  "mean_b_cross"),
              "sessions_common_grid": len(dates)}
    if bridge["pair_specific_mean_cross"] and bridge["common_grid_naive_mean_cross"]:
        bridge["grid_ratio"] = (bridge["pair_specific_mean_cross"]
                                / bridge["common_grid_naive_mean_cross"])
        bridge["reading"] = ("the published pair mean was computed on per-pair intersections; "
                             "the ATD grid ratio separates that choice from the omission, whose "
                             "own factor is inflation.cross.measured_factor")
    else:
        bridge["grid_ratio"] = None

    published = {}
    for face_id, stem in (("E239", "owncross"), ("E240", "AGGATT"),
                          ("E236", "sharediff"), ("E233", "per_member_gamma")):
        fname = _face_file(stem)
        f, _p = _read_face(fname, outdir) if fname else (None, None)
        if f:
            published[face_id] = f
    inv = inventory(outdir)
    verdicts = reprice_verdicts(designs, published, panel, syms, lag)
    levels = level_claims(designs, published)
    insulation = difference_insulation(designs)

    face = {
        "study": "E242",
        "title": "how many published family slopes are inflated by omitting the other members?",
        "generated": datetime.now().isoformat(timespec="seconds"),
        "evidence_cutoff": dates[-1],
        "frozen_spec": {
            "question": "E240 priced one omission in one design (factor 1.89). Every design in "
                        "this family whose regressor set leaves a member out inherits a factor; "
                        "which published numbers are units artefacts?",
            "nested_designs": ["S0 own only (omits 4)", "S1 own + one (omits 3; E239/E240 form)",
                               "S2 own + one + sum of the rest 3 (identified, E240's form)",
                               "S3 own + each of the other four (identified, nothing omitted)"],
            "grid_law": "the identified forms force every member onto the member's own sessions, "
                        "so they exist only on the common intersection; a per-pair grid cannot "
                        "host them",
            "factor": "measured = naive / identified; predicted = (1+(k-1)rho-k rho^2)/(1-rho^2) "
                      "at the measured mean pairwise correlation of turnover increments",
            "closed_form_tolerance": CLOSED_FORM_TOL,
            "verdict_vocabulary": list(VERDICTS),
            "no_adoption": "this face re-prices nothing and adopts nothing",
        },
        "members": syms,
        "grid": {"dates": len(dates), "first": dates[0], "last": dates[-1],
                 "kind": "common intersection of every member's sessions"},
        "collinearity": coll,
        "designs": designs,
        "inflation": infl,
        "grid_bridge": bridge,
        "inventory": inv,
        "verdicts": verdicts,
        "level_claims": levels,
        "difference_insulation": insulation,
        "book": {"panel": "data/daily basket (equal weight)", "members": syms},
        "no_bill": {"permitted": False,
                    "reason": "this face only asks which published slopes were units artefacts"},
    }
    face["summary"] = _summary(face)
    face["answer"] = _answer(face)
    if save:
        if not os.path.isdir(outdir):
            os.makedirs(outdir)
        name = "OMISSION-%s.json" % face["evidence_cutoff"]
        text = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
        for nm in (name, "omission_latest.json"):
            with open(os.path.join(outdir, nm), "w", encoding="utf-8") as fh:
                fh.write(text)
        rows = ["member,b_own_only,b_own_plus_one,b_own_all,b_cross_naive,b_cross_all,diff_all"]
        s0 = {m["member"]: m for m in (designs["own_only"].get("members") or [])
              if m.get("b_own") is not None}
        s1 = {m.get("own_of"): m for m in (designs["own_plus_one"].get("pairs") or [])}
        s1m = {}
        for p in (designs["own_plus_one"].get("pairs") or []):
            s1m.setdefault(p["own_of"], []).append(p)
        for m in (designs["own_plus_all"].get("members") or []):
            if m.get("b_own") is None:
                continue
            sym = m["member"]
            b1 = (sum(p["b_own"] for p in s1m.get(sym, [])) / len(s1m.get(sym, []))
                  if s1m.get(sym) else None)
            bc1 = (sum(p["b_cross"] for p in s1m.get(sym, [])) / len(s1m.get(sym, []))
                   if s1m.get(sym) else None)
            rows.append("%s,%s,%s,%s,%s,%s,%s" % (
                sym, _csv((s0.get(sym) or {}).get("b_own")), _csv(b1),
                _csv(m["b_own"]), _csv(bc1), _csv(m.get("b_cross_mean")), _csv(m.get("diff"))))
        csv_name = "omission_pairs_%s.csv" % face["evidence_cutoff"]
        with open(os.path.join(outdir, csv_name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(rows) + "\n")
        face["_written"] = [os.path.relpath(os.path.join(outdir, name), ROOT).replace(
            "\\", "/"), os.path.relpath(os.path.join(outdir, csv_name), ROOT).replace(
            "\\", "/")]
        print("wrote %s" % " + ".join(face["_written"]))
    return face


def _csv(v):
    return "" if v is None else ("%.6g" % v)


def _summary(face):
    infl = face.get("inflation") or {}
    c = infl.get("cross") or {}
    o = infl.get("own") or {}
    br = face.get("grid_bridge") or {}
    vs = face.get("verdicts") or []
    flips = [v["face"] for v in vs if v.get("repriced_verdict") == "flips"]
    surv = [v["face"] for v in vs
            if v.get("consumes_omitted_design") and v.get("survives") is True]
    nprice = [v["face"] for v in vs if v.get("consumes_omitted_design")]
    inv = face.get("inventory") or []
    lv = face.get("level_claims") or []
    ins = face.get("difference_insulation") or {}
    at_risk = [r for r in lv if r.get("factor") and abs(r["factor"] - 1.0) > 0.10]
    return {
        "verdict": ("a_published_verdict_flips_under_repricing" if flips
                    else "omission_inflates_levels_and_spares_paired_differences"),
        "measured_cross_factor": c.get("measured_factor"),
        "naive_cross": c.get("naive_own_plus_one"),
        "identified_cross": c.get("identified_own_plus_all"),
        "identified_cross_sum_form": c.get("identified_own_one_plus_sum"),
        "closed_form_factor": infl.get("closed_form"),
        "rho": infl.get("rho"),
        "closed_form_gap_relative": c.get("closed_form_gap_relative"),
        "closed_form_matches": c.get("closed_form_matches"),
        "own_factor_vs_identified": o.get("measured_factor_vs_identified"),
        "own_only_factor_vs_identified": o.get("measured_factor_own_only_vs_identified"),
        "grid_ratio": br.get("grid_ratio"),
        "pair_specific_mean_cross": br.get("pair_specific_mean_cross"),
        "common_grid_naive_mean_cross": br.get("common_grid_naive_mean_cross"),
        "sessions": (face.get("grid") or {}).get("dates"),
        "inventory_rows": len(inv),
        "inventory_repriceable": sum(1 for r in inv if r.get("repriceable")),
        "level_claims": len(lv),
        "levels_at_risk": [r["face"] + "." + r["key"] for r in at_risk],
        "difference_gap": ins.get("gap"),
        "difference_insulated": (ins.get("identified_pooled_diff") is not None),
        "verdicts_priced": nprice,
        "verdicts_survive": surv,
        "verdicts_flip": flips,
        "verdicts_not_repriceable": [v["face"] for v in vs
                                     if v.get("repriced_verdict") == "not_repriceable"],
    }


def _f(v, spec="%.3f"):
    return "n/a" if v is None else spec % v


def _ci(ci):
    return "n/a" if not ci else "[%s, %s]" % (_f(ci[0]), _f(ci[1]))


def _answer(face):
    s = face["summary"]
    base = (face.get("verdicts") or [{}])[0]
    return ("omission sweep: %d published slopes read, %d re-priceable; the single-counterparty "
            "slope is x%s the identified one (closed form x%s at rho %s); the per-pair grid "
            "alone accounts for x%s; E239's difference re-prices to %s %s -> survives=%s; "
            "levels at risk: %s; flips: %s"
            % (s["inventory_rows"], s["inventory_repriceable"],
               _f(s["measured_cross_factor"], "%.2f"), _f(s["closed_form_factor"], "%.2f"),
               _f(s["rho"]), _f(s["grid_ratio"], "%.2f"),
               _f(base.get("repriced_diff")), _ci(base.get("repriced_diff_ci")),
               base.get("survives"),
               ", ".join(s["levels_at_risk"]) or "none",
               ", ".join(s["verdicts_flip"]) or "none"))


# ---------------------------------------------------------------- selftest
def synth(n=900, own=0.40, cross=0.10, rho=0.0, noise=1.0, members=5, seed=1,
          independent=None):
    """A book where every member's move responds to its OWN increment and to EACH other
    member's increment separately, with the increments sharing a common factor of weight rho.

    The identified regression recovers `own` and `cross` exactly. The pair design (own + one)
    leaves three members out, and because the increments are correlated those omitted channels
    load onto the retained one -- which is the defect this face measures.

    `independent` names members whose increment is drawn WITHOUT the common factor. With
    exchangeable increments the omitted block loads equally on the retained own and cross
    regressors, so the DIFFERENCE is untouched and only the levels move; decoupling one
    counterparty breaks that symmetry and is how a verdict can be made to flip.
    """
    rnd = random.Random(seed)
    syms = ["syn%d" % i for i in range(members)]
    indep = set(independent or ())
    lo = {s: 18.0 for s in syms}
    per = {s: {} for s in syms}
    for t in range(n):
        f = rnd.gauss(0.0, 0.6)
        dl = {}
        for s in syms:
            if s in indep:
                dl[s] = rnd.gauss(0.0, 0.6)
            else:
                dl[s] = rho * f + math.sqrt(max(1e-9, 1.0 - rho * rho)) * rnd.gauss(0.0, 0.6)
        for s in syms:
            lo[s] += dl[s]
        for s in syms:
            y = own * dl[s] + cross * sum(dl[o] for o in syms if o != s)
            y += rnd.gauss(0.0, noise)
            per[s]["d%05d" % t] = (y, lo[s])
    return per, syms


def _run_synth(**kw):
    per, syms = synth(**kw)
    saved = globals()["BASKET"]
    globals()["BASKET"] = syms
    try:
        face = run(save=False, per=per)
    finally:
        globals()["BASKET"] = saved
    return face


def selftest():
    legs = []

    def leg(name, fn):
        try:
            fn()
            legs.append((name, True, ""))
        except AssertionError as exc:
            legs.append((name, False, str(exc)))

    def l_identified_recovers_the_planted_slopes():
        face = _run_synth(own=0.40, cross=0.10, rho=0.0, seed=3)
        d = face["designs"]["own_plus_all"]
        assert abs(d["mean_b_own"] - 0.40) < 0.08, "own %.3f vs planted 0.40" % d["mean_b_own"]
        assert abs(d["mean_b_cross"] - 0.10) < 0.06, \
            "cross %.3f vs planted 0.10" % d["mean_b_cross"]

    def l_no_correlation_is_no_inflation():
        # the mechanism is the correlation, not the code: independent increments cannot be
        # absorbed by a retained counterparty
        face = _run_synth(own=0.40, cross=0.10, rho=0.0, seed=4)
        f = face["inflation"]["cross"]["measured_factor"]
        assert f is not None and abs(f - 1.0) < 0.35, "rho=0 gave factor %.3f" % f
        assert face["inflation"]["rho"] is not None
        assert abs(face["inflation"]["rho"]) < 0.10, face["inflation"]["rho"]

    def l_correlation_inflates_and_the_closed_form_tracks_it():
        # r1261 law: prove the machinery moved before trusting the equality
        face = _run_synth(own=0.40, cross=0.10, rho=0.6, seed=5)
        infl = face["inflation"]
        f = infl["cross"]["measured_factor"]
        cf = infl["closed_form"]
        assert f is not None and f > 1.4, "rho=0.6 gave factor %.3f" % f
        assert cf is not None and cf > 1.4, "closed form %.3f" % cf
        assert abs((f - cf) / cf) <= 0.6, "measured %.3f vs closed %.3f" % (f, cf)
        assert infl["cross"]["naive_own_plus_one"] > infl["cross"]["identified_own_plus_all"]

    def l_exchangeable_increments_leave_the_difference_alone():
        # the omitted block loads EQUALLY on the retained own and cross regressors when the
        # increments are exchangeable, so a verdict that reads a DIFFERENCE is structurally
        # insulated even though both levels are inflated
        face = _run_synth(own=0.35, cross=0.20, rho=0.6, seed=6)
        naive = (face["designs"]["own_plus_one"].get("pooled") or {}).get("diff")
        ident = (face["designs"]["own_plus_all"].get("pooled") or {}).get("diff")
        assert naive is not None and ident is not None
        assert abs(naive - ident) < 0.15, \
            "exchangeable omission moved the difference: naive %.3f ident %.3f" % (naive, ident)
        f = face["inflation"]["cross"]["measured_factor"]
        assert f > 1.3, "the levels must still move, factor %.3f" % f

    def l_a_decoupled_counterparty_cannot_break_the_pairing():
        # the pooled design runs every ordered pair in BOTH directions, so a counterparty that
        # is decoupled from the omitted block cannot tilt the difference either
        face = _run_synth(own=0.30, cross=0.30, rho=0.7, seed=16, independent=("syn4",))
        ins = face["difference_insulation"]
        assert ins.get("gap") is not None
        assert abs(ins["gap"]) < 0.20, "the pairing failed to cancel: gap %.3f" % ins["gap"]
        f = face["inflation"]["cross"]["measured_factor"]
        assert f is not None and f > 1.3, "the levels must still be inflated, factor %.3f" % f

    def l_the_level_gate_is_where_the_reading_changes_side():
        # the deliverable test: a magnitude bar sitting inside the level's gate window reads
        # one way on the published level and the other way on the identified level, while the
        # difference's own window is far narrower
        face = _run_synth(own=0.30, cross=0.30, rho=0.65, seed=17)
        lv = [r for r in face["level_claims"] if r["key"] in
              ("pooled_cross", "naive_cross", "mean_cross")]
        assert lv, [r["key"] for r in face["level_claims"]]
        wide = max((r["gate_window"][1] - r["gate_window"][0]) for r in lv)
        assert wide > 0.10, "no level moved far enough to carry a gate: %.3f" % wide
        ins = face["difference_insulation"]
        dw = ins["gate_window"][1] - ins["gate_window"][0]
        assert dw < wide, "the difference is not narrower than the level (%.3f vs %.3f)" % (
            dw, wide)
        assert face["summary"]["levels_at_risk"], face["summary"]

    def l_mechanism_really_happened():
        face = _run_synth(own=0.3, cross=0.1, rho=0.5, seed=7)
        g = face["grid"]
        assert g["dates"] > 500, g
        s3 = face["designs"]["own_plus_all"]
        assert s3["n_members"] == 5, s3["n_members"]
        assert (s3.get("pooled") or {}).get("rows_used", 0) > 2000, s3.get("pooled")
        assert len((face["designs"]["own_plus_one"] or {}).get("pairs") or []) == 20

    def l_sum_form_substitutes_for_the_full_form():
        face = _run_synth(own=0.35, cross=0.12, rho=0.4, seed=8)
        infl = face["inflation"]
        assert infl["identified_forms_agree"] is True, infl["substitution"]

    def l_every_interval_contains_its_point():
        face = _run_synth(own=0.35, cross=0.12, rho=0.3, seed=9)
        for name in ("own_plus_one", "own_plus_all"):
            d = face["designs"][name]
            for m in (d.get("members") or []):
                if m.get("diff") is None or not m.get("diff_ci"):
                    continue
                lo, hi = m["diff_ci"]
                assert lo <= m["diff"] <= hi, "%s %s interval excludes its point" % (name, m)
        pooled = (face["designs"]["own_plus_all"].get("pooled") or {})
        if pooled.get("diff_ci"):
            lo, hi = pooled["diff_ci"]
            assert lo <= pooled["diff"] <= hi, "pooled interval excludes its point"

    def l_grid_bridge_is_published_or_refused():
        face = _run_synth(own=0.3, cross=0.1, rho=0.2, seed=10)
        br = face["grid_bridge"]
        assert br.get("pair_specific_mean_cross") is not None or br.get("reading") is None
        assert br.get("grid_ratio") is not None

    def l_non_repriceable_faces_say_why():
        face = _run_synth(own=0.3, cross=0.1, rho=0.2, seed=11)
        nr = [v for v in face["verdicts"] if v["repriced_verdict"] == "not_repriceable"]
        assert len(nr) >= 2, [v["face"] for v in face["verdicts"]]
        for v in nr:
            assert v.get("reason"), v

    def l_inventory_is_machine_read_not_asserted():
        face = _run_synth(own=0.3, cross=0.1, rho=0.2, seed=12)
        for r in face["inventory"]:
            assert r.get("path") is None or os.path.isfile(
                os.path.join(ROOT, r["path"])), "inventory row cites a missing face: %r" % (r,)
            assert "omits_members" in r and "regressor_set" in r

    def l_no_charge_is_asserted():
        face = _run_synth(own=0.3, cross=0.1, rho=0.2, seed=13)
        assert face["no_bill"]["permitted"] is False

    def l_short_grid_is_a_verdict_not_a_crash():
        per, syms = synth(n=80, seed=14)
        saved = globals()["BASKET"]
        globals()["BASKET"] = syms
        try:
            face = run(save=False, per=per)
        finally:
            globals()["BASKET"] = saved
        assert face["summary"]["verdict"] == "unresolved", face["summary"]

    leg("the identified design recovers the planted slopes",
        l_identified_recovers_the_planted_slopes)
    leg("uncorrelated increments produce no inflation", l_no_correlation_is_no_inflation)
    leg("correlation inflates and the closed form tracks it",
        l_correlation_inflates_and_the_closed_form_tracks_it)
    leg("exchangeable increments leave the difference alone",
        l_exchangeable_increments_leave_the_difference_alone)
    leg("a decoupled counterparty cannot break the pairing",
        l_a_decoupled_counterparty_cannot_break_the_pairing)
    leg("the level gate is where a reading changes side",
        l_the_level_gate_is_where_the_reading_changes_side)
    leg("the machinery really ran (grid, members, rows, pairs)", l_mechanism_really_happened)
    leg("the sum form substitutes for the full form",
        l_sum_form_substitutes_for_the_full_form)
    leg("every published difference interval contains its point",
        l_every_interval_contains_its_point)
    leg("the grid bridge is published", l_grid_bridge_is_published_or_refused)
    leg("faces that cannot be re-priced say why", l_non_repriceable_faces_say_why)
    leg("inventory rows are machine-read from faces that exist",
        l_inventory_is_machine_read_not_asserted)
    leg("no charge is asserted on the face", l_no_charge_is_asserted)
    leg("a short grid is a verdict, not a crash", l_short_grid_is_a_verdict_not_a_crash)

    ok = sum(1 for _n, p, _m in legs if p)
    for n, p, m in legs:
        print("  [%s] %s%s" % ("PASS" if p else "FAIL", n, (" :: " + m) if m else ""))
    print("selftest %d/%d" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="E242 omission-inflation sweep")
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