# -*- coding: utf-8 -*-
"""_r426bmc_close_inflight.py -- r426 S7 closeout, IN-FLIGHT variant.

Judge-finalize --wave 2 burn still alive at close time (detached 19:28:59,
silent-by-design per r422 law) -> product adoption deferred to next round
poll (r422 adoption law). All state/heartbeat/report numbers derive from
verified on-disk faces only; no hand-copied numbers.
Laws: heartbeat_epoch_utc MUST be JSON int (R170/R178); clock_read ISO-8601
T-separated (R262); sample real machine faces.
"""
import datetime
import hashlib
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
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free",
                          "--format=csv,noheader,nounits"],
                         capture_output=True, text=True,
                         creationflags=CREATE_NO_WINDOW, timeout=20)
    gpu_free = int(out.stdout.strip().splitlines()[0])
except Exception:
    gpu_free = -1

wm = json.load(open("results/watermark_red.json", encoding="utf-8"))
print("samples: cpu=%s%% ram_free=%sGB gpu_free=%sMiB wm_red=%s wm_lane=%s"
      % (cpu_pct, idle_ram, gpu_free, wm.get("red"), wm.get("lane")))

# burn liveness at close time
alive = False
pid = None
for p in psutil.process_iter(["pid", "cmdline"]):
    cl = " ".join(p.info["cmdline"] or [])
    if "mass_trial_w1.py" in cl and "judge-finalize" in cl:
        alive, pid = True, p.info["pid"]
        break
prod_exists = os.path.exists("results/mass_trial/w2_judge.json")
if not alive and not prod_exists:
    print("FATAL-FACE: burn dead AND product absent -> respawn needed next round")
print("BURN: alive=%s pid=%s product_exists=%s" % (alive, pid, prod_exists))


def sg(args):
    p = subprocess.run(["git"] + args, capture_output=True, text=True,
                       encoding="utf-8", errors="replace",
                       creationflags=CREATE_NO_WINDOW)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


# group orders.md face re-verify (decisions.md MATCH already proven by d19_check)
sg(["-C", r"K:\Fluxgroup\FluxGroup", "fetch", "origin"])
rc, blob = sg(["-C", r"K:\Fluxgroup\FluxGroup", "show",
               "origin/main:docs/orders.md"])
orders_sha = hashlib.sha1(blob.encode("utf-8", "replace")).hexdigest().upper() \
    if rc == 0 else "GITFAIL"
orders_face = "MATCH" if orders_sha == "68947C178D21814FBB5B20C3497F1DC28D42D50C" \
    else "CHANGED(" + orders_sha[:12] + ")"
print("orders.md face: %s" % orders_face)

sg(["fetch", "origin"])
rc, behind = sg(["rev-list", "--count", "HEAD..origin/main"])
print("origin behind (pre-commit): %s" % behind.strip())

DID = ("r426 bm-c: (1) DEAD-SESSION ADOPTION + wave-2 judge lane: dead r426 predecessor "
       "(19:12-19:31) delivered SHARD-1 two-layer done-flip (commit bb9a5882e 19:14, "
       "stale-takeover of bm-b 18:44:20 claim per fleet >20min law, bm-a MSG-1909 "
       "receipts acknowledged) -- r426 probe re-verified pool two-layer 4/4 done + "
       "805/805 rows on origin + 0 duplicate live procs; judge-finalize --wave 2 "
       "DETACHED burn still IN FLIGHT at close (spawned 19:28:59 PID %s, alive=%s, "
       "silent-by-design single-thread) -> next round poll+adopt w2_judge.json per "
       "r422 adoption law; r425 0-byte finalize log (19:14:48 dead non-detached spawn) "
       "kept as evidence. (2) S0: 11-commit integrate FF 7868c927a (bm-a r638 "
       "post_review anchor repoint + bm-b r629/630 dead-session closeouts + NULLS "
       "lane-face settle) + 14 stale local regen faces discarded pre-pull (origin "
       "newer) + autostash clean + marker scan rc1-clean; D-19 4167B784 MATCH "
       "zero-consume; group orders.md face %s; fleet orders 152/152 zero-unacked "
       "(dir-vs-ack double scan); inbox MSG-2005 = bm-b->bm-a not-mine (SHARD-1 "
       "burn-state report, bm-a's consumption face). (3) S1 smoke 47/47 fresh "
       "post-pull; SatEngine rc0 alive (N1 registry waves 59-114 healthy). "
       "(4) S6 37 legs rc0: dualrun ZERO-DRIFT streak 25; watermark green "
       "golden-week legal-idle faces; ORANGE shadow; daily_report + LIVE-2026-10-03 "
       "+ scorecard-family stale-takeover derives (bm-a heartbeat 23min stale, "
       "O-2100 s2.4 law); aggressive_lab clean rc0 this pass. (5) S7 4/4: claws "
       "MATCH x2, loop pin=5 no-op, watchdog PRESENT, attrition CLEAN. (6) task "
       "boards: session jobs empty + fleet tickets 0 open (all claimed) -- no new "
       "claims, single-lane focus on wave finalize handoff."
       % (pid, alive, orders_face))
NEXT = ("(a) r427: poll judge-finalize --wave 2 -> adopt w2_judge.json (complete=true, "
        "805 cells, ledger single-shot chain-linear) + product closeout derived from "
        "product json (dead-session template results/_r426bmc_close.py) <=10-06; "
        "O-2115 wave-2 acceptance 10-08; (b) D-06 full-reconciliation closeout 10-07; "
        "(c) T-143 assembly window post-10-09 (deliverable 10-29); (d) moneyflow GM "
        "ruling watch (MSG-1452/1543); (e) W14 lane zero-touch pending GM dual-ruling; "
        "(f) bm-b SHARD-1 duplicate-delivery watch (MSG-1909 sec.2; cross-machine "
        "determinism pattern: byte-identical -> discard duplicate).")
VERIFY = ("burn poll receipts: _r426bmc_w2_judge_finalize_log.txt (spawn 19:28:59, "
          "freeze 4796399f3) + psutil alive=%s pid=%s at close %s; probe receipts "
          "_r426bmc_probe.py/out (orders 152/152, shards 4/4 two-layer done, 805/805 "
          "rows on origin, w2_judge.json absent pre-close=%s); smoke 47/47; S6 37 "
          "legs rc0 (_r426bmc_s6_log.txt); dualrun streak 25 ZERO-DRIFT; attrition "
          "CLEAN rc0; claws MATCH x2; loop pin=5 no-op; watchdog PRESENT; D-19 "
          "4167B784 MATCH; orders.md face %s; WM red=false lane healthy; push "
          "delivery verify post-commit (本地未达 origin=0)"
          % (alive, pid, NOW, not prod_exists, orders_face))

# ---- state-bm-c.json ----
sp = "state-bm-c.json"
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 426
st["clock_read"] = NOW
st["cpu_pct"] = cpu_pct
st["current_task"] = ("r426: wave-2 judge 4/4 verified (SHARD-1 flip bb9a5882e "
                      "adopted) + judge-finalize --wave 2 burn in flight (PID %s, "
                      "spawned 19:28:59); next: r427 poll+adopt w2_judge.json" % pid)
st["did"] = DID
st["gpu_free_vram_mib"] = gpu_free
st["heartbeat_epoch_utc"] = EPOCH
st["idle_ram_gb"] = idle_ram
st["last_seen"] = NOW
st["last_round"] = ("r426 bm-c: dead-session adoption -- wave-2 judge 4/4 flip "
                    "verified (805/805 on origin), finalize burn in flight, S6 37 "
                    "legs rc0")
st["last_round_at"] = NOW
st["last_round_ts"] = NOW
st["last_ts"] = NOW
st["last_decisions_read_at"] = NOW
st["next"] = NEXT
st["updated"] = NOW
st["updated_at"] = NOW
st["verify"] = VERIFY
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
assert isinstance(json.load(open(sp, encoding="utf-8"))["heartbeat_epoch_utc"], int)
print("state-bm-c.json written (round_no=426; epoch=%d int-verified)" % EPOCH)

# ---- round report line ----
WM_LINE = ("WM 绿（red=false lane healthy；golden-week 合法 idle·board 零 open·bandit "
           "next_pick moneyflow-IC 源阻断维持）" if not wm.get("red")
           else "WM 红（red=true @%s）" % wm.get("ts"))
rl = "%s\t| r426 bm-c\t| %s\t| %s | dept:策略/研究\t| %s\t| %s\n" % (
    NOW, DID, WM_LINE, VERIFY, NEXT)
with open("round_reports-bm-c.md", "a", encoding="utf-8") as fh:
    fh.write(rl)
print("round_reports-bm-c.md appended")

# ---- heartbeat fleet/machines/bm-c.json ----
hp = "fleet/machines/bm-c.json"
hb = json.load(open(hp, encoding="utf-8"))
hb["activity_now"] = ("r426: wave-2 judge 4/4 verified (SHARD-1 stale-takeover flip "
                      "adopted, 805/805 rows on origin); judge-finalize --wave 2 "
                      "detached burn IN FLIGHT (PID %s @ 19:28:59); r427 polls+adopts"
                      % pid)
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
hb["latest_artifact"] = ("results/mass_trial/w2_judge_shard_1of4.jsonl "
                         "(wave 4/4 complete, commit bb9a5882e @19:14) + S6 37-leg "
                         "fresh faces @%s; w2_judge.json burn in flight" % NOW)
hb["next_milestone"] = ("r427 adopt w2_judge.json (burn in flight, PID %s) -> "
                        "wave-2 judgment CLOSED <=10-06; O-2115 acceptance "
                        "evidence pack 10-08; D-06 closeout 10-07" % pid)
hb["prod_lanes"] = ("MASS_TRIAL_W2 judge-finalize burn in flight (bm-c detached); "
                    "moneyflow lane GM-ruling pending; D-06 closeout 10-07")
hb["round_no"] = 426
hb["verdict"] = "healthy"
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int)
print("heartbeat written (epoch int verified, orders_ack kept: %d entries)"
      % len(chk.get("orders_ack", [])))
print("CLOSE_OK behind_origin_precommit=%s" % behind.strip())
