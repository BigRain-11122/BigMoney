import re
t = open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
for m in re.finditer(r'"a_seed_base": ([0-9_]+)', t):
    print(m.group(0))
