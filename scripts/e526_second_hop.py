"""E526 -- what happens at the second hop of the arguments that are forwarded again?

E520 (results/state_tilt/forwardedarg_latest.json) followed E519's non-answers one hop and found
that 12 of the 20 values handed to a forwarded parameter are *again* a parameter or a local one
level up.  It published that as one count -- ``arguments_forwarded_again`` -- which says the chain
did not end at that call site but says nothing about where it does end.

This study opens each of those 12 parcels and publishes, per parcel:

  * the hop-1 call site that forwards (which module and line hands the value on, and whether the
    forwarded name was a parameter of the caller or a local of it)
  * the second hop: for a forwarded *parameter*, every call site of the function that owns that
    parameter and what each one hands over; for a forwarded *local*, the statement inside the
    caller that binds the name and what it binds it from
  * an arrival class that keeps the two answers apart -- ``resolved_at_the_second_hop`` (the value
    is written, computed, called or read right there) versus
    ``forwarded_again_at_the_second_hop`` (the chain continues) -- instead of folding them into a
    single ``mixed`` bucket

Everything is re-derived from the cited source at ``check``/``verify`` time; the upstream row count
is asserted against E520's own summary so the two faces cannot drift.  The corpus, the argument
classifier and the parameter tracer are imported from E520 rather than cloned.

    python scripts/e526_second_hop.py run        # build + write the face
    python scripts/e526_second_hop.py check      # gate the published face (fast)
    python scripts/e526_second_hop.py verify     # re-derive from the tree and gate
    python scripts/e526_second_hop.py selftest   # fixture corpus + doctored faces
"""
from __future__ import annotations

import ast
import hashlib
import io
import json
import os
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e520_forwarded_argument as e520  # noqa: E402  (reuse the corpus, do not clone)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")

CARD = "E526-WHAT-HAPPENS-AT-THE-SECOND-HOP-OF-THE-12-ARGUMENTS-THAT-ARE-FORWARDED-AGAIN"
STUDY = "E526_second_hop"
DATE_STAMP = "2026-11-08"
FACE_NAME = "secondhop_latest.json"
DATED_PREFIX = "SECONDHOP"

SELF_EXCLUDED = ("e526_", "run_e526", "_e526", "SECONDHOP", "secondhop_")

UPSTREAM_FACE = os.path.join("results", "state_tilt", "FORWARDEDARG-2026-11-08.json")
UPSTREAM_STUDY = e520.STUDY

# ---------------------------------------------------------------- hop-1 vocabulary
H_PARAMETER = e520.A_PARAMETER_AGAIN
H_LOCAL = e520.A_LOCAL_AGAIN
HOP1_VOCAB = (H_PARAMETER, H_LOCAL)

# ---------------------------------------------------------------- hop-2 style
S_CALL_SITE = "a_call_site_of_the_function_that_owns_the_parameter"
S_BINDING = "the_statement_inside_the_caller_that_binds_the_local"
S_NO_BINDING = "no_binding_anywhere_inside_the_caller"
STYLE_VOCAB = (S_CALL_SITE, S_BINDING, S_NO_BINDING)

# ---------------------------------------------------------------- arrival vocabulary
R_RESOLVED = "resolved_at_the_second_hop"
R_FORWARDED = "forwarded_again_at_the_second_hop"
R_MIXED = "mixed_resolved_and_forwarded"
R_DEFAULT = "left_at_the_default_at_the_second_hop"
R_NEVER = "no_supplying_site_in_this_tree"
ARRIVAL_VOCAB = (R_RESOLVED, R_FORWARDED, R_MIXED, R_DEFAULT, R_NEVER)

# a value that is produced, computed, called or read at the second hop ends there
RESOLVED = tuple(e520.SUPPLIED) + (e520.A_CALL, e520.A_READ, e520.A_COMPUTED)

# ---------------------------------------------------------------- verdict vocabulary
V_RESOLVED = "every_second_hop_resolves_to_a_value_that_is_not_forwarded_again"
V_FORWARDED = "the_chain_continues_past_the_second_hop"
V_UNSETTLED = ("some_second_hop_never_reaches_a_supplying_site_so_the_population_stays_"
               "unmeasured")
V_EMPTY = "no_forwarded_argument_in_the_upstream_face"
VERDICT_VOCAB = (V_RESOLVED, V_FORWARDED, V_UNSETTLED, V_EMPTY)


def _now():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def _sha256_file(path):
    h = hashlib.sha256()
    with io.open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _is_self(rel):
    name = os.path.basename(rel or "")
    return name.startswith(SELF_EXCLUDED)


# ------------------------------------------------------------------ upstream population
def load_upstream(root=None):
    path = os.path.join(root or ROOT, UPSTREAM_FACE)
    with io.open(path, encoding="utf-8") as fh:
        face = json.load(fh)
    return face, _sha256_file(path)


def population(face):
    """Every E520 call site whose argument is again a parameter or a local one level up."""
    parcels = []
    seen = {}
    for row in face.get("rows") or []:
        if row.get("question") != "who_supplies_this_parameter":
            continue
        for site in row.get("call_sites") or []:
            kind = site.get("argument_kind")
            if kind not in HOP1_VOCAB:
                continue
            key = (site.get("caller_module"), site.get("line"), site.get("argument"),
                   kind)
            if key in seen:
                seen[key]["rows_that_share_this_parcel"] += 1
                continue
            item = {
                "module": row.get("module"),
                "function": row.get("function"),
                "local": row.get("local"),
                "source": row.get("source"),
                "def_line": row.get("line"),
                "hop1_kind": kind,
                "site_module": site.get("caller_module"),
                "site_line": site.get("line"),
                "site_argument": site.get("argument"),
                "site_ownership": site.get("ownership"),
                "rows_that_share_this_parcel": 1,
            }
            seen[key] = item
            parcels.append(item)
    parcels.sort(key=lambda r: (r["site_module"] or "", r["site_line"] or 0,
                               r["site_argument"] or "", r["function"] or ""))
    return parcels


# ------------------------------------------------------------------ second hop
def _enclosing_function(corpus, module, line):
    holder = corpus.enclosing(module, line or 0)
    return holder.get("func") if holder else None


def _binding_sites(module, funcname, name, before_line, corpus):
    """Statements inside ``funcname`` that bind ``name``, with what each binds it from."""
    funcdef = corpus.signature(module, funcname)
    if funcdef is None:
        return None
    sites = []
    for node in ast.walk(funcdef):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node is not funcdef:
            continue  # a nested function binds its own names
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if e520._binds_target(target, name):
                    sites.append({"line": node.lineno, "from": node.value,
                                  "how": "an_assignment_inside_the_caller"})
        elif isinstance(node, (ast.For, ast.AsyncFor)):
            if e520._binds_target(node.target, name):
                sites.append({"line": node.lineno, "from": node.iter,
                              "how": "a_loop_target_fed_by_the_iterated_expression"})
        elif isinstance(node, ast.withitem):
            if node.optional_vars is not None and \
                    e520._binds_target(node.optional_vars, name):
                sites.append({"line": getattr(node, "lineno", None) or 0,
                              "from": node.context_expr,
                              "how": "a_with_target_fed_by_the_context_expression"})
        elif isinstance(node, ast.NamedExpr):
            if isinstance(node.target, ast.Name) and node.target.id == name:
                sites.append({"line": node.lineno, "from": node.value,
                              "how": "an_assignment_expression"})
    sites.sort(key=lambda s: (s["line"] or 0))
    return [s for s in sites if not before_line or (s["line"] or 0) <= (before_line or 0)] \
        or sites


def hop_of_parcel(parcel, corpus):
    """The second hop of one forwarded parcel, as a list of measured hand-overs."""
    site_module = parcel["site_module"]
    name = parcel["site_argument"]
    if parcel["hop1_kind"] == H_PARAMETER:
        funcname = _enclosing_function(corpus, site_module, parcel["site_line"])
        if funcname is None:
            return {"style": S_NO_BINDING, "sites": [], "note":
                    "the enclosing function of the forwarding call site is not resolvable"}
        traced = e520._trace_parameter(
            {"site_module": site_module, "function": funcname, "local": name}, corpus)
        sites = [dict(site, hop_function=funcname) for site in traced["call_sites"]]
        return {"style": S_CALL_SITE, "sites": sites, "note": traced["note"]}

    funcname = _enclosing_function(corpus, site_module, parcel["site_line"])
    if funcname is None:
        return {"style": S_NO_BINDING, "sites": [], "note":
                "the enclosing function of the forwarding call site is not resolvable"}
    binds = _binding_sites(site_module, funcname, name, parcel["site_line"], corpus)
    if not binds:
        return {"style": S_NO_BINDING, "sites": [], "note":
                "the local is bound nowhere inside the function that forwards it"}
    sites = []
    for bind in binds:
        sites.append({
            "caller_module": site_module,
            "line": bind["line"],
            "ownership": None,
            "argument": e520._short(bind["from"]),
            "argument_kind": e520._classify_argument(bind["from"], site_module, corpus),
            "hop_function": funcname,
            "bound_how": bind["how"],
        })
    return {"style": S_BINDING, "sites": sites, "note": None}


def _arrival(kinds):
    if not kinds:
        return R_NEVER
    unique = set(kinds)
    if unique == {e520.A_NO_CALL_SITE}:
        return R_NEVER
    if unique <= set(RESOLVED):
        return R_RESOLVED
    if unique <= set(e520.FORWARDED_AGAIN):
        return R_FORWARDED
    if unique == {e520.A_DEFAULT}:
        return R_DEFAULT
    return R_MIXED


def analyse_parcel(parcel, corpus):
    rec = dict(parcel)
    hop = hop_of_parcel(parcel, corpus)
    rec["hop_style"] = hop["style"]
    rec["hop_sites"] = hop["sites"]
    rec["hop_site_count"] = len(hop["sites"])
    rec["note"] = hop["note"]
    counts = {}
    for site in hop["sites"]:
        kind = site.get("argument_kind")
        counts[kind] = counts.get(kind, 0) + 1
    rec["second_hop_kind_counts"] = counts
    rec["arrival"] = _arrival([s.get("argument_kind") for s in hop["sites"]])
    return rec


# ------------------------------------------------------------------ summary / verdict
def _count(rows, key, vocab):
    out = dict((v, 0) for v in vocab)
    for rec in rows:
        value = rec.get(key)
        out[value] = out.get(value, 0) + 1
    return out


def _summary(rows, sources, upstream=None):
    kinds = dict((v, 0) for v in e520.ARGUMENT_VOCAB)
    hop2_sites = 0
    for rec in rows:
        for kind, n in (rec.get("second_hop_kind_counts") or {}).items():
            kinds[kind] = kinds.get(kind, 0) + n
            hop2_sites += n
    by_hop1 = _count(rows, "hop1_kind", HOP1_VOCAB)
    arrivals = _count(rows, "arrival", ARRIVAL_VOCAB)
    styles = _count(rows, "hop_style", STYLE_VOCAB)
    return {
        "parcels_examined": len(rows),
        "sources_read": sources,
        "upstream_arguments_forwarded_again": (upstream or {}).get(
            "arguments_forwarded_again"),
        "parcels_by_hop1_kind": by_hop1,
        "parcels_by_hop_style": styles,
        "parcels_by_arrival": arrivals,
        "second_hop_sites": hop2_sites,
        "second_hop_kind_counts": kinds,
        "second_hop_values_resolved_there": sum(kinds.get(k, 0) for k in RESOLVED),
        "second_hop_values_forwarded_again": sum(kinds.get(k, 0)
                                                 for k in e520.FORWARDED_AGAIN),
        "second_hop_values_at_the_default": kinds.get(e520.A_DEFAULT, 0),
        "parcels_resolved_at_the_second_hop": arrivals.get(R_RESOLVED, 0),
        "parcels_forwarded_again_at_the_second_hop": arrivals.get(R_FORWARDED, 0),
        "parcels_mixed_at_the_second_hop": arrivals.get(R_MIXED, 0),
        "parcels_left_at_the_default": arrivals.get(R_DEFAULT, 0),
        "parcels_with_no_supplying_site": arrivals.get(R_NEVER, 0),
        "distinct_supplying_modules": sorted({
            s.get("caller_module") for r in rows for s in r.get("hop_sites") or []
            if s.get("caller_module") and s.get("argument_kind") in RESOLVED}),
    }


def _verdict(summary):
    if not summary["parcels_examined"]:
        return V_EMPTY
    if summary["parcels_forwarded_again_at_the_second_hop"]:
        return V_FORWARDED
    if summary["parcels_with_no_supplying_site"]:
        return V_UNSETTLED
    return V_RESOLVED


# ------------------------------------------------------------------ build / gate
def corpus_files(root=None):
    root = root or ROOT
    seen = set()
    for sub in ("scripts", "Tools", "firm", "live", "monitor"):
        base = os.path.join(root, sub)
        for dirpath, _dirs, files in os.walk(base):
            for name in files:
                if name.endswith(".py") and not _is_self(name):
                    seen.add(os.path.relpath(os.path.join(dirpath, name), root))
    return sorted(seen)


def build(root=None, write=True, rows=None, sources=None, upstream_sha=None, upstream=None):
    root = root or ROOT
    if rows is None:
        face, sha = load_upstream(root)
        parcels = population(face)
        corpus = e520.ForwardCorpus(root)
        rows = [analyse_parcel(p, corpus) for p in parcels]
        upstream_sha = upstream_sha or sha
        upstream = face.get("summary")
        sources = len(corpus_files(root)) if sources is None else sources
    summary = _summary(rows, sources or 0, upstream)
    face = {
        "study": STUDY,
        "card": CARD,
        "title": ("what happens at the second hop of the arguments that are forwarded again"),
        "generated": _now(),
        "evidence_cutoff": DATE_STAMP,
        "population_source": ("%s::population() -- every E520 call site whose argument_kind is "
                              "a_parameter_of_the_function_that_contains_the_call_site or "
                              "a_local_of_the_function_that_contains_the_call_site"
                              % os.path.basename(__file__)),
        "upstream_face": UPSTREAM_FACE.replace(os.sep, "/"),
        "upstream_study": UPSTREAM_STUDY,
        "upstream_face_sha256": upstream_sha,
        "method_limits": [
            "a forwarded *parameter* is followed through the call sites of the function that owns "
            "it; a function reached through a container, a callback or an instance attribute is "
            "outside this scan and is published as no_supplying_site_in_this_tree, never as a "
            "written value",
            "a forwarded *local* is followed to the statement that binds it inside the caller at or "
            "before the forwarding line; a name bound later in the same body is still published "
            "because Python binds it before the call only when the path runs through the statement",
            "the second hop is never followed a third time: a value that is again a parameter or a "
            "local is published as forwarded_again_at_the_second_hop and the chain ends there in "
            "this face",
            "the argument classifier and the parameter tracer are imported from E520, so a change "
            "in E520 moves this face and verify reports it",
            "nothing is executed and no source is rewritten",
            "sources_read is a snapshot of a live tree other lanes write to; it is published but "
            "not gated, while every arrival, kind and verdict is re-derived",
        ],
        "summary": summary,
        "verdict": _verdict(summary),
        "verdict_vocab": list(VERDICT_VOCAB),
        "arrival_vocab": list(ARRIVAL_VOCAB),
        "hop_style_vocab": list(STYLE_VOCAB),
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
                "upstream_face", "upstream_face_sha256", "summary", "verdict", "sites",
                "method_limits", "arrival_vocab", "hop_style_vocab", "verdict_vocab"):
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
    if summary.get("parcels_examined") != len(rows):
        bad.append("the examined population does not add up")
    upstream = summary.get("upstream_arguments_forwarded_again")
    if upstream is not None and upstream != summary.get("parcels_examined"):
        bad.append("the parcels examined (%r) drift from E520's forwarded count (%r)"
                   % (summary.get("parcels_examined"), upstream))
    for row in rows:
        where = "%s:%s" % (row.get("site_module"), row.get("site_line"))
        if row.get("hop1_kind") not in HOP1_VOCAB:
            bad.append("%s publishes hop-1 kind %r outside the vocabulary"
                       % (where, row.get("hop1_kind")))
        if row.get("hop_style") not in STYLE_VOCAB:
            bad.append("%s publishes hop style %r outside the vocabulary"
                       % (where, row.get("hop_style")))
        if row.get("arrival") not in ARRIVAL_VOCAB:
            bad.append("%s publishes arrival %r outside the vocabulary"
                       % (where, row.get("arrival")))
        kinds = [s.get("argument_kind") for s in row.get("hop_sites") or []]
        if row.get("arrival") != _arrival(kinds):
            bad.append("%s publishes arrival %r that its own sites do not derive"
                       % (where, row.get("arrival")))
        if row.get("hop_style") == S_NO_BINDING and row.get("hop_sites"):
            bad.append("%s says it found no site and publishes %d"
                       % (where, len(row.get("hop_sites") or [])))
        if row.get("arrival") == R_RESOLVED and any(k in e520.FORWARDED_AGAIN for k in kinds):
            bad.append("%s is published resolved although a site forwards again" % where)
    recomputed = _summary(rows, summary.get("sources_read") or 0, summary)
    for key in ("parcels_by_hop1_kind", "parcels_by_hop_style", "parcels_by_arrival",
                "second_hop_sites", "second_hop_kind_counts",
                "second_hop_values_resolved_there", "second_hop_values_forwarded_again",
                "second_hop_values_at_the_default", "parcels_resolved_at_the_second_hop",
                "parcels_forwarded_again_at_the_second_hop", "parcels_mixed_at_the_second_hop",
                "parcels_left_at_the_default", "parcels_with_no_supplying_site"):
        if recomputed.get(key) != summary.get(key):
            bad.append("the summary key %s does not re-derive from the rows" % key)
    return bad


def check(face=None, root=None):
    face = face or load_face(root)
    bad = face_problems(face, root)
    print("E526 check: %d problem(s)" % len(bad))
    for line in bad[:20]:
        print("  - %s" % line)
    return 1 if bad else 0


def verify(root=None):
    published = load_face(root)
    fresh = build(root=root, write=False)
    bad = face_problems(published, root)
    if fresh["verdict"] != published["verdict"]:
        bad.append("the verdict drifts when re-derived")
    volatile = ("sources_read", "parcels_examined", "parcels_by_hop1_kind",
                "parcels_by_hop_style", "parcels_by_arrival", "second_hop_sites",
                "second_hop_kind_counts", "second_hop_values_resolved_there",
                "second_hop_values_forwarded_again", "second_hop_values_at_the_default",
                "parcels_resolved_at_the_second_hop",
                "parcels_forwarded_again_at_the_second_hop",
                "parcels_mixed_at_the_second_hop", "parcels_left_at_the_default",
                "parcels_with_no_supplying_site", "distinct_supplying_modules")
    trimmed = {k: v for k, v in fresh["summary"].items() if k not in volatile}
    pinned = {k: v for k, v in published["summary"].items() if k not in volatile}
    if json.dumps(trimmed, sort_keys=True) != json.dumps(pinned, sort_keys=True):
        moved = sorted(k for k in set(trimmed) | set(pinned) if trimmed.get(k) != pinned.get(k))
        bad.append("the summary drifts when re-derived: %r" % moved[:6])
    for key in volatile:
        if fresh["summary"].get(key) != published["summary"].get(key):
            print("  note: %s moved %r -> %r (live tree, not gated)"
                  % (key, published["summary"].get(key), fresh["summary"].get(key)))
    print("E526 verify: %d problem(s)" % len(bad))
    for line in bad[:20]:
        print("  - %s" % line)
    return 1 if bad else 0


# ------------------------------------------------------------------ selftest
FIXTURE = '''\
def inner(value):
    return value


def mid(blob):
    return inner(blob)


def pass_literal():
    return mid(["x"])


def pass_again(seed):
    return mid(seed)


def bind_then_forward():
    dataset = make_rows()
    return inner(dataset)


def looped_forward():
    for chunk in make_rows():
        inner(chunk)
    return None


def absent_owner(ghost):
    return inner(ghost)


def make_rows():
    return ["y"]
'''


def _fixture_root():
    import tempfile
    d = tempfile.mkdtemp(prefix="e526_")
    os.makedirs(os.path.join(d, "scripts"))
    with io.open(os.path.join(d, "scripts", "fixture_mod.py"), "w", encoding="utf-8",
                 newline="\n") as fh:
        fh.write(FIXTURE)
    return d


def _lineno_of(text, needle):
    for index, line in enumerate(io.open(text, encoding="utf-8").read().splitlines(), 1):
        if needle in line:
            return index
    raise AssertionError("fixture line %r not found" % needle)


def selftest():
    bad = []
    d = _fixture_root()
    src = os.path.join(d, "scripts", "fixture_mod.py")
    try:
        corpus = e520.ForwardCorpus(d)
        mid_line = _lineno_of(src, "return inner(blob)")
        bind_line = _lineno_of(src, "return inner(dataset)")
        loop_line = _lineno_of(src, "inner(chunk)")
        absent_line = _lineno_of(src, "return inner(ghost)")
        parcels = [
            {"module": "fixture_mod", "function": "inner", "local": "blob",
             "source": "scripts/fixture_mod.py", "def_line": 1, "hop1_kind": H_PARAMETER,
             "site_module": "fixture_mod", "site_line": mid_line,
             "site_argument": "blob", "site_ownership": None,
             "rows_that_share_this_parcel": 1},
            {"module": "fixture_mod", "function": "inner", "local": "dataset",
             "source": "scripts/fixture_mod.py", "def_line": 1, "hop1_kind": H_LOCAL,
             "site_module": "fixture_mod", "site_line": bind_line,
             "site_argument": "dataset", "site_ownership": None,
             "rows_that_share_this_parcel": 1},
            {"module": "fixture_mod", "function": "inner", "local": "chunk",
             "source": "scripts/fixture_mod.py", "def_line": 1, "hop1_kind": H_LOCAL,
             "site_module": "fixture_mod", "site_line": loop_line,
             "site_argument": "chunk", "site_ownership": None,
             "rows_that_share_this_parcel": 1},
            {"module": "fixture_mod", "function": "absent_owner", "local": "ghost",
             "source": "scripts/fixture_mod.py", "def_line": 1, "hop1_kind": H_PARAMETER,
             "site_module": "fixture_mod", "site_line": absent_line,
             "site_argument": "ghost", "site_ownership": None,
             "rows_that_share_this_parcel": 1},
        ]
        rows = [analyse_parcel(p, corpus) for p in parcels]
    finally:
        import shutil
        shutil.rmtree(d, ignore_errors=True)

    param, bound, looped, ghost = rows
    if param["hop_style"] != S_CALL_SITE:
        bad.append("a forwarded parameter is followed through %r, expected the call sites"
                   % (param["hop_style"],))
    if param["hop_site_count"] != 2:
        bad.append("mid has %d measured call sites, expected 2" % param["hop_site_count"])
    kinds = sorted(s["argument_kind"] for s in param["hop_sites"])
    if kinds != sorted([e520.A_LITERAL, e520.A_PARAMETER_AGAIN]):
        bad.append("the second hop of mid is %r, expected a literal and a forwarded parameter"
                   % (kinds,))
    if param["arrival"] != R_MIXED:
        bad.append("mid's arrival is %r, expected mixed" % (param["arrival"],))
    if bound["hop_style"] != S_BINDING:
        bad.append("a forwarded local is followed to %r, expected the binding statement"
                   % (bound["hop_style"],))
    if bound["hop_site_count"] != 1:
        bad.append("the local dataset has %d binding sites, expected 1"
                   % (bound["hop_site_count"],))
    if bound["hop_sites"][0]["argument_kind"] != e520.A_CALL:
        bad.append("dataset is bound from %r, expected the result of a call"
                   % (bound["hop_sites"][0]["argument_kind"],))
    if bound["arrival"] != R_RESOLVED:
        bad.append("a local bound from a call is %r, expected resolved_at_the_second_hop"
                   % (bound["arrival"],))
    if looped["hop_sites"][0]["argument_kind"] != e520.A_CALL:
        bad.append("a loop target is bound from %r, expected the iterated expression classified"
                   % (looped["hop_sites"][0]["argument_kind"],))
    if ghost["arrival"] != R_NEVER:
        bad.append("a function with no call site is %r, expected no_supplying_site_in_this_tree"
                   % (ghost["arrival"],))

    summary = _summary(rows, 1, {"arguments_forwarded_again": 4})
    face = {
        "study": STUDY, "card": CARD, "generated": _now(), "evidence_cutoff": DATE_STAMP,
        "population_source": "e526_second_hop.py::population() -- fixture",
        "upstream_face": UPSTREAM_FACE.replace(os.sep, "/"), "upstream_face_sha256": "0" * 64,
        "method_limits": ["fixture"], "arrival_vocab": list(ARRIVAL_VOCAB),
        "hop_style_vocab": list(STYLE_VOCAB), "verdict_vocab": list(VERDICT_VOCAB),
        "summary": summary, "verdict": _verdict(summary), "sites": rows,
    }
    if face_problems(face):
        bad.append("the fixture face does not pass its own gate: %r" % face_problems(face)[:3])

    doctored = json.loads(json.dumps(face))
    doctored["sites"][0]["hop_sites"] = doctored["sites"][0]["hop_sites"][:1]
    doctored["sites"][0]["hop_site_count"] = 1
    if not face_problems(doctored):
        bad.append("a face that hides a forwarding site passed the gate")

    doctored2 = json.loads(json.dumps(face))
    doctored2["sites"][1]["arrival"] = R_FORWARDED
    if not face_problems(doctored2):
        bad.append("a face that calls a resolved arrival forwarded passed the gate")

    doctored3 = json.loads(json.dumps(face))
    doctored3["summary"]["parcels_examined"] = 3
    if not face_problems(doctored3):
        bad.append("a face whose population does not add up passed the gate")

    print("E526 selftest: %d problem(s) / %d checks" % (len(bad), 11))
    for line in bad:
        print("  - %s" % line)
    return 1 if bad else 0


# ------------------------------------------------------------------ entry
def run():
    face = build()
    s = face["summary"]
    print("E526 run: opened %r forwarded parcels (%r parameters / %r locals) across %r sources"
          % (s["parcels_examined"], s["parcels_by_hop1_kind"].get(H_PARAMETER),
             s["parcels_by_hop1_kind"].get(H_LOCAL), s["sources_read"]))
    print("  second hop: %r sites | resolved there %r | forwarded again %r | default %r"
          % (s["second_hop_sites"], s["second_hop_values_resolved_there"],
             s["second_hop_values_forwarded_again"], s["second_hop_values_at_the_default"]))
    print("  arrivals %r" % (s["parcels_by_arrival"],))
    print("  kinds %r" % (s["second_hop_kind_counts"],))
    print("  upstream forwarded count %r / examined %r"
          % (s["upstream_arguments_forwarded_again"], s["parcels_examined"]))
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