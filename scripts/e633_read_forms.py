"""E633 -- does a read form the classifier does not name sit on a counted read line?

E632 (r1651 bm-b) counts read *nodes* on the lines E631 counted, using the same classifier E623
built: a string subscript or a ``.get("key")`` call.  E632 publishes that limit itself -- a read the
classifier does not name is invisible at node level exactly as it was at line level.

This study prices that hole on the population E632 already fixed: for each of its counted read
lines, resolve the receiver of the counted read, then walk every *other* access of that receiver on
the same physical line and classify it.  The classes are keyed on one question -- does this access
read THIS key without producing a read node the classifier would count?

  * ``recognised_read_of_the_key``     the node E623 already counts (cross-checked against E632)
  * ``unnamed_entry_read_of_the_key``  ``"k" in d``, ``del d["k"]``, ``d.setdefault("k", ...)``,
                                       ``d.pop("k")`` at the receiver's own level -- a real entry
                                       read that no read node represents
  * ``read_of_a_different_key``        a named key that is not this one
  * ``read_with_a_computed_key``       a subscript/keyed call whose key is an expression: it reads
                                       *some* key of the receiver, not demonstrably this one
  * ``read_below_the_receiver``        depth >= 2: the chain has already left the receiver object
  * ``container_enumeration``          ``.keys()/.values()/.items()``, ``for k in d``, ``len(d)``,
                                       a bare ``d`` truthiness test, an iteration

Aliases are followed one hop inside the function (``v = d`` makes ``v`` a receiver too), because a
variable subscript is one of the forms that would otherwise be invisible.  The walk is NAME level,
not object level (E206/E207 family) and that is published as a limit rather than a footnote.

CLI: build (default) | check | verify | selftest
"""
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
FACE = "READFORMGAP.json"
LATEST = "readformgap_latest.json"
STUDY = "E633_read_forms"
SELF_PARTS = {"e633_read_forms.py", "run_e633_smoke_leg.py", "_probe_e633.py"}
SOURCE_FACE = "results/state_tilt/READSAMELINE.json"

import e623_deadline_key_use as e623  # noqa: E402

R_KEY = "recognised_read_of_the_key"
R_UNNAMED = "unnamed_entry_read_of_the_key"
R_OTHER = "read_of_a_different_key"
R_COMPUTED = "read_with_a_computed_key"
R_BELOW = "read_below_the_receiver"
R_CONTAINER = "container_enumeration"
R_WRITE = "write_of_the_key"

FORMS = [R_KEY, R_UNNAMED, R_OTHER, R_COMPUTED, R_BELOW, R_CONTAINER, R_WRITE]

#: form -> True (reads this key without a read node) / False (does not) / None (cannot be decided)
COULD_FORCE = {
    R_KEY: False,
    R_UNNAMED: True,
    R_OTHER: False,
    R_COMPUTED: None,
    R_BELOW: False,
    R_CONTAINER: False,
    R_WRITE: False,
}

CONTAINER_ATTRS = {"keys", "values", "items", "copy", "popitem", "clear"}
ENTRY_CALL_ATTRS = {"setdefault", "pop"}
BARE_CALLS = {"len", "bool", "str", "any", "all", "list", "dict", "sorted", "iter", "sum", "min", "max"}


# ---------------------------------------------------------------- AST helpers
def load_source(root=ROOT):
    return json.load(io.open(os.path.join(root, SOURCE_FACE), encoding="utf-8"))


def counted_lines(source):
    """One row per counted read line, straight out of E632's rows."""
    out = []
    for r in (source.get("rows") or []):
        out.append({
            "module": r.get("module"),
            "function": r.get("function"),
            "dead_line": r.get("dead_line", r.get("line")),
            "key": r.get("key"),
            "read_line": r.get("read_line"),
            "read_nodes_on_the_line": r.get("read_nodes_on_the_line"),
            "is_a_duplicate_row": bool(r.get("is_a_duplicate_row")),
        })
    out.sort(key=lambda x: (x["module"] or "", x["read_line"], x["key"] or ""))
    return out


def function_nodes(tree):
    return [n for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]


def base_of(node):
    """(leftmost name, container depth) of an expression, or (None, depth)."""
    d = 0
    cur = node
    for _ in range(64):
        if isinstance(cur, ast.Subscript) or isinstance(cur, ast.Attribute):
            d += 1
            cur = cur.value
        elif isinstance(cur, ast.Call):
            cur = cur.func
        elif isinstance(cur, ast.Name):
            return cur.id, d
        else:
            return None, d
    return None, d


def const_str(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def aliases_of(scope, root):
    """One hop: names bound to ``root`` by a plain ``v = root`` inside the function."""
    if not root:
        return set()
    out = set()
    for n in scope:
        if not isinstance(n, ast.Assign):
            continue
        if not isinstance(n.value, ast.Name) or n.value.id != root:
            continue
        for t in n.targets:
            if isinstance(t, ast.Name):
                out.add(t.id)
    return out


def resolve_root(scope, name):
    """One hop backwards: if ``name`` was bound by a plain ``name = other``, that is the root."""
    if not name:
        return name
    for n in scope:
        if not isinstance(n, ast.Assign):
            continue
        if not isinstance(n.value, ast.Name):
            continue
        for t in n.targets:
            if isinstance(t, ast.Name) and t.id == name and n.value.id != name:
                return n.value.id
    return name


def access_sites(scope, line, roots):
    """Every access of any name in ``roots`` whose node starts on ``line``."""
    sites = []
    chain_roots = set()
    for n in scope:
        if getattr(n, "lineno", None) != line:
            continue
        if isinstance(n, ast.Subscript):
            name, depth = base_of(n.value)
            if name in roots:
                ctx = ("store" if isinstance(n.ctx, ast.Store)
                       else "del" if isinstance(n.ctx, ast.Del) else "load")
                sites.append({"node": n, "kind": "subscript", "root": name,
                              "depth": depth + 1, "key": const_str(n.slice), "ctx": ctx})
                chain_roots.add(id(base_name(n.value)))
        elif isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
            name, depth = base_of(n.func.value)
            if name in roots:
                arg = const_str(n.args[0]) if n.args else None
                sites.append({"node": n, "kind": "call", "root": name,
                              "depth": depth + 1, "attr": n.func.attr, "key": arg})
                chain_roots.add(id(base_name(n.func.value)))
        elif isinstance(n, ast.Compare):
            for op, right in zip(n.ops, n.comparators):
                if not isinstance(op, (ast.In, ast.NotIn)):
                    continue
                name, depth = base_of(right)
                if name in roots:
                    sites.append({"node": n, "kind": "membership", "root": name,
                                  "depth": depth + 1, "key": const_str(n.left),
                                  "negative": isinstance(op, ast.NotIn)})
                    chain_roots.add(id(base_name(right)))
        elif isinstance(n, (ast.For, ast.AsyncFor)):
            name, depth = base_of(n.iter)
            if name in roots:
                sites.append({"node": n, "kind": "iteration", "root": name,
                              "depth": depth + 1, "key": None})
        elif isinstance(n, ast.Delete):
            for t in n.targets:
                if isinstance(t, ast.Subscript):
                    name, depth = base_of(t.value)
                    if name in roots:
                        chain_roots.add(id(base_name(t.value)))
    bare = []
    for n in scope:
        if getattr(n, "lineno", None) != line or not isinstance(n, ast.Name):
            continue
        if n.id in roots and n.id and id(n) not in chain_roots:
            bare.append({"node": n, "kind": "bare_name", "root": n.id, "depth": 0,
                         "key": None})
    for n in scope:
        if getattr(n, "lineno", None) != line or not isinstance(n, ast.Call):
            continue
        if not isinstance(n.func, ast.Name) or n.func.id not in BARE_CALLS:
            continue
        for a in n.args:
            name, depth = base_of(a)
            if name in roots:
                bare.append({"node": n, "kind": "container_call", "root": name,
                             "depth": depth, "key": n.func.id})
    out = sites + bare
    out.sort(key=lambda s: (getattr(s["node"], "col_offset", -1), s["kind"]))
    return out


def base_name(node):
    cur = node
    for _ in range(64):
        if isinstance(cur, ast.Name):
            return cur
        if isinstance(cur, (ast.Subscript, ast.Attribute)):
            cur = cur.value
        elif isinstance(cur, ast.Call):
            cur = cur.func
        else:
            return None
    return None


def classify(site, key, recognised_ids):
    """The class of one access site for the row's key."""
    if id(site["node"]) in recognised_ids:
        return R_KEY
    if site["kind"] in ("bare_name", "container_call", "iteration"):
        return R_CONTAINER
    if site["depth"] > 1:
        return R_BELOW
    if site["kind"] == "subscript":
        ctx = site.get("ctx")
        if ctx == "store":
            return R_WRITE if site["depth"] == 1 else R_BELOW
        if ctx == "del":
            if site["key"] is None:
                return R_COMPUTED
            return R_UNNAMED if site["key"] == key else R_OTHER
        if site["key"] is None:
            return R_COMPUTED
        return R_KEY if site["key"] == key else R_OTHER
    if site["kind"] == "membership":
        if site["key"] is None:
            return R_COMPUTED
        return R_UNNAMED if site["key"] == key else R_OTHER
    if site["kind"] == "call":
        attr = site["attr"]
        if attr == "get":
            if site["key"] is None:
                return R_CONTAINER    # .get() with no argument is a container call
            return R_OTHER if site["key"] != key else R_UNNAMED
        if attr in CONTAINER_ATTRS:
            return R_CONTAINER
        if attr in ENTRY_CALL_ATTRS:
            if site["key"] is None:
                return R_COMPUTED
            return R_UNNAMED if site["key"] == key else R_OTHER
        return R_CONTAINER            # any other method call is not an entry read here
    return R_CONTAINER


def module_tree(root, cache, module):
    if module not in cache:
        try:
            src = io.open(os.path.join(root, module), encoding="utf-8", errors="replace").read()
            cache[module] = ast.parse(src)
        except (SyntaxError, ValueError, OSError):
            cache[module] = None
    return cache[module]


def measure(root=ROOT):
    source = load_source(root)
    lines = counted_lines(source)
    cache = {}
    rows = []
    unresolvable = 0
    for c in lines:
        tree = module_tree(root, cache, c["module"])
        fn = None
        if tree is not None:
            fn = e623.innermost(function_nodes(tree), {"function": c["function"],
                                                       "line": c["dead_line"]})
        if fn is None:
            unresolvable += 1
            rows.append(dict(c, receiver=None, aliases=[], accesses=[], recognised_reads_on_the_line=0))
            continue
        scope = e623.own_scope(fn)
        reads = e623.key_reads(scope, c["key"])
        on_line = [n for n in reads if n.lineno == c["read_line"]]
        receiver = None
        for n in on_line:
            if isinstance(n, ast.Subscript):
                receiver, _ = base_of(n.value)
            elif isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
                receiver, _ = base_of(n.func.value)
            if receiver:
                break
        receiver = resolve_root(scope, receiver)
        aliases = sorted(aliases_of(scope, receiver))
        roots = set(aliases) | ({receiver} if receiver else set())
        recognised_ids = {id(n) for n in reads}
        sites = access_sites(scope, c["read_line"], roots) if roots else []
        accesses = []
        for s in sites:
            form = classify(s, c["key"], recognised_ids)
            accesses.append({
                "form": form,
                "kind": s["kind"],
                "root": s["root"],
                "depth": s["depth"],
                "key": s["key"],
                "column": getattr(s["node"], "col_offset", None),
                "could_force_a_second_read": COULD_FORCE[form],
            })
        r = dict(c)
        r["receiver"] = receiver
        r["aliases"] = aliases
        r["recognised_reads_on_the_line"] = len(on_line)
        r["accesses"] = accesses
        rows.append(r)
    counts = counts_of(rows, source, unresolvable)
    m = {
        "source_face": SOURCE_FACE,
        "population_source": "the counted read lines E632 published in %s (one row per counted read "
                             "line)" % SOURCE_FACE,
        "method": "re-parse each module holding a counted read line, resolve the function that spans "
                  "the dead line, resolve the receiver of the counted read, follow one hop of local "
                  "aliasing, then classify every other access of that receiver that starts on the "
                  "same physical line by whether it reads this key without producing a read node",
        "forms": {f: COULD_FORCE[f] for f in FORMS},
        "counts": counts,
        "rows": rows,
        "limits": [
            "the receiver is identified by its leftmost name, so `a[b]['k']` and `a['k']` share a "
            "receiver -- depth is published on every access so the reader can separate them",
            "an access that starts on a neighbouring line belongs to that line's count, not this one "
            "(the claim being priced is E632's line-level one)",
            "aliasing is followed one hop inside the function body only: an alias passed in as a "
            "parameter, stored on an object or built by a comprehension is not followed",
            "a computed key at the receiver's own level reads *some* key and cannot be decided as "
            "this key or another one, so it is published as its own class and never folded into the "
            "same-key count",
            "`.items()/.keys()/.values()` iterate the container; they read entries but produce no "
            "single-key read node, so they are classed container-level and not as same-key reads",
        ],
    }
    m["verdict"] = derive_verdict(m)
    m["answer"] = answer_of(m)
    return m


def counts_of(rows, source=None, unresolvable=0):
    accesses = [a for r in rows for a in r["accesses"]]
    c = {
        "counted_read_lines": len(rows),
        "lines_with_a_resolved_receiver": sum(1 for r in rows if r.get("receiver")),
        "lines_that_do_not_resolve": sum(1 for r in rows if not r.get("receiver")),
        "modules_that_could_not_be_re_parsed": unresolvable,
        "receiver_with_a_local_alias": sum(1 for r in rows if r.get("aliases")),
        "accesses_to_a_counted_line_receiver": len(accesses),
        "lines_carrying_an_other_access_of_the_receiver": sum(
            1 for r in rows if any(a["form"] != R_KEY for a in r["accesses"])),
        "recognised_reads_re_derived": sum(r["recognised_reads_on_the_line"] for r in rows),
        "unrecognised_entry_reads_of_the_key": sum(1 for a in accesses if a["form"] == R_UNNAMED),
        "lines_carrying_an_unrecognised_entry_read": sum(
            1 for r in rows if any(a["form"] == R_UNNAMED for a in r["accesses"])),
        "computed_key_reads_at_the_receivers_own_level": sum(
            1 for a in accesses if a["form"] == R_COMPUTED),
        "different_key_reads": sum(1 for a in accesses if a["form"] == R_OTHER),
        "reads_below_the_receiver": sum(1 for a in accesses if a["form"] == R_BELOW),
        "container_level_accesses": sum(1 for a in accesses if a["form"] == R_CONTAINER),
    }
    for f in FORMS:
        c["form_" + f] = sum(1 for a in accesses if a["form"] == f)
    if source is not None:
        srows = source.get("rows") or []
        c["e632_published_rows"] = len(srows)
        c["e632_published_read_nodes"] = sum(int(r.get("read_nodes_on_the_line") or 0)
                                             for r in srows)
    return c


def derive_verdict(m):
    c = m["counts"]
    if c["lines_that_do_not_resolve"] or c["modules_that_could_not_be_re_parsed"]:
        return ("%d_of_%d_counted_read_lines_do_not_resolve_to_a_receiver_so_the_form_census_"
                "cannot_be_priced"
                % (c["lines_that_do_not_resolve"], c["counted_read_lines"]))
    if c["unrecognised_entry_reads_of_the_key"] > 0:
        return ("%d_of_%d_counted_read_lines_carry_%d_entry_read(s)_of_the_same_key_that_produce_no_"
                "read_node_so_E632_undercounts_the_reads_on_those_lines"
                % (c["lines_carrying_an_unrecognised_entry_read"], c["counted_read_lines"],
                   c["unrecognised_entry_reads_of_the_key"]))
    if c["recognised_reads_re_derived"] != c.get("e632_published_read_nodes"):
        return ("the_recognised_reads_re_derived_here_do_not_match_E632_read_node_total_so_the_"
                "census_prices_a_different_population")
    return ("no_counted_read_line_names_this_key_outside_the_classifier_so_the_node_count_E632_"
            "published_stands")


def answer_of(m):
    c = m["counts"]
    return ("Of the %d counted read line(s) E632 published, %d resolve to a receiver; that receiver "
            "carries %d other access(es) on those lines, of which %d read this key with no read node "
            "(%d line(s)), %d read a computed key at the receiver's own level and %d read a different "
            "named key. %d alias(es) were followed one hop."
            % (c["counted_read_lines"], c["lines_with_a_resolved_receiver"],
               c["accesses_to_a_counted_line_receiver"],
               c["unrecognised_entry_reads_of_the_key"],
               c["lines_carrying_an_unrecognised_entry_read"],
               c["computed_key_reads_at_the_receivers_own_level"],
               c["different_key_reads"], c["receiver_with_a_local_alias"]))


# ---------------------------------------------------------------- face guard
def face_problems(face):
    p = []
    rows = face.get("rows") or []
    c = face.get("counts") or {}
    accesses = [a for r in rows for a in (r.get("accesses") or [])]
    for r in rows:
        name = (r.get("module") or "").split("/")[-1]
        if name in SELF_PARTS:
            p.append("this study lists itself as a population row: %s" % name)
        for a in (r.get("accesses") or []):
            f = a.get("form")
            if f not in FORMS:
                p.append("row %r publishes an unknown form %r" % (r.get("read_line"), f))
                continue
            if a.get("could_force_a_second_read") is not COULD_FORCE[f]:
                p.append("row %r form %s publishes could_force=%r, the table says %r"
                         % (r.get("read_line"), f, a.get("could_force_a_second_read"),
                            COULD_FORCE[f]))
            if f == R_UNNAMED and a.get("depth") != 1:
                p.append("row %r classes a depth-%r access as an entry read"
                         % (r.get("read_line"), a.get("depth")))
            if f == R_OTHER and a.get("key") is not None and a.get("key") == r.get("key"):
                p.append("row %r classes its own key as a different key" % (r.get("read_line"),))
    want = counts_of(rows)
    for k, v in want.items():
        if k in ("e632_published_rows", "e632_published_read_nodes"):
            continue
        if c.get(k) != v:
            p.append("counts.%s does not re-derive (%r vs %r)" % (k, c.get(k), v))
    if c.get("e632_published_read_nodes") is not None:
        derived = derive_verdict({"counts": c})
        if face.get("verdict") != derived:
            p.append("the published verdict %r is not what the table forces (%r)"
                     % (face.get("verdict"), derived))
    if face.get("forms") != {f: COULD_FORCE[f] for f in FORMS}:
        p.append("the face's form table is not the module's")
    if not rows:
        p.append("the face publishes no row at all")
    return p


def face_from(m):
    face = {
        "study": STUDY,
        "script": "scripts/e633_read_forms.py",
        "card": "E633",
        "evidence_cutoff": TODAY,
        "dept": "research+engineering",
        "method": m["method"],
        "population_source": m["population_source"],
        "source_face": m["source_face"],
        "forms": m["forms"],
        "counts": m["counts"],
        "rows": m["rows"],
        "limits": m["limits"],
        "verdict": m["verdict"],
        "answer": m["answer"],
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
FIXTURE = '''\
def plain(m):
    a = m["k"]
    return a


def membership(m):
    b = m["k"] if "k" in m else None
    return b


def getter(m):
    c = m.get("k")
    return c


def computed(m, k2):
    d = m[k2]
    return d


def other_key(m):
    e = m["j"]
    return e


def alias(m):
    mm = m
    f = mm["k"]
    return f


def deleted(m):
    del m["k"]


def deep(m):
    g = m["k"]["x"]
    return g


def walk(m):
    out = []
    for kk in m:
        out.append(kk)
    return out


def sized(m):
    return len(m)
'''


def _rows_from_fixture():
    tree = ast.parse(FIXTURE)
    fns = function_nodes(tree)
    out = []
    for fn in fns:
        scope = e623.own_scope(fn)
        key = "k"
        reads = e623.key_reads(scope, key)
        lines = sorted({getattr(n, "lineno", None) for n in scope} - {None})
        for line in lines:
            on_line = [n for n in reads if n.lineno == line]
            receiver = None
            for n in on_line:
                if isinstance(n, ast.Subscript):
                    receiver, _ = base_of(n.value)
                elif isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
                    receiver, _ = base_of(n.func.value)
                if receiver:
                    break
            if receiver is None:
                # a line with no recognised read: the receiver is a name that is not a binding
                # target on that line, preferring one that actually appears as the base of an
                # access on it (a bare argument name is not the object being read)
                targets = {id(t) for n in scope if isinstance(n, ast.Assign) and n.lineno == line
                           for t in n.targets if isinstance(t, ast.Name)}
                bases = set()
                for n in scope:
                    if getattr(n, "lineno", None) != line:
                        continue
                    if isinstance(n, ast.Subscript):
                        bases.add(base_of(n.value)[0])
                    elif isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
                        bases.add(base_of(n.func.value)[0])
                    elif isinstance(n, ast.Compare):
                        for op, right in zip(n.ops, n.comparators):
                            if isinstance(op, (ast.In, ast.NotIn)):
                                bases.add(base_of(right)[0])
                cands = [n for n in scope
                         if isinstance(n, ast.Name) and n.lineno == line and id(n) not in targets]
                pick = next((c.id for c in cands if c.id in bases), None)
                receiver = pick if pick else (cands[0].id if cands else None)
            receiver = resolve_root(scope, receiver)
            aliases = sorted(aliases_of(scope, receiver))
            roots = set(aliases) | ({receiver} if receiver else set())
            recognised_ids = {id(n) for n in reads}
            acc = []
            for s in (access_sites(scope, line, roots) if roots else []):
                form = classify(s, key, recognised_ids)
                acc.append({"form": form, "kind": s["kind"], "depth": s["depth"],
                            "key": s["key"], "could_force_a_second_read": COULD_FORCE[form]})
            if not acc and not on_line:
                continue          # a line with neither a read nor an access is not a population row
            if receiver is None:
                out.append({"module": "scripts/fx.py", "function": fn.name,
                            "dead_line": fn.lineno, "key": key, "read_line": line,
                            "receiver": None, "aliases": [], "accesses": acc,
                            "recognised_reads_on_the_line": len(on_line),
                            "is_a_duplicate_row": False})
                continue
            out.append({"module": "scripts/fx.py", "function": fn.name, "dead_line": fn.lineno,
                        "key": key, "read_line": line, "receiver": receiver,
                        "aliases": aliases, "recognised_reads_on_the_line": len(on_line),
                        "accesses": acc, "is_a_duplicate_row": False})
    return out


def selftest():
    legs = []
    rows = _rows_from_fixture()
    by_fn = {}
    for r in rows:
        by_fn.setdefault(r["function"], []).append(r)
    fix_lines = FIXTURE.splitlines()

    def line_of(text):
        return next(i + 1 for i, ln in enumerate(fix_lines) if text in ln)

    def forms_at(text):
        ln = line_of(text)
        return [a["form"] for r in rows if r["read_line"] == ln for a in r["accesses"]]

    def row_at(text):
        ln = line_of(text)
        return next(r for r in rows if r["read_line"] == ln)

    def forms(fn):
        return [a["form"] for r in by_fn.get(fn, []) for a in r["accesses"]]

    legs.append(("a plain read is the only access on its line",
                 forms_at('a = m["k"]') == [R_KEY]))
    legs.append(("a membership test on the same line is an unnamed entry read",
                 R_UNNAMED in forms_at('b = m["k"] if')))
    legs.append(("a .get with a keyword argument is counted as a recognised read",
                 forms_at('c = m.get("k")') == [R_KEY]))
    legs.append(("an expression key at the receiver's own level is the computed class",
                 R_COMPUTED in forms_at('d = m[k2]')))
    legs.append(("a different string key is its own class",
                 forms_at('e = m["j"]') == [R_OTHER]))
    legs.append(("a local alias makes the alias's subscript an access of the receiver",
                 row_at('f = mm["k"]')["receiver"] == "m"
                 and "mm" in row_at('f = mm["k"]')["aliases"]
                 and R_KEY in forms_at('f = mm["k"]')))
    legs.append(("del d['k'] reads the key without producing a read node",
                 R_UNNAMED in forms_at('del m["k"]')))
    legs.append(("a two-step chain is below the receiver, not a second read of the key",
                 R_BELOW in forms_at('g = m["k"]["x"]')
                 and R_KEY in forms_at('g = m["k"]["x"]')))
    legs.append(("iterating the container is container level",
                 R_CONTAINER in forms_at('for kk in m:')))
    legs.append(("len(m) is container level", R_CONTAINER in forms_at('return len(m)')))
    legs.append(("every published could_force flag matches the form table",
                 all(a["could_force_a_second_read"] is COULD_FORCE[a["form"]]
                     for r in rows for a in r["accesses"])))

    c = counts_of(rows)
    c["e632_published_rows"] = len(rows)
    c["e632_published_read_nodes"] = c["recognised_reads_re_derived"]
    legs.append(("counts.counted_read_lines", c["counted_read_lines"] == len(rows)))
    legs.append(("counts.unrecognised_entry_reads_of_the_key counts both the membership and the del",
                 c["unrecognised_entry_reads_of_the_key"] == 2))
    legs.append(("counts.computed_key_reads", c["computed_key_reads_at_the_receivers_own_level"] >= 1))
    legs.append(("counts.form table re-adds to the access total",
                 sum(c["form_" + f] for f in FORMS) == c["accesses_to_a_counted_line_receiver"]))
    v = derive_verdict({"counts": c})
    legs.append(("the verdict names the undercount when a same-key read is unnamed",
                 "undercounts_the_reads_on_those_lines" in v))
    c2 = dict(c)
    c2["unrecognised_entry_reads_of_the_key"] = 0
    c2["lines_carrying_an_unrecognised_entry_read"] = 0
    c2["e632_published_read_nodes"] = c["recognised_reads_re_derived"]
    c2["form_" + R_UNNAMED] = 0
    c2["accesses_to_a_counted_line_receiver"] -= 2
    legs.append(("with nothing unnamed the verdict says the node count stands",
                 "stands" in derive_verdict({"counts": c2})))
    c3 = dict(c2)
    c3["e632_published_read_nodes"] = c2["recognised_reads_re_derived"] + 1
    legs.append(("a population that differs from E632's refuses the claim",
                 "prices_a_different_population" in derive_verdict({"counts": c3})))
    c4 = dict(c2)
    c4["lines_that_do_not_resolve"] = 1
    legs.append(("an unresolved receiver refuses to price the census",
                 "cannot_be_priced" in derive_verdict({"counts": c4})))

    face = {"study": STUDY, "rows": rows, "counts": c, "verdict": v,
            "forms": {f: COULD_FORCE[f] for f in FORMS}}
    legs.append(("face_problems accepts the fixture", face_problems(face) == []))
    bad = json.loads(json.dumps(face))
    bad["counts"]["form_" + R_UNNAMED] = 0
    legs.append(("face_problems catches a tampered form count", bool(face_problems(bad))))
    bad2 = json.loads(json.dumps(face))
    _idx = next(i for i, r in enumerate(bad2["rows"]) if r.get("accesses"))
    bad2["rows"][_idx]["accesses"][0]["could_force_a_second_read"] = True
    legs.append(("face_problems catches a could_force flag that contradicts the table",
                 bool(face_problems(bad2))))
    bad3 = json.loads(json.dumps(face))
    bad3["verdict"] = "other"
    legs.append(("face_problems catches a verdict the table does not force",
                 bool(face_problems(bad3))))
    bad4 = json.loads(json.dumps(face))
    bad4["rows"][0]["module"] = "scripts/e633_read_forms.py"
    legs.append(("face_problems catches this study listing itself", bool(face_problems(bad4))))

    # live arms
    try:
        live, problems = build(root=ROOT)
        legs.append(("the published face builds with no problems", problems == []))
        legs.append(("the population is E632's counted read lines",
                     live["counts"]["counted_read_lines"] ==
                     len(load_source(ROOT).get("rows") or [])))
        legs.append(("the recognised reads re-derive E632's node total",
                     live["counts"]["recognised_reads_re_derived"] ==
                     live["counts"]["e632_published_read_nodes"]))
        legs.append(("every counted line resolves to a receiver",
                     live["counts"]["lines_that_do_not_resolve"] == 0))
        live2, problems2 = build(root=ROOT)
        legs.append(("the build is deterministic",
                     json.dumps(live, sort_keys=True) == json.dumps(live2, sort_keys=True)
                     and problems2 == problems))
    except Exception as exc:  # noqa: BLE001
        legs.append(("live build raised: %r" % (exc,), False))

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
        _, problems = build(root=ROOT)
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
    print("lines=%d receivers=%d accesses=%d unnamed=%d computed=%d other_key=%d below=%d "
          "container=%d recognised=%d"
          % (c["counted_read_lines"], c["lines_with_a_resolved_receiver"],
             c["accesses_to_a_counted_line_receiver"],
             c["unrecognised_entry_reads_of_the_key"],
             c["computed_key_reads_at_the_receivers_own_level"],
             c["different_key_reads"], c["reads_below_the_receiver"],
             c["container_level_accesses"], c["recognised_reads_re_derived"]))
    print("verdict=" + face["verdict"])
    print("answer=" + face["answer"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))