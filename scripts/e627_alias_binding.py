"""E627 -- is the object a dead face-key line reads also bound to another local name?

E625 (r1643) closed the same-object value test and E626 (r1644) followed its one remaining handover
into the callee.  Both published the same hole: *no alias analysis, so a write through another name
bound to the same dict is invisible*.  This card closes that hole for the interval between the dead
face-key read and its sibling read, and then asks whether the hole contained anything.

For each live dead face-key line, every second name bound in the interval is classified:

  a_second_name_is_bound_to_the_same_object            alias = recv, alias = a_previous_alias
  a_second_name_is_bound_to_a_value_of_the_receiver    alias = recv.get(k) / recv[k] / recv.pop(k)
  a_second_name_is_bound_to_the_receivers_items        for a in recv.items()/keys()/values()
  a_second_name_is_bound_to_a_copy_of_the_receiver     alias = recv.copy()  (a different dict)
  a_second_name_is_bound_to_something_else             anything else

Only the first form shares the dict, so only it can hide a write at the key.  For each same-object
alias name the same write marks E625 uses (store/del/update/setdefault/pop/clear, plus handover to a
call) are re-run with the alias as the receiver, restricted to lines after the alias is bound and
after the dead line -- a write through the alias is exactly what neither E625 nor E626 can see.

Row class:

  the_alias_scan_stores_the_duplicate_over        a same-object alias is written at the key
  the_alias_scan_leaves_the_duplicate_undecided   an alias is handed to a call, or written at a
                                                  computed key
  the_alias_scan_has_nothing_to_say               no alias, or aliases that never write

The face publishes the per-line alias bindings, the corrected survive/stored/undecided split (E626's
class overridden by alias evidence) and a cross-check that the re-derived rows are still the ones
E626 published.

Deliberately NOT done: no alias bound before the function body that holds the dead line (a module
level name), no rebinding through a container or a comprehension, no attribute/class resolution, no
interprocedural descent, no fixture write, no runner.

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
FACE = "ALIASBINDING.json"
LATEST = "aliasbinding_latest.json"
STUDY = "E627_alias_binding"
SELF_PARTS = {"e627_alias_binding.py", "run_e627_smoke_leg.py", "_probe_e627.py"}

ALIAS_CLASSES = [
    "a_second_name_is_bound_to_the_same_object",
    "a_second_name_is_bound_to_a_value_of_the_receiver",
    "a_second_name_is_bound_to_the_receivers_items",
    "a_second_name_is_bound_to_a_copy_of_the_receiver",
    "a_second_name_is_bound_to_something_else",
]
SAME_OBJECT, A_VALUE, THE_ITEMS, A_COPY, SOMETHING_ELSE = ALIAS_CLASSES

SCAN_STORES_OVER = "the_alias_scan_stores_the_duplicate_over"
SCAN_UNDECIDED = "the_alias_scan_leaves_the_duplicate_undecided"
SCAN_NOTHING = "the_alias_scan_has_nothing_to_say"
SCAN_CLASSES = [SCAN_STORES_OVER, SCAN_UNDECIDED, SCAN_NOTHING]

if HERE not in sys.path:
    sys.path.insert(0, HERE)
import e619_dead_reader_locals as e619                                              # noqa: E402
import e622_deadlocal_reach as e622                                                 # noqa: E402
import e623_deadline_key_use as e623                                                # noqa: E402
import e624_sibling_read_object as e624                                             # noqa: E402
import e625_sibling_read_value as e625                                              # noqa: E402
import e626_handover_write as e626                                                  # noqa: E402


# ---------------------------------------------------------------- binding classification
def _method_of(expr, recv):
    """The attribute name when ``expr`` is ``recv.<attr>(...)``, else None."""
    if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Attribute):
        if e624.text_of(expr.func.value) == recv:
            return expr.func.attr
    return None


def binding_class(expr, same_names):
    """What a second local name is bound to, in the vocabulary this study publishes."""
    if isinstance(expr, ast.Name) and expr.id in same_names:
        return SAME_OBJECT
    if isinstance(expr, ast.Subscript) and e624.text_of(expr.value) in same_names:
        return A_VALUE
    if isinstance(expr, ast.Call):
        for recv in same_names:
            attr = _method_of(expr, recv)
            if attr in ("get", "pop", "setdefault"):
                return A_VALUE
            if attr in ("items", "keys", "values"):
                return THE_ITEMS
            if attr == "copy":
                return A_COPY
    return SOMETHING_ELSE


def iter_class(expr, same_names):
    """What a ``for`` target is bound to over that iterable."""
    inner = expr
    if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Name) \
            and expr.func.id in ("list", "tuple", "sorted") and expr.args:
        inner = expr.args[0]
    if isinstance(inner, ast.Name) and inner.id in same_names:
        return THE_ITEMS          # iterating a dict yields its keys
    if isinstance(inner, ast.Call):
        for recv in same_names:
            attr = _method_of(inner, recv)
            if attr in ("items", "keys", "values"):
                return THE_ITEMS
    return SOMETHING_ELSE


# ---------------------------------------------------------------- alias scan
def scan_aliases(nodes, recv_text, key, dead_line, sibling_line):
    """Second names bound in the interval, and what each same-object alias does at ``key``."""
    same = {recv_text}
    bindings = []
    windows = {}                       # alias -> (start_line, end_line or None)
    order = sorted(nodes, key=lambda n: (getattr(n, "lineno", 0), getattr(n, "col_offset", 0)))
    for n in order:
        line = getattr(n, "lineno", 0)
        if line > sibling_line:
            continue
        if isinstance(n, ast.Assign) and len(n.targets) == 1 \
                and isinstance(n.targets[0], ast.Name):
            alias, expr = n.targets[0].id, n.value
            cls = binding_class(expr, same)
            bindings.append({"line": line, "alias": alias, "form": "assignment",
                             "binds": e624.text_of(expr), "alias_class": cls,
                             "in_the_interval": dead_line < line <= sibling_line})
            if cls == SAME_OBJECT:
                same.add(alias)
                windows[alias] = (line, None)
            elif alias in windows:
                windows[alias] = (windows[alias][0], line)     # rebound: the window closes here
            continue
        if isinstance(n, ast.For):
            cls = iter_class(n.iter, same)
            names = [t.id for t in ast.walk(n.target) if isinstance(t, ast.Name)]
            bindings.append({"line": line, "alias": names, "form": "for_target",
                             "binds": e624.text_of(n.iter), "alias_class": cls,
                             "in_the_interval": dead_line < line <= sibling_line})
            if cls == SAME_OBJECT:
                for a in names:
                    same.add(a)
                    windows[a] = (line, None)
            continue
    named, unnamed, handed = [], [], []
    for alias in sorted(same - {recv_text}):
        start, end = windows.get(alias, (dead_line, None))
        w_named, w_unnamed, w_handed = e625.write_marks(order, alias, key, alias)
        lo = max(start, dead_line)
        for mark, bucket in ((w_named, named), (w_unnamed, unnamed), (w_handed, handed)):
            for m in mark:
                if lo <= m["line"] and (end is None or m["line"] < end):
                    bucket.append({"line": m["line"], "alias": alias, "form": m["form"]})
    return {"alias_bindings": bindings,
            "same_object_alias_names": sorted(same - {recv_text}),
            "alias_writes_naming_the_key": named,
            "alias_writes_without_naming_the_key": unnamed,
            "alias_handovers_to_a_call": handed}


def scan_class(scan):
    if scan["alias_writes_naming_the_key"]:
        return SCAN_STORES_OVER
    if scan["alias_writes_without_naming_the_key"] or scan["alias_handovers_to_a_call"]:
        return SCAN_UNDECIDED
    return SCAN_NOTHING


# ---------------------------------------------------------------- rows with alias facts
def alias_facts(tree, stem, graph):
    """E626's rows for one module, each same-object read extended with the alias scan."""
    rows, inert = e626.handover_facts(tree, stem, graph)
    for r in rows:
        fn = e623.innermost(graph["fns"], r)
        if fn is None:
            continue
        hi = max([r["line"]] + [s.get("line") or r["line"]
                                for s in (r.get("sibling_reads") or [])])
        nodes, _nested = e625.interval_nodes(fn, -1, hi)
        for s in (r.get("sibling_reads") or []):
            if not s.get("same_object"):
                continue
            recv = s.get("sibling_receiver") or s.get("receiver")
            scan = scan_aliases(nodes, recv, r["key"], r["line"], s.get("line") or r["line"])
            s.update(scan)
            s["alias_scan_class"] = scan_class(scan)
        same = [s for s in (r.get("sibling_reads") or []) if s.get("same_object")]
        r["same_object_alias_bindings"] = sum(
            1 for s in same for b in (s.get("alias_bindings") or []) if b.get("in_the_interval"))
        r["same_object_alias_names"] = sorted(
            {a for s in same for a in (s.get("same_object_alias_names") or [])})
        r["duplicate_class_after_the_alias_scan"] = final_class(r, same)
    return rows, inert


def final_class(r, same):
    """E626's duplicate class, overridden wherever an alias says more."""
    if not (r.get("corrected_class") == e624.CORRECTED[0]
            and r.get("sibling_read_reads_the_same_object_after_the_dead_line")):
        return None
    base = r.get("duplicate_class_after_one_hop")
    scans = [s.get("alias_scan_class") for s in same]
    if base == e626.DUPLICATE_STORED or SCAN_STORES_OVER in scans:
        return e626.DUPLICATE_STORED
    if base == e626.DUPLICATE_UNDECIDED or SCAN_UNDECIDED in scans:
        return e626.DUPLICATE_UNDECIDED
    if base == e626.DUPLICATE_SURVIVES:
        return e626.DUPLICATE_SURVIVES
    return None


def measure(root=ROOT):
    mods, skipped = e619.population(root)
    skip = (set(e622.SELF_PARTS) | set(e623.SELF_PARTS) | set(e624.SELF_PARTS)
            | set(e625.SELF_PARTS) | set(e626.SELF_PARTS) | set(SELF_PARTS))
    keep = [(rel, tree) for rel, tree in mods if os.path.basename(rel) not in skip]
    lines, inert = [], 0
    for rel, tree in keep:
        stem = os.path.basename(rel)[:-3]
        graph = e622.call_graph(tree, stem)
        rows, inert_here = alias_facts(tree, stem, graph)
        for r in rows:
            r["module"] = rel
        lines.extend(rows)
        inert += inert_here
    lines.sort(key=lambda r: (r["module"], r["line"]))
    return {"population_modules": len(keep), "skipped": skipped, "lines": lines,
            "inert_dead_facekey_lines": inert,
            "cross_check": e626_cross_check(root, lines)}


# ---------------------------------------------------------------- cross-check
def e626_cross_check(root, lines):
    """Diff the re-derived rows against the face E626 published (row for row)."""
    out = {"published": False, "agrees": None}
    path = os.path.join(root, "results", "state_tilt", "handoverwrite_latest.json")
    if not os.path.exists(path):
        out["note"] = "no published E626 face on disk"
        return out
    pub = json.load(io.open(path, encoding="utf-8"))
    key = lambda r: (r.get("module"), r.get("function"), r.get("def_line"), r.get("line"))
    published = {key(r): r for r in (pub.get("lines") or [])}
    mine = {key(r): r for r in lines}
    moved = sorted(k for k in set(mine) & set(published)
                   if mine[k].get("duplicate_class_after_one_hop")
                   != published[k].get("duplicate_class_after_one_hop"))
    out.update({
        "published": True,
        "published_lines": len(published),
        "rederived_lines": len(mine),
        "lines_whose_class_differs_n": len(moved),
        "lines_whose_class_differs": [list(k) for k in moved[:10]],
        "lines_only_here": [list(k) for k in sorted(set(mine) - set(published))][:10],
        "lines_only_in_the_published_face":
            [list(k) for k in sorted(set(published) - set(mine))][:10],
        "published_split": {k: (pub.get("counts") or {}).get(k) for k in
                            ("duplicates_that_survive_the_one_hop_test",
                             "duplicates_stored_over_after_one_hop",
                             "duplicates_still_undecided_after_one_hop")},
        "agrees": not moved and not (set(published) - set(mine)),
    })
    return out


# ---------------------------------------------------------------- counts / verdict
def _duplicates(lines):
    return [r for r in lines
            if r.get("corrected_class") == e624.CORRECTED[0]
            and r.get("sibling_read_reads_the_same_object_after_the_dead_line")]


def counts_of(m):
    lines = m["lines"]
    ac = {k: 0 for k in ALIAS_CLASSES}
    sc = {k: 0 for k in SCAN_CLASSES}
    instances = 0
    out_of_interval = 0
    for r in lines:
        for s in (r.get("sibling_reads") or []):
            if not s.get("same_object"):
                continue
            for b in (s.get("alias_bindings") or []):
                if not b.get("in_the_interval"):
                    out_of_interval += 1
                    continue
                instances += 1
                ac[b.get("alias_class")] = ac.get(b.get("alias_class"), 0) + 1
            sc[s.get("alias_scan_class")] = sc.get(s.get("alias_scan_class"), 0) + 1
    dup = _duplicates(lines)
    final = {k: 0 for k in e626.DUPLICATE_CLASSES}
    for r in dup:
        got = r.get("duplicate_class_after_the_alias_scan")
        if got in final:
            final[got] += 1
    with_alias = [r for r in dup if r.get("same_object_alias_names")]
    closed = [r for r in dup
              if any(s.get("alias_scan_class") == SCAN_STORES_OVER
                     for s in (r.get("sibling_reads") or []) if s.get("same_object"))]
    c = {
        "population_modules": m["population_modules"],
        "skipped_modules": len(m["skipped"]),
        "live_dead_facekey_lines": len(lines),
        "inert_dead_facekey_lines": m["inert_dead_facekey_lines"],
        "same_object_duplicate_rows": len(dup),
        "alias_binding_instances": instances,
        "alias_bindings_outside_the_interval": out_of_interval,
        "same_object_alias_bindings": ac[SAME_OBJECT],
        "duplicate_rows_with_a_same_object_alias": len(with_alias),
        "duplicate_rows_the_alias_scan_can_close": len(closed),
        "duplicates_surviving_after_the_alias_scan": final[e626.DUPLICATE_SURVIVES],
        "duplicates_stored_over_after_the_alias_scan": final[e626.DUPLICATE_STORED],
        "duplicates_still_undecided_after_the_alias_scan": final[e626.DUPLICATE_UNDECIDED],
        "duplicates_surviving_the_one_hop_test": sum(
            1 for r in dup if r.get("duplicate_class_after_one_hop") == e626.DUPLICATE_SURVIVES),
        "duplicates_stored_over_after_one_hop": sum(
            1 for r in dup if r.get("duplicate_class_after_one_hop") == e626.DUPLICATE_STORED),
        "duplicates_still_undecided_after_one_hop": sum(
            1 for r in dup if r.get("duplicate_class_after_one_hop") == e626.DUPLICATE_UNDECIDED),
    }
    for k in ALIAS_CLASSES:
        c["alias_" + k] = ac[k]
    for k in SCAN_CLASSES:
        c["scan_" + k] = sc[k]
    return c


def derive_verdict(m):
    c = counts_of(m)
    if c["population_modules"] == 0:
        return "no_face_publishers_in_the_population"
    if c["live_dead_facekey_lines"] == 0:
        return "no_live_dead_facekey_line_in_the_population"
    n = c["same_object_duplicate_rows"]
    if n == 0:
        return "no_same_object_duplicate_row_left_to_test_for_an_alias"
    if c["same_object_alias_bindings"] == 0:
        return ("no_second_name_is_bound_to_the_receiver_in_any_of_the_%d_duplicate_intervals" % n)
    if c["duplicate_rows_the_alias_scan_can_close"] == 0:
        return ("the_%d_second_name(s)_bound_to_the_receiver_write_no_key_so_the_one_hop_split_"
                "stands" % c["same_object_alias_bindings"])
    k = c["duplicate_rows_the_alias_scan_can_close"]
    return ("%d_of_the_%d_duplicate_reads_left_open_are_written_through_a_second_name_bound_to_the_"
            "same_object" % (k, n))


def answer_of(m):
    c = counts_of(m)
    if c["same_object_duplicate_rows"] == 0:
        return "E626 left no same-object duplicate row, so there is no interval to scan for an alias"
    return ("Over %d live dead face-key line(s) and %d same-object duplicate row(s) this study finds "
            "%d second-name binding(s): %d to the same object, %d to a value of the receiver, %d to "
            "its items or keys and %d to something else.  %d duplicate row(s) carry a same-object "
            "alias; %d of them are written at the key through that alias.  The corrected split is "
            "%d survive / %d stored / %d undecided (E626 published %d / %d / %d)"
            % (c["live_dead_facekey_lines"], c["same_object_duplicate_rows"],
               c["alias_binding_instances"], c["alias_" + SAME_OBJECT], c["alias_" + A_VALUE],
               c["alias_" + THE_ITEMS], c["alias_" + SOMETHING_ELSE] + c["alias_" + A_COPY],
               c["duplicate_rows_with_a_same_object_alias"],
               c["duplicate_rows_the_alias_scan_can_close"],
               c["duplicates_surviving_after_the_alias_scan"],
               c["duplicates_stored_over_after_the_alias_scan"],
               c["duplicates_still_undecided_after_the_alias_scan"],
               c["duplicates_surviving_the_one_hop_test"],
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
    ac = {k: 0 for k in ALIAS_CLASSES}
    sc = {k: 0 for k in SCAN_CLASSES}
    instances = 0
    out_of_interval = 0
    for r in lines:
        same = [s for s in (r.get("sibling_reads") or []) if s.get("same_object")]
        for s in same:
            binds = s.get("alias_bindings") or []
            for b in binds:
                if not b.get("in_the_interval"):
                    out_of_interval += 1
                    continue
                instances += 1
                cls = b.get("alias_class")
                if cls not in ALIAS_CLASSES:
                    p.append("line %r in %r carries alias_class=%r"
                             % (r.get("line"), r.get("function"), cls))
                    continue
                ac[cls] += 1
            want = scan_class({
                "alias_writes_naming_the_key": s.get("alias_writes_naming_the_key") or [],
                "alias_writes_without_naming_the_key":
                    s.get("alias_writes_without_naming_the_key") or [],
                "alias_handovers_to_a_call": s.get("alias_handovers_to_a_call") or []})
            if s.get("alias_scan_class") != want:
                p.append("line %r in %r says the alias scan settles as %r against its own marks "
                         "(%r)" % (r.get("line"), r.get("function"),
                                   s.get("alias_scan_class"), want))
            sc[want] += 1
            named = s.get("alias_writes_naming_the_key") or []
            aliases = set(s.get("same_object_alias_names") or [])
            for m in named:
                if m.get("alias") not in aliases:
                    p.append("line %r in %r publishes a write through %r, which is not a bound "
                             "same-object alias" % (r.get("line"), r.get("function"),
                                                    m.get("alias")))
        if s and r.get("same_object_alias_names") is not None:
            want_names = sorted({a for s2 in same for a in (s2.get("same_object_alias_names") or [])})
            if sorted(r.get("same_object_alias_names") or []) != want_names:
                p.append("line %r in %r does not publish the union of its reads' alias names"
                         % (r.get("line"), r.get("function")))
        if r.get("same_object_alias_bindings") is not None:
            want_n = sum(1 for s in same for b in (s.get("alias_bindings") or [])
                         if b.get("in_the_interval"))
            if r.get("same_object_alias_bindings") != want_n:
                p.append("line %r in %r publishes %r alias binding(s) against %d in its reads"
                         % (r.get("line"), r.get("function"),
                            r.get("same_object_alias_bindings"), want_n))
        want_cls = final_class(r, same)
        if r.get("duplicate_class_after_the_alias_scan") != want_cls:
            p.append("line %r in %r publishes duplicate_class_after_the_alias_scan=%r against its "
                     "own reads (%r)" % (r.get("line"), r.get("function"),
                                         r.get("duplicate_class_after_the_alias_scan"), want_cls))
    if counts.get("alias_binding_instances") != instances:
        p.append("counts.alias_binding_instances does not re-derive from the rows")
    if counts.get("alias_bindings_outside_the_interval") != out_of_interval:
        p.append("counts.alias_bindings_outside_the_interval does not re-derive from the rows")
    for k in ALIAS_CLASSES:
        if counts.get("alias_" + k) != ac[k]:
            p.append("counts.alias_%s does not re-derive from the rows" % k)
    if sum(ac.values()) != instances:
        p.append("the alias classes do not add up to the instance count")
    for k in SCAN_CLASSES:
        if counts.get("scan_" + k) != sc[k]:
            p.append("counts.scan_%s does not re-derive from the rows" % k)
    dup = _duplicates(lines)
    if counts.get("same_object_duplicate_rows") != len(dup):
        p.append("counts.same_object_duplicate_rows does not re-derive")
    split = (counts.get("duplicates_surviving_after_the_alias_scan", 0)
             + counts.get("duplicates_stored_over_after_the_alias_scan", 0)
             + counts.get("duplicates_still_undecided_after_the_alias_scan", 0))
    if split != len(dup):
        p.append("the corrected split does not add up to the duplicate count")
    with_alias = sum(1 for r in dup if r.get("same_object_alias_names"))
    if counts.get("duplicate_rows_with_a_same_object_alias") != with_alias:
        p.append("counts.duplicate_rows_with_a_same_object_alias does not re-derive")
    closed = sum(1 for r in dup
                 if any(s.get("alias_scan_class") == SCAN_STORES_OVER
                        for s in (r.get("sibling_reads") or []) if s.get("same_object")))
    if counts.get("duplicate_rows_the_alias_scan_can_close") != closed:
        p.append("counts.duplicate_rows_the_alias_scan_can_close does not re-derive")
    cc = face.get("e626_cross_check") or {}
    if cc.get("published"):
        if cc.get("agrees") is False:
            p.append("the re-derived E626 population no longer matches the published face "
                     "(%r rows differ)" % cc.get("lines_whose_class_differs_n"))
        if cc.get("rederived_lines") != counts.get("live_dead_facekey_lines"):
            p.append("the E626 cross-check re-derived %r lines but the counts say %r"
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
        "script": "scripts/e627_alias_binding.py",
        "evidence_cutoff": TODAY,
        "dept": "research+engineering",
        "method": ("over every same-object sibling read E626 published, classify each second local "
                   "name bound in the interval and re-run E625's write marks with that name as the "
                   "receiver: a write through an alias bound to the same dict is the one form the "
                   "key/object/value stack could not see"),
        "population_source": ("scripts/*.py (AST) via e619.population, E626's one-hop rows over "
                              "E625's value facts over E624's same-object reads, less the "
                              "E619/E622/E623/E624/E625/E626/this study self-exclusion sets"),
        "counts": counts_of(m),
        "e626_cross_check": m.get("cross_check") or {"published": False},
        "lines": m["lines"],
        "skipped": m["skipped"],
        "limits": [
            "only names bound inside the function that holds the dead line: a module-level or "
            "package-level alias of the receiver is out of scope",
            "no rebinding through a container, a comprehension, an attribute or a return value: only "
            "a plain `alias = recv` (and chains of those) shares the dict",
            "a value obtained from the dict (get/pop/setdefault/subscript) is published as a value "
            "binding, and mutating that value is not a write at a key",
            "an alias handed to a call is published as undecided, not followed further",
            "a copy of the dict is another object; writes through it are not writes to the receiver",
            "no interprocedural descent and no class/attribute resolution",
            "the population is the one E626 published; this study excludes itself, its smoke leg "
            "and its probe, and keeps every earlier study's self-exclusion set",
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


def reads_only(m):
    return m["counts"]


def writes_named(m):
    m["counts"] = 2


def plain_two_reads(m):
    face = {"counts": 1, "x": None}
    seen = []
    first = m["counts"]
    seen.append(m["counts"])
    json.dump(face, io.open("x", "w"))
    return seen


def alias_named(m):
    face = {"counts": 1, "x": None}
    seen = []
    first = m["counts"]
    alias = m
    alias["counts"] = 3
    seen.append(m["counts"])
    json.dump(face, io.open("x", "w"))
    return seen


def alias_named_via_update(m):
    face = {"counts": 1, "x": None}
    seen = []
    first = m["counts"]
    alias = m
    alias.update({"counts": 4})
    seen.append(m["counts"])
    json.dump(face, io.open("x", "w"))
    return seen


def alias_chain_named(m):
    face = {"counts": 1, "x": None}
    seen = []
    first = m["counts"]
    alias = m
    second = alias
    second["counts"] = 5
    seen.append(m["counts"])
    json.dump(face, io.open("x", "w"))
    return seen


def alias_unnamed(m, payload):
    face = {"counts": 1, "x": None}
    seen = []
    first = m["counts"]
    alias = m
    alias.update(payload)
    seen.append(m["counts"])
    json.dump(face, io.open("x", "w"))
    return seen


def alias_reads_only(m):
    face = {"counts": 1, "x": None}
    seen = []
    first = m["counts"]
    alias = m
    reads_only(alias)
    seen.append(m["counts"])
    json.dump(face, io.open("x", "w"))
    return seen


def alias_value_binding(m):
    face = {"counts": 1, "x": None}
    seen = []
    first = m["counts"]
    value = m.get("counts")
    seen.append(m["counts"])
    json.dump(face, io.open("x", "w"))
    return seen


def alias_items_binding(m):
    face = {"counts": 1, "x": None}
    seen = []
    first = m["counts"]
    for k, v in m.items():
        pass
    seen.append(m["counts"])
    json.dump(face, io.open("x", "w"))
    return seen


def alias_copy_binding(m):
    face = {"counts": 1, "x": None}
    seen = []
    first = m["counts"]
    other = m.copy()
    other["counts"] = 6
    seen.append(m["counts"])
    json.dump(face, io.open("x", "w"))
    return seen


def alias_rebound_then_written(m, other):
    face = {"counts": 1, "x": None}
    seen = []
    first = m["counts"]
    alias = m
    alias = other
    alias["counts"] = 7
    seen.append(m["counts"])
    json.dump(face, io.open("x", "w"))
    return seen


plain_two_reads({"counts": 1})
alias_named({"counts": 1})
alias_named_via_update({"counts": 1})
alias_chain_named({"counts": 1})
alias_unnamed({"counts": 1}, {"counts": 9})
alias_reads_only({"counts": 1})
alias_value_binding({"counts": 1})
alias_items_binding({"counts": 1})
alias_copy_binding({"counts": 1})
alias_rebound_then_written({"counts": 1}, {"counts": 2})
'''


def selftest():
    legs = []
    tree = ast.parse(FIXTURE)
    graph = e622.call_graph(tree, "fixture")
    rows, inert = alias_facts(tree, "fixture", graph)

    def rows_of(fn_name):
        return [r for r in rows if r["function"] == fn_name]

    def same_of(fn_name):
        return [s for r in rows_of(fn_name)
                for s in (r.get("sibling_reads") or []) if s.get("same_object")]

    def scans_of(fn_name):
        return {s.get("alias_scan_class") for s in same_of(fn_name)}

    def binds_of(fn_name):
        return [b.get("alias_class") for s in same_of(fn_name)
                for b in (s.get("alias_bindings") or []) if b.get("in_the_interval")]

    def dup_classes_of(fn_name):
        return {r.get("duplicate_class_after_the_alias_scan") for r in rows_of(fn_name)}

    legs.append(("the fixture yields live dead face-key lines", len(rows) >= 9 and inert == 0))
    legs.append(("a name bound to the receiver is the same object",
                 binds_of("alias_named") == [SAME_OBJECT]))
    legs.append(("a write through that alias stores the duplicate over",
                 scans_of("alias_named") == {SCAN_STORES_OVER}
                 and dup_classes_of("alias_named") == {e626.DUPLICATE_STORED}))
    legs.append(("a named update through the alias also stores it over",
                 dup_classes_of("alias_named_via_update") == {e626.DUPLICATE_STORED}))
    legs.append(("an alias chained off another alias keeps the same object",
                 dup_classes_of("alias_chain_named") == {e626.DUPLICATE_STORED}))
    legs.append(("an unnamed write through the alias leaves it undecided",
                 dup_classes_of("alias_unnamed") == {e626.DUPLICATE_UNDECIDED}))
    legs.append(("an alias handed to a call leaves it undecided",
                 scans_of("alias_reads_only") == {SCAN_UNDECIDED}
                 and dup_classes_of("alias_reads_only") == {e626.DUPLICATE_UNDECIDED}))
    legs.append(("a value of the receiver is not the receiver",
                 binds_of("alias_value_binding") == [A_VALUE]
                 and scans_of("alias_value_binding") == {SCAN_NOTHING}))
    legs.append(("iterating the items binds the items, not the receiver",
                 binds_of("alias_items_binding") == [THE_ITEMS]
                 and scans_of("alias_items_binding") == {SCAN_NOTHING}))
    legs.append(("a copy of the receiver is a different object",
                 binds_of("alias_copy_binding") == [A_COPY]
                 and scans_of("alias_copy_binding") == {SCAN_NOTHING}
                 and dup_classes_of("alias_copy_binding") == {e626.DUPLICATE_SURVIVES}))
    legs.append(("a rebinding closes the alias window before the write",
                 scans_of("alias_rebound_then_written") == {SCAN_NOTHING}))
    legs.append(("a row with no alias anywhere has nothing for the scan to say",
                 binds_of("plain_two_reads") == []
                 and scans_of("plain_two_reads") == {SCAN_NOTHING}
                 and dup_classes_of("plain_two_reads") == {e626.DUPLICATE_SURVIVES}))

    for r in rows:
        r["module"] = "scripts/fixture.py"
    m = {"population_modules": 1, "skipped": [], "lines": rows,
         "inert_dead_facekey_lines": inert}
    c = counts_of(m)
    legs.append(("counts re-add the line rows", c["live_dead_facekey_lines"] == len(rows)))
    legs.append(("the alias classes add up to the instance count",
                 sum(c["alias_" + k] for k in ALIAS_CLASSES) == c["alias_binding_instances"]))
    legs.append(("the corrected split adds up",
                 c["duplicates_surviving_after_the_alias_scan"]
                 + c["duplicates_stored_over_after_the_alias_scan"]
                 + c["duplicates_still_undecided_after_the_alias_scan"]
                 == c["same_object_duplicate_rows"]))
    legs.append(("the alias scan closes exactly the rows it stores over",
                 c["duplicate_rows_the_alias_scan_can_close"]
                 == c["duplicates_stored_over_after_the_alias_scan"]
                 and c["duplicate_rows_the_alias_scan_can_close"] >= 3))
    face, problems = face_from(m)
    legs.append(("the fixture face has no problems", problems == []))
    bad = {"counts": dict(face["counts"]), "lines": [dict(r) for r in face["lines"]],
           "verdict": face["verdict"], "e626_cross_check": face["e626_cross_check"]}
    bad["counts"]["alias_" + SAME_OBJECT] = int(bad["counts"]["alias_" + SAME_OBJECT]) + 1
    legs.append(("a perturbed alias count fails face_problems", face_problems(bad) != []))
    bad2 = {"counts": dict(face["counts"]), "lines": [dict(r) for r in face["lines"]],
            "verdict": "other", "e626_cross_check": face["e626_cross_check"]}
    legs.append(("a perturbed verdict fails face_problems", face_problems(bad2) != []))
    bad3 = {"counts": dict(face["counts"]), "lines": [dict(r) for r in face["lines"]][:-1],
            "verdict": face["verdict"], "e626_cross_check": face["e626_cross_check"]}
    legs.append(("a dropped line row fails face_problems", face_problems(bad3) != []))
    flipped = [dict(r) for r in face["lines"]]
    done = False
    for r in flipped:
        for s in (r.get("sibling_reads") or []):
            if s.get("same_object") and s.get("alias_writes_naming_the_key"):
                s["alias_writes_naming_the_key"] = []
                s["alias_scan_class"] = SCAN_NOTHING
                done = True
                break
        if done:
            break
    bad4 = {"counts": dict(face["counts"]), "lines": flipped, "verdict": face["verdict"],
            "e626_cross_check": face["e626_cross_check"]}
    legs.append(("an alias write silently dropped fails face_problems", face_problems(bad4) != []))

    mods, _skipped = e619.population(ROOT)
    kept = [os.path.basename(rel) for rel, _ in mods
            if os.path.basename(rel) not in (set(e622.SELF_PARTS) | set(e623.SELF_PARTS)
                                             | set(e624.SELF_PARTS) | set(e625.SELF_PARTS)
                                             | set(e626.SELF_PARTS) | set(SELF_PARTS))]
    legs.append(("the real population parses and is non-empty", len(mods) > 100))
    legs.append(("this script excludes itself", "e627_alias_binding.py" not in kept))
    real = measure(root=ROOT)
    cc = real["cross_check"]
    legs.append(("the E626 cross-check read a published face", cc.get("published") is True))
    legs.append(("the re-derived rows are the ones E626 published", cc.get("agrees") is True))
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
    print("population=%d lines=%d duplicates=%d aliases=%d same_object_aliases=%d "
          "rows_with_alias=%d closed=%d survive=%d stored=%d undecided=%d"
          % (c["population_modules"], c["live_dead_facekey_lines"],
             c["same_object_duplicate_rows"], c["alias_binding_instances"],
             c["same_object_alias_bindings"], c["duplicate_rows_with_a_same_object_alias"],
             c["duplicate_rows_the_alias_scan_can_close"],
             c["duplicates_surviving_after_the_alias_scan"],
             c["duplicates_stored_over_after_the_alias_scan"],
             c["duplicates_still_undecided_after_the_alias_scan"]))
    for k in ALIAS_CLASSES:
        print("  %s=%d" % (k, c["alias_" + k]))
    print("verdict=" + face["verdict"])
    print("answer=" + face["answer"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))