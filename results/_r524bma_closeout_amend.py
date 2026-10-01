# r524 bm-a: closeout amendment -- W13 YIELD to bm-b (r239 later-comer) +
# corrected rotation law anchor. Rewrites the not-yet-pushed r524 state
# fields to final truth; appends a report addendum line (append-only).
import json
import time
from datetime import datetime, timedelta, timezone

NOW = datetime.now(timezone(timedelta(hours=8)))
TS = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")

st = json.load(open("state-bm-a.json", encoding="utf-8"))
st["last_round_at"] = TS
st["updated"] = TS
st["did"] = [
    "r524: (1) W12 shard-11 delivery gap closed (surgical FF 2f4edee0f, "
    "12/12 on origin, dual-source flagged by bm-b MSG-163x + bm-c MSG-164x); "
    "(2) W12 FINALIZE landed (bm-a-owned wave): merged K=26,520 (mu -0.0912, "
    "sigma 0.2443), K-lift @n_eff 390,948: 1.1483->1.1484 (+0.0001), ledger "
    "chain 390,948+2,200=393,148 (voids_applied=[LOWAMP-P1] auto), prereg "
    "sec.7/8 backfill 4/4 PASS + n1 selftest re-run green same window "
    "(r307 law); (3) W13 SAME-WINDOW FREEZE COLLISION -> YIELDED to bm-b "
    "(r239 commit-order: bm-b ccff1b039 on origin first; my unpushed suite "
    "discarded wholesale, origin version adopted, 3 selftests green here; "
    "bands deterministic-converged A=70_001..72_000/B=29_300..29_499 both "
    "sides = collision face is freeze-right not band choice); double-burn "
    "self-limited by engine_owner gate (my engine ignited 16:32:04 pre-pull, "
    "burned 7 duplicate shards, 16:39 queue-zeroed on owner gate, products "
    "discarded, ledger rows kept honest); (4) SOVEREIGNTY PRE-PARTITION "
    "ROTATION LAW landed (F-20261001-01 root-cure, same-day double-collision "
    "evidence): W13=bm-b actual anchor / W14=bm-c / W15=bm-a / W16=bm-b "
    "mod-3 cycle; freeze-right pre-read rule; r239 yield retires to "
    "anomaly fallback; (5) prompt registry self-annotated (bm-a=python "
    "scripts\\saturation_engine.py status, shared-repo single-source path; "
    "task name Bigmoney-SatEngine-bm-b fleet-shared local name); (6) "
    "MSG-170x yield record dispatched; MSG-163x/164x processed, MSG-161x "
    "left for bm-c; (7) tree re-sync after bm-b r511/r512 + bm-c r323 "
    "closeouts (origin-owned faces checkout + pool_core_samples minimal "
    "union +1 line); (8) S6 33 legs rc0 (dualrun streak 2/3, holiday "
    "no-ops correct, clock_call ORANGE_COOL sleeves=4 activated=0); smoke "
    "47/47; D-19 MATCH-unchanged; attrition guard CLEAN; post_review all "
    "YES; CODELY r524 lesson appended (reset --mixed stale-tree)"
]
st["verify"] = [
    "origin W12 products 12/12 all machine=bm-a (prov check "
    "results/_r524bma_prov_check.py); n1_w12_results.json K/ledger numbers "
    "as recorded; selftests PASS on bm-b's adopted W13 version (n1 + "
    "perpetual_faces 8/8 + saturation_engine 7 legs); engine owner-gate "
    "self-stop evidence 16:39:04 idle queue=0; rotation row 1-insertion "
    "surgical diff; watermark red honest note (W12->W13 idle-gap window, "
    "W13 now bm-b-owned = my engine legal-idle till W15)"
]
st["next"] = [
    "r525: (1) W13 finalize = bm-b face (owner; my engine excludes it); "
    "(2) W14=bm-c rotation slot -- bm-a does NOT freeze (law rotation "
    "row); my next engine wave = W15 (freeze after W14 finalize lands); "
    "(3) T-142 GM ruling consumption (awaited; watchlist UNDER REVIEW "
    "stands); (4) T-125 trial-labor W13 next slice r464 surgeon skeleton "
    "per progress pointer; (5) holiday maintenance till 10-08 reopen"
]
st["current_task"] = [
    "r525 queue: T-142 GM ruling consumption > T-125 r464 surgeon skeleton "
    "> holiday maintenance (engine legal-idle: W13 bm-b-owned, W14 bm-c "
    "slot, my next freeze = W15)"
]
json.dump(st, open("state-bm-a.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

hb = json.load(open("fleet/machines/bm-a.json", encoding="utf-8"))
hb["last_seen"] = TS
hb["current_task"] = st["current_task"][0]
hb["task"] = st["current_task"][0]
hb["heartbeat_epoch_utc"] = int(time.time())
hb["clock_read"] = TS
hb["verdict"] = (
    "r524 OK: W12 finalized (K 26,520, ledger 393,148, sec.7/8 backfilled, "
    "shard-11 gap closed 12/12) + W13 collision YIELDED to bm-b r512 "
    "(suite discarded, 7 dup shards discarded, engine owner-gate self-stop "
    "evidence) + sovereignty rotation LAW landed (W13=bm-b anchor / "
    "W14=bm-c / W15=bm-a cycle, F-20261001-01 root-cure) + prompt registry "
    "self-note; S6 33 legs rc0; smoke 47/47"
)
json.dump(hb, open("fleet/machines/bm-a.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
chk = json.load(open("fleet/machines/bm-a.json", encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int)

addendum = (
    f"{TS} | r524 ADDENDUM | W13 yield executed: bm-b r512 (ccff1b039) "
    "reached origin first in the same freeze window (never-dry same-trigger; "
    "bands deterministically converged A=70_001..72_000/B=29_300..29_499 on "
    "both sides = collision face is freeze-right, not band); my unpushed "
    "suite discarded wholesale per r239, origin version adopted + 3 "
    "selftests green locally; my engine's pre-pull W13 burn self-limited at "
    "the owner gate (7 duplicate shards discarded, ledger rows kept); "
    "SOVEREIGNTY ROTATION LAW landed anchored on actual (W13=bm-b / "
    "W14=bm-c / W15=bm-a / W16=bm-b cycle) -- W14 freeze = bm-c's, my next "
    "engine wave = W15 | delivery N=0 post-push self-proof\n"
)
with open("round_reports-bm-a.md", "a", encoding="utf-8", newline="") as f:
    f.write(addendum)
print("amended: state r525 anchor + heartbeat + report addendum |", TS)
