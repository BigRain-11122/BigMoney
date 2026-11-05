"""E417 -- does any face the suite opens have a same-named foreign copy in a directory
a reader could be started from?

E415 priced the two bare-path reads in the durable corpus: one of them would measure a
different document of the same basename from another launch directory.  E417 widens the
question from the call shape to the NAME.  Population = the faces E411 priced (read from
its published face, never hardcoded).  For every literal face we ask: which directories
could serve a bare read of this basename (the repo root, every directory holding a
``*latest.json`` pointer, the CLI home, the sibling repositories under the fleet root),
and does any of them hold a DIFFERENT file with that basename.

The bill is the shadow population: same bytes / different document / non-json, plus a
key-level diff for JSON so a reader can see whether the two copies differ in the fields
it reads.  Whether the name is actually read as a bare literal is joined from
``smoke_test.py`` (an AST search for string literals equal to the basename) -- a name that
only ever appears with a directory component is a different (pinned) shape.

Deterministic, offline, no writer runs.  ``run`` writes
``results/state_tilt/SHADOWFACE-<cutoff>.json`` + ``shadowface_latest.json``; ``verify``
re-derives and refuses a stored face that does not agree; ``selftest`` exercises the
classifiers on a temp fixture.
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "results", "state_tilt")
FACE = "SHADOWFACE-%s.json"
LATEST = "shadowface_latest.json"
STUDY = "E417_shadow_face"

SKIP_DIRNAMES = {"__pycache__", "node_modules", ".git", ".codely-cli", "_quarantine",
                 "Money02", "Money0923", "legacy", "data", "logs"}

# Directories a process could plausibly be launched from.  Each entry is (label, path);
# a missing path is reported, not invented.
FLEET_ROOT = r"C:\Fluxgroup"
CLI_HOME = r"C:\Users\Administrator\.codely-cli"

C_UNIQUE = "name_exists_only_at_the_face"
C_SAME_BYTES = "foreign_copy_same_bytes"
C_DIFFERENT = "foreign_copy_different_document"
CLASS_VOCAB = (C_UNIQUE, C_SAME_BYTES, C_DIFFERENT)

I_SAME_KEYS = "same_top_level_keys"
I_DIFFERENT_KEYS = "different_top_level_keys"
I_UNREADABLE = "not_readable_as_json"
I_NOT_JSON = "not_json"
IMPACT_VOCAB = (I_SAME_KEYS, I_DIFFERENT_KEYS, I_UNREADABLE, I_NOT_JSON)

V_NO_SHADOW = ("no_face_the_suite_opens_has_a_foreign_copy_of_its_basename_in_a_directory_"
               "a_reader_could_start_from")
V_SHADOW_PINNED = ("foreign_copies_exist_but_every_name_is_read_with_a_directory_component")
V_SHADOW_BARE = ("at_least_one_face_read_by_a_bare_literal_basename_also_has_a_foreign_"
                 "copy_in_a_directory_a_reader_could_start_from")
VERDICT_VOCAB = (V_NO_SHADOW, V_SHADOW_PINNED, V_SHADOW_BARE)

COMPARE = ("study", "evidence_cutoff", "summary", "rows", "candidate_dirs", "verdict",
           "verdict_reason", "method_limits", "population_keys")

# Counts over a growing corpus: every results directory that gains a *latest.json pointer adds a
# candidate, so these move on an honest rebuild.  Declared here AND in the face, so a leg cannot
# widen the gate (E420/E421 law -- a count in an equality gate is unsatisfiable).
POPULATION_KEYS = (
    # r1476: the population, and its literal/templated split, are corpus counts too -- one new
    # results pointer moved 232->233 and 218->219 and re-red the leg for growth alone.  What a
    # reader acts on (bare-literal exposure = 0) is a reading and is still compared exactly.
    "faces",
    "faces_literal",
    "faces_templated",
    "faces_on_disk",
    "faces_with_a_foreign_copy",
    "faces_with_a_different_document_copy",
    "different_document_copies_on_a_generic_basename",
    "different_document_copies_on_a_specific_basename",
)


# ------------------------------------------------------------------ io
def _rel(path: str, root: str = ROOT) -> str:
    try:
        return os.path.relpath(path, root).replace("\\", "/")
    except ValueError:
        return path.replace("\\", "/")


def _under(path: str, root: str) -> bool:
    try:
        a = os.path.normcase(os.path.abspath(path))
        b = os.path.normcase(os.path.abspath(root))
        return a == b or a.startswith(b + os.sep)
    except (OSError, ValueError):
        return False


def _sha(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def write_face(face: dict, outdir: str | None = None) -> str:
    outdir = outdir or OUT_DIR
    os.makedirs(outdir, exist_ok=True)
    text = json.dumps(face, ensure_ascii=False, indent=1) + "\n"
    for name in (FACE % face["evidence_cutoff"], LATEST):
        with open(os.path.join(outdir, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
    return os.path.join(outdir, FACE % face["evidence_cutoff"])


# ------------------------------------------------------------------ 1. population
def load_population(root: str = ROOT) -> tuple:
    """The faces E411 priced, machine-read from its newest published face."""
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
            faces.append({"face": name, "on_disk_at_publish": bool(row.get("on_disk"))})
    return faces, _rel(path, root)


def is_templated(name: str) -> bool:
    return "%" in name or "*" in name


# ------------------------------------------------------------------ 2. candidate directories
def _walk_latest_dirs(root: str) -> list:
    dirs = []
    for base, subdirs, files in os.walk(root):
        subdirs[:] = [s for s in subdirs if s not in SKIP_DIRNAMES]
        if any(f.endswith("latest.json") for f in files):
            dirs.append(base)
    return dirs


def candidate_dirs(root: str = ROOT) -> list:
    rows = []

    def add(label, path):
        rows.append({"label": label, "path": path, "exists": os.path.isdir(path)})

    add("repo_root", root)
    add("cli_home", CLI_HOME)
    add("cli_memory", os.path.join(CLI_HOME, "memory"))
    add("fleet_root", FLEET_ROOT)
    add("group_repo", os.path.join(FLEET_ROOT, "FluxGroup"))
    if os.path.isdir(FLEET_ROOT):
        for name in sorted(os.listdir(FLEET_ROOT)):
            p = os.path.join(FLEET_ROOT, name)
            if os.path.isdir(p) and name != "FluxGroup":
                add("fleet_sibling:" + name, p)
    for d in _walk_latest_dirs(root):
        add("holds_a_latest_pointer", d)
    seen, out = set(), []
    for r in rows:
        key = os.path.normcase(os.path.abspath(r["path"]))
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


def index_basenames(dirs: list) -> dict:
    """basename -> [(dir_label, dir_path, file_path)] for one directory level each."""
    idx = {}
    for d in dirs:
        if not d["exists"]:
            continue
        try:
            entries = os.listdir(d["path"])
        except OSError:
            continue
        for name in entries:
            p = os.path.join(d["path"], name)
            if os.path.isfile(p):
                idx.setdefault(name, []).append((d["label"], d["path"], p))
    return idx


# ------------------------------------------------------------------ 3. impact
def json_impact(own: str, foreign: str) -> str:
    """How the two documents differ, in the terms a reader would notice."""
    if not own.endswith(".json") or not foreign.endswith(".json"):
        return I_NOT_JSON
    try:
        if os.path.getsize(own) > 4 * 1024 * 1024 or os.path.getsize(foreign) > 4 * 1024 * 1024:
            return I_UNREADABLE
        a = json.load(open(own, encoding="utf-8"))
        b = json.load(open(foreign, encoding="utf-8"))
    except (OSError, ValueError, UnicodeDecodeError):
        return I_UNREADABLE
    if not isinstance(a, dict) or not isinstance(b, dict):
        return I_SAME_KEYS if type(a) is type(b) else I_DIFFERENT_KEYS
    return I_SAME_KEYS if set(a) == set(b) else I_DIFFERENT_KEYS


# ------------------------------------------------------------------ 4. bare read sites
READ_CALLS = ("open", "load", "read_text", "read_bytes", "read_csv", "read_parquet")
MODE_ARGS = {"r", "rb", "rt", "w", "a", "r+", "w+", "a+"}


def bare_literal_sites(root: str = ROOT) -> dict:
    """basename -> [line] for bare literal basenames PASSED TO A READ CALL in smoke_test.py.

    A bare string constant is not a read.  ``"latest.json"`` appears in suffix tests and
    glob patterns many times for every one place that opens it, so the join has to look at
    the call: first positional argument (or ``path=``) of open/load/read_* with no directory
    component.  E415's site scan is the same shape; here the unit is the name, not the site.
    """
    p = os.path.join(root, "smoke_test.py")
    out = {}
    if not os.path.exists(p):
        return out
    tree = ast.parse(open(p, encoding="utf-8").read())
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        name = fn.id if isinstance(fn, ast.Name) else getattr(fn, "attr", None)
        if name not in READ_CALLS:
            continue
        args = list(node.args)
        if not args:
            for kw in node.keywords:
                if kw.arg == "path":
                    args = [kw.value]
                    break
        if not args:
            continue
        arg = args[0]
        if not isinstance(arg, ast.Constant) or not isinstance(arg.value, str):
            continue
        v = arg.value
        if not v or "/" in v or "\\" in v or "." not in v:
            continue
        out.setdefault(v, []).append(node.lineno)
    return out


# ------------------------------------------------------------------ build
def build(root: str = ROOT, now: datetime | None = None, write: bool = True) -> dict:
    now = now or datetime.now(timezone.utc).astimezone()
    cutoff = now.date().isoformat()
    pop, pop_source = load_population(root)
    dirs = candidate_dirs(root)
    idx = index_basenames(dirs)
    bare = bare_literal_sites(root)

    rows, templated = [], []
    for item in pop:
        name = item["face"]
        base = os.path.basename(name)
        if is_templated(name):
            templated.append(name)
            continue
        own = os.path.join(root, name.replace("/", os.sep))
        on_disk = os.path.isfile(own)
        own_sha = _sha(own) if on_disk else None
        shadows = []
        for label, dpath, fpath in idx.get(base, []):
            if os.path.normcase(os.path.abspath(fpath)) == os.path.normcase(os.path.abspath(own)):
                continue
            fsha = _sha(fpath)
            if fsha == own_sha:
                shadows.append({"label": label, "dir": _rel(dpath, root), "path": _rel(fpath, root),
                                "outside_repo": not _under(fpath, root),
                                "class": C_SAME_BYTES, "impact": None, "sha": fsha})
            else:
                shadows.append({"label": label, "dir": _rel(dpath, root), "path": _rel(fpath, root),
                                "outside_repo": not _under(fpath, root),
                                "class": C_DIFFERENT,
                                "impact": json_impact(own, fpath) if on_disk else I_UNREADABLE,
                                "sha": fsha})
        if not shadows:
            klass = C_UNIQUE
        elif any(s["class"] == C_DIFFERENT for s in shadows):
            klass = C_DIFFERENT
        else:
            klass = C_SAME_BYTES
        rows.append({
            "face": name,
            "on_disk": on_disk,
            "own_sha": own_sha,
            "class": klass,
            "shadows": shadows,
            "shadow_count": len(shadows),
            "different_document_copies": sum(1 for s in shadows if s["class"] == C_DIFFERENT),
            "bare_literal_site_lines": bare.get(base, []),
            "read_as_a_bare_literal": bool(bare.get(base)),
        })

    # A basename several faces share is a generic name (this tree has five faces called
    # latest.json); its "foreign copies" are the other faces, not a duplicate.  Measured
    # from the population, never from a word list.
    base_counts = {}
    for r in rows:
        b = os.path.basename(r["face"])
        base_counts[b] = base_counts.get(b, 0) + 1
    for r in rows:
        b = os.path.basename(r["face"])
        r["basename_faces_in_population"] = base_counts[b]
        r["generic_basename"] = base_counts[b] > 1

    by_class = {}
    by_impact = {}
    for r in rows:
        by_class[r["class"]] = by_class.get(r["class"], 0) + 1
        for s in r["shadows"]:
            if s["class"] == C_DIFFERENT:
                by_impact[s["impact"]] = by_impact.get(s["impact"], 0) + 1

    exposed = [r for r in rows if r["class"] == C_DIFFERENT]
    bare_exposed = [r for r in exposed if r["read_as_a_bare_literal"]]

    if not exposed:
        verdict = V_NO_SHADOW
    elif bare_exposed:
        verdict = V_SHADOW_BARE
    else:
        verdict = V_SHADOW_PINNED

    generic_exposed = [r for r in exposed if r["generic_basename"]]
    specific_exposed = [r for r in exposed if not r["generic_basename"]]
    reason = (
        "%d of %d literal faces have at least one same-named copy with different bytes in a "
        "directory a reader could be launched from; %d of those are a generic basename shared by "
        "several faces (latest.json) and %d use a name only one face carries; %d of the exposed "
        "names is read by a bare literal in smoke_test.py, so %d would land on a different document."
        % (len(exposed), len(rows), len(generic_exposed), len(specific_exposed),
           sum(1 for r in exposed if r["read_as_a_bare_literal"]), len(bare_exposed))
    )

    face = {
        "study": STUDY,
        "card": "E417-WHICH-READER-WOULD-FIND-A-FOREIGN-COPY-OF-ITS-FACE",
        "title": "same-named foreign copies of the faces the suite opens, priced by launch directory",
        "evidence_cutoff": cutoff,
        "generated": now.isoformat(timespec="seconds"),
        "population_source": pop_source,
        "verdict": verdict,
        "verdict_reason": reason,
        "summary": {
            "faces": len(pop),
            "faces_literal": len(rows),
            "faces_templated": len(templated),
            "faces_on_disk": sum(1 for r in rows if r["on_disk"]),
            "faces_with_a_foreign_copy": sum(1 for r in rows if r["shadow_count"]),
            "faces_with_a_different_document_copy": len(exposed),
            "faces_read_as_a_bare_literal": sum(1 for r in rows if r["read_as_a_bare_literal"]),
            "bare_literal_faces_that_would_read_a_foreign_document": len(bare_exposed),
            "different_document_copies_on_a_generic_basename": len(generic_exposed),
            "different_document_copies_on_a_specific_basename": len(specific_exposed),
        },
        "by_class": by_class,
        "by_impact": by_impact,
        "population_keys": list(POPULATION_KEYS),
        "candidate_dirs": dirs,
        "rows": rows,
        "templated_faces": templated,
        "method_limits": [
            "one directory level per candidate dir: a bare read of the basename can only land on a "
            "file directly inside the launch directory, so deeper copies are not shadows for this shape.",
            "the CLI home and the fleet siblings are read from this host's layout; a path that does "
            "not exist is published with exists=false and contributes nothing.",
            "the impact class compares top-level key sets only, never values: same_top_level_keys "
            "means the reader would meet a document of the same shape, not the same numbers.",
            "the bare-literal join reads smoke_test.py string constants equal to the basename; a "
            "reader that builds the name from a variable is invisible to it.",
            "templated faces (%s/*) are excluded from the shadow test and listed separately: a "
            "template has no single basename to shadow.",
            "this study excludes its own artefact names from the candidate index by pointing the "
            "shadow test at E411's population, which predates SHADOWFACE-*.",
            "own_sha is a snapshot of the bytes compared at generation time: producers rewrite their "
            "faces every round, so verify re-derives the classification and the shadow paths but "
            "never equality-gates a stored sha (E420 family -- a number that moves on an honest "
            "rebuild cannot be a gate).",
        ],
    }
    face["_path"] = write_face(face) if write else None
    return face


# ------------------------------------------------------------------ verify
def _comparable(payload: dict) -> dict:
    out = {}
    for k in COMPARE:
        v = payload.get(k)
        if k == "rows" and isinstance(v, list):
            # own_sha is published as evidence of WHAT was compared, not as a reading: every
            # producer in this tree rewrites its faces each round, so a stored sha would red the
            # study whenever an unrelated leg ran (E420 family).  The comparison keeps the
            # classification, which DOES move when a copy's bytes converge on the face's.
            v = [{kk: r.get(kk) for kk in ("face", "on_disk", "class",
                                           "shadow_count", "different_document_copies",
                                           "read_as_a_bare_literal", "generic_basename",
                                           "basename_faces_in_population")}
                 for r in v]
        if k == "candidate_dirs" and isinstance(v, list):
            v = [{kk: d.get(kk) for kk in ("label", "exists")} for d in v]
        out[k] = v
    return out


def verify(root: str = ROOT) -> list:
    p = os.path.join(root, "results", "state_tilt", LATEST)
    if not os.path.exists(p):
        return ["no published face at results/state_tilt/%s" % LATEST]
    stored = json.load(open(p, encoding="utf-8"))
    fresh = build(root=root, write=False)
    problems = []
    a, b = _comparable(stored), _comparable(fresh)
    for k in COMPARE:
        if a.get(k) != b.get(k):
            problems.append("%s does not re-derive" % k)
    if stored.get("verdict") not in VERDICT_VOCAB:
        problems.append("stored verdict is outside the vocabulary")
    if fresh.get("verdict") not in VERDICT_VOCAB:
        problems.append("live verdict is outside the vocabulary")
    s = fresh["summary"]
    if sum((fresh.get("by_class") or {}).values()) != s["faces_literal"]:
        problems.append("by_class does not re-add to the literal face count")
    if s["faces_literal"] + s["faces_templated"] != s["faces"]:
        problems.append("literal and templated faces do not re-add to the population")
    exposed = sum(1 for r in fresh["rows"] if r["class"] == C_DIFFERENT)
    if s["faces_with_a_different_document_copy"] != exposed:
        problems.append("the different-document count and its class disagree")
    if (s["different_document_copies_on_a_generic_basename"]
            + s["different_document_copies_on_a_specific_basename"]) != exposed:
        problems.append("the generic/specific split does not re-add to the exposed count")
    for r in fresh["rows"]:
        if r["generic_basename"] != (r["basename_faces_in_population"] > 1):
            problems.append("a row calls a shared basename generic without it being shared")
            break
        if r["basename_faces_in_population"] < 1:
            problems.append("a row carries a basename population of zero")
            break
    bare = sum(1 for r in fresh["rows"] if r["class"] == C_DIFFERENT and r["read_as_a_bare_literal"])
    if s["bare_literal_faces_that_would_read_a_foreign_document"] != bare:
        problems.append("the bare-literal exposure count does not re-derive from rows")
    if fresh["verdict"] == V_NO_SHADOW and exposed:
        problems.append("published as no-shadow while a face has a different-document copy")
    if fresh["verdict"] == V_SHADOW_BARE and not bare:
        problems.append("published as bare-literal exposure with no such row")
    for r in fresh["rows"]:
        if r["class"] not in CLASS_VOCAB:
            problems.append("a row class is outside the vocabulary")
            break
        if r["class"] == C_UNIQUE and r["shadow_count"]:
            problems.append("a unique row carries shadows")
            break
        for sh in r["shadows"]:
            if sh["class"] == C_DIFFERENT and sh["impact"] not in IMPACT_VOCAB:
                problems.append("a shadow impact is outside the vocabulary")
                break
    return problems


# ------------------------------------------------------------------ selftest
def selftest() -> int:
    import tempfile
    fails = []

    def leg(name, cond):
        if not cond:
            fails.append(name)

    tmp = tempfile.mkdtemp(prefix="e417_")
    try:
        a = os.path.join(tmp, "a")
        b = os.path.join(tmp, "b")
        os.makedirs(a)
        os.makedirs(b)
        doc = {"x": 1, "y": 2}
        other = {"x": 1}
        open(os.path.join(a, "face.json"), "w", encoding="utf-8").write(json.dumps(doc))
        open(os.path.join(b, "face.json"), "w", encoding="utf-8").write(json.dumps(other))
        open(os.path.join(b, "twin.json"), "w", encoding="utf-8").write(json.dumps(doc))
        leg("json_impact different keys", json_impact(os.path.join(a, "face.json"),
                                                      os.path.join(b, "face.json")) == I_DIFFERENT_KEYS)
        leg("json_impact same bytes is same keys", json_impact(os.path.join(a, "face.json"),
                                                               os.path.join(b, "twin.json")) == I_SAME_KEYS)
        bad = os.path.join(b, "bad.json")
        open(bad, "w", encoding="utf-8").write("{not json")
        leg("json_impact unreadable", json_impact(os.path.join(a, "face.json"), bad) == I_UNREADABLE)
        md = os.path.join(b, "note.md")
        open(md, "w", encoding="utf-8").write("x")
        leg("json_impact non-json", json_impact(os.path.join(a, "face.json"), md) == I_NOT_JSON)
        leg("templated faces are templated", is_templated("results/%s_latest.json") and
            is_templated("results/PROFILE-*.json") and not is_templated("results/x.json"))
        idx = index_basenames([{"label": "a", "path": a, "exists": True},
                               {"label": "b", "path": b, "exists": True}])
        leg("index finds both copies", len(idx.get("face.json") or []) == 2)
        leg("index keeps one level", "twin.json" in idx)
        # verdict is a function of the rows, not of the prose
        def verdict_of(exposed, bare_exp):
            if not exposed:
                return V_NO_SHADOW
            return V_SHADOW_BARE if bare_exp else V_SHADOW_PINNED
        leg("verdict no shadow", verdict_of(0, 0) == V_NO_SHADOW)
        leg("verdict pinned", verdict_of(2, 0) == V_SHADOW_PINNED)
        leg("verdict bare", verdict_of(2, 1) == V_SHADOW_BARE)
        leg("all classes in vocabulary", set(CLASS_VOCAB) == {C_UNIQUE, C_SAME_BYTES, C_DIFFERENT})
        counts = {}
        for nm in ("a/latest.json", "b/latest.json", "c/only.json"):
            nb = os.path.basename(nm)
            counts[nb] = counts.get(nb, 0) + 1
        leg("a shared basename is generic and a lone one is not",
            counts["latest.json"] > 1 and counts["only.json"] == 1)
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)

    total = 13
    if fails:
        print("selftest FAIL %d/%d: %s" % (total - len(fails), total, "; ".join(fails)))
        return 1
    print("selftest PASS %d/%d" % (total, total))
    return 0


def main(argv: list) -> int:
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "run":
        face = build()
        print(json.dumps({"evidence_cutoff": face["evidence_cutoff"], "verdict": face["verdict"],
                          "summary": face["summary"]}, ensure_ascii=False, indent=1))
        print("written:", face.get("_path"))
        for r in face["rows"]:
            if r["class"] == C_DIFFERENT:
                print("  %-52s copies=%d bare=%s" %
                      (r["face"], r["different_document_copies"], r["read_as_a_bare_literal"]))
        return 0
    if cmd == "verify":
        problems = verify()
        print(json.dumps({"problems": problems}, ensure_ascii=False))
        return 0 if not problems else 1
    if cmd == "selftest":
        return selftest()
    print("usage: e417_shadow_face.py run|verify|selftest", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))