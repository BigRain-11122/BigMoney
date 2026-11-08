"""E541 -- when the published expression's shape occurs more than once, does the row's own
evidence name the occurrence, and does E540's nearest-to-anchor rule land on the same node?

E540 published one row per census row and located the published expression as an AST node: for
every row it took the nodes in the file whose AST shape equals the expression's shape and, when
there was more than one (48 of 303 located rows), picked the nearest to the published line --
preferring first the candidates inside the function that holds the published line.  That pick is
an upper bound on resolution, not a resolution: nothing checked whether it is the node the row
means.

This study asks the census row's own evidence to choose among shape-identical candidates:

  1. CANDIDATES -- the same-shape nodes E540 counted, recomputed from the file at its own cutoff
     and addressed as (lineno, col_offset).
  2. ARMS -- four constraints the row already carries, applied conjunctively in a fixed order:
       TEXT           the candidate's source segment equals the row's published expression text
                      (whitespace-normalised; ast byte offsets, per-file line cache -- never
                      ast.get_source_segment per node, which re-splits the whole file each call)
       TEXT_RENDERED  the same comparison with whitespace and quote style dropped.  This arm
                      exists because the census publishes a RE-SERIALIZED expression: string
                      literals come back single-quoted while the sources use double quotes, so
                      the strict arm refuses 46 of the 48 rows -- an absence of text evidence
                      only if you forget the text was re-rendered
       FUNCTION       the candidate sits in the function the census row names
       CONSTANT       the candidate's segment carries the constant the census row names
     An arm that would reject every surviving candidate is REFUSED for that row and published
     as such: it is evidence that the arm is miscalibrated for that row (the census row's line
     can sit in another function, as E540 measured), not evidence about the node.  The row's
     ``family_dir`` and ``class`` fields are NOT arms: family_dir is a normalised directory that
     no site spells, and class names how the family was attributed, not which node was read.
  3. DECISION -- exactly one survivor decides; more than one stays ambiguous; the arm that first
     narrowed the set to one is published, so the reader sees whose evidence did the work.
  4. AGREEMENT -- recompute E540's rule verbatim (innermost function of the published line, then
     min by (|lineno - published|, lineno)) and publish whether it lands on the decided node.
     For ambiguous rows publish whether E540's pick is at least inside the surviving set.

Nothing is executed but this measurement, no source file is rewritten, and the population is the
census face as it sits on disk at its own cutoff.

Usage:
  python scripts/e541_branch_ambiguity.py run
  python scripts/e541_branch_ambiguity.py check
  python scripts/e541_branch_ambiguity.py verify
  python scripts/e541_branch_ambiguity.py selftest
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import sys
import tempfile
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

CARD = ("E541-WHICH-OF-THE-ROWS-WHOSE-EXPRESSION-SHAPE-APPEARS-MORE-THAN-ONCE-IS-THE-NEAREST-"
        "OCCURRENCE-THE-ONE-THE-EVIDENCE-NAMES")
STUDY = "E541_branch_ambiguity"
DATE_STAMP = "2026-11-08"
FACE_NAME = "branchambiguity_latest.json"
DATED_PREFIX = "BRANCHAMBIGUITY"

UPSTREAM_FACE = "results/state_tilt/linepointer_latest.json"
CENSUS_FACE = "results/state_tilt/latestfamily_latest.json"

# how many decided rows this study needs before it is willing to call the nearest rule tested
DECIDED_FLOOR = 10

# ------------------------------------------------------------------ arm vocabulary
A_TEXT = "the_candidate_segment_equals_the_published_expression_text"
A_TEXT_RENDERED = "the_candidate_segment_equals_the_published_text_once_whitespace_and_quote_style_are_dropped"
A_FUNCTION = "the_candidate_sits_in_the_function_the_census_row_names"
A_CONSTANT = "the_candidate_segment_carries_the_constant_the_census_row_names"
ARM_VOCAB = (A_TEXT, A_TEXT_RENDERED, A_FUNCTION, A_CONSTANT)

# ------------------------------------------------------------------ decided-by vocabulary
D_TEXT = "the_expression_text_narrowed_the_candidates_to_one"
D_TEXT_RENDERED = "the_published_text_ignored_for_whitespace_and_quote_style_narrowed_them_to_one"
D_FUNCTION = "the_census_row_s_function_narrowed_the_candidates_to_one"
D_CONSTANT = "the_census_row_s_constant_narrowed_the_candidates_to_one"
D_COMBINATION = "only_the_arms_together_narrowed_the_candidates_to_one"
D_SINGLE = "the_row_carried_a_single_candidate_so_no_arm_was_needed"
D_AMBIGUOUS = "the_arms_left_more_than_one_candidate"
D_NO_CENSUS_ROW = "the_census_row_this_site_points_at_could_not_be_rejoined"
D_NO_FILE = "the_file_this_site_points_at_could_not_be_read"
D_NO_CANDIDATES = "no_node_of_the_published_shape_was_found_in_the_file"
DECIDED_VOCAB = (D_TEXT, D_TEXT_RENDERED, D_FUNCTION, D_CONSTANT, D_COMBINATION, D_SINGLE,
                 D_AMBIGUOUS, D_NO_CENSUS_ROW, D_NO_FILE, D_NO_CANDIDATES)

# ------------------------------------------------------------------ verdict vocabulary
V_AGREE = ("the_nearest_occurrence_rule_lands_on_the_node_the_evidence_decides_on_most_rows_the_"
           "evidence_can_decide")
V_DISAGREE = ("the_nearest_occurrence_rule_lands_off_the_node_the_evidence_decides_on_most_rows_"
              "the_evidence_can_decide")
V_UNTESTED = ("the_row_evidence_decides_too_few_rows_for_the_nearest_occurrence_rule_to_be_tested")
V_SINGLE = "no_row_carries_more_than_one_candidate_so_there_is_no_ambiguity_to_decide"
V_EMPTY = "the_upstream_face_published_no_ambiguous_rows"
VERDICT_VOCAB = (V_AGREE, V_DISAGREE, V_UNTESTED, V_SINGLE, V_EMPTY)

ARM_ORDER = (A_TEXT, A_TEXT_RENDERED, A_FUNCTION, A_CONSTANT)

WS_RE = re.compile(r"\s+")
QUOTE_RE = re.compile(r"['\"]")


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


def _norm(text):
    return WS_RE.sub(" ", text or "").strip()


def _shape(text):
    """Whitespace-free, quote-style-free form: what the census's own rendering preserves."""
    return WS_RE.sub("", (text or "").replace("'", '"'))


# ------------------------------------------------------------------ population

def load_json_face(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def population(line_face):
    """Every site of the upstream face whose published shape has more than one node."""
    return [dict(s) for s in line_face.get("sites") or []
            if isinstance(s.get("shape_variants"), int) and s["shape_variants"] > 1]


def census_index(census):
    """(file, line, kind) -> the census rows that published that line."""
    index = {}
    for key, kind in (("read_sites", "read"), ("write_sites", "write")):
        for row in census.get(key) or []:
            index.setdefault((row.get("file"), row.get("line"), kind), []).append(row)
    return index


def rejoin(site, index):
    """The census row a site points at, or None when the join finds nothing unique."""
    kind = "read" if site.get("published_in") == "read_sites" else "write"
    rows = index.get((site.get("file"), site.get("published_line"), kind)) or []
    if not rows:
        return None, None
    keys = {(r.get("function"), (r.get("evidence") or {}).get("constant")) for r in rows}
    if len(keys) > 1:
        return None, "the_census_rows_at_that_line_disagree_on_function_or_constant"
    return rows[0], None


# ------------------------------------------------------------------ file index

def _splitlines_no_ff(source):
    """ast's own line splitter: form feed and lone CR do not start a new line."""
    idx = 0
    lines = []
    next_line = ""
    while idx < len(source):
        c = source[idx]
        next_line += c
        idx += 1
        if c == "\r" and idx < len(source) and source[idx] == "\n":
            next_line += "\n"
            idx += 1
        if c in "\r\n":
            lines.append(next_line)
            next_line = ""
    if next_line:
        lines.append(next_line)
    return lines


def _span(node):
    return (node.lineno, getattr(node, "end_lineno", None) or node.lineno)


def file_index(root, rel, cache):
    """AST view of one file plus the byte lines needed to cut a node's own source text once."""
    if rel in cache:
        return cache[rel]
    path = os.path.join(root, rel)
    entry = {"lines": [], "bytes": [], "by_shape": {}, "funcs": [], "errors": []}
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except (OSError, UnicodeDecodeError) as exc:
        entry["errors"].append("unreadable: %s" % exc.__class__.__name__)
        cache[rel] = entry
        return entry
    entry["lines"] = _splitlines_no_ff(text)
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError) as exc:
        entry["errors"].append("unparseable: %s" % exc.__class__.__name__)
        cache[rel] = entry
        return entry
    for node in ast.walk(tree):
        if isinstance(node, ast.expr):
            entry["by_shape"].setdefault(
                ast.dump(node, include_attributes=False), []).append(node)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            entry["funcs"].append((node.lineno, getattr(node, "end_lineno", None) or node.lineno,
                                   node.name))
    cache[rel] = entry
    return entry


def _bytes(lines, lineno):
    """UTF-8 bytes of one cached line; ast column offsets are byte offsets."""
    return lines[lineno - 1].encode("utf-8")


def segment(index, node):
    """The node's own source text, cut from cached lines (one slice, not a whole-file re-split)."""
    lineno = getattr(node, "lineno", None)
    col = getattr(node, "col_offset", None)
    end_lineno = getattr(node, "end_lineno", None)
    end_col = getattr(node, "end_col_offset", None)
    if lineno is None or col is None or end_lineno is None or end_col is None:
        return None
    lines = index["lines"]
    if end_lineno > len(lines) or lineno < 1:
        return None
    if lineno == end_lineno:
        return _bytes(lines, lineno)[col:end_col].decode("utf-8", "replace")
    parts = [_bytes(lines, lineno)[col:]]
    for i in range(lineno + 1, end_lineno):
        parts.append(_bytes(lines, i))
    parts.append(_bytes(lines, end_lineno)[:end_col])
    return b"".join(parts).decode("utf-8", "replace")


def _innermost_func(index, line):
    best = None
    for start, end, name in index["funcs"]:
        if start <= line <= end and (best is None or end - start < best[1] - best[0]):
            best = (start, end, name)
    return best


def candidate_rows(index, expr, published):
    """Every node of the published expression's shape, with the evidence each candidate offers."""
    try:
        target = ast.parse(expr or "", mode="eval").body
    except (SyntaxError, ValueError):
        return None
    nodes = index["by_shape"].get(ast.dump(target, include_attributes=False)) or []
    out = []
    for node in nodes:
        fn = _innermost_func(index, node.lineno)
        out.append({
            "line": node.lineno,
            "col": node.col_offset,
            "end_line": getattr(node, "end_lineno", None),
            "function": fn[2] if fn else "<module>",
            "text": _norm(segment(index, node)),
        })
    return out


def nearest_candidate(cands, published, index):
    """E540's rule, recomputed verbatim: the published line's function first, then nearest."""
    if not cands:
        return None
    fn = _innermost_func(index, published)
    inside = [c for c in cands if fn and fn[0] <= c["line"] <= fn[1]]
    pool = inside or cands
    return min(pool, key=lambda c: (abs(c["line"] - published), c["line"]))


# ------------------------------------------------------------------ arms

def _arm_survivors(arm, cands, expr_text, function_name, constant):
    if arm == A_TEXT:
        if not expr_text:
            return None
        return [c for c in cands if c["text"] == _norm(expr_text)]
    if arm == A_TEXT_RENDERED:
        if not expr_text:
            return None
        want = _shape(expr_text)
        return [c for c in cands if _shape(c["text"]) == want]
    if arm == A_FUNCTION:
        if function_name is None:
            return None
        return [c for c in cands if c["function"] == function_name]
    if arm == A_CONSTANT:
        if not constant:
            return None
        token = _norm(constant)
        return [c for c in cands if token and token in (c["text"] or "")]
    raise AssertionError("unknown arm %r" % (arm,))


def apply_arms(cands, expr_text, function_name, constant):
    """Apply each arm in order; an arm that would empty the set is refused and recorded."""
    trace = []
    survivors = list(cands)
    narrowed_by = None
    for arm in ARM_ORDER:
        before = len(survivors)
        got = _arm_survivors(arm, survivors, expr_text, function_name, constant)
        if got is None:
            trace.append({"arm": arm, "state": "not_applicable", "before": before,
                          "after": before})
            continue
        if not got:
            trace.append({"arm": arm, "state": "refused_because_it_rejects_every_candidate",
                          "before": before, "after": before,
                          "would_have_left": 0})
            continue
        survivors = got
        trace.append({"arm": arm, "state": "applied", "before": before, "after": len(got)})
        if len(got) == 1 and narrowed_by is None and before > 1:
            narrowed_by = arm
    return survivors, trace, narrowed_by


def _decided_by(survivors, trace, narrowed_by, cands):
    if not cands:
        return D_NO_CANDIDATES
    if len(cands) == 1:
        return D_SINGLE
    if len(survivors) != 1:
        return D_AMBIGUOUS
    if narrowed_by == A_TEXT:
        return D_TEXT
    if narrowed_by == A_TEXT_RENDERED:
        return D_TEXT_RENDERED
    if narrowed_by == A_FUNCTION:
        return D_FUNCTION
    if narrowed_by == A_CONSTANT:
        return D_CONSTANT
    if narrowed_by is None:
        return D_COMBINATION
    return D_COMBINATION


def analyse_site(site, census_row, root, cache):
    rel = site.get("file")
    published = site.get("published_line")
    out = {
        "site": site.get("site") or ("%s:%s" % (rel, published)),
        "file": rel,
        "published_line": published,
        "published_in": site.get("published_in"),
        "tier": site.get("tier"),
        "class": site.get("class"),
        "expr": site.get("expr"),
        "expression_span": site.get("expression_span"),
        "shape_variants": site.get("shape_variants"),
        "census_function": (census_row or {}).get("function"),
        "census_constant": ((census_row or {}).get("evidence") or {}).get("constant"),
        "census_family_dir": ((census_row or {}).get("evidence") or {}).get("family_dir"),
        "census_rejoin_note": site.get("census_rejoin_note"),
        "candidates": [],
        "arm_trace": [],
        "survivors": [],
        "decided_by": None,
        "decided_node": None,
        "nearest_node": None,
        "nearest_agrees_with_the_decision": None,
        "nearest_is_inside_the_surviving_set": None,
    }
    if census_row is None:
        out["decided_by"] = D_NO_CENSUS_ROW
        return out
    if not rel or not isinstance(published, int):
        out["decided_by"] = D_NO_FILE
        return out
    index = file_index(root, rel, cache)
    if index["errors"]:
        out["decided_by"] = D_NO_FILE
        out["index_errors"] = list(index["errors"])
        return out
    cands = candidate_rows(index, site.get("expr") or "", published)
    if cands is None:
        out["decided_by"] = D_NO_CANDIDATES
        out["index_errors"] = ["the_published_expression_does_not_parse"]
        return out
    out["candidates"] = cands
    if not cands:
        out["decided_by"] = D_NO_CANDIDATES
        return out
    survivors, trace, narrowed_by = apply_arms(
        cands, site.get("expr"), out["census_function"], out["census_constant"])
    out["arm_trace"] = trace
    out["survivors"] = [{"line": c["line"], "col": c["col"], "function": c["function"]}
                        for c in survivors]
    out["decided_by"] = _decided_by(survivors, trace, narrowed_by, cands)
    if len(survivors) == 1:
        out["decided_node"] = {"line": survivors[0]["line"], "col": survivors[0]["col"],
                               "function": survivors[0]["function"]}
    nearest = nearest_candidate(cands, published, index)
    out["nearest_node"] = {"line": nearest["line"], "col": nearest["col"],
                           "function": nearest["function"]} if nearest else None
    if out["decided_node"] is not None:
        out["nearest_agrees_with_the_decision"] = (
            (nearest["line"], nearest["col"])
            == (out["decided_node"]["line"], out["decided_node"]["col"]))
    out["nearest_is_inside_the_surviving_set"] = any(
        (nearest["line"], nearest["col"]) == (c["line"], c["col"]) for c in survivors)
    return out


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
    if summary["rows_with_a_single_candidate"] == summary["rows"]:
        return V_SINGLE
    if summary["rows_decided"] < DECIDED_FLOOR:
        return V_UNTESTED
    if summary["nearest_agrees_with_the_decision"] * 2 >= summary["rows_decided"]:
        return V_AGREE
    return V_DISAGREE


def analyse(sites, census_rows, root=None):
    root = root or ROOT
    cache = {}
    return [analyse_site(site, census_rows[i], root, cache)
            for i, site in enumerate(sites)]


def pairs_from_faces(root=None):
    """The population and its census rows, read fresh from the two faces on disk."""
    root = root or ROOT
    line_face = load_json_face(os.path.join(root, UPSTREAM_FACE))
    census = load_json_face(os.path.join(root, CENSUS_FACE))
    index = census_index(census)
    pairs = []
    for site in population(line_face):
        row, reason = rejoin(site, index)
        if reason:
            site = dict(site, census_rejoin_note=reason)
        pairs.append((site, row))
    return (pairs,
            _sha256_file(os.path.join(root, UPSTREAM_FACE)),
            _sha256_file(os.path.join(root, CENSUS_FACE)))


def build(root=None, write=True, pairs=None, upstream_sha=None, census_sha=None):
    root = root or ROOT
    if pairs is None:
        pairs, upstream_sha, census_sha = pairs_from_faces(root)
    sites = [p[0] for p in pairs]
    census_rows = [p[1] for p in pairs]
    analysed = analyse(sites, census_rows, root)
    decided_by = _count([s["decided_by"] for s in analysed], DECIDED_VOCAB)
    decided = [s for s in analysed if s.get("decided_node") is not None]
    ambiguous = [s for s in analysed if s["decided_by"] == D_AMBIGUOUS]
    arms = {}
    for arm in ARM_ORDER:
        applied = refused = decided_here = 0
        for site in analysed:
            for step in site["arm_trace"]:
                if step["arm"] != arm:
                    continue
                if step["state"] == "applied":
                    applied += 1
                    if step["before"] > 1 and step["after"] == 1:
                        decided_here += 1
                elif step["state"].startswith("refused"):
                    refused += 1
        arms[arm] = {"applied": applied, "refused_because_it_rejects_every_candidate": refused,
                     "narrowed_the_row_to_one": decided_here}
    agrees = sum(1 for s in decided if s.get("nearest_agrees_with_the_decision") is True)
    disagrees = sum(1 for s in decided if s.get("nearest_agrees_with_the_decision") is False)
    summary = {
        "rows": len(analysed),
        "rows_with_a_single_candidate": decided_by[D_SINGLE],
        "rows_decided": len(decided),
        "rows_ambiguous": len(ambiguous),
        "rows_with_no_census_row": decided_by[D_NO_CENSUS_ROW],
        "rows_with_no_readable_file": decided_by[D_NO_FILE],
        "rows_with_no_candidate": decided_by[D_NO_CANDIDATES],
        "decided_by": decided_by,
        "arms": arms,
        "candidates_overall": sum(len(s["candidates"]) for s in analysed),
        "candidates_left_overall": sum(len(s["survivors"]) for s in analysed),
        "arms_refused_overall": sum(v["refused_because_it_rejects_every_candidate"]
                                    for v in arms.values()),
        "nearest_agrees_with_the_decision": agrees,
        "nearest_disagrees_with_the_decision": disagrees,
        "ambiguous_rows_where_nearest_is_inside_the_surviving_set": sum(
            1 for s in ambiguous if s.get("nearest_is_inside_the_surviving_set") is True),
        "ambiguous_rows_where_nearest_is_outside_the_surviving_set": sum(
            1 for s in ambiguous if s.get("nearest_is_inside_the_surviving_set") is False),
        "decided_plus_ambiguous_sums_to_the_rows": (
            len(decided) + len(ambiguous) + decided_by[D_NO_CENSUS_ROW] + decided_by[D_NO_FILE]
            + decided_by[D_NO_CANDIDATES] == len(analysed)),
    }
    summary["decided_share"] = (round(len(decided) / float(len(analysed)), 4)
                               if analysed else None)
    summary["rows_addressed_by_the_evidence"] = len(decided) + len(
        [s for s in ambiguous
         if s.get("nearest_is_inside_the_surviving_set") is True])
    return {
        "card": CARD,
        "study": STUDY,
        "question": ("when the published expression's shape occurs more than once in the file, "
                     "does the census row's own evidence pick the occurrence, and does E540's "
                     "nearest-to-anchor rule pick the same node?"),
        "evidence_cutoff": DATE_STAMP,
        "generated": _now(),
        "population_source": ("%s::population() -- every site of the upstream face whose "
                             "shape_variants is greater than one, rejoined to the census row "
                             "that published the same file+line+kind" % os.path.basename(__file__)),
        "upstream_face": UPSTREAM_FACE if pairs is None or upstream_sha else "caller-supplied rows",
        "upstream_sha256": upstream_sha,
        "census_face": CENSUS_FACE if pairs is None or census_sha else "caller-supplied rows",
        "census_sha256": census_sha,
        "arm_vocab": list(ARM_VOCAB),
        "decided_by_vocab": list(DECIDED_VOCAB),
        "verdict_vocab": list(VERDICT_VOCAB),
        "decided_floor": DECIDED_FLOOR,
        "summary": summary,
        "verdict": _verdict(summary),
        "sites": analysed,
        "method_limits": [
            "the arms are three constraints the census row happens to carry; a row whose evidence "
            "is wrong narrows the candidates to the wrong node and this study cannot tell -- it "
            "measures whether the evidence decides, not whether the evidence is right",
            "an arm that would reject every surviving candidate is refused for that row, so a row "
            "can stay ambiguous when its evidence is present but miscalibrated; the refusal is "
            "published per row and per arm rather than being silently dropped",
            "candidate identity is (lineno, col_offset) at the face's own cutoff; a file edited "
            "since the upstream face was published would shift both sides and the row would be "
            "published with no candidate instead of being silently re-located",
            "the text arm compares whitespace-normalised source segments and is therefore blind "
            "to two candidates that differ only in line breaks or in quote style",
            "the census's own expr is a re-serialized rendering rather than the source text, so "
            "the strict text arm refuses almost every row and the rendered arm carries the text "
            "evidence; both arms are published separately so the refusal is not read as absence",
            "the rendered arm drops every apostrophe and every whitespace character before "
            "comparing, so two candidates that differ only inside a string literal's spacing are "
            "indistinguishable to it",
            "the population is the upstream face's ambiguous rows only; the 255 rows E540 located "
            "unambiguously are outside this measurement by construction",
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
    for key in ("card", "question", "evidence_cutoff", "population_source", "arm_vocab",
                "decided_by_vocab", "verdict_vocab", "summary", "verdict", "sites",
                "method_limits"):
        if key not in face:
            problems.append("missing key %s" % key)
    if problems:
        return problems
    summary, sites = face["summary"], face["sites"]
    if summary["rows"] != len(sites):
        problems.append("rows does not equal the site rows")
    decided_by = _count([s.get("decided_by") for s in sites], face["decided_by_vocab"])
    if decided_by != summary["decided_by"]:
        problems.append("decided_by does not re-derive from the sites")
    if sum(decided_by.values()) != len(sites):
        problems.append("a site carries a decided_by outside the vocabulary")
    for site in sites:
        if site.get("decided_by") not in face["decided_by_vocab"]:
            problems.append("site %s carries decided_by %r"
                            % (site.get("site"), site.get("decided_by")))
    decided = [s for s in sites if s.get("decided_node") is not None]
    if summary["rows_decided"] != len(decided):
        problems.append("rows_decided does not re-derive from the sites")
    if summary["rows_ambiguous"] != decided_by[D_AMBIGUOUS]:
        problems.append("rows_ambiguous does not re-derive")
    if summary["rows_with_a_single_candidate"] != decided_by[D_SINGLE]:
        problems.append("rows_with_a_single_candidate does not re-derive")
    if summary["candidates_overall"] != sum(len(s.get("candidates") or []) for s in sites):
        problems.append("candidates_overall does not re-derive")
    if summary["candidates_left_overall"] != sum(len(s.get("survivors") or []) for s in sites):
        problems.append("candidates_left_overall does not re-derive")
    arms = {}
    for arm in face["arm_vocab"]:
        applied = refused = narrowed = 0
        for site in sites:
            for step in site.get("arm_trace") or []:
                if step.get("arm") != arm:
                    continue
                if step.get("state") == "applied":
                    applied += 1
                    if step.get("before", 0) > 1 and step.get("after") == 1:
                        narrowed += 1
                elif str(step.get("state", "")).startswith("refused"):
                    refused += 1
        arms[arm] = {"applied": applied,
                     "refused_because_it_rejects_every_candidate": refused,
                     "narrowed_the_row_to_one": narrowed}
    if arms != summary["arms"]:
        problems.append("arms do not re-derive from the site traces")
    if summary["arms_refused_overall"] != sum(
            v["refused_because_it_rejects_every_candidate"] for v in arms.values()):
        problems.append("arms_refused_overall does not re-derive")
    agrees = sum(1 for s in decided if s.get("nearest_agrees_with_the_decision") is True)
    if summary["nearest_agrees_with_the_decision"] != agrees:
        problems.append("nearest_agrees_with_the_decision does not re-derive")
    if summary["nearest_disagrees_with_the_decision"] != len(decided) - agrees:
        problems.append("nearest_disagrees_with_the_decision does not re-derive")
    ambiguous = [s for s in sites if s.get("decided_by") == D_AMBIGUOUS]
    if summary["ambiguous_rows_where_nearest_is_inside_the_surviving_set"] != sum(
            1 for s in ambiguous if s.get("nearest_is_inside_the_surviving_set") is True):
        problems.append("ambiguous_rows_where_nearest_is_inside_the_surviving_set "
                        "does not re-derive")
    if summary["ambiguous_rows_where_nearest_is_outside_the_surviving_set"] != sum(
            1 for s in ambiguous if s.get("nearest_is_inside_the_surviving_set") is False):
        problems.append("ambiguous_rows_where_nearest_is_outside_the_surviving_set "
                        "does not re-derive")
    if summary["decided_plus_ambiguous_sums_to_the_rows"] != (
            len(decided) + len(ambiguous) + decided_by[D_NO_CENSUS_ROW]
            + decided_by[D_NO_FILE] + decided_by[D_NO_CANDIDATES] == len(sites)):
        problems.append("decided_plus_ambiguous_sums_to_the_rows does not re-derive")
    if face["verdict"] != _verdict(summary):
        problems.append("verdict does not re-derive from the summary")
    if face["verdict"] not in face["verdict_vocab"]:
        problems.append("verdict is outside the vocabulary")
    for site in sites:
        if site.get("decided_by") == D_AMBIGUOUS and len(site.get("survivors") or []) < 2:
            problems.append("site %s is ambiguous with fewer than two survivors"
                            % site.get("site"))
        if site.get("decided_node") is not None and not any(
                (site["decided_node"]["line"], site["decided_node"]["col"])
                == (c["line"], c["col"]) for c in site.get("survivors") or []):
            problems.append("site %s decided a node that is not a survivor" % site.get("site"))
        if site.get("decided_node") is not None and site.get("candidates") and not any(
                (site["decided_node"]["line"], site["decided_node"]["col"])
                == (c["line"], c["col"]) for c in site["candidates"]):
            problems.append("site %s decided a node that is not a candidate" % site.get("site"))
        if site.get("decided_node") is not None and site.get("nearest_agrees_with_the_decision") is None:
            problems.append("site %s decided without comparing the nearest rule"
                            % site.get("site"))
    return problems


def check(root=None, face=None):
    face = face or load_face(root)
    problems = face_problems(face)
    print("check: problems=%s" % json.dumps(problems, ensure_ascii=False)[:600])
    return 0 if not problems else 1


def verify(root=None):
    face = load_face(root)
    pairs, upstream_sha, census_sha = pairs_from_faces(root)
    rebuilt = build(root, write=False, pairs=pairs,
                    upstream_sha=upstream_sha, census_sha=census_sha)
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

# Every fixture node has the SAME AST shape -- same call, same name, same constant value -- and
# differs only in quote style and whitespace, which is exactly the ambiguity E541 measures: a shape
# match cannot separate them and the row's text can (until whitespace normalisation collapses two
# of them, which is the limit the face publishes).
FIXTURE_SRC = (
    "import os\n"                                                  # 1
    "def alpha(root):\n"                                           # 2
    "    return os.path.join(root, 'thing_latest.json')\n"         # 3
    "\n"                                                           # 4
    "def beta(root):\n"                                            # 5
    "    return os.path.join(root, \"thing_latest.json\")\n"       # 6
    "\n"                                                           # 7
    "def gamma(root):\n"                                           # 8
    "    path = os.path.join(root,\n"                              # 9
    "        \"thing_latest.json\")\n"                             # 10
    "    return path\n"                                            # 11
)

SINGLE_SRC = (
    "import os\n"                                                  # 1
    "def solo(root):\n"                                            # 2
    "    return os.path.join(root, 'only_latest.json')\n"          # 3
)

EXPR_SINGLE = "os.path.join(root, 'thing_latest.json')"
EXPR_DOUBLE = 'os.path.join(root, "thing_latest.json")'


def _site(line, expr, variants=3, file="fixture.py"):
    return {"file": file, "published_line": line, "published_in": "read_sites",
            "site": "%s:%s" % (file, line), "tier": "fixture", "class": "fixture",
            "expr": expr, "shape_variants": variants}


def _census(function, constant):
    return {"function": function, "evidence": {"constant": constant,
                                               "family_dir": "data/thing"}}


def _fixture_pairs():
    return [
        # only line 3 spells the expression with single quotes: the text arm decides it
        (_site(3, EXPR_SINGLE), _census("alpha", "root")),
        # text leaves {6, 10} (whitespace collapses); the census function decides line 10
        (_site(10, EXPR_DOUBLE), _census("gamma", "root")),
        # same evidence at a module-level line: function decides 10, nearest rule picks 6
        (_site(7, EXPR_DOUBLE), _census("gamma", "root")),
        # the census function names no candidate -> arm refused, row stays ambiguous,
        # and the nearest rule lands on line 3, which the text arm excluded
        (_site(3, EXPR_DOUBLE), _census("alpha", "root")),
        # no census row at all
        (_site(3, EXPR_SINGLE), None),
        # unreadable file
        (_site(3, EXPR_SINGLE, file="missing.py"), _census("alpha", "root")),
        # expression that does not parse
        (_site(3, "nowhere(x)"), _census("alpha", "root")),
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
        with open(os.path.join(tmp, "fixture_single.py"), "w", encoding="utf-8",
                  newline="\n") as fh:
            fh.write(SINGLE_SRC)
        pairs = _fixture_pairs()
        face = build(root=tmp, write=False, pairs=pairs)
        sites = face["sites"]
        arm("every fixture row is analysed", len(sites) == len(pairs),
            "%s of %s" % (len(sites), len(pairs)))
        arm("the same-shape nodes are found three times",
            [c["line"] for c in sites[0]["candidates"]] == [3, 6, 9],
            json.dumps([c["line"] for c in sites[0]["candidates"]]))
        arm("a quote style the other candidates do not spell decides the row by text",
            sites[0]["decided_by"] == D_TEXT
            and (sites[0]["decided_node"]["line"], sites[0]["decided_node"]["col"]) == (3, 11),
            json.dumps({"by": sites[0]["decided_by"], "node": sites[0]["decided_node"]}))
        arm("whitespace normalisation leaves two candidates and the function decides",
            sites[1]["decided_by"] == D_FUNCTION
            and sites[1]["decided_node"]["line"] == 9
            and len(sites[1]["survivors"]) == 1,
            json.dumps({"by": sites[1]["decided_by"], "node": sites[1]["decided_node"]}))
        arm("the nearest rule agrees when the decision sits under the published line",
            sites[1]["nearest_agrees_with_the_decision"] is True,
            json.dumps(sites[1]["nearest_node"]))
        arm("the nearest rule can pick a node the evidence excludes",
            sites[2]["decided_by"] == D_FUNCTION
            and sites[2]["nearest_agrees_with_the_decision"] is False
            and sites[2]["nearest_node"]["line"] == 6,
            json.dumps({"decided": sites[2]["decided_node"],
                        "nearest": sites[2]["nearest_node"]}))
        arm("an arm that rejects every candidate is refused, not applied",
            any(step["arm"] == A_FUNCTION and step["state"].startswith("refused")
                for step in sites[3]["arm_trace"]),
            json.dumps(sites[3]["arm_trace"]))
        arm("a refused arm leaves the row ambiguous",
            sites[3]["decided_by"] == D_AMBIGUOUS and len(sites[3]["survivors"]) == 2,
            json.dumps({"by": sites[3]["decided_by"],
                        "survivors": len(sites[3]["survivors"])}))
        arm("the nearest rule can land outside the surviving set",
            sites[3]["nearest_is_inside_the_surviving_set"] is False
            and sites[3]["nearest_node"]["line"] == 3,
            json.dumps(sites[3]["nearest_node"]))
        arm("a row with no census row is published as such",
            sites[4]["decided_by"] == D_NO_CENSUS_ROW, sites[4]["decided_by"])
        arm("an unreadable file is published as such",
            sites[5]["decided_by"] == D_NO_FILE, sites[5]["decided_by"])
        arm("an unparseable expression is published with no candidate",
            sites[6]["decided_by"] == D_NO_CANDIDATES, sites[6]["decided_by"])
        arm("the decided and ambiguous rows plus the unresolvable ones sum to the rows",
            face["summary"]["decided_plus_ambiguous_sums_to_the_rows"] is True,
            json.dumps(face["summary"]))
        arm("a built fixture face passes its own gate", face_problems(face) == [],
            json.dumps(face_problems(face), ensure_ascii=False)[:400])

        doctored = json.loads(json.dumps(face))
        doctored["verdict"] = "a_verdict_this_study_never_publishes"
        arm("a hand-written verdict is refused", bool(face_problems(doctored)))

        doctored = json.loads(json.dumps(face))
        doctored["sites"][3]["decided_by"] = D_TEXT
        arm("an ambiguity relabelled as a decision is refused", bool(face_problems(doctored)))

        doctored = json.loads(json.dumps(face))
        doctored["sites"][1]["decided_node"] = {"line": 6, "col": 11, "function": "beta"}
        arm("a decision that is not a survivor is refused", bool(face_problems(doctored)))

        doctored = json.loads(json.dumps(face))
        doctored["summary"]["arms"][A_FUNCTION]["refused_because_it_rejects_every_candidate"] += 1
        arm("an inflated refusal count is refused", bool(face_problems(doctored)))

        doctored = json.loads(json.dumps(face))
        doctored["summary"]["nearest_disagrees_with_the_decision"] += 1
        arm("an inflated disagreement count is refused", bool(face_problems(doctored)))

        single = build(root=tmp, write=False,
                       pairs=[(_site(3, "os.path.join(root, 'only_latest.json')", variants=1,
                                    file="fixture_single.py"), _census("solo", "root"))])
        arm("a single-candidate population publishes the single verdict",
            single["verdict"] == V_SINGLE
            and single["summary"]["rows_with_a_single_candidate"] == 1,
            json.dumps({"verdict": single["verdict"],
                        "single": single["summary"]["rows_with_a_single_candidate"]}))

    one = [{"text": 'os.path.join(root, "thing_latest.json")'}]
    arm("the strict text arm refuses the census's single-quoted re-rendering",
        _arm_survivors(A_TEXT, one, "os.path.join(root, 'thing_latest.json')", None, None) == [],
        json.dumps(_arm_survivors(A_TEXT, one, "os.path.join(root, 'thing_latest.json')",
                                  None, None)))
    arm("the rendered arm keeps the candidate the census re-rendering describes",
        len(_arm_survivors(A_TEXT_RENDERED, one, "os.path.join(root, 'thing_latest.json')",
                           None, None)) == 1,
        json.dumps(len(_arm_survivors(A_TEXT_RENDERED, one,
                                      "os.path.join(root, 'thing_latest.json')", None, None))))

    arm("an empty population publishes the empty verdict",
        build(root=ROOT, write=False, pairs=[])["verdict"] == V_EMPTY)
    print("selftest: %d arms, %d failed" % (26, len(failures)))
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
        print("run: rows=%s decided=%s ambiguous=%s single=%s"
              % (s["rows"], s["rows_decided"], s["rows_ambiguous"],
                 s["rows_with_a_single_candidate"]))
        print("run: decided_by=%s" % json.dumps(s["decided_by"], ensure_ascii=False))
        print("run: arms=%s" % json.dumps(s["arms"], ensure_ascii=False))
        print("run: nearest agrees=%s disagrees=%s | ambiguous inside=%s outside=%s"
              % (s["nearest_agrees_with_the_decision"],
                 s["nearest_disagrees_with_the_decision"],
                 s["ambiguous_rows_where_nearest_is_inside_the_surviving_set"],
                 s["ambiguous_rows_where_nearest_is_outside_the_surviving_set"]))
        print("run: candidates %s -> %s" % (s["candidates_overall"],
                                            s["candidates_left_overall"]))
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