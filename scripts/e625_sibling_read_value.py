"""E625 -- does the sibling read see the VALUE the dead line saw?

E624 (r1642) closed under object identity and wrote its own hole into ``limits``: *a mutation of the
object is not a rebinding of the name -- m["k"] read twice with m["k"] = ... in between still counts
as the same object*.  Object identity is the weakest of the three tests (key, object, value); this
card prices the third one.

For every sibling read E624 accepted as reading the SAME object, the interval between the two lines
is scanned for a write to that object at that key:

  the_key_is_stored_between_the_two_lines                    m["k"] = ..., del m["k"], m |= {"k":...}
  the_object_is_written_without_the_key_being_named           m.update(payload), m.clear(),
                                                              m[k2] = ... with a computed key
  the_object_is_handed_to_a_call_between_the_two_lines        f(m) -- invisible, so undecidable
  the_key_is_not_stored_between_the_two_lines                 nothing touches it: same value

Only the last class lets a sibling read be called a re-read of the value the dead line produced.  A
named store makes it a different value even though it is the same dict; the two middle classes are
published as undecidable rather than guessed either way.

Population: E624's published line rows, re-derived by importing ``e624_sibling_read_object`` (its
``object_facts``, ``text_of``, ``receiver_of`` and ``SAME`` are used, not re-implemented), with
E619's, E622's, E623's, E624's and this study's self-exclusion sets kept, and a cross-check that the
re-derived rows still match the published E624 face line for line and corrected class for class.

Deliberately NOT done: no alias analysis and no value tracing -- a write through an alias name is
invisible, a nested def that is called between the lines is not descended into, and a call that is
handed the object could write anything.  Every row carries the interval's write marks so a reader can
check any row by eye against the 34-line population.

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
FACE = "SIBLINGREADVALUE-%s.json" % TODAY
LATEST = "siblingreadvalue_latest.json"
STUDY = "E625_sibling_read_value"
SELF_PARTS = {"e625_sibling_read_value.py", "run_e625_smoke_leg.py", "_probe_e625.py"}

VALUE_CLASSES = [
    "the_key_is_stored_between_the_two_lines",
    "the_object_is_written_without_the_key_being_named",
    "the_object_is_handed_to_a_call_between_the_two_lines",
    "the_key_is_not_stored_between_the_two_lines",
]
UNCHANGED = VALUE_CLASSES[3]
READ_ONLY_METHODS = {"get", "keys", "items", "values", "copy", "setdefault_key_lookup"}

if HERE not in sys.path:
    sys.path.insert(0, HERE)
import e619_dead_reader_locals as e619                                              # noqa: E402
import e622_deadlocal_reach as e622                                                 # noqa: E402
import e623_deadline_key_use as e623                                                # noqa: E402
import e624_sibling_read_object as e624                                             # noqa: E402


# ---------------------------------------------------------------- literal helpers
def lit_str(node):
    """The literal string a node is, or None when it is not one."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def dict_literal_keys(call):
    """Keys a ``m.update(...)`` call names, or None when the payload cannot be read statically."""
    keys = set()
    for kw in call.keywords:
        if kw.arg is None:
            return None                      # **payload: keys unknown
        keys.add(kw.arg)
    for a in call.args:
        if isinstance(a, ast.Dict):
            for k in a.keys:
                lit = lit_str(k) if k is not None else None
                if lit is None:
                    return None              # {**other} or a computed key
                keys.add(lit)
        elif isinstance(a, ast.Call) and isinstance(a.func, ast.Attribute) and a.func.attr == "items":
            return None
        else:
            return None
    return keys


# ---------------------------------------------------------------- the interval
def interval_nodes(fn, lo, hi):
    """Nodes of ``fn`` whose own line sits in (lo, hi], not descending into nested definitions."""
    out, nested = [], []
    def walk(node):
        for ch in ast.iter_child_nodes(node):
            line = getattr(ch, "lineno", 0)
            if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
                if lo < line <= hi:
                    nested.append(line)
                continue
            if lo < line <= hi:
                out.append(ch)
            walk(ch)
    walk(fn)
    return out, sorted(set(nested))


def write_marks(nodes, recv_text, key, recv_name):
    """What the interval does to ``recv_text``'s entry at ``key``."""
    named, unnamed, handed = [], [], []
    if recv_text is None:
        return named, unnamed, handed
    for n in nodes:
        if isinstance(n, ast.Delete):
            for t in n.targets:
                if isinstance(t, ast.Subscript) and e624.text_of(t.value) == recv_text:
                    lit = lit_str(t.slice)
                    if lit == key:
                        named.append({"line": n.lineno, "form": "del_receiver_at_key"})
                    elif lit is None:
                        unnamed.append({"line": n.lineno, "form": "del_receiver_at_a_computed_key"})
            continue
        if isinstance(n, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            targets = n.targets if isinstance(n, ast.Assign) else [n.target]
            for t in targets:
                if not isinstance(t, ast.Subscript) or e624.text_of(t.value) != recv_text:
                    continue
                lit = lit_str(t.slice)
                form = "store_at_key" if lit == key else "store_at_a_computed_key"
                if lit == key:
                    named.append({"line": n.lineno, "form": form})
                elif lit is None:
                    unnamed.append({"line": n.lineno, "form": form})
            continue
        if isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Attribute) and e624.text_of(f.value) == recv_text:
                attr = f.attr
                if attr == "update":
                    keys = dict_literal_keys(n)
                    if keys is None:
                        unnamed.append({"line": n.lineno, "form": "receiver_update_unnamed_payload"})
                    elif key in keys:
                        named.append({"line": n.lineno, "form": "receiver_update_names_the_key"})
                elif attr == "setdefault":
                    lit = lit_str(n.args[0]) if n.args else None
                    if lit == key:
                        named.append({"line": n.lineno,
                                      "form": "receiver_setdefault_at_key"})
                    elif lit is None:
                        unnamed.append({"line": n.lineno,
                                        "form": "receiver_setdefault_at_a_computed_key"})
                elif attr == "pop":
                    lit = lit_str(n.args[0]) if n.args else None
                    if lit == key:
                        named.append({"line": n.lineno, "form": "receiver_pop_at_key"})
                    elif lit is None:
                        unnamed.append({"line": n.lineno,
                                        "form": "receiver_pop_at_a_computed_key"})
                elif attr in ("clear", "popitem"):
                    named.append({"line": n.lineno, "form": "receiver_" + attr})
                elif attr in READ_ONLY_METHODS:
                    continue
                else:
                    unnamed.append({"line": n.lineno, "form": "receiver_method_" + attr})
                continue
            for a in list(n.args) + [kw.value for kw in n.keywords]:
                if e624.text_of(a) == recv_text and recv_name is not None:
                    handed.append({"line": n.lineno, "form": "receiver_handed_to_a_call"})
                    break
    return named, unnamed, handed


def value_class(named, unnamed, handed):
    if named:
        return VALUE_CLASSES[0]
    if handed:
        return VALUE_CLASSES[2]
    if unnamed:
        return VALUE_CLASSES[1]
    return UNCHANGED


# ---------------------------------------------------------------- rows with value facts
def value_facts(tree, stem, graph):
    """E624's rows for one module, each sibling read extended with what the interval writes."""
    rows, inert = e624.object_facts(tree, stem, graph)
    out = []
    for r in rows:
        fn = e623.innermost(graph["fns"], r)
        if fn is None:
            out.append(r)
            continue
        same = [s for s in (r.get("sibling_reads") or []) if s.get("same_object")]
        for s in same:
            lo, hi = sorted((r["line"], s["line"]))
            nodes, nested = interval_nodes(fn, lo, hi)
            recv = s.get("sibling_receiver") or s.get("receiver")
            named, unnamed, handed = write_marks(nodes, recv, r["key"], recv)
            cls = value_class(named, unnamed, handed)
            s.update({
                "value_class": cls,
                "sees_the_value_the_dead_line_saw": cls == UNCHANGED,
                "writes_naming_the_key": named,
                "writes_without_naming_the_key": unnamed,
                "handovers_to_a_call": handed,
                "nested_definitions_in_the_interval": nested,
            })
        r["same_object_sibling_reads"] = len(same)
        r["same_object_sibling_reads_that_see_the_value"] = sum(
            1 for s in same if s.get("sees_the_value_the_dead_line_saw"))
        r["value_classes_of_the_same_object_reads"] = [s["value_class"] for s in same]
        r["duplicate_survives_the_value_test"] = bool(
            r.get("corrected_class") == e624.CORRECTED[0]
            and r.get("sibling_read_reads_the_same_object_after_the_dead_line")
            and r["same_object_sibling_reads_that_see_the_value"] > 0)
        # a nested def could be called between the lines and write the key: visible, not decided
        r["a_nested_definition_sits_in_the_interval"] = bool(
            any(s.get("nested_definitions_in_the_interval") for s in same))
        out.append(r)
    return out, inert


def measure(root=ROOT):
    mods, skipped = e619.population(root)
    skip = set(e622.SELF_PARTS) | set(e623.SELF_PARTS) | set(e624.SELF_PARTS) | set(SELF_PARTS)
    keep = [(rel, tree) for rel, tree in mods if os.path.basename(rel) not in skip]
    lines, inert = [], 0
    for rel, tree in keep:
        stem = os.path.basename(rel)[:-3]
        graph = e622.call_graph(tree, stem)
        rows, inert_here = value_facts(tree, stem, graph)
        for r in rows:
            r["module"] = rel
        lines.extend(rows)
        inert += inert_here
    lines.sort(key=lambda r: (r["module"], r["line"]))
    return {"population_modules": len(keep), "skipped": skipped, "lines": lines,
            "inert_dead_facekey_lines": inert,
            "cross_check": e624_cross_check(root, lines)}


# ---------------------------------------------------------------- cross-check
def e624_cross_check(root, lines):
    """Diff the re-derived rows against the face E624 published (line for line, class for class)."""
    out = {"published": False, "agrees": None}
    path = os.path.join(root, "results", "state_tilt", "siblingreadobject_latest.json")
    if not os.path.exists(path):
        out["note"] = "no published E624 face on disk"
        return out
    pub = json.load(io.open(path, encoding="utf-8"))
    key = lambda r: (r.get("module"), r.get("function"), r.get("def_line"), r.get("line"))
    published = {key(r): r.get("corrected_class") for r in (pub.get("lines") or [])}
    mine = {key(r): r.get("corrected_class") for r in lines}
    moved = sorted(k for k in set(mine) & set(published) if mine[k] != published[k])
    out.update({
        "published": True,
        "published_lines": len(published),
        "rederived_lines": len(mine),
        "lines_whose_class_differs_n": len(moved),
        "lines_whose_class_differs": [list(k) for k in moved[:10]],
        "lines_only_here": [list(k) for k in sorted(set(mine) - set(published))][:10],
        "lines_only_in_the_published_face":
            [list(k) for k in sorted(set(published) - set(mine))][:10],
        "published_superseded_same_object":
            sum(1 for r in (pub.get("lines") or [])
                if r.get("corrected_class") == e624.CORRECTED[0]),
        "rederived_superseded_same_object":
            sum(1 for r in lines if r.get("corrected_class") == e624.CORRECTED[0]),
        "agrees": not moved and not (set(published) - set(mine)),
    })
    return out


# ---------------------------------------------------------------- counts / verdict
def counts_of(m):
    lines = m["lines"]
    same_reads = 0
    vc = {k: 0 for k in VALUE_CLASSES}
    for r in lines:
        for s in (r.get("sibling_reads") or []):
            if not s.get("same_object"):
                continue
            same_reads += 1
            vc[s.get("value_class")] = vc.get(s.get("value_class"), 0) + 1
    dup = [r for r in lines
           if r.get("corrected_class") == e624.CORRECTED[0]
           and r.get("sibling_read_reads_the_same_object_after_the_dead_line")]
    survive = [r for r in dup if r.get("duplicate_survives_the_value_test")]
    changed = [r for r in dup if r["same_object_sibling_reads"] and
               not r["same_object_sibling_reads_that_see_the_value"]
               and any(s.get("value_class") == VALUE_CLASSES[0]
                       for s in (r.get("sibling_reads") or []) if s.get("same_object"))]
    undecided = [r for r in dup if r not in survive and r not in changed]
    c = {
        "population_modules": m["population_modules"],
        "skipped_modules": len(m["skipped"]),
        "live_dead_facekey_lines": len(lines),
        "inert_dead_facekey_lines": m["inert_dead_facekey_lines"],
        "rows_with_a_same_object_sibling_read": sum(
            1 for r in lines if r.get("same_object_sibling_reads")),
        "same_object_sibling_read_instances": same_reads,
        "same_object_duplicate_rows": len(dup),
        "same_object_duplicates_that_survive_the_value_test": len(survive),
        "same_object_duplicates_the_key_is_stored_for": len(changed),
        "same_object_duplicates_left_undecided": len(undecided),
        "rows_with_a_nested_definition_in_the_interval": sum(
            1 for r in lines if r.get("a_nested_definition_sits_in_the_interval")),
    }
    for k in VALUE_CLASSES:
        c["value_" + k] = vc[k]
    return c


def derive_verdict(m):
    c = counts_of(m)
    if c["population_modules"] == 0:
        return "no_face_publishers_in_the_population"
    if c["live_dead_facekey_lines"] == 0:
        return "no_live_dead_facekey_line_in_the_population"
    total = c["same_object_duplicate_rows"]
    if total == 0:
        return "no_same_object_duplicate_read_to_price"
    n = c["same_object_duplicates_that_survive_the_value_test"]
    if n == total:
        return ("every_one_of_the_%d_same_object_duplicate_reads_sees_the_value_the_dead_line_saw"
                % total)
    if n == 0:
        return ("none_of_the_%d_same_object_duplicate_reads_sees_the_value_the_dead_line_saw"
                % total)
    return ("%d_of_%d_same_object_duplicate_reads_sees_the_value_the_dead_line_saw"
            % (n, total))


def answer_of(m):
    c = counts_of(m)
    return ("E624 accepted %d sibling reads as reading the same object as their dead line, over %d "
            "of the %d live dead face-key lines.  Pricing the value now: %d of those reads find no "
            "write to that key on that object between the two lines, %d find a write that names the "
            "key, %d a write that does not name it, and %d the object handed to a call; so %d of the "
            "%d same-object duplicate rows survive the value test, %d are stored over, and %d stay "
            "undecided"
            % (c["same_object_sibling_read_instances"],
               c["rows_with_a_same_object_sibling_read"], c["live_dead_facekey_lines"],
               c["value_" + UNCHANGED], c["value_" + VALUE_CLASSES[0]],
               c["value_" + VALUE_CLASSES[1]], c["value_" + VALUE_CLASSES[2]],
               c["same_object_duplicates_that_survive_the_value_test"],
               c["same_object_duplicate_rows"],
               c["same_object_duplicates_the_key_is_stored_for"],
               c["same_object_duplicates_left_undecided"]))


def face_problems(face):
    p = []
    if not isinstance(face, dict) or "counts" not in face:
        return ["the face carries no counts block"]
    counts = face["counts"]
    lines = face.get("lines") or []
    if counts.get("live_dead_facekey_lines") != len(lines):
        p.append("counts.live_dead_facekey_lines says %r but the face publishes %d lines"
                 % (counts.get("live_dead_facekey_lines"), len(lines)))
    vc = {k: 0 for k in VALUE_CLASSES}
    same = 0
    for r in lines:
        got = [s.get("value_class") for s in (r.get("sibling_reads") or [])
               if s.get("same_object")]
        if sorted(got) != sorted(r.get("value_classes_of_the_same_object_reads") or []):
            p.append("line %r in %r does not mirror its same-object value classes on the row"
                     % (r.get("line"), r.get("function")))
        if len(got) != r.get("same_object_sibling_reads"):
            p.append("line %r in %r publishes same_object_sibling_reads=%r against %d read(s)"
                     % (r.get("line"), r.get("function"),
                        r.get("same_object_sibling_reads"), len(got)))
        ok = sum(1 for s in (r.get("sibling_reads") or [])
                 if s.get("same_object") and s.get("sees_the_value_the_dead_line_saw"))
        if ok != r.get("same_object_sibling_reads_that_see_the_value"):
            p.append("line %r in %r does not re-derive how many same-object reads see the value"
                     % (r.get("line"), r.get("function")))
        for s in (r.get("sibling_reads") or []):
            if not s.get("same_object"):
                continue
            same += 1
            if s.get("value_class") not in VALUE_CLASSES:
                p.append("line %r in %r carries value_class=%r"
                         % (r.get("line"), r.get("function"), s.get("value_class")))
                continue
            vc[s["value_class"]] += 1
            if s.get("sees_the_value_the_dead_line_saw") is not (s["value_class"] == UNCHANGED):
                p.append("line %r in %r marks sees_the_value against value_class=%r"
                         % (r.get("line"), r.get("function"), s["value_class"]))
            if s["value_class"] == VALUE_CLASSES[0] and not s.get("writes_naming_the_key"):
                p.append("line %r in %r says the key is stored with no naming write published"
                         % (r.get("line"), r.get("function")))
            if s["value_class"] == VALUE_CLASSES[1] and (
                    s.get("writes_naming_the_key") or not s.get("writes_without_naming_the_key")):
                p.append("line %r in %r says an unnamed write changed the key without that shape"
                         % (r.get("line"), r.get("function")))
            if s["value_class"] == VALUE_CLASSES[2] and (
                    s.get("writes_naming_the_key") or not s.get("handovers_to_a_call")):
                p.append("line %r in %r says the object was handed to a call without that shape"
                         % (r.get("line"), r.get("function")))
            if s["value_class"] == UNCHANGED and (
                    s.get("writes_naming_the_key") or s.get("writes_without_naming_the_key")
                    or s.get("handovers_to_a_call")):
                p.append("line %r in %r says nothing was written yet publishes write marks"
                         % (r.get("line"), r.get("function")))
        want_survive = bool(
            r.get("corrected_class") == e624.CORRECTED[0]
            and r.get("sibling_read_reads_the_same_object_after_the_dead_line")
            and r.get("same_object_sibling_reads_that_see_the_value"))
        if bool(r.get("duplicate_survives_the_value_test")) is not want_survive:
            p.append("line %r in %r publishes duplicate_survives_the_value_test=%r against its "
                     "own rows" % (r.get("line"), r.get("function"),
                                   r.get("duplicate_survives_the_value_test")))
    if counts.get("same_object_sibling_read_instances") != same:
        p.append("counts.same_object_sibling_read_instances does not re-derive")
    for k in VALUE_CLASSES:
        if counts.get("value_" + k) != vc[k]:
            p.append("counts.value_%s does not re-derive from the rows" % k)
    if sum(vc.values()) != same:
        p.append("the value classes do not add up to the same-object read count")
    dup = [r for r in lines
           if r.get("corrected_class") == e624.CORRECTED[0]
           and r.get("sibling_read_reads_the_same_object_after_the_dead_line")]
    if counts.get("same_object_duplicate_rows") != len(dup):
        p.append("counts.same_object_duplicate_rows does not re-derive")
    sv = [r for r in dup if r.get("duplicate_survives_the_value_test")]
    if counts.get("same_object_duplicates_that_survive_the_value_test") != len(sv):
        p.append("counts.same_object_duplicates_that_survive_the_value_test does not re-derive")
    if counts.get("rows_with_a_same_object_sibling_read") != sum(
            1 for r in lines if r.get("same_object_sibling_reads")):
        p.append("counts.rows_with_a_same_object_sibling_read does not re-derive")
    split = (counts.get("same_object_duplicates_that_survive_the_value_test", 0)
             + counts.get("same_object_duplicates_the_key_is_stored_for", 0)
             + counts.get("same_object_duplicates_left_undecided", 0))
    if split != counts.get("same_object_duplicate_rows"):
        p.append("the surviving/stored/undecided split does not add up to the duplicate count")
    cc = face.get("e624_cross_check") or {}
    if cc.get("published"):
        if cc.get("agrees") is False:
            p.append("the re-derived E624 population no longer matches the published face (%r "
                     "lines differ, %r only in the published face)"
                     % (cc.get("lines_whose_class_differs_n"),
                        len(cc.get("lines_only_in_the_published_face") or [])))
        if cc.get("published_superseded_same_object") != \
                cc.get("rederived_superseded_same_object"):
            p.append("the E624 superseded same-object count moved between the faces")
        if cc.get("rederived_lines") != counts.get("live_dead_facekey_lines"):
            p.append("the E624 cross-check re-derived %r lines but the counts say %r"
                     % (cc.get("rederived_lines"), counts.get("live_dead_facekey_lines")))
    derived = derive_verdict({"population_modules": counts.get("population_modules"),
                              "lines": lines,
                              "inert_dead_facekey_lines":
                                  counts.get("inert_dead_facekey_lines"),
                              "skipped": [None] * (counts.get("skipped_modules") or 0)})
    if face.get("verdict") != derived:
        p.append("the published verdict %r is not what the line rows force (%r)"
                 % (face.get("verdict"), derived))
    return p


def face_from(m):
    face = {
        "study": STUDY,
        "script": "scripts/e625_sibling_read_value.py",
        "evidence_cutoff": TODAY,
        "dept": "research+engineering",
        "method": ("take the same-object sibling reads E624 accepted (importing its object facts, "
                   "not re-implementing them) and scan the interval between the dead line and each "
                   "read for a write to that key on that object: a store/del/update/setdefault/pop "
                   "that names the key means the read sees a different value, an unnamed write or "
                   "the object handed to a call leaves it undecided, and only an untouched key "
                   "means the two reads saw the same value"),
        "population_source": ("scripts/*.py (AST) via e619.population, E624's same-object sibling "
                              "reads over E623's live-holder line rows, less the E619/E622/E623/"
                              "E624/this study self-exclusion sets"),
        "counts": counts_of(m),
        "e624_cross_check": m.get("cross_check") or {"published": False},
        "lines": m["lines"],
        "skipped": m["skipped"],
        "limits": [
            "no alias analysis: a write through another name bound to the same dict is invisible",
            "a write inside a nested def that is called between the two lines is not descended "
            "into; rows that have a nested def in the interval are published with that flag",
            "f(m) could write anything, so the object being handed to a call leaves the value "
            "undecided rather than unchanged",
            "value identity is read off the interval's write marks only -- two reads of an "
            "untouched key are taken to see the same value, which is what immutability of a dict "
            "entry between two statements means, not a proof about concurrent writers",
            "this study excludes itself and its smoke leg and probe, and keeps E619's, E622's, "
            "E623's and E624's self-exclusion sets, so the population is the one E624 published",
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


def choose():
    return {"counts": 1}


def untouched(m):
    face = {"counts": 1, "x": None}
    seen = []
    first = m["counts"]
    seen.append(m["counts"])
    json.dump(face, io.open("x", "w"))
    return seen


def stored(m):
    face = {"counts": 1, "x": None}
    seen = []
    first = m["counts"]
    m["counts"] = 2
    seen.append(m["counts"])
    json.dump(face, io.open("x", "w"))
    return seen


def updated_named(m):
    face = {"counts": 1, "x": None}
    seen = []
    first = m["counts"]
    m.update({"counts": 3})
    seen.append(m["counts"])
    json.dump(face, io.open("x", "w"))
    return seen


def updated_unnamed(m, payload):
    face = {"counts": 1, "x": None}
    seen = []
    first = m["counts"]
    m.update(payload)
    seen.append(m["counts"])
    json.dump(face, io.open("x", "w"))
    return seen


def handed(m, fixer):
    face = {"counts": 1, "x": None}
    seen = []
    first = m["counts"]
    fixer(m)
    seen.append(m["counts"])
    json.dump(face, io.open("x", "w"))
    return seen


def popped(m):
    face = {"counts": 1, "x": None}
    seen = []
    first = m["counts"]
    m.pop("counts", None)
    seen.append(m.get("counts"))
    json.dump(face, io.open("x", "w"))
    return seen


def computed_key(m, k):
    face = {"counts": 1, "x": None}
    seen = []
    first = m["counts"]
    m[k] = 9
    seen.append(m["counts"])
    json.dump(face, io.open("x", "w"))
    return seen


untouched({"counts": 1})
stored({"counts": 1})
updated_named({"counts": 1})
updated_unnamed({"counts": 1}, {"counts": 4})
handed({"counts": 1}, choose)
popped({"counts": 1})
computed_key({"counts": 1}, "counts")
'''


def selftest():
    legs = []
    tree = ast.parse(FIXTURE)
    graph = e622.call_graph(tree, "fixture")
    rows, inert = value_facts(tree, "fixture", graph)
    by = {r["function"]: r for r in rows}

    def vc(fn_name):
        r = by.get(fn_name) or {}
        same = [s for s in (r.get("sibling_reads") or []) if s.get("same_object")]
        return same[0]["value_class"] if same else None

    legs.append(("the fixture yields live dead face-key lines", len(rows) >= 6 and inert == 0))
    legs.append(("an untouched key is the value the dead line saw", vc("untouched") == UNCHANGED))
    legs.append(("a store naming the key changes the value",
                 vc("stored") == VALUE_CLASSES[0]))
    legs.append(("update with a literal naming the key changes the value",
                 vc("updated_named") == VALUE_CLASSES[0]))
    legs.append(("update with an unreadable payload leaves the value undecided",
                 vc("updated_unnamed") == VALUE_CLASSES[1]))
    legs.append(("the object handed to a call leaves the value undecided",
                 vc("handed") == VALUE_CLASSES[2]))
    legs.append(("pop at the key changes the value", vc("popped") == VALUE_CLASSES[0]))
    legs.append(("a store at a computed key leaves the value undecided",
                 vc("computed_key") == VALUE_CLASSES[1]))
    legs.append(("every row mirrors its same-object value classes",
                 all(sorted(r.get("value_classes_of_the_same_object_reads") or [])
                     == sorted(s.get("value_class") for s in (r.get("sibling_reads") or [])
                               if s.get("same_object")) for r in rows)))
    legs.append(("an untouchd row is not published as a surviving duplicate",
                 all(r.get("duplicate_survives_the_value_test") in (True, False) for r in rows)))

    for r in rows:
        r["module"] = "scripts/fixture.py"
        r["reach"] = r.get("reach") or "called_from_module_level"
    m = {"population_modules": 1, "skipped": [], "lines": rows,
         "inert_dead_facekey_lines": inert}
    c = counts_of(m)
    legs.append(("counts re-add the line rows", c["live_dead_facekey_lines"] == len(rows)))
    legs.append(("the value classes add up to the same-object reads",
                 sum(c["value_" + k] for k in VALUE_CLASSES)
                 == c["same_object_sibling_read_instances"]))
    face, problems = face_from(m)
    legs.append(("the fixture face has no problems", problems == []))
    bad = {"counts": dict(face["counts"]), "lines": [dict(r) for r in face["lines"]],
           "verdict": face["verdict"], "e624_cross_check": face["e624_cross_check"]}
    bad["counts"]["value_" + UNCHANGED] = int(bad["counts"]["value_" + UNCHANGED]) + 1
    legs.append(("a perturbed value class count fails face_problems",
                 face_problems(bad) != []))
    bad2 = {"counts": dict(face["counts"]), "lines": [dict(r) for r in face["lines"]],
            "verdict": "other", "e624_cross_check": face["e624_cross_check"]}
    legs.append(("a perturbed verdict fails face_problems", face_problems(bad2) != []))
    bad3 = {"counts": dict(face["counts"]), "lines": [dict(r) for r in face["lines"]][:-1],
            "verdict": face["verdict"], "e624_cross_check": face["e624_cross_check"]}
    legs.append(("a dropped line row fails face_problems", face_problems(bad3) != []))
    flipped = [dict(r) for r in face["lines"]]
    for r in flipped:
        same = [s for s in (r.get("sibling_reads") or []) if s.get("same_object")]
        if same:
            same[0]["sees_the_value_the_dead_line_saw"] = not same[0].get(
                "sees_the_value_the_dead_line_saw")
            break
    bad4 = {"counts": dict(face["counts"]), "lines": flipped, "verdict": face["verdict"],
            "e624_cross_check": face["e624_cross_check"]}
    legs.append(("a flipped same-object read fails face_problems", face_problems(bad4) != []))

    mods, _skipped = e619.population(ROOT)
    kept = [os.path.basename(rel) for rel, _ in mods
            if os.path.basename(rel) not in (set(e622.SELF_PARTS) | set(e623.SELF_PARTS)
                                             | set(e624.SELF_PARTS) | set(SELF_PARTS))]
    legs.append(("the real population parses and is non-empty", len(mods) > 100))
    legs.append(("this script excludes itself", "e625_sibling_read_value.py" not in kept))
    real = measure(root=ROOT)
    cc = real["cross_check"]
    legs.append(("the E624 cross-check read a published face", cc.get("published") is True))
    legs.append(("the re-derived rows are the ones E624 published", cc.get("agrees") is True))
    legs.append(("the published superseded same-object count carries over",
                 cc.get("published_superseded_same_object")
                 == cc.get("rederived_superseded_same_object")))
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
    print("population=%d lines=%d rows_with_same_object=%d same_object_reads=%d duplicates=%d "
          "survive=%d stored=%d undecided=%d skipped=%d"
          % (c["population_modules"], c["live_dead_facekey_lines"],
             c["rows_with_a_same_object_sibling_read"],
             c["same_object_sibling_read_instances"], c["same_object_duplicate_rows"],
             c["same_object_duplicates_that_survive_the_value_test"],
             c["same_object_duplicates_the_key_is_stored_for"],
             c["same_object_duplicates_left_undecided"], c["skipped_modules"]))
    for k in VALUE_CLASSES:
        print("  %s=%d" % (k, c["value_" + k]))
    print("verdict=" + face["verdict"])
    print("answer=" + face["answer"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))