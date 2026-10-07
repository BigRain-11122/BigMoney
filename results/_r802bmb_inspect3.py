import subprocess, json

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

for p in ['results/fund_divlowvol_p1/nulls.jsonl','results/saturation_engine/history_bm-b.jsonl']:
    st = stages_of(p)
    ours = blob(st['2']).decode('utf-8',errors='replace').splitlines()
    theirs = blob(st['3']).decode('utf-8',errors='replace').splitlines()
    os_, ts_ = set(ours), set(theirs)
    print('%s: ours=%d theirs=%d theirs_missing_from_ours=%d sample=%r' % (
        p, len(ours), len(theirs), len(ts_ - os_), list(ts_ - os_)[:2]))

for p in ['results/p1d_gates.json','results/saturation_engine/face_bm-b.json','results/saturation_engine/state_bm-b.json']:
    st = stages_of(p)
    o = json.loads(blob(st['2']))
    t = json.loads(blob(st['3']))
    ok = blob(st['2'])
    tk = blob(st['3'])
    print('%s: ours_bytes=%d theirs_bytes=%d identical=%s' % (p, len(ok), len(tk), ok == tk))
    # show a couple of ts-ish fields
    for k in ('ts','updated','last_tick','now','generated'):
        if isinstance(o, dict) and k in o:
            print('   ours.%s=%s theirs.%s=%s' % (k, str(o[k])[:40], k, str(t.get(k))[:40] if isinstance(t,dict) else '?'))
            break
