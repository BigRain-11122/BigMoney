# round 480 wave-1 rebase resolver (bigmoney-conflict-resolve skill recipes)
# rebase context: stage2=ours=origin/main(8b496c2fa: bm-a r491/492 + bm-c r289)
#                 stage3=theirs=my r479 commit (8d8ba07d8 replay)
# merge-base for wave1 = 165b194e9
import subprocess, json, re, sys

BASE_REV = '165b194e9'

def stage(n, path):
    r = subprocess.run(['git', 'show', f':{n}:{path}'], capture_output=True)
    return r.stdout if r.returncode == 0 else None

def base_blob(path):
    r = subprocess.run(['git', 'show', f'{BASE_REV}:{path}'], capture_output=True)
    return r.stdout if r.returncode == 0 else b''

WALLCLOCK_RE = re.compile(r'^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}')

def deep_ts(obj):
    # R350: no key-exclude lists; wall-clock values must carry time-of-day; key normalize strip _ -
    best = ''
    def walk(o):
        nonlocal best
        if isinstance(o, dict):
            for k, v in o.items():
                kk = re.sub(r'[_\-]', '', str(k).lower())
                if isinstance(v, str) and WALLCLOCK_RE.match(v):
                    hit = any(s in kk for s in ('ts', 'generated', 'updated', 'asof', 'stamp', 'time', 'date', 'cutoff', 'seen'))
                    if hit and v > best:
                        best = v
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(obj)
    return best

def detect_eol(blob):
    return b'\r\n' if b'\r\n' in blob[:2000] else b'\n'

def detect_indent(blob):
    m = re.search(rb'\n([ \t]+)"', blob)
    return len(m.group(1)) if m else 1

def serialize(obj, ref_blob):
    eol = detect_eol(ref_blob)
    txt = json.dumps(obj, indent=detect_indent(ref_blob), ensure_ascii=False)
    out = txt.encode('utf-8')
    if eol == b'\r\n':
        out = out.replace(b'\n', b'\r\n')
    if ref_blob.endswith((b'\n', b'\r\n')) and not out.endswith(eol):
        out += eol
    if not ref_blob.endswith((b'\n', b'\r\n')) and out.endswith(eol):
        out = out[:-len(eol)]
    return out

def clean_markers(blob):
    # origin/main committed a marker-polluted blob (bm-a r492 missed this one);
    # take HEAD-side lines of each embedded block (their HEAD side = newest pre-existing state)
    if b'<<<<<<<' not in blob:
        return blob
    eol = detect_eol(blob)
    lines = blob.split(eol)
    out, mode = [], 'normal'
    for ln in lines:
        if ln.startswith(b'<<<<<<<'):
            mode = 'head'; continue
        if ln.startswith(b'======='):
            mode = 'other'; continue
        if ln.startswith(b'>>>>>>>'):
            mode = 'normal'; continue
        if mode != 'other':
            out.append(ln)
    return eol.join(out)

def write(path, data):
    with open(path, 'wb') as f:
        f.write(data)

report = []

def take_new_snapshot(path, clean_ours=False):
    o, t = stage(2, path), stage(3, path)
    if clean_ours:
        o = clean_markers(o)
    jo, jt = json.loads(o), json.loads(t)
    to, tt = deep_ts(jo), deep_ts(jt)
    side = 'ours' if (not tt or (to and to >= tt)) else 'theirs'
    if to == tt == '' and to != 'x':
        # tie or no probe: fall back whole-blob newest is unknowable -> take ours (origin) per commit-order law
        side = 'ours'
    write(path, o if side == 'ours' else t)
    report.append(f'{path}: snapshot take-{side} (probe ours={to!r} theirs={tt!r})')

def union_ledger_audit(path):
    o, t = stage(2, path), stage(3, path)
    jo, jt = json.loads(o), json.loads(t)
    ho, ht = jo.get('history', []), jt.get('history', [])
    key_ts = lambda it: it.get('ts') if isinstance(it, dict) and isinstance(it.get('ts'), str) else None
    if all(key_ts(x) for x in ho + ht):
        seen, merged = set(), []
        for it in sorted(ho + ht, key=key_ts):
            k = key_ts(it)
            if k not in seen:
                seen.add(k); merged.append(it)
        jo['history'] = merged
        zero_loss = len(merged)
    else:
        # fallback: repr-dedupe, ours order first then theirs-only
        seen, merged = set(), []
        for it in ho + ht:
            k = json.dumps(it, sort_keys=True, ensure_ascii=False)
            if k not in seen:
                seen.add(k); merged.append(it)
        jo['history'] = merged
        zero_loss = len(merged)
    lo, lt = jo.get('latest', {}), jt.get('latest', {})
    jo['latest'] = lo if (lo.get('ts', '') or '') >= (lt.get('ts', '') or '') else lt
    data = serialize(jo, o)
    write(path, data)
    report.append(f'{path}: ledger union history |ours|={len(ho)} |theirs|={len(ht)} -> {zero_loss}, latest ts={jo["latest"].get("ts")}')

def resolve_regime():
    path = 'results/regime_state.json'
    o, t = stage(2, path), stage(3, path)
    jo, jt = json.loads(o), json.loads(t)
    for lk in ('history', 'transitions'):
        ho, ht = jo.get(lk, []), jt.get(lk, [])
        kk = 'asof' if lk == 'history' else 'ts'
        seen, merged = set(), []
        for it in ho + ht:
            k = it.get(kk) if isinstance(it, dict) else None
            if k is None:
                k = json.dumps(it, sort_keys=True, ensure_ascii=False)
            if k not in seen:
                seen.add(k); merged.append(it)
        jo[lk] = merged
    if (jo.get('updated') or '') >= (jt.get('updated') or ''):
        keep = 'ours'
    else:
        keep = 'theirs'
        for k, v in jt.items():
            if k not in ('history', 'transitions'):
                jo[k] = v
    write(path, serialize(jo, o))
    report.append(f'{path}: state scalars take-{keep} (updated ours={jo.get("updated")!r}), history len={len(jo["history"])}')

def resolve_pool():
    path = 'results/runnable_pool.json'
    o, t = stage(2, path), stage(3, path)
    jo, jt = json.loads(o), json.loads(t)
    eo, et = {x['id']: x for x in jo['entries']}, {x['id']: x for x in jt['entries']}
    merged, absorb, deliberate = 0, 0, 0
    for eid in eo:  # all ids both sides (verified live: 146/146)
        oe, te = eo[eid], et.get(eid)
        if te is None:
            continue
        if oe.get('status') == 'done' and te.get('status') != 'done':
            absorb += 1; continue          # done absorbs: keep ours (origin completed record)
        if te.get('status') == 'done' and oe.get('status') != 'done':
            eo[eid] = te; absorb += 1; continue
        if oe.get('status') == te.get('status'):
            continue                        # identical payload (verified live)
        # status dispute with deliberate annotation on one side -> annotated side wins (info preservation)
        if te.get('defer_note') and not oe.get('defer_note'):
            eo[eid] = te; deliberate += 1; continue
        if oe.get('defer_note') and not te.get('defer_note'):
            deliberate += 1; continue
        report.append(f'  UNRESOLVED entry {eid}: ours={oe.get("status")} theirs={te.get("status")} no note either side')
    write(path, serialize(jo, o))
    report.append(f'{path}: pool union done-absorb={absorb} deliberate-defer-wins={deliberate}, entries={len(jo["entries"])}')

def resolve_codely():
    path = 'CODELY.md'
    o, t, b = stage(2, path), stage(3, path), base_blob(path)
    # common prefix of o vs t (bytes), assert prefix == base (pure-append both sides)
    n = 0
    mlen = min(len(o), len(t))
    while n < mlen and o[n] == t[n]:
        n += 1
    # back up to line boundary
    n2 = o.rfind(b'\n', 0, n)
    prefix = o[:n2 + 1] if n2 >= 0 else b''
    if prefix == b or b == b'':
        merged = prefix + o[len(prefix):] + t[len(prefix):]
        write(path, merged)
        report.append(f'{path}: memory-union DIRECT-CONCAT pass (prefix={len(prefix)}B base={len(b)}B ours-sfx={len(o)-len(prefix)}B theirs-sfx={len(t)-len(prefix)}B -> {len(merged)}B)')
    else:
        # origin reorganized (hot-cold reorg same-window) -> take ours structure, append my-side suffix lines verbatim
        ol, tl = o.split(b'\n'), t.split(b'\n')
        pl = prefix.split(b'\n')
        my_suffix = tl[len(pl) - 1:]
        my_suffix = [x for x in my_suffix if x.strip()]
        oset = set(ol)
        new_lines = [x for x in my_suffix if x not in oset]
        merged = o
        if new_lines:
            if not merged.endswith(b'\n'):
                merged += b'\n'
            merged += b'\n'.join(new_lines) + b'\n'
        write(path, merged)
        report.append(f'{path}: memory-union REORG-FALLBACK (prefix-identity FAILED prefix={len(prefix)}B base={len(b)}B) -> ours {len(o)}B + {len(new_lines)} my new lines -> {len(merged)}B')

def resolve_twin_group(json_path, md_paths):
    o, t = stage(2, json_path), stage(3, json_path)
    jo, jt = json.loads(o), json.loads(t)
    to, tt = deep_ts(jo), deep_ts(jt)
    side = 'ours' if (not tt or (to and to >= tt)) else 'theirs'
    write(json_path, o if side == 'ours' else t)
    for mp in md_paths:
        om, tm = stage(2, mp), stage(3, mp)
        write(mp, om if side == 'ours' else tm)
    report.append(f'{json_path}+twins: take-{side} (probe ours={to!r} theirs={tt!r})')

# ---- wave-1 execution ----
take_new_snapshot('results/futures_update_status.json')
take_new_snapshot('results/lhb_update_status.json')
take_new_snapshot('results/update_status.json')
take_new_snapshot('results/token_usage.json')
take_new_snapshot('results/_attrition_guard_scan.json', clean_ours=True)
take_new_snapshot('results/p2cal_ext/shard-2-of-4.json')  # verified: only audit run-metadata differs
union_ledger_audit('results/compute_audit.json')
union_ledger_audit('results/compute_audit.bm-a.json')
resolve_regime()
resolve_pool()
resolve_codely()
resolve_twin_group('docs/daily_report/REPORT-2026-09-30.json', ['docs/daily_report/REPORT-2026-09-30.md'])
resolve_twin_group('docs/live_usage/LIVE-2026-09-30.json', ['docs/live_usage/LIVE-2026-09-30.md', 'docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md'])

# parse-verify every resolved json before write-back claim (r185 law)
fails = []
for p in ['results/futures_update_status.json', 'results/lhb_update_status.json', 'results/update_status.json',
          'results/token_usage.json', 'results/_attrition_guard_scan.json', 'results/p2cal_ext/shard-2-of-4.json',
          'results/compute_audit.json', 'results/compute_audit.bm-a.json', 'results/regime_state.json',
          'results/runnable_pool.json', 'docs/daily_report/REPORT-2026-09-30.json',
          'docs/live_usage/LIVE-2026-09-30.json', 'docs/live_usage/LIVE-latest.json']:
    try:
        json.loads(open(p, 'rb').read().decode('utf-8'))
    except Exception as e:
        fails.append(f'{p}: {e}')
print('\n'.join(report))
print('PARSE-VERIFY:', 'ALL PASS' if not fails else 'FAIL -> ' + '; '.join(fails))
sys.exit(0 if not fails else 2)
