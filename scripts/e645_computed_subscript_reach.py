"""E645 -- whether a depth-1 store whose subscript is computed can reach a counted row key.

E644 answered E641's blind spot with a literal-only reading and said so in its own limits: 22 of
the 32 depth-1 Store/Del sites in the counted functions subscript with an expression rather than a
string constant, so "no site names a counted row key" is a statement about literal spellings.  A
computed subscript could equal the counted key at run time and no reader of E644's face can see it.

This study prices that residual with two gates that are independent of each other:

  * the KEY GATE -- can the subscript evaluate to a string equal to a counted read key?  Resolved
    by walking the subscript expression back to its binding (loop target over a literal tuple, a
    local assignment over a literal, or module scope) and, when that resolves, publishing the
    finite set of strings it can take.  Three states are distinguished: 'resolved' (a finite set of
    string constants), 'not_a_string_key' (a tuple key, a non-string constant, or a slice -- a
    shape that cannot equal a string row key whatever its value), and 'unresolved'.
  * the CONTAINER GATE -- does the store write into the same object a counted read line reads?
    Name equality against the read receiver, plus one alias step (``x = P`` followed by ``x[k]``),
    because a matching key in a different dict cannot change the value the counted line reads.

Only a site that clears BOTH gates can reach a counted row key; a site that fails the container
gate is excluded structurally, whatever its subscript evaluates to.  The two readings are published
side by side so neither can be dropped when quoting the verdict.

Population is E644's published face (results/state_tilt/ONEDEPTHWRITE.json) -- the computed
subscript sites are selected from it, not re-derived, because a second definition of "depth-1
store in a counted function" would be free to drift from the published one.
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
FACE = "COMPUTEDREACH.json"
LATEST = "computedreach_latest.json"
STUDY = "E645_computed_subscript_reach"
SOURCE_FACE = "results/state_tilt/ONEDEPTHWRITE.json"

import e638_two_depth_subscripts as e638  # noqa: E402
import e640_writeread_collide as e640  # noqa: E402
import e641_writer_receiver as e641  # noqa: E402

DOMAIN_RESOLVED = "resolved"
DOMAIN_NOT_A_STRING_KEY = "not_a_string_key"
DOMAIN_UNRESOLVED = "unresolved"
DOMAIN_STATES = (DOMAIN_RESOLVED, DOMAIN_NOT_A_STRING_KEY, DOMAIN_UNRESOLVED)

CONTAINER_WAY_SAME_NAME = "same_name_as_the_read_receiver"
CONTAINER_WAY_ALIAS = "aliases_the_read_receiver"
CONTAINER_WAY_OTHER = "another_object"
CONTAINER_WAYS = (CONTAINER_WAY_SAME_NAME, CONTAINER_WAY_ALIAS, CONTAINER_WAY_OTHER)

V_NO_COMPUTED_SITE = (
    "no counted function carries a depth-1 store whose subscript is computed, so there is no "
    "residual to price and E644's literal-only reading had no blind spot to disclose")
V_REACHES = (
    "at least one computed-subscript depth-1 store both writes into the container a counted read "
    "line reads and subscripts with an expression whose resolvable value set contains that line's "
    "key, so the counted mapping can be reached by a spelling no literal matcher sees")
V_NO_SITE_WRITES_INTO_THE_READ_CONTAINER = (
    "none of the computed-subscript depth-1 stores writes into the object a counted read line "
    "reads, so a matching key would land in a different dict and cannot change the counted value: "
    "the residual E644 published is closed by container identity, whatever the subscripts evaluate "
    "to")
V_CONTAINER_OPEN_BUT_NO_KEY_IN_DOMAIN = (
    "at least one computed-subscript site writes into the container a counted read line reads, but "
    "every subscript whose value set resolves excludes that line's key, so reaching the counted "
    "mapping needs a spelling the resolved sets rule out")
V_UNDECIDED = (
    "at least one computed-subscript site writes into the container a counted read line reads and "
    "its subscript does not resolve to a finite set of strings, so whether it can spell the counted "
    "key is not decidable from the source")


def say(line):
    sys.stdout.write(line + "\n")


def rel(module, root=ROOT):
    return os.path.relpath(module, root).replace("\\", "/")


# ---------------------------------------------------------------- value domains
def _const_set(value):
    """The finite string set a literal node can take, or None when it is not a set of strings."""
    if isinstance(value, ast.Constant):
        if isinstance(value.value, str):
            return {value.value}
        return None
    if isinstance(value, (ast.Tuple, ast.List, ast.Set)):
        out = set()
        for elt in value.elts:
            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                out.add(elt.value)
            else:
                return None
        return out
    if isinstance(value, ast.Dict):
        out = set()
        for key in value.keys:
            if isinstance(key, ast.Constant) and isinstance(key.value, str):
                out.add(key.value)
            else:
                return None
        return out
    return None


def _iterable_domain(value, fn, tree, index, depth=0):
    """(state, values) for a loop's iterable -- a literal collection of strings resolves."""
    consts = _const_set(value)
    if consts is not None:
        return DOMAIN_RESOLVED, sorted(consts)
    if isinstance(value, ast.Name):
        got = _resolve_name(value.id, fn, tree, index, depth)
        if got is None:
            return DOMAIN_UNRESOLVED, None
        return got
    return DOMAIN_UNRESOLVED, None


def _resolve_name(name, fn, tree, index, depth=0):
    """(state, values) for what the name is bound to inside ``fn`` (module scope as fallback)."""
    if depth > 3:
        return None
    info = index.get(name)
    if not info:
        return None
    kind = info.get("binding")
    if kind == "loop_target":
        for node in e641._scope_nodes(fn):
            if isinstance(node, (ast.For, ast.AsyncFor)) and name in e641._target_names(node.target):
                return _iterable_domain(node.iter, fn, tree, index, depth + 1)
        return None
    if kind in ("local_assignment", "module_scope"):
        pool = list(e641._scope_nodes(fn)) if kind == "local_assignment" else list(tree.body)
        for node in pool:
            if isinstance(node, ast.Assign):
                for tgt in node.targets:
                    if isinstance(tgt, ast.Name) and tgt.id == name:
                        return _iterable_domain(node.value, fn, tree, index, depth + 1)
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) \
                    and node.target.id == name and node.value is not None:
                return _iterable_domain(node.value, fn, tree, index, depth + 1)
        return None
    return None


def _domain_of(value, fn, tree, index, depth=0):
    """(state, sorted values or None) for one subscript expression."""
    if isinstance(value, ast.Slice):
        return DOMAIN_NOT_A_STRING_KEY, None
    if isinstance(value, ast.Tuple):
        return DOMAIN_NOT_A_STRING_KEY, None
    if isinstance(value, ast.List):
        return DOMAIN_NOT_A_STRING_KEY, None
    if isinstance(value, ast.Constant):
        if isinstance(value.value, str):
            return DOMAIN_RESOLVED, [value.value]
        return DOMAIN_NOT_A_STRING_KEY, None
    if isinstance(value, ast.Name):
        got = _resolve_name(value.id, fn, tree, index, depth)
        if got is None:
            return DOMAIN_UNRESOLVED, None
        return got
    # JoinedStr / Call / BinOp / Attribute and everything else: no finite value set from source.
    return DOMAIN_UNRESOLVED, None


# ---------------------------------------------------------------- container identity
def _receiver_aliases(fn, tree, receivers):
    """Local names assigned (directly) from a read receiver inside the same function."""
    out = {}
    for node in e641._scope_nodes(fn):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Name) \
                and node.value.id in receivers:
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id not in receivers:
                    out.setdefault(tgt.id, node.value.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.value, ast.Name) \
                and node.value.id in receivers and isinstance(node.target, ast.Name) \
                and node.target.id not in receivers:
            out.setdefault(node.target.id, node.value.id)
    return out


def container_way(container, receivers, aliases):
    if not container:
        return CONTAINER_WAY_OTHER
    if container in receivers:
        return CONTAINER_WAY_SAME_NAME
    if container in aliases:
        return CONTAINER_WAY_ALIAS
    return CONTAINER_WAY_OTHER


# ---------------------------------------------------------------- measure
def load_source(root=ROOT):
    with io.open(os.path.join(root, SOURCE_FACE), encoding="utf-8") as fh:
        return json.load(fh)


def subscript_node(tree, line, column):
    for node in ast.walk(tree):
        if not isinstance(node, ast.Subscript):
            continue
        if node.lineno != line or node.col_offset != column:
            continue
        if e638.subscript_depth(node) == 1:
            return node
    return None


def measure(root=ROOT, source=None):
    src = source if source is not None else load_source(root)
    out = []
    trees = {}
    for fn in src.get("functions") or []:
        module = (fn.get("module") or "").replace("\\", "/")
        computed = [s for s in (fn.get("depth1_sites") or []) if s.get("has_computed_key")]
        entry = {
            "module": module,
            "function": fn.get("function"),
            "start": fn.get("start"), "end": fn.get("end"),
            "read_receivers": sorted({r.get("receiver") for r in (fn.get("read_lines") or [])
                                      if r.get("receiver")}),
            "read_keys": sorted({r.get("key") for r in (fn.get("read_lines") or [])
                                 if r.get("key")}),
            "computed_write_sites": [],
            "scope_problem": None,
        }
        if not computed:
            out.append(entry)
            continue
        path = os.path.join(root, module)
        if module not in trees:
            trees[module] = e640.tree_of(path)
        tree = trees[module]
        if tree is None:
            entry["scope_problem"] = "does_not_parse"
            out.append(entry)
            continue
        fnode = e641.function_node(tree, {"qualname": entry["function"], "start": entry["start"]})
        if fnode is None:
            entry["scope_problem"] = "function_not_found"
            out.append(entry)
            continue
        index = e641.binding_index(fnode, tree)
        receivers = set(entry["read_receivers"])
        aliases = _receiver_aliases(fnode, tree, receivers)
        for site in sorted(computed, key=lambda s: (s.get("line") or 0, s.get("column") or 0)):
            node = subscript_node(tree, site["line"], site["column"])
            if node is None:
                entry["computed_write_sites"].append({
                    "line": site["line"], "column": site["column"],
                    "container": site.get("container"),
                    "container_way": container_way(site.get("container"), receivers, aliases),
                    "subscript_kind": "not_found",
                    "domain_state": DOMAIN_UNRESOLVED,
                    "domain_values": None,
                    "domain_hits_a_counted_read_key": None,
                    "keys_it_can_spell": [],
                    "reaches_a_counted_row_key": False,
                })
                continue
            state, values = _domain_of(node.slice, fnode, tree, index)
            hits = sorted(set(values) & set(entry["read_keys"])) if values else []
            way = container_way(site.get("container"), receivers, aliases)
            entry["computed_write_sites"].append({
                "line": site["line"], "column": site["column"],
                "container": site.get("container"),
                "container_way": way,
                "subscript_kind": type(node.slice).__name__,
                "domain_state": state,
                "domain_values": values,
                "domain_hits_a_counted_read_key": bool(hits) if state == DOMAIN_RESOLVED else None,
                "keys_it_can_spell": hits,
                "reaches_a_counted_row_key": bool(
                    way != CONTAINER_WAY_OTHER and state == DOMAIN_RESOLVED and hits),
            })
        out.append(entry)
    out.sort(key=lambda e: (e["module"], e["start"] or 0))
    counts = counts_of(out)
    doc = {
        "study": STUDY,
        "date": TODAY,
        "source_face": SOURCE_FACE,
        "method": ("for every depth-1 Store/Del site whose subscript is computed (selected from "
                   "E644's published face), resolve the subscript expression to a finite set of "
                   "string constants where the source allows it, classify the result as resolved / "
                   "not_a_string_key / unresolved, and record whether the store writes into the "
                   "object a counted read line of the same function reads (name equality plus one "
                   "alias step); a site reaches the counted mapping only when both gates open"),
        "population_source": ("%d function(s) machine-read from %s; %d computed-subscript depth-1 "
                              "store site(s) selected from that face's own rows"
                              % (len(out), SOURCE_FACE,
                                 sum(len(f["computed_write_sites"]) for f in out))),
        "counts": counts,
        "functions": out,
        "limits": [
            "'computed' is E644's flag: the site's depth-1 subscript was not a string constant.  A "
            "site whose subscript is a tuple (cell_recs[(cell, face)]) is computed by that "
            "definition and is published here as not_a_string_key, because a tuple key cannot "
            "equal a string row key whatever its elements are",
            "a resolved value set is the set of literal strings the expression can take by "
            "following its binding to a loop target over a literal collection, a local assignment "
            "over a literal, or a module-scope literal, at most three hops; a parameter, a call "
            "result, an attribute or a joined string is published as unresolved, not as empty",
            "the container gate is name equality plus one alias step (x = P; x[k] = v).  It is not "
            "an alias proof: two names can point at one object through a parameter default, a "
            "module global, or a call that returns a shared dict, and none of those are followed",
            "an 'unresolved' domain beside an open container gate is the only state in which this "
            "face cannot answer, and the verdict names that limit rather than folding it into "
            "either answer",
            "the counted read lines and their keys are E644's, which are E640's, not re-derived "
            "here: a second definition of 'counted read line' would be free to drift",
        ],
    }
    doc["verdict"] = decide(counts)
    doc["answer"] = answer_of(counts, out)
    return doc


def counts_of(functions):
    sites = [s for f in functions for s in f["computed_write_sites"]]
    dom_hist = {s: 0 for s in DOMAIN_STATES}
    for site in sites:
        dom_hist[site["domain_state"]] = dom_hist.get(site["domain_state"], 0) + 1
    way_hist = {w: 0 for w in CONTAINER_WAYS}
    for site in sites:
        way_hist[site["container_way"]] = way_hist.get(site["container_way"], 0) + 1
    return {
        "counted_functions": len(functions),
        "counted_functions_with_a_scope_problem": sum(
            1 for f in functions if f.get("scope_problem")),
        "computed_subscript_sites": len(sites),
        "functions_carrying_a_computed_site": sum(
            1 for f in functions if f["computed_write_sites"]),
        "domain_state_histogram": dict(sorted(dom_hist.items())),
        "sites_with_a_resolved_domain": sum(
            1 for s in sites if s["domain_state"] == DOMAIN_RESOLVED),
        "sites_whose_domain_hits_a_counted_read_key": sum(
            1 for s in sites if s.get("domain_hits_a_counted_read_key")),
        "distinct_counted_keys_a_domain_can_spell": len(
            {k for s in sites for k in s.get("keys_it_can_spell") or []}),
        "container_way_histogram": dict(sorted(way_hist.items())),
        "sites_writing_into_the_read_container": sum(
            1 for s in sites if s["container_way"] != CONTAINER_WAY_OTHER),
        "sites_writing_into_an_alias_of_the_read_container": sum(
            1 for s in sites if s["container_way"] == CONTAINER_WAY_ALIAS),
        "sites_reaching_a_counted_row_key": sum(
            1 for s in sites if s.get("reaches_a_counted_row_key")),
        "sites_excluded_by_the_container_gate_alone": sum(
            1 for s in sites
            if s["container_way"] == CONTAINER_WAY_OTHER
            and s["domain_state"] == DOMAIN_UNRESOLVED),
    }


def decide(c):
    if not c.get("computed_subscript_sites"):
        return V_NO_COMPUTED_SITE
    if c.get("sites_reaching_a_counted_row_key"):
        return V_REACHES
    if not c.get("sites_writing_into_the_read_container"):
        return V_NO_SITE_WRITES_INTO_THE_READ_CONTAINER
    if c.get("sites_with_a_resolved_domain") < c.get("computed_subscript_sites") \
            and (c.get("domain_state_histogram") or {}).get(DOMAIN_UNRESOLVED):
        return V_UNDECIDED
    return V_CONTAINER_OPEN_BUT_NO_KEY_IN_DOMAIN


def answer_of(c, functions):
    parts = []
    for f in functions:
        if not f["computed_write_sites"]:
            continue
        spelled = ", ".join(
            "L%s:%s/%s%s" % (
                s["line"], s["subscript_kind"], s["domain_state"],
                ("->" + ",".join(s["keys_it_can_spell"])) if s.get("keys_it_can_spell") else "")
            for s in f["computed_write_sites"])
        parts.append("%s:%s(%d computed site(s), reads %s via %s)"
                     % (f["module"], f["function"], len(f["computed_write_sites"]),
                        ",".join(f["read_keys"]) or "-",
                        ",".join(f["read_receivers"]) or "-"))
    return ("%d computed-subscript depth-1 store(s) in %d of %d counted function(s); domains %s; "
            "containers %s; %d write into the read container (%d through an alias); %d reach a "
            "counted row key; %d are excluded by container identity alone. %s"
            % (c.get("computed_subscript_sites"), c.get("functions_carrying_a_computed_site"),
               c.get("counted_functions"),
               json.dumps(c.get("domain_state_histogram") or {}, sort_keys=True),
               json.dumps(c.get("container_way_histogram") or {}, sort_keys=True),
               c.get("sites_writing_into_the_read_container"),
               c.get("sites_writing_into_an_alias_of_the_read_container"),
               c.get("sites_reaching_a_counted_row_key"),
               c.get("sites_excluded_by_the_container_gate_alone"),
               " | ".join(parts)))


COUNT_KEYS = (
    "counted_functions", "counted_functions_with_a_scope_problem", "computed_subscript_sites",
    "functions_carrying_a_computed_site", "domain_state_histogram",
    "sites_with_a_resolved_domain", "sites_whose_domain_hits_a_counted_read_key",
    "distinct_counted_keys_a_domain_can_spell", "container_way_histogram",
    "sites_writing_into_the_read_container",
    "sites_writing_into_an_alias_of_the_read_container",
    "sites_reaching_a_counted_row_key", "sites_excluded_by_the_container_gate_alone",
)


def face_problems(face):
    problems = []
    if not face:
        return ["face is absent or empty"]
    functions = face.get("functions") or []
    c = face.get("counts") or {}
    live = counts_of(functions)
    for key in COUNT_KEYS:
        if c.get(key) != live.get(key):
            problems.append("counts.%s does not re-add from the functions" % key)
    if decide(live) != face.get("verdict"):
        problems.append("the published verdict is not the one the counts force")
    for f in functions:
        for s in f.get("computed_write_sites") or []:
            if s.get("container_way") not in CONTAINER_WAYS:
                problems.append("%s:%s publishes a container way outside the vocabulary"
                                % (f["module"], f["function"]))
                break
            if s.get("domain_state") not in DOMAIN_STATES:
                problems.append("%s:%s publishes a domain state outside the vocabulary"
                                % (f["module"], f["function"]))
                break
            if s.get("domain_state") == DOMAIN_RESOLVED and not s.get("domain_values"):
                problems.append("%s:%s resolves a domain to no value at all"
                                % (f["module"], f["function"]))
                break
            if s.get("domain_state") != DOMAIN_RESOLVED and s.get("domain_values") is not None:
                problems.append("%s:%s publishes values for a domain it did not resolve"
                                % (f["module"], f["function"]))
                break
            inner = set(s.get("domain_values") or [])
            hits = set(s.get("keys_it_can_spell") or [])
            if not hits <= inner:
                problems.append("%s:%s spells a key its own value set does not carry"
                                % (f["module"], f["function"]))
                break
            if not hits <= set(f.get("read_keys") or []):
                problems.append("%s:%s spells a key no counted read line of its own function reads"
                                % (f["module"], f["function"]))
                break
            expected = bool(s.get("container_way") != CONTAINER_WAY_OTHER
                            and s.get("domain_state") == DOMAIN_RESOLVED and hits)
            if bool(s.get("reaches_a_counted_row_key")) != expected:
                problems.append("%s:%s reaches a counted key while one of the two gates is shut"
                                % (f["module"], f["function"]))
                break
            if f.get("start") is not None and f.get("end") is not None \
                    and not (f["start"] <= (s.get("line") or 0) <= f["end"]):
                problems.append("%s:%s publishes a site outside its own span"
                                % (f["module"], f["function"]))
                break
    if face.get("verdict") == V_REACHES and not c.get("sites_reaching_a_counted_row_key"):
        problems.append("the reaching verdict is not the one its counts force")
    if face.get("verdict") == V_NO_SITE_WRITES_INTO_THE_READ_CONTAINER \
            and c.get("sites_writing_into_the_read_container"):
        problems.append("the container-closed verdict hides a site that writes into the read dict")
    if face.get("verdict") == V_NO_COMPUTED_SITE and c.get("computed_subscript_sites"):
        problems.append("the no-computed-site verdict hides published computed sites")
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
    say("run: functions=%d computed_sites=%d resolved=%d domain_hits=%d in_container=%d "
        "reaches=%d"
        % (c["counted_functions"], c["computed_subscript_sites"], c["sites_with_a_resolved_domain"],
           c["sites_whose_domain_hits_a_counted_read_key"],
           c["sites_writing_into_the_read_container"], c["sites_reaching_a_counted_row_key"]))
    say("run: verdict=" + doc["verdict"])
    say("run: answer=" + doc["answer"])
    return doc


# ---------------------------------------------------------------- selftest
def _fixture_root(files):
    import tempfile
    root = tempfile.mkdtemp(prefix="e645_")
    for name, body in files.items():
        path = os.path.join(root, name)
        os.makedirs(os.path.dirname(path) or root, exist_ok=True)
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)
    return root


def _source(module, function, read_lines, sites, start=1, end=40):
    return {"functions": [{
        "module": module, "function": function, "start": start, "end": end,
        "read_lines": read_lines,
        "depth1_sites": [dict(s, has_computed_key=True) for s in sites],
    }]}


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

    BODY = (
        "def f(P):\n"
        "    days = P['days']\n"
        "    out = {}\n"
        "    for cell in ('a', 'b'):\n"
        "        out[cell] = 1\n"
        "    return out, days\n"
    )

    def _measure(body, read_lines, sites, function="f"):
        root = _fixture_root({"a.py": body})
        return measure(root=root, source=_source("a.py", function, read_lines, sites)), root

    def a_loop_over_a_literal_resolves_to_its_strings():
        doc, _ = _measure(BODY, [{"line": 2, "key": "days", "receiver": "P"}],
                          [{"line": 5, "column": 8, "container": "out"}])
        site = doc["functions"][0]["computed_write_sites"][0]
        assert site["domain_state"] == DOMAIN_RESOLVED, site
        assert site["domain_values"] == ["a", "b"], site
        assert site["keys_it_can_spell"] == [], site

    def a_resolved_domain_names_the_key_it_contains():
        body = BODY.replace("('a', 'b')", "('a', 'days')")
        doc, _ = _measure(body, [{"line": 2, "key": "days", "receiver": "P"}],
                          [{"line": 5, "column": 8, "container": "out"}])
        site = doc["functions"][0]["computed_write_sites"][0]
        assert site["keys_it_can_spell"] == ["days"], site
        assert site["container_way"] == CONTAINER_WAY_OTHER, site
        assert site["reaches_a_counted_row_key"] is False, site

    def a_store_into_the_read_container_with_a_matching_key_reaches():
        body = (
            "def f(P):\n"
            "    days = P['days']\n"
            "    for k in ('days', 'n'):\n"
            "        P[k] = 0\n"
            "    return days\n"
        )
        doc, _ = _measure(body, [{"line": 2, "key": "days", "receiver": "P"}],
                          [{"line": 4, "column": 8, "container": "P"}])
        site = doc["functions"][0]["computed_write_sites"][0]
        assert site["container_way"] == CONTAINER_WAY_SAME_NAME, site
        assert site["keys_it_can_spell"] == ["days"], site
        assert site["reaches_a_counted_row_key"] is True, site
        assert doc["verdict"] == V_REACHES, doc["verdict"]

    def an_alias_of_the_read_container_counts_as_the_same_object():
        body = (
            "def f(P):\n"
            "    days = P['days']\n"
            "    alias = P\n"
            "    for k in ('days',):\n"
            "        alias[k] = 0\n"
            "    return days\n"
        )
        doc, _ = _measure(body, [{"line": 2, "key": "days", "receiver": "P"}],
                          [{"line": 5, "column": 8, "container": "alias"}])
        site = doc["functions"][0]["computed_write_sites"][0]
        assert site["container_way"] == CONTAINER_WAY_ALIAS, site
        assert site["reaches_a_counted_row_key"] is True, site

    def an_unresolved_domain_beside_a_shut_container_is_excluded_structurally():
        body = BODY.replace("('a', 'b')", "argv")
        doc, _ = _measure(body, [{"line": 2, "key": "days", "receiver": "P"}],
                          [{"line": 5, "column": 8, "container": "out"}])
        site = doc["functions"][0]["computed_write_sites"][0]
        assert site["domain_state"] == DOMAIN_UNRESOLVED, site
        assert site["reaches_a_counted_row_key"] is False, site
        assert doc["counts"]["sites_excluded_by_the_container_gate_alone"] == 1, doc["counts"]
        assert doc["verdict"] == V_NO_SITE_WRITES_INTO_THE_READ_CONTAINER, doc["verdict"]

    def an_unresolved_domain_beside_an_open_container_is_undecided():
        body = (
            "def f(P, keys):\n"
            "    days = P['days']\n"
            "    for k in keys:\n"
            "        P[k] = 0\n"
            "    return days\n"
        )
        doc, _ = _measure(body, [{"line": 2, "key": "days", "receiver": "P"}],
                          [{"line": 4, "column": 8, "container": "P"}])
        assert doc["verdict"] == V_UNDECIDED, doc["verdict"]

    def an_open_container_with_every_resolved_domain_excluding_the_key_is_named_separately():
        body = (
            "def f(P):\n"
            "    days = P['days']\n"
            "    for k in ('days_x', 'n'):\n"
            "        P[k] = 0\n"
            "    return days\n"
        )
        doc, _ = _measure(body, [{"line": 2, "key": "days", "receiver": "P"}],
                          [{"line": 4, "column": 8, "container": "P"}])
        assert doc["verdict"] == V_CONTAINER_OPEN_BUT_NO_KEY_IN_DOMAIN, doc["verdict"]

    def a_tuple_subscript_is_not_a_string_key_whatever_its_elements():
        body = (
            "def f(P):\n"
            "    days = P['days']\n"
            "    cells = {}\n"
            "    for cell in ('days',):\n"
            "        cells[(cell, 'x')] = 1\n"
            "    return days\n"
        )
        doc, _ = _measure(body, [{"line": 2, "key": "days", "receiver": "P"}],
                          [{"line": 5, "column": 8, "container": "cells"}])
        site = doc["functions"][0]["computed_write_sites"][0]
        assert site["domain_state"] == DOMAIN_NOT_A_STRING_KEY, site
        assert site["reaches_a_counted_row_key"] is False, site

    def a_non_string_constant_subscript_is_not_a_string_key():
        body = (
            "def f(P):\n"
            "    days = P['days']\n"
            "    row = {}\n"
            "    row[0] = 1\n"
            "    return days\n"
        )
        doc, _ = _measure(body, [{"line": 2, "key": "days", "receiver": "P"}],
                          [{"line": 4, "column": 4, "container": "row"}])
        site = doc["functions"][0]["computed_write_sites"][0]
        assert site["domain_state"] == DOMAIN_NOT_A_STRING_KEY, site

    def a_slice_subscript_is_not_a_key():
        body = (
            "def f(P):\n"
            "    days = P['days']\n"
            "    arr = {}\n"
            "    arr[1:3] = 0\n"
            "    return days\n"
        )
        doc, _ = _measure(body, [{"line": 2, "key": "days", "receiver": "P"}],
                          [{"line": 4, "column": 4, "container": "arr"}])
        site = doc["functions"][0]["computed_write_sites"][0]
        assert site["domain_state"] == DOMAIN_NOT_A_STRING_KEY, site

    def an_empty_population_publishes_the_verdict_it_forces():
        root = _fixture_root({"a.py": "def f():\n    return 1\n"})
        doc = measure(root=root, source=_source("a.py", "f", [], []))
        assert doc["verdict"] == V_NO_COMPUTED_SITE, doc["verdict"]
        assert face_problems(doc) == [], face_problems(doc)

    def the_face_re_adds_and_refuses_a_tampered_row():
        body = (
            "def f(P):\n"
            "    days = P['days']\n"
            "    for k in ('days', 'n'):\n"
            "        P[k] = 0\n"
            "    return days\n"
        )
        doc, _ = _measure(body, [{"line": 2, "key": "days", "receiver": "P"}],
                          [{"line": 4, "column": 8, "container": "P"}])
        assert face_problems(doc) == [], face_problems(doc)
        bad = json.loads(json.dumps(doc))
        bad["counts"]["sites_reaching_a_counted_row_key"] = 0
        assert face_problems(bad), "a tampered count was accepted"
        bad = json.loads(json.dumps(doc))
        bad["functions"][0]["computed_write_sites"][0]["reaches_a_counted_row_key"] = False
        bad["counts"]["sites_reaching_a_counted_row_key"] = 0
        bad["verdict"] = V_NO_SITE_WRITES_INTO_THE_READ_CONTAINER
        assert any("reaches a counted key" in p for p in face_problems(bad)), face_problems(bad)

    def a_tampered_verdict_is_refused():
        doc, _ = _measure(BODY, [{"line": 2, "key": "days", "receiver": "P"}],
                          [{"line": 5, "column": 8, "container": "out"}])
        doc["verdict"] = V_REACHES
        assert any("verdict" in p for p in face_problems(doc)), face_problems(doc)

    for name, fn in [
        ("a loop over a literal resolves to its strings", a_loop_over_a_literal_resolves_to_its_strings),
        ("a resolved domain names the key it contains", a_resolved_domain_names_the_key_it_contains),
        ("a store into the read container with a matching key reaches",
         a_store_into_the_read_container_with_a_matching_key_reaches),
        ("an alias of the read container counts as the same object",
         an_alias_of_the_read_container_counts_as_the_same_object),
        ("an unresolved domain beside a shut container is excluded structurally",
         an_unresolved_domain_beside_a_shut_container_is_excluded_structurally),
        ("an unresolved domain beside an open container is undecided",
         an_unresolved_domain_beside_an_open_container_is_undecided),
        ("an open container with every resolved domain excluding the key is named separately",
         an_open_container_with_every_resolved_domain_excluding_the_key_is_named_separately),
        ("a tuple subscript is not a string key whatever its elements",
         a_tuple_subscript_is_not_a_string_key_whatever_its_elements),
        ("a non-string constant subscript is not a string key",
         a_non_string_constant_subscript_is_not_a_string_key),
        ("a slice subscript is not a key", a_slice_subscript_is_not_a_key),
        ("an empty population publishes the verdict it forces",
         an_empty_population_publishes_the_verdict_it_forces),
        ("the face re-adds and refuses a tampered row",
         the_face_re_adds_and_refuses_a_tampered_row),
        ("a tampered verdict is refused", a_tampered_verdict_is_refused),
    ]:
        leg(name, fn)
    failed = [n for n, ok in legs if not ok]
    say("selftest: %d/%d green" % (len(legs) - len(failed), len(legs)))
    if failed:
        say("selftest: failing legs -> " + "; ".join(failed))
    return 0 if not failed else 1


# ---------------------------------------------------------------- CLI
def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run")
    args = ap.parse_args(argv[1:])
    cmd = args.cmd.lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "check":
        doc = build(root=ROOT)
        problems = face_problems(doc)
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
    doc = build(root=ROOT)
    problems = face_problems(doc)
    if problems:
        say("PROBLEMS: " + "; ".join(problems))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
