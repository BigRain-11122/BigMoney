# -*- coding: utf-8 -*-
import io
t = io.open('results/_w244bma_freeze_edits.py', encoding='utf-8').read()
pats = [
 'r1002','r1003','r1004','r1005','r1006','r1007','01:4x','20:4x',
 '260ffd3f8','70141bc22','08df387e0','6207e60e9','MSG-20261015-0206','_w244bma_20261015',
 'thirty-third','233 + candidate','owner_rows=233','== 233','233/125/67','bma_ordinal=126',
 '125 + candidate','126th','one hundred and twenty-sixth','ONE HUNDRED AND TWENTY-SIXTH',
 'TWO HUNDRED AND FORTY-FOURTH','958,935','958_935','532,520','532_520',
 'W242/W241','(242, 241','range(232, 243)','range(209, 245)',
 'if w < 244)','if w < 243)','w<244','w<243',
 'range(16, 244)','range(17, 244)','range(16,244)','range(17,244)','below 244','below-244',
 '_c243','PERPETUAL-N1-W244','PERPETUAL_N1_W244','PERPETUAL_N1_W243','N1_BANDS.get(243)',
 'n3r1_used244','arith_a244','arith_b244','n1w244','n1_w244','n1_w243',
 'WAVE_CONFIGS[244]','WAVE_CONFIGS[243]','_set_wave(244)',
 '"wave": 244','244: {"batch"','243: {"batch"','244: {{"a"','244: {"a"','243: {"a"',
 'W244','W243','W242','w244','w243','w242','N1_BANDS[243]','N1_BANDS[242]','N1_BANDS[241]',
 'N1_BANDS[240]','N1_BANDS[239]','N1_BANDS[238]','N1_BANDS[237]','N1_BANDS[236]',
]
for p in pats:
    c = t.count(p)
    print(repr(p), '->', c)
