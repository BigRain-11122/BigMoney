# r1011 ack fixer: remove bogus '--help' ack entry (probe pollution) from both faces,
# then canonical-append the real O-20261018-2144 ack via orders_ack_append.py (r1053 law).
# ASCII only. Read-back assertions per r504 validate-then-atomic law.
import json, os, subprocess, sys

ROOT = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
os.chdir(ROOT)

def rf(p):
    with open(p, 'r', encoding='utf-8') as f:
        return f.read()

def wf(p, s):
    with open(p, 'w', encoding='utf-8', newline='\n') as f:
        f.write(s)

faces = ('state.json', os.path.join('fleet', 'machines', 'bm-b.json'))
for p in faces:
    d = json.loads(rf(p))
    lst = d.get('orders_ack', [])
    before = len(lst)
    lst2 = [x for x in lst if x != '--help']
    d['orders_ack'] = lst2
    if d.get('orders_ack_last') == '--help':
        d['orders_ack_last'] = lst2[-1] if lst2 else ''
    wf(p, json.dumps(d, indent=1, ensure_ascii=False) + '\n')
    print('SANITIZE', p, before, '->', len(lst2))

r = subprocess.run([sys.executable, os.path.join('Tools', 'orders_ack_append.py'), 'O-20261018-2144-bm-c.md'],
                   capture_output=True, text=True, encoding='utf-8', errors='replace')
print('ACK-RC', r.returncode, (r.stdout or '').strip()[-220:], (r.stderr or '').strip()[-220:])
if r.returncode != 0:
    sys.exit(2)

for p in faces:
    d = json.loads(rf(p))
    lst = d.get('orders_ack', [])
    assert 'O-20261018-2144-bm-c.md' in lst, p + ' missing real ack'
    assert '--help' not in lst, p + ' still has bogus entry'
    print('VERIFY', p, 'count', len(lst), 'last', d.get('orders_ack_last'))
print('ACKFIX-COMPLETE')
