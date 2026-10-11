import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
src = open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
i = src.find('"finalize"')
print(repr(src[i-1200:i+600]))
