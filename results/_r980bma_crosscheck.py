# -*- coding: utf-8 -*-
"""Cross-check: which SUB new-strings carry the prior-wave B band citation,
and where the template's own prior-band (W236: 536_004..536_203) citations sit."""
import ast, io, json, re, subprocess, difflib

SRC = 'results/_r980bma_w238_derive_v2.py'
src = io.open(SRC, encoding='utf-8').read()
tree = ast.parse(src)


def render(node):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.JoinedStr):
        return ''.join(str(v.value) if isinstance(v, ast.Constant) else '<EXPR>'
                       for v in node.values)
    raise ValueError('unsupported')


pairs = []
for node in ast.walk(tree):
    if isinstance(node, ast.Call) and getattr(node.func, 'id', None) == 'A':
        arg = node.args[0]
        if isinstance(arg, ast.Tuple) and len(arg.elts) == 2:
            try:
                pairs.append((render(arg.elts[0]), render(arg.elts[1])))
            except ValueError:
                pairs.append(('<unsupported>', '<unsupported>'))

BAND = '538_204..538_403'
PREV = '536_004..536_203'
print('SUB new-strings containing W237-B-band citation %s:' % BAND)
for i, (o, n) in enumerate(pairs, 1):
    if BAND in n:
        print('  SUB#%d new_band=%d old_band=%d  new[:60]=%s' %
              (i, n.count(BAND), o.count(BAND), n[:60]))

GIT = r'C:\Program Files\Git\cmd\git.exe'
tpl = subprocess.run([GIT, 'show', 'd311a5439:research/PERPETUAL_N1_W237_PREREG.md'],
                     capture_output=True).stdout.decode('utf-8')
print()
print('template W236-B-band citations (%s): %d' % (PREV, tpl.count(PREV)))
for m in re.finditer(re.escape(PREV), tpl):
    s = m.start()
    print('  TPL@%d: ...%s...' % (s, tpl[max(0, s - 50):s + 60].replace('\n', ' ')[-100:]))
# which SUB old covers each
print()
for m in re.finditer(re.escape(PREV), tpl):
    s = m.start()
    for i, (o, n) in enumerate(pairs, 1):
        if o != '<unsupported>' and PREV in o:
            sm = difflib.SequenceMatcher(None, o, tpl, autojunk=False)
            blocks = [b for b in sm.get_matching_blocks() if b.size >= 4]
            if blocks and blocks[0].b <= s < blocks[-1].b + blocks[-1].size:
                print('TPL@%d covered by SUB#%d old (new_band=%d)' % (s, i, n.count(BAND)))
                break
