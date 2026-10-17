# -*- coding: utf-8 -*-
import json, io, time
p = r'fleet\machines\bm-b.json'
with io.open(p, 'r', encoding='utf-8') as f:
    d = json.load(f)
epoch = int(time.time())
d['heartbeat_epoch_utc'] = epoch
ts = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
d['clock_read'] = ts
d['ts'] = ts
d['last_seen'] = ts
with io.open(p, 'w', encoding='utf-8', newline='') as f:
    json.dump(d, f, ensure_ascii=False, indent=1)
# self-verify per S7 law
with io.open(p, 'r', encoding='utf-8') as f:
    d2 = json.load(f)
assert isinstance(d2['heartbeat_epoch_utc'], int), 'epoch not int'
assert 'T' in d2['clock_read'], 'clock_read missing T separator'
print('EPOCH_FIXED=' + str(epoch) + ' TS=' + ts + ' VERIFY_OK')
