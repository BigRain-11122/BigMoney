"""Standalone runner for the E495 (doctorpub) smoke leg.

The suite's leg text lives in ``smoke_test.py``; this runner exercises the same assertions
without launching the whole suite (35+ minutes).  It also proves the guard is not decorative:
two doctored copies of the published face must go red.

    python scripts/run_e495_smoke_leg.py
"""

import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e495_doctorpub as e495

FACE = os.path.join(ROOT, "results", "state_tilt", "doctorpub_latest.json")
PARENT = os.path.join(ROOT, "results", "state_tilt", "latestdoctor_latest.json")


def _load(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def main():
    legs = []

    def leg(name, ok, note=""):
        legs.append((name, bool(ok), note))

    face = _load(FACE)
    parent = _load(PARENT)
    rows = face.get("rows") or []
    summary = face.get("summary") or {}

    leg("the face passes its own guard", not e495.row_problems(face),
        repr(e495.row_problems(face))[:120])
    leg("the verdict is in the vocabulary", face.get("verdict") in e495.VERDICT_VOCAB,
        repr(face.get("verdict"))[:80])
    want = sorted(r["latest_basename"] for r in (parent.get("rows") or [])
                  if not r.get("has_a_producer_composer"))
    leg("the population is E492's harness-only set",
        sorted(r["latest_basename"] for r in rows) == want,
        "%d rows vs %d" % (len(rows), len(want)))
    leg("no harness leaves its bytes behind",
        summary.get("faces_whose_harness_leaves_its_bytes_behind") == 0,
        repr(summary.get("faces_whose_harness_leaves_its_bytes_behind")))
    leg("every harness restores the original",
        summary.get("harness_composers_that_restore") == summary.get("harness_composer_sites")
        and summary.get("harness_composer_sites"),
        "%r of %r" % (summary.get("harness_composers_that_restore"),
                      summary.get("harness_composer_sites")))
    leg("the writer axis accounts for every face",
        (summary.get("faces_with_a_writer_other_than_the_harness") or 0)
        + (summary.get("faces_no_source_other_than_the_harness_names") or 0) == len(rows),
        "%r + %r vs %r" % (summary.get("faces_with_a_writer_other_than_the_harness"),
                           summary.get("faces_no_source_other_than_the_harness_names"),
                           len(rows)))
    leg("a BOM source is disclosed, not silently skipped",
        any("e429" in s for s in (face.get("sources") or {}).get("start_with_a_bom") or []),
        repr((face.get("sources") or {}).get("start_with_a_bom"))[:120])

    doctored = json.loads(json.dumps(face))
    if doctored.get("rows") and doctored["rows"][0].get("harness"):
        doctored["rows"][0]["harness"][0]["discipline"] = e495.A_LEAVES
        doctored["rows"][0]["harness_leaves_its_bytes_behind"] = False
        leg("a hidden leaving harness is caught", bool(e495.row_problems(doctored)),
            "guard stayed silent")
    else:
        leg("a hidden leaving harness is caught", False, "no harness row to doctor")

    carried = json.loads(json.dumps(face))
    carried["summary"]["no_producer_faces"] = 999
    leg("a carried summary is caught", bool(e495.row_problems(carried)),
        "guard stayed silent")

    passed = sum(1 for _, ok, _ in legs if ok)
    for name, ok, note in legs:
        print("%s %s%s" % ("PASS" if ok else "FAIL", name,
                           (" -- " + note) if note and not ok else ""))
    print("%d/%d" % (passed, len(legs)))
    return 0 if passed == len(legs) else 1


if __name__ == "__main__":
    sys.exit(main())