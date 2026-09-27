import subprocess

def show(ref, f):
    return subprocess.run(['git', 'show', ref + ':' + f], capture_output=True).stdout.decode('utf-8', errors='replace')

for f in ['CODELY.md', 'research/memory-archive/202609.md']:
    b = show('origin/machine/bm-c-r89', f)
    m = open(f, encoding='utf-8').read()
    bset = set(l.strip() for l in b.splitlines() if l.strip())
    mset = set(l.strip() for l in m.splitlines() if l.strip())
    only_b = sorted(x for x in bset - mset if x.startswith('-'))
    only_m = sorted(x for x in mset - bset if x.startswith('-'))
    print('== %s : branch %dB / main %dB, branch-only lines=%d, main-only lines=%d' % (f, len(b.encode("utf-8")), len(m.encode("utf-8")), len(only_b), len(only_m)))
    for x in only_b[:10]:
        print('  BRANCH-ONLY:', x[:180])
    for x in only_m[:10]:
        print('  MAIN-ONLY :', x[:180])
