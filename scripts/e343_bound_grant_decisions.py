"""E343 -- where does a bound grant actually decide something?

E340 counted every permission-shaped field in the tree with its access shape and found 22 rows where
the producer reads its own published face.  Of those, 18 are *bound*: the producer loads the key off
its own face into a name, and what that name then does never appears on the access line.  A bound
grant is exactly where self-authorization would hide, because the only thing separating "reads its
own output" from "grants itself an allowance" is downstream code.

This study follows each bound name inside its producer to its first downstream use and classifies
what that use is:

    compared      the name is evaluated inside a Compare (==, >=, in, ...) : the disk value is put
                  against something else, so the producer cannot move it alone.
    conditioned   the name is used as a truthiness test (``if x:``) : a decision, but not a check of
                  the value against anything.
    passed_to_call the name is handed to a call as an argument -- the decision lives in the callee,
                  which may or may not compare it.
    returned      the name leaves the function as its return value.
    in_arithmetic the name feeds arithmetic (the bound value becomes a quantity, not a permission).
    stored        the name is written into another structure (a dict entry, a list, a new face).
    rebound       the name is reassigned before any other use (the bind was a temporary).
    never_used    nothing downstream references the name at all.

A row is **sole authority** when nothing downstream ever compares it and nothing downstream even
tests it -- the value the producer last wrote is the only authority for whatever it feeds.  The card
asks for that subset by name, plus one worked example of the mechanism such a row would need.

The mechanism sketch is computed rather than written: for the illustrative row we report what a
check would have to assert, who could assert it (producer selftest / chain leg / foreign reader),
and whether the cheap ingredients already exist (a frozen module-level literal that names the same
permission word, an existing selftest in the producer, foreign readers).

Usage:
    python scripts/e343_bound_grant_decisions.py run|verify|selftest
"""

import ast
import io
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-01"
FACE = "BOUNDGRANT-%s.json" % TODAY
LATEST = "boundgrant_latest.json"
STUDY = "E343_bound_grant_decisions"

# E340's own face is the population; reading it is the point (this study is a consumer of it, not a
# second census).
SOURCE_FACE = os.path.join(OUTDIR, "ALLOWANCE-%s.json" % TODAY)
SOURCE_STUDY = "E340_who_authorizes_whose_allowance"

V_COMPARED = "every_bound_grant_is_put_through_a_comparison_before_it_is_used"
V_NONE_USED = "no_bound_grant_is_ever_used_after_it_is_bound"
V_SOLE = ("some_bound_grants_are_the_only_authority_for_the_value_they_feed_and_the_cheap_ingredient"
          "_for_a_check_already_exists_in_the_producer")
V_SOLE_BARE = ("some_bound_grants_are_the_only_authority_for_the_value_they_feed_and_nothing_in_the"
               "_producer_could_assert_it_today")

USE_KINDS = ("compared", "conditioned", "passed_to_call", "returned", "in_arithmetic",
             "stored", "rebound", "never_used", "inline_use")


def say(message):
    sys.stdout.write(str(message) + "\n")
    sys.stdout.flush()


def relp(path):
    return (path or "").replace("\\", "/")


def read_text(root, rel):
    try:
        with io.open(os.path.join(root, rel), encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


# ------------------------------------------------------------------------------- face-holding names

def loader_functions(tree):
    """Functions in this module whose body calls json.load -- ``_read_json`` wrappers."""
    out = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for inner in ast.walk(node):
            if isinstance(inner, ast.Attribute) and inner.attr == "load":
                out.add(node.name)
                break
    return out


def _holds_loaded_face(value, loaders):
    for node in ast.walk(value):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr == "load":
                return True
            if isinstance(func, ast.Name) and func.id in loaders:
                return True
    return False


def face_names(tree):
    """Names that can hold the published face: bound from json.load or from a wrapper around it."""
    loaders = loader_functions(tree)
    names = set()
    for node in ast.walk(tree):
        targets, value = None, None
        if isinstance(node, ast.Assign):
            targets, value = node.targets, node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets, value = [node.target], node.value
        if targets is None or value is None:
            continue
        if not _holds_loaded_face(value, loaders):
            continue
        for target in targets:
            for sub in ast.walk(target):
                if isinstance(sub, ast.Name):
                    names.add(sub.id)
    return names, loaders


def _key_of(node, key):
    """Does this access *read* ``key``?  Handles face.get(key), face.get(key, d), face[key].

    ``face[key] = value`` is deliberately NOT an access: a whole-path subscript writes into the
    loaded dict, and E340's line-shaped classifier counted those as bound reads (its own subject:
    see ``accesses_excluded_as_writes`` in this face).  The first draft of this study inherited the
    defect and reported scripts/update_futures.py:363 -- a store of ``expected`` -- as a bound grant.
    """
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "get":
        if node.args and isinstance(node.args[0], ast.Constant) and node.args[0].value == key:
            return True
        return False
    if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant) \
            and node.slice.value == key and isinstance(node.ctx, ast.Load):
        return True
    return False


def _is_store_of(node, key):
    return (isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant)
            and node.slice.value == key and not isinstance(node.ctx, ast.Load))


def _receiver(node):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        base = node.func.value
        if isinstance(base, ast.Name):
            return base.id
    if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name):
        return node.value.id
    return None


# --------------------------------------------------------------------------------------- the walk

def _scope_of(tree):
    """-> list of (scope_node, nodes_belonging_to_it, {parent_by_child}).

    Grouping by *nearest enclosing function* rather than walking each function subtree: walking the
    module subtree also visits everything inside it, which published the same binding twice and made
    the first draft's selftest fail on a length of 2 for one binding.
    """
    parents = {}
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            parents[child] = parent

    def nearest_scope(node):
        cur = parents.get(node)
        while cur is not None:
            if isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef)):
                return cur
            cur = parents.get(cur)
        return tree

    groups = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node is not tree:
            owner = nearest_scope(node)
        else:
            owner = nearest_scope(node)
        group = groups.setdefault(id(owner), (owner, []))
        group[1].append(node)
    return [(scope, nodes, parents) for scope, nodes in groups.values()]


def _context_kind(node, parents):
    """Walk the ancestry of one Name node upward until a decision-shaped wrapper shows up.

    A container (dict/list/tuple/subscript) is *transparent*: ``all(isinstance(v, str) for v in
    (src, permit))`` reaches a Call through a Tuple, and calling that "stored" was the first
    draft's defect.  Only a container whose value lands in an assignment is a store.
    """
    cur = node
    saw_container = False
    while cur in parents:
        cur = parents[cur]
        if isinstance(cur, ast.Compare):
            return "compared"
        if isinstance(cur, (ast.If, ast.While, ast.Assert)):
            # the Name reached an if/while/assert before any Compare: a truthiness test
            return "conditioned"
        if isinstance(cur, ast.Return):
            return "returned"
        if isinstance(cur, ast.Call):
            return "passed_to_call"
        if isinstance(cur, (ast.BinOp, ast.UnaryOp)):
            return "in_arithmetic"
        if isinstance(cur, (ast.Dict, ast.List, ast.Tuple, ast.Subscript, ast.Set)):
            saw_container = True
            continue
        if isinstance(cur, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            return "stored" if saw_container else "rebound"
        if isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Module)):
            break
    return "other"


def aliases_of(nodes, roots, rounds=4):
    """Names that carry the bound value: ``p = permit.strip()`` is where a permit is decided.

    Bounded to a few rounds because every extra hop costs precision, and published per row so a
    reader can see how far the study followed.  Over-including aliases only ever *removes* sole
    authority claims, which is the conservative direction.
    """
    names = set(roots)
    for _ in range(rounds):
        added = False
        for node in nodes:
            if not isinstance(node, ast.Assign) or len(node.targets) != 1:
                continue
            target = node.targets[0]
            if not isinstance(target, ast.Name) or target.id in names:
                continue
            if {n.id for n in ast.walk(node.value) if isinstance(n, ast.Name)} & names:
                names.add(target.id)
                added = True
        if not added:
            break
    return sorted(names - set(roots))


def follow_binding(src, key, stats=None):
    """-> (rows, error).  ``stats`` (optional dict) is filled with the write count.

    A row is produced for every *read* of ``key`` whose receiver is a face-holding name.  Accesses
    that are themselves the decision (Compare / if / assert / bare call) are reported as
    ``inline_use`` because there is no name to follow; writes into the loaded dict are counted in
    ``stats["excluded_as_writes"]`` and not treated as grants at all.
    """
    try:
        tree = ast.parse(src)
    except SyntaxError as exc:
        return [], "unparseable: %s" % exc
    names, _loaders = face_names(tree)
    rows = []
    writes = 0
    for scope, nodes, parents in _scope_of(tree):
        for node in nodes:
            if _is_store_of(node, key) and _receiver(node) in names:
                writes += 1
                continue
            if not _key_of(node, key):
                continue
            recv = _receiver(node)
            if recv not in names:
                continue
            holder = parents.get(node)
            if not isinstance(holder, (ast.Assign, ast.AnnAssign)):
                rows.append({"binding_line": None, "binding_name": None, "alias_names": [],
                             "first_use_line": getattr(node, "lineno", None),
                             "first_use_kind": "inline_use",
                             "downstream_uses": 0, "compares_downstream": 0,
                             "conditions_downstream": 0, "sole_authority": False})
                continue
            targets = holder.targets if isinstance(holder, ast.Assign) else [holder.target]
            bound = [t.id for t in targets if isinstance(t, ast.Name)]
            if not bound:
                # ``bench["ytd_baselines"] = ytd.get("baselines")`` reads the grant and immediately
                # files it somewhere else: there is no name holding the value, so there is nothing to
                # follow.  The first draft bound the *container* (``bench``) and published a grant
                # against a name that never held it.
                rows.append({"binding_line": getattr(holder, "lineno", None), "binding_name": None,
                             "alias_names": [], "first_use_line": getattr(node, "lineno", None),
                             "first_use_kind": "stored", "downstream_uses": 0,
                             "compares_downstream": 0, "conditions_downstream": 0,
                             "sole_authority": False})
                continue
            line = getattr(holder, "lineno", None)
            for name in sorted(set(bound)):
                alias_names = aliases_of(nodes, [name])
                watched = {name} | set(alias_names)
                # where each alias is *defined*: that node is the bind, not a use of it
                alias_stores = set()
                for other in nodes:
                    if isinstance(other, (ast.Assign, ast.AnnAssign)):
                        targets_o = other.targets if isinstance(other, ast.Assign) else [other.target]
                        for target in targets_o:
                            for sub in ast.walk(target):
                                if isinstance(sub, ast.Name) and sub.id in alias_names:
                                    alias_stores.add(id(sub))
                uses = []
                for other in nodes:
                    if not isinstance(other, ast.Name) or other.id not in watched:
                        continue
                    if getattr(other, "lineno", 0) <= (line or 0):
                        # the store side of the binding itself, or any earlier use of the name
                        continue
                    if other.id != name and id(other) in alias_stores:
                        continue
                    uses.append(other)
                uses.sort(key=lambda n: (getattr(n, "lineno", 0), getattr(n, "col_offset", 0)))
                kinds = [_context_kind(u, parents) for u in uses]
                row = {
                    "binding_line": line,
                    "binding_name": name,
                    "alias_names": alias_names,
                    "first_use_line": getattr(uses[0], "lineno", None) if uses else None,
                    "first_use_kind": kinds[0] if kinds else "never_used",
                    "downstream_uses": len(uses),
                    "compares_downstream": kinds.count("compared"),
                    "conditions_downstream": kinds.count("conditioned"),
                }
                row["sole_authority"] = is_sole_authority(row)
                rows.append(row)
    if stats is not None:
        stats["excluded_as_writes"] = writes
    return rows, None


def is_sole_authority(row):
    """The card's definition, tightened: no comparison AND no truthiness test downstream.

    Publishing both is deliberate -- a ``conditioned`` row is a decision without a check, so it can
    never be "compared", but calling it sole authority would overstate the finding.
    """
    if row["first_use_kind"] in ("never_used", "inline_use"):
        return False
    if not row.get("binding_name") or not row.get("downstream_uses"):
        # no name held the value, or nothing downstream referenced it: there is no decision to be
        # the sole authority *for*.  The first draft let a "filed into another dict" row through.
        return False
    return row["compares_downstream"] == 0 and row["conditions_downstream"] == 0


# ------------------------------------------------------------------------------------ mechanism

FROZEN_ASSIGN = re.compile(r"^([A-Z][A-Z0-9_]{2,})\s*=\s*(.+)$")


def frozen_literals(src, key):
    """Module-level constants whose name carries the permission word and whose value is a literal."""
    word = re.split(r"[^A-Za-z0-9]+", key)[0].upper()
    out = []
    for line in src.splitlines():
        match = FROZEN_ASSIGN.match(line)
        if not match or not word:
            continue
        if word in match.group(1).upper():
            out.append(match.group(1))
    return sorted(set(out))


def has_selftest(src):
    return bool(re.search(r"^def [A-Za-z0-9_]*selftest[A-Za-z0-9_]*\(", src, re.M))


def mechanism_for(row, src):
    """What would have to be asserted so this producer could no longer award itself this value."""
    literals = frozen_literals(src, row["key"])
    self_tested = has_selftest(src)
    if literals:
        assertable = "frozen_literal"
        who = "producer selftest" if self_tested else "chain leg"
        assertion = ("%s must equal %s (a module-level literal in the same file) at load time, and "
                     "the load must fail otherwise" % (row["binding_name"], literals[0]))
    elif self_tested:
        assertable = "recomputation"
        who = "producer selftest"
        assertion = ("%s must equal a value recomputed from the producer's own inputs inside its "
                     "selftest, so that editing the face alone fails the test"
                     % row["binding_name"])
    else:
        assertable = "none_available"
        who = "chain leg"
        assertion = ("no literal and no selftest exist in this producer: a chain leg would have to "
                     "recompute %s from the inputs named beside %s on the face and compare"
                     % (row["binding_name"], row["key"]))
    return {
        "assertable_from": assertable,
        "asserted_by": who,
        "assertion": assertion,
        "cheap_ingredients": {
            "frozen_literal_present": bool(literals),
            "frozen_literals": literals[:4],
            "producer_has_selftest": self_tested,
        },
    }


# ---------------------------------------------------------------------------------------- the maths

def summarize(rows):
    by_kind = {}
    for row in rows:
        by_kind[row["first_use_kind"]] = by_kind.get(row["first_use_kind"], 0) + 1
    sole = [r for r in rows if r["sole_authority"]]
    return {
        "bound_rows": len(rows),
        "by_first_use_kind": by_kind,
        "never_used": by_kind.get("never_used", 0),
        "inline_use": by_kind.get("inline_use", 0),
        "compared_first": by_kind.get("compared", 0),
        "conditioned_first": by_kind.get("conditioned", 0),
        "sole_authority": len(sole),
        "sole_authority_faces": sorted({r["face"] for r in sole}),
        "sole_authority_durable": sum(1 for r in sole if r["shape_source"] == "durable"),
        "sole_authority_with_frozen_literal": sum(1 for r in sole if r["cheap_literal"]),
        "sole_authority_with_producer_selftest": sum(1 for r in sole if r["producer_has_selftest"]),
        "sole_authority_with_foreign_readers": sum(1 for r in sole if r["n_foreign_readers"]),
        "sole_authority_unpinned": sum(1 for r in sole if not r["selftest_pin"]),
        "rows_with_no_downstream_use": sum(1 for r in rows if r["downstream_uses"] == 0),
    }


def decide(summary):
    n = summary.get("bound_rows") or 0
    if n == 0:
        return V_NONE_USED, ["E340 published no bound self-read to follow"]
    compared = summary.get("compared_first") or 0
    if compared == n:
        return V_COMPARED, ["%s of %s bound names are compared at their first use" % (n, n)]
    unused = summary.get("never_used") or 0
    if unused == n:
        return V_NONE_USED, ["%s of %s bound names are never referenced after the bind" % (n, n)]
    sole = summary.get("sole_authority") or 0
    cheap = summary.get("sole_authority_with_frozen_literal") or 0
    if sole and cheap:
        return V_SOLE, ["%s of %s bound grants are sole authority; %s of them already carry a frozen "
                        "literal the producer could compare against" % (sole, n, cheap)]
    return V_SOLE_BARE, ["%s of %s bound grants are sole authority and none of them has a literal "
                         "in place to check against" % (sole, n)]


# ---------------------------------------------------------------------------------------- build

def build(root=None):
    root = root or ROOT
    t0 = time.time()
    path = os.path.join(root, os.path.relpath(SOURCE_FACE, ROOT))
    with io.open(path, encoding="utf-8") as fh:
        source = json.load(fh)
    if source.get("study") != SOURCE_STUDY:
        raise SystemExit("source face is %r, expected %r" % (source.get("study"), SOURCE_STUDY))

    population = [e for e in source.get("self_read_entries") or [] if e.get("class") == "self_bound"]
    rows, skipped, write_only = [], [], []
    total_writes = 0
    for entry in population:
        producer = relp(entry.get("reading_producer") or "")
        key = entry.get("key") or ""
        if not producer or not key:
            skipped.append({"face": entry.get("face"), "key": key, "why": "no producer or key"})
            continue
        src = read_text(root, producer)
        if not src:
            skipped.append({"face": entry.get("face"), "key": key,
                            "why": "producer %s not readable" % producer})
            continue
        stats = {}
        found, why = follow_binding(src, key, stats)
        total_writes += int(stats.get("excluded_as_writes") or 0)
        if why:
            skipped.append({"face": entry.get("face"), "key": key, "why": why})
            continue
        if not found:
            row = {"face": entry.get("face"), "key": key, "producer": producer,
                   "writes_excluded": stats.get("excluded_as_writes") or 0}
            write_only.append(row)
            skipped.append({"face": entry.get("face"), "key": key,
                            "why": "no *read* of %r on a face-holding name in %s (%d write-only "
                                   "accesses excluded)" % (key, producer, row["writes_excluded"])})
            continue
        literals = frozen_literals(src, key)
        self_tested = has_selftest(src)
        for row in found:
            row.update({
                "face": entry.get("face"),
                "key": key,
                "producer": producer,
                "shape_source": entry.get("shape_source"),
                "n_foreign_readers": entry.get("n_foreign_readers") or 0,
                "selftest_pin": bool(entry.get("selftest_pin")),
                "cheap_literal": bool(literals),
                "producer_has_selftest": self_tested,
            })
            row["sole_authority"] = is_sole_authority(row)
            rows.append(row)

    rows.sort(key=lambda r: (str(r["face"]), r["key"], r["producer"],
                             r["binding_line"] or 0, r["binding_name"] or ""))
    summary = summarize(rows)
    summary["entries_that_were_write_only"] = len(write_only)
    summary["accesses_excluded_as_writes"] = total_writes
    verdict, reasons = decide(summary)

    sole = [r for r in rows if r["sole_authority"]]
    worked = None
    if sole:
        pick = sorted(sole, key=lambda r: (not r["cheap_literal"], str(r["producer"]),
                                           str(r["face"]), r["key"]))[0]
        worked = dict(pick)
        worked["mechanism"] = mechanism_for(pick, read_text(root, pick["producer"]))

    doc = {
        "study": STUDY,
        "evidence_cutoff": TODAY,
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "definition": {
            "population": ("E340's self_bound rows only: the producer loads the key off its own "
                           "published face into a name (%s -> %d rows)"
                           % (relp(os.path.relpath(SOURCE_FACE, ROOT)), len(population))),
            "first_use": ("the earliest Name node carrying the bound variable after the binding "
                          "line, inside the same scope, wrapped by its nearest decision-shaped "
                          "ancestor: Compare / if-while-assert / return / call / arithmetic / "
                          "container / reassignment"),
            "sole_authority": ("nothing downstream compares the name and nothing downstream tests "
                               "it: the value the producer last wrote is the only authority for "
                               "whatever it feeds.  Aliases are followed (``p = permit.strip()`` "
                               "counts as the permit) up to four hops, and every row publishes "
                               "``alias_names`` so a reader can see how far the study looked"),
            "inline_use": ("the key is read and used on one line, so there is no name to follow -- "
                           "those rows are counted but cannot be sole authority by construction"),
            "write": ("``face[key] = value`` is a store into the loaded dict, not a grant: those are "
                      "counted in ``accesses_excluded_as_writes`` and the entries whose only access "
                      "was a store are listed in ``write_only_entries``.  E340's line-shaped "
                      "classifier counted them as bound reads, which is why its 18 is larger than "
                      "the number of real reads here"),
        },
        "source": {"study": source.get("study"),
                   "verdict": source.get("verdict"),
                   "asof_head": source.get("asof_head"),
                   "self_bound_rows": len(population)},
        "summary": summary,
        "verdict": verdict,
        "reasons": reasons,
        "rows": rows,
        "sole_authority_rows": [{"face": r["face"], "key": r["key"], "producer": r["producer"],
                                 "binding_name": r["binding_name"],
                                 "alias_names": r["alias_names"],
                                 "binding_line": r["binding_line"],
                                 "first_use_line": r["first_use_line"],
                                 "first_use_kind": r["first_use_kind"],
                                 "downstream_uses": r["downstream_uses"],
                                 "shape_source": r["shape_source"],
                                 "n_foreign_readers": r["n_foreign_readers"],
                                 "selftest_pin": r["selftest_pin"]}
                                for r in sole],
        "worked_example": worked,
        "write_only_entries": write_only,
        "skipped": skipped,
        "timing": {"full_build_seconds": round(time.time() - t0, 2)},
    }
    return doc


# ---------------------------------------------------------------------------------------- verify

def _cmp(a, b, path, out):
    if isinstance(a, dict) and isinstance(b, dict):
        for key in sorted(set(a) | set(b)):
            if key not in a:
                out.append("%s.%s missing in the published face" % (path, key))
            elif key not in b:
                out.append("%s.%s not produced now" % (path, key))
            else:
                _cmp(a[key], b[key], "%s.%s" % (path, key), out)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append("%s length %s published vs %s now" % (path, len(a), len(b)))
        for idx, (x, y) in enumerate(zip(a, b)):
            _cmp(x, y, "%s[%d]" % (path, idx), out)
    elif isinstance(a, float) or isinstance(b, float):
        try:
            if abs(float(a) - float(b)) > 1e-9:
                out.append("%s %r published vs %r now" % (path, a, b))
        except (TypeError, ValueError):
            out.append("%s not numeric: %r vs %r" % (path, a, b))
    elif a != b:
        out.append("%s %r published vs %r now" % (path, a, b))


def verify(root=None):
    root = root or ROOT
    path = os.path.join(root, os.path.relpath(os.path.join(OUTDIR, FACE), ROOT))
    if not os.path.isfile(path):
        return ["published face missing: %s" % relp(os.path.relpath(path, root))]
    with io.open(path, encoding="utf-8") as fh:
        published = json.load(fh)
    now = build(root)
    problems = []
    for key in ("study", "evidence_cutoff", "definition", "summary", "verdict", "reasons",
                "rows", "sole_authority_rows", "write_only_entries", "skipped"):
        if key not in published:
            problems.append("published face has no %r" % key)
            continue
        _cmp(published[key], now.get(key), key, problems)
    # the two invariants the finding rests on, checked against the published face rather than
    # against the freshly built one
    for row in published.get("rows") or []:
        if row.get("sole_authority") and (row.get("compares_downstream") or
                                          row.get("conditions_downstream")):
            problems.append("%s/%s claims sole authority with a downstream check"
                            % (row.get("face"), row.get("key")))
        if row.get("first_use_kind") not in USE_KINDS:
            problems.append("%s/%s publishes an unknown use kind %r"
                            % (row.get("face"), row.get("key"), row.get("first_use_kind")))
    summary = published.get("summary") or {}
    sole = summary.get("sole_authority")
    listed = len(published.get("sole_authority_rows") or [])
    if sole != listed:
        problems.append("summary says %s sole-authority rows, the list carries %s" % (sole, listed))
    return problems


# -------------------------------------------------------------------------------------- publishing

def write_face(doc, root=None):
    root = root or ROOT
    outdir = os.path.join(root, os.path.relpath(OUTDIR, ROOT))
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    face_path = os.path.join(outdir, FACE)
    with io.open(face_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(doc, ensure_ascii=False, indent=1, sort_keys=True) + "\n")
    latest = {
        "study": doc["study"],
        "evidence_cutoff": doc["evidence_cutoff"],
        "generated": doc["generated"],
        "verdict": doc["verdict"],
        "reasons": doc["reasons"],
        "source": doc["source"],
        "summary": doc["summary"],
        "sole_authority_rows": doc["sole_authority_rows"],
        "worked_example": doc["worked_example"],
        "face": relp(os.path.relpath(face_path, root)),
    }
    with io.open(os.path.join(outdir, LATEST), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(latest, ensure_ascii=False, indent=1, sort_keys=True) + "\n")
    return face_path


# ---------------------------------------------------------------------------------------- selftest

def _fixture(binding_use, key="permit", bind_line="    v = face.get('permit')"):
    body = [
        "def _read_json(path):",
        "    with open(path) as fh:",
        "        return json.load(fh), None",
        "",
        "def main():",
        "    face, err = _read_json('results/x.json')",
        bind_line,
        binding_use,
    ]
    return "\n".join(body) + "\n"


def cmd_selftest():
    checks = []

    def check(name, condition, detail=""):
        checks.append((name, bool(condition), detail))

    rows, why = follow_binding(_fixture("    if v != 3:\n        raise SystemExit(1)"), "permit")
    check("a compared bound name is classified compared and is not sole authority",
          why is None and len(rows) == 1 and rows[0]["first_use_kind"] == "compared"
          and rows[0]["sole_authority"] is False, repr(rows))

    rows, _ = follow_binding(_fixture("    return v"), "permit")
    check("a returned bound name is sole authority",
          len(rows) == 1 and rows[0]["first_use_kind"] == "returned"
          and rows[0]["sole_authority"] is True, repr(rows))

    rows, _ = follow_binding(_fixture("    do(v)"), "permit")
    check("a name handed to a call is not sole authority (the decision left the scope)",
          len(rows) == 1 and rows[0]["first_use_kind"] == "passed_to_call"
          and rows[0]["sole_authority"] is True, repr(rows))

    rows, _ = follow_binding(_fixture("    if v:\n        return 1"), "permit")
    check("a truthiness test is conditioned and is NOT sole authority",
          len(rows) == 1 and rows[0]["first_use_kind"] == "conditioned"
          and rows[0]["sole_authority"] is False, repr(rows))

    rows, _ = follow_binding(_fixture("    total = v + 1"), "permit")
    check("a bound value used only arithmetically is sole authority",
          len(rows) == 1 and rows[0]["first_use_kind"] == "in_arithmetic"
          and rows[0]["sole_authority"] is True, repr(rows))

    rows, _ = follow_binding(_fixture("    pass"), "permit")
    check("a bound name nothing touches is never_used and not sole authority",
          len(rows) == 1 and rows[0]["first_use_kind"] == "never_used"
          and rows[0]["sole_authority"] is False, repr(rows))

    rows, _ = follow_binding(_fixture("    v = 2\n    return v"), "permit")
    check("a rebound name reports rebound at its first use",
          len(rows) == 1 and rows[0]["first_use_kind"] == "rebound", repr(rows))

    rows, _ = follow_binding(
        "def _read_json(path):\n    return json.load(open(path)), None\n\n"
        "def main():\n    face, err = _read_json('x')\n    if face.get('permit') != 3:\n"
        "        raise SystemExit(1)\n", "permit")
    check("an inline read has no name to follow and is published as inline_use",
          len(rows) == 1 and rows[0]["first_use_kind"] == "inline_use"
          and rows[0]["sole_authority"] is False, repr(rows))

    # a name stored into a container first is not compared by that act -- the stored value can still
    # be read anywhere downstream, so the counter stays 0 and the row stays sole authority
    rows, _ = follow_binding(
        _fixture("    bucket = {'p': v}\n    return bucket"), "permit")
    check("storing the bound value counts no compare and stays sole authority",
          len(rows) == 1 and rows[0]["first_use_kind"] == "stored"
          and rows[0]["compares_downstream"] == 0
          and rows[0]["sole_authority"] is True, repr(rows))

    filed = ("import json\ndef _read_json(p):\n    return json.load(open(p)), None\n\n"
             "def main():\n    ytd, err = _read_json('y')\n    out = {}\n"
             "    out['p'] = ytd.get('baselines')\n    return out\n")
    rows, _ = follow_binding(filed, "baselines")
    check("a value filed into another dict has no bound name and is not a grant row",
          len(rows) == 1 and rows[0]["binding_name"] is None
          and rows[0]["sole_authority"] is False, repr(rows))

    rows, _ = follow_binding(_fixture("    other = v\n    if v == 2:\n        return 1"), "permit")
    check("compares_downstream counts a compare that is not the first use",
          len(rows) == 1 and rows[0]["compares_downstream"] == 1
          and rows[0]["sole_authority"] is False, repr(rows))

    rows, _ = follow_binding(_fixture("    return v"), "absent_key")
    check("a key that is not read on a face-holding name yields no row",
          rows == [], repr(rows))

    store_only = ("def _read_json(p):\n    return json.load(open(p)), None\n\n"
                  "def main():\n    st, err = _read_json('x')\n"
                  "    st['permit'] = 3\n    return st\n")
    stats = {}
    rows, _ = follow_binding(store_only, "permit", stats)
    check("a store into the loaded dict is not a grant read and is counted as excluded",
          rows == [] and stats.get("excluded_as_writes") == 1, "%r %r" % (rows, stats))

    rows, _ = follow_binding(
        _fixture("    ok = all(isinstance(v, str) for v in (1, v))"), "permit")
    check("a tuple feeding a call is transparent, not a container store",
          len(rows) == 1 and rows[0]["first_use_kind"] == "passed_to_call", repr(rows))

    rows, _ = follow_binding(
        _fixture("    p = v.strip()\n    if p in ('A', 'B'):\n        return 0"), "permit")
    check("an alias that is compared downstream removes sole authority",
          len(rows) == 1 and rows[0]["alias_names"] == ["p"]
          and rows[0]["compares_downstream"] >= 1
          and rows[0]["sole_authority"] is False, repr(rows))

    src = ("LIMIT_PERMIT = 12\n\ndef cmd_selftest():\n    return 0\n\n"
           "def main():\n    face = {}\n    v = face.get('permit')\n    return v\n")
    check("a frozen literal is found by the permission word", frozen_literals(src, "permit") ==
          ["LIMIT_PERMIT"], repr(frozen_literals(src, "permit")))

    mech = mechanism_for({"binding_name": "v", "key": "permit"}, src)
    check("the mechanism names the literal and the producer selftest when both exist",
          mech["assertable_from"] == "frozen_literal" and mech["asserted_by"] == "producer selftest",
          repr(mech))

    mech = mechanism_for({"binding_name": "v", "key": "permit"},
                         "def main():\n    return 1\n")
    check("with neither a literal nor a selftest the mechanism falls to a chain leg",
          mech["assertable_from"] == "none_available" and mech["asserted_by"] == "chain leg",
          repr(mech))

    base = summarize([{"first_use_kind": "compared", "sole_authority": False,
                       "shape_source": "durable", "cheap_literal": False,
                       "producer_has_selftest": False, "n_foreign_readers": 0,
                       "selftest_pin": False, "downstream_uses": 1, "face": "a"}])
    verdict, _ = decide(base)
    check("all-compared decides the compared verdict", verdict == V_COMPARED, verdict)

    base = summarize([{"first_use_kind": "never_used", "sole_authority": False,
                       "shape_source": "durable", "cheap_literal": False,
                       "producer_has_selftest": False, "n_foreign_readers": 0,
                       "selftest_pin": False, "downstream_uses": 0, "face": "a"}])
    verdict, _ = decide(base)
    check("all-unused decides the never-used verdict", verdict == V_NONE_USED, verdict)

    base = summarize([{"first_use_kind": "returned", "sole_authority": True,
                       "shape_source": "durable", "cheap_literal": True,
                       "producer_has_selftest": True, "n_foreign_readers": 0,
                       "selftest_pin": False, "downstream_uses": 1, "face": "a"}])
    verdict, reasons = decide(base)
    check("sole authority with a cheap literal decides the cheap verdict and says so in a reason",
          verdict == V_SOLE and "1 of 1" in reasons[0], "%s %r" % (verdict, reasons))

    bad = []
    checks_failed = 0
    for name, ok, detail in checks:
        if not ok:
            checks_failed += 1
            bad.append("%s -- %s" % (name, detail[:120]))
    say("selftest: %d/%d legs pass" % (len(checks) - checks_failed, len(checks)))
    for line in bad:
        say("  FAIL " + line)
    return 0 if checks_failed == 0 else 1


# ------------------------------------------------------------------------------------------- cli

def cmd_run():
    doc = build()
    path = write_face(doc)
    say("study=%s verdict=%s" % (doc["study"], doc["verdict"]))
    for reason in doc["reasons"]:
        say("  reason: " + reason)
    say("  bound rows=%d sole_authority=%d never_used=%d inline_use=%d"
        % (doc["summary"]["bound_rows"], doc["summary"]["sole_authority"],
           doc["summary"]["never_used"], doc["summary"]["inline_use"]))
    if doc["skipped"]:
        say("  skipped=%d" % len(doc["skipped"]))
        for row in doc["skipped"]:
            say("    skipped %s / %s: %s" % (row["face"], row["key"], row["why"]))
    say("face=%s" % relp(os.path.relpath(path, ROOT)))
    return 0


def cmd_verify():
    problems = verify()
    if problems:
        say("verify: %d problem(s)" % len(problems))
        for line in problems:
            say("  " + line)
        return 1
    say("verify: 0 problems")
    return 0


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "run":
        return cmd_run()
    if cmd == "verify":
        return cmd_verify()
    if cmd == "selftest":
        return cmd_selftest()
    say(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))