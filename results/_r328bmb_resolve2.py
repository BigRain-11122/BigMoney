# -*- coding: utf-8 -*-
"""r328 bm-b resolve2 (16-UU replay onto 644594be; classifier 11 GREEN + 5 UNKNOWN manually
classified = same-day idempotent re-derivation snapshots, take-new by embedded ts).

Sides: stage1=base ef92ff78, stage2=ours=HEAD=644594be (bm-a 14:06-14:07 S6 face),
stage3=theirs=d711a941 (bmb 14:04-14:05 S6 face). bm-a side newer on every snapshot.

Recipes:
- CODELY.md            memory-union + archival-preservation: bm-a 15th-batch consolidation is canon
                       (archive file carries 十一~十五批 verbatim, verified); resolved = ours verbatim
                       + bmb r328 line appended (the only genuinely-new bmb entry); <10KB assert.
- compute_audit.json   rolling-ledger: history union zero-loss (|A u B|=207), latest take-new (ours
                       14:06:16), producer recipe json.dump(indent=2, ensure_ascii=False) CRLF.
- regime_state.json    history/transitions identical both sides; only 'updated' differs -> take ours
                       whole bytes (newest scalars, R208 take-new).
- 13 snapshot/js-wrapper files: take ours whole bytes (latest-state semantics; every file's
                       embedded ts verified ours >= theirs).
Verification: r185 parse-verify before add; zero-loss counts; byte writes with no BOM.
"""
import io
import json
import subprocess

def blob(sha):
    return subprocess.run(['git', 'cat-file', 'blob', sha], capture_output=True).stdout

out = subprocess.run(['git', 'ls-files', '-u'], capture_output=True, text=True).stdout
st = {}
for l in out.strip().splitlines():
    p = l.split()
    st.setdefault(p[3], {})[int(p[2])] = p[1]
assert len(st) == 16, sorted(st)

def w(path, data):
    with open(path, 'wb') as f:
        f.write(data)

# 1. CODELY.md
c2 = blob(st['CODELY.md'][2]).decode('utf-8').splitlines()
c3 = blob(st['CODELY.md'][3]).decode('utf-8').splitlines()
r328 = [l for l in c3 if 'r328 bm-b' in l and 'BOM' in l]
assert len(r328) == 1 and r328[0] not in set(c2)
resolved = c2 + r328
out_b = ('\n'.join(resolved) + '\n').encode('utf-8')
assert len(out_b) < 10240 and out_b.count(b'\r\n') == 0
w('CODELY.md', out_b)
chk = open('CODELY.md', 'rb').read()
assert chk == out_b and r328[0].encode('utf-8') in chk
print('CODELY.md: ours(15th-batch consolidated) + r328 line = %dB <10KB' % len(chk))

# 2. compute_audit.json
a2 = json.loads(blob(st['results/compute_audit.json'][2]).decode('utf-8'))
a3 = json.loads(blob(st['results/compute_audit.json'][3]).decode('utf-8'))
h2 = {e['ts']: e for e in a2['history']}
h3 = {e['ts']: e for e in a3['history']}
union = dict(h2)
merges = 0
for ts, e in h3.items():
    if ts in union and union[ts] != e:
        u = dict(union[ts]); u.update(e); union[ts] = u; merges += 1
    else:
        union[ts] = e
hist = sorted(union.values(), key=lambda e: e['ts'])
latest = a2['latest'] if a2['latest']['ts'] >= a3['latest']['ts'] else a3['latest']
assert len(hist) == len(set(h2) | set(h3)), (len(hist), len(set(h2) | set(h3)))
with open('results/compute_audit.json', 'w', encoding='utf-8', newline='') as f:
    json.dump({'latest': latest, 'history': hist}, f, indent=2, ensure_ascii=False)
raw = open('results/compute_audit.json', 'rb').read()
if raw.count(b'\r\n') == 0:
    raw = raw.replace(b'\n', b'\r\n')
    w('results/compute_audit.json', raw)
chk = json.loads(io.open('results/compute_audit.json', encoding='utf-8').read())
assert len(chk['history']) == len(set(h2) | set(h3)) and chk['latest']['ts'] == latest['ts']
print('compute_audit: zero-loss union %d rows (same-ts merges=%d), latest %s'
      % (len(chk['history']), merges, chk['latest']['ts']))

# 3. regime_state.json
r2 = json.loads(blob(st['results/regime_state.json'][2]).decode('utf-8'))
r3 = json.loads(blob(st['results/regime_state.json'][3]).decode('utf-8'))
assert r2['history'] == r3['history'] and r2['transitions'] == r3['transitions']
assert [k for k in set(r2) | set(r3) if r2.get(k) != r3.get(k)] == ['updated']
assert r2['updated'] > r3['updated']
w('results/regime_state.json', blob(st['results/regime_state.json'][2]))
chk = json.loads(io.open('results/regime_state.json', encoding='utf-8').read())
assert chk == r2
print("regime_state: take-ours whole bytes (updated=%s)" % chk['updated'])

# 4. snapshots: take ours whole bytes
SNAP = {
    'docs/daily_report/REPORT-2026-09-27.json': '14:06:16',
    'docs/daily_report/REPORT-2026-09-27.md': None,
    'results/dashboard_status.js': None,
    'results/dashboard_status.json': '14:06:16',
    'results/fundamental_b_layer_filter.json': '14:07:12',
    'results/futures_update_status.json': '14:06:47',
    'results/heat_update_status.json': '14:06:47',
    'results/lhb_update_status.json': '14:06:46',
    'results/prospect_promotion/_summary.json': '14:07:23',
    'results/scorecard_v1.json': '14:06:28',
    'results/strategy_scorecard.json': '14:06:34',
    'results/token_usage.json': '14:07:29',
    'results/update_status.json': '14:06:24',
}
for p, ts_probe in SNAP.items():
    b2 = blob(st[p][2])
    if p.endswith('.json'):
        json.loads(b2.decode('utf-8'))          # parse-verify ours before write (r185)
        if ts_probe:
            body = b2.decode('utf-8')
            assert ts_probe in body, p           # ours ts embedded as inspected
    w(p, b2)
    assert open(p, 'rb').read() == b2 and not b2.startswith(b'\xef\xbb\xbf')
    print('snapshot take-ours: %s (%dB)' % (p, len(b2)))

print('ALL 16 RESOLVED + PARSE-VERIFIED')
