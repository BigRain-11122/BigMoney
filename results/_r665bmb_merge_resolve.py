# -*- coding: utf-8 -*-
# r665 bm-b push-race merge resolver (31 UU full-counted, r663 recipe reuse):
#   regen snapshot faces -> checkout origin/main (zero-loss, next S6 re-derives)
#   results/runnable_pool.json (POOL face) -> checkout origin + sync_face settle
#     (per-face max-merge from lane views, r626d law; claim regression assert)
#   results/compute_audit.json -> (ts, canonical) line-level union + zero-loss
#     containment both sides (r658/r660 law), latest = fresher ts side
#   results/token_usage.json -> take-ours under 4 premises (newer generated;
#     crash_fuse append faces identical; machines keyset identical; ours default
#     report_bytes fresher) -- r649 chain-law face, diverged-parallel variant:
#     append faces byte-identical = zero append-loss; snapshot self-heals next run
#   x2_watch_log.jsonl (auto-merged by git, NOT UU) -> containment verify vs
#     HEAD/MERGE_HEAD canon line sets (r656 law); no rewrite if contained
# Verification BEFORE add: reparse/marker checks; add is a separate step
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
assert len(uu) == 31, f"expected 31 UU, got {len(uu)} -- face set drifted, re-inspect"

POOL = "results/runnable_pool.json"
AUDIT = "results/compute_audit.json"
TOKEN = "results/token_usage.json"
X2 = "results/x2_watch_log.jsonl"
special = {POOL, AUDIT, TOKEN}
report = {"uu_n": len(uu), "checkout_origin": [], "pool_settle": None,
          "audit_union": None, "token_takeours": None, "x2_verify": None}

# --- 1) regen faces: take origin ---
for f in uu:
    if f in special:
        continue
    rc, out, err = run(["git", "checkout", "origin/main", "--", f])
    assert rc == 0, f"checkout origin fail {f}: {err.decode('utf-8','replace')[-120:]}"
    report["checkout_origin"].append(f)
print("checkout origin (regen):", len(report["checkout_origin"]))
assert len(report["checkout_origin"]) == 28

# --- 2) pool face: checkout origin, then sync_face settle (r626d law) ---
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
rc, out, err = run(["git", "add", "--", POOL])
assert rc == 0, "pool add fail"

# --- 3) compute_audit.json: (ts, canonical) union, zero-loss containment (r660) ---
o = json.loads(blob("HEAD", AUDIT))
t = json.loads(blob("MERGE_HEAD", AUDIT))

def canon(row):
    return json.dumps(row, sort_keys=True, ensure_ascii=False)

seen = set()
union = []
for row in sorted(o["history"] + t["history"], key=lambda r: str(r.get("ts", ""))):
    k = (str(row.get("ts", "")), canon(row))
    if k in seen:
        continue
    seen.add(k)
    union.append(row)
o_set = {(str(r.get("ts", "")), canon(r)) for r in o["history"]}
t_set = {(str(r.get("ts", "")), canon(r)) for r in t["history"]}
u_set = {(str(r.get("ts", "")), canon(r)) for r in union}
lost_o = len(o_set - u_set)
lost_t = len(t_set - u_set)
assert lost_o == 0 and lost_t == 0, f"LOSS o={lost_o} t={lost_t}"
lo, lt = str(o["latest"].get("ts", "")), str(t["latest"].get("ts", ""))
latest = o["latest"] if lo >= lt else t["latest"]
merged = {"latest": latest, "history": union}
out_b = json.dumps(merged, ensure_ascii=False, indent=1).encode("utf-8")
with io.open(AUDIT, "wb") as f:
    f.write(out_b)
rc, out, err = run(["git", "add", "--", AUDIT])
assert rc == 0, "audit add fail"
report["audit_union"] = {"ours": len(o["history"]), "theirs": len(t["history"]),
                         "union": len(union), "latest_side": "ours" if lo >= lt else "theirs",
                         "latest_ts": latest.get("ts")}
print("compute_audit union:", report["audit_union"])

# --- 4) token_usage.json: take-ours under 4 premises (diverged-parallel variant) ---
O = json.loads(blob("HEAD", TOKEN))
T = json.loads(blob("MERGE_HEAD", TOKEN))
p1 = str(O["generated"]) > str(T["generated"])
of = O.get("l2_local_llm", {}).get("crash_fuse", {})
tf = T.get("l2_local_llm", {}).get("crash_fuse", {})
p2 = of.get("sigs") == tf.get("sigs") and of.get("refusals") == tf.get("refusals")
p3 = sorted(O.get("machines", {}).keys()) == sorted(T.get("machines", {}).keys())
p4 = O.get("machines", {}).get("default", {}).get("report_bytes", 0) >= \
     T.get("machines", {}).get("default", {}).get("report_bytes", 0)
assert p1 and p2 and p3 and p4, f"token take-ours premises broken: p1={p1} p2={p2} p3={p3} p4={p4}"
with io.open(TOKEN, "wb") as f:
    f.write(json.dumps(O, ensure_ascii=False, indent=1).encode("utf-8"))
rc, out, err = run(["git", "add", "--", TOKEN])
assert rc == 0, "token add fail"
report["token_takeours"] = {"ours_generated": O["generated"],
                            "theirs_generated": T["generated"],
                            "fuse_sigs": of.get("sigs"), "fuse_refusals": of.get("refusals")}
print("token take-ours ok:", report["token_takeours"])

# --- 5) x2_watch_log.jsonl (auto-merged): containment verify vs both parents ---
work = io.open(X2, "rb").read().decode("utf-8", "replace")
work_lines = set(l for l in work.split("\n") if l)
head_lines = set(l for l in blob("HEAD", X2).decode("utf-8", "replace").split("\n") if l)
their_lines = set(l for l in blob("MERGE_HEAD", X2).decode("utf-8", "replace").split("\n") if l)
lost_h = len(head_lines - work_lines)
lost_t2 = len(their_lines - work_lines)
report["x2_verify"] = {"work_n": len(work_lines), "head_n": len(head_lines),
                       "theirs_n": len(their_lines), "lost_head": lost_h, "lost_theirs": lost_t2}
print("x2 containment:", report["x2_verify"])
assert lost_h == 0, f"x2 auto-merge LOST {lost_h} head lines -- union surgery required"
if lost_t2 > 0:
    # union surgery keep-first (r663 phase-3 pattern)
    merged_lines = []
    seen_l = set()
    for ln in (blob("HEAD", X2).decode("utf-8", "replace").split("\n") +
               blob("MERGE_HEAD", X2).decode("utf-8", "replace").split("\n")):
        if ln == "" or ln in seen_l:
            continue
        seen_l.add(ln)
        merged_lines.append(ln)
    ms = set(merged_lines)
    assert head_lines <= ms and their_lines <= ms, "x2 union containment FAILED"
    with io.open(X2, "wb") as f:
        f.write(("\n".join(merged_lines) + "\n").encode("utf-8"))
    rc, out, err = run(["git", "add", "--", X2])
    assert rc == 0, "x2 add fail"
    report["x2_verify"]["surgery"] = "union keep-first applied"
    print("x2 union surgery applied:", len(ms), "lines")

# --- 6) pre-commit verification: markers on all 31 faces + json reparse ---
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
for f in uu:
    if f.endswith(".json"):
        json.load(io.open(f, encoding="utf-8"))
print("json reparse: all", sum(1 for f in uu if f.endswith(".json")), "json faces clean")
js = io.open("results/dashboard_status.js", encoding="utf-8").read()
json.loads(js.split("=", 1)[1].strip().rstrip(";"))
print("js face parse: clean")

with io.open("results/_r665bmb_merge_resolve.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=1)
print("RESOLVE OK -- run add+commit as a separate step next")
