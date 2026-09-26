# r276 bm-b rebase-2 resolver: autofill_state.json only (bm-a r273 series vs my 0ad827f2).
# Same recipe as _r276bmb_resolve.py (r203/R208/r215/r220/r245/r140). Tie -> ours.
import json, subprocess

def blob(stage, path):
    return subprocess.check_output(['git', 'show', f':{stage}:{path}'])

p = 'results/autofill_state.json'
a, b = blob(2, p), blob(3, p)
ja, jb = json.loads(a.decode('utf-8-sig')), json.loads(b.decode('utf-8-sig'))
out = dict(ja)
by_row = {}
for row in ja.get('launches', []) + jb.get('launches', []):
    by_row[json.dumps(row, sort_keys=True, ensure_ascii=False)] = row
union_desc = sorted(by_row.values(), key=lambda r: r.get('ts', ''), reverse=True)
out['launches'] = sorted(union_desc[:50], key=lambda r: r.get('ts', ''))
ta = (ja.get('last_tick') or {}).get('ts')
tb = (jb.get('last_tick') or {}).get('ts')
if tb and (not ta or tb > ta):
    out['last_tick'] = jb['last_tick']   # strictly newer only; tie falls through to ours (r140)
else:
    out['last_tick'] = ja['last_tick']
assert isinstance(out['last_tick'], dict)
raw1 = blob(1, p)
bom = raw1.startswith(b'\xef\xbb\xbf')
crlf = b'\r\n' in raw1
nl = raw1.endswith(b'\n')
indent = 2 if b'\n  "' in raw1[:400] else 1
s = json.dumps(out, ensure_ascii=False, indent=indent)
if nl:
    s += '\n'
open(p, 'w', encoding='utf-8-sig' if bom else 'utf-8', newline='').write(s)
print(f'union {len(ja["launches"])}+{len(jb["launches"])} -> {len(out["launches"])}; last_tick {ta} vs {tb} -> {out["last_tick"].get("ts")}')
