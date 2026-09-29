# r447 bm-b rebase wedge-2 resolver: runnable_pool.json single-file union
# ours(:2) = bm-a 8c8d609a6 (adds INNOVATION-QUOTA-SLOT-6, W12-JUDGE stale 'ready')
# theirs(:3) = bm-b round 447 (W12-JUDGE -> 'done' flip, no SLOT-6)
# Recipe: entries union by id (zero loss, both sides' changes kept), W12-JUDGE state
# takes bm-b 'done' (judgment completed 05:17:43, finalize 05:22:37 = newer face).
# Producer format: CRLF + indent=1, re-emitted exactly.
import subprocess, json

def blob(n):
    return subprocess.run(['git', 'show', f':{n}:results/runnable_pool.json'], capture_output=True).stdout

ours = json.loads(blob(2).decode('utf-8'))
theirs = json.loads(blob(3).decode('utf-8'))

def key(e):
    return e.get('id') or e.get('name')

tmap = {key(e): e for e in theirs['entries']}
merged_entries = []
for e in ours['entries']:
    k = key(e)
    if k in tmap and json.dumps(tmap[k], sort_keys=True, ensure_ascii=False) != json.dumps(e, sort_keys=True, ensure_ascii=False):
        merged_entries.append(tmap[k])  # both-modified: take theirs (W12-JUDGE done)
    else:
        merged_entries.append(e)
for e in theirs['entries']:
    if key(e) not in {key(x) for x in merged_entries}:
        merged_entries.append(e)  # theirs-only entries (none expected this wedge)

res = dict(ours)
res['entries'] = merged_entries
out = json.dumps(res, ensure_ascii=False, indent=1).replace('\n', '\r\n')
with open('results/runnable_pool.json', 'w', encoding='utf-8', newline='') as f:
    f.write(out)

# verify (r185 law) before add
chk = json.loads(open('results/runnable_pool.json', encoding='utf-8').read())
ids = [key(e) for e in chk['entries']]
assert len(ids) == len(set(ids)), 'dup ids'
assert len(ids) == 132, f'entry count {len(ids)} != 132'
w12 = [e for e in chk['entries'] if key(e) == 'TRIAL-LABOR-W12-JUDGE'][0]
assert w12['status'] == 'done', w12['status']
assert 'INNOVATION-QUOTA-SLOT-6' in ids
print(f'pool union OK: {len(ids)} entries, W12-JUDGE=done, SLOT-6 present')
subprocess.run(['git', 'add', 'results/runnable_pool.json'], check=True)
print('staged')
