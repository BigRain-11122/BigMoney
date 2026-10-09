# r944 bm-a closeout: round report line + state-bm-a.json + heartbeat (fresh read-modify-write per 10-06 law)
import json, time, datetime, psutil, subprocess

NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())
R = "944"

REPORT_LINE = (
    NOW + " | r" + R + " | bm-a | dept:工程 (watch-window round: S0 clean sync 0/0 + S6 39 legs rc0 + quartet green) | "
    "S0: origin==HEAD 0/0 zero-rebase (Saturday; dirty-at-start = 7 own daemon live-wins faces, absorbed this closeout) | "
    "S0.5: orders diff ZERO (60 files vs 199 acked) + DEC b87a92b1 python-raw MATCH via C: real-path -- zero re-consume "
    "zero action | S1 smoke 49/49 | S2 board 48 claimed / 0 open; idle trigger NOT GREEN-IDLE (VRAM 0.61GB, jman LoRA "
    "MV-lane O-20261009-2330 occupies as known) -- no backlog claim obligation | "
    "S3/S6: chain 39 legs ALL rc0 (_r944bma_s6_chain.json; no new bar Saturday, panel tail 2026-10-09 pre==post; "
    "scorecard/market_clock/thermo/ths/ah/fund legs host=bm-a executed, bm-b/bm-c lane legs honest no-op); "
    "dualrun_reconcile ZERO-DRIFT streak 1 (419 entries, cutoff 03:52:53); attrition guard CLEAN (4 files, 5 historical "
    "shrinks healed); WM probe red=false 06:10:04 lane healthy | SatEngine ALIVE rc0 idle queue0; orphan face=1 "
    "(probe read-only, no kill) | lane survey: W17 screen = bm-c lane-pinned owner_since 05:37 (shards 0-4 keepalive; "
    "5/6/7 open-but-lane-pinned NOT cross-machine claimable) zero claim correct; PARKING-P1 burn due 10-14 12:00 "
    "in-cadence (SEED_REGISTRY parking_p1_null_base=94_300, r915 adjudicated exception 4 pre-burn catch in canon, "
    "burn NOT yet run -- watch holds); W204 seat=bm-c locked (MSG-20261010-0022-bmc) owner to arm | "
    "S7: loop-pin8 no-op (first fire 06:08:00) + watchdog present (06:10) + pre-commit/pre-push claws both match True; "
    "inbox zero unread | "
    "next: r945 = 5x HANDOVER refresh (product list + completion status) + watch window continues (PARKING-P1 / W17 "
    "funnel bm-c / W204 arm bm-c)"
)

# 1) round report append (fresh read, verify last line is r943)
with open("round_reports-bm-a.md", "rb") as f:
    rep = f.read().decode("utf-8")
lines = rep.rstrip("\n").split("\n")
assert "r943" in lines[-1], "report tail is not r943: " + lines[-1][:80]
rep_out = rep.rstrip("\n") + "\n" + REPORT_LINE + "\n"
with open("round_reports-bm-a.md", "wb") as f:
    f.write(rep_out.encode("utf-8"))
print("[closeout] report line r944 appended, tail ok")

# fresh system readings (single-source law: one nvidia-smi read for all gpu* fields r799)
CPU = round(psutil.cpu_percent(interval=1), 1)
RAM_FREE = round(psutil.virtual_memory().available / 1e9, 1)
_v = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                    capture_output=True, text=True)
VRAM_MIB = int(_v.stdout.strip().splitlines()[0])
VRAM_GB = round(VRAM_MIB / 1024, 2)

did = ("r944: watch-window round green (S0 0/0 clean sync + orders/decisions quartet MATCH zero action + smoke 49/49 + "
       "S6 39 legs rc0 no-new-bar Saturday + dualrun ZERO-DRIFT streak 1 + attrition CLEAN + WM green 06:10:04 + "
       "W17/PARKING-P1/W204 lane survey all in-cadence)")
art = ("results/_r944bma_s6_chain.json (39 legs rc0, no new bar, panel 2026-10-09) + results/_r944bma_s6_driver.py "
       "(bloodline roll r943->r944) + results/watermark_red.json red=false 06:10:04")
nxt = ("r945: 5x HANDOVER refresh (research/HANDOVER.md product list + completion status) + watch window continues "
       "(PARKING-P1 burn due 10-14 12:00; W17 screen funnel bm-c lane; W204 arm by bm-c seat owner)")
verd = ("green (r944: watch window; S6 39/39 rc0; smoke 49/49; dualrun ZERO-DRIFT streak 1; attrition CLEAN; quartet "
        "MATCH; W17/PARKING-P1/W204 in-cadence; engine ALIVE idle)")

# 2) state file update (fresh read)
with open("state-bm-a.json", "rb") as f:
    st = json.loads(f.read().decode("utf-8"))
st["round_no"] = 944
st["round"] = 944
st["loop_round"] = 944
st["round_no_label"] = "r944"
st["last_round"] = 943
st["ts"] = NOW
st["clock_read"] = NOW
st["updated"] = NOW
st["updated_at"] = NOW
st["last_seen"] = NOW
st["last_run"] = NOW
st["last_round_at"] = NOW
st["last_round_ts"] = NOW
st["last_round_closed"] = NOW
st["last_heartbeat_epoch_utc"] = EPOCH
st["heartbeat_epoch_utc"] = EPOCH
st["did"] = did
st["last_action"] = "r944 closeout: watch window green + S6 39 legs + daemon churn absorb"
st["last_artifact"] = art
st["latest_artifact"] = art
st["next"] = nxt
st["now_active"] = nxt
st["current"] = nxt
st["task"] = nxt
st["current_task"] = nxt
st["next_milestone"] = "PARKING-P1 burn due 10-14 12:00; W204 arm pending bm-c; HANDOVER 5x r945"
st["verdict"] = verd
st["verify"] = verd
st["last_orders_seen"] = "r944 scan zero unacked (60 files vs 199 ack, ORD 0ddb01d9 unchanged)"
st["last_orders_at"] = "2026-10-10"
st["last_orders_ts"] = NOW
st["last_decisions_seen"] = "D-20261010-01/02/03 hash b87a92b1 MATCH r944 scan; zero new BigMoney dispatch"
st["last_decisions_at"] = "2026-10-10"
st["last_decisions_ts"] = NOW
st["push_verified"] = {"ts": NOW, "origin_tip": "pending", "ahead_behind": "pending",
                       "note": "r944 watch-window closeout; push verification post-commit"}
st["sync"] = dict(st["push_verified"])
with open("state-bm-a.json", "wb") as f:
    f.write((json.dumps(st, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
st2 = json.loads(open("state-bm-a.json", "rb").read().decode("utf-8"))
assert isinstance(st2["heartbeat_epoch_utc"], int) and isinstance(st2["last_heartbeat_epoch_utc"], int)
print("[closeout] state-bm-a.json updated, epoch int verified", EPOCH)

# 3) heartbeat (fresh read)
with open("fleet/machines/bm-a.json", "rb") as f:
    hb = json.loads(f.read().decode("utf-8"))
hb["round_no"] = 944
hb["round"] = 944
hb["loop_round"] = 944
hb["last_round"] = 943
hb["ts"] = NOW
hb["clock_read"] = NOW
hb["last_seen"] = NOW
hb["last_run"] = NOW
hb["heartbeat_epoch_utc"] = EPOCH
hb["last_heartbeat_epoch_utc"] = EPOCH
hb["heartbeat_epoch_utc_type_int"] = True
# single-source system faces (r799 law: all cpu*/gpu* fields from one read each)
hb["cores"] = 32
hb["cpu_cores"] = 32
for k in ("cpu_load_pct", "cpu_pct", "cpu_total_pct", "cpu_util_pct"):
    hb[k] = CPU
hb["free_ram_gb"] = RAM_FREE
hb["ram_free_gb"] = RAM_FREE
for k in ("gpu0_free_vram_gb",):
    hb[k] = VRAM_GB
for k in ("gpu_free_vram", "gpu_idle_vram"):
    hb[k] = VRAM_GB
for k in ("gpu_free_vram_gb", "gpu_idle_vram_gb"):
    hb[k] = VRAM_GB
for k in ("gpu_free_vram_mb", "gpu_free_vram_mib", "gpu_idle_vram_mb", "gpu_idle_vram_mib"):
    hb[k] = VRAM_MIB
hb["did"] = did
hb["last_action"] = "r944 closeout: watch window green + S6 39 legs + daemon churn absorb"
hb["last_artifact"] = art
hb["latest_artifact"] = art
hb["next"] = nxt
hb["now_active"] = nxt
hb["current"] = nxt
hb["current_task"] = nxt
hb["task"] = nxt
hb["next_milestone"] = "PARKING-P1 burn due 10-14 12:00; W204 arm pending bm-c; HANDOVER 5x r945"
hb["verdict"] = verd
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["last_orders_seen"] = "r944 scan zero unacked (ORD 0ddb01d9 unchanged)"
hb["last_orders_at"] = "2026-10-10"
hb["last_orders_sha"] = "0ddb01d9aca7588382fb4341651f6d7548503070d4a12cf98c2774346d48276e"
hb["last_decisions_seen"] = "D-20261010-01/02/03 hash b87a92b1 MATCH r944 scan"
hb["last_decisions_at"] = "2026-10-10"
hb["last_decisions_sha"] = "b87a92b1b445fd1dab4daa9250c9d52eb85e0ac122c7b870ce5f83e822c67374"
with open("fleet/machines/bm-a.json", "wb") as f:
    f.write((json.dumps(hb, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
hb2 = json.loads(open("fleet/machines/bm-a.json", "rb").read().decode("utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int)
print("[closeout] heartbeat updated, epoch int verified, cpu=%s ram=%s vram=%sMiB" % (CPU, RAM_FREE, VRAM_MIB))
print("CLOSEOUT WRITES DONE")
