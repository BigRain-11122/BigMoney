import subprocess, json
# r689 bm-a: finalize process CPU progress + engine W116/117 face
r = subprocess.run(['powershell', '-NoProfile', '-Command',
    '$p = Get-CimInstance Win32_Process -Filter "ProcessId=32480"; '
    'if ($p) { $p | Select-Object ProcessId,UserModeTime,KernelModeTime,CreationDate | ConvertTo-Json } else { "GONE" }'],
    capture_output=True)
print('PROC:', r.stdout.decode('gbk', 'replace').strip() or r.stderr.decode('gbk','replace').strip()[:200])

d = json.load(open(r'results\saturation_engine\state_bm-a.json', encoding='utf-8'))
print('engine state top keys:', list(d.keys())[:12])
for k in d:
    if 'W11' in str(k) or '116' in str(k) or '117' in str(k):
        v = d[k]
        print(k, ':', json.dumps(v, ensure_ascii=False)[:300])
# queue face
q = d.get('queue') or d.get('n1_queue') or {}
if isinstance(q, dict):
    print('queue sample:', json.dumps(q, ensure_ascii=False)[:400])
elif isinstance(q, list):
    print('queue len:', len(q), 'first:', json.dumps(q[:2], ensure_ascii=False)[:300])
