import subprocess, os
os.chdir(r'K:\Fluxgroup\FluxGroup\quant\bigmoney')
G = r'C:\Program Files\Git\bin\git.exe'

def git(*a):
    r = subprocess.run([G] + list(a), capture_output=True, cwd=os.getcwd())
    return r.returncode, r.stdout.decode('utf-8', 'replace'), r.stderr.decode('utf-8', 'replace')

keep = {'results/autofill_state.bm-c.json', 'results/dispatcher_state.bm-c.json',
        'results/saturation_engine/face_bm-c.json', 'results/saturation_engine_state.bm-c.json'}
rc, out, err = git('reset', '--mixed', 'origin/main')
print('reset rc', rc, err[:150])
rc, out, err = git('status', '--porcelain')
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
print('checkout_count', len(co), 'untracked', untracked)
for i in range(0, len(co), 50):
    rc2, out2, err2 = git('checkout', '--', *co[i:i + 50])
    if rc2 != 0:
        print('CHUNK FAIL', i, rc2, err2[:300])
print('checkout done')
rc, out, err = git('status', '--porcelain')
print('--- post ---')
print(out[:800])
