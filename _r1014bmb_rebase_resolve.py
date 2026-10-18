# -*- coding: utf-8 -*-
# r1014 bm-b rebase conflict resolver (r1008 family: shared regen faces ->
# per-file ts newer-wins whole-file). Rebase context: ours(stage2)=origin tip
# (bm-c r1104), theirs(stage3)=my replayed r1014 commit.
import subprocess, re, sys

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

TS_PAT = re.compile(r'(20\d\d-\d\d-\d\d[T ]\d\d:\d\d(?::\d\d)?)')


def side(stage, path):
    r = subprocess.run(['git', 'show', ':%d:%s' % (stage, path)],
                       capture_output=True, timeout=60)
    return r.returncode, r.stdout.decode('utf-8', 'replace')


def ts_of(text):
    m = TS_PAT.search(text)
    return m.group(1) if m else None


for p in FILES:
    rc2, ours = side(2, p)
    rc3, theirs = side(3, p)
    if rc2 != 0 and rc3 != 0:
        print('BOTH-MISSING %s -> git rm' % p)
        subprocess.run(['git', 'rm', '-f', '--', p], capture_output=True)
        continue
    if rc3 != 0:
        pick = 'ours'
    elif rc2 != 0:
        pick = 'theirs'
    else:
        to, tt = ts_of(ours), ts_of(theirs)
        if to and tt:
            pick = 'ours' if to >= tt else 'theirs'
        else:
            pick = 'ours'  # unparseable ts -> origin-tip side (fleet current truth)
        print('%s: ts_ours=%s ts_theirs=%s -> %s' % (p, to, tt, pick))
    r = subprocess.run(['git', 'checkout', '--%s' % pick, '--', p],
                       capture_output=True, timeout=60)
    if r.returncode != 0:
        print('CHECKOUT-FAIL %s rc=%d %s' % (p, r.returncode,
                                             r.stderr.decode('utf-8', 'replace')[:150]))
        sys.exit(1)
    r = subprocess.run(['git', 'add', '--', p], capture_output=True, timeout=60)
    if r.returncode != 0:
        print('ADD-FAIL %s' % p)
        sys.exit(1)

# post-resolve marker scan (r1048 claw law: zero conflict markers may ride)
bad = []
for p in FILES:
    r = subprocess.run(['git', 'show', ':0:%s' % p if False else ':%s' % p],
                       capture_output=True, timeout=60)
    t = r.stdout.decode('utf-8', 'replace')
    if '<<<<<<< ' in t or '>>>>>>> ' in t:
        bad.append(p)
if bad:
    print('MARKER-RESIDUE %s' % bad)
    sys.exit(1)
print('RESOLVE-OK 7+1 faces newer-wins, zero markers')
