# _r881bmc_w18_lane_relay.py -- r881 bm-c: W18 pool enforcement edit
# (W17 handover-precedent relay). Content-level double-file edit: shared +
# lane faces both edited identically in one op (double-file law); the
# pre-existing 26B inter-face delta is sync_face-settled ('unchanged'
# verdict 17:2x) and is left untouched (drift archaeology NOT in scope).
#   (1) TRIAL-LABOR-W18-GENERATE -> done (session flip; products landed
#       16:57:43 in f705f1ccc: 692 cells census sha16 724b6135 + ledger
#       row; cmd_generate exits no-claim by design (W17 family) --
#       session flip is the done path, W17-GENERATE done owner bm-a
#       precedent). Stops the no-claim re-fire loop.
#   (2) SCREEN-SHARD-1..7 lane_owner bm-c -> "ANY" (RAM-gate relay per
#       W17 precedent + CEO O-1825 chain clock: bm-c free RAM 0.8-1.5GB
#       << 4GB gate, parked by CEO game session 4.6GB + MV chain = legal
#       yield; bm-b alive ram_free 6.2GB 17:11:44 heartbeat; data_deps
#       all git-tracked = bm-b data-locality gate passes). SHARD-0 stays
#       lane bm-c (worker pid alive in r379 bounded RAM wait -- machine-
#       local checkpoints have no cross-machine lock, shard-0 must stay
#       single-machine to bar double-burn).
import json
import datetime

SHARED = "results/runnable_pool.json"
LANE = "results/runnable_pool.bm-c.json"
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
RELAY_NOTE = ("r881 bm-c lane relay (W17 handover precedent): bm-c free "
              "RAM 0.8-1.5GB << 4GB gate r354 (CEO game session 4.6GB + "
              "MV chain = legal yield), shard workers parked r379/r491; "
              "lane opened ANY for healthy-machine burn; checkpoint "
              "stays machine-local -- screen-finalize round consolidates "
              "faces via fleet channel before judging.")

def load(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)

def dump(p, d):
    s = json.dumps(d, indent=1, ensure_ascii=False).replace("\n", "\r\n")
    with open(p, "w", encoding="utf-8", newline="") as fh:
        fh.write(s)

def edit(d):
    ents = {e["id"]: e for e in d.get("entries", [])}
    g = ents["TRIAL-LABOR-W18-GENERATE"]
    assert g["status"] == "ready", "generate not ready"
    g["status"] = "done"
    g["shards"][0]["status"] = "done"
    g["shards"][0]["done_at"] = NOW
    g["shards"][0]["flip_note"] = (
        "r881 bm-c session flip: worker (autofill 16:56:53 pid 43080) "
        "products landed 16:57:43 commit f705f1ccc (692 paired cells "
        "census sha16 724b6135 + grammar ledger row); cmd_generate "
        "exits no-claim by design (W17 family) -- session flip is the "
        "done path (W17-GENERATE done owner bm-a precedent).")
    for i in range(1, 8):
        e = ents["TRIAL-LABOR-W18-SCREEN-SHARD-%d" % i]
        assert e["lane_owner"] == "bm-c", "shard %d lane not bm-c" % i
        e["lane_owner"] = "ANY"
        e["lane_relay_at"] = NOW
        e["lane_relay_note"] = RELAY_NOTE
    d["updated_at"] = NOW

d1, d2 = load(SHARED), load(LANE)
edit(d1)
edit(d2)
dump(SHARED, d1)
dump(LANE, d2)
# post-verify: both parse; edited fields identical across faces
c1, c2 = load(SHARED), load(LANE)
e1 = {e["id"]: e for e in c1["entries"]}
e2 = {e["id"]: e for e in c2["entries"]}
assert e1["TRIAL-LABOR-W18-GENERATE"]["status"] == "done"
assert e2["TRIAL-LABOR-W18-GENERATE"]["status"] == "done"
for i in range(1, 8):
    k = "TRIAL-LABOR-W18-SCREEN-SHARD-%d" % i
    assert e1[k]["lane_owner"] == "ANY" and e2[k]["lane_owner"] == "ANY"
assert e1["TRIAL-LABOR-W18-SCREEN-SHARD-0"]["lane_owner"] == "bm-c"
assert e2["TRIAL-LABOR-W18-SCREEN-SHARD-0"]["lane_owner"] == "bm-c"
print("pool edit OK: generate=done both faces, shards1-7 lane=ANY both "
      "faces, shard0 lane=bm-c preserved")
