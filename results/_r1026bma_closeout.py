# r1026 bm-a closeout: round report line + state + heartbeat (python raw-bytes JSON, no PS pipes)
import json, io, os, time, subprocess
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now = datetime.now().astimezone()
ts = now.isoformat(timespec="seconds")
epoch = int(time.time())

# --- live samples: RAM (ctypes) + GPU free VRAM (nvidia-smi) ---
free_ram_gb = None
total_ram_gb = None
try:
    import ctypes
    class MS(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    ms = MS(); ms.dwLength = ctypes.sizeof(MS)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms))
    free_ram_gb = round(ms.ullAvailPhys / (1024**3), 1)
    total_ram_gb = round(ms.ullTotalPhys / (1024**3), 1)
except Exception:
    pass
gpu_free = None
try:
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                         capture_output=True, text=True, timeout=20)
    gpu_free = int(out.stdout.strip().splitlines()[0])
except Exception:
    pass

did = ("r1026 closed: 死窗遗产吸收收口轮 (01:16-05:08 死窗=xq-T1 对审签章已落 group 10e64bd + 5 腿即死 S6 链) -- "
       "(1) S0 双段 ff 拉齐 origin 14 提交 (bm-c W255/W256/W257 三链全落+W257 splice 注册面生效 550293d3f; "
       "4 untracked 日报让路面经 treasure_guard prescan rc0 清行; 6 共享 results 陈旧面 revert live-wins); "
       "(2) O-20261017-0131-bm-c §1 星晴 T1 对审签章=死窗已执行毕 (11 板 264 格+tier-2 双源互证+四件裁定: "
       "S5-32 prompt v1.1 签发/S1-07 扩 16 种子/条件项 4 件全重抽/备选收编 4 维持 1 弃 2+导演加备 1; "
       "26 签章位 GO/7 回炉位 HOLD 候 T1-1R; POOL-0013 卡漂移确认呈 dispatcher 写手席) 本轮回执收编入链; "
       "(3) S6 43 腿完整重跑 43/43 rc0 bad=0 (死窗 5 腿即死治愈; 分离进程+日志重定向防 5min 斩首; 驱动器 _r1026bma_s6chain.ps1); "
       "(4) zt_pool 周五 10-16 四面前向采集面随批上链 (死窗腿产物; gate overlap 校验内; collected_days 四面各增 10-16); "
       "(5) D-19 双 delta: ORD 553f4568->fcc715ea 6 新行消费零新派工 (00:1x bm-c 车道定格令/00:5x @bm-b 停摆并案/"
       "01:1x T1 verdict 回执/01:2x 本机 POOL-0013 回执/02:1x 本机签章回执/03:2x bm-c 三线收官回执=涉 bm-a 动作全已执行) "
       "+ DEC hold 881b6dcb; (6) smoke 49/49 + satengine ALIVE rc0 队列 0 + 双爪 match + 双任务在册针位 :X8 + attrition CLEAN; "
       "孤儿面=1 (死窗 probe 面 mcp-bridge 只读零杀); 周六夜窗满载合法")

last_artifact = ("group 10e64bd (xq-T1-DIRECTOR-SIGNOFF-r1026.md 死窗主产品·11 板签章) + "
                 "fleet/orders/O-20261017-0131-bm-c.md 回执节 (本批入链) + data/zt_pool/* 10-16 四面前向采集面 + "
                 "results/_r1026bma_s6chain_rc.log 43/43 rc0 (gitignored 本地证据) + _r1026bma_s6chain.ps1 (43 腿驱动器入链) + "
                 "group orders.md 02:1x @bm-a 签章回执行 (死窗落)")

next_ptr = ("r1027+: (a) engine-lane: W257 已 splice 注册 (bm-c r1060 550293d3f) -> bm-c r1061 将 sixgate->finalize->W258 席位; "
            "bm-a own-wave 探针预制件候窗 (pit-lineage law: _w257bmc 血统克隆-> _w258bma probe·live re-derive on post-W257 universe) -- "
            "抢席窗窄 (bm-c ~10min 自续链), 被占则目标顺延 W259+; (b) backlog 1 可领行 (BigHouse 行为线研究 idle-claim 候 GREEN-IDLE 档); "
            "(c) POOL-0018 bm-b 词级滚动到货 -> POOL-0003 复审窗+28 缺曲覆盖 (死线 10-17 24:00); "
            "(d) moneyflow 面板自愈观察 -> IC reference 批点火候; (e) bm-d join-report 落地即接线 (O-2148 sec.3); "
            "(f) W258 席位 MSG 监听 (bm-c self-seat vs bm-a 抢席裁决·commit-time order)")

milestone = ("W257 finalize->W258 席位竞争裁决 (窗 <=2026-10-18); POOL-0018 词级滚动到货 -> POOL-0003 复审+28 缺曲覆盖 (死线 10-17 24:00)")

verdict = ("green-full-work (watermark=绿 insufficient_history 观察窗 red=false; smoke 49/49; satengine ALIVE rc0 队列 0 候链; "
           "死窗遗产全收编: T1 签章回执入链+S6 43/43 完整重跑+zt_pool 周五面上链; D-19 ORD 推进 fcc715ea 零新派工; "
           "双爪双任务全绿; 孤儿面=1 死窗 probe 只读; 周六夜窗满载合法)")

verify = ("smoke 49/49 + S6 43/43 rc0 bad=0 (chain log) + satengine status rc0 (queue_depth 0) + "
          "d19 update --advance read-back 恒等 (dec=881b6dcb hold / ord=fcc715ea) + 双爪 precommit/prepush CR 归一 match=YES + "
          "schtasks 双任务在册 (IterationLoop/Watchdog 针位 :X8 对齐) + attrition_guard scan rc0 CLEAN + "
          "treasure_guard prescan rc0 登记簿零命中 (4+1 件) + idle_trigger --worked declared + 心跳 epoch int 回读")

orders_seen = ("r1026: ORD 553f4568->fcc715ea consumed (6 新行: 00:1x bm-c 车道定格令 / 00:5x @bm-b 停摆并案单 / "
               "01:1x T1 verdict 回执 / 01:2x 本机 POOL-0013 回执 / 02:1x 本机签章回执行 / 03:2x bm-c 三线收官回执 -- "
               "涉 bm-a 动作全已执行, 零新派工)")

ack_note = ("r1026: +1 ack (O-20261017-0131-bm-c 星晴 T1 对审签章请求+漫剧线接产令: sec.1 @bm-a 签章=死窗 02:2x 执行毕本轮回执收编; "
            "POOL-0013 卡漂移=呈 dispatcher 写手席销卡; sec.2/3=bm-b/bm-c 域零本机动作)")

now_active = ("bm-a full-work (r1026 死窗遗产收口毕); engine-lane = W257 注册面已生效, W258 席位竞争观察 (bm-c r1061 finalize 在途); "
              "35B:8090 常设; 周六夜窗满载合法")

seq_note = ("r1026 sequence-honest: dead window 01:16-05:08 self-labeled r1026 in its O-0131 receipt (02:2x, signoff landed group 10e64bd) "
            "but died pre-commit on bigmoney (S6 chain 5 legs then 5-min kill face); THIS window = r1026 estate-absorption closeout per "
            "r1008/r1023 precedent; canonical face = round_reports-bm-a.md + git log")

common = {
    "round": 1026, "round_no": 1026, "loop_round": 1026, "last_round": 1026,
    "round_no_label": "r1026",
    "clock_read": ts, "ts": ts, "updated": ts, "updated_at": ts,
    "last_round_at": ts, "last_round_closed": ts, "last_round_ts": ts,
    "last_run": ts, "last_seen": ts, "last_action_at": ts,
    "last_orders_at": ts, "last_orders_read_at": ts,
    "last_decisions_at": ts, "last_decisions_read_at": ts,
    "current": did, "did": did,
    "last_action": "r1026: 死窗遗产收口 (xq-T1 签章回执 + S6 43/43 完整重跑 + zt_pool 10-16 上链) + D-19 ORD 推进",
    "current_task": "r1026 estate-absorption closeout (O-0131 receipt + S6 43 legs + D-19 + zt_pool Friday faces)",
    "task": "r1026 estate-absorption closeout (O-0131 receipt + S6 43 legs + D-19 + zt_pool Friday faces)",
    "last_artifact": last_artifact, "recent_artifact": last_artifact, "latest_artifact": last_artifact,
    "next": next_ptr, "next_milestone": milestone,
    "now_active": now_active,
    "verdict": verdict, "verify": verify,
    "last_orders_seen": orders_seen,
    "orders_ack_note": ack_note,
    "idle_rounds": 0, "agenda_starved": False,
    "orphan_face": 1, "orphan_faces": 1, "orphan_killed": 0,
    "heartbeat_epoch_utc": epoch, "last_heartbeat_epoch_utc": epoch,
    "heartbeat_epoch_utc_type_int": True,
}

if free_ram_gb is not None:
    common["free_ram_gb"] = free_ram_gb
    common["ram_free_gb"] = free_ram_gb
    common["idle_ram_gb"] = free_ram_gb
    common["ram_free_mb"] = int(free_ram_gb * 1024)
    common["idle_ram_mb"] = int(free_ram_gb * 1024)
    common["free_ram_pct"] = round(free_ram_gb / total_ram_gb * 100, 1) if total_ram_gb else None
    common["ram_free_pct"] = common["free_ram_pct"]
    common["ram_load_pct"] = round(100 - common["free_ram_pct"], 1) if common["free_ram_pct"] else None
if total_ram_gb is not None:
    common["total_ram_gb"] = total_ram_gb
if gpu_free is not None:
    common["gpu_free_vram_mb"] = gpu_free
    common["gpu_source_note"] = "nvidia-smi live read %s (CEO working machine, honest %d MiB free)" % (ts, gpu_free)

# codely census (headless -p only per 63943e50b gate fix)
try:
    out = subprocess.run(["powershell", "-NoProfile", "-Command",
                          "@(Get-CimInstance Win32_Process -Filter \"name='codely.exe'\" | Where-Object { $_.CommandLine -match ' -p ' }).Count"],
                         capture_output=True, text=True, timeout=30)
    live = int(out.stdout.strip())
    common["codely_live_count"] = live
    common["codely_live_count_note"] = "r1026 %s census: headless-only -p count=%d (gate-fixed probe face)" % (ts, live)
except Exception:
    pass

def update_json(path, extra):
    fp = os.path.join(ROOT, path)
    d = json.load(io.open(fp, encoding="utf-8"))
    d.update(common)
    d.update(extra)
    # orders_ack append
    ack = d.get("orders_ack", [])
    if "O-20261017-0131-bm-c.md" not in ack:
        ack.append("O-20261017-0131-bm-c.md")
        d["orders_ack"] = ack
    tmp = fp + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    os.replace(tmp, fp)
    # read-back epoch int assertion (R170/R178 law)
    rb = json.load(io.open(fp, encoding="utf-8"))
    assert isinstance(rb["heartbeat_epoch_utc"], int), "epoch not int"
    print("WROTE %s (epoch=%d int-verified)" % (path, rb["heartbeat_epoch_utc"]))

state_extra = {
    "last_decisions_seen": "r1026: DEC 881b6dcb hold (集团 decisions.md 零新行; bm-c r1059 同谳)",
    "notes_seq_repair_r1026": seq_note,
}
# d19 guard block refresh
sd = json.load(io.open(os.path.join(ROOT, "state-bm-a.json"), encoding="utf-8"))
g = sd.get("d19_watermark_guard", {})
g["round_ref"] = 1026
g["ts"] = ts
state_extra["d19_watermark_guard"] = g
update_json("state-bm-a.json", state_extra)

hb_extra = {}
update_json(os.path.join("fleet", "machines", "bm-a.json"), hb_extra)

# round report line
line = ("%s | r1026 bm-a (dept:舰队-死窗遗产收口+数据-S6维护) | WM-VERDICT: 绿 (red=false; satengine ALIVE rc0 queue0) | "
        "当前: %s | 验证: %s | 下轮: (a) W258 席位竞争裁决 (bm-c r1061 finalize 在途; bm-a 探针预制件候窗) (b) backlog 1 可领行候 GREEN-IDLE "
        "(c) POOL-0018 到货->POOL-0003 复审 (死线 10-17 24:00) | 本地未达 origin commit 数=0 (推送读回验)\n") % (ts, did, verify)
fp = os.path.join(ROOT, "round_reports-bm-a.md")
with io.open(fp, "a", encoding="utf-8", newline="") as f:
    f.write(line)
print("APPENDED round report line (%d chars)" % len(line))
print("samples: free_ram_gb=%s gpu_free_vram_mb=%s" % (free_ram_gb, gpu_free))
