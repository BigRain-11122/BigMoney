import subprocess

# Their version of n1 from origin
out = subprocess.check_output(['git', 'show', 'origin/main:scripts/perpetual_faces_n1.py'])
data = out
i = data.find(b'# --- W101 materializer face')
print('W101 leg at', i)
seg = data[i:i+7000]
# find the priors assertion and dep loop
import re
for pat in (rb'_priors101[^\n]*', rb'assert _priors101[\s\S]{0,400}', rb'for _depw in range[^\n]*'):
    for m in re.finditer(pat, seg):
        print('---', m.group(0)[:420])
# their W101 frag tail
j = data.find(b'"W101 row, r583 bm-a] "')
print('their frag tail at', j, repr(data[j-60:j+40]) if j > 0 else 'check split')
# their canon bullet order check
out2 = subprocess.check_output(['git', 'show', 'origin/main:research/PERPETUAL_FACES.md']).decode('utf-8')
k99 = out2.find('- N1 \u6ce299')
k101 = out2.find('- N1 \u6ce2101')
print('canon W99 at', k99, 'W101 at', k101, 'order ok:', 0 < k99 < k101)
# their pf entries
out3 = subprocess.check_output(['git', 'show', 'origin/main:scripts/perpetual_faces.py'])
p99 = out3.find(b'99: {"a": (241_004')
p101 = out3.find(b'101: {"a": (245_004')
print('pf W99 at', p99, 'W101 at', p101)
