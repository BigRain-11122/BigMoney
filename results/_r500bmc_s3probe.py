# r500 bm-c S3 probe bundle: watermark + N2-W15 SHARD-10 pool state + boards census.
# Output to file only (r446). Read-only.
import json, os, re

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
out = {}

# 1) watermark red flag
wm_path = REPO + r"\results\watermark_red.json"
if os.path.exists(wm_path):
    with open(wm_path, "r", encoding="utf-8") as f:
        wm = json.load(f)
    out["watermark"] = {"red": wm.get("red"), "reason": str(wm.get("reason", ""))[:200],
                        "next_pick": wm.get("next_pick")}
else:
    out["watermark"] = "ABSENT"

# 2) shared pool N2-W15 + lane mirror state
def pool_face(fname):
    p = REPO + r"\results" + "\\" + fname
    if not os.path.exists(p):
        return "ABSENT"
    with open(p, "r", encoding="utf-8") as f:
        d = json.load(f)
    faces = {}
    for e in d.get("entries", []):
        eid = str(e.get("id", ""))
        if "N2-W15" in eid or "n2-w15" in eid.lower():
            shards = []
            for s in e.get("shards", []):
                shards.append({"key": s.get("key"), "status": s.get("status"),
                               "owner": s.get("owner"), "owner_since": s.get("owner_since")})
            faces[eid] = {"entry_status": e.get("status"), "shards": shards}
    return faces

out["shared_pool_n2w15"] = pool_face("runnable_pool.json")
out["lane_bm_a"] = pool_face("runnable_pool.bm-a.json")
out["lane_bm_b"] = pool_face("runnable_pool.bm-b.json")
out["lane_bm_c_exists"] = os.path.exists(REPO + r"\results\runnable_pool.bm-c.json")
if out["lane_bm_c_exists"]:
    out["lane_bm_c"] = pool_face("runnable_pool.bm-c.json")

# 3) fleet tasks open census
tdir = REPO + r"\fleet\tasks"
open_tickets = []
if os.path.isdir(tdir):
    for fn in sorted(os.listdir(tdir)):
        if not fn.endswith(".json"):
            continue
        try:
            with open(tdir + "\\" + fn, "r", encoding="utf-8") as f:
                t = json.load(f)
            st = str(t.get("status", ""))
            if st in ("open", "claimed", "in_progress"):
                open_tickets.append({"file": fn, "status": st,
                                     "owner": t.get("claimed_by") or t.get("owner"),
                                     "title": str(t.get("title", t.get("subject", "")))[:60]})
        except Exception as ex:
            open_tickets.append({"file": fn, "status": "PARSE_ERR", "err": str(ex)[:80]})
out["fleet_tasks_active"] = open_tickets

with open(REPO + r"\results\_r500bmc_s3probe.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("S3PROBE-OK " + json.dumps(out, ensure_ascii=False)[:400])
