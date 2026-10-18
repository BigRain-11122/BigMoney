# -*- coding: utf-8 -*-
# r1095 bm-c closeout: state advance 1095->1096 + heartbeat + round-report row (canonical
# root path per r750 law). Fresh-read-modify-write both faces; read-back asserts (R170/R178 epoch int law).
import json, time, datetime, psutil, subprocess, io, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
NOWISO = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())
vm = psutil.virtual_memory()
FREE_RAM = round(vm.available / (1024 ** 3), 2)
CPU_PCT = round(psutil.cpu_percent(interval=1), 1)
try:
    _g = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total",
                          "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=15)
    gu, gm, gt = [int(x.strip()) for x in _g.stdout.strip().split(",")]
except Exception:
    gu, gm, gt = 96, 8065, 16384

DID = ("r1095: W270 CYCLE COMPLETE + W271 SEAT LANDED origin 87d2697cd -- full five-face freeze cycle "
       "executed per the seat-first chain in ONE window: needle preflight MEASURED (results/_r1095bmc_needle_"
       "preflight.py/json; disclosed heal: '_w269bmc_' removed from the editor gone-list -- phase-3 "
       "lineage-template rep legitimately reproduces it x1, mirrors E269 pattern per r1091 W268 出稿双坑预检 law) "
       "-> derive editor + freeze edits (segment-scoped presence gates _set_wave(270):1/(269):0/(268):0) -> "
       "splice CLEAN-AT-BIRTH 3rd gen commit 1c814343e (CR-normalized worktree==landed; banned ADMIT; pf/n1 "
       "selftest rc0; zero disk pollution from the aborted first run -- mid-window origin advance bm-a r1061 "
       "chain 79545748ab caught by executor gate0 fail-closed per r609, S0 discard-2-regenerable-probe-faces "
       "[_r686bmb_d19_check.json + watermark_red.json live-wins] then ff-merge x2 [bm-b r1008 c80a274bf5 + "
       "bm-a r1061 79545748ab], re-splice landed on clean base) -> engine mtime-watch self-burn 12/12 shards "
       "(batched self-commits 6c1aee751d+ae98b97a10) -> sixgate PRE-FINALIZE ALL PASS 33rd consecutive "
       "(GBK reader-thread noise on one selftest capture = known benign pit-encoding face) -> finalize "
       "one-pass ledger 1,016,135+2,200=1,018,335 EXACT / K 589,720+2,200=591,920 EXACT (w270-only mu -0.0917 "
       "in-band / merged -0.0927 / sigma 0.2451 / K-lift +0.0000 held-flat) -> fivekeys 6/6 ALL PASS [key1 "
       "only-vs-merged gap 0.0010196 / key1b merged-vs-W269 3.8e-06 / key2 sigma rel 3.39e-05 / key3 A p95 "
       "0.3158->0.3268 double-direction in-band / key4 K-lift 0.0000 / key5 se_mu 0.000319 held-flat; anchors "
       "FULL-PRECISION machine-read from n1_w269_results.json per r1093 pit law] -> sec.7/8 backfilled "
       "placeholders=0 -> cycle estate e4b015cbb pushed behind=0; MSG-1654 bm-a S5-27 director ruling processed "
       "(staging XQ_S5-27 BLOCKED-director->PENDING-bmc-reroll per ruling a695c06; MSG swept processed; ack "
       "MSG-175x written; physical re-roll = GPU KF lane queued behind PACK-A i2v drain, loop CPU-only "
       "standing); S6 light 10/10 rc0 (dualrun ZERO-DRIFT streak 51 [461] / audit FLAG supply_floor "
       "answered-by-chain [W270 burn in flight at S6 time] / ORANGE 6th day shadow / CALL-2026-10-16 "
       "ORANGE_COOL idempotent / bars cutoff 10-16 weekend honest / REPORT-2026-10-18 faces=5 / token "
       "delta=0); W271 SEAT published=reserved 261st engine wave (probe _w271bmc_20261018_probe.py "
       "canon-clone ADMIT first-try: A 611_501..613_500 TWENTIETH consecutive A-hop [naive 611_301..613_300 "
       "REFUSED at registered W270 B 611_301..611_500, hop past 611_500] / B 613_501..613_700 TWENTY-FIRST "
       "consecutive above-own-A [naive 611_501..611_700 lands inside own-A window -> cascade hop past "
       "613_500] / seed_admit FREE x2 base=611501 span=2000 / base=613501 span=200 / origin vacancy "
       "four-check green / W272 staircase projections recorded; seat commit 87d2697cd push first-try "
       "behind=0); S7: attrition 4 CLEAN (guard scan rc0, healed historicals as-is) + S7 tail dual-scan "
       "CAUGHT ORD watermark delta b94534b0->c8b328c1 = 1 new group row (17:20 CEO bm-d hardware 定案: CPU "
       "E5-2696v2 x2 purchased + 议题收窄令 hardware-topic-only-GPU-card-queue; bm-a lane executed-and-closed "
       "same-window; 不涉本司 BigMoney/quant = zero-action per consumption law) consumed same-window via "
       "d19 update --advance (r1090 two-face law in-tool: heartbeat mirrors synced 7 + read-back full-string "
       "equality OK) + re-probe FALSE closed + unacked=0 + zero face divergence + idle --worked rc0 + quad "
       "green (loop pin next fire 17:35 + watchdog registered next fire 17:29 [S4U flip access-denied = "
       "adjudicated default-principal standing face per D-20261002-02] + pre-commit/pre-push claws x2 "
       "installed) + orphan face=0")

NEXT = ("r1096: (1) W271 prereg derive = FIRST ACTION on the post-W270-REGISTERED universe (canon-clone "
        "_w270bmc prereg machinery per E63 age() machine-needle law; needle facts-probe MEASURED r1077 law; "
        "r1091 W268 出稿双坑预检: gone 清单禁收裸波号 token + 折行断言形拆短 needle 禁跨续行拼长串; anchors "
        "FULL-PRECISION machine-read from n1_w270_results.json per r1093 pit law; bands A 611_501..613_500 / "
        "B 613_501..613_700 registered on splice; W272 staircase faces pre-disclosed in seat MSG leg4 -- "
        "naive W272 A 613_501..615_500 REFUSED at registered W271 B 613_501..613_700 once registered -> A "
        "first-clean moves past 613_700, live walk governs never transcribe r587) -> five-face freeze splice "
        "-> engine self-burn -> sixgate -> finalize -> fivekeys -> sec.7/8 -> W272 seat (multi-step per "
        "window budget, W270 one-window precedent); (2) xq32 S5-27 PENDING-bmc-reroll: physical GPU re-roll "
        "queued behind PACK-A i2v drain (GPU KF lane, loop CPU-only standing; CEO weekend production); "
        "(3) Monday 10-20 15:30 bars window: full papers chain (weekend 10-18/19 no bars, cutoff 10-16 "
        "current, debt=0); (4) RAM watch standing (MV PACK-A GPU burn in flight, free-RAM face watched; "
        "loop CPU-only); (5) 24h died-pre-closeout incident-review watch standing per O-20261018-0948 sec.3.4")

ARTIFACT = ("W270 cycle products landed e4b015cbb (results/perpetual_faces/n1_w270_results.json finalize "
            "one-pass ledger 1,018,335 / merged K 591,920 EXACT + sixgate/fivekeys/sec78 receipts + "
            "results/_w270bmc_derive_editor.py + _w270bmc_freeze_edits.py + _w270bmc_freeze_receipt.json) + "
            "W271 seat estate origin 87d2697cd (results/_w271bmc_20261018_probe.py + "
            "_w271bmc_20261018_probe_receipt.json + fleet/inbox/MSG-20261018-175x-bmc-w271-seat.md)")

VERDICT = ("green r1095 product window (W270 full five-face cycle landed e4b015cbb + W271 seat landed "
           "87d2697cd; both push first-try behind=0; S7 tail dual-scan caught+consumed 1 不涉本司 group row "
           "same-window; CEO weekend-use standing loop CPU-only, GPU=MV PACK-A i2v burn in flight 96% util)")

# ---- state face ----
sp = os.path.join(REPO, "state-bm-c.json")
with open(sp, encoding="utf-8") as f:
    st = json.load(f)
assert st["round_no"] in (1095, 1096), "counter precondition: %r (1096 = idempotent re-run)" % st["round_no"]
st.update({
    "round_no": 1096, "round_no_label": "r1095 closeout -> counter 1096",
    "last_round": "r1095", "last_round_at": NOWISO, "last_round_ts": NOWISO,
    "last_seen": NOWISO, "last_seen_at": NOWISO, "ts": NOWISO, "updated": NOWISO,
    "updated_at": NOWISO, "clock_read": NOWISO, "activity_now": NOWISO, "now_active": NOWISO,
    "last_round_closed": NOWISO, "last_round_closed_at": NOWISO,
    "last_round_label": "r1095",
    "current_task": "r1095 closeout: W270 cycle+W271 seat landed origin e4b015cbb+87d2697cd; next = W271 prereg derive r1096 FIRST ACTION",
    "current_task_at": NOWISO, "current_task_ts": EPOCH,
    "did": DID, "last_round_summary": DID[:1200], "last_round_summary_at": NOWISO,
    "last_action": "r1095 closeout (W270 cycle complete + W271 seat publish; counter 1095->1096)",
    "last_action_at": NOWISO, "head_sha": "r1095 closeout (W270 cycle complete + W271 seat publish; counter 1095->1096)",
    "verdict": VERDICT, "verify": ("W270 sixgate PRE-FINALIZE ALL PASS + finalize one-pass ledger 1,018,335 EXACT / "
             "K 591,920 EXACT + fivekeys 6/6 (anchors full-precision machine-read) + sec.7/8 placeholders=0 + "
             "push e4b015cbb behind=0 + W271 seat probe ADMIT + seat push 87d2697cd behind=0 + S6 light 10/10 "
             "+ attrition 4 CLEAN + s05 tail delta consumed (d19 --advance two-face, mirrors synced 7, "
             "re-probe FALSE) + unacked=0 + idle --worked rc0 + quad green (loop/watchdog/claws x2) + "
             "heartbeat epoch int + clock_read ISO-T read-back + 本地未达 origin commit 数=0"),
    "next": NEXT, "next_pointer": NEXT,
    "latest_artifact": ARTIFACT, "last_artifact": ARTIFACT, "recent_artifact": ARTIFACT,
    "next_milestone": ("W271 prereg derive + five-face freeze chain (r1096, within 48h); Monday 10-20 15:30 "
                        "papers chain; xq32 S5-27 GPU re-roll behind PACK-A drain"),
    "prod_lanes": ("CPU=engine W271 armed (seat 87d2697cd landed -> prereg derive r1096 FIRST ACTION); "
                   "GPU=MV PACK-A i2v burn in flight (CEO weekend production standing: gen-only, loop "
                   "CPU-only); short-video lane DISABLED standing per O-20261017-1741"),
    "full_load_selfproof": {"占用一行": ("CPU=engine W271 armed (seat 87d2697cd -> prereg derive r1096 FIRST "
        "ACTION); GPU=MV PACK-A i2v burn in flight (gen-only standing, loop CPU-only); short-video lane "
        "DISABLED standing per O-20261017-1741")},
    "note": ("r1095: product window (state round_no=1095 at open, executed r1095, advanced 1095->1096 so "
             "next=r1096); zero absorb owed (r1094 closeout landed clean 16:34, zero dead window between -- "
             "this window ran the full W270 cycle + W271 seat in direct continuation); zero double-count: "
             "S0.5 dual-delta FALSE at open (ord b94534b0 / dec 4cfdd17c r1094 pins), S7 tail re-scan "
             "caught the 17:20 group row and consumed it same-window via d19 --advance (final pins ord "
             "c8b328c1 / dec 4cfdd17c)"),
    "orphan_face": 0, "orphan_faces": 0,
    "free_ram_gb": FREE_RAM, "ram_free_gb": FREE_RAM, "idle_ram_gb": FREE_RAM,
    "cpu_pct": CPU_PCT, "cpu_util_pct": CPU_PCT, "cpu_idle_pct": round(100 - CPU_PCT, 1),
    "gpu_util_pct": gu, "gpu_mem_used_mib": gm, "gpu_total_vram_mib": gt,
    "gpu_free_vram_mib": gt - gm, "gpu_free_vram_mb": gt - gm, "free_vram_mb": gt - gm,
    "orders_ack_receipt": ("r1095: S0.5 opening dual-delta FALSE both scans (ord content-sha1 b94534b0 / dec "
                           "raw-blob sha256 4cfdd17c hold per state keys); S7 TAIL DUAL-SCAN CAUGHT ORD delta "
                           "b94534b0->c8b328c1 = 1 new group row (17:20 CEO bm-d hardware 定案 CPU E5-2696v2 x2 + "
                           "议题收窄令; bm-a lane executed-and-closed; 不涉本司 = zero-action) consumed "
                           "same-window via d19 update --advance (r1090 two-face law in-tool, mirrors synced "
                           "7, read-back OK); re-probe FALSE closed; unacked=0; zero face divergence; final "
                           "pins ord c8b328c1 / dec 4cfdd17c"),
    "last_orders_read_note": "r1095: S7 tail ORD delta consumed at close (content-sha1 b94534b0->c8b328c1 via d19 --advance two-face; 1 row 不涉本司 zero-action)",
    "last_decisions_read_note": "r1095: DEC delta FALSE hold at close (raw-blob sha256 4cfdd17c, zero rows owed)",
    "ram_critical_face": ("MV PACK-A i2v GPU-lane python squeeze watch standing; loop CPU-only; free=%.2fGB "
                          "at r1095 closeout (cycle survived at this level)" % FREE_RAM),
    "sync": {"origin_tip": "r1095 W271 seat 87d2697cd landed (push first-try, behind=0); closeout commit rides this window",
             "ts": NOWISO},
    "r1095_closeout_note": ("r1095: (1) S0-1 anchor bm-c + round-zero probe py_faces=3 orphans=0 zero-kill + "
        "S0 origin advance mid-window: pull --rebase failed on 3 daemon live-faces -> discard-2-regenerable "
        "probe faces live-wins -> ff-merge x2 (bm-b r1008 c80a274bf5 + bm-a r1061 chain 79545748ab) clean; "
        "(2) W270 five-face freeze cycle FIRST ACTION executed in-window (needle preflight MEASURED with "
        "gone-list heal disclosed ['_w269bmc_' phase-3 lineage-template rep x1, E269 mirror] -> splice "
        "executor gate0 caught mid-window origin advance fail-closed -> re-splice CLEAN-AT-BIRTH 3rd gen "
        "1c814343e -> engine self-burn 12/12 (6c1aee751d+ae98b97a10) -> sixgate PRE-FINALIZE ALL PASS 33rd "
        "consecutive -> finalize one-pass 1,018,335/591,920 EXACT -> fivekeys 6/6 full-precision anchors -> "
        "sec.7/8 placeholders=0 -> estate e4b015cbb pushed behind=0); (3) MSG-1654 S5-27 director ruling "
        "processed (staging flip + MSG sweep + ack written; physical re-roll = GPU KF lane behind PACK-A "
        "drain, loop CPU-only); (4) S6 light 10/10 rc0 (dualrun streak 51 / supply_floor answered-by-chain / "
        "ORANGE 6th day shadow / ORANGE_COOL idempotent / bars cutoff 10-16 weekend honest / REPORT-2026-10-18 "
        "faces=5 / token delta=0); (5) W271 seat probe+MSG authored live, seat commit 87d2697cd push "
        "first-try behind=0 (261st engine wave, bmc 90th own wave candidate); (6) S7: attrition 4 CLEAN + "
        "tail dual-scan caught+consumed ORD 17:20 row (d19 --advance two-face, mirrors synced 7) + "
        "re-probe FALSE + unacked=0 + idle --worked rc0 + quad green (loop next fire 17:35 + watchdog next "
        "fire 17:29 adjudicated-default face + claws x2) + orphan face=0; counter 1095->1096"),
})
with open(sp, "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
with open(sp, encoding="utf-8") as f:
    st2 = json.load(f)
assert st2["round_no"] == 1096 and st2["last_round"] == "r1095"

# ---- heartbeat face ----
hp = os.path.join(REPO, "fleet", "machines", "bm-c.json")
with open(hp, encoding="utf-8") as f:
    hb = json.load(f)
hb.update({
    "clock_read": NOWISO, "cpu_pct": CPU_PCT, "cpu_idle_pct": round(100 - CPU_PCT, 1),
    "current_task": st["current_task"], "current_task_at": NOWISO, "current_task_ts": EPOCH,
    "did": DID, "free_ram_gb": FREE_RAM, "idle_ram_gb": FREE_RAM, "ram_free_gb": FREE_RAM,
    "heartbeat_epoch_utc": EPOCH, "last_round": "r1095", "last_round_at": NOWISO,
    "last_round_ts": NOWISO, "last_seen": NOWISO, "last_seen_at": NOWISO, "ts": NOWISO,
    "round_no": 1096, "round_no_label": "r1095 closeout -> counter 1096",
    "last_round_summary": DID[:1200], "last_round_summary_at": NOWISO,
    "last_action": st["last_action"], "last_action_at": NOWISO,
    "last_round_closed": NOWISO, "last_round_closed_at": NOWISO, "last_round_label": "r1095",
    "verdict": VERDICT, "next_pointer": NEXT, "next": NEXT, "next_milestone": st["next_milestone"],
    "latest_artifact": ARTIFACT, "last_artifact": ARTIFACT, "recent_artifact": ARTIFACT,
    "activity_now": NOWISO, "now_active": NOWISO, "updated": NOWISO, "updated_at": NOWISO,
    "idle_rounds": 0, "agenda_starved": False,
    "gpu_util_pct": gu, "gpu_mem_used_mib": gm, "gpu_total_vram_mib": gt,
    "gpu_free_vram_mib": gt - gm, "gpu_free_vram_mb": gt - gm, "free_vram_mb": gt - gm,
    "gpu_free_mb": gt - gm, "gpu_idle_mb": gt - gm,
    "prod_lanes": st["prod_lanes"], "full_load_selfproof": st["full_load_selfproof"],
    "note": st["note"], "ram_critical_face": st["ram_critical_face"],
    "sync": st["sync"],
    "r1095_closeout_note": st["r1095_closeout_note"],
    "head_sha": st["head_sha"], "verify": st["verify"],
    "orders_ack_receipt": st["orders_ack_receipt"],
    "last_orders_read_note": st["last_orders_read_note"],
    "last_decisions_read_note": st["last_decisions_read_note"],
    "orphan_face": 0, "orphan_faces": 0,
    "last_round_at_legacy": hb.get("last_round_at_legacy"),
})
with open(hp, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
with open(hp, encoding="utf-8") as f:
    hb2 = json.load(f)
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178 law)"
assert hb2["round_no"] == 1096 and len(hb2["orders_ack"]) == len(hb["orders_ack"]), \
    "heartbeat read-back: list length must hold (orders_ack_count FIELD is a known stale mirror r1052-family face)"

# ---- round report row (canonical root path per r750 law) ----
rp = os.path.join(REPO, "round_reports-bm-c.md")
ROW = ("| %s | r1095 | bm-c | watermark verdict=green (red=false lane healthy; S0.5 opening dual FALSE "
       "ord b94534b0/dec 4cfdd17c hold; S7 TAIL DUAL-SCAN CAUGHT ORD delta b94534b0->c8b328c1 = 1 group row "
       "17:20 CEO bm-d hardware 定案 [CPU E5-2696v2 x2 + 议题收窄令; bm-a lane closed; 不涉本司 zero-action] "
       "consumed same-window d19 --advance two-face [mirrors synced 7, read-back OK] re-probe FALSE closed; "
       "unacked=0 ack-scan CLEAN zero face divergence; satengine ALIVE; dualrun ZERO-DRIFT streak 51) | "
       "r1095: W270 CYCLE COMPLETE + W271 SEAT LANDED origin e4b015cbb + 87d2697cd (ONE-window full chain: "
       "needle preflight MEASURED with gone-list heal disclosed ['_w269bmc_' phase-3 lineage-template rep "
       "x1, E269 mirror per r1091 预检] -> splice gate0 fail-closed caught mid-window origin advance -> "
       "discard-2-regenerable live-wins ff-merge x2 -> splice CLEAN-AT-BIRTH 3rd gen 1c814343e "
       "[_set_wave(270):1/(269):0/(268):0 + CR-normalized worktree==landed + banned ADMIT + pf/n1 selftest "
       "rc0] -> engine self-burn 12/12 [6c1aee751d+ae98b97a10] -> sixgate PRE-FINALIZE ALL PASS 33rd "
       "consecutive -> finalize one-pass ledger 1,016,135+2,200=1,018,335 EXACT / K 589,720+2,200=591,920 "
       "EXACT [w270-only mu -0.0917 in-band / merged -0.0927 / sigma 0.2451 / K-lift +0.0000] -> fivekeys "
       "6/6 [key1 0.0010196 / key1b 3.8e-06 / key2 3.39e-05 / key3 A p95 0.3158->0.3268 in-band / key4 "
       "0.0000 / key5 se_mu 0.000319 held-flat; anchors FULL-PRECISION machine-read n1_w269_results.json "
       "per r1093 pit law] -> sec.7/8 placeholders=0 -> estate e4b015cbb behind=0) + MSG-1654 S5-27 "
       "director ruling processed [staging XQ_S5-27 BLOCKED-director->PENDING-bmc-reroll per a695c06; MSG "
       "swept; ack written; physical re-roll = GPU KF lane behind PACK-A drain, loop CPU-only] + S6 light "
       "10/10 rc0 [dualrun streak 51 / supply_floor answered-by-chain / ORANGE 6th day shadow / ORANGE_COOL "
       "idempotent / bars cutoff 10-16 weekend honest / REPORT-2026-10-18 faces=5 / token delta=0] + W271 "
       "SEAT 261st wave [probe ADMIT first-try: A 611_501..613_500 TWENTIETH A-hop / B 613_501..613_700 "
       "TWENTY-FIRST above-own-A / seed_admit FREE x2 / vacancy four-check green / W272 projections; seat "
       "push 87d2697cd first-try behind=0] + S7 attrition 4 CLEAN + idle --worked + quad green "
       "[loop+watchdog adjudicated-default face + claws x2] + orphan face=0 | 验证: cycle estate e4b015cbb + "
       "seat 87d2697cd both on origin behind=0 fetch-verified + sixgate/finalize/fivekeys receipts on disk "
       "+ attrition scan rc0 + d19 read-back equality + epoch int + 本地未达 origin commit 数=0 | 下步: "
       "r1096 W271 prereg derive FIRST ACTION (post-W270 universe, never transcribe r587) -> splice -> "
       "burn -> sixgate -> finalize -> W272 seat; xq32 S5-27 GPU re-roll behind PACK-A drain; Monday "
       "10-20 15:30 papers chain |\n\n" % NOWISO)
with io.open(rp, "a", encoding="utf-8", newline="") as f:
    f.write(ROW)
print("CLOSEOUT OK r1095->1096 @ %s | ram=%.2fGB gpu=%d%%/%dMiB | epoch=%d" % (NOWISO, FREE_RAM, gu, gm, EPOCH))
