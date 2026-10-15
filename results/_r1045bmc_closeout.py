# -*- coding: utf-8 -*-
# r1045 bm-c closeout: state + heartbeat + round-report row (canon clone pattern from r1043).
import io
import json
import os
import time
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
EPOCH = int(time.time())

ABSORB = ("r1045 absorb note: dead window self-labeled r1044 (fired ~06:5x after r1043 closeout 06:04:57) "
          "executed the P0 autofill _tick_owned_dirt check-ignore filter fix + W20 SCREEN shard-2 claim "
          "deadlock heal (staged-set mutual block, session-owns-index resolution) with commits+pushes already "
          "on origin (90d02a94e P0 fix + 3f78fa7e7 shard-1 close heal + 69f22f780 autofill claim + a19d36a5b "
          "harvest flip + 629e85de8 pool_worker pass no-op sweep), W20 SCREEN 4/4 shards ALL CLOSED via its "
          "chain, plus W250 prereg prep scratch (frozen-face extraction results/_w250bmc_w249_frozen_face.txt "
          "+ needle scans results/_w250bmc_ctx.txt / _w250bmc_needle_counts.txt / _r1044bmc_needle_floor_scan* "
          "-- byte-verified == git 4103f0d5d blob this window BEFORE use), then died pre-closeout (state frozen "
          "at round_no=1044, heartbeat stale at r1043/06:04:57, zero W250 prereg emitted); this session "
          "executed as r1045 (next after highest committed label r1044) per bm-c absorb precedent lineage "
          "(r894..r1043, 38th instance) and advanced counter 1044->1046 so next session = r1046; zero "
          "double-count: S0.5 dual-delta FALSE both scans this window (ORD f321f54a / DEC ec6b9164 hold, "
          "probe-verified, unacked=0), dead-window debts handled by its own origin commits + this window "
          "landing the prep estate")

DID = ("r1045 bm-c: (1) S0-1 anchor bm-c + round-zero probe py_faces=6 orphans=2 zero-kill; (2) ABSORB 38th gen "
       "(dead r1044: P0 autofill fix + W20 shard-2 unlock chain already on origin; prep estate landed this "
       "window, frozen-face byte-verified vs git 4103f0d5d); (3) P0 PRODUCT = W250 PREREG FREEZE LANDED "
       "4f7a130ff pushed origin (seat-first FIRST ACTION, machine-SUB from frozen W249 template: bands A "
       "565_501..567_500 / B 545_101..545_300 both hops=0 seed-decoupled 13th consecutive seed-gap face, "
       "key-anchored to W249 actuals ledger 972,135 / K=545,720 / merged mu -0.09277202 / sigma 0.2450284 / "
       "p95 0.3158 / se_mu 0.000332 equal-chain / K-lift 0.0000; banned_direction_gate ADMIT rc0 this window; "
       "machine gates 55 VMAP legs + 53 floors + 9 post-legs + 71 MUST + 51 MUST_NOT + 7 block replaces all "
       "PASS; three same-window heals disclosed: probe-receipt date-roll leg _20261015->_20261016 (precedent "
       "chain had no date leg, W248/W249 shared date), lowercase line_pre_w248 POST_LEG (escapes uppercase "
       "W-roll, W249 derive precedent), owner face 本候选 bm-a->bm-c (E63 heal family, r1042 live-block heal "
       "precedent)); (4) S0.5 dual-delta FALSE both scans (opening + S7 tail) + unacked=0; (5) smoke 49/49; "
       "(6) S6 43/43 rc0 idempotent sweep (bars 10-15 consumed, 10-16 not due till 15:30, token delta=0); "
       "(7) W20 SCREEN 4/4 shards ALL DONE (pool face closed by dead-r1044 chain, verified); (8) S7 quad green "
       "(loop pin=5 no-op + watchdog re-registered + claws x2 live-verified by this window's commit+push) + "
       "attrition 4 CLEAN; counter 1044->1046")

NEXT = ("r1046: (1) W250 five-face freeze splice = FIRST ACTION (editor derive: clone results/_w249bmc_derive_editor.py "
        "13.9KB -> _w250bmc_derive_editor.py with wave+1 rolls (range faces: fresh range(238,250)/legs range(233,249)/"
        "dropped list(range(237,248))->(238,249)/kept [232..236]->[233,237]/parity 107->108 rows/receipt keys from "
        "_w250bmc_20261016_probe_receipt.json), run editor -> results/_w250bmc_freeze_edits.py, run splice on disk; "
        "(2) engine mtime-watch self-burn 12/12 follows (2-cycle product-growth face = ignition evidence r325 law); "
        "(3) sixgate PRE-FINALIZE in the burn window (W217+ standing law); (4) finalize one-pass + fivekeys + sec7/8 "
        "backfill (bm-c r1043 W249 paradigm); (5) bars 10-16 window 15:30 (papers debt=0); (6) W251 seat publish after "
        "finalize; (7) ORD/DEC tail re-scan")

VERDICT = ("green: r1045 = ABSORB 38th (dead r1044 estate: P0 autofill fix chain already on origin + prep scratch "
           "verified+landed) + P0 PRODUCT W250 PREREG FREEZE LANDED 4f7a130ff (machine-SUB, banned ADMIT rc0, "
           "W250 supply chain unblocked: splice->burn->finalize = r1046) + S6 43/43 + smoke 49/49 + S7 quad green")

PROD = ("CPU=W20 SCREEN 4/4 shards ALL DONE (pool face closed 07:0x via dead-r1044 chain, verified this window) + "
        "engine queue idle (never-dry supply = W250 prereg frozen, splice next) ; GPU=VRAM 14.54G free ; N1=W250 "
        "PREREG FROZEN 4f7a130ff (bands A 565_501..567_500 / B 545_101..545_300) -> five-face splice = r1046 first "
        "action ; SPAWN-GATE=codely cap2 live")

ARTIFACT = ("research/PERPETUAL_N1_W250_PREREG.md (W250 prereg freeze LANDED 4f7a130ff pushed origin 06-16 07:3x, "
            "banned_direction_gate ADMIT rc0, key-anchored to W249 actuals ledger 972,135 / K=545,720) + "
            "results/_r1045bmc_s6_log.txt (43 legs rc=0)")

CLOSE = ("r1045: 38th-gen absorb (dead r1044: P0 autofill fix + W20 shard-2 unlock chain on origin + W250 prep "
         "estate verified+landed) + P0 PRODUCT W250 PREREG FREEZE LANDED 4f7a130ff (seat-first FIRST ACTION, "
         "machine-SUB from frozen W249 template, banned ADMIT rc0, three same-window needle heals disclosed: "
         "date-roll / lowercase line_pre / owner-face E63) + W20 SCREEN 4/4 closed + S6 43/43 + smoke 49/49 + "
         "S7 quad green + attrition 4 CLEAN | " + NOW)

SELFPROOF = {
    "占用一行": PROD,
    "当前活": "r1045 closeout (W250 prereg freeze landed + dead r1044 absorb)",
    "最近实物": ARTIFACT,
    "下个交付物": "W250 five-face splice + engine self-burn 12/12 + sixgate PRE-FINALIZE + finalize (r1046 chain)",
    "队列水位": "池 ready=0 (W20 closed)·N1 W250 prereg frozen·P2/P3 空·jobs 0",
}

ROW = (NOW + " | r1045 | bm-c | ABSORB 38th gen (dead r1044: P0 autofill _tick_owned_dirt fix + W20 shard-2 "
       "claim deadlock heal + autofill/pool_worker self-commits 90d02a94e/3f78fa7e7/69f22f780/a19d36a5b/629e85de8 "
       "all on origin pre-death, W20 SCREEN 4/4 closed; prep scratch frozen-face+needles landed this window, "
       "byte-verified == git 4103f0d5d; state frozen 1044) + P0 PRODUCT = W250 PREREG FREEZE LANDED 4f7a130ff "
       "pushed origin: machine-SUB from frozen W249 template, bands A 565_501..567_500 / B 545_101..545_300 both "
       "hops=0 seed-decoupled (13th consecutive seed-gap), key-anchored to W249 actuals (ledger 972,135 / K=545,720 "
       "/ mu -0.09277202 / sigma 0.2450284 / p95 0.3158 / se 0.000332 / K-lift 0.0000), banned_direction_gate ADMIT "
       "rc0, gates 55+53+9+71+51 all PASS, 7 blocks replaced; three same-window heals disclosed: probe-receipt "
       "date-roll leg (W248/W249 shared date = precedent had no date leg), lowercase line_pre_w248 POST_LEG, owner "
       "face bm-a->bm-c (E63 family) | S0.5 dual-delta FALSE both scans + unacked=0 | smoke 49/49 | S6 43/43 rc0 "
       "(bars 10-16 not due till 15:30, token delta=0) | W20 SCREEN 4/4 ALL DONE verified | S7 quad green (loop "
       "pin=5 no-op, watchdog re-registered, S4U flip denied=adjudicated default-principal face, claws x2 "
       "live-verified via commit+push) + attrition 4 CLEAN | watermark verdict GREEN (red=false healthy lane, "
       "supply face=W250 prereg frozen) | orphan_face=2 zero-kill | local-ahead-of-origin=0 (push landed "
       "629e85de8..4f7a130ff verified; closeout commit rides after) | next r1046: W250 five-face splice FIRST "
       "ACTION (editor derive wave+1 clone -> freeze_edits -> splice -> engine self-burn -> sixgate PRE-FINALIZE "
       "-> finalize chain) + bars 10-16 15:30 recheck")


def atomic_write(path, text):
    tmp = path + ".tmp_r1045"
    with io.open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    os.replace(tmp, path)


# --- state-bm-c.json + heartbeat (mirrored content) ---
sp = os.path.join(ROOT, "state-bm-c.json")
d = json.load(io.open(sp, encoding="utf-8"))
d["round_no"] = 1046
d["round_no_label"] = "r1045"
d["last_round"] = "r1045"
d["last_round_label"] = "r1045"
for k in ("clock_read", "ts", "updated", "updated_at", "last_seen", "last_seen_at",
          "now_active", "activity_now", "last_round_at", "last_round_ts",
          "last_round_closed", "last_round_summary_at", "last_ts", "last_action_at",
          "current_task_at"):
    d[k] = NOW
d["current_task"] = "r1045 closeout (W250 prereg freeze landed + dead r1044 absorb)"
d["current_task_ts"] = EPOCH
d["heartbeat_epoch_utc"] = EPOCH
d["heartbeat_epoch_utc_type"] = "int (assert)"
d["did"] = DID
d["note"] = ("r1045: W250 PREREG FROZEN 4f7a130ff (machine-SUB from W249 template, banned ADMIT, bands A "
             "565_501..567_500 / B 545_101..545_300) | five-face splice = r1046 first action | W20 SCREEN "
             "4/4 closed")
d["last_round_summary"] = ("r1045: absorb 38th gen + W250 prereg FREEZE LANDED 4f7a130ff (banned ADMIT rc0, "
                          "3 needle heals disclosed) + W20 4/4 closed + S6 43/43 + smoke 49/49 + S7 quad green")
d["last_action"] = "r1045 closeout (W250 prereg freeze + dead r1044 absorb)"
d["verdict"] = VERDICT
d["next"] = NEXT
d["next_pointer"] = NEXT
d["next_milestone"] = "r1046+: W250 five-face splice + engine self-burn + sixgate + finalize + bars 10-16 15:30 window"
d["latest_artifact"] = ARTIFACT
d["last_artifact"] = ARTIFACT
d["recent_artifact"] = ARTIFACT
d["prod_lanes"] = PROD
d["full_load_selfproof"] = SELFPROOF
d["r1045_absorb_note"] = ABSORB
d["r1045_closeout_note"] = CLOSE
d["head_sha"] = "4f7a130ff (r1045 prereg freeze; origin/main same, push landed 629e85de8..4f7a130ff)"
d["sync"] = {"origin_tip": "4f7a130ff (prereg freeze push landed first-try clean; closeout commit rides after)",
             "ts": NOW, "ahead_behind": "local-ahead-0 (push + fetch verified pre-closeout)"}
d["last_pulled_at"] = NOW
d["cpu_pct"] = "4"
d["cpu_util_pct"] = "4"
d["cpu_idle_pct"] = 96.0
d["free_ram_gb"] = 6.3
d["ram_free_gb"] = 6.3
d["idle_ram_gb"] = 6.3
d["gpu_free_vram_gb"] = 14.54
d["gpu_free_vram_mib"] = 14889
d["gpu_free_vram_mb"] = 14889
d["gpu_vram_free_mb"] = 14889
d["free_vram_mb"] = 14889
d["orphan_face"] = 2
d["orphan_faces"] = 2
d["idle_rounds"] = 0
d["agenda_starved"] = False
d["codely_live_count"] = 1
d["verify"] = ("receipts: prereg derive stdout (34,465B, 7 blocks, 55+53+9+71+51 gates) + banned gate ADMIT "
               "rc0 + push landed 629e85de8..4f7a130ff + S6 log 43x rc=0 (results/_r1045bmc_s6_log.txt) + "
               "smoke 49/49 + attrition 4 CLEAN + epoch int readback + tail dual-scan FALSE + frozen-face "
               "byte-identity vs git 4103f0d5d")

text = json.dumps(d, ensure_ascii=False, indent=1)
atomic_write(sp, text)
atomic_write(os.path.join(ROOT, "fleet", "machines", "bm-c.json"), text)

# --- round report row (canonical path) ---
rp = os.path.join(ROOT, "round_reports-bm-c.md")
t = io.open(rp, encoding="utf-8", newline="").read()
assert "r1045" not in t.splitlines()[-1], "last row already r1045?"
if not t.endswith("\n"):
    t += "\n"
t += ROW + "\n"
atomic_write(rp, t)

# --- self-verification ---
chk = json.load(io.open(sp, encoding="utf-8"))
hb = json.load(io.open(os.path.join(ROOT, "fleet", "machines", "bm-c.json"), encoding="utf-8"))
assert chk["round_no"] == 1046 and chk["last_round"] == "r1045"
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
assert hb["round_no"] == 1046 and hb["did"] == DID
assert "r1045" in io.open(rp, encoding="utf-8").read().splitlines()[-1]
print("closeout OK: state+heartbeat round_no=1046 last_round=r1045 epoch_int=%d row appended" % EPOCH)
print("row:", ROW[:120], "...")
