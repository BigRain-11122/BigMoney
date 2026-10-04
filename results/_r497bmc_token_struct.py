import json, subprocess
ours = json.load(open('results/token_usage.json', encoding='utf-8'))
theirs_raw = subprocess.run(['git', 'show', 'origin/main:results/token_usage.json'], capture_output=True).stdout
theirs = json.loads(theirs_raw.decode('utf-8'))
for mid in sorted(ours['machines']):
    o, t = ours['machines'][mid], theirs['machines'].get(mid)
    print("==", mid)
    print("  ours  keys:", sorted(o.keys()))
    print("  theirs keys:", sorted(t.keys()) if t else None)
    same = o == t
    print("  identical:", same)
    if not same:
        for k in sorted(set(o) | set(t)):
            ov, tv = o.get(k), (t or {}).get(k)
            if ov != tv:
                so, st = json.dumps(ov, ensure_ascii=False)[:120], json.dumps(tv, ensure_ascii=False)[:120]
                print("   DIFF %s:\n     ours=%s\n     theirs=%s" % (k, so, st))
