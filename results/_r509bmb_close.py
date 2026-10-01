# r509 bm-b round close-out: state + heartbeat + round report
import json, time, subprocess

NOW = "2026-10-01T15:3x:xx+08:00"
TS  = time.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"

# --- state.json ---
st = json.load(open('state.json', encoding='utf-8-sig'))
st['machine_id'] = 'bm-b'
st['round_no'] = 509
st['note'] = ("r509: S0 integration adopted r508 crashed-session residue onto origin/main "
              "(r314 CAS single carry 9135d6cf1 delivered: bm-b engine instance + W10 wave "
              "12/12 products + claims + telemetry + CODELY/ticket/pool-samples union; dual "
              "duplicate lineage collapsed; UA rename-detection resolved per mirror-fix) + "
              "STOCK_FACE_FURNACE_P1 phantom ledger REAL-APPENDED (r506 block never existed "
              "on disk -- runner guard-only bug; real append 386,267+281=386,548 + runner "
              "persistence fix + selftest 22/22, MSG-1432 fulfilled with truth correction) + "
              "W10 finalize DELIVERED (K=22,120 merged mu -0.0913 sigma 0.24453 se_mu "
              "0.001644, skill_line_v2 1.1482->1.1491 K-lift +0.0009, ledger 386,548+2,200="
              "388,748, predictions 4/4 PASS, S7/S8 same-window backfill) + S6 37 legs rc0 "
              "+ smoke 47/47")
for k in ('last_round_at', 'last_round_ts', 'ts', 'updated', 'updated_at'):
    st[k] = TS
st['last_round_at'] = "2026-10-01T15:3x:xx+08:00"
json.dump(st, open('state.json', 'w', encoding='utf-8', newline='\n'),
          ensure_ascii=False, indent=1)
print('state round_no =', st['round_no'])

# --- heartbeat ---
hb = json.load(open('fleet/machines/bm-b.json', encoding='utf-8-sig'))
epoch = int(time.time())
assert isinstance(epoch, int)
hb['machine_id'] = 'bm-b'
hb['last_seen'] = TS
hb['current_task'] = 'r509 close: W10 finalized (388,748) + furnace ledger real-append + S0 integration delivered'
hb['cpu_cores'] = 16
try:
    import psutil
    hb['idle_ram_gb'] = round(psutil.virtual_memory().available / 1e9, 1)
except Exception:
    pass
hb['gpu_idle_vram_gb'] = None  # no GPU workload lane this round (headless box, honest)
hb['verdict'] = 'round-509-ok: products delivered (W10 finalize + furnace real-append); next: W11 prereg (never-dry)'
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = TS
assert isinstance(hb['heartbeat_epoch_utc'], int)
assert 'T' in hb['clock_read']
json.dump(hb, open('fleet/machines/bm-b.json', 'w', encoding='utf-8', newline='\n'),
          ensure_ascii=False, indent=1)
print('heartbeat epoch int =', epoch, '| clock =', TS)

# --- round report ---
ROW = ("2026-10-01T15:3x:xx+08:00 | r509 bm-b | dept:研究/工程 | [watermark verdict: 15:23 probe insufficient_history（15min 窗重置态 n=1·非红如实）·compute_audit FLAG:idle_with_work+supply_floor=池排空 0 ready+供给断流 108min——W10 波毕引擎队列空=诚实供给面，W11 prereg=下轮首动作（never-dry 律·供给断流非怠工）] | "
 "本轮主产出（实物）: (1) **S0 整合收编 r508 死会话遗产直达 origin**（r314 CAS 单 carry commit 9135d6cf1 送达 fetch 自证）: 双重复谱系（main 分支 9 commit+detached 5 commit 同内容异 SHA）收敛为单携带面——bm-b 饱和引擎实例（scripts/saturation_engine.py 659 行+s3 CEO 面）+W10 首波 12/12 分片产物+12 claim 件+引擎遥测 4 件+bm-b lane 面+CODELY/票面/pool_samples 三 union（外科断言 4/17/14 行全过）+共享派生面取 origin 侧；push 三连拒（机队峰窗 bm-a 三连推）→r505 预置 ride+r501 净路（commit -C/--skip/假拒绝族一次收敛）→UA 冲突=bm-a mirror-fix rename 检测自动迁移连字符路径（rev-p2 双机 claim 并存零丢失）(2) **STOCK_FACE_FURNACE_P1 幻影账本真补记**（MSG-1432 履约+真相修正）: r506 的「ledger 380,320」定谳=从未落盘（append_ledger 纯函数返回 dict 不写盘+runner 只写 guard=281 trials 幻影蒸发·全树扫描双侧零命中）→真补账 386,267+281=**386,548**（活链头 derive·block 持久化入 mom_summary.json·voids_applied=[LOWAMP-P1]）+runner 修复（guard 前持久化+pit-95 拒绝腿+selftest 22/22）+MSG-153x 回执 bm-c (3) **W10 finalize 落账交付**: 12/12 分片合并=**K=22,120** 累计池（merged mu=−0.0913·sigma=0.24453·se_mu=0.001644）·skill_line_v2 @n_eff 386,548=**1.1482→1.1491**（K-lift +0.0009）·账本 **386,548+2,200=388,748**（链线性：W8→W9→REV-P2→LOWAMP-P2→FURNACE→W10 五连）·§5 预测 **4/4 PASS**（mu 漂移 0.0075<0.02/sigma −0.47%<±10%/A p95 +0.0146<0.05/线动 +0.0009≤0.02）·§7/§8 同窗回填（r307 两态律）·n1 selftest 绿（W10 materializer 面全腿） | "
 "验证: S1 smoke 47/47·S6 37 腿全 rc0（reconcile DRIFT 1 键=观察相 streak 重置照录·25/32/33/36 腿 bm-a 心跳 32min=stale-takeover 合法接管 r378 律·REGIME_GUARD enforce 请求→prospect 腿按数据 cutoff 09-30<10-01 日期门诚实降级 shadow· collectors 车道护栏诚实 no-op 13 腿）·attrition scan CLEAN（4 台账·healed 照录）·schtasks 三任务健康（Loop 正在运行/SatEngine 就绪/Watchdog 就绪）·orders 轮首+S7 双扫差集 EMPTY（139/139 O-* 全 ack·README 非令件）·D-19 753F99E8 MATCH-unchanged（python raw-bytes·temp partial clone）·furnace/n1 双 selftest 22/22+全绿·pre-commit claw MATCH·本地未达 origin commit 数=0（收轮 push+fetch 自证） | "
 "坑律（S4 已入 CODELY.md 一条）: append_ledger 返回 dict 不落盘+guard-only=幻影记账面（finalize runner 持久化顺序律） | inbox: MSG-1432（W9 链头衔接→真补账履约+回执）+MSG-1453（O-1420 回执/W9 闭卷/REV-P2 交付披露——本机无在飞烧录核实）+MSG-150x（LOWAMP-P2-NULLS 收线 kill 请求→audit pool_ready=0+引擎 queue=0 双证无在飞·零 kill 需求）三件处置入 processed | "
 "下轮指针: (1) **W11 prereg 起草**（never-dry 律·引擎队列空+supply_floor 旗——B +200 算术位落 W10 A 带预告已钉 §8·disjoint 机验强制+engine_owner 认领面）(2) T-141 s2 ledger-conversion bm-c in_progress 零干扰观察+N2/N3/N4 生成器钩子随面（法典 §1 恒不空面）(3) bm-c harvest/握手面回执观察 | "
 "executive 三行实况: 当前活=W10 波全链收口毕（引擎 idle·queue 0·诚实供给面）；最近实物=results/perpetual_faces/n1_w10_results.json（K=22,120·账本 388,748）+mom_summary.json 真补账块@15:2x+origin 9135d6cf1；下个里程碑=W11 prereg 冻结→引擎续供（窗 ≤48h·下轮首动作） [via bm-b]\n")
with open('logs/iteration-loop/round_reports.md', 'a', encoding='utf-8', newline='') as f:
    f.write(ROW)
print('round report appended')
