import os, json, datetime, subprocess

# 1) moneyflow refresh liveness
prog = 'data/moneyflow/_progress.json'
d = json.load(open(prog, encoding='utf-8'))
print('MF done count:', len(d.get('done', [])),
      'prog mtime:', datetime.datetime.fromtimestamp(os.path.getmtime(prog)).strftime('%H:%M:%S'))
q = "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
q += "Where-Object {$_.CommandLine -match 'moneyflow'} | "
q += "Select-Object -First 3 ProcessId,CreationDate | ConvertTo-Json -Compress"
r = subprocess.run(['powershell', '-NoProfile', '-Command', q],
                   capture_output=True, text=True)
print('MF procs:', (r.stdout or '').strip()[:220])

# 2) W241 finalize face
print('w241 finalize:', os.path.exists('results/perpetual_faces/n1_w241_results.json'))

# 3) pit-data.md size
print('pit-data size:', os.path.getsize('research/pit-data.md'))
