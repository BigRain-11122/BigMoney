"""E315 -- the leg epsilon that meets a two-regime gate.

E314 (r1333) turned each clamped gate into a model: where the form switches, the tolerance in
each regime, the scale the tolerance is normalised by. Five rows of the census now carry a
tolerance that depends on the gated quantity. But a gate only ever governs a comparison, and
the comparison is made by a leg that carries its own epsilon. Publishing the gate's two regimes
says nothing about which side of the leg that gate lands on.

So this study joins each two-regime gate to the leg that consumes it and asks one question per
row, in the quantity's own units:

* where does the gate's tolerance equal the leg's epsilon -- the **crossover scale** `eps/tol`,
  pure arithmetic from two published numbers, valid in the regime where tolerance is `tol * x`;
* is that crossover inside the range of magnitudes the face itself publishes, or beyond it
  (in which case the gate never tightens as far as the leg anywhere a reader can see);
* and how do the two numbers compare **at the face's own largest magnitude**, where the gate is
  loosest in absolute terms.

Three facts make this more than a restatement of E314:

1. four of the five legs publish `0.0` as their epsilon. A zero epsilon is exact equality, so no
   tolerance can ever be as tight as the leg: the leg binds at every magnitude, and the gate's
   "flat regime" rescues nothing -- it is only the loosest place the gate ever gets.
2. one leg publishes a non-zero epsilon and it *is* finer than the gate's flattest tolerance
   (`1e-09` against `0.0` at the zero end), so the gate is stricter than the leg only in a
   single-point regime nobody measures at, and looser at every positive magnitude past a
   crossover of `5e-07` units.
3. the flat regime is a claim about the small end of the domain, and the face's own leaves
   decide whether that end is ever visited. A regime no published magnitude falls into is a
   regime that cannot be tested by reading the face, whatever the arithmetic says.

The ratios are published as orders of magnitude rather than as `inf`: a leg at zero epsilon has
no finite ratio, and printing `1e12` for it would manufacture a number the arithmetic does not
support.

usage:
  python scripts/e315_leg_epsilon_vs_flat_regime.py run
  python scripts/e315_leg_epsilon_vs_flat_regime.py verify
  python scripts/e315_leg_epsilon_vs_flat_regime.py selftest
"""

import copy
import io
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import e314_clamped_gate_census as e314  # noqa: E402 -- the regime model is E314's

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE = "LEGEPS-%s.json"
LATEST = "legeps_latest.json"
UPSTREAM = os.path.join(OUTDIR, "gateclamp_latest.json")
TODAY = "2026-10-31"
STUDY = "E315_leg_epsilon_vs_flat_regime"
VERDICT = ("four_of_five_quantity_dependent_legs_demand_exact_equality_so_the_gate_is_looser_"
           "at_every_magnitude_the_face_publishes")

# the classes in which the gate's tolerance is a function of the gated quantity
QUANTITY_CLASSES = (
    "piecewise_floor",
    "linear_in_the_quantity",
    "constant_after_normalisation_and_linear",
)


def _read(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def save(payload, name, outdir=None):
    outdir = outdir or OUTDIR
    os.makedirs(outdir, exist_ok=True)
    with io.open(os.path.join(outdir, name), "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1, sort_keys=False)
        fh.write("\n")


# ------------------------------------------------------------------ the arithmetic

def flat_regime_tolerance(model):
    """The gate's tolerance at the small end of the domain, in the quantity's own units.

    Below the clamp's floor the tolerance is `tol * floor`; a linear gate with no floor has no
    flat regime at all, its tolerance only reaches zero at `x = 0`, which is exact equality.
    Returning `0.0` for that case is arithmetic, not a convention: at the zero end `tol * 0 = 0`.
    """
    cls = model.get("class")
    if cls == "piecewise_floor":
        gate, floor = model.get("gate"), model.get("floor")
        if gate is None or floor is None:
            return None
        return float(gate) * float(floor)
    if cls == "linear_in_the_quantity":
        return 0.0
    if cls == "constant_after_normalisation_and_linear":
        return None
    return None


def crossover_scale(model, leg_eps):
    """`eps / tol` -- the magnitude where the gate's `tol * x` tolerance equals the leg's epsilon.

    Only defined where the tolerance really is `tol * x`; a row whose gate carries no scale has
    no crossover to publish, so it returns None instead of a number borrowed from another regime.
    """
    if leg_eps is None:
        return None
    gate = model.get("gate")
    if not gate:
        return None
    if model.get("class") not in ("piecewise_floor", "linear_in_the_quantity"):
        return None
    return float(leg_eps) / float(gate)


def orders_of_magnitude(looser, tighter):
    """log10(looser/tighter), or None when the ratio has no finite value.

    A zero epsilon makes the ratio infinite. Printing a large finite number there would be the
    same mistake as printing a tolerance for an exact test: the quantity is unbounded.
    """
    if looser is None or tighter is None:
        return None
    if tighter == 0.0:
        return None
    if looser <= 0.0:
        return None
    return math.log10(looser / tighter)


def classify(model, leg_eps, flat_tol):
    """Which side of the leg the gate lands on at the small end of the domain."""
    if leg_eps is None:
        return "leg_epsilon_unpublished"
    if leg_eps == 0.0:
        return "leg_demands_exact_equality"
    if flat_tol == 0.0:
        return "gate_is_exact_only_at_the_zero_end"
    if flat_tol is None:
        return "gate_has_no_flat_regime_to_compare"
    if leg_eps < flat_tol:
        return "leg_finer_than_the_gates_flattest_tolerance"
    if leg_eps > flat_tol:
        return "leg_coarser_than_the_gates_flattest_tolerance"
    return "leg_epsilon_equals_the_gates_flattest_tolerance"


def leaf_magnitudes(face):
    """Every finite number the face publishes, with its path: the magnitudes a reader can see."""
    return e314.numeric_leaves(face)


def quantity_identifier(model):
    """The name the gate's scale is built on -- `prev`, `session_open`, `target`."""
    exprs = model.get("scale_expressions") or []
    if not exprs:
        return None
    return e314.scale_identifier(exprs[-1])


def attributable_magnitudes(face, ident):
    """The face's magnitudes that can be read as the quantity the gate is rated in.

    A leaf is attributable only when its own path names that quantity. Counting every number on
    the face instead would put the tolerance constant, the sample size and the version stamp
    into the same bucket as a measurement, and the count would then say the gate is exercised
    when it has not been (E207/E208 family: a name is not a measurement). When the quantity is
    simply absent, the honest answer is an empty set with a status, never a count.
    """
    if face is None:
        return [], "face_absent"
    if not ident:
        return [], "no_quantity_identifier"
    hits = [(v, p) for v, p in leaf_magnitudes(face) if ident.lower() in p.lower()]
    if not hits:
        return [], "quantity_not_published_on_the_face"
    return hits, "attributed_by_name"


def measure_at_the_leaves(face, model, leg_eps, ident=None):
    """Count the attributable magnitudes by which side of the leg the gate falls on."""
    values, status = attributable_magnitudes(face, ident)
    out = {
        "status": status,
        "leaves_total": 0,
        "leaves_in_the_flat_regime": 0,
        "leaves_where_the_gate_is_looser_than_the_leg": 0,
        "leaves_where_the_gate_is_tighter_than_the_leg": 0,
        "leaves_where_the_gate_equals_the_leg": 0,
        "leaves_with_no_gate_value": 0,
    }
    if status != "attributed_by_name" or leg_eps is None:
        return out
    floor = model.get("floor")
    for value, _path in values:
        out["leaves_total"] += 1
        if model.get("class") == "piecewise_floor" and floor is not None:
            if abs(value) < float(floor):
                out["leaves_in_the_flat_regime"] += 1
        tol = e314.tolerance_at(model, value)
        if tol is None:
            out["leaves_with_no_gate_value"] += 1
            continue
        if tol > leg_eps:
            out["leaves_where_the_gate_is_looser_than_the_leg"] += 1
        elif tol < leg_eps:
            out["leaves_where_the_gate_is_tighter_than_the_leg"] += 1
        else:
            out["leaves_where_the_gate_equals_the_leg"] += 1
    return out


def analyse(row, faces):
    model = row.get("regime_model") or {}
    leg_eps = row.get("leg_tolerance")
    face_rel = row.get("face")
    face = faces.at(face_rel) if face_rel else None
    ident = quantity_identifier(model)
    flat_tol = flat_regime_tolerance(model)
    cross = crossover_scale(model, leg_eps)
    face_max = row.get("face_max_abs_value")
    tol_at_max = e314.tolerance_at(model, face_max) if face_max is not None else None
    tol_at_one = e314.tolerance_at(model, 1.0)
    counts = measure_at_the_leaves(face, model, leg_eps, ident)
    inside = None
    if cross is not None and face_max is not None:
        inside = bool(cross <= float(face_max))
    return {
        "face": face_rel,
        "gate_path": row.get("gate_path"),
        "gate_value": row.get("gate_value"),
        "regime_class": model.get("class"),
        "switch_point": model.get("switch_point_in_the_scales_units"),
        "scale_expressions": model.get("scale_expressions"),
        "quantity_identifier": ident,
        "quantity_published_on_the_face": bool(
            counts["status"] == "attributed_by_name"),
        "leg_expression": row.get("leg_expression"),
        "leg_epsilon": leg_eps,
        "flat_regime_tolerance": flat_tol,
        "gate_tolerance_at_one_unit_of_the_quantity": tol_at_one,
        "orders_of_magnitude_the_gate_is_looser_at_one_unit": orders_of_magnitude(tol_at_one,
                                                                                 leg_eps),
        "gate_tolerance_at_the_face_maximum": tol_at_max,
        "face_max_abs_value": face_max,
        "crossover_scale": cross,
        "crossover_inside_the_published_range": inside,
        "orders_of_magnitude_the_leg_is_tighter_at_the_face_maximum": (
            orders_of_magnitude(tol_at_max, leg_eps)),
        "class": classify(model, leg_eps, flat_tol),
        "face_state": ("absent" if face is None else "present"),
        "leaves": counts,
    }


def build(outdir=None):
    up = _read(UPSTREAM)
    faces = e314.Faces()
    src = [r for r in (up.get("rows") or [])
           if (r.get("regime_model") or {}).get("class") in QUANTITY_CLASSES]
    rows = [analyse(r, faces) for r in src]
    rows.sort(key=lambda r: (r["face"] or "", r["gate_path"] or "", r["leg_expression"] or ""))

    def count(pred):
        return sum(1 for r in rows if pred(r))

    def leaves(key):
        return sum(int((r["leaves"] or {}).get(key) or 0) for r in rows)

    classes = [
        "leg_demands_exact_equality",
        "gate_is_exact_only_at_the_zero_end",
        "leg_finer_than_the_gates_flattest_tolerance",
        "leg_coarser_than_the_gates_flattest_tolerance",
        "leg_epsilon_equals_the_gates_flattest_tolerance",
        "gate_has_no_flat_regime_to_compare",
        "leg_epsilon_unpublished",
    ]
    census = {
        "upstream_rows": len(up.get("rows") or []),
        "upstream_rows_selected": len(src),
        "rows": len(rows),
        "rows_in_each_class": {c: count(lambda r, c=c: r["class"] == c) for c in classes},
        "rows_whose_leg_demands_exact_equality": count(
            lambda r: r["class"] == "leg_demands_exact_equality"),
        "rows_whose_leg_epsilon_is_published": count(lambda r: r["leg_epsilon"] is not None),
        "rows_whose_gate_is_tighter_at_the_face_maximum": count(
            lambda r: (r["orders_of_magnitude_the_leg_is_tighter_at_the_face_maximum"] is not None
                       and r["orders_of_magnitude_the_leg_is_tighter_at_the_face_maximum"] > 0)),
        "rows_with_a_crossover_scale": count(lambda r: r["crossover_scale"] is not None),
        "rows_whose_crossover_lies_inside_the_published_range": count(
            lambda r: r["crossover_inside_the_published_range"] is True),
        "rows_whose_crossover_lies_beyond_the_published_range": count(
            lambda r: r["crossover_inside_the_published_range"] is False),
        "rows_whose_crossover_is_unpublished": count(
            lambda r: r["crossover_inside_the_published_range"] is None),
        "rows_publishing_a_flat_regime": count(lambda r: r["regime_class"] == "piecewise_floor"),
        "rows_whose_quantity_identifier_is_published": count(
            lambda r: r["quantity_published_on_the_face"] is True),
        "rows_whose_quantity_identifier_is_not_a_key_on_the_face": count(
            lambda r: r["quantity_published_on_the_face"] is False),
        "rows_whose_leaf_measurement_is_unattributable": count(
            lambda r: (r["leaves"] or {}).get("status") != "attributed_by_name"),
        "leaf_measurement_status": {
            s: count(lambda r, s=s: (r["leaves"] or {}).get("status") == s)
            for s in ("attributed_by_name", "quantity_not_published_on_the_face",
                      "no_quantity_identifier", "face_absent")
        },
        "magnitudes_attributable_to_the_rated_quantity": leaves("leaves_total"),
        "attributable_magnitudes_inside_a_flat_regime": leaves("leaves_in_the_flat_regime"),
        "attributable_magnitudes_where_the_gate_is_looser_than_the_leg": leaves(
            "leaves_where_the_gate_is_looser_than_the_leg"),
        "attributable_magnitudes_where_the_gate_is_tighter_than_the_leg": leaves(
            "leaves_where_the_gate_is_tighter_than_the_leg"),
        "attributable_magnitudes_where_the_gate_equals_the_leg": leaves(
            "leaves_where_the_gate_equals_the_leg"),
        "rows_whose_gate_is_looser_than_the_leg_at_one_unit_of_the_quantity": count(
            lambda r: (r["orders_of_magnitude_the_gate_is_looser_at_one_unit"] or 0) > 0),
        "rows_whose_named_face_is_absent": count(lambda r: r["face_state"] == "absent"),
    }
    payload = {
        "schema": "bigmoney/e315-legeps/v1",
        "study": STUDY,
        "title": ("where does each two-regime gate's tolerance meet the leg's epsilon, and which "
                  "of the two is the real gate at the magnitudes the face publishes?"),
        "evidence_cutoff": TODAY,
        "generated": TODAY,
        "self_faces_excluded": [FACE % TODAY, LATEST],
        "upstream": {
            "gate_clamp_face": os.path.relpath(UPSTREAM, ROOT).replace(os.sep, "/"),
            "upstream_rows": len(up.get("rows") or []),
            "rows_selected": len(src),
            "selection": "regime classes whose tolerance depends on the gated quantity "
                         "(%s)" % ", ".join(QUANTITY_CLASSES),
        },
        "join_rules": {
            "crossover_scale": "eps / tol -- the magnitude at which a `tol * x` tolerance equals "
                               "the leg's epsilon; defined only where the gate really is `tol * "
                               "x`, and never borrowed across regimes",
            "flat_regime_tolerance": "piecewise: tol * floor, the gate's finest tolerance in the "
                                     "flat regime; linear with no floor: 0.0, which is exact "
                                     "equality at the zero end rather than a rounded tolerance",
            "orders_of_magnitude": "log10(gate tolerance / leg epsilon) at the face's largest "
                                   "magnitude; None (not a big number) when the epsilon is zero, "
                                   "because the ratio is unbounded",
            "published_range": "the face's own numeric leaves bound what a reader can see; a "
                               "crossover above the largest leaf is a crossover no reader reaches",
            "leaves": "only leaves whose own path names the quantity the gate is rated in are "
                      "counted; the tolerance constant and the sample size sit on the same face "
                      "and counting them would say the gate is exercised when it is not, so an "
                      "unattributable set is published as a status with zero, never as a count",
        },
        "census": census,
        "verdict": VERDICT,
        "quantity_dependent_rows": [
            {
                "class": r["class"],
                "face": r["face"],
                "gate_path": r["gate_path"],
                "gate_value": r["gate_value"],
                "regime_class": r["regime_class"],
                "switch_point": r["switch_point"],
                "leg_epsilon": r["leg_epsilon"],
                "flat_regime_tolerance": r["flat_regime_tolerance"],
                "quantity_identifier": r["quantity_identifier"],
                "quantity_published_on_the_face": r["quantity_published_on_the_face"],
                "gate_tolerance_at_one_unit_of_the_quantity":
                    r["gate_tolerance_at_one_unit_of_the_quantity"],
                "orders_of_magnitude_the_gate_is_looser_at_one_unit":
                    r["orders_of_magnitude_the_gate_is_looser_at_one_unit"],
                "gate_tolerance_at_the_face_maximum": r["gate_tolerance_at_the_face_maximum"],
                "face_max_abs_value": r["face_max_abs_value"],
                "crossover_scale": r["crossover_scale"],
                "crossover_inside_the_published_range":
                    r["crossover_inside_the_published_range"],
                "orders_of_magnitude_the_leg_is_tighter_at_the_face_maximum":
                    r["orders_of_magnitude_the_leg_is_tighter_at_the_face_maximum"],
                "leaves": r["leaves"],
            } for r in rows
        ],
        "rows": rows,
        "notes": [
            "an epsilon of 0.0 is exact equality, not a very small tolerance: no gate tolerance "
            "can be as tight, so the leg binds at every magnitude and the gate's flat regime is "
            "only the loosest place the gate ever gets",
            "at one unit of the gated quantity the gate's tolerance is already far looser than "
            "the one non-zero leg epsilon, and the crossover sits at 5e-07 units -- below any "
            "share price, so the leg is the binding test across the whole live range",
            "the flat regime is a statement about the small end of the domain, and the quantity "
            "it is rated in is not a key on either face, so the regime cannot be exercised by "
            "reading the face at all: the leaf measurement is published as a status with zero "
            "magnitudes instead of a count of unrelated numbers",
            "the crossover is published only where the gate really is `tol * x`: a row whose "
            "gate carries no scale has no crossover, and deriving one from another regime would "
            "reintroduce the unit error E313 was written to remove",
        ],
        "identity_checks": [],
    }
    payload["identity_checks"] = identity_checks(payload)
    save(payload, FACE % TODAY, outdir)
    save(payload, LATEST, outdir)
    return payload


def identity_checks(p):
    rows = p.get("rows") or []
    c = p.get("census") or {}
    checks = []

    def add(name, ok):
        checks.append({"check": name, "ok": bool(ok)})

    def close(a, b):
        if a is None or b is None:
            return False
        return abs(a - b) <= 1e-12 * max(abs(a), abs(b), 1e-30)

    add("the_rows_are_exactly_the_upstream_rows_with_a_quantity_dependent_gate",
        len(rows) == c.get("rows") == c.get("upstream_rows_selected"))
    add("the_class_partition_sums_to_the_rows",
        sum((c.get("rows_in_each_class") or {}).values()) == len(rows))
    add("every_row_publishes_a_leg_epsilon",
        all(r["leg_epsilon"] is not None for r in rows))
    add("a_zero_epsilon_is_classified_as_exact_equality_and_never_as_a_ratio",
        all(r["class"] == "leg_demands_exact_equality"
            and r["orders_of_magnitude_the_leg_is_tighter_at_the_face_maximum"] is None
            for r in rows if r["leg_epsilon"] == 0.0))
    add("the_crossover_is_the_epsilon_over_the_gate",
        all(close(r["crossover_scale"] * float(r["gate_value"]), r["leg_epsilon"])
            for r in rows if r["crossover_scale"] is not None))
    add("a_row_with_no_scale_publishes_no_crossover",
        all(r["crossover_scale"] is None for r in rows
            if r["regime_class"] not in ("piecewise_floor", "linear_in_the_quantity")))
    add("the_flat_regime_tolerance_is_the_gate_times_the_floor",
        all(close(r["flat_regime_tolerance"],
                  float(r["gate_value"]) * float(r["switch_point"]))
            for r in rows if r["regime_class"] == "piecewise_floor"))
    add("the_orders_of_magnitude_at_the_face_maximum_match_the_two_published_numbers",
        all(r["orders_of_magnitude_the_leg_is_tighter_at_the_face_maximum"] is None
            or close(10.0 ** r["orders_of_magnitude_the_leg_is_tighter_at_the_face_maximum"]
                     * float(r["leg_epsilon"]),
                     float(r["gate_tolerance_at_the_face_maximum"]))
            for r in rows if r["leg_epsilon"]))
    add("the_orders_of_magnitude_at_one_unit_match_the_two_published_numbers",
        all(r["orders_of_magnitude_the_gate_is_looser_at_one_unit"] is None
            or close(10.0 ** r["orders_of_magnitude_the_gate_is_looser_at_one_unit"]
                     * float(r["leg_epsilon"]),
                     float(r["gate_tolerance_at_one_unit_of_the_quantity"]))
            for r in rows if r["leg_epsilon"]))
    add("every_leaf_lands_on_exactly_one_side_of_the_leg",
        all((r["leaves"]["leaves_where_the_gate_is_looser_than_the_leg"]
             + r["leaves"]["leaves_where_the_gate_is_tighter_than_the_leg"]
             + r["leaves"]["leaves_where_the_gate_equals_the_leg"]
             + r["leaves"]["leaves_with_no_gate_value"]) == r["leaves"]["leaves_total"]
            for r in rows))
    add("an_unattributable_measurement_publishes_zero_magnitudes_and_a_status",
        all(r["leaves"]["leaves_total"] == 0
            and r["leaves"]["status"] != "attributed_by_name"
            for r in rows if r["quantity_published_on_the_face"] is False))
    add("the_quantity_published_flag_is_derived_from_the_measurement_status",
        all(bool(r["quantity_published_on_the_face"])
            == (r["leaves"]["status"] == "attributed_by_name") for r in rows))
    add("a_zero_epsilon_row_never_publishes_a_finite_ratio",
        all(r["orders_of_magnitude_the_gate_is_looser_at_one_unit"] is None for r in rows
            if r["leg_epsilon"] == 0.0))
    add("leaves_in_the_flat_regime_are_a_subset_of_the_leaves_examined",
        all(r["leaves"]["leaves_in_the_flat_regime"] <= r["leaves"]["leaves_total"] for r in rows))
    add("a_zero_epsilon_row_has_no_leaf_on_which_the_gate_is_tighter",
        all(r["leaves"]["leaves_where_the_gate_is_tighter_than_the_leg"] == 0
            for r in rows if r["leg_epsilon"] == 0.0))
    add("the_study_never_reads_itself",
        all((r["face"] or "").find("LEGEPS-") < 0 for r in rows))
    add("a_crossover_verdict_is_published_for_every_row_that_has_one",
        all((r["crossover_inside_the_published_range"] is not None)
            for r in rows if r["crossover_scale"] is not None
            and r["face_max_abs_value"] is not None))
    add("no_row_claims_the_leg_finer_than_a_flat_tolerance_it_does_not_have",
        all(not (r["class"] == "leg_finer_than_the_gates_flattest_tolerance"
                 and not (r["leg_epsilon"] < r["flat_regime_tolerance"]))
            for r in rows))
    return checks


# --------------------------------------------------------------------------- cli

def cmd_run():
    p = build()
    c = p["census"]
    print("E315 %s cutoff=%s" % (p["verdict"], p["evidence_cutoff"]))
    print("  rows=%d of %d upstream | classes=%s"
          % (c["rows"], c["upstream_rows"],
             json.dumps(c["rows_in_each_class"], ensure_ascii=False, sort_keys=True)))
    print("  leg epsilon published: %d | exact equality: %d | crossover published: %d "
          "(inside the range %d / beyond %d / unpublished %d)"
          % (c["rows_whose_leg_epsilon_is_published"], c["rows_whose_leg_demands_exact_equality"],
             c["rows_with_a_crossover_scale"],
             c["rows_whose_crossover_lies_inside_the_published_range"],
             c["rows_whose_crossover_lies_beyond_the_published_range"],
             c["rows_whose_crossover_is_unpublished"]))
    print("  rated quantity published on the face: yes=%d no=%d | attributable magnitudes=%d "
          "(looser=%d tighter=%d equal=%d) | status=%s"
          % (c["rows_whose_quantity_identifier_is_published"],
             c["rows_whose_quantity_identifier_is_not_a_key_on_the_face"],
             c["magnitudes_attributable_to_the_rated_quantity"],
             c["attributable_magnitudes_where_the_gate_is_looser_than_the_leg"],
             c["attributable_magnitudes_where_the_gate_is_tighter_than_the_leg"],
             c["attributable_magnitudes_where_the_gate_equals_the_leg"],
             json.dumps(c["leaf_measurement_status"], ensure_ascii=False, sort_keys=True)))
    for r in p["quantity_dependent_rows"]:
        print("  %s %s leg_eps=%r flat=%r gate@1unit=%r gate@max=%r crossover=%r class=%s "
              "quantity=%r published=%s"
              % (r["face"], r["gate_path"], r["leg_epsilon"], r["flat_regime_tolerance"],
                 r["gate_tolerance_at_one_unit_of_the_quantity"],
                 r["gate_tolerance_at_the_face_maximum"], r["crossover_scale"], r["class"],
                 r["quantity_identifier"], r["quantity_published_on_the_face"]))
    bad = [x for x in p["identity_checks"] if not x["ok"]]
    print("  identity: %d/%d ok" % (len(p["identity_checks"]) - len(bad),
                                    len(p["identity_checks"])))
    for x in bad:
        print("   FAIL", x["check"])
    return 0 if not bad else 1


def cmd_verify():
    path = os.path.join(OUTDIR, FACE % TODAY)
    if not os.path.exists(path):
        print("verify: face absent")
        return 2
    p = _read(path)
    problems = []
    if p["verdict"] != VERDICT:
        problems.append("verdict moved")
    for x in identity_checks(p):
        if not x["ok"]:
            problems.append("identity: " + x["check"])
    fresh = build(outdir=os.path.join(ROOT, "results", "_e315_verify"))
    if [(r["class"], r["crossover_scale"], r["leg_epsilon"]) for r in fresh["rows"]] != \
            [(r["class"], r["crossover_scale"], r["leg_epsilon"]) for r in p["rows"]]:
        problems.append("a re-run changes a class, a crossover or an epsilon")
    if [r["leaves"] for r in fresh["rows"]] != [r["leaves"] for r in p["rows"]]:
        problems.append("a re-run changes the leaf counts")
    if (fresh.get("census") or {}).get("verdict") == "never":
        problems.append("impossible")
    print("verify: %d problems" % len(problems))
    for x in problems:
        print("  -", x)
    return 0 if not problems else 1


def check(name, ok, detail=""):
    print(("  PASS " if ok else "  FAIL ") + name + ((" :: " + detail) if detail and not ok else ""))
    return bool(ok)


def cmd_selftest():
    p = _read(os.path.join(OUTDIR, FACE % TODAY))
    ok = True

    # --- the arithmetic, on fixtures
    m = e314.regime_model(1e-12, [1.0], ["max(1.0, prev)"])
    ok &= check("fixture: a clamped gate's flat tolerance is tol*floor",
                flat_regime_tolerance(m) == 1e-12,
                "got=%r" % (flat_regime_tolerance(m),))
    ok &= check("fixture: a linear gate's tolerance is zero at the zero end",
                flat_regime_tolerance(e314.regime_model(0.002, [], ["session_open"])) == 0.0)
    ok &= check("fixture: the crossover of a 1e-09 leg against a 0.002 gate is 5e-07",
                abs(crossover_scale(e314.regime_model(0.002, [], ["session_open"]), 1e-09)
                    - 5e-07) < 1e-20)
    ok &= check("fixture: a zero epsilon has no finite ratio",
                orders_of_magnitude(1e-12, 0.0) is None)
    ok &= check("fixture: a positive ratio is a log10",
                abs(orders_of_magnitude(1e-9, 1e-12) - 3.0) < 1e-12)
    ok &= check("fixture: a zero epsilon is exact equality",
                classify(m, 0.0, 1e-12) == "leg_demands_exact_equality")
    ok &= check("fixture: a leg finer than the flattest tolerance is classified as finer",
                classify(m, 1e-13, 1e-12) == "leg_finer_than_the_gates_flattest_tolerance")
    ok &= check("fixture: a leg coarser than the flattest tolerance is classified as coarser",
                classify(m, 1e-9, 1e-12) == "leg_coarser_than_the_gates_flattest_tolerance")
    ok &= check("fixture: a linear gate nobody's epsilon reaches is exact only at zero",
                classify(e314.regime_model(0.002, [], ["session_open"]), 1e-09, 0.0)
                == "gate_is_exact_only_at_the_zero_end")
    ok &= check("fixture: a gate with no scale has no crossover",
                crossover_scale(e314.regime_model(0.1, [], []), 1e-9) is None)
    ok &= check("fixture: leaves are counted on both sides of the epsilon",
                measure_at_the_leaves({"prev_at": 0.5, "prev_b": 2.0}, m, 1e-12, "prev")
                ["leaves_where_the_gate_is_looser_than_the_leg"] == 1)
    ok &= check("fixture: a leaf below the floor is counted inside the flat regime",
                measure_at_the_leaves({"prev_at": 0.5}, m, 1e-12, "prev")
                ["leaves_in_the_flat_regime"] == 1)
    ok &= check("fixture: a number whose path does not name the quantity is not attributed",
                measure_at_the_leaves({"sample_size": 5, "tol": 1e-12}, m, 1e-12, "prev")
                ["status"] == "quantity_not_published_on_the_face")
    ok &= check("fixture: an unattributable set publishes zero, not a count of other numbers",
                measure_at_the_leaves({"sample_size": 5}, m, 1e-12, "prev")["leaves_total"] == 0)
    ok &= check("fixture: no identifier means no attribution, not a wildcard",
                measure_at_the_leaves({"prev": 0.5}, m, 1e-12, None)["status"]
                == "no_quantity_identifier")

    # --- the published face
    c = p["census"]
    ok &= check("identity: every check green", all(x["ok"] for x in p["identity_checks"]))
    ok &= check("findings: five rows carry a quantity dependent gate", c["rows"] == 5,
                "got=%d" % c["rows"])
    ok &= check("findings: four legs demand exact equality",
                c["rows_whose_leg_demands_exact_equality"] == 4,
                "got=%d" % c["rows_whose_leg_demands_exact_equality"])
    ok &= check("findings: no face publishes the quantity its gate is rated in",
                c["rows_whose_quantity_identifier_is_published"] == 0,
                "got=%d" % c["rows_whose_quantity_identifier_is_published"])
    ok &= check("findings: the only crossover is below one unit of the quantity",
                all(r["crossover_scale"] < 1e-6 for r in p["quantity_dependent_rows"]
                    if r["crossover_scale"] is not None))
    ok &= check("findings: at one unit of the quantity the gate is looser than the one non-zero "
                "leg",
                all(r["orders_of_magnitude_the_gate_is_looser_at_one_unit"] > 0
                    for r in p["quantity_dependent_rows"] if r["leg_epsilon"]))
    ok &= check("findings: the leaf measurement is unattributable on every row",
                c["magnitudes_attributable_to_the_rated_quantity"] == 0,
                "got=%d" % c["magnitudes_attributable_to_the_rated_quantity"])
    ok &= check("findings: at the face maximum the gate is looser than every leg",
                all(r["orders_of_magnitude_the_leg_is_tighter_at_the_face_maximum"] is None
                    or r["orders_of_magnitude_the_leg_is_tighter_at_the_face_maximum"] > 0
                    for r in p["quantity_dependent_rows"]))
    ok &= check("counts: no row is counted twice",
                c["rows"] == len({(r["face"], r["gate_path"], r["leg_expression"])
                                  for r in p["rows"]}))

    # --- mutations must be caught
    m = copy.deepcopy(p)
    for r in m["rows"]:
        if r["leg_epsilon"] == 0.0:
            r["leg_epsilon"] = 1e-12
            break
    ok &= check("mutation: a zero epsilon rewritten as a number is caught",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    for r in m["rows"]:
        if r["crossover_scale"] and r["crossover_scale"] > 0.0:
            r["crossover_scale"] *= 2.0
            break
    else:
        ok &= check("mutation: no positive crossover in the face to mutate", False)
    ok &= check("mutation: a doubled crossover is caught",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    for r in m["rows"]:
        if r["regime_class"] == "piecewise_floor":
            r["flat_regime_tolerance"] = 1e-9
            break
    ok &= check("mutation: a flat tolerance that is not tol*floor is caught",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    m["census"]["rows_in_each_class"]["leg_demands_exact_equality"] += 1
    ok &= check("mutation: an inflated class partition is caught",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    m["rows"].append(dict(m["rows"][0]))
    ok &= check("mutation: a duplicated row is caught",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    for r in m["rows"]:
        if r["leg_epsilon"] == 0.0:
            r["leaves"]["leaves_where_the_gate_is_tighter_than_the_leg"] = 3
            break
    ok &= check("mutation: a zero epsilon with a tighter gate leaf is caught",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    for r in m["rows"]:
        if r["crossover_scale"] is not None:
            r["crossover_inside_the_published_range"] = None
            break
    ok &= check("mutation: dropping a published crossover verdict is caught",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    for r in m["rows"]:
        if r["class"] == "leg_demands_exact_equality":
            r["class"] = "leg_finer_than_the_gates_flattest_tolerance"
            break
    ok &= check("mutation: a leg finer than a tolerance it does not have is caught",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    for r in m["rows"]:
        r["face"] = "results/state_tilt/LEGEPS-2026-10-31.json"
        break
    ok &= check("mutation: a row reading this study's own face is caught",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    for r in m["rows"]:
        if r["leg_epsilon"]:
            r["orders_of_magnitude_the_gate_is_looser_at_one_unit"] = 99.0
            break
    ok &= check("mutation: an orders-of-magnitude claim its numbers do not support is caught",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    for r in m["rows"]:
        if not r["quantity_published_on_the_face"]:
            r["leaves"]["leaves_total"] = 12
            break
    ok &= check("mutation: an unattributable measurement given a count is caught",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    for r in m["rows"]:
        r["quantity_published_on_the_face"] = True
        break
    ok &= check("mutation: a publication flag that disagrees with the status is caught",
                not all(x["ok"] for x in identity_checks(m)))

    print("selftest: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    cmd = argv[1]
    if cmd == "run":
        return cmd_run()
    if cmd == "verify":
        return cmd_verify()
    if cmd == "selftest":
        return cmd_selftest()
    print("unknown command: " + cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))