# -*- coding: utf-8 -*-
t = open('scripts/perpetual_faces_n1.py', encoding='utf-8', newline='').read().replace('\r\n', '\n')
i = t.find('204: {"batch": "PERPETUAL-N1-W204",')
j = t.find('"engine_owner": "bm-c"},', i)
seg = t[i:j + len('"engine_owner": "bm-c"},')]
import re
print(repr(seg[:300]))
print('---')
print(repr(seg[-400:]))
print('--- bare 204 tokens:', re.findall(r'\b204\b', seg))
print('--- bare 203 tokens:', re.findall(r'\b203\b', seg))
