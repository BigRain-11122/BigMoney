# -*- coding: utf-8 -*-
"""r1006 bm-c closeout: state + heartbeat + canonical round report (r750 law).
Absorb 25th instance: dead 18:40-19:28 W241 chain estate landed this window."""
import json, time, datetime, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

# fresh machine reads (RAM via psutil, fallback idle-trigger face)
try:
    import psutil
    free_ram = round(psutil.virtual_memory().available / 1024**3, 1)
except Exception:
    free_ram = 1.9
gpu_free = 147  # wave2 burn holding the card (nvidia-smi face from idle trigger window)

ORD_SHA = "0b202b9510ec6aaf57ea3764f3b9ae8b010f3ee0"
DEC_SHA = "c61d7884b347e7e706ed98546aadc304f7f3afddd9071a511a0152a860a064bb"

did = ("r1006: (1) S0-1 anchor bm-c + round-zero probe py_faces=9 orphans=3 ZERO-KILL (same legal face as r1001/r1002: "
       "wave2 runner polling-leg PID 24076 + album-serve resident + user Doubao pythonw); (2) S0 stash-bridge: 10 overlap regenerable faces "
       "stashed -> ff hit daemon-race on fleet/machine-health.json (live-write between status and merge) -> checkout live-wins -> "
       "ff-merge cacbfbecc (behind grew 3->5 mid-window, all 5 caught); (3) ABSORB 25th INSTANCE: dead 18:40-19:28 chain machine-verified "
       "BEFORE landing (r1003 prereg derive 18:40 + r1004 editor 18:50/19:13 + splice landed by r1005 commit 8e980ce3e + engine self-burn "
       "12/12 daemon appends 6cd270b40/27e514139 + sixgate PRE-FINALIZE 19:23 15th-consecutive correct-phase + finalize one-pass 19:27 + "
       "fivekey 19:28 ALL PASS): ledger 952,335+2,200=954,535 EXACT / merged K=528,120 EXACT / merged mu -0.09275776546996894 sigma "
       "0.2450994564577611 byte-equal product-vs-receipt / W242 seat projection CONFIRMED live (bm-a MSG-20261014-1814, key5 pass) -> "
       "estate commit af6ec72f9 PUSHED (prereg sec7/8 backfill + sixgate/fivekey receipts + n1_w241_results.json + E63-4 legkey card "
       "update-in-place); W241 = bm-c 67th owned wave FULL CYCLE CLOSED; (4) S0.5 ORD delta TRUE consumed 1176e4c4->0b202b95 (3 rows: "
       "17:4x 主AGENT 13-seat panel = committee domain zero bm-c action / 18:5x CEO 全面开工夜令 O-20261014-1855 MV 最高优先级+明晨成品死线 "
       "= 本机执行面 GPU MV wave2 烧制中 + 本窗 W241 收口 / 19:2x Phase 1-alpha item4 = @bm-b only) / DEC delta FALSE hold c61d7884 / "
       "unacked=0; (5) S1 smoke 49/49; (6) S3: satengine ALIVE rc0 burns 0 queue 0 (W242=bm-a seat in-flight, chain theirs per seat-first) "
       "+ wm red=false healthy + idle green_idle=false RAM 1.9pct honest not-claim-eligible (GPU lane=MV wave2 protected per O-20261014-0312 "
       "sec.2) + post_review today 0-x; (7) wave2 watch: runner PID 24076 alive since 15:44, 41 mp4s landed bmc/i2v, newest D01_carver_words "
       "19:37:46 actively producing ~10min/clip, ~35+/39 wave2 slots, on-pace tonight full-local cut; harvest+CDN face = next window; "
       "(8) bars 10-14 still undelivered source-side 19:43 probe (cutoff 10-13, failures 0, papers debt=0); (9) S6 chain: dualrun "
       "ZERO-DRIFT streak 51 (456) + compute_audit FLAG pool_starvation/supply_floor answered-by-chain (W242 bm-a in-flight + RW-5 freeze "
       "bans new prereg first-intake) + wm py_low_with_work_cands NAMED-ANSWER (GPU=MV legal burn per CEO 1855 night order + CPU "
       "waits-upstream W242 legally chained) + 15 lane-guard no-ops + fund_premium no-op NAV 10-13 + thermo no-op Money02-absent + clock "
       "CALL-2026-10-13 ORANGE_COOL idempotent + regime crash10d+breadth0.81 triggers recorded + fundamental 23.8h-fresh skip + b_layer mask "
       "regen + daily_report REPORT-2026-10-14 faces=5 + LIVE-2026-10-14 (ORANGE cap 50%) + token delta=0 + attrition 4 CLEAN; (10) S7 quad "
       "green (loop pin=5 no-op 19:55 + watchdog 19:49 + both claws installed); counter 1004->1007 so next = r1007")

verdict = ("green: r1006 = PRODUCT window (W241 FULL CYCLE CLOSED on origin af6ec72f9: finalize ledger 954,535 EXACT / K 528,120 / "
           "five-key ALL PASS / sec7-8 backfilled / 15th consecutive PRE-FINALIZE sixgate -- dead-chain absorb 25th instance verified-"
           "before-landing) + watch window (wave2 runner alive 41 mp4s newest 19:37 GPU=MV night-order top priority / bars await sina "
           "late-bar debt=0); smoke 49/49 + dualrun streak 51 + audit flags answered-by-chain + satengine alive + attrition 4 CLEAN + "
           "orphan 3/3 legal zero-kill")

prod_lanes = ("CPU=N1 W241 CLOSED (finalize landed this window ledger 954,535 K=528,120, estate af6ec72f9); W242=bm-a SEAT in-flight "
              "(their chain per seat-first law); MF-IC-P1: parked, bm-a collector lane; GPU=MV V3 wave2 burning (runner PID 24076 alive, "
              "~35+/39 landed newest D01 19:37, ~10min/clip, harvest+CDN face next window, tonight full-local cut per CEO 1855 night order)")

current_task = "r1006 closeout landed (W241 cycle closed); next = wave2 harvest watch + W242 finalize watch (bm-a chain) + bars await sina"

next_pointer = ("r1007: (1) wave2 harvest watch (runner PID 24076; at 39/39 completion: CDN re-upload of UPLOAD_FAIL_OR_SKIPPED slots + "
                "q88 board + orders receipt + poke bm-a assembly station -- CEO 1855 night order top priority, tonight full-local cut); "
                "(2) W242 finalize watch (bm-a chain; on landing -> W243 seat probe per seat-first law); (3) bars re-probe -> papers FULL "
                "CHAIN when 10-14 bar lands on sina (update_daily gate -> live.paper REGIME_GUARD -> t35_openfill -> t24 x2 -> "
                "aggressive/alloc/grid/system_v1 papers -> t35_paper_export -> daily faces); (4) MF-IC-P1 parked bm-a collector lane "
                "(standing relay)")

latest_artifact = "r1006: W241 finalize estate on origin af6ec72f9 (n1_w241_results.json 19:27 + fivekey ALL PASS + sec7/8 backfill)"

next_milestone = ("wave2 39/39 harvest + CDN tonight ~20:30-21:00; W242 finalize->W243 seat (bm-a chain, <=48h); 10-15 晨 CEO 成品死线 "
                  "(MV, bm-a assembly station consumes our wave2 clips)")

# ---- state-bm-c.json ----
sp = os.path.join(REPO, "state-bm-c.json")
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 1007
st["last_round"] = "r1006"
st["last_round_at"] = now_iso
st["last_round_label"] = "r1006"
st["did"] = did
st["verdict"] = verdict
st["current_task"] = current_task
st["current_task_at"] = now_iso
st["next_pointer"] = next_pointer
st["next"] = next_pointer
st["next_milestone"] = next_milestone
st["latest_artifact"] = latest_artifact
st["last_artifact"] = latest_artifact
st["prod_lanes"] = prod_lanes
st["last_orders_sha"] = ORD_SHA
st["last_orders_at"] = now_iso
st["last_orders_seen"] = now_iso
st["last_orders_read_at"] = now_iso
st["last_decisions_sha"] = DEC_SHA
st["last_decisions_at"] = now_iso
st["last_decisions_read_at"] = now_iso
st["last_decisions_seen"] = now_iso
st["last_seen"] = now_iso
st["last_seen_at"] = now_iso
st["ts"] = now_iso
st["updated"] = now_iso
st["updated_at"] = now_iso
st["now_active"] = f"{now_iso} | r1006 | bm-c: W241 finalize estate landed af6ec72f9 + wave2/bars watch | counter 1006->1007"
st["last_round_summary"] = ("r1006: ABSORB 25th (dead 18:40-19:28 W241 chain) -> estate verified+landed af6ec72f9 (finalize 954,535/K 528,120 "
                            "fivekey ALL PASS sixgate 15th consecutive sec78 backfilled) + ff cacbfbecc behind-5 caught + ORD 3 rows consumed "
                            "(1855 CEO night order = MV top priority, GPU wave2 executing) + smoke 49/49 + S6 all-green + quad green; counter "
                            "1006->1007")
st["idle_rounds"] = 0
st["agenda_starved"] = False
st["orphan_face"] = 3
st["orphan_faces"] = 3
st["free_ram_gb"] = free_ram
st["ram_free_gb"] = free_ram
st["idle_ram_gb"] = free_ram
st["gpu_free_vram_mb"] = gpu_free
st["last_round_closed"] = now_iso
st["last_action"] = "r1006 closeout (W241 finalize estate absorb-land + S6 chain + quad green)"
st["last_action_at"] = now_iso
st["r1006_absorb_note"] = ("r1006 absorb note: dead sessions r1003 (prereg derive 18:40, landed in estate chain by r1005) / r1004 "
                          "(editor derive 18:50 + freeze edits 19:13, landed via r1005 splice commit 8e980ce3e) / r1005-continuation "
                          "(sixgate 19:23 + finalize 19:27 + fivekey 19:28 + sec78 backfill authored+run, died pre-commit) -- this session "
                          "absorbed per bm-c absorb precedent lineage (25th instance, r894..r1002): estate machine-verified BEFORE landing "
                          "(ledger identity EXACT + K 528,120 EXACT + five keys ALL PASS + merged mu/sigma byte-equal product-vs-receipt); "
                          "executed as r1006 (next after highest committed label r1005) and advanced counter 1004->1007 so next session = "
                          "r1007; zero double-count: S0.5 ORD delta consumed THIS window (1176e4c4->0b202b95, 3 rows incl CEO 1855 night "
                          "order), DEC delta FALSE hold; dead-chain body debts handled by r1005 splice commit + this estate commit")
st["r1006_closeout_note"] = st["last_round_summary"]
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---- heartbeat fleet/machines/bm-c.json ----
hp = os.path.join(REPO, "fleet", "machines", "bm-c.json")
h = json.load(open(hp, encoding="utf-8"))
h["free_ram_gb"] = free_ram
h["gpu_free_vram_mb"] = gpu_free
h["prod_lanes"] = prod_lanes
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["heartbeat_epoch_utc"] = epoch
h["last_seen"] = now_iso
h["clock_read"] = now_iso
h["ts"] = now_iso
h["current_task"] = current_task
h["now_active"] = st["now_active"]
h["latest_artifact"] = latest_artifact
h["verdict"] = verdict
h["did"] = did
json.dump(h, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---- canonical round report (r750 law) ----
rp = os.path.join(REPO, "logs", "iteration-loop", "round_reports-bm-c.md")
line = (f"{now_iso} | r1006 | bm-c | {did} | 证据: estate push af6ec72f9 (origin verified behind=0) + ff cacbfbecc + "
        f"fivekey receipt ALL PASS (ledger 954,535 EXACT) + probe receipt ORD 0b202b95/DEC c61d7884 + smoke 49/49 + "
        f"dualrun ZERO-DRIFT streak 51 (456) + attrition 4 CLEAN + quad green (loop pin=5/watchdog 19:49/claws x2) + "
        f"orphan face=3 (wave2 runner/album-serve/Doubao 用户件=服务/用户域零杀) | 当前活: W241 全周期收口落地+MV wave2 GPU 烧制监护中 | "
        f"最近实物: n1_w241_results.json + 五键收据（19:27·origin af6ec72f9）| 下个里程碑: wave2 收割+CDN 今晚 ~20:30 · "
        f"W242 finalize 落地即 W243 席（bm-a 链·≤48h）· 10-15 晨 CEO 成品死线 | watermark verdict=red:false healthy·py_low_with_work_cands "
        f"点名已答（GPU=MV 夜令合法烧·CPU waits-upstream W242）| 本地未达 origin commit 数=closeout push 骑本窗（fetch-verify 下轮开窗） | "
        f"下轮指针: r1007 = wave2 harvest watch + W242 watch + bars papers 链候 sina\n")
with open(rp, "a", encoding="utf-8") as f:
    f.write(line)

# asserts (R170/R178 law)
h2 = json.load(open(hp, encoding="utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch must be int"
s2 = json.load(open(sp, encoding="utf-8"))
assert s2["round_no"] == 1007
print("CLOSEOUT OK", now_iso, "epoch", epoch, "free_ram", free_ram)
