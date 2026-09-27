# -*- coding: utf-8 -*-
"""r346 bm-b resolver v2: autofill_state.json UU via full stage blobs.
ours=:2: (HEAD=origin/bm-c tick) theirs=:3: (replayed local bm-b tick ccd31d5e).
Canon: last_tick=max ts (r84 tie->ours); launches=union dedup (ts,machine,entry,shard,pid).
Probe law r110: every git show must rc==0 AND non-empty before use.
"""
import json, subprocess, sys

P = 'results/autofill_state.json'

def show(stage):
    r = subprocess.run(['git', 'show', f':{stage}:{P}'], capture_output=True)
    if r.returncode != 0 or not r.stdout:
        print(f'FATAL: :{stage}: probe rc={r.returncode} len={len(r.stdout)}'); sys.exit(1)
    return json.loads(r.stdout.decode('utf-8'))

a = show(2)  # ours = HEAD (origin/bm-c)
b = show(3)  # theirs = replayed (local bm-b tick)

la, lb = a.get('launches', []), b.get('launches', [])
seen, union = set(), []
for rec in la + lb:
    k = (rec.get('ts'), rec.get('machine'), rec.get('entry'), rec.get('shard'), rec.get('pid'))
    if k in seen: continue
    seen.add(k); union.append(rec)
union.sort(key=lambda r: (r.get('ts') or '', r.get('machine') or ''))

ta = a.get('last_tick', {}).get('ts', '')
tb = b.get('last_tick', {}).get('ts', '')
winner = a if (ta or '') >= (tb or '') else b
print(f'last_tick: ours(HEAD) {ta} vs theirs {tb} -> winner machine={winner.get("last_tick",{}).get("machine")}')
print(f'launches: {len(la)}+{len(lb)} -> union {len(union)} (dropped {len(la)+len(lb)-len(union)} dups)')
base_keys = set(a.keys()) | set(b.keys())
print('top-level keys union:', sorted(base_keys))

merged = {}
# prefer non-launch fields from the fresher last_tick side, but carry any key only one side has
src, other = (a, b) if winner is a else (b, a)
for k in base_keys:
    if k == 'launches': continue
    merged[k] = src[k] if k in src else other[k]
merged['launches'] = union
out = json.dumps(merged, ensure_ascii=False, indent=1)
open(P, 'wb').write((out + '\n').encode('utf-8'))
json.loads(open(P, encoding='utf-8').read())

subprocess.run(['git', 'add', P], check=True)
r = subprocess.run(['git', '-c', 'core.editor=true', 'rebase', '--continue'], capture_output=True, text=True)
print('rebase --continue rc=', r.returncode)
print((r.stdout or '')[-500:])
print((r.stderr or '')[-300:])
sys.exit(r.returncode)
