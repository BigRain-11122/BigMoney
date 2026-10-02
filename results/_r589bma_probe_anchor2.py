# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
raw = open('scripts/perpetual_faces.py', encoding='utf-8').read()
i = raw.find('109: {"a": (261_004')
print('pf W109 row idx:', i)
print(repr(raw[i - 130:i + 340]))
raw2 = open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
j = raw2.find('"shard_subdir": "n1_w109"')
print('n1 W109 cfg idx:', j)
print(repr(raw2[j - 120:j + 200]))
