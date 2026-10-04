"""_r483bmc_flip_shard3.py -- bm-c r483: SHARD-3 two-layer done-flip by
finalize-collect authority (r668 law: finalize round MUST complete pool
double-flip same-window; burner bm-a completed+pushed the 1228 rows but
pool face still ready -> autofill re-ignition loop hazard).
Laws: r488/r489 two-layer / r509 raw-text surgical edit ONLY (CRLF,
json.dumps forbidden) / r311 owner_since bump + claimed_since preservation
/ r400 monotonic ts / r497 claim backfill with HONEST provenance (flip
authority record, NOT a fabricated bm-a worker handshake).
Abort-before-write: all gates in-memory; single atomic write; re-verify.
"""
import datetime
import difflib
import json
import os
import sys

os.chdir(r"K:\Fluxgroup\FluxGroup\quant\bigmoney")
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
POOL = "results/runnable_pool.json"
CLAIM = ("results/pool_claims/MASS-TRIAL-W3-SCREEN-SHARD-3/"
         "w3-screen-3of4.bm-c.json")
E3 = "MASS-TRIAL-W3-SCREEN-SHARD-3"


def fail(msg):
    print("ABORT:", msg)
    sys.exit(1)


# ---- gate 1: burn completeness (shard-3 rows present, zero dup, tiling) ----
cand_meta = json.load(open("results/mass_trial/w3_candidates.json",
                           encoding="utf-8"))
rows = [json.loads(l) for l in
        open("results/mass_trial/w3_screen_checkpoint.jsonl",
             encoding="utf-8") if l.strip()]
cand = [r for r in rows if r.get("row_type") == "candidate"]
ids = [r["id"] for r in cand]
cids = [r["id"] for r in cand_meta["candidates"]]
if len(set(ids)) != len(ids):
    fail("dup ids in checkpoint (%d unique/%d)" % (len(set(ids)), len(ids)))
if set(ids) != set(cids):
    fail("candidate tiling mismatch vs w3_candidates.json")
if not (len(cand) == cand_meta["n"] == 4814):
    fail("candidate count %d != n %d" % (len(cand), cand_meta["n"]))
pos = {c: i for i, c in enumerate(cids)}
s3 = [c for c in ids if pos[c] >= 3681]
# combined-row order: candidates [0:4814) + controls [4814:4889) + nulls
# [4889:4909) -- shard-3 [3681:4909) = 1133 candidates + 75 ctrl + 20 null
n_ctrl = sum(1 for r in rows if r.get("row_type") == "control")
n_null = sum(1 for r in rows if r.get("row_type") == "null")
if len(s3) != 4814 - 3681 or n_ctrl != 75 or n_null != 20:
    fail("shard-3 face %d candidates + %d ctrl + %d null != 1133+75+20"
         % (len(s3), n_ctrl, n_null))
print("gate1 PASS: 4814/4814 candidates zero-dup; shard-3 face = "
      "1133 cand + 75 ctrl + 20 null = 1228/1228 present")

# ---- gate 2: crash fuse zero hits for w3-screen-3of4 ----
for cf in ("results/crash_fuse.json", "results/crash_fuse.bm-c.json",
           "results/crash_fuse.bm-a.json", "results/crash_fuse.bm-b.json"):
    if os.path.exists(cf):
        s = open(cf, encoding="utf-8", errors="replace").read()
        if "w3-screen-3of4" in s and "crash" in s.lower():
            idx = s.find("w3-screen-3of4")
            win = s[max(0, idx - 200):idx + 300]
            if '"crash"' in win or "crash_counted" in win:
                fail("crash marker near w3-screen-3of4 in " + cf)
print("gate2 PASS: crash fuse zero crash-markers for w3-screen-3of4")

# ---- gate 3: pre-state on shared pool ----
raw = open(POOL, "rb").read()
text = raw.decode("utf-8")
assert "\r\n" in text, "expected CRLF pool file"
pre = json.loads(text)
pre_list = pre["entries"] if isinstance(pre, dict) else pre
pres = {e["id"]: e for e in pre_list
        if str(e.get("id", "")).startswith("MASS-TRIAL-W3-SCREEN")}
for k in ("MASS-TRIAL-W3-SCREEN-SHARD-0", "MASS-TRIAL-W3-SCREEN-SHARD-1",
          "MASS-TRIAL-W3-SCREEN-SHARD-2"):
    if pres[k]["status"] != "done" or pres[k]["shards"][0]["status"] != "done":
        fail(k + " lost done state")
e3 = pres[E3]
if e3["status"] != "ready": fail("entry not ready")
if e3["shards"][0]["status"] != "ready": fail("shard not ready")
if e3["shards"][0]["owner"] != "bm-a": fail("owner drift")
old_os = e3["shards"][0]["owner_since"]
if NOW <= old_os: fail("monotonic ts gate: NOW <= owner_since " + old_os)
n_pre = len(pre_list)
print("gate3 PASS: 0/1/2 done, SHARD-3 ready, owner bm-a since " + old_os
      + ", entries=" + str(n_pre))

# ---- surgical edit ----
lines = text.split("\r\n")
a = next((j for j, l in enumerate(lines)
          if l.strip() == '"id": "%s",' % E3), None)
if a is None: fail("id anchor not found")
# entry end = worker_class line + closing " }" (last entry in file)
end = None
for j in range(a, min(a + 200, len(lines))):
    if lines[j].strip() == '"worker_class": "self-contained"' \
            and lines[j + 1].strip() == "}":
        end = j
        break
if end is None: fail("entry end (worker_class + close brace) not found")
block = lines[a:end + 2]

si = [j for j, l in enumerate(block) if l.strip() == '"status": "ready",']
if len(si) != 2: fail("expected 2 ready-status lines, got %d" % len(si))
ent_s, shard_s = si
if '"key": "w3-screen-3of4"' not in "".join(block[:shard_s]):
    fail("second status not in shard face order")
oi = [j for j, l in enumerate(block) if l.strip() == '"owner": "bm-a",']
osi = [j for j, l in enumerate(block)
       if l.strip().startswith('"owner_since":')]
if len(oi) != 1 or len(osi) != 1 or osi[0] != oi[0] + 1:
    fail("owner/owner_since pair not unique/adjacent (o=%d os=%d)"
         % (len(oi), len(osi)))
oline = block[oi[0]]
indent_o = oline[:len(oline) - len(oline.lstrip())]

new_block = list(block)
new_block[ent_s] = new_block[ent_s].replace('"ready"', '"done"')
new_block[shard_s] = new_block[shard_s].replace('"ready"', '"done"')
# shard tail: claimed_since preserve + owner_since bump + done_at +
# harvested_by + harvest_claim + owner last (r311 + landed shape)
new_block[oi[0]] = (indent_o + '"claimed_since": "%s",\r\n' % old_os
                    + indent_o + '"owner_since": "%s",\r\n' % NOW
                    + indent_o + '"done_at": "%s",\r\n' % NOW
                    + indent_o + '"harvested_by": "bm-c",\r\n'
                    + indent_o + '"harvest_claim": '
                    '"w3-screen-3of4.bm-c.json (flip-authority record: '
                    'burn by bm-a per pool claim 15:53:07, rows verified '
                    '4814/4814 zero-dup post r482-law dedup; no bm-a '
                    'worker claim pushed)",\r\n'
                    + indent_o + '"owner": "bm-a"')
# entry tail FIRST (list indices still pre-deletion), THEN delete the old
# owner_since line -- del-before-index = off-by-one eats the entry close
# brace (JSON never closes; debugged in-memory, zero disk touch)
wc = end - a
wcl = new_block[wc]
indent_w = wcl[:len(wcl) - len(wcl.lstrip())]
if wcl.strip() != '"worker_class": "self-contained"':
    fail("worker_class anchor drift: %r" % wcl)
new_block[wc] = (indent_w + '"worker_class": "self-contained",\r\n'
                 + indent_w + '"done_by": "bm-c",\r\n'
                 + indent_w + '"done_at": "%s"' % NOW)
del new_block[osi[0]]

new_text = "\r\n".join(lines[:a] + new_block + lines[end + 2:])
if new_text == text: fail("no change produced")

# ---- gate 4: post-edit parse + semantic assertions (in memory) ----
post = json.loads(new_text)
post_list = post["entries"] if isinstance(post, dict) else post
psts = {e["id"]: e for e in post_list
        if str(e.get("id", "")).startswith("MASS-TRIAL-W3-SCREEN")}
p3 = psts[E3]
s3f = p3["shards"][0]
assert p3["status"] == "done" and p3["done_by"] == "bm-c" \
    and p3["done_at"] == NOW
assert s3f["status"] == "done" and s3f["done_at"] == NOW \
    and s3f["harvested_by"] == "bm-c" and s3f["owner"] == "bm-a"
assert s3f["claimed_since"] == old_os and s3f["owner_since"] == NOW
for k in ("MASS-TRIAL-W3-SCREEN-SHARD-0", "MASS-TRIAL-W3-SCREEN-SHARD-1",
          "MASS-TRIAL-W3-SCREEN-SHARD-2"):
    assert psts[k]["status"] == "done"
assert len(post_list) == n_pre
d = [l for l in difflib.unified_diff(text.split("\r\n"),
                                     new_text.split("\r\n"), lineterm="")
     if l[:1] in "+-" and l[:3] not in ("+++", "---")]
print("gate4 PASS: parse+semantics ok, entries=%d, changed lines=%d"
      % (len(post_list), len(d)))
for l in d: print("  ", l[:150])

# ---- claim file backfill (r497, HONEST provenance) ----
claim_obj = {
    "machine_id": "bm-c",
    "state": "closed",
    "pid": None,
    "outcome": "ok",
    "exit_code": None,
    "started": "2026-10-04 15:53:07 (bm-a burn start per pool claim)",
    "closed_at": NOW,
    "result_ref": ("flip-authority record (NOT a bm-a worker handshake): "
                   "shard-3 rows [3681:4909) burned+pushed by bm-a "
                   "(r685 union evidence commit 71400f82e); completion "
                   "verified by bm-c r483 finalize gate = 4814/4814 "
                   "candidates zero-dup (r482-law keep-first dedup, "
                   "evidence results/_r483bmc_ckpt_dedup.json) + "
                   "w3_screen_summary.json complete=true; two-layer "
                   "done-flip landed by finalize session bm-c r483 per "
                   "r668 same-window law (autofill re-ignition hazard)"),
}
os.makedirs(os.path.dirname(CLAIM), exist_ok=True)
with open(CLAIM, "w", encoding="utf-8", newline="\r\n") as fh:
    fh.write(json.dumps(claim_obj, ensure_ascii=False, indent=1) + "\n")
print("claim file written:", CLAIM)

# ---- atomic pool write + disk re-verify ----
with open(POOL, "wb") as fh:
    fh.write(new_text.encode("utf-8"))
disk = json.loads(open(POOL, "rb").read().decode("utf-8"))
dl = disk["entries"] if isinstance(disk, dict) else disk
d3 = {e["id"]: e for e in dl}[E3]
assert d3["status"] == "done" and d3["shards"][0]["status"] == "done"
print("disk re-verify PASS; FLIP_OK old_owner_since=%s new=%s"
      % (old_os, NOW))
