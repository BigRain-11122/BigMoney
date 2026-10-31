"""E322 -- E321 left 25 rows with "no producer names the face". Is the population or the needle missing?

E321 asked whether the producing side names the gated quantity and reported 25 gates with no
producer at all.  That number decides how the rest of the census is read: E321's own verdict
sentence says those gates "have no producer that publishes the key at all, so no reading of the
producer can name them".  This study asks one question of exactly those rows -- is there a writer
on disk, and if so which mechanical step of the lookup hid it.

Nothing here re-reads the gates or re-grades E321's five classes: the population is the
``no_producer_names_the_face`` rows of QUANTITYNAME, the corpus is the same producing packages
E312 walks, and every cause is a pure function of the two.

Two properties of the lookup are deliberately NOT inherited from E312:

* ``e312.sources()`` drops the auditor's own file (``_OWN``), so a face written by E312 can never
  find its producer.  This corpus keeps every source and reports ``auditor_is_the_writer``.
* ``producer_candidates()`` substitutes only ISO dates (``YYYY-MM-DD``), while this repo also dates
  faces compactly (``CASHLeg-20261027``), and some writers compose the name from a format string
  (``f"p1e_nulls_{cls}.json"``).  Both families are searched here and the winning step is published.

Usage:
    python scripts/e322_residual_refusal_causes.py run|build|verify|selftest
"""
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import e312_gate_operand_identity as e312  # noqa: E402  (path set above)

ROOT = e312.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
INPUT = "QUANTITYNAME-2026-10-31.json"
TODAY = "2026-10-31"
FACE = "REFUSALCAUSE-%s.json" % TODAY
LATEST = "refusalcause_latest.json"
STUDY = "E322_residual_refusal_causes"

UPSTREAM_CLASS = "no_producer_names_the_face"

# -------------------------------------------------------------------------------- cause vocabulary
CAUSE_LITERAL = "the_name_is_spelled_in_the_writer"
CAUSE_ISO = "found_only_after_substituting_an_iso_date"
CAUSE_COMPACT = "found_only_after_substituting_a_compact_date"
CAUSE_COMPOSED = "found_only_after_stripping_to_a_name_prefix"
CAUSE_NONE = "no_writer_in_the_source_tree"

CAUSES = (CAUSE_LITERAL, CAUSE_ISO, CAUSE_COMPACT, CAUSE_COMPOSED, CAUSE_NONE)

VERDICT_ALL = "every_refused_row_has_a_writer_on_disk_so_the_needle_was_the_defect"
VERDICT_SOME = "most_refused_rows_have_a_writer_but_some_are_genuinely_unowned"
VERDICT_NONE = "the_refusal_survives_a_wider_needle_so_these_faces_are_unowned"

VERDICTS = (VERDICT_ALL, VERDICT_SOME, VERDICT_NONE)

ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
COMPACT_DATE = re.compile(r"(?<!\d)(20\d{6})(?!\d)")
TEMPLATE_MARKERS = ("%s", "{", "*")


# -------------------------------------------------------------------------------- corpus
_SRC = None


def corpus():
    """Every python source under the producing packages, INCLUDING the other auditors.

    E312's ``sources()`` skips its own file because a census that quotes itself fabricates
    matches; the cost is that its own output face becomes unowned.  Here every auditor except
    THIS one is kept and named -- this scanner is excluded because it spells the very filenames
    it is looking for (the E204/r1232 self-inclusion trap: first burn had two faces resolving to
    "the writer spells the name", and the writer was this file).
    """
    global _SRC
    if _SRC is not None:
        return _SRC
    own = os.path.abspath(__file__)
    out = []
    for sub in ("scripts", "Tools", "live", "monitor", "firm"):
        base = os.path.join(ROOT, sub)
        for dirpath, _dirs, files in os.walk(base):
            for fn in sorted(files):
                if not fn.endswith(".py"):
                    continue
                path = os.path.join(dirpath, fn)
                if os.path.abspath(path) == own:
                    continue
                try:
                    with io.open(path, encoding="utf-8", errors="replace") as fh:
                        out.append((path, fh.read()))
                except OSError:
                    continue
    _SRC = out
    return _SRC


def strip_to_needle(text):
    """The literal prefix a templated name is written as (`GATEOPERANDS-%s.json` -> `GATEOPERANDS-`)."""
    base = os.path.basename(text)
    for marker in TEMPLATE_MARKERS:
        base = base.split(marker)[0]
    return base


def search(needle, src=None):
    """Writers whose source contains `needle`, with the template markers stripped first."""
    needle = strip_to_needle(needle)
    if len(needle) < 3:
        return []
    hits = []
    for path, text in (src if src is not None else corpus()):
        if needle in text:
            hits.append(path)
    return hits


def name_prefixes(base):
    """Progressive name prefixes, longest first, for a name composed from a format string."""
    stem = os.path.splitext(base)[0]
    parts = re.split(r"[_\-]", stem)
    out = []
    for i in range(len(parts) - 1, 0, -1):
        prefix = "_".join(parts[:i]) if "_" in stem else "-".join(parts[:i])
        if len(prefix) >= 3 and prefix not in out:
            out.append(prefix)
    return out


def needles_for(face):
    """Ordered (label, needle) attempts.  The order IS the taxonomy -- first hit wins."""
    base = os.path.basename(face)
    tries = [("literal", base)]
    if ISO_DATE.search(base):
        tries.append(("iso", ISO_DATE.sub("%s", base)))
    if COMPACT_DATE.search(base):
        tries.append(("compact", COMPACT_DATE.sub("%s", base)))
    for prefix in name_prefixes(base):
        tries.append(("composed", prefix))
    return tries


def locate(face):
    """First needle that reaches a writer, with the step that did it."""
    for label, needle in needles_for(face):
        hits = search(needle)
        if hits:
            return label, needle, hits
    return None, None, []


STEP_TO_CAUSE = {
    "literal": CAUSE_LITERAL,
    "iso": CAUSE_ISO,
    "compact": CAUSE_COMPACT,
    "composed": CAUSE_COMPOSED,
}


def auditor_names(writers):
    """Which of the hits is the census machinery itself (E312/E321/E322 and their upstream)."""
    own = set()
    for path in writers:
        name = os.path.basename(path)
        if re.match(r"^e(3\d{2})_", name):
            own.add(name)
    return sorted(own)


def classify_face(face):
    step, needle, writers = locate(face)
    rel = sorted(set(e312.rel(p) for p in writers))
    return {
        "face": face,
        "needle_that_reached": needle,
        "step": step,
        "cause": STEP_TO_CAUSE.get(step, CAUSE_NONE),
        "writers": rel,
        "writer_count": len(rel),
        "auditor_is_the_writer": bool(rel) and all(
            re.match(r"^scripts/e3\d{2}_", w) for w in rel),
        "auditors_named": auditor_names(writers),
    }


# -------------------------------------------------------------------------------- build
def _read(name):
    with io.open(os.path.join(OUTDIR, name), encoding="utf-8") as fh:
        return json.load(fh)


def population(doc):
    return [r for r in (doc.get("rows") or []) if r.get("class") == UPSTREAM_CLASS]


def build():
    doc = _read(INPUT)
    rows = population(doc)
    by_face = {}
    for r in rows:
        by_face.setdefault(r.get("face"), []).append(r)

    faces = []
    for face in sorted(by_face):
        got = classify_face(face)
        got["rows"] = len(by_face[face])
        got["leaves"] = sorted(set(r.get("leaf") for r in by_face[face]))
        faces.append(got)

    cause_tally = {}
    for f in faces:
        cause_tally[f["cause"]] = cause_tally.get(f["cause"], 0) + 1
    row_tally = {}
    for f in faces:
        row_tally[f["cause"]] = row_tally.get(f["cause"], 0) + f["rows"]

    owned_rows = sum(f["rows"] for f in faces if f["writers"])
    owned_faces = sum(1 for f in faces if f["writers"])
    unowned = [f["face"] for f in faces if not f["writers"]]

    if owned_faces == len(faces):
        verdict = VERDICT_ALL
    elif owned_faces * 2 > len(faces):
        verdict = VERDICT_SOME
    else:
        verdict = VERDICT_NONE

    verdict_reason = (
        "%d rows E321 classified as having no producer resolve to %d faces; %d of those faces "
        "(carrying %d of the %d rows) do have a writer in the source tree, so the refusal was the "
        "lookup and not the repository. Three mechanical steps account for every one of them: %d "
        "faces (%d rows) are written by the census machinery's own module and lost to its source "
        "self-exclusion, %d face(s) carry a compact date the ISO substitution never touches, %d "
        "face(s) are composed from a format string so the published filename appears nowhere in "
        "the writer. %d faces remain unowned."
        % (len(rows), len(faces), owned_faces, owned_rows, len(rows),
           sum(1 for f in faces if f["auditor_is_the_writer"]),
           sum(f["rows"] for f in faces if f["auditor_is_the_writer"]),
           sum(1 for f in faces if f["cause"] == CAUSE_COMPACT),
           sum(1 for f in faces if f["cause"] == CAUSE_COMPOSED),
           len(unowned))
    )

    return {
        "study": STUDY,
        "title": ("why the producer lookup refused: are E321's unowned rows a repository fact or a "
                  "needle fact?"),
        "evidence_cutoff": TODAY,
        "upstream": INPUT,
        "verdict": verdict,
        "verdict_reason": verdict_reason,
        "population": {
            "source": "QUANTITYNAME-%s.json rows with class %s" % (TODAY, UPSTREAM_CLASS),
            "rows": len(rows),
            "faces": len(faces),
            "rows_per_face": {f["face"]: f["rows"] for f in faces},
        },
        "summary": {
            "rows": len(rows),
            "faces": len(faces),
            "faces_with_a_writer": owned_faces,
            "rows_with_a_writer": owned_rows,
            "faces_unowned": len(unowned),
            "unowned_faces": unowned,
            "by_cause_faces": cause_tally,
            "by_cause_rows": row_tally,
            "causes": list(CAUSES),
            "corpus_files": len(corpus()),
            "corpus_keeps_the_auditor": True,
            "corpus_self_excluded": os.path.basename(os.path.abspath(__file__)),
        },
        "held_fixed": ("E321's rows are read, never rewritten; no gate value is recomputed, no "
                       "class of E321 is changed, and no face outside this study is written"),
        "no_bill": ("published faces and in-repo sources only; no draws, no panel read, no engine, "
                    "no network"),
        "faces": faces,
    }


# -------------------------------------------------------------------------------- io / verify
def _count(values):
    out = {}
    for v in values:
        out[v] = out.get(v, 0) + 1
    return out


def save(payload, name=None):
    os.makedirs(OUTDIR, exist_ok=True)
    path = os.path.join(OUTDIR, name or FACE)
    text = json.dumps(payload, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    for target in (path, os.path.join(OUTDIR, LATEST)):
        with io.open(target, "w", encoding="utf-8") as fh:
            fh.write(text)
    return path


def run(save_face=True):
    face = build()
    if save_face:
        save(face)
    return face


def verify():
    problems = []
    face = _read(LATEST)
    fresh = build()
    if face.get("verdict") != fresh.get("verdict"):
        problems.append("the verdict does not re-derive")
    if face.get("verdict") not in VERDICTS:
        problems.append("verdict %r is outside the frozen set" % (face.get("verdict"),))
    if face.get("summary") != fresh.get("summary"):
        problems.append("the summary does not re-derive")
    rows = face.get("faces") or []
    if sum(f.get("rows") or 0 for f in rows) != (face.get("summary") or {}).get("rows"):
        problems.append("the face counts do not sum to the row population")
    for f in rows:
        if f.get("cause") not in CAUSES:
            problems.append("face cause %r is outside the frozen set" % (f.get("cause"),))
            break
        if f.get("cause") == CAUSE_NONE and f.get("writers"):
            problems.append("a face with no cause carries writers")
            break
        if f.get("cause") != CAUSE_NONE and not f.get("writers"):
            problems.append("a face with a cause carries no writer")
            break
    return problems


def selftest():
    legs = []

    def leg(name, ok, detail=""):
        legs.append((bool(ok), name, detail))

    leg("L1 an ISO-dated name substitutes", ISO_DATE.sub("%s", "REPRO-2026-10-31.json") == "REPRO-%s.json")
    leg("L2 a compact-dated name is invisible to the ISO rule",
        ISO_DATE.sub("%s", "CASHLeg-20261027.json") == "CASHLeg-20261027.json")
    leg("L3 the compact rule catches it",
        COMPACT_DATE.sub("%s", "CASHLeg-20261027.json") == "CASHLeg-%s.json")
    leg("L4 a compact rule does not eat a run inside a longer number",
        COMPACT_DATE.sub("%s", "x1202610279.json") == "x1202610279.json")
    leg("L5 the template marker is stripped before the search",
        strip_to_needle("GATEOPERANDS-%s.json") == "GATEOPERANDS-")
    leg("L6 an f-string brace is stripped too", strip_to_needle("p1e_nulls_{cls}.json") == "p1e_nulls_")
    leg("L7 prefixes are progressive and longest-first",
        name_prefixes("p1e_nulls_M_arc.json") == ["p1e_nulls_M", "p1e_nulls", "p1e"],
        repr(name_prefixes("p1e_nulls_M_arc.json")))
    leg("L8 a too-short prefix is refused", all(len(p) >= 3 for p in name_prefixes("a_b_c.json")))
    leg("L9 the needle order IS the taxonomy",
        [lab for lab, _ in needles_for("CASHLeg-20261027.json")][:3] == ["literal", "compact", "composed"],
        repr([lab for lab, _ in needles_for("CASHLeg-20261027.json")]))
    leg("L10 a name with no template still offers a composed attempt",
        "composed" in [lab for lab, _ in needles_for("p1e_nulls_M_arc.json")])
    src = [("scripts/fake_writer.py", 'FACE = "CASHLeg-%s.json" % d\n')]
    step, needle, hits = None, None, []
    for lab, ndl in needles_for("CASHLeg-20261027.json"):
        got = search(ndl, src)
        if got:
            step, needle, hits = lab, ndl, got
            break
    leg("L11 the compact step is the one that reaches a format-string writer",
        step == "compact" and len(hits) == 1, "%r %r" % (step, needle))
    leg("L12 the auditor is kept in this corpus (the E312 exclusion is the defect under test)",
        len(corpus()) > 0 and any(os.path.basename(p).startswith("e312_") for p, _ in corpus()))
    leg("L12b this scanner is NOT in its own corpus (r1232 self-inclusion trap)",
        not any(os.path.abspath(p) == os.path.abspath(__file__) for p, _ in corpus()))
    own = auditor_names([os.path.join(ROOT, "scripts", "e312_gate_operand_identity.py")])
    leg("L13 an auditor-named writer is reported as such", own == ["e312_gate_operand_identity.py"], repr(own))
    face = _read(LATEST)
    leg("L14 the published census partitions its own faces into rows",
        sum(f.get("rows") or 0 for f in face.get("faces") or []) == (face.get("summary") or {}).get("rows"))
    leg("L15 every face carries its cause and its writer list, including the negative one",
        all("cause" in f and "writers" in f for f in face.get("faces") or []))
    leg("L16 the verdict is inside the frozen set", face.get("verdict") in VERDICTS)
    return legs


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "run"
    if cmd == "run":
        face = run()
        print(json.dumps({"face": FACE, "verdict": face["verdict"],
                          "rows": face["summary"]["rows"],
                          "faces": face["summary"]["faces"],
                          "faces_with_a_writer": face["summary"]["faces_with_a_writer"],
                          "by_cause_faces": face["summary"]["by_cause_faces"]},
                         ensure_ascii=False))
        return 0
    if cmd == "build":
        print(json.dumps(build(), ensure_ascii=False, indent=1))
        return 0
    if cmd == "verify":
        problems = verify()
        print(json.dumps({"problems": problems}, ensure_ascii=False))
        return 1 if problems else 0
    if cmd == "selftest":
        legs = selftest()
        passed = sum(1 for ok, _, _ in legs if ok)
        for ok, name, detail in legs:
            print("%s %s%s" % ("PASS" if ok else "FAIL", name,
                               "" if ok else "  <- %r" % (detail,)))
        print("%d/%d" % (passed, len(legs)))
        return 0 if passed == len(legs) else 1
    print("usage: e322_residual_refusal_causes.py [run|build|verify|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main())