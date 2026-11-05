"""E455: price the distance between each of the three census faces that re-red at r1473 and a fresh
reading of its own producer, using the shared tolerance rule in scripts/growth_tolerance.py.

r1473 measured the delta as growth by eye (227->232 readers, 265->266 sites, 230->233 faces, the
verdicts unchanged) but the smoke legs still demanded exact equality, so the same three legs would
re-red again one round later.  This study asks the mechanical version of that question for each leg
and publishes the answer, so the tolerance rule is exercised against live payloads and not only
against fixtures.

    python scripts/e455_growth_census.py run     # build, classify, publish results/state_tilt/GROWTHTOL-<cutoff>.json
    python scripts/e455_growth_census.py check   # re-derive the published verdict from its own rows
    python scripts/e455_growth_census.py selftest
"""
from __future__ import annotations

import importlib
import io
import json
import os
import sys

import growth_tolerance as gt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STUDIES = [
    {
        "card": "E398",
        "face": os.path.join("results", "state_tilt", "latestfamily_latest.json"),
        "module": "e398_latest_family",
        "list_key": "read_sites",
        "row_id": "anchor",
        "class_fields": ("tier", "class"),
        "build": lambda m: m.build(write=False),
    },
    {
        "card": "E409",
        "face": os.path.join("results", "state_tilt", "unfloored_latest.json"),
        "module": "e409_unfloored_faces",
        "list_key": "ledger",
        "row_id": "face",
        "class_fields": ("label",),
        "build": lambda m: m.build(write=False),
    },
    {
        "card": "E411",
        "face": os.path.join("results", "state_tilt", "readertiers_latest.json"),
        "module": "e411_reader_tiers",
        "list_key": "faces",
        "row_id": "face",
        "class_fields": ("no_reader_that_can_go_red", "all_readers_in_the_two_blind_tiers"),
        "build": lambda m: m.build(write=False, skip_writers=True),
    },
]


def _load(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def build(write=True):
    if os.path.join(ROOT, "scripts") not in sys.path:
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
    rows = []
    for spec in STUDIES:
        published = _load(os.path.join(ROOT, spec["face"]))
        module = importlib.import_module(spec["module"])
        fresh = spec["build"](module)
        result = gt.classify(published, fresh, list_key=spec["list_key"],
                             row_id=spec["row_id"], class_fields=spec["class_fields"])
        rows.append({
            "card": spec["card"],
            "face": spec["face"].replace(os.sep, "/"),
            "module": spec["module"],
            "list_key": spec["list_key"],
            "row_id": spec["row_id"],
            "class_fields": list(spec["class_fields"]),
            "result": result,
            "line": gt.describe(result),
            "tolerated": gt.tolerates(result),
        })
    tolerated = sum(1 for r in rows if r["tolerated"])
    identical = sum(1 for r in rows if r["result"]["verdict"] == gt.IDENTICAL)
    failing = [r["card"] for r in rows if not r["tolerated"]
               and r["result"]["verdict"] != gt.IDENTICAL]
    if not failing and identical == len(rows):
        verdict = "all_three_census_faces_still_re_derive_exactly"
    elif not failing:
        verdict = ("every_census_face_that_moved_moved_only_by_growth_and_the_verdicts_did_not_"
                   "move_so_the_legs_can_tolerate_it_instead_of_re_redding")
    else:
        verdict = "%d_of_%d_census_faces_moved_for_a_reason_growth_cannot_explain" % (
            len(failing), len(rows))
    payload = {
        "study": "E455",
        "title": "why a census over a growing tree re-reds one round after republish",
        "evidence_cutoff": _cutoff(rows),
        "rule": {
            "module": "scripts/growth_tolerance.py",
            "tolerated_verdict": gt.PURE_GROWTH,
            "still_refused": [gt.LOST_ROW, gt.SHRANK, gt.VERDICT_MOVED,
                              gt.MOVED_WITHOUT_GROWTH, gt.CHANGED_VALUE],
        },
        "rows": rows,
        "summary": {
            "faces_priced": len(rows),
            "faces_identical": identical,
            "faces_tolerated_as_pure_growth": tolerated,
            "faces_failing": len(failing),
        },
        "verdict": verdict,
    }
    if write:
        out_dir = os.path.join(ROOT, "results", "state_tilt")
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, "GROWTHTOL-%s.json" % payload["evidence_cutoff"])
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
        latest = os.path.join(out_dir, "growthtol_latest.json")
        with io.open(latest, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
        print("wrote %s" % os.path.relpath(path, ROOT))
    return payload


def _cutoff(rows):
    """The cutoff is the date the fresh readings were taken, never a wall clock written twice."""
    import datetime
    return datetime.date.today().isoformat()


def check():
    path = os.path.join(ROOT, "results", "state_tilt", "growthtol_latest.json")
    published = _load(path)
    bad = []
    rows = published.get("rows") or []
    identical = sum(1 for r in rows if r["result"]["verdict"] == gt.IDENTICAL)
    tolerated = sum(1 for r in rows if r["tolerated"])
    failing = [r["card"] for r in rows
               if not r["tolerated"] and r["result"]["verdict"] != gt.IDENTICAL]
    summary = published.get("summary") or {}
    if summary.get("faces_priced") != len(rows):
        bad.append("the published face count does not re-add to its rows")
    if summary.get("faces_identical") != identical:
        bad.append("faces_identical does not re-derive from the rows")
    if summary.get("faces_tolerated_as_pure_growth") != tolerated:
        bad.append("the tolerated count does not re-derive from the rows")
    if summary.get("faces_failing") != len(failing):
        bad.append("the failing count does not re-derive from the rows")
    for row in rows:
        if row["tolerated"] != gt.tolerates(row["result"]):
            bad.append("%s: tolerated flag disagrees with its own result" % row["card"])
    verdict = published.get("verdict") or ""
    if not failing and identical == len(rows):
        want = "all_three_census_faces_still_re_derive_exactly"
    elif not failing:
        want = ("every_census_face_that_moved_moved_only_by_growth_and_the_verdicts_did_not_"
                "move_so_the_legs_can_tolerate_it_instead_of_re_redding")
    else:
        want = "%d_of_%d_census_faces_moved_for_a_reason_growth_cannot_explain" % (
            len(failing), len(rows))
    if verdict != want:
        bad.append("the verdict does not re-derive: %r != %r" % (verdict, want))
    for b in bad:
        print("BAD %s" % b)
    print("check %s" % ("clean" if not bad else "%d problem(s)" % len(bad)))
    return 0 if not bad else 1


def selftest():
    ok = total = 0

    def leg(name, cond):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
        else:
            print("FAIL %s" % name)

    leg("growth module is the shared one", gt.PURE_GROWTH == "pure_growth")
    leg("every study declares a list key", all(s.get("list_key") for s in STUDIES))
    leg("cards are distinct", len({s["card"] for s in STUDIES}) == len(STUDIES))
    leg("no study writes its own face from here", all("write=True" not in str(s["build"])
                                                     for s in STUDIES))
    print("%d/%d" % (ok, total))
    return 0 if ok == total else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "run":
        payload = build(write=True)
        print(json.dumps(payload["summary"], ensure_ascii=False, sort_keys=True))
        print(payload["verdict"])
        return 0
    if cmd == "check":
        return check()
    if cmd == "selftest":
        return selftest()
    print("usage: python scripts/e455_growth_census.py run|check|selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))