import re
src = open('live/paper.py', encoding='utf-8').read()
for pat in [r'OOS_START *=.*', r'ANCHOR_TOL *=.*', r'COST_X1_RATE *=.*', r'COST_X2_RATE *=.*', r'MIN_BARS_COST_CHECK *=.*']:
    for m in re.finditer(pat, src):
        print(m.group(0))
print('-- SIGNAL_BUILDERS keys --')
for m in re.finditer(r'SIGNAL_BUILDERS\["([^"]+)"\]', src):
    print(m.group(1))
print('-- science_gates API --')
sg = open('scripts/science_gates.py', encoding='utf-8').read()
for pat in [r'def append_ledger.*', r'def ledger_head.*', r'def cutoff_meta.*']:
    for m in re.finditer(pat, sg):
        print(m.group(0))
