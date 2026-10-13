# r983 bm-c closeout: round report line + heartbeat + state (wait-state window)
# Fields machine-derived, zero literal watermark constants (r583 law).
import json, time, io, os

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW_ISO = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
NOW_EPOCH = int(time.time())

did = ("r983: (1) S0-1 anchor bm-c + round-zero probe py_faces=9 orphans=2 zero-kill; S0 fetch behind-0/0 "
       "(daemon live-face dirty x5, no rebase owed); (2) S0.5 ORD/DEC dual-delta FALSE both scans (opening + S7 tail; "
       "hold ord/dec watermarks per state keys; unacked=0); (3) S1 smoke 49/49; S3: satengine ALIVE rc0 (W235 12/12 dedup, "
       "W236=bm-a seat 5c25db795 04:46 in-flight, chain theirs per seat-first) + wm red=false healthy wait-state "
       "(next_pick=claimed MF-IC-P1 parked source-blocked) + post_review 0 non-YES-non-WAIT since 10-14 (05:00:48 "
       "sweep clean, 51 NO historical) + pool ready=1 N2U3-LEG3-TRAIN claimed-by-bm-b 05:02 (E3 zero-touch) + jobs=0 "
       "+ idle green_idle=false RAM 1.8pct honest not-claim-eligible; (4) WAIT-STATE WINDOW declared per one-line law: "
       "10-14 bars not due until 15:30, W236 prereg/splice/burn/finalize = bm-a lane in-flight, MF-IC-P1 parked 20d at "
       "S2 completion gate (bm-a collector code-crash, relay MSG-20261014-0512 in inbox for them), MV V3 director "
       "rulings not arrived; (5) S6 light: dualrun ZERO-DRIFT streak 51 + compute_audit FLAG supply_gap/supply_floor "
       "structural (ready 1<floor 3, unclaimed 0, answered-by-seat W236=bm-a chain) + token delta=0 L2 legs 0 today; "
       "(6) S7: attrition 4 CLEAN + pin=5 no-op + watchdog re-registered + both claws installed + tail dual-scan FALSE; "
       "counter 983->984")

verdict = ("green: wait-state window honestly declared (bars not due 15:30; W236=bm-a active chain yield held; "
           "MF-IC-P1 source-blocked upstream 20d disclosed; pool sole-ready claimed by bm-b; idle RAM-gated 1.8pct) "
           "+ S6 light zero-drift + smoke 49/49 + post_review zero-x + S7 quad green")

next_ptr = ("r984: (1) W236 chain watch continues -- bm-a in-flight (prereg/splice/burn/finalize theirs; absorb ONLY "
            "if their window dies post-seat per seat-first law); (2) MF collector fix watch -- if bm-a panel completes, "
            "MF-IC-P1 S2 completion gate check -> batch run per S0 lane-ruling-4 (execution machine = panel holder); "
            "(3) 10-14 bars re-probe after 15:30 -> papers full chain when new bar lands; (4) MV V3 director rulings "
            "watch -- execute per ruling when ORD rows arrive")

summary = ("r983: wait-state window (W236=bm-a in-flight yield + MF-IC-P1 parked 20d + bars not due + rulings not "
           "arrived) + dual-delta FALSE x2 + smoke 49/49 + S6 light zero-drift + S7 quad green; counter 983->984")

artifact = "wait-state window (no new artifact; watch faces only; sole pool entry claimed by bm-b)"

# --- round report line (append, fixed five-field format) ---
rr_path = os.path.join(ROOT, "round_reports-bm-c.md")
line = ("2026-10-14 05:2x | r983 | bm-c wait-state window close (W236 yield + MF-IC-P1 parked + bars not due + zero "
        "unacked + zero idle-eligible) | smoke 49/49 + s05 dual FALSE x2 + dualrun streak 51 + attrition 4 CLEAN + S7 "
        "quad + post_review 0-x | r984: W236 watch (bm-a chain) + MF panel watch -> MF-IC-P1 unpark + 10-14 bars "
        "post-15:30 papers chain + MV rulings watch\n")
with io.open(rr_path, "a", encoding="utf-8", newline="") as f:
    f.write(line)

# --- heartbeat ---
hb_path = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
hb = json.load(io.open(hb_path, encoding="utf-8"))
hb.update({
    "last_seen": NOW_ISO, "ts": NOW_ISO, "updated": NOW_ISO, "updated_at": NOW_ISO,
    "heartbeat_epoch_utc": NOW_EPOCH,
    "current_task": "r983 wait-state close (W236 yield watch + MF panel watch + bars pre-15:30)",
    "current_task_at": NOW_ISO,
    "now_active": "2026-10-14 05:2x | r983 | bm-c: wait-state window close | counter 983->984",
    "activity_now": "2026-10-14 05:2x | r983 | bm-c: wait-state window close | counter 983->984",
    "last_round": 983, "last_round_at": NOW_ISO, "round_no": 984, "round_no_label": "r983",
    "did": did, "verdict": verdict, "next": next_ptr, "next_pointer": next_ptr,
    "last_round_summary": summary,
    "latest_artifact": artifact, "last_artifact": artifact, "recent_artifact": artifact,
    "next_milestone": "10-14 bars post-15:30 papers chain + W236 finalize watch (bm-a) + MF panel completion -> MF-IC-P1 unpark",
    "orders_ack_receipt": "r983: zero unacked both scans (opening + S7 tail); group ORD/DEC dual-delta FALSE (hold ord/dec per state); zero bm-c execution owed this window",
    "orders_ack_ts": NOW_ISO,
    "orphan_face": 2, "orphan_faces": 2,
    "idle_rounds": 0, "agenda_starved": False,
    "head_sha": "r983 closeout commit rides this window",
    "verify": "receipts: probe results/_orphan_face_probe.bm-c.json + smoke 49/49 + s05 dual FALSE x2 + dualrun streak 51 + attrition results/_attrition_guard_scan.json CLEAN + S7 quad (pin=5/watchdog/claws)",
    "prod_lanes": ("CPU=N1 W236: bm-a chain in-flight (seat landed 5c25db795 04:46, prereg next theirs; bm-c yielded per seat-first); "
                   "MF-IC-P1: parked 20d source-blocked (bm-a collector code-crash, relay MSG-0512 in inbox); GPU=MV V3: director rulings pending"),
})
with io.open(hb_path, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
chk = json.load(io.open(hb_path, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"

# --- state ---
st_path = os.path.join(ROOT, "state-bm-c.json")
st = json.load(io.open(st_path, encoding="utf-8"))
st.update({
    "clock_read": NOW_ISO, "ts": NOW_ISO, "updated": NOW_ISO,
    "heartbeat_epoch_utc": NOW_EPOCH,
    "round_no": 984, "round_no_label": "r983", "last_round": 983, "last_round_at": NOW_ISO,
    "last_round_ts": NOW_EPOCH, "last_ts": NOW_EPOCH, "last_seen": NOW_ISO, "last_seen_at": NOW_ISO,
    "current_task": "r983 wait-state close (W236 yield watch + MF panel watch + bars pre-15:30)",
    "current_task_at": NOW_ISO, "current_task_ts": NOW_EPOCH,
    "did": did, "verdict": verdict, "next": next_ptr, "next_pointer": next_ptr,
    "last_round_summary": summary,
    "latest_artifact": artifact, "last_artifact": artifact, "recent_artifact": artifact,
    "now_active": "2026-10-14 05:2x | r983 | bm-c: wait-state window close | counter 983->984",
    "activity_now": "2026-10-14 05:2x | r983 | bm-c: wait-state window close | counter 983->984",
    "next_milestone": "10-14 bars post-15:30 papers chain + W236 finalize watch (bm-a) + MF panel completion -> MF-IC-P1 unpark",
    "orders_ack_receipt": "r983: zero unacked both scans; group ORD/DEC dual-delta FALSE (hold watermarks per state keys); zero bm-c execution owed",
    "orders_ack_ts": NOW_ISO,
    "orphan_face": 2, "orphan_faces": 2,
    "idle_rounds": 0, "agenda_starved": False,
    "head_sha": "r983 closeout commit rides this window",
    "verify": "receipts: probe results/_orphan_face_probe.bm-c.json + smoke 49/49 + s05 probe dual FALSE x2 + dualrun streak 51 (results/pool_dualrun.bm-c.jsonl) + attrition results/_attrition_guard_scan.json CLEAN + S7 quad (pin=5/watchdog/claws)",
    "r983_closeout_note": "r983: clean continuation window (state round_no=983 at open, executed r983, advanced 983->984 so next=r984); zero absorb owed (r982 closeout landed clean, zero dead window between); zero double-count: S0.5 dual-delta FALSE both scans (opening + S7 tail); wait-state window honestly declared per one-line law",
    "r983_absorb_note": "",
    "note": "r983: wait-state window close (W236 yield + MF-IC-P1 parked + bars not due); counter 983->984",
})
with io.open(st_path, "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
chk2 = json.load(io.open(st_path, encoding="utf-8"))
assert isinstance(chk2["heartbeat_epoch_utc"], int), "epoch must be int"
print("closeout writes OK: round_report + heartbeat + state; round_no -> 984; epoch int-assert PASS")
