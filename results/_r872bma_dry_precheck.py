# -*- coding: utf-8 -*-
import ast, io, json, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

src = io.open(r'results\_r869bma_w183_prereg_build.py', encoding='utf-8').read()
tree = ast.parse(src)

def ev(n):
    if isinstance(n, ast.Constant):
        return n.value
    raise AssertionError('unsupported node %r' % (ast.dump(n)[:80],))

BACK183 = None
EXPECT = None
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1:
        tg = node.targets[0]
        if isinstance(tg, ast.Name) and tg.id == 'BACK183' and isinstance(node.value, ast.List):
            BACK183 = [(ev(p.elts[0]), ev(p.elts[1])) for p in node.value.elts]
        if isinstance(tg, ast.Name) and tg.id == 'EXPECT' and isinstance(node.value, ast.Dict):
            EXPECT = {ev(k): ev(v) for k, v in zip(node.value.keys, node.value.values)}
assert BACK183 and EXPECT and len(BACK183) == 50 and len(EXPECT) == 50

blob = io.open(r'results\_r872bma_w184_prereg_src.txt', encoding='utf-8').read()
mism = []
out_t = blob
for tok, val in BACK183:
    n = out_t.count(val)
    exp = EXPECT[tok]
    if n != exp:
        mism.append((tok, n, exp, val[:70]))
    else:
        out_t = out_t.replace(val, tok)
print('ordered-simulation mismatches:', len(mism))
for m in mism:
    print('MISMATCH', m[0], 'count', m[1], 'expect', m[2], repr(m[3]))
# also dump EXPECT for reference
io.open(r'results\_r872bma_back183_expect_dump.json', 'w', encoding='utf-8').write(
    json.dumps({'BACK183': [[t, v] for t, v in BACK183], 'EXPECT': EXPECT},
               ensure_ascii=False, indent=1))
print('dumped BACK183/EXPECT')
