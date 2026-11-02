"""E377 -- how large is the blind spot "a writer the census cannot name".

E371 measured two ``store_needed`` members and found their whole bill was one parsed source: both
write their faces through paths they format at run time, so a census that keys literal/constant
paths records them as writing nothing.  That is one instance of a tree-wide question, and this
study asks the tree-wide version:

  (1) CENSUS -- every ``json.dump`` call in the corpus, classified by whether its destination
      resolves to a nameable path (a string literal, a name bound to one, or an ``os.path.join``
      of constants) or is supplied at run time (an f-string / ``%`` / ``.format``, a function
      argument, a helper's return value).  One row per writer, so the count can be audited;
  (2) REACH -- which published faces those unnameable writers plausibly write.  A writer's
      evidence is the face-shaped string literals in its own text MINUS every face any resolved
      sink in the corpus already keys: a face that survives both tests is a face no census has
      ever keyed;
  (3) EXPLANATION -- is any of those faces one E350 publishes as an unwritten guard?  That is the
      answer the card asks for: "no writer" splits into "no named writer" and "a writer the
      instrument cannot name", and only the second is recoverable.

Nothing here rewrites E350/E353/E368/E371 faces; the E350 face is read, never rebuilt.

Usage:
  python scripts/e377_unresolved_destination.py run       # build the face
  python scripts/e377_unresolved_destination.py verify    # re-derive the checks that need no scan
  python scripts/e377_unresolved_destination.py selftest  # offline fixture legs
"""
from __future__ import annotations

import ast
import io
import json
import os
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e347_published_number_gate_census as e347  # noqa: E402
import e350_field_branch_census as e350  # noqa: E402

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-03"
FACE = "UNRESOLVEDDEST-%s.json" % TODAY
LATEST = "unresolveddest_latest.json"
STUDY = "E377_unresolved_destination"
SELF_REL = "scripts/e377_unresolved_destination.py"
MAX_WRITER_ROWS = 400
MAX_FACE_ROWS = 200

# Why a destination could not be named.  The labels matter: "formatted" is a path the writer
# builds and a census COULD follow with more work, while "argument_supplied" is a path only the
# caller knows, so a reader must not treat the two as one bucket.
WHY_LITERAL = "literal"
WHY_BOUND = "bound_constant"
WHY_JOINED = "joined_constants"
WHY_FORMATTED = "formatted"
WHY_JOINED_COMPUTED = "joined_computed"
WHY_ARGUMENT = "argument_supplied"
WHY_ATTRIBUTE = "attribute_supplied"
WHY_HELPER = "returned_from_helper"
WHY_LOCAL = "local_expression"
WHY_OTHER = "other"

RESOLVED = (WHY_LITERAL, WHY_BOUND, WHY_JOINED)

V_ALL_NAMED = ("every_json_dump_destination_in_the_corpus_resolves_to_a_nameable_path_so_a_"
               "missing_writer_is_a_writer_that_does_not_exist_and_not_one_the_instrument_cannot_see")
V_BLIND_SPOT = ("an_unnameable_destination_set_exists_and_it_reaches_published_faces_that_no_"
                "resolved_sink_in_the_corpus_keys_so_no_writer_splits_into_no_named_writer_and_a_"
                "writer_the_instrument_cannot_name")
V_REACHES_NOTHING = ("the_unnameable_destination_set_exists_but_every_face_its_writers_name_is_"
                     "already_keyed_by_a_resolved_sink_elsewhere_so_the_blind_spot_costs_no_number")
V_EMPTY = "no_json_dump_call_was_found_in_the_corpus_so_no_claim_is_made"


def say(message):
    print(message, flush=True)


# ------------------------------------------------------------------ classification

def _consts(tree):
    """Name -> string constant, for module-level and first-assignment bindings."""
    out = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target, value = node.targets[0], node.value
            if isinstance(target, ast.Name) and isinstance(value, ast.Constant) \
                    and isinstance(value.value, str):
                out.setdefault(target.id, value.value)
    return out


def _value(expr, consts):
    """The string an expression denotes statically, or ``None``."""
    if isinstance(expr, ast.Constant) and isinstance(expr.value, str):
        return expr.value
    if isinstance(expr, ast.Name):
        return consts.get(expr.id)
    if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Attribute) \
            and expr.func.attr == "join":
        parts = [_value(a, consts) for a in expr.args]
        if parts and all(p is not None for p in parts):
            return os.path.join(*parts)
    if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Attribute) \
            and expr.func.attr in ("format", "absolute", "abspath", "normpath") \
            and expr.args is not None:
        if expr.func.attr in ("absolute", "abspath", "normpath") and expr.args:
            inner = _value(expr.args[0], consts)
            if inner is None:
                return None
            return inner if expr.func.attr != "abspath" else os.path.join(ROOT, inner)
        return None
    return None


def _unwrap_open(expr):
    """``json.dump(x, open(p, "w"))`` -- the destination is ``open``'s first argument."""
    if isinstance(expr, ast.Call) and expr.args:
        func = expr.func
        name = func.id if isinstance(func, ast.Name) else (
            func.attr if isinstance(func, ast.Attribute) else "")
        if name in ("open", "open_text", "fdopen"):
            return expr.args[0]
    return expr


def _open_path(expr):
    """The path argument when ``expr`` is a call that opens a file, else ``None``."""
    if isinstance(expr, ast.Call) and expr.args:
        func = expr.func
        name = func.id if isinstance(func, ast.Name) else (
            func.attr if isinstance(func, ast.Attribute) else "")
        if name in ("open", "open_text", "fdopen", "NamedTemporaryFile"):
            return expr.args[0]
    return None


def _handle_paths(tree):
    """file-object name -> its path expression (``with open(P) as fh:`` / ``fh = open(P)``).

    Without this the census reads ``json.dump(obj, fh)`` as a destination supplied by the caller,
    which is true of the HANDLE and false of the path: the path sits three tokens away in the same
    function.  Almost every writer in this corpus takes the handle form, so leaving it out turns the
    instrument into a machine for reporting that nothing can be named.
    """
    out = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.With):
            for item in node.items:
                target = item.optional_vars
                if isinstance(target, ast.Name):
                    inner = _open_path(item.context_expr)
                    if inner is not None:
                        out.setdefault(target.id, inner)
        elif isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name):
            inner = _open_path(node.value)
            if inner is not None:
                out.setdefault(node.targets[0].id, node.value)
    return out


def _formatted(expr):
    return (isinstance(expr, ast.JoinedStr)
            or (isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.Mod))
            or (isinstance(expr, ast.Call) and isinstance(expr.func, ast.Attribute)
                and expr.func.attr == "format"))


def _bound_names(tree):
    """Name -> the expression it is assigned anywhere in the source.

    A name bound to something non-constant is still NOT "provided by the caller": the two are
    different reasons a path cannot be named, and one of them is fixable by reading further.
    """
    out = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Name):
                    out.setdefault(target.id, node.value)
    return out


def classify(expr, consts, bound=None):
    """``(why, target)`` for one destination expression."""
    if _formatted(expr):
        return WHY_FORMATTED, "<formatted>"
    bound = bound or {}
    if isinstance(expr, ast.Name) and expr.id not in consts and expr.id in bound:
        # One hop only: a local alias of a formatted path is a formatted path, not a caller's.
        inner = bound[expr.id]
        if _formatted(inner):
            return WHY_FORMATTED, "<formatted>"
        return WHY_LOCAL, "<bound to a local expression>"
    resolved = _value(expr, consts)
    if resolved is not None:
        if isinstance(expr, ast.Constant):
            return WHY_LITERAL, resolved
        if isinstance(expr, ast.Name):
            return WHY_BOUND, resolved
        return WHY_JOINED, resolved
    if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Attribute) \
            and expr.func.attr == "join":
        return WHY_JOINED_COMPUTED, "<computed>"
    if isinstance(expr, ast.Name):
        return WHY_ARGUMENT, "<provided by caller>"
    if isinstance(expr, ast.Attribute):
        return WHY_ATTRIBUTE, "<attribute>"
    if isinstance(expr, ast.Call):
        return WHY_HELPER, "<returned>"
    return WHY_OTHER, "<other>"


def _parents(tree):
    parent = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parent[child] = node
    return parent


def _enclosing(parent, node):
    cur = parent.get(node)
    while cur is not None:
        if isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return cur.name
        cur = parent.get(cur)
    return "<module>"


def dump_destinations(text):
    """``[{line, func, why, target, resolved}]`` for every ``json.dump`` in one source."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return None
    consts = e347.constants(tree)
    bound = _bound_names(tree)
    handles = _handle_paths(tree)
    parent = _parents(tree)
    out = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "dump"):
            continue
        func = node.func.value
        if not (isinstance(func, ast.Name) and func.id in ("json", "ujson", "simplejson")):
            continue
        if len(node.args) < 2:
            continue
        dest = _unwrap_open(node.args[1])
        # The handle form is the common one: follow one alias hop to the path it was opened from.
        if isinstance(dest, ast.Name) and dest.id in handles:
            dest = handles[dest.id]
        why, target = classify(dest, consts, bound)
        out.append({"line": node.lineno, "func": _enclosing(parent, node),
                    "why": why, "target": target, "resolved": why in RESOLVED})
    return out


def face_literals(text):
    """Face-shaped string literals in the source (``.json`` / ``.jsonl`` paths).

    A template that still carries a placeholder (``results/_r%s.json``) is NOT a face name -- it is
    the unnameable half of the census, and counting it here would credit an unnameable writer with a
    face no reader can key.
    """
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return set()
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            value = node.value
            if "%s" in value or "%d" in value or "{" in value:
                continue
            if value.endswith((".json", ".jsonl")) and ("/" in value or "\\" in value):
                out.add(value.replace("\\", "/"))
    return out


def _literals_by_func(text):
    """function name -> face-shaped literals inside it (``<module>`` handled by the caller)."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return {}
    out = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            vals = set()
            for sub in ast.walk(node):
                if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                    value = sub.value
                    if "%s" in value or "%d" in value or "{" in value:
                        continue
                    if value.endswith((".json", ".jsonl")) and ("/" in value or "\\" in value):
                        vals.add(e350._face_key(value))
            out[node.name] = vals
    return out


def _is_published(path):
    rel = path.lstrip("./")
    return os.path.exists(os.path.join(ROOT, rel))


# ------------------------------------------------------------------ census

def census(sources):
    """One pass over the corpus: per-writer rows + the resolved-sink face set."""
    rows = []
    keyed = set()
    parsed = 0
    for rel, text in sources:
        calls = dump_destinations(text)
        if calls is None:
            continue
        parsed += 1
        try:
            tree = ast.parse(text)
            consts = e347.constants(tree)
            sinks = e350._dump_sinks(tree, consts)
            bindings, _bindings_unresolved = e350._face_bindings(tree, consts)
        except SyntaxError:
            sinks, bindings = {}, {}
        # A face is "keyed" if ANY resolved site names it -- a read or a write.  Restricting the
        # denominator to sinks would count every face the corpus only READS as unkeyed, which is
        # the same over-statement the census exists to avoid.
        for faces in list(sinks.values()) + list(bindings.values()):
            keyed |= set(faces)
        unresolved = [c for c in calls if not c["resolved"]]
        if not unresolved:
            continue
        # REACH is scoped to the function that carries the unnameable dump: a face literal
        # elsewhere in the same module is a different writer's path, and crediting it here would
        # manufacture reach the evidence does not carry.
        by_func = _literals_by_func(text)
        loose = {e350._face_key(f) for f in face_literals(text)}
        named = set()
        for call in unresolved:
            named |= loose if call["func"] == "<module>" else by_func.get(call["func"], set())
        named = sorted(f for f in named if _is_published(f))
        rows.append({"source": rel, "dump_calls": len(calls),
                     "resolved": len(calls) - len(unresolved),
                     "unresolved": len(unresolved),
                     "why": sorted({c["why"] for c in unresolved}),
                     "unnameable_faces": named,
                     "evidence": ["%s:%d %s %s" % (rel, c["line"], c["func"], c["why"])
                                  for c in unresolved][:6]})
    return {"rows": rows, "keyed": keyed, "parsed": parsed}


def decide(summary):
    if not summary.get("dump_calls"):
        return V_EMPTY
    if not summary.get("unresolved_calls"):
        return V_ALL_NAMED
    if summary.get("faces_no_census_keys"):
        return V_BLIND_SPOT
    return V_REACHES_NOTHING


def build(write_face=True):
    sources = [(rel, text) for rel, text in e350._sources() if rel != SELF_REL]
    say("corpus: %d sources" % len(sources))
    result = census(sources)
    rows, keyed = result["rows"], result["keyed"]
    say("writers with an unnameable destination: %d (parsed %d)" % (len(rows), result["parsed"]))

    total = sum(r["dump_calls"] for r in rows)
    unresolved = sum(r["unresolved"] for r in rows)
    # Every console, not only the unresolved writers, so the denominator is not the autoresponder.
    all_calls = 0
    for rel, text in sources:
        calls = dump_destinations(text) if rel not in {r["source"] for r in rows} else None
        if calls is not None:
            all_calls += len(calls)
    all_calls += total

    unnamed = sorted({f for r in rows for f in r["unnameable_faces"]})
    no_census = [f for f in unnamed if f not in keyed]
    say("faces named by an unnameable writer: %d; of those no resolved sink keys: %d"
        % (len(unnamed), len(no_census)))

    e350_face = {}
    path = os.path.join(OUTDIR, "fieldbranch_latest.json")
    if os.path.exists(path):
        with io.open(path, encoding="utf-8") as fh:
            e350_face = json.load(fh)
    guards = e350_face.get("unwritten_guards") or []
    guard_faces = {g.get("face") for g in guards if g.get("face_resolved")}
    explained = [g for g in guards
                 if g.get("face") in set(no_census) or g.get("face") in set(unnamed)]
    say("E350 unwritten guards: %d rows, %d on a resolved face; %d named by an unnameable writer"
        % (len(guards), len(guard_faces), len(explained)))

    summary = {
        "corpus_sources": len(sources),
        "sources_parsed": result["parsed"],
        "dump_calls": all_calls,
        "unresolved_calls": unresolved,
        "writers_with_unresolved": len(rows),
        "faces_named_by_unnameable_writers": len(unnamed),
        "faces_no_census_keys": len(no_census),
        "keyed_faces_in_corpus": len(keyed),
        "e350_unwritten_guard_rows": len(guards),
        "e350_unwritten_guard_rows_named_by_an_unnameable_writer": len(explained),
        "why_histogram": _histogram(rows),
    }
    face = {
        "study": STUDY,
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "evidence_cutoff": TODAY,
        "source": SELF_REL,
        "summary": summary,
        "writers": rows[:MAX_WRITER_ROWS],
        "writers_truncated": max(0, len(rows) - MAX_WRITER_ROWS),
        "faces_no_census_keys": no_census[:MAX_FACE_ROWS],
        "faces_no_census_keys_truncated": max(0, len(no_census) - MAX_FACE_ROWS),
        "e350_unwritten_guards_explained": [
            {"face": g.get("face"), "field": g.get("field"), "guards": g.get("guards")}
            for g in explained[:MAX_FACE_ROWS]],
        "verdict": decide(summary),
        "bound": ("the reach test is a NAME test over one source's literals, so it shows a face the "
                  "writer could be writing, never that it writes it; a writer whose destination a "
                  "caller supplies names no face at all, so its reach is under-counted, not "
                  "over-counted; 'keyed' is the union of resolved sinks over the same corpus E350 "
                  "walks, so a face keyed only by another unnameable writer still counts as unkeyed; "
                  "the E350 face is read as published and not rebuilt here"),
    }
    if write_face:
        for target in (os.path.join(OUTDIR, FACE), os.path.join(OUTDIR, LATEST)):
            with open(target, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
                fh.write("\n")
        say("wrote %s" % os.path.join(OUTDIR, FACE))
    return face


def _histogram(rows):
    counts = {}
    for row in rows:
        for why in row["why"]:
            counts[why] = counts.get(why, 0) + 1
    return dict(sorted(counts.items()))


def verify():
    """Re-derive what needs no corpus scan: the internal arithmetic and the verdict."""
    path = os.path.join(OUTDIR, FACE)
    with io.open(path, encoding="utf-8") as fh:
        face = json.load(fh)
    problems = []
    summary = face.get("summary") or {}
    rows = face.get("writers") or []
    if summary.get("writers_with_unresolved") != len(rows) + (face.get("writers_truncated") or 0):
        problems.append("writer count does not equal the published rows")
    if summary.get("unresolved_calls") != sum(r["unresolved"] for r in rows):
        problems.append("unresolved call count does not re-add from the rows")
    for row in rows:
        if row["resolved"] + row["unresolved"] != row["dump_calls"]:
            problems.append("row does not add up: %s" % row["source"])
        if not row["evidence"]:
            problems.append("row carries no evidence line: %s" % row["source"])
    if len(face.get("faces_no_census_keys") or []) + (face.get("faces_no_census_keys_truncated") or 0) \
            != summary.get("faces_no_census_keys"):
        problems.append("face list does not match the published count")
    if face.get("verdict") != decide(summary):
        problems.append("verdict does not re-derive from the summary")
    say("verify: %d problem(s)" % len(problems))
    for p in problems:
        say("  - %s" % p)
    return 1 if problems else 0


# ------------------------------------------------------------------ selftest

FIXT_A = '''
import json
json.dump({}, open("results/state_tilt/DELTA-2026-11-01.json", "w"))
'''

FIXT_B = '''
import json
def write(rnd):
    out = "results/_r%sbmb_chain.json" % rnd
    json.dump({}, open(out, "w"))
'''

FIXT_C = '''
import json
def write(path):
    json.dump({}, open(path, "w"))
'''

FIXT_D = '''
import json, os
OUTDIR = "results/state_tilt"
FACE = "ALPHA.json"
json.dump({}, open(os.path.join(OUTDIR, FACE), "w"))
'''


def selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append((name, bool(ok), detail))

    a = dump_destinations(FIXT_A)[0]
    leg("a literal destination resolves and names its face",
        a["resolved"] and a["why"] == WHY_LITERAL and a["target"].endswith("DELTA-2026-11-01.json"),
        str(a))

    b = dump_destinations(FIXT_B)[0]
    leg("a local alias of a formatted path is unnameable, not caller-supplied",
        not b["resolved"] and b["why"] == WHY_FORMATTED, str(b))

    c = dump_destinations(FIXT_C)[0]
    leg("a caller-supplied destination is a different bucket from a formatted one",
        not c["resolved"] and c["why"] == WHY_ARGUMENT, str(c))

    d = dump_destinations(FIXT_D)[0]
    leg("a join of two constants is resolved", d["resolved"] and d["why"] == WHY_JOINED
        and d["target"].endswith("ALPHA.json"), str(d))

    leg("the enclosing function is published as evidence",
        b["func"] == "write" and c["func"] == "write", "%s / %s" % (b["func"], c["func"]))

    leg("a face-shaped literal is collected and a bare word is not",
        "results/_r%sbmb_chain.json" not in face_literals(FIXT_B)
        and "results/state_tilt/DELTA-2026-11-01.json" in face_literals(FIXT_A),
        str(face_literals(FIXT_A)))

    clean = {"dump_calls": 5, "unresolved_calls": 0, "faces_no_census_keys": 0}
    leg("no unnameable destination means no blind spot", decide(clean) == V_ALL_NAMED)
    leg("an unnameable set that reaches an unkeyed face is the blind spot",
        decide({"dump_calls": 5, "unresolved_calls": 2, "faces_no_census_keys": 1}) == V_BLIND_SPOT)
    leg("an unnameable set that reaches only keyed faces costs nothing",
        decide({"dump_calls": 5, "unresolved_calls": 2, "faces_no_census_keys": 0})
        == V_REACHES_NOTHING)
    leg("no dump call is no claim", decide({"dump_calls": 0}) == V_EMPTY)

    total = len(legs)
    bad = [n for n, ok, _ in legs if not ok]
    for name, ok, detail in legs:
        say("%s %s%s" % ("PASS" if ok else "FAIL", name, (" | " + detail) if not ok else ""))
    say("selftest: %d/%d" % (total - len(bad), total))
    return 1 if bad else 0


def main(argv):
    mode = (argv[1] if len(argv) > 1 else "run").lower()
    if mode == "selftest":
        return selftest()
    if mode == "verify":
        return verify()
    build(write_face=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))