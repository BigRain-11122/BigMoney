# -*- coding: utf-8 -*-
# r1068 bm-c: raw-blob worktree restore for pf/n1 (post-rebase autocrlf smudge
# face: rebase checkout wrote CRLF worktree copies -> raw-byte sha16 diverged
# from landed LF blobs + freeze receipt; git content identical (diff empty);
# restore exact landed bytes via git cat-file raw write, bypassing smudge)
import hashlib
import subprocess

COMMIT = 'e1a94b335'
for p in ['scripts/perpetual_faces.py', 'scripts/perpetual_faces_n1.py']:
    blob = subprocess.run(['git', 'show', f'{COMMIT}:{p}'], capture_output=True).stdout
    assert len(blob) > 1000, f'blob read fail {p}'
    with open(p, 'wb') as fh:
        fh.write(blob)
    h = hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
    print(p, '->', h)
