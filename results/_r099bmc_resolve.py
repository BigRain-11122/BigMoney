# r99 bm-c 28-UU storm resolver (rebase onto 205b9e79): snapshot M-fresher take-new + ledger unions per R345 precedent + r334 union-key law + r339 blob-byte law
# Side semantics in rebase: :2: = ours = 205b9e79 (bm-a R345 face), :3: = theirs = 034baf2a (bm-c r99 face)
import subprocess, json, io, os, sys

repo = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
os.chdir(repo)

def blob(rev, path):
    r = subprocess.run(['git', 'show', rev + path], capture_output=True)
    if r.returncode != 0:
        print('BLOB FAIL', rev, path, '|', r.stderr[:200])
        return None
    return r.stdout  # raw bytes (blob-tail law r339: no worktree CRLF illusion)

def w(path, data_bytes):
    with io.open(path, 'wb') as f:
        f.write(data_bytes)

def jload(b):
    return json.loads(b.decode('utf-8')) if b is not None else None

def ts_of(obj, keys=('ts', 'generated', 'generated_at', 'updated', 'epoch', 'asof', 'last_tick')):
    # deep-probe: find freshest timestamp-looking scalar anywhere (r344 deep-ts probe law: nested layers must be scanned)
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

uu = subprocess.run(['git', 'diff', '--name-only', '--diff-filter=U'], capture_output=True, text=True).stdout.split()
print('UU count:', len(uu))

snapshots, unions, unverdict = [], [], []
for p in uu:
    o, t = blob(':2:', p), blob(':3:', p)
    if o is None or t is None:
        unverdict.append((p, 'MISSING_BLOB'))
        continue
    if o == t:
        snapshots.append((p, 'byte-identical take-either'))  # CRLF-illusion cases land here
        w(p, t); continue
    try:
        jo, jt = jload(o), jload(t)
    except Exception:
        unverdict.append((p, 'NOT_JSON'))
        continue
    # classify: ledger faces -> union; single-snapshot -> M-fresher
    if p == 'results/x2_watch_log.jsonl':
        unions.append((p, 'jsonl line union'))
        lo = [l for l in o.decode('utf-8').splitlines() if l.strip()]
        lt = [l for l in t.decode('utf-8').splitlines() if l.strip()]
        # dedup by (key: watch epoch/day fields) keep both fresh-order = union with dedup key = full line minus volatile? r334: dedup key must include face-real-time key
        # x2 log lines are append-only events; union = ordered unique lines, dedup on full line identity
        seen, merged = set(), []
        for l in lo + lt:
            if l not in seen:
                seen.add(l); merged.append(l)
        w(p, ('\n'.join(merged) + '\n').encode('utf-8'))
        print('%s union %d+%d -> %d lines' % (p, len(lo), len(lt), len(merged)))
        continue
    if p == 'results/autofill_state.json':
        # r84 composite-key law: state keys are per-batch dicts; union top-level keys, fresher value wins per key; last_tick same-second tie -> take ours(HEAD-side)=:2: per R345 precedent
        mo = {}
        for k, v in jo.items():
            mo[k] = v
        for k, v in jt.items():
            if k not in mo:
                mo[k] = v; continue
            vo, vt = ts_of(v), ts_of(v.get('state') if isinstance(v, dict) else v)
            so, st = ts_of({k: mo[k]}), ts_of({k: v})
            if st is not None and so is not None:
                if st > so: mo[k] = v
                # tie (same-second) -> keep ours (:2:) per R345 last_tick-tie-take-HEAD precedent
            elif st is not None: mo[k] = v
            # so-only -> keep ours
        w(p, json.dumps(mo, ensure_ascii=False, indent=1).encode('utf-8') + b'\n')
        unions.append((p, 'autofill composite-key union key-count %d' % len(mo)))
        print('%s union keys=%d (ours %d / theirs %d)' % (p, len(mo), len(jo), len(jt)))
        continue
    if p == 'results/compute_audit.json':
        # R345/r97 precedent: history array union zero-loss (201|201 -> 202)
        ho, ht = jo.get('history', []), jt.get('history', [])
        keyf = lambda h: h.get('ts') or h.get('epoch') or json.dumps(h, sort_keys=True)
        seenu, merged = set(), []
        for h in sorted(ho + ht, key=lambda x: x.get('ts', '') if isinstance(x, dict) else ''):
            k = keyf(h)
            if k not in seenu:
                seenu.add(k); merged.append(h)
        jt['history'] = merged
        w(p, json.dumps(jt, ensure_ascii=False, indent=1).encode('utf-8') + b'\n')
        unions.append((p, 'audit history union %d+%d->%d' % (len(ho), len(ht), len(merged))))
        print('%s union history %d+%d -> %d' % (p, len(ho), len(ht), len(merged)))
        continue
    if p == 'results/token_usage.json':
        # increment ledger: union daily buckets, per-day take fresher cumulative (they run same day, later run = superset by construction increment)
        jo2, jt2 = jo, jt
        # structure probe: assume dict of day->numbers or {days:{...}}
        mo = dict(jo2); 
        for k, v in jt2.items():
            if isinstance(v, dict) and isinstance(mo.get(k), dict):
                mo[k] = {**mo[k], **v}  # theirs (later run) wins overlapping keys, union the rest
            else:
                mo[k] = v if k in jt2 else mo.get(k)
        for k, v in jt2.items():
            if k not in mo: mo[k] = v
        w(p, json.dumps(mo, ensure_ascii=False, indent=1).encode('utf-8') + b'\n')
        unions.append((p, 'token_usage bucket union'))
        print('%s union buckets=%d' % (p, len(mo)))
        continue
    # default: snapshot M-fresher take-new (deep-ts probe)
    so, st = ts_of(jo), ts_of(jt)
    pick_t = (st is not None and (so is None or st >= so))
    w(p, t if pick_t else o)
    snapshots.append((p, 'take-%s (ours_ts=%s theirs_ts=%s)' % ('theirs' if pick_t else 'ours', so, st)))

for p, note in snapshots:
    print('SNAP %-52s %s' % (p, note))
for p, note in unions:
    print('UNION %-52s %s' % (p, note))
for p, note in unverdict:
    print('!! UNVERDICT %-42s %s' % (p, note))

# conflict-marker sweep (precommit claw parity): staged worktree files must be marker-free
bad = []
for p in uu:
    try:
        txt = io.open(p, 'rb').read()
        if b'<<<<<<<' in txt or b'>>>>>>>' in txt:
            bad.append(p)
    except FileNotFoundError:
        bad.append(p + ' (missing)')
print('MARKER SWEEP:', 'CLEAN' if not bad else bad)
print('RESOLVE DONE; next: git add -A + rebase --continue')
