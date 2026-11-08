"""E534 (r1561 bm-b): does a depth-cap null, read by a caller that cannot tell it apart,
reach a published payload as the claim that the thing is not there?

E529 (results/state_tilt/depthcapnull_latest.json) published 12 depth-cap arms that return a
null sentinel.  Eight of them have readers that never test the value and two test it against the
same null, so no reader can separate "the recursion hit its cap" from "the thing is not there".

But "read without a guard" is still a statement about a call site, not about a publication.  A
sentinel that is bound and dropped, or that only feeds a local branch, never becomes a fact
anyone reads.  This study follows each such value out of its reader:

  * read -> bind -> terminal: the value is discarded, bound and never read, only tested,
    carried into a named field of an assembled dict, counted (len/sum/any/all), folded into a
    sentence, handed to another call, or returned out of the reader
  * when it is carried into a field the key is published, and the reader is asked whether it
    writes a payload at all -- a field assembled in a function that never dumps is not a
    publication

Every arm publishes a chain class and the counts behind it.  "Silently read" never stands in for
"published as a fact", and a chain this scan cannot follow is its own class, not a zero.

    python scripts/e534_cap_to_payload.py run        # build + write the face
    python scripts/e534_cap_to_payload.py check      # gate the published face (fast)
    python scripts/e534_cap_to_payload.py verify     # re-derive from the tree and gate
    python scripts/e534_cap_to_payload.py selftest   # fixture corpus + doctored faces
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
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e529_depth_cap_null as e529          # noqa: E402  corpus, parse, call naming, null spellings

CARD = ("E534-WHICH-DEPTH-CAP-NULL-THAT-NO-READER-TESTS-REACHES-A-PUBLISHED-PAYLOAD-"
        "AS-A-CLAIM-THAT-THE-THING-IS-NOT-THERE")
STUDY = "E534_cap_to_payload"
DATE_STAMP = "2026-11-08"
FACE_NAME = "captopayload_latest.json"
DATED_PREFIX = "CAPTOPAYLOAD"

SELF_EXCLUDED = ("e534_", "run_e534", "_e534", "CAPTOPAYLOAD", "captopayload_")

UPSTREAM_FACE = "results/state_tilt/depthcapnull_latest.json"
UPSTREAM_STUDY = e529.STUDY

# the two reader classes E529 said cannot separate the cap from the absence
READER_CANNOT_TELL = (
    e529.D_NO_TEST,
    e529.D_SAME_SENTINEL,
)

# ---------------------------------------------------------------- chain vocabulary
C_PAYLOAD_FIELD = "the_value_is_carried_into_a_named_field_of_a_payload_this_reader_writes"
C_PAYLOAD_FIELD_UNWRITTEN = "the_value_is_carried_into_a_named_field_but_the_reader_writes_no_payload"
C_PAYLOAD_BODY = "the_value_is_the_body_of_a_payload_this_reader_writes_so_no_key_names_it"
C_PAYLOAD_BODY_UNWRITTEN = "the_value_is_assembled_as_a_payload_body_but_the_reader_writes_no_payload"
C_COUNTED = "the_value_becomes_a_counted_quantity"
C_SENTENCE = "the_value_is_folded_into_a_sentence_a_human_reads"
C_FORWARDED = "the_value_leaves_the_reader_as_an_argument_or_a_return"
C_TESTED = "the_reader_tests_the_value_narrowly_but_cannot_still_separate_the_cap"
C_DISCARDED = "the_reader_discards_the_value"
C_BOUND_NEVER_READ = "the_value_is_bound_and_never_read"
C_STOPS_ELSEWHERE = "the_value_stops_inside_the_reader"
C_UNRESOLVED = "the_chain_could_not_be_followed_statically"
CHAIN_VOCAB = (C_PAYLOAD_FIELD, C_PAYLOAD_BODY, C_PAYLOAD_FIELD_UNWRITTEN,
               C_PAYLOAD_BODY_UNWRITTEN, C_COUNTED, C_SENTENCE, C_FORWARDED, C_TESTED,
               C_DISCARDED, C_BOUND_NEVER_READ, C_STOPS_ELSEWHERE, C_UNRESOLVED)

# precedence: the most load-bearing outcome a row carries decides its chain class
_PRIMARY = (C_PAYLOAD_FIELD, C_PAYLOAD_BODY, C_SENTENCE, C_COUNTED,
            C_PAYLOAD_FIELD_UNWRITTEN, C_PAYLOAD_BODY_UNWRITTEN, C_FORWARDED, C_TESTED,
            C_BOUND_NEVER_READ, C_DISCARDED, C_STOPS_ELSEWHERE, C_UNRESOLVED)

V_ABSENCE_IS_PUBLISHED = \
    "a_cap_null_reaches_a_published_payload_a_sentence_or_a_count_so_the_cap_can_be_read_as_absence"
V_ONLY_ASSEMBLED = \
    "cap_nulls_reach_named_fields_but_no_reader_in_the_population_writes_a_payload"
V_NEVER_LEAVES_THE_READER = \
    "every_cap_null_stops_inside_its_reader_so_silently_read_is_not_published_as_a_fact"
V_EMPTY = "the_upstream_face_carries_no_arm_in_the_two_reader_classes"
VERDICT_VOCAB = (V_ABSENCE_IS_PUBLISHED, V_ONLY_ASSEMBLED, V_NEVER_LEAVES_THE_READER, V_EMPTY)

USE_VOCAB = e529.USE_VOCAB

# funcs whose argument is being written out
WRITE_FUNCS = {"dump", "dumps", "write", "writelines", "writestr", "write_face"}
# funcs that turn a value into a counted quantity
COUNT_FUNCS = {"len", "sum", "any", "all", "count"}
# dict keys whose value a reader takes as a verdict/answer sentence
SENTENCE_KEYS = {"verdict", "answer", "sentence", "why", "reason", "note", "conclusion",
                 "summary_text", "explain", "detail", "verdict_text"}


def _now():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def _sha256_file(path):
    h = hashlib.sha256()
    try:
        with io.open(path, "rb") as fh:
            for block in iter(lambda: fh.read(1 << 20), b""):
                h.update(block)
    except OSError:
        return None
    return h.hexdigest()


# ------------------------------------------------------------------ upstream population
def load_upstream(root=None):
    path = os.path.join(root or ROOT, UPSTREAM_FACE)
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh), _sha256_file(path)


def population(face):
    """E529 arms in the two classes whose reader cannot separate the cap from an absence."""
    arms = []
    for arm in face.get("arms") or []:
        if arm.get("distinguish") not in READER_CANNOT_TELL:
            continue
        arms.append({k: arm.get(k) for k in (
            "module", "function", "counter", "cap", "cap_class", "sentinel", "distinguish",
            "dead_arm", "has_recursive_call", "lines", "call_site_count", "use_counts")})
    arms.sort(key=lambda a: (a["module"] or "", a["function"] or ""))
    return arms


def sites_for(face, arm):
    """The E529 call sites this arm owns: same module, not the recursive self-call."""
    out = []
    for site in face.get("call_sites") or []:
        if site.get("callee") != arm["function"]:
            continue
        if arm["module"] not in (site.get("attributed_modules") or []):
            continue
        if site.get("use") == e529.U_RECURSIVE:
            continue
        out.append({k: site.get(k) for k in (
            "module", "line", "callee", "caller", "use", "distinguish")})
    out.sort(key=lambda s: (s["module"] or "", s["line"] or 0))
    return out


# ------------------------------------------------------------------ the tree
def corpus_rels(root=None):
    return [rel for rel in e529.corpus_files(root) if not rel.startswith(SELF_EXCLUDED)]


def parse(rels, root=None):
    trees, failed = [], []
    for rel in rels:
        tree = e529._read_tree(rel, root or ROOT)
        if tree is None:
            failed.append(rel)
            continue
        trees.append((rel, tree))
    return trees, failed


def find_call(trees, module, line, callee, caller):
    """The call node E529 published, located by line, name and enclosing function."""
    for rel, tree in trees:
        if rel != module:
            continue
        parents = e529._parents(tree)
        hits = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if getattr(node, "lineno", None) != line:
                continue
            if e529._call_name(node) != callee:
                continue
            fn = e529._enclosing_function(node, parents, tree)
            hits.append((node, fn, parents))
        for node, fn, parents in hits:
            if caller is None or getattr(fn, "name", None) == caller:
                return node, fn, parents, tree
        if hits:
            return hits[0][0], hits[0][1], hits[0][2], tree
        return None, None, None, tree
    return None, None, None, None


def _writes_a_payload(fn):
    for node in ast.walk(fn):
        if isinstance(node, ast.Call):
            name = e529._call_name(node)
            if name in WRITE_FUNCS:
                return True
    return False


def _ancestors(node, parents):
    chain = []
    cur = parents.get(node)
    while cur is not None:
        chain.append(cur)
        if isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef)):
            break
        cur = parents.get(cur)
    return chain


def _key_of(subscript_ancestor):
    """The constant key an expression is written under, when that key is a literal."""
    sl = subscript_ancestor.slice
    if isinstance(sl, ast.Constant) and isinstance(sl.value, str):
        return sl.value
    return None


def _flow_from(node, parents):
    """Walk outward from one expression node: what does the reader do with this value?"""
    reached = set()
    keys = []
    cur = node
    for _ in range(40):
        par = parents.get(cur)
        if par is None:
            break
        if isinstance(par, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Module, ast.ClassDef)):
            break
        if isinstance(par, ast.Expr) and par.value is cur:
            reached.add(C_DISCARDED)
            break
        if isinstance(par, (ast.Assign, ast.AnnAssign)):
            break
        if isinstance(par, ast.Dict) and any(v is cur for v in par.values):
            idx = [i for i, v in enumerate(par.values) if v is cur][0]
            key_node = par.keys[idx] if idx < len(par.keys) else None
            key = key_node.value if isinstance(key_node, ast.Constant) \
                and isinstance(key_node.value, str) else None
            if key:
                keys.append(key)
            reached.add(C_SENTENCE if key in SENTENCE_KEYS else C_PAYLOAD_FIELD)
            break
        if isinstance(par, ast.Subscript) and isinstance(par.ctx, ast.Store) \
                and par.value is cur:
            key = _key_of(par)
            if key:
                keys.append(key)
            reached.add(C_SENTENCE if key in SENTENCE_KEYS else C_PAYLOAD_FIELD)
            break
        if isinstance(par, ast.JoinedStr):
            reached.add(C_SENTENCE)
            break
        if isinstance(par, ast.BinOp):
            other = par.right if par.left is cur else par.left
            if isinstance(par.op, ast.Add) and isinstance(other, ast.Constant) \
                    and isinstance(other.value, str):
                reached.add(C_SENTENCE)
                break
            if isinstance(par.op, ast.Mod) and isinstance(par.left, ast.Constant) \
                    and isinstance(par.left.value, str):
                reached.add(C_SENTENCE)
                break
        if isinstance(par, ast.Call):
            name = e529._call_name(par)
            args = list(par.args) + [k.value for k in par.keywords]
            if name in COUNT_FUNCS and any(a is cur for a in args):
                reached.add(C_COUNTED)
                break
            if name in WRITE_FUNCS and any(a is cur for a in args):
                reached.add(C_PAYLOAD_BODY)
                break
            if isinstance(par.func, ast.Attribute) and par.func.attr == "format" \
                    and par.func.value is cur:
                reached.add(C_SENTENCE)
                break
            if any(a is cur for a in args):
                reached.add(C_FORWARDED)
                break
        if isinstance(par, ast.Return) and par.value is cur:
            reached.add(C_FORWARDED)
            break
        if isinstance(par, (ast.Compare, ast.If, ast.While, ast.BoolOp, ast.UnaryOp)):
            reached.add(C_TESTED)
            break
        cur = par
    if not reached:
        reached.add(C_STOPS_ELSEWHERE)
    return reached, keys


def flow_of(fn, name, after_line, parents):
    """What the reader does with a value bound to `name` at/after `after_line`."""
    reached = set()
    keys = []
    if fn is None:
        return {C_UNRESOLVED}, keys
    # a later rebinding of the same name is a different value: stop the walk there
    rebind = None
    for node in ast.walk(fn):
        if not isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        if not any(isinstance(t, ast.Name) and t.id == name for t in targets):
            continue
        line = getattr(node, "lineno", 0)
        if line <= after_line:
            continue
        rebind = line if rebind is None else min(rebind, line)
    for node in ast.walk(fn):
        if not (isinstance(node, ast.Name) and node.id == name
                and isinstance(node.ctx, ast.Load)):
            continue
        line = getattr(node, "lineno", 0)
        if line <= after_line:
            continue
        if rebind is not None and line >= rebind:
            continue
        classes, found = _flow_from(node, parents)
        reached |= classes
        keys.extend(found)
    if not reached:
        reached.add(C_BOUND_NEVER_READ)
    return reached, sorted(set(keys))


def classify_site(trees, site, sentinel):
    """Follow one call site's returned value to its terminal class."""
    rec = dict(site)
    rec.update({"reader_function": site.get("caller"), "reader_writes_a_payload": None,
                "terminal_classes": [], "payload_keys": [], "chain": C_UNRESOLVED,
                "sentinel": sentinel})
    call, fn, parents, tree = find_call(trees, site["module"], site["line"],
                                        site["callee"], site.get("caller"))
    if call is None or tree is None:
        rec["chain"] = C_UNRESOLVED
        rec["terminal_classes"] = [C_UNRESOLVED]
        return rec
    writes = _writes_a_payload(fn) if fn is not None else None
    rec["reader_writes_a_payload"] = writes
    par = parents.get(call)
    bound = None
    if isinstance(par, ast.Assign):
        for t in par.targets:
            if isinstance(t, ast.Name):
                bound = t.id
                break
    elif isinstance(par, ast.AnnAssign) and isinstance(par.target, ast.Name):
        bound = par.target.id
    if bound is not None and fn is not None:
        reached, keys = flow_of(fn, bound, getattr(par, "lineno", 0), parents)
    else:
        reached, keys = _flow_from(call, parents)
    rec["payload_keys"] = keys
    if C_PAYLOAD_FIELD in reached and not writes:
        reached = (reached - {C_PAYLOAD_FIELD}) | {C_PAYLOAD_FIELD_UNWRITTEN}
    if C_PAYLOAD_BODY in reached and not writes:
        reached = (reached - {C_PAYLOAD_BODY}) | {C_PAYLOAD_BODY_UNWRITTEN}
    rec["terminal_classes"] = sorted(reached)
    rec["chain"] = C_UNRESOLVED
    for klass in _PRIMARY:
        if klass in reached:
            rec["chain"] = klass
            break
    return rec


def follow(trees, arms, face):
    rows = []
    for arm in arms:
        rec = {k: arm.get(k) for k in ("module", "function", "counter", "cap", "cap_class",
                                       "sentinel", "distinguish", "dead_arm",
                                       "has_recursive_call", "lines")}
        sites = sites_for(face, arm)
        traced = [classify_site(trees, s, arm.get("sentinel")) for s in sites]
        counts = {k: 0 for k in CHAIN_VOCAB}
        for t in traced:
            counts[t["chain"]] += 1
        rec["sites_total"] = len(traced)
        rec["sites_by_chain"] = counts
        rec["payload_keys"] = sorted({k for t in traced for k in (t["payload_keys"] or [])})
        rec["readers_that_write_a_payload"] = len([t for t in traced
                                                   if t.get("reader_writes_a_payload")])
        rec["chain"] = None
        for klass in _PRIMARY:
            if counts.get(klass):
                rec["chain"] = klass
                break
        if rec["chain"] is None:
            rec["chain"] = C_UNRESOLVED
        rec["sites"] = traced
        rows.append(rec)
    rows.sort(key=lambda r: (r["module"] or "", r["function"] or ""))
    return rows


# ------------------------------------------------------------------ face
def _count(records, key, vocab):
    got = {k: 0 for k in vocab}
    for rec in records:
        value = rec.get(key)
        if value in got:
            got[value] += 1
    return got


def _site_count(rows, klass):
    return sum((r.get("sites_by_chain") or {}).get(klass, 0) for r in rows)


def _summary(rows, sources, failures):
    by_chain = _count(rows, "chain", CHAIN_VOCAB)
    return {
        "sources_read": sources,
        "parse_failures": len(failures),
        "arms_in_population": len(rows),
        "arms_by_chain": by_chain,
        "call_sites_followed": sum(r.get("sites_total") or 0 for r in rows),
        "sites_by_chain": {k: _site_count(rows, k) for k in CHAIN_VOCAB},
        "arms_reaching_a_payload_field": by_chain[C_PAYLOAD_FIELD],
        "arms_reaching_a_payload_body": by_chain[C_PAYLOAD_BODY],
        "arms_reaching_a_sentence": by_chain[C_SENTENCE],
        "arms_reaching_a_count": by_chain[C_COUNTED],
        "arms_whose_field_is_never_written": by_chain[C_PAYLOAD_FIELD_UNWRITTEN],
        "arms_whose_body_is_never_written": by_chain[C_PAYLOAD_BODY_UNWRITTEN],
        "arms_that_stop_inside_the_reader": len([r for r in rows if r.get("chain") in
                                                 (C_DISCARDED, C_BOUND_NEVER_READ,
                                                  C_STOPS_ELSEWHERE, C_TESTED)]),
        "arms_whose_reader_tests_the_value_narrowly": len(
            [r for r in rows if (r.get("sites_by_chain") or {}).get(C_TESTED)]),
        "arms_e529_published_as_never_tested_that_do_test": sorted(
            "%s::%s" % (r.get("module"), r.get("function")) for r in rows
            if r.get("distinguish") == e529.D_NO_TEST
            and (r.get("sites_by_chain") or {}).get(C_TESTED)),
        "arms_by_e529_reader_class": _count(rows, "distinguish", READER_CANNOT_TELL),
        "arms_whose_value_leaves_by_a_call": by_chain[C_FORWARDED],
        "arms_unresolved": by_chain[C_UNRESOLVED],
        "payload_keys_named": sorted({k for r in rows for k in (r.get("payload_keys") or [])}),
        "rows_that_publish_no_chain_class": len([r for r in rows if not r.get("chain")]),
    }


def _verdict(summary):
    if not summary["arms_in_population"]:
        return V_EMPTY
    if summary["arms_reaching_a_payload_field"] or summary["arms_reaching_a_payload_body"] \
            or summary["arms_reaching_a_sentence"] or summary["arms_reaching_a_count"]:
        return V_ABSENCE_IS_PUBLISHED
    if summary["arms_whose_field_is_never_written"] or summary["arms_whose_body_is_never_written"]:
        return V_ONLY_ASSEMBLED
    return V_NEVER_LEAVES_THE_READER


def build(root=None, write=True, arms=None, rows=None, sources=None, failures=None,
          upstream_sha=None):
    root = root or ROOT
    if arms is None:
        face, sha = load_upstream(root)
        arms = population(face)
        upstream_sha = upstream_sha or sha
        trees, failed = parse(corpus_rels(root), root)
        rows = follow(trees, arms, face)
        sources = len(trees) if sources is None else sources
        failures = failed if failures is None else failures
    summary = _summary(rows, sources or 0, failures or [])
    face = {
        "study": STUDY,
        "card": CARD,
        "title": ("does a depth-cap null that no reader tests reach a published payload as the "
                  "claim that the thing is not there"),
        "generated": _now(),
        "evidence_cutoff": DATE_STAMP,
        "population_source": ("%s::population() -- the E529 arms whose reader cannot separate "
                              "the cap from the absence" % os.path.basename(__file__)),
        "upstream_face": UPSTREAM_FACE,
        "upstream_study": UPSTREAM_STUDY,
        "upstream_face_sha256": upstream_sha,
        "method_limits": [
            "one hop out of the reader: a value handed to another call or returned is published "
            "as that class and the next consumer is not followed",
            "a field is only called a publication when the same reader function contains a "
            "write call; a dict assembled and never dumped is its own class",
            "the reader's payload keys are the literal keys the value is written under; a "
            "computed key is not named and does not count as a named field",
            "a bound value is followed by NAME inside its reader and the walk stops at "
            "a later rebinding of that name; a load of the rebound value is therefore "
            "never counted as a read of the sentinel",
            "the population is E529's two reader classes verbatim; a site E529 could not "
            "attribute to the defining module is out of scope here too",
            "nothing is executed and no source is rewritten",
            "sources_read and parse_failures are a snapshot of a live tree other lanes write to; "
            "they are published but not gated, while every chain class is re-derived",
        ],
        "summary": summary,
        "verdict": _verdict(summary),
        "verdict_vocab": list(VERDICT_VOCAB),
        "chain_vocab": list(CHAIN_VOCAB),
        "use_vocab": list(USE_VOCAB),
        "arms": rows,
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


def face_problems(face, root=None):
    bad = []
    for key in ("study", "card", "generated", "evidence_cutoff", "population_source",
                "upstream_face", "upstream_face_sha256", "summary", "verdict", "arms",
                "method_limits", "parse_failures"):
        if key not in face:
            bad.append("the face does not publish %s" % key)
    if face.get("study") != STUDY:
        bad.append("the face is not this study")
    if not str(face.get("population_source") or "").startswith(
            "e534_cap_to_payload.py::population()"):
        bad.append("the population_source is not this study's population function")
    if face.get("verdict") not in VERDICT_VOCAB:
        bad.append("the verdict %r is not in the vocabulary" % face.get("verdict"))
    summary = face.get("summary") or {}
    rows = face.get("arms") or []
    if face.get("verdict") != _verdict(summary):
        bad.append("the published verdict does not re-derive from the summary")
    if summary.get("arms_in_population") != len(rows):
        bad.append("the published arm count does not match the rows")
    if summary.get("parse_failures") != len(face.get("parse_failures") or []):
        bad.append("the parse-failure count does not match the published list")
    by_chain = _count(rows, "chain", CHAIN_VOCAB)
    if by_chain != (summary.get("arms_by_chain") or {}):
        bad.append("the per-arm chain counts do not re-derive")
    if sum(by_chain.values()) != len(rows):
        bad.append("the chain classes do not cover every arm")
    live = {k: _site_count(rows, k) for k in CHAIN_VOCAB}
    if live != (summary.get("sites_by_chain") or {}):
        bad.append("the per-site chain counts do not re-derive")
    if summary.get("call_sites_followed") != sum(r.get("sites_total") or 0 for r in rows):
        bad.append("the followed site count does not re-derive")
    if summary.get("arms_reaching_a_payload_field") != by_chain[C_PAYLOAD_FIELD]:
        bad.append("the payload-field arm count does not re-derive")
    if summary.get("arms_reaching_a_payload_body") != by_chain[C_PAYLOAD_BODY]:
        bad.append("the payload-body arm count does not re-derive")
    if summary.get("arms_reaching_a_sentence") != by_chain[C_SENTENCE]:
        bad.append("the sentence arm count does not re-derive")
    if summary.get("arms_reaching_a_count") != by_chain[C_COUNTED]:
        bad.append("the counted arm count does not re-derive")
    if summary.get("arms_whose_value_leaves_by_a_call") != by_chain[C_FORWARDED]:
        bad.append("the forwarded arm count does not re-derive")
    if summary.get("arms_unresolved") != by_chain[C_UNRESOLVED]:
        bad.append("the unresolved arm count does not re-derive")
    if summary.get("arms_that_stop_inside_the_reader") != len(
            [r for r in rows if r.get("chain") in (C_DISCARDED, C_BOUND_NEVER_READ,
                                                  C_STOPS_ELSEWHERE, C_TESTED)]):
        bad.append("the stop-inside count does not re-derive")
    if summary.get("arms_whose_reader_tests_the_value_narrowly") != len(
            [r for r in rows if (r.get("sites_by_chain") or {}).get(C_TESTED)]):
        bad.append("the narrow-test arm count does not re-derive")
    disagreed = sorted("%s::%s" % (r.get("module"), r.get("function")) for r in rows
                       if r.get("distinguish") == e529.D_NO_TEST
                       and (r.get("sites_by_chain") or {}).get(C_TESTED))
    if summary.get("arms_e529_published_as_never_tested_that_do_test") != disagreed:
        bad.append("the disagreement list with E529 does not re-derive")
    if summary.get("payload_keys_named") != sorted(
            {k for r in rows for k in (r.get("payload_keys") or [])}):
        bad.append("the named payload keys do not re-derive from the rows")
    for row in rows:
        if row.get("distinguish") not in READER_CANNOT_TELL:
            bad.append("arm %s::%s is outside the two reader classes"
                       % (row.get("module"), row.get("function")))
        for key in ("module", "function", "sentinel", "chain"):
            if not row.get(key):
                bad.append("arm %s::%s does not publish %s"
                           % (row.get("module"), row.get("function"), key))
                break
        if not row.get("sites_total"):
            bad.append("arm %s::%s follows no call site" % (row.get("module"),
                                                            row.get("function")))
        if row.get("chain") == C_PAYLOAD_FIELD and not row.get("payload_keys"):
            bad.append("arm %s::%s claims a published field and names no key"
                       % (row.get("module"), row.get("function")))
        if row.get("chain") == C_PAYLOAD_FIELD and not row.get("readers_that_write_a_payload"):
            bad.append("arm %s::%s claims a write and counts no writing reader"
                       % (row.get("module"), row.get("function")))
        if row.get("chain") == C_PAYLOAD_FIELD_UNWRITTEN and row.get("readers_that_write_a_payload"):
            bad.append("arm %s::%s claims a field is never written while a reader writes"
                       % (row.get("module"), row.get("function")))
        if sum((row.get("sites_by_chain") or {}).values()) != row.get("sites_total"):
            bad.append("arm %s::%s chain counts do not cover its sites"
                       % (row.get("module"), row.get("function")))
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
    print("E534 check: %d problem(s)" % len(bad))
    for line in bad[:20]:
        print("  - %s" % line)
    return 1 if bad else 0


def verify(root=None):
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
    print("E534 verify: %d problem(s)" % len(bad))
    for line in bad[:20]:
        print("  - %s" % line)
    return 1 if bad else 0


# ------------------------------------------------------------------ selftest
FIXTURE = '''
import json


def _deep(node, depth):
    if depth > 3:
        return None
    return _deep(node, depth + 1)


def baseline(path):
    value = _deep(path, 0)
    return 1


def count_it(path):
    value = _deep(path, 0)
    return len(value)


def name_it(path):
    value = _deep(path, 0)
    payload = {"resolved": value, "verdict": value}
    with open(path, "w") as fh:
        json.dump(payload, fh)
    return 0


def assemble_only(path):
    value = _deep(path, 0)
    payload = {"resolved": value}
    return payload


def sentence_it(path):
    value = _deep(path, 0)
    return "resolved %s" % (value,)


def drop_it(path):
    _deep(path, 0)
    return 0


def main():
    baseline("a")
    count_it("b")
    name_it("c")
    assemble_only("d")
    sentence_it("e")
    drop_it("f")
    return 0
'''


def _line_of(text, needle, start=0):
    idx = text.index(needle, start)
    return text[:idx].count("\n") + 1


def _fixture_arm(text, carrier, rel="scripts/fixture_mod.py"):
    return {
        "module": rel,
        "function": "_deep",
        "counter": "depth",
        "cap": 3,
        "cap_class": e529.CAP_CONSTANT,
        "sentinel": "None",
        "distinguish": e529.D_NO_TEST,
        "dead_arm": False,
        "has_recursive_call": True,
        "lines": [_line_of(text, "if depth > 3")],
        "call_site_count": 1,
        "use_counts": {},
        "_carrier": carrier,
    }


def _fixture_site(text, carrier, rel="scripts/fixture_mod.py"):
    use = {
        "baseline": e529.U_BINDS_AND_NEVER,
        "count_it": e529.U_PASSES,
        "name_it": e529.U_BINDS_AND_NEVER,
        "assemble_only": e529.U_BINDS_AND_NEVER,
        "sentence_it": e529.U_BINDS_AND_NEVER,
        "drop_it": e529.U_DISCARD,
    }[carrier]
    return {
        "module": rel,
        "line": _line_of(text, "_deep(path, 0)", text.index("def %s(" % carrier)),
        "callee": "_deep",
        "callee_modules": [rel],
        "attributed_modules": [rel],
        "caller": carrier,
        "use": use,
        "distinguish": e529.D_NO_TEST,
    }


def selftest():
    bad = []
    tmp = tempfile.mkdtemp(prefix="e534_")
    try:
        os.makedirs(os.path.join(tmp, "scripts"))
        path = os.path.join(tmp, "scripts", "fixture_mod.py")
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(FIXTURE)
        trees, failed = parse(["scripts/fixture_mod.py"], tmp)
        if failed or not trees:
            bad.append("the fixture corpus did not parse: %r" % failed)
        carriers = ("baseline", "count_it", "name_it", "assemble_only", "sentence_it",
                    "drop_it")
        rows = []
        for carrier in carriers:
            arm = _fixture_arm(FIXTURE, carrier)
            face = {"call_sites": [_fixture_site(FIXTURE, carrier)]}
            rows.extend(follow(trees, [arm], face))
        got = {r["function"] + "@" + r["sites"][0]["caller"]: r for r in rows}
        if len(rows) != len(carriers):
            bad.append("expected %d arms, saw %d" % (len(carriers), len(rows)))
        arms = [_fixture_arm(FIXTURE, c) for c in carriers]
        expect = {
            "baseline": C_BOUND_NEVER_READ,
            "count_it": C_COUNTED,
            "name_it": C_PAYLOAD_FIELD,
            "assemble_only": C_PAYLOAD_FIELD_UNWRITTEN,
            "sentence_it": C_SENTENCE,
            "drop_it": C_DISCARDED,
        }
        for carrier, klass in expect.items():
            row = got.get("_deep@" + carrier)
            if row is None:
                bad.append("the %s carrier is missing from the followed rows" % carrier)
                continue
            if row["chain"] != klass:
                bad.append("%s should chain as %r, saw %r" % (carrier, klass, row["chain"]))
        named = got.get("_deep@name_it")
        if named is not None:
            if not named["payload_keys"]:
                bad.append("the payload carrier names no key")
            elif "resolved" not in named["payload_keys"]:
                bad.append("the payload key the value lands under was not named: %r"
                           % named["payload_keys"])
            if not named["readers_that_write_a_payload"]:
                bad.append("the payload carrier is not counted as a writing reader")
        counting = got.get("_deep@count_it")
        if counting is not None and counting["sites_by_chain"].get(C_COUNTED) != 1:
            bad.append("the counting carrier was not classified as a counted quantity")

        # a population that never reaches a payload must flip the verdict
        calm = [r for r in rows if r["function"] + "@" + r["sites"][0]["caller"]
                in ("_deep@baseline", "_deep@drop_it")]
        calm_summary = _summary(calm, 1, [])
        if _verdict(calm_summary) != V_NEVER_LEAVES_THE_READER:
            bad.append("a world of discards should say the value never leaves, saw %r"
                       % _verdict(calm_summary))
        assembled = [r for r in rows if r["function"] + "@" + r["sites"][0]["caller"]
                     == "_deep@assemble_only"]
        if _verdict(_summary(assembled, 1, [])) != V_ONLY_ASSEMBLED:
            bad.append("a world that only assembles should say so, saw %r"
                       % _verdict(_summary(assembled, 1, [])))
        if _verdict(_summary([], 1, [])) != V_EMPTY:
            bad.append("an empty population is not reported as empty")

        os.makedirs(os.path.join(tmp, "results", "state_tilt"))
        up = os.path.join(ROOT, UPSTREAM_FACE)
        shutil.copyfile(up, os.path.join(tmp, "results", "state_tilt",
                                        os.path.basename(UPSTREAM_FACE)))
        face_out = build(root=tmp, write=False, arms=arms, rows=rows, sources=1, failures=[],
                         upstream_sha=_sha256_file(up))
        if face_problems(face_out, tmp):
            bad.append("the fixture face is refused by its own gate: %r"
                       % face_problems(face_out, tmp)[:2])
        for doctor, why in (
            (lambda f: f.__setitem__("verdict", V_NEVER_LEAVES_THE_READER),
             "a hand-written verdict"),
            (lambda f: f["summary"].__setitem__("arms_in_population", 99),
             "an edited arm count"),
            (lambda f: f["summary"].__setitem__("arms_reaching_a_payload_field", 0),
             "a zeroed payload arm count"),
            (lambda f: [r.__setitem__("payload_keys", []) for r in f["arms"]
                        if r["chain"] == C_PAYLOAD_FIELD][:1],
             "a payload arm that names no key"),
            (lambda f: [r.__setitem__("chain", C_BOUND_NEVER_READ) for r in f["arms"]
                        if r["chain"] == C_PAYLOAD_FIELD][:1],
             "a published field relabelled as unread"),
            (lambda f: f.__setitem__("upstream_face_sha256", "0" * 64),
             "an edited upstream pin"),
        ):
            hurt = copy.deepcopy(face_out)
            doctor(hurt)
            if not face_problems(hurt, tmp):
                bad.append("%s survived the gate" % why)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if bad:
        print("E534 selftest: %d problem(s)" % len(bad))
        for line in bad[:20]:
            print("  - %s" % line)
        return 1
    print("E534 selftest: clean")
    return 0


# ------------------------------------------------------------------ entry
def run():
    face = build()
    s = face["summary"]
    print("E534 run: followed %r arms / %r call sites in %r sources (%r parse failures)"
          % (s["arms_in_population"], s["call_sites_followed"], s["sources_read"],
             s["parse_failures"]))
    print("  arms: payload %r | sentence %r | counted %r | assembled-never-written %r | "
          "forwarded %r | stops inside %r | unresolved %r"
          % (s["arms_reaching_a_payload_field"], s["arms_reaching_a_sentence"],
             s["arms_reaching_a_count"], s["arms_whose_field_is_never_written"],
             s["arms_whose_value_leaves_by_a_call"], s["arms_that_stop_inside_the_reader"],
             s["arms_unresolved"]))
    print("  named payload keys: %r" % (s["payload_keys_named"],))
    print("  readers that test the value narrowly: %r arms (E529 said never tested: %r)"
          % (s["arms_whose_reader_tests_the_value_narrowly"],
             s["arms_e529_published_as_never_tested_that_do_test"]))
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