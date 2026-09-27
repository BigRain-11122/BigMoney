# r338 bm-b resolver: push-rejection rebase storm (766356a2 onto 218d2ff8 bm-c r95)
# 16 UU: 2 rolling-ledger (compute_audit/regime_state) + 1 mixed (autofill_state) + 13 take-new-by-deep-ts
# Laws: r188/R208/r140(tie->HEAD)/r185(parse-before-write)/r223-r234(EOL face)/r245(asc write-back)/r333(per-face key)
#       r311/D-20260927-09(deep ts probe)/R209(js wrapper whole-bytes)
import subprocess, json, re, sys

def blob(stage, path):
    r = subprocess.run(['git', 'show', stage.rstrip(':') + ':' + path], capture_output=True)
    assert r.returncode == 0, (stage, path, r.stderr[:200])
    return r.stdout

TS_HINT = re.compile(r'^(ts|time|asof|date|updated|updated_at|generated|generated_at|fetched|last_fetch|snapshot_ts|epoch)$|(_ts|_at|_epoch)$')

def deep_ts(obj, best=None):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and TS_HINT.match(k) and len(v) >= 8:
                if best is None or v > best: best = v
            elif isinstance(v, (int, float)) and TS_HINT.match(k) and v > 10**9:
                s = str(v)
                if best is None or s > best: best = s
            best = deep_ts(v, best)
    elif isinstance(obj, list):
        for i in obj: best = deep_ts(i, best)
    return best

def face_of(raw):
    indent = 1
    m = re.search(rb'\n([ \t]+)"', raw)
    if m: indent = len(m.group(1).replace(b'\t', b'    '))
    return {'crlf': b'\r\n' in raw, 'nl_end': raw.endswith(b'\n'), 'indent': indent,
            'ascii': all(b < 128 for b in raw[:4000])}

def emit(obj, face):
    out = json.dumps(obj, ensure_ascii=not face['ascii'], indent=face['indent']).encode('utf-8')
    if face['crlf']: out = out.replace(b'\n', b'\r\n')
    if not face['nl_end']: out = out.rstrip(b'\r\n') if face['nl_end'] is False else out
    if not face['nl_end']: out = out[:-2] if (face['crlf'] and out.endswith(b'\r\n')) else out.rstrip(b'\n')
    json.loads(out.decode('utf-8'))  # r185 parse-verify before write
    return out

def entry_keys(items_a, items_b):
    ka = {k for k in (items_a[0] if items_a else {})} | {k for k in (items_b[0] if items_b else {})}
    return tuple(sorted(k for k in ka if any(TS_HINT.match(k) for _ in [0]) and k in ka and TS_HINT.match(k)))

def dedup_key(e, keys):
    if not keys: return json.dumps(e, sort_keys=True, ensure_ascii=False)
    return tuple(e.get(k) for k in keys)

def log(s): print(s, flush=True)

resolved = []
def take_new(path, kind='json'):
    o_raw, t_raw = blob(':2:', path), blob(':3:', path)
    if kind == 'json':
        o, t = json.loads(o_raw), json.loads(t_raw)
        to, tt = deep_ts(o), deep_ts(t)
        pick_t = tt is not None and (to is None or tt > to)   # tie or missing -> :2: HEAD (r140)
    else:  # text: regex ISO probe
        iso = rb'20\d{2}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}'
        to = max(m.group(0) for m in re.finditer(iso, o_raw)) if re.search(iso, o_raw) else None
        tt = max(m.group(0) for m in re.finditer(iso, t_raw)) if re.search(iso, t_raw) else None
        pick_t = tt is not None and (to is None or tt > to)
    win_raw = t_raw if pick_t else o_raw
    side = ':3:(bm-b r338)' if pick_t else ':2:(upstream HEAD)'
    open(path, 'wb').write(win_raw)
    log('  %-52s take-new %-18s ts(ours=%s theirs=%s)' % (path, side, to, tt))
    resolved.append(path)

def union_ledger_top(path, union_keys, sort_asc=True):
    b_raw, o_raw, t_raw = blob(':1:', path), blob(':2:', path), blob(':3:', path)
    B, O, T = json.loads(b_raw), json.loads(o_raw), json.loads(t_raw)
    face = face_of(o_raw)
    out = {}
    for k in O:
        ov, tv = O[k], T.get(k)
        if k in union_keys and isinstance(ov, list) and isinstance(tv, list):
            keys = entry_keys(ov, tv)
            omap = {dedup_key(e, keys): e for e in ov}
            tmap = {dedup_key(e, keys): e for e in tv}
            shared = set(omap) & set(tmap)
            for kk in shared:
                if json.dumps(omap[kk], sort_keys=True) != json.dumps(tmap[kk], sort_keys=True):
                    merged = dict(omap[kk]); merged.update(tmap[kk]); omap[kk] = merged
                    log('    %s[%s]: shared-key field-supplement merge' % (path, k))
            union = dict(omap)
            for kk, e in tmap.items():
                if kk not in union: union[kk] = e
            expect = len(set(omap) | set(tmap))
            assert len(union) == expect, ('union count', path, k, len(union), expect)
            base_keys = {dedup_key(e, keys) for e in B.get(k, [])}
            lost = base_keys - set(union)
            assert not lost, ('BASE ROW LOST', path, k, sorted(lost)[:3])
            items = list(union.values())
            if keys and sort_asc: items.sort(key=lambda e: tuple(str(x) for x in (e.get(keys[0]),)))
            out[k] = items
            log('  %-52s union[%s] rows=%d (|O|=%d |T|=%d shared=%d) keys=%s' % (path, k, len(items), len(omap), len(tmap), len(shared), keys))
        elif isinstance(ov, dict) and isinstance(tv, dict) and k == 'last_tick':
            to, tt = deep_ts(ov), deep_ts(tv)
            out[k] = tv if (tt is not None and (to is None or tt > to)) else ov
            assert isinstance(out[k], dict), 'last_tick must stay dict'
            log('  %-52s last_tick whole-dict take (%s side)' % (path, 'theirs' if out[k] is tv else 'ours'))
        else:
            to, tt = deep_ts(ov), deep_ts(tv)
            out[k] = tv if (tt is not None and (to is None or tt > to)) else ov
    for k in T:
        if k not in O: out[k] = T[k]; log('  %-52s key %r theirs-only carried' % (path, k))
    open(path, 'wb').write(emit(out, face))
    resolved.append(path)

def autofill_cap50(path):
    b_raw, o_raw, t_raw = blob(':1:', path), blob(':2:', path), blob(':3:', path)
    B, O, T = json.loads(b_raw), json.loads(o_raw), json.loads(t_raw)
    face = face_of(o_raw)
    lo, lt = O.get('launches', []), T.get('launches', [])
    keys = entry_keys(lo, lt)
    omap = {dedup_key(e, keys): e for e in lo}; tmap = {dedup_key(e, keys): e for e in lt}
    for kk in set(omap) & set(tmap):
        if json.dumps(omap[kk], sort_keys=True) != json.dumps(tmap[kk], sort_keys=True):
            m = dict(omap[kk]); m.update(tmap[kk]); omap[kk] = m
    union = dict(omap)
    for kk, e in tmap.items():
        if kk not in union: union[kk] = e
    expect = len(set(omap) | set(tmap)); assert len(union) == expect, ('cap50 union count', len(union), expect)
    base_keys = {dedup_key(e, keys) for e in B.get('launches', [])}
    assert not (base_keys - set(union)), ('BASE LOST', sorted(base_keys - set(union))[:3])
    sortk = keys[0] if keys else None
    items = sorted(union.values(), key=lambda e: (str(e.get(sortk)) if sortk else json.dumps(e, sort_keys=True)), reverse=True)[:50]  # cap 50 = keep newest
    items = sorted(items, key=lambda e: (str(e.get(sortk)) if sortk else json.dumps(e, sort_keys=True)))  # r245: write back ASC (producer append order)
    out = {}
    for k in O:
        ov, tv = O[k], T.get(k)
        if k == 'launches': out[k] = items; continue
        if k == 'last_tick' and isinstance(ov, dict) and isinstance(tv, dict):
            to, tt = deep_ts(ov), deep_ts(tv)
            out[k] = tv if (tt is not None and (to is None or tt > to)) else ov
            assert isinstance(out[k], dict)
        else:
            to, tt = deep_ts(ov), deep_ts(tv)
            out[k] = tv if (tt is not None and (to is None or tt > to)) else ov
    for k in T:
        if k not in O: out[k] = T[k]
    log('  %-52s launches union=%d -> cap50=%d asc-written, keys=%s' % (path, len(union), len(items), keys))
    open(path, 'wb').write(emit(out, face))
    resolved.append(path)

log('r338 resolver: 16 UU')
# --- rolling-ledger + mixed ---
union_ledger_top('results/compute_audit.json', {'history'})
union_ledger_top('results/regime_state.json', {'history', 'transitions', 'launches'})
autofill_cap50('results/autofill_state.json')
# --- js wrapper whole-bytes (R209) ---
o_raw, t_raw = blob(':2:', 'results/dashboard_status.js'), blob(':3:', 'results/dashboard_status.js')
mo = re.search(rb'window\.DASH_DATA\s*=\s*(\{.*\})\s*;?\s*$', o_raw, re.S); mt = re.search(rb'window\.DASH_DATA\s*=\s*(\{.*\})\s*;?\s*$', t_raw, re.S)
assert mo and mt, 'js wrapper shape drift'
to, tt = deep_ts(json.loads(mo.group(1))), deep_ts(json.loads(mt.group(1)))
pick_t = tt is not None and (to is None or tt > to)
open('results/dashboard_status.js', 'wb').write(t_raw if pick_t else o_raw)
log('  %-52s js-wrapper whole-bytes take %s (ts %s/%s)' % ('results/dashboard_status.js', ':3:' if pick_t else ':2:', to, tt))
resolved.append('results/dashboard_status.js')
# --- take-new family (snapshot + regenerable artifacts incl. 5 classifier-UNKNOWN manually qualified) ---
for p in ['results/dashboard_status.json', 'results/fundamental_b_layer_filter.json', 'results/futures_update_status.json',
          'results/heat_update_status.json', 'results/lhb_update_status.json', 'results/token_usage.json', 'results/update_status.json',
          'results/scorecard_v1.json', 'results/strategy_scorecard.json', 'results/prospect_promotion/_summary.json',
          'docs/daily_report/REPORT-2026-09-27.json']:
    take_new(p, 'json')
take_new('docs/daily_report/REPORT-2026-09-27.md', 'text')
# --- stage all resolved (autocrlf=false: zero translation churn) ---
for p in resolved:
    r = subprocess.run(['git', '-c', 'core.autocrlf=false', 'add', p], capture_output=True)
    assert r.returncode == 0, (p, r.stderr[:200])
    sg = subprocess.run(['git', 'show', ':' + p], capture_output=True).stdout
    assert not any(m in sg for m in (b'<<<<<<<', b'>>>>>>>', b'=======')), ('marker in staged', p)
unm = subprocess.run(['git', 'diff', '--name-only', '--diff-filter=U'], capture_output=True).stdout.decode().strip()
assert unm == '', ('still unmerged', unm)
log('STAGED OK: %d files, zero markers, zero unmerged' % len(resolved))
print('RESOLVER PASS')
