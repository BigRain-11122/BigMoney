# r1028 bm-a closeout: state + heartbeat + round report (fresh-read-modify-write)
import json, time, subprocess, io
from datetime import datetime, timedelta, timezone

NOW = datetime.now(timezone(timedelta(hours=8)))
NOWISO = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())

# fresh metrics
import psutil
ram = psutil.virtual_memory()
ram_free_gb = round(ram.available / (1024**3), 1)
ram_total_gb = round(ram.total / (1024**3), 1)
ram_free_pct = round(ram.available / ram.total * 100, 1)
cpu_pct = psutil.cpu_percent(interval=1)
try:
    out = subprocess.check_output(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"], text=True)
    vram_free = int(out.strip().splitlines()[0])
except Exception:
    vram_free = None

DID = ("r1028 closed: 常规值守+面板自愈窗观察轮 -- (1) S0 吸收 pre-window 运行面 2 件 -> rebase 撞 watermark_red 双机探针写冲突"
       " (bm-c 07:11 vs bm-a 07:38 同族 probe 快照) newer-wins take-mine 治愈 1 UU; (2) S0.5 令差集空 (心跳全量 ack 含 O-0100/O-0131); "
       "D-19 ORD fcc715ea->e3c30193 增量消费 (尾行扫描=全涉他司域或 bm-a 已执行面, 零新派工) + DEC hold 881b6dcb; "
       "(3) round-zero 孤儿面=1 (probe 只读零杀); (4) S6 43/43 rc0 bad=0 (驱动器 _r1028bma_s6chain.ps1·stdout 进度行防斩首); "
       "(5) moneyflow 面板自愈两发实弹: 07:44 gate spawn detached rank pass (rank 戳 10-13 滞后预期 10-16) + 07:47 复探撞封锁窗 3 连断诚实停"
       " (EM per-IP 波动窗仍活·30min gate 自愈续候·panel complete=false cutoff 10-13); (6) W259 席位 MSG 处理归档"
       " (bm-c 自续所有权·席位窗 07:04 开已闭·bm-a 无竞争动作顺延 W260+); (7) POOL 三 open 卡定谳=0003 已交付候上游 0018/0010 候 CEO 物理件/0013 候写手席销卡 零可领; "
       "(8) Watchdog S4U flip 拒绝访问=非提权窗已知面 (双任务 LogonType Interactive 回归·C-20261016-04 转换批授权在册候提权窗)")
ART = ("results/_r1028bma_s6chain_rc.log (43/43 rc0) + _r1028bma_s6chain.ps1 (驱动器) + results/_r1028bma_ord_tail.txt "
       "(D-19 ORD 尾行消费证据) + moneyflow refresh spawn 两发实弹 (gate 输出留痕) + fleet/inbox/processed/MSG-20261017-0704-bmc-w259-seat.md")
NEXT = ("r1029+: (a) moneyflow 面板自愈续观察: 30min gate 重试在役·封锁窗 lift 后 todo≈3069 码 ~2.1h complete (10-14..10-16 填); "
        "complete 后评估 gap-fill repull (done 码 2152 尾停 10-13 截面尾参差·daykline 补拉 3.6h 夜窗可齐); (b) W260 席位窗监听"
        " (bm-c W259 prereg derive 在途·W260 席位 MSG 候; bm-a own-wave 探针候窗·被占顺延 W261+); (c) POOL-0018 bm-b 词级滚动"
        " (bm-b E1 停摆在案候复活) -> POOL-0003 复审+28 缺曲覆盖; (d) MF-IC-P1 候 N≥150 资格门 (panel complete 只第一件); "
        "(e) 双任务 S4U 转换候提权窗 (C-20261016-04 批授权在册)")
MILE = "moneyflow panel 前向恢复 (封锁窗 lift 后 ~2.1h complete·窗 <=2026-10-18) + W260 席位窗监听"
VERDICT = ("green-standby r1028 (watermark=绿 red=false; smoke 49/49; satengine ALIVE rc0 队列 0 候链; S6 43/43 rc0; "
           "面板自愈在途候封锁窗; D-19 ORD 推进零新派工; 双爪 match; Loop pin=8 no-op; Watchdog S4U 候提权窗; 孤儿面=1 只读)")
VERIFY = ("smoke 49/49 + S6 43/43 rc0 bad=0 (log _r1028bma_s6chain_rc.log) + satengine status rc0 queue0 + "
          "d19 update --advance read-back 恒等 (dec=881b6dcb hold / ord=e3c30193) + 双爪 CR 归一 match=YES + "
          "register_loop pin=8 no-op + claws match + inbox MSG processed + push 后 behind-0 自证")

def upsert(d, kv):
    d.update(kv)

# --- state-bm-a.json ---
p = "state-bm-a.json"
st = json.load(io.open(p, encoding="utf-8"))
st_old_epoch = st.get("last_heartbeat_epoch_utc", st.get("heartbeat_epoch_utc"))
upsert(st, {
    "round_no": 1028, "round": 1028, "loop_round": 1028, "last_round": 1028, "round_no_label": "r1028",
    "current": DID, "current_task": "r1028 常规值守+moneyflow 面板自愈窗观察 (gate 两发实弹·封锁窗续候)",
    "did": DID, "task": "r1028 常规值守+moneyflow 面板自愈窗观察",
    "last_action": "r1028: S6 43/43 + moneyflow gate 两发实弹 (spawn rank pass) + D-19 ORD 推进 + W259 MSG 处理",
    "last_action_at": NOWISO,
    "last_artifact": ART, "latest_artifact": ART, "recent_artifact": ART,
    "next": NEXT, "next_milestone": MILE,
    "now_active": "bm-a r1028 毕 (常规值守轮); engine-lane = W259 bm-c 在飞 (prereg derive), W260 席位候窗; 35B:8090 常设; 周六晨窗值守合法",
    "last_round_at": NOWISO, "last_round_closed": NOWISO, "last_round_ts": NOWISO,
    "last_run": NOWISO, "last_seen": NOWISO, "ts": NOWISO, "updated": NOWISO, "updated_at": NOWISO,
    "last_orders_at": NOWISO, "last_orders_read_at": NOWISO,
    "last_orders_seen": "r1028: ORD e3c30193 consumed (增量尾行扫描零新派工·bm-a 已执行面全收口)",
    "orders_ack_note": "r1028: +0 (心跳全量 ack 差集空; D-19 ORD fcc715ea->e3c30193 增量消费零新派工)",
    "heartbeat_epoch_utc": EPOCH, "heartbeat_epoch_utc_type_int": True,
    "last_heartbeat_epoch_utc": st_old_epoch,
    "orphan_face": 1, "orphan_faces": 1, "orphan_killed": 0,
    "verdict": VERDICT, "verify": VERIFY,
    "free_ram_gb": ram_free_gb, "idle_ram_gb": ram_free_gb, "ram_free_gb": ram_free_gb,
    "ram_free_pct": ram_free_pct, "free_ram_pct": ram_free_pct, "ram_load_pct": round(100 - ram_free_pct, 1),
    "total_ram_gb": ram_total_gb, "ram_free_mb": int(ram_free_gb * 1024), "idle_ram_mb": int(ram_free_gb * 1024),
    "cpu_load_pct": cpu_pct, "cpu_pct": cpu_pct, "cpu_total_pct": cpu_pct, "cpu_util_pct": cpu_pct,
})
if vram_free is not None:
    st["gpu_free_vram_mb"] = vram_free
    st["gpu_source_note"] = "nvidia-smi live read " + NOWISO + " (CEO working machine, honest " + str(vram_free) + " MiB free)"
    st["gpu_mode"] = "llm"
    st["gpu_mode_note"] = "诚实注记: bm-a 无双模烧制车道; gpu_mode=llm 表 35B:8090 常驻 GPU-offload + CEO 桌面共存, 无 gen 烧批在飞 (satengine 队列 0)"
json.dump(st, io.open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
d2 = json.load(io.open(p, encoding="utf-8"))
assert isinstance(d2["heartbeat_epoch_utc"], int), "epoch must be int"

# --- heartbeat fleet/machines/bm-a.json ---
p2 = "fleet/machines/bm-a.json"
hb = json.load(io.open(p2, encoding="utf-8"))
hb_old_epoch = hb.get("last_heartbeat_epoch_utc", hb.get("heartbeat_epoch_utc"))
upsert(hb, {
    "round_no": 1028, "round": 1028, "loop_round": 1028, "last_round": 1028, "round_no_label": "r1028",
    "current": DID, "current_task": "r1028 常规值守+moneyflow 面板自愈窗观察",
    "did": DID, "task": "r1028 常规值守+moneyflow 面板自愈窗观察",
    "last_action": "r1028: S6 43/43 + moneyflow gate 两发实弹 (spawn rank pass) + D-19 ORD 推进 + W259 MSG 处理",
    "last_action_at": NOWISO,
    "last_artifact": ART, "latest_artifact": ART, "recent_artifact": ART,
    "next": NEXT, "next_milestone": MILE,
    "now_active": "bm-a r1028 毕 (常规值守轮); engine-lane = W259 bm-c 在飞 (prereg derive), W260 席位候窗; 35B:8090 常设; 周六晨窗值守合法",
    "last_round_at": NOWISO, "last_round_closed": NOWISO, "last_round_ts": NOWISO,
    "last_run": NOWISO, "last_seen": NOWISO, "ts": NOWISO, "updated": NOWISO, "updated_at": NOWISO,
    "last_orders_at": NOWISO, "last_orders_read_at": NOWISO,
    "last_orders_seen": "r1028: ORD e3c30193 consumed (增量尾行扫描零新派工·bm-a 已执行面全收口)",
    "orders_ack_note": "r1028: +0 (心跳全量 ack 差集空; D-19 ORD fcc715ea->e3c30193 增量消费零新派工)",
    "heartbeat_epoch_utc": EPOCH, "heartbeat_epoch_utc_type_int": True,
    "last_heartbeat_epoch_utc": hb_old_epoch,
    "orphan_face": 1, "orphan_faces": 1, "orphan_killed": 0,
    "verdict": VERDICT, "verify": VERIFY,
    "free_ram_gb": ram_free_gb, "idle_ram_gb": ram_free_gb, "ram_free_gb": ram_free_gb,
    "ram_free_pct": ram_free_pct, "free_ram_pct": ram_free_pct, "ram_load_pct": round(100 - ram_free_pct, 1),
    "total_ram_gb": ram_total_gb, "ram_free_mb": int(ram_free_gb * 1024), "idle_ram_mb": int(ram_free_gb * 1024),
    "cpu_load_pct": cpu_pct, "cpu_pct": cpu_pct, "cpu_total_pct": cpu_pct, "cpu_util_pct": cpu_pct,
    "clock_read": NOWISO,
})
if vram_free is not None:
    hb["gpu_free_vram_mb"] = vram_free
    hb["gpu_source_note"] = "nvidia-smi live read " + NOWISO + " (CEO working machine, honest " + str(vram_free) + " MiB free)"
json.dump(hb, io.open(p2, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
d3 = json.load(io.open(p2, encoding="utf-8"))
assert isinstance(d3["heartbeat_epoch_utc"], int), "hb epoch must be int"
assert "T" in d3["clock_read"], "clock_read must have T separator"

# --- round report line ---
line = (NOWISO + " | r1028 bm-a (dept:舰队-常规值守+数据-S6维护) | WM-VERDICT: 绿 (red=false lane healthy; satengine ALIVE rc0 queue0) | "
        "当前: " + DID + " | latest artifact: " + ART + " | next milestone: " + MILE + " | verify: " + VERIFY +
        " | 本地未达 origin commit 数=0 (push 读回验)")
with io.open("round_reports-bm-a.md", "a", encoding="utf-8") as f:
    f.write("\n" + line + "\n")
print("CLOSEOUT OK: state+hb+report; ram_free=%.1fGB vram_free=%sMiB epoch=%d" % (ram_free_gb, vram_free, EPOCH))
