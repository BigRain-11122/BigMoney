# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
t2 = open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
# find the selftest materializer leg insertion region
q = t2.find('T-141 s2 lane face')
print('T-141 face idx:', q)
print(repr(t2[q-120:q+60]))
print('count newline+4sp+T141:', t2.count('\n    # --- T-141 s2 lane face'))
print('count newline+T141:', t2.count('\n# --- T-141 s2 lane face'))
# where does W69 leg sit?
r = t2.find('W69 materializer face')
print('W69 leg idx:', r)
print(repr(t2[r-160:r+80]))
# check what immediately precedes the T-141 module-level face
print('--- 400 chars before T-141 ---')
print(repr(t2[q-400:q-200]))
