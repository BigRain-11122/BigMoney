import json, glob
rows = []
for f in sorted(glob.glob('fleet/tasks/T-*.json')):
    with open(f, encoding='utf-8-sig') as fh:
        t = json.load(fh)
    rows.append((t.get('id'), t.get('status'), t.get('claimed_by', '') or '', t.get('priority', '')))
open_cnt = 0
for r in rows:
    if r[1] in ('open', 'claimed', 'in_progress'):
        open_cnt += 1
        print('ACTIVE:', json.dumps(r, ensure_ascii=False))
print('TOTAL_TICKETS:', len(rows), 'ACTIVE:', open_cnt)
print('NON_DONE:')
for r in rows:
    if r[1] not in ('done', 'closed'):
        print(' ', json.dumps(r, ensure_ascii=False))
