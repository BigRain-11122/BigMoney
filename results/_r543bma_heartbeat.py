import json, io, time, datetime, psutil

p = 'fleet/machines/bm-a.json'
d = json.load(io.open(p, encoding='utf-8'))
now_local = datetime.datetime.now(datetime.timezone.utc).astimezone()
vm = psutil.virtual_memory()
d['last_seen'] = now_local.isoformat(timespec='seconds')
d['current_task'] = 'r543 engine-seat observation window (W31=bm-b slot 48h window opened 22:52; W33=bm-a next seat; no queue-jump per leg0 tripwire analysis)'
d['cpu_cores'] = psutil.cpu_count(logical=True)
d['idle_ram_gb'] = round(vm.available / (1024**3), 1)
try:
    import subprocess
    out = subprocess.check_output(
        ['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
        capture_output=True, text=True, timeout=10)
    d['gpu_idle_vram_mb'] = int(out.strip().splitlines()[0])
except Exception:
    d['gpu_idle_vram_mb'] = None
d['verdict'] = 'py_low_board_clear (legal seat-wait: board closed, pool ready=0, engine idle between waves, W31=bm-b rotation window active)'
d['heartbeat_epoch_utc'] = int(time.time())
d['clock_read'] = now_local.isoformat(timespec='seconds')
io.open(p, 'w', encoding='utf-8', newline='').write(
    json.dumps(d, ensure_ascii=False, indent=2))
# self-verify per law: epoch must be JSON int
chk = json.load(io.open(p, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
assert 'T' in chk['clock_read'], 'clock_read must be T-separated'
print('heartbeat ok: epoch', chk['heartbeat_epoch_utc'], 'clock', chk['clock_read'])
