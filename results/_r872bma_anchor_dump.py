# -*- coding: utf-8 -*-
import json, io, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
d = json.load(io.open(r'results\_r872bma_back183_expect_dump.json', encoding='utf-8'))
m = dict(d['BACK183'])
for tok in ['@ANCHOR@', '@S5ANCH@', '@CLAIMLAW@', '@MERGE@', '@GATEW@', '@VAC@', '@R250@', '@WAVEFREE@', '@TITLE@', '@SCANFACE@']:
    print('=' * 14, tok, '=' * 14)
    print(m[tok])
