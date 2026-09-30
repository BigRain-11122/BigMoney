import subprocess, json

def stage(n):
    b = subprocess.check_output(['git', 'show', ':%d:results/crash_fuse.json' % n])
    return json.loads(b.decode('utf-8'))

a = stage(2)  # ours = replayed runtime-sync blob (46-row version)
b = stage(3)  # theirs = origin newer (bm-a fire-fighting rows)
print('stage2 sigs', len(a.get('sigs', {})), 'cleared', len(a.get('cleared', {})))
print('stage3 sigs', len(b.get('sigs', {})), 'cleared', len(b.get('cleared', {})))
ka, kb = set(a.get('sigs', {})), set(b.get('sigs', {}))
print('sigs only-in-2:', len(ka - kb), '| only-in-3:', len(kb - ka), '| common:', len(ka & kb))
ca, cb = set(a.get('cleared', {})), set(b.get('cleared', {}))
print('cleared only-in-2:', len(ca - cb), '| only-in-3:', len(cb - ca), '| common:', len(ca & cb))
for k in sorted(ka & kb):
    ra, rb = a['sigs'][k], b['sigs'][k]
    if ra != rb:
        print('DIFF sig', k[:60], '| 2:', json.dumps({x: ra[x] for x in ('count', 'refusals', 'last_crash_ts', 'last_refusal_ts', 'code_sha256')}, ensure_ascii=False)[:150])
        print('              | 3:', json.dumps({x: rb[x] for x in ('count', 'refusals', 'last_crash_ts', 'last_refusal_ts', 'code_sha256')}, ensure_ascii=False)[:150])
for k in sorted(ca & cb):
    if a['cleared'][k] != b['cleared'][k]:
        print('DIFF cleared', k[:60], '| 2 ts', a['cleared'][k].get('cleared_ts'), '| 3 ts', b['cleared'][k].get('cleared_ts'))
print('other keys 2:', [k for k in a if k not in ('sigs', 'cleared')])
print('other keys 3:', [k for k in b if k not in ('sigs', 'cleared')])
