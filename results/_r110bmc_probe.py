import json, subprocess, re

def blob(rev):
    return subprocess.run(['git','show',rev],capture_output=True,text=True,encoding='utf-8',errors='replace').stdout

def deep_ts(obj, path=''):
    out=[]
    if isinstance(obj,dict):
        for k,v in obj.items():
            p=f'{path}.{k}' if path else k
            if isinstance(v,str) and re.match(r'^20\d{2}-',v):
                out.append((p,v))
            out.extend(deep_ts(v,p))
    elif isinstance(obj,list):
        for i,v in enumerate(obj):
            out.extend(deep_ts(v,f'{path}[{i}]'))
    return out

faces=[
 ('REPORT-md :2: origin', blob(':2:docs/daily_report/REPORT-2026-09-27.md'), 'txt'),
 ('REPORT-md :3: mine', blob(':3:docs/daily_report/REPORT-2026-09-27.md'), 'txt'),
 ('REPORT-json worktree-twin-automerge', open('docs/daily_report/REPORT-2026-09-27.json',encoding='utf-8').read(), 'json'),
 ('compute_audit :2: origin', blob(':2:results/compute_audit.json'), 'json'),
 ('compute_audit :3: mine', blob(':3:results/compute_audit.json'), 'json'),
 ('heat_status :2: origin', blob(':2:results/heat_update_status.json'), 'json'),
 ('heat_status :3: mine', blob(':3:results/heat_update_status.json'), 'json'),
 ('regime :2: origin', blob(':2:results/regime_state.json'), 'json'),
 ('regime :3: mine', blob(':3:results/regime_state.json'), 'json'),
]
for name,txt,kind in faces:
    print(f'=== {name} ===')
    try:
        if kind=='json':
            o=json.loads(txt)
            for p,v in deep_ts(o)[:8]: print(f'  ts {p} = {v}')
            if isinstance(o,dict):
                hk=[k for k in o.keys() if k in ('history','transitions','latest')]
                print('  top-keys:',list(o.keys())[:14])
                for k in hk:
                    if isinstance(o[k],list): print(f'  {k} len={len(o[k])}')
        else:
            m=re.findall(r'2026-\d\d-\d\d[ T]\d\d:\d\d:\d\d',txt)
            print('  ts-found:',m[:4],'len:',len(txt))
    except Exception as e:
        print('  parse-ERR',e)
