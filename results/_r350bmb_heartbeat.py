# -*- coding: utf-8 -*-
import json, time, psutil, subprocess
from datetime import datetime, timezone, timedelta

p = r'fleet/machines/bm-b.json'
h = json.load(open(p, encoding='utf-8'))
mem = psutil.virtual_memory()
try:
    out = subprocess.run(['nvidia-smi', '--query-gpu=memory.total,memory.used', '--format=csv,noheader,nounits'],
                         capture_output=True, text=True).stdout.strip().split(',')
    gpu_free = round((int(out[0]) - int(out[1])) / 1024, 2)
except Exception:
    gpu_free = h.get('gpu_free_vram_gb', 6.9)
epoch = int(time.time())
now = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')

h['last_seen'] = now
h['heartbeat_epoch_utc'] = epoch
h['clock_read'] = now
h['current_task'] = ("r350 closed: wave-1a s3 judgment-face FROZEN deb3b1f4 (sec.9.1 P-5C grid+shared-lib lines+seed "
                     "20285000+grammar-ledger row, freeze-before-burn honored) + S6 30/30 + 5x HANDOVER r350; next r351 = "
                     "judge runner build + pool entry MASS-TRIAL-W1-JUDGE shards=4; W2-A finalize harvest window; CEO 48h "
                     "clock 09-29 22:45")
h['cpu_cores'] = 16
h['free_ram_gb'] = round(mem.available / 1e9, 2)
h['gpu_free_vram_gb'] = gpu_free
h['total_ram_gb'] = 23.9
h['cpu_util_pct'] = psutil.cpu_percent(interval=1)
h['round_no'] = 350
h['verdict'] = ("green: wave-1a s3 freeze deb3b1f4 landed pre-burn; W2-A burn 4-worker full-core alive no-kill; RAM "
                "6.72GB crossed SCREEN flip gate (autofill owns flip); smoke 25/25; orders 99/99 double-scan zero diff")
for k, v in [('cores', 16), ('idle_ram_gb', h['free_ram_gb']), ('gpu_free_vram_mb', int(gpu_free * 1024)),
             ('idle_ram_mb', int(h['free_ram_gb'] * 1024)), ('gpu_idle_vram_mb', int(gpu_free * 1024)),
             ('round', 350), ('loop_round', 350), ('cpu_pct', h['cpu_util_pct'])]:
    h[k] = v
h['gpu_idle_vram_gb'] = gpu_free
json.dump(h, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# self-verify: epoch must be JSON int (R170/R178 law)
back = json.load(open(p, encoding='utf-8'))
assert isinstance(back['heartbeat_epoch_utc'], int), 'epoch not int'
assert 'T' in back['clock_read'] and '+' in back['clock_read'], 'clock_read not ISO8601 T-sep'
print('heartbeat ok: epoch=%d(int) clock=%s ram=%.2fGB gpu=%.2fGB' % (
    back['heartbeat_epoch_utc'], back['clock_read'], back['free_ram_gb'], back['gpu_free_vram_gb']))
