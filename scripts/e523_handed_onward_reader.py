"""E523 -- who reads the result that was handed onward?

E522 (results/state_tilt/SILENTARMREAD-2026-11-08.json) published 351 call sites that hand the
callee's result onward without reading it there, 342 of them in production code.  Handing a value
on is exactly where a study of hazards stops being a study of the site: the site says nothing
about what the receiver does with it.  A returned sentinel that every caller guards is not a
hazard; a returned sentinel that lands in a function which never loads its parameter is not one
either -- but a returned sentinel read blind one hop away is the same defect, further from the
proof.

So this study follows the value one hop, per handed-onward site:

  * ``return value``      -> resolve the enclosing function's production call sites and ask
                             whether each one guards the result before its first read
  * ``sink(value)``       -> resolve the callee through the same import rules E515 uses; if it is
                             in-repo, ask whether the parameter is loaded at all and whether the
                             first load sits behind a terminating guard; if it is not in-repo the
                             value left the tree at that call
  * ``{"k": value}``      -> stored, not read: the reader is whoever reads the container

The site verdict is then about the *reader*, not about the site, and the study verdict is about
whether any handed result lands on a reader with no guard.

Attribution limit, published in the face: a receiver is resolved statically by name through the
corpus import maps; a value carried through a container, an attribute or a dynamic dispatch is
reported as not followed rather than counted as safe.

    python scripts/e523_handed_onward_reader.py run        # build + write the face
    python scripts/e523_handed_onward_reader.py check      # gate the published face (fast)
    python scripts/e523_handed_onward_reader.py verify     # re-derive from the tree and gate
    python scripts/e523_handed_onward_reader.py selftest   # fixture corpus + doctored faces
"""
from __future__ import annotations

import ast
import copy
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e515_empty_arm_cover as e515          # noqa: E402  corpus, call resolution, guards, reads
import e522_silent_arm_caller as e522        # noqa: E402  the handed-onward population and scan

CARD = ("E523-WHO-READS-THE-RESULT-THAT-WAS-HANDED-ONWARD")
STUDY = "E523_handed_onward_reader"
DATE_STAMP = "2026-11-08"
FACE_NAME = "handedread_latest.json"
DATED_PREFIX = "HANDEDREAD"

SELF_EXCLUDED = ("e523_", "run_e523", "_e523", "_r1550", "HANDEDREAD", "handedread_")

UPSTREAM_FACE = "results/state_tilt/SILENTARMREAD-%s.json" % e522.DATE_STAMP
UPSTREAM_STUDY = e522.STUDY
PRODUCTION_REACH = (e515.REACH_PRODUCTION, e515.REACH_MODULE)

# how the value leaves the site
F_RETURNED = "returned_from_the_enclosing_function"
F_ARGUMENT = "passed_as_an_argument_to_a_call"
F_STORED = "stored_in_a_container"
F_CONSUMED = "consumed_inside_an_expression_at_the_site"
F_OTHER = "handed_on_in_a_form_this_scan_does_not_follow"
FORM_VOCAB = (F_RETURNED, F_ARGUMENT, F_STORED, F_CONSUMED, F_OTHER)

# what the receiver does with it
R_RETURNED_TO_NO_PRODUCTION_CALLER = "returned_to_no_production_caller"
R_RETURNED_AND_READ_BEHIND_A_GUARD = "returned_and_every_production_caller_guards_it"
R_RETURNED_AND_READ_WITHOUT_A_GUARD = "returned_and_a_production_caller_reads_it_unguarded"
R_ARGUMENT_TO_AN_IN_REPO_CALLEE_THAT_NEVER_LOADS_IT = "argument_to_an_in_repo_callee_that_never_loads_the_parameter"
R_ARGUMENT_TO_AN_IN_REPO_CALLEE_THAT_READS_IT_WITH_A_GUARD = "argument_to_an_in_repo_callee_that_reads_the_parameter_behind_a_guard"
R_ARGUMENT_TO_AN_IN_REPO_CALLEE_THAT_READS_IT_WITHOUT_A_GUARD = "argument_to_an_in_repo_callee_that_reads_the_parameter_with_no_guard"
R_ARGUMENT_TO_AN_EXTERNAL_CALLEE = "argument_to_a_callee_outside_the_corpus_so_the_value_left_the_tree"
R_STORED = "stored_in_a_container_the_reader_is_whoever_reads_the_container"
R_READ_IN_AN_EXPRESSION = "read_inside_an_expression_at_the_site_with_no_guard_but_not_by_a_named_reader"
R_FORM_NOT_FOLLOWED = "the_hand_on_form_is_not_one_this_scan_follows_so_the_reader_is_out_of_reach"
R_UNRESOLVED = "the_receiver_could_not_be_resolved_statically"
READER_VOCAB = (R_RETURNED_TO_NO_PRODUCTION_CALLER, R_RETURNED_AND_READ_BEHIND_A_GUARD,
                R_RETURNED_AND_READ_WITHOUT_A_GUARD,
                R_ARGUMENT_TO_AN_IN_REPO_CALLEE_THAT_NEVER_LOADS_IT,
                R_ARGUMENT_TO_AN_IN_REPO_CALLEE_THAT_READS_IT_WITH_A_GUARD,
                R_ARGUMENT_TO_AN_IN_REPO_CALLEE_THAT_READS_IT_WITHOUT_A_GUARD,
                R_ARGUMENT_TO_AN_EXTERNAL_CALLEE, R_STORED, R_READ_IN_AN_EXPRESSION,
                R_FORM_NOT_FOLLOWED, R_UNRESOLVED)

V_SOME_HANDED_RESULT_IS_READ_WITHOUT_A_GUARD = "some_handed_onward_result_reaches_a_production_reader_with_no_guard"
V_EVERY_REACHED_READER_GUARDS = "every_handed_onward_result_that_reaches_a_reader_is_guarded_there"
V_NOTHING_REACHES_A_READER = "no_handed_onward_result_reaches_an_in_repo_reader"
V_EMPTY = "the_upstream_face_carries_no_handed_onward_production_site"
VERDICT_VOCAB = (V_SOME_HANDED_RESULT_IS_READ_WITHOUT_A_GUARD, V_EVERY_REACHED_READER_GUARDS,
                 V_NOTHING_REACHES_A_READER, V_EMPTY)


def _now():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


# ------------------------------------------------------------------ upstream population
def load_upstream(root=None):
    path = os.path.join(root or ROOT, UPSTREAM_FACE)
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh), _sha256_file(path)


def population(face):
    rows = []
    for site in face.get("sites") or []:
        if site.get("verdict") != e522.CT_HANDED:
            continue
        if site.get("reach") not in PRODUCTION_REACH:
            continue
        rows.append({k: site.get(k) for k in (
            "source", "line", "call_expression", "callee", "callee_module", "callee_line",
            "enclosing_function", "reach", "binding", "bound_name", "read_kind",
            "first_read_line", "first_read_expression")})
    rows.sort(key=lambda r: (r["source"] or "", r["line"] or 0))
    return rows


# ------------------------------------------------------------------ corpus helpers
def corpus_rels(root=None):
    return [rel for rel in e515.corpus(root) if not rel.startswith(SELF_EXCLUDED)]


def parse(rels, root=None):
    trees, failed = [], []
    for rel in rels:
        try:
            trees.append((rel, ast.parse(e515._src(rel, root or ROOT))))
        except (SyntaxError, OSError, UnicodeDecodeError, ValueError):
            failed.append(rel)
    return trees, failed


def function_index(trees):
    """(rel, name) -> dummy callee row, for every function the corpus defines."""
    out = {}
    for rel, tree in trees:
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                out.setdefault((rel, node.name), {
                    "module": rel, "rel": rel, "name": node.name, "line": node.lineno,
                    "arms": 1, "return_paths": 0, "returns_nothing": 0, "returns_a_value": 0,
                })
    return out


def enclosing_function_at(tree, line):
    return e515.enclosing_def(e515.function_spans(tree), line)


def call_at(tree, line, expression=None):
    """The call the site is about; the excerpt disambiguates two calls on one line."""
    candidates = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and n.lineno == line]
    if not candidates:
        return None
    if expression:
        for node in candidates:
            if e515._excerpt(node) == expression:
                return node
    return candidates[0]


def handon_node(func, call, parents, symbol):
    """The node that hands the value on: the parent of the first load of the bound name."""
    if symbol:
        loads = [n for n in ast.walk(func)
                 if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load) and n.id == symbol] \
            if func is not None else []
        reads = e515.first_reads(func, call.lineno, symbol, loads)
        if reads:
            return reads[0], parents.get(reads[0])
    return call, parents.get(call)


def form_of(site, parents, node):
    """Which of the four hand-on forms this site uses."""
    if site.get("binding") == "a_container_element" or site.get("binding") == "discarded":
        return F_STORED if site.get("binding") == "a_container_element" else F_OTHER
    if node is None:
        return F_OTHER
    if isinstance(node, ast.Return):
        return F_RETURNED
    if isinstance(node, (ast.Dict, ast.List, ast.Tuple, ast.Set, ast.DictComp, ast.ListComp)):
        return F_STORED
    if isinstance(node, ast.keyword):
        return F_ARGUMENT
    if isinstance(node, ast.Call):
        return F_ARGUMENT
    if isinstance(node, (ast.Compare, ast.BinOp, ast.BoolOp, ast.UnaryOp, ast.IfExp,
                         ast.JoinedStr, ast.FormattedValue)):
        return F_CONSUMED
    if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign, ast.Attribute, ast.Subscript)):
        return F_OTHER
    return F_OTHER


def receiver_calls(trees, carriers):
    """Production call sites of the carrier functions (one hop, same rules as E522)."""
    if not carriers:
        return []
    callees = {}
    for (rel, name), row in function_index(trees).items():
        if (rel, name) in carriers:
            callees[(rel, name)] = dict(row)
    if not callees:
        return []
    sites = e522.scan(trees, callees)
    return [s for s in sites if s["reach"] in PRODUCTION_REACH]


def argument_reader(trees, index, rel, handon, argument_node):
    """handon is the call that receives the value; argument_node is the value expression itself."""
    """Where an argument lands: the callee's parameter, whether it is loaded, under what guard."""
    parent = handon
    if not isinstance(parent, ast.Call):
        return R_UNRESOLVED
    imports = None
    for trel, tree in trees:
        if trel == rel:
            imports = e515.import_maps(tree)
            break
    if imports is None:
        return R_UNRESOLVED
    resolved = e515.resolve_call(imports, parent, rel, index, index)
    if resolved is None:
        return R_ARGUMENT_TO_AN_EXTERNAL_CALLEE
    target = None
    for trel, tree in trees:
        if trel != resolved[0]:
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == resolved[1]:
                target = node
                break
        break
    if target is None:
        return R_UNRESOLVED
    position = None
    for i, arg in enumerate(parent.args):
        if arg is argument_node or (isinstance(arg, ast.Call) and arg is argument_node):
            position = i
            break
    if position is None:
        if any(kw.value is argument_node for kw in parent.keywords):
            names = [a.arg for a in target.args.args]
            for kw in parent.keywords:
                if kw.value is argument_node:
                    position = names.index(kw.arg) if kw.arg in names else None
                    break
        if position is None:
            return R_UNRESOLVED
    params = [a.arg for a in target.args.args]
    if position >= len(params):
        return R_ARGUMENT_TO_AN_EXTERNAL_CALLEE
    param = params[position]
    loads = sorted([n for n in ast.walk(target)
                    if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load) and n.id == param],
                   key=lambda n: n.lineno)
    if not loads:
        return R_ARGUMENT_TO_AN_IN_REPO_CALLEE_THAT_NEVER_LOADS_IT
    ifs = sorted([n for n in ast.walk(target) if isinstance(n, ast.If)], key=lambda n: n.lineno)
    guards = e515.terminating_guards(target, target.lineno, loads[0].lineno, param, ifs)
    if any(g["terminates"] for g in guards):
        return R_ARGUMENT_TO_AN_IN_REPO_CALLEE_THAT_READS_IT_WITH_A_GUARD
    return R_ARGUMENT_TO_AN_IN_REPO_CALLEE_THAT_READS_IT_WITHOUT_A_GUARD


# ------------------------------------------------------------------ the one-hop scan
def scan(trees, sites, root=None):
    by_rel = dict(trees)
    index = function_index(trees)
    carriers = {(s["source"], s["enclosing_function"]) for s in sites
                if s.get("enclosing_function")}
    hop = receiver_calls(trees, carriers)
    rows = []
    for site in sites:
        tree = by_rel.get(site["source"])
        row = dict(site)
        row.update({"form": F_OTHER, "receiver_kind": None, "reader_function": None,
                    "reader_module": None, "receiver_sites_total": 0,
                    "receiver_sites_guarded": 0, "receiver_sites_unguarded": 0,
                    "receiver_sites_handed_again": 0, "reader_parameter": None,
                    "reader_loads": 0, "verdict": R_UNRESOLVED})
        if tree is None:
            rows.append(row)
            continue
        parents = e515.parent_map(tree)
        call = call_at(tree, site["line"], site.get("call_expression"))
        func = enclosing_function_at(tree, site["line"])
        if call is None:
            rows.append(row)
            continue
        read_node, node = handon_node(func, call, parents, site.get("bound_name"))
        row["form"] = form_of(site, parents, node)
        if row["form"] == F_RETURNED:
            mine = [h for h in hop if h["source"] == site["source"]
                    and h["callee"] == site["enclosing_function"]]
            row["receiver_kind"] = "the_enclosing_function_returns_it_to_its_own_callers"
            row["reader_function"] = site["enclosing_function"]
            row["reader_module"] = site["source"]
            row["receiver_sites_total"] = len(mine)
            row["receiver_sites_guarded"] = len([h for h in mine
                                                 if h["verdict"] in (e522.CT_GUARDED,
                                                                    e522.CT_TESTED_IN_PLACE)])
            row["receiver_sites_unguarded"] = len([h for h in mine
                                                   if h["verdict"] in (e522.CT_UNGUARDED,
                                                                       e522.CT_UNPACKED)])
            row["receiver_sites_handed_again"] = len([h for h in mine
                                                      if h["verdict"] == e522.CT_HANDED])
            if not mine:
                row["verdict"] = R_RETURNED_TO_NO_PRODUCTION_CALLER
            elif row["receiver_sites_unguarded"]:
                row["verdict"] = R_RETURNED_AND_READ_WITHOUT_A_GUARD
            else:
                row["verdict"] = R_RETURNED_AND_READ_BEHIND_A_GUARD
        elif row["form"] == F_ARGUMENT:
            row["receiver_kind"] = "the_callee_takes_it_as_an_argument"
            row["verdict"] = argument_reader(trees, index, site["source"], node, read_node)
            if isinstance(node, ast.Call):
                row["reader_function"] = e515._excerpt(node.func)
                row["reader_module"] = site["source"]
                row["reader_loads"] = 1 if row["verdict"].startswith("argument_to_an_in_repo") else 0
        elif row["form"] == F_STORED:
            row["receiver_kind"] = "the_value_goes_into_a_container"
            row["verdict"] = R_STORED
        elif row["form"] == F_CONSUMED:
            row["receiver_kind"] = "the_value_is_read_inside_an_expression_here"
            row["verdict"] = R_READ_IN_AN_EXPRESSION
        else:
            row["receiver_kind"] = "the_form_is_not_followed"
            row["verdict"] = R_FORM_NOT_FOLLOWED
        rows.append(row)
    rows.sort(key=lambda r: (r["source"] or "", r["line"] or 0))
    return rows


# ------------------------------------------------------------------ face
def _count(records, key, vocab):
    got = {k: 0 for k in vocab}
    for rec in records:
        value = rec.get(key)
        if value in got:
            got[value] += 1
    return got


def _summary(rows, sources, failures, population_size):
    by_reader = _count(rows, "verdict", READER_VOCAB)
    by_form = _count(rows, "form", FORM_VOCAB)
    return {
        "sources_read": sources,
        "parse_failures": len(failures),
        "handed_onward_sites_in_upstream": population_size,
        "sites_at_module_level": len([r for r in rows if r.get("reach") == e515.REACH_MODULE]),
        "sites_followed": len(rows),
        "sites_by_form": by_form,
        "sites_by_reader": by_reader,
        "returned_sites": by_form[F_RETURNED],
        "returned_sites_with_no_production_caller": by_reader[R_RETURNED_TO_NO_PRODUCTION_CALLER],
        "returned_sites_whose_callers_all_guard":
            by_reader[R_RETURNED_AND_READ_BEHIND_A_GUARD],
        "returned_sites_read_unguarded_one_hop_away":
            by_reader[R_RETURNED_AND_READ_WITHOUT_A_GUARD],
        "argument_sites": by_form[F_ARGUMENT],
        "argument_sites_whose_callee_never_loads_the_parameter":
            by_reader[R_ARGUMENT_TO_AN_IN_REPO_CALLEE_THAT_NEVER_LOADS_IT],
        "argument_sites_whose_callee_reads_it_behind_a_guard":
            by_reader[R_ARGUMENT_TO_AN_IN_REPO_CALLEE_THAT_READS_IT_WITH_A_GUARD],
        "argument_sites_whose_callee_reads_it_with_no_guard":
            by_reader[R_ARGUMENT_TO_AN_IN_REPO_CALLEE_THAT_READS_IT_WITHOUT_A_GUARD],
        "argument_sites_that_left_the_tree": by_reader[R_ARGUMENT_TO_AN_EXTERNAL_CALLEE],
        "stored_sites": by_form[F_STORED],
        "sites_read_inside_an_expression": by_form[F_CONSUMED],
        "sites_whose_form_is_not_followed": by_reader[R_FORM_NOT_FOLLOWED],
        "unresolved_sites": by_reader[R_UNRESOLVED],
        "sites_that_reach_a_reader_with_no_guard":
            by_reader[R_RETURNED_AND_READ_WITHOUT_A_GUARD]
            + by_reader[R_ARGUMENT_TO_AN_IN_REPO_CALLEE_THAT_READS_IT_WITHOUT_A_GUARD],
        "sites_that_reach_a_reader_that_guards":
            by_reader[R_RETURNED_AND_READ_BEHIND_A_GUARD]
            + by_reader[R_ARGUMENT_TO_AN_IN_REPO_CALLEE_THAT_READS_IT_WITH_A_GUARD]
            + by_reader[R_ARGUMENT_TO_AN_IN_REPO_CALLEE_THAT_NEVER_LOADS_IT],
    }


def _verdict(summary):
    if not summary["sites_followed"]:
        return V_EMPTY
    if summary["sites_that_reach_a_reader_with_no_guard"]:
        return V_SOME_HANDED_RESULT_IS_READ_WITHOUT_A_GUARD
    if summary["sites_that_reach_a_reader_that_guards"]:
        return V_EVERY_REACHED_READER_GUARDS
    return V_NOTHING_REACHES_A_READER


def build(root=None, write=True, sites=None, rows=None, sources=None, failures=None,
          upstream_sha=None):
    root = root or ROOT
    if sites is None:
        face, sha = load_upstream(root)
        sites = population(face)
        upstream_sha = upstream_sha or sha
    if rows is None:
        trees, failed = parse(corpus_rels(root), root)
        rows = scan(trees, sites, root)
        sources = len(trees) if sources is None else sources
        failures = failed if failures is None else failures
    summary = _summary(rows, sources or 0, failures or [], len(sites))
    face = {
        "study": STUDY,
        "card": CARD,
        "title": "who reads the value that a site handed onward, and is that reader guarded",
        "generated": _now(),
        "evidence_cutoff": DATE_STAMP,
        "population_source": ("%s::population() -- the handed-onward production sites of the "
                              "published E522 face" % os.path.basename(__file__)),
        "upstream_face": UPSTREAM_FACE,
        "upstream_study": UPSTREAM_STUDY,
        "upstream_face_sha256": upstream_sha,
        "method_limits": [
            "one hop only: a value carried through a container, an attribute or a dynamic "
            "dispatch is published as stored/other, never as safe",
            "a receiver call is resolved by the same import rules E515 uses; a call this scan "
            "cannot resolve is published as unresolved, not as external",
            "a returned value is followed through the enclosing function's name, so two "
            "functions sharing a name in different modules stay separate but a function "
            "passed as a callback is not followed at all",
            "an argument is read at the parameter position of the resolved callee; the scan "
            "does not chase *args or **kwargs beyond that position",
            "nothing is executed and no source is rewritten",
            "sources_read and parse_failures are a snapshot of a live tree that other lanes "
            "write to; they are published but not gated, while every reader class is re-derived",
        ],
        "summary": summary,
        "verdict": _verdict(summary),
        "verdict_vocab": list(VERDICT_VOCAB),
        "form_vocab": list(FORM_VOCAB),
        "reader_vocab": list(READER_VOCAB),
        "sites": rows,
        "parse_failures": failures or [],
    }
    if write:
        write_face(face, root)
    return face


def write_face(face, root=None):
    root = root or ROOT
    outdir = os.path.join(root, "results", "state_tilt")
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    dated = os.path.join(outdir, "%s-%s.json" % (DATED_PREFIX, DATE_STAMP))
    latest = os.path.join(outdir, FACE_NAME)
    text = json.dumps(face, indent=1, sort_keys=True)
    for path in (dated, latest):
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text + "\n")
    return dated


def load_face(root=None, name=None):
    path = os.path.join(root or ROOT, "results", "state_tilt", name or FACE_NAME)
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def face_problems(face, root=None, population_size=None):
    bad = []
    for key in ("study", "card", "generated", "evidence_cutoff", "population_source",
                "upstream_face", "upstream_face_sha256", "summary", "verdict", "sites",
                "method_limits", "parse_failures"):
        if key not in face:
            bad.append("the face does not publish %s" % key)
    if face.get("study") != STUDY:
        bad.append("the face is not this study")
    if not str(face.get("population_source") or "").startswith(
            "e523_handed_onward_reader.py::population()"):
        bad.append("the population_source is not this study's population function")
    if face.get("verdict") not in VERDICT_VOCAB:
        bad.append("the verdict %r is not in the vocabulary" % face.get("verdict"))
    summary = face.get("summary") or {}
    rows = face.get("sites") or []
    if face.get("verdict") != _verdict(summary):
        bad.append("the published verdict does not re-derive from the summary")
    if summary.get("sites_followed") != len(rows):
        bad.append("the followed population does not add up")
    if summary.get("parse_failures") != len(face.get("parse_failures") or []):
        bad.append("the parse-failure count does not match the published list")
    if population_size is None:
        population_size = summary.get("handed_onward_sites_in_upstream")
    if population_size is not None and population_size != len(rows):
        bad.append("the face follows %d of the %d upstream handed-onward sites"
                   % (len(rows), population_size))
    by_form = _count(rows, "form", FORM_VOCAB)
    if by_form != (summary.get("sites_by_form") or {}):
        bad.append("the per-form counts do not re-derive")
    if sum(by_form.values()) != len(rows):
        bad.append("the per-form classes do not cover every row")
    by_reader = _count(rows, "verdict", READER_VOCAB)
    if by_reader != (summary.get("sites_by_reader") or {}):
        bad.append("the per-reader counts do not re-derive")
    if sum(by_reader.values()) != len(rows):
        bad.append("the per-reader classes do not cover every row")
    for row in rows:
        for key in ("source", "line", "form", "receiver_kind", "verdict"):
            if key not in row or row[key] is None:
                bad.append("row %s:%s does not publish %s" % (row.get("source"),
                                                              row.get("line"), key))
                break
        if row.get("verdict") in (R_RETURNED_AND_READ_WITHOUT_A_GUARD,
                                  R_RETURNED_AND_READ_BEHIND_A_GUARD) \
                and not row.get("receiver_sites_total"):
            bad.append("row %s:%s claims readers while counting none"
                       % (row.get("source"), row.get("line")))
        if row.get("verdict") == R_RETURNED_AND_READ_WITHOUT_A_GUARD \
                and not row.get("receiver_sites_unguarded"):
            bad.append("row %s:%s claims an unguarded reader while counting none"
                       % (row.get("source"), row.get("line")))
        if row.get("form") != F_RETURNED and row.get("receiver_sites_total"):
            bad.append("row %s:%s counts a returned-to reader outside the returned form"
                       % (row.get("source"), row.get("line")))
    upstream = face.get("upstream_face")
    if upstream:
        path = os.path.join(root or ROOT, upstream)
        if not os.path.isfile(path):
            bad.append("the upstream face is not on disk at %s" % upstream)
        elif _sha256_file(path) != face.get("upstream_face_sha256"):
            bad.append("the upstream face changed since this face was built -- rebuild")
    return bad


def check(face=None, root=None):
    face = face or load_face(root)
    bad = face_problems(face, root)
    print("E523 check: %d problem(s)" % len(bad))
    for line in bad[:20]:
        print("  - %s" % line)
    return 1 if bad else 0


def verify(root=None):
    """Re-derive and gate.  The corpus size is a live-tree snapshot, not a measurement: another
    lane writing a .py into a corpus directory moves ``sources_read`` without moving a single row
    of this study, so those two counters are printed for the drift and are not gated.
    """
    published = load_face(root)
    fresh = build(root=root, write=False)
    bad = face_problems(published, root)
    if fresh["verdict"] != published["verdict"]:
        bad.append("the verdict drifts when re-derived")
    volatile = ("sources_read", "parse_failures")
    trimmed = {k: v for k, v in fresh["summary"].items() if k not in volatile}
    pinned = {k: v for k, v in published["summary"].items() if k not in volatile}
    if json.dumps(trimmed, sort_keys=True) != json.dumps(pinned, sort_keys=True):
        moved = sorted(k for k in set(trimmed) | set(pinned) if trimmed.get(k) != pinned.get(k))
        bad.append("the summary drifts when re-derived: %r" % moved[:6])
    for key in volatile:
        if fresh["summary"].get(key) != published["summary"].get(key):
            print("  note: %s moved %r -> %r (live tree, not gated)"
                  % (key, published["summary"].get(key), fresh["summary"].get(key)))
    print("E523 verify: %d problem(s)" % len(bad))
    for line in bad[:20]:
        print("  - %s" % line)
    return 1 if bad else 0


# ------------------------------------------------------------------ selftest
FIXTURE = '''
def _read(path):
    return open(path).read()


def builder(path):
    if not path:
        return ""
    return _read(path)


def returned_carrier(path):
    value = builder(path)
    return value


def argument_carrier(path):
    value = builder(path)
    return sum(value)


def dropping_carrier(path):
    value = builder(path)
    return ignores_the_value(value)


def reading_carrier(path):
    value = builder(path)
    return reads_payload(value)


def ignores_the_value(payload):
    return 1


def reads_payload(payload):
    return payload.strip()


def guarded_reader(path):
    got = returned_carrier(path)
    if not got:
        return None
    return got.strip()


def blind_reader(path):
    got = returned_carrier(path)
    return got.strip()


def main():
    guarded_reader("a")
    blind_reader("b")
    argument_carrier("c")
    dropping_carrier("d")
    reading_carrier("e")
    return 0
'''


def _line_of(text, needle, start=0):
    idx = text.index(needle, start)
    return text[:idx].count("\n") + 1


def _fixture_site(text, carrier, rel="scripts/fixture_mod.py"):
    start = text.index("def %s(" % carrier)
    return {
        "source": rel,
        "line": _line_of(text, "builder(path)", start),
        "call_expression": "builder(path)",
        "callee": "builder",
        "callee_module": rel,
        "callee_line": _line_of(text, "def builder("),
        "enclosing_function": carrier,
        "reach": e515.REACH_PRODUCTION,
        "binding": "a_single_name",
        "bound_name": "value",
        "read_kind": e515.READ_HANDON,
        "first_read_line": _line_of(text, "builder(path)", start),
        "first_read_expression": "",
    }


def selftest():
    bad = []
    tmp = tempfile.mkdtemp(prefix="e523_")
    try:
        os.makedirs(os.path.join(tmp, "scripts"))
        path = os.path.join(tmp, "scripts", "fixture_mod.py")
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(FIXTURE)
        sites = [_fixture_site(FIXTURE, name) for name in
                 ("returned_carrier", "argument_carrier", "dropping_carrier", "reading_carrier")]
        if len(population_of(sites)) != 4:
            bad.append("the fixture population did not keep its four production sites")
        trees, failed = parse(["scripts/fixture_mod.py"], tmp)
        if failed or not trees:
            bad.append("the fixture corpus did not parse: %r" % failed)
        rows = scan(trees, sites, tmp)
        by = {r["enclosing_function"]: r for r in rows}
        if by["returned_carrier"]["form"] != F_RETURNED:
            bad.append("a returned value was not classified as returned (%r)"
                       % by["returned_carrier"]["form"])
        if by["returned_carrier"]["verdict"] != R_RETURNED_AND_READ_WITHOUT_A_GUARD:
            bad.append("a returned value with one blind reader should be the unguarded class, saw %r"
                       % by["returned_carrier"]["verdict"])
        if by["returned_carrier"]["receiver_sites_total"] != 2:
            bad.append("expected two production callers of the returned carrier, saw %r"
                       % by["returned_carrier"]["receiver_sites_total"])
        if by["returned_carrier"]["receiver_sites_guarded"] != 1:
            bad.append("the guarded fixture reader was not counted as guarded")
        if by["argument_carrier"]["form"] != F_ARGUMENT:
            bad.append("an argument form was not classified as such (%r)"
                       % by["argument_carrier"]["form"])
        if by["argument_carrier"]["verdict"] != R_ARGUMENT_TO_AN_EXTERNAL_CALLEE:
            bad.append("an argument to sum() should be external, saw %r"
                       % by["argument_carrier"]["verdict"])
        if by["dropping_carrier"]["verdict"] != R_ARGUMENT_TO_AN_IN_REPO_CALLEE_THAT_NEVER_LOADS_IT:
            bad.append("an argument to a callee that never loads it should say so, saw %r"
                       % by["dropping_carrier"]["verdict"])
        if by["reading_carrier"]["verdict"] != \
                R_ARGUMENT_TO_AN_IN_REPO_CALLEE_THAT_READS_IT_WITHOUT_A_GUARD:
            bad.append("an argument read with no guard should say so, saw %r"
                       % by["reading_carrier"]["verdict"])

        # a guarded-only world must flip the study verdict
        calm_sites = [s for s in sites if s["enclosing_function"] not in
                      ("returned_carrier", "reading_carrier")]
        calm_rows = [r for r in rows if r["enclosing_function"] not in
                     ("returned_carrier", "reading_carrier")]
        calm = _summary(calm_rows, 1, [], len(calm_sites))
        if _verdict(calm) != V_EVERY_REACHED_READER_GUARDS:
            bad.append("a corpus whose only readers guard should report the guarded verdict, saw %r"
                       % _verdict(calm))
        empty = _summary([], 1, [], 0)
        if _verdict(empty) != V_EMPTY:
            bad.append("an empty population is not reported as empty")

        os.makedirs(os.path.join(tmp, "results", "state_tilt"))
        up = os.path.join(ROOT, UPSTREAM_FACE)
        shutil.copyfile(up, os.path.join(tmp, "results", "state_tilt",
                                        os.path.basename(UPSTREAM_FACE)))
        face = build(root=tmp, write=False, sites=sites, rows=rows, sources=1, failures=[],
                     upstream_sha=_sha256_file(up))
        if face["verdict"] != V_SOME_HANDED_RESULT_IS_READ_WITHOUT_A_GUARD:
            bad.append("the fixture verdict should be the unguarded one, saw %r" % face["verdict"])
        if face_problems(face, tmp):
            bad.append("the fixture face is refused by its own gate: %r"
                       % face_problems(face, tmp)[:2])
        for doctor, why in (
            (lambda f: f.__setitem__("verdict", V_EVERY_REACHED_READER_GUARDS),
             "a hand-written verdict"),
            (lambda f: f["summary"].__setitem__("sites_followed", 99),
             "an edited followed count"),
            (lambda f: f["summary"]["sites_by_reader"].__setitem__(R_STORED, 3),
             "an edited reader histogram"),
            (lambda f: f["sites"][0].__setitem__("verdict", R_STORED),
             "a row relabelled as stored"),
            (lambda f: [r.__setitem__("form", F_RETURNED) for r in f["sites"]
                        if r["form"] != F_RETURNED][:1],
             "a row whose form claims a returned reader it does not count"),
            (lambda f: f.__setitem__("upstream_face_sha256", "0" * 64),
             "an edited upstream pin"),
        ):
            hurt = copy.deepcopy(face)
            doctor(hurt)
            if not face_problems(hurt, tmp):
                bad.append("%s survived the gate" % why)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if bad:
        print("E523 selftest: %d problem(s)" % len(bad))
        for line in bad[:20]:
            print("  - %s" % line)
        return 1
    print("E523 selftest: clean")
    return 0


def population_of(sites):
    """The fixture rows are already distilled rows; the filter is the population's own rule."""
    return [s for s in sites if s.get("reach") in PRODUCTION_REACH]


# ------------------------------------------------------------------ entry
def run():
    face = build()
    s = face["summary"]
    print("E523 run: followed %r handed-onward production sites in %r sources (%r parse failures)"
          % (s["sites_followed"], s["sources_read"], s["parse_failures"]))
    print("  forms: returned %r | argument %r | stored %r"
          % (s["returned_sites"], s["argument_sites"], s["stored_sites"]))
    print("  readers with no guard %r (returned %r / argument %r) | guarded %r | left the tree %r"
          " | no caller %r | unresolved %r"
          % (s["sites_that_reach_a_reader_with_no_guard"],
             s["returned_sites_read_unguarded_one_hop_away"],
             s["argument_sites_whose_callee_reads_it_with_no_guard"],
             s["sites_that_reach_a_reader_that_guards"],
             s["argument_sites_that_left_the_tree"],
             s["returned_sites_with_no_production_caller"],
             s["unresolved_sites"]))
    print("  verdict %r" % face["verdict"])
    return 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "run"
    table = {"run": run, "check": check, "verify": verify, "selftest": selftest}
    if cmd not in table:
        print(__doc__)
        return 2
    return table[cmd]()


if __name__ == "__main__":
    sys.exit(main())
