"""E464 -- which identity does a producer intend when it writes two names?

E463 showed that 4 faces (2 file pairs) declare two different identity VALUES, that the only
consumer of both is the test suite, and that no producer of the cards the two voices name ever
mentions those faces.  So one producer writes both keys: it holds one intention and two labels.
Nothing had asked which of the two its own module constants, literal dict values or carried
upstream values say it meant.

For every face in the multi-value population this study reads the source that the parent face
names as its producer, and records -- per producer -- three separate things:

  W  does this source WRITE this face?  A writer is resolved by data flow: the path expression of
     an open-for-write / write_text call is expanded through module-level assignments and tuple
     for-loops into face stems, and the stem is compared with the face's own stem.  A source that
     merely names the face (a reader) is published apart rather than counted as its producer.
  K  for each declared identity key, what KIND of expression the producer writes: a literal, a
     module constant (resolved), or a call/subscript (a value carried from an upstream payload).
  M  whether the value it declares is the payload value exactly, only as a slug prefix
     (E413 -> "E413-DOES-THE-..."), or not at all.

The verdict is computed from the writer rows only, so a reader mis-listed as a producer cannot
decide how a face names itself.

Run:      python scripts/e464_producer_intent.py run
Verify:   python scripts/e464_producer_intent.py verify     (re-derives from the live tree)
Check:    python scripts/e464_producer_intent.py check      (tallies re-derive from the face)
Selftest: python scripts/e464_producer_intent.py selftest
"""

import argparse
import ast
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
if os.path.join(ROOT, "scripts") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "scripts"))

import e451_prereg_digest as e451  # noqa: E402  (walk_py / read_text)
import e461_identity_consumers as e461  # noqa: E402  (string_constants)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "producerintent_latest.json"
DATED_PREFIX = "PRODUCERINTENT"
CARD = "E464-WHICH-IDENTITY-A-PRODUCER-INTENDS-WHEN-IT-WRITES-TWO-NAMES"
PARENT_FACE = "identitydialect_latest.json"

# The identity family reads identity names as names, so every member votes itself a producer.
SELF_SKIP = ("e461_", "e462_", "e463_", "e464_", "run_e461", "run_e462", "run_e463", "run_e464")
# A key that can carry an identity.  The parent face grades only `card` and `study`; the payload
# may carry a third voice (NAMERESOLVE also writes source_study=E406_...) that was never graded.
# A face POINTER is not an identity: source_face/face name another file, so they are counted apart
# and never merged into an identity tally (a path is not a study id).
IDENTITY_KEY_VOCAB = ("card", "study", "source_study", "parent_study", "card_id", "study_id")
POINTER_KEY_VOCAB = ("source_face", "face", "face_path")
MAX_READ_BYTES = 2 * 1024 * 1024
MAX_ROWS = 500
MAX_PRODUCERS_PER_FACE = 12
RESOLVE_DEPTH = 3

# A module constant whose NAME says identity.  Value still has to look like a card/study id.
ID_NAME_RE = re.compile(r"^(CARD|CARD_ID|STUDY|STUDY_ID|SOURCE_STUDY|FACE|FACE_ID|FACE_NAME"
                        r"|PARENT_STUDY|SELF_STUDY)(_[A-Z0-9_]+)?$")
ID_VALUE_RE = re.compile(r"^E\d{3}\b")

I_BOTH = "writes_both_voices_itself"
I_ONE_CARRY = "declares_one_identity_and_carries_the_other_from_an_upstream_payload"
I_ONE_ONLY = "declares_one_identity_and_no_second_voice_at_all"
I_NONE = "declares_no_identity_value_for_the_keys_it_writes"
INTENT_CLASSES = (I_BOTH, I_ONE_CARRY, I_ONE_ONLY, I_NONE)

R_NOT_WRITER = "names_the_face_without_writing_it_exactly"
R_WRITES_OTHER_JSON = "names_the_face_and_writes_some_json_but_not_this_face"

V_EMPTY = "no_face_declares_two_identity_values"
V_BOTH = "every_producer_writes_both_voices_itself"
V_CARRY = "every_producer_declares_one_identity_and_carries_the_other"
V_MIXED = "some_producers_write_both_voices_while_others_carry_one_from_upstream"
V_NONE = "no_producer_declares_any_identity_value_for_the_keys_it_writes"
VERDICT_VOCAB = (V_EMPTY, V_BOTH, V_CARRY, V_MIXED, V_NONE)


# ----------------------------------------------------------------------------- helpers


def _load(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def is_own_output(rel):
    base = os.path.basename(rel)
    if base == FACE_NAME:
        return True
    return base.startswith(DATED_PREFIX + "-") and base.endswith(".json")


def face_stem(name):
    """Stem of a face filename or a templated face path piece: SELFRES-%s.json -> selfres."""
    s = name.strip().replace("\\", "/").split("/")[-1].lower()
    if not s.endswith(".json") and ".json" not in s:
        return ""
    s = s.split(".json")[0]
    s = re.sub(r"%[-0-9.]*[sd]|\{[^}]*\}", "", s)
    s = re.sub(r"-(20\d\d)-?(0[1-9]|1[0-2])-?(0[1-9]|[12]\d|3[01])$", "", s)
    s = re.sub(r"(20\d\d)(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])$", "", s)
    s = re.sub(r"[-_](latest|undated)$", "", s)
    s = s.replace("-", "").replace("_", "")
    return s


def identity_values_from_payload(payload):
    """Identity keys the face's own payload carries as non-empty strings (pointers excluded)."""
    out = {}
    for key, val in (payload or {}).items():
        if key in IDENTITY_KEY_VOCAB and isinstance(val, str) and val.strip():
            out[key] = [val]
    return out


def pointer_keys_in_payload(payload):
    """Keys that point at another face: published apart because a path is not an identity."""
    return {key: val for key, val in (payload or {}).items()
            if key in POINTER_KEY_VOCAB and isinstance(val, str) and val.strip()}


def split_rows(parent_rows):
    """Faces declaring two or more distinct identity values (parent columns, machine-read)."""
    out = []
    for row in parent_rows:
        vals = row.get("distinct_declared_values") or []
        if len(vals) < 2:
            continue
        out.append({
            "face": row["face"],
            "family": row.get("family"),
            "declared_values": {f: list(v) for f, v in (row.get("declared_values") or {}).items()},
            "read_names": list(row.get("read_names") or []),
            "never_read_names": list(row.get("never_read_names") or []),
            "producers": list(row.get("producers") or []),
        })
    return out


def _const_str(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def module_constants(tree):
    """Module-level simple string assignments: {NAME: value}.  Last assignment wins."""
    consts = {}
    for node in getattr(tree, "body", []):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name):
            val = _const_str(node.value)
            if val is not None:
                consts[node.targets[0].id] = val
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            val = _const_str(node.value) if node.value is not None else None
            if val is not None:
                consts[node.target.id] = val
    return consts


def identity_constants(consts):
    """The module constants whose name says identity and whose value looks like a card id."""
    return {name: val for name, val in consts.items()
            if ID_NAME_RE.match(name) and ID_VALUE_RE.match(val.strip())}


def _stems_in(expr):
    out = set()
    for node in ast.walk(expr):
        val = _const_str(node)
        if val is None or ".json" not in val.lower():
            continue
        stem = face_stem(val)
        if stem:
            out.add(stem)
    return out


def write_sites(tree):
    """Path expressions of open-for-write / write_text|write_bytes calls, with their data flow."""
    writes = []
    assigns = {}
    loops = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name):
            assigns.setdefault(node.targets[0].id, []).append(node.value)
        elif isinstance(node, ast.For) and isinstance(node.target, ast.Name) \
                and isinstance(node.iter, (ast.Tuple, ast.List)):
            loops.setdefault(node.target.id, []).extend(list(node.iter.elts))
        elif isinstance(node, ast.With):
            for item in node.items:
                if item.optional_vars is None:
                    continue
                call = item.context_expr
                if not isinstance(call, ast.Call):
                    continue
                fname = call.func.attr if isinstance(call.func, ast.Attribute) else ""
                if fname != "open" or not call.args:
                    continue
                mode = _const_str(call.args[1]) if len(call.args) > 1 else ""
                for kw in call.keywords:
                    if kw.arg == "mode":
                        mode = _const_str(kw.value) or mode
                if mode and any(c in mode for c in "wa"):
                    writes.append(call.args[0])
        if isinstance(node, ast.Call):
            f = node.func
            fname = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else "")
            if fname in ("write_text", "write_bytes") and isinstance(f, ast.Attribute):
                writes.append(f.value)
            elif fname == "open" and node.args:
                mode = _const_str(node.args[1]) if len(node.args) > 1 else ""
                for kw in node.keywords:
                    if kw.arg == "mode":
                        mode = _const_str(kw.value) or mode
                if mode and any(c in mode for c in "wa"):
                    writes.append(node.args[0])
    stems = set()
    for expr in writes:
        stems |= _stems_of(expr, assigns, loops, 0)
    return stems


def _stems_of(expr, assigns, loops, depth):
    out = _stems_in(expr)
    if depth >= RESOLVE_DEPTH:
        return out
    names = {n.id for n in ast.walk(expr) if isinstance(n, ast.Name)}
    for name in names:
        for sub in (assigns.get(name) or [])[-2:]:
            out |= _stems_of(sub, assigns, loops, depth + 1)
        for sub in (loops.get(name) or []):
            out |= _stems_of(sub, assigns, loops, depth + 1)
    return out


def key_sites(tree, keys):
    """[(key, kind, value)] for every dict-literal / subscript write of an identity key."""
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            for knode, vnode in zip(node.keys, node.values):
                key = _const_str(knode)
                if key in keys:
                    out.append((key, _value_kind(vnode), _value_text(vnode)))
        elif isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Subscript):
                    key = _const_str(tgt.slice)
                    if key in keys:
                        out.append((key, _value_kind(node.value), _value_text(node.value)))
    return out


def _value_text(node):
    """The literal text, or the bare name, of a value expression (None for anything computed)."""
    if isinstance(node, ast.Constant):
        return _const_str(node)
    if isinstance(node, ast.Name):
        return node.id
    return None


def _value_kind(node):
    if isinstance(node, ast.Constant):
        return "literal"
    if isinstance(node, ast.Name):
        return "name"
    if isinstance(node, ast.Call):
        return "call"
    if isinstance(node, ast.Subscript):
        return "subscript"
    if isinstance(node, ast.JoinedStr):
        return "fstring"
    return "other"


def resolve_kind(kind, value, consts):
    """A name that resolves to a module constant is a declaration, not a carried value."""
    if kind == "name":
        resolved = consts.get(value) if value else None
        return ("constant", resolved) if resolved else ("name_unresolved", None)
    return (kind, value)


def value_match(declared, payload_values):
    """exact when it equals a payload value, prefixed when it is that value plus a slug tail."""
    for pv in payload_values:
        if declared == pv:
            return "exact", pv
    for pv in payload_values:
        if declared.startswith(pv + "-") or declared.startswith(pv + "_"):
            return "prefixed", pv
    return "none", None


# ----------------------------------------------------------------------------- corpus


def index_source(rel, tree, keys):
    consts = module_constants(tree)
    lits = e461.string_constants(tree)
    return {
        "rel": rel,
        "literals": lits,
        "consts": consts,
        "identity_constants": identity_constants(consts),
        "write_stems": write_sites(tree),
        "writes_any_json": any(".json" in v.lower() for v in lits),
        "key_sites": key_sites(tree, keys),
    }


def corpus(keys, skip_self=True):
    out = []
    errors = []
    for rel in e451.walk_py(ROOT):
        base = os.path.basename(rel)
        if is_own_output(rel):
            continue
        if skip_self and any(base.startswith(s) for s in SELF_SKIP):
            continue
        path = os.path.join(ROOT, rel)
        try:
            if os.path.getsize(path) > MAX_READ_BYTES:
                continue
            tree = ast.parse(e451.read_text(path))
        except (SyntaxError, ValueError, OSError):
            errors.append(rel)
            continue
        out.append(index_source(rel, tree, keys))
    return {src["rel"]: src for src in out}, errors


# ----------------------------------------------------------------------------- intent


def producer_row(src, face):
    """One producer's voice, measured three ways (W writes, K expression kind, M value match)."""
    stem = face_stem(os.path.basename(face["face"]))
    exact = stem in src["write_stems"]
    writes_other = (not exact) and src["writes_any_json"] and any(
        face_stem(v) == stem for v in src["literals"])
    keys = sorted(face["declared_values"])
    per_key = {}
    pointers = {}
    carried = []
    declared_values = []
    for key, kind, value in src["key_sites"]:
        rkind, rvalue = resolve_kind(kind, value, src["consts"])
        if key in POINTER_KEY_VOCAB:
            pointers.setdefault(key, []).append({"kind": rkind, "value": rvalue})
            continue
        entry = per_key.setdefault(key, [])
        entry.append({"kind": rkind, "value": rvalue})
        if rkind in ("call", "subscript", "name_unresolved"):
            carried.append(key)
        elif rvalue:
            declared_values.append((key, rvalue))
    matches = {}
    for key, value in declared_values:
        how, hit = value_match(value, face["declared_values"].get(key) or [])
        if how != "none":
            matches[key] = {"declared": value, "payload_value": hit, "match": how}
    distinct = sorted({m["payload_value"] for m in matches.values()})
    if len(distinct) >= 2:
        intent = I_BOTH
    elif len(distinct) == 1 and carried:
        intent = I_ONE_CARRY
    elif len(distinct) == 1:
        intent = I_ONE_ONLY
    else:
        intent = I_NONE
    return {
        "source": src["rel"],
        "writes_this_face": exact,
        "writes_some_json": bool(src["writes_any_json"]),
        "residue": "" if exact else (R_WRITES_OTHER_JSON if writes_other else R_NOT_WRITER),
        "identity_constants": src["identity_constants"],
        "keys_written": per_key,
        "pointer_keys_written": pointers,
        "keys_carried_from_another_payload": sorted(set(carried)),
        "declared_values_that_match_a_payload_value": matches,
        "intent_class": intent,
    }


def grade(rows, sources):
    graded = []
    for face in rows:
        prow = []
        for rel in face["producers"][:MAX_PRODUCERS_PER_FACE]:
            src = sources.get(rel)
            if src is None:
                prow.append({"source": rel, "writes_this_face": None,
                             "residue": "source_not_in_the_corpus", "intent_class": None,
                             "identity_constants": {}, "keys_written": {},
                             "keys_carried_from_another_payload": [],
                             "declared_values_that_match_a_payload_value": {}})
                continue
            prow.append(producer_row(src, face))
        writers = [p for p in prow if p.get("writes_this_face")]
        classes = {c: sum(1 for p in writers if p.get("intent_class") == c) for c in INTENT_CLASSES}
        graded.append({
            "face": face["face"],
            "family": face.get("family"),
            "declared_values": face["declared_values"],
            "declared_values_graded_by_the_parent": face.get(
                "declared_values_graded_by_the_parent") or {},
            "identity_keys_in_the_payload_not_graded_by_the_parent": list(
                face.get("identity_keys_in_the_payload_not_graded_by_the_parent") or []),
            "pointer_keys_in_the_payload": list(face.get("pointer_keys_in_the_payload") or []),
            "pointer_keys_written_by_producers": sorted(
                {k for p in prow for k in (p.get("pointer_keys_written") or {})}),
            "identity_keys_written_that_the_payload_does_not_carry": sorted(
                {k for p in prow for k in (p.get("keys_written") or {})
                 if k not in (face["declared_values"] or {})}),
            "read_names": face["read_names"],
            "never_read_names": face["never_read_names"],
            "producers_named_by_the_parent": face["producers"],
            "producers": prow,
            "writers": [p["source"] for p in writers],
            "writer_count": len(writers),
            "non_writers": [p["source"] for p in prow if not p.get("writes_this_face")],
            "intent_classes_among_writers": classes,
            "producers_declaring_nothing": [
                p["source"] for p in writers if p.get("intent_class") == I_NONE],
        })
    return graded


def verdict_for(graded):
    writers = [p for g in graded for p in g["producers"] if p.get("writes_this_face")]
    if not graded:
        return V_EMPTY
    if not writers:
        return V_NONE
    both = sum(1 for p in writers if p.get("intent_class") == I_BOTH)
    carry = sum(1 for p in writers if p.get("intent_class") == I_ONE_CARRY)
    any_decl = both + carry + sum(1 for p in writers if p.get("intent_class") == I_ONE_ONLY)
    if not any_decl:
        return V_NONE
    if both and not carry and both == len(writers):
        return V_BOTH
    if carry and not both:
        return V_CARRY
    if both and carry:
        return V_MIXED
    return V_NONE


# ----------------------------------------------------------------------------- build


def build(write=True):
    parent = _load(os.path.join(OUTDIR, PARENT_FACE))
    rows = split_rows(parent.get("rows") or [])
    for row in rows:
        row["declared_values_graded_by_the_parent"] = dict(row["declared_values"])
        try:
            payload = _load(os.path.join(ROOT, row["face"]))
        except (OSError, ValueError):
            payload = {}
        carried = identity_values_from_payload(payload)
        row["identity_values_in_the_payload"] = carried
        row["pointer_keys_in_the_payload"] = sorted(pointer_keys_in_payload(payload))
        for key, vals in carried.items():
            row["declared_values"].setdefault(key, vals)
        row["identity_keys_in_the_payload_not_graded_by_the_parent"] = sorted(
            k for k in carried if k not in row["declared_values_graded_by_the_parent"])
    keys = sorted({k for r in rows for k in r["declared_values"]}
                  | set(IDENTITY_KEY_VOCAB) | set(POINTER_KEY_VOCAB))
    sources, errors = corpus(keys)
    graded = grade(rows, sources)

    writers = [p for g in graded for p in g["producers"] if p.get("writes_this_face")]
    summary = {
        "card": CARD,
        "corpus_sources": len(sources),
        "corpus_parse_errors": len(errors),
        "faces_declaring_two_or_more_identity_values": len(graded),
        "distinct_face_stems": len({face_stem(os.path.basename(g["face"])) for g in graded}),
        "producers_named_by_the_parent": sum(len(g["producers_named_by_the_parent"])
                                             for g in graded),
        "producers_that_write_the_face": len(writers),
        "producers_that_do_not_write_the_face": sum(
            len(g["non_writers"]) for g in graded),
        "residue_classes": {
            c: sum(1 for g in graded for p in g["producers"] if p.get("residue") == c)
            for c in (R_NOT_WRITER, R_WRITES_OTHER_JSON)},
        "intent_classes_among_writers": {
            c: sum(1 for p in writers if p.get("intent_class") == c) for c in INTENT_CLASSES},
        "producers_declaring_a_value_that_matches_the_payload": sum(
            1 for p in writers if p.get("declared_values_that_match_a_payload_value")),
        "producer_votes_declared_only_as_a_slug_prefix": sum(
            1 for p in writers for m in (p.get("declared_values_that_match_a_payload_value")
                                        or {}).values() if m.get("match") == "prefixed"),
        "identity_keys_carried_by_the_payloads": sorted(
            {k for g in graded for k in (g.get("declared_values") or {})}),
        "identity_key_instances_in_the_payloads": sum(
            len(g.get("declared_values") or {}) for g in graded),
        "faces_carrying_an_identity_key_the_parent_never_graded": sum(
            1 for g in graded if g.get("identity_keys_in_the_payload_not_graded_by_the_parent")),
        "faces_whose_producer_writes_an_identity_key_the_payload_does_not_carry": sum(
            1 for g in graded if g.get("identity_keys_written_that_the_payload_does_not_carry")),
        "faces_whose_payload_carries_a_pointer_key": sum(
            1 for g in graded if g.get("pointer_keys_in_the_payload")),
        "producer_instances_writing_a_pointer_key": sum(
            1 for g in graded for p in g["producers"] for _ in (p.get("pointer_keys_written")
                                                                or {})),
        "faces_with_no_writer_in_the_corpus": sum(1 for g in graded if not g["writer_count"]),
        "faces_whose_writer_declares_nothing": sum(
            1 for g in graded if g["producers_declaring_nothing"]),
        "writers_per_face": {g["face"]: g["writers"] for g in graded},
    }
    face = {
        "card": CARD,
        "study": "E464",
        "title": "which identity a producer intends when it writes two names",
        "evidence_cutoff": parent.get("evidence_cutoff"),
        "population_source": (
            "the rows of " + PARENT_FACE + " that declare two or more distinct identity values "
            "(machine-read from that face); producers machine-read from each row's own producer "
            "list, then re-measured against the source corpus (" + "/".join(SELF_SKIP)
            + " excluded, own outputs excluded)"
        ),
        "verdict": verdict_for(graded),
        "verdict_vocab": list(VERDICT_VOCAB),
        "intent_classes": list(INTENT_CLASSES),
        "residue_classes": [R_NOT_WRITER, R_WRITES_OTHER_JSON],
        "summary": summary,
        "rows": graded[:MAX_ROWS],
        "parse_errors": errors[:50],
        "method_limits": [
            "the population is the parent face's multi-value rows, so a face that declares two "
            "values but was never graded by the parent is invisible here",
            "the producer list is the parent's, machine-read; this study can refute a listed "
            "producer (it does not write the face) but cannot discover a producer the parent "
            "never listed",
            "a writer is recognised through the path expression of a write call, expanded through "
            "module-level assignments and tuple for-loops only; a path assembled by a function "
            "call or a dict lookup is not resolved and the source is published as a non-writer",
            "a declared value matches the payload when it equals it or when it is that value plus "
            "a slug tail (- or _); the two cases are published apart, never merged",
            "intent is read from dict literals and constant-key subscripts only; a key whose value "
            "is assembled by a helper function carries no kind and is counted as undeclared",
        ],
    }
    if write:
        os.makedirs(OUTDIR, exist_ok=True)
        for name in (FACE_NAME, "%s-%s.json" % (
                DATED_PREFIX, (face.get("evidence_cutoff") or "undated").split()[0])):
            with io.open(os.path.join(OUTDIR, name), "w", encoding="utf-8", newline="\n") as fh:
                json.dump(face, fh, ensure_ascii=False, indent=1)
                fh.write("\n")
    return face


# ----------------------------------------------------------------------------- gates


def tally_problems(face):
    """Every published number must re-derive from the published rows."""
    problems = []
    s = face.get("summary", {})
    rows = face.get("rows", [])
    if s.get("faces_declaring_two_or_more_identity_values") != len(rows):
        problems.append("face count %r != rows %r"
                        % (s.get("faces_declaring_two_or_more_identity_values"), len(rows)))
    writers = [p for r in rows for p in (r.get("producers") or []) if p.get("writes_this_face")]
    if s.get("producers_that_write_the_face") != len(writers):
        problems.append("writer total does not re-derive from the rows")
    if s.get("producers_that_do_not_write_the_face") != sum(
            len(r.get("non_writers") or []) for r in rows):
        problems.append("non-writer total does not re-derive from the rows")
    for c in INTENT_CLASSES:
        got = sum(1 for p in writers if p.get("intent_class") == c)
        if (s.get("intent_classes_among_writers") or {}).get(c) != got:
            problems.append("intent class %s: published %r rows %r"
                            % (c, (s.get("intent_classes_among_writers") or {}).get(c), got))
    for c in (R_NOT_WRITER, R_WRITES_OTHER_JSON):
        got = sum(1 for r in rows for p in (r.get("producers") or []) if p.get("residue") == c)
        if (s.get("residue_classes") or {}).get(c) != got:
            problems.append("residue class %s: published %r rows %r"
                            % (c, (s.get("residue_classes") or {}).get(c), got))
    if s.get("producers_declaring_a_value_that_matches_the_payload") != sum(
            1 for p in writers if p.get("declared_values_that_match_a_payload_value")):
        problems.append("payload-matching producer total does not re-derive from the rows")
    if s.get("faces_with_no_writer_in_the_corpus") != sum(
            1 for r in rows if not (r.get("writer_count") or 0)):
        problems.append("writerless face total does not re-derive from the rows")
    if s.get("faces_whose_writer_declares_nothing") != sum(
            1 for r in rows if r.get("producers_declaring_nothing")):
        problems.append("undeclared face total does not re-derive from the rows")
    if s.get("producers_named_by_the_parent") != sum(
            len(r.get("producers_named_by_the_parent") or []) for r in rows):
        problems.append("named-producer total does not re-derive from the rows")
    if s.get("writers_per_face") != {r["face"]: r.get("writers") or [] for r in rows}:
        problems.append("writers_per_face does not re-derive from the rows")
    if s.get("identity_key_instances_in_the_payloads") != sum(
            len(r.get("declared_values") or {}) for r in rows):
        problems.append("identity-key instance total does not re-derive from the rows")
    if s.get("faces_carrying_an_identity_key_the_parent_never_graded") != sum(
            1 for r in rows if r.get("identity_keys_in_the_payload_not_graded_by_the_parent")):
        problems.append("ungraded identity-key face total does not re-derive from the rows")
    if s.get("faces_whose_producer_writes_an_identity_key_the_payload_does_not_carry") != sum(
            1 for r in rows if r.get("identity_keys_written_that_the_payload_does_not_carry")):
        problems.append("producer-writes-an-unpublished-key total does not re-derive from the rows")
    if s.get("producer_votes_declared_only_as_a_slug_prefix") != sum(
            1 for p in writers for m in (p.get("declared_values_that_match_a_payload_value")
                                         or {}).values() if m.get("match") == "prefixed"):
        problems.append("slug-prefix vote total does not re-derive from the rows")
    if s.get("faces_whose_payload_carries_a_pointer_key") != sum(
            1 for r in rows if r.get("pointer_keys_in_the_payload")):
        problems.append("pointer-key face total does not re-derive from the rows")
    if s.get("producer_instances_writing_a_pointer_key") != sum(
            1 for r in rows for p in (r.get("producers") or [])
            for _ in (p.get("pointer_keys_written") or {})):
        problems.append("pointer-key producer total does not re-derive from the rows")
    for r in rows:
        got_writers = sorted(p["source"] for p in (r.get("producers") or [])
                             if p.get("writes_this_face"))
        if sorted(r.get("writers") or []) != got_writers:
            problems.append("row %s writer list does not re-derive" % r.get("face"))
        if r.get("writer_count") != len(got_writers):
            problems.append("row %s writer count does not re-derive" % r.get("face"))
        got_non = sorted(p["source"] for p in (r.get("producers") or [])
                         if not p.get("writes_this_face"))
        if sorted(r.get("non_writers") or []) != got_non:
            problems.append("row %s non-writer list does not re-derive" % r.get("face"))
        for p in r.get("producers") or []:
            if p.get("writes_this_face") and p.get("residue"):
                problems.append("row %s writer %s carries a non-writer residue"
                                % (r.get("face"), p.get("source")))
            if not p.get("writes_this_face") and not p.get("residue"):
                problems.append("row %s non-writer %s carries no residue class"
                                % (r.get("face"), p.get("source")))
            for key, entries in (p.get("keys_written") or {}).items():
                if key not in IDENTITY_KEY_VOCAB:
                    problems.append("row %s producer %s writes a key outside the identity "
                                    "vocabulary" % (r.get("face"), p.get("source")))
                if not entries:
                    problems.append("row %s producer %s has an empty key site list"
                                    % (r.get("face"), p.get("source")))
        got_unpublished = sorted({k for p in (r.get("producers") or [])
                                  for k in (p.get("keys_written") or {})
                                  if k not in (r.get("declared_values") or {})})
        if sorted(r.get("identity_keys_written_that_the_payload_does_not_carry") or []) \
                != got_unpublished:
            problems.append("row %s unpublished-key list does not re-derive" % r.get("face"))
        for p in r.get("producers") or []:
            for key in (p.get("pointer_keys_written") or {}):
                if key not in POINTER_KEY_VOCAB:
                    problems.append("row %s producer %s writes a non-pointer key as a pointer"
                                    % (r.get("face"), p.get("source")))
    if face.get("verdict") != verdict_for(rows):
        problems.append("verdict does not re-derive from the rows")
    return problems


def verify():
    problems = []
    live = build(write=False)
    on_disk = _load(os.path.join(OUTDIR, FACE_NAME))
    if live["summary"] != on_disk.get("summary"):
        diff = sorted(k for k in live["summary"] if live["summary"][k] != on_disk["summary"].get(k))
        problems.append("summary is stale against the live tree: %s" % ", ".join(diff))
    if live.get("verdict") != on_disk.get("verdict"):
        problems.append("verdict differs: live %r disk %r"
                        % (live.get("verdict"), on_disk.get("verdict")))
    problems.extend(tally_problems(on_disk))
    return problems


def check():
    return tally_problems(_load(os.path.join(OUTDIR, FACE_NAME)))


# ----------------------------------------------------------------------------- selftest


def _tree(src):
    return ast.parse(src)


def selftest():
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    # --- stems
    leg("a dated face stem drops the date",
        face_stem("SELFRES-2026-10-29.json") == "selfres")
    leg("a templated stem drops the placeholder",
        face_stem("SELFRES-%s.json") == "selfres")
    leg("a latest stem drops the suffix",
        face_stem("nameresolve_latest.json") == "nameresolve")
    leg("two spellings of one face share a stem",
        face_stem("NAMERESOLVE-2026-11-04.json") == face_stem("nameresolve_latest.json"))
    leg("a non-json literal is not a face stem", face_stem("results/state_tilt") == "")

    # --- population
    parent_rows = [
        {"face": "results/x/SPLIT-2026-11-06.json", "declared_values":
         {"card": ["E413"], "study": ["E421"]}, "producers": ["p.py"], "read_names": ["card"],
         "never_read_names": [], "distinct_declared_values": ["E413", "E421"]},
        {"face": "results/x/AGREE-2026-11-06.json", "declared_values":
         {"card": ["E1"], "study": ["E1"]}, "producers": ["p.py"], "read_names": ["card"],
         "never_read_names": [], "distinct_declared_values": ["E1"]},
    ]
    rows = split_rows(parent_rows)
    leg("only a face with two distinct values enters the population", len(rows) == 1)
    leg("values are carried verbatim", rows[0]["declared_values"]["study"] == ["E421"])
    payload_keys = identity_values_from_payload(
        {"card": "E413-A", "study": "E421_b", "source_study": "E406_x", "verdict": "v",
         "rows": [1]})
    leg("a face's own payload is asked for its identity keys, not for any string key",
        sorted(payload_keys) == ["card", "source_study", "study"])
    leg("the third voice the parent never graded is visible in the payload",
        payload_keys["source_study"] == ["E406_x"])
    leg("a pointer key is not counted as an identity",
        identity_values_from_payload({"source_face": "results/x/a.json", "face": "a.json"}) == {}
        and sorted(pointer_keys_in_payload({"source_face": "results/x/a.json"}))
        == ["source_face"])

    # --- constants and identity constants
    tree = _tree('STUDY = "E253"\nSTUDY_NAME = "self row"\nFACE = "results/x/a.json"\n')
    consts = module_constants(tree)
    leg("module constants are read", consts.get("STUDY") == "E253")
    ids = identity_constants(consts)
    leg("an identity constant needs both an identity name and a card-shaped value",
        ids == {"STUDY": "E253"})

    # --- key kinds
    keys = ["card", "study", "source_study"]
    tree = _tree('f = {"study": STUDY, "source_study": src.get("study"),\n'
                 '     "card": "E413-DOES-X"}\n')
    sites = key_sites(tree, keys)
    kinds = {k: kind for k, kind, _v in sites}
    leg("a literal, a name and a call are three different kinds",
        kinds.get("card") == "literal" and kinds.get("study") == "name"
        and kinds.get("source_study") == "call")
    leg("a name resolving to a constant is a declaration, not a carried value",
        resolve_kind("name", "STUDY", consts) == ("constant", "E253"))
    leg("an unresolved name stays unresolved",
        resolve_kind("name", "NOPE", consts) == ("name_unresolved", None))

    # --- value match
    leg("an exact payload value matches exactly",
        value_match("E421", ["E421"]) == ("exact", "E421"))
    leg("a slug prefix matches only as a prefix",
        value_match("E413-DOES-THE-STRONG-BASIS", ["E413"]) == ("prefixed", "E413"))
    leg("a prefix is not accepted as an exact match",
        value_match("E4131", ["E413"])[0] == "none")

    # --- writer detection through data flow
    src = ('out = os.path.join(OUTDIR, "SELFRES-%s.json" % cutoff)\n'
           'latest = os.path.join(OUTDIR, "selfres_latest.json")\n'
           'for target in (out, latest):\n'
           '    with io.open(target, "w", encoding="utf-8") as fh:\n'
           '        json.dump(face, fh)\n')
    leg("a writer is found through a variable and a tuple loop",
        {"selfres"} == write_sites(_tree(src)))
    reader = ('src = io.open(os.path.join(OUTDIR, "SELFRES-2026-10-29.json"), encoding="utf-8")\n')
    leg("a reader that only opens for reading is not a writer", write_sites(_tree(reader)) == set())

    # --- intent classification
    face = {"face": "results/x/SELFRES-2026-10-29.json",
            "declared_values": {"source_study": ["E252"], "study": ["E253"]}}
    carried_src = index_source("carries.py", _tree(
        'STUDY = "E253"\n'
        'open("results/x/SELFRES-2026-10-29.json", "w")\n'
        'f = {"study": STUDY, "source_study": src.get("study")}\n'), keys)
    row = producer_row(carried_src, face)
    leg("a writer that declares one value and carries the other is classed as carrying",
        row["writes_this_face"] and row["intent_class"] == I_ONE_CARRY
        and row["keys_carried_from_another_payload"] == ["source_study"])

    face2 = {"face": "results/x/NAMERESOLVE-2026-11-04.json",
             "declared_values": {"card": ["E413"], "study": ["E421"]}}
    both_src = index_source("both.py", _tree(
        'open("results/x/NAMERESOLVE-2026-11-04.json", "w")\n'
        'f = {"card": "E413-DOES-X", "study": "E421_a_name"}\n'), keys)
    row2 = producer_row(both_src, face2)
    leg("a writer that declares both voices as slugs is classed as writing both",
        row2["intent_class"] == I_BOTH)
    leg("both of its matches are published as prefixes",
        sorted(m["match"] for m in row2["declared_values_that_match_a_payload_value"].values())
        == ["prefixed", "prefixed"])

    silent_src = index_source("silent.py", _tree(
        'open("results/x/NAMERESOLVE-2026-11-04.json", "w")\n'), keys)
    leg("a writer that writes no identity key declares nothing",
        producer_row(silent_src, face2)["intent_class"] == I_NONE)

    reader_src = index_source("reader.py", _tree(
        'E253_FACE = os.path.join(OUTDIR, "SELFRES-2026-10-29.json")\n'
        'STUDY = "E254"\n'
        'open("results/x/SELFRES-2026-10-29.json", encoding="utf-8")\n'
        'open("results/x/BANDPOW-2026-10-29.json", "w")\n'), keys)
    leg("a source that names the face, writes other json and never writes this face is residue",
        producer_row(reader_src, face)["residue"] == R_WRITES_OTHER_JSON)

    # --- verdict branches
    def graded_with(classes, writers=True):
        prods = [{"source": "p%d.py" % i, "writes_this_face": writers,
                  "intent_class": c} for i, c in enumerate(classes)]
        return [{"face": "f.json", "producers": prods}]

    leg("verdict is empty on an empty population", verdict_for([]) == V_EMPTY)
    leg("verdict is both when every writer declares both",
        verdict_for(graded_with([I_BOTH, I_BOTH])) == V_BOTH)
    leg("verdict is carry when every writer carries one",
        verdict_for(graded_with([I_ONE_CARRY])) == V_CARRY)
    leg("verdict is mixed when one writer declares both and one carries",
        verdict_for(graded_with([I_BOTH, I_ONE_CARRY])) == V_MIXED)
    leg("verdict is none when no writer declares anything",
        verdict_for(graded_with([I_NONE])) == V_NONE)

    # --- gates
    good = {
        "verdict": V_NONE,
        "summary": {
            "faces_declaring_two_or_more_identity_values": 1,
            "producers_that_write_the_face": 1,
            "producers_that_do_not_write_the_face": 0,
            "producers_named_by_the_parent": 1,
            "intent_classes_among_writers": {c: (1 if c == I_NONE else 0)
                                             for c in INTENT_CLASSES},
            "residue_classes": {R_NOT_WRITER: 0, R_WRITES_OTHER_JSON: 0},
            "producers_declaring_a_value_that_matches_the_payload": 0,
            "faces_with_no_writer_in_the_corpus": 0,
            "faces_whose_writer_declares_nothing": 1,
            "identity_key_instances_in_the_payloads": 2,
            "faces_carrying_an_identity_key_the_parent_never_graded": 0,
            "faces_whose_producer_writes_an_identity_key_the_payload_does_not_carry": 0,
            "producer_votes_declared_only_as_a_slug_prefix": 0,
            "faces_whose_payload_carries_a_pointer_key": 0,
            "producer_instances_writing_a_pointer_key": 0,
            "writers_per_face": {"f.json": ["p0.py"]},
        },
        "rows": [{
            "face": "f.json",
            "declared_values": {"card": ["E413"], "study": ["E421"]},
            "declared_values_graded_by_the_parent": {"card": ["E413"], "study": ["E421"]},
            "identity_keys_in_the_payload_not_graded_by_the_parent": [],
            "pointer_keys_in_the_payload": [],
            "pointer_keys_written_by_producers": [],
            "identity_keys_written_that_the_payload_does_not_carry": [],
            "producers_named_by_the_parent": ["p0.py"],
            "producers": [{
                "source": "p0.py", "writes_this_face": True, "residue": "",
                "intent_class": I_NONE, "keys_written": {"card": [{"kind": "call",
                                                                   "value": None}]},
                "pointer_keys_written": {},
                "keys_carried_from_another_payload": ["card"],
                "declared_values_that_match_a_payload_value": {}}],
            "writers": ["p0.py"], "writer_count": 1, "non_writers": [],
            "producers_declaring_nothing": ["p0.py"],
        }],
    }
    leg("gate accepts a consistent face", tally_problems(good) == [])
    good["summary"]["faces_declaring_two_or_more_identity_values"] = 2
    leg("gate refuses a face count that does not re-derive",
        any("face count" in p for p in tally_problems(good)))
    good["summary"]["faces_declaring_two_or_more_identity_values"] = 1
    good["summary"]["intent_classes_among_writers"][I_NONE] = 0
    leg("gate refuses an intent tally that does not re-derive",
        any("intent class" in p for p in tally_problems(good)))
    good["summary"]["intent_classes_among_writers"][I_NONE] = 1
    good["rows"][0]["producers"][0]["writes_this_face"] = False
    leg("gate refuses a writer that carries no residue when it stops being a writer",
        any("residue" in p for p in tally_problems(good)))
    good["rows"][0]["producers"][0]["writes_this_face"] = True
    good["rows"][0]["producers"][0]["keys_written"] = {"mystery": [{"kind": "literal",
                                                                   "value": "x"}]}
    good["rows"][0]["identity_keys_written_that_the_payload_does_not_carry"] = ["mystery"]
    leg("gate refuses a producer writing a key outside the identity vocabulary",
        any("identity vocabulary" in p for p in tally_problems(good)))
    good["rows"][0]["producers"][0]["keys_written"] = {"card": [{"kind": "call", "value": None}]}
    good["rows"][0]["identity_keys_written_that_the_payload_does_not_carry"] = []
    good["verdict"] = V_BOTH
    leg("gate refuses a verdict that does not re-derive from the rows",
        any("verdict" in p for p in tally_problems(good)))

    leg("own face is skipped by name", is_own_output("results/state_tilt/" + FACE_NAME))
    leg("a dated own output is skipped",
        is_own_output("results/state_tilt/%s-2026-11-06.json" % DATED_PREFIX))
    leg("the parent face is not own output", not is_own_output(
        "results/state_tilt/identitydialect_latest.json"))

    ok = sum(1 for _n, c in legs if c)
    for name, cond in legs:
        print(("PASS " if cond else "FAIL ") + name)
    print("selftest %d/%d" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


# ----------------------------------------------------------------------------- main


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "run":
        face = build(write=True)
        s = face["summary"]
        print("verdict:", face["verdict"])
        print("multi-value faces:", s["faces_declaring_two_or_more_identity_values"],
              "| stems:", s["distinct_face_stems"],
              "| producers named:", s["producers_named_by_the_parent"],
              "| writers:", s["producers_that_write_the_face"])
        print("intent among writers:", s["intent_classes_among_writers"],
              "| residue:", s["residue_classes"])
        print("writers per face:", s["writers_per_face"])
        problems = tally_problems(face)
        print("problems:", problems)
        return 0 if not problems else 1
    if cmd == "verify":
        problems = verify()
        print("problems:", problems)
        return 0 if not problems else 1
    if cmd == "check":
        problems = check()
        print("problems:", problems)
        return 0 if not problems else 1
    if cmd == "selftest":
        return selftest()
    print("usage: e464_producer_intent.py [run|verify|check|selftest]", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))