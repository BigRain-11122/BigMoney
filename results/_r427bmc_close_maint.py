"""_r427bmc_close_maint.py -- r427 S7 closeout (maintenance round, product in flight).
Laws: heartbeat_epoch_utc JSON int (R170/R178); clock_read ISO-8601 T-sep (R262);
round report fields ts|round|did|verify|next; targeted adds only (dirty-at-start tree).
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

DID = ("r427 bm-c: (1) WAVE-2 JUDGE-FINALIZE POLL (state next-a line): detached burn PID 31276 "
       "still IN FLIGHT at close 20:21 (spawned 19:28:59, cpu 2986s ~ wall = single-thread "
       "actively computing family CSCV PBO over 805 cells; product w2_judge.json writes only at "
       "finalize end -- honestly absent; per r422 adoption law detached burn lifetime is "
       "session-independent, OS loop 10-min poll adopts at landing via template "
       "_r426bmc_close.py; deadline <=10-06, O-2115 acceptance 10-08 -- 5 days margin). "
       "(2) S0: zero-action (HEAD==origin 0/0 post r426b addendum push; dirty-at-start 5 files "
       "all bm-c-owned runtime faces + deferred finalize log). (3) S0.5: orders 152/152 "
       "zero-unacked (mechanical dir-vs-ack diff); D-19 4167B784 MATCH zero-consume; group "
       "orders.md 68947C17 face unchanged; decisions/orders 双面零消费. (4) S1 smoke 47/47 "
       "fresh; SatEngine rc0 alive (N1 waves 59-114). (5) S6 34 legs ALL rc0: ZERO-DRIFT streak "
       "26; market_clock CALL-2026-09-30 ORANGE_COOL; golden-week lane guards all honest no-op; "
       "daily_report REPORT-2026-10-03 + LIVE-2026-10-03 idempotent regen; token L2 3 legs today. "
       "(6) S7 4/4: loop pin=5 no-op; watchdog registered (idempotent); both claws LF-fresh "
       "installed; attrition CLEAN rc0. r426 deferred finalize-log receipt kept deferred "
       "(open-handle rationale: burn exit may append completion line -- adoption round commits "
       "it atomically with product).")
NEXT = ("(a) r428: poll judge-finalize --wave 2 burn PID 31276 -> if w2_judge.json landed: adopt "
        "(complete=true 805 cells, ledger single-shot chain-linear, E[FP], G2-eligible, "
        "verdicts) via _r426bmc_close.py template adapted to landing round + idempotent "
        "finalize rerun no-op check + commit product+deferred log receipt atomically, "
        "deadline <=10-06; O-2115 wave-2 acceptance evidence pack 10-08; (b) D-06 "
        "full-reconciliation closeout 10-07; (c) T-143 assembly window post-10-09 (deliverable "
        "10-29); (d) moneyflow GM ruling watch (MSG-1452/1543); (e) W14 lane zero-touch pending "
        "GM dual-ruling; (f) bm-b SHARD-1 duplicate-delivery watch (MSG-1909 sec.2).")
VERIFY = ("burn poll receipts: PID 31276 alive cpu_sec=2986 at 20:21:06 + w2_judge.json absent "
          "(probe _r427bmc_probe.py: D19 SHA 4167B784 MATCH, GORDERS SHA 68947C17 MATCH, orders "
          "152/152, WM red=false); smoke 47/47; S6 34 legs rc0 (_r427bmc_s6_log.txt; dualrun "
          "ZERO-DRIFT streak 26); attrition CLEAN rc0; loop pin=5 no-op; watchdog registered; "
          "claws installed x2; push delivery verify post-commit (本地未达 origin=0)")

sp = "state-bm-c.json"
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 427
st["clock_read"] = NOW
st["cpu_pct"] = cpu_pct
st["current_task"] = ("r427: judge-finalize --wave 2 burn IN FLIGHT (PID 31276, cpu %ds at "
                      "close); next: r428 poll -> adopt w2_judge.json at landing (template "
                      "_r426bmc_close.py), deadline <=10-06" % burn_cpu)
st["did"] = DID
st["gpu_free_vram_mib"] = gpu_free
st["heartbeat_epoch_utc"] = EPOCH
st["idle_ram_gb"] = idle_ram
st["last_seen"] = NOW
st["last_round"] = "r427 bm-c: maintenance round -- wave-2 finalize burn poll (in flight), S6 34 legs rc0, S7 4/4 green"
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
print("state-bm-c.json written (round_no=427; epoch=%d int-verified)" % EPOCH)

WM_LINE = ("WM 绿（red=false lane healthy；golden-week 合法 idle·board 零 open·bandit next_pick "
           "moneyflow-IC claimed-by-other 维持）" if not wm.get("red")
           else "WM 红（red=true @%s）" % wm.get("ts"))
rl = "%s\t| r427 bm-c\t| %s\t| %s | dept:策略/研究\t| %s\t| %s\n" % (NOW, DID, WM_LINE, VERIFY, NEXT)
with open("round_reports-bm-c.md", "a", encoding="utf-8") as fh:
    fh.write(rl)
print("round_reports-bm-c.md appended")

hp = "fleet/machines/bm-c.json"
hb = json.load(open(hp, encoding="utf-8"))
hb["activity_now"] = ("r427: wave-2 judge-finalize burn poll -- IN FLIGHT (PID 31276 cpu %ds); "
                      "S6 34 legs rc0; adoption at landing via template, deadline <=10-06"
                      % burn_cpu)
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
hb["latest_artifact"] = ("results/mass_trial/w2_judge_shard_0-3of4.jsonl (805/805 rows on "
                         "origin, r423-426) + in-flight w2_judge.json finalize burn (r427 poll "
                         "receipts _r427bmc_probe.py) @ %s" % NOW)
hb["next_milestone"] = ("wave-2 judge product w2_judge.json adoption <=10-06 (burn ETA hours; "
                        "OS 10-min poll); O-2115 acceptance evidence pack 10-08; D-06 closeout "
                        "10-07")
hb["prod_lanes"] = ("MASS_TRIAL_W2 finalize burn in flight (PID 31276); moneyflow lane "
                    "GM-ruling pending; D-06 closeout 10-07")
hb["round_no"] = 427
hb["verdict"] = "healthy"
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int)
print("heartbeat written (epoch int verified, orders_ack kept: %d entries)" % len(chk.get("orders_ack", [])))
sg(["fetch", "origin"])
rc, behind = sg(["rev-list", "--count", "HEAD..origin/main"])
print("origin behind pre-commit=%s" % behind.strip())
print("CLOSE_OK")
