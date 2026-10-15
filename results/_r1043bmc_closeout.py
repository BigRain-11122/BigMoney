# -*- coding: utf-8 -*-
# r1043 bm-c closeout: state + heartbeat + round-report row (canon clone pattern).
import io
import json
import os
import time
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())

ABSORB = ("r1043 absorb note: dead-session chain r1037..r1042 (SIX sessions after r1036 closeout 22:39) "
          "each ran full/partial bodies with commits+pushes (r1037: W249 seat publish 8949e0aef + xq T1 push "
          "verify/poke + S6 43/43 23:03-23:05; r1038: S6 43/43 00:38-00:42 + xq seareview tier1 map/digest; "
          "r1039: d19 facts/rows ORD d24c2750->33ea18b5 (11 rows judged) + DEC ab3f0cc9->ec6b9164 (4 rows "
          "judged) zero bm-c action + orphan probes; r1040: W249 prereg author 04:04:22 (uncommitted, landed "
          "by r1041); r1041: W249 prereg freeze LANDED 4103f0d5d + D-20261016-01(2)/02 bm-c legs (git_claw "
          "fourth owner channel + memory-budget-gate comment sync) 20a29f8ba; r1042: W249 five-face splice "
          "LANDED 5d4aeec59 + engine self-burn 12/12 self-commits 2d0b41383/f528ab7ab/dfbb4afa2 + xq "
          "seareview payload) -- ALL died pre-closeout (state frozen at round_no=1037, heartbeat stale at "
          "r1036/22:39); this session executed as r1043 (next after highest committed label r1042) per bm-c "
          "absorb precedent lineage (r894..r1035, 37th instance) and advanced counter 1037->1044 so next "
          "session = r1044; zero double-count: S0.5 dual-delta FALSE both scans this window (watermarks ORD "
          "f321f54a / DEC ec6b9164 already advanced by dead sessions at 05:05, probe-verified fresh), "
          "dead-session debts handled by their own commits + this closeout landing the W249 cycle completion")

DID = ("r1043 bm-c: (1) S0-1 anchor bm-c + round-zero probe py_faces=7 orphans=2 zero-kill; (2) ABSORB 37th gen "
       "(see absorb note); (3) P0 PRODUCT = W249 cycle COMPLETE this window correct-phase: sixgate PRE-FINALIZE "
       "ALL PASS (_r1043bmc_w249_sixgate.json, dual-sha16 pf 487b9fb3d98aa09e / n1 ee694186ffc6ee97, "
       "bands==freeze receipt, banned rc0, pf+n1 selftest, shards 12/12, W248 boundary 561501/544701 kept) -> "
       "finalize one-pass ledger 969,935+2,200=972,135 EXACT / merged K=545,720 (543,520+2,200) / w249-only mu "
       "-0.08793 sigma 0.24233 / merged mu -0.09277 sigma 0.24503 / K-lift 0.0000 in-band / audit machine=bm-c "
       "finalize_only=true -> fivekeys ALL PASS (_r1043bmc_w249_fivekeys.json: key1 0.00485<0.02, key1b 0.00002, "
       "key2 sigma rel -0.0045pct, key3 p95 0.3158 vs 0.3154 +0.0004, key4 0.0, key5 se_mu 0.000332 equal-chain) "
       "-> sec.7/8 backfilled (backfill-limited law, needle-count asserts 1/1); (4) W250 SEAT published queue-head "
       "(probe _w250bmc_20261016 rc0 ADMIT: A 565_501..567_500 hops=0 13th seed-gap / B 545_101..545_300 hops=0 / "
       "seed gates FREE both / origin vacancy 4-check / no-skip W251/W252; W251+ proj: A 567_501..569_500 CLEAN / "
       "B naive 545_301..545_500 REFUSED seed 545_500 + W240..W249 A-ladder -> 565_501..565_700 hops=11, live "
       "re-derive governs); W249 seat MSG swept processed; (5) S0.5 dual-delta FALSE both scans + unacked=0; "
       "(6) smoke 49/49; (7) S6 43/43 rc0 idempotent sweep (bars 10-15 consumed, 10-16 not due till 15:30, t35 "
       "PASS zero-pending, token delta=0); (8) W20 CPU lane: shard-0 autofill DONE rc0 05:47-05:51 + shard-3 "
       "claimed 06:02 burning + shards 1/2 ready RAM 26.4pct free; (9) S7 quad green + attrition 4 CLEAN; "
       "counter 1037->1044")

NEXT = ("r1044: (1) W250 prereg derive = FIRST ACTION (seat-first law, machine-SUB from frozen W249 template, "
        "key-anchored to W249 actuals ledger 972,135 / K=545,720); (2) W250 five-face freeze splice after prereg "
        "(engine mtime-watch self-burn follows); (3) xq T1 seareview lane watch (tier1 map + payload landed by "
        "dead sessions, bm-a consumption); (4) bars 10-16 window 15:30 (papers debt=0); (5) W20 shards 1/2 "
        "autofill watch; (6) ORD/DEC tail re-scan")

VERDICT = ("green: r1043 = ABSORB 37th (dead r1037..r1042 estate verified + W249 cycle completed THIS window "
           "correct-phase: sixgate->finalize 972,135 EXACT/K=545,720->fivekeys ALL PASS->backfill) + W250 seat "
           "published (ADMIT A 565_501..567_500 / B 545_101..545_300) + S6 43/43 + smoke 49/49 + S7 quad green")

PROD = ("CPU=W20 SCREEN shard-3 RUNNING (autofill claimed 06:02) + shard-0 DONE rc0 05:51 + shards 1/2 ready "
        "(RAM 26.4pct free un-park window) ; GPU=xq T1 wave-1 harvest landed (seareview payload r1042 estate) + "
        "VRAM 14.54G free ; N1=W249 COMPLETE (ledger 972,135 / K=545,720) + W250 seat OPEN (A 565_501..567_500 / "
        "B 545_101..545_300) -> prereg derive r1044 first action ; SPAWN-GATE=codely cap2 live")

ARTIFACT = ("results/perpetual_faces/n1_w249_results.json (finalize 06-16 05:5x, ledger 972,135, K=545,720, "
            "fivekeys ALL PASS) + _w250bmc_20261016_probe_receipt.json (W250 seat ADMIT) + commit cc06f1f4a "
            "pushed origin")

CLOSE = ("r1043: 37th-gen absorb + W249 full cycle COMPLETE (sixgate PRE-FINALIZE first correct-phase -> "
         "finalize 972,135 EXACT / K=545,720 -> fivekeys ALL PASS -> sec.7/8 backfilled) + W250 seat published + "
         "W20 shard-0 done + S6 43/43 + smoke 49/49 + S7 quad green + attrition 4 CLEAN | " + NOW)

SELFPROOF = {
    "占用一行": PROD,
    "当前活": "r1043 closeout (W249 cycle complete + W250 seat published)",
    "最近实物": ARTIFACT,
    "下个交付物": "W250 prereg derive (r1044 首动作·seat-first) + splice+burn+finalize 链 + bars 10-16 15:30 窗",
    "队列水位": "池 ready=W20 shards 1/2 (RAM un-park window)·N1 W250 seat queued·P2/P3 空·jobs 0",
}

ROW = (NOW + " | r1043 | bm-c | ABSORB 37th gen (dead r1037..r1042: W249 seat 8949e0aef + prereg 4103f0d5d + "
       "splice 5d4aeec59 + engine self-burn 12/12 self-commits + S6 chains 23:03/00:38 + d19 consumption + "
       "seareview payload -- all pre-closeout deaths, state frozen 1037) + P0 PRODUCT = W249 cycle COMPLETE "
       "correct-phase THIS window: sixgate PRE-FINALIZE ALL PASS (dual-sha16 pf 487b9fb3d98aa09e / n1 "
       "ee694186ffc6ee97, shards 12/12, W248 boundary kept) -> finalize one-pass ledger 969,935+2,200=972,135 "
       "EXACT / K=545,720 / w249-only mu -0.08793 / K-lift 0.0000 in-band -> fivekeys ALL PASS (key1 0.00485 / "
       "key2 -0.0045pct / key3 +0.0004 / key4 0.0 / key5 0.000332 equal) -> sec.7/8 backfilled | W250 SEAT "
       "published (probe ADMIT: A 565_501..567_500 hops=0 13th seed-gap / B 545_101..545_300 hops=0, gates "
       "FREE, vacancy 4-check, no-skip W251/W252; W251+ proj B-refusal face disclosed: seed 545_500 + "
       "W240..W249 A-ladder -> hops=11, live re-derive governs) | W249 seat MSG swept processed | S0.5 "
       "dual-delta FALSE both scans (dead-session watermarks ORD f321f54a/DEC ec6b9164 verified, unacked=0) | "
       "smoke 49/49 | S6 43/43 rc0 (idempotent sweep, bars 10-16 not due, t35 PASS zero-pending, token delta=0) "
       "| W20 CPU lane: shard-0 autofill DONE rc0 05:51 + shard-3 claimed 06:02 + shards 1/2 ready RAM 26.4% | "
       "S7 quad green (loop pin=5 no-op, watchdog S4U-flip denied=adjudicated face, claws x2 installed) + "
       "attrition 4 CLEAN | watermark verdict GREEN (red=false, healthy lane, W250 seat open = supply face) | "
       "orphan_face=2 zero-kill | local-ahead-of-origin=0 (push landed dfbb4afa2..cc06f1f4a fetch-verified) | "
       "next r1044: W250 prereg derive FIRST ACTION (seat-first law, machine-SUB from W249 actuals ledger "
       "972,135/K=545,720) + splice window + W20 autofill watch + bars 10-16 15:30 recheck")


def atomic_write(path, text):
    tmp = path + ".tmp_r1043"
    with io.open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    os.replace(tmp, path)


# --- state-bm-c.json + heartbeat (mirrored content) ---
sp = os.path.join(ROOT, "state-bm-c.json")
d = json.load(io.open(sp, encoding="utf-8"))
d["round_no"] = 1044
d["round_no_label"] = "r1043"
d["last_round"] = "r1043"
d["last_round_label"] = "r1043"
for k in ("clock_read", "ts", "updated", "updated_at", "last_seen", "last_seen_at",
          "now_active", "activity_now", "last_round_at", "last_round_ts",
          "last_round_closed", "last_round_summary_at", "last_ts", "last_action_at",
          "current_task_at"):
    d[k] = NOW
d["current_task"] = "r1043 closeout (W249 cycle complete + W250 seat published)"
d["current_task_ts"] = EPOCH
d["heartbeat_epoch_utc"] = EPOCH
d["heartbeat_epoch_utc_type"] = "int (assert)"
d["did"] = DID
d["note"] = ("r1043: W249 cycle COMPLETE (finalize 972,135/K=545,720 fivekeys PASS) | W250 seat published "
             "(A 565_501..567_500 / B 545_101..545_300 ADMIT) | prereg derive = r1044 first action")
d["last_round_summary"] = ("r1043: absorb 37th gen + W249 cycle COMPLETE (sixgate->finalize 972,135/K=545,720->"
                          "fivekeys ALL PASS->backfill) + W250 seat published + S6 43/43 + smoke 49/49 + S7 quad green")
d["last_action"] = "r1043 closeout (W249 cycle + W250 seat, same-window)"
d["verdict"] = VERDICT
d["next"] = NEXT
d["next_pointer"] = NEXT
d["next_milestone"] = "r1044+: W250 prereg derive + splice+burn+finalize chain + bars 10-16 15:30 window + W20 autofill"
d["latest_artifact"] = ARTIFACT
d["last_artifact"] = ARTIFACT
d["recent_artifact"] = ARTIFACT
d["prod_lanes"] = PROD
d["full_load_selfproof"] = SELFPROOF
d["r1043_absorb_note"] = ABSORB
d["r1043_closeout_note"] = CLOSE
d["head_sha"] = "cc06f1f4a (r1043; origin/main same, push landed dfbb4afa2..cc06f1f4a)"
d["sync"] = {"origin_tip": "cc06f1f4a (r1043 estate push landed first-try clean, no hot-window race this window)",
             "ts": NOW, "ahead_behind": "local-ahead-0 (push + fetch verified)"}
d["last_pulled_at"] = NOW
d["cpu_pct"] = "8"
d["cpu_util_pct"] = "8"
d["cpu_idle_pct"] = 92.0
d["free_ram_gb"] = 6.8
d["ram_free_gb"] = 6.8
d["idle_ram_gb"] = 6.8
d["gpu_free_vram_gb"] = 14.54
d["gpu_free_vram_mib"] = 14890
d["gpu_free_vram_mb"] = 14890
d["gpu_vram_free_mb"] = 14890
d["free_vram_mb"] = 14890
d["orphan_face"] = 2
d["orphan_faces"] = 2
d["idle_rounds"] = 0
d["agenda_starved"] = False
d["codely_live_count"] = 1
d["verify"] = ("receipts: sixgate ALL PASS _r1043bmc_w249_sixgate.json + finalize stdout ledger identity + "
               "fivekeys ALL PASS _r1043bmc_w249_fivekeys.json + backfill needle-count asserts + probe ADMIT "
               "_w250bmc_20261016_probe_receipt.json + push landed dfbb4afa2..cc06f1f4a + S6 log 43x rc=0 + "
               "smoke 49/49 + attrition 4 CLEAN + epoch int readback + tail dual-scan FALSE")

text = json.dumps(d, ensure_ascii=False, indent=1)
atomic_write(sp, text)
atomic_write(os.path.join(ROOT, "fleet", "machines", "bm-c.json"), text)

# --- round report row (canonical path) ---
rp = os.path.join(ROOT, "round_reports-bm-c.md")
t = io.open(rp, encoding="utf-8", newline="").read()
assert "r1043" not in t.splitlines()[-1], "last row already r1043?"
if not t.endswith("\n"):
    t += "\n"
t += ROW + "\n"
atomic_write(rp, t)

# --- self-verification ---
chk = json.load(io.open(sp, encoding="utf-8"))
hb = json.load(io.open(os.path.join(ROOT, "fleet", "machines", "bm-c.json"), encoding="utf-8"))
assert chk["round_no"] == 1044 and chk["last_round"] == "r1043"
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert hb["round_no"] == 1044 and hb["did"] == DID
assert "r1043" in io.open(rp, encoding="utf-8").read().splitlines()[-1]
print("closeout OK: state+heartbeat round_no=1044 last_round=r1043 epoch_int=%d row appended" % EPOCH)
print("row:", ROW[:120], "...")
