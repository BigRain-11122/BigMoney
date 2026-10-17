# r1063 bm-c closeout script (53rd-gen absorb continuation window)
# Dead r1063 window estate: W259 PREREG FREEZE landed+pushed b709bc2cc + D-19 ORD pre-advance
# (2f264fbc->29a77086, judged legitimate by tail spot-check) + S6 43/43 rc0 (08:02:18) +
# splice editor PRE-BUILT (_w259bmc_derive_editor.py, NOT run). THIS window: estate verified
# (banned gate re-run ADMIT rc0, probe receipt re-read ADMIT, blob identity, S6 log read-back)
# + S0 ff-merge behind=2 (bm-a r1028) via 17-face stash-bridge DROP + closeout.
import io, json, os, re, sys, time, ctypes, subprocess
from datetime import datetime, timezone, timedelta

if sys.stdout:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
REPORT = os.path.join(ROOT, "round_reports-bm-c.md")

tz = timezone(timedelta(hours=8))
NOW = datetime.now(tz).strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())

# live RAM reading
class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
mem = MEMORYSTATUSEX()
mem.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
try:
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem))
    FREE_RAM = round(mem.ullAvailPhys / (1024 ** 3), 1)
except Exception:
    FREE_RAM = None
# live GPU free reading
GPU_FREE = None
try:
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                         capture_output=True, text=True, timeout=20)
    GPU_FREE = int(float(out.stdout.strip().splitlines()[0]))
except Exception:
    GPU_FREE = None

absorb_note = (
    "r1063 absorb note: dead window self-labeled r1063 (fired ~07:1x after the r1062 closeout 07:12:19) "
    "executed the FULL W259 prereg derive body + landed it on origin: W258 frozen-face extraction "
    "_w259bmc_w258_frozen_face.txt (07:19:33, byte-verified @ 824b46d31 pre-backfill face per r1052/r1049 law) "
    "+ needle probe (07:21) + derive script _w259bmc_prereg_derive.py (07:38:24) + derive run ALL GATES PASS "
    "(07:38:41) + W259 PREREG FREEZE committed+pushed b709bc2cc 07:39:54 (bands A 585_101..587_100 EIGHTH "
    "consecutive A-hop / B 587_101..587_300 NINTH consecutive above-own-A; 4 disclosed needle-heals + 3 "
    "same-window derive fixes; banned ADMIT rc0; out 45,806B sha256_16 ca4805af49781954 sec7/8 placeholders "
    "intact) + S0.5 probe 07:47:43 (ORD delta 2f264fbc->29a77086) + D-19 advance LANDED 07:49:36 (state "
    "last_orders_sha 29a77086, uncommitted-doc face) + S6 43-leg chain 08:02:18 rc0 (log "
    "results/_r1063bmc_s6_log.txt) + splice editor builder chain 08:03:38-08:07:44 (editor needle preflight "
    "08:03:45 + builder _r1063bmc_build_editor.py -> editor _w259bmc_derive_editor.py BUILT NOT RUN, zero "
    "freeze_edits/receipt = splice intact) -- died pre-closeout (state frozen round_no=1063, heartbeat stale "
    "r1062). This session (per bm-c absorb precedent lineage r894..r1062, 53rd instance) machine-verified the "
    "estate BEFORE closeout: prereg worktree==committed blob (b2a353f38 both faces) + out anchor 45,806B / "
    "sha256_16 ca4805af49781954 == commit message + banned_direction_gate re-run ADMIT rc0 + W259 probe "
    "receipt re-read ADMIT + S6 log 43x rc=0 read-back + ORD pre-advance tail spot-check via bm-a's "
    "r1028 ORD tail extraction (range = 1 row, 07:3x P1 light-dispatch @bm-b drama CDN, bm-b lane zero bm-c "
    "action, bm-a zero-new-dispatch corroborating). Zero double-count: the dead window's advance covered the "
    "only in-range row; fresh probes this window (08:22 + S7 tail) dual-delta FALSE both faces."
)

did = (
    "r1063 (53rd-gen absorb continuation window): (1) S0-1 anchor bm-c + round-zero probe py_faces=7 "
    "orphans=2 zero-kill; (2) S0 ff-merge behind=2 (bm-a r1028 6a9340078+161447118, W259 seat MSG swept "
    "processed by bm-a) via 17-face targeted stash-bridge DROP live-wins disclosed (regenerable status "
    "faces: daily_report/live_usage/compute_audit/token_usage/update_status/regime_state/lhb/futures/"
    "fundamental_b_layer/watermark_red/d19 receipt/2 bm-b evidence files; r1008 legacy stash "
    "identity-protected at stash@{1}; next-window S6 rerun regenerates all; dead-window 08:02 S6 log = this "
    "round's S6 evidence); (3) S0.5: dead-window D-19 ORD pre-advance (2f264fbc->29a77086 landed 07:49:36) "
    "judged LEGITIMATE by tail spot-check -- 1 row in range = 07:3x P1 light-dispatch @bm-b drama CDN row "
    "(bm-b lane, zero bm-c action, bm-a zero-new-dispatch corroborating); fresh probe 08:22 + S7 tail "
    "dual-scan dual-delta FALSE both (ORD 29a77086==current / DEC 881b6dcb hold, unacked=0, zero mid-round "
    "arrivals); (4) S1 smoke 49/49 + satengine ALIVE rc0; (5) ESTATE VERIFIED (see absorb note): W259 "
    "PREREG FREEZE b709bc2cc on origin (worktree==committed blob b2a353f38 + out 45,806B sha256_16 "
    "ca4805af49781954) + banned_direction_gate re-run ADMIT rc0 + W259 probe receipt re-read ADMIT (A "
    "585_101..587_100 EIGHTH A-hop / B 587_101..587_300 NINTH above-own-A, relation asserts all green, "
    "seed_admit FREE x2, origin vacancy four-check) + S6 43/43 rc0 absorbed (dead-window 08:02:18, not "
    "rerun per same-round law) + splice editor PRE-BUILT not run; (6) S2 boards clear (jobs 0 / inbox 0 / "
    "fleet tasks 0 open / idle green_idle=false RAM-gate honest 4.0% not-claim-eligible, claimable_pool=1); "
    "(7) S7: attrition 4 CLEAN + idle --worked rc0 + loop pin=5 no-op + watchdog registered (S4U flip "
    "access-denied = adjudicated default-principal standing face) + claws x2 installed LF-normalized; "
    "counter 1063->1064, W259 five-face splice = r1064 FIRST ACTION @ prereg b709bc2cc out ca4805af49781954 "
    "with editor pre-built"
)

closeout_note = (
    "r1063: 53rd-gen absorb continuation (dead W259 prereg window estate verified, landed b709bc2cc by "
    "predecessor; splice editor pre-built for r1064) + S0 ff-merge behind=2 bm-a r1028 (17-face stash-bridge "
    "drop disclosed) + S0.5 ORD pre-advance judged legitimate (1 row @bm-b lane zero bm-c action) + probes "
    "dual-delta FALSE both + S6 43/43 absorbed (dead-window 08:02:18 rc0) + smoke 49/49 + satengine ALIVE + "
    "banned gate ADMIT re-run + attrition 4 CLEAN + idle worked + quad green | " + NOW
)

verify = (
    "estate: prereg worktree==committed blob b2a353f38 (git rev-parse HEAD:path == hash-object) + out "
    "45,806B sha256_16 ca4805af49781954 == commit message anchor + banned_direction_gate re-run ADMIT rc0 "
    "(no banned direction claimed) + W259 probe receipt re-read ADMIT (bands A 585_101..587_100 / B "
    "587_101..587_300, relation asserts all true, seed_admit FREE x2, origin vacancy, W260+ projection "
    "recorded) + S6 log 43x rc=0 read-back (08:02:18) + splice intact (editor built, zero freeze_edits/"
    "receipt on disk); gates: smoke 49/49 + satengine ALIVE rc0 + s05 probe dual FALSE opening+S7 tail "
    "(ord 29a77086 / dec 881b6dcb) + unacked=0 + attrition 4 CLEAN + idle worked rc0 + epoch int readback "
    "+ report line +1 asserted + orphan face=2 zero-kill"
)

prod_lanes = (
    "CPU=engine W259 prereg frozen (five-face splice = r1064 FIRST ACTION, editor pre-built) ; GPU=llm "
    "fill-gap mode 27b resident (C-03 dual-mode; GPU burns = interactive window lane per O-0131 sec.3; "
    "loop CPU-only)"
)

next_ptr = (
    "r1064: (1) W259 five-face splice (FIRST ACTION per seat-first law; editor PRE-BUILT by dead r1063 "
    "window = results/_w259bmc_derive_editor.py [built by _r1063bmc_build_editor.py from committed W258 "
    "editor canon, E63 lineage; editor needle preflight counts on disk 08:03:45] -- RUN the editor -> "
    "_w259bmc_freeze_edits.py -> run freeze edits -> splice receipt dual-sha16 pf dca9e66660f0c4ac->next / "
    "n1 381d26df7e6d6b7f->next; bands A 585_101..587_100 / B 587_101..587_300; prereg anchor b709bc2cc out "
    "ca4805af49781954; count-asserted authoring gates per canon lineage) -> engine self-burn 12/12 "
    "(mtime-watch) -> sixgate PRE-FINALIZE (21st consecutive target; triple identity n1==receipt==LANDED) "
    "-> finalize one-pass 991,935+2,200=994,135 / K=565,520+2,200=567,720 EXACT -> fivekeys vs W258 keys "
    "(key1 gap 0.002891 / key4 K-lift 0.0000 / key5 se_mu 0.000326 carried) -> sec.7/8 backfill "
    "placeholders=0 -> W260 seat publish (live re-derive on post-W259 universe; naive W260 A "
    "587_101..589_100 expected REFUSED by registered W259 B 587_101..587_300 = NINTH consecutive A-hop face "
    "per probe leg4; W260 freezer MUST re-derive, never transcribe); (2) Monday 10-19 15:30 bars window: "
    "full papers chain fires on the new bar; (3) GPU lane = llm fill-gap 27b resident (GEN state yields "
    "per C-20261016-03 dual-mode law)"
)

milestone = (
    "W259 five-face splice -> self-burn 12/12 -> sixgate 21st consecutive -> finalize 994,135/K=567,720 "
    "EXACT -> W260 seat publish (r1064-r1066, 48h window)"
)

artifact = (
    "research/PERPETUAL_N1_W259_PREREG.md (frozen 45,806B, origin b709bc2cc, sha256_16 ca4805af49781954) "
    "+ results/_r1063bmc_s6_log.txt (43/43 rc0) + results/_w259bmc_derive_editor.py (pre-built splice "
    "editor)"
)

# ---------------- state ----------------
with io.open(STATE, "r", encoding="utf-8") as f:
    st = json.load(f)
assert st.get("round_no") == 1063, "round_no expected 1063, got %r" % st.get("round_no")
st["round_no"] = 1064
for k in ("clock_read", "ts", "updated", "updated_at", "last_seen", "last_seen_at",
          "now_active", "activity_now", "current_task_at", "last_round_at",
          "last_round_closed", "last_seen_at"):
    st[k] = NOW
st["current_task"] = ("r1063 closeout (53rd-gen absorb continuation: W259 prereg estate verified + "
                      "S0 ff-merge behind=2 + S6 43/43 absorbed + quad green)")
st["current_task_ts"] = EPOCH
st["heartbeat_epoch_utc"] = EPOCH
st["last_round"] = "r1063"
st["last_round_label"] = "r1063"
st["round_no_label"] = "r1063"
st["did"] = did
st["note"] = ("r1063: 53rd-gen absorb -- dead window landed W259 prereg b709bc2cc + splice editor "
              "pre-built; splice = r1064 first action")
st["verify"] = verify
st["r1063_absorb_note"] = absorb_note
st["r1063_closeout_note"] = closeout_note
st["prod_lanes"] = prod_lanes
st["next"] = next_ptr
st["next_pointer"] = next_ptr
st["next_milestone"] = milestone
st["latest_artifact"] = artifact
st["last_artifact"] = artifact
st["recent_artifact"] = artifact
st["last_round_summary"] = ("r1063: 53rd-gen absorb (W259 prereg estate verified b709bc2cc + editor "
                            "pre-built + S6 43/43 absorbed + smoke 49/49 + quad green)")
st["last_round_summary_at"] = NOW
st["last_action"] = "r1063 closeout (53rd-gen absorb + S0 ff-merge behind=2 + quad green; counter 1063->1064)"
st["last_action_at"] = NOW
if FREE_RAM is not None:
    st["free_ram_gb"] = FREE_RAM
    st["ram_free_gb"] = FREE_RAM
    st["idle_ram_gb"] = FREE_RAM
if GPU_FREE is not None:
    st["gpu_free_vram_mib"] = GPU_FREE
    st["gpu_free_vram_mb"] = GPU_FREE
    for k in ("gpu_free_mib", "gpu_free_mb", "gpu_idle_vram_mb", "gpu_idle_vram_mib",
              "gpu_idle_mb", "gpu_idle_mib", "gpu_vram_free_mb", "free_vram_mb"):
        if k in st:
            st[k] = GPU_FREE
    gb = round(GPU_FREE / 1024.0, 1)
    if "gpu_free_vram_gb" in st:
        st["gpu_free_vram_gb"] = gb
with io.open(STATE, "w", encoding="utf-8", newline="") as f:
    json.dump(st, f, indent=1, ensure_ascii=False)
    f.write("\n")

# ---------------- heartbeat ----------------
with io.open(HB, "r", encoding="utf-8") as f:
    hb = json.load(f)
for k in ("last_seen", "ts", "now_active", "activity_now", "clock_read", "current_task_at",
          "last_seen_at", "last_round_at", "last_round_closed"):
    hb[k] = NOW
hb["current_task"] = ("r1063 closeout (53rd-gen absorb continuation: W259 prereg estate verified + "
                      "S0 ff-merge + S6 absorbed + quad green)")
hb["current_task_ts"] = EPOCH
hb["heartbeat_epoch_utc"] = EPOCH
hb["round_no"] = 1064
hb["last_round"] = "r1063"
hb["last_round_label"] = "r1063"
hb["did"] = did
verdict = ("green: r1063 = 53rd-gen absorb continuation -- W259 PREREG FREEZE estate verified (landed "
           "b709bc2cc by predecessor: worktree==committed blob + banned ADMIT re-run + probe receipt "
           "ADMIT A 585_101..587_100 / B 587_101..587_300) + splice editor pre-built for r1064 + S0 "
           "ff-merge behind=2 bm-a r1028 (17-face stash-bridge drop disclosed) + dead-window D-19 ORD "
           "pre-advance judged legitimate (1 row @bm-b lane) + probes dual-delta FALSE both + S6 43/43 "
           "rc0 absorbed + smoke 49/49 + attrition CLEAN + orphan face=2 zero-kill")
hb["verdict"] = verdict
hb["verify"] = verify
hb["prod_lanes"] = prod_lanes
hb["next"] = next_ptr
hb["next_pointer"] = next_ptr
hb["next_milestone"] = milestone
hb["latest_artifact"] = artifact
hb["last_artifact"] = artifact
hb["recent_artifact"] = artifact
hb["last_round_summary"] = st["last_round_summary"]
hb["last_round_summary_at"] = NOW
hb["last_action"] = st["last_action"]
hb["last_action_at"] = NOW
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["health"] = "ok"
if FREE_RAM is not None:
    hb["free_ram_gb"] = FREE_RAM
    hb["ram_free_gb"] = FREE_RAM
    hb["idle_ram_gb"] = FREE_RAM
if GPU_FREE is not None:
    hb["gpu_free_vram_mib"] = GPU_FREE
    hb["gpu_free_vram_mb"] = GPU_FREE
    for k in ("gpu_free_mib", "gpu_free_mb", "gpu_idle_vram_mb", "gpu_idle_vram_mib",
              "gpu_idle_mb", "gpu_idle_mib", "gpu_vram_free_mb", "free_vram_mb"):
        if k in hb:
            hb[k] = GPU_FREE
    gb = round(GPU_FREE / 1024.0, 1)
    if "gpu_free_vram_gb" in hb:
        hb["gpu_free_vram_gb"] = gb
with io.open(HB, "w", encoding="utf-8", newline="") as f:
    json.dump(hb, f, indent=1, ensure_ascii=False)
    f.write("\n")

# ---------------- round report ----------------
with io.open(REPORT, "r", encoding="utf-8") as f:
    lines = f.readlines()
n0 = len(lines)
# reuse the verdict glyph from the r1062 row (format-stable, zero literal guess)
glyph = "green"
for l in reversed(lines):
    if "| r1062 | bm-c |" in l:
        m = re.search(r"watermark verdict=(\S+)", l)
        if m:
            glyph = m.group(1)
        break
verdict_line = ("watermark verdict=" + glyph + " (red=false healthy / satengine ALIVE rc0 / engine-queue "
                "never-dry W259 prereg frozen b709bc2cc + splice editor pre-built / jobs 0 / inbox 0)")
row = (NOW + " | r1063 | bm-c | " + verdict_line + " | " + NOW + " | r1063 | " + did +
       " | local-behind-origin N=0 (closeout push rides this window) | next: " + next_ptr + "\n")
lines.append(row)
with io.open(REPORT, "w", encoding="utf-8", newline="") as f:
    f.writelines(lines)

# ---------------- assertions ----------------
with io.open(STATE, "r", encoding="utf-8") as f:
    st2 = json.load(f)
assert st2["round_no"] == 1064, "state round_no readback failed"
assert isinstance(st2["heartbeat_epoch_utc"], int), "state epoch not int"
with io.open(HB, "r", encoding="utf-8") as f:
    hb2 = json.load(f)
assert isinstance(hb2["heartbeat_epoch_utc"], int), "heartbeat epoch not int"
assert hb2["round_no"] == 1064, "heartbeat round_no readback failed"
with io.open(REPORT, "r", encoding="utf-8") as f:
    n1 = len(f.readlines())
assert n1 == n0 + 1, "report line count +1 assertion failed (%d -> %d)" % (n0, n1)
assert "r1063" in lines[-1], "report last row r1063 assertion failed"
print("CLOSEOUT OK %s | state round_no=1064 | hb epoch=%d int | report %d->%d | free_ram=%s gpu_free=%s"
      % (NOW, EPOCH, n0, n1, FREE_RAM, GPU_FREE))
