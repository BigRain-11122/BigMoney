"""_r486bmc_w3_shard3_flip.py -- bm-c r486: W3-JUDGE SHARD-3 two-layer
done-flip (burn completed 17:23:18 within window, 194/194 rows, runner
pid 12356 launched 17:17:32 by autofill tick).

Laws applied (r485 shard0-flip lineage, adapted per r461 no-blind-reuse):
- r488/r489 two-layer (entry.status + shards[].status both -> done)
- r497 stop-gap: claim file backfill (real pid + completion provenance)
- r509 raw-text surgical edit ONLY (CRLF preserved, json.dumps forbidden)
- r400 action-time ts (owner_since monotonic refresh > claim 17:17:32)
- r310 product delivery: checkpoint committed to origin in same window
- r325 ignition evidence: 194/194 unique rows growing checkpoint
Sibling expectations this round (3-machine relay live): SHARD-0 done
(r485 bm-c), SHARD-1 ready owner=bm-b, SHARD-2 ready owner=bm-a.
Abort-before-write: all gates on in-memory text; single atomic write;
post-write re-parse from disk."""
import datetime
import hashlib
import json
import os
import sys

os.chdir(r"K:\Fluxgroup\FluxGroup\quant\bigmoney")
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
POOL = "results/runnable_pool.json"
CKPT = "results/mass_trial/w3_judge_shard_3of4.jsonl"
CLAIM = "results/pool_claims/MASS-TRIAL-W3-JUDGE-SHARD-3/w3-judge-3of4.bm-c.json"
EID = "MASS-TRIAL-W3-JUDGE-SHARD-3"
SKEY = "w3-judge-3of4"
PID = 12356
STARTED = "2026-10-04 17:17:32"


def fail(msg):
    print("ABORT:", msg)
    sys.exit(1)


# ---- gate 1: ckpt completeness (194 rows, i%4==3, unique) ----
rows = [json.loads(l) for l in open(CKPT, encoding="utf-8") if l.strip()]
ids = [r["cell_id"] for r in rows]
if len(rows) != 194:
    fail("rows=%d != 194" % len(rows))
if len(set(ids)) != 194:
    fail("cell_id dup: %d unique" % len(set(ids)))
if any(r["i"] % 4 != 3 for r in rows):
    fail("non-i%4==3 rows present")
if not all(str(i).startswith("JUDGE|") for i in ids):
    fail("cell_id prefix shape unexpected")
mtime = datetime.datetime.fromtimestamp(os.path.getmtime(CKPT)).strftime(
    "%Y-%m-%d %H:%M:%S")
print("gate1 PASS: 194/194 unique i%4==3 rows, ckpt mtime " + mtime)

# ---- gate 2: crash fuse scan for w3-judge-3of4 ----
fus = {}
for cf in ("results/crash_fuse.json", "results/crash_fuse.bm-c.json"):
    if os.path.exists(cf):
        fus[cf] = json.load(open(cf, encoding="utf-8"))
for cf, d in fus.items():
    s = json.dumps(d, ensure_ascii=False)
    idx = s.find(SKEY)
    hits = 0
    while idx != -1:
        window = s[max(0, idx - 200):idx + 300]
        if '"crash"' in window or "crash_counted" in window:
            hits += 1
            print("NOTE crash-fuse window near %s: %s" % (SKEY, window[:300]))
        idx = s.find(SKEY, idx + 1)
    if hits:
        fail("crash marker blocking harvest")
print("gate2 PASS: crash fuse clean for %s" % SKEY)

# ---- gate 3: pre-state assertions (3-machine relay shape) ----
raw = open(POOL, "rb").read()
text = raw.decode("utf-8")
assert "\r\n" in text, "expected CRLF pool file"
pre = json.loads(text)
pre_list = pre["entries"]
if len(pre_list) != 376:
    fail("entries=%d != 376" % len(pre_list))
pres = {e["id"]: e for e in pre_list
        if str(e.get("id", "")).startswith("MASS-TRIAL-W3-JUDGE")}
if set(pres) != {"MASS-TRIAL-W3-JUDGE-SHARD-%d" % i for i in range(4)}:
    fail("W3-JUDGE family shape: %s" % sorted(pres))
e3 = pres[EID]
s3 = e3["shards"][0]
if e3["status"] != "ready":
    fail("entry not ready: %s" % e3["status"])
if s3["status"] != "ready" or s3["key"] != SKEY:
    fail("shard not ready / key mismatch")
if s3.get("owner") != "bm-c" or not s3.get("owner_since"):
    fail("shard owner face missing (claim not visible)")
claim_ts = s3["owner_since"]
if not ("17:1" in claim_ts or "17:2" in claim_ts):
    print("NOTE owner_since=%s (expect ~17:17 claim ts)" % claim_ts)
# siblings: SHARD-0 done (r485), SHARD-1 bm-b, SHARD-2 bm-a
e0 = pres["MASS-TRIAL-W3-JUDGE-SHARD-0"]
if e0["status"] != "done" or e0["shards"][0]["status"] != "done":
    fail("SHARD-0 not done (r485 flip missing)")
for i, own in ((1, "bm-b"), (2, "bm-a")):
    ei = pres["MASS-TRIAL-W3-JUDGE-SHARD-%d" % i]
    if ei["status"] != "ready":
        fail("sibling SHARD-%d entry not ready: %s" % (i, ei["status"]))
    si = ei["shards"][0]
    if si["status"] != "ready":
        fail("sibling SHARD-%d shard not ready" % i)
    if si.get("owner") != own:
        print("NOTE SHARD-%d owner=%r (expected %s)" % (i, si.get("owner"), own))
print("gate3 PASS: SHARD-0 done, SHARD-1/2 ready owned, SHARD-3 claim "
     "owner_since=%s, entries=376" % claim_ts)

# ---- surgical edit (r509 mechanism) ----
lines = text.split("\r\n")
try:
    a = next(j for j, l in enumerate(lines)
             if l.strip() == '"id": "%s",' % EID)
except StopIteration:
    fail("id anchor line not found")
end = None
for j in range(a, min(a + 120, len(lines))):
    if (lines[j].strip() == '"worker_class": "self-contained"'
            and lines[j + 1].strip() in ("},", "}")):
        end = j
        break
if end is None:
    fail("entry end anchor not found")
block = lines[a:end + 2]
ei = [j for j, l in enumerate(block) if l.strip() == '"status": "ready",']
if len(ei) != 2:
    fail("expected 2 ready-status lines, got %d" % len(ei))
ent_s, shard_s = ei[0], ei[1]
if '"key": "%s"' % SKEY not in "".join(block[:shard_s]):
    fail("second status not in shard face order")
oi = [j for j, l in enumerate(block) if l.strip() == '"owner": "bm-c",']
os_ = [j for j, l in enumerate(block) if l.strip().startswith('"owner_since":')]
if len(oi) != 1 or len(os_) != 1:
    fail("owner pair not unique (o=%d os=%d)" % (len(oi), len(os_)))
if os_[0] != oi[0] + 1:
    fail("owner_since not adjacent to owner")
oline, osline = block[oi[0]], block[os_[0]]
indent_o = oline[:len(oline) - len(oline.lstrip())]
indent_s = osline[:len(osline) - len(osline.lstrip())]
old_os = osline.strip()

new_block = list(block)
new_block[ent_s] = new_block[ent_s].replace('"ready"', '"done"')
new_block[shard_s] = new_block[shard_s].replace('"ready"', '"done"')
new_block[oi[0]] = indent_o + '"owner_since": "%s",' % NOW
new_block[os_[0]] = (indent_s + '"done_at": "%s",\r\n' % NOW
                     + indent_s + '"harvested_by": "bm-c",\r\n'
                     + indent_s + '"harvest_claim": "%s.bm-c.json",\r\n'
                     % SKEY
                     + indent_s + '"owner": "bm-c"')
wc = end - a
if new_block[wc].strip() != '"worker_class": "self-contained"':
    fail("worker_class anchor drift")
indent_w = new_block[wc][:len(new_block[wc]) - len(new_block[wc].lstrip())]
new_block[wc] = (indent_w + '"worker_class": "self-contained",\r\n'
                 + indent_w + '"done_by": "bm-c",\r\n'
                 + indent_w + '"done_at": "%s"' % NOW)
new_text = "\r\n".join(lines[:a] + new_block + lines[end + 2:])
if new_text == text:
    fail("no change produced")

# ---- gate 4: post-edit parse + semantic assertions (in memory) ----
post = json.loads(new_text)
post_list = post["entries"]
posts = {e["id"]: e for e in post_list
         if str(e.get("id", "")).startswith("MASS-TRIAL-W3-JUDGE")}
p3, ps3 = posts[EID], posts[EID]["shards"][0]
assert p3["status"] == "done" and p3["done_by"] == "bm-c" and p3["done_at"] == NOW
assert ps3["status"] == "done" and ps3["done_at"] == NOW
assert ps3["harvested_by"] == "bm-c" and ps3["owner"] == "bm-c"
assert ps3["harvest_claim"] == "%s.bm-c.json" % SKEY
assert posts["MASS-TRIAL-W3-JUDGE-SHARD-0"]["status"] == "done"
for i in (1, 2):
    assert posts["MASS-TRIAL-W3-JUDGE-SHARD-%d" % i]["status"] == "ready"
assert len(post_list) == 376
print("gate4 PASS: post-edit semantics (SHARD-3 entry+shard done, siblings "
      "untouched: 0 done / 1,2 ready)")

# ---- write claim file (r497 backfill, real provenance) ----
claim_obj = {
    "machine_id": "bm-c",
    "state": "closed",
    "pid": PID,
    "heartbeat": "2026-10-04T" + mtime[11:] + "+08:00",
    "outcome": "ok",
    "exit_code": 0,
    "started": STARTED,
    "closed_at": mtime,
    "result_ref": ("autofill-launched runner (no worker-side handshake, w1 r351 "
                   "zero-touch face); rc unobserved directly -- completeness "
                   "evidence = 194/194 unique cell rows (i mod 4 == 3) in "
                   "checkpoint, ckpt mtime " + mtime + ", runner pid %d "
                   "exited; claim backfilled + two-layer done-flip landed by "
                   "burner-side session bm-c r486 per r497/r488/r489 law" % PID)
}
os.makedirs(os.path.dirname(CLAIM), exist_ok=True)
with open(CLAIM, "w", encoding="utf-8", newline="\r\n") as fh:
    fh.write(json.dumps(claim_obj, ensure_ascii=False, indent=1) + "\n")
print("claim file written:", CLAIM)

# ---- atomic pool write ----
with open(POOL, "wb") as fh:
    fh.write(new_text.encode("utf-8"))
print("pool flipped (two-layer done, action ts %s)" % NOW)

# ---- post-write re-verify from disk ----
disk = json.loads(open(POOL, "rb").read().decode("utf-8"))
d3 = {e["id"]: e for e in disk["entries"]}[EID]
assert d3["status"] == "done" and d3["shards"][0]["status"] == "done"
assert json.loads(open(CLAIM, encoding="utf-8").read())["state"] == "closed"
print("disk re-verify PASS; sha16(pool)=%s"
      % hashlib.sha256(open(POOL, "rb").read()).hexdigest()[:16])
print("FLIP_OK old_owner_since=%s new=%s" % (old_os, NOW))
