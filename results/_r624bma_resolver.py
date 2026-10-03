# r624 bm-a rebase conflict resolver (canonical recipes: jsonl union / json+md ts-diffpick)
import io, json, re, sys, os, subprocess

def sides(path):
    t = io.open(path, encoding='utf-8', errors='replace').read()
    if '<<<<<<<' not in t:
        return None
    # split into conflict hunks; common (non-conflict) text kept once
    pat = re.compile(r'<<<<<<< [^\n]*\n(.*?)\n?=======\n(.*?)\n?>>>>>>> [^\n]*\n', re.S)
    return t, pat

def resolve_jsonl(path):
    """union by line: common text + both sides, dedup full-line identical (deterministic twins)"""
    t, pat = sides(path)
    out = []
    lastend = 0
    rows_ours, rows_theirs = [], []
    for m in pat.finditer(t):
        out.append(t[lastend:m.start()])
        a = [l for l in m.group(1).splitlines() if l.strip()]
        b = [l for l in m.group(2).splitlines() if l.strip()]
        seen = set(a)
        for l in b:
            if l not in seen:
                a.append(l)
        out.extend(a)
        lastend = m.end()
    out.append(t[lastend:])
    merged = ''.join(out)
    # final safety: whole-file line dedup preserving order (r294: dedup domain=full-line identity only)
    lines = merged.splitlines()
    seen, final = set(), []
    for l in lines:
        if l in seen:
            continue
        seen.add(l)
        final.append(l)
    io.open(path, 'w', encoding='utf-8', newline='\n').write('\n'.join(final) + ('\n' if final else ''))
    return 'union'

def ts_of(obj):
    """extract best-effort embedded wall-clock from json obj/dict or md text"""
    if isinstance(obj, dict):
        for k in ('generated', 'generated_at', 'written_at', 'updated', 'updated_at', 'asof', 'ts', 'timestamp', 'now', 'now_utc', 'elapsed'):
            v = obj.get(k)
            if isinstance(v, (int, float)) and v > 1_700_000_000:
                return v
            if isinstance(v, str) and re.match(r'2026-\d\d-\d\d', v):
                return v
        for v in obj.values():
            r = ts_of(v)
            if r:
                return r
    return None

def resolve_json(path):
    t, pat = sides(path)
    out = []
    lastend = 0
    mode = 'ours'
    for m in pat.finditer(t):
        out.append(t[lastend:m.start()])
        try:
            jo = json.loads(m.group(1))
            jt = json.loads(m.group(2))
            to, tt = ts_of(jo), ts_of(jt)
            if to is not None and tt is not None and str(tt) > str(to):
                mode = 'theirs-partial'
                out.append(m.group(2))
            else:
                out.append(m.group(1))
        except Exception:
            # unparseable side: keep ours (adopted newer local products, r623 12:52)
            out.append(m.group(1))
        lastend = m.end()
    out.append(t[lastend:])
    io.open(path, 'w', encoding='utf-8', newline='\n').write(''.join(out))
    return mode

def resolve_md(path):
    t, pat = sides(path)
    out = []
    lastend = 0
    for m in pat.finditer(t):
        out.append(t[lastend:m.start()])
        to = re.findall(r'2026-\d\d-\d\d[T ]\d\d:\d\d(?::\d\d)?', m.group(1))
        tt = re.findall(r'2026-\d\d-\d\d[T ]\d\d:\d\d(?::\d\d)?', m.group(2))
        if to and tt and tt[-1] > to[-1]:
            out.append(m.group(2))
        else:
            out.append(m.group(1))
        lastend = m.end()
    out.append(t[lastend:])
    io.open(path, 'w', encoding='utf-8', newline='\n').write(''.join(out))
    return 'ts-diffpick'

files = subprocess.run(['git', 'diff', '--name-only', '--diff-filter=U'],
                       capture_output=True, text=True, encoding='utf-8').stdout.split()
summary = {}
for f in files:
    f = f.strip()
    if not f:
        continue
    if f.endswith('.jsonl'):
        r = resolve_jsonl(f)
    elif f.endswith('.json'):
        r = resolve_json(f)
    elif f.endswith('.md') or f.endswith('.js'):
        r = resolve_md(f)
    else:
        r = 'UNHANDLED:' + f
    summary[f] = r
    if not r.startswith('UNHANDLED'):
        subprocess.run(['git', 'add', f], capture_output=True)
for k, v in sorted(summary.items()):
    print(v, '|', k)
# verify no markers remain anywhere
bad = []
for f in summary:
    if os.path.exists(f) and '<<<<<<<' in io.open(f, encoding='utf-8', errors='replace').read():
        bad.append(f)
print('REMAINING-MARKERS:', bad if bad else 'NONE')
