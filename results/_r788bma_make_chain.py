# r788 bm-a: create S6 chain script from r787 bloodline (round number + output file fix)
src = open('results/_r787bma_s6_chain.py', encoding='utf-8').read()
src = src.replace('r787 bm-a; bloodline = r783 verbatim 38 legs',
                  'r788 bm-a; bloodline = r783 verbatim 38 legs; W162 finalize round')
src = src.replace('"round": 786', '"round": 788')
src = src.replace('_r786bma_s6_facts.json', '_r788bma_s6_facts.json')
open('results/_r788bma_s6_chain.py', 'w', encoding='utf-8').write(src)
import re
assert '"round": 788' in src and '_r788bma_s6_facts.json' in src
print('written r788 chain OK')
