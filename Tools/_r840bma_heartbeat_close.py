# r840 bm-a heartbeat close: round counters, epoch int, clock_read T-format, orders_ack append
import json, time, datetime

HB = 'fleet/machines/bm-a.json'
with open(HB, encoding='utf-8') as fh:
    d = json.load(fh)

now = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
epoch = int(time.time())
d['round_no'] = 840
d['round'] = 840
d['last_round'] = 'r840'
d['loop_round'] = 'r840'
d['last_seen'] = now
d['clock_read'] = now
d['ts'] = now
d['heartbeat_epoch_utc'] = epoch
d['verdict'] = ('healthy; smoke 48/48; O-20261008-1300 executed same-round (orphan_face_probe v1.1 '
                'live, orphan face=0); engine alive idle (W14-JUDGE in-flight on bm-c); holiday '
                'cutoff 2026-09-30; 10-08 reopen re-arm due')
d['current_task'] = ('W177 seat chain next window + 10-08 market reopen data-chain re-arm; '
                     'orphan probe now round-zero standing item (O-1300)')
ack = d.get('orders_ack', [])
if isinstance(ack, list) and 'O-20261008-1300-bm-c.md' not in ack:
    ack.append('O-20261008-1300-bm-c.md')
d['orders_ack'] = ack

with open(HB, 'w', encoding='utf-8', newline='\n') as fh:
    json.dump(d, fh, ensure_ascii=False, indent=2)

# self-check: epoch must be JSON int, clock_read must contain 'T'
chk = json.load(open(HB, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch not int (R170/R178 law)'
assert 'T' in chk['clock_read'], 'clock_read not T-separated (R262 law)'
assert chk['clock_read'] == chk['ts'], 'ts/clock_read same-source law'
assert 'O-20261008-1300-bm-c.md' in chk['orders_ack']
print('heartbeat ok: round 840, epoch', chk['heartbeat_epoch_utc'], 'int, clock', chk['clock_read'])
