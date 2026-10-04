# r692 bm-b probe: who is writing trio NULLS + N2-W15 state right now (active burn liveness, ownerless-pool adjudication)
import subprocess, json, os, datetime

out = {}
r = subprocess.run(['powershell', '-NoProfile', '-Command',
    "Get-CimInstance Win32_Process | Where-Object { $_.Name -in 'python.exe','pythonw.exe' } | "
    "Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json -Compress"],
    capture_output=True, text=True)
try:
    d = json.loads(r.stdout)
    if isinstance(d, dict):
        d = [d]
    procs = []
    for p in d:
        cl = (p.get('CommandLine') or '')
        if any(k in cl for k in ('fund_value', 'fund_quality', 'fund_divlowvol', 'n2_w15', 'nulls', 'autofill', 'burn', 'trial_labor', 'mass_trial', 'fund_p1')):
            procs.append({'pid': p.get('ProcessId'), 'created': str(p.get('CreationDate'))[:19], 'cmd': cl[:200]})
    out['burn_procs'] = procs
    out['total_python'] = len(d)
except Exception as ex:
    out['err'] = str(ex)
    out['raw'] = (r.stdout or '')[:500]

# nulls file freshness
for fam in ('fund_value_p1', 'fund_quality_p1', 'fund_divlowvol_p1'):
    p = f'results/{fam}/nulls.jsonl'
    if os.path.exists(p):
        st = os.stat(p)
        with open(p, 'rb') as f:
            n = sum(1 for _ in f)
        out[fam] = {'mtime': datetime.datetime.fromtimestamp(st.st_mtime).isoformat(), 'lines': n}

# N2-W15 generate log tail (new-code flush proof per r691 next(a))
for cand in ('results/n2_w15/generate.log', 'results/n2_w15/run.log', 'results/n2_w15/n2_w15_generate.log'):
    if os.path.exists(cand):
        with open(cand, 'rb') as f:
            tail = f.read()[-2000:].decode('utf-8', errors='replace')
        out['n2_log_file'] = cand
        out['n2_log_tail'] = tail[-600:]
        break

with open('results/_r692bmb_burn_liveness.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False)[:1500])
