# -*- coding: utf-8 -*-
import subprocess, json, re
def blob(stage, path): return subprocess.run(['git','show',f':{stage}:{path}'],capture_output=True).stdout

j2=json.loads(blob(2,'results/compute_audit.json')); j3=json.loads(blob(3,'results/compute_audit.json'))
h2,h3=j2['history'],j3['history']
print('hist len2:',len(h2),'len3:',len(h3),'row keys:',sorted(h2[0].keys()) if h2 else '-')
print('tail ts2:',[r.get('ts') for r in h2][-3:]); print('tail ts3:',[r.get('ts') for r in h3][-3:])
print('latest2 ts:',j2['latest'].get('ts'),' latest3 ts:',j3['latest'].get('ts'))

b2s=blob(2,'results/dashboard_status.js').decode('utf-8','replace'); b3s=blob(3,'results/dashboard_status.js').decode('utf-8','replace')
m2=re.search(r'generated[^0-9]{0,4}([0-9T:.\-+]{10,30})',b2s); m3=re.search(r'generated[^0-9]{0,4}([0-9T:.\-+]{10,30})',b3s)
print('js gen2:',m2.group(1) if m2 else '?',' gen3:',m3.group(1) if m3 else '?')

r2=json.loads(blob(2,'results/regime_state.json')); r3=json.loads(blob(3,'results/regime_state.json'))
print('regime updated2:',r2.get('updated'),' updated3:',r3.get('updated'))
print('regime hist len2:',len(r2.get('history',[])),'len3:',len(r3.get('history',[])))

for p in ['results/dashboard_status.json','results/fundamental_b_layer_filter.json','results/futures_update_status.json','results/heat_update_status.json','results/lhb_update_status.json','results/token_usage.json','results/update_status.json']:
    a,b=json.loads(blob(2,p)),json.loads(blob(3,p))
    t2=a.get('ts') or a.get('generated') or a.get('updated') or '-'
    t3=b.get('ts') or b.get('generated') or b.get('updated') or '-'
    print(p, 'ours=',t2,' mine=',t3)
