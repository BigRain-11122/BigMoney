# -*- coding: utf-8 -*-
import ast, io, json, sys

src = io.open(r'results\_r869bma_w183_buildgen.py', encoding='utf-8').read()
tree = ast.parse(src)

S82 = None
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1:
        tg = node.targets[0]
        if isinstance(tg, ast.Name) and tg.id == 'S82' and isinstance(node.value, ast.List):
            S82 = node.value
if S82 is None:
    raise SystemExit('S82 list not found')

lit_pairs = []
expr_pairs = []
for elt in S82.elts:
    assert isinstance(elt, ast.Tuple) and len(elt.elts) == 2, ast.dump(elt)[:100]
    o, n = elt.elts
    try:
        ov = ast.literal_eval(o)
        nv = ast.literal_eval(n)
        lit_pairs.append([ov, nv])
    except (ValueError, SyntaxError):
        expr_pairs.append([ast.dump(o)[:120], ast.dump(n)[:120]])

print('literal pairs:', len(lit_pairs), ' expression pairs:', len(expr_pairs))
out = {'literal_pairs': lit_pairs, 'expression_pair_dumps': expr_pairs}
io.open(r'results\_r872bma_s82_extract.json', 'w', encoding='utf-8').write(
    json.dumps(out, ensure_ascii=False, indent=1))
print('dumped to results/_r872bma_s82_extract.json')
