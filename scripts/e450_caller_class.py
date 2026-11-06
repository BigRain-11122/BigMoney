"""E450: E444 graded every attribute call row against the classes of the module it was ATTRIBUTED
to and found those six modules define no class at all, so the wrapper side is settled.

That leaves the caller side.  If a row's receiver is a name the caller binds, the class it names a
method of is usually defined in the caller's own module -- the row is then a real reader of a
sibling object, and the name index attributed it to the wrong module.  This study asks the caller
side of the same population, and it separates two readings that a careless count would merge:

  reading N (name)    -- the method name is carried by SOME class defined in the caller's file.
                         Cheap, and a coincidence is indistinguishable from a type.
  reading B (binding) -- the receiver is that class: it is assigned a call to a class defined in
                         the caller, or the receiver itself is a constructor call to one, and that
                         class carries the method.  This is the reader the card is asking about.

Both are published.  The population is re-derived live from E444's own stages, and the face pins
itself to E444's published numbers: the row total and the whole receiver distribution must match,
or `verify` refuses.

Usage:
    python scripts/e450_caller_class.py run|verify|check|selftest
"""
from __future__ import annotations

import ast
import io
import json
import os
import sys
from datetime import date

import e429_two_hop_writer as e420
import e437_name_recall as e437
import e439_file_slot_callers as e439
import e440_shared_wrapper_names as e440
import e444_attr_method as e444
import growth_tolerance as gt

ROOT = e420.ROOT
ST = e420.ST
OUTDIR = ST
FACE_NAME = "callerclass_latest.json"
DATED_PREFIX = "CALLERCLASS"
CARD_ID = ("E450-WHICH-BOUND-RECEIVER-NAMES-A-METHOD-OF-A-CLASS-IN-THE-CALLERS-OWN-MODULE")

RECV_SELF = e444.RECV_SELF
RECV_CTOR = e444.RECV_CTOR
RECV_BOUND = e444.RECV_BOUND
RECV_UNBOUND = e444.RECV_UNBOUND
RECV_OTHER = e444.RECV_OTHER
RECV_MISSING = e444.RECV_MISSING
RECV_VOCAB = e444.RECV_VOCAB

# How the receiver name is bound in the caller, when it is a name at all.
BIND_CTOR = "a_name_assigned_a_call_to_a_class_defined_in_the_caller"
BIND_OTHER_CALL = "a_name_assigned_a_call_to_something_that_is_not_a_local_class"
BIND_NOT_A_CALL = "a_name_assigned_something_that_is_not_a_call"
BIND_NEVER = "a_name_never_assigned_in_the_caller_parameter_import_or_loop_target"
BIND_NOT_A_NAME = "the_receiver_is_not_a_name"
BIND_VOCAB = (BIND_CTOR, BIND_OTHER_CALL, BIND_NOT_A_CALL, BIND_NEVER, BIND_NOT_A_NAME)

V_EMPTY = "no_bound_or_constructor_receiver_row_to_grade"
V_ALL_NAME = "every_bound_or_constructor_row_names_a_method_carried_by_a_class_in_the_callers_module"
V_NONE_NAME = ("no_bound_or_constructor_row_names_a_method_carried_by_a_class_in_the_callers_module")
V_SOME_NAME = ("some_bound_or_constructor_rows_name_a_method_carried_by_a_class_in_the_callers_module"
               "_but_a_name_is_not_a_type")
VERDICT_VOCAB = (V_EMPTY, V_ALL_NAME, V_SOME_NAME, V_NONE_NAME)

_VIEW_CACHE: dict[str, dict | None] = {}
_AST_CACHE: dict[str, ast.AST | None] = {}


def _rel(path: str) -> str:
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


def _load(path: str) -> dict:
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _tally(rows: list[dict], key: str) -> dict:
    out = {v: 0 for v in BIND_VOCAB} if key == "binding" else {v: 0 for v in RECV_VOCAB}
    for r in rows:
        out[r[key]] = out.get(r[key], 0) + r["rows"]
    return out


def _collect_calls(node, stack: list, calls: dict, bound: set) -> None:
    """E444's collector, extended to carry the class named by a constructor receiver.

    The receiver KIND comes from e444._receiver_kind, so the two collectors cannot disagree about
    the vocabulary -- if they ever do, the face's receiver-distribution pin fails.
    """
    if isinstance(node, ast.ClassDef):
        stack.append(("class", node.name))
        for child in node.body:
            _collect_calls(child, stack, calls, bound)
        stack.pop()
        return
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        stack.append(("func", node.name))
        for child in node.body:
            _collect_calls(child, stack, calls, bound)
        stack.pop()
        return
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        recv = node.func.value
        kind, name = e444._receiver_kind(recv, bound)
        ctor_class = None
        if isinstance(recv, ast.Call) and isinstance(recv.func, ast.Name):
            ctor_class = recv.func.id
        enclosing = None
        for tag, value in reversed(stack):
            if tag == "class":
                enclosing = value
                break
        calls.setdefault((getattr(node, "lineno", -1), node.func.attr), []).append(
            (kind, name, enclosing, ctor_class))
    for child in ast.iter_child_nodes(node):
        _collect_calls(child, stack, calls, bound)


def _assignments(tree) -> dict[str, list]:
    """name -> every value node assigned to it anywhere in the module (Assign / AnnAssign / with)."""
    out: dict[str, list] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    out.setdefault(target.id, []).append(node.value)
                elif isinstance(target, ast.Tuple):
                    for elt in target.elts:
                        if isinstance(elt, ast.Name):
                            out.setdefault(elt.id, []).append(node.value)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if node.value is not None:
                out.setdefault(node.target.id, []).append(node.value)
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            for item in node.items:
                if item.optional_vars is not None and isinstance(item.optional_vars, ast.Name):
                    out.setdefault(item.optional_vars.id, []).append(item.context_expr)
        elif isinstance(node, ast.For):
            if isinstance(node.target, ast.Name):
                out.setdefault(node.target.id, []).append(node.iter)
    return out


def _tree(rel: str) -> ast.AST | None:
    if rel in _AST_CACHE:
        return _AST_CACHE[rel]
    try:
        src = io.open(os.path.join(ROOT, rel), encoding="utf-8", errors="replace").read()
        tree = ast.parse(src)
    except (OSError, SyntaxError, ValueError):
        tree = None
    _AST_CACHE[rel] = tree
    return tree


def file_view(rel: str) -> dict | None:
    """classes+methods, bindable names, attribute calls and assignments for one caller module."""
    if rel in _VIEW_CACHE:
        return _VIEW_CACHE[rel]
    tree = _tree(rel)
    if tree is None:
        _VIEW_CACHE[rel] = None
        return None
    bound = e444._bound_names(tree)
    calls: dict = {}
    _collect_calls(tree, [], calls, bound)
    view = {"classes": e444._class_index(tree), "bound": bound, "calls": calls,
            "assigns": _assignments(tree)}
    _VIEW_CACHE[rel] = view
    return view


def binding_kind(value_nodes: list, classes: dict[str, set]) -> str:
    """How a receiver name came to hold its value, from the caller's own assignment sites."""
    if not value_nodes:
        return BIND_NEVER
    for value in value_nodes:
        if isinstance(value, ast.Call) and isinstance(value.func, ast.Name) \
                and value.func.id in classes:
            return BIND_CTOR
    if any(isinstance(v, ast.Call) for v in value_nodes):
        return BIND_OTHER_CALL
    return BIND_NOT_A_CALL


def classes_carrying(classes: dict[str, set], method_name: str) -> list[str]:
    return sorted(c for c, methods in classes.items() if method_name in methods)


def grade_caller(view: dict | None, line: int, method_name: str) -> dict:
    """Grade one row on the caller side.

    reading N -- is the method name carried by a class in the caller's file?
    reading B -- is the receiver that class, and does it carry the method?
    """
    out = {
        "located": False,
        "receiver_kind": RECV_MISSING,
        "receiver_name": None,
        "binding": BIND_NOT_A_NAME,
        "classes_carrying_the_name": [],
        "name_hit": False,
        "binding_hit": None,
        "receiver_class": None,
    }
    if not view:
        return out
    seen = view["calls"].get((line, method_name))
    if not seen:
        return out
    kind, name, _enclosing, ctor_class = seen[0]
    classes = view["classes"]
    carrying = classes_carrying(classes, method_name)
    out["located"] = True
    out["receiver_kind"] = kind
    out["receiver_name"] = name
    out["classes_carrying_the_name"] = carrying
    out["name_hit"] = bool(carrying)
    if kind == RECV_CTOR:
        out["receiver_class"] = ctor_class
        out["binding_hit"] = bool(ctor_class in classes and method_name in classes[ctor_class])
        return out
    if kind in (RECV_BOUND, RECV_UNBOUND):
        out["binding"] = binding_kind(view["assigns"].get(name) or [], classes)
        if out["binding"] == BIND_CTOR:
            holders = [v.func.id for v in view["assigns"].get(name) or []
                       if isinstance(v, ast.Call) and isinstance(v.func, ast.Name)
                       and v.func.id in classes]
            out["receiver_class"] = holders[0] if holders else None
            out["binding_hit"] = bool(holders and method_name in classes[holders[0]])
        else:
            out["binding_hit"] = False
        return out
    return out


PIN_GROWTH = "growth_only_superset"
PIN_MOVED = "population_moved_or_shrank"


def population_pin(mine: dict, theirs: dict) -> dict:
    """E455's rule applied to E444's published receiver distribution.

    The corpus gains files every round, so a census re-derived live is a superset of the snapshot
    and exact equality would be a one-round purchase.  What must still hold: no receiver kind may
    LOSE rows, and E444's own distribution must sum to its published row total.  Growth is a fact
    to publish, not a defect to hide.
    """
    per: dict[str, dict] = {}
    for kind in RECV_VOCAB:
        before = int((theirs or {}).get(kind, 0) or 0)
        now = int((mine or {}).get(kind, 0) or 0)
        per[kind] = {"e444": before, "now": now, "delta": now - before}
    lost = sorted(k for k, v in per.items() if v["delta"] < 0)
    return {
        "e444_row_total": sum(v["e444"] for v in per.values()),
        "now_row_total": sum(v["now"] for v in per.values()),
        "delta": sum(v["delta"] for v in per.values()),
        "per_receiver_kind": per,
        "kinds_that_lost_rows": lost,
        "verdict": PIN_MOVED if lost else PIN_GROWTH,
    }


def verdict_for(total: int, name_hit: int, binding_hit: int) -> str:
    """Recomputed from the counts, never carried."""
    if not total:
        return V_EMPTY
    if name_hit == 0:
        return V_NONE_NAME
    if binding_hit == total:
        return V_ALL_NAME
    return V_SOME_NAME


EXCLUDE_PREFIXES = ("e444", "_e444", "run_e444", "e450", "_e450", "run_e450")


def graded_rows(cutoff: str | None = None,
                exclude: tuple[str, ...] = EXCLUDE_PREFIXES) -> tuple[list[dict], str]:
    """The per-row reading this face aggregates, exposed for the studies that ask it again.

    E456 takes the cross-module half of this same population, so it must not re-derive the
    population a second way: it calls this and filters.  The whole point is that a second
    derivation would be a second measurement of who is in scope.
    """
    face439 = _load(e440.CARD)
    cut = cutoff or face439["evidence_cutoff"]
    wrappers = e439.wrapper_rows(face439)
    sources = [p for p in e437.corpus()
               if not os.path.basename(p).startswith(exclude)]
    sites, _parsed = e420.scan_corpus(sources)
    param = [s for found in sites.values() for s in found if s.parameter_directories()]
    index = e420.main_call_index({s.func for s in param}, sources)
    print("stage: %d parameter sites over %d sources" % (len(param), len(sources)), flush=True)

    checks = e439.recheck(face439, param)
    confirmed = {(c["callee_file"], c["callee_function"]) for c in checks
                 if c["recheck"] == e439.R_CONFIRMED}
    reach = {(p, f): set(e439.reachable_callers(p, sources)) for p, f in wrappers}
    rows_all = e437.call_rows(param, index)
    print("stage: %d/%d wrappers confirmed live, %d call rows"
          % (len(confirmed), len(wrappers), len(rows_all)), flush=True)

    graded: list[dict] = []
    for row in rows_all:
        key = (row["callee_file"], row["callee_function"])
        if key not in confirmed:
            continue
        if row["caller_file"] in reach[key]:
            continue
        spell = e440.spelling_at(row["caller_file"], row["caller_line"], row["callee_function"])
        if spell != e440.S_ATTR:
            continue
        view = file_view(row["caller_file"])
        g = grade_caller(view, row["caller_line"], row["callee_function"])
        graded.append({
            "wrapper_name": row["callee_function"],
            "wrapper_file": row["callee_file"],
            "caller_file": row["caller_file"],
            "caller_function": row["caller_function"],
            "caller_line": row["caller_line"],
            "caller_kind": e437.caller_kind({"file": row["caller_file"],
                                             "caller": row["caller_function"]}),
            **g,
        })
    print("stage: %d attribute call rows re-derived for the caller side" % len(graded),
          flush=True)
    return graded, cut


def build(cutoff: str | None = None) -> dict:
    graded, cut = graded_rows(cutoff)

    scoped = [g for g in graded if g["receiver_kind"] in (RECV_BOUND, RECV_CTOR)]
    cells: dict[tuple, int] = {}
    for g in scoped:
        k = (g["receiver_kind"], g["binding"], g["name_hit"], g["binding_hit"],
             g["caller_kind"])
        cells[k] = cells.get(k, 0) + 1
    published = [{"receiver_kind": k[0], "binding": k[1], "name_hit": k[2],
                  "binding_hit": k[3], "caller_kind": k[4], "rows": v}
                 for k, v in sorted(cells.items(), key=lambda kv: str(kv[0]))]

    total_all = len(graded)
    total = sum(g["rows"] for g in published)
    name_hit = sum(g["rows"] for g in published if g["name_hit"])
    binding_hit = sum(g["rows"] for g in published if g["binding_hit"])
    by_recv_all = _tally([{"receiver_kind": g["receiver_kind"], "rows": 1} for g in graded],
                         "receiver_kind")
    by_binding = _tally(published, "binding")
    by_recv_scoped = _tally(published, "receiver_kind")

    modules_named: dict[str, int] = {}
    modules_bound: dict[str, int] = {}
    for g in scoped:
        if g["name_hit"]:
            modules_named[g["caller_file"]] = modules_named.get(g["caller_file"], 0) + 1
        if g["binding_hit"]:
            modules_bound[g["caller_file"]] = modules_bound.get(g["caller_file"], 0) + 1

    verdict = verdict_for(total, name_hit, binding_hit)
    pinned = _load(os.path.join(OUTDIR, e444.FACE_NAME))
    pinned_summary = pinned.get("summary", {})
    pin = population_pin(by_recv_all, pinned_summary.get("rows_by_receiver_kind") or {})
    return {
        "study": "E450_which_bound_receiver_names_a_method_of_a_class_in_the_callers_own_module",
        "card": CARD_ID,
        "title": "the caller side of E444's attribute rows: does a bound receiver name a method that "
                 "a class defined in the caller's own module carries, and is the receiver that class",
        "generated": date.today().isoformat(),
        "evidence_cutoff": cut,
        "verdict": verdict,
        "receiver_vocab": list(RECV_VOCAB),
        "binding_vocab": list(BIND_VOCAB),
        "verdict_vocab": list(VERDICT_VOCAB),
        "summary": {
            "attribute_call_rows_re_derived": total_all,
            "rows_in_scope_bound_or_constructor_receiver": total,
            "rows_name_hit": name_hit,
            "rows_binding_hit": binding_hit,
            "share_name_hit": round(name_hit / total, 4) if total else None,
            "share_binding_hit": round(binding_hit / total, 4) if total else None,
            "name_hit_minus_binding_hit": name_hit - binding_hit,
            "rows_by_receiver_kind_all_rows": by_recv_all,
            "rows_by_receiver_kind_in_scope": by_recv_scoped,
            "rows_by_binding": by_binding,
            "rows_production": sum(g["rows"] for g in published
                                   if g["caller_kind"] == e440.REACH_PROD),
            "rows_test": sum(g["rows"] for g in published
                             if g["caller_kind"] == e440.REACH_TEST),
            "distinct_caller_modules_with_a_name_hit": len(modules_named),
            "distinct_caller_modules_with_a_binding_hit": len(modules_bound),
            "rows_by_caller_module_name_hit": dict(sorted(modules_named.items(),
                                                          key=lambda kv: (-kv[1], kv[0]))),
            "rows_by_caller_module_binding_hit": dict(sorted(modules_bound.items(),
                                                             key=lambda kv: (-kv[1], kv[0]))),
            "population_pin": pin,
            "reproduces_e444_row_total": pin["now_row_total"] == pin["e444_row_total"],
            "reproduces_e444_receiver_distribution": pin["delta"] == 0,
            "e444_row_total": pinned_summary.get("attribute_call_rows_graded"),
            "e444_receiver_distribution": pinned_summary.get("rows_by_receiver_kind"),
        },
        "rows": published,
        "binding_examples": [
            {"wrapper_name": g["wrapper_name"], "caller_file": g["caller_file"],
             "caller_function": g["caller_function"], "caller_line": g["caller_line"],
             "receiver_name": g["receiver_name"], "receiver_class": g["receiver_class"],
             "receiver_kind": g["receiver_kind"]}
            for g in scoped if g["binding_hit"]
        ][:25],
        "method_limits": [
            "reading N is a name test, not a type test: a receiver bound to os.fdopen matches a "
            "class in the same file that happens to carry the method name, so N is an upper bound "
            "and only reading B is evidence that the row is a reader of the caller's own object",
            "reading B requires the assignment site and the constructor to be in the same file; a "
            "receiver built by a factory function, by a class imported from elsewhere, or by an "
            "annotation-only declaration reads as not bound to a local class",
            "a receiver name bound in two places is graded on its first constructor assignment; the "
            "face does not model control flow, so a name reused for two types counts once",
            "bound/unbound and the assignment sites are module-wide, so a name bound in a different "
            "function still counts -- the same limit E444 publishes for its own receiver axis",
            "the population is E440's attribute spelling class re-derived live, so a wrapper whose "
            "call rows were attributed by reachability is outside this face; the pin to E444's "
            "published totals is what makes that population the same one",
            "self/cls rows are excluded from the scope by the card's own question (they are E444's "
            "axis, and their own-class answer is already published there)",
        ],
    }


def write_face(face: dict) -> str:
    os.makedirs(OUTDIR, exist_ok=True)
    path = os.path.join(OUTDIR, FACE_NAME)
    targets = [path, os.path.join(OUTDIR, "%s-%s.json" % (DATED_PREFIX,
                                                          face.get("evidence_cutoff")))]
    for target in targets:
        with io.open(target, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
    return path


def tally_problems(face: dict) -> list[str]:
    problems: list[str] = []
    if face.get("verdict") not in VERDICT_VOCAB:
        problems.append("verdict outside the published vocabulary")
    s = face.get("summary", {})
    rows = face.get("rows") or []
    total = sum(r.get("rows", 0) for r in rows)
    if s.get("rows_in_scope_bound_or_constructor_receiver") != total:
        problems.append("the scope total does not equal the sum of the published rows")
    name_hit = sum(r["rows"] for r in rows if r.get("name_hit"))
    binding_hit = sum(r["rows"] for r in rows if r.get("binding_hit"))
    if s.get("rows_name_hit") != name_hit:
        problems.append("rows_name_hit does not re-derive from the rows")
    if s.get("rows_binding_hit") != binding_hit:
        problems.append("rows_binding_hit does not re-derive from the rows")
    if binding_hit > name_hit:
        problems.append("the binding arm cannot exceed the name arm")
    for r in rows:
        if r.get("binding_hit") and not r.get("name_hit"):
            problems.append("a binding hit whose class does not carry the name")
            break
        if r.get("receiver_kind") not in (RECV_BOUND, RECV_CTOR):
            problems.append("a row outside the card's scope was published")
            break
    if sum((s.get("rows_by_receiver_kind_in_scope") or {}).values()) != total:
        problems.append("rows_by_receiver_kind_in_scope does not close against the row total")
    if sum((s.get("rows_by_binding") or {}).values()) != total:
        problems.append("rows_by_binding does not close against the row total")
    if s.get("rows_production", 0) + s.get("rows_test", 0) != total:
        problems.append("production plus test rows do not close against the row total")
    pin = s.get("population_pin") or {}
    if pin.get("verdict") != PIN_GROWTH:
        problems.append("the population against E444's published one is not a growth-only superset")
    if pin.get("now_row_total") != s.get("attribute_call_rows_re_derived"):
        problems.append("the pin's row total differs from the re-derived row total")
    if pin.get("e444_row_total") != s.get("e444_row_total"):
        problems.append("the pin does not rebuild E444's published total from its distribution")
    if s.get("reproduces_e444_row_total") != (pin.get("delta") == 0):
        problems.append("the reproduction flag is carried, not derived from the pin")
    if s.get("name_hit_minus_binding_hit") != name_hit - binding_hit:
        problems.append("name_hit_minus_binding_hit is carried, not derived")
    if face.get("verdict") != verdict_for(total, name_hit, binding_hit):
        problems.append("the verdict does not re-derive from the published counts")
    return problems


def row_identity(row: dict) -> dict:
    """Stable identity for a published cell: the demographic it belongs to.

    The claim a cell makes (name hit / binding hit) is the CLASS, so E455's rule reports a flipped
    claim as class_moved instead of as a row that vanished and another that appeared.  The count is
    the measurement and may only move up.
    """
    cell = dict(row)
    cell["cell"] = "%s|%s|%s" % (row.get("receiver_kind"), row.get("binding"),
                                 row.get("caller_kind"))
    return cell


def _keyed(face: dict) -> dict:
    out = dict(face)
    out["rows"] = [row_identity(r) for r in (face.get("rows") or [])]
    return out


def tolerated(result: dict) -> bool:
    """Both standing answers, not only the growing one.

    growth_tolerance.tolerates() asks "may this difference stand as growth?", so it answers False
    for `identical` -- correct for its own question and wrong for a verify, which must accept a
    quiet tree.  This face therefore names both verdicts explicitly.
    """
    return result.get("verdict") in (gt.IDENTICAL, gt.PURE_GROWTH)


def verify(face: dict | None = None) -> list[str]:
    face = face or _load(os.path.join(OUTDIR, FACE_NAME))
    problems = tally_problems(face)
    live = build(face.get("evidence_cutoff"))
    if live["verdict"] != face["verdict"]:
        problems.append("live verdict %s != published %s" % (live["verdict"], face["verdict"]))
    # The corpus gains files every round, so an exact equality between the published summary and a
    # fresh reading is a one-round purchase (E455).  What is asserted instead: no cell loses rows, no
    # claim flips, the verdict holds, and every integer count keeps its direction -- pure growth is
    # reported, not refused.
    tol = gt.classify(_keyed(face), _keyed(live), list_key="rows", row_id="cell",
                      class_fields=("name_hit", "binding_hit"))
    print("growth: %s | %s" % (tol.get("verdict"), gt.describe(tol)))
    if not tolerated(tol):
        problems.append("the live reading is not a growth-only superset: %s" % tol.get("verdict"))
    pin = (face.get("summary") or {}).get("population_pin") or {}
    if pin.get("verdict") != PIN_GROWTH:
        problems.append("the published pin is not a growth-only superset of E444")
    return problems


def selftest() -> int:
    legs = 0
    fails: list[str] = []

    def check(name: str, cond: bool) -> None:
        nonlocal legs
        legs += 1
        if not cond:
            fails.append(name)

    src = (
        "class Box:\n"
        "    def write(self, p):\n"
        "        return p\n"
        "class Empty:\n"
        "    pass\n"
        "def go(path):\n"
        "    b = Box()\n"
        "    b.write(path)\n"
        "    Box().write(path)\n"
        "    other = open(path)\n"
        "    other.write(path)\n"
        "    never.write(path)\n"
        "    return b\n"
    )
    tree = ast.parse(src)
    classes = e444._class_index(tree)
    assigns = _assignments(tree)
    check("classes_read", classes == {"Box": {"write"}, "Empty": set()})
    check("assigns_read_local_ctor", any(isinstance(v, ast.Call) for v in assigns.get("b", [])))
    check("assigns_read_call_not_class_name",
          binding_kind(assigns.get("other") or [], classes) == BIND_OTHER_CALL)
    check("assigns_absent_is_never", binding_kind([], classes) == BIND_NEVER)
    check("assigns_non_call",
          binding_kind([ast.Constant(value=1)], classes) == BIND_NOT_A_CALL)
    check("binding_reads_local_ctor", binding_kind(assigns.get("b") or [], classes) == BIND_CTOR)

    calls: dict = {}
    bound = e444._bound_names(tree)
    _collect_calls(tree, [], calls, bound)
    view = {"classes": classes, "bound": bound, "calls": calls, "assigns": assigns}
    check("calls_indexed", len(calls) == 4)
    check("ctor_class_recorded",
          any(rec[3] == "Box" for recs in calls.values() for rec in recs))

    hit = grade_caller(view, 8, "write")
    check("grade_located", hit["located"] is True)
    check("grade_bound_ctor", hit["receiver_kind"] == RECV_BOUND)
    check("grade_name_hit", hit["name_hit"] is True)
    check("grade_binding_hit", hit["binding_hit"] is True)
    check("grade_receiver_class", hit["receiver_class"] == "Box")

    ctor = grade_caller(view, 9, "write")
    check("grade_ctor_kind", ctor["receiver_kind"] == RECV_CTOR)
    check("grade_ctor_binding_hit", ctor["binding_hit"] is True)
    check("grade_ctor_class", ctor["receiver_class"] == "Box")

    other = grade_caller(view, 11, "write")
    check("grade_other_binding", other["binding"] == BIND_OTHER_CALL)
    check("name_is_not_a_type", other["name_hit"] is True and other["binding_hit"] is False)

    unbound = grade_caller(view, 12, "write")
    check("grade_unbound_kind", unbound["receiver_kind"] == RECV_UNBOUND)
    check("grade_unbound_never", unbound["binding"] == BIND_NEVER)

    missing = grade_caller(view, 999, "write")
    check("grade_missing", missing["receiver_kind"] == RECV_MISSING and not missing["located"])
    check("grade_no_view", grade_caller(None, 8, "write")["located"] is False)

    check("classes_carrying_empty", classes_carrying(classes, "close") == [])
    check("classes_carrying_hit", classes_carrying(classes, "write") == ["Box"])

    check("verdict_empty", verdict_for(0, 0, 0) == V_EMPTY)
    check("verdict_none", verdict_for(10, 0, 0) == V_NONE_NAME)
    check("verdict_some", verdict_for(10, 3, 1) == V_SOME_NAME)
    check("verdict_all", verdict_for(10, 10, 10) == V_ALL_NAME)

    def row(kind=RECV_BOUND, binding=BIND_CTOR, name_hit=True, binding_hit=True, rows=1,
            caller_kind=e440.REACH_PROD):
        return {"receiver_kind": kind, "binding": binding, "name_hit": name_hit,
                "binding_hit": binding_hit, "caller_kind": caller_kind, "rows": rows}

    def face_of(rows: list[dict]) -> dict:
        total = sum(r["rows"] for r in rows)
        name_hit = sum(r["rows"] for r in rows if r["name_hit"])
        binding_hit = sum(r["rows"] for r in rows if r["binding_hit"])
        return {
            "verdict": verdict_for(total, name_hit, binding_hit),
            "rows": rows,
            "summary": {
                "attribute_call_rows_re_derived": total,
                "rows_in_scope_bound_or_constructor_receiver": total,
                "rows_name_hit": name_hit,
                "rows_binding_hit": binding_hit,
                "name_hit_minus_binding_hit": name_hit - binding_hit,
                "rows_by_receiver_kind_all_rows": {},
                "rows_by_receiver_kind_in_scope": _tally(rows, "receiver_kind"),
                "rows_by_binding": _tally(rows, "binding"),
                "rows_production": sum(r["rows"] for r in rows
                                       if r["caller_kind"] == e440.REACH_PROD),
                "rows_test": sum(r["rows"] for r in rows
                                 if r["caller_kind"] == e440.REACH_TEST),
                "population_pin": {
                    "e444_row_total": total,
                    "now_row_total": total,
                    "delta": 0,
                    "per_receiver_kind": {},
                    "kinds_that_lost_rows": [],
                    "verdict": PIN_GROWTH,
                },
                "reproduces_e444_row_total": True,
                "reproduces_e444_receiver_distribution": True,
                "e444_row_total": total,
            },
        }

    good = face_of([row(), row(kind=RECV_CTOR)])
    check("tally_clean_face", tally_problems(good) == [])

    bad = face_of([row()])
    bad["summary"]["rows_name_hit"] = 5
    check("tally_catches_carried_count", any("re-derive" in p for p in tally_problems(bad)))

    bad2 = face_of([row(name_hit=False, binding_hit=True)])
    check("tally_catches_binding_without_name",
          any("binding hit whose class" in p for p in tally_problems(bad2)))

    bad3 = face_of([row(binding_hit=False, name_hit=False)])
    bad3["rows"].append(row(kind=RECV_SELF))
    check("tally_catches_out_of_scope_row",
          any("outside the card's scope" in p for p in tally_problems(bad3)))

    bad4 = face_of([row()])
    bad4["summary"]["population_pin"]["verdict"] = PIN_MOVED
    check("tally_catches_broken_pin",
          any("not a growth-only superset" in p for p in tally_problems(bad4)))

    grown = population_pin({"a_name_the_caller_binds": 12, "a_constructor_call_in_the_caller": 3},
                           {"a_name_the_caller_binds": 10,
                            "a_constructor_call_in_the_caller": 3})
    check("pin_growth_is_allowed", grown["verdict"] == PIN_GROWTH and grown["delta"] == 2)
    check("pin_rebuilds_the_snapshot_total", grown["e444_row_total"] == 13)
    shrank = population_pin({"a_name_the_caller_binds": 9},
                            {"a_name_the_caller_binds": 10})
    check("pin_refuses_a_lost_kind",
          shrank["verdict"] == PIN_MOVED
          and shrank["kinds_that_lost_rows"] == ["a_name_the_caller_binds"])

    bad6 = face_of([row()])
    bad6["summary"]["reproduces_e444_row_total"] = False
    check("tally_catches_a_carried_pin_flag",
          any("carried, not derived" in p for p in tally_problems(bad6)))

    ident = row_identity(row(rows=3))
    check("identity_keys_the_demographic",
          ident["cell"] == "%s|%s|%s" % (RECV_BOUND, BIND_CTOR, e440.REACH_PROD))
    check("identity_keeps_the_claim_out_of_the_cell",
          row_identity(row(rows=3, name_hit=False, binding_hit=False))["cell"] == ident["cell"])

    stored = face_of([row(rows=2), row(kind=RECV_CTOR, rows=1)])
    grown_live = face_of([row(rows=3), row(kind=RECV_CTOR, rows=1)])
    shrunk_live = face_of([row(rows=1), row(kind=RECV_CTOR, rows=1)])
    flipped_live = face_of([row(rows=2, name_hit=False, binding_hit=False),
                            row(kind=RECV_CTOR, rows=1)])
    grew = gt.classify(_keyed(stored), _keyed(grown_live), list_key="rows", row_id="cell",
                       class_fields=("name_hit", "binding_hit"))
    shrank = gt.classify(_keyed(stored), _keyed(shrunk_live), list_key="rows", row_id="cell",
                         class_fields=("name_hit", "binding_hit"))
    flipped = gt.classify(_keyed(stored), _keyed(flipped_live), list_key="rows", row_id="cell",
                          class_fields=("name_hit", "binding_hit"))
    check("verify_tolerates_growth", tolerated(grew))
    check("verify_refuses_a_shrunk_cell", not tolerated(shrank))
    check("verify_refuses_a_flipped_claim", not tolerated(flipped))

    quiet = gt.classify(_keyed(stored), _keyed(stored), list_key="rows", row_id="cell",
                        class_fields=("name_hit", "binding_hit"))
    check("verify_accepts_an_identical_reading", quiet["verdict"] == gt.IDENTICAL)
    check("verify_tolerates_identity", tolerated(quiet))
    check("the_shared_rule_does_not", gt.tolerates(quiet) is False)

    bad5 = face_of([row(binding_hit=False)])
    bad5["verdict"] = V_ALL_NAME
    check("tally_catches_moved_verdict",
          any("verdict does not re-derive" in p for p in tally_problems(bad5)))

    if fails:
        print("SELFTEST FAIL %d/%d" % (len(fails), legs))
        for f in fails:
            print("  -", f)
        return 1
    print("SELFTEST OK %d/%d" % (legs, legs))
    return 0


def main(argv: list[str]) -> int:
    action = argv[1] if len(argv) > 1 else "run"
    if action == "selftest":
        return selftest()
    if action == "run":
        face = build()
        path = write_face(face)
        s = face["summary"]
        print("rows=%d scope=%d name_hit=%d binding_hit=%d"
              % (s["attribute_call_rows_re_derived"],
                 s["rows_in_scope_bound_or_constructor_receiver"],
                 s["rows_name_hit"], s["rows_binding_hit"]))
        print("verdict=%s" % face["verdict"])
        print("face=%s" % _rel(path))
        return 0
    if action == "check":
        problems = tally_problems(_load(os.path.join(OUTDIR, FACE_NAME)))
        for p in problems:
            print("problem:", p)
        print("check problems=%s" % (len(problems),))
        return 1 if problems else 0
    if action == "verify":
        problems = verify()
        for p in problems:
            print("problem:", p)
        print("verify problems=%s" % (len(problems),))
        return 1 if problems else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))