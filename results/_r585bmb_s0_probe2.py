# r585 bm-b probe2: verify engine-domain split zero-loss + pool row byte diff + inbox MSG state
import subprocess, sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
REPO = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
CREATE = 0x08000000

def blob(path, ref='origin/main'):
    r = subprocess.run(['git', '-C', REPO, 'show', '%s:%s' % (ref, path)],
                       capture_output=True, creationflags=CREATE)
    return r.stdout if r.returncode == 0 else None

# 1. pit-engine.md on origin: exists + contains migrated rows (spot check 5)
pe = blob('research/pit-engine.md')
print('pit-engine.md on origin: %s bytes=%s' % (pe is not None, len(pe) if pe else 0))
if pe:
    t = pe.decode('utf-8', 'replace')
    for probe in ['r511 bm-b', 'r518 bm-b', 'r523 bm-a', 'r576 bm-b', 'r374 bm-c',
                  'r570 bm-a', 'r583 bm-b', 'r582 bm-b']:
        print('  contains %s: %s' % (probe, probe in t))
    # count rows in pit-engine
    print('  md5-assert rows mention count:', t.count('## ') if '## ' in t else 'n/a')

# 2. full-byte diff of one diverged pool row (n1w103-0of12) local vs origin
ob = blob('results/pool_core_samples.jsonl').decode('utf-8', 'replace')
with open(os.path.join(REPO, 'results', 'pool_core_samples.jsonl'), 'rb') as f:
    lb = f.read().decode('utf-8', 'replace')
for o_line in ob.splitlines():
    if 'n1w103-0of12' in o_line:
        for l_line in lb.splitlines():
            if 'n1w103-0of12' in l_line:
                print('ORIG-ROW: %s' % o_line)
                print('LOCAL-ROW: %s' % l_line)
                import json
                oj, lj = json.loads(o_line), json.loads(l_line)
                for k in sorted(set(oj) | set(lj)):
                    if oj.get(k) != lj.get(k):
                        print('  DIFF KEY %s: origin=%r local=%r' % (k, oj.get(k), lj.get(k)))
                break
        break

# 3. inbox + processed MSG state for the W102 seat file
for d in ['fleet/inbox', 'fleet/inbox/processed']:
    p = os.path.join(REPO, d.replace('/', os.sep))
    if os.path.isdir(p):
        names = sorted(os.listdir(p))
        w102 = [n for n in names if 'w102' in n.lower() or 'W102' in n]
        print('%s: files=%d w102=%s' % (d, len(names), w102))
r = subprocess.run(['git', '-C', REPO, 'ls-tree', 'origin/main', '--name-only',
                    'fleet/inbox/', 'fleet/inbox/processed/'],
                   capture_output=True, text=True, creationflags=CREATE)
lines = [l for l in r.stdout.splitlines() if 'w102' in l.lower()]
print('origin inbox w102 files: %s' % lines)
