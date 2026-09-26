# R279 bm-a rebase collision resolver (skill bigmoney-conflict-resolve, r203/R208 family)
# Context: pull --rebase replay of dead-R278 commit b23a1179 (autofill claim fusion-nav-0of1
# owner=bm-a 23:50:03) vs origin 7e78f7f5 (bm-b claim same shard 00:00:04 = stale-read claim,
# bm-a claim unpushed because R278 was killed at 25min budget pre-S7-push).
# Census proof (pre-resolution): both blobs 50 entries, entry-set diff EMPTY, status diff EMPTY
# -> ONLY differing field = FUSION-P1-NAV shards[0].owner (bm-a vs bm-b).
# Ruling: fleet/README.md S4 later-yields -- bm-a claimed first (23:50:03 < 00:00:04) AND
# completed the batch (products landed 23:52:59, adopted cf16fa35). Take theirs (=b23a1179
# pool face, owner bm-a). Ground-truth final state lands post-rebase as r244 harvest flip
# (entry+shard done + harvest_note). Zero loss by census proof.
import json
import subprocess
import sys

PATH = "results/runnable_pool.json"

def pool_bytes(rev):
    return subprocess.run(["git", "show", f"{rev}:{PATH}"], capture_output=True).stdout

def census(raw):
    d = json.loads(raw.decode("utf-8-sig"))
    return ({e["id"]: e.get("status") for e in d["entries"]}, d)

ours = pool_bytes("7e78f7f5")   # origin side (bm-b claim)
theirs = pool_bytes("b23a1179")  # replayed commit (bm-a claim)

co, do = census(ours)
ct, dt = census(theirs)
assert co == ct, "entry census differs -- abort, manual adjudication required"
assert len(co) == 50, f"unexpected entry count {len(co)}"

# field-level proof: only FUSION-P1-NAV shard owner/owner_since differ
diffs = []
for eo, et in zip(do["entries"], dt["entries"]):
    assert eo["id"] == et["id"]
    if eo != et:
        diffs.append(eo["id"])
assert diffs == ["FUSION-P1-NAV"], f"unexpected diff set: {diffs}"

with open(PATH, "wb") as f:
    f.write(theirs)
d = json.loads(open(PATH, "rb").read().decode("utf-8-sig"))
fe = [e for e in d["entries"] if e["id"] == "FUSION-P1-NAV"][0]
assert fe["shards"][0]["owner"] == "bm-a"
assert isinstance(fe["shards"][0], dict)
print("resolve ok: pool byte-identical to b23a1179 face; only-face proof FUSION-P1-NAV owner=bm-a (first-claim S4); bm-b 00:00:04 claim = stale-read void (its own r280 pitfall family)")
sys.exit(0)
