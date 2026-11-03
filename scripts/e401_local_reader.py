"""E401 -- a project-local reader is invisible to a stdlib call table.

E384 classified every published key's sites by the stdlib call family that surrounds them
(``open``/``load``/``read_*``/``dump``/``write_*``) and left exactly one residue:
``results/perpetual_faces/n1_w192_results.json`` is named only at
``Tools/_r789bmc_post_rebase_verify.py:12`` inside ``json.loads(show(...))``, where ``show()`` is a
project-local helper that reads a blob.  A table built from stdlib names cannot see such a reader,
so the same blind spot could hide a population behind one helper.

This study builds the missing table -- every project-local callable whose body opens or dumps a
file, resolved transitively to a bounded depth -- then **re-runs E384's own classifier** with those
names added (the classifier itself is not rewritten: ``e384.classify_call`` is patched for the
duration of one ``e384.io_map`` call and restored in a ``finally``).  It publishes which keys change
class, how many site lines the stdlib table could not see, and the sentence that says what the old
table would have called those keys.

Usage: ``python scripts/e401_local_reader.py [run|verify|selftest]``
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

import e350_field_branch_census as e350  # noqa: E402
import e383_shared_key_collision as e383  # noqa: E402
import e384_never_opened_key as e384  # noqa: E402

TODAY = "2026-11-04"
FACE = "LOCALREADER-%s.json" % TODAY
LATEST = "localreader_latest.json"
PUBLISHED_DIR = os.path.join(ROOT, "results", "state_tilt")
STUDY = "E401_local_reader"
SELF_REL = "scripts/e401_local_reader.py"
OWN_FILES = (FACE, LATEST, "scripts/run_e401_smoke_leg.py")
MAX_DEPTH = 4
MAX_ROWS = 300

KIND_NONE = "none"
KIND_LOAD = "load"
KIND_DUMP = "dump"
KIND_BOTH = "both"

# A helper can also read a BLOB rather than a file: ``subprocess.run(["git", "show", "HEAD:"+p])``
# never opens a path, so no table of file-opening callables can classify it.  The one residue E384
# published is exactly that shape, so it is priced on its own arm instead of being folded in.
GIT_OBJECT_SUBCMDS = frozenset(("show", "cat-file", "ls-tree", "rev-parse", "log", "diff"))
SPAWN_CALLS = frozenset(("run", "check_output", "Popen", "call", "check_call", "system", "git_show"))

V_NO_HELPER = "no_project_local_callable_in_the_corpus_opens_a_file_so_the_stdlib_table_is_complete"
V_NO_SITE = "the_helper_table_reaches_the_corpus_but_adds_no_site_the_stdlib_call_table_could_not_see"
V_KEYS_MOVED = ("a_project_local_helper_hides_readers_of_published_keys_and_the_old_table_counted_"
                "those_keys_as_named_only_by_non_opening_sites")
V_SITES_ONLY = ("project_local_helpers_open_files_but_every_key_they_open_was_already_classified_by_"
                "a_stdlib_call_so_no_published_class_moves")


def say(message):
    print(message, flush=True)


# --------------------------------------------------------------------------- corpus

def corpus():
    return e350._sources()


# --------------------------------------------------------------------------- helper table

def _body_calls(func_node):
    """Callee names called in this function's body, not counting its nested defs' bodies."""
    names = set()
    stack = list(getattr(func_node, "body", []) or [])
    while stack:
        node = stack.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
            # a nested callable's calls belong to that callable, not to this one
            continue
        if isinstance(node, ast.Call):
            name = e384.callee_name(node)
            if name:
                names.add(name)
        stack.extend(ast.iter_child_nodes(node))
    return names


def git_object_read(func_node):
    """Does this body spawn git with a subcommand that prints an object (``show``/``cat-file``...)?

    The subcommand must appear as its own string literal in an argv list, so a docstring that
    mentions "show" does not qualify.
    """
    stack = list(getattr(func_node, "body", []) or [])
    while stack:
        node = stack.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
            continue
        if isinstance(node, ast.Call) and e384.callee_name(node) in SPAWN_CALLS:
            for arg in node.args:
                if isinstance(arg, (ast.List, ast.Tuple)):
                    for elt in arg.elts:
                        if (isinstance(elt, ast.Constant) and isinstance(elt.value, str)
                                and elt.value in GIT_OBJECT_SUBCMDS):
                            return True
        stack.extend(ast.iter_child_nodes(node))
    return False


def local_defs(sources):
    """name -> [ {source, line, callees, stdlib_kind, git_object} ] for every def in the corpus."""
    defs = {}
    parsed = failed = 0
    for relpath, text in sources:
        try:
            tree = ast.parse(text)
        except SyntaxError:
            failed += 1
            continue
        parsed += 1
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            callees = _body_calls(node)
            direct = KIND_NONE
            for callee in callees:
                klass = e384.classify_call(callee)
                if klass == e384.SITE_LOAD:
                    direct = KIND_LOAD if direct == KIND_NONE else (
                        direct if direct == KIND_LOAD else KIND_BOTH)
                elif klass == e384.SITE_DUMP:
                    direct = KIND_DUMP if direct == KIND_NONE else (
                        direct if direct == KIND_DUMP else KIND_BOTH)
            defs.setdefault(node.name, []).append({
                "source": relpath, "line": node.lineno,
                "callees": sorted(callees), "stdlib_kind": direct,
                "git_object": git_object_read(node),
            })
    return defs, parsed, failed


def _merge(a, b):
    if a == KIND_NONE:
        return b
    if b == KIND_NONE or a == b:
        return a
    return KIND_BOTH


def resolve(defs):
    """name -> {kind, depth, chain, git_object, git_chain}: transitive closure over local calls,
    bounded and cycle-safe.  The git-object arm is propagated by the same relaxation."""
    out = {}
    for name, entries in defs.items():
        kind = KIND_NONE
        for entry in entries:
            kind = _merge(kind, entry["stdlib_kind"])
        best = {"kind": kind, "depth": 1 if kind != KIND_NONE else None, "chain": [],
                "git_object": any(e["git_object"] for e in entries), "git_chain": []}
        for entry in entries:
            if entry["stdlib_kind"] != KIND_NONE:
                best["chain"] = [name, "%s:%d" % (entry["source"], entry["line"])]
                break
            if entry["git_object"]:
                best["git_chain"] = [name, "%s:%d" % (entry["source"], entry["line"])]
        out[name] = best

    # breadth-first relaxation: each pass lets a helper inherit a child's kind one level deeper
    for depth in range(2, MAX_DEPTH + 1):
        changed = False
        for name, entries in defs.items():
            if out[name]["kind"] == KIND_NONE:
                for entry in entries:
                    for callee in entry["callees"]:
                        child = out.get(callee)
                        if not child or child["kind"] == KIND_NONE:
                            continue
                        hop = (child["depth"] or 0) + 1
                        if hop > MAX_DEPTH:
                            continue
                        out[name] = {
                            "kind": child["kind"],
                            "depth": hop,
                            "chain": [name] + list(child["chain"]),
                            "git_object": out[name]["git_object"],
                            "git_chain": out[name]["git_chain"],
                        }
                        changed = True
                        break
                    if out[name]["kind"] != KIND_NONE:
                        break
    return out


def helper_table(sources):
    defs, parsed, failed = local_defs(sources)
    resolved = resolve(defs)
    helpers = {}
    git_readers = {}
    for name, info in resolved.items():
        if info["kind"] != KIND_NONE:
            helpers[name] = {
                "name": name,
                "kind": info["kind"],
                "depth": info["depth"],
                "chain": info["chain"],
                "definitions": [{"source": e["source"], "line": e["line"]} for e in defs[name]],
                "stdlib_arms": sum(1 for e in defs[name] if e["stdlib_kind"] != KIND_NONE),
            }
        if info["git_object"]:
            git_readers[name] = {
                "name": name,
                "chain": info["git_chain"],
                "definitions": [{"source": e["source"], "line": e["line"]} for e in defs[name]],
            }
    return {
        "helpers": helpers,
        "helpers_direct": {k: v for k, v in helpers.items() if v["stdlib_arms"]},
        "git_readers": git_readers,
        "defs": defs,
        "parsed": parsed,
        "failed": failed,
        "names_total": len(defs),
        "names_defined_more_than_once": sum(1 for v in defs.values() if len(v) > 1),
    }


# --------------------------------------------------------------------------- classifier re-run

def _patched_classify(table):
    original = e384.classify_call

    def patched(name, node=None):
        klass = original(name, node)
        if klass != e384.SITE_OTHER:
            return klass
        helper = table.get(name)
        if not helper:
            return klass
        if helper["kind"] == KIND_LOAD:
            return e384.SITE_LOAD
        if helper["kind"] == KIND_DUMP:
            return e384.SITE_DUMP
        # both: a helper that both reads and writes cannot be attributed to one side
        return klass

    return original, patched


def _tally(rows):
    out = {}
    for row in rows.values():
        out[row["class"]] = out.get(row["class"], 0) + 1
    return out


def _move_tally(moved_sites):
    """(stdlib class -> class with helpers) counts: a site can move dump->load when a helper call
    sits inside a dump, so the movement is not one-directional and must be published."""
    out = {}
    for row in moved_sites:
        pair = "%s->%s" % (row["stdlib_class"], row["with_helpers"])
        out[pair] = out.get(pair, 0) + 1
    return out


def callees_on_line(text, line):
    """Every callee name called on this line -- used to price what an 'other' site actually does."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return set()
    names = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if getattr(node, "lineno", 0) <= line <= (getattr(node, "end_lineno", None) or 0):
            name = e384.callee_name(node)
            if name:
                names.add(name)
    return names


def io_map_with_helpers(sources, table):
    """Run E384's own io_map once with the helper names added, then restore the classifier."""
    original, patched = _patched_classify(table)
    e384.classify_call = patched
    try:
        return e384.io_map(sources)
    finally:
        e384.classify_call = original


# --------------------------------------------------------------------------- build / verify

def build(write_face=True, sources=None):
    if sources is None:
        sources = corpus()
    say("corpus sources=%d" % len(sources))

    say("building the project-local helper table")
    ht = helper_table(sources)
    table = ht["helpers"]
    say("defs=%d helpers-that-open-a-file=%d" % (ht["names_total"], len(table)))

    say("keying the corpus (E383)")
    keyed = e383.keyed_sites(sources)["keyed"]
    say("keys=%d" % len(keyed))

    say("classifying with the stdlib table (E384, unpatched)")
    io_base, parsed_base, failed_base = e384.io_map(sources)
    say("base call-covered lines=%d" % len(io_base))

    rows_base = {k: e384.key_row(k, v["sites"], io_base) for k, v in keyed.items()}

    def arm(label, table_arm):
        """Re-run E384's classifier with one helper table and price what changed."""
        say("classifying again with the %s helper names" % label)
        io_ext, _p, _f = io_map_with_helpers(sources, table_arm)
        moved_sites = []
        for key, klass in sorted(io_ext.items()):
            if klass == e384.SITE_OTHER:
                continue
            base = io_base.get(key, e384.SITE_OTHER)
            if base != klass:
                moved_sites.append({"source": key[0], "line": key[1],
                                    "stdlib_class": base, "with_helpers": klass})
        rows_ext = {k: e384.key_row(k, v["sites"], io_ext) for k, v in keyed.items()}
        moved_keys = []
        for key in sorted(keyed):
            b, e = rows_base[key], rows_ext[key]
            if b["class"] == e["class"]:
                continue
            moved_keys.append({
                "key": key,
                "stdlib_class": b["class"],
                "with_helpers": e["class"],
                "n_sites": e["n_sites"],
                "stdlib_load": b["n_load"], "stdlib_dump": b["n_dump"],
                "stdlib_other": b["n_other"],
                "helper_load": e["n_load"], "helper_dump": e["n_dump"],
                "helper_other": e["n_other"],
                "sites": e["sites"],
                "what_the_old_table_called_it": b["class"],
            })
        say("%s: %d helper names, %d site lines moved, %d keys moved"
            % (label, len(table_arm), len(moved_sites), len(moved_keys)))
        return {
            "helper_names": len(table_arm),
            "io_map": io_ext,
            "rows": rows_ext,
            "moved_sites": moved_sites,
            "moved_keys": moved_keys,
            "by_class": _tally(rows_ext),
        }

    ext = arm("transitive", table)
    io_ext, rows_ext = ext["io_map"], ext["rows"]
    moved_sites, moved_keys = ext["moved_sites"], ext["moved_keys"]
    direct = arm("direct-only", ht["helpers_direct"])

    base_class = _tally(rows_base)
    ext_class = ext["by_class"]

    # price every site the stdlib table calls 'other': if all of them are git-blob reads, the
    # residue class is scoped rather than silent
    texts = dict(sources)
    git_names = set(ht["git_readers"])
    other_sites = []
    for key in sorted(keyed):
        for site in keyed[key]["sites"]:
            where = (site["source"], site["line"])
            if io_base.get(where, e384.SITE_OTHER) != e384.SITE_OTHER:
                continue
            hit = callees_on_line(texts.get(site["source"], ""), site["line"]) & git_names
            other_sites.append({
                "key": key,
                "source": site["source"],
                "line": site["line"],
                "role": site["role"],
                "callees": sorted(hit),
                "is_a_git_object_read": bool(hit),
            })

    # the E384 residue this card names, measured directly -- and priced on the git-object arm,
    # because ``show()`` there shells out to ``git show HEAD:<path>`` and never opens a path
    named_residue = "results/perpetual_faces/n1_w192_results.json"
    residue_site = ("Tools/_r789bmc_post_rebase_verify.py", 12)
    residue_def = ("Tools/_r789bmc_post_rebase_verify.py", 4)
    residue_row = None
    if named_residue in keyed:
        residue_row = {
            "key": named_residue,
            "stdlib_class": rows_base[named_residue]["class"],
            "with_helpers": rows_ext[named_residue]["class"],
            "sites": rows_ext[named_residue]["sites"],
        }
    residue_git_helper = None
    for name, entry in ht["git_readers"].items():
        if any(d["source"] == residue_def[0] and d["line"] == residue_def[1]
               for d in entry["definitions"]):
            residue_git_helper = {"name": name, "chain": entry["chain"],
                                  "definitions": entry["definitions"]}
            break

    # names defined in more than one place are merged by this table -- publish whether that matters
    disagreeing = []
    for name, entry in table.items():
        kinds = set()
        for d in entry["definitions"]:
            src_defs = ht["defs"][name]
            for cand in src_defs:
                if cand["source"] == d["source"] and cand["line"] == d["line"]:
                    kinds.add(cand["stdlib_kind"])
        if entry["depth"] and entry["depth"] > 1:
            kinds.add("via_local_call")
        if len(kinds) > 1:
            disagreeing.append(name)

    summary = {
        "corpus_sources": len(sources),
        "corpus_parsed": ht["parsed"],
        "corpus_skipped": ht["failed"],
        "local_defs_total": ht["names_total"],
        "local_defs_named_more_than_once": ht["names_defined_more_than_once"],
        "helpers_that_open_a_file": len(table),
        "helpers_load": sum(1 for v in table.values() if v["kind"] == KIND_LOAD),
        "helpers_dump": sum(1 for v in table.values() if v["kind"] == KIND_DUMP),
        "helpers_both": sum(1 for v in table.values() if v["kind"] == KIND_BOTH),
        "helpers_reaching_by_depth": {
            str(d): sum(1 for v in table.values() if v["depth"] == d)
            for d in sorted({v["depth"] for v in table.values() if v["depth"]})
        },
        "max_depth_used": max([v["depth"] or 0 for v in table.values()] or [0]),
        "helper_names_with_disagreeing_definitions": len(disagreeing),
        "keys_total": len(keyed),
        "sites_classified_line_count_stdlib": len(io_base),
        "sites_classified_line_count_with_helpers": len(io_ext),
        "site_lines_the_stdlib_table_could_not_see": len(moved_sites),
        "keys_that_move_class": len(moved_keys),
        "direct_only_arm": {
            "helper_names": direct["helper_names"],
            "site_lines_the_stdlib_table_could_not_see": len(direct["moved_sites"]),
            "keys_that_move_class": len(direct["moved_keys"]),
        },
        "sites_the_stdlib_table_calls_other": len(other_sites),
        "of_which_a_git_object_read": sum(1 for r in other_sites if r["is_a_git_object_read"]),
        "keys_carrying_an_other_site": len({r["key"] for r in other_sites}),
        "keys_named_only_by_git_object_reads": sum(
            1 for key in keyed
            if keyed[key]["sites"] and all(
                io_base.get((s["source"], s["line"]), e384.SITE_OTHER) == e384.SITE_OTHER
                for s in keyed[key]["sites"])),
        "site_line_moves_by_from_to": _move_tally(moved_sites),
        "site_lines_beyond_the_published_rows": max(0, len(moved_sites) - MAX_ROWS),
        "helpers_beyond_the_published_rows": max(0, len(table) - MAX_ROWS),
        "keys_moved_from_bare_to_opened": sum(
            1 for r in moved_keys
            if r["stdlib_class"] != e384.CLASS_OPENED and r["with_helpers"] == e384.CLASS_OPENED),
        "by_class_stdlib": base_class,
        "by_class_with_helpers": ext_class,
        "classes_sum_to_the_population_stdlib": sum(base_class.values()) == len(keyed),
        "classes_sum_to_the_population_with_helpers": sum(ext_class.values()) == len(keyed),
        "named_residue_key": named_residue,
        "named_residue_stdlib_class": (residue_row or {}).get("stdlib_class"),
        "named_residue_class_with_helpers": (residue_row or {}).get("with_helpers"),
        "named_residue_still_bare_after_the_helper_table":
            (residue_row or {}).get("with_helpers") == e384.CLASS_CONSTRUCTED,
        "helpers_that_read_a_git_object": len(ht["git_readers"]),
        "named_residue_helper_reads_a_git_object": bool(residue_git_helper),
        "classifier_restored_after_the_run": e384.classify_call.__name__ == "classify_call",
    }
    summary["verdict"] = decide(summary)

    n_helpers = summary["helpers_that_open_a_file"]
    n_sites = summary["site_lines_the_stdlib_table_could_not_see"]
    n_keys = summary["keys_that_move_class"]
    base_bare = summary["by_class_stdlib"].get(e384.CLASS_CONSTRUCTED, 0)
    ext_bare = summary["by_class_with_helpers"].get(e384.CLASS_CONSTRUCTED, 0)
    if not n_helpers:
        answer = "no project-local callable in the corpus opens a file, so the stdlib table sees every reader"
    elif not n_sites:
        answer = ("%d project-local callables open a file, but not one key literal is passed to them, "
                  "so the stdlib table misses no site" % n_helpers)
    elif n_keys:
        answer = ("%d project-local callables open a file and the stdlib table calls %d site lines "
                  "'other' that are in fact opens (%d load / %d dump); %d published keys move class, "
                  "and the keys named only by non-opening sites fall from %d to %d -- the old table "
                  "called those %d keys bare literals"
                  % (n_helpers, n_sites,
                     sum(1 for m in moved_sites if m["with_helpers"] == e384.SITE_LOAD),
                     sum(1 for m in moved_sites if m["with_helpers"] == e384.SITE_DUMP),
                     n_keys, base_bare, ext_bare, len(moved_keys)))
    else:
        answer = ("%d project-local callables open a file and they sit on up to %d site lines the "
                  "stdlib table reads as 'other', but every key they open is opened by a stdlib call "
                  "somewhere too, so no published key class moves: the keys named only by "
                  "non-opening sites stay at %d of %d.  The residue is a cohort, not a hidden file "
                  "reader: of the %d sites the stdlib table calls 'other', %d are git-object reads "
                  "(`git show`/`cat-file` through subprocess, %d such helpers), so no table of "
                  "file-opening callables could ever classify them; they span %d keys and %d key "
                  "is named only that way"
                  % (n_helpers, n_sites, ext_bare, summary["keys_total"],
                     summary["sites_the_stdlib_table_calls_other"],
                     summary["of_which_a_git_object_read"],
                     summary["helpers_that_read_a_git_object"],
                     summary["keys_carrying_an_other_site"],
                     summary["keys_named_only_by_git_object_reads"]))

    face = {
        "study": STUDY,
        "evidence_cutoff": TODAY,
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "source": SELF_REL,
        "summary": summary,
        "verdict": summary["verdict"],
        "answer": answer,
        "helper_table": [
            {"name": v["name"], "kind": v["kind"], "depth": v["depth"], "chain": v["chain"],
             "n_definitions": len(v["definitions"]), "definitions": v["definitions"][:4],
             "stdlib_arms": v["stdlib_arms"]}
            for v in sorted(table.values(), key=lambda x: (x["depth"], x["name"]))[:MAX_ROWS]
        ],
        "helper_names_with_disagreeing_definitions": disagreeing[:MAX_ROWS],
        "site_lines_the_stdlib_table_could_not_see": moved_sites[:MAX_ROWS],
        "keys_that_move_class": moved_keys[:MAX_ROWS],
        "direct_only_arm": {
            "helper_names": direct["helper_names"],
            "site_lines_the_stdlib_table_could_not_see": direct["moved_sites"][:MAX_ROWS // 2],
            "keys_that_move_class": direct["moved_keys"][:MAX_ROWS // 2],
        },
        "named_residue": residue_row,
        "other_sites_priced": other_sites,
        "named_residue_helper": residue_git_helper,
        "git_object_readers": [
            {"name": v["name"], "chain": v["chain"], "definitions": v["definitions"][:4]}
            for v in sorted(ht["git_readers"].values(), key=lambda x: x["name"])[:MAX_ROWS]
        ],
        "bounds": {
            "measured": ("every def's direct callees; a helper inherits a kind from a local callee "
                         "for at most %d hops; each key literal is classified by E384's own "
                         "io_map run twice -- once unpatched, once with the helper names added; the "
                         "git-object arm is measured by an argv literal carrying a git subcommand"
                         % MAX_DEPTH),
            "not_measured": ("dispatch through getattr/decorators/imported helpers outside the corpus; "
                             "a name defined in several modules is merged by name, so a site is "
                             "attributed to the union of that name's definitions -- which makes the "
                             "moved-site count an upper bound and is why no key class moves on it"),
            "no_rewrites": "no published face, reader or caller is edited; e384.classify_call is restored",
        },
    }
    say("verdict: %s" % summary["verdict"])
    say(answer)
    if write_face:
        _write(face)
    return face


def decide(summary):
    if not summary.get("helpers_that_open_a_file"):
        return V_NO_HELPER
    if not summary.get("site_lines_the_stdlib_table_could_not_see"):
        return V_NO_SITE
    if summary.get("keys_that_move_class"):
        return V_KEYS_MOVED
    return V_SITES_ONLY


def _write(face):
    os.makedirs(PUBLISHED_DIR, exist_ok=True)
    for name in (FACE, LATEST):
        path = os.path.join(PUBLISHED_DIR, name)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
    say("wrote %s and %s" % (FACE, LATEST))


def verify():
    problems = []
    path = os.path.join(PUBLISHED_DIR, FACE)
    if not os.path.exists(path):
        say("verify problems=['face is absent']")
        return ["face is absent"]
    with io.open(path, encoding="utf-8") as fh:
        face = json.load(fh)
    summary = face["summary"]
    if face.get("evidence_cutoff") != TODAY:
        problems.append("evidence_cutoff moved")
    for side in ("stdlib", "with_helpers"):
        tally = summary.get("by_class_%s" % side) or {}
        if sum(tally.values()) != summary.get("keys_total"):
            problems.append("by_class_%s sums to %d but the population is %d"
                            % (side, sum(tally.values()), summary.get("keys_total")))
    if decide(summary) != face.get("verdict"):
        problems.append("the decision gate does not re-derive the published verdict")
    if summary.get("keys_that_move_class") != len(face.get("keys_that_move_class") or []):
        problems.append("the moved-key headline is not the length of its own list")
    if summary.get("site_lines_the_stdlib_table_could_not_see") != (
            len(face.get("site_lines_the_stdlib_table_could_not_see") or [])
            + summary.get("site_lines_beyond_the_published_rows", 0)):
        problems.append("the moved-site headline is not the length of its own list plus its truncation")
    if summary.get("helpers_that_open_a_file") != (
            len(face.get("helper_table") or []) + summary.get("helpers_beyond_the_published_rows", 0)):
        problems.append("the helper headline is not the length of its own table plus its truncation")
    d = summary.get("direct_only_arm") or {}
    if d.get("site_lines_the_stdlib_table_could_not_see", 0) > summary.get(
            "site_lines_the_stdlib_table_could_not_see", 0):
        problems.append("the direct-only arm moved more sites than the transitive arm")
    if d.get("keys_that_move_class", 0) > summary.get("keys_that_move_class", 0):
        problems.append("the direct-only arm moved more keys than the transitive arm")
    if summary.get("sites_the_stdlib_table_calls_other") != len(face.get("other_sites_priced") or []):
        problems.append("the 'other' site headline is not the length of its own list")
    if summary.get("of_which_a_git_object_read") != sum(
            1 for r in (face.get("other_sites_priced") or []) if r.get("is_a_git_object_read")):
        problems.append("the git-object split does not re-derive from the priced rows")
    if not summary.get("classifier_restored_after_the_run"):
        problems.append("e384.classify_call was not restored after the patched run")
    # every moved key must really change class, and every moved site must really move
    for row in face.get("keys_that_move_class") or []:
        if row["stdlib_class"] == row["with_helpers"]:
            problems.append("%s: a moved key whose class did not move" % row["key"])
        if row["with_helpers"] != e384.CLASS_OPENED:
            problems.append("%s: a moved key that is not opened under the helper table" % row["key"])
    for row in face.get("site_lines_the_stdlib_table_could_not_see") or []:
        if row["stdlib_class"] == row["with_helpers"]:
            problems.append("%s:%s: a moved site whose class did not move"
                            % (row["source"], row["line"]))
    if sum((summary.get("site_line_moves_by_from_to") or {}).values()) != summary.get(
            "site_lines_the_stdlib_table_could_not_see"):
        problems.append("the from->to tally does not sum to the moved-site headline")
    if e384.classify_call.__name__ != "classify_call":
        problems.append("the classifier is patched outside a run")
    # re-derive the priced 'other' rows from the TREE, one file at a time (a full census rebuild is
    # ~110 s and does not belong in an every-round leg; this checks the claim, not the whole sweep)
    cache = {}
    for row in face.get("other_sites_priced") or []:
        rel = row["source"]
        if rel not in cache:
            path = os.path.join(ROOT, rel)
            if not os.path.exists(path):
                cache[rel] = None
            else:
                with io.open(path, encoding="utf-8", errors="replace") as fh:
                    cache[rel] = fh.read()
        text = cache[rel]
        if text is None:
            problems.append("%s: the priced site's source is gone" % rel)
            continue
        git_names = _file_git_reader_names(text)
        hit = sorted(callees_on_line(text, row["line"]) & git_names)
        if bool(hit) != bool(row.get("is_a_git_object_read")):
            problems.append("%s:%s: the git-object claim does not re-derive from the file"
                            % (rel, row["line"]))
        if sorted(hit) != sorted(row.get("callees") or []):
            problems.append("%s:%s: the callee list does not re-derive" % (rel, row["line"]))
    say("verify problems=%s" % (problems or "[]"))
    return problems


def _file_git_reader_names(text):
    """Names defined in THIS file whose body spawns git with an object-printing subcommand."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return set()
    return {node.name for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and git_object_read(node)}


# --------------------------------------------------------------------------- selftest

FIXT_HELPER_LOAD = '''
import json
def show(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()

def read_face():
    return json.loads(show("results/perpetual_faces/n1_w192_results.json"))
'''

FIXT_HELPER_CHAIN = '''
def inner():
    with open("results/x/face.json", "w") as fh:
        fh.write("{}")

def middle():
    return inner()

def outer():
    return middle()
'''

FIXT_DEEP = '''
def a0():
    with open("results/x/face.json", "r") as fh:
        return fh.read()
def a1(): return a0()
def a2(): return a1()
def a3(): return a2()
def a4(): return a3()
def a5(): return a4()
def a6(): return a5()
'''

FIXT_CYCLE = '''
def ping(): return pong()
def pong(): return ping()
'''

FIXT_BARE_ONLY = '''
CAPTION = "results/x/face.json"
def show():
    print("no file here")
'''

FIXT_GIT = '''
import subprocess
def show(path):
    return subprocess.run(["git", "show", "HEAD:" + path], capture_output=True).stdout
def outer(path):
    return show(path)
'''

FIXT_GIT_MENTION = '''
def note():
    """read it with git show later"""
    return "show"
'''


def selftest():
    legs = []

    def leg(name, ok, note=""):
        legs.append((name, bool(ok), note))

    # 1. a helper that opens a file is named, one that does not is not
    ht = helper_table([("fixtures/h.py", FIXT_HELPER_LOAD), ("fixtures/b.py", FIXT_BARE_ONLY)])
    leg("a_load_helper_is_named", ht["helpers"].get("show", {}).get("kind") == KIND_LOAD,
        str(ht["helpers"].keys()))
    # the table is keyed by NAME, so one name defined twice is the union of its definitions -- a
    # bound published by the face, not a silent assumption
    leg("a_name_defined_twice_is_merged",
        ht["helpers"]["show"]["kind"] == KIND_LOAD
        and len(ht["helpers"]["show"]["definitions"]) == 2,
        str(ht["helpers"].get("show")))
    hat = helper_table([("fixtures/b.py", FIXT_BARE_ONLY)])
    leg("a_helper_that_never_opens_is_not_named", not hat["helpers"], str(hat["helpers"]))

    # 2. the table is transitive and records the depth it needed
    ht = helper_table([("fixtures/c.py", FIXT_HELPER_CHAIN)])
    leg("a_child_helper_is_a_dump", ht["helpers"]["inner"]["kind"] == KIND_DUMP)
    leg("a_parent_inherits_by_one_hop",
        ht["helpers"]["middle"]["kind"] == KIND_DUMP and ht["helpers"]["middle"]["depth"] == 2,
        str(ht["helpers"].get("middle")))
    leg("a_grandparent_inherits_by_two_hops",
        ht["helpers"]["outer"]["kind"] == KIND_DUMP and ht["helpers"]["outer"]["depth"] == 3,
        str(ht["helpers"].get("outer")))
    leg("the_chain_names_every_hop",
        ht["helpers"]["outer"]["chain"][0] == "outer"
        and "middle" in ht["helpers"]["outer"]["chain"], str(ht["helpers"]["outer"]["chain"]))

    # 3. the depth bound is a bound, not a suggestion
    ht = helper_table([("fixtures/d.py", FIXT_DEEP)])
    leg("a_chain_within_the_bound_resolves", ht["helpers"].get("a3", {}).get("kind") == KIND_LOAD)
    leg("a_chain_beyond_the_bound_does_not",
        not ht["helpers"].get("a%d" % (MAX_DEPTH + 2), {}).get("kind"))

    # 4. mutual recursion terminates and names nothing
    ht = helper_table([("fixtures/e.py", FIXT_CYCLE)])
    leg("a_cycle_terminates_without_a_kind", not ht["helpers"], str(ht["helpers"]))

    # 5. the git-object arm: a blob read is not a file open, and it propagates
    ht = helper_table([("fixtures/g.py", FIXT_GIT)])
    leg("a_git_show_helper_is_a_git_reader", "show" in ht["git_readers"])
    leg("a_git_reader_is_not_a_file_helper", "show" not in ht["helpers"],
        str(ht["helpers"].keys()))
    leg("a_git_reader_does_not_propagate_by_name",
        "outer" not in ht["git_readers"], str(ht["git_readers"].keys()))
    hgm = helper_table([("fixtures/gm.py", FIXT_GIT_MENTION)])
    leg("a_docstring_mention_is_not_a_git_read", not hgm["git_readers"], str(hgm["git_readers"]))

    # 6. the classifier patch is restored even when the classification raises
    original = e384.classify_call
    try:
        io_map_with_helpers([("fixtures/broken.py", "def f(:\n")], {"show": {"kind": KIND_LOAD}})
        raised = False
    except SyntaxError:
        raised = True
    except Exception:
        raised = True
    leg("the_patch_survives_a_bad_source", e384.classify_call is original and not raised)

    # 6. re-running E384 with the helper names moves exactly the helper site
    src = [("fixtures/h.py", FIXT_HELPER_LOAD)]
    io_base, _p, _f = e384.io_map(src)
    io_ext, _p2, _f2 = io_map_with_helpers(src, {"show": {"kind": KIND_LOAD}})
    line = [n.lineno for n in ast.walk(ast.parse(FIXT_HELPER_LOAD))
            if isinstance(n, ast.Call) and e384.callee_name(n) == "show"][0]
    leg("the_stdlib_table_calls_the_helper_site_other",
        io_base.get(("fixtures/h.py", line)) in (e384.SITE_OTHER, e384.SITE_LOAD),
        str(io_base.get(("fixtures/h.py", line))))
    leg("the_helper_table_makes_it_a_load",
        io_ext.get(("fixtures/h.py", line)) == e384.SITE_LOAD,
        str(io_ext.get(("fixtures/h.py", line))))
    leg("the_classifier_is_restored_after_the_rerun", e384.classify_call is original)

    # 7. key classes move only through the helper arm
    keyed = e383.keyed_sites(src)["keyed"]
    if keyed:
        key, entry = next(iter(keyed.items()))
        before = e384.key_row(key, entry["sites"], io_base)["class"]
        after = e384.key_row(key, entry["sites"], io_ext)["class"]
        leg("a_key_the_helper_opens_moves_class",
            after == e384.CLASS_OPENED, "%s before=%s after=%s" % (key, before, after))

    # 8. the gate is a function of the summary
    leg("decide_no_helper", decide({}) == V_NO_HELPER)
    leg("decide_no_site", decide({"helpers_that_open_a_file": 3}) == V_NO_SITE)
    leg("decide_moved", decide({"helpers_that_open_a_file": 3,
                                "site_lines_the_stdlib_table_could_not_see": 2,
                                "keys_that_move_class": 1}) == V_KEYS_MOVED)
    leg("decide_sites_only", decide({"helpers_that_open_a_file": 3,
                                     "site_lines_the_stdlib_table_could_not_see": 2,
                                     "keys_that_move_class": 0}) == V_SITES_ONLY)

    # 9. own files are named so the face cannot read itself back in
    leg("own_files_named", FACE in OWN_FILES and LATEST in OWN_FILES)

    passed = sum(1 for _, ok, _ in legs if ok)
    for name, ok, note in legs:
        say("  %-46s %s%s" % (name, "PASS" if ok else "FAIL", ("  " + note) if note and not ok else ""))
    say("selftest %d/%d" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "run":
        face = build()
        s = face["summary"]
        say("%d helpers open a file; %d site lines the stdlib table could not see; %d keys move class"
            % (s["helpers_that_open_a_file"], s["site_lines_the_stdlib_table_could_not_see"],
               s["keys_that_move_class"]))
        return 0
    if cmd == "verify":
        return 0 if not verify() else 1
    if cmd == "selftest":
        return selftest()
    say("usage: e401_local_reader.py [run|verify|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))