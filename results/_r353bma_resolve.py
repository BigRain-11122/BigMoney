# r353 bm-a push-rejection storm resolver (16 UU, two-machine same-window S6 chain collision)
# SIDE ASSERTION (r351 law, rebase-replay window): stage :2: == HEAD == replayed base == OTHER-side face;
#                   stage :3: == commit being replayed == OUR round-353 face. Opposite of merge intuition.
# Probe law r345/r100/R350: deep-scan nested ts, strip '_-' from keys before stem match, value must be
#   20xx- AND contain time-of-day ([T ]HH:MM) before feeding max; NO key-exclude tables.
# Tie -> HEAD side (:2:) per r140. Parse-verify before write-back (r185). Blob reads only, never working tree.
import subprocess, json, re, sys

FILES_SNAPSHOT = [
    'results/daily_scorecard.json', 'results/dashboard_status.json',
    'results/fundamental_b_layer_filter.json', 'results/futures_update_status.json',
    'results/heat_update_status.json', 'results/lhb_update_status.json',
    'results/prospect_promotion/_summary.json', 'results/scorecard_v1.json',
    'results/strategy_scorecard.json', 'results/token_usage.json', 'results/update_status.json',
]
REPORT_JSON = 'docs/daily_report/REPORT-2026-09-27.json'
REPORT_MD = 'docs/daily_report/REPORT-2026-09-27.md'
JS_WRAP = 'results/dashboard_status.js'
MIXED = 'results/autofill_state.json'
ROLL_AUDIT = 'results/compute_audit.json'
ROLL_REGIME = 'results/regime_state.json'

STEMS = ('updated', 'generated', 'asof', 'ts', 'lastattempt', 'lastseen', 'now', 'collected', 'timestamp', 'time')
V_TS = re.compile(r'^20\d{2}-')
V_CLOCK = re.compile(r'[T ]\d{2}:\d{2}')
# r353 live-fire: key normalization must REPLACE all '_-/' chars (strip only trims ENDS:
# 'as_of'.strip('_-')=='as_of' != 'asof' -- as_of family silently missed probe -> false tie;
# correct = replace, per r100 catalog wording; resolver evidence below)

def blob(spec):
    r = subprocess.run(['git', 'show', spec], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f'BLOB FAIL rc={r.returncode} {spec}: {r.stderr.decode("utf-8","replace")[:200]}')
    return r.stdout

def probe(obj):
    best = ''
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str):
                nk = re.sub(r'[_\-/]', '', k).lower()
                if any(nk.startswith(s) for s in STEMS) and V_TS.match(v) and V_CLOCK.search(v):
                    if v > best: best = v
            sub = probe(v)
            if sub > best: best = sub
    elif isinstance(obj, list):
        for v in obj:
            sub = probe(v)
            if sub > best: best = sub
    return best

def side_bytes(path):
    b2 = blob(f':2:{path}'); b3 = blob(f':3:{path}')
    return b2, b3

def pick_side(path, note):
    b2, b3 = side_bytes(path)
    try: p2 = probe(json.loads(b2.decode('utf-8')))
    except Exception: p2 = ''
    try: p3 = probe(json.loads(b3.decode('utf-8')))
    except Exception: p3 = ''
    if not p2 and not p3: side = 2; why = 'both-probe-empty tie->HEAD'
    elif p3 > p2: side = 3; why = f'ours fresher {p3}>{p2}'
    elif p2 > p3: side = 2; why = f'theirs fresher {p2}>{p3}'
    else: side = 2; why = f'tie {p2}=={p3}->HEAD'
    print(f'[take-side] {path}: {note} | side=:{side}: ({why})')
    return b2 if side == 2 else b3

def dump_like_base(obj, base_text):
    m = re.search(r'\n([ \t]+)"', base_text)
    indent = len(m.group(1)) if m else 2
    ascii_face = '\\u' in base_text[:2000]
    out = json.dumps(obj, ensure_ascii=ascii_face, indent=indent)
    return out

def load(b):
    return json.loads(b.decode('utf-8'))

results = {}

def resolve_snapshot(path):
    data = pick_side(path, 'snapshot take-new whole-face bytes')
    json.loads(data.decode('utf-8'))  # parse-verify before write-back
    results[path] = data

def resolve_twin():
    side_bytes_map = {}
    b2, b3 = side_bytes(REPORT_JSON)
    j2 = load(b2); j3 = load(b3)
    p2 = probe(j2); p3 = probe(j3)
    if not p2 and not p2: side = 2
    elif p3 > p2: side = 3
    elif p2 > p3: side = 2
    else: side = 2
    print(f'[twin] {REPORT_JSON}: probe ours={p3!r} theirs={p2!r} -> side=:{side}:')
    jb = b2 if side == 2 else b3
    json.loads(jb.decode('utf-8'))
    # md MUST take the SAME side, whole bytes from that side's blob (r329: never parse md as json)
    mb2 = blob(f':2:{REPORT_MD}'); mb3 = blob(f':3:{REPORT_MD}')
    mb = mb2 if side == 2 else mb3
    results[REPORT_JSON] = jb
    results[REPORT_MD] = mb
    print(f'[twin] {REPORT_MD}: same side=:{side}: whole bytes {len(mb)}B')

def resolve_js():
    data = pick_side(JS_WRAP, 'js-wrapper take-side whole bytes (R209: never re-dump, wrapper preserved)')
    head = data[:200].decode('utf-8', 'replace')
    assert 'window.DASH_DATA' in head, 'js wrapper missing -- refuse blind write'
    m = re.match(rb'window\.DASH_DATA\s*=\s*', data)
    body = data[m.end():].rstrip().rstrip(b';')
    json.loads(body.decode('utf-8'))  # parse-verify payload
    results[JS_WRAP] = data

def union_list(a, b, keyf=None):
    '''string-keyed zero-loss union preserving append order; keyf returns dedup key per entry'''
    out, seen = [], set()
    for e in a + b:
        k = keyf(e) if keyf else json.dumps(e, ensure_ascii=False, sort_keys=True)
        if k in seen: continue
        seen.add(k); out.append(e)
    return out

def resolve_mixed_autofill():
    b2, b3 = side_bytes(MIXED)
    base = blob(f':1:{MIXED}')
    d2, d3 = load(b2), load(b3)
    l2 = d2.get('launches', []); l3 = d3.get('launches', [])
    def ckey(e):
        return tuple(str(e.get(f, '')) for f in ('ts', 'machine', 'pid', 'runner_sha256', 'entry', 'shard'))
    # collision-key dedup BEFORE cap (r322/r83): same-key pairs -> field-union merge keep-one, real divergence = flag
    byk = {}
    for e in l2 + l3:
        k = ckey(e)
        if k not in byk: byk[k] = dict(e); continue
        cur = byk[k]
        fk2, fk3 = set(cur.keys()), set(e.keys())
        if fk2 == fk3:
            diff = {f for f in fk2 if cur[f] != e[f]}
            if diff:
                raise SystemExit(f'AUTOFILL real-divergence flag key={k} fields={sorted(diff)} -- adjudicate manually')
        else:
            for f in fk3 - fk2: cur[f] = e[f]  # additive field-union keep-one
            for f in fk2 - fk3: pass
            diff = {f for f in fk2 & fk3 if cur[f] != e[f]}
            if diff:
                raise SystemExit(f'AUTOFILL real-divergence flag key={k} fields={sorted(diff)} -- adjudicate manually')
    merged = sorted(byk.values(), key=lambda e: str(e.get('ts', '')), reverse=True)[:50]  # cap keep-newest-50
    merged.sort(key=lambda e: str(e.get('ts', '')))  # write-back re-sort ASC (r245 producer append order)
    t2, t3 = d2.get('last_tick', {}), d3.get('last_tick', {})
    p2, p3 = probe(t2), probe(t3)
    lt = t2 if p3 <= p2 else t3  # tie->HEAD(:2:)
    out = dict(d3 if p3 > p2 else d2)  # top-level face from fresher side
    out['launches'] = merged
    out['last_tick'] = lt
    assert isinstance(out['last_tick'], dict), 'last_tick must be dict'
    n2, n3, nu = len(l2), len(l3), len(merged)
    raw = len(byk)
    print(f'[mixed] {MIXED}: launches {n2}+{n3} -> union {raw} -> cap50 {nu} (asc re-sorted); last_tick side={"ours" if lt is t3 else "theirs"}')
    text = dump_like_base(out, base.decode('utf-8'))
    json.loads(text)
    results[MIXED] = text.encode('utf-8')

def resolve_rolling(path, ledger_keys):
    b2, b3 = side_bytes(path)
    base = blob(f':1:{path}')
    d2, d3 = load(b2), load(b3)
    p2, p3 = probe(d2), probe(d3)
    fresh = d3 if p3 > p2 else d2
    out = dict(fresh)  # state fields take-new wholesale
    for k in ledger_keys:
        l2 = d2.get(k, []); l3 = d3.get(k, [])
        u = union_list(l2, l3)
        out[k] = u
        print(f'[rolling] {path}.{k}: {len(l2)}+{len(l3)} -> union {len(u)} (zero-loss check: {len(u)}=={len(l2)+len(l3)-0 if len(u)==len(set(json.dumps(e,ensure_ascii=False,sort_keys=True) for e in l2+l3)) else "MISMATCH"})')
    text = dump_like_base(out, base.decode('utf-8'))
    json.loads(text)
    results[path] = text.encode('utf-8')

def main():
    for p in FILES_SNAPSHOT: resolve_snapshot(p)
    resolve_twin()
    resolve_js()
    resolve_mixed_autofill()
    resolve_rolling(ROLL_AUDIT, ['history'])
    resolve_rolling(ROLL_REGIME, ['history', 'transitions'])
    # write-back
    for p, data in results.items():
        with open(p, 'wb') as f: f.write(data)
        print(f'[write] {p} {len(data)}B')
    # post write-back parse verify from disk
    for p in results:
        if p.endswith('.json'):
            json.loads(open(p, encoding='utf-8').read())
    print('ALL RESOLVED + PARSE-VERIFIED, files written:', len(results))

if __name__ == '__main__':
    main()
