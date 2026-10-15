# r1026 W20 draft probe facts (funnel 2/5) — machine-frozen supply legs
# legs: seed band occupancy / burned-fn inventory / triaxis verdict reads / DSR head / registry location
import io, json, subprocess, os, hashlib, collections

F = {}

# leg0: seed registry location + live keys
reg_paths = ['results/seed_registry/seed_registry.json', 'results/trial_labor_w17/seed_registry.json']
found = None
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in ('.git', '__pycache__', 'node_modules', 'data', 'media')]
    for f in files:
        if f.lower() == 'seed_registry.json':
            found = os.path.join(root, f).replace('\\', '/')
            break
    if found: break
F['seed_registry_path'] = found
if found:
    d = json.load(io.open(found, encoding='utf-8'))
    keys = list(d.keys()) if isinstance(d, dict) else []
    F['seed_registry_keys_n'] = len(keys)
    F['seed_registry_sample'] = keys[:5] + keys[-3:]

# leg1: W20 band occupancy probe (20650000 family, W17 2061/W18 2063/W19 2064 precedent -> W20 = 20650000)
band = 20650000
r = subprocess.run(['python', 'scripts/seed_admit_gate.py', '--base', str(band), '--span', '1'],
                   capture_output=True, text=True, encoding='utf-8', errors='replace')
F['seed_admit_gate_w20_base'] = {'base': band, 'span': 1, 'rc': r.returncode,
                                 'stdout_tail': (r.stdout or '')[-400:], 'stderr_tail': (r.stderr or '')[-200:]}

# leg2: W16 entry-source anchor (the GENERATE baseline product face)
p16 = 'results/trial_labor_w16/w16_candidates.json'
b = io.open(p16, 'rb').read()
F['w16_source'] = {'path': p16, 'bytes': len(b), 'sha256_raw_lf': hashlib.sha256(b).hexdigest()[:16],
                  'sha256_crlf_canonical': hashlib.sha256(b.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')).hexdigest()[:16]}
d16 = json.loads(b.decode('utf-8'))
F['w16_n'] = d16['n']
F['w16_fns'] = sorted(set(c['fn'] for c in d16['candidates']))
F['w16_grammar_sha'] = d16.get('grammar_sha256', '')[:16]

# leg3: triaxis verdict reads (W17/W18/W19 judge faces)
for w in ('w17', 'w18', 'w19'):
    p = 'results/trial_labor_%s/%s_judge.json' % (w, w)
    if os.path.exists(p):
        d = json.load(io.open(p, encoding='utf-8'))
        keep = {}
        for k in ('n_judged', 'eligible_reform', 'verdict', 'lawful_zero', 'wave', 'n_cells'):
            if k in d: keep[k] = d[k]
        F[w + '_judge_face'] = {'path': p, 'keys': keep, 'top_keys': list(d.keys())[:12]}
    else:
        F[w + '_judge_face'] = {'path': p, 'absent': True}

# leg4: burned-fn inventory from grammar ledger (dedup base for GENERATE)
led = io.open('research/TRIAL_GRAMMAR_LEDGER.md', encoding='utf-8').read()
F['ledger_bytes'] = len(led.encode('utf-8'))
rows = [l for l in led.splitlines() if l.startswith('| TRIAL_LABOR_W1') or l.startswith('| TRIAL_LABOR_W') or l.startswith('| MASS_TRIAL') or l.startswith('| PERPETUAL-N2') or l.startswith('| N2U3')]
F['ledger_wave_rows_n'] = len(rows)
F['ledger_wave_labels'] = [r.split('|')[1].strip() for r in rows]

# leg5: DSR live head
import glob
heads = sorted(glob.glob('results/n1_w2*_results.json'))
F['dsr_head_file'] = heads[-1] if heads else None
if heads:
    d = json.load(io.open(heads[-1], encoding='utf-8'))
    for k in ('ledger', 'ledger_total', 'k_total', 'K', 'asof'):
        if k in d: F['dsr_head_' + k] = d[k]
    if 'ledger' not in F and 'dsr_head_ledger' not in F:
        F['dsr_head_top_keys'] = list(d.keys())[:10]

# leg6: queue collision probe (registration hygiene)
r = subprocess.run(['python', 'scripts/queue_head_collision_probe.py'], capture_output=True, text=True,
                   encoding='utf-8', errors='replace')
F['queue_collision_probe'] = {'rc': r.returncode, 'stdout_tail': (r.stdout or '')[-500:]}

out = 'results/_r1026bmc_w20_probe_facts.json'
io.open(out, 'w', encoding='utf-8').write(json.dumps(F, ensure_ascii=False, indent=1))
print("FACTS LANDED:", out)
print("seed_reg:", F.get('seed_registry_path'), "keys_n:", F.get('seed_registry_keys_n'))
print("w20 band rc:", F['seed_admit_gate_w20_base']['rc'], "| stdout tail:", F['seed_admit_gate_w20_base']['stdout_tail'][-200:])
print("w16 fns:", len(F['w16_fns']), "| dsr head:", F.get('dsr_head_file'), F.get('dsr_head_ledger'), F.get('dsr_head_K'))
print("collision:", F['queue_collision_probe']['rc'], F['queue_collision_probe']['stdout_tail'][-160:])
