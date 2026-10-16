# -*- coding: utf-8 -*-
# r1046 bm-c: verify W250 print-face heal (rows 68->69) delta face.
# Method: locate the disclosed heal line in W250 block; rebuild pre-heal
# face by reverting 69->68 on that single line and re-hash; must equal
# receipt n1_sha16_post (050d7e70375727f2) = proves heal is the ONLY delta.
import hashlib
import io

t = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = t.find('250: {"batch": "PERPETUAL-N1-W250"')
seg = t[i:i + 2500]
faces = [l.strip() for l in seg.splitlines() if '68' in l or '69' in l]
print('W250 68/69 faces:')
for f in faces:
    print('  ', f)

for line in seg.splitlines():
    if '69' in line and '68' not in line:
        pre = t.replace(line, line.replace('69', '68', 1), 1)
        sha = hashlib.sha256(pre.encode('utf-8')).hexdigest()[:16]
        print('revert-line:', line.strip())
        print('pre-heal-sha16:', sha)
        print('MATCH-RECEIPT:', sha == '050d7e70375727f2')
        break
print('n1_now_sha16:', hashlib.sha256(t.encode('utf-8')).hexdigest()[:16])
