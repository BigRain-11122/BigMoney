import json, time, subprocess, os, datetime

BM = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
now = datetime.datetime.now()
now_iso = now.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
epoch = int(time.time())

# --- machine readings ---
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
prev_round = st.get("round_no", 984)
st["round_no"] = prev_round + 1
st["r984_closeout_note"] = ("r984: (1) S0-1 anchor bm-c + round-zero probe py_faces=8 orphans=2 zero-kill; "
    "S0 stash->pull --rebase->pop clean (r923bmb estate landed; daemon state files x6 legit dirty, zero conflict); "
    "(2) S0.5 dual-delta TRUE both consumed: ORD ae5d7cda->53582389 (new rows = 10-13 23:5x V3-fix relay + tail rows, BigStream MV lane, zero BigMoney execution) "
    "+ DEC 2bf2a0ef->86187eff (new row = C-20261013-01 group cleanup case executed, targets=BigStream/MiniGame group-tree files, zero BigMoney execution) "
    "+ unacked local=0 both scans (opening + S7 tail, sha-identity 86187eff/53582389 verified zero mid-round rows); "
    "(3) S1 smoke 49/49; (4) S3: satengine ALIVE rc0 (burns 0/queue 0, W236=bm-a seat 5c25db795 04:46 in-flight, chain theirs per seat-first) "
    "+ wm red=false healthy wait-state (next_pick=claimed MF-IC-P1 parked source-blocked) + post_review today ✗0 (✓45/🟡5, 05:00:48 sweep) "
    "+ jobs=0 + idle green_idle=false RAM 1.8pct honest not-claim-eligible (GPU lane=MV V3 burn window protected per O-20261014-0312 sec.2); "
    "(5) WAIT-STATE WINDOW held per one-line law (10-14 bars not due until 15:30; MF-IC-P1 parked 20d at S2 gate, collector fix=bm-a lane, MSG-0512 relay in inbox addressed to bm-a; "
    "pool ready=0 sole-entry claimed-by-bm-b N2U3 + RW-5 freeze bans new prereg first-intake = supply legally chained to W236 finalize [bm-a]); "
    "(6) S6 light: dualrun ZERO-DRIFT streak 51 + compute_audit FLAG supply_floor structural (ready 0<floor 3, answered-by-chain W236) + token delta=0 L2 legs 0 today; "
    "(7) S7: attrition 4 CLEAN + pin=5 no-op + watchdog re-registered + both claws installed + tail dual-scan zero-new; "
    "pitfall same-window: s05 probe first-print GBK UnicodeEncodeError on emoji -> PYTHONIOENCODING=utf-8 rerun (known pit-encoding face, zero data loss)")
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
hb["round_no_label"] = "r984"
hb["last_round"] = prev_round
hb["last_round_at"] = now_iso
hb["last_round_ts"] = epoch
hb["loop_round"] = prev_round + 1
hb["current_task"] = "r984 wait-state window close (S0.5 dual-consume + S6 light + S7 quad)"
hb["current_task_at"] = now_iso
hb["current_task_ts"] = now_iso
hb["last_artifact"] = "wait-state window (no new artifact; S0.5 dual-delta consume + probe evidence _r984bmc_s05_probe.json)"
hb["recent_artifact"] = hb["last_artifact"]
hb["latest_artifact"] = hb["last_artifact"]
hb["next_milestone"] = "10-14 bars post-15:30 papers chain + W236 finalize watch (bm-a) -> W237 seat chain + MF panel completion -> MF-IC-P1 unpark"
hb["prod_lanes"] = ("CPU=N1 W236: bm-a chain in-flight (seat 5c25db795 04:46, prereg/splice/burn/finalize theirs; bm-c yield held per seat-first); "
    "MF-IC-P1: parked 20d source-blocked (bm-a collector code-crash, MSG-0512 in inbox for them); GPU=MV V3 burn window (director fix rounds relayed 10-13 23:5x, rulings pending)")
hb["activity_now"] = f"2026-10-14 05:4x | r984 | bm-c: wait-state window close | counter {prev_round}->{prev_round+1}"
hb["now_active"] = hb["activity_now"]
hb["did"] = st["r984_closeout_note"]
hb["verdict"] = ("green: wait-state window honestly held (bars not due 15:30; W236=bm-a active chain yield held; MF-IC-P1 source-blocked upstream 20d; "
    "pool ready=0 sole-entry claimed by bm-b + RW-5 freeze = no new supply line legal; idle RAM-gated 1.8pct; GPU=MV V3 protected window) "
    "+ S0.5 dual-delta consumed both + smoke 49/49 + post_review ✗0 + S6 light zero-drift + S7 quad green")
hb["next"] = ("r985: (1) W236 chain watch continues -- bm-a in-flight (absorb ONLY if their window dies post-seat per seat-first law); "
    "(2) MF collector fix watch -- if bm-a panel completes, MF-IC-P1 S2 completion gate check; "
    "(3) 10-14 bars re-probe after 15:30 -> papers full chain when new bar lands; (4) MV V3 director rulings watch (GPU lane)")
hb["next_pointer"] = hb["next"]
hb["last_round_summary"] = ("r984: wait-state window hold (W236=bm-a in-flight yield + MF-IC-P1 parked 20d + bars not due + RW-5 freeze) "
    "+ S0.5 dual-delta TRUE consumed both (ORD V3-relay rows / DEC C-20261013-01 cleanup row, zero BigMoney action) "
    "+ smoke 49/49 + post_review ✗0 + S6 light zero-drift streak 51 + S7 quad green; counter 984->985")
hb["last_action"] = "r984 closeout (S0.5 dual-consume + S6 light + S7 quad)"
hb["last_action_at"] = now_iso
hb["orders_ack_receipt"] = ("r984: zero unacked both scans (opening + S7 tail sha-identity); group ORD/DEC dual-delta TRUE consumed both "
    "(ord 53582389 = BigStream MV lane rows; dec 86187eff = C-20261013-01 group cleanup executed row); zero bm-c execution owed this window")
hb["orders_ack_ts"] = now_iso
hb["last_decisions_sha"] = "86187eff59851ded73aa827b6251ca997adf57318e74571800c6838bdffc04e7"
hb["last_decisions_read_at"] = now_iso
hb["last_decisions_at"] = now_iso
hb["last_decisions_seen"] = now_iso
hb["last_decisions_read_note"] = ("r984: DEC delta TRUE 2bf2a0ef->86187eff consumed (C-20261013-01 集团工作区清理案 executed row "
    "[安全层45件删除+正典层53件点名导演席+orders/decisions 不拆分>1MB专项] -- 点名对象=BigStream/MiniGame 集团树文件·涉本司零执行件·水位推进)")
hb["last_orders_sha"] = "53582389766e6ba4f3d1c89504d442e131b97601"
hb["last_orders_at"] = now_iso
hb["last_orders_read_at"] = now_iso
hb["last_orders_seen"] = now_iso
hb["last_orders_sha_note"] = "r984: ORD delta TRUE ae5d7cda->53582389 consumed (new rows = 10-13 23:5x @bm-c V3 修批 relay + 22:5x 委员会清理案行 -- BigStream MV 车道·涉本司零执行件)"
hb["last_pulled_at"] = now_iso
hb["last_round_closed"] = now_iso
hb["last_round_summary_at"] = now_iso
hb["verify"] = ("receipts: probe results/_orphan_face_probe.bm-c.json + smoke 49/49 + s05 dual-consume results/_r984bmc_s05_probe.json/_consume.json "
    "+ dualrun streak 51 + attrition results/_attrition_guard_scan.json CLEAN + S7 quad (pin=5/watchdog/claws x2)")
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

# self-verify epoch int type
hb2 = json.load(open(hp, encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in hb2["clock_read"], "clock_read must be T-separated"

# --- 3) round report ---
rp = os.path.join(BM, "round_reports-bm-c.md")
line = (f"{now_iso} | r984 | S0-1 anchor+probe(8/2/0)·S0 stash-pull-pop(r923bmb estate landed·x6 state files legit)·"
    "S0.5 dual-delta TRUE consumed both (ORD 53582389=V3-fix relay rows/DEC 86187eff=C-20261013-01 cleanup row·涉本司零执行件·unacked=0 opening+tail sha-identity)·"
    "S1 49/49·S3 satengine ALIVE(burns 0/queue 0·W236=bm-a seat in-flight yield)+wm red=false wait-state(next_pick=claimed MF-IC-P1 parked)·"
    "post_review ✗0(✓45/🟡5)·jobs 0·idle green_idle=false RAM 1.8%(GPU=MV V3 burn window protected O-20261014-0312 §2)·"
    "S6 light dualrun ZERO-DRIFT streak 51+audit FLAG supply_floor structural(ready 0<3·answered-by-chain W236·RW-5 freeze=no new line legal)+token 0·"
    "S7 attrition 4 CLEAN+pin5 no-op+watchdog re-reg+claws x2+counter 984->985 | "
    "smoke 49/49·probe results/_r984bmc_s05_probe.json·attrition results/_attrition_guard_scan.json | "
    "r985: W236 bm-a chain watch(absorb only if window dies post-seat)·MF panel watch->S2 gate check·15:30 bars re-probe->papers chain·MV V3 rulings watch\n")
with open(rp, "a", encoding="utf-8") as f:
    f.write(line)

print(f"closeout written: state round_no {prev_round}->{prev_round+1}; heartbeat epoch={epoch} int-verified; report appended")
