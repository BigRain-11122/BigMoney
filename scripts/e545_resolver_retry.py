"""E545 -- do the three arms E533 left open move once E536's interpreter is pointed at them?

E533 (results/state_tilt/CALLPUREARM-2026-11-08.json) published four arms of E527's population and
closed exactly one, the arm whose argument was ``list(range(6))``.  The three it left open were left
open for reasons that are *not* "no resolver tried":

    scripts/e285_interrange_gap_ceiling.py:505   argument ``interval(off['rows'], 'tight')``
    scripts/regime5_validation.py:173            argument ``stats_idxs`` (the caller's own parameter)
    scripts/regime5_validation.py:319            argument ``win_stats``  (a bound non-call expression)

E536 then built a literal interpreter that runs a repo-source body with a site's arguments bound to
it.  E533's three arms were never re-read with it, so "not decidable" and "not measured" are the same
sentence in the published face.  This study separates them by running three passes per arm:

  * ``verbatim``  -- E536's ``evaluate_argument`` unchanged, at the published site line;
  * ``extended``  -- the same interpreter with the caller module's own functions in its ``_fn_map``
                     and with every free name inside the argument expression bound one hop back in
                     the caller, so ``interval(off['rows'], 'tight')`` is a value rather than a
                     name the interpreter never heard of;
  * ``one_hop_out`` -- only for an arm whose argument is the caller's own parameter: the call sites
                     of that caller, with their own argument for the parameter resolved the same way.

Nothing in this repository is executed -- the tree is read as text and interpreted by E536's
evaluator, and no source is rewritten.  An item store between a binding and the site is *not*
replayed here (that is E544's subject); the fold's value is the unmutated container's and the store
lines are published beside it.

    python scripts/e545_resolver_retry.py build     # write the face
    python scripts/e545_resolver_retry.py check     # gate the published face (fast)
    python scripts/e545_resolver_retry.py verify    # re-derive from the tree and gate
    python scripts/e545_resolver_retry.py selftest  # fixture corpus + doctored faces
"""
from __future__ import annotations

import ast
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e527_undecidable_arm as e527  # noqa: E402
import e533_call_pure_arm as e533  # noqa: E402
import e536_inlined_fold as e536  # noqa: E402

OUTDIR = os.path.join(ROOT, "results", "state_tilt")

CARD = ("E545-WHICH-OF-E533-S-REMAINING-OPEN-ARMS-THE-E536-RESOLVER-CAN-SETTLE-ONCE-THE-"
        "INTERPRETER-IS-IN-HAND")
STUDY = "E545_resolver_retry"
DATE_STAMP = "2026-11-08"
FACE_NAME = "resolverretry_latest.json"
DATED_PREFIX = "RESOLVERRETRY"
PARENT_FACE = "CALLPUREARM-2026-11-08.json"
# the arm E536 named as its own limit; the population must contain it or "priced the pattern"
# would be claimed off a scan that never reached the witness
WITNESS = ("scripts/e285_interrange_gap_ceiling.py", 505)
SELF_EXCLUDED = ("e545_", "run_e545", "_e545", "RESOLVERRETRY", "resolverretry_")

# --- what a pass produced -----------------------------------------------------------------
R_VALUE = "the_expression_folds_to_a_value"
R_PARAM = "the_expression_is_a_parameter_of_the_caller"
R_UNFOLLOWABLE = "the_expression_reads_something_this_resolver_cannot_follow"
R_ERROR = "the_expression_could_not_be_read"
RESULT_VOCAB = (R_VALUE, R_PARAM, R_UNFOLLOWABLE, R_ERROR)

# --- the three passes ---------------------------------------------------------------------
P_VERBATIM = "verbatim_e536_resolver_at_the_published_site"
P_EXTENDED = "extended_resolver_with_free_names_bound_one_hop_back"
P_ONE_HOP = "one_hop_out_to_the_callers_call_sites"
PASS_VOCAB = (P_VERBATIM, P_EXTENDED, P_ONE_HOP)

# --- per-arm outcome ----------------------------------------------------------------------
O_CLOSED_VERBATIM = "the_arm_closes_under_the_unmodified_resolver"
O_CLOSED_EXTENDED = "the_arm_closes_once_the_free_names_are_bound_one_hop_back"
O_OPEN_PARAM = "the_arm_stays_open_because_its_argument_is_the_callers_parameter"
O_OPEN_READ = "the_arm_stays_open_because_the_expression_reads_a_value_no_static_resolver_follows"
O_UNREAD = "the_arm_could_not_be_re_read_because_the_published_expression_does_not_parse"
OUTCOME_VOCAB = (O_CLOSED_VERBATIM, O_CLOSED_EXTENDED, O_OPEN_PARAM, O_OPEN_READ, O_UNREAD)

V_ALL = "every_open_arm_E533_left_closes_once_the_interpreters_own_module_functions_are_in_hand"
V_PARAM_ONLY = "the_arms_that_stay_open_stay_open_on_a_callers_parameter_or_a_read_no_resolver_follows"
V_NONE_MOVED = "no_open_arm_moves_under_the_extension_so_the_refusal_was_never_about_the_resolver"
V_EMPTY = "no_open_arm_in_the_parent_was_available_to_re_read"
VERDICT_VOCAB = (V_ALL, V_PARAM_ONLY, V_NONE_MOVED, V_EMPTY)


def _now():
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def _is_self(name):
    return any(prefix in name for prefix in SELF_EXCLUDED)


def _reason(exc):
    return "%s%s" % (exc.why, (":" + exc.detail) if getattr(exc, "detail", None) else "")


# ------------------------------------------------------------------ population
def load_parent(root=None):
    root = root or ROOT
    with open(os.path.join(root, "results", "state_tilt", PARENT_FACE), "r", encoding="utf-8") as fh:
        return json.load(fh)


def population(parent):
    """Every arm E533 published open -- the ones whose call did not fold to a literal."""
    rows = []
    for arm in parent.get("arms") or []:
        if arm.get("fold_class") == e533.F_FOLDS:
            continue
        rows.append(arm)
    return rows


# ------------------------------------------------------------------ the resolver passes
def free_names(node):
    out = []
    for sub in ast.walk(node):
        if isinstance(sub, ast.Name) and isinstance(sub.ctx, ast.Load) and sub.id not in out:
            out.append(sub.id)
    return out


def _module_env(root, rel):
    tree = e536.module_tree(root, rel)
    return {"_fn_map": e536._top_functions(tree)}


def eval_binding(bound, root, rel, bound_line, env, depth, seen):
    """The value of one binding expression, following a repo call once."""
    if depth > 3:
        raise e536._Uneval("the_binding_chain_is_deeper_than_three_hops")
    if isinstance(bound, ast.Call) and isinstance(bound.func, ast.Name):
        name = bound.func.id
        if name in e533.FOLDERS or name in e536.BUILTIN_NAMES:
            # a builtin call is the interpreter's own job, not a repository callee
            return e536.ev(bound, env, root, 0)
        if name in seen:
            raise e536._Uneval("the_binding_is_cyclic", name)
        found = e536.find_callee(root, rel, name)
        if not found or found[1] is None:
            raise e536._Uneval("the_binding_calls_a_name_no_single_module_defines", name)
        crel, fn, ctree = found[0], found[1], found[2]
        fn._e536_rel = crel
        body_class, _reads = e536.classify_body(fn, ctree, root)
        if body_class not in (e536.B_PURE, e536.B_REPO_CALL):
            raise e536._Uneval("the_binding_calls_a_body_classed_%s" % body_class, name)
        args = []
        for arg in bound.args:
            cls, val, _txt, why, _b = resolve(arg, root, rel, bound_line, depth + 1, seen | {name})
            if val is None:
                raise e536._Uneval("an_argument_of_the_binding_call_does_not_fold",
                                   "%s:%s" % (ast.unparse(arg)[:40], why or cls))
            args.append(val)
        return e536.call_function(fn, args, {}, root)
    return e536.ev(bound, env, root, 0)


def resolve(node, root, rel, line, depth=0, seen=frozenset()):
    """(class, value, value_text, reason, bindings) for one expression at one site."""
    tree = e536.module_tree(root, rel)
    if tree is None:
        return R_ERROR, None, None, "the_site_s_module_could_not_be_parsed", []
    env = _module_env(root, rel)
    bindings = []
    # a name whose call is already a same-module function is resolved by the interpreter itself,
    # not by a binding lookup -- publishing it as "no binding" would say the expression reads
    # something it does not
    called = {sub.func.id for sub in ast.walk(node)
              if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name)}
    for name in free_names(node):
        if name in env or name in e536.BUILTIN_NAMES or name in e533.FOLDERS:
            continue
        if name in called and name in env.get("_fn_map", {}):
            continue
        kind, bound, bound_line = e536._binding_node(root, rel, line, name)
        rec = {"name": name, "binding_kind": kind, "bound_line": bound_line,
               "class": None, "value_text": None, "reason": None}
        if bound is None:
            rec["class"] = R_PARAM if kind == "parameter" else R_UNFOLLOWABLE
            rec["reason"] = ("the_name_is_the_caller_s_own_parameter" if kind == "parameter"
                             else "no_binding_of_this_name_before_the_site")
        else:
            try:
                value = eval_binding(bound, root, rel, bound_line, env, depth, seen | {name})
                env[name] = value
                rec["class"] = R_VALUE
                rec["value_text"] = e533._text(value)[:160]
            except e536._Uneval as exc:
                rec["class"] = R_UNFOLLOWABLE
                rec["reason"] = _reason(exc)
        bindings.append(rec)
    if any(b["class"] == R_PARAM for b in bindings):
        return R_PARAM, None, None, "a_free_name_in_the_expression_is_the_caller_s_parameter", bindings
    stuck = [b for b in bindings if b["class"] != R_VALUE]
    if stuck:
        # name the binding that stopped it, so an open arm reads "X binds to a read of Y"
        return (R_UNFOLLOWABLE, None, None,
                "%s_binds_to_%s" % (stuck[0]["name"], stuck[0]["reason"]), bindings)
    try:
        value = e536.ev(node, env, root, 0)
        return R_VALUE, value, e533._text(value)[:200], None, bindings
    except e536._Uneval as exc:
        return R_UNFOLLOWABLE, None, None, _reason(exc), bindings


def _text_of(value):
    try:
        return e533._text(value)[:200]
    except Exception:
        return repr(value)[:200]


def verbatim_pass(node, root, source, line):
    cls, txt, val, why = e536.evaluate_argument(node, root, source, line)
    rec = {"pass": P_VERBATIM, "class": e536_site_class(cls), "value_text": txt,
           "reason": why}

    if val is not None:
        rec["value_text"] = _text_of(val)
    return rec


def e536_site_class(cls):
    """E536's site classes, mapped into this study's result vocabulary."""
    if cls == e536.S_LITERAL:
        return R_VALUE
    if cls == e536.S_LITERAL_ONE_HOP:
        return R_VALUE
    return R_UNFOLLOWABLE


def one_hop_out(root, source, callee_fn, parameter):
    """For an arm whose argument is the caller's own parameter: its call sites."""
    tree = e536.module_tree(root, source)
    out = []
    if tree is None:
        return out
    params = e536._param_names(callee_fn)
    if parameter not in params:
        return out
    idx = params.index(parameter)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
            continue
        if node.func.id != callee_fn.name:
            continue
        if idx >= len(node.args):
            out.append({"site_line": getattr(node, "lineno", 0),
                        "argument_expression": None, "class": R_UNFOLLOWABLE,
                        "value_text": None,
                        "reason": "the_site_does_not_pass_this_positional_argument"})
            continue
        arg = node.args[idx]
        cls, val, txt, why, _b = resolve(arg, root, source, getattr(node, "lineno", 0))
        out.append({"site_line": getattr(node, "lineno", 0),
                    "argument_expression": ast.unparse(arg)[:120],
                    "class": cls, "value_text": txt, "reason": why})
    return sorted(out, key=lambda r: r["site_line"] or 0)


def analyse_arm(arm, root=None):
    root = root or ROOT
    rec = {
        "source": arm.get("source"),
        "line": arm.get("line"),
        "callee": arm.get("callee"),
        "parameter": arm.get("parameter"),
        "argument_expression": arm.get("argument_expression"),
        "e533_argument_kind": arm.get("argument_kind"),
        "e533_fold_class": arm.get("fold_class"),
        "verbatim": None,
        "extended": None,
        "one_hop_out": [],
        "intervening_item_stores": [],
        "arm_outcome": O_UNREAD,
        "error": None,
    }
    try:
        node = ast.parse(rec["argument_expression"], mode="eval").body
    except Exception as exc:
        rec["error"] = "the_published_argument_expression_does_not_parse: %s" % exc
        return rec
    rec["verbatim"] = verbatim_pass(node, root, rec["source"], rec["line"])
    cls, val, txt, why, bindings = resolve(node, root, rec["source"], rec["line"])
    rec["extended"] = {"pass": P_EXTENDED, "class": cls, "value_text": txt,
                       "reason": why, "bindings": bindings}
    if rec["e533_argument_kind"] == "the_caller_function_s_own_parameter":
        tree = e536.module_tree(root, rec["source"])
        caller = e533._caller_function(tree, rec["line"]) if tree is not None else None
        if caller is not None:
            # the caller's own parameter is the name the arm's expression is, not the callee's
            # parameter name the census publishes beside it
            caller_param = None
            for bound in (rec["extended"] or {}).get("bindings") or []:
                if bound.get("binding_kind") == "parameter":
                    caller_param = bound["name"]
                    break
            rec["caller_parameter"] = caller_param or rec["parameter"]
            rec["one_hop_out"] = one_hop_out(root, rec["source"], caller, rec["caller_parameter"])
    # every store that sits between a folded binding and the site is published beside the value:
    # the fold reads the container as bound, not as the site sees it (E544 prices the difference)
    stores = []
    for bound in (rec["extended"] or {}).get("bindings") or []:
        if bound.get("class") != R_VALUE or not bound.get("bound_line") or \
                bound["bound_line"] < 0:
            continue
        for store in e536._intervening_item_stores(root, rec["source"],
                                                   bound["bound_line"], rec["line"]):
            stores.append({"binding": bound["name"], "store_line": store["line"],
                           "target": store["target"]})
    rec["intervening_item_stores"] = stores
    rec["arm_outcome"] = _outcome(rec)
    return rec


def _outcome(rec):
    if rec["extended"] and rec["extended"]["class"] == R_VALUE:
        if rec["verbatim"] and rec["verbatim"]["class"] == R_VALUE:
            return O_CLOSED_VERBATIM
        return O_CLOSED_EXTENDED
    if rec["extended"] and rec["extended"]["class"] == R_PARAM:
        return O_OPEN_PARAM
    if rec["extended"] and rec["extended"]["class"] in (R_UNFOLLOWABLE,):
        return O_OPEN_READ
    return O_UNREAD


# ------------------------------------------------------------------ summary / verdict
def _count(rows, key):
    out = {}
    for row in rows:
        val = row.get(key)
        out[val] = out.get(val, 0) + 1
    return out


def _summary(rows):
    closed = sum(1 for r in rows if r["arm_outcome"] in (O_CLOSED_VERBATIM, O_CLOSED_EXTENDED))
    return {
        "open_arms_in_parent": len(rows),
        "arms_closed": closed,
        "arms_closed_by_the_extension_only": sum(1 for r in rows
                                                 if r["arm_outcome"] == O_CLOSED_EXTENDED),
        "arms_still_open": len(rows) - closed,
        "arms_by_outcome": _count(rows, "arm_outcome"),
        "verbatim_by_class": _count([r["verbatim"] or {} for r in rows], "class"),
        "extended_by_class": _count([r["extended"] or {} for r in rows], "class"),
        "arms_with_call_sites_published": sum(1 for r in rows if r["one_hop_out"]),
        "call_sites_published": sum(len(r["one_hop_out"]) for r in rows),
        "call_sites_that_fold": sum(1 for r in rows for s in r["one_hop_out"]
                                    if s["class"] == R_VALUE),
        "witness_in_population": any((r["source"], r["line"]) == WITNESS for r in rows),
        "arms_with_a_store_between_binding_and_site":
            sum(1 for r in rows if r["intervening_item_stores"]),
    }


def _verdict(summary):
    if not summary["open_arms_in_parent"]:
        return V_EMPTY
    if summary["arms_still_open"] == 0:
        return V_ALL
    if summary["arms_closed"] == 0:
        return V_NONE_MOVED
    return V_PARAM_ONLY


def build(root=None, write=True, rows=None, parent=None, witness_required=True):
    root = root or ROOT
    if rows is None:
        parent = parent or load_parent(root)
        rows = [analyse_arm(a, root) for a in population(parent)]
    summary = _summary(rows)
    face = {
        "study": STUDY,
        "card": CARD,
        "title": ("whether E533's three remaining open arms move once E536's literal interpreter "
                  "has the caller module's own functions and one hop of free-name binding"),
        "generated": _now(),
        "evidence_cutoff": DATE_STAMP,
        "population_source": ("%s::population() -- every arm E533 published whose call did not "
                              "fold to a literal" % os.path.basename(__file__)),
        "parent_face": PARENT_FACE,
        "method_limits": [
            "the resolver is E536's interpreter unchanged plus two things it did not have: the "
            "caller module's own top-level functions in its _fn_map, and every free name inside "
            "the argument expression bound one hop back in the caller",
            "an item store between a binding and the site is counted and published but NOT "
            "replayed -- the folded value is the unmutated container's, which is E544's subject",
            "one_hop_out is published only for an arm whose argument is the caller's own "
            "parameter; it reads that caller's call sites in the same module and resolves the "
            "argument passed at that position, so a parameter filled by another module's caller "
            "stays 'not measured'",
            "nothing in this repository is executed and no source is rewritten",
            "a fixture corpus is not a repository: the selftest proves the resolver's behaviour "
            "on constructed arms, the face is the repository's own reading",
        ],
        "summary": summary,
        "verdict": _verdict(summary),
        "verdict_vocab": list(VERDICT_VOCAB),
        "result_vocab": list(RESULT_VOCAB),
        "pass_vocab": list(PASS_VOCAB),
        "arm_outcome_vocab": list(OUTCOME_VOCAB),
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
    text = json.dumps(face, ensure_ascii=False, indent=1) + "\n"
    for path in (os.path.join(outdir, "%s-%s.json" % (DATED_PREFIX, DATE_STAMP)),
                 os.path.join(outdir, FACE_NAME)):
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
    return text


def load_face(root=None):
    root = root or ROOT
    with open(os.path.join(root, "results", "state_tilt", FACE_NAME), "r", encoding="utf-8") as fh:
        return json.load(fh)


def face_problems(face, witness_required=True):
    problems = []
    rows = face.get("arms") or []
    summary = face.get("summary") or {}
    if face.get("verdict") not in VERDICT_VOCAB:
        problems.append("verdict %r is not in its own vocabulary" % (face.get("verdict"),))
    if summary.get("open_arms_in_parent") != len(rows):
        problems.append("open_arms_in_parent %r does not equal the published arms %d"
                        % (summary.get("open_arms_in_parent"), len(rows)))
    rec = _summary(rows)
    for key in ("arms_closed", "arms_closed_by_the_extension_only", "arms_still_open",
                "arms_with_call_sites_published", "call_sites_published",
                "call_sites_that_fold", "witness_in_population",
                "arms_with_a_store_between_binding_and_site"):
        if summary.get(key) != rec[key]:
            problems.append("%s does not re-derive (%r vs %r)" % (key, summary.get(key), rec[key]))
    for key in ("arms_by_outcome", "verbatim_by_class", "extended_by_class"):
        if summary.get(key) != rec[key]:
            problems.append("%s does not re-derive" % key)
    if _verdict(summary) != face.get("verdict"):
        problems.append("the verdict does not re-derive from the summary")
    if witness_required and not summary.get("witness_in_population"):
        problems.append("the e285 witness E536 published as its own limit is not in the population")
    for row in rows:
        where = "%s:%s" % (row.get("source"), row.get("line"))
        if row.get("arm_outcome") not in OUTCOME_VOCAB:
            problems.append("%s: arm_outcome %r is not in its vocabulary"
                            % (where, row.get("arm_outcome")))
        for name in ("verbatim", "extended"):
            block = row.get(name) or {}
            if block.get("class") not in RESULT_VOCAB:
                problems.append("%s: %s class %r is not in its vocabulary"
                                % (where, name, block.get("class")))
        if row.get("arm_outcome") in (O_CLOSED_VERBATIM, O_CLOSED_EXTENDED):
            if not (row.get("extended") or {}).get("value_text"):
                problems.append("%s: a closed arm carries no folded value" % where)
        else:
            if (row.get("extended") or {}).get("value_text"):
                problems.append("%s: an open arm carries a folded value" % where)
            if not (row.get("extended") or {}).get("reason"):
                problems.append("%s: an open arm carries no reason" % where)
        if row.get("arm_outcome") == O_OPEN_PARAM and not row.get("one_hop_out"):
            problems.append("%s: a parameter arm publishes no call sites" % where)
        if row.get("arm_outcome") == O_CLOSED_EXTENDED and \
                (row.get("verbatim") or {}).get("class") == R_VALUE:
            problems.append("%s: an arm marked extension-only already folded verbatim" % where)
        for site in row.get("one_hop_out") or []:
            if site.get("class") not in RESULT_VOCAB:
                problems.append("%s: a call site class %r is not in its vocabulary"
                                % (where, site.get("class")))
    return problems


def check(face=None, root=None):
    face = face if face is not None else load_face(root)
    problems = face_problems(face)
    print(json.dumps({"study": STUDY, "face": FACE_NAME, "problems": problems,
                      "verdict": face.get("verdict"), "arms": len(face.get("arms") or []),
                      "summary": face.get("summary")}, ensure_ascii=False, indent=1))
    return 0 if not problems else 1


def verify(root=None):
    root = root or ROOT
    live = build(root, write=False)
    published = load_face(root)
    problems = face_problems(live)
    if live.get("arms") != published.get("arms"):
        live_by = {(r["source"], r["line"]): r for r in live["arms"]}
        pub_by = {(r["source"], r["line"]): r for r in published["arms"]}
        missing = sorted(set(live_by) - set(pub_by))
        extra = sorted(set(pub_by) - set(live_by))
        if missing:
            problems.append("the published face is missing %d live arms, e.g. %r"
                            % (len(missing), missing[:3]))
        if extra:
            problems.append("the published face carries %d arms that no longer reproduce, e.g. %r"
                            % (len(extra), extra[:3]))
        for key in sorted(set(live_by) & set(pub_by)):
            if live_by[key] != pub_by[key]:
                problems.append("arm %r re-derives differently (published %r, live %r)"
                                % (key, (pub_by[key].get("extended") or {}).get("value_text"),
                                   (live_by[key].get("extended") or {}).get("value_text")))
    if live.get("verdict") != published.get("verdict"):
        problems.append("the verdict re-derives to %r, the face publishes %r"
                        % (live.get("verdict"), published.get("verdict")))
    print(json.dumps({"study": STUDY, "problems": problems, "verdict": live.get("verdict"),
                      "arms_live": len(live["arms"]), "arms_published": len(published["arms"]),
                      "summary": live.get("summary")}, ensure_ascii=False, indent=1))
    return 0 if not problems else 1


# ------------------------------------------------------------------ selftest
FIXTURE = '''\
"""fixture module for E545."""

SCALE = 2


def _td(lo, hi):
    return {"lo": lo + 0.0, "hi": hi + 0.0}


def fixture_arm():
    rows = [{"row": "a", "tight": _td(1.0, 1.1)},
            {"row": "b", "tight": _td(1.0, 1.1)}]
    return {"arm": "a:1", "rows": rows}


def interval(rows, tail):
    lows = [r[tail]["lo"] for r in rows]
    highs = [r[tail]["hi"] for r in rows]
    return {"lo": min(lows), "hi": max(highs)}


def down_the_rows(rows, tail):
    off = fixture_arm()
    off["rows"][1]["tight"] = _td(0.9, 1.2)
    hull = interval(off["rows"], tail)
    return {"hull": hull}


def reads_the_face(path):
    return read_json(path)


def table(idxs):
    return {"n": len(idxs)}


def from_a_face():
    rows_arg = reads_the_face("x.json")
    return table(rows_arg)


def caller(rows_arg, idxs):
    return table(idxs)


def lit_caller():
    return caller([1, 2], list(range(6)))


def param_caller():
    return lit_caller()
'''

DOCTORED = [
    ("verdict", lambda f: f.__setitem__("verdict", "a_verdict_this_study_never_publishes")),
    ("class", lambda f: f["arms"][0]["extended"].__setitem__("class", "a_class_not_published")),
    ("value", lambda f: f["arms"][0].__setitem__("arm_outcome", O_CLOSED_EXTENDED)),
    ("count", lambda f: f["summary"].__setitem__("arms_closed", 99)),
    ("witness", lambda f: f["summary"].__setitem__("witness_in_population", True)
     if not f["summary"].get("witness_in_population") else None),
]


def _fixture_population():
    return [
        # a direct call whose arguments are a repo call over a container bound from a repo call
        {"source": "fixture.py", "line": 30, "callee": "down_the_rows",
         "parameter": "tail", "argument_expression": "interval(off['rows'], 'tight')",
         "argument_kind": "a_direct_call_at_the_site",
         "fold_class": e533.F_REPO_CALLEE},
        # the caller's own parameter
        {"source": "fixture.py", "line": 46, "callee": "table",
         "parameter": "idxs", "argument_expression": "idxs",
         "argument_kind": "the_caller_function_s_own_parameter",
         "fold_class": e533.F_NOT_A_CALL},
        # a name bound from an expression that reads the tree
        {"source": "fixture.py", "line": 50, "callee": "table",
         "parameter": "idxs", "argument_expression": "rows_arg",
         "argument_kind": "a_name_the_caller_binds_from_an_expression_that_is_not_a_call",
         "fold_class": e533.F_NOT_A_CALL},
    ]


def selftest():
    """Fixture corpus: the three passes must separate a foldable arm from a parameter arm."""
    legs = []

    def leg(name, ok, detail=""):
        legs.append({"leg": name, "ok": bool(ok), "detail": detail})

    root = tempfile.mkdtemp(prefix="e545_selftest_")
    try:
        path = os.path.join(root, "fixture.py")
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(FIXTURE)
        text = FIXTURE.split("\n")

        def line_of(needle):
            for idx, line in enumerate(text, start=1):
                if needle in line:
                    return idx
            raise AssertionError("fixture line not found: %r" % needle)

        arms = _fixture_population()
        arms[0]["line"] = line_of("hull = interval(off")
        arms[1]["line"] = line_of("return table(idxs)")
        arms[2]["line"] = line_of("return table(rows_arg)")
        node = ast.parse(arms[1]["argument_expression"], mode="eval").body

        cls, val, _txt, why, binds = resolve(node, root, "fixture.py", arms[1]["line"])
        leg("a parameter arm is published as a parameter", cls == R_PARAM, "%s/%s" % (cls, why))
        leg("the parameter arm publishes its binding row", any(b["name"] == "idxs" for b in binds))

        rows = [analyse_arm(a, root) for a in arms]
        leg("three fixture arms are analysed", len(rows) == 3)
        # the direct-call arm: `off` is a repo call, `interval` is same-module
        direct = [r for r in rows if r["argument_expression"].startswith("interval(")][0]
        leg("a call over a container bound from a repo call does not fold verbatim",
            direct["verbatim"]["class"] != R_VALUE, str(direct["verbatim"]))
        # the store between binding and site must be published, not replayed
        leg("the item store between binding and site is published",
            bool(direct["intervening_item_stores"]),
            str(direct["intervening_item_stores"]))
        # the parameter arm must publish its call sites
        param = rows[1]
        leg("the parameter arm publishes its call sites", param["arm_outcome"] == O_OPEN_PARAM
            and len(param["one_hop_out"]) >= 1, str(param["arm_outcome"]))
        leg("the call-site argument is published with a class",
            all(s["class"] in RESULT_VOCAB for s in param["one_hop_out"]))
        # the tree-reading arm stays open with a reason
        tree_arm = rows[2]
        leg("a name read off the tree stays open with a reason",
            tree_arm["arm_outcome"] == O_OPEN_READ
            and bool((tree_arm["extended"] or {}).get("reason")), str(tree_arm["extended"]))

        face = build(root, write=False, rows=rows, parent=None, witness_required=False)
        problems = face_problems(face, witness_required=False)
        leg("the built face gates clean", problems == [], "; ".join(problems)[:160])
        leg("a hand-written verdict is refused", bool(
            _doctor(face, "verdict")), "a verdict outside the vocabulary was accepted")
        leg("a summary that outgrows its rows is refused", bool(_doctor(face, "count")))
        leg("a class outside the vocabulary is refused", bool(_doctor(face, "class")))
    finally:
        try:
            import shutil
            shutil.rmtree(root, ignore_errors=True)
        except Exception:
            pass
    good = sum(1 for l in legs if l["ok"])
    print(json.dumps({"study": STUDY, "selftest": "%d/%d" % (good, len(legs)), "legs": legs},
                     ensure_ascii=False, indent=1))
    return 0 if good == len(legs) else 1


def _doctor(face, kind):
    """Copy the face, apply one doctoring, return the problems the gate finds (must be non-empty)."""
    doc = json.loads(json.dumps(face))
    if kind == "verdict":
        doc["verdict"] = "a_verdict_this_study_never_publishes"
    elif kind == "class":
        doc["arms"][0]["extended"]["class"] = "a_class_not_published"
    elif kind == "count":
        doc["summary"]["arms_closed"] = 99
    elif kind == "value":
        doc["arms"][0]["arm_outcome"] = O_CLOSED_EXTENDED
    elif kind == "witness":
        doc["summary"]["witness_in_population"] = not doc["summary"].get("witness_in_population")
    else:
        raise AssertionError("unknown doctoring %r" % kind)
    return face_problems(doc)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    action = argv[0] if argv else "build"
    if action == "build":
        face = build()
        print(json.dumps({"study": STUDY, "wrote": [FACE_NAME,
                                                    "%s-%s.json" % (DATED_PREFIX, DATE_STAMP)],
                          "verdict": face["verdict"], "summary": face["summary"]},
                         ensure_ascii=False, indent=1))
        return 0
    if action == "check":
        return check()
    if action == "verify":
        return verify()
    if action == "selftest":
        return selftest()
    print("usage: %s [build|check|verify|selftest]" % os.path.basename(__file__))
    return 2


if __name__ == "__main__":
    sys.exit(main())