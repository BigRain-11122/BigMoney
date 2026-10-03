import json, os, time, datetime, shutil

# --- heartbeat: fleet/machines/bm-b.json (bm-b writes ONLY its own file) ---
p = 'fleet/machines/bm-b.json'
h = json.load(open(p, encoding='utf-8'))
now = datetime.datetime.now().astimezone()
now_iso = now.isoformat(timespec='seconds')
epoch = int(time.time())

import psutil
cpu_pct = psutil.cpu_percent(interval=2)
vm = psutil.virtual_memory()
avail_gb = round(vm.available / 1024**3, 2)
total_gb = round(vm.total / 1024**3, 2)
gpu_free = None
try:
    import subprocess
    r = subprocess.run(['nvidia-smi', '--query-gpu=memory.free',
                        '--format=csv,noheader,nounits'],
                       capture_output=True, text=True, timeout=10)
    gpu_free = round(float(r.stdout.strip().splitlines()[0]) / 1024, 2)
except Exception:
    gpu_free = h.get('gpu_idle_vram_gb')

h['last_seen'] = now_iso
h['heartbeat_epoch_utc'] = epoch
h['clock_read'] = now_iso
h['round_no'] = 613
h['round_no_label'] = 'round 613 (bm-b)'
h['current_task'] = ('T-155 FUND-DIVLOWVOL-P1 runner BUILT+IGNITED (4 pool entries ready, autofill domain); '
                     'dual NULLS burns alive (VALUE ~130/2000 ETA 10-06, QUALITY ~48/2000 ETA 10-08); '
                     're-burn chain pid 8016 (PE-X2 in fire)')
h['verdict'] = ('round 613 done: WM=GREEN loaded (py 65-97% three burns legal); smoke 47/47; S6 34/34 rc0; '
                'attrition CLEAN; claws 2/2 + loop pin=2 no-op + watchdog alive (idempotent re-register '
                'after my ArgString call-signature slip, zero harm); orders 150/150 double-scan zero-new; '
                'D-19 hash identical (case-normalized, temp partial clone recipe); '
                'DELIVERABLE: scripts/fund_divlowvol_p1.py runner (selftest 31/31, probe 16/16 PASS, '
                't0=2006-02-06 reproduced) + 4 pool entries (cells x1/x2 + NULLS 2000 + SENS 500)')
h['ts'] = now_iso
h['updated'] = now_iso
h['updated_at'] = now_iso
h['cpu_util_pct'] = cpu_pct
h['free_ram_gb'] = avail_gb
h['idle_ram_gb'] = avail_gb
h['ram_avail_gb'] = avail_gb
h['ram_free_gb'] = round((vm.free / 1024**3), 2)
h['total_ram_gb'] = total_gb
if gpu_free is not None:
    h['gpu_idle_vram_gb'] = gpu_free
    h['gpu_idle_vram_mb'] = int(gpu_free * 1024)
    h['gpu_free_vram_gb'] = gpu_free
    h['gpu_free_vram_mb'] = int(gpu_free * 1024)
    h['gpu_vram_free'] = gpu_free

with open(p, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(h, f, ensure_ascii=False, indent=1)

# self-verify: epoch must be JSON int, clock_read T-separated
chk = json.load(open(p, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int (R170/R178 law)'
assert 'T' in chk['clock_read'][:11], 'clock_read must be T-separated (R262 law)'
print('heartbeat OK: epoch=%d (int) clock=%s cpu=%.1f%% ram_avail=%.2fGB gpu_free=%s'
      % (chk['heartbeat_epoch_utc'], chk['clock_read'], cpu_pct, avail_gb, gpu_free))

# --- inbox: messages addressed to bm-b or ALL, unprocessed ---
inbox = 'fleet/inbox'
proc = 'fleet/inbox/processed'
unhandled = []
if os.path.isdir(inbox):
    for fn in sorted(os.listdir(inbox)):
        if not fn.endswith('.json') and not fn.endswith('.md'):
            continue
        fp = os.path.join(inbox, fn)
        try:
            body = open(fp, encoding='utf-8', errors='replace').read()[:800]
        except Exception:
            body = ''
        low = body.lower()
        if ('bm-b' in body or 'all' in low.split('"to"')[-1][:60]) and fn not in (
                'processed', 'README.md'):
            unhandled.append((fn, body[:160]))
print('inbox unhandled for bm-b/ALL:', len(unhandled))
for fn, preview in unhandled:
    print('  MSG:', fn, '|', preview.replace('\n', ' ')[:140])
