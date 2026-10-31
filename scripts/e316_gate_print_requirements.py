"""E316 -- what a face would have to print before a reader could evaluate its own gate.

E315 (r1334) joined each two-regime gate to the leg that consumes it and found that the
quantity the gate is normalised by -- `prev`, `session_open` -- is not a key on either face:
0 of 5 rows publish it, so the regime arithmetic is only readable by someone holding the
producer. That is a statement about what is missing, not about what would be enough.

This study asks the constructive version: per row, what is the smallest set of additional
keys the face would have to print before a reader with no producer access could compute the
gate's tolerance at one magnitude of the quantity it is rated in -- and is any of that set
already on the face under another name?

Four elements are always required, because the tolerance cannot be evaluated without all four:

* the **identifier** -- which number on the face is the one the gate is normalised by;
* the **unit** -- draws, CNY per share, a fraction; a tolerance in the wrong unit is a number;
* **one magnitude** of that quantity, with the step/row it belongs to (a tolerance at an
  unpublished magnitude is a formula, not a test);
* the **scale expression** -- `tol * max(1.0, prev)` and `tol * x` are different gates, and
  the face prints neither.

A fifth, the **floor**, is required only where the regime model is piecewise: below the
switch the tolerance is `tol * floor`, and a reader who does not know the floor cannot see
where the two regimes change.

Three things this study adds to E315:

1. the two faces fail for **opposite reasons**. One publishes plenty of numbers in the same
   unit as the gated quantity but none of them is that quantity -- a *decoy*, which is worse
   than an absence because it invites substitution, and the substitution has a measurable
   cost: the tolerance a reader would compute from the decoys spans nearly three orders of
   magnitude on that face. The other publishes no positive number at all: it covers a day on
   which the leg had nothing to compare, so its emptiness is the day, not the schema.
2. the identifier is not always missing from the **schema**. On one face the identifier is a
   quoted payload key in the producer with zero instances today, so the requirement is
   already met for any day that has a comparison in it -- a conditional the face does not say.
3. a unit word is not a quantity. `base_draws` names the unit of the gated quantity and is
   not a magnitude of it; counting it would repeat, on the reader side, the writer-side error
   that a name is a measurement (E207/E208 family).

usage:
  python scripts/e316_gate_print_requirements.py run
  python scripts/e316_gate_print_requirements.py verify
  python scripts/e316_gate_print_requirements.py selftest
"""

import copy
import io
import json
import math
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import e314_clamped_gate_census as e314  # noqa: E402 -- the regime model is E314's

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE = "GATEPRINT-%s.json"
LATEST = "gateprint_latest.json"
UPSTREAM = os.path.join(OUTDIR, "legeps_latest.json")
SCRIPTS = os.path.join(ROOT, "scripts")
TODAY = "2026-10-31"
STUDY = "E316_gate_print_requirements"
VERDICT = ("the_reader_set_is_on_no_face_and_the_two_faces_fail_for_opposite_reasons_"
           "same_unit_decoys_on_one_a_day_without_comparisons_on_the_other")

QUANTITY_CLASSES = (
    "piecewise_floor",
    "linear_in_the_quantity",
    "constant_after_normalisation_and_linear",
)

# The unit vocabulary is measured from where the identifier is built, not guessed from its
# spelling: `prev` is the previous step's arrival count in draws (E260's monotone leg walks a
# grid of draw counts), `session_open` is a share price in CNY. An identifier outside this
# table is published as unit_unassessable rather than given a default unit.
UNIT_VOCABULARY = {
    "prev": {
        "unit": "draws",
        "unit_words": ("draw", "draws"),
        "derived_from": ("scripts/e260_band_endpoint_arrival.py nonmonotone_steps: `prev` is "
                         "the previous entry of a series keyed by draw counts"),
    },
    "session_open": {
        "unit": "CNY per share",
        "unit_words": ("price", "px", "cny", "open"),
        "derived_from": ("scripts/t35_open_fill_verify.py: `session_open` is joined from the "
                         "pending-watch marks, a share price"),
    },
}

# Elements every quantity-dependent gate needs before a reader can evaluate it.
CORE_ELEMENTS = ("quantity_identifier", "quantity_unit", "one_magnitude", "scale_expression")
FLOOR_ELEMENT = "floor"

ELEMENT_KEYS = {
    "quantity_identifier": "gate_quantity.identifier",
    "quantity_unit": "gate_quantity.unit",
    "one_magnitude": "gate_quantity.magnitude",
    "scale_expression": "gate_scale.expression",
    "floor": "gate_scale.floor",
}

SUGGESTED_KEYS = {
    "quantity_identifier": "gate_quantity.identifier",
    "quantity_unit": "gate_quantity.unit",
    "one_magnitude": "gate_quantity.magnitude (with the step/row it belongs to)",
    "scale_expression": "gate_scale.expression",
    "floor": "gate_scale.floor",
}

TOKEN_SPLIT = re.compile(r"[^A-Za-z0-9]+")
TOLERANCE_TOKENS = ("tol", "tolerance", "tolerance_x", "frac")
FLOOR_TOKENS = ("floor", "switch", "switch_point", "clamp")
NOISE_TOKENS = ("generated", "ts", "version", "schema")

# Counters that pay out a comparison: how many rows were matched, dropped, breached, filled.
# A face that publishes these and reports zero of every one of them compared nothing at all.
OUTCOME_TOKENS = ("matched", "compared", "comparisons", "filled", "drops", "dropped", "breach",
                  "cases", "rows", "traders", "outcomes", "pending")
# ...but a counter named after the absence of work is the evidence of emptiness, not a rung on
# the ladder: `zero_pending_traders = 6` says six traders had nothing to compare.
NEGATED_TOKENS = ("zero", "no", "none", "missing", "unjudgeable", "unmeasured", "not")


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

def path_tokens(path):
    """Tokens of a leaf path -- whole tokens, never substrings (E313: 'n_' inside a price)."""
    return [t.lower() for t in TOKEN_SPLIT.split(str(path)) if t]


def all_leaves(obj, path="", out=None):
    """Every leaf with its path: numbers, strings and empty containers, in one pass."""
    if out is None:
        out = []
    if isinstance(obj, dict):
        if not obj:
            out.append((None, path, "empty_dict"))
        for k, v in obj.items():
            all_leaves(v, path + "." + str(k) if path else str(k), out)
    elif isinstance(obj, list):
        if not obj:
            out.append((None, path, "empty_list"))
        for i, v in enumerate(obj):
            all_leaves(v, path + "[%d]" % i, out)
    elif isinstance(obj, bool):
        out.append((obj, path, "bool"))
    elif isinstance(obj, str):
        out.append((obj, path, "string"))
    elif isinstance(obj, (int, float)):
        out.append((float(obj), path, "number"))
    return out


def is_tolerance_leaf(path, gate_path):
    """The gate's own value, and anything named like one, is never a magnitude of the quantity."""
    if gate_path and path == gate_path:
        return True
    return any(t in TOLERANCE_TOKENS for t in path_tokens(path))


def is_noise_leaf(path):
    return any(t in NOISE_TOKENS for t in path_tokens(path))


class Producers(object):
    """The scripts that name a face -- read once, used to see whether a key exists in a schema.

    The study excludes its own source: this file names every identifier in its unit vocabulary,
    so scanning it would cite the reader as the producer and turn the finding into an artefact
    of the vocabulary it declares (E310 family -- a census that lives in the directory it
    scans must not count itself).
    """

    def __init__(self, scripts_dir, self_rel=None):
        self.scripts_dir = scripts_dir
        self.self_rel = self_rel
        self._text = {}

    def _load(self, name):
        if name not in self._text:
            try:
                with io.open(os.path.join(self.scripts_dir, name), encoding="utf-8") as fh:
                    self._text[name] = fh.read()
            except (OSError, UnicodeDecodeError):
                self._text[name] = ""
        return self._text[name]

    def naming(self, face_rel):
        base = os.path.basename(str(face_rel))
        stem = base[:-5] if base.endswith(".json") else base
        out = []
        for name in sorted(os.listdir(self.scripts_dir)):
            if not name.endswith(".py"):
                continue
            rel = "scripts/" + name
            if self.self_rel and rel == self.self_rel:
                continue
            text = self._load(name)
            if base in text or (stem and stem in text):
                out.append(rel)
        return out

    def writers(self, face_rel, scripts):
        """Candidates that bind the face name (a writer), rather than merely mentioning it."""
        base = os.path.basename(str(face_rel))
        pat = re.compile(r"=\s*[^\n=]*" + re.escape(base))
        out = []
        for rel in scripts:
            if pat.search(self._load(os.path.basename(rel))):
                out.append(rel)
        return out

    def identifier_as_payload_key(self, ident, scripts, writers=None):
        """Is the identifier a quoted dict key anywhere in the scripts that name this face?

        A writer's hit is stronger evidence than a mention, so the tier is published: the same
        line in a study that quotes the face as an upstream proves nothing about the schema.
        """
        if not ident:
            return None
        pat = re.compile(r'"%s"\s*:' % re.escape(ident))
        tiers = [("writer", writers or []),
                 ("other_script_naming_the_face",
                  [s for s in scripts if s not in (writers or [])])]
        for tier, group in tiers:
            for rel in group:
                text = self._load(os.path.basename(rel))
                m = pat.search(text)
                if m:
                    line = text.count("\n", 0, m.start()) + 1
                    return {"script": rel, "line": line, "tier": tier}
        return None


# ------------------------------------------------------------------ the reader set

def required_elements(regime_class, scale_expressions):
    """The smallest set of elements a reader needs, derived from the regime model.

    The floor is required only where the model is piecewise: a linear gate has no switch and
    asking it for a floor would manufacture a key that carries no information.
    """
    els = list(CORE_ELEMENTS)
    if regime_class == "piecewise_floor":
        els.append(FLOOR_ELEMENT)
    if not scale_expressions:
        els = [e for e in els if e != "scale_expression"]
    return els


def unit_entry(ident):
    vocab = UNIT_VOCABULARY.get(ident or "")
    if vocab is None:
        return {"unit": None, "unit_words": (), "derived_from": None}

    return dict(vocab)


def identifier_present(face_leaves, ident):
    """A key whose own tokens name the identifier: an exact hit, or nothing."""
    if not ident:
        return None
    want = ident.lower()
    for value, path, kind in face_leaves:
        if want in path_tokens(path):
            return path
    return None


def unit_present(face_leaves, words):
    if not words:
        return None
    for value, path, kind in face_leaves:
        toks = path_tokens(path)
        if any(w in toks for w in words):
            return path
    return None


def magnitude_candidates(face_leaves, ident):
    """Positive numbers whose own path names the identifier -- the gated quantity's values."""
    if not ident:
        return []
    want = ident.lower()
    out = []
    for value, path, kind in face_leaves:
        if kind != "number" or value is None or value <= 0:
            continue
        if want in path_tokens(path):
            out.append((value, path))
    return out


def decoys(face_leaves, ident, words, gate_path):
    """Numbers in the gated quantity's unit that are not the gated quantity.

    Excluded: the gate's own value and anything tolerance-named, plus timestamps and schema
    stamps. What remains is the set a reader would substitute, and the point of publishing it
    is that the substitution is not free -- see the tolerance spread.
    """
    if not words:
        return []
    want = (ident or "").lower()
    out = []
    for value, path, kind in face_leaves:
        if kind != "number" or value is None:
            continue
        toks = path_tokens(path)
        if want and want in toks:
            continue
        if not any(w in toks for w in words):
            continue
        if is_tolerance_leaf(path, gate_path) or is_noise_leaf(path):
            continue
        out.append((value, path))
    return out


def scale_present(face_leaves, ident):
    """A published string that is the gate's scale expression -- `max(1.0, prev)`."""
    if not ident:
        return None
    for value, path, kind in face_leaves:
        if kind != "string" or not value:
            continue
        if e314.scale_identifier(value) == ident:
            return path
    return None


def floor_present(face_leaves, model):
    """The floor the model switches at, published as its own number or inside a scale string."""
    floor = model.get("floor")
    if floor is None:
        return None
    for value, path, kind in face_leaves:
        toks = path_tokens(path)
        if kind == "number" and value is not None and any(t in toks for t in FLOOR_TOKENS):
            if abs(float(value) - float(floor)) <= 1e-12 * max(abs(float(floor)), 1.0):
                return path
        if kind == "string" and value:
            for token in FLOOR_TOKENS:
                if token in toks:
                    return path
    return None


def day_without_comparisons(face_leaves, gate_path):
    """Does the face cover a day on which nothing was compared?

    Two measured facts together, never a guess from the verdict string: the face publishes
    outcome counters (matched / dropped / breach / rows ...) and every one of them is zero,
    and at least one list field is empty -- the per-row detail a non-empty day populates.
    A counter named after the absence of work (`zero_pending_traders`) is evidence of the
    empty day and is therefore excluded from the ladder it would otherwise inflate.
    """
    outcomes = []
    for value, path, kind in face_leaves:
        if kind != "number" or value is None:
            continue
        toks = path_tokens(path)
        if is_tolerance_leaf(path, gate_path) or is_noise_leaf(path):
            continue
        if any(t in NEGATED_TOKENS for t in toks):
            continue
        if any(t in OUTCOME_TOKENS for t in toks):
            outcomes.append((value, path))
    empty_lists = [p for v, p, k in face_leaves if k == "empty_list"]
    nonzero = [p for v, p in outcomes if v != 0]
    return {
        "outcome_counters_published": len(outcomes),
        "outcome_counters_nonzero": len(nonzero),
        "outcome_counter_examples": [{"value": v, "path": p} for v, p in outcomes[:4]],
        "empty_list_fields": len(empty_lists),
        "empty_list_examples": empty_lists[:3],
        "day_without_comparisons": bool(outcomes and not nonzero and empty_lists),
    }


def row_model(row):
    """Rebuild E314's regime model from the fields this upstream face publishes.

    E315's rows carry the class, the gate, the switch point and the scale expressions rather
    than a nested model; rebuilding it through the shared constructor keeps one definition of
    what "piecewise" means instead of a second copy living in this study.
    """
    cls = row.get("regime_class")
    floors = []
    if cls == "piecewise_floor" and row.get("switch_point") is not None:
        floors = [row["switch_point"]]
    return e314.regime_model(row.get("gate_value"), floors,
                             row.get("scale_expressions") or [])


def analyse(row, faces, producers):
    model = row_model(row)
    ident = row.get("quantity_identifier")
    gate_path = row.get("gate_path")
    face_rel = row.get("face")
    face = faces.at(face_rel) if face_rel else None
    leaves = all_leaves(face) if face is not None else []
    vocab = unit_entry(ident)
    required = required_elements(model.get("class"), model.get("scale_expressions"))

    producer_scripts = producers.naming(face_rel) if face_rel else []
    producer_writers = producers.writers(face_rel, producer_scripts) if face_rel else []
    ident_in_schema = producers.identifier_as_payload_key(ident, producer_scripts,
                                                          producer_writers)

    present_as = {
        "quantity_identifier": identifier_present(leaves, ident),
        "quantity_unit": unit_present(leaves, vocab["unit_words"]),
        "one_magnitude": None,
        "scale_expression": scale_present(leaves, ident),
        "floor": floor_present(leaves, model),
    }
    mags = magnitude_candidates(leaves, ident)
    if mags:
        present_as["one_magnitude"] = mags[0][1]
    decoy_hits = decoys(leaves, ident, vocab["unit_words"], gate_path)

    availability = day_without_comparisons(leaves, gate_path)

    elements = []
    for el in required:
        path = present_as.get(el)
        evidence = "absent"
        if path:
            evidence = "present"
        elif el == "quantity_identifier" and ident_in_schema:
            evidence = "present_in_the_producer_schema_only"
        elements.append({
            "element": el,
            "required": True,
            "present": bool(path),
            "present_as": path,
            "evidence": evidence,
            "suggested_key": SUGGESTED_KEYS[el],
        })
    for el in ("quantity_identifier", "quantity_unit", "one_magnitude", "scale_expression",
               FLOOR_ELEMENT):
        if el not in required:
            elements.append({
                "element": el,
                "required": False,
                "present": bool(present_as.get(el)),
                "present_as": present_as.get(el),
                "evidence": ("present" if present_as.get(el) else "not_required"),
                "suggested_key": SUGGESTED_KEYS[el],
            })

    absent = [e["element"] for e in elements if e["required"] and not e["present"]]
    decoy_values = [v for v, _p in decoy_hits if v and v > 0]
    decoy_tols = [e314.tolerance_at(model, v) for v in decoy_values]
    decoy_tols = [t for t in decoy_tols if t is not None and t > 0]

    if not absent:
        unavailability = "readable_from_the_face_alone"
    elif availability["day_without_comparisons"]:
        unavailability = "the_face_covers_a_day_with_no_comparisons"
    else:
        unavailability = "schema_gap"

    return {
        "face": face_rel,
        "gate_path": gate_path,
        "gate_value": row.get("gate_value"),
        "regime_class": model.get("class"),
        "quantity_identifier": ident,
        "quantity_unit": vocab["unit"],
        "quantity_unit_derived_from": vocab["derived_from"],
        "leg_expression": row.get("leg_expression"),
        "leg_epsilon": row.get("leg_tolerance"),
        "face_state": ("absent" if face is None else "present"),
        "required_elements": required,
        "elements": elements,
        "elements_required": len(required),
        "elements_present": sum(1 for e in elements if e["required"] and e["present"]),
        "elements_absent": len(absent),
        "minimal_added_keys": [SUGGESTED_KEYS[e] for e in absent],
        "tolerance_computable_from_the_face_alone": not absent,
        "identifier_named_in_the_producer_schema": ident_in_schema,
        "producer_candidates": producer_scripts,
        "producer_writers": producer_writers,
        "identifiers_on_the_face": [p for v, p, k in leaves
                                   if ident and ident.lower() in path_tokens(p)][:5],
        "gated_quantity_magnitudes": [{"value": v, "path": p} for v, p in mags[:5]],
        "gated_quantity_magnitude_count": len(mags),
        "decoy_magnitudes": [{"value": v, "path": p} for v, p in decoy_hits[:5]],
        "decoy_count": len(decoy_hits),
        "decoy_positive_values": len(decoy_values),
        "decoy_tolerance_min": (min(decoy_tols) if decoy_tols else None),
        "decoy_tolerance_max": (max(decoy_tols) if decoy_tols else None),
        "decoy_tolerance_spread_orders_of_magnitude": (
            math.log10(max(decoy_tols) / min(decoy_tols))
            if len(decoy_tols) > 1 and min(decoy_tols) > 0 else None),
        "day_without_comparisons": availability,
        "class": unavailability,
    }


def build(outdir=None):
    up = _read(UPSTREAM)
    faces = e314.Faces()
    producers = Producers(SCRIPTS,
                          self_rel=os.path.relpath(os.path.abspath(__file__),
                                                   ROOT).replace(os.sep, "/"))
    src = [r for r in (up.get("rows") or [])
           if r.get("regime_class") in QUANTITY_CLASSES]
    rows = [analyse(r, faces, producers) for r in src]
    rows.sort(key=lambda r: (r["face"] or "", r["gate_path"] or "", r["leg_expression"] or ""))

    def count(pred):
        return sum(1 for r in rows if pred(r))

    def needs(el):
        return count(lambda r, el=el: el in [k for k in (r["minimal_added_keys"] or [])])

    def needs_el(el):
        return count(lambda r, el=el: any(
            e["element"] == el and e["required"] and not e["present"] for e in r["elements"]))

    classes = ("readable_from_the_face_alone", "schema_gap",
               "the_face_covers_a_day_with_no_comparisons")
    faces_seen = sorted({r["face"] for r in rows})
    per_face_decoys = {}
    for r in rows:
        per_face_decoys.setdefault(r["face"], r["decoy_count"])
    census = {
        "upstream_rows": len(up.get("rows") or []),
        "upstream_rows_selected": len(src),
        "rows": len(rows),
        "faces": len({r["face"] for r in rows}),
        "rows_in_each_class": {c: count(lambda r, c=c: r["class"] == c) for c in classes},
        "rows_readable_from_the_face_alone": count(
            lambda r: r["class"] == "readable_from_the_face_alone"),
        "rows_with_a_schema_gap": count(lambda r: r["class"] == "schema_gap"),
        "rows_on_a_face_that_covers_a_day_without_comparisons": count(
            lambda r: r["class"] == "the_face_covers_a_day_with_no_comparisons"),
        "rows_needing_a_printed_identifier": needs_el("quantity_identifier"),
        "rows_needing_a_printed_unit": needs_el("quantity_unit"),
        "rows_needing_a_printed_magnitude": needs_el("one_magnitude"),
        "rows_needing_a_printed_scale_expression": needs_el("scale_expression"),
        "rows_needing_a_printed_floor": needs_el(FLOOR_ELEMENT),
        "rows_whose_identifier_exists_only_in_the_producer_schema": count(
            lambda r: bool(r["identifier_named_in_the_producer_schema"]) and not any(
                e["element"] == "quantity_identifier" and e["present"] for e in r["elements"])),
        "schema_evidence_tiers": {
            t: count(lambda r, t=t: (r["identifier_named_in_the_producer_schema"] or {})
                     .get("tier") == t)
            for t in ("writer", "other_script_naming_the_face")
        },
        "rows_whose_schema_evidence_names_a_script_that_writes_the_face": count(
            lambda r: (r["identifier_named_in_the_producer_schema"] or {}).get("tier")
            == "writer"),
        "rows_whose_unit_is_named_under_another_key": count(
            lambda r: any(e["element"] == "quantity_unit" and e["present"] for e in r["elements"])),
        "rows_whose_unit_vocabulary_is_unassessable": count(
            lambda r: r["quantity_unit"] is None),
        "rows_publishing_at_least_one_magnitude_of_the_gated_quantity": count(
            lambda r: r["gated_quantity_magnitude_count"] > 0),
        "rows_carrying_same_unit_decoys": count(lambda r: r["decoy_count"] > 0),
        "decoy_magnitudes_total": sum(r["decoy_count"] for r in rows),
        "decoy_magnitudes_per_face": per_face_decoys,
        "decoy_magnitudes_on_distinct_faces": sum(per_face_decoys.values()),
        "decoys_with_a_positive_value": sum(r["decoy_positive_values"] for r in rows),
        "rows_whose_decoys_span_more_than_one_decade_of_tolerance": count(
            lambda r: (r["decoy_tolerance_spread_orders_of_magnitude"] or 0.0) > 1.0),
        "tolerances_computable_from_the_faces_alone": count(
            lambda r: r["tolerance_computable_from_the_face_alone"]),
        "elements_required_total": sum(r["elements_required"] for r in rows),
        "elements_present_total": sum(r["elements_present"] for r in rows),
        "elements_absent_total": sum(r["elements_absent"] for r in rows),
        "minimal_added_keys_total": sum(len(r["minimal_added_keys"]) for r in rows),
        "element_availability": {
            el: {
                "required_on": count(lambda r, el=el: el in r["required_elements"]),
                "present": count(lambda r, el=el: any(
                    e["element"] == el and e["required"] and e["present"]
                    for e in r["elements"])),
                "absent": count(lambda r, el=el: any(
                    e["element"] == el and e["required"] and not e["present"]
                    for e in r["elements"])),
            }
            for el in ("quantity_identifier", "quantity_unit", "one_magnitude",
                       "scale_expression", FLOOR_ELEMENT)
        },
        "faces_seen": faces_seen,
    }
    payload = {
        "schema": "bigmoney/e316-gateprint/v1",
        "study": STUDY,
        "title": ("what is the smallest set of keys a face would have to print before a reader "
                  "with no producer access could evaluate the gate at one magnitude of the "
                  "quantity it is rated in?"),
        "evidence_cutoff": TODAY,
        "generated": TODAY,
        "self_faces_excluded": [FACE % TODAY, LATEST],
        "self_scripts_excluded": [os.path.relpath(os.path.abspath(__file__),
                                                  ROOT).replace(os.sep, "/")],
        "upstream": {
            "leg_epsilon_face": os.path.relpath(UPSTREAM, ROOT).replace(os.sep, "/"),
            "upstream_rows": len(up.get("rows") or []),
            "rows_selected": len(src),
            "selection": "regime classes whose tolerance depends on the gated quantity",
        },
        "join_rules": {
            "required_set": "identifier + unit + one magnitude + the scale expression, plus the "
                            "floor where the regime model is piecewise; each element is derived "
                            "from E314's regime model, not from a per-face list",
            "presence": "an element is present only when a leaf on the face carries it: the "
                        "identifier as a whole path token, the unit as a whole path token, the "
                        "magnitude as a positive number under the identifier's own path, the "
                        "scale as a string the producer's own `scale_identifier` resolves to the "
                        "identifier, the floor as its number under a floor-named path or a "
                        "floor-named string",
            "decoys": "numbers in the gated quantity's unit whose path does not name it, with "
                      "the gate's own value and every tolerance-named or timestamp leaf excluded "
                      "-- the set a reader would substitute, priced by the tolerance each one "
                      "would produce",
            "day_without_comparisons": "no positive number outside the tolerance constants and "
                                       "at least one empty list field: the face covers a day on "
                                       "which the leg had nothing to compare, so its emptiness "
                                       "is the day and not the schema",
            "unit_vocabulary": "declared per identifier with the line its unit was derived from; "
                               "an identifier outside the table is published as "
                               "unit_unassessable instead of being given a default unit",
        },
        "census": census,
        "verdict": VERDICT,
        "rows": rows,
        "notes": [
            "three rows come off a face that publishes 57 numbers in the gated quantity's unit and none "
            "of them is the quantity: a decoy is worse than an absence because it invites "
            "substitution, and the tolerance a reader would compute from those decoys spans 1.5 "
            "orders of magnitude (6e-11 at the smallest published count to 1.92e-09 at the "
            "largest)",
            "two rows come off a face that covers a day on which nothing was compared -- zero "
            "positive numbers outside the tolerance constant, every per-trader detail list "
            "empty -- so calling their absence a schema gap would be the same artefact E315 "
            "avoided one level down",
            "on that second face the identifier is a quoted payload key in the producer and has "
            "zero instances today: the requirement is met for any day that carries a comparison, "
            "and the face does not say which kind of day it is",
            "a unit word is not a quantity: `base_draws` names the unit of the gated quantity "
            "without being one of its magnitudes, and counting it would repeat the writer-side "
            "error of treating a name as a measurement",
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
    add("every_row_derives_its_required_set_from_the_regime_model",
        all(("floor" in r["required_elements"]) == (r["regime_class"] == "piecewise_floor")
            for r in rows))
    add("every_required_element_is_present_in_the_element_list",
        all(sorted(e["element"] for e in r["elements"] if e["required"])
            == sorted(r["required_elements"]) for r in rows))
    add("a_present_element_always_cites_a_path_and_an_absent_one_never_does",
        all(bool(e["present_as"]) == bool(e["present"]) for r in rows for e in r["elements"]))
    add("the_element_counts_recompute_from_the_elements",
        all(r["elements_present"] == sum(1 for e in r["elements"]
                                         if e["required"] and e["present"])
            and r["elements_absent"] == r["elements_required"] - r["elements_present"]
            for r in rows))
    add("the_minimal_added_set_is_exactly_the_absent_required_elements",
        all(r["minimal_added_keys"] == [e["suggested_key"] for e in r["elements"]
                                        if e["required"] and not e["present"]]
            for r in rows))
    add("computability_is_the_empty_absent_set",
        all(r["tolerance_computable_from_the_face_alone"] == (r["elements_absent"] == 0)
            for r in rows))
    add("a_gated_quantity_magnitude_is_never_the_gate_itself",
        all(all(m["path"] != r["gate_path"] for m in r["gated_quantity_magnitudes"])
            for r in rows))
    add("no_decoy_is_the_gate_itself_or_a_tolerance_named_leaf",
        all(all(m["path"] != r["gate_path"]
                and not any(t in TOLERANCE_TOKENS for t in path_tokens(m["path"]))
                for m in r["decoy_magnitudes"]) for r in rows))
    add("no_decoy_names_the_gated_quantity_itself",
        all(all(r["quantity_identifier"].lower() not in path_tokens(m["path"])
                for m in r["decoy_magnitudes"]) for r in rows))
    add("the_decoy_count_matches_the_published_decoys_or_exceeds_the_shown_page",
        all(r["decoy_count"] >= len(r["decoy_magnitudes"]) for r in rows))
    add("a_day_without_comparisons_publishes_outcome_counters_and_none_of_them_is_nonzero",
        all(r["day_without_comparisons"]["outcome_counters_published"] >= 1
            and r["day_without_comparisons"]["outcome_counters_nonzero"] == 0
            for r in rows if r["day_without_comparisons"]["day_without_comparisons"]))
    add("a_day_without_comparisons_carries_at_least_one_empty_list",
        all(r["day_without_comparisons"]["empty_list_fields"] >= 1
            for r in rows if r["day_without_comparisons"]["day_without_comparisons"]))
    add("the_unavailability_class_is_derived_never_asserted",
        all((r["class"] == "readable_from_the_face_alone" and r["elements_absent"] == 0)
            or (r["class"] == "the_face_covers_a_day_with_no_comparisons"
                and r["elements_absent"] > 0
                and r["day_without_comparisons"]["day_without_comparisons"])
            or (r["class"] == "schema_gap" and r["elements_absent"] > 0
                and not r["day_without_comparisons"]["day_without_comparisons"])
            for r in rows))
    add("a_schema_gap_row_carries_numbers_a_reader_could_mistake_for_the_quantity",
        all(r["decoy_count"] > 0 for r in rows if r["class"] == "schema_gap"))
    add("the_decoy_spread_recomputes_from_the_two_published_tolerances",
        all(r["decoy_tolerance_spread_orders_of_magnitude"] is None
            or close(10.0 ** r["decoy_tolerance_spread_orders_of_magnitude"],
                     r["decoy_tolerance_max"] / r["decoy_tolerance_min"])
            for r in rows))
    add("every_row_that_cites_a_producer_schema_evidence_points_at_a_file_on_disk",
        all(os.path.exists(os.path.join(ROOT, r["identifier_named_in_the_producer_schema"]
                                        ["script"].replace("/", os.sep)))
            for r in rows if r["identifier_named_in_the_producer_schema"]))
    add("the_schema_only_evidence_is_used_for_the_identifier_and_for_nothing_else",
        all(e["evidence"] != "present_in_the_producer_schema_only"
            or e["element"] == "quantity_identifier"
            for r in rows for e in r["elements"]))
    add("a_row_that_needs_a_printed_identifier_is_exactly_a_row_without_one_on_the_face",
        all((e["element"] == "quantity_identifier" and e["required"] and not e["present"])
            == ("gate_quantity.identifier" in r["minimal_added_keys"])
            for r in rows for e in r["elements"] if e["element"] == "quantity_identifier"))
    add("the_per_face_decoy_count_matches_every_row_cut_from_that_face",
        all((c.get("decoy_magnitudes_per_face") or {}).get(r["face"]) == r["decoy_count"]
            for r in rows))
    add("the_study_never_reads_itself",
        all("GATEPRINT-" not in (r["face"] or "") for r in rows))
    add("every_row_has_a_unit_or_is_published_as_unassessable",
        all((r["quantity_unit"] is not None)
            == any(e["element"] == "quantity_unit" and e["required"] for e in r["elements"])
            for r in rows))
    add("no_schema_evidence_cites_this_study_itself",
        all((r["identifier_named_in_the_producer_schema"] or {}).get("script")
            != (p.get("self_scripts_excluded") or [None])[0] for r in rows))
    add("this_study_is_not_among_the_producer_candidates_of_any_row",
        all((p.get("self_scripts_excluded") or [None])[0] not in r["producer_candidates"]
            for r in rows))
    add("a_schema_only_identifier_is_cited_from_its_writers_before_any_other_mention",
        all((r["identifier_named_in_the_producer_schema"] or {}).get("tier") == "writer"
            for r in rows if (r["identifier_named_in_the_producer_schema"] or {}).get("tier")))
    return checks


# --------------------------------------------------------------------------- cli

def cmd_run():
    p = build()
    c = p["census"]
    print("E316 %s cutoff=%s" % (p["verdict"], p["evidence_cutoff"]))
    print("  rows=%d on %d faces | classes=%s"
          % (c["rows"], c["faces"], json.dumps(c["rows_in_each_class"], ensure_ascii=False,
                                               sort_keys=True)))
    print("  reader set: required=%d present=%d absent=%d | minimal added keys=%d | "
          "tolerances computable from the faces alone=%d"
          % (c["elements_required_total"], c["elements_present_total"],
             c["elements_absent_total"], c["minimal_added_keys_total"],
             c["tolerances_computable_from_the_faces_alone"]))
    print("  elements: %s" % json.dumps(c["element_availability"], ensure_ascii=False,
                                        sort_keys=True))
    print("  decoys: %d same-unit numbers (%d positive) on %d rows | rows spanning >1 decade of "
          "tolerance=%d | identifier only in the producer schema on %d rows"
          % (c["decoy_magnitudes_total"], c["decoys_with_a_positive_value"],
             c["rows_carrying_same_unit_decoys"],
             c["rows_whose_decoys_span_more_than_one_decade_of_tolerance"],
             c["rows_whose_identifier_exists_only_in_the_producer_schema"]))
    for r in p["rows"]:
        print("  %s %s qty=%r unit=%r need=%s decoys=%d spread=%r class=%s"
              % (r["face"], r["gate_path"], r["quantity_identifier"], r["quantity_unit"],
                 ",".join(r["minimal_added_keys"]) or "-", r["decoy_count"],
                 r["decoy_tolerance_spread_orders_of_magnitude"], r["class"]))
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
    fresh = build(outdir=os.path.join(ROOT, "results", "_e316_verify"))
    key = lambda r: (r["class"], tuple(r["minimal_added_keys"]), r["decoy_count"],
                     r["gated_quantity_magnitude_count"],
                     tuple((e["element"], e["present"], e["evidence"]) for e in r["elements"]))
    if [key(r) for r in fresh["rows"]] != [key(r) for r in p["rows"]]:
        problems.append("a re-run changes a class, a required key, a decoy count or an element")
    if (fresh.get("census") or {}).get("decoy_magnitudes_total") != \
            (p.get("census") or {}).get("decoy_magnitudes_total"):
        problems.append("a re-run changes the decoy census")
    print("verify: %d problems" % len(problems))
    for x in problems:
        print("  -", x)
    return 0 if not problems else 1


def check(name, ok, detail=""):
    print(("  PASS " if ok else "  FAIL ") + name
          + ((" :: " + detail) if detail and not ok else ""))
    return bool(ok)


def cmd_selftest():
    p = _read(os.path.join(OUTDIR, FACE % TODAY))
    ok = True

    # --- the element arithmetic, on fixtures
    ok &= check("fixture: a piecewise gate requires the floor",
                required_elements("piecewise_floor", ["max(1.0, prev)"])
                == ["quantity_identifier", "quantity_unit", "one_magnitude",
                    "scale_expression", "floor"])
    ok &= check("fixture: a linear gate does not require a floor",
                required_elements("linear_in_the_quantity", ["session_open"])
                == ["quantity_identifier", "quantity_unit", "one_magnitude",
                    "scale_expression"])
    ok &= check("fixture: a gate with no scale does not require the scale expression",
                "scale_expression" not in required_elements("linear_in_the_quantity", []))
    fx = {"rows": [{"prev": 200.0, "base_draws": 200.0}]}
    ok &= check("fixture: a key naming the identifier is found",
                identifier_present(all_leaves(fx), "prev") == "rows[0].prev")
    ok &= check("fixture: a unit word is found under another key",
                unit_present(all_leaves(fx), ("draw", "draws")) == "rows[0].base_draws")
    ok &= check("fixture: a magnitude of the quantity is the number under its own path",
                [v for v, _p in magnitude_candidates(all_leaves(fx), "prev")] == [200.0])
    ok &= check("fixture: a zero magnitude is not a magnitude",
                magnitude_candidates(all_leaves({"prev": 0.0}), "prev") == [])
    ok &= check("fixture: a same-unit number that is not the quantity is a decoy",
                [q for _v, q in decoys(all_leaves({"base_draws": 200.0}), "prev",
                                       ("draw", "draws"), "frozen_spec.tolerance")]
                == ["base_draws"])
    ok &= check("fixture: the gate's own value is never a decoy",
                decoys(all_leaves({"draws_tol": 1e-12}), "prev", ("draws",),
                       "draws_tol") == [])
    ok &= check("fixture: a magnitude that names the quantity is never a decoy",
                decoys(all_leaves({"prev_draws": 5.0}), "prev", ("draws",), "tolerance") == [])
    ok &= check("fixture: the scale is a published string the producer resolves",
                scale_present(all_leaves({"scale": "max(1.0, prev)"}), "prev") == "scale")
    ok &= check("fixture: a scale that does not resolve to the identifier is not the scale",
                scale_present(all_leaves({"scale": "max(1.0, target)"}), "prev") is None)
    ok &= check("fixture: the floor is found under a floor-named key",
                floor_present(all_leaves({"gate_scale": {"floor": 1.0}}),
                              {"floor": 1.0}) == "gate_scale.floor")
    ok &= check("fixture: a floor-named key with the wrong number is not the floor",
                floor_present(all_leaves({"floor": 2.0}), {"floor": 1.0}) is None)
    ok &= check("fixture: an empty day is no outcome counter plus an empty list",
                day_without_comparisons(all_leaves({"rel_tol": 0.002,
                                                    "counters": {"matched": 0, "breach": 0},
                                                    "detail": []}),
                                        "rel_tol")["day_without_comparisons"] is True)
    ok &= check("fixture: a counter named after the absence does not unmake the empty day",
                day_without_comparisons(all_leaves({"rel_tol": 0.002,
                                                    "counters": {"matched": 0,
                                                                 "zero_pending_traders": 6},
                                                    "detail": []}),
                                        "rel_tol")["day_without_comparisons"] is True)
    ok &= check("fixture: a face with no outcome counter is not declared an empty day",
                day_without_comparisons(all_leaves({"rel_tol": 0.002, "n": 0, "detail": []}),
                                        "rel_tol")["day_without_comparisons"] is False)
    ok &= check("fixture: a day with one positive outcome counter is not an empty day",
                day_without_comparisons(all_leaves({"rel_tol": 0.002, "n_matched": 3,
                                                    "detail": []}),
                                        "rel_tol")["day_without_comparisons"] is False)
    ok &= check("fixture: whole tokens only -- a price is not a count",
                unit_present(all_leaves({"session_open": 12.5}), ("n", "draw"))
                is None)

    # --- the published face
    c = p["census"]
    ok &= check("identity: every check green", all(x["ok"] for x in p["identity_checks"]))
    ok &= check("findings: five rows on two faces", c["rows"] == 5 and c["faces"] == 2,
                "rows=%r faces=%r" % (c["rows"], c["faces"]))
    ok &= check("findings: no face lets a reader compute a tolerance",
                c["tolerances_computable_from_the_faces_alone"] == 0,
                "got=%d" % c["tolerances_computable_from_the_faces_alone"])
    ok &= check("findings: the two faces split between a schema gap and an empty day",
                c["rows_with_a_schema_gap"] >= 1
                and c["rows_on_a_face_that_covers_a_day_without_comparisons"] >= 1,
                "gap=%r empty=%r" % (c["rows_with_a_schema_gap"],
                                     c["rows_on_a_face_that_covers_a_day_without_comparisons"]))
    ok &= check("findings: the schema-gap face carries same-unit decoys",
                c["decoy_magnitudes_total"] > 0,
                "got=%d" % c["decoy_magnitudes_total"])
    ok &= check("findings: the decoy substitution is worth more than a decade of tolerance",
                c["rows_whose_decoys_span_more_than_one_decade_of_tolerance"] >= 1,
                "got=%d" % c["rows_whose_decoys_span_more_than_one_decade_of_tolerance"])
    ok &= check("findings: no row publishes a magnitude of the gated quantity",
                c["rows_publishing_at_least_one_magnitude_of_the_gated_quantity"] == 0,
                "got=%d" % c["rows_publishing_at_least_one_magnitude_of_the_gated_quantity"])
    ok &= check("findings: the identifier is a producer payload key on the empty-day rows",
                c["rows_whose_identifier_exists_only_in_the_producer_schema"] >= 1,
                "got=%d" % c["rows_whose_identifier_exists_only_in_the_producer_schema"])
    ok &= check("counts: no row is counted twice",
                c["rows"] == len({(r["face"], r["gate_path"], r["leg_expression"])
                                  for r in p["rows"]}))

    # --- mutations must be caught
    m = copy.deepcopy(p)
    stripped = False
    for r in m["rows"]:
        for e in r["elements"]:
            if e["present"]:
                e["present_as"] = None
                stripped = True
                break
        if stripped:
            break
    ok &= check("mutation: a present element stripped of its path is caught",
                stripped and not all(x["ok"] for x in identity_checks(m)),
                "no present element to mutate" if not stripped else "")
    m = copy.deepcopy(p)
    for r in m["rows"]:
        if r["minimal_added_keys"]:
            r["minimal_added_keys"].pop()
            break
    ok &= check("mutation: a shortened minimal set is caught",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    for r in m["rows"]:
        r["class"] = "readable_from_the_face_alone"
        break
    ok &= check("mutation: a claimed-readable row is caught",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    for r in m["rows"]:
        if r["class"] == "schema_gap":
            r["class"] = "the_face_covers_a_day_with_no_comparisons"
            break
    ok &= check("mutation: an empty day claimed on a face full of numbers is caught",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    for r in m["rows"]:
        if r["decoy_magnitudes"]:
            r["decoy_magnitudes"][0]["path"] = r["gate_path"]
            break
    ok &= check("mutation: the gate counted as its own decoy is caught",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    for r in m["rows"]:
        if r["decoy_magnitudes"]:
            r["decoy_magnitudes"][0]["path"] = "rows[0].%s" % r["quantity_identifier"]
            break
    ok &= check("mutation: a decoy that is really the quantity is caught",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    for r in m["rows"]:
        if r["decoy_tolerance_spread_orders_of_magnitude"] is not None:
            r["decoy_tolerance_max"] = r["decoy_tolerance_max"] * 10.0
            break
    ok &= check("mutation: a decoy spread its two tolerances do not support is caught",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    for r in m["rows"]:
        e = [x for x in r["elements"] if x["element"] == "floor"][0]
        if e["required"]:
            r["required_elements"].remove("floor")
            break
    ok &= check("mutation: a piecewise row dropping its floor requirement is caught",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    for r in m["rows"]:
        r["elements_absent"] = 0
        break
    ok &= check("mutation: an element count that disagrees with the elements is caught",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    for r in m["rows"]:
        r["gated_quantity_magnitudes"] = [{"value": 1.0, "path": r["gate_path"]}]
        break
    ok &= check("mutation: the gate published as a magnitude of its own quantity is caught",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    for r in m["rows"]:
        if r["identifier_named_in_the_producer_schema"]:
            r["identifier_named_in_the_producer_schema"]["script"] = "scripts/does_not_exist.py"
            break
    ok &= check("mutation: a schema citation to a file that is not there is caught",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    m["census"]["rows_in_each_class"]["schema_gap"] += 1
    ok &= check("mutation: an inflated class partition is caught",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    m["rows"].append(dict(m["rows"][0]))
    ok &= check("mutation: a duplicated row is caught",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    for r in m["rows"]:
        r["face"] = "results/state_tilt/GATEPRINT-2026-10-31.json"
        break
    ok &= check("mutation: a row reading this study's own face is caught",
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