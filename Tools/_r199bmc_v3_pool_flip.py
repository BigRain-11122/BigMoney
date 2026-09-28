# -*- coding: utf-8 -*-
"""r199 bm-c: DECISION-CHAIN-V3-TOURNAMENT pool flip waiting->ready
(per prereg s6 'v2 finalize -> ready-flip 衔接零死轮' + entry defer_note
'flip executor = the round that observes V2-P1 done + runner selftest green').
Shared-face single-writer law (pool schema); r409 bm-a flip precedent."""
import json

POOL = "results/runnable_pool.json"
NOW = "2026-09-29T05:08:00+08:00"

with open(POOL, encoding="utf-8") as fh:
    pool = json.load(fh)

entries = pool["entries"]
e = next(x for x in entries if x["id"] == "DECISION-CHAIN-V3-TOURNAMENT")
v2 = next(x for x in entries if x["id"] == "DECISION-CHAIN-V2-P1")

# --- ready conditions asserted (defer_note verbatim) ---
assert e["status"] == "waiting", f"v3 status {e['status']} != waiting"
assert v2["status"] == "done", f"V2-P1 status {v2['status']} != done (queue law)"
import os
assert os.path.exists("scripts/decision_chain_v3_tournament.py"), "runner absent"
assert os.path.exists("results/sentiment_axes/axes_full_history.json"), \
    "full-A axes artifact absent (H2' physical dep)"

e["status"] = "ready"
e["ready_at"] = NOW
e["ready_flipped_by"] = "bm-c r199"
sh = e["shards"][0]
assert sh["key"] == "v3-0of1"
sh["status"] = "ready"
e["data_gates"] = (
    "READY (flip bm-c r199; defer_note conditions MET: V2-P1 done "
    "(LANDED bm-b 16:40 chain_win=False) + runner built "
    "scripts/decision_chain_v3_tournament.py selftest 18/18 hermetic "
    "r116 law + G-STYLE/G-SENTIMENT censuses in-runner fail-closed). "
    "In-runner exit-2 gates: artifact (t34 curves both axes + deep panel "
    "t18 + sleeve two-path a4/a5 + GC001 + v1 records + t18 manifest) + "
    "G-V3 both legs + G-ANCHOR 6/6 + G-CENSUS {1255,1506} + G-MANIFEST "
    "48 + G-REPRO-v1 B/D bit-level (ci95 seed decoration excluded per "
    "v2 s9-a6) + G-REPRO-REV sleeve stats bit-level + G-STYLE four style "
    "legs r60 window census (partial=degraded disclosure non-VOID) + "
    "G-SENTIMENT axes artifact sha256 integrity + window coverage + "
    "HOST GATE machine==bm-b (prereg s2 mandatory host; non-host = "
    "honest VOID exit 2, verified live on bm-c r199). A-1 amendment "
    "face: H2' sentiment gate consumes frozen git artifact "
    "results/sentiment_axes/axes_full_history.json (SENTIMENT-AXES-"
    "FULLHIST-P1 done) -- zero Money02 dependency added beyond v2 "
    "family. J-TOUR: falsification vs H3 + DSR n_trials=16566 + CSCV "
    "PBO three-arm calendar panel (slice-law asserted) + E[FP]; winner "
    "= candidate registration only, paper wiring through 10-01 month "
    "boundary. After run: verdict JSON+CSV+prereg s7/s8 backfill+ledger "
    "v3 row flip+gate_attrition row (runner mechanical); harvest "
    "receipt = round report + CODELY.md line (session face).")
e["flip_note"] = (
    "ready-flip bm-c r199 per prereg s6 zero-dead-round law; burn host "
    "pinned bm-b (lane_owner honored); RAM r354 three-sample law "
    "applies at launch; negative results reported honestly per "
    "O-20260927-2255 (results reported as soon as they land).")

with open(POOL, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(pool, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
print("FLIPPED: DECISION-CHAIN-V3-TOURNAMENT waiting -> ready "
       f"(shard {sh['key']} ready, {NOW})")
