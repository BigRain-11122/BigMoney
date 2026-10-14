# -*- coding: utf-8 -*-
import io
t = io.open('_r1014bmc_mv_full_shots.py', encoding='utf-8').read()

def block(marker):
    i = t.find(marker)
    if i < 0:
        return None
    j = i
    while True:
        j = t.find('\n', j + 1)
        if j == -1:
            return t[i:]
        seg = t[i:j]
        if seg.count('(') == seg.count(')') and seg.rstrip().endswith(')'):
            return seg
    return t[i:]

print(block('HIM = ('))
print()
print(block('ERA = (') or block('ERA=') or 'NO ERA BLOCK')
print()
for key in ('ANTI_K', 'HER = ('):
    b = block(key)
    if b:
        print(b)
        print()
