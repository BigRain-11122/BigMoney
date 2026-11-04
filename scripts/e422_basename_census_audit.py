"""E422: does any basename-keyed census record a face without the directory its reader spells?

E421 found that E406's 33 unresolved names were mostly stored as a bare basename, so "resolves
to no file" was a property of the census's path construction rather than of the tree. This study
asks the same question of the OTHER basename-keyed censuses and prices the answer per census:

    E402 fragment producers        name field `fragment`   rows 52
    E404 constant directories      name field `fragment`   rows 18
    E409 unfloored faces           name field `face`       rows  2
    E411 reader tiers              name field `face`       rows 204

For every row: what form is the name in (bare vs spelled with a directory), and -- for the bare
ones -- does any directory the python corpus spells hold a file of that name. A row's published
landing boolean only changes if that join can exist, so the bill is "rows whose reading changes",
not "rows in a census that happens to store a short name".

Two rules hold the instrument honest:
  * a name match is exact or `/name`-suffixed, never `endswith(name)` (E330 family: `delta_latest
    .json` sits inside `keydelta_latest.json`);
  * a fragment the census itself classifies as a piece of a computed name is not a filename, so
    "rejoining a directory" is not even defined for it.

verbs: run | verify | selftest
"""
import ast
import collections
import hashlib
import io
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

# Reuse, do not rebuild: the corpus walk and the on-disk basename index already exist (E421).
import e421_strong_basis_resolution as E421  # noqa: E402

SELF = "scripts/e422_basename_census_audit.py"
STATE_TILT = os.path.join(ROOT, "results", "state_tilt")
LATEST = os.path.join(STATE_TILT, "basenamecensus_latest.json")

# Counts over the python corpus (which grows every round), re-derived by a leg from the row list
# instead of compared to a fresh build -- declared here so no leg carries its own copy of the
# list (scripts/population_keys.py, r1441).
POPULATION_KEYS = ("bare_rows_with_a_directory_spelled_in_the_corpus",
                   "bare_rows_with_a_literal_directory_spelling",
                   "bare_rows_with_only_a_variable_head_spelling")

CENSUSES = [
    {
        "study": "E402_fragment_producers",
        "rows_key": "rows",
        "name_key": "fragment",
        "boolean_keys": ["producer_path_exists"],
        "directory_keys": ["producer_directory_expression", "producer_composed_path"],
        "not_a_whole_filename_class_key": "producer_class",
        "not_a_whole_filename_class": (
            "fragment_is_a_suffix_or_prefix_of_a_computed_name_so_the_key_was_never_a_whole_filename"
        ),
    },
    {
        "study": "E404_constant_directory_resolution",
        "rows_key": "rows",
        "name_key": "fragment",
        "boolean_keys": ["path_exists"],
        "directory_keys": ["resolved_directory", "composed_path", "directory_expression"],
        "not_a_whole_filename_class_key": "class",
        "not_a_whole_filename_class": None,
    },
    {
        "study": "E409_session_only_writers_leave_their_readers_unfloored",
        "rows_key": "ledger",
        "name_key": "face",
        "boolean_keys": ["on_disk"],
        "directory_keys": [],
        "not_a_whole_filename_class_key": None,
        "not_a_whole_filename_class": None,
    },
    {
        "study": "E411_reader_tiers_for_every_face_the_suite_opens",
        "rows_key": "faces",
        "name_key": "face",
        "boolean_keys": ["on_disk"],
        "directory_keys": [],
        "not_a_whole_filename_class_key": None,
        "not_a_whole_filename_class": None,
    },
]


# ------------------------------------------------------------------ small helpers

def _rel(path: str) -> str:
    return os.path.relpath(path, ROOT).replace("\\", "/")


def _norm(value: str) -> str:
    return str(value).replace("\\", "/")


def is_bare(name: str) -> bool:
    """A name with no directory part at all."""
    return "/" not in _norm(name) and "\\" not in str(name)


def spells(node_strings, base: str):
    """Directories (as spelled) that name this basename: exact `/name` tails only."""
    dirs = set()
    for s in node_strings:
        if not isinstance(s, str):
            continue
        n = _norm(s)
        if n == base:
            continue
        if n.endswith("/" + base):
            dirs.add(n[: -(len(base) + 1)] or "/")
    return dirs


def constant_strings(text: str):
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    return [n.value for n in ast.walk(tree)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)]


def _parts(node):
    """`os.path.join('a', 'b', name)`, `Path('a') / 'b' / name` -> [('a',1),('b',1),(name,0)].

    The flag says whether the part is a literal; a spelling whose head contains a variable is
    recorded but cannot be resolved to a directory on disk, and is published as such."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [(node.value, 1)]
    if isinstance(node, ast.Call):
        parts = []
        func = node.func
        name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
        if name not in ("join", "Path", "PurePath", "path"):
            return None
        for arg in node.args:
            sub = _parts(arg)
            if sub is None:
                return None
            parts.extend(sub)
        return parts
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        left = _parts(node.left)
        right = _parts(node.right)
        if left is None or right is None:
            return None
        return left + right
    if isinstance(node, ast.Name):
        return [(node.id, 0)]
    if isinstance(node, ast.Attribute):
        return [(node.attr, 0)]
    return None


def _all_constant_parts(node):
    parts = _parts(node)
    return None if parts is None else [p for p, _ in parts]


def spell_sites(text: str, base: str) -> set:
    """Directories this module spells in front of `base`, whether as one literal or as the
    leading parts of a join()/Path() chain. A trailing bare constant is not a spelling."""
    out = set()
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return out
    for node in ast.walk(tree):
        parts = _all_constant_parts(node)
        if not parts or len(parts) < 2:
            continue
        tail = _norm(parts[-1])
        if tail != base:
            continue
        head = [_norm(p) for p in parts[:-1] if isinstance(p, str)]
        if not head:
            continue
        out.add("/".join(head))
    for s in constant_strings(text):
        out |= spells([s], base)
    return out


def directory_spellings(base: str, texts, exclude=()) -> list:
    """Every directory the corpus spells in front of this basename, sorted.

    `texts` may be the raw{rel: text} mapping (parsed here) or an index built once by
    `spelling_index`. The index form exists because a per-name parse of the whole corpus costs
    minutes, not seconds (E419's per-call `get_source_segment` lesson)."""
    if isinstance(texts, SpellingIndex):
        return texts.dirs_for(base)
    out = set()
    for rel, text in texts.items():
        if rel in exclude or rel == SELF:
            continue
        out |= spell_sites(text, base)
    return sorted(out)


class SpellingIndex:
    """base -> directories, built in one parse of the corpus.

    `dirs_for` returns every spelling; `literal_dirs_for` only those whose head is all literals,
    because a head like `fx/results/grid_paper` is a fixture base, not a place on disk."""

    def __init__(self, texts: dict, exclude=()):
        self._index = collections.defaultdict(set)
        self._literal = collections.defaultdict(set)
        for rel, text in texts.items():
            if rel in exclude or rel == SELF:
                continue
            try:
                tree = ast.parse(text)
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                parts = _parts(node)
                if not parts or len(parts) < 2:
                    continue
                tail = _norm(parts[-1][0])
                if "." not in tail or "/" in tail:
                    continue
                head = [_norm(p) for p, _ in parts[:-1]]
                if not head:
                    continue
                spelled = "/".join(head)
                self._index[tail].add(spelled)
                if all(flag for _, flag in parts[:-1]):
                    self._literal[tail].add(spelled)
            for s in [n.value for n in ast.walk(tree)
                      if isinstance(n, ast.Constant) and isinstance(n.value, str)]:
                n = _norm(s)
                if "/" not in n:
                    continue
                base = n.rsplit("/", 1)[1]
                if "." in base:
                    d = n[: -(len(base) + 1)] or "/"
                    self._index[base].add(d)
                    self._literal[base].add(d)

    def dirs_for(self, base: str) -> list:
        return sorted(self._index.get(base, ()))

    def literal_dirs_for(self, base: str) -> list:
        return sorted(self._literal.get(base, ()))


def repo_file_index() -> dict:
    """basename -> every on-disk path with that name, in one walk (same top-dir recipe as E421)."""
    index = collections.defaultdict(list)
    for top in ("results", "docs", "data", "research", "knowledge", "fleet", "state", "scripts"):
        root = os.path.join(ROOT, top)
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in ("_quarantine", "__pycache__")]
            for name in filenames:
                index[name].append(_rel(os.path.join(dirpath, name)))
    return index


def join_exists(directory: str, base: str, tree_root: str = ROOT) -> bool:
    d = _norm(directory).lstrip("/")
    if not d or d in (".",):
        return os.path.exists(os.path.join(tree_root, base))
    if os.path.isabs(d):
        return os.path.exists(os.path.join(d, base))
    return os.path.exists(os.path.join(tree_root, d.replace("/", os.sep), base))


def published_boolean(row: dict, keys) -> object:
    for k in keys:
        if k in row:
            return row[k]
    return None


def published_directory(row: dict, keys) -> object:
    for k in keys:
        v = row.get(k)
        if isinstance(v, str) and v.strip():
            return v
    return None


# ------------------------------------------------------------------ per-row audit

def audit_row(census: dict, row: dict, texts: dict, repo_index, tree_root: str = ROOT,
              exclude=()) -> dict:
    name = row.get(census["name_key"])
    name = _norm(name) if isinstance(name, str) else ""
    out = {
        "census": census["study"],
        "name": name,
        "name_form": "path" if (name and not is_bare(name)) else ("bare" if name else "missing"),
        "published_booleans": {k: row.get(k) for k in census["boolean_keys"] if k in row},
        "published_directory": published_directory(row, census.get("directory_keys") or []),
    }
    if out["name_form"] != "bare":
        out["reading_changes_if_rejoined"] = False
        out["why_not"] = "the row already spells a directory, so there is nothing to rejoin"
        return out

    cls_key = census.get("not_a_whole_filename_class_key")
    cls = row.get(cls_key) if cls_key else None
    out["published_class"] = cls
    out["is_a_whole_filename"] = cls != census.get("not_a_whole_filename_class")

    if not out["is_a_whole_filename"]:
        out["directories_the_corpus_spells"] = []
        out["joins_that_exist"] = []
        out["files_in_repo_with_this_name"] = []
        out["reading_changes_if_rejoined"] = False
        out["why_not"] = ("the census itself classifies this as a piece of a computed name, so it is "
                          "not a filename a directory could be rejoined to")
        return out

    dirs = directory_spellings(name, texts, exclude=exclude)
    literal = (texts.literal_dirs_for(name) if isinstance(texts, SpellingIndex) else list(dirs))
    joins = [d for d in dirs if join_exists(d, name, tree_root)]
    files = list(repo_index.get(name, ())) if isinstance(repo_index, dict) \
        else (list(repo_index(name)) if repo_index else [])
    published = [v for v in out["published_booleans"].values()]
    any_true = any(v is True for v in published)

    changes = bool(joins or files) and not any_true
    out["directories_the_corpus_spells"] = dirs
    out["directories_spelled_with_a_literal_head"] = literal
    out["directories_spelled_with_a_variable_head"] = [d for d in dirs if d not in literal]
    out["joins_that_exist"] = joins
    out["files_in_repo_with_this_name"] = files
    out["reading_changes_if_rejoined"] = changes
    if changes:
        out["why_not"] = ""
    elif any_true:
        out["why_not"] = "the published boolean is already true, so rejoining cannot change it"
    elif dirs:
        out["why_not"] = ("a directory is spelled in the corpus but it does not hold a file of this "
                          "name, so the join cannot land")
    else:
        out["why_not"] = "no directory in the python corpus spells this basename at all"
    return out


def build(cutoff=None, faces=None, texts=None, repo_index=None, tree_root=ROOT) -> dict:
    if texts is None:
        texts = SpellingIndex(E421.module_texts())
    elif isinstance(texts, dict):
        texts = SpellingIndex(texts)
    repo_index_ = repo_file_index() if repo_index is None else repo_index
    faces = _faces() if faces is None else faces

    rows = []
    censuses = []
    for spec in CENSUSES:
        face_path, face = faces[spec["study"]]
        source_rows = face.get(spec["rows_key"]) or []
        per = [audit_row(spec, r, texts, repo_index_, tree_root) for r in source_rows]
        rows.extend(per)
        censuses.append({
            "study": spec["study"],
            "face": _rel(face_path),
            "evidence_cutoff": face.get("evidence_cutoff"),
            "rows_key": spec["rows_key"],
            "name_key": spec["name_key"],
            "rows": len(per),
            "bare_rows": sum(1 for r in per if r["name_form"] == "bare"),
            "path_rows": sum(1 for r in per if r["name_form"] == "path"),
            "bare_rows_with_a_published_directory": sum(
                1 for r in per
                if r["name_form"] == "bare" and r.get("published_directory")),
            "bare_rows_with_no_directory_in_any_field": sum(
                1 for r in per
                if r["name_form"] == "bare" and not r.get("published_directory")),
            "bare_rows_with_a_literal_directory_spelling": sum(
                1 for r in per if r.get("directories_spelled_with_a_literal_head")),
            "bare_rows_with_only_a_variable_head_spelling": sum(
                1 for r in per
                if r.get("directories_the_corpus_spells")
                and not r.get("directories_spelled_with_a_literal_head")),
            "bare_rows_that_are_not_whole_filenames": sum(
                1 for r in per if r["name_form"] == "bare" and r.get("is_a_whole_filename") is False),
            "bare_rows_with_a_directory_spelled_in_the_corpus": sum(
                1 for r in per if r.get("directories_the_corpus_spells")),
            "bare_rows_whose_join_exists": sum(1 for r in per if r.get("joins_that_exist")),
            "bare_rows_whose_name_exists_anywhere_in_the_repo": sum(
                1 for r in per if r.get("files_in_repo_with_this_name")),
            "rows_whose_reading_changes_if_rejoined": sum(
                1 for r in per if r.get("reading_changes_if_rejoined")),
            "published_true_booleans": sum(
                1 for r in per for v in r["published_booleans"].values() if v is True),
        })

    cutoffs = [c["evidence_cutoff"] for c in censuses if c["evidence_cutoff"]]
    cutoff = cutoff or (min(cutoffs) if cutoffs else None)

    bare = [r for r in rows if r["name_form"] == "bare"]
    path = [r for r in rows if r["name_form"] == "path"]
    bare_no_dir = [r for r in bare if not r.get("published_directory")]
    changing = [r for r in rows if r.get("reading_changes_if_rejoined")]

    # Incidental: a field NAMED for a directory that holds a file path (E206/E207 family).
    named_directory_holding_a_file = []
    for spec in CENSUSES:
        _, face = faces[spec["study"]]
        for r in face.get(spec["rows_key"]) or []:
            v = r.get("resolved_directory")
            if isinstance(v, str) and os.path.splitext(_norm(v))[1] in (".json", ".md", ".csv", ".jsonl"):
                name = _norm(r.get(spec["name_key"]) or "")
                composed = _norm(v) + "/" + name
                named_directory_holding_a_file.append({
                    "census": spec["study"], "name": name,
                    "field": "resolved_directory", "value": _norm(v),
                    "basename_equals_the_fragment": os.path.basename(_norm(v)) == name,
                    "a_join_would_compose": composed,
                    "that_join_exists": os.path.exists(os.path.join(ROOT, composed.replace("/", os.sep))),
                })

    summary = {
        "censuses": len(censuses),
        "rows_in_population": len(rows),
        "rows_recording_a_bare_name": len(bare),
        "rows_spelling_a_directory": len(path),
        "censuses_recording_a_bare_name_without_a_directory": [
            c["study"] for c in censuses if c["bare_rows"] and
            c["bare_rows"] > c["bare_rows_with_a_published_directory"]
        ],
        "bare_rows_with_no_published_directory": len(bare_no_dir),
        "bare_rows_with_a_published_directory": sum(
            1 for c in censuses for _ in range(c["bare_rows_with_a_published_directory"])),
        "bare_rows_that_are_not_whole_filenames": sum(
            1 for r in bare if r.get("is_a_whole_filename") is False),
        "bare_rows_with_a_directory_spelled_in_the_corpus": sum(
            1 for r in bare if r.get("directories_the_corpus_spells")),
        "bare_rows_with_a_literal_directory_spelling": sum(
            1 for r in bare if r.get("directories_spelled_with_a_literal_head")),
        "bare_rows_with_only_a_variable_head_spelling": sum(
            1 for r in bare if r.get("directories_the_corpus_spells")
            and not r.get("directories_spelled_with_a_literal_head")),
        "bare_rows_whose_join_exists": sum(1 for r in bare if r.get("joins_that_exist")),
        "bare_rows_whose_name_exists_anywhere_in_the_repo": sum(
            1 for r in bare if r.get("files_in_repo_with_this_name")),
        "rows_whose_reading_changes_if_rejoined": len(changing),
        "control_path_rows_whose_file_exists": sum(
            1 for r in path for v in r["published_booleans"].values() if v is True),
        "control_path_rows": len(path),
        "named_directory_field_holding_a_file_path": len(named_directory_holding_a_file),
        "named_directory_field_joins_that_would_double_the_name": sum(
            1 for r in named_directory_holding_a_file if r["basename_equals_the_fragment"]),
        "named_directory_field_joins_that_exist": sum(
            1 for r in named_directory_holding_a_file if r["that_join_exists"]),
        "verdict": "",
    }
    summary["verdict"] = _verdict(summary)

    return {
        "study": "E422_basename_census_audit",
        "card": "E422-WHICH-OTHER-CENSUS-RECORDS-A-BARE-BASENAME",
        "evidence_cutoff": cutoff,
        "censuses": censuses,
        "rows": rows,
        "incidental": {"named_directory_field_holding_a_file_path": named_directory_holding_a_file},
        "bounds": {
            "measured": ("each row's name form and, for bare names, every directory the python "
                         "corpus spells in front of that basename, tested for existence on disk"),
            "not_measured": ("a directory spelled in source is a bound, not a runtime resolution: the "
                             "study does not execute the reader to learn which directory it is handed"),
            "no_rewrites": "no published face, census or reader is edited here",
        },
        "summary": summary,
        "population_keys": list(POPULATION_KEYS),
        "verdict": summary["verdict"],
    }


def _verdict(s: dict) -> str:
    if s["rows_whose_reading_changes_if_rejoined"] == 0:
        if len(s["censuses_recording_a_bare_name_without_a_directory"]) == 1:
            return ("one_of_four_basename_keyed_censuses_stores_the_name_without_its_directory_and_"
                    "rejoining_a_directory_changes_no_row")
        return "no_census_in_the_population_records_a_bare_basename_without_its_directory"
    return ("basename_storage_is_not_only_a_property_of_E406_censuses_are_affected_and_"
            "%d_rows_change" % s["rows_whose_reading_changes_if_rejoined"])


# ------------------------------------------------------------------ faces on disk

def _faces() -> dict:
    out = {}
    for name in sorted(os.listdir(STATE_TILT)):
        if not name.endswith(".json") or name.endswith("_latest.json"):
            continue
        path = os.path.join(STATE_TILT, name)
        try:
            with io.open(path, encoding="utf-8") as fh:
                face = json.load(fh)
        except (OSError, ValueError):
            continue
        study = face.get("study")
        if study not in {c["study"] for c in CENSUSES}:
            continue
        prev = out.get(study)
        key = (str(face.get("evidence_cutoff") or ""), os.path.getmtime(path))
        if prev is None or key > (str(prev[1].get("evidence_cutoff") or ""), os.path.getmtime(prev[0])):
            out[study] = (path, face)
    missing = [c["study"] for c in CENSUSES if c["study"] not in out]
    if missing:
        raise SystemExit("census faces missing for: %s" % ", ".join(missing))
    return out


# ------------------------------------------------------------------ verbs

def run() -> dict:
    face = build()
    cutoff = face["evidence_cutoff"] or "unknown"
    path = os.path.join(STATE_TILT, "BASENAMECENSUS-%s.json" % cutoff)
    blob = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(blob + "\n")
    with io.open(LATEST, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(blob + "\n")
    print(json.dumps(face["summary"], ensure_ascii=False, indent=1))
    print("wrote %s (sha %s)" % (_rel(path), hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]))
    print("verdict:", face["verdict"])
    return face


def verify(face=None) -> list:
    problems = []
    face = face or build()
    for c in face["censuses"]:
        if c["bare_rows"] + c["path_rows"] != c["rows"]:
            problems.append("%s: bare+path != rows" % c["study"])
        if c["rows_whose_reading_changes_if_rejoined"] > c["bare_rows"]:
            problems.append("%s: more changing rows than bare rows" % c["study"])
    s = face["summary"]
    if s["rows_in_population"] != sum(c["rows"] for c in face["censuses"]):
        problems.append("population does not sum to the per-census rows")
    if s["rows_recording_a_bare_name"] != sum(c["bare_rows"] for c in face["censuses"]):
        problems.append("bare rows do not sum to the per-census bare rows")
    recounted = sum(1 for r in face["rows"] if r.get("reading_changes_if_rejoined"))
    if recounted != s["rows_whose_reading_changes_if_rejoined"]:
        problems.append("changing rows do not re-derive from the row list")
    if face["verdict"] != _verdict(s):
        problems.append("verdict does not re-derive from the summary")
    if not face.get("evidence_cutoff"):
        problems.append("no evidence_cutoff (science gate C2)")
    else:
        for c in face["censuses"]:
            if c["evidence_cutoff"] and c["evidence_cutoff"] < face["evidence_cutoff"]:
                problems.append("%s: cutoff older than the published cutoff" % c["study"])
    print("problems:", problems if problems else "none")
    return problems


def _fixture_texts() -> dict:
    return {
        "scripts/fixture_writer.py": (
            "import os\n"
            "OUT = os.path.join('results', 'sample', 'alpha_face.json')\n"
            "open(OUT, 'w')\n"
            "open(os.path.join(tmp, 'beta_face.json'), 'w')\n"
        ),
        "scripts/fixture_suffix.py": "NAME = 'keydelta_latest.json'\n",
    }


def selftest() -> int:
    fails = []

    def leg(name, ok, detail=""):
        print("[%s] %s%s" % ("PASS" if ok else "FAIL", name, (" | " + detail) if detail else ""))
        if not ok:
            fails.append(name)

    tmp = tempfile.mkdtemp(prefix="e422_")
    os.makedirs(os.path.join(tmp, "results", "sample"), exist_ok=True)
    with io.open(os.path.join(tmp, "results", "sample", "alpha_face.json"), "w") as fh:
        fh.write("{}")
    texts = _fixture_texts()

    leg("bare name has no directory part", is_bare("alpha_face.json") and not is_bare("results/alpha_face.json"))

    dirs = directory_spellings("alpha_face.json", texts)
    leg("a spelled path yields its directory", dirs == ["results/sample"], str(dirs))

    leg("join exists where the file is", join_exists("results/sample", "alpha_face.json", tmp))
    leg("join does not exist where it is not",
        not join_exists("results/absent", "alpha_face.json", tmp))

    leg("a basename inside a longer name is not spelled",
        spells(["keydelta_latest.json"], "delta_latest.json") == set(),
        "endswith is not 'spells'")
    leg("a bare constant is not a directory spelling",
        spells(["alpha_face.json"], "alpha_face.json") == set())

    spec = dict(CENSUSES[0])
    whole = {"fragment": "alpha_face.json", "producer_path_exists": False,
             "producer_class": "cwd_relative_no_directory_supplied"}
    row = audit_row(spec, whole, texts, lambda b: [], tmp)
    leg("a bare whole name that lands changes its reading", row["reading_changes_if_rejoined"] is True,
        str(row["joins_that_exist"]))

    already = dict(whole, producer_path_exists=True)
    row2 = audit_row(spec, already, texts, lambda b: [], tmp)
    leg("a true boolean cannot change", row2["reading_changes_if_rejoined"] is False)

    nolanding = dict(whole, fragment="absent_face.json")
    row3 = audit_row(spec, nolanding, texts, lambda b: [], tmp)
    leg("a bare name nothing spells does not change", row3["reading_changes_if_rejoined"] is False)

    piece = dict(whole, producer_class=spec["not_a_whole_filename_class"])
    row4 = audit_row(spec, piece, texts, lambda b: [], tmp)
    leg("a piece of a computed name is not a filename", row4["is_a_whole_filename"] is False)

    e404 = dict(CENSUSES[1])
    withdir = {"fragment": "alpha_face.json", "path_exists": False,
               "resolved_directory": "results/sample"}
    row5 = audit_row(e404, withdir, texts, lambda b: [], tmp)
    leg("a bare name with a published directory is not 'without a directory'",
        row5["published_directory"] == "results/sample" and row5["name_form"] == "bare")

    pathrow = audit_row(e404, {"fragment": "results/sample/alpha_face.json", "path_exists": False},
                        texts, lambda b: [], tmp)
    leg("a path row is never counted as bare", pathrow["name_form"] == "path")

    faces = {}
    for spec2 in CENSUSES:
        rows = [dict(whole), dict(already), dict(piece)] if spec2["study"].startswith("E402") \
            else [{"fragment": "alpha_face.json", "path_exists": False}] if spec2["study"].startswith("E404") \
            else [{"face": "results/sample/alpha_face.json", "on_disk": True}]
        faces[spec2["study"]] = (spec2["study"] + ".json", {
            "study": spec2["study"], "evidence_cutoff": "2026-11-04", spec2["rows_key"]: rows})
    built = build(cutoff="2026-11-04", faces=faces, texts=texts, repo_index=lambda b: [], tree_root=tmp)
    leg("summary sums the per-census rows",
        built["summary"]["rows_in_population"] == sum(c["rows"] for c in built["censuses"]))
    leg("verdict re-derives", built["verdict"] == _verdict(built["summary"]))
    leg("verify is clean on the fixture face", verify(built) == [])
    leg("evidence_cutoff is derived, not written by hand",
        built["evidence_cutoff"] == "2026-11-04")

    print("%d legs, %d failed" % (16, len(fails)))
    return 1 if fails else 0


def main(argv) -> int:
    verb = (argv[1] if len(argv) > 1 else "run").lower()
    if verb == "run":
        run()
        return 0
    if verb == "verify":
        return 1 if verify() else 0
    if verb == "selftest":
        return selftest()
    raise SystemExit("usage: %s [run|verify|selftest]" % argv[0])


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))