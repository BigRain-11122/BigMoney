import json, os
p = "results/saturation_engine/state_bm-a.json"
d = json.load(open(p, encoding="utf-8"))
keep = ["burns_active", "queue_next", "queue_depth", "last_verdict", "cycle", "shards_done_total", "heartbeat_ts", "engine_owner", "now_burn", "current_wave"]
for k in keep:
    if k in d:
        v = d[k]
        s = json.dumps(v, ensure_ascii=False)
        print(k, "=", s[:500])
print("ALL KEYS:", sorted(d.keys()))
print()
print("n1_w235_results exists:", os.path.exists("results/perpetual_faces/n1_w235_results.json"))
print("n1_w234_results exists:", os.path.exists("results/perpetual_faces/n1_w234_results.json"))
for f in ["results/perpetual_faces/n1_w235_results.json"]:
    if os.path.exists(f):
        dd = json.load(open(f, encoding="utf-8"))
        print(f, "keys:", sorted(dd.keys())[:20])
