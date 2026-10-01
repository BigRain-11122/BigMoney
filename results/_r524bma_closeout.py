# r524 bm-a: state/heartbeat/round-report closeout writes.
import json
import time
from datetime import datetime, timedelta, timezone

NOW = datetime.now(timezone(timedelta(hours=8)))
TS = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")

# --- state-bm-a.json -------------------------------------------------------
st = json.load(open("state-bm-a.json", encoding="utf-8"))
st["round_no"] = 525
st["last_round"] = 524
st["last_round_at"] = TS
st["updated"] = TS
st["last_round_ts"] = TS
st["did"] = [
    "r524: (1) W12 shard-11 delivery gap closed (surgical FF 2f4edee0f, "
    "12/12 on origin, dual-source flagged by bm-b MSG-163x + bm-c MSG-164x); "
    "(2) W12 FINALIZE landed: merged K=26,520 (mu -0.0912, sigma 0.2443), "
    "K-lift @n_eff 390,948: 1.1483->1.1484 (+0.0001), ledger chain "
    "390,948+2,200=393,148 (voids_applied=[LOWAMP-P1] auto), prereg sec.7/8 "
    "backfill 4/4 PASS + n1 selftest re-run green same window (r307 law); "
    "(3) W13 FREEZE SUITE + ENGINE LIVE (fourth engine wave, second "
    "bm-a-owned, sovereignty-rotation first wave): band gate ADMIT "
    "(results/_r524bma_w13_band_gate.py: A=70_001..72_000 forced skip-over "
    "past 66_000/67_000 cluster six-point avoidance, B=29_300..29_499 "
    "arithmetic), prereg frozen, law sec.4 W13 row + SOVEREIGNTY "
    "PRE-PARTITION ROTATION landed (W13=bm-a/W14=bm-b/W15=bm-c mod-3, "
    "F-20261001-01 triple-freeze root-cure), WAVE_CONFIGS/N1_BANDS mirrors "
    "+ W13 materializer selftest leg + pool-era guard leg update, three "
    "selftests green (n1 / perpetual_faces 8/8 / saturation_engine 7 legs), "
    "banned gate ADMIT; engine ignited 16:32:04, self-driving; "
    "(4) prompt registry self-annotated (bm-a=python scripts\\saturation_"
    "engine.py status, shared-repo single-source same path as bm-b; task "
    "name Bigmoney-SatEngine-bm-b fleet-shared local name); (5) MSG-165x "
    "reply dispatched (yield receipts ack + engine_owner gate evidence + "
    "rotation); MSG-163x/164x processed, MSG-161x left for bm-c; "
    "(6) tree re-sync after bm-b r511 + bm-c r323 closeouts (origin-owned "
    "faces checkout + pool_core_samples minimal union +1 line); "
    "(7) S6 33 legs rc0 (dualrun streak 2/3, holiday no-ops correct, "
    "clock_call ORANGE_COOL sleeves=4 activated=0); smoke 47/47; D-19 "
    "MATCH-unchanged; attrition guard CLEAN; post_review all YES; CODELY "
    "r524 lesson appended (reset --mixed stale-tree)"
]
st["verify"] = [
    "origin W12 products 12/12 all machine=bm-a (prov check "
    "results/_r524bma_prov_check.py); n1_w12_results.json K/ledger numbers "
    "as recorded; three selftests PASS incl. W13 leg; engine live evidence "
    "16:32:04 ignited:n1w13-0of12 + done_total climbing; band gate ADMIT "
    "receipt; surgical push 2f4edee0f fetch-verified; watermark red "
    "honest note (W12->W13 idle-gap window, W13 burn heals next window)"
]
st["next"] = [
    "r525: (1) W13 finalize (after 12/12 burned ~59s/shard cadence) + "
    "prereg sec.7/8 backfill + selftest re-run; (2) W14=bm-b rotation slot "
    "(bm-a does NOT freeze; MSG-165x + law rotation row stand); (3) T-142 "
    "GM ruling consumption (awaited; watchlist UNDER REVIEW stands); "
    "(4) T-125 trial-labor W13 next slice r464 surgeon skeleton per "
    "progress pointer; (5) holiday maintenance till 10-08 reopen"
]
st["current_task"] = [
    "r525 queue: W13 finalize (after 12/12) > T-142 ruling consumption > "
    "T-125 r464 surgeon skeleton > holiday maintenance"
]
json.dump(st, open("state-bm-a.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("state: round_no", st["round_no"], "| last_round", st["last_round"])

# --- heartbeat fleet/machines/bm-a.json ------------------------------------
hb = json.load(open("fleet/machines/bm-a.json", encoding="utf-8"))
hb["last_seen"] = TS
hb["current_task"] = st["current_task"][0]
hb["task"] = st["current_task"][0]
hb["heartbeat_epoch_utc"] = int(time.time())
hb["clock_read"] = TS
hb["last_round"] = 524
hb["round_no"] = 525
hb["verdict"] = (
    "r524 OK: W12 finalized (K 26,520, ledger 393,148, sec.7/8 backfilled) "
    "+ W13 frozen+ignited (sovereignty-rotation first wave, A=70_001..72_000 "
    "skip-over ADMIT, engine self-driving) + rotation law landed "
    "(F-20261001-01 root-cure) + shard-11 gap closed 12/12 on origin; "
    "S6 33 legs rc0; smoke 47/47"
)
json.dump(hb, open("fleet/machines/bm-a.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
chk = json.load(open("fleet/machines/bm-a.json", encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
print("heartbeat: epoch", chk["heartbeat_epoch_utc"], "int OK |", TS)

# --- round report round_reports-bm-a.md ------------------------------------
line = (
    f"{TS} | r524 | W12 finalize (K 26,520, ledger 390,948+2,200=393,148, "
    "K-lift +0.0001, sec.7/8 backfill 4/4 PASS) + shard-11 gap closed "
    "(12/12 origin, surgical 2f4edee0f) + W13 freeze suite + engine "
    "ignited 16:32 (rotation first wave: A=70_001..72_000 skip-over ADMIT "
    "/ B=29_300..29_499; law rotation W13=bm-a/W14=bm-b/W15=bm-c = "
    "F-20261001-01 triple-freeze root-cure) + prompt registry self-note + "
    "MSG-165x + tree re-sync (bm-b r511/bm-c r323 closeouts) + CODELY "
    "lesson | watermark RED honest note (W12-done->W13-freeze idle gap; "
    "py_low cand=T-141 only [bm-b-claimed design work, not bm-a-burnable]; "
    "W13 burn in flight heals next window) | 当前活=W13 引擎波烧录中 "
    "(self-driving); 最近实物=results/perpetual_faces/n1_w12_results.json "
    "(16:2x) + research/PERPETUAL_N1_W13_PREREG.md (16:3x); 下个里程碑=W13 "
    "finalize ~17:1x + W14 bm-b 轮值冻结窗 | verify: 3 selftests PASS "
    "(W13 leg) + band gate ADMIT receipt + prov check 12/12 bm-a + smoke "
    "47/47 + S6 33 legs rc0 + attrition CLEAN + D-19 MATCH | delivery N=0 "
    "post-push self-proof | next: r525 W13 finalize > T-142 GM ruling > "
    "T-125 r464 surgeon skeleton\n"
)
with open("round_reports-bm-a.md", "a", encoding="utf-8", newline="") as f:
    f.write(line)
print("round report: r524 line appended")
