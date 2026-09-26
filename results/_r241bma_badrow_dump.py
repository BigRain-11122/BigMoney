# -*- coding: utf-8 -*-
"""R241: dump full T-27-VETO-FIELD post_review rows for re-derivation."""
import io
import json

for i, line in enumerate(io.open('results/post_review.jsonl', encoding='utf-8')):
    if not line.strip():
        continue
    r = json.loads(line)
    v = str(r.get('verdict', r.get('status', '?')))
    if v.upper() == 'NO' or '✗' in v:
        print(f'--- row {i} ---')
        print(json.dumps(r, ensure_ascii=False, indent=1))
