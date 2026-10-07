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

st = stages_of('results/fund_divlowvol_p1/nulls.jsonl')
ours = [json.loads(l) for l in blob(st['2']).decode('utf-8').splitlines()]
theirs = [json.loads(l) for l in blob(st['3']).decode('utf-8').splitlines()]
print('nulls ours k-range: %d..%d (sorted=%s) head=%r' % (ours[0]['k'], ours[-1]['k'], [r['k'] for r in ours] == sorted(r['k'] for r in ours), [r['k'] for r in ours[:3]]))
print('nulls theirs k-range: %d..%d (sorted=%s) tail=%r' % (theirs[0]['k'], theirs[-1]['k'], [r['k'] for r in theirs] == sorted(r['k'] for r in theirs), [r['k'] for r in theirs[-3:]]))
ok = set(r['k'] for r in ours); tk = set(r['k'] for r in theirs)
print('ours_unique_k=%d theirs_unique_k=%d sample_ours_unique=%r' % (len(ok-tk), len(tk-ok), sorted(ok-tk)[:5]))
print('ours 1757/1758 present: %s/%s' % (1757 in ok, 1758 in ok))

st2 = stages_of('results/saturation_engine/history_bm-b.jsonl')
oh = [json.loads(l) for l in blob(st2['2']).decode('utf-8').splitlines()]
th = [json.loads(l) for l in blob(st2['3']).decode('utf-8').splitlines()]
oe = [r['epoch'] for r in oh]; te = [r['epoch'] for r in th]
print('hist ours epoch sorted=%s range=%d..%d' % (oe == sorted(oe), oe[0], oe[-1]))
print('hist theirs epoch sorted=%s range=%d..%d' % (te == sorted(te), te[0], te[-1]))
ou = set(oe) - set(te); tu = set(te) - set(oe)
print('hist ours_unique=%d theirs_unique=%d' % (len(ou), len(tu)))
print('hist ours_unique epochs=%r' % sorted(ou))
print('hist theirs_unique epochs=%r' % sorted(tu))
# dup check within each side
print('hist ours dups=%d theirs dups=%d' % (len(oe)-len(set(oe)), len(te)-len(set(te))))
