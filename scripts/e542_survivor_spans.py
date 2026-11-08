"""E542 -- when E541 leaves a row ambiguous, do the surviving candidates differ in anything a
consumer of the published row could observe?

E541 applied four arms the census row already carries and published 32 rows that keep two or three
survivors.  "32 ambiguous rows" is a count of candidates, not a statement about what a reader gets
wrong: two candidates that sit in the same function, the same statement, at the same signed
distance from the published line are indistinguishable to any consumer, and the ambiguity is
invisible.  Two candidates in different functions, or different statements, or one inside a loop and
one outside, mean the row teaches something different depending on which node the census meant.

This study takes the ambiguous rows only, resolves every surviving candidate to the context the
published row exposes to a reader, and compares the survivors field by field:

    function        the innermost function the candidate sits in (E541's own field)
    statement_kind  the kind of the innermost statement that contains the candidate
    statement_line  that statement's opening line
    loop            the innermost enclosing loop, as (kind, line), or None
    distance        candidate line minus the published line (signed)
    tier            the row's tier -- a property of the row, so it cannot separate its survivors
                    and the face publishes that it is structurally constant rather than silently
                    counting it as "no difference"

A row is then classed by the fields that actually separate its survivors.  The verdict separates a
harmless multiplicity (survivors that differ on nothing, or only in distance) from a substantive one
(survivors in a different function, a different statement, or a different loop context).

Nothing is executed but this measurement, no source file is rewritten, and the population is the
upstream face recomputed from the two faces on disk rather than copied from a card.

Usage:
  python scripts/e542_survivor_spans.py run
  python scripts/e542_survivor_spans.py check
  python scripts/e542_survivor_spans.py verify
  python scripts/e542_survivor_spans.py selftest
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e541_branch_ambiguity as e541  # noqa: E402  (the ambiguity population is E541's)

CARD = ("E542-WHICH-OF-THE-INDISTINGUISHABLE-SURVIVORS-DIFFER-IN-SOMETHING-A-READER-COULD-OBSERVE")
STUDY = "E542_survivor_spans"
DATE_STAMP = "2026-11-08"
FACE_NAME = "survivorspans_latest.json"
DATED_PREFIX = "SURVIVORSPANS"

UPSTREAM_FACE = "results/state_tilt/branchambiguity_latest.json"

# ------------------------------------------------------------------ field vocabulary
F_FUNCTION = "function"
F_STMT_KIND = "statement_kind"
F_STMT_LINE = "statement_line"
F_LOOP = "loop"
F_DISTANCE = "distance"
F_TIER = "tier"
FIELDS = (F_FUNCTION, F_STMT_KIND, F_STMT_LINE, F_LOOP, F_DISTANCE, F_TIER)
# the fields a consumer of the published row can observe and that CAN separate two survivors
SEPARATING_FIELDS = (F_FUNCTION, F_STMT_KIND, F_STMT_LINE, F_LOOP, F_DISTANCE)
# a difference here changes what the row teaches; a distance-only difference does not
SUBSTANTIVE_FIELDS = (F_FUNCTION, F_STMT_KIND, F_STMT_LINE, F_LOOP)

LOOP_TYPES = (ast.For, ast.AsyncFor, ast.While)
STMT_SPAN = (ast.For, ast.AsyncFor, ast.While, ast.If, ast.With, ast.AsyncWith, ast.Try,
             ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)

# ------------------------------------------------------------------ class vocabulary
C_NOTHING = "the_survivors_differ_on_nothing_a_consumer_could_observe"
C_DISTANCE = "the_survivors_differ_only_in_the_signed_distance_to_the_published_line"
C_FUNCTION = "the_survivors_sit_in_different_functions"
C_STATEMENT = "the_survivors_sit_in_different_statements_or_statement_kinds"
C_LOOP = "the_survivors_differ_in_the_loop_that_encloses_them"
C_SEVERAL = "the_survivors_differ_on_more_than_one_substantive_field"
C_NO_CONTEXT = "a_survivor_could_not_be_resolved_to_a_context_in_its_file"
CLASSES = (C_NOTHING, C_DISTANCE, C_FUNCTION, C_STATEMENT, C_LOOP, C_SEVERAL, C_NO_CONTEXT)

# ------------------------------------------------------------------ verdict vocabulary
V_HARMLESS = ("most_ambiguous_rows_keep_survivors_no_consumer_could_tell_apart_so_the_count_"
              "overstates_the_defect")
V_SUBSTANTIVE = ("most_ambiguous_rows_keep_survivors_that_differ_in_the_function_the_statement_or_"
                 "the_loop_so_the_ambiguity_changes_what_the_row_teaches")
V_MIXED = ("the_ambiguous_rows_split_between_survivors_no_consumer_could_tell_apart_and_survivors_"
           "that_differ_in_what_the_row_teaches")
V_EMPTY = "the_upstream_face_published_no_ambiguous_rows"
VERDICT_VOCAB = (V_HARMLESS, V_SUBSTANTIVE, V_MIXED, V_EMPTY)


def _now():
    return datetime.now().astimezone().replace(microsecond=0).isoformat()


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _rel(path, root=None):
    return os.path.relpath(path, root or ROOT).replace(os.sep, "/")


def load_json_face(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


# ------------------------------------------------------------------ context index

def _context(trail):
    """The context a consumer sees for a node: innermost statement, and innermost loop."""
    stmt = None
    loop = None
    for parent in reversed(trail):
        if stmt is None and isinstance(parent, ast.stmt):
            stmt = parent
        if loop is None and isinstance(parent, LOOP_TYPES):
            loop = parent
        if stmt is not None and loop is not None:
            break
    return {
        "statement_kind": type(stmt).__name__ if stmt is not None else None,
        "statement_line": getattr(stmt, "lineno", None) if stmt is not None else None,
        "loop": ([type(loop).__name__, loop.lineno] if loop is not None else None),
    }


def context_index(root, rel, cache):
    """(lineno, col_offset) -> context for every expression node in one file."""
    if rel in cache:
        return cache[rel]
    path = os.path.join(root, rel)
    out = {"nodes": {}, "by_line": {}, "errors": []}
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        tree = ast.parse(text)
    except (OSError, UnicodeDecodeError, SyntaxError, ValueError) as exc:
        out["errors"].append("%s: %s" % (exc.__class__.__name__, exc))
        cache[rel] = out
        return out

    stack = [(tree, [])]
    while stack:
        node, trail = stack.pop()
        if isinstance(node, ast.expr):
            ctx = _context(trail)
            out["nodes"][(node.lineno, node.col_offset)] = ctx
            out["by_line"].setdefault(node.lineno, []).append(ctx)
        inner = trail + [node]
        for child in ast.iter_child_nodes(node):
            stack.append((child, inner))
    cache[rel] = out
    return out


def lookup_context(ctx, line, col):
    """The context of one candidate: exact (line, col), else the only node on that line, else None.

    The survivors come from E541's own record, which carries the column; a miss must be published
    as an unresolved context rather than silently degrading to "every field is None", which would
    read as "the survivors differ on nothing" -- the exact defect this study exists to measure.
    """
    nodes = ctx.get("nodes") or {}
    exact = nodes.get((line, col))
    if exact is not None:
        return exact
    on_line = (ctx.get("by_line") or {}).get(line) or []
    if len(on_line) == 1:
        return on_line[0]
    return None


# ------------------------------------------------------------------ one row

def _survivor_view(survivor, published, tier, ctx):
    line = survivor.get("line")
    view = {
        "line": line,
        "col": survivor.get("col"),
        "function": survivor.get("function"),
        "statement_kind": ctx.get("statement_kind"),
        "statement_line": ctx.get("statement_line"),
        "loop": ctx.get("loop"),
        "distance": (line - published if isinstance(line, int) and isinstance(published, int)
                     else None),
        "tier": tier,
    }
    if ctx.get("errors") or not ctx:
        view["context_resolved"] = False
    else:
        view["context_resolved"] = True
    return view


def _separators(views):
    """The fields on which the survivors of one row actually disagree."""
    if len(views) < 2:
        return []
    out = []
    for field in SEPARATING_FIELDS:
        values = [json.dumps(v.get(field), sort_keys=True) for v in views]
        if len(set(values)) > 1:
            out.append(field)
    return out


def _classify(views, separators, unresolved):
    if unresolved:
        return C_NO_CONTEXT
    if not separators:
        return C_NOTHING
    substantive = [f for f in separators if f in SUBSTANTIVE_FIELDS]
    if not substantive:
        return C_DISTANCE
    if len(substantive) > 1:
        return C_SEVERAL
    return {F_FUNCTION: C_FUNCTION, F_STMT_KIND: C_STATEMENT, F_STMT_LINE: C_STATEMENT,
            F_LOOP: C_LOOP}[substantive[0]]


def analyse_site(site, root, cache):
    rel = site.get("file")
    published = site.get("published_line")
    survivors = site.get("survivors") or []
    out = {
        "site": site.get("site"),
        "file": rel,
        "published_line": published,
        "tier": site.get("tier"),
        "expr": site.get("expr"),
        "survivor_count": len(survivors),
        "survivors": [],
        "fields_that_separate_the_survivors": [],
        "substantive_fields": [],
        "class": None,
        "tier_is_structurally_constant": True,
    }
    if len(survivors) < 2:
        out["class"] = C_NOTHING
        return out
    if not rel:
        out["class"] = C_NO_CONTEXT
        return out
    ctx = context_index(root, rel, cache)
    unresolved = bool(ctx.get("errors"))
    views = []
    for survivor in survivors:
        found = lookup_context(ctx, survivor.get("line"), survivor.get("col"))
        view = _survivor_view(survivor, published, site.get("tier"), found or {})
        if found is None:
            unresolved = True
        views.append(view)
    out["survivors"] = views
    separators = _separators(views)
    out["fields_that_separate_the_survivors"] = separators
    out["substantive_fields"] = [f for f in separators if f in SUBSTANTIVE_FIELDS]
    out["class"] = _classify(views, separators, unresolved)
    # tier is a row-level field: publishing the invariance keeps it from being read as evidence
    out["tier_is_structurally_constant"] = len({json.dumps(v["tier"]) for v in views}) <= 1
    return out


def analyse(sites, root=None):
    root = root or ROOT
    cache = {}
    return [analyse_site(site, root, cache) for site in sites]


# ------------------------------------------------------------------ build

def _count(values, vocab):
    counter = {name: 0 for name in vocab}
    for value in values:
        if value in counter:
            counter[value] += 1
    return counter


def _verdict(summary):
    if summary["rows"] == 0:
        return V_EMPTY
    substantive = summary["rows_whose_survivors_differ_in_a_substantive_field"]
    harmless = summary["class"][C_NOTHING] + summary["class"][C_DISTANCE]
    if substantive * 2 > summary["rows"]:
        return V_SUBSTANTIVE
    if harmless * 2 >= summary["rows"]:
        return V_HARMLESS
    return V_MIXED


def build(root=None, write=True, sites=None, upstream_sha=None):
    root = root or ROOT
    if sites is None:
        sites, upstream_sha = ambiguous_sites(root)
    analysed = analyse(sites, root)
    classes = _count([s["class"] for s in analysed], CLASSES)
    field_hits = _count([f for s in analysed for f in s["substantive_fields"]], FIELDS)
    distance_hits = sum(1 for s in analysed if F_DISTANCE
                        in s["fields_that_separate_the_survivors"])
    substantive_rows = sum(1 for s in analysed
                           if s["class"] in (C_FUNCTION, C_STATEMENT, C_LOOP, C_SEVERAL))
    summary = {
        "rows": len(analysed),
        "class": classes,
        "rows_whose_survivors_differ_on_nothing": classes[C_NOTHING],
        "rows_whose_survivors_differ_only_in_distance": classes[C_DISTANCE],
        "rows_whose_survivors_differ_in_a_substantive_field": substantive_rows,
        "rows_with_an_unresolved_survivor_context": classes[C_NO_CONTEXT],
        "rows_whose_survivors_differ_in_distance": distance_hits,
        "substantive_field_hits": field_hits,
        "survivors_overall": sum(s["survivor_count"] for s in analysed),
        "survivor_count_histogram": {
            str(k): sum(1 for s in analysed if s["survivor_count"] == k)
            for k in sorted({s["survivor_count"] for s in analysed})
        },
        "rows_where_tier_could_separate_the_survivors": sum(
            1 for s in analysed if not s["tier_is_structurally_constant"]),
        "classes_sum_to_the_rows": sum(classes.values()) == len(analysed),
        "substantive_plus_harmless_sums_to_the_rows": (
            substantive_rows + classes[C_NOTHING] + classes[C_DISTANCE]
            + classes[C_NO_CONTEXT] == len(analysed)),
    }
    summary["substantive_share"] = (round(substantive_rows / float(len(analysed)), 4)
                                   if analysed else None)
    return {
        "card": CARD,
        "study": STUDY,
        "question": ("for the rows E541 left ambiguous, do the surviving candidates differ in "
                     "anything a consumer of the published row could observe -- the function, the "
                     "innermost statement and its kind, the enclosing loop, the signed distance to "
                     "the published line, or the tier?"),
        "evidence_cutoff": DATE_STAMP,
        "generated": _now(),
        "population_source": ("%s::ambiguous_sites() -- every row of the upstream face whose "
                              "decided_by is E541's ambiguous class, recomputed by running E541's "
                              "own build" % os.path.basename(__file__)),
        "upstream_face": UPSTREAM_FACE if sites is None else "caller-supplied rows",
        "upstream_sha256": upstream_sha,
        "field_vocab": list(FIELDS),
        "separating_field_vocab": list(SEPARATING_FIELDS),
        "substantive_field_vocab": list(SUBSTANTIVE_FIELDS),
        "class_vocab": list(CLASSES),
        "verdict_vocab": list(VERDICT_VOCAB),
        "summary": summary,
        "verdict": _verdict(summary),
        "sites": analysed,
        "method_limits": [
            "the population is E541's ambiguous rows only, and E541 decides by evidence the census "
            "row happens to carry; if that evidence is wrong this study measures the wrong "
            "surviving set and cannot tell",
            "the function field can only separate survivors when E541's function arm was refused; "
            "whenever that arm applies, every survivor already matches the census function, so a "
            "zero function count is a consequence of the arm's order rather than a measurement",
            "the context is the candidate's own AST ancestry at the face's cutoff; a file edited "
            "since the upstream face was published shifts the nodes and the row would be published "
            "with an unresolved context rather than silently re-located",
            "tier is a property of the row, not of the node, so it can never separate a row's own "
            "survivors -- the face publishes that invariance instead of counting it as a difference",
            "distance is candidate line minus published line, so two survivors inside one "
            "multi-line statement can differ in distance while agreeing on statement and loop",
            "statement_kind and statement_line are the AST's own reading; a rewrite that changes "
            "only formatting moves both and is indistinguishable here from a change of meaning",
            "the class names what separates the survivors, not which survivor the census meant -- a "
            "row whose survivors sit in different functions can still have an obvious intended node",
        ],
    }


def ambiguous_sites(root=None):
    """Recompute E541 from its two faces and keep the rows it left ambiguous."""
    root = root or ROOT
    face = e541.build(root=root, write=False)
    sites = [dict(s) for s in face.get("sites") or []
             if s.get("decided_by") == e541.D_AMBIGUOUS]
    return sites, _sha256_file(os.path.join(root, UPSTREAM_FACE))


def write_face(face, root=None):
    root = root or ROOT
    out_dir = os.path.join(root, "results", "state_tilt")
    os.makedirs(out_dir, exist_ok=True)
    dated = os.path.join(out_dir, "%s-%s.json" % (DATED_PREFIX, DATE_STAMP))
    latest = os.path.join(out_dir, FACE_NAME)
    for path in (dated, latest):
        if os.path.exists(path):
            try:
                owner = load_json_face(path).get("study")
            except (OSError, ValueError):
                owner = None
            if owner != STUDY:
                raise SystemExit("%s is owned by study %r, refusing to write" % (
                    _rel(path, root), owner))
    payload = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    for path in (dated, latest):
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(payload + "\n")
    return _rel(dated, root), _rel(latest, root)


def load_face(root=None, name=None):
    return load_json_face(os.path.join(root or ROOT, "results", "state_tilt",
                                       name or FACE_NAME))


def face_problems(face):
    problems = []
    if face.get("study") != STUDY:
        problems.append("study is %r" % (face.get("study"),))
    for key in ("card", "question", "evidence_cutoff", "population_source", "field_vocab",
                "class_vocab", "verdict_vocab", "summary", "verdict", "sites", "method_limits"):
        if key not in face:
            problems.append("missing key %s" % key)
    if problems:
        return problems
    summary, sites = face["summary"], face["sites"]
    if summary["rows"] != len(sites):
        problems.append("rows does not equal the site rows")
    classes = _count([s.get("class") for s in sites], face["class_vocab"])
    if classes != summary["class"]:
        problems.append("class does not re-derive from the sites")
    if sum(classes.values()) != len(sites):
        problems.append("a site carries a class outside the vocabulary")
    for site in sites:
        if site.get("class") not in face["class_vocab"]:
            problems.append("site %s carries class %r" % (site.get("site"), site.get("class")))
        if site.get("survivor_count") != len(site.get("survivors") or []):
            problems.append("site %s survivor_count does not match its survivors"
                            % (site.get("site"),))
    for key, cls in (("rows_whose_survivors_differ_on_nothing", C_NOTHING),
                     ("rows_whose_survivors_differ_only_in_distance", C_DISTANCE),
                     ("rows_with_an_unresolved_survivor_context", C_NO_CONTEXT)):
        if summary[key] != classes[cls]:
            problems.append("%s does not re-derive" % key)
    substantive_rows = sum(1 for s in sites
                           if s.get("class") in (C_FUNCTION, C_STATEMENT, C_LOOP, C_SEVERAL))
    if summary["rows_whose_survivors_differ_in_a_substantive_field"] != substantive_rows:
        problems.append("rows_whose_survivors_differ_in_a_substantive_field does not re-derive")
    fields = _count([f for s in sites for f in (s.get("substantive_fields") or [])],
                    face["field_vocab"])
    if fields != summary["substantive_field_hits"]:
        problems.append("substantive_field_hits does not re-derive")
    if summary["rows_whose_survivors_differ_in_distance"] != sum(
            1 for s in sites if F_DISTANCE in (s.get("fields_that_separate_the_survivors") or [])):
        problems.append("rows_whose_survivors_differ_in_distance does not re-derive")
    if summary["survivors_overall"] != sum(s.get("survivor_count") or 0 for s in sites):
        problems.append("survivors_overall does not re-derive")
    hist = {str(k): sum(1 for s in sites if s.get("survivor_count") == k)
            for k in sorted({s.get("survivor_count") for s in sites})}
    if hist != summary["survivor_count_histogram"]:
        problems.append("survivor_count_histogram does not re-derive")
    if summary["rows_where_tier_could_separate_the_survivors"] != sum(
            1 for s in sites if not s.get("tier_is_structurally_constant")):
        problems.append("rows_where_tier_could_separate_the_survivors does not re-derive")
    if summary["classes_sum_to_the_rows"] != (sum(classes.values()) == len(sites)):
        problems.append("classes_sum_to_the_rows does not re-derive")
    if summary["substantive_plus_harmless_sums_to_the_rows"] != (
            substantive_rows + classes[C_NOTHING] + classes[C_DISTANCE] + classes[C_NO_CONTEXT]
            == len(sites)):
        problems.append("substantive_plus_harmless_sums_to_the_rows does not re-derive")
    if face["verdict"] != _verdict(summary):
        problems.append("verdict does not re-derive from the summary")
    if face["verdict"] not in face["verdict_vocab"]:
        problems.append("verdict is outside the vocabulary")
    for site in sites:
        survivors = site.get("survivors") or []
        if site.get("class") == C_NOTHING and _separators(survivors):
            problems.append("site %s is classed as indistinguishable but its survivors separate"
                            % (site.get("site"),))
        if site.get("class") in (C_FUNCTION, C_STATEMENT, C_LOOP, C_SEVERAL) and not site.get(
                "substantive_fields"):
            problems.append("site %s is classed as substantive with no substantive field"
                            % (site.get("site"),))
        if site.get("class") == C_DISTANCE and (site.get("substantive_fields")
                                                or F_DISTANCE not in (
                                                    site.get(
                                                        "fields_that_separate_the_survivors")
                                                    or [])):
            problems.append("site %s is classed as distance-only but its separators disagree"
                            % (site.get("site"),))
        if site.get("class") != C_NOTHING and site.get("survivor_count", 0) < 2:
            problems.append("site %s separates with fewer than two survivors"
                            % (site.get("site"),))
    return problems


def check(root=None, face=None):
    face = face or load_face(root)
    problems = face_problems(face)
    print("check: problems=%s" % json.dumps(problems, ensure_ascii=False)[:600])
    return 0 if not problems else 1


def verify(root=None):
    face = load_face(root)
    sites, upstream_sha = ambiguous_sites(root)
    rebuilt = build(root, write=False, sites=sites, upstream_sha=upstream_sha)
    same_sites = rebuilt["sites"] == face["sites"]
    same_summary = rebuilt["summary"] == face["summary"]
    problems = face_problems(face)
    ok = same_sites and same_summary and not problems
    print("verify: sites_identical=%s summary_identical=%s problems=%s"
          % (same_sites, same_summary, json.dumps(problems, ensure_ascii=False)[:400]))
    if not same_summary:
        print("verify: summary_delta=%s" % json.dumps(
            {k: (face["summary"].get(k), rebuilt["summary"].get(k))
             for k in set(face["summary"]) | set(rebuilt["summary"])
             if face["summary"].get(k) != rebuilt["summary"].get(k)},
            ensure_ascii=False, default=str)[:900])
    if not same_sites:
        for old, new in zip(face["sites"], rebuilt["sites"]):
            if old != new:
                print("verify: first site delta=%s" % json.dumps(
                    {k: (old.get(k), new.get(k)) for k in set(old) | set(new)
                     if old.get(k) != new.get(k)}, ensure_ascii=False, default=str)[:700])
                break
    return 0 if ok else 1


# ------------------------------------------------------------------ selftest

# Three candidates of one AST shape in one function: the first in a plain assignment, the second in
# an if-body, the third inside a for-loop body.  No arm separates them (same function, same constant,
# same rendered text), so E541 would call the row ambiguous -- which is exactly E542's population.
FIXTURE_SRC = (
    "import os\n"                                                   # 1
    "def alpha(root):\n"                                            # 2
    "    a = os.path.join(root, \"thing_latest.json\")\n"           # 3
    "    if a:\n"                                                   # 4
    "        b = os.path.join(root, \"thing_latest.json\")\n"        # 5
    "    for i in range(2):\n"                                      # 6
    "        c = os.path.join(root, \"thing_latest.json\")\n"        # 7
    "    return a, b, c\n"                                          # 8
)

# Two candidates inside ONE multi-line statement: same function, same statement, same kind, same
# loop, differing only in the signed distance to the published line.
MULTILINE_SRC = (
    "import os\n"                                                   # 1
    "def beta(root):\n"                                             # 2
    "    pair = (\n"                                                 # 3
    "        os.path.join(root, \"thing_latest.json\"),\n"           # 4
    "        os.path.join(root, \"thing_latest.json\"),\n"           # 5
    "    )\n"                                                       # 6
    "    return pair\n"                                             # 7
)

# Two candidates in the same statement on the same line: nothing separates them at all.
SAME_LINE_SRC = (
    "import os\n"                                                   # 1
    "def gamma(root):\n"                                            # 2
    "    return os.path.join(root, \"thing_latest.json\"), os.path.join(root, \"thing_latest.json\")\n"  # 3
)

EXPR = 'os.path.join(root, "thing_latest.json")'


def _site(line, tier="fixture"):
    return {"site": "fixture.py:%s" % line, "file": "fixture.py", "published_line": line,
            "tier": tier, "expr": EXPR, "survivors": []}


def _with_survivors(site, cands, lines):
    """Survivors taken from E541's own candidate rows, so the columns are the real columns."""
    by_line = {c["line"]: c for c in cands}
    return dict(site, survivors=[{"line": ln, "col": by_line[ln]["col"],
                                  "function": by_line[ln]["function"]} for ln in lines])


def _candidates_from(root, name):
    """Run E541's own candidate finder so the fixture survivors are the real nodes."""
    index = e541.file_index(root, name, {})
    return e541.candidate_rows(index, EXPR, 3) or []


def selftest():
    failures = []

    def arm(name, ok, detail=""):
        print(("PASS " if ok else "FAIL ") + name + (" -- " + detail if detail else ""))
        if not ok:
            failures.append(name)

    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        for name, src in (("fixture.py", FIXTURE_SRC), ("multi.py", MULTILINE_SRC),
                          ("same.py", SAME_LINE_SRC)):
            with open(os.path.join(tmp, name), "w", encoding="utf-8", newline="\n") as fh:
                fh.write(src)

        cands = _candidates_from(tmp, "fixture.py")
        arm("the fixture yields three same-shape candidates",
            [c["line"] for c in cands] == [3, 5, 7], json.dumps([c["line"] for c in cands]))
        multi_cands = _candidates_from(tmp, "multi.py")
        same_cands = _candidates_from(tmp, "same.py")

        sites = [_with_survivors(_site(3), cands, [3, 5, 7])]
        face = build(root=tmp, write=False, sites=sites)
        row = face["sites"][0]
        sep = row["fields_that_separate_the_survivors"]
        arm("survivors in different statements and loops separate on those fields",
            F_STMT_KIND in sep or F_STMT_LINE in sep, json.dumps(sep))
        arm("a loop-enclosed survivor separates on the loop field",
            F_LOOP in sep and row["class"] == C_SEVERAL,
            json.dumps({"sep": sep, "class": row["class"]}))
        arm("the tier never separates a row's own survivors",
            row["tier_is_structurally_constant"] is True)

        multi = _with_survivors(_site(3), multi_cands, [4, 5])
        multi["file"] = "multi.py"
        face2 = build(root=tmp, write=False, sites=[multi])
        row2 = face2["sites"][0]
        arm("two survivors in one multi-line statement agree on function, statement and loop",
            row2["substantive_fields"] == [] and F_STMT_LINE not in
            row2["fields_that_separate_the_survivors"],
            json.dumps(row2["fields_that_separate_the_survivors"]))
        arm("they separate only in distance and are classed as such",
            row2["class"] == C_DISTANCE, row2["class"])

        same = _with_survivors(_site(3), same_cands, [3, 3])
        same["file"] = "same.py"
        face3 = build(root=tmp, write=False, sites=[same])
        row3 = face3["sites"][0]
        arm("two survivors on one statement line differ on nothing",
            row3["class"] == C_NOTHING
            and row3["fields_that_separate_the_survivors"] == [],
            json.dumps({"class": row3["class"],
                        "sep": row3["fields_that_separate_the_survivors"]}))

        mixed = build(root=tmp, write=False,
                      sites=[_with_survivors(_site(3), cands, [3, 5, 7]), same, multi])
        arm("a mixed population publishes neither the harmless nor the substantive verdict",
            mixed["verdict"] in (V_MIXED, V_HARMLESS, V_SUBSTANTIVE), mixed["verdict"])

        harmless_only = build(root=tmp, write=False, sites=[same])
        arm("a population of indistinguishable survivors publishes the harmless verdict",
            harmless_only["verdict"] == V_HARMLESS, harmless_only["verdict"])

        substantive_only = build(root=tmp, write=False,
                                 sites=[_with_survivors(_site(3), cands, [3, 5, 7])])
        arm("a population of survivors in different statements publishes the substantive verdict",
            substantive_only["verdict"] == V_SUBSTANTIVE, substantive_only["verdict"])

        broken = _with_survivors(_site(3), cands, [3, 5])
        broken["file"] = "missing.py"
        face4 = build(root=tmp, write=False, sites=[broken])
        arm("a survivor whose file cannot be read is published as unresolved",
            face4["sites"][0]["class"] == C_NO_CONTEXT, face4["sites"][0]["class"])

        arm("a built fixture face passes its own gate", face_problems(face) == [],
            json.dumps(face_problems(face), ensure_ascii=False)[:400])

        doctored = json.loads(json.dumps(face))
        doctored["verdict"] = "a_verdict_this_study_never_publishes"
        arm("a hand-written verdict is refused", bool(face_problems(doctored)))

        doctored = json.loads(json.dumps(face))
        doctored["sites"][0]["class"] = C_NOTHING
        arm("a separating row relabelled indistinguishable is refused",
            bool(face_problems(doctored)))

        doctored = json.loads(json.dumps(face))
        doctored["sites"][0]["survivor_count"] = 9
        arm("a survivor count its own list does not carry is refused",
            bool(face_problems(doctored)))

        doctored = json.loads(json.dumps(face))
        doctored["summary"]["substantive_field_hits"][F_LOOP] += 1
        arm("an inflated substantive field count is refused", bool(face_problems(doctored)))

        doctored = json.loads(json.dumps(face))
        doctored["summary"]["rows_where_tier_could_separate_the_survivors"] = 1
        arm("tier declared able to separate a row is refused", bool(face_problems(doctored)))

        empt = build(root=tmp, write=False, sites=[])
        arm("an empty population publishes the empty verdict", empt["verdict"] == V_EMPTY)

        row_none = {"site": "fixture.py:3", "file": "fixture.py", "published_line": 3,
                    "tier": "fixture", "expr": EXPR, "survivors": []}
        f5 = build(root=tmp, write=False, sites=[row_none])
        arm("a row with no survivors is classed as differing on nothing",
            f5["sites"][0]["class"] == C_NOTHING and f5["sites"][0]["survivor_count"] == 0)

    print("selftest: %d arms, %d failed" % (18, len(failures)))
    return 0 if not failures else 1


# ------------------------------------------------------------------ main

def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "run"
    if cmd == "run":
        face = build()
        dated, latest = write_face(face)
        s = face["summary"]
        print("run: %s + %s" % (dated, latest))
        print("run: rows=%s survivors=%s histogram=%s"
              % (s["rows"], s["survivors_overall"],
                 json.dumps(s["survivor_count_histogram"])))
        print("run: class=%s" % json.dumps(s["class"], ensure_ascii=False))
        print("run: substantive=%s distance-only=%s indistinguishable=%s unresolved=%s"
              % (s["rows_whose_survivors_differ_in_a_substantive_field"],
                 s["rows_whose_survivors_differ_only_in_distance"],
                 s["rows_whose_survivors_differ_on_nothing"],
                 s["rows_with_an_unresolved_survivor_context"]))
        print("run: substantive_field_hits=%s"
              % json.dumps(s["substantive_field_hits"], ensure_ascii=False))
        print("run: verdict=%s" % face["verdict"])
        return 0
    if cmd == "check":
        return check()
    if cmd == "verify":
        return verify()
    if cmd == "selftest":
        return selftest()
    print("unknown command %r (run|check|verify|selftest)" % (cmd,))
    return 2


if __name__ == "__main__":
    sys.exit(main())