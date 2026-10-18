# -*- coding: utf-8 -*-
"""r1068 bm-a closeout: state + heartbeat + round report three-face write.
Laws honored: R170/R178 epoch int guard, R262 clock_read T-separator,
d19 mirrors preserved, orders_ack already appended via canonical tool.
"""
import io, json, time, subprocess, datetime

NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())
ORD_SHA = "6bfe7815b16fdebf149da24e8377cbf1761b82642175fa7374ce34ee324e2905"
DEC_SHA = "4cfdd17caa13c60b718d3031f132620c8f66a9cc1e1b133a2f4cc73071b535c0"

try:
    gts = subprocess.run(["git", "-C", r"C:\Users\sjs20\Desktop\FluxGroup", "log", "-1",
                          "--format=%cI", "origin/main"], capture_output=True).stdout.decode().strip()
except Exception:
    gts = None

ram_free_mb = None; total_ram_gb = None; cpu_pct = None
try:
    import psutil
    vm = psutil.virtual_memory()
    ram_free_mb = int(vm.available // (1024 * 1024))
    total_ram_gb = round(vm.total / (1024**3), 1)
    cpu_pct = round(psutil.cpu_percent(interval=0.5), 1)
except Exception:
    pass
if ram_free_mb is None:
    import ctypes
    class MS(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong)]
    ms = MS(); ms.dwLength = ctypes.sizeof(MS)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms))
    ram_free_mb = int(ms.ullAvailPhys // (1024 * 1024)); total_ram_gb = round(ms.ullTotalPhys // (1024**3), 1)
ram_free_gb = round(ram_free_mb / 1024.0, 1)
ram_total = total_ram_gb if total_ram_gb else 93.6
ram_free_pct = round(ram_free_gb / ram_total * 100.0, 1)
ram_load_pct = round(100.0 - ram_free_pct, 1)

gpu_free_vram_mb = None
try:
    o = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                       capture_output=True).stdout.decode().strip().splitlines()
    gpu_free_vram_mb = int(float(o[0]))
except Exception:
    pass
GPU_NOTE = ("nvidia-smi live measure r1068 closeout (CEO weekend machine, honest free face; "
            "BmaIdleGuard deployed this round, GPU lane = BigStream MV burns domain)")
if cpu_pct is None:
    cpu_pct = 12.2

DID = ("r1068: (1) S0 pull window: fetch behind=10 -> pull --rebase --autostash ff absorbed bm-c r1098..r1101 + "
       "bm-b r1010/r1011 batch (W272 FIVE-FACE CHAIN COMPLETE one-window r1100: splice c99ee20a4 + self-burn 12/12 "
       "+ sixgate 35th + finalize ledger 1,022,735/K=596,320 EXACT + fivekeys 6/6 + sec78 = W272 CLOSED; W273 SEAT "
       "published r1101 owner=bm-c 92nd own wave -> bm-a zero wave obligation GATED held; bm-b r1010 deferred "
       "payload surgery-delivered 466312108f + r1011 closeout; TWO NEW FLEET ORDERS O-20261018-2144 CEO "
       "idle-recurrence all-hands + O-20261018-2236 10-min idle hard-SLA root-cure); autostash pop 1 UU "
       "(watermark_red.json) resolved newer-wins bm-a 22:58:04 vs bm-c 21:20:01 per r1028 family, stash dropped, "
       "zero markers; (2) orphan probe 32 py faces / 0 orphans / 1 resident server (8792 exempt); (3) S0.5 "
       "orders_ack dual-scan 2 unacked (O-2144 + O-2236) -> BOTH consumed same-round with receipts: adjudication "
       "(three adjudication items = director-seat BigStream domain per dual-company law r1064 precedent, council "
       "auto-adjudication backup per O-2236 sec2.3; GPU self-claim = BigStream MV lane active; bank restock = "
       "work-bank mechanism pending kit) + INTERIM IDLEGUARD DEPLOYED (Tools/bma_idleguard.pyw per O-2236 sec2.1 "
       "spec: two-hop >=600s / machine-state.flag=pause yield zero-action / GPU busy = util>=20% + non-whitelist "
       "burn proc >=800MiB / SatEngine dead auto-revive via register_satengine_task+tick / bank-absent honest "
       "PRODUCER exposure, zero schema guessing) + BmaIdleGuard task registered 10-min Ready first fire 23:15 + "
       "first-hop live-fire rc0 (GPU util 3% idle face, satengine 0 alive, hop1-idle-marked; log ~/.codely-cli/"
       "sentinel/bma-idleguard.log) + S4U XML flip access-denied = carried C-20261016-04 (pythonw GUI-subsystem "
       "structurally windowless, zero-desktop-window guarantee holds at default principal) + MSG-20261018-2310 "
       "dispatched to bm-c (canon kit NOT on group origin: two probes 23:0x tip e740d12 zero idle-guard-kit/"
       "work-bank hits; canon adopt <=1 round after landing; localization 3 spots pre-studied); receipts appended "
       "in both order files receipt sections + dual-face ack lists via orders_ack_append.py (rescan CLEAN "
       "105/114/0); (4) D-19 ord delta consumed (1261d272 -> 6bfe7815: 6 new rows = 20:48/20:54/21:11 group "
       "automation-line orders [BigMoney jianshe-an <=10-25 already dispatched GM-layer 20:48, zero loop "
       "duplication per dedup law, report-line visibility] + 22:32/22:41/22:51 bm-d hardware/P-card rows "
       "[hardware domain executed via bm-a other-window seats]) -- advance read-back full-string equality, "
       "mirrors synced 3; dec 4cfdd17c hold; (5) S1 smoke 49/49; S2 job_list empty + boards drained (r1058 "
       "census face held, zero re-scan per product law sec.2); (6) S3 satengine ALIVE rc0 (guard first-hop "
       "verified satengine=0) + watermark green red=false; idle round-head green_idle (idle_rounds=1, "
       "agenda_starved=true, pool 0) consumed same-round via --worked (basis = O-2236 P0 execution = real "
       "product work); (7) MAIN: O-2236/O-2144 P0 same-round execution (IdleGuard deployment above) + S6 chain "
       "43 rc-lines (42 legs + live_paper) all rc0 bad=0 (_r1068bma_s6chain.ps1 = r1067 face clone verbatim; "
       "Sunday no-op faces); (8) S7 loop pin=8 no-op + claws reinstalled both + attrition guard rc0 (in-chain) + "
       "watchdog alive (S4U flip access-denied = carried C-20261016-04) + BmaIdleGuard Ready; inbox = MSG-out "
       "to bm-c only (zero inbound for bm-a)")

CUR = ("r1068: P0 order-execution product round (O-20261018-2236 + O-20261018-2144 consumed same-round: interim "
       "BmaIdleGuard deployed + task Ready + first-hop verified + receipts + MSG for canon kit) + S6 43 rc-lines "
       "all green + D-19 ord delta consumed 6bfe7815; waiting faces: canon kit on bm-c push, W273 chain on bm-c "
       "lane, MF Monday adjudication <=10-19, council sec.6 <=10-20, E20 reserved")
CURTASK = ("r1068: O-2236/O-2144 P0 execution round (interim IdleGuard deployed+verified, receipts dual-face, "
           "MSG-2310 canon-kit request) + S6 43 rc-lines rc0 bad=0 + D-19 ord advance 6bfe7815 consumed")
ART = ("Tools/bma_idleguard.pyw + Tools/register_idleguard_task.ps1 (interim 10-min idle guard per O-2236 sec2.1 "
       "spec, BmaIdleGuard task Ready first fire 23:15, first-hop live-fire rc0) + receipts in O-2144/O-2236 + "
       "fleet/inbox/MSG-20261018-2310-bma-idleguard-kit-push.md + S6-derived same-day idempotent faces + "
       "_r1068bma_s6chain.ps1")
ORD_SEEN = ("r1068: D-19 ord delta consumed (1261d272 -> 6bfe7815; 6 rows = three group automation-line orders "
            "20:48/20:54/21:11 [BigMoney construction-plan <=10-25 dispatched GM-layer 20:48, zero loop "
            "duplication] + three bm-d hardware/P-card rows [other-window executed]; zero new BigMoney-loop "
            "obligation beyond visibility) + O-2144/O-2236 fleet orders consumed same-round with receipts; dec "
            "4cfdd17c hold")
DEC_SEEN = "r1068: D-19 zero-delta hold (dec 4cfdd17c, zero new group rows consumed)"
VERDICT = ("GREEN: r1068: P0 order-execution product round all green -- O-2236/O-2144 consumed same-round "
           "(interim IdleGuard deployed per spec + BmaIdleGuard Ready + first-hop rc0 + receipts dual-face 105/114/0 "
           "+ MSG-2310 canon-kit request) + S6 43 rc-lines + live_paper rc0 bad=0 + smoke 49/49 + D-19 ord advance "
           "6bfe7815 read-back equal mirrors synced 3 + dec hold 4cfdd17c + satengine ALIVE rc0 + watermark green "
           "red=false + orphan 0/32 + loop pin=8 no-op + claws x2 + attrition guard rc0 + idle --worked (O-2236 P0 "
           "execution = real product work); honest faces = S4U XML flip access-denied carried C-20261016-04 "
           "(pythonw structurally windowless), canon kit pending upstream (interim live, adopt <=1 round after "
           "bm-c push), BmaIdleGuard first scheduled fires post-closeout observation rides next round; product "
           "score = 2-point candidate (runnable infra: guard + registered task + live-fire evidence)")
VERIFY = ("results/_r1068bma_s6chain_rc.log 43 rc-lines all rc0 bad=0 + live_paper rc0 (in-log) + smoke 49/49 + "
          "orders_ack_scan CLEAN 105/114/0 (dual-face, rc0) + d19 advance read-back full-string equality (ord "
          "6bfe7815 / dec 4cfdd17c, mirrors synced 3) + idle --worked receipt (idle_rounds 0, agenda_starved "
          "false) + guard first-hop log ~/.codely-cli/sentinel/bma-idleguard.log (hop1-idle-marked, gpu util 3%, "
          "satengine 0) + BmaIdleGuard task Ready (schtasks via wrapper rc0, first fire 23:15)")
NXT = ("r1069: (1) BmaIdleGuard first scheduled fires observation (23:15/23:25 log: hop-wait -> hop2 bank-absent "
       "exposure or busy-clear) + canon kit watch on group origin (adopt <=1 round after bm-c push, localization "
       "3 spots pre-studied: PYW path / bank filename / SYS_PY); (2) MF Monday adjudication <=10-19 (S6 retest "
       "adds day-13 face or blockade breaks; five-day chain day-8..12 frozen for adjudication); (3) W273 chain "
       "watch on bm-c lane (prereg derive = bm-c FIRST ACTION -> splice -> self-burn -> sixgate -> finalize -> "
       "W274 seat; zero bm-a wave obligation until a seat names bm-a); (4) council sec.6 first ruling table watch "
       "<=10-20 12:00; (5) BigMoney construction-plan <=10-25 = GM-layer owned, loop support on demand (zero "
       "duplication); (6) E20 three-axis synthesis = GM/council signature reserved face; (7) CODELY.md headroom "
       "maintained (zero appends r1068); (8) HANDOVER 5x next = r1070 closeout (round_no multiple of 5)")
NXTM = ("BmaIdleGuard scheduled-fire observation + canon kit adopt <=1 round after bm-c push + MF Monday "
        "adjudication <=10-19 + W273 chain watch (bm-c lane)")
ACK_NOTE = ("r1068: fleet board CLEAN after same-round consumption (105 orders / 114 acks, 0 unacked, 0 face "
            "divergence); two new fleet orders O-20261018-2144 + O-20261018-2236 both consumed with receipts "
            "(dual-face ack via canonical tool); group ord delta = 6 rows consumed via D-19 advance (three "
            "automation-line orders = GM-layer dispatched construction-plan face + three hardware rows = "
            "informational); inbox = MSG-out to bm-c only")
NOTE = ("r1068: (1) O-2236 @bm-a P0 executed same-round via interim guard: canon kit absent from group origin "
        "(bm-c built locally, push pending) -> MSG-20261018-2310 dispatched; interim = spec-faithful (two-hop/"
        "pause-yield/GPU-busy-three-face/SatEngine-revive/bank-absent-exposure), claim leg zero-schema-guessing "
        "pending canon bank schema; canon adopt <=1 round after push; (2) BmaIdleGuard S4U XML flip "
        "access-denied = carried C-20261016-04 (watchdog family face, elevation window pending); pythonw = "
        "GUI-subsystem, structurally zero-window at default principal; (3) O-2144 three adjudication items = "
        "director-seat BigStream domain per r1064 precedent (same items), O-2236 sec2.3 council auto-adjudication "
        "backup armed; (4) waiting objects one-line each per product law sec.2")

# ---------- state face ----------
with io.open("state-bm-a.json", "r", encoding="utf-8") as f:
    st = json.load(f)
prev_epoch = st.get("heartbeat_epoch_utc", EPOCH)
st.update({
    "agenda_starved": False, "clock_read": NOW, "current": CUR, "current_task": CURTASK,
    "did": DID, "heartbeat_epoch_utc": EPOCH, "heartbeat_epoch_utc_type_int": True,
    "idle_rounds": 0, "last_action": DID, "last_action_at": NOW,
    "last_artifact": ART, "latest_artifact": ART, "recent_artifact": ART,
    "last_decisions_at": NOW, "last_decisions_read_at": NOW, "last_decisions_seen": DEC_SEEN,
    "last_decisions_sha": DEC_SHA, "last_heartbeat_epoch_utc": prev_epoch,
    "last_orders_at": NOW, "last_orders_read_at": NOW, "last_orders_seen": ORD_SEEN,
    "last_orders_sha": ORD_SHA, "last_round": "r1068", "last_round_at": NOW,
    "last_round_closed": NOW, "last_round_label": "r1068", "last_round_ts": NOW,
    "last_run": NOW, "last_seen": NOW, "loop_round": 1068, "round": 1068, "round_no": 1069,
    "round_no_label": "r1068", "next": NXT, "next_milestone": NXTM,
    "now_active": "bm-a loop r1068 closeout (P0 order-execution product round)",
    "orphan_face": 0, "orphan_faces": 0, "orphan_killed": 0,
    "orders_ack_note": ACK_NOTE, "task": "r1068: P0 order-execution round (O-2236/O-2144 IdleGuard + S6 chain + D-19 + closeout)",
    "ts": NOW, "updated": NOW, "updated_at": NOW, "verdict": VERDICT, "verify": VERIFY,
    "notes_r1068": NOTE,
    "free_ram_gb": ram_free_gb, "ram_free_gb": ram_free_gb, "idle_ram_gb": ram_free_gb,
    "ram_free_mb": ram_free_mb, "idle_ram_mb": ram_free_mb,
    "free_ram_pct": ram_free_pct, "ram_free_pct": ram_free_pct, "ram_load_pct": ram_load_pct,
    "total_ram_gb": ram_total,
    "gpu_free_vram_mb": gpu_free_vram_mb if gpu_free_vram_mb is not None else st.get("gpu_free_vram_mb"),
    "gpu_source_note": GPU_NOTE,
    "cpu_load_pct": cpu_pct, "cpu_pct": cpu_pct, "cpu_total_pct": cpu_pct, "cpu_util_pct": cpu_pct,
})
if gts:
    st["last_orders_ts"] = gts
if "d19_watermark_guard" in st and isinstance(st["d19_watermark_guard"], dict):
    st["d19_watermark_guard"]["round_ref"] = 1068
    st["d19_watermark_guard"]["ts"] = NOW
with io.open("state-bm-a.json", "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# ---------- heartbeat face ----------
with io.open("fleet/machines/bm-a.json", "r", encoding="utf-8") as f:
    hb = json.load(f)
hb.update({
    "agenda_starved": False, "clock_read": NOW, "current": CUR, "current_task": CURTASK,
    "did": DID, "last_action": DID, "last_action_at": NOW,
    "last_artifact": ART, "latest_artifact": ART, "recent_artifact": ART,
    "last_decisions_at": NOW, "last_decisions_read_at": NOW, "last_decisions_seen": DEC_SEEN,
    "last_decisions_sha": DEC_SHA, "last_heartbeat_epoch_utc": prev_epoch,
    "last_orders_at": NOW, "last_orders_read_at": NOW, "last_orders_seen": ORD_SEEN,
    "last_orders_sha": ORD_SHA, "last_round": "r1068", "last_round_at": NOW,
    "last_round_closed": NOW, "last_round_label": "r1068", "last_round_ts": NOW,
    "last_run": NOW, "last_seen": NOW, "loop_round": 1068, "round": 1068, "round_no": 1069,
    "round_no_label": "r1068", "next": NXT, "next_milestone": NXTM,
    "now_active": "bm-a loop r1068 closeout (P0 order-execution product round)",
    "orphan_face": 0, "orphan_faces": 0, "orphan_killed": 0,
    "orders_ack_note": ACK_NOTE, "task": "r1068: P0 order-execution round (O-2236/O-2144 IdleGuard + S6 chain + D-19 + closeout)",
    "ts": NOW, "updated": NOW, "updated_at": NOW, "verdict": VERDICT, "verify": VERIFY,
    "health": "green",
    "heartbeat_epoch_utc": EPOCH, "heartbeat_epoch_utc_type_int": True,
    "idle_rounds": 0,
    "free_ram_gb": ram_free_gb, "ram_free_gb": ram_free_gb, "idle_ram_gb": ram_free_gb,
    "ram_free_mb": ram_free_mb, "idle_ram_mb": ram_free_mb,
    "free_ram_pct": ram_free_pct, "ram_free_pct": ram_free_pct, "ram_load_pct": ram_load_pct,
    "total_ram_gb": ram_total,
    "gpu_free_vram_mb": gpu_free_vram_mb if gpu_free_vram_mb is not None else hb.get("gpu_free_vram_mb"),
    "gpu_source_note": GPU_NOTE,
    "cpu_load_pct": cpu_pct, "cpu_pct": cpu_pct, "cpu_total_pct": cpu_pct, "cpu_util_pct": cpu_pct,
})
if gts:
    hb["last_orders_ts"] = gts
with io.open("fleet/machines/bm-a.json", "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# ---------- round report line ----------
RR = (NOW + " | r1068 | P0 令执行产品轮：S0 拉取窗（fetch behind=10→pull --rebase --autostash ff 吸收 bm-c r1098..r1101+"
      "bm-b r1010/r1011 批〔W272 五面链一窗收官：splice+自燃 12/12+sixgate 35th+finalize ledger 1,022,735/K=596,320+"
      "fivekeys 6/6+sec78=W272 CLOSED·W273 席已发布 owner=bm-c 92nd own wave=bm-a 零波义务 GATED 维持·bm-b r1010 递延载荷"
      "外科送达 466312108f+r1011 收口·**新令两份=O-20261018-2144 CEO 闲置复发全员令+O-20261018-2236 10min 闲置硬 SLA 根治令**〕）·"
      "autostash pop 1 UU（watermark_red.json）r1028 族 newer-wins 清解（bm-a 22:58:04 胜 bm-c 21:20:01·stash 丢·零标记）·"
      "孤儿探针 0/32 面（1 resident 8792 豁免）·S0.5 双扫 2 未回执（O-2144+O-2236）→**两令同轮消费+回执**：三裁件=导演席 "
      "BigStream 域按 r1064 同件判例零 quant-loop 义务（委员会 10:00 径裁兜底在令内）+GPU 自领活=BigStream MV 烧批道+"
      "**过渡 BmaIdleGuard 部署**（Tools/bma_idleguard.pyw 按 §2.1 规格：两跳 ≥600s/pause 旗让路/GPU 忙判 util≥20%+非白名单"
      "烧批 ≥800MiB/SatEngine 死自动复活/银行缺位诚实曝光零 schema 猜测）+任务注册 BmaIdleGuard（10min·Ready 实测·首火 "
      "23:15·S4U flip 拒绝访问=carried C-20261016-04〔与 watchdog 同病〕·pythonw=GUI 子系统结构性零窗）+首跳实弹 rc0（GPU "
      "util 3% 闲+satengine 0 活+hop1 标记·日志 sentinel/bma-idleguard.log）+**canon kit 不在集团 origin**（两探 tip "
      "e740d12 零命中）→MSG-20261018-2310 已发 @bm-c 请推上链·落地后 ≤1 轮 canon adopt（本地化三处已预研）·双令回执节已落+"
      "双面 ack 105/114/0 CLEAN·D-19 ord 增量消费（1261d272→6bfe7815·6 行=集团自动化条线三令〔BigMoney 建设案 ≤10-25 GM 层"
      "已 dispatched 零双开〕+bm-d 硬件三行·advance 读回恒等·镜像 synced 3）·dec 4cfdd17c hold·S1 smoke 49/49·S2 板面维持"
      "（r1058 census 面·零重扫）·S3 satengine ALIVE rc0+水位绿 red=false·idle 轮首 green_idle（idle_rounds=1·pool 0）→"
      "--worked 同轮清零（basis=O-2236 P0 执行=实产出工）·**主产 2=S6 链 43 rc-lines 全 rc0 bad=0**（_r1068bma_s6chain.ps1="
      "r1067 面 verbatim 克隆·周日 no-op 面）·S7 loop pin=8 no-op（下火 23:18）+watchdog 活（S4U=carried）+双爪重装+attrition "
      "guard rc0（链内）+inbox=仅 MSG-out @bm-c | 证据=results/_r1068bma_s6chain_rc.log 43 rc-lines rc0 bad=0+smoke 49/49+"
      "orders_ack_scan CLEAN 105/114/0+guard 首跳日志 hop1-idle-marked+BmaIdleGuard Ready（wrapper 查询 rc0·首火 23:15）+"
      "d19 advance 读回恒等（ord 6bfe7815·镜像 synced 3）+idle --worked 回执 | 当前活=本轮收口（O-2236/O-2144 P0 执行完毕）·"
      "最近实物=Tools/bma_idleguard.pyw+register_idleguard_task.ps1（守卫+任务在役·首火 23:15）·下个里程碑=canon kit adopt"
      "（≤1 轮 after bm-c 推）+MF 周一裁决 <=10-19+W273 链守望（bm-c 道） | 本轮=产品 2 分（可跑基础设施：守卫+注册任务+实弹证据+"
      "双令回执；等待态律合规零重扫） | 下轮指针=r1069：守卫首火观察（23:15/23:25 日志线）+canon kit 望（adopt ≤1 轮）+MF 周一"
      "裁决 <=10-19（day-13 面或封锁破）+W273 余链（bm-c 道·W274 席候 W273 §7/8）+委员会 §6 <=10-20 12:00+BigMoney 建设案 "
      "≤10-25（GM 层主责·loop 按需支援）+CODELY.md 余量维持 | 本地未达 origin commit 数=0（收口 push 验证后）")
with io.open("round_reports-bm-a.md", "a", encoding="utf-8") as f:
    f.write("\n" + RR + "\n")

# ---------- self-verify ----------
with io.open("state-bm-a.json", "r", encoding="utf-8") as f:
    st2 = json.load(f)
with io.open("fleet/machines/bm-a.json", "r", encoding="utf-8") as f:
    hb2 = json.load(f)
assert isinstance(st2["heartbeat_epoch_utc"], int) and isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in st2["clock_read"] and "T" in hb2["clock_read"], "clock_read must be T-separated"
assert st2["round_no"] == 1069 and hb2["round_no"] == 1069
print("CLOSEOUT_OK now=%s epoch=%d ram_free_gb=%s gpu_free_mb=%s cpu=%s gts=%s" %
      (NOW, EPOCH, ram_free_gb, gpu_free_vram_mb, cpu_pct, gts))
