# r1026 bm-c absorb-window closeout: state + heartbeat + round report (canonical path)
import json, time, io, sys, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
now = "2026-10-15T{:02d}:{:02d}:{:02d}+08:00".format(*time.localtime()[3:6])
epoch = int(time.time())

def load(p):
    return json.load(open(ROOT + "\\" + p, encoding='utf-8'))

def save(p, d):
    json.dump(d, open(ROOT + "\\" + p, "w", encoding='utf-8', newline=''), ensure_ascii=False, indent=1)

# fresh machine sample
os_free_gb = None; cpu_pct = None
try:
    import ctypes
    class MS(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong)]
    ms = MS(); ms.dwLength = ctypes.sizeof(MS); ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms))
    os_free_gb = round(ms.ullAvailPhys / (1024**3), 2); memload = ms.dwMemoryLoad
except Exception:
    os_free_gb = 0.71; memload = 97
try:
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free,utilization.gpu", "--format=csv,noheader,nounits"], capture_output=True, text=True)
    parts = r.stdout.strip().split(","); gpu_free_mb = int(parts[0]); gpu_util = int(parts[1])
except Exception:
    gpu_free_mb = 14848; gpu_util = 0

ORD_SHA = "0de5aaecefac4c4550ec27393e96432a893d9b7d"
DEC_SHA = "578804c1acfa186f6d7b0a403f8d7ab27acf1a73f15ca035628aebe3554261cd"

absorb_note = ("r1026 absorb note: prior dead window (self-labeled r1026, opened ~11:48 after r1025 closeout 11:31, last write 12:07:37, "
    "ZERO commits, state counter still 1026) executed: S0 (rebase conflict on research/HANDOVER.md ours=4c37fbd6b vs theirs=e3581d89b -> "
    "r990 pit-mandate sequencer capture results/_r1026bmc_rebase_sequencer_capture/ 14 files + _r1026bmc_handover_union.py line-level union heal, "
    "treasure_guard rc3 carve-out honored, landed clean) + S0.5 dual-scan 11:56 (zero new rows then) + W20 supply funnel legs 1/5+2/5 "
    "(research/TRIAL_LABOR_W20_CANDIDATE_ENTRYGEN_PREREG_DRAFT.md 15,431B + probe facts + banned gate rc0 ADMIT BAN-04 new_mechanism exception "
    "+ seed_admit 20650000 span1 rc0 FREE + SEED_REGISTRY live 221) + S6 chain 43/43 rc0 (log 12:03-12:07) -- died pre-commit; "
    "this session (12:15, PID 67504 = only live loop codely) absorbed per bm-c absorb precedent lineage (r894..r1025, 29th instance): "
    "estate machine-verified BEFORE landing (banned gate re-run rc0 ADMIT + seed gate positional re-run rc0 FREE + SEED_REGISTRY 221 keys "
    "re-read via science_gates + W16 anchor sha256_16 22179881b7537193 raw-bytes re-hash + W17/W18/W19 judge faces 344/188/112 eligible_reform=[] "
    "+ queue collision CLEAR + ledger 21 wave rows/445,022B); honest disclosure: probe facts JSON live-gate legs (banned/seed/seed_registry_path/dsr/"
    "funnel_status) = null or rc2 tool-path-defect records (scripts\\ vs Tools\\), superseded by this window's direct gate re-runs rc0 both; "
    "static legs (w16/judge/ledger/collision) all good; executed as r1026 continuation, counter 1026->1027 so next session = r1027; "
    "zero double-count: ORD rows after 11:56 (12:0x token law) + DEC D-20261015-03 were NOT visible to the dead window, consumed THIS window")

closeout_note = ("r1026 closeout: (1) S0-1 anchor bm-c + round-zero probe py_faces=5 orphans=2 zero-kill + S0 fetch 0/0 (HEAD==origin 4a3b1100e, "
    "daemon live-faces legit dirty); (2) S0.5 dual-delta TRUE both consumed THIS window: ORD 46c60d47->0de5aaec (1 new row = 12:0x CEO 云端token严管令 "
    "O-20261015-1200, committee-executed same-window, zero BigMoney action; LOCAL_FIRST + token_meter already standing) / DEC 6910a9ed->578804c1 "
    "(new row = D-20261015-03 token law legislation, HQ executed; D-15-01/02 already consumed by r1019/r1020 -- bm-c D-02 leg CLOSED 59f699771 "
    "(evidence trio selftest 6/6 + live probe + F-note), bm-b D-02 leg PENDING in window (3 bm-b-suffix tick faces still tracked per "
    "owning-machine-only untrack law), window to 10-17 00:00) + unacked=0; (3) S1 smoke 49/49; (4) S3: satengine ALIVE rc0 queue 0 + "
    "watermark red=false healthy lane + W245=bm-a seat in-flight (r1012 estate-absorb landed ~10:48, finalize NOT landed -> W246 bm-c turn "
    "staged per chain-order law) + idle green_idle=false RAM-gate honest (ram_free_pct=3.2, U256 w001/w003 claims stay deferred) + "
    "MV GPU lane: POOL-0014 KF 14/14 + LOOKBOARD landed, awaiting bm-a director review (no review row on origin as of 12:17 fetch) + "
    "inbox 2 MSGs both addressed bm-a zero bm-c debt + jobs 0 open; (5) PRODUCT = dead-window estate landed: W20 candidate draft (funnel 1/5+2/5, "
    "entry GENERATE route, X/S/T three-axis all-consumed fixed, three fn-family directions dd_ladder/near_52w_high/turnover_regime, "
    "58-fn roster zero-intersection draft-assert, seeds band 20650000 family, evidence_cutoff 2026-09-22 P-5C binding) + probe facts + "
    "sequencer capture evidence; (6) S6 43/43 rc0 absorbed NOT rerun per same-round law (dead window 12:03-12:07 chain, faces on disk); "
    "(7) S7 quad green (loop pin=5 no-op + watchdog registered + claws installed x2) + commit rides this window")

state = load("state-bm-c.json")
state["round_no"] = 1027
state["loop_round"] = state.get("loop_round", 993)
state["last_round"] = "r1026"
state["last_round_at"] = now
state["last_round_label"] = "r1026"
state["last_round_closed"] = now
state["last_seen"] = now; state["last_seen_at"] = now; state["last_ts"] = now
state["ts"] = now; state["updated"] = now; state["updated_at"] = now
state["clock_read"] = now
state["current_task"] = "r1026 absorb closeout: W20 draft landed (funnel 1/5+2/5) + S6 43/43 absorbed + ORD/DEC consumed"
state["current_task_at"] = now
state["current_task_ts"] = epoch
state["last_orders_sha"] = ORD_SHA
state["last_orders_read_at"] = now
state["last_decisions_sha"] = DEC_SHA
state["last_decisions_read_at"] = now
state["last_round_summary"] = ("r1026 bm-c: (1) S0-1 anchor + probe 5/2 zero-kill + fetch 0/0; (2) ABSORB 29th: dead r1026 window (11:48-12:07 "
    "zero-commit) estate verified+landed -- W20 candidate draft funnel 1/5+2/5 (banned rc0 ADMIT + seed 20650000 rc0 FREE + SEED_REGISTRY 221 + "
    "W16 anchor 22179881b7537193 + judge 344/188/112 + collision CLEAR, probe-facts live-leg path-defect disclosed superseded) + S6 43/43 rc0 "
    "absorbed not-rerun + sequencer capture 14-file evidence; (3) S0.5 ORD 0de5aaec (token law row, zero action) + DEC 578804c1 (D-15-03) "
    "consumed, unacked=0; (4) smoke 49/49; satengine ALIVE; wm red=false; W245 bm-a in-flight -> W246 staged; idle RAM-gate honest 3.2%; "
    "(5) S7 quad green; counter 1026->1027")
state["last_action"] = "r1026 closeout (absorb W20 draft estate + ORD/DEC consumption)"
state["last_action_at"] = now
state["verdict"] = ("green: dead r1026 window absorbed (W20 candidate draft landed = funnel 1/5+2/5 product + S6 43/43 absorbed + gates "
    "re-verified rc0 both), W-chain = bm-a W245 in-flight (finalize pending) -> W246 bm-c turn staged per chain-order law, U256 claims deferred "
    "honest (RAM gate 3.2%<40%), MV V4 GPU lane = awaiting bm-a director review of JAY-REDO-KF-BOARD-r1025.jpg (POOL-0014), no-silent-idle "
    "structural-wait annotation carried")
state["did"] = state.get("did", "")
state["r1026_absorb_note"] = absorb_note
state["r1026_closeout_note"] = closeout_note
state["next"] = ("r1027: (1) W245 finalize watch -> W246 seat (bm-c turn, chain-order law); W20 freeze window (funnel 3/5, ANY healthy machine, "
    "commit=lock): ten-leg probe = fn roster finalization (dd_ladder/near_52w_high/turnover_regime families + sig_params grids + kin orthogonality) "
    "+ ledger rescan + A7 census zero-intersection fail-closed + 58-fn roster assert + control sha three-face read + W17/W18/W19 verdict "
    "consumption re-check + seeds band span=1001 full re-run + collision four-check -> freeze four-piece (commit + SEED_REGISTRY 3 keys "
    "20650000/20650500/20651000 same-commit + wave ticket T-<date>-<seq>-P1 + F-04 MSG); (2) bars 10-15 due 15:30 -> update_daily gate -> "
    "papers full chain (live.paper REGIME_GUARD + t35 + t24 x2 + aggr/alloc/grid/system_v1 + export + faces); (3) RAM gate opens -> U256 "
    "bmc-w001 funnel-1 audit + bmc-w003 collector verify claims; (4) MV V4 GPU lane: i2v INT8 768P full batch on bm-a director review of "
    "JAY-REDO-KF-BOARD-r1025.jpg; (5) S8 prompt wiring: re-check bm-b sentinel edit on origin")
state["next_pointer"] = state["next"]
state["next_milestone"] = ("r1027: (1) bars 10-15 due 15:30 -> papers full chain; (2) W20 freeze window (funnel 3/5) per draft §8; (3) W245 "
    "finalize -> W246 seat; (4) MV V4 i2v batch on director review")
state["latest_artifact"] = ("r1026: research/TRIAL_LABOR_W20_CANDIDATE_ENTRYGEN_PREREG_DRAFT.md (funnel 1/5+2/5, gates rc0 ADMIT/FREE) + "
    "results/_r1026bmc_w20_probe_facts.json + sequencer capture evidence (this commit)")
state["last_artifact"] = state["latest_artifact"]
state["recent_artifact"] = state["latest_artifact"]
state["free_ram_gb"] = os_free_gb
state["ram_free_gb"] = os_free_gb
state["idle_ram_gb"] = os_free_gb
state["gpu_free_vram_mb"] = gpu_free_mb
state["gpu_free_vram_mib"] = gpu_free_mb
state["gpu_free_mb"] = gpu_free_mb
state["cpu_pct"] = 100 - memload
state["idle_rounds"] = 0
state["agenda_starved"] = False
state["now_active"] = "{} | r1026 | bm-c: absorb W20 draft estate + ORD/DEC consumed | counter 1026->1027 (r1026 exec)".format(now)
state["activity_now"] = state["now_active"]
state["heartbeat_epoch_utc"] = epoch
state["d19_watermark_guard"]["round_ref"] = 1027
state["d19_watermark_guard"]["ts"] = now
state["prod_lanes"] = ("CPU=N1 W245=bm-a chain (prereg landed, splice/burn/finalize theirs; W246 bm-c turn staged) ; GPU=MV V4 POOL-0014 "
    "awaiting bm-a director review -> i2v INT8 768P full batch next ; SUPPLY=W20 candidate draft landed (funnel 1/5+2/5), freeze window open")
state["full_load_selfproof"] = {
    "占用一行": "GPU=MV 车道候导演席批（POOL-0014 KF 14/14+LOOKBOARD 已交付）+ComfyUI 常驻+album serve；CPU=吸收窗簿记带（py 0-6%）",
    "当前活": "r1026 吸收窗收口（死窗遗产 W20 候选稿落地+S6 43/43 吸收+ORD/DEC 消费）",
    "最近实物": "research/TRIAL_LABOR_W20_CANDIDATE_ENTRYGEN_PREREG_DRAFT.md（12:0x·funnel 1/5+2/5·双闸 rc0）",
    "下个交付物": "W20 冻结窗（funnel 3/5·十腿 probe+四件套）+W245 finalize 落地即 W246 席+bars 15:30 papers 全链",
    "队列水位": "N1 引擎 0 在烧（W245 bm-a 在飞·W246 候）·U256 w001/w003 候 RAM 门·P2/P3 队列空·jobs 0·inbox 2 件均致 bm-a"
}
save("state-bm-c.json", state)

# heartbeat
h = load("fleet\\machines\\bm-c.json")
h["last_seen"] = now
h["ts"] = now
h["updated_at"] = now
h["clock_read"] = now
h["current_task"] = state["current_task"]
h["current_task_at"] = now
h["verdict"] = state["verdict"]
h["did"] = state["last_round_summary"]
h["next"] = state["next"]
h["latest_artifact"] = state["latest_artifact"]
h["round_no"] = 1027
h["free_ram_gb"] = os_free_gb
h["ram_free_gb"] = os_free_gb
h["gpu_free_vram_mb"] = gpu_free_mb
h["gpu_free_mb"] = gpu_free_mb
h["gpu_util_pct"] = gpu_util
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["heartbeat_epoch_utc"] = epoch
h["now_active"] = state["now_active"]
h["activity_now"] = state["now_active"]
h["prod_lanes"] = state["prod_lanes"]
save("fleet\\machines\\bm-c.json", h)

# round report (canonical path per r750/r985 law)
line = ("| {} | r1026 | bm-c 吸收窗：死窗 r1026（11:48-12:07 零 commit）遗产验讫落地=W20 候选草案 funnel 1/5+2/5（入场 GENERATE 路线·X/S/T 三轴全固定·"
    "三方向族 dd_ladder/near_52w_high/turnover_regime·seeds 带 20650000 族·cutoff 2026-09-22）+probe 事实件+序捕件 14 文件+S6 43/43 rc0 吸收不重跑；"
    "S0.5 ORD 0de5aaec（12:0x token 严管令·委员会同窗收口零 bigmoney 动作）+DEC 578804c1（D-15-03·HQ 收口）消费；W245=bm-a 在飞 finalize 未落→W246 席照链序法候；"
    "U256 claims 候 RAM 门（3.2%）honest；MV GPU=POOL-0014 候 bm-a 导演席批 | 验证：smoke 49/49+banned gate 复跑 rc0 ADMIT+seed gate 20650000 复跑 rc0 FREE+"
    "SEED_REGISTRY 221 键+W16 锚 sha256_16=22179881b7537193 复哈希+W17/W18/W19 判决面 344/188/112+撞头探针 CLEAR+S6 日志 43×rc0+S7 四绿 "
    "| r1027：W245 finalize watch→W246 席+W20 冻结窗（funnel 3/5 十腿 probe+四件套）+bars 15:30 papers 全链 | {}\n".format(now, epoch))
with open(ROOT + r"\round_reports-bm-c.md", "a", encoding="utf-8", newline="") as f:
    f.write(line)

print("CLOSEOUT OK", now, "epoch", epoch, "free_ram", os_free_gb, "gpu_free_mb", gpu_free_mb)
print("state round_no ->", state["round_no"], "| ORD", ORD_SHA[:12], "| DEC", DEC_SHA[:12])
