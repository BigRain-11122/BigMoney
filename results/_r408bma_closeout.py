"""r408 bm-a closeout: state round_no 408 + heartbeat (int epoch, T-sep
clock, R170/R178/R262 laws) + round report append. One-shot."""
import json
import os
import time
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.now(timezone(timedelta(hours=8)))
TS = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")

import psutil
idle_ram_gb = round(psutil.virtual_memory().available / (1024 ** 3), 1)
cores = os.cpu_count() or 1

gpu_vram_free = "n/a"
try:
    import subprocess
    r = subprocess.run(
        ["nvidia-smi", "--query-gpu=memory.free",
         "--format=csv,noheader,nounits"],
        capture_output=True, text=True, timeout=20)
    if r.returncode == 0 and r.stdout.strip():
        gpu_vram_free = f"{int(r.stdout.strip().splitlines()[0])}MB"
except Exception:
    pass

# 1) state file
sp = os.path.join(ROOT, "state-bm-a.json")
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 408
st["did"] = ("r408: W5-GENERATE harvest closure trio (r244 landed-marker "
             "law): product verify n=3926 distinct (prereg band [2800,4600] "
             "PASS; raw 5000 -> excl 1 -> dedup 4999 -> 3926; grammar "
             "29720178c39425de; ledger wave-5 row runner-written) + "
             "screen-prep PASS 16s + pool surgery (GENERATE ready->done + "
             "TRIAL-LABOR-W5-SCREEN direct-ready 4,126 cells) + commit "
             "ef9e07c2 push LANDED + S6 36 legs rc=0 nonzero=[]")
st["verify"] = ("smoke 26/26; prep gates fail-closed all-asserted (panel "
                "48/48, anchors 6/6, census L 1253/1127/875, G-VOL/G-YANG "
                "raw-face anchors live); pool flip JSON round-trip; push "
                "b424baf4..ef9e07c2; S6 36/36 rc=0; orders double-scan "
                "zero unacked; heartbeat epoch int self-asserted")
st["next"] = ("(1) W5-SCREEN burn watch (autofill claim -> minutes-level "
              "pool batch) -> screen-finalize (ledger TRIAL_LAB_W5_SCREEN "
              "+ w5_screen.json + survivors feed W5-JUDGE entry parked "
              "waiting per prereg sec.0 physical-order gate); (2) 10-01 "
              "month-first triple fire (science_audit+monthly_briefing+"
              "self_review SR6) + REGIME_GUARD v3 date gate opens; (3) "
              "next 5x=r410 HANDOVER; (4) T-109 s2 probe-face watch "
              "(bm-c lane)")
st["last_round_at"] = TS
st["current_task"] = ("r408: W5 generate harvested + screen entered; "
                      "watch autofill screen burn")
st["updated"] = NOW.strftime("%Y-%m-%d %H:%M:%S")
st["round"] = 408
st["loop_round"] = 408
with open(sp, "w", encoding="utf-8") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)

# 2) heartbeat
hp = os.path.join(ROOT, "fleet", "machines", "bm-a.json")
hb = json.load(open(hp, encoding="utf-8"))
epoch = int(time.time())
assert isinstance(epoch, int)
hb["last_seen"] = TS
hb["current_task"] = st["current_task"]
hb["cpu_cores"] = cores
hb["idle_ram_gb"] = idle_ram_gb
hb["gpu_free_vram"] = gpu_vram_free
hb["verdict"] = ("green; W5-GENERATE harvested done (n=3926), W5-SCREEN "
                 "pool entry ready for autofill claim; board 0 open; "
                 "orders 130/130 acked (double-scan)")
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = TS
with open(hp, "w", encoding="utf-8") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in chk["clock_read"], "clock_read must be T-separated"
print(f"heartbeat ok: epoch={chk['heartbeat_epoch_utc']} "
      f"clock={chk['clock_read']} ram={idle_ram_gb}GB gpu={gpu_vram_free}")

# 3) round report append
rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-a.md")
line = (
    f"{TS} | R408 bm-a (dept:策略+研究·W5 generate 收口轮) | "
    "WM first-line verdict: green (red=false; probe 02:11 "
    "py_low_with_work_cands py 3.9-6.2% -- legal: W5-SCREEN pool entry "
    "entered ready THIS round = next autofill claim burns meaningful "
    "work; cpu_total 83% = OTHER session's census tmp-script burn, not "
    "repo face; board 0 open + bandit 0) | did: S0-1 anchor bm-a + S0 "
    "clean pull + S0.5 orders full-name diff zero unacked (双扫 both "
    "passes) + decisions: D-20260929-02 receipt = BOTH legs landed "
    "(r406 inbox_guard fetch-freeze submit/pass 9/9 + r407 T-115 "
    "claims-face origin read; this round W5 harvest honored the "
    "protocol: fetch-before-submit + landed-marker flip before stale "
    "window) + D-20260929-03 BigDomain legal-routing = 非本仓例零动作 + "
    "S1 smoke 26/26 + S2 双板 job_list 0 + fleet 0 open (bm-a in-flight: "
    "T-102/T-109/T-97/T-98/T-114 claimed) + S3 MAIN CLOSURE **W5-"
    "GENERATE 收口三件套**: (1) product verify -- n=3926 distinct (prereg "
    "sec.5 band [2800,4600] PASS), raw 5000 (A500/B4500) -> exclusion "
    "hits 1 (W5-B-0670 dual_momentum w2_screen_survivor semantic "
    "completion, disclosed) -> dedup 4999->3926, zero engine cells "
    "burned, single-shot marker intact, grammar sha16 29720178c39425de "
    "anchored, TRIAL_GRAMMAR_LEDGER wave-5 row runner-written 01:58:30; "
    "(2) screen-prep PASS 16s (G-PANEL 48/48 + G-ANCHOR registered-six "
    "faithful on W5 eight-tuple identity face + G-CENSUS L "
    "{1253,1127,875} + G-EXCLUDE {A:0,B:1} + G-VOL raw-face anchors "
    "{519,1523,1441} + G-YANG raw-face anchors {1751,962,914} both "
    "re-verified live fail-closed; leg-L disclosure faces 594calm/"
    "518wild + 819yang/812red structural-only per prereg sec.2); (3) "
    "pool surgery (Tools/_r408_w5_harvest_flip.py, JSON round-trip "
    "self-verified) -- GENERATE ready->done (r244 landed-marker law) + "
    "**TRIAL-LABOR-W5-SCREEN direct-ready** (4,126 cells = 3,926 "
    "distinct + 200 nulls; runner screen-prep gate + tl2._ram_gate_gb "
    "4GB three-sample in-runner; W2/W3/W4-SCREEN lineage; done BEFORE "
    "02:15 same-version cooldown expiry = stale-takeover relaunch "
    "double-burn blocked; 02:00 tick relaunch_cooldown had held the "
    "line) + commit ef9e07c2 push LANDED b424baf4..ef9e07c2 || S6 36 "
    "legs rc=0 nonzero=[] (audit v2.4.1 py 6.2%/cpu 83%; probe "
    "py_low_with_work_cands; daily no-new cutoff 09-28; regime ORANGE "
    "breadth 0.83 shadow; clock CALL-0928 ORANGE_COOL sleeves4 act0; "
    "lhb/heat/futures/repo/options cutoff-covered zero-network; MF "
    "throttle 18.4min; sinaMF 20td in-window; astock/etf/revosc/"
    "minfeed/alloc/fundprem lane-guard no-op; ths same-day idempotent; "
    "AH throttle 18min; fundamental 16.3h fresh-skip; blf 5-gates "
    "all_pass; live_paper OK shadow; t35v PASS zero-pending; t24 22/22 "
    "drift0 + promotion 0/22 honest; aggr/grid/sysv1 idempotent marks@"
    "cutoff; t35e 09-28 6traders; scorecard 6/28/7 15.3s; REPORT-0929 "
    "faces4 token1; LIVE-0929 ORANGE cap50%; build 432combos; token "
    "L2 delta=0) || S7: schtasks Loop pin=8 Running next 02:18 + "
    "Watchdog re-reg first fire 02:20 + claw MATCH no-op + inbox 净 | "
    "verify: smoke 26/26 + prep fail-closed gates + pool JSON "
    "round-trip + push LANDED + S6 36/36 + orders double-scan zero + "
    "heartbeat epoch int self-asserted | next: (1) W5-SCREEN burn watch "
    "-> screen-finalize (ledger TRIAL_LAB_W5_SCREEN + w5_screen.json + "
    "w5_screen_cells.csv + survivors -> W5-JUDGE entry parked waiting "
    "per sec.0 physical-order; 48h CEO 告报钟 from judge-finalize); (2) "
    "10-01 month-first triple fire + REGIME_GUARD v3 opens; (3) next "
    "5x=r410 HANDOVER; (4) T-109 s2 probe-face watch (bm-c lane)\n")
with open(rp, "a", encoding="utf-8") as fh:
    fh.write(line)
print("report appended:", line[:120], "...")
