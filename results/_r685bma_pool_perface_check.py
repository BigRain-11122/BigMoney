"""r685 bm-a: per-face owner_since newer-wins check vs fresh origin (r474 law).

Compares every (entry_id, shard_key) owner_since + entry status between local
runnable_pool.json and origin/main blob. Reports faces where origin is NEWER
(needs max-merge into local before push) or local is newer (ours wins, fine).
"""
import json, subprocess

raw = open(r"results/runnable_pool.json", "rb").read()
r = subprocess.run(["git", "fetch", "origin"], capture_output=True)
r.check_returncode()
ob = subprocess.run(["git", "show", "origin/main:results/runnable_pool.json"],
                    capture_output=True)
ob.check_returncode()
org = json.loads(ob.stdout.decode("utf-8"))
loc = json.loads(raw.decode("utf-8"))


def ents(p):
    return p["entries"] if isinstance(p, dict) and "entries" in p else p

L = {x["id"]: x for x in ents(loc)}
O = {x["id"]: x for x in ents(org)}

local_newer, origin_newer, missing_loc, missing_org = [], [], [], []
for eid, oe in O.items():
    le = L.get(eid)
    if le is None:
        missing_loc.append(eid)
        continue
    for osh in oe.get("shards", []):
        lsh = next((s for s in le.get("shards", []) if s.get("key") == osh["key"]), None)
        ov, lv = osh.get("owner_since", ""), (lsh or {}).get("owner_since", "")
        if ov and lv and ov != lv:
            (origin_newer if ov > lv else local_newer).append(f"{eid}:{osh['key']} {lv} -> {ov}")
        if (lsh or {}).get("status") != osh.get("status"):
            local_newer.append(f"{eid}:{osh['key']} status {osh.get('status')} -> {(lsh or {}).get('status')}")
for eid in L:
    if eid not in O:
        missing_org.append(eid)

out = {
    "round": 685, "machine": "bm-a",
    "origin_tip": subprocess.run(["git", "rev-parse", "origin/main"],
                                 capture_output=True, text=True).stdout.strip()[:10],
    "origin_newer_faces": origin_newer,
    "local_newer_faces_count": len(local_newer),
    "missing_in_local": missing_loc,
    "missing_in_origin": missing_org,
    "verdict": "MAX-MERGE-NEEDED" if origin_newer else "LOCAL-WINS-ALL (push safe)",
}
json.dump(out, open(r"results/_r685bma_pool_perface_check.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(json.dumps({k: (v if k != "local_newer_faces_count" else v) for k, v in out.items()},
                 ensure_ascii=False))
