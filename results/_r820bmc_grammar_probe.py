import json

w17 = json.load(open('results/trial_labor_w17/w17_grammar.json', encoding='utf-8'))
w16 = json.load(open('results/trial_labor_w16/w16_grammar.json', encoding='utf-8'))
print('W17 grammar top keys:', sorted(w17.keys()))
print('W16 grammar top keys:', sorted(w16.keys()))
if 'faces' in w16:
    fks = list(w16['faces'].keys())
    print('W16 faces entries:', len(fks), 'sample:', fks[:3])
if 'faces' in w17:
    fks = list(w17['faces'].keys())
    print('W17 faces entries:', len(fks), 'sample:', fks[:3])

# worker initializer in w17 script
src = open('scripts/trial_labor_w17.py', encoding='utf-8').read()
i = src.find('def _screen_worker_init')
if i < 0:
    i = src.find('initializer=')
    print('---initializer face---')
    print(src[max(0, i - 600):i + 200])
else:
    print(src[i:i + 900])
