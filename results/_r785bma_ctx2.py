# -*- coding: utf-8 -*-
import io
n1 = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8', newline='').read()
k = n1.find('160: {"batch"')
print('--- context before 160 entry ---')
print(repr(n1[k-120:k+60]))
m = n1.find('"engine_owner": "bm-a"},', k) + len('"engine_owner": "bm-a"},')
print('--- context after entry160 ---')
print(repr(n1[m:m+80]))
cs = n1.find('"+ W160 materializer face')
ce = n1.find('"r783 bm-a] "', cs)
print('--- claim context before/after ---')
print(repr(n1[cs-80:cs+40]))
print(repr(n1[ce-40:ce+80]))
