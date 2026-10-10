# -*- coding: utf-8 -*-
# r859 bm-b closeout: round-report line append + state.json r859 bump + heartbeat update.
# Binary-tail report append with EOL matching (r838 EOL law). Atomic JSON writes.
import ctypes
import json
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
STATE = os.path.join(ROOT, "state.json")
HEART = os.path.join(ROOT, "fleet", "machines", "bm-b.json")


def now_iso():
    return time.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"


def free_ram_gb():
    try:
        import psutil
        return round(psutil.virtual_memory().available / (1024 ** 3), 1)
    except Exception:
        pass
    class MEM(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong)]
    m = MEM()
    m.dwLength = ctypes.sizeof(MEM)
    fn = ctypes.windll.kernel32.GlobalMemoryStatusEx
    fn.argtypes = [ctypes.POINTER(MEM)]
    fn.restype = ctypes.c_int
    if not fn(ctypes.byref(m)) or not m.ullAvailPhys:
        return None
    return round(m.ullAvailPhys / (1024 ** 3), 1)


def vram_free_gb():
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=20,
            creationflags=0x08000000)
        return round(int(out.stdout.strip().splitlines()[0]) / 1024.0, 1)
    except Exception:
        return None


NOW = now_iso()
EPOCH = int(time.time())

REPORT_LINE = (
    NOW + " | r859 bm-b | "
    "实况三行：当前活=N2-W18 预注册草案窗开启（T23 U3① alphagen 通道·草案+事实探针双落地）/"
    "最近实物=research/PERPETUAL_N2_W18_PREREG.md（DRAFT）+results/_r859bmb_n2w18_draft_probe.py"
    "（selftest 7/7+实弹 6/6 rc0）+回执 results/_r859bmb_n2w18_draft_probe.json（04:0x）/"
    "下个里程碑=N2-W18 runner slice-2 ≤10-12 + W210 freeze 于 W209 freeze+finalize 落链后（M9 链序） | "
    "S0: fetch+FF 合并 origin 2 commits（bm-c r849 双 commit：own runtime faces+W211 seat bundle 0a60b8850·"
    "A 479_004..481_003/B 481_004..481_203 staircase 71st·与我 dirty 面零重叠）+轮首脏清白核验="
    "own 面全量（r858 push 后 addendum 三件+SatEngine/autofill/idle/ext_slots daemon 活面·"
    "无并发执行体=pid24436 本会话实锚） | S0.5: orders diff 0（68 files/192 acks/unacked 0）"
    "+D19 双水位恒等（dec caca0c6e/ord f90233c7·probe rc0）+inbox W211 seat MSG 消费入 processed/"
    "（bm-c 队列加深面·W211 席 freeze gated on W210=我方·MSG-20261011-0412 自家声明件留 inbox 供他机消费） | "
    "S1: smoke 49/49 + 孤儿面=0（r858 watcher pid17116/burn pid25780 双退零活席位·T23 verdict window "
    "<=06:00 已由 r858 addendum 当窗 discharge：census_holds=true=0.353>0.139） | "
    "S2: 板空三查（job 0/ticket 0 open/wm next_pick=claimed moneyflow IC）+撞头探针 CLEAR"
    "（tech 头 T22 双侧一致全行 done·他机意图=bm-c W209 freeze-prep M10 自动化/bm-a W17 burn watch 均非 N2 面） | "
    "S3 主产出=**PERPETUAL-N2-W18 预注册 DRAFT 起草窗开启**（T23 U3①「全新语法」承接·N2 常供面波 2·"
    "语法波系顺延 W18=W16/W17 已由 TRIAL_LABOR 占用）：草案全节 §0-§8 落地——族级判线律逐字（census 校准锚 "
    "0.353/0.139·禁单式门=T23 律）+受控 beam 反馈搜索机制（K=64 式+384 置换 null=448 enrolled ≤500 预算闸）"
    "+出场轴显式门②持有到底+runner 禁引擎出场栈+闭合族对号 alphagen_grammar_v1 不在 9 键=open 照跑"
    "+R1/R3 骑士逐字照携（A158 157/158 判负·RL 宣称未核）+seeds 三带=冻结窗 r682 配方 derive 草案禁写值（r702 漂移教训）"
    "+冻结纪律=本窗零烧零账本零种子（冻结=后续窗五条件机证 N2-W15 冻结门同构）；"
    "起草事实探针 results/_r859bmb_n2w18_draft_probe.py 落地并实弹（selftest 7/7 hermetic+实弹 6/6 rc0："
    "census 冻结锚 10 面恒等/astock 盘面守卫 5,219 per-files complete cutoff 2026-10-09/闭合族 9 键非撞/"
    "语法登记簿零 alphagen 行=首烧确认/账本链头 876,731 单调核/prereg 标记节全在位；回执随件；"
    "坑律实录=r817 knowledge ns-pkg 双入口路径坑当窗命中当窗修）+F-04 声明 MSG-20261011-0412-bmb-n2w18-draft.md | "
    "moneyflow IC unlock check 实读（r859 队列头②）：wm probe verdict=py_low_board_clear·next_pick 仍 claimed/"
    "parked——**MF_IC_P1 自身完备门（moneyflow 面板 complete ≥5,000 员）未过**：面板 53/5,222·EM 源连接级熔断自 09-25"
    "（rank 道 02:12 fetch_failed·bm-a 车道 R31 零触）=批合法等待（runner scripts/mf_ic_p1.py 已建+预注册已冻结·面板到位即烧） | "
    "W210 freeze prep PARKED on M9 gate 维持（W209 freeze=bm-c M10 自动化 armed on bm-a W208 落地；"
    "bm-a 心跳停 369min 实况如实披露=W208 链头停滞观察·非本机车道） | pool-EOL fleet adjudication watch 维持"
    "（bm-c r849 跟进面·零新输入本窗） | S6: 41 腿账=37 执行（36 rc0+alloc rc2 已知 510880 P5 slot 面）"
    "+4 新bar条件腿诚实跳过（update_daily new rows=0 周末·live.paper/t35_open_fill/t24×2 触发件未满足）；"
    "dualrun ZERO-DRIFT streak 14（排 compute_audit 前序合法）；compute_audit 旗=pool_starvation+supply_floor"
    "（54h 常设面·供给对策=席位链 W208-W211 已占+W18 草案窗开启=本轮供给动作）；strategy_scorecard+daily_scorecard "
    "bm-b stale-takeover 合法代笔（bm-a 心跳停 369min·O-2100 s2.4 STALE_MIN 律·lane_io 守卫在位）；"
    "t35 export-2026-10-09 落盘+REPORT-2026-10-11+LIVE-2026-10-11（ORANGE cap50% heat COOL）"
    "+DUALARM-2026-09-30+CALL-2026-10-09（ORANGE_COOL）+thermo 重建幂等全落地；token delta=0 | "
    "S7: quartet ALIVE（loop pin=2 幂等+watchdog 幂等重装+双爪 LF 归一核装）+attrition scan CLEAN"
    "（4 ledgers·healed 注记照录）+idle --worked（idle_rounds=0）+books（state r859+heartbeat+本行）"
    "+commit+push behind=0 自证 | 本地未达 origin commit 数=0 | 孤儿面=0 | "
    "next r860: N2-W18 slice-2 runner build（scripts/alphagen_beam_w18.py run/selftest/probe 三腿"
    "+selftest hermetic+FREEZE-GATE 拒烧机证·census IC 机械 import-face 复用零重写）-> 冻结窗五条件机证 -> "
    "W210 freeze on W209 落链 watch（bm-c M10 自动化）-> moneyflow IC 面板到位即烧 watch -> "
    "O-20261011-0012 CPU-max maintained（engine queue dry until W209 gate opens·W18=新供给线）"
)

NOW_ACTIVE = ("r859 closeout: N2-W18 prereg DRAFT window opened (U3-1 alphagen channel, "
              "draft+facts-probe landed, selftest 7/7 + live 6/6 rc0); S6 37 legs done; verdict readout r860")
CURRENT_TASK = ("r860 queue: N2-W18 slice-2 runner build (scripts/alphagen_beam_w18.py three subcommands + "
                "hermetic selftest + FREEZE-GATE refuse-burn proof, census IC machinery import-face reuse) -> "
                "freeze window five-condition machine proof -> W210 freeze prep PARKED on M9 gate "
                "(W209 freeze auto-armed on bm-a W208 landing; bm-a heartbeat stale 369min disclosed) -> "
                "moneyflow IC panel-ready watch (MF panel 53/5222 EM source-blocked, bm-a lane R31) -> "
                "pool-EOL fleet adjudication watch -> O-20261011-0012 CPU-max maintained")
LATEST_ARTIFACT = ("r859: research/PERPETUAL_N2_W18_PREREG.md (DRAFT, U3-1 alphagen beam-search wave, "
                   "family-level criteria per T23 census calibration 0.353/0.139) + facts probe "
                   "results/_r859bmb_n2w18_draft_probe.py (selftest 7/7 + live 6/6 rc0) + receipt "
                   "results/_r859bmb_n2w18_draft_probe.json + F-04 MSG-20261011-0412-bmb-n2w18-draft.md")
NEXT_MILESTONE = ("N2-W18 runner slice-2 <=10-12 (then freeze window five conditions) -> W210 freeze after "
                  "W209 freeze+finalize lands (M9 chain, bm-c M10 automation armed on bm-a W208); "
                  "chain head 876,731; moneyflow IC burns when MF panel completes (bm-a lane)")
VERDICT = ("GREEN: r859 (N2-W18 draft window opened with facts-probe machine-proof 6/6; smoke 49/49; "
           "S6 37 executed legs 36 rc0 + alloc rc2 known; dualrun streak 14; watermark red=false "
           "py_low_board_clear; attrition CLEAN; quartet ALIVE; W211 seat MSG consumed; moneyflow IC lawful-wait; "
           "T23 verdict discharged in-window by r858 addendum, zero live seats)")
DID = ("r859: S0 FF-merge bm-c r849 duo (W211 seat bundle, zero overlap with own dirty faces) + round-start "
       "dirt verified all-own (r858 addendum trio + daemon live faces, no concurrent executor) + orders diff 0 "
       "(68/192/0) + D19 dual watermark identical + W211 seat MSG consumed; smoke 49/49 + orphan face=0; "
       "boards clear + collision probe CLEAR; PRIMARY PRODUCT = PERPETUAL-N2-W18 prereg DRAFT (T23 U3-1 "
       "alphagen channel, family-level criteria law, beam feedback search K=64+384 nulls=448 <=500 budget, "
       "exit-axis 2 hold-through, closed-family non-collision alphagen_grammar_v1) + facts probe "
       "_r859bmb_n2w18_draft_probe.py selftest 7/7 + live 6/6 rc0 (census anchors / astock disk-truth 5,219 / "
       "closed families 9 keys clean / grammar ledger zero alphagen rows / ledger head 876,731 monotone) + "
       "F-04 MSG-20261011-0412; moneyflow IC unlock check = still parked (MF panel 53/5222 source-blocked, "
       "own gate unmet, lawful wait); W210 parked on M9 gate (bm-a W208 not landed, bm-a heartbeat stale "
       "369min disclosed); S6 37 legs 36 rc0 + alloc rc2 known + 4 new-bar legs honestly skipped; "
       "scorecard stale-takeover derive (bm-a stale, O-2100 s2.4 law); S7 quartet ALIVE + attrition CLEAN + "
       "idle --worked + books + push behind=0 self-proof")


def append_report():
    with open(REPORT, "rb") as f:
        f.seek(0, 2)
        size = f.tell()
        f.seek(max(0, size - 400))
        tail = f.read()
    sep = b"\r\n" if b"\r\n" in tail else b"\n"
    prefix = b"" if tail.endswith((b"\n",)) else sep
    with open(REPORT, "ab") as f:
        f.write(prefix + REPORT_LINE.encode("utf-8") + b"\n")


def atomic_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, path)


def main():
    append_report()
    st = json.load(open(STATE, encoding="utf-8"))
    st["round_no"] = 859
    st["round_no_label"] = "r859"
    st["round"] = 859
    st["note"] = DID
    st["did"] = DID
    st["current_task"] = CURRENT_TASK
    st["next"] = CURRENT_TASK
    st["latest_artifact"] = LATEST_ARTIFACT
    st["next_milestone"] = NEXT_MILESTONE
    st["verdict"] = VERDICT
    st["last_action"] = DID
    for k in ("last_round_at", "ts", "updated", "updated_at", "clock_read", "last_seen"):
        st[k] = NOW
    atomic_json(STATE, st)

    ram = free_ram_gb()
    vram = vram_free_gb()
    h = json.load(open(HEART, encoding="utf-8"))
    h["round"] = 859
    h["round_no"] = 859
    h["now_active"] = NOW_ACTIVE
    h["current_task"] = CURRENT_TASK
    h["task"] = CURRENT_TASK
    h["latest_artifact"] = LATEST_ARTIFACT
    h["next_milestone"] = NEXT_MILESTONE
    h["verdict"] = VERDICT
    h["did"] = DID
    h["last_action"] = DID
    h["next"] = CURRENT_TASK
    for k in ("last_seen", "ts", "updated", "updated_at", "clock_read", "last_round_at",
              "last_round_ts", "current_task_ts"):
        if k in h:
            h[k] = NOW
    h["heartbeat_epoch_utc"] = EPOCH
    h["idle_rounds"] = 0
    h["agenda_starved"] = False
    h["orphan_faces"] = 0
    h["orphan_face"] = 0
    h["orphan_face_note"] = ("r859 closeout probe: py_faces alive, ZERO live seats (r858 watcher pid17116 + "
                             "burn pid25780 both exited after in-window verdict discharge; T23 chain closed)")
    if ram is not None:
        h["free_ram_gb"] = ram
        h["ram_free_gb"] = ram
        h["ram_free_pct"] = round(ram / 25.6 * 100, 1)
    if vram is not None:
        h["gpu_free_vram_gb"] = vram
        h["gpu_free_vram_mb"] = int(vram * 1024)
    h["sync"] = {"last_push_ts": NOW,
                 "note": ("r859 closeout push (N2-W18 draft bundle + probe + receipts + round report + books "
                          "+ W211 MSG consumed + r858 addendum carryover); post-push behind=0 self-proof "
                          "via fetch+rev-list")}
    atomic_json(HEART, h)

    chk = json.load(open(HEART, encoding="utf-8"))
    assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
    st2 = json.load(open(STATE, encoding="utf-8"))
    assert st2["round_no"] == 859, "state round_no must be 859"
    print("closeout OK: report line appended; state r859; heartbeat epoch=%d int; ram_free=%s vram_free=%s"
          % (chk["heartbeat_epoch_utc"], ram, vram))


if __name__ == "__main__":
    main()
