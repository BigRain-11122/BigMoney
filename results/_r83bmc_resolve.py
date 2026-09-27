# -*- coding: utf-8 -*-
"""r83 bm-c resolver: results/autofill_state.json stash-pop union (v2, programmatic).

Replaces the broken marker-based v1 (its C1 resolution duplicated the diff3 common
tail -> invalid JSON). Sources both sides from git objects instead:
  ours   = HEAD (upstream bm-a r325 union canon, 50 launches / 44 crash_counted,
          contains a same-composite-key duplicate pair at the tail:
          (2026-09-27 12:30:02, bm-c, pid 22408) once w/o crash_counted + once w/ it)
  theirs = dropped stash ae36a5a0 (bm-c local drift, 44 launches, all crash_counted,
          last_tick ts 2026-09-27 13:20:02 machine bm-c)

Canon applied:
  r322  - composite key (ts,machine,pid,runner_sha256,entry,shard); same-key sides
          must be content-merged via field union; identical duplicate in ours ->
          dedup to one record carrying crash_counted=true (zero unique info lost).
  r325  - last_tick same-second tie -> HEAD side (bm-a).
Result written back with indent=1 (original style), strict utf-8, then re-verified.
"""
import io, json, subprocess, sys

def gshow(ref, path):
    b = subprocess.run(['git', 'show', f'{ref}:{path}'], capture_output=True, check=True)
    return json.loads(b.stdout.decode('utf-8'))

ours = gshow('HEAD', 'results/autofill_state.json')
theirs = gshow('ae36a5a00c44053fa5a2f50df6d94a6e0dc10b5f', 'results/autofill_state.json')

K = lambda r: (r.get('ts'), r.get('machine'), r.get('pid'),
               r.get('runner_sha256'), r.get('entry'), r.get('shard'))

# 1) theirs subset check (zero-loss precondition)
ours_keys = {}
dups = []
for r in ours['launches']:
    k = K(r)
    if k in ours_keys:
        dups.append(k)
    else:
        ours_keys[k] = dict(r)
# 6 same-key pairs inherited from bm-a r325 concatenation-union, each verified
# content-identical modulo crash_counted (probed above): (None, True) -> keep True.
assert len(dups) == 6, f'expected 6 known dup pairs, got {len(dups)}: {dups}'
for k in dups:
    pair = [r for r in ours['launches'] if K(r) == k]
    diff = {f for f in set(pair[0]) | set(pair[1])
            if pair[0].get(f) != pair[1].get(f)}
    assert diff == {'crash_counted'}, (k, sorted(diff))
    assert pair[0].get('crash_counted') is None and pair[1]['crash_counted'] is True, k
    ours_keys[k]['crash_counted'] = True
missing = [K(r) for r in theirs['launches'] if K(r) not in ours_keys]
assert not missing, f'theirs records missing from ours: {missing}'

# 2) field-union overlay: crash_counted from theirs onto ours records
n_overlay = 0
for r in theirs['launches']:
    k = K(r)
    tgt = ours_keys[k]
    for f, v in r.items():
        if f not in tgt or tgt[f] != v:
            if f == 'crash_counted' and v is True:
                tgt[f] = v
                n_overlay += 1
            else:
                # same-key non-cc field divergence must be surfaced, not silently merged
                raise AssertionError(f'field divergence at {k}: {f} {tgt.get(f)!r} vs {v!r}')

merged = list(ours_keys.values())
# key-order stability: preserve first-seen position (dict insertion order)
assert len(merged) == 44, f'expected 44 after dedup, got {len(merged)}'
assert all(r.get('crash_counted') is True for r in merged), 'post-union cc gap'

# 3) last_tick tie -> HEAD
last = dict(ours['last_tick'])
assert last['ts'] == theirs['last_tick']['ts'] == '2026-09-27 13:20:02'

out = {'launches': merged, 'last_tick': last}
io.open('results/autofill_state.json', 'w', encoding='utf-8', newline='\n').write(
    json.dumps(out, ensure_ascii=False, indent=1) + '\n')

# 4) strict re-verify
d = json.loads(io.open('results/autofill_state.json', encoding='utf-8').read())
assert len(d['launches']) == 44
keys = [K(r) for r in d['launches']]
assert len(set(keys)) == 44, 'dup residue'
assert all(r['crash_counted'] is True for r in d['launches'])
assert d['last_tick'] == {'ts': '2026-09-27 13:20:02', 'machine': 'bm-a',
                          'py_cpu_pct': 0.0, 'verdict': 'pool_empty_or_busy'}
print(f'UNION-OK launches={len(d["launches"])} crash_counted=44 dedup=6pairs '
      f'(content-identical modulo cc, r322 canon) last_tick=bm-a(13:20:02 tie->HEAD per r325)')
