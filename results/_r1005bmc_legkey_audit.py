# -*- coding: utf-8 -*-
# r1005 heal probe: cross-check every legN key read in _w241bmc_freeze_edits.py
# against the actual probe receipt keys (E63-family assert-shape drift audit).
import json, re
d = json.load(open(r'results\_w241bmc_20261014_probe_receipt.json', encoding='utf-8'))
src = open(r'results\_w241bmc_freeze_edits.py', encoding='utf-8').read()
reads = set(re.findall(r"leg(\d)\.get\(['\"]([^'\"]+)['\"]\)", src))
reads |= set(re.findall(r"leg(\d)\[['\"]([^'\"]+)['\"]\]", src))
missing = []
for ln, k in sorted(reads):
    legs = d['legs']
    if ln in legs:
        ok = k in legs[ln]
        print(f'leg{ln}.{k}: ' + ('OK' if ok else 'MISSING'))
        if not ok:
            missing.append((ln, k))
    else:
        print(f'leg{ln}: MISSING LEG')
        missing.append((ln, k))
print('---receipt legs available---')
for lk, lv in d['legs'].items():
    print(f'leg {lk} keys: {sorted(lv.keys())}')
print('---MISSING LIST---')
print(json.dumps(missing))
