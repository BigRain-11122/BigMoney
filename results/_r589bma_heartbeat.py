# -*- coding: utf-8 -*-
"""r589 bm-a heartbeat update (r583 law: load existing, update dynamic fields
only, orders_ack list carried verbatim; epoch MUST be JSON int)."""
import json, time, datetime, psutil, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
P = 'fleet/machines/bm-a.json'
h = json.load(open(P, encoding='utf-8'))
ack = h.get('orders_ack', [])          # carried verbatim (r583 law)
h['last_seen'] = datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat(timespec='seconds')
h['heartbeat_epoch_utc'] = int(time.time())
h['clock_read'] = datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat(timespec='seconds')
h['current_task'] = 'r589: W110 five-face freeze+ignition (100th engine wave) + W107 finalize one-pass (chain head 599,948, K=233,320) + D-19 phantom-key re-anchor'
h['verdict'] = 'green'
cpu = psutil.cpu_percent(interval=1)
vm = psutil.virtual_memory()
h['cpu_cores'] = psutil.cpu_count()
h['idle_ram_gb'] = round(vm.available / 1e9, 1)
g = None
try:
    import subprocess
    o = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
                      capture_output=True)
    if o.returncode == 0:
        g = round(int(o.stdout.decode().splitlines()[0]) / 1024, 1)
except Exception:
    pass
if g is not None:
    h['gpu_idle_vram_gb'] = g
h['orders_ack'] = ack                  # same list back (no rebuild)
json.dump(h, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
h2 = json.load(open(P, encoding='utf-8'))
assert isinstance(h2['heartbeat_epoch_utc'], int), 'epoch must be int (F7)'
assert 'T' in h2['clock_read'], 'clock_read must be ISO T-format (F7)'
assert len(h2['orders_ack']) == len(ack) == 143, 'orders_ack carried verbatim'
print('heartbeat ok: epoch=%d (int) clock=%s ack=%d' % (h2['heartbeat_epoch_utc'], h2['clock_read'], len(h2['orders_ack'])))
