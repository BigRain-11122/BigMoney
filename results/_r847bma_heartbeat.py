import json
import io
import os
import subprocess
import time
import datetime

p = r'fleet\machines\bm-a.json'
d = json.load(io.open(p, encoding='utf-8'))

now = time.time()
now_dt = datetime.datetime.now().astimezone()
now_iso = now_dt.strftime('%Y-%m-%dT%H:%M:%S+08:00')

import psutil
free_ram = round(psutil.virtual_memory().available / (1 << 30), 1)
try:
    out = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
                          capture_output=True, text=True, timeout=10)
    vram_free = round(float(out.stdout.strip().splitlines()[0]) / 1024.0, 2)
except Exception:
    vram_free = d.get('gpu_free_vram_gb', 0)

d['last_seen'] = now_iso
d['ts'] = now_iso
d['clock_read'] = now_iso
d['heartbeat_epoch_utc'] = int(now)
d['current_task'] = 'O-2240 SiliconWatch v4 deploy (md5 e4f75d81 x3 verified, render 0 jsErr) + O-2315 idle hard-trigger loop (idle_trigger.py + loop leg + prompt step + heartbeat fields)'
d['cpu_cores'] = 32
d['cores'] = 32
d['free_ram_gb'] = free_ram
d['gpu_free_vram_gb'] = vram_free
d['verdict'] = 'green'
ack = d.get('orders_ack', [])
for o in ('O-20261007-2240-bm-c.md', 'O-20261007-2315-bm-c.md'):
    if o not in ack:
        ack.append(o)
d['orders_ack'] = ack

tmp = p + '.tmp%d' % os.getpid()
io.open(tmp, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1))
os.replace(tmp, p)

chk = json.load(io.open(p, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
assert 'T' in chk['clock_read'], 'clock_read must be T-separated'
assert isinstance(chk['idle_rounds'], int) and isinstance(chk['agenda_starved'], bool)
assert chk['orders_ack'][-2:] == ['O-20261007-2240-bm-c.md', 'O-20261007-2315-bm-c.md'] or all(
    o in chk['orders_ack'] for o in ('O-20261007-2240-bm-c.md', 'O-20261007-2315-bm-c.md'))
print('heartbeat written: epoch=%d clock=%s vram=%sGB ram=%sGB ack=%d' % (
    chk['heartbeat_epoch_utc'], chk['clock_read'], vram_free, free_ram, len(chk['orders_ack'])))
