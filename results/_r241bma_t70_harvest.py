# -*- coding: utf-8 -*-
"""R241 T-70: per-task verdict harvest B vs C (functional axis + fix rounds)."""
import io
import json
import glob
import os

rows = []
for tdir in sorted(glob.glob('results/local_coding_pilot/tasks/*/')):
    tid = os.path.basename(tdir.rstrip('/\\'))
    row = {'task': tid}
    for arm in ('A', 'B', 'C'):
        mp = os.path.join(tdir, arm, 'metrics.json')
        if os.path.exists(mp):
            try:
                m = json.load(io.open(mp, encoding='utf-8'))
                if isinstance(m, list):
                    m = m[-1] if m else {}
                row[arm] = {
                    'verdict': m.get('verdict'),
                    'exit': m.get('exit', m.get('exit_code')),
                    'fix_rounds': m.get('fix_rounds', m.get('rounds')),
                    'keys': sorted(m.keys())[:10],
                }
            except Exception as e:
                row[arm] = {'err': str(e)[:80]}
    rows.append(row)

for r in rows:
    print(f"task {r['task']}:")
    for arm in ('A', 'B', 'C'):
        v = r.get(arm)
        if v:
            print(f"  {arm}: {json.dumps(v, ensure_ascii=False)[:220]}")
print()
cs = json.load(io.open('results/local_coding_pilot/C_batch_status.json',
                       encoding='utf-8'))
print('C batch mode:', cs.get('mode'), 'current:', cs.get('current'),
      'updated:', cs.get('updated'))
