# r802 bm-b pick-4 (747fb5976 checkpoint replay) conflict resolver - daemon live faces
# r621 law: rolling-window stale-tip divergence -> key-union zero loss; r440 law: own-lane daemon
# snapshots -> ts-duel live-wins (ours 12:00:05 > theirs 11:53:04).
# Faces: nulls.jsonl (union by k, 1723+2=1725), history_bm-b.jsonl (union by epoch, 120+8=128),
# p1d_gates/face/state jsons (take ours raw bytes).
import subprocess, json, sys

def stages_of(path):
    out = subprocess.run(['git','ls-files','-u','--',path],capture_output=True,text=True).stdout
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
    return subprocess.run(['git','cat-file','-p',sha],capture_output=True).stdout

receipt = {'round': 'r802', 'machine': 'bm-b', 'event': 'pick-4 747fb5976 replay resolve', 'faces': {}}

# ---- nulls.jsonl: union by k, shared-row identity assert ----
p = 'results/fund_divlowvol_p1/nulls.jsonl'
st = stages_of(p)
olines = blob(st['2']).decode('utf-8').splitlines()
tlines = blob(st['3']).decode('utf-8').splitlines()
o = {json.loads(l)['k']: l for l in olines}
t = {json.loads(l)['k']: l for l in tlines}
for k in set(o) & set(t):
    assert o[k] == t[k], 'shared row content mismatch k=%d' % k
merged_k = sorted(set(o) | set(t))
out_lines = [o[k] if k in o else t[k] for k in merged_k]
assert len(out_lines) == len(o) + len(set(t) - set(o)), 'union count mismatch'
raw = blob(st['2'])
crlf = b'\r\n' in raw
nl = '\r\n' if crlf else '\n'
with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(nl.join(out_lines) + nl)
receipt['faces'][p] = {'recipe': 'key-union (r621)', 'ours': len(olines), 'theirs': len(tlines),
                       'union': len(out_lines), 'ours_unique': sorted(set(o)-set(t)), 'theirs_unique': sorted(set(t)-set(o))}
print('nulls union: %d + %d -> %d (ours_unique=%s theirs_unique=%s)' % (len(olines), len(tlines), len(out_lines), sorted(set(o)-set(t)), sorted(set(t)-set(o))))

# ---- history_bm-b.jsonl: union by epoch, sort asc ----
p = 'results/saturation_engine/history_bm-b.jsonl'
st = stages_of(p)
olines = blob(st['2']).decode('utf-8').splitlines()
tlines = blob(st['3']).decode('utf-8').splitlines()
o = {json.loads(l)['epoch']: l for l in olines}
t = {json.loads(l)['epoch']: l for l in tlines}
for k in set(o) & set(t):
    assert o[k] == t[k], 'shared epoch row mismatch %d' % k
merged_e = sorted(set(o) | set(t))
out_lines = [o[e] if e in o else t[e] for e in merged_e]
assert len(out_lines) == len(set(o) | set(t))
raw = blob(st['2'])
crlf = b'\r\n' in raw
nl = '\r\n' if crlf else '\n'
with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(nl.join(out_lines) + nl)
receipt['faces'][p] = {'recipe': 'epoch-union (r621)', 'ours': len(olines), 'theirs': len(tlines), 'union': len(out_lines)}
print('history union: %d + %d -> %d' % (len(olines), len(tlines), len(out_lines)))

# ---- snapshots: take ours (live ts 12:00:05 > 11:53:04) ----
for p in ['results/p1d_gates.json', 'results/saturation_engine/face_bm-b.json', 'results/saturation_engine/state_bm-b.json']:
    st = stages_of(p)
    data = blob(st['2'])
    assert b'<<<<<<<' not in data
    with open(p, 'wb') as f:
        f.write(data)
    receipt['faces'][p] = {'recipe': 'ts-duel ours-live-wins (r440)'}
    json.loads(data.decode('utf-8'))  # parse verify r185
    print('take ours: %s' % p)

# parse-verify jsonl files (r185 law)
for p in ['results/fund_divlowvol_p1/nulls.jsonl', 'results/saturation_engine/history_bm-b.jsonl']:
    for i, l in enumerate(open(p, encoding='utf-8')):
        if l.strip():
            json.loads(l)
    print('parse-ok: %s' % p)

with open('results/_r802bmb_pick4_resolve.json', 'w', encoding='utf-8') as f:
    json.dump(receipt, f, indent=1, ensure_ascii=False)

all_files = ['results/fund_divlowvol_p1/nulls.jsonl', 'results/saturation_engine/history_bm-b.jsonl',
             'results/p1d_gates.json', 'results/saturation_engine/face_bm-b.json',
             'results/saturation_engine/state_bm-b.json', 'results/_r802bmb_pick4_resolve.json']
r = subprocess.run(['git', 'add', '--'] + all_files, capture_output=True, text=True)
if r.returncode != 0:
    print('GIT ADD FAIL:', r.stderr); sys.exit(3)
print('pick-4 resolver done, receipt staged')
