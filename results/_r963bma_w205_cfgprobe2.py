# -*- coding: utf-8 -*-
t = open('scripts/perpetual_faces_n1.py', encoding='utf-8', newline='').read().replace('\r\n', '\n')
i = t.find('204: {"batch')
j = t.find('"engine_owner": "bm-c"},', i)
seg = t[i:j + 24]
print('batch-hyphen count:', seg.count('PERPETUAL-N1-W204'))
print('prereg-underscore count:', seg.count('PERPETUAL_N1_W204'))
print('204-prefix count:', seg.count('204: {"batch'))
