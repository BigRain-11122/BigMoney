# r1031 bm-a closeout: round report line + state + heartbeat (canon face writes)
import io, json, time, subprocess, os
from datetime import datetime, timezone, timedelta

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
CST = timezone(timedelta(hours=8))
now = datetime.now(CST)
iso = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

# --- live machine facts ---
def ram_free_gb():
    import ctypes
    class M(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong)]
    m = M(); m.dwLength = ctypes.sizeof(M); ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return round(m.ullAvailPhys / (1024**3), 1), round(m.dwMemoryLoad, 1)

free_gb, load_pct = ram_free_gb()
try:
    gpu_out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                             capture_output=True, text=True, timeout=15)
    vram_free = int(gpu_out.stdout.strip().splitlines()[0])
except Exception:
    vram_free = -1
try:
    cpu_out = subprocess.run(["wmic", "cpu", "get", "loadpercentage", "/value"], capture_output=True, text=True, timeout=15)
    cpu_pct = float([l for l in cpu_out.stdout.splitlines() if "LoadPercentage=" in l][0].split("=")[1])
except Exception:
    cpu_pct = -1.0

REPORT_LINE = (
    f"{iso} | r1031 bm-a (dept:舰队·常规值守+S6 全链绿轮) | S0 吸收 pre-window 运行面 3 件 "
    f"(orphan probe+watermark ts+heartbeat stat-noise) -> commit 96b9418ed (amend 含 11:21:06 面) + pull --rebase clean; "
    f"live-writer 定谳: watermark_red.json 轮中活写=Tools/watchdog.ps1 Invoke-C7 腿 (PS ConvertTo-Json 面·machine=bm-a·~2min 拍) "
    f"非 py_watermark 专属=r1028 吸收配方 (newer-wins+amend+rebase) 对两写者通用无需改法 | S0.5 令差集空 (最新令 O-20261017-0131 已 ack); "
    f"D-19 opening NOOP (dec 7f12de36/ord d1ebd7cc 恒等); S7 收尾双扫捕获 ORD 增量 d1ebd7cc->1a0f2402 = 恰 1 行 "
    f"(2f37df0 11:29:19 bm-c 静默令 PR-20261017-02·bm-c 本机车道·零本司动作) 消费+回执 | S1 smoke 49/49 | S3: satengine ALIVE rc0 "
    f"queue0 idle; watermark red=false healthy; idle_trigger green_idle=false (RAM {round(100-load_pct,1)}% free·CEO 周六用机合法占用·无领单义务); "
    f"任务板零 open + jobs 0; P2/P3 队列全耗尽; W261 own-wave 席位窗候 W260 finalize (bm-c 席 prereg 冻结 10:2x·n1_w260_results 未落=烧录在飞) | "
    f"S6 43/43 rc0 bad=0 (driver results/_r1031bma_s6chain.ps1·log results/_r1031bma_s6chain_rc.log); moneyflow 封锁复测=封锁延续 "
    f"(refresh 3 连 RemoteDisconnected->conn_stopped·rank 道 11:07 fetch_failed·panel cutoff 2026-10-13 complete=false·gate 30min 自愈在役·checkpoint 完好) | "
    f"S7: Loop pin=8 no-op + Watchdog 在役 (S4U flip 拒绝访问=C-20261016-04 adjudicated 面) + 双爪 CR 归一 MATCH + attrition guard rc0 + "
    f"收尾双扫差集 (ORD 已消费) | 下轮指针: (a) W260 finalize 监视=W261 席位窗开门即探针 (post-W260 universe live 重推导); (b) moneyflow 封锁 lift 复测随 S6 gate "
    f"(源解封后 todo~3069 码 ~2.1h complete→MF-IC-P1 N>=150 资格门); (c) 5x HANDOVER 轮=1035; (d) 双任务 S4U 转换候提权窗 (C-20261016-04 批授权在册) | "
    f"WM-VERDICT: 绿 (red=false lane=healthy)"
)

def append_line(path, line):
    p = os.path.join(ROOT, path)
    prev = io.open(p, "rb").read() if os.path.exists(p) else b""
    with io.open(p, "ab") as f:
        f.write(line.encode("utf-8") + b"\n")
    return len(prev), len(io.open(p, "rb").read())

prev_r, new_r = append_line("round_reports-bm-a.md", REPORT_LINE)
assert new_r > prev_r and (new_r - prev_r) < 3000, "round report append delta unexpected"

# --- state update (in-memory full read-modify-write, atomic temp replace per r985 law) ---
sp = os.path.join(ROOT, "state-bm-a.json")
st = json.loads(io.open(sp, encoding="utf-8").read())
st["round_no"] = 1031
st["round"] = 1031
st["last_round"] = 1031
st["loop_round"] = 1031
st["last_round_at"] = iso
st["last_round_closed"] = iso
st["last_round_ts"] = iso
st["last_run"] = iso
st["last_seen"] = iso
st["ts"] = iso
st["updated"] = iso
st["updated_at"] = iso
st["last_action_at"] = iso
st["last_action"] = ("r1031: 常规值守+S6 43/43 rc0 + ORD 尾扫增量 1 行消费 (bm-c 静默令·零本司动作) + "
                      "moneyflow 封锁复测 (延续·conn_stopped) + watermark_red live-writer 定谳 (watchdog C7)")
st["current_task"] = "r1031 常规值守+S6 全链绿 (moneyflow 封锁窗续候·W261 候 W260 finalize)"
st["current"] = ("r1031 closed: 常规值守+S6 全链绿+ORD 尾扫增量消费轮 -- (1) S0 吸收 pre-window 运行面 "
                 "(orphan probe+watermark ts+heartbeat stat-noise) -> commit 96b9418ed·pull --rebase clean; "
                 "watermark_red live-writer 定谳=watchdog.ps1 Invoke-C7 腿 (r1028 配方通用); (2) S0.5 令差集空; "
                 "D-19 opening 恒等零动作; (3) S1 smoke 49/49; satengine ALIVE rc0 队列 0 idle; (4) 任务板零 open+"
                 "jobs 0+P2/P3 队列耗尽+idle green_idle=false (CEO 周六用机·无领单义务); (5) moneyflow 封锁复测:"
                 "refresh 3 连 RemoteDisconnected->conn_stopped·panel cutoff 10-13·gate 自愈在役; (6) S6 43/43 rc0 "
                 "bad=0 (driver _r1031bma_s6chain.ps1·含 live_paper rc0); (7) S7: Loop pin=8 no-op + Watchdog 在役"
                 "(S4U flip=adjudicated 面) + 双爪 CR 归一 MATCH + 收尾双扫 ORD 增量 1 行 (2f37df0 bm-c 静默令·"
                 "bm-c 车道) 消费 read-back 1a0f2402 恒等")
st["did"] = st["current"]
st["task"] = "r1031 常规值守+moneyflow 封锁复测+ORD 尾扫增量消费"
st["last_artifact"] = ("results/_r1031bma_s6chain_rc.log (43/43 rc0 bad=0) + results/_r1031bma_s6chain.ps1 (驱动器) + "
                       "S0 吸收 commit 96b9418ed + moneyflow 封锁复测留痕 (results/moneyflow_update_status.json "
                       "11:29:49 面) + results/_orphan_face_probe.bm-a.json (py_faces 25/orphans 1 只读)")
st["recent_artifact"] = st["last_artifact"]
st["latest_artifact"] = st["last_artifact"]
st["verdict"] = ("green-standby r1031 (watermark=绿 red=false; smoke 49/49; satengine ALIVE rc0 队列 0 idle; "
                 "S6 43/43 rc0; D-19 opening 恒等+尾扫 ORD 1 行消费 (bm-c 域零本司动作); moneyflow 封锁延续 "
                 "conn_stopped·gate 自愈在役; W261 own-wave 候 W260 finalize (bm-c 烧录在飞); 双爪 match; "
                 "Loop pin=8 no-op; Watchdog S4U=adjudicated 面; 孤儿面=1 只读沿载 (r1029 同读数)")
st["verify"] = ("smoke 49/49 + S6 43/43 rc0 bad=0 (log _r1031bma_s6chain_rc.log) + satengine status rc0 queue0 + "
                "d19 update --advance read-back 恒等 (dec=7f12de36 恒等/ord opening d1ebd7cc 恒等->尾扫 "
                "1a0f2402 推进) + 双爪 CR 归一 match=YES + register_loop pin=8 no-op + attrition_guard rc0 + "
                "round_reports-bm-a.md r1031 行落盘 + push 后 behind-0 自证")
st["last_orders_at"] = iso
st["last_orders_seen"] = ("r1031: 尾扫 ORD d1ebd7cc->1a0f2402 消费 (增量=2f37df0 11:29:19 bm-c 静默令行·"
                          "bm-c 本机车道·零本司派工); opening 扫描时点增量=0")
st["last_decisions_at"] = iso
st["last_decisions_seen"] = "r1031: DEC 7f12de36 恒等零动作 (r1030 消费后无新增)"
st["last_decisions_ts"] = iso
st["next"] = ("r1032+: (a) W260 finalize 监视 (bm-c 席·12 分片烧录) -> 落地即 W261 席位窗开 (bm-a own-wave 探针·"
              "post-W260 universe live 重推导·席位 MSG 前置); (b) moneyflow 封锁窗 lift 复测随每轮 S6 gate "
              "(源解封后 todo≈3069 码 ~2.1h complete·再评估 gap-fill repull 夜窗 ~3.6h); (c) MF-IC-P1 候 N≥150 "
              "资格门 (panel complete 只第一件); (d) 5x HANDOVER 核对轮=1035; (e) 双任务 S4U 转换候提权窗 "
              "(C-20261016-04 批授权在册); (f) POOL-0018 bm-b 词级滚动候 + POOL-0003 复审")
st["next_milestone"] = ("W260 finalize->W261 席位窗开 (bm-c 烧录 ETA 今午后) + moneyflow panel complete "
                        "(封锁 lift 后·窗 <=2026-10-19)")
st["now_active"] = ("bm-a r1031 毕 (常规值守+S6 全链绿); engine-lane = W260 bm-c 席位在册 (prereg 冻结毕·"
                    "烧录在飞), bm-a own-wave 候 W261; 35B:8090 常设; 周六午窗值守合法 (CEO 用机中)")
st["orders_ack_note"] = "r1031: +0 新令 (opening 差集空; 尾扫增量 1 行=bm-c 域回执行·零本司派工·回执随本行)"
st["orphan_face"] = 1
st["orphan_faces"] = 1
st["orphan_killed"] = 0
st["free_ram_gb"] = free_gb
st["ram_free_gb"] = free_gb
st["idle_ram_gb"] = free_gb
st["ram_free_pct"] = round(100 - load_pct, 1)
st["free_ram_pct"] = round(100 - load_pct, 1)
st["ram_load_pct"] = load_pct
st["cpu_load_pct"] = cpu_pct
st["cpu_pct"] = cpu_pct
st["gpu_free_vram_mb"] = vram_free
st["gpu_source_note"] = f"nvidia-smi live read {iso} (CEO working machine, honest {vram_free} MiB free)"
st["idle_rounds"] = 0
st["agenda_starved"] = False
st["last_heartbeat_epoch_utc"] = st.get("heartbeat_epoch_utc", epoch)
st["heartbeat_epoch_utc"] = epoch
st["heartbeat_epoch_utc_type_int"] = True
st["clock_read"] = iso
st["d19_watermark_guard"]["round_ref"] = 1031
st["d19_watermark_guard"]["ts"] = iso
st["d19_watermark_guard_round_ref"] = 1031
st["notes_r1031"] = ("r1031: watermark_red.json 轮中活写者=Tools/watchdog.ps1 Invoke-C7 腿 (PS ConvertTo-Json 面·"
                     "observed 11:19:06/11:21:06 两拍·py_watermark 非唯一写者)——r1028 吸收配方 (absorb-commit+"
                     "pull --rebase+UU newer-wins) 对两写者通用; bm-a.json 轮首 M=纯 stat-noise (diff 空·git add "
                     "刷新即清); closeout 工具坑自踩实录=PS5.1 Set-Content 重写 CJK py 文件=GBK 双编码损毁"
                     "(pit-encoding 姊妹面·write_file 全量重写即愈·脚本零写入即崩零盘污)")

tmp = sp + ".tmp"
with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
os.replace(tmp, sp)
back = json.loads(io.open(sp, encoding="utf-8").read())
assert back["round_no"] == 1031 and isinstance(back["heartbeat_epoch_utc"], int)

# --- heartbeat ---
hp = os.path.join(ROOT, "fleet", "machines", "bm-a.json")
hb = json.loads(io.open(hp, encoding="utf-8").read())
hb["last_seen"] = iso
hb["ts"] = iso
hb["clock_read"] = iso
hb["heartbeat_epoch_utc"] = epoch
hb["heartbeat_epoch_utc_type_int"] = True
hb["round"] = 1031
hb["last_round"] = 1031
hb["round_no"] = 1031
hb["current_task"] = st["current_task"]
hb["verdict"] = "green-standby r1031 (S6 43/43 rc0; smoke 49/49; satengine ALIVE idle; ORD 尾扫增量消费; moneyflow 封锁续候; W261 候 W260 finalize)"
hb["now_active"] = st["now_active"]
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["free_ram_gb"] = free_gb
hb["ram_free_gb"] = free_gb
hb["cpu_pct"] = cpu_pct
hb["cpu_total_pct"] = cpu_pct
hb["gpu_free_vram_mb"] = vram_free
hb["did"] = st["did"]
hb["last_artifact"] = st["last_artifact"]
hb["next_milestone"] = st["next_milestone"]
hb["orders_ack_last"] = "O-20261017-0131-bm-c.md"
tmp = hp + ".tmp"
with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
os.replace(tmp, hp)
back_hb = json.loads(io.open(hp, encoding="utf-8").read())
assert isinstance(back_hb["heartbeat_epoch_utc"], int) and back_hb["round_no"] == 1031

print(json.dumps({
    "round": 1031, "ts": iso, "epoch_int": isinstance(back_hb["heartbeat_epoch_utc"], int),
    "ram_free_gb": free_gb, "cpu_pct": cpu_pct, "vram_free_mb": vram_free,
    "report_delta_bytes": new_r - prev_r,
}, ensure_ascii=False))
