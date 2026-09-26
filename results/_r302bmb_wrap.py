# -*- coding: utf-8 -*-
"""r302 bm-b wrap: state.json round flip + round-report append + heartbeat refresh.

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
GPU_FREE_MB = 6942                                             # nvidia-smi sample 06:06
CPU_PCT = 30                                                   # Win32_Processor sample

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

TASK = ("r302 maintenance round (T-87 probe#15 on_track 91.2% + S6 30/30 "
        "+ autofill_state UU canon resolve)")

# --- 1) state.json round flip 301 -> 302 ---
SP = os.path.join(ROOT, "logs", "iteration-loop", "state.json")
st = json.load(io.open(SP, encoding="utf-8-sig"))
st["round_no"] = 302
st["did"] = ("r302 维护轮: S0 stash->rebase->pop 收编 bm-a r296-r298(64023a42+370feea9)·"
             "autofill_state 单件 UU 冻结正典解(union 50|50->51 cap50 弃最旧1·"
             "last_tick=bm-b 06:00:01 claim_lost_yield 保真); S0.5 orders 91/91 双扫零未ack; "
             "S1 smoke 25/25; S3 T-87 探针#15 on_track 91.2%(4766/5228)@12.65/min "
             "ETA 06:40:24<周一死线 零形状缺陷(delta=10 全轮号面)·FUSION-GRID-P1 池件认领竞速"
             "让路 bm-a(claim_lost_yield=设计面·bm-a r297 崩溃修复+重发·零碰); "
             "S6 30/30 rc=0(audit CLEAN 零旗·WM probe py_low_with_work_cands=供给在途合法); "
             "post_review 13/13 NO 全翻绿零开; 迁移 v2.2 armed editor-gated 勿双 arm")
st["verdict"] = "green"
st["next"] = ("T-87 完成态复探(ETA 06:40 后 gate 收尾·462 股尾段·attempts 自愈面); "
              "09-28 周一首新 bar 全链; 迁移窗 v2.2 armed 至 09-29 12:00")
st["last_round_ts"] = NOW
st["last_result"] = "ok"
st["current_task"] = TASK
st["updated_at"] = NOW
with io.open(SP, "w", encoding="utf-8", newline="") as f:
    f.write(json.dumps(st, ensure_ascii=False, indent=1))
chk = json.load(io.open(SP, encoding="utf-8-sig"))
assert chk["round_no"] == 302
print("state.json round 302 ok")

# --- 2) round report append (single line, fixed fields) ---
RP = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
line = (
    NOW + " | r302 bm-b | dept:工程/数据 | "
    "WM-VERDICT: 绿 red=false lane healthy(probe 06:04:30 py_low_with_work_cands="
    "合法供给在途:T-87 刷新网络限速构造性低 py 4.6% 在飞 91.2%+pool FUSION-GRID-P1 "
    "已 bm-a 认领重发中·板 32 票全 claimed 0 open·bandit 0·无违令) | "
    "did: S0 stash->rebase->pop 收编 bm-a r296-r298(64023a42 FUSION-GRID 崩溃修复+"
    "370feea9 wrap)·autofill_state 单件 UU 按冻结正典解析器解(launches union 50|50->51 "
    "cap50 弃最旧 BOND-PANEL-SHARD-0·last_tick 同秒 bm-b 06:00:01 claim_lost_yield>bm-a "
    "05:50:01 保真 r140/r215/r223·difflib delta=6 全 docstring 轮号面·r296 坑律续执行); "
    "S0.5 orders 91/91 轮首+收尾双扫零未ack·decisions 直扫 bm-b 无集团仓 clone 不可达"
    "如实注记 R291 镜面=fleet/orders 零差集; S1 smoke 25/25; S2 板 32 票全 claimed 零 open+"
    "job_list 0+水位红牌 red=false; S3 T-87 探针#15 on_track 91.2%(4766/5228)@12.65/min "
    "ETA 06:40:24<周一 09:15 死线·at_cutoff 4755/4766·header/ohlc 零缺陷·attempts 9 只全 "
    "1 次零隔离(下轮 spawn 自愈面)·冻结血统 Copy-Item+replace 仅轮号面+difflib delta=10 "
    "复核(r298 坑律); FUSION-GRID-P1 池件让路 bm-a(autofill 06:00:01 tick "
    "claim_lost_yield=设计让路面·bm-a r297 已闭环 05:50 首烧 KeyError sharpe_full 崩+"
    "B7b 契约腿正典+06:10 tick 重发·烧批归 bm-a 车道本机零碰); S6 30/30 legs rc=0"
    "(_r302bmb_s6_chain.ps1 Copy-Item delta=2 轮号面:audit v2.3 CLEAN 零旗 "
    "pool_starvation 清除=pool-supply-gap·regime ORANGE shadow breadth 0.77·update_daily "
    "周末零新行合法·astock lock-alive no-op·bm-a/bm-c 车道 stdout-only 诚实 no-op·"
    "fundamental 7.8h 新鲜跳过·live.paper OK·t35v PASS 零 pending·t24 22/22 drift 0·"
    "promo 0/22·aggr/grid 幂等 no-op·export 09-24 再生·daily_report faces=4 token=1·"
    "token L2=0); 迁移 v2.2 journal 健康 precheck waiting(editor 三进程仍拦+T-87 刷新"
    "进程占柄=车道班次设计面·勿双 arm·窗至 09-29 12:00); post_review 13/13 NO 全翻绿"
    "零开; S7 inbox 零未读·schtasks 三任务在役 CSV 口径(IterationLoop 正在运行=本轮·"
    "Autofill 06:10 就绪·Watchdog 06:30 就绪·R49)·state/heartbeat 302 epoch int 自证 | "
    "evidence: results/_r302bmb_astock_pass_probe.py+json(#15 on_track·difflib 取证)+"
    "results/_r302bmb_resolve.py(autofill_state UU 正典解)+_r302bmb_s6_chain.ps1+"
    "results/_r302bmb_s6_chain.log(30/30 rc=0)+smoke 25/25+orders 91/91 双扫 | "
    "next: T-87 完成态复探(ETA 06:40 后 gate 收尾·462 股尾段·attempts 自愈)·"
    "FUSION-GRID bm-a 烧批落地后 harvest 三件套归 bm-a 车道·09-28 周一首新 bar 全链"
    "(update_daily->live.paper->t35v->t24x2->aggr->grid 5 账首拍唤醒->export->scorecard->"
    "daily_report)·迁移窗 v2.2 armed editor-gated 至 09-29 12:00 勿双 arm"
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
hb["round_no"] = 302
hb["verdict"] = "green"
hb["cores"] = 16
hb["idle_ram_gb"] = FREE_GB
hb["gpu_free_vram_mb"] = GPU_FREE_MB
hb["idle_ram_mb"] = FREE_MB
hb["gpu_idle_vram_mb"] = GPU_FREE_MB
hb["gpu_idle_vram_gb"] = GPU_GB
hb["cpu_pct"] = CPU_PCT
hb["round"] = 302
hb["free_ram_mb"] = FREE_MB
with io.open(HB, "w", encoding="utf-8", newline="") as f:
    f.write(json.dumps(hb, ensure_ascii=False, indent=1))
v = json.load(io.open(HB, encoding="utf-8-sig"))
assert isinstance(v["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178)"
assert "T" in v["clock_read"] and "+" in v["clock_read"], "clock_read T-sep law (R262)"
print("heartbeat ok: epoch=%d int, clock=%s, free_ram=%sGB gpu=%sMB" % (
    v["heartbeat_epoch_utc"], v["clock_read"], FREE_GB, GPU_FREE_MB))
