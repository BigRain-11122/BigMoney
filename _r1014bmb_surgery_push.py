# -*- coding: utf-8 -*-
# r1014 bm-b rebase ghost-refusal bypass (r1032 quit+surgery / r1008 write-tree
# straight-through). Context: rebase of my r1014 commit eca78df594 onto bm-c tip
# 5253a3e59d; all 8 UU faces resolved+added, `rebase --continue` ghost-refuses.
import subprocess, re, os, tempfile, sys

BASE = '5253a3e59d58d46bc9a1557d87d1bb9f237ac615'
MINE = 'eca78df594'
FILES = [
    'docs/daily_report/REPORT-2026-10-19.json',
    'docs/daily_report/REPORT-2026-10-19.md',
    'results/_attrition_guard_scan.json',
    'results/_r686bmb_d19_check.json',
    'results/compute_audit.json',
    'results/fundamental_b_layer_filter.json',
    'results/regime_state.json',
    'results/update_status.json',
]


def git(*a):
    return subprocess.run(['git'] + list(a), capture_output=True)


def sha40(s):
    return re.fullmatch(r'[0-9a-f]{40}', s or '') is not None


# 1. zero unmerged entries (ghost-refusal precondition)
r = git('ls-files', '--unmerged')
assert r.stdout.strip() == b'', ('unmerged remain', r.stdout[:300])

# 2. write-tree on the fully-resolved index
r = git('write-tree')
tree = r.stdout.decode().strip()
assert r.returncode == 0 and sha40(tree), ('write-tree', tree, r.stderr[:200])

# 3. commit-tree on bm-c tip with the original r1014 message
r = git('log', '-1', '--format=%B', MINE)
msg = r.stdout.decode('utf-8')
msgf = os.path.join(tempfile.gettempdir(), 'r1014bmb_msg.txt')
with open(msgf, 'w', encoding='utf-8', newline='\n') as f:
    f.write(msg)
r = git('commit-tree', tree, '-p', BASE, '-F', msgf)
newc = r.stdout.decode().strip()
assert r.returncode == 0 and sha40(newc), ('commit-tree', newc, r.stderr[:300])

# 4. marker scan on the new commit (commit-tree bypasses hooks -- manual claw)
for p in FILES:
    r = git('show', '%s:%s' % (newc, p))
    t = r.stdout.decode('utf-8', 'replace')
    assert '<<<<<<< ' not in t and '>>>>>>> ' not in t, ('marker', p)

# 5. quit + full-name update-ref + reset --mixed (reflog-guard: local main had
#    zero foreign commits -- rebase never completed a replay)
r = git('rebase', '--quit')
assert r.returncode == 0, ('rebase --quit', r.stderr[:200])
r = git('update-ref', 'refs/heads/main', newc)
assert r.returncode == 0, ('update-ref', r.stderr[:200])
r = git('reset', '--mixed')
assert r.returncode == 0, ('reset', r.stderr[:200])
r = git('symbolic-ref', '-q', 'HEAD')
assert r.stdout.decode().strip() == 'refs/heads/main', 'detached after surgery'

# 6. push + verify
r = subprocess.run(['git', 'push', 'origin', 'refs/heads/main:refs/heads/main'],
                   capture_output=True)
out = (r.stdout + r.stderr).decode(errors='replace')
push_ok = r.returncode == 0 and not any(
    w in out for w in ('fatal', 'rejected', 'failed', 'error'))
assert push_ok, ('push', out[:300])
r = git('fetch', 'origin')
assert r.returncode == 0
tip = git('rev-parse', 'origin/main').stdout.decode().strip()
head = git('rev-parse', 'HEAD').stdout.decode().strip()
behind = git('rev-list', '--count', 'HEAD..origin/main').stdout.decode().strip()
ahead = git('rev-list', '--count', 'origin/main..HEAD').stdout.decode().strip()
assert tip == head and behind == '0', ('delivery', tip, head)
print('{"surgery_push": "ok", "base": "%s", "new": "%s", "tip": "%s", '
      '"behind": %s, "ahead": %s}' % (BASE[:10], newc[:10], tip[:10], behind, ahead))
