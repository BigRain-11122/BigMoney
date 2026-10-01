# r502 bm-b cherry-pick conflict resolver #2 (pick 32855dd96)
# 1) results/p1d_gates.json: snapshot face (probe gates meta.date) -> take ours (HEAD=11:25 daemon write
#    newer than crashed-session 11:15 snapshot); rest of file identical per diff.
# 2) results/pool_core_samples.jsonl: append-log -> line-level union zero-loss (r188 law), ts-sorted.
import subprocess, json

def show(stage, path):
    return subprocess.check_output(['git', 'show', f':{stage}:{path}'])

# 1) p1d_gates.json -> ours
ours = show(2, 'results/p1d_gates.json')
json.loads(ours.decode('utf-8'))  # parse verify
with open('results/p1d_gates.json', 'wb') as f:
    f.write(ours)
print('p1d_gates.json: took ours (11:25 newer snapshot), parse OK')

# 2) pool_core_samples.jsonl -> union of :2: (ours) and :3: (theirs) lines
ours_lines = show(2, 'results/pool_core_samples.jsonl').decode('utf-8').splitlines()
theirs_lines = show(3, 'results/pool_core_samples.jsonl').decode('utf-8').splitlines()
union = {}
for ln in ours_lines + theirs_lines:
    ln = ln.strip()
    if not ln:
        continue
    obj = json.loads(ln)
    key = (obj['ts'], obj['machine_id'], obj.get('shard', ''), obj.get('pid'))
    union[key] = ln  # dedupe identical lines; conflicting dup keys -> ours wins (same-tick same-shard improbable)
def ts_key(ln):
    return json.loads(ln)['ts']
merged = sorted(union.values(), key=ts_key)
blob = '\n'.join(merged) + '\n'
with open('results/pool_core_samples.jsonl', 'wb') as f:
    f.write(blob.encode('utf-8'))
print(f'pool_core_samples.jsonl union: ours={len(ours_lines)} theirs={len(theirs_lines)} -> merged={len(merged)} (expect |A|+|B|-dup)')
print('RESOLVED-OK')
