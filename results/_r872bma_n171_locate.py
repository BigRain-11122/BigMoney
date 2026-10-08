# -*- coding: utf-8 -*-
import ast, io, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

src = io.open(r'results\_r869bma_w183_prereg_build.py', encoding='utf-8').read()
tree = ast.parse(src)

def ev(n):
    if isinstance(n, ast.Constant):
        return n.value
    raise AssertionError('unsupported')

BACK183 = None
EXPECT = None
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1:
        tg = node.targets[0]
        if isinstance(tg, ast.Name) and tg.id == 'BACK183' and isinstance(node.value, ast.List):
            BACK183 = [(ev(p.elts[0]), ev(p.elts[1])) for p in node.value.elts]
        if isinstance(tg, ast.Name) and tg.id == 'EXPECT' and isinstance(node.value, ast.Dict):
            EXPECT = {ev(k): ev(v) for k, v in zip(node.value.keys, node.value.values)}

blob = io.open(r'results\_r872bma_w184_prereg_src.txt', encoding='utf-8').read()
out_t = blob
for tok, val in BACK183:
    if tok == '@N171@':
        break
    n = out_t.count(val)
    if n == EXPECT[tok]:
        out_t = out_t.replace(val, tok)
idx = 0
while True:
    i = out_t.find('183', idx)
    if i < 0:
        break
    print(repr(out_t[max(0, i - 60):i + 63]))
    idx = i + 3
