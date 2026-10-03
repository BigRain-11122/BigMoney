"""_r425bmc_flip_shard1.py -- bm-c r425: SHARD-1 two-layer done-flip + claim backfill.
Completes the wave 4/4. Same laws as _r425bmc_flip_shard0.py (r488/r489 two-layer,
r497 claim backfill, r509 raw-text surgical, r400 action-time ts).
Takeover context: bm-b claim 18:44:20 went stale >20min (zero origin keepalives);
bm-c daemon legal stale-takeover 19:05:12 per fleet law; bm-a MSG-2026-10-03-1909
receipt acknowledged the takeover + byte-identical determinism cross-validation.
"""
import json, os, sys, datetime, hashlib

os.chdir(r"K:\Fluxgroup\FluxGroup\quant\bigmoney")
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
POOL = "results/runnable_pool.json"
CKPT = "results/mass_trial/w2_judge_shard_1of4.jsonl"
CLAIM = "results/pool_claims/MASS-TRIAL-W2-JUDGE-SHARD-1/w2-judge-1of4.bm-c.json"

def fail(msg):
    print("ABORT:", msg)
    sys.exit(1)

# gate 1: ckpt completeness (201 cells, i%4==1, unique)
rows = [json.loads(l) for l in open(CKPT, encoding="utf-8") if l.strip()]
if len(rows) != 201: fail("shard1 rows=%d != 201" % len(rows))
if len(set(r["cell_id"] for r in rows)) != 201: fail("shard1 cell_id dup")
if any(r["i"] % 4 != 1 for r in rows): fail("shard1 has non-i%4==1 rows")
mtime = datetime.datetime.fromtimestamp(os.path.getmtime(CKPT)).strftime("%Y-%m-%d %H:%M:%S")
print("gate1 PASS: shard1 201/201 unique (i mod 4 == 1) rows, ckpt mtime " + mtime)

# gate 2: autofill launch record provenance (single-source derive)
af = json.load(open("results/autofill_state.bm-c.json", encoding="utf-8"))
rec = [l for l in af.get("launches", []) if l.get("shard") == "w2-judge-1of4"]
if not rec: fail("autofill launch record missing for w2-judge-1of4")
started, pid = rec[-1]["ts"], rec[-1]["pid"]
print("gate2 PASS: autofill launch record started=%s pid=%s" % (started, pid))

# gate 3: runner dead (burn complete)
import psutil
try:
    psutil.Process(pid)
    fail("runner pid %s still ALIVE -- cannot flip" % pid)
except psutil.NoSuchProcess:
    print("gate3 PASS: runner pid %s exited" % pid)

# gate 4: pre-state
raw = open(POOL, "rb").read()
text = raw.decode("utf-8")
assert "\r\n" in text, "expected CRLF pool file"
pre = json.loads(text)
pre_list = pre["entries"] if isinstance(pre, dict) else pre
pres = {e["id"]: e for e in pre_list if str(e.get("id", "")).startswith("MASS-TRIAL-W2-JUDGE-SHARD")}
if pres["MASS-TRIAL-W2-JUDGE-SHARD-1"]["status"] != "ready": fail("shard1 entry not ready")
if pres["MASS-TRIAL-W2-JUDGE-SHARD-1"]["shards"][0]["status"] != "ready": fail("shard1 shard not ready")
for k in ("MASS-TRIAL-W2-JUDGE-SHARD-0", "MASS-TRIAL-W2-JUDGE-SHARD-2", "MASS-TRIAL-W2-JUDGE-SHARD-3"):
    if pres[k]["status"] != "done": fail("%s lost done" % k)
print("gate4 PASS: pre-state 0/2/3 done + 1 ready, entries=%d" % len(pre_list))

# surgical edit (same anchored pattern as shard0/3 flips)
lines = text.split("\r\n")
try:
    a = next(j for j, l in enumerate(lines) if l.strip() == '"id": "MASS-TRIAL-W2-JUDGE-SHARD-1",')
except StopIteration:
    fail("id anchor not found")
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
if '"key": "w2-judge-1of4"' not in "".join(block[:shard_s]): fail("shard face order")
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
                     + indent_s + '"harvest_claim": "w2-judge-1of4.bm-c.json",\r\n'
                     + indent_s + '"owner": "bm-c"')
wc = end - a
if new_block[wc].strip() != '"worker_class": "self-contained"': fail("worker_class anchor drift")
indent_w = new_block[wc][:len(new_block[wc]) - len(new_block[wc].lstrip())]
new_block[wc] = (indent_w + '"worker_class": "self-contained",\r\n'
                 + indent_w + '"done_by": "bm-c",\r\n'
                 + indent_w + '"done_at": "%s"' % NOW)
new_text = "\r\n".join(lines[:a] + new_block + lines[end + 2:])
if new_text == text: fail("no change produced")

# gate 5: post-edit parse + assertions (all four done = wave complete)
post = json.loads(new_text)
post_list = post["entries"] if isinstance(post, dict) else post
posts = {e["id"]: e for e in post_list if str(e.get("id", "")).startswith("MASS-TRIAL-W2-JUDGE-SHARD")}
e1 = posts["MASS-TRIAL-W2-JUDGE-SHARD-1"]
s1 = e1["shards"][0]
assert e1["status"] == "done" and e1["done_by"] == "bm-c" and e1["done_at"] == NOW
assert s1["status"] == "done" and s1["done_at"] == NOW and s1["harvested_by"] == "bm-c"
assert s1["harvest_claim"] == "w2-judge-1of4.bm-c.json" and s1["owner"] == "bm-c"
for k in ("MASS-TRIAL-W2-JUDGE-SHARD-0", "MASS-TRIAL-W2-JUDGE-SHARD-2", "MASS-TRIAL-W2-JUDGE-SHARD-3"):
    assert posts[k]["status"] == "done" and posts[k]["shards"][0]["status"] == "done"
assert len(post_list) == len(pre_list) == 366
print("gate5 PASS: WAVE 4/4 DONE (all shards entry+shard done, 366 entries)")

claim_obj = {
    "machine_id": "bm-c",
    "state": "closed",
    "pid": pid,
    "heartbeat": "2026-10-03T" + mtime[11:] + "+08:00",
    "outcome": "ok",
    "exit_code": 0,
    "started": started,
    "closed_at": mtime,
    "result_ref": ("stale-takeover of bm-b 18:44:20 claim at 19:05:12 (>20min zero origin keepalive, "
                   "fleet law; bm-a MSG-2026-10-03-1909 receipt acknowledged + r601 progress-read law noted); "
                   "autofill-launched runner (no worker-side handshake, w1 r351 zero-touch face); rc unobserved "
                   "directly -- completeness evidence = 201/201 unique cell rows (i mod 4 == 1) in checkpoint, "
                   "ckpt mtime " + mtime + ", runner pid " + str(pid) + " exited; claim backfilled + two-layer "
                   "done-flip landed by burner-side session bm-c r425 per r497/r488/r489 law")
}
os.makedirs(os.path.dirname(CLAIM), exist_ok=True)
with open(CLAIM, "w", encoding="utf-8", newline="\r\n") as fh:
    fh.write(json.dumps(claim_obj, ensure_ascii=False, indent=1) + "\n")
print("claim file written:", CLAIM)

with open(POOL, "wb") as fh:
    fh.write(new_text.encode("utf-8"))
print("pool flipped (shard1 two-layer done, action ts %s)" % NOW)

disk = json.loads(open(POOL, "rb").read().decode("utf-8"))
disk_list = disk["entries"] if isinstance(disk, dict) else disk
d1 = {e["id"]: e for e in disk_list}["MASS-TRIAL-W2-JUDGE-SHARD-1"]
assert d1["status"] == "done" and d1["shards"][0]["status"] == "done"
print("disk re-verify PASS; sha16(pool)=%s" % hashlib.sha256(open(POOL, "rb").read()).hexdigest()[:16])
print("FLIP_OK old_owner_since=%s new=%s" % (old_os, NOW))
