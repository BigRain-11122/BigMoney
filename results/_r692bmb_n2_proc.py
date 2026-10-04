# r692 bm-b probe2: N2 generate process liveness (PID 54492 old-code watch + any perpetual_faces_n2 proc)
import subprocess, json, datetime

r = subprocess.run(['powershell', '-NoProfile', '-Command',
    "Get-CimInstance Win32_Process | Where-Object { $_.Name -in 'python.exe','pythonw.exe' } | "
    "Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json -Compress"],
    capture_output=True, text=True)
d = json.loads(r.stdout)
if isinstance(d, dict):
    d = [d]
out = {'total_python': len(d), 'n2_procs': [], 'pid_54492': None}
now = datetime.datetime.now()
for p in d:
    cl = (p.get('CommandLine') or '')
    pid = p.get('ProcessId')
    if pid == 54492:
        out['pid_54492'] = cl[:200]
    if 'perpetual_faces_n2' in cl or 'n2_w15' in cl or 'perpetual' in cl:
        cd = p.get('CreationDate')
        age = None
        if cd:
            try:
                # PS JSON date: /Date(epoch_ms)/
                ms = int(str(cd).split('(')[1].split(')')[0].split('+')[0])
                age = round((now.timestamp() * 1000 - ms) / 60000, 1)
            except Exception:
                age = str(cd)[:22]
        out['n2_procs'].append({'pid': pid, 'age_min': age, 'cmd': cl[:220]})
with open('results/_r692bmb_n2_proc.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False))
