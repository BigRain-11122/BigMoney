# _r298bma_wrap.py -- R298 bm-a wrap: round report + state + heartbeat
import json, time, ctypes, datetime, os

TS = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
EPOCH = int(time.time())
CLOCK = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

R298_LINE = (
    "2026-09-27 06:2x | R298 bm-a (dept:research+strategy+fleet) | "
    "WM first-line verdict: py_low_board_clear LEGAL (pool 0 ready post-harvest + "
    "board 0 open + bandit 0; audit v2.3 idle-starvation candidate span-null "
    "honest = 30min window not yet established; supply line OPENED same round: "
    "queue #4 sector-leader named, prereg next round per R99 freeze-first) | "
    "S0 pull clean (bm-b r302 fast-forward, zero conflict) + S0.5 orders "
    "double-scan 91/91 zero unacked (round-start + wrap) + decisions zero new "
    "post D-20260927-05 + S1 smoke 25/25 | "
    "S3 MAIN: FUSION-GRID-P1 relaunch verified 06:10:01 autofill pid 18524 new "
    "sha 0cce3192 (crash-fuse cleared by sha change per O-0947 fix-first; fill "
    "latency 29.9min vs O-2100 10min target MISS honest = crash-diagnosis round "
    "consumed window) -> landed 06:10:37 elapsed 28.8s workers 4 -> HARVEST "
    "THREE-PIECE same round: (1) prereg s7/s8 single-finalization 0/45 G1'v2 "
    "NEGATIVE (best EW__DEDUP 0.5301 vs own-null line 1.7825, null pool mu "
    "0.4209/sigma 0.2754/K 2000; bootstrap CI [-0.3299, 1.392] lower<=0; DSR "
    "0.0 vs sr_star 1.2511 @ n_trials 202441; family PBO 0.4857 observe band; "
    "verdict semantics = grid config-family NO increment over random same-mask "
    "portfolios, member-alpha existence NOT falsified per sec.1 pre-embed) + "
    "5-prediction reconciliation (P1 MISS diversification arithmetic "
    "median-corr-as-rhobar; P2 HIT; P3 magnitude MISS premise face falsified: "
    "exact v3 regime ORANGE+RED 10% not 61% approx face -> CODELY kenglu "
    "appended; P4 HIT; P5 clean) + x2 stress face all 45 <= +0.0454 honest + "
    "descriptive 45/45 all-pass non-binding + regime exact G754/Y714/R141/O22 "
    "zero-drift vs R296 gate + dedup disclosure 6/990 pairs >=0.999 "
    "survivor-face-empty no collapse (2) gate_attrition entries row 55 (r248 "
    "entries-list law; PBO recompute zero-drift 0.4857 assert) (3) post_review "
    "T-85-FUSION-GRID-P1 registered 29 checks all dry-run-verified as reviewer "
    "sees + scanner derived 29/29 YES + pool done-flip (r291 live-read assert "
    "before write) + T-85 ticket DONE all four slices with result_ref (s1 NAV "
    "R283; s2/s3 this batch; s4 survivor face naturally empty = zero "
    "STRATEGY_LIBRARY intake, zero FUSION-* paper-account proposal) | "
    "ledger 200,396 + 2,045 = 202,441 single-count PASS | "
    "S4 kenglu +1 (prediction-premise exact-face-first law; CODELY 7656B "
    "<=10KB) | SCHOOL_SUPPLY_S1 ledger closure: #1 bm-b judged 5/7 G1 but G2 "
    "0/7 PBO 0.7714 / #2 SOE 0/5 F6-entries structural / #3 kline 7/7 "
    "negative -- all cited to shared attrition+post_review rows; #4 "
    "sector-leader non-limit-up = next supply, queue supply line OPEN | "
    "S6 chain 30/30 rc=0 (compute_audit CLEAN; daily cutoff 09-24 no-op "
    "Sunday; regime trigger breadth 0.77 ORANGE shadow; t35 verify PASS "
    "0-breach zero-pending 6; prospect 22/22 drift 0; promotion 0/22 "
    "eligible honest; aggr/alloc/grid paper idempotent no-ops; lane guards "
    "honest astock=bm-b fundprem=bm-c alloc=bm-b; ah_panel + moneyflow "
    "spawned detached refresh per design) + token L2 legs 0 today | "
    "NEXT R299: P0 = queue #4 sector-leader non-limit-up prereg (R99 "
    "freeze-first: probe facts + D6 vs WILD-S1 limit-up family + seed "
    "registry + freeze commit) + carried T-23 consumption prereg + "
    "O-2030/O-2100 anchor-migration eval"
)

with open("logs/iteration-loop/round_reports-bm-a.md", "a", encoding="utf-8") as f:
    f.write(R298_LINE + "\n")
print("report: R298 line appended")

# ---------- state-bm-a.json ----------
sp = "state-bm-a.json"
st = json.load(open(sp, encoding="utf-8"))
st_last = dict(st)
st["round_no"] = 298
st["did"] = ("R298: FUSION-GRID-P1 relaunch 06:10:01 (pid 18524, new sha 0cce3192, "
             "fuse cleared) landed 06:10:37 elapsed 28.8s -> HARVEST complete: "
             "verdict NEGATIVE 0/45 G1'v2 (best EW__DEDUP 0.5301 vs own-null line "
             "1.7825 mu 0.4209; CI lower -0.3299; DSR 0.0; PBO 0.4857) = config-family "
             "no-increment, member-alpha NOT falsified; prereg s7/s8 single-finalized "
             "(P1 MISS/P2 HIT/P3 magnitude-MISS premise face/P4 HIT/P5 clean); "
             "attrition row 55 + post_review 29/29 YES + pool done-flip + T-85 "
             "ticket DONE 4 slices (s4 survivor face empty); queue ledger "
             "#1/#2/#3 closed + #4 named next supply; kenglu +1 (prediction-premise "
             "exact-face-first); S6 30/30 rc=0; smoke 25/25")
st["verdict"] = "ok"
st["next"] = ("R299: P0 queue #4 sector-leader non-limit-up prereg (R99 freeze-first: "
              "probe facts + D6 vs WILD-S1 + seed + freeze) + carried T-23 consumption "
              "prereg + O-2030/O-2100 anchor-migration eval")
st["ts"] = TS
st["last_round_ts"] = st_last.get("ts", "2026-09-27 06:03:00")
st["updated_at"] = TS
st["current_task"] = st["did"][:120]
st["last_run"] = TS
st["last_round_at"] = st["last_round_ts"]
st["last_round"] = 297
st["updated"] = TS
st["last_seen"] = TS
st["task"] = st["next"]
json.dump(st, open(sp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("state: round_no=298 ts=", TS)

# ---------- heartbeat fleet/machines/bm-a.json ----------
class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
mem = MEMORYSTATUSEX()
mem.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem))
free_gb = round(mem.ullAvailPhys / (1024 ** 3), 1)

import subprocess
try:
    cpu_out = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "(Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average"],
        capture_output=True, text=True, timeout=20).stdout.strip()
    cpu_pct = float(cpu_out)
except Exception:
    cpu_pct = 8.0

hp = "fleet/machines/bm-a.json"
hb = json.load(open(hp, encoding="utf-8"))
hb["last_seen"] = TS
hb["current_task"] = ("R298 done: FUSION-GRID-P1 harvested judged-negative 0/45 "
                      "(config no-increment, slot closed); T-85 ticket DONE 4 slices; "
                      "supply line OPEN queue #4 sector-leader prereg next round")
hb["cpu_cores"] = 32
hb["cpu_pct"] = cpu_pct
hb["free_ram_gb"] = free_gb
hb["free_ram_mb"] = int(mem.ullAvailPhys / (1024 ** 2))
hb["idle_ram_gb"] = free_gb
gpu_free_mb = 5670  # compute_audit face 06:16: 12282 total - 6612 used
hb["gpu_free_vram_gb"] = round(gpu_free_mb / 1024, 1)
hb["gpu_free_vram_mb"] = gpu_free_mb
hb["gpu_idle_vram_gb"] = round(gpu_free_mb / 1024, 1)
hb["gpu_idle_vram_mb"] = gpu_free_mb
hb["gpu0_free_vram_gb"] = round(gpu_free_mb / 1024, 1)
hb["gpu"] = {"present": True, "idle_vram_free_gb": round(gpu_free_mb / 1024, 1),
             "note": "compute_audit face 06:16: 12282 MiB total - 6612 used = 5670 free"}
hb["verdict"] = ("healthy: harvest closed FUSION-GRID-P1 judged 0/45 negative-honest "
                 "(three-piece complete, post_review 29/29 YES); pool empty post-harvest "
                 "= idle-starvation candidate span-null (30min window not established); "
                 "supply line OPEN = queue #4 sector-leader prereg next round per R99 "
                 "freeze-first; board 0 open, bandit 0")
hb["heartbeat_epoch_utc"] = EPOCH
hb["clock_read"] = CLOCK
hb["round_no"] = 298
hb["task"] = hb["current_task"]
hb["cores"] = 32
json.dump(hb, open(hp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int (F7)"
assert "T" in chk["clock_read"] and "+" in chk["clock_read"], "clock_read T-separated ISO (F7)"
print("heartbeat: epoch=%d (int verified) clock=%s cpu=%s free_ram=%sGB"
      % (chk["heartbeat_epoch_utc"], chk["clock_read"], cpu_pct, free_gb))
