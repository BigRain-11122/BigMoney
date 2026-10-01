import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))

# pool: :3 (mine: NULLS-done settle + W9 supply 12 entries) as base
b = subprocess.check_output(["git", "show", ":3:results/runnable_pool.json"])
open("results/runnable_pool.json", "wb").write(b)
json.load(open("results/runnable_pool.json", encoding="utf-8"))
print("pool base = :3 written")

from merge_lane_views import sync_face  # noqa: E402
r = sync_face("runnable_pool")
print("sync:", r.get("status"), "shared=", r.get("wrote_shared"),
      "lane=", r.get("wrote_lane"), "|", (r.get("notes") or [""])[0][:80])

pool = json.load(open("results/runnable_pool.json", encoding="utf-8"))
ents = pool.get("entries", [])
by_id = {e.get("id"): e for e in ents}
w9 = [e for e in ents if "N1-W9" in str(e.get("id", ""))]
n = by_id.get("LOWAMP-P2-NULLS")
print("W9 =", len(w9), "| NULLS =", n.get("status"),
      n["shards"][0].get("status"))
rev2 = by_id.get("REV-P2-NULLS")
print("REV-P2-NULLS:", (rev2 or {}).get("status"),
      ((rev2 or {}).get("shards") or [{}])[0].get("owner"))
w14 = by_id.get("TRIAL-LABOR-W14-GENERATE")
print("W14 =", (w14 or {}).get("status"),
      "| park kept =", bool((w14 or {}).get("park_note")))
la = [e for e in ents if str(e.get("id", "")).startswith("LOWAMP-P2-")]
print("LOWAMP-P2 family done:", sum(1 for e in la if e.get("status") == "done"),
      "/", len(la))
assert len(w9) == 12, "W9 lost"
assert n.get("status") == "done", "NULLS lost"
assert rev2 is not None, "rev-p2 claim lost"
assert sum(1 for e in la if e.get("status") == "done") == 18, "P2 family"
print("POOL_RESOLVE_OK")
