import json, time, datetime, psutil, io

now = datetime.datetime.now().astimezone()
hb_path = 'fleet/machines/bm-b.json'
hb = json.load(open(hb_path, encoding='utf-8'))

epoch = int(time.time())
vm = psutil.virtual_memory()
gputil_ok = True
try:
    import subprocess
    out = subprocess.run(['nvidia-smi', '--query-gpu=memory.free',
                          '--format=csv,noheader,nounits'],
                         capture_output=True, text=True, timeout=10).stdout.strip()
    gpu_free_vram_mb = int(out.splitlines()[0]) if out else None
except Exception:
    gputil_ok = False
    gpu_free_vram_mb = None

hb['last_seen'] = now.strftime('%Y-%m-%d %H:%M:%S')
hb['current_task'] = ('r519 complete: W22 ELEVENTH engine wave frozen (A 86_001..88_000/B 39_100..39_299 '
                      'ADMIT, origin ff1f9c1a8) + ignited (5/12 shards burning) + P0 W20 finalize product '
                      'restore (bm-a r533 closeout stomp, 4th instance, healed d855bc650)')
hb['cpu_cores'] = psutil.cpu_count(logical=True)
hb['free_ram_gb'] = round(vm.available / 1024**3, 2)
if gpu_free_vram_mb is not None:
    hb['gpu_free_vram_mb'] = gpu_free_vram_mb
hb['verdict'] = ('r519 complete end-to-end: W22 freeze+ignite main product (burn in flight 5/12); '
                 'P0 W20 product restore (closeout sweep 4th instance, zero science pollution); '
                 'S6 37 legs rc0; smoke 47/47; orders double-scan EMPTY; D-19 MATCH')
hb['heartbeat_epoch_utc'] = epoch
assert isinstance(hb['heartbeat_epoch_utc'], int)
hb['clock_read'] = now.strftime('%Y-%m-%dT%H:%M:%S+08:00')

with io.open(hb_path, 'w', encoding='utf-8', newline='') as f:
    json.dump(hb, f, ensure_ascii=False, indent=2)

chk = json.load(open(hb_path, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
assert 'T' in chk['clock_read'], 'clock_read must be ISO with T separator'
print('heartbeat written: epoch=', chk['heartbeat_epoch_utc'], 'clock=', chk['clock_read'])
print('free_ram_gb=', chk['free_ram_gb'], 'gpu_free_vram_mb=', chk.get('gpu_free_vram_mb'))
