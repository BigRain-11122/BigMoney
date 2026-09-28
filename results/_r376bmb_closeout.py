# r376 bm-b S4/S5/S7 closeout: orders double-scan, round report, CODELY pit-law + batch-46 fold, state, heartbeat
import io, json, os, time, datetime, subprocess, shutil

ROOT = r'C:\Users\Administrator\Desktop\Bigmoney'
now = datetime.datetime.now().astimezone()
ts = now.strftime('%Y-%m-%dT%H:%M:%S+08:00')

# ---- 1) S7 orders double-scan (round-start scan was 99/99 empty diff) ----
odir = os.path.join(ROOT, 'fleet', 'orders')
files = sorted(f for f in os.listdir(odir) if f.startswith('O-') and f.endswith('.md'))
hb = json.load(open(os.path.join(ROOT, 'fleet', 'machines', 'bm-b.json'), encoding='utf-8'))
acked = set(hb.get('orders_ack', []))
unacked = [f for f in files if f not in acked]
print('DOUBLE-SCAN orders on disk:', len(files), 'unacked:', unacked)

# ---- 2) round report append ----
rp = os.path.join(ROOT, 'logs', 'iteration-loop', 'round_reports.md')
line = (ts + ' | round 376 bm-b | dept:舰队/工程 (维护+水位见证轮) | '
 'WM-VERDICT: 绿 (red=false@10:20:21 lane healthy; probe 10:39:25 py_low_with_work_cands=合法结构占用: '
 'census W2B 4-worker 在飞 + W4-GENERATE 已由 autofill 发射(10:30:02 pid26604 keepalive) + 板 0 open/0 bandit + '
 '重载 judge 候选全数 RAM 门 r354 未放行(free 2.8GB<4GB)=census 不释放就轮不到, 非怠工) | '
 'did: (1) S0-1 bm-b 锚定 + S0 pull --rebase 撞 r149 族未跟踪件 abort(Cannot fast-forward working tree @results/_r155bmc_resolve_rest.py)'
 '——零手动 reset --hard、三探后证实并发 autofill 自循环已代为完成 rebase 落位(HEAD 同步 origin 3bdfe4f1, blob 76348fa 双侧恒等; '
 '早前 hash 假 mismatch=PS UTF-16 重定向读数面 r352), 预拉快照 16ceee54+r369 活面律; '
 '(2) S0.5 orders 99/99 首尾双扫描零差集 + decisions.md 路径本机不存在=零动作; '
 '(3) smoke 25/25; '
 '(4) S6 维护链 30 腿 rc=0: compute_audit v2.3 无旗 / watermark probe py_low_with_work_cands / update_daily 盘前合法 / '
 'market_regime rc0 / strategy_scorecard+scorecard 面再 derive(bm-a hb 滞40min 合法 stale-takeover) / market_clock CALL-0924 ORANGE_COOL sleeves4 act0 / '
 'lhb no-op / bm-a+bm-c 守卫腿诚实 no-op(heat/futures/repo/options/moneyflow/sina_mf/ths/ah/fund_premium/sysv1) / '
 'astock_daily+rev_osc bm-b 腿 cutoff0924 幂等 no-op 零网络 / fundamental 0.8h 跳过 / b_layer_mask 再生 / '
 'live.paper 锚定 OK 2bars / t35 verify 0924 PASS 零例(+stale-takeover derive O-2100 s2.4) / prospect paper 22/22 drift0 / '
 'promotion 0/22 诚实腿败 / aggr+alloc+grid 幂等 no-op / t35_export 0924 落盘 / daily_scorecard+daily_report(0928 幂等再生)+build_status+token_meter(L2 0 today); '
 '(5) S7 任务自愈 pin=2 no-op + watchdog 就绪 + pre-commit 钳 OK; 迁移执行器实探=armed precheck 等待(Tuanjie 3 进程+车道 CWD 占柄未退, 窗至 09-29 12:00, 零干预零双 arm); '
 '(6) CODELY 坑律 r376 一条 + 当窗整编四十六批(r375 条 verbatim 归档零丢失校验)。| '
 'verify: smoke 25/25 PASS, S6 全腿 rc=0, git 同步 origin 3bdfe4f1, blob 76348fa 恒等 | '
 'next: census W2B 收尾(ETA~14:1x)→RAM 3-sample→W1/MASS x4/W2/W3 flips→finalize x5→W2/W3 intake; '
 '15:30 新 bar 窗 astock_daily/rev_osc+live.paper trio; W4-GENERATE autofill 在飞')
with io.open(rp, 'a', encoding='utf-8', newline='') as f:
    f.write('\n' + line + '\n')
print('round report appended')

# ---- 3) CODELY.md: append r376 pit-law, fold batch-46 (migrate r375 entry verbatim) ----
cp = os.path.join(ROOT, 'CODELY.md')
src = io.open(cp, encoding='utf-8').read()
new_entry = ('- [2026-09-28 10:5 r376 bm-b] 坑律：**pull --rebase abort 自荐 `git reset --hard`＝活写面在场时的毒方（r149 族的收方面）**'
 '——撞未跟踪件 abort(Cannot fast-forward your working tree) 后先三探 status -sb / log / rev-parse blob-hash 再动手；'
 '本窗实况=并发 autofill 自循环已代为完成 rebase 落位(16ceee54 零丢失)，盲从 reset --hard 必砸 census 活写面；'
 'blob 恒等比对禁 PS `>` 重定向(UTF-16 假 mismatch＝r352 面)，git rev-parse 直读。指针=16ceee54/3bdfe4f1。')
r375_marker = '- [2026-09-28 10:2 r375 bm-b] 坑律：'
idx = src.find(r375_marker)
assert idx >= 0, 'r375 entry not found'
r375_line = src[idx:].split('\n', 1)[0].rstrip()
batch46_ptr = ('冷层指针：坑律正典 2026-09-28 四十六批（r376 bm-b 窗·水位律当窗整编：r376 新坑律 append 后超 ≤10KB 硬线）：'
 'r375 逃逸分支 reconcile 重放陈 addendum 撞活写面（r369 活面新者胜 cherry-pick 面） 一条全文 verbatim=archive 202609.md'
 '『坑律归档 2026-09-28 四十六批』节（行级零丢失校验）。')
# remove r375 entry (tail), insert batch-46 pointer after batch-45 pointer line, append new entry at end
head = src[:idx].rstrip('\n')
b45 = '『坑律归档 2026-09-28 四十五批』节（行级零丢失校验）。'
i45 = head.find(b45)
assert i45 >= 0, 'batch-45 pointer not found'
insert_at = i45 + len(b45)
out = head[:insert_at] + '\n' + batch46_ptr + head[insert_at:] + '\n' + new_entry + '\n'
io.open(cp, 'w', encoding='utf-8', newline='').write(out)
sz = os.path.getsize(cp)
print('CODELY.md after append+fold:', sz, 'bytes')
assert sz <= 10240, 'still over 10KB hard line: %d' % sz

# archive batch-46 section with r375 entry verbatim + zero-loss verify
ap = os.path.join(ROOT, 'research', 'memory-archive', '202609.md')
asec = ('\n\n## 坑律归档 2026-09-28 四十六批（r376 bm-b 窗·水位律当窗整编类：CODELY.md append 后超 ≤10KB 硬线）\n\n'
        + r375_line + '\n')
with io.open(ap, 'a', encoding='utf-8', newline='') as f:
    f.write(asec)
atxt = io.open(ap, encoding='utf-8').read()
assert r375_line in atxt, 'zero-loss check failed'
assert r375_marker not in io.open(cp, encoding='utf-8').read(), 'r375 entry still in hot'
print('batch-46 fold verified: r375 entry verbatim in archive, removed from hot')

# ---- 4) state.json round_no++ ----
sp = os.path.join(ROOT, 'state.json')
st = json.load(open(sp, encoding='utf-8'))
st['round_no'] = 376
st['note'] = ('r376 bm-b: S0 pull r149-族 abort 自愈实况(并发 autofill 代完 rebase 零 reset --hard)+CODELY r376 坑律+四十六批整编; '
 'S6 30 腿 rc=0; census W2B 在飞+W4-GENERATE autofill 在飞; judge flips RAM 门未放行')
io.open(sp, 'w', encoding='utf-8', newline='').write(json.dumps(st, ensure_ascii=False, indent=1) + '\n')
print('state.json round_no ->', st['round_no'])

# ---- 5) heartbeat refresh (samples + int epoch + T-clock) ----
epoch = int(time.time())
try:
    import psutil
    vm = psutil.virtual_memory()
    free_gb = round(vm.available / 1024**3, 2)
    cpu_pct = psutil.cpu_percent(interval=1)
except Exception as e:
    free_gb, cpu_pct = None, None
    print('psutil fail:', e)
gpu_free_mb = None
try:
    o = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
                       capture_output=True, text=True, timeout=20)
    gpu_free_mb = int(o.stdout.strip().splitlines()[0])
except Exception as e:
    print('nvidia-smi fail:', e)

hb['last_seen'] = ts
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = ts
hb['current_task'] = ('r376 done: S0 pull abort r149-族自愈(autofill 代完 rebase, 零 reset --hard, blob 恒等核验)+坑律 r376+批46整编; '
 'S6 30 legs rc=0 (5 lawful stale-takeover @ bma hb stale 40min); census W2B in-flight + W4-GENERATE autofill 在飞; '
 'next: census finalize -> RAM 3-sample -> W1/MASS x4/W2/W3 flips -> W2/W3 intake; 15:30 new-bar window astock_daily/rev_osc + live.paper trio')
hb['round_no'] = 376
hb['round'] = 376
hb['loop_round'] = 376
if free_gb is not None:
    hb['free_ram_gb'] = free_gb
    hb['idle_ram_gb'] = free_gb
    hb['free_ram_mb'] = int(free_gb * 1024)
    hb['idle_ram_mb'] = int(free_gb * 1024)
if cpu_pct is not None:
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
hbp = os.path.join(ROOT, 'fleet', 'machines', 'bm-b.json')
io.open(hbp, 'w', encoding='utf-8', newline='').write(json.dumps(hb, ensure_ascii=False, indent=1) + '\n')
chk = json.load(open(hbp, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
print('heartbeat written: epoch int ok =', chk['heartbeat_epoch_utc'], '| free_ram_gb =', free_gb, '| cpu =', cpu_pct, '| gpu_free_mb =', gpu_free_mb)
print('DONE r376 closeout files')
