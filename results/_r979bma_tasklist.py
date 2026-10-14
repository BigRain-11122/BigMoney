import subprocess
o = subprocess.run(['schtasks', '/query', '/fo', 'csv'],
                   capture_output=True).stdout.decode('gbk', errors='replace')
keys = ('Bigmoney', 'SatEngine', 'Idle', 'Watchdog', 'Autofill', 'EngineTick', 'Dispatcher')
rows = [l for l in o.splitlines() if any(k in l for k in keys)]
for r in rows:
    f = r.split('","')
    if len(f) >= 4:
        print(f[0].strip('"'), '| next=', f[1], '| state=', f[3].rstrip('"'))
    else:
        print(r[:120])
