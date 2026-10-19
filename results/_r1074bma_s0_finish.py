# r1074bm-a S0: mark UU resolved (live-writer fresh face 07:51:04 wins), scan markers, drop autostash, verify
import subprocess, sys
REPO = r'C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney'
def git(*args):
    r = subprocess.run(['git', '-C', REPO] + list(args), capture_output=True, text=True, encoding='utf-8', errors='replace')
    return r.returncode, (r.stdout or '') + (r.stderr or '')
# 1. add the live-writer face (clears UU)
rc, out = git('add', 'results/watermark_red.json')
print('add rc', rc, out.strip()[:200])
# 2. marker scan (git diff --check over staged + worktree)
rc, out = git('diff', '--check')
print('diff-check rc', rc, 'markers:', repr(out.strip()[:200]) if out.strip() else 'CLEAN')
# 3. stash list
rc, out = git('stash', 'list')
print('stash-list rc', rc)
print(out.strip()[:400])
lines = [l for l in out.splitlines() if 'autostash' in l or ('On ' in l and 'autostash' in l)]
# drop autostash stash@{0} only if it is OUR fresh autostash (created this window)
if lines:
    rc, out = git('stash', 'drop', 'stash@{0}')
    print('stash-drop rc', rc, out.strip()[:200])
else:
    print('NO_AUTOSTASH_ENTRY (already dropped or none)')
# 4. final status + behind/ahead
rc, out = git('status', '--porcelain=v1', '-uall')
print('status rc', rc); print(out.strip()[:500])
rc, out = git('rev-list', '--count', 'origin/main..main')
ahead = out.strip()
rc, out = git('rev-list', '--count', 'main..origin/main')
behind = out.strip()
print('ahead', ahead, 'behind', behind)
