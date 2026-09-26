# -*- coding: utf-8 -*-
"""r305 bm-b wrap: state.json round flip + round-report append + heartbeat
refresh. One-shot, deterministic except wall-clock faces. Self-verify:
json re-parse of all three files, epoch isinstance(int), clock_read
'T'+offset (R170/R178/R262 laws)."""
import ctypes
import datetime as dt
import io
import json
import os
import time
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = dt.datetime.now().astimezone().isoformat(timespec="seconds")   # +offset
EPOCH = int(time.time())
GPU_FREE_MB = 6944                                             # nvidia-smi 06:53
CPU_PCT = 3                                                    # Win32_Processor 06:53

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

TASK = ("r305: T-87 first-pull settled (pass_complete 5217/5228, quarantined "
        "11, settled 12, gate no-op fresh) + settle-law 3-fix + py_watermark "
        "lock-face fix + S6 30/30 + 5x HANDOVER")

# --- 1) state.json round flip 304 -> 305 ---
SP = os.path.join(ROOT, "logs", "iteration-loop", "state.json")
st = json.load(io.open(SP, encoding="utf-8-sig"))
st["round_no"] = 305
st["did"] = ("r305: S0 stash->pull--rebase->pop 干净(Already up to date); "
             "S0.5 orders 91/91 双扫零未ack(_r305bmb_orders_diff.py 双向全差集·"
             "decisions 直扫不可达 R291 如实注记); S1 smoke 25/25; S2 零 open 票+"
             "job_list 0+红牌 red=false; S3 T-87 首拉收口全弧=探针#18 末段在飞->"
             "06:40:11 pass ended 5217/5228->完成态探针 pass_complete·11 股三振 "
             "quarantine+12 股停牌短尾 settle·settle 律缺口三修(suspended-settle "
             "面+load_progress 携带修+bytes-cutoff 优先·selftest 全过)·manual "
             "cycles 3-8 收口·06:52 稳态 complete=true/cutoff 2026-09-24/gate "
             "no-op 零网络·py_watermark local_batch_running 锁面修复(0.5 核 CPU "
             "阈恒漏检网络限速 pass→假 idle·修=锁面纳入+selftest 23 腿)·"
             "post_review 开放负判定 per-id 解析=0 开口·T-87 票+progress_r305_bmb; "
             "S6 30/30 rc=0(audit CLEAN 零旗·池 56/56 done); 5x 核对=HANDOVER "
             "L4 级联6层+尾窗 r305 行·统一链 200,396->202,441 实读(+2,045=bm-a "
             "FUSION_GRID_P1 判负批·75 件 0 平衡败); 迁移 v2.2 armed 勿双 arm")
st["verdict"] = "green"
st["next"] = ("09-28 周一首新 bar 全链(update_daily->live.paper->t35v->t24x2->"
              "aggr->grid 首拍->export->scorecard->daily_report)+T-87 周一 15:30 "
              "后首次日续拉实弹(全宇宙分离 fetch ~3.5h by-design·settled 重臂自愈)"
              "+10-01 月度三件套+迁移窗 v2.2 armed 至 09-29 12:00+R310 下次 5x 核对")
st["last_round_ts"] = NOW
st["last_result"] = "ok"
st["current_task"] = TASK
st["updated_at"] = NOW
with io.open(SP, "w", encoding="utf-8", newline="") as f:
    f.write(json.dumps(st, ensure_ascii=False, indent=1))
chk = json.load(io.open(SP, encoding="utf-8-sig"))
assert chk["round_no"] == 305 and "+" in chk["last_round_ts"]
print("state.json round 305 ok")

# --- 2) round report append (single line, fixed fields) ---
RP = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
line = (
    NOW + " | r305 bm-b | dept:工程/数据 | "
    "WM-VERDICT: 绿 red=false lane healthy(watermark_red 06:30:14 red=false; "
    "probe 06:36:31 post-fix honest py_low_with_work_cands=T-87 供给在飞网络"
    "限速构造性低 py 2.1%·r305 修复=py_watermark local_batch_running 锁面纳入"
    "〔data/*/_refresh.lock 活 pid〕+refresh_lock_lanes 披露+selftest 21->23 腿="
    "网络限速 detached pass 0.36 核<0.5 CPU 阈恒漏检实证·06:33:05 旧口径 "
    "py_low_board_clear 假 idle 留档 append-only 不改·06:52 收口后真稳态=板清+"
    "零批合法 idle) | "
    "did: S0 stash->pull--rebase->pop 干净(Already up to date 零新远端); "
    "S0.5 orders 91/91 轮首+收尾双扫零未ack·_r305bmb_orders_diff.py 双向全差集"
    "器(文件面91=ack面91 零ghost)·集团 decisions.md 直扫 bm-b 无集团仓 clone 不可达"
    "如实注记 R291 镜面=fleet/orders 零差集; S1 smoke 25/25; S2 板 0 open(status="
    "open 全 grep 零命中)+job_list 0+水位红牌 red=false(next_pick=moneyflow IC="
    "claimed·panel 源阻断 30min 自愈面·advisory only); S3 T-87 首拉收口全弧="
    "探针#18 末段在飞 5144/5228@12.69/min ETA 06:39:17(冻结血统 Copy-Item+replace "
    "轮号面+difflib delta=2/8 复核 r298 坑律)→06:40:11 pass ended 5217/5228·"
    "完成态探针新面 pass_complete·11 股三振 quarantine(000019 停牌+001235/001246+"
    "301xxx/688xxx/689009 新股相)+12 股停牌短尾 settle·**settle 律设计缺口三修**"
    "〔fetch-success attempts.pop→quarantine 永不可达→complete 结构性不可达+gate "
    "30min 无限 spawn 环〕=suspended-settle 面(同 cutoff>=3 周期离 todo·新 cutoff "
    "重臂=复牌股自愈·selftest 腿齐)+load_progress 白名单携带修(settle 计数每周期"
    "归1实弹定谳)+panel cutoff bytes-derive 优先(setle-only 周期免盖滞后戳)·manual "
    "refresh cycles 3-8(操作员周期越过 30min gate 节流·~60 请求 2.5s·披露)·06:52 "
    "稳态=complete true/cutoff 2026-09-24/universe 5228/per_files 5217/quarantined "
    "11/settled 12·gate no-op panel-fresh 零网络·smoke 25/25 双补丁后复跑·T-87 票 "
    "+progress_r305_bmb 行(_r305bmb_ticket_progress.py); py_watermark 锁面修复"
    "(scripts/py_watermark.py: _refresh_locks_alive+_pid_alive+work_cands 纳入+"
    "selftest 23 腿·活探针 refresh_lock_lanes=[astock_daily]); post_review 开放"
    "负判定 per-id 解析器(_r305bmb_postreview_pool.py)=0 开口(13 历史 NO 皆同 id "
    "后续 YES 翻绿·WAIT 551 皆旧轮在案); S6 30/30 legs rc=0(_r305bmb_s6_chain.ps1 "
    "Copy-Item delta=2 轮号面:audit v2.3 CLEAN 零旗 hist201·regime ORANGE shadow "
    "breadth 0.77·update_daily 周末合法·lhb <30min 节流·heat 周末 no-op·futures "
    "cutoff 覆盖零网络·bm-a/bm-c 车道 stdout-only 诚实 no-op·fundamental 8.2h 新鲜"
    "跳过·b_layer verdict 再生·live.paper OK·t35v PASS 零 pending·t24 22/22 drift "
    "0·promo 0/22·aggr/alloc/grid 幂等 no-op·export 09-24 再生·daily_report "
    "faces=4 token=1·池 56/56 done 零可认领); 5x 核对=HANDOVER L4 级联 6 层+尾窗 "
    "r305 行·统一链 200,396->202,441 实读(+2,045=bm-a FUSION_GRID_P1 判负批·"
    "INTERNAL_BALANCE_FAIL=0·75 件·_r295bmb_ledger_scan 复跑); 迁移 v2.2 journal "
    "armed editor-gated(Tuanjie 编辑器 3 进程+旧根 cwd-holder 在拦·车道照跑·勿双 "
    "arm·窗至 09-29 12:00); S7 inbox 零未读·schtasks 三任务在役 CSV 口径"
    "(IterationLoop running=本轮·Autofill 06:40 就绪·Watchdog 07:00 就绪·R49)·"
    "state/heartbeat 305 epoch int 自证 | "
    "evidence: _r305bmb_astock_completion_probe.py+json(pass_complete·四探针弧 "
    "06:35/06:40/06:44/06:52)+_r305bmb_astock_pass_probe.py+json(#18)+_r305bmb_s6_"
    "chain.ps1+log(30/30 rc=0)+_r305bmb_lineage_copy.py(delta 2/8/2)+_r305bmb_"
    "orders_diff.py+json(91/91)+_r305bmb_postreview_pool.py(0 开口)+_r305bmb_"
    "ticket_progress.py+scripts/py_watermark.py(selftest 23 腿)+scripts/update_"
    "astock_daily.py(selftest 全过)+smoke 25/25x2+_r295bmb_ledger_scan.py(HEAD "
    "202,441) | next: 09-28 周一首新 bar 全链(update_daily->live.paper->t35v->"
    "t24x2->aggr->grid 首拍唤醒->export->scorecard->daily_report)+T-87 周一 "
    "15:30 后首次日续拉实弹(全宇宙分离 fetch ~3.5h by-design·settled 重臂自愈·"
    "r306+ 车道探针接力)+10-01 月度三件套+REGIME_GUARD v3 日期门+迁移窗 v2.2 "
    "armed 至 09-29 12:00 勿双 arm+R310 下次 5x 核对"
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
hb["round_no"] = 305
hb["verdict"] = "green"
hb["cores"] = 16
hb["idle_ram_gb"] = FREE_GB
hb["gpu_free_vram_mb"] = GPU_FREE_MB
hb["idle_ram_mb"] = FREE_MB
hb["gpu_idle_vram_mb"] = GPU_FREE_MB
hb["gpu_idle_vram_gb"] = GPU_GB
hb["cpu_pct"] = CPU_PCT
hb["round"] = 305
hb["free_ram_mb"] = FREE_MB
with io.open(HB, "w", encoding="utf-8", newline="") as f:
    f.write(json.dumps(hb, ensure_ascii=False, indent=1))
v = json.load(io.open(HB, encoding="utf-8-sig"))
assert isinstance(v["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178)"
assert "T" in v["clock_read"] and "+" in v["clock_read"], "clock_read T-sep law (R262)"
assert v["round_no"] == 305
print("heartbeat ok: epoch=%d int, clock=%s, free_ram=%sGB gpu=%sMB" % (
    v["heartbeat_epoch_utc"], v["clock_read"], FREE_GB, GPU_FREE_MB))
