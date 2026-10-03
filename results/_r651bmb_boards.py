# -*- coding: ascii -*-
# r651 bm-b: fleet tasks board open-scan + inbox unread scan (probe-to-file law)
import json, os, glob

print('---TASKS---')
for p in sorted(glob.glob('fleet/tasks/*.json')):
    try:
        j = json.load(open(p, encoding='utf-8'))
    except Exception as e:
        print('ERR', p, repr(e)[:80]); continue
    st = j.get('status')
    if st in ('open', 'claimed', 'in_progress'):
        sub = j.get('subject') or j.get('title') or ''
        desc = (j.get('description') or '')[:100]
        claimed = j.get('claimed_by') or ''
        print(f"{os.path.basename(p)} | {st} | claimed_by={claimed} | {sub} | {desc}")

print('---INBOX---')
ib = 'fleet/inbox'
pr = 'fleet/inbox/processed'
done = set(os.listdir(pr)) if os.path.isdir(pr) else set()
for p in sorted(glob.glob(ib + '/*.md')) + sorted(glob.glob(ib + '/*.json')):
    n = os.path.basename(p)
    print(('PROCESSED? ' if n in done else 'UNREAD ') + n)
for p in sorted(glob.glob(ib + '/*.md')) + sorted(glob.glob(ib + '/*.json')):
    pass
