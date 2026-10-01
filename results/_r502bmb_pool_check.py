import json, subprocess
pool = json.load(open('results/runnable_pool.json', encoding='utf-8'))
entries = pool if isinstance(pool, list) else pool.get('entries', pool.get('pool', []))
if isinstance(entries, dict):
    entries = list(entries.values())
for e in entries:
    st = e.get('status')
    eid = e.get('id', '')
    if any(k in eid for k in ('W7', 'W8', 'STOCKFURN')):
        shards = e.get('shards', [])
        done = sum(1 for s in shards if isinstance(s, dict) and s.get('status') == 'done')
        print(f"{eid}: entry={st} shards {done}/{len(shards)}")
# product presence on origin for W7
out = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', 'origin/main', 'results/perpetual_faces/'])
w7 = [l for l in out.decode().splitlines() if 'N1-W7' in l and 'SHARD' in l]
print(f"\nW7 product files on origin: {len(w7)}")
for l in w7[:16]:
    print(' ', l)
