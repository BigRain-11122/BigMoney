import re
src = open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = src.find('def main()')
print(src[i:i+2600])
