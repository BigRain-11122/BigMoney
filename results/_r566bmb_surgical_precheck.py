# -*- coding: utf-8 -*-
"""r566 bm-b surgical push pre-check: payload intersection vs origin new commits."""
import subprocess

def out(*a):
    return subprocess.check_output(list(a), text=True)

BASE = out('git', 'merge-base', 'HEAD', 'origin/main').strip()
print('merge-base:', BASE)
mine = set(out('git', 'diff', '--name-only', BASE, 'HEAD').splitlines())
theirs = set(out('git', 'diff', '--name-only', BASE, 'origin/main').splitlines())
print('my payload files:', len(mine))
print('their files:', len(theirs))
inter = sorted(mine & theirs)
print('INTERSECTION (conflict candidates):', inter or '(none)')
