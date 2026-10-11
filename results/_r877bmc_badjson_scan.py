# -*- coding: utf-8 -*-
# r877 bm-c: find the malformed paper JSON that broke strategy_scorecard
import glob
import json
import os

bad = []
for p in glob.glob(r'results\paper\**\*.json', recursive=True) + \
         glob.glob(r'results\*_paper\*.json') + \
         glob.glob(r'results\paper\*.json'):
    try:
        with open(p, encoding='utf-8') as fh:
            json.load(fh)
    except Exception as e:
        bad.append((p, str(e)))
print('scanned:', len(glob.glob(r'results\paper\**\*.json', recursive=True)))
print('BAD:', len(bad))
for p, e in bad:
    print(p, '|', e, '| size', os.path.getsize(p), '| mtime',
          os.path.getmtime(p))
