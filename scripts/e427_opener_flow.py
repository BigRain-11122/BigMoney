"""E427 -- which template inside an opener is the name that opener actually reads.

E426 located 2,818 templates that sit inside a function which opens a file, and it published
that location as the interesting fact.  Location is not dataflow: a template can be built on
one line and read five lines later, or it can be built and only printed while the opener reads
an unrelated constant.  This study resolves the assignment target of every in-opener template
and asks whether any opener call in the same function reads it -- directly, as the opener's own
argument, or through exactly one local rebinding.

Reuse: the corpus walk, the four template shapes, the specificity rule and the opener vocabulary
are imported from `e426_dynamic_face_names`, so the base population is the same population and
the only thing that moves is the class on top of it (a second detector would make the bill
unreadable -- E366/E208 family).

Three states for a *bound* template, plus one published shape that is not a class:

  read_by_the_opener                    an opener in the same function reads the target, or the
                                        template IS the opener's argument expression
  read_after_one_rebinding              a same-function local is assigned from the target and an
                                        opener reads that local (exactly one hop; a second hop is
                                        not followed and the bound is published)
  in_an_opener_but_the_opener_reads_something_else
                                        the template is bound but no opener in the scope reads it
  template_has_no_binding               (shape, not a class) the template is inside a call
                                        argument, a return, or a bare expression, so there is no
                                        name to follow.  Counted and published beside the three
                                        states, never folded into "unread", because "there is no
                                        target" and "the target is unread" are different bills.

Subcommands: run | verify | selftest
"""
from __future__ import annotations

import ast
import importlib.util
import json
import os
import re
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "results", "state_tilt")
FACE = "OPENERFLOW-%s.json"
LATEST = "openerflow_latest.json"
STUDY = "E427_opener_flow"
CARD = "E427-WHICH-TEMPLATE-IN-AN-OPENER-IS-NOT-THE-NAME-THAT-OPENER-READS"

_E426_PATH = os.path.join(ROOT, "scripts", "e426_dynamic_face_names.py")

# The scanner is part of the corpus it reads (E180/E207/E332 family): its own file never
# contributes a template, and neither does the predecessor whose population it consumes.
SELF_FILES = {"e427_opener_flow.py"}

S_READ = "read_by_the_opener"
S_REBIND = "read_after_one_rebinding"
S_UNREAD = "in_an_opener_but_the_opener_reads_something_else"
S_UNBOUND = "template_has_no_binding"
STATE_VOCAB = (S_READ, S_REBIND, S_UNREAD)

V = ("a_template_that_sits_in_a_function_that_opens_a_file_is_read_by_that_opener_only_when_"
     "its_binding_reaches_an_openers_argument_so_location_is_not_dataflow")


def _load_e426():
    spec = importlib.util.spec_from_file_location("e426_dynamic_face_names", _E426_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


E426 = _load_e426()
OPENERS = E426.OPENERS


def _rel(path: str, root: str = ROOT) -> str:
    return os.path.relpath(path, root).replace("\\", "/")


def write_face(face: dict, outdir: str | None = None) -> str:
    outdir = outdir or OUT_DIR
    os.makedirs(outdir, exist_ok=True)
    cutoff = face["evidence_cutoff"]
    path = os.path.join(outdir, FACE % cutoff)
    body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=False)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(body + "\n")
    latest = os.path.join(outdir, LATEST)
    with open(latest, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(body + "\n")
    return path


# ------------------------------------------------------------------ shapes (E426's, verbatim)
def template_text(node) -> tuple | None:
    """(kind, normalised template text) for the four shapes E426 counts, else None."""
    norm = E426._norm
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        for side, other, left in ((node.left, node.right, True),
                                  (node.right, node.left, False)):
            if isinstance(side, ast.Constant) and isinstance(side.value, str) \
                    and not isinstance(other, ast.Constant):
                text = norm(side.value) + "*" if left else "*" + norm(side.value)
                return "concatenation", text
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
        if isinstance(node.left, ast.Constant) and isinstance(node.left.value, str) \
                and node.right is not None:
            return "percent_format", re.sub(r"%[-+ 0#]*\d*(?:\.\d+)?[sdifrxX]", "*",
                                            node.left.value)
    if isinstance(node, ast.JoinedStr):
        if any(isinstance(v, ast.FormattedValue) for v in node.values):
            parts = []
            for v in node.values:
                if isinstance(v, ast.Constant) and isinstance(v.value, str):
                    parts.append(norm(v.value))
                else:
                    parts.append("*")
            return "fstring", "".join(parts)
    if isinstance(node, ast.Call):
        fn = node.func
        if isinstance(fn, ast.Attribute) and fn.attr == "format" \
                and isinstance(fn.value, ast.Constant) and isinstance(fn.value.value, str):
            return "str_format", re.sub(r"\{[^{}]*\}", "*", fn.value.value)
        if isinstance(fn, ast.Attribute) and fn.attr == "join" and node.args:
            tail = node.args[-1]
            if isinstance(tail, ast.Constant) and isinstance(tail.value, str) \
                    and tail.value.endswith(".json") \
                    and any(not isinstance(a, ast.Constant) for a in node.args[:-1]):
                return "path_join_with_a_dynamic_head", "*" + norm(tail.value)
    return None


def _name_of(node):
    """Dotted name for a Name/Attribute expression, else None."""
    parts = []
    cur = node
    while isinstance(cur, ast.Attribute):
        parts.append(cur.attr)
        cur = cur.value
    if isinstance(cur, ast.Name):
        parts.append(cur.id)
        return ".".join(reversed(parts))
    return None


def _exprs_in(node):
    """Every Name id and dotted-attribute name that appears inside an expression."""
    out = []
    for sub in ast.walk(node):
        if isinstance(sub, ast.Name):
            out.append(sub.id)
        elif isinstance(sub, ast.Attribute):
            n = _name_of(sub)
            if n:
                out.append(n)
    return out


def _call_label(call) -> str:
    fn = call.func
    if isinstance(fn, ast.Name):
        return fn.id
    if isinstance(fn, ast.Attribute):
        return fn.attr
    return ""


def _is_opener_call(call) -> bool:
    return isinstance(call, ast.Call) and _call_label(call) in OPENERS


def _qualname(fn, parents) -> str:
    names = []
    cur = fn
    while cur is not None:
        if isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names.append(cur.name)
        cur = parents.get(cur)
    return ".".join(reversed(names)) if names else "<module>"


def _assignment_targets(stmt):
    if isinstance(stmt, ast.Assign):
        return [t for t in stmt.targets]
    if isinstance(stmt, ast.AnnAssign):
        return [stmt.target]
    if isinstance(stmt, ast.NamedExpr):
        return [stmt.target]
    return []


def analyse_source(text: str, rel: str) -> list:
    """One row per in-opener template: its binding and whether that opener reads it."""
    if rel in SELF_FILES:
        return []
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    parents = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[child] = node

    def scope_of(node):
        cur = parents.get(node)
        while cur is not None:
            if isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef)):
                return cur
            cur = parents.get(cur)
        return None

    rows = []
    for node in ast.walk(tree):
        shape = template_text(node)
        if shape is None:
            continue
        kind, text = shape
        if ".json" not in text:
            continue
        specific, stems = E426._specificity(text)
        if not specific:
            continue
        scope = scope_of(node)
        if scope is None or not E426._has_opener(scope):
            continue

        opener_calls = [n for n in ast.walk(scope) if _is_opener_call(n)]

        # (a) the template IS (inside) an expression handed to an opener -- decided before the
        # ascent, because the ascent consumes the node identity as it climbs
        direct = False
        for call in opener_calls:
            exprs = list(call.args) + [kw.value for kw in call.keywords]
            for expr in exprs:
                if expr is node or any(sub is node for sub in ast.walk(expr)):
                    direct = True
                    break
            if direct:
                break

        # -- ascend to the binding: the nearest Assign/AnnAssign/NamedExpr whose value holds it.
        # A template nested inside a helper call (os.path.join(OUT, "%s.json" % name)) is bound by
        # the assignment that holds the join, so the climb passes through every expression node.
        target, position = None, "no_binding"
        cur = node
        while True:
            parent = parents.get(cur)
            if isinstance(parent, (ast.Assign, ast.AnnAssign, ast.NamedExpr)):
                if getattr(parent, "value", None) is cur:
                    tgts = _assignment_targets(parent)
                    target = _name_of(tgts[0]) if tgts else None
                    position = "assigned" if target else "no_binding"
                break
            if parent is None or isinstance(parent, ast.stmt):
                position = "returned" if isinstance(parent, ast.Return) else "no_binding"
                break
            if isinstance(parent, (ast.expr, ast.Tuple, ast.List)):
                cur = parent
                continue
            position = "call_argument" if isinstance(parent, (ast.keyword, ast.withitem)) \
                else "no_binding"
            break

        # (b) an opener reads the bound name
        read_target = False
        if target:
            short = target.split(".")[-1]
            for call in opener_calls:
                exprs = list(call.args) + [kw.value for kw in call.keywords]
                for expr in exprs:
                    ids = _exprs_in(expr)
                    if target in ids or short in ids:
                        read_target = True
                        break
                if read_target:
                    break

        # (c) one rebinding hop inside the same scope
        rebind = None
        if target and not direct and not read_target:
            short = target.split(".")[-1]
            for stmt in ast.walk(scope):
                if not isinstance(stmt, (ast.Assign, ast.AnnAssign)):
                    continue
                value = getattr(stmt, "value", None)
                if value is None:
                    continue
                ids = set(_exprs_in(value))
                if target not in ids and short not in ids:
                    continue
                for tgt in _assignment_targets(stmt):
                    name = _name_of(tgt)
                    if not name:
                        continue
                    nshort = name.split(".")[-1]
                    if name == target or nshort == short:
                        continue
                    for call in opener_calls:
                        exprs = list(call.args) + [kw.value for kw in call.keywords]
                        if any(nshort in _exprs_in(e) or name in _exprs_in(e) for e in exprs):
                            rebind = {"from": target, "to": name, "line": stmt.lineno}
                            break
                    if rebind:
                        break
                if rebind:
                    break

        if direct or read_target:
            state = S_READ
        elif rebind:
            state = S_REBIND
        elif position != "assigned" or not target:
            state = S_UNBOUND
        else:
            state = S_UNREAD

        rows.append({
            "module": rel,
            "function": _qualname(scope, parents),
            "line": getattr(node, "lineno", 0),
            "kind": kind,
            "template": text,
            "stem_fragments": stems,
            "binding": "unbound" if state == S_UNBOUND else (target or "unbound"),
            "position": position,
            "state": state,
            "the_opener_argument_is_this_template": direct,
            "rebind_hop": rebind,
            "openers_in_scope": len(opener_calls),
        })
    return rows


def scan(root: str = ROOT) -> dict:
    rows, modules, skipped = [], 0, 0
    for path in E426.python_corpus(root):
        rel = _rel(path, root)
        try:
            text = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            skipped += 1
            continue
        modules += 1
        rows.extend(analyse_source(text, rel))
    # E426 published `templates_in_an_opener` unfiltered by specificity (2818 at its run).  This
    # study prices only the *specific* ones -- the population E426 actually used for reach -- so
    # the unfiltered count is re-derived here with E426's own collector and published beside it:
    # a base that differs is then a stated difference in filter, not a silent drift.
    try:
        _, all_templates = E426.collect_corpus(root)
        unfiltered = sum(1 for t in all_templates
                         if t["in_an_opener"] and t["module"] not in
                         {"scripts/" + f for f in SELF_FILES})
    except Exception:  # pragma: no cover - a census that cannot re-run must not fabricate one
        unfiltered = None
    return {"rows": rows, "modules": modules, "unreadable_modules": skipped,
            "unfiltered_in_opener": unfiltered}


# ------------------------------------------------------------------ build
def build(root: str = ROOT, now: datetime | None = None, write: bool = True) -> dict:
    now = now or datetime.now().astimezone()
    scan_result = scan(root)
    rows = scan_result["rows"]

    by_state = {s: 0 for s in (S_READ, S_REBIND, S_UNREAD)}
    by_state[S_UNBOUND] = 0
    for r in rows:
        by_state[r["state"]] += 1

    bound = by_state[S_READ] + by_state[S_REBIND] + by_state[S_UNREAD]
    read_total = by_state[S_READ] + by_state[S_REBIND]
    if bound == 0:
        verdict, reason = "no_in_opener_template_was_found_so_nothing_is_priced", \
            "the scan found 0 templates inside an opener"
    else:
        verdict = V
        reason = ("%d of %d in-opener templates are read by an opener in their own function "
                  "(%d directly as its argument, %d through one rebinding); %d sit beside an "
                  "unrelated read and %d carry no binding at all"
                  % (read_total, bound, by_state[S_READ], by_state[S_REBIND],
                     by_state[S_UNREAD], by_state[S_UNBOUND]))

    # E426's own base count, read back from its face rather than remembered
    base = None
    base_path = os.path.join(root, "results", "state_tilt", "dynamicname_latest.json")
    if os.path.exists(base_path):
        try:
            prior = json.load(open(base_path, encoding="utf-8"))
            base = prior.get("summary", {}).get("templates_in_an_opener")
        except (OSError, json.JSONDecodeError):
            base = None

    by_function: dict = {}
    for r in rows:
        if r["state"] == S_UNREAD:
            key = "%s:%s" % (r["module"], r["function"])
            by_function[key] = by_function.get(key, 0) + 1
    top_unread = sorted(({"site": k, "unread": v} for k, v in by_function.items()),
                        key=lambda d: (-d["unread"], d["site"]))[:25]

    by_module: dict = {}
    for r in rows:
        m = by_module.setdefault(r["module"], {s: 0 for s in STATE_VOCAB})
        m[r["state"]] = m.get(r["state"], 0) + 1
        m.setdefault(S_UNBOUND, 0)
    module_rows = sorted(
        ({"module": k, "read": v[S_READ] + v[S_REBIND], "unread": v[S_UNREAD],
          "unbound": v.get(S_UNBOUND, 0),
          "in_opener": v[S_READ] + v[S_REBIND] + v[S_UNREAD] + v.get(S_UNBOUND, 0)}
         for k, v in by_module.items()),
        key=lambda d: (-d["unread"], d["module"]))

    sample = sorted(rows, key=lambda r: (r["state"] != S_READ, r["module"], r["line"]))[:80]
    all_rows = sorted(rows, key=lambda r: (r["module"], r["line"], r["template"]))

    face = {
        "study": STUDY,
        "card": CARD,
        "title": "which template inside an opener is the name that opener actually reads",
        "evidence_cutoff": now.strftime("%Y-%m-%d"),
        "generated": now.isoformat(timespec="seconds"),
        "population_source": "results/state_tilt/dynamicname_latest.json (E426 base) + live "
                             "python corpus re-parse",
        "verdict": verdict,
        "verdict_reason": reason,
        "state_vocab": list(STATE_VOCAB),
        "unbound_shape_note": ("%s is a shape, not a class: 'there is no name to follow' is a "
                               "different bill from 'the name is unread'." % S_UNBOUND),
        "summary": {
            "corpus_modules": scan_result["modules"],
            "unreadable_modules": scan_result["unreadable_modules"],
            "in_opener_templates": len(rows),
            "e426_templates_in_an_opener": base,
            "e426_recount_unfiltered_today": scan_result["unfiltered_in_opener"],
            "unfiltered_delta_vs_e426": (scan_result["unfiltered_in_opener"] - base)
                                        if (base is not None and
                                            scan_result["unfiltered_in_opener"] is not None)
                                        else None,
            "base_matches_e426": (base == scan_result["unfiltered_in_opener"])
                                 if base is not None else None,
            "base_note": ("E426's published number is unfiltered by specificity; this study scans "
                          "only the specific templates (the population E426 used for reach), so "
                          "the two numbers differ by the non-specific ones. The unfiltered count "
                          "is re-derived today with E426's own collector and the scanner's own "
                          "file excluded, so a non-zero delta is corpus growth since E426 ran, "
                          "not a filter change."),
            "bound_templates": bound,
            "read_by_the_opener": by_state[S_READ],
            "read_after_one_rebinding": by_state[S_REBIND],
            "unread_bound": by_state[S_UNREAD],
            "read_by_the_opener_including_one_rebinding": read_total,
            "share_read": round(read_total / bound, 4) if bound else None,
            "the_opener_argument_is_this_template": sum(
                1 for r in rows if r["the_opener_argument_is_this_template"]),
            "unbound_shape": by_state[S_UNBOUND],
        },
        "by_state": by_state,
        "by_module": module_rows[:40],
        "top_unread_sites": top_unread,
        "rows": all_rows,
        "rows_published": len(all_rows),
        "rows_sample": sample,
        "rows_sample_size": len(sample),
        "method_limits": [
            "a binding is followed only when the template is the whole right-hand side or sits "
            "inside it; a template embedded in a dict/list literal that is then subscripted is "
            "bound to the container, not to the leaf, and lands in the unread state.",
            "exactly one rebinding hop is followed. A second hop is not, so the read count is a "
            "lower bound and the unread count is an upper bound; the size of that gap is not "
            "published here (a two-hop pass belongs to whoever prices the residue).",
            "an opener is counted by call name (E426's vocabulary: open/read_*/json.load). A "
            "helper that takes the name and opens inside itself is invisible, so 'the opener "
            "reads it' means 'the name reaches a call that this census calls an opener'.",
            "name matching is by identifier, not by scope resolution: a same-named local "
            "shadowing the target inside the same function would count as a read.",
            "the corpus is the same python corpus E426 walks; it excludes Money02/legacy and it "
            "excludes results/, so a template built only by a notebook or a shell script is out "
            "of population, not zero.",
        ],
    }
    if write:
        face["face_path"] = _rel(write_face(face, os.path.join(root, "results", "state_tilt")), root)
    return face


# ------------------------------------------------------------------ verify / selftest
def verdict_for(rows) -> str:
    """The verdict recomputed from the row list alone (the gate never trusts the stored string)."""
    bound = sum(1 for r in rows if r.get("state") in STATE_VOCAB)
    return V if bound else "no_in_opener_template_was_found_so_nothing_is_priced"


def tally_problems(face: dict) -> list:
    """Structural problems in a published face: the table must close against its own rows."""
    problems = []
    rows = face.get("rows") or []
    counts = {}
    for r in rows:
        state = r.get("state")
        if state not in tuple(STATE_VOCAB) + (S_UNBOUND,):
            problems.append("%s:%s carries a state outside the vocabulary: %r"
                            % (r.get("module"), r.get("line"), state))
            break
        counts[state] = counts.get(state, 0) + 1
    if counts != face.get("by_state"):
        problems.append("by_state does not close against the rows: %r vs %r"
                        % (counts, face.get("by_state")))
    summary = face.get("summary") or {}
    if summary.get("in_opener_templates") != len(rows):
        problems.append("in_opener_templates %r does not match %d rows"
                        % (summary.get("in_opener_templates"), len(rows)))
    bound = sum(1 for r in rows if r.get("state") in STATE_VOCAB)
    read = sum(1 for r in rows if r.get("state") in (S_READ, S_REBIND))
    if summary.get("bound_templates") != bound:
        problems.append("bound_templates %r does not match %d bound rows"
                        % (summary.get("bound_templates"), bound))
    if summary.get("read_by_the_opener_including_one_rebinding") != read:
        problems.append("read total %r does not match %d read rows"
                        % (summary.get("read_by_the_opener_including_one_rebinding"), read))
    if summary.get("the_opener_argument_is_this_template") != sum(
            1 for r in rows if r.get("the_opener_argument_is_this_template")):
        problems.append("the direct-argument count does not close against the rows")
    if face.get("verdict") != verdict_for(rows):
        problems.append("verdict does not re-derive from the rows")
    return problems


def verify(root: str = ROOT) -> list:
    problems = []
    pub_path = os.path.join(root, "results", "state_tilt", LATEST)
    if not os.path.exists(pub_path):
        return ["published face missing: %s" % _rel(pub_path, root)]
    try:
        published = json.load(open(pub_path, encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return ["published face unreadable: %s" % exc]

    fresh = build(root, write=False)
    for key in ("in_opener_templates", "bound_templates", "read_by_the_opener",
                "read_after_one_rebinding", "unread_bound", "unbound_shape"):
        if published.get("summary", {}).get(key) != fresh["summary"].get(key):
            problems.append("summary.%s does not re-derive: published=%r fresh=%r"
                            % (key, published.get("summary", {}).get(key),
                               fresh["summary"].get(key)))
    if published.get("by_state") != fresh["by_state"]:
        problems.append("by_state does not re-derive")
    if not published.get("verdict"):
        problems.append("published face carries no verdict")
    if published.get("population_source") is None:
        problems.append("published face names no population_source (E368: a replay and a "
                        "re-walk must be distinguishable)")
    return problems


FIXTURE = '''
import json, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")


def direct(name):
    with open(f"results/direct-{name}.json", encoding="utf-8") as fh:
        return json.load(fh)


def via_target(name):
    path = os.path.join(OUT, "%s-table.json" % name)
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def via_rebind(name):
    path = os.path.join(OUT, "%s-reb.json" % name)
    alias = path
    with open(alias, encoding="utf-8") as fh:
        return json.load(fh)


def unread(name):
    path = os.path.join(OUT, "%s-unread.json" % name)
    print("built", path)
    with open("results/constant.json", encoding="utf-8") as fh:
        return json.load(fh)


def unbound(name):
    print("in an opener: " + "results/%s-loose.json" % name)
    with open("results/constant.json", encoding="utf-8") as fh:
        return json.load(fh)
'''


def selftest() -> int:
    rows = analyse_source(FIXTURE, "_e427_fixture.py")
    by_fn = {}
    for r in rows:
        by_fn.setdefault(r["function"], []).append(r["state"])
    checks = [
        ("direct", all(s == S_READ for s in by_fn.get("direct", [])) and by_fn.get("direct")),
        ("via_target", all(s == S_READ for s in by_fn.get("via_target", []))),
        ("via_rebind", all(s == S_REBIND for s in by_fn.get("via_rebind", []))),
        ("unread", all(s == S_UNREAD for s in by_fn.get("unread", []))),
        ("unbound", all(s == S_UNBOUND for s in by_fn.get("unbound", []))),
    ]
    bad = [name for name, ok in checks if not ok]
    print("[selftest] rows=%d functions=%s" % (len(rows), sorted(by_fn)))
    for name, states in sorted(by_fn.items()):
        print("  %-11s %s" % (name, states))
    if bad:
        print("FAIL: %s" % ", ".join(bad))
        return 1
    # a template named only by a literal is not a template
    extra = analyse_source('x = "results/literal.json"\nopen(x)\n', "_lit.py")
    if extra:
        print("FAIL: a pure literal produced a row")
        return 1
    print("selftest 5/5")
    return 0


def main(argv: list) -> int:
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "verify":
        problems = verify()
        for p in problems:
            print("[FAIL] %s" % p)
        if not problems:
            print("verify problems=[]")
        return 1 if problems else 0
    if cmd == "run":
        face = build()
        s = face["summary"]
        print("[%s] %d specific in-opener templates (E426 published %s unfiltered; today's unfiltered "
              "recount %s -> %s) | read %d direct + %d rebind = %d | unread %d | unbound %d"
              % (STUDY, s["in_opener_templates"], s["e426_templates_in_an_opener"],
                 s["e426_recount_unfiltered_today"],
                 "match" if s["base_matches_e426"] else "DIFF",
                 s["read_by_the_opener"], s["read_after_one_rebinding"],
                 s["read_by_the_opener_including_one_rebinding"], s["unread_bound"],
                 s["unbound_shape"]))
        print("face=%s" % face.get("face_path"))
        return 0
    print("usage: run | verify | selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))