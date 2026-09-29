# r451 bm-a: GM lane reassignment for TRIAL-LABOR-W11-GENERATE (O-1730 stale-takeover)
# Claimant bm-b silent >120min (session heartbeat 22:46:38, autofill keepalive last
# 23:36:24, zero generate products landed on origin since; machine offline evidence).
# Generate leg verified data-free: cmd_generate has zero parquet/deep-panel/network
# deps (pure git-face grammar+seeds+exclusion). Single-shot refuse-if-exists guard
# in runner = zero double-burn on bm-b revival (its autofill fresh-read pool yields
# to fresh owner claim). Pool single-writer respected: minimal field edit, no other
# entries touched. Lane reassign bm-b -> ANY opens the shard to healthy-machine
# claim per O-1730 (CEO immediate-law: takeover without waiting for stale owner).
import json
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
PATH = "results/runnable_pool.json"
EID = "TRIAL-LABOR-W11-GENERATE"

raw = open(PATH, encoding="utf-8").read()
d = json.loads(raw)
e = [x for x in d["entries"] if x.get("id") == EID]
assert len(e) == 1, f"expected exactly 1 entry, got {len(e)}"
e = e[0]
before = e.get("lane_owner")
assert e.get("status") == "ready", f"entry status {e.get('status')} != ready"
assert e["shards"][0].get("status") == "ready", "shard not ready"

e["lane_owner"] = "ANY"
e["_lane_reassign"] = {
    "from": before,
    "to": "ANY",
    "by": "bm-a GM per O-1730 stale-takeover",
    "ts": "2026-09-30 00:5x +08:00",
    "why": "owner machine silent >120min: session heartbeat 2026-09-29 22:46:38, "
           "autofill keepalive stopped 23:36:24, zero generate products on origin "
           "74min+; generate leg verified data-free (no deep-panel/network deps, "
           "pure git-face); runner refuse-if-exists single-shot guard = zero "
           "double-burn; SCREEN/JUDGE lanes stay bm-b (deep-panel data law R31)",
}

out = json.dumps(d, ensure_ascii=False, indent=1)
json.loads(out)  # parse-verify before write
open(PATH, "w", encoding="utf-8", newline="").write(out)
print(json.dumps({"entry": EID, "lane_owner": before + " -> ANY",
                  "shard_owner_unchanged": e["shards"][0].get("owner")},
                 ensure_ascii=False))
