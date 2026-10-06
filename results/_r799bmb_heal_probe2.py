import subprocess, json, hashlib

def show(ref, path):
    r = subprocess.run(['git', 'show', ref + ':' + path], capture_output=True)
    return r.stdout

def jd(b):
    return json.loads(b.decode('utf-8'))

def sha(o):
    return hashlib.sha256(json.dumps(o, sort_keys=True).encode()).hexdigest()

pre = jd(show('7ffcd2011', 'results/compute_audit.json'))
cur = jd(open('results/compute_audit.json', 'rb').read())
pre_rows = {sha(r): r for r in pre['history']}
cur_rows = {sha(r): r for r in cur['history']}
lost = [pre_rows[h] for h in set(pre_rows) - set(cur_rows)]
print('lost rows:', len(lost))
for r in lost:
    print(json.dumps(r, ensure_ascii=False)[:400])
# ts ordering check: where would they slot
all_ts = [r['ts'] for r in cur['history']]
print('cur ts range:', min(all_ts), '..', max(all_ts))
for r in lost:
    print('lost ts:', r['ts'])
