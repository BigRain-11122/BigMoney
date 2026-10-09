import json

g = json.load(open('results/trial_labor_w16/w16_grammar.json', encoding='utf-8'))
faces = set(g['faces'])
cells = json.load(open('results/trial_labor_w17/w17_cells.json', encoding='utf-8'))
ent = json.load(open('results/trial_labor_w16/w16_candidates.json', encoding='utf-8'))
cands = {c['candidate_id']: c for c in ent['candidates']}
mks = set()
for cell in cells['cells']:
    c = cands.get(cell['candidate_id'])
    if c:
        mks.add(c['module'] + '.' + c['fn'])
missing = mks - faces
print('cells', len(cells['cells']), 'mks', len(mks),
      'missing_faces', sorted(missing)[:5],
      'OK' if not missing else 'FAIL')
