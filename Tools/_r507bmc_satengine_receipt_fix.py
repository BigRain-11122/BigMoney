# -*- coding: utf-8 -*-
"""r507 bm-c: reconstruct the satengine-resolve receipt that failed to write in
_window (author slip: missing `import json` in _r507bmc_satengine_resolve.py ->
NameError at receipt write, AFTER both faces resolved and rebase continued OK).
Facts below are replayed from the live transcript of that run (resolver stdout:
both faces strategy=regen-take-newer side=s1 basis=max-ts blocks=0 = daemon had
already overwritten conflict markers with fresh live content; worktree passthrough,
zero-loss). No values invented; rebase completion is the physical proof."""
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
receipt = {
    "round": "r507",
    "note": "reconstructed receipt: original write died to missing-import slip "
            "(NameError json) after both faces resolved; rebase completed "
            "0e5aae75d, zero marker residue (pre-commit claw gate passed)",
    "files": {
        "results/saturation_engine/face_bm-c.json": {
            "strategy": "regen-take-newer", "side": "s1",
            "basis": "max-ts", "blocks": 0,
            "note": "daemon live-rewrite overwrote markers pre-resolve; "
                    "worktree fresh content passthrough (live-wins)"},
        "results/saturation_engine_state.bm-c.json": {
            "strategy": "regen-take-newer", "side": "s1",
            "basis": "max-ts", "blocks": 0,
            "note": "daemon live-rewrite overwrote markers pre-resolve; "
                    "worktree fresh content passthrough (live-wins)"},
    },
    "rebase_result": "Successfully rebased and updated refs/heads/main (pick2=0e5aae75d)",
}
out = os.path.join(REPO, "results", "_r507bmc_satengine_resolve.json")
with open(out, "w", encoding="utf-8", newline="\n") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("receipt written", out)
