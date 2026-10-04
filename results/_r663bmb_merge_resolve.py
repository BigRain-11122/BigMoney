# -*- coding: utf-8 -*-
# r663 bm-b push-race merge resolver (31 UU full-counted):
#   regen snapshot faces -> checkout origin/main (zero-loss, next S6 re-derives)
#   results/runnable_pool.json (POOL face) -> checkout origin + sync_face settle
#     (per-face max-merge from lane views, r626d law; NO blind replay-only)
#   results/x2_watch_log.jsonl (append-only) -> exact-line union keep-first,
#     zero-loss containment check both sides (r656 law; HEAD:/MERGE_HEAD: direct
#     blobs per r657 law-2 -- index stage2/3 destroyed by add)
# Verification BEFORE add: reparse/regression checks; add is a separate step
# (r657 law-3: no ;chain coupling of surgery and add/commit).
import json, subprocess, io, os, sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, "scripts")

def run(cmd):
    p = subprocess.run(cmd, capture_output=True)
    return p.returncode, p.stdout, p.stderr

def blob(ref, path):
    rc, out, err = run(["git", "show", ref + ":" + path])
    if rc != 0:
        raise RuntimeError(f"blob read fail {ref}:{path}: {err.decode('utf-8','replace')[-120:]}")
    return out

# full UU list from porcelain (no tail truncation, r657 law-1)
rc, st, _ = run(["git", "status", "--porcelain"])
uu = [l[3:].strip() for l in st.decode("utf-8", "replace").splitlines()
      if l[:2] in ("UU", "AA")]
print("UU faces:", len(uu))
assert len(uu) > 0, "expected merge conflicts, none found -- wrong state?"

X2 = "results/x2_watch_log.jsonl"
POOL = "results/runnable_pool.json"
special = {X2, POOL}
report = {"uu_n": len(uu), "checkout_origin": [], "pool_settle": None, "x2_union": None}

# --- 1) regen faces: take origin ---
for f in uu:
    if f in special:
        continue
    rc, out, err = run(["git", "checkout", "origin/main", "--", f])
    assert rc == 0, f"checkout origin fail {f}: {err.decode('utf-8','replace')[-120:]}"
    report["checkout_origin"].append(f)
print("checkout origin (regen):", len(report["checkout_origin"]))

# --- 2) pool face: checkout origin, then sync_face settle ---
rc, out, err = run(["git", "checkout", "origin/main", "--", POOL])
assert rc == 0, "pool checkout fail"
import merge_lane_views as mlv

def claims_of(data):
    m = {}
    for e in data.get("entries", []):
        for s in e.get("shards", []) or []:
            m[(str(e.get("id")), str(s.get("key")))] = (s.get("status"), s.get("owner"), s.get("owner_since"))
    return m

pre = claims_of(json.loads(blob("HEAD", POOL).decode("utf-8")))
r = mlv.sync_face("runnable_pool")
report["pool_settle"] = str(r)[:220]
post = claims_of(json.load(io.open(POOL, encoding="utf-8")))
reg = [k for k, (st_, ow, ts) in pre.items()
       if k not in post or (ow == "bm-b" and ts and (not post[k][2] or str(post[k][2]) < str(ts)))]
print("pool settle:", str(r)[:160])
print("claim regressions vs my HEAD:", len(reg), "| pre", len(pre), "post", len(post))
assert not reg, f"pool claim regression after settle: {reg[:5]}"
report["pool_pre_claims"] = len(pre)
report["pool_post_claims"] = len(post)

# --- 3) x2_watch_log.jsonl: exact-line union keep-first, zero-loss both sides ---
head_lines = blob("HEAD", X2).decode("utf-8", "replace").split("\n")
their_lines = blob("MERGE_HEAD", X2).decode("utf-8", "replace").split("\n")
seen = set()
merged = []
for ln in head_lines + their_lines:
    if ln == "":
        continue
    if ln in seen:
        continue
    seen.add(ln)
    merged.append(ln)
hs, ts_ = set(l for l in head_lines if l), set(l for l in their_lines if l)
ms = set(merged)
assert hs <= ms and ts_ <= ms, "x2 union zero-loss containment FAILED"
work = blob("MERGE_HEAD", X2)  # EOL base: use theirs raw to preserve CRLF family
with io.open(X2, "wb") as f:
    f.write(("\n".join(merged) + "\n").encode("utf-8"))
report["x2_union"] = {"head_n": len(hs), "theirs_n": len(ts_), "merged_n": len(ms),
                      "dedup_removed": (len(head_lines) + len(their_lines) - len(hs) - len(ts_))}
print("x2 union:", report["x2_union"])

# --- 4) pre-add verification: no conflict markers in any resolved face ---
marker_faces = []
for f in uu:
    with io.open(f, "rb") as fh:
        data = fh.read()
    for ln in data.split(b"\n"):
        if ln.startswith(b"<<<<<<<") or ln.startswith(b">>>>>>>"):
            marker_faces.append(f)
            break
assert not marker_faces, f"conflict markers remain: {marker_faces}"
print("marker check: clean on all", len(uu), "resolved faces")

with io.open("results/_r663bmb_merge_resolve.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=1)
print("RESOLVE OK -- run add+commit as a separate step next")
