# -*- coding: utf-8 -*-
"""r162 bm-c heartbeat updater (r161 kenglu lawful form: %z slice + exact assert)."""
import json, time, datetime, os

p = 'fleet/machines/bm-c.json'
now = datetime.datetime.now().astimezone()
s = now.strftime('%Y-%m-%dT%H:%M:%S%z')  # Windows %z -> "+0800" 5-tail
clock = s[:19] + '+' + s[20:22] + ':' + s[22:24]  # r161 lawful slice
assert clock.endswith('+08:00'), f'bad clock format: {clock}'
datetime.datetime.fromisoformat(clock)  # parse-level assert

d = json.load(open(p, encoding='utf-8'))
epoch = int(time.time())
d['heartbeat_epoch_utc'] = epoch
d['clock_read'] = clock
d['last_seen'] = clock
d['round_no'] = 162
d['current_task'] = ('r162 closed: W5 supply-prep parked (no-draft ruling honored; '
                     'probe+digest+draft ready zero-prep-latency) + MSG-1215 acked + S6 30 legs rc=0; '
                     'next = 15:35 fund_premium first-fire + new-bar relay + W5 freeze-trigger watch')
d['verdict'] = ('green-maintenance + W5 supply-prep parked under capacity-law ruling '
                '(board 0 open + pool 2 ready bmb lanes + judge faces all bmb RAM-gated '
                '= zero bm-c-claimable 15-round; W4 generate bmb fix-relaunch window; '
                'bma silent 137min MSG-1042 plan holds till 15:35+)')
d['cpu_cores'] = os.cpu_count()
try:
    import psutil
    d['free_ram_gb'] = round(psutil.virtual_memory().available / (1024 ** 3), 1)
    d['cpu_util_pct'] = psutil.cpu_percent(interval=0.5)
except Exception as ex:
    print('psutil skip:', ex)

json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

d2 = json.load(open(p, encoding='utf-8'))
ep = d2['heartbeat_epoch_utc']
cl = d2['clock_read']
assert isinstance(ep, int), 'epoch not int!'
assert datetime.datetime.fromisoformat(cl), 'clock unparseable'
print('heartbeat OK: epoch int', ep, '| clock', cl,
      '| free_ram_gb', d2.get('free_ram_gb'), '| cpu_util_pct', d2.get('cpu_util_pct'),
      '| cores', d2.get('cpu_cores'))
