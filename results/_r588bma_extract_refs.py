# r588 helper: extract W109 reference pieces for W110 freeze adaptation
src = open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()

# 1. W109 WAVE_CONFIGS entry
i = src.find('109: {"batch": "PERPETUAL-N1-W109"')
eoc = src.find('"engine_owner": "bm-b"', i)
j = src.find('}', eoc) + 1
blk = src[i:j]
open('results/_r588bma_w109_cfg_ref.txt', 'w', encoding='utf-8', newline='\n').write(blk)
print('== W109 WAVE_CONFIGS entry ==')
print(blk)
print('== tail-check: next entry starts ==')
print(repr(src[j:j+40]))

# 2. W109 summary list segment
k = src.find('W109 materializer face [')
kstart = src.rfind('"', 0, k)
kend = src.find(']', k)
kend2 = src.find('"', kend)
seg = src[kstart:kend2+1]
open('results/_r588bma_w109_sum_ref.txt', 'w', encoding='utf-8', newline='\n').write(seg)
print('== W109 summary segment ==')
print(seg[:200], '...')
print('== after ==')
print(repr(src[kend2:kend2+60]))

# 3. canon row in PERPETUAL_FACES.md
law = open('research/PERPETUAL_FACES.md', encoding='utf-8').read()
m = law.find('- N1 \u6ce2109\uff08')
mend = law.find('\n', m)
print('== canon W109 row ==')
print(law[m:mend])
print('== next line ==')
print(law[mend:mend+120])
open('results/_r588bma_w109_canon_ref.txt', 'w', encoding='utf-8', newline='\n').write(law[m:mend])
