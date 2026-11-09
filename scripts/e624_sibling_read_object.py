"""E624 -- is the sibling read counted for a dead face-key line reading the SAME OBJECT?

E623 (r1641) closed over how many kinds of dead face-key line exist, and one of its classes says
"superseded duplicate read": another read of the same key exists on a LATER line of the same
function.  E623's own limits list states the hole out loud -- *a read counts when it indexes the
same literal key, whatever the object*.  ``got["verdict"]`` and ``faces[UP_E350].get("verdict")``
are both a read of the key ``"verdict"``; they are not the same dict, so the second is not a
re-read of anything the first produced.

This study prices that hole.  For every published dead face-key line it takes the sibling reads
E623 counted, recovers each read's RECEIVER expression (``m["k"]`` -> ``m``, ``x.get("k")`` ->
``x``) and asks whether the receiver is the same object as the dead line's receiver.

Four relations, fixed before the scan:

  same_receiver_bound_once              the two receivers are the same expression text and no
                                        statement between the two lines binds that name (or
                                        assigns that attribute path): the same object, provably
  same_receiver_rebound_in_between      the same expression text, but the name or the attribute
                                        path is bound between the lines -- an earlier value is not
                                        the current one
  different_receiver_expression         the receiver text differs: a different object is read
  receiver_is_a_computed_expression     the receiver is a call, or has no nameable base, so object
                                        identity is not decidable statically

Each published row then carries a ``corrected_class`` recomputed from those relation facts, so the
count that E623 published is re-asked under object identity: a superseded duplicate that reads a
different object is not a superseded duplicate.

Population: E623's published line rows, re-derived by importing ``e623_deadline_key_use`` (its
``classify_tree``, ``innermost``, ``own_scope`` and ``key_reads`` are used, not re-implemented),
with E619's, E622's and this study's self-exclusion sets kept, and a cross-check that the
re-derived rows still match the published E623 face line for line and class for class.

Deliberately NOT done: no alias analysis.  ``q = P`` then ``q["days"]`` is published as a different
receiver even though the two names may hold one dict.  That is why every row carries both receiver
texts beside its verdict -- the population is 34 lines and a reader can check any row by eye.

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
FACE = "SIBLINGREADOBJECT-%s.json" % TODAY
LATEST = "siblingreadobject_latest.json"
STUDY = "E624_sibling_read_object"
SELF_PARTS = {"e624_sibling_read_object.py", "run_e624_smoke_leg.py", "_probe_e624.py"}
RELATIONS = ["same_receiver_bound_once", "same_receiver_rebound_in_between",
             "different_receiver_expression", "receiver_is_a_computed_expression"]
CORRECTED = ["superseded_duplicate_read_on_the_same_object",
             "same_object_read_only_before_the_dead_line",
             "another_object_is_read_instead",
             "only_read_of_that_key_on_that_object_in_the_function"]
# a relation that does prove object identity, used whenever a row needs one boolean
SAME = "same_receiver_bound_once"

if HERE not in sys.path:
    sys.path.insert(0, HERE)
import e619_dead_reader_locals as e619                                              # noqa: E402
import e622_deadlocal_reach as e622                                                 # noqa: E402
import e623_deadline_key_use as e623                                                # noqa: E402


# ---------------------------------------------------------------- receivers and bindings
def text_of(node):
    """Source text of an expression node, whitespace-normalised; None when unparseable."""
    if node is None:
        return None
    try:
        return " ".join(ast.unparse(node).split())
    except Exception:
        return None


def receiver_of(node):
    """The object a key read reads from: ``m["k"]`` -> ``m``, ``x.get("k")`` -> ``x``."""
    if isinstance(node, ast.Subscript):
        return node.value
    if isinstance(node, ast.Call):
        return getattr(node.func, "value", None)
    return None


def base_name(node):
    """The leftmost Name of a receiver chain, or None when there is no nameable base."""
    seen = 0
    while node is not None and seen < 20:
        seen += 1
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, (ast.Attribute, ast.Subscript)):
            node = node.value
        else:
            # a call result is a fresh object, a constant has no name: not the same object twice
            return None
    return None


def target_names(target):
    """Every name bound by one assignment/for target."""
    if isinstance(target, ast.Name):
        yield target.id
    elif isinstance(target, (ast.Tuple, ast.List)):
        for el in target.elts:
            for n in target_names(el):
                yield n
    elif isinstance(target, ast.Starred):
        for n in target_names(target.value):
            yield n


def rebind_lines(scope, name, recv_text):
    """Lines in ``scope`` that bind ``name`` or assign the receiver's own attribute path."""
    out = []
    for n in scope:
        targets, line = [], None
        if isinstance(n, ast.Assign):
            targets, line = n.targets, n.lineno
        elif isinstance(n, (ast.AugAssign, ast.AnnAssign)):
            targets, line = [n.target], n.lineno
        elif isinstance(n, (ast.For, ast.AsyncFor)):
            targets, line = [n.target], n.lineno
        elif isinstance(n, (ast.With, ast.AsyncWith)):
            # a withitem carries no line of its own; the With statement's line is the binding line
            bound = [it.optional_vars for it in n.items if it.optional_vars is not None]
            if bound:
                targets, line = bound, n.lineno
        elif isinstance(n, ast.NamedExpr):
            targets, line = [n.target], n.lineno
        elif isinstance(n, ast.ExceptHandler):
            if n.name == name:
                out.append(n.lineno)
            continue
        else:
            continue
        for t in targets:
            if name in set(target_names(t)) or (recv_text and text_of(t) == recv_text):
                out.append(line)
                break
    return sorted(set(out))


def relation_of(dead_node, sibling, scope, dead_line, sibling_line):
    """The object relation between the dead read and one sibling read (see module docstring)."""
    d_rcv, s_rcv = receiver_of(dead_node), receiver_of(sibling)
    d_txt, s_txt = text_of(d_rcv), text_of(s_rcv)
    if d_txt is None or s_txt is None:
        return "receiver_is_a_computed_expression", d_txt, s_txt
    if d_txt != s_txt:
        return "different_receiver_expression", d_txt, s_txt
    name = base_name(d_rcv)
    if name is None:
        return "receiver_is_a_computed_expression", d_txt, s_txt
    between = [ln for ln in rebind_lines(scope, name, d_txt) if dead_line < ln <= sibling_line]
    if between:
        return "same_receiver_rebound_in_between", d_txt, s_txt
    return SAME, d_txt, s_txt


# ---------------------------------------------------------------- rows with object facts
# the relation order used when two reads sit on one line and disagree
PRECEDENCE = [SAME, "different_receiver_expression", "same_receiver_rebound_in_between",
              "receiver_is_a_computed_expression"]


def object_facts(tree, stem, graph):
    """E623's rows for one module, each extended with the object relation of its sibling reads."""
    rows, inert = e623.classify_tree(tree, stem)
    out = []
    for r in rows:
        r.pop("_own_id", None)
        fn = e623.innermost(graph["fns"], r)
        if fn is None:
            continue
        scope = e623.own_scope(fn)
        reads = e623.key_reads(scope, r["key"])
        dead_nodes = [n for n in reads if n.lineno == r["line"]]
        if not dead_nodes:
            r.update({"sibling_reads": [], "nearest_later_sibling_relation": None,
                      "sibling_read_reads_the_same_object_after_the_dead_line": False,
                      "sibling_read_reads_the_same_object_before_the_dead_line": False,
                      "dead_reads_on_that_line": 0,
                      "dead_receiver": None,
                      "corrected_class": "only_read_of_that_key_on_that_object_in_the_function",
                      "object_facts_note": "no read node resolved at the published line"})
            out.append(r)
            continue
        sibling = []
        for line in (r.get("other_read_lines") or []):
            rels = []
            for n in reads:
                if n.lineno != line:
                    continue
                rel, d_txt, s_txt = relation_of(dead_nodes[0], n, scope, r["line"], line)
                rels.append((rel, d_txt, s_txt))
            if not rels:
                continue
            rels.sort(key=lambda t: PRECEDENCE.index(t[0]))
            sibling.append({"line": line, "relation": rels[0][0],
                            "receiver": rels[0][1], "sibling_receiver": rels[0][2],
                            "same_object": rels[0][0] == SAME,
                            "relations_on_that_line": [t[0] for t in rels]})
        later = [s for s in sibling if s["line"] > r["line"]]
        earlier = [s for s in sibling if s["line"] < r["line"]]
        same_after = any(s["same_object"] for s in later)
        same_before = any(s["same_object"] for s in earlier)
        if same_after:
            corrected = CORRECTED[0]
        elif same_before:
            corrected = CORRECTED[1]
        elif sibling:
            corrected = CORRECTED[2]
        else:
            corrected = CORRECTED[3]
        r.update({
            "sibling_reads": sibling,
            "nearest_later_sibling_relation": later[0]["relation"] if later else None,
            "sibling_read_reads_the_same_object_after_the_dead_line": same_after,
            "sibling_read_reads_the_same_object_before_the_dead_line": same_before,
            "dead_reads_on_that_line": len(dead_nodes),
            "dead_receiver": text_of(receiver_of(dead_nodes[0])),
            "corrected_class": corrected,
        })
        out.append(r)
    return out, inert


def measure(root=ROOT):
    mods, skipped = e619.population(root)
    skip = set(e622.SELF_PARTS) | set(e623.SELF_PARTS) | set(SELF_PARTS)
    keep = [(rel, tree) for rel, tree in mods
            if os.path.basename(rel) not in skip]
    lines = []
    inert = 0
    for rel, tree in keep:
        stem = os.path.basename(rel)[:-3]
        graph = e622.call_graph(tree, stem)
        rows, inert_here = object_facts(tree, stem, graph)
        for r in rows:
            r["module"] = rel
        lines.extend(rows)
        inert += inert_here
    lines.sort(key=lambda r: (r["module"], r["line"]))
    return {"population_modules": len(keep), "skipped": skipped, "lines": lines,
            "inert_dead_facekey_lines": inert,
            "cross_check": e623_cross_check(root, lines)}


# ---------------------------------------------------------------- cross-check
def e623_cross_check(root, lines):
    """Diff the re-derived rows against the face E623 published (line for line, class for class)."""
    out = {"published": False, "agrees": None}
    path = os.path.join(root, "results", "state_tilt", "deadlinekeyuse_latest.json")
    if not os.path.exists(path):
        out["note"] = "no published E623 face on disk"
        return out
    pub = json.load(io.open(path, encoding="utf-8"))
    published = {(r.get("module"), r.get("function"), r.get("def_line"), r.get("line")):
                 r.get("class") for r in (pub.get("lines") or [])}
    mine = {(r.get("module"), r.get("function"), r.get("def_line"), r.get("line")):
            r.get("class") for r in lines}
    moved = sorted(k for k in set(mine) & set(published) if mine[k] != published[k])
    out.update({
        "published": True,
        "published_lines": len(published),
        "rederived_lines": len(mine),
        "lines_whose_class_differs": [list(k) for k in moved[:10]],
        "lines_whose_class_differs_n": len(moved),
        "lines_only_here": [list(k) for k in sorted(set(mine) - set(published))][:10],
        "lines_only_in_the_published_face":
            [list(k) for k in sorted(set(published) - set(mine))][:10],
        "agrees": not moved and not (set(published) - set(mine)),
    })
    return out


# ---------------------------------------------------------------- counts / verdict
def counts_of(m):
    lines = m["lines"]
    rel = {k: 0 for k in RELATIONS}
    for r in lines:
        for s in (r.get("sibling_reads") or []):
            rel[s["relation"]] = rel.get(s["relation"], 0) + 1
    sup = [r for r in lines if r.get("class") == "superseded_duplicate_read"]
    sup_same = [r for r in sup if r.get("sibling_read_reads_the_same_object_after_the_dead_line")]
    corrected = {k: sum(1 for r in lines if r.get("corrected_class") == k) for k in CORRECTED}
    c = {
        "population_modules": m["population_modules"],
        "skipped_modules": len(m["skipped"]),
        "live_dead_facekey_lines": len(lines),
        "inert_dead_facekey_lines": m["inert_dead_facekey_lines"],
        "rows_with_a_sibling_read": sum(1 for r in lines if r.get("sibling_reads")),
        "sibling_read_instances": sum(len(r.get("sibling_reads") or []) for r in lines),
        "superseded_rows": len(sup),
        "superseded_rows_on_the_same_object": len(sup_same),
        "superseded_rows_on_another_object": len(sup) - len(sup_same),
        "rows_downgraded_from_e623_class": sum(
            1 for r in lines if r.get("class") == "superseded_duplicate_read"
            and r.get("corrected_class") != CORRECTED[0]),
        "rows_whose_dead_line_had_no_resolvable_read": sum(
            1 for r in lines if r.get("dead_reads_on_that_line") == 0),
    }
    for k in RELATIONS:
        c["relation_" + k] = rel[k]
    for k in CORRECTED:
        c["corrected_" + k] = corrected[k]
    return c


def derive_verdict(m):
    c = counts_of(m)
    if c["population_modules"] == 0:
        return "no_face_publishers_in_the_population"
    if c["live_dead_facekey_lines"] == 0:
        return "no_live_dead_facekey_line_in_the_population"
    total = c["superseded_rows"]
    if total == 0:
        return "no_superseded_duplicate_read_to_check"
    n = c["superseded_rows_on_the_same_object"]
    if n == total:
        return ("every_one_of_the_%d_superseded_duplicate_reads_reads_the_same_object_as_the_dead"
                "_line" % total)
    if n == 0:
        return ("none_of_the_%d_superseded_duplicate_reads_reads_the_same_object_as_the_dead_line"
                % total)
    return ("%d_of_%d_superseded_duplicate_reads_read_the_same_object_as_the_dead_line"
            % (n, total))


def answer_of(m):
    c = counts_of(m)
    return ("E623 published %d dead face-key lines in live holders and classed %d as superseded "
            "duplicate reads -- a later read of the same literal key.  Under object identity %d of "
            "those %d read the same object as the dead line and %d read a different one, so %d "
            "lines lose that class and are re-published as another_object_is_read_instead.  Across "
            "all %d lines there are %d sibling reads: %d are the same receiver bound once, %d the "
            "same receiver rebound in between, %d a different receiver expression, and %d sit on a "
            "receiver that is a computed expression; corrected, %d lines are superseded duplicates "
            "on the same object, %d read the same object only before the dead line, %d read "
            "another object instead, and %d are the only read of that key on that object in the "
            "function"
            % (c["live_dead_facekey_lines"], c["superseded_rows"],
               c["superseded_rows_on_the_same_object"], c["superseded_rows"], 
               c["superseded_rows_on_another_object"], c["rows_downgraded_from_e623_class"],
               c["live_dead_facekey_lines"], c["sibling_read_instances"],
               c["relation_same_receiver_bound_once"],
               c["relation_same_receiver_rebound_in_between"],
               c["relation_different_receiver_expression"],
               c["relation_receiver_is_a_computed_expression"],
               c["corrected_" + CORRECTED[0]], c["corrected_" + CORRECTED[1]],
               c["corrected_" + CORRECTED[2]], c["corrected_" + CORRECTED[3]]))


def face_problems(face):
    p = []
    if not isinstance(face, dict) or "counts" not in face:
        return ["the face carries no counts block"]
    counts = face["counts"]
    lines = face.get("lines") or []
    if counts.get("live_dead_facekey_lines") != len(lines):
        p.append("counts.live_dead_facekey_lines says %r but the face publishes %d lines"
                 % (counts.get("live_dead_facekey_lines"), len(lines)))
    for k in CORRECTED:
        want = sum(1 for r in lines if r.get("corrected_class") == k)
        if counts.get("corrected_" + k) != want:
            p.append("counts.corrected_%s does not re-derive from the lines" % k)
    if sum(counts.get("corrected_" + k, 0) for k in CORRECTED) != len(lines):
        p.append("the corrected classes do not add up to the published line count")
    rel = {k: 0 for k in RELATIONS}
    for r in lines:
        for s in (r.get("sibling_reads") or []):
            rel[s.get("relation")] = rel.get(s.get("relation"), 0) + 1
    for k in RELATIONS:
        if counts.get("relation_" + k) != rel[k]:
            p.append("counts.relation_%s does not re-derive from the sibling_reads" % k)
    if counts.get("sibling_read_instances") != sum(rel.values()):
        p.append("counts.sibling_read_instances does not equal the relation total")
    if counts.get("rows_with_a_sibling_read") != sum(1 for r in lines if r.get("sibling_reads")):
        p.append("counts.rows_with_a_sibling_read does not re-derive")
    sup = [r for r in lines if r.get("class") == "superseded_duplicate_read"]
    if counts.get("superseded_rows") != len(sup):
        p.append("counts.superseded_rows does not re-derive from the E623 classes on the rows")
    same = [r for r in sup if r.get("sibling_read_reads_the_same_object_after_the_dead_line")]
    if counts.get("superseded_rows_on_the_same_object") != len(same):
        p.append("counts.superseded_rows_on_the_same_object does not re-derive")
    if counts.get("superseded_rows_on_another_object") != len(sup) - len(same):
        p.append("counts.superseded_rows_on_another_object does not re-derive")
    for r in lines:
        if r.get("corrected_class") not in CORRECTED:
            p.append("line %r in %r carries corrected_class=%r, not a published class"
                     % (r.get("line"), r.get("function"), r.get("corrected_class")))
        if r.get("corrected_class") == CORRECTED[0] and not \
                r.get("sibling_read_reads_the_same_object_after_the_dead_line"):
            p.append("line %r in %r is published as a same-object superseded read with no "
                     "same-object read after it" % (r.get("line"), r.get("function")))
        if r.get("corrected_class") == CORRECTED[1] and (
                r.get("sibling_read_reads_the_same_object_after_the_dead_line")
                or not r.get("sibling_read_reads_the_same_object_before_the_dead_line")):
            p.append("line %r in %r is published as a before-only same-object read without that "
                     "shape" % (r.get("line"), r.get("function")))
        if r.get("corrected_class") == CORRECTED[2] and not r.get("sibling_reads"):
            p.append("line %r in %r says another object is read instead, yet has no sibling read"
                     % (r.get("line"), r.get("function")))
        if r.get("corrected_class") == CORRECTED[3] and r.get("sibling_reads"):
            p.append("line %r in %r says it is the only read on that object, yet publishes "
                     "sibling reads" % (r.get("line"), r.get("function")))
        for s in (r.get("sibling_reads") or []):
            if s.get("relation") not in RELATIONS:
                p.append("line %r in %r carries a sibling read with relation=%r"
                         % (r.get("line"), r.get("function"), s.get("relation")))
            if s.get("same_object") is not (s.get("relation") == SAME):
                p.append("line %r in %r marks same_object=%r against relation=%r"
                         % (r.get("line"), r.get("function"), s.get("same_object"),
                            s.get("relation")))
            if s.get("receiver") != s.get("sibling_receiver") and \
                    s.get("relation") != "different_receiver_expression":
                p.append("line %r in %r publishes unequal receiver texts under a same-receiver "
                         "relation" % (r.get("line"), r.get("function")))
    cc = face.get("e623_cross_check") or {}
    if cc.get("published"):
        if cc.get("agrees") is False:
            p.append("the re-derived E623 population no longer matches the published face "
                     "(%r lines differ, %r only in the published face)"
                     % (cc.get("lines_whose_class_differs_n"),
                        len(cc.get("lines_only_in_the_published_face") or [])))
        if cc.get("rederived_lines") != counts.get("live_dead_facekey_lines"):
            p.append("the E623 cross-check re-derived %r lines but the counts say %r"
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
    """The published face built from an already-walked population (selftest walks the corpus once)."""
    face = {
        "study": STUDY,
        "script": "scripts/e624_sibling_read_object.py",
        "evidence_cutoff": TODAY,
        "dept": "research+engineering",
        "method": ("take the dead face-key lines E623 published (importing its classification, "
                   "not re-implementing it), recover each read's receiver expression, and for "
                   "every sibling read E623 counted ask whether the receiver is the same object: "
                   "same text and no binding of that name or assignment of that attribute path "
                   "between the two lines; then re-publish each row under a corrected class"),
        "population_source": ("scripts/*.py (AST) via e619.population, E623's live-holder line "
                              "rows, less E619's, E622's, E623's and this study's self-exclusion "
                              "sets"),
        "counts": counts_of(m),
        "e623_cross_check": m["cross_check"],
        "lines": m["lines"],
        "skipped": m["skipped"],
        "limits": [
            "no alias analysis: q = P; q[\"days\"] is published as a different receiver even "
            "though both names may hold one dict -- each row carries both receiver texts so the "
            "34-line population can be checked by eye",
            "a mutation of the object is not a rebinding of the name: m[\"k\"] read twice with "
            "m[\"k\"] = ... in between still counts as the same object, which is what object "
            "identity means but not what value identity would mean",
            "in-place aliasing through a function argument (f(m) mutating m) is invisible",
            "the receiver has to be a nameable chain; f()[\"k\"] and [a][b][\"k\"] are published "
            "as computed and are not decided either way",
            "this study excludes itself, its smoke leg and probe, and keeps E619's, E622's and "
            "E623's self-exclusion sets, so the population is the one E623 published",
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


def get(x):
    return {"k": 1, "bar": 2}


def build(m, other):
    face = {"counts": {"n": 1}, "rows": [], "x": None, "d": None, "k": None}
    seen = []
    same = m["counts"]
    moved = m["rows"]
    elsewhere = other["x"]
    getter = m["d"]
    callme = choose()["x"]
    copycat = dict(m)["x"]
    seen.append(m["x"])
    seen.append(m["counts"])
    seen.append(m.get("d"))
    m = {"rows": 1, "x": 2, "d": 3, "counts": 4}
    seen.append(m["rows"])
    face["x"] = seen
    json.dump(face, io.open("x", "w"))
    return face


def walk(rows):
    out = []
    for r in rows:
        prev = r["bar"]
        out.append(r["bar"])
    return out


def twice(m):
    out = []
    first = get(m)["k"]
    out.append(get(m)["k"])
    return out


def solo(m):
    only = m["counts"]
    return 1


build({"counts": 1, "rows": [], "x": None, "d": None}, {"x": 1})
walk([{"bar": 1}])
twice({"k": 1})
solo({"counts": 1})
'''


def selftest():
    legs = []
    tree = ast.parse(FIXTURE)
    graph = e622.call_graph(tree, "fixture")
    rows, inert = object_facts(tree, "fixture", graph)
    by = {r["local"]: r for r in rows}

    def rel_of(local):
        sibs = (by.get(local) or {}).get("sibling_reads") or []
        return sibs[0]["relation"] if sibs else None

    legs.append(("the fixture yields live dead face-key lines", len(rows) >= 8 and inert == 0))
    legs.append(("every row publishes a corrected class",
                 all(r.get("corrected_class") in CORRECTED for r in rows)))
    legs.append(("a receiver read again with no rebinding in between is the same object",
                 rel_of("same") == SAME))
    legs.append(("a receiver rebound between the two lines is not the same object",
                 rel_of("moved") == "same_receiver_rebound_in_between"))
    legs.append(("a different receiver name is a different object",
                 rel_of("elsewhere") == "different_receiver_expression"))
    legs.append(("a .get() on the same receiver is the same object",
                 rel_of("getter") == SAME))
    legs.append(("a call receiver against a name is a different object",
                 rel_of("callme") == "different_receiver_expression"))
    legs.append(("a dict(m) receiver against a name is a different object",
                 rel_of("copycat") == "different_receiver_expression"))
    legs.append(("a loop-local read after the dead line stays the same object",
                 rel_of("prev") == SAME))
    legs.append(("the same computed receiver twice is not decidable",
                 rel_of("first") == "receiver_is_a_computed_expression"))
    legs.append(("a row with no sibling read is the only read on that object",
                 by.get("only", {}).get("corrected_class") == CORRECTED[3]))
    legs.append(("a row whose only sibling reads another object is not a duplicate",
                 by.get("elsewhere", {}).get("corrected_class") == CORRECTED[2]))
    legs.append(("the loop-carried row publishes a same-object read after the dead line",
                 by.get("prev", {}).get("sibling_read_reads_the_same_object_after_the_dead_line")
                 is True))
    legs.append(("the dead receiver text is published",
                 by.get("same", {}).get("dead_receiver") == "m"))

    for r in rows:
        r["module"] = "scripts/fixture.py"
        r["reach"] = r.get("reach") or "called_from_module_level"
    m = {"population_modules": 1, "skipped": [], "lines": rows,
         "inert_dead_facekey_lines": inert}
    c = counts_of(m)
    legs.append(("counts re-add the line rows",
                 c["live_dead_facekey_lines"] == len(rows)
                 and sum(c["corrected_" + k] for k in CORRECTED) == len(rows)))
    legs.append(("the relation tally equals the sibling read instances",
                 sum(c["relation_" + k] for k in RELATIONS) == c["sibling_read_instances"]))
    legs.append(("the superseded count is the same-object one",
                 c["superseded_rows_on_the_same_object"]
                 == len([r for r in rows if r.get("class") == "superseded_duplicate_read"
                         and r.get("sibling_read_reads_the_same_object_after_the_dead_line")])))
    legs.append(("the verdict is derived from the superseded/same-object split",
                 c["superseded_rows"] > 0 and derive_verdict(m).startswith(
                     "%d_of_%d_superseded_duplicate_reads_read_the_same_object_as_the_dead_line"
                     % (c["superseded_rows_on_the_same_object"], c["superseded_rows"]))))

    mods, skipped = e619.population(ROOT)
    kept = [rel for rel, _ in mods if os.path.basename(rel) not in
            (set(e622.SELF_PARTS) | set(e623.SELF_PARTS) | set(SELF_PARTS))]
    legs.append(("the real population parses and is non-empty", len(mods) > 100))
    legs.append(("this script excludes itself",
                 "scripts/e624_sibling_read_object.py" not in kept))
    real = measure(root=ROOT)
    cc = real["cross_check"]
    legs.append(("the E623 cross-check read a published face", cc.get("published") is True))
    legs.append(("the re-derived rows are the ones E623 published", cc.get("agrees") is True))
    face, problems = face_from(real)
    legs.append(("the built face has no problems", problems == []))
    bad = {"counts": dict(face["counts"]), "lines": [dict(r) for r in face["lines"]],
           "verdict": face["verdict"], "e623_cross_check": face["e623_cross_check"]}
    bad["counts"]["superseded_rows_on_the_same_object"] = int(
        bad["counts"]["superseded_rows_on_the_same_object"]) + 1
    legs.append(("a perturbed same-object count fails face_problems", face_problems(bad) != []))
    bad2 = {"counts": dict(face["counts"]), "lines": [dict(r) for r in face["lines"]],
            "verdict": "other", "e623_cross_check": face["e623_cross_check"]}
    legs.append(("a perturbed verdict fails face_problems", face_problems(bad2) != []))
    bad3 = {"counts": dict(face["counts"]), "lines": [dict(r) for r in face["lines"]][:-1],
            "verdict": face["verdict"], "e623_cross_check": face["e623_cross_check"]}
    legs.append(("a dropped line row fails face_problems", face_problems(bad3) != []))
    flipped = [dict(r) for r in face["lines"]]
    for r in flipped:
        if r.get("corrected_class") == CORRECTED[1]:
            r["sibling_read_reads_the_same_object_before_the_dead_line"] = False
            break
    bad4 = {"counts": dict(face["counts"]), "lines": flipped, "verdict": face["verdict"],
            "e623_cross_check": face["e623_cross_check"]}
    legs.append(("a before-only row without its shape fails face_problems",
                 face_problems(bad4) != []))

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
    print("population=%d lines=%d rows_with_sibling=%d sibling_reads=%d superseded=%d "
          "same_object=%d another_object=%d downgraded=%d skipped=%d"
          % (c["population_modules"], c["live_dead_facekey_lines"],
             c["rows_with_a_sibling_read"], c["sibling_read_instances"],
             c["superseded_rows"], c["superseded_rows_on_the_same_object"],
             c["superseded_rows_on_another_object"],
             c["rows_downgraded_from_e623_class"], c["skipped_modules"]))
    for k in RELATIONS:
        print("  %s=%d" % (k, c["relation_" + k]))
    for k in CORRECTED:
        print("  corrected %s=%d" % (k, c["corrected_" + k]))
    print("verdict=" + face["verdict"])
    print("answer=" + face["answer"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))