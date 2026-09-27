import json, time, datetime, subprocess

p = 'fleet/machines/bm-c.json'
h = json.load(open(p, encoding='utf-8'))
now = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
epoch = int(time.time())

import psutil
cpu = psutil.cpu_percent(interval=1)
ram = psutil.virtual_memory()
free_ram = round(ram.available / 1024**3, 1)

try:
    out = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
                         capture_output=True, text=True, timeout=10).stdout.strip().splitlines()
    vram = int(float(out[0]))
except Exception:
    vram = h.get('gpu_free_vram_mb', -1)

h['last_seen'] = now
h['heartbeat_epoch_utc'] = epoch
h['clock_read'] = now
h['current_task'] = 'r131 green-maintenance watch (T-95 owner-watch: W2B burning bmb, V2-P1 defer post-W2B)'
h['cpu_util_pct'] = cpu
h['cpu_pct'] = cpu
h['free_ram_gb'] = free_ram
h['idle_ram_gb'] = free_ram
h['gpu_free_vram_mb'] = vram
h['round_no'] = 131
h['updated_at'] = now
h['verdict'] = ('green maintenance; pool 88 (81 done + W2B census bm-b burning prio1 + 6 waiting = V2-P1 defer '
                'post-W2B + judge family bm-b RAM/deep-panel-gated) zero bm-c-claimable; T-95 fuse auto-clear '
                'armed at next pick; fund_premium first snapshot 15:30 today bmc lane; trial-labor funnel full')
json.dump(h, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

r = json.load(open(p, encoding='utf-8'))
assert isinstance(r['heartbeat_epoch_utc'], int), 'EPOCH NOT INT'
assert r['round_no'] == 131
assert 'T' in r['clock_read'] and ' ' not in r['clock_read'], 'CLOCK NOT T-SEP'
print('HEARTBEAT_OK epoch=%d round=131 cpu=%.1f free_ram=%.1fGB vram=%dMB ts=%s'
      % (r['heartbeat_epoch_utc'], cpu, free_ram, vram, now))
