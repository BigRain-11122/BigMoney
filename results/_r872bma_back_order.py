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
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1:
        tg = node.targets[0]
        if isinstance(tg, ast.Name) and tg.id == 'BACK183' and isinstance(node.value, ast.List):
            BACK183 = [(ev(p.elts[0]), ev(p.elts[1])) for p in node.value.elts]

print('ORDER:')
for i, (t, v) in enumerate(BACK183):
    print(f'{i:2d} {t:14s} len={len(v):5d} {v[:50]!r}')
