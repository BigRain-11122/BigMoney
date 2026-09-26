# r280bm-b rebase collision resolver: fusion-nav-0of1 claim race (bm-a 23:20:03 original claim,
# renewed 23:40:03 via 83b08771; my tick 2805e84c 23:40:04 re-claim 20min late, tick verdict itself
# = claim_lost_yield). Per fleet/README s4 commit-order later-yield + r279/r266 law: take origin
# (bm-a) face byte-exact for results/runnable_pool.json; my claim replay becomes legal empty drop
# (r279 precedent: yielding pre-commit = zero-change legal drop, do not chase).
import subprocess, json, sys

PATH = 'results/runnable_pool.json'

def blob(rev):
    r = subprocess.run(['git', 'show', rev + ':' + PATH], capture_output=True)
    if r.returncode != 0:
        print('FATAL: cannot read', rev, r.stderr.decode('utf-8', 'replace')); sys.exit(1)
    return r.stdout

theirs = blob('83b08771')  # origin/main canonical face (bm-a owner)
d = json.loads(theirs.decode('utf-8'))
fus = [e for e in d.get('entries', []) if str(e.get('id', '')) == 'FUSION-P1-NAV']
assert len(fus) == 1, 'FUSION-P1-NAV entry count != 1'
sh = fus[0]['shards']
assert len(sh) == 1 and sh[0]['key'] == 'fusion-nav-0of1', 'shard face drifted: %r' % sh
assert sh[0].get('owner') == 'bm-a', 'owner not bm-a: %r' % sh[0].get('owner')
assert sh[0].get('owner_since') == '2026-09-26 23:40:03', 'owner_since face drifted: %r' % sh[0].get('owner_since')
assert theirs.endswith(b'\n') is False, 'origin blob tail-newline face drifted'
with open(PATH, 'wb') as f:
    f.write(theirs)  # byte-exact LF face, zero EOL flip (R269 family: mirror last-writer face)
subprocess.run(['git', 'add', PATH], check=True)
print('OK: runnable_pool.json resolved to bm-a yield face (owner=bm-a, owner_since=23:40:03), byte-exact LF')
