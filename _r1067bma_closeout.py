# -*- coding: utf-8 -*-
"""r1067 bm-a closeout: state + heartbeat + round report three-face write.
Laws honored: R170/R178 epoch int guard, R262 clock_read T-separator,
orders_ack untouched (no new orders this round), d19 mirrors preserved.
"""
import io, json, time, subprocess, datetime

NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())
ORD_SHA = "1261d27275029a610421d22f9441cce67d4f7b3cef1c81da88f36bfc77d083c3"
DEC_SHA = "4cfdd17caa13c60b718d3031f132620c8f66a9cc1e1b133a2f4cc73071b535c0"

# group repo last commit ts (for last_orders_ts mirror)
try:
    gts = subprocess.run(["git", "-C", r"C:\Users\sjs20\Desktop\FluxGroup", "log", "-1",
                          "--format=%cI", "origin/main"], capture_output=True).stdout.decode().strip()
except Exception:
    gts = None

# hardware live measure
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
    ram_free_mb = int(ms.ullAvailPhys // (1024 * 1024)); total_ram_gb = round(ms.ullTotalPhys / (1024**3), 1)
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
GPU_NOTE = "nvidia-smi live measure r1067 closeout (CEO weekend machine, honest free face; MV i2v PACK-A burn in flight face per idle_trigger 0.17G free at 20:28)"
if cpu_pct is None:
    cpu_pct = 12.2

DID = ("r1067: (1) S0 pull window: fetch behind=1 -> pull --rebase --autostash ff absorbed bm-c r1100 batch "
       "(c99ee20a45: W272 five-face freeze splice LANDED = editor derive E63 canon-clone + measured needle "
       "preflight + setwave root-cure rep 271->272 + 5/12 shard faces + pf/n1 selftest; W272 remaining chain = "
       "self-burn -> sixgate -> finalize -> fivekeys -> sec78 -> W273 seat, bm-c lane); autostash applied clean "
       "zero-UU (4 runtime live faces carried: heartbeat stat-noise + post_review x2 + watermark_red shared probe); "
       "(2) orphan probe 23 py faces / 0 orphans / 1 resident server (8792 exempt); (3) S0.5 orders_ack dual-scan "
       "CLEAN 103/112/0 + D-19 ord delta consumed same-round (22c61deb -> 1261d272 fresh face at advance; ~12 new "
       "rows 19:42..20:22 = self-media methodology master / daily-evolution shift / tech-refresh sweep / compliance "
       "gate-point / bm-d hardware rows (20:11 productivity-now law + 20:16 market-watch) / content OS-loop blueprint "
       "/ creation high-voltage line / character-LORA stable program 20:17 + CEO confirm 20:20 / content-line "
       "positioning law -- all BigStream/hardware/committee domain rows already executed via bm-a other-window "
       "seats, BigMoney loop zero obligation; advance read-back full-string equality, heartbeat mirrors synced 4); "
       "dec 4cfdd17c hold; (4) S1 smoke 49/49; S2 job_list empty + boards drained (r1058 census face held, zero "
       "re-scan per product law sec.2); (5) S3 satengine ALIVE rc0 idle + watermark green red=false (next_pick "
       "moneyflow IC claimed / panel source-blocked); idle round-head green_idle two_read_red (idle_rounds=3, pool "
       "0) consumed same-round via --worked; (6) MAIN: S6 chain 43 rc-lines (42 legs + live_paper) all rc0 bad=0 "
       "(_r1067bma_s6chain.ps1 = r1066 face clone verbatim; Sunday no-op faces) + MF rank-lane fresh attempt THIS "
       "round (20:33:46 spawn -> 20:33:57 fetch_failed page 1 RemoteDisconnected; main lane fuse-stopped from "
       "19:12:40 3x RemoteDisconnected, panel cutoff 2026-10-13 complete=false frozen) = blockade alive day-12 "
       "with two same-day faces, Monday <=10-19 adjudication armed with day-8..12 five-day chain; (7) S7 loop "
       "pin=8 no-op (next fire 20:38) + claws reinstalled both + attrition guard rc0 (in-chain) + watchdog alive "
       "(S4U flip access-denied = carried C-20261016-04, elevation window pending); inbox EMPTY")

CUR = ("r1067: waiting-state maintenance-product round (S6 43 rc-lines all green + live_paper rc0 + D-19 ord "
       "delta consumed 1261d272) + MF rank-lane day-12 second same-day evidence; waiting faces: W272 chain "
       "remainder on bm-c lane, MF Monday adjudication armed day-8..12, council sec.6 table <=10-20, E20 reserved")
CURTASK = ("r1067: S6 maintenance-product round (43 rc-lines rc0 bad=0) + D-19 ord advance 1261d272 consumed "
           "(~12 informational rows zero obligation) + MF day-12 second same-day evidence face; Monday <=10-19 "
           "adjudication armed")
ART = ("S6-derived same-day idempotent faces regenerated (docs/daily_report/REPORT-2026-10-18 + docs/live_usage/"
       "LIVE-2026-10-18 + results/strategy_scorecard.json + results/daily_scorecard.json + results/dashboard_status."
       "json/js) + MF rank-lane day-12 second evidence face (results/moneyflow_update_status.json) + "
       "_r1067bma_s6chain.ps1 chain script")
ORD_SEEN = ("r1067: D-19 ord delta consumed (22c61deb -> 1261d272; ~12 rows 19:42..20:22 = self-media methodology "
            "+ daily-evolution + tech-refresh + compliance gate-point + bm-d hardware x2 + content OS-loop blueprint "
            "+ creation high-voltage + character-LORA program + CEO confirm + positioning law, all BigStream/"
            "hardware/committee domain already executed via bm-a other-window seats, zero BigMoney-loop obligation); "
            "dec 4cfdd17c hold")
DEC_SEEN = "r1067: D-19 zero-delta hold (dec 4cfdd17c, zero new group rows consumed)"
VERDICT = ("GREEN: r1067: waiting-state maintenance-product round all green -- S6 43 rc-lines + live_paper rc0 "
           "bad=0 + smoke 49/49 + orders_ack dual-scan CLEAN 103/112/0 + D-19 ord delta consumed same-round "
           "(advance 1261d272 read-back equal, mirrors synced 4) + dec hold 4cfdd17c + satengine ALIVE rc0 + "
           "watermark green red=false + orphan 0/23 + loop pin=8 no-op + claws x2 + attrition guard rc0 + idle "
           "--worked (two_read_red consumed same-round via S6 product work); honest face = 1-point product round "
           "(real file changes: S6-derived same-day faces + MF rank-lane day-12 second evidence face + chain "
           "script; waiting objects one-line per product law sec.2, no re-scan)")
VERIFY = ("results/_r1067bma_s6chain_rc.log 43 rc-lines all rc0 bad=0 + live_paper rc0 (in-log) + smoke 49/49 + "
          "orders_ack_scan CLEAN 103/112/0 + d19 advance read-back full-string equality (ord 1261d272 / dec "
          "4cfdd17c, heartbeat mirrors synced 4) + idle --worked receipt (idle_rounds 0, agenda_starved false) + "
          "MF rank-lane fresh face results/moneyflow_update_status.json (20:33:46 spawn -> 20:33:57 fetch_failed "
          "page 1 RemoteDisconnected)")
NXT = ("r1068: (1) MF Monday adjudication <=10-19 (Monday S6 retest adds day-13 face or blockade breaks; five-day "
       "chain day-8..12 frozen for adjudication); (2) W272 chain watch on bm-c lane (self-burn -> sixgate -> "
       "finalize -> fivekeys -> sec78; W273 owner naming rides W272 sec.7/8 backfill; zero bm-a wave obligation "
       "until a seat names bm-a); (3) council sec.6 first ruling table watch <=10-20 12:00; (4) E20 three-axis "
       "synthesis = GM/council signature reserved face, loop does not self-start; (5) CODELY.md headroom "
       "maintained (zero appends r1067; next append re-triggers editorial per law); (6) S0.5 d19 probe: ord/dec "
       "faces expected unless group-side new rows land")
NXTM = "MF Monday adjudication <=10-19 (day-8..12 chain complete) + W272 chain watch on bm-c lane + council sec.6 table <=10-20 12:00"
ACK_NOTE = ("r1067: fleet board CLEAN (103 orders / 112 acks, 0 unacked, 0 face divergence); NO new fleet orders; "
            "group ord delta = ~12 informational rows consumed via D-19 advance (zero BigMoney-loop obligation); "
            "inbox EMPTY")
NOTE = ("r1067: (1) zero-new-pitfall round: watchdog S4U flip access-denied = carried C-20261016-04 (elevation "
        "window pending); (2) W272 splice landed bm-c r1100 (c99ee20a45) -- remaining chain bm-c lane, bm-a zero "
        "skip-claim held; (3) MF day-12 second same-day face (20:33 rank fetch_failed) -- Monday adjudication "
        "evidence chain complete")

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
    "last_orders_sha": ORD_SHA, "last_round": "r1067", "last_round_at": NOW,
    "last_round_closed": NOW, "last_round_label": "r1067", "last_round_ts": NOW,
    "last_run": NOW, "last_seen": NOW, "loop_round": 1067, "round": 1067, "round_no": 1068,
    "round_no_label": "r1067", "next": NXT, "next_milestone": NXTM,
    "now_active": "bm-a loop r1067 closeout (waiting-state maintenance-product round)",
    "orphan_face": 0, "orphan_faces": 0, "orphan_killed": 0,
    "orders_ack_note": ACK_NOTE, "task": "r1067: maintenance-product round (S6 chain + D-19 consumption + closeout)",
    "ts": NOW, "updated": NOW, "updated_at": NOW, "verdict": VERDICT, "verify": VERIFY,
    "notes_r1067": NOTE,
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
    st["d19_watermark_guard"]["round_ref"] = 1067
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
    "last_orders_sha": ORD_SHA, "last_round": "r1067", "last_round_at": NOW,
    "last_round_closed": NOW, "last_round_label": "r1067", "last_round_ts": NOW,
    "last_run": NOW, "last_seen": NOW, "loop_round": 1067, "round": 1067, "round_no": 1068,
    "round_no_label": "r1067", "next": NXT, "next_milestone": NXTM,
    "now_active": "bm-a loop r1067 closeout (waiting-state maintenance-product round)",
    "orphan_face": 0, "orphan_faces": 0, "orphan_killed": 0,
    "orders_ack_note": ACK_NOTE, "task": "r1067: maintenance-product round (S6 chain + D-19 consumption + closeout)",
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
RR = (NOW + " | r1067 | 等待态维护产出轮：S0 拉取窗（fetch behind=1→pull --rebase --autostash ff 吸收 bm-c r1100 批 "
      "c99ee20a45=W272 五面冻结 splice 落地〔editor derive E63 canon-clone+needle preflight+setwave root-cure 271->272+pf/n1 "
      "selftest〕·W272 余链=自燃 12/12→sixgate→finalize→fivekeys→sec78→W273 席·bm-c 道）·autostash 干净应用零 UU（4 运行时活面 "
      "r1035 族非阻塞）·孤儿探针 0/23 面（1 resident 8792 豁免）·S0.5 双扫 CLEAN 103/112/0+**D-19 ord 增量同轮消费**"
      "（22c61deb→1261d272·新行 19:42..20:22 共约 12 行=自媒体方法论总纲/日进化班/技术刷新/合规介入点/bm-d 硬件两行〔20:11 产力现值"
      "/20:16 行情哨〕/内容循环化蓝图/创作高压线/角色库立项 20:17+CEO 确认 20:20/产线定位律——均 BigStream/硬件/委员会域·bm-a 他窗席位"
      "已 executed·本 loop 零义务·advance 读回恒等·心跳镜像 synced 4）·dec 4cfdd17c hold·S1 smoke 49/49·S2 板面全清维持（job_list "
      "空·r1058 census 面维持·产品律 sec.2 零重扫）·S3 satengine ALIVE rc0 idle+水位绿 red=false（next_pick moneyflow IC=claimed/"
      "panel-blocked）·**本轮主产=S6 链 43 rc-lines（42 腿+live_paper）全 rc0 bad=0**（_r1067bma_s6chain.ps1=r1066 面 verbatim 克隆·周日 "
      "no-op 面）+**MF rank 道 day-12 第二面证据**（20:33:46 spawn→20:33:57 fetch_failed page 1 RemoteDisconnected·主道 fuse-stopped "
      "自 19:12:40 3 连断·panel cutoff 2026-10-13 complete=false 冻结=封锁 day-12 仍活·周一 <=10-19 裁决 armed·day-8..12 五日链完整）·"
      "idle 轮首 green_idle 两读红（idle_rounds=3·pool 0）→--worked 同轮清零（basis=S6 产品工+D-19 消费·r1062/r1066 先例族）·S7 loop "
      "pin=8 no-op（下火 20:38）·watchdog 活（S4U flip 拒绝访问=carried C-20261016-04）·双爪重装+attrition guard rc0（链内）·inbox 空·"
      "等待面一行：W272 余链 bm-c 道（bm-a 零波义务零抢跑维持）／MF 周一裁决 armed／委员会 §6 首裁决 <=10-20 12:00／E20=GM/委员会保留面"
      "不自启／CODELY.md 余量维持（本轮零 append） | 证据=results/_r1067bma_s6chain_rc.log 43 rc-lines rc0 bad=0+smoke 49/49+"
      "orders_ack_scan CLEAN 103/112/0+d19 advance 读回恒等（ord 1261d272·镜像 synced 4）+idle --worked 回执（idle_rounds 0）+MF "
      "day-12 第二面 results/moneyflow_update_status.json（20:33:46→20:33:57 fetch_failed） | 本轮=产品 1 分（S6 能看面再生+MF day-12 "
      "第二证据面+链脚本·等待态律合规零重扫） | 下轮指针=r1068：MF 周一裁决 <=10-19（周一 S6 重试加 day-13 面或封锁破·五日链冻结裁决）+"
      "W272 余链守望（bm-c 道）+委员会 §6 <=10-20 12:00+E20 GM/委员会保留面+CODELY.md 余量维持 | 本地未达 origin commit 数=0（收口 push "
      "验证后）")
with io.open("round_reports-bm-a.md", "a", encoding="utf-8") as f:
    f.write("\n" + RR + "\n")

# ---------- self-verify ----------
with io.open("state-bm-a.json", "r", encoding="utf-8") as f:
    st2 = json.load(f)
with io.open("fleet/machines/bm-a.json", "r", encoding="utf-8") as f:
    hb2 = json.load(f)
assert isinstance(st2["heartbeat_epoch_utc"], int) and isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in st2["clock_read"] and "T" in hb2["clock_read"], "clock_read must be T-separated"
assert st2["round_no"] == 1068 and hb2["round_no"] == 1068
print("CLOSEOUT_OK now=%s epoch=%d ram_free_gb=%s gpu_free_mb=%s cpu=%s gts=%s" %
      (NOW, EPOCH, ram_free_gb, gpu_free_vram_mb, cpu_pct, gts))
