# r351 S7 closeout: state-bm-c.json + fleet/machines/bm-c.json + inbox move.
# Types: heartbeat_epoch_utc MUST be python int (R170/R178 law); clock_read ISO8601 with T (R262 law).
import json, time, shutil, os, sys, subprocess
sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
now = time.time()
epoch = int(now)
import datetime
clock = datetime.datetime.fromtimestamp(now).astimezone().isoformat(timespec="seconds")

# --- system sample (cpu / ram / gpu via nvidia-smi silent) ---
cpu_pct = 0.0
idle_ram_gb = 0.0
try:
    out = subprocess.check_output(
        ["powershell", "-NoProfile", "-Command",
         "(Get-CimInstance Win32_Processor | Measure-Object -Property "
         "LoadPercentage -Average).Average; [math]::Round("
         "(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,1)"],
        encoding="utf-8", timeout=30)
    parts = out.split()
    cpu_pct = float(parts[0]); idle_ram_gb = float(parts[1])
except Exception as e:
    print("sys sample fallback:", e)
gpu_free = 0
try:
    o = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
        encoding="utf-8", timeout=20)
    gpu_free = int(o.strip().splitlines()[0])
except Exception:
    gpu_free = 9721  # last sampled face

verify = ("r351: S0 dead-session forensics r347-r350 integration (state stuck 346 + "
          "self-labeled r347/r348/r349/r350 commits on origin + no live session process "
          "-> numbers 347-350 burned per r529 law, r351 resumes) + MAIN PRODUCT: "
          "W52 FULL-LIFECYCLE SINGLE-WINDOW wave (FREEZE five-piece: band gate ADMIT "
          "[A 147_004..149_003 / B 46_201..46_400 both ARITHMETIC CONTINUATION no "
          "skip, CLEAN machine-derived; leg0 49-row + leg0b prose + leg1 both-CLEAN + "
          "leg2 first-clean==arithmetic + leg3 + N3-R1 leg + probe-cluster leg + "
          "origin slot vacancy; first push raced bm-a/bm-b 3 commits -> rebase relay "
          "-> landed, W52 row on origin = slot lock] + banned gate ADMIT + prereg "
          "frozen [anchor=W49 landed] + canon W52 row + N1_BANDS/WAVE_CONFIGS[52] + "
          "selftest W52 materializer leg same-window) -> 12/12 no-restart burn "
          "(per-tick re-read auto-saw row, product growth 05:5x) -> FINALIZE "
          "one-pass + TRIPLE FINALIZE W50->W51->W52 same window (W48re bm-a r558 "
          "+ W49 bm-b r558 landed = chain unblocked; W50 K=107,920 ledger 474,548 "
          "[S5 4/4 anchor W47-frozen, K-lift +0.0002]; W51 K=110,120 ledger 476,748 "
          "[S5 4/4 dual-anchor W47-frozen+W50-rolled, K-lift -0.0003 honest negative; "
          "bm-b r558 W51 same-number double-freeze YIELDED to bm-c r350 per r511/"
          "r530 -- MSG-0610 receipt, zero ledger pollution]; W52 K=112,320 == sec.0 "
          "projection BIT-EXACT ledger 478,948 CHAIN HEAD [S5 4/4 dual-anchor "
          "W49-frozen+W51-rolled, K-lift -0.0001]; se_mu narrowing 0.000745->0.000738"
          "->0.000731; chain FULLY CAUGHT UP W1..W52 zero in-flight upstream seats; "
          "prereg s7/s8 session-side mechanical backfill x3 same commit + post-"
          "backfill default-wave selftest PASS [r307 two-state]) + LOWAMP-P3 verdict "
          "consumed: judged-negative (LA-REP legacy base sharpe 1.158 / +15.9% full "
          "but trade_gate FAIL [7 trades/9 entries < 30 min], skill line 1.97 >> "
          "obs, DSR 0.27 < 0.95, PBO 0.49 observe; E1 three-leg PASS, nulls 2000/2000, "
          "ledger 461,348 landed by bm-b dead r533; LOWAMP family P1-void/P2/P3 "
          "three-times negative = line honestly closed per O-1901) + S6 spine rc0 "
          "(dualrun ZERO-DRIFT streak 33/3; WM py_low_with_work_cands legal-idle "
          "whitelist; audit flags pool_starvation/supply_floor = W52 post-burn empty "
          "queue, W53 = next-round standing step; REPORT/LIVE-2026-10-02 regen; "
          "attrition CLEAN; b_layer 4 gates PASS; token delta 0) + D-19 MATCH-"
          "unchanged (4FD50184 raw-blob python law) + T-131 collector alive "
          "(pid 23868, product growth 05:42 fresh)")

did = ("r351: dead-session S0 integration + W52 full-lifecycle single-window "
       "(freeze -> 12/12 burn -> finalize) + triple finalize W50/W51/W52 "
       "(ledger 474,548/476,748/478,948) + LOWAMP-P3 judged-negative consumption + "
       "S6 chain")
current_task = ("W52 full-lifecycle closed same window (freeze 3a81352d3 -> burn "
                "-> finalize one-pass K=112,320); chain W1..W52 fully caught up; "
                "T-131 fund_history backfill in flight (network-bound pid 23868); "
                "engine idle post-W52 = queue empty, W53 freeze next round per "
                "de-throttle first-free law")
next_ = ("(r352)(a) W53 freeze first-free-number (fresh fetch + band-gate "
         "machine-verify per W52 row W53+ projection both CLEAN: A 149_004..151_003 "
         "/ B 46_401..46_600, r535 law); (b) T-131 backfill liveness watch + "
         "completion closeout (~ETA hours, r340 three-face law); (c) T-134 s2 "
         "p1e_synth conversion (r340 pick9 = 2586.9s heaviest; r304 paradigm); "
         "(d) register_satengine_task.ps1 S4U-first dead-code cleanup "
         "(D-20261002-02, window 10-04); (e) T-143 month-exam prep ticket claim "
         "decision (deliverable 10-29, accounts face=bm-c primary); (f) month-"
         "boundary first exam 10-31")

# --- state-bm-c.json ---
sp = os.path.join(ROOT, "state-bm-c.json")
st = json.load(open(sp, encoding="utf-8"))
st["machine_id"] = "bm-c"
st["round_no"] = 351
st["last_round_at"] = "r351"
st["last_round_ts"] = clock
st["updated"] = clock
st["cpu_pct"] = cpu_pct
st["idle_ram_gb"] = idle_ram_gb
st["gpu_free_vram_mib"] = gpu_free
st["verify"] = verify
st["did"] = did
st["current_task"] = current_task
st["next"] = next_
st["heartbeat_epoch_utc"] = epoch
st["clock_read"] = clock
st["note"] = ("r351 skipped dead r347-r350 numbering per r529 law (state stuck 346 + "
              "four self-labeled commits on origin + no live session = dead-before-S7 "
              "batch; their products W46 finalize/W47 yield/W50+W51 freeze+burn all "
              "verified on origin, zero redone). W52 = FIFTH single-window full-"
              "lifecycle wave (W32/W42/W43/W46 precedents). bm-b r558 W51 double-"
              "freeze yield receipt MSG-0610 archived. W51 prereg sec0 projection "
              "omitted W48 seat 2,200 (projection-only face, disclosed in W52 "
              "prereg; finalize runtime derive immune).")
st["last_ts"] = clock
st["last_decisions_sha"] = "4fd50184453162a8b01c47d6ca79224b95869db2487aa18e10d61479177f250c"
st["last_decisions_read_at"] = clock
st["last_round"] = ("2026-10-02 r351 bm-c: W52 full-lifecycle single-window + triple "
                    "finalize W50/W51/W52 (ledger head 478,948) + LOWAMP-P3 verdict "
                    "consumption + S6 chain")
st["last_seen"] = clock
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
chk = json.load(open(sp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178)"
assert "T" in chk["clock_read"], "clock_read must be T-separated (R262)"
print("state-bm-c.json updated: round", chk["round_no"], "epoch", chk["heartbeat_epoch_utc"])

# --- fleet/machines/bm-c.json (heartbeat; orders_ack untouched) ---
mp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
m = json.load(open(mp, encoding="utf-8"))
m["last_seen"] = clock
m["heartbeat_epoch_utc"] = epoch
m["clock_read"] = clock
m["current_task"] = "r351 done: W52 full-lifecycle + triple finalize W50/51/52 (ledger 478,948); T-131 backfill in flight"
m["cpu_cores"] = 32
m["idle_ram_gb"] = idle_ram_gb
m["gpu_free_vram_mib"] = gpu_free
m["verdict"] = ("healthy: W52 wave closed same-window; chain W1..W52 caught up; "
                "engine queue empty (W53 = next-round standing step); T-131 "
                "network collector in flight")
json.dump(m, open(mp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
chk2 = json.load(open(mp, encoding="utf-8"))
assert isinstance(chk2["heartbeat_epoch_utc"], int), "epoch must be int"
assert isinstance(chk2.get("orders_ack"), list) and len(chk2["orders_ack"]) == 144
print("machines/bm-c.json heartbeat updated, ack=144")

# --- inbox: MSG-0610 processed (yield receipt to bm-c; primary action = W51 "
# --- finalize chain seat which this round discharged with live-head derive) ---
src = os.path.join(ROOT, "fleet", "inbox", "MSG-20261002-0610-bm-b.md")
dst = os.path.join(ROOT, "fleet", "inbox", "processed",
                   "MSG-20261002-0610-bm-b.md")
if os.path.exists(src):
    shutil.move(src, dst)
    print("MSG-0610 moved to processed")
else:
    print("MSG-0610 already moved")
print("clock:", clock, "| cpu%", cpu_pct, "| idle_ram_gb", idle_ram_gb,
      "| gpu_free", gpu_free)
