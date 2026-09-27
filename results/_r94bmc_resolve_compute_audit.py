# r94 bm-c: results/compute_audit.json rolling-ledger union resolver (r341 law: whole-entry canonical dedup)
# Sides: HEAD = post-rebase origin/main (bma r341, 229-entry union); REBASE_HEAD = my e0c82ede (my 18:09:52 audit appended).
# Union: whole-entry canonical-json dedup (identical entries collapse), sort by ts, preserve top-level schema from HEAD side.
import json, subprocess, sys

def show(ref):
    p = subprocess.run(['git', 'show', f'{ref}:results/compute_audit.json'], capture_output=True)
    if p.returncode != 0:
        print(f'FATAL git show {ref} rc={p.returncode}'); sys.exit(2)
    return json.loads(p.stdout.decode('utf-8'))

ha, ta = show('HEAD'), show('REBASE_HEAD')
key_h = [k for k in ha.keys() if isinstance(ha[k], list)]
assert key_h, 'no list key found in HEAD compute_audit'
hist_key = key_h[0] if len(key_h) == 1 else max(key_h, key=lambda k: len(ha[k]))
hl, tl = ha.get(hist_key, []), ta.get(hist_key, [])
print(f'top-level keys HEAD={list(ha.keys())} | hist_key={hist_key} HEAD={len(hl)} REBASE_HEAD={len(tl)}')

def canon(e):
    return json.dumps(e, sort_keys=True, ensure_ascii=False)

seen, union = {}, []
for e in hl + tl:
    k = canon(e)
    if k not in seen:
        seen[k] = True
        union.append(e)
union.sort(key=lambda e: str(e.get('ts', '')))

# same-ts content-collision probe (r334 law: disclose, keep both)
ts_seen = {}
collisions = 0
for e in union:
    t = str(e.get('ts', ''))
    if t in ts_seen:
        collisions += 1
    ts_seen[t] = ts_seen.get(t, 0) + 1

out = dict(ha)          # top-level schema (non-history keys) from HEAD side
out[hist_key] = union
if 'latest' in ha and union:
    out['latest'] = union[-1]   # latest = newest entry by ts (my 18:09:52 > bma 17:51:55)
with open('results/compute_audit.json', 'w', encoding='utf-8', newline='') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)  # HEAD blob format: indent=2, NO trailing newline (probed)
chk = json.load(open('results/compute_audit.json', encoding='utf-8'))
n = len(chk[hist_key])
print(f'union={len(union)} raw={len(hl)+len(tl)} dup={len(hl)+len(tl)-len(union)} final={n} same_ts_collisions={collisions}')
newest = union[-1].get('ts') if union else 'EMPTY'
print(f'newest_entry={newest} | JSON-valid ok')
