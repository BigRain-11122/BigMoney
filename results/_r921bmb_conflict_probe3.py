import subprocess, json


def stage_blob(path, stage):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    return json.loads(r.stdout.decode('utf-8'))


o = stage_blob('results/d19_watermark.json', 2)
t = stage_blob('results/d19_watermark.json', 3)
print('d19_watermark OURS:', json.dumps(o, ensure_ascii=False, sort_keys=True)[:600])
print()
print('d19_watermark THEIRS:', json.dumps(t, ensure_ascii=False, sort_keys=True)[:600])
print()
mh_o = stage_blob('fleet/machine-health.json', 2)
mh_t = stage_blob('fleet/machine-health.json', 3)
print('machine-health OURS rows:')
for r in mh_o:
    print('  ', {k: r.get(k) for k in list(r.keys())[:8]})
print('machine-health THEIRS rows:')
for r in mh_t:
    print('  ', {k: r.get(k) for k in list(r.keys())[:8]})
