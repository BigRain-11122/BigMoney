# r91 bm-c: results/autofill_state.json union resolver v2
# v1 lesson: staged the UU worktree too early -> :1:/:2:/:3: blobs gone (r90 pitlaw cousin).
# v2 reads the two live sides directly: HEAD:file = post-rebase remote-ledger,
# stash@{0}:file = pre-pull local worktree (superset of r90 committed version).
# Union = launches whole-entry dedup (canonical json), sort by ts, last_tick = newer ts.
import json, subprocess, sys

def show(ref):
    p = subprocess.run(['git', 'show', f'{ref}:results/autofill_state.json'],
                       capture_output=True)
    if p.returncode != 0:
        print(f'FATAL git show {ref} rc={p.returncode}'); sys.exit(2)
    return json.loads(p.stdout.decode('utf-8'))

oa, ta = show('HEAD'), show('stash@{0}')
ol, tl = oa.get('launches', []), ta.get('launches', [])
assert isinstance(ol, list) and isinstance(tl, list), 'launches must be list on both sides'

def canon(e):
    return json.dumps(e, sort_keys=True, ensure_ascii=False)

seen, union = set(), []
for e in ol + tl:
    k = canon(e)
    if k not in seen:
        seen.add(k)
        union.append(e)
union.sort(key=lambda e: str(e.get('ts', '')))

cap = max(len(ol), len(tl), 48)
trimmed = union[-cap:] if len(union) > cap else union

ot, tt = oa.get('last_tick'), ta.get('last_tick')
def tick_ts(x):
    return str(x.get('ts', '')) if isinstance(x, dict) else str(x or '')
last_tick = ot if tick_ts(ot) >= tick_ts(tt) else tt

out = {'launches': trimmed, 'last_tick': last_tick}
with open('results/autofill_state.json', 'w', encoding='utf-8', newline='') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
    f.write('\n')
newest = trimmed[-1].get('ts') if trimmed else 'EMPTY'
print(f'HEAD={len(ol)} stash={len(tl)} union={len(union)} kept={len(trimmed)} '
      f'dup={len(ol)+len(tl)-len(union)} cap={cap} last_tick={tick_ts(last_tick)} newest_launch={newest}')
