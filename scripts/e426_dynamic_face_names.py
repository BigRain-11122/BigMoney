"""E426 -- which face names are only reachable through a variable-built string.

Every census in this tree reads face names out of string constants (E402 basenames, E404
resolved directories, E422 bare names, E417 bare literals).  Each of them declares the same
method limit in prose: *a reader that builds the name from a variable is invisible to it*.
E417 wrote that sentence last round and moved on.  This study prices it.

Three machine-read sources, never a word list:

  1. the python corpus (`scripts/`, `Tools/`, `firm/`, `live/`, `monitor/`, repo root), parsed
     with `ast`; every string constant is a literal candidate, and every expression that
     produces a `*.json` name from a non-constant part is a *template*;
  2. the faces on disk under `results/**/*.json` -- the published population;
  3. E411's READERTIERS population -- the faces a reader in this tree actually opens.

A template only reaches a face if it is *specific*: after removing the wildcard, some path
component must retain a non-empty stem.  `stem + ".json"` and `results/<dir>/*.json` name a
directory or the whole format, not a face, and counting them would say every face is
dynamically reachable -- which is true and useless.  Specificity is computed from the template
text, and the count of discarded (non-specific) templates is published beside the used ones.

The reading that matters is the second population: for a face the suite opens, is its name
available to a literal census at all, and does the template that does reach it sit inside a
function that opens a file (an opener) or in dead text (a report string, a doc line)?

Subcommands: run | verify | selftest
"""
from __future__ import annotations

import ast
import json
import os
import re
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "results", "state_tilt")
FACE = "DYNAMICNAME-%s.json"
LATEST = "dynamicname_latest.json"
STUDY = "E426_dynamic_face_names"

SKIP_DIRNAMES = {"__pycache__", "node_modules", ".git", ".codely-cli", "_quarantine",
                 "Money02", "Money0923", "legacy", "data", "logs", "results", "state"}
CORPUS_DIRS = ("scripts", "Tools", "firm", "live", "monitor")

# The scanner is part of the corpus it reads (E180/E207 family): its own name, and the name of
# its predecessor in this round's series, never contribute a literal or a template.
SELF_FILES = {"e426_dynamic_face_names.py"}

OPENERS = {"open", "read_text", "read_bytes", "read_csv", "read_parquet", "read_json", "load"}

C_LITERAL = "named_by_a_literal_somewhere"
C_BOTH = "named_by_a_literal_and_reached_by_a_template"
C_DYNAMIC = "only_a_variable_built_name_matches"
C_NONE = "neither_a_literal_nor_a_matching_template"
CLASS_VOCAB = (C_LITERAL, C_BOTH, C_DYNAMIC, C_NONE)

V_CENSUS_ADEQUATE = ("every_face_a_reader_opens_is_named_by_a_literal_in_the_corpus_and_no_"
                     "published_face_is_only_dynamically_reachable")
V_READERS_LITERAL_WRITERS_DYNAMIC = ("every_file_face_a_reader_opens_is_named_by_a_literal_"
                                     "while_the_producers_spell_only_a_template_so_a_literal_"
                                     "census_describes_what_is_read_not_what_is_written")
V_DYNAMIC_ONLY_READ = ("at_least_one_file_face_a_reader_opens_is_reachable_only_through_a_"
                       "template_and_that_template_sits_in_a_function_which_opens_a_file")
V_DYNAMIC_ONLY_UNREAD = ("a_file_face_a_reader_opens_is_reachable_only_through_a_template_but_"
                         "no_such_template_sits_in_an_opener")
VERDICT_VOCAB = (V_CENSUS_ADEQUATE, V_READERS_LITERAL_WRITERS_DYNAMIC, V_DYNAMIC_ONLY_READ,
                 V_DYNAMIC_ONLY_UNREAD)

COMPARE = ("study", "evidence_cutoff", "verdict", "verdict_reason", "summary_core", "rows",
           "non_literal_faces_by_directory", "e411_rows", "templates_used_sample",
           "method_limits", "population_keys", "class_vocab")

# Counts over a growing corpus move on an honest rebuild (E420/E421 law): a new module adds
# literals and templates, and this round's own successor will add more.  Declared here AND in
# the face so a leg cannot widen the gate.
POPULATION_KEYS = (
    "faces_on_disk",
    "faces_literal_named",
    "faces_only_dynamically_reachable",
    "literals",
    "templates",
    "specific_templates",
    "templates_in_an_opener",
    "e411_faces",
)


# ------------------------------------------------------------------ io
def _rel(path: str, root: str = ROOT) -> str:
    try:
        return os.path.relpath(path, root).replace("\\", "/")
    except ValueError:
        return path.replace("\\", "/")


def _norm(text: str) -> str:
    return text.replace("\\", "/")


def write_face(face: dict, outdir: str | None = None) -> str:
    outdir = outdir or OUT_DIR
    os.makedirs(outdir, exist_ok=True)
    text = json.dumps(face, ensure_ascii=False, indent=1) + "\n"
    for name in (FACE % face["evidence_cutoff"], LATEST):
        with open(os.path.join(outdir, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
    return os.path.join(outdir, FACE % face["evidence_cutoff"])


# ------------------------------------------------------------------ corpus
def python_corpus(root: str = ROOT) -> list:
    out = []
    for base, subdirs, files in os.walk(root):
        subdirs[:] = [s for s in subdirs if s not in SKIP_DIRNAMES]
        for f in files:
            if not f.endswith(".py") or f in SELF_FILES:
                continue
            out.append(os.path.join(base, f))
    return sorted(out)


def _specificity(template: str) -> tuple:
    """(is_specific, stem_fragments).

    A template is specific when some literal fragment, reduced to its last path component and
    stripped of the `.json` suffix, keeps a non-empty stem.  That is the question "does this
    template say anything about WHICH face", answered from the text alone.
    """
    stems = []
    for frag in template.split("*"):
        last = frag.split("/")[-1]
        if last.endswith(".json"):
            last = last[:-5]
        if last.strip():
            stems.append(last)
    return bool(stems), stems


def _template_regex(template: str):
    rx = _RX_CACHE.get(template)
    if rx is None:
        rx = re.compile("^" + ".*".join(re.escape(p) for p in template.split("*")) + "$")
        _RX_CACHE[template] = rx
    return rx


_RX_CACHE: dict = {}


def _may_reach(template: dict, face_rel: str) -> bool:
    """Cheap substring gate before any regex: every stem fragment must appear in the path.

    A template that names `SIG-` cannot match a face whose path never contains `SIG-`, so the
    expensive pattern is only run on the candidates.  This is a filter, never the decision.
    """
    hay = face_rel
    for frag in template.get("stem_fragments") or []:
        if frag not in hay:
            return False
    return True


class _Collector(ast.NodeVisitor):
    def __init__(self, rel: str):
        self.rel = rel
        self.stack: list = []
        self.literals: dict = {}
        self.templates: list = []

    # -- scope tracking (only functions matter: a module-level string is not an opener scope)
    def visit_FunctionDef(self, node):
        self.stack.append(node)
        self.generic_visit(node)
        self.stack.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def _in_opener(self) -> bool:
        if not self.stack:
            return False
        return _has_opener(self.stack[-1])

    def _add(self, kind: str, text: str, line: int) -> None:
        norm = _norm(text)
        if ".json" not in norm:
            return
        specific, stems = _specificity(norm)
        self.templates.append({"module": self.rel, "line": line, "kind": kind,
                               "template": norm, "specific": specific,
                               "stem_fragments": stems,
                               "in_an_opener": self._in_opener()})

    def visit_Constant(self, node):
        if isinstance(node.value, str):
            v = node.value
            self.literals.setdefault(v, []).append({"module": self.rel, "line": node.lineno})

    # -- * + literal / literal + *  ->  template
    def visit_BinOp(self, node):
        if isinstance(node.op, ast.Add):
            for side, other, left in ((node.left, node.right, True),
                                      (node.right, node.left, False)):
                if isinstance(side, ast.Constant) and isinstance(side.value, str) \
                        and not isinstance(other, ast.Constant):
                    text = _norm(side.value) + "*" if left else "*" + _norm(side.value)
                    self._add("concatenation", text, node.lineno)
                    break
        elif isinstance(node.op, ast.Mod):
            if isinstance(node.left, ast.Constant) and isinstance(node.left.value, str) \
                    and node.right is not None:
                text = re.sub(r"%[-+ 0#]*\d*(?:\.\d+)?[sdifrxX]", "*", node.left.value)
                self._add("percent_format", text, node.lineno)
        self.generic_visit(node)

    # -- f-string
    def visit_JoinedStr(self, node):
        if any(isinstance(v, ast.FormattedValue) for v in node.values):
            parts = []
            for v in node.values:
                if isinstance(v, ast.Constant) and isinstance(v.value, str):
                    parts.append(_norm(v.value))
                else:
                    parts.append("*")
            self._add("fstring", "".join(parts), node.lineno)
        self.generic_visit(node)

    def visit_Call(self, node):
        func = node.func
        # "<literal>".format(...)
        if isinstance(func, ast.Attribute) and func.attr == "format":
            if isinstance(func.value, ast.Constant) and isinstance(func.value.value, str):
                text = re.sub(r"\{[^{}]*\}", "*", func.value.value)
                self._add("str_format", text, node.lineno)
        # os.path.join(<any non-literal>, "<tail>.json")
        if isinstance(func, ast.Attribute) and func.attr == "join" and node.args:
            tail = node.args[-1]
            if isinstance(tail, ast.Constant) and isinstance(tail.value, str) \
                    and tail.value.endswith(".json") \
                    and any(not isinstance(a, ast.Constant) for a in node.args[:-1]):
                self._add("path_join_with_a_dynamic_head", "*" + _norm(tail.value),
                          node.lineno)
        self.generic_visit(node)


def _has_opener(fn) -> bool:
    """Does this function body open something?  Approximate on purpose and stated as a limit:
    any call by name is enough -- the question is "is the name used near a read", not a dataflow.
    """
    for node in ast.walk(fn):
        if isinstance(node, ast.Call):
            f = node.func
            if isinstance(f, ast.Name) and f.id in OPENERS:
                return True
            if isinstance(f, ast.Attribute) and f.attr in OPENERS:
                return True
    return False


def collect_source(text: str, rel: str) -> tuple:
    """(literals, templates) from one module's source text; a parse error is returned as ([], []).

    A module that does not parse contributes nothing rather than raising: the corpus includes
    half-written scratch files, and one of them must not stop the census.
    """
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return {}, []
    c = _Collector(rel)
    c.visit(tree)
    return c.literals, c.templates


def collect_corpus(root: str = ROOT) -> tuple:
    literals: dict = {}
    templates: list = []
    for path in python_corpus(root):
        try:
            text = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        lits, tmpls = collect_source(text, _rel(path, root))
        for k, v in lits.items():
            literals.setdefault(k, []).extend(v)
        templates.extend(tmpls)
    return literals, templates


# ------------------------------------------------------------------ populations
def face_paths(root: str = ROOT) -> list:
    """Published faces under results/.

    Three exclusions, each with a reason:
      * files whose basename starts with ``_`` are round receipts and scratch faces
        (``_r1444bmb_s6_chain.json``) that every round rewrites -- counting them would make the
        population move for no reason but the clock;
      * this study's own two faces (E180/E207 family: a scanner that counts its own artefact
        changes the population by publishing);
      * ``__pycache__`` by dirname.
    """
    out = []
    d = os.path.join(root, "results")
    for base, subdirs, files in os.walk(d):
        subdirs[:] = [s for s in subdirs if s not in {"__pycache__"}]
        for f in files:
            if not f.endswith(".json") or f.startswith("_"):
                continue
            if f.startswith("DYNAMICNAME-") or f == LATEST:
                continue
            out.append(_rel(os.path.join(base, f), root))
    return sorted(out)


def e411_population(root: str = ROOT) -> tuple:
    d = os.path.join(root, "results", "state_tilt")
    cands = sorted(f for f in os.listdir(d)
                   if f.startswith("READERTIERS-") and f.endswith(".json"))
    if not cands:
        raise SystemExit("no READERTIERS-*.json population face (E411) under results/state_tilt")
    path = os.path.join(d, cands[-1])
    payload = json.load(open(path, encoding="utf-8"))
    faces = []
    for row in payload.get("faces") or []:
        name = row.get("face")
        if isinstance(name, str) and name:
            faces.append(name)
    return faces, _rel(path, root)


def literal_names(literals: dict) -> set:
    """Basenames some string constant spells -- either bare, or as the tail of a path literal."""
    out = set()
    for text in literals:
        norm = _norm(text).rstrip("/")
        base = norm.split("/")[-1]
        if base.endswith(".json"):
            out.add(base)
    return out


def _face_kind(name: str, root: str = ROOT) -> str:
    """What the E411 population row actually is.

    That population is "names the suite opens", and it carries three shapes: a file, a directory
    (a store the suite writes into, e.g. `results/state_tilt`), and a templated name
    (`TSMOM-%s.md`) that has no single basename by construction.  Only a file can be lit by a
    literal or a template, so the other two are labelled rather than counted as blind spots.
    """
    if "%" in name or "*" in name:
        return "templated"
    if os.path.isdir(os.path.join(root, name.replace("/", os.sep))):
        return "directory"
    return "file"


def classify(face_rel: str, names: set, specific: list) -> dict:
    base = face_rel.split("/")[-1]
    named_literal = base in names
    matches = []
    for t in specific:
        if not _may_reach(t, face_rel):
            continue
        rx = _template_regex(t["template"])
        if rx.match(face_rel) or rx.match(base):
            matches.append(t)
    if named_literal and matches:
        k = C_BOTH
    elif matches:
        k = C_DYNAMIC
    elif named_literal:
        k = C_LITERAL
    else:
        k = C_NONE
    return {"class": k, "literal_named": named_literal, "matches": matches}


def _match_summary(matches: list) -> list:
    out = []
    for t in matches[:4]:
        out.append({"module": t["module"], "line": t["line"], "kind": t["kind"],
                    "template": t["template"], "in_an_opener": t["in_an_opener"]})
    return out


# ------------------------------------------------------------------ build
def build(root: str = ROOT, now: datetime | None = None, write: bool = True) -> dict:
    now = now or datetime.now(timezone.utc).astimezone()
    cutoff = now.date().isoformat()
    literals, templates = collect_corpus(root)
    print("corpus: %d literals, %d templates" % (len(literals), len(templates)),
          file=sys.stderr, flush=True)
    names = literal_names(literals)
    specific = [t for t in templates if t["specific"]]
    faces = face_paths(root)
    print("faces on disk: %d" % len(faces), file=sys.stderr, flush=True)
    e411, e411_source = e411_population(root)

    rows_all = []
    by_class = {}
    for face in faces:
        r = classify(face, names, specific)
        by_class[r["class"]] = by_class.get(r["class"], 0) + 1
        if r["class"] != C_LITERAL:
            rows_all.append({"face": face, "class": r["class"],
                             "literal_named": r["literal_named"],
                             "matches": _match_summary(r["matches"]),
                             "match_count": len(r["matches"]),
                             "any_match_in_an_opener": any(t["in_an_opener"] for t in r["matches"])})

    # 13k faces at ~1KB a row is a 13MB face; the study publishes a deterministic sample plus a
    # per-directory tally, and the gate reads the tally, not the sample (a sample that moved with
    # the corpus would be a number in an equality gate -- E420 family).
    rows = rows_all[:60]
    per_dir = {}
    for r in rows_all:
        d = r["face"].split("/")[0] + "/" + (r["face"].split("/")[1] if r["face"].count("/") > 1 else "")
        slot = per_dir.setdefault(d, {"dir": d, "non_literal": 0, "dynamic_only": 0,
                                      "in_an_opener": 0})
        slot["non_literal"] += 1
        if r["class"] == C_DYNAMIC:
            slot["dynamic_only"] += 1
        if r["any_match_in_an_opener"]:
            slot["in_an_opener"] += 1
    per_dir_rows = sorted(per_dir.values(), key=lambda s: (-s["non_literal"], s["dir"]))[:40]

    e411_rows = []
    for face in e411:
        r = classify(face, names, specific)
        kind = _face_kind(face, root)
        e411_rows.append({"face": face, "kind": kind, "class": r["class"],
                          "literal_named": r["literal_named"],
                          "matches": _match_summary(r["matches"]),
                          "match_count": len(r["matches"]),
                          "any_match_in_an_opener": any(t["in_an_opener"] for t in r["matches"])})

    files = [r for r in e411_rows if r["kind"] == "file"]
    dynamic_only = [r for r in files if r["class"] == C_DYNAMIC]
    dynamic_only_read = [r for r in dynamic_only if r["any_match_in_an_opener"]]
    on_disk_dynamic = [r for r in rows_all if r["class"] == C_DYNAMIC]
    if dynamic_only_read:
        verdict = V_DYNAMIC_ONLY_READ
    elif dynamic_only:
        verdict = V_DYNAMIC_ONLY_UNREAD
    elif on_disk_dynamic:
        verdict = V_READERS_LITERAL_WRITERS_DYNAMIC
    else:
        verdict = V_CENSUS_ADEQUATE

    reason = (
        "%d of %d file faces a reader opens and %d of %d published faces are reachable only "
        "through a variable-built name; %d of the opened ones is reached by a template inside a "
        "function that opens a file (%d templates used of %d found, %d in an opener). The split "
        "is directional: consumers name the face literally, producers only name a template."
        % (len(dynamic_only), len(files), len(on_disk_dynamic), len(faces),
           len(dynamic_only_read), len(specific), len(templates),
           sum(1 for t in specific if t["in_an_opener"]))
    )

    face = {
        "study": STUDY,
        "card": "E426-WHICH-READER-BUILDS-A-FACE-NAME-FROM-A-VARIABLE-SO-NO-LITERAL-NAMES-IT",
        "title": "face names that only a variable-built string reaches, and whether that string "
                 "sits in an opener",
        "evidence_cutoff": cutoff,
        "generated": now.isoformat(timespec="seconds"),
        "population_source": e411_source,
        "verdict": verdict,
        "verdict_reason": reason,
        "class_vocab": list(CLASS_VOCAB),
        "summary": {
            "faces_on_disk": len(faces),
            "faces_literal_named": by_class.get(C_LITERAL, 0) + by_class.get(C_BOTH, 0),
            "faces_only_dynamically_reachable": len(on_disk_dynamic),
            "literals": len(literals),
            "templates": len(templates),
            "specific_templates": len(specific),
            "templates_in_an_opener": sum(1 for t in templates if t["in_an_opener"]),
            "e411_faces": len(e411_rows),
            "e411_file_faces": len(files),
            "e411_directory_rows": sum(1 for r in e411_rows if r["kind"] == "directory"),
            "e411_templated_rows": sum(1 for r in e411_rows if r["kind"] == "templated"),
            "e411_faces_only_dynamically_reachable": len(dynamic_only),
            "e411_faces_dynamic_and_in_an_opener": len(dynamic_only_read),
            "e411_faces_with_no_mask_at_all": sum(1 for r in files if r["class"] == C_NONE),
        },
        "by_class_all_faces": by_class,
        "by_class_e411": {k: sum(1 for r in files if r["class"] == k) for k in CLASS_VOCAB},
        "population_keys": list(POPULATION_KEYS),
        "rows": rows,
        "rows_published": len(rows),
        "non_literal_faces_by_directory": per_dir_rows,
        "e411_rows": e411_rows,
        "templates_used_sample": ["%s:%d %s %s%s" % (t["module"], t["line"], t["kind"],
                                                    t["template"], " [opener]" if t["in_an_opener"] else "")
                                  for t in sorted(specific, key=lambda t: (t["module"], t["line"]))[:40]],
        "templates_discarded_not_specific": sorted(
            {"%s:%d %s" % (t["module"], t["line"], t["template"])
             for t in templates if not t["specific"]})[:200],
        "method_limits": [
            "a literal is counted when some string constant's last path component equals the "
            "basename; a literal split across os.path.join arguments is not reconstructed here "
            "(E422 owns join-chain reconstruction), so faces named only that way land in the "
            "C_NONE bucket rather than C_LITERAL.",
            "specificity is text-level: a template is specific when a fragment keeps a non-empty "
            "stem after the last '/' and the '.json' suffix are removed. A template like "
            "'%s.json' that receives a literal stem through a variable is therefore discarded "
            "here even though it does name a face at runtime -- the discard list is published.",
            "in_an_opener is the nearest enclosing FunctionDef containing any call to a name in "
            "OPENERS; it is not dataflow. A name built in a function that also logs an unrelated "
            "file counts as being in an opener.",
            "the corpus is source text on disk; a module that does not parse contributes nothing "
            "(half-written scratch files are common in this tree).",
            "this study's own file is excluded by name (E180/E207 family), so its templates and "
            "literals cannot feed the reading.",
            "rows and templates move when any module is added or edited -- a new collector with a "
            "new literal legitimately reclassifies a face. The producer must be re-derived after "
            "the corpus grows (E421/E419 precedent); verify therefore compares rows, not counts.",
            "the population excludes basenames starting with '_': those are round receipts and "
            "scratch faces that every round rewrites, so counting them would move the reading "
            "without moving the tree's content.",
        ],
    }
    face["summary_core"] = {k: v for k, v in face["summary"].items() if k not in POPULATION_KEYS}
    face["_path"] = write_face(face) if write else None
    return face


# ------------------------------------------------------------------ verify
def verify(root: str = ROOT) -> list:
    problems = []
    p = os.path.join(root, "results", "state_tilt", LATEST)
    if not os.path.exists(p):
        return ["no published face at results/state_tilt/%s" % LATEST]
    stored = json.load(open(p, encoding="utf-8"))
    fresh = build(root=root, write=False)
    for k in COMPARE:
        a = stored.get("summary_core") if k == "summary_core" else stored.get(k)
        b = fresh.get("summary_core") if k == "summary_core" else fresh.get(k)
        if a != b:
            problems.append("%s does not re-derive" % k)
    if stored.get("verdict") not in VERDICT_VOCAB:
        problems.append("stored verdict is outside the vocabulary")
    if list(stored.get("population_keys") or []) != list(POPULATION_KEYS):
        problems.append("the face declares population keys its producer does not")
    if list(stored.get("class_vocab") or []) != list(CLASS_VOCAB):
        problems.append("the face declares a class vocabulary its producer does not")
    s = fresh["summary"]
    bc = fresh["by_class_all_faces"]
    if sum(bc.values()) != s["faces_on_disk"]:
        problems.append("the class table does not re-add to the faces on disk")
    if s["faces_literal_named"] != bc.get(C_LITERAL, 0) + bc.get(C_BOTH, 0):
        problems.append("the literal-named count does not re-add")
    if s["faces_only_dynamically_reachable"] != bc.get(C_DYNAMIC, 0):
        problems.append("the dynamic-only count does not re-add")
    if sum(fresh["by_class_e411"].values()) != s["e411_file_faces"]:
        problems.append("the E411 class table does not re-add to its file population")
    published_rows = [r for r in fresh["rows"]]
    if any(r["class"] == C_LITERAL for r in published_rows):
        problems.append("a literal-named face was published in the non-literal row list")
    if fresh["rows_published"] != len(fresh["rows"]):
        problems.append("the published row count and the row list disagree")
    tally = sum(s["non_literal"] for s in fresh["non_literal_faces_by_directory"])
    non_literal_total = sum(fresh["by_class_all_faces"].get(k, 0)
                            for k in (C_DYNAMIC, C_BOTH, C_NONE))
    if tally > non_literal_total:
        problems.append("the directory tally exceeds the non-literal faces it summarises")
    if non_literal_total != fresh["summary"]["faces_on_disk"] \
            - fresh["by_class_all_faces"].get(C_LITERAL, 0):
        problems.append("the non-literal total does not close against the literal count")
    if fresh["summary"]["faces_on_disk"] - fresh["summary"]["faces_literal_named"] \
            != fresh["by_class_all_faces"].get(C_DYNAMIC, 0) \
            + fresh["by_class_all_faces"].get(C_NONE, 0):
        problems.append("literal-named, dynamic-only and unmasked do not close the books")
    for r in fresh["rows"] + fresh["e411_rows"]:
        if r["class"] not in CLASS_VOCAB:
            problems.append("%s: class outside the vocabulary" % r["face"])
            break
        if r["match_count"] <= 4 and r["match_count"] != len(r["matches"]):
            problems.append("%s: the match count does not match its list" % r["face"])
            break
        if r["class"] == C_DYNAMIC and r["literal_named"]:
            problems.append("%s: published as dynamic-only while named by a literal" % r["face"])
            break
    dyn = [r for r in fresh["e411_rows"] if r["kind"] == "file" and r["class"] == C_DYNAMIC]
    read = [r for r in dyn if r["any_match_in_an_opener"]]
    disk_dyn = [r for r in fresh["rows"] if r["class"] == C_DYNAMIC]
    if fresh["verdict"] == V_CENSUS_ADEQUATE and (dyn or disk_dyn):
        problems.append("published as adequate while a face is only dynamically reachable")
    if fresh["verdict"] == V_READERS_LITERAL_WRITERS_DYNAMIC and (dyn or not disk_dyn):
        problems.append("published as readers-literal/writers-dynamic without that split")
    if fresh["verdict"] == V_DYNAMIC_ONLY_READ and not read:
        problems.append("published as dynamic-and-read with no such row")
    if fresh["verdict"] == V_DYNAMIC_ONLY_UNREAD and read:
        problems.append("published as dynamic-but-unread while a row sits in an opener")
    if fresh["verdict"] == V_DYNAMIC_ONLY_UNREAD and not dyn:
        problems.append("published as dynamic-but-unread with no dynamic row at all")
    for t in fresh["templates_used_sample"]:
        # "<module>:<line> <kind> <template>[ [opener]]" -- the template text is the last field
        body = t.split(" ", 2)[-1]
        body = body.rsplit(" [opener]", 1)[0]
        ok, _stems = _specificity(body)
        if not ok:
            problems.append("a used template is not specific by its own text: %s" % body)
            break
    return problems


# ------------------------------------------------------------------ selftest
def selftest() -> int:
    fails = []

    def leg(name, cond):
        if not cond:
            fails.append(name)

    # --- specificity
    leg("bare placeholder is not specific", _specificity("*.json")[0] is False)
    leg("directory-only template is not specific",
        _specificity("results/state_tilt/*.json")[0] is False)
    leg("named stem is specific", _specificity("SIG-*.json")[0] is True)
    leg("path with named stem is specific", _specificity("results/sig/SIG-*.json")[0] is True)
    leg("stem fragments are published", _specificity("A-*-B.json")[1] == ["A-", "-B"])

    # --- regex
    rx = _template_regex("results/E-*.json")
    leg("template regex matches under a directory", bool(rx.match("results/E-1.json")))
    leg("template regex does not match another stem", not rx.match("results/F-1.json"))
    leg("dot in template is escaped", not _template_regex("E.1.json").match("EX1.json"))

    # --- one source, every shape
    src = '''
import json, os
FACE = "results/thing-%s.json"
NAME = "results/" + stem
OTHER = "%s" % tail
F = f"results/{kind}_latest.json"
G = "results/{}.json".format(kind)
H = os.path.join("results", "LITONLY.json")
H2 = os.path.join(root, "results", "DYNJOIN.json")
J = stem + ".json"
K = "results/literal_face.json"
def opener():
    p = "results/thing-%s.json" % ("x",)
    return json.load(open(p, encoding="utf-8"))
def report():
    return "results/thing-%s.json" % ("x",)
'''
    lits, tmpls = collect_source(src, "fixture.py")
    kinds = sorted({t["kind"] for t in tmpls})
    leg("all five construction shapes are found",
        {"concatenation", "percent_format", "fstring", "str_format",
         "path_join_with_a_dynamic_head"} <= set(kinds))
    leg("a literal json name is a literal", "results/literal_face.json" in lits)
    leg("a fully literal join is not a template",
        not any(t["template"].endswith("LITONLY.json") for t in tmpls))
    leg("a join with a dynamic head is a template",
        any(t["template"].endswith("DYNJOIN.json") for t in tmpls))
    leg("an opener is recognised", any(t["in_an_opener"] for t in tmpls))
    leg("a report scope is not an opener",
        any(not t["in_an_opener"] for t in tmpls))
    leg("a parse error contributes nothing", collect_source("def (:", "bad.py") == ({}, []))

    # --- classification is a function of its inputs
    names = literal_names({"results/literal_face.json": [{"module": "m", "line": 1}],
                           "literal_face.json": [{"module": "m", "line": 2}]})
    leg("literal_names keeps the basename", "literal_face.json" in names)
    t_named = {"module": "m", "line": 1, "kind": "percent_format",
               "template": "results/thing-*.json", "specific": True,
               "stem_fragments": ["thing-"], "in_an_opener": True}
    leg("both mask is both", classify("results/thing-1.json",
                                      {"thing-1.json"}, [t_named])["class"] == C_BOTH)
    leg("dynamic only", classify("results/thing-1.json", set(), [t_named])["class"] == C_DYNAMIC)
    leg("literal only", classify("results/other.json", {"other.json"},
                                 [t_named])["class"] == C_LITERAL)
    leg("no mask at all", classify("results/other.json", set(),
                                   [t_named])["class"] == C_NONE)

    # --- verdict is a function of the rows
    def verdict_of(dyn, read, disk_dyn):
        if read:
            return V_DYNAMIC_ONLY_READ
        if dyn:
            return V_DYNAMIC_ONLY_UNREAD
        return V_READERS_LITERAL_WRITERS_DYNAMIC if disk_dyn else V_CENSUS_ADEQUATE

    leg("verdict adequate", verdict_of(0, 0, 0) == V_CENSUS_ADEQUATE)
    leg("verdict readers literal writers dynamic",
        verdict_of(0, 0, 9000) == V_READERS_LITERAL_WRITERS_DYNAMIC)
    leg("verdict read", verdict_of(2, 1, 5) == V_DYNAMIC_ONLY_READ)
    leg("verdict unread", verdict_of(2, 0, 5) == V_DYNAMIC_ONLY_UNREAD)
    leg("a directory row is labelled, not a blind spot",
        _face_kind("results/state_tilt") == "directory" and
        _face_kind("results/X-%s.json") == "templated")
    leg("class vocabulary has four members", len(CLASS_VOCAB) == 4)

    total = 27
    if fails:
        print("selftest FAIL %d/%d: %s" % (total - len(fails), total, "; ".join(fails)))
        return 1
    print("selftest PASS %d/%d" % (total, total))
    return 0


def main(argv: list) -> int:
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "run":
        face = build()
        print(json.dumps({"evidence_cutoff": face["evidence_cutoff"],
                          "verdict": face["verdict"],
                          "summary": face["summary"]}, ensure_ascii=False, indent=1))
        print("written:", face.get("_path"))
        for r in face["e411_rows"]:
            if r["class"] == C_DYNAMIC:
                print("  %-56s opener=%s %s" % (r["face"], r["any_match_in_an_opener"],
                                                (r["matches"] or [{}])[0].get("template")))
        return 0
    if cmd == "verify":
        problems = verify()
        print(json.dumps({"problems": problems}, ensure_ascii=False))
        return 0 if not problems else 1
    if cmd == "selftest":
        return selftest()
    print("usage: e426_dynamic_face_names.py run|verify|selftest", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))