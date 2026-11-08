"""Standalone runner for the E542 smoke leg.

``smoke_test.main()`` takes no leg filter (r1499), so a full-suite run cannot be used to check one
leg.  This script replicates the E542 leg's comparisons verbatim against the face on disk, so the
leg can be proved green without launching the 25-minute suite, and can be proved to fail on a
doctored face (``--doctor``) so the leg is known to be able to go red.

Nothing is rewritten: the doctor arm works on an in-memory copy.

Usage:
  python scripts/run_e542_smoke_leg.py
  python scripts/run_e542_smoke_leg.py --doctor
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e542_survivor_spans as m  # noqa: E402

FACE = os.path.join(ROOT, "results", "state_tilt", "survivorspans_latest.json")


def problems(face):
    bad = []
    summary = face.get("summary") or {}
    rows = face.get("sites") or []
    bad.extend(m.face_problems(face))
    if not rows:
        bad.append("the row population is empty")
    if summary.get("rows") != len(rows):
        bad.append("rows does not equal the published site rows")
    if not summary.get("classes_sum_to_the_rows"):
        bad.append("the classes do not add up to the rows")
    if not summary.get("substantive_plus_harmless_sums_to_the_rows"):
        bad.append("the substantive and harmless classes do not add up to the rows")
    if summary.get("rows_where_tier_could_separate_the_survivors") != 0:
        bad.append("a row publishes tier as able to separate its own survivors")
    for row in rows:
        survivors = row.get("survivors") or []
        if row.get("survivor_count") != len(survivors):
            bad.append("row %s carries a survivor count its list does not match"
                       % (row.get("site"),))
            break
        if row.get("class") == m.C_NOTHING and m._separators(survivors):
            bad.append("row %s is indistinguishable yet its survivors separate"
                       % (row.get("site"),))
            break
        if row.get("class") == m.C_DISTANCE and row.get("substantive_fields"):
            bad.append("row %s is distance-only yet names a substantive field"
                       % (row.get("site"),))
            break
        if any(v.get("tier") != row.get("tier") for v in survivors):
            bad.append("row %s carries a survivor whose tier disagrees with the row"
                       % (row.get("site"),))
            break
    return bad


def doctor(face):
    """Mutations the leg must refuse. Returns the names of the ones that slipped through."""
    slipped = []
    doc = json.loads(json.dumps(face))
    doc["verdict"] = "a_verdict_this_study_never_publishes"
    if not problems(doc):
        slipped.append("hand-written verdict")
    substantive = [i for i, r in enumerate(face["sites"])
                   if r.get("class") in (m.C_SEVERAL, m.C_STATEMENT)]
    if substantive:
        doc = json.loads(json.dumps(face))
        doc["sites"][substantive[0]]["class"] = m.C_NOTHING
        if not problems(doc):
            slipped.append("separating row relabelled indistinguishable")
    doc = json.loads(json.dumps(face))
    doc["sites"][0]["survivor_count"] = (face["sites"][0].get("survivor_count") or 0) + 5
    if not problems(doc):
        slipped.append("survivor count its list does not carry")
    doc = json.loads(json.dumps(face))
    doc["summary"]["substantive_field_hits"][m.F_STMT_LINE] += 1
    if not problems(doc):
        slipped.append("inflated substantive field count")
    doc = json.loads(json.dumps(face))
    doc["summary"]["rows_where_tier_could_separate_the_survivors"] = 1
    if not problems(doc):
        slipped.append("tier declared separating")
    return slipped


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    with open(FACE, encoding="utf-8") as fh:
        face = json.load(fh)
    bad = problems(face)
    if "--doctor" in argv:
        slipped = doctor(face)
        print("doctor: %d mutated faces slipped through: %s"
              % (len(slipped), json.dumps(slipped, ensure_ascii=False)))
        return 0 if slipped else 1
    s = face.get("summary") or {}
    print("leg: problems=%s" % json.dumps(bad, ensure_ascii=False)[:400])
    print("leg: %d ambiguous rows / %d survivors / %d substantive"
          % (s.get("rows", 0), s.get("survivors_overall", 0),
             s.get("rows_whose_survivors_differ_in_a_substantive_field", 0)))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())