import json
import glob
import re

# 1. find trials ledger files
for f in glob.glob('results/*ledger*') + glob.glob('results/*trials*') + glob.glob('research/*LEDGER*'):
    print('ledger file:', f)

# 2. read science_gates ledger storage
sg = open('scripts/science_gates.py', encoding='utf-8').read()
m = re.search(r'def ledger_head.*?(?=\ndef |\Z)', sg, re.S)
if m:
    print('== ledger_head:')
    print(m.group(0)[:900])
m2 = re.search(r'(RESULTS_TRIALS[^\n]*|TRIALS_FILE[^\n]*|ledger_path[^\n]*)', sg)
print('path hints:', m2.group(0) if m2 else None)

# 3. pool entry full
pool = json.load(open('results/runnable_pool.json', encoding='utf-8'))
ents = pool.get('entries', [])
for e in ents:
    if e.get('id') == 'SINA-CONSTRUCT-P1':
        print('== SINA entry FULL:')
        print(json.dumps(e, ensure_ascii=False, indent=1))
    if e.get('id') in ('FUSION-P1-NAV', 'T19-PHANTOM-P1'):
        print('== other entry', e.get('id'), 'status=', e.get('status'), 'keys=', list(e.keys()))
        print('   ', json.dumps(e, ensure_ascii=False)[:400])
