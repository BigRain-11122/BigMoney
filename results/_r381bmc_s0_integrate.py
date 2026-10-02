import subprocess, os
os.chdir(r'K:\Fluxgroup\FluxGroup\quant\bigmoney')
G = r'C:\Program Files\Git\bin\git.exe'

def git(*a):
    r = subprocess.run([G] + list(a), capture_output=True, cwd=os.getcwd())
    return r.returncode, r.stdout.decode('utf-8', 'replace'), r.stderr.decode('utf-8', 'replace')

rc, out, err = git('reset', '--mixed', 'origin/main')
print('reset rc', rc, err[:200])
rc, out, err = git('status', '--porcelain')
keep = {'results/autofill_state.bm-c.json', 'results/dispatcher_state.bm-c.json',
        'results/saturation_engine/face_bm-c.json', 'results/saturation_engine_state.bm-c.json'}
co = []
untracked = []
for line in out.split('\n'):
    if not line.strip():
        continue
    st = line[:2]
    path = line[3:].strip('"')
    if st == '??':
        untracked.append(path)
        continue
    if path in keep:
        continue
    co.append(path)
print('checkout_count', len(co), 'untracked', len(untracked))
for i in range(0, len(co), 50):
    rc, out, err = git('checkout', '--', *co[i:i + 50])
    if rc != 0:
        print('CHUNK FAIL', i, rc, err[:300])
print('checkout done')
rc, out, err = git('status', '--porcelain')
print('--- post status ---')
print(out[:2000])
