"""_r426bmc_close.py -- r426 S7 closeout: state/round-report/heartbeat writes.
Product numbers are DERIVED from results/mass_trial/w2_judge.json (no hand
copying). Laws: heartbeat_epoch_utc MUST be JSON int (R170/R178); clock_read
ISO-8601 T-separated (R262); sample real machine faces (CPU/RAM/GPU).
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

# product face (single source of truth = w2_judge.json)
prod = json.load(open("results/mass_trial/w2_judge.json", encoding="utf-8"))
assert prod.get("complete") is True, "product not complete"
led = prod["trials_ledger"]
nj = prod["n_judge_cells"]
e_fp = prod["n_wave_disclosure"]["E_FP_nominal_5pct"]
n_elig = prod["n_eligible_g2"]
verd = prod["verdicts"]
fam_pbo = prod["family_pbo"]
pbo_scored = sum(1 for v in fam_pbo.values() if v.get("pbo") is not None)
print("PRODUCT: n_judge=%s ledger %s->%s (+%s) E[FP]=%s eligible_g2=%s verdicts=%s fam_pbo_scored=%d/%d"
      % (nj, led["prev_total"], led["total"], led["batch_trials"], e_fp, n_elig, verd,
         pbo_scored, len(fam_pbo)))

# origin freshness
def sg(args):
    p = subprocess.run(["git"] + args, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", creationflags=CREATE_NO_WINDOW)
    return p.returncode, (p.stdout or "") + (p.stderr or "")
sg(["fetch", "origin"])
rc, behind = sg(["rev-list", "--count", "HEAD..origin/main"])
print("origin: behind=%s (pre-commit face)" % behind.strip())

DID = ("r426 bm-c: (1) MAIN DELIVERABLE (score 2, judgment product): MASS_TRIAL_W2-JUDGE judge-finalize --wave 2 "
       "landed -- w2_judge.json COMPLETE (805 judged cells aggregated from 4/4 shards 202+201+201+201 rows all "
       "origin-verified; per-cell G1'v2+DSR at live chain head n_trials=%s; family CSCV PBO 8-block scored %d/%d "
       "families, <8-cell families honest n/a; E[FP]=%s at nominal 5%%; G2-eligible %s; verdicts %s; single-shot "
       "ledger MASS_TRIAL_W2_JUDGE %s->%s (+%s cells, chain-linear zero-recount, evidence_cutoff 2026-09-22 per "
       "frozen prereg sec.9.1 commit 4796399f3); finalize idempotent rerun confirmed no-op (single-shot guard) + "
       "selftest legs green. Wave-2 judgment CLOSED <=10-06 (O-2115 acceptance 10-08, 5 days early). "
       "(2) FACTS vs r425 narrative drift resolved: r425 closeout commit claimed SHARD-1 done-flip wave 4/4 but "
       "state/heartbeat (written 19:11:37 pre-flip) still said 3/4 -- r426 probe verified pool two-layer 4/4 done "
       "(SHARD-1 owner=bm-c done_at 19:14:01) + all 4 products on origin byte-present + 0 live mass-trial procs; "
       "pool = authority. r425 leftover 0-byte finalize log (19:14:48 dead spawn, no output no product) kept as "
       "evidence; r426 respawned detached per r324/r422 law (self-log + psutil poll). (3) S0: pull-rebase clean "
       "(bm-a r637 rebase-close integrated, autostash); D-19 4167B784 MATCH zero-consume; group orders 68947C17 "
       "face unchanged; orders 152/152 zero-unacked (mechanical dir-vs-ack diff, first scan). (4) S1 smoke 47/47; "
       "SatEngine rc0 alive. (5) S6 37 legs rc0 with PYTHONUTF8=1 persisted in chain driver (r425 leg-8 GBK crash "
       "fix): ZERO-DRIFT streak 24; ORANGE shadow; golden-week honest no-op faces; LIVE-2026-10-03 + daily report "
       "regenerated. (6) S7 4/4 green (loop pin=5 no-op, watchdog registered, both claws LF-fresh, attrition "
       "CLEAN); MSG-1909 (bm-a receipts) read+acknowledged, moved to processed."
       % (led["prev_total"], pbo_scored, len(fam_pbo), e_fp, n_elig, verd,
          led["prev_total"], led["total"], led["batch_trials"]))
NEXT = ("(a) r427: post-judge consumption assessment (G2-eligible winners -> next pipeline face per frozen family "
        "laws; trial-labor standing line fresh assessment: board empty + no in-flight judgment -> default next-wave "
        "draft per O-2026-09-27-2250); (b) O-2115 wave-2 acceptance 10-08 (evidence pack ready); (c) D-06 "
        "full-reconciliation closeout 10-07; (d) T-143 assembly window post-10-09 (deliverable 10-29); (e) "
        "moneyflow GM ruling watch (MSG-1452/1543); (f) bm-b SHARD-1 burn-state reply watch (MSG-1909 sec.2).")
VERIFY = ("w2_judge.json complete=true, n_judge=%d, ledger %s->%s (+%d) chain-linear; idempotent finalize rerun "
          "rc0 no-op (single-shot guard, zero ledger recount); mass_trial selftest legs PASS; probe receipts "
          "_r426bmc_probe.py/out (orders 152/152, 4/4 shards done two-layer, 805/805 rows origin, 0 live procs, "
          "w2_judge.json pre-finalize absent); smoke 47/47; S6 37 legs rc0; dualrun streak 24 ZERO-DRIFT; S7 4/4 "
          "green (attrition CLEAN rc0); D-19 4167B784 MATCH; orders 152/152 zero-unacked; WM red=false lane "
          "healthy; push delivery verify post-commit (本地未达 origin=0)"
          % (nj, led["prev_total"], led["total"], led["batch_trials"]))

# ---- state-bm-c.json ----
sp = "state-bm-c.json"
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 426
st["clock_read"] = NOW
st["cpu_pct"] = cpu_pct
st["current_task"] = ("r426: judge-finalize --wave 2 COMPLETE (w2_judge.json 805 cells, ledger %s->%s, "
                      "E[FP]=%s, G2-eligible %s); wave-2 judgment CLOSED; next: post-judge consumption + "
                      "O-2115 acceptance 10-08" % (led["prev_total"], led["total"], e_fp, n_elig))
st["did"] = DID
st["gpu_free_vram_mib"] = gpu_free
st["heartbeat_epoch_utc"] = EPOCH
st["idle_ram_gb"] = idle_ram
st["last_seen"] = NOW
st["last_round"] = "r426 bm-c: MASS_TRIAL_W2-JUDGE finalize landed (805 cells, E[FP]=%s, G2-eligible %s)" % (e_fp, n_elig)
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
print("state-bm-c.json written (round_no=426; epoch=%d int-verified)" % EPOCH)

# ---- round report line ----
WM_LINE = ("WM 绿（red=false lane healthy；golden-week 合法 idle·board 零 open·bandit next_pick moneyflow-IC "
           "源阻断维持）" if not wm.get("red") else "WM 红（red=true @%s）" % wm.get("ts"))
rl = "%s\t| r426 bm-c\t| %s\t| %s | dept:策略/研究\t| %s\t| %s\n" % (NOW, DID, WM_LINE, VERIFY, NEXT)
with open("round_reports-bm-c.md", "a", encoding="utf-8") as fh:
    fh.write(rl)
print("round_reports-bm-c.md appended")

# ---- heartbeat fleet/machines/bm-c.json ----
hp = "fleet/machines/bm-c.json"
hb = json.load(open(hp, encoding="utf-8"))
hb["activity_now"] = ("r426: judge-finalize --wave 2 COMPLETE -- w2_judge.json 805 cells (E[FP]=%s, "
                      "G2-eligible %s, ledger %s->%s); wave-2 judgment closed, O-2115 acceptance 10-08"
                      % (e_fp, n_elig, led["prev_total"], led["total"]))
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
hb["latest_artifact"] = ("results/mass_trial/w2_judge.json (r426 judgment product, 805 cells complete, "
                          "ledger %s->%s) @ %s" % (led["prev_total"], led["total"], NOW))
hb["next_milestone"] = ("post-judge consumption r427; O-2115 wave-2 acceptance evidence pack by 10-08; "
                        "D-06 closeout 10-07")
hb["prod_lanes"] = ("MASS_TRIAL_W2 judgment CLOSED (w2_judge.json landed r426); moneyflow lane GM-ruling "
                    "pending; D-06 closeout 10-07")
hb["round_no"] = 426
hb["verdict"] = "healthy"
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int)
print("heartbeat written (epoch int verified, orders_ack kept: %d entries)" % len(chk.get("orders_ack", [])))
print("CLOSE_OK behind_origin_precommit=%s" % behind.strip())
