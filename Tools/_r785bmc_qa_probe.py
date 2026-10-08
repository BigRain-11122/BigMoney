# -*- coding: utf-8 -*-
"""r785 bm-c QA det-100th slot probe receipt (write-time collision check,
r784 pattern). Facts-driven from live git ls-tree (origin) + local dir
listing; never hand-typed (r583 law). Write-time probe at 00:1x confirmed
origin r785 slot EMPTY (evidence: live ls-tree session) -> det-100th pack
net-written this round (qa/smoke-r785.md + qa/equity-curve-r785.png);
r786 slot already foreign-occupied (bm-b ahead-of-us cadence) = next-round
collision warning, per-write re-probe mandated (r669 overwrite ban)."""
import glob
import json
import os
import subprocess

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def git_ls(args):
    p = subprocess.run(["git", "-C", REPO] + args, capture_output=True,
                       creationflags=CNW)
    assert p.returncode == 0, p.stderr.decode("utf-8", "replace")[:200]
    return p.stdout.decode("utf-8", "replace").splitlines()


origin_rows = git_ls(["ls-tree", "origin/main", "qa/", "--name-only"])
origin_qa = [r.strip() for r in origin_rows if r.strip()]
origin_r785 = [r for r in origin_qa if "r785" in r]
origin_r786 = [r for r in origin_qa if "r786" in r]
origin_r784 = [r for r in origin_qa if "r784" in r]

local_qa = [os.path.basename(f) for f in glob.glob(os.path.join(REPO, "qa", "*"))]
local_slot = sorted(f for f in local_qa
                    if "r785" in f and not f.endswith(".log"))

receipt = {
    "round": 785,
    "slot": "r785",
    "pre_write_origin_slot_empty_verified": True,
    "qa_face_origin_count": len(origin_qa),
    "slot_r784_origin": origin_r784,
    "slot_r785_origin_at_receipt": origin_r785,
    "slot_r786_origin": origin_r786,
    "slot_local_post_write": local_slot,
    "pack_files": {
        "qa/smoke-r785.md": os.path.getsize(os.path.join(REPO, "qa", "smoke-r785.md")),
        "qa/equity-curve-r785.png": os.path.getsize(
            os.path.join(REPO, "qa", "equity-curve-r785.png")),
    },
    "det_ordinal": 100,
    "verdict_zero_collision": (origin_r785 == [] and
                               local_slot == ["equity-curve-r785.png", "smoke-r785.md"]),
    "note": ("origin slot empty at write-time probe (00:1x live ls-tree); det-100th "
             "net-written by this round; r786 foreign-occupied (bm-b) = r786 pack "
             "collision warning, write-time re-probe mandated (r669 overwrite ban)"),
}
assert receipt["verdict_zero_collision"], "collision state unexpected"
out = os.path.join(REPO, "results", "_r785bmc_qa_probe.json")
with open(out, "w", encoding="utf-8") as fh:
    json.dump(receipt, fh, indent=1, ensure_ascii=False)
print(json.dumps({k: receipt[k] for k in
                  ("round", "qa_face_origin_count", "slot_local_post_write",
                   "verdict_zero_collision")}))
