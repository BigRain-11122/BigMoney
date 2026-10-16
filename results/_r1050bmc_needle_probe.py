# -*- coding: utf-8 -*-
import io
src = io.open('results/_w251bmc_freeze_edits.py', encoding='utf-8').read()
pats = [
    'A=FIRST-CLEAN arithmetic continuation of prior-wave A tail',
    '"B": "13-HOP WALK above own-A',
    'the walk hops past the',
    'W252 A/B same-freeze mutual exclusion',
    'W252 A window must be CLEAN',
    'W252 B window must be CLEAN',
    'must be the first-clean arithmetic continuation',
    'W252 A/B same-freeze',
]
for pat in pats:
    i = src.find(pat)
    print('====', pat[:50], 'at', i)
    if i >= 0:
        print(repr(src[max(0, i-160):i+620]))
