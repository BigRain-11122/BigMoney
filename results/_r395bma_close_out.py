# r395 bm-a close-out: round report line + state round_no + heartbeat (epoch int self-check)
# evidence script per _r150bmc_* precedent; run once, then committed with round close.
import json, time, datetime

now = datetime.datetime.now()
ts_iso = now.strftime('%Y-%m-%dT%H:%M:%S') + '+08:00'

# ---- 1. round report line (S5) ----
rr = 'logs/iteration-loop/round_reports-bm-a.md'
line = (
 "2026-09-28T09:1x+08:00 | R395 bm-a (dept:策略+研究·TRIAL_LABOR 常设线 W3 screen-finalize 收割轮) | "
 "WM first-line verdict: 绿（red=false lane healthy；probe 09:04:55 py_low_board_clear 合法闲置白名单：板 0 open+bandit 0+本机无可跑批〔W3-SCREEN 已 done 翻面；池 1 ready=W2B census bm-b 车道护栏；judge 面 waiting=bmb flip 串行+RAM〕；audit v2.3 CLEAN flags=[]）| "
 "did: S0-1 锚定 bm-a+S0 FF 拉齐 bm-c r150（8347895e）+tick 活写 fold-in c0496cde（r369 live-writer-wins 律）+rebase onto 718f896b；"
 "S0.5 orders 99/99 双扫零未回执+决策审核：**D-20260928-02① 实证已落地**（autofill claim/keepalive/tick 三层 pre-add mid-op 守卫 r331 竞态窗 defer+S15j/S17h 腿=commit 6a8e2bb2 00:31 在册·本轮回执）+D-20260928-03① pin=8 S7 verify no-op 在册+D-03② 车道迁移续批（pool retirement r388 面在用）+D-06 委员会 C-02 席3 意见已在册（F-20260928-01 零新动作）；"
 "S1 smoke 25/25+S2 双板零 open（97 票全 claimed/done）；"
 "S3 主闭环：**TRIAL_LABOR_W3 screen-finalize LANDED**（烧批车道=bma per bmc r150 yield close·开工前 fetch+inbox 复读 r394 坑律遵守）：烧批 08:50:01 pid 27476→08:54:39 checkpoint **3752/3752**（3552 候选+200 null·~4.6min·target_met=true）+tick 09:00:01 重拉 todo=0 quick-exit（shard 未翻 done 前重拉=已知无害面·checkpoint 零追加实证）→finalize missing-cells 门零缺格→null p95 0.511572（=641/1253 离散格点·与 W2 同格=格点巧合非同源 bug·双波 rate 列表实测不同已核验）→**survivors 513/3552=14.4%**（gate 分段：bear 218/1150=18.96%／none 163/1220=13.36%／bull 132/1182=11.17%——GATE x2 生存成本如实披露）→产物 w3_screen.json（evidence_cutoff 2026-09-22 C2 键·grammar 锚 cc59eab79db53436 恒等·ledger **297,428→301,180** 批 3,752）+w3_screen_cells.csv 3552 行+gate_attrition TRIAL_LAB_W3_SCREEN 行（镜像 MASS schema·判线 strict->）+池条目 done 翻面（tick 重拉止）+**MSG-0915 judge-unblock 回执**（bmb r370 judge 三件套物理依赖 screen-finalize 已满足·剩余=RAM r354 三采样）——push 68cc3d06；"
 "S6 33 腿全 rc=0（盘前 no-op 族·cutoff 09-24 中秋正确；AH refresh+moneyflow rank pass 分离后台合法 spawn；regime ORANGE shadow breadth 0.77；clock ORANGE_COOL sleeves4 activated0；live 族幂等 OK；t35v PASS 零例；t24 22/22+promo 0/22 诚实；scorecard 6+28+7；daily_report faces=4 token=1；token L2=0）；"
 "S7：orders scan-2 99/99+post_review 零 ✗+inbox MSG-0844/0858 归档 processed（和解闭环）+MSG-0905 处理（bmb judge 认领零异议让路）+bmb r370 judge 落地两笔 pull 零冲突（零文件重叠） | "
 "verify: finalize 产品全字段验（C2 顶层键+账本链+锚恒等+CSV 行数）+smoke 25/25+S6 33 腿 rc=0（2 腿本机命令拼装误报重跑绿·非模块故障）+schtasks Loop Running pin=8+claw identical+watermark red=false+heartbeat epoch int 自证 | "
 "next: IntradayMarks 09:25 首拍验证（下轮首务·system_v1/REV-OSC 纸盘今日 marks）；W3-JUDGE 烧批=bmb flip executor（W2-JUDGE 先行串行·RAM 门）bma 二机验证位；15:30 后新 bar 全链接力（REGIME_GUARD v3 日期门 10-01 前 shadow 诚实）；TRIAL_LABOR 下一供给步=W4 grammar supply 调研（judge 队列在飞·起草窗开板空时）；D-03② 车道迁移下一批（consumer merge view）"
)
with open(rr, 'a', encoding='utf-8', newline='\n') as f:
    f.write(line + '\n')
print('round report appended')

# ---- 2. state-bm-a.json round_no 395 ----
st = json.load(open('state-bm-a.json', encoding='utf-8'))
st['round_no'] = 395
st['round'] = 395
st['loop_round'] = 395
st['did'] = ("R395: W3 screen-finalize 收割轮：烧批车道 bma（bmc r150 yield）3752/3752 全格→null p95 0.511572→survivors 513/3552=14.4%（gate 分段 bear 18.96%/none 13.36%/bull 11.17%）→产物 w3_screen.json+cells csv+gate_attrition 行+池 done 翻面+MSG-0915 judge-unblock 回执（push 68cc3d06）+决策 D-02① 实证回执（autofill mid-op 守卫 6a8e2bb2 在册）+D-03① pin=8 verify+S6 33 腿 rc=0+orders 99/99 双扫+inbox 三 MSG 处理归档")
st['verify'] = ("finalize 产品 C2 键+账本链 297,428→301,180+grammar 锚+CSV 行数全验+双波 null p95 同格点=离散格 641/1253 巧合核验非同源+smoke 25/25+S6 33 rc=0+pin=8+claw identical+red=false")
st['next'] = ("IntradayMarks 09:25 首拍验证（下轮首务）；W3-JUDGE=bmb flip executor 串行+RAM 门（bma 二机验证位）；15:30 新 bar 全链接力（v3 日期门 10-01 前 shadow）；W4 grammar supply 调研=TRIAL_LABOR 下一供给步；D-03② consumer merge view 下一批")
st['last_round_at'] = ts_iso
st['last_round_ts'] = ts_iso
st['last_round'] = ts_iso
st['current_task'] = 'r395 closed: W3 screen-finalize landed (513/3552 survivors, ledger 301,180); next = IntradayMarks 09:25 verify + judge burn watch (bmb flip)'
st['updated'] = ts_iso
st['ts'] = now.strftime('%Y-%m-%d %H:%M:%S')
json.dump(st, open('state-bm-a.json','w',encoding='utf-8',newline='\n'), ensure_ascii=False, indent=1)
print('state round_no=395 written')

# ---- 3. heartbeat fleet/machines/bm-a.json ----
hb = json.load(open('fleet/machines/bm-a.json', encoding='utf-8'))
epoch = int(time.time())
assert isinstance(epoch, int)
hb['machine_id'] = 'bm-a'
hb['last_seen'] = now.strftime('%Y-%m-%d %H:%M:%S')
hb['current_task'] = 'R395 done: W3 screen-finalize LANDED (burn lane bma per bmc yield; 3752/3752 cells; null p95 0.511572; survivors 513/3552; ledger 301,180; pool done-flipped; MSG-0915 judge-unblock) + D-02(1) receipt verified in-repo + S6 33 legs rc=0'
hb['cpu_cores'] = 32
hb['cpu_pct'] = 36.0
hb['free_ram_gb'] = 42.9
hb['gpu_free_vram_gb'] = 5.5
hb['verdict'] = ('py_low_board_clear legal idle (board closed 0 open; W3-SCREEN finalize landed+flipped this round; '
                 'pool 1 ready = CENSUS-FUS-S2-W2B bm-b lane guard; judge faces waiting = bmb flip executor serial+RAM r354; '
                 'IntradayMarks 09:25 armed first-fire)')
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = ts_iso
hb['task'] = 'round-closed'
hb['round_no'] = 395
hb['round'] = 395
hb['loop_round'] = 395
hb['cores'] = 32
hb['free_ram_mb'] = 42900
hb['idle_ram_gb'] = 42.9
hb['total_ram_gb'] = 100.6
hb['cpu_util_pct'] = 36.0
hb['gpu_free_vram_mb'] = 5629
hb['gpu_idle_vram_gb'] = 5.5
hb['gpu_idle_vram_mb'] = 5629
hb['gpu_total_vram_mb'] = 12282
hb['gpu0_free_vram_gb'] = 5.5
json.dump(hb, open('fleet/machines/bm-a.json','w',encoding='utf-8',newline='\n'), ensure_ascii=False, indent=1)
chk = json.load(open('fleet/machines/bm-a.json', encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
assert 'T' in chk['clock_read']
print('heartbeat written; epoch int verified:', chk['heartbeat_epoch_utc'], chk['clock_read'])
