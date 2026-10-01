import subprocess

KEEP = {
    'results/autofill_state.bm-a.json',
    'results/saturation_engine/state_bm-a.json',
    'results/saturation_engine/face_bm-a.json',
    'results/saturation_engine/history_bm-a.jsonl',
}

out = subprocess.check_output(['git', 'status', '--porcelain'], text=True)
paths = []
for line in out.splitlines():
    st = line[:2]
    if st == '??':
        continue  # untracked: own tools + stale leftovers -- never checkout targets
    p = line[3:].strip()
    if p.startswith('"') and p.endswith('"'):
        p = p[1:-1]
    if p in KEEP:
        continue
    paths.append(p)
print('checkout count:', len(paths))
subprocess.check_call(['git', 'checkout', '--'] + paths)
r = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
print('remaining status:')
print(r.stdout)
