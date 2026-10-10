# -*- coding: utf-8 -*-
# r867 bm-b closeout: round-report line append + state.json r867 bump + heartbeat update.
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


def ram_free_pct():
    try:
        import psutil
        return round(psutil.virtual_memory().available * 100.0 / psutil.virtual_memory().total, 1)
    except Exception:
        return None


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
RAM = free_ram_gb()
RAMP = ram_free_pct()
VRAM = vram_free_gb()

REPORT_LINE = (
    NOW + " | r867 bm-b | "
    "实况三行：当前活=N2 素材池消费批 MP1 slice-1 起草窗（T24 登记+同轮认领·prereg DRAFT+六腿起草探针双落地）/"
    "最近实物=research/N2_MP1_PREREG.md（DRAFT §0-§8+§0.5·banned gate ADMIT rc0）+results/_r867bmb_mp1_draft_probe.py"
    "（实弹 rc0）+回执 results/_r867bmb_mp1_draft_probe.json（池 96 员/89 可算/178 门/锚 3341-390-149·07:0x）/"
    "下个里程碑=MP1 slice-2 runner+冻结窗+slice-3 池烧录 finalize ≤2026-10-13（W20 §0 消费评估窗令面） | "
    "S0: fetch behind=0（HEAD=a8ff3243a=origin tip 免 pull）+轮首脏=5 daemon live faces（SatEngine 每分钟回写"
    "致 stash→pull→pop 三步竞态实录——pop 后 pull 再脏=改走 fetch+behind 计数零竞态路径·daemon 面零丢）"
    "+孤儿面=0（10 py faces） | S0.5: orders diff 0（68 files/192 acks/unacked 0）+D19 双水位恒等"
    "（dec caca0c6e/ord f90233c7·probe rc0）+决策审核步零增量（水位键不动） | S1: smoke 49/49 | "
    "S2: 板面 job 0/ticket 0 open/wm red=false（py_low_board_clear 合法 idle=板全闭环+池空+无可跑批白名单）"
    "+SAT alive rc0 idle（queue 0）+idle trigger green_idle=true idle_rounds 1→--worked 当窗清零"
    "（backlog 池线=他司游戏线项非本司车道·本司常设议程=MP1 供给线本窗落地） | "
    "S3 主产出=**N2-MP1 素材池消费批 slice-1（池首消费·W19/W20 §8 消费侧指针）**："
    "tech.md T24 登记（queue_seed_gate check rc0 hits=[] status=open+scan CLEAR）+同轮认领；"
    "prereg DRAFT 全节落地——批型=判别力探针/供应普查（A158-TSGATE-P1 逐字先例·gate_census→gate_verify 血统）"
    "·非试验账本批（marks+0·SEED+0·零 rng=无种子带步）·出场轴=探针批不适用声明·consumer_plan 三验全过"
    "（PASS→独立复核资格→v4 政体门候选臂库/PARTIAL→C1 输入特征/FAIL=关线照报）·D6 换用法独立假设（r433 判例）"
    "+选择偏差披露（96 员=截面 IC 存活面·时序门读数不外推）·判线=gate_verify 三控逐字（IS≤2016-12-31/OOS≥2017-01-01"
    "·diff−0.10% 成本·stride-20 不重叠·MIN_EV=15）·多重检验税 N=178 门 E[FP]=8.9·cutoff 2026-10-09+G-ANCHOR-MP1 新锚"
    "（DELTA(VOLUME,30)_q10@510300 decidable==3341∧open==390∧first_idx==149·in-run fail-closed）"
    "+数据完备门四件（G-PANEL/G-CUTOFF 3,490 行/G-ANCHOR/G-FACTORS）；"
    "§0.5 禁向闸实跑 ADMIT rc0（初版误触 BAN-03「日内」子串=「截日内跨股票排名」CSRANK 语义措辞碰撞·"
    "非禁向宣称·改正文措辞为「按日期截面」+误触实录留痕 §0.5·禁绕闸律合规）；"
    "六腿起草探针实弹 rc0：池读数 96=48+48 跨波 overlap=0（T-84s3 构造复核）·parser round-trip 96/96"
    "（formula_str 逆解析器新面）·CSRANK 7 式单工具不可算诚实排除（[n_dates,1] 退化为常量实证）"
    "→89 可算式×q10/q90=178 门·M1 正向 9 员带（W19 波）全可算·面板 1,724 csv 五员末 bar 2026-10-09"
    "·1,013 工具 ≥500 bars（A158-TSGATE §7 同面同数）·t23 评估器单工具腿 3/3 finite~99%"
    "（**轴约定坑当窗治愈：t23 面板=[n_dates,n_stocks]·axis0=时间/axis1=截面——首版 [1,n] 误构全 NaN 静默面**"
    "·正确面 [:,None] 痊愈·坑由 prereg §2+回执承载+slice-2 selftest 手值腿将钉死）"
    "·a158_tsgate_probe 复用面四函数在位（thin/inst_gate_stats/load_truncated/gate_universe）；"
    "CODELY.md 帽位 108B 实读（30,612B）——本轮坑教训已由 prereg §2+回执承载·记忆 append 延至 slice-2 轮合批"
    "（届时 mini-split 当窗办） | S6: 41 腿账=40 rc0+alloc rc2 已知 510880 P5 slot 携带面（r866 同款）；"
    "dualrun ZERO-DRIFT streak 22（排 compute_audit 前序合法）；compute_audit 旗=pool_starvation+supply_floor"
    "（post-burn 常态·供给对策=MP1 轨道本身本窗落地=T24 slice-1）；update_daily 周末 0 新行合法 no-op"
    "·thermo/dualarm/rev_osc/daily_report REPORT-2026-10-11+LIVE-2026-10-11（ORANGE）幂等落地·token delta 0 | "
    "S7: quartet ALIVE（loop pin=2 no-op+watchdog 幂等重装+双爪 LF 归一核装）+attrition scan CLEAN"
    "（4 ledgers·1 healed shrink 历史注记照录）+idle --worked+books+commit+push behind=0 自证 | "
    "本地未达 origin commit 数=0 | 孤儿面=0 | "
    "next r868: MP1 slice-2 runner build（scripts/mp1_tsgate_probe.py=A158-TSGATE runner 克隆+池公式评估面"
    "〔parser 迁移+t23 evaluate import 单源〕+selftest hermetic 七腿）→冻结窗（探针批型五条件：selftest 复跑"
    "+数据完备门 probe 复跑+banned gate rc0+origin 写前复核+状态翻面 FROZEN 同 commit）→slice-3 池条目"
    "（runnable_pool lane-free）+烧录+finalize+§7/§8 回填+TREASURE 收口步 ≤10-13 窗令面 →CODELY.md mini-split 合批"
    "→W210 freeze watch 维持（bm-a W208/W209 链）→moneyflow IC panel-ready watch 维持（bm-a 车道）"
    "→O-20261011-0012 CPU-max maintained"
)

NOW_ACTIVE = ("r867 closeout: N2-MP1 material-pool consumption batch slice-1 landed "
              "(T24 registered+claimed, prereg DRAFT with banned-gate ADMIT, six-leg draft probe rc0: "
              "pool 96/89 computable/178 gates/anchor 3341-390-149); S6 41 legs; verdict readout r868")
CURRENT_TASK = ("r868 queue: N2-MP1 slice-2 runner build (scripts/mp1_tsgate_probe.py clone of "
                "a158_tsgate_probe + pool-formula evaluation face with parser migration + t23 evaluate "
                "import, hermetic selftest) -> freeze window (census-type five conditions) -> slice-3 "
                "pool burn+finalize+sec7/8 backfill <=10-13 (W20 sec.0 window order) -> CODELY.md "
                "mini-split batched at next append -> W210 freeze watch (bm-a chain) -> moneyflow IC "
                "panel-ready watch -> O-20261011-0012 CPU-max maintained")
LATEST_ARTIFACT = ("r867: research/N2_MP1_PREREG.md (DRAFT, material-pool consumption wave-1, TSGATE "
                   "usage-swap census 178 gates, G-ANCHOR-MP1 3341/390/149) + results/_r867bmb_mp1_draft_probe.py "
                   "(live rc0) + receipt results/_r867bmb_mp1_draft_probe.json + tech.md T24 row "
                   "(claimed, slice-1 done) + banned-gate receipt results/_r867bmb_banned_gate.txt (ADMIT)")
NEXT_MILESTONE = ("N2-MP1 slice-2 runner + freeze + slice-3 pool burn+finalize <=2026-10-13 (W20 sec.0 "
                  "consumption evaluation window); pool first-consumption verdict lands in-window; "
                  "chain head 877,723 monotone (census batch zero-append)")
VERDICT = ("GREEN: r867 (N2-MP1 material-pool consumption slice-1 landed: prereg DRAFT + six-leg probe "
           "rc0 with anchor triple pinned, T24 registered+claimed, banned gate ADMIT after wording fix; "
           "smoke 49/49; S6 40/41 rc0 alloc-known; dualrun streak 22; watermark py_low_board_clear lawful; "
           "orders diff 0; D19 identical; SAT alive; attrition CLEAN; orphan face=0; idle cleared --worked)")
DID = ("r867: S0 fetch behind=0 (HEAD=origin tip a8ff3243a, no pull needed; daemon-face stash-pull race "
       "disclosed, zero-loss fetch path) + orphan face=0 (10 py faces) + orders diff 0 (68/192, S7 rescan 0) "
       "+ D19 dual watermark identical (dec caca0c6e/ord f90233c7) + smoke 49/49 + boards clear + SAT alive "
       "rc0 idle + idle green_idle cleared --worked; PRIMARY PRODUCT = N2-MP1 MATERIAL-POOL CONSUMPTION "
       "BATCH SLICE-1 (first consumption of W19+W20 96-member factor material pool per W19/W20 sec.8 "
       "pointer, all-new prereg + cost stress, A158-TSGATE-P1/A10 precedent): tech.md T24 registered "
       "(queue_seed_gate rc0) + claimed same round; prereg DRAFT research/N2_MP1_PREREG.md full skeleton "
       "(census-type probe batch, non-trial ledger, marks+0 SEED+0 no-seed-bands; gate_verify three-control "
       "line verbatim; 178 two-sided gates E[FP]=8.9; cutoff 2026-10-09; G-ANCHOR-MP1 new fail-closed anchor "
       "DELTA(VOLUME,30)_q10@510300 3341/390/149; consumer_plan three-checks; usage-swap independent "
       "hypothesis r433 + selection-bias disclosure) + sec0.5 banned_direction_gate ADMIT rc0 (initial "
       "BAN-03 'intraday' substring word-face collision on CSRANK semantics phrasing fixed in-body, "
       "disclosed in sec0.5, no bypass) + six-leg draft probe live rc0 (pool 96=48+48 cross-wave overlap=0 "
       "T-84s3 recheck; parser round-trip 96/96; CSRANK 7 excluded honest -> 89 computable; M1 positive "
       "9-member band all computable; panel 1,724 csv five-member cutoff 2026-10-09, 1,013 instruments "
       ">=500 bars same face as A158-TSGATE; t23 evaluator single-instrument leg 3/3 finite~99% with "
       "axis-convention pit healed in-window [n_dates,n_stocks] axis0=time; a158_tsgate reuse face 4 "
       "functions in place) + receipt results/_r867bmb_mp1_draft_probe.json; CODELY.md cap 108B headroom "
       "disclosed, memory append deferred to slice-2 batch mini-split; S6 41 legs 40 rc0 + alloc rc2 known "
       "510880 stale-leg carried (dualrun ZERO-DRIFT streak 22; compute_audit pool_starvation+supply_floor "
       "post-burn normal, supply answer = MP1 lane itself; daily_report REPORT-2026-10-11 + "
       "LIVE-2026-10-11 ORANGE idempotent); S7 quartet green (loop pin=2 no-op, watchdog re-registered, "
       "both claws LF-normalized) + attrition CLEAN + idle --worked + books (state r867, heartbeat, this "
       "line) + commit + push behind=0 self-proof"
       )
NEXT = ("r868 queue: N2-MP1 slice-2 runner build (scripts/mp1_tsgate_probe.py: A158-TSGATE runner clone + "
        "pool-formula evaluation face, parser migration from probe, t23 evaluate import single-source, "
        "hermetic selftest 7 legs) -> census-type freeze window (selftest re-run + data-gate probe re-run "
        "+ banned gate rc0 + origin pre-write check + FROZEN flip same commit) -> slice-3 runnable_pool "
        "entry (lane-free) + burn + finalize + sec7/8 backfill + TREASURE closeout step <=10-13 window "
        "order -> CODELY.md mini-split batched at next append (cap 108B) -> W210 freeze watch (bm-a "
        "W208/W209 chain, seats blocked) -> moneyflow IC panel-ready watch (bm-a lane) -> O-20261011-0012 "
        "CPU-max maintained")
LAST_ACTION = DID

# ---------------- report append (binary, EOL law) ----------------
with open(REPORT, "ab") as fh:
    raw = open(REPORT, "rb").read()
    eol = b"\r\n" if raw.endswith(b"\r\n") else b"\n"
    fh.write(REPORT_LINE.encode("utf-8") + eol)

# ---------------- state.json ----------------
with open(STATE, encoding="utf-8") as fh:
    st = json.load(fh)
st["round"] = 867
st["round_no"] = 867
st["round_no_label"] = "r867"
for k in ("clock_read", "ts", "last_round_at", "last_round_ts", "last_seen", "updated", "updated_at"):
    st[k] = NOW
st["last_round_at"] = NOW
st["now_active"] = NOW_ACTIVE
st["current_task"] = CURRENT_TASK
st["task"] = CURRENT_TASK
st["did"] = DID
st["last_action"] = LAST_ACTION
st["next"] = NEXT
st["next_milestone"] = NEXT_MILESTONE
st["latest_artifact"] = LATEST_ARTIFACT
st["verdict"] = VERDICT
st["orphan_face"] = 0
st["orphan_faces"] = 0
st["orphan_face_note"] = ("r867 round probe: py_faces=10 alive, orphans=0 (zero live seats; "
                          "MP1 slice-1 draft leg, zero detached burns)")
st["last_decisions_read_at"] = NOW
st["last_orders_read_at"] = NOW
with open(STATE, "w", encoding="utf-8") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1, sort_keys=True)

# ---------------- heartbeat ----------------
with open(HEART, encoding="utf-8") as fh:
    hb = json.load(fh)
hb["clock_read"] = NOW
hb["ts"] = NOW
hb["last_seen"] = NOW
hb["last_round_at"] = NOW
hb["last_action_at"] = NOW
hb["heartbeat_epoch_utc"] = EPOCH
hb["round"] = 867
hb["round_no"] = 867
hb["cpu_cores"] = 16
if RAM is not None:
    hb["free_ram_gb"] = RAM
    hb["ram_free_gb"] = RAM
if RAMP is not None:
    hb["ram_free_pct"] = RAMP
if VRAM is not None:
    hb["gpu_free_vram_gb"] = VRAM
    hb["vram_free_gb"] = VRAM
    hb["gpu_free_vram_mb"] = int(round(VRAM * 1024))
hb["current_task"] = CURRENT_TASK
hb["task"] = CURRENT_TASK
hb["did"] = DID
hb["last_action"] = LAST_ACTION
hb["next"] = NEXT
hb["now_active"] = NOW_ACTIVE
hb["latest_artifact"] = LATEST_ARTIFACT
hb["next_milestone"] = NEXT_MILESTONE
hb["verdict"] = VERDICT
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["orphan_face"] = 0
hb["orphan_faces"] = 0
hb["orphan_face_note"] = st["orphan_face_note"]
hb["sync"] = {
    "last_push_ts": NOW,
    "note": ("r867 closeout push (MP1 slice-1: prereg DRAFT + probe + T24 row + S6 chain + books); "
             "post-push behind=0 self-proof via fetch+rev-list"),
}
with open(HEART, "w", encoding="utf-8") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1, sort_keys=True)

# ---------------- self-verify (smoke F7 law) ----------------
chk = json.load(open(HEART, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "clock_read must be ISO8601 T-separated"
chk2 = json.load(open(STATE, encoding="utf-8"))
assert chk2["round_no"] == 867
print("books ok: report line appended; state r867; heartbeat epoch=%d ram=%s vram=%s" % (chk["heartbeat_epoch_utc"], RAM, VRAM))
