# -*- coding: utf-8 -*-
# r1017 bm-a scratch: find all assert-tuple closer lines in W245 template vs gen
import io

tpl = io.open('results/_w245bma_freeze_edits.py', encoding='utf-8', newline='').read()
gen = io.open('results/_r1017bma_w246_gen.py', encoding='utf-8', newline='').read()

for tag, text, needle in (
        ('TPL machine-checkable', tpl, 'machine-checkable'),
        ('GEN machine-checkable', gen, 'machine-checkable'),
        ('TPL hop_lands_inside_A', tpl, 'B_hop_lands_inside_A=false)'),
        ('GEN hop_lands_inside_A', gen, 'B_hop_lands_inside_A=false)')):
    print('=== %s ===' % tag)
    for n, ln in enumerate(text.split('\n')):
        if needle in ln:
            print('L%d: %r' % (n + 1, ln))
