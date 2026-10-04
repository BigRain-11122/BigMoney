# -*- coding: utf-8 -*-
# r675 bm-b S7 closeout: state round_no+1, heartbeat (int epoch + T clock), round-report
# append (bytes mode, mixed-encoding file, r641 law), CODELY pit-law append.
import ctypes
import datetime
import io
import json
import time


class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


def ram_gb():
    st = MEMORYSTATUSEX()
    st.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(st))
    return st.ullTotalPhys / 2**30, st.ullAvailPhys / 2**30, st.dwMemoryLoad


now = time.time()
now_dt = datetime.datetime.now().astimezone()
clock = now_dt.isoformat(timespec="seconds")   # T separator + UTC offset (F7 caliber)
epoch = int(now)
total_gb, avail_gb, load_pct = ram_gb()

# --- 1) state.json round_no 674 -> 675 (json.dump + json.loads self-verify, r645 law) ---
sp = "state.json"
d = json.load(io.open(sp, encoding="utf-8"))
assert d.get("round_no") == 674, f"unexpected round_no {d.get('round_no')}"
d["round_no"] = 675
d["round_no_label"] = "round 675 (bm-b)"
with io.open(sp, "w", encoding="utf-8", newline="") as f:
    json.dump(d, f, ensure_ascii=False, indent=1)
chk = json.load(io.open(sp, encoding="utf-8"))
assert chk["round_no"] == 675, "state round_no self-verify FAIL"
print("state.json round_no -> 675 OK")

# --- 2) heartbeat fleet/machines/bm-b.json (int epoch, T clock, self-verify) ---
hp = "fleet/machines/bm-b.json"
h = json.load(io.open(hp, encoding="utf-8"))
h["last_seen"] = clock
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = clock
h["round_no"] = 675
h["round_no_label"] = "round 675 (bm-b)"
h["current_task"] = ("r675: trio watch probe fixed (pool-leg entries[].shards[] + 3-evidence "
                     "burning verdict x3, V793/Q616/D462) + S6 38/38 single-segment + HANDOVER 5x "
                     "r671-r675 + finalize candidate window 10-06..10-08 watch")
h["verdict"] = "healthy burning"
h["ts"] = clock
h["updated"] = clock
h["updated_at"] = clock
h["cpu_cores"] = 16
h["cpu_util_pct"] = float(load_pct)
h["free_ram_gb"] = round(avail_gb, 2)
h["idle_ram_gb"] = round(avail_gb, 2)
h["ram_free_gb"] = round(avail_gb, 2)
h["ram_avail_gb"] = round(avail_gb, 2)
h["total_ram_gb"] = round(total_gb, 2)
h["ram_gb"] = round(total_gb, 2)
# GPU idle vram from nvidia-smi live read (3295 MiB @14:3x)
h["gpu_idle_vram_gb"] = round(3295 / 1024, 2)
h["gpu_idle_vram_mb"] = 3295
h["gpu_free_vram_gb"] = round(3295 / 1024, 2)
h["gpu_free_vram_mb"] = 3295.0
h["gpu_vram_free"] = 3295
h["gpu_free_vram_mib"] = 3295
with io.open(hp, "w", encoding="utf-8", newline="") as f:
    json.dump(h, f, ensure_ascii=False, indent=1)
hchk = json.load(io.open(hp, encoding="utf-8"))
assert isinstance(hchk["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178 law)"
assert "T" in hchk["clock_read"] and "+" in hchk["clock_read"], "clock must be T-separated ISO8601"
print("heartbeat OK: epoch=%d clock=%s" % (hchk["heartbeat_epoch_utc"], hchk["clock_read"]))

# --- 3) round report append (bytes mode: mixed-encoding history file, r641 law) ---
ts = now_dt.strftime("%Y-%m-%dT%H:%M:%S+08:00")
rr_line = (
    f"{ts} | r675 (bm-b) PRODUCT (dept:舰队值守+数据维护链): [watermark verdict: GREEN (red=false "
    "lane=healthy; py_cpu 85.5%=trio burn 合法占用; audit CLEAN; dualrun ZERO-DRIFT streak 51)] | "
    "当前活: FUND 三族 NULLS 烧录在飞 V793/Q616/D462 of 2000 @14:17 (39.6/30.8/23.1pct, owner=bm-b "
    "keepalive 14:10:11 鲜活, rate 23.7/20.2/17.8/h 宽窗法, ETA V 10-06T17 / Q 10-07T10 / D 10-08T04) | "
    "最近实物: results/_r675bmb_trio_watch.{{py,json}} (14:17, trio watch 探针修正版——r674 pool 腿查不存在"
    "的顶层 shards 键=三族 NOT-FOUND 假读数, 修=entries[].shards[] 正位+三证健康判定〔k 增长+mtime 新鲜+"
    "keepalive〕burning=true x3+宽窗速率 git log -12 端对距) + results/trio_burn_eta.json 刷新 + "
    "research/HANDOVER.md 5x 行 r671-r675 增量窗 (前窗 r651-r670 已由 r670 英文行合并覆盖) + S6 38/38 "
    "单段 rc0 (update_fundamental 快照龄 0.2h<24h=r674 次轮指针收账毕; REPORT/LIVE-2026-10-04 再生; "
    "bm-a 心跳 stale 33min 四面 lane_io stale-takeover derive 合法 O-2100 s2.4) | 本轮同窗: orders/D-19 "
    "双扫双键 MATCH (153/153, decisions 4E5BE321 / orders 68947C17, sparse-clone 原字节配方复验) + "
    "smoke 48/48 + attrition CLEAN (bm-a healed 4 行注记照录) + 自愈 5/5 (loop pin=2 no-op/watchdog "
    "14:24 首燃/双爪在位) + 板扫 169 票 0 open (J 队列全闭线维持) | 下轮指针: trio 看护续期 + V 烧完 "
    "(~10-06 17时) = 首族 finalize 候选 (三族窗 10-06..10-08; finalize 轮必同窗池面双翻 r668 律; 判词面按"
    "冻结路径如实出) | 本地未达 origin commit 数=见 push_verify 回执\n"
)
with io.open("logs/iteration-loop/round_reports.md", "ab") as f:
    f.write(rr_line.encode("utf-8"))
print("round report appended")

# --- 4) CODELY.md pit-law append (one entry) ---
pit = (
    f"[{ts[:16]} r675 bm-b] trio watch 探针结构键位坑+窄窗速率饿死修（r674 探针 pool 腿读不存在的顶层 "
    "shards 键=三族全 NOT-FOUND 假读数，池 shards 实嵌于 entries[].shards[]；速率估读 git log -3 相邻对在 "
    "daemon 自提交密集窗 dt<0.1h 门饿死 rate=None→ETA 面瞬时空值）。How to apply：共享 JSON 态面探针写"
    "路径断言前先实探结构键位（读源 schema 亦可）；烧速率估读一律宽窗 git log -12 新旧端对距。修=results/"
    "_r675bmb_trio_watch.py（三证健康判定 k 增长+mtime+keepalive）。\n"
)
with io.open("CODELY.md", "ab") as f:
    f.write(pit.encode("utf-8"))
print("CODELY pit-law appended")
print("CLOSEOUT-WRITES OK")
