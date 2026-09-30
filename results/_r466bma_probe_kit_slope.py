import re
kit = open('results/_r463bma_w13_layer_kit.py', encoding='utf-8').read()
i = kit.find('SUMN_LAYER_TEXT')
seg = kit[i:]
# find _sumn_faces_raw def and the slope computation inside layer text
j = seg.find('def _sumn_faces_raw')
print('--- _sumn_faces_raw (first 55 lines) ---')
for k, ln in enumerate(seg[j:].splitlines()[:55]):
    print(ln)
print()
k2 = seg.find('slope_sign_split')
print('--- slope split context ---')
print(seg[k2-900:k2+1100])
