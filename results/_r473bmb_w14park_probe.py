# r473 bm-b: W14 park fallout probe (post MSG-1755) -- pool entry state, autofill lane state, generate outputs
import json, os, glob, time

rep = {}

# 1. pool file structure + W14 entries
for pool_path in ["results/runnable_pool.json", "results/runnable_pool.bm-b.json"]:
    if not os.path.exists(pool_path):
        rep[pool_path] = "ABSENT"
        continue
    d = json.load(open(pool_path, encoding="utf-8"))
    if isinstance(d, dict):
        items = d.get("entries") or d.get("pool") or d.get("items") or []
        rep[pool_path] = {"toplevel_keys": list(d.keys())[:12], "n_items": len(items)}
    else:
        items = d
        rep[pool_path] = {"type": "list", "n_items": len(items)}
    w14 = []
    for e in items:
        s = json.dumps(e, ensure_ascii=False)
        if "W14" in s or "w14" in s:
            w14.append({k: e.get(k) for k in list(e.keys())[:14] if not isinstance(e.get(k), (list, dict)) or k == "shards"})
    rep[pool_path]["w14_entries"] = w14[:6]
    rep[pool_path]["w14_count"] = len(w14)
    # last few entries status histogram
    hist = {}
    for e in items:
        hist[e.get("status", "?")] = hist.get(e.get("status", "?"), 0) + 1
    rep[pool_path]["status_hist"] = hist

# 2. autofill lane state
for st in ["results/autofill_state.bm-b.json"]:
    if os.path.exists(st):
        d = json.load(open(st, encoding="utf-8"))
        rep[st] = {k: d.get(k) for k in list(d.keys())[:16] if not isinstance(d.get(k), (list, dict))}
        launches = d.get("launches") or []
        if launches:
            rep[st]["last_launch"] = launches[-1] if not isinstance(launches[-1], dict) else {kk: launches[-1].get(kk) for kk in list(launches[-1].keys())[:12]}
            rep[st]["n_launches"] = len(launches)

# 3. recent W14-ish outputs anywhere in results/
cands = []
for pat in ["results/*w14*", "results/**/*w14*", "results/trial_labor_w14*/**"]:
    for p in glob.glob(pat, recursive=True):
        cands.append(p)
seen = sorted(set(cands))
now = time.time()
rep["w14_files"] = [{"path": p, "mtime": time.strftime("%H:%M:%S", time.localtime(os.path.getmtime(p))), "bytes": os.path.getsize(p)} for p in seen[:20]]
# newest files anywhere in results (top 8 by mtime)
allr = []
for p in glob.glob("results/*"):
    allr.append((os.path.getmtime(p), p))
allr.sort(reverse=True)
rep["results_newest"] = [{"path": p, "mtime": time.strftime("%H:%M:%S", time.localtime(m))} for m, p in allr[:8]]

print(json.dumps(rep, ensure_ascii=False, indent=1, default=str))
