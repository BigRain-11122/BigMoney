# -*- coding: utf-8 -*-
# r431 bm-c: surgical replay of pending pick-3 (S7 wrap commit) after r427-style
# rebase closeout. Daemon-live worktree faces keep the LIVE version (newer-wins,
# r630 law -- no rollback of actively-written append-only faces); all other pick-3
# files restored from the original commit. 40-hex hard verification before any use.
import subprocess, re, sys

REPO = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
CREATE = 0x08000000
SHORT = '6e6c5f55b'

def git(*a):
    p = subprocess.run(['git'] + list(a), capture_output=True, creationflags=CREATE, cwd=REPO)
    return p.returncode, (p.stdout or b'').decode('utf-8', 'replace') + (p.stderr or b'').decode('utf-8', 'replace')

rc, full = git('rev-parse', SHORT)
full = full.strip()
if not re.match(r'^[0-9a-f]{40}$', full):
    print('FAIL resolve pick3 sha: %r' % full[:60])
    sys.exit(2)
print('PICK3=%s' % full)

rc, msg = git('log', '-1', '--format=%s', full)
print('PICK3_MSG=%s' % msg.strip()[:80])

rc, files_out = git('show', '--format=', '--name-only', full)
p3 = [f.strip() for f in files_out.split('\n') if f.strip()]
print('PICK3_FILES=%d' % len(p3))

rc, st = git('status', '--porcelain')
live = set()
for ln in st.split('\n'):
    if ln.startswith(' M '):
        live.add(ln[3:].strip().strip('"'))
print('LIVE_NOW=%d' % len(live))

skipped_live = sorted(set(p3) & live)
restored = sorted(set(p3) - live)
print('RESTORE=%d LIVE-WINS=%d %s' % (len(restored), len(skipped_live), skipped_live[:6]))
for f in restored:
    rc, out = git('checkout', full, '--', f)
    if rc != 0:
        print('FAIL checkout %s: %s' % (f, out[:100]))
        sys.exit(2)

git('add', '-A', '--', ':(exclude)results/_r426bmc_w2_judge_finalize_log.txt')
rc, out = git('commit', '-C', full)
if rc != 0:
    print('FAIL commit -C: %s' % out[:300])
    sys.exit(2)
rc, new_head = git('rev-parse', 'HEAD')
new_head = new_head.strip()
print('P3_LANDED=%s rc=0' % new_head)

# marker scan on THIS ROUND's delta files (line-anchored, r423 caliber)
rc, touched = git('diff', '--name-only', 'origin/main..HEAD')
bad = []
for f in [x.strip() for x in touched.split('\n') if x.strip()]:
    rc, blob = git('show', 'HEAD:%s' % f)
    if rc != 0:
        continue
    for i, ln in enumerate(blob.split('\n')):
        if re.match(r'^(<<<<<<<|\|\|\|\|\|\|\||=======$|>>>>>>>)', ln.rstrip('\r')):
            bad.append((f, i + 1))
print('MARKER_SCAN_DELTA=%d files, hits=%s' % (len([x for x in touched.split('\n') if x.strip()]), bad if bad else 'NONE'))
if bad:
    sys.exit(2)

rc, ahead = git('rev-list', '--left-right', '--count', 'origin/main...HEAD')
print('AHEAD_BEHIND(origin...HEAD)=%s' % ahead.strip())
print('PICK3 SURGICAL REPLAY DONE')
