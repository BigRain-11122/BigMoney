import json, os, datetime

# orders double-scan (S7)
acks = json.load(open('fleet/machines/bm-b.json', encoding='utf-8')).get('orders_ack', [])
orders = sorted(f for f in os.listdir('fleet/orders') if f.startswith('O-') and f.endswith('.md'))
new = [o for o in orders if o not in acks]
print('S7 orders double-scan:', len(orders), 'total,', len(new), 'NEW')
for o in new:
    print('NEW:', o)

# state round_no ++
s = json.load(open('state.json', encoding='utf-8'))
s['round_no'] = int(s.get('round_no', 0)) + 1
s['round_no_label'] = 'round %d (bm-b)' % s['round_no']
now = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
for k in ('last_round_at', 'last_round_ts', 'last_seen', 'ts', 'updated', 'updated_at'):
    s[k] = now
s['last_decisions_sha'] = s['last_decisions_sha'].lower()  # normalize case (r613 D-19 lesson)
s['note'] = ('r613: T-155 DIVLOWVOL runner built+ignited (selftest 31/31, probe 16/16, t0 pin '
             'reproduced, 4 pool entries); S6 34/34 rc0; prereg sec.2 prose slip disclosed '
             '(judgment faces unchanged)')
with open('state.json', 'w', encoding='utf-8', newline='\n') as f:
    json.dump(s, f, ensure_ascii=False, indent=1)
print('state round_no ->', s['round_no'], '| sha normalized lowercase')
