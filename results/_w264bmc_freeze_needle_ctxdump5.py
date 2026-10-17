# -*- coding: utf-8 -*-
import io
t = io.open('results/_w263bma_freeze_edits.py', encoding='utf-8', newline='').read()
print('CRLF count:', t.count('\r\n'), 'LF count:', t.count('\n') - t.count('\r\n'))
lines = t.split('\n')
for want in (7, 8, 9, 10, 129, 130, 364, 365, 523, 524, 769, 770):
    if want - 1 < len(lines):
        print(f'==L{want}==')
        print(lines[want - 1])
