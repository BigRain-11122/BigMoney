# r691 bm-b origin-truth probe: N2-W15 pool entry ownership after bm-a r694 wave
# (B-machine law: judge fleet reality from origin refs, subprocess raw bytes, no PS pipe)
import json, subprocess, io

def blob(path, ref="origin/main"):
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True)
    assert r.returncode == 0, f"git show failed {path}: {r.stderr[:200]}"
    return json.loads(r.stdout.decode("utf-8"))

pool = blob("results/runnable_pool.json")
out = []
for e in pool["entries"]:
    k = str(e.get("key", ""))
    if "W15" in k or ("N2" in k and "GENERATE" in k):
        out.append({
            "key": k, "status": e.get("status"),
            "shards": e.get("shards"), "runner": e.get("runner"),
            "runner_args": e.get("runner_args"),
            "lane_owner": e.get("lane_owner"),
            "audit": e.get("audit"),
        })

hb_a = blob("fleet/machines/bm-a.json")
hb_b = blob("fleet/machines/bm-b.json")
facts = {
    "n2_entries": out,
    "bm_a_heartbeat": {
        "last_seen": hb_a.get("last_seen"),
        "current_task": (hb_a.get("current_task") or "")[:400],
        "verdict": hb_a.get("verdict"),
    },
    "bm_b_heartbeat_origin": {
        "last_seen": hb_b.get("last_seen"),
        "current_task": (hb_b.get("current_task") or "")[:200],
    },
}

with io.open(r"results/_r691bmb_n2_origin_truth.json", "w", encoding="utf-8") as f:
    json.dump(facts, f, ensure_ascii=False, indent=1)
print("WROTE results/_r691bmb_n2_origin_truth.json entries=%d" % len(out))
for e in out:
    print(json.dumps(e, ensure_ascii=False)[:500])
