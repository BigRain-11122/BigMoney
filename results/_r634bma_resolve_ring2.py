# -*- coding: utf-8 -*-
"""r634 bm-a ring-2 resolver (merge origin/main a9bed981c, merge-state):
- results/_attrition_guard_scan.json: snapshot take-new by deep wall-clock ts probe on STAGED blobs;
  merge orientation :2:=ours(local bm-a), :3:=theirs(origin bm-c) (r627 swap law); tie->ours HEAD (r140).
- CODELY.md: memory-union -- base=merge-base blob; prefix identity assertion; new = base + ours-suffix + theirs-suffix;
  byte account len(new)==len(ours)+len(theirs)-len(base); no line dedup (r311).
Receipt appended into results/_r634bma_resolve_receipt.json.
"""
import json, subprocess, sys, re

WALL = re.compile(r'^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}')

def blob(rev, path):
    spec = f'{rev}{path}' if rev.endswith(':') else f'{rev}:{path}'
    r = subprocess.run(['git', 'show', spec], capture_output=True)
    if r.returncode != 0:
        sys.stderr.write(f'blob read fail {spec}: {r.stderr.decode("utf-8","replace")[:200]}\n'); sys.exit(2)
    return r.stdout

def deep_ts(obj, path='', best=None):
    if best is None: best = [None, '']
    if isinstance(obj, dict):
        for k, v in obj.items(): deep_ts(v, f'{path}.{k}', best)
    elif isinstance(obj, list):
        for i, v in enumerate(obj): deep_ts(v, f'{path}[{i}]', best)
    elif isinstance(obj, str) and WALL.match(obj):
        n = obj.replace(' ', 'T')
        if best[0] is None or n > best[0]: best[0], best[1] = n, path
    return best

# --- attrition scan snapshot ---
p = 'results/_attrition_guard_scan.json'
o_ts = deep_ts(json.loads(blob(':2:', p).decode('utf-8')))
t_ts = deep_ts(json.loads(blob(':3:', p).decode('utf-8')))
if o_ts[0] is None and t_ts[0] is None: side, why = 2, 'both no wall-clock -> tie ours (r140)'
elif t_ts[0] is None: side, why = 2, 'theirs no wall-clock'
elif o_ts[0] is None: side, why = 3, 'ours no wall-clock'
elif o_ts[0] >= t_ts[0]: side, why = 2, f'ours {o_ts[0]} >= theirs {t_ts[0]} -> ours (r140 tie canon)'
else: side, why = 3, f'theirs {t_ts[0]} > ours {o_ts[0]}'
chosen = blob(f':{side}:', p)
open(p, 'wb').write(chosen)
json.loads(open(p, 'rb').read().decode('utf-8'))
print(f'[attrition_scan] side={side} ({why}) bytes={len(chosen)}')

# --- CODELY.md memory-union ---
p = 'CODELY.md'
base = blob('0d726090790d4c6d83d2040a7c9cf5fa12b94da7', p)
ours = blob(':2:', p)
theirs = blob(':3:', p)
if not ours.startswith(base):
    print('PREFIX FAIL ours -- entry-level coverage verification required (r327 law); ABORT resolve for manual pass')
    sys.exit(3)
if not theirs.startswith(base):
    print('PREFIX FAIL theirs -- entry-level coverage verification required (r327 law); ABORT resolve for manual pass')
    sys.exit(3)
new = ours + theirs[len(base):]
assert len(new) == len(ours) + len(theirs) - len(base), 'byte account mismatch'
assert b'<<<<<<<' not in new and b'>>>>>>>' not in new, 'conflict marker in union output'
open(p, 'wb').write(new)
print(f'[CODELY.md] memory-union OK: base={len(base)} ours={len(ours)} theirs={len(theirs)} new={len(new)}')

# receipt
rec_path = 'results/_r634bma_resolve_receipt.json'
rec = json.loads(open(rec_path, encoding='utf-8').read())
rec['ring2'] = {'merge': 'origin/main a9bed981c (bm-c r422 closeout)',
                'attrition_scan': {'side': side, 'why': why, 'ours_ts': o_ts, 'theirs_ts': t_ts},
                'codely_memory_union': {'base_bytes': len(base), 'ours_bytes': len(ours),
                                        'theirs_bytes': len(theirs), 'new_bytes': len(new)}}
json.dump(rec, open(rec_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('RING2 RESOLVE OK')
