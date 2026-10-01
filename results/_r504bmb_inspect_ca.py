"""r504 bm-b: inspect compute_audit.json conflict stages via raw git bytes (r209 law)."""
import subprocess, json

for side, spec in [('ours(S2=origin-side)', ':2:'), ('theirs(S3=local-pick)', ':3:')]:
    raw = subprocess.check_output(['git', 'show', spec + 'results/compute_audit.json'])
    d = json.loads(raw.decode('utf-8'))
    h = d.get('history', [])
    print(side, 'top_ts=', d.get('ts'), 'history_n=', len(h))
    print('  top_keys=', sorted(d.keys()))
    if h:
        print('  hist_row_keys=', sorted(h[-1].keys()))
        print('  last_hist_ts=', h[-1].get('ts'))
