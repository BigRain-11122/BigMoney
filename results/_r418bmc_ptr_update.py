# -*- coding: utf-8 -*-
# r418 bm-c: append batch-1 receipt lines to the three domain pointer lines in CODELY.md
import sys

REPO = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
CODELY = REPO + r'\CODELY.md'

APPENDS = {
    5: '；r418 bm-c pre-split survivors 批次一 2 条（r294 union 去重域坑/r294 amend 撞劫坑）已入件（件内对账行+receipt 为准）',
    6: '；r418 bm-c pre-split survivors 批次一 3 条（r489 池翻面双层坑/r511 pool worker initializer 重跑 fixture/r327 亚百 ms 池化 IPC 反噬）已入件（件内对账行+receipt 为准）',
    7: '；r418 bm-c pre-split survivors 批次一 2 条（r307 波带尾律算术撞值跳位/r494 波 runner 复制粘贴键漂移）已入件（件内对账行+receipt 为准）',
}
END = '已入件（件内对账行为准）。'

raw = open(CODELY, 'rb').read()
text = raw.decode('utf-8')
trailing = text.endswith('\r\n')
lines = [l.rstrip('\r') for l in text.split('\n')]
if trailing and lines and lines[-1] == '':
    lines.pop()

for idx, add in APPENDS.items():
    ln = lines[idx]
    assert ln.endswith(END), 'L%d does not end with expected tail: %r' % (idx + 1, ln[-40:])
    assert 'r418 bm-c' not in ln, 'L%d already has r418 receipt' % (idx + 1)
    lines[idx] = ln[:-len(END)] + add + END

new_text = '\r\n'.join(lines) + ('\r\n' if trailing else '')
assert '\r\r\n' not in new_text
open(CODELY, 'wb').write(new_text.encode('utf-8'))
print('POINTER LINES UPDATED: %d, bytes %d -> %d' % (len(APPENDS), len(raw), len(new_text.encode('utf-8'))))
