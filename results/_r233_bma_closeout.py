# r233 bm-a closeout: state round_no flip + heartbeat update (epoch int, per R170/R178 law)
import json, io, os, time, sys, subprocess
sys.stdout.reconfigure(encoding='utf-8')

# --- state flip (no BOM, LF, compact single-line per current producer format) ---
sp = 'state-bm-a.json'
raw = open(sp, 'rb').read()
d = json.loads(raw.decode('utf-8'))
d['round_no'] = 233
d['did'] = ("R233: T-72 s2 pull supervision R6 (4654/5228 @08:00:03 attempts=0 zero failures, PID 29132 alive, "
            "rate ~24/min ETA ~08:24 acceptance ~R236-238; spot QC 6/6 freshest-tail schema-identical 100rows "
            "tail=09-24 four-tier self-consistency dev<=6.6e-10; ticket progress_r233 text-level minimal diff) + "
            "S6 weekend chain green (audit CLEAN, probe py_low_board_clear legal idle, daily cutoff 09-24 legal no-op, "
            "regime ORANGE d2 shadow, MF rank/AH known EM-throttle family, blf 5222 all_pass, paper family gated "
            "off no-new-bar, export idempotent traders=6, scorecard/dashboard refreshed, token delta=0) + "
            "orders 74/74 double-scan zero-missing; decisions no new lines")
with io.open(sp, 'w', encoding='utf-8', newline='') as f:
    f.write(json.dumps(d, ensure_ascii=False, separators=(',', ':')))
print('state ->', d['round_no'])

# --- heartbeat (bm-a only writes its own file) ---
hp = 'fleet/machines/bm-a.json'
h = json.load(open(hp, encoding='utf-8'))
def ram_gb():
    import ctypes
    class M(ctypes.Structure):
        _fields_ = [('dwLength', ctypes.c_ulong), ('dwMemoryLoad', ctypes.c_ulong),
                    ('ullTotalPhys', ctypes.c_uint64), ('ullAvailPhys', ctypes.c_uint64)]
    m = M(); m.dwLength = ctypes.sizeof(M)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return round(m.ullAvailPhys / 1e9, 2), m.dwMemoryLoad
free_ram, memload = ram_gb()
try:
    cpu = float(subprocess.run(['wmic', 'cpu', 'get', 'loadpercentage'], capture_output=True, text=True, timeout=10).stdout.strip().split()[-1])
except Exception:
    cpu = 0.0
try:
    gpu_out = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'], capture_output=True, text=True, timeout=10).stdout.strip().splitlines()[0]
    gpu_free = round(float(gpu_out) / 1024, 2)
except Exception:
    gpu_free = h.get('gpu_free_vram_gb', 0.0)
now = time.time()
h['machine_id'] = 'bm-a'
h['last_seen'] = '2026-09-26T08:0x'
h['current_task'] = 'T-72 s2 first-pull supervision (4654/5228, acceptance ~R236-238)'
h['cpu_cores'] = 32
h['cpu_pct'] = cpu
h['free_ram_gb'] = free_ram
h['gpu_free_vram_gb'] = gpu_free
h['verdict'] = 'GREEN'
h['heartbeat_epoch_utc'] = int(now)
h['clock_read'] = time.strftime('%Y-%m-%dT%H:%M:%S+08:00', time.localtime(now))
h['round_no'] = 233
# orders_ack unchanged (74/74 double-scanned, zero missing)
with io.open(hp, 'w', encoding='utf-8', newline='') as f:
    f.write(json.dumps(h, ensure_ascii=False, separators=(',', ':')))
# self-verify: epoch must be JSON int (R170/R178)
h2 = json.loads(io.open(hp, encoding='utf-8').read())
assert isinstance(h2['heartbeat_epoch_utc'], int), 'epoch must be int'
print('heartbeat written: epoch int =', h2['heartbeat_epoch_utc'], '| clock =', h2['clock_read'], '| ram', free_ram, 'GB | cpu', cpu, '| gpu_free', gpu_free)
