"""E540 -- is the "line" a census face publishes a statement anchor or the expression itself?

E398 publishes one row per read site and per write site of a bare ``latest.json``, and every row
carries ``file`` + ``line`` + ``expr``.  E539 showed that the name inside the row's evidence often
does not sit on that line (158 of 294 checkable rows named it elsewhere in the enclosing function).
That measurement treated "elsewhere" as a coarse pointer; this study asks what the published line
*is*:

  1. SPAN -- locate the expression the row publishes as an AST node of the file it names (node
     shape, not text: line numbers differ between the published row and the file), then find the
     innermost statement that holds it and the innermost function that holds that statement.
  2. ANCHOR -- classify the published line against those spans: the expression line itself, the
     statement's opening line, a continuation of that statement, a loop header above it, another
     statement in the same function, or another statement in the file.  Publish the signed
     distance from the anchor to the expression.
  3. CONSUMERS -- does anything in this corpus land on a published line to read a value?  Count the
     sites that read a ``line`` field out of a payload and the sites that resolve a source position
     at run time (linecache / readlines()[n] / splitlines()[n]), and publish what a consumer
     landing on the anchor would actually find (does the published line even name part of the
     expression?).

Nothing is executed but this measurement, no file is rewritten, and the population is the census
face as it sits on disk at its own cutoff.

Usage:
  python scripts/e540_line_pointer_distance.py run
  python scripts/e540_line_pointer_distance.py check
  python scripts/e540_line_pointer_distance.py verify
  python scripts/e540_line_pointer_distance.py selftest
"""
from __future__ import annotations

import ast
import hashlib
import json
import keyword
import os
import re
import sys
import tempfile
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

CARD = "E540-WHICH-LINE-POINTER-A-FACE-PUBLISHES-IS-A-STATEMENT-ANCHOR-RATHER-THAN-THE-EXPRESSION-LINE"
STUDY = "E540_line_pointer_distance"
DATE_STAMP = "2026-11-08"
FACE_NAME = "linepointer_latest.json"
DATED_PREFIX = "LINEPOINTER"

UPSTREAM_FACE = "results/state_tilt/latestfamily_latest.json"

# ------------------------------------------------------------------ anchor vocabulary
A_EXPRESSION = "the_published_line_is_part_of_the_expression_itself"
A_STATEMENT_START = "the_published_line_opens_the_statement_that_holds_the_expression"
A_INSIDE_STATEMENT = "the_published_line_is_a_continuation_of_that_statement"
A_LOOP_HEADER = "the_published_line_is_a_loop_header_above_the_expression"
A_OTHER_STMT_SAME_FUNCTION = "the_published_line_is_another_statement_in_the_same_function"
A_OTHER_STMT_IN_FILE = "the_published_line_is_another_statement_in_the_file"
A_NO_EXPRESSION = "no_node_for_the_published_expression_was_located"
A_NO_FILE = "the_row_points_at_a_file_this_measurement_could_not_read"
A_LINE_OUTSIDE = "the_published_line_is_outside_the_file"
ANCHOR_VOCAB = (A_EXPRESSION, A_STATEMENT_START, A_INSIDE_STATEMENT, A_LOOP_HEADER,
                A_OTHER_STMT_SAME_FUNCTION, A_OTHER_STMT_IN_FILE, A_NO_EXPRESSION,
                A_NO_FILE, A_LINE_OUTSIDE)

# ------------------------------------------------------------------ locator vocabulary
L_NODE = "the_shape_of_the_published_expression_equals_a_node_in_the_file"
L_NAME = "a_line_carrying_every_identifier_of_the_expression_near_the_row"
L_NO_NODE = "no_node_and_no_line_in_the_file_carries_the_expression"
L_DOES_NOT_PARSE = "the_published_expression_does_not_parse_as_a_python_expression"
L_NO_FILE = "the_file_could_not_be_read"
L_OUTSIDE = "the_published_line_is_outside_the_file"
LOCATOR_VOCAB = (L_NODE, L_NAME, L_NO_NODE, L_DOES_NOT_PARSE, L_NO_FILE, L_OUTSIDE)

# ------------------------------------------------------------------ verdict vocabulary
V_ANCHOR = ("most_published_lines_are_anchors_rather_than_the_expression_line_so_a_consumer_"
            "landing_there_reads_a_statement_not_a_value")
V_ON_LINE = "most_published_lines_are_part_of_the_expression_itself"
V_EMPTY = "the_census_face_published_no_rows"
VERDICT_VOCAB = (V_ANCHOR, V_ON_LINE, V_EMPTY)

BUCKETS = ("0", "1-3", "4-10", "11-30", "31+")

SKIP_DIRS = {".git", ".venv", "__pycache__", "node_modules", "results", "data", "logs"}
SELF_SKIP = ("scripts/e540_line_pointer_distance.py", "scripts/e539_label_vs_evidence.py",
             "scripts/e398_latest_family.py")

IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
PY_WORDS = set(keyword.kwlist) | {"True", "False", "None"}

LINE_FIELD_PATTERNS = (
    re.compile(r"\.get\(\s*[\"']line[\"']\s*[,)]"),
    re.compile(r"\[\s*[\"']line[\"']\s*\]"),
    re.compile(r"\.get\(\s*[\"']line_no[\"']\s*[,)]"),
)
POSITION_PATTERNS = (
    re.compile(r"\blinecache\b"),
    re.compile(r"readlines\(\)\s*\["),
    re.compile(r"splitlines\(\)\s*\["),
    re.compile(r"itertools\.islice\("),
)


def _now():
    return datetime.now().astimezone().replace(microsecond=0).isoformat()


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _rel(path, root=None):
    root = root or ROOT
    return os.path.relpath(path, root).replace(os.sep, "/")


# ------------------------------------------------------------------ population

def load_upstream(root=None):
    path = os.path.join(root or ROOT, UPSTREAM_FACE)
    with open(path, encoding="utf-8") as fh:
        return json.load(fh), _sha256_file(path)


def population(face):
    rows = []
    for key in ("read_sites", "write_sites"):
        for row in face.get(key) or []:
            item = dict(row)
            item["published_in"] = key
            rows.append(item)
    return rows


# ------------------------------------------------------------------ file index

def _span(node):
    return (node.lineno, getattr(node, "end_lineno", None) or node.lineno)


def file_index(root, rel, cache):
    """AST-derived view of one file: expression nodes by shape, statement/function/loop spans."""
    if rel in cache:
        return cache[rel]
    path = os.path.join(root, rel)
    entry = {"lines": None, "by_shape": {}, "stmts": [], "funcs": [], "loops": [],
             "stmts_by_line": [], "error": None}
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        entry["error"] = "unreadable: %s" % exc.__class__.__name__
        cache[rel] = entry
        return entry
    entry["lines"] = text.split("\n")
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError) as exc:
        entry["error"] = "unparseable: %s" % exc.__class__.__name__
        cache[rel] = entry
        return entry
    for node in ast.walk(tree):
        if isinstance(node, ast.expr):
            entry["by_shape"].setdefault(ast.dump(node, include_attributes=False), []).append(node)
        if isinstance(node, ast.stmt):
            entry["stmts"].append(_span(node))
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            entry["funcs"].append(_span(node))
        if isinstance(node, (ast.For, ast.AsyncFor, ast.While)):
            entry["loops"].append(_span(node))
    cache[rel] = entry
    return entry


def _innermost(spans, line):
    best = None
    for start, end in spans:
        if start <= line <= end and (best is None or end - start < best[1] - best[0]):
            best = (start, end)
    return best


def _encloses(span, other):
    return span is not None and other is not None and span[0] <= other[0] and other[1] <= span[1]


def names_of(expr):
    seen = []
    for name in IDENT_RE.findall(expr or ""):
        if name in PY_WORDS or name in seen:
            continue
        seen.append(name)
    return seen[-3:]


def locate_node(index, expr, near_line):
    try:
        target = ast.parse(expr, mode="eval").body
    except (SyntaxError, ValueError):
        return None, L_DOES_NOT_PARSE, 0
    cands = index["by_shape"].get(ast.dump(target, include_attributes=False)) or []
    if not cands:
        return None, L_NO_NODE, 0
    fn = _innermost(index["funcs"], near_line)
    inside = [n for n in cands if fn and fn[0] <= n.lineno <= fn[1]]
    pool = inside or cands
    return min(pool, key=lambda n: (abs(n.lineno - near_line), n.lineno)), L_NODE, len(cands)


def locate_by_name(index, expr, near_line):
    wanted = names_of(expr)
    if not wanted:
        return None
    lines = index["lines"]
    fn = _innermost(index["funcs"], near_line)
    lo, hi = (fn if fn else (1, len(lines)))
    best = None
    for i in range(max(lo, 1), min(hi, len(lines)) + 1):
        text = lines[i - 1]
        if all(w in text for w in wanted):
            if best is None or abs(i - near_line) < abs(best - near_line):
                best = i
    return best


def classify(published, expr_span, stmt_span, loop_start, same_function):
    """Pure: the anchor class of a published line given the spans this study located."""
    if expr_span is None:
        return A_NO_EXPRESSION
    if expr_span[0] <= published <= expr_span[1]:
        return A_EXPRESSION
    if stmt_span is not None and stmt_span[0] <= published <= stmt_span[1]:
        return A_STATEMENT_START if published == stmt_span[0] else A_INSIDE_STATEMENT
    if loop_start is not None and published == loop_start:
        return A_LOOP_HEADER
    if same_function:
        return A_OTHER_STMT_SAME_FUNCTION
    return A_OTHER_STMT_IN_FILE


def bucket_of(distance):
    if distance is None:
        return None
    mag = abs(int(distance))
    if mag == 0:
        return "0"
    if mag <= 3:
        return "1-3"
    if mag <= 10:
        return "4-10"
    if mag <= 30:
        return "11-30"
    return "31+"


def analyse_row(row, root, cache):
    rel = row.get("file")
    published = row.get("line")
    expr = row.get("expr") or ((row.get("evidence") or {}).get("expr"))
    out = {
        "site": row.get("site") or ("%s:%s" % (rel, published)),
        "published_in": row.get("published_in"),
        "file": rel,
        "published_line": published,
        "tier": row.get("tier"),
        "class": row.get("class"),
        "expr": expr,
        "locator": None,
        "anchor": None,
        "published_line_is_a_loop_header": False,
        "expression_span": None,
        "statement_span": None,
        "loop_start": None,
        "same_function": None,
        "distance": None,
        "published_line_text": None,
        "published_line_names_part_of_the_expression": None,
    }
    if not rel or not isinstance(published, int):
        out["anchor"] = A_NO_FILE
        out["locator"] = L_NO_FILE
        return out
    index = file_index(root, rel, cache)
    if index["error"]:
        out["anchor"] = A_NO_FILE
        out["locator"] = L_NO_FILE
        out["index_error"] = index["error"]
        return out
    lines = index["lines"]
    if published < 1 or published > len(lines):
        out["anchor"] = A_LINE_OUTSIDE
        out["locator"] = L_OUTSIDE
        return out
    out["published_line_text"] = lines[published - 1].strip()[:200]
    node, locator, shape_variants = locate_node(index, expr or "", published)
    out["shape_variants"] = shape_variants
    if node is not None:
        expr_span = _span(node)
    else:
        name_line = locate_by_name(index, expr or "", published)
        expr_span = (name_line, name_line) if name_line else None
        locator = L_NAME if name_line else locator
    out["locator"] = locator
    if expr_span is None:
        out["anchor"] = A_NO_EXPRESSION
        out["published_line_names_part_of_the_expression"] = False
        return out
    out["expression_span"] = list(expr_span)
    stmt = _innermost(index["stmts"], expr_span[0])
    out["statement_span"] = list(stmt) if stmt else None
    loops = [s for s in index["loops"] if s[0] <= expr_span[0] and s[1] >= expr_span[1]]
    loop_start = min((s[0] for s in loops), default=None)
    out["loop_start"] = loop_start
    fn_expr = _innermost(index["funcs"], expr_span[0])
    fn_pub = _innermost(index["funcs"], published)
    out["same_function"] = bool(fn_expr is not None and fn_expr == fn_pub)
    out["anchor"] = classify(published, expr_span, stmt, loop_start, out["same_function"])
    out["distance"] = expr_span[0] - published
    out["published_line_is_a_loop_header"] = bool(loop_start is not None and loop_start == published)
    wanted = names_of(expr or "")
    text = lines[published - 1]
    out["published_line_names_part_of_the_expression"] = any(w in text for w in wanted) if wanted else None
    return out


# ------------------------------------------------------------------ consumers leg

def line_pointer_consumers(root=None):
    root = root or ROOT
    hits = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in sorted(dirnames) if d not in SKIP_DIRS and not d.startswith(".")]
        for name in sorted(filenames):
            if not name.endswith(".py"):
                continue
            rel = _rel(os.path.join(dirpath, name), root)
            if rel in SELF_SKIP:
                continue
            try:
                with open(os.path.join(dirpath, name), encoding="utf-8") as fh:
                    text = fh.read()
            except OSError:
                continue
            for i, line in enumerate(text.split("\n"), 1):
                for arm, patterns in (("reads_a_line_field", LINE_FIELD_PATTERNS),
                                      ("resolves_a_source_position", POSITION_PATTERNS),
                                      ("names_the_census_face", LINE_FIELD_PATTERNS[:0]
                                       + (re.compile(r"latestfamily"),))):
                    if any(p.search(line) for p in patterns):
                        hits.append({"file": rel, "line": i, "arm": arm,
                                     "text": line.strip()[:180]})
                        break
    return hits


# ------------------------------------------------------------------ build

def _count(values, vocab):
    counter = {name: 0 for name in vocab}
    for value in values:
        if value in counter:
            counter[value] += 1
    return counter


def _median(values):
    if not values:
        return None
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2.0


def _verdict(summary):
    if summary["rows"] == 0:
        return V_EMPTY
    if summary["rows_published_on_the_expression_line"] * 2 >= summary["rows"]:
        return V_ON_LINE
    return V_ANCHOR


def analyse(rows, root=None):
    root = root or ROOT
    cache = {}
    return [analyse_row(row, root, cache) for row in rows]


def build(root=None, write=True, rows=None, upstream_sha=None):
    root = root or ROOT
    if rows is None:
        face, upstream_sha = load_upstream(root)
        rows = population(face)
    sites = analyse(rows, root)
    anchors = _count([s["anchor"] for s in sites], ANCHOR_VOCAB)
    locators = _count([s["locator"] for s in sites], LOCATOR_VOCAB)
    distances = [s["distance"] for s in sites if isinstance(s["distance"], int)]
    buckets = _count([bucket_of(d) for d in distances], BUCKETS)
    located = len(distances)
    by_tier = {}
    for site in sites:
        tier = site.get("tier") or "unstated"
        row = by_tier.setdefault(tier, {"total": 0, A_EXPRESSION: 0, "anchored": 0})
        row["total"] += 1
        if site["anchor"] == A_EXPRESSION:
            row[A_EXPRESSION] += 1
        elif site["distance"] is not None:
            row["anchored"] += 1
    consumers = line_pointer_consumers(root)
    summary = {
        "rows": len(sites),
        "rows_read": sum(1 for s in sites if s["published_in"] == "read_sites"),
        "rows_written": sum(1 for s in sites if s["published_in"] == "write_sites"),
        "by_locator": locators,
        "expressions_located": located,
        "by_anchor": anchors,
        "anchor_sums_to_the_rows": sum(anchors.values()) == len(sites),
        "rows_published_on_the_expression_line": anchors[A_EXPRESSION],
        "rows_published_at_the_statement_start": anchors[A_STATEMENT_START],
        "rows_published_inside_the_same_statement": anchors[A_INSIDE_STATEMENT],
        "rows_published_at_a_loop_header": anchors[A_LOOP_HEADER],
        "rows_published_elsewhere_in_the_same_function": anchors[A_OTHER_STMT_SAME_FUNCTION],
        "rows_published_elsewhere_in_the_file": anchors[A_OTHER_STMT_IN_FILE],
        "rows_with_no_located_expression": anchors[A_NO_EXPRESSION] + anchors[A_NO_FILE]
        + anchors[A_LINE_OUTSIDE],
        "published_line_names_part_of_the_expression": sum(
            1 for s in sites if s.get("published_line_names_part_of_the_expression") is True),
        "published_line_says_something_else": sum(
            1 for s in sites if s.get("published_line_names_part_of_the_expression") is False),
        "rows_whose_expression_shape_appears_more_than_once_in_the_file": sum(
            1 for s in sites if (s.get("shape_variants") or 0) > 1),
        "loop_headers_published": sum(1 for s in sites if s.get("published_line_is_a_loop_header")),
        "distance": {
            "min": min(distances) if distances else None,
            "max": max(distances) if distances else None,
            "median": _median(distances),
            "mean_abs": (round(sum(abs(d) for d in distances) / float(located), 3)
                         if located else None),
            "buckets": buckets,
            "rows_measured": located,
            "buckets_sum_to_the_measured_rows": sum(buckets.values()) == located,
        },
        "by_tier": by_tier,
        "line_pointer_consumers": {
            "sites": len(consumers),
            "reads_a_line_field": sum(1 for c in consumers if c["arm"] == "reads_a_line_field"),
            "resolves_a_source_position": sum(
                1 for c in consumers if c["arm"] == "resolves_a_source_position"),
            "names_the_census_face": sum(
                1 for c in consumers if c["arm"] == "names_the_census_face"),
            "files": sorted({c["file"] for c in consumers}),
        },
    }
    return {
        "card": CARD,
        "study": STUDY,
        "question": ("is the line a census face publishes the expression a reader would land on, "
                     "or a statement anchor above it?"),
        "evidence_cutoff": DATE_STAMP,
        "generated": _now(),
        "population_source": ("%s::population() -- every read_sites row then every write_sites row "
                              "of the census face" % os.path.basename(__file__)),
        "upstream_face": UPSTREAM_FACE if rows is None or upstream_sha else "caller-supplied rows",
        "upstream_sha256": upstream_sha,
        "anchor_vocab": list(ANCHOR_VOCAB),
        "locator_vocab": list(LOCATOR_VOCAB),
        "distance_buckets": list(BUCKETS),
        "verdict_vocab": list(VERDICT_VOCAB),
        "summary": summary,
        "verdict": _verdict(summary),
        "sites": sites,
        "consumers": consumers,
        "method_limits": [
            "the expression is located by AST node shape, so a file that spells the same value "
            "with a different expression (a temporary, a loop variable) is published as "
            "no node and falls back to a name match rather than being resolved",
            "the statement span is the innermost ast.stmt containing the expression's first "
            "line; a call spanning a comprehension keeps its own statement, so the anchor is "
            "never attributed to an enclosing statement that only syntactically contains it",
            "the consumer leg is a static pattern scan over .py files outside results/ and "
            "data/; it cannot tell which payload a line is read from, so the count is an upper "
            "bound on sites that COULD land on a published line",
            "the population is the census face as published on disk at its own cutoff; nothing "
            "is rebuilt upstream",
        ],
    }


def write_face(face, root=None):
    root = root or ROOT
    out_dir = os.path.join(root, "results", "state_tilt")
    os.makedirs(out_dir, exist_ok=True)
    dated = os.path.join(out_dir, "%s-%s.json" % (DATED_PREFIX, DATE_STAMP))
    latest = os.path.join(out_dir, FACE_NAME)
    for path in (latest, dated):
        if os.path.exists(path):
            try:
                with open(path, encoding="utf-8") as fh:
                    owner = json.load(fh).get("study")
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
    path = os.path.join(root or ROOT, "results", "state_tilt", name or FACE_NAME)
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def face_problems(face):
    problems = []
    if face.get("study") != STUDY:
        problems.append("study is %r" % (face.get("study"),))
    for key in ("card", "question", "evidence_cutoff", "population_source", "summary",
                "verdict", "sites", "consumers", "method_limits"):
        if key not in face:
            problems.append("missing key %s" % key)
    if problems:
        return problems
    summary, sites = face["summary"], face["sites"]
    if summary["rows"] != len(sites):
        problems.append("rows does not equal the site rows")
    anchors = _count([s.get("anchor") for s in sites], face["anchor_vocab"])
    if anchors != summary["by_anchor"]:
        problems.append("by_anchor does not re-derive from the sites")
    if sum(anchors.values()) != len(sites):
        problems.append("a site carries an anchor outside the vocabulary")
    locators = _count([s.get("locator") for s in sites], face["locator_vocab"])
    if locators != summary["by_locator"]:
        problems.append("by_locator does not re-derive from the sites")
    distances = [s["distance"] for s in sites if isinstance(s.get("distance"), int)]
    if summary["expressions_located"] != len(distances):
        problems.append("expressions_located does not re-derive")
    buckets = _count([bucket_of(d) for d in distances], face["distance_buckets"])
    if buckets != summary["distance"]["buckets"]:
        problems.append("distance buckets do not re-derive from the sites")
    if summary["distance"]["buckets_sum_to_the_measured_rows"] != (
            sum(buckets.values()) == len(distances)):
        problems.append("buckets_sum_to_the_measured_rows does not re-derive")
    if summary["rows_published_on_the_expression_line"] != anchors[A_EXPRESSION]:
        problems.append("rows_published_on_the_expression_line does not re-derive")
    if summary["published_line_names_part_of_the_expression"] != sum(
            1 for s in sites if s.get("published_line_names_part_of_the_expression") is True):
        problems.append("published_line_names_part_of_the_expression does not re-derive")
    if summary["published_line_says_something_else"] != sum(
            1 for s in sites if s.get("published_line_names_part_of_the_expression") is False):
        problems.append("published_line_says_something_else does not re-derive")
    if summary["rows_whose_expression_shape_appears_more_than_once_in_the_file"] != sum(
            1 for s in sites if (s.get("shape_variants") or 0) > 1):
        problems.append("shape-ambiguity count does not re-derive")
    if face["verdict"] != _verdict(summary):
        problems.append("verdict does not re-derive from the summary")
    if face["verdict"] not in face["verdict_vocab"]:
        problems.append("verdict is outside the vocabulary")
    for site in sites:
        if site.get("anchor") not in face["anchor_vocab"]:
            problems.append("site %s carries anchor %r" % (site.get("site"), site.get("anchor")))
            continue
        published = site.get("published_line")
        span = site.get("expression_span")
        if span is not None:
            again = classify(published, tuple(span),
                             tuple(site["statement_span"]) if site.get("statement_span") else None,
                             site.get("loop_start"), bool(site.get("same_function")))
            if again != site.get("anchor"):
                problems.append("site %s is published as %r but its spans classify as %r"
                                % (site.get("site"), site.get("anchor"), again))
            if site.get("distance") != span[0] - published:
                problems.append("site %s publishes a distance its spans do not derive"
                                % (site.get("site"),))
            if bucket_of(site.get("distance")) != bucket_of(span[0] - published):
                problems.append("site %s publishes a distance bucket its spans do not derive"
                                % (site.get("site"),))
        elif site.get("anchor") not in (A_NO_EXPRESSION, A_NO_FILE, A_LINE_OUTSIDE):
            problems.append("site %s carries no expression span but is classed %r"
                            % (site.get("site"), site.get("anchor")))
    declared = summary["line_pointer_consumers"]["sites"]
    if declared != len(face["consumers"]):
        problems.append("line_pointer_consumers.sites does not equal the consumer rows")
    for arm in ("reads_a_line_field", "resolves_a_source_position", "names_the_census_face"):
        want = sum(1 for c in face["consumers"] if c.get("arm") == arm)
        if summary["line_pointer_consumers"][arm] != want:
            problems.append("line_pointer_consumers[%s] does not re-derive" % arm)
    return problems


def check(root=None, face=None):
    face = face or load_face(root)
    problems = face_problems(face)
    print("check: problems=%s" % json.dumps(problems, ensure_ascii=False)[:600])
    return 0 if not problems else 1


def verify(root=None):
    face = load_face(root)
    upstream, sha = load_upstream(root)
    rebuilt = build(root, write=False, rows=population(upstream), upstream_sha=sha)
    same_sites = rebuilt["sites"] == face["sites"]
    same_summary = rebuilt["summary"] == face["summary"]
    same_consumers = rebuilt["consumers"] == face["consumers"]
    problems = face_problems(face)
    ok = same_sites and same_summary and same_consumers and not problems
    print("verify: sites_identical=%s summary_identical=%s consumers_identical=%s problems=%s"
          % (same_sites, same_summary, same_consumers,
             json.dumps(problems, ensure_ascii=False)[:400]))
    if not same_summary:
        print("verify: summary_delta=%s" % json.dumps(
            {k: (face["summary"].get(k), rebuilt["summary"].get(k))
             for k in set(face["summary"]) | set(rebuilt["summary"])
             if face["summary"].get(k) != rebuilt["summary"].get(k)}, ensure_ascii=False)[:900])
    if not same_sites:
        for old, new in zip(face["sites"], rebuilt["sites"]):
            if old != new:
                print("verify: first site delta=%s" % json.dumps(
                    {k: (old.get(k), new.get(k)) for k in set(old) | set(new)
                     if old.get(k) != new.get(k)}, ensure_ascii=False, default=str)[:700])
                break
    return 0 if ok else 1


# ------------------------------------------------------------------ selftest

FIXTURE_SRC = (
    "def f(root):\n"                                  # 1
    "    payload = {\n"                               # 2
    "        'a': root / 'latest.json',\n"            # 3
    "    }\n"                                         # 4
    "    for item in payload:\n"                      # 5
    "        value = read(root / 'latest.json')\n"    # 6
    "    other = object()\n"                          # 7
    "    return payload\n"                            # 8
)


def _fixture_row(line, expr="root / 'latest.json'", file="fixture.py"):
    return {"file": file, "line": line, "expr": expr, "site": "%s:%s" % (file, line),
            "published_in": "read_sites", "tier": "fixture", "class": None}


def _fixture_rows():
    return [
        _fixture_row(3),                       # expression itself
        _fixture_row(2),                       # the dict literal's opening line
        _fixture_row(5),                       # loop header above the expression
        _fixture_row(7),                       # another statement in the same function
        _fixture_row(3, expr="nowhere(x)"),    # no node, no name
        _fixture_row(3, file="missing.py"),    # file not readable
        _fixture_row(99),                      # published line outside the file
    ]


def selftest():
    failures = []

    def arm(name, ok, detail=""):
        print(("PASS " if ok else "FAIL ") + name + (" -- " + detail if detail else ""))
        if not ok:
            failures.append(name)

    with tempfile.TemporaryDirectory() as tmp:
        with open(os.path.join(tmp, "fixture.py"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(FIXTURE_SRC)
        rows = _fixture_rows()
        face = build(root=tmp, write=False, rows=rows)
        sites = face["sites"]
        arm("fixture rows all analysed", len(sites) == len(rows),
            "%s of %s" % (len(sites), len(rows)))
        got = [s["anchor"] for s in sites]
        want = [A_EXPRESSION, A_STATEMENT_START, A_LOOP_HEADER, A_OTHER_STMT_SAME_FUNCTION,
                A_NO_EXPRESSION, A_NO_FILE, A_LINE_OUTSIDE]
        arm("every anchor class is produced by its own row", got == want,
            json.dumps(got, ensure_ascii=False))
        arm("the expression line publishes distance zero",
            sites[0]["distance"] == 0 and sites[0]["expression_span"] == [3, 3],
            json.dumps({k: sites[0][k] for k in ("distance", "expression_span")}))
        arm("the dict opening line is charged one line of distance",
            sites[1]["distance"] == 1, str(sites[1]["distance"]))
        arm("the loop header is named as a loop header",
            sites[2]["anchor"] == A_LOOP_HEADER and sites[2]["published_line_is_a_loop_header"]
            and sites[2]["distance"] == 1, json.dumps(
                {k: sites[2][k] for k in ("anchor", "distance", "loop_start")}))
        arm("an unlocatable expression is not charged a distance",
            sites[4]["distance"] is None and sites[4]["locator"] in (L_NO_NODE, L_NAME),
            json.dumps({k: sites[4][k] for k in ("locator", "anchor", "distance")}))
        arm("the anchor buckets sum to the measured rows",
            face["summary"]["distance"]["buckets_sum_to_the_measured_rows"]
            and sum(face["summary"]["distance"]["buckets"].values())
            == face["summary"]["expressions_located"],
            json.dumps(face["summary"]["distance"]["buckets"]))
        arm("a built fixture face passes its own gate", face_problems(face) == [],
            json.dumps(face_problems(face), ensure_ascii=False)[:300])

        doctored = json.loads(json.dumps(face))
        doctored["verdict"] = "a_verdict_this_study_never_publishes"
        arm("a hand-written verdict is refused", bool(face_problems(doctored)))

        doctored = json.loads(json.dumps(face))
        doctored["sites"][0]["anchor"] = A_OTHER_STMT_IN_FILE
        arm("a row moved to another anchor class is refused", bool(face_problems(doctored)))

        doctored = json.loads(json.dumps(face))
        doctored["sites"][0]["distance"] = 5
        arm("a distance its spans do not derive is refused", bool(face_problems(doctored)))

        doctored = json.loads(json.dumps(face))
        doctored["summary"]["by_anchor"][A_EXPRESSION] += 1
        arm("an inflated anchor count is refused", bool(face_problems(doctored)))

        doctored = json.loads(json.dumps(face))
        doctored["summary"]["line_pointer_consumers"]["reads_a_line_field"] += 1
        arm("an inflated consumer count is refused", bool(face_problems(doctored)))

    arm("an empty population publishes the empty verdict",
        build(root=ROOT, write=False, rows=[])["verdict"] == V_EMPTY)
    print("selftest: %d arms, %d failed" % (12, len(failures)))
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
        print("run: rows=%s located=%s on_the_expression_line=%s anchored_elsewhere=%s"
              % (s["rows"], s["expressions_located"],
                 s["rows_published_on_the_expression_line"],
                 s["rows"] - s["rows_published_on_the_expression_line"]))
        print("run: by_anchor=%s" % json.dumps(s["by_anchor"], ensure_ascii=False))
        print("run: distance=%s" % json.dumps(s["distance"], ensure_ascii=False))
        print("run: consumers=%s" % json.dumps(s["line_pointer_consumers"], ensure_ascii=False)[:300])
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