# -*- coding: utf-8 -*-
raw = open('research/PERPETUAL_FACES.md', encoding='utf-8').read()
anchor = '\n- 每波 finalize 后：`science_gates.append_ledger` 落行'
print('anchor count:', raw.count(anchor))
i = raw.find('- N1 波109（')
j = raw.find(anchor)
print('W109 canon row at', i, '| anchor at', j)
print('tail before anchor:', repr(raw[max(0,j-120):j+60]))
