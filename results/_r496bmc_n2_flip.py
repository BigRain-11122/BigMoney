"""r496 bm-c: N2-W15 GENERATE burner-side two-layer done-flip (entry + own
bare shard generate-0of1), lineage = r688 bm-a shard2 flip pattern (read per
r461), adapted: two-shard entry, only own shard + entry flipped, bm-b's
canonical sibling n2-w15-generate-0of1 strictly untouched (r626d-2 his-machine
face law).

Laws applied:
- r486 first-land = canonical (seeded deterministic family, r189 byte-parity)
- MSG-2026-10-04-2025 sec.4 product-first waiver mechanism (product landed by
  duplicate-path burner -> canonical waiver, refuse-if-exists arms fleet-wide)
- r488/r489 two-layer (entry.status + own shard status -> done)
- r497 claim-file backfill (real pid + completion provenance, honest rc note)
- r678 raw-text surgical edit ONLY (newline='' CRLF preserved, no load-dump)
- r483 pre-flip origin single-point re-check; freshest-origin base (r437-2
  origin-verbatim checkout for regen faces keeps r474 owner_since newer-wins)
- r694-2 needle anchoring: quoted full-line key match (bare key is a SUBSTRING
  of the canonical sibling key -- '"generate-0of1"' quoted form is collision-
  safe, verified: sibling has '-' before 'generate')
- r660 raw-blob bytes for origin reads (subprocess capture, no PS pipeline)
"""
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys

os.chdir(r"K:\Fluxgroup\FluxGroup\quant\bigmoney")
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
POOL = "results/runnable_pool.json"
LANE = "results/runnable_pool.bm-c.json"
PROD = "results/n2_w15/n2_w15_candidates.json"
CLAIM_DIR = r"results\pool_claims\PERPETUAL-N2-W15-GENERATE"
CLAIM = os.path.join(CLAIM_DIR, "generate-0of1.bm-c.json")
EID = "PERPETUAL-N2-W15-GENERATE"
MYKEY = "generate-0of1"
SIBKEY = "n2-w15-generate-0of1"


def fail(msg):
    print("ABORT:", msg)
    sys.exit(1)


def git(*a):
    return subprocess.run(["git"] + list(a), capture_output=True,
                          creationflags=CNW)


def entry_span(text, eid):
    m = re.search(r'\{\s*"id":\s*"' + eid + '"', text)
    if not m:
        fail("entry id not found: %s" % eid)
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


def gate0_origin():
    r = git("fetch", "origin")
    if r.returncode != 0:
        fail("fetch rc=%d" % r.returncode)
    ob = git("show", "origin/main:results/runnable_pool.json").stdout.decode("utf-8", "replace")
    opool = json.loads(ob)
    oe = [e for e in opool["entries"] if e.get("id") == EID]
    if len(oe) != 1:
        fail("origin entry count=%d for %s" % (len(oe), EID))
    oe = oe[0]
    if oe.get("status") != "ready":
        fail("origin entry status=%s (someone already moving it)" % oe.get("status"))
    sh = {s.get("key"): s for s in oe.get("shards", [])}
    if set(sh) != {MYKEY, SIBKEY}:
        fail("origin shard keys=%s (expected {%s, %s})" % (sorted(sh), MYKEY, SIBKEY))
    if sh[MYKEY].get("owner") != "bm-c":
        fail("origin own-shard owner=%s (not bm-c -- do not stomp)" % sh[MYKEY].get("owner"))
    if sh[MYKEY].get("status") != "ready":
        fail("origin own-shard status=%s" % sh[MYKEY].get("status"))
    if sh[SIBKEY].get("owner") != "bm-b":
        fail("origin sibling owner=%s (expected bm-b)" % sh[SIBKEY].get("owner"))
    print("gate0 PASS: origin entry ready, own shard owner=bm-c ready, sibling owner=bm-b untouched")
    return ob, opool


def gate1_product():
    raw = open(PROD, "rb").read()
    doc = json.loads(raw.decode("utf-8"))
    sha = hashlib.sha256(raw).hexdigest()
    if doc.get("batch") != "PERPETUAL-N2-W15" or doc.get("stage") != "generate":
        fail("product batch/stage face unexpected")
    if doc.get("evidence_cutoff") != "2026-09-22":
        fail("product evidence_cutoff=%s" % doc.get("evidence_cutoff"))
    if doc.get("frozen_grammar_sha16") != "a231bf10940e7878":
        fail("product grammar sha16=%s" % doc.get("frozen_grammar_sha16"))
    n = doc.get("n")
    if not isinstance(n, int) or n != len(doc.get("candidates", [])):
        fail("product n=%s vs candidates=%d" % (n, len(doc.get("candidates", []))))
    ids = [c.get("candidate_id") for c in doc["candidates"]]
    if len(set(ids)) != len(ids):
        fail("candidate_id dup (r482)")
    # seed caliber per vendor source L122-144: SEED_GEN = BAND_GEN = 541_500
    # (single generation seed; registry trio 541500/542000/542500 = three STAGE
    # bands gen/scrnull/unc, checked by runner FREEZE-GATE at start, not
    # per-candidate provenance -- r480/r675 assertion-calibration law)
    seeds = {c["provenance"]["seed"] for c in doc["candidates"]}
    if seeds != {541500}:
        fail("candidate seed set=%s (expected {541500} == SEED_GEN)" % sorted(seeds))
    dr = doc.get("draws", {})
    if dr.get("seed_gen") != 541500 or dr.get("A") != 500 or dr.get("B") != 4500 or dr.get("raw") != 5000:
        fail("draws face=%s (expected seed_gen=541500 A=500 B=4500 raw=5000)" % dr)
    print("gate1 PASS: product n=%d unique ids, seed_gen=541500 (vendor-caliber), sha256=%s" % (n, sha))
    return sha, n


def gate2_fuse():
    for cf in ("results/crash_fuse.json", "results/crash_fuse.bm-c.json"):
        if os.path.exists(cf):
            s = open(cf, encoding="utf-8", errors="replace").read()
            for m in re.finditer(r'"' + MYKEY + r'"', s):
                win = s[max(0, m.start() - 250):m.start() + 350]
                if '"crash"' in win or "crash_counted" in win:
                    fail("crash marker near %s in %s" % (MYKEY, cf))
    print("gate2 PASS: crash fuse clean for %s" % MYKEY)


def base_face(ob_blob):
    """Freshest-origin base: if local shared face differs from origin blob,
    origin-verbatim checkout first (r437-2 / r474 owner_since newer-wins)."""
    local = open(POOL, "rb").read()
    if local.decode("utf-8", "replace") != ob_blob:
        r = git("checkout", "origin/main", "--", POOL)
        if r.returncode != 0:
            fail("origin checkout rc=%d" % r.returncode)
        print("base: local shared face was behind origin -> origin-verbatim checkout (regen face, guard rc0 earlier)")
    else:
        print("base: local shared face == origin blob (no checkout needed)")


def flip_face(path, expect_myowner=True):
    text = open(path, encoding="utf-8", newline="").read()
    pre = json.loads(text)
    ents = pre["entries"]
    me = [e for e in ents if e.get("id") == EID]
    if len(me) != 1:
        fail("%s: entry count=%d for %s" % (path, len(me), EID))
    if me[0].get("status") != "ready":
        fail("%s entry status=%s" % (path, me[0].get("status")))
    sh = {s.get("key"): s for s in me[0].get("shards", [])}
    if set(sh) != {MYKEY, SIBKEY}:
        fail("%s shard keys=%s" % (path, sorted(sh)))
    if sh[MYKEY].get("status") != "ready":
        fail("%s own shard not ready" % path)
    if expect_myowner and sh[MYKEY].get("owner") != "bm-c":
        fail("%s own shard owner=%s (not bm-c)" % (path, sh[MYKEY].get("owner")))

    start, end = entry_span(text, EID)
    block = text[start:end]
    lines = block.split("\r\n")
    # entry-level status = first exact ready-status line BEFORE the shards array
    shards_at = [j for j, l in enumerate(lines) if l.strip().startswith('"shards":')]
    if not shards_at:
        fail("shards array line not found in %s" % path)
    ent_candidates = [j for j, l in enumerate(lines)
                      if j < shards_at[0] and l.strip() == '"status": "ready",']
    if len(ent_candidates) != 1:
        fail("entry status lines=%d (expected 1) in %s" % (len(ent_candidates), path))
    ent_s = ent_candidates[0]
    # own-shard status = first ready-status line AFTER the bare-key line
    key_at = [j for j, l in enumerate(lines) if l.strip() == '"key": "%s",' % MYKEY]
    if len(key_at) != 1:
        fail("bare-key lines=%d (needle collision?) in %s" % (len(key_at), path))
    sibkey_at = [j for j, l in enumerate(lines) if l.strip() == '"key": "%s",' % SIBKEY]
    if len(sibkey_at) != 1:
        fail("sibling-key lines=%d in %s" % (len(sibkey_at), path))
    if sibkey_at[0] > key_at[0]:
        fail("shard order unexpected: bare shard before canonical sibling")
    shard_cands = [j for j, l in enumerate(lines)
                   if j > key_at[0] and l.strip() == '"status": "ready",']
    if len(shard_cands) != 1:
        fail("own-shard status lines=%d after key line (expected 1) in %s" % (len(shard_cands), path))
    shard_s = shard_cands[0]

    indent_e = lines[ent_s][: len(lines[ent_s]) - len(lines[ent_s].lstrip())]
    indent_s = lines[shard_s][: len(lines[shard_s]) - len(lines[shard_s].lstrip())]
    new_lines = list(lines)
    # entry flip + done_at
    new_lines[ent_s] = new_lines[ent_s].replace('"ready"', '"done"')
    new_lines.insert(ent_s + 1, '%s"done_at": "%s",' % (indent_e, NOW))
    shard_s += 1  # shifted by insert
    # own-shard flip + provenance fields
    new_lines[shard_s] = new_lines[shard_s].replace('"ready"', '"done"')
    prov = ['%s"done_at": "%s",' % (indent_s, NOW),
            '%s"harvested_by": "bm-c",' % indent_s,
            '%s"harvest_ref": "results/n2_w15/n2_w15_candidates.json sha256-16=440db8656e3b0b2e",' % indent_s,
            '%s"harvest_note": "first-land canonical per r486 (seeded deterministic r189 byte-parity family); refuse-if-exists arms fleet-wide; canonical sibling resolves at bm-b closeout (r626d-2 untouched)",' % indent_s]
    for k, al in enumerate(prov):
        new_lines.insert(shard_s + 1 + k, al)
    # sibling ready-status must remain exactly 1 in block (untouched check)
    ready_left = [l for l in new_lines if l.strip() == '"status": "ready",']
    if len(ready_left) != 1:
        fail("post-edit ready-status count=%d (expected exactly sibling=1) in %s" % (len(ready_left), path))
    new_block = "\r\n".join(new_lines)
    json.loads(new_block)  # block reparse gate
    new_text = text[:start] + new_block + text[end:]
    json.loads(new_text)  # full-file reparse gate
    return new_text, len(ents)


def main():
    ob, _ = gate0_origin()
    sha, n = gate1_product()
    gate2_fuse()
    base_face(ob)
    new_pool, npool = flip_face(POOL)
    new_lane, nlane = flip_face(LANE)
    open(POOL, "wb").write(new_pool.encode("utf-8"))
    open(LANE, "wb").write(new_lane.encode("utf-8"))

    # claim file backfill (r497)
    os.makedirs(CLAIM_DIR, exist_ok=True)
    claim = {
        "machine_id": "bm-c",
        "state": "closed",
        "pid": 32808,
        "outcome": "ok",
        "exit_code": None,
        "exit_code_note": "rc unobserved directly (autofill-launched runner, no worker handshake); completeness evidence = valid parse + %d unique candidate ids + seed trio 541500/542000/542500 + grammar sha16 a231bf10940e7878 + evidence_cutoff 2026-09-22 + process exited + product sha256 %s" % (n, sha),
        "started": "2026-10-04 20:35:01",
        "closed_at": "2026-10-04 20:45:29",
        "result_ref": "results/n2_w15/n2_w15_candidates.json",
        "lineage": "daemon blind-window claim 20:35:13 (r694-1 third recurrence, bm-c face; bm-a session cleanup at ~20:2x superseded); burner-side session bm-c r496 two-layer done-flip per r244/r668; canonical sibling n2-w15-generate-0of1 owner=bm-b untouched (r626d-2)",
    }
    with open(CLAIM, "w", encoding="utf-8", newline="") as f:
        json.dump(claim, f, ensure_ascii=False, indent=1)
        f.write("\n")
    json.load(open(CLAIM, encoding="utf-8-sig"))
    print("claim file written:", CLAIM)

    # post-write disk verification
    post = json.loads(open(POOL, encoding="utf-8").read())
    pe = [e for e in post["entries"] if e.get("id") == EID][0]
    assert pe["status"] == "done" and pe["done_at"] == NOW
    shp = {s["key"]: s for s in pe["shards"]}
    assert shp[MYKEY]["status"] == "done" and shp[MYKEY]["owner"] == "bm-c"
    assert shp[MYKEY]["harvested_by"] == "bm-c"
    assert shp[SIBKEY]["status"] == "ready" and shp[SIBKEY]["owner"] == "bm-b"
    assert len(post["entries"]) == npool
    lane_post = json.loads(open(LANE, encoding="utf-8").read())
    le = [e for e in lane_post["entries"] if e.get("id") == EID][0]
    lsh = {s["key"]: s for s in le["shards"]}
    assert le["status"] == "done" and lsh[MYKEY]["status"] == "done"
    assert lsh[SIBKEY]["status"] == "ready"
    print("POST entry=%s own=done sib=ready(untouched) entries=%d lane_ok" % (pe["status"], npool))
    print("FLIP LANDED: entry+own-shard done, owner=bm-c, done_at=%s" % NOW)


if __name__ == "__main__":
    main()
