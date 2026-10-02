import subprocess, os, json
os.chdir(r'K:\Fluxgroup\FluxGroup\quant\bigmoney')
G = r'C:\Program Files\Git\bin\git.exe'

def git(*a):
    r = subprocess.run([G] + list(a), capture_output=True, cwd=os.getcwd())
    return r.returncode, r.stdout.decode('utf-8', 'replace'), r.stderr.decode('utf-8', 'replace')

# 1. science-payload diff disclosure before discarding my variant
mine = json.load(open('results/perpetual_faces/n1_w108_results.json', encoding='utf-8'))
rc, out, err = git('show', 'origin/main:results/perpetual_faces/n1_w108_results.json')
o = json.loads(out)
sci_keys = ['null_pool_cumulative', 'skill_line_v2_k_lift', 'families']
same_sci = all(json.dumps(mine.get(k), sort_keys=True) == json.dumps(o.get(k), sort_keys=True) for k in sci_keys)
print('science_payload_identical', same_sci)
print('mine_machine', mine['audit']['machine'], 'origin_machine', o['audit']['machine'])
print('mine_ledger_total', mine['science_gates']['ledger']['total'], 'origin_ledger_total', o['science_gates']['ledger']['total'])

# 2. yield surgery: reset to origin, keep local rides only
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
print('checkout_count', len(co), 'untracked', len(untracked))
print('untracked_list', untracked)
for i in range(0, len(co), 50):
    rc2, out2, err2 = git('checkout', '--', *co[i:i + 50])
    if rc2 != 0:
        print('CHUNK FAIL', i, rc2, err2[:300])
print('checkout done')
rc, out, err = git('status', '--porcelain')
print('--- post status ---')
print(out[:1200])
