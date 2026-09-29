import json
from datetime import datetime, timezone, timedelta

tz = timezone(timedelta(hours=8))
now = datetime.now(tz)
iso = now.strftime('%Y-%m-%dT%H:%M:%S+08:00')
ts = now.strftime('%Y-%m-%d %H:%M:%S')

# state.json round increment (bm-b face)
p = r'state.json'
d = json.load(open(p, encoding='utf-8'))
d['round_no'] = 416
d['note'] = ('r416: W6 48h CEO report landed docs/trial_labor/CEO-REPORT-WAVE6-20260929.md '
             '(judge 08:14:22 -> deadline 2026-10-01 08:14:22, ~47h early; 3,952->293->0/0, E[FP]=14.65, ledger 333,432 live-verified; '
             'VCONF surge>none>dry 8.78/7.27/6.11% screen-face direction holds, judge all-zero; prereg sec.5 null-median 0.5036>0.50 first miss disclosed) '
             '+ W6 attrition 2 rows (SCREEN+JUDGE, history 6->8) + W6 prereg sec.7/8 one-shot backfill (first wave ever backfilled; W1-W5 5-wave sec.7 drift debt disclosed) '
             '+ S6 34 legs rc=0 (dualrun real-drift observation streak-reset, comp_audit FLAG:supply_floor pool 0-ready floor-3 breach) '
             '+ S7 trio green (loop pin=2 running, watchdog 09:10, claw in-sync); next: W7 trial-labor draft berth (standing line, supply_floor carrier), 09:15 minute-feed first-live window watch')
d['last_round_at'] = iso
d['last_round_ts'] = iso
d['ts'] = ts
json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('state.json round_no ->', d['round_no'])

# heartbeat update (fleet face)
epoch = int(now.timestamp())
hb = json.load(open(r'fleet\machines\bm-b.json', encoding='utf-8'))
hb['last_seen'] = iso
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = iso
hb['current_task'] = ('round 416 closed: W6 48h CEO report landed (CEO-REPORT-WAVE6, ~47h early) + W6 attrition 2 rows + prereg sec.7/8 backfill (W1-W5 drift debt disclosed). '
                       'Next: W7 trial-labor draft berth (TRIAL_LABOR_LAW standing line, comp_audit supply_floor flag carrier), 09:15 T-104 minute-feed first-live window (bm-b lane)')
hb['round_no'] = 416
hb['loop_round'] = 416
hb['round'] = 416
hb['n_orders_ack'] = len(hb.get('orders_ack', []))
assert isinstance(hb['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
json.dump(hb, open(r'fleet\machines\bm-b.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('heartbeat updated, epoch int:', hb['heartbeat_epoch_utc'], 'orders_ack:', hb['n_orders_ack'])
