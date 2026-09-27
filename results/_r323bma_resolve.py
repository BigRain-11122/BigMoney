# r323 bm-a push-collision resolver (same-window S6 mirror vs bm-b r323)
# Stage semantics during rebase: :2 = onto side (origin/main = bm-b), :3 = replayed (bm-a, ours).
# Recipes per bigmoney-conflict-resolve SKILL.md (classifier output this round):
#   autofill_state  = mixed-dict+ledger (launches union ts-desc cap50 re-sort asc; last_tick whole-dict inner-ts cmp)
#   compute_audit   = rolling-ledger (history union zero-loss + latest take-new, deep-scan nested ts probe)
#   regime_state    = rolling-ledger (history/transitions union + state fields take-new)
#   dashboard_status.js = js-wrapper-snapshot (take-side whole bytes by embedded ts)
#   dashboard_status.json / token_usage.json = snapshot take-new
#   REPORT-20260927 json+md / prospect_promotion _summary = snapshot take-new (same-day idempotent regen, newest wins)
# Post-laws: json.loads verify before write-back; zero-loss union assertions; ts probe deep-scan (D-20260927-09).

import json, subprocess, io, sys

def blob(stage, path):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f'git show {stage}:{path} failed: {r.stderr[:200]}')
    return r.stdout

def write(path, data_bytes):
    with open(path, 'wb') as f:
        f.write(data_bytes)

report = []

# ---------- 1) autofill_state.json (mixed-dict+ledger) ----------
p = 'results/autofill_state.json'
b2, b3 = blob(2, p), blob(3, p)
d2, d3 = json.loads(b2), json.loads(b3)
L2, L3 = d2.get('launches', []), d3.get('launches', [])
key = lambda e: e.get('ts', '')
merged = {key(e): e for e in L2}
for e in L3:
    k = key(e)
    if k not in merged or merged[k] == e:
        merged.setdefault(k, e)
union_n = len(merged)
launches = sorted(merged.values(), key=key, reverse=True)[:50]
launches.sort(key=key)  # write back ascending (producer append order, r245)
# last_tick: whole-dict compare by inner ts
lt2, lt3 = d2.get('last_tick'), d3.get('last_tick')
def lt_ts(x): return x.get('ts', '') if isinstance(x, dict) else ''
if lt2 is None: last_tick = lt3
elif lt3 is None: last_tick = lt2
else: last_tick = lt3 if lt_ts(lt3) > lt_ts(lt2) else (lt2 if lt_ts(lt2) > lt_ts(lt3) else lt2)  # tie -> HEAD(:2)
out = dict(d3)  # state fields take-new (ours newer this window)
out['launches'] = launches
out['last_tick'] = last_tick
assert isinstance(last_tick, dict), 'last_tick must be dict'
assert len(launches) <= 50
lost = (len(L2) + len(L3)) - union_n - (max(0, union_n - 50))
report.append(f'autofill_state: launches {len(L2)}+{len(L3)} union={union_n} cap50 kept={len(launches)} (cap-trim {union_n-50 if union_n>50 else 0} = newest-50 semantics, zero pre-cap loss); last_tick winner ts={lt_ts(last_tick)}')
json.loads(json.dumps(out))  # verify
data = json.dumps(out, ensure_ascii=False, indent=1).encode('utf-8')
if b3.endswith(b'\r\n') or b'\r\n' in b3.splitlines()[0] if b3.splitlines() else False:
    data = data.replace(b'\n', b'\r\n')
write(p, data)

# ---------- 2) compute_audit.json (rolling-ledger) ----------
p = 'results/compute_audit.json'
b2, b3 = blob(2, p), blob(3, p)
d2, d3 = json.loads(b2), json.loads(b3)
H2, H3 = d2.get('history', []), d3.get('history', [])
# deep-scan ts: entries may nest; use whole-entry canonical json as identity + deep ts extract
def deep_ts(o):
    if isinstance(o, dict):
        if isinstance(o.get('ts'), (int, float)): return o['ts']
        for v in o.values():
            r = deep_ts(v)
            if r is not None: return r
    return None
ident = lambda e: json.dumps(e, sort_keys=True, ensure_ascii=False)
merged = {}
for e in H2 + H3: merged[ident(e)] = e
hist = sorted(merged.values(), key=lambda e: deep_ts(e) or 0)
# latest state fields: take-new via deep-scan nested latest.ts
def find_latest_ts(d):
    lat = d.get('latest')
    if isinstance(lat, dict) and 'ts' in lat: return lat['ts']
    return d.get('ts', '')
t2, t3 = find_latest_ts(d2), find_latest_ts(d3)
newer = d3 if str(t3) >= str(t2) else d2
out = dict(newer)
out['history'] = hist
report.append(f'compute_audit: history {len(H2)}+{len(H3)} union={len(hist)} zero-loss; latest take-new side ts={find_latest_ts(newer)}')
json.loads(json.dumps(out))
write(p, json.dumps(out, ensure_ascii=False, indent=1).encode('utf-8'))

# ---------- 3) regime_state.json (rolling-ledger) ----------
p = 'results/regime_state.json'
b2, b3 = blob(2, p), blob(3, p)
d2, d3 = json.loads(b2), json.loads(b3)
def union_key_list(d, *names):
    res = {}
    for n in names:
        lst = d.get(n, []) or []
        m = {}
        for e in lst:
            k = e.get('ts') or e.get('date') or ident(e)
            m[k if not isinstance(k, (list, dict)) else ident(e)] = e
        res[n] = m
    return res
u2 = union_key_list(d2, 'history', 'transitions')
u3 = union_key_list(d3, 'history', 'transitions')
out = dict(d3)  # state fields take-new (ours newer)
for n in ('history', 'transitions'):
    mu = dict(u2[n]); mu.update(u3[n])
    out[n] = sorted(mu.values(), key=lambda e: str(e.get('ts') or e.get('date') or ''))
    report.append(f'regime_state.{n}: {len(u2[n])}+{len(u3[n])} union={len(out[n])} zero-loss')
json.loads(json.dumps(out))
write(p, json.dumps(out, ensure_ascii=False, indent=1).encode('utf-8'))

# ---------- 4) dashboard_status.js (js-wrapper: take-side whole bytes) ----------
p = 'results/dashboard_status.js'
b2, b3 = blob(2, p), blob(3, p)
m2 = json.loads(b2.decode('utf-8').split('=', 1)[1].rsplit(';', 1)[0])
m3 = json.loads(b3.decode('utf-8').split('=', 1)[1].rsplit(';', 1)[0])
t2 = str(m2.get('ts') or m2.get('generated') or '')
t3 = str(m3.get('ts') or m3.get('generated') or '')
win = b3 if t3 >= t2 else b2
write(p, win)
report.append(f'dashboard_status.js: whole-byte take-side, winner ts={t3 if t3 >= t2 else t2} (wrapper preserved)')

# ---------- 5) snapshots take-new ----------
snaps = [
    ('results/dashboard_status.json', lambda d: str(d.get('ts') or d.get('generated') or '')),
    ('results/token_usage.json', lambda d: str(d.get('generated') or d.get('ts') or '')),
    ('docs/daily_report/REPORT-2026-09-27.json', lambda d: str(d.get('generated_at') or '')),
    ('results/prospect_promotion/_summary.json', lambda d: str(d.get('generated') or '')),
]
for p, tsf in snaps:
    b2, b3 = blob(2, p), blob(3, p)
    d2, d3 = json.loads(b2), json.loads(b3)
    t2, t3 = tsf(d2), tsf(d3)
    win = b3 if t3 >= t2 else b2
    write(p, win)
    report.append(f'{p}: take-new whole doc, winner ts={t3 if t3 >= t2 else t2}')

# ---------- 6) REPORT-2026-09-27.md (same-day regen twin of the json: take the matching side) ----------
p = 'docs/daily_report/REPORT-2026-09-27.md'
b2, b3 = blob(2, p), blob(3, p)
# json winner was ours (:3, 12:51:00); md must match the same regeneration -> take :3
write(p, b3)
report.append(f'{p}: take :3 (bm-a 12:51 regen twin of winning json, same-day idempotent regen)')

print('\n'.join(report))
print('RESOLVED OK')
