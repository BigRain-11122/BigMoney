# -*- coding: utf-8 -*-
# r992 bm-b: POOL-0018 first-batch delivery via temp-index tree surgery on the
# GROUP repo (promisor + sparse-cone tree: surgery never touches the worktree).
# Foreign-face guard: files already on origin with diverging content are SKIPPED
# (never overwrite another machine's face); byte-identical = already-delivered.
# Also carries the D-19 dual watermark probe (decisions/orders sha256 vs state keys).
import subprocess, hashlib, json, os, sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

GRP = r'C:\Fluxgroup\FluxGroup'
ANCH = 'cph4/fleet/mv-album-001-jay/anchors'
DISK = os.path.join(GRP, ANCH)
D19_DEC_KEY = '1d4741e4a0d6514519040442182b0679a423d58896a4105861e152108be441f1'
D19_ORD_KEY = '1df82bab4faea632fb2593a54fce799680878091aea9184220635e9d43c1dfa7'

def git(*a, timeout=180):
    r = subprocess.run(['git', '-C', GRP] + list(a), capture_output=True, timeout=timeout)
    return r.returncode, r.stdout.decode('utf-8', 'replace').strip()

files = sorted(f for f in os.listdir(DISK) if f.endswith('-words.json'))
print('WORDS_FILES_ON_DISK=%d' % len(files))

rcf, _ = git('fetch', 'origin')
rc, tip = git('rev-parse', 'origin/main')
print('ORIGIN_MAIN=%s rc=%d fetch_rc=%d' % (tip, rc, rcf))

tmpidx = os.path.join(GRP, '.git', 'surgery_idx_r992')
msgfile = os.path.join(GRP, '.git', 'surgery_msg_r992.txt')
env = dict(os.environ, GIT_INDEX_FILE=tmpidx)

def genv(*a, timeout=240):
    r = subprocess.run(['git', '-C', GRP] + list(a), capture_output=True, env=env, timeout=timeout)
    return r.returncode, r.stdout.decode('utf-8', 'replace').strip()

rc, _ = genv('read-tree', tip)
print('READ_TREE rc=%d' % rc)
if rc != 0:
    print('FATAL read-tree failed')
    sys.exit(2)

added, skipped_identical, skipped_foreign = [], [], []
for f in files:
    p = os.path.join(DISK, f)
    rel = ANCH + '/' + f
    r = subprocess.run(['git', '-C', GRP, 'hash-object', '-w', '--no-filters', p],
                       capture_output=True, timeout=60)
    sha = r.stdout.decode('utf-8', 'replace').strip()
    if len(sha) != 40:
        print('HASH_FAIL %s -> %r' % (f, sha[:60]))
        continue
    rc0, osha = git('rev-parse', tip + ':' + rel)
    if rc0 == 0 and osha == sha:
        skipped_identical.append(rel)
        continue
    if rc0 == 0 and osha != sha:
        skipped_foreign.append((rel, osha, sha))
        continue
    rcu, _ = genv('update-index', '--add', '--cacheinfo', '100644', sha, rel)
    if rcu == 0:
        added.append((rel, sha))
    else:
        print('UPDATE_INDEX_FAIL %s rc=%d' % (rel, rcu))

print('ADD=%d IDENTICAL_SKIP=%d FOREIGN_SKIP=%d' % (len(added), len(skipped_identical), len(skipped_foreign)))
for rel, osha, msha in skipped_foreign:
    print('FOREIGN-DIVERGES %s origin=%s mine=%s (left untouched)' % (rel, osha[:12], msha[:12]))

newc = None
if added:
    rc, tree = genv('write-tree')
    print('TREE=%s rc=%d' % (tree, rc))
    if rc != 0:
        print('FATAL write-tree')
        sys.exit(2)
    msg = ('POOL-0018 first-batch done: whisperX word anchors %d/%d (Jay album songs)\n\n'
           'Card: POOL-0018 (dispatcher pool, bm-b lane cpu-sound, claimed r990/r991)\n'
           'Action: done (first batch, %d files this push)\n'
           'Evidence: cph4/fleet/mv-album-001-jay/anchors/*-words.json (whisperx small int8 + zh wav2vec2 align)\n'
           'Structure face (POOL-0019) honestly blocked: madmom/allin1 build fused out after 3 attempts\n'
           'In-production songs (anjing/jiandanan/kaibuliaokou/qingtian) await audio Taildrop per card note\n'
           'Machine: bm-b r992 headless round\n') % (len(added), len(files), len(added))
    with open(msgfile, 'w', encoding='utf-8') as fh:
        fh.write(msg)

    def mkcommit(parent):
        r = subprocess.run(['git', '-C', GRP, 'commit-tree', tree, '-p', parent, '-F', msgfile],
                           capture_output=True, env=env, timeout=60)
        return r.stdout.decode('utf-8', 'replace').strip()

    newc = mkcommit(tip)
    print('COMMIT=%s' % newc)
    if len(newc) != 40:
        print('FATAL commit-tree')
        sys.exit(2)
    r = subprocess.run(['git', '-C', GRP, 'push', 'origin', newc + ':refs/heads/main'],
                       capture_output=True, timeout=180)
    out = (r.stdout + r.stderr).decode('utf-8', 'replace')
    print('PUSH rc=%d %s' % (r.returncode, out[:200].replace('\n', ' | ')))
    if r.returncode != 0:
        print('race retry on fresh tip...')
        git('fetch', 'origin')
        rc, tip2 = git('rev-parse', 'origin/main')
        newc = mkcommit(tip2)
        r = subprocess.run(['git', '-C', GRP, 'push', 'origin', newc + ':refs/heads/main'],
                           capture_output=True, timeout=180)
        print('PUSH_RETRY rc=%d commit=%s' % (r.returncode, newc))
        if r.returncode != 0:
            print('PUSH_FAILED - commits stay local (none); rerun next round')

if added and newc:
    git('fetch', 'origin')
    rc, otip = git('rev-parse', 'origin/main')
    ok = 0
    for rel, sha in added:
        rcv, osha = git('rev-parse', otip + ':' + rel)
        if osha == sha:
            ok += 1
        else:
            print('CONTENT-MISMATCH %s origin=%s mine=%s' % (rel, osha[:12], sha[:12]))
    print('CONTENT_CHECK %d/%d on origin tip %s' % (ok, len(added), otip[:12]))

def blob_sha256(ref):
    r = subprocess.run(['git', '-C', GRP, 'show', ref], capture_output=True, timeout=60)
    return hashlib.sha256(r.stdout).hexdigest()

d19d = blob_sha256('origin/main:docs/decisions.md')
d19o = blob_sha256('origin/main:docs/orders.md')
print('D19_DECISIONS_SHA=%s DELTA=%s' % (d19d, d19d != D19_DEC_KEY))
print('D19_ORDERS_SHA=%s DELTA=%s' % (d19o, d19o != D19_ORD_KEY))
print('ANCHOR_SURGERY_DONE')
