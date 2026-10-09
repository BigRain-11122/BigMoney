# -*- coding: utf-8 -*-
import io
pfn = io.open('scripts/perpetual_faces.py', encoding='utf-8', newline='').read().replace('\r\n', '\n')
a = pfn.find('    # W194 (bm-a r905 freeze')
print('pf194 at', a)
end = pfn.find('"engine_owner": "bm-a"},', a)
print('engine_owner line at', end)
if end > 0:
    print(repr(pfn[end - 80:end + 60]))
    print('---after pf194 block---')
    print(repr(pfn[end + len('"engine_owner": "bm-a"},'):end + 320]))
b = pfn.find('    # W195 (bm-a r909 freeze')
print('pf195 at', b, '| order OK:', a < b)
