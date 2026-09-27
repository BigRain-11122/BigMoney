# r370 bm-a: V2-P1 lane pin 3rd re-adoption + bm-c dead-claim clear (4th swallow case, tree-blind window).
# bm-c tick 01:50:04 (pre-defer old code, tree forked before pin 208c487d) rewrote whole pool with its
# stale lane_owner=null face AND claimed v2-0of1 (bm-c lacks t34 curves per data_gates proven sets ->
# artifact-gate exit-2 treadmill). Fix: re-pin lane_owner=bm-b + clear bm-c dead claim + note update.
import json

POOL = "results/runnable_pool.json"
TID = "DECISION-CHAIN-V2-P1"
LANE_NOTE = ("a2 canonical (bm-c r118 adoption): execution lane = checkpoint-bearing machines; "
             "proven-complete set per own data_gates = bm-b (t34 base curves both axes + x2 curve union "
             "complete + deep panel, v1 finalize r318); bm-a artifact-gate exit-2 relaunch loop 01:10/01:20 "
             "tick log evidence; T-93 sender/receiver hash parity 30/30; "
             "3rd re-pin r370 02:2x: 1st pin e8d63eb4 swallowed by r351 resolver union (re-adopt 208c487d), "
             "2nd swallow = bm-c tick 01:50:04 tree-blind whole-file write (pre-defer old code) which also "
             "claimed v2-0of1 as bm-c (dead claim: no t34 curves on bm-c per data_gates) -- cleared; "
             "post-defer ticks (autofill r351+) defer git writes when origin moved pool")

raw = open(POOL, "rb").read()
crlf = b"\r\n" in raw
d = json.loads(raw.decode("utf-8"))
entries = d["entries"] if isinstance(d, dict) else d
e = next(x for x in entries if x.get("id") == TID)
assert e.get("lane_owner") in (None, "bm-b"), f"guard: unexpected lane_owner {e.get('lane_owner')!r}"

changed = []
if e.get("lane_owner") != "bm-b":
    e["lane_owner"] = "bm-b"
    changed.append("lane_owner->bm-b")
e["lane_note"] = LANE_NOTE
changed.append("lane_note updated (3rd re-pin provenance)")
for s in e.get("shards") or []:
    if s.get("owner") == "bm-c" and s.get("owner_since") == "2026-09-28 01:50:04":
        s["owner"] = None
        s["owner_since"] = None
        changed.append("bm-c dead claim cleared (v2-0of1, no t34 curves on bm-c)")

text = json.dumps(d, ensure_ascii=False, indent=1)
if crlf:
    text = text.replace("\n", "\r\n")
open(POOL, "wb").write(text.encode("utf-8"))
chk = json.loads(open(POOL, "rb").read().decode("utf-8"))
ent = next(x for x in (chk["entries"] if isinstance(chk, dict) else chk) if x.get("id") == TID)
assert ent["lane_owner"] == "bm-b"
assert all(s.get("owner") is None for s in ent.get("shards") or [])
print("ADOPTED-3rd:", "; ".join(changed))
