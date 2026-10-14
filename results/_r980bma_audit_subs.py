# -*- coding: utf-8 -*-
"""Dump the 7 re-anchored SUB pairs (old/new) from v2 derive for drift audit.
JoinedStr (f-string) elements rendered with placeholders to keep index alignment."""
import ast, io, difflib, subprocess

SRC = 'results/_r980bma_w238_derive_v2.py'
src = io.open(SRC, encoding='utf-8').read()
tree = ast.parse(src)


def render(node):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.JoinedStr):
        out = []
        for v in node.values:
            if isinstance(v, ast.Constant):
                out.append(str(v.value))
            else:
                out.append('<EXPR:%s>' % ast.dump(v.value)[:40])
        return ''.join(out)
    raise ValueError('unsupported: %r' % node)


pairs = []
for node in ast.walk(tree):
    if isinstance(node, ast.Call) and getattr(node.func, 'id', None) == 'A':
        arg = node.args[0]
        if isinstance(arg, ast.Tuple) and len(arg.elts) == 2:
            try:
                pairs.append((render(arg.elts[0]), render(arg.elts[1])))
            except ValueError:
                pairs.append(('<unsupported>', '<unsupported>'))

print('total SUB pairs:', len(pairs))
MISS = [1, 7, 8, 19, 22, 26, 37]
GIT = r'C:\Program Files\Git\cmd\git.exe'
tpl = subprocess.run([GIT, 'show', 'd311a5439:research/PERPETUAL_N1_W237_PREREG.md'],
                     capture_output=True).stdout.decode('utf-8')
report = []
for idx in MISS:
    old, new = pairs[idx - 1]
    sm = difflib.SequenceMatcher(None, old, tpl, autojunk=False)
    blocks = [b for b in sm.get_matching_blocks() if b.size >= 4]
    hit = None
    if blocks:
        s0 = blocks[0].b
        e0 = blocks[-1].b + blocks[-1].size
        seg = tpl[s0:e0]
        hit = {'pos': [s0, e0], 'ratio': round(difflib.SequenceMatcher(None, old, seg).ratio(), 4),
               'seg': seg}
    report.append({'sub': idx, 'old_len': len(old), 'new_len': len(new),
                   'old': old, 'new': new, 'tpl_hit': hit})

io.open('results/_r980bma_sub_audit.json', 'w', encoding='utf-8', newline='').write(
    __import__('json').dumps(report, ensure_ascii=False, indent=1))
print('audit written to results/_r980bma_sub_audit.json')
for r in report:
    print('SUB#%(sub)d old_len=%(old)d new_len=%(new)d hit=%s' %
          {'sub': r['sub'], 'old': r['old_len'], 'new': r['new_len'],
           'hit': ('%(pos)s r=%(ratio)s' % r['tpl_hit']) if r['tpl_hit'] else 'NONE'})
