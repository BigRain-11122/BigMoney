"""E456: E450 graded the caller side and found 6,875 rows whose receiver is a name assigned a call
to something that is not a class defined in the caller.  Those are the rows where the receiver's
class, if it has one, came from somewhere else in the repository -- which is exactly the
attribution the name index would have got wrong.

This study takes that population and asks one more question: resolve the called name through the
caller's own imports to a module in this repository, index that module's classes and their methods,
and count how many rows name a method the imported class carries.  Rows whose callee does not
resolve in-tree are published as a residue, never folded into a zero.

Two readings are kept apart, as in E450:
  reading R (resolved) -- the callee resolves to a class defined in an in-repo module.
  reading H (hit)      -- that class carries the method name the row calls.  Only H is evidence
                          that the row reads an object of the imported class; R is the reach.

The population is not re-derived a second way: it is E450's own `graded_rows()` filtered to the
cross-module binding, and the face pins itself to E450's published 6,875 on that arm.

Usage:
    python scripts/e456_import_class.py run|verify|check|selftest
"""
from __future__ import annotations

import ast
import io
import json
import os
import sys
from datetime import date

import e437_name_recall as e437
import e440_shared_wrapper_names as e440
import e444_attr_method as e444
import e450_caller_class as e450
import growth_tolerance as gt

ROOT = e450.ROOT
ST = e450.ST
OUTDIR = ST
FACE_NAME = "importclass_latest.json"
DATED_PREFIX = "IMPORTCLASS"
CARD_ID = "E456-WHICH-CALL-BOUND-RECEIVER-NAMES-A-CLASS-IMPORTED-FROM-ANOTHER-MODULE"

BIND_OTHER_CALL = e450.BIND_OTHER_CALL

# The import form that carried the callee name into the caller.
FORM_MODULE = "a_module_level_import"
FORM_FUNCTION = "a_function_level_import"
FORM_MODULE_ALIASED = "a_module_level_aliased_import"
FORM_FUNCTION_ALIASED = "a_function_level_aliased_import"
FORM_VOCAB = (FORM_MODULE, FORM_FUNCTION, FORM_MODULE_ALIASED, FORM_FUNCTION_ALIASED)

# Why a callee did not resolve to an in-repo class.
R_BUILTIN = "the_callee_is_a_builtin_name"
R_LOCAL_DEF = "the_callee_is_defined_in_the_caller_itself"
R_NOT_IMPORTED = "the_callee_name_is_not_imported_bound_or_local_to_the_caller"
R_CALLEE_IS_A_MODULE = "the_callee_is_a_module_not_a_class"
R_MODULE_NOT_IN_TREE = "the_imported_module_has_no_file_in_this_repository"
R_MODULE_AMBIGUOUS = "the_module_name_matches_more_than_one_file"
R_IMPORT_NOT_A_CLASS = "the_imported_name_exists_in_that_module_but_is_not_a_class"
R_CLASS_NOT_IN_MODULE = "the_module_defines_no_name_of_that_kind"
R_CALLEE_SHAPE = "the_call_target_is_not_a_plain_name_or_qualified_name"
R_NO_CALL_VALUE = "the_receiver_has_no_call_on_the_assignment_sites_this_study_reads"
R_ATTRIBUTE_ON_AN_IMPORTED_OBJECT = "the_call_reads_an_attribute_of_an_imported_name_not_a_module"
RESIDUE_VOCAB = (R_BUILTIN, R_LOCAL_DEF, R_NOT_IMPORTED, R_CALLEE_IS_A_MODULE,
                 R_MODULE_NOT_IN_TREE, R_MODULE_AMBIGUOUS, R_IMPORT_NOT_A_CLASS,
                 R_CLASS_NOT_IN_MODULE, R_CALLEE_SHAPE, R_NO_CALL_VALUE,
                 R_ATTRIBUTE_ON_AN_IMPORTED_OBJECT)

OUTCOME_RESOLVED = "callee_resolved_to_a_class_in_an_in_repo_module"
OUTCOME_VOCAB = (OUTCOME_RESOLVED,) + RESIDUE_VOCAB

# Outcomes reached through an import of the caller: these carry the import's form, and only these
# may.  A builtin, a local factory and a name the caller never binds are not import stories.
IMPORT_INVOLVED = (OUTCOME_RESOLVED, R_CALLEE_IS_A_MODULE, R_MODULE_NOT_IN_TREE, R_MODULE_AMBIGUOUS,
                   R_IMPORT_NOT_A_CLASS, R_CLASS_NOT_IN_MODULE, R_ATTRIBUTE_ON_AN_IMPORTED_OBJECT)

V_EMPTY = "no_row_whose_receiver_is_bound_to_a_call_outside_the_callers_own_classes"
V_NONE_RESOLVED = "no_row_callee_resolves_to_a_class_defined_in_this_repository"
V_NONE_HIT = "no_resolved_row_names_a_method_that_the_imported_class_carries"
V_SOME = ("some_resolved_rows_name_a_method_that_the_imported_class_carries_but_resolution_is"
          "_static_alias_only")
V_ALL = "every_resolved_row_names_a_method_that_the_imported_class_carries"
VERDICT_VOCAB = (V_EMPTY, V_NONE_RESOLVED, V_NONE_HIT, V_SOME, V_ALL)

_IMPORT_CACHE: dict[str, dict] = {}
_FILES: set[str] | None = None


def _rel(path: str) -> str:
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


def _load(path: str) -> dict:
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def repo_files() -> set[str]:
    if _FILES is None:
        globals()["_FILES"] = set(e437.corpus())
    return _FILES


def module_to_rel(module: str, caller_rel: str, files: set[str] | None = None) -> list[str]:
    """Every corpus file a dotted module string could name, best-first.

    Absolute imports in this repository are written both ways (`import e437_name_recall` from a
    script that lives beside it, `import firm.risk.b_layer_filter` from the repo root), so a
    resolver that only joins the dotted path would miss the sibling spelling that most call sites
    actually use.  Ambiguity is returned, not resolved by guessing.
    """
    files = repo_files() if files is None else files
    if not module:
        return []
    out: list[str] = []
    if module.startswith("."):
        level = len(module) - len(module.lstrip("."))
        rest = module.lstrip(".")
        base = os.path.dirname(caller_rel)
        for _ in range(max(level - 1, 0)):
            base = os.path.dirname(base)
        parts = [p for p in rest.split(".") if p]
        if parts:
            out.append("/".join(([base] if base else []) + parts) + ".py")
            out.append("/".join(([base] if base else []) + parts) + "/__init__.py")
        elif base:
            out.append(base + "/__init__.py")
    else:
        parts = [p for p in module.split(".") if p]
        base = os.path.dirname(caller_rel)
        for i in range(0, len(parts)):
            tail = "/".join(parts[i:])
            out.append(tail + ".py")
            out.append(tail + "/__init__.py")
            if base:
                out.append(base + "/" + tail + ".py")
                out.append(base + "/" + tail + "/__init__.py")
        out.append(parts[-1] + "/__init__.py")
        if base:
            out.append(base + "/" + parts[-1] + "/__init__.py")
    seen: list[str] = []
    for cand in out:
        if cand in files and cand not in seen:
            seen.append(cand)
    return seen


def imports_of(rel: str) -> dict:
    """local name -> [{module, imported_name, aliased, form}], with the import's own scope."""
    if rel in _IMPORT_CACHE:
        return _IMPORT_CACHE[rel]
    tree = e450._tree(rel)
    if tree is None:
        _IMPORT_CACHE[rel] = {}
        return {}
    out: dict[str, list[dict]] = {}

    def record(local: str, module: str, imported_name, aliased: bool, in_func: bool) -> None:
        if in_func and aliased:
            form = FORM_FUNCTION_ALIASED
        elif in_func:
            form = FORM_FUNCTION
        elif aliased:
            form = FORM_MODULE_ALIASED
        else:
            form = FORM_MODULE
        out.setdefault(local, []).append({"module": module, "imported_name": imported_name,
                                          "aliased": aliased, "form": form})

    def walk(node, in_func: bool) -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for child in node.body:
                walk(child, True)
            return
        if isinstance(node, ast.Import):
            for alias in node.names:
                record(alias.asname or alias.name.split(".")[0], alias.name, None,
                       alias.asname is not None, in_func)
        elif isinstance(node, ast.ImportFrom):
            module = ("." * node.level) + (node.module or "")
            for alias in node.names:
                if alias.name == "*":
                    continue
                record(alias.asname or alias.name, module, alias.name,
                       alias.asname is not None, in_func)
        for child in ast.iter_child_nodes(node):
            walk(child, in_func)

    walk(tree, False)
    _IMPORT_CACHE[rel] = out
    return out


def resolve_callee(func, imports: dict, caller_rel: str,
                   files: set[str] | None = None) -> dict:
    """Resolve the name a receiver was assigned a call to.

    Returns {outcome, module, class_name, form}.  `outcome` is OUTCOME_RESOLVED only when the
    callee names a class that the module's own AST defines; everything else is a named residue.

    A builtin and a name the caller itself defines are checked before the import table: `open` is
    not "an import the caller forgot", and a local factory is not a cross-module name that failed
    to resolve.  Folding all three into one residue would let the headline "nothing resolves"
    hide which of the three is the population.
    """
    empty = {"outcome": None, "module": None, "class_name": None, "form": None}
    if isinstance(func, ast.Name):
        if func.id in BUILTIN_NAMES:
            return dict(empty, outcome=R_BUILTIN)
        if func.id in local_defs(caller_rel):
            return dict(empty, outcome=R_LOCAL_DEF)
        entries = imports.get(func.id) or []
        if not entries:
            return dict(empty, outcome=R_NOT_IMPORTED)
        entry = entries[0]
        if entry["imported_name"] is None:
            return dict(empty, outcome=R_CALLEE_IS_A_MODULE, form=entry["form"])
        cands = module_to_rel(entry["module"], caller_rel, files)
        if not cands:
            return dict(empty, outcome=R_MODULE_NOT_IN_TREE, form=entry["form"])
        if len(cands) > 1:
            return dict(empty, outcome=R_MODULE_AMBIGUOUS, form=entry["form"])
        defs = _defs(cands[0])
        if entry["imported_name"] in defs["classes"]:
            return {"outcome": OUTCOME_RESOLVED, "module": cands[0],
                    "class_name": entry["imported_name"], "form": entry["form"]}
        if entry["imported_name"] in defs["functions"]:
            return dict(empty, outcome=R_IMPORT_NOT_A_CLASS, module=cands[0],
                        class_name=entry["imported_name"], form=entry["form"])
        return dict(empty, outcome=R_CLASS_NOT_IN_MODULE, module=cands[0],
                    class_name=entry["imported_name"], form=entry["form"])
    if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
        entries = imports.get(func.value.id) or []
        if not entries:
            return dict(empty, outcome=R_NOT_IMPORTED)
        entry = entries[0]
        if entry["imported_name"] is not None:
            return dict(empty, outcome=R_ATTRIBUTE_ON_AN_IMPORTED_OBJECT, form=entry["form"])
        cands = module_to_rel(entry["module"], caller_rel, files)
        if not cands:
            return dict(empty, outcome=R_MODULE_NOT_IN_TREE, form=entry["form"])
        if len(cands) > 1:
            return dict(empty, outcome=R_MODULE_AMBIGUOUS, form=entry["form"])
        defs = _defs(cands[0])
        if func.attr in defs["classes"]:
            return {"outcome": OUTCOME_RESOLVED, "module": cands[0],
                    "class_name": func.attr, "form": entry["form"]}
        if func.attr in defs["functions"]:
            return dict(empty, outcome=R_IMPORT_NOT_A_CLASS, module=cands[0],
                        class_name=func.attr, form=entry["form"])
        return dict(empty, outcome=R_CLASS_NOT_IN_MODULE, module=cands[0],
                    class_name=func.attr, form=entry["form"])
    return dict(empty, outcome=R_CALLEE_SHAPE)


_CLASS_CACHE: dict[str, dict[str, set]] = {}
_DEFS_CACHE: dict[str, dict] = {}
_LOCAL_CACHE: dict[str, dict] = {}
BUILTIN_NAMES = frozenset(dir(__import__("builtins")))


def _defs(rel: str) -> dict:
    """Top-level classes and functions a module defines: what an import of it can name.

    Top level only: a method inside a class is not reachable as ``from mod import method``, so
    counting the whole AST as "the module defines that name" would grade an import of a method
    name as "a function, not a class" instead of as "no such name".
    """
    if rel not in _DEFS_CACHE:
        tree = e450._tree(rel)
        if tree is None:
            _DEFS_CACHE[rel] = {"classes": {}, "functions": set()}
        else:
            funcs = {n.name for n in tree.body
                     if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
            _DEFS_CACHE[rel] = {"classes": e444._class_index(tree), "functions": funcs}
    return _DEFS_CACHE[rel]


def local_defs(rel: str) -> set[str]:
    """Names the caller defines itself: a callee from here is not an import at all."""
    if rel not in _LOCAL_CACHE:
        tree = e450._tree(rel)
        if tree is None:
            _LOCAL_CACHE[rel] = set()
        else:
            own = {n.name for n in ast.walk(tree)
                   if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}
            _LOCAL_CACHE[rel] = own
    return _LOCAL_CACHE[rel]


def _classes(rel: str) -> dict[str, set]:
    if rel not in _CLASS_CACHE:
        _CLASS_CACHE[rel] = _defs(rel)["classes"]
    return _CLASS_CACHE[rel]


def grade_row(row: dict, files: set[str] | None = None) -> dict:
    """One E450 cross-module row, read through the caller's imports."""
    view = e450.file_view(row["caller_file"])
    name = row.get("receiver_name")
    values = (view or {}).get("assigns", {}).get(name) or []
    calls = [v for v in values if isinstance(v, ast.Call)]
    if not calls:
        return {"outcome": R_NO_CALL_VALUE, "module": None, "class_name": None,
                "form": None, "name_hit": False}
    imports = imports_of(row["caller_file"])
    first_residue = None
    for call in calls:
        res = resolve_callee(call.func, imports, row["caller_file"], files)
        if res["outcome"] != OUTCOME_RESOLVED:
            if first_residue is None:
                first_residue = res
            continue
        classes = _classes(res["module"])
        res["name_hit"] = row["wrapper_name"] in classes.get(res["class_name"], set())
        return res
    return dict(first_residue, name_hit=False)


def pin_for(mine: int, theirs: int) -> dict:
    """E455's growth rule against E450's published arm: the arm may grow, never shrink."""
    return {
        "e450_rows_binding_other_call": theirs,
        "now_rows_in_scope": mine,
        "delta": mine - theirs,
        "verdict": "growth_only_superset" if mine >= theirs else "population_moved_or_shrank",
    }


def verdict_for(total: int, resolved: int, hit: int) -> str:
    if not total:
        return V_EMPTY
    if not resolved:
        return V_NONE_RESOLVED
    if not hit:
        return V_NONE_HIT
    if hit == resolved:
        return V_ALL
    return V_SOME


def resolver_control(files: set[str] | None = None) -> dict:
    """Can the resolver hit anything at all?

    The headline is a zero, and a zero is only a measurement if the instrument is shown to fire.
    This walks every assignment whose value is a call to a plain or module-qualified name, over the
    same corpus the population came from, and publishes how many of those resolve to a class this
    repository defines.  A zero here would mean the zero in the headline is unmeasured.
    """
    files = repo_files() if files is None else files
    total = 0
    resolved = 0
    examples: list[dict] = []
    for rel in sorted(files):
        if os.path.basename(rel).startswith(("e456", "_e456", "run_e456")):
            continue
        tree = e450._tree(rel)
        if tree is None:
            continue
        imps = imports_of(rel)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            value = node.value
            if not isinstance(value, ast.Call):
                continue
            f = value.func
            if not (isinstance(f, ast.Name)
                    or (isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name))):
                continue
            total += 1
            r = resolve_callee(f, imps, rel, files)
            if r["outcome"] == OUTCOME_RESOLVED:
                resolved += 1
                if len(examples) < 5:
                    examples.append({"caller_file": rel, "module": r["module"],
                                     "class_name": r["class_name"],
                                     "import_form": r["form"]})
    return {"assignment_calls_to_a_plain_or_qualified_name": total,
            "resolved_to_a_class_in_an_in_repo_module": resolved,
            "share": round(resolved / total, 6) if total else None,
            "examples": examples}


def build(cutoff: str | None = None) -> dict:
    graded, cut = e450.graded_rows(cutoff, exclude=e450.EXCLUDE_PREFIXES
                                    + ("e456", "_e456", "run_e456"))
    scope = [g for g in graded if g["binding"] == BIND_OTHER_CALL]
    print("stage: %d cross-module rows in scope" % len(scope), flush=True)

    read: list[dict] = []
    for row in scope:
        g = grade_row(row)
        read.append({
            "wrapper_name": row["wrapper_name"],
            "wrapper_file": row["wrapper_file"],
            "caller_file": row["caller_file"],
            "caller_function": row["caller_function"],
            "caller_line": row["caller_line"],
            "caller_kind": row["caller_kind"],
            "receiver_name": row["receiver_name"],
            **g,
        })
    print("stage: %d rows read through the caller's imports" % len(read), flush=True)

    cells: dict[tuple, int] = {}
    for r in read:
        k = (r["outcome"], r["form"], bool(r.get("name_hit")))
        cells[k] = cells.get(k, 0) + 1
    published = [{"outcome": k[0], "import_form": k[1], "name_hit": k[2], "rows": v}
                 for k, v in sorted(cells.items(), key=lambda kv: (str(kv[0][0]),
                                                                   str(kv[0][1]), kv[0][2]))]

    total = sum(r["rows"] for r in published)
    resolved = sum(r["rows"] for r in published if r["outcome"] == OUTCOME_RESOLVED)
    hit = sum(r["rows"] for r in published if r["name_hit"])
    by_outcome = {v: 0 for v in OUTCOME_VOCAB}
    for r in published:
        by_outcome[r["outcome"]] = by_outcome.get(r["outcome"], 0) + r["rows"]
    by_form = {v: 0 for v in FORM_VOCAB}
    for r in published:
        if r["import_form"] is not None:
            by_form[r["import_form"]] = by_form.get(r["import_form"], 0) + r["rows"]
    by_form_resolved = {v: 0 for v in FORM_VOCAB}
    for r in published:
        if r["outcome"] == OUTCOME_RESOLVED:
            by_form_resolved[r["import_form"]] = by_form_resolved.get(r["import_form"], 0) + r["rows"]
    by_residue = {v: by_outcome.get(v, 0) for v in RESIDUE_VOCAB}

    modules = sorted({r["module"] for r in read if r["outcome"] == OUTCOME_RESOLVED})
    pairs = sorted({(r["module"], r["class_name"]) for r in read
                    if r["outcome"] == OUTCOME_RESOLVED})
    hit_modules: dict[str, int] = {}
    for r in read:
        if r.get("name_hit") and r["module"]:
            hit_modules[r["module"]] = hit_modules.get(r["module"], 0) + 1

    published_450 = _load(os.path.join(OUTDIR, e450.FACE_NAME))
    their_summary = (published_450.get("summary") or {})
    their_arm = int(((their_summary.get("rows_by_binding") or {})
                     .get(BIND_OTHER_CALL, 0)) or 0)
    pin = pin_for(total, their_arm)
    control = resolver_control()

    return {
        "study": "E456_which_call_bound_receiver_names_a_class_imported_from_another_module",
        "card": CARD_ID,
        "title": "the cross-module half of E450: does a receiver bound to a call resolve, through "
                 "the caller's imports, to a class in this repository that carries the method name",
        "generated": date.today().isoformat(),
        "evidence_cutoff": cut,
        "verdict": verdict_for(total, resolved, hit),
        "outcome_vocab": list(OUTCOME_VOCAB),
        "import_form_vocab": list(FORM_VOCAB),
        "residue_vocab": list(RESIDUE_VOCAB),
        "verdict_vocab": list(VERDICT_VOCAB),
        "summary": {
            "rows_in_scope_cross_module_binding": total,
            "rows_callee_resolved_in_tree": resolved,
            "rows_callee_residue": total - resolved,
            "rows_name_hit": hit,
            "share_of_scope_name_hit": round(hit / total, 4) if total else None,
            "share_of_resolved_name_hit": round(hit / resolved, 4) if resolved else None,
            "rows_by_outcome": by_outcome,
            "rows_by_import_form": by_form,
            "resolved_rows_by_import_form": by_form_resolved,
            "rows_by_residue": by_residue,
            "distinct_imported_modules": len(modules),
            "distinct_imported_class_pairs": len(pairs),
            "rows_by_hit_module": dict(sorted(hit_modules.items(),
                                              key=lambda kv: (-kv[1], kv[0]))),
            "population_pin": pin,
            "e450_rows_binding_other_call": their_arm,
            "resolver_control": control,
        },
        "rows": published,
        "resolved_examples": [
            {"module": r["module"], "class_name": r["class_name"], "import_form": r["form"],
             "method_name": r["wrapper_name"], "caller_file": r["caller_file"],
             "caller_line": r["caller_line"], "name_hit": r["name_hit"]}
            for r in read if r["outcome"] == OUTCOME_RESOLVED
        ][:25],
        "residue_examples": [
            {"outcome": r["outcome"], "method_name": r["wrapper_name"],
             "caller_file": r["caller_file"], "receiver_name": r["receiver_name"]}
            for r in read if r["outcome"] != OUTCOME_RESOLVED
        ][:25],
        "method_limits": [
            "resolution is static: an import that resolves to a file does not prove the call "
            "returns an instance of the class, so H is an upper bound on readers of that class",
            "only a plain name or a module-qualified name is resolved; a call on an attribute of an "
            "imported object, on a subscript, or on a chained call is published as residue rather "
            "than guessed",
            "a receiver name assigned several calls module-wide is graded on the first call that "
            "resolves in-tree; control flow is not modelled, so the same limit E450 publishes "
            "applies here",
            "sibling imports (`import e437_name_recall` from a script beside it) and dotted imports "
            "are both tried; a module string that matches more than one corpus file is published "
            "as ambiguous instead of resolved by preference",
            "the module universe is this study's corpus, so an import of a file outside it reads as "
            "not in tree -- that is a statement about the scan, not about the repository",
            "the headline is a zero, so the face publishes a resolver control over the whole corpus "
            "(every assignment whose value is a call to a plain or qualified name): if that control "
            "ever reads zero, the zero in the headline is an instrument failure, not a reading",
            "the study's own smoke leg lives in smoke_test.py, a shared file the population already "
            "includes; the handful of call rows the leg adds are counted as growth rather than "
            "excluded, because carving one study's lines out of a shared file would make the "
            "population depend on who is reading it",
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
    rows = face.get("rows") or []
    s = face.get("summary") or {}
    total = sum(r.get("rows", 0) for r in rows)
    resolved = sum(r["rows"] for r in rows if r.get("outcome") == OUTCOME_RESOLVED)
    hit = sum(r["rows"] for r in rows if r.get("name_hit"))
    if s.get("rows_in_scope_cross_module_binding") != total:
        problems.append("the scope total does not equal the sum of the published rows")
    if s.get("rows_callee_resolved_in_tree") != resolved:
        problems.append("rows_callee_resolved_in_tree does not re-derive from the rows")
    if s.get("rows_callee_residue") != total - resolved:
        problems.append("rows_callee_residue does not re-derive from the rows")
    if s.get("rows_name_hit") != hit:
        problems.append("rows_name_hit does not re-derive from the rows")
    if hit > resolved:
        problems.append("a name hit outside the resolved population")
    for r in rows:
        if r.get("outcome") not in OUTCOME_VOCAB:
            problems.append("a row outcome outside the published vocabulary")
            break
        if r.get("import_form") is not None and r["import_form"] not in FORM_VOCAB:
            problems.append("a row carries an import form outside the published vocabulary")
            break
        if r["outcome"] == OUTCOME_RESOLVED and r.get("import_form") is None:
            problems.append("a resolved row carries no import form")
            break
        if (r.get("import_form") is not None) != (r["outcome"] in IMPORT_INVOLVED):
            problems.append("the import form is present exactly when an import was involved")
            break
        if r.get("name_hit") and r["outcome"] != OUTCOME_RESOLVED:
            problems.append("a name hit whose callee did not resolve")
            break
    by_outcome = {v: 0 for v in OUTCOME_VOCAB}
    for r in rows:
        by_outcome[r["outcome"]] = by_outcome.get(r["outcome"], 0) + r["rows"]
    if by_outcome != (s.get("rows_by_outcome") or {}):
        problems.append("rows_by_outcome is carried, not derived from the rows")
    by_form = {v: 0 for v in FORM_VOCAB}
    for r in rows:
        if r["import_form"] is not None:
            by_form[r["import_form"]] = by_form.get(r["import_form"], 0) + r["rows"]
    if by_form != (s.get("rows_by_import_form") or {}):
        problems.append("rows_by_import_form is carried, not derived from the rows")
    resolved_form = {v: 0 for v in FORM_VOCAB}
    for r in rows:
        if r["outcome"] == OUTCOME_RESOLVED:
            resolved_form[r["import_form"]] = resolved_form.get(r["import_form"], 0) + r["rows"]
    if resolved_form != (s.get("resolved_rows_by_import_form") or {}):
        problems.append("resolved_rows_by_import_form is carried, not derived from the rows")
    if s.get("share_of_scope_name_hit") != (round(hit / total, 4) if total else None):
        problems.append("share_of_scope_name_hit is carried, not derived")
    if s.get("share_of_resolved_name_hit") != (round(hit / resolved, 4) if resolved else None):
        problems.append("share_of_resolved_name_hit is carried, not derived")
    pin = s.get("population_pin") or {}
    if pin.get("verdict") != "growth_only_superset":
        problems.append("the population against E450's published arm is not a growth-only superset")
    if pin.get("now_rows_in_scope") != total:
        problems.append("the pin's row total differs from the re-derived row total")
    if pin.get("e450_rows_binding_other_call") != s.get("e450_rows_binding_other_call"):
        problems.append("the pin does not carry E450's published arm")
    control = s.get("resolver_control") or {}
    if not (control.get("resolved_to_a_class_in_an_in_repo_module") or 0) > 0:
        problems.append("the resolver never fires on the whole corpus, so the zero is unmeasured")
    if not control.get("assignment_calls_to_a_plain_or_qualified_name"):
        problems.append("the resolver control read no assignment calls at all")
    if not control.get("examples"):
        problems.append("the resolver control publishes no hit example")
    if face.get("verdict") != verdict_for(total, resolved, hit):
        problems.append("the verdict does not re-derive from the published counts")
    return problems


def row_identity(row: dict) -> dict:
    cell = dict(row)
    cell["cell"] = "%s|%s" % (row.get("outcome"), row.get("import_form"))
    return cell


def _keyed(face: dict) -> dict:
    out = dict(face)
    out["rows"] = [row_identity(r) for r in (face.get("rows") or [])]
    return out


def tolerated(result: dict) -> bool:
    return result.get("verdict") in (gt.IDENTICAL, gt.PURE_GROWTH)


def verify(face: dict | None = None) -> list[str]:
    face = face or _load(os.path.join(OUTDIR, FACE_NAME))
    problems = tally_problems(face)
    live = build(face.get("evidence_cutoff"))
    if live["verdict"] != face["verdict"]:
        problems.append("live verdict %s != published %s" % (live["verdict"], face["verdict"]))
    tol = gt.classify(_keyed(face), _keyed(live), list_key="rows", row_id="cell",
                      class_fields=("name_hit",))
    print("growth: %s | %s" % (tol.get("verdict"), gt.describe(tol)))
    if not tolerated(tol):
        problems.append("the live reading is not a growth-only superset: %s" % tol.get("verdict"))
    return problems


FIXTURE_MODULE = "class Box:\n    def write(self, p):\n        return p\nclass Empty:\n    pass\n"
FIXTURE_CALLER = (
    "from mod import Box\n"
    "import mod as m\n"
    "from mod import Empty as E\n"
    "def go(path):\n"
    "    from other import Box as BX\n"
    "    a = Box()\n"
    "    a.write(path)\n"
    "    b = m.Box()\n"
    "    b.write(path)\n"
    "    c = E()\n"
    "    c.write(path)\n"
    "    d = build_box()\n"
    "    d.write(path)\n"
    "    e = m.Box().write\n"
    "    return a\n"
)


def selftest() -> int:
    legs = 0
    fails: list[str] = []

    def check(name: str, cond: bool) -> None:
        nonlocal legs
        legs += 1
        if not cond:
            fails.append(name)

    files = {"scripts/mod.py", "scripts/other.py", "scripts/caller.py"}
    imports = imports_of("scripts/caller.py") if False else None  # cache is filesystem-backed
    tree = ast.parse(FIXTURE_CALLER)

    # The import index walks the fixture, not the disk.
    saved = dict(_IMPORT_CACHE)
    _IMPORT_CACHE["scripts/caller.py"] = {}
    try:
        # Build the index by hand from the fixture so the leg does not read the repo.
        idx: dict[str, list[dict]] = {}
        for node in tree.body:
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    idx.setdefault(alias.asname or alias.name, []).append(
                        {"module": "mod", "imported_name": alias.name,
                         "aliased": alias.asname is not None, "form": FORM_MODULE})
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    idx.setdefault(alias.asname or alias.name.split(".")[0], []).append(
                        {"module": alias.name, "imported_name": None,
                         "aliased": alias.asname is not None, "form": FORM_MODULE_ALIASED})
        inner = tree.body[3]
        for node in inner.body:
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    idx.setdefault(alias.asname or alias.name, []).append(
                        {"module": "other", "imported_name": alias.name,
                         "aliased": alias.asname is not None, "form": FORM_FUNCTION_ALIASED})
        _IMPORT_CACHE["scripts/caller.py"] = idx
        imports = idx

        # Classes come from the fixture sources, not from disk.
        _DEFS_CACHE["scripts/mod.py"] = {"classes": e444._class_index(ast.parse(FIXTURE_MODULE)),
                                         "functions": {"helper"}}
        _DEFS_CACHE["scripts/other.py"] = {"classes": {"Box": {"write"}}, "functions": set()}
        _LOCAL_CACHE["scripts/caller.py"] = {"go"}

        check("module_resolves_sibling_spelling",
              module_to_rel("mod", "scripts/caller.py", files) == ["scripts/mod.py"])
        check("module_resolves_dotted_spelling",
              module_to_rel("scripts.mod", "scripts/caller.py", files) == ["scripts/mod.py"])
        check("module_absent_is_empty",
              module_to_rel("os.path", "scripts/caller.py", files) == [])

        from_import = resolve_callee(ast.Name(id="Box"), imports, "scripts/caller.py", files)
        check("from_import_resolves", from_import["outcome"] == OUTCOME_RESOLVED)
        check("from_import_form", from_import["form"] == FORM_MODULE)
        check("from_import_class", from_import["class_name"] == "Box")

        aliased_module = resolve_callee(ast.Attribute(value=ast.Name(id="m"), attr="Box"),
                                        imports, "scripts/caller.py", files)
        check("aliased_module_resolves", aliased_module["outcome"] == OUTCOME_RESOLVED)
        check("aliased_module_form", aliased_module["form"] == FORM_MODULE_ALIASED)

        not_imported = resolve_callee(ast.Name(id="build_box"), imports,
                                      "scripts/caller.py", files)
        check("not_imported_is_residue", not_imported["outcome"] == R_NOT_IMPORTED)

        plain_module = resolve_callee(ast.Name(id="m"), imports, "scripts/caller.py", files)
        check("a_module_is_not_a_class", plain_module["outcome"] == R_CALLEE_IS_A_MODULE)

        stdlib = resolve_callee(ast.Name(id="open"), imports, "scripts/caller.py", files)
        check("builtin_is_named_as_a_builtin", stdlib["outcome"] == R_BUILTIN)

        local = resolve_callee(ast.Name(id="go"), imports, "scripts/caller.py", files)
        check("local_definition_is_not_an_import", local["outcome"] == R_LOCAL_DEF)

        imported_function = resolve_callee(ast.Name(id="helper"), {
            "helper": [{"module": "mod", "imported_name": "helper", "aliased": False,
                        "form": FORM_MODULE}]}, "scripts/caller.py", files)
        check("imported_function_is_not_a_class",
              imported_function["outcome"] == R_IMPORT_NOT_A_CLASS)

        shape = resolve_callee(ast.Subscript(value=ast.Name(id="Box"), slice=ast.Constant(0)),
                               imports, "scripts/caller.py", files)
        check("odd_shape_residue", shape["outcome"] == R_CALLEE_SHAPE)

        attr_on_object = resolve_callee(
            ast.Attribute(value=ast.Name(id="Box"), attr="build"), imports,
            "scripts/caller.py", files)
        check("attribute_on_imported_name_residue",
              attr_on_object["outcome"] == R_ATTRIBUTE_ON_AN_IMPORTED_OBJECT)

        # A dotted module that exists both at the root and beside the caller is ambiguous, and the
        # resolver says so rather than preferring the sibling spelling.
        two = {"pkg/mod.py", "scripts/pkg/mod.py"}
        amb = resolve_callee(
            ast.Attribute(value=ast.Name(id="m"), attr="Box"),
            {"m": [{"module": "pkg.mod", "imported_name": None, "aliased": True,
                    "form": FORM_MODULE_ALIASED}]},
            "scripts/caller.py", two)
        check("ambiguous_module_is_a_residue", amb["outcome"] == R_MODULE_AMBIGUOUS)

        # A module that exists but has no such class.
        _DEFS_CACHE["scripts/other.py"] = {"classes": {}, "functions": set()}
        miss = resolve_callee(ast.Name(id="BX"), imports, "scripts/caller.py", files)
        check("missing_class_is_a_residue", miss["outcome"] == R_CLASS_NOT_IN_MODULE)
        _DEFS_CACHE["scripts/other.py"] = {"classes": {"Box": {"write"}}, "functions": set()}

        def row(name, method="write", file="scripts/caller.py", line=6):
            return {"wrapper_name": method, "wrapper_file": "scripts/mod.py",
                    "caller_file": file, "caller_function": "go", "caller_line": line,
                    "caller_kind": e440.REACH_PROD, "receiver_name": name}

        view = {"assigns": {"a": [ast.parse("Box()").body[0].value],
                            "b": [ast.parse("m.Box()").body[0].value],
                            "d": [ast.parse("build_box()").body[0].value]}}
        saved_view = e450._VIEW_CACHE.get("scripts/caller.py")
        e450._VIEW_CACHE["scripts/caller.py"] = view
        try:
            ga = grade_row(row("a"), files)
            check("grade_binding_hit", ga["outcome"] == OUTCOME_RESOLVED and ga["name_hit"])
            gb = grade_row(row("b"), files)
            check("grade_aliased_hit", gb["outcome"] == OUTCOME_RESOLVED and gb["name_hit"])
            gd = grade_row(row("d"), files)
            check("grade_residue_row", gd["outcome"] == R_NOT_IMPORTED and not gd["name_hit"])
            gnone = grade_row(row("zzz"), files)
            check("grade_no_call_value", gnone["outcome"] == R_NO_CALL_VALUE)
            gmiss = grade_row(row("a", method="close"), files)
            check("grade_method_absent", gmiss["outcome"] == OUTCOME_RESOLVED
                  and gmiss["name_hit"] is False)
        finally:
            if saved_view is None:
                e450._VIEW_CACHE.pop("scripts/caller.py", None)
            else:
                e450._VIEW_CACHE["scripts/caller.py"] = saved_view
    finally:
        _IMPORT_CACHE.clear()
        _IMPORT_CACHE.update(saved)
        _DEFS_CACHE.pop("scripts/mod.py", None)
        _DEFS_CACHE.pop("scripts/other.py", None)
        _LOCAL_CACHE.pop("scripts/caller.py", None)

    check("verdict_empty", verdict_for(0, 0, 0) == V_EMPTY)
    check("verdict_none_resolved", verdict_for(10, 0, 0) == V_NONE_RESOLVED)
    check("verdict_none_hit", verdict_for(10, 4, 0) == V_NONE_HIT)
    check("verdict_some", verdict_for(10, 4, 2) == V_SOME)
    check("verdict_all", verdict_for(10, 4, 4) == V_ALL)

    pin_grow = pin_for(11, 10)
    check("pin_growth", pin_grow["verdict"] == "growth_only_superset" and pin_grow["delta"] == 1)
    check("pin_shrink", pin_for(9, 10)["verdict"] == "population_moved_or_shrank")

    def cell(outcome=OUTCOME_RESOLVED, form=FORM_MODULE, hit=True, rows=1):
        return {"outcome": outcome, "import_form": form, "name_hit": hit, "rows": rows}

    def face_of(rows):
        total = sum(r["rows"] for r in rows)
        resolved = sum(r["rows"] for r in rows if r["outcome"] == OUTCOME_RESOLVED)
        hit = sum(r["rows"] for r in rows if r["name_hit"])
        by_outcome = {v: 0 for v in OUTCOME_VOCAB}
        for r in rows:
            by_outcome[r["outcome"]] = by_outcome.get(r["outcome"], 0) + r["rows"]
        by_form = {v: 0 for v in FORM_VOCAB}
        for r in rows:
            if r["import_form"] is not None:
                by_form[r["import_form"]] = by_form.get(r["import_form"], 0) + r["rows"]
        resolved_form = {v: 0 for v in FORM_VOCAB}
        for r in rows:
            if r["outcome"] == OUTCOME_RESOLVED:
                resolved_form[r["import_form"]] = (resolved_form.get(r["import_form"], 0)
                                                   + r["rows"])
        return {
            "verdict": verdict_for(total, resolved, hit),
            "rows": rows,
            "summary": {
                "rows_in_scope_cross_module_binding": total,
                "rows_callee_resolved_in_tree": resolved,
                "rows_callee_residue": total - resolved,
                "rows_name_hit": hit,
                "share_of_scope_name_hit": round(hit / total, 4) if total else None,
                "share_of_resolved_name_hit": round(hit / resolved, 4) if resolved else None,
                "rows_by_outcome": by_outcome,
                "rows_by_import_form": by_form,
                "resolved_rows_by_import_form": resolved_form,
                "rows_by_residue": {v: by_outcome.get(v, 0) for v in RESIDUE_VOCAB},
                "population_pin": {"e450_rows_binding_other_call": total,
                                   "now_rows_in_scope": total, "delta": 0,
                                   "verdict": "growth_only_superset"},
                "e450_rows_binding_other_call": total,
                "resolver_control": {
                    "assignment_calls_to_a_plain_or_qualified_name": 10,
                    "resolved_to_a_class_in_an_in_repo_module": 1,
                    "share": 0.1,
                    "examples": [{"caller_file": "scripts/caller.py"}],
                },
            },
        }

    good = face_of([cell(), cell(outcome=R_NOT_IMPORTED, form=None, hit=False)])
    check("tally_clean_face", tally_problems(good) == [])

    bad = face_of([cell()])
    bad["summary"]["rows_name_hit"] = 3
    check("tally_catches_carried_count", any("re-derive" in p for p in tally_problems(bad)))

    bad2 = face_of([cell()])
    bad2["rows"] = [cell(outcome=R_NOT_IMPORTED, form=FORM_MODULE, hit=False)]
    bad2["summary"] = face_of([cell(outcome=R_NOT_IMPORTED, form=None, hit=False)])["summary"]
    bad2["summary"]["rows_by_import_form"] = {v: 0 for v in FORM_VOCAB}
    check("tally_catches_a_form_on_a_non_import_row",
          any("present exactly when an import was involved" in p for p in tally_problems(bad2)))

    ok_import_residue = face_of([cell(outcome=R_MODULE_NOT_IN_TREE, form=FORM_MODULE, hit=False)])
    check("tally_accepts_a_form_on_an_import_residue", tally_problems(ok_import_residue) == [])
    check("import_residue_form_counted",
          ok_import_residue["summary"]["rows_by_import_form"][FORM_MODULE] == 1)

    bad3 = face_of([cell()])
    bad3["rows"] = [cell(outcome=R_NOT_IMPORTED, form=None, hit=True)]
    bad3["summary"]["rows_name_hit"] = 1
    bad3["summary"]["rows_callee_resolved_in_tree"] = 0
    bad3["summary"]["rows_callee_residue"] = 1
    bad3["summary"]["rows_by_outcome"] = {v: (1 if v == R_NOT_IMPORTED else 0)
                                          for v in OUTCOME_VOCAB}
    bad3["summary"]["rows_by_import_form"] = {v: 0 for v in FORM_VOCAB}
    bad3["verdict"] = V_SOME
    check("tally_catches_hit_without_resolution",
          any("name hit whose callee did not resolve" in p for p in tally_problems(bad3)))

    bad4 = face_of([cell()])
    bad4["summary"]["population_pin"]["verdict"] = "population_moved_or_shrank"
    check("tally_catches_broken_pin",
          any("growth-only superset" in p for p in tally_problems(bad4)))

    bad5 = face_of([cell()])
    bad5["verdict"] = V_NONE_HIT
    check("tally_catches_moved_verdict",
          any("verdict does not re-derive" in p for p in tally_problems(bad5)))

    bad6 = face_of([cell()])
    bad6["summary"]["resolver_control"]["resolved_to_a_class_in_an_in_repo_module"] = 0
    check("tally_catches_an_unmeasured_zero",
          any("unmeasured" in p for p in tally_problems(bad6)))

    ident = row_identity(cell(outcome=OUTCOME_RESOLVED, form=FORM_FUNCTION))
    check("identity_keys_outcome_and_form",
          ident["cell"] == "%s|%s" % (OUTCOME_RESOLVED, FORM_FUNCTION))
    check("identity_keeps_claim_out_of_cell",
          row_identity(cell(hit=False))["cell"] == row_identity(cell(hit=True))["cell"])

    stored = face_of([cell(rows=2), cell(outcome=R_NOT_IMPORTED, form=None, hit=False)])
    grown_live = face_of([cell(rows=3), cell(outcome=R_NOT_IMPORTED, form=None, hit=False)])
    shrunk_live = face_of([cell(rows=1), cell(outcome=R_NOT_IMPORTED, form=None, hit=False)])
    check("growth_tolerated",
          tolerated(gt.classify(_keyed(stored), _keyed(grown_live), list_key="rows",
                                row_id="cell", class_fields=("name_hit",))))
    check("shrink_refused",
          not tolerated(gt.classify(_keyed(stored), _keyed(shrunk_live), list_key="rows",
                                    row_id="cell", class_fields=("name_hit",))))

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
        print("rows=%d resolved=%d residue=%d hit=%d"
              % (s["rows_in_scope_cross_module_binding"], s["rows_callee_resolved_in_tree"],
                 s["rows_callee_residue"], s["rows_name_hit"]))
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