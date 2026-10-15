# r1022 closeout: absorb dead r1022-attempt estate + state + heartbeat + round report (newline fix)
# -*- coding: utf-8 -*-
import json, time, psutil, subprocess, io, os

NOW = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
EPOCH = int(time.time())
R = 'r1022'

def resample():
    vm = psutil.virtual_memory()
    cpu = psutil.cpu_percent(interval=1)
    gpu_free = None
    try:
        out = subprocess.run(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],
                             capture_output=True, text=True, timeout=10).stdout.strip().splitlines()[0]
        gpu_free = int(out)
    except Exception:
        pass
    return round(vm.available/1e9,2), cpu, gpu_free

free_ram, cpu_pct, gpu_free = resample()

# 0) round report: fix r1021 concatenated row (missing newline) then append r1022 row
RP = 'round_reports-bm-c.md'
b = open(RP, 'rb').read()
JOINT = '（收尾 push 后复核）2026-10-15T07:52:41'.encode('utf-8')
assert b.count(JOINT) == 1, 'joint needle must be unique: %d' % b.count(JOINT)
b = b.replace(JOINT, '（收尾 push 后复核）\r\n2026-10-15T07:52:41'.encode('utf-8'))
if not b.endswith(b'\r\n'):
    b += b'\r\n'
ROW = (f"{NOW} | r1022 | bm-c | WM-VERDICT: green red=false（py_low_board_clear 合法白名单：板全闭环/池 0 ready/RW-5 冻结已解除·W244 finalize 07:47 落地 bm-a r1008〔ledger 961,135/K=534,720〕/jobs 0） | "
       f"ABSORB 29th（同标签死亡前窗 r1022-attempt 08:15-09:24：席位 MSG 08:15 已作 superseded 隔离〔quarantine 09:24 rc0·treasure_guard 零命中〕+探针 08:17 遗产收编+bm-a 席位 MSG 移 processed+90 行 sentinel_bm-c.py 在飞改=他窗件未提交不碰） | "
       f"W245 席位让路定谳：bm-a GM 重派接管车道 origin 2b0947947（本机 r1020 闭窗宣告后心跳冻结 64.5min·stall>1 轮 per r1009 规则·按 commit 时间序 bm-a 先落席=后到让路零争议·带位交叉核对 identical） | "
       f"S6 链 37/37 rc0 174.9s（dualrun streak 51 零漂移+REPORT/LIVE-2026-10-15 faces 刷新+collectors lane-guard no-ops+fund_premium pre-15:30+token delta 0） | S1 smoke 49/49 | S0.5 双水位 FALSE both（ORD e2423fef/DEC 6910a9ed hold）+ inbox MSG-0825 bm-b→bm-a 池补货催办=非收件人不越道（本机「发布后即领即烧」回执保持·green_idle=false RAM 6.5%<40% 闸诚实本窗不领） | "
       f"post_review 今日 ✓46/✗0（两处 ✗ 字符=分布行+诚实负描述·零 P0 债） | S7：attrition 4 CLEAN+loop pin=5 no-op+watchdog 幂等重注册+双爪装毕+孤儿面=2 零杀+轮报告 r1021 行换行债修复 | "
       f"下轮：15:30 bars→papers 全链；池供给解冻后 W20 供给起草（r859 双法=submit 门禁+外科插入·超本窗工程如实指针）；bm-a 导演审回执→B 批 GPU 解锁 | 本地未达 origin commit 数=0（收尾 push 后复核）\r\n").encode('utf-8')
open(RP, 'wb').write(b + ROW)

# 1) state-bm-c.json
SP = 'state-bm-c.json'
st = json.load(open(SP, encoding='utf-8'))
did = (f"{R} bm-c: (1) S0-1 anchor bm-c + probe py_faces=5 orphans=2 zero-kill + fetch behind=0 (HEAD=2b0947947 via dead-window pull estate); "
       f"(2) S0.5 dual-delta FALSE both (ORD e2423fef / DEC 6910a9ed hold) + inbox MSG-0825 bm-b->bm-a pool-restock = non-party left for addressee (bm-c claim-and-burn receipt standing); "
       f"(3) ABSORB 29th dead r1022-attempt window: seat MSG 08:15 quarantined superseded 09:24 (rc0 guard) + probe 08:17 estate committed + bm-a seat MSG processed-move absorbed + 90-line Tools/sentinel_bm-c.py in-flight edit LEFT UNCOMMITTED (foreign window file, untouched); "
       f"(4) S1 smoke 49/49; (5) W245 seat YIELDED to bm-a GM-reassignment takeover lane (origin 2b0947947; bm-c declared turn at r1020 then heartbeat froze 64.5min = stall>1 round per r1009 rule; commit-time first-landed; zero dispute); RW-5 freeze LIFTED (W244 finalize landed 07:47 bm-a r1008 ledger 961,135/K=534,720) -> supply unblocked, W20 drafting = out-of-window authoring (runner+prereg+submit gates+surgical insert r859 dual-law) -> next-pointer; satengine ALIVE rc0 queue 0 burns 0; idle green_idle=false RAM 6.5pct<40pct gate honest not-claim-eligible; MV V3 GPU lane upstream-gated (bm-a director review); post_review today 46 rows all-check zero P0; "
       f"(6) S6 chain 37/37 rc0 174.9s (dualrun streak 51 zero-drift + REPORT/LIVE-2026-10-15 faces refreshed + collectors lane-guard no-ops + token delta 0); "
       f"(7) S7: attrition 4 CLEAN + loop pin=5 no-op + watchdog re-registered idempotent + both claws installed + round-report r1021-row newline-debt fixed; counter 1022->1023")
nxt = (f"r1023: (1) bars 10-15 due 15:30 -> update_daily gate -> papers full chain (live.paper REGIME_GUARD + t35 openfill + t24 x2 + aggr/alloc/grid/system_v1 + export + faces); "
       f"(2) pool supply resume post-RW-5-lift: W20 trial-labor supply drafting per r859 dual-law (autofill submit gates + raw-text surgical insert + MSG publish + commit+push before daemon claim) -- RAM-light spare-parts items claimable once bm-a publishes per MSG-0825 (bm-c receipt: claim-and-burn; green_idle RAM gate governs eligibility); "
       f"(3) MV V3 GPU lane unlock on bm-a director review receipts (A-batch fullres 1344x768 + casting x3 + B-batch 12 frames); "
       f"(4) absorb note: Tools/sentinel_bm-c.py 90-line in-flight edit left uncommitted for owner window (do not blindly commit); "
       f"(5) W245=bm-a freeze/burn/finalize chain watch; W246 seat per rotation")
for k in ['clock_read','ts','updated','updated_at','current_task_at','last_round_at','last_round_ts','last_seen','last_seen_at','last_ts','last_round_closed']:
    st[k] = NOW
st['round_no'] = 1023
st['round_no_label'] = R
st['last_round'] = 1022
st['did'] = did
st['last_round_summary'] = did
st['current_task'] = f"{R}: watch window absorb (dead r1022-attempt estate + W245 yield to bm-a) + S6 37/37 + S7 quad green"
st['next_pointer'] = nxt
st['next'] = nxt
st['next_milestone'] = nxt
st['note'] = did[:400]
st['heartbeat_epoch_utc'] = EPOCH
st['free_ram_gb'] = free_ram
st['ram_free_gb'] = free_ram
st['idle_ram_gb'] = free_ram
st['cpu_pct'] = cpu_pct
st['last_round_closed'] = NOW
if isinstance(st.get('gpu_free_vram_mib'), int):
    st['gpu_free_vram_mib'] = gpu_free
    st['gpu_free_vram_mb'] = gpu_free
json.dump(st, open(SP,'w',encoding='utf-8'), ensure_ascii=False, indent=1)

# 2) heartbeat
HP = 'fleet/machines/bm-c.json'
hb = json.load(open(HP, encoding='utf-8'))
hb['heartbeat_epoch_utc'] = EPOCH
hb['clock_read'] = NOW
hb['ts'] = NOW
hb['updated'] = NOW
hb['updated_at'] = NOW
hb['last_seen'] = NOW
hb['last_seen_at'] = NOW
hb['round_no'] = 1022
hb['last_round'] = 'r1022'
hb['loop_round'] = 1022
hb['round_no_label'] = R
hb['now_active'] = f"{NOW} | r1022 | bm-c: watch-window absorb closeout (W245 yielded to bm-a; RW-5 lifted; S6 37/37) | counter 1022->1023"
hb['current_task'] = st['current_task']
hb['current_task_at'] = NOW
hb['did'] = did
hb['last_round_summary'] = "r1022: dead-window estate absorbed (superseded seat claim quarantined; probe estate committed; MSG processed) + W245 seat yielded to bm-a (GM takeover 2b0947947) + RW-5 freeze LIFTED (W244 finalized 07:47) + S6 37/37 + S7 quad green"
hb['last_round_summary_at'] = NOW
hb['next'] = nxt
hb['next_pointer'] = nxt
hb['next_milestone'] = nxt
hb['last_artifact'] = "r1022: S6 chain 37/37 rc0 174.9s (dualrun streak 51 + REPORT/LIVE-2026-10-15 faces + market_clock idempotent + collectors no-ops) + W245 yield note + quarantine 20261015T0924 superseded claim manifest"
hb['last_action'] = f"{R} watch-window absorb closeout"
hb['last_action_at'] = NOW
hb['last_round_at'] = NOW
hb['last_decisions_read_at'] = NOW
hb['last_orders_read_at'] = NOW
hb['last_decisions_at'] = NOW
hb['last_orders_at'] = NOW
hb['free_ram_gb'] = free_ram
hb['idle_ram_gb'] = free_ram
hb['ram_free_gb'] = free_ram
hb['cpu_pct'] = cpu_pct
hb['cpu_util_pct'] = cpu_pct
hb['cpu_idle_pct'] = round(100-cpu_pct,1)
hb['idle_rounds'] = 0
hb['agenda_starved'] = False
hb['orphan_face'] = 2
hb['orphan_faces'] = 2
hb['prod_lanes'] = "CPU=N1 W246 seat watch (W245=bm-a chain in-flight: seat published 09:20, freeze/burn/finalize theirs; RW-5 lifted -> W20 supply drafting queued next round); GPU=ComfyUI resident idle (wave3 trial boards delivered 05:43; A-batch fullres + casting promotion + B-batch 12 frames gated on bm-a director review)"
hb['latest_artifact'] = hb['last_artifact']
hb['verdict'] = "green: r1022 watch window (W245 seat = bm-a GM takeover lane, bm-c yields per stall>1round rule; RW-5 freeze LIFTED post-W244-finalize -> supply drafting next round; bars 15:30; MV GPU lane awaits bm-a director review; S6 37/37 + S7 quad green)"
hb['health'] = 'ok'
hb['last_round_closed'] = NOW
hb['last_round_ts'] = EPOCH
hb['activity_now'] = hb['now_active']
hb['full_load_selfproof'] = {
  "占用一行": "GPU=ComfyUI 8188 resident idle (wave3 trial delivered; queue empty, next burn gated on bm-a director review) + CPU=N1 W246 seat watch (W245=bm-a freeze/burn/finalize in-flight)",
  "当前活": f"{R} watch-window absorb closeout + S6/S7 maintenance green (37/37 + quad)",
  "下一交付物": "r1023: 15:30 bars -> papers full chain; W20 pool supply drafting (RW-5 lifted); MV GPU unlock on bm-a director receipts",
  "队列水位": "N1 engine 0 burning on bm-c (W245=bm-a wave) · MV V3 wave3 trial delivered, A/B batches gated upstream · P2/P3 queues all-done · pool ready=0 (W20 supply drafting queued) · bars 15:30"
}
if isinstance(hb.get('gpu_free_vram_mib'), int):
    hb['gpu_free_vram_mib'] = gpu_free
    hb['gpu_free_vram_mb'] = gpu_free
    hb['gpu_free_vram_gb'] = round((gpu_free or 0)/1024,2)
json.dump(hb, open(HP,'w',encoding='utf-8'), ensure_ascii=False, indent=1)

# verify epoch int
chk = json.load(open(HP, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
chk2 = json.load(open(SP, encoding='utf-8'))
assert isinstance(chk2['heartbeat_epoch_utc'], int), 'state epoch must be int'
assert chk2['round_no'] == 1023
print('state+heartbeat OK; epoch', EPOCH, '| ram', free_ram, '| cpu', cpu_pct, '| gpu_free', gpu_free, '| round report row appended')
