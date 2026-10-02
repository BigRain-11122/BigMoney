# r602 bm-b: pool-face heal via canonical sync_face in temp dir (r598 settle path).
# Sources: origin blobs (regressed shared + bm-a stale claim lane + bm-c lane) + my lane
# (valuepb-x2 done 04:38:04 + nulls owner=bm-b). Assertions fail-closed before payload.
import subprocess, json, os, sys, shutil, tempfile

REPO = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
TD = os.path.join(REPO, "results", "_r602bmb_poolheal_td")
shutil.rmtree(TD, ignore_errors=True)
os.makedirs(TD)

def blob2file(path, dest):
    p = subprocess.run(["git", "-C", REPO, "show", "origin/main:" + path], capture_output=True)
    if p.returncode != 0:
        print("blob fetch fail", path, p.stderr.decode()[:200]); sys.exit(1)
    with open(os.path.join(TD, dest), "wb") as f:
        f.write(p.stdout)

# origin faces -> temp dir (production layout: shared + 3 lanes)
for p in ("results/runnable_pool.json", "results/runnable_pool.bm-a.json",
          "results/runnable_pool.bm-b.json", "results/runnable_pool.bm-c.json"):
    blob2file(p, os.path.basename(p))

sys.path.insert(0, os.path.join(REPO, "scripts"))
os.chdir(REPO)
import merge_lane_views as mlv

res = mlv.sync_face("runnable_pool", results_dir=TD, machine="bm-b")
print("sync_face result:", json.dumps({k: v for k, v in res.items() if k != "notes"},
                                      ensure_ascii=False))
for n in res.get("notes", [])[:10]:
    print("note:", str(n)[:200])

# --- r381 yield posture + r603 stability pin: valuepb-x2 attribution = origin's terminal
# flip (bm-a duplicate burn actually executed 04:54->05:00:04; products canonical = mine
# ac8519fd2). Take origin's entry object VERBATIM in all three faces (no attribution fight,
# converged terminal state); only NULLS claim needs restoration.
EID = "FUND-VALUE-P1-CELL-VALUEPB-X2"
orig_pool = json.loads(subprocess.run(["git", "-C", REPO, "show",
                          "origin/main:results/runnable_pool.json"], capture_output=True).stdout.decode("utf-8-sig", "replace"))
if isinstance(orig_pool, dict):
    for k in ("entries", "pool", "items", "runnable"):
        if isinstance(orig_pool.get(k), list):
            orig_pool = orig_pool[k]; break
orig_entry = next(x for x in orig_pool if x.get("id") == EID)
print("origin terminal entry (yield posture): status=%s owner=%s done_at=%s done_by=%s"
      % (orig_entry.get("status"), orig_entry["shards"][0].get("owner"),
         orig_entry["shards"][0].get("done_at"), orig_entry.get("done_by")))

def probe_face(raw):
    crlf = raw.count(b"\r\n") > 0
    trailing = raw.endswith(b"\n")
    lines = raw.decode("utf-8", "replace").splitlines()
    ind = 2
    for ln in lines[1:]:
        if ln.strip().startswith('"') and ln.startswith(" "):
            ind = len(ln) - len(ln.lstrip())
            break
    return ind, crlf, trailing

def rewrite_entry(path, eid, new_entry):
    raw = open(path, "rb").read()
    ind, crlf, trailing = probe_face(raw)
    data = json.loads(raw.decode("utf-8-sig", "replace"))
    items = data
    if isinstance(data, dict):
        for k in ("entries", "pool", "items", "runnable"):
            if isinstance(data.get(k), list):
                items = data[k]; break
    idx = next(i for i, x in enumerate(items) if x.get("id") == eid)
    before = json.dumps(items[idx], ensure_ascii=False, sort_keys=True)
    items[idx] = json.loads(json.dumps(new_entry))  # deep copy, origin verbatim
    out = json.dumps(data, ensure_ascii=False, indent=ind)
    if crlf:
        out = out.replace("\n", "\r\n")
    if trailing:
        out += "\n"
    open(path, "wb").write(out.encode("utf-8"))
    return before != json.dumps(new_entry, ensure_ascii=False, sort_keys=True)

changed = {}
for name in ("runnable_pool.json", "runnable_pool.bm-a.json", "runnable_pool.bm-b.json"):
    p = os.path.join(TD, name)
    changed[name] = rewrite_entry(p, EID, orig_entry)
print("valuepb-x2 origin-verbatim entry pin per face:", changed)

merged_path = os.path.join(TD, "runnable_pool.json")
d = json.load(open(merged_path, encoding="utf-8"))
if isinstance(d, dict):
    for k in ("entries", "pool", "items", "runnable"):
        if isinstance(d.get(k), list):
            d = d[k]; break
orig = json.loads(subprocess.run(["git", "-C", REPO, "show", "origin/main:results/runnable_pool.json"],
                                 capture_output=True).stdout.decode("utf-8-sig", "replace"))
if isinstance(orig, dict):
    for k in ("entries", "pool", "items", "runnable"):
        if isinstance(orig.get(k), list):
            orig = orig[k]; break

def find(items, eid):
    return next((x for x in items if x.get("id") == eid), None)

fails = []
# 1) valuepb-x2: origin terminal entry preserved VERBATIM (r381 yield posture, both layers done)
e = find(d, "FUND-VALUE-P1-CELL-VALUEPB-X2")
sh = (e or {}).get("shards", [{}])[0]
if not (e and e.get("status") == "done" and sh.get("status") == "done"
        and json.dumps(e, ensure_ascii=False, sort_keys=True)
        == json.dumps(orig_entry, ensure_ascii=False, sort_keys=True)):
    fails.append("valuepb-x2 != origin terminal entry (yield-posture violation)")
# 2) nulls: my claim restored (r489 claim visibility = origin)
e2 = find(d, "FUND-VALUE-P1-NULLS")
sh2 = (e2 or {}).get("shards", [{}])[0]
if not (sh2.get("owner") == "bm-b"):
    fails.append("nulls owner not restored: owner=%s" % sh2.get("owner"))
# 3) SENS: bm-a's legitimate done flip preserved
e3 = find(d, "FUND-VALUE-P1-SENS")
sh3 = (e3 or {}).get("shards", [{}])[0]
if not (e3 and e3.get("status") == "done" and sh3.get("status") == "done"):
    fails.append("SENS done regression: %s/%s" % (e3 and e3.get("status"), sh3.get("status")))
# 4) id-union: no entry lost vs origin
oids = {x.get("id") for x in orig}
nids = {x.get("id") for x in d}
if oids - nids:
    fails.append("entries lost vs origin: %s" % sorted(oids - nids)[:5])
# 5) done-absorption only: no origin-done entry regressed
for o in orig:
    if o.get("status") == "done":
        n = find(d, o.get("id"))
        if not n or n.get("status") != "done":
            fails.append("origin-done entry regressed: %s" % o.get("id"))

print("entry counts: origin=%d merged=%d" % (len(orig), len(d)))
if fails:
    print("HEAL ASSERTIONS FAILED:")
    for f in fails:
        print(" -", f)
    sys.exit(2)
print("HEAL ASSERTIONS PASS (yield posture): valuepb-x2 == origin terminal entry (done/bm-a 05:00:04, both layers), nulls owner=bm-b restored, SENS done (bm-a) preserved, %d entries union-lossless" % len(d))
print("settled shared ->", merged_path)
print("settled lane ->", os.path.join(TD, "runnable_pool.bm-b.json"))
