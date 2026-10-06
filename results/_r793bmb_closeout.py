# r793 bm-b S7 close-out: state.json + heartbeat + round report line (atomic single pass)
import json, time, subprocess, ctypes, os
from datetime import datetime, timedelta, timezone

TZ = timezone(timedelta(hours=8))
now = datetime.now(TZ)
now_iso = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

# system stats: free RAM via GlobalMemoryStatusEx, GPU via nvidia-smi (CREATE_NO_WINDOW)
class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
ms = MEMORYSTATUSEX(); ms.dwLength = ctypes.sizeof(ms)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms))
free_ram_gb = round(ms.ullAvailPhys / 1024**3, 2)
gpu_free_vram_gb = None
try:
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                       capture_output=True, creationflags=0x08000000, timeout=20)
    gpu_free_vram_gb = round(int(r.stdout.decode().strip().splitlines()[0]) / 1024, 3)
except Exception:
    gpu_free_vram_gb = None

# ---------- state.json ----------
sp = "state.json"
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 793
st["round_no_label"] = "r793"
st["note"] = ("r793: S0 landing round: r792's own un-pushed round commit (ad5d482ba, replayed as 9b19eb9ad) + autofill self-commit + r793 churn-absorb "
              "all rebased onto advanced origin tip e73305d0c via 2-cycle conflict surgery (13-face pick-2 batch: 6 doc twins same-side stage3 by deep-ts probe 02:18>02:15, "
              "2 rolling-ledger union compute_audit/regime_state, 5 snapshot take-new; 6-face pick-4 daemon batch: 3 jsonl line-union + 3 live-wins; "
              "receipts results/_r793bmb_rebase_resolve.json + _r793bmb_rebase_resolve2.json). r787 atomic-law confirmation: partial-path add still blocked by "
              "unstaged daemon ticks -> add -u + continue in one shell = convergent. D-19 consumed: decisions sha 635C3024->ACC32216 (rows D-20261007-01/02/03; "
              "BigMoney face CODELY 27,664B<=30,720B compliant, zero action; D-02/03 HQ/CPH4 faces zero action). QA pack r793 5/5 detached --round 793 explicit. "
              "S6 chain 35/35 rc0 golden-week no-op. Trio probe fresh: Q 1888/2000 rate 0.384/min ETA ~07:43 / D 1563/2000 rate 0.314/min ETA ~10-08 01:00 / V 2000 COMPLETE.")
st["last_round_at"] = now_iso
st["ts"] = now_iso
st["updated"] = now_iso
st["last_seen"] = now_iso
st["clock_read"] = now_iso
st["last_round_ts"] = now_iso
st["last_decisions_sha"] = "ACC322169EAA759A6EA34C65BE35AA7EED7EA9B96DC0895DC7F4F682BECDF2FD"
st["last_decisions_at"] = now_iso
st["last_decisions_read_at"] = now_iso
st["last_orders_sha"] = "858D46C3587FDA1726A3BBD5275E70E7D6AF48391FBCAFE04D78BC6A37BD4EA1"
st["last_orders_read_at"] = now_iso
st["last_orders_sha_note"] = ("r793: orders 163/163 zero-delta (fleet dir vs ack set-diff both empty, machine-checked); group orders.md sha 858D46C3 "
                              "(105,767B @origin); decisions sha CHANGED 635C3024->ACC32216 = consumed D-20261007-01/02/03 (BigMoney face = CODELY cap already "
                              "compliant 27,664B, HQ 31,320B read face was stale vs r789 early-close receipt); zero new BigMoney dispatch")
st["last_decisions_sha_method"] = "SHA-256 hex upper of git show origin/main:docs/decisions.md raw bytes via group tree C:\\Users\\Administrator\\FluxGroup fetch+show (D-20261004-02③ real-path fallback)"
st["did"] = ("r793: S0 landing surgery (r792 commit 9b19eb9ad + 2 daemon commits onto advanced origin; 19 conflict faces resolved per canon, 2 receipts) + "
             "D-19 decisions consumption (ACC32216: D-20261007-01/02/03, BigMoney face zero-action compliant) + orders 163/163 + smoke 48/48 + "
             "QA r793 5/5 detached + S6 35/35 rc0 + trio readiness probe (Q 1888/D 1563/V 2000) + S7 quartet 4/4 + attrition 4 ledgers CLEAN")
st["verdict"] = ("green: S0 landing closed (r792 round commit on origin tip pending push); trio Q/D burns alive (1888/1563 of 2000, V complete); "
                 "orders 163/163; smoke 48/48; QA r793 5/5; satengine alive rc0 idle; boards 0 open; CODELY 27,664B<=cap compliant")
st["current_task"] = ("r793 closed; next = trio Q finalize ~10-07 07:43 (first-to-2000 same-window per r668, G4 r638 fallback armed) / D finalize ~10-08 01:00 + "
                      "market reopen 10-08 (S6 legs 25-28 + REGIME_GUARD v3 first new bar enforce)")
st["next"] = ("(1) trio Q finalize ~10-07 07:43 (Q 1888/2000 rate 0.384/min; first-to-2000 same-window per r668 law; window 10-05..10-09; G1 pending Q+D; "
              "G2 integrity + G3 rehearsal green; G4 PENDING r638 fallback armed); (2) D finalize ~10-08 01:00 (D 1563/2000 rate 0.314/min); "
              "(3) market reopen 10-08: S6 legs 25-28 resume + REGIME_GUARD v3 first new bar enforce; "
              "(4) O-20261006-2358 trio self-claim law: post-trio-close <=1h claim one backlog item")
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---------- heartbeat ----------
hp = os.path.join("fleet", "machines", "bm-b.json")
hb = json.load(open(hp, encoding="utf-8"))
hb["last_seen"] = now_iso
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = now_iso
hb["free_ram_gb"] = free_ram_gb
hb["gpu_free_vram_gb"] = gpu_free_vram_gb
hb["gpu_free_vram_mb"] = int(gpu_free_vram_gb * 1024) if gpu_free_vram_gb else None
hb["verdict"] = st["verdict"]
hb["current_task"] = st["current_task"]
hb["last_round_at"] = now_iso
hb["round_no"] = 793
hb["round"] = 793
hb["last_action"] = ("r793: S0 landing surgery (r792 commit + 19-face 2-cycle conflict resolution onto advanced origin, receipts x2) + D-19 consumption "
                     "(decisions ACC32216 rows D-20261007-01/02/03; BigMoney face CODELY cap compliant zero-action) + QA 5/5 + S6 35/35 rc0")
hb["now_active"] = ("FUND trio NULLS judgment batch in-flight: Q 1888/2000 (rate 0.384/min, ETA ~07:43) / D 1563/2000 (rate 0.314/min, ETA ~10-08 01:00) / "
                    "V 2000/2000 COMPLETE @02:51 probe; G1 pending Q+D, G2+G3 green, G4 r638 fallback armed; finalize window 10-05..10-09")
hb["latest_artifact"] = ("results/_r793bmb_rebase_resolve.json + _r793bmb_rebase_resolve2.json (19-face S0 surgery receipts: 6 doc twins same-side, "
                         "2 rolling-ledger union, 5+3 snapshot/live-wins, 3 jsonl line-union) + qa/smoke-r793.md 5/5 (93 trades determinism=True, "
                         "equity-curve-r793.png 64,616B) @2026-10-07T02:5x")
hb["next_milestone"] = ("trio Q finalize ~10-07 07:43 first-to-2000 same-window (r668 law, G4 r638 fallback armed) / D ~10-08 01:00 + market reopen 10-08 "
                        "(S6 legs 25-28 + REGIME_GUARD v3 first new bar enforce) — within 48h window")
hb["task"] = "r793 closed; see state.next"
hb["ts"] = now_iso
hb["updated"] = now_iso
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# epoch int + clock T-sep self-verify (R170/R178/R262 laws)
hb2 = json.load(open(hp, encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in hb2["clock_read"] and " " not in hb2["clock_read"], "clock_read must be T-separated ISO"

# ---------- round report line ----------
RR = os.path.join("logs", "iteration-loop", "round_reports.md")
line = (
    "2026-10-07T%02d:%02d+08:00 | round 793 (bm-b, dept:engineering, S0 landing surgery r792-tail + D-19 new-row consumption round) | "
    "[watermark verdict: GREEN (red=false lane healthy; satengine alive rc0 idle queue_depth=0; boards 0 open both boards; "
    "trio Q/D in-flight burning = trial-labor line satisfied; next_pick absent = bandit advisory face none)] | "
    "CEO three-line: current-work = FUND trio NULLS judgment batch in-flight (Q 1888/2000 rate 0.384/min ETA ~07:43 / D 1563/2000 rate 0.314/min ETA ~10-08 01:00 / "
    "V 2000/2000 COMPLETE @02:51 probe; burns alive; G1 pending Q+D, G2 integrity + G3 rehearsal green, G4 PENDING r638 fallback armed; window 10-05..10-09) | "
    "latest-artifact = results/_r793bmb_rebase_resolve.json + _r793bmb_rebase_resolve2.json (S0 landing surgery: r792 un-pushed round commit 9b19eb9ad + autofill "
    "self-commit + r793 churn-absorb all rebased onto advanced origin tip e73305d0c; 19 conflict faces resolved per conflict-resolve canon = pick-2 13-face batch "
    "[6 doc snapshot twins same-side stage3-mine 02:18>02:15 deep-ts probe / 2 rolling-ledger union compute_audit+regime_state zero-loss / 5 snapshot take-new] + "
    "pick-4 6-face daemon batch [3 jsonl line-union / 3 live-wins; p1d_gates took stage2 by ts probe]) + qa/smoke-r793.md 5/5 (93 trades determinism=True, "
    "equity-curve-r793.png 64,616B, detached --round 793 explicit per r758 law) | "
    "next-milestone = trio Q finalize ~10-07 07:43 (first-to-2000 same-window per r668 law, G4 r638 fallback armed) / D finalize ~10-08 01:00 + market reopen 10-08 "
    "(S6 legs 25-28 resume + REGIME_GUARD v3 first new bar enforce) + post-trio-close <=1h backlog self-claim per O-20261006-2358 | "
    "S0: identity=bm-b anchored (machine.json first-read); churn-absorb 7 live faces committed first per r620 law; pull --rebase 4-local-commit replay onto advanced "
    "origin; r787 atomic-law live confirmation: partial-path add (13 conflicted only) still blocked by unstaged daemon ticks -> git add -u + continue in one shell = "
    "convergent (add must cover ALL dirty tracked faces, not conflict set only) | "
    "S0.5: orders 163/163 zero-delta machine-checked (fleet dir 163 vs ack set 163, set-diff both empty, round-start scan; S7 rescan deferred to next landing since "
    "no in-round order ingestion); D-19 decisions sha 635C3024->ACC32216 CHANGED = consumed 10-07 00:00 batch D-20261007-01/02/03: BigMoney face = CODELY.md 27,664B "
    "<=30,720B cap compliant (D-20261002-06 gate closed early by r789 receipt; HQ 31,320B read face stale vs our landed trim, honest zero-action note) + "
    "D-20261007-02 (evolution-ledger 400KB = HQ tooling face) + D-20261007-03 (patrol-stamp chronic = CPH4 face) both non-BigMoney zero action; "
    "group orders.md sha 858D46C3 CEO-pending zone scanned = zero new BigMoney rows | "
    "S1: smoke 48/48 | S2: job_list 0 + fleet tasks 176 files 0 open (46 claimed lanes respected); dev queue adjudicated closed per r297/r307 "
    "(J12 anti-dup no-touch / J13 bm-a lane / J10+J18b delivered / town 11-floor landed / Optuna gated frozen 6<8) | "
    "S3: S0 landing surgery = round engineering closure; trio = waiting state single-declaration per waiting-round law (fresh probe @02:51 in S6 leg 39: Q 1888/D 1563/V 2000, "
    "rates measured, aliveness inherited from r792 process-level verify + fresh line growth); post_review zero active FAIL rows; satengine status alive idle rc0 | "
    "S6: chain 35/35 rc0 (golden-week no-op face, legs 25-28 built-in skip; dualrun reconcile ran before compute_audit per T-116 s3 ordering law) | "
    "S7: quartet 4/4 (IterationLoop next-run 03:02 pin :02 OK / LoopWatchdog 02:55 OK / pre-commit claw OK / pre-push claw OK, CR-normalized compare); "
    "attrition guard 4 ledgers CLEAN (results/_attrition_guard_scan.json; pre-790 healed row noted); state round_no 792->793; heartbeat epoch=%d int-verified; "
    "watermarks decisions=ACC32216 orders=858D46C3; push+fetch+ls-tree delivery self-verify below\n" % (now.hour, now.minute, epoch)
)
with open(RR, "a", encoding="utf-8") as f:
    f.write(line)
print("CLOSE-OUT WRITES DONE")
print("now=%s epoch=%d free_ram=%s gpu_vram=%s" % (now_iso, epoch, free_ram_gb, gpu_free_vram_gb))
