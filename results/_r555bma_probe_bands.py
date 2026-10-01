"""r555 helper: extract W44/45/46 seed bases + N1_BANDS tail from origin script."""
import subprocess, re

src = subprocess.check_output(['git', 'show', 'origin/main:scripts/perpetual_faces_n1.py']).decode('utf-8')
for w in (44, 45, 46):
    i = src.find('%d: {"batch"' % w)
    if i < 0:
        print(w, 'entry NOT FOUND')
        continue
    j = src.find('shard_subdir', i)
    seg = src[i:j]
    a = re.search(r'a_seed_base["\s:]+([\d_]+)', seg)
    b = re.search(r'b_exit_seed_base["\s:]+([\d_]+)', seg)
    print('W%d A_base=%s B_base=%s' % (w, a.group(1) if a else '?', b.group(1) if b else '?'))

# N1_BANDS dict: find its definition and print keys 44..46
i = src.find('N1_BANDS = {')
if i >= 0:
    j = src.find('}', src.find('}', i) + 1)  # crude; just print a window
    print('--- N1_BANDS window ---')
    print(src[i:i+1500])
