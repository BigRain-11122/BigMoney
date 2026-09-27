# r370 bm-a idempotent re-adoption: DECISION-CHAIN-V2-P1 lane pin swallowed by r351 resolver union
# (r348-family cross-machine swallow, 3rd case after r349/r120).
# r369 pin face (commit e8d63eb4) replayed verbatim: lane_owner=bm-b + lane_note + stale bm-a
# shard-claim cleared. Guards: no-op if already adopted; abort if unexpected foreign state.
import json

POOL = "results/runnable_pool.json"
TID = "DECISION-CHAIN-V2-P1"
LANE_NOTE = ("a2 canonical (bm-c r118 adoption): execution lane = checkpoint-bearing machines; "
             "proven-complete set per own data_gates = bm-b (t34 base curves both axes + x2 curve union "
             "complete + deep panel, v1 finalize r318); bm-a artifact-gate exit-2 relaunch loop 01:10/01:20 "
             "tick log evidence; T-93 sender/receiver hash parity 30/30")

raw = open(POOL, "rb").read()
crlf = b"\r\n" in raw
d = json.loads(raw.decode("utf-8"))
entries = d["entries"] if isinstance(d, dict) else d
assert isinstance(entries, list), "entries must be list"
e = None
for x in entries:
    if x.get("id") == TID:
        e = x
        break
assert e is not None, "target entry missing"

lo = e.get("lane_owner")
assert lo in (None, "bm-b"), f"guard: unexpected lane_owner {lo!r} (foreign pin present; abort)"
changed = []
if lo != "bm-b":
    e["lane_owner"] = "bm-b"
    changed.append("lane_owner->bm-b")
if e.get("lane_note") != LANE_NOTE:
    e["lane_note"] = LANE_NOTE
    changed.append("lane_note restored")
sh = e.get("shards") or []
for s in sh:
    if s.get("owner") == "bm-a" and s.get("owner_since") == "2026-09-28 01:20:05":
        s["owner"] = None
        s["owner_since"] = None
        changed.append("stale bm-a shard claim cleared (v2-0of1)")

if not changed:
    print("NO-OP: lane pin already in place")
else:
    text = json.dumps(d, ensure_ascii=False, indent=1)
    if crlf:
        text = text.replace("\n", "\r\n")
    with open(POOL, "wb") as f:
        f.write(text.encode("utf-8"))
    chk = json.loads(open(POOL, "rb").read().decode("utf-8"))
    ent = [x for x in (chk["entries"] if isinstance(chk, dict) else chk) if x.get("id") == TID][0]
    assert ent["lane_owner"] == "bm-b", "post-write verify failed"
    assert all(s.get("owner") is None for s in ent.get("shards") or []), "shard claim verify failed"
    print("ADOPTED:", "; ".join(changed))
