"""r555 helper: inspect bm-b's W47 registration on origin (bands + owner + prereg anchor)."""
import subprocess, re

src = subprocess.check_output(['git', 'show', 'origin/main:scripts/perpetual_faces.py']).decode('utf-8')
i = src.find('47: {')
print('N1_BANDS[47] (origin):')
print(src[i:i + 170])

n1 = subprocess.check_output(['git', 'show', 'origin/main:scripts/perpetual_faces_n1.py']).decode('utf-8')
j = n1.find('47: {"batch"')
seg = n1[j:j + 1400]
a = re.search(r'a_seed_base["\s:]+([\d_]+)', seg)
b = re.search(r'b_exit_seed_base["\s:]+([\d_]+)', seg)
eo = re.search(r'engine_owner["\s:]+(\w+)', seg)
print('WAVE_CONFIGS[47]: A_base=%s B_base=%s engine_owner=%s' % (
    a.group(1) if a else '?', b.group(1) if b else '?', eo.group(1) if eo else '?'))

# their prereg anchor + K projection
pr = subprocess.check_output(['git', 'show', 'origin/main:research/PERPETUAL_N1_W47_PREREG.md']).decode('utf-8')
m = re.search(r'锚 \*\*(-[\d.]+)\*\*', pr)
print('prereg mu anchor:', m.group(1) if m else '?')
for pat in ('0.085749', '0.240870', '0.3214', '45_001', '137_004', '465,748', '101,320'):
    print(' prereg contains %r:' % pat, pat in pr)
# their shard products on origin
out = subprocess.check_output(['git', 'ls-tree', 'origin/main', 'results/p2cal_ext/n1_w47/']).decode('utf-8')
print('origin n1_w47 products:', len(out.strip().splitlines()))
print(out)
