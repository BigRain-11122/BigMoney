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

# epoch-union for history ledger
p = 'results/saturation_engine/history_bm-b.jsonl'
st = stages_of(p)
if st:
    olines = blob(st['2']).decode('utf-8').splitlines()
    tlines = blob(st['3']).decode('utf-8').splitlines()
    o = {json.loads(l)['epoch']: l for l in olines}
    t = {json.loads(l)['epoch']: l for l in tlines}
    for e in set(o) & set(t):
        assert o[e] == t[e], 'shared epoch mismatch %d' % e
    merged = [o[e] if e in o else t[e] for e in sorted(set(o) | set(t))]
    nl = '\r\n' if '\r\n' in blob(st['2']).decode('utf-8', errors='replace') else '\n'
    with open(p, 'w', encoding='utf-8', newline='') as f:
        f.write(nl.join(merged) + nl)
    print('epoch-union: %d + %d -> %d' % (len(olines), len(tlines), len(merged)))

# ts-duel take-ours for live snapshots (ours = newer live state at every churn pick)
for p in ['results/p1d_gates.json', 'results/saturation_engine/face_bm-b.json', 'results/saturation_engine/state_bm-b.json']:
    st = stages_of(p)
    if st:
        data = blob(st['2'])
        assert b'<<<<<<<' not in data
        with open(p, 'wb') as f:
            f.write(data)
        json.loads(data.decode('utf-8'))
        print('take-ours: %s' % p)

r = subprocess.run(['git','add','-A','results/saturation_engine','results/p1d_gates.json'],
                   capture_output=True, text=True)
sys.exit(r.returncode)
