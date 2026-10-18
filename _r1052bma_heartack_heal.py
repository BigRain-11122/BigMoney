#!/usr/bin/env python
# r1052 bm-a: heartbeat orders_ack heal -- r1051 closeout appended the
# O-20261018-0948-bm-a.md ack to state-bm-a.json but MISSED the heartbeat
# face (fleet/machines/bm-a.json), so orders_ack_scan.py (which reads the
# heartbeat) flags a false P0 unacked debt at round start. The order was
# genuinely consumed same-round at r1051 (v2 pull+face verify+census 407);
# this script completes the receipt face only. Also syncs the stale
# last_orders_*/last_decisions_* mirror fields from the state canonical
# face (heartbeat carried r1049-era sha values). Validate-then-atomic-write
# per r504 law. Read-only on state; single-writer on heartbeat (this
# round session owns it per S7 law).
import json
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
HEART = os.path.join(BASE, 'fleet', 'machines', 'bm-a.json')
STATE = os.path.join(BASE, 'state-bm-a.json')
TARGET = 'O-20261018-0948-bm-a.md'

with open(HEART, encoding='utf-8') as fh:
    heart = json.load(fh)
with open(STATE, encoding='utf-8') as fh:
    state = json.load(fh)

pre = dict(heart)
ack = list(heart.get('orders_ack', []))
appended = TARGET not in ack
if appended:
    ack.append(TARGET)
heart['orders_ack'] = ack
heart['orders_ack_last'] = TARGET

synced = {}
for k in ('last_decisions_sha', 'last_orders_sha', 'last_decisions_ts',
          'last_decisions_at', 'last_decisions_read_at', 'last_orders_ts',
          'last_orders_at', 'last_orders_read_at'):
    if k in state and heart.get(k) != state[k]:
        synced[k] = (heart.get(k), state[k])
        heart[k] = state[k]

# sanity gates before write: state canonical values must be the r1051 faces
assert state.get('last_orders_sha', '').startswith('af206ff3'), \
    'state last_orders_sha unexpected: %r' % state.get('last_orders_sha')
assert state.get('last_decisions_sha', '').startswith('0ad85a30'), \
    'state last_decisions_sha unexpected: %r' % state.get('last_decisions_sha')

tmp = HEART + '.tmp'
with open(tmp, 'w', encoding='utf-8') as fh:
    json.dump(heart, fh, ensure_ascii=False, indent=1)
os.replace(tmp, HEART)

# post-write validation (re-read + assertions)
with open(HEART, encoding='utf-8') as fh:
    check = json.load(fh)
assert isinstance(check.get('orders_ack'), list)
assert TARGET in check['orders_ack']
assert check.get('orders_ack_last') == TARGET
assert check.get('last_orders_sha') == state['last_orders_sha']
assert isinstance(check.get('heartbeat_epoch_utc'), int)

print('HEAL-OK appended=%s ack_count=%d ack_last=%s' %
      (appended, len(check['orders_ack']), check['orders_ack_last']))
print('SYNCED-FIELDS=%d' % len(synced))
for k in sorted(synced):
    print('  %s: %s -> %s' % (k, synced[k][0], synced[k][1]))
