"""E391 -- which published key name carries two different structures in two published faces.

E383 measured keys that merge *files* (one key, many faces behind it) and E238/E239 measured
which participant a share belongs to.  Neither answers the cheaper question a reader actually
hits: the *same name* stored as a number in one face and as a mapping in another.  A consumer
that does ``doc["cap"] + 0`` works on nine faces and raises ``TypeError`` on the tenth, and no
schema file records the switch.

What this census measures, statically and deterministically:

  * every key name in every published JSON face under ``results/`` (quarantine excluded, files
    above ``MAX_BYTES`` published as skipped, never silently dropped),
  * the *shape* of the value stored under it -- ``null`` / ``bool`` / ``int`` / ``float`` /
    ``str`` (with a timestamp and a path sub-kind) / ``list[<first non-null element shape>]`` /
    ``dict``,
  * a coarse structural class (``num`` / ``str`` / ``bool`` / ``list`` / ``dict``) and, per
    key, whether one face stores a structure another face stores differently.

Refusals that keep the count from inflating (each is a fixture):

  * ``null`` beside a value is *absence*, not a second meaning -- published as its own class,
    not folded into the conflict count (a missing field and a dict are different questions);
  * ``int`` beside ``float`` is a numeric width, not a different structure (JSON has one number
    type; Python callers rarely care);
  * a list of two element shapes is a conflict only when both lists are non-empty -- an empty
    list is a container waiting for data, not a second meaning;
  * the census does not count itself: its own face, its latest mirror and its own source are
    excluded from both populations (E180/E207 family);
  * a reader is a *statically resolvable* literal subscript or ``.get``-family call; a key
    passed as a variable is not credited (E390's lesson);
  * a row-map key is an *index*, not a name -- ``{"0": 5}`` in one face and ``{"0": {...}}`` in
    another is one digit meaning a different row in each table, so field-shaped keys and
    index-shaped keys are counted apart and only the field-shaped ones can carry a verdict.
    Measured on this corpus: 3,910 of 7,797 structural conflicts are index keys;
  * ``reader_sites`` is a *name-matched* count over the whole repo.  It says a site writes the
    same literal; it never says the site opens the face that stores it (E390 charged 45 reads to
    faces they never open).  It is published as an upper bound, and the field is named
    ``read_bound_is_name_matched_not_face_resolved`` so a reader cannot mistake it for a sighting.

Verdict is recomputed from the summary: a structural conflict that no in-repo site reads is a
latent hazard, not an active one, and the two are published separately.

    python scripts/e391_key_name_two_meanings.py run
    python scripts/e391_key_name_two_meanings.py verify
    python scripts/e391_key_name_two_meanings.py selftest
"""
import ast
import glob
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
STUDY = "E391_key_name_two_meanings"
TODAY = "2026-11-03"
FACE = "TWOMEANINGS-%s.json" % TODAY
LATEST = "twomeanings_latest.json"
SELF = os.path.abspath(__file__)

SKIP_DIRS = {".git", "__pycache__", "_quarantine", "node_modules", ".codely-cli", "_smoke"}
MAX_BYTES = 1024 * 1024
MAX_NODES_PER_FACE = 20000
MAX_DEPTH = 8
OWN_FACES = {FACE, LATEST}

TS_RX = re.compile(r"^\d{4}-\d{2}-\d{2}([T ][0-9:.\-+ ]+)?$")
PATH_RX = re.compile(r"\.(json|jsonl|py|md|csv|parquet|txt|html|out|err)$")
# A key that names a field starts with a letter or underscore; a key that indexes a row map is a
# number, a code, a date or a sign -- and the same index digit means a different row in every
# table.  Measured on this corpus: 3,910 of 7,797 structural conflicts are index keys, so the
# split is published rather than assumed away.
KEY_IDENT_RX = re.compile(r"^[A-Za-z_][A-Za-z0-9_.\-]*$")

V_EMPTY = "no_published_key_name_appears_in_two_faces"
V_NONE = "no_published_field_shaped_key_name_carries_two_structural_meanings"
V_LATENT = ("identifier_shaped_conflicts_exist_and_no_in_repo_site_reads_any_of_them_by_literal")
V_READ = ("at_least_one_identifier_shaped_key_name_carries_two_structural_meanings_and_in_repo_sites_"
          "read_that_literal_but_this_census_does_not_show_those_sites_open_the_face_that_carries_it")
VOCAB = frozenset({V_EMPTY, V_NONE, V_LATENT, V_READ})


def key_kind(key):
    """``name`` for a field-shaped key, ``index`` for a row-map key (numbers, codes, dates)."""
    return "name" if KEY_IDENT_RX.match(key) else "index"

CLASSES = ("structural_conflict", "list_element_conflict", "null_or_value",
           "numeric_width", "string_kind_conflict", "single")
STRUCTURAL_CATS = ("num", "str", "bool", "list", "dict")


# ------------------------------------------------------------------ shapes
def shape(v):
    """Shape of one stored value, with the two sub-kinds that change what a reader can do."""
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "bool"
    if isinstance(v, int):
        return "int"
    if isinstance(v, float):
        return "float"
    if isinstance(v, str):
        if TS_RX.match(v):
            return "str:timestamp"
        if PATH_RX.search(v):
            return "str:path"
        return "str"
    if isinstance(v, list):
        if not v:
            return "list[]"
        elems = {shape(x) for x in v}
        return "list[%s]" % (elems.pop() if len(elems) == 1 else "mixed")
    if isinstance(v, dict):
        return "dict"
    return "other"


def coarse(s):
    if s in ("int", "float"):
        return "num"
    if s.startswith("str"):
        return "str"
    if s.startswith("list"):
        return "list"
    return s


def classify(shapes):
    """Class of one key given its multiset of shapes (null included)."""
    nonnull = {s for s in shapes if s != "null"}
    cats = {coarse(s) for s in nonnull}
    if len(cats) >= 2:
        return "structural_conflict"
    if nonnull and "null" in shapes:
        return "null_or_value"
    lists = {s for s in nonnull if s.startswith("list[") and s != "list[]"}
    if len(lists) >= 2:
        return "list_element_conflict"
    if {"int", "float"} <= nonnull:
        return "numeric_width"
    kinds = {s for s in nonnull if s.startswith("str")}
    if len(kinds) >= 2:
        return "string_kind_conflict"
    return "single"


def decide(summary):
    """Verdict from the summary alone, so a reader and the smoke leg re-derive the same string."""
    if not summary.get("keys"):
        return V_EMPTY
    if not summary.get("structural_conflicts_name_keys"):
        return V_NONE
    if not summary.get("structural_conflicts_read"):
        return V_LATENT
    return V_READ


def walk_keys(obj, out, file_rel, depth=0):
    """Depth-first: record every dict key with the shape of its value (nested included).

    Iterative with a hard container budget: a 3 MB judge face nests lists of rows of dicts,
    and a depth-first recursion over it visits hundreds of millions of nodes (measured: the
    first draft of this census never finished one round).  A face that hits the budget is
    counted as truncated and published, never silently dropped.
    """
    stack = [(obj, depth)]
    visited = 0
    while stack:
        node, d = stack.pop()
        visited += 1
        if visited > MAX_NODES_PER_FACE:
            return False
        if d > MAX_DEPTH:
            continue
        if isinstance(node, dict):
            for k, v in node.items():
                if isinstance(k, str):
                    out.setdefault(k, []).append({"file": file_rel, "shape": shape(v)})
                if isinstance(v, (dict, list)):
                    stack.append((v, d + 1))
        elif isinstance(node, list):
            for v in node:
                if isinstance(v, (dict, list)):
                    stack.append((v, d + 1))
    return True


# ------------------------------------------------------------- populations
def json_corpus(root=ROOT):
    faces, skipped = [], {"quarantine": 0, "too_large": 0, "own": 0}
    for p in glob.glob(os.path.join(root, "results", "**", "*.json"), recursive=True):
        rel = os.path.relpath(p, root).replace("\\", "/")
        if rel.split("/")[1] in SKIP_DIRS or _under_skip(rel):
            skipped["quarantine"] += 1
            continue
        if os.path.basename(p) in OWN_FACES:
            skipped["own"] += 1
            continue
        if os.path.getsize(p) > MAX_BYTES:
            skipped["too_large"] += 1
            continue
        faces.append((p, rel))
    return sorted(faces, key=lambda x: x[1]), skipped


def _under_skip(rel):
    parts = rel.split("/")
    return any(p in SKIP_DIRS for p in parts[:-1])


def py_corpus(root=ROOT):
    out = []
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in files:
            if fn.endswith(".py"):
                p = os.path.join(base, fn)
                if os.path.abspath(p) == SELF:
                    continue
                out.append(p)
    return sorted(out)


def _literal(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def reader_keys(src):
    """{key: n_sites} for literal subscripts and .get-family calls in one source."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return {}
    found = {}
    for node in ast.walk(tree):
        key = None
        if isinstance(node, ast.Subscript):
            key = _literal(node.slice)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr in ("get", "pop", "setdefault") and node.args:
            key = _literal(node.args[0])
        if key is not None:
            found[key] = found.get(key, 0) + 1
    return found


def scan_readers(root=ROOT):
    keys, files = {}, 0
    for p in py_corpus(root):
        try:
            src = io.open(p, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        if '["' not in src and "['" not in src and ".get(" not in src:
            continue
        files += 1
        for k, n in reader_keys(src).items():
            keys[k] = keys.get(k, 0) + n
    return keys, files


def build(root=ROOT):
    faces, skipped = json_corpus(root)
    table = {}
    parse_errors = []
    truncated = []
    for path, rel in faces:
        try:
            with io.open(path, encoding="utf-8") as fh:
                doc = json.load(fh)
        except Exception as e:
            parse_errors.append({"file": rel, "error": type(e).__name__})
            continue
        if not walk_keys(doc, table, rel):
            truncated.append(rel)

    readers, py_files = scan_readers(root)

    rows = []
    for key in sorted(table):
        occ = table[key]
        shapes = {}
        for o in occ:
            shapes[o["shape"]] = shapes.get(o["shape"], 0) + 1
        cls = classify(shapes)
        files = sorted({o["file"] for o in occ})
        rows.append({
            "key": key,
            "class": cls,
            "shape_counts": shapes,
            "shapes": sorted(shapes),
            "occ": len(occ),
            "faces": len(files),
            "files": files[:12],
            "faces_truncated": max(0, len(files) - 12),
            "reader_sites": readers.get(key, 0),
            "kind": key_kind(key),
        })

    summary = {
        "faces_scanned": len(faces) - len(parse_errors),
        "faces_parse_error": len(parse_errors),
        "faces_truncated_node_budget": len(truncated),
        "truncated_faces": truncated[:20],
        "files_skipped": skipped,
        "py_files_scanned": py_files,
    }
    by_class = {c: 0 for c in CLASSES}
    for r in rows:
        by_class[r["class"]] += 1
    summary["by_class"] = by_class
    summary.update(derive_summary(rows, keys=len(rows), by_class=by_class))

    # Publish the conflicts, not the whole key set: 70,870 single-shape rows are a count, and a
    # 33 MB face that lists them is a face no reader scans (measured: the untrimmed face is 33 MB).
    published = [r for r in rows if r["class"] == "structural_conflict"]
    summary["rows_published"] = len(published)
    summary["rows_counted_only"] = len(rows) - len(published)
    verdict = decide(summary)

    return {
        "study": STUDY,
        "evidence_cutoff": TODAY,
        "verdict": verdict,
        "summary": summary,
        "rows": published,
        "rows_policy": ("only structural_conflict rows are listed; the other classes are counted in "
                        "by_class and in rows_counted_only"),
        "parse_errors": parse_errors,
        "face_classes": list(CLASSES),
        "vocab": sorted(VOCAB),
        "verify_covers": list(ROW_DERIVED),
        "verify_does_not_cover": list(WALK_ONLY),
        "note": ("a structural conflict is one key name stored as a number in one published face "
                 "and as a container/string/bool in another; null beside a value and int beside "
                 "float are published as their own classes and never added to that count."),
    }


def derive_summary(rows, keys=None, by_class=None):
    """Every count in the summary that is a function of the row table, re-added here.

    The corpus totals (faces scanned, parse errors, files skipped, py files read) are properties
    of the walk and are not re-derivable from rows; verify names them as such instead of pretending
    to check them.

    ``*_name_keys`` counts field-shaped keys only; ``*_index_keys`` counts row-map keys (numbers,
    codes, dates).  ``reader_sites`` is a *name-matched* count over the whole repo -- it says a site
    writes the same literal, never that the site opens the face that carries it (E390's rule, and
    the reason the read number is published as an upper bound).
    """
    conflicts = [r for r in rows if r.get("class") == "structural_conflict"]
    name_conf = [r for r in conflicts if r.get("kind") == "name"]
    index_conf = [r for r in conflicts if r.get("kind") != "name"]
    name_read = [r for r in name_conf if (r.get("reader_sites") or 0) > 0]
    name_latent = [r for r in name_conf if not (r.get("reader_sites") or 0)]
    return {
        "keys": len(rows) if keys is None else keys,
        "structural_conflicts": len(conflicts),
        "structural_conflicts_name_keys": len(name_conf),
        "structural_conflicts_index_keys": len(index_conf),
        "structural_conflicts_read": len(name_read),
        "structural_conflicts_latent": len(name_latent),
        "conflicted_keys_with_a_name_matched_read": len(
            {r["key"] for r in name_conf if (r.get("reader_sites") or 0) > 0}),
        "read_keys_in_conflict": sorted(r["key"] for r in name_read),
        "latent_keys": sorted(r["key"] for r in name_latent),
        "read_sites_on_conflicted_keys": sum(r.get("reader_sites") or 0 for r in name_read),
        "read_bound_is_name_matched_not_face_resolved": True,
    }


ROW_DERIVED = ("keys", "structural_conflicts", "structural_conflicts_name_keys",
               "structural_conflicts_index_keys", "structural_conflicts_read",
               "structural_conflicts_latent", "conflicted_keys_with_a_name_matched_read", "read_keys_in_conflict",
               "latent_keys", "read_sites_on_conflicted_keys",
               "read_bound_is_name_matched_not_face_resolved")
WALK_ONLY = ("faces_scanned", "faces_parse_error", "faces_truncated_node_budget",
             "files_skipped", "py_files_scanned", "truncated_faces")


def verify(row_only=True):
    """Re-derive every published number from the published row table (no corpus walk).

    ``row_only=True`` is the default because a full rebuild re-parses the whole results tree
    (12k faces / ~560 MB, minutes); the S6 leg must be cheap.  Everything that is a function of
    the rows is recomputed; the walk totals are listed in ``walk_only`` so a reader knows which
    numbers this check does not cover.
    """
    path = os.path.join(OUTDIR, FACE)
    if not os.path.exists(path):
        return ["face missing: %s" % FACE]
    with io.open(path, encoding="utf-8") as fh:
        disk = json.load(fh)
    rows = disk.get("rows") or []
    published = disk.get("summary") or {}
    live = derive_summary(rows, keys=published.get("keys"))
    problems = []
    if published.get("rows_published") != len(rows):
        problems.append("rows_published is not the number of listed rows")
    if int(published.get("rows_counted_only") or 0) + len(rows) != int(published.get("keys") or 0):
        problems.append("counted-only rows and listed rows do not add up to the key count")
    if any(r.get("class") != "structural_conflict" for r in rows):
        problems.append("a non-conflict row was listed (the face publishes conflicts only)")
    by_class = published.get("by_class") or {}
    if sum(by_class.values()) != int(published.get("keys") or 0):
        problems.append("by_class does not add up to the key count")
    for k in ROW_DERIVED:
        if published.get(k) != live.get(k):
            problems.append("summary.%s does not re-add from the rows" % k)
    if disk.get("verdict") != decide(published):
        problems.append("verdict does not re-derive from the summary")
    if disk.get("verdict") not in VOCAB:
        problems.append("verdict outside the frozen vocabulary")
    if disk.get("face_classes") != list(CLASSES):
        problems.append("class vocabulary drifted")
    for row in rows:
        if classify({s: 1 for s in row.get("shapes") or []}) != row.get("class"):
            problems.append("row %r does not re-classify" % row.get("key"))
            break
        if row.get("occ") != sum((row.get("shape_counts") or {}).values()):
            problems.append("row %r occ does not re-add from shape_counts" % row.get("key"))
            break
        if row.get("kind") != key_kind(row.get("key") or ""):
            problems.append("row %r is filed under the wrong key kind" % row.get("key"))
            break
    return problems


# ---------------------------------------------------------------- fixtures
FIXTURE_FACES = {
    "results/a.json": {"cap": 5, "rows": [{"k": 1}], "asof": "2026-11-03", "n": None, "0": 7},
    "results/b.json": {"cap": {"cell": 5}, "rows": [], "asof": "notes.md", "n": 3, "0": {"cell": 1}},
    "results/c.json": {"cap": 5.0, "rows": [{"k": 1}], "flat": [1, 2], "wide": ["a", 1]},
}
FIXTURE_PY = {
    "scripts/reader.py": 'd = load()\nv = d["cap"]\nw = d.get("flat")\n',
    "scripts/unread.py": 'x = 1\n',
}


def _fixture_tree(tmp):
    for rel, doc in FIXTURE_FACES.items():
        p = os.path.join(tmp, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(doc, fh)
    for rel, src in FIXTURE_PY.items():
        p = os.path.join(tmp, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(src)


def selftest():
    import tempfile
    fails = []

    checks = []

    def ck(cond, msg):
        checks.append(cond)
        if not cond:
            fails.append(msg)

    # shape vocabulary
    ck(shape(None) == "null", "None is not null")
    ck(shape(True) == "bool", "True graded as a number (bool is not int here)")
    ck(shape(3) == "int" and shape(3.0) == "float", "int/float widths not separated")
    ck(shape("2026-11-03") == "str:timestamp", "a bare ISO date is not a timestamp")
    ck(shape("results/x.json") == "str:path", "a path is not a path")
    ck(shape([]) == "list[]", "empty list not marked empty")
    ck(shape([1, 2]) == "list[int]", "homogeneous list element shape wrong")
    ck(shape([1, "a"]) == "list[mixed]", "heterogeneous list not mixed")

    # classes: the four refusals
    ck(classify({"int": 1, "dict": 1}) == "structural_conflict", "num vs dict is not a conflict")
    ck(classify({"int": 1, "null": 1}) == "null_or_value", "null beside a value was called a conflict")
    ck(classify({"int": 1, "float": 1}) == "numeric_width", "int vs float was called a conflict")
    ck(classify({"list[]", "list[int]"}) == "single", "empty list beside a list was called a conflict")
    ck(classify({"list[int]", "list[str]"}) == "list_element_conflict", "two element shapes not caught")
    ck(classify({"str", "str:path"}) == "string_kind_conflict", "string kinds not separated")
    ck(classify({"dict": 1}) == "single", "one shape is not a conflict")

    # reader extraction must be literal-only
    rk = reader_keys('d["a"]\nd.get("b")\nd[k]\nd.pop("c")\n')
    ck(rk.get("a") == 1 and rk.get("b") == 1 and rk.get("c") == 1, "literal reads not counted")
    ck(len(rk) == 3, "a variable subscript was credited as a literal read")

    tmp = tempfile.mkdtemp(prefix="e391_")
    _fixture_tree(tmp)
    doc = build(root=tmp)
    sums = doc["summary"]
    ck(sums["faces_scanned"] == 3, "fixture faces not scanned: %s" % sums["faces_scanned"])
    ck(sums["structural_conflicts"] == 2, "cap and the index key should be the two conflicts: %s"
       % sums["structural_conflicts"])
    ck(sums["structural_conflicts_name_keys"] == 1, "the index key was counted as a field name")
    ck(sums["structural_conflicts_index_keys"] == 1, "the index-key conflict was dropped")
    ck(sums["structural_conflicts_read"] == 1, "cap is read by the fixture reader")
    ck(sums["structural_conflicts_latent"] == 0, "no latent conflict in the fixture")
    ck(doc["verdict"] == V_READ, "fixture verdict is not V_READ: %s" % doc["verdict"])
    ck(sums["read_keys_in_conflict"] == ["cap"], "read conflict list wrong")
    ck("rows" in doc and not any(r["key"] == "flat" for r in doc["rows"]),
       "a counted-only row was listed in the published table")
    ck(all(r["class"] == "structural_conflict" for r in doc["rows"]),
       "the published table lists a row that is not a conflict")
    ck(sums["rows_published"] == len(doc["rows"]), "rows_published is not the listed row count")
    ck(sums["rows_published"] + sums["rows_counted_only"] == sums["keys"],
       "listed plus counted-only rows do not add up to the key count")
    ck(sums["by_class"]["single"] >= 1, "the counted-only singles vanished from by_class")

    # key kind: a row map's index is not a field name (measured split: 3,910 index / 3,887 name)
    ck(key_kind("cap") == "name", "a field name was filed as an index")
    ck(key_kind("_meta") == "name", "an underscore field was filed as an index")
    ck(key_kind("0") == "index", "the index '0' was filed as a field name")
    ck(key_kind("000001") == "index", "a stock code was filed as a field name")
    ck(key_kind("2026-11-03") == "index", "a date key was filed as a field name")
    ck(key_kind("+ 19,") == "index", "a sign-prefixed index was filed as a field name")

    # a tree whose only conflicts are index keys is not a field-name conflict at all
    tmp3 = tempfile.mkdtemp(prefix="e391_")
    for rel, docx in (("results/x.json", {"0": 1}), ("results/y.json", {"0": {"cell": 1}})):
        p = os.path.join(tmp3, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(docx, fh)
    doc3 = build(root=tmp3)
    ck(doc3["summary"]["structural_conflicts"] == 1, "index conflict not measured at all")
    ck(doc3["summary"]["structural_conflicts_name_keys"] == 0, "index key counted as a name")
    ck(doc3["verdict"] == V_NONE, "an index-only tree is not 'no field-name conflict'")

    # a conflict nobody reads must be reported as latent, not active
    tmp2 = tempfile.mkdtemp(prefix="e391_")
    _fixture_tree(tmp2)
    os.remove(os.path.join(tmp2, "scripts", "reader.py"))
    doc2 = build(root=tmp2)
    ck(doc2["verdict"] == V_LATENT, "unread conflict was not graded latent: %s" % doc2["verdict"])
    ck(doc2["summary"]["structural_conflicts_read"] == 0, "latent tree reports a read")

    # the real corpus must not count its own face or its own source (cheap: population only,
    # a full build here would spend the round's wall time re-parsing 12k faces for one assert)
    faces_live, _skipped = json_corpus()
    ck(not any(os.path.basename(p) in OWN_FACES for p, _rel in faces_live),
       "the census listed its own output face as a corpus face")
    ck(not any(os.path.abspath(p) == SELF for p in py_corpus()),
       "the census listed its own source as a reader site")

    total = len(checks)
    print("selftest %d/%d" % (total - len(fails), total))
    for f in fails:
        print("  FAIL", f)
    return 0 if not fails else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "verify":
        problems = verify()
        print(json.dumps({"problems": problems}, ensure_ascii=False))
        return 0 if not problems else 1
    if cmd == "run":
        doc = build()
        os.makedirs(OUTDIR, exist_ok=True)
        with io.open(os.path.join(OUTDIR, FACE), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(doc, fh, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            fh.write("\n")
        mirror = dict(doc)
        mirror["face"] = FACE
        with io.open(os.path.join(OUTDIR, LATEST), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(mirror, fh, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            fh.write("\n")
        s = doc["summary"]
        print("%s -> %s" % (STUDY, os.path.join(OUTDIR, FACE)))
        print("verdict: %s" % doc["verdict"])
        print("%d faces / %d keys / %d structural conflicts = %d field-shaped + %d index (%d read by "
              "name match, %d latent) / %d name-matched read sites"
              % (s["faces_scanned"], s["keys"], s["structural_conflicts"],
                 s["structural_conflicts_name_keys"], s["structural_conflicts_index_keys"],
                 s["structural_conflicts_read"], s["structural_conflicts_latent"],
                 s["read_sites_on_conflicted_keys"]))
        for r in doc["rows"]:
            if r["class"] == "structural_conflict" and r["kind"] == "name":
                print("  conflict:", r["key"], r["shapes"], "faces=%d readers=%d"
                      % (r["faces"], r["reader_sites"]))
        return 0
    print("unknown mode: %s" % cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))