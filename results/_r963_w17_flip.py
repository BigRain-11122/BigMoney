# r963 observation-round harvest flip executor (bm-a, 2026-10-10 22:2x)
# Law anchors: r309 (entry+shard double flip, three-way reconciliation, no cross-round left-over),
# r497 (closed+ok claim = harvest evidence), r488 (burn-without-flip = ghost ready face),
# r311/r180 (done row: owner_since bump to flip moment, done_at = completion),
# r527 pre-check done: entry-layer governance fields ABSENT (park_note/parked_per/unfreeze_gate)
#                     -> no two-layer conflict, single-machine flip is legal (r309 observation-round executor).
# Target: TRIAL-LABOR-W17-SCREEN-SHARD-7 / shard w17-screen-7of8
#   worker claim state=closed outcome=ok closed_at=2026-10-10T21:49:25+08:00
#   product results/trial_labor_w17/checkpoint/screen_shard_7of8.jsonl = 198 lines == all-sibling parity
#   r962 control plane died (21:53 push-rebase crash) before the pool-side harvest flip.
import json, os, sys

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
POOL = os.path.join(REPO, "results", "runnable_pool.json")
CLAIM = os.path.join(REPO, "results", "pool_claims", "TRIAL-LABOR-W17-SCREEN-SHARD-7",
                     "w17-screen-7of8.bm-a.json")
CKPT = os.path.join(REPO, "results", "trial_labor_w17", "checkpoint", "screen_shard_7of8.jsonl")
ENTRY_ID = "TRIAL-LABOR-W17-SCREEN-SHARD-7"
SHARD_KEY = "w17-screen-7of8"

# --- gate 1: worker claim closed+ok
c = json.load(open(CLAIM, encoding="utf-8"))
assert c.get("state") == "closed" and c.get("outcome") == "ok", ("claim not closed+ok", c)
closed_at = c.get("closed_at") or c.get("heartbeat")
assert closed_at and closed_at.startswith("2026-10-10T"), ("bad closed_at", closed_at)
done_stamp = closed_at[:19].replace("T", " ")  # sibling space format e.g. "2026-10-10 21:49:25"
print("gate1 claim: closed+ok at", closed_at)

# --- gate 2: product presence + family parity (all 8 shards 198 lines)
counts = {}
for i in range(8):
    p = os.path.join(REPO, "results", "trial_labor_w17", "checkpoint", "screen_shard_%dof8.jsonl" % i)
    assert os.path.exists(p), "missing ckpt %d" % i
    counts[i] = sum(1 for _ in open(p, encoding="utf-8"))
assert len(set(counts.values())) == 1, ("parity fail", counts)
print("gate2 product: 8/8 ckpts, parity", counts[0], "lines each")

# --- gate 3: pool face pre-state (entry+shard ready, owner bm-a, no governance hold)
raw = open(POOL, "rb").read()
assert raw.count(b"\r\n") == raw.count(b"\n"), "pool not pure CRLF"
d = json.loads(raw.decode("utf-8"))
ents = d.get("entries", [])
e = [x for x in ents if x.get("id") == ENTRY_ID]
assert len(e) == 1, "entry not unique"
e = e[0]
assert e.get("status") == "ready", ("entry not ready", e.get("status"))
assert e.get("lane_owner") in ("bm-a", None, "", "ANY"), ("lane", e.get("lane_owner"))
for gk in ("park_note", "parked_per", "unfreeze_gate"):
    assert gk not in e, "governance hold present: " + gk
sh = [s for s in e.get("shards", []) if s.get("key") == SHARD_KEY]
assert len(sh) == 1, "shard not unique"
sh = sh[0]
assert sh.get("status") == "ready", ("shard not ready", sh.get("status"))
assert sh.get("owner") == "bm-a", ("owner", sh.get("owner"))
print("gate3 pool: entry+shard ready, owner bm-a, governance clean")

# --- flip: entry.status + shard.status -> done; done_at = claim completion; owner_since = flip moment
import datetime
flip_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
e["status"] = "done"
sh["status"] = "done"
sh["done_at"] = done_stamp
sh["owner_since"] = flip_now  # r311: done row must be newest same-key base at settle

out = json.dumps(d, ensure_ascii=False, indent=1)
data = out.replace("\n", "\r\n").encode("utf-8")
with open(POOL, "wb") as f:
    f.write(data)

# --- post assertions: parse OK, counts unchanged, only intended deltas
d2 = json.loads(open(POOL, "rb").read().decode("utf-8"))
assert len(d2["entries"]) == len(ents), "entry count changed"
e2 = [x for x in d2["entries"] if x.get("id") == ENTRY_ID][0]
sh2 = [s for s in e2["shards"] if s.get("key") == SHARD_KEY][0]
assert e2["status"] == "done" and sh2["status"] == "done"
assert sh2["done_at"] == done_stamp
for other in [x for x in d2["entries"] if x.get("id") != ENTRY_ID]:
    if other.get("id") == "TRIAL-LABOR-W17-JUDGE":
        assert other.get("status") == "ready", "JUDGE touched!"
sib = [x for x in d2["entries"] if x.get("id") == "TRIAL-LABOR-W17-SCREEN-SHARD-6"][0]
ssh = sib["shards"][0]
assert ssh["status"] == "done" and ssh["done_at"] == "2026-10-10 21:40:04", "SHARD-6 disturbed"
print("FLIPPED: %s entry+shard -> done (done_at=%s, owner_since=%s)" % (ENTRY_ID, done_stamp, flip_now))
print("post: entries=%d, JUDGE untouched ready, SHARD-6 sibling intact" % len(d2["entries"]))
