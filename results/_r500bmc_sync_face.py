# r500 bm-c: SHARD-10 r668 pool back-flip via canonical two-way settle (sync_face).
# Evidence: burn closed ok 22:10:09 (96 cells), own lane flipped done 22:17:33,
# shared face still ready on origin tip -> r668 double-flip gap. sync_face is the
# sanctioned library write path (merge_lane_views L16-18, r385 debt-3 slice-5).
import json, sys

sys.path.insert(0, r"K:\Fluxgroup\FluxGroup\quant\bigmoney\scripts")
from merge_lane_views import sync_face  # noqa: E402

r = sync_face("runnable_pool", machine="bm-c")
with open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r500bmc_sync_face.json", "w",
          encoding="utf-8") as f:
    json.dump(r, f, ensure_ascii=False, indent=1)
print("SYNC-FACE " + json.dumps(r, ensure_ascii=False)[:600])
