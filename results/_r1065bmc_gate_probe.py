# -*- coding: utf-8 -*-
import io
bs = io.open('results/_r1065bmc_build_editor.py', encoding='utf-8', newline='').read()
i = bs.find('NEW_GATES')
j = bs.find('sect("# ============ structural output gates', i)
print('builder NEW_GATES idx range:', i, j)
print(bs[i:j+220])
print()
print('=== w245_a in builder ===')
k = 0
while True:
    k = bs.find('w245_a', k)
    if k < 0: break
    print('idx', k, ':', repr(bs[max(0,k-150):k+120]))
    k += 1
print()
print('=== w245_a in W259 freeze_edits OUTPUT ===')
try:
    t = io.open('results/_w259bmc_freeze_edits.py', encoding='utf-8', newline='').read()
    print('count:', t.count('w245_a'))
    k = 0
    while True:
        k = t.find('w245_a', k)
        if k < 0: break
        print('idx', k, ':', repr(t[max(0,k-200):k+150]))
        k += 1
except FileNotFoundError:
    print('W259 freeze_edits file not found')
