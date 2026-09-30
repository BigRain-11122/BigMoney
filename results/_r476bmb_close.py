import json, time, os, io, ctypes, subprocess, datetime, glob

os.chdir(os.path.dirname(os.path.abspath(__file__)) + '\\..')

now = datetime.datetime.now()
ts = now.strftime('%Y-%m-%dT%H:%M:%S') + now.strftime('%z')[:3] + ':' + now.strftime('%z')[3:]
epoch = int(time.time())

# --- inbox: process messages addressed to bm-b / ALL (leave own MSG-1945 for others) ---
for name in ('MSG-20260930-2012-bmc-bmb-aps-freshentry-semantics.md',
             'MSG-20260930-1947-bmc-ALL-cross-start-robustness-berth.md'):
    src = os.path.join('fleet', 'inbox', name)
    dst = os.path.join('fleet', 'inbox', 'processed', name)
    if os.path.exists(src):
        os.replace(src, dst)
        print('processed:', name)

# --- machine stats ---
class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [('dwLength', ctypes.c_ulong), ('dwMemoryLoad', ctypes.c_ulong),
                ('ullTotalPhys', ctypes.c_ulonglong), ('ullAvailPhys', ctypes.c_ulonglong)]
stat = MEMORYSTATUSEX()
stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
free_ram_gb = round(stat.ullAvailPhys / 1024**3, 1)
total_ram_gb = round(stat.ullTotalPhys / 1024**3, 1)
gpu_free = 0.0
try:
    out = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
                         capture_output=True, text=True, timeout=10).stdout.strip().splitlines()[0]
    gpu_free = round(int(out) / 1024, 1)
except Exception:
    pass
try:
    load1 = subprocess.run(['powershell', '-NoProfile', '-Command',
                            '(Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average'],
                           capture_output=True, text=True, timeout=15).stdout.strip()
    cpu_util = int(load1)
except Exception:
    cpu_util = 0

# --- state.json: round 475 -> 476 ---
sp = 'state.json'
st = json.load(open(sp, encoding='utf-8'))
st['round_no'] = 476
st['note'] = ("r476: crash-window closeout (dead 19:42 firing adopted: EXCLUSION-MARGINAL-P1 runner engine leg +791L "
              "selftest 16/16 re-verified) + seed collision resolved (exclusion_marginal_rand 20329000->20329500, "
              "bm-c cross_start_robustness_p1 same-window fait accompli, ours unburned yields) + F-04 MSG-1945 "
              "O-1858 sec.2b vs W14 PARKED -> GM adjudication request + pool EXCLUSION-MARGINAL-P1-RUN priority 0 "
              "ready claim-cleared for autofill (ignition_sla flag till watchdog tick ignites) + O-1858/O-1901 acked "
              "129/129 + S6 38 legs rc0 (dualrun ZERO-DRIFT 141; WM py_low_board_clear; CALL-2026-09-30 ORANGE_COOL; "
              "bars 09-29 pre-holiday source-lag no-op per r485; stale-takeover derives legal bm-a hb 77-78min; "
              "attrition CLEAN) + smoke 47/47; NEXT: burn lands via autofill -> harvest round flips done + prereg "
              "s7/s8 backfill + carrier marginal table + TRACK #3 row; W14 awaits GM ruling on MSG-1945; 10-01 "
              "month-first trio + REGIME_GUARD v3 date gate hands-off + O-1858 holiday full-core from 10-01")
for k in ('last_round_at', 'last_round_ts', 'ts', 'updated', 'updated_at'):
    st[k] = ts
json.dump(st, open(sp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('state.json -> round 476')

# --- heartbeat fleet/machines/bm-b.json ---
hp = os.path.join('fleet', 'machines', 'bm-b.json')
hb = json.load(open(hp, encoding='utf-8'))
hb['last_seen'] = ts
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = ts
hb['round_no'] = 476
hb['round'] = 476
hb['loop_round'] = 476
hb['last_round_at'] = ts
ack = hb.get('orders_ack', [])
new_order = 'O-20260930-1858-bm-a.md'
if new_order not in ack:
    ack.append(new_order)
hb['orders_ack'] = ack
hb['n_orders_ack'] = len(ack)
on_disk = len(glob.glob(os.path.join('fleet', 'orders', 'O-*.md')))
hb['current_task'] = ('r476 crash-window closeout: EXCLUSION-MARGINAL-P1 burn queued (autofill ignition next watchdog '
                      'tick), W14 held pending GM adjudication (MSG-1945)')
hb['cpu_cores'] = 16
hb['cores'] = 16
hb['cpu_util_pct'] = cpu_util
hb['free_ram_gb'] = free_ram_gb
hb['idle_ram_gb'] = free_ram_gb
hb['ram_free_gb'] = free_ram_gb
hb['total_ram_gb'] = total_ram_gb
hb['gpu_free_vram_gb'] = gpu_free
hb['gpu_idle_vram_gb'] = gpu_free
hb['gpu_free_vram_mb'] = int(gpu_free * 1024)
hb['verdict'] = ('r476 crash-window closeout OK: dead firing adopted + seed collision resolved + burn re-armed; '
                 'orders %d/%d acked' % (len(ack), on_disk))
json.dump(hb, open(hp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
print('heartbeat: round 476, orders_ack %d/%d, epoch int OK, free_ram %.1fGB gpu_free %.1fGB' %
      (len(ack), on_disk, free_ram_gb, gpu_free))

# --- round report append (bm-b file per fleet README s6) ---
rp = os.path.join('logs', 'iteration-loop', 'round_reports.md')
line = ('%s | r476 | bm-b crash-window closeout: dead 19:42 firing adopted (runner engine leg +791L selftest 16/16 '
        're-verified) + seed collision exclusion_marginal_rand 20329000->20329500 (bm-c cross_start fait accompli, '
        'unburned yields) + MSG-1945 O-1858/sec.2b-vs-W14-PARKED GM adjudication request + pool burn priority 0 '
        'claim-cleared + O-1858 acked (holiday full-core from 10-01, W14 face held) | evidence: commit 25b13a8a5 '
        'pushed e6f06a3e5..25b13a8a5; smoke 47/47; S6 38 legs rc0 (dualrun ZERO-DRIFT 141, WM py_low_board_clear, '
        'CALL ORANGE_COOL, bars 09-29 source-lag no-op r485, attrition CLEAN); audit flags ignition_sla+supply_floor '
        'honest | next: autofill ignites EXCLUSION burn -> harvest flip + prereg s7/s8 + carrier table; W14 GM '
        'ruling; 10-01 month-first trio\n' % ts)
with io.open(rp, 'a', encoding='utf-8', newline='\n') as f:
    f.write(line)
print('round report appended')
