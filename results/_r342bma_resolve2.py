# -*- coding: utf-8 -*-
# r342 bm-a resolver PASS-2: rebase stop vs bm-c r94 chain (13-UU same-window dual-machine S6 faces)
# 12 snapshot/twin/js faces: take-NEW (theirs=mine, all 18:12-18:14 > ours 18:09-18:10) byte-verbatim
# compute_audit: rolling-ledger union (r188/R208) mirror base CRLF indent2 face (r223/r234)
# regime_state: verify histories identical -> take- theirs whole; else union
import subprocess, json, sys

def blob(st, p):
    r = subprocess.run(['git', 'show', st + ':' + p], capture_output=True)
    assert r.returncode == 0, (st, p)
    return r.stdout

def log(s): print(s, flush=True)

# ---- A) byte-verbatim take-theirs faces (all newer by deep ts probe) ----
TAKE_THEIRS = [
    'docs/daily_report/REPORT-2026-09-27.json',   # generated 18:14:07 > 18:10:36 (twin json face)
    'docs/daily_report/REPORT-2026-09-27.md',      # twin-side coupling r329: md from SAME side blob
    'results/dashboard_status.js',                # js-wrapper R209: whole bytes, no re-emit
    'results/dashboard_status.json',              # meta.generated_at 18:14:09 > 18:10:38
    'results/fundamental_b_layer_filter.json',    # updated 18:14:07 > 18:10:24
    'results/futures_update_status.json',          # ts 18:13:41 > 18:10:20
    'results/heat_update_status.json',             # updated 18:13:41 > 18:10:19
    'results/lhb_update_status.json',              # updated 18:13:41 > 18:10:19 (326B mine newer face)
    'results/scorecard_v1.json',                   # generated 18:12:47 > 18:10:03
    'results/strategy_scorecard.json',            # generated 18:12:53 > 18:10:12
    'results/token_usage.json',                    # generated 18:14:10 > 18:10:38
    'results/update_status.json',                  # updated 18:12:33 > 18:09:59
]
for p in TAKE_THEIRS:
    b3 = blob(':3', p)
    b2 = blob(':2', p)
    assert b3 and b3 != b2, p
    if p.endswith('.json'):
        json.loads(b3.decode('utf-8'))  # parse-verify before write (r185)
    if p.endswith('.js'):
        t = b3.decode('utf-8')
        assert t.lstrip().startswith('window.DASH_DATA') and t.rstrip().endswith(';'), 'js wrapper face'
        json.loads(t[t.index('{'):t.rindex('}') + 1])
    open(p, 'wb').write(b3)
    log(f'take-theirs: {p} ({len(b3)}B)')

# ---- B) compute_audit.json rolling-ledger union ----
CAP = 'results/compute_audit.json'
b1, b2, b3 = blob(':1', CAP), blob(':2', CAP), blob(':3', CAP)
B, O, T = json.loads(b1), json.loads(b2), json.loads(b3)
assert b1.count(b'\r\n') > 0, 'base face must be CRLF (mirror source)'
oh, th = O['history'], T['history']
okeys = {e['ts']: e for e in oh}; tkeys = {e['ts']: e for e in th}
shared = set(okeys) & set(tkeys)
for k in shared:
    assert json.dumps(okeys[k], sort_keys=True) == json.dumps(tkeys[k], sort_keys=True), 'shared row divergence ' + k
u = {}
for e in oh: u[e['ts']] = e
for e in th:
    if e['ts'] in u and e['ts'] not in shared:
        assert json.dumps(u[e['ts']], sort_keys=True) == json.dumps(e, sort_keys=True), 'dup-ts divergence'
    u.setdefault(e['ts'], e)
expect = len(set(okeys) | set(tkeys))
assert len(u) == expect, (len(u), expect)
hist = sorted(u.values(), key=lambda e: e['ts'])
# latest take-new by deep ts probe (mine 18:12:25 > bmc 18:09:52); tie->HEAD r140
assert T['latest']['ts'] >= O['latest']['ts'], 'expected theirs latest newer'
merged = {'latest': T['latest'], 'history': hist}
out = json.dumps(merged, indent=2, ensure_ascii=False).encode('utf-8').replace(b'\n', b'\r\n')
json.loads(out.decode('utf-8'))
open(CAP, 'wb').write(out)
log(f'compute_audit union: |ours|={len(okeys)} |theirs|={len(tkeys)} shared={len(shared)} -> rows={len(hist)} '
    f'(== |A u B|={expect}); latest take-new ts={T["latest"]["ts"]}; face=CRLF/indent2 mirror base')

# ---- C) regime_state.json: identical-histories check then take-theirs ----
REG = 'results/regime_state.json'
r2, r3 = blob(':2', REG), blob(':3', REG)
J2, J3 = json.loads(r2), json.loads(r3)
h2 = json.dumps(J2.get('history', []), sort_keys=True); h3 = json.dumps(J3.get('history', []), sort_keys=True)
t2 = json.dumps(J2.get('transitions', []), sort_keys=True); t3 = json.dumps(J3.get('transitions', []), sort_keys=True)
if h2 == h3 and t2 == t3:
    assert J3.get('updated', '') >= J2.get('updated', ''), 'regime updated not newer'
    open(REG, 'wb').write(r3)
    log(f'regime_state: histories/transitions identical ({len(J3.get("history", []))} rows) -> take-theirs whole '
        f'(updated {J3.get("updated")})')
else:
    # union ledgers by face-real key (asof per r334) then take-new state fields
    def union(A, Bk, key):
        m = {}
        for e in A: m[e.get(key)] = e
        for e in Bk: m.setdefault(e.get(key), e)
        return sorted(m.values(), key=lambda e: e.get(key, ''))
    Jm = dict(J3)
    Jm['history'] = union(J2.get('history', []), J3.get('history', []), 'asof')
    Jm['transitions'] = union(J2.get('transitions', []), J3.get('transitions', []), 'asof')
    face = r3 if r3.count(b'\r\n') > 0 else r2
    eol = b'\r\n' if face.count(b'\r\n') > 0 else b'\n'
    out = json.dumps(Jm, indent=2, ensure_ascii=False).encode('utf-8').replace(b'\n', b'\r\n' if eol == b'\r\n' else b'\n')
    json.loads(out.decode('utf-8'))
    open(REG, 'wb').write(out)
    log(f'regime_state: UNION path histories |A|={len(J2.get("history", []))} |B|={len(J3.get("history", []))} '
        f'-> {len(Jm["history"])}; transitions -> {len(Jm["transitions"])}')

# ---- D) stage all + verify ----
import os
allp = TAKE_THEIRS + [CAP, REG]
for p in allp:
    r = subprocess.run(['git', '-c', 'core.autocrlf=false', 'add', p], capture_output=True)
    assert r.returncode == 0, (p, r.stderr)
# staged verification: no markers anywhere, json parse, face checks
for p in allp:
    sb = subprocess.run(['git', 'show', ':' + p], capture_output=True).stdout
    txt = sb.decode('utf-8', errors='replace')
    assert not any(l.startswith('<<<<<<<') or l.startswith('>>>>>>>') or l == '=======' for l in txt.split('\n')), 'marker in staged ' + p
    if p.endswith('.json'):
        json.loads(sb.decode('utf-8'))
log('staged marker-scan: 14 files clean')
uu = subprocess.run(['git', 'diff', '--name-only', '--diff-filter=U'], capture_output=True, text=True).stdout.strip()
assert uu == '', 'still unmerged: ' + uu
sg = json.loads(subprocess.run(['git', 'show', ':' + CAP], capture_output=True).stdout.decode('utf-8'))
assert len(sg['history']) == expect and subprocess.run(['git', 'show', ':' + CAP], capture_output=True).stdout.count(b'\r\n') > 0
log(f'FINAL: compute_audit staged rows={len(sg["history"])} CRLF ok; all 14 staged clean')
print('RESOLVER-2 PASS')
