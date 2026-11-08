"""E549 -- what the four unclassified sites actually do with the constant.

E546 (r1575) published 35 constants whose terminal is the module file itself and
left four rows classed ``the_name_is_consumed_but_no_site_says_what_it_is``: in
every one of them the constant is handed to something the site scan did not
follow.  The card for this study says the remaining question is not a scan over
more sites but a read of the *enclosing function*: does the path get opened,
joined, or only compared -- and where a comparison is the whole use, publish it
as a class of its own so that "unknown" stops standing in for "we never read the
enclosing function".

So this study re-derives its population from E546's own published face (the four
rows, machine-read, never hand-listed), and for each site:

  * locates the innermost function that contains the site (AST),
  * binds the constant name -- plus, where the constant is a default argument,
    the parameter name it arrives under -- and walks that function body for every
    load of those names,
  * classes each load by what the AST does with it: compared, opened, probed for
    existence, joined, or handed to a callee this scan does not follow,
  * publishes the row class from those loads.

The reading it produces: three of the four are identity tokens -- the constant is
normalised with ``os.path.abspath`` and compared, so the module's own file is
excluded from a corpus it would otherwise scan itself into -- and the fourth is a
default argument whose callee both probes and opens the path.  Nothing stays
unknown.

    python scripts/e549_unclassified_site.py build      # publish the face
    python scripts/e549_unclassified_site.py check      # re-derive from source; problems must be []
    python scripts/e549_unclassified_site.py verify     # two builds identical
    python scripts/e549_unclassified_site.py selftest   # offline fixtures + defect refusals
"""
from __future__ import annotations

import ast
import io
import json
import os
import sys
import textwrap
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
STATE_TILT = os.path.join(ROOT, "results", "state_tilt")
PARENT_LATEST = os.path.join(STATE_TILT, "filepathjoined_latest.json")
LATEST = os.path.join(STATE_TILT, "unclassifiedsite_latest.json")

STUDY = "E549"
CARD = "E549"
TITLE = "what the four unclassified sites actually do with the constant"
EVIDENCE_CUTOFF = "2026-11-08"

# The parent's own word for the rows this study consumes.
R_UNKNOWN_PARENT = "the_name_is_consumed_but_no_site_says_what_it_is"

# Row classes -- one per thing the enclosing function turns out to do.
R_IDENTITY = "the_whole_use_is_a_comparison_and_the_constant_is_an_identity_token"
R_OPENED = "the_constant_arrives_as_a_default_argument_and_the_callee_opens_it"
R_PROBE = "the_constant_arrives_as_a_default_argument_and_the_callee_only_tests_it"
R_RESIDUAL = "the_site_still_needs_a_read_this_scan_does_not_do"
ROW_VOCAB = (R_IDENTITY, R_OPENED, R_PROBE, R_RESIDUAL)

# Use classes -- what the AST does with one load of the name.
U_COMPARED = "the_load_is_one_side_of_a_comparison_and_the_value_is_never_read"
U_OPENED = "the_load_reaches_open_so_the_constant_is_read_as_a_file"
U_PROBED = "the_load_only_asks_whether_the_path_exists"
U_JOINED = "the_load_is_joined_with_a_child_name_so_the_constant_is_a_container"
U_PASSED = "the_load_is_handed_to_a_callee_this_scan_does_not_follow"
U_REBOUND = "the_load_is_only_rebound_to_another_name"
USE_VOCAB = (U_COMPARED, U_OPENED, U_PROBED, U_JOINED, U_PASSED, U_REBOUND)

ARRIVES_DEFAULT = "a_default_argument_of_the_enclosing_function"
ARRIVES_BARE = "a_bare_name_inside_the_enclosing_function"

V_ALL = "every_unclassified_site_was_read_out_of_its_enclosing_function_and_no_row_stays_unknown"
V_RESIDUAL = "some_unclassified_sites_still_need_a_read_this_scan_does_not_do"
VERDICT_VOCAB = (V_ALL, V_RESIDUAL)

# Frames that only normalise a path -- climbing through them lands on the real use.
PATH_FRAMES = ("abspath", "normpath", "realpath", "expanduser", "abspath_norm")


# ---------------------------------------------------------------- source reads
def _read(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


def _fname(func):
    try:
        return ast.unparse(func)
    except Exception:
        return "?"


def _short(text, n=120):
    text = " ".join(str(text).split())
    return text if len(text) <= n else text[: n - 1] + "\u2026"


def _parent_map(tree):
    parents = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[child] = node
    return parents


def _innermost_function(tree, line):
    best = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            end = getattr(node, "end_lineno", node.lineno)
            if node.lineno <= line <= end:
                if best is None or node.lineno >= best.lineno:
                    best = node
    return best


def _constants_named(body, name):
    """Every Name load of ``name`` inside the given statement list."""
    out = []
    for node in body:
        for sub in ast.walk(node):
            if isinstance(sub, ast.Name) and isinstance(sub.ctx, ast.Load) and sub.id == name:
                out.append(sub)
    return sorted(out, key=lambda n: (n.lineno, n.col_offset))


def _climb_frames(node, parents):
    """Climb out of path-normalising wrappers; return the outermost such node."""
    cur = node
    while True:
        par = parents.get(cur)
        if isinstance(par, ast.Call) and par.args and par.args[0] is cur and \
                _fname(par.func).split(".")[-1] in PATH_FRAMES:
            cur = par
            continue
        return cur


def _classify_use(node, parents):
    """-> (use_class, detail dict) for one load of the bound name."""
    cur = _climb_frames(node, parents)
    wrapped = cur is not node
    par = parents.get(cur)
    detail = {"line": node.lineno}
    if wrapped:
        detail["climbed_through"] = _short(_fname(cur.func) if isinstance(cur, ast.Call) else "?")
    if isinstance(par, ast.Compare):
        detail["the_other_side"] = _short(ast.unparse(par.left if cur in par.comparators else par.comparators[0]))
        detail["operator"] = " ".join(ast.unparse(o) for o in par.ops)
        detail["statement"] = _short(ast.unparse(par))
        return U_COMPARED, detail
    if isinstance(par, ast.Call):
        callee = _fname(par.func).split(".")[-1]
        detail["callee"] = _fname(par.func)
        detail["argument_position"] = par.args.index(cur) if cur in par.args else None
        if callee == "open":
            return U_OPENED, detail
        if callee == "join":
            return U_JOINED, detail
        if callee in ("exists", "isfile", "isdir"):
            return U_PROBED, detail
        return U_PASSED, detail
    if isinstance(par, (ast.Assign, ast.AnnAssign)):
        detail["rebound_as"] = _short(ast.unparse(par))
        return U_REBOUND, detail
    detail["parent_node"] = type(par).__name__ if par is not None else "none"
    return U_PASSED, detail


def _bound_through_defaults(fn, name):
    """Names the constant arrives under: itself, plus any parameter defaulting to it."""
    bound = {name}
    args = fn.args
    positional = list(getattr(args, "posonlyargs", [])) + list(args.args)
    pairs = list(zip(positional[len(positional) - len(args.defaults):], args.defaults))
    pairs += [(a, d) for a, d in zip(args.kwonlyargs, args.kw_defaults) if d is not None]
    hits = []
    for arg, default in pairs:
        if any(isinstance(sub, ast.Name) and sub.id == name for sub in ast.walk(default)):
            bound.add(arg.arg)
            hits.append(arg.arg)
    return bound, hits


def analyze(text, name, site_lines):
    """Read each site out of its enclosing function.  Pure: text in, rows' guts out."""
    tree = ast.parse(text)
    parents = _parent_map(tree)
    sites = []
    for line in site_lines:
        fn = _innermost_function(tree, line)
        site = {"line": line}
        if fn is None:
            site["enclosing"] = None
            site["the_constant_arrives_as"] = ARRIVES_BARE
            site["uses"] = []
            site["site_class"] = R_RESIDUAL
            site["why_no_use"] = "the site sits at module level, where nothing reads it"
            sites.append(site)
            continue
        bound, via_default = _bound_through_defaults(fn, name)
        node_at = None
        for node in ast.walk(fn):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load) and node.lineno == line:
                node_at = node
        site["enclosing"] = {"function": fn.name, "start_line": fn.lineno,
                             "end_line": getattr(fn, "end_lineno", fn.lineno)}
        site["the_constant_arrives_as"] = ARRIVES_DEFAULT if via_default else ARRIVES_BARE
        if via_default:
            site["the_parameter_that_carries_it"] = via_default[0]
        uses = []
        for node in _constants_named(fn.body, name) + [
                n for p in via_default for n in _constants_named(fn.body, p)]:
            cls, detail = _classify_use(node, parents)
            uses.append({"use_class": cls, "detail": detail})
        uses.sort(key=lambda u: u["detail"]["line"])
        site["uses"] = uses
        if node_at is None and not uses:
            site["why_no_use"] = "no load of the bound name inside the enclosing function"
        site["site_class"] = _site_class(uses)
        sites.append(site)
    return sites


def _site_class(uses):
    classes = [u["use_class"] for u in uses]
    if not classes:
        return R_RESIDUAL
    if U_OPENED in classes:
        return R_OPENED
    if U_JOINED in classes:
        return R_RESIDUAL
    if U_PROBED in classes and all(c in (U_PROBED, U_COMPARED) for c in classes):
        return R_PROBE
    if all(c == U_COMPARED for c in classes):
        return R_IDENTITY
    return R_RESIDUAL


def _row_class(row):
    classes = {s["site_class"] for s in row["sites"]}
    if classes == {R_IDENTITY}:
        return R_IDENTITY
    if R_OPENED in classes:
        return R_OPENED
    if classes == {R_PROBE}:
        return R_PROBE
    return R_RESIDUAL


def _what_it_is_used_as(row_class):
    return {
        R_IDENTITY: "an_identity_token_never_read",
        R_OPENED: "a_file_read_through_a_default_parameter",
        R_PROBE: "a_path_only_tested_for_existence",
        R_RESIDUAL: "not_settled_by_this_scan",
    }[row_class]


# ---------------------------------------------------------------- the face
def _parent_population():
    parent = json.load(io.open(PARENT_LATEST, encoding="utf-8"))
    rows = [r for r in parent.get("rows") or [] if r.get("row_class") == R_UNKNOWN_PARENT]
    return parent, rows


def build(write=True):
    parent, pop = _parent_population()
    rows = []
    for prow in pop:
        src = prow["source"]
        sites = analyze(_read(os.path.join(ROOT, src)), prow["name"],
                        [s["line"] for s in prow.get("sites") or []])
        row = {
            "source": src,
            "name": prow["name"],
            "declaration_line": prow["line"],
            "the_value_the_parent_published": prow.get("value"),
            "sites": sites,
            "site_count": len(sites),
            "row_class": None,
            "what_the_constant_is_used_as": None,
        }
        row["row_class"] = _row_class(row)
        row["what_the_constant_is_used_as"] = _what_it_is_used_as(row["row_class"])
        rows.append(row)
    rows.sort(key=lambda r: (r["source"], r["declaration_line"]))

    by_class = {c: 0 for c in ROW_VOCAB}
    for r in rows:
        by_class[r["row_class"]] += 1
    uses = [u for r in rows for s in r["sites"] for u in s["uses"]]
    uses_by_class = {c: 0 for c in USE_VOCAB}
    for u in uses:
        uses_by_class[u["use_class"]] += 1

    summary = {
        "rows_the_parent_published_as_unknown": len(pop),
        "parent_rows_total": len(parent.get("rows") or []),
        "rows": len(rows),
        "reproduction_matches_the_parent": len(rows) == len(pop) and
        len(pop) == (parent.get("summary") or {}).get("by_class", {}).get(R_UNKNOWN_PARENT),
        "by_class": by_class,
        "sites": sum(r["site_count"] for r in rows),
        "uses": len(uses),
        "uses_by_class": uses_by_class,
        "identity_token_rows": by_class[R_IDENTITY],
        "opened_rows": by_class[R_OPENED],
        "probe_rows": by_class[R_PROBE],
        "residual_rows": by_class[R_RESIDUAL],
        "rows_whose_constant_is_never_read": by_class[R_IDENTITY],
        "rows_whose_constant_is_read_as_a_file": by_class[R_OPENED],
        "sites_where_a_climbed_frame_normalised_the_path": sum(
            1 for u in uses if u["detail"].get("climbed_through")),
        "comparison_sites_whose_other_side_is_the_normalised_own_path": sum(
            1 for u in uses if u["use_class"] == U_COMPARED
            and "abspath" in str(u["detail"].get("the_other_side", ""))),
    }
    verdict = V_RESIDUAL if summary["residual_rows"] else V_ALL

    face = {
        "study": STUDY,
        "card": CARD,
        "title": TITLE,
        "generated": datetime.now().astimezone().isoformat(timespec="seconds"),
        "evidence_cutoff": parent.get("evidence_cutoff") or EVIDENCE_CUTOFF,
        "population_source": {
            "parent_face": "results/state_tilt/filepathjoined_latest.json",
            "parent_study": parent.get("study"),
            "parent_evidence_cutoff": parent.get("evidence_cutoff"),
            "parent_row_class_consumed": R_UNKNOWN_PARENT,
            "rows_the_parent_published_as_unknown": len(pop),
            "parent_rows_total": len(parent.get("rows") or []),
            "how_the_population_was_taken": "the parent's own rows with its own class word -- machine-read, never hand-listed",
        },
        "method_limits": [
            "one enclosing function per site: a load handed to another callee is published as passed, not followed",
            "for the default-argument row the callee IS the enclosing function, so that row is exactly one hop and no further",
            "a comparison class says what the AST does (compare), not what the compared value means at run time",
            "no execution: the classes are static, and 'read as a file' means a load reaches open(), not that the file exists",
        ],
        "summary": summary,
        "verdict": verdict,
        "verdict_vocab": list(VERDICT_VOCAB),
        "row_vocab": list(ROW_VOCAB),
        "use_vocab": list(USE_VOCAB),
        "rows": rows,
    }
    if write:
        out = os.path.join(STATE_TILT, "UNCLASSIFIEDSITE-%s.json" % face["evidence_cutoff"])
        text = json.dumps(face, ensure_ascii=False, indent=1)
        for path in (out, LATEST):
            io.open(path, "w", encoding="utf-8", newline="\n").write(text + "\n")
    return face


def face_problems(face):
    """Re-derive everything the face claims, from its own rows.  -> [problem]."""
    probs = []
    rows = face.get("rows") or []
    s = face.get("summary") or {}
    if not rows:
        probs.append("the population is empty")
        return probs

    by_class = {c: 0 for c in ROW_VOCAB}
    uses = []
    for r in rows:
        if r.get("row_class") not in ROW_VOCAB:
            probs.append("row class outside the vocabulary: %s" % (r.get("row_class"),))
        else:
            by_class[r["row_class"]] += 1
        if not r.get("sites"):
            probs.append("a row publishes no site (%s)" % r.get("source"))
            continue
        for site in r["sites"]:
            if not site.get("uses") and site.get("site_class") != R_RESIDUAL:
                probs.append("a site publishes no use yet is classed %s (%s:%s)"
                             % (site.get("site_class"), r.get("source"), site.get("line")))
            for u in site.get("uses") or []:
                if u.get("use_class") not in USE_VOCAB:
                    probs.append("use class outside the vocabulary: %s" % (u.get("use_class"),))
                uses.append(u)
        laid = _row_class(r)
        if laid != r["row_class"]:
            probs.append("a row's class is not what its sites say (%s: %s vs %s)"
                         % (r.get("source"), r["row_class"], laid))
        if r.get("what_the_constant_is_used_as") != _what_it_is_used_as(laid):
            probs.append("a row's use-word is not what its class says (%s)" % r.get("source"))
        # a row called an identity token must contain no load that reaches open()/join/exists
        row_uses = [u for site in r["sites"] for u in site.get("uses") or []]
        if laid == R_IDENTITY and any(u["use_class"] in (U_OPENED, U_JOINED, U_PROBED)
                                     for u in row_uses):
            probs.append("a row is called an identity token beside a load that reads it (%s)"
                         % r.get("source"))
        if laid == R_OPENED and not any(u["use_class"] == U_OPENED for u in row_uses):
            probs.append("a row is called an opened file with no load that reaches open() (%s)"
                         % r.get("source"))

    if s.get("by_class") != by_class:
        probs.append("the summary's class counts are not the rows' (%s vs %s)" % (s.get("by_class"), by_class))
    for key, val in (("identity_token_rows", by_class[R_IDENTITY]),
                     ("opened_rows", by_class[R_OPENED]),
                     ("probe_rows", by_class[R_PROBE]),
                     ("residual_rows", by_class[R_RESIDUAL]),
                     ("rows", len(rows)),
                     ("uses", len(uses))):
        if s.get(key) != val:
            probs.append("summary %s=%r but the rows say %r" % (key, s.get(key), val))
    uses_by_class = {c: 0 for c in USE_VOCAB}
    for u in uses:
        if u["use_class"] in uses_by_class:
            uses_by_class[u["use_class"]] += 1
    if s.get("uses_by_class") != uses_by_class:
        probs.append("the summary's use counts are not the rows'")
    pop = (face.get("population_source") or {})
    if pop.get("rows_the_parent_published_as_unknown") != len(rows):
        probs.append("the study's population is not the parent's own unknown-row count")
    if s.get("reproduction_matches_the_parent") is not True:
        probs.append("the population is not published as reproducing the parent")
    want = V_RESIDUAL if by_class[R_RESIDUAL] else V_ALL
    if face.get("verdict") != want:
        probs.append("the verdict is not what the rows derive (%r vs %r)" % (face.get("verdict"), want))
    if face.get("verdict") not in VERDICT_VOCAB:
        probs.append("verdict outside the vocabulary")
    return probs


def check():
    pub = json.load(io.open(LATEST, encoding="utf-8"))
    problems = list(face_problems(pub))
    fresh = build(write=False)
    if [r["source"] for r in fresh["rows"]] != [r["source"] for r in pub["rows"]]:
        problems.append("the published population is not the one the parent has now")
    else:
        for a, b in zip(fresh["rows"], pub["rows"]):
            if json.dumps(a, sort_keys=True) != json.dumps(b, sort_keys=True):
                problems.append("a published row is not what the source says now (%s)" % a["source"])
    if fresh["verdict"] != pub["verdict"]:
        problems.append("the published verdict is not the one the sources derive now")
    print(json.dumps({"problems": problems, "verdict": pub.get("verdict"),
                      "rows": len(pub.get("rows") or [])}, ensure_ascii=False))
    return 1 if problems else 0


def verify():
    a, b = build(write=False), build(write=False)
    pa = {k: v for k, v in a.items() if k != "generated"}
    pb = {k: v for k, v in b.items() if k != "generated"}
    problems = [] if json.dumps(pa, sort_keys=True) == json.dumps(pb, sort_keys=True) else \
        ["two builds of the same sources differ"]
    print(json.dumps({"problems": problems}, ensure_ascii=False))
    return 1 if problems else 0


# ---------------------------------------------------------------- selftest
FIXTURES = {
    "identity": textwrap.dedent('''
        import os
        HERE = os.path.dirname(os.path.abspath(__file__))
        SELF = os.path.abspath(__file__)
        def corpus():
            out = []
            for p in ["a.py"]:
                if os.path.abspath(p) == SELF:
                    continue
                out.append(p)
            return out
    ''').split("\n"),
    "opened_default": textwrap.dedent('''
        import os
        CAL_PATH = os.path.join("data", "cal.csv")
        def load(path=CAL_PATH):
            if not os.path.exists(path):
                return []
            with open(path, encoding="utf-8") as fh:
                return [l.strip() for l in fh]
    ''').split("\n"),
    "probe_default": textwrap.dedent('''
        import os
        CAL_PATH = os.path.join("data", "cal.csv")
        def has(path=CAL_PATH):
            return os.path.exists(path)
    ''').split("\n"),
    "passed": textwrap.dedent('''
        import os
        CAL_PATH = os.path.join("data", "cal.csv")
        def use(path=CAL_PATH):
            return read_it(path)
    ''').split("\n"),
}


def _line_of(lines, needle):
    for i, l in enumerate(lines, 1):
        if needle in l:
            return i
    raise AssertionError("fixture line not found: %s" % needle)


def selftest():
    fails = []
    n = 0

    def ok(name, cond, detail=""):
        nonlocal n
        n += 1
        if not cond:
            fails.append(name + ((" -- " + detail) if detail else ""))
        print(("PASS " if cond else "FAIL ") + name + ((" -- " + detail) if detail else ""))

    # 1 -- a comparison is the whole use: identity token
    s = analyze("\n".join(FIXTURES["identity"]), "SELF",
                [_line_of(FIXTURES["identity"], "== SELF")])
    ok("identity: one site, classed as an identity token",
       len(s) == 1 and s[0]["site_class"] == R_IDENTITY, json.dumps(s[:1])[:200])
    ok("identity: the use is a comparison and it climbed through abspath",
       s[0]["uses"][0]["use_class"] == U_COMPARED and
       "abspath" in str(s[0]["uses"][0]["detail"].get("the_other_side")))

    # 2 -- the constant arrives as a default argument and the callee opens it
    lines = FIXTURES["opened_default"]
    s = analyze("\n".join(lines), "CAL_PATH", [_line_of(lines, "path=CAL_PATH")])
    ok("opened: the constant arrives as a default argument",
       s[0]["the_constant_arrives_as"] == ARRIVES_DEFAULT, json.dumps(s[0])[:200])
    ok("opened: both the probe and the open are published, the open dominates",
       s[0]["site_class"] == R_OPENED and
       {u["use_class"] for u in s[0]["uses"]} == {U_PROBED, U_OPENED},
       json.dumps([u["use_class"] for u in s[0]["uses"]]))

    # 3 -- only tested
    lines = FIXTURES["probe_default"]
    s = analyze("\n".join(lines), "CAL_PATH", [_line_of(lines, "path=CAL_PATH")])
    ok("probe: a default argument that is only tested is not called a read",
       s[0]["site_class"] == R_PROBE)

    # 4 -- handed to a callee: stays residual, and says so
    lines = FIXTURES["passed"]
    s = analyze("\n".join(lines), "CAL_PATH", [_line_of(lines, "path=CAL_PATH")])
    ok("passed: a load handed to a callee this scan does not follow is residual",
       s[0]["site_class"] == R_RESIDUAL and
       s[0]["uses"][0]["use_class"] == U_PASSED)

    # 5 -- the published face
    face = build(write=False)
    rows = face["rows"]
    ok("face: the population is the parent's own four unknown rows",
       len(rows) == 4 and face["summary"]["rows_the_parent_published_as_unknown"] == 4)
    ok("face: no row stays residual", face["summary"]["residual_rows"] == 0,
       str(face["summary"]["by_class"]))
    ok("face: three identity tokens and one opened-through-a-parameter",
       face["summary"]["identity_token_rows"] == 3 and face["summary"]["opened_rows"] == 1,
       str(face["summary"]["by_class"]))
    ok("face: all four comparison sites compare against a normalised own path",
       face["summary"]["comparison_sites_whose_other_side_is_the_normalised_own_path"] == 4 and
       face["summary"]["uses_by_class"][U_COMPARED] == 4,
       str(face["summary"]["comparison_sites_whose_other_side_is_the_normalised_own_path"]))
    ok("face: face_problems is clean", face_problems(face) == [], str(face_problems(face))[:300])
    ok("face: verdict says no row stays unknown", face["verdict"] == V_ALL)

    # 6 -- doctored copies must be refused
    doc = json.loads(json.dumps(face))
    doc["verdict"] = "a_verdict_this_study_never_publishes"
    ok("defect: a hand-written verdict is refused", bool(face_problems(doc)))
    doc = json.loads(json.dumps(face))
    doc["rows"] = doc["rows"][:-1]
    ok("defect: a summary that outlives its rows is refused", bool(face_problems(doc)))
    doc = json.loads(json.dumps(face))
    for r in doc["rows"]:
        if r["row_class"] == R_IDENTITY:
            r["row_class"] = R_RESIDUAL
            break
    ok("defect: a flipped row class is refused", bool(face_problems(doc)))
    doc = json.loads(json.dumps(face))
    for r in doc["rows"]:
        if r["row_class"] == R_OPENED:
            r["sites"][0]["uses"] = [{"use_class": U_COMPARED, "detail": {"line": 1}}]
            break
    ok("defect: an opened row whose sites only compare is refused", bool(face_problems(doc)))
    doc = json.loads(json.dumps(face))
    doc["population_source"]["rows_the_parent_published_as_unknown"] = 9
    ok("defect: a population size that is not the parent's is refused", bool(face_problems(doc)))

    print("%d/%d legs green" % (n - len(fails), n))
    return 1 if fails else 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "build"
    if cmd == "build":
        face = build()
        print(json.dumps({"rows": len(face["rows"]), "verdict": face["verdict"],
                          "by_class": face["summary"]["by_class"]}, ensure_ascii=False))
        return 0
    if cmd == "check":
        return check()
    if cmd == "verify":
        return verify()
    if cmd == "selftest":
        return selftest()
    raise SystemExit("unknown command: %s (build|check|verify|selftest)" % cmd)


if __name__ == "__main__":
    sys.exit(main())