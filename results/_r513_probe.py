import subprocess, json

def side(p, s):
    return json.loads(subprocess.check_output(['git', 'show', f':{s}:{p}']).decode('utf-8-sig'))

for p in ('results/p1d_gates.json',):
    for s, label in ((2, 'OURS(origin-base)'), (3, 'THEIRS(my-ride)')):
        d = side(p, s)
        meta = d.get('meta', {})
        print(p, label, 'meta=', {k: meta.get(k) for k in ('ts', 'generated', 'cutoff', 'asof') if k in meta})

p = 'results/autofill_state.bm-b.json'
for s, label in ((2, 'OURS(origin-base)'), (3, 'THEIRS(my-ride)')):
    d = side(p, s)
    lt = d.get('last_tick', {})
    launches = d.get('launches', [])
    print(p, label, 'last_tick ts=', lt.get('ts'), '| launches n=', len(launches), '| first/last ts=', (launches[0].get('ts'), launches[-1].get('ts')) if launches else None, '| core_samples_seen type=', type(d.get('core_samples_seen')).__name__, '| lane_machine=', d.get('lane_machine'))

for p in ('results/pool_core_samples.jsonl', 'results/saturation_engine/history_bm-b.jsonl', 'results/saturation_engine/ledger_bm-b.jsonl'):
    for s, label in ((2, 'base'), (3, 'mine')):
        out = subprocess.check_output(['git', 'show', f':{s}:{p}'])
        lines = out.decode('utf-8-sig').splitlines()
        print(p, label, 'lines=', len(lines), '| first=', lines[0][:80] if lines else '', '| last=', lines[-1][:80] if lines else '')
