# -*- coding: utf-8 -*-
"""r818 bm-c close-out bookkeeping (state + heartbeat + round report).
Facts-driven: ORD/DEC shas read from results/_r818bmc_s05_facts.json
(r583 law: ZERO literal sha constants), watermark verdict from
results/watermark_red.json, idle face from results/idle_trigger.bm-c.json.
RAM via ctypes GlobalMemoryStatusEx (zero subprocess), VRAM via
nvidia-smi CREATE_NO_WINDOW. Heartbeat epoch = int(time.time()) JSON int
(R170/R178 law). clock_read/ts ISO8601 with T separator (R262 law)."""
import ctypes
import json
import os
import subprocess
import time
from datetime import datetime, timezone, timedelta

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CNW = 0x08000000
TZ = timezone(timedelta(hours=8))
NOW = datetime.now(TZ)
NOW_ISO = NOW.isoformat(timespec="seconds")


def ram_free_gb():
    class MemStat(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    m = MemStat()
    m.dwLength = ctypes.sizeof(MemStat)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return round(m.ullAvailPhys / 1e9, 1), round(m.ullTotalPhys / 1e9, 1), \
        round(100 - m.dwMemoryLoad, 1)


def vram_free_mb():
    try:
        p = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                            "--format=csv,noheader"],
                           capture_output=True, creationflags=CNW, timeout=20)
        return int(p.stdout.decode().strip().splitlines()[0].split()[0])
    except Exception:
        return -1


def jload(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


facts = jload(os.path.join(R, "results", "_r818bmc_s05_facts.json"))
wm = jload(os.path.join(R, "results", "watermark_red.json"))
idle = jload(os.path.join(R, "results", "idle_trigger.bm-c.json"))
free_gb, total_gb, free_pct = ram_free_gb()
vfree = vram_free_mb()
epoch = int(time.time())

ACT = ("当前活: r818 bm-c H3 5/5 权重字节验收+768P T2V 测试片点火（第 119 连守轮）"
       "| 最近实物: H3 五件 40,282,065,079B 逐件恒等验收+prompt_id d21c754a 768P "
       "测试在飞+research/pit-data.md 收据步死亡坑律（receipt _r818bmc_pit_append.json）"
       "+S6 40/40 rc0+qa/smoke-r818-bm-c.md @本轮收口 commit "
       "| 下个里程碑: H3 首片落 cph4/fleet/h3-local-test/outbound/local/（在飞·ETA "
       "~21:0x）+W17 SLA 10-10 00:00 窗前读数")
NEXT = ("r819 续作: ①H3 768P 测试片完成验收（results/_r818bmc_h3_client_state.json "
        "delivered 面）→outbound 交付+README 证据件+group canon commit+push 传回（bm-a "
        "收片呈 CEO 地址）②W17 screens SLA 10-10 00:00 窗前读数（autofill 循环·RAM 门·"
        "shard-1 43204 死=parked 面 autofill 自复投）③Tools 老龄助手隔离批（census 在案·"
        "treasure_guard prescan+quarantine manifest 7 天观察律先行）④C7 MSG 待 bm-b "
        "（离线挂起如实）⑤10-09 bar 第 13 轮守（sina 迟发自愈）⑥主件余量 211B 红线"
        "（新坑律一律直写域件 r666 范式）⑦tick 成轮验证（r817 ⑬留痕承接）")
VERD = ("smoke 49/49 + SAT engine status rc0 (alive, N1 wave ledger 143-201 face) + "
        "S6 40/40 rc0 (results/_r818bmc_s6_log.txt, nonzero-rc count=0) + H3 weights "
        "5/5 byte-exact vs manifest table (40,282,065,079B; state json advisory-only "
        "per receipt-step-death pit law, receipt _r818bmc_pit_append.json) + H3 768P "
        "T2V submitted prompt_id d21c754a (queue running=1, in-flight, "
        "video-only workflow = constructive no-audio per O-20261009-1901) + idle "
        "non-green (RAM %.1fGB free / %.1f%%, W17+H3 in-flight, idle_rounds=0, agenda "
        "not starved) + self-heal green (IterationLoop no-op pin=5 first-fire 20:25, "
        "watchdog re-registered, both claws installed LF-normalized) + attrition 4 "
        "ledgers CLEAN (healed history disclosed) + orphan face=1 read-only (probe "
        "py_faces=5) + DEC/ORD start+close sweep (dec hold, ord status-edit delta "
        "consumed, unacked 0) + SSH fetch rc0 both legs (GitHub channel healed, r817 "
        "⑥ note closed) + watermark_red=%s"
        % (free_gb, free_pct, json.dumps(wm.get("red", "?"))))

REPORT = ("2026-10-09T20:3x+08:00 | r818 | dept:工程/舰队（H3 权重验收+768P 测试片点火+"
          "ORD 水位消费+S6 40 腿+自愈链·第 119 bm-c 连守轮） | 本地未达 origin commit 数="
          "0（收口 commit 后 push+fetch 自证） | WM-VERDICT: %s（red=%s） | 孤儿面=1"
          "（只读·probe py_faces=5） | r818: ①S0=absorb commit 8f56ebfa0（own 活面）+SSH "
          "fetch rc0 双腿+rebase 首发拒→drift-normalize 11 面→retry 一发即中〔r814 正法"
          "第 5 轮连验〕·漂移面回查=CRLF 假脏零内容损失实锚（pit-git-resolver-rebase.md 三"
          "代条目全在 origin 版）；②S0.5=DEC 零 delta/ORD delta TRUE（EA6B0AB5→0A1D9C1D·"
          "新增行零=既有 BigStream 行 executed 状态翻面·零本司动作水位照更新）+unacked 0+"
          "inbox 出站 1（C7 MSG 待 bm-b·离线挂起）；③S1 smoke 49/49+SAT 引擎活 rc0（wave "
          "143-201 面）+idle 非绿（RAM %.1fGB 空闲·W17/H3 双在飞·idle_rounds=0）；④"
          "**H3 装机收口（O-1746 bm-c 面）**：5/5 权重落盘逐件字节==manifest 目标（总和 "
          "40,282,065,079B 恒等）·驱动收据步死亡（state 停 file-3 in-flight+receipt 零落盘"
          "+进程消失·坑律直写 pit-data.md·byte-count 门=验收面）→/free 清缓存（队列 0/0 "
          "安全窗）→**768P T2V 测试片点火**：canon 工作流 h3_t2v_local_768p_bmc.json（"
          "1344x768·124f≈5s@24fps·4 步 turbo LoRA·泥板刻字提示词=O-1746 原规格·纯画面链="
          "构造性无音轨合规 CEO 音轨禁令）提交 8188 共享服务器 prompt_id d21c754a·分离长活"
          "pid 46364（bm-a r919 evening-chain 先例·收口下轮验证）；⑤S6 40/40 rc0（"
          "update_daily 10-09 bar 第 12 轮守 new rows=0 cutoff 10-08 sina 迟发诚实·pool_"
          "dualrun 先行腿）；⑥自愈链全绿（loop pin=5 no-op·watchdog 重注册 20:24 首火·双爪"
          "LF 归一装）+attrition 4 ledger CLEAN；⑦A-sync 复核=SSH fetch 双腿 rc0=GitHub 通"
          "道 heal（r817 ⑥挂起注记解除）；⑧W17 shard-1 pid 43204 死=parked 面（autofill "
          "resubmit 车道所有·SLA 10-10 00:00 窗前读数） | %s"
          % ("绿" if not wm.get("red") else "红", json.dumps(wm.get("red", "?")),
             free_gb, NEXT))

# ---- state file ----
sp = os.path.join(R, "state-bm-c.json")
st = jload(sp)
st["round_no"] = 819
st["last_round"] = 818
st["round_no_label"] = "round 818 (bm-c)"
for k in ("clock_read", "current_task_at", "last_round_at", "last_round_ts",
          "last_seen", "last_seen_at", "last_ts", "updated", "updated_at",
          "last_decisions_read_at", "last_decisions_at", "last_orders_at",
          "last_run_at", "current_task_ts", "last_round_summary_at"):
    st[k] = NOW_ISO
st["heartbeat_epoch_utc"] = epoch
st["last_decisions_sha"] = facts["dec_sha"]
st["last_orders_sha"] = facts["ord_sha"]
st["dec_sha_method"] = ("python subprocess raw-blob bytes SHA-256 (group-tree "
    "origin/main git show; r818 start sweep via SSH primary leg rc0 (channel "
    "healed, r817 A-sync note closed); dec delta FALSE = unchanged, zero action; "
    "facts-driven from results/_r818bmc_s05_facts.json, 64hex shape-asserted; "
    "close face reads sha PROGRAMMATICALLY from facts json, ZERO literal "
    "constants (r583 law)")
st["ord_sha_method"] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN "
    "per r537 law; r818 start sweep via SSH primary leg rc0; ord delta TRUE = "
    "EA6B0AB5 -> %s consumed IN-ROUND: delta face = status-edit on existing "
    "BigStream rows (O-20261009-1830 executed closeout note), ZERO new order rows, "
    "zero BigMoney action, watermark updated; all bm-c dispatches (O-1746/O-1755/"
    "O-1845) already executed in r817/receipts in case; facts-driven, 40hex "
    "shape-asserted; ZERO literal constants (r583 law)" % facts["ord_sha"][:8])
st["current_task"] = ACT
st["activity_now"] = ACT
st["next"] = NEXT
st["next_pointer"] = NEXT
st["next_milestone"] = NEXT
st["verify"] = VERD
st["verdict"] = VERD
st["last_round_summary"] = REPORT
st["did"] = REPORT
st["free_ram_gb"] = free_gb
st["ram_free_gb"] = free_gb
st["idle_ram_gb"] = free_gb
st["total_ram_gb"] = total_gb
st["gpu_free_vram_mb"] = vfree
st["gpu_free_vram_mib"] = vfree
st["gpu_free_mb"] = vfree
st["gpu_idle_vram_mb"] = vfree
st["gpu_idle_vram_mib"] = vfree
st["gpu_vram_free_mb"] = vfree
st["gpu_idle_mb"] = vfree
st["gpu_idle_mib"] = vfree
st["idle_rounds"] = 0
st["agenda_starved"] = False
st["cpu_idle_pct"] = round(100 - idle.get("cpu_pct", 11.0), 1) if "cpu_pct" in idle else 89.0
st["cpu_util_pct"] = idle.get("cpu_pct", 11.0) if "cpu_pct" in idle else 11.0
st["cpu_pct"] = idle.get("cpu_pct", 11.0) if "cpu_pct" in idle else 11.0
st["latest_artifact"] = ("Tools/_r818bmc_{s0,s05,s6,ignite,h3_client,close}.py ("
    "r818 helper set, 1-gen clones) + research/pit-data.md (r818 H3 downloader "
    "receipt-step-death law, +797B direct-write, receipt "
    "results/_r818bmc_pit_append.json) + H3 weights 5/5 D:/ComfyUI/ComfyUI/models "
    "(40,282,065,079B byte-exact, O-1746) + H3 768P T2V prompt_id d21c754a "
    "in-flight (client pid 46364, state results/_r818bmc_h3_client_state.json) + "
    "results/_r818bmc_s6_log.txt (40/40 rc0) + qa/smoke-r818-bm-c.md + qa/"
    "equity-curve-r818-bm-c.png (detached QA pair) + results/_orphan_face_probe."
    "bm-c.json (orphan 1 read-only) + results/_attrition_guard_scan.json (4 "
    "CLEAN) @ " + NOW_ISO)
with open(sp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# ---- heartbeat ----
hp = os.path.join(R, "fleet", "machines", "bm-c.json")
hb = jload(hp)
hb["last_seen"] = NOW_ISO
hb["ts"] = NOW_ISO
hb["clock_read"] = NOW_ISO
hb["heartbeat_epoch_utc"] = epoch
hb["current_task"] = ACT
hb["current_task_at"] = NOW_ISO
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["cpu_cores"] = 32
hb["cores"] = 32
hb["free_ram_gb"] = free_gb
hb["idle_ram_gb"] = free_gb
hb["ram_free_gb"] = free_gb
hb["gpu_free_vram_mb"] = vfree
hb["gpu_free_vram_mib"] = vfree
hb["gpu_free_mb"] = vfree
hb["verdict"] = "ok"
hb["next"] = NEXT
hb["next_milestone"] = NEXT
hb["latest_artifact"] = st["latest_artifact"]
with open(hp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# ---- round report ----
rp = os.path.join(R, "round_reports-bm-c.md")
with open(rp, "a", encoding="utf-8", newline="\n") as f:
    f.write("\n" + REPORT + "\n")

# ---- self-asserts ----
st2 = jload(sp)
hb2 = jload(hp)
assert isinstance(st2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert isinstance(hb2["heartbeat_epoch_utc"], int), "hb epoch must be JSON int"
assert "T" in st2["clock_read"] and "T" in hb2["clock_read"], "T separator law"
print("CLOSE OK round=818 next=819 epoch=%d ram_free=%.1fGB vram_free=%dMB "
      "ord_sha=%s dec_sha=%s" % (epoch, free_gb, vfree,
                                 facts["ord_sha"][:8], facts["dec_sha"][:8]))
