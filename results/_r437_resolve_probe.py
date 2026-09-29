import subprocess, json, sys

def show(rev, path):
    return subprocess.run(['git', 'show', f'{rev}:{path}'], capture_output=True).stdout.decode('utf-8', errors='replace')

MINE = 'a108ca779'   # stage3 (replayed round-437 close)
ORIG = '26d0d8dbb'   # stage2 (origin head: bm-c r232 close)
base = subprocess.run(['git', 'merge-base', MINE + '^', ORIG], capture_output=True).stdout.decode().strip()
print('merge-base:', base)

uu = [l[3:] for l in subprocess.run(['git', 'status', '--porcelain'], capture_output=True).stdout.decode().splitlines() if l.startswith('UU')]

for p in uu:
    b = set(show(base, p).split('\n'))
    o = set(show(ORIG, p).split('\n'))
    m = set(show(MINE, p).split('\n'))
    print(f'== {p}')
    print(f'   origin +{len(o-b)} -{len(b-o)} | mine +{len(m-b)} -{len(b-m)} | common-new {len((o&m)-b)}')
    for l in sorted(o - b)[:3]:
        print('   O+', l[:130])
    for l in sorted(m - b)[:3]:
        print('   M+', l[:130])
