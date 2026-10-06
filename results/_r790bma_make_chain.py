import io
src = io.open(r'results\_r788bma_s6_chain.py', encoding='utf-8').read()
out = src.replace('_r788bma', '_r790bma').replace('"round": 788', '"round": 790').replace('r788 bm-a; bloodline = r783', 'r790 bm-a; bloodline = r788')
io.open(r'results\_r790bma_s6_chain.py', 'w', encoding='utf-8', newline='').write(out)
print('written', len(out))
