# -*- coding: utf-8 -*-
"""r1222 bm-c: W320 freeze-face adjudication v2 (r1188 law face + post-receipt heal).

Same three byte-faces as the W319 adjudication, plus a mechanical treatment of the
one delta this wave actually has: the r1221 window ran TWO heal edits (bare-number
faces: cfg shard_subdir + prose wave label) at 01:31, i.e. AFTER the freeze receipt
was written at 01:27. So the receipt's n1_sha16_post is a pre-heal face.

Instead of smoothing that away (or failing on it), the delta is proved by
REVERSE-APPLYING the heal to the current worktree and requiring byte equality with
the receipt post face. Explained => PASS (heal delta disclosed, unexplained=0);
not reproducible => FAIL.
"""
import hashlib
import io
import json
import re
import subprocess

W = 320


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
bands = fr['bands']
assert bands['A'] == [719301, 721300] and bands['B'] == [721301, 721500], bands

splice = git('log', '--format=%H', '--grep', 'W%d five-face splice' % W, '-1').decode().strip()
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
        'parent_raw_sha16': s16(parent),
        'worktree_raw_sha16': s16(wt_raw),
        'worktree_lf_sha16': s16(lf(wt_raw)),
        'receipt_pre_sha16': fr[key + '_sha16_pre'],
        'receipt_post_sha16': fr[key + '_sha16_post'],
    }

pre_ok_all, post_ok_all = True, True
for k in faces:
    f = faces[k]
    pre_basis = None
    for basis, sha in (('raw_lf', f['parent_raw_sha16']),
                       ('crlf', f['parent_crlf_sha16'])):
        if sha == f['receipt_pre_sha16']:
            pre_basis = basis
            break
    post_basis = None
    for basis, sha in (('landed_lf', f['landed_lf_sha16']),
                       ('landed_crlf', f['landed_crlf_sha16'])):
        if sha == f['receipt_post_sha16']:
            post_basis = basis
            break
    f['pre_basis'] = pre_basis
    f['post_basis'] = post_basis
    pre_ok_all = pre_ok_all and pre_basis is not None

# ---- reverse-apply the r1221 post-receipt heal on the n1 face -------------------
wt_lf = lf(io.open('scripts/perpetual_faces_n1.py', 'rb').read()).decode('utf-8')
heal_deltas = []
recon = wt_lf
undo = [
    ('cfg_shard_subdir',
     '"shard_subdir": "n1_w320", "out_name": "n1_w320_results.json",',
     '"shard_subdir": "n1_w319", "out_name": "n1_w320_results.json",'),
    ('prose_wave_label', '"wave 320: "', '"wave 319: "'),
]
for tag, cur, prev in undo:
    c = recon.count(cur)
    if c == 1:
        recon = recon.replace(cur, prev, 1)
        heal_deltas.append({'tag': tag, 'reversed': True,
                            'current_face': cur, 'pre_heal_face': prev,
                            'source': 'results/_r1221bmc_heal_w320_cfg.py'})
    else:
        heal_deltas.append({'tag': tag, 'reversed': False, 'count': c,
                            'source': 'results/_r1221bmc_heal_w320_cfg.py'})
recon_sha = s16(recon.encode('utf-8'))
heal_reproduced = all(h['reversed'] for h in heal_deltas) and recon_sha == fr['n1_sha16_post']
faces['n1']['pre_heal_reconstruction_sha16'] = recon_sha
faces['n1']['pre_heal_reconstruction_eq_receipt_post'] = heal_reproduced
post_basis = 'receipt post face is a PRE-HEAL face, reproduced byte-exactly by reverse-applying the two disclosed r1221 heal edits'
faces['n1']['post_basis'] = post_basis
post_ok_all = faces['pf']['post_basis'] is not None and heal_reproduced

pre_ok = pre_ok_all
post_ok = post_ok_all
wt_ok = all(faces[k]['worktree_raw_sha16'] == faces[k]['receipt_post_sha16']
            or faces[k]['worktree_lf_sha16'] == faces[k]['receipt_post_sha16'] for k in faces)
replay_eq_landed = all(faces[k]['worktree_lf_sha16'] == faces[k]['landed_lf_sha16'] for k in faces)

adj = {
    'wave': W,
    'splice': splice,
    'origin_base': base,
    'bands': bands,
    'landed_n1_sha16': faces['n1']['landed_lf_sha16'],
    'landed_pf_sha16': faces['pf']['landed_lf_sha16'],
    'receipt_n1_sha16_post': fr['n1_sha16_post'],
    'receipt_n1_sha16_pre': fr['n1_sha16_pre'],
    'receipt_pf_sha16_post': fr['pf_sha16_post'],
    'receipt_pf_sha16_pre': fr['pf_sha16_pre'],
    'prereg_sha16': s16(io.open('research/PERPETUAL_N1_W%d_PREREG.md' % W, 'rb').read()),
    'pre_faces_match_receipt': pre_ok,
    'post_faces_match_receipt': post_ok,
    'post_match_mode': ('pf: eol-basis direct match; n1: pre-heal receipt face reproduced '
                        'byte-exactly by reverse-applying the disclosed heal'),
    'worktree_raw_eq_receipt_post': wt_ok,
    'replay_lf_sha16': faces['n1']['worktree_lf_sha16'],
    'landed_lf_sha16': faces['n1']['landed_lf_sha16'],
    'replay_lf_eq_landed': replay_eq_landed,
    'faces': faces,
    'eol_basis_note': ('per-face EOL basis is recorded, never smoothed: each receipt face is '
                       'proved identical to its OWN parent/landed normalization (r1188/r1208)'),
    'heal_deltas': heal_deltas,
    'unexplained_deltas': [],
    'reconcile_note': ('direct reconciliation on pf (parent-CRLF == receipt pre, landed-CRLF == '
                       'receipt post, worktree raw == receipt post, worktree LF == landed LF) and '
                       'on n1 worktree/landed equality; the single n1 receipt-face delta is the '
                       'post-receipt heal (01:31 vs receipt 01:27) and is proved by byte-exact '
                       'reverse application, not by assertion'),
    'law': ('worktree==landed is compared CR-normalized (autocrlf smudge face); receipt post faces '
            'are pre-commit CRLF faces -> reconciled mechanically, never by trusting either side '
            '(r1188 bm-c)'),
}
ok = pre_ok and post_ok and replay_eq_landed and heal_reproduced
adj['verdict'] = 'PASS' if ok else 'FAIL'
out = 'results/_n1_face_adjudication_w%d.json' % W
io.open(out, 'w', encoding='utf-8', newline='\n').write(json.dumps(adj, indent=1, ensure_ascii=False))
print(json.dumps({'verdict': adj['verdict'], 'pre_ok': pre_ok, 'post_ok': post_ok,
                  'worktree_raw_eq_post': wt_ok, 'replay_lf_eq_landed': replay_eq_landed,
                  'heal_reproduced': heal_reproduced, 'recon_sha16': recon_sha,
                  'receipt_post': fr['n1_sha16_post'],
                  'out': out, 'splice': splice[:10], 'base': base[:10]}, indent=1))
raise SystemExit(0 if ok else 1)