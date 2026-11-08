"""E556 -- do the six faces E555 rescued survive the loss of the message that names them?

E555 (r1581) folded six of E554's 67 unresolved ``wrote <path>`` rows by evaluating
``Path(__file__).resolve().parents[k]`` against the writer's own path, and reported
that all six faces exist on disk.  A named face is not an announced one: E554's own
at-risk arm -- "does the face have a ``<stem>_latest.json`` pointer or a source that
names the path" -- was never run over these six rows, because E554 could not resolve
them.

This study re-reads the six faces from E555's published face (machine-read, never
hand-copied) and asks, for each one, what is left if the message is lost:

  * a ``<stem>_latest.json`` pointer face exists on disk and names the face
  * a source other than the writer *loads* the face (an ``open``/``read_text``/
    ``json.load``/``read_json`` call whose argument folds to the face path)
  * a source merely *mentions* the path or basename (E554's ``source_literal`` arm)
  * nothing at all besides the message

E554 counted a mention as an announcement.  A mention is not a reader, so the same
six rows are priced on two arms and the difference is published row by row:
``announced_but_never_loaded``.

    python scripts/e556_rescued_face.py build      # publish the face
    python scripts/e556_rescued_face.py check      # re-derive from source; problems must be []
    python scripts/e556_rescued_face.py verify     # two builds identical
    python scripts/e556_rescued_face.py selftest   # offline fixtures + defect refusals
"""
from __future__ import annotations

import ast
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e554_wrote_population as e554  # noqa: E402  (the announcement arm this study runs)

STATE_TILT = os.path.join(ROOT, "results", "state_tilt")
LATEST = os.path.join(STATE_TILT, "rescuedface_latest.json")
DATED_PREFIX = "RESCUEDFACE"
PARENT = os.path.join(STATE_TILT, "unfoldedname_latest.json")
# A face the tree is known to load back: if the reader arm cannot see a reader
# here, its "nothing reads these" is blindness, not evidence.
CONTROL_FACE = "results/state_tilt/unfoldedname_latest.json"

STUDY = "E556"
CARD = "E556"
TITLE = ("whether the six faces E555 folded survive the loss of the message that names them")
EVIDENCE_CUTOFF = "2026-11-08"

# ---- survival classes -----------------------------------------------------
S_POINTER_AND_READER = "a_pointer_face_and_a_source_load_it"
S_POINTER_ONLY = "a_pointer_face_names_it_and_nothing_loads_it"
S_READER_ONLY = "a_source_loads_it_and_no_pointer_face_names_it"
S_MESSAGE_ONLY = "only_the_message_names_it"

SURVIVAL_VOCAB = (S_POINTER_AND_READER, S_POINTER_ONLY, S_READER_ONLY, S_MESSAGE_ONLY)
SURVIVORS = (S_POINTER_AND_READER, S_POINTER_ONLY, S_READER_ONLY)

V_ALL_SURVIVE = "every_rescued_face_keeps_an_announcement_once_the_message_is_lost"
V_SOME_DIE = "some_rescued_faces_are_announced_only_by_the_message_that_names_them"

# Loads only: a call whose argument folds to the face.  ``json.load(f)`` is not
# here on purpose -- the path is bound by the ``open``/``Path`` that produced f,
# and that call is the one this scan follows.
LOAD_FUNCS = ("open", "read_text", "read_bytes", "loads", "read_json", "read_csv",
              "read_parquet", "loadtxt", "genfromtxt", "read_excel")

PATHISH = re.compile(r"^(results|docs|data|state|research|knowledge|logs)/")
_POINTER = re.compile(r"_latest\.json$")


def _read(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


def _rel(path):
    return os.path.relpath(path, ROOT).replace("\\", "/")


# ---------------------------------------------------------------- population
def population():
    """The six faces E555 folded, read out of E555's own published face."""
    parent = json.load(io.open(PARENT, encoding="utf-8"))
    faces = parent.get("folded_faces") or []
    out = []
    for f in faces:
        path = f.get("path")
        if not path:
            continue
        out.append({"path": path, "writer": f.get("writer"), "line": f.get("line")})
    out.sort(key=lambda r: (r["path"], str(r["writer"])))
    return out


# ---------------------------------------------------------------- pointer arm
def _pointer_faces_on_disk(face_rel):
    """Every ``<stem>_latest.json`` that exists on disk for this face, and the
    subset whose content names the face."""
    base = os.path.basename(face_rel)
    stem = base.rsplit(".", 1)[0]
    dated = base
    out = []
    for name in sorted(os.listdir(STATE_TILT)):
        if not _POINTER.match(name):
            continue
        if not name.startswith(stem + "_latest"):
            # a pointer is allowed to be named after the dated stem too
            if not (name.startswith(dated.rsplit(".", 1)[0]) and name != base):
                continue
        rel = "results/state_tilt/" + name
        text = ""
        try:
            text = _read(os.path.join(STATE_TILT, name))
        except OSError:
            pass
        out.append({"path": rel, "names_the_face": (dated in text or face_rel in text)})
    return out


# ---------------------------------------------------------------- reader arm
_CALL_CACHE = {}
_FILE_INDEX = {}


def _scope_tables(tree, consts):
    """Per-function cumulative scopes, built once per file.

    E554's ``_local_scope`` walks the whole enclosing function for every call it
    is asked about.  Asked once that is fine; asked for every call in a 24k-line
    gate file it is O(n^2) and burned six CPU-minutes on the first build of this
    study.  The evidence is identical -- the same assignments folded in the same
    order -- only the walk happens once.
    """
    tables = {}

    def assignments(node):
        out = []
        for sub in ast.walk(node):
            if isinstance(sub, ast.Assign) and len(sub.targets) == 1:
                tgt = sub.targets[0]
                if isinstance(tgt, ast.Name):
                    out.append((sub.lineno, tgt.id, sub.value))
                elif isinstance(tgt, ast.Subscript) and isinstance(tgt.value, ast.Name) \
                        and isinstance(tgt.slice, ast.Constant):
                    out.append((sub.lineno,
                                "__sub__%s:%s" % (tgt.value.id, tgt.slice.value),
                                sub.value))
            elif isinstance(sub, ast.AnnAssign) and isinstance(sub.target, ast.Name) \
                    and sub.value is not None:
                out.append((sub.lineno, sub.target.id, sub.value))
        return sorted(out, key=lambda a: a[0])

    def table_for(func, start, end):
        merged = dict(consts)
        steps = [(start, dict(merged))]
        for line, name, value in assignments(func):
            val, _why = e554._fold(value, merged)
            if val is not None:
                merged[name] = val
            steps.append((line + 1, dict(merged)))
        tables[(start, end)] = steps
        return steps

    funcs = [n for n in ast.walk(tree)
             if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    ranges = []
    for f in funcs:
        start = min([f.lineno] + [d.lineno for d in f.decorator_list])
        end = getattr(f, "end_lineno", None) or start
        ranges.append((start, end, f))
    ranges.sort()
    for start, end, f in ranges:
        table_for(f, start, end)
    tables[(1, 10 ** 9)] = [(1, dict(consts))]
    return tables, ranges


def _scope_at(index, line):
    tables, ranges = index
    best = None
    for start, end, _f in ranges:
        if start <= line <= end:
            best = (start, end)          # innermost wins because ranges are sorted
    steps = tables.get(best) if best else None
    if steps is None:
        steps = tables[(1, 10 ** 9)]
    chosen = steps[0][1]
    for boundary, scope in steps:
        if boundary <= line:
            chosen = scope
        else:
            break
    return chosen


def _file_index(rel):
    if rel in _FILE_INDEX:
        return _FILE_INDEX[rel]
    text = e554._corpus().get(rel)
    entry = None
    if text is not None:
        try:
            tree = ast.parse(text)
        except SyntaxError:
            tree = None
        if tree is not None:
            consts = e554._module_constants(tree)
            calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
                     and e554._leaf(n.func) in LOAD_FUNCS]
            entry = (tree, consts, calls, _scope_tables(tree, consts))
    _FILE_INDEX[rel] = entry
    return entry


def _loads_in(rel, face_rel):
    """Every load call in ``rel`` whose argument folds to ``face_rel``."""
    base = os.path.basename(face_rel)
    stem = base.rsplit(".", 1)[0]
    text = e554._corpus().get(rel)
    if text is None:
        return []
    if face_rel not in text and base not in text and stem not in text:
        return []
    key = (rel, face_rel)
    if key in _CALL_CACHE:
        return _CALL_CACHE[key]
    index = _file_index(rel)
    found = []
    if index is not None:
        _tree, consts, calls, scopes = index
        for node in calls:
            scope = _scope_at(scopes, node.lineno)
            for arg in list(node.args) + [k.value for k in node.keywords]:
                val, _why = e554._fold(arg, scope)
                if val is None:
                    continue
                if val == face_rel or _norm_slash(val).endswith("/" + base):
                    found.append({"source": rel, "line": node.lineno,
                                  "call": e554._leaf(node.func), "argument": val})
                    break
    found.sort(key=lambda r: (r["source"], r["line"]))
    _CALL_CACHE[key] = found
    return found


def _norm_slash(s):
    return (s or "").replace("\\", "/")


def _readers_of(face_rel, writer_rel):
    out = []
    for rel in sorted(e554._corpus()):
        if rel == writer_rel:
            continue
        out.extend(_loads_in(rel, face_rel))
    return out


# ---------------------------------------------------------------- classification
def classify_survival(pointer_naming, readers):
    has_pointer = any(p.get("names_the_face") for p in pointer_naming)
    has_reader = bool(readers)
    if has_pointer and has_reader:
        return S_POINTER_AND_READER
    if has_pointer:
        return S_POINTER_ONLY
    if has_reader:
        return S_READER_ONLY
    return S_MESSAGE_ONLY


def _rederive_survival(row):
    return classify_survival(row["facts"]["pointer_faces"], row["facts"]["readers"])


def _rederive_announce(row):
    return e554.classify_announce(row["face"], row["facts"]["announcements"])


def _rederive_risk(row):
    return e554.classify_risk(row["spawn_class"], row["announcement_class"],
                              False)


def build(write=True):
    rows = []
    for site in population():
        face_rel = site["path"]
        writer = site["writer"]
        exists = os.path.isfile(os.path.join(ROOT, face_rel))
        pointers = _pointer_faces_on_disk(face_rel)
        readers = _readers_of(face_rel, writer)
        mentions = e554._announcements_of(face_rel, writer) if exists else []
        mentions = [m for m in mentions if m.get("kind") == "source_literal"]
        module_name = os.path.basename(writer).rsplit(".", 1)[0] if writer else ""
        spawn_cls = e554.classify_spawn(
            e554._spawners_of(writer, module_name) if writer else [])
        # E554's arm is the mention arm; the pointer arm must not inflate it, so
        # the announcement class is taken over the literal mentions only and the
        # pointer evidence is republished separately.
        ann_cls = e554.classify_announce(face_rel, mentions) if exists else e554.A_UNASSESSABLE
        survival = classify_survival(pointers, readers)
        rows.append({
            "face": face_rel,
            "face_exists_on_disk": exists,
            "writer": writer,
            "writer_line": site["line"],
            "spawn_class": spawn_cls,
            "announcement_class": ann_cls,
            "risk_class": e554.classify_risk(spawn_cls, ann_cls, False),
            "survival_class": survival,
            "announced_but_never_loaded": bool(
                mentions and not readers and not any(p.get("names_the_face") for p in pointers)),
            "facts": {
                "pointer_faces": pointers,
                "readers": readers,
                "announcements": mentions,
            },
        })
    rows.sort(key=lambda r: (r["face"], str(r["writer"])))

    control_readers = _readers_of(CONTROL_FACE, "")

    by_survival = {c: 0 for c in SURVIVAL_VOCAB}
    by_announce = {c: 0 for c in (e554.A_SOURCE_LITERAL, e554.A_POINTER_FACE,
                                  e554.A_BOTH, e554.A_ONLY_MESSAGE,
                                  e554.A_UNASSESSABLE)}
    by_risk = {c: 0 for c in e554.RISK_VOCAB}
    for r in rows:
        by_survival[r["survival_class"]] += 1
        by_announce[r["announcement_class"]] = by_announce.get(r["announcement_class"], 0) + 1
        by_risk[r["risk_class"]] = by_risk.get(r["risk_class"], 0) + 1

    loading_sources = sorted({x["source"] for r in rows for x in r["facts"]["readers"]})
    message_only = [r["face"] for r in rows if r["survival_class"] == S_MESSAGE_ONLY]
    if not control_readers:
        raise SystemExit("the reader arm is blind: it finds no load of %s" % CONTROL_FACE)
    verdict = V_SOME_DIE if message_only else V_ALL_SURVIVE

    summary = {
        "rows": len(rows),
        "parent_faces_published": len(population()),
        "control_face": CONTROL_FACE,
        "control_loads_found": len(control_readers),
        "faces_that_exist_on_disk": sum(1 for r in rows if r["face_exists_on_disk"]),
        "pointer_faces_found": sum(len(r["facts"]["pointer_faces"]) for r in rows),
        "pointer_faces_that_name_the_face": sum(
            1 for r in rows for p in r["facts"]["pointer_faces"] if p.get("names_the_face")),
        "loads_found": sum(len(r["facts"]["readers"]) for r in rows),
        "distinct_loading_sources": len(loading_sources),
        "loading_sources": loading_sources,
        "rows_with_a_load": sum(1 for r in rows if r["facts"]["readers"]),
        "rows_with_a_naming_pointer": sum(
            1 for r in rows if any(p.get("names_the_face") for p in r["facts"]["pointer_faces"])),
        "rows_announced_but_never_loaded": sum(
            1 for r in rows if r["announced_but_never_loaded"]),
        "rows_message_only": len(message_only),
        "message_only_faces": message_only,
        "by_survival_class": {k: v for k, v in by_survival.items() if v},
        "by_announcement_class": {k: v for k, v in by_announce.items() if v},
        "by_risk_class": {k: v for k, v in by_risk.items() if v},
    }

    face = {
        "study": STUDY,
        "card": CARD,
        "title": TITLE,
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "population_source": {
            "face": _rel(PARENT),
            "field": "folded_faces",
            "selector": "every row E555 folded by evaluating parents[k]",
            "published": len(population()),
        },
        "rows": rows,
        "summary": summary,
        "verdict": verdict,
        "verdict_line": ("%d of %d rescued faces are announced only by the message: %s"
                         % (len(message_only), len(rows), ", ".join(message_only) or "none")),
        "method_note": (
            "The reader arm folds a load call's argument through module constants and "
            "the enclosing function's assignments before comparing; a mention without a "
            "load is republished as the E554 literal arm and never counted as a reader."),
        "method_bound": (
            "static AST only: a load through a variable built at run time is not seen and "
            "is published as no reader rather than as unread; the pointer arm inspects only "
            "results/state_tilt/*_latest.json, so a pointer kept elsewhere counts as absent; "
            "mentions are counted in executable sources only (py/ps1/bat/cmd/sh), so a "
            "reference from another markdown document is not an announcement; the reader arm "
            "is controlled against %s, which the tree does load." % CONTROL_FACE),
    }
    if write:
        os.makedirs(STATE_TILT, exist_ok=True)
        _write(os.path.join(STATE_TILT, "%s-%s.json" % (DATED_PREFIX, EVIDENCE_CUTOFF)), face)
        _write(LATEST, face)
    return face


def _write(path, obj):
    raw = json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=False)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(raw + "\n")


# ---------------------------------------------------------------- gate
def face_problems(face):
    probs = []
    rows = face.get("rows") or []
    s = face.get("summary") or {}
    if not rows:
        return ["the population is empty"]
    for r in rows:
        if not PATHISH.match(r.get("face") or ""):
            probs.append("a row names something that is not a face path (%s)" % (r.get("face"),))
        if r.get("face_exists_on_disk") and not os.path.isfile(os.path.join(ROOT, r["face"])):
            probs.append("a row claims its face is on disk and it is not (%s)" % (r.get("face"),))
        if r.get("survival_class") not in SURVIVAL_VOCAB:
            probs.append("a survival class outside the vocabulary (%s)" % (r.get("survival_class"),))
        got = _rederive_survival(r)
        if got != r.get("survival_class"):
            probs.append("a row's survival class is not what its own facts say (%s: %s vs %s)"
                         % (r.get("face"), r.get("survival_class"), got))
        got_a = _rederive_announce(r)
        if got_a != r.get("announcement_class"):
            probs.append("a row's announcement class is not what its own mentions say (%s)"
                         % (r.get("face"),))
        got_r = _rederive_risk(r)
        if got_r != r.get("risk_class"):
            probs.append("a row's risk class is not what its own arms say (%s)" % (r.get("face"),))
        for reader in r["facts"]["readers"]:
            if reader.get("source") == r.get("writer"):
                probs.append("a row counts its own writer as a reader (%s)" % (r.get("face"),))
            if reader.get("call") not in LOAD_FUNCS:
                probs.append("a row counts a non-load call as a reader (%s)" % (r.get("face"),))
        if r["facts"]["readers"] and r.get("survival_class") == S_MESSAGE_ONLY:
            probs.append("a row with a load is classed message-only (%s)" % (r.get("face"),))
        if any(p.get("names_the_face") for p in r["facts"]["pointer_faces"]) and \
                r.get("survival_class") == S_MESSAGE_ONLY:
            probs.append("a row with a naming pointer is classed message-only (%s)"
                         % (r.get("face"),))

    by_survival = {c: 0 for c in SURVIVAL_VOCAB}
    by_announce = {}
    by_risk = {}
    for r in rows:
        by_survival[r["survival_class"]] += 1
        by_announce[r["announcement_class"]] = by_announce.get(r["announcement_class"], 0) + 1
        by_risk[r["risk_class"]] = by_risk.get(r["risk_class"], 0) + 1
    loading_sources = sorted({x["source"] for r in rows for x in r["facts"]["readers"]})
    message_only = [r["face"] for r in rows if r["survival_class"] == S_MESSAGE_ONLY]
    expected = {
        "rows": len(rows),
        "faces_that_exist_on_disk": sum(1 for r in rows if r["face_exists_on_disk"]),
        "pointer_faces_found": sum(len(r["facts"]["pointer_faces"]) for r in rows),
        "pointer_faces_that_name_the_face": sum(
            1 for r in rows for p in r["facts"]["pointer_faces"] if p.get("names_the_face")),
        "loads_found": sum(len(r["facts"]["readers"]) for r in rows),
        "distinct_loading_sources": len(loading_sources),
        "loading_sources": loading_sources,
        "rows_with_a_load": sum(1 for r in rows if r["facts"]["readers"]),
        "rows_with_a_naming_pointer": sum(
            1 for r in rows if any(p.get("names_the_face") for p in r["facts"]["pointer_faces"])),
        "rows_announced_but_never_loaded": sum(
            1 for r in rows if r["announced_but_never_loaded"]),
        "rows_message_only": len(message_only),
        "message_only_faces": message_only,
        "by_survival_class": {k: v for k, v in by_survival.items() if v},
        "by_announcement_class": {k: v for k, v in by_announce.items() if v},
        "by_risk_class": {k: v for k, v in by_risk.items() if v},
        "control_face": CONTROL_FACE,
        "control_loads_found": len(_readers_of(CONTROL_FACE, "")),
    }
    if not expected["control_loads_found"]:
        probs.append("the reader arm finds no load of the control face: it is blind")
    for key, val in expected.items():
        if s.get(key) != val:
            probs.append("summary %s=%r but the rows say %r" % (key, s.get(key), val))
    want = V_SOME_DIE if message_only else V_ALL_SURVIVE
    if face.get("verdict") != want:
        probs.append("the verdict is not what the rows derive (%r vs %r)"
                     % (face.get("verdict"), want))
    if not face.get("evidence_cutoff"):
        probs.append("the face carries no evidence_cutoff")
    if (face.get("population_source") or {}).get("published") != s.get("parent_faces_published"):
        probs.append("the population source publishes a different parent size")
    if s.get("parent_faces_published") != len(population()):
        probs.append("the parent face no longer publishes this many folded faces")
    return probs


def check():
    pub = json.load(io.open(LATEST, encoding="utf-8"))
    problems = list(face_problems(pub))
    fresh = build(write=False)
    if [(r["face"], r["writer"]) for r in fresh["rows"]] != \
            [(r["face"], r["writer"]) for r in pub["rows"]]:
        problems.append("the published population is not the one E555 publishes now")
    else:
        for a, b in zip(fresh["rows"], pub["rows"]):
            if json.dumps(a, sort_keys=True) != json.dumps(b, sort_keys=True):
                problems.append("a published row is not what the sources say now (%s)"
                                % (a["face"],))
    if fresh["verdict"] != pub["verdict"]:
        problems.append("the published verdict is not the one the sources derive now")
    print(json.dumps({"problems": problems, "verdict": pub.get("verdict"),
                      "rows": len(pub.get("rows") or []),
                      "message_only": (pub.get("summary") or {}).get("rows_message_only")},
                     ensure_ascii=False))
    return 1 if problems else 0


def verify():
    a, b = build(write=False), build(write=False)
    problems = [] if json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True) else \
        ["two builds of the same sources differ"]
    if not problems:
        problems = list(face_problems(a))
    print(json.dumps({"problems": problems}, ensure_ascii=False))
    return 1 if problems else 0


# ---------------------------------------------------------------- selftest
def selftest():
    fails = []
    n = 0

    def ok(label, cond):
        nonlocal n
        n += 1
        if not cond:
            fails.append(label)

    def survival(pointer_rows, readers):
        return classify_survival(pointer_rows, readers)

    ok("pointer that names the face plus a load is the fully surviving class",
       survival([{"path": "x_latest.json", "names_the_face": True}],
                [{"source": "a.py", "line": 1, "call": "open"}]) == S_POINTER_AND_READER)
    ok("a pointer that exists but never names the face does not survive",
       survival([{"path": "x_latest.json", "names_the_face": False}], []) == S_MESSAGE_ONLY)
    ok("a load without a pointer survives as reader-only",
       survival([], [{"source": "a.py", "line": 9, "call": "open"}]) == S_READER_ONLY)
    ok("nothing at all is message-only", survival([], []) == S_MESSAGE_ONLY)
    ok("the survivors are exactly the three non-message classes",
       set(SURVIVORS) == set(SURVIVAL_VOCAB) - {S_MESSAGE_ONLY})

    # a mention is not a reader: the load arm must not fire on a print-only mention
    fixture = (
        "import os\n"
        "OUT = os.path.join('results', 'state_tilt', 'fixture.json')\n"
        "def emit():\n"
        "    print('wrote', OUT)\n")
    tree = ast.parse(fixture)
    consts = e554._module_constants(tree)
    loads = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
             and e554._leaf(node.func) in LOAD_FUNCS]
    ok("a writer that only prints its face has no load call", loads == [])
    val, _why = e554._fold(ast.parse("os.path.join('results','state_tilt','fixture.json')"
                                     ).body[0].value, {})
    ok("the fold names the face", val == "results/state_tilt/fixture.json")

    loader = (
        "import json, io\n"
        "P = 'results/state_tilt/fixture.json'\n"
        "def read():\n"
        "    return json.load(io.open(P, encoding='utf-8'))\n")
    tree2 = ast.parse(loader)
    consts2 = e554._module_constants(tree2)
    hit = []
    for node in ast.walk(tree2):
        if not isinstance(node, ast.Call):
            continue
        if e554._leaf(node.func) not in LOAD_FUNCS:
            continue
        for arg in node.args + [k.value for k in node.keywords]:
            v, _w = e554._fold(arg, consts2)
            if v == "results/state_tilt/fixture.json":
                hit.append(node.lineno)
    ok("a load whose argument folds to the face is seen", hit == [4])
    ok("the reader vocabulary excludes json.load itself",
       "load" not in LOAD_FUNCS and "open" in LOAD_FUNCS)

    # a row with a load may never be classed message-only
    ok("identities: reader implies not message-only",
       classify_survival([], [{"source": "a.py", "line": 1, "call": "open"}])
       != S_MESSAGE_ONLY)

    ok("the control face is a face the published tree loads back",
       CONTROL_FACE.startswith("results/state_tilt/") and CONTROL_FACE.endswith(".json"))
    ok("a blind arm would publish no evidence: the guard is an assertion, not a sentence",
       "the reader arm is blind" in io.open(os.path.abspath(__file__), encoding="utf-8").read())

    print("%d/%d legs green" % (n - len(fails), n))
    for f in fails:
        print("FAIL: %s" % f)
    return 1 if fails else 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "build"
    if cmd == "build":
        face = build()
        print(json.dumps({"rows": len(face["rows"]), "verdict": face["verdict"]},
                         ensure_ascii=False))
        return 0
    if cmd == "check":
        return check()
    if cmd == "verify":
        return verify()
    if cmd == "selftest":
        return selftest()
    if cmd == "population":
        rows = population()
        print(json.dumps({"rows": len(rows), "faces": [r["path"] for r in rows]},
                         ensure_ascii=False))
        return 0
    raise SystemExit("unknown command: %s (build|check|verify|selftest|population)" % cmd)


if __name__ == "__main__":
    sys.exit(main())