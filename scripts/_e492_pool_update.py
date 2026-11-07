# -*- coding: utf-8 -*-
"""Close E491 and refill the supply floor with E492 (r1516 bm-b), JSON face only."""
import io
import json
import sys

POOL = "results/runnable_pool.json"
NOW = "2026-11-07T10:12:00+0800"

E492_ID = ("E492-OF-THE-MULTI-COMPOSED-LATEST-NAMES-HOW-MANY-EXTRA-COMPOSERS-ARE-DOCTOR-"
           "HARNESSES-AND-DO-ANY-OF-THEM-LEAVE-A-MUTATED-FACE-BEHIND")


def main():
    pool = json.load(io.open(POOL, encoding="utf-8"))
    hit = 0
    for entry in pool["entries"]:
        if entry.get("id", "").startswith("E491-"):
            entry["status"] = "done"
            entry["owner"] = "bm-b r1516"
            entry["settled_at"] = NOW
            entry["deliverable"] = "results/state_tilt/LATESTCOPIER-<cutoff>.json"
            entry["target"] = "results/state_tilt/latestcopier_latest.json"
            entry["result_ref"] = "results/state_tilt/latestcopier_latest.json"
            entry["result_note"] = (
                "176 latest names: 123 written directly, 2 copies inside the source directory, "
                "0 copies out, 51 with several composers, 0 with no static composer; "
                "bandthreshguard_latest.json is written by e273:385 shutil.copyfile(path, "
                "latest) through the same OUTDIR constant, so E489's dir_only row is one "
                "writer's second write, not a second writer")
            hit += 1
    if not hit:
        sys.stderr.write("E491 not found in the pool\n")
        return 2
    if not any(e.get("id") == E492_ID for e in pool["entries"]):
        pool["entries"].append({
            "id": E492_ID,
            "title": ("E491 left 51 of 176 latest names with two or more static composers. A "
                      "sample of the extras are leg runners (scripts/run_eXXX_smoke_leg.py) "
                      "that write a doctored copy of the face to prove a leg can go red. For "
                      "each of the 51 multi-composed names, classify every composer as "
                      "producer / leg-runner doctor / one-off repair, publish how many writers "
                      "remain once doctors are excluded, and say whether any doctor writer can "
                      "leave a mutated face on disk (does it restore the original bytes, or "
                      "write a doctored payload and exit)."),
            "source": ("E491 (r1516 bm-b): 176 latest names / 2 copy-same-dir / 0 copy-other-dir "
                       "/ 123 direct / 51 several / 0 none; e452's and e447's latest names are "
                       "each written by the study AND by run_eXXX_smoke_leg.py"),
            "lane": "cpu-only",
            "lane_note": "static: AST classification of the published composers plus a read of "
                         "each leg runner's restore path, no network",
            "deliverable": "results/state_tilt/LATESTDOCTOR-<cutoff>.json",
            "target": "results/state_tilt/latestdoctor_latest.json",
            "evidence_cutoff": "2026-11-07",
            "entered_at": NOW,
            "entered_by": "bm-b r1516 (supply floor refill after E491)",
            "status": "ready",
            "result_ref": None,
        })
    pool["updated_at"] = NOW
    body = json.dumps(pool, indent=1, ensure_ascii=False) + "\n"
    with io.open(POOL, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(body)
    print("E491 closed; E492 seeded; entries=%d" % len(pool["entries"]))
    ready = [e["id"][:8] for e in pool["entries"] if e.get("status") == "ready"]
    print("ready: %s" % ", ".join(ready))
    return 0


if __name__ == "__main__":
    sys.exit(main())