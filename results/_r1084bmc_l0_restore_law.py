# r1084-continuation bm-c: piece-3c -- law-preservation restore: CEO 本地故障→云端恢复律 (group-wide CEO production law,
# unique L0 copy, over-matched by SIGS path heuristic in the 3b sweep) copied back from quarantine into L0 User section.
# Quarantine stays append-only (archive copy retained); L0 regains the live law. Zero net loss either side.
import io

L0 = r'C:\Users\Dasheng\.codely-cli\CODELY.md'
QUAR = r'C:\Users\Dasheng\memory\topics\cross-machine-quarantine.md'
NEEDLE = '本地故障→云端恢复律'

with io.open(QUAR, 'r', encoding='utf-8') as f:
    qlines = f.read().split('\n')
law = [l for l in qlines if l.startswith('- [') and NEEDLE in l]
assert law, 'no law line found in quarantine'
assert all(l == law[0] for l in law), 'quarantine copies diverge, abort'
lawline = law[-1]  # 2 copies expected: dead-window 07:59 sweep + post-restore 3b sweep (identical bytes)

with io.open(L0, 'r', encoding='utf-8') as f:
    l0 = f.read()
assert NEEDLE not in l0, 'law already present in L0, abort (no double-add)'
lines = l0.split('\n')
out = []
inserted = False
for i, l in enumerate(lines):
    if not inserted and l.strip() == '### Feedback':
        out.append(lawline)
        out.append('')
        inserted = True
    out.append(l)
if not inserted:  # no Feedback header found: append at end
    out.append(lawline)
    inserted = True
with io.open(L0, 'w', encoding='utf-8', newline='') as f:
    f.write('\n'.join(out))

import os
print('restored law line %dB -> L0 bytes=%d entries=%d' % (len(lawline.encode('utf-8')), os.path.getsize(L0), sum(1 for x in out if x.startswith('- ['))))
print('LAW-RESTORED:', lawline[:120])
