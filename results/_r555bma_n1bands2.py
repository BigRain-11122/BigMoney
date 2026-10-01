"""r555 helper: dump N1_BANDS W44/W45/W46 entries verbatim from scripts/perpetual_faces.py."""
import subprocess

pf = subprocess.check_output(['git', 'show', 'origin/main:scripts/perpetual_faces.py']).decode('utf-8')
i = pf.find('N1_BANDS = {')
tail = pf[i:]
# find each wave key entry
for w in (44, 45, 46):
    marker = '%d: {' % w
    k = tail.find(marker)
    if k < 0:
        print('W%d marker not found' % w)
        continue
    # comment block starts after previous entry's closing
    cstart = tail.rfind('\n\n', 0, k)
    cend = tail.find('\n    },', k)
    print('==== N1_BANDS entry W%d ====' % w)
    print(tail[max(cstart, k - 900):cend + 8])
    print()
# Also dump the closing of the dict (what follows W46) to know where to insert W47
last = tail.find('46: {')
nxt = tail.find('\n}', last)
print('==== after W46 entry (dict close region) ====')
print(tail[nxt - 200:nxt + 400])
