# r585 bm-b pre-surgery probe: line-set diff between working tree and origin
# blob for CODELY.md + pool_core_samples.jsonl (r373 blob-space law, r530 bytes law)
import subprocess, sys, os, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
REPO = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
CREATE = 0x08000000

def blob(path, ref):
    r = subprocess.run(['git', '-C', REPO, 'show', '%s:%s' % (ref, path)],
                       capture_output=True, creationflags=CREATE)
    return r.stdout if r.returncode == 0 else None

def worktree(path):
    with open(os.path.join(REPO, path), 'rb') as f:
        return f.read()

for path in ['CODELY.md', 'results/pool_core_samples.jsonl']:
    ob = blob(path, 'origin/main')
    lb = worktree(path)
    if ob is None:
        print('%s: NOT ON origin' % path); continue
    # blob space: repo blobs are LF; compare line sets
    olines = [l for l in ob.split(b'\n') if l.strip()]
    llines = [l for l in lb.replace(b'\r\n', b'\n').split(b'\n') if l.strip()]
    oset, lset = set(olines), set(llines)
    only_local = [l for l in llines if l not in oset]
    only_origin = [l for l in olines if l not in lset]
    print('%s: origin_lines=%d local_lines=%d only_local=%d only_origin=%d'
          % (path, len(olines), len(llines), len(only_local), len(only_origin)))
    for l in only_local[:12]:
        print('  LOCAL-ONLY: %s' % l[:150].decode('utf-8', 'replace'))
    for l in only_origin[:12]:
        print('  ORIGIN-ONLY: %s' % l[:150].decode('utf-8', 'replace'))

# engine pointer line check across three faces
t = blob('CODELY.md', 'origin/main').decode('utf-8', 'replace')
print('origin has engine-domain pointer line: %s' % ('\u5f15\u64ce\u57df\u62c6\u4ef6' in t))
h = blob('CODELY.md', 'HEAD').decode('utf-8', 'replace')
print('HEAD has engine-domain pointer line: %s' % ('\u5f15\u64ce\u57df\u62c6\u4ef6' in h))
# merge-base + my committed delta files
r = subprocess.run(['git', '-C', REPO, 'merge-base', 'main', 'origin/main'],
                   capture_output=True, text=True, creationflags=CREATE)
base = r.stdout.strip()
print('merge-base=%s' % base[:12])
r = subprocess.run(['git', '-C', REPO, 'diff', '--name-only', base, 'main'],
                   capture_output=True, text=True, creationflags=CREATE)
my_files = [l for l in r.stdout.splitlines() if l.strip()]
print('my_committed_delta_files=%d' % len(my_files))
print('\n'.join('  ' + f for f in my_files))
