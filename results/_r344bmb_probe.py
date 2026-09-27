import subprocess, json

def run(args):
    r = subprocess.run(args, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(repr(r.stderr[:200]))
    return r.stdout

# parse stages
out = run(['git', 'ls-files', '-u']).decode('utf-8')
blobs = {}  # (stage,path) -> sha
for line in out.strip().splitlines():
    meta, path = line.split('\t')
    mode, sha, stage = meta.split()
    blobs[(int(stage), path)] = sha

def side(path, stage):
    return run(['git', 'cat-file', '-p', blobs[(stage, path)]])

def jload(b):
    return json.loads(b.decode('utf-8'))

files = ['fleet/machines/bm-b.json', 'logs/iteration-loop/state.json',
         'results/astock_daily_update_status.json', 'results/autofill_state.json',
         'results/compute_audit.json', 'results/regime_state.json']
for p in files:
    try:
        b2, b3 = side(p, 2), side(p, 3)
        d2, d3 = jload(b2), jload(b3)
        print('=====', p)
        for k in ('round_no', 'round', 'last_seen', 'updated_at', 'ts', 'heartbeat_epoch_utc', 'generated', 'asof', 'cutoff'):
            if isinstance(d2, dict) and k in d2: print('  ours(origin) ', k, '=', str(d2[k])[:70])
            if isinstance(d3, dict) and k in d3: print('  theirs(r339) ', k, '=', str(d3[k])[:70])
        if p == 'results/autofill_state.json':
            print('  ours last_tick.ts=', (d2.get('last_tick') or {}).get('ts'), 'launches=', len(d2.get('launches', [])))
            print('  theirs last_tick.ts=', (d3.get('last_tick') or {}).get('ts'), 'launches=', len(d3.get('launches', [])))
        if p == 'results/compute_audit.json':
            print('  ours history=', len(d2.get('history', [])), 'theirs history=', len(d3.get('history', [])))
        if p == 'results/regime_state.json':
            for kk in ('transitions', 'history', 'snapshots', 'states'):
                if kk in d2 or kk in d3:
                    print('  ', kk, 'ours=', len(d2.get(kk, [])), 'theirs=', len(d3.get(kk, [])))
        if p == 'results/astock_daily_update_status.json':
            print('  ours keys=', sorted(d2.keys())[:12])
            print('  theirs keys=', sorted(d3.keys())[:12])
    except Exception as e:
        print('=====', p, 'ERR', repr(e)[:200])

# round_reports.md tails
p = 'logs/iteration-loop/round_reports.md'
t2 = side(p, 2).decode('utf-8', 'replace').splitlines()
t3 = side(p, 3).decode('utf-8', 'replace').splitlines()
print('=====', p, 'ours_lines=', len(t2), 'theirs_lines=', len(t3))
print('  ours tail2:', [l[:110] for l in t2[-2:]])
print('  theirs tail2:', [l[:110] for l in t3[-2:]])
common = 0
for a, b in zip(t2, t3):
    if a == b: common += 1
    else: break
print('  common_prefix_lines=', common)
