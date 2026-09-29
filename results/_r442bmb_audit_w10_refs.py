import re
src = open('scripts/trial_labor_w11.py', encoding='utf-8').read()
lines = src.split('\n')
# current-wave W10 references that are NOT legitimate prior-wave mentions
legit = re.compile(
    r'tl10|PRIOR_WAVE|20311500|r438|r437|bm-c r228|MOM|W9|W1-W10|W10-JUDGE|'
    r'W10 order|W10-order|W10 semantic|W10 frozen|W10 machinery|W10 face|'
    r'W10 screen|W10 judge|W10\'s own|vs W10|AMP->W9->W10|W10 adoption|'
    r'w10_screen|w10_judge|W10-GENERATE|W10 is NEW')
hits = []
for i, l in enumerate(lines):
    for m in re.finditer(r'W10', l):
        ctx = l[max(0, m.start() - 40):m.end() + 30]
        if not legit.search(ctx):
            hits.append((i + 1, l.strip()[:110]))
            break
for h in hits[:30]:
    print(f'{h[0]:5d}: {h[1]}')
print('total suspicious:', len(hits))
