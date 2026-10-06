# -*- coding: utf-8 -*-
import os

def norm(p):
    if not os.path.exists(p):
        return None
    return open(p, 'rb').read().replace(b'\r\n', b'\n').replace(b'\r', b'\n')

for hook in ('pre-commit', 'pre-push'):
    live = norm(os.path.join('.git', 'hooks', hook))
    canon = norm(os.path.join('Tools', 'git-hooks', hook))
    print(hook, 'live:', 'MISSING' if live is None else len(live), '| canon:', 'MISSING' if canon is None else len(canon), '| identical:', live == canon)
