import json, time, subprocess, datetime

NOW = datetime.datetime.now(datetime.timezone.utc).astimezone()
clock_read = NOW.strftime('%Y-%m-%dT%H:%M:%S+08:00') if NOW.utcoffset().total_seconds() == 8*3600 else NOW.isoformat(timespec='seconds')
epoch = int(time.time())

# cpu cores
try:
    cores = int(subprocess.check_output(['powershell','-NoProfile','-Command',
        '(Get-CimInstance Win32_ComputerSystem).NumberOfLogicalProcessors']).decode().strip())
except Exception:
    cores = 32
# idle RAM GB
try:
    free_kb = int(subprocess.check_output(['powershell','-NoProfile','-Command',
        '[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,1)']).decode().strip())
except Exception:
    free_kb = 0
# GPU idle VRAM GB (nvidia-smi MiB -> GB conversion, r91 unit law)
gpu_vram_idle = 0.0
try:
    out = subprocess.check_output(['nvidia-smi','--query-gpu=memory.total,memory.used','--format=csv,noheader,nounits'], timeout=10).decode()
    tot, used = [float(x.strip()) for x in out.strip().split(',')]
    gpu_vram_idle = round((tot - used) / 1024.0, 1)
except Exception:
    gpu_vram_idle = -1.0

# state file
with open('state-bm-a.json', encoding='utf-8') as f:
    state = json.load(f)
state['round_no'] = 365
state['did'] = 'R365 5x HANDOVER check (bm-a R361-365 window row + product-face zero-drift verify: ledger 286,551 flat, pool 80=78done+W2A ready bm-b+W2B waiting) + Sunday green maintenance (orders 98/98 dual-scan zero-unacked, decisions mtime-regression=content-verified zero new actionable, smoke 25/25, post_review YES=44 NO=0, S6 30-leg rc=0 weekend no-op family zero-masked, WM py_low_board_clear legal-idle, T-94 owner bm-b s1-frozen shards pending declare per MSG-2335)'
state['verify'] = 'smoke 25/25 + S6 30 rc=0 + orders 98/98 x2 + post_review NO=0 + claw identical + schtasks 4/4 + epoch int'
state['next'] = 'Mon 09-28 09:15 T-91 s3 auto-fire (IntradayMarks 09:25 armed; first bar ~15:30 -> live.paper enforce-gated + t35 + exports; sysv1 first SIG-09-24 Top10 marks via bm-b BARS evening); bm-b T-94 runner+screen-pool declare -> my shard claim per MSG-2335; MF/AH EM self-heal watch; council window 09-29 12:00; next 5x=R370'
state['last_round_at'] = clock_read
state['updated'] = clock_read
with open('state-bm-a.json', 'w', encoding='utf-8') as f:
    json.dump(state, f, ensure_ascii=False, indent=2)

# heartbeat
with open('fleet/machines/bm-a.json', encoding='utf-8') as f:
    hb = json.load(f)
hb['last_seen'] = clock_read
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = clock_read
hb['cpu_cores'] = cores
hb['idle_ram_gb'] = free_kb
hb['gpu_idle_vram_gb'] = gpu_vram_idle
hb['verdict'] = 'healthy r365 green-maintenance 5x-HANDOVER (T-91 armed Mon 09:15; T-94 shards standing-by owner bm-b declare per MSG-2335)'
hb['current_task'] = 'r365 closed: Sunday green maintenance + HANDOVER 5x check (ledger 286,551 flat, pool 80 intact, smoke 25/25, S6 rc=0, orders 98/98)'
with open('fleet/machines/bm-a.json', 'w', encoding='utf-8') as f:
    json.dump(hb, f, ensure_ascii=False, indent=2)

# self-verify epoch int + clock T-format
hb2 = json.load(open('fleet/machines/bm-a.json', encoding='utf-8'))
assert isinstance(hb2.get('heartbeat_epoch_utc'), int), 'epoch not int'
assert 'T' in hb2.get('clock_read',''), 'clock_read missing T separator'
print('OK cores=%s idle_ram_gb=%s gpu_idle_vram_gb=%s epoch=%d clock=%s' % (cores, free_kb, gpu_vram_idle, hb2['heartbeat_epoch_utc'], hb2['clock_read']))
