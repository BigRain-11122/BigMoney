"""E525 -- what happens to the values the second reader still forwards?

E524 (results/state_tilt/readeronward_latest.json) followed each handed-onward value one hop past
its second reader and then stopped, publishing two classes that are names for holes rather than
answers:

  * 23 sites: "the value left the corpus at the second hop"
  *  6 sites: "the second reader hands it on again so the chain is still unmeasured"

This study opens both, one parcel at a time, and keeps the two upstream classes separate:

  * for a site E524 said left the tree, resolve the second-hop receiving call in the source and name
    the boundary the value actually crosses -- the process exit status (``sys.exit``/``SystemExit``/
    ``exit``/``quit``/``os._exit``), an imported external function, another named function in this
    corpus, or a name the corpus never resolves
  * for a site E524 said is still forwarded, publish the form that stopped the scan -- a value stored
    into a container whose reader is whoever reads the container, or a hand-on form E523 does not
    follow -- and say so instead of inventing a reader

Every boundary is re-derived from the cited source line at ``check`` time, not copied from the
upstream face.  A container the scan does not follow is published as unmeasured, never as a zero.

    python scripts/e525_onward_residue.py run        # build + write the face
    python scripts/e525_onward_residue.py check      # gate the published face (fast, 29 files)
    python scripts/e525_onward_residue.py verify     # re-derive from the tree and gate
    python scripts/e525_onward_residue.py selftest   # fixture corpus + doctored faces
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

import e515_empty_arm_cover as e515          # noqa: E402  corpus / source loader
import e522_silent_arm_caller as e522        # noqa: E402  the handed-onward call-site verdicts
import e523_handed_onward_reader as e523     # noqa: E402  the vocabulary of the second reader
import e524_reader_onward as e524            # noqa: E402  the upstream two-hop face

CARD = "E525-WHAT-HAPPENS-TO-THE-VALUES-THE-SECOND-READER-STILL-FORWARDS"
STUDY = "E525_onward_residue"
DATE_STAMP = "2026-11-08"
FACE_NAME = "onwardresidue_latest.json"
DATED_PREFIX = "ONWARDRESIDUE"

SELF_EXCLUDED = ("e525_", "run_e525", "_e525", "ONWARDRESIDUE", "onwardresidue_")

UPSTREAM_FACE = "results/state_tilt/readeronward_latest.json"
UPSTREAM_STUDY = e524.STUDY

# the two upstream chains this study opens
RESIDUE_CHAINS = (e524.C_LEFT_THE_TREE, e524.C_STILL_HANDED_FURTHER)

# ---------------------------------------------------------------- boundaries
B_PROCESS_EXIT = "the_process_exit_status"
B_EXTERNAL_LIBRARY = "an_imported_function_outside_this_corpus"
B_SELF_RECURSION = "the_same_function_again_so_the_chain_closes_inside_one_body"
B_NAMED_IN_REPO_FUNCTION = "another_named_function_in_this_corpus"
B_OUT_OF_REACH_FORM = "a_container_or_hand_on_form_this_scan_does_not_follow"
B_UNRESOLVED_NAME = "a_name_this_corpus_never_resolves"

BOUNDARY_VOCAB = (B_PROCESS_EXIT, B_EXTERNAL_LIBRARY, B_SELF_RECURSION,
                  B_NAMED_IN_REPO_FUNCTION, B_OUT_OF_REACH_FORM, B_UNRESOLVED_NAME)
NAMED_BOUNDARIES = (B_PROCESS_EXIT, B_EXTERNAL_LIBRARY, B_SELF_RECURSION,
                    B_NAMED_IN_REPO_FUNCTION)
UNMEASURED_BOUNDARIES = (B_OUT_OF_REACH_FORM, B_UNRESOLVED_NAME)

PROCESS_EXIT_LAST = ("exit", "quit", "_exit", "SystemExit")
PROCESS_EXIT_MODULES = ("sys", "os", "")

V_LEFT_TREE_IS_ENTIRELY_THE_PROCESS_EXIT = (
    "every_value_E524_said_left_the_corpus_at_the_second_hop_is_the_process_exit_status_and_not_a_"
    "library_boundary")
V_LEFT_TREE_MIXES_NAMED_BOUNDARIES = \
    "the_values_that_left_the_corpus_at_the_second_hop_cross_more_than_one_kind_of_boundary"
V_EMPTY = "the_upstream_face_carries_no_second_hop_residue"
VERDICT_VOCAB = (V_LEFT_TREE_IS_ENTIRELY_THE_PROCESS_EXIT, V_LEFT_TREE_MIXES_NAMED_BOUNDARIES,
                 V_EMPTY)


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
    """The E524 rows whose chain is a name for a hole, not an answer."""
    rows = []
    for row in face.get("sites") or []:
        if row.get("chain") not in RESIDUE_CHAINS:
            continue
        rec = {k: row.get(k) for k in (
            "source", "line", "call_expression", "callee", "callee_module", "callee_line",
            "enclosing_function", "reach", "binding", "bound_name", "read_kind",
            "first_read_line", "first_read_expression", "form", "receiver_kind", "verdict",
            "reader_function", "reader_module", "chain", "deepest_unguarded_depth",
            "second_readers_total", "second_readers_guarded", "second_readers_unguarded",
            "second_readers_handed_further", "second_readers_unresolved",
            "second_readers_left_the_tree", "second_readers_never_load")}
        rows.append(rec)
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


# ------------------------------------------------------------------ second-hop parcels
def residue_parcels(trees, rows, all_sites):
    """Follow the same second hop E524 followed, and keep every parcel tied to its owner row."""
    _out, second_rows, followed = e524.second_hop(trees, all_sites)
    by_owner = {}
    for s in second_rows:
        by_owner.setdefault((s.get("callee_module"), s.get("callee")), []).append(s)

    wanted = {
        e524.C_LEFT_THE_TREE: lambda v: v == e523.R_ARGUMENT_TO_AN_EXTERNAL_CALLEE,
        e524.C_STILL_HANDED_FURTHER: lambda v: v in (e523.R_STORED, e523.R_FORM_NOT_FOLLOWED),
    }
    out = []
    for row in rows:
        parcels = by_owner.get((row.get("reader_module"), row.get("reader_function")), [])
        keep = wanted[row.get("chain")]
        rec = dict(row)
        kept = []
        for parcel in parcels:
            item = dict(parcel)
            item["matches_the_chain"] = bool(keep(parcel.get("verdict")))
            kept.append(item)
        rec["residue_parcels"] = kept
        rec["parcels_in_bucket"] = len(parcels)
        out.append(rec)
    return out, followed


# ------------------------------------------------------------------ boundary resolution from source
def _dotted(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _dotted(node.value)
        return ("%s.%s" % (base, node.attr)) if base else None
    if isinstance(node, ast.Call):
        return _dotted(node.func)
    if isinstance(node, ast.Subscript):
        return _dotted(node.value)
    return None


def _call_names_on_line(tree, line):
    names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            start = getattr(node, "lineno", None)
            end = getattr(node, "end_lineno", start) or start
            if start is None:
                continue
            if start <= line <= end:
                dotted = _dotted(node.func)
                if dotted:
                    names.append(dotted)
    return names


def _import_map(tree):
    mapping = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mapping[alias.asname or alias.name.split(".")[0]] = alias.name
        elif isinstance(node, ast.ImportFrom):
            if node.module and not node.level:
                for alias in node.names:
                    mapping[alias.asname or alias.name] = node.module
    return mapping


def _external_library(dotted, imports):
    base = dotted.split(".")[0]
    module = imports.get(base)
    if not module:
        return None
    if module.split(".")[0] in getattr(sys, "stdlib_module_names", ()):  # 3.10+
        return module
    if module.split(".")[0] in ("os", "sys", "json", "re", "io", "ast"):
        return module
    return module if not module.endswith(".py") else None


def classify(parcel, tree):
    """Name the boundary the parcel's value crosses, from the cited source line itself."""
    names = _call_names_on_line(tree, parcel.get("line") or 0)
    reader = parcel.get("reader_function") or ""
    reader_last = reader.split(".")[-1]
    hit = next((n for n in names if n == reader or n.split(".")[-1] == reader_last), None)
    if hit is not None:
        last = hit.split(".")[-1]
        prefix = hit.split(".")[0] if "." in hit else ""
        if last in PROCESS_EXIT_LAST and prefix in PROCESS_EXIT_MODULES:
            return B_PROCESS_EXIT, hit, None
    if parcel.get("verdict") in (e523.R_STORED, e523.R_FORM_NOT_FOLLOWED):
        return B_OUT_OF_REACH_FORM, (parcel.get("reader_function") or "the_container"), None
    enclosing = parcel.get("enclosing_function")
    if enclosing and parcel.get("callee") == enclosing \
            and (parcel.get("callee_module") or "") == parcel.get("source"):
        return B_SELF_RECURSION, parcel["callee"], parcel["callee_module"]
    callee_module = parcel.get("callee_module") or ""
    if callee_module.endswith(".py"):
        return B_NAMED_IN_REPO_FUNCTION, parcel.get("callee"), callee_module
    if hit is not None:
        module = _external_library(hit, _import_map(tree))
        if module:
            return B_EXTERNAL_LIBRARY, hit, module
    if reader and not reader.endswith(".py") and "." not in reader:
        return B_UNRESOLVED_NAME, reader, None
    return B_UNRESOLVED_NAME, (hit or reader or None), None


def tree_index(root=None, rels=None):
    """Parse only the files the rows cite -- this is what makes `check` fast."""
    index, failed = {}, []
    for rel in sorted(set(rels or [])):
        try:
            index[rel] = ast.parse(e515._src(rel, root or ROOT))
        except (SyntaxError, OSError, UnicodeDecodeError, ValueError):
            failed.append(rel)
    return index, failed


def resolve_rows(rows, index):
    for row in rows:
        for parcel in row.get("residue_parcels") or []:
            tree = index.get(parcel.get("source"))
            if tree is None:
                parcel["boundary"], parcel["boundary_name"], parcel["boundary_module"] = \
                    B_UNRESOLVED_NAME, None, None
                parcel["boundary_evidence"] = "the_source_did_not_parse"
                continue
            klass, name, module = classify(parcel, tree)
            parcel["boundary"] = klass
            parcel["boundary_name"] = name
            parcel["boundary_module"] = module
            parcel["boundary_evidence"] = "line_%s_calls_%r" % (parcel.get("line"), name)
        parcels = row.get("residue_parcels") or []
        row["boundary_class"] = next((p.get("boundary") for p in parcels
                                      if p.get("matches_the_chain")), None)
    return rows


# ------------------------------------------------------------------ face
def _count(records, key, vocab):
    got = {k: 0 for k in vocab}
    for rec in records:
        value = rec.get(key)
        if value in got:
            got[value] += 1
    return got


def _by_chain_class(rows, chain):
    return _count([r for r in rows if r.get("chain") == chain], "boundary_class",
                  BOUNDARY_VOCAB)


def _unique_parcels(rows):
    """One physical second-hop call is one parcel, even when several rows share its owner."""
    seen = {}
    for row in rows:
        for parcel in row.get("residue_parcels") or []:
            key = (parcel.get("source"), parcel.get("line"), parcel.get("callee"))
            if key not in seen:
                item = dict(parcel)
                item["rows_that_share_this_parcel"] = 0
                seen[key] = item
            seen[key]["rows_that_share_this_parcel"] += 1
    return list(seen.values())


def _summary(rows, sources, failures, population_size, parcels_followed):
    parcels = _unique_parcels(rows)
    by_boundary = _count(rows, "boundary_class", BOUNDARY_VOCAB)
    return {
        "sources_read": sources,
        "parse_failures": len(failures),
        "sites_in_population": population_size,
        "sites_followed": len(rows),
        "second_hop_sites_followed": parcels_followed,
        "sites_from_left_the_tree": len([r for r in rows if r.get("chain") == e524.C_LEFT_THE_TREE]),
        "sites_from_still_forwarded": len([r for r in rows
                                           if r.get("chain") == e524.C_STILL_HANDED_FURTHER]),
        "sites_by_boundary": by_boundary,
        "sites_by_boundary_for_left_the_tree": _by_chain_class(rows, e524.C_LEFT_THE_TREE),
        "sites_by_boundary_for_still_forwarded":
            _by_chain_class(rows, e524.C_STILL_HANDED_FURTHER),
        "sites_whose_residue_ends_in_a_named_boundary":
            len([r for r in rows if r.get("boundary_class") in NAMED_BOUNDARIES]),
        "sites_whose_residue_stays_unmeasured":
            len([r for r in rows if r.get("boundary_class") in UNMEASURED_BOUNDARIES]),
        "sites_that_are_the_process_exit_status":
            len([r for r in rows if r.get("boundary_class") == B_PROCESS_EXIT]),
        "left_tree_sites_that_are_the_process_exit_status":
            len([r for r in rows if r.get("chain") == e524.C_LEFT_THE_TREE
                 and r.get("boundary_class") == B_PROCESS_EXIT]),
        "still_forwarded_sites_that_stop_at_a_container_or_unfollowed_form":
            len([r for r in rows if r.get("chain") == e524.C_STILL_HANDED_FURTHER
                 and r.get("boundary_class") == B_OUT_OF_REACH_FORM]),
        "parcels_examined": len(parcels),
        "parcels_matching_the_chain": len([p for p in parcels if p.get("matches_the_chain")]),
        "parcels_outside_the_matching_form":
            len([p for p in parcels if not p.get("matches_the_chain")]),
        "parcels_by_boundary": _count(parcels, "boundary", BOUNDARY_VOCAB),
        "parcels_that_return_into_the_same_function":
            len([p for p in parcels if p.get("boundary") == B_SELF_RECURSION]),
        "parcels_shared_by_more_than_one_row":
            len([p for p in parcels if (p.get("rows_that_share_this_parcel") or 0) > 1]),
        "rows_that_publish_no_boundary": len([r for r in rows if not r.get("boundary_class")]),
    }


def _verdict(summary):
    if not summary["sites_followed"]:
        return V_EMPTY
    left = summary["sites_from_left_the_tree"]
    if not left:
        return V_EMPTY
    if summary["left_tree_sites_that_are_the_process_exit_status"] == left:
        return V_LEFT_TREE_IS_ENTIRELY_THE_PROCESS_EXIT
    return V_LEFT_TREE_MIXES_NAMED_BOUNDARIES


def build(root=None, write=True, rows=None, sources=None, failures=None,
          upstream_sha=None, parcels_followed=0, population_size=None):
    root = root or ROOT
    if rows is None:
        face, sha = load_upstream(root)
        rows_in = population(face)
        all_sites = e524.population(face)
        trees, failed = parse(corpus_rels(root), root)
        rows, parcels_followed = residue_parcels(trees, rows_in, all_sites)
        index, _index_failed = tree_index(root, sorted(
            {r.get("source") for r in rows if r.get("source")} |
            {p.get("source") for r in rows
             for p in (r.get("residue_parcels") or []) if p.get("source")}))
        resolve_rows(rows, index)
        sources = len(trees) if sources is None else sources
        failures = failed if failures is None else failures
        upstream_sha = upstream_sha or sha
        population_size = len(rows_in) if population_size is None else population_size
    summary = _summary(rows, sources or 0, failures or [], population_size or len(rows),
                       parcels_followed)
    face = {
        "study": STUDY,
        "card": CARD,
        "title": "what happens to the values the second reader still forwards",
        "generated": _now(),
        "evidence_cutoff": DATE_STAMP,
        "population_source": ("%s::population() -- the E524 rows whose chain is a name for a hole "
                              "(`left the tree` / `still handed onward`)" % os.path.basename(__file__)),
        "upstream_face": UPSTREAM_FACE,
        "upstream_study": UPSTREAM_STUDY,
        "upstream_face_sha256": upstream_sha,
        "method_limits": [
            "'left the tree' is E523's name for a second-hop callee outside the corpus; this study "
            "re-reads the receiving call on its own line, so a `sys.exit(main())` entry point is "
            "published as the process exit, not as a library boundary",
            "a value stored into a container is published as an unfollowed form, never as a reader "
            "this scan reached",
            "the boundary is named from the cited source line only; a line that does not parse is "
            "published as an unresolved name with that evidence, not assumed",
            "the two upstream classes stay separate in every tally: a left-the-tree row and a "
            "still-forwarded row are never added into one 'residue resolved' number",
            "several rows can share one physical second-hop parcel (one function's return arm read "
            "by several first readers); the parcel tallies are de-duplicated on "
            "(source, line, callee) and every parcel publishes rows_that_share_this_parcel",
            "nothing is executed and no source is rewritten",
            "sources_read and the parcel count are a snapshot of a live tree that other lanes "
            "write to; they are published but not gated, while every boundary class is re-derived",
        ],
        "summary": summary,
        "verdict": _verdict(summary),
        "verdict_vocab": list(VERDICT_VOCAB),
        "boundary_vocab": list(BOUNDARY_VOCAB),
        "named_boundaries": list(NAMED_BOUNDARIES),
        "unmeasured_boundaries": list(UNMEASURED_BOUNDARIES),
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
                "method_limits", "parse_failures", "boundary_vocab"):
        if key not in face:
            bad.append("the face does not publish %s" % key)
    if face.get("study") != STUDY:
        bad.append("the face is not this study")
    if not str(face.get("population_source") or "").startswith("e525_onward_residue.py::population()"):
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
        bad.append("the face follows %d of the %d upstream residue sites"
                   % (len(rows), population_size))
    by_boundary = _count(rows, "boundary_class", BOUNDARY_VOCAB)
    if by_boundary != (summary.get("sites_by_boundary") or {}):
        bad.append("the per-boundary counts do not re-derive")
    if sum(by_boundary.values()) != len(rows):
        bad.append("the per-boundary classes do not cover every row")
    for chain, key in ((e524.C_LEFT_THE_TREE, "sites_by_boundary_for_left_the_tree"),
                       (e524.C_STILL_HANDED_FURTHER, "sites_by_boundary_for_still_forwarded")):
        if _by_chain_class(rows, chain) != (summary.get(key) or {}):
            bad.append("the per-boundary counts for %s do not re-derive" % chain)
    if summary.get("sites_from_left_the_tree") != \
            len([r for r in rows if r.get("chain") == e524.C_LEFT_THE_TREE]):
        bad.append("the left-the-tree count does not re-derive")
    if summary.get("sites_from_still_forwarded") != \
            len([r for r in rows if r.get("chain") == e524.C_STILL_HANDED_FURTHER]):
        bad.append("the still-forwarded count does not re-derive")
    named = len([r for r in rows if r.get("boundary_class") in NAMED_BOUNDARIES])
    if summary.get("sites_whose_residue_ends_in_a_named_boundary") != named:
        bad.append("the named-boundary count does not re-derive")
    unmeasured = len([r for r in rows if r.get("boundary_class") in UNMEASURED_BOUNDARIES])
    if summary.get("sites_whose_residue_stays_unmeasured") != unmeasured:
        bad.append("the unmeasured count does not re-derive")
    parcels = _unique_parcels(rows)
    if summary.get("parcels_examined") != len(parcels):
        bad.append("the parcel count does not re-derive")
    if summary.get("parcels_matching_the_chain") != \
            len([p for p in parcels if p.get("matches_the_chain")]):
        bad.append("the chain-matching parcel count does not re-derive")
    if _count(parcels, "boundary", BOUNDARY_VOCAB) != (summary.get("parcels_by_boundary") or {}):
        bad.append("the per-parcel boundary counts do not re-derive")
    for row in rows:
        if row.get("chain") not in RESIDUE_CHAINS:
            bad.append("row %s:%s carries an upstream chain this study does not open"
                       % (row.get("source"), row.get("line")))
        if not row.get("boundary_class"):
            bad.append("row %s:%s publishes no boundary class"
                       % (row.get("source"), row.get("line")))
            continue
        if row["boundary_class"] not in BOUNDARY_VOCAB:
            bad.append("row %s:%s carries a boundary outside the vocabulary"
                       % (row.get("source"), row.get("line")))
        parcels = row.get("residue_parcels") or []
        matching = [p for p in parcels if p.get("matches_the_chain")]
        if not parcels:
            bad.append("row %s:%s publishes a boundary with no parcel behind it"
                       % (row.get("source"), row.get("line")))
            continue
        if not matching:
            bad.append("row %s:%s publishes a boundary with no parcel that matches its upstream "
                       "chain" % (row.get("source"), row.get("line")))
            continue
        if matching[0].get("boundary") != row["boundary_class"]:
            bad.append("row %s:%s boundary disagrees with its first chain-matching parcel"
                       % (row.get("source"), row.get("line")))
        for parcel in parcels:
            if parcel.get("boundary") not in BOUNDARY_VOCAB:
                bad.append("parcel %s:%s carries no boundary"
                           % (parcel.get("source"), parcel.get("line")))
    if face.get("verdict") == V_LEFT_TREE_IS_ENTIRELY_THE_PROCESS_EXIT \
            and summary.get("left_tree_sites_that_are_the_process_exit_status") != \
            summary.get("sites_from_left_the_tree"):
        bad.append("the process-exit verdict does not match the left-the-tree tally")
    upstream = face.get("upstream_face")
    if upstream:
        path = os.path.join(root or ROOT, upstream)
        if not os.path.isfile(path):
            bad.append("the upstream face is not on disk at %s" % upstream)
        elif _sha256_file(path) != face.get("upstream_face_sha256"):
            bad.append("the upstream face changed since this face was built -- rebuild")
    return bad


def regate_boundaries(face, root=None):
    """Re-read every cited line and refuse a face whose boundary drifts from the source."""
    bad = []
    parcels = [(i, p) for i, row in enumerate(face.get("sites") or [])
               for p in (row.get("residue_parcels") or [])]
    index, failed = tree_index(root, [p.get("source") for _i, p in parcels])
    if failed:
        print("  note: %d cited source(s) no longer parse: %r" % (len(failed), failed[:4]))
    for i, parcel in parcels:
        tree = index.get(parcel.get("source"))
        if tree is None:
            continue
        klass, _name, _module = classify(parcel, tree)
        if klass != parcel.get("boundary"):
            bad.append("parcel %s:%s boundary drifts (%s -> %s)"
                       % (parcel.get("source"), parcel.get("line"), parcel.get("boundary"), klass))
    for row in face.get("sites") or []:
        parcels = row.get("residue_parcels") or []
        matching = [p for p in parcels if p.get("matches_the_chain")]
        if matching and matching[0].get("boundary") != row.get("boundary_class"):
            bad.append("row %s:%s boundary drifts from its first chain-matching parcel"
                       % (row.get("source"), row.get("line")))
    return bad


def check(face=None, root=None):
    face = face or load_face(root)
    bad = face_problems(face, root)
    bad.extend(regate_boundaries(face, root))
    print("E525 check: %d problem(s)" % len(bad))
    for line in bad[:20]:
        print("  - %s" % line)
    return 1 if bad else 0


def verify(root=None):
    """Re-derive from the whole tree and gate.  Corpus size is a live-tree snapshot."""
    published = load_face(root)
    fresh = build(root=root, write=False)
    bad = face_problems(published, root)
    bad.extend(regate_boundaries(published, root))
    if fresh["verdict"] != published["verdict"]:
        bad.append("the verdict drifts when re-derived")
    volatile = ("sources_read", "parse_failures", "second_hop_sites_followed",
                "parcels_examined", "parcels_by_boundary",
                "parcels_that_return_into_the_same_function")
    trimmed = {k: v for k, v in fresh["summary"].items() if k not in volatile}
    pinned = {k: v for k, v in published["summary"].items() if k not in volatile}
    if json.dumps(trimmed, sort_keys=True) != json.dumps(pinned, sort_keys=True):
        moved = sorted(k for k in set(trimmed) | set(pinned) if trimmed.get(k) != pinned.get(k))
        bad.append("the summary drifts when re-derived: %r" % moved[:6])
    for key in volatile:
        if fresh["summary"].get(key) != published["summary"].get(key):
            print("  note: %s moved %r -> %r (live tree, not gated)"
                  % (key, published["summary"].get(key), fresh["summary"].get(key)))
    print("E525 verify: %d problem(s)" % len(bad))
    for line in bad[:20]:
        print("  - %s" % line)
    return 1 if bad else 0


# ------------------------------------------------------------------ selftest
FIXTURE = '''
import sys


def build(path):
    if not path:
        return None
    return path.strip()


def guard_and_read(path):
    value = build(path)
    if not value:
        return 0
    return value.strip()


def forward_again(path):
    value = build(path)
    return value.strip()


def container_of_values(path):
    value = build(path)
    return [value, value]


def same_function_again(expr, depth):
    if depth > 3:
        return None
    return same_function_again(expr, depth + 1)


def another_named_function(path):
    value = build(path)
    return helper(value)


def helper(payload):
    return payload


def unbound_callback(path, callback):
    value = build(path)
    return callback(value)


def main(callback=None):
    forward_again("a")
    container_of_values("b")
    same_function_again("c", 0)
    another_named_function("d")
    unbound_callback("e", callback)
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''


def _fixture_parcel(kind, callee, enclosing, line_hint, text, verdict=None):
    lines = text.splitlines()
    line = next(i + 1 for i, ln in enumerate(lines) if line_hint in ln)
    return {
        "source": "scripts/fixture_mod.py",
        "line": line,
        "callee": callee,
        "callee_module": "scripts/fixture_mod.py",
        "enclosing_function": enclosing,
        "reader_function": None,
        "reader_module": None,
        "verdict": verdict or e523.R_ARGUMENT_TO_AN_EXTERNAL_CALLEE,
        "kind": kind,
    }


def selftest():
    bad = []
    tmp = tempfile.mkdtemp(prefix="e525_")
    try:
        os.makedirs(os.path.join(tmp, "scripts"))
        path = os.path.join(tmp, "scripts", "fixture_mod.py")
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(FIXTURE)
        index, failed = tree_index(tmp, ["scripts/fixture_mod.py"])
        if failed or not index:
            bad.append("the fixture corpus did not parse: %r" % failed)
            raise RuntimeError("fixture")
        tree = index["scripts/fixture_mod.py"]

        def expect(label, parcel, want):
            got = classify(parcel, tree)[0]
            if got != want:
                bad.append("%s: expected %s, saw %s" % (label, want, got))

        expect("a sys.exit entry point", {"line": FIXTURE.splitlines().index(
            "    sys.exit(main())") + 1, "reader_function": "sys.exit", "verdict":
            e523.R_ARGUMENT_TO_AN_EXTERNAL_CALLEE, "callee": "main", "callee_module":
            "scripts/fixture_mod.py", "source": "scripts/fixture_mod.py",
            "enclosing_function": None}, B_PROCESS_EXIT)
        expect("a callback the corpus never binds", {
            "line": next(i + 1 for i, ln in enumerate(FIXTURE.splitlines())
                         if "callback(value)" in ln),
            "reader_function": "callback", "verdict": e523.R_ARGUMENT_TO_AN_EXTERNAL_CALLEE,
            "callee": "callback", "callee_module": None, "source": "scripts/fixture_mod.py",
            "enclosing_function": "unbound_callback"}, B_UNRESOLVED_NAME)
        expect("a value stored into a container", {
            "line": next(i + 1 for i, ln in enumerate(FIXTURE.splitlines())
                         if "build(path)" in ln and "container" not in ln),
            "reader_function": None, "verdict": e523.R_STORED, "callee": "build",
            "callee_module": "scripts/fixture_mod.py", "source": "scripts/fixture_mod.py",
            "enclosing_function": "container_of_values"}, B_OUT_OF_REACH_FORM)
        expect("a self-recursive forward", {
            "line": next(i + 1 for i, ln in enumerate(FIXTURE.splitlines())
                         if "same_function_again(expr, depth + 1)" in ln),
            "reader_function": None, "verdict": e523.R_ARGUMENT_TO_AN_EXTERNAL_CALLEE,
            "callee": "same_function_again", "callee_module": "scripts/fixture_mod.py",
            "source": "scripts/fixture_mod.py",
            "enclosing_function": "same_function_again"}, B_SELF_RECURSION)
        expect("a forward to another named function", {
            "line": next(i + 1 for i, ln in enumerate(FIXTURE.splitlines())
                         if "return helper(value)" in ln),
            "reader_function": "helper", "verdict": e523.R_ARGUMENT_TO_AN_EXTERNAL_CALLEE,
            "callee": "helper", "callee_module": "scripts/fixture_mod.py",
            "source": "scripts/fixture_mod.py", "enclosing_function": "another_named_function"
        }, B_NAMED_IN_REPO_FUNCTION)

        # a fixture face built from the same rows must pass its own gate
        rows = []
        for label, parcel, chain in (
                ("exit", {"line": FIXTURE.splitlines().index("    sys.exit(main())") + 1,
                          "source": "scripts/fixture_mod.py", "reader_function": "sys.exit",
                          "reader_module": "scripts/fixture_mod.py", "verdict":
                          e523.R_ARGUMENT_TO_AN_EXTERNAL_CALLEE, "callee": "main",
                          "callee_module": "scripts/fixture_mod.py", "form": e523.F_RETURNED,
                          "enclosing_function": None}, e524.C_LEFT_THE_TREE),
                ("container", {"line": next(i + 1 for i, ln in enumerate(FIXTURE.splitlines())
                                            if "build(path)" in ln),
                               "source": "scripts/fixture_mod.py", "reader_function": "build",
                               "reader_module": "scripts/fixture_mod.py", "verdict": e523.R_STORED,
                               "callee": "build", "callee_module": "scripts/fixture_mod.py",
                               "form": e523.F_RETURNED, "enclosing_function":
                               "container_of_values"}, e524.C_STILL_HANDED_FURTHER)):
            row = {"source": parcel["source"], "line": parcel["line"], "chain": chain,
                   "form": parcel["form"], "verdict": e522.CT_HANDED,
                   "residue_parcels": [dict(parcel, matches_the_chain=True)]}
            rows.append(row)
        resolve_rows(rows, index)
        if rows[0]["boundary_class"] != B_PROCESS_EXIT:
            bad.append("the fixture entry point is not published as the process exit")
        if rows[1]["boundary_class"] != B_OUT_OF_REACH_FORM:
            bad.append("the fixture container is not published as an unfollowed form")
        summary = _summary(rows, 1, [], len(rows), 2)
        if _verdict(summary) != V_LEFT_TREE_IS_ENTIRELY_THE_PROCESS_EXIT:
            bad.append("a fixture whose only left-the-tree row is sys.exit should say so, saw %r"
                       % _verdict(summary))
        empty = _summary([], 1, [], 0, 0)
        if _verdict(empty) != V_EMPTY:
            bad.append("an empty population is not reported as empty")

        os.makedirs(os.path.join(tmp, "results", "state_tilt"))
        up = os.path.join(ROOT, UPSTREAM_FACE)
        shutil.copyfile(up, os.path.join(tmp, "results", "state_tilt",
                                        os.path.basename(UPSTREAM_FACE)))
        face = build(root=tmp, write=False, rows=copy.deepcopy(rows), sources=1, failures=[],
                     upstream_sha=_sha256_file(up), parcels_followed=2, population_size=2)
        face["sites"][0]["boundary_class"] = B_PROCESS_EXIT
        if face_problems(face, tmp):
            bad.append("the fixture face is refused by its own gate: %r"
                       % face_problems(face, tmp)[:2])
        for doctor, why in (
            (lambda f: f.__setitem__("verdict", V_LEFT_TREE_MIXES_NAMED_BOUNDARIES),
             "a hand-written verdict"),
            (lambda f: f["summary"].__setitem__("sites_followed", 99),
             "an edited followed count"),
            (lambda f: f["sites"][0].__setitem__("boundary_class", B_EXTERNAL_LIBRARY),
             "a relabelled boundary on the entry point"),
            (lambda f: f["summary"].__setitem__("sites_from_left_the_tree", 0),
             "a zeroed left-the-tree count"),
            (lambda f: f["sites"][0]["residue_parcels"][0].__setitem__("boundary",
                                                                       B_EXTERNAL_LIBRARY),
             "a parcel whose boundary contradicts its own line"),
            (lambda f: f.__setitem__("upstream_face_sha256", "0" * 64),
             "an edited upstream pin"),
            (lambda f: f["sites"][1]["residue_parcels"].pop(),
             "a row whose parcel list was emptied"),
        ):
            hurt = copy.deepcopy(face)
            doctor(hurt)
            if not (face_problems(hurt, tmp) or regate_boundaries(hurt, tmp)):
                bad.append("%s survived the gate" % why)
    except RuntimeError:
        pass
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if bad:
        print("E525 selftest: %d problem(s)" % len(bad))
        for line in bad[:20]:
            print("  - %s" % line)
        return 1
    print("E525 selftest: clean")
    return 0


# ------------------------------------------------------------------ entry
def run():
    face = build()
    s = face["summary"]
    print("E525 run: opened %r residue sites in %r sources (%r parse failures), "
          "%r second-hop parcels"
          % (s["sites_followed"], s["sources_read"], s["parse_failures"],
             s["second_hop_sites_followed"]))
    print("  from left-the-tree %r | from still-forwarded %r"
          % (s["sites_from_left_the_tree"], s["sites_from_still_forwarded"]))
    print("  boundaries: process exit %r | external library %r | self recursion %r | "
          "another in-corpus function %r | unfollowed form %r | unresolved name %r"
          % (s["sites_by_boundary"][B_PROCESS_EXIT],
             s["sites_by_boundary"][B_EXTERNAL_LIBRARY],
             s["sites_by_boundary"][B_SELF_RECURSION],
             s["sites_by_boundary"][B_NAMED_IN_REPO_FUNCTION],
             s["sites_by_boundary"][B_OUT_OF_REACH_FORM],
             s["sites_by_boundary"][B_UNRESOLVED_NAME]))
    print("  named %r | still unmeasured %r | parcels returning into the same function %r"
          % (s["sites_whose_residue_ends_in_a_named_boundary"],
             s["sites_whose_residue_stays_unmeasured"],
             s["parcels_that_return_into_the_same_function"]))
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