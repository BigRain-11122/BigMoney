"""E459: E456 resolved the cross-module half of E450 and left 928 rows whose callee module has no
file in this repository.  Those imports are mostly the standard library, which the instrument can
import even though the module is not in the tree -- so the module name is the only handle on the
receiver's class, and nobody has looked the class up.

This study takes that residue and asks: resolve the module name with the interpreter's own module
table (never the network), look the class up by the name the import form carried, and count how many
rows name a method that class carries.

Three readings, kept apart:
  reading M (reach)    -- the module name resolves to something importable.
  reading C (class)    -- that module carries a class with the name the import form named.
  reading H (hit)      -- the class carries the method name the row calls.

A row only reaches H through M and C.  Rows that do not reach M are published as a residue of their
own, never folded into a zero: "no class carries the name" and "the module could not be imported" are
different findings, and merging them would make the first invisible.

Usage:
    python scripts/e459_stdlib_class.py run|verify|check|selftest
"""
from __future__ import annotations

import ast
import csv
import importlib
import importlib.util
import io
import json
import os
import sys
from datetime import date

import e450_caller_class as e450
import e456_import_class as e456
import growth_tolerance as gt

ROOT = e450.ROOT
ST = e450.ST
OUTDIR = ST
FACE_NAME = "stdlibclass_latest.json"
DATED_PREFIX = "STDLIBCLASS"
CARD_ID = "E459-WHICH-STDLIB-CLASS-A-CROSS-MODULE-RECEIVER-IS-BOUND-TO"
EXCLUDE = e450.EXCLUDE_PREFIXES + ("e456", "_e456", "run_e456", "e459", "_e459", "run_e459")

BIND_OTHER_CALL = e450.BIND_OTHER_CALL
R_NOT_IN_TREE = e456.R_MODULE_NOT_IN_TREE
FORM_VOCAB = e456.FORM_VOCAB

# Why the row did or did not reach a class.
O_HIT = "module_imported_class_found_and_carries_the_method"
O_MISS = "module_imported_class_found_and_does_not_carry_the_method"
O_FACTORY = "module_carries_the_named_attribute_but_it_is_not_a_class"
O_ATTR_ABSENT = "module_carries_no_attribute_of_that_name"
O_NO_NAME = "the_import_form_carried_no_class_name_to_look_up"
O_NOT_IMPORTABLE = "module_name_does_not_resolve_to_an_importable_module"
O_IMPORT_RAISED = "module_resolves_but_importing_it_raised"
OUTCOME_VOCAB = (O_HIT, O_MISS, O_FACTORY, O_ATTR_ABSENT, O_NO_NAME,
                 O_NOT_IMPORTABLE, O_IMPORT_RAISED)
# Which readings a class was actually looked up for.
CLASS_LOOKED_UP = (O_HIT, O_MISS)

V_EMPTY = "no_rows_fell_in_this_residue"
V_NONE_IMPORTABLE = "no_row_reached_an_importable_module_so_the_hit_count_is_unmeasured"
V_NONE_CLASS = "every_importable_module_lacks_a_class_of_the_named_kind"
V_NONE_HIT = "no_looked_up_class_carries_the_method_the_row_calls"
V_ALL = "every_looked_up_class_carries_the_method_the_row_calls"
V_SOME = "some_looked_up_classes_carry_the_method_and_some_do_not"
VERDICT_VOCAB = (V_EMPTY, V_NONE_IMPORTABLE, V_NONE_CLASS, V_NONE_HIT, V_ALL, V_SOME)


# ---------------------------------------------------------------- module resolution
def resolve_name(module_name: str, class_name: str | None, method_name: str | None,
                 importer=None) -> dict:
    """Look a dotted module name up in the interpreter's own table, then the class, then the method.

    `importer` is injectable so the selftest can stand in a fake table; the production path is
    importlib.  find_spec is tried before the import because an import of a broken module can be
    slow or noisy, and the two failures ("no such module" vs "it raised") are different findings.
    """
    importer = importlib if importer is None else importer
    if not module_name:
        return {"outcome": O_NOT_IMPORTABLE, "why": "no_module_name", "method_present": False}
    try:
        spec = importer.util.find_spec(module_name)
    except (ImportError, AttributeError, ValueError, TypeError):
        spec = None
    if spec is None:
        return {"outcome": O_NOT_IMPORTABLE, "why": "find_spec_returned_none",
                "method_present": False}
    try:
        mod = importer.import_module(module_name)
    except Exception as exc:  # noqa: BLE001 - an import that raises is a finding, not a crash
        return {"outcome": O_IMPORT_RAISED, "why": type(exc).__name__, "method_present": False}
    if not class_name:
        return {"outcome": O_NO_NAME, "why": "no_class_name_in_the_import_form",
                "method_present": False}
    if not hasattr(mod, class_name):
        return {"outcome": O_ATTR_ABSENT, "why": "module_has_no_attribute_of_that_name",
                "method_present": False}
    cls = getattr(mod, class_name)
    if not isinstance(cls, type):
        return {"outcome": O_FACTORY, "why": "the_attribute_is_callable_but_not_a_class",
                "method_present": False}
    present = bool(method_name) and hasattr(cls, method_name) and callable(
        getattr(cls, method_name, None))
    return {"outcome": O_HIT if present else O_MISS, "why": "looked_up",
            "method_present": present}


# ---------------------------------------------------------------- population
def callee_handle(row: dict, files: set[str] | None = None) -> dict | None:
    """The (module, class, form) of the first call in the receiver's assignments that E456 could
    not place in the tree.  E456 returns the module name as None on that arm, so it is recovered
    here from the same import table rather than re-parsed a second way."""
    view = e450.file_view(row["caller_file"])
    name = row.get("receiver_name")
    values = (view or {}).get("assigns", {}).get(name) or []
    calls = [v for v in values if isinstance(v, ast.Call)]
    if not calls:
        return None
    imports = e456.imports_of(row["caller_file"])
    for call in calls:
        res = e456.resolve_callee(call.func, imports, row["caller_file"], files)
        if res["outcome"] != R_NOT_IN_TREE:
            continue
        f = call.func
        if isinstance(f, ast.Name):
            entries = imports.get(f.id) or []
            if not entries:
                continue
            entry = entries[0]
            return {"module_name": entry["module"], "class_name": entry["imported_name"],
                    "form": entry["form"]}
        if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name):
            entries = imports.get(f.value.id) or []
            if not entries:
                continue
            entry = entries[0]
            if entry["imported_name"] is not None:
                continue
            return {"module_name": entry["module"], "class_name": f.attr, "form": entry["form"]}
    return None


def build(cutoff: str | None = None) -> dict:
    graded, cut = e450.graded_rows(cutoff, exclude=EXCLUDE)
    scope = [g for g in graded if g["binding"] == BIND_OTHER_CALL]
    print("stage: %d cross-module rows in scope" % len(scope), flush=True)

    read: list[dict] = []
    for row in scope:
        handle = callee_handle(row, files=None)
        if handle is None:
            continue
        res = resolve_name(handle["module_name"], handle["class_name"], row["wrapper_name"])
        read.append({
            "wrapper_name": row["wrapper_name"],
            "caller_file": row["caller_file"],
            "receiver_name": row["receiver_name"],
            "module_name": handle["module_name"],
            "class_name": handle["class_name"],
            "import_form": handle["form"],
            **res,
        })
    print("stage: %d rows whose callee module is not in the tree" % len(read), flush=True)

    cells: dict[tuple, int] = {}
    for r in read:
        k = (r["outcome"], r["import_form"])
        cells[k] = cells.get(k, 0) + 1
    published = [{"outcome": k[0], "import_form": k[1], "rows": v}
                 for k, v in sorted(cells.items(), key=lambda kv: (str(kv[0][0]), str(kv[0][1])))]

    by_outcome = {v: 0 for v in OUTCOME_VOCAB}
    for r in published:
        by_outcome[r["outcome"]] = by_outcome.get(r["outcome"], 0) + r["rows"]
    total = sum(by_outcome.values())

    hit = by_outcome[O_HIT]
    looked_up = by_outcome[O_HIT] + by_outcome[O_MISS]
    importable = sum(by_outcome[v] for v in OUTCOME_VOCAB
                     if v not in (O_NOT_IMPORTABLE, O_IMPORT_RAISED))

    by_module: dict[str, dict] = {}
    for r in read:
        cell = by_module.setdefault(r["module_name"], {"module": r["module_name"],
                                                      "rows": 0, "imported": 0, "hit": 0}
                                    | {v: 0 for v in OUTCOME_VOCAB})
        cell["rows"] += 1
        cell[r["outcome"]] += 1
        if r["outcome"] not in (O_NOT_IMPORTABLE, O_IMPORT_RAISED):
            cell["imported"] += 1
        if r["outcome"] == O_HIT:
            cell["hit"] += 1
    modules_published = sorted(by_module.values(), key=lambda c: (-c["rows"], c["module"]))

    by_form = {v: {"importable": 0, "looked_up": 0, "hit": 0} for v in FORM_VOCAB}
    for r in read:
        if r["import_form"] not in by_form:
            continue
        b = by_form[r["import_form"]]
        if r["outcome"] not in (O_NOT_IMPORTABLE, O_IMPORT_RAISED):
            b["importable"] += 1
        if r["outcome"] in (O_HIT, O_MISS):
            b["looked_up"] += 1
        if r["outcome"] == O_HIT:
            b["hit"] += 1

    named: dict[tuple, int] = {}
    for r in read:
        k = (r["module_name"], r["class_name"] or "")
        named[k] = named.get(k, 0) + 1
    top_named = [{"module": k[0], "attribute": k[1], "rows": v}
                 for k, v in sorted(named.items(), key=lambda kv: (-kv[1], str(kv[0])))[:20]]

    residue_examples = [{"module_name": r["module_name"], "why": r["why"],
                         "caller_file": r["caller_file"], "class_name": r["class_name"]}
                        for r in read if r["outcome"] in (O_NOT_IMPORTABLE, O_IMPORT_RAISED)][:25]
    hit_examples = [{"module_name": r["module_name"], "class_name": r["class_name"],
                     "method": r["wrapper_name"], "caller_file": r["caller_file"]}
                    for r in read if r["outcome"] == O_HIT][:25]

    prev = _load(os.path.join(OUTDIR, e456.FACE_NAME))
    their_residue = ((prev or {}).get("summary") or {}).get("rows_by_residue", {}).get(
        R_NOT_IN_TREE)
    pin = {"e456_rows_on_this_residue": their_residue, "now_rows_in_scope": total,
           "delta": None if their_residue is None else total - their_residue,
           "verdict": ("unpinned" if their_residue is None else
                       ("growth_only_superset" if total >= their_residue
                        else "population_moved_or_shrank"))}

    verdict = _verdict_for(total, importable, looked_up, hit)

    face = {
        "study": "E459",
        "card": CARD_ID,
        "title": "the standard-library classes behind E456's 928 out-of-tree receivers",
        "evidence_cutoff": cut,
        "generated": date.today().isoformat(),
        "rows": published,
        "module_rows": modules_published,
        "summary": {
            "rows_whose_callee_module_is_not_in_the_tree": total,
            "rows_by_outcome": by_outcome,
            "reach": {
                "importable": importable,
                "share_importable": round(importable / total, 6) if total else None,
                "class_looked_up": looked_up,
                "share_looked_up": round(looked_up / total, 6) if total else None,
                "hit": hit,
                "share_hit_of_looked_up": round(hit / looked_up, 6) if looked_up else None,
                "share_hit_of_all_rows": round(hit / total, 6) if total else None,
            },
            "rows_by_import_form": by_form,
            "distinct_modules": len(by_module),
            "top_named_attributes": top_named,
            "population_pin": pin,
        },
        "outcome_vocab": list(OUTCOME_VOCAB),
        "verdict_vocab": list(VERDICT_VOCAB),
        "verdict": verdict,
        "residue_examples": residue_examples,
        "hit_examples": hit_examples,
    }
    return face


def _verdict_for(total: int, importable: int, looked_up: int, hit: int) -> str:
    if not total:
        return V_EMPTY
    if not importable:
        return V_NONE_IMPORTABLE
    if not looked_up:
        return V_NONE_CLASS
    if not hit:
        return V_NONE_HIT
    if hit == looked_up:
        return V_ALL
    return V_SOME


# ---------------------------------------------------------------- io + checks
def _load(path: str) -> dict | None:
    try:
        with io.open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def write_face(face: dict) -> dict:
    os.makedirs(OUTDIR, exist_ok=True)
    dated = os.path.join(OUTDIR, "%s-%s.json" % (DATED_PREFIX, face["evidence_cutoff"]))
    latest = os.path.join(OUTDIR, FACE_NAME)
    for path in (dated, latest):
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
    bad = [c for c in face["module_rows"] if c["rows"] != sum(c[v] for v in OUTCOME_VOCAB)]
    rows = [{"module": c["module"], "rows": c["rows"], "importable": c["imported"],
             "hit": c["hit"], "hit_rate_of_looked_up":
                 (round(c[O_HIT] / (c[O_HIT] + c[O_MISS]), 6) if (c[O_HIT] + c[O_MISS]) else None)}
            for c in face["module_rows"]]
    path = os.path.join(OUTDIR, "stdlibclass_by_module_%s.csv" % face["evidence_cutoff"])
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["module", "rows", "importable", "hit",
                                           "hit_rate_of_looked_up"])
        w.writeheader()
        w.writerows(rows)
    return {"dated": dated, "latest": latest, "csv": path, "module_rows_disagreeing": len(bad)}


def tally_problems(face: dict) -> list[str]:
    problems: list[str] = []
    s = face["summary"]
    bo = s["rows_by_outcome"]
    if sum(bo.values()) != s["rows_whose_callee_module_is_not_in_the_tree"]:
        problems.append("rows_by_outcome does not add to the row total")
    rows_total = sum(r["rows"] for r in face["rows"])
    if rows_total != s["rows_whose_callee_module_is_not_in_the_tree"]:
        problems.append("published cells do not add to the row total")
    mod_total = sum(c["rows"] for c in face["module_rows"])
    if mod_total != s["rows_whose_callee_module_is_not_in_the_tree"]:
        problems.append("module rows do not add to the row total")
    if s["reach"]["hit"] != bo[O_HIT]:
        problems.append("reach.hit disagrees with rows_by_outcome")
    if s["reach"]["class_looked_up"] != bo[O_HIT] + bo[O_MISS]:
        problems.append("reach.class_looked_up disagrees with rows_by_outcome")
    for r in face["rows"]:
        if r["outcome"] not in OUTCOME_VOCAB:
            problems.append("unknown outcome %r" % r["outcome"])
    return problems


def verify(path: str | None = None) -> list[str]:
    face = _load(path or os.path.join(OUTDIR, FACE_NAME))
    if not face:
        return ["face missing"]
    problems = tally_problems(face)
    # the instrument must be shown to fire: the published hit examples must re-resolve
    for ex in face["hit_examples"][:10]:
        res = resolve_name(ex["module_name"], ex["class_name"], ex["method"])
        if res["outcome"] != O_HIT:
            problems.append("published hit %s.%s.%s no longer resolves as a hit"
                            % (ex["module_name"], ex["class_name"], ex["method"]))
    for ex in face["residue_examples"][:10]:
        res = resolve_name(ex["module_name"], ex["class_name"], "x")
        if res["outcome"] not in (O_NOT_IMPORTABLE, O_IMPORT_RAISED):
            problems.append("published residue %s now resolves" % ex["module_name"])
    return problems


# ---------------------------------------------------------------- selftest
class _FakeSpec:
    def __init__(self, ok):
        self.ok = ok


class _FakeImportlib:
    """A module table with three shapes: a class that carries the method, a class that does not,
    and a name that never resolves."""

    class _Util:
        @staticmethod
        def find_spec(name):
            return _FakeSpec(True) if name in ("good", "hollow") else None

    util = _Util()

    class _Good:
        class Thing:
            def carry(self):
                return 1

    class _Hollow:
        class Thing:
            pass

    @classmethod
    def import_module(cls, name):
        if name == "good":
            return cls._Good
        if name == "hollow":
            return cls._Hollow
        raise ImportError(name)


def _raises_import(name):
    raise RuntimeError("boom")


def selftest() -> int:
    legs: list[tuple[str, bool, str]] = []

    def leg(name, ok, note=""):
        legs.append((name, bool(ok), note))

    r = resolve_name("good", "Thing", "carry", importer=_FakeImportlib)
    leg("hit: resolved class carries the method", r["outcome"] == O_HIT, r["outcome"])
    r = resolve_name("good", "Thing", "absent_method", importer=_FakeImportlib)
    leg("miss: resolved class lacks the method", r["outcome"] == O_MISS, r["outcome"])
    r = resolve_name("hollow", "Thing", "carry", importer=_FakeImportlib)
    leg("miss: hollow class is not mistaken for a hit", r["outcome"] == O_MISS, r["outcome"])
    r = resolve_name("hollow", "Nope", "carry", importer=_FakeImportlib)
    leg("absent: a module without the attribute is not a factory",
        resolve_name("hollow", "Nope", "carry", importer=_FakeImportlib)["outcome"]
        == O_ATTR_ABSENT)
    r = resolve_name("never_there_xyz", "Thing", "carry", importer=_FakeImportlib)
    leg("residue: unresolvable name is not folded into a zero",
        r["outcome"] == O_NOT_IMPORTABLE, r["outcome"])
    leg("residue: empty module name is a residue, not a hit",
        resolve_name("", "Thing", "carry", importer=_FakeImportlib)["outcome"] == O_NOT_IMPORTABLE)
    leg("threshold: receipt imports a real stdlib class through the live table",
        resolve_name("io", "BytesIO", "write")["outcome"] == O_HIT)
    leg("threshold: a factory that is not a class is a residue of its own kind",
        resolve_name("csv", "writer", "writerow")["outcome"] == O_FACTORY)

    leg("verdict: empty population is named", _verdict_for(0, 0, 0, 0) == V_EMPTY)
    leg("verdict: nothing importable is named",
        _verdict_for(10, 0, 0, 0) == V_NONE_IMPORTABLE)
    leg("verdict: no class looked up is named", _verdict_for(10, 4, 0, 0) == V_NONE_CLASS)
    leg("verdict: no hit is named", _verdict_for(10, 4, 2, 0) == V_NONE_HIT)
    leg("verdict: all hits is named", _verdict_for(10, 4, 2, 2) == V_ALL)
    leg("verdict: partial is named", _verdict_for(10, 4, 2, 1) == V_SOME)

    face = {"summary": {"rows_whose_callee_module_is_not_in_the_tree": 2,
                        "rows_by_outcome": {v: 0 for v in OUTCOME_VOCAB},
                        "reach": {"hit": 0, "class_looked_up": 0}},
            "rows": [], "module_rows": [], "hit_examples": [], "residue_examples": []}
    face["summary"]["rows_by_outcome"][O_MISS] = 2
    problems = tally_problems(face)
    leg("tally: a zeroed ledger with an empty cell list is caught",
        any("do not add" in p for p in problems))

    for name, ok, note in legs:
        print("%s %s%s" % ("[PASS]" if ok else "[FAIL]", name, (" -- " + note) if note else ""))
    print("selftest %d/%d" % (sum(1 for _, ok, _ in legs if ok), len(legs)))
    return 0 if all(ok for _, ok, _ in legs) else 1


def main(argv: list[str]) -> int:
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "selftest":
        return selftest()
    if cmd in ("run", "build"):
        face = build()
        paths = write_face(face)
        problems = tally_problems(face)
        s = face["summary"]
        print("rows=%d importable=%d looked_up=%d hit=%d modules=%d"
              % (s["rows_whose_callee_module_is_not_in_the_tree"], s["reach"]["importable"],
                 s["reach"]["class_looked_up"], s["reach"]["hit"], s["distinct_modules"]))
        print("verdict=%s" % face["verdict"])
        print("pin=%s" % json.dumps(s["population_pin"], ensure_ascii=False))
        print("wrote=%s%s" % (paths["latest"], " problems=%s" % problems if problems else ""))
        return 0 if not problems else 1
    if cmd in ("verify", "check"):
        problems = verify()
        for p in problems:
            print("[FAIL] " + p)
        print("verify %s" % ("clean" if not problems else "%d problem(s)" % len(problems)))
        return 0 if not problems else 1
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    raise SystemExit(main(sys.argv))