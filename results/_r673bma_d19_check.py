# r673 bm-a D-19 group watermark check (r660 law: python subprocess raw-bytes, zero PS pipe)
import json, subprocess, hashlib, sys

GRP = r'C:\Users\sjs20\Desktop\FluxGroup'
s = json.load(open('state-bm-a.json', encoding='utf-8'))

def blob(path):
    r = subprocess.run(['git', '-C', GRP, 'show', 'origin/main:' + path], capture_output=True)
    if r.returncode != 0:
        print('FETCH-FAIL', path, r.returncode); sys.exit(2)
    return r.stdout

f = subprocess.run(['git', '-C', GRP, 'fetch', 'origin'], capture_output=True)
print('fetch rc:', f.returncode)

for path, key in (('docs/decisions.md', 'last_decisions_sha'), ('docs/orders.md', 'last_orders_sha')):
    b = blob(path)
    sha = hashlib.sha256(b).hexdigest()
    ref = s.get(key, '')
    match = sha == ref
    print(f'{path}: sha256={sha[:16]} state={ref[:16]} MATCH={match}')
    if not match:
        # extract new lines: lines in current blob not in... we cannot diff without old blob; report sha change + tail preview
        print(f'{key} CHANGED -> need consumption')
        tail = b.decode('utf-8', errors='replace').splitlines()[-40:]
        open('results/_r673bma_d19_tail.txt', 'wb').write(('\n'.join(tail)).encode('utf-8'))
        print('tail saved to results/_r673bma_d19_tail.txt')
