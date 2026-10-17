# -*- coding: utf-8 -*-
"""r1035 bm-a closeout: HANDOVER 5x row + round report line + state + heartbeat.
Fresh-read + append/atomic-write per multi-writer ledger laws (r583/r775)."""
import json, os, time, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().astimezone()
TS = NOW.strftime('%Y-%m-%dT%H:%M:%S') + NOW.strftime('%z')[:3] + ':' + NOW.strftime('%z')[3:]

# ---------- 1) HANDOVER r1035 5x row (append at end) ----------
handover = os.path.join(ROOT, 'research', 'HANDOVER.md')
row = ("> bm-a round 1035 五倍数核对（2026-10-17T15:1x 核对；增量窗覆盖 r1031-r1035 五轮·5x 截恰逢其位零欠账·逐轮权威=ROOT round_reports-bm-a.md 全行在册+state-bm-a.json notes 族）："
"增量窗主线=**W 波链席位让路裁定线+moneyflow 双车道封锁观察线+rebase sequencer 卡死 bypass 律立法+S6 连绿**——"
"r1031=watermark_red 轮中活写者探明（watchdog Invoke-C7 腿=第二写者·py_watermark 非唯一·r1028 吸收配方对两写者通用）+closeout 工具坑自踩实录（PS5.1 Set-Content 重写 CJK py=GBK 双编码损毁·pit-encoding 姊妹面）；"
"r1032=D-19 收尾双扫增量消费（ORD 9bf93c91=bm-c V5 4 镜回执行·DEC 午班四拍板含 POOL-0020 代验收 dispatcher 席销卡）+W261 席位 MSG 归档+watermark_red amend 吸收（r1028 配方二次实弹）+**死窗死于 rebase sequencer 卡死**（all-conflicts-fixed 态 continue 反复拒·git 2.55.0.windows.2·根因未定谳疑共享探针面活写竞态）→**bypass 律落 CODELY**（quit+cherry-pick estate relay·r1032_absorb 判例）+push 竞速双拒 vs bm-c r1065/r1066 热推终达 200d29152；"
"r1033=S6 43/43 重跑 rc0+live_paper rc0（14:07→14:11）+D-19 ORD 1df82bab 推进消费（5 行零 BigMoney 派工）+W261 splice observed LANDED（bm-c 烧录·bm-a 候 W262）+moneyflow 封锁重测仍 active；"
"r1034=S6 43/43+live_paper bad=0+D-19 双 hold+**W262 席位让路裁定**（bm-c r1067 14:37:28 origin vacancy+commit-time 先到·bm-a per fleet README §4 让路·W263=bm-a 窗 gated on W262 注册·no-skip-claim 零 W263/W264 抢注验毕）+W261 完整链验证（splice 68aad04b6+自烧 12/12+sixgate 23rd PRE-FINALIZE ALL PASS+finalize one-pass 996,335+2,200=998,535 EXACT/K=572,120+fivekeys 6/6+sec.7/8 占位=0）+**moneyflow daykline 备份车道首现 conn 级 3 连败熔断**（300706-08 RemoteDisconnected 14:50·EM 封锁疑似自 clist 扩至 per-stock 端点族或瞬态·下轮重测裁定·checkpoint 完好）+rank 车道 fetch_failed fall-through 修法（r1027）工作如设计（无饿死）+四件套绿（watchdog S4U flip 拒绝访问携带 C-20261016-04）；"
"r1035=本核对轮〔S6 43/43 rc0+live_paper rc0（15:05:02→15:11:10·driver _r1035bma_s6chain.ps1）+D-19 双 hold（dec 1d4741e4/ord 1df82bab 双扫恒等零新行）+W262 注册观察=未落（bm-c 派生中·W263 bm-a 窗保持 gated）+moneyflow 重测=30min spawn 节流窗内诚实 no-op（15:20:41 后实际连接重测归下轮）+孤儿面=1 只读携带+四件套幂等（loop pin=8 no-op·watchdog -Force 重注 S4U flip 拒绝访问携带·双爪 MATCH 重装）+5x HANDOVER（本行）〕。"
"维护面全窗：smoke 49/49 链·S6 43 腿 rc0 链（r1033/r1034/r1035 三连）·D-19 双水位 method-pin（dec 1d4741e4/ord 1df82bab·r1032 消费后双 hold 链）·attrition CLEAN 链·孤儿面 0-1 只读链·四件套幂等链（S4U flip 拒绝访问=C-20261016-04 携带面）。"
"产品清单漂移（增量代表面非全列）=results/_r103{3,4,5}bma_s6chain.ps1+_r103{3,4,5}bma_s6chain_rc.log 驱动器/回执族+results/_r1032bma_* 遗产抢救工件族+CODELY.md r1032 bypass 律行（quit+cherry-pick estate relay）+docs/daily_report/REPORT-2026-10-17.md+docs/live_usage/LIVE-2026-10-17.md 再生+本行 research/HANDOVER.md。"
"指针：**W262 注册落地→W263 bm-a own-wave 席位窗（live re-derive post-W262 universe·禁 r587 转抄）+moneyflow 节流窗后连接重测（瞬态/扩面裁定·15:20+）+双任务 S4U 转换候提权窗（C-20261016-04）+月界首考 10-31**；下一 5x=bm-a r1040。[via bm-a r1035]\n")
with open(handover, 'r', encoding='utf-8', newline='') as f:
    raw = f.read()
if 'bm-a round 1035 ' in raw:
    print('HANDOVER row already present, skip')
else:
    if not raw.endswith('\n'):
        raw += '\n'
    raw += row
    tmp = handover + '.tmp1035'
    with open(tmp, 'w', encoding='utf-8', newline='') as f:
        f.write(raw)
    os.replace(tmp, handover)
    print('HANDOVER row appended, new size =', os.path.getsize(handover))

# ---------- 2) round report line (ROOT canonical face) ----------
rpt = os.path.join(ROOT, 'round_reports-bm-a.md')
line = (TS + " | r1035 bm-a (dept:舰队·常规维护轮·S6 43/43 全绿+W262 注册观察+moneyflow 节流窗内 no-op+5x HANDOVER) | "
"WM-VERDICT: 绿 (red=false lane=healthy; satengine ALIVE queue0 idle; idle green_idle=false 合法=RAM 20.2% CEO 周末用机) | "
"当前活=r1035 常规维护收口（S6 43/43 rc0+live_paper rc0·15:05:02→15:11:10；W262 注册未落=bm-c 派生中·W263 bm-a 窗保持 gated；D-19 双 hold dec 1d4741e4/ord 1df82bab 零新行；moneyflow=30min spawn 节流窗内诚实 no-op·15:20:41 后连接重测归下轮；队列 P2/P3 全 done 无 open 队头；孤儿面=1 只读携带；四件套幂等绿-watchdog S4U flip 拒绝访问携带 C-20261016-04）；"
"最近实物=results/_r1035bma_s6chain_rc.log（43/43 rc0 bad=0 15:11:10）+results/_r1035bma_s6chain.ps1+research/HANDOVER.md r1035 5x 行；"
"下个里程碑=W262 注册落地→W263 bm-a own-wave 席位窗（live re-derive post-W262 universe）+moneyflow 连接重测裁定（下轮 15:20+ 节流窗开后）；本地未达 origin commit 数=0（收口 push 后自证）\n")
with open(rpt, 'r', encoding='utf-8', newline='') as f:
    raw = f.read()
if 'r1035 bm-a (' in raw:
    print('report line already present, skip')
else:
    if not raw.endswith('\n'):
        raw += '\n'
    raw += line
    tmp = rpt + '.tmp1035'
    with open(tmp, 'w', encoding='utf-8', newline='') as f:
        f.write(raw)
    os.replace(tmp, rpt)
    print('report line appended, lines =', raw.count('\n'))

# ---------- 3) state-bm-a.json ----------
st = os.path.join(ROOT, 'state-bm-a.json')
with open(st, 'r', encoding='utf-8') as f:
    s = json.load(f)
epoch = int(time.time())
did = ("r1035 closed: standard maintenance round: S0 fetch (rebase blocked by runtime live faces, non-blocking; local==origin 0/0) + round-zero orphan probe (py_faces=17 orphans=1 read-only carried) + "
"S0.5 fleet ORD 差集空 (latest O-20261017-0131 acked) + D-19 opening double-probe HOLD (dec 1d4741e4/ord 1df82bab identical to watermarks, zero new rows) + "
"S1 smoke 49/49 + watermark red=false lane healthy + satengine ALIVE queue0 idle (py 0%) + idle green_idle=false lawful (RAM 20.2% CEO weekend machine) + "
"queue P2/P3 heads all done (no open rows) + W262 registration watch = NOT yet registered (bm-c deriving, W263 bm-a window stays gated, live re-derive law) + "
"moneyflow retest observation = 30-min spawn throttle window (last spawn 14:50:41 -> next 15:20:41), S6 leg honest no-op, actual conn retest adjudication deferred to next round; panel cutoff 2026-10-13 complete=False standing + "
"S6 chain 43/43 rc0 + live_paper rc0 bad=0 (15:05:02->15:11:10, driver _r1035bma_s6chain.ps1) + quad green (loop pin=8 no-op, watchdog -Force idempotent re-reg with S4U flip access-denied carried C-20261016-04, precommit+prepush claws MATCH reinstall) + "
"5x HANDOVER duty = r1035 row appended (increment r1031-r1035) + commit+push closeout")
s.update({
    'round_no': 1035, 'round': 1035, 'loop_round': 1035, 'last_round': 1035,
    'clock_read': TS, 'ts': TS, 'updated': TS, 'updated_at': TS, 'last_run': TS, 'last_seen': TS,
    'last_round_at': TS, 'last_round_closed': TS, 'last_round_ts': TS, 'last_heartbeat_epoch_utc': s.get('heartbeat_epoch_utc', epoch),
    'heartbeat_epoch_utc': epoch, 'heartbeat_epoch_utc_type_int': True,
    'idle_rounds': 0, 'agenda_starved': False, 'orphan_face': 1, 'orphan_faces': 1, 'orphan_killed': 0,
    'current': did, 'did': did,
    'current_task': 'r1035 maintenance (S6 43/43 + W262 registration watch + moneyflow throttle-window no-op + 5x HANDOVER)',
    'task': 'r1035 maintenance (S6 43/43 + W262 registration watch + moneyflow throttle-window no-op + 5x HANDOVER)',
    'last_action': 'r1035: S6 43/43 rc0 + D-19 double-hold + W262 registration watch (W263 gated) + moneyflow throttle-window no-op + 5x HANDOVER row',
    'last_action_at': TS,
    'last_artifact': 'results/_r1035bma_s6chain_rc.log (43/43 rc0 bad=0 15:11:10) + results/_r1035bma_s6chain.ps1 + research/HANDOVER.md r1035 5x row',
    'recent_artifact': 'results/_r1035bma_s6chain_rc.log (43/43 rc0 bad=0 15:11:10) + results/_r1035bma_s6chain.ps1 + research/HANDOVER.md r1035 5x row',
    'latest_artifact': 'results/_r1035bma_s6chain_rc.log (43/43 rc0 bad=0 15:11:10) + results/_r1035bma_s6chain.ps1 + research/HANDOVER.md r1035 5x row',
    'now_active': 'bm-a r1035 maintenance closed; W262 = bm-c seat (registration pending, W263 bm-a window gated); moneyflow double-lane conn-block observation standing (throttle window retest next round)',
    'verdict': 'green r1035 maintenance (S6 43/43 rc0 bad=0 + smoke 49/49 + satengine ALIVE queue0 + D-19 double-hold + W262 watch gated + moneyflow throttle no-op honest + quad green)',
    'verify': 'S6 43/43 rc0 log _r1035bma_s6chain_rc.log + smoke 49/49 + d19 double-hold (dec/ord identical) + claws match x2 + loop pin=8 no-op + attrition rc0',
    'next': 'r1036+: (a) W262 registration watch -> W263 bm-a own-wave seat window (live re-derive post-W262-REGISTERED universe, never transcribe r587); (b) moneyflow conn retest after 15:20:41 throttle window (transient vs widened adjudication); (c) dual-task S4U conversion carried (C-20261016-04); (d) next 5x = r1040',
    'next_milestone': 'W262 registration -> W263 bm-a seat window + moneyflow conn retest adjudication (next round post-15:20)',
    'last_decisions_seen': 'r1035: dec 1d4741e4 hold both scans (identical to watermark)',
    'last_orders_seen': 'r1035: opening + closing double-scan both HOLD (ord 1df82bab identical zero new rows; dec 1d4741e4 hold both)',
    'last_decisions_at': TS, 'last_orders_at': TS, 'last_decisions_read_at': TS, 'last_orders_read_at': TS,
    'notes_r1035': ('r1035: (1) W262 registration NOT yet landed at 15:0x (seat MSG 14:37 published, prereg derive = bm-c next window FIRST ACTION) -> W263 bm-a window stays gated, zero skip-claim; '
                    '(2) moneyflow retest deferred by design: 30-min spawn throttle (last_spawn 14:50:41 -> 15:20:41) means S6 leg honest no-op; actual conn retest = next round window; '
                    '(3) S0 rebase blocked by 3 runtime live faces (heartbeat stat-noise + orphan probe + watermark_red shared probe) = non-blocking fetch-only path, absorbed at closeout add -A per r751 law; '
                    '(4) watchdog S4U flip access-denied = known carried face C-20261016-04 (manual S4U re-pass needs elevation window)'),
})
# fresh RAM/CPU sample if psutil available (else keep last known)
try:
    import psutil
    ram = psutil.virtual_memory()
    s['free_ram_gb'] = round(ram.available / (1024**3), 1)
    s['ram_free_gb'] = s['free_ram_gb']
    s['idle_ram_gb'] = s['free_ram_gb']
    s['ram_free_pct'] = round(ram.available * 100 / ram.total, 1)
    s['free_ram_pct'] = s['ram_free_pct']
    s['ram_load_pct'] = round(100 - s['ram_free_pct'], 1)
    s['cpu_pct'] = psutil.cpu_percent(interval=1)
    s['cpu_total_pct'] = s['cpu_pct']
    s['cpu_load_pct'] = s['cpu_pct']
except Exception as e:
    print('psutil sample skipped:', repr(e))
tmp = st + '.tmp1035'
with open(tmp, 'w', encoding='utf-8', newline='') as f:
    json.dump(s, f, ensure_ascii=False, indent=1)
os.replace(tmp, st)
with open(st, 'r', encoding='utf-8') as f:
    chk = json.load(f)
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
print('state updated: round_no=', chk['round_no'], 'epoch_int=', isinstance(chk['heartbeat_epoch_utc'], int), 'ram_free=', chk.get('free_ram_gb'), 'cpu=', chk.get('cpu_pct'))

# ---------- 4) heartbeat fleet/machines/bm-a.json ----------
hb_path = os.path.join(ROOT, 'fleet', 'machines', 'bm-a.json')
with open(hb_path, 'r', encoding='utf-8') as f:
    hb = json.load(f)
hb.update({
    'last_seen': TS, 'ts': TS, 'clock_read': TS,
    'heartbeat_epoch_utc': epoch,
    'current_task': 'r1035 maintenance closed (S6 43/43 rc0 + W262 watch + moneyflow throttle no-op + 5x HANDOVER)',
    'task': 'r1035 maintenance closed (S6 43/43 rc0 + W262 watch + moneyflow throttle no-op + 5x HANDOVER)',
    'verdict': 'green r1035 maintenance (S6 43/43 rc0 bad=0 + smoke 49/49 + satengine ALIVE queue0 + D-19 double-hold + W262 watch gated + quad green)',
    'idle_rounds': 0,
    'agenda_starved': False,
    'did': did,
    'last_action': 'r1035: S6 43/43 rc0 + D-19 double-hold + W262 registration watch (W263 gated) + moneyflow throttle-window no-op + 5x HANDOVER row',
    'now_active': 'bm-a r1035 maintenance closed; W263 bm-a window gated on W262 registration (bm-c deriving); moneyflow retest next round post-15:20',
    'free_ram_gb': s.get('free_ram_gb'), 'ram_free_gb': s.get('free_ram_gb'),
    'cpu_pct': s.get('cpu_pct'),
    'next': 'r1036: W262 registration watch -> W263 bm-a seat window; moneyflow conn retest (post-15:20)',
})
tmp = hb_path + '.tmp1035'
with open(tmp, 'w', encoding='utf-8', newline='') as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
os.replace(tmp, hb_path)
with open(hb_path, 'r', encoding='utf-8') as f:
    chk2 = json.load(f)
assert isinstance(chk2['heartbeat_epoch_utc'], int), 'hb epoch must be int'
assert 'T' in chk2['clock_read'], 'clock_read must be T-separated'
print('heartbeat updated ok, epoch=', chk2['heartbeat_epoch_utc'])
print('CLOSEOUT_SCRIPT_DONE')
