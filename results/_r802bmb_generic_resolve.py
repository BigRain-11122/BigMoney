# r802 bm-b GENERIC rebase-conflict resolver (S6 twins per-face ts-empirical, runtime duel)
# Recurring same-minute push-race face (3rd today): my r801 S6 run vs concurrent machine's S6 run.
# Canon: regen/snapshot faces duel on internal ts key (updated/ts/generated/generated_at, first hit wins);
# md twins follow their json pair side; compute_audit = history union + latest duel; token_usage = per-key max.
# Reusable: no hardcoded sides. Receipt -> results/_r802bmb_generic_resolve.json
import subprocess, json, sys, io

TS_KEYS = ['updated', 'ts', 'generated', 'generated_at', 'last_attempt']

def stages_of(path):
    out = subprocess.run(['git','ls-files','-u','--',path],capture_output=True,text=True).stdout
    res = {}
    for line in out.strip().split('\n'):
        if not line.strip():
            continue
        meta, _, fp = line.partition('\t')
        parts = meta.split()
        if len(parts) >= 3:
            res[parts[2]] = parts[1]
    return res

def blob(sha):
    return subprocess.run(['git','cat-file','-p',sha],capture_output=True).stdout

def duel_ts(j):
    for k in TS_KEYS:
        if isinstance(j, dict) and k in j and isinstance(j[k], str):
            return j[k]
    return None

receipt = {'round': 'r802', 'machine': 'bm-b', 'event': 'generic S6-twin rebase resolve (vs bm-c r673 line)', 'faces': {}}

def take_side(path, st, side):
    sha = st['2'] if side == 2 else st['3']
    data = blob(sha)
    if b'<<<<<<<' in data:
        print('MARKER-LEAK ABORT', path); sys.exit(2)
    with open(path, 'wb') as f:
        f.write(data)
    receipt['faces'][path] = {'recipe': 'ts-duel', 'winner': 'ours(st2)' if side == 2 else 'theirs(st3)'}
    print('take %-50s <- %s' % (path, 'ours' if side == 2 else 'theirs'))

# ---- 1. pure ts-duel json snapshots ----
DUEL = ['results/regime_state.json','results/update_status.json','results/fundamental_b_layer_filter.json',
        'results/_attrition_guard_scan.json','results/futures_update_status.json','results/lhb_update_status.json']
for p in DUEL:
    st = stages_of(p)
    if not st:
        continue
    j2 = json.loads(blob(st['2']))
    j3 = json.loads(blob(st['3']))
    t2, t3 = duel_ts(j2), duel_ts(j3)
    side = 3 if (t3 or '') >= (t2 or '') else 2
    receipt['faces'][p] = {'recipe': 'ts-duel', 'st2_ts': t2, 'st3_ts': t3}
    take_side(p, st, side)
    print('  duel %s: st2=%s st3=%s' % (p.split('/')[-1], t2, t3))

# ---- 2. regen twins: json duels, md follows json ----
TWINS = [('docs/daily_report/REPORT-2026-10-07.json', 'docs/daily_report/REPORT-2026-10-07.md'),
         ('docs/live_usage/LIVE-2026-10-07.json', 'docs/live_usage/LIVE-2026-10-07.md'),
         ('docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md')]
for jp, mp in TWINS:
    st = stages_of(jp)
    if not st:
        continue
    j2 = json.loads(blob(st['2']))
    j3 = json.loads(blob(st['3']))
    t2, t3 = duel_ts(j2), duel_ts(j3)
    side = 3 if (t3 or '') >= (t2 or '') else 2
    receipt['faces'][jp] = {'recipe': 'regen-twin ts-duel', 'st2_ts': t2, 'st3_ts': t3}
    take_side(jp, st, side)
    print('  duel %s: st2=%s st3=%s' % (jp.split('/')[-1], t2, t3))
    stm = stages_of(mp)
    if stm:
        take_side(mp, stm, side)

# ---- 3. compute_audit: history union + latest duel ----
p = 'results/compute_audit.json'
st = stages_of(p)
if st:
    j2 = json.loads(blob(st['2']))
    j3 = json.loads(blob(st['3']))
    h2 = j2.get('history', []); h3 = j3.get('history', [])
    union = {}
    for e in h2 + h3:
        union[e['ts']] = e
    merged = [union[k] for k in sorted(union.keys())]
    latest = j3['latest'] if j3['latest']['ts'] >= j2['latest']['ts'] else j2['latest']
    n_exp = len(set(e['ts'] for e in h2) | set(e['ts'] for e in h3))
    assert len(merged) == n_exp, 'union count mismatch'
    receipt['faces'][p] = {'recipe': 'rolling union+duel', 'hist_st2': len(h2), 'hist_st3': len(h3), 'union': len(merged),
                          'latest': latest['ts']}
    raw = blob(st['2'])
    crlf = b'\r\n' in raw
    txt = json.dumps({'latest': latest, 'history': merged}, indent=1, ensure_ascii=False)
    if crlf:
        txt = txt.replace('\n', '\r\n')
    with open(p, 'wb') as f:
        f.write(txt.encode('utf-8'))
    json.loads(open(p, 'rb').read().decode('utf-8'))
    print('union compute_audit: %d+%d->%d latest=%s' % (len(h2), len(h3), len(merged), latest['ts']))

# ---- 4. token_usage: per-key max ----
p = 'results/token_usage.json'
st = stages_of(p)
if st:
    j2 = json.loads(blob(st['2']))
    j3 = json.loads(blob(st['3']))
    def max_merge(a, b):
        if isinstance(a, dict) and isinstance(b, dict):
            out = {}
            for k in set(a) | set(b):
                out[k] = max_merge(a[k], b[k]) if (k in a and k in b) else a.get(k, b.get(k))
            return out
        if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool) and not isinstance(b, bool):
            return max(a, b)
        return a
    newer = j3 if (j3.get('generated','') >= j2.get('generated','')) else j2
    merged = max_merge(j2, j3)
    for k, v in newer.items():
        if not isinstance(v, (int, float)) or isinstance(v, bool):
            merged[k] = v
    receipt['faces'][p] = {'recipe': 'per-key max', 'generated': merged.get('generated')}
    raw = blob(st['2'])
    crlf = b'\r\n' in raw
    txt = json.dumps(merged, indent=1, ensure_ascii=False)
    if crlf:
        txt = txt.replace('\n', '\r\n')
    with open(p, 'wb') as f:
        f.write(txt.encode('utf-8'))
    json.loads(open(p, 'rb').read().decode('utf-8'))
    print('token max-union: generated=%s' % merged.get('generated'))

# ---- stage everything resolved ----
all_files = list(receipt['faces'].keys())
r = subprocess.run(['git','add','--'] + all_files, capture_output=True, text=True)
if r.returncode != 0:
    print('GIT ADD FAIL:', r.stderr); sys.exit(3)
with open('results/_r802bmb_generic_resolve.json','w',encoding='utf-8') as f:
    json.dump(receipt, f, indent=1, ensure_ascii=False)
subprocess.run(['git','add','results/_r802bmb_generic_resolve.json'], capture_output=True)
print('generic resolver done: %d faces, receipt staged' % len(all_files))
