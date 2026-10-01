"""r504 bm-b: origin-truth pool check (r513 stale-view law) -- what is ready/claimable
on origin/main runnable_pool.json, and what supply waves exist."""
import subprocess, json

raw = subprocess.check_output(['git', 'show', 'origin/main:results/runnable_pool.json'],
                              encoding='utf-8')
pool = json.loads(raw)
entries = pool['entries'] if isinstance(pool, dict) else pool
if isinstance(entries, dict):
    entries = list(entries.values())

from collections import Counter
st = Counter(e.get('status', '?') for e in entries)
print('total entries:', len(entries))
print('status counts:', dict(st))

ready = [e for e in entries if e.get('status') == 'ready']
for e in ready:
    shards = e.get('shards', [])
    sh_st = Counter(s.get('status', '?') for s in shards) if shards else {}
    print('READY:', e.get('id'), '| shards:', dict(sh_st) if sh_st else 'no-shards',
          '| owner:', e.get('owner'), '| runner:', e.get('runner', e.get('script', '?')))

# perpetual wave census
waves = Counter()
for e in entries:
    i = e.get('id', '')
    if 'N1-W' in i:
        waves[i.split('-W')[0] + '-W' + i.split('-W')[1].split('-')[0]] = waves.get(
            i.split('-W')[0] + '-W' + i.split('-W')[1].split('-')[0], 0) + 1
print('perpetual N1 waves:', dict(sorted(waves.items())))
