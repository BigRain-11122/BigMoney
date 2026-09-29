"""r442 bm-b: mid-round heartbeat update (in-flight marker, concurrent-
session backoff signal); epoch int + T-separated clock_read law."""
import json
import time
import datetime

p = 'fleet/machines/bm-b.json'
hb = json.load(open(p, encoding='utf-8'))
now = datetime.datetime.now().astimezone()
hb['last_seen'] = now.strftime('%Y-%m-%d %H:%M:%S')
hb['heartbeat_epoch_utc'] = int(time.time())
hb['clock_read'] = now.isoformat(timespec='seconds')
hb['current_task'] = ('r442 IN FLIGHT (interactive session alive): '
                      'W11 runner slice-1 built (trial_labor_w11.py '
                      'fourteen-tuple STD axis, compiles, funnel threaded), '
                      'selftest conversion in progress -- DO NOT start a '
                      'concurrent round 442; back off and wait for state '
                      'round_no increment')
hb['round_no'] = 441
hb['round'] = 441
hb['loop_round'] = 441
json.dump(hb, open(p, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
# self-verify law
hb2 = json.load(open(p, encoding='utf-8'))
e = hb2['heartbeat_epoch_utc']
assert isinstance(e, int) and not isinstance(e, bool), e
assert 'T' in hb2['clock_read'], hb2['clock_read']
print('heartbeat ok: epoch', e, 'int:', isinstance(e, int),
      'clock:', hb2['clock_read'])
