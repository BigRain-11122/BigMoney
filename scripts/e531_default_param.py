"""E531 -- what does the signature default that E530/E526 landed on actually name?

E530 (results/state_tilt/thirdhop_latest.json) followed the chains E526 left moving and published
that some of them end at a *signature default* rather than at a caller.  A default is a value the
signature itself writes, so the chain does reach something -- but "something" is not a population.
E526 published the same class of hand-over one hop earlier, so both faces are read here.

For every omission site those two faces publish (``argument_kind`` == the signature default), this
study resolves the callee signature through the E520 ownership classifier and publishes, per site:

  * ``default_class`` -- what the signature's own default expression names (a sentinel such as
    ``None``, an empty container, a literal, a module constant of the defining module, a name from
    another module, a call result, a read/scan of the tree, or a computed expression);
  * ``constant_chain`` -- when the default or its substitute is a module constant, the module-level
    name chain it folds through (``ROOT -> e326.ROOT``), so "a constant" is never left as a word;
  * ``rescue_class`` -- what the *body* does with a sentinel default: rebind it from a module
    constant, rebind it from a call result, guard every use with a fallback, pass it on unchanged,
    or never read it at all;
  * ``caller_could_have_supplied`` -- whether the function that omits the argument has a value of
    that name in scope at its own call site (its own parameter, a local, a module constant), so
    "the default supplies it" stops standing in for "the population is whatever the signature
    happens to hold".

An omission site whose call names the function only by a bare name that no import binds, or whose
receiver is not a name, is published as a *name collision* rather than resolved: E520 already keeps
those apart and this face must not merge them back.

    python scripts/e531_default_param.py run        # build + write the face
    python scripts/e531_default_param.py check      # gate the published face (fast)
    python scripts/e531_default_param.py verify     # re-derive from the tree and gate
    python scripts/e531_default_param.py selftest   # fixture corpus + doctored faces
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
import e526_second_hop as e526  # noqa: E402  (the second hop that produced part of the population)
import e513_constant_origin as e513  # noqa: E402  (READERS / WALKERS: a read of the tree)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")

CARD = ("E531-WHAT-DOES-THE-SIGNATURE-DEFAULT-THAT-SUPPLIES-ROOT-TO-THE-8-OMITTING-CALL-SITES-"
        "ACTUALLY-NAME")
STUDY = "E531_default_param"
DATE_STAMP = "2026-11-08"
FACE_NAME = "defaultparam_latest.json"
DATED_PREFIX = "DEFAULTPARAM"

SELF_EXCLUDED = ("e531_", "run_e531", "_e531", "DEFAULTPARAM", "defaultparam_")

UPSTREAM_FACES = (
    ("results/state_tilt/thirdhop_latest.json", "E530_third_hop"),
    ("results/state_tilt/secondhop_latest.json", e526.STUDY),
)
MAX_CONSTANT_HOPS = 4

# ---------------------------------------------------------------- default expressions
D_NONE = "a_sentinel_none"
D_EMPTY = "a_sentinel_empty_container_or_falsy_literal"
D_LITERAL = "a_literal_value"
D_CONSTANT = "a_module_constant_of_the_defining_module"
D_FOREIGN = "a_name_from_another_module"
D_CALL = "a_call_result"
D_READ = "a_read_or_scan_of_the_tree"
D_COMPUTED = "a_computed_expression"
D_NO_DEFAULT = "the_signature_has_no_default_for_this_parameter"
DEFAULT_VOCAB = (D_NONE, D_EMPTY, D_LITERAL, D_CONSTANT, D_FOREIGN, D_CALL, D_READ, D_COMPUTED,
                 D_NO_DEFAULT)
SENTINELS = (D_NONE, D_EMPTY)

# ---------------------------------------------------------------- what the body does
R_REBIND_CONST = "the_body_rebinds_it_from_a_module_constant"
R_REBIND_CALL = "the_body_rebinds_it_from_a_call_result"
R_REBIND_READ = "the_body_rebinds_it_from_a_read_or_scan_of_the_tree"
R_REBIND_LITERAL = "the_body_rebinds_it_from_a_literal"
R_REBIND_COMPUTED = "the_body_rebinds_it_from_a_computed_expression"
R_GUARD_CONST = "every_use_is_guarded_with_a_module_constant"
R_GUARD_READ = "every_use_is_guarded_with_a_read_or_scan_of_the_tree"
R_GUARD_OTHER = "every_use_is_guarded_with_another_value"
R_PASSED_ON = "the_body_passes_the_sentinel_on_unchanged"
R_NEVER_READ = "the_body_never_reads_it"
R_VALUE = "not_applicable_the_default_is_already_a_value"
R_NO_SIGNATURE = "not_applicable_no_signature_was_resolved"
RESCUE_VOCAB = (R_REBIND_CONST, R_REBIND_CALL, R_REBIND_READ, R_REBIND_LITERAL, R_REBIND_COMPUTED,
                R_GUARD_CONST, R_GUARD_READ, R_GUARD_OTHER, R_PASSED_ON, R_NEVER_READ, R_VALUE,
                R_NO_SIGNATURE)
RESCUED = (R_REBIND_CONST, R_REBIND_CALL, R_REBIND_READ, R_REBIND_LITERAL, R_REBIND_COMPUTED,
           R_GUARD_CONST, R_GUARD_READ, R_GUARD_OTHER, R_VALUE)

# ---------------------------------------------------------------- resolution
X_RESOLVED = "the_signature_is_in_this_tree"
X_NAME_ONLY = "the_name_is_only_a_collision_no_import_binds_it"
X_RECEIVER = "the_receiver_of_the_attribute_call_is_not_a_name"
X_NO_SIGNATURE = "the_callee_signature_is_not_in_this_tree"
RESOLUTION_VOCAB = (X_RESOLVED, X_NAME_ONLY, X_RECEIVER, X_NO_SIGNATURE)

C_OWN_PARAMETER = "its_own_parameter_of_that_name"
C_LOCAL = "a_local_of_that_name"
C_MODULE_CONSTANT = "a_module_constant_of_the_calling_module"
C_NOTHING = "nothing_of_that_name_is_in_scope_at_the_call_site"
CALLER_VOCAB = (C_OWN_PARAMETER, C_LOCAL, C_MODULE_CONSTANT, C_NOTHING)

V_RESCUED = "every_default_is_a_sentinel_that_the_body_replaces_with_a_named_value"
V_UNRESCUED = "some_default_is_a_sentinel_that_nothing_in_the_body_replaces"
V_VALUE = "some_default_is_itself_a_value_so_the_chain_ends_in_the_signature"
V_UNRESOLVED = "no_omission_site_resolves_to_a_signature_in_this_tree"
V_EMPTY = "the_upstream_faces_publish_no_omission_site"
VERDICT_VOCAB = (V_RESCUED, V_UNRESCUED, V_VALUE, V_UNRESOLVED, V_EMPTY)


def _now():
    from datetime import datetime
    return datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S")


def _sha256_file(path):
    digest = hashlib.sha256()
    with io.open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_self(name):
    return any(name.startswith(prefix) for prefix in SELF_EXCLUDED)


# ------------------------------------------------------------------ population
def load_upstream(root=None):
    root = root or ROOT
    faces = []
    for rel, study in UPSTREAM_FACES:
        path = os.path.join(root, rel)
        with io.open(path, encoding="utf-8") as fh:
            faces.append({"path": rel, "study": study, "face": json.load(fh),
                          "sha256": _sha256_file(path)})
    return faces


def population(faces):
    """Every omission site the two upstream faces publish, deduplicated by identity."""
    sites = []
    for entry in faces:
        face = entry["face"]
        for chain in face.get("chains") or []:
            for hop in chain.get("hops") or []:
                for site in hop.get("sites") or []:
                    if site.get("argument_kind") != e520.A_DEFAULT:
                        continue
                    sites.append({
                        "upstream_study": entry["study"],
                        "caller_module": site.get("caller_module"),
                        "line": site.get("line"),
                        "callee": site.get("hop_function"),
                        "parameter": hop.get("name"),
                        "chain_argument": chain.get("argument"),
                        "chain_shape": chain.get("shape"),
                    })
        for parcel in face.get("sites") or []:
            for site in parcel.get("hop_sites") or []:
                if site.get("argument_kind") != e520.A_DEFAULT:
                    continue
                sites.append({
                    "upstream_study": entry["study"],
                    "caller_module": site.get("caller_module"),
                    "line": site.get("line"),
                    "callee": site.get("hop_function"),
                    "parameter": parcel.get("local"),
                    "chain_argument": parcel.get("local"),
                    "chain_shape": parcel.get("arrival"),
                })
    dedup = {}
    for site in sites:
        key = (site["caller_module"], site["line"], site["callee"], site["parameter"])
        if key not in dedup:
            dedup[key] = site
        else:
            seen = dedup[key].setdefault("also_published_by", [])
            if site["upstream_study"] not in seen and site["upstream_study"] != \
                    dedup[key]["upstream_study"]:
                seen.append(site["upstream_study"])
    rows = sorted(dedup.values(), key=lambda r: (str(r["caller_module"]), r["line"] or 0,
                                                 str(r["callee"])))
    return rows


# ------------------------------------------------------------------ expression classes
def _module_names(corpus, module):
    cache = getattr(corpus, "_e531_module_names", None)
    if cache is None:
        cache = {}
        setattr(corpus, "_e531_module_names", cache)
    if module in cache:
        return cache[module]
    names = {}
    tree = corpus.trees.get(module)
    if tree is not None:
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        names[target.id] = node.value
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                names[node.target.id] = node.value
    cache[module] = names
    return names


def classify_expr(node, module, corpus):
    """What one expression names, in the vocabulary this face publishes."""
    if node is None:
        return D_NO_DEFAULT
    if isinstance(node, ast.Constant):
        value = node.value
        if value is None:
            return D_NONE
        if value in ("", 0, False, 0.0):
            return D_EMPTY
        return D_LITERAL
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        return D_EMPTY if not node.elts else D_LITERAL
    if isinstance(node, ast.Dict):
        return D_EMPTY if not node.keys else D_LITERAL
    if isinstance(node, ast.Name):
        if node.id in (corpus.imports.get(module) or {}):
            return D_FOREIGN
        if corpus.lookup(module, node.id) is not None or node.id in _module_names(corpus, module):
            return D_CONSTANT
        return D_COMPUTED
    if isinstance(node, ast.Attribute):
        return D_FOREIGN
    if isinstance(node, ast.Call):
        func = node.func
        name = None
        if isinstance(func, ast.Name):
            name = func.id
        elif isinstance(func, ast.Attribute):
            name = func.attr
        if name in e513.READERS or name in e513.WALKERS:
            return D_READ
        return D_CALL
    return D_COMPUTED


def constant_chain(node, module, corpus):
    """Follow module-level `Name = <Name|Attribute>` hops so a constant is never just a word."""
    chain = []
    seen = set()
    current = node
    for _ in range(MAX_CONSTANT_HOPS):
        if isinstance(current, ast.Name):
            if (module, current.id) in seen:
                chain.append("%s:%s (loop)" % (module, current.id))
                return chain, D_COMPUTED
            seen.add((module, current.id))
            chain.append("%s:%s" % (module, current.id))
            value = _module_names(corpus, module).get(current.id)
            if value is None:
                return chain, D_CONSTANT
            current = value
            continue
        if isinstance(current, ast.Attribute) and isinstance(current.value, ast.Name):
            owner = current.value.id
            target = (corpus.imports.get(module) or {}).get(owner)
            chain.append("%s.%s" % (owner, current.attr))
            if target is None:
                return chain, D_FOREIGN
            stem = os.path.splitext(os.path.basename(target.replace(".", "/")))[0]
            value = _module_names(corpus, stem).get(current.attr)
            module = stem
            if value is None:
                return chain, D_CONSTANT
            current = value
            continue
        return chain, classify_expr(current, module, corpus)
    return chain, D_COMPUTED


def _source_of(node, module, corpus, tree):
    """The source text of one expression, read from the module file (not re-serialised)."""
    if node is None or tree is None:
        return None
    try:
        path = os.path.join(getattr(corpus, "root", ROOT), corpus.by_module.get(module, ""))
        with io.open(path, encoding="utf-8") as fh:
            text = fh.read()
        segment = ast.get_source_segment(text, node)
        if segment is not None:
            return " ".join(segment.split())
    except Exception:  # pragma: no cover - defensive, the class is what is gated
        pass
    return None


def _body_scope(funcdef):
    """Nodes inside the function body but outside any nested def (the rescue site lives here)."""
    stack = list(funcdef.body)
    while stack:
        node = stack.pop()
        yield node
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
            continue
        stack.extend(ast.iter_child_nodes(node))


def _binds_param(node, param):
    """(is_an_assignment_of_param, bound_expression) for statements that rebind ``param``."""
    if isinstance(node, ast.Assign):
        if any(isinstance(t, ast.Name) and t.id == param for t in node.targets):
            return True, node.value, node.lineno
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) \
            and node.target.id == param:
        return True, node.value, node.lineno
    return False, None, None


def _fallback_of(value, param):
    """The substitute expression inside `p = p or X` / `p = p if p is not None else X`."""
    if isinstance(value, ast.BoolOp) and isinstance(value.op, ast.Or):
        values = value.values
        if values and isinstance(values[0], ast.Name) and values[0].id == param:
            return values[1] if len(values) > 1 else None
    if isinstance(value, ast.IfExp):
        body = value.body
        test = value.test
        if isinstance(body, ast.Name) and body.id == param:
            return value.orelse
        if isinstance(test, ast.Compare) and isinstance(test.left, ast.Name) \
                and test.left.id == param:
            return value.orelse
    return None


def _rescue_of(node, module, corpus):
    """Classify one substitute expression into the rescue vocabulary."""
    kind = classify_expr(node, module, corpus)
    return {
        D_CONSTANT: R_REBIND_CONST,
        D_FOREIGN: R_REBIND_CONST,
        D_CALL: R_REBIND_CALL,
        D_READ: R_REBIND_READ,
        D_LITERAL: R_REBIND_LITERAL,
        D_EMPTY: R_REBIND_LITERAL,
        D_NONE: R_REBIND_LITERAL,
        D_COMPUTED: R_REBIND_COMPUTED,
    }.get(kind, R_REBIND_COMPUTED)


def _guarded_uses(funcdef, param):
    """Every Load use of ``param`` and the fallback each one is guarded by, if any."""
    uses = []
    for node in _body_scope(funcdef):
        if not isinstance(node, ast.Name) or node.id != param or not isinstance(node.ctx, ast.Load):
            continue
        uses.append(node)
    if not uses:
        return [], R_NEVER_READ
    parents = {}
    for node in _body_scope(funcdef):
        for child in ast.iter_child_nodes(node):
            parents[child] = node
    fallbacks = []
    for use in uses:
        parent = parents.get(use)
        guard = None
        if isinstance(parent, ast.BoolOp) and isinstance(parent.op, ast.Or) and \
                parent.values and parent.values[0] is use and len(parent.values) > 1:
            guard = parent.values[1]
        elif isinstance(parent, ast.IfExp) and parent.body is use:
            guard = parent.orelse
        elif isinstance(parent, ast.Compare) and parent.left is use:
            guard = "test"  # `p is not None` is the guard itself; the body decides the value
        if guard is None:
            return uses, R_PASSED_ON
        if guard != "test":
            fallbacks.append(guard)
    if not fallbacks:
        return uses, R_GUARD_OTHER
    return uses, None


def analyse_site(site, corpus):
    row = dict(site)
    module = row["caller_module"]
    row["resolution"] = X_NO_SIGNATURE
    row["callee_module"] = None
    row["default_class"] = D_NO_DEFAULT
    row["default_source"] = None
    row["constant_chain"] = []
    row["constant_terminal_class"] = None
    row["rescue_class"] = R_NO_SIGNATURE
    row["rescue_source"] = None
    row["rescue_chain"] = []
    row["rescue_terminal_class"] = None
    row["caller_function"] = None
    row["caller_could_have_supplied"] = C_NOTHING

    tree = corpus.trees.get(module)
    call = None
    if tree is not None:
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or node.lineno != row["line"]:
                continue
            func = node.func
            name = func.id if isinstance(func, ast.Name) else (
                func.attr if isinstance(func, ast.Attribute) else None)
            if name == row["callee"]:
                call = node
                break
    if call is None:
        row["resolution"] = X_NO_SIGNATURE
        return row

    ownership = e520._ownership(module, call, module, row["callee"], corpus)
    row["ownership"] = ownership
    if ownership == e520.O_NAME_ONLY:
        row["resolution"] = X_NAME_ONLY
        return row
    if ownership == e520.O_UNRESOLVED_RECEIVER:
        row["resolution"] = X_RECEIVER
        return row

    target = None
    if isinstance(call.func, ast.Name):
        target = (corpus.imports.get(module) or {}).get(row["callee"])
    else:
        owner = call.func.value.id if isinstance(call.func.value, ast.Name) else None
        target = (corpus.imports.get(module) or {}).get(owner) if owner else None
    callee_module = module if target is None else target
    funcdef = (corpus.funcs.get(callee_module) or {}).get(row["callee"])
    if funcdef is None:
        row["resolution"] = X_NO_SIGNATURE
        return row
    row["resolution"] = X_RESOLVED
    row["callee_module"] = callee_module

    param = row["parameter"]
    default = _default_node(funcdef, param)
    row["default_class"] = classify_expr(default, callee_module, corpus)
    callee_tree = corpus.trees.get(callee_module)
    row["default_source"] = _source_of(default, callee_module, corpus, callee_tree)
    if row["default_class"] in (D_CONSTANT, D_FOREIGN) and default is not None:
        row["constant_chain"], row["constant_terminal_class"] = constant_chain(
            default, callee_module, corpus)

    rescue_node = None
    for node in _body_scope(funcdef):
        is_bind, value, line = _binds_param(node, param)
        if not is_bind or value is None:
            continue
        fallback = _fallback_of(value, param)
        if fallback is None:
            continue
        rescue_node = fallback
        row["rescue_class"] = _rescue_of(fallback, callee_module, corpus)
        row["rescue_line"] = line
        break

    if rescue_node is None:
        _uses, guard_class = _guarded_uses(funcdef, param)
        if guard_class is not None:
            row["rescue_class"] = guard_class
        else:
            # every use is guarded; describe the fallback used at the first guarded site
            parents = {}
            for node in _body_scope(funcdef):
                for child in ast.iter_child_nodes(node):
                    parents[child] = node
            for node in _body_scope(funcdef):
                if isinstance(node, ast.Name) and node.id == param and \
                        isinstance(node.ctx, ast.Load):
                    parent = parents.get(node)
                    if isinstance(parent, ast.BoolOp) and len(parent.values) > 1 and \
                            parent.values[0] is node:
                        fb = parent.values[1]
                        kind = classify_expr(fb, callee_module, corpus)
                        row["rescue_class"] = {
                            D_CONSTANT: R_GUARD_CONST, D_FOREIGN: R_GUARD_CONST,
                            D_READ: R_GUARD_READ, D_CALL: R_GUARD_READ,
                        }.get(kind, R_GUARD_OTHER)
                        row["rescue_source"] = _source_of(fb, callee_module, corpus,
                                                         callee_tree)
                        row["rescue_line"] = parent.lineno
                        break
            if not row["rescue_source"]:
                row["rescue_class"] = R_GUARD_OTHER
    else:
        row["rescue_source"] = _source_of(rescue_node, callee_module, corpus, callee_tree)
        if classify_expr(rescue_node, callee_module, corpus) in (D_CONSTANT, D_FOREIGN):
            row["rescue_chain"], row["rescue_terminal_class"] = constant_chain(
                rescue_node, callee_module, corpus)

    if row["default_class"] not in SENTINELS:
        row["rescue_class"] = R_VALUE

    holder = corpus.enclosing(module, row["line"]) or {}
    caller = holder.get("func")
    row["caller_function"] = caller
    if caller is not None:
        if param in corpus.param_names(module, caller):
            row["caller_could_have_supplied"] = C_OWN_PARAMETER
        elif param in (corpus.constants_of(module, caller) or []):
            row["caller_could_have_supplied"] = C_LOCAL
        elif corpus.lookup(module, param) is not None or param in _module_names(corpus, module):
            row["caller_could_have_supplied"] = C_MODULE_CONSTANT
    return row


def _default_node(funcdef, param):
    args = funcdef.args
    positional = [a.arg for a in getattr(args, "posonlyargs", []) or []] + \
        [a.arg for a in args.args]
    defaults = args.defaults or []
    if defaults and param in positional[-len(defaults):]:
        return defaults[positional.index(param) - (len(positional) - len(defaults))]
    kwonly = [a.arg for a in (args.kwonlyargs or [])]
    if param in kwonly:
        return (args.kw_defaults or [])[kwonly.index(param)]
    return None


# ------------------------------------------------------------------ summary / verdict
def _count(rows, key, vocab):
    out = dict((v, 0) for v in vocab)
    for row in rows:
        out[row.get(key)] = out.get(row.get(key), 0) + 1
    return out


def _summary(rows, sources, upstream=None):
    resolved = [r for r in rows if r["resolution"] == X_RESOLVED]
    return {
        "omission_sites_examined": len(rows),
        "sites_by_resolution": _count(rows, "resolution", RESOLUTION_VOCAB),
        "sites_by_default_class": _count(rows, "default_class", DEFAULT_VOCAB),
        "sites_by_rescue_class": _count(rows, "rescue_class", RESCUE_VOCAB),
        "sites_by_caller_could_have_supplied": _count(rows, "caller_could_have_supplied",
                                                     CALLER_VOCAB),
        "resolved_signatures": len(resolved),
        "defaults_that_are_a_sentinel": sum(
            1 for r in resolved if r["default_class"] in SENTINELS),
        "defaults_that_are_themselves_a_value": sum(
            1 for r in resolved if r["default_class"] in (D_LITERAL, D_CONSTANT, D_FOREIGN,
                                                          D_CALL, D_READ)),
        "sentinel_defaults_the_body_replaces": sum(
            1 for r in resolved if r["default_class"] in SENTINELS
            and r["rescue_class"] in RESCUED and r["rescue_class"] != R_VALUE),
        "sentinel_defaults_nothing_replaces": sum(
            1 for r in resolved if r["default_class"] in SENTINELS
            and r["rescue_class"] in (R_PASSED_ON, R_NEVER_READ)),
        "omissions_whose_caller_had_the_name_in_scope": sum(
            1 for r in resolved if r["caller_could_have_supplied"] != C_NOTHING),
        "distinct_callee_signatures": len(set(
            (r["callee_module"], r["callee"], r["parameter"]) for r in resolved)),
        "distinct_default_expressions": len(set(
            (r["callee_module"], r["callee"], r["parameter"], r["default_source"])
            for r in resolved)),
        "upstream_faces": upstream or [],
        "sources_read": sources,
    }


def _verdict(summary):
    if not summary["omission_sites_examined"]:
        return V_EMPTY
    if not summary["resolved_signatures"]:
        return V_UNRESOLVED
    if summary["defaults_that_are_themselves_a_value"]:
        return V_VALUE
    if summary["sentinel_defaults_nothing_replaces"]:
        return V_UNRESCUED
    return V_RESCUED


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


def build(root=None, write=True, rows=None, sources=None, upstream=None):
    root = root or ROOT
    if rows is None:
        faces = load_upstream(root)
        upstream = [{"path": f["path"], "study": f["study"], "sha256": f["sha256"]}
                    for f in faces]
        corpus = e520.ForwardCorpus(root)
        rows = [analyse_site(site, corpus) for site in population(faces)]
        sources = len(corpus_files(root)) if sources is None else sources
    summary = _summary(rows, sources or 0, upstream)
    face = {
        "study": STUDY,
        "card": CARD,
        "title": ("what does the signature default that E530/E526 landed on actually name, and "
                  "does the body ever replace it"),
        "generated": _now(),
        "evidence_cutoff": DATE_STAMP,
        "population_source": ("%s::population() -- every omission site published as the signature "
                              "default by E530's chains and E526's hop sites, deduplicated by "
                              "(caller module, line, callee, parameter)" % os.path.basename(__file__)),
        "upstream_faces": upstream or [],
        "method_limits": [
            "a name that no import binds (or whose receiver is not a name) is published as a name "
            "collision, never resolved: the same function name in another module is a different "
            "signature and merging the two would invent a population",
            "the rescue is read from the defining function's own body only: a substitute supplied "
            "by a caller one hop out is out of scope and stays published as the sentinel it is",
            "a guarded use is one where the parameter is the first operand of `p or X` or the body "
            "of `p if p is not None else X`; a guard written any other way is published as "
            "passed_on_unchanged rather than guessed",
            "a constant chain follows module-level `Name = <Name|Attribute>` hops up to %d and "
            "stops at anything else; the terminal class is published beside the chain"
            % MAX_CONSTANT_HOPS,
            "nothing is executed and no source is rewritten",
            "sources_read is a snapshot of a live tree other lanes write to; it is published but "
            "not gated, while every class and the verdict are re-derived",
        ],
        "summary": summary,
        "verdict": _verdict(summary),
        "verdict_vocab": list(VERDICT_VOCAB),
        "default_vocab": list(DEFAULT_VOCAB),
        "rescue_vocab": list(RESCUE_VOCAB),
        "resolution_vocab": list(RESOLUTION_VOCAB),
        "sites": rows,
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
                "upstream_faces", "summary", "verdict", "sites", "method_limits",
                "default_vocab", "rescue_vocab", "resolution_vocab"):
        if key not in face:
            bad.append("the face does not publish %s" % key)
    if face.get("study") != STUDY:
        bad.append("the face is not this study")
    if "::population()" not in str(face.get("population_source") or ""):
        bad.append("the population_source is not this study's population function")
    if face.get("verdict") not in VERDICT_VOCAB:
        bad.append("the verdict %r is not in the vocabulary" % face.get("verdict"))
    summary = face.get("summary") or {}
    rows = face.get("sites") or []
    if face.get("verdict") != _verdict(summary):
        bad.append("the published verdict does not re-derive from the summary")
    if summary.get("omission_sites_examined") != len(rows):
        bad.append("the examined population does not add up")
    for row in rows:
        where = "%s:%s" % (row.get("caller_module"), row.get("line"))
        if row.get("resolution") not in RESOLUTION_VOCAB:
            bad.append("%s publishes resolution %r outside the vocabulary"
                       % (where, row.get("resolution")))
        if row.get("resolution") != X_RESOLVED:
            if row.get("default_class") != D_NO_DEFAULT:
                bad.append("%s is unresolved but publishes a default class" % where)
            continue
        if row.get("default_class") not in DEFAULT_VOCAB:
            bad.append("%s publishes default class %r outside the vocabulary"
                       % (where, row.get("default_class")))
        if row.get("default_class") == D_NO_DEFAULT:
            bad.append("%s resolves to a signature that carries no default" % where)
        if row.get("rescue_class") not in RESCUE_VOCAB:
            bad.append("%s publishes rescue class %r outside the vocabulary"
                       % (where, row.get("rescue_class")))
        if row.get("caller_could_have_supplied") not in CALLER_VOCAB:
            bad.append("%s publishes caller class %r outside the vocabulary"
                       % (where, row.get("caller_could_have_supplied")))
        if row.get("default_class") not in SENTINELS and row.get("rescue_class") != R_VALUE:
            bad.append("%s has a value default but publishes a rescue" % where)
        if row.get("default_class") in SENTINELS and row.get("rescue_class") == R_VALUE:
            bad.append("%s has a sentinel default but is published as already a value" % where)
        if row.get("rescue_class") in (R_REBIND_CONST, R_REBIND_CALL, R_REBIND_READ,
                                       R_GUARD_CONST, R_GUARD_READ) and not row.get("rescue_source"):
            bad.append("%s publishes a rescue but no rescue source" % where)
        if row.get("default_class") in SENTINELS and row.get("param_echo") is not None:
            bad.append("%s echoes its parameter in a field that is not the parameter" % where)
        if row.get("caller_could_have_supplied") != C_NOTHING and not row.get("caller_function"):
            bad.append("%s says the caller holds the name but names no caller" % where)
    recomputed = _summary(rows, summary.get("sources_read") or 0,
                          summary.get("upstream_faces"))
    for key in ("sites_by_resolution", "sites_by_default_class", "sites_by_rescue_class",
                "sites_by_caller_could_have_supplied", "resolved_signatures",
                "defaults_that_are_a_sentinel", "defaults_that_are_themselves_a_value",
                "sentinel_defaults_the_body_replaces", "sentinel_defaults_nothing_replaces",
                "omissions_whose_caller_had_the_name_in_scope", "distinct_callee_signatures",
                "distinct_default_expressions"):
        if recomputed.get(key) != summary.get(key):
            bad.append("the summary key %s does not re-derive from the sites" % key)
    return bad


def check(face=None, root=None):
    face = face or load_face(root)
    bad = face_problems(face, root)
    print("E531 check: %d problem(s)" % len(bad))
    for line in bad[:20]:
        print("  - %s" % line)
    return 1 if bad else 0


def verify(root=None):
    published = load_face(root)
    fresh = build(root=root, write=False)
    bad = face_problems(published, root)
    if fresh["verdict"] != published["verdict"]:
        bad.append("the verdict drifts when re-derived")
    volatile = ("sources_read", "omission_sites_examined", "sites_by_resolution",
                "sites_by_default_class", "sites_by_rescue_class",
                "sites_by_caller_could_have_supplied", "resolved_signatures",
                "defaults_that_are_a_sentinel", "defaults_that_are_themselves_a_value",
                "sentinel_defaults_the_body_replaces", "sentinel_defaults_nothing_replaces",
                "omissions_whose_caller_had_the_name_in_scope", "distinct_callee_signatures",
                "distinct_default_expressions")
    trimmed = {k: v for k, v in fresh["summary"].items() if k not in volatile}
    pinned = {k: v for k, v in published["summary"].items() if k not in volatile}
    if json.dumps(trimmed, sort_keys=True) != json.dumps(pinned, sort_keys=True):
        moved = sorted(k for k in set(trimmed) | set(pinned) if trimmed.get(k) != pinned.get(k))
        bad.append("the summary drifts when re-derived: %r" % moved[:6])
    for key in volatile:
        if fresh["summary"].get(key) != published["summary"].get(key):
            print("  note: %s moved %r -> %r (live tree, not gated)"
                  % (key, published["summary"].get(key), fresh["summary"].get(key)))
    print("E531 verify: %d problem(s)" % len(bad))
    for line in bad[:20]:
        print("  - %s" % line)
    return 1 if bad else 0


# ------------------------------------------------------------------ selftest
FIXTURE = '''\
ROOT = "/repo"
CONST = {"a": 1}


def sink(value):
    return value


def sentinel_rebound_const(root=None):
    root = root or ROOT
    return sink(root)


def sentinel_rebound_call(index=None):
    index = index if index is not None else sink(index)
    return index


def sentinel_guarded(root=None):
    return sink(root or ROOT)


def sentinel_dropped(root=None):
    return sink("nothing")


def value_default(root="/repo"):
    return sink(root)


def callers():
    sentinel_rebound_const()
    sentinel_rebound_call()
    sentinel_guarded()
    sentinel_dropped()
    value_default()
'''


def _fixture_root():
    import tempfile
    d = tempfile.mkdtemp(prefix="e531_")
    os.makedirs(os.path.join(d, "scripts"))
    with io.open(os.path.join(d, "scripts", "fixture_mod.py"), "w", encoding="utf-8",
                 newline="\n") as fh:
        fh.write(FIXTURE)
    return d


def _line_of(root, needle):
    path = os.path.join(root, "scripts", "fixture_mod.py")
    for index, line in enumerate(io.open(path, encoding="utf-8").read().splitlines(), 1):
        if needle in line:
            return index
    raise AssertionError("fixture line %r not found" % needle)


def _fixture_sites(root):
    corpus = e520.ForwardCorpus(root)
    rows = []
    for callee, param in (("sentinel_rebound_const", "root"), ("sentinel_rebound_call", "index"),
                          ("sentinel_guarded", "root"), ("sentinel_dropped", "root"),
                          ("value_default", "root")):
        line = _line_of(root, "%s()" % callee)
        rows.append(analyse_site({"upstream_study": "fixture", "caller_module": "fixture_mod",
                                  "line": line, "callee": callee, "parameter": param,
                                  "chain_argument": param, "chain_shape": "fixture"}, corpus))
    return rows, corpus


def selftest():
    checks = []
    fails = []
    root = _fixture_root()

    def ok(name, cond, detail=""):
        checks.append(name)
        if not cond:
            fails.append("%s %s" % (name, detail))

    rows, corpus = _fixture_sites(root)
    by_callee = dict((r["callee"], r) for r in rows)

    ok("a call in the same module resolves to its own signature",
       all(r["resolution"] == X_RESOLVED for r in rows),
       [(r["callee"], r["resolution"]) for r in rows])
    ok("a None default is published as a sentinel",
       by_callee["sentinel_rebound_const"]["default_class"] == D_NONE,
       by_callee["sentinel_rebound_const"]["default_class"])
    ok("a literal default is published as a value, not a sentinel",
       by_callee["value_default"]["default_class"] == D_LITERAL,
       by_callee["value_default"]["default_class"])
    ok("a value default carries no rescue",
       by_callee["value_default"]["rescue_class"] == R_VALUE,
       by_callee["value_default"]["rescue_class"])
    ok("`p = p or CONST` is published as a rebinding from a module constant",
       by_callee["sentinel_rebound_const"]["rescue_class"] == R_REBIND_CONST,
       by_callee["sentinel_rebound_const"]["rescue_class"])
    ok("`p = p if p is not None else CALL` is published as a rebinding from a call",
       by_callee["sentinel_rebound_call"]["rescue_class"] == R_REBIND_CALL,
       by_callee["sentinel_rebound_call"]["rescue_class"])
    ok("`p or CONST` at the use site is published as a guard",
       by_callee["sentinel_guarded"]["rescue_class"] == R_GUARD_CONST,
       by_callee["sentinel_guarded"]["rescue_class"])
    ok("a sentinel the body never reads is published as dropped, not rescued",
       by_callee["sentinel_dropped"]["rescue_class"] in (R_NEVER_READ, R_PASSED_ON),
       by_callee["sentinel_dropped"]["rescue_class"])
    ok("a sentinel that is replaced is counted as rescued",
       by_callee["sentinel_rebound_const"]["rescue_class"] in RESCUED,
       by_callee["sentinel_rebound_const"]["rescue_class"])

    face = build(root=root, write=False, rows=rows, sources=0,
                 upstream=[{"path": "fixture", "study": "fixture", "sha256": "0" * 64}])
    ok("the fixture face has no problems", not face_problems(face), face_problems(face))
    ok("a literal default alongside the sentinels wins the verdict: the chain ends in the "
       "signature", face["verdict"] == V_VALUE, face["verdict"])

    sentinels_only = [dict(r) for r in rows if r["callee"] != "value_default"]
    dropped_face = build(root=root, write=False, rows=sentinels_only, sources=0,
                         upstream=[{"path": "fixture", "study": "fixture", "sha256": "0" * 64}])
    ok("one dropped sentinel moves the verdict away from 'every default is rescued'",
       dropped_face["verdict"] == V_UNRESCUED, dropped_face["verdict"])

    healed = [dict(r) for r in sentinels_only if r["callee"] != "sentinel_dropped"]
    healed_face = build(root=root, write=False, rows=healed, sources=0,
                        upstream=[{"path": "fixture", "study": "fixture", "sha256": "0" * 64}])
    ok("with only rescued sentinels the verdict is 'every default is rescued'",
       healed_face["verdict"] == V_RESCUED, healed_face["verdict"])

    doctored = json.loads(json.dumps(face))
    doctored["verdict"] = V_RESCUED
    ok("a verdict that does not re-derive is refused",
       any("verdict does not re-derive" in p for p in face_problems(doctored)),
       face_problems(doctored)[:3])

    doctored = json.loads(json.dumps(face))
    for row in doctored["sites"]:
        if row["callee"] == "sentinel_rebound_const":
            row["rescue_class"] = R_VALUE
    ok("a sentinel default published as already a value is refused",
       any("already a value" in p for p in face_problems(doctored)),
       face_problems(doctored)[:3])

    doctored = json.loads(json.dumps(face))
    for row in doctored["sites"]:
        if row["callee"] == "value_default":
            row["rescue_class"] = R_REBIND_CONST
    ok("a value default carrying a rescue is refused",
       any("but publishes a rescue" in p for p in face_problems(doctored)),
       face_problems(doctored)[:3])

    doctored = json.loads(json.dumps(face))
    for row in doctored["sites"]:
        if row["callee"] == "sentinel_rebound_call":
            row["rescue_source"] = None
    ok("a rescue published without its source is refused",
       any("no rescue source" in p for p in face_problems(doctored)),
       face_problems(doctored)[:3])

    doctored = json.loads(json.dumps(face))
    for row in doctored["sites"]:
        if row["callee"] == "sentinel_guarded":
            row["resolution"] = X_NAME_ONLY
            row["default_class"] = D_NONE
    ok("an unresolved site that still publishes a default class is refused",
       any("unresolved but publishes" in p for p in face_problems(doctored)),
       face_problems(doctored)[:3])

    empty = build(root=root, write=False, rows=[], sources=0,
                  upstream=[{"path": "fixture", "study": "fixture", "sha256": "0" * 64}])
    ok("an empty population is its own verdict", empty["verdict"] == V_EMPTY, empty["verdict"])

    print("E531 selftest: %d/%d checks passed" % (len(checks) - len(fails), len(checks)))
    for line in fails:
        print("  FAIL %s" % line)
    return 1 if fails else 0


def run():
    face = build()
    summary = face["summary"]
    print("E531 run: %d omission site(s) | verdict=%s"
          % (summary["omission_sites_examined"], face["verdict"]))
    print("  resolved signatures=%d of %d sites | sentinel defaults=%d | value defaults=%d"
          % (summary["resolved_signatures"], summary["omission_sites_examined"],
             summary["defaults_that_are_a_sentinel"], summary["defaults_that_are_themselves_a_value"]))
    print("  rescued=%d | nothing replaces=%d | caller had the name in scope=%d"
          % (summary["sentinel_defaults_the_body_replaces"],
             summary["sentinel_defaults_nothing_replaces"],
             summary["omissions_whose_caller_had_the_name_in_scope"]))
    print("  default classes: %r" % summary["sites_by_default_class"])
    print("  rescue classes: %r" % summary["sites_by_rescue_class"])
    return 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] not in ("run", "check", "verify", "selftest"):
        print(__doc__.strip().splitlines()[-4])
        return 2
    return {"run": run, "check": check, "verify": verify, "selftest": selftest}[argv[0]]()


if __name__ == "__main__":
    sys.exit(main())