"""E473 -- is the unread vintage output spillover from producers that also publish studied faces?

E472 priced 97 vintage families under ``results/`` that no study opens: 571 files, 28.5 MB, and 10-11
unread families re-emitted on each of the last six cutoffs.  It answered "who reads this" and left
"who writes it, and what else does that writer write" open.  If a writer's studied output and its
unread output come from the same script, the unread part is spillover that can be pruned at source;
if the unread part is a producer's only resolved output, the producer itself is the question.

Producer evidence is deliberately stricter than E472's ``writes`` flag, which reads "the site has any
write call and its literals mention the family token" and therefore counts ``smoke_test.py`` (the
suite writes something and mentions 54 families).  Here a writer is a site whose **write-call
evidence** names the family token: the literals inside an ``open(path, "w")`` / ``write_text`` /
``to_csv`` / ``json.dump`` argument list, plus one hop through assigned names.  The gap between the
two definitions is published as a finding, not hidden.

Per writer this face publishes:

  families_written        vintage families (of E472's 97) whose token its write evidence names
  faces_resolved          files under ``results/`` its write evidence resolves to (path literal,
                          basename literal, or family token prefix)
  faces_with_a_study      resolved faces some other study site opens (not a smoke leg, not a
                          one-off ``_r`` script)
  unread_bytes_per_cutoff sum over its unread families of E472's bytes / vintages
  class                   emits both studied and unread output / resolves faces and none is
                          studied / writes a family but no face its evidence names resolves

Reader evidence is one pass over the ``.py`` corpus collecting opener-call literals (``open`` /
``read_text`` / ``read_csv`` / ``json.load`` ...), keyed by normalised path, basename and family
token.  A face's consumers are the opener sites whose key matches, minus the face's own writer.

Scope limits, published not hidden: only ``results/`` can be resolved (docs/ and data/ faces are out
of scope); a path composed from a variable that no assignment in the same module binds is not
resolved; a face resolved by a family-token prefix is attributed to that writer even when another
writer also emits the family (the ``shared_families`` field says so); and the reader channel is a
literal channel -- an opener that composes the whole path at runtime from argv is invisible here.

Run:      python scripts/e473_producer_spill.py run
Verify:   python scripts/e473_producer_spill.py verify   (rebuilds from the live tree and compares)
Check:    python scripts/e473_producer_spill.py check    (every tally re-derives from the rows)
Selftest: python scripts/e473_producer_spill.py selftest
"""

import argparse
import ast
import datetime
import io
import json
import os
import re
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
if os.path.join(ROOT, "scripts") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "scripts"))

import e451_prereg_digest as e451  # noqa: E402  (read_text)
import e468_pointer_reach as e468  # noqa: E402  (_walk_py)
import e470_target_read as e470  # noqa: E402  (_assignments / _is_opener / _is_smoke)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "producerspill_latest.json"
DATED_PREFIX = "PRODUCERSPILL"
CARD = "E473-DO-THE-UNREAD-VINTAGE-FAMILIES-COME-FROM-PRODUCERS-WHOSE-OTHER-FACES-A-STUDY-DOES-OPEN"
SOURCE_FACE = os.path.join("results", "state_tilt", "vintageread_latest.json")

SELF_SKIP = tuple(e470.SELF_SKIP) + ("e472_", "e473_", "run_e472", "run_e473")
MAX_READ_BYTES = 4 * 1024 * 1024
FACE_EXTS = ("json", "jsonl", "csv", "md", "parquet", "txt", "html")
WRITE_FUNCS = ("write_text", "write_bytes", "savetxt", "to_csv", "to_parquet", "to_json",
               "writerow", "writerows", "dump", "write", "replace")
DATE_TAIL = re.compile(r"[-_](\d{8}|\d{4}-\d{2}-\d{2})(?:[-_][A-Za-z0-9]+)*$")
MIN_TOKEN_LEN = 4

EMITS_BOTH = "publishes_at_least_one_face_a_study_opens_and_at_least_one_family_nothing_reads"
EMITS_ONLY_UNREAD = "resolves_faces_and_none_of_them_is_opened_by_a_study"
EMITS_UNRESOLVED = "writes_a_family_but_no_face_its_evidence_names_can_be_resolved_on_disk"
CLASSES = (EMITS_BOTH, EMITS_ONLY_UNREAD, EMITS_UNRESOLVED)

V_NO_WRITER = "no_write_call_evidence_names_any_of_the_unread_families"
V_ALL_SPILL = "every_unread_family_writer_also_publishes_a_face_a_study_opens"
V_NONE_SPILL = "no_unread_family_writer_publishes_any_face_a_study_opens"
V_MIXED = "some_unread_family_writers_also_publish_studied_faces_and_some_publish_only_unread"
VERDICT_VOCAB = (V_NO_WRITER, V_ALL_SPILL, V_NONE_SPILL, V_MIXED)


def _load(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _norm(text):
    return str(text).replace("\\", "/").strip()


def _now():
    return datetime.datetime.now().astimezone()


def _cutoff(root=None):
    return datetime.date.today().isoformat()


# ------------------------------------------------------------------ tokens


def family_token(name):
    """``WIDTHLADDER-20261106`` / ``WIDTHLADDER-`` / ``widthladder_latest`` -> ``widthladder``."""
    stem = os.path.basename(_norm(name))
    if "." in stem:
        stem = stem.rsplit(".", 1)[0]
    stem = DATE_TAIL.sub("", stem)
    return stem.strip("-_ ").lower()


def _has_ext(name):
    return "." in os.path.basename(_norm(name)) and \
        os.path.basename(_norm(name)).rsplit(".", 1)[-1].lower() in FACE_EXTS


def _ext(name):
    base = os.path.basename(_norm(name))
    return base.rsplit(".", 1)[-1].lower() if "." in base else ""


# ------------------------------------------------------------- write evidence


def _is_write_call(node):
    f = node.func
    name = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else "")
    if name == "open":
        modes = []
        if len(node.args) > 1 and isinstance(node.args[1], ast.Constant):
            modes.append(node.args[1].value)
        for kw in node.keywords:
            if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                modes.append(kw.value.value)
        return any(isinstance(m, str) and ("w" in m or "a" in m or "x" in m) for m in modes)
    return name in WRITE_FUNCS


def write_evidence(tree, assigned):
    """Literals a write call could put on disk: its own args plus one hop through names."""
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and _is_write_call(node):
            out.extend(e470._evidence(node, assigned))
    return out


def opener_evidence(tree, assigned):
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and e470._is_opener(node):
            out.extend(e470._evidence(node, assigned))
    return out


# ------------------------------------------------------------- results index


def results_index(root=None):
    """{basename_lower: [rel, ...]}, {family_token: [rel, ...]} over files under results/."""
    root = root or ROOT
    base_idx, fam_idx = {}, {}
    pop = os.path.join(root, "results")
    for dirpath, dirnames, filenames in os.walk(pop):
        dirnames[:] = [d for d in dirnames if d not in ("_quarantine", "__pycache__")]
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            rel = _norm(os.path.relpath(full, root))
            base_idx.setdefault(fn.lower(), []).append(rel)
            tok = family_token(fn)
            if tok:
                fam_idx.setdefault(tok, []).append(rel)
    return base_idx, fam_idx


def _resolve(lits, root, base_idx, fam_idx):
    """Files under results/ a writer's evidence literals can name. Returns {rel: channel}."""
    out = {}
    for lit in lits:
        n = _norm(lit)
        if not n or len(n) < MIN_TOKEN_LEN:
            continue
        if "/" in n and _has_ext(n):
            for cand in (n, n.lstrip("./")):
                p = os.path.join(root, cand)
                if os.path.isfile(p) and _norm(cand).startswith("results/"):
                    out[_norm(cand)] = "path_literal"
                    break
            continue
        if _has_ext(n) and "/" not in n:
            for rel in base_idx.get(n.lower()) or []:
                out.setdefault(rel, "basename_literal")
            continue
        if not _has_ext(n) and (n.endswith("-") or n.endswith("_")) and len(n) >= 6:
            tok = family_token(n)
            for rel in fam_idx.get(tok) or []:
                out.setdefault(rel, "family_token")
    return out


# ------------------------------------------------------------- reader index


def scan_corpus(root=None, fam_tokens=None):
    """One AST pass over the corpus: opener records plus each site's write evidence.

    Two passes over ~8k sources cost two parses per file; the reader channel and the writer channel
    read the same trees, so they are collected together.
    """
    root = root or ROOT
    fam_tokens = fam_tokens or {}
    records, writers = [], {}
    scanned = 0
    for rel in e468._walk_py(root):
        base = os.path.basename(rel)
        if any(base.startswith(s) for s in SELF_SKIP):
            continue
        path = os.path.join(root, rel)
        try:
            if os.path.getsize(path) > MAX_READ_BYTES:
                continue
            text = e451.read_text(path)
        except (OSError, ValueError):
            continue
        if not any(t in text for t in ("open(", "write_text", "dump(", "to_csv", "to_parquet",
                                       "savetxt", "write(", "read_text", "read_csv", "load(")):
            continue
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        scanned += 1
        assigned = e470._assignments(tree)
        for lit in opener_evidence(tree, assigned):
            n = _norm(lit)
            if not n or len(n) < MIN_TOKEN_LEN:
                continue
            keys = []
            if "/" in n:
                keys.append(("path", n))
            if _has_ext(n):
                keys.append(("basename", os.path.basename(n).lower()))
            tok = family_token(n)
            if tok and len(tok) >= MIN_TOKEN_LEN:
                keys.append(("family", tok))
            if keys:
                records.append({"source": rel, "literal": n, "keys": keys})
        lits = write_evidence(tree, assigned)
        if lits:
            named = sorted({family_token(lit) for lit in lits} & set(fam_tokens))
            if named:
                writers[rel] = {"literals": lits, "named": named}
    return records, writers, {"sources_scanned": scanned, "opener_literals": len(records)}


def consumer_lookup(records):
    """{("path"|"basename"|"family", key): {source: kind}}"""
    idx = {}
    for rec in records:
        kind = "leg" if e470._is_smoke(rec["source"]) else (
            "round" if e470._is_round_script(rec["source"]) else "study")
        for key in rec["keys"]:
            idx.setdefault(key, {}).setdefault(rec["source"], kind)
    return idx


def _consumers_of(face, idx, writer):
    cands = {}
    cands.update(idx.get(("path", face), {}) or {})
    cands.update(idx.get(("basename", os.path.basename(face).lower()), {}) or {})
    cands.update(idx.get(("family", family_token(face)), {}) or {})
    cands.pop(writer, None)
    kinds = {"study": [], "leg": [], "round": []}
    for src, kind in cands.items():
        kinds.setdefault(kind, []).append(src)
    for key in kinds:
        kinds[key].sort()
    return kinds


# ------------------------------------------------------------------ build


def build(write=True, root=None, source_face=None):
    root = root or ROOT
    source_face = source_face or os.path.join(root, SOURCE_FACE)
    src = _load(source_face)
    families = src.get("rows") or []
    base_idx, fam_idx = results_index(root)

    fam_tokens = {}
    for row in families:
        tok = family_token(str(row["family"])) if row.get("family") else ""
        if tok:
            fam_tokens[tok] = row

    records, writers, scan_meta = scan_corpus(root, fam_tokens)
    idx = consumer_lookup(records)
    scanned = scan_meta["sources_scanned"]

    rows = []
    for rel, info in sorted(writers.items()):
        unread_fams = [fam_tokens[t] for t in info["named"]]
        resolved = _resolve(info["literals"], root, base_idx, fam_idx)
        face_rows = []
        for face in sorted(resolved):
            kinds = _consumers_of(face, idx, rel)
            if kinds["study"]:
                residue = "opened_by_a_study_that_does_not_write_it"
            elif kinds["leg"]:
                residue = "opened_only_by_a_smoke_or_runner_leg"
            elif kinds["round"]:
                residue = "opened_only_by_a_one_off_round_script"
            else:
                residue = "no_opener_site_in_the_corpus"
            face_rows.append({"face": face, "resolved_by": resolved[face], "residue": residue,
                              "study_consumers": kinds["study"],
                              "leg_consumers": kinds["leg"],
                              "round_consumers": kinds["round"]})
        studied = [fr for fr in face_rows if fr["residue"] ==
                   "opened_by_a_study_that_does_not_write_it"]
        unread_bytes = 0.0
        for fam in unread_fams:
            vintages = max(1, int(fam.get("vintages") or 1))
            unread_bytes += float(fam.get("bytes") or 0) / vintages
        rows.append({
            "writer": rel,
            "families_written": [f["family"] for f in unread_fams],
            "families_written_count": len(unread_fams),
            "shared_families": [f["family"] for f in unread_fams
                                if len(f.get("producers") or []) > 1],
            "faces_resolved": len(face_rows),
            "faces_with_a_study": len(studied),
            "unread_faces": sum(1 for fr in face_rows if fr["residue"] !=
                                "opened_by_a_study_that_does_not_write_it"),
            "unread_bytes_per_cutoff": round(unread_bytes, 6),
            "class": (EMITS_BOTH if studied else (EMITS_ONLY_UNREAD if face_rows else EMITS_UNRESOLVED)),
            "faces": face_rows,
        })

    both = [r for r in rows if r["class"] == EMITS_BOTH]
    only = [r for r in rows if r["class"] == EMITS_ONLY_UNREAD]
    unresolved = [r for r in rows if r["class"] == EMITS_UNRESOLVED]
    distinct_unread = sum(float(f.get("bytes") or 0) / max(1, int(f.get("vintages") or 1))
                          for f in families)
    covered = {fam for r in rows for fam in r["families_written"]}
    summary = {
        "source_face": _norm(os.path.relpath(source_face, root)),
        "source_families": len(families),
        "source_family_bytes_per_cutoff": round(distinct_unread, 6),
        "families_with_a_write_evidence_writer": len(covered),
        "families_with_no_write_evidence_writer": len(families) - len(covered),
        "writers": len(rows),
        "writers_emitting_both": len(both),
        "writers_emitting_only_unread": len(only),
        "writers_with_no_resolved_face": len(unresolved),
        "writers_ranked_by_unread_bytes_per_cutoff": [
            {"writer": r["writer"], "unread_bytes_per_cutoff": r["unread_bytes_per_cutoff"],
             "families": r["families_written_count"], "class": r["class"]}
            for r in sorted(rows, key=lambda x: (-x["unread_bytes_per_cutoff"], x["writer"]))[:15]
        ],
        "sum_of_writers_unread_bytes_per_cutoff": round(
            sum(r["unread_bytes_per_cutoff"] for r in rows), 6),
        "resolved_faces_total": sum(r["faces_resolved"] for r in rows),
        "resolved_faces_with_a_study": sum(r["faces_with_a_study"] for r in rows),
        "e472_loose_producers": len({p for f in families for p in (f.get("producers") or [])}),
        "writer_scan": {"sources_with_write_evidence": scanned},
        "reader_scan": scan_meta,
    }
    face = {
        "card": CARD,
        "study": "E473_is_the_unread_vintage_output_spillover_from_writers_that_also_publish_"
                 "studied_faces",
        "title": "is the unread vintage output spillover from writers whose other faces are read?",
        "evidence_cutoff": _cutoff(root) if root == ROOT else "2026-01-01",
        "generated": _now().isoformat(timespec="seconds"),
        "population_source": {
            "face": summary["source_face"],
            "families": len(families),
            "files": src.get("summary", {}).get("files_in_unread_families"),
            "note": "E472 rows are the population; this study does not re-derive the families",
        },
        "writer_definition": "a site whose write-call evidence literals name the family token "
                             "(stricter than E472's writes flag, which is any write call in a "
                             "site that merely mentions the token)",
        "summary": summary,
        "rows": rows,
        "verdict": verdict_for(summary),
        "verdict_vocab": list(VERDICT_VOCAB),
        "method_limits": [
            "only files under results/ can be resolved; docs/ and data/ output is out of scope",
            "a path composed at runtime from argv or a config file has no literal and is invisible",
            "a family-token match attributes every file of that family to the writer even when "
            "several writers emit it (shared_families says so)",
            "unread bytes are E472's family bytes divided by its vintage count, so a family whose "
            "files are uneven in size yields an average per cutoff, not a measured one",
            "a reader that normalises the path after reading argv is counted as no consumer",
        ],
    }
    if write:
        os.makedirs(OUTDIR, exist_ok=True)
        if root == ROOT:
            dated = os.path.join(OUTDIR, "%s-%s.json" % (DATED_PREFIX, face["evidence_cutoff"]))
            _write_text(dated, json.dumps(face, ensure_ascii=False, indent=1))
        _write_text(os.path.join(OUTDIR, FACE_NAME),
                    json.dumps(face, ensure_ascii=False, indent=1))
    return face


def verdict_for(summary):
    if not summary.get("writers"):
        return V_NO_WRITER
    both = summary.get("writers_emitting_both") or 0
    only = summary.get("writers_emitting_only_unread") or 0
    if both and not only:
        return V_ALL_SPILL
    if only and not both:
        return V_NONE_SPILL
    return V_MIXED


# ------------------------------------------------------------------ guards


def _recompute_tallies(face):
    rows = face.get("rows") or []
    both = [r for r in rows if r.get("class") == EMITS_BOTH]
    only = [r for r in rows if r.get("class") == EMITS_ONLY_UNREAD]
    unresolved = [r for r in rows if r.get("class") == EMITS_UNRESOLVED]
    return {
        "writers": len(rows),
        "writers_emitting_both": len(both),
        "writers_emitting_only_unread": len(only),
        "writers_with_no_resolved_face": len(unresolved),
        "resolved_faces_total": sum(int(r.get("faces_resolved") or 0) for r in rows),
        "resolved_faces_with_a_study": sum(int(r.get("faces_with_a_study") or 0) for r in rows),
        "sum_of_writers_unread_bytes_per_cutoff": round(
            sum(float(r.get("unread_bytes_per_cutoff") or 0) for r in rows), 6),
    }


def row_problems(face):
    problems = []
    rows = face.get("rows") or []
    summary = face.get("summary") or {}
    for key, value in _recompute_tallies(face).items():
        if summary.get(key) != value:
            problems.append("summary.%s does not re-derive (%r vs %r)"
                            % (key, summary.get(key), value))
    for r in rows:
        fams = r.get("families_written") or []
        if r.get("families_written_count") != len(fams):
            problems.append("%s: families_written_count != len(families_written)" % r.get("writer"))
        if not fams:
            problems.append("%s: a writer row names no family" % r.get("writer"))
        faces = r.get("faces") or []
        if r.get("faces_resolved") != len(faces):
            problems.append("%s: faces_resolved != len(faces)" % r.get("writer"))
        studied = [f for f in faces
                   if f.get("residue") == "opened_by_a_study_that_does_not_write_it"]
        if r.get("faces_with_a_study") != len(studied):
            problems.append("%s: faces_with_a_study does not re-derive" % r.get("writer"))
        for f in studied:
            if not f.get("study_consumers"):
                problems.append("%s: a studied face names no study consumer" % r.get("writer"))
        if r.get("class") not in CLASSES:
            problems.append("%s: class outside the frozen vocabulary" % r.get("writer"))
        elif r.get("class") == EMITS_BOTH and not studied:
            problems.append("%s: emits_both with no studied face" % r.get("writer"))
        elif r.get("class") == EMITS_ONLY_UNREAD and studied:
            problems.append("%s: only_unread with a studied face" % r.get("writer"))
        elif r.get("class") == EMITS_ONLY_UNREAD and not faces:
            problems.append("%s: only_unread with no resolved face" % r.get("writer"))
        elif r.get("class") == EMITS_UNRESOLVED and faces:
            problems.append("%s: unresolved with a resolved face" % r.get("writer"))
        if r.get("unread_faces") != len(faces) - len(studied):
            problems.append("%s: unread_faces does not re-derive" % r.get("writer"))
        if float(r.get("unread_bytes_per_cutoff") or 0) < 0:
            problems.append("%s: negative unread bytes" % r.get("writer"))
    if face.get("verdict") not in VERDICT_VOCAB:
        problems.append("verdict outside the frozen vocabulary")
    elif face.get("verdict") != verdict_for(summary):
        problems.append("verdict does not re-derive from the summary")
    return problems


def check(path=None):
    path = path or os.path.join(OUTDIR, FACE_NAME)
    face = _load(path)
    problems = row_problems(face)
    for p in problems:
        print("PROBLEM", p)
    print("checked %s: problems=%d rows=%d" % (_norm(os.path.relpath(path, ROOT)),
                                               len(problems), len(face.get("rows") or [])))
    return 1 if problems else 0


def verify():
    live = build(write=False)
    path = os.path.join(OUTDIR, FACE_NAME)
    published = _load(path)
    problems = []
    if live.get("verdict") != published.get("verdict"):
        problems.append("verdict %r != live %r" % (published.get("verdict"), live.get("verdict")))
    ls, ps = live.get("summary") or {}, published.get("summary") or {}
    for key in ("writers", "writers_emitting_both", "writers_emitting_only_unread",
                "resolved_faces_total", "resolved_faces_with_a_study"):
        if ls.get(key) != ps.get(key):
            problems.append("%s: published %r live %r" % (key, ps.get(key), ls.get(key)))
    for p in problems:
        print("PROBLEM", p)
    print("verified %s against the live tree: problems=%d" % (FACE_NAME, len(problems)))
    return 1 if problems else 0


def _write_text(path, text):
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


# ------------------------------------------------------------------ selftest


def _fixture(tmp):
    res = os.path.join(tmp, "results", "state_tilt")
    os.makedirs(res)
    scr = os.path.join(tmp, "scripts")
    os.makedirs(scr)
    for name, body in (
        ("ALPHA-20260101.json", "{}"),
        ("ALPHA-20260102.json", "{}"),
        ("DELTA-20260101.json", "{}"),
        ("BETA-20260101.json", "{}"),
        ("BETA-20260102.json", "{}"),
        ("GAMMA-20260101.json", "{}{}"),
        ("GAMMA-20260102.json", "{}{}"),
    ):
        with io.open(os.path.join(res, name), "w", encoding="utf-8") as fh:
            fh.write(body)
    _write_text(os.path.join(scr, "p.py"),
                "import json\n"
                "with open('results/state_tilt/ALPHA-20260101.json', 'w') as fh:\n"
                "    json.dump({}, fh)\n"
                "with open('results/state_tilt/ALPHA-20260102.json', 'w') as fh:\n"
                "    json.dump({}, fh)\n"
                "with open('results/state_tilt/DELTA-20260101.json', 'w') as fh:\n"
                "    json.dump({}, fh)\n")
    _write_text(os.path.join(scr, "q.py"),
                "import json\n"
                "with open('results/state_tilt/BETA-' + '20260101' + '.json', 'w') as fh:\n"
                "    json.dump({}, fh)\n")
    _write_text(os.path.join(scr, "r.py"),
                "import json\n"
                "for d in ('20260101', '20260102'):\n"
                "    p = 'results/state_tilt/GAMMA-' + d + '.json'\n"
                "    open(p, 'w').write('{}{}')\n")
    _write_text(os.path.join(scr, "reader.py"),
                "import json\n"
                "f = json.load(open('results/state_tilt/DELTA-20260101.json', encoding='utf-8'))\n")
    _write_text(os.path.join(scr, "smoke_test.py"),
                "import json\n"
                "x = json.load(open('results/state_tilt/BETA-20260101.json', encoding='utf-8'))\n")
    src = {
        "rows": [
            {"family": "ALPHA", "bytes": 200, "vintages": 2, "producers": ["scripts/p.py"]},
            {"family": "BETA", "bytes": 100, "vintages": 2, "producers": ["scripts/q.py"]},
            {"family": "GAMMA", "bytes": 40, "vintages": 2, "producers": ["scripts/r.py"]},
        ],
        "summary": {"files_in_unread_families": 6},
    }
    src_path = os.path.join(tmp, "vintageread_latest.json")
    _write_text(src_path, json.dumps(src))
    return src_path


def selftest():
    fails = []
    legs = [0]

    def want(cond, msg):
        legs[0] += 1
        if not cond:
            fails.append(msg)

    with tempfile.TemporaryDirectory() as tmp:
        src_path = _fixture(tmp)
        face = build(write=False, root=tmp, source_face=src_path)
        rows = {r["writer"].replace("\\", "/"): r for r in face["rows"]}
        want("scripts/p.py" in rows, "p.py was not located as a writer")
        want("scripts/q.py" in rows, "q.py was not located as a writer")
        want("scripts/r.py" in rows, "r.py was not located as a writer (family-token path)")
        want("scripts/reader.py" not in rows, "a pure reader was classed as a writer")
        want("scripts/smoke_test.py" not in rows, "the smoke leg was classed as a writer")
        if "scripts/p.py" in rows:
            p = rows["scripts/p.py"]
            want(p["class"] == EMITS_BOTH, "p.py should emit both, got %r" % (p["class"],))
            want(p["faces_with_a_study"] >= 1, "p.py's DELTA face has no study consumer")
            want(abs(p["unread_bytes_per_cutoff"] - 100.0) < 1e-6,
                 "p.py unread bytes per cutoff %r != 100" % (p["unread_bytes_per_cutoff"],))
            want(p["families_written"] == ["ALPHA"], "p.py families %r" % (p["families_written"],))
        if "scripts/q.py" in rows:
            q = rows["scripts/q.py"]
            want(q["class"] == EMITS_ONLY_UNREAD, "q.py should be only-unread")
            want(q["faces_with_a_study"] == 0, "q.py's BETA face should have no study consumer")
            want(all("smoke_test.py" not in (f.get("study_consumers") or [])
                     for f in q["faces"]), "a smoke leg was counted as a study consumer")
        if "scripts/r.py" in rows:
            r = rows["scripts/r.py"]
            want(r["class"] == EMITS_ONLY_UNREAD, "r.py should be only-unread")
            want(r["faces_resolved"] >= 2, "r.py's family token resolved %d faces"
                 % (r["faces_resolved"],))
        want(face["verdict"] == V_MIXED, "verdict %r != mixed" % (face["verdict"],))
        want(face["summary"]["writers"] == 3, "writers %r" % (face["summary"]["writers"],))
        want(face["summary"]["writers_with_no_resolved_face"] == 0,
             "an unresolved writer appeared in a fixture where every writer resolves")
        want(row_problems(face) == [], "row_problems on a clean face: %r" % (row_problems(face),))

        # doctored copies must be caught
        bad = json.loads(json.dumps(face))
        bad["summary"]["writers_emitting_both"] += 1
        want(row_problems(bad) != [], "a doctored both-count survived the guard")
        bad2 = json.loads(json.dumps(face))
        for r in bad2["rows"]:
            if r["class"] == EMITS_BOTH:
                r["faces_with_a_study"] = 0
        want(row_problems(bad2) != [], "an emits_both row with no studied face survived")
        bad3 = json.loads(json.dumps(face))
        bad3["rows"][0]["unread_faces"] = 99
        want(row_problems(bad3) != [], "an unread_faces mismatch survived")
        bad4 = json.loads(json.dumps(face))
        bad4["verdict"] = "something_else"
        want(row_problems(bad4) != [], "a verdict outside the vocabulary survived")

    print("selftest: %s (%d legs, %d failed)" % ("FAIL" if fails else "PASS", legs[0],
          len(fails)))
    for f in fails:
        print("  FAIL ::", f)
    return 1 if fails else 0


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "check":
        return check()
    if cmd == "verify":
        return verify()
    if cmd == "run":
        face = build()
        s = face["summary"]
        print("writers=%d both=%d only_unread=%d resolved_faces=%d studied=%d verdict=%s"
              % (s["writers"], s["writers_emitting_both"], s["writers_emitting_only_unread"],
                 s["resolved_faces_total"], s["resolved_faces_with_a_study"], face["verdict"]))
        print("unread bytes/cutoff: families=%.1f sum_of_writers=%.1f"
              % (s["source_family_bytes_per_cutoff"], s["sum_of_writers_unread_bytes_per_cutoff"]))
        return 0
    print("unknown command %r (run|check|verify|selftest)" % (cmd,))
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))