import json
import time

PATH = r'fleet\machines\bm-a.json'
d = json.load(open(PATH, encoding='utf-8'))
epoch = int(time.time())
d['last_seen'] = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
d['verdict'] = 'idle-healthy golden-week (r661 guard round: S6 31 legs rc0, board clear, pool 3-ready=bm-b in-flight no-touch)'
d['current_task'] = ('r661: guard round S6 all-green + production-line inventory; '
                     'next=10-05 V-NULLS finalize watch + 10-08 open-window dual-jump (run-11/run-7)')
d['heartbeat_epoch_utc'] = epoch
d['clock_read'] = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
d['round_no'] = 661
if 'cpu_cores' not in d:
    d['cpu_cores'] = 32

json.dump(d, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# post-write self-checks
chk = json.load(open(PATH, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
assert 'T' in chk['clock_read'], 'clock_read must be T-separated ISO 8601'
print('heartbeat updated: epoch=%d (int PASS), clock=%s, round_no=%d' % (
    chk['heartbeat_epoch_utc'], chk['clock_read'], chk['round_no']))
