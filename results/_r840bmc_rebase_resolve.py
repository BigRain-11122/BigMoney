# -*- coding: utf-8 -*-
# r840 bm-c rebase resolver: 14 UU shared regen faces -> per-face ts-duel newer-wins;
# jsonl/history-array faces -> union. Then stage, atomic continue.
import subprocess, json, re

files = subprocess.run(['git', 'diff', '--name-only', '--diff-filter=U'],
                       capture_output=True, text=True).stdout.split()

def blob(stage, f):
    return subprocess.run(['git', 'show', ':%s:%s' % (stage, f)], capture_output=True).stdout

TS_RE = re.compile(r'"(ts|generated|generated_at|asof)"\s*:\s*"([^"]+)"')

def ts_of(b):
    m = TS_RE.search(b[:3000].decode('utf-8', 'replace'))
    return m.group(2) if m else ''

report = []
for f in files:
    ours, theirs = blob(2, f), blob(3, f)
    o, t = ts_of(ours), ts_of(theirs)
    if o and t:
        winner = 'ours' if o >= t else 'theirs'
    elif o and not t:
        winner = 'ours'
    elif t and not o:
        winner = 'theirs'
    else:
        winner = 'ours'  # no ts visible: our S6 just regenerated; keep local
    # history-array / jsonl faces: union merge (append-only)
    union = False
    if f.endswith('.jsonl'):
        union = True
    else:
        try:
            jo = json.loads(ours); jt = json.loads(theirs)
            if isinstance(jo, dict) and isinstance(jt, dict) and 'history' in jo and 'history' in jt:
                union = True
        except Exception:
            pass
    if union:
        # jsonl: line-level union preserving order (ours first, append theirs-only lines)
        if f.endswith('.jsonl'):
            lo = [l for l in ours.decode('utf-8', 'replace').splitlines() if l.strip()]
            lt = [l for l in theirs.decode('utf-8', 'replace').splitlines() if l.strip()]
            so = set(lo)
            merged = lo + [l for l in lt if l not in so]
            data = ('\n'.join(merged) + '\n').encode('utf-8')
        else:
            jo = json.loads(ours); jt = json.loads(theirs)
            ho = jo.get('history', []); ht = jt.get('history', [])
            seen = {json.dumps(h, sort_keys=True, ensure_ascii=False) for h in ho}
            jo['history'] = ho + [h for h in ht if json.dumps(h, sort_keys=True, ensure_ascii=False) not in seen]
            data = json.dumps(jo, ensure_ascii=False, indent=1).encode('utf-8')
        verdict = 'UNION'
    else:
        data = ours if winner == 'ours' else theirs
        verdict = winner.upper()
    with open(f, 'wb') as fh:
        fh.write(data)
    report.append('%s :: %s (ours=%s theirs=%s)' % (f, verdict, o or '-', t or '-'))

print('\n'.join(report))
# marker hard gate: no conflict markers in any resolved face
bad = []
for f in files:
    b = open(f, 'rb').read()
    if b'<<<<<<<' in b or b'>>>>>>>' in b:
        bad.append(f)
print('MARKER_CHECK:', 'CLEAN' if not bad else 'DIRTY ' + ','.join(bad))
subprocess.run(['git', 'add', '-A'])
print('STAGED_FOR_CONTINUE')
