"""E615 -- does a live sweep open what it globs, or only enumerate the name?

E613 (r1636) priced reachability: 76 ancestor-only faces rest on five round scripts nothing names,
and the one landing module a live chain does run (``scripts/e396_face_basename_suffix.py``) reaches
54 of them only through a pattern naming nothing (``*/**/*``).  Reachability was the question
there.  Whether the sweep that reaches a face does anything with the hit was not asked.

So this study takes the same landing modules, resolves each glob call to the loop (or the binding
followed by the loop) that consumes the yielded path, and classifies one hop into the body:

  opens_it                     an opener (``open``/``io.open``/``Path.open``) is applied to the yield
  opens_it_through_a_helper    the yield is the argument of a module function that opens its parameter
  hands_it_to_a_subprocess     the yield reaches a call whose literals name a reader (``hash-object``)
  reads_only_the_name          every use is a name-shaped question (basename/relpath/endswith/
                               getsize/print/... or an attribute such as ``.stem``)
  never_references_the_yield   the loop body does not mention the loop variable at all
  pattern_is_not_a_literal     the pattern is computed (``f + '/**/*'``), so the landing names nothing
  no_loop_this_scan_can_follow the yield is bound but no loop over that binding is found

The faces are then priced on top of that: opened by a sweeper, opened only by a sweeper no entry
point runs again, or opened by no landing sweep at all.  A face opened by ``_r239`` (a one-off that
does open) and one opened only by ``e396`` (a live sweep that never opens) are different facts.

Run:      python scripts/e615_glob_sweep_use.py run
Verify:   python scripts/e615_glob_sweep_use.py verify
Check:    python scripts/e615_glob_sweep_use.py check
Selftest: python scripts/e615_glob_sweep_use.py selftest
"""

import argparse
import ast
import io
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import e609_glob_reach as e609                                         # noqa: E402  (segments)
import e611_sweep_reruns as e611                                       # noqa: E402  (classifier)
import e613_ancestor_reruns as e613                                    # noqa: E402  (population)
import e470_target_read as e470                                        # noqa: E402  (is_glob/opener)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
SELF_STEM = "GLOBSWEEPUSE"
OUT_PATH = os.path.join(OUTDIR, SELF_STEM + ".json")
SELF_SKIP = ("e615_", "run_e615") + tuple(e613.SELF_SKIP)

C_OPENS = "opens_it"
C_HELPER = "opens_it_through_a_helper"
C_SUBPROC = "hands_it_to_a_subprocess"
C_NAME = "reads_only_the_name"
C_DISCARDS = "never_references_the_yield"
C_NO_LOOP = "no_loop_this_scan_can_follow"
CLASSES = (C_OPENS, C_HELPER, C_SUBPROC, C_NAME, C_DISCARDS, C_NO_LOOP)
OPENS = (C_OPENS, C_HELPER, C_SUBPROC)

V_SOME = "at_least_one_face_is_opened_by_a_landing_sweep"
V_NONE = "no_landing_sweep_opens_any_face_it_yields"
V_EMPTY = "the_population_is_empty"
VERDICT_VOCAB = (V_SOME, V_NONE, V_EMPTY)

NAME_FUNCS = frozenset((
    "basename", "relpath", "splitext", "dirname", "abspath", "normpath", "realpath",
    "endswith", "startswith", "getsize", "isfile", "isdir", "exists", "islink",
    "print", "str", "repr", "replace", "split", "rsplit", "join", "lower", "upper",
    "format", "len", "sorted", "list", "set", "tuple", "enumerate", "getmtime",
))
NAME_ATTRS = frozenset(("name", "stem", "suffix", "suffixes", "parent", "parts", "as_posix"))
READER_LITERALS = ("hash-object", "--cacheinfo", "shutil.copy", "copyfile")


# --------------------------------------------------------------------------- population
def _read_json(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def population(root=None):
    """E613's population: the ancestor-only faces, with the sites that name an ancestor."""
    root = root or ROOT
    pop, why = e613.population(root)
    return pop, why


def landing_modules(root=None):
    """Every module E613 published as a landing: ancestor sweepers plus the no-name sweeps."""
    root = root or ROOT
    pop, _why = population(root)
    mods = set()
    for rec in pop:
        for s in rec["sites"]:
            src = s.get("source")
            if src and src.endswith(".py"):
                mods.add(src)
    corpus_texts = []
    for e in e613.entry_corpora(root):
        text = e611._text(root, e["source"])
        if text:
            corpus_texts.append((e["source"], e["kind"], text))
    no_name, _sites, _links = e613.no_name_sweeps(root, corpus_texts)
    for r in no_name:
        mods.add(r["module"])
    return sorted(m for m in mods
                  if not any(os.path.basename(m).startswith(s) for s in SELF_SKIP)), no_name


# --------------------------------------------------------------------------- scan
def _parents(tree):
    par = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            par[child] = node
    return par


def _pattern_node(call):
    if not call.args:
        return None
    first = call.args[0]
    for kw in call.keywords or []:
        if kw.arg in ("pathname", "pattern"):
            return kw.value
    return first


def _static_text(node, assigned):
    """The pattern text when the argument is built only from string literals, else None.

    A pattern is usually composed (``os.path.join("results", "**", "*.json")``), so reading only a
    bare Constant would grade the most common spelling as computed (E470's one-hop lesson).
    """
    if node is None:
        return None
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        parts = []
        for v in node.values:
            if isinstance(v, ast.Constant):
                parts.append(str(v.value))
            else:
                return None
        return "".join(parts)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = _static_text(node.left, assigned)
        right = _static_text(node.right, assigned)
        return None if left is None or right is None else left + right
    if isinstance(node, ast.Call):
        fn = node.func
        fname = fn.id if isinstance(fn, ast.Name) else getattr(fn, "attr", "")
        if fname == "join":
            parts = [_static_text(a, assigned) for a in node.args]
            if parts and all(p is not None for p in parts):
                return "/".join(parts)
            return None
    if isinstance(node, ast.Name) and node.id in assigned:
        lits = assigned[node.id]
        if len(lits) == 1:
            return lits[0]
    return None


def _repo_relative(pattern):
    """Reduce a pattern rooted in this repo (absolute or Windows) to its repo-relative spelling."""
    pat = pattern.replace("\\", "/")
    idx = pat.lower().find("/bigmoney/")
    if idx >= 0:
        return pat[idx + len("/bigmoney/"):]
    return pat


def _helpers_that_open(tree):
    """Module-level functions whose body applies an opener to the first parameter."""
    out = {}
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        names = [a.arg for a in node.args.args]
        if not names:
            continue
        first = names[0]
        for inner in ast.walk(node):
            if isinstance(inner, ast.Call) and e470._is_opener(inner):
                if any(isinstance(a, ast.Name) and a.id == first
                       for a in list(inner.args) + _kw_values(inner)):
                    out[node.name] = first
                    break
    return out


def _kw_values(call):
    out = []
    for kw in call.keywords or []:
        out.append(kw.value)
    return out


def _mentions(node, name):
    return any(isinstance(n, ast.Name) and n.id == name and isinstance(n.ctx, ast.Load)
               for n in ast.walk(node))


def _names_a_reader(call):
    for n in ast.walk(call):
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            if any(lit in n.value for lit in READER_LITERALS):
                return True
    return False


def _consumer_of(call, par):
    """(loop variable, the statements that consume it) for this glob call.

    The statements -- not the loop node -- because the loop's iter expression still mentions the
    binding, and counting that mention as a use of the yielded path graded every sweep as
    unclassifiable (fixture leg 5).
    """
    node = call
    while node in par:
        up = par[node]
        if isinstance(up, (ast.For, ast.AsyncFor)):
            if isinstance(up.target, ast.Name):
                return up.target.id, list(up.body) + list(up.orelse)
            return None, None
        if isinstance(up, (ast.ListComp, ast.SetComp, ast.GeneratorExp)):
            for gen in up.generators:
                if isinstance(gen.target, ast.Name):
                    return gen.target.id, [up.elt] + list(gen.ifs)
            return None, None
        if isinstance(up, (ast.Assign, ast.AnnAssign)):
            targets = getattr(up, "targets", None) or [up.target]
            for t in targets:
                if isinstance(t, ast.Name):
                    loop = _loop_over(par, up, t.id)
                    if loop is None:
                        return None, None
                    return loop.target.id, list(loop.body) + list(loop.orelse)
            return None, None
        node = up
    return None, None


def _loop_over(par, start, name):
    """A For over ``name``, searched from the scope that bound it (the loop may follow it)."""
    scope = start
    while scope in par:
        up = par[scope]
        if isinstance(up, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef)):
            scope = up
            break
        scope = up
    for node in ast.walk(scope):
        if isinstance(node, (ast.For, ast.AsyncFor)) and _mentions(node.iter, name):
            if isinstance(node.target, ast.Name):
                return node
    return None


def _classify_body(nodes, var, helpers, par):
    """One hop from the yielded path into the loop body."""
    if not nodes or var is None:
        return C_NO_LOOP
    uses = []
    for stmt in nodes:
        uses.extend(n for n in ast.walk(stmt)
                    if isinstance(n, ast.Name) and n.id == var
                    and isinstance(n.ctx, ast.Load))
    if not uses:
        return C_DISCARDS
    calls = []
    for stmt in nodes:
        calls.extend(n for n in ast.walk(stmt) if isinstance(n, ast.Call))
    for call in calls:
        if e470._is_opener(call):
            if any(_mentions(a, var) for a in list(call.args) + _kw_values(call)):
                return C_OPENS
    for call in calls:
        if _names_a_reader(call):
            if any(_mentions(a, var) for a in list(call.args) + _kw_values(call)):
                return C_SUBPROC
    for call in calls:
        fn = call.func
        fname = fn.id if isinstance(fn, ast.Name) else getattr(fn, "attr", "")
        if fname in helpers:
            if any(isinstance(a, ast.Name) and a.id == var
                   for a in list(call.args) + _kw_values(call)):
                return C_HELPER
    return C_NAME if all(_is_name_shaped(u, par) for u in uses) else C_NO_LOOP


def _is_name_shaped(use, par):
    """Does this use only ask a question about the path's name?"""
    node = use
    while node in par:
        up = par[node]
        if isinstance(up, ast.Call):
            fn = up.func
            fname = fn.id if isinstance(fn, ast.Name) else getattr(fn, "attr", "")
            return fname in NAME_FUNCS
        if isinstance(up, ast.Attribute):
            return up.attr in NAME_ATTRS or up.attr in NAME_FUNCS
        if isinstance(up, (ast.For, ast.AsyncFor, ast.FunctionDef, ast.Module)):
            return False
        node = up
    return False


def scan_module(rel, root=None):
    """Every glob call in one module, with the treatment of what it yields."""
    root = root or ROOT
    text = e611._text(root, rel)
    row = {"module": rel, "on_checkout": text is not None, "glob_calls": []}
    if text is None:
        return row
    try:
        tree = ast.parse(text)
    except SyntaxError:
        row["glob_calls_error"] = "syntax_error"
        return row
    par = _parents(tree)
    helpers = _helpers_that_open(tree)
    assigned = e470._assignments(tree)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not e470._is_glob(node):
            continue
        pat_node = _pattern_node(node)
        static = _static_text(pat_node, assigned)
        literal = _repo_relative(static) if static is not None else None
        var, nodes = _consumer_of(node, par)
        treatment = _classify_body(nodes, var, helpers, par)
        row["glob_calls"].append({
            "line": getattr(node, "lineno", 0),
            "pattern": literal if literal is not None else _describe(pat_node),
            "pattern_is_a_literal": literal is not None,
            "bound_to": var,
            "has_a_loop": bool(nodes),
            "treatment": treatment,
        })
    row["glob_calls"].sort(key=lambda r: (r["line"], str(r["pattern"])))
    return row


def _describe(node):
    if node is None:
        return "<no argument>"
    try:
        return ast.unparse(node)
    except (AttributeError, ValueError):
        return "<unprintable>"


# --------------------------------------------------------------------------- build
def build(root=None, write=False):
    root = root or ROOT
    pop, why = population(root)
    mods, no_name = landing_modules(root)
    module_rows = [scan_module(m, root) for m in mods]
    by_module = {r["module"]: r for r in module_rows}

    corpus_texts = []
    for e in e613.entry_corpora(root):
        text = e611._text(root, e["source"])
        if text:
            corpus_texts.append((e["source"], e["kind"], text))
    entry_class = {}
    for m in mods:
        entry_class[m] = e611._classify(m, corpus_texts, root)

    def treatments_for(source, pattern):
        """Treatments of the glob call whose static pattern is this site's pattern.

        A call whose pattern is computed is priced in its own row but pairs with no face: the
        landing was measured by E609, and only the body is this study's measurement.
        """
        row = by_module.get(source)
        if row is None:
            return []
        want = str(pattern or "").replace("\\", "/")
        return [g["treatment"] for g in row["glob_calls"]
                if g["pattern_is_a_literal"]
                and str(g["pattern"]).replace("\\", "/") == want]

    faces = []
    for rec in pop:
        rows = []
        for s in rec["sites"]:
            src = s.get("source") or ""
            if not src.endswith(".py"):
                continue
            treats = treatments_for(src, s.get("pattern"))
            cls = entry_class.get(src, {}).get("class", e611.C_NONE)
            rows.append({"source": src, "pattern": s.get("pattern"),
                         "entry_class": cls, "treatments": treats})
        opened = sorted({t for r in rows for t in r["treatments"] if t in OPENS})
        live_open = any(r["entry_class"] != e611.C_NONE and r["treatments"]
                        and any(t in OPENS for t in r["treatments"]) for r in rows)
        one_off_open = any(r["entry_class"] == e611.C_NONE and r["treatments"]
                           and any(t in OPENS for t in r["treatments"]) for r in rows)
        faces.append({
            "face": rec["face"],
            "present": rec["present"],
            "sweepers": sorted({r["source"] for r in rows}),
            "sweeper_rows": rows,
            "treatments": opened,
            "opened_by_a_landing_sweep": bool(opened),
            "opened_by_a_sweep_an_entry_point_runs_again": live_open,
            "opened_only_by_a_one_off": one_off_open and not live_open,
            "never_opened_by_a_landing_sweep": not opened,
        })

    counts = {c: 0 for c in CLASSES}
    calls = 0
    for r in module_rows:
        for g in r["glob_calls"]:
            calls += 1
            counts[g["treatment"]] += 1
    counts["modules"] = len(module_rows)
    counts["modules_on_checkout"] = sum(1 for r in module_rows if r["on_checkout"])
    counts["glob_calls"] = calls
    counts["glob_calls_with_a_literal_pattern"] = sum(
        1 for r in module_rows for g in r["glob_calls"] if g["pattern_is_a_literal"])
    counts["faces"] = len(faces)
    counts["faces_opened_by_a_landing_sweep"] = sum(
        1 for f in faces if f["opened_by_a_landing_sweep"])
    counts["faces_opened_by_a_sweep_an_entry_point_runs_again"] = sum(
        1 for f in faces if f["opened_by_a_sweep_an_entry_point_runs_again"])
    counts["faces_opened_only_by_a_one_off"] = sum(
        1 for f in faces if f["opened_only_by_a_one_off"])
    counts["faces_never_opened_by_a_landing_sweep"] = sum(
        1 for f in faces if f["never_opened_by_a_landing_sweep"])
    counts["glob_calls_with_a_computed_pattern"] = sum(
        1 for r in module_rows for g in r["glob_calls"] if not g["pattern_is_a_literal"])
    counts["faces_no_sweep_pattern_this_scan_can_pair_with"] = sum(
        1 for f in faces if f["sweeper_rows"]
        and all(not r["treatments"] for r in f["sweeper_rows"]))
    counts["modules_that_open_what_they_glob"] = sum(
        1 for r in module_rows
        if any(g["treatment"] in OPENS for g in r["glob_calls"]))
    counts["modules_that_only_read_the_name"] = sum(
        1 for r in module_rows
        if r["glob_calls"] and all(g["treatment"] in (C_NAME, C_DISCARDS)
                                   for g in r["glob_calls"]))
    counts["live_modules"] = sum(1 for m in mods if entry_class[m]["class"] != e611.C_NONE)

    face = {
        "study": "E615_glob_sweep_use",
        "card": "E615-WHETHER-A-LIVE-SWEPT-MODULE-EVER-OPENS-WHAT-IT-GLOBS",
        "evidence_cutoff": e613._cutoff(pop),
        "population_source": ("results/state_tilt/GLOBSWEEPREACH.json (E609 ancestor-only faces) "
                              "+ results/state_tilt/ANCESTORRERUNS.json (E613 landing modules)"),
        "population_note": why or "read from the published E609/E613 faces",
        "class_vocabulary": list(CLASSES),
        "counts": counts,
        "modules": [
            dict(r, **{"entry_class": entry_class[r["module"]]["class"],
                       "entry_named_by": entry_class[r["module"]]["named_by"]})
            for r in module_rows
        ],
        "no_name_sweeps": no_name,
        "faces": faces,
        "verdict": verdict_from(counts),
        "answer": answer_sentence(counts, module_rows, faces),
        "limits": [
            "one hop only: the treatment is the loop body's treatment of the loop variable, so a "
            "yield that is renamed (``rel = os.path.relpath(p)`` then ``open(rel)``) is graded on "
            "the first hop and reads as a name use, not as an open",
            "a computed pattern (``f + '/**/*'``) is published as not-a-literal: the landing it "
            "performs was measured by E609, but the pattern text here cannot be matched back to a "
            "face path, so it contributes no treatment to any face",
            "the population is machine-read from E609's and E613's published faces; a stale "
            "upstream face would be graded as published, and population_note says where it came from",
            "literal openers elsewhere in the corpus are E606's measurement and are not re-derived "
            "here -- this face prices only what the landing sweeps do with what they glob",
            "a module is 'live' when E611's classifier finds an entry point naming its basename; a "
            "reference composed from a string is a miss",
        ],
    }
    pr = face_problems(face)
    if write and not pr:
        write_face(face)
    return face, pr


def verdict_from(counts):
    if not counts.get("faces"):
        return V_EMPTY
    return V_SOME if counts.get("faces_opened_by_a_landing_sweep") else V_NONE


def answer_sentence(counts, module_rows, faces):
    total = counts.get("faces") or 0
    if not total:
        return "the population is empty, so no landing sweep is priced"
    live = [r for r in module_rows
            if any(g["treatment"] in OPENS for g in r["glob_calls"])
            and r.get("module")]
    names = [r["module"] for r in module_rows
             if r["glob_calls"] and all(g["treatment"] in (C_NAME, C_DISCARDS)
                                        for g in r["glob_calls"])]
    return ("of %d faces reached only by a glob that names an ancestor, %d are opened by some "
            "landing sweep, %d are opened only by a sweeper no entry point runs again, and %d are "
            "opened by no landing sweep at all. Across %d landing modules and %d glob calls, %d "
            "calls open what they yield, %d only read the name, %d carry a pattern that is not a "
            "literal, and %d modules only ever read the name (%s)."
            % (total, counts.get("faces_opened_by_a_landing_sweep", 0),
               counts.get("faces_opened_only_by_a_one_off", 0),
               counts.get("faces_never_opened_by_a_landing_sweep", 0),
               counts.get("modules", 0), counts.get("glob_calls", 0),
               counts.get(C_OPENS, 0) + counts.get(C_HELPER, 0) + counts.get(C_SUBPROC, 0),
               counts.get(C_NAME, 0), counts.get("glob_calls_with_a_computed_pattern", 0),
               len(names), ", ".join(names) or "none"))


def write_face(face):
    os.makedirs(OUTDIR, exist_ok=True)
    body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    for path in (OUT_PATH, os.path.join(OUTDIR, SELF_STEM + "-latest.json")):
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)


# --------------------------------------------------------------------------- guard
def face_problems(face):
    p = []
    if not isinstance(face, dict) or "counts" not in face:
        return ["the face carries no counts block"]
    counts = face["counts"]
    modules = face.get("modules") or []
    faces = face.get("faces") or []
    if not faces:
        p.append("the face publishes no faces")
    if not modules:
        p.append("the face publishes no module rows")
    tally = {}
    calls = 0
    for rec in modules:
        for g in rec.get("glob_calls") or []:
            calls += 1
            t = g.get("treatment")
            if t not in CLASSES:
                p.append("module %s carries an unknown treatment %r" % (rec.get("module"), t))
            tally[t] = tally.get(t, 0) + 1
    for c in CLASSES:
        if counts.get(c, 0) != tally.get(c, 0):
            p.append("counts.%s says %r but the module rows count %r"
                     % (c, counts.get(c), tally.get(c, 0)))
    if counts.get("glob_calls") != calls:
        p.append("counts.glob_calls says %r but the module rows carry %d"
                 % (counts.get("glob_calls"), calls))
    if counts.get("modules") != len(modules):
        p.append("counts.modules says %r but the face publishes %d rows"
                 % (counts.get("modules"), len(modules)))
    if counts.get("faces") != len(faces):
        p.append("counts.faces says %r but the face publishes %d rows"
                 % (counts.get("faces"), len(faces)))
    opened = sum(1 for f in faces if f.get("opened_by_a_landing_sweep"))
    if counts.get("faces_opened_by_a_landing_sweep") != opened:
        p.append("counts.faces_opened_by_a_landing_sweep does not re-derive from the face rows")
    never = sum(1 for f in faces if f.get("never_opened_by_a_landing_sweep"))
    if counts.get("faces_never_opened_by_a_landing_sweep") != never:
        p.append("counts.faces_never_opened_by_a_landing_sweep does not re-derive")
    if opened + never != len(faces):
        p.append("opened + never_opened does not cover every face")
    for f in faces:
        if f.get("opened_by_a_landing_sweep") != bool(f.get("treatments")):
            p.append("face %s disagrees with its own treatment list" % f.get("face"))
            break
    if face.get("verdict") not in VERDICT_VOCAB:
        p.append("verdict %r is outside the vocabulary" % face.get("verdict"))
    else:
        if face["verdict"] != verdict_from(counts):
            p.append("verdict does not follow the counts")
    if not face.get("answer"):
        p.append("the face publishes no answer sentence")
    return p


# --------------------------------------------------------------------------- selftest
def _fixture(files, faces, sites_by_source=None):
    """Throw-away repo laid out like the real one: module files plus an E609 face."""
    tmp = tempfile.mkdtemp(prefix="e615_")
    for rel, text in files.items():
        path = os.path.join(tmp, rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(path) or tmp, exist_ok=True)
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
    rows = []
    for rel, sources in faces.items():
        path = os.path.join(tmp, rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("{}\n")
        dirs = e609.segments(rel)[:-1]
        ancestor = dirs[:1]
        sites = []
        for src in sources:
            pattern = (sites_by_source or {}).get(src, "/".join(ancestor + ["**", "*.json"]))
            sites.append({"source": src, "line": 1, "pattern": pattern,
                          "score": len(ancestor), "naming_segments": ancestor,
                          "named_dir_depth": len(ancestor)})
        rows.append({"face": rel, "present": True, "disagreeing_series": 1,
                     "class": e609.C_PART, "sites": sites})
    p = os.path.join(tmp, "results", "state_tilt", "GLOBSWEEPREACH.json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"faces": rows}, fh)
    return tmp


OPENING_SWEEP = """import glob, json, os
for path in glob.glob("results/**/*.json", recursive=True):
    with open(path, encoding="utf-8") as fh:
        json.load(fh)
"""

NAMING_SWEEP = """import glob, os
names = []
for p in glob.glob("results/**/*.json", recursive=True):
    names.append(os.path.basename(p))
print(len(names))
"""

HELPER_SWEEP = """import glob, json
def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)
for p in glob.glob("results/**/*.json", recursive=True):
    load(p)
"""


def selftest():
    legs = []

    def leg(name, cond, note=""):
        legs.append({"leg": name, "ok": bool(cond), "note": note})

    # 1. an opener is graded OPENS and the face counts as opened
    tmp = _fixture({"results/_r700_sweep.py": OPENING_SWEEP},
                   {"results/paper/A_paper.json": ["results/_r700_sweep.py"]})
    try:
        face, pr = build(root=tmp, write=False)
        leg("an opener is graded OPENS",
            face["modules"][0]["glob_calls"][0]["treatment"] == C_OPENS,
            str(face["modules"][0]["glob_calls"]))
        leg("a face an opener sweeps is opened", face["faces"][0]["opened_by_a_landing_sweep"])
        leg("verdict is SOME when a sweep opens", face["verdict"] == V_SOME, face["verdict"])
        leg("guard accepts the opener fixture", not pr, str(pr))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 2. a name-only sweep opens nothing
    tmp = _fixture({"results/_r701_sweep.py": NAMING_SWEEP},
                   {"results/paper/B_paper.json": ["results/_r701_sweep.py"]})
    try:
        face, pr = build(root=tmp, write=False)
        leg("a basename-only loop is graded NAME",
            face["modules"][0]["glob_calls"][0]["treatment"] == C_NAME,
            str(face["modules"][0]["glob_calls"]))
        leg("a name-only sweep leaves the face never opened",
            face["faces"][0]["never_opened_by_a_landing_sweep"] is True, str(face["faces"][0]))
        leg("verdict is NONE when nothing opens",
            face["verdict"] == V_NONE, face["verdict"])
        leg("guard accepts the name-only fixture", not pr, str(pr))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 3. an open behind a module helper is still an open
    tmp = _fixture({"results/_r702_sweep.py": HELPER_SWEEP},
                   {"results/paper/C_paper.json": ["results/_r702_sweep.py"]})
    try:
        face, _pr = build(root=tmp, write=False)
        leg("a helper that opens its parameter grades HELPER",
            face["modules"][0]["glob_calls"][0]["treatment"] == C_HELPER,
            str(face["modules"][0]["glob_calls"]))
        leg("a helper open still opens the face", face["faces"][0]["opened_by_a_landing_sweep"])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 4. a loop that mentions nothing is DISCARD
    tmp = _fixture({"results/_r703_sweep.py":
                    'import glob\nfor p in glob.glob("results/**/*.json", recursive=True):\n'
                    '    pass\n'},
                   {"results/paper/D.json": ["results/_r703_sweep.py"]})
    try:
        face, _pr = build(root=tmp, write=False)
        leg("an unreferenced yield is graded DISCARD",
            face["modules"][0]["glob_calls"][0]["treatment"] == C_DISCARDS,
            str(face["modules"][0]["glob_calls"]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 5. a computed pattern names nothing
    tmp = _fixture({"Tools/_r704_surgery.py":
                    'import glob as _g\nfor f in ["results"]:\n'
                    '    targets = sorted(_g.glob(f + "/**/*", recursive=True))\n'
                    '    for t in targets:\n        print(t)\n'},
                   {"results/paper/E.json": ["Tools/_r704_surgery.py"]})
    try:
        face, pr = build(root=tmp, write=False)
        call = face["modules"][0]["glob_calls"][0]
        leg("a computed pattern is not a literal", call["pattern_is_a_literal"] is False,
            str(call))
        leg("a computed pattern still has its body priced",
            call["treatment"] == C_NAME, str(call))
        leg("the two-hop binding still finds its loop", call["has_a_loop"] is True, str(call))
        leg("a face whose only sweep cannot be paired is counted",
            face["counts"]["faces_no_sweep_pattern_this_scan_can_pair_with"] == 1,
            str(face["counts"]))
        leg("guard accepts the computed-pattern fixture", not pr, str(pr))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 6. opening is attributed to the sweeper that does it, live vs one-off
    tmp = _fixture({"Tools/s6_chain_bmb.py": 'LEGS = [["python", "scripts/e396_x.py"]]\n',
                    "scripts/e396_x.py": NAMING_SWEEP,
                    "results/_r705_sweep.py": OPENING_SWEEP},
                   {"results/paper/F.json": ["scripts/e396_x.py", "results/_r705_sweep.py"]},
                   sites_by_source={"scripts/e396_x.py": "*/**/*.json"})
    try:
        face, _pr = build(root=tmp, write=False)
        row = face["faces"][0]
        leg("a face opened by a one-off and merely named by a live sweep stays off the live count",
            row["opened_by_a_sweep_an_entry_point_runs_again"] is False, str(row))
        leg("that same face is opened_only_by_a_one_off",
            row["opened_only_by_a_one_off"] is True, str(row))
        leg("the live sweeper is graded LIVE_CHAIN",
            [m for m in face["modules"]
             if m["module"] == "scripts/e396_x.py"][0]["entry_class"] == e611.C_CHAIN,
            str(face["modules"]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 7. the guard can go red
    tmp = _fixture({"results/_r706_sweep.py": OPENING_SWEEP},
                   {"results/paper/G.json": ["results/_r706_sweep.py"]})
    try:
        face, _ = build(root=tmp, write=False)
        bad = json.loads(json.dumps(face))
        bad["counts"][C_OPENS] = 9
        leg("the guard rejects a treatment count that does not re-derive",
            bool(face_problems(bad)))
        bad2 = json.loads(json.dumps(face))
        bad2["verdict"] = V_NONE
        leg("the guard rejects a verdict that does not follow the counts",
            bool(face_problems(bad2)))
        bad3 = json.loads(json.dumps(face))
        bad3["faces"][0]["opened_by_a_landing_sweep"] = False
        bad3["faces"][0]["treatments"] = []
        leg("the guard rejects a face that disagrees with its treatments",
            bool(face_problems(bad3)))
        bad4 = json.loads(json.dumps(face))
        bad4["modules"][0]["glob_calls"][0]["treatment"] = "opens_it_maybe"
        leg("the guard rejects a treatment outside the vocabulary", bool(face_problems(bad4)))
        bad5 = json.loads(json.dumps(face))
        bad5["counts"]["glob_calls"] = 4
        leg("the guard rejects a glob-call count that does not re-derive",
            bool(face_problems(bad5)))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 8. this study's own files are not landing modules
    tmp = _fixture({"scripts/e615_glob_sweep_use.py": NAMING_SWEEP,
                    "results/_r707_sweep.py": OPENING_SWEEP},
                   {"results/paper/H.json": ["scripts/e615_glob_sweep_use.py",
                                             "results/_r707_sweep.py"]},
                   sites_by_source={"scripts/e615_glob_sweep_use.py": "*/**/*.json"})
    try:
        face, _pr = build(root=tmp, write=False)
        leg("this study does not price itself",
            [m["module"] for m in face["modules"]] == ["results/_r707_sweep.py"],
            str([m["module"] for m in face["modules"]]))
        leg("the remaining face is still opened by the real sweeper",
            face["faces"][0]["opened_by_a_landing_sweep"] is True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    failures = [x for x in legs if not x["ok"]]
    print(json.dumps({"legs": len(legs), "failed": len(failures), "detail": failures},
                     ensure_ascii=False, indent=1))
    return 0 if not failures else 1


# --------------------------------------------------------------------------- cli
def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="build")
    args = ap.parse_args(argv[1:])
    cmd = args.cmd.lower()
    if cmd == "selftest":
        return selftest()
    face, problems = build(write=(cmd in ("build", "run")))
    if problems:
        print("PROBLEMS: " + "; ".join(problems))
        return 1
    c = face["counts"]
    print("faces=%d modules=%d glob_calls=%d literal_calls=%d"
          % (c["faces"], c["modules"], c["glob_calls"],
             c["glob_calls_with_a_literal_pattern"]))
    print("treatments=" + json.dumps({k: c.get(k, 0) for k in CLASSES}, sort_keys=True))
    print("faces_opened=%d opened_by_a_live_sweep=%d opened_only_by_a_one_off=%d never_opened=%d"
          % (c["faces_opened_by_a_landing_sweep"],
             c["faces_opened_by_a_sweep_an_entry_point_runs_again"],
             c["faces_opened_only_by_a_one_off"],
             c["faces_never_opened_by_a_landing_sweep"]))
    print("modules_that_open=%d modules_name_only=%d live_modules=%d computed_only_faces=%d"
          % (c["modules_that_open_what_they_glob"], c["modules_that_only_read_the_name"],
             c["live_modules"], c["faces_no_sweep_pattern_this_scan_can_pair_with"]))
    print("computed_pattern_calls=%d" % c["glob_calls_with_a_computed_pattern"])
    print("verdict=" + face["verdict"])
    print("answer=" + face["answer"])
    if cmd in ("check", "verify"):
        pr = face_problems(face)
        print("problems=%s" % json.dumps(pr, ensure_ascii=False))
        return 0 if not pr else 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
