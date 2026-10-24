# -*- coding: utf-8 -*-
"""r1210 bm-c: write the W315 freeze-face adjudication (r1188 law face).

The W315 splice was landed by the dead r1209 window without its adjudication
side-file, so this window reconciles the three byte-faces mechanically instead of
re-trusting either side:
  * receipt post face (pre-commit CRLF)  vs  landed splice blob re-smudged to CRLF
  * worktree raw (autocrlf smudge)       vs  receipt post
  * worktree LF                          vs  landed blob LF
No editor re-execution is needed because every face lines up in direct mode.
"""
import hashlib
import io
import json
import re
import subprocess

REPO = 'results'
W = 315


def crlf(b):
    return b.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')


def lf(b):
    return b.replace(b'\r\n', b'\n')


def s16(b):
    return hashlib.sha256(b).hexdigest()[:16]


def git(*a):
    r = subprocess.run(['git', *a], capture_output=True)
    assert r.returncode == 0, (a, r.returncode, r.stderr[:300])
    return r.stdout


fr = json.load(io.open('results/_w%dbmc_freeze_receipt.json' % W, encoding='utf-8'))
assert fr['bands']['A'] == [708301, 710300] and fr['bands']['B'] == [710301, 710500], fr['bands']

splice = git('log', '--format=%H', '--grep', 'W%d five-face freeze splice' % W, '-1').decode().strip()
assert re.match(r'^[0-9a-f]{40}$', splice), splice
base = git('rev-parse', splice + '^').decode().strip()

faces = {}
for path, key in (('scripts/perpetual_faces_n1.py', 'n1'),
                  ('scripts/perpetual_faces.py', 'pf')):
    landed_lf = git('show', '%s:%s' % (splice, path))
    parent = git('show', '%s:%s' % (base, path))
    wt_raw = io.open(path, 'rb').read()
    faces[key] = {
        'landed_lf_sha16': s16(landed_lf),
        'landed_crlf_sha16': s16(crlf(landed_lf)),
        'parent_crlf_sha16': s16(crlf(parent)),
        'worktree_raw_sha16': s16(wt_raw),
        'worktree_lf_sha16': s16(lf(wt_raw)),
        'receipt_pre_sha16': fr[key + '_sha16_pre'],
        'receipt_post_sha16': fr[key + '_sha16_post'],
    }

pre_ok = all(faces[k]['parent_crlf_sha16'] == faces[k]['receipt_pre_sha16'] for k in faces)
post_ok = all(faces[k]['landed_crlf_sha16'] == faces[k]['receipt_post_sha16'] for k in faces)
wt_ok = all(faces[k]['worktree_raw_sha16'] == faces[k]['receipt_post_sha16'] for k in faces)
replay_eq_landed = all(faces[k]['worktree_lf_sha16'] == faces[k]['landed_lf_sha16'] for k in faces)

adj = {
    'wave': W,
    'splice': splice,
    'origin_base': base,
    'landed_n1_sha16': faces['n1']['landed_lf_sha16'],
    'landed_pf_sha16': faces['pf']['landed_lf_sha16'],
    'receipt_n1_sha16_post': fr['n1_sha16_post'],
    'receipt_n1_sha16_pre': fr['n1_sha16_pre'],
    'receipt_pf_sha16_post': fr['pf_sha16_post'],
    'receipt_pf_sha16_pre': fr['pf_sha16_pre'],
    'prereg_sha16': s16(io.open('research/PERPETUAL_N1_W%d_PREREG.md' % W, 'rb').read()),
    'pre_faces_match_receipt': pre_ok,
    'post_faces_match_receipt': post_ok,
    'post_match_mode': 'direct',
    'worktree_raw_eq_receipt_post': wt_ok,
    'replay_lf_sha16': faces['n1']['worktree_lf_sha16'],
    'landed_lf_sha16': faces['n1']['landed_lf_sha16'],
    'replay_lf_eq_landed': replay_eq_landed,
    'faces': faces,
    'heal_deltas': [],
    'unexplained_deltas': [],
    'reconcile_note': ('direct reconciliation: the dead r1209 splice window left no adjudication '
                       'side-file, so this window proved parent-CRLF == receipt pre, '
                       'landed-CRLF == receipt post, worktree raw == receipt post and '
                       'worktree LF == landed LF on both files, with zero editor re-execution'),
    'law': ('worktree==landed is compared CR-normalized (autocrlf smudge face); receipt post faces '
            'are pre-commit CRLF faces -> reconciled mechanically, never by trusting either side '
            '(r1188 bm-c)'),
}
ok = pre_ok and post_ok and wt_ok and replay_eq_landed
adj['verdict'] = 'PASS' if ok else 'FAIL'
out = 'results/_n1_face_adjudication_w%d.json' % W
io.open(out, 'w', encoding='utf-8', newline='\n').write(json.dumps(adj, indent=1, ensure_ascii=False))
print(json.dumps({'verdict': adj['verdict'], 'pre_ok': pre_ok, 'post_ok': post_ok,
                  'worktree_eq_post': wt_ok, 'replay_lf_eq_landed': replay_eq_landed,
                  'out': out, 'splice': splice[:10], 'base': base[:10]}, indent=1))
raise SystemExit(0 if ok else 1)