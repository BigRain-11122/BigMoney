# -*- coding: utf-8 -*-
# r877 bm-c: S6 runner lineage clone (r736 law) -- verbatim clone of the
# r869 runner with round-ref replacement r869->r877, asserts applied.
import io

SRC = r'results\_r869bmc_s6_runner.ps1'
DST = r'results\_r877bmc_s6_runner.ps1'
with io.open(SRC, 'r', encoding='utf-8') as fh:
    t = fh.read()
n = t.count('r869')
assert n == 2, 'round-ref occurrence count != 2 (got %d)' % n
t2 = t.replace('r869', 'r877')
assert 'r869' not in t2 and t2.count('r877') >= 2
assert len(t) == len(t2), 'length drift in clone'
with io.open(DST, 'w', encoding='utf-8', newline='') as fh:
    fh.write(t2)
with io.open(DST, 'r', encoding='utf-8') as fh:
    back = fh.read()
assert back == t2, 'write-back mismatch'
print('clone OK: _r877bmc_s6_runner.ps1 written (44 legs, r869->r877 x2)')
