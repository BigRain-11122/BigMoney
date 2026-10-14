# -*- coding: utf-8 -*-
# debug recount for W244 derive (r982 count-fixes lineage)
import json, io

src = io.open('results/_w244bma_prereg_derive.py', encoding='utf-8').read()
head = src.split('# ---------- apply ----------')[0]
mid = src.split('# ---------- apply ----------')[1].split('# legal retained counts')[0]

ns = {}
exec(head + mid + r'''
import json as _dbg
keys = ['555_501..557_500','541_901..542_100','542_001..542_200','sixth consecutive','0206-bma','08df387e0',
'958,935','956,735','954,535','W2..W243','W1..W243','241 行','01:4x','20:4x','第 126 枚','第 234 波',
'池第 242 枚','parity 102 行','共二百四十一面','二百四十一行','534,720 投影','532,520+2,200',
'553_501..555_500','541_701..541_900','连续第五个 seed-gap','owner rows 233','engine_owner 行 233',
'n1_w243_results.json','n1_w244_results.json','n1_w240_results.json','n1_w241_results.json','n1_w242_results.json',
'_w244bma','_w243bma','v2..W243','W5..W243','W136..W243','17:3x','19:5x','PERPETUAL-N1-W244',
'PERPETUAL_N1_W244','n1_w244/shard','553501','541701','_w243bma_freeze_edits.py','_w244bma_freeze_edits.py']
print(_dbg.dumps({k: out.count(k) for k in keys}, ensure_ascii=False, indent=0))
''', ns)
