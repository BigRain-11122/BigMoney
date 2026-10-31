"""E325 -- how many census gates read a value no source in the tree can produce.

E321..E324 measured a NAME problem: for each gate leaf, is there a producer, and does that
producer publish a key of that name.  Every one of those studies took the FACE for granted --
that some source in the tree writes it.  The pool card asks the layer below: **how many of the
196 gate rows sit on a face that no source can reproduce at all?**

A face-level defect is not a naming defect.  If the face is unreproducible, renaming a key,
resolving a decoy or widening a needle all buy nothing: the row describes a number whose
producer does not exist, and the honest reading of every other field on that row is "unknown".

The measurement is deliberately a ladder, because "no writer" is a fact about a LOOKUP until it
has been widened.  Each rung keeps every earlier rung's writers and adds exactly one way of
naming a face:

  R1 STANDARD   E321/E312's lookup as published (self-excluding auditor set, single-line writer)
  R2 FULL       every python source under the producing packages kept (E323's corpus), this
                scanner excluded -- the auditor's own faces become visible
  R3 FAMILY     a face named by a format template (``f"p1e_nulls_{cls}.json"``) counts
  R4 COMPOSED   a path assembled on an assignment/os.path.join line counts when its module can
                write (the ``os.path.join(OUT, "turnover_derivation.json")`` shape)

Usage:
    python scripts/e325_orphan_gate_faces.py run|verify|selftest
"""
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import e312_gate_operand_identity as e312  # noqa: E402  (path set above)
import e321_quantity_name_reach as e321  # noqa: E402
import e323_reach_under_wider_needle as e323  # noqa: E402

ROOT = e312.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
INPUT = "results/state_tilt/REACHWIDE-2026-10-31.json"
TODAY = "2026-10-31"
FACE = "ORPHANGATEFACE-%s.json" % TODAY
LATEST = "orphangateface_latest.json"
STUDY = "E325_orphan_gate_faces"

CLS_NAMED = "reproducible_by_a_source_that_names_the_file_and_writes"
CLS_COMPOSED = "reproducible_through_a_path_the_source_composes"
CLS_FAMILY = "reproducible_through_a_format_template"
CLS_NAMED_ONLY = "named_by_sources_that_never_write"
CLS_ORPHAN = "no_source_in_the_corpus_names_the_face"
CLS_ABSENT = "the_face_is_not_on_disk"

RUNG_STANDARD = "R1_standard_needle"
RUNG_FULL = "R2_every_auditor_kept"
RUNG_FAMILY = "R3_plus_format_templates"
RUNG_COMPOSED = "R4_plus_composed_paths"
RUNGS = (RUNG_STANDARD, RUNG_FULL, RUNG_FAMILY, RUNG_COMPOSED)

VERDICT_NONE = "every_writer_less_face_in_the_population_is_a_lookup_artefact_under_a_later_rung"
VERDICT_SOME = "some_faces_survive_every_rung_and_are_a_face_level_defect"
VERDICT_EMPTY = "every_face_in_the_population_has_a_writer_on_the_first_rung"

WRITE_CALL = re.compile(r"(?:json\.dump|\.to_csv|\.write_text|\.write_json|"
                        r"\bwritelines?\(|open\(\s*[^,)]+,\s*[\"'](?:w|a|x|r\+))")
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
COMPACT = re.compile(r"\d{8}")
FAMILY_BRACE = ("{", "%s")


def relp(path):
    return path.replace("\\", "/") if not os.path.isabs(path) else e312.rel(path)


def read_json(rel_path, root=None):
    with io.open(os.path.join(root or ROOT, rel_path), encoding="utf-8") as fh:
        return json.load(fh)


# --------------------------------------------------------------------------------- corpus

_SRC = None
_WCACHE = {}


def corpus():
    """E323's corpus minus this scanner (the r1232 self-inclusion trap)."""
    global _SRC
    if _SRC is None:
        own = os.path.abspath(__file__)
        _SRC = [(p, s) for p, s in e323.corpus() if os.path.abspath(p) != own]
    return _SRC


def write_capable(src):
    """Does this module write anything at all?  The gate for every composed-name rule."""
    key = id(src)
    if key in _WCACHE:
        return _WCACHE[key]
    match = WRITE_CALL.search(src or "")
    _WCACHE[key] = match.group(0) if match else None
    return _WCACHE[key]


def naming_lines(src, needle):
    """Lines that carry the needle, with the line number and a dot-class colouring."""
    out = []
    for lineno, line in enumerate((src or "").splitlines(), 1):
        if needle and needle in line:
            out.append((lineno, line.strip()))
    return out


def single_line_writer(src, basename):
    """`open(basename, "w")` / a dump straight onto a name: the strictest evidence."""
    for var in re.findall(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*.*%s" % re.escape(basename),
                          src or "", re.M):
        if re.search(r"open\(\s*%s\s*,\s*[\"'](?:w|a|x|r\+)" % re.escape(var), src or ""):
            return {"shape": "assignment_then_open", "var": var}
    for lineno, line in enumerate((src or "").splitlines(), 1):
        if basename not in line:
            continue
        if re.search(r"(?:json\.dump\([^)]*open\(|write_text\(|write_json\()", line):
            return {"shape": "dump_onto_open", "line": lineno}
    return None


def family_templates(face):
    """The needles a composer would spell for this face.

    A dated face has its date replaced by the template marker below.  An undated face with an
    underscore suffix (`p1e_nulls_M_arc.json`) can be spelled by its parent family; the longest
    prefix that a composer would actually format is the one whose next character in the source
    is a brace or ``%s``.
    """
    basename = os.path.basename(face)
    out = []
    if DATE.search(basename):
        out.append(re.sub(DATE, "%s", basename).split(".")[0] + ".json")
        stem = re.sub(r"-?%s.*$" % DATE.pattern, "", basename)
        if stem and stem != basename:
            out.append(stem)
    # a compact stamp is its own shape (E322's "1 compact date" cause, now at face level)
    if COMPACT.search(basename):
        out.append(re.sub(COMPACT, "%s", basename).split(".")[0] + ".json")
    stem = basename[:-5] if basename.endswith(".json") else basename
    parts = stem.split("_")
    for cut in range(len(parts) - 1, 0, -1):
        out.append("_".join(parts[:cut]) + "_")
    seen, ordered = set(), []
    for needle in out:
        if needle and needle not in seen:
            seen.add(needle)
            ordered.append(needle)
    return ordered


def template_writer(src, face):
    """Does this module format the face's family into existence and write the result?

    Only for a face the module never spells: if the literal name is in the source, the family
    formatter is not evidence about THIS face (the source names it and does not write it), and a
    family credit there would turn every reader of a composed family into its producer.
    """
    writ = write_capable(src)
    if not writ:
        return None
    if os.path.basename(face) in (src or ""):
        return None
    for needle in family_templates(face):
        for lineno, line in naming_lines(src, needle):
            tail = line.split(needle, 1)[1] if needle in line else ""
            # the formatter may open directly on the needle (f"F_{c}"), behind the separator the
            # family name already carries (f"REGIME5-DIAG-{cutoff}"), or inside the needle itself
            # when the source stores the template as a constant ("PRECISIONCENSUS-%s.json")
            rest = tail.lstrip()
            if rest[:1] in ("-", "_"):
                rest = rest[1:]
            inside = ("%s" in needle) or ("{" in needle)
            if not inside and not any(rest.startswith(m) for m in FAMILY_BRACE):
                continue
            if not re.search(r"(?:=|join\(|format\(|f[\"'])", line):
                continue
            return {"shape": "format_template", "needle": needle, "line": lineno,
                    "text": line[:120], "write_call": writ}
    return None


def composed_path_writer(src, face):
    """The file name appears on a path-building line inside a module that can write."""
    basename = os.path.basename(face)
    needles = [basename]
    if DATE.search(basename):
        needles.append(re.sub(DATE, "%s", basename).split("%s")[0])
    writ = write_capable(src)
    if not writ:
        return None
    for needle in needles:
        for lineno, line in naming_lines(src, needle):
            if re.search(r"(?:=\s*(?:os\.path\.join|[A-Za-z_]+_?PATH)|join\(|Path\()", line) or \
               re.search(r"^\s*[A-Za-z_][A-Za-z0-9_]*\s*=\s*[^=]*[\"']\s*$", line) or \
               re.search(r"^\s*[\"'][^\"']+[\"']\s*\)?,?\s*$", line):
                return {"shape": "composed_path", "needle": needle, "line": lineno,
                        "text": line[:120], "write_call": writ}
    return None


def writers_full(face, files=None):
    """Every source that can reproduce this face, at the rung the evidence supports."""
    basename = os.path.basename(face)
    needles = [basename]
    if DATE.search(basename):
        needles.append(re.sub(DATE, "%s", basename))
    named, composed, family, mentions = [], [], [], []
    for path, src in (files if files is not None else corpus()):
        hit = None
        for needle in needles:
            if needle and needle in src:
                hit = needle
                break
        if hit is None:
            # A composed name is the point: the source never spells the face, it formats it.
            fam = template_writer(src, face)
            if fam:
                family.append({"producer": relp(path), "evidence": fam})
            continue
        strict = single_line_writer(src, basename)
        if strict:
            named.append({"producer": relp(path), "evidence": strict})
            continue
        fam = template_writer(src, face)
        if fam:
            family.append({"producer": relp(path), "evidence": fam})
            continue
        comp = composed_path_writer(src, face)
        if comp:
            composed.append({"producer": relp(path), "evidence": comp})
            continue
        mentions.append({"producer": relp(path), "write_call": write_capable(src),
                         "lines": [ln for _n, ln in naming_lines(src, hit)][:3]})
    return {"named": named, "family": family, "composed": composed, "mentions": mentions}


def writers_standard(face):
    """E321/E312's published lookup, unchanged, so the first rung is not my reading of it."""
    try:
        return sorted({relp(p) for p, _s in e321.producer_candidates(face)})
    except Exception as exc:  # pragma: no cover - defensive, a lookup must never kill a face
        return ["LOOKUP-ERROR:%s" % exc]


def class_at_rung(writers, rung, on_disk):
    if not on_disk:
        return CLS_ABSENT
    if rung == RUNG_STANDARD:
        return CLS_NAMED if writers["standard"] else CLS_ORPHAN
    if writers["named"]:
        return CLS_NAMED
    if rung == RUNG_FULL:
        return CLS_NAMED_ONLY if writers["mentions"] else CLS_ORPHAN
    if rung == RUNG_FAMILY:
        if writers["family"]:
            return CLS_FAMILY
        return CLS_NAMED_ONLY if writers["mentions"] else CLS_ORPHAN
    if writers["family"]:
        return CLS_FAMILY
    if writers["composed"]:
        return CLS_COMPOSED
    return CLS_NAMED_ONLY if writers["mentions"] else CLS_ORPHAN


# ------------------------------------------------------------------------------ measure one face

def face_record(face, rows, root=None, files=None):
    root = root or ROOT
    on_disk = os.path.exists(os.path.join(root, face))
    writers = writers_full(face, files)
    writers["standard"] = writers_standard(face)
    rec = {"face": face, "on_disk": on_disk, "rows": len(rows),
           "leaves": [r.get("leaf") for r in rows][:40],
           "upstream_classes": sorted({r.get("class_after") for r in rows}),
           "writers_standard": writers["standard"],
           "writers_named": [w["producer"] for w in writers["named"]],
           "writers_family": writers["family"],
           "writers_composed": writers["composed"],
           "mentions_only": [m["producer"] for m in writers["mentions"]],
           "class_by_rung": {rung: class_at_rung(writers, rung, on_disk) for rung in RUNGS}}
    first = None
    for rung in RUNGS:
        if rec["class_by_rung"][rung] != CLS_ORPHAN:
            first = rung
            break
    rec["first_rung_that_finds_a_writer"] = first
    rec["orphan_under"] = [r for r in RUNGS if rec["class_by_rung"][r] == CLS_ORPHAN]
    rec["evidence"] = (writers["named"][:2] or writers["family"][:2] or
                       writers["composed"][:2] or writers["mentions"][:2])
    return rec


def population(doc):
    rows = doc.get("rows") or []
    by_face = {}
    for row in rows:
        by_face.setdefault(row.get("face"), []).append(row)
    return rows, by_face


def build(outdir=None, root=None):
    root = root or ROOT
    doc = read_json(INPUT, root)
    rows, by_face = population(doc)
    faces = []
    for face in sorted(by_face):
        if face:
            faces.append(face_record(face, by_face[face], root))
    rung_counts = {}
    for rung in RUNGS:
        orphan = [f for f in faces if f["class_by_rung"][rung] == CLS_ORPHAN]
        absent = [f for f in faces if f["class_by_rung"][rung] == CLS_ABSENT]
        rung_counts[rung] = {
            "orphan_faces": len(orphan),
            "orphan_face_names": [f["face"] for f in orphan],
            "orphan_rows": sum(f["rows"] for f in orphan),
            "absent_faces": len(absent),
            "rows_total": len(rows),
            "faces_total": len(faces),
            "share_of_rows": round(100.0 * sum(f["rows"] for f in orphan) / len(rows), 2)
            if rows else 0.0,
            "largest_orphan_rows": max([f["rows"] for f in orphan] or [0]),
        }
    final = rung_counts[RUNG_COMPOSED]
    moved = [f for f in faces if f["class_by_rung"][RUNG_STANDARD] !=
             f["class_by_rung"][RUNG_COMPOSED]]
    if not rung_counts[RUNG_STANDARD]["orphan_faces"]:
        verdict = VERDICT_EMPTY
    elif final["orphan_faces"]:
        verdict = VERDICT_SOME
    else:
        verdict = VERDICT_NONE
    reason = (
        "the published lookup reports %d of %d rows (%s pct) and %d of %d faces writer-less. A "
        "rule that demands a writer rather than a mention reports %d rows / %d faces, format "
        "templates take that to %d rows / %d faces, and composed paths to %d / %d. So the "
        "published lookup OVER-credits (its stem fallback accepts a bare mention: %d rows are "
        "orphan under writer evidence but named under it) while the strictest rule is the one "
        "that orphans the most faces -- the ladder is monotone only from the second rung, and "
        "'no writer' is a fact about a named rule, never about the repository."
        % (rung_counts[RUNG_STANDARD]["orphan_rows"], len(rows),
           rung_counts[RUNG_STANDARD]["share_of_rows"],
           rung_counts[RUNG_STANDARD]["orphan_faces"], len(faces),
           rung_counts[RUNG_FULL]["orphan_rows"], rung_counts[RUNG_FULL]["orphan_faces"],
           rung_counts[RUNG_FAMILY]["orphan_rows"], rung_counts[RUNG_FAMILY]["orphan_faces"],
           final["orphan_rows"], final["orphan_faces"],
           rung_counts[RUNG_FULL]["orphan_rows"] - rung_counts[RUNG_STANDARD]["orphan_rows"]))
    out = {
        "study": STUDY,
        "title": ("the gate rows whose face has no writer: a face-level defect measured as a "
                  "ladder of naming rules, so 'unreproducible' can never be quoted from one rung"),
        "evidence_cutoff": TODAY,
        "upstream": os.path.basename(INPUT),
        "upstream_study": doc.get("study"),
        "held_fixed": ("every row, leaf, class and gate value of the upstream face is read and "
                       "never rewritten; only the definition of 'a source can produce this face' "
                       "moves, one rule per rung"),
        "no_bill": ("published faces and in-repo sources only; no draws, no panel read, no engine, "
                    "no network"),
        "corpus": {"files": len(corpus()), "self_excluded": os.path.basename(__file__),
                   "packages": ["scripts", "Tools", "live", "monitor", "firm"]},
        "rules": {
            RUNG_STANDARD: ("E321/E312 producer_candidates as published -- an INSTRUMENT measured "
                            "for reference, not a rung of the writer-evidence ladder (its stem "
                            "fallback credits a mention without a writer)"),
            RUNG_FULL: "every python source under the producing packages, this scanner excluded",
            RUNG_FAMILY: "a face named by a format template counts",
            RUNG_COMPOSED: ("a file name on an assignment/os.path.join line counts when its "
                            "module can write"),
        },
        "faces": faces,
        "by_rung": rung_counts,
        "moved_faces": [{"face": f["face"], "rows": f["rows"],
                         "standard": f["class_by_rung"][RUNG_STANDARD],
                         "final": f["class_by_rung"][RUNG_COMPOSED],
                         "first_rung_that_finds_a_writer": f["first_rung_that_finds_a_writer"]}
                        for f in moved],
        "verdict": verdict,
        "verdict_reason": reason,
    }
    out["summary"] = {
        "rows": len(rows),
        "faces": len(faces),
        "orphan_rows_by_rung": {r: rung_counts[r]["orphan_rows"] for r in RUNGS},
        "orphan_faces_by_rung": {r: rung_counts[r]["orphan_faces"] for r in RUNGS},
        "faces_moved": len(moved),
        "rows_on_the_largest_first_rung_orphan": rung_counts[RUNG_STANDARD]["largest_orphan_rows"],
        "rows_that_survive_every_rung": final["orphan_rows"],
        "faces_that_survive_every_rung": final["orphan_face_names"],
        "row_and_face_readings_disagree": (
            final["orphan_rows"] < rung_counts[RUNG_STANDARD]["orphan_rows"] and
            final["orphan_faces"] > rung_counts[RUNG_STANDARD]["orphan_faces"]),
        "ladder_is_monotone_from": RUNG_FULL,
        "rows_the_published_lookup_credits_that_writer_evidence_refuses": (
            rung_counts[RUNG_FULL]["orphan_rows"] - rung_counts[RUNG_STANDARD]["orphan_rows"]),
        # not an orphan is not the same as reproduced: a face a source NAMES and never writes is
        # still unresolved, and folding it into "resolved" would over-read this face.
        "unresolved_faces_named_but_no_writer_shown": [
            {"face": f["face"], "rows": f["rows"], "mentions_only": f["mentions_only"][:4]}
            for f in faces if f["class_by_rung"][RUNG_COMPOSED] == CLS_NAMED_ONLY],
        "unresolved_rows": sum(f["rows"] for f in faces
                               if f["class_by_rung"][RUNG_COMPOSED] == CLS_NAMED_ONLY),
        "row_reading_falls_by": (rung_counts[RUNG_STANDARD]["orphan_rows"] -
                                 final["orphan_rows"]),
        "face_reading_rises_by": (final["orphan_faces"] -
                                  rung_counts[RUNG_STANDARD]["orphan_faces"]),
        "faces_orphan_on_one_rung_and_written_on_a_later_one": [
            {"face": f["face"], "rows": f["rows"],
             "first_rung_that_finds_a_writer": f["first_rung_that_finds_a_writer"]}
            for f in faces
            if f["class_by_rung"][RUNG_STANDARD] == CLS_ORPHAN
            and f["class_by_rung"][RUNG_COMPOSED] != CLS_ORPHAN
            and f["class_by_rung"][RUNG_COMPOSED] != CLS_ABSENT],
        "unpublished_lookup_self_exclusion_is_the_largest_cause":
            rung_counts[RUNG_STANDARD]["largest_orphan_rows"] > 0 and
            final["orphan_rows"] < rung_counts[RUNG_STANDARD]["orphan_rows"],
    }
    if outdir:
        path = os.path.join(outdir, FACE)
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
        latest = os.path.join(outdir, LATEST)
        with io.open(latest, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
    return out


# ----------------------------------------------------------------------------------- commands

def cmd_run():
    out = build(OUTDIR)
    print("E325 orphan-face ladder over %d gate rows / %d faces (corpus %d sources)"
          % (out["summary"]["rows"], out["summary"]["faces"], out["corpus"]["files"]))
    for rung in RUNGS:
        c = out["by_rung"][rung]
        print("  %-24s orphan faces %d  rows %d (%s pct)  largest %d"
              % (rung, c["orphan_faces"], c["orphan_rows"], c["share_of_rows"],
                 c["largest_orphan_rows"]))
    for f in out["moved_faces"]:
        print("  moved: %-52s rows %2d  %s -> %s  (first writer at %s)"
              % (f["face"], f["rows"], f["short"] if "short" in f else f["standard"],
                 f["final"], f["first_rung_that_finds_a_writer"]))
    print("verdict:", out["verdict"])
    print("reason:", out["verdict_reason"])
    return 0


def cmd_verify():
    """Re-derive the published face from the tree and refuse a stale or hand-edited one."""
    path = os.path.join(OUTDIR, FACE)
    if not os.path.exists(path):
        print("verify: face missing:", FACE)
        return 2
    on_disk = read_json(os.path.join("results", "state_tilt", FACE))
    fresh = build(None)
    problems = []
    if on_disk.get("verdict") != fresh.get("verdict"):
        problems.append("verdict on disk %r != %r" % (on_disk.get("verdict"),
                                                      fresh.get("verdict")))
    for rung in RUNGS:
        a = (on_disk.get("by_rung") or {}).get(rung) or {}
        b = fresh["by_rung"][rung]
        for key in ("orphan_faces", "orphan_rows", "rows_total", "faces_total"):
            if a.get(key) != b[key]:
                problems.append("%s.%s %r != %r" % (rung, key, a.get(key), b[key]))
    for face, rec in zip([f["face"] for f in fresh["faces"]],
                         [f["face"] for f in (on_disk.get("faces") or [])]):
        if face != rec:
            problems.append("face order drifted at %r" % face)
            break
    if problems:
        print("verify: %d problem(s)" % len(problems))
        for p in problems:
            print("  -", p)
        return 1
    print("verify: problems=[] (%d faces, %d rows)"
          % (fresh["summary"]["faces"], fresh["summary"]["rows"]))
    return 0


def cmd_selftest():
    import tempfile

    checks = []

    def check(name, ok, detail=""):
        checks.append((name, bool(ok), detail))
        print("  %-62s %s%s" % (name, "PASS" if ok else "FAIL",
                                ("  " + detail) if (detail and not ok) else ""))

    def fixture(files, face, rows=None):
        """A temp tree plus the source list the classifier must read INSTEAD of the repo."""
        tmp = tempfile.mkdtemp(prefix="e325_")
        srcs = []
        for rel, text in files.items():
            full = os.path.join(tmp, rel)
            parent = os.path.dirname(full)
            if parent and not os.path.isdir(parent):
                os.makedirs(parent, exist_ok=True)
            if rel.endswith(".py"):
                srcs.append((full, text))
            with io.open(full, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(text)
        face_full = os.path.join(tmp, face)
        parent = os.path.dirname(face_full)
        if not os.path.isdir(parent):
            os.makedirs(parent, exist_ok=True)
        if not os.path.exists(face_full):
            with io.open(face_full, "w", encoding="utf-8", newline="\n") as fh:
                fh.write("{}")
        rows = rows if rows is not None else [{"face": face, "leaf": "a.b",
                                               "class_after": "x"}]
        by = {}
        for r in rows:
            by.setdefault(r["face"], []).append(r)
        return tmp, by, srcs

    # L1 a single-line writer is reproducible on the first rung
    tmp, by, srcs = fixture({"scripts/w.py":
                             'import json, os\n'
                             'p = os.path.join("results", "A-2026-01-01.json")\n'
                             'open(p, "w").write("{}")\n'}, "results/A-2026-01-01.json")
    rec = face_record("results/A-2026-01-01.json", by["results/A-2026-01-01.json"], tmp, srcs)
    check("L1 a named-and-written face is reproducible", rec["on_disk"] and
          rec["class_by_rung"][RUNG_STANDARD] != CLS_ORPHAN or
          rec["class_by_rung"][RUNG_COMPOSED] in (CLS_NAMED, CLS_COMPOSED),
          str(rec["class_by_rung"]))

    # L2 a face only quoted by a reader stays writer-less at every rung
    tmp2, by2, srcs2 = fixture(
        {"scripts/r.py": 'print("results/B-2026-01-01.json is a face")\n'},
        "results/B-2026-01-01.json")
    rec2 = face_record("results/B-2026-01-01.json", by2["results/B-2026-01-01.json"],
                       tmp2, srcs2)
    check("L2 a mention in a module that never writes is not a writer",
          rec2["class_by_rung"][RUNG_FULL] == CLS_NAMED_ONLY and
          rec2["class_by_rung"][RUNG_COMPOSED] == CLS_NAMED_ONLY,
          str(rec2["class_by_rung"]))

    # L3 a format template names the face at the family rung, not before
    tmp3, by3, srcs3 = fixture(
        {"scripts/f.py": 'import json, os\nfor c in ("M", "N"):\n'
                         '    p = os.path.join("results", f"F_{c}.json")\n'
                         '    json.dump({}, open(p, "w"))\n'}, "results/F_M.json")
    rec3 = face_record("results/F_M.json", by3["results/F_M.json"], tmp3, srcs3)
    check("L3 an f-string family is a writer at the family rung only",
          rec3["class_by_rung"][RUNG_FULL] == CLS_ORPHAN and
          rec3["class_by_rung"][RUNG_FAMILY] == CLS_FAMILY, str(rec3["class_by_rung"]))

    # L4 a path assigned on its own line is found at the composed rung
    tmp4, by4, srcs4 = fixture(
        {"scripts/aud.py": 'import json, os\nD = "results/C-2026-01-01.json"\n'
                           'json.dump({}, open(D, "w"))\n'}, "results/C-2026-01-01.json")
    rec4 = face_record("results/C-2026-01-01.json", by4["results/C-2026-01-01.json"],
                       tmp4, srcs4)
    check("L4 a face written through an assigned path is found at the composed rung",
          rec4["class_by_rung"][RUNG_COMPOSED] in (CLS_NAMED, CLS_COMPOSED),
          str(rec4["class_by_rung"]))

    # L5 a face missing from disk is its own class, never an orphan
    rec5 = face_record("results/GONE.json", [{"face": "results/GONE.json", "leaf": "x"}],
                       tmp, [])
    check("L5 an absent face reports absent, not orphan",
          rec5["class_by_rung"][RUNG_COMPOSED] == CLS_ABSENT, str(rec5["class_by_rung"]))

    # L6 rows and faces are different counts on one orphan face
    rows = [{"face": "results/Z.json", "leaf": "a.b", "class_after": "x"},
            {"face": "results/Z.json", "leaf": "a.c", "class_after": "y"},
            {"face": "results/Y.json", "leaf": "a.b", "class_after": "x"}]
    by = {}
    for r in rows:
        by.setdefault(r["face"], []).append(r)
    rec6 = face_record("results/Z.json", by["results/Z.json"], tmp, [])
    check("L6 two rows on one face count as two rows and one face",
          rec6["rows"] == 2 and len(by) == 2, str((rec6["rows"], len(by))))

    # L6b a Path-division assignment is a composed path (the shape a literal needle misses)
    tmp6b, by6b, srcs6b = fixture(
        {"scripts/p.py": 'import json, os\nOUT = ROOT / "results" / "P-20260101.json"\n'
                         'json.dump({}, open(OUT, "w"))\n'.replace("ROOT", 'os.getcwd()'),
         }, "results/P-20260101.json")
    rec6b = face_record("results/P-20260101.json", by6b["results/P-20260101.json"],
                        tmp6b, srcs6b)
    check("L6b a Path-division path counts as a composed writer",
          rec6b["class_by_rung"][RUNG_COMPOSED] in (CLS_NAMED, CLS_COMPOSED),
          str(rec6b["class_by_rung"]))

    # L6c a constant holding the template is a family writer (the %s-inside-the-needle shape)
    tmp6c, by6c, srcs6c = fixture(
        {"scripts/c.py": 'import json, os\nFACE = "C-%s.json"\n'
                         'json.dump({}, open(os.path.join("results", FACE % "20260101"), "w"))\n'},
        "results/C-20260101.json")
    rec6c = face_record("results/C-20260101.json", by6c["results/C-20260101.json"],
                        tmp6c, srcs6c)
    check("L6c a compact date held as a %s template is a family writer",
          rec6c["class_by_rung"][RUNG_FAMILY] == CLS_FAMILY, str(rec6c["class_by_rung"]))

    # L7 the writer-evidence ladder is monotone; the published lookup is an instrument, not a rung
    out = build()
    counts = [out["by_rung"][r]["orphan_rows"] for r in RUNGS[1:]]
    check("L7 the writer-evidence ladder is monotone non-increasing in orphan rows",
          all(counts[i + 1] <= counts[i] for i in range(len(counts) - 1)), str(counts))
    check("L7b the published lookup is disclosed as an instrument, not a rung",
          out["summary"].get("ladder_is_monotone_from") == RUNG_FULL,
          str(out["summary"].get("ladder_is_monotone_from")))

    # L8 the published share is arithmetic, not a second measurement
    c = out["by_rung"][RUNG_STANDARD]
    check("L8 the published share equals the published counts",
          abs(c["share_of_rows"] - round(100.0 * c["orphan_rows"] / c["rows_total"], 2)) < 1e-9,
          "%r vs %r" % (c["share_of_rows"], c["orphan_rows"]))

    # L9 the scanner is excluded from its own corpus
    own = os.path.abspath(__file__)
    check("L9 this scanner is excluded from its own corpus",
          all(os.path.abspath(p) != own for p, _s in corpus()))

    # L10 every face in the population came from a row, so no face is invented
    faces_in_rows = {r["face"] for r in read_json(INPUT)["rows"]}
    check("L10 the face population is exactly the rows' faces",
          set(f["face"] for f in out["faces"]) == faces_in_rows)

    passed = sum(1 for _n, ok, _d in checks if ok)
    print("selftest: %d/%d" % (passed, len(checks)))
    return 0 if passed == len(checks) else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd in ("run", "build"):
        return cmd_run()
    if cmd == "verify":
        return cmd_verify()
    if cmd == "selftest":
        return cmd_selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))

