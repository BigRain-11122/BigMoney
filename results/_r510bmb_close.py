"""r510 bm-b close: heartbeat write (R170/R178 int-epoch law) + round
report line append (UTF-8 safe)."""
import json
import time

NOW = time.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
EPOCH = int(time.time())

hb = {
    "machine_id": "bm-b",
    "root_path": "C:\\Fluxgroup",
    "role": "compute-node",
    "joined": "2026-09-23",
    "last_seen": NOW,
    "heartbeat_epoch_utc": EPOCH,
    "clock_read": NOW,
    "current_task": "r510 close: W11 engine wave burning (self-driving) + S0 storm delivered",
    "cpu_cores": 16,
    "free_ram_gb": 6.0,
    "gpu_free_vram_gb": 2.2,
    "total_ram_gb": 0.0,
    "cpu_util_pct": 13.0,
    "round_no": 510,
    "verdict": "round-510-ok: S0 storm integrated (642e2bc94) + W11 freeze suite ignited (never-dry supply-gap root fix); next: W11 finalize + W12 prereg (A forced-skip)",
    "idle_ram_gb": 6.0,
    "gpu_idle_vram_gb": None,
}
# carry orders_ack forward from the existing heartbeat (all 140 acked)
with open("fleet/machines/bm-b.json", encoding="utf-8") as f:
    prev = json.load(f)
hb["orders_ack"] = prev.get("orders_ack", [])
with open("fleet/machines/bm-b.json", "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
chk = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"], "clock_read must be T-separated"
print("heartbeat ok: epoch=%d clock=%s acks=%d"
      % (chk["heartbeat_epoch_utc"], chk["clock_read"], len(chk["orders_ack"])))

REPORT = (
    " | dept:研究/工程/舰队 | [watermark verdict: RED=runnable-work-idle-low-cpu 根因定谳并本轮闭环——W10 波 14:59 烧尽后引擎队列 depth=0+池 ready=0+supply_family_streak 129min=供给断流面（never-dry 律 breach·非池机制故障）；本轮根治=N1-W11 冻结套件落地→引擎 15:43:01 点火 n1w11 自驱烧录中（本 S6 采样窗 15:43-15:44 恰为点火前后缘=audit/watermark 红旗如实携带为 pre-ignition 快照，下轮应翻绿）] | "
    "本轮主产出（实物）: (1) **S0 风暴整合交付**：r509 收官 commit eb7faf07a 滞死 mid-rebase（S7 push-retry 15:26 会话亡·单 pick 停摆·零已解冲突）+origin 已进（bm-a r522 2d28710cf）——按 r220 理由子句边界（已解冲突白费=不触发）abort+单 pick rebase 至最新 origin=一趟解：31-UU 全按 bigmoney-conflict-resolve 正典（分类器 30 classified+1 UNKNOWN 手工定性 snapshot；docs/快照面 hardened deep-ts probe 全侧 clean sweep〔本机 r509 15:23-25 > bm-a r522 15:18-20·wallclock 池〕+md/js twins 同侧；compute_audit history union 203|201→204·regime_state history/transitions union·x2_watch_log 行 union 2208|2202→2214 零丢失；r185 parse-gate 全过；r305 假拒绝复现→r501 净路 commit -C/--quit/update-ref/checkout）→ **642e2bc94 FF 一次推送**，r509 全量工作（W10 finalize 388,748+炉真补账+MSG-1432 履约）正式送达 (2) **N1-W11 冻结套件+点火**（never-dry 供给律常设步·r509 下轮指针兑现）：带 A 36_100..38_099/B 28_900..29_099 算术续带·band-gate ADMIT（pre-W11 九行+158 registry 值+lfc 实际流·回执 results/_r510bmb_w11_band_gate.py）·banned-gate ADMIT rc0·法典 §4 W11 行+prereg research/PERPETUAL_N1_W11_PREREG.md+WAVE_CONFIGS/N1_BANDS 镜像+pf selftest 8/8+n1 selftest PASS（W11 materializer 腿）·W12 预告=A 带强制跳位（40_000/40_001 探针点撞）·引擎 tick 15:43:01 点火 n1w11-0→自驱（12 分片 60s cadence·W10 同律） (3) S6 37 腿全 rc0（10-01 国庆假日=expected bar date 恒 2026-09-30 诚实 no-op 面；stale-takeover derive 合法 bm-a 心跳 24min；REGIME enforce→shadow 诚实降级照录；REPORT/LIVE 当日再生成；token delta=0） | "
    "验证: S1 smoke 47/47·orders 轮首+S7 双扫差集 EMPTY（140 件全 ack）·D-19 753F99E8 MATCH-unchanged（python raw-bytes·temp partial clone·r503 大小写归一）·attrition scan CLEAN（healed 2 行照录）·schtasks 三任务健康（Loop 正在运行 pin=2 no-op/Watchdog 就绪/SatEngine 就绪）·claw MATCH·engine alive（heartbeat 4s·W11 shard-3of12 在烧 queue 8） | "
    "坑律（已入 CODELY.md 一条）: r220 禁 abort 律边界定谳（零解状态+origin 领先=retarget 一趟解最优·理由子句不触发） | "
    "inbox: MSG-1535（bm-a REV-P2 收敛+r514 修复通报=本机无动作·已入 processed）+MSG-150x（LOWAMP-P2-NULLS 收线 kill 请求=r509 已核实在飞为零·移入 processed 补收尾）·MSG-153x（本机→bm-c 出站在场待其收） | "
    "下轮指针: (1) W11 12/12 烧毕→finalize（K 22,120→24,320·prev=388,748 derive·§7/§8 回填+E1 对账）(2) W12 prereg 首动（A 带强制跳位·首自由窗机闸定·B 29_100..29_299 机验）(3) T-139 stage-B 判决/census ranking 对决面 bm-a 侧在途观察 | "
    "executive 三行实况: 当前活=饱和引擎 W11 波自驱烧录（12 分片 60s cadence·预计 ~15:5x-16:0x 全毕）+bm-c s2 ledger-conversion 在途不打扰；最近实物=research/PERPETUAL_N1_W11_PREREG.md+results/_r510bmb_w11_band_gate.py ADMIT（commit 720b8ee57 origin 在案）+642e2bc94（r509 全量送达）；下个里程碑=W11 finalize 判决面（K=24,320·账本 388,748+2,200=390,948·窗 ≤8h·下轮） [via bm-b]\n"
)
with open("logs/iteration-loop/round_reports.md", "a", encoding="utf-8") as f:
    f.write(NOW + " | r510 bm-b" + REPORT)
print("round report appended")
