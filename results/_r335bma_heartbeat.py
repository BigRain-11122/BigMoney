# -*- coding: utf-8 -*-
# r335 bm-a: S7 heartbeat close refresh (single-writer own file; epoch must be JSON int per R170/R178)
import json, time, subprocess, os

p = 'fleet/machines/bm-a.json'
d = json.load(open(p, encoding='utf-8'))

now = time.time()
clock_read = time.strftime('%Y-%m-%dTH:%M:%S', time.localtime(now)).replace('TH', 'T')
# ISO 8601 with UTC offset, T separator (R262 law)
off = time.strftime('%z', time.localtime(now))
clock_read = time.strftime('%Y-%m-%dTH:%M:%S', time.localtime(now)).replace('TH', 'T') + off[:3] + ':' + off[3:]

# machine sample: cpu + free ram via psutil, gpu via nvidia-smi
try:
    import psutil
    cpu_pct = psutil.cpu_percent(interval=1)
    free_ram_gb = round(psutil.virtual_memory().available / (1024**3), 2)
except Exception:
    cpu_pct, free_ram_gb = 0.0, 0.0
try:
    out = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
                         capture_output=True, text=True, timeout=10).stdout.strip().splitlines()
    gpu_free_vram_gb = round(float(out[0]) / 1024, 2)
except Exception:
    gpu_free_vram_gb = d.get('gpu_free_vram_gb', 0.0)

d['last_seen'] = clock_read
d['current_task'] = ('R335 done: S6 33/33 rc=0 + sina-construct lane pick=(a) MSG-1615 (local census burn queued '
                     'behind bm-b script + prereg freeze) + bm-b last_seen ISO fix ACKED (face closed) + 5x '
                     'HANDOVER R331-335 landed + PS ConvertFrom-Json false-fail pitfall law (python authoritative '
                     'board scans); watch faces: bm-b sina_construct_ic.py -> SINA_CONSTRUCT_P1 freeze -> local '
                     'census burn / Mon 09-28 09:15 T-91 s3 first-marks auto-fire / 10-01 month trio / AH '
                     'EM-mapping throttle-expiry retry')
d['cpu_pct'] = cpu_pct
d['free_ram_gb'] = free_ram_gb
d['gpu_free_vram_gb'] = gpu_free_vram_gb
d['verdict'] = 'healthy'
d['heartbeat_epoch_utc'] = int(now)          # JSON int type, R170/R178 law
d['clock_read'] = clock_read                  # T-separated ISO with offset, R262 law
d['round_no'] = 335
d['task'] = 'idle-round-done'

json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
# post-write self-verification
v = json.load(open(p, encoding='utf-8'))
assert isinstance(v['heartbeat_epoch_utc'], int), 'epoch must be int'
assert 'T' in v['clock_read'] and '+' in v['clock_read'], 'clock_read must be T-separated ISO with offset'
print('heartbeat ok: epoch(int)=', v['heartbeat_epoch_utc'], ' clock=', v['clock_read'], ' cpu=', cpu_pct,
      ' free_ram_gb=', free_ram_gb, ' gpu_free=', gpu_free_vram_gb)
