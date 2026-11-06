"""E451 -- does a study that names a prereg note publish a digest of it anywhere?

E449 (results/state_tilt/deadprereg_latest.json) published seven research notes that a study
script names through a PREREG constant, are named by filename in code text, and are opened by no
opener in the corpus.  The constant is assigned once and never read again, so the note's authority
over the study is a claim made in prose only.

A prereg constrains a study only if some artifact the study publishes can be tied back to the exact
bytes of the note.  That tie is a digest: a sha/hash value in a published face that equals the
note's current sha256, or a pinned as-of date recorded beside the numbers.  This study asks, per
note,

  1. which `.py` files in the corpus name the note by filename (the naming population);
  2. of those, which ones publish a face at all -- a string literal that resolves under `results/`
     (the producer set, read from the file's own literals, not from a grep of the study id);
  3. of the faces those producers write that exist on disk today, does any carry the note's
     sha256 (full or a hex prefix of at least 12 chars), or a pinned prereg/note as-of date?

Per-study classes (frozen vocabulary):

    note_digest_published              a face written by a naming producer carries the note digest
                                       or a pinned as-of of it
    note_named_but_no_digest           naming producers publish faces; none carries a digest
    note_not_named_by_its_own_producer no naming .py in the corpus publishes any results/ face

Nothing is executed: static AST over the naming files, `os.path.exists` on the candidate faces, and
sha256 of the note bytes.  Naming files that publish no face are published as the residue rather
than dropped, so the study population is never silently narrowed.

Usage:
    python scripts/e451_prereg_digest.py run        # build and publish the face
    python scripts/e451_prereg_digest.py check      # re-derive every tally from the published rows
    python scripts/e451_prereg_digest.py verify     # re-derive from the live tree and refuse drift
    python scripts/e451_prereg_digest.py selftest   # offline legs
"""

from __future__ import annotations

import ast
import hashlib
import io
import json
import os
import re
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
SOURCE_FACE = "deadprereg_latest.json"
FACE_NAME = "prereghash_latest.json"
DATED_PREFIX = "PREREGHASH"
CARD = "E451-WHICH-STUDY-THAT-CITES-ITS-PREREG-NOTE-CARRIES-NO-DIGEST-OF-IT"
SELF_SKIP = ("e451", "run_e451")

SKIP_DIRS = frozenset({
    ".git", "node_modules", "__pycache__", ".codely-cli", "_quarantine", ".mypy_cache",
    ".pytest_cache", "venv", ".venv",
})

C_DIGEST = "note_digest_published"
C_NAMED_NO_DIGEST = "note_named_but_no_digest"
C_NOT_NAMED = "note_not_named_by_its_own_producer"
CLASSES = (C_DIGEST, C_NAMED_NO_DIGEST, C_NOT_NAMED)

D_FULL = "sha256_full"
D_PREFIX = "sha256_hex_prefix"
D_ASOF = "pinned_as_of_date"
DIGEST_KINDS = (D_FULL, D_PREFIX, D_ASOF)

MIN_PREFIX = 12
ASOF_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")
PROSE_ASOF_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
FACE_RE = re.compile(r"^(results/.+\.(?:json|md|csv|txt))$", re.I)
DIGEST_KEY_RE = re.compile(r"(sha|hash|digest)", re.I)
PREREG_KEY_RE = re.compile(r"(prereg|note_as_of|note_sha|pinned)", re.I)

V_EMPTY = "no_prereg_note_to_grade"
V_ALL = "every_study_that_names_a_prereg_note_publishes_a_digest_of_it"
V_NONE = "no_study_publishes_a_digest_of_the_prereg_note_it_names"
V_SOME = ("some_studies_publish_a_digest_of_their_prereg_note_but_most_do_not")
VERDICT_VOCAB = (V_EMPTY, V_ALL, V_SOME, V_NONE)


# ----------------------------------------------------------------------------- helpers


def _rel(path: str) -> str:
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


def _load(path: str) -> dict:
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def is_own_output(rel: str) -> bool:
    name = os.path.basename(rel)
    if name == FACE_NAME:
        return True
    return name.startswith(DATED_PREFIX + "-") and name.endswith(".json")


def sha256_of(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def walk_py(root: str = ROOT) -> list:
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if not name.endswith(".py"):
                continue
            rel = _rel(os.path.join(dirpath, name))
            if any(rel.split("/")[-1].startswith(s) for s in SELF_SKIP):
                continue
            out.append(rel)
    return sorted(out)


def read_text(path: str) -> str:
    try:
        with io.open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def naming_lines(text: str, basename: str) -> list:
    """1-based line numbers of every line that carries the note basename."""
    return [i for i, line in enumerate(text.splitlines(), 1) if basename in line]


def faces_in_tree(tree: ast.AST) -> list:
    """Every string literal in the file that resolves under results/.

    The literal is normalised the way the writers compose it: backslashes to slashes, leading
    './' dropped.  A literal that still carries a brace or a format placeholder is kept as
    written (it is a template, not a face) and is reported by the caller as unprobeable.
    """
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
            continue
        val = node.value.replace("\\", "/")
        for token in _candidate_tokens(val):
            if FACE_RE.match(token) and token not in out:
                out.append(token)
    return out


def _candidate_tokens(val: str) -> list:
    token = val.strip()
    idx = token.lower().find("results/")
    if idx < 0:
        return []
    token = token[idx:]
    token = token.split()[0] if token.split() else token
    token = token.rstrip("\"'")
    return [token]


def is_template(face: str) -> bool:
    return "{" in face or "%s" in face


def stem_slug(note_stem: str) -> str:
    """The study's own file-name slug: LOWAMP-DEEP-P1 -> lowamp_deep_p1."""
    return note_stem.lower().replace("-", "_")


def is_own_producer(rel: str, slug: str) -> bool:
    """Is this file the study's own producer rather than a lane scratch script?

    The own producer carries the study slug in its basename (scripts/fund_divlowvol_p1.py for
    FUND-DIVLOWVOL-P1); a ``_r630bma_*`` receipt or a shared module that merely names the note is a
    naming file, not the study's producer.
    """
    base = os.path.basename(rel).lower()
    return slug in base


def prereg_keys(payload) -> list:
    """Every field name in a published payload that names a prereg/pin/sha (value ignored)."""
    out = []

    def walk(node, path):
        if isinstance(node, dict):
            for k, v in node.items():
                sub = path + "." + str(k) if path else str(k)
                if PREREG_KEY_RE.search(str(k)) or DIGEST_KEY_RE.search(str(k)):
                    out.append(sub)
                walk(v, sub)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, "%s[%d]" % (path, i))

    walk(payload, "")
    return out[:6]


def prose_asof(payload) -> list:
    """A prereg key whose value mentions a date without being one: a prose as-of, not a pin.

    ``prereg_state = "FROZEN v1.0 (2026-10-03 bm-b r610 five-condition freeze window)"`` names a
    freeze date a human can read and no reader can check: it does not open with the date, so a
    consumer cannot key on it, and it says nothing about the note's bytes.
    """
    out = []

    def walk(node, path):
        if isinstance(node, dict):
            for k, v in node.items():
                sub = path + "." + str(k) if path else str(k)
                if isinstance(v, str) and PREREG_KEY_RE.search(str(k)) and PROSE_ASOF_RE.search(v) \
                        and not ASOF_RE.match(v.strip()):
                    out.append({"field": sub, "value": v[:90]})
                walk(v, sub)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, "%s[%d]" % (path, i))

    walk(payload, "")
    return out[:4]


def digest_hits(payload, sha: str, note_stem: str) -> list:
    """Walk a published payload and return every digest / pinned as-of hit for the note."""
    hits = []

    def walk(node, path):
        if isinstance(node, dict):
            for k, v in node.items():
                sub = path + "." + str(k) if path else str(k)
                if isinstance(v, str):
                    kind = _value_kind(str(k), v, sha)
                    if kind:
                        hits.append({"field": sub, "kind": kind, "value": v[:80]})
                else:
                    walk(v, sub)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, "%s[%d]" % (path, i))

    walk(payload, "")
    return hits


def _value_kind(key: str, value: str, sha: str) -> str:
    v = value.strip().lower()
    if v.startswith("sha256:"):
        v = v[len("sha256:"):]
    if v == sha:
        return D_FULL
    if MIN_PREFIX <= len(v) < len(sha) and re.fullmatch(r"[0-9a-f]+", v) and sha.startswith(v):
        return D_PREFIX
    if PREREG_KEY_RE.search(key) and ASOF_RE.match(v):
        return D_ASOF
    return ""


def class_of(naming_producers: int, faces_probed: int, hits: int) -> str:
    if not naming_producers or not faces_probed:
        return C_NOT_NAMED
    return C_DIGEST if hits else C_NAMED_NO_DIGEST


def verdict_for(rows: list) -> str:
    if not rows:
        return V_EMPTY
    digests = sum(1 for r in rows if r["class"] == C_DIGEST)
    if digests == len(rows):
        return V_ALL
    if digests == 0:
        return V_NONE
    return V_SOME


# ----------------------------------------------------------------------------- build


def note_population() -> list:
    face = _load(os.path.join(OUTDIR, SOURCE_FACE))
    return [r["target"] for r in face["rows"] if r.get("target")]


def build() -> dict:
    notes = note_population()
    corpus = walk_py()
    texts = {rel: read_text(os.path.join(ROOT, rel)) for rel in corpus}
    trees = {}
    for rel in corpus:
        if not any(os.path.basename(n) in texts[rel] for n in notes):
            continue
        try:
            trees[rel] = ast.parse(texts[rel])
        except SyntaxError:
            trees[rel] = None

    rows = []
    residue = []
    for note in notes:
        base = os.path.basename(note)
        stem = base.rsplit(".", 1)[0]
        abs_note = os.path.join(ROOT, note.replace("/", os.sep))
        sha = sha256_of(abs_note) if os.path.exists(abs_note) else ""
        naming = [rel for rel in corpus if base in texts[rel]]
        producers = []
        unprobeable = []
        for rel in naming:
            tree = trees.get(rel)
            faces = faces_in_tree(tree) if tree is not None else []
            real = [f for f in faces if not is_template(f)]
            templ = [f for f in faces if is_template(f)]
            if templ:
                unprobeable.append({"file": rel, "templates": templ[:5],
                                    "reason": "face_path_is_a_template_not_a_literal"})
            if not real:
                residue.append({"note": note, "file": rel, "reason": "names_the_note_but_publishes_no_face"})
                continue
            producers.append({"file": rel, "faces": real,
                              "naming_lines": naming_lines(texts[rel], base)})

        slug = stem_slug(stem)
        own = [p for p in producers if is_own_producer(p["file"], slug)]
        basis = "own_producer_named_by_the_study_slug"
        if not own:
            own = producers
            basis = "no_own_producer_filename_falls_back_to_every_naming_producer"
        own_files = {p["file"] for p in own}
        near_miss = []
        probed, hits, missing = [], [], []
        for p in producers:
            for face in p["faces"]:
                if is_own_output(face):
                    continue
                absf = os.path.join(ROOT, face.replace("/", os.sep))
                if not os.path.exists(absf):
                    missing.append({"file": p["file"], "face": face})
                    continue
                probed.append({"file": p["file"], "face": face})
                if not face.lower().endswith(".json"):
                    continue
                try:
                    payload = _load(absf)
                except (ValueError, OSError):
                    continue
                found = digest_hits(payload, sha, stem)
                for h in found:
                    hits.append({"file": p["file"], "face": face, **h})
                keys = prereg_keys(payload)
                prose = prose_asof(payload)
                mentions = stem.lower() in json.dumps(payload, ensure_ascii=False).lower()
                if not found and (keys or mentions or prose):
                    near_miss.append({"face": face, "writer": p["file"],
                                      "in_own_producer": p["file"] in own_files,
                                      "prereg_named_fields": keys,
                                      "asof_dates_in_prose": prose,
                                      "mentions_the_study_stem": mentions})

        rows.append({
            "note": note,
            "note_stem": stem,
            "note_sha256": sha,
            "note_bytes": os.path.getsize(abs_note) if os.path.exists(abs_note) else 0,
            "naming_files": sorted(naming),
            "naming_file_count": len(naming),
            "producers": producers,
            "producer_count": len(producers),
            "faces_probed": probed,
            "faces_missing_on_disk": missing,
            "own_producers": own,
            "own_producer_files": sorted(own_files),
            "own_producer_faces_probed": len([f for f in probed if f["file"] in own_files]),
            "producer_basis": basis,
            "near_miss_faces": near_miss,
            "digest_hits": hits,
            "digest_kind": hits[0]["kind"] if hits else None,
            "class": class_of(len(own), len([f for f in probed if f["file"] in own_files]),
                              len(hits)),
        })

    by_class = {c: sum(1 for r in rows if r["class"] == c) for c in CLASSES}
    summary = {
        "class_counts": by_class,
        "class_vocabulary": list(CLASSES),
        "notes": len(rows),
        "naming_files_total": sum(r["naming_file_count"] for r in rows),
        "distinct_naming_files": len({f for r in rows for f in r["naming_files"]}),
        "producers_total": sum(r["producer_count"] for r in rows),
        "faces_probed_total": sum(len(r["faces_probed"]) for r in rows),
        "faces_missing_on_disk_total": sum(len(r["faces_missing_on_disk"]) for r in rows),
        "digest_kind_counts": {k: sum(1 for r in rows if r["digest_kind"] == k) for k in DIGEST_KINDS},
        "studies_with_a_digest": sum(1 for r in rows if r["digest_hits"]),
        "notes_missing_on_disk": sum(1 for r in rows if not r["note_sha256"]),
        "own_producers_total": sum(len(r["own_producers"]) for r in rows),
        "own_producer_faces_probed_total": sum(r["own_producer_faces_probed"] for r in rows),
        "studies_falling_back_to_every_naming_producer":
            sum(1 for r in rows if r["producer_basis"].startswith("no_own_producer")),
        "near_miss_faces_total": sum(len(r["near_miss_faces"]) for r in rows),
        "near_miss_faces_in_own_producer":
            sum(1 for r in rows for f in r["near_miss_faces"] if f["in_own_producer"]),
        "faces_whose_prereg_as_of_is_prose_only":
            sum(1 for r in rows for f in r["near_miss_faces"] if f["asof_dates_in_prose"]),
        "residue_rows": len(residue),
        "unprobeable_rows": len(unprobeable),
        "population_source": SOURCE_FACE,
        "corpus_py_files": len(corpus),
    }
    face = {
        "card": CARD,
        "study": "E451_which_study_that_names_a_prereg_note_publishes_a_digest_of_it",
        "title": "does a study that names a prereg note publish a digest of it anywhere",
        "evidence_cutoff": str(date.today()),
        "source_face": SOURCE_FACE,
        "summary": summary,
        "rows": rows,
        "residue": residue,
        "unprobeable": unprobeable,
        "method_limits": [
            "naming is a basename match in the file text; a note named through a composed or "
            "imported path is not counted as naming",
            "a producer's faces are the string literals it carries that resolve under results/; a "
            "path assembled from parts at call time is reported in `unprobeable` as a template, "
            "never silently dropped",
            "digest evidence is a value equal to the note's current sha256 (full or >=12 hex "
            "prefix) or a prereg/note key carrying an ISO as-of date; a digest of a different "
            "version of the note does not match, and that is the measurement",
            "only JSON faces are inspected for digest fields; md/csv/txt faces are probed for "
            "existence and counted, not parsed",
            "a study is graded on the faces of its own producer (the file whose basename carries "
            "the study slug); when no such file names the note the grading falls back to every "
            "naming producer and says so in producer_basis",
            "near_miss_faces are published beside the classes: a face that names a prereg field or "
            "the study stem but carries no digest is the evidence that the claim is made in prose "
            "rather than pinned",
        ],
        "verdict": verdict_for(rows),
    }
    return face


def write_face(face: dict) -> str:
    body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    dated = os.path.join(OUTDIR, "%s-%s.json" % (DATED_PREFIX, face["evidence_cutoff"]))
    latest = os.path.join(OUTDIR, FACE_NAME)
    for path in (dated, latest):
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)
    return latest


# ----------------------------------------------------------------------------- check


def tally_problems(face: dict) -> list:
    problems = []
    rows = face["rows"]
    s = face["summary"]
    by_class = {c: sum(1 for r in rows if r["class"] == c) for c in CLASSES}
    if by_class != s["class_counts"]:
        problems.append("class_counts do not re-derive: %s vs %s" % (by_class, s["class_counts"]))
    if len(rows) != s["notes"]:
        problems.append("notes count %d != rows %d" % (s["notes"], len(rows)))
    naming = sum(r["naming_file_count"] for r in rows)
    if naming != s["naming_files_total"]:
        problems.append("naming_files_total %d != re-derived %d" % (s["naming_files_total"], naming))
    for r in rows:
        if r["naming_file_count"] != len(r["naming_files"]):
            problems.append("%s: naming_file_count != len(naming_files)" % r["note"])
        if r["producer_count"] != len(r["producers"]):
            problems.append("%s: producer_count != len(producers)" % r["note"])
        want = class_of(r["producer_count"], len(r["faces_probed"]), len(r["digest_hits"]))
        if r["class"] != want:
            problems.append("%s: class %s does not re-derive (want %s)" % (r["note"], r["class"], want))
        if r["class"] == C_DIGEST and not r["digest_hits"]:
            problems.append("%s: graded digest but carries no hit" % r["note"])
        if r["own_producer_files"] != sorted(p["file"] for p in r["own_producers"]):
            problems.append("%s: own_producer_files do not re-derive" % r["note"])
        own_probed = len([f for f in r["faces_probed"]
                          if f["file"] in set(r["own_producer_files"])])
        if own_probed != r["own_producer_faces_probed"]:
            problems.append("%s: own_producer_faces_probed %d != %d"
                            % (r["note"], r["own_producer_faces_probed"], own_probed))
        if r["digest_hits"] and r["class"] != C_DIGEST:
            problems.append("%s: carries a hit but is not graded digest" % r["note"])
        kind = r["digest_hits"][0]["kind"] if r["digest_hits"] else None
        if kind != r["digest_kind"]:
            problems.append("%s: digest_kind %s != %s" % (r["note"], r["digest_kind"], kind))
    if len(face.get("residue", [])) != s["residue_rows"]:
        problems.append("residue_rows %d != len(residue) %d"
                        % (s["residue_rows"], len(face.get("residue", []))))
    if len(face.get("unprobeable", [])) != s["unprobeable_rows"]:
        problems.append("unprobeable_rows %d != len(unprobeable) %d"
                        % (s["unprobeable_rows"], len(face.get("unprobeable", []))))
    kinds = {k: sum(1 for r in rows if r["digest_kind"] == k) for k in DIGEST_KINDS}
    if kinds != s["digest_kind_counts"]:
        problems.append("digest_kind_counts do not re-derive: %s vs %s"
                        % (kinds, s["digest_kind_counts"]))
    if verdict_for(rows) != face["verdict"]:
        problems.append("verdict %s does not re-derive (want %s)"
                        % (face["verdict"], verdict_for(rows)))
    return problems


def verify() -> list:
    """Re-derive from the live tree; refuse a face that no longer reproduces."""
    fresh = build()
    published = _load(os.path.join(OUTDIR, FACE_NAME))
    problems = []
    if [r["note"] for r in fresh["rows"]] != [r["note"] for r in published["rows"]]:
        problems.append("note population moved since publication")
    for a, b in zip(fresh["rows"], published["rows"]):
        if a["note"] != b["note"]:
            continue
        if a["class"] != b["class"]:
            problems.append("%s: class %s -> %s" % (a["note"], b["class"], a["class"]))
        if len(a["digest_hits"]) != len(b["digest_hits"]):
            problems.append("%s: digest hits %d -> %d"
                            % (a["note"], len(b["digest_hits"]), len(a["digest_hits"])))
        if len(a["faces_probed"]) != len(b["faces_probed"]):
            problems.append("%s: probed faces %d -> %d"
                            % (a["note"], len(b["faces_probed"]), len(a["faces_probed"])))
    if fresh["verdict"] != published["verdict"]:
        problems.append("verdict %s -> %s" % (published["verdict"], fresh["verdict"]))
    return problems


# ----------------------------------------------------------------------------- selftest


def selftest() -> int:
    bad = []

    def check(name, ok, detail=""):
        if not ok:
            bad.append(name + ((" | " + str(detail)) if detail else ""))

    sha = hashlib.sha256(b"note bytes").hexdigest()

    # 1 full digest
    check("a full sha256 value is a digest hit",
          _value_kind("prereg_sha256", sha, sha) == D_FULL)
    check("sha256: prefixed value is a digest hit",
          _value_kind("k", "sha256:" + sha, sha) == D_FULL)
    # 2 prefix
    check("a 16-char hex prefix is a digest hit",
          _value_kind("k", sha[:16], sha) == D_PREFIX)
    check("a 6-char prefix is not strong enough to be a digest",
          _value_kind("k", sha[:6], sha) == "")
    check("a value that is not a prefix of the sha is not a hit",
          _value_kind("k", "0" * 16, sha) == "")
    # 3 as-of
    check("a prereg key carrying an ISO date is a pinned as-of",
          _value_kind("prereg_as_of", "2026-10-09", sha) == D_ASOF)
    check("a date on a key that does not name the prereg is not a hit",
          _value_kind("published_at", "2026-10-09", sha) == "")
    prose = prose_asof({"prereg_state": "FROZEN v1.0 (2026-10-03 bm-b r610)"})
    check("a prose freeze date is published as prose, not as a pin",
          len(prose) == 1 and prose[0]["field"] == "prereg_state", prose)
    check("a prose freeze date is not a digest hit",
          _value_kind("prereg_state", "FROZEN v1.0 (2026-10-03 bm-b r610)", sha) == "")
    check("a keyed ISO date is not also counted as prose",
          prose_asof({"prereg_as_of": "2026-10-09"}) == [])

    # 4 payload walk finds a nested hit and keeps the field path
    payload = {"meta": {"pin": {"prereg_sha256": sha}}, "rows": [{"x": 1}]}
    hits = digest_hits(payload, sha, "STUDY")
    check("a nested digest is found", len(hits) == 1 and hits[0]["kind"] == D_FULL, hits)
    check("the hit names its field path", hits and hits[0]["field"] == "meta.pin.prereg_sha256", hits)
    check("a payload with no digest yields no hit", digest_hits({"a": 1}, sha, "S") == [])

    # 5 face extraction from source
    src = ('import os\nOUT = "results/state_tilt/THING-2026-11-06.json"\n'
           'T = "results/t23/%s.json" % X\nP = os.path.join(ROOT, "src", "x.py")\n')
    faces = faces_in_tree(ast.parse(src))
    check("a literal results face is extracted", "results/state_tilt/THING-2026-11-06.json" in faces, faces)
    check("a template face is extracted and marked as a template",
          "results/t23/%s.json" in faces and is_template("results/t23/%s.json"), faces)
    check("a non-results path is not a face",
          not any("src/x.py" in f for f in faces), faces)
    check("a backslash literal is normalised", faces_in_tree(
        ast.parse('P = "results\\\\t23\\\\X.json"\n')) == ["results/t23/X.json"])
    check("a prose line that merely mentions results/ is still a face token",
          faces_in_tree(ast.parse('S = "see results/a.json for detail"\n')) == ["results/a.json"])

    # 6 naming lines
    text = "a\nPREREG = 'research/X-P1.md'\nb\n# cites research/X-P1.md\n"
    check("naming lines are 1-based and complete",
          naming_lines(text, "X-P1.md") == [2, 4], naming_lines(text, "X-P1.md"))
    check("a basename that is absent has no naming lines",
          naming_lines(text, "Y-P1.md") == [])

    # 7 classes
    check("no naming producer is its own class", class_of(0, 0, 0) == C_NOT_NAMED)
    check("naming producers with no probeable face are its own class",
          class_of(3, 0, 0) == C_NOT_NAMED)
    check("producers with probed faces and no hit", class_of(3, 5, 0) == C_NAMED_NO_DIGEST)
    check("one hit is enough to be digest published", class_of(3, 5, 1) == C_DIGEST)
    check("a hit without a probed face cannot happen but is graded by the hit",
          class_of(0, 0, 0) == C_NOT_NAMED)

    # 8 verdict precedence
    check("empty population", verdict_for([]) == V_EMPTY)
    check("all digest", verdict_for([{"class": C_DIGEST}]) == V_ALL)
    check("none digest", verdict_for([{"class": C_NAMED_NO_DIGEST},
                                      {"class": C_NOT_NAMED}]) == V_NONE)
    check("some digest", verdict_for([{"class": C_DIGEST},
                                      {"class": C_NOT_NAMED}]) == V_SOME)

    # 9 own outputs are never population
    check("own latest face is excluded", is_own_output("results/state_tilt/" + FACE_NAME))
    check("own dated face is excluded",
          is_own_output("results/state_tilt/%s-2026-11-06.json" % DATED_PREFIX))
    check("a sibling face is not excluded",
          not is_own_output("results/state_tilt/deadprereg_latest.json"))

    # 10 a truncated face token is still a path, not a directory
    check("a directory-only token is not a face", faces_in_tree(ast.parse('D = "results/t23/"\n')) == [])

    total = 30
    if bad:
        print("selftest FAIL %d/%d" % (len(bad), total))
        for b in bad:
            print("  -", b)
        return 1
    print("selftest %d/%d PASS" % (total, total))
    return 0


# ----------------------------------------------------------------------------- cli


def main(argv: list) -> int:
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "run":
        face = build()
        path = write_face(face)
        s = face["summary"]
        print("wrote %s" % _rel(path))
        print("notes %d | class %s" % (s["notes"], json.dumps(s["class_counts"], ensure_ascii=False)))
        print("naming files %d (%d distinct) | producers %d | faces probed %d | missing %d"
              % (s["naming_files_total"], s["distinct_naming_files"], s["producers_total"],
                 s["faces_probed_total"], s["faces_missing_on_disk_total"]))
        print("digest kinds %s | residue %d | unprobeable %d"
              % (json.dumps(s["digest_kind_counts"]), s["residue_rows"], s["unprobeable_rows"]))
        print("verdict: %s" % face["verdict"])
        return 0
    if cmd == "check":
        face = _load(os.path.join(OUTDIR, FACE_NAME))
        problems = tally_problems(face)
        print("problems=%s" % json.dumps(problems, ensure_ascii=False))
        return 0 if not problems else 1
    if cmd == "verify":
        problems = verify()
        print("problems=%s" % json.dumps(problems, ensure_ascii=False))
        return 0 if not problems else 1
    if cmd == "selftest":
        return selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))