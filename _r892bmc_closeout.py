# r892 closeout: O-2215 oversight-face receipt + state + heartbeat + round report
# -*- coding: utf-8 -*-
import json, time, psutil, os, subprocess

NOW = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
EPOCH = int(time.time())
R = 'r892'

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

# 1) receipt into O-20261011-2215-bm-c.md (bm-c oversight-face section)
rec_2215 = f"""

## §五 bm-c 巡查面回执（r892·2026-10-11 22:2x）
- 机制验活：FluxGroup-FleetOversight schtasks 正门在役（hourly·Last Result=0·下轮 22:36:33）——豁免撤除已确认落盘（fleet/oversight/exemptions.json BigLife 行删除实测 2026-10-11 22:1x）→ 22:36 起巡查器实读 BigLife 仓 24h/48h 提交（当前 c24=0/c48=0=复工前如实 RED 上板，豁免面不再遮蔽）。
- 翻绿确认（24h 窗）：**值守中**——窗口至 2026-10-12 22:15；bm-a 解冻点火（首轮回执 ≤12h）+年轮线批落 commit 即翻绿；巡查器 hourly 自读，值守轮按窗核验后回本节勾选销账。
- 本机其他面：BigLife 生产五线/云端配额=§@bm-a 义务面（非本机）；bm-c MV GPU 车道持续满载（专辑 i2v XQ 24 单在烧·2/25 落·CEO 优先令 O-2126）。
"""
with open('fleet/orders/O-20261011-2215-bm-c.md', 'a', encoding='utf-8', newline='') as fh:
    fh.write(rec_2215)

# 2) state-bm-c.json
SP = 'state-bm-c.json'
st = json.load(open(SP, encoding='utf-8'))
did = (f"{R} bm-c: (1) S0-1 anchor bm-c + round-zero probe py_faces=7 orphans=2 zero-kill "
       f"(both MV-lane infra KEPT: c1011_album_serve.pyw :8800 idle HTTP frame-distributor + PID54748 "
       f"burn client in poll phase CPU-0 normal while ComfyUI server PID2308 actively renders); "
       f"(2) S0 behind=1 incoming e44a59e12 = O-20261011-2215 BigLife naming order (via bm-c "
       f"interactive) -> autostash rebase CLEAN 0/0, order consumed via origin blob + local file; "
       f"(3) S0.5 orders delta TRUE -> consumed: docs/orders.md new row = BigLife 点名复工令 "
       f"(non-BigMoney lane -> zero repo action) + fleet order O-2215 §@bm-c oversight face processed: "
       f"FluxGroup-FleetOversight hourly alive rc0 (next 22:36), exemptions.json BigLife row REMOVED "
       f"confirmed on disk -> post-removal inspector reads BigLife c24/c48 live = honest RED until "
       f"bm-a ignition; bm-c duty = 24h 翻绿确认 watch (window to 10-12 22:15, receipt appended, "
       f"checkbox open by design); watermark ADVANCED ord 075caa8d (dec unchanged eb14c441, read-back OK); "
       f"(4) MV lane O-2126: 2/25 done (V2_KFL 510.6s + XQ_XQ28 2138.4s/277f at 22:14:34), fails-bmc.txt "
       f"absent = zero fails, unit 3 in-flight -- harvest NOT due, no re-scan beyond progress read; "
       f"(5) W211 chain: cron 847675d7 durable alive + M11 armed, await W210 (bm-b) finalize -- no "
       f"re-scan; (6) S1 smoke 49/49; S2 boards CLEAR (jobs 0, fleet open 0; P2 tech all done; P3 head "
       f"E17 = bm-b declared lane, yielded); satengine alive rc0 front=209 queue=0; idle_trigger "
       f"green_idle=false (RAM 0.2GB gate ON + vram held by MV burn -> heavy CPU batches legally "
       f"gated, py_low_with_work_cands legal whitelist = local_batch MV i2v in-flight + board closed "
       f"+ pool upstream-gated); (7) S6 FULL 38/38 rc0 + 7 disclosed skips (r889 38-leg chain restored "
       f"vs r890/r891 30-leg reduced set: paper legs + daily_scorecard + build_status + "
       f"queue_seed_gate_scan all rc0 idempotent; dualrun zero-drift streak 7; compute_audit flags "
       f"pool_starvation+supply_floor = upstream-gated supply chain W210->W211 + RAM gate, disclosed "
       f"not faulted); (8) S7: attrition 4 ledgers CLEAN, loop pin=5 no-op, watchdog re-registered, "
       f"precommit+prepush claws re-installed; heartbeat epoch int verified")
nxt = (f"r893: (1) MV XQ-24 completion harvest watch (2/25 progressing, harvest at 25/25 + receipt "
       f"into O-2126) -> next i2v wave per assignment; (2) W210 (bm-b) finalize watch -> M11/cron "
       f"auto-exec W211 freeze -> n1_w211 burn -> finalize -> W212 seat; (3) BigLife 翻绿确认 24h "
       f"watch (window to 10-12 22:15, oversight hourly live-read); (4) 10-13/14 P0 matrix v1 "
       f"assembly window (16 rows/15 wired, six-member fwd-accum honest hold)")
for k in ['clock_read','ts','updated','updated_at','current_task_at','last_round_at','last_round_ts','last_seen','last_seen_at','last_ts']:
    st[k] = NOW
st['round_no'] = 892
st['round_no_label'] = R
st['last_round'] = 892
st['did'] = did
st['last_round_summary'] = did
st['current_task'] = f"{R}: O-2215 oversight-face receipt + MV lane watch + S6 38/38 + watermark advance + closeout"
st['next_pointer'] = nxt
st['next'] = nxt
st['next_milestone'] = nxt
st['note'] = did[:400]
st['heartbeat_epoch_utc'] = EPOCH
st['free_ram_gb'] = free_ram
st['ram_free_gb'] = free_ram
st['idle_ram_gb'] = free_ram
st['cpu_pct'] = cpu_pct
st['last_decisions_read_at'] = NOW
st['last_orders_read_at'] = NOW
st['last_orders_sha'] = '075caa8d977e5baf6248548ce9b6f4ce06c8d030'
st['last_orders_at'] = NOW
st['last_decisions_sha'] = 'eb14c441ba0131e26e3c3b2fafc17900747152dd463a654beacffdce65ef5d73'
st['last_round_closed'] = NOW
st['orphan_face'] = 2
st['orphan_faces'] = 2
st['now_active'] = f"{R}: MV album i2v burn in-flight GPU lane (2/25 done, unit3 rendering) + BigLife oversight 24h watch + W211 armed behind W210"
st['last_artifact'] = 'K:/Fluxgroup/FluxGroup/media/mv-album-001-jay/clips-local-768/XQ_XQ28.mp4 (2026-10-11 22:14:34, 768P int8 277-frame XQ28 clip, unit 2/25) + results/_r892bmc_s6_log.txt 38/38'
st['recent_artifact'] = st['last_artifact']
st['latest_artifact'] = st['last_artifact']
st['verdict'] = ('green: order-receipt + watch round -- O-2215 oversight face verified alive with BigLife '
                 'exemption removal consumed next hourly run; MV i2v 2/25 progressing zero fails; W211 '
                 'armed behind W210 upstream; RAM gate + board clear = legal watch state')
if isinstance(st.get('gpu_free_vram_mib'), int):
    st['gpu_free_vram_mib'] = gpu_free
    st['gpu_free_vram_mb'] = gpu_free
json.dump(st, open(SP,'w',encoding='utf-8'), ensure_ascii=False, indent=1)

# 3) heartbeat
HP = 'fleet/machines/bm-c.json'
hb = json.load(open(HP, encoding='utf-8'))
acks = hb.get('orders_ack') or []
for o in ['O-20261011-2215-bm-c.md']:
    if o not in acks:
        acks.append(o)
hb['orders_ack'] = acks
hb['orders_ack_count'] = len(acks)
hb['orders_ack_last'] = 'O-20261011-2215-bm-c.md'
hb['orders_ack_receipt'] = (f"{R}: O-2215 BigLife naming order §@bm-c oversight face verified (hourly task "
                            f"alive rc0, exemptions.json BigLife row removed on disk, inspector reads c24/c48 "
                            f"live from 22:36 run; 24h turn-green confirm watch to 10-12 22:15)")
hb['heartbeat_epoch_utc'] = EPOCH
hb['clock_read'] = NOW
hb['ts'] = NOW
hb['updated'] = NOW
hb['updated_at'] = NOW
hb['last_seen'] = NOW
hb['last_seen_at'] = NOW
hb['last_round_closed'] = NOW
hb['round_no'] = 892
hb['last_round'] = 892
hb['loop_round'] = 892
hb['round_no_label'] = R
hb['now_active'] = st['now_active']
hb['current_task'] = st['current_task']
hb['current_task_at'] = NOW
hb['did'] = did
hb['last_round_summary'] = did
hb['last_round_summary_at'] = NOW
hb['next'] = nxt
hb['next_pointer'] = nxt
hb['next_milestone'] = nxt
hb['last_artifact'] = st['last_artifact']
hb['recent_artifact'] = st['last_artifact']
hb['latest_artifact'] = st['last_artifact']
hb['last_action'] = f"{R} O-2215 oversight receipt + S6 38/38 + watermark advance"
hb['last_action_at'] = NOW
hb['last_decisions_sha'] = st['last_decisions_sha']
hb['last_orders_sha'] = st['last_orders_sha']
hb['last_decisions_read_at'] = NOW
hb['last_orders_read_at'] = NOW
hb['last_decisions_at'] = NOW
hb['free_ram_gb'] = free_ram
hb['idle_ram_gb'] = free_ram
hb['ram_free_gb'] = free_ram
hb['cpu_pct'] = cpu_pct
hb['cpu_util_pct'] = cpu_pct
hb['cpu_idle_pct'] = round(100-cpu_pct,1)
hb['idle_rounds'] = 0
hb['agenda_starved'] = False
hb['orphan_face'] = 'orphans=2 (both MV-lane infra KEPT: :8800 idle HTTP frame-distributor + PID54748 burn client poll-phase, ComfyUI server rendering unit3)'
hb['orphan_faces'] = 2
hb['prod_lanes'] = 'GPU=MV album i2v XQ 24+V2_KFL (O-2126; 2/25 done, unit3 in-flight, 8.5-35min/unit); CPU=W211 armed behind W210 (bm-b) + RAM gate 0.2GB on heavy batches'
hb['verdict'] = st['verdict']
hb['health'] = 'ok'
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

# 4) round report line
RP = 'logs/iteration-loop/round_reports-bm-c.md'
summary = (f"bm-c: order-receipt + watch round -- O-2215 BigLife naming order §@bm-c processed "
           f"(oversight face verified alive: hourly task rc0 next-22:36, exemptions.json BigLife row "
           f"REMOVED on disk -> inspector reads c24/c48 live from 22:36, honest RED until bm-a ignition; "
           f"24h turn-green watch to 10-12 22:15, receipt appended, checkbox open by design; §@bm-a "
           f"production = not this machine); D-19 orders delta consumed (BigLife row non-BigMoney, "
           f"zero repo action), watermark ADVANCED ord 075caa8d read-back OK; MV i2v lane 2/25 done "
           f"(XQ_XQ28 2138.4s at 22:14:34, zero fails, unit3 in-flight, harvest not due); W211 armed "
           f"behind W210 (bm-b, cron 847675d7 alive, no re-scan); S6 FULL chain 38/38 rc0 + 7 disclosed "
           f"skips (r889 38-leg precedent restored: paper legs + daily_scorecard + build_status + "
           f"queue_seed_gate all rc0; dualrun streak 7; pool_starvation flags = upstream-gated supply "
           f"+ RAM gate disclosed); S1 smoke 49/49; boards clear (P2 all done, P3 head E17=bm-b yielded); "
           f"orphans=2 (both MV-lane infra kept)")
evidence = ("smoke 49/49 + S6 log _r892bmc_s6_log.txt ok=38 bad=0 + watermark advance read-back OK "
            "(ord 075caa8d) + attrition 4 CLEAN + MV progress-bmc.jsonl 2/25 zero-fails + loop pin=5 no-op")
line = f"{NOW} | r892 | {summary} | {evidence} | {nxt}\n"
with open(RP, 'a', encoding='utf-8', newline='') as fh:
    fh.write(line)

print('receipts+state+heartbeat+roundreport OK; epoch', EPOCH, '| ram', free_ram, '| cpu', cpu_pct, '| gpu_free', gpu_free)
