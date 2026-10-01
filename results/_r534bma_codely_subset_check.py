"""r534: verify worktree CODELY.md subset of HEAD (r326 reverse-drop guard) before checkout."""
import subprocess

def run(args):
    return subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='replace').stdout

wt = open(r'CODELY.md', encoding='utf-8').read().splitlines()
head = run(['git', 'show', 'HEAD:CODELY.md']).splitlines()
head_set = set(head)
missing = [l for l in wt if l not in head_set and l.strip()]
print(f'worktree lines: {len(wt)}, HEAD lines: {len(head)}')
print('worktree-unique lines (missing from HEAD):', len(missing))
for l in missing[:10]:
    print('  MISS:', l[:100])
print('VERDICT:', 'SUBSET-SAFE-CHECKOUT' if not missing else 'UNION-REQUIRED')
