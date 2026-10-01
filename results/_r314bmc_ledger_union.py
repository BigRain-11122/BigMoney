import json, subprocess, sys
repo = 'K:/Fluxgroup/FluxGroup/quant/bigmoney'
BASE = '576fd2c1e'   # pick base (origin tip at detach)
MINE = 'ae8615f54'   # my round commit

def show_obj(rev, path):
    return subprocess.check_output(['git','-C',repo,'show',f'{rev}:{path}'])

def union_ledgers(path):
    o = json.loads(show_obj(BASE, path).decode('utf-8'))
    t = json.loads(show_obj(MINE, path).decode('utf-8'))
    if not isinstance(o, dict) or not isinstance(t, dict):
        open(f'{repo}/{path}','wb').write(show_obj(BASE, path)); return 'fallback-origin(not-dict)'
    merged = dict(o)
    notes = []
    LIST_KEYS = ('history','runs','records','entries','findings','items','log')
    for k in LIST_KEYS:
        if isinstance(o.get(k), list) and isinstance(t.get(k), list):
            ok = {json.dumps(x, sort_keys=True, ensure_ascii=False) for x in o[k]}
            add = [x for x in t[k] if json.dumps(x, sort_keys=True, ensure_ascii=False) not in ok]
            merged[k] = o[k] + add
            notes.append(f'{k}: origin {len(o[k])} + mine-unique {len(add)}')
    # carry over any mine-only top-level keys (non-envelope)
    ENV = {'ts','generated','elapsed','elapsed_sec','machine','workers','updated_at','generated_at'}
    for k, v in t.items():
        if k not in merged and k not in ENV:
            merged[k] = v
    data = json.dumps(merged, ensure_ascii=False, indent=2)
    open(f'{repo}/{path}','w',encoding='utf-8',newline='').write(data.replace('\n','\r\n') if show_obj(BASE,path).count(b'\r\n')>0 else data)
    return '; '.join(notes) if notes else 'no-list-keys-merged(top-level carried)'

for path in ['results/science_audit.json', 'results/self_review/self_review_ledger.json']:
    print('UNION', path, '->', union_ledgers(path))
print('LEDGER-UNION-OK')
