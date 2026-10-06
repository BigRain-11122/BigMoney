# r780 bm-b P0 probe: trio pool entry states + worker liveness facts (read-only)
import json, os, time

p = json.load(open('results/runnable_pool.json', encoding='utf-8'))
print('pool updated_at:', p.get('updated_at'))
for x in p['entries']:
    sid = str(x.get('id', x.get('batch_id', '')))
    if 'nulls' not in sid:
        continue
    slim = {k: v for k, v in x.items() if k != 'shards' and not isinstance(v, (list, dict))}
    print('ENTRY', json.dumps(slim, ensure_ascii=False)[:400])
    sh = x.get('shards')
    if isinstance(sh, list):
        for s in sh:
            print('  SHARD', json.dumps({k: v for k, v in s.items() if not isinstance(v, (list, dict))}, ensure_ascii=False)[:300])
    elif isinstance(sh, dict):
        for sk, sv in sh.items():
            print('  SHARD', sk, json.dumps({k: v for k, v in sv.items() if not isinstance(v, (list, dict))}, ensure_ascii=False)[:300])

af = json.load(open('results/autofill_state.bm-b.json', encoding='utf-8'))
lt = af.get('last_tick', {})
print('autofill last_tick ts:', lt.get('ts') if isinstance(lt, dict) else lt)
print('autofill keys:', sorted(af.keys()))
for k in ('claims', 'active', 'in_flight'):
    if k in af:
        print(k, json.dumps(af[k], ensure_ascii=False)[:400])

# worker process liveness: any python running fund_* burn?
import subprocess
r = subprocess.run(['powershell', '-NoProfile', '-Command',
                    "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
                    "Where-Object {$_.CommandLine -match 'fund_'} | "
                    "Select-Object ProcessId,CreationDate | ConvertTo-Json -Compress"],
                   capture_output=True, text=True)
print('burn workers:', (r.stdout or '').strip()[:600] or 'NONE')
