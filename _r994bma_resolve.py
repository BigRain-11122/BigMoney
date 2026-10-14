# -*- coding: utf-8 -*-
"""r994 rebase conflict resolve: 8 runtime status faces, ts-newer-wins per file."""
import subprocess, json, sys

GIT = r"C:\Program Files\Git\cmd\git.exe"
FILES = [
    'results/_attrition_guard_scan.json',
    'results/compute_audit.json',
    'results/fundamental_b_layer_filter.json',
    'results/futures_update_status.json',
    'results/lhb_update_status.json',
    'results/regime_state.json',
    'results/token_usage.json',
    'results/update_status.json',
]

def side_ts(rev, path):
    try:
        out = subprocess.run([GIT, 'show', f'{rev}:{path}'], capture_output=True).stdout
        j = json.loads(out.decode('utf-8', errors='replace'))
        for k in ('ts', 'generated_at', 'scan_ts', 'written_at'):
            if k in j and isinstance(j[k], str):
                return j[k]
        return ''
    except Exception:
        return None  # unparsable

for f in FILES:
    ours = side_ts(':2', f)
    theirs = side_ts(':3', f)
    if ours is None and theirs is None:
        pick = ':2'  # both unparsable -> ours
        why = 'both-unparsable'
    elif ours is None:
        pick = ':3'; why = 'ours-unparsable'
    elif theirs is None:
        pick = ':2'; why = 'theirs-unparsable'
    else:
        pick = ':2' if ours >= theirs else ':3'
        why = f'ts {ours} vs {theirs}'
    blob = subprocess.run([GIT, 'show', f'{pick}:{f}'], capture_output=True).stdout
    with open(f, 'wb') as fh:
        fh.write(blob)
    subprocess.run([GIT, 'add', f], check=True)
    print(f'{f}: pick {pick} ({why})')
print('RESOLVED 8/8')
