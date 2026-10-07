import subprocess, json

def side(stage, f):
    r = subprocess.run(['git','show',stage+':'+f],capture_output=True)
    return r.stdout

for f in ['results/p1d_gates.json','results/token_usage.json']:
    for tag, st in (('H',':2:'),('P',':3:')):
        b = side(st, f)
        try:
            j = json.loads(b.decode('utf-8'))
        except Exception as e:
            print(f, tag, 'DECODE-ERR', e, 'len', len(b))
            continue
        if isinstance(j, dict):
            print(f, tag, 'keys:', list(j)[:12])
            for k, v in j.items():
                if isinstance(v, (str, int, float, bool)):
                    print('   ', k, '=', str(v)[:80])
                elif isinstance(v, dict):
                    print('   ', k, '= dict keys', list(v)[:8])
                elif isinstance(v, list):
                    print('   ', k, '= list len', len(v))
