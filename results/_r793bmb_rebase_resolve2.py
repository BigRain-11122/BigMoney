# r793 bm-b rebase resolve2: pick 4/4 churn-absorb vs autofill self-commit, 6 bm-b daemon live faces
# recipes: jsonl append-log -> line union of stage2+stage3(+worktree json lines) zero-loss (r188);
#          json snapshot live face -> newest by deep ts among stage2/stage3/parsable-worktree (R208/r100/R350 live-wins).
import subprocess, json, re

TS_RE = re.compile(r'^20\d{2}-\d{2}-\d{2}[T ]')

def blob(st, path):
    r = subprocess.run(['git', 'show', ':%d:%s' % (st, path)], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError('git show :%d:%s rc=%d' % (st, path, r.returncode))
    return r.stdout

def deep_max_ts(obj, best=''):
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

def try_json(b):
    try:
        return json.loads(b)
    except Exception:
        return None

def wt_bytes(path):
    try:
        return open(path, 'rb').read()
    except Exception:
        return b''

def resolve_jsonl_union(path):
    lines = []
    seen = set()
    for src in (blob(2, path), blob(3, path), wt_bytes(path)):
        for ln in src.decode('utf-8', 'replace').splitlines():
            ln = ln.strip()
            if not ln:
                continue
            if not ln.startswith('{'):  # skip conflict markers / non-json
                continue
            try:
                json.loads(ln)
            except Exception:
                continue
            if ln not in seen:
                seen.add(ln)
                lines.append(ln)
    # sort by embedded ts if present, else keep arrival order
    def ts_of(ln):
        d = try_json(ln.encode())
        if isinstance(d, dict):
            return deep_max_ts(d)
        return ''
    if all(ts_of(l) for l in lines):
        lines.sort(key=ts_of)
    data = ('\n'.join(lines) + '\n').encode('utf-8')
    with open(path, 'wb') as f:
        f.write(data)
    # verify every line parses
    for ln in lines:
        json.loads(ln)
    return {'class': 'append-log-union', 'lines': len(lines)}

def resolve_snapshot_live(path):
    cands = []
    b3 = blob(3, path)
    d3 = try_json(b3)
    cands.append((deep_max_ts(d3) if d3 is not None else '', b3, 'stage3'))
    b2 = blob(2, path)
    d2 = try_json(b2)
    cands.append((deep_max_ts(d2) if d2 is not None else '', b2, 'stage2'))
    wb = wt_bytes(path)
    dw = try_json(wb)
    if dw is not None:
        cands.append((deep_max_ts(dw), wb, 'worktree-live'))
    best_ts, best_b, side = max(cands, key=lambda c: c[0])
    with open(path, 'wb') as f:
        f.write(best_b)
    json.loads(open(path, 'rb').read())  # parse-verify (r185)
    return {'class': 'snapshot-live-wins', 'took': side, 'ts': best_ts}

receipt = {}
receipt['results/fund_divlowvol_p1/nulls.jsonl'] = resolve_jsonl_union('results/fund_divlowvol_p1/nulls.jsonl')
receipt['results/fund_quality_p1/nulls.jsonl'] = resolve_jsonl_union('results/fund_quality_p1/nulls.jsonl')
receipt['results/saturation_engine/history_bm-b.jsonl'] = resolve_jsonl_union('results/saturation_engine/history_bm-b.jsonl')
receipt['results/p1d_gates.json'] = resolve_snapshot_live('results/p1d_gates.json')
receipt['results/saturation_engine/face_bm-b.json'] = resolve_snapshot_live('results/saturation_engine/face_bm-b.json')
receipt['results/saturation_engine/state_bm-b.json'] = resolve_snapshot_live('results/saturation_engine/state_bm-b.json')

with open('results/_r793bmb_rebase_resolve2.json', 'w') as f:
    json.dump(receipt, f, indent=1, ensure_ascii=False)
print('RESOLVED2', len(receipt), 'faces')
for k, v in receipt.items():
    print(' ', k, '->', v['class'], v.get('took', 'lines=%s' % v.get('lines')))
