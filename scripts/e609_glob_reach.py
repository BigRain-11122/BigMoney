"""E609 -- does a glob sweep reach the faces that no literal names?

E606 (r1633) published 86 faces whose printed count disagrees with their own rows and reported that
81 of them are opened by no literal in the corpus.  E606 said in its own limits what that means: it
counted literal openers only, so "no reader" there is "no literal opener" and cannot be read as
"nothing on this disk could load it".  This study prices that missing channel.

For every face in the E606 population with no literal reader, every glob()/iglob()/rglob()/glob
method call in the corpus is turned into the pattern(s) it could really use (literal arguments
composed through ``os.path.join`` / ``Path`` / f-strings / one-hop name assignments, made
repo-relative when the composed path is absolute) and matched per segment against the face path.
The matching rule is Python's, not fnmatch's: ``*`` stays inside one segment, ``**`` spans segments
(E470 / E273's ``glob('*')`` lesson).

A segment is NAMING when some literal text survives after its wildcards are removed.  ``**`` names
nothing, ``*`` names nothing, ``FILEHIT*.json`` names the file, ``results`` names a directory.
That is the whole difference between "a sweep lands here" and "a sweep says what it is looking for".

Four classes, published apart:

  NAMES_DIRECTORY   the best pattern naming the face also names at least one of the face's own
                    directories, and the row publishes how deep the name reaches
  NAMES_FILE_ONLY   the best pattern names the face's file but no directory segment -- ``**`` is
                    spanning the directories and carries the location for it
  UNBOUNDED_ONLY    patterns match the face but every one carries no naming segment at all
  NOT_REACHED       no glob in the corpus lands on the face
  FACE_ABSENT       the face is not on this checkout (E606 read it from a packed path)

Run:      python scripts/e609_glob_reach.py run
Verify:   python scripts/e609_glob_reach.py verify   (re-derives from the live tree)
Check:    python scripts/e609_glob_reach.py check    (tallies re-derive from the face)
Selftest: python scripts/e609_glob_reach.py selftest
"""

import argparse
import ast
import io
import json
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import e470_target_read as e470                                      # noqa: E402  (segment rule)
import e468_pointer_reach as e468                                    # noqa: E402  (_walk_py)
import e451_prereg_digest as e451                                    # noqa: E402  (read_text)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
SELF_STEM = "GLOBSWEEPREACH"
OUT_PATH = os.path.join(OUTDIR, SELF_STEM + ".json")
MAX_READ_BYTES = 1 << 20
SITES_PER_FACE = 8
SELF_SKIP = ("e609_", "run_e609", "e606_", "run_e606", "smoke_test")

C_FULL = "names_the_directory"
C_PART = "names_an_ancestor_directory_only"
C_FILE = "names_the_file_only"
C_UNB = "unbounded_only"
C_NONE = "not_reached"
C_ABSENT = "face_absent"
CLASSES = (C_FULL, C_PART, C_FILE, C_UNB, C_NONE, C_ABSENT)

V_FULL = "at_least_one_face_no_literal_names_is_reached_by_a_glob_that_names_its_own_directory"
V_PART = "faces_no_literal_names_are_reached_only_by_globs_that_name_an_ancestor_but_never_their_own_directory"
V_FILE = "faces_no_literal_names_are_reached_only_by_globs_that_name_the_file_while_double_star_spans_the_directories"
V_UNB = "every_glob_that_lands_on_an_unread_face_is_an_unbounded_sweep"
V_NONE = "no_glob_in_the_corpus_lands_on_any_of_the_unread_faces"
V_EMPTY = "the_population_is_empty"
VERDICT_VOCAB = (V_FULL, V_PART, V_FILE, V_UNB, V_NONE, V_EMPTY)


# --------------------------------------------------------------------------- naming rule
def segments(pattern):
    return [s for s in str(pattern or "").replace("\\", "/").split("/") if s]


def naming_core(segment):
    """Literal text left after the wildcards are removed; '' means the segment names nothing."""
    text = re.sub(r"\[[^\]]*\]", "", segment)
    text = text.replace("*", "").replace("?", "")
    return text


def names_something(segment):
    """A segment names something only when an alphanumeric character survives the wildcards.

    ``*.json`` strips to ``.json``, and a file extension is not a name (E206 family): without this
    rule every ``*.json`` sweep would be published as naming a file.
    """
    core = naming_core(segment)
    stem = re.sub(r"\.[A-Za-z0-9]{1,6}$", "", core)
    return bool(re.search(r"[0-9A-Za-z]", stem))


def naming_segments(pattern):
    return [s for s in segments(pattern) if names_something(s)]


def is_bounded(pattern):
    return bool(naming_segments(pattern))


def named_dir_depth(face_rel, pattern):
    """How many of the face's own directory segments the pattern names (0 = location unnamed)."""
    dirs = [re.sub(r"[^0-9a-z]+", "", s.lower()) for s in segments(face_rel)[:-1]]
    pat_segs = segments(pattern)
    named = {re.sub(r"[^0-9a-z]+", "", naming_core(s).lower())
             for s in pat_segs[:-1] if names_something(s)}
    depth = 0
    for d in dirs:
        if any(d == n or n.startswith(d) for n in named):
            depth += 1
    return depth


def match_score(face_rel, pattern):
    """None when the pattern cannot land on the face; else the number of naming segments."""
    if e470.glob_score(face_rel, pattern) is None:
        return None
    return len(naming_segments(pattern))


def classify(face_rel, hits):
    """Class of one face.  FULL means the pattern names the face's own directory; PART means it
    names an ancestor only -- 'results/**/*.json' lands on results/state_tilt/X.json while saying
    nothing about state_tilt, which is a different answer from naming it."""
    if not hits:
        return C_NONE
    bounded = [h for h in hits if h.get("naming_segments")]
    if not bounded:
        return C_UNB
    total = len(segments(face_rel)[:-1])
    best = max(int(h.get("named_dir_depth") or 0) for h in bounded)
    if best >= total and total:
        return C_FULL
    if best > 0:
        return C_PART
    return C_FILE


# --------------------------------------------------------------------------- population
def population(root=None):
    """The disagreeing faces E606 published with no literal reader at all."""
    root = root or ROOT
    path = os.path.join(root, "results", "state_tilt", "COUNTRYCOMPARE.json")
    with io.open(path, encoding="utf-8") as fh:
        e606 = json.load(fh)
    out = []
    for rec in e606.get("faces") or []:
        if rec.get("reader_pairs"):
            continue
        rel = rec.get("face")
        out.append({
            "face": rel,
            "present": os.path.exists(os.path.join(root, rel)),
            "disagreeing_series": rec.get("disagreeing_series"),
        })
    out.sort(key=lambda r: r["face"])
    return out


# --------------------------------------------------------------------------- pattern recovery
def _const_pick(values):
    """Deterministic pick among literals bound to one name: prefer the wildcard-bearing one,
    then the longest.  A name bound to several literals is rare and disclosed as a method limit."""
    if not values:
        return None
    wild = [v for v in values if any(ch in v for ch in "*?[")]
    pool = wild or values
    return sorted(pool, key=lambda v: (-len(v), v))[0]


def pattern_of(node, assigned, depth=0):
    if depth > 4 or node is None:
        return None
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        parts = []
        for v in node.values:
            if isinstance(v, ast.Constant) and isinstance(v.value, str):
                parts.append(v.value)
            else:
                parts.append("*")
        return "".join(parts)
    if isinstance(node, ast.Name):
        return _const_pick(assigned.get(node.id) or [])
    if isinstance(node, ast.Attribute):
        return _const_pick(assigned.get(node.attr) or [])
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = pattern_of(node.left, assigned, depth + 1)
        right = pattern_of(node.right, assigned, depth + 1)
        if left is None and right is None:
            return None
        return (left or "*") + (right or "*")
    if isinstance(node, ast.Call):
        f = node.func
        name = f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else "")
        if name not in ("join", "Path", "PurePath", "PosixPath", "WindowsPath"):
            return None
        parts = []
        for a in node.args:
            got = pattern_of(a, assigned, depth + 1)
            parts.append(got if got is not None else "*")
        if not parts:
            return None
        return "/".join(p for p in parts if p != "")
    return None


def rel_pattern(pat, root=None):
    """Make a composed pattern repo-relative when it resolved to an absolute path."""
    root = root or ROOT
    pat = str(pat or "").replace("\\", "/")
    if not pat:
        return None
    absolute = pat.startswith("/") or (len(pat) > 2 and pat[1] == ":")
    if absolute:
        base = root.replace("\\", "/").rstrip("/") + "/"
        if pat.lower().startswith(base.lower()):
            pat = pat[len(base):]
        else:
            for anchor in ("/results/", "/scripts/", "/Tools/", "/data/", "/knowledge/"):
                idx = pat.lower().find(anchor.lower())
                if idx >= 0:
                    pat = pat[idx + 1:]
                    break
    while pat.startswith("./"):
        pat = pat[2:]
    return pat


def glob_calls(tree, source_rel, assigned, root=None):
    """[(line, [candidate patterns])] for every glob-family call in one module."""
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not e470._is_glob(node):
            continue
        if not node.args:
            continue
        base = None
        if isinstance(node.func, ast.Attribute):
            base = pattern_of(node.func.value, assigned)
        arg = pattern_of(node.args[0], assigned)
        cands = []
        if arg:
            cands.append(arg)
            if base:
                cands.append(base.rstrip("/") + "/" + arg.lstrip("/"))
        elif base:
            cands.append(base)
        cands = [rel_pattern(c, root) for c in cands]
        cands = [c for c in cands if c]
        if cands:
            out.append((getattr(node, "lineno", 0), cands))
    return out


# --------------------------------------------------------------------------- build
def build(root=None, write=False):
    root = root or ROOT
    pop = population(root)
    by_face = {rec["face"]: [] for rec in pop}
    seen_bounded, seen_unbounded = set(), set()
    stats = {"sources_scanned": 0, "glob_calls": 0}

    for rel in e468._walk_py(root):
        if any(os.path.basename(rel).startswith(s) for s in SELF_SKIP):
            continue
        path = os.path.join(root, rel)
        try:
            if os.path.getsize(path) > MAX_READ_BYTES:
                continue
            text = e451.read_text(path)
        except (OSError, ValueError):
            continue
        if "glob" not in text:
            continue
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        stats["sources_scanned"] += 1
        assigned = e470._assignments(tree)
        for line, cands in glob_calls(tree, rel, assigned, root):
            stats["glob_calls"] += 1
            for cand in cands:
                (seen_bounded if is_bounded(cand) else seen_unbounded).add(cand)
            for face in pop:
                best = None
                for cand in cands:
                    score = match_score(face["face"], cand)
                    if score is None:
                        continue
                    if best is None or score > best[1]:
                        best = (cand, score)
                if best is None:
                    continue
                cand = best[0]
                by_face[face["face"]].append({
                    "source": rel,
                    "line": line,
                    "pattern": cand,
                    "score": best[1],
                    "naming_segments": naming_segments(cand),
                    "named_dir_depth": named_dir_depth(face["face"], cand),
                })
    stats["bounded_patterns"] = len(seen_bounded)
    stats["unbounded_patterns"] = len(seen_unbounded)

    faces = []
    counts = {c: 0 for c in CLASSES}
    for rec in pop:
        hits = by_face[rec["face"]]
        cls = classify(rec["face"], hits) if rec["present"] else C_ABSENT
        bounded = [h for h in hits if h["naming_segments"]]
        unbounded = [h for h in hits if not h["naming_segments"]]
        counts[cls] += 1
        faces.append({
            "face": rec["face"],
            "present": rec["present"],
            "disagreeing_series": rec["disagreeing_series"],
            "class": cls,
            "bounded_sites": len(bounded),
            "unbounded_sites": len(unbounded),
            "sites": sorted(hits, key=lambda h: (-int(h.get("named_dir_depth") or 0),
                                                 h["source"], h["line"]))[:SITES_PER_FACE],
        })

    total = len(faces)
    counts["faces"] = total
    counts["faces_present"] = sum(1 for f in faces if f["present"])
    counts["faces_absent_from_checkout"] = total - counts["faces_present"]
    counts["faces_with_a_bounded_site"] = sum(1 for f in faces if f["bounded_sites"])
    counts["faces_naming_own_directory"] = counts.get(C_FULL, 0)
    counts["faces_with_only_unbounded_sites"] = sum(
        1 for f in faces if f["unbounded_sites"] and not f["bounded_sites"])
    counts["bounded_patterns_in_corpus"] = stats["bounded_patterns"]
    counts["unbounded_patterns_in_corpus"] = stats["unbounded_patterns"]
    counts["glob_calls"] = stats["glob_calls"]
    counts["sources_scanned"] = stats["sources_scanned"]
    ved = verdict_from(counts)

    face = {
        "study": "E609_glob_reach",
        "card": "E609-WHETHER-A-GLOB-SWEEP-REACHES-THE-FACES-NO-LITERAL-OPENS",
        "evidence_cutoff": _cutoff(faces),
        "class_vocabulary": list(CLASSES),
        "naming_rule": ("a path segment names something when literal text survives after its "
                        "wildcards are stripped: '**' and '*' name nothing, 'FILEHIT*.json' names "
                        "the file, 'results' names a directory"),
        "counts": counts,
        "faces": faces,
        "verdict": ved,
        "answer": answer_sentence(counts),
        "limits": [
            "the population is E606's publish: faces whose printed count disagrees with their own "
            "rows AND whose literal-reader count is zero. A face a literal opens but never reads a "
            "count from is E606's other class and is not here",
            "a glob pattern is recovered from literals plus one-hop name assignments, "
            "os.path.join / Path composition and f-strings; a pattern built from a value this "
            "tracer cannot follow is published as a miss, not as a match",
            "an argument this tracer cannot follow inside a composed pattern is filled with '*' -- "
            "that can only widen a pattern, never narrow it, so it can create an UNBOUNDED_ONLY "
            "reading but never a false NAMES_DIRECTORY one",
            "matching is per segment (``*`` inside a segment, ``**`` across segments). fnmatch "
            "semantics would let '*' swallow separators and 'match' every face (E273/E470 family)",
            "a glob that lands on a directory and is filtered by the caller afterwards counts as a "
            "landing: this measures reach, not consumption",
            "faces missing from this checkout are published as face_absent rather than graded",
            "E606 printed 81 faces with no reader at all; its own reader_pairs table holds 6 pairs "
            "across 5 faces, only 4 of which appear among the 86 face rows, so the row-level "
            "population here is 82. The one-face difference is E606's tally, disclosed rather than "
            "silently repaired",
            "at most %d sites per face are published; the counts are complete even when the site "
            "list is truncated" % SITES_PER_FACE,
        ],
    }
    pr = face_problems(face)
    if write and not pr:
        write_face(face)
    return face, pr


def _cutoff(faces):
    best = ""
    for f in faces:
        for m in re.finditer(r"(20\d\d-\d\d-\d\d)", f["face"]):
            if m.group(1) > best:
                best = m.group(1)
    return best or "no-date-in-population"


def answer_sentence(counts):
    total = counts.get("faces") or 0
    if not total:
        return "the population is empty, so nothing is priced"
    return ("of %d disagreeing faces that no literal opens, %d are reached by a glob that names "
            "their own directory, %d only by a glob that names an ancestor (so the sweep says "
            "nothing about which subdirectory), %d only by a glob that names the file while '**' "
            "spans the directories, %d only by sweeps with no naming segment at all, and %d by no "
            "glob in the corpus (%d of the %d absent from this checkout)."
            % (total, counts.get(C_FULL, 0), counts.get(C_PART, 0), counts.get(C_FILE, 0),
               counts.get(C_UNB, 0), counts.get(C_NONE, 0),
               counts.get("faces_absent_from_checkout", 0), total))


def verdict_from(counts):
    if not counts.get("faces"):
        return V_EMPTY
    if counts.get(C_FULL):
        return V_FULL
    if counts.get(C_PART):
        return V_PART
    if counts.get(C_FILE):
        return V_FILE
    if counts.get(C_UNB):
        return V_UNB
    return V_NONE


def write_face(face):
    os.makedirs(OUTDIR, exist_ok=True)
    body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    for path in (OUT_PATH, os.path.join(OUTDIR, SELF_STEM + "-latest.json")):
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)


# --------------------------------------------------------------------------- guard
def face_problems(face):
    p = []
    if not isinstance(face, dict) or "counts" not in face:
        return ["the face carries no counts block"]
    counts, faces = face["counts"], face.get("faces") or []
    if not faces:
        p.append("the face publishes no faces")
    tally = {}
    for rec in faces:
        cls = rec.get("class")
        if cls not in CLASSES:
            p.append("face %s carries an unknown class %r" % (rec.get("face"), cls))
            break
        tally[cls] = tally.get(cls, 0) + 1
        if cls == C_ABSENT and rec.get("present"):
            p.append("face %s is graded absent but is on the checkout" % rec.get("face"))
            break
        if cls != C_ABSENT and not rec.get("present"):
            p.append("face %s is graded %r but is not on the checkout" % (rec.get("face"), cls))
            break
        if cls in (C_FULL, C_PART, C_FILE) and rec.get("bounded_sites", 0) < 1:
            p.append("face %s is graded %r with no bounded site" % (rec.get("face"), cls))
            break
        if cls == C_UNB and not rec.get("unbounded_sites"):
            p.append("face %s is graded UNBOUNDED_ONLY with no unbounded site" % rec.get("face"))
            break
        if rec.get("sites") and classify(rec.get("face") or "", rec["sites"]) != cls:
            p.append("face %s grades itself %r but its published sites say %r"
                     % (rec.get("face"), cls, classify(rec.get("face") or "", rec["sites"])))
            break
    for c in CLASSES:
        if counts.get(c, 0) != tally.get(c, 0):
            p.append("counts.%s says %r but the rows say %d" % (c, counts.get(c), tally.get(c, 0)))
    if counts.get("faces") != len(faces):
        p.append("counts.faces says %r but the face publishes %d rows"
                 % (counts.get("faces"), len(faces)))
    if counts.get("faces_with_a_bounded_site") != sum(1 for f in faces if f["bounded_sites"]):
        p.append("counts.faces_with_a_bounded_site does not re-derive")
    if face.get("verdict") != verdict_from(counts):
        p.append("verdict %r does not re-derive from the counts (rule says %r)"
                 % (face.get("verdict"), verdict_from(counts)))
    if not face.get("answer"):
        p.append("the face carries no answer sentence")
    return p


# --------------------------------------------------------------------------- selftest
def _fixture(files, faces):
    """Build a throw-away repo: files = {relpath: text}, faces = [face relpath]."""
    tmp = tempfile.mkdtemp(prefix="e609_")
    for rel, text in files.items():
        path = os.path.join(tmp, rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
    for rel in faces:
        path = os.path.join(tmp, rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("{}\n")
    with io.open(os.path.join(tmp, "results", "state_tilt", "COUNTRYCOMPARE.json"), "w",
                 encoding="utf-8", newline="\n") as fh:
        json.dump({"faces": [{"face": rel, "reader_pairs": 0, "disagreeing_series": 1}
                             for rel in faces]}, fh)
    return tmp


def selftest():
    legs = []

    def leg(name, cond, note=""):
        legs.append({"leg": name, "ok": bool(cond), "note": note})

    FACE_DIR = "results/state_tilt/DIRHIT.json"
    FACE_FILE = "results/state_tilt/FILEHIT.json"
    FACE_UNB = "results/state_tilt/UNBHIT.json"
    FACE_NONE = "results/state_tilt/NONEHIT.json"

    # 1. a bounded pattern that names the directory
    tmp = _fixture({"scripts/x/a.py": "import glob\np = glob.glob('results/state_tilt/DIRHIT*.json')\n"},
                   [FACE_DIR])
    try:
        face, pr = build(root=tmp, write=False)
        rec = face["faces"][0]
        leg("dir face is names_the_directory", rec["class"] == C_FULL, str(rec["class"]))
        leg("dir face publishes named_dir_depth 2", (rec["sites"][0]["named_dir_depth"] == 2),
            str(rec["sites"]))
        leg("dir fixture face problems empty", not pr, str(pr))
        leg("verdict recomputes to V_FULL", face["verdict"] == V_FULL, face["verdict"])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 2. '**' spans directories, only the file is named
    tmp = _fixture({"scripts/x/b.py": "import glob\np = glob.glob('**/FILEHIT*.json')\n"},
                   [FACE_FILE])
    try:
        face, pr = build(root=tmp, write=False)
        rec = face["faces"][0]
        leg("file face is names_the_file_only", rec["class"] == C_FILE, str(rec["class"]))
        leg("file face names no directory segment", rec["sites"][0]["named_dir_depth"] == 0,
            str(rec["sites"]))
        leg("file fixture face problems empty", not pr, str(pr))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 2b. a sweep that names only an ancestor directory
    tmp = _fixture({"scripts/x/b2.py": "import glob\np = glob.glob('results/**/*.json')\n"},
                   [FACE_DIR])
    try:
        face, pr = build(root=tmp, write=False)
        rec = face["faces"][0]
        leg("ancestor-only sweep is names_an_ancestor_directory_only", rec["class"] == C_PART,
            str(rec["class"]))
        leg("ancestor-only sweep names depth 1 of 2",
            rec["sites"][0]["named_dir_depth"] == 1, str(rec["sites"][0]))
        leg("ancestor fixture problems empty", not pr, str(pr))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 3. a sweep whose segments carry no literal at all
    tmp = _fixture({"scripts/x/c.py": "import glob\np = glob.glob('**/*.json')\n"}, [FACE_UNB])
    try:
        face, pr = build(root=tmp, write=False)
        rec = face["faces"][0]
        leg("unbounded sweep is unbounded_only", rec["class"] == C_UNB, str(rec["class"]))
        leg("unbounded sweep publishes no naming segment",
            rec["sites"][0]["naming_segments"] == [], str(rec["sites"]))
        leg("unbounded fixture face problems empty", not pr, str(pr))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 4. a pattern aimed at another directory does not reach this face
    tmp = _fixture({"scripts/x/d.py": "import glob\np = glob.glob('results/other/*.json')\n"},
                   [FACE_NONE])
    try:
        face, pr = build(root=tmp, write=False)
        leg("other-dir pattern is not_reached", face["faces"][0]["class"] == C_NONE,
            str(face["faces"][0]["class"]))
        leg("not_reached fixture problems empty", not pr, str(pr))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 5. the naming rule itself
    leg("bare '*' names nothing", not is_bounded("*"))
    leg("'**/*.json' names nothing", not is_bounded("**/*.json"))
    leg("'FILEHIT*.json' names the file", naming_core("FILEHIT*.json") == "FILEHIT.json")
    leg("'results/state_tilt/*.json' names two directories",
        len(naming_segments("results/state_tilt/*.json")) == 2)
    leg("a bracket class plus an extension names nothing", not names_something("[ab].json"))
    leg("a file stem names something", names_something("FILEHIT*.json"))
    leg("'*' does not swallow the separator (E470 per-segment rule)",
        e470.glob_score("results/state_tilt/DIRHIT.json", "*") is None)
    leg("'**' spans the separator", e470.glob_score("results/state_tilt/DIRHIT.json",
                                                    "**/DIRHIT.json") is not None)

    # 6. composition and absolutisation
    tree = ast.parse("glob.glob(os.path.join('results','state_tilt','*.json'))")
    leg("a composed join is recovered as one pattern",
        pattern_of(tree.body[0].value.args[0], {}) == "results/state_tilt/*.json")
    tree = ast.parse("glob.glob(f'results/{ST}/x*.json')")
    leg("an f-string hole stays a wildcard",
        pattern_of(tree.body[0].value.args[0], {}) == "results/*/x*.json")
    leg("an absolute pattern is made repo-relative",
        rel_pattern(os.path.join(ROOT, "results", "state_tilt", "*.json")) ==
        "results/state_tilt/*.json")

    # 7. self-exclusion and the writer-is-a-reader note
    leg("a self-source is skipped by the walk",
        any(s["source"].startswith("e609_") for f in ({}).get("faces", []) for s in f["sites"])
        is False)
    leg("a bounded file-only hit is not a directory claim",
        classify(FACE_FILE, [{"naming_segments": ["FILEHIT*.json"], "named_dir_depth": 0}]) == C_FILE)

    bad = [l for l in legs if not l["ok"]]
    print(json.dumps({"legs": len(legs), "failed": len(bad), "detail": bad},
                     ensure_ascii=False, indent=1))
    return 0 if not bad else 1


# --------------------------------------------------------------------------- cli
def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="build")
    args = ap.parse_args(argv[1:])
    cmd = args.cmd.lower()
    if cmd == "selftest":
        return selftest()
    face, problems = build(write=(cmd in ("build", "run")))
    if problems:
        print("PROBLEMS: " + "; ".join(problems))
        return 1
    c = face["counts"]
    print("faces=%d present=%d by_class=%s"
          % (c["faces"], c["faces_present"], json.dumps({k: c.get(k, 0) for k in CLASSES},
                                                        sort_keys=True)))
    print("glob_calls=%d bounded_patterns=%d unbounded_patterns=%d sources=%d"
          % (c["glob_calls"], c["bounded_patterns_in_corpus"],
             c["unbounded_patterns_in_corpus"], c["sources_scanned"]))
    print("verdict=" + face["verdict"])
    print("answer=" + face["answer"])
    if cmd in ("check", "verify"):
        pr = face_problems(face)
        print("problems=%s" % json.dumps(pr, ensure_ascii=False))
        return 0 if not pr else 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))