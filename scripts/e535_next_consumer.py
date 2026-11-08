"""E535 (r1565 bm-b): is the sentinel a reader hands onward consumed by a caller that
writes a payload?

E534 (results/state_tilt/captopayload_latest.json) followed every depth-cap arm of E529 into
its reader and published, per call site, what the reader does with the value.  Five of those
sites only hand the value onward (three arms) and one assembles it into a field of a container
the reader never writes.  In all six cases the question "is the cap published as the claim that
the thing is not there" was left open by construction: E534's own limit says the next consumer
is not followed.

This study follows exactly those six sites one hop further.  For each site the hop kind is read
off the tree, not assumed:

  * the value leaves as the reader's own `return` -- the next consumers are the corpus call
    sites of that reader, attributed the same way E529 attributes a site (same module, or a
    module that imports its stem), and each is classified with E534's own reader classifier
  * the value leaves as an argument to a named call -- the receiving callee's definition is
    located in the corpus and the parameter at the passed position is followed with the same
    walk E534 uses on a bound name
  * the value sits in a named field of a container the reader never writes -- the container is
    followed first; if it never leaves the reader the field dies there, and that is its own
    class rather than a publication

Every row publishes its hop kind, the next consumer it landed on, and the disposition class of
that consumer.  "Handed onward" never stands in for "published", and a hop this scan cannot
follow is its own class with the reason named.

    python scripts/e535_next_consumer.py run        # build + write the face
    python scripts/e535_next_consumer.py check      # gate the published face (fast)
    python scripts/e535_next_consumer.py verify     # re-derive from the tree and gate
    python scripts/e535_next_consumer.py selftest   # fixture corpus + doctored faces
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

import e529_depth_cap_null as e529          # noqa: E402  corpus, parse, call naming
import e534_cap_to_payload as e534          # noqa: E402  reader classifier, flow walk

CARD = ("E535-WHICH-SENTINEL-A-READER-HANDS-ONWARD-IS-CONSUMED-BY-A-CALLER-THAT-WRITES-"
        "A-PAYLOAD")
STUDY = "E535_sentinel_next_consumer"
DATE_STAMP = "2026-11-08"
FACE_NAME = "nextconsumer_latest.json"
DATED_PREFIX = "NEXTCONSUMER"

SELF_EXCLUDED = ("e535_", "run_e535", "_e535", "NEXTCONSUMER", "nextconsumer_")

UPSTREAM_FACE = "results/state_tilt/captopayload_latest.json"
UPSTREAM_STUDY = e534.STUDY

# the E534 site classes this study exists to follow: handed onward, and the field-nobody-writes
FOLLOW_ON = (e534.C_FORWARDED, e534.C_PAYLOAD_FIELD_UNWRITTEN)

# ---------------------------------------------------------------- hop vocabulary
H_RETURN = "the_value_leaves_the_reader_as_its_own_return"
H_ARGUMENT = "the_value_leaves_the_reader_as_an_argument_to_a_named_call"
H_UNWRITTEN_FIELD = "the_value_sits_in_a_named_field_of_a_container_the_reader_never_writes"
H_UNRESOLVED = "the_hop_out_of_the_reader_could_not_be_named_statically"
HOP_VOCAB = (H_RETURN, H_ARGUMENT, H_UNWRITTEN_FIELD, H_UNRESOLVED)

# ---------------------------------------------------------------- disposition vocabulary
S_PAYLOAD_FIELD = "the_next_consumer_puts_the_value_in_a_named_field_of_a_payload_it_writes"
S_PAYLOAD_BODY = "the_next_consumer_writes_the_value_out_as_the_body_of_a_payload"
S_FIELD_UNWRITTEN = "the_next_consumer_assembles_a_named_field_and_writes_no_payload"
S_BODY_UNWRITTEN = "the_next_consumer_assembles_a_body_and_writes_no_payload"
S_SENTENCE = "the_next_consumer_folds_the_value_into_a_sentence_a_human_reads"
S_COUNTED = "the_next_consumer_turns_the_value_into_a_counted_quantity"
S_TESTED = "the_next_consumer_only_tests_the_value_against_the_same_null"
S_FORWARDED = "the_next_consumer_hands_the_value_on_again"
S_DISCARDED = "the_next_consumer_discards_the_value"
S_BOUND_NEVER_READ = "the_value_is_bound_in_the_next_consumer_and_never_read"
S_STOPS = "the_value_stops_inside_the_next_consumer"
S_NO_CONSUMER = "no_consumer_of_the_reader_exists_in_the_corpus"
S_CALLEE_NOT_DEFINED = "the_receiving_callee_is_not_defined_in_this_corpus"
S_FIELD_DEAD = "the_container_never_leaves_the_reader_so_the_field_dies_there"
S_BUILTIN_TEST = ("the_value_is_tested_inline_by_a_builtin_type_or_length_test_so_the_hop_never_"
                  "leaves_the_reader")
S_LIBRARY_CALL = "the_value_is_handed_to_a_library_call_whose_body_this_corpus_cannot_read"
S_SEPARATED_IN_THE_READER = (
    "the_read_sits_inside_a_branch_that_already_separated_the_null_from_the_absence")
S_UNRESOLVED = "the_next_consumer_could_not_be_followed_statically"
S_VOCAB = (S_PAYLOAD_FIELD, S_PAYLOAD_BODY, S_SENTENCE, S_COUNTED, S_FIELD_UNWRITTEN,
           S_BODY_UNWRITTEN, S_TESTED, S_BUILTIN_TEST, S_LIBRARY_CALL, S_SEPARATED_IN_THE_READER,
           S_FORWARDED, S_DISCARDED, S_BOUND_NEVER_READ, S_STOPS,
           S_NO_CONSUMER, S_CALLEE_NOT_DEFINED, S_FIELD_DEAD, S_UNRESOLVED)

# precedence: the most load-bearing disposition a row carries decides its class
_PRIMARY = (S_PAYLOAD_FIELD, S_PAYLOAD_BODY, S_SENTENCE, S_COUNTED, S_FIELD_UNWRITTEN,
            S_BODY_UNWRITTEN, S_SEPARATED_IN_THE_READER, S_BUILTIN_TEST, S_LIBRARY_CALL,
            S_FORWARDED, S_TESTED, S_BOUND_NEVER_READ, S_DISCARDED,
            S_NO_CONSUMER, S_CALLEE_NOT_DEFINED, S_FIELD_DEAD, S_STOPS, S_UNRESOLVED)

PUBLISHED_CLASSES = (S_PAYLOAD_FIELD, S_PAYLOAD_BODY, S_SENTENCE, S_COUNTED)

# a call whose body is not in this corpus and which only tests its argument
INLINE_TEST_BUILTINS = {"isinstance", "issubclass", "len", "bool", "all", "any", "hasattr",
                        "callable", "type"}
# a call whose body is not in this corpus and which transforms its argument
LIBRARY_TRANSFORMS = {"sorted", "set", "frozenset", "list", "tuple", "dict", "str", "int",
                      "float", "repr", "join", "reversed", "enumerate", "zip", "map", "filter"}

# E534 chain class -> this study's disposition, so the second hop is read by one vocabulary
_FROM_E534 = {
    e534.C_PAYLOAD_FIELD: S_PAYLOAD_FIELD,
    e534.C_PAYLOAD_BODY: S_PAYLOAD_BODY,
    e534.C_PAYLOAD_FIELD_UNWRITTEN: S_FIELD_UNWRITTEN,
    e534.C_PAYLOAD_BODY_UNWRITTEN: S_BODY_UNWRITTEN,
    e534.C_SENTENCE: S_SENTENCE,
    e534.C_COUNTED: S_COUNTED,
    e534.C_TESTED: S_TESTED,
    e534.C_FORWARDED: S_FORWARDED,
    e534.C_DISCARDED: S_DISCARDED,
    e534.C_BOUND_NEVER_READ: S_BOUND_NEVER_READ,
    e534.C_STOPS_ELSEWHERE: S_STOPS,
    e534.C_UNRESOLVED: S_UNRESOLVED,
}

V_PUBLISHED_TWO_HOPS_OUT = \
    ("a_sentinel_no_reader_in_the_population_tests_is_published_as_absence_by_a_consumer_two_" \
     "hops_out")
V_ASSEMBLED_TWO_HOPS_OUT = \
    "the_second_consumer_assembles_a_field_and_writes_no_payload_either"
V_DIES_IN_A_SECOND_READER = \
    "every_sentinel_handed_onward_dies_in_its_second_consumer"
V_CHAIN_STILL_MOVING = "the_sentinel_is_still_being_forwarded_one_hop_out"
V_NO_SECOND_READER = \
    ("the_handed_on_class_holds_no_second_reader_so_no_sentinel_is_published_two_hops_out")
V_SPLIT_BY_SHAPE = \
    ("the_handed_on_class_is_not_one_shape_part_of_it_never_reaches_a_second_reader_and_part_"
     "is_still_moving")
V_EMPTY = "the_upstream_face_carries_no_site_in_the_two_follow_on_classes"
VERDICT_VOCAB = (V_PUBLISHED_TWO_HOPS_OUT, V_ASSEMBLED_TWO_HOPS_OUT, V_CHAIN_STILL_MOVING,
                 V_DIES_IN_A_SECOND_READER, V_NO_SECOND_READER, V_SPLIT_BY_SHAPE, V_EMPTY)


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
    """E534 sites that only hand the value onward, plus the field no reader writes."""
    rows = []
    for arm in face.get("arms") or []:
        for site in arm.get("sites") or []:
            if site.get("chain") not in FOLLOW_ON:
                continue
            row = {
                "module": arm.get("module"),
                "function": arm.get("function"),
                "counter": arm.get("counter"),
                "sentinel": arm.get("sentinel"),
                "e529_reader_class": arm.get("distinguish"),
                "e534_chain": site.get("chain"),
                "reader_function": site.get("caller"),
                "site_line": site.get("line"),
                "callee": site.get("callee"),
                "e534_terminal_classes": list(site.get("terminal_classes") or []),
                "e534_payload_keys": list(site.get("payload_keys") or []),
            }
            rows.append(row)
    rows.sort(key=lambda r: (r["module"] or "", r["reader_function"] or "", r["site_line"] or 0))
    return rows


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


def _stem(rel):
    return os.path.splitext(os.path.basename(rel))[0]


def consumers_of(trees, reader, owner_module):
    """Corpus call sites of `reader`, attributed by module equality or by importing its stem."""
    stem = _stem(owner_module)
    out = []
    for rel, tree in trees:
        if _stem(rel) != stem and stem not in e529._imports(tree):
            continue
        parents = e529._parents(tree)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if e529._call_name(node) != reader:
                continue
            fn = e529._enclosing_function(node, parents, tree)
            out.append({"module": rel, "line": getattr(node, "lineno", 0), "callee": reader,
                        "caller": getattr(fn, "name", None)})
    out.sort(key=lambda s: (s["module"], s["line"]))
    return out


def _hop_from(node, parents):
    """Walk outward from the call that produced the value: how does it leave the reader?"""
    cur = node
    for _ in range(40):
        par = parents.get(cur)
        if par is None:
            break
        if isinstance(par, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Module, ast.ClassDef)):
            break
        if isinstance(par, ast.Return) and par.value is cur:
            return H_RETURN, {"via": "return", "detail_line": getattr(par, "lineno", 0)}
        if isinstance(par, ast.Call):
            pos = None
            for i, arg in enumerate(par.args):
                if arg is cur:
                    pos = i
            kw = None
            for key in par.keywords:
                if key.value is cur:
                    kw = key.arg
            if pos is not None or kw is not None:
                return H_ARGUMENT, {"via": "argument", "callee": e529._call_name(par),
                                    "position": pos, "keyword": kw,
                                    "detail_line": getattr(par, "lineno", 0)}
        if isinstance(par, ast.Dict) and any(v is cur for v in par.values):
            idx = [i for i, v in enumerate(par.values) if v is cur][0]
            key_node = par.keys[idx] if idx < len(par.keys) else None
            key = key_node.value if isinstance(key_node, ast.Constant) \
                and isinstance(key_node.value, str) else None
            return H_UNWRITTEN_FIELD, {"via": "dict_literal", "key": key,
                                       "container": None, "node": par}
        if isinstance(par, ast.Subscript) and isinstance(par.ctx, ast.Store) and par.value is cur:
            return H_UNWRITTEN_FIELD, {"via": "subscript_store", "key": e534._key_of(par),
                                       "container": getattr(par.value, "id", None),
                                       "node": par}
        cur = par
    return H_UNRESOLVED, {}


def _origins(call, parents, fn):
    """The call itself, plus every later read of a name it was bound to.

    E534's own flow walk classifies a site from the bound NAME as well as from the call node,
    so a value that is stored and only handed on three lines later is a forward there.  The hop
    has to start from the same places, otherwise a stored-then-passed value reads as a hop this
    scan never followed.
    """
    nodes = [call]
    bound = None
    bind_line = None
    par = parents.get(call)
    if isinstance(par, ast.Assign):
        for target in par.targets:
            if isinstance(target, ast.Name):
                bound = target.id
        bind_line = getattr(par, "lineno", 0)
    elif isinstance(par, ast.AnnAssign) and isinstance(par.target, ast.Name):
        bound = par.target.id
        bind_line = getattr(par, "lineno", 0)
    if bound is not None and fn is not None:
        rebind = None
        for node in ast.walk(fn):
            if not isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                continue
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if not any(isinstance(t, ast.Name) and t.id == bound for t in targets):
                continue
            line = getattr(node, "lineno", 0)
            if line <= bind_line:
                continue
            rebind = line if rebind is None else min(rebind, line)
        for node in ast.walk(fn):
            if isinstance(node, ast.Name) and node.id == bound \
                    and isinstance(node.ctx, ast.Load):
                line = getattr(node, "lineno", 0)
                if line <= bind_line:
                    continue
                if rebind is not None and line >= rebind:
                    continue
                nodes.append(node)
    return bound, nodes


_HOP_PRIORITY = (H_ARGUMENT, H_RETURN, H_UNWRITTEN_FIELD)


def _guard_on(node, parents, name):
    """Is this read inside a branch whose own test already separated `name` from None?"""
    if not name:
        return None
    cur = node
    for _ in range(60):
        par = parents.get(cur)
        if par is None:
            break
        if isinstance(par, ast.If) and any(cur is stmt for stmt in par.body):
            test = par.test
            for sub in ast.walk(test):
                if isinstance(sub, ast.Compare):
                    operands = [sub.left] + list(sub.comparators)
                    if any(isinstance(o, ast.Name) and o.id == name for o in operands):
                        ops = [type(o) for o in sub.ops]
                        if ast.IsNot in ops or ast.NotEq in ops or ast.Gt in ops \
                                or ast.GtE in ops:
                            return {"line": getattr(par, "lineno", 0),
                                    "test": _test_text(test)}
                if isinstance(test, ast.Name) and test.id == name:
                    return {"line": getattr(par, "lineno", 0), "test": _test_text(test)}
                if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not) \
                        and isinstance(test.operand, ast.Name) and test.operand.id == name:
                    return {"line": getattr(par, "lineno", 0), "test": _test_text(test)}
        cur = par
    return None


def _test_text(node):
    try:
        return ast.unparse(node)
    except Exception:                                   # pragma: no cover - old pythons
        return "a test this scan cannot print"


def _hop_of_site(call, parents, fn):
    """Every hop out of the reader this site expresses, and the one that leads the row."""
    bound, nodes = _origins(call, parents, fn)
    found = []
    guard = None
    for node in nodes:
        hop, detail = _hop_from(node, parents)
        if hop == H_UNRESOLVED:
            continue
        if any((h == hop and d.get("callee") == detail.get("callee")
                and d.get("position") == detail.get("position")
                and d.get("keyword") == detail.get("keyword")
                and d.get("key") == detail.get("key")) for h, d in found):
            continue
        found.append((hop, detail))
        if guard is None:
            guard = _guard_on(node, parents, bound)
    if not found:
        return H_UNRESOLVED, {}, bound, [], None
    primary = None
    for want in _HOP_PRIORITY:
        for hop, detail in found:
            if hop == want:
                primary = (hop, detail)
                break
        if primary:
            break
    hops_all = sorted({hop for hop, _ in found})
    return primary[0], primary[1], bound, hops_all, guard


def _consumer_chain(trees, site, sentinel):
    """E534's own classifier, plus one binding shape it cannot see: tuple destructuring.

    E519's published lesson is that `a, b = f()` binds names its assignment scan records only
    when the target is an ast.Name.  A second hop that destructures its source therefore reads
    as "stops inside", which is the instrument's shape and not the value's fate.
    """
    got = e534.classify_site(trees, site, sentinel)
    classes = list(got.get("terminal_classes") or [])
    if classes and e534.C_STOPS_ELSEWHERE not in classes:
        return got
    call, fn, parents, tree = e534.find_call(trees, site["module"], site["line"],
                                             site["callee"], site.get("caller"))
    if call is None or fn is None:
        return got
    names, line = [], None
    par = parents.get(call)
    if isinstance(par, ast.Assign) and len(par.targets) == 1 \
            and isinstance(par.targets[0], ast.Tuple):
        # `a, b = f()`: the call IS the value and every target name receives a piece of it
        names = [elt.id for elt in par.targets[0].elts if isinstance(elt, ast.Name)]
        line = getattr(par, "lineno", 0)
    elif isinstance(par, ast.Tuple):
        # `x = (f(), 0)`: the call is one element of the tuple that is being unpacked
        holder = parents.get(par)
        targets = None
        if isinstance(holder, ast.Assign) and len(holder.targets) == 1:
            targets = holder.targets[0]
        elif isinstance(holder, ast.AnnAssign):
            targets = holder.target
        if isinstance(targets, ast.Tuple):
            idx = [i for i, elt in enumerate(par.elts) if elt is call]
            if idx:
                i = idx[0]
                if i < len(targets.elts) and isinstance(targets.elts[i], ast.Name):
                    names = [targets.elts[i].id]
                    line = getattr(holder, "lineno", 0)
    if not names:
        return got
    reached, keys = set(), []
    for name in names:
        got_reached, got_keys = e534.flow_of(fn, name, line, parents)
        reached |= got_reached
        keys.extend(got_keys)
    writes = e534._writes_a_payload(fn)
    if e534.C_PAYLOAD_FIELD in reached and not writes:
        reached = (reached - {e534.C_PAYLOAD_FIELD}) | {e534.C_PAYLOAD_FIELD_UNWRITTEN}
    if e534.C_PAYLOAD_BODY in reached and not writes:
        reached = (reached - {e534.C_PAYLOAD_BODY}) | {e534.C_PAYLOAD_BODY_UNWRITTEN}
    return {"reader_writes_a_payload": writes, "terminal_classes": sorted(reached),
            "payload_keys": sorted(set(keys)),
            "bound_by_destructuring": ",".join(names)}


def _container_name(detail, parents):
    name = detail.get("container")
    if name:
        return name
    node = detail.get("node")
    cur = node
    for _ in range(10):
        if cur is None:
            return None
        par = parents.get(cur)
        if par is None:
            return None
        if isinstance(par, ast.Assign):
            for target in par.targets:
                if isinstance(target, ast.Name):
                    return target.id
            return None
        if isinstance(par, (ast.AnnAssign, ast.AugAssign)) and isinstance(par.target, ast.Name):
            return par.target.id
        cur = par
    return None


def _s_classes(c_classes):
    return {_FROM_E534.get(k, S_UNRESOLVED) for k in c_classes}


def _primary(classes):
    for klass in _PRIMARY:
        if klass in classes:
            return klass
    return S_UNRESOLVED


def _defs(trees):
    defs = {}
    for rel, tree in trees:
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                defs.setdefault(node.name, []).append((rel, node))
    return defs


def _resolve_callee(trees, defs, callee, owner_module):
    """The receiving callee's definition, attributed the same way a call site is."""
    stem = _stem(owner_module)
    hits = []
    for rel, fn in defs.get(callee) or []:
        if rel == owner_module:
            hits.append((rel, fn))
            continue
        tree = dict((r, t) for r, t in trees).get(rel)
        if tree is not None and stem in e529._imports(tree):
            hits.append((rel, fn))
    hits.sort(key=lambda pair: (pair[0], getattr(pair[1], "lineno", 0)))
    return hits[0] if hits else None


def _param_name(fn, position, keyword):
    if keyword:
        names = [a.arg for a in fn.args.args] + [a.arg for a in fn.args.kwonlyargs]
        return keyword if keyword in names else None
    if position is None:
        return None
    args = list(fn.args.posonlyargs) + list(fn.args.args)
    if position < len(args):
        return args[position].arg
    return None


def follow_row(trees, defs, row):
    rec = dict(row)
    rec.update({"hop": H_UNRESOLVED, "hop_detail": {}, "hops_found": [], "guard": None,
                "bound_name": None, "next_consumer": None,
                "next_consumer_module": None, "next_consumer_writes_a_payload": None,
                "dispositions": [], "disposition": S_UNRESOLVED, "consumer_sites": [],
                "note": None})
    call, fn, parents, tree = e534.find_call(trees, row["module"], row["site_line"],
                                             row["callee"], row["reader_function"])
    if call is None or tree is None:
        rec["note"] = "the E534 call site is not locatable in this tree"
        return rec
    hop, detail, bound, hops_all, guard = _hop_of_site(call, parents, fn)
    rec["hop"] = hop
    rec["hops_found"] = hops_all
    rec["bound_name"] = bound
    rec["guard"] = guard
    rec["hop_detail"] = {k: v for k, v in detail.items() if k != "node"}
    if guard:
        rec["dispositions"] = [S_SEPARATED_IN_THE_READER]
        rec["disposition"] = S_SEPARATED_IN_THE_READER
        rec["note"] = ("the read sits inside %s at line %s in the reader itself, so the "
                       "null arm never reaches this hop" % (guard.get("test"),
                                                          guard.get("line")))
        return rec
    if hop == H_RETURN:
        sites = consumers_of(trees, row["reader_function"], row["module"])
        traced = []
        for site in sites:
            got = _consumer_chain(trees, site, row.get("sentinel"))
            traced.append({"module": site["module"], "line": site["line"],
                           "caller": site["caller"],
                           "writes_a_payload": got.get("reader_writes_a_payload"),
                           "e534_dispositions": got.get("terminal_classes") or [],
                           "disposition": _primary(_s_classes(got.get("terminal_classes") or [])),
                           "payload_keys": got.get("payload_keys") or []})
        rec["consumer_sites"] = traced
        if not traced:
            rec["dispositions"] = [S_NO_CONSUMER]
            rec["disposition"] = S_NO_CONSUMER
            rec["note"] = "no corpus call site of %s could be attributed" % row["reader_function"]
            return rec
        classes = {t["disposition"] for t in traced}
        rec["next_consumer"] = row["reader_function"]
        rec["next_consumer_module"] = ", ".join(sorted({t["module"] for t in traced}))
        rec["next_consumer_writes_a_payload"] = any(t["writes_a_payload"] for t in traced)
        rec["dispositions"] = sorted(classes)
        rec["disposition"] = _primary(classes)
        return rec
    if hop == H_ARGUMENT:
        callee = detail.get("callee")
        if callee in INLINE_TEST_BUILTINS:
            rec["next_consumer"] = callee
            rec["dispositions"] = [S_BUILTIN_TEST]
            rec["disposition"] = S_BUILTIN_TEST
            rec["note"] = ("%s is a builtin test: the value is tested inline and the hop never "
                           "leaves the reader" % callee)
            return rec
        if callee in LIBRARY_TRANSFORMS:
            rec["next_consumer"] = callee
            rec["dispositions"] = [S_LIBRARY_CALL]
            rec["disposition"] = S_LIBRARY_CALL
            rec["note"] = ("%s is a library call whose body is not in this corpus, so what its "
                           "result feeds is not measured here" % callee)
            return rec
        hit = _resolve_callee(trees, defs, callee, row["module"])
        if hit is None:
            rec["dispositions"] = [S_CALLEE_NOT_DEFINED]
            rec["disposition"] = S_CALLEE_NOT_DEFINED
            rec["next_consumer"] = callee
            rec["note"] = "the receiving callee is not defined under scripts/Tools/firm/live/monitor"
            return rec
        rel, callee_fn = hit
        param = _param_name(callee_fn, detail.get("position"), detail.get("keyword"))
        rec["next_consumer"] = callee
        rec["next_consumer_module"] = rel
        rec["hop_detail"]["parameter"] = param
        if param is None:
            rec["dispositions"] = [S_UNRESOLVED]
            rec["disposition"] = S_UNRESOLVED
            rec["note"] = "the passed position does not land on a named parameter"
            return rec
        callee_tree = dict(trees).get(rel)
        callee_parents = e529._parents(callee_tree) if callee_tree is not None else {}
        classes_c, keys = e534.flow_of(callee_fn, param, -1, callee_parents)
        rec["next_consumer_writes_a_payload"] = e534._writes_a_payload(callee_fn)
        rec["hop_detail"]["payload_keys"] = keys
        classes = _s_classes(classes_c)
        if S_FIELD_UNWRITTEN in classes and not rec["next_consumer_writes_a_payload"]:
            pass
        if S_PAYLOAD_FIELD in classes and not rec["next_consumer_writes_a_payload"]:
            classes = (classes - {S_PAYLOAD_FIELD}) | {S_FIELD_UNWRITTEN}
        if S_PAYLOAD_BODY in classes and not rec["next_consumer_writes_a_payload"]:
            classes = (classes - {S_PAYLOAD_BODY}) | {S_BODY_UNWRITTEN}
        if callee in INLINE_TEST_BUILTINS:
            rec["dispositions"] = [S_BUILTIN_TEST]
            rec["disposition"] = S_BUILTIN_TEST
            rec["note"] = ("%s(%s, ...) is a builtin test: the value is tested inline "
                           "and the hop never leaves the reader" % (callee, param))
            return rec
        if callee in LIBRARY_TRANSFORMS:
            rec["dispositions"] = [S_LIBRARY_CALL]
            rec["disposition"] = S_LIBRARY_CALL
            rec["note"] = ("%s is a library call whose body is not in this corpus, so "
                           "what its result feeds is not measured here" % callee)
            return rec
        rec["dispositions"] = sorted(classes)
        rec["disposition"] = _primary(classes)
        return rec
    if hop == H_UNWRITTEN_FIELD:
        container = _container_name(detail, parents)
        rec["hop_detail"]["container"] = container
        if container is None or fn is None:
            rec["dispositions"] = [S_UNRESOLVED]
            rec["disposition"] = S_UNRESOLVED
            rec["note"] = "the container of the field is not a name this scan can follow"
            return rec
        returned = any(isinstance(n, ast.Return) and isinstance(n.value, ast.Name)
                       and n.value.id == container for n in ast.walk(fn))
        if not returned:
            rec["dispositions"] = [S_FIELD_DEAD]
            rec["disposition"] = S_FIELD_DEAD
            rec["next_consumer"] = None
            rec["note"] = "container %r never leaves %s" % (container, row["reader_function"])
            return rec
        sites = consumers_of(trees, row["reader_function"], row["module"])
        traced = []
        for site in sites:
            got = _consumer_chain(trees, site, row.get("sentinel"))
            traced.append({"module": site["module"], "line": site["line"],
                           "caller": site["caller"],
                           "writes_a_payload": got.get("reader_writes_a_payload"),
                           "e534_dispositions": got.get("terminal_classes") or [],
                           "disposition": _primary(_s_classes(got.get("terminal_classes") or [])),
                           "payload_keys": got.get("payload_keys") or []})
        rec["consumer_sites"] = traced
        if not traced:
            rec["dispositions"] = [S_NO_CONSUMER]
            rec["disposition"] = S_NO_CONSUMER
            rec["note"] = "container %r returns but no corpus caller exists" % container
            return rec
        classes = {t["disposition"] for t in traced}
        rec["next_consumer"] = row["reader_function"]
        rec["next_consumer_module"] = ", ".join(sorted({t["module"] for t in traced}))
        rec["next_consumer_writes_a_payload"] = any(t["writes_a_payload"] for t in traced)
        rec["dispositions"] = sorted(classes)
        rec["disposition"] = _primary(classes)
        return rec
    rec["note"] = "the value stops inside the reader or leaves by a form this scan does not name"
    return rec


def follow(trees, rows):
    defs = _defs(trees)
    out = [follow_row(trees, defs, row) for row in rows]
    out.sort(key=lambda r: (r["module"] or "", r["reader_function"] or "", r["site_line"] or 0))
    return out


# ------------------------------------------------------------------ face
def _count(records, key, vocab):
    got = {k: 0 for k in vocab}
    for rec in records:
        value = rec.get(key)
        if value in got:
            got[value] += 1
    return got


def _summary(rows, sources, failures):
    by_disposition = _count(rows, "disposition", S_VOCAB)
    return {
        "sources_read": sources,
        "parse_failures": len(failures),
        "sites_in_population": len(rows),
        "sites_by_disposition": by_disposition,
        "sites_by_hop": _count(rows, "hop", HOP_VOCAB),
        "sites_by_e534_class": _count(rows, "e534_chain", FOLLOW_ON),
        "sites_published_two_hops_out": sum(by_disposition[k] for k in PUBLISHED_CLASSES),
        "sites_whose_second_consumer_assembles_without_writing":
            by_disposition[S_FIELD_UNWRITTEN] + by_disposition[S_BODY_UNWRITTEN],
        "sites_that_die_in_a_second_reader": by_disposition[S_NO_CONSUMER] +
            by_disposition[S_FIELD_DEAD] + by_disposition[S_DISCARDED] +
            by_disposition[S_BOUND_NEVER_READ] + by_disposition[S_STOPS],
        "sites_still_forwarded": by_disposition[S_FORWARDED],
        "sites_only_tested": by_disposition[S_TESTED],
        "sites_with_no_defined_callee": by_disposition[S_CALLEE_NOT_DEFINED],
        "sites_whose_hop_is_a_builtin_test": by_disposition[S_BUILTIN_TEST],
        "sites_whose_hop_is_a_library_call": by_disposition[S_LIBRARY_CALL],
        "sites_separated_by_a_guard_inside_the_reader": by_disposition[S_SEPARATED_IN_THE_READER],
        "sites_that_never_leave_the_reader_at_the_second_hop":
            by_disposition[S_BUILTIN_TEST] + by_disposition[S_LIBRARY_CALL] +
            by_disposition[S_SEPARATED_IN_THE_READER],
        "sites_unresolved": by_disposition[S_UNRESOLVED],
        "next_consumers_named": sorted({r.get("next_consumer") for r in rows
                                        if r.get("next_consumer")}),
        "payload_keys_named": sorted({k for r in rows
                                      for k in ((r.get("hop_detail") or {}).get("payload_keys")
                                                or [])}),
        "consumer_sites_followed": sum(len(r.get("consumer_sites") or []) for r in rows),
        "rows_that_publish_no_disposition": len([r for r in rows if not r.get("disposition")]),
    }


def _verdict(summary):
    if not summary["sites_in_population"]:
        return V_EMPTY
    if summary["sites_published_two_hops_out"]:
        return V_PUBLISHED_TWO_HOPS_OUT
    if summary["sites_whose_second_consumer_assembles_without_writing"]:
        return V_ASSEMBLED_TWO_HOPS_OUT
    total = summary["sites_in_population"]
    never = summary["sites_that_never_leave_the_reader_at_the_second_hop"]
    if summary["sites_still_forwarded"] and never:
        return V_SPLIT_BY_SHAPE
    if summary["sites_still_forwarded"]:
        return V_CHAIN_STILL_MOVING
    if never == total:
        return V_NO_SECOND_READER
    if summary["sites_that_die_in_a_second_reader"] == total:
        return V_DIES_IN_A_SECOND_READER
    return V_NO_SECOND_READER


def build(root=None, write=True, rows=None, sources=None, failures=None, upstream_sha=None):
    root = root or ROOT
    if rows is None:
        face, sha = load_upstream(root)
        rows = population(face)
        upstream_sha = upstream_sha or sha
        trees, failed = parse(corpus_rels(root), root)
        rows = follow(trees, rows)
        sources = len(trees) if sources is None else sources
        failures = failed if failures is None else failures
    summary = _summary(rows, sources or 0, failures or [])
    face = {
        "study": STUDY,
        "card": CARD,
        "title": ("is a sentinel handed onward by a reader that never tests it consumed by a "
                  "caller that writes a payload"),
        "generated": _now(),
        "evidence_cutoff": DATE_STAMP,
        "population_source": ("%s::population() -- the E534 sites that only hand the value "
                              "onward or assemble a field no reader writes"
                              % os.path.basename(__file__)),
        "upstream_face": UPSTREAM_FACE,
        "upstream_study": UPSTREAM_STUDY,
        "upstream_face_sha256": upstream_sha,
        "method_limits": [
            "one hop out of E534's reader: a value that leaves again is published as "
            "still_forwarded and the third consumer is not followed",
            "a return hop enumerates corpus call sites by name and attributes them by module "
            "equality or by importing the reader's module stem; a call reached through an "
            "alias the corpus does not import is out of scope and would show as no consumer",
            "an argument hop resolves the callee by name under scripts/Tools/firm/live/monitor "
            "and binds the parameter at the passed position; a callee that is a library or a "
            "callable value is published as not_defined_in_this_corpus, not as a zero",
            "the container of an unwritten field is followed only when it is a name; a field "
            "assembled inline and dropped is published as field_dies_there",
            "dispositions use E534's reader classifier unchanged for the return hop, so the "
            "'writes a payload' test is the same one E534 applies to its own readers",
            "nothing is executed and no source is rewritten",
            "sources_read and parse_failures are a snapshot of a live tree other lanes write to; "
            "they are published but not gated, while every disposition is re-derived",
        ],
        "summary": summary,
        "verdict": _verdict(summary),
        "verdict_vocab": list(VERDICT_VOCAB),
        "hop_vocab": list(HOP_VOCAB),
        "disposition_vocab": list(S_VOCAB),
        "e534_class_vocab": list(FOLLOW_ON),
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


def face_problems(face, root=None):
    bad = []
    for key in ("study", "card", "generated", "evidence_cutoff", "population_source",
                "upstream_face", "upstream_face_sha256", "summary", "verdict", "sites",
                "method_limits", "parse_failures"):
        if key not in face:
            bad.append("the face does not publish %s" % key)
    if face.get("study") != STUDY:
        bad.append("the face is not this study")
    if not str(face.get("population_source") or "").startswith(
            "e535_next_consumer.py::population()"):
        bad.append("the population_source is not this study's population function")
    if face.get("verdict") not in VERDICT_VOCAB:
        bad.append("the verdict %r is not in the vocabulary" % face.get("verdict"))
    summary = face.get("summary") or {}
    rows = face.get("sites") or []
    if face.get("verdict") != _verdict(summary):
        bad.append("the published verdict does not re-derive from the summary")
    if summary.get("sites_in_population") != len(rows):
        bad.append("the published site count does not match the rows")
    if summary.get("parse_failures") != len(face.get("parse_failures") or []):
        bad.append("the parse-failure count does not match the published list")
    by_disposition = _count(rows, "disposition", S_VOCAB)
    if by_disposition != (summary.get("sites_by_disposition") or {}):
        bad.append("the per-site disposition counts do not re-derive")
    if sum(by_disposition.values()) != len(rows):
        bad.append("the disposition counts do not add up to the published rows")
    by_hop = _count(rows, "hop", HOP_VOCAB)
    if by_hop != (summary.get("sites_by_hop") or {}):
        bad.append("the per-site hop counts do not re-derive")
    published = sum(by_disposition[k] for k in PUBLISHED_CLASSES)
    if summary.get("sites_published_two_hops_out") != published:
        bad.append("the published-headline count of two-hop publications does not re-derive")
    assembled = by_disposition[S_FIELD_UNWRITTEN] + by_disposition[S_BODY_UNWRITTEN]
    if summary.get("sites_whose_second_consumer_assembles_without_writing") != assembled:
        bad.append("the assembled-but-unwritten count does not re-derive")
    followed = sum(len(r.get("consumer_sites") or []) for r in rows)
    if summary.get("consumer_sites_followed") != followed:
        bad.append("the followed-consumer-site count does not re-derive")
    for row in rows:
        if row.get("disposition") not in S_VOCAB:
            bad.append("a row publishes a disposition outside the vocabulary: %r"
                       % row.get("disposition"))
        if row.get("hop") not in HOP_VOCAB:
            bad.append("a row publishes a hop outside the vocabulary: %r" % row.get("hop"))
        if row.get("disposition") == S_SEPARATED_IN_THE_READER and not (row.get("guard") or {}):
            bad.append("a guarded disposition is published without the guard it sits behind")
        if row.get("hop") == H_RETURN and row.get("disposition") not in (
                S_NO_CONSUMER, S_UNRESOLVED, S_SEPARATED_IN_THE_READER) \
                and not row.get("consumer_sites"):
            bad.append("a return hop publishes a disposition with no consumer site behind it")
        if row.get("disposition") in PUBLISHED_CLASSES \
                and not row.get("next_consumer_writes_a_payload"):
            bad.append("a publication is claimed by a consumer that writes no payload")
    return bad


def check(root=None, face=None):
    face = face or load_face(root)
    problems = face_problems(face, root)
    return problems


def verify(root=None):
    """Re-derive from the tree and compare against the published face."""
    face = load_face(root)
    fresh = build(root or ROOT, write=False)
    problems = face_problems(fresh, root)
    if fresh.get("verdict") != face.get("verdict"):
        problems.append("the stored verdict %r does not re-derive (%r)"
                        % (face.get("verdict"), fresh.get("verdict")))
    for key in ("sites_in_population", "sites_by_disposition", "sites_by_hop",
                "sites_published_two_hops_out",
                "sites_whose_second_consumer_assembles_without_writing",
                "consumer_sites_followed"):
        if (face.get("summary") or {}).get(key) != (fresh.get("summary") or {}).get(key):
            problems.append("the stored summary field %r does not re-derive" % key)
    stored = {(r.get("module"), r.get("reader_function"), r.get("site_line")):
              (r.get("hop"), r.get("disposition")) for r in face.get("sites") or []}
    derived = {(r.get("module"), r.get("reader_function"), r.get("site_line")):
               (r.get("hop"), r.get("disposition")) for r in fresh.get("sites") or []}
    for key in sorted(set(stored) | set(derived)):
        if stored.get(key) != derived.get(key):
            problems.append("site %r is stored as %r but re-derives as %r"
                            % (key, stored.get(key), derived.get(key)))
    return problems


# ------------------------------------------------------------------ selftest
FIXTURE_A = '''\
"""fixture: a depth cap that returns None, a reader that returns the value, and a callee."""


def _resolve(node, depth=0):
    if depth > 6:
        return None
    return _resolve(node, depth + 1)


def _why(node):
    return _resolve(node, 0)


def _eval(node):
    return emit(_resolve(node, 0))


def emit(value):
    import json
    face = {"text": value}
    with open("out.json", "w") as fh:
        json.dump(face, fh)
    return face
'''

FIXTURE_B = '''\
"""fixture: a caller of the reader that also writes a payload."""
import json

import a_mod


def report(node):
    got = a_mod._why(node)
    face = {"verdict": got}
    with open("rep.json", "w") as fh:
        json.dump(face, fh)
    return face
'''

FIXTURE_C = '''\
"""fixture: a caller that destructures the reader's return before writing it out."""
import json

import a_mod


def unpack(node):
    got, extra = a_mod._why(node)
    face = {"text": got}
    with open("un.json", "w") as fh:
        json.dump(face, fh)
    return face
'''

FIXTURE_FACE = {
    "study": e534.STUDY,
    "card": e534.CARD,
    "arms": [{
        "module": "scripts/a_mod.py",
        "function": "_resolve",
        "counter": "depth",
        "sentinel": "None",
        "distinguish": e529.D_NO_TEST,
        "chain": e534.C_FORWARDED,
        "sites": [
            {"module": "scripts/a_mod.py", "line": 11, "callee": "_resolve",
             "caller": "_why", "chain": e534.C_FORWARDED,
             "terminal_classes": [e534.C_FORWARDED], "payload_keys": []},
            {"module": "scripts/a_mod.py", "line": 15, "callee": "_resolve",
             "caller": "_eval", "chain": e534.C_FORWARDED,
             "terminal_classes": [e534.C_FORWARDED], "payload_keys": []},
        ],
    }],
}


def _fixture_root():
    root = tempfile.mkdtemp(prefix="e535_fixture_")
    os.makedirs(os.path.join(root, "scripts"))
    os.makedirs(os.path.join(root, "results", "state_tilt"))
    for name, text in (("a_mod.py", FIXTURE_A), ("b_mod.py", FIXTURE_B),
                       ("c_mod.py", FIXTURE_C)):
        with io.open(os.path.join(root, "scripts", name), "w", encoding="utf-8",
                     newline="\n") as fh:
            fh.write(text)
    with io.open(os.path.join(root, UPSTREAM_FACE), "w", encoding="utf-8",
                 newline="\n") as fh:
        fh.write(json.dumps(FIXTURE_FACE, indent=1))
    return root


def selftest():
    problems = []
    root = _fixture_root()
    try:
        face = build(root, write=True)
        summary = face["summary"]
        if summary["sites_in_population"] != 2:
            problems.append("fixture: expected 2 sites, got %r"
                            % summary["sites_in_population"])
        hops = summary["sites_by_hop"]
        if hops.get(H_RETURN) != 1:
            problems.append("fixture: the return hop was not named (%r)" % hops)
        if hops.get(H_ARGUMENT) != 1:
            problems.append("fixture: the argument hop was not named (%r)" % hops)
        if summary["sites_published_two_hops_out"] != 2:
            problems.append("fixture: expected both hops published, got %r"
                            % summary["sites_published_two_hops_out"])
        if face["verdict"] != V_PUBLISHED_TWO_HOPS_OUT:
            problems.append("fixture: verdict %r is not the published class" % face["verdict"])
        # the return hop lands on report(), which writes a payload: not on b_mod itself
        row0 = [r for r in face["sites"] if r["hop"] == H_RETURN][0]
        callers = [s["caller"] for s in row0["consumer_sites"]]
        if callers != ["report", "unpack"]:
            problems.append("fixture: the return hop's consumers are not report()+unpack() (%r)"
                            % callers)
        # unpack() destructures the return: E534's classifier reads that shape as "stops inside"
        unpack_row = [s for s in row0["consumer_sites"] if s["caller"] == "unpack"]
        if unpack_row and unpack_row[0]["disposition"] != S_PAYLOAD_FIELD:
            problems.append("fixture: a destructured return was not followed to its writer (%r)"
                            % (unpack_row[0]["disposition"],))
        if not row0["next_consumer_writes_a_payload"]:
            problems.append("fixture: report() writes a payload but the row denies it")
        # the argument hop binds emit()'s parameter and sees the dump
        row1 = [r for r in face["sites"] if r["hop"] == H_ARGUMENT][0]
        if (row1.get("hop_detail") or {}).get("callee") != "emit":
            problems.append("fixture: the argument hop did not name emit()")
        if row1["disposition"] != S_PAYLOAD_FIELD:
            problems.append("fixture: emit() puts the value in a dumped field but the row says %r"
                            % row1["disposition"])
        if check(root=root):
            problems.append("fixture: the freshly written face does not pass its own gate")
        if verify(root=root):
            problems.append("fixture: the freshly written face does not re-derive")
        # doctored faces must all be refused
        doctored = []
        bad = copy.deepcopy(face)
        bad["verdict"] = V_DIES_IN_A_SECOND_READER
        doctored.append(("verdict flipped", bad))
        bad = copy.deepcopy(face)
        bad["sites"][0]["disposition"] = S_NO_CONSUMER
        doctored.append(("a disposition changed under its consumer list", bad))
        bad = copy.deepcopy(face)
        bad["sites"][0]["hop"] = H_UNRESOLVED
        doctored.append(("a hop kind blanked", bad))
        bad = copy.deepcopy(face)
        bad["summary"]["sites_published_two_hops_out"] = 0
        doctored.append(("the headline count lowered", bad))
        bad = copy.deepcopy(face)
        bad["summary"]["sites_by_hop"][H_ARGUMENT] = 0
        doctored.append(("a hop count zeroed", bad))
        bad = copy.deepcopy(face)
        bad["sites"][1]["next_consumer_writes_a_payload"] = False
        doctored.append(("a publication carried by a non-writing consumer", bad))
        for label, face_bad in doctored:
            if not face_problems(face_bad, root):
                problems.append("fixture: the gate accepted a doctored face (%s)" % label)
        # a truthy but empty population must still be its own verdict
        empty = build(root, write=False, rows=[], sources=2, failures=[])
        if empty["verdict"] != V_EMPTY:
            problems.append("fixture: an empty population did not publish the empty verdict")
        if face_problems(empty, root):
            problems.append("fixture: the empty face does not pass its own gate")
    finally:
        shutil.rmtree(root, ignore_errors=True)
    return problems


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "run"
    if cmd == "run":
        face = build()
        summary = face["summary"]
        print("verdict:", face["verdict"])
        print("sites:", summary["sites_in_population"],
              "| published:", summary["sites_published_two_hops_out"],
              "| assembled-unwritten:",
              summary["sites_whose_second_consumer_assembles_without_writing"],
              "| dies:", summary["sites_that_die_in_a_second_reader"],
              "| forwarded:", summary["sites_still_forwarded"],
              "| unresolved:", summary["sites_unresolved"])
        print("sources:", summary["sources_read"], "| parse failures:",
              summary["parse_failures"])
        return 0
    if cmd == "check":
        problems = check()
        for problem in problems:
            print("PROBLEM:", problem)
        print("check problems=%d" % len(problems))
        return 0 if not problems else 2
    if cmd == "verify":
        problems = verify()
        for problem in problems:
            print("PROBLEM:", problem)
        print("verify problems=%d" % len(problems))
        return 0 if not problems else 2
    if cmd == "selftest":
        problems = selftest()
        for problem in problems:
            print("PROBLEM:", problem)
        print("selftest problems=%d" % len(problems))
        return 0 if not problems else 2
    print("usage: e535_next_consumer.py [run|check|verify|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main())