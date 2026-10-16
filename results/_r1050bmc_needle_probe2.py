# -*- coding: utf-8 -*-
import io
src = io.open('results/_w251bmc_freeze_edits.py', encoding='utf-8').read()

# 1. full band-facts block (raw)
i = src.find('"        # band facts (law sec.4 W251 row)')
j = src.find('no staircase-equality assumption);', i)
print('==== BANDFACTS RAW (%d..%d)' % (i, j))
print(repr(src[i:j+len('no staircase-equality assumption);')]))

# 2. B assert block messages (raw)
k = src.find('B 13-HOP WALK face')
print('==== BASSERT RAW at', k)
print(repr(src[max(0,k-200):k+900]))

# 3. A clean assert + mutual exclusion (raw)
m = src.find('A window must be CLEAN')
print('==== ACLEAN RAW at', m)
print(repr(src[max(0,m-100):m+700]))
n = src.find('same-freeze mutual exclusion')
print('==== EXCL RAW at', n)
print(repr(src[max(0,n-200):n+400]))
