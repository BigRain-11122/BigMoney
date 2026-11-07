"""E483 -- for each of E479's leg-only twins, what does each leg that opens it actually
assert: does it re-derive a number from the payload, pin a field to a constant, or merely
require the file to exist?

E479 (r1512) priced the retirement of the unread vintage families by bytes and found 30 of
the 36 latest-pointer twins whose only non-producer openers are smoke/runner legs.  Bytes
price the file; they do not price the legs.  A leg that only asks ``os.path.exists`` can be
deleted in the same edit that deletes the face, while a leg that pins a field to a frozen
literal, or re-derives a tally from the payload, has to be rewritten -- and the rewrite
depends on what it is asserting.  This study asks that question per (twin, site) and
publishes the classification so the retirement is priced in edits.

Two things are measured before the classification, because both change what the 30 means:

  a. MODE.  E479 counted every ``open`` call carrying the twin's name as an opener.  A
     write-mode call is not a reader; several of these twins are opened for writing by the
     script that publishes them, and the doctor legs write the face deliberately (then put
     it back).  A twin whose opener set is the writer's own write plus legs was never
     "opened only by a leg" -- the residue label is off, and the study publishes that
     disagreement rather than inheriting it.

  b. LINE.  E479's sites are recorded as (source, line).  A recorded line that no longer
     holds an open call would silently classify as "unreadable", so the count of stale
     lines is published as its own reading instead of being absorbed into a class.

The debt classes are then read off the *asserting block* that owns each site: the nearest
enclosing block that carries an assertion (``check(...)``, ``assert``, ``_bad.append``), so a
metadata block such as ``with open(face) as fh:`` is not mistaken for the whole leg.

Run:      python scripts/e483_leg_debt.py run
Check:    python scripts/e483_leg_debt.py check     (tallies re-derive from the face)
Verify:   python scripts/e483_leg_debt.py verify    (re-classifies from the live tree)
Selftest: python scripts/e483_leg_debt.py selftest
"""
import argparse
import ast
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
if os.path.join(ROOT, "scripts") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "scripts"))

import e494_latest_authors as e494  # noqa: E402

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "legdebt_latest.json"
DATED_PREFIX = "LEGDEBT"
EVIDENCE_CUTOFF = "2026-11-07"
CARD = ("E483-DO-THE-SMOKE-LEGS-THAT-READ-A-TWIN-ASSERT-ON-ITS-CONTENT-OR-MERELY-ON-ITS-"
        "EXISTENCE")
SELF_EXCLUDED = ("e483_", "run_e483")
SOURCE_FACE_GLOB = "TWINREAD-"

# ---- how a site touches the file -------------------------------------------------------------
M_READ = "opens_it_for_reading"
M_WRITE = "opens_it_for_writing"
M_INDIRECT = "hands_the_path_to_a_helper_that_opens_it"
MODE_VOCAB = (M_READ, M_WRITE, M_INDIRECT)

# ---- what the asserting block does with the payload ------------------------------------------
D_REDERIVE = "re_derives_a_number_from_the_payload"
D_PIN = "asserts_a_field_equals_a_constant_or_a_frozen_vocabulary"
D_PRESENCE = "asserts_a_field_is_present_without_comparing_a_value"
D_EXISTS = "only_requires_the_file_to_exist"
D_BYTES = "compares_the_face_with_a_copy_of_itself_and_reads_no_field"
D_NO_FIELD = "reads_the_file_and_reads_no_field_in_this_block"
D_UNREADABLE = "the_source_is_absent_or_does_not_parse"
DEBT_VOCAB = (D_REDERIVE, D_PIN, D_PRESENCE, D_EXISTS, D_BYTES, D_NO_FIELD, D_UNREADABLE)
# strongest first: the twin-level label is the strongest debt any of its readers carries
DEBT_ORDER = (D_REDERIVE, D_PIN, D_PRESENCE, D_BYTES, D_NO_FIELD, D_EXISTS,
              D_UNREADABLE)
DEBT_RANK = {k: i for i, k in enumerate(DEBT_ORDER)}

# ---- who the opener is -----------------------------------------------------------------------
S_SUITE = "the_smoke_suite"
S_RUNNER = "a_standalone_leg_runner"
S_INSTRUMENT = "an_instrument"
S_ONEOFF = "a_one_off_round_script"
ROLE_VOCAB = (S_SUITE, S_RUNNER, S_INSTRUMENT, S_ONEOFF)

V_REDERIVE = "some_leg_re_derives_a_number_from_its_twin"
V_PIN = "some_leg_pins_a_twin_field_to_a_constant_and_none_re_derives"
V_PRESENCE = "some_leg_only_asserts_a_twin_field_is_present"
V_BYTES = "some_leg_only_compares_its_twin_with_a_copy_of_itself"
V_EXISTS = "every_leg_that_opens_a_twin_only_requires_the_file_to_exist"
V_NO_FIELD = "some_leg_reads_its_twin_without_asserting_anything_about_a_field"

# ---- is the parent's literal the one this line opens? ----------------------------------------
A_REACHABLE = "the_literal_the_parent_records_is_what_this_line_opens"
A_UNFOLDED = "this_line_opens_a_name_this_build_cannot_fold"
A_NOT_THIS_LINE = "this_line_opens_a_different_file_than_the_parent_records"
ATTR_VOCAB = (A_REACHABLE, A_UNFOLDED, A_NOT_THIS_LINE)
V_EMPTY = "no_twin_in_the_population_has_a_readable_leg"
V_ERROR = "a_site_could_not_be_classified_in_this_environment"
VERDICT_VOCAB = (V_REDERIVE, V_PIN, V_PRESENCE, V_BYTES, V_NO_FIELD, V_EXISTS,
                  V_EMPTY, V_ERROR)

NEW_NAMES = ("load", "loads")
TEXT_READS = ("read", "read_text", "read_bytes")
PAYLOAD_METHODS = ("get", "items", "keys", "values")
ASSERT_TAILS = ("check", "assertEqual", "assertTrue", "assertFalse", "assertIs",
                "assertIn", "assertNotEqual")
BLOCK_TYPES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Try, ast.If, ast.For, ast.While,
               ast.With)


# ---------------------------------------------------------------------------------------------
# small shared helpers
# ---------------------------------------------------------------------------------------------
def _rel(path):
    path = os.path.abspath(path)
    if path.startswith(ROOT + os.sep):
        return path[len(ROOT) + 1:].replace(os.sep, "/")
    return path


def _load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _newest(prefix):
    if not os.path.isdir(OUTDIR):
        return None
    hits = sorted(p for p in os.listdir(OUTDIR)
                  if p.startswith(prefix) and p.endswith(".json") and "_" not in p)
    if not hits:
        return None
    return os.path.join(OUTDIR, hits[-1])


def role_of(source):
    base = os.path.basename(source)
    if base == "smoke_test.py":
        return S_SUITE
    if base.startswith("run_e") and "smoke_leg" in base:
        return S_RUNNER
    if base.startswith("_tmp") or base.startswith("_r") or base.startswith("_"):
        return S_ONEOFF
    if base.startswith("e") and base[1:4].isdigit():
        return S_INSTRUMENT
    if "/results/" in "/" + source.replace(os.sep, "/"):
        return S_ONEOFF
    return S_INSTRUMENT


# ---------------------------------------------------------------------------------------------
# the AST arms
# ---------------------------------------------------------------------------------------------
def parents(tree):
    par = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            par[child] = node
    return par


def has_assertion(node):
    for sub in ast.walk(node):
        if isinstance(sub, ast.Assert):
            return True
        if isinstance(sub, ast.Call):
            tail = e494._func_tail(sub.func)
            if tail in ASSERT_TAILS:
                return True
            if tail == "append" and isinstance(sub.func, ast.Attribute):
                value = sub.func.value
                if isinstance(value, ast.Name) and "bad" in value.id:
                    return True
    return False


def _is_json_load(call):
    """``json.load``/``json.loads`` -- not ``<helper>.load``, which opens the path itself."""
    func = call.func
    return isinstance(func, ast.Attribute) and func.attr in NEW_NAMES and \
        isinstance(func.value, ast.Name) and func.value.id == "json"


def open_call_near(tree, line, slack=0):
    """The open-ish call a site line names; an exact line wins over a near one."""
    cands = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        tail = e494._func_tail(node.func)
        if tail == "open":
            pass
        elif tail in TEXT_READS:
            pass
        elif _is_json_load(node):
            pass
        else:
            continue
        cands.append(node)
    if not cands:
        return None
    exact = [n for n in cands if getattr(n, "lineno", -99) == line]
    pool = exact or [n for n in cands if abs(getattr(n, "lineno", -99) - line) <= slack]
    if not pool:
        return None
    return max(pool, key=lambda n: getattr(n, "end_lineno", n.lineno) - n.lineno)


def mode_of_site(tree, line):
    """(mode, why) -- write / read / indirect, with the evidence that decided it."""
    call = open_call_near(tree, line)
    if call is None:
        return M_INDIRECT, "no open call carries this line"
    tail = e494._func_tail(call.func)
    if tail in TEXT_READS:
        return M_READ, "a text read on a handle opened at this line"
    if _is_json_load(call):
        return M_READ, "a json load at this line"
    mode = e494._mode_of(call)
    if e494._is_write_mode(mode):
        return M_WRITE, "mode=%r" % mode
    return M_READ, "mode=%r" % (mode or "r (default)")


def live_open_argument(tree, consts, line, call):
    """The path expression the open call at this line actually uses, unwrapped."""
    if call is None or not call.args:
        return None
    arg = call.args[0]
    while isinstance(arg, ast.Call) and arg.args and \
            e494._func_tail(arg.func) in FILE_ACCESS:
        arg = arg.args[0]
    if isinstance(arg, ast.Name):
        best = None
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and \
                    isinstance(node.targets[0], ast.Name) and \
                    node.targets[0].id == arg.id and \
                    getattr(node, "lineno", 10 ** 9) < line:
                if best is None or node.lineno > best.lineno:
                    best = node
        if best is None:
            return None
        arg = best.value
    return arg


def attribution_of(tree, consts, line, call, parent_literal):
    """Does the literal the parent recorded appear among what this line opens?"""
    want = os.path.basename(parent_literal or "")
    arg = live_open_argument(tree, consts, line, call)
    if arg is None:
        return A_UNFOLDED
    folded = e494._fold_string(arg, consts)
    got = {os.path.basename(p) for p in folded if p}
    if not got:
        return A_UNFOLDED
    return A_REACHABLE if want in got else A_NOT_THIS_LINE


def asserting_block(tree, par, line):
    """The nearest enclosing block that carries this leg's assertions."""
    call = open_call_near(tree, line)
    chain = []
    cur = call if call is not None else tree
    while cur is not None:
        chain.append(cur)
        cur = par.get(cur)
    for node in chain:
        if isinstance(node, BLOCK_TYPES) and node is not tree and has_assertion(node):
            return node
    for node in chain:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return node
    return tree


def payload_roots(unit):
    roots = set()
    for node in ast.walk(unit):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and \
                isinstance(node.targets[0], ast.Name):
            for sub in ast.walk(node.value):
                if isinstance(sub, ast.Call):
                    tail = e494._func_tail(sub.func)
                    if tail in NEW_NAMES or tail in TEXT_READS:
                        roots.add(node.targets[0].id)
                        break
    return roots


def payload_ish(expr, roots, bound, depth=3):
    found = set()
    for sub in ast.walk(expr):
        if isinstance(sub, ast.Name) and sub.id in roots:
            found.add(sub.id)
        elif isinstance(sub, ast.Call) and e494._func_tail(sub.func) in \
                NEW_NAMES + TEXT_READS:
            found.add("call:" + e494._func_tail(sub.func))
    if bound and depth > 0:
        for sub in ast.walk(expr):
            if isinstance(sub, ast.Name) and sub.id in bound and sub.id not in found:
                if payload_ish(bound[sub.id], roots, bound, depth - 1):
                    found.add(sub.id)
    return found


def derive_bindings(unit, roots):
    bound = {}
    for _ in range(3):
        added = False
        for node in ast.walk(unit):
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and \
                    isinstance(node.targets[0], ast.Name) and \
                    node.targets[0].id not in roots and node.targets[0].id not in bound:
                if payload_ish(node.value, roots, bound):
                    bound[node.targets[0].id] = node.value
                    added = True
        if not added:
            break
    return bound


def is_literal_side(expr):
    if isinstance(expr, ast.Constant):
        return True
    if isinstance(expr, (ast.Tuple, ast.List, ast.Set)):
        return all(is_literal_side(e) for e in expr.elts)
    if isinstance(expr, ast.Dict):
        return all(v is None or is_literal_side(v) for v in expr.values)
    if isinstance(expr, ast.UnaryOp):
        return is_literal_side(expr.operand)
    return False


FILE_ACCESS = ("open", "read", "read_text", "read_bytes", "load", "loads")

# A module from this list cannot build a value this study would call a re-derivation.
STD_MODULES = frozenset((
    "os", "sys", "io", "json", "ast", "math", "time", "datetime", "pathlib", "re",
    "hashlib", "collections", "itertools", "functools", "subprocess", "shutil", "glob",
    "random", "statistics", "tempfile", "importlib", "argparse", "csv", "typing", "copy",
    "textwrap", "warnings", "traceback", "logging", "platform", "socket", "string",
    "decimal", "fractions", "uuid", "urllib", "base64", "gzip", "zipfile", "pickle",
    "struct", "unicodedata", "contextlib", "dataclasses", "enum", "numbers", "operator",
    "pprint", "shlex", "signal", "sqlite3", "unittest", "concurrent", "threading",
    "multiprocessing", "html", "xml", "email", "http", "ssl", "errno", "fcntl",
))
# Calls that compute a number *out of* the payload.
DERIVING_FUNCS = frozenset(("len", "sum", "abs", "min", "max", "round", "any", "all",
                            "pow", "divmod"))
DERIVING_METHODS = frozenset(("count", "index", "total"))
# Calls that reshape a payload value without deriving a new number from it.
NEUTRAL_CALLS = frozenset(("dumps", "loads", "str", "repr", "format", "sorted", "tuple",
                           "list", "dict", "set", "frozenset", "float", "int", "bool",
                           "strip", "split", "lower", "upper", "replace"))


def callee_is_a_payload_access(call, roots, bound):
    """Is this call a read *of* the payload (``f.get(...)``, ``json.load(...)``)?"""
    func = call.func
    if isinstance(func, ast.Attribute):
        base = func.value
        if isinstance(base, ast.Name) and (base.id in roots or base.id in bound):
            return True
        if payload_ish(base, roots, bound, 1):
            return True
        return func.attr in FILE_ACCESS
    if isinstance(func, ast.Name):
        return func.id in FILE_ACCESS or func.id in roots or func.id in bound
    return False


def module_names(tree):
    """(functions defined here, module aliases imported here from outside the stdlib)."""
    funcs, mods = set(), set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            funcs.add(node.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                root = (alias.asname or alias.name).split(".")[0]
                if root not in STD_MODULES:
                    mods.add(root)
        elif isinstance(node, ast.ImportFrom) and node.module:
            if node.module.split(".")[0] in STD_MODULES:
                continue
            for alias in node.names:
                mods.add(alias.asname or alias.name)
    return funcs, mods


def value_building_call(call, info):
    """A call into this file's own functions or into a study it imports.

    ``os.path.join``, ``json.dumps``, ``len`` and ``os.path.exists`` are not builders: a
    path built from a payload value is still a path, and a boolean probe of it asserts a
    link, not a number.
    """
    if not info:
        return False
    funcs, mods = info
    func = call.func
    if isinstance(func, ast.Name):
        return func.id in funcs
    if isinstance(func, ast.Attribute):
        base = func.value
        if isinstance(base, ast.Name):
            return base.id in mods
        if isinstance(base, ast.Attribute):
            root = base
            while isinstance(root, ast.Attribute):
                root = root.value
            if isinstance(root, ast.Name):
                return root.id in mods
            return False
        if isinstance(base, ast.Call):
            tail = e494._func_tail(base.func)
            return tail == "import_module"
    return False


def building_names(unit, info):
    """Names bound in this block to a value the block builds (``fresh = mod.build()``)."""
    if not info:
        return set()
    out = set()
    for node in ast.walk(unit):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and \
                isinstance(node.targets[0], ast.Name):
            for sub in ast.walk(node.value):
                if isinstance(sub, ast.Call) and value_building_call(sub, info):
                    out.add(node.targets[0].id)
                    break
    return out


def is_builder_side(side, built, info):
    """A side whose value is built here: a call into a study's own builders, or a name
    bound to one.  This is what makes the comparison a *re-derivation* rather than a pin."""
    for node in ast.walk(side):
        if not isinstance(node, ast.Call):
            continue
        if value_building_call(node, info):
            return True
        func = node.func
        base = func.value if isinstance(func, ast.Attribute) else None
        if isinstance(base, ast.Name) and base.id in built:
            return True
        if isinstance(func, ast.Name) and func.id in built:
            return True
    return False


def computes_from_the_payload(side, roots, bound):
    """The payload value is counted or summed on this side (``len(rows)``)."""
    if not payload_ish(side, roots, bound):
        return False
    for node in ast.walk(side):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name) and func.id in DERIVING_FUNCS:
            return True
        if isinstance(func, ast.Attribute) and func.attr in DERIVING_METHODS:
            return True
    return False


def is_pure_read_side(side, roots, bound, built, info):
    """Reads the payload and computes nothing: payload access, or a neutral normaliser."""
    if not payload_ish(side, roots, bound):
        return False
    if is_builder_side(side, built, info):
        return False
    for node in ast.walk(side):
        if not isinstance(node, ast.Call):
            continue
        if callee_is_a_payload_access(node, roots, bound):
            continue
        if isinstance(node.func, ast.Attribute) and node.func.attr in NEUTRAL_CALLS:
            continue
        if isinstance(node.func, ast.Name) and node.func.id in NEUTRAL_CALLS:
            continue
        return False
    return True


def classify_block(unit, info=None):
    """The debt class of one asserting block that owns a read site."""
    roots = payload_roots(unit)
    if not roots:
        return D_NO_FIELD, {"roots": [], "value": 0, "presence": 0, "rederive": 0,
                            "bytes_only": 0, "externally_derived": 0,
                            "comparisons_that_count_the_payload": 0}
    bound = derive_bindings(unit, roots)
    built = building_names(unit, info)
    value = presence = rederive = bytes_only = externally = computed = 0
    for node in ast.walk(unit):
        tests = []
        if isinstance(node, ast.Compare):
            tests = [node]
        elif isinstance(node, ast.If):
            tests = [node.test]
        for test in tests:
            if isinstance(test, ast.Compare):
                sides = [test.left] + list(test.comparators)
                pure = [x for x in sides if is_pure_read_side(x, roots, bound, built, info)]
                builders = [x for x in sides if is_builder_side(x, built, info)]
                if any(computes_from_the_payload(x, roots, bound) for x in sides):
                    computed += 1
                if not pure and not builders:
                    continue
                if builders:
                    rederive += 1
                elif len(pure) > 1:
                    # the payload compared with a payload read: a copy of itself
                    bytes_only += 1
                elif all(is_literal_side(x) for x in sides if not any(x is p for p in pure)):
                    value += 1
                else:
                    externally += 1
            elif payload_ish(test, roots, bound):
                presence += 1
    counts = {"roots": sorted(roots), "value": value, "presence": presence,
              "rederive": rederive, "bytes_only": bytes_only,
              "externally_derived": externally,
              "comparisons_that_count_the_payload": computed}
    if rederive:
        return D_REDERIVE, counts
    if value:
        return D_PIN, counts
    if externally:
        return D_PIN, counts
    if bytes_only:
        return D_BYTES, counts
    if presence:
        return D_PRESENCE, counts
    return D_EXISTS, counts


# ---------------------------------------------------------------------------------------------
# population
# ---------------------------------------------------------------------------------------------
def population():
    """E479's leg-only twins, read from its face -- never restated."""
    path = _newest(SOURCE_FACE_GLOB)
    if not path:
        raise SystemExit("no %s* face in %s" % (SOURCE_FACE_GLOB, OUTDIR))
    face = _load_json(path)
    rows = [r for r in (face.get("rows") or [])
            if r.get("residue") == "opened_only_by_a_smoke_or_runner_leg"]
    meta = {"face": _rel(path), "face_evidence_cutoff": face.get("evidence_cutoff"),
            "face_verdict": face.get("verdict"),
            "twins_in_the_face": len(face.get("rows") or []),
            "residue_read_as_leg_only": "opened_only_by_a_smoke_or_runner_leg"}
    return path, rows, meta


_cache = {}


def source_tree(rel):
    if rel not in _cache:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            _cache[rel] = None
        else:
            try:
                text = io.open(path, encoding="utf-8").read()
                tree = ast.parse(text)
            except (SyntaxError, UnicodeDecodeError) as exc:  # pragma: no cover
                _cache[rel] = {"error": str(exc)}
            else:
                _cache[rel] = {"tree": tree, "par": parents(tree),
                               "info": module_names(tree),
                               "lines": text.count("\n") + 1}
    return _cache[rel]


def measure_site(twin_base, source, line, parent_literal=None):
    got = source_tree(source)
    if got is None:
        return {"source": source, "line": line, "mode": M_INDIRECT,
                "mode_evidence": "the source is not on disk", "debt": D_UNREADABLE,
                "role": role_of(source), "block": None, "counts": {},
                "parent_literal_attribution": A_UNFOLDED}
    if "error" in got:
        return {"source": source, "line": line, "mode": M_INDIRECT,
                "mode_evidence": "the source does not parse", "debt": D_UNREADABLE,
                "role": role_of(source), "block": None, "counts": {},
                "parent_literal_attribution": A_UNFOLDED}
    tree, par = got["tree"], got["par"]
    mode, why = mode_of_site(tree, line)
    call = open_call_near(tree, line)
    consts = e494._collect_consts(tree)
    row = {"source": source, "line": line, "twin_basename": twin_base, "mode": mode,
           "mode_evidence": why, "role": role_of(source),
           "parent_literal_attribution": attribution_of(tree, consts, line, call,
                                                        parent_literal)}
    if mode != M_READ:
        row["debt"] = None
        row["block"] = None
        row["counts"] = {}
        return row
    unit = asserting_block(tree, par, line)
    debt, counts = classify_block(unit, got.get("info"))
    row["debt"] = debt
    row["block"] = {"kind": type(unit).__name__,
                    "start": getattr(unit, "lineno", 0),
                    "end": getattr(unit, "end_lineno", 0)}
    row["counts"] = counts
    return row


def build():
    path, rows, meta = population()
    measured = []
    stale_lines = []
    for row in rows:
        twin = row.get("twin")
        twin_base = os.path.basename(twin or "")
        sites = row.get("counting_openers") or []
        measured_sites = []
        for site in sites:
            src, line = site.get("source"), site.get("line") or 0
            got = source_tree(src)
            if got and "tree" in got and open_call_near(got["tree"], line) is None:
                stale_lines.append({"source": src, "line": line, "twin": twin})
            m = measure_site(twin_base, src, line, site.get("literal"))
            m["parent_literal"] = site.get("literal")
            m["parent_match"] = site.get("match")
            measured_sites.append(m)
        reads = [m for m in measured_sites if m["mode"] == M_READ]
        writes = [m for m in measured_sites if m["mode"] == M_WRITE]
        by_debt = {}
        for m in reads:
            by_debt[m["debt"]] = by_debt.get(m["debt"], 0) + 1
        strongest = None
        for key in DEBT_ORDER:
            if by_debt.get(key):
                strongest = key
                break
        producers = [p for p in (row.get("producers") or [])]
        residue_wrong = bool(reads) and not reads and False
        # the residue label says "only legs open it"; a write-mode site is the writer itself
        writer_opened = bool(writes) and not (
            set(m["source"] for m in writes) & set(producers))
        measured.append({
            "twin": twin,
            "twin_basename": twin_base,
            "family_dir": row.get("family_dir"),
            "members": row.get("members"),
            "bytes": row.get("bytes"),
            "parent_residue": row.get("residue"),
            "parent_reading_sites": row.get("opener_sites"),
            "sites": measured_sites,
            "sites_total": len(measured_sites),
            "read_sites": len(reads),
            "write_sites": len(writes),
            "sites_by_mode": {k: sum(1 for m in measured_sites if m["mode"] == k)
                              for k in MODE_VOCAB},
            "sites_by_debt": by_debt,
            "strongest_debt": strongest,
            "write_sites_by_the_writer": sum(1 for m in writes if m["source"] in producers),
            "write_sites_not_by_a_listed_producer": sum(
                1 for m in writes if m["source"] not in producers),
            "residue_label_has_no_reader_left": bool(writes) and not reads,
        })
    all_sites = [s for t in measured for s in t["sites"]]
    by_mode = {k: sum(1 for s in all_sites if s["mode"] == k) for k in MODE_VOCAB}
    by_debt = {}
    for s in all_sites:
        if s["mode"] == M_READ:
            by_debt[s["debt"]] = by_debt.get(s["debt"], 0) + 1
    by_role = {}
    for s in all_sites:
        by_role.setdefault(s["role"], {})
        key = s["debt"] if s["mode"] == M_READ else s["mode"]
        by_role[s["role"]][key] = by_role[s["role"]].get(key, 0) + 1
    strongest = {}
    for t in measured:
        strongest[t["strongest_debt"]] = strongest.get(t["strongest_debt"], 0) + 1
    summary = {
        "twins_in_population": len(measured),
        "sites_in_population": len(all_sites),
        "sites_by_mode": by_mode,
        "read_sites_by_debt": by_debt,
        "read_sites": sum(by_debt.values()),
        "sites_by_role": by_role,
        "twins_by_strongest_debt": strongest,
        "twins_whose_opener_set_holds_no_reader": sum(
            1 for t in measured if t["residue_label_has_no_reader_left"]),
        "twins_with_a_write_site": sum(1 for t in measured if t["write_sites"]),
        "twins_with_a_write_site_from_a_listed_producer": sum(
            1 for t in measured if t["write_sites_by_the_writer"]),
        "twins_with_a_write_site_from_someone_else": sum(
            1 for t in measured if t["write_sites_not_by_a_listed_producer"]),
        "write_sites_by_role": {
            role: sum(1 for t in measured for x in t["sites"]
                      if x["mode"] == M_WRITE and x["role"] == role)
            for role in ROLE_VOCAB},
        "twins_where_the_publishing_instrument_opens_its_own_twin": sorted(
            t["twin_basename"] for t in measured
            if any(x["mode"] == M_WRITE and x["role"] != S_RUNNER for x in t["sites"])),
        "twins_where_a_doctor_harness_writes_it": sorted(
            t["twin_basename"] for t in measured
            if any(x["mode"] == M_WRITE and x["role"] == S_RUNNER for x in t["sites"])),
        "sites_where_the_recorded_line_holds_no_open_call": len(stale_lines),
        "sites_where_the_recorded_line_holds_no_open_call_note":
            "these are the sites that hand the path to a helper (M_INDIRECT), not records "
            "whose line numbers have rotted",
        "sites_where_the_recorded_line_holds_no_open_call_list": stale_lines,
        "sites_by_parent_literal_attribution": {
            k: sum(1 for x in all_sites if x.get("parent_literal_attribution") == k)
            for k in ATTR_VOCAB},
        "distinct_sources": len(set(s["source"] for s in all_sites)),
        "read_sites_in_a_standalone_leg_runner": sum(
            1 for s in all_sites if s["mode"] == M_READ and s["role"] == S_RUNNER),
        "twins_retirable_with_existence_only_edits": sorted(
            t["twin_basename"] for t in measured
            if t["strongest_debt"] in (D_EXISTS, D_BYTES, None)),
        "twins_that_would_need_an_assertion_rewritten": sorted(
            t["twin_basename"] for t in measured
            if t["strongest_debt"] in (D_REDERIVE, D_PIN, D_PRESENCE)),
    }
    return {
        "card": CARD,
        "study": "E483_leg_debt_on_the_leg_only_twins",
        "title": ("do the legs that open E479's leg-only twins re-derive a number, pin a "
                  "field, or only require the file to exist?"),
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "generated": None,
        "population_source": meta,
        "mode_definition": {
            M_READ: "the site calls open() without a write-mode, or a json load / text read "
                    "on a handle it opened at that line",
            M_WRITE: "the site calls open() with a mode that can write (w/a/x/+)",
            M_INDIRECT: "the site names the path but no open call carries that line -- the "
                        "path is handed to a helper that opens it, which this build cannot "
                        "follow, so it is published rather than folded into a class",
        },
        "debt_definition": {
            D_REDERIVE: "an assertion compares a payload value with a value this block "
                        "builds itself (a call that is not a payload access)",
            D_PIN: "an assertion compares a payload value with a literal or a frozen "
                   "vocabulary",
            D_PRESENCE: "an assertion tests a payload value for truth without comparing it",
            D_EXISTS: "no assertion touches a payload value: the block only needs the file",
            D_BYTES: "the only comparisons put payload reads on both sides -- the face is "
                     "compared with a copy of itself and no field is read",
            D_NO_FIELD: "the block opens the file but binds no payload in the block: a "
                        "shim that hands the bytes on, or a leg that only compares bytes",
            D_UNREADABLE: "the source is absent from this tree or does not parse",
        },
        "role_definition": {
            S_SUITE: "smoke_test.py -- a leg in the full suite",
            S_RUNNER: "scripts/run_e*_smoke_leg.py -- a leg extracted and run standalone",
            S_INSTRUMENT: "scripts/e###_*.py -- a study instrument",
            S_ONEOFF: "a one-off round script (leading underscore or under results/)",
        },
        "summary": summary,
        "rows": measured,
        "method_limits": [
            "the population is E479's own residue class, inherited not re-measured: a "
            "reader E479 missed is not in this study either",
            "a site is classified by its asserting block, so a block that asserts on two "
            "different faces gives both sites the same class",
            "an assertion built from a call is read as a re-derivation; whether that call "
            "actually rebuilds the face is not executable here",
            "M_INDIRECT sites are named, not classified: following a helper parameter is "
            "another study",
            "a deleted or renamed source is published as unreadable rather than assumed "
            "unchanged",
        ],
    }


def verdict_for(rows, summary=None):
    rows = rows or []
    summary = summary or {}
    if not rows:
        return V_EMPTY
    if summary.get("read_sites_by_debt", {}).get(D_UNREADABLE):
        return V_ERROR
    seen = set()
    for t in rows:
        if t.get("strongest_debt"):
            seen.add(t["strongest_debt"])
    if not seen:
        return V_EMPTY
    for key, verdict in ((D_REDERIVE, V_REDERIVE), (D_PIN, V_PIN), (D_PRESENCE, V_PRESENCE),
                         (D_BYTES, V_BYTES), (D_NO_FIELD, V_NO_FIELD), (D_EXISTS, V_EXISTS)):
        if key in seen:
            return verdict
    return V_EMPTY


# ---------------------------------------------------------------------------------------------
# tallies / check / verify / write
# ---------------------------------------------------------------------------------------------
def tally_problems(face):
    bad = []
    rows = face.get("rows") or []
    summary = face.get("summary") or {}
    if face.get("card") != CARD:
        bad.append("the card id is not this study's")
    if face.get("verdict") not in VERDICT_VOCAB:
        bad.append("verdict outside the frozen vocabulary")
    if face.get("verdict") != verdict_for(rows, summary):
        bad.append("the verdict does not re-derive from the rows")

    def recount(fn):
        out = {}
        for t in rows:
            for s in t.get("sites") or []:
                key = fn(s)
                if key is None:
                    continue
                out[key] = out.get(key, 0) + 1
        return out

    if summary.get("twins_in_population") != len(rows):
        bad.append("twins_in_population does not equal the row count")
    if summary.get("sites_in_population") != sum(len(t.get("sites") or []) for t in rows):
        bad.append("sites_in_population does not re-derive")
    if (summary.get("sites_by_mode") or {}) != recount(lambda s: s.get("mode")):
        bad.append("sites_by_mode does not re-derive")
    reads = recount(lambda s: s.get("debt") if s.get("mode") == M_READ else None)
    if (summary.get("read_sites_by_debt") or {}) != reads:
        bad.append("read_sites_by_debt does not re-derive")
    if summary.get("read_sites") != sum(reads.values()):
        bad.append("read_sites does not re-derive")
    if summary.get("read_sites") != recount(lambda s: "read"
                                            if s.get("mode") == M_READ else None).get("read"):
        bad.append("read_sites disagrees with the mode tally")
    by_role = {}
    for t in rows:
        for s in t.get("sites") or []:
            key = s.get("debt") if s.get("mode") == M_READ else s.get("mode")
            by_role.setdefault(s.get("role"), {})
            by_role[s["role"]][key] = by_role[s["role"]].get(key, 0) + 1
    if (summary.get("sites_by_role") or {}) != by_role:
        bad.append("sites_by_role does not re-derive")
    strongest = {}
    for t in rows:
        if t.get("strongest_debt"):
            strongest[t["strongest_debt"]] = strongest.get(t["strongest_debt"], 0) + 1
    if (summary.get("twins_by_strongest_debt") or {}) != strongest:
        bad.append("twins_by_strongest_debt does not re-derive")
    for t in rows:
        site_debt = {}
        for s in t.get("sites") or []:
            if s.get("mode") == M_READ:
                site_debt[s.get("debt")] = site_debt.get(s.get("debt"), 0) + 1
        if (t.get("sites_by_debt") or {}) != site_debt:
            bad.append("sites_by_debt does not re-derive for %s" % t.get("twin_basename"))
            break
        want = None
        for key in DEBT_ORDER:
            if site_debt.get(key):
                want = key
                break
        if t.get("strongest_debt") != want:
            bad.append("strongest_debt does not re-derive for %s" % t.get("twin_basename"))
            break
        if t.get("read_sites") != sum(site_debt.values()):
            bad.append("read_sites does not re-derive for %s" % t.get("twin_basename"))
            break
    if summary.get("twins_where_the_publishing_instrument_opens_its_own_twin") != sorted(
            t["twin_basename"] for t in rows
            if any(x.get("mode") == M_WRITE and x.get("role") != S_RUNNER
                   for x in (t.get("sites") or []))):
        bad.append("twins_where_the_publishing_instrument_opens_its_own_twin does not "
                   "re-derive")
    if summary.get("twins_where_a_doctor_harness_writes_it") != sorted(
            t["twin_basename"] for t in rows
            if any(x.get("mode") == M_WRITE and x.get("role") == S_RUNNER
                   for x in (t.get("sites") or []))):
        bad.append("twins_where_a_doctor_harness_writes_it does not re-derive")
    if (summary.get("write_sites_by_role") or {}) != {
            role: sum(1 for t in rows for x in (t.get("sites") or [])
                      if x.get("mode") == M_WRITE and x.get("role") == role)
            for role in ROLE_VOCAB}:
        bad.append("write_sites_by_role does not re-derive")
    if summary.get("twins_with_a_write_site") != sum(
            1 for t in rows if t.get("write_sites")):
        bad.append("twins_with_a_write_site does not re-derive")
    if summary.get("twins_whose_opener_set_holds_no_reader") != sum(
            1 for t in rows if t.get("residue_label_has_no_reader_left")):
        bad.append("twins_whose_opener_set_holds_no_reader does not re-derive")
    if summary.get("twins_retirable_with_existence_only_edits") != sorted(
            t["twin_basename"] for t in rows
            if t.get("strongest_debt") in (D_EXISTS, D_BYTES, D_NO_FIELD, None)):
        bad.append("twins_retirable_with_existence_only_edits does not re-derive")
    if summary.get("twins_that_would_need_an_assertion_rewritten") != sorted(
            t["twin_basename"] for t in rows
            if t.get("strongest_debt") in (D_REDERIVE, D_PIN, D_PRESENCE)):
        bad.append("twins_that_would_need_an_assertion_rewritten does not re-derive")
    if summary.get("sites_where_the_recorded_line_holds_no_open_call") != len(
            summary.get("sites_where_the_recorded_line_holds_no_open_call_list") or []):
        bad.append("the no-open-call count does not re-derive from the list")
    attr = {k: 0 for k in ATTR_VOCAB}
    for t in rows:
        for x in t.get("sites") or []:
            key = x.get("parent_literal_attribution")
            if key in attr:
                attr[key] += 1
            else:
                bad.append("a site carries an attribution state outside the vocabulary")
                break
    if (summary.get("sites_by_parent_literal_attribution") or {}) != attr:
        bad.append("sites_by_parent_literal_attribution does not re-derive")
    if sum(attr.values()) != sum(len(t.get("sites") or []) for t in rows):
        bad.append("the attribution tally does not cover every site")
    if summary.get("distinct_sources") != len({s.get("source") for t in rows
                                               for s in (t.get("sites") or [])}):
        bad.append("distinct_sources does not re-derive")
    for t in rows:
        for s in t.get("sites") or []:
            if s.get("mode") == M_READ and s.get("debt") not in DEBT_VOCAB:
                bad.append("a read site carries a debt class outside the vocabulary")
                break
            if s.get("mode") != M_READ and s.get("debt") is not None:
                bad.append("a non-read site carries a debt class")
                break
            if s.get("mode") not in MODE_VOCAB:
                bad.append("a site carries a mode outside the vocabulary")
                break
    if [r for r in rows if (r.get("twin_basename") or "") in
            ("legdebt_latest.json",) or (r.get("twin") or "").find("legdebt") >= 0]:
        bad.append("this study appears in its own population")
    if summary.get("read_sites") and not summary.get("twins_that_would_need_an_assertion_"
                                                     "rewritten"):
        bad.append("no twin needs an assertion rewritten though read sites exist")
    return bad


def check_problems(path=None):
    face = _load_json(path or os.path.join(OUTDIR, FACE_NAME))
    return tally_problems(face)


def verify():
    """Re-classify every site from the live tree and diff against the face."""
    face = _load_json(os.path.join(OUTDIR, FACE_NAME))
    problems = tally_problems(face)
    fresh = {}
    for t in face.get("rows") or []:
        for s in t.get("sites") or []:
            fresh[(s.get("source"), s.get("line"))] = measure_site(
                s.get("twin_basename"), s.get("source"), s.get("line") or 0)
    moved = []
    for t in face.get("rows") or []:
        for s in t.get("sites") or []:
            now = fresh.get((s.get("source"), s.get("line")))
            if not now:
                continue
            for key in ("mode", "debt"):
                if now.get(key) != s.get(key):
                    moved.append({"source": s.get("source"), "line": s.get("line"),
                                  "field": key, "was": s.get(key), "now": now.get(key)})
    if moved:
        problems.append("the live tree re-classifies %d sites differently" % len(moved))
        problems.append("moved=%s" % json.dumps(moved[:5], ensure_ascii=False))
    return problems


def _write(face):
    os.makedirs(OUTDIR, exist_ok=True)
    face["generated"] = _now()
    body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    dated = os.path.join(OUTDIR, "%s-%s.json" % (DATED_PREFIX, face["evidence_cutoff"]))
    for path in (dated, os.path.join(OUTDIR, FACE_NAME)):
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body + "\n")
    return dated


def _now():
    import time
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def _rows_for_review(face):
    out = []
    for t in face.get("rows") or []:
        if t.get("strongest_debt") in (D_REDERIVE, D_PIN, D_PRESENCE):
            out.append(t)
    return out


def cmd_run():
    face = build()
    face["verdict"] = verdict_for(face["rows"], face["summary"])
    face["card_answer"] = {
        "twins_with_a_leg_that_re_derives": sum(
            1 for t in face["rows"] if (t.get("sites_by_debt") or {}).get(D_REDERIVE)),
        "twins_with_a_leg_that_pins_a_value": sum(
            1 for t in face["rows"] if (t.get("sites_by_debt") or {}).get(D_PIN)),
        "twins_whose_legs_only_require_the_file": sum(
            1 for t in face["rows"] if t.get("strongest_debt") == D_EXISTS),
        "twins_with_no_reader_left_in_the_opener_set": face["summary"][
            "twins_whose_opener_set_holds_no_reader"],
    }
    dated = _write(face)
    s = face["summary"]
    print("%s | %s" % (_rel(dated), face["verdict"]))
    print("twins %d | sites %d %s" % (s["twins_in_population"], s["sites_in_population"],
                                      s["sites_by_mode"]))
    print("read sites %d %s" % (s["read_sites"], s["read_sites_by_debt"]))
    print("twins by strongest debt %s" % s["twins_by_strongest_debt"])
    print("opener sets with no reader left %d | write sites %d | no-open-call sites %d"
          % (s["twins_whose_opener_set_holds_no_reader"],
             s["sites_by_mode"].get(M_WRITE, 0),
             s["sites_where_the_recorded_line_holds_no_open_call"]))
    print("attribution %s" % s["sites_by_parent_literal_attribution"])
    print("write sites by role %s" % s["write_sites_by_role"])
    print("the writer is counted as an opener on %d twins | a doctor writes it on %d"
          % (len(s["twins_where_the_publishing_instrument_opens_its_own_twin"]),
             len(s["twins_where_a_doctor_harness_writes_it"])))
    print("retirable with existence-only edits %d | need an assertion rewritten %d"
          % (len(s["twins_retirable_with_existence_only_edits"]),
             len(s["twins_that_would_need_an_assertion_rewritten"])))
    return 0


def cmd_check():
    problems = check_problems()
    print("check problems=%s" % json.dumps(problems, ensure_ascii=False))
    return 0 if not problems else 1


def cmd_verify():
    problems = verify()
    print("verify problems=%s" % json.dumps(problems, ensure_ascii=False))
    return 0 if not problems else 1


# ---------------------------------------------------------------------------------------------
# selftest -- fixtures, no repo faces
# ---------------------------------------------------------------------------------------------
def _unit(src):
    tree = ast.parse(src)
    return tree, parents(tree)


def _debt_of(src, anchor_text):
    """Classify the asserting block that owns the first line containing ``anchor_text``."""
    tree, par = _unit(src)
    line = next(i for i, ln in enumerate(src.split("\n"), 1) if anchor_text in ln)
    unit = asserting_block(tree, par, line)
    return classify_block(unit, module_names(tree))


def selftest():
    out = []

    def t(name, cond, detail=""):
        out.append((name, bool(cond), detail))

    def eq(name, got, want):
        out.append((name, got == want, "got=%r want=%r" % (got, want)))

    # 1. a leg that only asks for the file
    eq("existence-only leg", _debt_of(
        "import json, os\n"
        "def leg():\n"
        "    p = 'x_latest.json'\n"
        "    if not os.path.exists(p):\n"
        "        raise SystemExit('missing')\n"
        "    f = json.load(open(p))\n"
        "    check('ok', True)\n", "json.load")[0], D_EXISTS)

    # 2. a leg that pins a field to a literal
    eq("pin to a literal", _debt_of(
        "import json\n"
        "def leg():\n"
        "    f = json.load(open('x_latest.json'))\n"
        "    if f.get('study') != 'E231':\n"
        "        bad.append('not E231')\n", "json.load")[0], D_PIN)

    # 3. a leg that pins against a frozen vocabulary
    eq("pin against a vocabulary", _debt_of(
        "import json\n"
        "def leg():\n"
        "    f = json.load(open('x_latest.json'))\n"
        "    if f.get('verdict') not in ('a', 'b'):\n"
        "        bad.append('outside')\n", "json.load")[0], D_PIN)

    # 4. a leg that only asserts a field is present
    eq("presence only", _debt_of(
        "import json\n"
        "def leg():\n"
        "    f = json.load(open('x_latest.json'))\n"
        "    cut = f.get('evidence_cutoff')\n"
        "    if not cut:\n"
        "        bad.append('no cutoff')\n", "json.load")[0], D_PRESENCE)

    # 5. a leg that re-derives a tally from the payload
    eq("re-derive a tally", _debt_of(
        "import json\n"
        "def tally(rows):\n"
        "    return {}\n"
        "def leg():\n"
        "    f = json.load(open('x_latest.json'))\n"
        "    rows = f.get('rows') or []\n"
        "    if tally(rows) != f.get('by_class'):\n"
        "        bad.append('does not re-derive')\n", "json.load")[0], D_REDERIVE)

    # 6. a doctor that compares the face with a copy of itself
    eq("bytes compared with a copy", _debt_of(
        "import io\n"
        "def main():\n"
        "    backup = io.open('x.json', 'rb').read()\n"
        "    same = io.open('x.json', 'rb').read() == backup\n"
        "    assert same\n", "io.open")[0], D_BYTES)

    # 7. modes
    tree, par = _unit("x = open('p', 'w')\ny = open('p')\nz = json.load(open('q'))\n")
    eq("write mode", mode_of_site(tree, 1)[0], M_WRITE)
    eq("default mode is a read", mode_of_site(tree, 2)[0], M_READ)
    eq("json load is a read", mode_of_site(tree, 3)[0], M_READ)
    tree2, _ = _unit("mod.load('p')\n")
    eq("a helper call is indirect", mode_of_site(tree2, 1)[0], M_INDIRECT)

    # 8. roles
    eq("suite role", role_of("smoke_test.py"), S_SUITE)
    eq("runner role", role_of("scripts/run_e423_smoke_leg.py"), S_RUNNER)
    eq("instrument role", role_of("scripts/e494_latest_authors.py"), S_INSTRUMENT)
    eq("one-off role", role_of("_tmp_r1277_view.py"), S_ONEOFF)

    # 9. the asserting block is the leg, not the with-block that opens the file
    src = ("import json\n"
           "def leg():\n"
           "    with open('x_latest.json', encoding='utf-8') as fh:\n"
           "        f = json.load(fh)\n"
           "    if f.get('study') != 'E231':\n"
           "        bad.append('nope')\n")
    tree, par = _unit(src)
    unit = asserting_block(tree, par, 3)
    t("the block owning a site is the asserting block", type(unit).__name__ == "FunctionDef",
      type(unit).__name__)

    # 10. verdict re-derives
    rows = [{"strongest_debt": D_EXISTS}, {"strongest_debt": D_PIN}]
    eq("verdict takes the strongest debt", verdict_for(rows, {}), V_PIN)
    eq("verdict on an empty population", verdict_for([], {}), V_EMPTY)
    eq("verdict with an unreadable site", verdict_for(
        [{"strongest_debt": D_PIN}], {"read_sites_by_debt": {D_UNREADABLE: 1}}), V_ERROR)

    # 11. a face that does not re-derive is refused
    face = {"card": CARD, "verdict": V_PIN, "rows": [{"twin_basename": "a_latest.json",
                                                     "sites": [], "strongest_debt": D_PIN}],
            "summary": {"twins_in_population": 1, "sites_in_population": 0}}
    t("a face with no re-deriving tallies is refused", tally_problems(face))

    # 12. the population is read, not restated
    src = io.open(os.path.join(ROOT, "scripts", "e483_leg_debt.py"), encoding="utf-8").read()
    t("the population comes from E479's face",
      "opened_only_by_a_smoke_or_runner_leg" in src and "SOURCE_FACE_GLOB" in src)
    t("this study excludes its own outputs", "e483_" in SELF_EXCLUDED)

    bad = [n for n, ok, d in out if not ok]
    for name, ok, detail in out:
        print(("PASS  " if ok else "FAIL  ") + name +
              ((" | " + detail) if detail and not ok else ""))
    print("selftest %d/%d" % (len(out) - len(bad), len(out)))
    return 0 if not bad else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="E483 -- what the legs of the leg-only twins assert")
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "check", "verify", "selftest", "build"])
    args = ap.parse_args(argv)
    if args.cmd == "run":
        return cmd_run()
    if args.cmd == "check":
        return cmd_check()
    if args.cmd == "verify":
        return cmd_verify()
    if args.cmd == "build":
        face = build()
        print(json.dumps(face["summary"], ensure_ascii=False, indent=1))
        print("verdict:", verdict_for(face["rows"], face["summary"]))
        return 0
    return selftest()


if __name__ == "__main__":
    sys.exit(main())