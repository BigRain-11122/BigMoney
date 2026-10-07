# r803 pool merge resolver: runnable_pool.json per-face max-merge (reland loop law MSG-0612/0640:
# owner_since/cleared_ts newer-wins per entry, NEVER whole-file replay) + attrition ts-duel
import json, subprocess

def stages_of(path):
    out = subprocess.run(['git', 'ls-files', '-u', '--', path], capture_output=True, text=True).stdout
    res = {}
    for line in out.strip().split('\n'):
        if not line.strip():
            continue
        meta, _, fp = line.partition('\t')
        parts = meta.split()
        if len(parts) >= 3:
            res[parts[2]] = parts[1]
    return res

def blob(sha):
    return subprocess.run(['git', 'cat-file', '-p', sha], capture_output=True).stdout

receipt = {'round': 'r803', 'machine': 'bm-b', 'event': 'push-race merge resolve vs bm-c r677', 'faces': {}}

# ---- 1. attrition scan: ts-duel ----
p = 'results/_attrition_guard_scan.json'
st = stages_of(p)
j2 = json.loads(blob(st['2'])); j3 = json.loads(blob(st['3']))
t2 = j2.get('ts') or j2.get('generated') or ''
t3 = j3.get('ts') or j3.get('generated') or ''
side = 3 if (t3 or '') >= (t2 or '') else 2
data = blob(st[str(side)])
open(p, 'wb').write(data)
receipt['faces'][p] = {'recipe': 'ts-duel', 'winner': 'ours' if side == 2 else 'theirs', 'st2_ts': t2, 'st3_ts': t3}

# ---- 2. runnable_pool: per-face max-merge ----
p = 'results/runnable_pool.json'
st = stages_of(p)
j2 = json.loads(blob(st['2'])); j3 = json.loads(blob(st['3']))
e2 = {e['id']: e for e in j2.get('entries', j2.get('pool', []))}
e3 = {e['id']: e for e in j3.get('entries', j3.get('pool', []))}
merged = {}
TSK = ['owner_since', 'cleared_ts', 'updated_at', 'ts', 'claimed_at']
for k in set(e2) | set(e3):
    a, b = e2.get(k), e3.get(k)
    if a is None:
        merged[k] = b; continue
    if b is None:
        merged[k] = a; continue
    ta = max((a.get(x) or '') for x in TSK)
    tb = max((b.get(x) or '') for x in TSK)
    merged[k] = b if tb >= ta else a
    receipt['faces'][p + ':' + k] = {'winner': 'ours' if (ta or '') >= (tb or '') and ta >= tb else 'theirs',
                                     'ours_ts': ta, 'theirs_ts': tb}
KEY = 'entries' if 'entries' in j2 else 'pool'
out = dict(j3 if (j3.get('updated_at') or '') >= (j2.get('updated_at') or '') else j2)
out[KEY] = [merged[k] for k in sorted(merged)]
# byte-shape: preserve CRLF if base had it
crlf = b'\r\n' in blob(st['2'])
txt = json.dumps(out, indent=1, ensure_ascii=False)
if crlf:
    txt = txt.replace('\n', '\r\n')
open(p, 'wb').write(txt.encode('utf-8'))
json.loads(open(p, 'rb').read().decode('utf-8'))
receipt['faces'][p] = {'recipe': 'per-face max-merge', 'ours': len(e2), 'theirs': len(e3), 'merged': len(merged)}

r = subprocess.run(['git', 'add', '--', 'results/runnable_pool.json', 'results/_attrition_guard_scan.json'],
                   capture_output=True, text=True)
assert r.returncode == 0, r.stderr
json.dump(receipt, open('results/_r803bmb_pool_merge_resolve.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
subprocess.run(['git', 'add', 'results/_r803bmb_pool_merge_resolve.json'], capture_output=True)
print('resolved: attrition ->', 'ours' if side == 2 else 'theirs', '| pool merged entries:', len(merged),
      '| per-entry winners:', {k.split(':')[-1]: v['winner'] for k, v in receipt['faces'].items() if ':' in k})
