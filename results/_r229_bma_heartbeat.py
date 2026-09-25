# r229 bm-a: heartbeat update (epoch int via int(time.time()), R170/R178 dual-offender law)
import json, io, time, psutil, platform

d = json.load(io.open('fleet/machines/bm-a.json', encoding='utf-8-sig'))
vm = psutil.virtual_memory()
epoch = int(time.time())
clock = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')

d['machine_id'] = 'bm-a'
d['last_seen'] = clock
d['clock_read'] = clock
d['heartbeat_epoch_utc'] = epoch
d['round_no'] = 229
d['current_task'] = 'r229 done: s2 pull supervised healthy (3782/5228 @07:21, ETA ~08:26); acceptance RUN at pull-completion round'
d['task'] = 'T-72 s2 first-pull in flight (3782/5228 @07:21, 22.2/min, ETA ~08:26); acceptance RUN (sina_mf_accept.py run) at completion round, then s3 S6 wiring'
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
    d['gpu_total_vram_mb'] = int(mi.total / 1e6)
    d['gpu'] = {'present': True, 'idle_vram_free_gb': round(free_mb / 1e3, 1), 'note': 'sampled r229'}
    pynvml.nvmlShutdown()
except Exception as e:
    d['gpu'] = {'present': True, 'idle_vram_free_gb': None, 'note': f'VRAM sample skipped: {type(e).__name__}'}

with io.open('fleet/machines/bm-a.json', 'w', encoding='utf-8-sig', newline='') as f:
    json.dump(d, f, ensure_ascii=False, indent=1)
    f.write("\n")

# self-verify per prompt law
v = json.load(io.open('fleet/machines/bm-a.json', encoding='utf-8-sig'))
assert isinstance(v['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
print('heartbeat ok: epoch', v['heartbeat_epoch_utc'], 'is-int', isinstance(v['heartbeat_epoch_utc'], int), 'clock', v['clock_read'], 'cpu%', v['cpu_pct'], 'ram_gb', v['free_ram_gb'])
