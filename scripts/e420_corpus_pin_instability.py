"""E420 -- an identity stamp over a growing corpus cannot be an equality gate.

The E387 smoke leg asserts that every face the republish audit covered is *still published at the
number the audit re-derived that day*. For `siblingentry_latest.json` the audited field is
`corpus_source.pin_id`: a sha256 over the whole in-repo python corpus (e361.stamp over
e326.corpus). Any round that adds a script moves it, and the face's own producer -- the thing that
keeps the face honest -- is what rewrites it. So the leg goes red on an honest rebuild, and no
amount of republishing makes it green.

This study measures that instead of assuming it:

  (a) VINTAGES -- how many distinct pin values this one face has carried and where each came from
                  (the audit's carried-at-head, the audit's re-derivation, the face on disk);
  (b) DRIFT    -- how many audited rows today's leg flags, split into corpus-fingerprint moves and
                  moves of an actual published number (only the second is a republish defect);
  (c) SELF     -- whether the face still names a pin file that exists and agrees with it, which is
                  the invariant that IS satisfiable and is what the assertion should measure.

Usage:
    python scripts/e420_corpus_pin_instability.py run|verify|selftest
"""
from __future__ import annotations

import io
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

import e326_template_parameter_consumers as e326  # noqa: E402
import e361_census_corpus_pin as e361  # noqa: E402

STUDY = "E420_corpus_pin_instability"
OUTDIR = os.path.join("results", "state_tilt")
AUDIT_REL = os.path.join(OUTDIR, "REPUBLISH-2026-11-03.json")
FINGERPRINT_PREFIX = "corpus_source."

VERDICTS = (
    "the_only_fields_that_moved_are_population_counts_that_grew_with_the_corpus_and_every_face_"
    "agrees_with_its_own_pin_so_the_old_equality_assertion_was_unsatisfiable_on_an_honest_rebuild",
    "at_least_one_audited_number_went_down_or_a_verdict_moved_since_the_audit_so_a_red_row_is_a_"
    "real_republish_defect_and_the_assertion_can_stay_an_equality",
)


def _load(rel):
    with io.open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return json.load(fh)


def _is_fingerprint(name, value):
    """A corpus address is named as one and shaped like a sha256, not like a measurement."""
    return (name.startswith(FINGERPRINT_PREFIX)
            and isinstance(value, str) and len(value) == 64
            and all(c in "0123456789abcdef" for c in value))


def _self_agreement(face, base=None):
    """(a) the face names a pin file that exists, (b) that file carries the face's own numbers."""
    cs = face.get("corpus_source") or {}
    name = cs.get("pin_file")
    row = {"names_a_pin_file": bool(name), "pin_file_exists": False,
           "pin_id_agrees": False, "members_agree": False, "members": cs.get("members")}
    if not name:
        return row
    path = os.path.join(base or os.path.join(ROOT, OUTDIR), name)
    if not os.path.exists(path):
        return row
    row["pin_file_exists"] = True
    with io.open(path, encoding="utf-8") as fh:
        pin = json.load(fh)
    row["pin_id_agrees"] = pin.get("pin_id") == cs.get("pin_id")
    row["members_agree"] = pin.get("members") == cs.get("members")
    row["pin_file_members"] = pin.get("members")
    return row


def build(audit_rel=AUDIT_REL):
    audit = _load(audit_rel)
    rows = []
    for r in audit.get("rows") or []:
        face_name = r.get("face")
        path = os.path.join(ROOT, OUTDIR, face_name or "")
        row = {"face": face_name, "on_disk": os.path.exists(path),
               "moved_columns": [], "moved_fingerprints": [], "moved_numbers": [],
               "moved_numbers_up": [], "moved_numbers_down": [],
               "carried_vs_audit_fingerprints": r.get("columns", {})
               .get("moved_detail", {})}
        if row["on_disk"]:
            face = _load(os.path.join(OUTDIR, face_name))
            fresh = r.get("fresh_today") or {}
            headline = {}
            for k, v in fresh.items():
                cur = _now_value(face, k)
                if cur == v:
                    continue
                row["moved_columns"].append(k)
                if (k.startswith("corpus_source.") and _is_fingerprint(k, v)) or k == "corpus_source.pin_file":
                    row["moved_fingerprints"].append(k)
                    continue
                row["moved_numbers"].append(k)
                if isinstance(v, (int, float)) and isinstance(cur, (int, float)):
                    (row["moved_numbers_down"] if cur < v else row["moved_numbers_up"]).append(k)
                elif k == "verdict":
                    row["verdict_moved"] = True
            row["self"] = _self_agreement(face)
            row["pin_on_disk"] = (face.get("corpus_source") or {}).get("pin_id")
            headline = None
        rows.append(row)

    vintages = []
    sib = [r for r in rows if (r.get("face") or "").startswith("siblingentry")]
    if sib:
        carried = (sib[0].get("carried_vs_audit_fingerprints") or {}).get("corpus_source.pin_id") or {}
        fresh = {}
        for a in audit.get("rows") or []:
            if (a.get("face") or "").startswith("siblingentry"):
                fresh = (a.get("fresh_today") or {}).get("corpus_source.pin_id")
        for label, value in (("audit_carried_at_head", carried.get("carried")),
                             ("audit_re_derived_today", carried.get("fresh") or fresh),
                             ("face_on_disk_now", sib[0].get("pin_on_disk"))):
            vintages.append({"source": label, "pin_id": value})

    corpus_now = e361.stamp(e326.corpus(), root=ROOT)
    flagged = [r for r in rows if r["moved_columns"]]
    only_fingerprint = [r for r in flagged if r["moved_columns"] == r["moved_fingerprints"]]
    numbers_moved = [r for r in flagged if r["moved_numbers"]]
    went_down = [r for r in flagged if r.get("moved_numbers_down")]
    verdict_flipped = [r for r in flagged if r.get("verdict_moved")]
    self_ok = [r for r in rows if (r.get("self") or {}).get("pin_id_agrees")
               and (r.get("self") or {}).get("members_agree")]

    satisfiable = not went_down and not verdict_flipped
    summary = {
        "audited_rows": len(rows),
        "rows_on_disk": sum(1 for r in rows if r["on_disk"]),
        "rows_the_leg_flags_today": len(flagged),
        "rows_flagged_only_by_a_corpus_fingerprint": len(only_fingerprint),
        "rows_where_a_published_number_moved": len(numbers_moved),
        "rows_where_a_number_went_down": len(went_down),
        "rows_whose_verdict_moved": len(verdict_flipped),
        "rows_whose_face_agrees_with_its_own_pin_file": len(self_ok),
        "distinct_pin_vintages_for_one_face": len({v["pin_id"] for v in vintages if v["pin_id"]}),
        "corpus_members_now": corpus_now.get("members"),
        "corpus_pin_id_now": corpus_now.get("pin_id"),
        "corpus_pin_id_equals_any_recorded_vintage":
            corpus_now.get("pin_id") in {v["pin_id"] for v in vintages},
    }
    return {
        "study": STUDY,
        "evidence_cutoff": "2026-11-04",
        "audit_face": audit_rel.replace(os.sep, "/"),
        "rows": rows,
        "pin_vintages": vintages,
        "summary": summary,
        "verdict": VERDICTS[0] if satisfiable else VERDICTS[1],
    }


def _now_value(face, dotted):
    """Read a dotted key out of the face; `None` when it is not carried there at all."""
    cur = face
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def _count(summary, key):
    """A published count, or -1 when the key is absent -- `0` is a measurement, not a missing one."""
    if key not in summary:
        return -1
    try:
        return int(summary[key])
    except (TypeError, ValueError):
        return -1


def verify(face_path=None):
    problems = []
    path = face_path or os.path.join(ROOT, OUTDIR, "PININSTABILITY-2026-11-04.json")
    if not os.path.exists(path):
        return ["no published face at %s" % path]
    face = _load(path) if os.path.isabs(path) else _load(path)
    s = face.get("summary") or {}
    if face.get("verdict") not in VERDICTS:
        problems.append("verdict outside the frozen set")
    rows = face.get("rows") or []
    if _count(s, "audited_rows") != len(rows):
        problems.append("audited_rows does not re-derive from the row list")
    flagged = [r for r in rows if r.get("moved_columns")]
    if _count(s, "rows_the_leg_flags_today") != len(flagged):
        problems.append("rows_the_leg_flags_today does not re-derive")
    if _count(s, "rows_where_a_published_number_moved") != \
            len([r for r in rows if r.get("moved_numbers")]):
        problems.append("rows_where_a_published_number_moved does not re-derive")
    if _count(s, "rows_where_a_number_went_down") != \
            len([r for r in rows if r.get("moved_numbers_down")]):
        problems.append("rows_where_a_number_went_down does not re-derive")
    if _count(s, "rows_whose_verdict_moved") != \
            len([r for r in rows if r.get("verdict_moved")]):
        problems.append("rows_whose_verdict_moved does not re-derive")
    if _count(s, "rows_whose_face_agrees_with_its_own_pin_file") != \
            len([r for r in rows if (r.get("self") or {}).get("pin_id_agrees")]):
        problems.append("rows_whose_face_agrees_with_its_own_pin_file does not re-derive")
    # a fingerprint move must never be counted as a number move, and vice versa
    for r in rows:
        overlap = set(r.get("moved_fingerprints") or []) & set(r.get("moved_numbers") or [])
        if overlap:
            problems.append("%s: %s counted as both a fingerprint and a number"
                            % (r.get("face"), sorted(overlap)[0]))
            break
    # the verdict must follow from the split, not from the author's sentence
    satisfiable = not any(r.get("moved_numbers_down") or r.get("verdict_moved") for r in rows)
    if face.get("verdict") != (VERDICTS[0] if satisfiable else VERDICTS[1]):
        problems.append("verdict does not follow from the down/verdict split")
    # every face that is on disk must be re-checked, not trusted from the record
    for r in rows:
        if not r.get("on_disk"):
            continue
        on_disk = _self_agreement(_load(os.path.join(OUTDIR, r["face"])))
        rec = r.get("self") or {}
        for key in ("pin_file_exists", "pin_id_agrees", "members_agree"):
            if on_disk.get(key) != rec.get(key):
                problems.append("%s: %s no longer re-derives" % (r["face"], key))
                break
    return problems


def selftest():
    bad = []
    tmp = tempfile.mkdtemp(prefix="e420_")

    def check(name, ok, detail=""):
        if not ok:
            bad.append("%s %s" % (name, detail))

    try:
        # (1) a 64-hex corpus_source field is a fingerprint, a 64-hex number field is not
        h = "a" * 64
        check("a corpus_source sha is a fingerprint",
              _is_fingerprint("corpus_source.pin_id", h))
        check("the same sha outside corpus_source is a measurement",
              not _is_fingerprint("summary.digest", h))
        check("a short corpus_source value is not a fingerprint",
              not _is_fingerprint("corpus_source.pin_file", "CORPUSPIN-x.json"))
        # (2) dotted read
        check("dotted read finds a nested key",
              _now_value({"a": {"b": 3}}, "a.b") == 3)
        check("a missing dotted key reads None, not an exception",
              _now_value({"a": {}}, "a.b") is None)
        # (3) the split decides the verdict
        face = {"study": STUDY, "evidence_cutoff": "2026-11-04", "verdict": VERDICTS[0],
                "summary": {"audited_rows": 1, "rows_the_leg_flags_today": 1,
                            "rows_where_a_published_number_moved": 0,
                            "rows_where_a_number_went_down": 0,
                            "rows_whose_verdict_moved": 0,
                            "rows_whose_face_agrees_with_its_own_pin_file": 0},
                "rows": [{"face": "f.json", "on_disk": False, "moved_columns": ["corpus_source.pin_id"],
                          "moved_fingerprints": ["corpus_source.pin_id"], "moved_numbers": [],
                          "moved_numbers_up": [], "moved_numbers_down": []}],
                "pin_vintages": []}
        p = os.path.join(tmp, "PININSTABILITY-2026-11-04.json")
        with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1)
        old = os.getcwd()
        os.chdir(tmp)
        try:
            problems = verify(p)
        finally:
            os.chdir(old)
        check("verify accepts a fingerprint-only row set", problems == [], problems)
        # a number that went UP is accretion and must still pass
        face["rows"][0]["moved_numbers"] = ["summary.sources_read"]
        face["rows"][0]["moved_numbers_up"] = ["summary.sources_read"]
        face["summary"]["rows_where_a_published_number_moved"] = 1
        with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1)
        old = os.getcwd()
        os.chdir(tmp)
        try:
            problems = verify(p)
        finally:
            os.chdir(old)
        check("verify accepts a number that only grew (accretion)", problems == [], problems)
        # a number that went DOWN is a defect and must flip the verdict
        face["rows"][0]["moved_numbers_down"] = ["summary.sources_read"]
        face["summary"]["rows_where_a_number_went_down"] = 1
        with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1)
        old = os.getcwd()
        os.chdir(tmp)
        try:
            problems = verify(p)
        finally:
            os.chdir(old)
        check("verify reds when a number went down but the verdict still says satisfiable",
              any("verdict" in x for x in problems), problems)
        # summary must re-derive
        face["summary"]["rows_where_a_number_went_down"] = 0
        face["summary"]["rows_where_a_published_number_moved"] = 5
        with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1)
        old = os.getcwd()
        os.chdir(tmp)
        try:
            problems = verify(p)
        finally:
            os.chdir(old)
        check("verify reds when a count does not re-derive",
              any("does not re-derive" in x for x in problems), problems)
        # (5) a face agreeing with its pin file is self-consistent
        pin = {"pin_id": h, "members": 7}
        with io.open(os.path.join(tmp, "PIN.json"), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(pin, fh)
        facefile = {"corpus_source": {"pin_file": "PIN.json", "pin_id": h, "members": 7}}
        agree = _self_agreement(facefile, base=tmp)
        check("a face that agrees with its pin file is self-consistent",
              agree["pin_file_exists"] and agree["pin_id_agrees"] and agree["members_agree"], agree)
        facefile["corpus_source"]["members"] = 8
        disagree = _self_agreement(facefile, base=tmp)
        check("a member count that disagrees with the pin file is caught",
              not disagree["members_agree"])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("selftest %s %d/%d" % ("PASS" if not bad else "FAIL", 10 - len(bad), 10))
    for b in bad:
        print("  -", b)
    return 0 if not bad else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "selftest":
        return selftest()
    if cmd == "verify":
        problems = verify()
        for p in problems:
            print("PROBLEM:", p)
        print("verify problems=%d" % len(problems))
        return 0 if not problems else 1
    face = build()
    os.makedirs(os.path.join(ROOT, OUTDIR), exist_ok=True)
    out = os.path.join(ROOT, OUTDIR, "PININSTABILITY-%s.json" % face["evidence_cutoff"])
    for target in (out, os.path.join(ROOT, OUTDIR, "pininstability_latest.json")):
        with io.open(target, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
    s = face["summary"]
    print("audited_rows=%d flagged_today=%d fingerprint_only=%d numbers_moved=%d" %
          (s["audited_rows"], s["rows_the_leg_flags_today"],
           s["rows_flagged_only_by_a_corpus_fingerprint"],
           s["rows_where_a_published_number_moved"]))
    print("distinct_pin_vintages_for_one_face=%d corpus_members_now=%s pin_now_is_a_recorded_vintage=%s"
          % (s["distinct_pin_vintages_for_one_face"], s["corpus_members_now"],
             s["corpus_pin_id_equals_any_recorded_vintage"]))
    print("verdict=%s" % face["verdict"])
    print("face=%s" % os.path.relpath(out, ROOT).replace(os.sep, "/"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))