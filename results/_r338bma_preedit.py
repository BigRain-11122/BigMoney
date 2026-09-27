import json
import sys
import os

sys.path.insert(0, 'scripts')
import science_gates

# 1. ledger head now
h = science_gates.ledger_head()
print('ledger_head:', json.dumps(h, ensure_ascii=False))

# 2. csv row-level face exists?
p = 'research/shortline/sina_construct_p1_results.csv'
print('csv exists:', os.path.exists(p), os.path.getsize(p) if os.path.exists(p) else 0)

# 3. gate_attrition current shape
ga = json.load(open('results/gate_attrition.json', encoding='utf-8'))
print('gate_attrition top keys:', list(ga.keys()))
ents = ga.get('entries', [])
print('entries len:', len(ents))
if ents:
    print('last entry:', json.dumps(ents[-1], ensure_ascii=False)[:500])

# 4. module header of collector (latent defect note)
src = open('scripts/update_sina_mf.py', encoding='utf-8').read(3500)
i = src.find('%.10g')
print('--- collector header %.10g context:')
print(src[max(0, i - 600):i + 500] if i >= 0 else 'not in update_sina_mf.py header')
