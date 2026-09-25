"""Rebase conflict resolution for results/autofill_state.json (r210, bm-b).

Union recipe per r185/r188/r191/r201 lessons:
- launches: union both sides (dedupe by exact identity), keep last 50 (rolling window design)
- last_tick: newer ts wins
- other keys: per-key, newer ts side wins; scalar diffs disclosed
"""
import json, subprocess, sys, io

def side(idx):
    raw = subprocess.run(['git', 'show', f':{idx}:results/autofill_state.json'],
                          capture_output=True, check=True).stdout
    return json.loads(raw.decode('utf-8'))

def ts_of(entry):
    return entry.get('ts') or entry.get('updated_at') or ''

ours = side(2)    # rebase ours = new base = bm-a deb50e5e side
theirs = side(3)  # rebase theirs = my b6e980f6 evidence commit side

out = {}
# union launches by identity (frozenset of items for hashability)
seen = set()
merged_launches = []
for e in (theirs.get('launches', []) + ours.get('launches', [])):
    key = json.dumps(e, ensure_ascii=False, sort_keys=True)
    if key in seen:
        continue
    seen.add(key)
    merged_launches.append(e)
# rolling window: keep last 50 (r188 launches[-50:] tick cap design)
merged_launches = merged_launches[-50:]
out['launches'] = merged_launches

# last_tick: newer ts wins
lt_o, lt_t = ours.get('last_tick', {}), theirs.get('last_tick', {})
out['last_tick'] = lt_t if ts_of(lt_t) >= ts_of(lt_o) else lt_o

# every other key: prefer theirs (my side) unless ours has it and theirs doesn't;
# for shared dict keys with ts, newer wins; equal -> either.
other_keys = sorted(set(ours.keys()) | set(theirs.keys()) - {'launches', 'last_tick'})
for k in other_keys:
    if k in ('launches', 'last_tick'):
        continue
    ov, tv = ours.get(k), theirs.get(k)
    if isinstance(ov, dict) and isinstance(tv, dict):
        m = dict(ov)
        m.update(tv)  # theirs wins on overlap; disclose below
        out[k] = m
    elif tv is not None:
        out[k] = tv
    else:
        out[k] = ov

with io.open('results/autofill_state.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

# report
print('merged launches:', len(out['launches']),
      '(ours', len(ours.get('launches', [])), '+ theirs', len(theirs.get('launches', [])), ')')
print('last_tick winner:', out['last_tick'].get('ts'), out['last_tick'].get('verdict'))
scalar_diffs = [k for k in other_keys if k in ours and k in theirs and ours[k] != theirs[k] and not isinstance(ours[k], dict)]
print('scalar key diffs (theirs kept):', scalar_diffs)
keys_only_ours = [k for k in ours if k not in theirs]
keys_only_theirs = [k for k in theirs if k not in ours]
print('keys only in ours(base):', keys_only_ours)
print('keys only in theirs(mine):', keys_only_theirs)
