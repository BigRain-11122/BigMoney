import subprocess, re

out = subprocess.check_output(['git', 'show', 'origin/main:scripts/perpetual_faces_n1.py'])
i = out.find(b'# --- W101 materializer face')
seg = out[i:i+9000]
for ln in seg.split(b'\n'):
    s = ln.strip()
    if (s.startswith(b'for _depw') or b'_priors' in s or s.startswith(b'assert _priors')
            or s.startswith(b'_priors') or (s.startswith(b'assert') and b'prior-wave' in s)
            or s.startswith(b'for wprev') or b'range(16,' in s or b'range(17,' in s):
        print(ln.decode('utf-8', 'replace'))
print('=== dep-loop + priors context done ===')
# find the exact priors assert block
m = re.search(rb'_priors\d+\s*=\s*sorted[\s\S]{0,500}?assert[\s\S]{0,400}?\)\n', seg)
if m:
    print(m.group(0).decode('utf-8', 'replace'))
