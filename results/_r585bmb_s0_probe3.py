# r585 bm-b probe3: locate non-engine local-only CODELY rows on origin (zero-loss audit)
import subprocess, sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
REPO = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
CREATE = 0x08000000

def blob(path, ref='origin/main'):
    r = subprocess.run(['git', '-C', REPO, 'show', '%s:%s' % (ref, path)],
                       capture_output=True, creationflags=CREATE)
    return r.stdout.decode('utf-8', 'replace') if r.returncode == 0 else None

faces = {
    'CODELY.md': blob('CODELY.md'),
    'research/pit-engine.md': blob('research/pit-engine.md'),
    'research/pit-pool.md': blob('research/pit-pool.md'),
    'research/pit-git.md': blob('research/pit-git.md'),
}
probes = ['r570 bm-a', 'r582 bm-b', 'r583 bm-b', 'r581 bm-b', 'r580 bm-b',
          'r578 bm-b', 'r370 bm-c', 'r359 bm-c', 'r566 bm-a', 'r565 bm-a',
          'r560 bm-b', 'r558 bm-b', 'r530 bm-b', 'r522 bm-b', 'r535 bm-a',
          'r521 bm-b', 'r534 bm-a', 'r330 bm-c', 'r529 bm-a', 'r319 bm-c',
          'r321 bm-c', 'r374 bm-c', 'r576 bm-b', 'r585 bm-a']
print('%-14s %-28s %s' % ('probe', 'in-CODELY', 'archive-location'))
for p in probes:
    loc = [k for k, v in faces.items() if k != 'CODELY.md' and v and p in v]
    inc = p in faces['CODELY.md'] if faces['CODELY.md'] else False
    print('%-14s %-28s %s' % (p, inc, loc if loc else '*** NOWHERE ***'))
# also check archive monthly files for anything nowhere
missing_check = ['r582 bm-b', 'r583 bm-b']
for m in ['research/memory-archive/202610.md', 'research/memory-archive/202609.md']:
    b = blob(m)
    if b:
        for p in missing_check:
            if p in b:
                print('%s found in %s' % (p, m))
