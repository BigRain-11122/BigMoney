# r1032 bm-a closeout: W261 seat MSG archive + round report + state + heartbeat
# surgical field updates, utf-8, zero console CJK prints (pit-encoding law)
import json, io, os, shutil, time, subprocess, ctypes

ts_now = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
epoch = int(time.time())

# --- 1. MSG archive ---
src = r'fleet/inbox/MSG-20261017-1225-bmc-w261-seat.md'
dst = r'fleet/inbox/processed/MSG-20261017-1225-bmc-w261-seat.md'
os.makedirs(r'fleet/inbox/processed', exist_ok=True)
assert os.path.exists(src), 'seat MSG missing after pull'
if not os.path.exists(dst):
    shutil.move(src, dst)
print('MSG archived:', os.path.exists(dst) and not os.path.exists(src))

# --- 2. live machine read (RAM via ctypes, VRAM via nvidia-smi) ---
class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [('dwLength', ctypes.c_ulong), ('dwMemoryLoad', ctypes.c_ulong),
                ('ullTotalPhys', ctypes.c_ulonglong), ('ullAvailPhys', ctypes.c_ulonglong),
                ('ullTotalPageFile', ctypes.c_ulonglong), ('ullAvailPageFile', ctypes.c_ulonglong),
                ('ullTotalVirtual', ctypes.c_ulonglong), ('ullAvailVirtual', ctypes.c_ulonglong),
                ('ullAvailExtendedVirtual', ctypes.c_ulonglong)]
m = MEMORYSTATUSEX(); m.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
ram_free_gb = round(m.ullAvailPhys / (1024**3), 1)
ram_total_gb = round(m.ullTotalPhys / (1024**3), 1)
ram_free_pct = round(100 - m.dwMemoryLoad, 1)
try:
    out = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
                         capture_output=True, text=True, timeout=20).stdout.strip().splitlines()
    gpu_free_vram_mb = int(float(out[-1]))
except Exception:
    gpu_free_vram_mb = -1
print('RAM free', ram_free_gb, 'GB /', ram_free_pct, '% ; VRAM free', gpu_free_vram_mb, 'MB')

# --- 3. round report append (root canonical face) ---
REPORT = r'round_reports-bm-a.md'
line = (ts_now + ' | r1032 bm-a (dept:舰队·常规值守+S6 全链绿+W261 席位消费轮) | '
 'S0 吸收 pre-window 运行面 3 件 (orphan probe+watermark ts+heartbeat stat-noise) -> commit 98d2a60b0 + pull --rebase clean; '
 'S0.5: fleet ORD 差集空 (最新 O-20261017-0131 已 ack); D-19 opening 双推进 dec 7f12de36->1d4741e4 + ord 1a0f2402->e4ce1c5a '
 '(消费=DEC D-20261017-04~07 决策轮午班四拍板: D-04 核销批 bigmoney 尾读零新行/D-05 BigStream 域/D-06 MiniGame 域/'
 'D-07 bm-b 停摆 E1 追认+POOL-0020 委员会代验收 [执行司=@bm-b 五面手术+dispatcher 写手席销卡·本环零直派·bm-b 停摆面在册] '
 '+ ORD 新行 c0697db 11:43 MV 暗水印令 [bm-a BigStream 交互窗行内 executed·零 BigMoney 动作]); '
 'S7 收尾双扫再捕获 ORD e4ce1c5a->9bf93c91 (增量=12:1x @bm-c 回执 V5 追加 4 镜重烧完成 [BigStream 域·INT8 768P 4/4+盲评过·零本司动作]) 消费+推进 read-back 恒等; '
 'S1 smoke 49/49 | S3: satengine ALIVE rc0 queue0 idle; watermark red=false healthy (next_pick=moneyflow IC 候面板); '
 'idle green_idle=false (RAM ' + str(ram_free_pct) + '% free/VRAM ' + str(gpu_free_vram_mb) + 'MB·CEO 周六用机+本机 MV V5 产线在飞=合法占用·无领单义务·idle_rounds=0); '
 '任务板零 open+jobs 0+P2/P3 队列耗尽; POOL 复审面: POOL-0003 whisper 词级锚点=活已由本机交互窗 V5 精修令承接 (行内「词级锚点重产在跑」·同活禁双开·销卡归 dispatcher 席零本环动作)+POOL-0010/0016/0018/0019/0020=他司/他机域; '
 'W260 finalize 落链 (ledger 994,135+2,200=996,335 EXACT / K 567,720+2,200=569,920 EXACT·fivekeys 6/6·sixgate 22nd 连绿) + '
 'W261 席位=bm-c r1065 55th-gen 同窗发布 (A 589_501..591_500 staircase TENTH A-hop / B 591_501..591_700 ELEVENTH above-own-A·bm-c 81st own·W261 freeze UNBLOCKED·prereg derive=其下窗首动作) — '
 'MSG-20261017-1225-bmc-w261-seat 内容已消费+归档 processed/ (bm-a 无并发主张·commit-time 序让路干净); bm-a own-wave 候位=W262 (post-W261 finalize·MSG 前瞻=staircase ELEVENTH A-hop 预期·live re-derive governs); '
 'S6 43/43 rc0 bad=0 (driver results/_r1032bma_s6chain.ps1·log results/_r1032bma_s6chain_rc.log·12:16:31->12:23:43); '
 'moneyflow 封锁复测=封锁延续 (refresh 3 连 RemoteDisconnected->conn_stopped 11:29:39·rank fetch_failed 12:19:29·panel cutoff 2026-10-13 complete=false n=5222·gate 30min 自愈在役·checkpoint 完好·解封后 todo 全宇宙 ~2.1h); '
 'S7: watermark_red 活写竞速窗 amend 吸收 (watchdog C7 面·r1028 配方) + Loop pin 检查 + 双爪 CR 归一 + push behind-0 自证 | '
 'scoring: 1 (S6 数据链 43 面续鲜+双 D-19 推进+席位 MSG 消费=文件级实物; 无新研究增量 [引擎席未开·板空·队列尽·封锁窗未解]) | '
 'next: (a) W261 prereg/freeze/finalize 监视 -> 落地即 W262 own-wave 候位窗开 (探针+席位 MSG·窗<=48h); (b) moneyflow 解封复测随每轮 S6 gate (MF-IC-P1 候 N>=150 资格门=面板 complete 第一件); (c) 5x HANDOVER 核对轮=1035; (d) 双任务 S4U 转换候提权窗 (C-20261016-04 批授权在册) | orphan face: 1 只读沿载 | [r1032 bm-a]')
with io.open(REPORT, 'a', encoding='utf-8', newline='') as f:
    f.write('\n' + line + '\n')
print('report appended')

# --- 4. state update ---
S = r'state-bm-a.json'
d = json.load(io.open(S, encoding='utf-8'))
r1032 = ('r1032 closed: 常规值守+S6 全链绿+W260 finalize 消费/W261 席位消费轮 -- (1) S0 吸收 3 运行面 commit 98d2a60b0+amend 竞速窗 -> rebase 2 commits CLEAN; '
 '(2) D-19 opening 双推进 (dec 1d4741e4/ord e4ce1c5a: DEC D-04~07 四拍板零本司直派 + ORD MV 暗水印行) + 收尾双扫 ORD 再推进 9bf93c91 (bm-c V5 4 镜回执·BigStream 域零动作); '
 '(3) S1 smoke 49/49; satengine ALIVE rc0 队列 0; (4) idle green_idle=false (CEO 周六用机合法)·板空·队列尽·POOL-0003 复审=交互窗已承活禁双开; '
 '(5) W260 finalize 落链+W261 席位 bm-c 同窗发布 (A 589_501..591_500/B 591_501..591_700) -> MSG-1225 消费归档·bm-a 候 W262; '
 '(6) S6 43/43 rc0 bad=0 (12:16:31->12:23:43·driver _r1032bma_s6chain.ps1); moneyflow 封锁延续 (conn_stopped·rank fetch_failed·gate 自愈在役); '
 '(7) S7: pin/爪检查+push behind-0 自证')
d['round_no'] = 1032; d['round'] = 1032; d['loop_round'] = 1032; d['last_round'] = 1032
d['current'] = r1032; d['current_task'] = 'r1032 常规值守+S6 全链绿+W261 席位 MSG 消费 (moneyflow 封锁窗续候)'
d['did'] = r1032; d['last_action'] = 'r1032: 常规值守+S6 43/43 rc0 + D-19 双推进+收尾增量 1 行消费 + W260 finalize/W261 席位 MSG 消费归档 + moneyflow 封锁复测 (延续) + POOL-0003 复审 (交互窗已承活)'
d['task'] = 'r1032 常规值守+S6 全链绿+W261 席位消费'
d['now_active'] = ('bm-a r1032 毕 (常规值守+S6 全链绿); engine-lane = W261 席位 bm-c 占有 (prereg derive=其下窗首动作·freeze UNBLOCKED), '
 'bm-a own-wave 候位 W262 (post-W261 finalize); 35B:8090 常设; 周六午后值守合法 (CEO 用机中·MV V5 产线本机在飞)')
art = ('results/_r1032bma_s6chain_rc.log (43/43 rc0 bad=0) + results/_r1032bma_s6chain.ps1 (驱动器) + '
 'fleet/inbox/processed/MSG-20261017-1225-bmc-w261-seat.md (W261 席位消费归档) + S6 吸收 commit (76 files) + D-19 双推进 read-back 恒等')
d['last_artifact'] = art; d['latest_artifact'] = art; d['recent_artifact'] = art
d['last_action_at'] = ts_now
d['next'] = ('r1033+: (a) W261 prereg/freeze/finalize 监视 (bm-c 席) -> finalize 落地即 W262 own-wave 候位窗开 (探针 _w262bma 系+席位 MSG·post-W261 REGISTERED universe live 重推导·staircase ELEVENTH A-hop 前瞻已录); '
 '(b) moneyflow 封锁窗 lift 复测随每轮 S6 gate (源解封后 todo 全宇宙 ~2.1h complete·再评估 gap-fill repull 夜窗 ~3.6h); '
 '(c) MF-IC-P1 候 N>=150 资格门 (panel complete 只第一件); (d) 5x HANDOVER 核对轮=1035; '
 '(e) 双任务 S4U 转换候提权窗 (C-20261016-04 批授权在册·@bm-a 48h 首批回执); (f) POOL-0018 bm-b 词级滚动候 (音源 CEO 物理件)')
d['next_milestone'] = 'W261 finalize -> W262 own-wave 候位窗 (bm-c prereg derive 在飞·ETA 今夜-明晨·窗 <=2026-10-19) + moneyflow panel complete (封锁 lift 后·窗 <=2026-10-19)'
d['verdict'] = ('green-standby r1032 (watermark=绿 red=false; smoke 49/49; satengine ALIVE rc0 队列 0; S6 43/43 rc0 bad=0; '
 'D-19 opening+收尾双推进 (dec 1d4741e4/ord 9bf93c91)·增量全消费零本司直派; moneyflow 封锁延续 conn_stopped·gate 自愈在役; '
 'W261 席位 bm-c 占有·bm-a 候 W262; 任务板零 open; 双爪 match; 孤儿面=1 只读沿载 (r1029 同读数)')
d['verify'] = ('smoke 49/49 + S6 43/43 rc0 bad=0 (log _r1032bma_s6chain_rc.log) + satengine status rc0 queue0 '
 '+ d19 update --advance x2 read-back 恒等 (dec 1d4741e4 两次推进恒等/ord e4ce1c5a->9bf93c91 收尾推进) '
 '+ W261 MSG 归档断言 (src gone/dst in) + push 后 behind-0 自证')
d['last_round_at'] = ts_now; d['last_round_closed'] = ts_now; d['last_round_ts'] = ts_now
d['last_run'] = ts_now; d['last_seen'] = ts_now; d['ts'] = ts_now
d['updated'] = ts_now; d['updated_at'] = ts_now; d['clock_read'] = ts_now
d['last_decisions_seen'] = 'r1032: DEC 1d4741e4 (D-20261017-04~07 午班四拍板·D-07 bm-b E1 追认+POOL-0020 代验收=执行司 @bm-b+dispatcher 席·零本司直派) 消费'
d['last_decisions_at'] = ts_now; d['last_decisions_ts'] = ts_now
d['last_decisions_sha'] = '1d4741e4a0d6514519040442182b0679a423d58896a4105861e152108be441f1'
d['last_decisions_read_at'] = ts_now
d['last_orders_seen'] = ('r1032: opening 双推进 ord e4ce1c5a (增量=c0697db 11:43 MV 暗水印令行·bm-a BigStream 交互窗 executed 零本司动作) '
 '+ 收尾双扫推进 9bf93c91 (增量=12:1x @bm-c V5 追加 4 镜重烧完成回执·BigStream 域零本司动作); fleet ORD 差集空 (O-0131 最新已 ack)')
d['last_orders_at'] = ts_now
d['last_orders_sha'] = '9bf93c91c353f72db729708c7b03b03ca6dd5ca70985cff1e6dbb36d10a7e98c'
d['last_orders_read_at'] = ts_now
d['last_orders_ts'] = ts_now
d['heartbeat_epoch_utc'] = epoch
d['free_ram_gb'] = ram_free_gb; d['ram_free_gb'] = ram_free_gb; d['idle_ram_gb'] = ram_free_gb
d['ram_free_pct'] = ram_free_pct; d['free_ram_pct'] = ram_free_pct
d['ram_load_pct'] = round(100 - ram_free_pct, 1)
d['total_ram_gb'] = ram_total_gb
d['gpu_free_vram_mb'] = gpu_free_vram_mb
d['gpu_source_note'] = 'nvidia-smi live read ' + ts_now + ' (CEO working machine + MV V5 line resident, honest free face)'
d['orphan_face'] = 1; d['orphan_faces'] = 1; d['orphan_killed'] = 0
d['notes_r1032'] = ('r1032: D-19 收尾双扫增量=bm-c V5 4 镜回执行 (ORD 9bf93c91)·opening DEC 增量=午班四拍板 (D-07 bm-b E1 追认在册·POOL-0020 代验收=dispatcher 席销卡); '
 'W261 席位 MSG 归档 face=内容先 git show 零树读+拉平后 shutil.move 断言; POOL.json 扫描踩 PS 管道 json 坑 (控制字符假错·subprocess raw-bytes 正法=reconfirm pit-ps); '
 'watermark_red 活写竞速窗 amend 吸收 (r1028 配方二次实弹)')
d['d19_watermark_guard']['round_ref'] = 1032
d['d19_watermark_guard']['ts'] = ts_now
d['orders_ack_note'] = 'r1032: +0 新 fleet 令 (差集空; 集团 ORD 增量 2 行均他司域回执/执行行·零本司派工·回执随本行)'
with io.open(S, 'w', encoding='utf-8', newline='') as f:
    json.dump(d, f, ensure_ascii=False, indent=1)
print('state updated')

# --- 5. heartbeat update ---
H = r'fleet/machines/bm-a.json'
h = json.load(io.open(H, encoding='utf-8'))
h['last_seen'] = ts_now; h['ts'] = ts_now; h['clock_read'] = ts_now
h['heartbeat_epoch_utc'] = epoch
h['current'] = r1032[:400]
h['did'] = d['did'][:400]
h['last_action'] = d['last_action']
h['task'] = d['task']; h['current_task'] = d['current_task']
h['now_active'] = d['now_active']
h['last_artifact'] = art[:400]
h['next_milestone'] = d['next_milestone']
h['verdict'] = 'green-standby r1032 (smoke 49/49; S6 43/43 rc0; watermark green; satengine ALIVE queue0; W261 seat bm-c owned, bm-a waits W262; CEO Saturday machine-use legal)'
h['idle_rounds'] = 0; h['agenda_starved'] = False
h['free_ram_gb'] = ram_free_gb; h['idle_ram_gb'] = ram_free_gb
h['free_ram_pct'] = ram_free_pct
h['gpu_free_vram_mb'] = gpu_free_vram_mb
h['ram_free_mb'] = int(ram_free_gb * 1024); h['idle_ram_mb'] = int(ram_free_gb * 1024)
h['last_heartbeat_epoch_utc'] = h.get('heartbeat_epoch_utc', epoch)
with io.open(H, 'w', encoding='utf-8', newline='') as f:
    json.dump(h, f, ensure_ascii=False, indent=1)
# epoch int self-check
chk = json.load(io.open(H, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
print('heartbeat updated, epoch int OK:', chk['heartbeat_epoch_utc'])
print('CLOSEOUT DONE')
