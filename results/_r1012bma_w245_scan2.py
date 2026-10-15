# -*- coding: utf-8 -*-
# r1012 bm-a: scan W244 editor for upstream stat literals + round-number
# narrative context (for W245 gen Phase B table construction)
import io, re
t = io.open('results/_w244bma_freeze_edits.py', encoding='utf-8').read()
lines = t.splitlines()

pats = ['958,935', '958_935', '532,520', '532_520', '-0.10', '-0.092', '-0.1039',
        '0.2412', '0.2450', 'p95', 'se_mu', 'K-lift', 'k_lift', '1.193',
        'r1004', 'r1005', 'r1006', 'r1007', 'r1008', 'r1009', 'r1003', 'r1002',
        'r1001', '08df387e0', '260ffd3f8', '70141bc22', 'MSG-20261015',
        '06:1x', '06:58', '07:1x', '07:4x', '01:4x', '20:4x', 'thirty-third',
        'W244', '945,735', '947,935']
seen = set()
for i, l in enumerate(lines):
    for p in pats:
        if p in l and (i, p) not in seen:
            seen.add((i, p))
            print('%4d [%s] %s' % (i + 1, p, l.strip().encode('unicode_escape').decode('ascii')[:150]))
            break
print('---counts---')
for p in ['958,935', '958_935', '532,520', '532_520', 'r1004', 'r1005', 'r1006',
          'r1007', 'MSG-20261015-0206', '08df387e0', '260ffd3f8', '70141bc22',
          'thirty-third consecutive', 'fifth consecutive seed-gap',
          'gap face sixth', '233 + candidate', 'bma_ordinal=126', '126th']:
    print('%-28s %d' % (p, t.count(p)))
