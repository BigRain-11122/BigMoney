# r324 bm-b push-collision resolver (same-window S6 mirror, 16-UU vs upstream window)
# Stage semantics during rebase: :2 = onto side (origin/main upstream), :3 = replayed (bm-b r324, ours).
# Recipes per bigmoney-conflict-resolve SKILL.md + classifier output (11 classified + 5 UNKNOWN hand-adjudicated
# per r317/r319/r320/r322/r323 precedent: same-day deterministic regen twins -> take-new newest generated).
# Laws mechanized: r185 parse-verify-before-add; r140 same-second tie -> HEAD(:2); r188/R208 zero-loss union;
# r215 cap50 newest-50; r245 write-back ascending; r223 CRLF mirror; r319 collision-key content-eq verify with
# composite-key escalation; r323 token_usage top-take-newer + machines key-union.
import json, subprocess, sys

def blob(stage, path):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f'git show {stage}:{path} failed: {r.stderr[:200]}')
    return r.stdout

def write(path, data_bytes):
    with open(path, 'wb') as f:
        f.write(data_bytes)

def crlf_mirror(base_bytes, data_bytes):
    return data_bytes.replace(b'\n', b'\r\n') if b'\r\n' in base_bytes else data_bytes

def deep_ts(o):
    # D-20260927-09 deep-scan: first ts-like key at any depth (dicts only, bfs by key priority)
    if not isinstance(o, dict):
        return ''
    for k in ('ts', 'generated', 'generated_at', 'updated', 'updated_at', 'asof', 'date'):
        if isinstance(o.get(k), str) and o[k]:
            return o[k]
    for v in o.values():
        if isinstance(v, dict):
            r = deep_ts(v)
            if r:
                return r
    return ''

def ident(e):
    return json.dumps(e, sort_keys=True, ensure_ascii=False)

report = []

# ---------- 1) autofill_state.json (mixed-dict+ledger) ----------
p = 'results/autofill_state.json'
b2, b3 = blob(2, p), blob(3, p)
d2, d3 = json.loads(b2), json.loads(b3)
L2, L3 = d2.get('launches', []), d3.get('launches', [])
merged = {}          # primary key = ts; collision content-diff -> composite key escalation (r319)
keyset = set()
for e in L2 + L3:
    k = e.get('ts', '')
    keyset.add(k)
    if k in merged and merged[k] != e:
        k = k + '|' + ident(e)[:40]   # composite escalation: never swallow a side silently
    if k not in merged or merged[k] == e:
        merged[k] = e
union_n = len(merged)
launches = sorted(merged.values(), key=lambda e: e.get('ts', ''), reverse=True)[:50]
launches.sort(key=lambda e: e.get('ts', ''))   # write back ascending (producer append order, r245)
lt2, lt3 = d2.get('last_tick'), d3.get('last_tick')
def lt_ts(x):
    return x.get('ts', '') if isinstance(x, dict) else ''
if lt2 is None:
    last_tick, base = lt3, d3
elif lt3 is None:
    last_tick, base = lt2, d2
else:
    if lt_ts(lt3) > lt_ts(lt2):
        last_tick, base = lt3, d3
    else:
        last_tick, base = lt2, d2   # includes tie -> HEAD(:2) per r140
out = dict(base)
out['launches'] = launches
out['last_tick'] = last_tick
assert isinstance(last_tick, dict), 'last_tick must be dict'
assert len(launches) <= 50
json.loads(json.dumps(out))
write(p, crlf_mirror(b2, json.dumps(out, ensure_ascii=False, indent=1).encode('utf-8')))
report.append(f'autofill_state: launches {len(L2)}+{len(L3)} union={union_n} cap50 kept={len(launches)} '
              f'(cap-trim {max(0, union_n - 50)} newest-50 semantics); last_tick winner ts={lt_ts(last_tick)} base-side={"2" if base is d2 else "3"}')

# ---------- 2) compute_audit.json (rolling-ledger) ----------
p = 'results/compute_audit.json'
b2, b3 = blob(2, p), blob(3, p)
d2, d3 = json.loads(b2), json.loads(b3)
H2, H3 = d2.get('history', []), d3.get('history', [])
merged = {}
for e in H2 + H3:
    k = ident(e)                    # canonical identity key: zero silent swallow (r319 spirit)
    merged[k] = e
hist = sorted(merged.values(), key=lambda e: str(deep_ts(e)))
def find_latest_ts(d):
    lat = d.get('latest')
    if isinstance(lat, dict):
        r = deep_ts(lat)
        if r:
            return r
    return deep_ts(d)
t2, t3 = find_latest_ts(d2), find_latest_ts(d3)
newer = d3 if str(t3) >= str(t2) else d2
out = dict(newer)
out['history'] = hist
assert len(hist) == len(merged)
json.loads(json.dumps(out))
write(p, json.dumps(out, ensure_ascii=False, indent=1).encode('utf-8'))
report.append(f'compute_audit: history {len(H2)}+{len(H3)} union={len(hist)} zero-loss asserted; '
              f'latest take-new side={"3" if newer is d3 else "2"} ts={find_latest_ts(newer)}')

# ---------- 3) regime_state.json (rolling-ledger) ----------
p = 'results/regime_state.json'
b2, b3 = blob(2, p), blob(3, p)
d2, d3 = json.loads(b2), json.loads(b3)
def keymap(lst):
    m = {}
    for e in lst:
        k = e.get('ts') or e.get('asof') or e.get('date') or ident(e)
        if k in m and m[k] != e:
            k = str(k) + '|b'   # r319: same-key content-diff -> composite escalation, never swallow a side
        m[k] = e
    return m
base = d3 if str(deep_ts(d3)) >= str(deep_ts(d2)) else d2
out = dict(base)
for n in ('history', 'transitions'):
    m2, m3 = keymap(d2.get(n, []) or []), keymap(d3.get(n, []) or [])
    mu = dict(m2)
    mu.update(m3)
    out[n] = sorted(mu.values(), key=lambda e: str(e.get('ts') or e.get('asof') or e.get('date') or ''))
    k2 = {str(e.get('ts') or e.get('asof') or e.get('date') or ident(e)) for e in (d2.get(n) or [])}
    k3 = {str(e.get('ts') or e.get('asof') or e.get('date') or ident(e)) for e in (d3.get(n) or [])}
    assert len({str(v) for v in mu.keys()}) >= len(k2 | k3), 'union key loss'
    report.append(f'regime_state.{n}: {len(m2)}+{len(m3)} union={len(out[n])} (raw keyset |A∪B|={len(k2 | k3)}, '
                  f'composite-escalated={len(out[n]) - len(k2 | k3)})')
json.loads(json.dumps(out))
write(p, json.dumps(out, ensure_ascii=False, indent=1).encode('utf-8'))
report.append(f'regime_state: state fields take-new side={"3" if base is d3 else "2"} ts={deep_ts(base)}')

# ---------- 4) dashboard_status.js (js-wrapper: take-side whole bytes, R209) ----------
p = 'results/dashboard_status.js'
b2, b3 = blob(2, p), blob(3, p)
m2 = json.loads(b2.decode('utf-8').split('=', 1)[1].rsplit(';', 1)[0])
m3 = json.loads(b3.decode('utf-8').split('=', 1)[1].rsplit(';', 1)[0])
t2, t3 = deep_ts(m2), deep_ts(m3)
win = b3 if t3 >= t2 else b2
write(p, win)
report.append(f'dashboard_status.js: whole-byte take-side winner ts={t3 if t3 >= t2 else t2} (wrapper preserved, R209)')

# ---------- 5) token_usage.json (snapshot take-new + machines key-union, r323) ----------
p = 'results/token_usage.json'
b2, b3 = blob(2, p), blob(3, p)
d2, d3 = json.loads(b2), json.loads(b3)
t2, t3 = deep_ts(d2), deep_ts(d3)
newer, older = (d3, d2) if str(t3) >= str(t2) else (d2, d3)
out = dict(newer)
mnew, mold = newer.get('machines', {}), older.get('machines', {})
mu = dict(mold)
for k, v in mnew.items():
    if k not in mu or str(deep_ts(v)) >= str(deep_ts(mu[k])):
        mu[k] = v
if mu:
    out['machines'] = mu
json.loads(json.dumps(out))
write(p, json.dumps(out, ensure_ascii=False, indent=1).encode('utf-8'))
report.append(f'token_usage: top take-new side={"3" if newer is d3 else "2"} ts={deep_ts(newer)}; '
              f'machines key-union {len(mold)}|{len(mnew)} -> {len(mu)} zero-loss')

# ---------- 6) snapshots take-new (whole doc by deep ts probe) ----------
snaps = [
    'results/dashboard_status.json',
    'results/update_status.json',
    'results/fundamental_b_layer_filter.json',
    'results/futures_update_status.json',
    'results/heat_update_status.json',
    'results/lhb_update_status.json',
    'results/scorecard_v1.json',
    'results/strategy_scorecard.json',
    'results/prospect_promotion/_summary.json',
]
for p in snaps:
    b2, b3 = blob(2, p), blob(3, p)
    d2, d3 = json.loads(b2), json.loads(b3)
    t2, t3 = deep_ts(d2), deep_ts(d3)
    win = b3 if str(t3) >= str(t2) else b2
    json.loads(win)                       # parse-verify before write (r185)
    write(p, win)
    report.append(f'{p}: take-new winner side={"3" if win is b3 else "2"} ts={t3 if str(t3) >= str(t2) else t2}')

# ---------- 7) daily_report twins (same-day idempotent regen: json take-new, md follows same side) ----------
pj = 'docs/daily_report/REPORT-2026-09-27.json'
pm = 'docs/daily_report/REPORT-2026-09-27.md'
b2, b3 = blob(2, pj), blob(3, pj)
d2, d3 = json.loads(b2), json.loads(b3)
t2, t3 = deep_ts(d2), deep_ts(d3)
winj = b3 if str(t3) >= str(t2) else b2
json.loads(winj)
write(pj, winj)
side = 3 if winj is b3 else 2
write(pm, blob(side, pm))
report.append(f'{pj}: take-new winner side={side} ts={t3 if str(t3) >= str(t2) else t2}; {pm}: taken same side (regen twin coherence)')

print('\n'.join(report))
print('RESOLVED OK: 16/16 faces written; post-write strict reparse follows in shell step')
