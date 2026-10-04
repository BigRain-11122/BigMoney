# r707 bm-a merge probe-2: crash_fuse structure + pool entry delta + paper_export ts
import subprocess, json

def side(f, n):
    return subprocess.run(["git", "show", f":{n}:{f}"], capture_output=True).stdout

# 1) crash_fuse structure
o = json.loads(side("results/crash_fuse.json", 2))
t = json.loads(side("results/crash_fuse.json", 3))
print("fuse ours keys:", list(o.keys()))
print("fuse theirs keys:", list(t.keys()))
for k in o:
    ov, tv = o.get(k), t.get(k)
    if ov == tv:
        print(f"  {k}: IDENTICAL")
    else:
        print(f"  {k}: DIFFERS ours={json.dumps(ov, ensure_ascii=False)[:200]}")
        print(f"  {k}:        theirs={json.dumps(tv, ensure_ascii=False)[:200]}")

# 2) pool entries delta
o = json.loads(side("results/runnable_pool.json", 2))
t = json.loads(side("results/runnable_pool.json", 3))
oe = {e["id"]: e for e in o["entries"]}
te = {e["id"]: e for e in t["entries"]}
print("\npool: ours", len(o["entries"]), "theirs", len(t["entries"]),
      "ids-equal:", set(oe) == set(te))
print("ours-only ids:", sorted(set(oe) - set(te))[:10])
print("theirs-only ids:", sorted(set(te) - set(oe))[:10])
ndiff = 0
for eid in sorted(set(oe) & set(te)):
    if oe[eid] != te[eid]:
        ndiff += 1
        if ndiff <= 14:
            os_, ts_ = oe[eid].get("status"), te[eid].get("status")
            osh = {s.get("shard_id", i): s for i, s in enumerate(oe[eid].get("shards", []))}
            tsh = {s.get("shard_id", i): s for i, s in enumerate(te[eid].get("shards", []))}
            bits = []
            for sid in sorted(set(osh) | set(tsh)):
                a, b = osh.get(sid), tsh.get(sid)
                if a != b:
                    bits.append(f"{sid}: O[{(a or {}).get('owner')},{(a or {}).get('status')},{(a or {}).get('owner_since','')[-14:]},{(a or {}).get('done_at','')[-14:]}] T[{(b or {}).get('owner')},{(b or {}).get('status')},{(b or {}).get('owner_since','')[-14:]},{(b or {}).get('done_at','')[-14:]}]")
            print(f"  DIFF {eid} status O={os_} T={ts_} :: " + " | ".join(bits[:4]))
print("total differing entries:", ndiff)

# 3) paper_export nested ts
for f in ("results/paper_export/export-2026-09-30.json", "results/paper_export/latest.json"):
    o2 = json.loads(side(f, 2)); t2 = json.loads(side(f, 3))
    same = o2 == t2
    tsf = {k: v for k, v in o2.items() if isinstance(v, str) and "2026-10" in v}
    print(f"\n{f} identical={same} ts-fields={tsf}")
    if not same:
        for k in o2:
            if o2.get(k) != t2.get(k):
                print(f"   differs at key {k}: O={json.dumps(o2.get(k))[:150]}")
                print(f"   differs at key {k}: T={json.dumps(t2.get(k))[:150]}")
