# -*- coding: utf-8 -*-
# r898: fix line 463 string closure in the W210 takeover freeze editor
p = 'results/_w210bmc_takeover_freeze_edits.py'
raw = open(p, encoding='utf-8', newline='').read()
lines = raw.split('\n')
i = 462  # 0-based -> display line 463
l = lines[i]
print('BEFORE:', repr(l[-30:]))
BS = chr(92)  # backslash
DQ = chr(34)  # double quote
# desired tail: ...W{wprev}" + closing DQ + ,
expected_tail = 'W{wprev}' + BS + DQ + ','
assert l.endswith(expected_tail), 'unexpected tail state'
lines[i] = l[:-1] + DQ + ','
print('AFTER:', repr(lines[i][-30:]))
open(p, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
print('fixed')
