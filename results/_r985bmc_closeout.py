import json, time, subprocess, os, datetime

BM = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CANON_RPT = os.path.join(BM, "logs", "iteration-loop", "round_reports-bm-c.md")  # r750 law canonical path
now = datetime.datetime.now()
now_iso = now.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
epoch = int(time.time())

def read_cpu_ram():
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=1)
        ram_free = round(psutil.virtual_memory().available / (1024**3), 1)
        return cpu, ram_free
    except Exception:
        return None, None

def read_gpu():
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.free",
                              "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=10)
        parts = [x.strip() for x in out.stdout.splitlines()[0].split(",")]
        return int(parts[0]), int(parts[1])
    except Exception:
        return None, None

cpu, ram_free = read_cpu_ram()
gpu_util, gpu_free_mib = read_gpu()

# --- 1) state-bm-c.json ---
sp = os.path.join(BM, "state-bm-c.json")
st = json.load(open(sp, encoding="utf-8"))
prev_round = st.get("round_no", 985)
assert prev_round == 985, f"state round_no {prev_round} != 985 - absorb check owed"
st["round_no"] = prev_round + 1
st["r985_closeout_note"] = ("r985: (1) S0-1 anchor bm-c + round-zero probe py_faces=9 orphans=2 zero-kill; S0 fetch 0/0 clean "
    "(x6 daemon live-faces legit dirty, no rebase owed); (2) S0.5 dual-delta FALSE both scans (opening + S7 tail; "
    "ord 53582389 / dec 86187eff hold per state keys; unacked=0); (3) S1 smoke 49/49; (4) S3: satengine ALIVE rc0 "
    "(W235 12/12, W236=bm-a chain in-flight prereg 67ade8314 landed 05:1x, splice/burn/finalize theirs per seat-first) "
    "+ wm red=false insufficient_history fresh window (bars_present=false, daily_panel cutoff 2026-10-13 fresh) "
    "+ jobs=0 + P2 queue empty (T5-T26 all done) + P3 head E17=bm-b declared lane (N2U3-LEG3-TRAIN closed done by bm-b "
    "d6b569d6f) + idle green_idle=false RAM-gated honest not-claim-eligible (GPU lane=MV V3 protected per O-20261014-0312 sec.2); "
    "(5) WAIT-STATE faces held per one-line law (10-14 bars not due until 15:30 -- papers chain debt check: 10-13 bar fully "
    "consumed, export-2026-10-13.json landed 00:09 + grid marks 23:13, zero papers debt owed; MF-IC-P1 parked 21d upstream "
    "bm-a collector, relay MSG-0512 standing; pool ready=0 + RW-5 freeze = supply legally chained to W236 finalize [bm-a]); "
    "(6) 5x DUTY + PRODUCT: HANDOVER row r985 landed (window r916-r985, 12 missed 5x stamps disclosed) + LEDGER PATH-SPLIT "
    "3rd INSTANCE HEAL (r749/r780 family): r958-r984 closeout scripts wrote round rows to ROOT orphan file (canonical face "
    "stalled at r957) -> r985 line-level union 20 rows verbatim (19 labels, r967 x2) + 8 never-written rounds "
    "(r960/961/964/966/972/973/978/979) consolidated backfill marker (fu-shu prohibition: no retroactive fabrication, "
    "authoritative faces = state closeout/absorb notes + git commits) + root freeze pointer + THIS closeout script writes "
    "the CANONICAL path (r750 law restored); treasure_guard prescan rc3 honored -> line-level union carve-out; "
    "receipt results/_r985bmc_ledger_heal_receipt.json (block sha256 bf4b1c28..., byte equation verified); "
    "(7) S6 light: dualrun ZERO-DRIFT streak 51 + compute_audit FLAG supply_floor structural (ready 0<floor 3, "
    "answered-by-chain W236) + update_daily no-op cutoff 2026-10-13 + token delta=0 L2 legs 0 today; "
    "(8) S7: attrition 4 CLEAN (1 healed historical note) + pin=5 no-op + watchdog re-registered + both claws MATCH "
    "+ tail dual-scan FALSE zero-new")
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# --- 2) heartbeat ---
hp = os.path.join(BM, "fleet", "machines", "bm-c.json")
hb = json.load(open(hp, encoding="utf-8"))
hb["last_seen"] = now_iso
hb["ts"] = now_iso
hb["clock_read"] = now_iso
hb["heartbeat_epoch_utc"] = epoch
hb["heartbeat_epoch_utc_type"] = "int"
hb["round_no"] = prev_round + 1
hb["round_no_label"] = "r985"
hb["last_round"] = prev_round
hb["last_round_at"] = now_iso
hb["last_round_ts"] = epoch
hb["loop_round"] = prev_round + 1
hb["current_task"] = "r985 wait-state window + 5x duty close (ledger path-split heal + HANDOVER r985 row + S7 quad)"
hb["current_task_at"] = now_iso
hb["current_task_ts"] = epoch
hb["last_artifact"] = "ledger path-split heal 3rd instance (20-row verbatim union r958-r984 + 8-round consolidated marker, receipt results/_r985bmc_ledger_heal_receipt.json)"
hb["recent_artifact"] = hb["last_artifact"]
hb["latest_artifact"] = hb["last_artifact"]
hb["next_milestone"] = "10-14 bars post-15:30 papers chain + W236 finalize watch (bm-a) -> W237 seat chain + MF panel completion -> MF-IC-P1 unpark"
hb["prod_lanes"] = ("CPU=N1 W236: bm-a chain in-flight (prereg 67ade8314 landed 05:1x; splice/burn/finalize theirs; "
    "bm-c yielded per seat-first); MF-IC-P1: parked 21d source-blocked (bm-a collector code-crash, relay MSG-0512 standing); "
    "GPU=MV V3: director rulings pending, i2v gated")
hb["activity_now"] = f"2026-10-14 06:0x | r985 | bm-c: ledger path-split heal + HANDOVER 5x row + wait-state close | counter {prev_round}->{prev_round+1}"
hb["now_active"] = hb["activity_now"]
hb["did"] = st["r985_closeout_note"]
hb["verdict"] = ("green: wait-state faces held (bars not due 15:30, 10-13 papers debt zero; W236=bm-a active chain yield held; "
    "MF-IC-P1 upstream-blocked 21d disclosed; pool ready=0 + RW-5 freeze; idle RAM-gated honest) + 5x duties landed "
    "(HANDOVER r985 row + ledger heal product, line-level union zero-delete) + smoke 49/49 + S6 light zero-drift + S7 quad green")
hb["next"] = ("r986: (1) W236 chain watch -- bm-a in-flight (absorb ONLY if their window dies post-seat per seat-first law); "
    "(2) 10-14 bars re-probe after 15:30 -> papers full chain when new bar lands; "
    "(3) MF collector fix watch -- if bm-a panel completes, MF-IC-P1 S2 completion gate check; "
    "(4) MV V3 director rulings watch; closeout scripts: canonical report path is MANDATORY (r750 law, this round healed 3rd instance)")
hb["next_pointer"] = hb["next"]
hb["last_round_summary"] = ("r985: wait-state + 5x duty window (ledger path-split 3rd-instance heal = 20-row verbatim union + 8-round marker + "
    "canonical path restored; HANDOVER r985 row landed, 12 missed stamps disclosed; W236=bm-a in-flight yield; bars not due; "
    "MF-IC-P1 parked 21d; pool 0 + RW-5 freeze) + S0.5 dual-delta FALSE x2 + smoke 49/49 + S6 light zero-drift streak 51 + S7 quad green; counter 985->986")
hb["last_action"] = "r985 closeout (ledger heal + HANDOVER 5x + S6 light + S7 quad)"
hb["last_action_at"] = now_iso
hb["orders_ack_receipt"] = ("r985: zero unacked both scans (opening + S7 tail); group ORD/DEC dual-delta FALSE both "
    "(ord 53582389 / dec 86187eff hold); zero bm-c execution owed this window")
hb["orders_ack_ts"] = now_iso
hb["last_pulled_at"] = now_iso
hb["last_round_closed"] = now_iso
hb["last_round_summary_at"] = now_iso
hb["verify"] = ("receipts: probe results/_orphan_face_probe.bm-c.json + smoke 49/49 + s05 dual-FALSE x2 "
    "+ ledger heal results/_r985bmc_ledger_heal_receipt.json (byte equation + per-label counts asserted) "
    "+ HANDOVER insert-only diff (1 insertion) + dualrun streak 51 + attrition results/_attrition_guard_scan.json CLEAN + S7 quad (pin=5/watchdog/claws x2)")
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["orphan_face"] = 2
hb["orphan_faces"] = 2
hb["health"] = "ok"
if cpu is not None:
    hb["cpu_pct"] = cpu
    hb["cpu_util_pct"] = cpu
    hb["cpu_idle_pct"] = round(100 - cpu, 1)
if ram_free is not None:
    hb["free_ram_gb"] = ram_free
    hb["ram_free_gb"] = ram_free
    hb["idle_ram_gb"] = ram_free
if gpu_util is not None:
    hb["gpu_util_pct"] = gpu_util
if gpu_free_mib is not None:
    hb["gpu_free_vram_mb"] = gpu_free_mib
    hb["gpu_free_mib"] = gpu_free_mib
    hb["gpu_idle_mb"] = gpu_free_mib
    hb["gpu_idle_vram_mb"] = gpu_free_mib
    hb["gpu_free_vram_gb"] = round(gpu_free_mib / 1024, 1)
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# self-verify epoch int type + clock format
hb2 = json.load(open(hp, encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in hb2["clock_read"], "clock_read must be T-separated"

# --- 3) round report row (CANONICAL PATH - r750 law) ---
row = (f"{now_iso} | r985 | bm-c wait-state+5x-duty window close | WM-VERDICT: green red=false (insufficient_history fresh window; "
    "bars_present=false + daily_panel cutoff 2026-10-13 fresh + 10-13 papers chain verified consumed zero-debt) | "
    f"orphan face=2 zero-kill (py_faces=9; MV-lane infra kept) | body: S0 fetch 0/0 clean (x6 daemon live-faces); "
    "S0.5 dual-delta FALSE both scans (ord 53582389/dec 86187eff hold, unacked=0); smoke 49/49; S3 satengine ALIVE rc0 "
    "(W236=bm-a chain in-flight prereg 67ade8314, yield per seat-first) + jobs=0 + P2 empty + P3 head E17=bm-b declared lane "
    "+ idle green_idle=false RAM-gated honest (GPU=MV V3 protected O-20261014-0312 sec.2); wait-state faces held one-line law "
    "(bars not due 15:30; MF-IC-P1 parked 21d upstream, relay MSG-0512 standing; pool ready=0 + RW-5 freeze supply chained W236 [bm-a]); "
    "PRODUCT (5x duty): (a) HANDOVER r985 row landed (window r916-r985, 12 missed 5x stamps disclosed honestly); "
    "(b) LEDGER PATH-SPLIT 3rd-instance heal (r749/r780 family): r958-r984 closeout scripts wrote rows to ROOT orphan file, "
    "canonical stalled at r957 -> line-level union 20 rows verbatim (r958/959/962/963/965/967x2/968/969/970/971/974/975/976/977/980/981/982/983/984) "
    "+ 8 never-written rounds consolidated marker (r960/961/964/966/972/973/978/979 - fu-shu prohibition, authoritative faces=state notes+git commits) "
    "+ root freeze pointer + closeout script canonical path restored; treasure_guard rc3 line-level-union carve-out honored; "
    "S6 light: dualrun ZERO-DRIFT streak 51 + audit FLAG supply_floor structural (answered-by-chain W236) + token delta=0; "
    "S7: attrition 4 CLEAN + pin=5 no-op + watchdog re-registered + claws x2 MATCH + tail dual-scan FALSE "
    "| evidence: results/_r985bmc_ledger_heal_receipt.json (block sha256 bf4b1c28... byte-equation asserted) + "
    "results/_r985bmc_ledger_probe.py + results/_orphan_face_probe.bm-c.json + smoke 49/49 + attrition CLEAN | "
    "本地未达 origin commit 数=0 (post-push delivery self-check this window; next-window S0 re-verify) | "
    "r986: W236 bm-a chain watch (absorb only if window dies post-seat) + 15:30 bars re-probe -> papers chain + MF panel watch + MV V3 rulings watch + closeout scripts canonical-path MANDATORY\n")
with open(CANON_RPT, "a", encoding="utf-8") as f:
    f.write(row)

print(f"closeout written: state round_no {prev_round}->{prev_round+1}; heartbeat epoch={epoch} int-verified; report row appended to CANONICAL path")
