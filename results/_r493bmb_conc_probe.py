import json, subprocess, os
# round_no from state.json
try:
    s = json.load(open('state.json'))
    print('state.json round_no:', s.get('round_no'), '| keys:', [k for k in list(s.keys())[:12]])
except Exception as e:
    print('state.json ERR:', e)
# codely processes (tasklist, avoid PS quoting)
out = subprocess.check_output(['tasklist', '/FO', 'CSV']).decode('gbk', 'replace')
rows = [l for l in out.splitlines() if 'codely' in l.lower() or 'python' in l.lower()]
print('--- codely/python processes ---')
for r in rows:
    print(r)
# mtimes of recent activity markers
for f in ['results/p1d_gates.json', 'results/autofill_state.bm-b.json', 'results/runnable_pool.bm-b.json', 'logs/iteration-loop/round_reports.md']:
    if os.path.exists(f):
        print(f, '->', subprocess.check_output(['powershell', '-NoProfile', '-Command', '(Get-Item "' + f + '").LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")']).decode().strip())
