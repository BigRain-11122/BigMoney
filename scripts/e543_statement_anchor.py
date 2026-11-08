"""E543 -- can the line the census already publishes close E542's ambiguity by itself?

E542 resolved every surviving candidate of the 32 ambiguous rows to the context a reader sees and
found that on all 32 rows the survivors sit in different statements: the published line is not
enough to tell the row apart by function, but the *statement* does differ from survivor to survivor.
That raises a zero-cost question the census never asked:

    read the published line as a statement anchor -- keep only the survivors whose innermost
    statement's opening line is the published line.

E543 applies exactly that one rule and publishes what it decides:

    decided    exactly one survivor sits in the statement that opens on the published line
    ambiguous  two or more survivors sit in that statement
    refused    no survivor sits in it, so the rule would empty the row and must be refused
    no_context a survivor carries no statement line to anchor on

For every decided row it also publishes whether the survivor the statement anchor picks is the same
node E540's nearest-to-published rule picked, recomputed through E541's own implementation of that
rule rather than re-written here.  The point is not to propose a new locator but to measure whether
the ambiguity can be closed by a field the census already publishes.

Nothing is executed but this measurement, no source file is rewritten, and the population is the
upstream face recomputed from the two faces on disk rather than copied from a card.

Usage:
  python scripts/e543_statement_anchor.py run
  python scripts/e543_statement_anchor.py check
  python scripts/e543_statement_anchor.py verify
  python scripts/e543_statement_anchor.py selftest
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e541_branch_ambiguity as e541  # noqa: E402  (E540's rule lives there, recomputed verbatim)
import e542_survivor_spans as e542  # noqa: E402  (the ambiguity population is E542's)

CARD = ("E543-WHICH-SURVIVORS-THE-PUBLISHED-LINE-ITSELF-SELECTS-WHEN-IT-IS-READ-AS-A-STATEMENT-ANCHOR")
STUDY = "E543_statement_anchor"
DATE_STAMP = "2026-11-08"
FACE_NAME = "statementanchor_latest.json"
DATED_PREFIX = "STATEMENTANCHOR"

UPSTREAM_FACE = "results/state_tilt/survivorspans_latest.json"

# ------------------------------------------------------------------ class vocabulary
C_DECIDED = "the_published_statement_line_selects_exactly_one_survivor"
C_AMBIGUOUS = "more_than_one_survivor_sits_in_the_statement_the_published_line_opens"
C_EMPTY = "no_survivor_sits_in_the_statement_the_published_line_opens_so_the_rule_would_refuse"
C_NO_CONTEXT = "a_survivor_carries_no_statement_line_to_anchor_on"
CLASSES = (C_DECIDED, C_AMBIGUOUS, C_EMPTY, C_NO_CONTEXT)

# ------------------------------------------------------------------ verdict vocabulary
V_CLOSED = ("the_published_line_is_already_a_statement_anchor_that_decides_most_ambiguous_rows_at_"
            "no_cost")
V_AMBIGUOUS = ("the_published_line_leaves_most_ambiguous_rows_ambiguous_because_several_survivors_"
               "open_in_the_same_statement")
V_REFUSED = ("reading_the_published_line_as_a_statement_anchor_would_empty_most_ambiguous_rows_"
             "because_no_survivor_sits_in_it")
V_MIXED = ("the_ambiguous_rows_split_between_decided_ambiguity_kept_and_rows_the_rule_would_empty")
V_EMPTY = "the_upstream_face_published_no_ambiguous_rows"
VERDICT_VOCAB = (V_CLOSED, V_AMBIGUOUS, V_REFUSED, V_MIXED, V_EMPTY)

E540_READ = "the_file_was_read_so_e540_s_rule_has_an_opinion"
E540_UNREADABLE = "the_file_could_not_be_read_so_e540_s_rule_has_no_opinion"
E540_NO_SURVIVORS = "the_row_carries_no_survivors_for_e540_s_rule_to_choose_between"
PICK_SOURCES = (E540_READ, E540_UNREADABLE, E540_NO_SURVIVORS)


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


# ------------------------------------------------------------------ the rule

def select_survivors(survivors, published):
    """Pure: the survivors whose innermost statement opens on the published line."""
    if not isinstance(published, int):
        return []
    return [s for s in survivors if s.get("statement_line") == published]


def _classify(survivors, selected):
    if any(not isinstance(s.get("statement_line"), int) for s in survivors):
        return C_NO_CONTEXT
    if len(selected) == 1:
        return C_DECIDED
    if len(selected) > 1:
        return C_AMBIGUOUS
    return C_EMPTY


def e540_pick(survivors, published, rel, root, cache):
    """E540's nearest-to-published rule through E541's own implementation."""
    if not survivors:
        return None, E540_NO_SURVIVORS
    if not rel:
        return None, E540_UNREADABLE
    index = e541.file_index(root, rel, cache)
    if index.get("errors"):
        return None, E540_UNREADABLE
    cands = [{"line": s.get("line"), "col": s.get("col"), "function": s.get("function")}
             for s in survivors]
    pick = e541.nearest_candidate(cands, published, index)
    if pick is None:
        return None, E540_UNREADABLE
    return {"line": pick.get("line"), "col": pick.get("col"),
            "function": pick.get("function")}, E540_READ


def analyse_site(site, root, cache):
    rel = site.get("file")
    published = site.get("published_line")
    survivors = site.get("survivors") or []
    selected = select_survivors(survivors, published)
    selected_keys = {(s.get("line"), s.get("col")) for s in selected}
    out = {
        "site": site.get("site"),
        "file": rel,
        "published_line": published,
        "tier": site.get("tier"),
        "expr": site.get("expr"),
        "survivor_count": len(survivors),
        "survivors_in_the_published_statement": [
            {"line": s.get("line"), "col": s.get("col"),
             "statement_kind": s.get("statement_kind"), "statement_line": s.get("statement_line")}
            for s in selected],
        "survivors_ruled_out": [
            {"line": s.get("line"), "col": s.get("col"),
             "statement_kind": s.get("statement_kind"), "statement_line": s.get("statement_line")}
            for s in survivors if (s.get("line"), s.get("col")) not in selected_keys],
        "selected_count": len(selected),
        "class": None,
        "published_line_opens_a_statement_a_survivor_sits_in": bool(selected),
        "e540_pick": None,
        "e540_pick_source": None,
        "agrees_with_e540": None,
    }
    out["class"] = _classify(survivors, selected)
    pick, source = e540_pick(survivors, published, rel, root, cache)
    out["e540_pick"] = pick
    out["e540_pick_source"] = source
    if out["class"] == C_DECIDED and pick is not None:
        chosen = selected[0]
        out["agrees_with_e540"] = ((pick.get("line"), pick.get("col"))
                                   == (chosen.get("line"), chosen.get("col")))
    return out


def analyse(sites, root=None):
    root = root or ROOT
    cache = {}
    return [analyse_site(site, root, cache) for site in sites]


# ------------------------------------------------------------------ population

def ambiguous_sites(root=None):
    """Recompute E542 from the faces on disk and keep every row it published."""
    root = root or ROOT
    face = e542.build(root=root, write=False)
    return [dict(s) for s in face.get("sites") or []], _sha256_file(
        os.path.join(root, UPSTREAM_FACE))


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
    rows = summary["rows"]
    if summary["rows_decided_by_the_statement_anchor"] * 2 > rows:
        return V_CLOSED
    if summary["rows_the_statement_anchor_would_refuse_to_empty"] * 2 > rows:
        return V_REFUSED
    if summary["rows_that_stay_ambiguous_inside_the_published_statement"] * 2 > rows:
        return V_AMBIGUOUS
    return V_MIXED


def build(root=None, write=True, sites=None, upstream_sha=None):
    root = root or ROOT
    if sites is None:
        sites, upstream_sha = ambiguous_sites(root)
    analysed = analyse(sites, root)
    classes = _count([s["class"] for s in analysed], CLASSES)
    decided = [s for s in analysed if s["class"] == C_DECIDED]
    compared = [s for s in decided if s["agrees_with_e540"] is not None]
    summary = {
        "rows": len(analysed),
        "class": classes,
        "rows_decided_by_the_statement_anchor": classes[C_DECIDED],
        "rows_that_stay_ambiguous_inside_the_published_statement": classes[C_AMBIGUOUS],
        "rows_the_statement_anchor_would_refuse_to_empty": classes[C_EMPTY],
        "rows_with_a_survivor_that_carries_no_statement_line": classes[C_NO_CONTEXT],
        "rows_whose_published_line_opens_a_statement_a_survivor_sits_in": sum(
            1 for s in analysed if s["published_line_opens_a_statement_a_survivor_sits_in"]),
        "selected_survivors_overall": sum(s["selected_count"] for s in analysed),
        "ruled_out_survivors_overall": sum(
            len(s["survivors_ruled_out"]) for s in analysed),
        "survivors_overall": sum(s["survivor_count"] for s in analysed),
        "decided_rows_compared_with_e540": len(compared),
        "rows_where_the_statement_anchor_agrees_with_e540": sum(
            1 for s in compared if s["agrees_with_e540"] is True),
        "rows_where_the_statement_anchor_disagrees_with_e540": sum(
            1 for s in compared if s["agrees_with_e540"] is False),
        "rows_where_e540_has_no_opinion": sum(
            1 for s in analysed if s["e540_pick_source"] != E540_READ),
        "classes_sum_to_the_rows": sum(classes.values()) == len(analysed),
        "decided_ambiguous_refused_and_unresolved_sum_to_the_rows": (
            classes[C_DECIDED] + classes[C_AMBIGUOUS] + classes[C_EMPTY] + classes[C_NO_CONTEXT]
            == len(analysed)),
        "survivors_accounted_for": sum(s["selected_count"] + len(s["survivors_ruled_out"])
                                       for s in analysed) == sum(
            s["survivor_count"] for s in analysed),
    }
    summary["decided_share"] = (round(classes[C_DECIDED] / float(len(analysed)), 4)
                               if analysed else None)
    summary["agreement_share_among_decided_rows"] = (
        round(summary["rows_where_the_statement_anchor_agrees_with_e540"] / float(len(compared)), 4)
        if compared else None)
    return {
        "card": CARD,
        "study": STUDY,
        "question": ("for the rows E542 measured as ambiguous, does reading the already-published "
                     "line as a statement anchor -- keep only the survivors whose innermost "
                     "statement opens on that line -- decide the row, leave it ambiguous, or "
                     "refuse to empty it, and does the survivor it picks agree with E540's "
                     "nearest-to-published rule?"),
        "evidence_cutoff": DATE_STAMP,
        "generated": _now(),
        "population_source": ("%s::ambiguous_sites() -- every row of E542's face, recomputed by "
                              "running E542's own build over the faces on disk" %
                              os.path.basename(__file__)),
        "upstream_face": UPSTREAM_FACE if sites is None else "caller-supplied rows",
        "upstream_sha256": upstream_sha,
        "rule": ("keep the survivors whose innermost statement's opening line equals the row's "
                 "published line; one kept survivor = decided, two or more = ambiguous, none = "
                 "refused (the rule would empty the row)"),
        "class_vocab": list(CLASSES),
        "pick_source_vocab": list(PICK_SOURCES),
        "verdict_vocab": list(VERDICT_VOCAB),
        "summary": summary,
        "verdict": _verdict(summary),
        "sites": analysed,
        "method_limits": [
            "the population is E542's rows only; if E541 left the wrong surviving set, this rule "
            "selects from the wrong set and cannot tell",
            "one kept survivor is called decided, but the rule says nothing about whether that "
            "survivor is the node the census meant -- it only says the published line stops being "
            "ambiguous",
            "a row the rule would empty is published as refused rather than applied: silently "
            "dropping every survivor would delete the ambiguity instead of resolving it",
            "E540's rule is recomputed through E541's implementation on the survivors of the row "
            "rather than re-implemented here, so agreement means what E541 would say, not what a "
            "reimplementation might",
            "agreement compares the candidate's line and column; E540 publishes the located span, "
            "so two different nodes cannot be distinguished beyond that pair",
            "statement_line is E542's AST reading at the face's cutoff; a file edited since then "
            "shifts the statement and the row is published with an unresolved context rather than "
            "silently re-located",
            "a row whose survivor list is empty is classed as refused: there is nothing to anchor "
            "on, and this study does not manufacture a decision out of an empty set",
            "the rule uses one row-level field the census already publishes; it is not evidence "
            "that the census always publishes a line that opens a statement",
        ],
    }


# ------------------------------------------------------------------ face io

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


# ------------------------------------------------------------------ gates

def face_problems(face):
    problems = []
    if face.get("study") != STUDY:
        problems.append("study is %r" % (face.get("study"),))
    for key in ("card", "question", "evidence_cutoff", "population_source", "rule",
                "class_vocab", "pick_source_vocab", "verdict_vocab", "summary", "verdict",
                "sites", "method_limits"):
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
    for key, cls in (("rows_decided_by_the_statement_anchor", C_DECIDED),
                     ("rows_that_stay_ambiguous_inside_the_published_statement", C_AMBIGUOUS),
                     ("rows_the_statement_anchor_would_refuse_to_empty", C_EMPTY),
                     ("rows_with_a_survivor_that_carries_no_statement_line", C_NO_CONTEXT)):
        if summary[key] != classes[cls]:
            problems.append("%s does not re-derive" % key)
    for site in sites:
        survivors = site.get("survivors_in_the_published_statement") or []
        ruled_out = site.get("survivors_ruled_out") or []
        if site.get("class") not in face["class_vocab"]:
            problems.append("site %s carries class %r" % (site.get("site"), site.get("class")))
        if site.get("selected_count") != len(survivors):
            problems.append("site %s selected_count does not match its kept survivors"
                            % (site.get("site"),))
        if len(survivors) + len(ruled_out) != site.get("survivor_count"):
            problems.append("site %s kept and ruled-out survivors do not add up to its count"
                            % (site.get("site"),))
        if site.get("class") == C_DECIDED and len(survivors) != 1:
            problems.append("site %s is decided with %d kept survivors"
                            % (site.get("site"), len(survivors)))
        if site.get("class") == C_AMBIGUOUS and len(survivors) < 2:
            problems.append("site %s is ambiguous with %d kept survivors"
                            % (site.get("site"), len(survivors)))
        if site.get("class") == C_EMPTY and survivors:
            problems.append("site %s would be emptied yet keeps survivors" % (site.get("site"),))
        if site.get("class") == C_NO_CONTEXT:
            every = ((site.get("survivors_in_the_published_statement") or [])
                     + (site.get("survivors_ruled_out") or []))
            if every and all(isinstance(s.get("statement_line"), int) for s in every):
                problems.append("site %s is unresolved yet every survivor carries a statement line"
                                % (site.get("site"),))
        if site.get("class") != C_NO_CONTEXT:
            kept_statements = {s.get("statement_line") for s in
                               (site.get("survivors_in_the_published_statement") or [])}
            ruled_statements = {s.get("statement_line") for s in
                                (site.get("survivors_ruled_out") or [])}
            if kept_statements and kept_statements != {site.get("published_line")}:
                problems.append("site %s keeps a survivor whose statement is not the published line"
                                % (site.get("site"),))
            if kept_statements & ruled_statements:
                problems.append("site %s rules out a survivor of the statement it keeps"
                                % (site.get("site"),))
        if site.get("published_line_opens_a_statement_a_survivor_sits_in") != bool(survivors):
            problems.append("site %s published-line flag disagrees with its kept survivors"
                            % (site.get("site"),))
        if site.get("e540_pick_source") not in face["pick_source_vocab"]:
            problems.append("site %s carries pick source %r"
                            % (site.get("site"), site.get("e540_pick_source")))
        if site.get("class") == C_DECIDED and site.get("e540_pick") is not None:
            pick, chosen = site["e540_pick"], survivors[0]
            expected = ((pick.get("line"), pick.get("col")) == (chosen.get("line"),
                                                                chosen.get("col")))
            if site.get("agrees_with_e540") is not expected:
                problems.append("site %s agreement does not re-derive" % (site.get("site"),))
        elif site.get("agrees_with_e540") is not None:
            problems.append("site %s publishes an agreement off a decided row"
                            % (site.get("site"),))
    if summary["rows_whose_published_line_opens_a_statement_a_survivor_sits_in"] != sum(
            1 for s in sites if s.get("published_line_opens_a_statement_a_survivor_sits_in")):
        problems.append("rows_whose_published_line_opens_a_statement_a_survivor_sits_in "
                        "does not re-derive")
    if summary["selected_survivors_overall"] != sum(s.get("selected_count") or 0 for s in sites):
        problems.append("selected_survivors_overall does not re-derive")
    if summary["ruled_out_survivors_overall"] != sum(
            len(s.get("survivors_ruled_out") or []) for s in sites):
        problems.append("ruled_out_survivors_overall does not re-derive")
    if summary["survivors_overall"] != sum(s.get("survivor_count") or 0 for s in sites):
        problems.append("survivors_overall does not re-derive")
    compared = [s for s in sites
                if s.get("class") == C_DECIDED and s.get("agrees_with_e540") is not None]
    if summary["decided_rows_compared_with_e540"] != len(compared):
        problems.append("decided_rows_compared_with_e540 does not re-derive")
    if summary["rows_where_the_statement_anchor_agrees_with_e540"] != sum(
            1 for s in compared if s.get("agrees_with_e540") is True):
        problems.append("rows_where_the_statement_anchor_agrees_with_e540 does not re-derive")
    if summary["rows_where_the_statement_anchor_disagrees_with_e540"] != sum(
            1 for s in compared if s.get("agrees_with_e540") is False):
        problems.append("rows_where_the_statement_anchor_disagrees_with_e540 does not re-derive")
    if summary["rows_where_e540_has_no_opinion"] != sum(
            1 for s in sites if s.get("e540_pick_source") != E540_READ):
        problems.append("rows_where_e540_has_no_opinion does not re-derive")
    if summary["classes_sum_to_the_rows"] != (sum(classes.values()) == len(sites)):
        problems.append("classes_sum_to_the_rows does not re-derive")
    if summary["decided_ambiguous_refused_and_unresolved_sum_to_the_rows"] != (
            classes[C_DECIDED] + classes[C_AMBIGUOUS] + classes[C_EMPTY] + classes[C_NO_CONTEXT]
            == len(sites)):
        problems.append(
            "decided_ambiguous_refused_and_unresolved_sum_to_the_rows does not re-derive")
    if summary["survivors_accounted_for"] != (
            sum(s.get("selected_count", 0) + len(s.get("survivors_ruled_out") or [])
                for s in sites) == sum(s.get("survivor_count") or 0 for s in sites)):
        problems.append("survivors_accounted_for does not re-derive")
    if face["verdict"] != _verdict(summary):
        problems.append("verdict does not re-derive from the summary")
    if face["verdict"] not in face["verdict_vocab"]:
        problems.append("verdict is outside the vocabulary")
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

# Three same-shape candidates in one function, each in its own statement: an assignment on line 3,
# an if-body assignment whose statement opens on line 4, and a for-body assignment opening on line 6.
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

# Two same-shape candidates inside ONE statement that opens on line 3: the published line 3 keeps both.
SAME_STATEMENT_SRC = (
    "import os\n"                                                   # 1
    "def beta(root):\n"                                             # 2
    "    pair = (os.path.join(root, \"thing_latest.json\"),\n"       # 3
    "            os.path.join(root, \"thing_latest.json\"))\n"       # 4
    "    return pair\n"                                             # 5
)

# Two candidates in two statements, one of which opens on line 4 and carries its node on line 5: the
# statement anchor keeps the line-5 node while E540's nearest rule keeps the line-3 node.
DISAGREE_SRC = (
    "import os\n"                                                   # 1
    "def eta(root):\n"                                              # 2
    "    u = os.path.join(root, \"thing_latest.json\")\n"            # 3
    "    v = (\n"                                                    # 4
    "        os.path.join(root, \"thing_latest.json\")\n"            # 5
    "    )\n"                                                       # 6
    "    return u, v\n"                                             # 7
)

EXPR = 'os.path.join(root, "thing_latest.json")'


def _fixture_sites(tmp, name, published=3, near=3):
    """Real rows: E542 resolves the survivors, so statement lines are E542's own readings."""
    index = e541.file_index(tmp, name, {})
    cands = e541.candidate_rows(index, EXPR, near) or []
    site = {"site": "%s:%s" % (name, published), "file": name, "published_line": published,
            "tier": "fixture", "expr": EXPR,
            "survivors": [{"line": c["line"], "col": c["col"], "function": c["function"]}
                          for c in cands]}
    return e542.analyse([site], root=tmp)


def selftest():
    failures = []
    ran = []

    def arm(name, ok, detail=""):
        ran.append(name)
        print(("PASS " if ok else "FAIL ") + name + (" -- " + detail if detail else ""))
        if not ok:
            failures.append(name)

    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        for name, src in (("fixture.py", FIXTURE_SRC), ("same.py", SAME_STATEMENT_SRC),
                          ("disagree.py", DISAGREE_SRC)):
            with open(os.path.join(tmp, name), "w", encoding="utf-8", newline="\n") as fh:
                fh.write(src)

        rows = _fixture_sites(tmp, "fixture.py")
        statements = sorted(r.get("statement_line") for r in rows[0]["survivors"])
        arm("the fixture resolves its three survivors into three different statements",
            statements == [3, 5, 7], json.dumps(statements))

        face = build(root=tmp, write=False, sites=rows)
        row = face["sites"][0]
        arm("a row published on the statement opening line keeps exactly one survivor",
            row["class"] == C_DECIDED and row["selected_count"] == 1, row["class"])
        arm("the survivor it keeps is the one whose statement opens there",
            row["survivors_in_the_published_statement"][0]["line"] == 3,
            json.dumps(row["survivors_in_the_published_statement"]))
        arm("the rule rules out every survivor of another statement",
            sorted(s["line"] for s in row["survivors_ruled_out"]) == [5, 7],
            json.dumps(sorted(s["line"] for s in row["survivors_ruled_out"])))
        arm("E540's nearest rule lands on the same survivor on this row",
            row["agrees_with_e540"] is True, json.dumps(row["e540_pick"]))

        inside_stmt = json.loads(json.dumps(rows))
        inside_stmt[0]["published_line"] = 5
        inside_stmt[0]["site"] = "fixture.py:5"
        face_stmt = build(root=tmp, write=False, sites=inside_stmt)
        row_stmt = face_stmt["sites"][0]
        arm("a published line on a statement opening keeps the survivor inside that statement",
            row_stmt["class"] == C_DECIDED
            and row_stmt["survivors_in_the_published_statement"][0]["line"] == 5,
            json.dumps(row_stmt["survivors_in_the_published_statement"]))
        arm("a published line that opens no survivor's statement is refused even when survivors "
            "sit on both sides of it", build(
                root=tmp, write=False, sites=[dict(inside_stmt[0], published_line=4,
                                                   site="fixture.py:4")])["sites"][0][
                    "class"] == C_EMPTY)

        disagree_rows = _fixture_sites(tmp, "disagree.py", published=4, near=4)
        face_dis = build(root=tmp, write=False, sites=disagree_rows)
        row_dis = face_dis["sites"][0]
        arm("the statement anchor can keep the node inside a multi-line statement",
            row_dis["class"] == C_DECIDED
            and row_dis["survivors_in_the_published_statement"][0]["line"] == 5,
            json.dumps(row_dis["survivors_in_the_published_statement"]))
        arm("the statement anchor can disagree with E540's nearest rule",
            row_dis["agrees_with_e540"] is False, json.dumps(row_dis["e540_pick"]))

        off_statement = json.loads(json.dumps(rows))
        off_statement[0]["published_line"] = 2
        off_statement[0]["site"] = "fixture.py:2"
        face_off = build(root=tmp, write=False, sites=off_statement)
        arm("a published line that opens no survivor's statement is published as refused",
            face_off["sites"][0]["class"] == C_EMPTY
            and face_off["sites"][0]["selected_count"] == 0, face_off["sites"][0]["class"])
        arm("a refused row publishes no agreement",
            face_off["sites"][0]["agrees_with_e540"] is None)

        same_rows = _fixture_sites(tmp, "same.py")
        face_same = build(root=tmp, write=False, sites=same_rows)
        arm("two survivors inside one statement leave the row ambiguous",
            face_same["sites"][0]["class"] == C_AMBIGUOUS
            and face_same["sites"][0]["selected_count"] == 2, face_same["sites"][0]["class"])

        unreadable = json.loads(json.dumps(rows))
        unreadable[0]["file"] = "missing.py"
        face_unread = build(root=tmp, write=False, sites=unreadable)
        arm("a row whose file cannot be read still decides and publishes no agreement",
            face_unread["sites"][0]["class"] == C_DECIDED
            and face_unread["sites"][0]["e540_pick_source"] == E540_UNREADABLE
            and face_unread["sites"][0]["agrees_with_e540"] is None,
            face_unread["sites"][0]["e540_pick_source"])

        no_line = {"site": "fixture.py:3", "file": "fixture.py", "published_line": 3,
                   "tier": "fixture", "expr": EXPR,
                   "survivors": [{"line": 3, "col": 0, "function": "<module>",
                                  "statement_line": None}]}
        face_no_line = build(root=tmp, write=False, sites=[no_line])
        arm("a survivor without a statement line is published as unresolved",
            face_no_line["sites"][0]["class"] == C_NO_CONTEXT, face_no_line["sites"][0]["class"])

        empty_row = {"site": "fixture.py:3", "file": "fixture.py", "published_line": 3,
                     "tier": "fixture", "expr": EXPR, "survivors": []}
        face_empty_row = build(root=tmp, write=False, sites=[empty_row])
        arm("a row with no survivors is refused rather than manufactured into a decision",
            face_empty_row["sites"][0]["class"] == C_EMPTY
            and face_empty_row["sites"][0]["e540_pick_source"] == E540_NO_SURVIVORS,
            face_empty_row["sites"][0]["class"])

        mixed = build(root=tmp, write=False,
                      sites=[rows[0], same_rows[0], off_statement[0]])
        arm("a mixed population publishes the mixed verdict", mixed["verdict"] == V_MIXED,
            mixed["verdict"])
        decided_only = build(root=tmp, write=False, sites=[rows[0]])
        arm("a population the anchor decides publishes the closed verdict",
            decided_only["verdict"] == V_CLOSED, decided_only["verdict"])
        ambiguous_only = build(root=tmp, write=False, sites=[same_rows[0]])
        arm("a population the anchor cannot separate publishes the ambiguous verdict",
            ambiguous_only["verdict"] == V_AMBIGUOUS, ambiguous_only["verdict"])
        refused_only = build(root=tmp, write=False, sites=[off_statement[0]])
        arm("a population the anchor would empty publishes the refused verdict",
            refused_only["verdict"] == V_REFUSED, refused_only["verdict"])

        arm("a built fixture face passes its own gate", face_problems(face) == [],
            json.dumps(face_problems(face), ensure_ascii=False)[:400])

        doctored = json.loads(json.dumps(face))
        doctored["verdict"] = "a_verdict_this_study_never_publishes"
        arm("a hand-written verdict is refused", bool(face_problems(doctored)))

        doctored = json.loads(json.dumps(face))
        doctored["summary"]["rows_decided_by_the_statement_anchor"] += 1
        arm("an inflated decided count is refused", bool(face_problems(doctored)))

        doctored = json.loads(json.dumps(face))
        doctored["sites"][0]["class"] = C_AMBIGUOUS
        arm("a decided row relabelled ambiguous is refused", bool(face_problems(doctored)))

        doctored = json.loads(json.dumps(face))
        doctored["sites"][0]["agrees_with_e540"] = None
        arm("an erased agreement on a decided row is refused", bool(face_problems(doctored)))

        doctored = json.loads(json.dumps(face_same))
        doctored["sites"][0]["agrees_with_e540"] = True
        arm("an agreement published on an ambiguous row is refused", bool(face_problems(doctored)))

        doctored = json.loads(json.dumps(face))
        doctored["sites"][0]["selected_count"] = 2
        arm("a selected count its own list does not carry is refused", bool(face_problems(doctored)))

        doctored = json.loads(json.dumps(face))
        doctored["sites"][0]["survivors_ruled_out"] = doctored["sites"][0][
            "survivors_ruled_out"][:1]
        arm("a ruled-out list that loses a survivor is refused", bool(face_problems(doctored)))

        empty_population = build(root=tmp, write=False, sites=[])
        arm("an empty population publishes the empty verdict",
            empty_population["verdict"] == V_EMPTY)

    print("selftest: %d arms, %d failed" % (len(ran), len(failures)))
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
        print("run: rows=%s survivors=%s kept=%s ruled_out=%s"
              % (s["rows"], s["survivors_overall"], s["selected_survivors_overall"],
                 s["ruled_out_survivors_overall"]))
        print("run: decided=%s ambiguous=%s refused=%s unresolved=%s"
              % (s["rows_decided_by_the_statement_anchor"],
                 s["rows_that_stay_ambiguous_inside_the_published_statement"],
                 s["rows_the_statement_anchor_would_refuse_to_empty"],
                 s["rows_with_a_survivor_that_carries_no_statement_line"]))
        print("run: e540_compared=%s agrees=%s disagrees=%s no_opinion=%s"
              % (s["decided_rows_compared_with_e540"],
                 s["rows_where_the_statement_anchor_agrees_with_e540"],
                 s["rows_where_the_statement_anchor_disagrees_with_e540"],
                 s["rows_where_e540_has_no_opinion"]))
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