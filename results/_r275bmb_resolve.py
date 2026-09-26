# r275 bm-b rebase conflict resolver (S7 push rejected same-window vs bm-a r271).
# Skill: bigmoney-conflict-resolve. 16 UU files: 12 classified + 4 UNKNOWN
# hand-adjudicated per r242 (daily_report json-twin governs, md same-side whole
# bytes) + r267 (scorecard family = generated-only drift, take-new by generated).
# Rebase semantics: :2 ours = origin/bm-a r271, :3 theirs = my be5b4420.
# r140 same-second tie -> ours. r265 format law: normalize T/space before max().
# All take-new files: winner blob written VERBATIM (zero format drift).
import json, subprocess, sys, re, datetime, io

def blob(stage, path):
    return subprocess.check_output(['git', 'show', f':{stage}:{path}'])

def probe_ts(obj, depth=0):
    # recursive two-level ts probe (r267); returns best candidate ts string or None
    best = None
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and re.match(r'^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}', v):
                if k.lower() in ('ts', 'updated', 'updated_at', 'generated', 'generated_at',
                                 'as_of', 'asof', 'last_attempt', 'last_fetch', 'completed_at'):
                    if best is None or norm(v) > norm(best):
                        best = v
            elif isinstance(v, (dict, list)) and depth < 2:
                sub = probe_ts(v, depth + 1)
                if sub is not None and (best is None or norm(sub) > norm(best)):
                    best = sub
    elif isinstance(obj, list):
        for v in obj[:3] + (obj[-3:] if len(obj) > 3 else []):
            sub = probe_ts(v, depth + 1)
            if sub is not None and (best is None or norm(sub) > norm(best)):
                best = sub
    return best

def norm(s):
    return s.replace('T', ' ')

def parse_face(path, raw):
    # R209: dashboard_status.js is a window.DASH_DATA = {...}; wrapper, not plain JSON
    if path.endswith('.js'):
        m = re.match(r'^\s*\w+\.DASH_DATA\s*=\s*(\{.*\})\s*;?\s*$', raw.decode('utf-8-sig'), re.S)
        if not m:
            raise ValueError(f'{path}: DASH_DATA wrapper not found')
        return json.loads(m.group(1))
    return json.loads(raw.decode('utf-8-sig'))

def take_new(path, key_hint=None):
    a, b = blob(2, path), blob(3, path)
    ja, jb = parse_face(path, a), parse_face(path, b)
    ta, tb = probe_ts(ja), probe_ts(jb)
    if ta is None or tb is None:
        print(f'  {path}: ts probe FAIL ({ta} vs {tb}) -> UNKNOWN, manual')
        return None
    if norm(tb) > norm(ta):
        winner, side = b, 'theirs(bm-b)'
    elif norm(tb) < norm(ta):
        winner, side = a, 'ours(bm-a)'
    else:
        winner, side = a, 'ours(bm-a) TIE-r140'
    open(path, 'wb').write(winner)
    print(f'  {path}: take-new {side} (ours_ts={ta} theirs_ts={tb})')
    return side

def face(raw):
    return {'bom': raw.startswith(b'\xef\xbb\xbf'), 'crlf': b'\r\n' in raw,
            'trailing_nl': raw.endswith(b'\n'),
            'indent': 2 if b'\n  "' in raw[:400] or b'\n  {' in raw[:400] else 1}

def dump_mirror(path, obj, mirror_raw):
    f = face(mirror_raw)
    enc = 'utf-8-sig' if f['bom'] else 'utf-8'
    nl = '\r\n' if f['crlf'] else '\n'
    s = json.dumps(obj, ensure_ascii=False, indent=f['indent'])
    if f['trailing_nl']:
        s += '\n'
    open(path, 'w', encoding=enc, newline='').write(s)

resolved, manual = [], []

# ---- 1. CODELY.md: memory-union (ours + theirs-only lines appended) ----
p = 'CODELY.md'
a_lines = blob(2, p).decode('utf-8-sig').splitlines()
b_lines = blob(3, p).decode('utf-8-sig').splitlines()
seen = set(a_lines)
extra = [l for l in b_lines if l not in seen and l.strip()]
merged = a_lines + extra
raw = '\n'.join(merged) + ('\n' if blob(2, p).endswith(b'\n') else '')
open(p, 'w', encoding='utf-8', newline='').write(raw)
print(f'  {p}: memory-union (ours {len(a_lines)} + theirs-only {len(extra)})')
resolved.append(p)

# ---- 2. autofill_state.json: mixed-dict+ledger (r203/R208/r215/r220/r245) ----
p = 'results/autofill_state.json'
a, b = blob(2, p), blob(3, p)
ja, jb = json.loads(a.decode('utf-8-sig')), json.loads(b.decode('utf-8-sig'))
out = dict(ja)
la, lb = ja.get('launches', []), jb.get('launches', [])
by_ts = {}
for row in la + lb:
    ts = row.get('ts') or row.get('time') or json.dumps(row, sort_keys=True)
    by_ts[ts] = row
union = sorted(by_ts.values(), key=lambda r: r.get('ts', ''))   # asc producer order (r245)
out['launches'] = union[-50:]                                   # cap 50 keeps newest
out['launches'] = sorted(out['launches'], key=lambda r: r.get('ts', ''))  # re-sort asc pre-write (r245 law)
ta = (ja.get('last_tick') or {}).get('ts')
tb = (jb.get('last_tick') or {}).get('ts')
if tb and (not ta or tb >= ta):
    out['last_tick'] = jb.get('last_tick')
elif ta:
    out['last_tick'] = ja.get('last_tick')
assert isinstance(out.get('last_tick'), dict), 'last_tick not dict'
dump_mirror(p, out, a)
resolved.append(p)
print(f"  {p}: launches union {len(la)}+{len(lb)} -> {len(out['launches'])} (asc, cap50); last_tick ts {ta} vs {tb}")

# ---- 3. compute_audit.json: rolling-ledger history union + snapshot take-new ----
p = 'results/compute_audit.json'
a, b = blob(2, p), blob(3, p)
ja, jb = json.loads(a.decode('utf-8-sig')), json.loads(b.decode('utf-8-sig'))
ha, hb = ja.get('history', []), jb.get('history', [])
seen = set(json.dumps(r, sort_keys=True, ensure_ascii=False) for r in ha)
union = ha + [r for r in hb if json.dumps(r, sort_keys=True, ensure_ascii=False) not in seen]
union.sort(key=lambda r: r.get('ts', ''))
out = dict(jb if (probe_ts(jb) or '') >= (probe_ts(ja) or '') else ja)   # snapshot fields take-new
out['history'] = union
dump_mirror(p, out, a)
resolved.append(p)
print(f"  {p}: history union {len(ha)}+{len(hb)} -> {len(union)} zero-loss; snapshot side ts={probe_ts(out) and ''}{out.get('ts', '')}")

# ---- 4. regime_state.json: rolling-ledger history union + state take-new ----
p = 'results/regime_state.json'
a, b = blob(2, p), blob(3, p)
ja, jb = json.loads(a.decode('utf-8-sig')), json.loads(b.decode('utf-8-sig'))
merged_hist = {}
for k in ('history', 'transitions'):
    if k in ja or k in jb:
        ha, hb = ja.get(k, []), jb.get(k, [])
        seenk = set(json.dumps(r, sort_keys=True, ensure_ascii=False) for r in ha)
        merged_hist[k] = ha + [r for r in hb if json.dumps(r, sort_keys=True, ensure_ascii=False) not in seenk]
out = dict(jb if norm(str(probe_ts(jb) or '')) >= norm(str(probe_ts(ja) or '')) else ja)
out.update(merged_hist)
dump_mirror(p, out, a)
resolved.append(p)
print(f"  {p}: history/transitions union kept; state take-new ts={out.get('asof') or out.get('ts')}")

# ---- 5. daily_report pair (UNKNOWN -> r242: json twin generated_at governs) ----
pj = 'docs/daily_report/REPORT-2026-09-26.json'
pm = 'docs/daily_report/REPORT-2026-09-26.md'
ja = json.loads(blob(2, pj).decode('utf-8-sig'))
jb = json.loads(blob(3, pj).decode('utf-8-sig'))
ga, gb = probe_ts(ja), probe_ts(jb)
side = 'theirs' if (gb and (not ga or norm(gb) > norm(ga))) else 'ours'
open(pj, 'wb').write(blob(3 if side == 'theirs' else 2, pj))
open(pm, 'wb').write(blob(3 if side == 'theirs' else 2, pm))
resolved += [pj, pm]
print(f'  daily_report pair: json generated_at ours={ga} vs theirs={gb} -> {side} whole bytes both files')

# ---- 6. snapshot / take-new families ----
for p in ['results/dashboard_status.json', 'results/dashboard_status.js',
          'results/fundamental_b_layer_filter.json', 'results/futures_update_status.json',
          'results/heat_update_status.json', 'results/lhb_update_status.json',
          'results/update_status.json', 'results/token_usage.json',
          'results/scorecard_v1.json', 'results/strategy_scorecard.json']:
    s = take_new(p)
    if s is None:
        manual.append(p)
    else:
        resolved.append(p)

# ---- parse-verify all resolved json/js files before add (r185) ----
fails = []
for p in resolved:
    if p.endswith('.json'):
        try:
            json.loads(open(p, encoding='utf-8-sig').read())
        except Exception as e:
            fails.append((p, str(e)))
    elif p.endswith('.js'):
        m = re.match(r'^\s*window\.DASH_DATA\s*=\s*(\{.*\})\s*;?\s*$', open(p, encoding='utf-8-sig').read(), re.S)
        if not m or not json.loads(m.group(1)):
            fails.append((p, 'js wrapper parse fail'))
print('parse-verify:', 'ALL PASS' if not fails else fails)
if manual:
    print('MANUAL REQUIRED:', manual)
sys.exit(1 if (fails or manual) else 0)
