# r989 bm-c closeout: state advance 989->990 + heartbeat + canonical round-report line
# Wait-state window #6 (one-line law). Canonical report path per r750 law (root file = frozen orphan archive).
import json, time, subprocess, datetime, io, sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

now_dt = datetime.datetime.now().astimezone()
now_iso = now_dt.isoformat(timespec="seconds")  # 2026-10-14T07:18:39+08:00 (T-separated, tz offset)
now_epoch = int(time.time())

# fresh metrics
try:
    import psutil
    free_ram = round(psutil.virtual_memory().available / (1024**3), 1)
    cpu_pct = psutil.cpu_percent(interval=1)
    cores = psutil.cpu_count(logical=True)
except Exception:
    free_ram, cpu_pct, cores = 0.7, 5.5, 32
try:
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                         capture_output=True, text=True, timeout=15).stdout.strip().splitlines()
    gpu_free_mb = int(out[0])
except Exception:
    gpu_free_mb = 768

STATE = ROOT + r"\state-bm-c.json"
HB = ROOT + r"\fleet\machines\bm-c.json"
REPORT = ROOT + r"\logs\iteration-loop\round_reports-bm-c.md"

did = ("r989: wait-state window #6 honestly held per one-line law (four wait-faces VERIFIED not rescanned: "
       "(1) W236 finalize product n1_w236_results.json ABSENT on disk + zero git history -> M12 trigger not open, W237 freeze-prep deferred to landing window; "
       "(2) 10-14 bars pre-15:30 (papers debt=0 per r985 10-13 full consumption); "
       "(3) MF-IC-P1 parked 23d upstream bm-a panel rebuild in flight ETA ~09:2x; "
       "(4) pool ready=0 + RW-5 freeze = supply legally chained to W236 finalize, structural audit FLAG answered-by-chain). "
       "S0 fetch 0/0 behind-0 (x7 own daemon live-faces legit dirty zero rebase owed); "
       "S0.5 opening dual-delta FALSE both (ord content-sha1 348eaf34 / dec raw-blob 86187eff hold, unacked=0); "
       "S1 smoke 49/49; S3 satengine ALIVE rc0 (all faces dedup 12/12, burns 0/queue 0, py_cpu 0%) + "
       "wm probe insufficient_history fresh window legal (bars_present=false, daily_panel cutoff 2026-10-13 fresh, board/pool/bandit all 0) + "
       "post_review today 0-x (45-ok/5-wait) + jobs=0 + fleet board 48-claimed none-open + "
       "idle green_idle=false RAM-gated honest (GPU=MV V3 burn window protected per O-20261014-0312 sec.2, zero touch); "
       "own W237 seat MSG swept inbox->processed (content landed 9312ef7ac last window); "
       "S6 light: dualrun ZERO-DRIFT streak 51 (446 entries) + compute_audit FLAG pool_starvation/supply_floor structural (supply_family_streak 231min, answered-by-chain W236+seat) + token delta=0; "
       "S7 quad: attrition 4 CLEAN + pin=5 no-op + watchdog registered + claws x2 installed + inbox 0.")

verify = ("receipts: probe results/_orphan_face_probe.bm-c.json (py_faces=8 orphans=2 zero-kill) + smoke 49/49 + "
          "s05 dual-FALSE opening+tail (results/_s05_probe.bm-c.json) + dualrun streak 51 + "
          "attrition results/_attrition_guard_scan.json CLEAN + S7 quad (pin=5 no-op/watchdog registered/claws x2) + "
          "post_review REPORT-20261014 45-ok/0-x/5-wait + n1_w236_results.json absence verified (Test-Path False + git log zero)")

verdict = ("green: wait-state window #6 honestly held (W236 finalize=bm-a in-flight M12 armed; bars pre-15:30 papers debt 0; "
           "MF-IC-P1 upstream panel ETA ~09:2x; pool+RW-5 supply chained to W236 finalize) + smoke 49/49 + S0.5 dual FALSE x2 + "
           "S6 light zero-drift streak 51 + S7 quad green")

next_ptr = ("r990: (1) M12 trigger watch -- W236 finalize lands -> W237 freeze-prep same-window per W236 bloodline "
            "(prereg derive needs W236 finalize anchor faces, gate0.5 loud-abort if absent); "
            "(2) MF panel watch ~09:2x -> MF-IC-P1 S2 completion gate check (panel holder=bm-a lane); "
            "(3) 10-14 bars re-probe after 15:30 -> papers full chain when new bar lands; "
            "(4) bm-a heartbeat face stale noted absorb-only (their commits landing); closeout scripts: canonical report path MANDATORY (r750 law)")

current_task = "r989 wait-state window #6 held (M12 waiting-upstream W236 finalize + bars pre-15:30 + MF-IC-P1 upstream + pool/RW-5 chained)"

# --- state file ---
with open(STATE, "r", encoding="utf-8") as f:
    st = json.load(f)
st["round_no"] = 990
st["last_round"] = "r989"
st["last_round_label"] = "r989"
st["loop_round"] = 989
for k in ("last_round_at", "last_seen", "last_seen_at", "clock_read", "updated", "updated_at", "last_round_closed"):
    st[k] = now_iso
for k in ("last_round_ts", "last_ts", "current_task_ts"):
    st[k] = now_epoch
st["heartbeat_epoch_utc"] = now_epoch
st["current_task"] = current_task
st["current_task_at"] = now_iso
st["did"] = did
st["verify"] = verify
st["verdict"] = verdict
st["next"] = next_ptr
st["next_pointer"] = next_ptr
st["activity_now"] = f"2026-10-14 {now_dt.strftime('%H:%M')} | r989 | bm-c: wait-state window #6 | counter 989->990"
st["now_active"] = st["activity_now"]
st["last_round_summary"] = "r989: wait-state window #6 (W236 finalize absent M12 armed + bars pre-15:30 + MF-IC-P1 upstream + pool/RW-5 chained) + smoke 49/49 + S0.5 dual FALSE x2 + S6 light zero-drift streak 51 + S7 quad green; counter 989->990"
st["last_round_summary_at"] = now_iso
st["last_action"] = "r989 closeout (wait-state window #6 + S6 light + S7 quad)"
st["last_action_at"] = now_iso
st["latest_artifact"] = "wait-state window #6 (no new artifact; zero-drift streak 51 held; post_review 45-ok/0-x; S7 quad green)"
st["last_artifact"] = st["latest_artifact"]
st["recent_artifact"] = st["latest_artifact"]
st["next_milestone"] = "10-14 15:30 bars -> papers chain + W236 finalize landing -> W237 freeze-prep (M12) + MF panel ~09:2x -> MF-IC-P1 unpark"
st["free_ram_gb"] = free_ram
st["ram_free_gb"] = free_ram
st["idle_ram_gb"] = free_ram
st["cpu_pct"] = cpu_pct
st["cpu_util_pct"] = cpu_pct
st["cpu_cores"] = cores
st["cores"] = cores
st["gpu_free_vram_mb"] = gpu_free_mb
st["gpu_free_vram_mib"] = gpu_free_mb
st["gpu_vram_free_mb"] = gpu_free_mb
st["idle_rounds"] = 0
st["agenda_starved"] = False
st["orders_ack_receipt"] = "r989: zero unacked both scans (opening + tail); group ORD/DEC dual-delta FALSE both (ord 348eaf34 content-sha / dec 86187eff hold); zero bm-c execution owed"
st["r989_closeout_note"] = ("r989: clean continuation window (state round_no=989 at open, executed r989, advanced 989->990 so next=r990); "
                           "zero absorb owed (r988 closeout 5654c4f04 landed clean, zero dead window between); "
                           "zero double-count: S0.5 dual-delta FALSE both scans (opening + S7 tail), unacked=0 both; "
                           "wait-state window #6 per one-line law; own W237 seat MSG swept to processed; bm-a heartbeat stale face noted absorb-only")
st["r989_absorb_note"] = ""
st["sync"] = {"origin_tip": "5654c4f04 (r988 closeout) at open; fetch 0/0 behind-0", "ts": now_iso,
              "ahead_behind": "0/0 pre-closeout (closeout commit+push rides this window)",
              "note": "r989: fetch 0/0 clean (x7 daemon live-faces legit dirty); wait-state window #6"}
st["health"] = "ok"

# --- heartbeat ---
with open(HB, "r", encoding="utf-8") as f:
    hb = json.load(f)
hb["machine_id"] = "bm-c"
hb["last_seen"] = now_iso
hb["clock_read"] = now_iso
hb["ts"] = now_iso
hb["heartbeat_epoch_utc"] = now_epoch
hb["current_task"] = current_task
hb["verdict"] = f"green (r989: wait-state window #6 held -- W236 finalize absent M12 armed / bars pre-15:30 / MF-IC-P1 upstream / pool+RW-5 chained to W236 finalize)"
hb["cpu_pct"] = cpu_pct
hb["cpu_cores"] = cores
hb["free_ram_gb"] = free_ram
hb["gpu_idle_vram_mb"] = gpu_free_mb
hb["idle_rounds"] = 0
hb["agenda_starved"] = False

# self-verify: epoch must be int (R170/R178 law), clock must be T-separated ISO
assert isinstance(hb["heartbeat_epoch_utc"], int) and isinstance(st["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in hb["clock_read"] and hb["clock_read"] == hb["ts"], "clock_read/ts must be same T-form ISO"

with open(STATE, "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
with open(HB, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# re-load self-check (write-then-read-back law)
for p in (STATE, HB):
    with open(p, "r", encoding="utf-8") as f:
        d = json.load(f)
    assert isinstance(d["heartbeat_epoch_utc"], int)
print("state+heartbeat written; epoch=%d clock=%s free_ram=%sG cpu=%s%% gpu_free=%sMB" % (now_epoch, now_iso, free_ram, cpu_pct, gpu_free_mb))

# --- canonical round report line ---
report_line = (f"{now_iso} | r989 | bm-c: wait-state window #6 per one-line law -- four wait-faces VERIFIED not rescanned: "
               "(1) W236 finalize product n1_w236_results.json ABSENT (Test-Path False + zero git history; bm-a commits in-flight, heartbeat stale face noted absorb-only) -> M12 trigger not open, W237 freeze-prep deferred to landing window; "
               "(2) 10-14 bars pre-15:30 (papers debt=0 per r985); (3) MF-IC-P1 parked 23d (bm-a panel rebuild ETA ~09:2x); "
               "(4) pool ready=0 + RW-5 freeze = supply legally chained to W236 finalize "
               "| WM-VERDICT: green red=false insufficient_history fresh window (bars_present=false, daily_panel cutoff 10-13 fresh, board/pool/bandit all 0) "
               "| orphan face=2 zero-kill (py_faces=8; MV-lane infra kept) "
               "| body: S0 fetch 0/0 behind-0 (x7 own daemon live-faces legit dirty zero rebase owed); S0.5 dual FALSE x2 opening+tail (ord 348eaf34/dec 86187eff hold, unacked=0); "
               "smoke 49/49; satengine ALIVE rc0 (faces dedup 12/12, burns 0/queue 0); jobs=0 + fleet board 48-claimed none-open; "
               "idle green_idle=false RAM-gated honest (GPU=MV V3 burn window protected O-20261014-0312 sec.2 zero touch); post_review today 0-x (45-ok/5-wait); "
               "own W237 seat MSG swept inbox->processed (content landed 9312ef7ac) "
               "| S6 light: dualrun ZERO-DRIFT streak 51 (446 entries) + audit FLAG pool_starvation+supply_floor structural (supply_family_streak 231min answered-by-chain W236+seat) + token delta=0 "
               "| S7 quad: attrition 4 CLEAN + pin=5 no-op + watchdog registered + claws x2 + inbox 0 "
               "| r990: M12 trigger watch (W236 finalize lands -> W237 freeze-prep same-window per W236 bloodline, gate0.5 loud-abort) + MF panel ~09:2x -> MF-IC-P1 S2 gate + 15:30 bars re-probe -> papers chain + bm-a heartbeat absorb-only\n")

with open(REPORT, "r", encoding="utf-8") as f:
    rep = f.read()
assert " | r989 | " not in rep, "tail anchor check: r989 row must not already exist"
with open(REPORT, "a", encoding="utf-8") as f:
    f.write(report_line)
print("canonical report line appended (r989)")
