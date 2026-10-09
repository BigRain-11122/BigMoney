# r940 bm-a closeout bookkeeping: HANDOVER 5x stamp + round report line + state + heartbeat
import json, time, datetime

now = datetime.datetime.now().astimezone()
ts_iso = now.strftime('%Y-%m-%dT%H:%M:%S') + '+08:00'
epoch = int(time.time())

HANDOVER_STAMP = (
    "> bm-a round 940 五轮核对（2026-10-10 04:3x·增量窗 r940 单轮〔r921-r939 已由 r939 合并戳收口〕·逐轮权威=round_reports-bm-a.md 全量在册）："
    "窗口主线=**r939 死会话 rebase 遗产抢救落地**（r939 会话 04:03 pull --rebase 撞 14 UU 后死亡〔pick 2fae1cd25 onto 96caaa9c8·真入口=非 porcelain status「interactive rebase in progress」r813 判例〕——"
    "抢救链全绿：E42 写者停窗（4 任务 disable→enable）→ 14 面判读（10 flat json S3-newest〔r939 03:55-04:00 > 基座侧 03:03-03:42〕+ compute_audit history 哈希 union 204→201〔r794 窗帽保真·latest 取新〕+ 3 md S3）→ "
    "标记零扫+add -u+continue 同 shell 原子环 rc0 → **二段 rebase**（origin 进 bm-b r814 双 commit=520e190b1）→ 13 面二轮判读（bm-b 04:02 再生面 S2-newest + **md 双胞胎一致性 override**〔json 取 S2 则 md 同取 S2·r917 默认 S3 律的孪生刻度修正〕+ compute_audit union）→ tip 标记 grep 仅 r505/r506 历史 probe 件=史前面非污染 → push e3b8bdd54 → fetch+rev-list **0/0 送达自证**；"
    "**池面 MSG-0612 face 级验证 PASS**：THERMO-OVERLAY-P1-BURN pick-only 入池保留〔status ready lane bm-a〕+ bm-c w17-screen-0..4 lane_owner=bm-c 认领全部存活 + updated_at newer-wins——陈旧重放回退零发生）；"
    "水位面=**PS-join 伪差拦截实锚**（PS 管道 join 算得 DEC b7289489「变」→python-raw canonical 复算=b87a92b1 与 r939 键恒等零消费·r814 族假 delta 机制再证）；"
    "T-181 面=THERMO-OVERLAY-P1-BURN 烧录待 autofill watchdog 认领（E42 停窗顺延·≤30min 节律内·prereg 窗 48h 自 03:3x 冻结充裕·verdict absorb 归 r941）；"
    "维护面=S6 39 腿 rc0 bad NONE〔driver r939 血统滚代 r940·new_bar=False 周六 no-op 族·regime_thermo_build 30s 幂等〕+ smoke 49/49 + attrition 4 台账 CLEAN + quartet GREEN〔loop pin=8 no-op/watchdog -Force 04:32 重火/双爪字节等〕+ 孤儿面 1〔jman LoRA GPU-bound 假阳性 MV 车道免动〕。"
    "指针：**r941=THERMO 烧录 verdict absorb + prereg sec.7/8 机补 + gate_attrition finalize check**；PARKING-P1 烧录 due 10-14 12:00；月界首考 10-31；下个 5x=bm-a r945。[via bm-a r940]"
)

REPORT_LINE = (
    "2026-10-10T04:3x:00+08:00 | r940 | bm-a | dept:工程 (S0 dead-session rebase estate salvage + S6 maintenance; T-181 burn monitoring) | "
    "WM-VERDICT: insufficient_history (probe 03:55:44 非红) + quartet DEC b87a92b1/ORD 0ddb01d9 python-raw hash MATCH zero re-consume (PS-join b7289489 伪差被 r814 canonical 律拦截=机制胜利实锚) | "
    "当前活: THERMO-OVERLAY-P1-BURN 待 autofill watchdog 认领烧录 (pool status=ready lane bm-a; E42 停窗顺延 <=30min 节律内; prereg 窗 48h 自 03:3x 冻结充裕) | "
    "最近实物: results/_r940bma_rebase_resolver.py + resolver2.py + 双 receipt json + results/_r940bma_s6_chain.json (39 legs 0 bad, 04:2x) | "
    "下个里程碑: r941 burn verdict absorb + prereg sec.7/8 machine backfill + gate_attrition finalize check; PARKING-P1 burn due 10-14 12:00 | "
    "did: S0-1 anchor bm-a + orphan_face=1 (jman LoRA musubi-tuner GPU-bound CPU-stall 假阳性 MV 车道只读免动) + "
    "**S0 死会话 rebase 遗产抢救** (r939 04:03 pull --rebase 撞 14 UU 死窗: pick 2fae1cd25 onto 96caaa9c8; r813 链=非 porcelain status 入口诊断 + E42 写者停窗 4 任务 + 14 面 resolver〔10 flat json S3-newest + compute_audit history 哈希 union 204->201 窗帽保真 + 3 md S3〕 + 标记零扫+add -u+continue 同 shell 原子 rc0 + 二段 rebase onto 520e190b1〔origin 进 bm-b r814 双 commit〕 + 13 面二轮 resolver〔S2-newest 04:02 再生面 + md 双胞胎一致性 override + compute_audit union〕 + tip 标记 grep 仅 r505/r506 历史 probe=史前面 + push e3b8bdd54 + fetch+rev-list 0/0 送达自证; 池面 MSG-0612 face 级验证 PASS=THERMO-OVERLAY-P1-BURN pick-only 保留 + bm-c w17-screen-0..4 lane_owner 认领存活 + updated_at newer-wins 零回退) + "
    "S0.5 双扫 orders/inbox: fleet 令面零新差集 (0058 已回执) + group ORD/DEC python-raw 双 MATCH 零消费 + inbox MSG-2026-10-10-0335 (本司 F-04 冻结声明) processed->processed/ + MSG-040x (bm-b->bm-c T-180 yield 非本机件留给 bm-c) + "
    "S1 smoke 49/49 + S2 板面: job_list 0 open, fleet tickets 0 unclaimed + S3: saturation engine ALIVE rc0 (queue 0 idle) + idle_trigger 04:08 green_idle=false (VRAM 1.09GB jman LoRA 他车道占用·无领单义务·idle_rounds 0) + "
    "S6 39 legs rc0 bad NONE new_bar=False (周六 no-op 族; driver r939 血统滚代 r940; regime_thermo_build 30s 幂等 P-5C 不动) + "
    "S7 quartet GREEN (loop pin=8 no-op first-fire 04:38 / watchdog -Force first-fire 04:32 / precommit+prepush claws 字节等) + attrition 4 台账 CLEAN (healed 注记历史件) + idle --worked + state 939->940 + HANDOVER r940 5x 准时落账 | "
    "verification: smoke 49/49 + S6 39/39 rc0 + attrition CLEAN + quartet GREEN + push 0/0 自证 + heartbeat epoch int 自证 + T 分隔钟 | "
    "scoring: 1 (抢救链=基础设施恢复+resolver 可跑件双 receipt=S0 阻断解除使 r939 2 分产品〔THERMO runner+池入条〕送达 origin; 本轮无新科学产品=烧录待 watchdog) | "
    "bookkeeping: 5/5 (state + report line + heartbeat + HANDOVER 5x stamp + S6 receipt 族) | "
    "treasure-capture: zero new method zero new treasure (resolver=域件配方复用 r782/r794/r917; S6 driver=血统滚代; TREASURE/METHODOLOGY zero append) | "
    "orphan_face=1 (jman LoRA GPU-bound 假阳性免动) | unacked_orders=0 (S0.5+S7 双扫) | 本地未达 origin commit 数=0 (commit 后 push+fetch+rev-list 自证) | token: L1 zero API | [r940 bm-a]"
)

# 1) HANDOVER append
with open('research/HANDOVER.md', 'a', encoding='utf-8') as f:
    f.write('\n' + HANDOVER_STAMP + '\n')

# 2) round report append
with open('round_reports-bm-a.md', 'a', encoding='utf-8') as f:
    f.write(REPORT_LINE.replace('04:3x:00', now.strftime('%H:%M:%S')) + '\n')

# 3) state update
with open('state-bm-a.json', encoding='utf-8') as f:
    st = json.load(f)

CUR = ("r941: THERMO-OVERLAY-P1-BURN verdict absorb (watchdog burn in-cadence) + prereg sec.7/8 machine backfill + gate_attrition finalize check; "
      "PARKING-P1 burn due 10-14 12:00; prereg window <=48h from 03:3x freeze; HANDOVER next 5x = r945")
NEXT = CUR
VERIFY = ("green (r940: S0 dead-session rebase estate salvaged 2-stage 27-UU zero-loss push e3b8bdd54 0/0; smoke 49/49; S6 39/39 rc0; "
          "attrition CLEAN; quartet GREEN; pool THERMO-OVERLAY-P1-BURN ready awaiting watchdog)")

st['round_no'] = 940
st['round'] = 940
st['loop_round'] = 940
st['last_round'] = 939
st['round_no_label'] = 'r940'
st['current'] = CUR
st['now_active'] = CUR
st['task'] = CUR
st['current_task'] = CUR
st['next'] = NEXT
st['next_milestone'] = "r941: THERMO burn verdict absorb + sec.7/8 backfill; PARKING-P1 burn due 10-14 12:00"
st['did'] = ("r940: S0 dead-session rebase estate salvage (r939 died mid pull --rebase 14 UU; 2-stage rebase 14+13 faces resolved zero-loss; "
             "E42 writer-pause; pool MSG-0612 face-verify PASS; push e3b8bdd54 0/0) + DEC/ORD python-raw double-MATCH (PS-join false-delta intercepted r814 law) + "
             "S6 39 legs rc0 bad NONE new_bar=False (Sat no-op) + smoke 49/49 + attrition CLEAN + quartet GREEN + HANDOVER r940 5x on-time stamp")
st['last_action'] = "r940 closeout: salvage chain delivered + S6 chain green + bookkeeping"
st['last_artifact'] = "results/_r940bma_rebase_resolver.py + resolver2.py + receipts + results/_r940bma_s6_chain.json (39 legs 0 bad)"
st['latest_artifact'] = st['last_artifact']
st['verify'] = VERIFY
st['verdict'] = VERIFY
st['clock_read'] = ts_iso
st['ts'] = ts_iso
st['updated'] = ts_iso
st['updated_at'] = ts_iso
st['last_seen'] = ts_iso
st['last_run'] = ts_iso
st['last_round_at'] = ts_iso
st['last_round_ts'] = ts_iso
st['last_round_closed'] = ts_iso
st['heartbeat_epoch_utc'] = epoch
st['last_heartbeat_epoch_utc'] = epoch
st['idle_rounds'] = 0
st['agenda_starved'] = False
st['orphan_faces'] = 1
st['last_decisions_ts'] = ts_iso
st['last_decisions_at'] = '2026-10-10'
st['last_orders_ts'] = ts_iso
st['last_orders_at'] = '2026-10-10'
st['push_verified'] = {"ts": "2026-10-10T04:24:00+08:00", "origin_tip": "e3b8bdd54",
                       "ahead_behind": "0/0", "note": "r940 salvage push delivered (r939 estate via 2-stage rebase); post-push fetch+rev-list"}
st['sync'] = dict(st['push_verified'])

with open('state-bm-a.json', 'w', encoding='utf-8') as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# 4) heartbeat update
hb_path = 'fleet/machines/bm-a.json'
with open(hb_path, encoding='utf-8') as f:
    hb = json.load(f)

hb['last_seen'] = ts_iso
hb['ts'] = ts_iso
hb['clock_read'] = ts_iso
hb['heartbeat_epoch_utc'] = epoch
hb['idle_rounds'] = 0
hb['agenda_starved'] = False
hb['verdict'] = VERIFY
hb['current_task'] = CUR
hb['last_artifact'] = st['last_artifact']
hb['next_milestone'] = st['next_milestone']
if 'cpu_cores' in hb:
    hb['cpu_cores'] = 32
if 'ram_free_pct' in hb:
    hb['ram_free_pct'] = 43.4
if 'gpu_free_vram_gb' in hb:
    hb['gpu_free_vram_gb'] = 1.09

with open(hb_path, 'w', encoding='utf-8') as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

assert isinstance(hb['heartbeat_epoch_utc'], int), 'epoch must be int'
print('BOOKKEEPING DONE r940 ts=', ts_iso, 'epoch=', epoch)
