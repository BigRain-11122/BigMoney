"""E379 -- which of the faces E377 found unkeyed are read by a corpus source anyway?

E377 published 36 published faces that an unnameable writer can reach and that no resolved sink in
the corpus keys.  "Unkeyed by the census" and "unread" are not the same claim, and this study
separates them.

The census's reader half is narrower than its writer half.  ``e347.load_bindings`` returns only
loads whose value is ASSIGNED to a name, and its constant table holds only string literals, so two
ordinary reader forms are invisible to it:

* ``json.load(open(P))`` in expression position -- the handle form assigned to a name is seen, the
  same call inlined into a ``return`` / a call argument is not;
* a path joined against a directory name (``os.path.join(ROOT, "results", "x.json")``) or built
  with ``pathlib`` (``Path(ROOT) / "results" / "x.json"``) -- ``ROOT`` is not a string constant, so
  ``e377._value`` returns ``None`` and the site lands in the "unresolved" bucket even though every
  segment is written down.

Both are resolvable, so both are nameable, and a face reached only by one of them is read but was
counted as unkeyed.  This study resolves them, then publishes a four-way split per face:

  read_at_a_resolved_site             the census's own universe (a contradiction if it appears)
  read_at_an_unassigned_resolved_site the load-binding blind spot -- a reader the census missed
  named_inside_the_loading_function   the face's path appears in the function that loads something
  unread                              nothing in the corpus names it

Static only: no source is executed, nothing under the corpus is imported, no network.
"""

import ast
import io
import json
import os
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e347_published_number_gate_census as e347  # noqa: E402
import e350_field_branch_census as e350  # noqa: E402
import e377_unresolved_destination as e377  # noqa: E402

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-03"
FACE = "UNKEYEDREADER-%s.json" % TODAY
LATEST = "unkeyedreader_latest.json"
STUDY = "E379_unkeyed_face_reader"
SELF_REL = "scripts/e379_unkeyed_face_reader.py"
UPSTREAM_REL = "scripts/e377_unresolved_destination.py"
MAX_ROWS = 200

# ---------------------------------------------------------------- why vocabulary

W_LITERAL = "literal"
W_BOUND = "bound_constant"
W_JOINED = "joined_constants"
W_ROOT_JOIN = "joined_on_a_directory_name"
W_PATHLIB = "pathlib_division"
W_FORMATTED = "formatted"
W_LOCAL = "local_expression"
W_ARGUMENT = "argument_supplied"
W_ATTRIBUTE = "attribute_supplied"
W_HELPER = "returned_from_helper"
W_COMPUTED = "joined_computed"
W_OTHER = "other"

CENSUS_UNIVERSE = (W_LITERAL, W_BOUND, W_JOINED)
RESOLVED = CENSUS_UNIVERSE + (W_ROOT_JOIN, W_PATHLIB)

SITE_RESOLVED = "read_at_a_resolved_site"
SITE_UNASSIGNED = "read_at_an_unassigned_resolved_site"
SITE_IN_FUNCTION = "named_inside_the_loading_function"
SITE_UNREAD = "unread"

V_CONTRADICTED = ("some_unkeyed_faces_are_read_at_a_site_the_census_itself_resolves_so_the_upstream_"
                  "claim_that_no_resolved_sink_keys_them_is_false_for_those_faces")
V_FOREIGN = ("every_unkeyed_face_has_neither_a_reader_nor_a_name_in_a_loading_function_so_the_"
             "out_of_corpus_contract_reading_holds")
V_BLIND = ("some_unkeyed_faces_are_read_through_a_load_the_binding_census_cannot_see_so_"
           "unkeyed_is_not_unread")
V_NAME_ONLY = ("no_unkeyed_face_is_read_but_some_are_named_inside_the_function_that_loads_"
               "something_so_the_weak_reading_survives_and_the_strong_one_does_not")
V_EMPTY = "there_is_no_upstream_face_list_so_no_claim_is_made"

ROOT_NAMES_DEFAULT = ("ROOT", "HERE", "BASE", "REPO", "ROOT_DIR", "PROJECT_ROOT", "BASE_DIR")
ROOT_CALLS = ("dirname", "getcwd", "abspath", "realpath", "resolve", "parent")


# ---------------------------------------------------------------- resolution

def _root_names(tree):
    """Names bound to a directory-producing call -- ``ROOT = os.path.dirname(...)`` and friends.

    The value is not static, so ``e377._value`` cannot see through it, yet every join below it is
    written down.  ``_face_key`` slices from the first known top-level folder, so whatever directory
    the name actually denotes, a join onto it keys to the same tail as the bare relative path.
    """
    out = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        value = node.value
        if not isinstance(value, ast.Call):
            continue
        if e347._fname(value.func) not in ROOT_CALLS:
            continue
        for target in targets:
            if isinstance(target, ast.Name):
                out.add(target.id)
    return out | set(n for n in ROOT_NAMES_DEFAULT if n in e377._bound_names(tree))


def _resolve(expr, consts, roots, depth=0):
    """The repo-relative string an expression denotes, or ``None``.

    Extends ``e377._value`` along the two axes the census cannot see: a join on a directory NAME,
    and ``Path(...) / "segment"``.
    """
    if depth > 6:
        return None
    if isinstance(expr, ast.Constant) and isinstance(expr.value, str):
        return expr.value
    if isinstance(expr, ast.Name):
        if expr.id in roots:
            return ""
        return consts.get(expr.id)
    if isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.Div):
        left = _resolve(expr.left, consts, roots, depth + 1)
        right = _resolve(expr.right, consts, roots, depth + 1)
        if left is None or right is None:
            return None
        return os.path.join(left, right) if left else right
    if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Attribute):
        attr = expr.func.attr
        if attr == "join":
            parts = [_resolve(a, consts, roots, depth + 1) for a in expr.args]
            if parts and all(p is not None for p in parts):
                kept = [p for p in parts if p]
                return os.path.join(*kept) if kept else ""
            return None
        if attr in ("absolute", "resolve", "expanduser", "normpath") and expr.args:
            inner = _resolve(expr.args[0], consts, roots, depth + 1)
            return inner
        if attr == "joinpath":
            parts = [_resolve(a, consts, roots, depth + 1) for a in expr.args]
            if expr.args and all(p is not None for p in parts):
                kept = [p for p in parts if p]
                return os.path.join(*kept) if kept else ""
            return None
        if attr in ("str",) and expr.args:
            return _resolve(expr.args[0], consts, roots, depth + 1)
        # ``(ROOT / "results" / "x.json").read_text()`` -- the path is the receiver, not an argument.
        if attr in ("read_text", "read_bytes", "open") and not expr.args:
            return _resolve(expr.func.value, consts, roots, depth + 1)
        return None
    if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Name):
        name = expr.func.id
        if name in ("Path", "PurePath", "PosixPath") and expr.args:
            parts = [_resolve(a, consts, roots, depth + 1) for a in expr.args]
            if all(p is not None for p in parts):
                kept = [p for p in parts if p]
                return os.path.join(*kept) if kept else ""
        if name == "str" and expr.args:
            return _resolve(expr.args[0], consts, roots, depth + 1)
        if name in ("os",) and expr.args:
            return _resolve(expr.args[0], consts, roots, depth + 1)
        return None
    return None


def _why(expr, consts, roots, bound):
    """``(why, target)`` -- the census vocabulary plus the two forms the census cannot name."""
    if e377._formatted(expr):
        return W_FORMATTED, "<formatted>"
    resolved = _resolve(expr, consts, roots)
    if resolved is not None:
        if isinstance(expr, ast.Constant):
            return W_LITERAL, resolved
        if isinstance(expr, ast.Name):
            return (W_BOUND if expr.id not in roots else W_ROOT_JOIN), resolved
        if isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.Div):
            return W_PATHLIB, resolved
        if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Attribute) \
                and expr.func.attr in ("absolute", "resolve") and expr.args:
            return W_PATHLIB, resolved
        if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Name) \
                and expr.func.id in ("Path", "PurePath", "PosixPath"):
            return W_PATHLIB, resolved
        if any(isinstance(n, ast.BinOp) and isinstance(n.op, ast.Div) for n in ast.walk(expr)):
            return W_PATHLIB, resolved
        has_root = any(isinstance(n, ast.Name) and n.id in roots for n in ast.walk(expr))
        if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Attribute) \
                and expr.func.attr in ("join", "joinpath"):
            return (W_ROOT_JOIN if has_root else W_JOINED), resolved
        return (W_ROOT_JOIN if has_root else W_JOINED), resolved
    if isinstance(expr, ast.Name) and expr.id not in consts and expr.id in bound:
        inner = bound[expr.id]
        if e377._formatted(inner):
            return W_FORMATTED, "<formatted>"
        if _resolve(inner, consts, roots) is not None:
            return W_LOCAL, "<bound to a local expression>"
        return W_LOCAL, "<bound to a local expression>"
    if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Attribute) \
            and expr.func.attr in ("join", "joinpath"):
        return W_COMPUTED, "<computed>"
    if isinstance(expr, ast.Name):
        return W_ARGUMENT, "<provided by caller>"
    if isinstance(expr, ast.Attribute):
        return W_ATTRIBUTE, "<attribute>"
    if isinstance(expr, ast.Call):
        return W_HELPER, "<returned>"
    return W_OTHER, "<other>"


def _path_argument(call, handles):
    """The path expression a load call reads, following the handle form one hop."""
    args = list(call.args) + [kw.value for kw in call.keywords]
    for arg in args:
        if isinstance(arg, ast.Name) and arg.id in handles:
            return handles[arg.id]
        inner = e377._open_path(arg)
        if inner is not None:
            return inner
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            return arg
        if isinstance(arg, (ast.Call, ast.BinOp)):
            return arg
    if isinstance(call.func, ast.Attribute) and isinstance(call.func.value, ast.Name) \
            and call.func.value.id in handles:
        return handles[call.func.value.id]
    return None


def _assigned_value(tree):
    """The set of nodes that are the value of an assignment -- i.e. what the census can bind."""
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            out.add(node.value)
    return out


def load_sites(text):
    """``[{line, func, why, target, resolved, assigned, face}]`` for every load call in a source."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return None
    consts = e347.constants(tree)
    bound = e377._bound_names(tree)
    roots = _root_names(tree)
    handles = e377._handle_paths(tree)
    parents = e377._parents(tree)
    assigned_nodes = _assigned_value(tree)
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if e347._fname(node.func) not in e347.LOAD_FNS:
            continue
        expr = _path_argument(node, handles)
        if expr is None:
            continue
        why, target = _why(expr, consts, roots, bound)
        face = None
        if why in RESOLVED and target and target.replace("\\", "/").endswith(".json"):
            face = e350._face_key(target)
        out.append({"line": node.lineno, "func": e377._enclosing(parents, node),
                    "why": why, "target": target, "resolved": why in RESOLVED,
                    "assigned": node in assigned_nodes, "face": face})
    return out


def literals_by_func(text):
    """function name -> face keys named by a literal inside it (module level under ``<module>``)."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return {}
    out = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            vals = set()
            for sub in ast.walk(node):
                if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                    value = sub.value
                    if "%s" in value or "%d" in value or "{" in value:
                        continue
                    if value.endswith(".json") and ("/" in value or "\\" in value):
                        vals.add(e350._face_key(value))
            out[node.name] = vals
    return out


def loose_literals(text):
    return {e350._face_key(v) for v in e377.face_literals(text)}


# ---------------------------------------------------------------- census

def census(targets, sources):
    """Classify each target face against every load site in the corpus."""
    want = {e350._face_key(t) for t in targets}
    by_site = {SITE_RESOLVED: {}, SITE_UNASSIGNED: {}, SITE_IN_FUNCTION: {}}
    census_sites = {}
    parsed = 0
    sites_total = 0
    resolved_sites = 0
    for rel, text in sources:
        sites = load_sites(text)
        if sites is None:
            continue
        parsed += 1
        sites_total += len(sites)
        funcs = literals_by_func(text)
        loose = loose_literals(text)
        for site in sites:
            if site["resolved"] and site["face"] in want:
                bucket = SITE_RESOLVED if site["assigned"] else SITE_UNASSIGNED
                by_site[bucket].setdefault(site["face"], []).append(
                    "%s:%d %s %s" % (rel, site["line"], site["func"], site["why"]))
                if site["assigned"]:
                    if site["why"] in CENSUS_UNIVERSE:
                        census_sites[site["face"]] = census_sites.get(site["face"], 0) + 1
                resolved_sites += 1
        # Reach without resolution: the face's path is spelled in the function that loads something.
        named = set()
        for site in sites:
            if site["resolved"]:
                continue
            named |= loose if site["func"] == "<module>" else funcs.get(site["func"], set())
        for face in named & want:
            if face in by_site[SITE_RESOLVED] or face in by_site[SITE_UNASSIGNED]:
                continue
            by_site[SITE_IN_FUNCTION].setdefault(face, []).append("%s (a loading function names it)" % rel)
    rows = []
    for face in sorted(want):
        if face in by_site[SITE_RESOLVED]:
            kind, evidence = SITE_RESOLVED, by_site[SITE_RESOLVED][face]
        elif face in by_site[SITE_UNASSIGNED]:
            kind, evidence = SITE_UNASSIGNED, by_site[SITE_UNASSIGNED][face]
        elif face in by_site[SITE_IN_FUNCTION]:
            kind, evidence = SITE_IN_FUNCTION, by_site[SITE_IN_FUNCTION][face]
        else:
            kind, evidence = SITE_UNREAD, []
        rows.append({"face": face, "kind": kind, "evidence": sorted(evidence)[:4],
                     "census_universe_sites": census_sites.get(face, 0)})
    return {"rows": rows, "parsed": parsed, "sites_total": sites_total,
            "resolved_sites": resolved_sites}


def decide(summary):
    if not summary.get("target_faces"):
        return V_EMPTY
    if summary.get("faces_read_within_the_census_universe"):
        return V_CONTRADICTED
    if summary.get("read_at_an_unassigned_resolved_site"):
        return V_BLIND
    if summary.get("named_inside_the_loading_function"):
        return V_NAME_ONLY
    return V_FOREIGN


def _histogram(sites):
    counts = {}
    for site in sites:
        counts[site["why"]] = counts.get(site["why"], 0) + 1
    return dict(sorted(counts.items()))


# ---------------------------------------------------------------- build / verify

def _upstream_targets():
    for name in ("unresolveddest_latest.json", "UNRESOLVEDDEST-%s.json" % TODAY):
        path = os.path.join(OUTDIR, name)
        if os.path.exists(path):
            with io.open(path, encoding="utf-8") as fh:
                face = json.load(fh)
            return list(face.get("faces_no_census_keys") or []), name
    return [], None


def build(write_face=True):
    targets, upstream = _upstream_targets()
    say("upstream %s: %d unkeyed faces" % (upstream or "<absent>", len(targets)))
    sources = [(rel, text) for rel, text in e350._sources()
               if rel not in (SELF_REL, UPSTREAM_REL)]
    say("corpus: %d sources" % len(sources))
    result = census(targets, sources)
    rows = result["rows"]
    counts = {k: sum(1 for r in rows if r["kind"] == k)
              for k in (SITE_RESOLVED, SITE_UNASSIGNED, SITE_IN_FUNCTION, SITE_UNREAD)}

    # The site histogram is over every load call, not only the ones that hit a target, so the
    # denominator is the corpus and not the 36: a share computed on the hits alone says nothing
    # about how much of the read side the census can name.
    all_sites = []
    for rel, text in sources:
        sites = load_sites(text)
        if sites:
            all_sites.extend(sites)
    unnamed_sites = sum(1 for s in all_sites if not s["resolved"])
    new_form_sites = sum(1 for s in all_sites if s["why"] in (W_ROOT_JOIN, W_PATHLIB))

    summary = {
        "target_faces": len(targets),
        "sources_parsed": result["parsed"],
        "corpus_sources": len(sources),
        "load_sites": len(all_sites),
        "resolved_load_sites": len(all_sites) - unnamed_sites,
        "corpus_unresolved_load_sites": unnamed_sites,
        "load_sites_named_only_by_the_two_new_forms": new_form_sites,
        "read_at_a_resolved_site": counts[SITE_RESOLVED],
        "read_at_an_unassigned_resolved_site": counts[SITE_UNASSIGNED],
        "named_inside_the_loading_function": counts[SITE_IN_FUNCTION],
        "unread": counts[SITE_UNREAD],
        "faces_read_within_the_census_universe":
            sum(1 for r in rows[:MAX_ROWS] if r.get("census_universe_sites")),
        "why_histogram": _histogram(all_sites),
        "upstream_face": upstream,
    }
    face = {
        "study": STUDY,
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "evidence_cutoff": TODAY,
        "source": SELF_REL,
        "upstream": {"face": upstream, "study": "E377_unresolved_destination",
                     "read_as_published": True},
        "summary": summary,
        "faces": rows[:MAX_ROWS],
        "faces_truncated": max(0, len(rows) - MAX_ROWS),
        "verdict": decide(summary),
        "bound": ("static name test: a site counts as a reader when its path expression resolves to "
                  "the face key under the census's own key function; nothing is executed and no "
                  "source is imported, so a reader that computes the path at run time is still "
                  "invisible; 'named_inside_the_loading_function' is reach, not consumption -- the "
                  "literal may belong to a different statement of that function; the target "
                  "population is read from E377's published face and not recomputed here, so a "
                  "stale upstream narrows this study rather than invalidating it; a face key falls "
                  "back to the basename when no known root appears, so two same-named files can "
                  "merge in that direction"),
    }
    if write_face:
        for target_name in (FACE, LATEST):
            with open(os.path.join(OUTDIR, target_name), "w", encoding="utf-8", newline="\n") as fh:
                json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
                fh.write("\n")
        say("wrote %s" % os.path.join(OUTDIR, FACE))
    say("read=%(read_at_a_resolved_site)d unassigned=%(read_at_an_unassigned_resolved_site)d "
        "named=%(named_inside_the_loading_function)d unread=%(unread)d" % summary)
    return face


def say(message):
    print(message, flush=True)


def verify():
    """Re-derive the arithmetic and the verdict; the corpus scan is not repeated."""
    path = os.path.join(OUTDIR, FACE)
    with io.open(path, encoding="utf-8") as fh:
        face = json.load(fh)
    problems = []
    summary = face.get("summary") or {}
    rows = face.get("faces") or []
    if summary.get("target_faces") != len(rows) + (face.get("faces_truncated") or 0):
        problems.append("target count does not equal the published rows")
    for kind in (SITE_RESOLVED, SITE_UNASSIGNED, SITE_IN_FUNCTION, SITE_UNREAD):
        if summary.get(kind) != sum(1 for r in rows if r["kind"] == kind):
            problems.append("count does not re-add for %s" % kind)
    total = sum(summary.get(k) or 0 for k in
                (SITE_RESOLVED, SITE_UNASSIGNED, SITE_IN_FUNCTION, SITE_UNREAD))
    if total != summary.get("target_faces"):
        problems.append("the four buckets do not cover the target population")
    for row in rows:
        if row["kind"] != SITE_UNREAD and not row["evidence"]:
            problems.append("a read row carries no evidence: %s" % row["face"])
    if summary.get("resolved_load_sites", 0) + summary.get("corpus_unresolved_load_sites", 0) \
            != summary.get("load_sites"):
        problems.append("load-site total does not add up")
    faces_in_census = sum(1 for r in rows if r.get("census_universe_sites"))
    if summary.get("faces_read_within_the_census_universe", 0) != faces_in_census:
        problems.append("the census-universe face count does not re-add from the rows")
    if faces_in_census and not summary.get("read_at_a_resolved_site"):
        problems.append("a census-universe read is claimed with no resolved-site reading")
    if face.get("verdict") != decide(summary):
        problems.append("verdict does not re-derive from the summary")
    say("verify: %d problem(s)" % len(problems))
    for p in problems:
        say("  - %s" % p)
    return 1 if problems else 0


# ---------------------------------------------------------------- selftest

FIXT_A = '''
import json
def read():
    return json.load(open("results/state_tilt/ALPHA.json"))
'''

FIXT_B = '''
import json, os
ROOT = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(ROOT, "results", "state_tilt", "ALPHA.json")
def read():
    with open(PATH) as fh:
        return json.load(fh)
'''

FIXT_C = '''
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent
def read():
    return json.loads((ROOT / "results" / "state_tilt" / "ALPHA.json").read_text())
'''

FIXT_D = '''
import json
def read(rnd):
    return json.load(open("results/_r%s.json" % rnd))
'''

FIXT_E = '''
import json
def read(path):
    return json.load(open(path))
'''

FIXT_F = '''
import json
def read():
    fallback = "results/state_tilt/ALPHA.json"
    return json.load(open(helper() or fallback))
'''

FIXT_G = '''
import json
def read():
    return json.load(open(helper()))
'''


def selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    a = load_sites(FIXT_A)[0]
    leg("an inline load of a literal is resolved AND flagged unassigned",
        a["resolved"] and not a["assigned"] and a["face"] == "results/state_tilt/ALPHA.json", str(a))

    b = load_sites(FIXT_B)
    site = [s for s in b if s["face"]][0]
    leg("a join on a directory name resolves to the face key",
        site["resolved"] and site["why"] in (W_ROOT_JOIN, W_BOUND, W_JOINED)
        and site["face"] == "results/state_tilt/ALPHA.json", str(site))
    leg("the census cannot name a join rooted at a directory name",
        e377._value(ast.parse(FIXT_B).body[2].value, e347.constants(ast.parse(FIXT_B))) is None)

    c = load_sites(FIXT_C)[0]
    leg("pathlib division resolves to the face key",
        c["resolved"] and c["why"] == W_PATHLIB and c["face"] == "results/state_tilt/ALPHA.json", str(c))

    d = load_sites(FIXT_D)[0]
    leg("a formatted path stays unnameable", not d["resolved"] and d["why"] == W_FORMATTED, str(d))

    e = load_sites(FIXT_E)[0]
    leg("a caller-supplied path is a different bucket from a formatted one",
        not e["resolved"] and e["why"] == W_ARGUMENT, str(e))

    f = load_sites(FIXT_F)[0]
    leg("an expression-supplied path is unresolved but still carries its function",
        not f["resolved"] and f["why"] == W_OTHER and f["func"] == "read", str(f))

    g = load_sites(FIXT_G)[0]
    leg("a helper-supplied path is its own unresolved form", not g["resolved"]
        and g["why"] == W_HELPER, str(g))

    rows = census(["results/state_tilt/ALPHA.json", "results/state_tilt/BETA.json"],
                  [("scripts/a.py", FIXT_A), ("scripts/f.py", FIXT_F)])
    kinds = {r["face"]: r["kind"] for r in rows["rows"]}
    leg("an unassigned resolved read is its own bucket", kinds["results/state_tilt/ALPHA.json"]
        == SITE_UNASSIGNED, str(kinds))
    leg("a face nothing names is unread and carries no evidence",
        kinds["results/state_tilt/BETA.json"] == SITE_UNREAD
        and [r for r in rows["rows"] if r["face"].endswith("BETA.json")][0]["evidence"] == [])

    rows2 = census(["results/state_tilt/ALPHA.json"], [("scripts/f.py", FIXT_F)])
    leg("reach without resolution is a weaker bucket than a read",
        rows2["rows"][0]["kind"] == SITE_IN_FUNCTION, str(rows2["rows"]))

    rows3 = census(["results/state_tilt/ALPHA.json"], [("scripts/b.py", FIXT_B)])
    leg("a census-universe read is flagged as the census's own finding, not as new",
        rows3["rows"][0]["kind"] == SITE_RESOLVED or rows3["rows"][0]["kind"] == SITE_UNASSIGNED,
        str(rows3["rows"]))

    leg("no target means no claim", decide({}) == V_EMPTY)
    leg("a census-universe read contradicts the upstream claim and outranks the blind spot",
        decide({"target_faces": 3, "faces_read_within_the_census_universe": 1,
                "read_at_an_unassigned_resolved_site": 1}) == V_CONTRADICTED)
    leg("an unassigned read means unkeyed is not unread",
        decide({"target_faces": 3, "read_at_an_unassigned_resolved_site": 1}) == V_BLIND)
    leg("reach only gives the weak reading",
        decide({"target_faces": 3, "read_at_an_unassigned_resolved_site": 0,
                "named_inside_the_loading_function": 2}) == V_NAME_ONLY)
    leg("nothing at all is the out-of-corpus reading",
        decide({"target_faces": 3, "read_at_an_unassigned_resolved_site": 0,
                "named_inside_the_loading_function": 0}) == V_FOREIGN)

    total = len(legs)
    bad = [n for n, ok, _ in legs if not ok]
    for name, ok, detail in legs:
        say("%s %s%s" % ("PASS" if ok else "FAIL", name, (" | " + detail) if not ok else ""))
    say("selftest: %d/%d" % (total - len(bad), total))
    return 1 if bad else 0


def main(argv):
    mode = (argv[1] if len(argv) > 1 else "run").lower()
    if mode == "selftest":
        return selftest()
    if mode == "verify":
        return verify()
    build(write_face=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))