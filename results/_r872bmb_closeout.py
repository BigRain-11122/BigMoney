"""r872 bm-b closeout: report line append + state.json + heartbeat write +
machine sampling (RAM/VRAM) + post-write self-verify (epoch int, T-sep clock,
round advance). Mirrors r870/r871 closeout field faces."""
import json
import time
import subprocess
import datetime

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW_ISO = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())

# --- sample machine resources -------------------------------------------
free_gb = pct = None
try:
    import ctypes
    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    m = MEMORYSTATUSEX()
    m.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    free_gb = round(m.ullAvailPhys / 1024**3, 1)
    pct = round(100.0 * m.ullAvailPhys / m.ullTotalPhys, 1)
except Exception:
    pass
vram_gb = vram_mb = None
try:
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                        "--format=csv,noheader,nounits"],
                       capture_output=True, text=True, timeout=20)
    vram_mb = int(r.stdout.strip().splitlines()[0])
    vram_gb = round(vram_mb / 1024, 2)
except Exception:
    pass

DID = ("r872 continuation round (predecessor session died 09:16 mid-round, this "
       "fire 09:22 resumed same round number): S0 rebase +2 bm-c r863; orders diff "
       "0 both scans; D19 dual watermark identical (dec caca0c6e/ord f90233c7); "
       "smoke 49/49; PRIMARY PRODUCT = T26 legacy chain closed end-to-end: runner "
       "dec master-reindex transcription drop (.reindex(master_dates) missing, A13 "
       "verbatim restored, r494 family recurrence, selftest 16/16x2, RAW 5-record "
       "checkpoint preserved zero reburn) -> resid resume 15 cells 6s -> finalize "
       "47.1s rc0: FV 2/9 PASS = raw|510050|f_c2 +0.2363 z2.44 CI-excludes-zero + "
       "raw|510500|f_c2 +0.1945 z2.11 = A13 anchor EXACT 4dp replication; supply "
       "notes 512100 dual-face replicated (+0.2643 raw/+0.2857 resid); f_c2v4/f_mp1 "
       "7 negative cells -> attrition (closest f_mp1|510500 +0.1636 z1.43 CI includes "
       "zero); MP1 predictor usage face tested-negative closed; f_c2 pair fixed as "
       "A1/C1 composite input-feature roster supply; prereg sec7/sec8 + arm-table "
       "A14 row + gate_attrition row 113 (guard CLEAN); ledger 877723->877753 (+30 "
       "single-shot); tech.md T26 done; alloc_paper rc=2 root-caused = 510880.csv "
       "second casualty of 10-10 13:16 deletion incident (marks intact, zero new "
       "bars since) -> T-2026-10-11-184-P1 transfer ticket filed (bm-a->bm-b Plan A) "
       "+ inbox MSG; S6 41 legs 40 rc0 + alloc rc2 known-face; S7 claws+watchdog "
       "verified, idle --worked (idle_rounds=0)")

NEXT = ("r873 queue: supply-floor response chain (P2/P3 queue-head collision probe "
        "CLEAR face + queue_seed_gate -> next prereg draft window, floor 0 -> >=3 "
        "ready, O-20261011-0012 CPU-max) -> T-184 transfer receiver leg watch (after "
        "bm-a pushes transfer branch: git checkout origin/transfer/t184-510880 -- "
        "data/daily/510880.csv + git restore --staged R90 pit law + manifest Verify) "
        "-> W210 freeze PARKED on M9 chain watch (bm-a face, no W209 signal) -> "
        "moneyflow IC panel watch -> O-20261011-0012 maintained")

ARTIFACT = ("r872: results/t101_v4_a14_predface.json (FV 2/9, 30 cells, cutoff "
            "2026-10-09, ledger 877753) + research/T-101-V4_A14_PREDFACE_PREREG.md "
            "sec7/sec8 backfill + research/DECISION_CHAIN_BENCHMARKS.md A14 row + "
            "results/gate_attrition.bm-b.json row 113 + runner heal "
            "scripts/t101_v4_a14_predface.py (dec reindex, commit-face) + "
            "fleet/tasks/T-2026-10-11-184-P1.json + MSG-20261011-0940")

VERDICT = ("GREEN: r872 continuation (A14 judgment landed FV 2/9 replication-held; "
           "T26 chain closed; MP1 predictor face tested-negative; supply floor "
           "0<3 breach = next-round prereg response; alloc_paper rc2 = 510880 "
           "transfer ticket filed; smoke 49/49; orders/d19 zero-delta)")

NOW_ACTIVE = ("r872 closeout: A14 verdict face landed (f_c2 replication 2/2 held, "
              "extension faces negative); T26 consumed; supply floor response queued "
              "next round")

MILESTONE = ("supply-floor chain: next prereg draft window -> pool ready 0 -> >=3 "
             "by <=2026-10-13; T-184 510880 restore before 2026-10-12 15:30 next bar")

# --- 1) round report line append ----------------------------------------
line = open(ROOT + r"\results\_r872bmb_report_line.txt", encoding="utf-8").read().strip()
rp = ROOT + r"\logs\iteration-loop\round_reports.md"
with open(rp, "a", encoding="utf-8") as fh:
    fh.write(line + "\n")
print("report line appended:", len(line), "bytes")

# --- 2) state.json --------------------------------------------------------
sp = ROOT + r"\state.json"
st = json.load(open(sp, encoding="utf-8"))
st.update({
    "clock_read": NOW_ISO, "ts": NOW_ISO, "updated": NOW_ISO, "updated_at": NOW_ISO,
    "last_seen": NOW_ISO, "last_round_at": NOW_ISO, "last_round_ts": NOW_ISO,
    "last_action_at": NOW_ISO,
    "current_task": NEXT, "task": NEXT, "next": NEXT,
    "did": DID, "last_action": DID,
    "latest_artifact": ARTIFACT, "now_active": NOW_ACTIVE,
    "next_milestone": MILESTONE,
    "round": 872, "round_no": 873, "round_no_label": "r872",
    "verdict": VERDICT,
    "orphan_face": 0, "orphan_faces": 0,
    "orphan_face_note": "r872 round probe: py_faces=11 alive, orphans=0",
    "last_decisions_read_at": NOW_ISO, "last_orders_read_at": NOW_ISO,
})
with open(sp, "w", encoding="utf-8") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)
print("state.json: round=872 round_no=873")

# --- 3) heartbeat ---------------------------------------------------------
hp = ROOT + r"\fleet\machines\bm-b.json"
hb = json.load(open(hp, encoding="utf-8"))
hb.update({
    "machine_id": "bm-b",
    "clock_read": NOW_ISO, "ts": NOW_ISO, "last_seen": NOW_ISO,
    "heartbeat_epoch_utc": EPOCH,
    "round": 872, "round_no": 873,
    "current_task": NEXT, "task": NEXT, "next": NEXT,
    "did": DID, "last_action": DID,
    "last_action_at": NOW_ISO, "last_round_at": NOW_ISO,
    "latest_artifact": ARTIFACT, "now_active": NOW_ACTIVE,
    "next_milestone": MILESTONE, "verdict": VERDICT,
    "idle_rounds": 0, "agenda_starved": False,
    "orphan_face": 0, "orphan_faces": 0,
    "orphan_face_note": "r872 round probe: py_faces=11 alive, orphans=0",
    "cpu_cores": 16,
    "free_ram_gb": free_gb, "ram_free_gb": free_gb, "ram_free_pct": pct,
    "gpu_free_vram_gb": vram_gb, "vram_free_gb": vram_gb,
    "gpu_free_vram_mb": vram_mb,
    "updated": NOW_ISO, "updated_at": NOW_ISO,
})
with open(hp, "w", encoding="utf-8") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)

# --- 4) self-verify ------------------------------------------------------
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "clock T-sep"
assert chk["round_no"] == 873, "round advance"
tail = open(rp, encoding="utf-8").read().strip().splitlines()[-1]
assert tail.startswith("2026-10-11") and "[r872 bm-b]" in tail, "report tail"
print(json.dumps({"self_verify": "PASS", "epoch": chk["heartbeat_epoch_utc"],
                  "clock_read": chk["clock_read"], "round_no": chk["round_no"],
                  "ram_free_gb": free_gb, "vram_free_gb": vram_gb,
                  "report_tail_tag": "[r872 bm-b]"}, ensure_ascii=False))
