# -*- coding: utf-8 -*-
import io
n1 = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8', newline='').read().replace('\r\n', '\n')
i = n1.find('# --- W199 materializer face')
j = n1.find('    _set_wave(2)', i)
frag = n1[i:j]
print('MAT199: PENDING count:', frag.count('PENDING'), ' processed count:', frag.count('processed'), ' archive count:', frag.count('archive'))
for ln in frag.splitlines():
    if 'PENDING' in ln or 'processed' in ln or 'archive' in ln:
        print('  MAT|', ln[:130])
i2 = n1.find('          "+ W199 materializer face')
j2 = n1.find('"r919 bm-a] "', i2) + len('"r919 bm-a] "')
claim = n1[i2:j2]
print('CLAIM199: PENDING:', claim.count('PENDING'), ' processed:', claim.count('processed'), ' archive:', claim.count('archive'))
i4 = n1.find('    199: {"batch": "PERPETUAL-N1-W199",')
j4 = n1.find('"engine_owner": "bm-a"},', i4) + len('"engine_owner": "bm-a"},')
cfg = n1[i4:j4]
print('CFG199: PENDING:', cfg.count('PENDING'), ' processed:', cfg.count('processed'), ' archive:', cfg.count('archive'))
pf = io.open('scripts/perpetual_faces.py', encoding='utf-8', newline='').read().replace('\r\n', '\n')
i3 = pf.find('    # W199 (bm-a r919 freeze')
j3 = pf.find('"engine_owner": "bm-a"},', i3) + len('"engine_owner": "bm-a"},')
pffrag = pf[i3:j3]
print('PF199: PENDING count:', pffrag.count('PENDING'), ' processed:', pffrag.count('processed'), ' archive:', pffrag.count('archive'))
for ln in pffrag.splitlines():
    if 'PENDING' in ln or 'processed' in ln or 'archive' in ln:
        print('  PF|', ln[:130])
# also check DROP_IF from r915
import ast
t915_src = io.open('results/_r915bma_w197_freeze_edits.py', encoding='utf-8').read()
t = ast.parse(t915_src)
for node in ast.walk(t):
    if isinstance(node, ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id == 'DROP_IF' and isinstance(node.value, ast.List):
        print('DROP_IF =', [ast.literal_eval(x) if isinstance(x, ast.Constant) else ast.literal_eval(x)[0] for x in node.value.elts])
