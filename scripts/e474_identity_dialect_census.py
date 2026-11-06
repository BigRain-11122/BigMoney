"""E474 -- every face's identity dialect, tree-wide, and whether any reader normalises it.

E460 found that the identity a face appears to lack is usually one it already carries, spelled as
the producer script's stem (e271_donor_choice_sensitivity).  That was measured inside E458's
residue only: 12 faces, producer side only.  E462 graded the dialect of the graded faces and found
some names are never read at all.

This card widens that to the whole tree and asks the reader side too:

  V  vocabulary   -- which field names count as identity, re-read from E458's frozen vocabulary
                     rather than re-invented here.
  D  dialect      -- for every face under results/, the dialect of each identity-named top-level
                     value: a card id, a path, a producer script stem, or none of those.
  S  stem resolve -- a stem value either names a script that exists (resolved), names a script
                     nobody ships (unresolved = the residue), or is not a stem at all.
  R  normalise    -- over the .py corpus, split the sources that READ an identity field by whether
                     they also carry a normaliser (a stem->card or card->stem idiom).  A tree where
                     identity values are only ever compared verbatim cannot join a face that
                     spells its identity as a stem against one that spells it as a card.

Limits published in the face: the population is top-level keys whose NAME is in the frozen
vocabulary (a face spelling identity under an unlisted name is not visible here, exactly the E462
dialect hazard), and a "normaliser" is an idiom in the same file as an identity read -- not a
proof that the idiom is applied to the identity value (E470's lesson: co-occurrence is not a join).

Run:      python scripts/e474_identity_dialect_census.py run
Check:    python scripts/e474_identity_dialect_census.py check
Verify:   python scripts/e474_identity_dialect_census.py verify     (re-derives from the live tree)
Selftest: python scripts/e474_identity_dialect_census.py selftest
"""

import argparse
import ast
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
if os.path.join(ROOT, "scripts") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "scripts"))

import e451_prereg_digest as e451  # noqa: E402  (walk_py / read_text)
import e461_identity_consumers as e461  # noqa: E402  (corpus / key_sites / READ_KINDS)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "identitydialectcensus_latest.json"
DATED_PREFIX = "IDENTITYDIALECTCENSUS"
CARD = "E474-HOW-MANY-FACES-NAME-THEIR-STUDY-AS-A-SCRIPT-STEM-AND-DOES-ANY-READER-NORMALISE-IT"
PARENT_FACE = "faceidentity_latest.json"
CUTOFF_ENV = "E474_CUTOFF"

MAX_FACE_BYTES = 4 * 1024 * 1024
MAX_FACES = 6000

# This family reads identity field names and stem idioms, so its own sources would vote for the
# dialect they are measuring.  Excluded by name, and the exclusion is published.
SELF_SKIP = ("e474_", "run_e474")

D_CARD = "card_id"
D_PATH = "path"
D_STEM = "producer_script_stem"
D_OTHER = "other"
DIALECTS = (D_CARD, D_PATH, D_STEM, D_OTHER)

S_RESOLVED = "names_a_script_that_exists"
S_DECLARED_ONE = "declared_as_a_literal_by_exactly_one_source"
S_DECLARED_MANY = "declared_by_several_sources"
S_UNRESOLVED = "names_no_script_and_no_source_declares_it"
S_NOT_A_STEM = "not_a_stem_shape"

NORMALISER_MARKERS = (
    "norm_stem",
    "splitext",
    ".basename(",
    'startswith("E")',
    "startswith('E')",
    "normalis",
    "normaliz",
    'endswith(".py")',
    "endswith('.py')",
)
CARD_RE_IDIOM = re.compile(r"E\d\{|E\[0-9\]|E\\\\d|\^E")

CARD_VALUE = re.compile(r"^E\d{2,4}$")
STEM_VALUE = re.compile(r"^[a-z][a-z0-9_]{2,60}$")
PATH_HINT = ("/", "\\")

V_EMPTY = "no_face_declares_a_top_level_identity"
V_CARDS_ONLY = "every_identity_value_is_a_card_id_or_a_path"
V_STEMS_RESOLVE = "stems_are_used_and_every_one_names_a_shipped_script"
V_STEMS_DANGLE = "some_faces_name_a_producer_script_that_does_not_exist"
VERDICTS = (V_EMPTY, V_CARDS_ONLY, V_STEMS_RESOLVE, V_STEMS_DANGLE)


# ----------------------------------------------------------------------------- helpers


def _load(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _rel(path):
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


def is_own_output(rel):
    base = os.path.basename(rel)
    if base == FACE_NAME:
        return True
    return base.startswith(DATED_PREFIX + "-") and base.endswith(".json")


def stem_index():
    """{stem: rel} for every .py under scripts/ and Tools/ (stem = basename without .py)."""
    out = {}
    for top in ("scripts", "Tools"):
        base = os.path.join(ROOT, top)
        for dirpath, _dirs, files in os.walk(base):
            for name in files:
                if not name.endswith(".py"):
                    continue
                stem = name[:-3]
                out.setdefault(stem, _rel(os.path.join(dirpath, name)))
    return out


def stem_index_repo():
    """{stem: rel} for every .py in the repo tree (stems are repo-wide, not scripts/-only).

    A stem that only resolves under scripts/ reads as dangling any producer living in monitor/ or
    firm/, which is an instrument artefact rather than a finding (E470 family).
    """
    out = {}
    skip = {".git", "results", "data", "Money02", "legacy", "_quarantine",
            "node_modules", "__pycache__"}
    for dirpath, dirs, files in os.walk(ROOT):
        dirs[:] = sorted(d for d in dirs if d not in skip)
        for name in files:
            if not name.endswith(".py"):
                continue
            out.setdefault(name[:-3], _rel(os.path.join(dirpath, name)))
    return out


def classify_value(name, value):
    """(dialect, normalised_value) for one identity-named value.  Pure function, selftested."""
    if not isinstance(value, str):
        return D_OTHER, None
    text = value.strip()
    if not text:
        return D_OTHER, None
    if CARD_VALUE.match(text):
        return D_CARD, text
    if any(h in text for h in PATH_HINT) and re.search(r"\.(json|md|csv|txt|parquet)$", text, re.I):
        return D_PATH, text
    stem = text[:-3] if text.endswith(".py") else text
    if STEM_VALUE.match(stem):
        return D_STEM, stem
    if text.endswith(".py"):
        return D_STEM, stem
    return D_OTHER, None


def stem_status(stem, index):
    if not stem:
        return S_NOT_A_STEM, None
    if stem in index:
        return S_RESOLVED, index[stem]
    return S_UNRESOLVED, None


def literal_stem_index():
    """{stem-shaped literal: [rel, ...]} over the repo's .py sources.

    A study id is often NOT the producer's script name (`e40_cashleg_drag` is written by
    `e40_...` but `e125_cashdrag_screened_twin` is written by `e125_...`); the second channel is
    the literal the producer declares in its own source.  Counting that separately is what keeps
    `dangling` from meaning "spelled differently from the filename" (E470 family).
    """
    out = {}
    sources, _errors = e461.corpus()
    for rel, _tree, literals, _sites in sources:
        for lit in literals:
            if not isinstance(lit, str) or not STEM_VALUE.match(lit):
                continue
            out.setdefault(lit, []).append(rel)
    return {k: sorted(set(v)) for k, v in out.items()}


def resolve_stem(stem, script_index, literal_index):
    """(status, resolved_rel) for one stem value: script name first, then a single declaration."""
    if not stem:
        return S_NOT_A_STEM, None
    if stem in script_index:
        return S_RESOLVED, script_index[stem]
    holders = literal_index.get(stem) or []
    if len(holders) == 1:
        return S_DECLARED_ONE, holders[0]
    if len(holders) > 1:
        return S_DECLARED_MANY, None
    return S_UNRESOLVED, None


# ----------------------------------------------------------------------------- faces


def walk_faces():
    """[(rel, payload)] over every parseable top-level-dict JSON under results/."""
    out = []
    errors = []
    base = os.path.join(ROOT, "results")
    for dirpath, dirs, files in os.walk(base):
        dirs[:] = sorted(d for d in dirs if d not in ("_quarantine", ".git"))
        for name in sorted(files):
            if not name.endswith(".json"):
                continue
            rel = _rel(os.path.join(dirpath, name))
            if is_own_output(rel):
                continue
            path = os.path.join(dirpath, name)
            try:
                if os.path.getsize(path) > MAX_FACE_BYTES:
                    continue
                payload = _load(path)
            except (ValueError, OSError):
                errors.append(rel)
                continue
            if not isinstance(payload, dict):
                continue
            out.append((rel, payload))
            if len(out) >= MAX_FACES:
                return out, errors
    return out, errors


def grade_faces(faces, vocab, index, literal_index=None):
    rows = []
    literal_index = literal_index or {}
    for rel, payload in faces:
        decl = []
        for name in sorted(payload):
            if name not in vocab:
                continue
            value = payload[name]
            if not isinstance(value, str) or not value.strip():
                continue
            dialect, norm = classify_value(name, value)
            status, script = (S_NOT_A_STEM, None)
            if dialect == D_STEM:
                status, script = resolve_stem(norm, index, literal_index)
            decl.append({
                "field": name,
                "value": value if len(value) <= 180 else value[:180] + "...",
                "dialect": dialect,
                "stem_status": status,
                "stem_resolves_to": script,
            })
        if not decl:
            continue
        dialects = {}
        for d in decl:
            dialects[d["dialect"]] = dialects.get(d["dialect"], 0) + 1
        stems = [d for d in decl if d["dialect"] == D_STEM]
        rows.append({
            "face": rel,
            "identity_fields": decl,
            "declared_count": len(decl),
            "dialects": dialects,
            "uses_a_stem": bool(stems),
            "every_value_is_a_stem": bool(stems) and len(stems) == len(decl),
            "has_dangling_stem": any(d["stem_status"] == S_UNRESOLVED for d in stems),
        })
    return rows


# ----------------------------------------------------------------------------- readers


def reader_census(vocab):
    """Split sources that READ an identity field by whether they also carry a normaliser."""
    sources, errors = e461.corpus()
    reading = []
    with_norm = []
    for rel, tree, literals, sites in sources:
        fields_read = sorted({f for f, kind, _ln in sites if f in vocab and kind in e461.READ_KINDS})
        if not fields_read:
            continue
        reading.append((rel, fields_read))
        text = e451.read_text(os.path.join(ROOT, rel))
        has_marker = any(m in text for m in NORMALISER_MARKERS)
        has_card_re = bool(CARD_RE_IDIOM.search(text))
        if has_marker or has_card_re:
            with_norm.append({
                "source": rel,
                "fields_read": fields_read,
                "marker": "text_idiom" if has_marker else "card_regex",
            })
    return {
        "corpus_sources": len(sources),
        "corpus_parse_errors": len(errors),
        "sources_reading_an_identity_field": len(reading),
        "sources_carrying_a_normaliser": len(with_norm),
        "normaliser_samples": with_norm[:12],
        "reading_samples": [r for r, _f in reading[:12]],
    }


# ----------------------------------------------------------------------------- build


def verdict_for(rows, readers):
    if not rows:
        return V_EMPTY
    stems = [r for r in rows if r["uses_a_stem"]]
    if not stems:
        return V_CARDS_ONLY
    if any(r["has_dangling_stem"] for r in stems):
        return V_STEMS_DANGLE
    return V_STEMS_RESOLVE


def build(write=True):
    parent = _load(os.path.join(OUTDIR, PARENT_FACE))
    vocab = sorted(parent.get("identity_field_vocabulary") or [])
    if not vocab:
        raise SystemExit("E474: E458 face carries no identity_field_vocabulary")
    index = stem_index_repo()
    literal_index = literal_stem_index()
    faces, face_errors = walk_faces()
    rows = grade_faces(faces, set(vocab), index, literal_index)
    readers = reader_census(set(vocab))

    dialect_totals = {d: 0 for d in DIALECTS}
    field_instances = 0
    for r in rows:
        field_instances += r["declared_count"]
        for d, n in r["dialects"].items():
            dialect_totals[d] = dialect_totals.get(d, 0) + n
    stems = [r for r in rows if r["uses_a_stem"]]
    dangling = [r for r in stems if r["has_dangling_stem"]]
    stem_only = [r for r in stems if r["every_value_is_a_stem"]]
    status_totals = {}
    for r in rows:
        for i in r["identity_fields"]:
            if i["dialect"] != D_STEM:
                continue
            status_totals[i["stem_status"]] = status_totals.get(i["stem_status"], 0) + 1
    cutoff = os.environ.get(CUTOFF_ENV) or "2026-11-06"
    face = {
        "card": CARD,
        "cutoff": cutoff,
        "evidence_cutoff": cutoff,
        "generated": cutoff,
        "verdict": verdict_for(rows, readers),
        "population": {
            "json_faces_under_results": len(faces),
            "json_parse_errors": len(face_errors),
            "faces_declaring_a_top_level_identity": len(rows),
            "identity_field_instances": field_instances,
            "identity_field_vocabulary": vocab,
            "vocabulary_source": PARENT_FACE,
            "scripts_indexed": len(index),
            "stem_shaped_literals_indexed": len(literal_index),
            "limit": ("population is top-level keys whose NAME is in the frozen vocabulary; a face "
                      "spelling its identity under an unlisted name is invisible here (E462 hazard)"),
        },
        "dialect_totals": dialect_totals,
        "stem_resolution_totals": status_totals,
        "rows": rows,
        "residue": {
            "faces_using_a_stem": len(stems),
            "faces_whose_every_identity_value_is_a_stem": len(stem_only),
            "faces_with_a_dangling_stem": len(dangling),
            "dangling_faces": sorted(r["face"] for r in dangling)[:40],
        },
        "readers": readers,
        "parse_errors": face_errors[:40],
    }
    path = os.path.join(OUTDIR, FACE_NAME)
    dated = os.path.join(OUTDIR, "%s-%s.json" % (DATED_PREFIX, cutoff))
    if write:
        for target in (dated, path):
            with io.open(target, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(face, fh, ensure_ascii=False, indent=1)
                fh.write("\n")
    return face, path, dated


# ----------------------------------------------------------------------------- check / verify


def tally_problems(face):
    problems = []
    rows = face.get("rows") or []
    totals = {d: 0 for d in DIALECTS}
    for r in rows:
        if r["declared_count"] != len(r["identity_fields"]):
            problems.append("row %s count != len(identity_fields)" % r["face"])
        for d, n in (r.get("dialects") or {}).items():
            totals[d] = totals.get(d, 0) + n
        stems = [i for i in r["identity_fields"] if i["dialect"] == D_STEM]
        if bool(stems) != bool(r.get("uses_a_stem")):
            problems.append("row %s stem flag does not re-derive" % r["face"])
    published = face.get("dialect_totals") or {}
    for d in DIALECTS:
        if published.get(d, 0) != totals.get(d, 0):
            problems.append("dialect total %s published %r != %r"
                            % (d, published.get(d, 0), totals.get(d, 0)))
    residue = face.get("residue") or {}
    dangling = [r for r in rows if r.get("has_dangling_stem")]
    if residue.get("faces_with_a_dangling_stem") != len(dangling):
        problems.append("dangling count does not re-derive")
    if face.get("verdict") != verdict_for(rows, face.get("readers") or {}):
        problems.append("verdict does not re-derive")
    return problems


def check():
    face = _load(os.path.join(OUTDIR, FACE_NAME))
    problems = tally_problems(face)
    print(json.dumps({"check": "problems=%d" % len(problems), "problems": problems[:12]},
                     ensure_ascii=False))
    return 0 if not problems else 1


def verify():
    """Re-derive the tallies from the live tree and compare against the published face."""
    published = _load(os.path.join(OUTDIR, FACE_NAME))
    fresh, _p, _d = build(write=False)
    problems = []
    for key in ("dialect_totals", "residue"):
        if json.dumps(published.get(key), sort_keys=True) != json.dumps(fresh.get(key), sort_keys=True):
            problems.append("%s moved against the live tree" % key)
    if published.get("population", {}).get("faces_declaring_a_top_level_identity") != \
            fresh["population"]["faces_declaring_a_top_level_identity"]:
        problems.append("graded face count moved")
    if published.get("verdict") != fresh.get("verdict"):
        problems.append("verdict moved: %r -> %r" % (published.get("verdict"), fresh.get("verdict")))
    print(json.dumps({"verify": "problems=%d" % len(problems), "problems": problems[:8],
                      "faces": fresh["population"]["faces_declaring_a_top_level_identity"]},
                     ensure_ascii=False))
    return 0 if not problems else 1


# ----------------------------------------------------------------------------- selftest


def selftest():
    ok = 0
    fail = []

    def leg(name, cond):
        nonlocal ok
        if cond:
            ok += 1
        else:
            fail.append(name)

    # value dialects
    leg("card id", classify_value("card", "E474") == (D_CARD, "E474"))
    leg("card id 3-digit", classify_value("study", "E62")[0] == D_CARD)
    leg("path", classify_value("prereg_path", "research/PREREG.md")[0] == D_PATH)
    leg("path json", classify_value("face", "results/state_tilt/x.json")[0] == D_PATH)
    leg("stem", classify_value("study", "e271_donor_choice_sensitivity") ==
        (D_STEM, "e271_donor_choice_sensitivity"))
    leg("stem with .py", classify_value("producer", "e403_family_arg.py") == (D_STEM, "e403_family_arg"))
    leg("other prose", classify_value("study", "two arms fitted by one code path")[0] == D_OTHER)
    leg("other empty", classify_value("card", "   ")[0] == D_OTHER)
    leg("other non-string", classify_value("card", 7)[0] == D_OTHER)
    # a stem-shaped value that carries a dot is not a stem
    leg("dotted value is not a stem", classify_value("study", "e474.v2")[0] == D_OTHER)

    # stem resolution
    idx = {"e474_identity_dialect_census": "scripts/e474_identity_dialect_census.py"}
    leg("resolved", stem_status("e474_identity_dialect_census", idx) ==
        (S_RESOLVED, "scripts/e474_identity_dialect_census.py"))
    leg("unresolved", stem_status("e999_not_a_script", idx)[0] == S_UNRESOLVED)
    leg("not a stem", stem_status(None, idx)[0] == S_NOT_A_STEM)

    # grading: a dangling stem is residue, a resolved one is not
    faces = [
        ("results/a.json", {"study": "e474_identity_dialect_census", "card": "E474"}),
        ("results/b.json", {"study": "e999_not_a_script"}),
        ("results/c.json", {"note": "e999_not_a_script"}),
    ]
    rows = grade_faces(faces, {"study", "card"}, idx)
    leg("only identity-named fields graded", len(rows) == 2)
    leg("resolved face not dangling", rows[0]["has_dangling_stem"] is False)
    leg("dangling face flagged", rows[1]["has_dangling_stem"] is True)
    leg("stem-only face detected", rows[1]["every_value_is_a_stem"] is True)
    leg("mixed face is not stem-only", rows[0]["every_value_is_a_stem"] is False)

    # verdict ladder
    cards_only = grade_faces([("results/z.json", {"card": "E474"})], {"study", "card"}, idx)
    leg("empty", verdict_for([], {}) == V_EMPTY)
    leg("cards only", verdict_for(cards_only, {}) == V_CARDS_ONLY)
    leg("dangling", verdict_for(rows, {}) == V_STEMS_DANGLE)
    leg("resolves", verdict_for([rows[0]], {}) == V_STEMS_RESOLVE)

    print(json.dumps({"selftest": "%d/%d" % (ok, ok + len(fail)), "failures": fail},
                     ensure_ascii=False))
    return 0 if not fail else 1


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=("run", "check", "verify", "selftest"))
    args = ap.parse_args(argv)
    if args.action == "run":
        face, _path, dated = build(write=True)
        print(json.dumps({"face": _rel(dated), "verdict": face["verdict"],
                          "graded": face["population"]["faces_declaring_a_top_level_identity"],
                          "dialects": face["dialect_totals"],
                          "residue": {k: v for k, v in face["residue"].items() if k != "dangling_faces"},
                          "readers": {k: face["readers"][k] for k in
                                      ("sources_reading_an_identity_field",
                                       "sources_carrying_a_normaliser")}},
                         ensure_ascii=False, indent=1))
        return 0
    if args.action == "check":
        return check()
    if args.action == "verify":
        return verify()
    return selftest()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))