import json, glob, os
print('--- n1_w47 products ---')
files = sorted(glob.glob('results/p2cal_ext/n1_w47/*.json'))
print('count:', len(files))
for f in files: print(' ', os.path.basename(f))
print('--- engine state ---')
st = json.load(open('results/saturation_engine/state_bm-b.json', encoding='utf-8'))
print('keys:', list(st.keys()))
for k in ('queue','active','burns','history'):
    v = st.get(k)
    if isinstance(v, list): print(k, 'len=', len(v), 'tail=', v[-2:] if v else [])
print('--- W47 prereg/finalize face ---')
p = 'results/perpetual_faces/n1_w47_results.json'
print('finalize results file exists:', os.path.exists(p))
if os.path.exists(p):
    d = json.load(open(p, encoding='utf-8'))
    print('keys:', list(d.keys())[:15])
    print('K:', d.get('K'), 'ledger:', json.dumps(d.get('ledger'))[:200])
print('--- canon wave registry tail ---')
import re
src = open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
# find N1_BANDS tail lines
m = re.findall(r'"?(W\d+|wave)"?\s*[:=].{0,120}', src)
for band in re.findall(r'\(?\s*(\d+)\s*,\s*(\d+)\s*\)?\s*#?\s*W(\d+)', src)[-8:]:
    print('band row:', band)
