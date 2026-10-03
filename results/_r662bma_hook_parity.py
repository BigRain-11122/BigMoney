# -*- coding: utf-8 -*-
"""r662 bm-a S7 hook parity probe: .git/hooks vs Tools/git-hooks (CR-normalized)."""
import os, sys

def norm(p):
    if not os.path.exists(p):
        return None
    with open(p, 'rb') as f:
        return f.read().replace(b'\r', b'')

pairs = [
    (r'.git\hooks\pre-commit', r'Tools\git-hooks\pre-commit', 'pre-commit'),
    (r'.git\hooks\pre-push', r'Tools\git-hooks\pre-push', 'pre-push'),
]
rc = 0
for local, canon, name in pairs:
    a, b = norm(local), norm(canon)
    if a is None:
        verdict = 'MISSING'
        rc = 1
    elif a == b:
        verdict = 'MATCH'
    else:
        verdict = 'DRIFT'
        rc = 1
    print('%s: %s' % (name, verdict))
sys.exit(rc)
