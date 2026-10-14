# -*- coding: utf-8 -*-
import ast, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
r = subprocess.run(['git', 'show', 'a9ab3b51d:research/PERPETUAL_N1_W241_PREREG.md'], capture_output=True)
tpl = r.stdout.decode('utf-8')
tree = ast.parse(open('results/_w242bma_prereg_derive.py', encoding='utf-8').read())
pairs = []
for node in ast.walk(tree):
    if isinstance(node, ast.Call) and getattr(node.func, 'id', '') == 'A' \
            and len(node.args) == 1 and isinstance(node.args[0], ast.Tuple) and len(node.args[0].elts) == 2:
        try:
            o = ast.literal_eval(node.args[0].elts[0]); n = ast.literal_eval(node.args[0].elts[1])
            pairs.append((o, n))
        except Exception:
            pass
print('pairs parsed:', len(pairs))
out = tpl
miss = 0
for i, (o, n) in enumerate(pairs, 1):
    c = out.count(o)
    if c != 1:
        print('MISS', i, c, o[:60]); miss += 1; continue
    out = out.replace(o, n)
print('applied:', len(pairs) - miss)
for s in ['551_501..553_500', '541_501..541_700', '541_404..541_603',
          '549_501..551_500', '541_204..541_403', 'hops=1', '541_500']:
    print(s, '=', out.count(s))
