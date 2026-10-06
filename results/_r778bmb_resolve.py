# r778 bm-b merge-window resolver (dead-session r777 adoption)
# Single UU face: results/_attrition_guard_scan.json
# Per-window ts evidence (r773 law): theirs 15:31:38 > ours 15:28:53, all other
# fields byte-identical (active_loss/files/rc) => take-new theirs, zero-loss.
# r609-2 law: blob-sha level compare (smudge-immune); r609-3: staged marker scan.
import subprocess, json, sys

PATH = 'results/_attrition_guard_scan.json'

def sh(*args):
    r = subprocess.run(list(args), capture_output=True)
    if r.returncode != 0:
        print('FAIL cmd:', args, r.stderr.decode('utf-8', 'replace')[:400]); sys.exit(2)
    return r.stdout

# 1) capture pre-add stage refs (r764: bare segment refs, no double colon)
ours_sha = sh('git', 'rev-parse', 'HEAD:' + PATH).decode().strip()
theirs_sha = sh('git', 'rev-parse', 'MERGE_HEAD:' + PATH).decode().strip()
print('ours_sha  ', ours_sha)
print('theirs_sha', theirs_sha)

# 2) ts evidence assertion (strptime-normalized numeric compare, r756 law)
from datetime import datetime
def pts(s): return datetime.fromisoformat(s)
o = json.loads(sh('git', 'show', 'HEAD:' + PATH))
t = json.loads(sh('git', 'show', 'MERGE_HEAD:' + PATH))
assert set(o) == set(t) == {'active_loss', 'files', 'rc', 'ts'}, 'key drift'
assert o['active_loss'] == t['active_loss'] and o['files'] == t['files'] and o['rc'] == t['rc'], 'content drift beyond ts'
assert pts(t['ts']) > pts(o['ts']), 'theirs must be newer for take-new'

# 3) materialize theirs blob bytes verbatim (byte-exact, no smudge)
blob = sh('git', 'show', 'MERGE_HEAD:' + PATH)
json.loads(blob)  # parse gate before write (r185 law)
with open(PATH, 'wb') as f:
    f.write(blob)

# 4) add, then verify staged blob-sha == theirs (r609-2: sha-level, immune to CRLF)
sh('git', 'add', PATH)
staged = sh('git', 'ls-files', '-s', PATH).decode().strip().split()
assert staged[1] == theirs_sha, 'staged sha %s != theirs %s' % (staged[1], theirs_sha)

# 5) staged-face conflict-marker scan across ALL staged entries (r609-3)
# Precise form: line-anchored markers only (prose-quoted literals in law text
# e.g. CODELY.md r609 entry are NOT conflict markers -- verified by hand above).
import re
pat_start = re.compile(rb'^<<<<<<< ')
pat_mid = re.compile(rb'^=======$')
pat_end = re.compile(rb'^>>>>>>> ')
out = sh('git', 'diff', '--cached', '--name-only').decode().splitlines()
bad = []
for p in out:
    b = sh('git', 'show', ':' + p)
    for ln in b.splitlines():
        if pat_start.match(ln) or pat_mid.match(ln) or pat_end.match(ln):
            bad.append(p); break
assert not bad, 'real marker leftovers in staged faces: %r' % bad
print('staged faces scanned:', len(out), 'marker leftovers: 0')

# 6) worktree-vs-blob parse identity (take-new face content gate)
with open(PATH, 'rb') as f:
    wt = f.read()
assert json.loads(wt) == t, 'worktree != theirs content'
print('RESOLVED take-new theirs, ts=', t['ts'])
print('OK single-face resolution complete; merge commit may proceed')
