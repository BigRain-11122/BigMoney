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

st = stages_of('results/compute_audit.json')
for s in ['1','2','3']:
    raw = subprocess.run(['git','cat-file','-p',st[s]],capture_output=True).stdout
    j = json.loads(raw)
    lat = j.get('latest',{})
    hist = j.get('history',[])
    print('st%s: latest.ts=%s hist_n=%d' % (s, lat.get('ts','?'), len(hist)))
    if hist:
        print('   hist[0].ts=%s hist[-1].ts=%s entry_keys=%s' % (hist[0].get('ts'), hist[-1].get('ts'), list(hist[0].keys())[:10]))
# regime_state deeper look for ledger keys
st2 = stages_of('results/regime_state.json')
for s in ['2','3']:
    raw = subprocess.run(['git','cat-file','-p',st2[s]],capture_output=True).stdout
    j = json.loads(raw)
    trans = j.get('transitions')
    print('regime st%s: transitions=%s dims_keys=%s' % (s, ('n=%d' % len(trans)) if isinstance(trans,list) else str(trans)[:50], list(j.get('dims',{}).keys())[:8] if isinstance(j.get('dims'),dict) else str(j.get('dims'))[:50]))
