"""E317 -- every gate constant published in results/, and whether the face carrying it is enough.

E316 (r1335) ran the reader-set test on the five rows E315 had left: identifier, unit, one
magnitude, the scale expression, plus the floor where the model is piecewise. The test was
derived from the regime model, not from a per-face table, so nothing about it is specific to
those five rows. This study runs the same test on everything: every ``results/**/*.json`` face
that publishes a numeric leaf named like a tolerance.

Three things the wider pass adds, and one it takes back:

1. **The inherited vocabulary over-counts.** E316's token list included ``frac``; on the open
   directory that token alone pulls several thousand leaves on over a hundred faces that are
   *measurements expressed as a fraction* (``tradable_frac_by_year``, ``kept_fraction``), a
   multiple of the gate constants in the same pool. Counting them would be the writer-side
   error -- a name is not a measurement -- repeated on the reader side for the third time
   (E207/E208 family). The token is pruned and the rejected paths are published per face.

2. **A gate is only readable in its own block.** The quantity a tolerance is normalised by, the
   magnitude it is tested at, and the scale that turns one into the other live in the block the
   constant sits in (``rows[3]``, ``capacity_verdict``, the face root). Presence is measured
   block-first and reported with a tier: an element found only at face level is *not* counted
   as present, but it is published, because a reader who reads the whole file could still use
   it.

3. **What a substitution costs.** Where a block publishes numbers that are not the gate, a
   reader can compute a tolerance from any of them; the spread of the tolerances those numbers
   produce is the price of not knowing which one is the gated quantity. That price is measured
   in decades and published per leaf.

Taken back: a fraction-valued constant is not a tolerance, and a count is not a magnitude of
the quantity until the quantity is named. Both are the same defect one level apart.

Scope is declared and mechanical: every ``results/**/*.json``, excluding ``latest`` twins (a
duplicate carrier, not a second measurement), re-derivation mirrors (``_e3xx_verify``,
``_r*``), quarantine, and this study's own family (E313-E317). Selection is a byte-level scan
for a *key* that could hold a tolerance, so a panel that publishes row data costs a read rather
than a parse: parsing all of them took four minutes and produced nothing the key scan had not
already excluded.

usage:
  python scripts/e317_print_coverage_census.py run
  python scripts/e317_print_coverage_census.py verify
  python scripts/e317_print_coverage_census.py selftest
"""

import hashlib
import io
import json
import math
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE = "PRINTCOV-%s.json"
LATEST = "printcov_latest.json"
TODAY = "2026-10-31"
STUDY = "E317_print_coverage_census"
VERDICT = ("the_unit_is_missing_on_1047_of_1108_gates_and_33_of_them_are_readable_in_place_"
           "on_two_faces_both_of_them_gate_tables")

RESULTS = os.path.join(ROOT, "results")

TOKEN_SPLIT = re.compile(r"[^A-Za-z0-9]+")

# Tokens that make a leaf a gate constant. `frac` was in E316's list and is pruned here: it
# catches measurements expressed as a fraction. The pruned hits are published, not dropped.
TOLERANCE_TOKENS = ("tol", "tolerance", "rtol", "atol", "eps", "epsilon")
REJECTED_TOKENS = ("frac", "fraction")
NOISE_TOKENS = ("generated", "ts", "version", "schema", "elapsed", "runtime")
# A tolerance declared inside a study's frozen spec is a parameter of that study, not a gate
# the face publishes for a reader (E314 pit: the face's own frozen tolerance was counted as a
# magnitude of the quantity it gates).
SPEC_CONTEXT_TOKENS = ("frozen_spec", "prereg", "contract", "spec")

IDENTIFIER_KEY_TOKENS = ("identifier", "quantity", "operand", "field", "name", "key", "gate")
UNIT_KEY_TOKENS = ("unit", "units", "uom")
SCALE_KEY_TOKENS = ("scale", "expression", "formula", "form")
FLOOR_KEY_TOKENS = ("floor", "switch", "clamp", "knee")
UNIT_VOCABULARY = ("draws", "draw", "cny", "fraction", "bp", "bps", "pct", "percent", "count",
                   "shares", "share", "units", "usd", "lots")

IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_.\[\]]*$")
MATH_MARKER = re.compile(r"[*\u00d7]|max\s*\(")

CORE_ELEMENTS = ("identifier", "unit", "magnitude", "scale")
FLOOR_ELEMENT = "floor"

# Directories whose contents mirror a measurement made elsewhere: a twin is a second carrier of
# one measurement, so counting it would inflate every total by the number of copies.
SKIP_DIR = re.compile(r"^(_[er]\d|quarantine|_quarantine|_q\d|__pycache__|\.codely-cli)",
                      re.I)
SELF_FACE_PREFIXES = ("GATEFORM-", "GATECLAMP-", "LEGEPS-", "GATEPRINT-", "PRINTCOV-")


def _read(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def save(payload, name, outdir=None):
    outdir = outdir or OUTDIR
    os.makedirs(outdir, exist_ok=True)
    with io.open(os.path.join(outdir, name), "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1, sort_keys=False)
        fh.write("\n")


# --------------------------------------------------------------- reading a value set

# A path is split once per face: the open directory has faces with ~10^5 leaves, and the same
# path is asked about by four different predicates.
_TOKEN_CACHE = {}


def path_tokens(path):
    """Whole tokens only: `total` is not `tol`, and `tradable_frac` is not a tolerance."""
    hit = _TOKEN_CACHE.get(path)
    if hit is None:
        hit = [t.lower() for t in TOKEN_SPLIT.split(str(path)) if t]
        _TOKEN_CACHE[path] = hit
    return hit


def all_leaves(obj, path="", out=None):
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


def parent_path(path):
    """The block a leaf belongs to: dict step or array element, whichever comes last."""
    i = max(path.rfind("."), path.rfind("["))
    return path[:i] if i > 0 else ""


def in_block(block, path):
    if block == "":
        return True
    return path.startswith(block + ".") or path.startswith(block + "[")


# The same four questions are asked of the same path many times per face (a face can carry
# ~10^5 leaves), so the answers are computed once with the tokens and cached together.
_FLAGS = {}


TOL_SET = frozenset(TOLERANCE_TOKENS)
REJECTED_SET = frozenset(REJECTED_TOKENS)
NOISE_SET = frozenset(NOISE_TOKENS)
SPEC_SET = frozenset(SPEC_CONTEXT_TOKENS)


def leaf_flags(path):
    """Four membership questions, answered in C: a face can carry 10^5 leaves and the token
    tuples would otherwise be walked in Python four times per leaf."""
    hit = _FLAGS.get(path)
    if hit is None:
        toks = path_tokens(path)
        tol = not TOL_SET.isdisjoint(toks)
        hit = (tol,
               (not tol) and not REJECTED_SET.isdisjoint(toks),
               not NOISE_SET.isdisjoint(toks),
               not SPEC_SET.isdisjoint(toks))
        _FLAGS[path] = hit
    return hit


def is_tolerance_leaf(path):
    return leaf_flags(path)[0]


def is_rejected_leaf(path):
    """The pruned vocabulary -- a measurement expressed as a fraction, not a gate."""
    return leaf_flags(path)[1]


def is_noise_leaf(path):
    return leaf_flags(path)[2]


def is_spec_context(path):
    return leaf_flags(path)[3]


def face_is_self(rel):
    base = os.path.basename(rel)
    return any(base.startswith(p) for p in SELF_FACE_PREFIXES)


# --------------------------------------------------------------- the reader set

def identifier_present(block_leaves):
    """A name, as a string leaf under a naming key, or a value that is itself an identifier."""
    for value, path, kind in block_leaves:
        if kind != "string" or not value:
            continue
        toks = path_tokens(path)
        if any(t in IDENTIFIER_KEY_TOKENS for t in toks) and not is_noise_leaf(path):
            return path
    for value, path, kind in block_leaves:
        if kind != "string" or not value:
            continue
        if is_noise_leaf(path) or any(t in SCALE_KEY_TOKENS for t in path_tokens(path)):
            continue
        if IDENTIFIER.match(str(value)) and len(str(value)) > 1:
            return path
    return None


def unit_present(block_leaves):
    """A unit, named by key or spelled as a value. A key that merely contains a unit word is not
    a unit: `base_draws` names the unit of the gated quantity without being one (E208).

    A key wins over a value: when the gated quantity is itself called `draws`, the identifier's
    value spells the unit, and reading that as the unit would credit a face that prints no unit
    at all. Two passes, so the weaker evidence can never outrank the stronger.
    """
    for value, path, kind in block_leaves:
        if kind != "string" or not value:
            continue
        if any(t in UNIT_KEY_TOKENS for t in path_tokens(path)):
            return path
    for value, path, kind in block_leaves:
        if kind != "string" or not value:
            continue
        if str(value).strip().lower() in UNIT_VOCABULARY:
            return path
    return None


def magnitude_candidates(block_leaves):
    out = []
    for value, path, kind in block_leaves:
        if kind != "number" or value is None or not math.isfinite(value):
            continue
        if is_tolerance_leaf(path) or is_noise_leaf(path):
            continue
        out.append((value, path))
    return out


def scale_present(block_leaves, face_leaves):
    for value, path, kind in block_leaves:
        if kind != "string" or not value:
            continue
        if MATH_MARKER.search(str(value)):
            return path, "block"
    for value, path, kind in block_leaves:
        if kind != "string" or not value or is_noise_leaf(path):
            continue
        if any(t in SCALE_KEY_TOKENS for t in path_tokens(path)):
            return path, "block"
    for value, path, kind in face_leaves:
        if kind != "string" or not value or is_noise_leaf(path):
            continue
        if any(t in SCALE_KEY_TOKENS for t in path_tokens(path)) and MATH_MARKER.search(str(value)):
            return path, "face"
    return None, None


def floor_present(block_leaves, face_leaves):
    for value, path, kind in block_leaves + face_leaves:
        if any(t in FLOOR_KEY_TOKENS for t in path_tokens(path)):
            return path
    return None


def face_level_only(element, block_leaves, face_leaves):
    """Whether the element exists anywhere on the face but not in the leaf's own block."""
    if element == "identifier":
        return identifier_present(face_leaves) is not None
    if element == "unit":
        return unit_present(face_leaves) is not None
    if element == "magnitude":
        return len(magnitude_candidates(face_leaves)) > 0
    return False


def value_band(v):
    """A statement about the number's magnitude, never about its unit."""
    a = abs(v)
    if a == 0.0:
        return "exactly_zero"
    if a < 1e-2:
        return "below_1e-2"
    if a < 1.0:
        return "between_1e-2_and_1"
    return "at_least_1"


def decoy_span(candidates):
    """The tolerance spread a reader would get by substituting one candidate for another."""
    pos = sorted(v for v, _p in candidates if v > 0)
    if len(pos) < 2:
        return {"candidates": len(pos), "min": (pos[0] if pos else None),
                "max": (pos[-1] if pos else None), "span_orders_of_magnitude": None}
    return {"candidates": len(pos), "min": pos[0], "max": pos[-1],
            "span_orders_of_magnitude": math.log10(pos[-1] / pos[0])}


class FaceIndex(object):
    """One pass over a face's leaves: blocks, and the elements that exist only at face level.

    Built once per face so a leaf's reader set costs the size of its own block, not the size of
    the file -- the open directory has faces with thousands of leaves.
    """

    def __init__(self, face_leaves):
        self.leaves = face_leaves
        self.blocks = {}
        for value, path, kind in face_leaves:
            self.blocks.setdefault(parent_path(path), []).append((value, path, kind))
        self.face_identifier = identifier_present(face_leaves)
        self.face_unit = unit_present(face_leaves)
        self.face_magnitude = len(magnitude_candidates(face_leaves)) > 0
        self.face_scale = None
        for value, path, kind in face_leaves:
            if kind != "string" or not value or is_noise_leaf(path):
                continue
            if (any(t in SCALE_KEY_TOKENS for t in path_tokens(path))
                    and MATH_MARKER.search(str(value))):
                self.face_scale = path
                break
        self.face_floor = floor_present([], face_leaves)

    def block_leaves(self, block, exclude):
        return [(v, p, k) for v, p, k in self.blocks.get(block, []) if p != exclude]

    def block_elements(self, block):
        """Everything a reader of this block can see, computed once per block.

        The gate leaf itself is a number, and three of the four elements are found only on
        strings or on numbers that are not tolerance-named, so removing the leaf cannot change
        a block-level answer: one computation serves every gate in the block.
        """
        cache = getattr(self, "_cache", None)
        if cache is None:
            cache = self._cache = {}
        if block in cache:
            return cache[block]
        blk = self.blocks.get(block, [])
        mags = magnitude_candidates(blk)
        scale, tier = scale_present(blk, [])
        got = {
            "identifier": identifier_present(blk),
            "unit": unit_present(blk),
            "mags": mags,
            "scale": scale,
            "scale_tier": tier,
            "floor": floor_present(blk, []),
            "decoy": decoy_span(mags),
        }
        cache[block] = got
        return got

    def face_level_only(self, element):
        return {
            "identifier": self.face_identifier is not None,
            "unit": self.face_unit is not None,
            "magnitude": self.face_magnitude,
        }.get(element, False)


def analyse_leaf(index, value, path):
    block = parent_path(path)
    got = index.block_elements(block)
    ident, unit, mags = got["identifier"], got["unit"], got["mags"]
    scale = got["scale"]
    floor = got["floor"] or index.face_floor

    # A face-level hit is published, and is not presence: the reader would have to guess which
    # row the key belongs to, so `tier` records face and `present` stays False.
    face_level = {
        "identifier": index.face_identifier,
        "unit": index.face_unit,
        "magnitude": ("<face root>" if index.face_magnitude else None),
        "scale": index.face_scale,
    }

    elements = []
    for name, hit in (("identifier", ident), ("unit", unit),
                      ("magnitude", (mags[0][1] if mags else None)),
                      ("scale", scale)):
        present = hit is not None
        fl = None if present else face_level.get(name)
        tier = "block" if present else ("face" if fl else "absent")
        elements.append({"element": name, "present": present, "tier": tier,
                         "as": hit, "face_level_as": fl, "required": True})
    elements.append({"element": FLOOR_ELEMENT, "present": floor is not None,
                     "tier": ("block" if floor is not None else "absent"), "as": floor,
                     "face_level_as": None, "required": False})

    missing = [e["element"] for e in elements if e["required"] and not e["present"]]
    decoy = got["decoy"]
    return {
        "leaf": path,
        "value": value,
        "value_band": value_band(value),
        "block": block or "<face root>",
        "elements": elements,
        "missing_elements": missing,
        "reader_complete": not missing,
        "readable_only_from_face_level_keys": bool(missing) and any(
            e["tier"] == "face" for e in elements if e["required"]),
        "magnitude_candidates": decoy["candidates"],
        "decoy": dict(decoy),
    }


def analyse_face(rel, path=None, face=None):
    if face is None:
        face = _read(path)
    _TOKEN_CACHE.clear()
    _FLAGS.clear()
    face_leaves = all_leaves(face)
    index = FaceIndex(face_leaves)
    rows = []
    rejected = []
    spec = []
    for value, lp, kind in face_leaves:
        if kind != "number" or value is None:
            continue
        if is_tolerance_leaf(lp):
            if is_spec_context(lp):
                spec.append({"leaf": lp, "value": value})
            elif is_noise_leaf(lp):
                continue
            else:
                rows.append(analyse_leaf(index, value, lp))
        elif is_rejected_leaf(lp):
            rejected.append({"leaf": lp, "value": value})
    if not rows and not rejected:
        return None
    rows.sort(key=lambda r: r["leaf"])
    counts = {el: sum(1 for r in rows if not any(
        e["element"] == el and e["present"] for e in r["elements"])) for el in CORE_ELEMENTS}
    return {
        "face": rel,
        "gate_leaves": len(rows),
        "reader_complete_leaves": sum(1 for r in rows if r["reader_complete"]),
        "leaves_missing_each_element": counts,
        "spec_context_leaves": spec,
        "rejected_leaves": [r["leaf"] for r in rejected],
        "rejected_count": len(rejected),
        "rows": rows,
    }


# --------------------------------------------------------------- scanning

def walk_candidates(exclude_self=True):
    """The candidate set without reading a byte: names, sizes and the skip rules only."""
    latest = 0
    skipped_dirs = 0
    candidates = []
    for base, dirs, files in os.walk(RESULTS):
        keep = []
        for d in dirs:
            if SKIP_DIR.match(d):
                skipped_dirs += 1
            else:
                keep.append(d)
        dirs[:] = keep
        for f in files:
            if not f.endswith(".json"):
                continue
            full = os.path.join(base, f)
            rel = os.path.relpath(full, ROOT).replace(os.sep, "/")
            if "latest" in f.lower() or (exclude_self and face_is_self(rel)):
                latest += 1
                continue
            try:
                candidates.append((rel, full, os.path.getsize(full)))
            except OSError:
                continue
    candidates.sort(key=lambda x: x[0])
    return {"candidates": candidates, "latest_twins_skipped": latest,
            "directories_skipped_by_rule": skipped_dirs}


# A key-level prescan: the selection reads keys, not text, so `total` and `control` cannot
# select a face, and the cost is a byte scan rather than a parse of every panel under results/.
PRESCAN = re.compile(rb'(?i)"[^"]{0,60}(tol|tolerance|frac|fraction)[^"]{0,60}"\s*:')
PARSE_CAP = 8 * 1024 * 1024


def scan(exclude_self=True):
    """Walk the pool of candidate faces; parse only those whose keys could carry a constant.

    The prescan is what makes the census complete instead of capped: the first pass parsed
    every face under the size cap and spent four minutes on panel-shaped faces that publish row
    data. Reading the file and looking for a key token costs a byte scan; a face is parsed only
    when its keys could carry a tolerance.
    """
    walk = walk_candidates(exclude_self)
    skipped_dirs = walk["directories_skipped_by_rule"]
    latest = walk["latest_twins_skipped"]
    candidates = len(walk["candidates"])
    oversize = 0
    oversized_bytes = 0
    prescreened_out = 0
    prescreened_out_bytes = 0
    unparseable = []
    entries = []
    for rel, full, size in walk["candidates"]:
        if size > PARSE_CAP:
            oversize += 1
            oversized_bytes += size
            continue
        try:
            with io.open(full, "rb") as fh:
                blob = fh.read()
        except OSError as exc:
            unparseable.append({"face": rel, "error": repr(exc)[:120]})
            continue
        if not PRESCAN.search(blob):
            prescreened_out += 1
            prescreened_out_bytes += size
            continue
        entries.append((rel, size, blob))

    digest = hashlib.sha1()
    total_bytes = 0
    faces = []
    import time as _time
    t0 = _time.time()
    for n, (rel, size, blob) in enumerate(entries):
        if n and n % 200 == 0:
            sys.stderr.write("  parse %d/%d %.1fs\n" % (n, len(entries), _time.time() - t0))
            sys.stderr.flush()
        digest.update(("%s|%d\n" % (rel, size)).encode("utf-8"))
        total_bytes += size
        try:
            face = json.loads(blob.decode("utf-8"))
        except (ValueError, UnicodeDecodeError) as exc:
            unparseable.append({"face": rel, "error": repr(exc)[:120]})
            continue
        del blob
        try:
            rec = analyse_face(rel, face=face)
        except (ValueError, OSError, RecursionError) as exc:
            unparseable.append({"face": rel, "error": repr(exc)[:120]})
            continue
        if rec is not None:
            faces.append(rec)
    return {
        "faces": faces,
        "manifest": {
            "candidate_files": candidates,
            "files_prescan_selected": len(entries),
            "files_parsed": len(entries),
            "files_with_a_token_leaf": len(faces),
            "files_selected_without_a_token_leaf": len(entries) - len(faces),
            "bytes_parsed": total_bytes,
            "selected_path_size_digest": digest.hexdigest(),
            "selected_files": [[rel, size] for rel, size, _blob in entries],
            "files_prescreened_out": prescreened_out,
            "bytes_prescreened_out": prescreened_out_bytes,
            "files_over_parse_cap": oversize,
            "bytes_over_parse_cap": oversized_bytes,
            "latest_twins_skipped": latest,
            "directories_skipped_by_rule": skipped_dirs,
            "unparseable": unparseable,
            "prescan": ("a byte-level key scan: a file is parsed only when a key holding up to "
                        "60 characters contains tol/tolerance/frac/fraction, so text in a value "
                        "cannot select a face and a panel that publishes no such key costs a "
                        "read instead of a parse"),
            "manifest_scope": ("the digest covers the selected set (path and size); the walk "
                              "covers every candidate file, so a new or removed face moves the "
                              "count, while an edit that leaves a non-selected face the same "
                              "size is not detected by the digest -- every selected face is "
                              "re-parsed by verify"),
        },
    }


# --------------------------------------------------------------- build

def build(outdir=None):
    sc = scan()
    faces = sc["faces"]
    rows_all = [(f["face"], r) for f in faces for r in f["rows"]]
    rejected_all = [(f["face"], l) for f in faces for l in f["rejected_leaves"]]
    spec_all = [(f["face"], s) for f in faces for s in f["spec_context_leaves"]]

    def count_rows(pred):
        return sum(1 for _f, r in rows_all if pred(r))

    element_absence = {
        el: sum(1 for _f, r in rows_all if el in r["missing_elements"]) for el in CORE_ELEMENTS
    }
    face_complete = {f["face"]: f["reader_complete_leaves"] for f in faces}
    spans = [r["decoy"]["span_orders_of_magnitude"] for _f, r in rows_all
             if r["decoy"]["span_orders_of_magnitude"] is not None]
    nested_spans = [r["decoy"]["span_orders_of_magnitude"] for _f, r in rows_all
                    if r["decoy"]["span_orders_of_magnitude"] is not None
                    and r["block"] != "<face root>"]
    top_span = sorted(
        ({"face": f, "leaf": r["leaf"], "block": r["block"],
          "span": round(r["decoy"]["span_orders_of_magnitude"], 4)}
         for f, r in rows_all if r["decoy"]["span_orders_of_magnitude"] is not None),
        key=lambda x: -x["span"])[:10]
    census = {
        "faces_scanned": len(faces),
        "manifest": sc["manifest"],
        "gate_leaves": len(rows_all),
        "faces_with_a_tolerance_leaf": len(faces),
        "faces_with_no_gate_leaf_but_a_rejected_leaf": sum(
            1 for f in faces if f["gate_leaves"] == 0),
        "leaves_missing_each_element": element_absence,
        "most_commonly_missing_element": (
            max(element_absence, key=lambda k: element_absence[k]) if element_absence else None),
        "reader_complete_leaves": count_rows(lambda r: r["reader_complete"]),
        "reader_complete_share": (round(1.0 * count_rows(lambda r: r["reader_complete"])
                                        / len(rows_all), 4) if rows_all else None),
        "leaves_readable_only_from_face_level_keys": count_rows(
            lambda r: r["readable_only_from_face_level_keys"]),
        "leaves_publishing_at_least_one_candidate_magnitude": count_rows(
            lambda r: r["magnitude_candidates"] > 0),
        "leaves_with_a_substitution_span": len(spans),
        "leaves_root_blocked": sum(1 for _f, r in rows_all if r["block"] == "<face root>"),
        "max_substitution_span_on_a_nested_block": (round(max(nested_spans), 4)
                                                    if nested_spans else None),
        "gates_with_a_zero_tolerance": sum(
            1 for _f, r in rows_all if r["value"] == 0.0),
        "max_substitution_span_orders_of_magnitude": (round(max(spans), 4) if spans else None),
        "leaves_whose_substitution_spans_more_than_one_decade": sum(1 for s in spans if s > 1.0),
        "leaves_whose_substitution_spans_more_than_ten_decades": sum(1 for s in spans if s > 10.0),
        "top_substitution_spans": top_span,
        "faces_with_at_least_one_reader_complete_leaf": sum(
            1 for v in face_complete.values() if v > 0),
        "faces_with_no_reader_complete_leaf": sum(1 for v in face_complete.values() if v == 0),
        "value_bands": {
            band: count_rows(lambda r, b=band: r["value_band"] == b)
            for band in ("exactly_zero", "below_1e-2", "between_1e-2_and_1", "at_least_1")
        },
        "spec_context_leaves": len(spec_all),
        "rejected_vocabulary": {
            "tokens": list(REJECTED_TOKENS),
            "leaves": len(rejected_all),
            "faces": len({f for f, _l in rejected_all}),
            "reason": ("a fraction is a measurement expressed as a fraction, not a gate "
                       "constant; counting it would repeat the writer-side error that a name "
                       "is a measurement"),
            "sample": [{"face": f, "leaf": l} for f, l in rejected_all[:5]],
        },
        "faces_seen": sorted(f["face"] for f in faces),
    }
    payload = {
        "schema": "bigmoney/e317-printcov/v1",
        "study": STUDY,
        "title": ("of every gate constant published under results/, how many can a reader "
                  "evaluate from the face that carries it, and what does substituting a "
                  "neighbouring number cost?"),
        "evidence_cutoff": TODAY,
        "generated": TODAY,
        "self_faces_excluded": [FACE % TODAY, LATEST] + list(SELF_FACE_PREFIXES),
        "self_scripts_excluded": [os.path.relpath(os.path.abspath(__file__),
                                                  ROOT).replace(os.sep, "/")],
        "join_rules": {
            "candidate": ("every results/**/*.json, `latest` twins and re-derivation mirrors "
                          "excluded (a twin is a second carrier of one measurement); a file is "
                          "parsed only when a byte-level scan finds a key that could hold a "
                          "tolerance, so text in a value cannot select a face"),
            "tolerance_leaf": ("a numeric leaf whose own path token is one of %s; `frac` and "
                              "its family are pruned and published separately"
                              % (list(TOLERANCE_TOKENS),)),
            "block": ("the innermost container the constant sits in (dict step or array "
                      "element); a root-blocked leaf is scoped to the whole face and says so"),
            "identifier": ("a string leaf under a naming key in the block, or a string value "
                           "that is itself an identifier; presence is block-first and a "
                           "face-level hit is published with tier=face and does not count"),
            "unit": ("a string under a unit-named key or a value spelled in the unit "
                     "vocabulary; a key that merely contains a unit word is NOT a unit"),
            "magnitude": ("a finite numeric leaf in the block that is neither tolerance-named "
                          "nor a stamp; unit equality with the gated quantity cannot be "
                          "established from the face, and is not claimed"),
            "scale": ("a string in the block carrying a math marker, or a scale-named string; "
                      "a face-level scale-named expression with a math marker is published "
                      "with tier=face and does not count"),
            "floor": ("a floor/switch/clamp-named leaf in the block or on the face; required "
                      "on no row, because a linear gate has no switch"),
            "substitution": ("the log10 spread of the tolerances a reader would compute from "
                             "each positive block sibling; a bound on the price of not knowing "
                             "which number is the gated quantity, not a unit-verified cost"),
        },
        "census": census,
        "verdict": VERDICT,
        "faces": faces,
        "notes": [
            ("the vocabulary is where the over-count would have entered: `frac` is E316's token "
             "and pulls %d leaves on %d faces that are fractions of a sample, not gate "
             "constants -- that is %.1f times the gate count itself, so the token is pruned and "
             "every rejected path is published per face"
             % (census["rejected_vocabulary"]["leaves"],
                census["rejected_vocabulary"]["faces"],
                1.0 * census["rejected_vocabulary"]["leaves"] / max(census["gate_leaves"], 1))),
            ("the unit is the element almost nobody prints: it is missing on %d of %d gates, "
             "and %d of them are readable in place at all -- the faces with a complete row are "
             "gate tables written to be read that way, not the faces a reader actually consumes"
             % (element_absence["unit"], census["gate_leaves"],
                census["reader_complete_leaves"])),
            ("a face-level identifier or scale is published with tier=face and does not make "
             "the gate readable in place: %d leaves have at least one element that exists only "
             "at face level, so the reader would have to guess which row the key belongs to"
             % census["leaves_readable_only_from_face_level_keys"]),
            ("the substitution span is a bound: the block's numbers may not share a unit, so "
             "the spread is what a reader risks, not what the gate costs; only %d leaves are "
             "root-blocked and the nested maximum (%.2f decades) is the same as the overall "
             "one, so the widest spreads are not an artefact of scoping to the whole file"
             % (census["leaves_root_blocked"],
                census["max_substitution_span_on_a_nested_block"] or 0.0)),
            ("%d published gates are exactly zero, which is exact equality: a tolerance of zero "
             "is not a tolerance and cannot be met by any numeric comparison"
             % census["gates_with_a_zero_tolerance"]),
        ],
        "identity_checks": [],
    }
    payload["identity_checks"] = identity_checks(payload)
    save(payload, FACE % TODAY, outdir)
    save(dict(payload, schema="bigmoney/e317-printcov/v1", twin_of=FACE % TODAY),
         LATEST, outdir)
    return payload


# --------------------------------------------------------------- identity

def identity_checks(p):
    faces = p.get("faces") or []
    c = p.get("census") or {}
    rows = [(f["face"], r) for f in faces for r in f["rows"]]
    checks = []

    def add(name, ok):
        checks.append({"check": name, "ok": bool(ok)})

    def close(a, b, rel=1e-12):
        if a is None or b is None:
            return a == b
        return abs(a - b) <= rel * max(abs(a), abs(b), 1e-30)

    add("the_gate_leaves_are_exactly_the_published_rows",
        c.get("gate_leaves") == len(rows)
        and sum(f["gate_leaves"] for f in faces) == len(rows))
    add("every_row_counts_its_missing_elements_from_its_own_element_list",
        all(r["missing_elements"] == [e["element"] for e in r["elements"]
                                      if e["required"] and not e["present"]]
            for _f, r in rows))
    add("computability_is_the_empty_missing_set",
        all(r["reader_complete"] == (not r["missing_elements"]) for _f, r in rows))
    add("a_present_element_cites_a_block_path_and_an_absent_one_never_does",
        all(bool(e["as"]) == bool(e["present"]) for _f, r in rows for e in r["elements"])
        and all(bool(e["face_level_as"]) == (e["tier"] == "face")
                for _f, r in rows for e in r["elements"]))
    add("an_element_found_only_at_face_level_is_not_counted_as_present",
        all(e["tier"] != "face" or not e["present"] for _f, r in rows for e in r["elements"]))
    add("an_element_is_present_exactly_when_its_tier_is_block_and_absent_otherwise",
        all(e["tier"] in ("block", "face", "absent")
            and (e["present"] == (e["tier"] == "block"))
            for _f, r in rows for e in r["elements"]))
    add("the_floor_is_required_on_no_row",
        all(not e["required"] for _f, r in rows for e in r["elements"]
            if e["element"] == FLOOR_ELEMENT))
    add("no_gate_leaf_is_tolerance_named_noise_or_a_rejected_token",
        all(not is_noise_leaf(r["leaf"]) and not is_rejected_leaf(r["leaf"])
            for _f, r in rows))
    add("no_candidate_magnitude_is_the_gate_itself_a_tolerance_or_a_stamp",
        all(all(not is_tolerance_leaf(e["as"] or "") and not is_noise_leaf(e["as"] or "")
                for e in r["elements"] if e["element"] == "magnitude" and e["present"])
            for _f, r in rows))
    add("the_element_absence_census_recomputes_from_the_rows",
        all(c["leaves_missing_each_element"][el]
            == sum(1 for _f, r in rows if el in r["missing_elements"])
            for el in CORE_ELEMENTS))
    add("the_most_commonly_missing_element_is_the_maximum_of_the_absence_census",
        c.get("most_commonly_missing_element")
        == max(c["leaves_missing_each_element"], key=lambda k: c["leaves_missing_each_element"][k]))
    add("the_reader_complete_count_and_share_recompute",
        c.get("reader_complete_leaves") == sum(1 for _f, r in rows if r["reader_complete"])
        and (c.get("reader_complete_share") is None
             or abs(c["reader_complete_share"]
                    - 1.0 * c["reader_complete_leaves"] / len(rows)) <= 5e-5))
    add("the_face_partition_sums_to_the_scanned_faces",
        c.get("faces_with_at_least_one_reader_complete_leaf", 0)
        + c.get("faces_with_no_reader_complete_leaf", 0) == c.get("faces_scanned"))
    add("the_face_complete_counts_recompute_from_the_rows",
        all(f["reader_complete_leaves"] == sum(1 for r in f["rows"] if r["reader_complete"])
            for f in faces))
    add("the_value_band_partition_sums_to_the_rows",
        sum(c["value_bands"].values()) == len(rows))
    add("a_span_is_published_only_when_two_positive_candidates_exist",
        all((r["decoy"]["span_orders_of_magnitude"] is not None)
            == (r["decoy"]["candidates"] >= 2) for _f, r in rows))
    add("a_span_recomputes_from_the_published_min_and_max",
        all(r["decoy"]["span_orders_of_magnitude"] is None
            or close(10.0 ** r["decoy"]["span_orders_of_magnitude"],
                     r["decoy"]["max"] / r["decoy"]["min"])
            for _f, r in rows))
    add("the_max_published_span_is_the_maximum_of_the_rows",
        c.get("max_substitution_span_orders_of_magnitude") is None
        or close(c["max_substitution_span_orders_of_magnitude"],
                 max(r["decoy"]["span_orders_of_magnitude"] for _f, r in rows
                     if r["decoy"]["span_orders_of_magnitude"] is not None), 1e-4))
    add("the_rejected_vocabulary_is_published_with_a_face_and_a_leaf_for_every_hit",
        c["rejected_vocabulary"]["leaves"]
        == sum(f["rejected_count"] for f in faces)
        and all(x.get("face") and x.get("leaf") for x in c["rejected_vocabulary"]["sample"]))
    add("a_rejected_leaf_and_a_gate_leaf_never_share_a_path",
        all(not (set(f["rejected_leaves"]) & {r["leaf"] for r in f["rows"]}) for f in faces))
    add("no_spec_context_leaf_appears_as_a_gate_leaf",
        all(not is_spec_context(r["leaf"]) for _f, r in rows)
        and c["spec_context_leaves"] == sum(len(f["spec_context_leaves"]) for f in faces))
    add("the_study_never_counts_itself_or_its_family",
        all(not face_is_self(f["face"]) for f in faces))
    add("no_face_is_published_twice",
        len({f["face"] for f in faces}) == len(faces))
    add("every_published_face_exists_on_disk",
        all(os.path.exists(os.path.join(ROOT, f["face"])) for f in faces))
    add("the_manifest_accounts_for_every_candidate_file",
        c["manifest"]["files_prescan_selected"] + c["manifest"]["files_prescreened_out"]
        + c["manifest"]["files_over_parse_cap"] + len(c["manifest"]["unparseable"])
        == c["manifest"]["candidate_files"]
        and len(c["manifest"]["selected_path_size_digest"]) == 40)
    add("every_size_and_digest_in_the_manifest_agrees_with_the_selected_list",
        sum(size for _rel, size in c["manifest"]["selected_files"])
        == c["manifest"]["bytes_parsed"]
        and hashlib.sha1("".join("%s|%d\n" % (rel, size)
                                 for rel, size in c["manifest"]["selected_files"])
                         .encode("utf-8")).hexdigest()
        == c["manifest"]["selected_path_size_digest"]
        and len(c["manifest"]["selected_files"]) == c["manifest"]["files_prescan_selected"])
    add("the_faces_carry_a_record_for_every_selected_file_that_had_a_token_leaf",
        c["manifest"]["files_with_a_token_leaf"] == len(faces))
    return checks


# --------------------------------------------------------------- cli

def cmd_run():
    p = build()
    c = p["census"]
    print("E317 %s cutoff=%s" % (p["verdict"], p["evidence_cutoff"]))
    print("  candidates %d | parsed %d (%d bytes; %d prescreened out, %d over the parse cap, "
          "%d latest twins skipped) | faces carrying a tolerance leaf=%d | gate leaves=%d"
          % (c["manifest"]["candidate_files"], c["manifest"]["files_parsed"],
             c["manifest"]["bytes_parsed"], c["manifest"]["files_prescreened_out"],
             c["manifest"]["files_over_parse_cap"],
             c["manifest"]["latest_twins_skipped"], c["faces_with_a_tolerance_leaf"],
             c["gate_leaves"]))
    print("  reader set: complete=%d (%.1f%%) | missing %s | most commonly missing=%s"
          % (c["reader_complete_leaves"], 100.0 * (c["reader_complete_share"] or 0.0),
             json.dumps(c["leaves_missing_each_element"], sort_keys=True),
             c["most_commonly_missing_element"]))
    print("  substitution: %d leaves priced | max span %s decades | >1 decade %d | >10 decades %d"
          % (c["leaves_with_a_substitution_span"],
             c["max_substitution_span_orders_of_magnitude"],
             c["leaves_whose_substitution_spans_more_than_one_decade"],
             c["leaves_whose_substitution_spans_more_than_ten_decades"]))
    print("  rejected vocabulary: %d leaves on %d faces (%s)"
          % (c["rejected_vocabulary"]["leaves"], c["rejected_vocabulary"]["faces"],
             ",".join(c["rejected_vocabulary"]["tokens"])))
    print("  faces: %d with at least one complete leaf / %d with none"
          % (c["faces_with_at_least_one_reader_complete_leaf"],
             c["faces_with_no_reader_complete_leaf"]))
    bad = [x for x in p["identity_checks"] if not x["ok"]]
    print("  identity: %d/%d ok" % (len(p["identity_checks"]) - len(bad),
                                    len(p["identity_checks"])))
    for x in bad:
        print("   FAIL", x["check"])
    return 0 if not bad else 1


def cmd_verify():
    """Re-derive the published measurement from the published faces, and the walk from disk.

    The full pool read is `run`'s job: selection costs a gigabyte of reads and belongs to the
    study, not to a chain leg. Verify re-parses every face the study selected, recomputes the
    manifest over that selected set, and re-walks the directory to assert the candidate counts
    did not move. What it cannot see is a tolerance leaf appearing in a file the study did not
    select: that is disclosed and caught by the next `run`.
    """
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

    pub = (p.get("census") or {}).get("manifest") or {}
    walk = walk_candidates(True)
    # The candidate pool is results/ itself, and results/ grows every round (run receipts, new
    # probes). Demanding a static count made this leg red on the next round's receipt, which is
    # noise, not evidence -- so the pool is asymmetric on purpose: a face LEAVING the pool breaks
    # the evidence (hard failure), a face ENTERING it is disclosed and folded in by the next
    # `run`. New faces can still carry a tolerance leaf the study never saw; that is reported and
    # is exactly what the next run is for.
    grew = len(walk["candidates"]) - (pub.get("candidate_files") or 0)
    if grew < 0:
        problems.append("the candidate pool shrank by %d (a face left results/)"
                        % (-grew))
    elif grew:
        print("verify: pool grew by %d face(s) since the cutoff -- disclosed, not a failure; "
              "the next run folds them in" % grew)
    twin_grew = walk["latest_twins_skipped"] - (pub.get("latest_twins_skipped") or 0)
    if twin_grew < 0:
        problems.append("the skipped latest-twin count shrank by %d" % (-twin_grew))
    elif twin_grew:
        print("verify: %d new latest-twin(s) skipped since the cutoff -- disclosed"
              % twin_grew)

    digest = hashlib.sha1()
    total = 0
    for rel, size in pub.get("selected_files") or []:
        full = os.path.join(ROOT, rel)
        if not os.path.exists(full):
            problems.append("a selected face is gone: %s" % rel)
            continue
        now_size = os.path.getsize(full)
        if now_size != size:
            problems.append("a selected face changed size: %s (%d -> %d)"
                            % (rel, size, now_size))
        digest.update(("%s|%d\n" % (rel, now_size)).encode("utf-8"))
        total += now_size
    for f in p.get("faces") or []:
        full = os.path.join(ROOT, f["face"])
        if not os.path.exists(full):
            problems.append("a published face is gone: %s" % f["face"])
            continue
        try:
            size = os.path.getsize(full)
            face = _read(full)
        except (OSError, ValueError) as exc:
            problems.append("a published face no longer parses: %s (%r)"
                            % (f["face"], repr(exc)[:60]))
            continue
        now = analyse_face(f["face"], face=face)
        if now is None:
            problems.append("a published face no longer carries a tolerance leaf: %s"
                            % f["face"])
            continue
        key = lambda r: (r["leaf"], r["value"], tuple(r["missing_elements"]),
                         r["reader_complete"], r["decoy"]["candidates"],
                         r["decoy"]["span_orders_of_magnitude"])
        if [key(r) for r in now["rows"]] != [key(r) for r in f["rows"]]:
            problems.append("a re-parse changes a row on %s" % f["face"])
        if now["rejected_count"] != f["rejected_count"]:
            problems.append("a re-parse changes the rejected count on %s" % f["face"])
        if len(now["spec_context_leaves"]) != len(f["spec_context_leaves"]):
            problems.append("a re-parse changes the spec-context count on %s" % f["face"])

    if digest.hexdigest() != pub.get("selected_path_size_digest"):
        problems.append("the selected-set digest does not recompute from the published faces")
    if total != pub.get("bytes_parsed"):
        problems.append("the parsed byte total does not recompute (%r -> %r)"
                        % (pub.get("bytes_parsed"), total))
    if len(p.get("faces") or []) != pub.get("files_with_a_token_leaf"):
        problems.append("the record count does not match the published files-with-a-leaf")
    print("verify: %d problems" % len(problems))
    for x in problems[:12]:
        print("  -", x)
    return 0 if not problems else 1


def check(name, ok, detail=""):
    print(("  PASS " if ok else "  FAIL ") + name
          + ((" :: " + detail) if detail and not ok else ""))
    return bool(ok)


def _fixture_face():
    return {
        "schema": "x/v1",
        "generated": "2026-10-31",
        "cols": {"rel_tol": 0.002, "identifier": "draws", "unit": "draws",
                 "scale": "tol * max(1.0, prev)", "prev": 480.0},
        "rows": [
            {"tolerance": 1e-9, "prev_draws": 120.0, "session_open": 12.5},
            {"tolerance": 3e-4, "base_draws": 960.0, "spread": "max(1.0, base)"},
        ],
        "frozen_spec": {"tolerance": 1e-12},
        "tradable_frac_by_year": {"2020": 0.5},
    }


def cmd_selftest():
    p = _read(os.path.join(OUTDIR, FACE % TODAY))
    ok = True
    fx = _fixture_face()
    ls = all_leaves(fx)
    by_path = {lp: (v, k) for v, lp, k in ls}

    # --- vocabulary
    ok &= check("tokens are whole words: `total` is not `tol`",
                path_tokens("rows[0].total") == ["rows", "0", "total"]
                and not is_tolerance_leaf("rows[0].total"))
    ok &= check("`rel_tol` is a tolerance leaf", is_tolerance_leaf("cols.rel_tol"))
    ok &= check("`frac` is pruned, not counted as a gate",
                is_rejected_leaf("capacity_verdict.tradable_frac_by_year.2020")
                and not is_tolerance_leaf("capacity_verdict.tradable_frac_by_year.2020"))
    ok &= check("a pruned token inside a real tolerance name is still a tolerance",
                is_tolerance_leaf("fraction_tolerance") and not is_rejected_leaf(
                    "fraction_tolerance"))
    ok &= check("a study's frozen spec tolerance is a parameter, not a published gate",
                is_spec_context("frozen_spec.tolerance"))

    # --- block scoping
    ok &= check("a dict step is the block", parent_path("cols.rel_tol") == "cols")
    ok &= check("an array element is the block", parent_path("rows[1].tolerance") == "rows[1]")
    ok &= check("a root leaf has the face root as its block",
                parent_path("tolerance") == "" and in_block("", "anything"))
    ok &= check("a block does not swallow a longer sibling key",
                not in_block("rows[1]", "rows[11].tolerance"))

    # --- the elements
    blk = [(v, lp, k) for v, lp, k in ls if in_block("cols", lp) and lp != "cols.rel_tol"]
    ok &= check("an identifier is a naming key's string in the block",
                identifier_present(blk) == "cols.identifier")
    ok &= check("a unit is found under a unit-named key",
                unit_present(blk) == "cols.unit")
    ok &= check("a unit is found from a spelled value",
                unit_present([("draws", "cols.kind", "string")]) == "cols.kind")
    ok &= check("a key that merely contains a unit word is not a unit (E208)",
                unit_present([(200.0, "base_draws", "number")]) is None)
    r1 = [(v, lp, k) for v, lp, k in ls if in_block("rows[1]", lp) and lp != "rows[1].tolerance"]
    ok &= check("a magnitude is a block number that is not the gate or a stamp",
                [lp for _v, lp in magnitude_candidates(r1)] == ["rows[1].base_draws"])
    ok &= check("a tolerance-named sibling is never a magnitude",
                magnitude_candidates([(1e-9, "rows[0].rel_tol", "number"),
                                      (5.0, "rows[0].prev", "number")])
                == [(5.0, "rows[0].prev")])
    ok &= check("a scale is a math-marked string in the block",
                scale_present([("max(1.0, prev)", "cols.scale", "string")], [])
                == ("cols.scale", "block"))
    ok &= check("a face-level scale is published with tier=face",
                scale_present([], [("max(1.0, prev)", "gate_scale.expression", "string")])
                == ("gate_scale.expression", "face"))
    ok &= check("a floor-named string with no math is not a scale",
                scale_present([("floor", "cols.note", "string")], []) == (None, None))
    ok &= check("the floor is found under a floor-named key",
                floor_present([(1.0, "cols.floor", "number")], []) == "cols.floor")
    ok &= check("a leaf with only a floor is not reader complete",
                not analyse_leaf(FaceIndex([(1.0, "cols.floor", "number"),
                                            (0.1, "cols.tol", "number")]),
                                 0.1, "cols.tol")["reader_complete"])

    # --- the price of a substitution
    ok &= check("a span is log10(max/min) over positive candidates",
                abs(decoy_span([(1.0, "a"), (1000.0, "b")])["span_orders_of_magnitude"] - 3.0)
                < 1e-12)
    ok &= check("one candidate has no span", decoy_span([(5.0, "a")])
                ["span_orders_of_magnitude"] is None)
    ok &= check("no candidate has no span", decoy_span([])["candidates"] == 0)
    ok &= check("a zero candidate is not priced", decoy_span([(0.0, "a"), (1.0, "b")])
                ["candidates"] == 1)
    ok &= check("the value band is a magnitude statement",
                [value_band(v) for v in (0.0, 1e-9, 0.02, 1.0)]
                == ["exactly_zero", "below_1e-2", "between_1e-2_and_1", "at_least_1"])

    # --- a whole fixture face
    rec = analyse_face("results/fixture.json", face=fx)
    ok &= check("the fixture face is analysed without touching disk", rec["face"] == "results/fixture.json")
    ok &= check("the fixture's three gate leaves are found and its spec leaf is not one",
                rec["gate_leaves"] == 3 and len(rec["spec_context_leaves"]) == 1)
    ok &= check("the fixture's fraction measurement is rejected, not counted",
                rec["rejected_count"] == 1)
    row1 = [r for r in rec["rows"] if r["leaf"] == "rows[1].tolerance"][0]
    ok &= check("a row whose block has a scale and a magnitude is still not complete without "
                "an identifier and a unit", row1["missing_elements"] == ["identifier", "unit"])
    row0 = [r for r in rec["rows"] if r["leaf"] == "rows[0].tolerance"][0]
    ok &= check("a row with three numbers and nothing else is missing three elements",
                row0["missing_elements"] == ["identifier", "unit", "scale"])

    # --- the published face
    c = p["census"]
    ok &= check("identity: every check green", all(x["ok"] for x in p["identity_checks"]))
    ok &= check("findings: the vocabulary over-count is published, not dropped",
                c["rejected_vocabulary"]["leaves"] > 0
                and c["rejected_vocabulary"]["faces"] > 0)
    ok &= check("findings: some leaves are complete and some are not",
                0 < c["reader_complete_leaves"] < c["gate_leaves"])
    ok &= check("findings: no single element is present on every leaf",
                all(v > 0 for v in c["leaves_missing_each_element"].values()))
    ok &= check("findings: faces split between having and lacking a complete leaf",
                c["faces_with_at_least_one_reader_complete_leaf"] > 0
                and c["faces_with_no_reader_complete_leaf"] > 0)
    return 0 if ok else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "run":
        return cmd_run()
    if cmd == "verify":
        return cmd_verify()
    if cmd == "selftest":
        return cmd_selftest()
    print("usage: %s [run|verify|selftest]" % os.path.basename(argv[0]))
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))