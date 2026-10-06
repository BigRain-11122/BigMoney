# -*- coding: utf-8 -*-
import io
lines = io.open('results/_r785bma_w161_freeze_edits.py', encoding='utf-8').read().splitlines()
l445 = lines[444]  # 0-based
print(repr(l445))
print('contains ee04482a2:', 'ee04482a2' in l445)
print('contains ee44442a2:', 'ee44442a2' in l445)
# what the landed n1 file actually has
n2 = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8', newline='').read()
print('file has "ee04482a2, SINGLE STATE zero seat gap W2..W160 all " (quoted):',
      '"ee04482a2, SINGLE STATE zero seat gap W2..W160 all "' in n2)
print('file has "ee44442a2, SINGLE STATE zero seat gap W2..W160 all " (quoted):',
      '"ee44442a2, SINGLE STATE zero seat gap W2..W160 all "' in n2)
