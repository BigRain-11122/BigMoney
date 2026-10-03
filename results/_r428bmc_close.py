# -*- coding: utf-8 -*-
"""_r428bmc_close.py -- r428 S7 closeout (maintenance round + chain-restore fix, burn in flight).
Laws: heartbeat_epoch_utc JSON int (R170/R178); clock_read ISO-8601 T-sep (R262);
round report fields ts|round|did|WM|dept|verify|next; targeted adds only (dirty-at-start tree).
"""
import datetime
import json
import os
import subprocess
import time

os.chdir(r"K:\Fluxgroup\FluxGroup\quant\bigmoney")
NOW = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())
CREATE_NO_WINDOW = 0x08000000

import psutil
cpu_pct = round(psutil.cpu_percent(interval=1), 1)
idle_ram = round(psutil.virtual_memory().available / 1e9, 1)
try:
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                         capture_output=True, text=True, creationflags=CREATE_NO_WINDOW, timeout=20)
    gpu_free = int(out.stdout.strip().splitlines()[0])
except Exception:
    gpu_free = -1

wm = json.load(open("results/watermark_red.json", encoding="utf-8"))
print("samples: cpu=%s%% ram_free=%sGB gpu_free=%sMiB wm_red=%s wm_lane=%s"
      % (cpu_pct, idle_ram, gpu_free, wm.get("red"), wm.get("lane")))

# burn face (polled fact, not hand-copied)
burn_alive = False
burn_cpu = 0
try:
    pr = psutil.Process(31276)
    ct = pr.cpu_times()
    burn_alive = pr.status() != psutil.STATUS_ZOMBIE
    burn_cpu = round(ct.user + ct.system)
except psutil.NoSuchProcess:
    pass
print("burn: alive=%s cpu_sec=%d w2_judge=%s" % (burn_alive, burn_cpu,
      os.path.exists("results/mass_trial/w2_judge.json")))

def sg(args):
    p = subprocess.run(["git"] + args, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", creationflags=CREATE_NO_WINDOW)
    return p.returncode, (p.stdout or "") + (p.stderr or "")

DID = ("r428 bm-c: (1) MAIN FIX (chain integrity): S6 canonical restore -- r427 driver had "
       "silently dropped 4 legs (update_fund_premium bm-c-lane T-16 + live_paper/"
       "t35_open_fill_verify/t24_prospect_paper new-bar detection surface); a static per-round "
       "driver without those legs can never see a new bar arrive; r428 driver "
       "Tools/_r428bmc_s6.py restores r426's 37-leg always-run-with-honest-no-op form; r427 "
       "'S6 34 legs' report corrected = 33 executed (off-by-one, disclosed, no history "
       "rewrite); standing guard = per-round driver adaptation must re-diff leg list vs "
       "canonical prompt, not blind-copy prior round. (2) WAVE-2 FINALIZE BURN POLL: detached "
       "PID 31276 alive through close (spawned 19:28:59, cpu 4020->4326s across round, "
       "single-thread family CSCV PBO over 805 cells); w2_judge.json honestly absent -- "
       "adoption deferred to landing round per r422 law (deadline <=10-06, O-2115 acceptance "
       "10-08). (3) S0: FF integrate 5 bm-b commits (54d70a72b..23aca6c1f r633 window: NULLS "
       "trio watch healthy + 9-face UU merge recovery + MSG-2015 processed); dirty-at-start 3 "
       "bm-c daemon faces + deferred finalize log (kept deferred, burn open-handle). (4) S0.5: "
       "orders 152/152 zero-unacked double-scan; D-19 4167B784 MATCH zero-consume; group "
       "orders.md 68947C17 MATCH; MSG-2015 = bm-a->ALL F-04 G2_SLOT_OLD_P1 claim declaration, "
       "bm-c FYI-only zero action (T-159 = bm-a lane). (5) S1 smoke 47/47; SatEngine rc0 alive "
       "(N1 waves 1-114 in register). (6) S6 37/37 rc0: ZERO-DRIFT streak 27; fund_premium "
       "restored leg = weekend no-op honest; live_paper anchor OK (5 bars since 09-23, golden "
       "week no new bar); lane guards all honest no-ops; CEO faces (daily_scorecard/dashboard/"
       "paper_export/t35_fill) stale-takeover derive legal (bm-a hb 20:24:41 >20min STALE_MIN "
       "law O-2100 s2.4). (7) S4 pit +1 -> research/pit-ps.md (Select-String comma-list "
       "missing-path = whole-call binding abort, $null.Count prints blank = silent "
       "false-negative; nearly mis-indicted r426 leg-drop; T1-T4 controlled experiments "
       "root-caused; PS 语义面家族). (8) S7 4/4: loop pin=5 no-op, watchdog registered, both "
       "claws LF-fresh, attrition CLEAN rc0 (2 healed historical shrinks noted).")
NEXT = ("(a) r429: poll judge-finalize --wave 2 burn PID 31276 -> if w2_judge.json landed: "
        "adopt (complete=true 805 cells, ledger single-shot chain-linear, E[FP], G2-eligible, "
        "verdicts) via _r426bmc_close.py template adapted to landing round + idempotent "
        "finalize rerun no-op check + commit product+deferred log receipt atomically, "
        "deadline <=10-06; O-2115 wave-2 acceptance evidence pack 10-08; (b) D-06 "
        "full-reconciliation closeout 10-07; (c) T-143 assembly window post-10-09 (deliverable "
        "10-29); (d) moneyflow GM ruling watch (MSG-1452/1543); (e) W14 lane zero-touch "
        "pending GM dual-ruling; (f) bm-a heartbeat staleness watch (last_seen 20:24:41; >3h = "
        "GM 改派呈报).")
VERIFY = ("probe receipts (_r427bmc_probe.py rerun: orders 152/152, D19 4167B784 MATCH, GORDERS "
          "68947C17 MATCH, WM red=false, burn alive, 1 live mass-trial proc); smoke 47/47; S6 "
          "37/37 rc0 (_r428bmc_s6_log.txt; ZERO-DRIFT streak 27; fund_premium weekend no-op "
          "rc0); Select-String pit T1-T4 controlled-experiment receipts in-session; attrition "
          "CLEAN rc0; loop pin=5 no-op; watchdog registered; claws installed x2; push delivery "
          "verify post-commit (本地未达 origin=0)")

sp = "state-bm-c.json"
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 428
st["clock_read"] = NOW
st["cpu_pct"] = cpu_pct
st["current_task"] = ("r428: S6 canonical 37-leg chain restore done (fund_premium + new-bar "
                      "surface, 37/37 rc0); W2 finalize burn IN FLIGHT (PID 31276, cpu %ds at "
                      "close); next: r429 poll -> adopt w2_judge.json at landing (template "
                      "_r426bmc_close.py), deadline <=10-06" % burn_cpu)
st["did"] = DID
st["gpu_free_vram_mib"] = gpu_free
st["heartbeat_epoch_utc"] = EPOCH
st["idle_ram_gb"] = idle_ram
st["last_seen"] = NOW
st["last_round"] = ("r428 bm-c: S6 canonical chain restore (37 legs incl fund_premium + new-bar "
                    "surface) + wave-2 finalize burn poll (in flight), S7 4/4 green")
st["last_round_at"] = NOW
st["last_round_ts"] = NOW
st["last_ts"] = NOW
st["last_decisions_read_at"] = NOW
st["next"] = NEXT
st["updated"] = NOW
st["updated_at"] = NOW
st["verify"] = VERIFY
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
assert isinstance(json.load(open(sp, encoding="utf-8"))["heartbeat_epoch_utc"], int), "epoch int"
print("state-bm-c.json written (round_no=428; epoch=%d int-verified)" % EPOCH)

WM_LINE = ("WM 绿（red=false lane healthy；golden-week 合法 idle·board 零 open·bandit next_pick "
           "moneyflow-IC 源阻断维持）" if not wm.get("red")
           else "WM 红（red=true @%s）" % wm.get("ts"))
rl = "%s\t| r428 bm-c\t| %s\t| %s | dept:工程/舰队\t| %s\t| %s\n" % (NOW, DID, WM_LINE, VERIFY, NEXT)
with open("round_reports-bm-c.md", "a", encoding="utf-8") as fh:
    fh.write(rl)
print("round_reports-bm-c.md appended")

hp = "fleet/machines/bm-c.json"
hb = json.load(open(hp, encoding="utf-8"))
hb["activity_now"] = ("r428: S6 canonical 37-leg chain restore (r427 4-leg drop corrected); "
                      "wave-2 finalize burn poll -- IN FLIGHT (PID 31276 cpu %ds); adoption at "
                      "landing via template, deadline <=10-06" % burn_cpu)
hb["clock_read"] = NOW
hb["cpu_pct"] = cpu_pct
hb["cpu_util_pct"] = cpu_pct
hb["free_ram_gb"] = idle_ram
hb["ram_free_gb"] = idle_ram
hb["idle_ram_gb"] = idle_ram
hb["gpu_free_mb"] = gpu_free
hb["gpu_free_vram_mb"] = gpu_free
hb["gpu_free_vram_mib"] = gpu_free
hb["gpu_idle_vram_mb"] = gpu_free
hb["gpu_idle_vram_mib"] = gpu_free
hb["current_task"] = st["current_task"]
hb["heartbeat_epoch_utc"] = EPOCH
hb["last_seen"] = NOW
hb["last_seen_at"] = NOW
hb["updated_at"] = NOW
hb["latest_artifact"] = ("Tools/_r428bmc_s6.py (S6 37-leg canonical restore) + "
                         "results/_r428bmc_s6_log.txt (37/37 rc0, ZERO-DRIFT streak 27) + "
                         "research/pit-ps.md r428 Select-String pit @ %s" % NOW)
hb["next_milestone"] = ("wave-2 judge product w2_judge.json adoption <=10-06 (burn ETA hours; "
                        "OS 10-min poll); O-2115 acceptance evidence pack 10-08; D-06 "
                        "closeout 10-07")
hb["prod_lanes"] = ("MASS_TRIAL_W2 finalize burn in flight (PID 31276); moneyflow lane "
                    "GM-ruling pending; D-06 closeout 10-07")
hb["round_no"] = 428
hb["verdict"] = "healthy"
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int)
print("heartbeat written (epoch int verified, orders_ack kept: %d entries)" % len(chk.get("orders_ack", [])))
sg(["fetch", "origin"])
rc, behind = sg(["rev-list", "--count", "HEAD..origin/main"])
print("origin behind pre-commit=%s" % behind.strip())
print("CLOSE_OK")
