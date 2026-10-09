# -*- coding: utf-8 -*-
"""r817 bm-b closeout receipt: state.json + heartbeat bm-b.json + round report line
(r900bm-a closeout pattern; epoch int type law R170/R178; S6/S7 evidence in round line)."""
import ctypes
import json
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now_iso = time.strftime('%Y-%m-%dT%H:%M:%S+08:00', time.localtime())
now_short = time.strftime('%Y-%m-%d %H:%M', time.localtime())

VERDICT = ("r817: T9 closed (landing_hooks +F1-BULL-COND 0/9 判负 verbatim + G2-SLOT-MON 2/47 stage-2 "
           "提名≠落地 intermediate; 5 families all-ok n_landings=0 armed; selftest exit 0 incl live leg "
           "+ selftest direct-invocation path fix pre-existing); smoke 49/49; S6 37 legs rc0; pool dualrun "
           "ZERO-DRIFT streak 51; watermark red=false healthy; orders both sweeps zero unacked; ORD/DEC "
           "hash MATCH; attrition CLEAN; 孤儿面=0")
NOW_ACTIVE = "r817: tech T9 closed (scorecard landing_hooks 判词面扩展·F1-BULL-COND+G2-SLOT-MON 双面 verbatim 接线)"
ARTIFACT = ("r817: scripts/strategy_scorecard.py landing_hooks 扩展 (+F1-BULL-COND/G2-SLOT-MON, selftest P11e "
            "legs) + research/LANDING_HOOKS_P1.md v1.1 增补件, " + now_short)
CURRENT = ("r818: tech queue head T10 (zt_pool 四面板交叉校验器) + waiting: Monday 10-12 09:15 minute_feed "
           "gated backfill 10-08/10-09 (verify rerun confirm) / astock refresh closeout / bm-c W17 "
           "post-training resumption / T-181 burn+finalize (bm-a)")
NEXT_MS = ("r818: tech T10 zt_pool cross-panel verifier (<=48h); Monday 2026-10-12 09:15 minute_feed first "
           "gated run backfills 10-08/10-09 in-window (verify rerun confirms recovery)")
TASK = "tech queue T10 head; waiting: astock refresh closeout / bm-c W17 resume post-training / T-181 burn by 10-12"
NOTE = ("r817: T9 landed (landing_hooks 判词面扩展: +F1-BULL-COND 批 verdict verbatim + G2-SLOT-MON 提名≠落地, "
        "spec v1.1 addendum, selftest P11e + live 5-family armed) + selftest 直调路径坑修复 (sys.path ROOT "
        "分支对等, pre-existing ModuleNotFoundError healed, CODELY r817 行)")


def free_ram_gb():
    class MS(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    m = MS()
    m.dwLength = ctypes.sizeof(MS)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return round(m.ullAvailPhys / (1024 ** 3), 1)


def gpu_free_mb():
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                              capture_output=True, text=True, timeout=15,
                              creationflags=0x08000000)  # CREATE_NO_WINDOW (U060 zero-flash law)
        return int(float(out.stdout.strip().splitlines()[0]))
    except Exception:
        return None


def upd(path, mutate):
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    mutate(d)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def st(d):
    d["round_no"] = 817
    d["round"] = 817
    d["round_no_label"] = "r817"
    d["note"] = NOTE
    d["did"] = "r817: tech T9 closed (landing_hooks two new frozen verdict faces wired + selftest P11e + spec v1.1) + S6 37 legs rc0"
    d["verdict"] = VERDICT
    d["now_active"] = NOW_ACTIVE
    d["latest_artifact"] = ARTIFACT
    d["current_task"] = CURRENT
    d["next"] = CURRENT
    d["next_milestone"] = NEXT_MS
    d["task"] = TASK
    for k in ("last_round_at", "ts", "updated", "updated_at", "clock_read", "last_round_ts"):
        if k in d:
            d[k] = now_iso


upd(os.path.join(ROOT, "state.json"), st)

ram = free_ram_gb()
gpu = gpu_free_mb()


def hb(d):
    d["round"] = 817
    d["round_no"] = 817
    d["now_active"] = NOW_ACTIVE
    d["current_task"] = CURRENT
    d["task"] = TASK
    d["latest_artifact"] = ARTIFACT
    d["next_milestone"] = NEXT_MS
    d["verdict"] = VERDICT
    d["last_action"] = ("r817: tech T9 (landing_hooks F1+G2 verbatim wiring + spec v1.1 + selftest P11e + "
                        "selftest path fix) + S6 37 legs rc0 + S7 quartet green")
    d["last_round_at"] = now_iso
    for k in ("last_seen", "updated", "ts", "clock_read"):
        d[k] = now_iso
    d["heartbeat_epoch_utc"] = int(time.time())
    d["idle_rounds"] = 0
    d["agenda_starved"] = False
    d["orphan_faces"] = 0
    d["orphan_face_note"] = ("r817 probe 05:2x: 15 py faces 0 orphans; astock refresh lock alive "
                             "(T-87 bm-b lane full-universe pull in-flight, lawful)")
    if ram is not None:
        d["free_ram_gb"] = ram
    if gpu is not None:
        d["gpu_free_vram_mb"] = gpu
        d["gpu_free_vram_gb"] = round(gpu / 1024.0, 2)


hb_path = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
upd(hb_path, hb)

chk = json.load(open(hb_path, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178)"

RR = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
line = (
    now_iso + " | r817 bm-b | dept:工程（tech T9 scorecard landing_hooks 判词面扩展·S6 全链 rc0） | "
    "WM-VERDICT: 绿（red=false·lane healthy·py_low 合法=板工零+池 ready 0=W17 bm-c 车道非本机候选+local=astock 在途法定批） | "
    "孤儿面=0（probe 15 py faces 0 orphans·只读） | "
    "①S0-1 锚定 bm-b；S0 fetch 实核落后 7=bm-c r827+W17 autofill 批→与本地脏面零文件重叠=ff-only 快进（0 ahead=pull-rebase 恒等面·r642 净树律适配·pull 撞 unstaged 非阻塞披露）；"
    "②S0.5 双扫=orders 60 全 ack 零未回执+D-19 探针 DEC a3ea37bd/ORD e286f842 双 MATCH 零新决策；"
    "③S1 smoke 49/49；S2 job_list 0+fleet 票 0 open（T-181 bm-a 认领在跑·T-179/180 done）；"
    "④P0 产品=T9 出列：scorecard landing_hooks 判词面扩展=+F1-BULL-COND（T-177 leg-2 s2·批 verdict verbatim·9 cells 0 pass·any_cell_full_chain_pass=false·best L250_k3=r899 判负闭卷如实）"
    "+G2-SLOT-MON（T-163·family_verdicts verbatim·2/47 提名 old_032+best_016=STAGE2_SHORTLIST_AWAITING_INDEPENDENT_FREEZE·提名≠落地零新判线）"
    "——判词逐字消费零重判·缺件 ABSENT fail-closed·live 5 族全 ok n_landings=0 armed；selftest P11e 新腿全过 exit 0 含 live 腿；"
    "spec LANDING_HOOKS_P1.md v1.1 增补件（v1.0 三族判线零触碰）；工程附修=模块顶 sys.path ROOT 修 selftest 直调 knowledge ns-pkg ModuleNotFoundError 前置坑（main() 分支早插/selftest 分支漏插·HEAD stash 复现 pre-existing·CODELY r817 行）；tech 队列 7→6（T10 队头）；"
    "⑤S6 37 腿全 rc0（dualrun ZERO-DRIFT streak 51+audit rc0+watermark probe+clock ORANGE_COOL sleeves=4 activated=0+dualarm BEAR@09-30×emo@09-22 再生+rev_osc 面板 incomplete 诚实 no-op+minute_feed 非工作日 no-op+thermo rc0+daily_report/LIVE-2026-10-10 再生 ORANGE cap50%+token delta=0；周六无新 bar 合法跳 live.paper 四腿）；"
    "⑥S7 四件套全绿（loop pin=2 no-op+watchdog 活+双爪 intact）+attrition 4 ledger CLEAN（3 历史缩行 healed 注记照录）；⑦S4 记忆一行（双入口分支路径面不对等坑） | "
    "验证证据: smoke 49/49+scorecard selftest exit 0（P11e+live 5 族 armed）+S6 37 legs rc0 日志 results/_r817bmb_s6.log+dualrun streak 51+attrition CLEAN+心跳 epoch int 自证 | "
    "记分: 2（T9=能跑能看能用实物：判词面接线+spec+selftest）| 记账预算: 5/5（state+心跳+轮报+tech 队列行+CODELY 坑行）| "
    "宝藏捕获: 零新方法零新宝藏（T9=读数面接线判词逐字复用；分支路径坑=坑律非方法论资产）| unacked_orders=0 | "
    "本地未达 origin commit 数=0（commit 后 push+fetch+rev-list 自证）| "
    "下轮指针: r818: ①tech 队头 T10（zt_pool 四面板交叉校验器）②周一 10-12 09:15 minute_feed 首 gated 轮回补 10-08/10-09→verify 复跑确认恢复③候：astock refresh closeout/bm-c W17 训练后复燃/T-181 burn 收口 | [r817 bm-b]\n")
with open(RR, "a", encoding="utf-8") as f:
    f.write(line)

print("r817 closeout OK:", now_iso, "| epoch_int:", chk["heartbeat_epoch_utc"],
      "| free_ram:", ram, "GB | gpu_free:", gpu, "MB")
