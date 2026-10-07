import json, subprocess

def g(f, s):
    return subprocess.run(['git','show',f':{s}:{f}'],capture_output=True).stdout.decode('utf-8',errors='replace')

# 1) compute_audit.json: true union of history (ts-ordered), latest = ours (newer 03:58:22)
f='results/compute_audit.json'
o,t=json.loads(g(f,2)),json.loads(g(f,3))
oh,th=o['history'],t['history']
merged=sorted(oh+th, key=lambda h:h['ts'])
seen=set(); dedup=[]
for h in merged:
    k=(h['ts'], json.dumps(h,sort_keys=True))
    if k not in seen: seen.add(k); dedup.append(h)
o['history']=dedup[-200:]
o['latest']=o['latest']  # ours newer
open(f,'w',encoding='utf-8').write(json.dumps(o,indent=2,ensure_ascii=False))
print('compute_audit union:',len(dedup),'entries; latest ts:',o['latest']['ts'])

# 2) token_usage.json: ours base + theirs' -bm-c section (bm-c's own freshest run) + sum-consistent total
f='results/token_usage.json'
o,t=json.loads(g(f,2)),json.loads(g(f,3))
o['machines']['-bm-c']=t['machines']['-bm-c']
tot=sum((m.get('report_tokens_est',0)+m.get('state_tokens_est',0)) for m in o['machines'].values())
if o.get('total_report_tokens_est') is not None:
    o['total_report_tokens_est']=tot
open(f,'w',encoding='utf-8').write(json.dumps(o,indent=2,ensure_ascii=False))
print('token_usage union: -bm-c from theirs, total=',tot)
