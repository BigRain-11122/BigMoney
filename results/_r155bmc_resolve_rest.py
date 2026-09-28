# -*- coding: utf-8 -*-
# r155 bm-c storm-rest resolver: 3 snapshot-class faces (deep-ts probe take-new; REPORT md twin follows json side)
# skill law: bigmoney-conflict-resolve snapshot/twin classes; r154 precedent (11-face take-new + twins same side)
import subprocess, json

def blob(rev, path):
    r = subprocess.run(['git', 'show', f'{rev}:{path}'], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f'stage read fail {rev} {path}: {r.stderr.decode("utf-8", "replace")[:200]}')
    return r.stdout

TS_KEYS = ('ts', 'updated', 'updated_at', 'generated', 'time', 'as_of')

def probe_ts(obj):
    cands = []
    def scan(d, depth):
        if depth > 2:
            return
        if isinstance(d, dict):
            for k, v in d.items():
                if isinstance(v, str) and k in TS_KEYS and v[:2] == '20':
                    cands.append(v)
                elif isinstance(v, dict):
                    scan(v, depth + 1)
    scan(obj, 0)
    return max(cands) if cands else None

faces = ['results/fundamental_b_layer_filter.json', 'docs/daily_report/REPORT-2026-09-28.json']
report_md = 'docs/daily_report/REPORT-2026-09-28.md'
winner = {}
for p in faces:
    a = blob(':2', p)
    b = blob(':3', p)
    ja = json.loads(a.decode('utf-8'))
    jb = json.loads(b.decode('utf-8'))
    ta, tb = probe_ts(ja), probe_ts(jb)
    if ta is None or tb is None:
        raise SystemExit(f'fail-closed: no ts probe for {p}: base={ta} replay={tb}')
    side = 3 if tb >= ta else 2
    data = b if side == 3 else a
    with open(p, 'wb') as f:
        f.write(data)
    json.loads(open(p, encoding='utf-8').read())  # parse-verify
    winner[p] = (side, ta, tb)
    print(f'[take-new] {p}: base_side ts={ta} replay_side ts={tb} -> take side {side}')

side = winner[faces[1]][0]
md = blob(f':{side}', report_md)
with open(report_md, 'wb') as f:
    f.write(md)
print(f'[take-new twin] {report_md}: follows report json side {side} (coupled-twin law)')
print('REST RESOLVED 3/3')
