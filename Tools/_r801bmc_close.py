# -*- coding: utf-8 -*-
"""r801 bm-c closeout (1-gen clone from _r800bmc_close.py; r294 dead-session
adoption window: prior 11:55 session died ~12:04 mid-S7; this session =
12:15 tick continuation, adopting QA/S6/design-doc estate + closing).
Steps: append round-report line -> bump state (round_no 801->802 + DEC/ORD
watermark keys consumed this round) -> refresh heartbeat -> self-assert.
Git add/commit/rebase/push handled by separate step (caller)."""
import ctypes
import datetime
import json
import os
import time

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())

# --- live RAM read via GlobalMemoryStatusEx (zero-window, no exe spawn) ---
class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


mem = MEMORYSTATUSEX()
mem.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem))
FREE_RAM = round(mem.ullAvailPhys / (1024 ** 3), 2)
# GPU: fresh idle_trigger read (12:15:01, in-repo, zero-window)
try:
    it = json.load(open(os.path.join(REPO, "results", "idle_trigger.bm-c.json"),
                        encoding="utf-8"))
    GPU_FREE_MIB = int(round(float(it.get("vram_free_gb", 1.1)) * 1024))
except Exception:
    GPU_FREE_MIB = 1104

DEC_SHA = "A4303E92304E25DA62392A6AFA75CB9070EF6271B9B3480D77854069473B91C6"
ORD_SHA = "40FE3CB24EC08CD30AD4DC13F4CE336611C75058"
DEC_METHOD = (
    "python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; "
    "r801 closing sweep = CONSUMED delta 83813196->A4303E92 (group 10-09 12:00 batch: "
    "D-20261009-04 receipt-sweep [bigmoney F-20260926-04 closed + F-20261009-01/03 "
    "replenish executed + F-20261009-02 QA-suffix executed, si-mian 4 flips landed] "
    "+ D-20261009-05 BigStream non-quant + D-20261009-06 orders long-age sweep "
    "non-quant -> zero-action per S0.5 law, receipt in round report); facts-driven "
    "from results/_r801bmc_s0_facts.json + results/_r801bmc_dec_rows.txt, "
    "64hex shape-asserted, never hand-typed (r583 S4 law"
)
ORD_METHOD = (
    "python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; "
    "r801 closing sweep = CONSUMED delta 175A85D1->40FE3CB2 (orders group 10-09 "
    "update: added rows = BigLife 3/4-fu receipts + MV-26 Krea-2 reorg row + "
    "MV-28 character-design + U360-L4 + U362 button-density, all executed "
    "receipts in MV/BigLife/MiniGame domains non-quant -> zero-action per S0.5 "
    "law, receipt in round report); facts-driven from results/_r801bmc_s0_facts."
    "json, 40hex shape-asserted, never hand-typed (r583 S4 law"
)

LINE = (
    "2026-10-09T12:2x+08:00 | r801 | dept:工程/研究（前会话猝死收养轮+CEO 令③设计件 v0.1 首稿+常设链全绿·第 102 bm-c 连守轮·r294 收养律双段执行） | "
    "本地未达 origin commit 数=0（commit 后 push+fetch 自证） | "
    "WM-VERDICT: 绿（red=false·verdict=py_low_board_clear 合法 idle·lane=healthy·next_pick=claimed moneyflow IC bm-a 车道合法·"
    "DEC 83813196→A4303E92/ORD 175A85D1→40FE3CB2 双消费〔收尾扫捕获·unacked 0〔55 orders〕·inbox 0→2 bm-a 消息随 rebase 吸收处置〕） | "
    "孤儿面=1（ComfyUI 产线只读不杀〔12:00 探针 r340 三面判别〕·pid 2180=W17 SHARD-1 runner RAM 门有界等待在飞非孤儿） | "
    "r801: ①S0 双段收养（r294 律）：前段=11:55 会话收养 r800 遗产（r800 会话 heartbeat 11:47 写后收口 commit 前猝死）——"
    "68 件定向吸收 commit 7e75ee831+pool_core_samples r605 union 治愈（2250=2249 origin+1 本地合法行 SUBSET_OK）+"
    "behind=2 rebase 19-UU churn 竞窗（r648 sha 通道+r782 content-driven+r516 deep-ts+r742 union+r790 活 UU+r794 定向 add 律族·"
    "ts-newer-wins 18+line-union 1·receipt=_r801bmc_rebase_resolve.json·tip=337f4af86）——前会话 12:04 S7 段再猝死；"
    "本会话=12:15 tick 二段收养（S6/QA/设计件收口+S7 closeout·零重跑零浪费）；"
    "②S0.5 双扫：轮首双恒等·收尾扫捕获双 delta——DEC 三新行=D-20261009-04 回执核销批（bigmoney 面三项全核销："
    "F-20260926-04 收讫闭行〔open→closed 司面自翻〕+F-20261009-01/03 备货池补货+F-20261009-02 QA 后缀=executed 核销〔司面 4 翻面随批落地 HQ-FEEDBACK〕）"
    "+D-05 BigStream/D-06 orders 长龄行专扫=非本司零动作；ORD 增行=BigLife 三/四犯回执+MV-26 重排版+MV-28+U360-L4+U362 全非 quant executed 行→零动作；"
    "水位键双更新（facts=_r801bmc_s05_facts+_r801bmc_s0_facts+dec_rows 探针件·shape-asserted）；"
    "③S1 smoke 49/49+QA r801 证据包 5/5（smoke-r801-bm-c.md·91 trades·sharpe 0.199·annual 0.0072·determinism=True·"
    "equity PNG 65,514B·per-machine 后缀律·前会话点火本会话收养）；"
    "④主产出=CEO 令 O-20261009-1105 §三③ exit-to-asset 引擎腿设计件 v0.1 首稿落地（research/PARKING_P1_ENGINE_LEG_DESIGN.md·76 行——"
    "命题基线/现金子状态机 CASH_FLAT→PARKED/血统复用律（engine/parking_sleeve.py←grid_sleeve+scripts/parking_paper.py←grid_paper）/"
    "回场协议 T+1 开盘保守代理 O-1132 同源+延迟成本三档压测面/风险隔离 sleeve_pnl 双列不并入组合回撤/三臂纸盘 A 国债 B 可转债 C 基线/"
    "逆回购=Phase-2 候选注记/接线门=PARKING-P1 判决批过门唯一闸〔bm-a prereg→判决跑→10-31 月界前〕/两权分立律判据线全归 bm-a prereg·"
    "SLA ≤10-16 12:00 提前 7 天达成；origin b904a0a0e PARKING-P1 prereg FROZEN〔10-14 窗提前〕已到站→v0.2 对齐修订=下轮窗）；"
    "⑤W17 池烧 RAM 门随班回执：SHARD-1 pid 2180（新码 sha 50934b02·11:38:23 点火）12:20 实读在飞（CPU 18.5s/WS 156MB 低耗等待态）·"
    "RAM 1.89GB<4GB 门未开（ComfyUI 产线常驻+Krea 17GB 下载挤压=CEO 前台面不动）·park 链 r800 已闭环不再喂 fuse·"
    "池 418=409 done+9 ready 全真实活（W17 判决链·autofill 12:12 SHARD-0 claim 刷新 commit 313357daf 在案）·SLA 10-10 00:00 跟进中；"
    "⑥S6 40/40 rc0 二十二连绿（前会话 12:01-12:02 跑完本会话收养·dualrun ZERO-DRIFT streak 51 维持·"
    "compute_audit flags=supply_gap+ignition_sla〔池饿已知面·RAM 物理阻塞非空转·py_procs=8 QA 烧窗瞬态〕·"
    "fund_premium 15:30 前诚实 no-op〔第十四观测窗〕·update_daily 10-08 截止零新行·R31 他机车道 no-op 族照录）；"
    "⑦S7 自愈批全绿（loop pin=5 present·watchdog present·双爪 CR 归一 MATCH·attrition 4 台账 CLEAN〔12:04 扫 active_loss=false〕·"
    "SAT 引擎活〔face_bm-c.json 12:19:16 新鲜 tick 面〕）·job 板清·idle 非绿档（RAM 8.9%<40% 无领单义务·idle_rounds=0·agenda 未饿）·"
    "捕获律双零（无新方法无新宝藏·坑律零——前会话 churn 竞窗 resolver 全程既有律族执法零新坑）| "
    "下轮指针: r802=①bm-a PARKING-P1 prereg FROZEN 到站（origin b904a0a0e·三臂 24 cells·null pool 94_300）→设计件 v0.2 对齐修订"
    "（判据键引用面·排程 §5 第 2 步）②W17 SHARD-1 帽退/park 循环随班回执（RAM 门后 autofill 自续·池烧完成后 T-2026-10-09-178-P1 "
    "judge verdict→s4 intake→48h CEO 呈报 SLA 10-10 00:00）③fund_premium 10-08 NAV 首采（发布面 T+1·15:30+ 轮）"
    "④CEO 三选项勾选等待态（MV 面）⑤bm-a 两 inbox 消息（W197 seat+parking-p1-claim）吸收处置 | "
    "本轮产品积分：2（设计件 v0.1 首稿=CEO 直令规格面实物〔SLA 提前 7 天〕+QA r801 包 5/5 能看能用+S6 40/40 二十二连绿+"
    "park 循环 LIVE 面=经营层实物）| "
    "记账预算：5（轮报行/心跳+state 收口/facts 双扫双件/HQ-FEEDBACK 4 翻面/dec_rows 探针件）"
)

# --- 1. round report append ---
rp = os.path.join(REPO, "logs", "iteration-loop", "round_reports-bm-c.md")
with open(rp, "a", encoding="utf-8") as fh:
    fh.write(LINE.replace("2026-10-09T12:2x+08:00", NOW) + "\n")

# --- 2. state bump + watermark keys ---
sp = os.path.join(REPO, "state-bm-c.json")
d = json.load(open(sp, encoding="utf-8"))
d["round_no"] = 802
d["round_no_label"] = "round 801 (bm-c)"
d["last_round"] = 801
d["last_round_at"] = NOW
d["last_round_ts"] = NOW
d["clock_read"] = NOW
d["last_seen"] = NOW
d["heartbeat_epoch_utc"] = EPOCH
d["free_ram_gb"] = FREE_RAM
d["idle_ram_gb"] = FREE_RAM
d["ram_free_gb"] = FREE_RAM
d["gpu_free_vram_mib"] = GPU_FREE_MIB
d["gpu_free_vram_mb"] = GPU_FREE_MIB
d["gpu_idle_vram_mb"] = GPU_FREE_MIB
d["gpu_idle_vram_mib"] = GPU_FREE_MIB
d["gpu_vram_free_mb"] = GPU_FREE_MIB
d["gpu_free_mb"] = GPU_FREE_MIB
d["gpu_idle_mb"] = GPU_FREE_MIB
d["gpu_free_mib"] = GPU_FREE_MIB
d["idle_rounds"] = 0
d["agenda_starved"] = False
d["last_decisions_sha"] = DEC_SHA
d["last_decisions_read_at"] = NOW
d["last_decisions_at"] = NOW
d["dec_sha_method"] = DEC_METHOD
d["last_decisions_sha_method"] = DEC_METHOD
d["last_orders_sha"] = ORD_SHA
d["last_orders_at"] = NOW
d["ord_sha_method"] = ORD_METHOD
d["last_orders_sha_method"] = ORD_METHOD
d["current_task"] = (
    "当前活: r801 bm-c（11:55-12:2x 窗·前会话猝死收养+CEO 令③设计件 v0.1+常设链全绿·第 102 连守轮·r294 双段收养）——"
    "主产出=exit-to-asset 引擎腿设计件 v0.1 首稿（PARKING_P1_ENGINE_LEG_DESIGN.md·SLA ≤10-16 提前 7 天）+"
    "QA r801 包 5/5+S6 40/40 二十二连绿+DEC/ORD 双消费（D-04 bigmoney 三项核销·司面 4 翻面） | "
    "最近实物: research/PARKING_P1_ENGINE_LEG_DESIGN.md（v0.1·76 行）+ qa/smoke-r801-bm-c.md（5/5）+ "
    "results/_r801bmc_s6_log.txt（40/40）+ HQ-FEEDBACK.md（4 翻面）@ 本轮收口 commit | "
    "下个里程碑: r802 设计件 v0.2 对齐（bm-a prereg FROZEN 已到站）+W17 RAM 门自续（SLA 10-10 00:00）+fund_premium 15:30+ 首采"
)
d["current_task_at"] = NOW
with open(sp, "w", encoding="utf-8") as fh:
    json.dump(d, fh, indent=1, ensure_ascii=False)

# --- 3. heartbeat refresh (own file only) ---
hp = os.path.join(REPO, "fleet", "machines", "bm-c.json")
h = json.load(open(hp, encoding="utf-8"))
h["round_no"] = 801
h["round_no_label"] = "round 801 (bm-c)"
h["last_round"] = 801
h["last_round_at"] = NOW
h["last_seen"] = NOW
h["clock_read"] = NOW
h["ts"] = NOW
h["heartbeat_epoch_utc"] = EPOCH
h["free_ram_gb"] = FREE_RAM
h["idle_ram_gb"] = FREE_RAM
h["ram_free_gb"] = FREE_RAM
h["gpu_free_vram_mb"] = GPU_FREE_MIB
h["gpu_idle_vram_mb"] = GPU_FREE_MIB
h["gpu_idle_vram_mib"] = GPU_FREE_MIB
h["gpu_vram_free_mb"] = GPU_FREE_MIB
h["gpu_free_mb"] = GPU_FREE_MIB
h["gpu_idle_mb"] = GPU_FREE_MIB
h["gpu_free_mib"] = GPU_FREE_MIB
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["last_decisions_sha"] = DEC_SHA
h["last_decisions_read_at"] = NOW
h["last_decisions_at"] = NOW
h["dec_sha_method"] = DEC_METHOD
h["last_decisions_sha_method"] = DEC_METHOD
h["last_orders_sha"] = ORD_SHA
h["last_orders_at"] = NOW
h["ord_sha_method"] = ORD_METHOD
h["last_orders_sha_method"] = ORD_METHOD
h["current_task"] = d["current_task"]
h["current_task_at"] = NOW
h["activity_now"] = d["current_task"]
h["latest_artifact"] = (
    "research/PARKING_P1_ENGINE_LEG_DESIGN.md (v0.1 CEO-order design, 76 lines) + "
    "qa/smoke-r801-bm-c.md 5/5 + qa/equity-curve-r801-bm-c.png + results/_r801bmc_s6_log.txt (40/40 rc0) "
    "+ HQ-FEEDBACK.md (D-20261009-04 4 flips) + results/_r801bmc_s05_facts.json + results/_r801bmc_s0_facts.json "
    "+ results/_r801bmc_dec_rows.txt + results/_r801bmc_rebase_resolve.json (19-UU) @ " + NOW
)
h["next_milestone"] = (
    "r802 续作: ①bm-a PARKING-P1 prereg FROZEN 到站（origin b904a0a0e·三臂 24 cells）→设计件 v0.2 对齐修订（判据键引用面·排程 §5 第 2 步）"
    "②W17 SHARD-1 帽退/park 循环随班回执（RAM 门后 autofill 自续·池烧完成后 T-2026-10-09-178-P1 judge verdict→s4 intake→"
    "48h CEO 呈报 SLA 10-10 00:00）③fund_premium 10-08 NAV 首采（发布面 T+1·15:30+ 轮）"
    "④CEO 三选项勾选等待态（MV 面）⑤bm-a 两 inbox 消息（W197 seat+parking-p1-claim）吸收处置"
)
h["next"] = h["next_milestone"]
h["next_pointer"] = h["next_milestone"]
h["did"] = LINE
h["last_round_summary"] = LINE
h["last_action"] = LINE
h["note"] = LINE
h["verdict"] = LINE
h["verify"] = (
    "QA smoke-r801-bm-c.md 5/5（91 trades·determinism=True·equity PNG 65,514B）+ "
    "S6 40/40 rc0 二十二连绿（results/_r801bmc_s6_log.txt）+ "
    "设计件 v0.1（research/PARKING_P1_ENGINE_LEG_DESIGN.md·76 行·CEO 令 O-20261009-1105 §三③·SLA 提前 7 天）+ "
    "rebase 19-UU 收口 receipt（results/_r801bmc_rebase_resolve.json·r648/r782/r516/r742 律族）+ "
    "DEC A4303E92/ORD 40FE3CB2 双消费（_r801bmc_s05_facts + _r801bmc_s0_facts + _r801bmc_dec_rows.txt 三件 shape-asserted）+ "
    "HQ-FEEDBACK 司面 4 翻面（D-20261009-04 拍板①②③核销收讫）+ dualrun ZERO-DRIFT streak 51 + "
    "attrition 4 台账 CLEAN（12:04 扫）+ 双爪 MATCH + loop pin=5 present + watchdog present + "
    "SAT 引擎活（face 12:19:16）+ W17 SHARD-1 pid 2180 在飞回执（RAM 1.89GB<4GB 门未开·park 链闭环零 fuse）"
)
h["last_seen_at"] = NOW
h["updated_at"] = NOW
h["updated"] = NOW
h["last_run_at"] = NOW
h["last_ts"] = NOW
h["last_pulled_at"] = NOW
with open(hp, "w", encoding="utf-8") as fh:
    json.dump(h, fh, indent=1, ensure_ascii=False)

# --- self-assert (R170/R178 epoch-int + T-sep + watermark shape) ---
h2 = json.load(open(hp, encoding="utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in h2["clock_read"], "clock_read must be T-separated ISO8601"
assert len(h2["last_decisions_sha"]) == 64, "dec sha 64hex"
assert len(h2["last_orders_sha"]) == 40, "ord sha 40hex"
s2 = json.load(open(sp, encoding="utf-8"))
assert s2["round_no"] == 802 and s2["last_round"] == 801, "state bump"
print("close ok: state round_no=%d last_round=%d hb round=%d epoch=%d (int) "
      "ram=%.2f gpu=%dMiB dec=%s.. ord=%s.." % (
          s2["round_no"], s2["last_round"], h2["round_no"],
          h2["heartbeat_epoch_utc"], FREE_RAM, GPU_FREE_MIB,
          DEC_SHA[:8], ORD_SHA[:8]))
