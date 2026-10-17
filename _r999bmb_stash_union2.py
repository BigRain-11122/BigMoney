# r999: union-merge r998's untracked post_review/REPORT-20261018.md (left in stash^3 by
# "already exists, no checkout") into HEAD's version. Other 4 same-day regen faces skipped
# (daily_report/ceo_live legs re-derive them in-chain this round).
import subprocess, io

def blob(spec):
    return subprocess.check_output(['git', 'show', spec]).decode('utf-8', errors='replace')

p = 'results/post_review/REPORT-20261018.md'
head = blob('HEAD:' + p).splitlines()
stashv = blob('stash@{0}^3:' + p).splitlines()
sset = set(l.rstrip('\r') for l in head)
extra = [l for l in stashv if l.rstrip('\r') not in sset]
merged = head + extra
with io.open(p, 'w', encoding='utf-8', newline='') as f:
    if merged:
        f.write('\n'.join(merged) + '\n')
print('post_review REPORT union head=%d stash=%d extra=%d' % (len(head), len(stashv), len(extra)))
