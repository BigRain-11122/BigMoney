"""r382 bm-b rebase-storm resolver (14-UU vs bm-c round 162 landed 00e2e073).
Recipes per classify_conflicts.py + hand-classified UNKNOWNs (REPORT twin=r373 snapshot-take-new,
scorecard family=L1 deterministic derive take-new) + r159 law (ts decides, not :2:/:3: labels).
"""
import subprocess, json, sys

def stage(n, path):
    return subprocess.run(['git', 'show', ':%d:%s' % (n, path)], capture_output=True).stdout

def write(path, data):
    if isinstance(data, str):
        data = data.encode('utf-8')
    open(path, 'wb').write(data)

report = []

# ---------- 1. CODELY.md : memory-union with bm-c batch-48 archival semantics ----------
p = 'CODELY.md'
s2 = stage(2, p).decode('utf-8')
s3 = stage(3, p).decode('utf-8')
lines2 = s2.split('\n')
lines3 = s3.split('\n')
# my genuinely-new line(s) absent from origin side; r159/r379 were lawfully archived
# out of the live face by bm-c batch-48 -> verify verbatim presence in archive (zero-loss),
# then append ONLY my genuinely-new r382 entry (no resurrection of archived lines):
arch = open('research/memory-archive/202609.md', encoding='utf-8').read()
assert 'r159' in arch and 'r379' in arch and '四十八批' in arch, 'batch-48 archive zero-loss verify FAIL'
mine_new = [l for l in lines3 if l not in lines2 and l.strip().startswith('- [') and 'r382 bm-b' in l]
assert len(mine_new) == 1, mine_new
theirs_new = [l for l in lines2 if l not in lines3]
out = s2.rstrip('\n') + '\n' + mine_new[0] + '\n'
assert 'r162 bm-c' in out  # their side carries their r162 entry + archival pointer
size = len(out.encode('utf-8'))
assert size <= 10240, 'CODELY over 10KB: %d' % size
write(p, out)
report.append('CODELY.md: bm-c batch-48 archival base (%dB, r159/r379 verbatim-in-archive verified) + my r382 line -> %dB <=10KB OK' % (len(s2.encode('utf-8')), size))

# ---------- 2. compute_audit.json : rolling-ledger union + snapshot take-new ----------
p = 'results/compute_audit.json'
d2 = json.loads(stage(2, p).decode('utf-8'))
d3 = json.loads(stage(3, p).decode('utf-8'))
h2, h3 = d2.get('history', []), d3.get('history', [])
k2 = {r['ts']: r for r in h2}
k3 = {r['ts']: r for r in h3}
union_ts = sorted(set(k2) | set(k3))
rows = [k3[t] if t in k3 else k2[t] for t in union_ts]
assert len(rows) == len(set(k2) | set(k3)), 'union zero-loss fail'
t2 = d2.get('ts'); t3 = d3.get('ts')
base = d3 if (t3 or '') >= (t2 or '') else d2
base['history'] = rows
assert json.loads(json.dumps(base))  # parse-verify
write(p, json.dumps(base, ensure_ascii=False, indent=2))
report.append('compute_audit.json: history union %d+%d->%d zero-loss, snapshot ts %s vs %s -> %s' %
              (len(h2), len(h3), len(rows), t2, t3, 'mine' if base is d3 else 'origin'))

# ---------- 3. regime_state.json : rolling-ledger union + state take-new ----------
p = 'results/regime_state.json'
d2 = json.loads(stage(2, p).decode('utf-8'))
d3 = json.loads(stage(3, p).decode('utf-8'))
for key in ('history', 'transitions'):
    a, b = d2.get(key, []), d3.get(key, [])
    seen = {json.dumps(x, sort_keys=True, ensure_ascii=False) for x in a}
    rows = list(a) + [x for x in b if json.dumps(x, sort_keys=True, ensure_ascii=False) not in seen]
    base = d3 if d3.get('updated', '') >= d2.get('updated', '') else d2
    base[key] = rows
    report.append('regime_state.%s: union %d+%d->%d, state updated %s vs %s -> %s' %
                  (key, len(a), len(b), len(rows), d2.get('updated'), d3.get('updated'),
                   'mine' if base is d3 else 'origin'))
assert json.loads(json.dumps(base))
write(p, json.dumps(base, ensure_ascii=False, indent=2))

# ---------- 4. dashboard_status.json / .js : snapshot / js-wrapper take-side by internal ts ----------
def dash_ts(blob):
    txt = blob.decode('utf-8')
    i = txt.find('{')
    d = json.loads(txt[i:txt.rfind('}') + 1]) if txt.startswith('window.') else json.loads(txt)
    return d
for p in ('results/dashboard_status.json', 'results/dashboard_status.js'):
    s2b, s3b = stage(2, p), stage(3, p)
    j2, j3 = dash_ts(s2b), dash_ts(s3b)
    t2 = j2.get('meta', {}).get('generated') or j2.get('generated') or j2.get('ts') or ''
    t3 = j3.get('meta', {}).get('generated') or j3.get('generated') or j3.get('ts') or ''
    win = s3b if (t3 or '') >= (t2 or '') else s2b
    write(p, win)
    report.append('%s: take-%s by internal ts (%s vs %s) whole-bytes, wrapper preserved' %
                  (p, 'mine' if win is s3b else 'origin', t2, t3))

# ---------- 5. plain snapshots take-new by ts ----------
SNAPS = {
    'docs/daily_report/REPORT-2026-09-28.json': ('generated_at',),
    'docs/daily_report/REPORT-2026-09-28.md': None,
    'results/fundamental_b_layer_filter.json': ('updated',),
    'results/futures_update_status.json': ('ts',),
    'results/lhb_update_status.json': ('updated',),
    'results/scorecard_v1.json': ('generated',),
    'results/strategy_scorecard.json': ('generated',),
    'results/token_usage.json': ('generated',),
    'results/update_status.json': ('updated',),
}
for p, keys in SNAPS.items():
    s2b, s3b = stage(2, p), stage(3, p)
    if keys:  # json ts probe
        d2 = json.loads(s2b.decode('utf-8'))
        d3 = json.loads(s3b.decode('utf-8'))
        def g(d):
            for k in keys:
                v = d.get(k)
                if v: return v
            return ''
        t2, t3 = g(d2), g(d3)
        win = s3b if t3 >= t2 else s2b
        write(p, win)
        report.append('%s: take-%s by %s (%s vs %s)' % (p, 'mine' if win is s3b else 'origin', keys[0], t2, t3))
    else:  # md twin: probe twin json ts (same generated_at family)
        j2 = json.loads(stage(2, 'docs/daily_report/REPORT-2026-09-28.json').decode('utf-8'))
        j3 = json.loads(stage(3, 'docs/daily_report/REPORT-2026-09-28.json').decode('utf-8'))
        win = s3b if j3['generated_at'] >= j2['generated_at'] else s2b
        write(p, win)
        report.append('%s: take-%s riding twin json generated_at (%s vs %s)' %
                      (p, 'mine' if win is s3b else 'origin', j2['generated_at'], j3['generated_at']))

print('\n'.join(report))
# final parse-verify sweep of every resolved json
for p in ('results/compute_audit.json', 'results/regime_state.json', 'results/dashboard_status.json',
          'docs/daily_report/REPORT-2026-09-28.json', 'results/fundamental_b_layer_filter.json',
          'results/futures_update_status.json', 'results/lhb_update_status.json',
          'results/scorecard_v1.json', 'results/strategy_scorecard.json',
          'results/token_usage.json', 'results/update_status.json'):
    json.load(open(p, encoding='utf-8'))
print('ALL RESOLVED + parse-verified')
