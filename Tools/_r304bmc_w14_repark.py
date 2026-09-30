"""r304 bm-c one-shot: W14-GENERATE governance re-park restoration.

Restores the canonical park state (bm-b r494 / commit 6297d6b10) after the
resurrection-3 chain: that re-park (entry+shard waiting + park_note) was
swallowed by the merger marker hole -- waiting+park_note lost to a stale
lane's bare-ready via the legacy rank (ready 2 > waiting 1) -- leading to
bm-a's unauthorized claim+launch (72bb3c0e0, 06:18:09) and bm-c daemon
takeover attempts (06:38-06:40, every claim deferred/rolled back, zero
launches on bm-c). The marker arm is fixed in this same commit
(merge_lane_views park_note deliberate-hold arm), so this re-park survives
future stale-ready merges: marked-waiting beats bare-ready (r378 risk
asymmetry).

Unfreeze law unchanged per MSG-060x: sec-4 self-proof or GM dual-ruling
ONLY. Kill-advice MSG-20261001-0637 to bm-a outstanding (w14_candidates.json
absent = trial-gate N=0, zero-loss window held). bm-a's kill+re-park receipt
supersedes the shard state when it lands.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + os.sep + "..")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + os.sep + ".." + os.sep + "scripts")

import Tools.autofill as af

EID = "TRIAL-LABOR-W14-GENERATE"

ENTRY_NOTE = (
    "r304 bm-c re-park (resurrection-3 closure): 6297d6b10 governance re-park "
    "(entry+shard waiting) was resurrected to bare-ready via merger marker "
    "hole (park_note not recognized as deliberate-hold marker; stale lane "
    "beat waiting via legacy rank ready>waiting) -> bm-a daemon claim+launch "
    "72bb3c0e0 06:18:09 + bm-c daemon takeover attempts 06:38-06:40 (all "
    "claim-deferred/rolled back, zero launches on bm-c, no pool_claims "
    "residue); marker arm fixed this commit; unfreeze = sec-4 self-proof or "
    "GM dual-ruling ONLY per MSG-060x; kill-advice MSG-20261001-0637 to bm-a "
    "outstanding (w14_candidates.json absent = N=0, zero-loss window held)"
)

SHARD_NOTE_SUFFIX = (
    " | r304 bm-c: re-parked after resurrection-3 (entry park_note carries "
    "full chain); bm-a burn kill-advice MSG-20261001-0637 outstanding; "
    "shard face superseded by bm-a kill+re-park receipt when it lands"
)


def main():
    assert not os.path.exists("results/trial_labor_w14/w14_candidates.json"), \
        "FAIL-CLOSED: product landed -- zero-loss window gone, escalate to GM"
    pool = af._pool_merged_view()
    e = next(x for x in pool.get("entries", []) if x.get("id") == EID)
    assert e.get("status") == "ready", e.get("status")
    now = af._now()
    e["status"] = "waiting"
    e["park_note"] = ENTRY_NOTE
    e.setdefault("parked_per", "D-20260930-41 sec.1.2 confirm-type-timing ban "
                               "+ MSG-20260930-1755-bma-ALL bm-a r483 "
                               "adjudication; receipt bm-b r473")
    sh = e["shards"][0]
    assert sh.get("key") == "generate-0of1", sh
    if sh.get("owner_since"):
        sh.setdefault("claimed_since", sh["owner_since"])
    sh["status"] = "waiting"
    sh["owner_since"] = now  # r311 latest.ts: this row is the newest same-key base
    sh["park_note"] = str(sh.get("park_note") or "") + SHARD_NOTE_SUFFIX
    af._write_lane_file_strict(af.POOL, pool)
    res = af._pool_settle()
    print("[settle]", res)
    pool2 = af._pool_merged_view()
    e2 = next(x for x in pool2.get("entries", []) if x.get("id") == EID)
    assert e2.get("status") == "waiting", e2.get("status")
    assert all(s.get("status") == "waiting" for s in e2["shards"]), e2["shards"]
    print("[verify] W14-GENERATE re-parked: entry waiting + %d shard(s) waiting"
          % len(e2["shards"]))


if __name__ == "__main__":
    main()
