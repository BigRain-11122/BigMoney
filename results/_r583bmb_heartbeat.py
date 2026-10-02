import json, subprocess, os, datetime

out = subprocess.check_output(['git', 'show', 'HEAD:fleet/machines/bm-b.json'])
hb = json.loads(out.decode('utf-8'))
ack = hb.get('orders_ack', [])
print('orders_ack count from git HEAD:', len(ack))
print('first 3:', ack[:3])
print('last 3:', ack[-3:])

now = datetime.datetime.now().astimezone()
import time
hb['machine_id'] = 'bm-b'
hb['last_seen'] = now.isoformat(timespec='seconds')
hb['heartbeat_epoch_utc'] = int(time.time())
hb['clock_read'] = now.isoformat(timespec='seconds')
hb['current_task'] = 'W100 engine burn in flight (tick self-ignited, shards landing); W97 finalize landed -> W98 bm-a unblocked'
hb['cpu_cores'] = 16
hb['ram_avail_gb'] = 5.4
hb['gpu_vram_free'] = '2250MiB'
hb['verdict'] = 'healthy: chain W98/W99/W100/W101 all registered in-flight; engine saturated (perpetual nulls line); pool empty by design'
assert isinstance(hb['heartbeat_epoch_utc'], int), 'epoch must be int'
assert 'T' in hb['clock_read'], 'clock_read must be T-separated'
with open('fleet/machines/bm-b.json', 'wb') as f:
    f.write(json.dumps(hb, ensure_ascii=False, indent=1).encode('utf-8'))
print('heartbeat rewritten; orders_ack preserved:', len(hb['orders_ack']))
chk = json.load(open('fleet/machines/bm-b.json', encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int)
print('self-check PASS: epoch int =', chk['heartbeat_epoch_utc'])
