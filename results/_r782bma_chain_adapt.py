# -*- coding: utf-8 -*-
src = open('results/_r781bma_s6_chain.py', encoding='utf-8').read()
src = src.replace('r781 bm-a; bloodline', 'r782 bm-a; bloodline')
src = src.replace('"round": 781', '"round": 782')
src = src.replace('_r781bma_s6_facts.json', '_r782bma_s6_facts.json')
open('results/_r782bma_s6_chain.py', 'w', encoding='utf-8', newline='').write(src)
print('chain script ready')
