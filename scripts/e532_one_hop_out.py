"""E532 -- the sentinel a function's own body never replaces: is it replaced one hop out?

E531 (results/state_tilt/defaultparam_latest.json) published, per omission site, what the
signature default names and what the *own body* does with it.  Exactly one arm came back as
``the_body_passes_the_sentinel_on_unchanged``: the function neither rebinds the sentinel nor guards
a use, so inside its own body the value is still ``None``.  E530 (thirdhop_latest.json) published
the same shape one hop earlier.  Both faces stop there, which leaves the reader with a sentence
that is true and unusable: "nothing replaces it" is a claim about one function, not about the
value.

This study follows that arm one hop out.  For every arm the two upstream faces publish as
passed-on / signature-default, it finds every call inside the defining body that hands the
parameter onward, maps the argument onto the callee's own parameter, and publishes what THAT
callee does with it:

  * ``replaced_by_module_constant`` / ``_by_call_result`` / ``_by_read`` / ``_by_literal`` /
    ``_by_computed`` / ``_guarded_by_*`` -- the callee's body supplies a value;
  * ``still_forwarded`` -- the callee's body hands the sentinel on again (the chain is longer
    than the card asked);
  * ``never_read`` -- the callee's body never loads the parameter;
  * ``no_signature`` -- the callee is a name collision, an unresolved receiver, or not in this
    tree, so the question is unaskable rather than answered;
  * ``no_forwarding_site`` -- the defining body hands the parameter to no call at all, so the
    arm is not about the callee.

The point of the face is the count: how many sentinels are actually rescued one hop out, and for
the rest, which kind of unrescued they are.

    python scripts/e532_one_hop_out.py run        # build + write the face
    python scripts/e532_one_hop_out.py check      # gate the published face (fast)
    python scripts/e532_one_hop_out.py verify     # re-derive from the tree and gate
    python scripts/e532_one_hop_out.py selftest   # fixture corpus + doctored faces
"""
from __future__ import annotations

import ast
import hashlib
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e520_forwarded_argument as e520  # noqa: E402  (corpus, ownership, argument classifier)
import e531_default_param as e531  # noqa: E402  (default / rescue vocabularies and helpers)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")

CARD = ("E532-WHICH-SENTINEL-THAT-NOTHING-REPLACES-IN-ITS-OWN-BODY-IS-REPLACED-ONE-HOP-OUT-BY-"
        "THE-CALLEE-IT-IS-FORWARDED-TO")
STUDY = "E532_one_hop_out"
DATE_STAMP = "2026-11-08"
FACE_NAME = "onehopout_latest.json"
DATED_PREFIX = "ONEHOPOUT"

SELF_EXCLUDED = ("e532_", "run_e532", "_e532", "ONEHOPOUT", "onehopout_")

UPSTREAM_FACES = (
    ("results/state_tilt/defaultparam_latest.json", e531.STUDY),
    ("results/state_tilt/thirdhop_latest.json", "E530_third_hop"),
)

# ---------------------------------------------------------------- hop-out vocabulary
H_REPLACE_CONST = "replaced_by_module_constant"
H_REPLACE_CALL = "replaced_by_call_result"
H_REPLACE_READ = "replaced_by_read_or_scan_of_the_tree"
H_REPLACE_LITERAL = "replaced_by_a_literal"
H_REPLACE_COMPUTED = "replaced_by_a_computed_expression"
H_GUARD_CONST = "every_use_is_guarded_with_a_module_constant"
H_GUARD_OTHER = "every_use_is_guarded_with_another_value"
H_STILL_FORWARDED = "still_forwarded_by_the_callee_as_well"
H_NEVER_READ = "the_callee_never_reads_it"
H_NO_SIGNATURE = "the_callee_signature_is_not_in_this_tree"
H_NO_FORWARDING = "the_owning_body_hands_it_to_no_call_at_all"

HOP_VOCAB = (H_REPLACE_CONST, H_REPLACE_CALL, H_REPLACE_READ, H_REPLACE_LITERAL,
             H_REPLACE_COMPUTED, H_GUARD_CONST, H_GUARD_OTHER, H_STILL_FORWARDED, H_NEVER_READ,
             H_NO_SIGNATURE, H_NO_FORWARDING)

REPLACED = (H_REPLACE_CONST, H_REPLACE_CALL, H_REPLACE_READ, H_REPLACE_LITERAL,
            H_REPLACE_COMPUTED, H_GUARD_CONST, H_GUARD_OTHER)

# ---------------------------------------------------------------- arm provenance
P_FROM_E531 = "e531_rescue_class_the_body_passes_the_sentinel_on_unchanged"
P_FROM_E530 = "e530_terminal_nothing_is_passed_so_the_signature_default_applies"
ARM_VOCAB = (P_FROM_E531, P_FROM_E530)

V_REPLACED_SOMEWHERE = "at_least_one_sentinel_that_nothing_replaces_in_its_own_body_is_replaced_one_hop_out"
V_NONE_REPLACED = "no_forwarded_sentinel_is_replaced_by_the_callee_it_goes_to"
V_NO_FORWARDING = "no_arm_hands_its_sentinel_to_another_call"
V_UNANSWERED = "the_arms_that_could_answer_it_do_not_resolve_to_a_signature"
VERDICT_VOCAB = (V_REPLACED_SOMEWHERE, V_NONE_REPLACED, V_NO_FORWARDING, V_UNANSWERED)


def _now():
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def _sha256_file(path):
    h = hashlib.sha256()
    with io.open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _is_self(name):
    low = name.lower()
    return any(tok.lower() in low for tok in SELF_EXCLUDED)


# ------------------------------------------------------------------ population
def load_upstream(root=None):
    root = root or ROOT
    faces = []
    for rel, study in UPSTREAM_FACES:
        path = os.path.join(root, rel)
        with io.open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
        faces.append({"path": rel, "study": study, "sha256": _sha256_file(path), "doc": doc})
    return faces


def population(faces):
    """Every arm the two upstream faces publish as passed-on / signature-default."""
    arms = {}
    for face in faces:
        doc = face["doc"]
        if face["study"] == e531.STUDY:
            for site in doc.get("sites") or []:
                if site.get("rescue_class") != e531.R_PASSED_ON:
                    continue
                if site.get("resolution") != e531.X_RESOLVED:
                    continue
                key = (site.get("callee_module"), site.get("callee"), site.get("parameter"))
                arms.setdefault(key, {
                    "module": site.get("callee_module"),
                    "function": site.get("callee"),
                    "parameter": site.get("parameter"),
                    "upstream_studies": [],
                    "upstream_lines": [],
                    "default_class": site.get("default_class"),
                    "default_source": site.get("default_source"),
                    "own_body_rescue": site.get("rescue_class"),
                    "arm_origin": P_FROM_E531,
                })
                entry = arms[key]
                if face["study"] not in entry["upstream_studies"]:
                    entry["upstream_studies"].append(face["study"])
                entry["upstream_lines"].append(site.get("line"))
        else:
            for chain in doc.get("chains") or []:
                if "nothing_is_passed_so_the_signature_default_applies" not in \
                        (chain.get("terminal_kinds") or []):
                    continue
                key = (chain.get("second_hop_module"), chain.get("second_hop_function"),
                       chain.get("parcel_local"))
                arms.setdefault(key, {
                    "module": chain.get("second_hop_module"),
                    "function": chain.get("second_hop_function"),
                    "parameter": chain.get("parcel_local"),
                    "upstream_studies": [],
                    "upstream_lines": [],
                    "default_class": None,
                    "default_source": None,
                    "own_body_rescue": e531.R_PASSED_ON,
                    "arm_origin": P_FROM_E530,
                })
                entry = arms[key]
                if face["study"] not in entry["upstream_studies"]:
                    entry["upstream_studies"].append(face["study"])
                entry["upstream_lines"].append(chain.get("second_hop_line"))
    out = []
    for key in sorted(arms, key=lambda k: (str(k[0]), str(k[1]), str(k[2]))):
        entry = arms[key]
        entry["arm_id"] = "%s::%s(%s)" % (entry["module"], entry["function"], entry["parameter"])
        entry["upstream_lines"] = sorted(set(x for x in entry["upstream_lines"]
                                            if x is not None))
        out.append(entry)
    return out


# ------------------------------------------------------------------ forwarding sites
def _pos_params(funcdef):
    args = funcdef.args
    return [a.arg for a in (getattr(args, "posonlyargs", []) or [])] + [a.arg for a in args.args]


def forwarding_sites(funcdef, param):
    """Every call inside the body (nested defs excluded) that hands ``param`` onward."""
    out = []
    for node in e531._body_scope(funcdef):
        if not isinstance(node, ast.Call):
            continue
        as_positional = any(isinstance(a, ast.Name) and a.id == param for a in node.args)
        as_keyword = None
        for kw in node.keywords or []:
            if isinstance(kw.value, ast.Name) and kw.value.id == param:
                as_keyword = kw.arg
                break
        if not as_positional and as_keyword is None:
            continue
        out.append({
            "line": node.lineno,
            "call": node,
            "as_keyword": as_keyword,
            "as_positional": as_positional,
        })
    out.sort(key=lambda r: r["line"])
    return out


def _callee_name(call):
    func = call.func
    if isinstance(func, ast.Name):
        return func.id, None
    if isinstance(func, ast.Attribute):
        owner = func.value.id if isinstance(func.value, ast.Name) else None
        return func.attr, owner
    return None, None


def _resolve(module, call, corpus, callee_module_hint=None):
    """(resolution, callee_module, funcdef) for one call node."""
    name, owner = _callee_name(call)
    if name is None:
        return e531.X_NO_SIGNATURE, None, None
    ownership = e520._ownership(module, call, module, name, corpus)
    if ownership == e520.O_NAME_ONLY:
        return e531.X_NAME_ONLY, None, None
    if ownership == e520.O_UNRESOLVED_RECEIVER:
        return e531.X_RECEIVER, None, None
    imports = corpus.imports.get(module) or {}
    if owner is None:
        target = imports.get(name)
    else:
        target = imports.get(owner)
    callee_module = module if target is None else target
    funcdef = (corpus.funcs.get(callee_module) or {}).get(name)
    if funcdef is None:
        return e531.X_NO_SIGNATURE, callee_module, None
    return e531.X_RESOLVED, callee_module, funcdef


def _target_parameter(call, callee_def, site, fallback):
    """Which parameter of the callee the handed-on value lands in."""
    if site.get("as_keyword"):
        return site["as_keyword"]
    names = _pos_params(callee_def)
    index = 0
    for arg in call.args:
        if isinstance(arg, ast.Starred):
            return fallback
        if isinstance(arg, ast.Name) and arg.id == fallback:
            return names[index] if index < len(names) else fallback
        index += 1
    return fallback


def _classify_callee(funcdef, param, module, corpus):
    """What the callee's own body does with the value it was handed."""
    callee_tree = corpus.trees.get(module)
    for node in e531._body_scope(funcdef):
        is_bind, value, line = e531._binds_param(node, param)
        if not is_bind or value is None:
            continue
        fallback = e531._fallback_of(value, param)
        if fallback is None:
            continue
        kind = e531.classify_expr(fallback, module, corpus)
        source = e531._source_of(fallback, module, corpus, callee_tree)
        cls = {
            e531.D_CONSTANT: H_REPLACE_CONST,
            e531.D_FOREIGN: H_REPLACE_CONST,
            e531.D_CALL: H_REPLACE_CALL,
            e531.D_READ: H_REPLACE_READ,
            e531.D_LITERAL: H_REPLACE_LITERAL,
            e531.D_EMPTY: H_REPLACE_LITERAL,
            e531.D_NONE: H_REPLACE_LITERAL,
            e531.D_COMPUTED: H_REPLACE_COMPUTED,
        }.get(kind, H_REPLACE_COMPUTED)
        chain = []
        if kind in (e531.D_CONSTANT, e531.D_FOREIGN):
            chain, _terminal = e531.constant_chain(fallback, module, corpus)
        return cls, source, line, chain
    _uses, guard_class = e531._guarded_uses(funcdef, param)
    if guard_class == e531.R_NEVER_READ:
        return H_NEVER_READ, None, None, []
    if guard_class == e531.R_PASSED_ON:
        return H_STILL_FORWARDED, None, None, []
    if guard_class == e531.R_GUARD_OTHER:
        return H_GUARD_OTHER, None, None, []
    # every use is guarded: describe the first guarded fallback
    parents = {}
    for node in e531._body_scope(funcdef):
        for child in ast.iter_child_nodes(node):
            parents[child] = node
    for node in e531._body_scope(funcdef):
        if not isinstance(node, ast.Name) or node.id != param or \
                not isinstance(node.ctx, ast.Load):
            continue
        parent = parents.get(node)
        if isinstance(parent, ast.BoolOp) and len(parent.values) > 1 and parent.values[0] is node:
            fb = parent.values[1]
            kind = e531.classify_expr(fb, module, corpus)
            cls = H_GUARD_CONST if kind in (e531.D_CONSTANT, e531.D_FOREIGN) else H_GUARD_OTHER
            return cls, e531._source_of(fb, module, corpus, callee_tree), parent.lineno, []
    return H_GUARD_OTHER, None, None, []


def analyse_arm(arm, corpus):
    row = dict(arm)
    row["own_body_rescue"] = row.get("own_body_rescue")
    module = row["module"]
    funcdef = (corpus.funcs.get(module) or {}).get(row["function"])
    row["resolved_own_body"] = funcdef is not None
    row["forwarding"] = []
    if funcdef is None:
        row["hop_out_class"] = H_NO_SIGNATURE
        row["hop_out_source"] = None
        return row
    if row.get("default_class") is None:
        default = e531._default_node(funcdef, row["parameter"])
        row["default_class"] = e531.classify_expr(default, module, corpus)
        row["default_source"] = e531._source_of(default, module, corpus,
                                               corpus.trees.get(module))
    sites = forwarding_sites(funcdef, row["parameter"])
    if not sites:
        row["hop_out_class"] = H_NO_FORWARDING
        row["hop_out_source"] = None
        return row
    for site in sites:
        call = site["call"]
        name, owner = _callee_name(call)
        resolution, callee_module, callee_def = _resolve(module, call, corpus)
        entry = {
            "line": site["line"],
            "callee": name,
            "receiver": owner,
            "as_keyword": site.get("as_keyword"),
            "resolution": resolution,
            "callee_module": callee_module,
            "callee_parameter": None,
            "hop_out_class": H_NO_SIGNATURE,
            "hop_out_source": None,
            "hop_out_line": None,
            "constant_chain": [],
        }
        if resolution == e531.X_RESOLVED and callee_def is not None:
            target = _target_parameter(call, callee_def, site, row["parameter"])
            entry["callee_parameter"] = target
            cls, source, line, chain = _classify_callee(callee_def, target, callee_module,
                                                       corpus)
            entry["hop_out_class"] = cls
            entry["hop_out_source"] = source
            entry["hop_out_line"] = line
            entry["constant_chain"] = chain
        row["forwarding"].append(entry)
    classes = [e["hop_out_class"] for e in row["forwarding"]]
    if any(c in REPLACED for c in classes):
        row["hop_out_class"] = next(c for c in classes if c in REPLACED)
    elif any(c == H_STILL_FORWARDED for c in classes):
        row["hop_out_class"] = H_STILL_FORWARDED
    elif any(c == H_NEVER_READ for c in classes):
        row["hop_out_class"] = H_NEVER_READ
    else:
        row["hop_out_class"] = H_NO_SIGNATURE
    replaced = [e for e in row["forwarding"] if e["hop_out_class"] in REPLACED]
    row["hop_out_source"] = replaced[0]["hop_out_source"] if replaced else None
    return row


# ------------------------------------------------------------------ summary / verdict
def _count(rows, key, vocab):
    out = dict((v, 0) for v in vocab)
    for row in rows:
        out[row.get(key)] = out.get(row.get(key), 0) + 1
    return out


def _summary(rows, sources, upstream=None):
    forwarding = [f for row in rows for f in row.get("forwarding") or []]
    replaced_sites = [f for f in forwarding if f["hop_out_class"] in REPLACED]
    return {
        "arms_examined": len(rows),
        "arms_by_origin": _count(rows, "arm_origin", ARM_VOCAB),
        "arms_by_hop_out_class": _count(rows, "hop_out_class", HOP_VOCAB),
        "arms_that_hand_it_onward": sum(1 for r in rows if r.get("forwarding")),
        "arms_replaced_one_hop_out": sum(1 for r in rows if r["hop_out_class"] in REPLACED),
        "arms_still_forwarded_one_hop_out": sum(1 for r in rows
                                                if r["hop_out_class"] == H_STILL_FORWARDED),
        "arms_whose_callee_never_reads_it": sum(1 for r in rows
                                                if r["hop_out_class"] == H_NEVER_READ),
        "arms_whose_callee_is_not_in_this_tree": sum(
            1 for r in rows if r["hop_out_class"] == H_NO_SIGNATURE),
        "forwarding_sites_examined": len(forwarding),
        "forwarding_sites_replaced": len(replaced_sites),
        "forwarding_sites_by_class": _count(forwarding, "hop_out_class", HOP_VOCAB),
        "distinct_callee_signatures": len(set(
            (f.get("callee_module"), f.get("callee"), f.get("callee_parameter"))
            for f in forwarding if f.get("callee_parameter"))),
        "distinct_owning_functions": len(set((r.get("module"), r.get("function")) for r in rows)),
        "sources_read": sources,
        "upstream_faces": upstream or [],
    }


def _verdict(summary):
    if summary.get("arms_that_hand_it_onward", 0) == 0:
        return V_NO_FORWARDING
    if summary.get("arms_replaced_one_hop_out", 0) > 0:
        return V_REPLACED_SOMEWHERE
    if summary.get("arms_whose_callee_is_not_in_this_tree", 0) == summary.get(
            "arms_that_hand_it_onward", 0):
        return V_UNANSWERED
    return V_NONE_REPLACED


# ------------------------------------------------------------------ build / gate
def corpus_files(root=None):
    root = root or ROOT
    seen = set()
    for sub in ("scripts", "Tools", "firm", "live", "monitor"):
        base = os.path.join(root, sub)
        for dirpath, _dirs, filenames in os.walk(base):
            for name in filenames:
                if name.endswith(".py") and not _is_self(name):
                    seen.add(os.path.relpath(os.path.join(dirpath, name), root))
    return sorted(seen)


def _population_source():
    return ("%s::population() -- every arm E531 publishes with rescue_class "
            "the_body_passes_the_sentinel_on_unchanged and every E530 chain whose terminals "
            "include nothing_is_passed_so_the_signature_default_applies, keyed by "
            "(module, function, parameter)" % os.path.basename(__file__))


def build(root=None, write=True, rows=None, sources=None, upstream=None):
    root = root or ROOT
    if rows is None:
        faces = load_upstream(root)
        upstream = [{"path": f["path"], "study": f["study"], "sha256": f["sha256"]}
                    for f in faces]
        corpus = e520.ForwardCorpus(root)
        rows = [analyse_arm(arm, corpus) for arm in population(faces)]
        sources = len(corpus_files(root)) if sources is None else sources
    summary = _summary(rows, sources or 0, upstream)
    face = {
        "study": STUDY,
        "card": CARD,
        "title": ("is the sentinel nothing replaces in its own body replaced one hop out by the "
                  "callee it is forwarded to"),
        "generated": _now(),
        "evidence_cutoff": DATE_STAMP,
        "population_source": _population_source(),
        "upstream_faces": upstream or [],
        "method_limits": [
            "one hop, not a chain: an arm whose callee also forwards the sentinel is published "
            "as still_forwarded and the next hop is out of scope",
            "the callee is resolved only when the call names it through an import this tree "
            "binds; a bare name no import binds, or a receiver that is not a name, is published "
            "as no_signature rather than merged onto a same-named function elsewhere",
            "the callee's parameter is mapped by keyword, or by position against the callee's "
            "positional list; a call that splats *args keeps the original name because the "
            "mapping is not decidable from the call node",
            "the callee's treatment is read from its own body only -- a substitute supplied by "
            "a third function is out of scope and stays published as never_read or forwarded",
            "nothing is executed and no source is rewritten",
            "sources_read is a snapshot of a live tree other lanes write to; it is published but "
            "not gated, while every class and the verdict are re-derived",
        ],
        "summary": summary,
        "verdict": _verdict(summary),
        "verdict_vocab": list(VERDICT_VOCAB),
        "hop_out_vocab": list(HOP_VOCAB),
        "arm_vocab": list(ARM_VOCAB),
        "arms": rows,
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
    text = json.dumps(face, indent=1, sort_keys=True, ensure_ascii=False)
    for path in (dated, latest):
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text + "\n")
    return dated


def load_face(root=None, name=None):
    path = os.path.join(root or ROOT, "results", "state_tilt", name or FACE_NAME)
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


GATED_SUMMARY_KEYS = ("arms_examined", "arms_by_origin", "arms_by_hop_out_class",
                      "arms_that_hand_it_onward", "arms_replaced_one_hop_out",
                      "arms_still_forwarded_one_hop_out", "arms_whose_callee_never_reads_it",
                      "arms_whose_callee_is_not_in_this_tree", "forwarding_sites_examined",
                      "forwarding_sites_replaced", "forwarding_sites_by_class",
                      "distinct_callee_signatures", "distinct_owning_functions")


def face_problems(face, root=None):
    bad = []
    for key in ("study", "card", "generated", "evidence_cutoff", "population_source",
                "upstream_faces", "summary", "verdict", "arms", "method_limits",
                "hop_out_vocab", "arm_vocab", "verdict_vocab"):
        if key not in face:
            bad.append("the face does not publish %s" % key)
    if face.get("study") != STUDY:
        bad.append("the face is not this study")
    if "::population()" not in str(face.get("population_source") or ""):
        bad.append("the population_source is not this study's population function")
    if face.get("verdict") not in VERDICT_VOCAB:
        bad.append("the verdict %r is not in the vocabulary" % face.get("verdict"))
    summary = face.get("summary") or {}
    rows = face.get("arms") or []
    if face.get("verdict") != _verdict(summary):
        bad.append("the published verdict does not re-derive from the summary")
    if summary.get("arms_examined") != len(rows):
        bad.append("the examined population does not add up")
    if summary.get("arms_that_hand_it_onward") != sum(1 for r in rows if r.get("forwarding")):
        bad.append("the arms that hand it onward do not re-derive")
    for row in rows:
        where = "%s::%s(%s)" % (row.get("module"), row.get("function"), row.get("parameter"))
        if row.get("arm_origin") not in ARM_VOCAB:
            bad.append("%s publishes an arm origin outside the vocabulary" % where)
        if row.get("hop_out_class") not in HOP_VOCAB:
            bad.append("%s publishes hop-out class %r outside the vocabulary"
                       % (where, row.get("hop_out_class")))
        if row.get("hop_out_class") in REPLACED and not row.get("hop_out_source"):
            bad.append("%s publishes a replacement but no source" % where)
        if row.get("hop_out_class") == H_NO_FORWARDING and row.get("forwarding"):
            bad.append("%s says it hands nothing onward but lists forwarding sites" % where)
        for entry in row.get("forwarding") or []:
            if entry.get("hop_out_class") not in HOP_VOCAB:
                bad.append("%s:%s publishes hop-out class %r outside the vocabulary"
                           % (where, entry.get("line"), entry.get("hop_out_class")))
            if entry.get("resolution") == e531.X_RESOLVED and not entry.get(
                    "callee_parameter"):
                bad.append("%s:%s resolved a callee but named no parameter"
                           % (where, entry.get("line")))
            if entry.get("hop_out_class") in REPLACED and not entry.get("hop_out_source"):
                bad.append("%s:%s publishes a replacement but no source"
                           % (where, entry.get("line")))
    recomputed = _summary(rows, summary.get("sources_read") or 0,
                          summary.get("upstream_faces"))
    for key in GATED_SUMMARY_KEYS:
        if recomputed.get(key) != summary.get(key):
            bad.append("the summary key %s does not re-derive from the arms" % key)
    return bad


def check(face=None, root=None):
    face = face or load_face(root)
    bad = face_problems(face, root)
    print("E532 check: %d problem(s)" % len(bad))
    for line in bad[:20]:
        print("  - %s" % line)
    return 1 if bad else 0


def verify(root=None):
    published = load_face(root)
    fresh = build(root=root, write=False)
    bad = face_problems(published, root)
    if fresh["verdict"] != published["verdict"]:
        bad.append("the verdict drifts when re-derived")
    volatile = ("sources_read",)
    trimmed = {k: v for k, v in fresh["summary"].items() if k not in volatile}
    pinned = {k: v for k, v in published["summary"].items() if k not in volatile}
    if json.dumps(trimmed, sort_keys=True, default=str) != json.dumps(
            pinned, sort_keys=True, default=str):
        moved = sorted(k for k in set(trimmed) | set(pinned) if trimmed.get(k) != pinned.get(k))
        bad.append("the summary drifts when re-derived: %r" % moved[:6])
    print("E532 verify: %d problem(s)" % len(bad))
    for line in bad[:20]:
        print("  - %s" % line)
    return 1 if bad else 0


# ------------------------------------------------------------------ selftest
FIXTURE = {
    "pkg/__init__.py": "",
    "pkg/mod.py": '''"""Fixture: four callees, one per hop-out class."""
import os

ROOT = os.path.dirname(os.path.abspath(__file__))


def replaces_from_constant(root=None, files=None):
    root = root or ROOT
    return [root, files]


def replaces_from_call(root=None):
    root = root or os.getcwd()
    return root


def never_reads_it(root=None):
    return 42


def guards_every_use(root=None):
    return (root or ROOT) + "x"


def still_forwards(root=None):
    return replaces_from_constant(root)


def caller_constant(root=None):
    return replaces_from_constant(root)


def caller_call(root=None):
    return replaces_from_call(root)


def caller_never(root=None):
    return never_reads_it(root)


def caller_guard(root=None):
    return guards_every_use(root)


def caller_forward(root=None):
    return still_forwards(root)
'''}


def _fixture_root():
    import tempfile
    root = tempfile.mkdtemp(prefix="e532_fx_")
    for rel, text in FIXTURE.items():
        path = os.path.join(root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
    return root


def _fixture_arms(root):
    corpus = e520.ForwardCorpus(root)
    base = {"upstream_studies": ["FX"], "upstream_lines": [0], "arm_origin": P_FROM_E531,
            "default_class": None, "default_source": None,
            "own_body_rescue": e531.R_PASSED_ON}
    names = ("caller_constant", "caller_call", "caller_never", "caller_guard",
             "caller_forward")
    rows = []
    for name in names:
        arm = dict(base)
        arm.update({"module": "mod", "function": name, "parameter": "root",
                    "arm_id": "mod::%s(root)" % name})
        rows.append(analyse_arm(arm, corpus))
    return rows


def selftest():
    fails = []

    def check(label, ok, detail=""):
        if not ok:
            fails.append("%s %s" % (label, detail))
        print("%s %s%s" % ("PASS" if ok else "FAIL", label,
                           ("" if ok else " -- " + str(detail))))

    root = _fixture_root()
    rows = _fixture_arms(root)
    by_name = {}
    for row in rows:
        by_name[row["function"]] = row

    # 1. a callee that rebinds from a module constant is published as replaced, with its source
    row = by_name["caller_constant"]
    check("a constant rebind one hop out is published as replaced",
          row["hop_out_class"] == H_REPLACE_CONST, row["hop_out_class"])
    check("the replacement names the substitute it rebinds from",
          (row.get("hop_out_source") or "") == "ROOT",
          row.get("hop_out_source"))
    check("the constant chain follows the module constant",
          row["forwarding"][0]["constant_chain"] == ["mod:ROOT"],
          row["forwarding"][0]["constant_chain"])

    # 2. a call-result substitute is a different class than a constant
    row = by_name["caller_call"]
    check("a call-result rebind one hop out is published as replaced_by_call_result",
          row["hop_out_class"] == H_REPLACE_CALL, row["hop_out_class"])

    # 3. a callee that never loads the parameter is published as never_read
    row = by_name["caller_never"]
    check("a callee that never reads the parameter is published as never_read",
          row["hop_out_class"] == H_NEVER_READ, row["hop_out_class"])

    # 4. a guard (root or X) is a replacement, not a pass-on
    row = by_name["caller_guard"]
    check("a guarded use one hop out is published as a replacement",
          row["hop_out_class"] in (H_GUARD_CONST, H_GUARD_OTHER), row["hop_out_class"])

    # 5. a callee that forwards again is NOT counted as a replacement
    row = by_name["caller_forward"]
    check("a callee that forwards again is published as still_forwarded",
          row["hop_out_class"] == H_STILL_FORWARDED, row["hop_out_class"])
    check("still_forwarded is outside the replaced set",
          row["hop_out_class"] not in REPLACED, row["hop_out_class"])

    # 6. an arm whose body hands the value to nothing
    arm = {"module": "pkg/mod.py", "function": "no_such_function", "parameter": "root",
           "upstream_studies": ["FX"], "upstream_lines": [0], "arm_origin": P_FROM_E531,
           "default_class": None, "default_source": None, "own_body_rescue": e531.R_PASSED_ON,
           "arm_id": "pkg/mod.py::no_such_function(root)"}
    row = analyse_arm(arm, e520.ForwardCorpus(root))
    check("an arm whose owning function is not in the tree is unaskable",
          row["hop_out_class"] == H_NO_SIGNATURE, row["hop_out_class"])

    # 7. the verdict vocabulary is a function of the summary alone
    summary = _summary([], 0)
    check("an empty population is published as no_forwarding",
          _verdict(summary) == V_NO_FORWARDING, _verdict(summary))
    summary = {"arms_that_hand_it_onward": 2, "arms_replaced_one_hop_out": 1,
               "arms_whose_callee_is_not_in_this_tree": 0}
    check("one replacement decides the verdict", _verdict(summary) == V_REPLACED_SOMEWHERE)
    summary = {"arms_that_hand_it_onward": 2, "arms_replaced_one_hop_out": 0,
               "arms_whose_callee_is_not_in_this_tree": 2}
    check("all-unresolvable is published as unanswered", _verdict(summary) == V_UNANSWERED)
    summary = {"arms_that_hand_it_onward": 2, "arms_replaced_one_hop_out": 0,
               "arms_whose_callee_is_not_in_this_tree": 1}
    check("a resolvable-but-unreplaced arm is published as none_replaced",
          _verdict(summary) == V_NONE_REPLACED)

    # 8. the gate refuses a doctored face
    face = build(root=root, write=False, rows=rows, sources=5, upstream=[])
    check("a freshly built fixture face passes its own gate",
          face_problems(face, root) == [], face_problems(face, root)[:3])
    doctored = json.loads(json.dumps(face))
    doctored["verdict"] = V_NONE_REPLACED
    check("the gate refuses a verdict that does not re-derive",
          any("verdict" in b for b in face_problems(doctored, root)))
    doctored = json.loads(json.dumps(face))
    doctored["arms"][0]["hop_out_class"] = H_NO_FORWARDING
    check("the gate refuses a class its own forwarding list contradicts",
          face_problems(doctored, root) != [])
    doctored = json.loads(json.dumps(face))
    doctored["arms"] = doctored["arms"][:-1]
    check("the gate refuses a shrunken population",
          any("add up" in b for b in face_problems(doctored, root)))

    total = 15
    print("E532 selftest: %d/%d" % (total - len(fails), total))
    return 1 if fails else 0


def run():
    face = build()
    dated = write_face(face)
    summary = face["summary"]
    print("E532 run: %d arms, %d forwarding sites, verdict=%s"
          % (summary["arms_examined"], summary["forwarding_sites_examined"], face["verdict"]))
    print("arms replaced one hop out: %d / %d"
          % (summary["arms_replaced_one_hop_out"], summary["arms_examined"]))
    print("face: %s" % os.path.relpath(dated, ROOT))
    return 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "run"
    if cmd == "run":
        return run()
    if cmd == "check":
        return check()
    if cmd == "verify":
        return verify()
    if cmd == "selftest":
        return selftest()
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())