"""E626 -- does the callee that is handed the object write the key the dead line read?

E625 (r1643) closed the value test for the same-object sibling reads and wrote its own hole into
``limits``: *f(m) could write anything, so the object being handed to a call leaves the value
undecided*.  One of its four same-object duplicate rows was published exactly that way
(``scripts/cn_core_ddctl_p1.py:367`` key ``days``, read again at 395, with ``P`` handed to
``build_dd_axis(P)`` at 372 and ``active_rebals(P)`` at 373).  This card follows that handover one
hop into the callee.

For every handover mark E625 published, the call at that line is resolved:

  the_callee_writes_the_key_on_its_parameter              the callee stores/dels/updates the key on
                                                          the parameter the object arrived in
  the_callee_writes_the_parameter_without_naming_the_key   update(payload) / param[k] with a
                                                          computed key: it may have written it
  the_callee_hands_the_parameter_on_again                 the parameter leaves on another call --
                                                          one hop is the stated bound
  the_callee_does_not_write_the_key_on_its_parameter      the callee only reads (or ignores) it
  the_callee_is_not_defined_in_this_module                an import: out of one-hop scope
  the_callee_is_an_attribute_call                         obj.method(m): the receiver decides
  no_call_of_the_handover_at_the_published_line           the mark and the AST disagree
  the_argument_position_is_out_of_the_callee_signature    *args / arity mismatch

A read whose every handover settles on "does not write" is a read of the same value again; a single
naming write settles it the other way; anything left open keeps the duplicate undecided.  The face
publishes the corrected survive/stored/undecided split beside E625's published one.

Population: E625's same-object sibling reads, re-derived by importing
``e625_sibling_read_value`` (its ``value_facts``, ``interval_nodes`` and ``write_marks`` are used, not
re-implemented) with E619's, E622's, E623's, E624's, E625's and this study's self-exclusion sets kept,
plus a cross-check that the re-derived rows still match the published E625 face row for row.

Deliberately NOT done: no interprocedural descent past one hop, no alias analysis, no class/attribute
resolution (an attribute call is published as out of scope, not guessed), no fixture write, no runner.

Deterministic, static, no network, no runner, no fixture write.
"""
import argparse
import ast
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-09"
FACE = "HANDOVERWRITE.json"
LATEST = "handoverwrite_latest.json"
STUDY = "E626_handover_write"
SELF_PARTS = {"e626_handover_write.py", "run_e626_smoke_leg.py", "_probe_e626.py"}

HANDOVER_CLASSES = [
    "the_callee_writes_the_key_on_its_parameter",
    "the_callee_writes_the_parameter_without_naming_the_key",
    "the_callee_hands_the_parameter_on_again",
    "the_callee_does_not_write_the_key_on_its_parameter",
    "the_callee_is_not_defined_in_this_module",
    "the_callee_is_an_attribute_call",
    "no_call_of_the_handover_at_the_published_line",
    "the_argument_position_is_out_of_the_callee_signature",
]
NAMED, UNNAMED_WRITE, HANDS_ON, NO_WRITE, NOT_IN_MODULE, ATTRIBUTE, NO_CALL, OUT_OF_SIGNATURE = \
    HANDOVER_CLASSES

READ_SETTLES_ON_SAME_VALUE = "the_read_settles_on_the_value_the_dead_line_saw"
READ_SETTLES_ON_A_DIFFERENT_VALUE = "the_read_settles_on_a_different_value"
READ_STAYS_UNDECIDED = "the_read_stays_undecided"
READ_CLASSES = [READ_SETTLES_ON_SAME_VALUE, READ_SETTLES_ON_A_DIFFERENT_VALUE, READ_STAYS_UNDECIDED]

DUPLICATE_SURVIVES = "duplicate_survives_the_one_hop_test"
DUPLICATE_STORED = "duplicate_is_stored_over"
DUPLICATE_UNDECIDED = "duplicate_stays_undecided"
DUPLICATE_CLASSES = [DUPLICATE_SURVIVES, DUPLICATE_STORED, DUPLICATE_UNDECIDED]

if HERE not in sys.path:
    sys.path.insert(0, HERE)
import e619_dead_reader_locals as e619                                              # noqa: E402
import e622_deadlocal_reach as e622                                                 # noqa: E402
import e623_deadline_key_use as e623                                                # noqa: E402
import e624_sibling_read_object as e624                                             # noqa: E402
import e625_sibling_read_value as e625                                              # noqa: E402


# ---------------------------------------------------------------- one hop
def module_functions(tree):
    """Module-level function defs by name (a name bound twice keeps the first, as Python does not)."""
    out = {}
    for n in tree.body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out.setdefault(n.name, n)
    return out


def calls_by_line(fn):
    """Call nodes of ``fn`` indexed by their own line, not descending into nested definitions."""
    nodes, _nested = e625.interval_nodes(fn, -1, 10 ** 9)
    out = {}
    for n in nodes:
        if isinstance(n, ast.Call):
            out.setdefault(n.lineno, []).append(n)
    return out


def resolve_handover(fn, recv_text, key, handover_line, funcs, calls=None):
    """Where the handed object goes and what the callee does to it at ``key``."""
    index = calls_by_line(fn) if calls is None else calls
    for c in index.get(handover_line) or []:
        pos = None
        for i, a in enumerate(c.args):
            if e624.text_of(a) == recv_text:
                pos = i
                break
        if pos is None:
            continue
        f = c.func
        if isinstance(f, ast.Attribute):
            return {"call_line": handover_line, "callee": e624.text_of(c.func),
                    "handover_class": ATTRIBUTE,
                    "why": "the call is a method on a receiver, whose body is not resolvable here"}
        if not isinstance(f, ast.Name):
            return {"call_line": handover_line,
                    "callee": e624.text_of(c.func) or "<unreadable expression>",
                    "handover_class": ATTRIBUTE,
                    "why": "the callee expression is not a plain name"}
        target = funcs.get(f.id)
        if target is None:
            return {"call_line": handover_line, "callee": f.id,
                    "handover_class": NOT_IN_MODULE,
                    "why": "no module-level def of that name in this file (an import or a global)"}
        params = [a.arg for a in target.args.args]
        if pos >= len(params):
            return {"call_line": handover_line, "callee": f.id,
                    "callee_def_line": target.lineno, "handover_class": OUT_OF_SIGNATURE,
                    "why": "argument %d falls outside the callee's %d positional parameter(s)"
                           % (pos, len(params))}
        param = params[pos]
        nodes, nested = e625.interval_nodes(target, -1, 10 ** 9)
        named, unnamed, handed = e625.write_marks(nodes, param, key, param)
        if named:
            cls = NAMED
        elif handed:
            cls = HANDS_ON
        elif unnamed:
            cls = UNNAMED_WRITE
        else:
            cls = NO_WRITE
        return {"call_line": handover_line, "callee": f.id,
                "callee_def_line": target.lineno, "parameter": param,
                "handover_class": cls,
                "writes_naming_the_key": named,
                "writes_without_naming_the_key": unnamed,
                "hands_the_parameter_on": handed,
                "nested_definitions_in_the_callee": nested}
    return {"call_line": handover_line, "callee": None, "handover_class": NO_CALL,
            "why": "no call carrying the receiver as an argument sits on that line"}


def read_class(resolutions):
    """What one handover-bearing read settles on."""
    if not resolutions:
        return READ_STAYS_UNDECIDED
    classes = [r["handover_class"] for r in resolutions]
    if NAMED in classes:
        return READ_SETTLES_ON_A_DIFFERENT_VALUE
    if any(c != NO_WRITE for c in classes):
        return READ_STAYS_UNDECIDED
    return READ_SETTLES_ON_SAME_VALUE


def duplicate_class(effective):
    """The duplicate-level split: survives on any same-value read, else stored or still open."""
    if not effective:
        return None
    if READ_SETTLES_ON_SAME_VALUE in effective:
        return DUPLICATE_SURVIVES
    if READ_SETTLES_ON_A_DIFFERENT_VALUE in effective:
        return DUPLICATE_STORED
    return DUPLICATE_UNDECIDED


# ---------------------------------------------------------------- rows with one-hop facts
def handover_facts(tree, stem, graph):
    """E625's rows for one module, each handover-bearing same-object read extended one hop."""
    rows, inert = e625.value_facts(tree, stem, graph)
    funcs = module_functions(tree)
    for r in rows:
        fn = e623.innermost(graph["fns"], r)
        if fn is None:
            continue
        index = calls_by_line(fn)
        same = [s for s in (r.get("sibling_reads") or []) if s.get("same_object")]
        for s in same:
            marks = s.get("handovers_to_a_call") or []
            if s.get("value_class") != e625.VALUE_CLASSES[2] or not marks:
                s["read_class_after_one_hop"] = (
                    READ_SETTLES_ON_A_DIFFERENT_VALUE
                    if s.get("value_class") == e625.VALUE_CLASSES[0]
                    else READ_SETTLES_ON_SAME_VALUE
                    if s.get("value_class") == e625.UNCHANGED
                    else READ_STAYS_UNDECIDED)
                s["handover_resolution"] = []
                continue
            recv = s.get("sibling_receiver") or s.get("receiver")
            s["handover_resolution"] = [
                resolve_handover(fn, recv, r["key"], m["line"], funcs, index) for m in marks]
            s["read_class_after_one_hop"] = read_class(s["handover_resolution"])
        effective = [s["read_class_after_one_hop"] for s in same]
        r["read_classes_after_one_hop"] = effective
        r["duplicate_class_after_one_hop"] = (
            duplicate_class(effective)
            if (r.get("corrected_class") == e624.CORRECTED[0]
                and r.get("sibling_read_reads_the_same_object_after_the_dead_line")) else None)
    return rows, inert


def measure(root=ROOT):
    mods, skipped = e619.population(root)
    skip = (set(e622.SELF_PARTS) | set(e623.SELF_PARTS) | set(e624.SELF_PARTS)
            | set(e625.SELF_PARTS) | set(SELF_PARTS))
    keep = [(rel, tree) for rel, tree in mods if os.path.basename(rel) not in skip]
    lines, inert = [], 0
    for rel, tree in keep:
        stem = os.path.basename(rel)[:-3]
        graph = e622.call_graph(tree, stem)
        rows, inert_here = handover_facts(tree, stem, graph)
        for r in rows:
            r["module"] = rel
        lines.extend(rows)
        inert += inert_here
    lines.sort(key=lambda r: (r["module"], r["line"]))
    return {"population_modules": len(keep), "skipped": skipped, "lines": lines,
            "inert_dead_facekey_lines": inert,
            "cross_check": e625_cross_check(root, lines)}


# ---------------------------------------------------------------- cross-check
def e625_cross_check(root, lines):
    """Diff the re-derived rows against the face E625 published (row for row)."""
    out = {"published": False, "agrees": None}
    path = os.path.join(root, "results", "state_tilt", "siblingreadvalue_latest.json")
    if not os.path.exists(path):
        out["note"] = "no published E625 face on disk"
        return out
    pub = json.load(io.open(path, encoding="utf-8"))
    key = lambda r: (r.get("module"), r.get("function"), r.get("def_line"), r.get("line"))
    published = {key(r): r for r in (pub.get("lines") or [])}
    mine = {key(r): r for r in lines}
    moved = sorted(k for k in set(mine) & set(published)
                   if mine[k].get("corrected_class") != published[k].get("corrected_class"))
    vc_moved = sorted(k for k in set(mine) & set(published)
                      if sorted(mine[k].get("value_classes_of_the_same_object_reads") or [])
                      != sorted(published[k].get("value_classes_of_the_same_object_reads") or []))
    published_undecided = (pub.get("counts") or {}).get(
        "same_object_duplicates_left_undecided")
    out.update({
        "published": True,
        "published_lines": len(published),
        "rederived_lines": len(mine),
        "lines_whose_class_differs_n": len(moved),
        "lines_whose_class_differs": [list(k) for k in moved[:10]],
        "lines_whose_value_classes_differ_n": len(vc_moved),
        "lines_whose_value_classes_differ": [list(k) for k in vc_moved[:10]],
        "lines_only_here": [list(k) for k in sorted(set(mine) - set(published))][:10],
        "lines_only_in_the_published_face":
            [list(k) for k in sorted(set(published) - set(mine))][:10],
        "published_undecided_duplicates": published_undecided,
        "agrees": not moved and not vc_moved and not (set(published) - set(mine)),
    })
    return out


# ---------------------------------------------------------------- counts / verdict
def _duplicates(lines):
    return [r for r in lines
            if r.get("corrected_class") == e624.CORRECTED[0]
            and r.get("sibling_read_reads_the_same_object_after_the_dead_line")]


def _leaving_a_handover(dup):
    """The duplicates whose value test E625 left open because the object went into a call."""
    return [r for r in dup
            if any(s.get("value_class") == e625.VALUE_CLASSES[2] and s.get("handovers_to_a_call")
                   for s in (r.get("sibling_reads") or []) if s.get("same_object"))]


def counts_of(m):
    lines = m["lines"]
    hc = {k: 0 for k in HANDOVER_CLASSES}
    rc = {k: 0 for k in READ_CLASSES}
    instances = 0
    for r in lines:
        for s in (r.get("sibling_reads") or []):
            if not s.get("same_object"):
                continue
            for h in (s.get("handover_resolution") or []):
                instances += 1
                hc[h.get("handover_class")] = hc.get(h.get("handover_class"), 0) + 1
            cls = s.get("read_class_after_one_hop")
            if s.get("value_class") == e625.VALUE_CLASSES[2] and s.get("handovers_to_a_call"):
                rc[cls] = rc.get(cls, 0) + 1
    dup = _duplicates(lines)
    dc = {k: 0 for k in DUPLICATE_CLASSES}
    for r in dup:
        got = r.get("duplicate_class_after_one_hop")
        if got in dc:
            dc[got] += 1
    leaving = _leaving_a_handover(dup)
    lc = {k: 0 for k in DUPLICATE_CLASSES}
    for r in leaving:
        got = r.get("duplicate_class_after_one_hop")
        if got in lc:
            lc[got] += 1
    c = {
        "population_modules": m["population_modules"],
        "skipped_modules": len(m["skipped"]),
        "live_dead_facekey_lines": len(lines),
        "inert_dead_facekey_lines": m["inert_dead_facekey_lines"],
        "same_object_duplicate_rows": len(dup),
        "handover_instances": instances,
        "same_object_reads_left_on_a_handover": sum(rc.values()),
        "duplicate_rows_leaving_a_handover": len(leaving),
        "duplicates_leaving_a_handover_that_settle_to_survive": lc[DUPLICATE_SURVIVES],
        "duplicates_leaving_a_handover_that_settle_to_stored": lc[DUPLICATE_STORED],
        "duplicates_leaving_a_handover_that_stay_undecided": lc[DUPLICATE_UNDECIDED],
        "duplicates_that_survive_the_one_hop_test": dc[DUPLICATE_SURVIVES],
        "duplicates_stored_over_after_one_hop": dc[DUPLICATE_STORED],
        "duplicates_still_undecided_after_one_hop": dc[DUPLICATE_UNDECIDED],
    }
    for k in HANDOVER_CLASSES:
        c["handover_" + k] = hc[k]
    for k in READ_CLASSES:
        c["read_" + k] = rc[k]
    return c


def derive_verdict(m):
    c = counts_of(m)
    if c["population_modules"] == 0:
        return "no_face_publishers_in_the_population"
    if c["live_dead_facekey_lines"] == 0:
        return "no_live_dead_facekey_line_in_the_population"
    if c["handover_instances"] == 0:
        return "no_same_object_read_is_left_undecided_by_a_handover"
    total = c["duplicate_rows_leaving_a_handover"]
    if total == 0:
        return ("the_%d_handovers_leave_no_duplicate_undecided" % c["handover_instances"])
    open_n = c["duplicates_leaving_a_handover_that_stay_undecided"]
    if open_n == 0:
        n = c["duplicates_leaving_a_handover_that_settle_to_survive"]
        if n == total:
            return ("all_%d_duplicate_reads_left_undecided_by_a_handover_settle_to_the_value_the_dead_"
                    "line_saw" % total)
        if n == 0:
            return ("none_of_the_%d_duplicate_reads_left_undecided_by_a_handover_keeps_the_value_the_"
                    "dead_line_saw" % total)
        return ("%d_of_the_%d_duplicate_reads_left_undecided_by_a_handover_settle_to_the_value_the_dead_"
                "line_saw" % (n, total))
    return ("%d_of_the_%d_duplicate_reads_left_undecided_by_a_handover_stay_undecided_after_one_hop"
            % (open_n, total))


def answer_of(m):
    c = counts_of(m)
    if c["handover_instances"] == 0:
        return "E625 left no same-object read undecided by a handover, so this card has no handover to follow"
    return ("E625 published %d duplicate row(s) with a handover and %d handover instance(s).  Following "
            "each one hop: %d callee(s) write the key on the parameter (%d naming it, %d not), %d hand "
            "the parameter on again, %d do not write it at all, %d are not defined in this module, %d "
            "are attribute calls, %d have no call on the published line and %d fall outside the "
            "callee's signature.  Of the %d duplicate row(s) that leave a handover, %d settle to the "
            "value the dead line saw, %d settle to a different value and %d stay undecided; the whole "
            "same-object set now stands at %d survive / %d stored / %d undecided"
            % (c["duplicate_rows_leaving_a_handover"], c["handover_instances"],
               c["handover_" + NAMED] + c["handover_" + UNNAMED_WRITE],
               c["handover_" + NAMED], c["handover_" + UNNAMED_WRITE],
               c["handover_" + HANDS_ON], c["handover_" + NO_WRITE],
               c["handover_" + NOT_IN_MODULE], c["handover_" + ATTRIBUTE],
               c["handover_" + NO_CALL], c["handover_" + OUT_OF_SIGNATURE],
               c["duplicate_rows_leaving_a_handover"],
               c["duplicates_leaving_a_handover_that_settle_to_survive"],
               c["duplicates_leaving_a_handover_that_settle_to_stored"],
               c["duplicates_leaving_a_handover_that_stay_undecided"],
               c["duplicates_that_survive_the_one_hop_test"],
               c["duplicates_stored_over_after_one_hop"],
               c["duplicates_still_undecided_after_one_hop"]))


# ---------------------------------------------------------------- face problems
def face_problems(face):
    p = []
    if not isinstance(face, dict) or "counts" not in face:
        return ["the face carries no counts block"]
    counts = face["counts"]
    lines = face.get("lines") or []
    if counts.get("live_dead_facekey_lines") != len(lines):
        p.append("counts.live_dead_facekey_lines says %r but the face publishes %d lines"
                 % (counts.get("live_dead_facekey_lines"), len(lines)))
    hc = {k: 0 for k in HANDOVER_CLASSES}
    rc = {k: 0 for k in READ_CLASSES}
    instances = 0
    for r in lines:
        same = [s for s in (r.get("sibling_reads") or []) if s.get("same_object")]
        for s in same:
            res = s.get("handover_resolution") or []
            marks = s.get("handovers_to_a_call") or []
            on_handover = s.get("value_class") == e625.VALUE_CLASSES[2]
            if on_handover and marks:
                if len(res) != len(marks):
                    p.append("line %r in %r publishes %d resolution(s) for %d handover mark(s)"
                             % (r.get("line"), r.get("function"), len(res), len(marks)))
                want = read_class(res)
                if s.get("read_class_after_one_hop") != want:
                    p.append("line %r in %r says the read settles as %r against its own resolutions "
                             "(%r)" % (r.get("line"), r.get("function"),
                                       s.get("read_class_after_one_hop"), want))
            elif res:
                p.append("line %r in %r publishes handover resolutions without a handover"
                         % (r.get("line"), r.get("function")))
            for h in res:
                instances += 1
                cls = h.get("handover_class")
                if cls not in HANDOVER_CLASSES:
                    p.append("line %r in %r carries handover_class=%r"
                             % (r.get("line"), r.get("function"), cls))
                    continue
                hc[cls] += 1
                if cls == NAMED and not h.get("writes_naming_the_key"):
                    p.append("line %r in %r says the callee writes the key with no naming write "
                             "published" % (r.get("line"), r.get("function")))
                if cls == UNNAMED_WRITE and (
                        h.get("writes_naming_the_key") or not h.get("writes_without_naming_the_key")):
                    p.append("line %r in %r says an unnamed callee write without that shape"
                             % (r.get("line"), r.get("function")))
                if cls == HANDS_ON and not h.get("hands_the_parameter_on"):
                    p.append("line %r in %r says the callee hands the parameter on with no such mark"
                             % (r.get("line"), r.get("function")))
                if cls == NO_WRITE and (h.get("writes_naming_the_key")
                                        or h.get("writes_without_naming_the_key")
                                        or h.get("hands_the_parameter_on")):
                    p.append("line %r in %r says the callee does not write the key yet publishes "
                             "write marks" % (r.get("line"), r.get("function")))
            if on_handover and marks:
                rc[s["read_class_after_one_hop"]] += 1
        dup = (r.get("corrected_class") == e624.CORRECTED[0]
               and r.get("sibling_read_reads_the_same_object_after_the_dead_line"))
        if dup:
            want = duplicate_class([s.get("read_class_after_one_hop") for s in same])
            if r.get("duplicate_class_after_one_hop") != want:
                p.append("line %r in %r publishes duplicate_class_after_one_hop=%r against its own "
                         "reads (%r)" % (r.get("line"), r.get("function"),
                                         r.get("duplicate_class_after_one_hop"), want))
        elif r.get("duplicate_class_after_one_hop") is not None:
            p.append("line %r in %r publishes a duplicate class on a non-duplicate row"
                     % (r.get("line"), r.get("function")))
    if counts.get("handover_instances") != instances:
        p.append("counts.handover_instances does not re-derive from the rows")
    for k in HANDOVER_CLASSES:
        if counts.get("handover_" + k) != hc[k]:
            p.append("counts.handover_%s does not re-derive from the rows" % k)
    if sum(hc.values()) != instances:
        p.append("the handover classes do not add up to the instance count")
    for k in READ_CLASSES:
        if counts.get("read_" + k) != rc[k]:
            p.append("counts.read_%s does not re-derive from the rows" % k)
    dup = _duplicates(lines)
    if counts.get("same_object_duplicate_rows") != len(dup):
        p.append("counts.same_object_duplicate_rows does not re-derive")
    split = (counts.get("duplicates_that_survive_the_one_hop_test", 0)
             + counts.get("duplicates_stored_over_after_one_hop", 0)
             + counts.get("duplicates_still_undecided_after_one_hop", 0))
    if split != len(dup):
        p.append("the survive/stored/undecided split does not add up to the duplicate count")
    leaving = _leaving_a_handover(dup)
    if counts.get("duplicate_rows_leaving_a_handover") != len(leaving):
        p.append("counts.duplicate_rows_leaving_a_handover does not re-derive")
    for k, field in ((DUPLICATE_SURVIVES, "duplicates_leaving_a_handover_that_settle_to_survive"),
                     (DUPLICATE_STORED, "duplicates_leaving_a_handover_that_settle_to_stored"),
                     (DUPLICATE_UNDECIDED, "duplicates_leaving_a_handover_that_stay_undecided")):
        want = sum(1 for r in leaving if r.get("duplicate_class_after_one_hop") == k)
        if counts.get(field) != want:
            p.append("counts.%s does not re-derive from the rows that leave a handover" % field)
    cc = face.get("e625_cross_check") or {}
    if cc.get("published"):
        if cc.get("agrees") is False:
            p.append("the re-derived E625 population no longer matches the published face (%r rows "
                     "differ, %r value-class lists differ)"
                     % (cc.get("lines_whose_class_differs_n"),
                        cc.get("lines_whose_value_classes_differ_n")))
        if cc.get("rederived_lines") != counts.get("live_dead_facekey_lines"):
            p.append("the E625 cross-check re-derived %r lines but the counts say %r"
                     % (cc.get("rederived_lines"), counts.get("live_dead_facekey_lines")))
    derived = derive_verdict({"population_modules": counts.get("population_modules"),
                              "lines": lines,
                              "inert_dead_facekey_lines": counts.get("inert_dead_facekey_lines"),
                              "skipped": [None] * (counts.get("skipped_modules") or 0)})
    if face.get("verdict") != derived:
        p.append("the published verdict %r is not what the line rows force (%r)"
                 % (face.get("verdict"), derived))
    return p


def face_from(m):
    face = {
        "study": STUDY,
        "script": "scripts/e626_handover_write.py",
        "evidence_cutoff": TODAY,
        "dept": "research+engineering",
        "method": ("take every handover mark E625 published on a same-object sibling read "
                   "(importing its value facts, not re-implementing them) and follow the call one "
                   "hop into a module-level callee: does the callee write the key on the parameter "
                   "the object arrived in (named / unnamed), hand it on, or not touch it"),
        "population_source": ("scripts/*.py (AST) via e619.population, E625's handover marks over "
                              "E624's same-object sibling reads, less the E619/E622/E623/E624/E625/"
                              "this study self-exclusion sets"),
        "counts": counts_of(m),
        "e625_cross_check": m.get("cross_check") or {"published": False},
        "lines": m["lines"],
        "skipped": m["skipped"],
        "limits": [
            "one hop only: a parameter handed on again is published as undecided, not followed",
            "no alias analysis: a write through another name bound to the same object is invisible",
            "no class or attribute resolution: obj.method(m) is published as out of scope, and a "
            "same-named method in another class is not guessed at",
            "no default-argument or keyword-position analysis: the positional argument that carries "
            "the receiver decides which parameter is watched",
            "a write inside a nested def of the callee that is called in its body is not descended "
            "into; callees with nested definitions publish those lines",
            "the population is the one E625 published; this study excludes itself and its smoke leg "
            "and probe and keeps E619's, E622's, E623's, E624's and E625's self-exclusion sets",
        ],
        "verdict": derive_verdict(m),
        "answer": answer_of(m),
    }
    return face, face_problems(face)


def build(root=ROOT):
    return face_from(measure(root=root))


def write_face(out_dir, doc, face=FACE, latest=LATEST):
    os.makedirs(out_dir, exist_ok=True)
    for name in (face, latest):
        with io.open(os.path.join(out_dir, name), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=1, sort_keys=False)
            fh.write("\n")
    return os.path.join(out_dir, face)


# ---------------------------------------------------------------- selftest
FIXTURE = '''
import io, json


def writes_named(m):
    m["counts"] = 2


def writes_named_via_update(m):
    m.update({"counts": 5})


def writes_named_via_pop(m):
    m.pop("counts", None)


def writes_unnamed(m, payload):
    m.update(payload)


def writes_unnamed_at_computed_key(m, k):
    m[k] = 7


def hands_on(m, fixer):
    fixer(m)


def reads_only(m):
    return m["counts"]


def ignores_it(m):
    return None


def handed_named(m):
    face = {"counts": 1, "x": None}
    seen = []
    first = m["counts"]
    writes_named(m)
    seen.append(m["counts"])
    json.dump(face, io.open("x", "w"))
    return seen


def handed_update_named(m):
    face = {"counts": 1, "x": None}
    seen = []
    first = m["counts"]
    writes_named_via_update(m)
    seen.append(m["counts"])
    json.dump(face, io.open("x", "w"))
    return seen


def handed_pop_named(m):
    face = {"counts": 1, "x": None}
    seen = []
    first = m["counts"]
    writes_named_via_pop(m)
    seen.append(m.get("counts"))
    json.dump(face, io.open("x", "w"))
    return seen


def handed_unnamed(m, payload):
    face = {"counts": 1, "x": None}
    seen = []
    first = m["counts"]
    writes_unnamed(m, payload)
    seen.append(m["counts"])
    json.dump(face, io.open("x", "w"))
    return seen


def handed_computed(m, k):
    face = {"counts": 1, "x": None}
    seen = []
    first = m["counts"]
    writes_unnamed_at_computed_key(m, k)
    seen.append(m["counts"])
    json.dump(face, io.open("x", "w"))
    return seen


def handed_reads_only(m):
    face = {"counts": 1, "x": None}
    seen = []
    first = m["counts"]
    reads_only(m)
    seen.append(m["counts"])
    json.dump(face, io.open("x", "w"))
    return seen


def handed_ignored(m):
    face = {"counts": 1, "x": None}
    seen = []
    first = m["counts"]
    ignores_it(m)
    seen.append(m["counts"])
    json.dump(face, io.open("x", "w"))
    return seen


def handed_on(m):
    face = {"counts": 1, "x": None}
    seen = []
    first = m["counts"]
    hands_on(m, reads_only)
    seen.append(m["counts"])
    json.dump(face, io.open("x", "w"))
    return seen


def handed_outside(m):
    face = {"counts": 1, "x": None}
    seen = []
    first = m["counts"]
    external_fixer(m)
    seen.append(m["counts"])
    json.dump(face, io.open("x", "w"))
    return seen


def handed_attribute(m):
    face = {"counts": 1, "x": None}
    seen = []
    first = m["counts"]
    box.fix(m)
    seen.append(m["counts"])
    json.dump(face, io.open("x", "w"))
    return seen


handed_named({"counts": 1})
handed_update_named({"counts": 1})
handed_pop_named({"counts": 1})
handed_unnamed({"counts": 1}, {"counts": 9})
handed_computed({"counts": 1}, "counts")
handed_reads_only({"counts": 1})
handed_ignored({"counts": 1})
handed_on({"counts": 1})
handed_outside({"counts": 1})
handed_attribute({"counts": 1})
'''


def selftest():
    legs = []
    tree = ast.parse(FIXTURE)
    graph = e622.call_graph(tree, "fixture")
    rows, inert = handover_facts(tree, "fixture", graph)
    by = {r["function"]: r for r in rows}

    def cls_of(fn_name):
        r = by.get(fn_name) or {}
        same = [s for s in (r.get("sibling_reads") or []) if s.get("same_object")]
        return same[0]["handover_resolution"][0]["handover_class"] if same else None

    def dup_of(fn_name):
        return (by.get(fn_name) or {}).get("duplicate_class_after_one_hop")

    legs.append(("the fixture yields live dead face-key lines", len(rows) >= 10 and inert == 0))
    legs.append(("a callee storing at the key is a naming write",
                 cls_of("handed_named") == NAMED))
    legs.append(("a callee updating with a literal key is a naming write",
                 cls_of("handed_update_named") == NAMED))
    legs.append(("a callee popping the key is a naming write",
                 cls_of("handed_pop_named") == NAMED))
    legs.append(("a callee updating with an unreadable payload is an unnamed write",
                 cls_of("handed_unnamed") == UNNAMED_WRITE))
    legs.append(("a callee storing at a computed key is an unnamed write",
                 cls_of("handed_computed") == UNNAMED_WRITE))
    legs.append(("a callee that only reads the key does not write it",
                 cls_of("handed_reads_only") == NO_WRITE))
    legs.append(("a callee that ignores the parameter does not write the key",
                 cls_of("handed_ignored") == NO_WRITE))
    legs.append(("a callee that hands the parameter on stays open",
                 cls_of("handed_on") == HANDS_ON))
    legs.append(("a callee outside this module stays open",
                 cls_of("handed_outside") == NOT_IN_MODULE))
    legs.append(("an attribute call stays open", cls_of("handed_attribute") == ATTRIBUTE))
    legs.append(("a naming callee stores the duplicate over", dup_of("handed_named") == DUPLICATE_STORED))
    legs.append(("a reading callee lets the duplicate survive",
                 dup_of("handed_reads_only") == DUPLICATE_SURVIVES))
    legs.append(("an ignoring callee lets the duplicate survive",
                 dup_of("handed_ignored") == DUPLICATE_SURVIVES))
    legs.append(("a handed-on callee keeps the duplicate undecided",
                 dup_of("handed_on") == DUPLICATE_UNDECIDED))
    legs.append(("an unnamed callee write keeps the duplicate undecided",
                 dup_of("handed_unnamed") == DUPLICATE_UNDECIDED))
    legs.append(("an outside callee keeps the duplicate undecided",
                 dup_of("handed_outside") == DUPLICATE_UNDECIDED))
    legs.append(("an attribute callee keeps the duplicate undecided",
                 dup_of("handed_attribute") == DUPLICATE_UNDECIDED))

    for r in rows:
        r["module"] = "scripts/fixture.py"
        r["reach"] = r.get("reach") or "called_from_module_level"
    m = {"population_modules": 1, "skipped": [], "lines": rows,
         "inert_dead_facekey_lines": inert}
    c = counts_of(m)
    legs.append(("counts re-add the line rows", c["live_dead_facekey_lines"] == len(rows)))
    legs.append(("the handover classes add up to the instance count",
                 sum(c["handover_" + k] for k in HANDOVER_CLASSES) == c["handover_instances"]))
    legs.append(("the duplicate split adds up",
                 c["duplicates_that_survive_the_one_hop_test"]
                 + c["duplicates_stored_over_after_one_hop"]
                 + c["duplicates_still_undecided_after_one_hop"]
                 == c["same_object_duplicate_rows"]))
    legs.append(("the handover-leaving split adds up to the handover duplicate count",
                 c["duplicates_leaving_a_handover_that_settle_to_survive"]
                 + c["duplicates_leaving_a_handover_that_settle_to_stored"]
                 + c["duplicates_leaving_a_handover_that_stay_undecided"]
                 == c["duplicate_rows_leaving_a_handover"]))
    face, problems = face_from(m)
    legs.append(("the fixture face has no problems", problems == []))
    bad = {"counts": dict(face["counts"]), "lines": [dict(r) for r in face["lines"]],
           "verdict": face["verdict"], "e625_cross_check": face["e625_cross_check"]}
    bad["counts"]["handover_" + NAMED] = int(bad["counts"]["handover_" + NAMED]) + 1
    legs.append(("a perturbed handover count fails face_problems", face_problems(bad) != []))
    bad2 = {"counts": dict(face["counts"]), "lines": [dict(r) for r in face["lines"]],
            "verdict": "other", "e625_cross_check": face["e625_cross_check"]}
    legs.append(("a perturbed verdict fails face_problems", face_problems(bad2) != []))
    bad3 = {"counts": dict(face["counts"]), "lines": [dict(r) for r in face["lines"]][:-1],
            "verdict": face["verdict"], "e625_cross_check": face["e625_cross_check"]}
    legs.append(("a dropped line row fails face_problems", face_problems(bad3) != []))
    flipped = [dict(r) for r in face["lines"]]
    done = False
    for r in flipped:
        for s in (r.get("sibling_reads") or []):
            if s.get("same_object") and (s.get("handover_resolution") or []):
                s["handover_resolution"] = [dict(s["handover_resolution"][0],
                                                 handover_class=NO_WRITE,
                                                 writes_naming_the_key=[],
                                                 writes_without_naming_the_key=[],
                                                 hands_the_parameter_on=[])]
                s["read_class_after_one_hop"] = READ_SETTLES_ON_SAME_VALUE
                done = True
                break
        if done:
            break
    bad4 = {"counts": dict(face["counts"]), "lines": flipped, "verdict": face["verdict"],
            "e625_cross_check": face["e625_cross_check"]}
    legs.append(("a handover silently republished as no-write fails face_problems",
                 face_problems(bad4) != []))

    mods, _skipped = e619.population(ROOT)
    kept = [os.path.basename(rel) for rel, _ in mods
            if os.path.basename(rel) not in (set(e622.SELF_PARTS) | set(e623.SELF_PARTS)
                                             | set(e624.SELF_PARTS) | set(e625.SELF_PARTS)
                                             | set(SELF_PARTS))]
    legs.append(("the real population parses and is non-empty", len(mods) > 100))
    legs.append(("this script excludes itself", "e626_handover_write.py" not in kept))
    real = measure(root=ROOT)
    cc = real["cross_check"]
    legs.append(("the E625 cross-check read a published face", cc.get("published") is True))
    legs.append(("the re-derived rows are the ones E625 published", cc.get("agrees") is True))
    face2, problems2 = face_from(real)
    legs.append(("the built face has no problems", problems2 == []))

    failed = [n for n, ok in legs if not ok]
    for name, ok in legs:
        print(("PASS" if ok else "FAIL") + " :: " + name)
    print("%d/%d selftest legs" % (len(legs) - len(failed), len(legs)))
    return 0 if not failed else 1


# ---------------------------------------------------------------- CLI
def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="build")
    args = ap.parse_args(argv[1:])
    cmd = args.cmd.lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "check":
        face, problems = build(root=ROOT)
        print("problems=" + json.dumps(problems, ensure_ascii=False))
        return 0 if not problems else 1
    if cmd == "verify":
        path = os.path.join(OUTDIR, FACE)
        if not os.path.exists(path):
            print("no face at %s" % path)
            return 1
        doc = json.load(io.open(path, encoding="utf-8"))
        problems = face_problems(doc)
        print("problems=" + json.dumps(problems, ensure_ascii=False))
        return 0 if not problems else 1
    face, problems = build(root=ROOT)
    if cmd in ("build", "run"):
        path = write_face(OUTDIR, face)
        print("face:", path)
    if problems:
        print("PROBLEMS: " + "; ".join(problems))
        return 1
    c = face["counts"]
    print("population=%d lines=%d duplicates=%d handovers=%d reads_on_handover=%d survive=%d "
          "stored=%d undecided=%d"
          % (c["population_modules"], c["live_dead_facekey_lines"],
             c["same_object_duplicate_rows"], c["handover_instances"],
             c["same_object_reads_left_on_a_handover"],
             c["duplicates_that_survive_the_one_hop_test"],
             c["duplicates_stored_over_after_one_hop"],
             c["duplicates_still_undecided_after_one_hop"]))
    for k in HANDOVER_CLASSES:
        print("  %s=%d" % (k, c["handover_" + k]))
    print("verdict=" + face["verdict"])
    print("answer=" + face["answer"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))