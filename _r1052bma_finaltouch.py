#!/usr/bin/env python
# r1052 bm-a final touch -- consume bm-c's W267 seat MSG (move to processed/
# per inbox law; the yield adjudication IS the consumption) + refresh the
# heartbeat epoch/ts face to the true closeout minute.
# -*- coding: utf-8 -*-
import json
import os
import shutil
import time
from datetime import datetime, timezone, timedelta

BASE = os.path.dirname(os.path.abspath(__file__))
TZ = timezone(timedelta(hours=8))
NOW = datetime.now(TZ).strftime('%Y-%m-%dT%H:%M:%S+08:00')
EPOCH = int(time.time())

SRC = os.path.join(BASE, 'fleet', 'inbox', 'MSG-20261018-1025-bmc-w267-seat.md')
DST = os.path.join(BASE, 'fleet', 'inbox', 'processed', 'MSG-20261018-1025-bmc-w267-seat.md')
assert os.path.isfile(SRC), 'seat MSG not in inbox (already moved?)'
os.makedirs(os.path.dirname(DST), exist_ok=True)
assert not os.path.exists(DST), 'processed target already exists'
shutil.move(SRC, DST)
assert os.path.isfile(DST) and not os.path.exists(SRC)

HEART = os.path.join(BASE, 'fleet', 'machines', 'bm-a.json')
with open(HEART, encoding='utf-8') as fh:
    d = json.load(fh)
d['heartbeat_epoch_utc'] = EPOCH
d['heartbeat_epoch_utc_type_int'] = True
d['clock_read'] = NOW
d['ts'] = NOW
d['updated'] = NOW
d['updated_at'] = NOW
d['last_seen'] = NOW
tmp = HEART + '.tmp'
with open(tmp, 'w', encoding='utf-8') as fh:
    json.dump(d, fh, ensure_ascii=False, indent=1)
os.replace(tmp, HEART)
with open(HEART, encoding='utf-8') as fh:
    c = json.load(fh)
assert isinstance(c['heartbeat_epoch_utc'], int) and c['heartbeat_epoch_utc'] == EPOCH
assert 'MSG-20261018-1025-bmc-w267-seat.md' in c['notes_r1052']

print('FINAL-TOUCH-OK %s epoch=%d' % (NOW, EPOCH))
