"""E314 -- clamped gates: two forms in one expression, and where the switch is.

E313 (r1332) published each gate's *observed form* and, where the producer multiplies its gate by
a scale, the scale and any `max(1.0, x)` clamp. Three published rows carry that clamp and one
divides by a fixed 100.0. Those four are the only gates in the census whose tolerance is not a
single number, and a reader of the face cannot do the arithmetic because neither the scale, the
floor nor the normalisation is published.

So this study turns the clamp into numbers, per row:

* **where the form switches** -- the floor, in the scale's own unit, with the expression that
  defines it;
* **the tolerance in each regime, in both units** -- absolute in the gated quantity's units and
  relative to it: above the floor `tol * x` / `tol`; below it `tol * floor` / `tol * floor / x`.
  The two regimes meet exactly at the switch (published as a continuity identity, not a claim);
* **when the flat regime becomes looser than half a unit of the quantity** -- `0.5 / tol`, pure
  arithmetic from the gate, which is what decides whether the clamp is ever load-bearing;
* **whether the face can reproduce either regime** -- the scale identifier and the clamp tokens
  are looked for in the face itself, so "not published" is a measurement and not an opinion.

The clamp converts unbounded relative looseness as `x -> 0` into a flat absolute tolerance. That
is an argument about the zero end of the domain. On a count domain it never engages, and the
upper regime never reaches half a count either -- so the gate is exact equality wearing a
tolerance, which is a fact about the domain, not about the clamp.

usage:
  python scripts/e314_clamped_gate_census.py run
  python scripts/e314_clamped_gate_census.py verify
  python scripts/e314_clamped_gate_census.py selftest
"""

import copy
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import e313_gate_form_and_scale as e313  # noqa: E402 -- the form/scales/floor reading is E313's

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE = "GATECLAMP-%s.json"
LATEST = "gateclamp_latest.json"
UPSTREAM = os.path.join(OUTDIR, "gateform_latest.json")
TODAY = "2026-10-31"
STUDY = "E314_clamped_gate_census"
VERDICT = ("a_clamp_that_never_engages_still_hides_the_tolerance_in_the_quantitys_own_units")

IDENT_ONLY = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
LITERAL = re.compile(r"^([0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)$")


def _read(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def save(payload, name, outdir=None):
    outdir = outdir or OUTDIR
    os.makedirs(outdir, exist_ok=True)
    with io.open(os.path.join(outdir, name), "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1, sort_keys=False)
        fh.write("\n")


# ------------------------------------------------------------------ reading a face

class Faces(object):
    """Load and interrogate a producer face once; several rows share one face."""

    def __init__(self):
        self._cache = {}

    def at(self, relpath):
        if relpath not in self._cache:
            ap = os.path.join(ROOT, relpath)
            try:
                self._cache[relpath] = _read(ap)
            except (OSError, ValueError):
                self._cache[relpath] = None
        return self._cache[relpath]


def numeric_leaves(obj, path="", out=None):
    """Every finite number in a face with its dotted path; booleans are labels, not magnitudes."""
    if out is None:
        out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            numeric_leaves(v, path + "." + str(k) if path else str(k), out)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            numeric_leaves(v, path + "[%d]" % i, out)
    elif isinstance(obj, bool):
        return out
    elif isinstance(obj, (int, float)):
        out.append((float(obj), path))
    return out


def key_names(obj, out=None):
    if out is None:
        out = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.add(str(k))
            key_names(v, out)
    elif isinstance(obj, list):
        for v in obj:
            key_names(v, out)
    return out


def face_max_abs(face):
    """The largest magnitude the face publishes, with its path -- a bound on every quantity on it."""
    best = None
    for value, path in numeric_leaves(face):
        m = abs(value)
        if best is None or m > best[0]:
            best = (m, path)
    return (best[0], best[1]) if best else (None, None)


def resolve_path(face, dotted):
    """Does the gate path the row names actually resolve on the face?"""
    if not dotted:
        return False
    cur = face
    for part in str(dotted).split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return False
    return True


def scale_identifier(expr):
    """The name a scale expression is built on: `max(1.0, prev)` -> `prev`, `target` -> `target`."""
    if not expr:
        return None
    names = IDENT_PLACE.findall(expr)
    return names[-1] if names else None


IDENT_PLACE = re.compile(r"(?<![0-9.])[A-Za-z_][A-Za-z0-9_]*")


# ------------------------------------------------------------------ the arithmetic

def split_scales(scales):
    """Fixed normalisations (a literal divisor) vs free scales (a name the domain defines)."""
    fixed, free = [], []
    for s in scales or []:
        m = LITERAL.match(str(s).strip())
        if m:
            fixed.append(float(m.group(1)))
        else:
            free.append(s)
    return fixed, free


def regime_model(gate, floors, scales):
    """The tolerance as a function of the gated quantity, as numbers in both units.

    Returns a dict whose class is one of:
      constant_absolute          -- one number, no dependence on the quantity
      constant_after_normalisation -- one number once the fixed divisor is undone
      linear_in_the_quantity     -- tol * x everywhere (and 0 at x = 0: exact equality there)
      piecewise_floor            -- tol * floor below the switch, tol * x above it
    """
    gate = float(gate) if gate is not None else None
    fixed, free = split_scales(scales)
    floor = float(floors[0]) if floors else None
    if gate is None:
        return {"class": "gate_value_unpublished", "gate": None}
    if floor is not None and free:
        return {
            "class": "piecewise_floor",
            "gate": gate,
            "floor": floor,
            "scale_expressions": free,
            "switch_point_in_the_scales_units": floor,
            "below_the_switch": {
                "absolute_in_the_quantitys_units": gate * floor,
                "relative_to_the_quantity": "tol * floor / x  (grows without bound as x -> 0)",
                "at_the_switch_relative": gate,
            },
            "above_the_switch": {
                "absolute_in_the_quantitys_units": "tol * x",
                "relative_to_the_quantity": gate,
            },
            "regimes": 2,
        }
    if free and gcd_floor_absent(floors):
        return {
            "class": "linear_in_the_quantity",
            "gate": gate,
            "floor": None,
            "scale_expressions": free,
            "switch_point_in_the_scales_units": None,
            "above_the_switch": {
                "absolute_in_the_quantitys_units": "tol * x",
                "relative_to_the_quantity": gate,
            },
            "at_zero_scale": {
                "absolute_in_the_quantitys_units": 0.0,
                "reading": "at x = 0 the gate is exact equality -- the degenerate end of a "
                           "relative band, and the reason a clamp exists",
            },
            "regimes": 1,
        }
    if fixed and not free:
        divisor = fixed[0]
        return {
            "class": "constant_after_normalisation",
            "gate": gate,
            "divisor": divisor,
            "absolute_in_the_published_units": gate,
            "absolute_in_the_original_units": gate * divisor,
            "regime_note": "the producer divides the quantity by the constant before comparing, "
                           "so one gate reads as two numbers depending on which unit a reader "
                           "assumes",
            "regimes": 1,
        }
    if fixed:
        divisor = fixed[0]
        return {
            "class": "constant_after_normalisation_and_linear",
            "gate": gate,
            "divisor": divisor,
            "absolute_in_the_original_units": gate * divisor,
            "scale_expressions": free,
            "regimes": 2,
        }
    return {
        "class": "constant_absolute",
        "gate": gate,
        "absolute_in_the_quantitys_units": gate,
        "relative_to_the_quantity": "tol / x  (no scale is named, so no relative reading is "
                                   "published)",
        "regimes": 1,
    }


def gcd_floor_absent(floors):
    return not floors


def half_unit_crossing(gate):
    """The quantity at which a `tol * x` gate's tolerance reaches half a unit: 0.5 / tol."""
    if not gate:
        return None
    return 0.5 / float(gate)


def tolerance_at(model, x):
    """The gate's absolute tolerance at a given magnitude, read through its own regime class.

    A constant gate does not become looser because the face happens to publish a large number
    somewhere else, so the arithmetic has to follow the model and not one formula (E238/E240
    family: a coefficient is only comparable inside its own parametrisation).
    """
    cls = model.get("class")
    gate = model.get("gate")
    if gate is None or x is None:
        return None
    if cls == "piecewise_floor":
        floor = model.get("floor")
        return float(gate) * float(floor) if abs(x) < float(floor) else float(gate) * abs(float(x))
    if cls == "linear_in_the_quantity":
        return float(gate) * abs(float(x))
    if cls == "constant_after_normalisation":
        return float(gate) * float(model.get("divisor") or 1.0)
    if cls in ("constant_absolute", "constant_after_normalisation_and_linear"):
        return float(gate)
    return None


def analyse(row, faces):
    gate = row.get("gate_value")
    floors = row.get("gate_scale_floors") or []
    scales = row.get("gate_scales") or []
    model = regime_model(gate, floors, scales)
    face_rel = row.get("face")
    face = faces.at(face_rel) if face_rel else None
    face_max, face_max_path = face_max_abs(face) if face is not None else (None, None)
    keys = key_names(face) if face is not None else set()
    ident = None
    if model.get("scale_expressions"):
        ident = scale_identifier(model["scale_expressions"][-1])
    floor = model.get("floor")
    return {
        "face": face_rel,
        "gate_path": row.get("gate_path"),
        "gate_value": gate,
        "gate_form_observed": row.get("gate_form_observed"),
        "gate_scales": scales,
        "gate_scale_floors": floors,
        "regime_model": model,
        "regime_classes": model.get("class"),
        "switch_point": model.get("switch_point_in_the_scales_units"),
        "scale_identifier": ident,
        "face_max_abs_value": face_max,
        "face_max_abs_path": face_max_path,
        "face_state": ("absent" if face is None else "present"),
        "tolerance_at_the_face_maximum_magnitude": tolerance_at(model, face_max),
        "half_unit_crossing": half_unit_crossing(gate),
        "clamp_engages_anywhere_on_this_face": (
            None if (floor is None or face_max is None) else bool(face_max < floor)),
        "tolerance_is_half_a_unit_or_coarser_at_the_face_maximum": (
            None if (gate is None or face_max is None) else
            bool((tolerance_at(model, face_max) or 0.0) >= 0.5)),
        "face_publishes": {
            "gate_path_resolves": resolve_path(face, row.get("gate_path")),
            "scale_identifier_in_a_key_name": (
                None if ident is None else any(ident.lower() in k.lower() for k in keys)),
            "clamp_tokens_on_the_face": (
                None if face is None else any(t in json.dumps(face) for t in
                                             ("max(", "max (", '"floor"', "clamp"))),
            "divisor_published": (
                None if "divisor" not in model else
                any(abs(v - model["divisor"]) < 1e-12 for v, _p in numeric_leaves(face))),
        },
        "leg_expression": row.get("leg_expression"),
        "leg_tolerance": row.get("leg_tolerance"),
        "reproducible_from_the_face": reproducible(row, model, ident, keys, face),
    }


def reproducible(row, model, ident, keys, face):
    """Can a consumer reproduce either regime without reading the producer?

    Both numbers are needed: the gate alone fixes the slope, and the scale (with its floor) fixes
    where the two regimes meet. A face that publishes the gate and neither of the other two
    entitles no regime at all.
    """
    if face is None:
        return {"answer": False, "why": "the face is absent, so nothing about the gate is published"}
    path_ok = resolve_path(face, row.get("gate_path"))
    ident_ok = (ident is not None and any(ident.lower() in k.lower() for k in keys))
    if model.get("class") == "constant_absolute":
        return {
            "answer": bool(path_ok),
            "gate_published": bool(path_ok),
            "why": ("a constant gate needs no scale: the face carries the whole tolerance"
                    if path_ok else "the gate path does not resolve on the face"),
        }
    if model.get("class") == "constant_after_normalisation":
        divisor_ok = any(abs(v - model["divisor"]) < 1e-12 for v, _p in numeric_leaves(face))
        return {
            "answer": bool(path_ok and divisor_ok),
            "gate_published": bool(path_ok),
            "divisor_published": bool(divisor_ok),
            "why": ("the gate and the fixed divisor are both on the face" if path_ok and divisor_ok
                    else "the gate is on the face but the fixed divisor is not, so the tolerance "
                         "exists in an unnamed unit"),
        }
    return {
        "answer": bool(path_ok and ident_ok),
        "gate_published": bool(path_ok),
        "scale_published": bool(ident_ok),
        "why": ("the gate and the scale it is normalised by are both on the face"
                if path_ok and ident_ok else
                "the gate is published as one number; the scale %r that turns tol into a "
                "tolerance is not a key on the face, so neither regime can be reproduced from it"
                % (ident or "the scale")),
    }


def build(outdir=None):
    up = _read(UPSTREAM)
    faces = Faces()
    rows = [analyse(r, faces) for r in up.get("rows") or []]
    rows.sort(key=lambda r: (r["face"] or "", r["gate_path"] or "", r["leg_expression"] or ""))

    def count(pred):
        return sum(1 for r in rows if pred(r))

    clamped = [r for r in rows if r["regime_classes"] == "piecewise_floor"]
    census = {
        "upstream_rows": len(up.get("rows") or []),
        "rows": len(rows),
        "regime_piecewise_floor": count(lambda r: r["regime_classes"] == "piecewise_floor"),
        "regime_linear_in_the_quantity": count(
            lambda r: r["regime_classes"] == "linear_in_the_quantity"),
        "regime_constant_after_normalisation": count(
            lambda r: r["regime_classes"] == "constant_after_normalisation"),
        "regime_constant_absolute": count(lambda r: r["regime_classes"] == "constant_absolute"),
        "regime_unresolved": count(lambda r: str(r["regime_classes"]).startswith("gate_value")),
        "rows_whose_tolerance_depends_on_the_quantity": count(
            lambda r: r["regime_classes"] in ("piecewise_floor", "linear_in_the_quantity",
                                              "constant_after_normalisation_and_linear")),
        "rows_publishing_a_switch_point": count(lambda r: r["switch_point"] is not None),
        "rows_where_the_clamp_never_engages_on_their_own_face": count(
            lambda r: r["clamp_engages_anywhere_on_this_face"] is False),
        "rows_whose_tolerance_is_half_a_unit_or_coarser_at_the_face_maximum": count(
            lambda r: r["tolerance_is_half_a_unit_or_coarser_at_the_face_maximum"] is True),
        "rows_whose_named_face_is_absent": count(lambda r: r["face_state"] == "absent"),
        "rows_whose_half_unit_crossing_exceeds_the_faces_largest_number": count(
            lambda r: (r["half_unit_crossing"] is not None and r["face_max_abs_value"] is not None
                       and r["half_unit_crossing"] > r["face_max_abs_value"])),
        "rows_reproducible_from_the_face": count(
            lambda r: (r["reproducible_from_the_face"] or {}).get("answer") is True),
        "rows_not_reproducible_from_the_face": count(
            lambda r: (r["reproducible_from_the_face"] or {}).get("answer") is not True),
        "rows_whose_scale_is_not_a_key_on_the_face": count(
            lambda r: (r["face_publishes"] or {}).get("scale_identifier_in_a_key_name") is False),
        "rows_whose_clamp_tokens_are_absent_from_the_face": count(
            lambda r: (r["face_publishes"] or {}).get("clamp_tokens_on_the_face") is False),
    }
    payload = {
        "schema": "bigmoney/e314-gateclamp/v1",
        "study": STUDY,
        "title": ("where does each clamped gate switch form, what is its tolerance in each regime "
                  "in both units, and can a consumer of the face reproduce either regime?"),
        "evidence_cutoff": TODAY,
        "generated": TODAY,
        "self_faces_excluded": [FACE % TODAY, LATEST],
        "upstream": {
            "gate_form_face": os.path.relpath(UPSTREAM, ROOT).replace(os.sep, "/"),
            "upstream_rows": len(up.get("rows") or []),
        },
        "join_rules": {
            "switch_point": "the floor of `max(floor, x)` in the scale's own unit; the two regimes "
                            "meet there exactly (published as a continuity identity)",
            "units": "absolute = the gate times the scale, in the gated quantity's own units; "
                     "relative = the gate itself above the switch, and tol*floor/x below it",
            "half_unit_crossing": "0.5 / tol -- the quantity at which a `tol * x` gate's tolerance "
                                  "reaches half a unit, so a gate below it can only ever separate "
                                  "values that differ by more than that quantity",
            "reproducible": "the gate path must resolve on the face AND the scale identifier must "
                            "appear as a key name there; anything less entitles no regime",
        },
        "census": census,
        "verdict": VERDICT,
        "clamped_rows": [
            {
                "face": r["face"],
                "gate_path": r["gate_path"],
                "gate_value": r["gate_value"],
                "scale_expressions": r["regime_model"].get("scale_expressions"),
                "switch_point": r["switch_point"],
                "tolerance_below_the_switch": r["regime_model"]["below_the_switch"],
                "tolerance_above_the_switch": r["regime_model"]["above_the_switch"],
                "face_max_abs_value": r["face_max_abs_value"],
                "tolerance_at_the_face_maximum_magnitude":
                    r["tolerance_at_the_face_maximum_magnitude"],
                "half_unit_crossing": r["half_unit_crossing"],
                "clamp_engages_on_this_face": r["clamp_engages_anywhere_on_this_face"],
                "reproducible_from_the_face": r["reproducible_from_the_face"],
                "face_publishes": r["face_publishes"],
            } for r in clamped
        ],
        "rows": rows,
        "notes": [
            "the clamp is continuous in both units: at the switch the absolute tolerance is "
            "tol*floor on both sides and the relative tolerance is tol on both sides, so the "
            "piecewise form is one band with one kink, not two bands",
            "what the clamp buys is boundedness of the relative tolerance as x -> 0; what it costs "
            "is that the gate's absolute size now depends on a scale the face does not print",
            "a gate that needs 5e11 units of the quantity before its tolerance reaches half a unit "
            "cannot separate adjacent values of that quantity anywhere in a face whose largest "
            "number is far below that -- the tolerance is a formality and equality is the real "
            "test, which is a statement about the domain, not about the clamp",
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

    add("row_count_matches_the_upstream_face", len(rows) == c.get("rows") == c.get("upstream_rows"))
    add("regime_partition_sums_to_the_rows",
        (c.get("regime_piecewise_floor", 0) + c.get("regime_linear_in_the_quantity", 0)
         + c.get("regime_constant_after_normalisation", 0) + c.get("regime_constant_absolute", 0)
         + c.get("regime_unresolved", 0)) == len(rows))
    add("every_clamped_row_publishes_its_switch_point",
        all(r["switch_point"] is not None for r in rows
            if r["regime_classes"] == "piecewise_floor"))
    add("every_clamped_row_publishes_its_tolerance_below_the_switch",
        all(isinstance(r["regime_model"]["below_the_switch"]["absolute_in_the_quantitys_units"],
                       float)
            for r in rows if r["regime_classes"] == "piecewise_floor"))
    def meets_at_the_switch(r):
        # a check that raises is a check no mutation can fail: every guard returns False instead
        below = r["regime_model"].get("below_the_switch") or {}
        gate, switch = r.get("gate_value"), r.get("switch_point")
        value = below.get("absolute_in_the_quantitys_units")
        if gate is None or switch is None or value is None:
            return False
        return abs(value - float(gate) * float(switch)) <= 1e-30 + 1e-9 * abs(
            float(gate) * float(switch))

    def relative_meets(r):
        below = r["regime_model"].get("below_the_switch") or {}
        rel, gate = below.get("at_the_switch_relative"), r.get("gate_value")
        if rel is None or gate is None:
            return False
        return abs(rel - float(gate)) <= 1e-9 * max(abs(float(gate)), 1e-30)

    add("the_two_regimes_meet_exactly_at_the_switch",
        all(meets_at_the_switch(r) for r in rows if r["regime_classes"] == "piecewise_floor"))
    add("the_relative_tolerance_is_continuous_at_the_switch",
        all(relative_meets(r) for r in rows if r["regime_classes"] == "piecewise_floor"))
    add("the_half_unit_crossing_is_the_inverse_of_twice_the_gate",
        all(abs(r["half_unit_crossing"] * float(r["gate_value"]) - 0.5) <=
            1e-9 * max(1.0, abs(r["half_unit_crossing"] * float(r["gate_value"])))
            for r in rows if r["half_unit_crossing"]))
    add("a_fixed_normalisation_is_undone_by_exactly_its_divisor",
        all(abs(r["regime_model"]["absolute_in_the_original_units"]
                - float(r["gate_value"]) * float(r["regime_model"]["divisor"])) <=
            1e-9 * abs(r["regime_model"]["absolute_in_the_original_units"])
            for r in rows if r["regime_classes"] == "constant_after_normalisation"))
    add("no_row_claims_reproducibility_without_publishing_its_scale",
        all(not (r["reproducible_from_the_face"].get("answer")
                 and r["regime_classes"] == "piecewise_floor"
                 and not r["reproducible_from_the_face"].get("scale_published"))
            for r in rows))
    add("a_clamp_engagement_flag_is_never_true_when_the_face_stays_below_the_floor",
        all(not r["clamp_engages_anywhere_on_this_face"]
            for r in rows if (r["clamp_engages_anywhere_on_this_face"] is not None
                              and r["face_max_abs_value"] is not None
                              and r["switch_point"] is not None
                              and r["face_max_abs_value"] >= r["switch_point"])))
    add("every_row_with_a_present_face_publishes_the_maximum_it_was_measured_against",
        all(r["face_max_abs_value"] is not None for r in rows if r["face_state"] == "present"))
    add("a_row_whose_face_is_absent_says_so_instead_of_publishing_a_number",
        all(r["face_max_abs_value"] is None
            for r in rows if r["face_state"] == "absent"))
    add("the_study_never_reads_itself_as_a_producer",
        all("e314_clamped_gate_census" not in (r["face"] or "") for r in rows))
    add("the_clamped_rows_are_the_rows_that_carry_a_floor",
        all(r["regime_classes"] == "piecewise_floor" for r in rows if r["gate_scale_floors"]))
    return checks


# --------------------------------------------------------------------------- cli

def cmd_run():
    p = build()
    c = p["census"]
    print("E314 %s cutoff=%s" % (p["verdict"], p["evidence_cutoff"]))
    print("  rows=%d | regime: piecewise_floor=%d linear=%d constant_after_norm=%d "
          "constant_absolute=%d unresolved=%d"
          % (c["rows"], c["regime_piecewise_floor"], c["regime_linear_in_the_quantity"],
             c["regime_constant_after_normalisation"], c["regime_constant_absolute"],
             c["regime_unresolved"]))
    print("  tolerance depends on the quantity in %d rows | switch point published in %d"
          % (c["rows_whose_tolerance_depends_on_the_quantity"],
             c["rows_publishing_a_switch_point"]))
    print("  clamp never engages on its own face: %d | half unit crossing above the face's "
          "largest number: %d | tolerance half a unit or coarser at that magnitude: %d | named "
          "face absent: %d"
          % (c["rows_where_the_clamp_never_engages_on_their_own_face"],
             c["rows_whose_half_unit_crossing_exceeds_the_faces_largest_number"],
             c["rows_whose_tolerance_is_half_a_unit_or_coarser_at_the_face_maximum"],
             c["rows_whose_named_face_is_absent"]))
    print("  reproducible from the face: yes=%d no=%d (scale not a key: %d, clamp tokens absent: %d)"
          % (c["rows_reproducible_from_the_face"], c["rows_not_reproducible_from_the_face"],
             c["rows_whose_scale_is_not_a_key_on_the_face"],
             c["rows_whose_clamp_tokens_are_absent_from_the_face"]))
    for r in p["clamped_rows"]:
        print("  switch: %s %s gate=%r floor=%r tol_below=%r tol_at_face_max=%r "
              "half_unit_at=%r clamp_engages=%s"
              % (r["face"], r["gate_path"], r["gate_value"], r["switch_point"],
                 r["tolerance_below_the_switch"]["absolute_in_the_quantitys_units"],
                 r["tolerance_at_the_face_maximum_magnitude"], r["half_unit_crossing"],
                 r["clamp_engages_on_this_face"]))
    bad = [x for x in p["identity_checks"] if not x["ok"]]
    print("  identity: %d/%d ok" % (len(p["identity_checks"]) - len(bad), len(p["identity_checks"])))
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
    fresh = build(outdir=os.path.join(ROOT, "results", "_e314_verify"))
    if [(r["regime_classes"], r["switch_point"]) for r in fresh["rows"]] != \
            [(r["regime_classes"], r["switch_point"]) for r in p["rows"]]:
        problems.append("a re-run changes a regime or switch point")
    if [r["reproducible_from_the_face"].get("answer") for r in fresh["rows"]] != \
            [r["reproducible_from_the_face"].get("answer") for r in p["rows"]]:
        problems.append("a re-run changes a reproducibility reading")
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
    m = regime_model(1e-12, [1.0, 1.0], ["max(1.0, prev)"])
    ok &= check("fixture: a floor and a free scale is a piecewise model",
                m["class"] == "piecewise_floor")
    ok &= check("fixture: the switch point is the floor",
                m["switch_point_in_the_scales_units"] == 1.0)
    ok &= check("fixture: below the switch the tolerance is tol*floor, a number",
                m["below_the_switch"]["absolute_in_the_quantitys_units"] == 1e-12)
    ok &= check("fixture: above the switch the tolerance is tol*x, an expression",
                m["above_the_switch"]["absolute_in_the_quantitys_units"] == "tol * x")
    ok &= check("fixture: below the switch the relative tolerance is unbounded",
                "grows without bound" in m["below_the_switch"]["relative_to_the_quantity"])
    ok &= check("fixture: the relative tolerance at the switch equals the gate",
                m["below_the_switch"]["at_the_switch_relative"] == 1e-12)
    m = regime_model(0.002, [], ["session_open"])
    ok &= check("fixture: a free scale with no floor is linear from zero",
                m["class"] == "linear_in_the_quantity")
    ok &= check("fixture: the zero end of a relative band is exact equality",
                m["at_zero_scale"]["reading"].startswith("at x = 0"))
    m = regime_model(1e-12, [], ["100.0"])
    ok &= check("fixture: a literal divisor is a fixed normalisation",
                m["class"] == "constant_after_normalisation")
    ok &= check("fixture: undoing a fixed divisor is exact arithmetic",
                abs(m["absolute_in_the_original_units"] - 1e-10) < 1e-20,
                "got=%r" % (m["absolute_in_the_original_units"],))
    m = regime_model(1e-12, [], [])
    ok &= check("fixture: no scale at all is a constant absolute gate",
                m["class"] == "constant_absolute")
    ok &= check("fixture: the half unit crossing is 0.5/tol",
                half_unit_crossing(1e-12) == 5e11)
    ok &= check("fixture: a zero gate has no half unit crossing",
                half_unit_crossing(0.0) is None)
    mp = regime_model(1e-12, [1.0], ["max(1.0, prev)"])
    ok &= check("fixture: below the floor the tolerance stays flat",
                tolerance_at(mp, 0.5) == 1e-12)
    ok &= check("fixture: above the floor the tolerance scales",
                tolerance_at(mp, 1920.0) == 1.92e-9)
    mc = regime_model(0.1, [], [])
    ok &= check("fixture: a constant gate does not grow with a large number on the face",
                tolerance_at(mc, 20261130.0) == 0.1)
    mn = regime_model(1e-12, [], ["100.0"])
    ok &= check("fixture: a fixed normalisation is undone in the tolerance too",
                abs(tolerance_at(mn, 1e6) - 1e-10) < 1e-22)
    ok &= check("fixture: bools are labels not magnitudes",
                numeric_leaves({"a": True, "b": 3}) == [(3.0, "b")])

    # --- the published face
    c = p["census"]
    ok &= check("identity: every check green", all(x["ok"] for x in p["identity_checks"]))
    ok &= check("findings: three rows carry a clamp",
                c["regime_piecewise_floor"] == 3,
                "got=%d" % c["regime_piecewise_floor"])
    ok &= check("findings: one row is a fixed normalisation",
                c["regime_constant_after_normalisation"] == 1)
    ok &= check("findings: the band-arrival clamp never engages on its own face",
                all(r["clamp_engages_on_this_face"] is False for r in p["clamped_rows"]))
    ok &= check("findings: the clamped rows' half unit crossing is far above their faces' "
                "largest number",
                all(r["half_unit_crossing"] > r["face_max_abs_value"] for r in p["clamped_rows"]))
    ok &= check("findings: one row names a face that does not exist",
                c["rows_whose_named_face_is_absent"] == 1,
                "got=%d" % c["rows_whose_named_face_is_absent"])
    ok &= check("findings: the clamped rows cannot be reproduced from their faces",
                all(r["reproducible_from_the_face"]["answer"] is False for r in p["clamped_rows"]))
    ok &= check("findings: the clamped rows' scale is not a key on the face",
                all(r["face_publishes"]["scale_identifier_in_a_key_name"] is False
                    for r in p["clamped_rows"]))
    ok &= check("findings: the clamped rows' faces carry no clamp token",
                all(r["face_publishes"]["clamp_tokens_on_the_face"] is False
                    for r in p["clamped_rows"]))
    ok &= check("counts: no row is counted twice",
                c["rows"] == len({(r["face"], r["gate_path"], r["leg_expression"]) for r in p["rows"]}))

    # --- mutations must be caught
    m = copy.deepcopy(p)
    for r in m["rows"]:
        if r["regime_classes"] == "piecewise_floor":
            r["switch_point"] = None
            break
    ok &= check("mutation: a clamped row with no switch point is caught",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    for r in m["rows"]:
        if r["regime_classes"] == "piecewise_floor":
            r["regime_model"]["below_the_switch"]["absolute_in_the_quantitys_units"] = 1e-9
            break
    ok &= check("mutation: a broken regime continuity is caught",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    m["census"]["regime_piecewise_floor"] += 1
    ok &= check("mutation: an inflated regime partition is caught",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    for r in m["rows"]:
        if r["regime_classes"] == "piecewise_floor":
            r["reproducible_from_the_face"] = {"answer": True, "gate_published": True,
                                               "scale_published": False, "why": "forged"}
            break
    ok &= check("mutation: a clamped row claiming reproducibility without its scale is caught",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    for r in m["rows"]:
        if r["regime_classes"] == "piecewise_floor":
            r["clamp_engages_anywhere_on_this_face"] = True
            break
    ok &= check("mutation: a clamp declared engaged above the floor is caught",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    m["rows"][0]["half_unit_crossing"] = 5e10
    ok &= check("mutation: a mis-stated half unit crossing is caught",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    for r in m["rows"]:
        if r["face_state"] == "present" and r["face_max_abs_value"] is not None:
            r["face_max_abs_value"] = None
            break
    ok &= check("mutation: a present-face row with no maximum is caught",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    for r in m["rows"]:
        if r["regime_classes"] == "constant_after_normalisation":
            r["regime_model"]["absolute_in_the_original_units"] = 1e-9
            break
    ok &= check("mutation: a mis-undone fixed normalisation is caught",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    m["rows"].append(dict(m["rows"][0]))
    ok &= check("mutation: a duplicated row is caught",
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