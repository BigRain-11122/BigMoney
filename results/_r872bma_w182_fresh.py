# -*- coding: utf-8 -*-
import ast, io, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

src = io.open(r'results\_r867bma_w182_prereg_build.py', encoding='utf-8').read()
tree = ast.parse(src)

def ev(n):
    if isinstance(n, ast.Constant):
        return n.value
    raise AssertionError('unsupported')

BACK182 = None
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1:
        tg = node.targets[0]
        if isinstance(tg, ast.Name) and tg.id == 'BACK182' and isinstance(node.value, ast.List):
            BACK182 = [(ev(p.elts[0]), ev(p.elts[1])) for p in node.value.elts]
m = dict(BACK182)
for tok in ['@SEMT@', '@KLT@', '@ORDINALS@', '@OWNCHAIN@']:
    print('=' * 16, tok, '=' * 16)
    print(m[tok])
print('=' * 16, '@CHAIN@ tail', '=' * 16)
print(m['@CHAIN@'][-100:])
