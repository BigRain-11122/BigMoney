# -*- coding: utf-8 -*-
import io

n1n = io.open('scripts/perpetual_faces_n1.py', encoding='utf-8',
              newline='').read().replace('\r\n', '\n')
i = n1n.find('    # --- W194 materializer face')
j = n1n.find('    _set_wave(2)', i)
chunk = n1n[i:j + len('    _set_wave(2)')]
dump = io.open('results/_r909bma_w195_face_mat.txt', encoding='utf-8',
               newline='').read()
print('chunk == dump:', chunk == dump, '| chunk len', len(chunk),
      '| dump len', len(dump))
k = chunk.find('REFUSED at its own start')
while k >= 0:
    print('CHUNK:', repr(chunk[k - 60:k + 60]))
    k = chunk.find('REFUSED at its own start', k + 1)
needle = '# 441_404..443_603 is REFUSED at its own start by the W193'
print('needle in chunk:', chunk.count(needle))
print('441_404 count in chunk:', chunk.count('441_404'))
print('441_404..443_603 count:', chunk.count('441_404..443_603'))
