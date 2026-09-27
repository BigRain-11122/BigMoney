# r124 bm-c rebase storm resolver (canon: r352 stage law :2:=origin :3:=mine; r370/r371 union+take-fresh recipes; r123 post-push re-verify law)
# Derived/union faces only -- zero science/governance semantic faces in conflict set (runnable_pool NOT conflicted).
import json, re, subprocess, sys

def stage(p, n):
    r = subprocess.run(['git', 'show', f':{n}:{p}'], capture_output=True)
    if r.returncode != 0:
        sys.exit(f'stage probe failed {p} :{n}: {r.stderr.decode("utf-8", "replace")[:200]}')
    return r.stdout.decode('utf-8')

TS_RE = re.compile(r'"(?:ts|generated|generated_at|updated|updated_at)"\s*:\s*"?(\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2})')

def first_ts(text):
    m = TS_RE.search(text)
    return m.group(1) if m else None

def resolve_take_fresh(p):
    a, b = stage(p, '2'), stage(p, '3')
    ta, tb = first_ts(a), first_ts(b)
    if ta and tb:
        return b if tb > ta else a, ('mine' if tb > ta else 'origin')
    return a, 'origin-fallback'

def resolve_token_usage(p):
    a, b = json.loads(stage(p, '2')), json.loads(stage(p, '3'))
    base = a if str(a.get('generated','')) >= str(b.get('generated','')) else b
    other = b if base is a else a
    ma, mb = a.get('machines', {}), b.get('machines', {})
    union = {}
    for k in set(ma) | set(mb):
        ea, eb = ma.get(k), mb.get(k)
        if ea is None: union[k] = eb; continue
        if eb is None: union[k] = ea; continue
        ta = first_ts(json.dumps(ea)); tb = first_ts(json.dumps(eb))
        union[k] = eb if (ta is None or (tb and tb > ta)) else ea
    base['machines'] = union
    for k in other:
        if k != 'machines' and k not in base:
            base[k] = other[k]
    return json.dumps(base, ensure_ascii=False, indent=1), f"machines-union {len(ma)}+{len(mb)}->{len(union)}"

def resolve_autofill(p):
    a, b = json.loads(stage(p, '2')), json.loads(stage(p, '3'))
    ta, tb = a.get('last_tick', {}).get('ts', ''), b.get('last_tick', {}).get('ts', '')
    base, lose = (b, a) if tb >= ta else (a, b)
    la, lb = a.get('launches', []), b.get('launches', [])
    ident = lambda e: json.dumps({k: e.get(k) for k in sorted(e) if k not in ('status', 'last_write_ts', 'heartbeat_ts')}, sort_keys=True)
    cur = {}
    for e in la + lb:
        key = ident(e)
        old = cur.get(key)
        if old is None or str(e.get('last_write_ts', e.get('heartbeat_ts', ''))) >= str(old.get('last_write_ts', old.get('heartbeat_ts', ''))):
            cur[key] = e
    base['launches'] = sorted(cur.values(), key=lambda e: str(e.get('started_at', e.get('last_write_ts', ''))))
    for k in lose:
        if k not in ('launches', 'last_tick') and k not in base:
            base[k] = lose[k]
    return json.dumps(base, ensure_ascii=False, indent=1), f"launch-union {len(la)}+{len(lb)}->{len(cur)} last_tick take-{'mine' if tb >= ta else 'origin'}"

def resolve_audit(p):
    a, b = json.loads(stage(p, '2')), json.loads(stage(p, '3'))
    ha, hb = a.get('history', []), b.get('history', [])
    cur = {}
    for e in ha + hb:
        t = e.get('ts', '')
        if t not in cur or t >= cur[t].get('ts', ''):
            cur[t] = e
    merged = sorted(cur.values(), key=lambda e: e.get('ts', ''))
    latest = max((a.get('latest'), b.get('latest')), key=lambda e: str(e.get('ts', ''))) if (a.get('latest') and b.get('latest')) else (a.get('latest') or b.get('latest'))
    base = a if str(a.get('latest', {}).get('ts', '')) >= str(b.get('latest', {}).get('ts', '')) else b
    base['history'] = merged
    base['latest'] = latest
    return json.dumps(base, ensure_ascii=False, indent=1), f"history-union {len(ha)}+{len(hb)}->{len(merged)} latest take-new {latest.get('ts')}"

TAKE_FRESH = [
    'docs/daily_report/REPORT-2026-09-28.json', 'docs/daily_report/REPORT-2026-09-28.md',
    'results/dashboard_status.js', 'results/dashboard_status.json',
    'results/fundamental_b_layer_filter.json', 'results/futures_update_status.json',
    'results/heat_update_status.json', 'results/lhb_update_status.json',
    'results/regime_state.json', 'results/scorecard_v1.json',
    'results/strategy_scorecard.json', 'results/update_status.json',
]
SPECIAL = {
    'results/token_usage.json': resolve_token_usage,
    'results/autofill_state.json': resolve_autofill,
    'results/compute_audit.json': resolve_audit,
}

log = []
for p in TAKE_FRESH:
    content, note = resolve_take_fresh(p)
    open(p, 'w', encoding='utf-8', newline='\n').write(content)
    log.append(f'{p}: take-fresh -> {note}')
for p, fn in SPECIAL.items():
    content, note = fn(p)
    open(p, 'w', encoding='utf-8', newline='\n').write(content)
    log.append(f'{p}: {note}')
# zero-marker parse-verify (r185 law)
bad = []
for p in TAKE_FRESH + list(SPECIAL):
    t = open(p, encoding='utf-8').read()
    if re.search(r'^(<<<<<<<|=======$|>>>>>>>)', t, re.M):
        bad.append(p)
if bad:
    sys.exit('MARKERS REMAIN: ' + ','.join(bad))
print('\n'.join(log))
print('RESOLVE OK, 15 files, zero markers')
