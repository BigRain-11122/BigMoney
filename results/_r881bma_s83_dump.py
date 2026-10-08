# -*- coding: utf-8 -*-
import io
src = io.open(r'results\_r877bma_w185_buildgen.py', encoding='utf-8').read()
i = src.find('S83 = [')
j = src.find('def s83(')
seg = src[i:j]
io.open(r'results\_r881bma_s83_extract.txt', 'w', encoding='utf-8', newline='\n').write(seg)
print('S83 segment bytes:', len(seg))
print('tuple open count:', seg.count('('))
