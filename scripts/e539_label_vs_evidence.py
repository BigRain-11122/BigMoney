"""E539 -- does a published class label survive the evidence row it travels with?

E398 publishes a census face (``results/state_tilt/latestfamily_latest.json``) in which every
read site and every write site of a bare ``latest.json`` carries two things side by side: a
``class`` naming where the family directory came from, and an ``evidence`` object naming the
exact expression / constant / binding that produced it.  E538 priced four rows as
``family_stated_at_the_site`` although their family came from an imported constant resolved
three functions away, which is the residue this study measures in full.

Three questions, each answered on the face as it is published on disk plus the source lines it
points at:

  1. INTERNAL -- for every row, does the label agree with its own evidence row?
       stated_at_the_site + a how that names a binding/constant      -> labelled literal, evidenced name
       stated_at_the_site + no family_dir and no family_suffix       -> labelled stated, nothing stated
       required_by_the_signature + no default published              -> labelled signature, no default
       from_the_value_the_site_itself_wrote + no written_expr        -> labelled carried, nothing carried
       not_supplied_anywhere + a family still published              -> labelled absent, family present
       no evidence object / class outside the vocabulary             -> unreadable row
  2. SOURCE -- the same rows are checked against the lines they point at: the name the evidence
     row names must appear on that line ("confirmed"), and a failure to find it is
     "contradicted" rather than folded into a zero.  Nothing is executed; the file is read.
  3. READERS -- does anything read the class label rather than the evidence (i.e. branch on it)?

Usage:
  python scripts/e539_label_vs_evidence.py run
  python scripts/e539_label_vs_evidence.py check
  python scripts/e539_label_vs_evidence.py verify
  python scripts/e539_label_vs_evidence.py selftest
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

CARD = "E539-WHICH-PUBLISHED-ROWS-CARRY-A-CLASS-THEIR-EVIDENCE-CONTRADICTS"
STUDY = "E539_label_vs_evidence"
DATE_STAMP = "2026-11-08"
FACE_NAME = "labelvsevidence_latest.json"
DATED_PREFIX = "LABELVSEVIDENCE"

UPSTREAM_FACE = "results/state_tilt/latestfamily_latest.json"

C_STATED = "family_stated_at_the_site"
C_SIGNATURE = "family_required_by_the_signature"
C_WRITTEN = "family_from_the_value_the_site_itself_wrote"
C_ABSENT = "family_not_supplied_anywhere"
CLASS_VOCAB = (C_STATED, C_SIGNATURE, C_WRITTEN, C_ABSENT)

LITERAL_HOWS = (
    "a literal component names the family directory",
    "the literals at the site build the directory",
)

# ------------------------------------------------------------------ verdict buckets
K_STATED_BUT_NAMED = "the_row_is_classed_stated_at_the_site_but_its_own_evidence_names_a_binding"
K_STATED_BUT_EMPTY = "the_row_is_classed_stated_at_the_site_and_publishes_no_family_at_all"
K_SIGNATURE_NAMES_NOTHING = ("the_row_is_classed_required_by_the_signature_and_publishes_neither_"
                             "a_parameter_nor_a_default")
K_WRITTEN_NO_EXPR = "the_row_is_classed_carried_from_its_own_write_and_names_no_written_expression"
K_ABSENT_BUT_FAMILY = "the_row_is_classed_not_supplied_anywhere_and_still_publishes_a_family"
K_NO_EVIDENCE = "the_row_carries_no_evidence_object"
K_OFF_VOCAB = "the_row_carries_a_class_outside_the_published_vocabulary"
K_AGREES = "the_label_and_its_own_evidence_row_agree"

CONTRADICTION_VOCAB = (K_STATED_BUT_NAMED, K_STATED_BUT_EMPTY, K_SIGNATURE_NAMES_NOTHING,
                       K_WRITTEN_NO_EXPR, K_ABSENT_BUT_FAMILY, K_NO_EVIDENCE, K_OFF_VOCAB)

S_CONFIRMED = "the_site_line_carries_the_name_the_evidence_row_names"
S_NEARBY = ("the_name_sits_on_a_neighbouring_line_so_the_row_points_at_the_statement_anchor_"
            "rather_than_the_expression_line")
S_CONTRADICTED = "the_name_the_evidence_row_names_appears_nowhere_in_the_file_it_points_at"
S_ELSEWHERE_IN_FUNCTION = ("the_name_appears_elsewhere_in_the_enclosing_function_but_the_row_points_at_"
                           "a_statement_anchor")
S_ELSEWHERE_IN_FILE = "the_name_appears_elsewhere_in_the_file_only"
S_LINE_MISSING = "the_site_line_does_not_exist_in_the_file_any_more"
S_FILE_UNREADABLE = "the_file_the_row_points_at_could_not_be_read"
S_NOTHING_NAMED = "the_evidence_row_names_no_expression_to_look_for"
SOURCE_VOCAB = (S_CONFIRMED, S_NEARBY, S_ELSEWHERE_IN_FUNCTION, S_ELSEWHERE_IN_FILE,
                S_CONTRADICTED, S_LINE_MISSING, S_FILE_UNREADABLE, S_NOTHING_NAMED)
WINDOW = 3

V_LABELS_HOLD = "every_published_label_agrees_with_its_own_evidence_row_and_with_the_line_it_points_at"
V_LABELS_DISAGREE = ("at_least_one_published_label_disagrees_with_its_own_evidence_row_or_with_the_"
                     "line_it_points_at")
V_EMPTY = "the_upstream_face_publishes_no_rows"
VERDICT_VOCAB = (V_LABELS_HOLD, V_LABELS_DISAGREE, V_EMPTY)


def _now():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _rel(path, root=None):
    return os.path.relpath(path, root or ROOT).replace("\\", "/")


# ------------------------------------------------------------------ population

def load_upstream(root=None):
    path = os.path.join(root or ROOT, UPSTREAM_FACE)
    with open(path, encoding="utf-8") as fh:
        return json.load(fh), _sha256_file(path)


def population(face):
    """Every site row the census face publishes, reads before writes, in face order."""
    rows = []
    for key in ("read_sites", "write_sites"):
        for row in face.get(key) or []:
            rows.append(dict(row, published_in=key))
    return rows


# ------------------------------------------------------------------ internal leg

def _family(ev):
    return ev.get("family_dir") or ev.get("family_suffix")


ABSENT_SENTINELS = ("", "none", "null", "na", "n/a", "''", '""')


def present(value):
    """A value the evidence row actually carries: null, 'None' and '' are published absences.

    E398 publishes ``default_expr`` on every signature row, but rows whose parameter has no
    default carry the four letters ``None`` there.  Truthiness therefore cannot tell "a default
    was published" from "the absence was published" -- the sentinel has to be named.
    """
    if value is None:
        return False
    return str(value).strip().lower() not in ABSENT_SENTINELS


def agree(row):
    """Class the row against the evidence object it carries; pure, no I/O."""
    ev = row.get("evidence")
    cls = row.get("class")
    if not isinstance(ev, dict) or not ev:
        return K_NO_EVIDENCE, {"reason": "evidence object absent or empty"}
    if cls not in CLASS_VOCAB:
        return K_OFF_VOCAB, {"class": cls}
    how = ev.get("how") or ""
    if cls == C_STATED:
        if how and how not in LITERAL_HOWS:
            return K_STATED_BUT_NAMED, {"how": how,
                                        "named": ev.get("constant") or ev.get("binding")}
        if not (_family(ev) or present(ev.get("family_dir")) or present(ev.get("family_suffix"))):
            return K_STATED_BUT_EMPTY, {"how": how, "evidence_keys": sorted(ev)}
        return K_AGREES, {"how": how, "family": _family(ev)}
    if cls == C_SIGNATURE:
        names_something = (present(ev.get("parameter")) or present(ev.get("local_alias"))
                           or present(ev.get("default_dir")) or present(ev.get("default_expr")))
        if not names_something:
            return K_SIGNATURE_NAMES_NOTHING, {"evidence_keys": sorted(ev)}
        return K_AGREES, {"parameter": ev.get("parameter"),
                          "default_dir": ev.get("default_dir") if present(ev.get("default_dir")) else None}
    if cls == C_WRITTEN:
        if not present(ev.get("written_expr")):
            return K_WRITTEN_NO_EXPR, {"evidence_keys": sorted(ev)}
        return K_AGREES, {"written_expr": ev.get("written_expr")}
    # C_ABSENT
    if present(_family(ev)):
        return K_ABSENT_BUT_FAMILY, {"how": how, "family": _family(ev)}
    return K_AGREES, {"how": how}


# ------------------------------------------------------------------ source leg

def names_to_look_for(ev):
    """What the evidence row itself says should be visible on the site line."""
    if not isinstance(ev, dict):
        return []
    for key in ("constant", "binding", "parameter", "local_alias"):
        value = ev.get(key)
        if value:
            return [str(value).split(".")[-1]]
    expr = ev.get("written_expr") or ev.get("default_expr")
    if expr:
        words = [w for w in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", str(expr))
                 if len(w) > 2 and w not in ("open", "os", "path", "join", "json", "load",
                                             "loads", "read", "self", "str", "null")]
        return words[-1:] if words else []
    family = _family(ev)
    if family:
        parts = [p for p in str(family).replace("\\", "/").split("/") if p]
        return parts[-1:]
    return []


def source_leg(rows, root=None):
    root = root or ROOT
    cache = {}
    out = []
    for row in rows:
        rel = row.get("file")
        line = row.get("line")
        names = names_to_look_for(row.get("evidence"))
        if not rel or not line:
            out.append(S_FILE_UNREADABLE)
            continue
        if rel not in cache:
            try:
                with open(os.path.join(root, rel), encoding="utf-8") as fh:
                    cache[rel] = fh.read().split("\n")
            except OSError:
                cache[rel] = None
        text_lines = cache[rel]
        if text_lines is None:
            out.append(S_FILE_UNREADABLE)
            continue
        if not names:
            out.append(S_NOTHING_NAMED)
            continue
        if line < 1 or line > len(text_lines):
            out.append(S_LINE_MISSING)
            continue
        wanted = [n.lower() for n in names]
        exact = text_lines[line - 1].lower()
        if any(n in exact for n in wanted):
            out.append(S_CONFIRMED)
            continue
        lo = max(0, line - 1 - WINDOW)
        hi = min(len(text_lines), line - 1 + WINDOW + 1)
        neighbourhood = "\n".join(text_lines[lo:hi]).lower()
        if any(n in neighbourhood for n in wanted):
            out.append(S_NEARBY)
            continue
        span = function_span(cache.setdefault(("span", rel), None) or _spans_of(cache, rel, root),
                             line)
        if span:
            body = "\n".join(text_lines[span[0] - 1:span[1]]).lower()
            if any(n in body for n in wanted):
                out.append(S_ELSEWHERE_IN_FUNCTION)
                continue
        whole = "\n".join(text_lines).lower()
        out.append(S_ELSEWHERE_IN_FILE if any(n in whole for n in wanted) else S_CONTRADICTED)
    return out


def function_span(span_list, line):
    """The innermost (start, end) the line sits inside, or None at module level."""
    best = None
    for start, end in span_list or []:
        if start <= line <= end and (best is None or end - start < best[1] - best[0]):
            best = (start, end)
    return best


def _spans_of(cache, rel, root):
    """Line spans of every def in the file, memoised on the read cache."""
    try:
        with open(os.path.join(root, rel), encoding="utf-8") as fh:
            tree = ast.parse(fh.read())
    except (OSError, SyntaxError, ValueError):
        cache[("span", rel)] = []
        return []
    spans = [(n.lineno, getattr(n, "end_lineno", n.lineno) or n.lineno)
             for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    cache[("span", rel)] = spans
    return spans


# ------------------------------------------------------------------ readers leg

CLASS_LITERALS = CLASS_VOCAB
SKIP_DIRS = {".git", ".venv", "__pycache__", "node_modules", "results", "data", "logs"}
BRANCH_HINTS = ("==", "!=", " in (", " in [", "not in", "if ", "elif ")


def label_readers(root=None):
    root = root or ROOT
    hits = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in sorted(dirnames) if d not in SKIP_DIRS and not d.startswith(".")]
        for name in sorted(filenames):
            if not name.endswith(".py"):
                continue
            rel = _rel(os.path.join(dirpath, name), root)
            if rel in ("scripts/e539_label_vs_evidence.py", "scripts/e398_latest_family.py"):
                continue
            try:
                with open(os.path.join(dirpath, name), encoding="utf-8") as fh:
                    text = fh.read()
            except OSError:
                continue
            if not any(c in text for c in CLASS_LITERALS):
                continue
            for i, line in enumerate(text.split("\n"), 1):
                for c in CLASS_LITERALS:
                    if c in line:
                        hits.append({
                            "file": rel, "line": i, "class": c,
                            "tests_the_label": any(h in line for h in BRANCH_HINTS),
                            "text": line.strip()[:160],
                        })
                        break
    return hits


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
    if summary["rows_agreeing_internally"] < summary["rows"]:
        return V_LABELS_DISAGREE
    if summary.get("source_contradicted", 0) > 0:
        return V_LABELS_DISAGREE
    return V_LABELS_HOLD


def analyse(rows, root=None):
    out = []
    sources = source_leg(rows, root)
    for row, src in zip(rows, sources):
        key, detail = agree(row)
        out.append({
            "site": row.get("site"), "file": row.get("file"), "line": row.get("line"),
            "kind": row.get("kind"), "tier": row.get("tier"),
            "class": row.get("class"), "published_in": row.get("published_in"),
            "how": (row.get("evidence") or {}).get("how"),
            "evidence": row.get("evidence"),
            "agreement": key, "agreement_detail": detail,
            "names_looked_for": names_to_look_for(row.get("evidence")),
            "source_check": src,
        })
    return out


def build(root=None, write=True, rows=None, upstream_sha=None):
    root = root or ROOT
    if rows is None:
        face, upstream_sha = load_upstream(root)
        rows = population(face)
    sites = analyse(rows, root)
    agreement = _count([s["agreement"] for s in sites], CONTRADICTION_VOCAB + (K_AGREES,))
    source_check = _count([s["source_check"] for s in sites], SOURCE_VOCAB)
    by_class_contradicting = {}
    for cls in CLASS_VOCAB:
        by_class_contradicting[cls] = sum(
            1 for s in sites
            if s["class"] == cls and s["agreement"] in CONTRADICTION_VOCAB)
    readers = label_readers(root)
    summary = {
        "rows": len(sites),
        "rows_read": sum(1 for s in sites if s.get("published_in") == "read_sites"),
        "rows_written": sum(1 for s in sites if s.get("published_in") == "write_sites"),
        "by_agreement": agreement,
        "rows_agreeing_internally": agreement[K_AGREES],
        "rows_contradicting_their_evidence": sum(agreement[k] for k in CONTRADICTION_VOCAB),
        "by_class_contradicting": by_class_contradicting,
        "signature_rows_without_a_default": sum(
            1 for s in sites
            if s["class"] == C_SIGNATURE
            and not present((s.get("evidence") or {}).get("default_dir"))
            and not present((s.get("evidence") or {}).get("default_expr"))),
        "stated_rows_whose_family_is_a_name_not_a_literal": by_class_contradicting[C_STATED],
        "how_of_the_stated_rows": _count([s.get("how") for s in sites
                                          if s["class"] == C_STATED
                                          and present(s.get("how"))],
                                         LITERAL_HOWS + tuple(sorted({
                                             s.get("how") for s in sites
                                             if s["class"] == C_STATED
                                             and present(s.get("how"))
                                             and s.get("how") not in LITERAL_HOWS}))),
        "agreement_sums_to_the_rows": sum(agreement.values()) == len(sites),
        "by_source_check": source_check,
        "rows_checkable": len(sites) - source_check[S_NOTHING_NAMED],
        "source_confirmed": source_check[S_CONFIRMED],
        "source_confirmed_in_the_neighbourhood": source_check[S_NEARBY],
        "source_contradicted": (source_check[S_CONTRADICTED] + source_check[S_LINE_MISSING]
                                + source_check[S_FILE_UNREADABLE]),
        "label_readers": len({(r["file"], r["line"]) for r in readers}),
        "label_readers_that_branch_on_it": len({(r["file"], r["line"]) for r in readers
                                                if r["tests_the_label"]}),
    }
    return {
        "card": CARD,
        "study": STUDY,
        "question": ("does every class label E398 publishes survive the evidence row it carries and "
                     "the source line that row points at?"),
        "evidence_cutoff": DATE_STAMP,
        "generated": _now(),
        "population_source": ("%s::population() -- every read_sites row then every write_sites row "
                              "of the census face" % os.path.basename(__file__)),
        "upstream_face": UPSTREAM_FACE,
        "upstream_sha256": upstream_sha,
        "class_vocab": list(CLASS_VOCAB),
        "literal_hows": list(LITERAL_HOWS),
        "agreement_vocab": list(CONTRADICTION_VOCAB + (K_AGREES,)),
        "source_vocab": list(SOURCE_VOCAB),
        "verdict_vocab": list(VERDICT_VOCAB),
        "summary": summary,
        "verdict": _verdict(summary),
        "sites": sites,
        "label_readers": readers,
        "method_limits": [
            "the source leg looks for the last dotted component of the name the evidence row "
            "carries; a line that spells the same name differently (getattr, a loop variable) is "
            "published as contradicted rather than resolved",
            "a literal-hows row is checked by its last family component, not by the whole path, so "
            "a line that names the tail but builds a different head still reads confirmed",
            "the reader leg counts class literals in .py files outside results/ and data/, and "
            "calls a line a branch when it carries a comparison or conditional token; it does not "
            "type-check which value is compared",
            "the face is read as published on disk at its own cutoff; nothing is rebuilt upstream "
            "and nothing is executed but this measurement",
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
                "verdict", "sites", "method_limits"):
        if key not in face:
            problems.append("missing key %s" % key)
    if problems:
        return problems
    summary, sites = face["summary"], face["sites"]
    if summary["rows"] != len(sites):
        problems.append("rows does not equal the site rows")
    agreement = _count([s.get("agreement") for s in sites], face["agreement_vocab"])
    if agreement != summary["by_agreement"]:
        problems.append("by_agreement does not re-derive from the sites")
    if sum(agreement.values()) != len(sites):
        problems.append("a site carries an agreement outside the vocabulary")
    contradicting = sum(agreement[k] for k in CONTRADICTION_VOCAB)
    if summary["rows_contradicting_their_evidence"] != contradicting:
        problems.append("rows_contradicting_their_evidence does not re-derive")
    if summary["rows_agreeing_internally"] != agreement[K_AGREES]:
        problems.append("rows_agreeing_internally does not re-derive")
    source = _count([s.get("source_check") for s in sites], face["source_vocab"])
    if source != summary["by_source_check"]:
        problems.append("by_source_check does not re-derive from the sites")
    if summary["rows_checkable"] != len(sites) - source[S_NOTHING_NAMED]:
        problems.append("rows_checkable does not equal the rows with a name to look for")
    if summary["source_confirmed"] != source[S_CONFIRMED]:
        problems.append("source_confirmed does not re-derive")
    if summary["source_confirmed_in_the_neighbourhood"] != source[S_NEARBY]:
        problems.append("source_confirmed_in_the_neighbourhood does not re-derive")
    contradicting = (source[S_CONTRADICTED] + source[S_LINE_MISSING] + source[S_FILE_UNREADABLE])
    if summary["source_contradicted"] != contradicting:
        problems.append("source_contradicted does not re-derive")
    for cls in CLASS_VOCAB:
        want = sum(1 for s in sites
                   if s.get("class") == cls and s.get("agreement") in CONTRADICTION_VOCAB)
        if summary["by_class_contradicting"].get(cls, 0) != want:
            problems.append("by_class_contradicting[%s] does not re-derive" % cls)
    if face["verdict"] != _verdict(summary):
        problems.append("verdict does not re-derive from the summary")
    if face["verdict"] not in VERDICT_VOCAB:
        problems.append("verdict is outside the vocabulary")
    for site in sites:
        if site.get("agreement") not in face["agreement_vocab"]:
            problems.append("site %s carries %r" % (site.get("site"), site.get("agreement")))
        if site.get("source_check") not in face["source_vocab"]:
            problems.append("site %s carries source %r" % (site.get("site"),
                                                           site.get("source_check")))
        reread, _detail = agree({"class": site.get("class"), "evidence": site.get("evidence")})
        if reread != site.get("agreement"):
            problems.append("site %s is published as %r but its evidence re-reads as %r"
                            % (site.get("site"), site.get("agreement"), reread))
    declared = face["summary"]["label_readers"]
    recomputed = len({(r["file"], r["line"]) for r in face["label_readers"]})
    if declared != recomputed and not problems:
        problems.append("label_readers does not equal the reader rows")
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
    same_readers = rebuilt["label_readers"] == face["label_readers"]
    problems = face_problems(face)
    ok = same_sites and same_summary and same_readers and not problems
    print("verify: sites_identical=%s summary_identical=%s readers_identical=%s problems=%s"
          % (same_sites, same_summary, same_readers,
             json.dumps(problems, ensure_ascii=False)[:400]))
    if not same_summary:
        print("verify: summary_delta=%s" % json.dumps(
            {k: (face["summary"].get(k), rebuilt["summary"].get(k))
             for k in set(face["summary"]) | set(rebuilt["summary"])
             if face["summary"].get(k) != rebuilt["summary"].get(k)}, ensure_ascii=False)[:900])
    return 0 if ok else 1


# ------------------------------------------------------------------ selftest

def _row(cls, how, **ev):
    evidence = {"how": how}
    evidence.update(ev)
    return {"class": cls, "evidence": evidence, "site": "x.py:1", "file": "x.py", "line": 1}


def _fixture_rows():
    return [
        _row(C_STATED, "the literals at the site build the directory", family_dir="data/live"),
        _row(C_STATED, "an imported constant names the directory", constant="D.LIVE_DIR",
             family_dir="data/live"),
        _row(C_STATED, "a literal component names the family directory"),
        _row(C_SIGNATURE, "signature parameter", parameter="family", default_dir="data/live",
             default_expr="'data/live'"),
        _row(C_SIGNATURE, "signature parameter", default_dir=None, default_expr="None"),
        _row(C_WRITTEN, "carried from this function's own write", written_expr="out_dir"),
        _row(C_WRITTEN, "carried from this function's own write"),
        _row(C_ABSENT, "no literal, constant, parameter or prior write"),
        _row(C_ABSENT, "no literal, constant, parameter or prior write", family_dir="data/live"),
        {"class": C_STATED, "site": "y.py:1"},
        {"class": "some_new_class", "evidence": {"how": "x"}, "site": "z.py:1"},
    ]


def selftest():
    fails = []
    ran = []

    def ok(name, cond, detail=""):
        ran.append(name)
        print(("PASS " if cond else "FAIL ") + name + (" -- " + detail if detail else ""))
        if not cond:
            fails.append(name)

    rows = _fixture_rows()
    keys = [agree(r)[0] for r in rows]
    expect = [K_AGREES, K_STATED_BUT_NAMED, K_STATED_BUT_EMPTY, K_AGREES,
              K_SIGNATURE_NAMES_NOTHING, K_AGREES, K_WRITTEN_NO_EXPR, K_AGREES,
              K_ABSENT_BUT_FAMILY, K_NO_EVIDENCE, K_OFF_VOCAB]
    ok("fixture arms classify as published", keys == expect,
       json.dumps(keys, ensure_ascii=False)[:200])
    counted = _count(keys, CONTRADICTION_VOCAB + (K_AGREES,))
    ok("agreement counts sum to the rows", sum(counted.values()) == len(rows))
    ok("the derived verdict refuses a contradicting population",
       _verdict({"rows": 2, "rows_agreeing_internally": 1, "source_contradicted": 0})
       == V_LABELS_DISAGREE)
    ok("the derived verdict accepts a clean population",
       _verdict({"rows": 2, "rows_agreeing_internally": 2, "source_contradicted": 0})
       == V_LABELS_HOLD)
    ok("an empty population is its own verdict",
       _verdict({"rows": 0, "rows_agreeing_internally": 0, "source_contradicted": 0}) == V_EMPTY)
    ok("a contradicted source line outranks an internally clean label",
       _verdict({"rows": 2, "rows_agreeing_internally": 2, "source_contradicted": 1})
       == V_LABELS_DISAGREE)
    ok("names_to_look_for prefers the constant over the family",
       names_to_look_for({"how": "x", "constant": "D.LIVE_DIR", "family_dir": "data/live"})
       == ["LIVE_DIR"])
    ok("names_to_look_for falls back to the family tail",
       names_to_look_for({"how": "x", "family_dir": "data/live"}) == ["live"])
    ok("names_to_look_for names nothing when the evidence names nothing",
       names_to_look_for({"how": "no literal, constant, parameter or prior write"}) == [])
    ok("a published absence is not a published default",
       present(None) is False and present("None") is False and present("data/live") is True,
       "the sentinel 'None' has to be named or a 27-row class is invented")

    # A published face that hands a label and its evidence disagreeing must be refused.
    upstream, sha = load_upstream()
    clean = build(rows=population(upstream), upstream_sha=sha, write=False)
    ok("the live face builds", clean["summary"]["rows"] > 0)
    ok("the live face's own gate passes", face_problems(clean) == [],
       json.dumps(face_problems(clean), ensure_ascii=False)[:300])

    doctored = json.loads(json.dumps(clean))
    doctored["verdict"] = "a_verdict_this_study_never_publishes"
    ok("a hand-written verdict is refused", face_problems(doctored) != [])

    doctored = json.loads(json.dumps(clean))
    doctored["sites"][0]["agreement"] = K_AGREES  # a counted row deleted from its bucket
    doctored["summary"]["by_agreement"][K_AGREES] -= 1
    ok("a row moved out of its bucket is refused", face_problems(doctored) != [])

    doctored = json.loads(json.dumps(clean))
    doctored["summary"]["rows_contradicting_their_evidence"] += 1
    ok("an inflated contradiction count is refused", face_problems(doctored) != [])

    doctored = json.loads(json.dumps(clean))
    doctored["summary"]["source_confirmed"] = 0
    ok("a rewritten source tally is refused", face_problems(doctored) != [])

    doctored = json.loads(json.dumps(clean))
    for site in doctored["sites"]:
        if site["class"] == C_STATED:
            site["agreement"] = K_AGREES
            site["how"] = "a local binding names the directory"
            break
    ok("a stated row agreeing on a non-literal how is refused", face_problems(doctored) != [])

    print("selftest: %d/%d" % (len(ran) - len(fails), len(ran)))
    return 0 if not fails else 1


# ------------------------------------------------------------------ main

def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "run"
    if cmd == "run":
        face = build()
        dated, latest = write_face(face)
        print("run: %s (%s)" % (dated, latest))
        print(json.dumps(face["summary"], ensure_ascii=False, indent=1))
        print("verdict: %s" % face["verdict"])
        return 0
    if cmd == "check":
        return check()
    if cmd == "verify":
        return verify()
    if cmd == "selftest":
        return selftest()
    print("usage: python scripts/e539_label_vs_evidence.py [run|check|verify|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main())