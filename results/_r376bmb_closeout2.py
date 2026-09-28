# r376 bm-b closeout continuation: size gate, archive batch-46, state, heartbeat (report already appended)
import io, json, os, time, datetime, subprocess

ROOT = r'C:\Users\Administrator\Desktop\Bigmoney'
cp = os.path.join(ROOT, 'CODELY.md')
sz = os.path.getsize(cp)
print('CODELY.md size now:', sz)
assert sz <= 10240, 'still over 10KB hard line: %d' % sz

# ---- archive batch-46: r375 entry verbatim (source of truth = git HEAD pre-fold CODELY.md) ----
head_codely = subprocess.run(['git', 'show', 'HEAD:CODELY.md'], capture_output=True, cwd=ROOT).stdout.decode('utf-8')
marker = '- [2026-09-28 10:2 r375 bm-b] 坑律：'
idx = head_codely.find(marker)
assert idx >= 0, 'r375 entry not in HEAD CODELY.md'
r375_line = head_codely[idx:].split('\n', 1)[0].rstrip()
ap = os.path.join(ROOT, 'research', 'memory-archive', '202609.md')
asec = ('\n\n## 坑律归档 2026-09-28 四十六批（r376 bm-b 窗·水位律当窗整编类：CODELY.md append 后超 ≤10KB 硬线）\n\n'
        + r375_line + '\n')
with io.open(ap, 'a', encoding='utf-8', newline='') as f:
    f.write(asec)
atxt = io.open(ap, encoding='utf-8').read()
assert r375_line in atxt, 'zero-loss check failed: r375 line not verbatim in archive'
assert marker not in io.open(cp, encoding='utf-8').read(), 'r375 entry still in hot CODELY.md'
print('batch-46 fold landed + zero-loss verified (r375 -> archive verbatim, hot cleared)')

# ---- state.json round_no++ ----
sp = os.path.join(ROOT, 'state.json')
st = json.load(open(sp, encoding='utf-8'))
st['round_no'] = 376
st['note'] = ('r376 bm-b: S0 pull r149-族 abort 自愈实况(并发 autofill 代完 rebase 零 reset --hard)+CODELY r376 坑律+四十六批整编; '
 'S6 30 腿 rc=0; census W2B 在飞+W4-GENERATE autofill 在飞; judge flips RAM 门未放行')
io.open(sp, 'w', encoding='utf-8', newline='').write(json.dumps(st, ensure_ascii=False, indent=1) + '\n')
print('state.json round_no ->', st['round_no'])

# ---- heartbeat refresh ----
now = datetime.datetime.now().astimezone()
ts = now.strftime('%Y-%m-%dT%H:%M:%S+08:00')
epoch = int(time.time())
import psutil
vm = psutil.virtual_memory()
free_gb = round(vm.available / 1024**3, 2)
cpu_pct = psutil.cpu_percent(interval=1)
gpu_free_mb = None
try:
    o = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
                       capture_output=True, text=True, timeout=20)
    gpu_free_mb = int(o.stdout.strip().splitlines()[0])
except Exception as e:
    print('nvidia-smi fail:', e)

hbp = os.path.join(ROOT, 'fleet', 'machines', 'bm-b.json')
hb = json.load(open(hbp, encoding='utf-8'))
hb['last_seen'] = ts
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = ts
hb['current_task'] = ('r376 done: S0 pull abort r149-族自愈(autofill 代完 rebase, 零 reset --hard, blob 恒等核验)+坑律 r376+批46整编; '
 'S6 30 legs rc=0 (lawful stale-takeover @ bma hb stale 40min); census W2B in-flight + W4-GENERATE autofill 在飞; '
 'next: census finalize -> RAM 3-sample -> W1/MASS x4/W2/W3 flips -> W2/W3 intake; 15:30 new-bar window astock_daily/rev_osc + live.paper trio')
hb['round_no'] = 376
hb['round'] = 376
hb['loop_round'] = 376
hb['free_ram_gb'] = free_gb
hb['idle_ram_gb'] = free_gb
hb['free_ram_mb'] = int(free_gb * 1024)
hb['idle_ram_mb'] = int(free_gb * 1024)
hb['cpu_util_pct'] = cpu_pct
hb['cpu_pct'] = cpu_pct
if gpu_free_mb is not None:
    hb['gpu_free_vram_gb'] = round(gpu_free_mb / 1024, 2)
    hb['gpu_idle_vram_gb'] = round(gpu_free_mb / 1024, 2)
    hb['gpu_free_vram_mb'] = gpu_free_mb
    hb['gpu_idle_vram_mb'] = gpu_free_mb
hb['verdict'] = ('healthy: smoke 25/25, S6 30 legs rc=0; S0 pull abort r149-族=自愈实况(并发 autofill 代完 rebase, 零手动 reset --hard, '
 'blob 76348fa 恒等, in-sync origin 3bdfe4f1); census W2B in-flight + W4-GENERATE autofill 在飞; judge flips RAM-gated r354 not-yet(free<4GB); '
 'orders 99/99 dual-scan; board 0 open; migration executor=armed precheck waiting(Tuanjie gate), zero interference')
hb['n_orders_ack'] = len(hb.get('orders_ack', []))
io.open(hbp, 'w', encoding='utf-8', newline='').write(json.dumps(hb, ensure_ascii=False, indent=1) + '\n')
chk = json.load(open(hbp, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
print('heartbeat: epoch int =', chk['heartbeat_epoch_utc'], '| clock =', ts, '| free_ram_gb =', free_gb, '| cpu =', cpu_pct, '| gpu_free_mb =', gpu_free_mb)
print('DONE r376 closeout continuation')
