"""r555 helper: dump canon W46 row + W47 projections + N1_BANDS[45/46] registration format."""
import subprocess, re

canon = subprocess.check_output(['git', 'show', 'origin/main:research/PERPETUAL_FACES.md']).decode('utf-8')
lines = canon.splitlines()
# print the W44/W45/W46 rows and any W47 projection lines
for i, l in enumerate(lines):
    if ('W45' in l or 'W46' in l or 'W47' in l) and l.strip().startswith('- N1'):
        print('CANON L%d:' % (i + 1))
        print(l)
        print()

pf = subprocess.check_output(['git', 'show', 'origin/main:research/perpetual_faces.py']).decode('utf-8')
for w in (45, 46):
    i = pf.find('%d: {' % w)
    if i < 0:
        print('N1_BANDS[%d] NOT FOUND by that pattern' % w)
        continue
    j = pf.find('},', i)
    # back up to comment start
    k = pf.rfind('\n\n', 0, i)
    print('==== N1_BANDS[%d] verbatim ====' % w)
    print(pf[max(k, i - 600):j + 2])
    print()
