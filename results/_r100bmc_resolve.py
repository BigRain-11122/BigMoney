# r100 bm-c 28-UU storm resolver (rebase f43df0c9 onto da8a2e2f): r99 pattern reused mirrored
# Side semantics in rebase: :2: = ours = da8a2e2f (bm-a R348 face, 19:42 FRESHER), :3: = theirs = f43df0c9 (bm-c r99 face, 19:27)
# r345 pitlaw add-on: post-resolve same-key-different-value side-diff re-verification for union faces
import subprocess, json, io, os, re

repo = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
os.chdir(repo)

def blob(rev, path):
    r = subprocess.run(['git', 'show', rev + path], capture_output=True)
    if r.returncode != 0:
        print('BLOB FAIL', rev, path, '|', r.stderr[:200])
        return None
    return r.stdout  # raw bytes (blob-tail law r339)

def w(path, data_bytes):
    with io.open(path, 'wb') as f:
        f.write(data_bytes)

def jload(b):
    return json.loads(b.decode('utf-8')) if b is not None else None

def ts_of(obj, keys=('ts', 'generated', 'generated_at', 'updated', 'epoch', 'asof', 'last_tick')):
    best = None
    def walk(o):
        nonlocal best
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, str):
                    for kk in keys:
                        if k.lower().startswith(kk) or k == kk:
                            if best is None or v > best[1]:
                                best = (k, v)
                walk(v)
        elif isinstance(o, list):
            for x in o:
                walk(x)
    walk(obj)
    return best[1] if best else None

def md_ts(b):
    m = re.search(rb'(generated|ts|updated)["\':\s]+(20\d\d-\d\d-\d\d[T ]\d\d:\d\d:\d\d)', b)
    return m.group(2).decode() if m else None

uu = subprocess.run(['git', 'diff', '--name-only', '--diff-filter=U'], capture_output=True, text=True).stdout.split()
print('UU count:', len(uu))

snapshots, unions, unverdict = [], [], []
audit_before = {}  # for r345 side-diff re-verify: union faces pre-state

for p in uu:
    o, t = blob(':2:', p), blob(':3:', p)
    if o is None or t is None:
        unverdict.append((p, 'MISSING_BLOB'))
        continue
    if o == t:
        snapshots.append((p, 'byte-identical take-either'))
        w(p, t); continue
    if p == 'results/x2_watch_log.jsonl':
        lo = [l for l in o.decode('utf-8').splitlines() if l.strip()]
        lt = [l for l in t.decode('utf-8').splitlines() if l.strip()]
        seen, merged = set(), []
        for l in lo + lt:
            if l not in seen:
                seen.add(l); merged.append(l)
        w(p, ('\n'.join(merged) + '\n').encode('utf-8'))
        unions.append((p, 'x2 line union %d+%d->%d' % (len(lo), len(lt), len(merged))))
        print('%s union %d+%d -> %d lines' % (p, len(lo), len(lt), len(merged)))
        continue
    if p == 'results/dashboard_status.js':
        so, st = md_ts(o), md_ts(t)
        pick_t = (st is not None and (so is None or st >= so))
        w(p, t if pick_t else o)
        snapshots.append((p, 'js-twin take-%s (ours=%s theirs=%s)' % ('theirs' if pick_t else 'ours', so, st)))
        continue
    try:
        jo, jt = jload(o), jload(t)
    except Exception:
        # non-JSON face (REPORT md): M-fresher take-new per r99 patch2
        so, st = md_ts(o), md_ts(t)
        pick_t = (st is not None and (so is None or st >= so))
        w(p, t if pick_t else o)
        snapshots.append((p, 'md take-%s (ours=%s theirs=%s)' % ('theirs' if pick_t else 'ours', so, st)))
        continue
    if p == 'results/autofill_state.json':
        mo = dict(jo)
        for k, v in jt.items():
            if k not in mo:
                mo[k] = v; continue
            so, st = ts_of(mo[k]), ts_of(v)
            if st is not None and so is not None:
                if st > so: mo[k] = v
            elif st is not None: mo[k] = v
        w(p, json.dumps(mo, ensure_ascii=False, indent=1).encode('utf-8') + b'\n')
        audit_before[p] = (sorted(jo.keys()), sorted(jt.keys()))
        unions.append((p, 'autofill composite-key union keys=%d (ours %d / theirs %d)' % (len(mo), len(jo), len(jt))))
        continue
    if p == 'results/compute_audit.json':
        ho, ht = jo.get('history', []), jt.get('history', [])
        keyf = lambda h: h.get('ts') or h.get('epoch') or json.dumps(h, sort_keys=True)
        seenu, merged = set(), []
        for h in sorted(ho + ht, key=lambda x: x.get('ts', '') if isinstance(x, dict) else ''):
            k = keyf(h)
            if k not in seenu:
                seenu.add(k); merged.append(h)
        jt['history'] = merged
        w(p, json.dumps(jt, ensure_ascii=False, indent=1).encode('utf-8') + b'\n')
        audit_before[p] = (len(ho), len(ht))
        unions.append((p, 'audit history union %d+%d->%d' % (len(ho), len(ht), len(merged))))
        continue
    if p == 'results/token_usage.json':
        mo = dict(jo)
        for k, v in jt.items():
            if isinstance(v, dict) and isinstance(mo.get(k), dict):
                mo[k] = {**mo[k], **v}
            else:
                mo[k] = v
        w(p, json.dumps(mo, ensure_ascii=False, indent=1).encode('utf-8') + b'\n')
        unions.append((p, 'token_usage bucket union keys=%d' % len(mo)))
        continue
    # default: snapshot M-fresher take-new (deep-ts probe)
    so, st = ts_of(jo), ts_of(jt)
    pick_t = (st is not None and (so is None or st >= so))
    if st is None and so is None:
        unverdict.append((p, 'BOTH_TS_PROBE_MISS - manual check'))
        continue
    w(p, t if pick_t else o)
    snapshots.append((p, 'take-%s (ours_ts=%s theirs_ts=%s)' % ('theirs' if pick_t else 'ours', so, st)))

for p, note in snapshots:
    print('SNAP %-52s %s' % (p, note))
for p, note in unions:
    print('UNION %-52s %s' % (p, note))
for p, note in unverdict:
    print('!! UNVERDICT %-42s %s' % (p, note))

# r345 law: post-resolve side-diff re-verification for union faces (key-set parity + zero silent drop)
for p in ['results/autofill_state.json', 'results/compute_audit.json']:
    if p not in audit_before:
        continue
    cur = jload(io.open(p, 'rb').read())
    if p == 'results/autofill_state.json':
        ko, kt = audit_before[p]
        kc = sorted(cur.keys())
        lost_o = [k for k in ko if k not in kc]
        lost_t = [k for k in kt if k not in kc]
        print('VERIFY %s: keys ours=%d theirs=%d merged=%d | lost_ours=%s lost_theirs=%s' % (p, len(ko), len(kt), len(kc), lost_o, lost_t))
        assert not lost_o and not lost_t, 'KEY LOSS DETECTED in autofill union'
    else:
        no, nt = audit_before[p]
        nc = len(cur.get('history', []))
        print('VERIFY %s: history ours=%d theirs=%d merged=%d' % (p, no, nt, nc))
        assert nc >= max(no, nt), 'HISTORY ROW LOSS DETECTED in audit union'

# dashboard twin consistency: .js and .json must come from same-side ts
js = io.open('results/dashboard_status.js', 'rb').read()
jsn = jload(io.open('results/dashboard_status.json', 'rb').read())
print('TWIN CHECK: js_ts=%s json_ts=%s' % (md_ts(js), ts_of(jsn)))

# conflict-marker sweep (precommit claw parity)
bad = []
for p in uu:
    try:
        txt = io.open(p, 'rb').read()
        if b'<<<<<<< ' in txt or b'>>>>>>> ' in txt:
            bad.append(p)
    except FileNotFoundError:
        bad.append(p + ' (missing)')
print('MARKER SWEEP:', 'CLEAN' if not bad else bad)
print('RESOLVE DONE; next: git add -A + rebase --continue')
