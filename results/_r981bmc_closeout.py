# -*- coding: utf-8 -*-
# r981 bm-c closeout: round report line + state advance (981->982) + heartbeat refresh
import json, time, subprocess, os, datetime

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW_ISO = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())

# ---- fresh machine readings ----
ram_free_gb = None; total_ram_gb = None; cpu_pct = None; cores = None
try:
    import psutil
    vm = psutil.virtual_memory()
    total_ram_gb = round(vm.total / 1024**3, 1)
    ram_free_gb = round(vm.available / 1024**3, 1)
    cpu_pct = psutil.cpu_percent(interval=1.0)
    cores = psutil.cpu_count(logical=True)
except Exception:
    pass

gpu_free_vram_mb = None; gpu_total_vram_mib = None; gpu_util = None
try:
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free,memory.total,utilization.gpu",
                        "--format=csv,noheader,nounits"], capture_output=True, timeout=20)
    parts = (r.stdout or b"").decode("utf-8", "replace").strip().splitlines()[0].split(",")
    gpu_free_vram_mb = int(float(parts[0]))
    gpu_total_vram_mib = int(float(parts[1]))
    gpu_util = int(float(parts[2]))
except Exception:
    pass

# ---- round report line (S5) ----
REPORT_LINE = (
    f"{NOW_ISO} | r981 | bm-c: W235 finalize LANDED-VERIFIED by bm-a via incoming 4 commits "
    f"(burn 2b3f33e9c + six-gate PRE-FINALIZE 10th consecutive af9ed30be + finalize one-pass ccf10ee3d "
    f"ledger 938,589+2,200=940,789 EXACT / merged K=514,920 EXACT / five-key ALL PASS / sec78 backfilled "
    f"+ bm-a r970 own-wave closeout 02c18bee5 + their S0 absorb b30fe44f2 in-flight) -> r980 next-ptr(1) DISCHARGED; "
    f"W236 chain YIELDED to bm-a per dual-open/T-18 (declared intent in ccf10ee3d 'W236 seat publication next' + "
    f"their window in-flight + zero w236 files on origin both checks); MF IC batch parked source-blocked "
    f"(panel fuse-stopped, bm-a R63 lane, 30min self-heal); P2 tech queue all-done + P3 E17 leg-3 train = bm-b "
    f"lane_owner in-flight (autofill keepalive d83e3c552 anchor); post_review zero-x (45 pass / 5 yellow); "
    f"queue collision probe CLEAR (T22/E14 heads both done-state); S0 stash-bridge pull behind-4->0 "
    f"(pop blocked by live autofill/dispatcher/satengine rewrites -> stash = stale daemon snapshots DROPPED "
    f"live-wins, supersession verified, disclosed); S0.5 ORD/DEC dual-delta FALSE both scans + unacked=0 "
    f"(hold ord 348eaf34 / dec 86187eff); S1 smoke 49/49; S3 satengine ALIVE rc0 (local_done 12/12 W235) + "
    f"wm red=false healthy + idle green_idle=false RAM gate 1.8pct tight protect-note kept; S6 41 legs ALL rc0 "
    f"(dualrun ZERO-DRIFT streak 51 + regime breadth 0.81 + market_clock CALL-2026-10-13 ORANGE_COOL + "
    f"lane-guards honest no-op family + 10 third-signal-veto skips host=bm-a fresh faces + REPORT-2026-10-14 + "
    f"LIVE-2026-10-14 ORANGE cap50% idempotent rewritten + token L2 0 today); S7 attrition 4 CLEAN (healed rows "
    f"historical) + quad green (loop pin=5 no-op / watchdog re-registered 04:48 / both claws installed); "
    f"counter 981->982 "
    f"| verify: 41-leg chain receipt rc0 + smoke 49/49 + attrition CLEAN + s05 probe dual FALSE x2 + push rides "
    f"| next: r982 (1) W236 seat+prereg watch -- bm-a declared + in-flight; if their window dies post-seat, "
    f"absorb prereg derive per seat-first law (subgen m32 pattern, R34 authoring); (2) MF IC batch unpark when "
    f"bm-a panel completes; (3) 10-14 bars re-probe after 15:30 -> papers full chain; (4) MV V3 director "
    f"rulings on QC-r977b per ORD rows"
)
with open(os.path.join(REPO, "round_reports-bm-c.md"), "a", encoding="utf-8", newline="") as f:
    f.write(REPORT_LINE + "\n")

# ---- state advance (S7) ----
STATE_PATH = os.path.join(REPO, "state-bm-c.json")
with open(STATE_PATH, "r", encoding="utf-8-sig") as f:
    state = json.load(f)

state["round_no"] = 982
state["last_round"] = 981
state["last_round_label"] = "r981"
state["loop_round"] = 981
state["clock_read"] = NOW_ISO
state["ts"] = NOW_ISO
state["updated"] = NOW_ISO
state["updated_at"] = NOW_ISO
state["last_seen"] = NOW_ISO
state["last_seen_at"] = NOW_ISO
state["last_round_at"] = NOW_ISO
state["last_round_closed"] = NOW_ISO
state["last_round_ts"] = EPOCH
state["last_ts"] = EPOCH
state["last_run_at"] = NOW_ISO
state["last_pulled_at"] = NOW_ISO
state["last_orders_read_at"] = NOW_ISO
state["last_decisions_read_at"] = NOW_ISO
state["last_orders_seen"] = NOW_ISO
state["last_decisions_seen"] = NOW_ISO
state["heartbeat_epoch_utc"] = EPOCH
state["current_task"] = "r981 closeout (W235 finalize verified landed + W236 yielded to bm-a in-flight + S6 41-leg zero-red + S7 quad)"
state["current_task_at"] = NOW_ISO
state["current_task_ts"] = EPOCH
state["last_action"] = "r981 closeout (S6 chain + W235 verify + W236 yield + S7 quad)"
state["last_action_at"] = NOW_ISO
if cpu_pct is not None:
    state["cpu_pct"] = cpu_pct
    state["cpu_util_pct"] = cpu_pct
    state["cpu_idle_pct"] = round(100.0 - cpu_pct, 1)
if cores is not None:
    state["cores"] = cores
    state["cpu_cores"] = cores
if ram_free_gb is not None:
    state["free_ram_gb"] = ram_free_gb
    state["idle_ram_gb"] = ram_free_gb
    state["ram_free_gb"] = ram_free_gb
if total_ram_gb is not None:
    state["total_ram_gb"] = total_ram_gb
if gpu_free_vram_mb is not None:
    state["gpu_free_vram_mb"] = gpu_free_vram_mb
    state["gpu_free_mib"] = gpu_free_vram_mb
    state["gpu_free_mb"] = gpu_free_vram_mb
    state["gpu_vram_free_mb"] = gpu_free_vram_mb
if gpu_total_vram_mib is not None:
    state["gpu_total_vram_mib"] = gpu_total_vram_mib
if gpu_util is not None:
    state["gpu_util_pct"] = gpu_util
    state["gpu_used_vram_mib"] = (gpu_total_vram_mib or 16384) - (gpu_free_vram_mb or 0)

state["did"] = (
    "r981: (1) S0-1 anchor bm-c + round-zero probe py_faces=8 orphans=2 zero-kill; S0 stash-bridge pull behind-4->0 "
    "(incoming = bm-a W235 full close: burn+sixgate 10th consecutive+finalize one-pass ledger 940,789/K 514,920 "
    "five-key ALL PASS+sec78 backfilled+own-wave closeout+their S0 absorb in-flight; pop blocked by live daemon "
    "rewrites -> stale-snapshot stash dropped live-wins, supersession verified); (2) r980 next-ptr(1) W235 "
    "finalize watch DISCHARGED -- landed+verified from origin commits (ccf10ee3d); (3) W236 chain YIELDED to bm-a "
    "per dual-open/T-18 declared-intent law (their closeout declares 'W236 seat publication next', their S0 "
    "absorb window in-flight, zero w236 files on origin both checks); (4) S0.5 ORD/DEC dual-delta FALSE both "
    "scans (opening + S7 re-scan) + repo-local unacked=0, hold ord 348eaf34 / dec 86187eff; (5) S1 smoke 49/49; "
    "S3: satengine ALIVE rc0 + wm red=false healthy + MF IC next_pick parked source-blocked (bm-a lane panel "
    "fuse-stopped) + post_review zero-x 45-pass + queue collision probe CLEAR + P2 all-done + P3 E17 leg3 "
    "bm-b lane_owner in-flight + idle green_idle=false RAM gate 1.8pct tight protect-note kept; (6) S6 full "
    "chain 41 legs ALL rc0: dualrun ZERO-DRIFT streak 51 + comp_audit ok + regime breadth 0.81 + market_clock "
    "CALL-2026-10-13 ORANGE_COOL + lane-guard no-op honest family + 10 third-signal-veto skips (host=bm-a "
    "origin commit fresh 9-10min = their window active face) + aggr/grid marks idempotent at cutoff 10-13 + "
    "REPORT-2026-10-14 + LIVE-2026-10-14 (ORANGE cap 50%) idempotent rewritten + token L2 0 today; (7) S7: "
    "attrition 4 CLEAN + loop pin=5 no-op + watchdog re-registered 04:48 + both claws installed; counter 981->982"
)
state["verify"] = (
    "receipts: 41-leg chain runner results/_r981bmc_s6_chain.py ALL rc0 + smoke 49/49 + attrition guard 4 CLEAN + "
    "s05 probe dual FALSE x2 + dualrun streak 51 zero-drift + S7 quad green (pin=5/watchdog 04:48/claws)"
)
state["verdict"] = (
    "green: W235 bm-a full-cycle finalize VERIFIED LANDED (940,789/K 514,920 five-key ALL PASS) + W236 chain "
    "correctly yielded to bm-a in-flight (anti-duplication) + zero unacked orders both scans + S6 41-leg "
    "zero-red + smoke 49/49 + S7 quad green; maintenance round with all sibling-held faces disclosed"
)
state["next"] = (
    "r982: (1) W236 seat+prereg watch -- bm-a declared + in-flight; if their window dies post-seat-landing, "
    "absorb prereg derive per seat-first law (subgen m32 pattern R34 authoring); (2) MF IC batch unpark when "
    "bm-a panel completes (fuse-stopped 30min self-heal); (3) 10-14 bars re-probe after 15:30 -> papers full "
    "chain when new bar lands; (4) MV V3 lane: director rulings on QC-r977b pending (SIL4 generation-side + "
    "SIL2/SING3b surgical-edit path) -> execute per ruling when ORD rows arrive"
)
state["next_pointer"] = state["next"]
state["next_milestone"] = (
    "W236 seat/prereg landing watch (bm-a window) -> burn chain; MV director rulings -> surgical-edit -> i2v; "
    "10-14 bars post-15:30 papers chain"
)
state["last_round_summary"] = (
    "r981: W235 finalize landed+verified (bm-a 940,789/K 514,920 five-key ALL PASS) + W236 yielded to bm-a "
    "in-flight + S6 41-leg zero-red + smoke 49/49 + zero unacked; counter 981->982"
)
state["last_round_summary_at"] = NOW_ISO
state["activity_now"] = (
    f"2026-10-14 04:4x-04:5x | r981 | bm-c: W235 finalize verified landed; W236 yielded to bm-a in-flight; "
    f"S6 41 legs zero-red | counter 981->982"
)
state["now_active"] = state["activity_now"]
state["prod_lanes"] = (
    "CPU=N1 W235: bm-a FULL CYCLE CLOSED (finalize 940,789/K 514,920 five-key ALL PASS landed ccf10ee3d); "
    "W236 seat+prereg = bm-a declared in-flight (bm-c yielded per dual-open); GPU=MV V3: director rulings "
    "pending, i2v gated on whitelist full sign"
)
state["head_sha"] = "group: b30fe44f2 (bm-a S0 absorb, in-flight window); quant: r981 closeout commit rides this window"
state["sync"] = {
    "origin_tip": "b30fe44f2 (bm-a S0 absorb in-flight; W235 full-close estate ccf10ee3d/02c18bee5 landed)",
    "ts": NOW_ISO,
    "ahead_behind": "0/0 pre-closeout (closeout commit+push rides)",
    "note": "r981: clean continuation window (round_no=981 at open, executed r981, advanced 981->982)",
}
state["latest_artifact"] = (
    "origin ccf10ee3d (bm-a W235 finalize five-key ALL PASS) + results/_r981bmc_s6_chain.py (41-leg receipt) + "
    "docs/daily_report/REPORT-2026-10-14.md + docs/live_usage/LIVE-2026-10-14.md"
)
state["last_artifact"] = state["latest_artifact"]
state["recent_artifact"] = state["latest_artifact"]
state["orders_ack_receipt"] = (
    "r981: zero unacked both scans (opening scan + S7 double-scan); group ORD/DEC dual-delta FALSE "
    "(hold ord 348eaf34 / dec 86187eff); zero bm-c execution owed this window"
)
state["orders_ack_ts"] = NOW_ISO
state["orphan_face"] = 2
state["orphan_faces"] = 2
state["r981_closeout_note"] = (
    "r981: clean continuation window (state round_no=981 at open, executed r981, advanced 981->982 so next "
    "session=r982); zero absorb owed (r980 closeout fb4941a6f landed clean, zero dead window between); "
    "zero double-count: S0.5 dual-delta FALSE both windows (ord 348eaf34 / dec 86187eff current, unacked=0); "
    "W236 chain face correctly yielded to bm-a (declared intent + in-flight window); S0 stash-bridge "
    "supersession drop disclosed (daemon live-faces rewrites blocked pop -> stale snapshots dropped live-wins)"
)

with open(STATE_PATH, "w", encoding="utf-8") as f:
    json.dump(state, f, ensure_ascii=False, indent=1)

# ---- heartbeat (fleet/machines/bm-c.json) ----
HB_PATH = os.path.join(REPO, "fleet", "machines", "bm-c.json")
with open(HB_PATH, "r", encoding="utf-8-sig") as f:
    hb = json.load(f)

hb["round_no"] = 981
hb["heartbeat_epoch_utc"] = EPOCH
hb["last_seen"] = NOW_ISO
hb["clock_read"] = NOW_ISO
hb["ts"] = NOW_ISO
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
if cpu_pct is not None:
    hb["cpu_pct"] = cpu_pct
    hb["cpu_util_pct"] = cpu_pct
    hb["cpu_idle_pct"] = round(100.0 - cpu_pct, 1)
if cores is not None:
    hb["cores"] = cores
    hb["cpu_cores"] = cores
if ram_free_gb is not None:
    hb["free_ram_gb"] = ram_free_gb
    hb["idle_ram_gb"] = ram_free_gb
    hb["ram_free_gb"] = ram_free_gb
if total_ram_gb is not None:
    hb["total_ram_gb"] = total_ram_gb
if gpu_free_vram_mb is not None:
    hb["gpu_free_vram_mb"] = gpu_free_vram_mb
    hb["gpu_free_mib"] = gpu_free_vram_mb
    hb["gpu_free_mb"] = gpu_free_vram_mb
    hb["gpu_vram_free_mb"] = gpu_free_vram_mb
    hb["gpu_idle_vram_mb"] = gpu_free_vram_mb
    hb["gpu_idle_mib"] = gpu_free_vram_mb
    hb["gpu_idle_mb"] = gpu_free_vram_mb
if gpu_total_vram_mib is not None:
    hb["gpu_total_vram_mib"] = gpu_total_vram_mib
    hb["gpu_mem_total_mib"] = gpu_total_vram_mib
if gpu_util is not None:
    hb["gpu_util_pct"] = gpu_util
    hb["gpu_mem_used_mib"] = (gpu_total_vram_mib or 16384) - (gpu_free_vram_mb or 0)
hb["current_task"] = "r981 closeout (W235 finalize verified + W236 yield + S6 41-leg + S7 quad)"
hb["prod_lanes"] = state["prod_lanes"]
hb["verdict"] = state["verdict"]
hb["health"] = "ok"

with open(HB_PATH, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# ---- self-verify: epoch int + fields present (F7 law) ----
with open(HB_PATH, "r", encoding="utf-8-sig") as f:
    hb2 = json.load(f)
with open(STATE_PATH, "r", encoding="utf-8-sig") as f:
    st2 = json.load(f)
assert isinstance(hb2.get("heartbeat_epoch_utc"), int), "epoch must be int"
assert isinstance(st2.get("heartbeat_epoch_utc"), int), "state epoch must be int"
assert "T" in hb2["clock_read"] and "+" in hb2["clock_read"], "clock_read must be ISO8601 with T and offset"
assert st2["round_no"] == 982 and st2["last_round"] == 981
print("CLOSEOUT OK | now=%s | epoch=%d | ram_free=%.1fGB | gpu_free=%sMB | cpu=%.1f%%" % (
    NOW_ISO, EPOCH, ram_free_gb or -1, gpu_free_vram_mb, cpu_pct or -1))
