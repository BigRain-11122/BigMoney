import subprocess, json


def blob(st, p):
    spec = st.rstrip(':') + ':' + p
    r = subprocess.run(['git', 'show', spec], capture_output=True)
    return json.loads(r.stdout)


for p in ['results/t35_open_fill_verify.json', 'results/_attrition_guard_scan.json']:
    o = blob(':2:', p)
    m = blob(':3:', p)
    print('==', p)
    for k in sorted(set(o) | set(m)):
        ov, mv = o.get(k), m.get(k)
        same = (ov == mv)
        if same:
            print(f'  {k}: SAME {str(ov)[:100]}')
        else:
            print(f'  {k}: DIFF')
            print(f'    origin={str(ov)[:300]}')
            print(f'    mine   ={str(mv)[:300]}')
