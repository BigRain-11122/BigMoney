"""E649 -- which of the residual module-level write sites run behind a module-level guard?

E643 published two numbers side by side: 2,641 two-depth write sites sit in the module body, and
3,237 module-body sites sit inside a module-level compound statement.  It published them as two
independent columns, so a reader can believe both and still not know whether E642's "module-level
write" is an import-time write at all: ``if __name__ == "__main__": P["days"] = x`` runs only when
the file is executed as a script, ``try: ... except ImportError: P[...] = ...`` runs once and may
skip its body, ``for ...: P[...] = ...`` runs zero or more times.

For every two-depth site that (a) has no enclosing function and (b) carries a store/delete at some
depth, this study publishes:

  * the guard region it executes in -- bare module body, main guard, other conditional, loop body,
    with body, try body, except handler, try-else, finally -- and the full chain when they nest,
  * its guard depth (how many regions deep) and whether any main guard is on the chain,
  * the literal key each write member addresses, and whether any of them names one of the counted
    row keys E633's read lines use (derived live from the same join E638/E640 use),
  * the bucket E643 assigned, so a write that is not in the module body is published as such
    instead of being folded into "bare module body",
  * a reconciliation against E643's published residual (machine-read from its face, never
    hand-copied): the difference is named rather than reconciled away.

The population (two-depth site grouping, owner split) is imported from E638/E640 and the bucket
ruler from E643, so this study cannot drift from the definitions it is pricing.
"""
import argparse
import ast
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
FACE = "GUARDEDWRITE.json"
LATEST = "guardedwrite_latest.json"
STUDY = "E649_guarded_module_level_writes"
SELF_PARTS = ("e649_", "run_e649_", "_probe_e649", "_r1670")
SOURCE_FACE = "results/state_tilt/NONFUNCSITE.json"
MAX_BYTES = 1024 * 1024
MAX_EXAMPLES_PER_GUARD = 6

import e391_key_name_two_meanings as e391  # noqa: E402
import e638_two_depth_subscripts as e638  # noqa: E402
import e640_writeread_collide as e640  # noqa: E402
import e643_nonfunc_site as e643  # noqa: E402

BLOCK_NODES = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.With, ast.AsyncWith, ast.Try,
               ast.ExceptHandler)
GUARDS = ("bare_module_body", "main_guard", "conditional", "loop", "with", "try", "try_else",
          "except_handler", "finally", "outside_module_body")
# What the guard says about when the site's statement executes, one line per guard.
IMPORT_TIME = {
    "bare_module_body": "runs_at_import",
    "main_guard": "not_at_import__runs_only_when_the_file_is_the_script",
    "conditional": "runs_at_import_if_the_test_is_true",
    "loop": "runs_at_import_zero_or_more_times",
    "with": "runs_at_import_once_inside_the_context_manager",
    "try": "runs_at_import_unless_an_earlier_statement_raised",
    "try_else": "runs_at_import_only_if_the_try_body_did_not_raise",
    "except_handler": "runs_at_import_only_on_the_matching_exception",
    "finally": "runs_at_import_always",
    "outside_module_body": "not_a_module_body_site__E643_put_it_in_another_context",
}

V_ABSENT = (
    "no_two_depth_site_outside_every_function_carries_a_write,_so_the_population_E642_calls_"
    "module_level_writes_has_no_members_and_the_guard_question_is_moot_at_this_population")
V_ALL_BARE = (
    "every_residual_module_level_write_site_sits_directly_in_the_module_body_at_guard_depth_zero,_"
    "so_all_of_them_execute_at_import_and_E642's_module_level_write_face_is_an_import_time_write_"
    "face")
V_ALL_GUARDED = (
    "every_residual_module_level_write_site_sits_inside_at_least_one_module_level_guard,_so_none_"
    "of_them_is_guaranteed_to_run_at_import_and_module_level_is_a_name_for_code_that_may_never_run")
V_MIXED = (
    "the_residual_splits_between_bare_module_body_sites_that_run_at_import_and_sites_behind_a_"
    "guard,_so_module_level_is_two_execution_faces_and_the_split_is_published_rather_than_"
    "collapsed")


# ---------------------------------------------------------------- helpers
def say(line):
    sys.stdout.write(line + "\n")


def corpus(root=ROOT):
    """The Python corpus E391 walks, minus this study's own files (exclusion by prefix)."""
    out = []
    for p in e391.py_corpus(root):
        if os.path.basename(p).startswith(SELF_PARTS):
            continue
        out.append(p)
    return out


def rel(module, root=ROOT):
    return os.path.relpath(module, root).replace("\\", "/")


def holds(node, line, column):
    """Position containment on (line, column); a node without an end position holds nothing."""
    return e643.holds(node, line, column)


def is_main_guard(test):
    """``__name__ == "__main__"`` (either operand order); everything else is another conditional.

    ``__name__ != "__main__"`` is deliberately NOT a main guard: its body is the import-time half,
    so reading it as "the main block" would invert what the site's guard means.
    """
    if not isinstance(test, ast.Compare) or len(test.ops) != 1:
        return False
    if not isinstance(test.ops[0], (ast.Eq, ast.Is)):
        return False
    pair = (test.left, test.comparators[0])
    for left, right in (pair, (pair[1], pair[0])):
        if (isinstance(left, ast.Name) and left.id == "__name__"
                and isinstance(right, ast.Constant) and right.value == "__main__"):
            return True
    return False


def kind_of(node):
    """The guard a compound statement contributes when it holds the position."""
    if isinstance(node, ast.If):
        return "main_guard" if is_main_guard(node.test) else "conditional"
    if isinstance(node, (ast.For, ast.AsyncFor, ast.While)):
        return "loop"
    if isinstance(node, (ast.With, ast.AsyncWith)):
        return "with"
    if isinstance(node, ast.ExceptHandler):
        return "except_handler"
    return "try"


def block_chain(tree, line, column):
    """Guard regions holding (line, column), outermost first, restricted to module-level code.

    Only statements that hold the position are descended into, so the append order is containment
    order and no sort is needed.  ``try``'s else and finally carry no node of their own, so they are
    published as regions -- ``block_depth`` here counts regions (how many guards the statement sits
    inside), which differs from E643's AST-node depth exactly on those two regions.
    """
    chain = []

    def visit(stmts, region=None):
        if region is not None:
            if not any(holds(st, line, column) for st in stmts if isinstance(st, ast.stmt)):
                return
            chain.append(region)
        for st in stmts:
            if not isinstance(st, (ast.stmt, ast.ExceptHandler)):
                continue
            if not holds(st, line, column):
                continue
            if isinstance(st, BLOCK_NODES):
                chain.append(kind_of(st))
                if isinstance(st, ast.Try):
                    visit(st.body)
                    visit(st.handlers)
                    visit(st.orelse, "try_else")
                    visit(st.finalbody, "finally")
                elif isinstance(st, (ast.If, ast.For, ast.AsyncFor, ast.While)):
                    visit(st.body)
                    visit(st.orelse)
                elif isinstance(st, (ast.With, ast.AsyncWith)):
                    visit(st.body)

    visit(tree.body)
    return chain


def guard_of(bucket, chain):
    if bucket != "module_body":
        return "outside_module_body"
    return chain[-1] if chain else "bare_module_body"


def counted_keys(root=ROOT):
    """The row keys E633's counted read lines use, derived live from the join E638/E640 share."""
    keys = set()
    for row in e638.join_counted_lines(root):
        key = row.get("key")
        if key:
            keys.add(key)
    return sorted(keys)


def write_keys(row):
    """Literal keys addressed by a store/delete member of this site, sorted and de-duplicated."""
    out = set()
    for member in row.get("members") or []:
        if member.get("ctx") in e640.WRITE_CTX and member.get("key"):
            out.add(member["key"])
    return sorted(out)


# ---------------------------------------------------------------- measure
def measure(root=ROOT):
    files = corpus(root)
    holes = {"over_the_size_cap": 0, "unreadable": 0, "does_not_parse": 0}
    keys = counted_keys(root)
    rows = []
    key_hits = []
    examples = {g: [] for g in GUARDS}
    total_sites = 0
    no_owner_total = 0
    for p in files:
        got, why = e638.file_sites(p)
        if got is None:
            holes[why] = holes.get(why, 0) + 1
            continue
        total_sites += len(got["sites"])
        if not got["sites"]:
            continue
        spans = e640.function_spans(p)
        ctx = e643.context_of_file(p)
        if spans is None or ctx is None:
            holes["does_not_parse"] = holes.get("does_not_parse", 0) + 1
            continue
        module = None
        for site in got["sites"]:
            if e640.innermost_owner(spans, site["line"]) is not None:
                continue
            no_owner_total += 1
            row = e640.site_row(site)
            if not row["any_member_is_write"]:
                continue
            if module is None:
                module = rel(p, root)
            bucket = e643.classify(ctx, site["line"], site["column"])["bucket"]
            chain = block_chain(ctx["tree"], site["line"], site["column"]) \
                if bucket == "module_body" else []
            guard = guard_of(bucket, chain)
            matched = sorted(set(write_keys(row)) & set(keys))
            lines = ctx["lines"]
            text = lines[site["line"] - 1].strip()[:160] if 0 < site["line"] <= len(lines) else ""
            out = {
                "module": module,
                "line": site["line"],
                "column": site["column"],
                "guard": guard,
                "chain": chain,
                "guard_depth": len(chain),
                "bucket": bucket,
                "import_time": IMPORT_TIME.get(guard),
                "write_ctx": sorted({m.get("ctx") for m in row["members"]
                                     if m.get("ctx") in e640.WRITE_CTX}),
                "write_keys": write_keys(row),
                "matched_keys": matched,
                "names_a_counted_key": bool(matched),
            }
            rows.append(out)
            if matched:
                key_hits.append({"module": module, "line": site["line"], "guard": guard,
                                 "chain": chain, "write_keys": write_keys(row),
                                 "matched_keys": matched, "source": text})
            bucket_examples = examples[guard]
            if len(bucket_examples) < MAX_EXAMPLES_PER_GUARD:
                bucket_examples.append({"module": module, "line": site["line"],
                                        "chain": chain, "write_keys": write_keys(row),
                                        "source": text})
    rows.sort(key=lambda r: (r["module"], r["line"], r["column"]))
    counts = counts_of(rows, len(files), holes, total_sites, keys, no_owner_total)
    doc = {
        "study": STUDY,
        "date": TODAY,
        "source_face": SOURCE_FACE,
        "method": ("re-parse every .py in the corpus E391 walks, import E638's two-depth site "
                   "grouping and E640's owner split, keep the sites that have no enclosing "
                   "function and carry a store/delete, and for each publish the module-level guard "
                   "region it executes in (bare body / main guard / other conditional / loop / with "
                   "/ try / try-else / except handler / finally), the full nesting chain, the "
                   "bucket E643 assigned, and whether any write member's literal key names one of "
                   "the counted row keys E633's read lines use"),
        "population_source": ("%d Python files of the tree corpus; the population is every "
                              "two-depth write site E640's owner split leaves without a function"
                              % len(files)),
        "counted_keys": keys,
        "counts": counts,
        "rows": rows,
        "key_hits": key_hits,
        "examples": {g: v for g, v in examples.items() if v},
        "limits": [
            "'guard' is the innermost module-level region holding the site's (line, column) and "
            "the chain is published beside it, so a site inside a for-loop inside an if is "
            "conditional>loop rather than a single label",
            "guard_depth counts guard regions, not AST block nodes: try's else and finally carry no "
            "node of their own, so this depth is one larger than E643's module_block_depth exactly "
            "on those two regions",
            "a main guard is only ``__name__ == '__main__'`` (either operand order); "
            "``__name__ != '__main__'`` is published as an ordinary conditional because its body is "
            "the half that runs at import",
            "the execution lines (import_time) are read off the guard kind alone; a loop body may "
            "run zero times, a with body may raise inside the context manager, and a conditional "
            "may be false -- those are named as such rather than resolved by evaluating the test",
            "a write site outside the module body (a class body, a lambda, a comprehension) is "
            "published with guard outside_module_body and is never counted as a bare module body "
            "site",
            "only literal keys can name a counted key; a computed subscript keeps the row but can "
            "never match, so the key column is a lower bound on what the site could address",
            "an augmented assignment (``P['k'] += 1``) is an ast store, so it counts as a write "
            "here exactly as it does in E640",
            "the exclusion list drops only this study's own files, so the E6xx study scripts stay "
            "inside the population and the residual is slightly larger than E643's published 2,641; "
            "the difference is published as delta_vs_source_face with its reason",
            "files over 1MB are skipped rather than parsed (E391's cap) and are counted apart",
        ],
    }
    doc["verdict"] = decide(counts)
    doc["answer"] = answer_of(counts)
    return doc


def live_counts(rows, counted=None):
    """Every headline re-derived from the rows alone, so the gate cannot drift from the face."""
    guard_hist = {}
    chain_hist = {}
    depth_hist = {}
    by_key = {}
    bare = guarded = not_at_import = key_hits = outside = 0
    for row in rows:
        guard = row.get("guard")
        guard_hist[guard] = guard_hist.get(guard, 0) + 1
        chain = row.get("chain") or []
        label = ">".join(chain) or row.get("guard")
        chain_hist[label] = chain_hist.get(label, 0) + 1
        depth = row.get("guard_depth", len(chain))
        depth_hist[str(depth)] = depth_hist.get(str(depth), 0) + 1
        if guard == "bare_module_body":
            bare += 1
        else:
            guarded += 1
        if "main_guard" in chain:
            not_at_import += 1
        if guard == "outside_module_body":
            outside += 1
        if row.get("names_a_counted_key"):
            key_hits += 1
            for key in row.get("matched_keys") or []:
                by_key[key] = by_key.get(key, 0) + 1
    return {
        "residual_write_sites": len(rows),
        "writes_in_bare_module_body": bare,
        "writes_behind_a_guard": guarded,
        "writes_with_a_main_guard_on_the_chain": not_at_import,
        "write_sites_outside_the_module_body": outside,
        "write_sites_naming_a_counted_key": key_hits,
        "write_sites_naming_a_counted_key_by_key": dict(sorted(by_key.items())),
        "guard_histogram": dict(sorted(guard_hist.items())),
        "guard_chain_histogram": dict(sorted(chain_hist.items())),
        "guard_depth_histogram": dict(sorted(depth_hist.items())),
        "guards_measured_with_no_site": [g for g in GUARDS if g not in guard_hist],
    }


def counts_of(rows, files_scanned=0, holes=None, total_sites=None, keys=None,
              sites_without_an_owner_function=0):
    holes = holes or {}
    c = live_counts(rows)
    c["python_files_scanned"] = files_scanned
    c["python_files_over_the_size_cap"] = int(holes.get("over_the_size_cap") or 0)
    c["python_files_unreadable"] = int(holes.get("unreadable") or 0)
    c["python_files_that_do_not_parse"] = int(holes.get("does_not_parse") or 0)
    c["two_depth_sites"] = total_sites if total_sites is not None else None
    c["sites_without_an_owner_function"] = sites_without_an_owner_function
    c["residual_read_only_sites"] = sites_without_an_owner_function - len(rows)
    c["counted_keys"] = list(keys or [])
    source = _source_residual()
    if source:
        c["source_face_no_owner_write_sites"] = source["write_sites_without_an_owner_function"]
        c["delta_vs_source_face"] = c["residual_write_sites"] - \
            source["write_sites_without_an_owner_function"]
        c["source_face_study"] = source["study"]
    return c


def _source_residual(root=ROOT):
    """E643's published residual write count, read from its face -- never hand-copied."""
    try:
        face = json.load(io.open(os.path.join(root, SOURCE_FACE), encoding="utf-8"))
    except (OSError, ValueError):
        return None
    counts = face.get("counts") or {}
    value = counts.get("write_sites_without_an_owner_function")
    if value is None:
        return None
    return {"write_sites_without_an_owner_function": value, "face": SOURCE_FACE,
            "study": face.get("study")}


def decide(c):
    if not c.get("residual_write_sites"):
        return V_ABSENT
    if (c.get("writes_in_bare_module_body") or 0) == (c.get("residual_write_sites") or 0):
        return V_ALL_BARE
    if (c.get("writes_behind_a_guard") or 0) == (c.get("residual_write_sites") or 0):
        return V_ALL_GUARDED
    return V_MIXED


def answer_of(c):
    return ("%d files, %d residual write site(s) with no owner function; guards %s; chains %s; "
            "depth %s; %d bare (run at import) / %d behind a guard / %d with a main guard on the "
            "chain (never at import); %d site(s) name a counted key %s of keys %s; %d site(s) are "
            "not module-body writes at all (delta vs E643's published residual: %s)"
            % (c.get("python_files_scanned"), c.get("residual_write_sites"),
               json.dumps(c.get("guard_histogram") or {}, sort_keys=True),
               json.dumps(c.get("guard_chain_histogram") or {}, sort_keys=True),
               json.dumps(c.get("guard_depth_histogram") or {}, sort_keys=True),
               c.get("writes_in_bare_module_body"), c.get("writes_behind_a_guard"),
               c.get("writes_with_a_main_guard_on_the_chain"),
               c.get("write_sites_naming_a_counted_key"),
               json.dumps(c.get("write_sites_naming_a_counted_key_by_key") or {}, sort_keys=True),
               json.dumps(c.get("counted_keys") or []),
               c.get("write_sites_outside_the_module_body"), c.get("delta_vs_source_face")))


COUNT_KEYS = (
    "residual_write_sites", "writes_in_bare_module_body", "writes_behind_a_guard",
    "writes_with_a_main_guard_on_the_chain", "write_sites_outside_the_module_body",
    "write_sites_naming_a_counted_key", "write_sites_naming_a_counted_key_by_key",
    "guard_histogram", "guard_chain_histogram", "guard_depth_histogram",
    "guards_measured_with_no_site",
)


def face_problems(face):
    """Everything the smoke leg refuses, re-derived from the face's own rows."""
    problems = []
    if not face:
        return ["face is absent or empty"]
    rows = face.get("rows") or []
    c = face.get("counts") or {}
    keys = set(c.get("counted_keys") or [])
    live = live_counts(rows)
    for key in COUNT_KEYS:
        if c.get(key) != live.get(key):
            problems.append("counts.%s does not re-add from the rows" % key)
    if decide(live) != face.get("verdict"):
        problems.append("the published verdict is not the one the rows force")
    if "sites_without_an_owner_function" in c:
        want_read_only = c["sites_without_an_owner_function"] - live["residual_write_sites"]
        if c.get("residual_read_only_sites") != want_read_only:
            problems.append("the read-only residual is not the no-owner residual minus the writes")
    for row in rows:
        chain = row.get("chain") or []
        if row.get("guard") not in GUARDS:
            problems.append("row %s:%s publishes an unknown guard %s"
                            % (row.get("module"), row.get("line"), row.get("guard")))
            break
        if row.get("guard_depth") != len(chain):
            problems.append("row %s:%s has a depth that is not its chain length"
                            % (row.get("module"), row.get("line")))
            break
        if not chain and row.get("guard") not in ("bare_module_body", "outside_module_body"):
            problems.append("row %s:%s has a guard but no chain"
                            % (row.get("module"), row.get("line")))
            break
        if chain and row.get("guard") != chain[-1]:
            problems.append("row %s:%s names a guard that is not the innermost region"
                            % (row.get("module"), row.get("line")))
            break
        if row.get("bucket") != "module_body" and row.get("guard") != "outside_module_body":
            problems.append("row %s:%s is not a module-body site but is guarded as one"
                            % (row.get("module"), row.get("line")))
            break
        if set(row.get("matched_keys") or []) - keys:
            problems.append("row %s:%s matches a key that is not a counted key"
                            % (row.get("module"), row.get("line")))
            break
        if bool(row.get("matched_keys")) != bool(row.get("names_a_counted_key")):
            problems.append("row %s:%s has a key match flag that disagrees with its keys"
                            % (row.get("module"), row.get("line")))
            break
        if row.get("guard") == "main_guard" and not chain:
            problems.append("row %s:%s is a main guard with no chain" % (row.get("module"),
                                                                        row.get("line")))
            break
        if row.get("guard") == "bare_module_body" and chain:
            problems.append("row %s:%s is a bare body with a chain" % (row.get("module"),
                                                                      row.get("line")))
            break
    if face.get("verdict") == V_ABSENT and rows:
        problems.append("the absent verdict is published while rows carry write sites")
    if face.get("verdict") == V_ALL_BARE and (live["writes_behind_a_guard"] or 0) > 0:
        problems.append("the all-bare verdict is published with a guarded site")
    if face.get("verdict") == V_ALL_GUARDED and (live["writes_in_bare_module_body"] or 0) > 0:
        problems.append("the all-guarded verdict is published with a bare site")
    if face.get("verdict") == V_MIXED and (
            live["writes_in_bare_module_body"] == 0 or live["writes_behind_a_guard"] == 0):
        problems.append("the mixed verdict is published while one side is empty")
    if "source_face_no_owner_write_sites" in c:
        if c.get("delta_vs_source_face") != (
                c["residual_write_sites"] - c["source_face_no_owner_write_sites"]):
            problems.append("the delta against the source face is not the difference")
    for guard, block in (face.get("examples") or {}).items():
        if guard not in GUARDS:
            problems.append("examples publish an unknown guard %s" % guard)
            break
    hits = face.get("key_hits") or []
    if len(hits) != (live.get("write_sites_naming_a_counted_key") or 0):
        problems.append("the published key hits are not the rows that name a counted key")
    for hit in hits:
        if not hit.get("matched_keys"):
            problems.append("a published key hit carries no matching key")
            break
        if hit.get("module") is None or hit.get("line") is None:
            problems.append("a published key hit has no address")
            break
    return problems


def write_face(out_dir, doc, face=FACE, latest=LATEST):
    os.makedirs(out_dir, exist_ok=True)
    for name in (face, latest):
        path = os.path.join(out_dir, name)
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
        say("run: %s" % os.path.relpath(path, ROOT))


def build(root=ROOT, out_dir=None):
    doc = measure(root)
    write_face(out_dir or OUTDIR, doc)
    c = doc["counts"]
    say("run: files=%d residual_writes=%d bare=%d guarded=%d main_guard=%d key_hits=%d"
        % (c["python_files_scanned"], c["residual_write_sites"],
           c["writes_in_bare_module_body"], c["writes_behind_a_guard"],
           c["writes_with_a_main_guard_on_the_chain"], c["write_sites_naming_a_counted_key"]))
    say("run: verdict=" + doc["verdict"])
    say("run: answer=" + doc["answer"])
    return doc, []


# ---------------------------------------------------------------- selftest
FIXTURE_SRC = '''\
D = {"a": {"b": 1}, "c": {"d": 2}, "e": {"f": 3}, "g": {"h": 4}, "i": {"j": 5}, "k": {"l": 6}}

D["a"]["b"] = 10
if __name__ == "__main__":
    D["c"]["d"] = 20
if True:
    D["e"]["f"] = 30
for _i in range(3):
    D["g"]["h"] = 40
with open(__file__) as _fh:
    D["i"]["j"] = 50
try:
    D["k"]["l"] = 60
except Exception:
    D["a"]["b"] = 61
else:
    D["c"]["d"] = 62
finally:
    D["e"]["f"] = 63
if True:
    for _i in range(2):
        D["g"]["h"] = 64


class C:
    D["a"]["b"] = 70
'''


def _guard_at(source, needle, nth=0):
    """Guard facts for the nth site whose source line contains ``needle`` (fixtures by text)."""
    ctx, got, spans = e643._fixture_ctx(source)
    hits = [s for s in got["sites"]
            if needle in (ctx["lines"][s["line"] - 1] if s["line"] <= len(ctx["lines"]) else "")]
    site = hits[nth]
    cls = e643.classify(ctx, site["line"], site["column"])
    chain = block_chain(ctx["tree"], site["line"], site["column"]) \
        if cls["bucket"] == "module_body" else []
    return {"guard": guard_of(cls["bucket"], chain), "chain": chain,
            "bucket": cls["bucket"], "depth": len(chain),
            "owner": e640.innermost_owner(spans, site["line"]), "site": site}


def _row(guard, chain=None, matched=(), keys=(), bucket="module_body"):
    chain = list(chain if chain is not None else ([] if guard in (
        "bare_module_body", "outside_module_body") else [guard]))
    return {"module": "a.py", "line": 1, "column": 0, "guard": guard, "chain": chain,
            "guard_depth": len(chain), "bucket": bucket, "import_time": IMPORT_TIME.get(guard),
            "write_ctx": ["store"], "write_keys": list(keys), "matched_keys": list(matched),
            "names_a_counted_key": bool(matched)}


def _sound_face(rows):
    c = live_counts(rows)
    hits = [{"module": r["module"], "line": r["line"], "guard": r["guard"],
             "chain": r["chain"], "write_keys": r["write_keys"],
             "matched_keys": r["matched_keys"], "source": ""}
            for r in rows if r.get("names_a_counted_key")]
    return {"rows": rows, "counts": c, "verdict": decide(c), "examples": {}, "key_hits": hits}


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

    def a_bare_module_site_is_bare():
        got = _guard_at(FIXTURE_SRC, "= 10")
        assert got["owner"] is None, got["owner"]
        assert got["guard"] == "bare_module_body" and got["chain"] == [], got
        assert got["depth"] == 0, got

    def a_main_guard_is_main_guard():
        got = _guard_at(FIXTURE_SRC, "= 20")
        assert got["owner"] is None, got
        assert got["guard"] == "main_guard" and got["chain"] == ["main_guard"], got
        assert IMPORT_TIME[got["guard"]].startswith("not_at_import"), got

    def another_conditional_is_conditional():
        got = _guard_at(FIXTURE_SRC, "= 30")
        assert got["guard"] == "conditional" and got["chain"] == ["conditional"], got

    def a_for_body_is_a_loop():
        got = _guard_at(FIXTURE_SRC, "= 40")
        assert got["guard"] == "loop" and got["chain"] == ["loop"], got

    def a_with_body_is_a_with():
        got = _guard_at(FIXTURE_SRC, "= 50")
        assert got["guard"] == "with" and got["chain"] == ["with"], got

    def a_try_body_is_a_try():
        got = _guard_at(FIXTURE_SRC, "= 60")
        assert got["guard"] == "try" and got["chain"] == ["try"], got

    def an_except_handler_is_its_own_guard():
        got = _guard_at(FIXTURE_SRC, "= 61")
        assert got["guard"] == "except_handler", got
        assert got["chain"] == ["try", "except_handler"], got

    def a_try_else_is_a_region_not_a_node():
        got = _guard_at(FIXTURE_SRC, "= 62")
        assert got["guard"] == "try_else" and got["chain"] == ["try", "try_else"], got

    def a_finally_is_a_region_not_a_node():
        got = _guard_at(FIXTURE_SRC, "= 63")
        assert got["guard"] == "finally" and got["chain"] == ["try", "finally"], got

    def nesting_publishes_the_whole_chain():
        got = _guard_at(FIXTURE_SRC, "= 64")
        assert got["chain"] == ["conditional", "loop"], got
        assert got["guard"] == "loop" and got["depth"] == 2, got

    def a_class_body_site_is_not_a_bare_module_site():
        got = _guard_at(FIXTURE_SRC, "= 70")
        assert got["bucket"] == "class_body", got
        assert got["guard"] == "outside_module_body" and got["chain"] == [], got

    def the_not_equal_main_test_is_not_a_main_guard():
        assert is_main_guard(ast.parse("if __name__ == '__main__':\n    pass\n").body[0].test)
        assert is_main_guard(ast.parse("if '__main__' == __name__:\n    pass\n").body[0].test)
        assert not is_main_guard(ast.parse("if __name__ != '__main__':\n    pass\n").body[0].test)
        assert not is_main_guard(ast.parse("if __name__:\n    pass\n").body[0].test)

    def a_nested_conditional_inside_a_main_guard_is_still_not_import_time():
        rows = [_row("conditional", chain=["main_guard", "conditional"])]
        c = live_counts(rows)
        assert c["writes_with_a_main_guard_on_the_chain"] == 1, c
        assert c["writes_behind_a_guard"] == 1, c

    def live_counts_add_up():
        rows = [_row("bare_module_body"), _row("main_guard"), _row("loop"),
                _row("conditional", chain=["conditional", "loop"]),
                _row("outside_module_body", bucket="class_body")]
        c = live_counts(rows)
        assert c["residual_write_sites"] == 5, c
        assert c["writes_in_bare_module_body"] == 1, c
        assert c["writes_behind_a_guard"] == 4, c
        assert c["write_sites_outside_the_module_body"] == 1, c
        assert c["guard_depth_histogram"] == {"0": 2, "1": 2, "2": 1}, c
        assert c["guard_chain_histogram"]["bare_module_body"] == 1, c
        assert c["guard_chain_histogram"]["outside_module_body"] == 1, c
        assert sum(c["guard_histogram"].values()) == 5, c

    def a_key_match_is_counted_per_key():
        rows = [_row("bare_module_body", matched=["days"], keys=["days"]),
                _row("loop", matched=["days"], keys=["days"]),
                _row("loop", keys=["other"])]
        c = live_counts(rows)
        assert c["write_sites_naming_a_counted_key"] == 2, c
        assert c["write_sites_naming_a_counted_key_by_key"] == {"days": 2}, c

    def all_four_verdicts_are_reachable():
        assert decide({"residual_write_sites": 0}) == V_ABSENT
        assert decide({"residual_write_sites": 2, "writes_in_bare_module_body": 2,
                       "writes_behind_a_guard": 0}) == V_ALL_BARE
        assert decide({"residual_write_sites": 2, "writes_in_bare_module_body": 0,
                       "writes_behind_a_guard": 2}) == V_ALL_GUARDED
        assert decide({"residual_write_sites": 2, "writes_in_bare_module_body": 1,
                       "writes_behind_a_guard": 1}) == V_MIXED

    def face_problems_accepts_a_sound_face():
        rows = [_row("bare_module_body"), _row("main_guard", matched=["days"], keys=["days"])]
        face = _sound_face(rows)
        face["counts"]["counted_keys"] = ["days"]
        assert face_problems(face) == [], face_problems(face)

    def face_problems_catches_a_histogram_that_does_not_add():
        face = _sound_face([_row("bare_module_body")])
        face["counts"]["guard_histogram"] = {"loop": 9}
        assert any("guard_histogram" in p for p in face_problems(face)), face_problems(face)

    def face_problems_catches_a_depth_that_is_not_the_chain():
        face = _sound_face([_row("bare_module_body")])
        face["rows"][0]["guard_depth"] = 3
        assert any("depth" in p for p in face_problems(face)), face_problems(face)

    def face_problems_catches_a_key_match_that_is_not_counted():
        face = _sound_face([_row("bare_module_body", matched=["ghost"], keys=["ghost"])])
        face["counts"]["counted_keys"] = ["days"]
        assert any("not a counted key" in p for p in face_problems(face)), face_problems(face)

    def face_problems_catches_a_wrong_verdict():
        face = _sound_face([_row("bare_module_body"), _row("loop")])
        face["verdict"] = V_ALL_BARE
        assert any("verdict" in p for p in face_problems(face)), face_problems(face)

    def face_problems_catches_key_hits_that_drop_a_matching_row():
        rows = [_row("bare_module_body", matched=["days"], keys=["days"])]
        face = _sound_face(rows)
        face["counts"]["counted_keys"] = ["days"]
        face["key_hits"] = []
        assert any("key hits" in p for p in face_problems(face)), face_problems(face)

    def face_problems_catches_a_delta_that_is_not_the_difference():
        face = _sound_face([_row("bare_module_body")])
        face["counts"]["source_face_no_owner_write_sites"] = 5
        face["counts"]["delta_vs_source_face"] = 99
        assert any("delta" in p for p in face_problems(face)), face_problems(face)

    def answer_names_the_numbers():
        c = live_counts([_row("bare_module_body"), _row("main_guard", matched=["days"],
                                                       keys=["days"])])
        c["python_files_scanned"] = 3
        c["residual_write_sites"] = 2
        a = answer_of(c)
        assert "2 residual write site" in a and "main_guard" in a and "days" in a, a

    for name, fn in [
        ("a_bare_module_site_is_bare", a_bare_module_site_is_bare),
        ("a_main_guard_is_main_guard", a_main_guard_is_main_guard),
        ("another_conditional_is_conditional", another_conditional_is_conditional),
        ("a_for_body_is_a_loop", a_for_body_is_a_loop),
        ("a_with_body_is_a_with", a_with_body_is_a_with),
        ("a_try_body_is_a_try", a_try_body_is_a_try),
        ("an_except_handler_is_its_own_guard", an_except_handler_is_its_own_guard),
        ("a_try_else_is_a_region_not_a_node", a_try_else_is_a_region_not_a_node),
        ("a_finally_is_a_region_not_a_node", a_finally_is_a_region_not_a_node),
        ("nesting_publishes_the_whole_chain", nesting_publishes_the_whole_chain),
        ("a_class_body_site_is_not_a_bare_module_site",
         a_class_body_site_is_not_a_bare_module_site),
        ("the_not_equal_main_test_is_not_a_main_guard",
         the_not_equal_main_test_is_not_a_main_guard),
        ("a_nested_conditional_inside_a_main_guard_is_still_not_import_time",
         a_nested_conditional_inside_a_main_guard_is_still_not_import_time),
        ("live_counts_add_up", live_counts_add_up),
        ("a_key_match_is_counted_per_key", a_key_match_is_counted_per_key),
        ("all_four_verdicts_are_reachable", all_four_verdicts_are_reachable),
        ("face_problems_accepts_a_sound_face", face_problems_accepts_a_sound_face),
        ("face_problems_catches_a_histogram_that_does_not_add",
         face_problems_catches_a_histogram_that_does_not_add),
        ("face_problems_catches_a_depth_that_is_not_the_chain",
         face_problems_catches_a_depth_that_is_not_the_chain),
        ("face_problems_catches_a_key_match_that_is_not_counted",
         face_problems_catches_a_key_match_that_is_not_counted),
        ("face_problems_catches_a_wrong_verdict", face_problems_catches_a_wrong_verdict),
        ("face_problems_catches_key_hits_that_drop_a_matching_row",
         face_problems_catches_key_hits_that_drop_a_matching_row),
        ("face_problems_catches_a_delta_that_is_not_the_difference",
         face_problems_catches_a_delta_that_is_not_the_difference),
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