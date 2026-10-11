import json, collections
d = json.load(open(r'results\trial_labor_w18\w18_judge.json', encoding='utf-8'))
vs = d['verdicts']
print('VERDICT COUNTS:', dict(collections.Counter(vs.values())))
cells = d['cells']
if isinstance(cells, dict):
    c0 = list(cells.keys())[0]
    print('CELL0 key:', c0)
    print('CELL0:', json.dumps(cells[c0], ensure_ascii=False)[:700])
else:
    print('CELL0:', json.dumps(cells[0], ensure_ascii=False)[:700])
raw = open(r'results\trial_labor_w18\w18_judge.json', encoding='utf-8').read()
i = raw.find('skill_line')
print('SKILL_CTX:', (raw[max(0, i-100):i+160] if i >= 0 else 'NOT FOUND'))
