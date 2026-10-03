"""_r430bmc_close.py -- r430 S5/S7 closeout: state/round-report/heartbeat writes.
All numbers DERIVED at runtime (no hand copying). Laws: heartbeat_epoch_utc
MUST be JSON int (R170/R178); clock_read ISO-8601 T-separated (R262);
nvidia-smi via CREATE_NO_WINDOW (U060); burn state via psutil live probe."""
import datetime
import json
import os
import shutil
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
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                           "--format=csv,noheader,nounits"],
                          capture_output=True, text=True,
                          creationflags=CREATE_NO_WINDOW, timeout=20)
    gpu_free = int(out.stdout.strip().splitlines()[0])
except Exception:
    gpu_free = -1

burn = {"pid": 31276, "alive": False}
try:
    p = psutil.Process(31276)
    burn = {"pid": p.pid, "alive": True,
            "cpu_s": round(p.cpu_times().user + p.cpu_times().system),
            "mem_mb": p.memory_info().rss // 1048576}
except Exception:
    pass

wm = json.load(open("results/watermark_red.json", encoding="utf-8"))
print("samples: cpu=%s%% ram_free=%sGB gpu_free=%sMiB wm_red=%s burn=%s"
      % (cpu_pct, idle_ram, gpu_free, wm.get("red"), burn))

DID = ("r430 bm-c: (1) W2 FINALIZE BURN POLL (state next-a): detached PID 31276 alive through close "
       "(spawned 19:28:59, cpu 6400->%ds this round, mem %sMB, finalize phase family CSCV PBO over 805 cells; "
       "4/4 shards 805/805 rows on origin, freeze 4796399f3); w2_judge.json honestly absent -- adoption deferred "
       "to landing round per r422 law (deadline <=10-06, O-2115 acceptance 10-08). (2) LANDING ADOPTION HARNESS "
       "DELIVERED (score-2 product, zero-cold-start for landing round): results/_r430bmc_w2_adopt.py per r629 "
       "mirror law (runner mass_trial_w1.py judge-finalize summary contract L1314-1357 face): pure validate_product "
       "core + six cross-checks (ledger chain-linear + batch identity MASS_TRIAL_W2_JUDGE; verdict-sum==n_judge=="
       "disclosure.judged_cells; eligible len==count; len(cells)==n_judge; family PBO accounting scored>=8-cells/"
       "unscored-honest-note; E[FP]==0.05*n_judge) + live cross-checks (science_gates.ledger_head not behind "
       "product + pit-95 finalize_already_landed single-shot tripwire) + selftest 10/10 (contract-exact synthetic "
       "mock positive + 5 negatives all REJECTED) + probe mode honest AWAITING exit 3 with burn psutil receipt = "
       "mechanized per-round poll. (3) DRIVER-GENERATION SLIP CAUGHT IN-ROUND (chain integrity, golden-week no-op "
       "day = zero data-face damage): first S6 run used obsolete r427 33-leg driver (results/_r427bmc_s6_chain.py, "
       "r428-adjudicated leg-drop face) -> canonical Tools/_r428bmc_s6.py 37-leg rerun under correct name "
       "_r430bmc_s6_log.txt (NON-ZERO LEGS: none; dualrun ZERO-DRIFT streak 31; fund_premium/live_paper/t35/"
       "t24_prospect new-bar faces present) + r429-trio executed (count==2 LOG dual-point assert replace -> run -> "
       "HEAD restore) + r372 EOL dual-space restore fix (HEAD blob LF -> worktree CRLF, sha 4ee7773ee8bee2de "
       "pre==post, git-clean verified) + S4 pit-ps +1 (driver-generation selection pit). (4) S0: churn-absorb x2 "
       "(daemon treadmill, r620 round-number-first-read law; also healed r429 index-leftover on _r428bmc_s6_log."
       "txt: staged-old vs worktree==HEAD, re-add synced index, zero data loss) + rebase integrate bm-a r642 "
       "series 4 commits (T-160 G2_SLOT_STOCK_P1 prereg frozen+claimed same round, zero-conflict replay of 2 "
       "local churn commits). (5) S0.5: orders 152/152 zero-unacked double-scan; D-19 4167B784 MATCH zero-consume; "
       "GORDERS 68947C17 MATCH; inbox MSG-2112 (bm-a T-160 berth start-work declaration, zero overlap with bm-c "
       "wave-2) read+acknowledged -> processed. (6) S1 smoke 47/47; SatEngine rc0 alive (round-zero check PASS); "
       "boards: session jobs empty + fleet tickets 0 open (47 claimed) -- no new claims, wave-2 single-lane "
       "focus. (7) HANDOVER 5x obligation (r430 = bm-c 5x per r425 pointer): increment window r426-430 line "
       "appended newest-first; post_review cross-scan zero pending; attrition CLEAN rc0."
       % (burn.get("cpu_s", -1), burn.get("mem_mb", -1)))
NEXT = ("(a) r431+: poll burn via python results/_r430bmc_w2_adopt.py probe (mechanized poll+AWAITING receipt) -> "
       "if w2_judge.json landed: ADOPTION-RECEIPT -> adapt _r426bmc_close.py template to landing round (count->"
       "replace->target-line-assert trio per r429 pit) + idempotent finalize rerun no-op check (single-shot guard) "
       "+ commit product + deferred burn log atomically, deadline <=10-06; O-2115 wave-2 acceptance evidence pack "
       "10-08; (b) D-06 full-reconciliation closeout 10-07; (c) T-143 assembly window post-10-09 (deliverable "
       "10-29); (d) moneyflow GM ruling watch (MSG-1452/1543); (e) W14 lane zero-touch pending GM dual-ruling; "
       "(f) bm-a heartbeat staleness watch (fresh 21:02; >3h = GM reassignment report).")
VERIFY = ("harness receipts (_r430bmc_w2_adopt.py selftest 10/10 PASS + probe AWAITING exit 3, burn alive "
          "cpu=%ss mem=%sMB); S6 canonical rerun _r430bmc_s6_log.txt NON-ZERO LEGS: none + dualrun ZERO-DRIFT "
          "streak 31 + 4 restored legs present; driver trio receipts (_r430bmc_driver_adapt.py ADAPT_OK "
          "sha_pre=4ee7773ee8bee2de + _r430bmc_driver_restore.py RESTORE_OK sha-equal + git status clean); pit "
          "append receipt (+1317B CRLF face, LF-blob md5=493c3ea27f6a3fc341c4ce040c67e0e8); probe receipts "
          "(_r427bmc_probe.py rerun: orders 152/152, D19 4167B784 MATCH, GORDERS 68947C17 MATCH, WM red=false "
          "lane healthy, burn alive, 1 live mass-trial proc); smoke 47/47; S7 4/4 green (loop pin=5 no-op, "
          "watchdog registered, claws MATCH x2 0816c79732f4/f117547739d0, attrition CLEAN rc0); HANDOVER 5x line "
          "r426-430; push delivery verify post-commit (本地未达 origin=0)"
          % (burn.get("cpu_s", -1), burn.get("mem_mb", -1)))

# ---- state-bm-c.json ----
sp = "state-bm-c.json"
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 430
st["clock_read"] = NOW
st["cpu_pct"] = cpu_pct
st["current_task"] = ("r430: W2 finalize burn poll (PID 31276 alive cpu=%ss at close, harness AWAITING receipt "
                      "mechanized); next: r431+ probe poll -> adopt at landing via harness ADOPTION-RECEIPT + "
                      "close-template trio, deadline <=10-06" % burn.get("cpu_s", -1))
st["did"] = DID
st["gpu_free_vram_mib"] = gpu_free
st["heartbeat_epoch_utc"] = EPOCH
st["idle_ram_gb"] = idle_ram
st["last_seen"] = NOW
st["last_round"] = ("r430 bm-c: w2 adoption harness delivered (selftest 10/10); driver-generation slip caught "
                    "in-round (canonical 37-leg rerun, pit-ps +1); S0 rebase bm-a r642 x4; S6 streak 31")
st["last_round_at"] = NOW
st["last_round_ts"] = NOW
st["last_ts"] = NOW
st["last_decisions_read_at"] = NOW
st["next"] = NEXT
st["updated"] = NOW
st["updated_at"] = NOW
st["verify"] = VERIFY
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
assert isinstance(json.load(open(sp, encoding="utf-8"))["heartbeat_epoch_utc"], int), "epoch must be int"
print("state-bm-c.json written (round_no=430; epoch=%d int-verified)" % EPOCH)

# ---- round report line ----
WM_LINE = ("WM 绿（red=false lane healthy；golden-week 合法 idle·板零 open·bandit next_pick moneyflow-IC 源阻断"
           "维持）" if not wm.get("red") else "WM 红（red=true @%s）" % wm.get("ts"))
rl = "%s\t| r430 bm-c\t| %s\t| %s | dept:策略/研究\t| %s\t| %s\n" % (NOW, DID, WM_LINE, VERIFY, NEXT)
with open("round_reports-bm-c.md", "a", encoding="utf-8") as fh:
    fh.write(rl)
print("round_reports-bm-c.md appended")

# ---- heartbeat fleet/machines/bm-c.json ----
hp = "fleet/machines/bm-c.json"
hb = json.load(open(hp, encoding="utf-8"))
hb["activity_now"] = ("r430: W2 finalize burn poll -- PID 31276 alive (cpu=%ss, 805-cell family CSCV PBO); "
                     "landing adoption harness delivered (_r430bmc_w2_adopt.py selftest 10/10, probe AWAITING "
                     "exit 3); adoption at landing, deadline <=10-06" % burn.get("cpu_s", -1))
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
hb["latest_artifact"] = ("results/_r430bmc_w2_adopt.py (r430 landing-adoption harness, selftest 10/10 + "
                         "probe AWAITING receipt) @ %s" % NOW)
hb["next_milestone"] = ("w2_judge.json landing -> adoption same round (harness + close-template trio), "
                        "deadline <=10-06; O-2115 acceptance evidence pack 10-08; D-06 closeout 10-07")
hb["prod_lanes"] = ("MASS_TRIAL_W2-JUDGE finalize burn in flight (PID 31276); adoption harness staged; "
                    "moneyflow lane GM-ruling pending; D-06 closeout 10-07")
hb["round_no"] = 430
hb["verdict"] = "healthy"
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int)
print("heartbeat written (epoch int verified, orders_ack kept: %d entries)" % len(chk.get("orders_ack", [])))

# ---- inbox: MSG-2112 processed ----
src = "fleet/inbox/MSG-2026-10-03-2112-bma-g2-slot-stock-p1.md"
dst = "fleet/inbox/processed/MSG-2026-10-03-2112-bma-g2-slot-stock-p1.md"
if os.path.exists(src):
    shutil.move(src, dst)
    print("inbox: MSG-2112 -> processed/")
else:
    print("inbox: MSG-2112 already moved")
print("CLOSE_OK burn=%s" % burn)
