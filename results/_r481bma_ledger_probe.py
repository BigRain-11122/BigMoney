import json, io

d = json.load(io.open('results/gate_attrition.json', encoding='utf-8'))
print('top keys:', list(d.keys()))
tl = d.get('trials_ledger')
if isinstance(tl, dict):
    print('tl keys:', list(tl.keys())[:12])
    print('tl.total:', tl.get('total'))
# fallback: search raw text for a total field
t = io.open('results/gate_attrition.json', encoding='utf-8').read()
idx = t.find('"total"')
print('raw total ctx:', t[idx:idx+60] if idx >= 0 else 'ABSENT')
