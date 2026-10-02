# r588 bm-a: restore remaining M-faces (regen twins + other-machine stale faces)
import subprocess

def git(a):
    return subprocess.run(['git'] + a, capture_output=True, text=True, encoding='utf-8', errors='replace')

st = git(['status', '--porcelain']).stdout
m = [l[3:].strip().strip('"') for l in st.splitlines() if 'M' in l[:2]]
print('M count:', len(m))
r = git(['checkout', '--'] + m)
print('restore rc=', r.returncode, (r.stderr or '')[-150:])
st2 = git(['status', '--porcelain']).stdout
lines = [l for l in st2.splitlines() if l.strip()]
print('remaining dirty:', len(lines))
for l in lines[:10]:
    print(' ', l[:100])
