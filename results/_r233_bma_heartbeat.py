# r233 bm-a heartbeat fix: restore producer format (psutil/pynvml, BOM+indent=1, R229 recipe)
# (first write used custom ctypes probe -> wrong ram/cpu readings + format drift; format-fidelity law R209)
import json, io, time, psutil

d = json.load(io.open('fleet/machines/bm-a.json', encoding='utf-8-sig'))
vm = psutil.virtual_memory()
epoch = int(time.time())
clock = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')

d['machine_id'] = 'bm-a'
d['last_seen'] = clock
d['clock_read'] = clock
d['heartbeat_epoch_utc'] = epoch
d['round_no'] = 233
d['current_task'] = 'r233 done: T-72 s2 pull supervised healthy (4654/5228 @08:00, QC 6/6, ETA ~08:24); acceptance RUN at pull-completion round (~R236-238)'
d['task'] = 'T-72 s2 first-pull in flight (4654/5228 @08:00:03, ~24/min, ETA ~08:24); acceptance RUN (sina_mf_accept.py run) at completion round, then s3 S6 wiring'
d['cpu_cores'] = psutil.cpu_count(logical=True)
d['cpu_pct'] = psutil.cpu_percent(interval=0.5)
d['free_ram_gb'] = round(vm.available / 1e9, 1)
d['idle_ram_gb'] = round(vm.available / 1e9, 1)
d['free_ram_mb'] = int(vm.available / 1e6)
d['cores'] = psutil.cpu_count(logical=True)
d['verdict'] = 'GREEN'
try:
    import pynvml
    pynvml.nvmlInit()
    h = pynvml.nvmlDeviceGetHandleByIndex(0)
    mi = pynvml.nvmlDeviceGetMemoryInfo(h)
    free_mb = int(mi.free / 1e6)
    d['gpu_free_vram_mb'] = free_mb
    d['gpu_idle_vram_mb'] = free_mb
    d['gpu_idle_vram_gb'] = round(free_mb / 1e3, 1)
    d['gpu_free_vram_gb'] = round(free_mb / 1e9, 2)
    d['gpu_total_vram_mb'] = int(mi.total / 1e6)
    d['gpu'] = {'present': True, 'idle_vram_free_gb': round(free_mb / 1e3, 1), 'note': 'sampled r233'}
    pynvml.nvmlShutdown()
except Exception as e:
    d['gpu'] = {'present': True, 'idle_vram_free_gb': None, 'note': f'VRAM sample skipped: {type(e).__name__}'}

with io.open('fleet/machines/bm-a.json', 'w', encoding='utf-8-sig', newline='') as f:
    json.dump(d, f, ensure_ascii=False, indent=1)
    f.write("\n")

v = json.load(io.open('fleet/machines/bm-a.json', encoding='utf-8-sig'))
assert isinstance(v['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
print('heartbeat ok: epoch', v['heartbeat_epoch_utc'], 'is-int', isinstance(v['heartbeat_epoch_utc'], int),
      'clock', v['clock_read'], 'cpu%', v['cpu_pct'], 'ram_gb', v['free_ram_gb'], 'gpu_idle_gb', v['gpu_idle_vram_gb'])
