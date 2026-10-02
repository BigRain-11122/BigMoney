# -*- coding: utf-8 -*-
# r595 bm-b surgery-2: second unwind-FF-recommit loop this round. The r595 commit (local-only) was
# claw-blocked as r374 diverged-base artifact (bm-a engine batch pushed W114 shard files after my
# base 8b11232fc). r374 law: integrate first, never --no-verify. Loop: unwind -> FF realign at
# execution-time rev-parse -> D-face zeroing (E-08 law) -> foreign-M take-origin -> recommit.
import subprocess
import sys

def run(args):
    return subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='replace')

def die(msg):
    print("ABORT:", msg); sys.exit(1)

# 1) unwind local r595 commit (571f93927-family); base = 8b11232fc
r = run(['git', 'rev-parse', 'HEAD'])
head = r.stdout.strip()
r = run(['git', 'log', '-1', '--format=%s'])
if 'round 595' not in r.stdout:
    die('HEAD is not the r595 commit: %s' % r.stdout[:80])
r = run(['git', 'reset', '--mixed', 'HEAD~1'])
if r.returncode != 0: die('unwind reset failed: %s' % r.stderr)
r = run(['git', 'rev-parse', 'HEAD'])
base = r.stdout.strip()
print('step1 unwound; base=%s' % base)

# 2) fresh fetch + execution-time target (r593 law)
r = run(['git', 'fetch', 'origin'])
if r.returncode != 0: die('fetch failed')
r = run(['git', 'rev-parse', 'origin/main'])
TARGET = r.stdout.strip()
if len(TARGET) != 40: die('bad target %r' % TARGET)
print('step2 execution-time origin/main =', TARGET)

# 3) KEEP = every dirty tracked face of my r595 payload (pre-FF snapshot)
r = run(['git', 'status', '--porcelain'])
keep, untracked = [], []
for ln in r.stdout.split('\n'):
    if not ln.strip() or len(ln) < 4: continue
    xy, path = ln[:2], ln[3:]
    if xy.strip() == '??':
        untracked.append(path)
    else:
        keep.append(path)
print('step3 payload: %d tracked-dirty + %d untracked' % (len(keep), len(untracked)))

# 4) FF realign: CAS update-ref old=base -> new=TARGET, then reset --mixed TARGET
r = run(['git', 'update-ref', 'refs/heads/main', TARGET, base])
if r.returncode != 0: die('update-ref CAS failed: %s' % r.stderr)
r = run(['git', 'reset', '--mixed', TARGET])
if r.returncode != 0: die('reset --mixed failed: %s' % r.stderr)
print('step4 FF realigned main ->', TARGET)

# 5) E-08 law: zero ALL D faces (origin files missing on disk) before any add; foreign-M -> origin
r = run(['git', 'status', '--porcelain'])
d_paths, m_foreign, m_keep = [], [], []
keepset = set(keep)
for ln in r.stdout.split('\n'):
    if not ln.strip() or len(ln) < 4: continue
    xy, path = ln[:2], ln[3:]
    if xy == ' D' or xy == 'D ':
        d_paths.append(path)
    elif xy.strip() == 'M':
        (m_keep if path in keepset else m_foreign).append(path)
if d_paths:
    print('step5 D-face restore (%d):' % len(d_paths))
    for p in d_paths: print('   ', p)
    r = run(['git', 'checkout', '--'] + d_paths)
    if r.returncode != 0: die('D-face checkout failed: %s' % r.stderr)
if m_foreign:
    print('step5 foreign-M -> take origin (%d): %s' % (len(m_foreign), ', '.join(m_foreign)))
    r = run(['git', 'checkout', '--'] + m_foreign)
    if r.returncode != 0: die('foreign-M checkout failed: %s' % r.stderr)

# 6) verify zero deletions
r = run(['git', 'status', '--porcelain'])
bad = [l for l in r.stdout.split('\n')
       if l.strip() and (l.startswith(' D') or l.startswith('D ') or l.startswith('DD') or l.startswith('AD'))]
print('step6 final deletions=%d (must be 0)' % len(bad))
for b in bad: print('  STILL-D:', b)
if bad: die('deletions remain')
print('SURGERY-2 OK: tree = origin + r595 payload, zero deletions')
