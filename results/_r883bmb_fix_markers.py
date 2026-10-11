# r883 bm-b: strip leftover stash-pop conflict markers (upstream side kept, stashed side dropped)
# source: predecessor-round stash pop residue packaged into autofill tick commits (r836 kin)
import sys

def fix(p):
    raw = open(p, encoding='utf-8', errors='replace').read()
    lines = raw.split('\n')
    out, mode = [], 'normal'  # normal | upstream | stashed
    for ln in lines:
        s = ln.strip()
        if s == '<<<<<<< Updated upstream':
            mode = 'upstream'; continue
        if s == '=======' and mode == 'upstream':
            mode = 'stashed'; continue
        if s == '>>>>>>> Stashed changes':
            mode = 'normal'; continue
        if mode in ('normal', 'upstream'):
            out.append(ln)
    fixed = '\n'.join(out)
    leftover = fixed.count('<<<<<<<') + fixed.count('>>>>>>>') + sum(1 for l in out if l.strip() == '=======')
    open(p, 'w', encoding='utf-8', newline='').write(fixed)
    print(p, 'leftover markers:', leftover, 'mode_end:', mode)

fix('results/p1d_gates.json')
fix('results/saturation_engine/history_bm-b.jsonl')

import json
d = json.load(open('results/p1d_gates.json', encoding='utf-8'))
print('p1d json valid OK, top keys:', len(d))
lines = [l for l in open('results/saturation_engine/history_bm-b.jsonl', encoding='utf-8') if l.strip()]
bad = 0
for i, l in enumerate(lines):
    try:
        json.loads(l)
    except Exception as e:
        bad += 1
        print('BAD LINE', i + 1, str(e)[:80])
print('history jsonl lines:', len(lines), 'bad:', bad)
sys.exit(0 if bad == 0 else 2)
