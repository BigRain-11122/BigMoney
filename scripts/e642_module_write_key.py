"""E642 -- do the module-level write sites E640 drops by definition name a key a counted read reads?

E640 answered the in-function question and published its residue as a number: 2,641 of the 5,514
two-depth write sites in the corpus sit at module level, where no enclosing function exists, so
"is the write in the same function as the read" cannot even be asked of them.  But the modules that
hold E633's 13 counted read lines are ordinary modules and their script bodies are exactly where a
dict literal is assigned wholesale -- `LEVELS = {...}` at module scope writes every key the module
later reads.  That is the cheap collision E640 left priced but untested.

This study:

  * takes the modules that hold E633's counted read lines (via E638's join, so the read population
    is the published one and not a second definition),
  * re-parses each of them, resolves every two-depth site to its innermost enclosing function with
    E640's own owner rule, and keeps the sites where that owner is None (module level),
  * publishes, per module, the module-level two-depth sites, the keys their members carry, whether
    each is a write (store/delete) and whether any member key equals a key a counted read line of
    that module reads,
  * publishes the corpus-wide module-level write total beside E640's published 2,641 so a reader can
    see the two populations are the same one, and
  * publishes the cross-module arm: module-level writes anywhere whose key matches any counted row
    key, because a key name is not scoped to its module.

Everything is re-derived from the tree; E640's published count is read from its face only as a
reconciliation figure and is never used as an input.
"""
import argparse
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
FACE = "MODULEWRITEKEY.json"
LATEST = "modulewritekey_latest.json"
STUDY = "E642_module_write_key"
SELF_PARTS = ("e642_", "run_e642_", "_probe_e642", "_r1663")
SOURCE_FACE = "results/state_tilt/WRITEREADCOLLIDE.json"
MAX_EXAMPLES = 25

import e638_two_depth_subscripts as e638  # noqa: E402
import e640_writeread_collide as e640  # noqa: E402

V_WRITE_AT_MODULE_LEVEL_NAMES_A_ROW_KEY = (
    "at_least_one_module_level_two_depth_write_site_sits_in_a_module_that_holds_a_counted_read_"
    "line_and_names_a_key_that_line_reads,_so_the_read_is_not_the_only_access_to_that_key_in_its_"
    "module")
V_MODULE_LEVEL_WRITES_ARE_OF_OTHER_KEYS = (
    "the_modules_holding_the_counted_read_lines_do_carry_module_level_two_depth_write_sites_but_"
    "none_of_them_names_a_key_a_counted_line_reads,_so_module_scope_writes_sit_beside_these_reads_"
    "only_of_other_keys")
V_NO_MODULE_LEVEL_WRITE_IN_THOSE_MODULES = (
    "no_module_that_holds_a_counted_read_line_carries_a_module_level_two_depth_write_site_while_"
    "the_corpus_does_carry_them,_so_the_zero_is_a_property_of_these_modules_not_of_the_form")
V_NO_MODULE_LEVEL_WRITE_ANYWHERE = (
    "no_module_in_the_corpus_carries_a_module_level_two_depth_write_site,_so_the_population_E640_"
    "dropped_is_empty_and_the_question_is_moot")
V_OFF_POPULATION = (
    "the_module_level_two_depth_write_form_exists_in_the_corpus_but_no_module_holding_a_counted_"
    "read_line_resolves_well_enough_to_be_measured,_so_the_question_is_settled_off_the_population_"
    "that_E633_counts")


def say(line):
    sys.stdout.write(line + "\n")


def rel(module, root=ROOT):
    return os.path.relpath(module, root).replace("\\", "/")


def corpus(root=ROOT):
    """E640's population, so the module-level total can be reconciled with its published 2,641."""
    out = []
    for p in e640.corpus(root):
        if os.path.basename(p).startswith(SELF_PARTS):
            continue
        out.append(p)
    return out


def module_level_sites(path):
    """(payload, None) or (None, why): the sites of one file whose owner function is None."""
    got, why = e638.file_sites(path)
    if got is None:
        return None, why
    spans = e640.function_spans(path)
    if spans is None:
        return None, "does_not_parse"
    keep = []
    for s in got["sites"]:
        if e640.innermost_owner(spans, s["line"]) is not None:
            continue
        row = e640.site_row(s)
        row["keys"] = sorted({m.get("key") for m in (s.get("members") or [])
                              if m.get("key") is not None})
        keep.append(row)
    keep.sort(key=lambda r: (r["line"], r["column"]))
    return {"sites": keep, "sites_total": len(got["sites"]),
            "subscript_nodes": got["subscript_nodes"]}, None


def counted_modules(root=ROOT):
    """One record per module holding at least one E633 counted read line."""
    by_module = {}
    for r in e638.join_counted_lines(root):
        module = (r.get("module") or "").replace("\\", "/")
        if not module:
            continue
        rec = by_module.setdefault(module, {"module": module, "read_lines": [], "keys": []})
        rec["read_lines"].append({
            "line": r.get("read_line"),
            "function": r.get("function"),
            "key": r.get("key"),
            "receiver": r.get("receiver"),
        })
        if r.get("key") is not None and r.get("key") not in rec["keys"]:
            rec["keys"].append(r["key"])
    out = sorted(by_module.values(), key=lambda r: r["module"])
    for rec in out:
        rec["read_lines"].sort(key=lambda x: (x["line"] or 0, x["key"] or ""))
        rec["keys"].sort()
    return out


def measure(root=ROOT):
    files = corpus(root)
    holes = {"over_the_size_cap": 0, "unreadable": 0, "does_not_parse": 0}
    corpus_module_writes = 0
    corpus_module_sites = 0
    for p in files:
        got, why = module_level_sites(p)
        if got is None:
            holes[why] = holes.get(why, 0) + 1
            continue
        corpus_module_sites += len(got["sites"])
        corpus_module_writes += sum(1 for s in got["sites"] if s["any_member_is_write"])

    mods = counted_modules(root)
    rows = []
    for rec in mods:
        path = os.path.join(root, rec["module"])
        got, why = module_level_sites(path)
        entry = {
            "module": rec["module"],
            "read_lines": rec["read_lines"],
            "row_keys": rec["keys"],
            "scope_problem": (why if got is None else None),
            "two_depth_sites_in_the_module": (got["sites_total"] if got else 0),
            "module_level_two_depth_sites": (len(got["sites"]) if got else 0),
            "module_level_write_sites": (sum(1 for s in (got["sites"] if got else [])
                                             if s["any_member_is_write"])),
            "sites": [],
        }
        if got is not None:
            for s in got["sites"]:
                named = sorted(set(s["keys"]) & set(rec["keys"]))
                entry["sites"].append({
                    "line": s["line"],
                    "column": s["column"],
                    "depth_pair": s["depth_pair"],
                    "keys": s["keys"],
                    "member_ctx": s["member_ctx"],
                    "any_member_is_write": s["any_member_is_write"],
                    "deepest_member_is_write": s["deepest_member_is_write"],
                    "names_a_row_key": named,
                })
        rows.append(entry)

    counts = counts_of(rows, len(files), holes, corpus_module_sites, corpus_module_writes, mods)
    m = {
        "study": STUDY,
        "source_face": SOURCE_FACE,
        "method": ("take the modules holding E633's counted read lines (E638's join), re-parse each "
                   "of them, keep every two-depth site whose innermost enclosing function is None "
                   "by E640's owner rule, publish its member keys beside the keys the module's "
                   "counted read lines read, and reconcile the corpus-wide module-level write total "
                   "with E640's published figure"),
        "population_source": ("%d Python files of the corpus E640 walks, of which %d module(s) hold "
                              "the counted read lines E638 joins"
                              % (len(files), len(mods))),
        "counts": counts,
        "rows": rows,
        "cross_module": cross_module_arm(root, files, mods),
        "limits": [
            "module level means the site's innermost enclosing function is None under E640's rule, "
            "so a site inside a class body (not a def) is module level here even though it runs at "
            "import time inside the class statement",
            "the collision test is key-name equality on a literal member key; a computed key names "
            "nothing and can never collide, and those sites are published separately rather than "
            "folded into the zero",
            "a module-level dict literal assigns every key it names whether or not the module ever "
            "reads it, so a hit here says the two accesses are in one module, not that they are "
            "ordered or that the value survives",
            "the corpus-wide module-level write total is re-derived with the same grouping and the "
            "same owner rule as E640, but this study's own files are excluded in addition to "
            "E640's, so the two totals are the same population to within this study's own sites",
            "files over 1MB are skipped rather than parsed (E391's cap) and are counted separately",
            "the cross-module arm matches key names against all counted row keys regardless of "
            "module, which is a weaker test than the per-module one and is published apart from it",
        ],
    }
    m["verdict"] = decide(counts)
    m["answer"] = answer_of(counts)
    return m


def cross_module_arm(root, files, mods):
    """Module-level writes anywhere whose key matches any counted row key."""
    keys = set()
    for rec in mods:
        keys.update(rec["keys"])
    hits = []
    sites_scanned = 0
    for p in files:
        got, why = module_level_sites(p)
        if got is None:
            continue
        for s in got["sites"]:
            if not s["any_member_is_write"]:
                continue
            sites_scanned += 1
            named = sorted(set(s["keys"]) & keys)
            if named:
                hits.append({"module": rel(p, root), "line": s["line"],
                             "column": s["column"], "keys": s["keys"],
                             "row_keys_named": named})
    hits.sort(key=lambda h: (h["module"], h["line"]))
    return {
        "counted_row_keys": sorted(keys),
        "module_level_write_sites_scanned": sites_scanned,
        "module_level_write_sites_naming_a_counted_row_key": len(hits),
        "in_the_modules_that_hold_the_reads": sum(
            1 for h in hits if h["module"] in {m["module"] for m in mods}),
        "examples": hits[:MAX_EXAMPLES],
    }


def counts_of(rows, files_scanned, holes, corpus_module_sites, corpus_module_writes, mods):
    sites = [s for r in rows for s in (r.get("sites") or [])]
    writes = [s for s in sites if s["any_member_is_write"]]
    write_keys = set()
    for s in writes:
        write_keys.update(s["keys"])
    row_keys = set()
    for r in rows:
        row_keys.update(r["row_keys"])
    return {
        "python_files_scanned": files_scanned,
        "python_files_over_the_size_cap": int((holes or {}).get("over_the_size_cap") or 0),
        "python_files_unreadable": int((holes or {}).get("unreadable") or 0),
        "python_files_that_do_not_parse": int((holes or {}).get("does_not_parse") or 0),
        "corpus_module_level_two_depth_sites": int(corpus_module_sites),
        "corpus_module_level_two_depth_write_sites": int(corpus_module_writes),
        "modules_holding_a_counted_read_line": len(mods),
        "modules_measured": sum(1 for r in rows if not r.get("scope_problem")),
        "modules_with_a_scope_problem": sum(1 for r in rows if r.get("scope_problem")),
        "counted_read_lines_in_those_modules": sum(len(r["read_lines"]) for r in rows),
        "counted_row_keys": len(row_keys),
        "modules_with_a_module_level_two_depth_site": sum(
            1 for r in rows if r.get("module_level_two_depth_sites")),
        "modules_with_a_module_level_two_depth_write_site": sum(
            1 for r in rows if r.get("module_level_write_sites")),
        "module_level_two_depth_sites_in_those_modules": len(sites),
        "module_level_write_sites_in_those_modules": len(writes),
        "module_level_write_sites_with_a_computed_key": sum(
            1 for s in writes if not s["keys"]),
        "distinct_module_level_write_keys_in_those_modules": len(write_keys),
        "sites_naming_a_row_key": sum(1 for s in sites if s["names_a_row_key"]),
        "write_sites_naming_a_row_key": sum(
            1 for s in writes if s["names_a_row_key"]),
        "modules_whose_module_level_writes_name_a_row_key": sum(
            1 for r in rows if any(s["names_a_row_key"]
                                  for s in (r.get("sites") or [])
                                  if s["any_member_is_write"])),
    }


def decide(c):
    if not c.get("corpus_module_level_two_depth_write_sites"):
        return V_NO_MODULE_LEVEL_WRITE_ANYWHERE
    if not c.get("modules_holding_a_counted_read_line") or not c.get("modules_measured"):
        return V_OFF_POPULATION
    if c.get("write_sites_naming_a_row_key"):
        return V_WRITE_AT_MODULE_LEVEL_NAMES_A_ROW_KEY
    if c.get("module_level_write_sites_in_those_modules"):
        return V_MODULE_LEVEL_WRITES_ARE_OF_OTHER_KEYS
    return V_NO_MODULE_LEVEL_WRITE_IN_THOSE_MODULES


def answer_of(c):
    return ("%d files; the corpus carries %d module-level two-depth site(s) of which %d are writes "
            "(E640 published 2,641 of 5,514 for the same population); %d module(s) hold the %d "
            "counted read line(s) over %d distinct row key(s), and %d of them could be measured: "
            "%d module-level site(s), %d write(s) (%d with a computed key), %d distinct write "
            "key(s); %d site(s) name a row key and %d write(s) do, in %d module(s)"
            % (c.get("python_files_scanned"),
               c.get("corpus_module_level_two_depth_sites"),
               c.get("corpus_module_level_two_depth_write_sites"),
               c.get("modules_holding_a_counted_read_line"),
               c.get("counted_read_lines_in_those_modules"),
               c.get("counted_row_keys"),
               c.get("modules_measured"),
               c.get("module_level_two_depth_sites_in_those_modules"),
               c.get("module_level_write_sites_in_those_modules"),
               c.get("module_level_write_sites_with_a_computed_key"),
               c.get("distinct_module_level_write_keys_in_those_modules"),
               c.get("sites_naming_a_row_key"),
               c.get("write_sites_naming_a_row_key"),
               c.get("modules_whose_module_level_writes_name_a_row_key")))


def face_from(m):
    return {
        "study": STUDY,
        "date": TODAY,
        "source_face": SOURCE_FACE,
        "method": m["method"],
        "population_source": m["population_source"],
        "counts": m["counts"],
        "rows": m["rows"],
        "cross_module": m["cross_module"],
        "limits": m["limits"],
        "verdict": m["verdict"],
        "answer": m["answer"],
    }


COUNT_KEYS = (
    "modules_holding_a_counted_read_line", "modules_measured", "modules_with_a_scope_problem",
    "counted_read_lines_in_those_modules", "counted_row_keys",
    "modules_with_a_module_level_two_depth_site",
    "modules_with_a_module_level_two_depth_write_site",
    "module_level_two_depth_sites_in_those_modules",
    "module_level_write_sites_in_those_modules",
    "module_level_write_sites_with_a_computed_key",
    "distinct_module_level_write_keys_in_those_modules",
    "sites_naming_a_row_key", "write_sites_naming_a_row_key",
    "modules_whose_module_level_writes_name_a_row_key",
)


def face_problems(face):
    """Everything the smoke leg refuses, re-derived from the face's own rows."""
    problems = []
    if not face:
        return ["face is absent or empty"]
    rows = face.get("rows") or []
    c = face.get("counts") or {}
    sites = [s for r in rows for s in (r.get("sites") or [])]
    live = {
        "modules_holding_a_counted_read_line": len(rows),
        "modules_measured": sum(1 for r in rows if not r.get("scope_problem")),
        "modules_with_a_scope_problem": sum(1 for r in rows if r.get("scope_problem")),
        "counted_read_lines_in_those_modules": sum(len(r.get("read_lines") or []) for r in rows),
        "counted_row_keys": len({k for r in rows for k in (r.get("row_keys") or [])}),
        "modules_with_a_module_level_two_depth_site": sum(
            1 for r in rows if r.get("module_level_two_depth_sites")),
        "modules_with_a_module_level_two_depth_write_site": sum(
            1 for r in rows if r.get("module_level_write_sites")),
        "module_level_two_depth_sites_in_those_modules": len(sites),
        "module_level_write_sites_in_those_modules": sum(
            1 for s in sites if s.get("any_member_is_write")),
        "module_level_write_sites_with_a_computed_key": sum(
            1 for s in sites if s.get("any_member_is_write") and not s.get("keys")),
        "distinct_module_level_write_keys_in_those_modules": len(
            {k for s in sites if s.get("any_member_is_write") for k in (s.get("keys") or [])}),
        "sites_naming_a_row_key": sum(1 for s in sites if s.get("names_a_row_key")),
        "write_sites_naming_a_row_key": sum(
            1 for s in sites if s.get("any_member_is_write") and s.get("names_a_row_key")),
        "modules_whose_module_level_writes_name_a_row_key": sum(
            1 for r in rows if any(s.get("names_a_row_key") for s in (r.get("sites") or [])
                                   if s.get("any_member_is_write"))),
    }
    for key in COUNT_KEYS:
        if c.get(key) != live.get(key):
            problems.append("counts.%s does not re-add from the rows" % key)
    for key in ("python_files_scanned", "corpus_module_level_two_depth_sites",
                "corpus_module_level_two_depth_write_sites"):
        if c.get(key) is None:
            problems.append("counts.%s is not published" % key)
    # the two corpus totals are inputs of the census, not sums of these rows; the verdict however
    # depends on them, so it is decided on the published totals beside the re-derived row sums
    live["corpus_module_level_two_depth_sites"] = c.get("corpus_module_level_two_depth_sites")
    live["corpus_module_level_two_depth_write_sites"] = c.get(
        "corpus_module_level_two_depth_write_sites")
    if decide(live) != face.get("verdict"):
        problems.append("the published verdict is not the one the counts force")
    for r in rows:
        if (r.get("module_level_two_depth_sites") or 0) > (r.get("two_depth_sites_in_the_module")
                                                           or 0):
            problems.append("module %s has more module-level sites than sites"
                            % r.get("module"))
            break
        if (r.get("module_level_write_sites") or 0) > (r.get("module_level_two_depth_sites") or 0):
            problems.append("module %s has more module-level writes than sites" % r.get("module"))
            break
        if len(r.get("sites") or []) != (r.get("module_level_two_depth_sites") or 0):
            problems.append("module %s publishes a site count its list does not carry"
                            % r.get("module"))
            break
        keys = set(r.get("row_keys") or [])
        for s in r.get("sites") or []:
            if s.get("names_a_row_key") and not (set(s.get("names_a_row_key")) <= keys):
                problems.append("module %s names a key the module does not read"
                                % r.get("module"))
                break
            if s.get("names_a_row_key") and not (set(s.get("names_a_row_key"))
                                                 <= set(s.get("keys") or [])):
                problems.append("module %s names a row key its members do not carry"
                                % r.get("module"))
                break
            carries_write = any(ctx in e640.WRITE_CTX for ctx in (s.get("member_ctx") or []))
            if s.get("any_member_is_write") != carries_write:
                problems.append("module %s has a write flag its member contexts do not carry"
                                % r.get("module"))
                break
    cm = face.get("cross_module") or {}
    if cm.get("module_level_write_sites_naming_a_counted_row_key") is not None:
        if cm.get("module_level_write_sites_naming_a_counted_row_key") < len(
                cm.get("examples") or []):
            problems.append("the cross-module arm publishes fewer examples than it counts")
    if face.get("verdict") == V_WRITE_AT_MODULE_LEVEL_NAMES_A_ROW_KEY \
            and not c.get("write_sites_naming_a_row_key"):
        problems.append("the verdict reports a hit the counts do not carry")
    if face.get("verdict") in (V_MODULE_LEVEL_WRITES_ARE_OF_OTHER_KEYS,
                               V_NO_MODULE_LEVEL_WRITE_IN_THOSE_MODULES) \
            and c.get("write_sites_naming_a_row_key"):
        problems.append("the no-hit verdict is not the one its own counts force")
    if face.get("verdict") == V_NO_MODULE_LEVEL_WRITE_IN_THOSE_MODULES \
            and (c.get("module_level_write_sites_in_those_modules")
                 or not c.get("corpus_module_level_two_depth_write_sites")):
        problems.append("the module-level zero verdict is not the one its totals force")
    return problems


def write_face(out_dir, doc, face=FACE, latest=LATEST):
    os.makedirs(out_dir, exist_ok=True)
    for name in (face, latest):
        path = os.path.join(out_dir, name)
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
        say("run: %s" % os.path.relpath(path, ROOT))


def build(root=ROOT, out_dir=None):
    doc = face_from(measure(root))
    write_face(out_dir or OUTDIR, doc)
    c = doc["counts"]
    say("run: files=%d corpus_module_sites=%d corpus_module_writes=%d modules=%d measured=%d "
        "sites=%d writes=%d row_keys=%d hits=%d"
        % (c["python_files_scanned"], c["corpus_module_level_two_depth_sites"],
           c["corpus_module_level_two_depth_write_sites"],
           c["modules_holding_a_counted_read_line"], c["modules_measured"],
           c["module_level_two_depth_sites_in_those_modules"],
           c["module_level_write_sites_in_those_modules"], c["counted_row_keys"],
           c["write_sites_naming_a_row_key"]))
    say("run: verdict=" + doc["verdict"])
    say("run: answer=" + doc["answer"])
    return doc, []


# ---------------------------------------------------------------- selftest
def _site(line, column, keys=(), ctxs=("load", "load"), named=()):
    return {"line": line, "column": column, "depth_pair": "1->2", "keys": list(keys),
            "member_ctx": list(ctxs),
            "any_member_is_write": any(x in e640.WRITE_CTX for x in ctxs),
            "deepest_member_is_write": ctxs[-1] in e640.WRITE_CTX,
            "names_a_row_key": list(named)}


FIXTURE_HIT = [{
    "module": "a.py", "read_lines": [{"line": 20, "function": "f", "key": "k", "receiver": "R"}],
    "row_keys": ["k"], "scope_problem": None, "two_depth_sites_in_the_module": 3,
    "module_level_two_depth_sites": 2, "module_level_write_sites": 1,
    "sites": [_site(3, 0, keys=["k"], ctxs=("load", "store"), named=["k"]),
              _site(20, 4, keys=["k"], ctxs=("load", "load"))]}]

FIXTURE_OTHER = [{
    "module": "a.py", "read_lines": [{"line": 20, "function": "f", "key": "k", "receiver": "R"}],
    "row_keys": ["k"], "scope_problem": None, "two_depth_sites_in_the_module": 2,
    "module_level_two_depth_sites": 1, "module_level_write_sites": 1,
    "sites": [_site(3, 0, keys=["z"], ctxs=("load", "store"))]}]

FIXTURE_READ_ONLY = [{
    "module": "b.py", "read_lines": [{"line": 12, "function": "g", "key": "days",
                                     "receiver": "P"}],
    "row_keys": ["days"], "scope_problem": None, "two_depth_sites_in_the_module": 2,
    "module_level_two_depth_sites": 1, "module_level_write_sites": 0,
    "sites": [_site(12, 4, keys=["days"], ctxs=("load", "load"))]}]


def _fixture_module(source):
    path = e640._fixture_path(source)
    try:
        return module_level_sites(path)
    finally:
        try:
            os.remove(path)
        except OSError:
            pass


def selftest():
    legs = []

    def leg(name, fn):
        try:
            fn()
            legs.append((name, True))
            say("PASS :: " + name)
        except AssertionError as exc:
            legs.append((name, False))
            say("FAIL :: %s :: %s" % (name, exc))

    def a_module_level_site_is_kept():
        got, why = _fixture_module('LV = 1\nD["k"]["j"] = 2\n')
        assert why is None, why
        assert len(got["sites"]) == 1, got
        assert got["sites"][0]["any_member_is_write"], got

    def a_site_inside_a_function_is_dropped():
        got, why = _fixture_module('def f():\n    D["k"]["j"] = 2\n')
        assert why is None, why
        assert got["sites"] == [], got
        assert got["sites_total"] == 1, got

    def a_class_body_site_is_module_level_here():
        got, why = _fixture_module('class C:\n    D["k"]["j"] = 2\n')
        assert why is None, why
        assert len(got["sites"]) == 1, got

    def keys_of_the_members_are_published():
        got, why = _fixture_module('D["k"]["j"] = 2\nE["q"]["r"] = 3\n')
        assert why is None, why
        keys = [s["keys"] for s in got["sites"]]
        assert ["j", "k"] in keys and ["q", "r"] in keys, keys

    def counts_add_up():
        c = counts_of(FIXTURE_HIT + FIXTURE_READ_ONLY, 3, {}, 40, 9, FIXTURE_HIT + FIXTURE_READ_ONLY)
        assert c["modules_holding_a_counted_read_line"] == 2, c
        assert c["module_level_two_depth_sites_in_those_modules"] == 3, c
        assert c["module_level_write_sites_in_those_modules"] == 1, c
        assert c["counted_row_keys"] == 2, c

    def a_hit_is_reachable():
        c = counts_of(FIXTURE_HIT, 3, {}, 40, 9, FIXTURE_HIT)
        assert c["write_sites_naming_a_row_key"] == 1, c
        assert decide(c) == V_WRITE_AT_MODULE_LEVEL_NAMES_A_ROW_KEY

    def other_keys_are_reachable():
        c = counts_of(FIXTURE_OTHER, 3, {}, 40, 9, FIXTURE_OTHER)
        assert c["write_sites_naming_a_row_key"] == 0, c
        assert decide(c) == V_MODULE_LEVEL_WRITES_ARE_OF_OTHER_KEYS

    def a_read_only_module_is_placed_by_the_corpus():
        c = counts_of(FIXTURE_READ_ONLY, 3, {}, 40, 9, FIXTURE_READ_ONLY)
        assert decide(c) == V_NO_MODULE_LEVEL_WRITE_IN_THOSE_MODULES

    def no_module_write_anywhere_is_reachable():
        c = counts_of(FIXTURE_READ_ONLY, 3, {}, 0, 0, FIXTURE_READ_ONLY)
        assert decide(c) == V_NO_MODULE_LEVEL_WRITE_ANYWHERE

    def off_population_is_reachable():
        row = dict(FIXTURE_HIT[0], scope_problem="does_not_parse", sites=[],
                   module_level_two_depth_sites=0, module_level_write_sites=0)
        c = counts_of([row], 3, {}, 40, 9, [row])
        assert decide(c) == V_OFF_POPULATION

    def a_computed_key_can_never_hit():
        s = _site(3, 0, keys=[], ctxs=("load", "store"), named=[])
        row = dict(FIXTURE_HIT[0], sites=[s], module_level_two_depth_sites=1,
                   module_level_write_sites=1)
        c = counts_of([row], 3, {}, 40, 9, [row])
        assert c["module_level_write_sites_with_a_computed_key"] == 1, c
        assert c["write_sites_naming_a_row_key"] == 0, c
        assert decide(c) == V_MODULE_LEVEL_WRITES_ARE_OF_OTHER_KEYS

    def face_problems_accepts_a_sound_face():
        for rows in (FIXTURE_HIT, FIXTURE_OTHER, FIXTURE_READ_ONLY):
            c = counts_of(rows, 3, {}, 40, 9, rows)
            face = {"rows": rows, "counts": c, "verdict": decide(c),
                    "cross_module": {"module_level_write_sites_naming_a_counted_row_key": 0,
                                     "examples": []}}
            assert not face_problems(face), (rows[0]["module"], face_problems(face))

    def face_problems_catches_a_wrong_verdict():
        c = counts_of(FIXTURE_HIT, 3, {}, 40, 9, FIXTURE_HIT)
        face = {"rows": FIXTURE_HIT, "counts": c,
                "verdict": V_MODULE_LEVEL_WRITES_ARE_OF_OTHER_KEYS,
                "cross_module": {}}
        assert any("verdict" in p for p in face_problems(face)), face_problems(face)

    def face_problems_catches_a_hit_on_a_key_the_module_does_not_read():
        row = json.loads(json.dumps(FIXTURE_HIT[0]))
        row["sites"][0]["names_a_row_key"] = ["zzz"]
        c = counts_of([row], 3, {}, 40, 9, [row])
        face = {"rows": [row], "counts": c,
                "verdict": V_WRITE_AT_MODULE_LEVEL_NAMES_A_ROW_KEY, "cross_module": {}}
        assert any("does not read" in p for p in face_problems(face)), face_problems(face)

    def face_problems_catches_a_write_flag_that_lies():
        row = json.loads(json.dumps(FIXTURE_OTHER[0]))
        row["sites"][0]["any_member_is_write"] = False
        c = counts_of([row], 3, {}, 40, 9, [row])
        face = {"rows": [row], "counts": c, "verdict": V_NO_MODULE_LEVEL_WRITE_IN_THOSE_MODULES,
                "cross_module": {}}
        assert any("write flag" in p for p in face_problems(face)), face_problems(face)

    def face_problems_catches_a_summary_that_drifts():
        c = counts_of(FIXTURE_HIT, 3, {}, 40, 9, FIXTURE_HIT)
        c["module_level_write_sites_in_those_modules"] = 99
        face = {"rows": FIXTURE_HIT, "counts": c,
                "verdict": V_WRITE_AT_MODULE_LEVEL_NAMES_A_ROW_KEY, "cross_module": {}}
        assert any("does not re-add" in p for p in face_problems(face)), face_problems(face)

    def answer_names_the_numbers():
        a = answer_of(counts_of(FIXTURE_HIT, 3, {}, 40, 9, FIXTURE_HIT))
        assert "module-level two-depth site(s) of which 9 are writes" in a, a

    for name, fn in [
        ("a_module_level_site_is_kept", a_module_level_site_is_kept),
        ("a_site_inside_a_function_is_dropped", a_site_inside_a_function_is_dropped),
        ("a_class_body_site_is_module_level_here", a_class_body_site_is_module_level_here),
        ("keys_of_the_members_are_published", keys_of_the_members_are_published),
        ("counts_add_up", counts_add_up),
        ("a_hit_is_reachable", a_hit_is_reachable),
        ("other_keys_are_reachable", other_keys_are_reachable),
        ("a_read_only_module_is_placed_by_the_corpus", a_read_only_module_is_placed_by_the_corpus),
        ("no_module_write_anywhere_is_reachable", no_module_write_anywhere_is_reachable),
        ("off_population_is_reachable", off_population_is_reachable),
        ("a_computed_key_can_never_hit", a_computed_key_can_never_hit),
        ("face_problems_accepts_a_sound_face", face_problems_accepts_a_sound_face),
        ("face_problems_catches_a_wrong_verdict", face_problems_catches_a_wrong_verdict),
        ("face_problems_catches_a_hit_on_a_key_the_module_does_not_read",
         face_problems_catches_a_hit_on_a_key_the_module_does_not_read),
        ("face_problems_catches_a_write_flag_that_lies",
         face_problems_catches_a_write_flag_that_lies),
        ("face_problems_catches_a_summary_that_drifts", face_problems_catches_a_summary_that_drifts),
        ("answer_names_the_numbers", answer_names_the_numbers),
    ]:
        leg(name, fn)
    ok = sum(1 for _, good in legs if good)
    say("selftest: %d/%d legs green" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


# ---------------------------------------------------------------- CLI
def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run")
    args = ap.parse_args(argv[1:])
    cmd = args.cmd.lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "check":
        doc, problems = build(root=ROOT)
        problems = problems + face_problems(doc)
        say("problems=" + json.dumps(problems, ensure_ascii=False))
        return 0 if not problems else 1
    if cmd == "verify":
        path = os.path.join(OUTDIR, FACE)
        if not os.path.exists(path):
            say("no face at %s" % path)
            return 1
        doc = json.load(io.open(path, encoding="utf-8"))
        problems = face_problems(doc)
        say("problems=" + json.dumps(problems, ensure_ascii=False))
        return 0 if not problems else 1
    doc, problems = build(root=ROOT)
    problems = problems + face_problems(doc)
    if problems:
        say("PROBLEMS: " + "; ".join(problems))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))