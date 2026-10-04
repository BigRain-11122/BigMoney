"""r507 bm-c: satengine lane-face UU resolve (rebase 2/2, two own-lane daemon
faces) via import of the r507 v2 resolver's regen-newer logic (r506 canon copy;
CODELY union leg not needed this window -- CODELY.md not in UU set)."""
import io
import os
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
import _r507bmc_rebase_resolve as R  # noqa: E402

for p in ("results/saturation_engine/face_bm-c.json",
          "results/saturation_engine_state.bm-c.json"):
    R.resolve_regen(p)
    print("resolved", p, "->", R.receipt["files"][p])
json.dump(R.receipt, io.open(os.path.join(ROOT, "results", "_r507bmc_satengine_resolve.json"),
                            "w", encoding="utf-8", newline="\n"),
         ensure_ascii=False, indent=1)
print("receipt written")
