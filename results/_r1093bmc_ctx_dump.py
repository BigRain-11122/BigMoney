# -*- coding: utf-8 -*-
import json
d = json.load(open('results/_r1093bmc_needle_preflight.json'))
for k in ('r1088', 'r1089', 'r1090', 'b9ad2f1119', 'authored 13:1x', 'r1089 MSG-',
          'pre-seat probe', '12:3x', '13:5x', '14:0x', 'cycle COMPLETE', '13:1x', 'W269p'):
    print('====', k, '====')
    for c in d['contexts'].get(k, [])[:22]:
        print(f"  L{c['line']}: {c['text'][:195]}")
