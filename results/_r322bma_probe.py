# -*- coding: utf-8 -*-
"""r322 bm-a S0 rebase-collision probe: per-UU-file stage2(origin)/stage3(replayed) blob facts.
Deep-scan ts + leaf-diff summary per D-20260927-09 (top-level miss != no ts).
"""
import json, subprocess, sys

def blob(stage, path):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout

TS_KEYS = ('ts', 'generated', 'updated', 'generated_at', 'last_run', 'asof', 'date',
           'datetime', 'time', 'epoch_utc', 'heartbeat_epoch_utc', 'last_seen', 'cutoff',
           'last_tick_ts', 'checked_at', 'run_at', 'timestamp')

def deep_ts(obj, path=''):
    """recursive scan for ts-like keys -> list of (path, value)"""
    found = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f'{path}.{k}' if path else k
            if isinstance(v, (str, int, float)) and any(t in k.lower() for t in TS_KEYS):
                found.append((p, v))
            found.extend(deep_ts(v, p))
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:3]):  # sample first entries only
            found.extend(deep_ts(v, f'{path}[{i}]'))
    return found

def leaf_diff(a, b, path=''):
    """structural leaf-level diff summary (recursive); returns list of diff notes"""
    out = []
    if type(a) != type(b):
        return [f'{path or "<root>"}: type {type(a).__name__}!={type(b).__name__}']
    if isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            p = f'{path}.{k}' if path else k
            if k not in a: out.append(f'{p}: only-in-OURS(origin)')
            elif k not in b: out.append(f'{p}: only-in-THEIRS(r321)')
            else: out.extend(leaf_diff(a[k], b[k], p))
    elif isinstance(a, list):
        if len(a) != len(b):
            out.append(f'{path}: len {len(a)}(origin) vs {len(b)}(r321)')
        for i in range(min(len(a), len(b))):
            out.extend(leaf_diff(a[i], b[i], f'{path}[{i}]'))
    else:
        if a != b:
            sa, sb = repr(a), repr(b)
            out.append(f'{path}: {sa[:60]} != {sb[:60]}')
    return out

uu = [l[3:].strip() for l in subprocess.run(['git', 'status', '--porcelain'],
        capture_output=True, text=True, encoding='utf-8', errors='replace').stdout.splitlines()
        if l.startswith('UU ')]

report = {}
for path in uu:
    b2, b3 = blob(2, path), blob(3, path)
    ent = {'sizes': [len(b2 or b''), len(b3 or b'')]}
    if b2 is None or b3 is None:
        ent['error'] = 'blob missing'
        report[path] = ent
        continue
    # bytes identical?
    ent['identical'] = (b2 == b3)
    if path.endswith(('.json', '.js')):
        try:
            j2 = json.loads(b2.decode('utf-8-sig', errors='replace'))
            j3 = json.loads(b3.decode('utf-8-sig', errors='replace'))
            ent['ts_origin'] = deep_ts(j2)[:6]
            ent['ts_r321'] = deep_ts(j3)[:6]
            diffs = leaf_diff(j2, j3)
            ent['diff_count'] = len(diffs)
            ent['diffs_head'] = diffs[:12]
        except Exception as e:
            ent['parse_error'] = repr(e)[:120]
    elif path.endswith('.jsonl'):
        l2 = [l for l in b2.decode('utf-8', errors='replace').splitlines() if l.strip()]
        l3 = [l for l in b3.decode('utf-8', errors='replace').splitlines() if l.strip()]
        ent['lines_origin'] = len(l2); ent['lines_r321'] = len(l3)
        ent['lines_union'] = len(set(l2) | set(l3))
        ent['only_origin'] = len(set(l2) - set(l3)); ent['only_r321'] = len(set(l3) - set(l2))
    else:  # .md
        t2 = b2.decode('utf-8', errors='replace'); t3 = b3.decode('utf-8', errors='replace')
        ent['md_equal'] = (t2 == t3)
        if t2 != t3:
            import difflib
            d = [l for l in difflib.unified_diff(t3.splitlines(), t2.splitlines(), 'r321', 'origin', lineterm='')][:16]
            ent['md_diff_head'] = d
    report[path] = ent

with open('results/_r322bma_probe_out.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=1, default=str)
print('OK -> results/_r322bma_probe_out.json', len(report))
