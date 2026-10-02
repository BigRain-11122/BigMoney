import subprocess, sys, json, os

def git(*args):
    r = subprocess.run(['git'] + list(args), capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    return r

MY = '1c4304265'          # my unpushed round-604 commit (to withdraw)
BASE = 'a7d3fdfb8'         # its parent = previous origin tip

cur = git('rev-parse', 'origin/main').stdout.strip()
print('origin/main now:', cur)
if cur == BASE:
    print('FATAL: origin unchanged?? claw fired on stale base -- re-diagnose')
    sys.exit(2)

# what is in origin's new delta (for restore classification)
d = git('diff', '--name-only', BASE, cur).stdout.splitlines()
print('origin delta faces:', len(d))

# step 1: withdraw my commit (content stays in working tree)
r = git('reset', '--mixed', BASE)
print('withdraw rc=', r.returncode)

# step 2+3: CAS onto origin tip + re-anchor
r = git('update-ref', 'refs/heads/main', cur, BASE)
print('update-ref rc=', r.returncode, r.stderr.strip()[:200])
if r.returncode != 0:
    sys.exit(3)
r = git('reset', '--mixed', cur)
print('reset --mixed rc=', r.returncode)

# step 4: faceted restore of origin-new faces my tree lacks (r595: verify presence first)
r = git('status', '--porcelain')
lines = [l for l in r.stdout.splitlines() if l.strip()]
d_rows = [l[3:].strip() for l in lines if 'D' in l[:2] and not l.startswith('??')]
# keep-dirty daemon faces never restored
keep_dirty = {
    'results/p1d_gates.json', 'results/pool_core_samples.jsonl',
    'results/saturation_engine/face_bm-b.json', 'results/saturation_engine/history_bm-b.jsonl',
    'results/saturation_engine/state_bm-b.json',
}
d_rows = [p for p in d_rows if p not in keep_dirty]
print('D-restore rows:', len(d_rows))
if d_rows:
    ls = git('ls-tree', 'origin/main', '--name-only', '--', *d_rows)
    present = set(l for l in ls.stdout.splitlines() if l.strip())
    missing = [p for p in d_rows if p not in present]
    if missing:
        print('FATAL: D faces NOT in origin (true deletion?):', missing)
        sys.exit(4)
    r = git('checkout', '--', *d_rows)
    print('checkout restore rc=', r.returncode, r.stderr.strip()[:200])

# verify: no more D rows except keep-dirty
r = git('status', '--porcelain')
lines = [l for l in r.stdout.splitlines() if l.strip()]
bad = [l for l in lines if 'D' in l[:2] and l[3:].strip() not in keep_dirty and not l.startswith('??')]
print('remaining non-keep D rows:', len(bad))
for l in bad[:5]:
    print('  ', l)
print('ring 2 phase A-B complete; working tree holds my payload dirty, HEAD==origin', cur[:9])
