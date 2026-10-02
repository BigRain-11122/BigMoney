import subprocess

out = subprocess.check_output(['git', 'show', 'origin/main:scripts/perpetual_faces_n1.py'])
i = out.find(b'# --- W101 materializer face')
seg = out[i:i+9000]
k = seg.find(b'[w for w in range(16, 100)]')
print(seg[k-700:k+500].decode('utf-8', 'replace'))
