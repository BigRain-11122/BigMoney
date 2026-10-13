# -*- coding: utf-8 -*-
"""r988 bm-c closeout: state round_no++, heartbeat faces, canonical round report append."""
import json, io, os, sys, time, datetime, subprocess
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now(datetime.timezone.utc).astimezone()
TS = NOW.isoformat(timespec='seconds')
EPOCH = int(time.time())

def load(p):
    return json.load(io.open(p, encoding='utf-8'))
def save(p, d):
    with io.open(p, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(d, f, ensure_ascii=False, indent=1)

# --- machine stats (fresh read) ---
free_ram = None; cpu_pct = None
try:
    import psutil
    vm = psutil.virtual_memory()
    free_ram = round(vm.available / 1024**3, 1)
    cpu_pct = round(psutil.cpu_percent(interval=1), 1)
except Exception:
    pass
vram_free = None
try:
    r = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
                       capture_output=True, text=True, timeout=20)
    vram_free = int(r.stdout.strip().splitlines()[0])
except Exception:
    pass
nproc = os.cpu_count()
print(f"stats: free_ram={free_ram}G cpu={cpu_pct}% vram_free={vram_free}MiB cores={nproc}")

# --- state file ---
sp = os.path.join(ROOT, 'state-bm-c.json')
st = load(sp)
st['round_no'] = int(st.get('round_no', 0)) + 1
st['current_task'] = "r988 W237 seat published=reserved (queue-depth supply; M12 freeze watch waiting-upstream W236 finalize) + wait-faces held (bars pre-15:30 + MF-IC-P1 upstream panel rebuild in flight)"
st['current_task_at'] = TS
st['last_round'] = 'r988'
st['last_round_at'] = TS
st['last_round_ts'] = EPOCH
st['clock_read'] = TS
st['last_seen'] = TS
st['did'] = ("r988: (1) S0-1 anchor bm-c + round-zero probe py_faces=8 orphans=2 zero-kill; S0 pre-round "
             "runtime-state commit (9 own faces) + ephemeral satengine faces treasure_guard rc0 discard "
             "(live writer race) + rebase clean; (2) S0.5 opening+tail dual scans FALSE both (ord content-sha1 "
             "348eaf34 pinned-method HOLD after self-caught sha256 misread = r977 documented method pin held; "
             "dec raw-blob sha256 86187eff hold; unacked=0); MSG-0645-bma processed (MF collector crash = "
             "CPython 3.14.4 DETACHED asyncio stdlib bug, bm-a v3 transport fix landed, bm-c dormant exposure "
             "family fix-on-touch noted); (3) S1 smoke 49/49; (4) S3 satengine ALIVE (alive_flag=true burns=0 "
             "queue=0 py_cpu 0.39%) + wm red=false green (next_pick=claimed MF-IC-P1 upstream) + idle "
             "green_idle=false RAM-gated honest (GPU=MV V3 protected O-20261014-0312 sec.2); (5) PRODUCT: "
             "W237 SEAT PUBLISHED=RESERVED per seat-first law O-20261010-2350 sec.2 (席位不排冻结窗·禁等上一波"
             "烧完才占下一席) + never-dry O-1819 + CPU standing-open O-20261013-2215: pre-seat probe "
             "_w237bmc_20261014_probe.py rc0 ADMIT (leg0 dual-state prior-wave face registry-first/receipt-fallback, "
             "W236 bands machine-read from frozen ADMIT receipt zero-transcription r587; leg1 A 536_204..538_203 "
             "hops=1 staircase NINETY-SEVENTH E36 + B 538_204..538_403 hops=1 own-A reservation W141; leg2 "
             "seed_admit_gate rc0 FREE x2; leg3 origin vacancy four-check green; leg4 W238+ naive projection "
             "98th anticipated) + seat MSG-20261014-0654-bmc-w237-seat + M12 freeze watch row (waiting-upstream "
             "W236 finalize, freeze-prep per W236 bloodline at landing window) -> pushed 9312ef7ac behind-0 "
             "verified dual-file ls-tree; bm-c 65th owned, 227th wave; (6) S6 chain 38/38 rc0 (dualrun streak 51 "
             "zero-drift; audit FLAG pool_starvation/supply_floor structural answered-by-chain W236+this seat; "
             "post_review 0-x; token face read); (7) S7 quad: attrition scan + pin=5 + watchdog + claws.")
save(sp, st)
print('state: round_no ->', st['round_no'])

# --- heartbeat ---
hp = os.path.join(ROOT, 'fleet', 'machines', 'bm-c.json')
h = load(hp)
h['last_seen'] = TS
h['ts'] = TS
h['clock_read'] = TS
h['heartbeat_epoch_utc'] = EPOCH
h['current_task'] = st['current_task']
h['cpu_cores'] = nproc
h['free_ram_gb'] = free_ram
h['idle_ram_gb'] = free_ram
h['gpu_free_vram_mib'] = vram_free
h['gpu_free_vram_mb'] = None if vram_free is None else round(vram_free / 1.048576)
h['cpu_pct'] = cpu_pct
h['idle_rounds'] = 0
h['agenda_starved'] = False
h['verdict'] = 'green (r988: W237 seat published queue-depth supply + engine alive + wait-faces: bars pre-15:30 / MF-IC-P1 upstream / M12 waiting-upstream)'
save(hp, h)
chk = load(hp)
assert isinstance(chk.get('heartbeat_epoch_utc'), int), 'epoch must be int'
print('heartbeat: epoch', chk['heartbeat_epoch_utc'], 'int-verified; orders_ack', len(chk.get('orders_ack', [])))

# --- canonical round report append ---
rp = os.path.join(ROOT, 'logs', 'iteration-loop', 'round_reports-bm-c.md')
lines = io.open(rp, encoding='utf-8', errors='replace').read().splitlines()
row = (f"{TS} | r988 | bm-c: W237 SEAT PUBLISHED=RESERVED (seat-first queue-depth supply per O-20261010-2350 "
       f"sec.2 禁等上一波烧完 + never-dry O-1815/O-1819 + CPU standing-open O-20261013-2215; bm-c 65th owned "
       f"227th wave; A 536_204..538_203 hops=1 staircase NINETY-SEVENTH E36 / B 538_204..538_403 hops=1 own-A "
       f"reservation W141; pre-seat probe _w237bmc_20261014 rc0 ADMIT: leg0 dual-state prior-wave face "
       f"registry-first/receipt-fallback W236 bands zero-transcription + leg2 seed_admit_gate FREE x2 + leg3 "
       f"origin vacancy four-check + leg4 W238+ 98th anticipated; upstream W236 seat 5c25db795+prereg 67ade8314 "
       f"burn pending -- seat does NOT wait; freeze waits-upstream M12 watch row armed state/queue/main.md; "
       f"push 9312ef7ac behind-0 dual-file verified) | WM-VERDICT: green red=false (bars pre-15:30; next_pick="
       f"claimed MF-IC-P1 upstream panel rebuild in flight ETA ~09:2x, S2 gate=bm-a lane) | orphan face=2 "
       f"zero-kill (py_faces=8; MV-lane infra kept) | body: S0 pre-round own-runtime commit + satengine live-face "
       f"treasure_guard rc0 discard (writer race, self-healing) + rebase clean; S0.5 dual FALSE x2 (ord sha1-method "
       f"348eaf34 HOLD -- interim sha256 misread self-caught, r986 method pin held; dec 86187eff hold; unacked=0; "
       f"MSG-0645-bma MF-crash root-cause processed: Py3.14.4 DETACHED asyncio stdlib bug, bm-a v3 fix live, "
       f"dormant family fix-on-touch noted); smoke 49/49; satengine ALIVE (burns 0/queue 0/py 0.39%); jobs=0 + "
       f"fleet 48-claimed none-open; idle green_idle=false RAM-gated honest 4.3% (GPU=MV V3 protected); "
       f"post_review 0-x | S6 chain 38/38 rc0 (dualrun ZERO-DRIFT streak 51; audit FLAG pool_starvation+"
       f"supply_floor structural answered-by-chain W236+this seat; token face read) | S7 quad: attrition scan + "
       f"pin=5 + watchdog + claws | r989: M12 trigger watch (W236 finalize lands -> W237 freeze-prep same-window "
       f"per W236 bloodline) + MF panel watch (09:2x -> MF-IC-P1 unpark on bm-a S2) + 15:30 bars re-probe -> "
       f"papers chain + bm-a heartbeat face stale 8.5h noted (their commits landing, absorb-only)")
with io.open(rp, 'a', encoding='utf-8', newline='\n') as f:
    f.write('\n' + row + '\n')
print('round report appended (canonical path), new line count:', len(lines) + 2)
print('CLOSEOUT DONE')
