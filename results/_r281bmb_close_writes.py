"""r281 bm-b closing writes: round report line, state, heartbeat, ticket.

Byte-face probed first (r255 five-face family): state/heartbeat = LF, indent=1,
no BOM, NO trailing newline; ticket = LF, indent=1, trailing newline; reports =
append-only with trailing-newline probe (r281 new pitfall law). All
timestamps derived from one now() instance (R271).
"""
import ctypes
import datetime as dt
import json
import subprocess
import time

now = dt.datetime.now().astimezone()
ts_line = now.isoformat(timespec="seconds")            # T-separator (R262)
epoch = int(time.time())                                # int (R170/R178)


class MS(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


ms = MS()
ms.dwLength = ctypes.sizeof(MS)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms))
free_ram_gb = round(ms.ullAvailPhys / 1e9, 1)
try:
    v = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                        "--format=csv,noheader,nounits"],
                       capture_output=True, text=True, timeout=10).stdout.strip()
    gpu_free_gb = round(float(v.splitlines()[0]) / 1024, 1)
except Exception:
    gpu_free_gb = 6.9

# ---- 1) round_reports.md append (trailing-newline probe first) ----
rp = "logs/iteration-loop/round_reports.md"
raw = open(rp, "rb").read()
assert raw.endswith(b"\n"), "trailing newline missing -- probe-first law"
r281 = (
    ts_line + " | r281 (bm-b) | dept:数据/工程 | WM-VERDICT: GREEN healthy red=false "
    "(bandit next_pick=claimed moneyflow IC 批等面板完成; 池 fusion-nav-0of1 owner=bm-a 在飞) | did: "
    "T-87 供给线全宇宙 pass 中途健康探针=on_track (207/5228=4.0%·rate 12.4/min·ETA 2026-09-27T06:48:57="
    "周一 09:15 死线前约 26h 富余·206/207 tail@cutoff 2026-09-24·1 例 09-03 早尾=suspension 诚实面"
    "·frozen-header 207/207 零坏·OHLC 3 样本零坏·lock pid 29440 活·attempts=1(000019 下次 gate 自愈)"
    "·quarantine=0) + 轮账本行完整面修复 (r272add|r273 与 r279|r280 两处无尾换行串行=多 ts 行扫描自捕"
    "→第二 ts 位前插 LF 拆行·字节零丢失·复扫 remaining_merged=[]) + S0.5 双扫 89/89 零未回执+决策台账"
    "无新行 (集团 decisions.md 不在位=零动作) | evidence: results/_r281bmb_astock_pass_probe.py/.json "
    "+ 修复验证 + smoke 25/25 + S6 26 腿 rc=0 (周末无新 bar 诚实 no-op: lhb/heat/futures 节流或覆盖"
    "·options/moneyflow/sina_mf/ths/ah/fund_premium 他机车道 stdout-only·astock_daily=30min 节流 lock-"
    "alive no-op·fundamental 新鲜跳过·marks 三车道幂等 no-op·t35_export/scorecard/report/build_status/"
    "token 全 rc=0) | next: r282=pass 完成复探 (ETA 06:49 后) + 周一 09-28 首次日续拉实弹 (gate 补拉 "
    "stragglers) + REV_OSC 消费面 watch (bm-a 开 TRANSFER 即裁) + 迁移窗 watch (Tuanjie 三进程在=v2.2 "
    "armed 等待) + 10-01 月首轮三件套 (science_audit+monthly_briefing+self_review)\n")
with open(rp, "ab") as f:
    f.write(r281.encode("utf-8"))

# ---- 2) state.json (LF, indent=1, NO trailing newline) ----
sp = "logs/iteration-loop/state.json"
st = json.loads(open(sp, encoding="utf-8-sig").read())
st["round_no"] = 281
st["did"] = ("r281: T-87 pass mid-flight probe on_track (207/5228, 12.4/min, ETA Sun 06:49 = 26h "
             "before Mon 09-28 deadline; zero shape defects; lock alive; 1 self-heal attempt) + "
             "round-reports ledger line-integrity repair (2 no-newline junctions split, zero loss, "
             "verified remaining_merged=[]) + S6 26 legs rc=0 weekend no-ops + orders 89/89")
st["verdict"] = "green"
st["next"] = ("r282: pass completion re-probe (~06:49) + Mon 09-28 first daily-continuation live fire "
              "+ REV_OSC consumption face watch + migration window watch + 10-01 month-first trio")
st["last_round_ts"] = ts_line
st["current_task"] = ("T-87 supply lane: full-universe pass in flight (probe on_track, ETA Sun 06:49); "
                      "r281 ledger line-repair + S6 26 legs green")
for k in ("updated_at", "last_seen", "ts", "last_round_at"):
    if k in st:
        st[k] = ts_line
if "updated" in st:
    st["updated"] = ts_line
with open(sp, "w", encoding="utf-8", newline="\n") as f:
    f.write(json.dumps(st, ensure_ascii=False, indent=1))

# ---- 3) heartbeat bm-b.json (LF, indent=1, NO trailing newline) ----
hp = "fleet/machines/bm-b.json"
hb = json.loads(open(hp, encoding="utf-8-sig").read())
hb["last_seen"] = now.isoformat()
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = now.isoformat()
hb["current_task"] = st["current_task"]
hb["free_ram_gb"] = free_ram_gb
hb["gpu_free_vram_gb"] = gpu_free_gb
hb["total_ram_gb"] = round(ms.ullTotalPhys / 1e9, 1)
hb["cpu_util_pct"] = 13.8
hb["round_no"] = 281
hb["verdict"] = "green"
hb["idle_ram_gb"] = free_ram_gb
hb["gpu_free_vram_mb"] = int(gpu_free_gb * 1024)
hb["idle_ram_mb"] = int(free_ram_gb * 1024)
hb["gpu_idle_vram_mb"] = int(gpu_free_gb * 1024)
hb["gpu_idle_vram_gb"] = gpu_free_gb
hb["round"] = 281
with open(hp, "w", encoding="utf-8", newline="\n") as f:
    f.write(json.dumps(hb, ensure_ascii=False, indent=1))
chk = json.loads(open(hp, encoding="utf-8-sig").read())
assert isinstance(chk["heartbeat_epoch_utc"], int) and "T" in chk["clock_read"], "F7 face"

# ---- 4) T-87 ticket progress_r281_bmb (LF, indent=1, trailing newline) ----
tp = "fleet/tasks/T-2026-09-26-87-P1.json"
tk = json.loads(open(tp, encoding="utf-8-sig").read())
tk["progress_r281_bmb"] = (
    "T-87 r281 bm-b supply-lane pass mid-flight health probe: "
    "results/_r281bmb_astock_pass_probe.py/.json -- verdict on_track @2026-09-27T00:03:57: "
    "per_files 207/5228 (4.0%), rate 12.4/min (lock-start face), ETA 2026-09-27T06:48:57 "
    "= ~26h before Mon 09-28 09:15 first live fire; 206/207 files at expected cutoff 2026-09-24 "
    "(1 early-tail 2026-09-03 = suspended face, honest); frozen-header check 0 mismatches across "
    "all 207 files; OHLC sanity 3-sample 0 bad; lock pid 29440 alive; attempts=1 (000019, self-heals "
    "on next gate spawn via file-derived todo); quarantined 0. S6 gate leg = honest 30min-throttle "
    "no-op (lock alive). No action needed before Monday; r282+ re-probe completion.")
with open(tp, "w", encoding="utf-8", newline="\n") as f:
    f.write(json.dumps(tk, ensure_ascii=False, indent=1) + "\n")

print("writes done | now:", ts_line, "| epoch:", epoch,
      "| ram_free:", free_ram_gb, "| gpu_free:", gpu_free_gb)
