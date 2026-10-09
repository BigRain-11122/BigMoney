# -*- coding: utf-8 -*-
# r917 bm-a rebase pick-3 (b6ce0f1fd churn-absorb-1) ledger resolve:
# S2 line-union S3 (r910 jsonl union family), marker-line filtered.
import json, subprocess

GIT = r'C:\Program Files\Git\cmd\git.exe'
MARKERS = ('<<<<<<<', '=======', '>>>>>>>')
PATH = 'results/saturation_engine/ledger_bm-a.jsonl'

def show(stage):
    r = subprocess.run([GIT, 'show', ':%s:%s' % (stage, PATH)], capture_output=True)
    return r.stdout.decode('utf-8', 'replace') if r.returncode == 0 else ''

def try_json(s):
    try:
        return json.loads(s)
    except Exception:
        return None

seen, union = set(), []
for ln in (show(2) + '\n' + show(3)).splitlines():
    s = ln.strip()
    if s and s not in seen and not s.startswith(MARKERS):
        seen.add(s)
        union.append(s)

def ts_key(s):
    d = try_json(s)
    for k in ('ts', 'time'):
        v = (d or {}).get(k)
        if isinstance(v, str) and v:
            return v
    return ''

union.sort(key=ts_key)
open(PATH, 'w', encoding='utf-8', newline='').write('\n'.join(union) + ('\n' if union else ''))
print('%s: S2+S3 line-union %d lines' % (PATH, len(union)))

r = subprocess.run([GIT, 'add', PATH], capture_output=True)
assert r.returncode == 0, r.stderr.decode('utf-8', 'replace')[:200]
print('ledger resolved + staged')
