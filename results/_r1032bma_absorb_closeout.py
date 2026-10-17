# r1032 bm-a absorption-closeout: state + heartbeat + report supplement row
# surgical field updates only; dead-window r1032 face preserved, this window = same-round absorption completion
import json, io, time, ctypes

ts_now = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
epoch = int(time.time())

class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [('dwLength', ctypes.c_ulong), ('dwMemoryLoad', ctypes.c_ulong),
                ('ullTotalPhys', ctypes.c_ulonglong), ('ullAvailPhys', ctypes.c_ulonglong),
                ('ullTotalPageFile', ctypes.c_ulonglong), ('ullAvailPageFile', ctypes.c_ulonglong),
                ('ullTotalVirtual', ctypes.c_ulonglong), ('ullAvailVirtual', ctypes.c_ulonglong),
                ('ullAvailExtendedVirtual', ctypes.c_ulonglong)]
m = MEMORYSTATUSEX(); m.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
ram_free_gb = round(m.ullAvailPhys / (1024**3), 1)
ram_free_pct = round(100 - m.dwMemoryLoad, 1)
import subprocess
try:
    out = subprocess.run(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
                         capture_output=True, text=True, timeout=20).stdout.strip().splitlines()
    gpu_free_vram_mb = int(float(out[-1]))
except Exception:
    gpu_free_vram_mb = -1

absorb_note = ('r1032 absorption-closeout (THIS window, same-round per r1008/r1023 precedent): '
 'dead-window died mid-rebase (sequencer stall: all-conflicts-fixed but continue refused repeatedly, git 2.55.0.windows.2) -> '
 'bypassed via author-script manual commit + rebase --quit + manual cherry-pick x3 estate commits (33+1 UU shared faces '
 'resolved: d19 ord/dec by group-origin ground-truth sha, ts newer-wins, same-day regen faces take-HEAD bm-c 13:16 side) -> '
 'push raced twice (origin advanced to bm-c r1066 mid-flight) -> re-cherry-picked onto 8c16409ba -> '
 'DELIVERED 8c16409ba..200d29152 range-verified behind-0; D-19 advanced AGAIN this window dec 1d4741e4 hold / ord 9bf93c91->a8d19449 '
 '(14 rows scanned ALL BigStream/bm-c/BigGame lanes, ZERO BigMoney dispatch, zero-action); '
 'S6 chain re-run this window 43/43 rc0 bad=0 (13:47->13:50:38, driver _r1032bma_s6chain.ps1); '
 'S1 smoke 49/49; satengine ALIVE queue0 idle; watermark red=false healthy; quad green (pin=8 no-op, watchdog Ready, claws match x2, attrition rc0); '
 'idle green_idle=false (RAM ' + str(ram_free_pct) + '% CEO weekend machine = lawful); inbox zero unread; '
 'CODELY pitfall row appended (sequencer-stall bypass law 1071B); orphan face=1 read-only carried')

verdict = ('green r1032 absorption-closeout (watermark=绿 red=false; smoke 49/49; satengine ALIVE rc0 队列 0 idle; '
 'S6 43/43 rc0 bad=0 本窗重跑; D-19 ord a8d19449 消费零本司派工; push 200d29152 range+behind-0 双证; '
 'W261 席位=bm-c 80th own (prereg 已冻结 03ab504d7 bm-c r1066)·bm-a own-wave 候 W262; moneyflow 封锁延续 conn_stopped·gate 自愈在役; '
 '双爪 match; Loop pin=8 no-op; Watchdog Ready; 孤儿面=1 只读)')

did_full = ('r1032 closed (dead-window work + THIS absorption window combined): ' + absorb_note)

# --- state-bm-a.json surgical update ---
with io.open('state-bm-a.json', encoding='utf-8') as f:
    s = json.load(f)
s['current_task'] = 'r1032 absorption-closeout (estate 三提交抢救上链+S6 43/43 重跑绿+D-19 双消费)'
s['now_active'] = ('bm-a r1032 absorption closed (sequencer stall bypassed via quit+cherry-pick; estate delivered 200d29152); '
 'engine-lane = W261 bm-c 席位在册 (prereg frozen 03ab504d7·derive/splice/finalize 归 bm-c r1067+), bm-a own-wave 候 W262; '
 '35B:8090 常设 (bm-c LLM 路由承接面·看门狗在役); 周六午窗值守合法 (CEO 用机中)')
s['task'] = 'r1032 estate absorption closeout (rebase stall bypass + S6 rerun + D-19 ord a8d19449)'
s['did'] = did_full
s['last_action'] = 'r1032 absorption: quit+cherry-pick x3 estate landed (200d29152) + S6 43/43 rc0 rerun + D-19 ord a8d19449 + CODELY sequencer-stall pitfall row'
s['current'] = 'r1032 closed: ' + absorb_note
s['verdict'] = verdict
s['verify'] = ('push range 8c16409ba..200d29152 verified (fetch+behind-0) + S6 43/43 rc0 bad=0 log _r1032bma_s6chain_rc.log + '
 'smoke 49/49 + satengine rc0 + d19 update --advance read-back ord=a8d19449 恒等 + 双爪 CR 归一 match=YES + '
 'register_loop pin=8 no-op + attrition_guard rc0 (chain leg) + round_reports-bm-a.md r1032 absorption 行落盘')
s['last_artifact'] = ('origin 200d29152 (estate 三提交: r1032 S0 absorb + S6 absorb + closeout) + '
 'results/_r1032bma_s6chain_rc.log (43/43 rc0 bad=0 13:50:38) + results/_r1032bma_uu_resolve.py + '
 'results/_r1032bma_uu_takehead.py (双冲突解器) + CODELY.md sequencer-stall 判例行')
s['latest_artifact'] = s['last_artifact']
s['recent_artifact'] = s['last_artifact']
s['last_orders_seen'] = ('r1032 absorption: opening dual-advance dead-window consumed ord 9bf93c91; THIS window re-advance '
 'ord 9bf93c91->a8d19449 (14 rows scanned all BigStream/bm-c/BigGame lanes zero BigMoney dispatch); dec 1d4741e4 hold both windows')
s['last_orders_sha'] = 'a8d19449e1d412af13ee4bc72473703d4c7b4fae9afbd1245bf4d43d09acb81c'
s['last_orders_at'] = ts_now
s['last_orders_ts'] = ts_now
s['last_orders_read_at'] = ts_now
s['last_decisions_seen'] = 'r1032 absorption: dec 1d4741e4 恒等两窗零动作 (group origin decisions.md sha 双窗恒等)'
s['last_decisions_at'] = ts_now
s['last_decisions_ts'] = ts_now
s['last_decisions_read_at'] = ts_now
s['orders_ack_note'] = 'r1032: opening 差集空 (死窗); absorption 窗增量 9bf93c91->a8d19449 全扫 14 行=BigStream/bm-c/BigGame 域零本司派工·回执随本行'
s['last_round'] = 1032
s['round_no'] = 1032
s['round'] = 1032
s['loop_round'] = 1032
s['last_round_at'] = ts_now
s['last_round_closed'] = ts_now
s['last_round_ts'] = ts_now
s['last_run'] = ts_now
s['last_seen'] = ts_now
s['ts'] = ts_now
s['updated'] = ts_now
s['updated_at'] = ts_now
s['last_action_at'] = ts_now
s['heartbeat_epoch_utc'] = epoch
s['last_heartbeat_epoch_utc'] = s.get('last_heartbeat_epoch_utc') or epoch
s['clock_read'] = ts_now
s['free_ram_gb'] = ram_free_gb
s['ram_free_gb'] = ram_free_gb
s['idle_ram_gb'] = ram_free_gb
s['ram_free_pct'] = ram_free_pct
s['free_ram_pct'] = ram_free_pct
s['ram_load_pct'] = round(100 - ram_free_pct, 1)
s['gpu_free_vram_mb'] = gpu_free_vram_mb
s['gpu_source_note'] = 'nvidia-smi live read ' + ts_now + ' (CEO working machine, honest free face)'
s['idle_rounds'] = 0
s['agenda_starved'] = False
s['orphan_face'] = 1
s['orphan_faces'] = 1
s['notes_r1032_absorb'] = ('r1032: dead-window died in rebase sequencer stall (continue refused at all-conflicts-fixed state, '
 'root-cause undetermined, suspected shared-probe-face live-write race); THIS window bypass law landed in CODELY.md pit row '
 '(quit+cherry-pick estate relay); push raced twice vs bm-c r1065/r1066 hot-push, final delivery 200d29152 range+behind-0')
s['next'] = ('r1033+: (a) W261 监视 (bm-c 席·prereg 冻结毕·splice/finalize 归 bm-c) -> 落地即 W262 own-wave 候位窗开 '
 '(bm-a 探针+席位 MSG·post-W261 universe live 重推导); (b) moneyflow 封锁窗 lift 复测随每轮 S6 gate '
 '(解封后 todo 全宇宙 ~2.1h complete·MF-IC-P1 候 N>=150 资格门=面板 complete 第一件); (c) 5x HANDOVER 核对轮=1035; '
 '(d) 双任务 S4U 转换候提权窗 (C-20261016-04 批授权在册); (e) POOL 复审面续 (POOL-0010/0016/0018/0019/0020=他司他机域)')
s['next_milestone'] = 'W261 finalize->W262 own-wave 候位窗开 (bm-c 烧录 ETA 今日午后) + moneyflow panel complete (解封后·窗<=2026-10-19)'
with io.open('state-bm-a.json', 'w', encoding='utf-8', newline='') as f:
    json.dump(s, f, ensure_ascii=False, indent=1)
print('state updated')

# --- heartbeat fleet/machines/bm-a.json ---
with io.open('fleet/machines/bm-a.json', encoding='utf-8') as f:
    h = json.load(f)
h['machine_id'] = 'bm-a'
h['active'] = True
h['current'] = s['current']
h['current_task'] = s['current_task']
h['did'] = s['did']
h['last_action'] = s['last_action']
h['last_action_at'] = ts_now
h['last_artifact'] = s['last_artifact']
h['latest_artifact'] = s['last_artifact']
h['recent_artifact'] = s['last_artifact']
h['verdict'] = verdict
h['task'] = s['task']
h['now_active'] = s['now_active']
h['next'] = s['next']
h['next_milestone'] = s['next_milestone']
h['orders_ack_note'] = s['orders_ack_note']
h['last_orders_seen'] = s['last_orders_seen']
h['last_orders_sha'] = s['last_orders_sha']
h['last_orders_at'] = ts_now
h['last_orders_ts'] = ts_now
h['last_orders_read_at'] = ts_now
h['last_decisions_seen'] = s['last_decisions_seen']
h['last_decisions_sha'] = '1d4741e4a0d6514519040442182b0679a423d58896a4105861e152108be441f1'
h['last_decisions_at'] = ts_now
h['last_decisions_ts'] = ts_now
h['last_decisions_read_at'] = ts_now
h['last_round'] = 1032
h['round_no'] = 1032
h['round'] = 1032
h['loop_round'] = 1032
h['last_round_at'] = ts_now
h['last_round_closed'] = ts_now
h['last_round_ts'] = ts_now
h['last_seen'] = ts_now
h['last_run'] = ts_now
h['ts'] = ts_now
h['updated'] = ts_now
h['updated_at'] = ts_now
h['heartbeat_epoch_utc'] = epoch
h['heartbeat_epoch_utc_type_int'] = isinstance(epoch, int)
h['clock_read'] = ts_now
h['free_ram_gb'] = ram_free_gb
h['ram_free_gb'] = ram_free_gb
h['idle_ram_gb'] = ram_free_gb
h['ram_free_pct'] = ram_free_pct
h['free_ram_pct'] = ram_free_pct
h['ram_load_pct'] = round(100 - ram_free_pct, 1)
h['gpu_free_vram_mb'] = gpu_free_vram_mb
h['gpu_source_note'] = s['gpu_source_note']
h['idle_rounds'] = 0
h['agenda_starved'] = False
h['orphan_face'] = 1
h['orphan_faces'] = 1
h['orphan_killed'] = 0
with io.open('fleet/machines/bm-a.json', 'w', encoding='utf-8', newline='') as f:
    json.dump(h, f, ensure_ascii=False, indent=1)
chk = json.load(io.open('fleet/machines/bm-a.json', encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
print('heartbeat updated, epoch int OK =', chk['heartbeat_epoch_utc'])

# --- round report absorption supplement row ---
REPORT = 'round_reports-bm-a.md'
line = (ts_now + ' | r1032 bm-a ABSORPTION-CLOSEOUT 补充行 (dept:舰队·estate 抢救+S6 重跑绿+D-19 再消费·同轮收口 per r1008/r1023 判例) | '
 '死窗死于 rebase sequencer 卡死 (all-conflicts-fixed 态 continue 反复拒·git 2.55.0.windows.2·根因未定谳) -> '
 '本窗绕过四步法 (author-script 手动 commit + rebase --quit + cherry-pick x3 + update-ref) 抢救 estate 三提交上链: '
 '推送两撞竞态 (origin 两度前进至 bm-c r1065/r1066) -> 终态交付 8c16409ba..200d29152 range+behind-0 双证; '
 '33+1 共享面 UU 解毕 (d19 ord/dec 集团仓 ground-truth sha 判 + ts newer-wins + 当日幂等再生面 take-HEAD bm-c 13:16 新侧零损失); '
 'D-19 本窗再推进 ord 9bf93c91->a8d19449 (14 行增量全扫=BigStream/bm-c/BigGame 域·零 BigMoney 派工) + dec 1d4741e4 恒等; '
 'S1 smoke 49/49 重跑绿; S6 43/43 rc0 bad=0 本窗重跑 (13:47->13:50:38); satengine ALIVE 队列 0; watermark red=false; '
 '四绿 (pin=8 no-op 13:58 下一拍 / Watchdog Ready / 双爪 match / attrition rc0); idle green_idle=false (RAM ' + str(ram_free_pct) + '% CEO 周六用机合法); '
 'CODELY.md sequencer-stall 判例行落盘 (1071B·S4); orphan face=1 只读 | '
 '验证: push range 行+fetch behind-0+S6 log+S6chain_rc.log 44 行 | '
 'next: W261 finalize 监视->W262 own-wave 候位窗 / moneyflow 解封复测随 S6 gate / HANDOVER 1035 / S4U 提权候窗 | [r1032 bm-a absorption]')
with io.open(REPORT, 'a', encoding='utf-8', newline='') as f:
    f.write('\n' + line + '\n')
print('report supplement row appended')
print('ABSORPTION-CLOSEOUT-ALL-DONE')
