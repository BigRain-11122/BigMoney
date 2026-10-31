"""E318 -- E317's zero-tolerance headline, re-counted under the count-word guard.

E317 (r1336) published: 289 faces / **1108 gate leaves**, of which the unit is missing on 1047,
and **122 published gates are exactly zero** ("a tolerance of zero is not a tolerance and
cannot be met by any numeric comparison").  E317 pruned ``frac`` for exactly the right reason --
a name is not a measurement (E207/E208 family) -- and then took the remaining tolerance-named
leaves at face value.

It should not have.  ``n_tolerance_named_not_gate`` is a *count* of gates that named a
tolerance without being one; it carries the token ``tolerance`` and therefore entered E317's
census as a gate whose tolerance is 0.0.  The same shape supplies ``pairs_no_leg_tolerance``,
``faces_with_no_tolerance_name_at_all``, ``comparisons_not_graded_tolerance_from_face`` and
``numeric_values``.  This study measures how much of E317's published arithmetic those leaves
carry, and then asks the question E317's sentence assumed an answer to: of the gates that
really do publish a zero tolerance, what is the zero *doing*?

Three legs, one face:

1. **The control.** Re-count E317's five headline numbers from its own published rows with the
   guard disabled.  If they do not reproduce, this study is measuring something else.
2. **The prune.** Apply a count-word guard frozen before any number is read, publish every
   pruned row with the word that pruned it (a guard that silently drops a real quote is worse
   than the defect -- E208), and re-count every affected census field.
3. **The residual.** For the gates that really publish 0.0, read the block each one gates and
   classify it by the shape of that block: only integers (exact equality on counts is a
   legitimate test), any floats (exact float equality), or no numeric siblings at all (a
   tolerance gating nothing measurable).  A zero tolerance is only a real gate where something
   numeric actually sits beside it.

usage:
  python scripts/e318_count_named_gate_leaves.py run
  python scripts/e318_count_named_gate_leaves.py verify
  python scripts/e318_count_named_gate_leaves.py selftest
"""

import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
INPUT = "PRINTCOV-2026-10-31.json"
FACE = "ZEROTOLPRUNE-%s.json"
LATEST = "zerotolprune_latest.json"
TODAY = "2026-10-31"
STUDY = "E318_count_named_gate_leaves"

# ---- the guard, frozen before any number is read -------------------------------
# A count word is a word about how many things there are, never a value of the thing
# measured (E207: 37,817 measurement-named cells could not be quotes; E208: prune by
# shape, and publish what you pruned).
COUNT_SUFFIX = re.compile(r"_(count|n)$")
ABSENCE_TOKENS = ("no", "not")
COUNT_NOUNS = ("count", "counts", "number", "numbers")
COUNT_EXACT = ("numeric_values",)


def count_word(leaf):
    """Return the token that marks this leaf as a count, or None.

    Token-level, never substring (E208/r1281 lesson, learned the hard way in this very
    guard: a substring rule for ``n_`` also matches ``written_law_tol``, which is a real
    1e-8 acceptance tolerance on results/sina_mf_accept.json -- pruning a real quote is
    worse than the over-count it would fix).
    """
    last = str(leaf).split(".")[-1]
    stripped = re.sub(r"\[\d+\]", "", last)
    toks = [t for t in re.split(r"[^A-Za-z0-9]+", stripped) if t]
    if stripped in COUNT_EXACT:
        return stripped
    if len(toks) > 1 and toks[0] == "n":
        return "n_<count>"
    if COUNT_SUFFIX.search(stripped):
        return "_count"
    for a in ABSENCE_TOKENS:
        if a in toks:
            return a
    for t in toks:
        if t in COUNT_NOUNS:
            return t
    return None


# ---- block walking ------------------------------------------------------------
BLOCK_IDX = re.compile(r"^(.*?)\[(\d+)\]$")


def resolve_block(doc, block):
    """Resolve E317's block label ('rows[3]', 'gates.GA', '<face root>') to a node."""
    if block in ("<face root>", "", None):
        return doc
    cur = doc
    for part in str(block).split("."):
        m = BLOCK_IDX.match(part)
        if m:
            key, idx = m.group(1), int(m.group(2))
            if key:
                if not isinstance(cur, dict) or key not in cur:
                    return None
                cur = cur[key]
            if not isinstance(cur, list) or idx >= len(cur):
                return None
            cur = cur[idx]
        else:
            if not isinstance(cur, dict) or part not in cur:
                return None
            cur = cur[part]
    return cur


def numeric_children(node, depth=0, max_depth=2):
    """Numeric leaves under a block, split by python type (int vs float)."""
    ints, floats = [], []
    if depth > max_depth:
        return ints, floats
    stack = [node]
    while stack:
        cur = stack.pop()
        if isinstance(cur, dict):
            for v in cur.values():
                if isinstance(v, bool):
                    continue
                if isinstance(v, int):
                    ints.append(v)
                elif isinstance(v, float):
                    floats.append(v)
                elif isinstance(v, (dict, list)):
                    stack.append(v)
        elif isinstance(cur, list):
            for v in cur:
                if isinstance(v, bool):
                    continue
                if isinstance(v, int):
                    ints.append(v)
                elif isinstance(v, float):
                    floats.append(v)
                elif isinstance(v, (dict, list)):
                    stack.append(v)
    return ints, floats


def block_shape(node):
    if node is None:
        return "block_unresolved"
    ints, floats = numeric_children(node)
    if not ints and not floats:
        return "no_numeric_sibling"
    if not floats:
        return "integers_only"
    return "floats_present"


# ---- census arithmetic --------------------------------------------------------
def tally(rows):
    """Every headline number this family publishes, from one row list."""
    bands = {}
    for r in rows:
        bands[r.get("value_band")] = bands.get(r.get("value_band"), 0) + 1
    missing = {}
    for r in rows:
        for el in r.get("missing_elements") or []:
            missing[el] = missing.get(el, 0) + 1
    spans = [r for r in rows if isinstance(r.get("decoy"), dict)
             and r["decoy"].get("candidates", 0) >= 2]
    span_vals = [r["decoy"].get("span_orders_of_magnitude") for r in spans]
    span_vals = [s for s in span_vals if isinstance(s, (int, float))]
    complete = [r for r in rows if r.get("reader_complete")]
    return {
        "gate_leaves": len(rows),
        "exactly_zero": bands.get("exactly_zero", 0),
        "value_bands": dict(sorted(bands.items())),
        "reader_complete_leaves": len(complete),
        "reader_complete_share": (len(complete) / float(len(rows))) if rows else 0.0,
        "leaves_missing_each_element": dict(sorted(missing.items())),
        "leaves_readable_only_from_face_level_keys": sum(
            1 for r in rows if r.get("readable_only_from_face_level_keys")),
        "leaves_with_a_substitution_span": len(spans),
        "max_substitution_span_orders_of_magnitude": max(span_vals) if span_vals else 0.0,
        "leaves_spanning_more_than_one_decade": sum(1 for s in span_vals if s > 1.0),
        "leaves_spanning_more_than_ten_decades": sum(1 for s in span_vals if s > 10.0),
    }


def published_control(census):
    """The five numbers E317 published that this study can re-derive from its rows."""
    return {
        "gate_leaves": census.get("gate_leaves"),
        "exactly_zero": census.get("gates_with_a_zero_tolerance"),
        "reader_complete_leaves": census.get("reader_complete_leaves"),
        "leaves_with_a_substitution_span": census.get("leaves_with_a_substitution_span"),
        "max_substitution_span_orders_of_magnitude":
            census.get("max_substitution_span_orders_of_magnitude"),
    }


def control_compare(mine, theirs, tol=1e-4):
    out = {}
    for k, want in theirs.items():
        got = mine.get(k)
        if isinstance(want, float) or isinstance(got, float):
            ok = isinstance(got, (int, float)) and abs(float(got) - float(want)) <= tol
        else:
            ok = got == want
        out[k] = {"published": want, "recounted": got, "ok": bool(ok)}
    return out


# ---- self-contained fixtures (hermetic; no file reads) ------------------------
def _fixture_rows():
    base = {"missing_elements": [], "reader_complete": False,
            "readable_only_from_face_level_keys": False, "decoy": None}
    def row(leaf, value, band):
        r = dict(base)
        r.update({"leaf": leaf, "value": value, "value_band": band, "block": "rows[0]"})
        return r
    rows = [
        row("rows[0].tolerance", 0.0, "exactly_zero"),          # real gate, zero
        row("rows[1].n_tolerance_named_not_gate", 0.0, "exactly_zero"),  # COUNT
        row("rows[2].tolerance", 0.5, "between_1e-2_and_1"),
        row("rows[3].pairs_no_leg_tolerance", 0.0, "exactly_zero"),      # COUNT
        row("meta.equivalence.tol", 1e-9, "below_1e-2"),
        row("rows[4].leg_count", 3.0, "at_least_1"),                     # COUNT
    ]
    rows[4]["decoy"] = {"candidates": 2, "span_orders_of_magnitude": 12.0}
    rows[5]["decoy"] = {"candidates": 3, "span_orders_of_magnitude": 2.5}
    rows[0]["missing_elements"] = ["unit", "scale"]
    rows[1]["missing_elements"] = ["unit"]
    return rows


def selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append({"leg": name, "ok": bool(ok), "detail": detail})

    # L1 the guard catches the exact defect that entered E317
    leg("L1 n_ prefix is a count", count_word("rows[1].n_tolerance_named_not_gate") == "n_<count>")
    # L2 the guard does not eat a real tolerance name (E208: pruning a real quote is worse)
    leg("L2 a real tolerance survives", count_word("rows[0].tolerance") is None,
        str(count_word("rows[0].tolerance")))
    leg("L3 leg_tolerance survives", count_word("rows[3].leg_tolerance") is None)
    # L4 absence nouns are counts, not gates
    leg("L4 absence noun is a count", count_word("pairs_no_leg_tolerance") is not None,
        str(count_word("pairs_no_leg_tolerance")))
    leg("L5 _count suffix", count_word("rows[4].leg_count") == "_count")
    # L6 index brackets must not hide a prefix match
    leg("L6 index does not hide the count word",
        count_word("rows[12].n_checked") == "n_<count>")
    # L6b the substring trap this guard actually fell into: "written_law_tol" contains "n_"
    leg("L6b a real tolerance is not pruned by a substring",
        count_word("law.written_law_tol") is None, str(count_word("law.written_law_tol")))

    rows = _fixture_rows()
    all_t = tally(rows)
    kept = [r for r in rows if count_word(r["leaf"]) is None]
    pruned = [r for r in rows if count_word(r["leaf"]) is not None]
    kept_t = tally(kept)

    # L7 arity identity: pruned rows plus kept rows are the published set, no loss
    leg("L7 arity identity keept+pruned == total",
        kept_t["gate_leaves"] + len(pruned) == all_t["gate_leaves"],
        "%d+%d vs %d" % (kept_t["gate_leaves"], len(pruned), all_t["gate_leaves"]))
    # L8 the zero tally moves by exactly the number of pruned zero rows
    zero_pruned = sum(1 for r in pruned if r["value"] == 0)
    leg("L8 exactly_zero loses exactly its pruned zeros",
        all_t["exactly_zero"] - kept_t["exactly_zero"] == zero_pruned,
        "%d-%d vs %d" % (all_t["exactly_zero"], kept_t["exactly_zero"], zero_pruned))
    # L9 the span tally keeps only rows carrying >= 2 candidates (>= 2 is what makes a spread)
    leg("L9 span tally counts only multi-candidate decoys",
        kept_t["leaves_with_a_substitution_span"] == 1,
        str(kept_t["leaves_with_a_substitution_span"]))
    leg("L10 ten-decade tally follows the frozen 10.0 line",
        kept_t["leaves_spanning_more_than_ten_decades"] == 1,
        str(kept_t["leaves_spanning_more_than_ten_decades"]))

    # block walker
    doc = {"rows": [{"tol": 0.0, "n_checked": 3, "inner": {"x": 1}},
                    {"tol": 0.0, "a": 1.5, "b": 2}],
           "gates": {"GA": {"checked": 4}}}
    leg("L11 dotted block resolves", resolve_block(doc, "gates.GA") == {"checked": 4})
    leg("L12 indexed block resolves", resolve_block(doc, "rows[1]") == {"tol": 0.0, "a": 1.5, "b": 2})
    leg("L13 missing block resolves to None", resolve_block(doc, "rows[9]") is None)
    leg("L14 root label is the document", resolve_block(doc, "<face root>") is doc)
    leg("L15 integers_only shape", block_shape(resolve_block(doc, "gates.GA")) == "integers_only")
    leg("L16 floats_present shape", block_shape(resolve_block(doc, "rows[1]")) == "floats_present")
    leg("L17 unresolved block is named", block_shape(None) == "block_unresolved")
    leg("L18 empty block is named", block_shape({}) == "no_numeric_sibling")
    leg("L19 bool is not a number", block_shape({"flag": True}) == "no_numeric_sibling")

    # the control leg must be able to fail
    cc = control_compare({"a": 1}, {"a": 2})
    leg("L20 control compare detects a mismatch", cc["a"]["ok"] is False)
    cc2 = control_compare({"a": 19.5935}, {"a": 19.5935})
    leg("L21 control compare tolerates a float round-trip", cc2["a"]["ok"] is True)
    # provenance: a study artifact is a census, a face with no E<n>_ study is a measurement
    leg("L22 a study face is named as one",
        face_provenance({"study": "E312_gate_operand_identity"})[0] == "study_face")
    leg("L23 a data face is named as one",
        face_provenance({"batch": "t18", "universe_n": 48})[0] == "data_face")
    leg("L24 an unreadable face is named, not guessed",
        face_provenance(None)[0] == "unreadable")

    failed = [l for l in legs if not l["ok"]]
    print("selftest %d/%d" % (len(legs) - len(failed), len(legs)))
    for l in legs:
        if not l["ok"]:
            print("  FAIL %s  %s" % (l["leg"], l["detail"]))
    return 0 if not failed else 1


# ---- run ----------------------------------------------------------------------
def load_rows():
    path = os.path.join(OUTDIR, INPUT)
    doc = json.load(io.open(path, encoding="utf-8"))
    rows = []
    for f in doc["faces"]:
        for r in f["rows"]:
            rr = dict(r)
            rr["face"] = f["face"]
            rows.append(rr)
    return doc, rows


STUDY_ID = re.compile(r"^E\d+_")


OBSERVED_MAX = re.compile(r"^max.*(diff|delta|err|gap|dev)")


def observed_max(node):
    """A block that publishes the maximum the gate observed makes its own zero testable."""
    if not isinstance(node, dict):
        return None
    for k, v in node.items():
        if OBSERVED_MAX.match(str(k).lower()) and isinstance(v, (int, float)) \
                and not isinstance(v, bool):
            return {"key": k, "value": v}
    return None


def face_provenance(doc):
    """study_face when the file is one of this programme's own study artifacts.

    A study face carries a ``study`` key of the form ``E<n>_<slug>``: it is a census of
    somebody else's numbers, not a measurement panel.  Measuring a census face's own row is
    self-reference -- the defect E317 excluded for its own E313-E317 family and did not apply to
    the family members published before it.
    """
    if not isinstance(doc, dict):
        return "unreadable", None
    study = doc.get("study")
    if isinstance(study, str) and STUDY_ID.match(study):
        return "study_face", study
    return "data_face", study if isinstance(study, str) else None


def classify_residual(rows, cache):
    """Shape the block each surviving zero-tolerance gate gates, and its provenance."""
    out = []
    for r in rows:
        face = r["face"]
        if face not in cache:
            path = os.path.join(ROOT, face)
            try:
                cache[face] = json.load(io.open(path, encoding="utf-8"))
            except Exception:
                cache[face] = None
        doc = cache[face]
        node = (resolve_block(doc, r.get("block")) if doc is not None else None)
        shape = block_shape(node)
        prov, study = face_provenance(doc)
        out.append({"face": face, "leaf": r["leaf"], "block": r.get("block"),
                    "block_shape": shape, "face_provenance": prov, "face_study": study,
                    "observed_max": observed_max(node)})
    tally_ = {}
    for o in out:
        tally_[o["block_shape"]] = tally_.get(o["block_shape"], 0) + 1
    return out, tally_


def build():
    doc, rows = load_rows()
    census = doc["census"]

    all_t = tally(rows)
    control = control_compare(all_t, published_control(census))

    pruned = [r for r in rows if count_word(r["leaf"]) is not None]
    kept = [r for r in rows if count_word(r["leaf"]) is None]
    kept_t = tally(kept)

    zero_all = [r for r in rows if r.get("value") == 0]
    zero_pruned = [r for r in pruned if r.get("value") == 0]
    zero_kept = [r for r in kept if r.get("value") == 0]

    cache = {}
    residual, shape_tally = classify_residual(zero_kept, cache)

    deltas = {}
    for k in all_t:
        if isinstance(all_t[k], (int, float)) and isinstance(kept_t.get(k), (int, float)):
            deltas[k] = {"unpruned": all_t[k], "pruned": kept_t[k],
                         "delta": kept_t[k] - all_t[k]}

    exact = shape_tally.get("integers_only", 0)
    floats = shape_tally.get("floats_present", 0)
    nothing = shape_tally.get("no_numeric_sibling", 0) + shape_tally.get("block_unresolved", 0)
    self_desc = [o for o in residual if o["face_provenance"] == "study_face"]
    other = [o for o in residual if o["face_provenance"] != "study_face"]

    identity = [
        {"check": "the_unpruned_recount_reproduces_e317_published", "ok":
            all(v["ok"] for v in control.values()), "detail": control},
        {"check": "kept_plus_pruned_is_the_published_set", "ok":
            kept_t["gate_leaves"] + len(pruned) == all_t["gate_leaves"],
         "detail": [kept_t["gate_leaves"], len(pruned), all_t["gate_leaves"]]},
        {"check": "every_pruned_leaf_carries_its_count_word", "ok":
            all(count_word(r["leaf"]) for r in pruned)},
        {"check": "the_zero_residual_split_is_whole", "ok":
            len(zero_kept) + len(zero_pruned) == len(zero_all),
         "detail": [len(zero_kept), len(zero_pruned), len(zero_all)]},
        {"check": "the_shapes_account_for_every_residual_gate", "ok":
            sum(shape_tally.values()) == len(residual)},
        {"check": "the_provenance_split_is_whole", "ok":
            len(self_desc) + len(other) == len(residual),
         "detail": [len(self_desc), len(other), len(residual)]},
        {"check": "the_guard_is_idempotent", "ok":
            [r["leaf"] for r in kept] == [r["leaf"] for r in rows
                                          if count_word(r["leaf"]) is None]},
    ]

    exact = shape_tally.get("integers_only", 0)
    floats = shape_tally.get("floats_present", 0)
    nothing = shape_tally.get("no_numeric_sibling", 0) + shape_tally.get("block_unresolved", 0)
    self_desc = [o for o in residual if o["face_provenance"] == "study_face"]
    other = [o for o in residual if o["face_provenance"] != "study_face"]
    verdict = ("%d_of_the_122_zero_tolerance_gates_were_counts_and_%d_of_the_remaining_%d_sit_"
               "on_this_programmes_own_study_faces_leaving_%d_on_a_data_face" % (
                   len(zero_pruned), len(self_desc), len(zero_kept), len(other)))

    face = {
        "schema": "bigmoney/e318-zerotolprune/v1",
        "study": STUDY,
        "title": ("E317's zero-tolerance headline re-counted under the count-word guard, "
                  "and what the surviving zeros gate"),
        "evidence_cutoff": TODAY,
        "generated": TODAY,
        "input_face": "results/state_tilt/" + INPUT,
        "join_rules": {
            "scope": "every row of E317's published census (289 faces / 1108 gate leaves)",
            "count_word": ("the final token of the leaf path starts with n_ , ends with _count, "
                           "or names an absence (no_/not_) or a bare count noun; frozen before "
                           "any number was read"),
            "block_shape": ("the block the tolerance sits in, numeric leaves to depth 2: "
                            "integers_only / floats_present / no_numeric_sibling / "
                            "block_unresolved; bool is not a number"),
            "control_tolerance": ("E317 publishes the substitution span to 4 decimals, so the "
                                  "re-count compares floats at 1e-4 absolute, not 1e-9"),
            "why_the_shape": ("a zero tolerance is an exact-equality test; it is a legitimate "
                              "test on counts and a fragile one on computed floats"),
        },
        "census": {
            "unpruned": all_t,
            "pruned": kept_t,
            "deltas": deltas,
            "count_named_rows": len(pruned),
            "count_named_by_word": _words(pruned),
            "count_named_zero_rows": len(zero_pruned),
            "zero_tolerance_gates_residual": len(zero_kept),
            "zero_tolerance_block_shapes": dict(sorted(shape_tally.items())),
            "zero_tolerance_gates_on_integer_blocks": exact,
            "zero_tolerance_gates_gating_nothing_numeric": nothing,
            "zero_tolerance_gates_that_describe_a_gate": len(self_desc),
            "zero_tolerance_gates_that_are_a_gate": len(other),
            "zero_tolerance_gates_by_provenance": {
                "study_face": len(self_desc), "data_face": len(other)},
            "zero_tolerance_gates_on_data_faces": [
                {"face": o["face"], "leaf": o["leaf"], "block": o["block"],
                 "block_shape": o["block_shape"], "observed_max": o["observed_max"]}
                for o in other],
            "data_face_zero_gates_with_a_published_observed_max":
                sum(1 for o in other if o["observed_max"]),
            "data_face_zero_gates_whose_observed_max_is_zero":
                sum(1 for o in other if o["observed_max"]
                    and o["observed_max"]["value"] == 0),
            "study_faces_carrying_a_residual_zero": sorted(
                set(o["face_study"] or o["face"] for o in self_desc)),
            "faces_with_a_residual_zero_tolerance_gate":
                len(set(o["face"] for o in residual)),
        },
        "control": control,
        "verdict": verdict,
        "residual_gates": residual,
        "count_named": [{"face": r["face"], "leaf": r["leaf"],
                         "value": r.get("value"), "count_word": count_word(r["leaf"])}
                        for r in pruned],
        "identity_checks": identity,
        "notes": [
            "%d of E317's %d gate leaves are counts of gates, not gates; %d of the %d "
            "'exactly zero' rows are those counts, so the headline over-states the zero-tolerance "
            "population by %d (%.1f%%)." % (
                len(pruned), all_t["gate_leaves"], len(zero_pruned), len(zero_all),
                len(zero_pruned), 100.0 * len(zero_pruned) / len(zero_all)),
            "the pruned share of the whole census is small (%d of %d) but it is concentrated "
            "exactly where the headline was: it is the zero band that moves, not the middle." %
            (len(pruned), all_t["gate_leaves"]),
            "the residual split is the part E317 asserted and did not measure: a zero tolerance "
            "on an integers-only block is an exact-equality test on counts (%d), on a block "
            "carrying floats it is an exact float equality (%d)." % (exact, floats),
            "%d residual gates sit in a block with nothing numeric beside them (or a block the "
            "label no longer resolves): there the zero gates nothing measurable." % nothing,
            "and the survivors are almost all self-referential: %d of the %d sit on this programme's "
            "own study faces (a file whose top-level `study` is E<n>_<slug>), i.e. they are "
            "census faces recording somebody else's exact-equality gate. E317 excluded its own "
            "E313-E317 studies and let the earlier members published by the same method through "
            "(E299 precision census, E305 precision gap, E308 leg tolerance, E312 gate operands), "
            "which is why the headline looked like a population of live gates: %d gate(s) on a "
            "non-study face actually publishes a zero tolerance." % (
                len(self_desc), len(zero_kept), len(other)),
            "one of the %d surviving zeros sits on a block a reader can check: it publishes its own "
            "observed maximum beside the zero (%s). A zero tolerance on a computed float is "
            "legitimate exactly where the compared number is a copy rather than a computation, "
            "and nothing else in the surviving population can say which one it is." % (
                len(zero_kept),
                ", ".join("%s=%s" % (o["observed_max"]["key"], o["observed_max"]["value"])
                          for o in other if o["observed_max"]) or "none published"),
            "this study does not re-scan the 289 faces: it re-reads E317's published rows and "
            "opens a face only to shape the block of a surviving zero. E317's own selection "
            "stays the population under test, warts included -- that is the point.",
        ],
    }
    return face


def _words(rows):
    out = {}
    for r in rows:
        w = count_word(r["leaf"]) or "?"
        out[w] = out.get(w, 0) + 1
    return dict(sorted(out.items()))


def write(face):
    os.makedirs(OUTDIR, exist_ok=True)
    p = os.path.join(OUTDIR, FACE % TODAY)
    with io.open(p, "w", encoding="utf-8", newline="") as fh:
        fh.write(json.dumps(face, ensure_ascii=False, indent=1) + "\n")
    lp = os.path.join(OUTDIR, LATEST)
    with io.open(lp, "w", encoding="utf-8", newline="") as fh:
        fh.write(json.dumps(face, ensure_ascii=False, indent=1) + "\n")
    return p


def run():
    face = build()
    p = write(face)
    c = face["census"]
    print("wrote %s" % os.path.relpath(p, ROOT))
    print("verdict: %s" % face["verdict"])
    for k, v in c["deltas"].items():
        print("  %-46s %8s -> %-8s %+d" % (k, v["unpruned"], v["pruned"], v["delta"]))
    print("  residual zero-tolerance gates: %d  shapes %s"
          % (c["zero_tolerance_gates_residual"], c["zero_tolerance_block_shapes"]))
    bad = [i for i in face["identity_checks"] if not i["ok"]]
    if bad:
        print("IDENTITY FAILED: %s" % [b["check"] for b in bad])
        return 1
    return 0


def verify():
    face = build()
    problems = []
    p = os.path.join(OUTDIR, FACE % TODAY)
    if not os.path.exists(p):
        print("missing face %s" % p)
        return 2
    disk = json.load(io.open(p, encoding="utf-8"))
    for k in ("verdict", "census", "control", "identity_checks"):
        if disk.get(k) != face.get(k):
            problems.append("published %s does not re-derive" % k)
    for i in face["identity_checks"]:
        if not i["ok"]:
            problems.append("identity: %s" % i["check"])
    if problems:
        for p_ in problems:
            print("PROBLEM %s" % p_)
        return 1
    print("verify: 0 problems over %d checks" % len(face["identity_checks"]))
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "selftest":
        sys.exit(selftest())
    if cmd == "verify":
        sys.exit(verify())
    if cmd == "run":
        sys.exit(run())
    print(__doc__)
    sys.exit(2)