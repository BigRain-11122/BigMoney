# -*- coding: utf-8 -*-
"""r682 bm-a: copy-adapt _r681bma_s6_chain.py -> _r682bma_s6_chain.py (r461 law:
no blind cross-round reuse; read source first, adapt with new round label)."""
t = open('results/_r681bma_s6_chain.py', 'rb').read().decode('utf-8')
assert t.count('_r681bma') == 1, f"source anchor count {t.count('_r681bma')}"
assert t.count('"round": "r681"') == 1
t = t.replace('_r681bma', '_r682bma')
t = t.replace('"round": "r681"', '"round": "r682"')
t = t.replace('r681 bm-a', 'r682 bm-a', 1)
assert '_r681bma' not in t and '"r681"' not in t
open('results/_r682bma_s6_chain.py', 'wb').write(t.encode('utf-8'))
print('r682 chain written,', len(t), 'chars')
