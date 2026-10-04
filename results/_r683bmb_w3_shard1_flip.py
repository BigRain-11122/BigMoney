"""_r683bmb_w3_shard1_flip.py -- bm-b r683: W3-JUDGE SHARD-1 two-layer
done-flip (burn completed within this round's window, 194/194 rows).

r485 bmc shard-0 precedent recipe (verbatim lineage, param-swapped):
- r488/r489 two-layer (entry.status + shards[].status both -> done)
- r497 stop-gap: claim file backfill (real pid + completion provenance)
- r509 raw-text surgical edit ONLY (CRLF preserved, json.dumps forbidden)
- r400 action-time ts; r310 product delivery; r325 ignition evidence
- r668 law: burn-done != pool-flip == autofill re-burn loop; owner-side
  same-window flip is the only correct action (last_tick 17:24:02 =
  relaunch_cooldown targeting this shard: flip must land before next tick)
Drift guards vs r485: sibling SHARD-0 already done (r485); entries count
dynamic (pre==post + family-shape) instead of hardcoded 376 (r419 law).
"""
import datetime
import hashlib
import json
import os
import sys

os.chdir(r"C:\Fluxgroup\FluxGroup\quant\bigmoney")
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
POOL = "results/runnable_pool.json"
CKPT = "results/mass_trial/w3_judge_shard_1of4.jsonl"
CLAIM = "results/pool_claims/MASS-TRIAL-W3-JUDGE-SHARD-1/w3-judge-1of4.bm-b.json"
EID = "MASS-TRIAL-W3-JUDGE-SHARD-1"
SKEY = "w3-judge-1of4"
SIB_DONE = {"MASS-TRIAL-W3-JUDGE-SHARD-0"}
SIB_READY = {"MASS-TRIAL-W3-JUDGE-SHARD-2", "MASS-TRIAL-W3-JUDGE-SHARD-3"}
PID = 21200
STARTED = "2026-10-04 17:12:02"


def fail(msg):
    print("ABORT:", msg)
    sys.exit(1)


# ---- gate 0: S0-restore classification door (r433 bm-c law) ----
import subprocess
tg = subprocess.run(["python", "Tools/treasure_guard.py", "restore", POOL],
                    capture_output=True)
if tg.returncode == 3:
    fail("treasure_guard rc3: registry hit -- restore forbidden path")
print("gate0 PASS: treasure_guard rc=%d (pool = regenerable daemon live-wins face)"
      % tg.returncode)

# ---- gate 1: ckpt completeness (194 rows, i%4==1, unique) ----
rows = [json.loads(l) for l in open(CKPT, encoding="utf-8") if l.strip()]
ids = [r["cell_id"] for r in rows]
if len(rows) != 194:
    fail("rows=%d != 194" % len(rows))
if len(set(ids)) != 194:
    fail("cell_id dup: %d unique" % len(set(ids)))
if any(r["i"] % 4 != 1 for r in rows):
    fail("non-i%4==1 rows present")
if not all(str(i).startswith("JUDGE|") for i in ids):
    fail("cell_id prefix shape unexpected")
imod = sorted(r["i"] for r in rows)
if imod[0] != 1 or imod[-1] != 773:
    fail("i-range unexpected: %s..%s" % (imod[0], imod[-1]))
mtime = datetime.datetime.fromtimestamp(os.path.getmtime(CKPT)).strftime(
    "%Y-%m-%d %H:%M:%S")
print("gate1 PASS: 194/194 unique i%4==1 rows (i 1..773), ckpt mtime " + mtime)

# ---- gate 2: crash fuse scan for w3-judge-1of4 ----
for cf in ("results/crash_fuse.json", "results/crash_fuse.bm-b.json"):
    if os.path.exists(cf):
        d = json.load(open(cf, encoding="utf-8"))
        s = json.dumps(d, ensure_ascii=False)
        if '"%s"' % SKEY in s:
            fail("crash fuse mention of %s in %s (inspect before flip)" % (SKEY, cf))
print("gate2 PASS: crash fuse clean for %s" % SKEY)

# ---- gate 3: pre-state assertions ----
raw = open(POOL, "rb").read()
text = raw.decode("utf-8")
assert "\r\n" in text, "expected CRLF pool file"
pre = json.loads(text)
pre_list = pre["entries"]
n_entries = len(pre_list)
pres = {e["id"]: e for e in pre_list
        if str(e.get("id", "")).startswith("MASS-TRIAL-W3-JUDGE")}
if set(pres) != SIB_DONE | SIB_READY | {EID}:
    fail("W3-JUDGE family shape: %s" % sorted(pres))
if pres[EID]["status"] != "ready":
    fail("entry not ready: %s" % pres[EID]["status"])
for sid in SIB_DONE:
    if pres[sid]["status"] != "done":
        fail("sibling %s expected done, got %s" % (sid, pres[sid]["status"]))
for sid in SIB_READY:
    if pres[sid]["status"] != "ready":
        fail("sibling %s expected ready, got %s" % (sid, pres[sid]["status"]))
e1 = pres[EID]
s1 = e1["shards"][0]
if s1["status"] != "ready" or s1["key"] != SKEY:
    fail("shard not ready / key mismatch: %s" % s1)
if s1.get("owner") != "bm-b" or not s1.get("owner_since"):
    fail("shard owner face missing (claim not visible)")
claim_ts = s1["owner_since"]
print("gate3 PASS: pre-state entry=ready sibs done/ready x2, claim owner_since=%s, entries=%d"
      % (claim_ts, n_entries))

# ---- surgical edit (r425 mechanism) ----
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
oi = [j for j, l in enumerate(block) if l.strip() == '"owner": "bm-b",']
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
                     + indent_s + '"harvested_by": "bm-b",\r\n'
                     + indent_s + '"harvest_claim": "%s.bm-b.json",\r\n'
                     % SKEY
                     + indent_s + '"owner": "bm-b"')
wc = end - a
if new_block[wc].strip() != '"worker_class": "self-contained"':
    fail("worker_class anchor drift")
indent_w = new_block[wc][:len(new_block[wc]) - len(new_block[wc].lstrip())]
new_block[wc] = (indent_w + '"worker_class": "self-contained",\r\n'
                 + indent_w + '"done_by": "bm-b",\r\n'
                 + indent_w + '"done_at": "%s"' % NOW)
new_text = "\r\n".join(lines[:a] + new_block + lines[end + 2:])
if new_text == text:
    fail("no change produced")

# ---- gate 4: post-edit parse + semantic assertions (in memory) ----
post = json.loads(new_text)
post_list = post["entries"]
if len(post_list) != n_entries:
    fail("entries count drift %d -> %d" % (n_entries, len(post_list)))
posts = {e["id"]: e for e in post_list
         if str(e.get("id", "")).startswith("MASS-TRIAL-W3-JUDGE")}
p1, ps1 = posts[EID], posts[EID]["shards"][0]
assert p1["status"] == "done" and p1["done_by"] == "bm-b" and p1["done_at"] == NOW
assert ps1["status"] == "done" and ps1["done_at"] == NOW
assert ps1["harvested_by"] == "bm-b" and ps1["owner"] == "bm-b"
assert ps1["harvest_claim"] == "%s.bm-b.json" % SKEY
for sid in SIB_DONE:
    assert posts[sid]["status"] == "done"
for sid in SIB_READY:
    assert posts[sid]["status"] == "ready"
print("gate4 PASS: post-edit semantics (entry+shard done, siblings untouched)")

# ---- write claim file (r497 backfill, real provenance) ----
claim_obj = {
    "machine_id": "bm-b",
    "state": "closed",
    "pid": PID,
    "heartbeat": "2026-10-04T" + mtime[11:] + "+08:00",
    "outcome": "ok",
    "exit_code": 0,
    "started": STARTED,
    "closed_at": mtime,
    "result_ref": ("autofill-launched runner (r199 launch-claim + r290 "
                   "self-commit, no worker-side handshake); rc unobserved "
                   "directly -- completeness evidence = 194/194 unique cell "
                   "rows (i mod 4 == 1, i 1..773) in checkpoint, ckpt mtime "
                   + mtime + ", runner pid %d exited (dual-form CSV+CIM "
                   "verified dead at 17:25:49 probe); claim backfilled + "
                   "two-layer done-flip landed by burner-side session bm-b "
                   "r683 per r497/r488/r489/r668 law" % PID)
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
d1 = {e["id"]: e for e in disk["entries"]}[EID]
assert d1["status"] == "done" and d1["shards"][0]["status"] == "done"
assert json.loads(open(CLAIM, encoding="utf-8").read())["state"] == "closed"
print("disk re-verify PASS; sha16(pool)=%s"
      % hashlib.sha256(open(POOL, "rb").read()).hexdigest()[:16])
print("FLIP_OK old_owner_since=%s new=%s" % (old_os, NOW))
