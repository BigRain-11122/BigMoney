# -*- coding: utf-8 -*-
"""r777 bm-c QA pack slot probe (det-96th clean first-write gate): origin
ls-tree over qa/ face, r777/r778/r779 slot occupancy + total file count.
Facts-driven JSON -> results/_r777bmc_qa_probe.json (r776 probe shape canon;
pattern credit: r776 inline probe -> results/_r776bmc_qa_probe.json)."""
import json
import os
import re
import subprocess

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
ROUND = 777
WATCH = ["r777", "r778", "r779"]


def main():
    p = subprocess.run(["git", "-C", REPO, "ls-tree", "origin/main",
                       "--name-only", "qa/"], capture_output=True)
    lines = [l for l in p.stdout.decode("utf-8", "replace").splitlines()
             if l.strip()]
    # r669 law: ls-tree --name-only carries the path prefix; basename-face
    # compare via regex on the leaf, never startswith on the raw line.
    occupied = []
    free_next = []
    for slot in WATCH:
        hits = [l for l in lines if re.search(r"[-_]%s\." % slot, os.path.basename(l))]
        (occupied.extend(hits) if hits else free_next.append(slot))
    facts = {
        "round": ROUND,
        "probe": "git ls-tree origin/main -- qa/ (leaf-slot regex, r669 basename law)",
        "occupied": occupied,
        "free_slots_next": free_next,
        "total_qa_files": len(lines),
        "decision": ("IGNITE det-96th with --round 777 (clean first-write, slot free)"
                     if not occupied else
                     "SKIP: canon name occupied by another machine evidence pack; "
                     "overwrite forbidden; defer to next free slot"),
    }
    out = os.path.join(REPO, "results", "_r777bmc_qa_probe.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, indent=1)
    print(json.dumps(facts, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
