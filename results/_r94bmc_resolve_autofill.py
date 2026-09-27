# r94 bm-c: results/autofill_state.json union resolver v3 (r93 identity-key law lineage)
# Law (r93): identity keys = ts+machine+entry+shard. Same-identity field-variants are ONE event.
# If identity sets equal (old_only=0 and head_only=0) -> take HEAD verbatim (more complete side wins).
# Else union by identity (prefer HEAD entry on collision), sort by ts, cap=max(len,48), last_tick=take-newer.
# Writer format law (r91/r93): indent=1 + trailing newline.
import json, subprocess, sys

def show(ref):
    p = subprocess.run(['git', 'show', f'{ref}:results/autofill_state.json'],
                       capture_output=True)
    if p.returncode != 0:
        print(f'FATAL git show {ref} rc={p.returncode}'); sys.exit(2)
    return json.loads(p.stdout.decode('utf-8'))

def ident(e):
    return (str(e.get('ts', '')), str(e.get('machine', '')),
            str(e.get('entry', '')), str(e.get('shard', '')))

oa, ta = show('HEAD'), show('stash@{0}')
ol, tl = oa.get('launches', []), ta.get('launches', [])
assert isinstance(ol, list) and isinstance(tl, list), 'launches must be list on both sides'

oi, ti = {ident(e) for e in ol}, {ident(e) for e in tl}
old_only = oi - ti          # events only in stash (pre-pull local) side
head_only = ti - oi          # events only in HEAD (post-rebase remote) side
print(f'HEAD={len(ol)} stash={len(tl)} ident_HEAD={len(oi)} ident_stash={len(ti)} '
      f'old_only={len(old_only)} head_only={len(head_only)}')

if not old_only and not head_only:
    out = {'launches': ol, 'last_tick': oa.get('last_tick')}
    verdict = 'IDENTITY-EQUAL -> take-HEAD-verbatim'
elif not old_only:
    out = {'launches': ol, 'last_tick': oa.get('last_tick')}
    verdict = 'STASH-SUBSET -> take-HEAD (no new local events; keepalive only?)'
else:
    merged = {}
    for e in ol:
        merged[ident(e)] = e
    for e in tl:                      # stash side fills gaps, never overwrites HEAD entries
        k = ident(e)
        if k not in merged:
            merged[k] = e
    union = sorted(merged.values(), key=lambda e: str(e.get('ts', '')))
    cap = max(len(ol), len(tl), 48)
    trimmed = union[-cap:] if len(union) > cap else union
    out = {'launches': trimmed}
    verdict = f'UNION kept={len(trimmed)} (merged={len(union)}, cap={cap})'

ot, tt = oa.get('last_tick'), ta.get('last_tick')
def tick_ts(x):
    return str(x.get('ts', '')) if isinstance(x, dict) else str(x or '')
out['last_tick'] = ot if tick_ts(ot) >= tick_ts(tt) else tt

with open('results/autofill_state.json', 'w', encoding='utf-8', newline='') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
    f.write('\n')
chk = json.load(open('results/autofill_state.json', encoding='utf-8'))
assert isinstance(chk['launches'], list)
print(f'{verdict} | last_tick={tick_ts(out["last_tick"])} | JSON-valid ok')
