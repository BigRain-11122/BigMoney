"""r686 bm-b: settle runnable_pool face after S0 reland (MSG-0612 law).

Uses merge_lane_views.sync_face library write path (CLI in this version
exposes merge/reconcile/resolve/selftest only). Prints result dict to
this file's stdout; exits 0 if status clean-settled, 2 on mechanism fault.
"""
import json
import sys

sys.path.insert(0, "scripts")
import merge_lane_views as mlv

res = mlv.sync_face("runnable_pool", machine="bm-b")
print(json.dumps(res, ensure_ascii=True, indent=1, sort_keys=True))
st = res.get("status")
sys.exit(0 if st in ("clean", "settled", "noop", "no-op") else 2)
