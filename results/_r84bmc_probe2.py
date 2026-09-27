# -*- coding: utf-8 -*-
"""r84 bm-c probe2: 7-UU replay batch (2/2 of d9316621 onto ef92ff78).

ours = HEAD = ef92ff78 (bm-a r326), theirs = d9316621 (bm-c r84),
base = merge-base = dd34727b. Pure measurement/ledger faces; zero-loss probe.
"""
import json, subprocess

def blob(ref, path):
    return subprocess.run(['git', 'show', f'{ref}:{path}'],
                          capture_output=True, check=True).stdout

def stage(n, path):
    return blob(f':{n}', path)

P = 'results/prospect_paper/_summary.json'
for n, tag in ((1, 'base'), (2, 'ours(bm-a)'), (3, 'theirs(bm-c)')):
    d = json.loads(stage(n, P))
    print(tag, P, json.dumps(d, ensure_ascii=False)[:300])

for path in ('results/compute_audit.json', 'results/regime_state.json'):
    for n, tag in ((1, 'base'), (2, 'ours'), (3, 'theirs')):
        d = json.loads(stage(n, path))
        ks = list(d.keys())
        info = {k: (len(d[k]) if isinstance(d[k], list) else 'dict') for k in ks}
        print(tag, path, info)

ca_o = json.loads(stage(2, 'results/compute_audit.json'))
ca_t = json.loads(stage(3, 'results/compute_audit.json'))
hist_o = ca_o.get('history', [])
hist_t = ca_t.get('history', [])
ko = {(e.get('ts'), e.get('machine')): e for e in hist_o}
kt = {(e.get('ts'), e.get('machine')): e for e in hist_t}
print('audit history: ours', len(ko), 'theirs', len(kt),
      'only_ours', len(set(ko) - set(kt)), 'only_theirs', len(set(kt) - set(ko)))
diff = [k for k in set(ko) & set(kt) if ko[k] != kt[k]]
print('audit same-key content-diff:', len(diff), diff[:3])
print('audit latest ours:', json.dumps(ca_o.get('latest', {}), ensure_ascii=False)[:200])
print('audit latest theirs:', json.dumps(ca_t.get('latest', {}), ensure_ascii=False)[:200])

rs_o = json.loads(stage(2, 'results/regime_state.json'))
rs_t = json.loads(stage(3, 'results/regime_state.json'))
print('regime ours keys:', {k: (len(v) if isinstance(v, list) else v) for k, v in rs_o.items() if not isinstance(v, dict)})
print('regime theirs keys:', {k: (len(v) if isinstance(v, list) else v) for k, v in rs_t.items() if not isinstance(v, dict)})
for k in rs_o:
    if isinstance(rs_o[k], list) and rs_o[k] and isinstance(rs_o[k][0], dict):
        print('regime list', k, 'ours', len(rs_o[k]), 'theirs', len(rs_t.get(k, [])),
              'entry keys:', sorted(rs_o[k][0].keys())[:8])

for n, tag in ((2, 'ours'), (3, 'theirs')):
    txt = stage(n, 'results/x2_watch_log.jsonl').decode('utf-8')
    lines = [l for l in txt.splitlines() if l.strip()]
    print(tag, 'x2 lines:', len(lines), 'tail:', lines[-1][:120] if lines else '')

for path in ('CODELY.md', 'HQ-FEEDBACK.md'):
    b, o, t = stage(1, path), stage(2, path), stage(3, path)
    print(path, 'bytes base/ours/theirs:', len(b), len(o), len(t))
    print('  ours==base+suffix:', o.startswith(b), 'suffix_len:', len(o) - len(b))
    print('  theirs==base+suffix:', t.startswith(b), 'suffix_len:', len(t) - len(b))
    print('  ours suffix:', repr(o[len(b):][:200]))
    print('  theirs suffix:', repr(t[len(b):][:200]))

a_o, a_t = stage(2, 'results/autofill_state.json'), stage(3, 'results/autofill_state.json')
print('autofill ours==theirs:', a_o == a_t, 'lens:', len(a_o), len(a_t))
