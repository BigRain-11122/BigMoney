# -*- coding: utf-8 -*-
"""r303 bm-b wrap: state.json round flip + round-report append + heartbeat refresh.

One-shot, deterministic except wall-clock faces (last_seen/epoch/clock_read/
current_task). Self-verify: json re-parse of all three files, epoch
isinstance(int), clock_read 'T' separator (R170/R178/R262 laws).
"""
import ctypes
import datetime as dt
import io
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = dt.datetime.now().astimezone().isoformat(timespec="seconds")   # +offset (R262 law)
EPOCH = int(time.time())
GPU_FREE_MB = 6949                                             # nvidia-smi sample 06:17
CPU_PCT = 0                                                    # Win32_Processor sample

# --- free RAM via GlobalMemoryStatusEx (authoritative avail phys) ---
class _MS(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
ms = _MS()
ms.dwLength = ctypes.sizeof(_MS)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms))
FREE_MB = int(ms.ullAvailPhys // (1024 * 1024))
FREE_GB = round(FREE_MB / 1024.0, 1)
GPU_GB = round(GPU_FREE_MB / 1024.0, 1)

TASK = ("r303 maintenance round (T-87 probe#16 on_track 93.9% + S6 30/30 + "
        "orders/pool/WM honest probes)")

# --- 1) state.json round flip 302 -> 303 ---
SP = os.path.join(ROOT, "logs", "iteration-loop", "state.json")
st = json.load(io.open(SP, encoding="utf-8-sig"))
st["round_no"] = 303
st["did"] = ("r303 维护轮: S0 stash->pull--rebase->pop 干净(fast-forward 4363a642->5b259090 "
             "收编 bm-a runnable_pool 更新·autofill_state stash-pop 零冲突); "
             "S0.5 orders 91/91 轮首+收尾双扫零未ack; S1 smoke 25/25; "
             "S3 T-87 探针#16 on_track 93.9%(4904/5228)@12.67/min ETA 06:39:56<周一死线 "
             "零形状缺陷(Copy-Item delta=8 全轮号面)·FUSION-GRID-P1 池件让路 bm-a 照旧零碰; "
             "S6 30/30 rc=0(audit CLEAN 零旗·WM py_low_with_work_cands=供给在途合法); "
             "post_review 零 ✗ 判决行; 迁移 v2.2 armed editor-gated 勿双 arm")
st["verdict"] = "green"
st["next"] = ("T-87 完成态复探(ETA 06:40 后 gate 收尾·~324 股尾段·attempts 自愈面); "
              "09-28 周一首新 bar 全链; 迁移窗 v2.2 armed 至 09-29 12:00")
st["last_round_ts"] = NOW
st["last_result"] = "ok"
st["current_task"] = TASK
st["updated_at"] = NOW
with io.open(SP, "w", encoding="utf-8", newline="") as f:
    f.write(json.dumps(st, ensure_ascii=False, indent=1))
chk = json.load(io.open(SP, encoding="utf-8-sig"))
assert chk["round_no"] == 303 and "+" in chk["last_round_ts"]
print("state.json round 303 ok")

# --- 2) round report append (single line, fixed fields) ---
RP = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
line = (
    NOW + " | r303 bm-b | dept:工程/数据 | "
    "WM-VERDICT: 绿 red=false lane healthy(watermark_red 06:00:13 red=false; "
    "probe 06:12:32 py_low_with_work_cands=合法供给在途:T-87 刷新网络限速构造性低 py "
    "avg 3.9% 在飞 93.9%+pool FUSION-GRID-P1 burn lane bm-a(autofill 06:10:01 tick "
    "claim_lost_yield 设计让路面)·板 32 票全 claimed 0 open·bandit 0·无违令) | "
    "did: S0 stash->pull--rebase->pop 干净(fast-forward 4363a642->5b259090 收编 bm-a "
    "runnable_pool FUSION-GRID-P1 ready 面更新·autofill_state stash-pop 零冲突); "
    "S0.5 orders 91/91 轮首+收尾双扫零未ack·decisions 直扫 bm-b 无集团仓 clone 不可达"
    "如实注记 R291 镜面=fleet/orders 零差集; S1 smoke 25/25; S2 板 32 票全 claimed 零 open+"
    "job_list 0+水位红牌 red=false(next_pick=moneyflow IC claimed·panel 源阻断 30min 自愈面); "
    "S3 T-87 探针#16 on_track 93.9%(4904/5228)@12.67/min ETA 06:39:56<周一 09:15 死线·"
    "at_cutoff 4893/4904·header/ohlc 零缺陷·last_refresh 06:05 快照 fails=10/4850 未触熔断·"
    "冻结血统 Copy-Item+replace 仅轮号面+difflib delta=8 复核(r298 坑律); FUSION-GRID-P1 "
    "池件让路 bm-a 照旧(burn lane=bm-a·r302 定谳·本机零碰); S6 30/30 legs rc=0"
    "(_r303bmb_s6_chain.ps1 Copy-Item delta=2 轮号面:audit v2.3 CLEAN 零旗·regime ORANGE "
    "shadow breadth 0.77·update_daily 周末零新行合法·update_lhb <30min 节流 no-op·"
    "update_heat 周末 no-op·update_futures cutoff 覆盖零网络·astock lock-alive no-op·"
    "bm-a/bm-c 车道 stdout-only 诚实 no-op·fundamental 7.9h 新鲜跳过·b_layer verdict 再生·"
    "live.paper OK·t35v PASS 零 pending·t24 22/22 drift 0·promo 0/22·aggr/alloc/grid 幂等 "
    "no-op·export 09-24 再生·daily_report faces=4 token=1); 迁移 v2.2 journal armed "
    "editor-gated(T-87 刷新进程占柄=车道班次设计面·勿双 arm·窗至 09-29 12:00); "
    "post_review 零 ✗ 判决行(2 处命中全为协议描述文本); S7 inbox 零未读(五件皆前轮已 "
    "processed)·schtasks 三任务在役 CSV 口径(IterationLoop 正在运行=本轮·Autofill 06:20 "
    "就绪·Watchdog 06:30 就绪·R49)·state/heartbeat 303 epoch int 自证 | "
    "evidence: results/_r303bmb_astock_pass_probe.py+json(#16 on_track·difflib 取证)+"
    "_r303bmb_s6_chain.ps1+results/_r303bmb_s6_chain.log(30/30 rc=0)+smoke 25/25+"
    "orders 91/91 双扫 | next: T-87 完成态复探(ETA 06:40 后 gate 收尾·~324 股尾段·"
    "attempts 自愈)·FUSION-GRID bm-a 烧批落地后 harvest 三件套归 bm-a 车道·09-28 周一"
    "首新 bar 全链(update_daily->live.paper->t35v->t24x2->aggr->grid 5 账首拍唤醒->"
    "export->scorecard->daily_report)·迁移窗 v2.2 armed editor-gated 至 09-29 12:00 勿双 arm"
)
raw = io.open(RP, "r", encoding="utf-8").read()
add_nl = "" if (not raw or raw.endswith("\n")) else "\n"
with io.open(RP, "a", encoding="utf-8", newline="") as f:
    f.write(add_nl + line + "\n")
print("round_reports.md +1 line ok")

# --- 3) heartbeat fleet/machines/bm-b.json ---
HB = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
hb = json.load(io.open(HB, encoding="utf-8-sig"))
hb["last_seen"] = NOW
hb["heartbeat_epoch_utc"] = EPOCH
hb["clock_read"] = NOW
hb["current_task"] = TASK
hb["cpu_cores"] = 16
hb["free_ram_gb"] = FREE_GB
hb["gpu_free_vram_gb"] = GPU_GB
hb["cpu_util_pct"] = CPU_PCT
hb["round_no"] = 303
hb["verdict"] = "green"
hb["cores"] = 16
hb["idle_ram_gb"] = FREE_GB
hb["gpu_free_vram_mb"] = GPU_FREE_MB
hb["idle_ram_mb"] = FREE_MB
hb["gpu_idle_vram_mb"] = GPU_FREE_MB
hb["gpu_idle_vram_gb"] = GPU_GB
hb["cpu_pct"] = CPU_PCT
hb["round"] = 303
hb["free_ram_mb"] = FREE_MB
with io.open(HB, "w", encoding="utf-8", newline="") as f:
    f.write(json.dumps(hb, ensure_ascii=False, indent=1))
v = json.load(io.open(HB, encoding="utf-8-sig"))
assert isinstance(v["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178)"
assert "T" in v["clock_read"] and "+" in v["clock_read"], "clock_read T-sep law (R262)"
assert v["round_no"] == 303
print("heartbeat ok: epoch=%d int, clock=%s, free_ram=%sGB gpu=%sMB" % (
    v["heartbeat_epoch_utc"], v["clock_read"], FREE_GB, GPU_FREE_MB))
