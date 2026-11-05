"""E444: E440 dropped 24,308 attribute call rows as "a method call on some object, not evidence
about the wrapper".  That rule reads the spelling, not the receiver.

`recv.write(p)` is not evidence about a module-level `write` -- true.  But if `write` is a method of
a class defined in the very module the row was attributed to, the row *is* evidence about that
module: someone is calling into that module's own object.  E440 never asked.  This study asks it,
for every one of those rows, from source only:

  Axis A -- which classes does the attributed module define, and which methods do they carry?
            Does this row name one of those methods?
  Axis B -- what is the receiver spelled as at the row's own line?
            self/cls inside the caller's class, a constructor call in the caller, a name the
            caller binds, a name the caller never binds, another expression.

Axis A is read from the *attributed* module (the wrapper's file).  Axis B is read from the
*caller's* live AST at the row's line.  Neither is inferred from the other, and a row that cannot
be located any more is published as missing rather than assumed either way.

Usage:
    python scripts/e444_attr_method.py run|verify|check|selftest
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

ROOT = e420.ROOT
ST = e420.ST
OUTDIR = ST
FACE_NAME = "attrmethod_latest.json"
DATED_PREFIX = "ATTRMETHOD"
CARD_ID = "E444-WHICH-ATTRIBUTE-CALL-NAMES-A-METHOD-OF-A-CLASS-IN-THE-MODULE-IT-WAS-ATTRIBUTED-TO"

RECV_SELF = "self_or_cls_inside_the_callers_class"
RECV_CTOR = "a_constructor_call_in_the_caller"
RECV_BOUND = "a_name_the_caller_binds"
RECV_UNBOUND = "a_name_the_caller_never_binds"
RECV_OTHER = "another_expression_in_the_caller"
RECV_MISSING = "the_receiver_is_not_at_that_line_in_the_live_file"
RECV_VOCAB = (RECV_SELF, RECV_CTOR, RECV_BOUND, RECV_UNBOUND, RECV_OTHER, RECV_MISSING)

V_EMPTY = "no_attribute_call_row_to_grade"
V_ALL = ("every_attribute_call_row_names_a_method_that_a_class_in_the_attributed_module_defines")
V_SOME = "some_attribute_call_rows_name_a_method_no_class_in_the_attributed_module_defines"
V_NONE = "no_attribute_call_row_names_a_method_of_a_class_in_the_attributed_module"
V_NO_CLASS = ("no_attribute_call_row_could_name_a_method_because_the_attributed_modules_define"
              "_no_class_at_all")
VERDICT_VOCAB = (V_EMPTY, V_ALL, V_SOME, V_NONE, V_NO_CLASS)

_AST_CACHE: dict[str, dict | None] = {}


def _rel(path: str) -> str:
    return os.path.relpath(path, ROOT).replace("\\", "/")


def _load(path: str) -> dict:
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _tally(rows: list[dict], key: str, vocab) -> dict:
    out = {v: 0 for v in vocab}
    for r in rows:
        out[r[key]] = out.get(r[key], 0) + r["rows"]
    return out


def _arg_names(node) -> list[str]:
    out = [a.arg for a in getattr(node.args, "posonlyargs", [])]
    out += [a.arg for a in node.args.args]
    out += [a.arg for a in node.args.kwonlyargs]
    if node.args.vararg:
        out.append(node.args.vararg.arg)
    if node.args.kwarg:
        out.append(node.args.kwarg.arg)
    return out


def _class_index(tree) -> dict[str, set]:
    """class name -> method names it defines directly in its body."""
    out: dict[str, set] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            methods = out.setdefault(node.name, set())
            for body in node.body:
                if isinstance(body, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    methods.add(body.name)
    return out


def _bound_names(tree) -> set[str]:
    """Every name this module can bind somewhere: imports, locals, parameters, assignments."""
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out.update(_arg_names(node))
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            out.add(node.id)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                out.add((alias.asname or alias.name).split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                out.add(alias.asname or alias.name)
        elif isinstance(node, ast.arg):
            out.add(node.arg)
    return out


def _receiver_kind(recv, bound: set[str]) -> tuple[str, str | None]:
    if isinstance(recv, ast.Name):
        if recv.id in ("self", "cls"):
            return RECV_SELF, recv.id
        return (RECV_BOUND if recv.id in bound else RECV_UNBOUND), recv.id
    if isinstance(recv, ast.Call):
        return RECV_CTOR, None
    return RECV_OTHER, None


def _collect_calls(node, stack: list, calls: dict, bound: set) -> None:
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
        kind, name = _receiver_kind(node.func.value, bound)
        enclosing = None
        for tag, value in reversed(stack):
            if tag == "class":
                enclosing = value
                break
        calls.setdefault((getattr(node, "lineno", -1), node.func.attr), []).append(
            (kind, name, enclosing))
    for child in ast.iter_child_nodes(node):
        _collect_calls(child, stack, calls, bound)


def file_view(rel: str) -> dict | None:
    """One pass per file: its classes and their methods, its bindable names, its attribute calls."""
    if rel in _AST_CACHE:
        return _AST_CACHE[rel]
    try:
        src = io.open(os.path.join(ROOT, rel), encoding="utf-8", errors="replace").read()
        tree = ast.parse(src)
    except (OSError, SyntaxError, ValueError):
        _AST_CACHE[rel] = None
        return None
    bound = _bound_names(tree)
    calls: dict = {}
    _collect_calls(tree, [], calls, bound)
    view = {"classes": _class_index(tree), "bound": bound, "calls": calls}
    _AST_CACHE[rel] = view
    return view


def grade_row(caller_view: dict | None, wrapper_view: dict | None, line: int,
              method: str) -> tuple[str, bool, bool, int]:
    """(receiver kind, method defined in the attributed module, self-class defines it, classes)."""
    defined = False
    classes_with: list[str] = []
    if wrapper_view:
        for cls, methods in wrapper_view["classes"].items():
            if method in methods:
                defined = True
                classes_with.append(cls)
    kind = RECV_MISSING
    own_class_defines = False
    if caller_view:
        seen = caller_view["calls"].get((line, method))
        if seen:
            kind, _name, enclosing = seen[0]
            if kind == RECV_SELF and enclosing:
                own_class_defines = method in caller_view["classes"].get(enclosing, set())
    return kind, defined, own_class_defines, len(classes_with)


def verdict_for(rows: list[dict], classes_in_those_modules: int) -> str:
    """Recomputed from the published rows and the class count, never carried."""
    total = sum(r["rows"] for r in rows)
    if not total:
        return V_EMPTY
    hit = sum(r["rows"] for r in rows
              if r["names_a_method_of_a_class_in_the_attributed_module"])
    if hit == total:
        return V_ALL
    if hit == 0:
        return V_NO_CLASS if classes_in_those_modules == 0 else V_NONE
    return V_SOME


def module_class_census(wrapper_files: set[str]) -> dict:
    """Classes and methods actually defined by the modules the attribute rows were attributed to."""
    blocks = []
    total_classes = 0
    for rel in sorted(wrapper_files):
        view = file_view(rel)
        classes = {c: sorted(m) for c, m in sorted((view or {}).get("classes", {}).items())}
        total_classes += len(classes)
        blocks.append({"module": rel, "parsed": view is not None,
                       "classes": classes, "class_count": len(classes),
                       "method_count": sum(len(m) for m in classes.values())})
    return {"modules": blocks, "modules_scanned": len(blocks),
            "classes_total": total_classes}


def build(cutoff: str | None = None) -> dict:
    face439 = _load(e440.CARD)
    cut = cutoff or face439["evidence_cutoff"]
    wrappers = e439.wrapper_rows(face439)
    names = sorted({f for _p, f in wrappers})
    sources = [p for p in e437.corpus()
               if not os.path.basename(p).startswith(("e444", "_e444", "run_e444"))]
    sites, _parsed = e420.scan_corpus(sources)
    param = [s for found in sites.values() for s in found if s.parameter_directories()]
    index = e420.main_call_index({s.func for s in param}, sources)
    print("stage: %d parameter sites over %d sources" % (len(param), len(sources)), flush=True)

    checks = e439.recheck(face439, param)
    confirmed = {(c["callee_file"], c["callee_function"]) for c in checks
                 if c["recheck"] == e439.R_CONFIRMED}
    defs = e439.definition_counts(names, sources)
    reach = {(p, f): set(e439.reachable_callers(p, sources)) for p, f in wrappers}
    rows_all = e437.call_rows(param, index)
    print("stage: %d/%d wrappers confirmed live, %d call rows"
          % (len(confirmed), len(wrappers), len(rows_all)), flush=True)

    graded: list[dict] = []
    e440_method_rows = 0
    per_class: dict[str, int] = {}
    for r in rows_all:
        key = (r["callee_file"], r["callee_function"])
        if key not in confirmed:
            continue
        if r["caller_file"] in reach[key]:
            continue
        spell = e440.spelling_at(r["caller_file"], r["caller_line"], r["callee_function"])
        if spell != e440.S_ATTR:
            continue
        e440_method_rows += 1
        caller_view = file_view(r["caller_file"])
        wrapper_view = file_view(r["callee_file"])
        kind, defined, own_class, n_classes = grade_row(
            caller_view, wrapper_view, r["caller_line"], r["callee_function"])
        if defined and wrapper_view:
            for cls, methods in wrapper_view["classes"].items():
                if r["callee_function"] in methods:
                    per_class[cls] = per_class.get(cls, 0) + 1
        graded.append({
            "wrapper_name": r["callee_function"],
            "wrapper_file": r["callee_file"],
            "caller_file": r["caller_file"],
            "caller_function": r["caller_function"],
            "caller_line": r["caller_line"],
            "caller_kind": e437.caller_kind({"file": r["caller_file"],
                                             "caller": r["caller_function"]}),
            "receiver_kind": kind,
            "names_a_method_of_a_class_in_the_attributed_module": defined,
            "self_rows_own_class_defines_it": own_class,
            "classes_in_the_attributed_module_with_that_method": n_classes,
        })
    print("stage: %d attribute call rows graded (E440 dropped %d as method calls)"
          % (len(graded), e440_method_rows), flush=True)

    cells: dict[tuple, int] = {}
    for g in graded:
        k = (g["wrapper_name"], g["wrapper_file"], g["receiver_kind"],
             g["names_a_method_of_a_class_in_the_attributed_module"], g["caller_kind"])
        cells[k] = cells.get(k, 0) + 1
    published = [{"wrapper_name": k[0], "wrapper_file": k[1], "receiver_kind": k[2],
                  "names_a_method_of_a_class_in_the_attributed_module": k[3],
                  "caller_kind": k[4], "rows": v} for k, v in sorted(cells.items())]

    hit = sum(g["rows"] for g in published
              if g["names_a_method_of_a_class_in_the_attributed_module"])
    total = sum(g["rows"] for g in published)
    by_recv = _tally(published, "receiver_kind", RECV_VOCAB)
    self_rows = sum(g["rows"] for g in published if g["receiver_kind"] == RECV_SELF)
    self_hits = sum(g["rows"] for g in published if g["receiver_kind"] == RECV_SELF
                    and g.get("names_a_method_of_a_class_in_the_attributed_module"))
    unbound = [g for g in published if g["receiver_kind"] in (RECV_UNBOUND, RECV_MISSING)]
    attributed_modules = {g["wrapper_file"] for g in published}
    census = module_class_census(attributed_modules)
    graded_names = {g["wrapper_name"] for g in published}

    verdict = verdict_for(published, census["classes_total"])
    return {
        "study": "E444_which_attribute_call_row_names_a_method_of_a_class_in_its_own_module",
        "card": CARD_ID,
        "title": "re-read E440's attribute call rows by their receiver: how many name a method that "
                 "a class defined in the very module the row was attributed to already carries",
        "generated": date.today().isoformat(),
        "evidence_cutoff": cut,
        "verdict": verdict,
        "receiver_vocab": list(RECV_VOCAB),
        "verdict_vocab": list(VERDICT_VOCAB),
        "summary": {
            "attribute_call_rows_graded": total,
            "rows_naming_a_method_of_a_class_in_the_attributed_module": hit,
            "share_naming_a_method_there": round(hit / total, 4) if total else None,
            "rows_naming_no_method_there": total - hit,
            "attr_call_rows_e440_classed_as_method_calls": e440_method_rows,
            "reproduces_e440_attribute_count": e440_method_rows == total,
            "rows_by_receiver_kind": by_recv,
            "self_rows_whose_own_class_defines_the_method": self_hits,
            "self_rows_total": self_rows,
            "rows_with_a_receiver_the_caller_never_binds_or_cannot_be_located":
                sum(g["rows"] for g in unbound),
            "rows_production": sum(g["rows"] for g in published
                                   if g["caller_kind"] == e440.REACH_PROD),
            "rows_test": sum(g["rows"] for g in published
                             if g["caller_kind"] == e440.REACH_TEST),
            "distinct_wrapper_names_graded": len(graded_names),
            "wrapper_names_with_no_attribute_rows": sorted(n for n in names
                                                           if n not in graded_names),
            "modules_the_rows_were_attributed_to": census["modules_scanned"],
            "classes_defined_across_those_modules": census["classes_total"],
            "class_census": census["modules"],
            "rows_by_class_in_the_attributed_module": dict(sorted(per_class.items())),
            "per_name": [
                {
                    "name": name,
                    "wrapper_files": sorted(p for p, f in wrappers if f == name),
                    "definitions": len(defs.get(name) or []),
                    "attribute_call_rows": sum(g["rows"] for g in published
                                               if g["wrapper_name"] == name),
                    "rows_naming_a_method_of_a_class_in_the_attributed_module":
                        sum(g["rows"] for g in published if g["wrapper_name"] == name
                            and g["names_a_method_of_a_class_in_the_attributed_module"]),
                }
                for name in names if name in graded_names
            ],
        },
        "rows": published,
        "receiver_examples": [
            {"wrapper_name": g["wrapper_name"], "caller_file": g["caller_file"],
             "caller_function": g["caller_function"], "caller_line": g["caller_line"],
             "receiver_kind": g["receiver_kind"]}
            for g in graded
            if g["receiver_kind"] in (RECV_UNBOUND, RECV_MISSING, RECV_OTHER)
        ][:40],
        "method_limits": [
            "'method defined in the attributed module' counts a def inside a ClassDef body; a "
            "module-level function of the same name is not a method and does not count",
            "a row that matches methods on several classes is counted once in the cell totals and "
            "once in each class under rows_by_class_in_the_attributed_module -- that block is not "
            "a partition of the row total",
            "the receiver is read from the caller's live AST at the row's own line; a file edited "
            "since the row was indexed reports missing rather than guessed",
            "bound/unbound is module-wide: a name bound anywhere in the caller file counts as "
            "bound, so a receiver bound in a different function reads as bound",
            "receiver kind is a spelling fact, not a type: a module alias reads as a bound name",
            "the population is E440's attribute spelling class re-derived live, so a wrapper whose "
            "call rows were attributed by reachability is outside this face",
        ],
    }


def write_face(face: dict) -> str:
    os.makedirs(OUTDIR, exist_ok=True)
    path = os.path.join(OUTDIR, FACE_NAME)
    targets = [path,
               os.path.join(OUTDIR, "%s-%s.json" % (DATED_PREFIX, face.get("evidence_cutoff")))]
    for target in targets:
        with io.open(target, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
    return path


def tally_problems(face: dict) -> list[str]:
    problems: list[str] = []
    s = face.get("summary") or {}
    rows = face.get("rows") or []
    by_recv: dict[str, int] = {v: 0 for v in RECV_VOCAB}
    by_name: dict[str, dict] = {}
    per_class: dict[str, int] = {}
    hit = 0
    total = 0
    for r in rows:
        if r.get("receiver_kind") not in RECV_VOCAB:
            problems.append("%s:%s receiver kind outside the vocabulary"
                            % (r.get("wrapper_name"), r.get("caller_file")))
            continue
        if r.get("caller_kind") not in (e440.REACH_PROD, e440.REACH_TEST):
            problems.append("%s:%s caller kind outside the vocabulary"
                            % (r.get("wrapper_name"), r.get("caller_file")))
        if not isinstance(r.get("rows"), int) or r.get("rows") <= 0:
            problems.append("%s:%s carries a non-positive cell count"
                            % (r.get("wrapper_name"), r.get("caller_file")))
            continue
        if not isinstance(r.get("names_a_method_of_a_class_in_the_attributed_module"), bool):
            problems.append("%s:%s does not carry a boolean method reading"
                            % (r.get("wrapper_name"), r.get("caller_file")))
            continue
        by_recv[r["receiver_kind"]] = by_recv.get(r["receiver_kind"], 0) + r["rows"]
        block = by_name.setdefault(r["wrapper_name"], {"rows": 0, "hit": 0})
        block["rows"] += r["rows"]
        total += r["rows"]
        if r["names_a_method_of_a_class_in_the_attributed_module"]:
            hit += r["rows"]
            block["hit"] += r["rows"]
    if total != s.get("attribute_call_rows_graded"):
        problems.append("the row cells do not close against attribute_call_rows_graded")
    if hit != s.get("rows_naming_a_method_of_a_class_in_the_attributed_module"):
        problems.append("the hit count does not re-derive from the rows")
    if by_recv != (s.get("rows_by_receiver_kind") or {}):
        problems.append("rows_by_receiver_kind does not re-derive from the rows")
    if (total - hit) != s.get("rows_naming_no_method_there"):
        problems.append("rows_naming_no_method_there does not re-derive")
    want = verdict_for(rows, s.get("classes_defined_across_those_modules") or 0)
    if want != face.get("verdict"):
        problems.append("the verdict does not re-derive from the published rows")
    if s.get("reproduces_e440_attribute_count") != (
            s.get("attr_call_rows_e440_classed_as_method_calls") == total):
        problems.append("reproduces_e440_attribute_count disagrees with its own two numbers")
    census = s.get("class_census") or []
    if len(census) != s.get("modules_the_rows_were_attributed_to"):
        problems.append("class_census does not cover every attributed module")
    if sum(block.get("class_count", 0) for block in census) \
            != s.get("classes_defined_across_those_modules"):
        problems.append("the class census does not add up to its own total")
    for block in census:
        if block.get("class_count") != len(block.get("classes") or {}):
            problems.append("%s: the class count does not re-derive" % block.get("module"))
        if block.get("method_count") != sum(len(m) for m in (block.get("classes") or {}).values()):
            problems.append("%s: the method count does not re-derive" % block.get("module"))
    if (s.get("classes_defined_across_those_modules") == 0) and hit:
        problems.append("rows claim a module method while the census finds no class at all")
    per = s.get("per_name") or []
    if len(per) != s.get("distinct_wrapper_names_graded"):
        problems.append("per_name does not cover every wrapper name graded")
    for block in per:
        mine = by_name.get(block.get("name"), {"rows": 0, "hit": 0})
        if block.get("attribute_call_rows") != mine["rows"]:
            problems.append("%s: attribute_call_rows does not re-derive" % block.get("name"))
        if block.get("rows_naming_a_method_of_a_class_in_the_attributed_module") != mine["hit"]:
            problems.append("%s: the hit count does not re-derive" % block.get("name"))
        if mine["rows"] == 0:
            problems.append("%s: graded a name with no rows" % block.get("name"))
    if sum(b.get("attribute_call_rows", 0) for b in per) != total:
        problems.append("the per-name blocks do not add up to the row total")
    if sum((s.get("rows_by_class_in_the_attributed_module") or {}).values()) < hit:
        problems.append("the per-class block cannot be smaller than the hit total")
    if s.get("rows_production", 0) + s.get("rows_test", 0) != total:
        problems.append("production plus test rows do not close against the row total")
    return problems


def verify(face: dict | None = None) -> list[str]:
    face = face or _load(os.path.join(OUTDIR, FACE_NAME))
    problems = tally_problems(face)
    live = build(face.get("evidence_cutoff"))
    if live["verdict"] != face["verdict"]:
        problems.append("live verdict %s != published %s" % (live["verdict"], face["verdict"]))
    for key in ("attribute_call_rows_graded",
                "rows_naming_a_method_of_a_class_in_the_attributed_module",
                "rows_by_receiver_kind",
                "rows_by_class_in_the_attributed_module",
                "classes_defined_across_those_modules",
                "class_census",
                "attr_call_rows_e440_classed_as_method_calls"):
        if live["summary"].get(key) != face["summary"].get(key):
            problems.append("live %s differs from the published face" % key)
    return problems


def selftest() -> int:
    legs = 0
    fails: list[str] = []

    def check(name: str, cond: bool) -> None:
        nonlocal legs
        legs += 1
        if not cond:
            fails.append(name)

    bound = {"buf", "self", "FOO"}
    check("recv_self", _receiver_kind(ast.Name(id="self"), bound)[0] == RECV_SELF)
    check("recv_cls", _receiver_kind(ast.Name(id="cls"), bound)[0] == RECV_SELF)
    check("recv_bound", _receiver_kind(ast.Name(id="buf"), bound)[0] == RECV_BOUND)
    check("recv_unbound", _receiver_kind(ast.Name(id="nobody"), bound)[0] == RECV_UNBOUND)
    check("recv_ctor",
          _receiver_kind(ast.parse("Foo()").body[0].value, bound)[0] == RECV_CTOR)
    check("recv_other",
          _receiver_kind(ast.parse("d['k']").body[0].value, bound)[0] == RECV_OTHER)

    tree = ast.parse(
        "import os\n"
        "class Box:\n"
        "    def write(self, p):\n"
        "        return p\n"
        "    def close(self):\n"
        "        return None\n"
        "class Empty:\n"
        "    pass\n"
        "def go(buf, other):\n"
        "    buf.write(1)\n"
        "    Box().write(2)\n"
        "    self_like = 0\n"
        "    unknown.write(3)\n"
    )
    view = {"classes": _class_index(tree), "bound": _bound_names(tree), "calls": {}}
    _collect_calls(tree, [], view["calls"], view["bound"])
    check("class_index_reads_methods", view["classes"]["Box"] == {"write", "close"})
    check("class_index_empty_class", view["classes"]["Empty"] == set())
    check("bound_reads_parameters", "buf" in view["bound"] and "other" in view["bound"])
    check("bound_reads_locals", "self_like" in view["bound"])
    check("bound_reads_imports", "os" in view["bound"])
    check("calls_indexed_per_line", len(view["calls"]) == 3)
    kinds = sorted(v[0][0] for v in view["calls"].values())
    check("calls_read_receivers",
          kinds == sorted([RECV_BOUND, RECV_CTOR, RECV_UNBOUND]))
    check("calls_carry_no_enclosing_class_at_module_scope",
          all(v[0][2] is None for v in view["calls"].values()))

    graded = grade_row({"classes": {"Box": {"write"}}, "calls": {}, "bound": set()},
                       {"classes": {"Box": {"write"}}, "calls": {}, "bound": set()},
                       99, "write")
    check("grade_missing_receiver", graded[0] == RECV_MISSING)
    check("grade_method_defined_anyway", graded[1] is True)
    check("grade_counts_the_classes", graded[3] == 1)

    def face_of(rows: list[dict], wrapper_names: list[str] | None = None) -> dict:
        per = []
        for name in sorted(wrapper_names if wrapper_names is not None
                           else {r["wrapper_name"] for r in rows}):
            mine = [r for r in rows if r["wrapper_name"] == name]
            per.append({
                "name": name, "wrapper_files": ["scripts/a.py"], "definitions": 1,
                "attribute_call_rows": sum(r["rows"] for r in mine),
                "rows_naming_a_method_of_a_class_in_the_attributed_module":
                    sum(r["rows"] for r in mine
                        if r["names_a_method_of_a_class_in_the_attributed_module"]),
            })
        by_recv = {v: 0 for v in RECV_VOCAB}
        for r in rows:
            by_recv[r["receiver_kind"]] += r["rows"]
        hit = sum(r["rows"] for r in rows
                  if r["names_a_method_of_a_class_in_the_attributed_module"])
        total = sum(r["rows"] for r in rows)
        classes = 1 if hit else 0
        return {
            "verdict": verdict_for(rows, classes),
            "rows": rows,
            "summary": {
                "attribute_call_rows_graded": total,
                "rows_naming_a_method_of_a_class_in_the_attributed_module": hit,
                "rows_naming_no_method_there": total - hit,
                "attr_call_rows_e440_classed_as_method_calls": total,
                "reproduces_e440_attribute_count": True,
                "rows_by_receiver_kind": by_recv,
                "rows_production": sum(r["rows"] for r in rows
                                       if r["caller_kind"] == e440.REACH_PROD),
                "rows_test": sum(r["rows"] for r in rows
                                 if r["caller_kind"] == e440.REACH_TEST),
                "distinct_wrapper_names_graded": len({r["wrapper_name"] for r in rows}),
                "modules_the_rows_were_attributed_to": 1 if total else 0,
                "classes_defined_across_those_modules": classes,
                "class_census": ([{"module": "scripts/a.py", "parsed": True,
                                   "classes": {"Box": ["write"]} if classes else {},
                                   "class_count": classes,
                                   "method_count": classes}] if total else []),
                "rows_by_class_in_the_attributed_module": {"Box": hit} if hit else {},
                "per_name": per,
            },
        }

    cell = {"wrapper_name": "write", "wrapper_file": "scripts/a.py",
            "receiver_kind": RECV_SELF,
            "names_a_method_of_a_class_in_the_attributed_module": True,
            "caller_kind": e440.REACH_PROD, "rows": 4}
    good = face_of([cell, dict(cell, receiver_kind=RECV_UNBOUND,
                              names_a_method_of_a_class_in_the_attributed_module=False,
                              rows=6)])
    check("tally_clean", tally_problems(good) == [])
    check("verdict_partial", good["verdict"] == V_SOME)
    check("verdict_no_class_when_the_census_is_empty",
          verdict_for([dict(cell, names_a_method_of_a_class_in_the_attributed_module=False,
                            rows=2)], 0) == V_NO_CLASS)
    check("verdict_none_when_classes_exist_but_none_match",
          verdict_for([dict(cell, names_a_method_of_a_class_in_the_attributed_module=False,
                            rows=2)], 3) == V_NONE)
    check("verdict_all", verdict_for([cell], 1) == V_ALL)
    check("verdict_empty_face", verdict_for([], 0) == V_EMPTY)
    classless = face_of([dict(cell, names_a_method_of_a_class_in_the_attributed_module=False,
                              rows=5)])
    check("classless_face_is_clean", tally_problems(classless) == [])
    check("classless_face_verdict", classless["verdict"] == V_NO_CLASS)
    lying = json.loads(json.dumps(classless))
    lying["rows"][0]["names_a_method_of_a_class_in_the_attributed_module"] = True
    check("tally_catches_a_hit_with_no_class_behind_it", tally_problems(lying) != [])
    bad = json.loads(json.dumps(good))
    bad["summary"]["rows_by_receiver_kind"][RECV_SELF] = 99
    check("tally_catches_a_shifted_receiver_cell", tally_problems(bad) != [])
    bad2 = json.loads(json.dumps(good))
    bad2["summary"]["rows_naming_a_method_of_a_class_in_the_attributed_module"] = 0
    check("tally_catches_a_shifted_hit_count", tally_problems(bad2) != [])
    bad3 = json.loads(json.dumps(good))
    bad3["verdict"] = V_ALL
    check("tally_catches_a_carried_verdict", tally_problems(bad3) != [])
    bad4 = json.loads(json.dumps(good))
    bad4["rows"][0]["rows"] = 0
    check("tally_catches_an_empty_cell", tally_problems(bad4) != [])
    bad5 = json.loads(json.dumps(good))
    bad5["summary"]["per_name"][0]["attribute_call_rows"] = 1
    check("tally_catches_a_wrong_name_block", tally_problems(bad5) != [])
    bad6 = json.loads(json.dumps(good))
    bad6["rows"][0]["receiver_kind"] = "made_up_receiver"
    check("tally_catches_an_unknown_receiver_word", tally_problems(bad6) != [])
    bad7 = json.loads(json.dumps(good))
    bad7["summary"]["reproduces_e440_attribute_count"] = False
    check("tally_catches_a_carried_reproduction_flag", tally_problems(bad7) != [])
    bad8 = json.loads(json.dumps(good))
    bad8["rows"][0]["names_a_method_of_a_class_in_the_attributed_module"] = 1
    check("tally_catches_a_non_boolean_reading", tally_problems(bad8) != [])

    empty = face_of([], wrapper_names=[])
    check("empty_face_is_clean", tally_problems(empty) == [])
    check("empty_face_verdict", empty["verdict"] == V_EMPTY)

    for name in fails:
        print("FAIL", name)
    print("selftest %d/%d" % (legs - len(fails), legs))
    return 1 if fails else 0


def main(argv: list[str]) -> int:
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "run":
        face = build()
        path = write_face(face)
        problems = tally_problems(face)
        s = face["summary"]
        print("verdict: %s" % face["verdict"])
        print(json.dumps(s["rows_by_receiver_kind"], ensure_ascii=False))
        print("names a method of a class in the attributed module: %d of %d rows (%s)"
              % (s["rows_naming_a_method_of_a_class_in_the_attributed_module"],
                 s["attribute_call_rows_graded"], s["share_naming_a_method_there"]))
        print("reproduces E440's attribute count: %s (%d vs %d)"
              % (s["reproduces_e440_attribute_count"],
                 s["attr_call_rows_e440_classed_as_method_calls"],
                 s["attribute_call_rows_graded"]))
        print("face: %s" % _rel(path))
        if problems:
            for p in problems:
                print("PROBLEM", p)
            return 1
        return 0
    if cmd == "verify":
        problems = verify()
        print("verify problems=%s" % json.dumps(problems, ensure_ascii=False))
        return 1 if problems else 0
    if cmd == "check":
        # fast leg: re-derives every published tally from the published rows, no corpus walk, so a
        # face whose reading was edited without its row refuses the chain.  `verify` is the
        # ~6 minute live rebuild and is published on demand.
        face = _load(os.path.join(OUTDIR, FACE_NAME))
        problems = tally_problems(face)
        print("check problems=%s" % json.dumps(problems, ensure_ascii=False))
        if not problems:
            s = face.get("summary") or {}
            print("%d attribute call row(s) over %d module(s) / %d class(es) there: naming a "
                  "module method %d" % (s.get("attribute_call_rows_graded"),
                                        s.get("modules_the_rows_were_attributed_to"),
                                        s.get("classes_defined_across_those_modules"),
                                        s.get("rows_naming_a_method_of_a_class_in_the_"
                                              "attributed_module")))
        return 1 if problems else 0
    print("usage: run|verify|check|selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))