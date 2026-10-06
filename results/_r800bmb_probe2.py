import subprocess, json

def stage(p, n):
    r = subprocess.run(['git', 'show', f':{n}:{p}'], capture_output=True)
    return r.stdout

for p in ['results/autofill_state.bm-b.json', 'results/p1d_gates.json']:
    print('=' * 20, p)
    for label, n in (('ours', 2), ('theirs', 3)):
        b = stage(p, n)
        print(f'--{label}-- len={len(b)} crlf={b.count(bytes([13,10]))}')
        j = json.loads(b.decode('utf-8'))
        if isinstance(j, dict):
            for k, v in j.items():
                if isinstance(v, list):
                    print(f'  {k}: list[{len(v)}]', 'last-row:', json.dumps(v[-1])[:120] if v else '')
                elif isinstance(v, dict):
                    print(f'  {k}: dict keys={list(v.keys())[:8]}')
                else:
                    print(f'  {k}: {json.dumps(v)[:100]}')
