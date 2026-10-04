# r699 bm-b pool state read (subprocess direct bytes, r660 law)
import json, subprocess
def show(path, ref='origin/main'):
    r = subprocess.run(['git','show',f'{ref}:{path}'], capture_output=True, cwd=r'C:\Fluxgroup\FluxGroup\quant\bigmoney')
    if r.returncode != 0:
        print('ERR', ref, path, r.returncode, r.stderr.decode('utf-8','replace')[:200]); return None
    return r.stdout
b = show('results/runnable_pool.json')
if b:
    d = json.loads(b.decode('utf-8'))
    for e in d.get('entries', []):
        if 'N2' in e.get('id','') or 'W15' in e.get('id','') or 'W3' in e.get('id',''):
            print('ENTRY', e.get('id'), 'status=', e.get('status'))
            for s in e.get('shards', []):
                print('  ', s.get('key'), s.get('status'), 'owner=', s.get('owner'), 'since=', s.get('owner_since'))
# trio entries too
    print('---trio/w3/judge ids---')
    for e in d.get('entries', []):
        print(e.get('id'), e.get('status'), len(e.get('shards',[])))
