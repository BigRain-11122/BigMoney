# -*- coding: utf-8 -*-
import json, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
d = json.load(open('results/perpetual_faces/n1_w186_results.json', encoding='utf-8'))
def find(o, key, p=''):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == key:
                print(p + '.' + k, '=', v)
            find(v, key, p + '.' + k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            find(v, key, p + '[%d]' % i)
find(d, 'voids_applied')
find(d, 'ledger')
