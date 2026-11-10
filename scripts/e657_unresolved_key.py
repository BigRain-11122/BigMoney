"""E657 -- how big is E647's unresolved-string blind spot for counted row keys?

E655 hit the edge of the instrument: E652 asks "does this file carry a counted row key?" and answers
from ``e647.collect_strings``, which hands a percent-formatted expression (and a value-bearing
f-string, and ``.format``) back as ONE unresolved handle and then **does not descend into it**.  A
counted key that lives inside that subtree -- ``"%s" % (blk["rows"],)`` -- is therefore invisible to
the literal arm, and the handle is published with a start position but no span.

This study sizes that blind spot corpus-wide, and separates the two ways a key can hide:

  subscript_key     the constant is the slice of a ``Subscript``; E652's *second* arm walks the whole
                    tree for exactly these, so the key is already counted there even though the
                    boolean ``carries_a_counted_row_key`` says otherwise -- an internal disagreement,
                    not a lost key
  everything else   dict-literal key, call argument, comparison, plain constant: invisible to BOTH
                    arms, because the literal arm cannot see into the handle and the subscript arm is
                    looking for a different shape

The deliverable is not the volume alone: for every module E652 published a row for, this face prints
E652's own two fields next to what is actually inside the handles, and it publishes separately the
files E652 never priced because they do not spell a read module.

  python scripts/e657_unresolved_key.py            # rebuild the face
  python scripts/e657_unresolved_key.py check      # rebuild + gate
  python scripts/e657_unresolved_key.py verify     # gate the published face
  python scripts/e657_unresolved_key.py selftest
"""
from __future__ import annotations

import argparse
import ast
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-10"
FACE = "UNRESOLVEDKEY.json"
LATEST = "unresolvedkey_latest.json"
STUDY = "E657_unresolved_string_handle"
SOURCE_FACE = "results/state_tilt/STRINGARMCENSUS.json"
SELF_PARTS = ("e657_", "run_e657_", "_r1674")
MAX_BYTES = 1024 * 1024          # E391's read cap, carried so every study in this family skips alike
MAX_HANDLES_PER_FILE = 40
MAX_SITES_PER_HANDLE = 12
DETAIL_BUDGET = 60          # files that keep per-handle detail; the rest keep their counts only
SOURCE_TRUNC = 200

ROLE_ORDER = ("dict_literal_key", "subscript_key", "call_argument", "comparison",
              "string_constant", "other_string")
KIND_ORDER = ("percent_formatting", "fstring_with_a_value", "str_format")

import e647_string_reach as e647  # noqa: E402
import e648_keygenericity as e648  # noqa: E402
import e652_string_arm_census as e652  # noqa: E402
import e655_counted_key_route as e655  # noqa: E402

# e647 records why a string could not be resolved; each why maps to the one node kind that produced it
KIND_OF_WHY = {"percent_formatting": "percent_formatting",
               "fstring_has_a_formatted_value": "fstring_with_a_value",
               "str_format": "str_format"}
NODE_OF_KIND = {"percent_formatting": (ast.BinOp,),
                "fstring_with_a_value": (ast.JoinedStr,),
                "str_format": (ast.Call,)}

V_NO_HANDLES = (
    "the_tree_reports_no_unresolved_string_handle_at_all,_so_there_is_no_subtree_for_a_counted_key_"
    "to_hide_inside_and_E652s_literal_arm_is_complete_on_this_population")
V_NO_KEYS = (
    "unresolved_handles_are_numerous,_but_not_one_string_constant_equal_to_a_counted_row_key_sits_"
    "inside_any_of_them,_so_the_blind_spot_E655_named_is_real_in_shape_and_empty_in_keys")
V_ALL_SUBSCRIPT = (
    "every_counted_key_inside_an_unresolved_handle_is_a_subscript_slice,_and_E652s_second_arm_walks_"
    "the_whole_tree_for_exactly_those,_so_the_handle_costs_neither_arm_a_key:_the_only_defect_is_that_"
    "the_boolean_carries_a_counted_row_key_is_derived_from_the_literal_arm_and_disagrees_with_the_"
    "subscript_arm_in_the_same_row")
V_INVISIBLE_OUTSIDE = (
    "counted_key_sites_inside_an_unresolved_handle_exist_in_a_role_neither_E652_arm_can_see,_but_"
    "not_one_of_them_sits_in_a_file_E652_published_a_row_for,_so_no_published_key_count_moves:_the_"
    "blind_spot_costs_the_corpus_wide_'carries_a_counted_row_key'_volume_inside_files_that_never_"
    "spell_a_read_module,_and_leaves_E652s_headline_intact")
V_INVISIBLE_INSIDE = (
    "some_counted_key_sites_inside_an_unresolved_handle_are_not_subscript_slices_and_at_least_one_"
    "of_them_sits_in_a_file_E652_published,_so_they_are_invisible_to_both_arms_and_the_published_"
    "census_undercounts_a_file_it_already_priced")


def say(line):
    sys.stdout.write(line + "\n")


def rel(module, root=ROOT):
    return os.path.relpath(module, root).replace("\\", "/")


def _source(module):
    try:
        lines = io.open(module, encoding="utf-8", errors="replace").read().splitlines()
    except OSError:
        return ""
    if not lines:
        return ""
    return lines[0].strip()[:SOURCE_TRUNC]


# ---------------------------------------------------------------- per-file
def handle_nodes(tree):
    """(line, column) -> candidate nodes, so an E647 handle can be resolved back to its subtree."""
    out = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.JoinedStr, ast.BinOp, ast.Call)):
            out.setdefault((node.lineno, node.col_offset), []).append(node)
    return out


def _resolve_handle(entry, nodes):
    kind = KIND_OF_WHY.get(entry.get("why"))
    if kind is None:
        return None, None
    wanted = NODE_OF_KIND[kind]
    for node in nodes.get((entry.get("line") or 0, entry.get("column") or 0), []):
        if isinstance(node, wanted):
            return kind, node
    return kind, None


def _span(node):
    start = node.lineno or 1
    end = node.end_lineno or start
    return [start, end]


def scan_file(path, keys, root=ROOT):
    """(payload, None) or (None, why): the unresolved handles of one file, priced against counted keys."""
    try:
        if os.path.getsize(path) > MAX_BYTES:
            return None, "over_the_size_cap"
        src = io.open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return None, "unreadable"
    try:
        tree = ast.parse(src)
    except (SyntaxError, ValueError):
        return None, "does_not_parse"
    parents = e647.parents_of(tree)
    literals, unresolved = e647.collect_strings(tree)
    nodes = handle_nodes(tree)
    handles, unresolved_handles, unreadable_handles = [], 0, 0
    elided_handles = 0
    for entry in unresolved:
        unresolved_handles += 1
        kind, node = _resolve_handle(entry, nodes)
        if node is None:
            unreadable_handles += 1
            continue
        constants = [c for c in ast.walk(node)
                     if isinstance(c, ast.Constant) and isinstance(c.value, str)]
        sites = []
        for const in constants:
            if const.value not in keys:
                continue
            parent = parents.get(const)
            role = e655.role_of(parent, const)
            site = {"key": const.value,
                    "line": const.lineno,
                    "column": const.col_offset,
                    "role": role,
                    "source": e655._line_source(src.splitlines(), const)}
            if role == "call_argument" and isinstance(parent, ast.Call):
                site["callee"] = e647._call_text(parent.func) or None
            sites.append(site)
        sites.sort(key=lambda s: (s["line"], s["column"]))
        if not sites:
            continue
        published = sites[:MAX_SITES_PER_HANDLE]
        handles.append({
            "kind": kind,
            "line": node.lineno,
            "column": node.col_offset,
            "span": _span(node),
            "string_constants_inside": len(constants),
            "counted_keys": published,
            "counted_keys_elided": max(0, len(sites) - len(published)),
            "counted_key_sites": len(sites),
            "invisible_sites": len([s for s in sites if s["role"] != "subscript_key"]),
            "source": e655._line_source(src.splitlines(), node),
        })
        if len(handles) >= MAX_HANDLES_PER_FILE:
            elided_handles = 1
            break
    handles.sort(key=lambda h: (h["line"], h["column"], h["kind"]))
    return {"handles": handles,
            "unresolved_handles": unresolved_handles,
            "unreadable_handles": unreadable_handles,
            "elided_handles": elided_handles,
            "string_literals": len(literals),
            "subscript_key_sites_anywhere": sum(
                1 for n in ast.walk(tree)
                if isinstance(n, ast.Subscript) and isinstance(n.slice, ast.Constant)
                and isinstance(n.slice.value, str) and n.slice.value in keys)}, None


# ---------------------------------------------------------------- e652 comparison
def load_e652(path=None):
    path = path or os.path.join(ROOT, SOURCE_FACE)
    if not os.path.exists(path):
        return {}, None
    doc = json.load(io.open(path, encoding="utf-8"))
    rows = {}
    for row in (doc.get("rows") or []):
        rows[row.get("module")] = {
            "carries_a_counted_row_key": bool(row.get("carries_a_counted_row_key")),
            "counted_keys_named": list(row.get("counted_keys_named") or []),
            "subscript_key_sites": int(row.get("subscript_key_sites") or 0),
            "unresolved_strings": int(row.get("unresolved_strings") or 0)}
    return rows, doc.get("generated") or doc.get("asof") or TODAY


def classify_against_e652(row, here):
    """What E652's two fields say about the same file, next to what the handles actually hold."""
    if row is None:
        return "outside_e652s_published_population"
    if here["invisible_sites"] > 0:
        return "invisible_to_both_arms"
    if row["subscript_key_sites"] >= here["counted_key_sites"]:
        return "already_counted_by_e652s_subscript_arm"
    return "seen_by_e652_but_undercounted"


# ---------------------------------------------------------------- measure
def measure(root=ROOT, counted=None, e652_rows=None):
    reads = e648.read_population() if counted is None else counted
    keys = {r["key"] for r in reads if r.get("key")}
    if e652_rows is None:
        e652_rows, _stamp = load_e652()
    files = e652.corpus(root)

    holes = {"over_the_size_cap": 0, "unreadable": 0, "does_not_parse": 0}
    volume = {"unresolved_handles": 0, "unreadable_handles": 0,
              "elided_handles": 0, "elided_sites": 0,
              "string_literals_examined": 0, "files_with_an_unresolved_handle": 0,
              "files_with_a_counted_key_inside_a_handle": 0,
              "subscript_key_sites_anywhere": 0,
              "counted_key_sites_inside_handles": 0,
              "invisible_sites": 0,
              "counted_key_sites_by_role": {},
              "counted_key_sites_by_kind": {},
              "invisible_by_role": {},
              "invisible_by_callee": {},
              "files_by_outcome": {}}
    rows, outside = [], []
    for path in files:
        got, why = scan_file(path, keys, root)
        if why is not None:
            holes[why] = holes.get(why, 0) + 1
            continue
        volume["unresolved_handles"] += got["unresolved_handles"]
        volume["unreadable_handles"] += got["unreadable_handles"]
        volume["elided_handles"] += got["elided_handles"]
        volume["elided_sites"] += sum(h["counted_keys_elided"] for h in got["handles"])
        volume["string_literals_examined"] += got["string_literals"]
        volume["subscript_key_sites_anywhere"] += got["subscript_key_sites_anywhere"]
        if got["unresolved_handles"]:
            volume["files_with_an_unresolved_handle"] += 1
        if not got["handles"]:
            continue
        module = rel(path, root)
        sites = sum(h["counted_key_sites"] for h in got["handles"])
        invisible = sum(h["invisible_sites"] for h in got["handles"])
        volume["counted_key_sites_inside_handles"] += sites
        volume["invisible_sites"] += invisible
        volume["files_with_a_counted_key_inside_a_handle"] += 1
        for h in got["handles"]:
            volume["counted_key_sites_by_kind"][h["kind"]] = \
                volume["counted_key_sites_by_kind"].get(h["kind"], 0) + h["counted_key_sites"]
            for s in h["counted_keys"]:
                volume["counted_key_sites_by_role"][s["role"]] = \
                    volume["counted_key_sites_by_role"].get(s["role"], 0) + 1
                if s["role"] == "subscript_key":
                    continue
                volume["invisible_by_role"][s["role"]] = \
                    volume["invisible_by_role"].get(s["role"], 0) + 1
                if s["role"] == "call_argument":
                    callee = s.get("callee") or "(unknown)"
                    volume["invisible_by_callee"][callee] = \
                        volume["invisible_by_callee"].get(callee, 0) + 1
        here = {"counted_key_sites": sites, "invisible_sites": invisible}
        cls = classify_against_e652(e652_rows.get(module), here)
        volume["files_by_outcome"][cls] = volume["files_by_outcome"].get(cls, 0) + 1
        entry = {"module": module,
                 "counted_key_sites": sites,
                 "invisible_sites": invisible,
                 "counted_keys": sorted({s["key"] for h in got["handles"]
                                         for s in h["counted_keys"]}),
                 "kinds": sorted({h["kind"] for h in got["handles"]}),
                 "class": cls,
                 "handles": got["handles"]}
        if cls == "outside_e652s_published_population":
            outside.append({"module": module, "counted_key_sites": sites,
                            "invisible_sites": invisible,
                            "counted_keys": entry["counted_keys"],
                            "kinds": entry["kinds"],
                            "handles": got["handles"]})
            continue
        e = e652_rows.get(module) or {}
        entry.update({"e652_carries_a_counted_row_key": e.get("carries_a_counted_row_key"),
                      "e652_counted_keys_named": e.get("counted_keys_named"),
                      "e652_subscript_key_sites": e.get("subscript_key_sites")})
        rows.append(entry)
    rows.sort(key=lambda r: (r["class"], r["module"]))
    outside.sort(key=lambda r: r["module"])
    # 707 files carry a counted key in a handle; publishing every handle would make this face the
    # largest in the family by an order of magnitude, so detail is spent on the files that carry an
    # invisible site (the only ones whose shape the counts do not already imply), deepest first, and
    # the elision is counted rather than silent
    ranked = sorted([r for r in rows + outside if r["invisible_sites"] > 0],
                    key=lambda r: (-r["invisible_sites"], r["module"]))
    detailed = {r["module"] for r in ranked[:DETAIL_BUDGET]}
    detailed |= {r["module"] for r in rows}
    elided = 0
    for entry in rows + outside:
        if entry["module"] not in detailed:
            elided += 1
            entry["handles_elided"] = len(entry.pop("handles") or [])
        else:
            entry["handles_elided"] = 0
    for entry in outside:
        for handle in entry.get("handles") or []:
            handle.pop("source", None)

    c = dict(volume)
    c.update({
        "python_files_seen": len(files),
        "python_files_scanned": len(files) - sum(holes.values()),
        "holes": holes,
        "counted_read_lines": len(reads),
        "counted_row_keys": len(keys),
        "counted_row_key_names": sorted(keys),
        "e652_published_rows": len(e652_rows),
        "files_matched_to_an_e652_row": len(rows),
        "e652_rows_published_without_a_key_but_carrying_one_here":
            len([r for r in rows
                 if r["e652_carries_a_counted_row_key"] is False and r["counted_key_sites"] > 0]),
        "matched_files_carrying_an_invisible_site":
            len([r for r in rows if r["invisible_sites"] > 0]),
        "files_published_without_a_key_but_carrying_an_invisible_one":
            len([r for r in rows if r["e652_carries_a_counted_row_key"] is False
                 and r["invisible_sites"] > 0]),
        "e652_rows_whose_boolean_contradicts_their_own_subscript_field":
            len([r for r in rows if r["e652_carries_a_counted_row_key"] is False
                 and (r["e652_subscript_key_sites"] or 0) > 0]),
        "files_outside_e652s_published_population": len(outside),
        "files_with_handles_elided": elided,
        "files_with_handle_detail": len(rows) + len(outside) - elided,
        "invisible_sites_outside_e652s_published_population":
            sum(r["invisible_sites"] for r in outside),
    })
    c["counted_key_sites_by_role"] = {k: c["counted_key_sites_by_role"][k]
                                      for k in sorted(c["counted_key_sites_by_role"])}
    c["counted_key_sites_by_kind"] = {k: c["counted_key_sites_by_kind"][k]
                                      for k in sorted(c["counted_key_sites_by_kind"])}
    c["invisible_by_role"] = {k: c["invisible_by_role"][k]
                              for k in sorted(c["invisible_by_role"])}
    c["invisible_by_callee"] = {k: c["invisible_by_callee"][k]
                                for k in sorted(c["invisible_by_callee"],
                                                key=lambda k: (-c["invisible_by_callee"][k], k))}
    c["files_by_outcome"] = {k: c["files_by_outcome"][k]
                             for k in sorted(c["files_by_outcome"])}
    return {"counts": c, "rows": rows, "outside": outside}


# ---------------------------------------------------------------- pronunciation
def decide(c):
    if c.get("unresolved_handles", 0) == 0:
        return V_NO_HANDLES
    if c.get("counted_key_sites_inside_handles", 0) == 0:
        return V_NO_KEYS
    if c.get("invisible_sites", 0) == 0:
        return V_ALL_SUBSCRIPT
    if c.get("files_published_without_a_key_but_carrying_an_invisible_one", 0) == 0:
        return V_INVISIBLE_OUTSIDE
    return V_INVISIBLE_INSIDE


def answer_of(c):
    return (
        "E647 published %s unresolved handles over %s files. %s of those files carry %s string "
        "constant(s) equal to a counted row key inside a handle: %s as a subscript slice (E652's "
        "second arm walks the whole tree for exactly that shape, so those keys are already counted "
        "there even when the row's boolean says otherwise) and %s in a role neither arm can see "
        "(%s). Against E652's published rows: %s of %s matched files carry a key in a handle, %s of "
        "them carry an invisible one, and the number of published files that say 'no key' while "
        "carrying an invisible one is %s -- so %s. The remaining %s file(s) with counted keys in "
        "handles were never priced at all because they do not spell a read module, and they hold %s "
        "invisible site(s). %s handle(s) could not be resolved back to a node and are published "
        "rather than dropped."
        % (c.get("unresolved_handles", 0), c.get("files_with_an_unresolved_handle", 0),
           c.get("files_with_a_counted_key_inside_a_handle", 0),
           c.get("counted_key_sites_inside_handles", 0),
           (c.get("counted_key_sites_inside_handles", 0) - c.get("invisible_sites", 0)),
           c.get("invisible_sites", 0),
           ", ".join("%s %s" % (k, v) for k, v in
                     sorted((c.get("invisible_by_role") or {}).items())),
           c.get("files_matched_to_an_e652_row", 0),
           c.get("files_matched_to_an_e652_row", 0),
           c.get("matched_files_carrying_an_invisible_site", 0),
           c.get("files_published_without_a_key_but_carrying_an_invisible_one", 0),
           ("no published E652 row moves" if not
            c.get("files_published_without_a_key_but_carrying_an_invisible_one", 0)
            else "published rows undercount the files they already price"),
           c.get("files_outside_e652s_published_population", 0),
           c.get("invisible_sites_outside_e652s_published_population", 0),
           c.get("unreadable_handles", 0)))


def face_from(m, e652_stamp=None):
    c = m["counts"]
    return {
        "study": STUDY,
        "source_face": SOURCE_FACE,
        "source_face_stamp": e652_stamp,
        "method": [
            "re-derive the counted read population E638 joins (module/line/key), and the corpus E652 "
            "walks, with the same 1MB read cap so both censuses skip the same files",
            "run E647's collect_strings unchanged; each published handle is resolved back to the node "
            "kind that produced it (percent_formatting -> BinOp, fstring_has_a_formatted_value -> "
            "JoinedStr, str_format -> Call) at its recorded (line, column)",
            "walk that node's own subtree (E647 stops at it) for string constants equal to a counted "
            "row key, and classify each site by the role its parent gives it",
            "the handle's span is the node's own lineno..end_lineno, not the enclosing statement: "
            "E647 publishes a start position and no span at all",
            "price every module that carries a counted key in a handle against E652's published row "
            "for that module (its boolean, its key list, its subscript count) and publish the "
            "classification; files with no E652 row are published separately",
        ],
        "answer": answer_of(c),
        "verdict": decide(c),
        "counts": c,
        "rows": m["rows"],
        "files_outside_e652s_published_population": m["outside"],
        "limitations": [
            "a subscript key is counted as visible to E652 because that arm walks the whole tree for "
            "Subscript nodes; the boolean is not, so the two fields in one E652 row can disagree and "
            "this face counts that disagreement instead of calling it a lost key",
            "'inside a handle' is decided by the node span, so a counted key in the same statement but "
            "outside the handle expression is not counted here",
            "the population is whatever e648.read_population() joins off this tree, so a stale "
            "population moves both the key set and the numerator together",
        ],
    }


def face_problems(face):
    problems = []
    c = face.get("counts") or {}
    rows = face.get("rows") or []
    outside = face.get("files_outside_e652s_published_population") or []
    sites = sum(r.get("counted_key_sites") or 0 for r in rows)
    outside_sites = sum(r.get("counted_key_sites") or 0 for r in outside)
    if sites + outside_sites != (c.get("counted_key_sites_inside_handles") or 0):
        problems.append("counted key sites do not re-add from rows (%d + %d vs %d)"
                        % (sites, outside_sites, c.get("counted_key_sites_inside_handles")))
    invisible = sum(r.get("invisible_sites") or 0 for r in rows) + \
        sum(r.get("invisible_sites") or 0 for r in outside)
    if invisible != (c.get("invisible_sites") or 0):
        problems.append("invisible sites do not re-add (%d vs %d)"
                        % (invisible, c.get("invisible_sites")))
    by_role = {}
    by_kind = {}
    for r in rows + outside:
        for h in (r.get("handles") or []):
            by_kind[h["kind"]] = by_kind.get(h["kind"], 0) + (h.get("counted_key_sites") or 0)
            for s in (h.get("counted_keys") or []):
                if s.get("role") not in ROLE_ORDER:
                    problems.append("role outside the frozen vocabulary: %r" % (s.get("role"),))
                by_role[s["role"]] = by_role.get(s["role"], 0) + 1
    for name, live in (("counted_key_sites_by_role", by_role),
                       ("counted_key_sites_by_kind", by_kind)):
        published = c.get(name) or {}
        for k in live:
            if k not in published:
                problems.append("%s publishes no bucket for the live role/kind %r" % (name, k))
    if not (c.get("elided_sites") or 0):
        live_invisible = sum((c.get("invisible_by_role") or {}).values())
        if live_invisible != (c.get("invisible_sites") or 0):
            problems.append("invisible_by_role sums to %d, not the %d invisible sites"
                            % (live_invisible, c.get("invisible_sites") or 0))
        live_arg = (c.get("invisible_by_role") or {}).get("call_argument", 0)
        live_callee = sum((c.get("invisible_by_callee") or {}).values())
        if live_arg and live_callee != live_arg:
            problems.append("invisible_by_callee sums to %d, not the %d call arguments"
                            % (live_callee, live_arg))
    if (c.get("files_with_handle_detail") or 0) + (c.get("files_with_handles_elided") or 0) != \
            (c.get("files_with_a_counted_key_inside_a_handle") or 0):
        problems.append("detail and elision do not add up to the files carrying a key")
    if (c.get("files_with_handle_detail") or 0) != len(rows) + \
            len([r for r in outside if r.get("handles")]):
        problems.append("the published detail count does not equal the rows that carry handles")
    if len(rows) != (c.get("files_matched_to_an_e652_row") or 0):
        problems.append("matched-file count does not equal the row count (%d vs %d)"
                        % (len(rows), c.get("files_matched_to_an_e652_row")))
    if len(outside) != (c.get("files_outside_e652s_published_population") or 0):
        problems.append("outside-population count does not equal its own list")
    if not (c.get("elided_sites") or 0) and not (c.get("elided_handles") or 0):
        live_invisible = sum((c.get("invisible_by_role") or {}).values())
        if live_invisible != (c.get("invisible_sites") or 0):
            problems.append("invisible_by_role sums to %d, not the %d invisible sites"
                            % (live_invisible, c.get("invisible_sites") or 0))
        live_arg = (c.get("invisible_by_role") or {}).get("call_argument", 0)
        live_callee = sum((c.get("invisible_by_callee") or {}).values())
        if live_arg and live_callee != live_arg:
            problems.append("invisible_by_callee sums to %d, not the %d call arguments"
                            % (live_callee, live_arg))
    for r in rows:
        cls = r.get("class") or ""
        if r.get("e652_carries_a_counted_row_key") is False and (r.get("invisible_sites") or 0) > 0 \
                and cls != "invisible_to_both_arms":
            problems.append("%r carries an invisible site but is classed %r" % (r.get("module"), cls))
            break
    if decide(c) != face.get("verdict"):
        problems.append("the published verdict is not the one its own counts force")
    if face.get("verdict") == V_NO_KEYS and sites + outside_sites:
        problems.append("the empty verdict is published with key sites")
    return problems


def write_face(out_dir, doc, face=FACE, latest=LATEST):
    os.makedirs(out_dir, exist_ok=True)
    for name in (face, latest):
        path = os.path.join(out_dir, name)
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
        say("run: %s" % os.path.relpath(path, ROOT))


def build(root=ROOT, out_dir=None):
    _rows, stamp = load_e652()
    doc = face_from(measure(root, e652_rows=_rows if _rows else None), stamp)
    write_face(out_dir or OUTDIR, doc)
    c = doc["counts"]
    say("run: handles=%d files_with_key_in_handle=%d sites=%d invisible=%d matched=%d outside=%d"
        % (c["unresolved_handles"], c["files_with_a_counted_key_inside_a_handle"],
           c["counted_key_sites_inside_handles"], c["invisible_sites"],
           c["files_matched_to_an_e652_row"],
           c["files_outside_e652s_published_population"]))
    say("run: verdict=" + doc["verdict"])
    say("run: answer=" + doc["answer"])
    return doc, []


# ---------------------------------------------------------------- selftest
def _fixture_root(files):
    import tempfile
    root = tempfile.mkdtemp(prefix="e657_")
    for name, body in files.items():
        path = os.path.join(root, name)
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)
    return root


KEYS = {"rows", "verdict"}


def _scan(body, keys=KEYS, name="m.py"):
    root = _fixture_root({name: body})
    got, why = scan_file(os.path.join(root, name), keys, root)
    assert why is None, why
    return got


def selftest():
    legs = []

    def leg(name, fn):
        try:
            fn()
            legs.append((name, True))
        except AssertionError as exc:
            legs.append((name, False))
            say("FAIL %s: %s" % (name, exc))

    def a_percent_handle_is_resolved_and_spanned():
        got = _scan('X = 1\nb = "%s" % (d["rows"],)\n')
        assert len(got["handles"]) == 1, got["handles"]
        h = got["handles"][0]
        assert h["kind"] == "percent_formatting", h
        assert h["span"] == [2, 2], h
        assert h["counted_key_sites"] == 1, h
        assert h["counted_keys"][0]["role"] == "subscript_key", h

    def an_fstring_value_is_a_handle():
        got = _scan('b = f"x {d[\'verdict\']} y"\n')
        assert [h["kind"] for h in got["handles"]] == ["fstring_with_a_value"], got["handles"]
        assert got["handles"][0]["counted_keys"][0]["role"] == "subscript_key", got["handles"]

    def a_str_format_handle_is_resolved():
        got = _scan('b = "{}".format(d["rows"])\n')
        assert [h["kind"] for h in got["handles"]] == ["str_format"], got["handles"]
        assert got["handles"][0]["counted_key_sites"] == 1, got["handles"]

    def a_dict_key_inside_a_handle_is_invisible():
        got = _scan('b = "%s" % ({"rows": 1},)\n')
        h = got["handles"][0]
        assert h["counted_keys"][0]["role"] == "dict_literal_key", h
        assert h["invisible_sites"] == 1, h

    def a_call_argument_inside_a_handle_is_invisible():
        got = _scan('b = "%s" % (check("rows"),)\n')
        h = got["handles"][0]
        assert h["counted_keys"][0]["role"] == "call_argument", h
        assert h["invisible_sites"] == 1, h

    def a_key_outside_the_handle_is_not_counted():
        got = _scan('b = "%s" % x\nd = {"rows": 1}\n')
        assert got["handles"] == [], got["handles"]
        assert got["subscript_key_sites_anywhere"] == 0, got

    def the_span_is_the_expressions_own_span():
        got = _scan('b = "%s%s" % (\n    d["rows"],\n    d["verdict"],\n)\n')
        assert got["handles"][0]["span"] == [1, 4], got["handles"][0]

    def a_key_beside_the_handle_in_the_same_statement_is_not_counted():
        got = _scan('def f():\n    return g("%s" % y,\n             d["rows"])\n')
        assert got["handles"] == [], got["handles"]

    def a_nested_handle_is_not_double_counted():
        got = _scan('b = "%s" % (f"{d[\'rows\']}",)\n')
        kinds = [h["kind"] for h in got["handles"]]
        assert kinds == ["percent_formatting"], kinds
        assert got["unresolved_handles"] == 1, got

    def an_unresolvable_handle_is_published_not_dropped():
        got = _scan('b = "%s" % d["rows"]  # a handle whose node e647 reports\n')
        assert got["unreadable_handles"] == 0, got
        # a why that no node kind maps to is counted, never silently zero
        assert e657_resolve_unknown_is_counted() >= 1

    def e657_resolve_unknown_is_counted():
        import ast as _ast
        entry = {"line": 1, "column": 0, "why": "no_such_why"}
        kind, node = _resolve_handle(entry, handle_nodes(_ast.parse('x = 1\n')))
        return 1 if (kind is None and node is None) else 0

    def a_file_without_handles_contributes_zero():
        got = _scan('a = {"rows": 1}\n')
        assert got["unresolved_handles"] == 0 and got["handles"] == [], got

    def e652_rows_classify_the_disagreement():
        here = {"counted_key_sites": 2, "invisible_sites": 0}
        row = {"carries_a_counted_row_key": False, "subscript_key_sites": 2}
        assert classify_against_e652(row, here) == "already_counted_by_e652s_subscript_arm"
        assert classify_against_e652(None, here) == "outside_e652s_published_population"
        assert classify_against_e652({"carries_a_counted_row_key": True,
                                      "subscript_key_sites": 0},
                                     {"counted_key_sites": 1, "invisible_sites": 1}) == \
            "invisible_to_both_arms"

    def the_decisions_are_forced_by_counts():
        assert decide({"unresolved_handles": 0}) == V_NO_HANDLES
        assert decide({"unresolved_handles": 5, "counted_key_sites_inside_handles": 0}) == V_NO_KEYS
        assert decide({"unresolved_handles": 5, "counted_key_sites_inside_handles": 3,
                       "invisible_sites": 0}) == V_ALL_SUBSCRIPT
        assert decide({"unresolved_handles": 5, "counted_key_sites_inside_handles": 3,
                       "invisible_sites": 1,
                       "files_published_without_a_key_but_carrying_an_invisible_one": 0}) == \
            V_INVISIBLE_OUTSIDE
        assert decide({"unresolved_handles": 5, "counted_key_sites_inside_handles": 3,
                       "invisible_sites": 1,
                       "files_published_without_a_key_but_carrying_an_invisible_one": 1}) == \
            V_INVISIBLE_INSIDE

    def a_callee_is_published_for_a_call_argument():
        got = _scan('b = "%s" % (d.get("rows"),)\n')
        site = got["handles"][0]["counted_keys"][0]
        assert site["role"] == "call_argument" and site["callee"] == "d.get", site

    def the_face_re_adds_from_its_own_rows():
        m = measure(_fixture_root({"m.py": 'b = "%s" % ({"rows": 1},)\n'}),
                    counted=[{"module": "m.py", "line": 1, "key": "rows", "function": "f",
                              "receiver": "d"}],
                    e652_rows={"m.py": {"carries_a_counted_row_key": False,
                                        "counted_keys_named": [], "subscript_key_sites": 0,
                                        "unresolved_strings": 1}})
        doc = face_from(m)
        assert face_problems(doc) == [], face_problems(doc)
        assert doc["verdict"] == V_INVISIBLE_INSIDE, doc["verdict"]

    def a_tampered_count_is_refused():
        m = measure(_fixture_root({"m.py": 'b = "%s" % d["rows"]\n'}),
                    counted=[{"module": "m.py", "line": 1, "key": "rows"}], e652_rows={})
        doc = face_from(m)
        doc["counts"]["counted_key_sites_inside_handles"] = 7
        assert any("re-add" in p for p in face_problems(doc)), face_problems(doc)

    def a_tampered_verdict_is_refused():
        m = measure(_fixture_root({"m.py": 'b = "%s" % d["rows"]\n'}),
                    counted=[{"module": "m.py", "line": 1, "key": "rows"}], e652_rows={})
        doc = face_from(m)
        doc["verdict"] = V_NO_KEYS
        assert any("verdict" in p for p in face_problems(doc)), face_problems(doc)

    def a_shared_key_list_is_used_verbatim():
        got = _scan('b = "%s" % d["not_a_counted_key"]\n')
        assert got["handles"] == [], got["handles"]

    leg("a percent handle is resolved and spanned", a_percent_handle_is_resolved_and_spanned)
    leg("an f-string value is a handle", an_fstring_value_is_a_handle)
    leg("a str.format handle is resolved", a_str_format_handle_is_resolved)
    leg("a dict key inside a handle is invisible", a_dict_key_inside_a_handle_is_invisible)
    leg("a call argument inside a handle is invisible",
        a_call_argument_inside_a_handle_is_invisible)
    leg("a key outside the handle is not counted", a_key_outside_the_handle_is_not_counted)
    leg("the span is the expression's own span", the_span_is_the_expressions_own_span)
    leg("a key beside the handle in the same statement is not counted",
        a_key_beside_the_handle_in_the_same_statement_is_not_counted)
    leg("a nested handle is not double counted", a_nested_handle_is_not_double_counted)
    leg("an unresolvable handle is published not dropped",
        an_unresolvable_handle_is_published_not_dropped)
    leg("a file without handles contributes zero", a_file_without_handles_contributes_zero)
    leg("e652 rows classify the disagreement", e652_rows_classify_the_disagreement)
    leg("the decisions are forced by counts", the_decisions_are_forced_by_counts)
    leg("a callee is published for a call argument", a_callee_is_published_for_a_call_argument)
    leg("the face re-adds from its own rows", the_face_re_adds_from_its_own_rows)
    leg("a tampered count is refused", a_tampered_count_is_refused)
    leg("a tampered verdict is refused", a_tampered_verdict_is_refused)
    leg("a key the population does not join is not counted", a_shared_key_list_is_used_verbatim)
    failed = [n for n, ok in legs if not ok]
    say("selftest: %d/%d green" % (len(legs) - len(failed), len(legs)))
    if failed:
        say("selftest: failing legs -> " + "; ".join(failed))
    return 0 if not failed else 1


# ---------------------------------------------------------------- CLI
def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run")
    args = ap.parse_args(argv[1:])
    cmd = args.cmd.lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "check":
        doc, problems = build(root=ROOT)
        problems = problems + face_problems(doc)
        say("problems=" + json.dumps(problems, ensure_ascii=False))
        return 0 if not problems else 1
    if cmd == "verify":
        path = os.path.join(OUTDIR, FACE)
        if not os.path.exists(path):
            say("no face at %s" % path)
            return 1
        doc = json.load(io.open(path, encoding="utf-8"))
        problems = face_problems(doc)
        say("problems=" + json.dumps(problems, ensure_ascii=False))
        return 0 if not problems else 1
    doc, problems = build(root=ROOT)
    problems = problems + face_problems(doc)
    if problems:
        say("PROBLEMS: " + "; ".join(problems))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
