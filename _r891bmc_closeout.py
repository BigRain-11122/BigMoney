# r891 closeout: receipts + state + heartbeat + round report
# -*- coding: utf-8 -*-
import json, time, psutil, os, subprocess

NOW = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
EPOCH = int(time.time())
R = 'r891'

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

# 1) receipts into the two orders
rec_2126 = f"""

## §5 回执（bm-c r891·2026-10-11 22:0x）
- 受理回执：✅ 本机线已开工（21:30:25 点火·PID 54748 pythonw h3_i2v_album.py --lane bmc·int8 四件权重 r880 装机验讫在册）；:8800 帧分发常驻活（HTTP 200）。
- 首条实测时长：V2_KFL 插队单 510.6s / 124 帧（21:38:56 落盘·progress-bmc.jsonl）→ XQ 24 单 ETA ≈ 3.4h（午夜前后全落）。
- 完成回执：XQ 24 单烧制中（GPU 单车道·ComfyUI 8188 在役）；完成件后续轮收口回执。
"""
rec_2147 = f"""

## 四、回执节（bm-c tick 窗·r891·2026-10-11 22:0x）
- [x] tick 窗：W210 波链供给恢复**核实已在位**（前窗 r887/r888 已完成注册全链）：W210 席位 declared bm-b 车道（origin 0a60b8850）·W211 pre-seat 探针 5 腿（r849 03:50 receipt）+freeze-prep bundle e8a2f4638+prereg e8a2f4638·W212 探针（r859 07:33）已备；**M11 行 armed**（state/queue/main.md L17·守望 W209+W210 五面+finalize 落链即窗执行 W211 freeze 链）+backup watch cron 847675d7 durable 活（4-59/17 每小时三分·durable 会话无关）——供给恢复已机制化，等 W210（bm-b）finalize 落链自动接力；点火验证=上游依赖窗内完成（M 链 armed 消费即验）。后续波供给一律 M 行 armed：✅ 已在位（M11+W212 探针段= c1010 续链模板实证）。
- [ ] bm-a / bm-b 段=各机回执（非本机义务）。
"""
for f, rec in [('fleet/orders/O-20261011-2126-bm-c.md', rec_2126),
               ('fleet/orders/O-20261011-2147-bm-c.md', rec_2147)]:
    with open(f, 'a', encoding='utf-8', newline='') as fh:
        fh.write(rec)

# 2) state-bm-c.json
SP = 'state-bm-c.json'
st = json.load(open(SP, encoding='utf-8'))
did = (f"{R} bm-c: (1) S0-1 anchor bm-c + round-zero probe py_faces=8 orphans=1 zero-kill "
       f"(the 1 orphan = c1011_album_serve.pyw :8800 frame-distributor, idle HTTP server CPU-0 normal, "
       f"probe-200 alive, MV-lane infra KEPT); S0 pull refused (daemon-churn live faces, r889 autostash "
       f"exception family) -> fetch verify behind=0 ahead=2 (r890 P0-matrix commit + fleet oversight-order "
       f"pending push -> merged into this round push); (2) S0.5 dual watermark delta TRUE both -> consumed: "
       f"D-20261011-05/06/07/08 four new rows (bm-c three-piece dispatch of C-01 = already executed prior "
       f"window: album KF 53/53 QC + V2 lane + hotscan schtasks; oversight executor deployed first-run rc0 "
       f"per D-08 -> zero new bm-c action) + 2 unacked orders acked (O-20261011-2126 album i2v local lane "
       f"verify: PID54748 XQ-24 burn in-flight, V2_KFL 510.6s first-unit measured, :8800 alive; "
       f"O-20261011-2147 sec.tick W210 supply: verified ALREADY mechanized by r887/r888 - seat bm-b lane, "
       f"W211 probe+freeze-prep+prereg landed, M11 row armed + backup cron 847675d7 durable alive; await "
       f"upstream finalize, no re-scan); (3) S1 smoke 49/49; S2 boards CLEAR (jobs 0; inbox MSG-0940 "
       f"addressed bm-a = non-party left for addressee); satengine alive rc0 queue_next=[] burns_active=[] "
       f"(GPU lane = MV i2v per O-2126; CPU wave supply = W210 upstream bm-b, M11 watch armed); "
       f"(4) S6 30/30 rc0 (dualrun zero-drift streak 6, compute_audit CLEAN, py_watermark rc0, Sunday "
       f"no-new-bar honest skips); (5) S7: D-19 dual watermark ADVANCED both (read-back equality OK), "
       f"attrition 4 ledgers CLEAN, loop pin=5 no-op, watchdog re-registered, precommit+prepush claws "
       f"re-installed; heartbeat epoch int verified")
nxt = (f"r892: (1) MV XQ-24 completion harvest (progress-bmc.jsonl 25/25 + fails-bmc.txt empty check + "
       f"completion receipt into O-2126) -> next i2v wave per assignment; (2) W210 (bm-b) finalize landing "
       f"watch -> M11/cron auto-exec W211 freeze -> n1_w211 burn -> finalize -> W212 seat (c1010 template); "
       f"(3) 10-13/14 P0 matrix v1 assembly window (16 rows/15 wired, six-member fwd-accum honest hold)")
for k in ['clock_read','ts','updated','updated_at','current_task_at','last_round_at','last_round_ts','last_seen','last_seen_at','last_ts']:
    st[k] = NOW
st['round_no'] = 891
st['round_no_label'] = R
st['last_round'] = 891
st['did'] = did
st['last_round_summary'] = did
st['current_task'] = f"{R}: orders receipts (album i2v lane + W210 supply watch) + S6 30/30 + watermark advance + closeout"
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
st['last_orders_sha'] = 'dda237eaa61e5038f783cef5dcac034b74921d20'
st['last_decisions_sha'] = 'eb14c441ba0131e26e3c3b2fafc17900747152dd463a654beacffdce65ef5d73'
st['last_round_closed'] = NOW
if isinstance(st.get('gpu_free_vram_mib'), int):
    st['gpu_free_vram_mib'] = gpu_free
    st['gpu_free_vram_mb'] = gpu_free
json.dump(st, open(SP,'w',encoding='utf-8'), ensure_ascii=False, indent=1)

# 3) heartbeat
HP = 'fleet/machines/bm-c.json'
hb = json.load(open(HP, encoding='utf-8'))
acks = hb.get('orders_ack') or []
for o in ['O-20261011-2126-bm-c.md','O-20261011-2147-bm-c.md']:
    if o not in acks:
        acks.append(o)
hb['orders_ack'] = acks
hb['orders_ack_count'] = len(acks)
hb['orders_ack_last'] = 'O-20261011-2147-bm-c.md'
hb['orders_ack_receipt'] = f"{R}: O-2126 album i2v lane verified in-flight (XQ-24 burn, V2_KFL 510.6s first unit, :8800 alive) + O-2147 sec.tick W210 supply verified already-mechanized (M11 armed + cron 847675d7, await bm-b finalize)"
hb['heartbeat_epoch_utc'] = EPOCH
hb['clock_read'] = NOW
hb['ts'] = NOW
hb['updated'] = NOW
hb['updated_at'] = NOW
hb['last_seen'] = NOW
hb['last_seen_at'] = NOW
hb['round_no'] = 891
hb['last_round'] = 891
hb['loop_round'] = 891
hb['round_no_label'] = R
hb['now_active'] = f"{R}: XQ-24 album i2v burn in-flight (GPU lane) + W210 upstream watch (CPU lane, M11 armed)"
hb['current_task'] = st['current_task']
hb['current_task_at'] = NOW
hb['did'] = did
hb['last_round_summary'] = did
hb['last_round_summary_at'] = NOW
hb['next'] = nxt
hb['next_pointer'] = nxt
hb['next_milestone'] = nxt
hb['last_artifact'] = 'r890 P0-MATRIX-v1 early assembly 16 rows/15 wired (c8ffdee7c 21:47) + V2_KFL i2v clip 21:38'
hb['last_action'] = f"{R} orders receipts + watermark advance + S6 30/30"
hb['last_action_at'] = NOW
hb['last_decisions_sha'] = st['last_decisions_sha']
hb['last_orders_sha'] = st['last_orders_sha']
hb['last_decisions_read_at'] = NOW
hb['last_orders_read_at'] = NOW
hb['free_ram_gb'] = free_ram
hb['idle_ram_gb'] = free_ram
hb['ram_free_gb'] = free_ram
hb['cpu_pct'] = cpu_pct
hb['cpu_util_pct'] = cpu_pct
hb['cpu_idle_pct'] = round(100-cpu_pct,1)
hb['idle_rounds'] = 0
hb['agenda_starved'] = False
hb['orphan_face'] = 'orphans=1 (c1011_album_serve.pyw :8800 frame-distributor idle HTTP, alive 200, kept)'
hb['orphan_faces'] = 1
hb['prod_lanes'] = 'GPU=MV album i2v XQ-24 (O-2126); CPU=wave supply W210 upstream watch (M11 armed); burn=MV clips 510.6s/unit'
hb['verdict'] = f"green: orders-receipt round -- album i2v XQ-24 burn in-flight (first unit 510.6s measured, ETA ~3.4h) + W210 supply chain verified mechanized (M11 armed + backup cron); ahead=2 merged push this round"
hb['health'] = 'ok'
hb['last_round_closed'] = NOW
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
print('receipts+state+heartbeat OK; epoch', EPOCH, '| ram', free_ram, '| cpu', cpu_pct, '| gpu_free', gpu_free)
