# -*- coding: utf-8 -*-
"""r382 bm-c W113 prereg anchor extraction: print the W111 finalize measured
keys (latest landed finalize = prereg sec.5 prediction anchor per r576)."""
import json

d = json.load(open('results/perpetual_faces/n1_w111_results.json', encoding='utf-8'))

def walk(o, p=''):
    if isinstance(o, dict):
        for k, v in o.items():
            walk(v, f'{p}.{k}' if p else k)
    elif isinstance(o, list):
        pass  # per-run families live in shard files, not the finalize merge
    elif isinstance(o, (int, float)) and not isinstance(o, bool):
        print(f'{p} = {o!r}')
    elif isinstance(o, str) and len(o) < 90:
        print(f'{p} = {o!r}')

walk(d)
