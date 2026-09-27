"""_r360bmb_resolve_tail -- second replay pass, 4-UU targeted recipes.

daily twins same-side take-new (r98); compute_audit history ts-key union
no-cap + latest take-new (r188/R208); fundamental_b_layer_filter snapshot
take-new (R208/R350). Parse-verify r185.
"""
import json
import subprocess

def blob(stage, path):
    return subprocess.run(['git', 'show', f':{stage}:{path}'],
                           capture_output=True).stdout

def jload(stage, path):
    return json.loads(blob(stage, path).decode('utf-8-sig'))

def probe_ts(d, keys=('ts', 'generated', 'generated_at', 'updated',
                      'updated_at', 'asof')):
    for k in keys:
        if isinstance(d, dict) and k in d:
            return str(d[k])
    return ''

def take_newer(path):
    d2, d3 = jload(2, path), jload(3, path)
    t2, t3 = probe_ts(d2), probe_ts(d3)
    side = 3 if t3 > t2 else 2
    with open(path, 'wb') as fh:
        fh.write(blob(side, path))
    json.loads(open(path, 'rb').read().decode('utf-8-sig'))
    print(f'  {path}: ours={t2!r} theirs={t3!r} -> side {side}')

# daily twins same-side
rj, rm = 'docs/daily_report/REPORT-2026-09-28.json', 'docs/daily_report/REPORT-2026-09-28.md'
d2, d3 = jload(2, rj), jload(3, rj)
side = 3 if probe_ts(d3) > probe_ts(d2) else 2
for p in (rj, rm):
    with open(p, 'wb') as fh:
        fh.write(blob(side, p))
json.loads(open(rj, 'rb').read().decode('utf-8-sig'))
print(f'  daily twins -> side {side} (ours={probe_ts(d2)!r} theirs={probe_ts(d3)!r})')

# compute_audit union
cp = 'results/compute_audit.json'
c2, c3 = jload(2, cp), jload(3, cp)
latest = c2['latest'] if probe_ts(c2['latest']) >= probe_ts(c3['latest']) \
    else c3['latest']
rows = {}
for src in (c2, c3):
    for r in src.get('history', []):
        rows[probe_ts(r) or json.dumps(r, sort_keys=True, default=str)] = r
hist = sorted(rows.values(), key=probe_ts)
raw2 = blob(2, cp)
crlf = b'\r\n' in raw2[:400]
merged = {'latest': latest, 'history': hist}
text = json.dumps(merged, ensure_ascii=False, indent=1) + '\n'
with open(cp, 'wb') as fh:
    fh.write(text.replace('\n', '\r\n' if crlf else '\n').encode('utf-8'))
json.loads(open(cp, 'rb').read().decode('utf-8-sig'))
print(f'  compute_audit: history {len(c2["history"])}U{len(c3["history"])} '
      f'-> {len(hist)} no-cap; latest={probe_ts(latest)!r}')

# fundamental snapshot
take_newer('results/fundamental_b_layer_filter.json')
print('TAIL RESOLUTION COMPLETE')
