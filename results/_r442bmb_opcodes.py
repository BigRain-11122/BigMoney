import difflib
w9 = open('scripts/trial_labor_w9.py', encoding='utf-8').read().split('\n')
w10 = open('scripts/trial_labor_w10.py', encoding='utf-8').read().split('\n')
sm = difflib.SequenceMatcher(None, w9, w10, autojunk=False)
n_ins = n_del = n_rep = 0
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == 'equal':
        continue
    if tag == 'insert':
        n_ins += 1
        kind = 'INS'
    elif tag == 'delete':
        n_del += 1
        kind = 'DEL'
    else:
        n_rep += 1
        kind = 'REP'
    print(f'{kind} w9[{i1+1}:{i2+1}] -> w10[{j1+1}:{j2+1}] '
          f'({j2-j1} new lines / {i2-i1} old)')
print('ins', n_ins, 'del', n_del, 'rep', n_rep)
