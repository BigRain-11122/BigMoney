import subprocess

out = subprocess.check_output(['git', 'show', 'origin/main:scripts/perpetual_faces_n1.py'])
i = out.find(b'# --- W101 materializer face')
seg = out[i:i+9000]
k = seg.find(b'W100')
while k > 0:
    print('---', seg[max(0,k-200):k+260].decode('utf-8', 'replace'))
    print('========')
    k = seg.find(b'W100', k+1)
    if k > 8000:
        break
