"""E524 -- is the reader of a handed-onward value itself handing it further?

E523 (results/state_tilt/handedread_latest.json) followed every handed-onward production site one
hop and stopped at the reader.  A one-hop stop is honest but it is also a floor: a reader that
checks a guard and then forwards the value has not guarded the value -- it has only passed it on.
So the chain past that reader is unmeasured, and "one hop" is not an answer to "how deep does the
unguarded read sit".

This study takes every site E523 resolved to an in-repo reader and follows the value once more:

  * the first reader is a *caller* of a returning function -> the parcels it hands onward are
    themselves handed-onward sites; scan them with the same one-hop rules and publish what the
    second reader does (reads behind a guard, reads blind, never loads it, hands it on again,
    leaves the tree, or cannot be resolved)
  * the first reader is an in-repo *callee* -> E523 already said what the callee does with the
    parameter (never loads it / reads behind a guard / reads blind), so the chain terminates there
    and this study says so instead of inventing a hop
  * the first reader reads it at the call site -> same, the chain ends at the depth E523 measured

Every row publishes a chain class, the depth of the deepest unguarded read it can prove, and the
counts behind it.  A chain this scan cannot follow, a reader it cannot resolve and a value that
left the tree are their own classes, never zeros.

    python scripts/e524_reader_onward.py run        # build + write the face
    python scripts/e524_reader_onward.py check      # gate the published face (fast)
    python scripts/e524_reader_onward.py verify     # re-derive from the tree and gate
    python scripts/e524_reader_onward.py selftest   # fixture corpus + doctored faces
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
import e522_silent_arm_caller as e522        # noqa: E402  handed-onward site verdicts
import e523_handed_onward_reader as e523     # noqa: E402  the one-hop reader face

CARD = "E524-WHICH-READER-OF-A-HANDED-ONWARD-RESULT-IS-ITSELF-HANDED-FURTHER"
STUDY = "E524_reader_onward"
DATE_STAMP = "2026-11-08"
FACE_NAME = "readeronward_latest.json"
DATED_PREFIX = "READERONWARD"

SELF_EXCLUDED = ("e524_", "run_e524", "_e524", "READERONWARD", "readeronward_")

UPSTREAM_FACE = "results/state_tilt/handedread_latest.json"
UPSTREAM_STUDY = e523.STUDY

# the depth-1 reader classes E523 could resolve to an actual in-repo reader
READER_REACHED = (
    e523.R_RETURNED_AND_READ_BEHIND_A_GUARD,
    e523.R_RETURNED_AND_READ_WITHOUT_A_GUARD,
    e523.R_ARGUMENT_TO_AN_IN_REPO_CALLEE_THAT_NEVER_LOADS_IT,
    e523.R_ARGUMENT_TO_AN_IN_REPO_CALLEE_THAT_READS_IT_WITH_A_GUARD,
    e523.R_ARGUMENT_TO_AN_IN_REPO_CALLEE_THAT_READS_IT_WITHOUT_A_GUARD,
)

# where the chain stands after this study's second hop
C_FIRST_READER_READS_IT = "the_first_reader_reads_it_so_the_chain_ends_at_the_depth_E523_measured"
C_SECOND_READER_GUARDS = "the_second_reader_reads_it_behind_a_guard"
C_SECOND_READER_UNGUARDED = "the_second_reader_reads_it_with_no_guard"
C_SECOND_READER_NEVER_LOADS = "the_second_reader_never_loads_it_so_the_value_dies_here"
C_STILL_HANDED_FURTHER = "the_second_reader_hands_it_on_again_so_the_chain_is_still_unmeasured"
C_SECOND_READER_UNRESOLVED = "the_second_reader_could_not_be_resolved_statically"
C_LEFT_THE_TREE = "the_value_left_the_corpus_at_the_second_hop"
CHAIN_VOCAB = (C_FIRST_READER_READS_IT, C_SECOND_READER_GUARDS, C_SECOND_READER_UNGUARDED,
               C_SECOND_READER_NEVER_LOADS, C_STILL_HANDED_FURTHER, C_SECOND_READER_UNRESOLVED,
               C_LEFT_THE_TREE)

V_UNGUARDED_SITS_TWO_HOPS_OUT = "an_unguarded_read_sits_two_hops_from_the_original_hand_on"
V_EVERY_CHAIN_ENDS_GUARDED_OR_DEAD = \
    "every_chain_that_extends_past_the_first_reader_ends_in_a_guard_a_dead_value_or_a_forward"
V_NO_CHAIN_EXTENDS = "no_chain_extends_past_the_reader_E523_already_measured"
V_EMPTY = "the_upstream_face_carries_no_site_that_reaches_a_reader"
VERDICT_VOCAB = (V_UNGUARDED_SITS_TWO_HOPS_OUT, V_EVERY_CHAIN_ENDS_GUARDED_OR_DEAD,
                 V_NO_CHAIN_EXTENDS, V_EMPTY)


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
    for row in face.get("sites") or []:
        if row.get("verdict") not in READER_REACHED:
            continue
        rows.append({k: row.get(k) for k in (
            "source", "line", "call_expression", "callee", "callee_module", "callee_line",
            "enclosing_function", "reach", "binding", "bound_name", "read_kind",
            "first_read_line", "first_read_expression", "form", "receiver_kind", "verdict",
            "reader_function", "reader_module", "receiver_sites_total",
            "receiver_sites_guarded", "receiver_sites_unguarded", "receiver_sites_handed_again")})
    rows.sort(key=lambda r: (r["source"] or "", r["line"] or 0))
    return rows


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


# ------------------------------------------------------------------ second hop
def _second_row_class(second):
    """Map one depth-2 reader verdict (E523 vocabulary) onto this study's chain vocabulary."""
    verdict = second.get("verdict")
    if verdict in (e523.R_ARGUMENT_TO_AN_IN_REPO_CALLEE_THAT_READS_IT_WITHOUT_A_GUARD,
                   e523.R_RETURNED_AND_READ_WITHOUT_A_GUARD,
                   e523.R_READ_IN_AN_EXPRESSION):
        return C_SECOND_READER_UNGUARDED
    if verdict in (e523.R_ARGUMENT_TO_AN_IN_REPO_CALLEE_THAT_READS_IT_WITH_A_GUARD,
                   e523.R_RETURNED_AND_READ_BEHIND_A_GUARD):
        return C_SECOND_READER_GUARDS
    if verdict in (e523.R_ARGUMENT_TO_AN_IN_REPO_CALLEE_THAT_NEVER_LOADS_IT,
                   e523.R_RETURNED_TO_NO_PRODUCTION_CALLER):
        return C_SECOND_READER_NEVER_LOADS
    if verdict == e523.R_ARGUMENT_TO_AN_EXTERNAL_CALLEE:
        return C_LEFT_THE_TREE
    if verdict in (e523.R_STORED, e523.R_FORM_NOT_FOLLOWED):
        return C_STILL_HANDED_FURTHER
    return C_SECOND_READER_UNRESOLVED


_PRIMARY = (C_SECOND_READER_UNGUARDED, C_STILL_HANDED_FURTHER, C_LEFT_THE_TREE,
            C_SECOND_READER_UNRESOLVED, C_SECOND_READER_NEVER_LOADS, C_SECOND_READER_GUARDS)


def second_hop(trees, rows):
    """Follow each population row one hop past the reader E523 measured."""
    carriers = {(r["reader_module"], r["reader_function"]) for r in rows
                if r.get("form") == e523.F_RETURNED and r.get("reader_function")}
    hop = e523.receiver_calls(trees, carriers) if carriers else []
    handed = [h for h in hop if h["verdict"] == e522.CT_HANDED]
    second_rows = e523.scan(trees, handed) if handed else []
    by_owner = {}
    for s in second_rows:
        by_owner.setdefault((s.get("callee_module"), s.get("callee")), []).append(s)

    out = []
    for row in rows:
        rec = dict(row)
        rec.update({"chain": None, "second_readers_total": 0, "second_readers_guarded": 0,
                    "second_readers_unguarded": 0, "second_readers_handed_further": 0,
                    "second_readers_unresolved": 0, "second_readers_left_the_tree": 0,
                    "second_readers_never_load": 0, "deepest_unguarded_depth": None})
        depth1 = row.get("verdict")
        if depth1 in (e523.R_RETURNED_AND_READ_WITHOUT_A_GUARD,
                      e523.R_ARGUMENT_TO_AN_IN_REPO_CALLEE_THAT_READS_IT_WITHOUT_A_GUARD):
            rec["deepest_unguarded_depth"] = 1
        parcels = []
        if row.get("form") == e523.F_RETURNED:
            parcels = by_owner.get((row.get("reader_module"), row.get("reader_function")), [])
        if parcels:
            classes = []
            for s in parcels:
                klass = _second_row_class(s)
                classes.append(klass)
                if klass == C_SECOND_READER_UNGUARDED:
                    rec["second_readers_unguarded"] += 1
                elif klass == C_SECOND_READER_GUARDS:
                    rec["second_readers_guarded"] += 1
                elif klass == C_SECOND_READER_NEVER_LOADS:
                    rec["second_readers_never_load"] += 1
                elif klass == C_STILL_HANDED_FURTHER:
                    rec["second_readers_handed_further"] += 1
                elif klass == C_LEFT_THE_TREE:
                    rec["second_readers_left_the_tree"] += 1
                else:
                    rec["second_readers_unresolved"] += 1
            rec["second_readers_total"] = len(parcels)
            for klass in _PRIMARY:
                if klass in classes:
                    rec["chain"] = klass
                    break
            if rec["second_readers_unguarded"]:
                rec["deepest_unguarded_depth"] = 2
        elif row.get("form") == e523.F_RETURNED:
            # E523 measured a caller reading it and no parcel was handed on: the chain ends there
            rec["chain"] = C_FIRST_READER_READS_IT
            rec["second_readers_total"] = 0
        else:
            # an argument form: E523 already resolved what the callee does with the parameter
            if depth1 == e523.R_ARGUMENT_TO_AN_IN_REPO_CALLEE_THAT_NEVER_LOADS_IT:
                rec["chain"] = C_SECOND_READER_NEVER_LOADS
                rec["second_readers_total"] = 1
                rec["second_readers_never_load"] = 1
            elif depth1 == e523.R_ARGUMENT_TO_AN_IN_REPO_CALLEE_THAT_READS_IT_WITH_A_GUARD:
                rec["chain"] = C_FIRST_READER_READS_IT
                rec["second_readers_total"] = 1
                rec["second_readers_guarded"] = 1
            elif depth1 == e523.R_ARGUMENT_TO_AN_IN_REPO_CALLEE_THAT_READS_IT_WITHOUT_A_GUARD:
                rec["chain"] = C_FIRST_READER_READS_IT
                rec["second_readers_total"] = 1
                rec["second_readers_unguarded"] = 1
            else:
                rec["chain"] = C_SECOND_READER_UNRESOLVED
                rec["second_readers_unresolved"] = 1
        out.append(rec)
    out.sort(key=lambda r: (r["source"] or "", r["line"] or 0))
    return out, second_rows, len(handed)


# ------------------------------------------------------------------ face
def _count(records, key, vocab):
    got = {k: 0 for k in vocab}
    for rec in records:
        value = rec.get(key)
        if value in got:
            got[value] += 1
    return got


def _summary(rows, sources, failures, population_size, second_sites):
    by_chain = _count(rows, "chain", CHAIN_VOCAB)
    by_form = _count(rows, "form", e523.FORM_VOCAB)
    return {
        "sources_read": sources,
        "parse_failures": len(failures),
        "sites_in_population": population_size,
        "sites_followed": len(rows),
        "sites_by_form": by_form,
        "sites_by_chain": by_chain,
        "second_hop_sites_followed": second_sites,
        "sites_that_hand_a_parcel_onward": len([r for r in rows
                                                if (r.get("second_readers_total") or 0)
                                                and r.get("form") == e523.F_RETURNED]),
        "sites_where_the_first_reader_reads_it": by_chain[C_FIRST_READER_READS_IT],
        "sites_with_an_unguarded_read_at_depth_1":
            len([r for r in rows if r.get("deepest_unguarded_depth") == 1]),
        "sites_with_an_unguarded_read_at_depth_2":
            len([r for r in rows if r.get("deepest_unguarded_depth") == 2]),
        "rows_with_a_read_at_both_depths":
            len([r for r in rows if r.get("deepest_unguarded_depth") == 2
                 and r.get("verdict") in (e523.R_RETURNED_AND_READ_WITHOUT_A_GUARD,
                                          e523.R_ARGUMENT_TO_AN_IN_REPO_CALLEE_THAT_READS_IT_WITHOUT_A_GUARD)]),
        "sites_where_the_second_reader_guards": by_chain[C_SECOND_READER_GUARDS],
        "sites_where_the_value_dies_at_the_second_reader": by_chain[C_SECOND_READER_NEVER_LOADS],
        "sites_still_handed_further_after_the_second_read": by_chain[C_STILL_HANDED_FURTHER],
        "sites_whose_second_reader_is_unresolved": by_chain[C_SECOND_READER_UNRESOLVED],
        "sites_that_left_the_tree_at_the_second_hop": by_chain[C_LEFT_THE_TREE],
        "rows_that_publish_no_chain_class": len([r for r in rows if not r.get("chain")]),
    }


def _verdict(summary):
    if not summary["sites_followed"]:
        return V_EMPTY
    if summary["sites_with_an_unguarded_read_at_depth_2"]:
        return V_UNGUARDED_SITS_TWO_HOPS_OUT
    if not summary["sites_that_hand_a_parcel_onward"]:
        return V_NO_CHAIN_EXTENDS
    return V_EVERY_CHAIN_ENDS_GUARDED_OR_DEAD


def build(root=None, write=True, sites=None, rows=None, sources=None, failures=None,
          upstream_sha=None, second_sites=0):
    root = root or ROOT
    if sites is None:
        face, sha = load_upstream(root)
        sites = population(face)
        upstream_sha = upstream_sha or sha
    if rows is None:
        trees, failed = parse(corpus_rels(root), root)
        rows, _second_rows, second_sites = second_hop(trees, sites)
        sources = len(trees) if sources is None else sources
        failures = failed if failures is None else failures
    summary = _summary(rows, sources or 0, failures or [], len(sites), second_sites)
    face = {
        "study": STUDY,
        "card": CARD,
        "title": "is the reader of a handed-onward value itself handing it further",
        "generated": _now(),
        "evidence_cutoff": DATE_STAMP,
        "population_source": ("%s::population() -- the sites the published E523 face resolved to an "
                              "in-repo reader" % os.path.basename(__file__)),
        "upstream_face": UPSTREAM_FACE,
        "upstream_study": UPSTREAM_STUDY,
        "upstream_face_sha256": upstream_sha,
        "method_limits": [
            "two hops, not a fixpoint: a chain still handed onward after the second reader is "
            "published as that class and its third reader is not followed",
            "the depth-2 parcels of a returning function are the call sites E522 already "
            "classifies as handed onward; a parcel bound and dropped is not one of them",
            "an argument-form row is terminal here because E523 already resolved what the callee "
            "does with the parameter; this study does not re-open that callee's body a second time",
            "a row can carry an unguarded read at both depths; deepest_unguarded_depth publishes "
            "the deeper of the two and the summary counts those rows separately",
            "nothing is executed and no source is rewritten",
            "sources_read, parse_failures and second_hop_sites_followed are a snapshot of a live "
            "tree that other lanes write to; they are published but not gated, while every chain "
            "class is re-derived",
        ],
        "summary": summary,
        "verdict": _verdict(summary),
        "verdict_vocab": list(VERDICT_VOCAB),
        "chain_vocab": list(CHAIN_VOCAB),
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
            "e524_reader_onward.py::population()"):
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
        population_size = summary.get("sites_in_population")
    if population_size is not None and population_size != len(rows):
        bad.append("the face follows %d of the %d upstream reader-reaching sites"
                   % (len(rows), population_size))
    by_chain = _count(rows, "chain", CHAIN_VOCAB)
    if by_chain != (summary.get("sites_by_chain") or {}):
        bad.append("the per-chain counts do not re-derive")
    if sum(by_chain.values()) != len(rows):
        bad.append("the per-chain classes do not cover every row")
    by_form = _count(rows, "form", e523.FORM_VOCAB)
    if by_form != (summary.get("sites_by_form") or {}):
        bad.append("the per-form counts do not re-derive")
    if summary.get("sites_where_the_first_reader_reads_it") != by_chain[C_FIRST_READER_READS_IT]:
        bad.append("the first-reader count does not re-derive from the rows")
    depth2 = len([r for r in rows if r.get("deepest_unguarded_depth") == 2])
    if summary.get("sites_with_an_unguarded_read_at_depth_2") != depth2:
        bad.append("the depth-2 unguarded count does not re-derive from the rows")
    if depth2 != by_chain[C_SECOND_READER_UNGUARDED]:
        bad.append("a row claims an unguarded second reader without the chain class, or the reverse")
    for row in rows:
        for key in ("source", "line", "form", "chain", "verdict"):
            if key not in row or row[key] is None:
                bad.append("row %s:%s does not publish %s" % (row.get("source"),
                                                              row.get("line"), key))
                break
        if row.get("chain") == C_SECOND_READER_UNGUARDED \
                and not row.get("second_readers_unguarded"):
            bad.append("row %s:%s claims an unguarded second reader and counts none"
                       % (row.get("source"), row.get("line")))
        if row.get("chain") == C_SECOND_READER_GUARDS and row.get("second_readers_unguarded"):
            bad.append("row %s:%s claims a guarded second reader and counts an unguarded one"
                       % (row.get("source"), row.get("line")))
        if row.get("chain") in (C_SECOND_READER_GUARDS, C_SECOND_READER_UNGUARDED,
                                C_SECOND_READER_NEVER_LOADS) \
                and not (row.get("second_readers_total") or 0):
            bad.append("row %s:%s resolves a second reader and counts none"
                       % (row.get("source"), row.get("line")))
        if row.get("deepest_unguarded_depth") == 2 and not row.get("second_readers_unguarded"):
            bad.append("row %s:%s publishes a depth-2 unguarded read and counts none"
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
    print("E524 check: %d problem(s)" % len(bad))
    for line in bad[:20]:
        print("  - %s" % line)
    return 1 if bad else 0


def verify(root=None):
    """Re-derive and gate.  Corpus size and the depth-2 parcel count are live-tree snapshots."""
    published = load_face(root)
    fresh = build(root=root, write=False)
    bad = face_problems(published, root)
    if fresh["verdict"] != published["verdict"]:
        bad.append("the verdict drifts when re-derived")
    volatile = ("sources_read", "parse_failures", "second_hop_sites_followed")
    trimmed = {k: v for k, v in fresh["summary"].items() if k not in volatile}
    pinned = {k: v for k, v in published["summary"].items() if k not in volatile}
    if json.dumps(trimmed, sort_keys=True) != json.dumps(pinned, sort_keys=True):
        moved = sorted(k for k in set(trimmed) | set(pinned) if trimmed.get(k) != pinned.get(k))
        bad.append("the summary drifts when re-derived: %r" % moved[:6])
    for key in volatile:
        if fresh["summary"].get(key) != published["summary"].get(key):
            print("  note: %s moved %r -> %r (live tree, not gated)"
                  % (key, published["summary"].get(key), fresh["summary"].get(key)))
    print("E524 verify: %d problem(s)" % len(bad))
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


def files_it(path):
    value = builder(path)
    return value


def files_it_plain(path):
    value = builder(path)
    return value


def hands_it_on(path):
    got = files_it(path)
    return blind_reader(got)


def hands_it_on_safely(path):
    got = files_it(path)
    return guarded_reader(got)


def reads_it_here(path):
    got = files_it_plain(path)
    return got.strip()


def blind_reader(payload):
    return payload.strip()


def guarded_reader(payload):
    if not payload:
        return None
    return payload.strip()


def main():
    hands_it_on("a")
    hands_it_on_safely("b")
    reads_it_here("c")
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
        "verdict": e522.CT_HANDED,
    }


def selftest():
    bad = []
    tmp = tempfile.mkdtemp(prefix="e524_")
    try:
        os.makedirs(os.path.join(tmp, "scripts"))
        path = os.path.join(tmp, "scripts", "fixture_mod.py")
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(FIXTURE)
        carriers = ("files_it", "files_it_plain")
        depth1_sites = [_fixture_site(FIXTURE, name) for name in carriers]
        trees, failed = parse(["scripts/fixture_mod.py"], tmp)
        if failed or not trees:
            bad.append("the fixture corpus did not parse: %r" % failed)
        # depth 1 is E523's own machinery: returned forms whose readers hand it on or read it
        depth1 = e523.scan(trees, depth1_sites, tmp)
        pop = population({"sites": depth1})
        if len(pop) != len([r for r in depth1 if r["verdict"] in READER_REACHED]):
            bad.append("the population filter does not follow the vocabulary it publishes")
        if len(pop) < 2:
            bad.append("the fixture kept %r population rows, expected two" % len(pop))
        rows, second_rows, second_n = second_hop(trees, pop)
        if not second_rows:
            bad.append("the fixture produced no depth-2 parcel to follow")
        by_carrier = {r["enclosing_function"]: r for r in rows}
        files_it = by_carrier.get("files_it")
        if files_it is None:
            bad.append("the parcel-handing carrier is missing from the followed rows")
        else:
            if files_it["second_readers_total"] != 2:
                bad.append("expected two depth-2 parcels, saw %r"
                           % files_it["second_readers_total"])
            if files_it["chain"] != C_SECOND_READER_UNGUARDED:
                bad.append("a blind reader two hops out should be the unguarded class, saw %r"
                           % files_it["chain"])
            if files_it["deepest_unguarded_depth"] != 2:
                bad.append("the depth of the unguarded read is not published as 2, saw %r"
                           % files_it["deepest_unguarded_depth"])
            if files_it["second_readers_guarded"] != 1:
                bad.append("the guarded sibling was not counted as a guarded second reader")
        plain = by_carrier.get("files_it_plain")
        if plain is None:
            bad.append("the plain carrier is missing from the followed rows")
        elif plain["chain"] != C_FIRST_READER_READS_IT:
            bad.append("a value its first reader reads should end the chain, saw %r"
                       % plain["chain"])
        elif plain["deepest_unguarded_depth"] != 1:
            bad.append("the plain carrier should publish an unguarded read at depth 1, saw %r"
                       % plain["deepest_unguarded_depth"])
        if not any(r["form"] == e523.F_RETURNED for r in pop):
            bad.append("the fixture never produced a returned-form population row")

        # a world where no parcel is handed on must flip the study verdict
        calm_pop = [r for r in pop if r["enclosing_function"] != "files_it"]
        calm_rows, calm_second, calm_n = second_hop(trees, calm_pop)
        calm = _summary(calm_rows, 1, [], len(calm_pop), calm_n)
        if _verdict(calm) != V_NO_CHAIN_EXTENDS:
            bad.append("a world where nothing is handed on should say no chain extends, saw %r"
                       % _verdict(calm))
        empty = _summary([], 1, [], 0, 0)
        if _verdict(empty) != V_EMPTY:
            bad.append("an empty population is not reported as empty")

        os.makedirs(os.path.join(tmp, "results", "state_tilt"))
        up = os.path.join(ROOT, UPSTREAM_FACE)
        shutil.copyfile(up, os.path.join(tmp, "results", "state_tilt",
                                        os.path.basename(UPSTREAM_FACE)))
        face = build(root=tmp, write=False, sites=pop, rows=rows, sources=1, failures=[],
                     upstream_sha=_sha256_file(up), second_sites=second_n)
        if face_problems(face, tmp):
            bad.append("the fixture face is refused by its own gate: %r"
                       % face_problems(face, tmp)[:2])
        for doctor, why in (
            (lambda f: f.__setitem__("verdict", V_EVERY_CHAIN_ENDS_GUARDED_OR_DEAD),
             "a hand-written verdict"),
            (lambda f: f["summary"].__setitem__("sites_followed", 99),
             "an edited followed count"),
            (lambda f: f["summary"].__setitem__("sites_with_an_unguarded_read_at_depth_2", 0),
             "a zeroed depth-2 count"),
            (lambda f: [r.__setitem__("second_readers_unguarded", 0) for r in f["sites"]
                        if r["chain"] == C_SECOND_READER_UNGUARDED][:1],
             "a row that counts no unguarded second reader"),
            (lambda f: [r.__setitem__("chain", C_SECOND_READER_GUARDS) for r in f["sites"]
                        if r["chain"] == C_SECOND_READER_UNGUARDED][:1],
             "a blind row relabelled as a guarded reader"),
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
        print("E524 selftest: %d problem(s)" % len(bad))
        for line in bad[:20]:
            print("  - %s" % line)
        return 1
    print("E524 selftest: clean")
    return 0


# ------------------------------------------------------------------ entry
def run():
    face = build()
    s = face["summary"]
    print("E524 run: followed %r reader-reaching sites in %r sources (%r parse failures), "
          "%r depth-2 parcels"
          % (s["sites_followed"], s["sources_read"], s["parse_failures"],
             s["second_hop_sites_followed"]))
    print("  chains: first reader reads %r | second guards %r | second blind %r | dies %r | "
          "still handed on %r | unresolved %r | left the tree %r"
          % (s["sites_where_the_first_reader_reads_it"],
             s["sites_where_the_second_reader_guards"],
             s["sites_with_an_unguarded_read_at_depth_2"],
             s["sites_where_the_value_dies_at_the_second_reader"],
             s["sites_still_handed_further_after_the_second_read"],
             s["sites_whose_second_reader_is_unresolved"],
             s["sites_that_left_the_tree_at_the_second_hop"]))
    print("  unguarded at depth 1 %r | at depth 2 %r | both %r | carriers that hand a parcel on %r"
          % (s["sites_with_an_unguarded_read_at_depth_1"],
             s["sites_with_an_unguarded_read_at_depth_2"],
             s["rows_with_a_read_at_both_depths"],
             s["sites_that_hand_a_parcel_onward"]))
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