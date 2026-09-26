# r300 bm-b: state.json round bump + heartbeat bm-b.json refresh (epoch int law, T-separated clock)
import io, json, time, datetime as dt

ROOT = r'C:\Users\Administrator\Desktop\Bigmoney'
STATE = ROOT + r'\logs\iteration-loop\state.json'
HB = ROOT + r'\fleet\machines\bm-b.json'

now_iso = dt.datetime.now().astimezone().isoformat(timespec='seconds')   # T-separated, +08:00
epoch = int(time.time())

# --- resource sample (psutil if present, else conservative fallback) ---
cpu_pct = None
free_ram_gb = None
gpu_free_gb = None
try:
    import psutil
    cpu_pct = round(psutil.cpu_percent(interval=1.0), 1)
    vm = psutil.virtual_memory()
    free_ram_gb = round(vm.available / (1024 ** 3), 1)
except Exception:
    pass
if cpu_pct is None:
    import subprocess
    out = subprocess.run(
        ['powershell', '-NoProfile', '-Command',
         "(Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average"],
        capture_output=True, text=True).stdout.strip()
    cpu_pct = float(out) if out else 0.0
    out2 = subprocess.run(
        ['powershell', '-NoProfile', '-Command',
         "[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,1)"],
        capture_output=True, text=True).stdout.strip()
    free_ram_gb = float(out2) if out2 else 0.0
# GPU free VRAM: keep last known value (nvidia-smi query below, fallback to previous)
try:
    import subprocess as sp
    o = sp.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
               capture_output=True, text=True).stdout.strip().splitlines()
    gpu_free_gb = round(float(o[0]) / 1024, 1) if o else None
except Exception:
    gpu_free_gb = None

# --- state.json ---
with io.open(STATE, encoding='utf-8-sig') as f:
    st = json.load(f)
assert st.get('round_no') == 299, 'round_no anchor drift: ' + str(st.get('round_no'))
st['round_no'] = 300
st['did'] = ('r300 维护轮+5x 核对：S0 stash-pop 干净；S0.5 orders 91/91 双扫零未ack；'
             'S1 smoke 25/25；S3 T-87 probe#13 on_track 83.2%(4350/5228)@12.62/min '
             'ETA 06:41:34·零形状缺陷(冻结血统律 delta=8 全轮号面)；S6 30/30 rc=0'
             '(audit pool_starvation 31.8min=供给在途态合法·regime ORANGE shadow·'
             'paper 族 no-op)；5x=统一链 198,389→200,396 实读(+2,007=bm-a CN_KLINE '
             '判负批·bm-b 零批)+HANDOVER L4 级联 5 深+文末增量窗行+post_review 尾零'
             '开口 NO；S7 双任务存活+inbox 零未读+state/heartbeat 300 epoch int 自证')
st['verdict'] = 'green'
st['next'] = ('T-87 完成态复探(ETA 06:41 后 gate 收尾·~878 股尾段)+FUSION_GRID_P1 '
              '入池后 autofill 自动烧分片；09-28 周一首新 bar 全链；迁移 v2.2 armed '
              'editor-gated 窗至 09-29 12:00(勿双 arm)')
st['last_round_ts'] = now_iso
st['last_result'] = 'ok'
st['current_task'] = 'r300 maintenance round (T-87 probe#13 + 5x HANDOVER/ledger reconcile + S6 30/30)'
st['updated_at'] = now_iso
with io.open(STATE, 'w', encoding='utf-8', newline='') as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# --- heartbeat bm-b.json ---
with io.open(HB, encoding='utf-8-sig') as f:
    hb = json.load(f)
hb['last_seen'] = now_iso
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = now_iso
hb['current_task'] = st['current_task']
if cpu_pct is not None:
    hb['cpu_util_pct'] = cpu_pct
    hb['cpu_pct'] = cpu_pct
if free_ram_gb is not None:
    hb['free_ram_gb'] = free_ram_gb
    hb['idle_ram_gb'] = free_ram_gb
    hb['idle_ram_mb'] = int(free_ram_gb * 1024)
    hb['free_ram_mb'] = int(free_ram_gb * 1024)
if gpu_free_gb is not None:
    hb['gpu_free_vram_gb'] = gpu_free_gb
    hb['gpu_idle_vram_gb'] = gpu_free_gb
    hb['gpu_free_vram_mb'] = int(gpu_free_gb * 1024)
    hb['gpu_idle_vram_mb'] = int(gpu_free_gb * 1024)
hb['round_no'] = 300
hb['round'] = 300
hb['verdict'] = 'green'
# orders_ack unchanged: 91/91, zero new orders this round
with io.open(HB, 'w', encoding='utf-8', newline='') as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# --- self-verify (smoke F7 laws) ---
with io.open(HB, encoding='utf-8-sig') as f:
    v = json.load(f)
assert isinstance(v['heartbeat_epoch_utc'], int), 'epoch must be JSON int'
assert 'T' in v['clock_read'] and '+' in v['clock_read'], 'clock_read must be T-separated ISO'
assert len(v['orders_ack'].split()) == v['n_orders_ack'] == 91, 'orders_ack count drift'
with io.open(STATE, encoding='utf-8-sig') as f:
    sv = json.load(f)
assert sv['round_no'] == 300, 'state round bump fail'
print('state round=300 | hb epoch int=', v['heartbeat_epoch_utc'],
      '| clock=', v['clock_read'],
      '| cpu=', cpu_pct, '| free_ram_gb=', free_ram_gb, '| gpu_free_gb=', gpu_free_gb)
