import subprocess, os, hashlib

keep = {
    'results/autofill_state.bm-b.json',
    'results/p1d_gates.json',
    'results/pool_core_samples.jsonl',
    'results/saturation_engine/face_bm-b.json',
    'results/saturation_engine/history_bm-b.jsonl',
    'results/saturation_engine/ledger_bm-b.jsonl',
    'results/saturation_engine/state_bm-b.json',
}
r = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
files = []
inbox_pair = []
for line in r.stdout.splitlines():
    st, path = line[:2], line[3:].strip().strip('"')
    if 'M' in st and path not in keep:
        files.append(path)
    elif 'D' in st and path not in keep:
        files.append(path)
# restore all D/M faces (except keep)
r2 = subprocess.run(['git', 'restore', '--'] + files, capture_output=True, text=True)
print('restoring', len(files), 'faces rc', r2.returncode, r2.stderr[-300:] if r2.stderr else '')

# r586 law: D+?? same-name pair for inbox MSG -> blob identity -> delete untracked original
untracked_msg = 'fleet/inbox/MSG-20261002-1817-bmb-w109-seat.md'
processed_msg = 'fleet/inbox/processed/MSG-20261002-1817-bmb-w109-seat.md'
if os.path.exists(untracked_msg) and os.path.exists(processed_msg):
    h1 = hashlib.sha256(open(untracked_msg, 'rb').read()).hexdigest()
    r3 = subprocess.run(['git', 'hash-object', processed_msg], capture_output=True, text=True)
    print('untracked sha256:', h1[:12], 'processed git-blob:', r3.stdout.strip()[:12])
    # compare content bytes via git show of the processed blob vs local file
    r4 = subprocess.run(['git', 'show', 'HEAD:' + processed_msg], capture_output=True)
    same = r4.stdout == open(untracked_msg, 'rb').read()
    print('byte-identical:', same)
    if same:
        os.remove(untracked_msg)
        print('untracked original removed (r586 closeout)')
r5 = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
print(r5.stdout)
