"""E510 -- does the ambiguity survive when the binding table is scoped?

E507 published 42 (member, site) pairs whose date symbol reads as "more than one origin".
Its binding table is module-wide: every assignment anywhere in the module can reach every
site in it, so a comprehension target or an unrelated function-local carries the same name
into the same answer.  This study re-reads those 42 pairs with a scoped table -- nearest
enclosing function first, then the module, comprehension targets shadowed -- and publishes,
per pair site, the binding it gets under each table and whether the ambiguous bucket shrinks.

The point is to separate the ambiguity that lives in the code from the ambiguity the resolver
manufactures, so what remains can be named as a real symbol collision.

Modes: run|build / check / verify / selftest.  Read-only: check, verify, selftest.

Reuse: the resolver, the module context builder and the face IO of
``scripts/e507_unresolved_origin.py`` are imported, never copied.  The population is E507's
own published face; it is never re-derived here.
"""
import ast
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import e504_name_compose as base  # noqa: E402
import e507_unresolved_origin as e507  # noqa: E402

ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "scopedbinding_latest.json"
DATED_PREFIX = "SCOPEDBINDING"
DATE_STAMP = "2026-11-07"
CARD = "E510-WHICH-OF-THE-42-AMBIGUOUS-RESIDUALS-BECOME-SINGLE-ORIGIN-WHEN-THE-BINDING-TABLE-IS-SCOPED"
STUDY = "E510_binding_scope"
UPSTREAM_FACE = os.path.join("results", "state_tilt", "UNRESOLVEDORIGIN-2026-11-07.json")
POPULATION_SOURCE = ("results/state_tilt/UNRESOLVEDORIGIN-2026-11-07.json rows with "
                     "tracks=mixed")
SELF_EXCLUDED = ("e510_", "run_e510", "_e510")

# ---------------------------------------------------------------- vocabulary
T_CLOCK, T_DATA, T_MIXED = e507.T_CLOCK, e507.T_DATA, e507.T_MIXED
T_NEITHER, T_UNKNOWN = e507.T_NEITHER, e507.T_UNKNOWN
TRACK_VOCAB = (T_CLOCK, T_DATA, T_MIXED, T_NEITHER, T_UNKNOWN)

R_CALLER, R_UNREADABLE = e507.R_CALLER, e507.R_UNREADABLE

TABLE_WIDE = "module_wide_every_assignment_in_the_module_can_reach_every_site"
TABLE_SCOPED = "scoped_nearest_enclosing_function_first_then_the_module"
TABLE_VOCAB = (TABLE_WIDE, TABLE_SCOPED)

K_SINGLE = "collapsed_to_a_single_origin_the_enclosing_scope_names_one_day"
K_CALLER = "collapsed_to_caller_supplied_the_symbol_is_a_parameter_of_the_enclosing_function"
K_NOT_DATE = "collapsed_to_not_a_date_the_enclosing_scope_binds_no_day_at_all"
K_MIXED = "stays_ambiguous_the_enclosing_scope_itself_holds_more_than_one_origin"
K_NO_BINDING = "became_unreadable_the_enclosing_scope_holds_no_binding_at_all"
K_OPERAND = "stays_unreadable_the_symbol_binds_in_scope_but_its_operand_binds_elsewhere"
COLLAPSE_VOCAB = (K_SINGLE, K_CALLER, K_NOT_DATE, K_MIXED, K_NO_BINDING, K_OPERAND)
NEEDS_FALLBACK = (K_NO_BINDING, K_OPERAND)
COLLAPSED = (K_SINGLE, K_CALLER, K_NOT_DATE)

V_SCOPE = ("the_scope_collapses_every_ambiguous_pair_so_the_bucket_was_the_resolvers")
V_MIXED = ("the_scope_collapses_part_of_the_bucket_and_the_rest_is_real_symbol_reuse")
V_CODE = "the_scope_changes_nothing_so_the_ambiguity_lives_in_the_code"
V_LOSS = "the_scoped_table_reads_less_than_the_module_wide_one_so_it_cannot_be_adopted_alone"
V_EMPTY = "no_pair_carries_an_ambiguous_symbol_at_all"
VERDICT_VOCAB = (V_SCOPE, V_MIXED, V_CODE, V_LOSS, V_EMPTY)

NESTED = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)
SYMBOL_RE = re.compile(r"^\s*([A-Za-z_]\w*)")

# ------------------------------------------------------------- scoped table
def _scope_statements(scope):
    if isinstance(scope, ast.Module):
        return list(scope.body)
    if isinstance(scope, ast.Lambda):
        return [scope.body]
    return list(scope.body)


def _scope_assigns(scope):
    """Assignments written directly in this scope; nested scopes excluded."""
    kept = []

    def rec(node):
        if isinstance(node, NESTED):
            return
        kept.append(node)
        for child in ast.iter_child_nodes(node):
            rec(child)

    for stmt in _scope_statements(scope):
        rec(stmt)
    return base.module_assigns(ast.Module(body=kept, type_ignores=[]))[0]


def _scope_params(scope):
    if not isinstance(scope, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
        return set()
    a = scope.args
    names = {x.arg for x in list(a.args) + list(a.kwonlyargs) + list(a.posonlyargs)}
    if a.vararg:
        names.add(a.vararg.arg)
    if a.kwarg:
        names.add(a.kwarg.arg)
    return names


def scope_chain(tree, line):
    """Scopes containing a 1-based line, innermost first, the module last."""
    spans = []
    for node in ast.walk(tree):
        if isinstance(node, NESTED):
            end = getattr(node, "end_lineno", None) or 10 ** 9
            if node.lineno <= line <= end:
                spans.append(node)
    spans.sort(key=lambda n: -(getattr(n, "end_lineno", 10 ** 9) - n.lineno))
    return spans + [tree]


def scoped_ctx(ctx, site_line):
    """The module-wide context with ``assigns``/``params`` restricted to the site's scopes."""
    tree = ctx["tree"]
    chain = scope_chain(tree, site_line)
    assigns, params = {}, set()
    for scope in chain:                 # innermost first: the nearest writer wins
        for name, rhs in _scope_assigns(scope).items():
            if name not in assigns:
                assigns[name] = list(rhs)
        if not params:
            params = _scope_params(scope)
    label = ""
    for scope in chain:
        if isinstance(scope, (ast.FunctionDef, ast.AsyncFunctionDef)):
            label = scope.name
            break
    kinds = [type(s).__name__ for s in chain]
    return dict(ctx, assigns=assigns, params=params), label, kinds


def _symbol_of(expr):
    m = SYMBOL_RE.match(expr or "")
    return m.group(1) if m else ""


def resolve_arm(ctx, expr, root, hist, narrow=None):
    """Resolve one expression under one table.  The cache is keyed without the table,
    so it is cleared per call: a stale entry would answer for the wrong scope."""
    try:
        node = ast.parse(expr, mode="eval").body
    except SyntaxError:
        return {"class": R_UNREADABLE, "tracks": T_UNKNOWN, "binding": "",
                "expression": "", "chain": ["expression_unparseable"]}
    e507._RES_CACHE.clear()
    got = e507._res_uncached(node, ctx, root, hist)
    return {"class": got["class"], "tracks": got["tracks"], "binding": got["binding"],
            "expression": (got.get("resolved_expression") or "")[:160],
            "chain": got["chain"][:10]}


def collapse_class(wide, narrow):
    """What the scoped read did to a pair the module-wide read called ambiguous."""
    if narrow["class"] == R_CALLER:
        return K_CALLER
    if narrow["tracks"] in (T_CLOCK, T_DATA):
        return K_SINGLE
    if narrow["tracks"] == T_MIXED:
        return K_MIXED
    if narrow["tracks"] == T_NEITHER:
        return K_NOT_DATE
    if narrow.get("class") == R_UNREADABLE:
        return K_NO_BINDING
    return K_OPERAND


def analyse(root=None, upstream=None):
    root = root or ROOT
    up = upstream if upstream is not None else base._load_json(os.path.join(root, UPSTREAM_FACE))
    hist = {"ok": False, "note": "the history arm is E507's; this study reads the tree only"}
    sites = {s["site"]: s for s in (up.get("sites") or [])}
    mixed = [r for r in (up.get("rows") or []) if r.get("tracks") == T_MIXED]

    pairs, by_key, rows = [], {}, []
    print("analyse: %d ambiguous pairs" % len(mixed), flush=True)
    for row in mixed:
        site = sites.get(row.get("site")) or {}
        source = row.get("source") or site.get("source") or ""
        line = row.get("line") or site.get("line") or 0
        expr = row.get("date_expression") or site.get("date_expression") or ""
        key = (source, expr, line)
        if key not in by_key:
            ctx = e507.ctx_of(root, source)
            rec = {"source": source, "line": line, "date_expression": expr,
                   "symbol": _symbol_of(expr), "scope": "", "scope_chain": [],
                   "tables": TABLE_VOCAB}
            if ctx is None:
                rec["wide"] = {"class": R_UNREADABLE, "tracks": T_UNKNOWN, "binding": "",
                               "expression": "", "chain": ["source_unparseable"]}
                rec["scoped"] = dict(rec["wide"])
                rec["collapse"] = K_NO_BINDING
            else:
                wide = resolve_arm(ctx, expr, root, hist)
                sctx, scope, kinds = scoped_ctx(ctx, line)
                narrow = resolve_arm(sctx, expr, root, hist, narrow=True)
                wide_nodes = ctx["assigns"].get(_symbol_of(expr), [])
                kept_ids = {id(n) for n in sctx["assigns"].get(_symbol_of(expr), [])}
                dropped = ["%s:%d" % (source, n.lineno) for n in wide_nodes
                           if id(n) not in kept_ids]
                rec.update({"wide": wide, "scoped": narrow, "scope": scope,
                            "scope_chain": kinds, "collapse": collapse_class(wide, narrow),
                            "bindings": {"symbol": _symbol_of(expr),
                                         "wide_assignments": len(wide_nodes),
                                         "scoped_assignments": len(
                                             sctx["assigns"].get(_symbol_of(expr), [])),
                                         "dropped_locations": sorted(set(dropped))[:6]}})
            by_key[key] = rec
            pairs.append(rec)
            print("analyse: %-40s %-24s scope=%-14s -> %s"
                  % (source[-40:], expr[:24], rec["scope"], rec["collapse"][:26]), flush=True)
        rows.append({"path": row.get("path"), "site": row.get("site"), "source": source,
                     "line": line, "date_expression": expr,
                     "symbol": _symbol_of(expr),
                     "upstream_chain": (row.get("symbol_chain") or [])[:6],
                     "collapse": by_key[key]["collapse"],
                     "wide_tracks": by_key[key]["wide"]["tracks"],
                     "scoped_tracks": by_key[key]["scoped"]["tracks"]})
    return {"pairs": pairs, "rows": rows, "upstream": up,
            "summary": _summary(pairs, rows)}


def _count(records, key, vocab):
    out = {k: 0 for k in vocab}
    for rec in records:
        if rec.get(key) in out:
            out[rec[key]] += 1
    return out


def _summary(pairs, rows):
    collapse = _count(pairs, "collapse", COLLAPSE_VOCAB)
    wide_tracks = {"%s" % k: 0 for k in TRACK_VOCAB}
    scoped_tracks = {"%s" % k: 0 for k in TRACK_VOCAB}
    for rec in pairs:
        wide_tracks[rec["wide"]["tracks"]] = wide_tracks.get(rec["wide"]["tracks"], 0) + 1
        scoped_tracks[rec["scoped"]["tracks"]] = scoped_tracks.get(
            rec["scoped"]["tracks"], 0) + 1
    dropped = sum(len(rec.get("bindings", {}).get("dropped_locations") or []) for rec in pairs)
    return {
        "evidence_cutoff": DATE_STAMP,
        "residual_pairs": len(rows),
        "pair_sites": len(pairs),
        "members_touched": len({r["path"] for r in rows}),
        "sources_touched": len({r["source"] for r in rows}),
        "symbols_touched": len({r["symbol"] for r in pairs if r["symbol"]}),
        "pairs_by_collapse": collapse,
        "collapsed_pairs": sum(collapse[k] for k in COLLAPSED),
        "stays_ambiguous_pairs": collapse[K_MIXED],
        "became_unreadable_pairs": collapse[K_NO_BINDING],
        "operand_out_of_scope_pairs": collapse[K_OPERAND],
        "pairs_needing_a_module_wide_fallback": sum(collapse[k] for k in NEEDS_FALLBACK),
        "wide_tracks_by_pair": wide_tracks,
        "scoped_tracks_by_pair": scoped_tracks,
        "dropped_binding_locations": dropped,
        "pairs_carrying_a_dropped_binding": sum(
            1 for rec in pairs if rec.get("bindings", {}).get("dropped_locations")),
    }


def _verdict(summary):
    if not summary["pair_sites"]:
        return V_EMPTY
    if sum(summary["pairs_by_collapse"][k] for k in NEEDS_FALLBACK) > summary["collapsed_pairs"]:
        return V_LOSS
    if summary["stays_ambiguous_pairs"] == 0:
        return V_SCOPE
    if summary["collapsed_pairs"] == 0:
        return V_CODE
    return V_MIXED


def _answers(summary):
    return {
        "how_many_ambiguous_pairs_did_e507_publish": summary["residual_pairs"],
        "how_many_distinct_pair_sites_are_behind_them": summary["pair_sites"],
        "how_many_collapse_to_a_single_origin": summary["pairs_by_collapse"][K_SINGLE],
        "how_many_collapse_to_caller_supplied": summary["pairs_by_collapse"][K_CALLER],
        "how_many_stay_ambiguous": summary["stays_ambiguous_pairs"],
        "how_many_become_unreadable": summary["became_unreadable_pairs"],
        "how_many_stay_unreadable_because_an_operand_binds_elsewhere":
            summary["operand_out_of_scope_pairs"],
        "how_many_pairs_need_the_module_wide_fallback":
            summary["pairs_needing_a_module_wide_fallback"],
        "how_many_binding_locations_the_scope_drops": summary["dropped_binding_locations"],
        "which_table_is_the_reading": TABLE_SCOPED,
    }


def build(root=None, write=True, upstream=None):
    root = root or ROOT
    got = analyse(root, upstream=upstream)
    summary = got["summary"]
    face = {
        "study": STUDY,
        "card": CARD,
        "title": ("Re-read E507's 42 ambiguous pairs with a scoped binding table: which of "
                  "them become single-origin, and which are a real reuse of one symbol?"),
        "evidence_cutoff": DATE_STAMP,
        "generated": e507._now(),
        "population_source": POPULATION_SOURCE,
        "table_vocab": list(TABLE_VOCAB),
        "collapse_vocab": list(COLLAPSE_VOCAB),
        "tracks_vocab": list(TRACK_VOCAB),
        "verdict_vocab": list(VERDICT_VOCAB),
        "method_limits": [
            "the population is E507's own published face; a pair appears here because that "
            "face called it ambiguous, not because this study re-read the upstream rows",
            "the scoped table resolves a name to the nearest enclosing scope that binds it, "
            "then the module; it is not a dataflow analysis, so a name rebound later in the "
            "same scope still contributes every assignment to that scope",
            "comprehension targets are shadowed (E507 already did this) and a lambda body is "
            "treated as its own scope",
            "a symbol that the enclosing scope does not bind and that is a parameter of the "
            "enclosing function is published as caller-supplied, never folded into clock/data",
            "the resolver cache is keyed without the table in key, so it is cleared per arm; "
            "a shared cache would answer one table with the other table's result",
            "only the tree is read: the git-history arm of E507 is not replayed here, so a "
            "pair whose only binding was historical is out of this study's reach",
        ],
        "summary": summary,
        "verdict": _verdict(summary),
        "answers": _answers(summary),
        "pairs": got["pairs"],
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
def summary_problems(summary, pairs, rows):
    problems = []
    if summary.get("residual_pairs") != len(rows):
        problems.append("residual_pairs=%r is not the row count %d"
                        % (summary.get("residual_pairs"), len(rows)))
    if summary.get("pair_sites") != len(pairs):
        problems.append("pair_sites is not the pair count")
    counts = _count(pairs, "collapse", COLLAPSE_VOCAB)
    if summary.get("pairs_by_collapse") != counts:
        problems.append("pairs_by_collapse does not re-derive from the pairs")
    if summary.get("collapsed_pairs") != sum(counts[k] for k in COLLAPSED):
        problems.append("collapsed_pairs is not the collapsed class count")
    if summary.get("stays_ambiguous_pairs") != counts[K_MIXED]:
        problems.append("stays_ambiguous_pairs is not the mixed class count")
    if summary.get("became_unreadable_pairs") != counts[K_NO_BINDING]:
        problems.append("became_unreadable_pairs is not the no-binding class count")
    if summary.get("operand_out_of_scope_pairs") != counts[K_OPERAND]:
        problems.append("operand_out_of_scope_pairs is not the operand class count")
    if summary.get("pairs_needing_a_module_wide_fallback") != sum(counts[k]
                                                                 for k in NEEDS_FALLBACK):
        problems.append("pairs_needing_a_module_wide_fallback is not the fallback class count")
    wide = {k: 0 for k in TRACK_VOCAB}
    scoped = {k: 0 for k in TRACK_VOCAB}
    for rec in pairs:
        wide[rec["wide"]["tracks"]] = wide.get(rec["wide"]["tracks"], 0) + 1
        scoped[rec["scoped"]["tracks"]] = scoped.get(rec["scoped"]["tracks"], 0) + 1
    if summary.get("wide_tracks_by_pair") != wide:
        problems.append("wide_tracks_by_pair does not re-derive")
    if summary.get("scoped_tracks_by_pair") != scoped:
        problems.append("scoped_tracks_by_pair does not re-derive")
    if summary.get("members_touched") != len({r["path"] for r in rows}):
        problems.append("members_touched is not the distinct member count")
    if summary.get("sources_touched") != len({r["source"] for r in rows}):
        problems.append("sources_touched is not the distinct source count")
    return problems


def row_problems(face):
    pairs = face.get("pairs") or []
    rows = face.get("rows") or []
    summary = face.get("summary") or {}
    problems = summary_problems(summary, pairs, rows)
    by_source = {(p["source"], p["date_expression"], p["line"]): p for p in pairs}
    for rec in pairs:
        if rec.get("collapse") not in COLLAPSE_VOCAB:
            problems.append("%s:%r: collapse outside the vocabulary"
                            % (rec.get("source"), rec.get("date_expression")))
        if rec.get("collapse") != collapse_class(rec.get("wide") or {}, rec.get("scoped") or {}):
            problems.append("%s:%r: collapse does not re-derive from its two arms"
                            % (rec.get("source"), rec.get("date_expression")))
        if not rec.get("date_expression"):
            problems.append("%s: pair publishes no expression" % (rec.get("source"),))
        for arm in ("wide", "scoped"):
            if (rec.get(arm) or {}).get("tracks") not in TRACK_VOCAB:
                problems.append("%s:%r: %s tracks outside the vocabulary"
                                % (rec.get("source"), rec.get("date_expression"), arm))
    for row in rows:
        if row.get("collapse") not in COLLAPSE_VOCAB:
            problems.append("%s/%s: row collapse outside the vocabulary"
                            % (row.get("path"), row.get("site")))
        key = (row.get("source"), row.get("date_expression"), row.get("line"))
        if key in by_source and by_source[key]["collapse"] != row.get("collapse"):
            problems.append("%s/%s: row disagrees with its pair site"
                            % (row.get("path"), row.get("site")))
        if not row.get("site"):
            problems.append("%s: row names no site" % (row.get("path"),))
    if face.get("verdict") != _verdict(summary):
        problems.append("verdict=%r does not re-derive from the summary (%r)"
                        % (face.get("verdict"), _verdict(summary)))
    if (face.get("answers") or {}).get("how_many_ambiguous_pairs_did_e507_publish") != \
            summary.get("residual_pairs"):
        problems.append("answers.how_many_ambiguous_pairs_did_e507_publish is not the row count")
    return problems


def check(face=None, root=None):
    root = root or ROOT
    face = face or base._load_json(os.path.join(root, "results", "state_tilt", FACE_NAME))
    problems = row_problems(face)
    print("check problems=%r" % (problems,))
    return 0 if not problems else 1


def verify(root=None):
    root = root or ROOT
    face = build(root, write=False)
    problems = row_problems(face)
    print("verify problems=%r" % (problems,))
    print("verdict=%s" % face["verdict"])
    print("summary=%s" % json.dumps(face["summary"], ensure_ascii=False, sort_keys=True))
    return 0 if not problems else 1


# ------------------------------------------------------------------ selftest
# delta: the same name bound with a formatted literal in a test function and with loaded
# data in the site's own function -- the module-wide table calls that mixed, the scope
# knows which one the site can see.
DELTA = '''import json


def _load(path):
    return json.load(open(path, encoding="utf-8"))


def _selftest():
    cal = ["2020-01-%02d" % d for d in range(1, 3)]
    return "FIX-%s.json" % cal[-1]


def build():
    cal = _load("data/bench.json")[-1][0]
    return "OUT-%s.json" % cal
'''

# theta: the site's symbol is a parameter of the enclosing function, while two other
# functions bind the same name to a day -- module-wide reads "mixed", the scope reads
# "the caller decides".
THETA = '''import json


def _load(path):
    return json.load(open(path, encoding="utf-8"))


def render(ticket, asof):
    return "ORDER-%s.md" % asof


def run():
    asof = _load("data/bench.json")[-1][0]
    return render(1, asof)


def _selftest():
    asof = {"bar": "2020-01-%02d" % 1}
    return "CARD-%s.md" % asof
'''

# iota: both assignments reachable from the site live in the site's own function, so the
# scope cannot separate them -- this is what a real reuse of one name looks like.
IOTA = '''import json


def _load(path):
    return json.load(open(path, encoding="utf-8"))


def build(face):
    cutoff = _load("data/bench.json")[-1][0]
    if face:
        cutoff = "%s-01-%02d" % (face, 1)
    return "SLICE-%s.json" % cutoff
'''

UPSILON = '''import json


def _load(path):
    return json.load(open(path, encoding="utf-8"))


def run():
    stamp = _load("data/bench.json")[-1][0]
    return _emit(stamp)


def _emit(stamp):
    return "???"
'''


PHI = '''import json


def _compose():
    cutoff = str(idx[-1].date())
    return "SS-%s.json" % cutoff


def run():
    idx = json.load(open("data/bench.json", encoding="utf-8"))
    return _compose()
'''


def _fixture_upstream():
    def site(sid, source, line, expr):
        return {"site": sid, "source": source, "line": line, "expression": expr,
                "date_expression": expr, "origin": "unresolved"}

    sites = [
        site("S0001", "scripts/delta.py", 15, "cal[-1]"),
        site("S0002", "scripts/theta.py", 9, "asof"),
        site("S0003", "scripts/iota.py", 12, "cutoff"),
        site("S0004", "scripts/upsilon.py", 13, "stamp"),
        site("S0005", "scripts/phi.py", 5, "cutoff"),
    ]
    rows = []
    for s, members in ((sites[0], ["results/OUT-2020-01-02.json"]),
                       (sites[1], ["results/ORDER-2020-01-02.md"]),
                       (sites[2], ["results/SLICE-2020-01-02.json"]),
                       (sites[3], ["results/NOPE-2020-01-02.json"]),
                       (sites[4], ["results/SS-2020-01-02.json"])):
        for path in members:
            rows.append({"path": path, "site": s["site"], "tracks": T_MIXED,
                         "date_expression": s["date_expression"], "symbol_chain": []})
    return {"sites": sites, "rows": rows, "summary": {"site_member_pairs": len(rows)}}


def selftest():
    checks, failures = 0, []

    def ok(name, cond, detail=None):
        nonlocal checks
        checks += 1
        if not cond:
            failures.append("%s (%r)" % (name, detail))

    import shutil
    import tempfile
    tmp = tempfile.mkdtemp(prefix="e510_selftest_")
    try:
        os.makedirs(os.path.join(tmp, "scripts"))
        for name, body in (("delta.py", DELTA), ("theta.py", THETA), ("iota.py", IOTA),
                           ("upsilon.py", UPSILON), ("phi.py", PHI)):
            with io.open(os.path.join(tmp, "scripts", name), "w", encoding="utf-8",
                         newline="\n") as fh:
                fh.write(body)
        up = _fixture_upstream()
        face = build(root=tmp, write=False, upstream=up)
        by_source = {p["source"]: p for p in face["pairs"]}

        delta = by_source.get("scripts/delta.py") or {}
        ok("a literal bound in a test function is not reachable from the site",
           delta.get("collapse") == K_SINGLE, delta.get("collapse"))
        ok("that pair reads as data under the scope",
           (delta.get("scoped") or {}).get("tracks") == T_DATA, delta.get("scoped"))
        ok("the module-wide arm still calls it ambiguous",
           (delta.get("wide") or {}).get("tracks") == T_MIXED, delta.get("wide"))
        ok("the dropped binding is published as a location",
           any("delta.py" in loc for loc in
               (delta.get("bindings") or {}).get("dropped_locations") or []),
           delta.get("bindings"))

        theta = by_source.get("scripts/theta.py") or {}
        ok("a parameter of the enclosing function is caller-supplied",
           theta.get("collapse") == K_CALLER, theta.get("collapse"))
        ok("a caller-supplied symbol is not folded into data",
           (theta.get("scoped") or {}).get("tracks") == T_UNKNOWN, theta.get("scoped"))

        iota = by_source.get("scripts/iota.py") or {}
        ok("two writers inside the site's own scope stay ambiguous",
           iota.get("collapse") == K_MIXED, iota.get("collapse"))
        ok("a scope that drops nothing is published as dropping nothing",
           not ((iota.get("bindings") or {}).get("dropped_locations")), iota.get("bindings"))

        upsilon = by_source.get("scripts/upsilon.py") or {}
        ok("a symbol the scope never binds reads as caller-supplied or unreadable",
           upsilon.get("collapse") in (K_CALLER, K_NO_BINDING), upsilon.get("collapse"))
        phi = by_source.get("scripts/phi.py") or {}
        ok("a symbol whose binding sits in scope but whose operand binds elsewhere is "
           "labelled, not folded",
           phi.get("collapse") == K_OPERAND, phi.get("collapse"))

        sites = {p["source"]: p for p in face["pairs"]}
        ok("the scope label names the enclosing function",
           sites["scripts/delta.py"]["scope"] == "build",
           sites["scripts/delta.py"]["scope"])
        ok("the scope chain starts at the function and ends at the module",
           sites["scripts/delta.py"]["scope_chain"][-1] == "Module",
           sites["scripts/delta.py"]["scope_chain"])
        ok("every upstream row keeps a record", len(face["rows"]) == 5, len(face["rows"]))
        ok("the fixture verdict collapses part of the bucket",
           face["verdict"] == V_MIXED, face["verdict"])
        ok("gate passes on the built fixture", row_problems(face) == [], row_problems(face))

        doctored = json.loads(json.dumps(face))
        doctored["pairs"][0]["collapse"] = K_MIXED
        ok("gate refuses a collapse the two arms contradict", row_problems(doctored) != [])
        doctored2 = json.loads(json.dumps(face))
        doctored2["summary"]["stays_ambiguous_pairs"] += 1
        ok("gate refuses a hand-written mixed count", row_problems(doctored2) != [])
        doctored3 = json.loads(json.dumps(face))
        doctored3["verdict"] = V_SCOPE
        ok("gate refuses a hand-written verdict", row_problems(doctored3) != [])
        doctored4 = json.loads(json.dumps(face))
        doctored4["summary"]["wide_tracks_by_pair"] = {k: 0 for k in TRACK_VOCAB}
        ok("gate refuses track counts the pairs contradict", row_problems(doctored4) != [])
        doctored5 = json.loads(json.dumps(face))
        doctored5["pairs"][0]["scoped"]["tracks"] = "guessed"
        ok("gate refuses a track outside the vocabulary", row_problems(doctored5) != [])
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