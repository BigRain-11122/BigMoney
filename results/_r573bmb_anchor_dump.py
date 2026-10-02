import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
t2 = open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = t2.find('r363 bm-c] "')
print('=== W78 summary tail ===')
print(repr(t2[i:i + 120]))
m = t2.count('r363 bm-c] "')
print('count r363 bm-c] =', m)
p = open('scripts/perpetual_faces.py', encoding='utf-8').read()
import re
cnt = len(re.findall(r'engine_owner==?"bm-b"', p))
rows = [w for w in range(2, 100) if ('    %d: {"a"' % w) in p]
print('pf registered rows:', rows)
import subprocess
