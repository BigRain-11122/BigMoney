import subprocess, json


def stage_blob(path, stage):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    return json.loads(r.stdout.decode('utf-8'))


faces = ['results/compute_audit.json', 'results/futures_update_status.json',
         'results/lhb_update_status.json', 'results/queue_head_collision_probe.json',
         'results/regime_state.json', 'results/scorecard_v1.json',
         'results/strategy_scorecard.json', 'results/update_status.json']

META_KEYS = {'generated', 'generated_at', 'elapsed_sec', 'ts', 'updated', 'meta'}


def strip_meta(obj):
    if isinstance(obj, dict):
        return {k: strip_meta(v) for k, v in obj.items() if k not in META_KEYS}
    if isinstance(obj, list):
        return [strip_meta(x) for x in obj]
    return obj


def find_ts(obj, depth=0):
    hits = []
    if depth > 3 or not isinstance(obj, dict):
        return hits
    for k, v in obj.items():
        kl = str(k).lower()
        if isinstance(v, str) and ('ts' in kl or 'time' in kl or 'date' in kl or 'updated' in kl or 'generated' in kl):
            if len(v) >= 8:
                hits.append((k, v))
        elif isinstance(v, dict):
            hits.extend(find_ts(v, depth + 1))
    return hits[:5]


for p in faces:
    o = stage_blob(p, 2)
    t = stage_blob(p, 3)
    print('=' * 16, p)
    print('  OURS ts:', find_ts(o))
    print('  THEIRS ts:', find_ts(t))
    if p in ('results/scorecard_v1.json', 'results/strategy_scorecard.json'):
        print('  data-identical(meta-strip):', strip_meta(o) == strip_meta(t))
    if p == 'results/compute_audit.json':
        print('  OURS history:', len(o.get('history', [])), 'THEIRS history:', len(t.get('history', [])))
