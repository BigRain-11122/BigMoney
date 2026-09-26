import json, glob
open_tickets = []
for f in sorted(glob.glob('fleet/tasks/*.json')):
    try:
        t = json.load(open(f, encoding='utf-8-sig'))
    except Exception as ex:
        print('PARSE-FAIL', f, ex)
        continue
    st = t.get('status', '?')
    if st not in ('done', 'closed', 'rejected'):
        open_tickets.append((f, st, t.get('claimed_by', ''), t.get('title', t.get('subject', ''))[:80]))
for f, st, cb, ti in open_tickets:
    print('OPEN:', f, '->', st, '|', cb, '|', ti)
print('total files:', len(glob.glob('fleet/tasks/*.json')), 'open:', len(open_tickets))
