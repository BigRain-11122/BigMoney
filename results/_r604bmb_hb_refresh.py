import json, subprocess, datetime
import psutil

m = psutil.virtual_memory()
free_gb = round(m.available / 1e9, 2)
total_gb = round(m.total / 1e9, 1)
g = None
try:
    o = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
                       capture_output=True, text=True, timeout=10)
    g = int(o.stdout.strip().splitlines()[0])
except Exception:
    g = None

d = json.load(open('fleet/machines/bm-b.json', encoding='utf-8'))
d['cpu_cores'] = 32
d['idle_ram_gb'] = free_gb
d['ram_gb'] = total_gb
if g is not None:
    d['gpu_idle_vram_mb'] = g
# keep heartbeat ts fields fresh alongside resource refresh
ts = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
d['last_seen'] = ts
d['clock_read'] = ts
open('fleet/machines/bm-b.json', 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1))
v = json.load(open('fleet/machines/bm-b.json', encoding='utf-8'))
print('idle_ram_gb:', free_gb, 'total:', total_gb, 'gpu_free_mb:', g)
print('epoch type:', type(v['heartbeat_epoch_utc']).__name__, v['heartbeat_epoch_utc'])
from datetime import datetime as _dt
_dt.fromisoformat(v['clock_read'])
print('clock iso ok:', v['clock_read'])
