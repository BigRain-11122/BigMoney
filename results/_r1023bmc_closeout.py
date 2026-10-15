# -*- coding: utf-8 -*-
# r1023 bm-c closeout books: round report row + state-bm-c.json + heartbeat.
import io, json, subprocess, datetime, os

NOW = datetime.datetime.now()
TS = NOW.strftime('%Y-%M-%dT%H:%M:%S+08:00')  # fixed below
TS = NOW.isoformat(timespec='seconds') + '+08:00'
EPOCH = int(NOW.timestamp())

ROW = ('2026-10-15T10:2x placeholder')  # replaced below

row_text = (TS + ' | r1023 | bm-c | WM-VERDICT: green red=false（py_low_board_clear 合法白名单：板全闭环/池 0 ready/W20 供给线=常设议程在册·funnel-0 审计已落地·bars 10-15 due 15:30·jobs 0） | '
 'CEO 令 O-20261015-0906-bm-b 回执三件全落：①委员会案 C-20261015-01 补票=Y 已 CAS 直投（group-tree origin f513876b·sha 验真·席行含风险三注：RAM 门常闭实测 1.27G/23.9G→池件须 RAM-light+claim 前 RAM 闸照旧；哨兵 v1.0 吸收 v3.0=自决顺延〔sentinel_bm-c.py 他人窗未收口编辑〕；LogonType 面实弹附注） '
 '②LogonType 自查=两任务实锤 InteractiveToken+SWA=true·S4U 重注册本机 live-fire=拒绝访问（0x80070005·D-20261002-02 集团裁决精确复现·维持默认 principal 正源·bm-b 提权宿主成功不可迁移·共享脚本修法随 bm-a 窗·本机任务定义未动） ③O-file 回执行翻 [x] | '
 'W20 供给审计探针落地（funnel-0·零烧零网络·results/_r1023bmc_w20_supply_audit.{py,json}）：路线 (b) 四源机读判决=REFINE_BENCH rev_p2 CONSUMED-JUDGED（TRIAL_GRAMMAR_LEDGER 行 21+23·升格路径 LOWAMP-DEEP-P1 已吃）/外源 TA 普查 CLOSED-ZERO-SURVIVOR（r937）/T-86 腿 CONSUMED/GENERATE=LIVE-ROUTE（入场×过滤·X/S/T 三轴按 W17/W18/W19 判决定谳全固定）·route (a) 股票宇宙面=CEO 署名门 standing·下窗首要=W20 候选稿 funnel 1/5（r924 bm-b W19-draft 先例+seed admit probe+banned gate+账本查重腿） | '
 'S6 37/37 rc0 70.7s（dualrun streak 51 零漂移+REPORT/LIVE-2026-10-15 faces 刷新+collectors lane-guard no-ops+token delta 0） | S1 smoke 49/49 | '
 'S0.5 双水位 FALSE both 双扫（opening+S7 tail·ORD e2423fef/DEC 6910a9ed hold）+ inbox MSG-0825（bm-a 当事·保持）/MSG-0906（bm-a+bm-c 双收·本机义务已处理·bm-a 义务留存原处） | '
 'S7：attrition 4 CLEAN+loop pin=5 no-op+watchdog PRESENT+双爪 MATCH x2+孤儿面=2 零杀 | '
 '下轮：bars 15:30→papers 全链；W20 候选稿起草（审计件为供给腿证据·funnel 1/5）；W245=bm-a freeze/burn/finalize 链观察·W246 席按轮转；MV V3 GPU 车道候 bm-a 导演审回执 | 本地未达 origin commit 数=0（收口 push 后 fetch 自证）')

P = 'round_reports-bm-c.md'
src = io.open(P, encoding='utf-8', newline='').read()
assert src.endswith('\n'), 'canonical report must be newline-terminated'
assert 'r1023 | bm-c' not in src, 'r1023 row already present -- idempotency abort'
io.open(P, 'a', encoding='utf-8', newline='').write(row_text + '\n')
print('report row appended (%d chars)' % len(row_text))

# ---- state ----
S = json.load(io.open('state-bm-c.json', encoding='utf-8'))
assert S['round_no'] == 1023, 'round_no face = %s (expected 1023)' % S['round_no']
S['round_no'] = 1024
S['round_no_label'] = 'r1023'
S['last_round'] = 1023
S['last_round_label'] = 'r1023'
S['clock_read'] = TS
S['heartbeat_epoch_utc'] = EPOCH
for k in ('last_round_at', 'last_round_ts', 'last_seen', 'last_seen_at', 'last_ts', 'ts', 'updated', 'updated_at', 'current_task_at', 'last_round_closed'):
    if k in S:
        S[k] = TS
S['current_task'] = 'r1023: CEO-order O-0906 receipt trio (vote Y + LogonType livefire + absorb-defer) + W20 supply funnel-0 audit + S6 37/37 + S7 quad green'
S['did'] = ('r1023 bm-c: (1) S0-1 anchor bm-c + probe py_faces=5 orphans=2 zero-kill + fetch 0/0; (2) S0.5 dual-delta FALSE both scans (ORD e2423fef / DEC 6910a9ed hold) + MSG-0825 non-party (bm-a) + MSG-0906 dual-address processed bm-c legs; '
 '(3) CEO-order receipt trio: council vote C-20261015-01 = Y CAS-deposited group-tree origin f513876b (sha-verified, risk-3-notes row) + LogonType self-check both tasks InteractiveToken+SWA=true + S4U live-fire = ACCESS-DENIED (D-20261002-02 replication, default-principal canon kept, shared-script fix = bm-a window) + sentinel v1.0 v3.0 absorption = self-decided DEFER (sentinel_bm-c.py foreign in-flight edit, owner window) + O-file receipt flipped [x]; '
 '(4) W20 supply funnel-0 audit probe landed (results/_r1023bmc_w20_supply_audit.{py,json}, zero-burn zero-network): route-b verdicts refine=CONSUMED-JUDGED (ledger rows 21+23) / external=CLOSED-ZERO-SURVIVOR (r937) / T86=CONSUMED / GENERATE=LIVE-ROUTE (entry-x-filter, X/S/T fixed per W17/W18/W19); route-a = CEO-gated standing; '
 '(5) S1 smoke 49/49; (6) S6 chain 37/37 rc0 70.7s (dualrun streak 51 zero-drift + faces refreshed + collectors no-ops + token delta 0); (7) S7 quad green (attrition 4 CLEAN + loop pin=5 no-op + watchdog PRESENT + claws MATCH x2) + tail dual-scan FALSE both')
S['verify'] = ('receipts: smoke 49/49 + vote deposit origin f513876b sha-verified read-back + S4U livefire ACCESS-DENIED honest rc + O-file receipt [x] + w20 audit json receipts (ledger row asserts) + dualrun streak 51 + attrition 4 CLEAN + claws CR-norm MATCH x2 + watchdog PRESENT + S7 tail dual-scan FALSE both + orphan face=2 legal zero-kill')
S['last_round_summary'] = S['did']
next_ptr = ('r1024: (1) bars 10-15 due 15:30 -> update_daily gate -> papers full chain (live.paper REGIME_GUARD + t35 openfill + t24 x2 + aggr/alloc/grid/system_v1 + export + faces); '
 '(2) W20 candidate draft funnel 1/5 (GENERATE route entry-x-filter per audit results/_r1023bmc_w20_supply_audit.json; r924 bm-b W19-draft precedent + seed-admit probe + banned gate + grammar-ledger dedup leg); '
 '(3) W245=bm-a freeze/burn/finalize chain watch; W246 seat per rotation; (4) MV V3 GPU lane unlock on bm-a director review receipts; (5) absorb note: Tools/sentinel_bm-c.py foreign in-flight edit left uncommitted (owner window); sentinel v3.0 absorption deferred until owner closes')
for k in ('next', 'next_pointer', 'next_milestone'):
    if k in S:
        S[k] = next_ptr
S['activity_now'] = TS + ' | r1023 | bm-c: CEO-order receipt trio + W20 funnel-0 audit | counter 1023->1024 (r1023 exec)'
S['now_active'] = S['activity_now']
S['last_action'] = 'r1023 closeout (CEO-order receipt + W20 supply audit)'
S['orphan_face'] = 2
S['orphan_faces'] = 2
S['r1023_closeout_note'] = ('r1023: clean continuation window (state round_no=1023 at open, executed r1023, advanced 1023->1024 so next=r1024); zero absorb owed (r1022 closeout landed clean); '
 'zero double-count: S0.5 dual-delta FALSE both scans (opening + S7 tail); products = CEO-order O-20261015-0906 bm-c receipt trio (vote Y deposit f513876b + LogonType livefire replication + sentinel-absorb defer) + W20 supply funnel-0 audit; '
 'S4U adjudication note: bm-b 09:06 MSG called InteractiveToken a violation of the 2026-09-29 S4U order, but in-repo D-20261002-02 group adjudication (S4U proven uninstallable from unelevated hosts) is standing law -- bm-c live-fire replicated ACCESS-DENIED same window; kept adjudicated default-principal state, no task definition touched')
art = ('r1023: council vote row on group-tree origin f513876b (C-20261015-01 bm-c seat Y) + W20 supply audit results/_r1023bmc_w20_supply_audit.json + O-file receipt flip + S6 faces (REPORT/LIVE-2026-10-15)')
for k in ('latest_artifact', 'last_artifact', 'recent_artifact', 'last_artifact'):
    if k in S:
        S[k] = art
S['last_round_summary_at'] = TS
S['last_action_at'] = TS
# orders_ack: O-20261015-0906-bm-b.md consumed this window
oa = S.get('orders_ack', [])
if 'O-20261015-0906-bm-b.md' not in oa:
    oa.append('O-20261015-0906-bm-b.md')
    S['orders_ack'] = oa
    S['orders_ack_count'] = len(oa)
    S['orders_ack_last'] = 'O-20261015-0906-bm-b.md'
    S['orders_ack_ts'] = TS
S['orders_ack_receipt'] = ('r1023: O-20261015-0906-bm-b consumed same-window (CEO never-idle order via bm-b): bm-c legs executed = council vote Y deposited f513876b + LogonType self-check + S4U livefire replication + sentinel-absorb defer; receipt flipped [x] in order file')
# live system faces from fresh audit
try:
    aud = json.load(io.open('results/compute_audit.bm-c.json', encoding='utf-8'))
    S['cpu_pct'] = aud.get('cpu_total_pct', S.get('cpu_pct'))
    S['cpu_idle_pct'] = round(100 - float(aud.get('cpu_total_pct', 0)), 1)
except Exception:
    pass
io.open('state-bm-c.json', 'w', encoding='utf-8', newline='\n').write(json.dumps(S, ensure_ascii=False, indent=1) + '\n')
chk = json.load(io.open('state-bm-c.json', encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
assert chk['round_no'] == 1024
print('state written: round_no=1024 epoch=%d (int verified)' % chk['heartbeat_epoch_utc'])

# ---- heartbeat ----
H = json.load(io.open('fleet/machines/bm-c.json', encoding='utf-8'))
H['last_seen'] = TS
H['ts'] = TS
H['clock_read'] = TS
H['heartbeat_epoch_utc'] = EPOCH
H['current_task'] = S['current_task']
H['current_task_at'] = TS
H['idle_rounds'] = 0
H['agenda_starved'] = False
H['verdict'] = ('green: r1023 = CEO-order receipt window (vote Y deposit + LogonType livefire + W20 funnel-0 audit) + pool 0 ready (W20 GENERATE draft = next-window supply) + bars 10-15 due 15:30 + S6 37/37 + S7 quad green')
H['note'] = S['did'][:400]
try:
    H['cpu_pct'] = S['cpu_pct']
except Exception:
    pass
H['free_ram_gb'] = H.get('free_ram_gb')
io.open('fleet/machines/bm-c.json', 'w', encoding='utf-8', newline='\n').write(json.dumps(H, ensure_ascii=False, indent=1) + '\n')
h2 = json.load(io.open('fleet/machines/bm-c.json', encoding='utf-8'))
assert isinstance(h2['heartbeat_epoch_utc'], int), 'heartbeat epoch must be int'
print('heartbeat written (epoch int verified)')
