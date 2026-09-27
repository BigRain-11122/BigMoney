r"""r344 bm-b fold driver — ATOMIC redo per r335 pitlaw canonical:
dynamic-sides canonical rebuild + atomic add-continue-push + post-window
reflog adjudication. One process, no command gaps for the tick to race.

Sides in REBASE are flipped: ours(:2:) = origin/main, theirs(:3:) = replayed
bm-b commit. Recipes per SKILL.md classification table (bigmoney-conflict-resolve).
"""
import subprocess, json, os, sys, time

def run(args, check=True):
    r = subprocess.run(args, capture_output=True)
    if check and r.returncode != 0:
        raise RuntimeError(f'{args}: {r.stderr.decode("utf-8", "replace")[:300]}')
    return r.stdout

def git(*a, check=False):
    r = subprocess.run(['git', *a], capture_output=True)
    out = (r.stdout + r.stderr).decode('utf-8', 'replace')
    return r.returncode, out

def stages():
    rc, out = git('ls-files', '-u')
    m = {}
    for line in out.strip().splitlines():
        if '\t' not in line:
            continue
        meta, path = line.split('\t')
        mode, sha, st = meta.split()
        m.setdefault(path, {})[int(st)] = sha
    return m

def cat(sha):
    return run(['git', 'cat-file', '-p', sha])

def detect(b):
    crlf = b'\r\n' in b[:2000]
    indent = 1
    for ln in b.split(b'\n')[1:6]:
        s = ln.lstrip(b'\r')
        if s.startswith(b'}') or s.startswith(b']'):
            continue
        stripped = len(s) - len(s.lstrip(b' '))
        if stripped > 0:
            indent = stripped
            break
    return crlf, indent

def dump(d, crlf, indent):
    s = json.dumps(d, ensure_ascii=False, indent=indent)
    if crlf:
        s = s.replace('\n', '\r\n')
    return (s + ('\r\n' if crlf else '\n')).encode('utf-8')

def rowkey(r):
    return json.dumps(r, sort_keys=True, ensure_ascii=False)

def take_side(p, s, side):
    b = cat(s[side])
    with open(p, 'wb') as f:
        f.write(b)
    return f'{p}: take :{side} whole (other-machine single-writer / authoritative side)'

def take_newer_json(p, s, ts_key):
    b2, b3 = cat(s[2]), cat(s[3])
    d2, d3 = json.loads(b2.decode('utf-8')), json.loads(b3.decode('utf-8'))
    crlf, indent = detect(b2 if b2 else b3)
    t2, t3 = str(d2.get(ts_key, '')), str(d3.get(ts_key, ''))
    win = 2 if t2 >= t3 else 3  # tie -> ours(:2: = origin/HEAD base) r140
    d = d2 if win == 2 else d3
    with open(p, 'wb') as f:
        f.write(dump(d, crlf, indent))
    return f'{p}: take-new({ts_key} {t2} vs {t3}) -> :{win}'

def take_round_newer(p, s):
    b2, b3 = cat(s[2]), cat(s[3])
    d2, d3 = json.loads(b2.decode('utf-8')), json.loads(b3.decode('utf-8'))
    crlf, indent = detect(b2 if b2 else b3)
    r2, r3 = d2.get('round_no', 0), d3.get('round_no', 0)
    win = 2 if r2 >= r3 else 3  # tie -> ours r140
    d = d2 if win == 2 else d3
    with open(p, 'wb') as f:
        f.write(dump(d, crlf, indent))
    return f'{p}: single-writer round_no {r2} vs {r3} -> :{win}'

def resolve_json_ledger(p, s):
    b2, b3 = cat(s[2]), cat(s[3])
    d2, d3 = json.loads(b2.decode('utf-8')), json.loads(b3.decode('utf-8'))
    crlf, indent = detect(b2 if b2 else b3)
    out = {}
    notes = []
    ledger_keys = {'history', 'launches', 'transitions', 'snapshots', 'entries', 'trials'}
    for k in sorted(set(d2) | set(d3)):
        v2, v3 = d2.get(k), d3.get(k)
        if isinstance(v2, list) and isinstance(v3, list) and (k in ledger_keys or (v2 and v3 and isinstance(v2[0], dict))):
            seen, union = set(), []
            for r in v3 + v2:
                key = rowkey(r)
                if key not in seen:
                    seen.add(key)
                    union.append(r)
            out[k] = union
            notes.append(f'{k}:{len(v2)}+{len(v3)}->uniq{len(union)}')
        elif isinstance(v2, dict) and isinstance(v3, dict):
            out[k] = {**v3, **v2}
        else:
            out[k] = v2 if v2 is not None else v3
    with open(p, 'wb') as f:
        f.write(dump(out, crlf, indent))
    return f'{p}: ledger-union [{", ".join(notes)}]'

def resolve_autofill(p, s):
    b2, b3 = cat(s[2]), cat(s[3])
    d2, d3 = json.loads(b2.decode('utf-8')), json.loads(b3.decode('utf-8'))
    crlf, indent = detect(b2 if b2 else b3)
    seen, union = set(), []
    for r in d3.get('launches', []) + d2.get('launches', []):
        key = rowkey(r)
        if key not in seen:
            seen.add(key)
            union.append(r)
    uniq = len(union)
    union.sort(key=lambda r: str(r.get('ts', '')), reverse=True)
    union = union[:50]
    union.sort(key=lambda r: str(r.get('ts', '')))  # r245 write-back ascending
    out = dict(d2)
    out['launches'] = union
    lt2, lt3 = d2.get('last_tick'), d3.get('last_tick')
    if isinstance(lt2, dict) and isinstance(lt3, dict):
        out['last_tick'] = lt2 if str(lt2.get('ts', '')) >= str(lt3.get('ts', '')) else lt3
    else:
        out['last_tick'] = lt2 if isinstance(lt2, dict) else lt3
    assert isinstance(out['last_tick'], dict)
    with open(p, 'wb') as f:
        f.write(dump(out, crlf, indent))
    return f'{p}: autofill launches uniq={uniq}->kept{len(union)} last_tick.ts={out["last_tick"].get("ts")}'

def resolve_md(p, s, sort_lines=True):
    b2, b3 = cat(s[2]), cat(s[3])
    t2 = b2.decode('utf-8', 'replace').splitlines()
    t3 = b3.decode('utf-8', 'replace').splitlines()
    common = 0
    for a, b in zip(t2, t3):
        if a == b:
            common += 1
        else:
            break
    tail2, tail3 = t2[common:], t3[common:]
    union, seen = [], set()
    for ln in tail2 + tail3:
        if ln not in seen and ln.strip():
            seen.add(ln)
            union.append(ln)
    if sort_lines:
        union.sort()  # ts-prefixed ledger lines sort chronologically
    out = t2[:common] + union
    crlf = b'\r\n' in b2[:4000] or b'\r\n' in b3[:4000]
    text = '\n'.join(out) + '\n'
    if crlf:
        text = text.replace('\n', '\r\n')
    with open(p, 'wb') as f:
        f.write(text.encode('utf-8'))
    return f'{p}: md-union prefix={common} tails {len(tail2)}+{len(tail3)} -> +{len(union)}'

def resolve_jsonl_union(p, s):
    b2, b3 = cat(s[2]), cat(s[3])
    l2 = b2.decode('utf-8', 'replace').splitlines()
    l3 = b3.decode('utf-8', 'replace').splitlines()
    seen = set(l2)
    extra = [l for l in l3 if l not in seen and l.strip()]
    out = l2 + extra
    crlf = b'\r\n' in b2[:4000]
    text = '\n'.join(out) + '\n'
    if crlf:
        text = text.replace('\n', '\r\n')
    with open(p, 'wb') as f:
        f.write(text.encode('utf-8'))
    return f'{p}: jsonl line-union ours={len(l2)} theirs-unique=+{len(extra)}'

def resolve_one(p, s):
    if p == 'results/autofill_state.json':
        return resolve_autofill(p, s)
    if p.endswith('.jsonl'):
        return resolve_jsonl_union(p, s)
    if p == 'CODELY.md':
        return resolve_md(p, s, sort_lines=False)  # memory-union, order-preserving
    if p == 'results/runnable_pool.json':
        return take_newer_json(p, s, 'updated_at')
    if p == 'results/astock_daily_update_status.json':
        return take_newer_json(p, s, 'ts')
    if p in ('results/compute_audit.json', 'results/regime_state.json'):
        return resolve_json_ledger(p, s)
    if p in ('fleet/machines/bm-b.json', 'logs/iteration-loop/state.json'):
        return take_round_newer(p, s)
    # other machines' single-writer faces: never rewrite theirs -> origin side
    if p.startswith('fleet/machines/') and p != 'fleet/machines/bm-b.json':
        return take_side(p, s, 2)
    if os.path.basename(p).startswith('state-bm-') and p != 'logs/iteration-loop/state.json':
        return take_side(p, s, 2)
    if p.endswith('.md'):
        return resolve_md(p, s, sort_lines=True)
    # generic json: ledger-ish keys -> union; ts face -> take-new; else :2:
    b2, b3 = cat(s[2]), cat(s[3])
    try:
        d2, d3 = json.loads(b2.decode('utf-8')), json.loads(b3.decode('utf-8'))
    except Exception:
        return take_side(p, s, 2)
    if isinstance(d2, dict) and isinstance(d3, dict):
        lk = {'history', 'launches', 'transitions', 'snapshots', 'entries'}
        if any(k in d2 and k in d3 for k in lk):
            return resolve_json_ledger(p, s)
        if 'ts' in d2 or 'updated_at' in d2:
            return take_newer_json(p, s, 'ts' if 'ts' in d2 else 'updated_at')
    return take_side(p, s, 2)

def resolve_stop():
    st = stages()
    if not st:
        return True
    notes = []
    for p in sorted(st):
        notes.append(resolve_one(p, st[p]))
    # validate all resolved before add (r185)
    for p in st:
        if p.endswith('.json'):
            json.loads(open(p, 'rb').read().decode('utf-8', 'replace'))
        raw = open(p, 'rb').read()
        blob_has_hist = any(mk in cat(st[p][s]) for mk in (b'<<<<<<<', b'>>>>>>>') for s in (2, 3) if s in st[p])
        if not blob_has_hist:
            assert b'<<<<<<<' not in raw and b'>>>>>>>' not in raw, f'markers left in {p}'
    for p in st:
        run(['git', 'add', p])
    for n in notes:
        print('RESOLVED |', n, flush=True)
    return False

def rebase_active():
    return os.path.exists('.git/rebase-merge') or os.path.exists('.git/rebase-apply')

TICK_OWNED = ('results/autofill_state.json', 'results/runnable_pool.json',
              'results/p1d_gates.json', 'results/crash_fuse.json')

def ride_tick_dirt():
    """r290 self-commit law: tick-owned unstaged dirt rides into the replay
    commit instead of blocking continue (r201 misleading-message pitlaw)."""
    rc, out = git('diff', '--name-only')
    added = []
    for ln in out.strip().splitlines():
        if ln.strip() in TICK_OWNED:
            run(['git', 'add', ln.strip()])
            added.append(ln.strip())
    if added:
        print('RIDE_TICK_DIRT:', added, flush=True)

def main():
    t0 = time.time()
    if rebase_active():
        print('RESUME: rebase already in flight', flush=True)
    else:
        rc, out = git('fetch', 'origin')
        print('fetch rc=', rc, flush=True)
        rc, out = git('rebase', 'origin/main')
        print('rebase start rc=', rc, out.strip().splitlines()[-1] if out.strip() else '', flush=True)
    spins = 0
    for i in range(40):
        if not rebase_active():
            print('REBASE_COMPLETE', flush=True)
            break
        st = stages()
        if st:
            resolve_stop()
        ride_tick_dirt()
        rc, out = git('-c', 'core.editor=true', 'rebase', '--continue')
        tail = out.strip().splitlines()[-1] if out.strip() else ''
        print(f'continue#{i} rc={rc} {tail[:160]}', flush=True)
        if rc != 0:
            if 'nothing to commit' in out or 'now empty' in out:
                git('rebase', '--skip')
            elif 'Could not apply' in out or 'Merge conflict' in out:
                pass  # normal conflict stop, loop resolves it
            elif 'You must edit all merge conflicts' in out:
                spins += 1
                if spins >= 2:
                    print('FULL_CONTINUE_OUTPUT:', out[-800:], flush=True)
                    return 2
            else:
                print('FULL_CONTINUE_OUTPUT:', out[-800:], flush=True)
                return 2
        else:
            spins = 0
    else:
        print('LOOP_EXHAUSTED', flush=True)
        return 1
    rc, out = git('status', '--porcelain=v1')
    print('STATUS_AFTER:', out.strip()[:400], flush=True)
    rc, out = git('log', '--oneline', '-8')
    print('LOG_TAIL:\n', out, flush=True)
    # atomic push immediately (still inside driver process)
    rc, out = git('push', 'origin', 'main')
    print('PUSH rc=', rc, out.strip().splitlines()[-1][:200] if out.strip() else '', flush=True)
    if rc != 0:
        print('PUSH_REJECTED — will handle at S7 face', flush=True)
    print(f'DRIVER_DONE in {time.time()-t0:.1f}s', flush=True)
    return 0

if __name__ == '__main__':
    sys.exit(main())
