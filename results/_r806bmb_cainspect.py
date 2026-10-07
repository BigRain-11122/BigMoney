import subprocess, json

o = json.loads(subprocess.run(['git','show',':2:results/compute_audit.json'],capture_output=True).stdout)
t = json.loads(subprocess.run(['git','show',':3:results/compute_audit.json'],capture_output=True).stdout)

def summ(d, tag):
    la = d.get('latest', {})
    print(tag, 'latest keys:', list(la.keys())[:12])
    for k, v in list(la.items())[:12]:
        if isinstance(v, dict):
            print('  ', k, '->', {kk: vv for kk, vv in v.items() if 'ts' in kk or 'time' in kk or kk in ('machine','epoch','t')})
        else:
            print('  ', k, '=', str(v)[:80])
    h = d.get('history', [])
    print(tag, 'history len:', len(h) if isinstance(h, list) else type(h))
    if isinstance(h, list) and h:
        print(tag, 'history tail:', json.dumps(h[-1], ensure_ascii=False)[:300])

summ(o, 'ORIGIN')
summ(t, 'OURS')
