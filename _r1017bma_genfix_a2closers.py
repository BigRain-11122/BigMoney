# -*- coding: utf-8 -*-
# r1017 bm-a scratch v2: append missing assert-tuple closer ')' on the two
# NEW-a2 message tails -- byte-truth form (inside gen ''' block, tails are
# )"\'  ->  )")\'  matching the proven W245 template element value ...)"  ->  ...)").
import ast
import io

BS = chr(92)
Q = chr(39)
gen = 'results/_r1017bma_w246_gen.py'
t = io.open(gen, encoding='utf-8', newline='').read()

fixes = [
    ('machine-checkable)"' + BS + Q + ',', 'machine-checkable)")' + BS + Q + ','),
    ('B_hop_lands_inside_A=false)"' + BS + Q + ',', 'B_hop_lands_inside_A=false)")' + BS + Q + ','),
]
for old, new in fixes:
    c = t.count(old)
    assert c == 1, 'needle tail=%r count=%d (expect 1)' % (old, c)
    t = t.replace(old, new)
    print('fixed tail: %r -> %r' % (old, new))

io.open(gen, 'w', encoding='utf-8', newline='').write(t)
ast.parse(io.open(gen, encoding='utf-8', newline='').read())
print('gen parses OK')

# value-level verification vs the proven W245 template element (rolled)
tpl = io.open('results/_w245bma_freeze_edits.py', encoding='utf-8', newline='').read()
i = tpl.find('machine-checkable)")')
ls = tpl.rfind(chr(10), 0, i) + 1
le = tpl.find(chr(10), i)
tpl_line = tpl[ls:le].rstrip(chr(13)).lstrip(' ')


def elem_value(line):
    e = ast.parse(line + chr(10)).body[0].value
    if isinstance(e, ast.Tuple):
        assert len(e.elts) == 1
        e = e.elts[0]
    assert isinstance(e, ast.Constant)
    return e.value


rolled = elem_value(tpl_line).replace('W245', 'W246')
g2 = io.open(gen, encoding='utf-8', newline='').read()
j = g2.find('machine-checkable)")')
ls2 = g2.rfind(chr(10), 0, j) + 1
le2 = g2.find(chr(10), j)
gen_line = g2[ls2:le2].rstrip(chr(13))
# gen line lives inside a ''' block: strip the leading \' and trailing \',
content = gen_line[2:] if gen_line.startswith(BS + Q) else gen_line
content = content[:content.rfind(BS + Q)] if content.endswith(BS + Q + ',') else content
content = content + ','
gv = elem_value(content)
assert gv == rolled, 'VALUE drift: %r vs %r' % (gv, rolled)
print('element-VALUE template-exact OK (rolled W246)')
