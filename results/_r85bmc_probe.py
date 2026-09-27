# -*- coding: utf-8 -*-
"""r85 bm-c S0 re-land probe: a7f66d3b (r84, un-landed, backup origin/machine/bm-c-r84)
replayed onto 6a67f945 (bm-b r328). ours=:2:=HEAD(6a67f945), theirs=:3:=a7f66d3b.
Per r84 pitlaw (SKILL L1 exception: un-landed commit re-land) + r322/r140/R208 laws.
"""
import json, subprocess

def blob(stage_n, path):
    r = subprocess.run(['git', 'show', f':{stage_n}:{path}'],
                       capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout

def deep_ts(obj, path='', out=None):
    """r311/D-09 deep-scan: collect ts-like leaf values at any nesting depth."""
    if out is None:
        out = []
    KEYHINTS = ('ts', 'time', 'generated', 'updated', 'cutoff', 'asof', 'date', 'seen')
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f'{path}.{k}'
            if isinstance(v, (str, int, float)) and any(h in k.lower() for h in KEYHINTS):
                out.append((p, v))
            else:
                deep_ts(v, p, out)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            deep_ts(v, f'{path}[{i}]', out)
    return out

def diff_paths(a, b, path='', out=None, limit=40):
    if out is None:
        out = []
    if len(out) >= limit:
        return out
    if type(a) is not type(b):
        out.append((path, f'type {type(a).__name__}!={type(b).__name__}'))
    elif isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a:
                out.append((f'{path}.{k}', 'ours-missing'))
            elif k not in b:
                out.append((f'{path}.{k}', 'theirs-missing'))
            else:
                diff_paths(a[k], b[k], f'{path}.{k}', out, limit)
    elif isinstance(a, list):
        if len(a) != len(b):
            out.append((f'{path}', f'len {len(a)}!={len(b)}'))
        for i, (x, y) in enumerate(zip(a, b)):
            if len(out) >= limit:
                break
            diff_paths(x, y, f'{path}[{i}]', out, limit)
    elif a != b:
        sa, sb = repr(a), repr(b)
        out.append((path, f'{sa[:60]} != {sb[:60]}'))
    return out

r = subprocess.run(['git', 'status', '--porcelain=v1'], capture_output=True, text=True)
uu = [l[3:] for l in r.stdout.splitlines() if l.startswith('UU ')]
report = {}
for f in uu:
    b1, b2, b3 = blob('1', f), blob('2', f), blob('3', f)
    ent = {'sizes': [len(b2 or b''), len(b3 or b'')], 'identical': b2 == b3}
    if f.endswith('.jsonl'):
        ol = (b2 or b'').decode('utf-8', 'replace').splitlines()
        tl = (b3 or b'').decode('utf-8', 'replace').splitlines()
        ent['lines'] = [len(ol), len(tl)]
        ent['ours_only'] = len(set(ol) - set(tl))
        ent['theirs_only'] = len(set(tl) - set(ol))
    elif f.endswith(('.json', '.js')):
        def parse(bs):
            if bs is None:
                return None
            txt = bs.decode('utf-8', 'replace')
            if f.endswith('.js'):
                txt = txt.strip()
                if txt.startswith('window.DASH_DATA'):
                    txt = txt[len('window.DASH_DATA'):].strip().lstrip('=').rstrip(';').strip()
                try:
                    return json.loads(txt)
                except Exception as e:
                    return f'PARSE-FAIL {e}'
            try:
                return json.loads(txt)
            except Exception as e:
                return f'PARSE-FAIL {e}'
        o, t = parse(b2), parse(b3)
        if isinstance(o, dict) and isinstance(t, dict):
            dps = diff_paths(o, t)
            ent['diff_paths'] = dps[:12]
            ent['ndiff'] = len(dps)
            ots = [v for _, v in deep_ts(o) if isinstance(v, str) and '2026-09-2' in str(v)]
            tts = [v for _, v in deep_ts(t) if isinstance(v, str) and '2026-09-2' in str(v)]
            ent['ts_probe_ours_max'] = max(ots) if ots else None
            ent['ts_probe_theirs_max'] = max(tts) if tts else None
            ent['top_keys'] = sorted(set(o) | set(t))[:14]
        else:
            ent['parse'] = [str(o)[:60], str(t)[:60]]
    elif f.endswith('.md'):
        ent['base_prefix'] = {
            'ours': (b2 or b'').startswith(b1) if b1 is not None else None,
            'theirs': (b3 or b'').startswith(b1) if b1 is not None else None}
        ent['suffix_sizes'] = [len(b2 or b'') - (len(b1) if b1 else 0),
                               len(b3 or b'') - (len(b1) if b1 else 0)]
        ent['crlf'] = [(b2 or b'').count(b'\r\n'), (b3 or b'').count(b'\r\n')]
    report[f] = ent
print(json.dumps({'n_uu': len(uu), 'base_head': subprocess.run(
    ['git', 'log', '--oneline', '-1', 'HEAD'], capture_output=True, text=True).stdout.strip(),
    'report': report}, ensure_ascii=False, indent=1))
