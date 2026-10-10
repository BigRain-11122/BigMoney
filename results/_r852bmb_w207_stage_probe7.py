# -*- coding: utf-8 -*-
# r852 probe7: resolve the owner contradiction — enumerate all occurrences
import re

n1 = open('scripts/perpetual_faces_n1.py', 'rb').read().decode('utf-8')

for pat in ('205: {"batch"', '"shard_subdir": "n1_w204"', '"prereg": ("research/PERPETUAL_N1_W205_PREREG.md',
            '"engine_owner": "bm-c"},', '204: {"batch"'):
    positions = [m.start() for m in re.finditer(re.escape(pat), n1)]
    print(pat[:50], '-> count', len(positions), 'at', positions[:5])

# show the exact bytes around EACH '205: {"batch"' occurrence
for m in re.finditer(re.escape('205: {"batch"'), n1):
    p = m.start()
    print()
    print('=== occurrence at', p, '===')
    print(repr(n1[p-260:p+120]))
