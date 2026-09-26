# -*- coding: utf-8 -*-
"""R241 S2 board probe: watermark red flag + open/claimed fleet tickets."""
import io
import json
import glob

print('=== watermark_red ===')
try:
    w = json.load(io.open('results/watermark_red.json', encoding='utf-8'))
    print(json.dumps(w, ensure_ascii=False)[:500])
except Exception as e:
    print('ERR', e)

print()
print('=== fleet tasks (open/claimed) ===')
for p in sorted(glob.glob('fleet/tasks/*.json')):
    try:
        t = json.load(io.open(p, encoding='utf-8'))
        s = t.get('status')
        if s in ('open', 'claimed'):
            pri = t.get('priority', '')
            cl = t.get('claimed_by', '')
            title = t.get('title', t.get('subject', ''))[:90]
            print(f"{t.get('id', '?')} [{s}] pri={pri} claimed_by={cl} | {title}")
    except Exception as e:
        print(p, 'ERR', e)

print()
print('=== post_review pending rows ===')
try:
    for line in io.open('results/post_review.jsonl', encoding='utf-8'):
        if not line.strip():
            continue
        r = json.loads(line)
        st = str(r.get('status', r.get('verdict', '')))
        if 'WAIT' in st.upper() or 'PENDING' in st.upper():
            print(r.get('id', r.get('ticket', '?')), st[:60])
except Exception as e:
    print('ERR', e)
