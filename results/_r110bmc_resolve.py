import json, subprocess

def blob(rev):
    return subprocess.run(['git','show',rev],capture_output=True,text=True,encoding='utf-8',errors='replace').stdout

R={}
a2=json.loads(blob(':2:results/compute_audit.json'))
a3=json.loads(blob(':3:results/compute_audit.json'))
h2,h3=a2['history'],a3['history']
# r319: probe per-face identity key = ts (only in-entry key; no machine field in audit rows)
seen={}
same_ts_diverge=0
for e in h2+h3:
    k=e.get('ts')
    assert k, f'ts key missing in entry'
    if k in seen:
        if seen[k]!=e:
            same_ts_diverge+=1
            print('SAME-TS DIVERGE:',k)
    else:
        seen[k]=e
union=sorted(seen.values(),key=lambda e:e['ts'])
assert same_ts_diverge==0, f'same-ts cross-side divergence: {same_ts_diverge}'
l2,l3=a2.get('latest',{}),a3.get('latest',{})
latest = l2 if str(l2.get('ts',''))>str(l3.get('ts','')) else l3
merged={'latest':latest,'history':union}
json.dump(merged,open('results/compute_audit.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
R['compute_audit']=f'union {len(h2)}|{len(h3)}->{len(union)} ts-key zero-loss same-ts-diverge=0, latest={latest.get("ts")} (o={l2.get("ts")} vs m={l3.get("ts")})'

s2=json.loads(blob(':2:results/heat_update_status.json'))
s3=json.loads(blob(':3:results/heat_update_status.json'))
assert s3['updated']>s2['updated'], (s3['updated'],s2['updated'])
json.dump(s3,open('results/heat_update_status.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
R['heat_status']=f"take mine ({s3['updated']} > {s2['updated']})"

g2=json.loads(blob(':2:results/regime_state.json'))
g3=json.loads(blob(':3:results/regime_state.json'))
assert [e['asof'] for e in g2['history']]==[e['asof'] for e in g3['history']]==['2026-09-23','2026-09-24']
assert g2['transitions']==g3['transitions']==[]
assert g3['updated']>g2['updated']
json.dump(g3,open('results/regime_state.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
R['regime']=f"ledger identical 2/0, take mine ({g3['updated']} > {g2['updated']})"

json.load(open('results/compute_audit.json',encoding='utf-8'))
json.load(open('results/heat_update_status.json',encoding='utf-8'))
json.load(open('results/regime_state.json',encoding='utf-8'))
md=open('docs/daily_report/REPORT-2026-09-27.md',encoding='utf-8').read()
assert '<<<<<<<' not in md and '2026-09-27 21:59:07' in md
R['report_md']='take mine (21:59:07 > 21:49:17); twin json automerge==my full side byte-identical (zero action)'
json.dump(R,open('results/_r110bmc_resolve.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print(json.dumps(R,ensure_ascii=False,indent=1))
print('ALL PARSE-VERIFIED OK')
