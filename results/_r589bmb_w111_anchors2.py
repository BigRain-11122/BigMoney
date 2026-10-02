# -*- coding: utf-8 -*-
"""r589 bm-b W111 freeze-window anchor dump 2 (read-only)."""
t2 = open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()

# 1. full W110 config entry
j = t2.find('110: {"batch"')
k = t2.find('111:', j)  # next entry marker if any
end = t2.find('"engine_owner": "bm-a"},', j)
end2 = t2.find('\n', end + 1)
print('=== W110 config entry FULL ===')
print(repr(t2[j-24:end2+1]))
print()

# 2. W110 selftest leg tail + T-141 anchor
m = t2.find('# --- W110 materializer face')
if m == -1:
    m = t2.find('W110 materializer face')
    m = t2.rfind('# ---', 0, m)
n = t2.find('# --- T-141 s2 lane face')
print('=== between W110 leg start and T-141 face ===')
print('W110 leg starts at', m, 'T-141 face at', n)
seg = t2[m:n]
print('leg length:', len(seg))
print('=== leg tail 300 chars ===')
print(repr(seg[-300:]))
print()

# 3. W110 summary segment (edit5 anchor): find 'sec.4 W110 row, r589' summary occurrence
s = t2.find('sec.4 W110 row, r589')
# the summary is the second occurrence of 'W110 materializer face' string
first = t2.find('W110 materializer face')
second = t2.find('W110 materializer face', first + 1)
sstart = t2.rfind('"+ W110 materializer face', 0, second + 50)
if sstart == -1:
    sstart = t2.rfind('W110 materializer face', 0, second)
    sstart = t2.rfind('"', 0, sstart)
send = t2.find('"+ T-141 s2 ', sstart)
print('=== summary segment region ===')
print(repr(t2[sstart-120:send+40]))
