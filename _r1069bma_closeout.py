# -*- coding: utf-8 -*-
"""r1069 bm-a closeout: state watermark fix (subprocess-raw decisions SHA),
heartbeat full-field update, round-report line append."""
import datetime as _dt
import json
import os
import subprocess
import time

import psutil

ROOT = os.path.dirname(os.path.abspath(__file__))
NOW = _dt.datetime.now().astimezone()
NOW_ISO = NOW.isoformat(timespec="seconds")
EPOCH = int(time.time())

DEC_SHA = "786587317ba7bfb9d9538cbc9384e3b4549fa52339a1f17bb6a9983b2af0db4d"
ORD_SHA = "243d0ab993316f5b4a1dd1870ca799f4c2f172621a1d7ece6d312a87088ba0bc"


def jswap(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


# 1) state watermark fix (polluted pipe-hash -> subprocess-raw blob hash)
sp = os.path.join(ROOT, "state-bm-a.json")
st = json.load(open(sp, "r", encoding="utf-8"))
st["last_decisions_sha"] = DEC_SHA
jswap(sp, st)
v = json.load(open(sp, "r", encoding="utf-8"))
assert v["last_decisions_sha"] == DEC_SHA and v["round_no"] == 1070
print("state ok: round_no=1070 dec_sha=786587...")

# 2) machine samples
vm = psutil.virtual_memory()
cpu_pct = psutil.cpu_percent(interval=2)
free_gb = round(vm.available / 1024 ** 3, 1)
free_pct = round(100.0 * vm.available / vm.total, 1)
try:
    graw = subprocess.run(
        ["nvidia-smi", "--query-gpu=memory.free",
         "--format=csv,noheader,nounits"],
        capture_output=True, text=True, timeout=20).stdout.strip().splitlines()
    gpu_free_mb = int(graw[0])
except Exception:
    gpu_free_mb = -1

# 3) heartbeat full update
hp = os.path.join(ROOT, "fleet", "machines", "bm-a.json")
hb = json.load(open(hp, "r", encoding="utf-8"))
hb["heartbeat_epoch_utc"] = EPOCH
hb["heartbeat_epoch_utc_type_int"] = True
hb["last_heartbeat_epoch_utc"] = 1792336449
hb["clock_read"] = NOW_ISO
hb["ts"] = NOW_ISO
hb["updated"] = NOW_ISO
hb["updated_at"] = NOW_ISO
hb["last_seen"] = NOW_ISO
hb["last_run"] = NOW_ISO
hb["last_round_at"] = NOW_ISO
hb["last_round_closed"] = NOW_ISO
hb["last_round_ts"] = NOW_ISO
hb["last_action_at"] = NOW_ISO
hb["last_decisions_at"] = NOW_ISO
hb["last_decisions_read_at"] = NOW_ISO
hb["last_orders_at"] = NOW_ISO
hb["last_orders_read_at"] = NOW_ISO
hb["round_no"] = 1070
hb["round"] = 1069
hb["loop_round"] = 1069
hb["last_round"] = "r1069"
hb["round_no_label"] = "r1069"
hb["last_round_label"] = "r1069"
hb["now_active"] = "bm-a loop r1069 closeout (product round: BigMoney automation-line construction case + five-element audit face)"
hb["current"] = ("r1069: product round -- BigMoney automation-line construction case "
                  "(research/AUTOMATION-LINE-PLAN-v1.md, CEO group orders 10-18 20:48/21:11, "
                  "deadline 10-25 report / 10-31 acceptance) + five-element audit face "
                  "(scripts/automation_line_audit.py, selftest 8/8, E1/E2/E4 OK, E3/E5 PARTIAL, "
                  "G1-G3 named gaps) + S6 44 legs rc0 + D-19 dec/ord dual advance")
hb["current_task"] = ("r1069: construction-case product round (audit face live-verified + plan v1 "
                      "landed + S6 44 rc0 + dual watermark advance)")
hb["task"] = hb["current_task"]
hb["did"] = ("r1069: (1) S0 fetch 0/0 level (pull blocked by 2 runtime dirty faces = "
             "non-blocking, behind=0 proven); round-zero orphan probe 0/36 faces; "
             "(2) S0.5 orders scan CLEAN 105/114/0; D-19 dec delta 4cfdd17c->78658731 "
             "(new rows 20:48/21:11 CEO automation-line orders -> BigMoney construction case "
             "<=10-25 = advanced THIS round with deliverable v1); D-19 ord delta 6bfe7815->"
             "243d0ab9 (4 new rows 22:32/22:41/22:51/23:1x = 3 hardware-domain executed + 1 "
             "committee-executed C-20261018-06, zero BigMoney obligation, watermarks advanced); "
             "(3) S1 smoke 49/49; sat-engine alive (verdict idle); GREEN-IDLE with empty "
             "backlog/pool/queues -> claimed CEO-ordered standing agenda = construction case; "
             "(4) products: scripts/automation_line_audit.py (five-element auditor, selftest "
             "8/8, live audit written results/automation_line_audit.json + .bm-a lane copy) + "
             "research/AUTOMATION-LINE-PLAN-v1.md (construction plan v1: measured five-element "
             "map, G1-G5 gaps, A1-A5 build schedule, V1-V5 acceptance); "
             "(5) S6 chain 44 legs rc0 (log results/_r1069bma_s6chain_rc.log); "
             "(6) S7: loop task pin=8 no-op, claws installed, watchdog S4U flip "
             "access-denied = carried elevation window (r1068 face); "
             "(7) pipe-hash pollution caught: decisions watermark must come from "
             "subprocess-raw blob bytes (3c80adab pipe artifact -> 78658731 raw)")
hb["last_action"] = hb["did"]
hb["next"] = ("r1070: (1) A1 false-green fix start (saturation_engine claimable crossface "
              "+ selftest false-green counterexample) per plan schedule <=10-21; "
              "(2) canon kit adopt within 1 round of bm-c push (MSG-2310 pending); "
              "(3) O-2236 receipt complete, watch first scheduled IdleGuard fires")
hb["next_milestone"] = ("A1 假绿判据修正 (sat_engine claimable crossface) <=10-21; "
                        "construction plan committee report <=10-25")
hb["last_artifact"] = ("scripts/automation_line_audit.py + research/AUTOMATION-LINE-PLAN-v1.md "
                       "(2026-10-18T23:27 audit anchor)")
hb["latest_artifact"] = hb["last_artifact"]
hb["recent_artifact"] = hb["last_artifact"]
hb["verify"] = ("audit selftest 8/8 PASS + live audit 5 elements (E1/E2/E4 OK, E3/E5 "
                "PARTIAL, 3 named gaps) + S6 44 rc0 log + smoke 49/49")
hb["verdict"] = ("GREEN: r1069 product round -- construction case v1 + audit face landed, "
                 "S6 44 rc0, board CLEAN, dual watermark advanced")
hb["last_decisions_sha"] = DEC_SHA
hb["last_decisions_seen"] = ("r1069: D-19 dec delta consumed 4cfdd17c -> 78658731 (subprocess-raw; "
                             "pipe-hash 3c80adab artifact discarded); new faces = group "
                             "automation-line orders 20:48/21:11 -> BigMoney seat obligation "
                             "(construction case <=10-25) advanced this round with deliverable v1")
hb["last_decisions_ts"] = "2026-10-18T21:11:00+08:00"
hb["last_orders_sha"] = ORD_SHA
hb["last_orders_seen"] = ("r1069: D-19 ord delta consumed 6bfe7815 -> 243d0ab9; 4 new rows "
                          "(22:32 48G/V100 ruling + 22:41 P-card workforce + 22:51 slot dispatch "
                          "@bm-b/@bm-c = hardware domain executed elsewhere; 23:1x CEO command-"
                          "decode C-20261018-06 = committee-executed) -- zero BigMoney "
                          "obligation, zero-action receipt")
hb["last_orders_ts"] = "2026-10-18T23:21:00+08:00"
hb["cpu_pct"] = cpu_pct
hb["cpu_load_pct"] = cpu_pct
hb["cpu_total_pct"] = cpu_pct
hb["cpu_util_pct"] = cpu_pct
hb["free_ram_gb"] = free_gb
hb["idle_ram_gb"] = free_gb
hb["ram_free_gb"] = free_gb
hb["free_ram_pct"] = free_pct
hb["ram_free_pct"] = free_pct
hb["ram_load_pct"] = round(100.0 - free_pct, 1)
hb["idle_ram_mb"] = int(vm.available / 1024 ** 2)
hb["ram_free_mb"] = hb["idle_ram_mb"]
hb["gpu_free_vram_mb"] = gpu_free_mb
hb["gpu_source_note"] = ("nvidia-smi live measure r1069 closeout (CEO weekend machine, "
                         "AutoYield pauseLite face active, GPU headroom reserved)")
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["orphan_face"] = 0
hb["orphan_faces"] = 0
hb["notes_r1069"] = ("r1069: (1) D-19 watermark hashing law sharpened live: group-tree blob "
                     "hashes MUST come from python subprocess raw bytes (pipe through PS "
                     "console codepage re-encodes -> polluted hash 3c80adab vs raw 78658731); "
                     "(2) construction-plan five-element audit face born: "
                     "scripts/automation_line_audit.py + research/AUTOMATION-LINE-PLAN-v1.md; "
                     "(3) tz-aware pit: os.path.getmtime naive dt vs aware now -- astimezone()")
jswap(hp, hb)

# 4) round report line append
rp = os.path.join(ROOT, "round_reports-bm-a.md")
line = (
    " | ".join([
        NOW_ISO,
        "r1069",
        ("产品轮（水位绿 red=false healthy）：当前活=集团自动化条线两令（10-18 20:48/21:11）派工的 BigMoney 建设案开工落地；"
         "最近实物=scripts/automation_line_audit.py（五要素审计面·selftest 8/8·实测 E1/E2/E4 OK·E3/E5 PARTIAL·G1-G3 缺口机读点名·"
         "锚 2026-10-18T23:27+08:00）+research/AUTOMATION-LINE-PLAN-v1.md（建设案 v1·§一实测五要素映射+§二 G1-G5 缺口+§三 A1-A5 排期+§四 V1-V5 验收·"
         "死线 10-25 呈报/10-31 验收）；下个里程碑=A1 假绿判据修正（sat_engine claimable 交叉面+selftest 假绿反例）≤10-21"),
        ("S0 fetch 0/0 齐平（pull 拦于 2 运行时脏面非阻塞·behind=0 实证）·孤儿探针 0/36 面·S0.5 双扫 CLEAN 105/114/0·"
         "D-19 dec 增量 4cfdd17c→78658731（新面=20:48/21:11 集团自动化条线两令·BigMoney 席建设案义务本件即开工首窗·"
         "哈希律现场淬炼=组树 blob 哈希必须 subprocess 原始字节·PS 管道码页重编码假值 3c80adab 弃用）·"
         "D-19 ord 增量 6bfe7815→243d0ab9（4 新行=22:32/22:41/22:51 硬件域 executed+23:1x 命令拆解令委员会已裁·零本司义务·零动作回执）·"
         "S1 smoke 49/49·饱和引擎活（verdict idle）·GREEN-IDLE 达档+backlog/pool/双队列全空→常设议程领 CEO 令建设案活（产品优先律 2 分件）·"
         "S6 44 腿 rc0（23:34 收口·log=results/_r1069bma_s6chain_rc.log）·S7 双爪在位+Loop 针位 8 no-op+watchdog S4U flip 拒绝访问=carried 提权窗待·"
         "canon kit 候 bm-c 上链（MSG-2310 在哨）·idle_trigger --worked 已声明"),
        ("下轮指针=r1070：A1 假绿修正开工（sat_engine 加可点火件交叉面+selftest 假绿反例断言）·kit 上链即 adopt（≤1 轮）·O-2236 首排点火观察"),
    ])
)
with open(rp, "a", encoding="utf-8") as f:
    f.write("\n" + line + "\n")
print("heartbeat + report done; cpu=%.1f%% ram_free=%.1fGB gpu_free=%dMB" %
      (cpu_pct, free_gb, gpu_free_mb))
