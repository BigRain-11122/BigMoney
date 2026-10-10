# -*- coding: utf-8 -*-
# r859 bm-c: classify shared dirty faces vs origin (twin vs ts-diff) pre-rebase
import subprocess, json, re

mine = subprocess.run(['git', 'status', '--short'], capture_output=True, text=True).stdout.splitlines()
dirty = []
for l in mine:
    s = l.rstrip('\n')
    if not s.strip():
        continue
    code = s[:2]
    path = s[3:].strip().strip('"')
    if 'M' in code:
        dirty.append(path)
inc = subprocess.run(['git', 'diff', '--name-only', 'HEAD', 'origin/main'],
                     capture_output=True, text=True).stdout.splitlines()
shared = sorted(set(dirty) & set(inc))
print('SHARED FACES:', len(shared))


def ts(b):
    try:
        d = json.loads(b.decode('utf-8', errors='replace'))
        if isinstance(d, dict):
            for k in ('ts', 'updated_at', 'updated', 'time', 'asof', 'generated_at', 'scan_ts', 'last_scan'):
                if d.get(k):
                    return '%s=%s' % (k, d[k])
            return str(list(d.items())[:1])[:70]
        return 'n/a'
    except Exception:
        m = re.search(rb'(20\d\d-\d\d-\d\d[T ]\d\d:\d\d)', b[:3000])
        return m.group(1).decode() if m else 'n/a'


for f in shared:
    try:
        wt = open(f, 'rb').read()
    except OSError:
        print('MISSING-WT', f)
        continue
    org = subprocess.run(['git', 'show', 'origin/main:' + f], capture_output=True).stdout
    if wt == org:
        print('TWIN', f)
        continue
    print('DIFF', f, '| mine:', ts(wt), '| theirs:', ts(org))
