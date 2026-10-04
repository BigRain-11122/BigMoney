import json, subprocess

# pool entries status census
p = json.load(open(r'results\runnable_pool.json', encoding='utf-8'))
entries = p.get('entries', {})
if isinstance(entries, dict):
    entries = list(entries.values())
census = {}
ready = []
for e in entries:
    st = e.get('status', '?')
    census[st] = census.get(st, 0) + 1
    if st in ('ready', 'running'):
        ready.append((e.get('id'), st, e.get('lane', '')[:50]))
print('pool census:', json.dumps(census))
for r in ready[:10]:
    print('ACTIVE:', r)

# python burn processes (NULLS trio + autofill)
out = subprocess.run(['powershell', '-NoProfile', '-Command',
                      'Get-CimInstance Win32_Process -Filter "Name=\'python.exe\'" | Select-Object ProcessId,CommandLine | ConvertTo-Json'],
                     capture_output=True).stdout.decode('utf-8', 'replace')
try:
    procs = json.loads(out)
    if isinstance(procs, dict):
        procs = [procs]
    for pr in procs:
        cl = (pr.get('CommandLine') or '')
        if any(k in cl for k in ('nulls', 'fund_', 'autofill', 'saturation')):
            print('PROC', pr.get('ProcessId'), cl[:150])
    print('total python procs:', len(procs))
except Exception as ex:
    print('parse err', ex, out[:200])
