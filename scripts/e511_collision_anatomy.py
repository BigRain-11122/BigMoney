"""E511 -- what is the residual ambiguity made of, at each of the four surviving sites?

E510 re-read E507's 42 ambiguous pairs with a scoped binding table and left four pair sites
ambiguous even then: ``idx`` at ``scripts/etf_book_cash_ladder.py:575`` and ``asof`` at three
lines of ``scripts/etf_book_order.py`` (1033/1043/1059, all inside ``run_card``).  "The scope
itself holds more than one origin" is a verdict about a name, and a name can be ambiguous in
two very different ways:

  * the name is *written more than once* inside the site's own scope, so which write reaches
    the site is a question about order of execution; or
  * the name is written exactly once and the *value* that flows in arrives from somewhere the
    line does not name (a call, a subscript of another name), so the ambiguity is one level
    down and no rename can separate anything, because there is nothing to separate.

This study answers that for each site by enumerating the bindings the site's own scope can
see, classifying each binding by the *shape of its right-hand side* (a seed literal, a step
that extends the symbol itself, a replacement that does not mention it, a call result, ...),
and publishing per site whether a rename removes the residual ambiguity or only a dataflow
read could.

Reuse: the scoped-table machinery of ``scripts/e510_binding_scope.py`` and the resolver
context builder of ``scripts/e507_unresolved_origin.py`` are imported, never copied.  The
population is E510's own published face; it is never re-derived here.

Modes: run|build / check / verify / selftest.  Read-only: check, verify, selftest.
"""
import ast
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import e504_name_compose as base  # noqa: E402
import e507_unresolved_origin as e507  # noqa: E402
import e510_binding_scope as e510  # noqa: E402

ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "collisionanatomy_latest.json"
DATED_PREFIX = "COLLISIONANATOMY"
DATE_STAMP = "2026-11-07"
CARD = "E511-WHICH-OF-THE-FOUR-SURVIVING-PAIRS-IS-A-TRUE-COLLISION-INSIDE-ONE-SCOPE"
STUDY = "E511_collision_anatomy"
UPSTREAM_FACE = os.path.join("results", "state_tilt", "SCOPEDBINDING-2026-11-07.json")
POPULATION_SOURCE = ("results/state_tilt/SCOPEDBINDING-2026-11-07.json pairs whose collapse "
                     "is stays_ambiguous_the_enclosing_scope_itself_holds_more_than_one_origin")
SELF_EXCLUDED = ("e511_", "run_e511", "_e511")

# ---------------------------------------------------------------- vocabulary
K_ONE = "one_in_scope_binding_the_value_enters_through_the_right_hand_side"
K_CHAIN = "sequential_build_up_of_one_meaning_every_step_extends_the_symbol_itself"
K_TWO = "more_than_one_meaning_under_one_name_a_step_replaces_rather_than_extends"
K_BRANCH = "rebinding_where_at_least_one_arm_replaces_and_one_extends"
K_PARAM = "caller_supplied_the_symbol_is_a_parameter_of_the_enclosing_scope"
K_NONE = "no_binding_at_all_in_the_site_scope"
ANATOMY_VOCAB = (K_ONE, K_CHAIN, K_TWO, K_BRANCH, K_PARAM, K_NONE)

RESOLVE_DATAFLOW = "sequential_dataflow_which_write_reaches_the_site"
RESOLVE_OPERAND = "operand_read_what_the_right_hand_side_actually_returns"
RESOLVE_BRANCH = "branch_join_which_arm_runs"
RESOLVE_CALL = "call_site_what_the_caller_passes"
RESOLVE_NONE = "nothing_to_resolve_the_symbol_is_bound_nowhere"
RESOLVE_VOCAB = (RESOLVE_DATAFLOW, RESOLVE_OPERAND, RESOLVE_BRANCH, RESOLVE_CALL, RESOLVE_NONE)

V_ALL = "every_residual_site_is_resolved_by_neither_a_rename_but_the_values"
V_PART = "some_residual_sites_would_separate_under_a_rename_and_the_rest_would_not"
V_RENAME = "every_residual_site_separates_under_a_rename_so_the_bucket_was_two_meanings"
V_EMPTY = "the_scoped_table_left_no_ambiguous_site_to_anatomise"
VERDICT_VOCAB = (V_ALL, V_PART, V_RENAME, V_EMPTY)

# ------------------------------------------------------- binding enumeration
COMPREHENSIONS = (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)


def _scope_nodes(scope):
    """Nodes written directly in this scope; nested scopes and comprehension bodies excluded.

    Each node travels with its ``exclusive`` marker: ``(if_node_id, arm)`` for the innermost
    ``if`` arm it sits in, ``()`` otherwise.  Two writes whose markers name the same ``if``
    node and different arms cannot both execute, which is what separates a branch join from
    two meanings sharing one name.
    """
    plain, comp_targets = [], []

    def rec(node, excl):
        if isinstance(node, e510.NESTED):
            return
        if isinstance(node, COMPREHENSIONS):
            # python 3 comprehensions have their own scope; E507 shadows them, so they are
            # disclosed separately rather than mixed into the scope's own bindings
            for gen in node.generators:
                for sub in ast.walk(gen.target):
                    if isinstance(sub, ast.Name):
                        comp_targets.append(sub.id)
            return
        plain.append((node, excl))
        if isinstance(node, ast.If):
            rec(node.test, excl)
            arm = {"if_line": getattr(node, "lineno", 0), "arm": "body"}
            for child in node.body:
                rec(child, (arm,) + excl)
            arm = {"if_line": getattr(node, "lineno", 0), "arm": "orelse"}
            for child in node.orelse:
                rec(child, (arm,) + excl)
            return
        for child in ast.iter_child_nodes(node):
            rec(child, excl)

    for stmt in e510._scope_statements(scope):
        rec(stmt, ())
    return plain, comp_targets


def _binding_of(node, symbol):
    """(kind, rhs, line) when this node binds ``symbol``, else None."""
    if isinstance(node, ast.Assign):
        for target in node.targets:
            for sub in ast.walk(target):
                if isinstance(sub, ast.Name) and sub.id == symbol:
                    return ("assign", node.value, node.lineno)
    if isinstance(node, ast.AnnAssign) and node.value is not None:
        if isinstance(node.target, ast.Name) and node.target.id == symbol:
            return ("annotated_assign", node.value, node.lineno)
    if isinstance(node, ast.AugAssign):
        if isinstance(node.target, ast.Name) and node.target.id == symbol:
            return ("augmented_assign", node.value, node.lineno)
    if isinstance(node, ast.For):
        for sub in ast.walk(node.target):
            if isinstance(sub, ast.Name) and sub.id == symbol:
                return ("loop_target", node.iter, node.lineno)
    if isinstance(node, (ast.With, ast.AsyncWith)):
        for item in node.items:
            if item.optional_vars is None:
                continue
            for sub in ast.walk(item.optional_vars):
                if isinstance(sub, ast.Name) and sub.id == symbol:
                    return ("with_as", item.context_expr, node.lineno)
    if isinstance(node, ast.NamedExpr):
        if isinstance(node.target, ast.Name) and node.target.id == symbol:
            return ("walrus", node.value, node.lineno)
    if isinstance(node, ast.ExceptHandler) and node.name == symbol:
        return ("exception_as", None, node.lineno)
    return None


SELF_SHAPES = ("aliases_a_name_itself", "branch_on_itself", "subscript_of_itself",
               "arithmetic_on_itself")


def _mentions(node, symbol):
    return any(isinstance(sub, ast.Name) and sub.id == symbol for sub in ast.walk(node))


def rhs_shape(rhs, symbol):
    """What kind of value the right-hand side is, from the AST alone."""
    if rhs is None:
        return "no_value"
    if isinstance(rhs, ast.Constant):
        return "literal_%s" % type(rhs.value).__name__
    if isinstance(rhs, ast.Name):
        return "aliases_a_name_itself" if rhs.id == symbol else "aliases_a_name"
    if isinstance(rhs, ast.BoolOp):
        return "defaulted_expression"
    if isinstance(rhs, ast.IfExp):
        return "branch_on_itself" if _mentions(rhs, symbol) else "branching_expression"
    if isinstance(rhs, ast.Call):
        return "call_result"
    if isinstance(rhs, ast.Subscript):
        return "subscript_of_itself" if _mentions(rhs, symbol) else \
            "subscript_of_another_object"
    if isinstance(rhs, ast.Attribute):
        return "attribute_of_another_object"
    if isinstance(rhs, ast.BinOp):
        return "arithmetic_on_itself" if _mentions(rhs, symbol) else "arithmetic"
    if isinstance(rhs, (ast.List, ast.Tuple)):
        return "literal_sequence"
    return type(rhs).__name__.lower()


def _operand_symbol(rhs):
    """The first other name the right-hand side reads, if any (one level, no recursion)."""
    if rhs is None:
        return ""
    for sub in ast.walk(rhs):
        if isinstance(sub, ast.Name) and isinstance(sub.ctx, ast.Load):
            return sub.id
    return ""


def bindings_in_scope(scope, symbol):
    """Every write of ``symbol`` the scope itself makes, in line order."""
    plain, comps = _scope_nodes(scope)
    out = []
    for node, excl in plain:
        got = _binding_of(node, symbol)
        if got:
            kind, rhs, line = got
            head = excl[0] if excl else None
            out.append({"line": line, "kind": kind, "shape": rhs_shape(rhs, symbol),
                        "operand": _operand_symbol(rhs), "rhs": rhs,
                        "if_arm": head})
    out.sort(key=lambda r: r["line"])
    seen, deduped = set(), []
    for rec in out:
        key = (rec["line"], rec["kind"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(rec)
    return deduped, comps


def mutually_exclusive(bindings):
    """True when every pair of writes sits in different arms of one and the same ``if``."""
    if len(bindings) < 2:
        return False
    pairs = 0
    for i, left in enumerate(bindings):
        for right in bindings[i + 1:]:
            a, b = left.get("if_arm"), right.get("if_arm")
            if not a or not b or a["if_line"] != b["if_line"] or a["arm"] == b["arm"]:
                return False
            pairs += 1
    return pairs > 0


def anatomy_of(bindings, comps, is_param):
    """The class of residual ambiguity at one site."""
    if is_param:
        return K_PARAM, RESOLVE_CALL
    if not bindings:
        return K_NONE, RESOLVE_NONE
    if len(bindings) == 1:
        return K_ONE, RESOLVE_OPERAND
    if mutually_exclusive(bindings):
        return K_BRANCH, RESOLVE_BRANCH
    extending = [b for b in bindings if b["shape"] in SELF_SHAPES]
    replacing = [b for b in bindings if b["shape"] not in SELF_SHAPES
                 and not str(b["shape"]).startswith("literal_")]
    if replacing and not extending:
        return K_TWO, RESOLVE_OPERAND
    if not replacing:
        return K_CHAIN, RESOLVE_DATAFLOW
    return K_BRANCH, RESOLVE_BRANCH


def _excerpt(rhs, src_lines):
    if rhs is None:
        return ""
    lo = max(0, (getattr(rhs, "lineno", 1) or 1) - 1)
    hi = max(lo + 1, getattr(rhs, "end_lineno", lo + 1) or (lo + 1))
    return " ".join(line.strip() for line in src_lines[lo:hi])[:160]


def design_of(root, source, line, symbol):
    """Enumerate the site's own-scope bindings and say what kind of ambiguity that is."""
    ctx = e507.ctx_of(root, source)
    if ctx is None:
        return {"scope": "", "scope_chain": [], "bindings": [], "comprehension_targets": [],
                "anatomy": K_NONE, "resolution": RESOLVE_NONE, "is_parameter": False,
                "source_unparseable": True}
    tree = ctx["tree"]
    chain = e510.scope_chain(tree, line)
    src_lines = io.open(os.path.join(root, source), encoding="utf-8",
                        errors="replace").read().split("\n")
    owner, bindings, comps, is_param = None, [], [], symbol in e510._scope_params(chain[0])
    for scope in chain:
        if isinstance(scope, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            found, got_comps = bindings_in_scope(scope, symbol)
            if found or symbol in e510._scope_params(scope):
                owner, bindings, comps = scope, found, got_comps
                is_param = symbol in e510._scope_params(scope)
                break
        elif isinstance(scope, ast.Module):
            found, got_comps = bindings_in_scope(scope, symbol)
            if found:
                owner, bindings, comps = scope, found, got_comps
                is_param = False
                break
    if owner is None:
        owner = chain[0]
    for rec in bindings:
        rec["rhs"] = _excerpt(rec["rhs"], src_lines)
    anatomy, resolution = anatomy_of(bindings, comps, is_param)
    label = getattr(owner, "name", "Module")
    return {"scope": label,
            "scope_chain": [type(n).__name__ if isinstance(n, ast.Module) else
                            getattr(n, "name", type(n).__name__) for n in chain][:6],
            "is_parameter": is_param,
            "bindings": [dict(rec) for rec in bindings],
            "comprehension_targets": comps,
            "anatomy": anatomy,
            "resolution": resolution,
            "source_unparseable": False}


def _operand_evidence(root, source, line, symbol, bindings):
    """For a single-binding site, say what the operand itself is bound to in the same scope."""
    if len(bindings) != 1:
        return []
    operand = bindings[0].get("operand") or ""
    if not operand or operand == symbol:
        return []
    ctx = e507.ctx_of(root, source)
    if ctx is None:
        return []
    chain = e510.scope_chain(ctx["tree"], line)
    src_lines = io.open(os.path.join(root, source), encoding="utf-8",
                        errors="replace").read().split("\n")
    for scope in chain:
        found, _ = bindings_in_scope(scope, operand)
        if found:
            head = found[0]
            return [{"symbol": operand, "line": head["line"], "kind": head["kind"],
                     "shape": head["shape"], "count_in_scope": len(found),
                     "rhs": _excerpt(head["rhs"], src_lines)}]
    return []


# ------------------------------------------------------------------ analysis
def analyse(root=None, upstream=None):
    root = root or ROOT
    up = upstream if upstream is not None else base._load_json(os.path.join(root, UPSTREAM_FACE))
    sites = {}
    for rec in (up.get("pairs") or []):
        if rec.get("collapse") != e510.K_MIXED:
            continue
        sites[(rec.get("source") or "", rec.get("line") or 0,
               rec.get("date_expression") or "")] = rec
    rows = [r for r in (up.get("rows") or [])
            if (r.get("source") or "", r.get("line") or 0,
                r.get("date_expression") or "") in sites]

    records = []
    for (source, line, expr), rec in sorted(sites.items()):
        symbol = rec.get("symbol") or ""
        design = design_of(root, source, line, symbol)
        members = sorted({r.get("path") for r in rows
                          if (r.get("source") or "", r.get("line") or 0,
                              r.get("date_expression") or "") == (source, line, expr)})
        removable = design["anatomy"] in (K_TWO,)
        records.append({
            "source": source, "line": line, "date_expression": expr, "symbol": symbol,
            "scope": design["scope"], "scope_chain": design["scope_chain"],
            "is_parameter": design["is_parameter"],
            "binding_count": len(design["bindings"]),
            "bindings": design["bindings"],
            "comprehension_targets": design["comprehension_targets"],
            "anatomy": design["anatomy"], "resolution": design["resolution"],
            "removable_by_a_rename": removable,
            "operand_evidence": _operand_evidence(root, source, line, symbol,
                                                  design["bindings"]),
            "members": members, "member_count": len(members),
        })
    return {"records": records, "rows": rows}


def _count(records, key, vocab):
    got = {k: 0 for k in vocab}
    for rec in records:
        value = rec.get(key)
        got[value] = got.get(value, 0) + 1
    return got


def _summary(records, rows):
    by_anatomy = _count(records, "anatomy", ANATOMY_VOCAB)
    by_resolution = _count(records, "resolution", RESOLVE_VOCAB)
    return {
        "evidence_cutoff": DATE_STAMP,
        "pair_sites": len(records),
        "members_under_them": len({r.get("path") for r in rows}),
        "sites_by_anatomy": by_anatomy,
        "sites_by_resolution": by_resolution,
        "sites_with_one_in_scope_binding": by_anatomy.get(K_ONE, 0),
        "sites_with_several_in_scope_bindings": len(records) - by_anatomy.get(K_ONE, 0)
        - by_anatomy.get(K_PARAM, 0) - by_anatomy.get(K_NONE, 0),
        "sites_removable_by_a_rename": sum(1 for r in records if r["removable_by_a_rename"]),
        "sites_needing_dataflow": sum(1 for r in records
                                     if r["resolution"] == RESOLVE_DATAFLOW),
        "sites_needing_an_operand_read": sum(1 for r in records
                                             if r["resolution"] == RESOLVE_OPERAND),
        "distinct_sources": len({r["source"] for r in records}),
        "distinct_symbols": len({r["symbol"] for r in records}),
    }


def _verdict(summary):
    total = summary["pair_sites"]
    if total == 0:
        return V_EMPTY
    removable = summary["sites_removable_by_a_rename"]
    if removable == total:
        return V_RENAME
    if removable == 0:
        return V_ALL
    return V_PART


def _answers(summary):
    return {
        "how_many_pair_sites_survive_the_scoped_table": summary["pair_sites"],
        "how_many_members_hang_on_them": summary["members_under_them"],
        "how_many_bind_their_symbol_once_in_the_site_scope":
            summary["sites_with_one_in_scope_binding"],
        "how_many_bind_it_more_than_once": summary["sites_with_several_in_scope_bindings"],
        "how_many_are_removable_by_a_rename": summary["sites_removable_by_a_rename"],
        "how_many_need_a_sequential_dataflow_read": summary["sites_needing_dataflow"],
        "how_many_need_an_operand_level_read": summary["sites_needing_an_operand_read"],
        "how_many_distinct_symbols_are_involved": summary["distinct_symbols"],
    }


def build(root=None, write=True, upstream=None):
    root = root or ROOT
    got = analyse(root, upstream=upstream)
    summary = _summary(got["records"], got["rows"])
    face = {
        "study": STUDY,
        "card": CARD,
        "title": ("E510 left four pair sites ambiguous under the scoped table. Enumerate every "
                  "write the site's own scope makes of that symbol, classify each by the shape "
                  "of its right-hand side, and say per site whether a rename removes the "
                  "residual ambiguity or only a dataflow read could."),
        "evidence_cutoff": DATE_STAMP,
        "generated": e507._now(),
        "population_source": POPULATION_SOURCE,
        "anatomy_vocab": list(ANATOMY_VOCAB),
        "resolution_vocab": list(RESOLVE_VOCAB),
        "verdict_vocab": list(VERDICT_VOCAB),
        "method_limits": [
            "the population is E510's own published face: a site appears because that face "
            "called it ambiguous under the scoped table, not because this study re-read "
            "E507's 42 pairs",
            "the enumeration is syntactic and stops at the site's own scope; a write in a "
            "different function is out of the population even though it carries the name",
            "comprehension targets are excluded from the scope's own bindings and published "
            "as a separate list, because python 3 gives them their own scope (E507's rule)",
            "no dataflow is executed: this face says which sites a rename can separate and "
            "which need one, it never claims to have performed the separation",
            "the right-hand-side excerpt is a single-line collapse of a possibly multi-line "
            "expression; the binding line number is the authority, the excerpt is for the eye",
            "an augmented assignment or a loop target is recorded as a write because it "
            "rebinds the name, even when the value it produces is the same kind as before",
        ],
        "summary": summary,
        "verdict": _verdict(summary),
        "answers": _answers(summary),
        "sites": got["records"],
        "rows": got["rows"],
    }
    if write:
        write_face(face, root)
    return face


def write_face(face, root=None):
    root = root or ROOT
    outdir = os.path.join(root, "results", "state_tilt")
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    for name in (FACE_NAME, "%s-%s.json" % (DATED_PREFIX, DATE_STAMP)):
        with io.open(os.path.join(outdir, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body + "\n")


# ---------------------------------------------------------------------- gate
def summary_problems(summary, sites, rows):
    problems = []
    if summary.get("pair_sites") != len(sites):
        problems.append("pair_sites is not the site count")
    if summary.get("members_under_them") != len({r.get("path") for r in rows}):
        problems.append("members_under_them is not the distinct member count")
    by_anatomy = _count(sites, "anatomy", ANATOMY_VOCAB)
    if summary.get("sites_by_anatomy") != by_anatomy:
        problems.append("sites_by_anatomy does not re-derive from the sites")
    by_resolution = _count(sites, "resolution", RESOLVE_VOCAB)
    if summary.get("sites_by_resolution") != by_resolution:
        problems.append("sites_by_resolution does not re-derive from the sites")
    if summary.get("sites_with_one_in_scope_binding") != by_anatomy.get(K_ONE, 0):
        problems.append("sites_with_one_in_scope_binding is not the one-binding class count")
    if summary.get("sites_removable_by_a_rename") != \
            sum(1 for r in sites if r.get("removable_by_a_rename")):
        problems.append("sites_removable_by_a_rename does not re-derive")
    if summary.get("sites_needing_dataflow") != by_resolution.get(RESOLVE_DATAFLOW, 0):
        problems.append("sites_needing_dataflow is not the dataflow class count")
    if summary.get("sites_needing_an_operand_read") != by_resolution.get(RESOLVE_OPERAND, 0):
        problems.append("sites_needing_an_operand_read is not the operand class count")
    if summary.get("distinct_sources") != len({s.get("source") for s in sites}):
        problems.append("distinct_sources does not re-derive")
    if summary.get("distinct_symbols") != len({s.get("symbol") for s in sites}):
        problems.append("distinct_symbols does not re-derive")
    return problems


def site_problems(face):
    sites = face.get("sites") or []
    rows = face.get("rows") or []
    summary = face.get("summary") or {}
    problems = summary_problems(summary, sites, rows)
    for rec in sites:
        name = "%s:%s" % (rec.get("source"), rec.get("line"))
        if rec.get("anatomy") not in ANATOMY_VOCAB:
            problems.append("%s: anatomy outside the vocabulary" % name)
        if rec.get("resolution") not in RESOLVE_VOCAB:
            problems.append("%s: resolution outside the vocabulary" % name)
        if rec.get("binding_count") != len(rec.get("bindings") or []):
            problems.append("%s: binding_count is not the binding list length" % name)
        if rec.get("member_count") != len(rec.get("members") or []):
            problems.append("%s: member_count is not the member list length" % name)
        if not rec.get("members"):
            problems.append("%s: no member carries this site" % name)
        # the anatomy must re-derive from the published bindings, not be asserted
        bindings = [{"shape": b.get("shape"), "if_arm": b.get("if_arm")}
                    for b in (rec.get("bindings") or [])]
        expect, resolution = anatomy_of(bindings, rec.get("comprehension_targets") or [],
                                       bool(rec.get("is_parameter")))
        if expect != rec.get("anatomy"):
            problems.append("%s: anatomy does not re-derive from its own bindings (%r vs %r)"
                            % (name, rec.get("anatomy"), expect))
        if resolution != rec.get("resolution"):
            problems.append("%s: resolution does not re-derive (%r vs %r)"
                            % (name, rec.get("resolution"), resolution))
        if bool(rec.get("removable_by_a_rename")) != (expect == K_TWO):
            problems.append("%s: removable_by_a_rename contradicts the anatomy" % name)
    if face.get("verdict") != _verdict(summary):
        problems.append("verdict=%r does not re-derive from the summary (%r)"
                        % (face.get("verdict"), _verdict(summary)))
    answers = face.get("answers") or {}
    if answers.get("how_many_pair_sites_survive_the_scoped_table") != summary.get("pair_sites"):
        problems.append("answers site count is not the summary site count")
    if answers.get("how_many_are_removable_by_a_rename") != \
            summary.get("sites_removable_by_a_rename"):
        problems.append("answers rename count is not the summary rename count")
    return problems


def check(face=None, root=None):
    root = root or ROOT
    face = face or base._load_json(os.path.join(root, "results", "state_tilt", FACE_NAME))
    problems = site_problems(face)
    print("check problems=%r" % (problems,))
    return 0 if not problems else 1


def verify(root=None):
    root = root or ROOT
    face = build(root, write=False)
    problems = site_problems(face)
    print("verify problems=%r" % (problems,))
    return 0 if not problems else 1


# ------------------------------------------------------------------ selftest
ALPHA = '''import json


def build(path):
    idx = None
    for part in path:
        idx = part.index if idx is None else idx.union(part.index)
    idx = idx[idx >= "2020-01-01"]
    return idx[-1].date()
'''

BETA = '''import json


def card(nav):
    tk = load(nav)
    asof = tk["priced_bar"] or "unknown"
    with open(asof, "w") as fh:
        fh.write(asof)
    return asof
'''

GAMMA = '''import json


def go(path):
    cal = "2020-01-02"
    cal = compute(path)
    return cal[-1]
'''

DELTA = '''import json


def go(flag, path):
    if flag:
        stamp = pick(path)
    else:
        stamp = stamp2
    return stamp
'''

EPSILON = '''import json


def go(stamp, path):
    return stamp.format(path)
'''

ZETA = '''import json


def go(path):
    return stamp[0]
'''


def _fixture_upstream():
    pairs, rows = [], []

    def site(source, line, expr, symbol, members):
        pairs.append({"source": source, "line": line, "date_expression": expr,
                      "symbol": symbol, "collapse": e510.K_MIXED,
                      "scoped": {"tracks": e507.T_MIXED}, "wide": {"tracks": e507.T_MIXED}})
        for path in members:
            rows.append({"path": path, "site": "S%s" % line, "source": source, "line": line,
                         "date_expression": expr, "collapse": e510.K_MIXED,
                         "scoped_tracks": e507.T_MIXED})
    site("scripts/alpha.py", 9, "idx[-1].date()", "idx", ["results/A-2020-01-02.json"])
    site("scripts/beta.py", 7, "asof", "asof", ["results/B-2020-01-02.json",
                                                "results/B-2020-01-03.json"])
    site("scripts/gamma.py", 7, "cal[-1]", "cal", ["results/C-2020-01-02.json"])
    site("scripts/delta.py", 9, "stamp", "stamp", ["results/D-2020-01-02.json"])
    site("scripts/epsilon.py", 5, "stamp", "stamp", ["results/E-2020-01-02.json"])
    site("scripts/zeta.py", 5, "stamp", "stamp", ["results/Z-2020-01-02.json"])
    # a collapsed pair must not enter the population
    pairs.append({"source": "scripts/theta.py", "line": 4, "date_expression": "d",
                  "symbol": "d", "collapse": e510.K_SINGLE,
                  "scoped": {"tracks": e507.T_DATA}, "wide": {"tracks": e507.T_MIXED}})
    return {"pairs": pairs, "rows": rows}


def selftest():
    checks, failures = 0, []

    def ok(name, cond, detail=None):
        nonlocal checks
        checks += 1
        if not cond:
            failures.append("%s (%r)" % (name, detail))

    import shutil
    import tempfile
    tmp = tempfile.mkdtemp(prefix="e511_selftest_")
    try:
        os.makedirs(os.path.join(tmp, "scripts"))
        for name, body in (("alpha.py", ALPHA), ("beta.py", BETA), ("gamma.py", GAMMA),
                           ("delta.py", DELTA), ("epsilon.py", EPSILON), ("zeta.py", ZETA)):
            with io.open(os.path.join(tmp, "scripts", name), "w", encoding="utf-8",
                         newline="\n") as fh:
                fh.write(body)
        up = _fixture_upstream()
        face = build(root=tmp, write=False, upstream=up)
        by_source = {s["source"]: s for s in face["sites"]}

        alpha = by_source.get("scripts/alpha.py") or {}
        ok("three writes that all extend the symbol are one meaning built in sequence",
           alpha.get("anatomy") == K_CHAIN, alpha.get("anatomy"))
        ok("a build-up chain needs a dataflow read, not a rename",
           alpha.get("resolution") == RESOLVE_DATAFLOW, alpha.get("resolution"))
        ok("a build-up chain is not removable by a rename",
           alpha.get("removable_by_a_rename") is False, alpha.get("removable_by_a_rename"))
        ok("the seed literal and the two extending steps are all published as bindings",
           alpha.get("binding_count") == 3, alpha.get("bindings"))

        beta = by_source.get("scripts/beta.py") or {}
        ok("one in-scope write means the value enters through the right-hand side",
           beta.get("anatomy") == K_ONE, beta.get("anatomy"))
        ok("a single write asks for an operand read, not a dataflow read",
           beta.get("resolution") == RESOLVE_OPERAND, beta.get("resolution"))
        ok("the operand is followed one level and its binding is published",
           (beta.get("operand_evidence") or [{}])[0].get("symbol") == "tk",
           beta.get("operand_evidence"))
        ok("the operand's own shape is reported",
           (beta.get("operand_evidence") or [{}])[0].get("shape") == "call_result",
           beta.get("operand_evidence"))

        gamma = by_source.get("scripts/gamma.py") or {}
        ok("a write that replaces rather than extends is two meanings under one name",
           gamma.get("anatomy") == K_TWO, gamma.get("anatomy"))
        ok("two meanings are the one case a rename separates",
           gamma.get("removable_by_a_rename") is True, gamma.get("removable_by_a_rename"))

        delta = by_source.get("scripts/delta.py") or {}
        ok("one extending arm plus one replacing arm is published as a branch, not as two "
           "meanings", delta.get("anatomy") == K_BRANCH, delta.get("anatomy"))
        ok("a branch asks which arm runs", delta.get("resolution") == RESOLVE_BRANCH,
           delta.get("resolution"))

        epsilon = by_source.get("scripts/epsilon.py") or {}
        ok("a parameter is caller-supplied", epsilon.get("anatomy") == K_PARAM,
           epsilon.get("anatomy"))
        zeta = by_source.get("scripts/zeta.py") or {}
        ok("a symbol bound nowhere in the scope is labelled, not guessed",
           zeta.get("anatomy") == K_NONE, zeta.get("anatomy"))

        ok("a collapsed pair does not enter this population",
           "scripts/theta.py" not in by_source, sorted(by_source))
        ok("every surviving pair site is anatomised",
           face["summary"]["pair_sites"] == 6, face["summary"]["pair_sites"])
        ok("the fixture verdict is mixed evidence, not a blanket rename",
           face["verdict"] == V_PART, face["verdict"])
        ok("the gate passes on the built fixture", site_problems(face) == [],
           site_problems(face))

        doctored = json.loads(json.dumps(face))
        doctored["sites"][0]["anatomy"] = K_TWO
        ok("the gate refuses an anatomy its own bindings contradict",
           site_problems(doctored) != [])
        doctored2 = json.loads(json.dumps(face))
        doctored2["summary"]["sites_removable_by_a_rename"] += 1
        ok("the gate refuses a hand-written rename count", site_problems(doctored2) != [])
        doctored3 = json.loads(json.dumps(face))
        doctored3["verdict"] = V_ALL
        ok("the gate refuses a hand-written verdict", site_problems(doctored3) != [])
        doctored4 = json.loads(json.dumps(face))
        doctored4["sites"][0]["binding_count"] = 99
        ok("the gate refuses a binding count the list contradicts", site_problems(doctored4) != [])
        doctored5 = json.loads(json.dumps(face))
        doctored5["sites"][0]["resolution"] = "guessed"
        ok("the gate refuses a resolution outside the vocabulary", site_problems(doctored5) != [])
        doctored6 = json.loads(json.dumps(face))
        doctored6["sites"][0]["removable_by_a_rename"] = True
        ok("the gate refuses a rename flag that contradicts the anatomy",
           site_problems(doctored6) != [])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("selftest %d/%d" % (checks - len(failures), checks))
    for failure in failures:
        print("FAIL: %s" % failure)
    return 0 if not failures else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    mode = argv[0] if argv else "run"
    if mode in ("run", "build"):
        face = build()
        print("verdict=%s" % face["verdict"])
        print("summary=%s" % json.dumps(face["summary"], ensure_ascii=False, sort_keys=True))
        return 0
    if mode == "check":
        return check()
    if mode == "verify":
        return verify()
    if mode == "selftest":
        return selftest()
    print("unknown mode %r" % mode)
    return 2


if __name__ == "__main__":
    sys.exit(main())