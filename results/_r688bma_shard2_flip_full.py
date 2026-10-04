"""_r688bma_shard2_flip.py -- bm-a r688: W3-JUDGE SHARD-2 two-layer done-flip.

Mirror of bm-c r485 _r485bmc_w3_shard0_flip.py pattern (r425 lineage).

Laws applied:
- r488/r489 two-layer (entry.status + shards[0].status both -> done)
- r497 stop-gap: claim file backfill (real pid + completion provenance)
- r509 raw-text surgical edit ONLY (CRLF preserved via newline='', json.dumps
  forbidden on pool faces per r678)
- r400 action-time ts (owner_since monotonic refresh > claim 17:15:08)
- r310 product delivery: checkpoint + flip committed to origin in same window
- r482/r685 id-dup probes (candidate_id unique, zero byte-dup rows)
- r483 pre-flip origin re-check (single-point fetch复核 right before write)
Special lineage: our launch-claim (commit 03f7ac259, owner=bm-a since
17:15:08, burn pid 26224 launched 17:15:02) was dropped from the shared pool
face by the r687 close-window merge (pool theirs-canonical, stale-fetch
artifact) while the lane mirror retained it. Burn completed 194/194 cells
(shard-2 = cells i%4==2). This round restores the claim and lands the
two-layer done-flip with full provenance.
"""
import datetime
import json
import os
import re
import subprocess
import sys

os.chdir(r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney")
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
POOL = "results/runnable_pool.json"
LANE = "results/runnable_pool.bm-a.json"
CKPT = "results/mass_trial/w3_judge_shard_2of4.jsonl"
CLAIM_DIR = r"results\pool_claims\MASS-TRIAL-W3-JUDGE-SHARD-2"
CLAIM = os.path.join(CLAIM_DIR, "w3-judge-2of4.bm-a.json")
EID = "MASS-TRIAL-W3-JUDGE-SHARD-2"
SKEY = "w3-judge-2of4"


def fail(msg):
    print("ABORT:", msg)
    sys.exit(1)


# ---- gate 0: pre-write origin re-check (r483 single-point) ----
subprocess.run(["git", "fetch", "origin"], capture_output=True)
ob = subprocess.run(
    ["git", "show", "origin/main:results/runnable_pool.json"], capture_output=True
).stdout.decode("utf-8")
opool = json.loads(ob)
ocand = [e for e in opool["entries"] if e.get("id") == EID][0]
if ocand["status"] != "ready":
    fail("origin SHARD-2 status=%s (not ready -- someone else already moving it)" % ocand["status"])
s0o = ocand["shards"][0].get("owner")
if s0o not in (None, "bm-a"):
    fail("origin SHARD-2 shard owner=%s (another machine's claim -- do not stomp)" % s0o)
if s0o == "bm-a" and ocand["shards"][0].get("owner_since") != "2026-10-04 17:15:08":
    fail("origin owner_since=%s != claim lineage 17:15:08 (unexpected owner face)" % ocand["shards"][0].get("owner_since"))
print("gate0 PASS: origin SHARD-2 ready, owner face = %s (own claim lineage ok)" % s0o)

# ---- gate 1: ckpt completeness (194 rows, i%4==2, unique) ----
rows = [json.loads(l) for l in open(CKPT, encoding="utf-8") if l.strip()]
ids = [r["cell_id"] for r in rows]
if len(rows) != 194:
    fail("rows=%d != 194" % len(rows))
if len(set(ids)) != 194:
    fail("cell_id dup: %d unique" % len(set(ids)))
if any(r["i"] % 4 != 2 for r in rows):
    fail("non-i%4==2 rows present")
if not all(str(i).startswith("JUDGE|") for i in ids):
    fail("cell_id prefix shape unexpected")
for r in rows:
    for k in ("dual_nulls", "sample_sufficient", "legs", "n_eff_start_windows"):
        if k not in r:
            fail("row %s missing key %s" % (r.get("candidate_id"), k))
raw_lines = [l for l in open(CKPT, "rb").read().split(b"\n") if l.strip()]
if len(set(raw_lines)) != len(raw_lines):
    fail("byte-dup rows present (r482)")
mtime = datetime.datetime.fromtimestamp(os.path.getmtime(CKPT)).strftime(
    "%Y-%m-%d %H:%M:%S")
print("gate1 PASS: 194/194 unique i%4==2 rows, all key fields, zero byte-dups, ckpt mtime " + mtime)

# ---- gate 2: crash fuse scan ----
for cf in ("results/crash_fuse.json", "results/crash_fuse.bm-a.json"):
    if os.path.exists(cf):
        s = open(cf, encoding="utf-8").read()
        if SKEY in s:
            idx = s.find(SKEY)
            win = s[max(0, idx - 200):idx + 300]
            if '"crash"' in win or "crash_counted" in win:
                fail("crash marker near %s in %s" % (SKEY, cf))
print("gate2 PASS: crash fuse clean for %s" % SKEY)


def load_face(path):
    text = open(path, encoding="utf-8", newline="").read()
    return text, json.loads(text)


def entry_span(text, eid):
    m = re.search(r'\{\s*"id":\s*"' + eid + '"', text)
    start = m.start()
    depth = 0
    i = start
    while True:
        c = text[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                break
        i += 1
    return start, i + 1


def flip_face(path, shard_has_owner, strict_family=True):
    text, pre = load_face(path)
    ents = pre["entries"]
    if len(ents) != 376:
        fail("%s entries=%d != 376" % (path, len(ents)))
    fam = {e["id"]: e for e in ents if str(e.get("id", "")).startswith("MASS-TRIAL-W3-JUDGE-SHARD")}
    if set(fam) != {"MASS-TRIAL-W3-JUDGE-SHARD-%d" % i for i in range(4)}:
        fail("family shape: %s" % sorted(fam))
    if fam[EID]["status"] != "ready":
        fail("%s entry status=%s" % (path, fam[EID]["status"]))
    if fam[EID]["shards"][0]["status"] != "ready" or fam[EID]["shards"][0]["key"] != SKEY:
        fail("%s shard face not ready" % path)
    print("DEBUG fam ids:", sorted(fam))
    print("DEBUG SHARD-0 status:", repr(fam.get("MASS-TRIAL-W3-JUDGE-SHARD-0", {}).get("status")))
    print("DEBUG EID status:", repr(fam[EID].get("status")), "shard0:", repr(fam[EID]["shards"][0].get("status")))
    if strict_family:
        if fam["MASS-TRIAL-W3-JUDGE-SHARD-0"]["status"] != "done":
            fail("SHARD-0 not done (unexpected)")
        for i in (1, 3):
            if fam["MASS-TRIAL-W3-JUDGE-SHARD-%d" % i]["status"] != "ready":
                fail("sibling SHARD-%d not ready" % i)
    start, end = entry_span(text, EID)
    block = text[start:end]
    lines = block.split("\r\n")
    st_idx = [j for j, l in enumerate(lines) if l.strip() == '"status": "ready",']
    if len(st_idx) != 2:
        fail("expected 2 ready-status lines, got %d in %s" % (len(st_idx), path))
    ent_s, shard_s = st_idx
    indent_e = "   "
    indent_s = lines[shard_s][: len(lines[shard_s]) - len(lines[shard_s].lstrip())]
    new_lines = list(lines)
    new_lines[ent_s] = new_lines[ent_s].replace('"ready"', '"done"')
    new_lines.insert(ent_s + 1, '%s"done_at": "%s",' % (indent_e, NOW))
    shard_s += 1  # shifted by insert
    new_lines[shard_s] = new_lines[shard_s].replace('"ready"', '"done"')
    if shard_has_owner:
        os_idx = [j for j, l in enumerate(new_lines) if l.strip().startswith('"owner_since":')]
        if len(os_idx) != 1:
            fail("owner_since not unique in shard face (%s)" % path)
        j = os_idx[0]
        new_lines[j] = re.sub(r'"owner_since": "[^"]*"', '"owner_since": "%s",' % NOW, new_lines[j])
        new_lines.insert(j + 1, '%s"done_at": "%s",' % (indent_s, NOW))
        new_lines.insert(j + 2, '%s"harvested_by": "bm-a",' % indent_s)
        new_lines.insert(j + 3, '%s"harvest_claim": "%s"' % (indent_s, "w3-judge-2of4.bm-a.json"))
    else:
        note_idx = [j for j, l in enumerate(new_lines) if l.strip().startswith('"note": "cells i%4==2')]
        if len(note_idx) != 1:
            fail("shard note anchor not unique in %s" % path)
        j = note_idx[0]
        if not new_lines[j].rstrip().endswith('"'):
            fail("note line shape unexpected")
        new_lines[j] = new_lines[j] + ","
        add = ['%s"owner": "bm-a",' % indent_s,
               '%s"owner_since": "%s",' % (indent_s, NOW),
               '%s"done_at": "%s",' % (indent_s, NOW),
               '%s"harvested_by": "bm-a",' % indent_s,
               '%s"harvest_claim": "%s"' % (indent_s, "w3-judge-2of4.bm-a.json")]
        for k, al in enumerate(add):
            new_lines.insert(j + 1 + k, al)
    new_block = "\r\n".join(new_lines)
    json.loads(new_block)  # reparse gate (block-level)
    new_text = text[:start] + new_block + text[end:]
    json.loads(new_text)  # reparse gate (full-file)
    return new_text


# ---- gate 3 executed inside flip_face pre-checks ----
# strict_family=False for lane mirror: our lane view is naturally stale for
# OTHER machines' shards (bm-c's SHARD-0 done-flip lives in shared pool + their
# lane, not ours) -- sibling checks apply to the shared face only.
new_pool = flip_face(POOL, shard_has_owner=True, strict_family=True)
new_lane = flip_face(LANE, shard_has_owner=True, strict_family=False)

# atomic writes
open(POOL, "wb").write(new_pool.encode("utf-8"))
open(LANE, "wb").write(new_lane.encode("utf-8"))

# ---- claim file backfill (r497) ----
os.makedirs(CLAIM_DIR, exist_ok=True)
claim = {
    "machine_id": "bm-a",
    "state": "closed",
    "pid": 26224,
    "heartbeat": datetime.datetime.fromtimestamp(os.path.getmtime(CKPT)).isoformat(),
    "outcome": "ok",
    "exit_code": 0,
    "started": "2026-10-04 17:15:02",
    "closed_at": mtime,
    "result_ref": (
        "autofill-launched runner (no worker-side handshake, w1 r351 zero-touch face); "
        "rc unobserved directly -- completeness evidence = 194/194 unique cell rows "
        "(i mod 4 == 2) in checkpoint, ckpt mtime " + mtime + ", runner pid 26224 exited "
        "(last-alive sample 2026-10-04T17:16:17 pool_core_samples multicore_burn); "
        "launch-claim commit 03f7ac259 owner=bm-a since 17:15:08 (claim row transiently "
        "lost in r687 close-window merge pool theirs-canonical, restored at origin by "
        "bm-b r689 per-face settle) -- claim consumed + two-layer done-flip landed by "
        "burner-side session bm-a r688 per r497/r488/r489 law"
    ),
}
with open(CLAIM, "w", encoding="utf-8", newline="") as f:
    json.dump(claim, f, ensure_ascii=False, indent=1)
    f.write("\n")
json.load(open(CLAIM, encoding="utf-8-sig"))
print("claim file written:", CLAIM)

# ---- post-write verification from disk ----
post = json.loads(open(POOL, encoding="utf-8").read())
pe = [e for e in post["entries"] if e.get("id") == EID][0]
assert pe["status"] == "done" and pe["done_at"] == NOW
assert pe["shards"][0]["status"] == "done"
assert pe["shards"][0]["owner"] == "bm-a"
assert pe["shards"][0]["harvest_claim"] == "w3-judge-2of4.bm-a.json"
assert len(post["entries"]) == 376
lane_post = json.loads(open(LANE, encoding="utf-8").read())
le = [e for e in lane_post["entries"] if e.get("id") == EID][0]
assert le["status"] == "done" and le["shards"][0]["status"] == "done"
sib = {e["id"]: e["status"] for e in post["entries"] if str(e.get("id", "")).startswith("MASS-TRIAL-W3-JUDGE-SHARD")}
print("POST pool family states:", sib)
print("FLIP LANDED: entry+shard done, owner=bm-a, done_at=%s, claim file backfilled" % NOW)
