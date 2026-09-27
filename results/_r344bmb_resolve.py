r"""r344 bm-b fold resolver — canonical recipes per SKILL.md (bigmoney-conflict-resolve).

Sides in REBASE are flipped: ours(:2:) = origin/main side, theirs(:3:) = replayed
bm-b commit. Recipes applied per file class; zero-loss union ledgers, take-new
snapshots, single-writer faces converge to newest own-machine content.
Reusable at every rebase stop. Stages read via `git ls-files -u` + `git cat-file -p`.
"""
import subprocess, json, sys

def run(args):
    r = subprocess.run(args, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f'{args}: {r.stderr.decode("utf-8", "replace")[:200]}')
    return r.stdout

def stages():
    out = run(['git', 'ls-files', '-u']).decode('utf-8')
    m = {}
    for line in out.strip().splitlines():
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

def resolve_json_ledger(p, s):
    b2, b3 = cat(s[2]), cat(s[3])
    d2, d3 = json.loads(b2.decode('utf-8')), json.loads(b3.decode('utf-8'))
    crlf, indent = detect(b2)
    out = {}
    ledger_keys = {'history', 'launches', 'transitions', 'snapshots'}
    for k in set(d2) | set(d3):
        v2, v3 = d2.get(k), d3.get(k)
        if isinstance(v2, list) and isinstance(v3, list) and (k in ledger_keys or all(isinstance(x, dict) for x in v2 + v3[:1])):
            seen, union = set(), []
            for r in v3 + v2:  # theirs first (replay side rows preserved first on tie)
                key = rowkey(r)
                if key not in seen:
                    seen.add(key)
                    union.append(r)
            out[k] = union
        elif isinstance(v2, dict) and isinstance(v3, dict):
            out[k] = {**v3, **v2}  # ours(origin) top wins on scalar tie
        else:
            out[k] = v2 if v2 is not None else v3
    return dump(out, crlf, indent), (p, 'ledger-union')

def take_newer_json(p, s, ts_key):
    b2, b3 = cat(s[2]), cat(s[3])
    d2, d3 = json.loads(b2.decode('utf-8')), json.loads(b3.decode('utf-8'))
    crlf, indent = detect(b2 if b2 else b3)
    t2, t3 = str(d2.get(ts_key, '')), str(d3.get(ts_key, ''))
    win = 2 if t2 >= t3 else 3  # tie -> ours (r140)
    d = d2 if win == 2 else d3
    return dump(d, crlf, indent), (p, f'take-new({ts_key})->:{win}: ours' if win == 2 else f'take-new({ts_key})->:{win}: theirs')

def resolve_autofill(p, s):
    b2, b3 = cat(s[2]), cat(s[3])
    d2, d3 = json.loads(b2.decode('utf-8')), json.loads(b3.decode('utf-8'))
    crlf, indent = detect(b2 if b2 else b3)
    # launches: union -> sort ts desc -> cap 50 -> write back re-sorted ASC (r245)
    seen, union = set(), []
    for r in d3.get('launches', []) + d2.get('launches', []):
        key = rowkey(r)
        if key not in seen:
            seen.add(key)
            union.append(r)
    union.sort(key=lambda r: str(r.get('ts', '')), reverse=True)
    union = union[:50]
    union.sort(key=lambda r: str(r.get('ts', '')))  # write-back ascending (r245)
    out = dict(d2)
    out['launches'] = union
    lt2, lt3 = d2.get('last_tick'), d3.get('last_tick')
    if isinstance(lt2, dict) and isinstance(lt3, dict):
        out['last_tick'] = lt2 if str(lt2.get('ts', '')) >= str(lt3.get('ts', '')) else lt3
    else:
        out['last_tick'] = lt2 if isinstance(lt2, dict) else lt3
    assert isinstance(out['last_tick'], dict), 'last_tick must be dict'
    body = dump(out, crlf, indent)
    # zero-loss check
    n2, n3 = len(d2.get('launches', [])), len(d3.get('launches', []))
    uniq = len({rowkey(r) for r in d2.get('launches', []) + d3.get('launches', [])})
    return body, (p, f'autofill: launches {n2}+{n3} uniq={uniq} -> kept={len(union)} (cap50), last_tick.ts={out["last_tick"].get("ts")}')

def take_round_newer(p, s):
    b2, b3 = cat(s[2]), cat(s[3])
    d2, d3 = json.loads(b2.decode('utf-8')), json.loads(b3.decode('utf-8'))
    crlf, indent = detect(b2 if b2 else b3)
    r2, r3 = d2.get('round_no', 0), d3.get('round_no', 0)
    win = 2 if r2 >= r3 else 3  # tie -> ours/HEAD (r140)
    d = d2 if win == 2 else d3
    return dump(d, crlf, indent), (p, f'single-writer round_no {r2}vs{r3} -> :{win}')

def resolve_md(p, s):
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
    for ln in tail3 + tail2:
        if ln not in seen and ln.strip():
            seen.add(ln)
            union.append(ln)
    union.sort()  # ts-prefix lines sort = chronological
    out = t2[:common] + union
    crlf = b'\r\n' in b2[:4000] or b'\r\n' in b3[:4000]
    text = '\n'.join(out) + '\n'
    if crlf:
        text = text.replace('\n', '\r\n')
    return text.encode('utf-8'), (p, f'md-union: prefix={common} tails {len(tail2)}+{len(tail3)} -> +{len(union)} lines (dedup by line)')

def main():
    st = stages()
    plan = []
    for p in sorted(st):
        if p == 'results/autofill_state.json':
            plan.append(resolve_autofill(p, st[p]))
        elif p == 'logs/iteration-loop/round_reports.md':
            plan.append(resolve_md(p, st[p]))
        elif p in ('results/compute_audit.json', 'results/regime_state.json'):
            plan.append(resolve_json_ledger(p, st[p]))
        elif p in ('results/astock_daily_update_status.json',):
            plan.append(take_newer_json(p, st[p], 'ts'))
        elif p == 'results/runnable_pool.json':
            plan.append(take_newer_json(p, st[p], 'updated_at'))
        elif p in ('fleet/machines/bm-b.json', 'logs/iteration-loop/state.json'):
            plan.append(take_round_newer(p, st[p]))
        else:
            print('UNHANDLED', p, '- skipping, resolve manually')
            return 1
    for body, note in plan:
        path = note[0]
        with open(path, 'wb') as f:
            f.write(body)
        json.loads(open(path, 'rb').read().decode('utf-8', 'replace') if not path.endswith('.md') else '{}')
        print('RESOLVED |', note)
    for body, note in plan:
        run(['git', 'add', note[0]])
    print('ALL_ADDED')
    return 0

if __name__ == '__main__':
    sys.exit(main())
