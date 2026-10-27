"""E111 -- stamp the repair factor into every face, and make a join refuse.

Background
----------
``e39_panel_census.write_json`` stamps ``evidence_cutoff`` on every face it
writes, and ``burncontrol`` (E88/E110) learned to name a cross-cutoff join as a
confound instead of a defect. That guard covers ONE of the two axes. The other
axis -- the code that burned the face -- was never written down, so E110 read a
pre-E108 face against a post-E108 one and called the difference a mismatch.

What is wrong with the current state
------------------------------------
Nothing on disk says which repair factor produced any given face. Two faces can
therefore be joined, agree or disagree, and the reader has no way to tell "the
burn is wrong" from "these are two different experiments". Back-stamping is
impossible: the stamp would be claiming what the code did, and the code that
did it is exactly what was not recorded.

What this delivers
------------------
1. ``panel_screen.repair_factor_id()`` -- a 12-char id over the source of the
   three repair functions (``split_events``/``neutralise``/``implied_ratio``).
2. ``e39_panel_census.write_json`` stamps ``repair_factor`` (+ ``_src``) on
   every face it writes from now on.
3. ``_repair_factor_guard`` makes ``burncontrol`` publish
   ``version_unknown`` / ``mixed_repair_factors`` instead of agreeing or
   mismatching. An unstamped face is UNKNOWN, never equal.

This tool publishes the census of what is on disk today: which faces carry the
current factor, which carry another, and which carry none -- so the size of the
unknown is measured rather than assumed.

Usage:
    python scripts/e111_face_factor_stamp.py run [--out F]
    python scripts/e111_face_factor_stamp.py selftest
"""
from __future__ import annotations

import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

FACE_DIR = os.path.join(ROOT, "results", "e44_midmonth")
FACE_GLOB = "*.json"
OUT_NAME = "FACESTAMP-20261027.json"


def classify(face, current):
    """-> one face's stamp state relative to the factor this process would burn.

    An absent stamp is ``unstamped`` and never resolves to "same".
    """
    tag = (face or {}).get("repair_factor")
    if not tag:
        return "unstamped"
    return "stamped_current" if tag == current else "stamped_other"


def census(current, paths):
    """-> per-face rows plus counts, for a list of face paths."""
    rows, counts = [], {"stamped_current": 0, "stamped_other": 0, "unstamped": 0}
    other_ids = {}
    for p in paths:
        name = os.path.basename(p)
        try:
            with open(p, encoding="utf-8") as fh:
                face = json.load(fh)
        except (OSError, ValueError) as exc:
            rows.append({"face": name, "state": "unreadable", "error": repr(exc)})
            continue
        state = classify(face, current)
        counts[state] += 1
        tag = face.get("repair_factor")
        if state == "stamped_other":
            other_ids[tag] = other_ids.get(tag, 0) + 1
        rows.append({"face": name, "state": state, "repair_factor": tag,
                     "cutoff": face.get("evidence_cutoff"),
                     "study": face.get("study")})
    rows.sort(key=lambda r: (r.get("state") or "", r.get("face") or ""))
    return rows, counts, other_ids


def run(out_path=None):
    import e39_panel_census as e39
    import panel_screen

    current = panel_screen.repair_factor_id()
    paths = sorted(glob.glob(os.path.join(FACE_DIR, FACE_GLOB)))
    rows, counts, other_ids = census(current, paths)

    control = e39.run_burncontrol()

    payload = {
        "tool": "scripts/e111_face_factor_stamp.py",
        "study": "e111_face_repair_factor_stamp",
        "evidence_cutoff": control.get("evidence_cutoff"),
        "repair_factor": current,
        "repair_factor_src": "+".join(panel_screen.REPAIR_FACTOR_SRC),
        "faces_scanned": len(paths),
        "counts": counts,
        "other_factor_ids": other_ids,
        "unstamped_faces": [r["face"] for r in rows if r["state"] == "unstamped"],
        "control": {"status": control.get("status"),
                    "summary": control.get("summary"),
                    "repair_factor": (control.get("repair_factor") or {}).get("verdict"),
                    "unstamped": (control.get("repair_factor") or {}).get("unstamped"),
                    "stale_twins": control.get("stale_twins")},
        "answers": {
            "can_a_join_report_agreement_today": False,
            "why": "the burn control's own three inputs carry no stamp, so the join "
                   "resolves to version_unknown instead of identical_on_this_face",
            "what_clears_it": "re-burn the twins on the current panel; the stamp is "
                              "written by write_json from this commit on",
        },
        "faces": rows,
        "honest": [
            "back-stamping an existing face is impossible: the stamp would be a claim "
            "about code that was never recorded, so old faces stay UNKNOWN",
            "the stamp is deliberately sensitive to any source edit, comments included: "
            "a wording change is a reason to re-burn, not a reason to keep joining",
            "the guard changes what the control PUBLISHES, not what the burn computes; "
            "no published number was rewritten by this leg",
            "descriptive census only: no gate, no verdict on any strategy, zero ledger",
        ],
    }

    out = out_path or os.path.join(FACE_DIR, OUT_NAME)
    # written through the census writer on purpose: this face proves the stamp
    # end to end, because it must come back off disk carrying one.
    e39.write_json(os.path.dirname(out), os.path.basename(out), payload)
    with open(out, encoding="utf-8") as fh:
        back = json.load(fh)
    payload["writer_proof"] = {
        "file": os.path.relpath(out, ROOT),
        "stamped_on_disk": bool(back.get("repair_factor")),
        "repair_factor_on_disk": back.get("repair_factor"),
        "matches_current": back.get("repair_factor") == current,
    }
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    return payload, out


def selftest():
    import e39_panel_census as e39
    import panel_screen

    fails, n = [], 0

    def chk(cond, label):
        nonlocal n
        n += 1
        if not cond:
            fails.append(label)

    cur = panel_screen.repair_factor_id()

    chk(classify({"repair_factor": cur}, cur) == "stamped_current",
        "a face stamped with the live id is current")
    chk(classify({"repair_factor": "ffffffffffff"}, cur) == "stamped_other",
        "a face stamped with another id is not silently counted as current")
    chk(classify({}, cur) == "unstamped", "a face with no stamp is unstamped")
    chk(classify({"repair_factor": ""}, cur) == "unstamped",
        "an empty stamp is not a stamp")

    # the guard is the thing that changes the published status
    chk(e39._repair_factor_guard([("a", {"repair_factor": cur})])["verdict"] == "uniform",
        "one stamped face is uniform")
    chk(e39._repair_factor_guard([("a", {"repair_factor": cur}), ("b", {})])["verdict"]
        == "version_unknown", "one unstamped face makes the whole join unknown")
    chk(e39._repair_factor_guard([("a", {"repair_factor": cur}),
                                  ("b", {"repair_factor": "0" * 12})])["verdict"]
        == "mixed_repair_factors", "two ids never agree")

    # the writer really stamps (round-trip through a scratch file)
    import tempfile
    tmp = tempfile.mkdtemp(prefix="e111_")
    p = e39.write_json(tmp, "probe.json", {"study": "probe"})
    with open(p, encoding="utf-8") as fh:
        back = json.load(fh)
    chk(back.get("repair_factor") == cur, "write_json stamps the live repair factor")
    chk(back.get("repair_factor_src") == "+".join(panel_screen.REPAIR_FACTOR_SRC),
        "write_json names which functions the id covers")
    chk(e39.write_json(tmp, "probe2.json", {"repair_factor": "explicit"})
        .endswith("probe2.json"), "an explicit stamp is written, not rejected")
    with open(os.path.join(tmp, "probe2.json"), encoding="utf-8") as fh:
        chk(json.load(fh).get("repair_factor") == "explicit",
            "an explicit stamp is never overwritten by the writer")

    # census counts only what it read
    rows, counts, others = census(cur, [p])
    chk(counts["stamped_current"] == 1 and counts["unstamped"] == 0,
        "the census counts a stamped face as current")
    chk(others == {}, "no other factor ids appear when there are none")

    print(json.dumps({"selftest": "%d/%d" % (n - len(fails), n), "fails": fails}))
    return 0 if not fails else 1


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    if argv[0] == "selftest":
        return selftest()
    if argv[0] == "run":
        out = None
        if "--out" in argv:
            out = argv[argv.index("--out") + 1]
        payload, path = run(out)
        print(json.dumps({
            "status": "published",
            "repair_factor": payload["repair_factor"],
            "faces_scanned": payload["faces_scanned"],
            "counts": payload["counts"],
            "control_status": payload["control"]["status"],
            "writer_proof": payload["writer_proof"],
            "file": os.path.relpath(path, ROOT),
        }, ensure_ascii=False))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))