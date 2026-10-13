import subprocess, json


def stage_blob(path, stage):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    return json.loads(r.stdout.decode('utf-8'))


for p in ['fleet/machine-health.json', 'results/compute_audit.json', 'results/_r686bmb_d19_check.json']:
    o = stage_blob(p, 2)
    t = stage_blob(p, 3)
    print('=' * 20, p)
    print('  OURS type:', type(o).__name__, 'THEIRS type:', type(t).__name__)
    if isinstance(o, list):
        print('  OURS rows:', [(r.get('machine_id'), r.get('ts') or r.get('last_seen')) for r in o])
        print('  THEIRS rows:', [(r.get('machine_id'), r.get('ts') or r.get('last_seen')) for r in t])
    else:
        print('  OURS top keys:', list(o.keys())[:14])
        print('  THEIRS top keys:', list(t.keys())[:14])
        if p == 'results/_r686bmb_d19_check.json':
            print('  OURS:', json.dumps(o, ensure_ascii=False)[:500])
            print('  THEIRS:', json.dumps(t, ensure_ascii=False)[:500])
        if p == 'results/compute_audit.json':
            print('  OURS latest:', {k: o.get('latest', {}).get(k) for k in ('machine', 'ts', 'py_cpu_pct')})
            print('  THEIRS latest:', {k: t.get('latest', {}).get(k) for k in ('machine', 'ts', 'py_cpu_pct')})
            print('  OURS history len:', len(o.get('history', [])), 'THEIRS history len:', len(t.get('history', [])))
