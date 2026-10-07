import io, datetime

p = 'HQ-FEEDBACK.md'
with io.open(p, encoding='utf-8') as f:
    lines = f.read().splitlines()

n0 = len(lines)
flipped = False
for i, l in enumerate(lines):
    if l.startswith('- F-20261007-01 ') and 'D-20261002-06' in l and '已提前核销' not in l:
        lines[i] = l.rstrip() + ' 〔状态自翻 bm-a r866 2026-10-08：D-20261007-04① 已提前核销=executed（集团独立实测三面绿·主件 30,398B≤30,720B+28 域件全达标·线级达标），本行「顺延窗 10-09」窗语已过时，唯一权威=D-20261007-04①；翻面依据=D-20261008-01② 消费步〕'
        flipped = True
        break

assert flipped, 'target row not found'
assert len(lines) == n0, 'row count changed unexpectedly'
with io.open(p, 'w', encoding='utf-8', newline='') as f:
    f.write('\n'.join(lines) + '\n')
print('flipped row; lines', n0, '->', len(lines))
