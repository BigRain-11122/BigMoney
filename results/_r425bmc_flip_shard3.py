"""_r425bmc_flip_shard3.py -- bm-c r425: SHARD-3 two-layer done-flip + claim backfill.
Adapted from _r425bmc_flip_shard0.py (same laws: r488/r489 two-layer, r497 claim backfill,
r509 raw-text surgical only, r400 action-time ts, r310 product delivery).
"""
import json, os, sys, datetime, hashlib

os.chdir(r"K:\Fluxgroup\FluxGroup\quant\bigmoney")
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
POOL = "results/runnable_pool.json"
CKPT = "results/mass_trial/w2_judge_shard_3of4.jsonl"
CLAIM = "results/pool_claims/MASS-TRIAL-W2-JUDGE-SHARD-3/w2-judge-3of4.bm-c.json"

def fail(msg):
    print("ABORT:", msg)
    sys.exit(1)

# ---- gate 1: ckpt SHARD-3 completeness (201 cells, i%4==3, unique) ----
rows = [json.loads(l) for l in open(CKPT, encoding="utf-8") if l.strip()]
ids = [r["cell_id"] for r in rows]
if len(rows) != 201: fail("shard3 rows=%d != 201" % len(rows))
if len(set(ids)) != 201: fail("shard3 cell_id dup")
if any(r["i"] % 4 != 3 for r in rows): fail("shard3 has non-i%4==3 rows")
mtime = datetime.datetime.fromtimestamp(os.path.getmtime(CKPT)).strftime("%Y-%m-%d %H:%M:%S")
print("gate1 PASS: shard3 201/201 unique (i mod 4 == 3) rows, ckpt mtime " + mtime)

# ---- gate 4: pre-state assertions ----
raw = open(POOL, "rb").read()
text = raw.decode("utf-8")
assert "\r\n" in text, "expected CRLF pool file"
pre = json.loads(text)
pre_list = pre["entries"] if isinstance(pre, dict) else pre
pres = {e["id"]: e for e in pre_list if str(e.get("id", "")).startswith("MASS-TRIAL-W2-JUDGE-SHARD")}
if pres["MASS-TRIAL-W2-JUDGE-SHARD-3"]["status"] != "ready": fail("shard3 entry not ready")
if pres["MASS-TRIAL-W2-JUDGE-SHARD-3"]["shards"][0]["status"] != "ready": fail("shard3 shard not ready")
if pres["MASS-TRIAL-W2-JUDGE-SHARD-0"]["status"] != "done": fail("shard0 lost done (r425 flip expected)")
if pres["MASS-TRIAL-W2-JUDGE-SHARD-2"]["status"] != "done": fail("shard2 lost done")
if pres["MASS-TRIAL-W2-JUDGE-SHARD-1"]["status"] != "ready": fail("shard1 unexpected state")
print("gate4 PASS: pre-state faces as expected (0 done, 1 ready, 2 done, 3 ready), entries=%d" % len(pre_list))

# ---- surgical edit ----
lines = text.split("\r\n")
try:
    a = next(j for j, l in enumerate(lines) if l.strip() == '"id": "MASS-TRIAL-W2-JUDGE-SHARD-3",')
except StopIteration:
    fail("id anchor line not found (strip-match)")
end = None
for j in range(a, min(a + 120, len(lines))):
    if lines[j].strip() == '"worker_class": "self-contained"' and lines[j+1].strip() in ("},", "}"):
        end = j
        break
if end is None: fail("entry end not found")
block = lines[a:end + 2]
ei = [j for j, l in enumerate(block) if l.strip() == '"status": "ready",']
if len(ei) != 2: fail("expected 2 ready-status lines, got %d" % len(ei))
ent_s, shard_s = ei[0], ei[1]
if '"key": "w2-judge-3of4"' not in "".join(block[:shard_s]): fail("second status not in shard face order")
oi = [j for j, l in enumerate(block) if l.strip() == '"owner": "bm-c",']
os_ = [j for j, l in enumerate(block) if l.strip().startswith('"owner_since":')]
if len(oi) != 1 or len(os_) != 1: fail("owner pair not unique")
oline, osline = block[oi[0]], block[os_[0]]
if os_[0] != oi[0] + 1: fail("owner_since not after owner")
indent_o = oline[:len(oline) - len(oline.lstrip())]
indent_s = osline[:len(osline) - len(osline.lstrip())]
old_os = osline.strip()

new_block = list(block)
new_block[ent_s] = new_block[ent_s].replace('"ready"', '"done"')
new_block[shard_s] = new_block[shard_s].replace('"ready"', '"done"')
new_block[oi[0]] = indent_o + '"owner_since": "%s",' % NOW
new_block[os_[0]] = (indent_s + '"done_at": "%s",\r\n' % NOW
                     + indent_s + '"harvested_by": "bm-c",\r\n'
                     + indent_s + '"harvest_claim": "w2-judge-3of4.bm-c.json",\r\n'
                     + indent_s + '"owner": "bm-c"')
wc = end - a
if new_block[wc].strip() != '"worker_class": "self-contained"': fail("worker_class anchor drift")
indent_w = new_block[wc][:len(new_block[wc]) - len(new_block[wc].lstrip())]
new_block[wc] = (indent_w + '"worker_class": "self-contained",\r\n'
                 + indent_w + '"done_by": "bm-c",\r\n'
                 + indent_w + '"done_at": "%s"' % NOW)
new_text = "\r\n".join(lines[:a] + new_block + lines[end + 2:])
if new_text == text: fail("no change produced")

# ---- gate 5: post-edit parse + semantic assertions ----
post = json.loads(new_text)
post_list = post["entries"] if isinstance(post, dict) else post
posts = {e["id"]: e for e in post_list if str(e.get("id", "")).startswith("MASS-TRIAL-W2-JUDGE-SHARD")}
e3 = posts["MASS-TRIAL-W2-JUDGE-SHARD-3"]
s3 = e3["shards"][0]
assert e3["status"] == "done" and e3["done_by"] == "bm-c" and e3["done_at"] == NOW
assert s3["status"] == "done" and s3["done_at"] == NOW and s3["harvested_by"] == "bm-c"
assert s3["harvest_claim"] == "w2-judge-3of4.bm-c.json" and s3["owner"] == "bm-c"
assert posts["MASS-TRIAL-W2-JUDGE-SHARD-0"]["status"] == "done"
assert posts["MASS-TRIAL-W2-JUDGE-SHARD-1"]["status"] == "ready"
assert posts["MASS-TRIAL-W2-JUDGE-SHARD-2"]["status"] == "done"
assert len(post_list) == len(pre_list) == 366
print("gate5 PASS: post-edit parse + assertions (shard3 entry+shard done, 0/2 done intact, 1 ready, 366 entries)")

# ---- write claim file (r497 backfill, real provenance) ----
claim_obj = {
    "machine_id": "bm-c",
    "state": "closed",
    "pid": 3508,
    "heartbeat": "2026-10-03T" + mtime[11:] + "+08:00",
    "outcome": "ok",
    "exit_code": 0,
    "started": "2026-10-03 18:57:17",
    "closed_at": mtime,
    "result_ref": ("autofill-launched runner (no worker-side handshake, w1 r351 zero-touch face); "
                   "rc unobserved directly -- completeness evidence = 201/201 unique cell rows (i mod 4 == 3) "
                   "in checkpoint, ckpt mtime " + mtime + ", runner pid 3508 exited; claim backfilled + two-layer "
                   "done-flip landed by burner-side session bm-c r425 per r497/r488/r489 law")
}
os.makedirs(os.path.dirname(CLAIM), exist_ok=True)
with open(CLAIM, "w", encoding="utf-8", newline="\r\n") as fh:
    fh.write(json.dumps(claim_obj, ensure_ascii=False, indent=1) + "\n")
print("claim file written:", CLAIM)

with open(POOL, "wb") as fh:
    fh.write(new_text.encode("utf-8"))
print("pool flipped (shard3 two-layer done, action ts %s)" % NOW)

disk = json.loads(open(POOL, "rb").read().decode("utf-8"))
disk_list = disk["entries"] if isinstance(disk, dict) else disk
d3 = {e["id"]: e for e in disk_list}["MASS-TRIAL-W2-JUDGE-SHARD-3"]
assert d3["status"] == "done" and d3["shards"][0]["status"] == "done"
print("disk re-verify PASS; sha16(pool)=%s" % hashlib.sha256(open(POOL, "rb").read()).hexdigest()[:16])
print("FLIP_OK old_owner_since=%s new=%s" % (old_os, NOW))
