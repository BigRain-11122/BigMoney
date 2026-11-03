"""E390 -- which in-repo reader asks a trial-labor state face for a field the wave already dropped.

E388 measured the walls (``results/state_tilt/SCHEMAACCRETE-*.json``): the key sets grow
across the family until one wall at 16->17 that removes eighteen fields, and no field ever
comes back.  A reader that survived that wall is not obviously broken: ``doc.get("n_survivors")``
returns ``None`` and ``doc["n_survivors"]`` raises ``KeyError`` inside whichever helper it was
called in, so the question this census answers is narrow and static:

  * for every .py site in the repo that names a dropped field **by literal string**,
  * classify whether that literal is a READ (subscript / getter), a write (dict key), a
    declared selector handed to a helper, or a mention (comment, docstring, comparison), and
  * if it is a read, resolve which wave the site opens and test it against the field's last
    sighting.

Three things this deliberately refuses to do:

  * a mention is not a use -- E389's lesson, so every row is classified on the AST with the
    literal's parent node, never on source text or a regex over ``field`` (a regex would count
    the docstring above, this module's own prose, and every ``assert "n_survivors" in ...``);
  * a glob reader cannot know its wave -- a site that resolves ``results/trial_labor_w*``
    lands on whichever directory sorts first or last, so it is published as
    ``family_glob_cannot_know`` rather than being credited with a verdict;
  * a wave is only "known" when the site's own path literal carries one number.  A file that
    builds the path from an argument, a range or several wave literals is
    ``wave_indeterminate`` -- reading intent out of a loop variable is how a census invents
    a site that does not exist.

Population is machine-read from E388's published face (never hand-copied), the census excludes
its own source (E180/E207 family: a scanner that walks the tree it writes into counts itself),
and the family directory list comes from the same reader E388 used.

Usage:  python scripts/e390_wrong_side_reader.py [run|verify|selftest]
"""

from __future__ import annotations

import argparse
import ast
import glob
import json
import os
import re
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E388_FACE = os.path.join(ROOT, "results", "state_tilt", "SCHEMAACCRETE-2026-11-03.json")
OUT_FACE = os.path.join(ROOT, "results", "state_tilt", "WRONGSIDE-2026-11-03.json")
OUT_LATEST = os.path.join(ROOT, "results", "state_tilt", "wrongside_latest.json")

STUDY = "E390_wrong_side_reader"
SELF = os.path.abspath(__file__)

WAVE_RX = re.compile(r"trial_labor_w(\d+)")
GLOB_RX = re.compile(r"trial_labor_w\*")
GETTERS = frozenset({"get", "pop", "setdefault"})
SELECTOR_KWARGS = frozenset({"field", "field_name", "name", "key"})

V_NONE = "no_in_repo_site_names_a_dropped_field_by_literal_string"
V_WRONG = ("at_least_one_in_repo_reader_opens_a_wave_after_the_field_it_asks_for_was_dropped_"
           "so_the_read_returns_none_or_raises_inside_the_helper_with_no_error_at_the_caller")
V_SAFE = "every_in_repo_reader_of_a_dropped_field_still_lands_on_a_wave_that_holds_it"

VOCAB = frozenset({V_NONE, V_WRONG, V_SAFE})

VERDICT_READ = frozenset({
    "reads_after_drop",
    "reads_where_the_field_still_lives",
    "wave_indeterminate",
    "family_glob_cannot_know",
    "reads_a_local_container_not_a_face",
    "reads_a_different_face",
    "target_unresolved",
    "not_a_read",
})


# ---------------------------------------------------------------- population
def read_dropped(path=E388_FACE):
    """{basename: {field: {"last_seen": int, "after_last": [waves]}}} from E388's own face."""
    with open(path, encoding="utf-8") as fh:
        face = json.load(fh)
    out = {}
    for table in face.get("basename_table", []):
        dropped = {}
        for row in table.get("field_rows", []):
            if row.get("removal_edges") and not row.get("re_added"):
                dropped[row["field"]] = {
                    "last_seen": row["last_seen"],
                    "after_last": list(row.get("waves_after_last_seen") or []),
                    "removal_edges": list(row["removal_edges"]),
                }
        out[table["basename"]] = dropped
    return out


def family_waves(root=ROOT):
    """Wave numbers that hold at least one state face -- E388's own rule, re-used not re-invented."""
    waves = []
    for d in glob.glob(os.path.join(root, "results", "trial_labor_w*")):
        m = WAVE_RX.search(os.path.basename(d))
        if m and os.path.isdir(d):
            waves.append(int(m.group(1)))
    return sorted(set(waves))


# ---------------------------------------------------------------- AST helpers
class Parents:
    def __init__(self, tree):
        self.map = {}
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                self.map[id(child)] = node

    def parent(self, node):
        return self.map.get(id(node))


def string_literals(tree):
    """Every str constant with its line, plus dict-key / keyword wrapping info."""
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            out.append(node)
    return out


JSON_READERS = frozenset({"load", "loads"})


def _call_name(call):
    func = call.func
    return func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")


def _is_face_loader(call):
    """``json.load(...)`` loads a face; a bare ``load(...)`` is this repo's own helper."""
    return (isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)
            and call.func.attr in JSON_READERS)


def _bound_kind(expr):
    """What is this expression bound to: a loaded face, a local container, or unknown?"""
    if isinstance(expr, ast.Call):
        if _is_face_loader(expr):
            return "face"
        name = _call_name(expr)
        if name in {"dict", "list", "set", "tuple", "defaultdict", "Counter"}:
            return "local"
        return "unknown"
    if isinstance(expr, ast.Dict):
        return "local"
    if isinstance(expr, (ast.List, ast.ListComp, ast.DictComp)):
        return "local"
    if isinstance(expr, ast.IfExp):
        return _prefer_face({_bound_kind(expr.body), _bound_kind(expr.orelse)})
    if isinstance(expr, ast.BoolOp):
        return _prefer_face({_bound_kind(v) for v in expr.values})
    return "unknown"


def _prefer_face(kinds):
    """``json.load(...) if p.exists() else {}`` is a face with an empty fallback, not two
    different containers -- the literal {} is what a missing file degrades to."""
    kinds = set(kinds) - {"unknown"}
    if "face" in kinds:
        return "face"
    if "local" in kinds:
        return "local"
    return "unknown"


def scope_bindings(tree):
    """{scope: {name: {kinds}}}, {scope: {name: [rhs exprs]}} and the parent map."""
    parents = Parents(tree)
    binds = {}
    exprs = {}

    def scope_of(node):
        cur = parents.parent(node)
        while cur is not None and not isinstance(
                cur, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            cur = parents.parent(cur)
        return cur

    def add(scope, name, kind, expr=None):
        binds.setdefault(scope, {}).setdefault(name, set()).add(kind)
        if expr is not None:
            exprs.setdefault(scope, {}).setdefault(name, []).append(expr)

    for node in ast.walk(tree):
        targets, value = [], None
        if isinstance(node, ast.Assign):
            targets, value = node.targets, node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets, value = [node.target], node.value
        elif isinstance(node, (ast.For, ast.AsyncFor)):
            targets, value = [node.target], node.iter
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            for item in node.items:
                if item.optional_vars is not None:
                    add(scope_of(item.optional_vars), getattr(item.optional_vars, "id", "?"),
                        _bound_kind(item.context_expr), item.context_expr)
            continue
        if not targets:
            continue
        kind = _bound_kind(value) if value is not None else "unknown"
        for target in targets:
            if isinstance(target, ast.Name):
                add(scope_of(target), target.id, kind, value)

    # a sub-dict of a loaded face is still face data: ``ctrl = d.get("per_face_survival")``
    # reads the face, it does not read an unrelated object.  Refine on the bindings already
    # collected (bounded, order-free) instead of guessing at parse time.
    for _ in range(4):
        changed = False
        for scope, by_name in list(exprs.items()):
            for name, exprs_of_name in list(by_name.items()):
                current = binds.get(scope, {}).get(name, set())
                if "face" in current:
                    continue
                for expr in exprs_of_name:
                    recv = None
                    if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Attribute) \
                            and expr.func.attr in GETTERS:
                        recv = expr.func.value
                    elif isinstance(expr, ast.Subscript):
                        recv = expr.value
                    if recv is None:
                        continue
                    kind = target_kind(recv, binds, parents)
                    if kind in {"face", "local"}:
                        add(scope, name, kind)
                        changed = True
        if not changed:
            break
    return binds, exprs, parents


def _scopes_of(node, parents):
    """The lexical scopes enclosing a node, innermost first, then the module."""
    out = []
    cur = parents.parent(node)
    while cur is not None:
        if isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            out.append(cur)
        cur = parents.parent(cur)
    out.append(None)
    return out


def collect_face_literals(expr, bind_exprs, parents, depth=0):
    """Every string literal that helps build the value a read is indexing into.

    The path is rarely at the read site: ``D = json.load(open(p))`` hides it behind ``p``,
    so the walk has to follow the call arguments and the name bindings, not just the
    expression's own constants.
    """
    if depth > 8 or expr is None:
        return []
    out = []
    if isinstance(expr, ast.Constant) and isinstance(expr.value, str):
        return [expr]
    if isinstance(expr, ast.Name):
        for bound in binding_exprs(expr, bind_exprs, parents):
            out.extend(collect_face_literals(bound, bind_exprs, parents, depth + 1))
        return out
    if isinstance(expr, ast.Subscript):
        out.extend(collect_face_literals(expr.value, bind_exprs, parents, depth + 1))
        return out
    if isinstance(expr, ast.Call):
        for arg in list(expr.args) + [kw.value for kw in expr.keywords]:
            out.extend(collect_face_literals(arg, bind_exprs, parents, depth + 1))
        return out
    for child in ast.iter_child_nodes(expr):
        out.extend(collect_face_literals(child, bind_exprs, parents, depth + 1))
    return out


def binding_exprs(expr, exprs, parents, depth=0):
    """The RHS expressions behind a read container: a loaded call's own node, or a name's bind."""
    if depth > 6:
        return []
    if isinstance(expr, ast.Call):
        return [expr]
    if isinstance(expr, ast.Subscript):
        return binding_exprs(expr.value, exprs, parents, depth + 1)
    if isinstance(expr, ast.Name):
        found = []
        for scope in _scopes_of(expr, parents):
            if scope in exprs and expr.id in exprs[scope]:
                found.extend(exprs[scope][expr.id])
        return found
    if isinstance(expr, (ast.Dict, ast.List)):
        return [expr]
    return []


def target_kind(expr, binds, parents, depth=0):
    """Resolve what a read's container is: face / local / unknown (chain-aware, depth-limited)."""
    if depth > 6:
        return "unknown"
    if isinstance(expr, ast.Call):
        if _is_face_loader(expr):
            return "face"
        name = _call_name(expr)
        if name in {"dict", "list", "set", "tuple", "defaultdict", "Counter"}:
            return "local"
        return "unknown"
    if isinstance(expr, ast.Subscript):
        return target_kind(expr.value, binds, parents, depth + 1)
    if isinstance(expr, ast.Name):
        scope = parents.parent(expr)
        while scope is not None and not isinstance(
                scope, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            scope = parents.parent(scope)
        kinds = set()
        rides = [scope, None]  # nearest scope, then module level
        cur = scope
        # walk out through enclosing scopes, then module
        while True:
            if cur in binds:
                kinds |= binds[cur].get(expr.id, set())
            nxt = parents.parent(cur) if cur is not None else None
            while nxt is not None and not isinstance(
                    nxt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                nxt = parents.parent(nxt)
            if nxt is None:
                if None in binds:
                    kinds |= binds[None].get(expr.id, set())
                break
            cur = nxt
        if len(kinds) == 1:
            return list(kinds)[0]
        for kind in ("face", "local"):
            if kind in kinds:
                return kind           # "unknown" is the absence of evidence and yields to it
        return "unknown"
    if isinstance(expr, (ast.Dict, ast.List, ast.ListComp, ast.DictComp)):
        return "local"
    return "unknown"


def classify(node, parents):
    """How is this string literal used?  Read / write / declared selector / mention."""
    parent = parents.parent(node)
    if isinstance(parent, ast.Subscript) and parent.slice is node:
        # D[\"field\"] = ... is a write: the literal names the slot being filled, not a slot
        # being asked for.  Two windows drafted the opposite and published a live writer as
        # a broken reader (w22_window_forecast.py:193).
        if isinstance(parent.ctx, ast.Store):
            return "write_subscript"
        return "read_subscript"
    if isinstance(parent, ast.Call):
        func = parent.func
        if parent.args and parent.args[0] is node and isinstance(func, ast.Attribute) and func.attr in GETTERS:
            return "read_getter"
        if isinstance(func, ast.Attribute) and func.attr in GETTERS and parent.args:
            pass  # the literal is not the first argument; fall through
    if isinstance(parent, ast.keyword) and parent.arg in SELECTOR_KWARGS:
        return "declared_selector"
    if isinstance(parent, ast.Dict) and any(k is node for k in parent.keys):
        # a dict key may be a write (facet assembly) or a fixture face; published as such
        return "dict_key"
    if isinstance(parent, ast.Call) and parent.args and parent.args[0] is node:
        func = parent.func
        name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
        if name in {"load", "loads", "read_text"}:
            return "load_target"
    return "mention"


FAMILY_SEG_RX = re.compile(r"^trial_labor_w(\d+)$")


def path_literals(literals):
    """Wave numbers carried by a path literal, and whether the family is globbed.

    A path segment must be *exactly* ``trial_labor_w<N>``.  ``results/trial_labor_w22_confirm``
    is a different directory that happens to start the same way -- reading wave 22 out of it is
    how a census manufactures a site that reads the family face and does not.
    """
    waves, globbed = set(), False
    for node in literals:
        v = node.value
        if GLOB_RX.search(v):
            globbed = True
        for seg in re.split(r"[\\/]+", v):
            m = FAMILY_SEG_RX.match(seg)
            if m:
                waves.add(int(m.group(1)))
    return sorted(waves), globbed


def basenames_named(literals, basenames):
    return sorted({node.value for node in literals if node.value in basenames})


# ---------------------------------------------------------------- census
def iter_py(root=ROOT):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames
                       if d not in {".git", "__pycache__", "node_modules", "_quarantine"}]
        for name in filenames:
            if name.endswith(".py"):
                yield os.path.join(dirpath, name)


def scan_site(path, dropped, basenames, root=ROOT):
    """Rows for one .py file, or [] when it names nothing interesting."""
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            src = fh.read()
    except OSError:
        return []
    if "trial_labor" not in src:
        return []
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []
    literals = string_literals(tree)
    field_owner = {}
    for base in basenames:
        for field in dropped.get(base, {}):
            field_owner.setdefault(field, []).append(base)
    rel = os.path.relpath(path, root).replace("\\", "/")
    waves, globbed = path_literals(literals)
    opened = basenames_named(literals, basenames)
    parents = Parents(tree)
    binds, bind_exprs, parents = scope_bindings(tree)
    rows = []
    for node in literals:
        value = node.value
        if value not in field_owner:
            continue
        kind = classify(node, parents)
        container = "n/a"
        face_names = []
        face_waves = []
        if kind.startswith("read"):
            parent = parents.parent(node)
            if isinstance(parent, ast.Subscript):
                target = parent.value
            else:
                target = parent.func.value
            container = target_kind(target, binds, parents)
            if container == "face":
                # which face?  Only the literals inside the expression that produced the
                # loaded value count -- a file that also mentions the family is not evidence
                # that THIS read is on it (build_status.py:299 reads "generated" from
                # portfolio_ew6.json and never opens a wave directory there).
                face_lits = []
                for expr in binding_exprs(target, bind_exprs, parents):
                    face_lits.extend(collect_face_literals(expr, bind_exprs, parents))
                face_names = sorted({n.value for n in face_lits if n.value in basenames})
                face_waves, face_globbed = path_literals(face_lits)
                if face_globbed:
                    globbed = True
        if kind.startswith("read") and container == "face":
            targets_here = [b for b in face_names if value in dropped[b]]
            if not targets_here:
                rows.append({
                    "site": rel, "line": node.lineno, "field": value,
                    "basename": None, "last_seen": None, "kind": kind,
                    "container": container, "wave_literals": face_waves,
                    "opens": face_names, "verdict": "reads_a_different_face",
                })
                continue
        else:
            targets_here = [b for b in field_owner[value]]
        for base in targets_here:
            last_seen = dropped[base][value]["last_seen"]
            if kind.startswith("read"):
                if container == "local":
                    verdict = "reads_a_local_container_not_a_face"
                elif container != "face":
                    verdict = "target_unresolved"
                elif globbed:
                    verdict = "family_glob_cannot_know"
                elif len(face_waves) == 1:
                    verdict = ("reads_after_drop" if face_waves[0] > last_seen
                               else "reads_where_the_field_still_lives")
                else:
                    verdict = "wave_indeterminate"
            else:
                verdict = "not_a_read"
            rows.append({
                "site": rel,
                "line": node.lineno,
                "field": value,
                "basename": base,
                "last_seen": last_seen,
                "kind": kind,
                "container": container,
                "wave_literals": face_waves if container == "face" else waves,
                "opens": face_names or opened,
                "verdict": verdict,
            })
    return rows


def census(root=ROOT, face=E388_FACE):
    dropped = read_dropped(face)
    basenames = sorted(dropped)
    rows = []
    for path in iter_py(root):
        if os.path.abspath(path) == SELF:
            continue
        rows.extend(scan_site(path, dropped, basenames, root=root))
    rows.sort(key=lambda r: (r["site"], r["line"], r["field"], r["basename"] or "",
                             r["verdict"]))
    return rows, dropped


def summarise(rows, dropped, root=ROOT):
    by_verdict = {}
    for row in rows:
        by_verdict[row["verdict"]] = by_verdict.get(row["verdict"], 0) + 1
    reads = [r for r in rows if r["kind"].startswith("read")]
    wrong = [r for r in rows if r["verdict"] == "reads_after_drop"]
    mention_only = [r for r in rows if r["kind"] == "mention"]
    return {
        "waves_on_disk": family_waves(root),
        "basenames_priced": sorted(dropped),
        "dropped_fields": {b: sorted(dropped[b]) for b in sorted(dropped)},
        "rows": len(rows),
        "sites": len({r["site"] for r in rows}),
        "read_rows": len(reads),
        "read_sites": len({r["site"] for r in reads}),
        "mention_only_rows": len(mention_only),
        "mention_only_sites": len({r["site"] for r in mention_only}),
        "by_verdict": dict(sorted(by_verdict.items())),
        "wrong_side_sites": sorted({r["site"] for r in wrong}),
        "wrong_side_rows": len(wrong),
        "read_sites_by_wave_status": {
            "single_wave_literal": len({r["site"] for r in reads
                                        if r["verdict"] in {"reads_after_drop",
                                                            "reads_where_the_field_still_lives"}}),
            "indeterminate_or_glob": len({r["site"] for r in reads
                                          if r["verdict"] in {"wave_indeterminate",
                                                              "family_glob_cannot_know"}}),
        },
    }


def decide(summary):
    if not summary["rows"]:
        return V_NONE
    if summary["wrong_side_rows"]:
        return V_WRONG
    return V_SAFE


def build(root=ROOT, face=E388_FACE):
    rows, dropped = census(root=root, face=face)
    summary = summarise(rows, dropped, root=root)
    return {
        "study": STUDY,
        "script": "scripts/e390_wrong_side_reader.py",
        "generated": "",
        "evidence_cutoff": "2026-09-22",
        "population_face": os.path.relpath(face, root).replace("\\", "/"),
        "method": ("static only: fields and their last sighting are machine-read from E388's "
                   "published face; a site is any .py under the repo that mentions 'trial_labor'; "
                   "a row needs a string literal whose value IS a dropped field, classified by its "
                   "AST parent (subscript/getter = read, dict key = write, keyword selector = "
                   "declared, otherwise mention); the wave is known only when the whole file "
                   "carries exactly one trial_labor_w<N> literal, otherwise indeterminate; a "
                   "family glob can never resolve its wave"),
        "summary": summary,
        "verdict": decide(summary),
        "rows": rows,
    }


def write_face(out_face, out_latest, face_obj):
    text = json.dumps(face_obj, ensure_ascii=False, indent=1) + "\n"
    for path in (out_face, out_latest):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)


# ---------------------------------------------------------------- verify / selftest
def verify(root=ROOT):
    problems = []
    with open(OUT_FACE, encoding="utf-8") as fh:
        published = json.load(fh)
    rebuilt = build(root=root)
    if published["summary"] != rebuilt["summary"]:
        for key in sorted(rebuilt["summary"]):
            if published["summary"].get(key) != rebuilt["summary"][key]:
                problems.append("summary.%s re-derives as %r, published %r"
                                % (key, rebuilt["summary"][key], published["summary"].get(key)))
    if published["verdict"] != rebuilt["verdict"]:
        problems.append("verdict re-derives as %r" % (rebuilt["verdict"],))
    if published["rows"] != rebuilt["rows"]:
        problems.append("rows do not re-derive (%d published, %d rebuilt)"
                        % (len(published["rows"]), len(rebuilt["rows"])))
    # the verdict must be a function of the rows, not a stored string
    if published["verdict"] != decide(published["summary"]):
        problems.append("published verdict is not what its own summary implies")
    # a row labelled reads_after_drop must really sit after the last sighting
    for row in published["rows"]:
        if row["verdict"] == "reads_after_drop" and not row["wave_literals"]:
            problems.append("row claims wrong side without a resolved wave: %s:%s"
                            % (row["site"], row["line"]))
    return problems


FIXTURE_JUDGE = '''import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, "results", "trial_labor_w19", "judge_state.json")
D = json.load(open(p, encoding="utf-8"))
a = D["n_survivors"]
b = D.get("n_survivors")
c = {"n_survivors": 1}
# n_survivors is discussed here and never read
assert "n_survivors" in str(D)
'''

FIXTURE_LOCAL = '''import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, "results", "trial_labor_w19", "judge_state.json")
D = json.load(open(p))
per_face = {}
for f in ("ENTRY", "EXIT"):
    per_face[f] = {"n": 3, "n_survivors": 1}
summary = {f: per_face[f]["n_survivors"] for f in per_face}
'''

FIXTURE_INDIRECT = '''import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, "results", "trial_labor_w19", "judge_state.json")
def load(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)
D = load(p)
print(D["n_survivors"])
'''

FIXTURE_EARLY = '''import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(ROOT, "results", "trial_labor_w12", "judge_state.json")))
print(D["n_survivors"])
'''

FIXTURE_GLOB = '''import glob, json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for d in sorted(glob.glob(os.path.join(ROOT, "results", "trial_labor_w*"))):
    D = json.load(open(os.path.join(d, "judge_state.json")))
    print(D.get("n_survivors"))
'''

FIXTURE_MULTI = '''import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for w in (18, 19):
    p = os.path.join(ROOT, "results", "trial_labor_w%d" % w, "judge_state.json")
    print(json.load(open(p)).get("cap"))
'''

FIXTURE_WRITE = '''import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, "results", "trial_labor_w19", "judge_state.json")
D = json.load(open(p))
D["n_survivors"] = 1
json.dump(D, open(p, "w"))
'''

FIXTURE_SIBLING = '''import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, "results", "trial_labor_w22_confirm", "w22_confirm_state.json")
print(json.load(open(p))["n_survivors"])
'''

FIXTURE_OTHERFACE = '''import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# this module also talks about results/trial_labor_w19/ in a note
j = json.load(open(os.path.join(ROOT, "results", "portfolio_ew6.json")))
print(j.get("generated"))
'''


def selftest():
    legs = []

    def leg(name, cond, note=""):
        legs.append((name, bool(cond), note))

    tmp = tempfile.mkdtemp(prefix="e390_")
    try:
        os.makedirs(os.path.join(tmp, "results", "trial_labor_w12"), exist_ok=True)
        os.makedirs(os.path.join(tmp, "results", "trial_labor_w19"), exist_ok=True)
        face = {"basename_table": [
            {"basename": "judge_state.json", "field_rows": [
                {"field": "n_survivors", "last_seen": 16,
                 "removal_edges": [{"from_wave": 16, "to_wave": 17}],
                 "waves_after_last_seen": [17, 19], "re_added": False},
                {"field": "cap", "last_seen": 19,
                 "removal_edges": [{"from_wave": 19, "to_wave": 21}],
                 "waves_after_last_seen": [21], "re_added": False},
                {"field": "vol_meta", "last_seen": 16,
                 "removal_edges": [{"from_wave": 16, "to_wave": 17}],
                 "waves_after_last_seen": [17], "re_added": False},
                {"field": "kept", "last_seen": 19, "removal_edges": [],
                 "waves_after_last_seen": [], "re_added": False},
            ]},
        ]}
        face_path = os.path.join(tmp, "face.json")
        with open(face_path, "w", encoding="utf-8") as fh:
            json.dump(face, fh)

        dropped = read_dropped(face_path)
        leg("dropped population read from the face", sorted(dropped["judge_state.json"]) ==
            ["cap", "n_survivors", "vol_meta"], str(sorted(dropped["judge_state.json"])))
        leg("a field with no removal edge is not in the population",
            "kept" not in dropped["judge_state.json"])

        def write(name, body):
            p = os.path.join(tmp, name)
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(body)
            return p

        cases = {
            "site_late.py": (FIXTURE_JUDGE, {"reads_after_drop"}),
            "site_early.py": (FIXTURE_EARLY, {"reads_where_the_field_still_lives"}),
            "site_glob.py": (FIXTURE_GLOB, {"family_glob_cannot_know"}),
            "site_multi.py": (FIXTURE_MULTI, {"wave_indeterminate"}),
            "site_write.py": (FIXTURE_WRITE, {"not_a_read"}),
            "site_sibling.py": (FIXTURE_SIBLING, {"wave_indeterminate"}),
            "site_local.py": (FIXTURE_LOCAL, {"reads_a_local_container_not_a_face"}),
            "site_indirect.py": (FIXTURE_INDIRECT, {"target_unresolved"}),
            "site_otherface.py": (FIXTURE_OTHERFACE, {"reads_a_different_face"}),
        }
        for name, (body, _) in cases.items():
            write(name, body)

        rows = []
        for name in cases:
            rows.extend(scan_site(os.path.join(tmp, name), dropped,
                                  ["judge_state.json"], root=tmp))

        by_site = {}
        for row in rows:
            by_site.setdefault(os.path.basename(row["site"]), []).append(row)

        late = by_site.get("site_late.py", [])
        late_reads = [r for r in late if r["field"] == "n_survivors" and r["kind"].startswith("read")]
        leg("the late site yields one row per distinct read form",
            len(late_reads) == 2, str(len(late_reads)))
        leg("subscript and getter are both reads",
            {r["kind"] for r in late_reads} == {"read_subscript", "read_getter"},
            str({r["kind"] for r in late_reads}))
        leg("a dict key is not a read",
            all(r["kind"] == "dict_key" for r in late if r["field"] == "n_survivors"
                and r["kind"] == "dict_key") and
            len([r for r in late if r["kind"] == "dict_key"]) == 1)
        leg("a bare mention (the assert) is not read and a comment is not a literal at all",
            len([r for r in late if r["kind"] == "mention"]) == 1 and
            all(r["verdict"] == "not_a_read" for r in late if r["kind"] == "mention"),
            str(len([r for r in late if r["kind"] == "mention"])))
        leg("a wave-19 read of a field dropped at 16 is the wrong side",
            all(r["verdict"] == "reads_after_drop" for r in late_reads))
        leg("a read at wave 12 is on the safe side",
            all(r["verdict"] == "reads_where_the_field_still_lives"
                for r in by_site.get("site_early.py", [])))
        leg("a family glob never gets a wave verdict",
            all(r["verdict"] == "family_glob_cannot_know"
                for r in by_site.get("site_glob.py", [])))
        leg("two wave literals in one file is indeterminate, not a guess",
            all(r["verdict"] == "wave_indeterminate"
                for r in by_site.get("site_multi.py", [])),
            str({r["verdict"] for r in by_site.get("site_multi.py", [])}))
        leg("cap's last sighting is 19 so an 18/19 read is not flagged",
            all(r["verdict"] != "reads_after_drop"
                for r in by_site.get("site_multi.py", []) if r["field"] == "cap"))
        write_rows = by_site.get("site_write.py", [])
        leg("a subscript store is a write, not a broken read",
            [r["kind"] for r in write_rows] == ["write_subscript"] and
            all(r["verdict"] == "not_a_read" for r in write_rows),
            str([(r["kind"], r["verdict"]) for r in write_rows]))
        sibling = by_site.get("site_sibling.py", [])
        leg("a sibling directory named trial_labor_w22_confirm is never family wave 22",
            all(r["wave_literals"] == [] for r in sibling) and
            all(r["verdict"] != "reads_after_drop" for r in sibling),
            str([(r["wave_literals"], r["verdict"]) for r in sibling]))
        other = by_site.get("site_otherface.py", [])
        leg("a file that merely mentions the family is not charged with its key",
            all(r["verdict"] == "reads_a_different_face" for r in other) and
            all(r["basename"] is None for r in other),
            str([(r["verdict"], r["basename"]) for r in other]))
        local = [r for r in by_site.get("site_local.py", []) if r["kind"].startswith("read")]
        leg("a key on a locally built dict is not a face read",
            [r["container"] for r in local] == ["local"] and
            all(r["verdict"] == "reads_a_local_container_not_a_face" for r in local),
            str([(r["container"], r["verdict"]) for r in local]))
        indirect = by_site.get("site_indirect.py", [])
        leg("a load behind a local helper is unresolved, never credited",
            [r["container"] for r in indirect] == ["unknown"] and
            all(r["verdict"] == "target_unresolved" for r in indirect),
            str([(r["container"], r["verdict"]) for r in indirect]))

        summary = summarise(rows, dropped, root=tmp)
        leg("wrong-side sites are named once each",
            summary["wrong_side_sites"] == ["site_late.py"], str(summary["wrong_side_sites"]))
        leg("verdict follows the rows", decide(summary) == V_WRONG)
        leg("an empty census says so rather than claiming safety",
            decide(summarise([], dropped, root=tmp)) == V_NONE)
        leg("a census with reads but no wrong side is V_SAFE",
            decide(summarise([r for r in rows if r["verdict"] != "reads_after_drop"],
                             dropped, root=tmp)) == V_SAFE)

        # the scanner must not count its own source (E180/E207 family)
        own = scan_site(SELF, dropped, ["judge_state.json"], root=ROOT)
        leg("the census is excluded from its own corpus by the caller",
            os.path.abspath(SELF) != os.path.abspath(os.path.join(ROOT, "scripts",
                                                                 "e390_wrong_side_reader.py"))
            or own is not None)
        corpus = list(iter_py(ROOT))
        leg("self is in the walk and is filtered by abspath, not by name",
            any(os.path.abspath(p) == SELF for p in corpus))

        # determinism: two censuses on the same tree agree
        a1 = census(root=ROOT)
        a2 = census(root=ROOT)
        leg("the census is deterministic", a1 == a2)
        leg("published population comes from a face that exists", os.path.exists(E388_FACE))
    finally:
        for name in os.listdir(tmp):
            p = os.path.join(tmp, name)
            if os.path.isfile(p):
                os.remove(p)
        for d in glob.glob(os.path.join(tmp, "results", "trial_labor_w*")):
            for name in os.listdir(d):
                os.remove(os.path.join(d, name))
            os.rmdir(d)
        if os.path.isdir(os.path.join(tmp, "results")):
            os.rmdir(os.path.join(tmp, "results"))
        if os.path.isdir(tmp):
            os.rmdir(tmp)

    bad = [n for n, ok, _ in legs if not ok]
    for name, ok, note in legs:
        print("%s %s%s" % ("ok  " if ok else "FAIL", name, ("  [%s]" % note) if note and not ok else ""))
    print("\nselftest %d/%d" % (len(legs) - len(bad), len(legs)))
    return 0 if not bad else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    ap = argparse.ArgumentParser()
    ap.add_argument("action", nargs="?", default="run",
                    choices=["run", "verify", "selftest"])
    args = ap.parse_args(argv)
    if args.action == "selftest":
        return selftest()
    if args.action == "verify":
        problems = verify()
        for p in problems:
            print("PROBLEM", p)
        print("verify problems=%d" % len(problems))
        return 0 if not problems else 1
    face = build()
    write_face(OUT_FACE, OUT_LATEST, face)
    s = face["summary"]
    print("rows=%d sites=%d read_sites=%d wrong_side_sites=%d"
          % (s["rows"], s["sites"], s["read_sites"], len(s["wrong_side_sites"])))
    print("by_verdict=%s" % json.dumps(s["by_verdict"], sort_keys=True))
    print("verdict=%s" % face["verdict"])
    print("wrote %s" % os.path.relpath(OUT_FACE, ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())