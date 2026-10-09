# -*- coding: utf-8 -*-
import io
pfn = io.open('scripts/perpetual_faces.py', encoding='utf-8', newline='').read().replace('\r\n', '\n')
a = pfn.find('    # W193 (bm-a r901 freeze')
print('pf193 at', a)
end = pfn.find('"engine_owner": "bm-a"},', a)
print('engine_owner line at', end)
if end > 0:
    print(repr(pfn[end - 80:end + 60]))
    print('---after pf193 block---')
    print(repr(pfn[end + len('"engine_owner": "bm-a"},'):end + 300]))
