import re
src = open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = src.find('def finalize()')
j = src.find('def probe()')
print(src[i:j])
