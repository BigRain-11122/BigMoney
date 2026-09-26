# -*- coding: utf-8 -*-
"""r306 bm-b wrap: state.json round flip + round-report append + heartbeat
refresh. Lineage: r305 wrap (post-R302 astimezone/T-sep laws). Self-verify:
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
GPU_FREE_MB = 6969                                             # nvidia-smi 07:2x
CPU_PCT = 2                                                    # Win32_Processor 07:2x

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

TASK = ("r306: R293 crash-salvage of r305 interrupted push-rebase (2 collision "
        "batches 28+30 UU resolved canonical, rebase completed 7df7a767, push "
        "landed) + S6 30/30 + orders 91/91 double-scan + kenglu rebase-continue "
        "unstaged-delta gate")

# --- 1) state.json round flip 305 -> 306 ---
SP = os.path.join(ROOT, "logs", "iteration-loop", "state.json")
st = json.load(io.open(SP, encoding="utf-8-sig"))
st["round_no"] = 306
st["did"] = ("r306: 轮首命中 R293 崩溃打捞态=r305 push-rejected 后 06:54:41 "
             "pull--rebase 中途会话亡(28 UU 搁浅·进程扫描零活主+IgnoreNew 发射"
             "自证)·liveness 定谳后独占续作·批次1 28件(classifier 12 GREEN+16 "
             "hand-qualified deepdiff=23 take-new by ts+2 dashboard 本机侧+2 "
             "union+1 mixed·零丢失门全过)·rebase --continue 被 'You must edit "
             "all merge conflicts' 拒而 ls-files -u=0·定谳=被重放提交外 tracked "
             "件未暂存 worktree 增量(p1d_gates 07:00 后台短命写手)触发同文案误"
             "导·正典=cp 增量->checkout 该件->continue->回移·448a972f 落地; push "
             "再拒(bm-a r300 a4c0e3d4 同窗落)·重试律 batch2 30件(+HANDOVER anchor-"
             "insert 双 5x 行 ts 序+runnable_pool A⊃B 超集+dashboard r301 先例 "
             "pool-ready 集成面取 ours+lhb overlap 富面+白名单扩 2 键)·7df7a767 "
             "落地·push 成功 a4c0e3d4..7df7a767 main; S0.5 orders 91/91 双扫零未"
             "ack(R291 注记); S1 smoke 25/25; S2 板 0 open+job_list 0+红牌 "
             "red=false 绿; S6 30/30 rc=0(冻结血统 r305 chain Copy-Item delta=1 "
             "轮号面+3 diff 工件); inbox MSG-0645 bm-a F-04 声明处理归档(队列#4 "
             "已被 r299 冻结+r300 runner 建成·池 ready=1·与 bm-b 车道零冲突)")
st["verdict"] = "green"
st["next"] = ("09-28 周一首新 bar 全链(update_daily->live.paper->t35v->t24x2->"
              "aggr->grid 首拍->export->scorecard->daily_report)+T-87 周一 15:30 "
              "后首次日续拉实弹+CN-SECTOR-LEADER-P1 判决批 autofill 自续(池 "
              "ready=1·bm-a 车道)+10-01 月度三件套+REGIME_GUARD v3 日期门+迁移窗 "
              "v2.2 armed 至 09-29 12:00 勿双 arm+R310 下次 5x 核对")
st["last_round_ts"] = NOW
st["last_result"] = "ok"
st["current_task"] = TASK
st["updated_at"] = NOW
with io.open(SP, "w", encoding="utf-8", newline="") as f:
    f.write(json.dumps(st, ensure_ascii=False, indent=1))
chk = json.load(io.open(SP, encoding="utf-8-sig"))
assert chk["round_no"] == 306 and "+" in chk["last_round_ts"]
print("state.json round 306 ok")

# --- 2) round report append (single line, fixed fields) ---
RP = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
line = (
    NOW + " | r306 bm-b | dept:舰队/工程 | "
    "WM-VERDICT: 绿 red=false lane healthy(watermark_red 07:00:13 red=false; "
    "S6 probe 复跑 rc=0;池 CN-SECTOR-LEADER-P1 ready=1 autofill 自续面·板清 "
    "py 低位合法 idle 白名单=池在飞 batch 由 watchdog C8 拥有 spawn) | "
    "did: R293 崩溃打捞轮=r305 wrap 06:53:47 后 push 拒->06:54:41 pull--rebase "
    "conflict 中途会话亡(28 UU 搁浅·rebase-merge msgnum1/1 todo 空)·liveness 三"
    "证=进程扫描(Bigmoney codely 唯一=本会话 PID3808 07:00:02·其余=启动链 29148/"
    "21796+迁移 watcher 28696 设计在役)+IgnoreNew 发射自证+state round_no 305 停"
    "更·定谳=崩溃非在飞→独占续作禁退避养脏; 批次1(28 UU)=classifier 12 GREEN+16 "
    "UNKNOWN hand-qualified(_r306bmb_deepdiff: 全部=确定性再 derive 派生面 ts 漂"
    "移·paper x6/export x2/REPORT/scorecards/prospect x2/status 群=strip 白名单"
    "等值断言后 take-new by ts·dashboard x2=本机侧整字节·compute_audit 201|201"
    "->202 union 双机样本零丢·x2_watch 522|528->534·autofill launches 50|50->"
    "union52 cap50 ASC·last_tick inner-ts 取新·crash_counted 富变体保全[unioncheck "
    "复核: A 内 4 重复+2 富 vs B 6 plain·并集数学定谳])·**rebase --continue 拒因 "
    "定谳**=被重放提交外 tracked 件带未暂 worktree 增量(p1d_gates.json MM·后台短"
    "命写手 07:00:12 落 07:00 面)时 git 2.55 以 'You must edit all merge conflicts' "
    "同一文案拒绝(GIT_TRACE built-in 后零子命令即死+trace2 死点=read_index+"
    "refresh 后=worktree 洁净门非 unmerged 门·ls-files -u=0 证)·正典=cp 增量->"
    "git checkout -- 该件->continue->回移增量=零丢失·448a972f 成; push 再拒="
    "bm-a r300 a4c0e3d4 同窗落(runner CN_SECTOR_LEADER_P1 built+gated+池 ready=1)"
    "→按律 pull--rebase 重试一次=批次2(30 UU=+HANDOVER anchor-insert 双 5x 行 "
    "实钟序保全 r210 零行丢+runnable_pool entries 57⊃56 超集取整(A-only=CN-SECTOR-"
    "LEADER-P1 池新面)+dashboard x2 r301 先例=pool-ready 集成面取 ours 整字节+"
    "lhb update 富面 overlap 键取 ours+白名单扩 digests_landed_24h/prereg_md_"
    "touched_24h 2 键 23 take-new 全 ours 07:0x>06:3x+union 201|202->203/x2 "
    "528 基->540 extra12+autofill last_tick ours 07:00:01)·7df7a767 成·push 落"
    "地 a4c0e3d4..7df7a767 main; S0.5 orders 91/91 轮首扫+收尾双扫零未ack(_r305bmb_"
    "orders_diff 复用·decisions 直扫不可达 R291 如实注记); S1 smoke 25/25; S2 板 "
    "0 open+job_list 0+next_pick moneyflow IC=claimed advisory; inbox MSG-"
    "20260927-0645 bm-a F-04 声明处理归档 processed/(队列#4 声明合法·已被 r299 "
    "冻结 b3d72924+r300 runner 建成+池 ready=1·与 bm-b 车道零冲突·本轮已在对撞"
    "解决中实证其产物全量入树); S6 30/30 legs rc=0(_r306bmb_s6_chain.ps1 冻结血"
    "统 Copy-Item+replace 轮号面·difflib delta=1 内容行 r298 坑律:audit CLEAN·"
    "regime ORANGE shadow·t35v PASS 零 pending·t24 22/22 drift 0·promo 0/22·"
    "aggr/alloc/grid 幂等 no-op·export/scorecard/daily_report 再生·bm-a/bm-c "
    "车道 stdout-only 诚实 no-op); post_review per-id 复扫零开口; kenglu S4 入 "
    "CODELY(rebase-continue unstaged-delta 门+误导文案定谳) | "
    "evidence: _r306bmb_resolve.py+resolve2.py(28+30 件全过门含零丢失/strip 等"
    "值/cap-oldest 断言)+_r306bmb_probe_conflicts/deepdiff/dashdiff/probe2/"
    "unioncheck.py(逐件 hand-qualify 定谳面)+_r306bmb_s6_chain.ps1(30/30 rc=0)+"
    "git 7df7a767(a4c0e3d4..7df7a767 main push 落)+_r305bmb_orders_diff 复用("
    "91/91)+smoke 25/25+state/heartbeat 306 epoch int 自证 | next: 09-28 周一"
    "首新 bar 全链(update_daily->live.paper->t35v->t24x2->aggr->grid 首拍唤醒->"
    "export->scorecard->daily_report)+T-87 周一 15:30 后首次日续拉实弹(全宇宙分"
    "离 fetch ~3.5h by-design·settled 重臂自愈)+CN-SECTOR-LEADER-P1 判决批 "
    "autofill 自续看护(bm-a 车道)+10-01 月度三件套+REGIME_GUARD v3 日期门+迁移"
    "窗 v2.2 armed 至 09-29 12:00 勿双 arm+R310 下次 5x 核对"
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
hb["round_no"] = 306
hb["verdict"] = "green"
hb["cores"] = 16
hb["idle_ram_gb"] = FREE_GB
hb["gpu_free_vram_mb"] = GPU_FREE_MB
hb["idle_ram_mb"] = FREE_MB
hb["gpu_idle_vram_mb"] = GPU_FREE_MB
hb["gpu_idle_vram_gb"] = GPU_GB
hb["cpu_pct"] = CPU_PCT
hb["round"] = 306
hb["free_ram_mb"] = FREE_MB
with io.open(HB, "w", encoding="utf-8", newline="") as f:
    f.write(json.dumps(hb, ensure_ascii=False, indent=1))
v = json.load(io.open(HB, encoding="utf-8-sig"))
assert isinstance(v["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178)"
assert "T" in v["clock_read"] and "+" in v["clock_read"], "clock_read T-sep law (R262)"
assert v["round_no"] == 306
print("heartbeat ok: epoch=%d int, clock=%s, free_ram=%sGB gpu=%sMB" % (
    v["heartbeat_epoch_utc"], v["clock_read"], FREE_GB, GPU_FREE_MB))
