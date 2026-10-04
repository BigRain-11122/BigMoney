# r684 bm-b: scan fleet/tasks for open tickets (S2 board check)
import json, os, sys

tasks_dir = r'fleet/tasks'
open_t, claimed_recent = [], []
for fn in sorted(os.listdir(tasks_dir)):
    if not fn.endswith('.json'):
        continue
    p = os.path.join(tasks_dir, fn)
    try:
        t = json.load(open(p, encoding='utf-8'))
    except Exception as e:
        print('BAD_JSON', fn, e)
        continue
    st = t.get('status', '')
    if st == 'open':
        open_t.append((fn, str(t.get('title', t.get('subject', '')))[:80]))
    elif st in ('claimed', 'in_progress'):
        claimed_recent.append((fn, t.get('claimed_by', '?'), st, str(t.get('title', t.get('subject', '')))[:60]))

print('OPEN_COUNT', len(open_t))
for fn, ti in open_t:
    print('OPEN', fn, '|', ti)
print('---claimed/in_progress (mine first)---')
mine = [c for c in claimed_recent if c[1] == 'bm-b']
print('MINE_ACTIVE', len(mine))
for c in mine:
    print('MINE', c[0], c[2], '|', c[3])
