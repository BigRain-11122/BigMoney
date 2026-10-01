import json, glob, os
rows = []
for f in sorted(glob.glob('fleet/tasks/*.json')):
    try:
        t = json.load(open(f, encoding='utf-8'))
        st = t.get('status', '?')
        own = t.get('claimed_by', '')
        if st in ('open', 'claimed', 'in_progress'):
            title = t.get('title', t.get('subject', ''))[:80]
            rows.append((os.path.basename(f), st, own, title))
    except Exception as e:
        rows.append((os.path.basename(f), 'ERR', '', str(e)[:60]))
for r in rows:
    print(' | '.join(r))
if not rows:
    print('(no open/claimed tickets)')
