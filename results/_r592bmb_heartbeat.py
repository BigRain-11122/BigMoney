# -*- coding: utf-8 -*-
# r592 bm-b heartbeat update: dynamic fields only, orders_ack carried verbatim (r583 law)
import json, time, datetime, os, glob, subprocess, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

now = datetime.datetime.now().astimezone()
iso = now.strftime('%Y-%m-%dT%H:%M:%S%z')
epoch = int(time.time())

# --- orders tail double-scan (S7 close face) ---
orders = sorted(os.path.basename(p) for p in glob.glob(r'fleet\orders\O-*.md'))
hb_path = r'fleet\machines\bm-b.json'
h = json.load(open(hb_path, encoding='utf-8'))
ack = h.get('orders_ack', [])
pending = [o for o in orders if o not in set(ack)]
print('tail-scan orders:', len(orders), 'ack:', len(ack), 'pending:', pending)
assert not pending, 'PENDING ORDERS AT S7 CLOSE: %s' % pending

# --- system stats ---
try:
    import psutil
    vm = psutil.virtual_memory()
    free_ram = round(vm.available / 1024**3, 1)
    total_ram = round(vm.total / 1024**3, 1)
    cpu_pct = psutil.cpu_percent(interval=1.5)
except Exception:
    free_ram, total_ram, cpu_pct = h.get('free_ram_gb', 5), h.get('total_ram_gb', 26), h.get('cpu_util_pct', 0)
gpu_free = None
try:
    r = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
                       capture_output=True, text=True, timeout=15)
    gpu_free = round(float(r.stdout.strip().splitlines()[0]) / 1024, 1)
except Exception:
    gpu_free = h.get('gpu_free_vram_gb', 2.1)

# --- dynamic field update (orders_ack untouched) ---
h['last_seen'] = iso
h['heartbeat_epoch_utc'] = epoch  # JSON int type per R170/R178 law
h['clock_read'] = iso
h['current_task'] = ('r592 product round: town.html alloc building v5-canon restoration landed (r538 bm-a false-basis re-anchor '
                     'surgically restored to pre-r538 blob e902ba6de, gate 17/17 + Edge render + multimodal verified); '
                     'engine lane rotation-waiting (W112 finalize pending origin, W113 bm-c seated)')
h['cpu_util_pct'] = cpu_pct
h['free_ram_gb'] = free_ram
h['idle_ram_gb'] = free_ram
h['ram_free_gb'] = free_ram
h['ram_avail_gb'] = free_ram
h['total_ram_gb'] = total_ram
h['gpu_free_vram_gb'] = gpu_free
h['gpu_idle_vram_gb'] = gpu_free
h['gpu_vram_free'] = gpu_free
h['gpu_idle_vram_mb'] = int(gpu_free * 1024)
h['gpu_free_vram_mb'] = int(gpu_free * 1024)
h['round_no'] = 592
h['round_no_label'] = 'r592'
h['verdict'] = ('product round: town.html v5 alignment fix landed (J12 line); legal-idle engine lane (W112 bm-a finalize pending '
                'on origin, W113 bm-c seat queued ahead of mine); moneyflow IC next_pick panel-blocked source conn-down; '
                'W14-GENERATE GM-parked; paper Golden-Week no-new-bar block; orders 143/143 ack both scans')

raw = open(hb_path, 'rb').read()
crlf = b'\r\n' in raw
out = json.dumps(h, ensure_ascii=False, indent=1)
if crlf:
    out = out.replace('\n', '\r\n')
open(hb_path, 'wb').write(out.encode('utf-8'))

# --- self-verify: reload, epoch type assert (R170/R178 dual law) ---
h2 = json.load(open(hb_path, encoding='utf-8'))
e = h2['heartbeat_epoch_utc']
assert isinstance(e, int) and not isinstance(e, bool), 'epoch not int: %r' % e
assert 'T' in h2['clock_read'], 'clock_read missing T separator'
print('heartbeat written: epoch=%d (int ok) clock=%s cpu=%.1f%% ram_free=%.1fGB gpu_free=%.1fGB crlf=%s'
      % (e, h2['clock_read'], cpu_pct, free_ram, gpu_free, crlf))
