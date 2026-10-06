# r792 bm-b S0 rebase conflict resolver (skill bigmoney-conflict-resolve recipes)
# stage2 = origin/main tip side ("ours" during rebase), stage3 = replayed bm-b commit side ("theirs")
# recipes: snapshot -> take-new whole side bytes by deep ts probe (R208/r100/R350);
#          rolling-ledger -> union ledger key by in-entry ts (zero loss, r319), state fields take-new (r188/R208);
#          EOL mirror local producer side (r223/r234).
import subprocess, json, re, sys

TS_RE = re.compile(r'^20\d{2}-\d{2}-\d{2}[T ]')

def blob(st, path):
    r = subprocess.run(['git', 'show', ':%d:%s' % (st, path)], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError('git show :%d:%s rc=%d %r' % (st, path, r.returncode, r.stderr[:200]))
    return r.stdout

def deep_max_ts(obj, best=''):
    # R350: deep-scan nested layers, no key-exclude lists; wall-clock values need date prefix
    if isinstance(obj, dict):
        for v in obj.values():
            best = deep_max_ts(v, best)
    elif isinstance(obj, list):
        for v in obj:
            best = deep_max_ts(v, best)
    elif isinstance(obj, str) and TS_RE.match(obj):
        if obj > best:
            best = obj
    return best

def resolve_snapshot(path):
    b2, b3 = blob(2, path), blob(3, path)
    t2, t3 = deep_max_ts(json.loads(b2)), deep_max_ts(json.loads(b3))
    winner = b3 if t3 > t2 else b2  # same-second tie -> stage2 origin side (r140 HEAD analog)
    side = 'stage3-mine' if t3 > t2 else ('stage2-origin' if t2 > t3 else 'tie-origin')
    with open(path, 'wb') as f:
        f.write(winner)
    json.loads(open(path, 'rb').read())  # parse-verify before add (r185)
    return {'class': 'snapshot', 'ts2': t2, 'ts3': t3, 'took': side}

def resolve_rolling(path, ledger_keys, key='ts'):
    b2, b3 = blob(2, path), blob(3, path)
    d2, d3 = json.loads(b2), json.loads(b3)
    eol = '\r\n' if b'\r\n' in b3 else '\n'  # mirror local producer side (stage3 = bm-b face)
    m = re.match(br'\{\n( +)"', b3)
    indent = len(m.group(1)) if m else 2
    out = dict(d3)  # start from mine (state fields corrected below)
    for k in ledger_keys:
        l2 = {e[key]: e for e in d2.get(k, [])}
        l3 = {e[key]: e for e in d3.get(k, [])}
        merged = dict(l2)
        merged.update(l3)  # same-ts collision -> mine (live daemon face wins locally)
        out[k] = [merged[t] for t in sorted(merged.keys())]
        assert len(out[k]) == len(set(l2.keys()) | set(l3.keys())), 'union zero-loss failed %s.%s' % (path, k)
    # state fields: take-new side overall by ts probe
    t2, t3 = deep_max_ts(d2), deep_max_ts(d3)
    if t2 > t3:
        for k, v in d2.items():
            if k not in ledger_keys:
                out[k] = v
    txt = json.dumps(out, indent=indent, ensure_ascii=False)
    data = txt.replace('\n', eol).encode('utf-8')
    if not data.endswith(eol.encode('latin-1')):
        pass
    with open(path, 'wb') as f:
        f.write(data)
    json.loads(open(path, 'rb').read())  # parse-verify (r185)
    return {'class': 'rolling-ledger', 'ts2': t2, 'ts3': t3, 'ledgers': ledger_keys,
            'union_sizes': {k: len(out[k]) for k in ledger_keys}}

receipt = {}
receipt['results/_attrition_guard_scan.json'] = resolve_snapshot('results/_attrition_guard_scan.json')
receipt['results/compute_audit.json'] = resolve_rolling('results/compute_audit.json', ['history'])
receipt['results/futures_update_status.json'] = resolve_snapshot('results/futures_update_status.json')
receipt['results/lhb_update_status.json'] = resolve_snapshot('results/lhb_update_status.json')
receipt['results/regime_state.json'] = resolve_rolling('results/regime_state.json', ['transitions', 'history'], key='asof')
receipt['results/update_status.json'] = resolve_snapshot('results/update_status.json')
with open('results/_r792bmb_rebase_resolve.json', 'w') as f:
    json.dump(receipt, f, indent=1, ensure_ascii=False)
print('RESOLVED', len(receipt), 'faces')
for k, v in receipt.items():
    print(' ', k, '->', v['class'], 'took', v.get('took', v.get('ledgers', '')))
