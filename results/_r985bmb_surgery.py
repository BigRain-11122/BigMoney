# r985 closeout segment C: ancestor-inclusive tree surgery + push + receipt.
# Bloodline: r984 surgery (results/_r984bmb_surgery.py) verbatim pattern <- r983 <- r982 v2.
# r985 payload policy: EXPLICIT own faces ONLY (no CANDIDATES auto-include this round --
#   bm-a r1019 landed 17:29 with S6-derived faces; stale-local auto-include = mirror-revert
#   risk, so every face below is bm-b-owned and local-newer by construction).
# CODELY.md INCLUDED this round (union landed: bm-c r1031 row absorbed + r983 row preserved).
# Superset assertion (anti mirror-revert): for append-only shared faces, CR-normalized
# origin-only line set must be EMPTY before the face may ship.
import subprocess, json, time, datetime, os, io

def run(args, inp=None, cap=None):
    if cap:
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE if inp else None)
        deadline = time.time() + cap
        while p.poll() is None and time.time() < deadline:
            time.sleep(1)
        if p.poll() is None:
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)], capture_output=True)
            out, err = p.communicate(inp)
            raise RuntimeError("TIMEOUT(tree-killed) %s :: %s" % (args[:3], (err or b"")[-300:].decode("utf-8", "replace")))
        out, err = p.communicate(inp)
        if p.returncode != 0:
            raise RuntimeError("rc=%d %s :: %s" % (p.returncode, args[:4], (err or b"")[-400:].decode("utf-8", "replace")))
        return out
    r = subprocess.run(args, capture_output=True, input=inp)
    if r.returncode != 0:
        raise RuntimeError("rc=%d %s :: %s" % (r.returncode, args[:4], (r.stderr or b"")[-400:].decode("utf-8", "replace")))
    return r.stdout

# ---- pre-flight 1: attrition guard scan (S7 closeout leg, must be CLEAN before push) ----
r = subprocess.run(["python", "scripts/attrition_ledger_guard.py", "scan"], capture_output=True)
print("attrition scan rc=%d :: %s" % (r.returncode, (r.stdout or b"")[-200:].decode("utf-8", "replace").strip()))
assert r.returncode == 0, "attrition guard not clean - push aborted"

print("fetch:", (run(["git", "fetch", "origin"], cap=120) or b"").decode().strip()[-120:])
BASE = run(["git", "rev-parse", "origin/main"]).decode().strip()
print("base(origin/main):", BASE)

# ---- pre-flight 2: superset assertion on append-only shared faces ----
APPEND_ONLY = ["logs/iteration-loop/round_reports.md", "CODELY.md", "research/HANDOVER.md"]
for p in APPEND_ONLY:
    # r962 law: round_reports.md is MIXED-ENCODING binary face -- byte-line comparison, never utf-8 decode
    ob = run(["git", "show", "%s:%s" % (BASE, p)])
    io.open(r"C:\Windows\Temp\_r985_superset_origin.md", "wb").write(ob)
    o = set(l.rstrip(b"\r") for l in ob.split(b"\n") if l.strip())
    m = set(l.rstrip(b"\r") for l in open(p, "rb").read().split(b"\n") if l.strip())
    assert not (o - m), "MIRROR-REVERT HAZARD in %s: origin-only byte-lines %d" % (p, len(o - m))
    print("superset OK:", p, "(origin-only=0)")

FACES = [
    "state.json",
    "fleet/machines/bm-b.json",
    "logs/iteration-loop/round_reports.md",
    "CODELY.md",
    "research/HANDOVER.md",
    "results/_r984bmb_push_receipt.json",
    "results/_r985bmb_closeout.py",
    "results/_r985bmb_surgery.py",
    "results/_r686bmb_d19_check.json",
    "results/_orphan_face_probe.bm-b.json",
    "results/_attrition_guard_scan.json",
    "results/astock_daily_update_status.json",
    "results/idle_trigger.bm-b.json",
    "results/watermark_red.json",
]
for p in FACES:
    assert os.path.exists(p), "face missing on disk: %s" % p

blob = {}
for p in FACES:
    blob[p] = run(["git", "hash-object", "-w", p]).decode().strip()
print("hash-object done: %d faces" % len(blob))

B = lambda sha: ("100644", "blob", sha)
T = lambda sha: ("040000", "tree", sha)

def ls_entries(treeish):
    out = run(["git", "ls-tree", treeish]).decode()
    ents = []
    for line in out.splitlines():
        if not line.strip():
            continue
        meta, name = line.split("\t", 1)
        mode, typ, sha = meta.split()
        assert name, "EMPTY NAME ENTRY (r957 law): %r" % line
        ents.append((mode, typ, sha, name))
    return ents

tree_map = {}
for p, sha in blob.items():
    parts = p.split("/")
    d = "/".join(parts[:-1])
    name = parts[-1]
    tree_map.setdefault(d, {})[name] = B(sha)

need = set()
for d0 in list(tree_map.keys()):
    if not d0:
        continue
    parts = d0.split("/")
    for i in range(1, len(parts) + 1):
        need.add("/".join(parts[:i]))
dirs = sorted(need, key=lambda d: -d.count("/"))
print("dirs to rebuild (ancestor-inclusive):", dirs)

for d in dirs:
    treeish = BASE + ":" + d
    merged = {name: (mode, typ, sha) for mode, typ, sha, name in ls_entries(treeish)}
    for name, ent in tree_map.get(d, {}).items():
        merged[name] = ent
    lines = []
    for name in sorted(merged, key=lambda n: n + ("/" if merged[n][1] == "tree" else "")):
        mode, typ, sha = merged[name]
        assert name, "empty name guard"
        lines.append("%s %s %s\t%s" % (mode, typ, sha, name))
    new = run(["git", "mktree", "--missing"], inp=("\n".join(lines) + "\n").encode()).decode().strip()
    print("tree %s -> %s (%d entries)" % (d, new[:12], len(merged)))
    if "/" in d:
        parent, base = d.rsplit("/", 1)
    else:
        parent, base = "", d
    tree_map.setdefault(parent, {})[base] = T(new)

merged_root = {name: (mode, typ, sha) for mode, typ, sha, name in ls_entries(BASE)}
for name, ent in tree_map.get("", {}).items():
    merged_root[name] = ent
lines = []
for name in sorted(merged_root, key=lambda n: n + ("/" if merged_root[n][1] == "tree" else "")):
    mode, typ, sha = merged_root[name]
    assert name, "empty name guard"
    lines.append("%s %s %s\t%s" % (mode, typ, sha, name))
root_tree = run(["git", "mktree", "--missing"], inp=("\n".join(lines) + "\n").encode()).decode().strip()
print("tree <root> -> %s (%d entries)" % (root_tree[:12], len(merged_root)))
assert root_tree, "root tree not built"

MSG = ("round 985: CODELY union merge (bm-c r1031 absorbed + r983 row preserved, 1/1->0/0) + HANDOVER 5x "
       "r981-r985 (wb-open truncation pit zero-loss recovery) + orphan index.lock healed (zero-committer) + "
       "astock refresh convergence honest defer (package awaits complete) + D-19 dual-sha zero-delta + "
       "smoke 49/49 + attrition CLEAN [via bm-b r985]")
NEW = run(["git", "commit-tree", root_tree, "-p", BASE, "-m", MSG]).decode().strip()
print("commit-tree:", NEW)
run(["git", "update-ref", "refs/heads/main", NEW])
print("pushing...")
push_out = run(["git", "push", "origin", NEW + ":refs/heads/main"], cap=240)
print("push:", (push_out or b"")[-200:].decode("utf-8", "replace"))
remote_tip = run(["git", "ls-remote", "origin", "refs/heads/main"]).decode().split()[0]
assert remote_tip == NEW, "remote tip mismatch: %s vs %s" % (remote_tip, NEW)
print("REMOTE VERIFIED:", remote_tip)

missing, stale = [], []
for p, sha in blob.items():
    r = subprocess.run(["git", "rev-parse", "%s:%s" % (remote_tip, p)], capture_output=True)
    if r.returncode != 0:
        missing.append(p)
    elif r.stdout.decode().strip() != sha:
        stale.append(p)
assert not missing, "delivery face missing: %s" % missing
assert not stale, "delivery face STALE (content mismatch): %s" % stale
print("delivery face: %d/%d CONTENT-VERIFIED on new tip" % (len(blob), len(blob)))

own_delivery = ["fleet/orders/O-20261015-0025-bm-b.md", "fleet/orders/O-20261015-0906-bm-b.md",
                "fleet/orders/O-20261015-0915-bm-b.md", "fleet/orders/O-20261015-0952-bm-b.md",
                "fleet/inbox/MSG-20261015-0104-bmb-P1B-G5-done.md",
                "fleet/inbox/MSG-20261015-0825-bm-b-cpu-pool-restock.md",
                "fleet/inbox/MSG-20261015-0952-bm-b-work-request.md",
                "fleet/inbox/MSG-20261015-1608-bm-b-animatic-53-53-done.md"]
dm = []
for p in own_delivery:
    ok_top = subprocess.run(["git", "cat-file", "-e", remote_tip + ":" + p], capture_output=True).returncode == 0
    ok_proc = subprocess.run(["git", "cat-file", "-e", remote_tip + ":fleet/inbox/processed/" + os.path.basename(p)],
                             capture_output=True).returncode == 0
    if not (ok_top or ok_proc):
        dm.append(p)
assert not dm, "own delivery faces missing (both accounts): %s" % dm
print("own orders/MSGs delivery face: %d/%d present on new tip (inbox/ or processed/)" % (
    len(own_delivery), len(own_delivery)))

orders_tip = run(["git", "ls-tree", "--name-only", remote_tip + ":fleet/orders"]).decode().split()
inbox_tip = run(["git", "ls-tree", "--name-only", remote_tip + ":fleet/inbox"]).decode().split()
print("S7 second scan: orders n=%d inbox n=%d" % (len(orders_tip), len(inbox_tip)))

receipt = {
    "base": BASE,
    "commit": NEW,
    "root_tree": root_tree,
    "face": len(blob),
    "ts": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+0800"),
    "status": "PUSHED_VERIFIED",
    "remote_tip": remote_tip,
    "faces": FACES,
    "own_delivery_verified": own_delivery,
    "delivery_check": "content-level rev-parse blob sha == hash-object local (%d/%d)" % (len(blob), len(blob)),
    "superset_check": "append-only faces (round_reports/CODELY/HANDOVER) origin-only line set EMPTY pre-ship",
    "note": ("C-r985 own-face surgery push (r982 v2 bloodline); explicit-faces-only policy (no CANDIDATES auto-include; "
             "bm-a r1019 17:29 S6-derived faces = stale-local revert risk avoided); CODELY.md INCLUDED (union landed: "
             "bm-c r1031 + local r983 rows both preserved); HANDOVER 5x r981-r985 entry rides (1,100,199B post "
             "zero-loss truncation recovery); astock data churn (per-files) held local pending completion package "
             "(worker final convergence, 18:08 gate window); docs faces excluded (anti-regression, r982 policy); "
             "shared pool faces excluded (max-merge law MSG-0612); r984 push receipt rides this push"),
}
with open("results/_r985bmb_push_receipt.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("receipt written: results/_r985bmb_push_receipt.json status=PUSHED_VERIFIED")

s = json.load(open("state.json", encoding="utf-8"))
s["sync"]["r985_main_push"] = {
    "status": "PUSHED_VERIFIED",
    "pushed_sha": NEW,
    "consumed_at": "pending r986",
    "behind_origin_main": 0,
    "note": receipt["note"],
}
s["sync"]["behind_origin_main"] = 0
s["sync"]["r984_main_push"]["consumed_at"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
s["latest_artifact"] = "origin main %s (C-r985) + results/_r985bmb_push_receipt.json" % NEW[:10]
s["last_artifact"] = s["latest_artifact"]
tmp = "state.json.r985tmp"
open(tmp, "wb").write(json.dumps(s, ensure_ascii=False, indent=1).encode("utf-8") + b"\n")
os.replace(tmp, "state.json")
h = json.load(open(r"fleet/machines/bm-b.json", encoding="utf-8"))
h["latest_artifact"] = "origin main %s (C-r985) + results/_r985bmb_push_receipt.json" % NEW[:10]
tmp = r"fleet\machines\bm-b.json.r985tmp"
open(tmp, "wb").write(json.dumps(h, ensure_ascii=False, indent=1).encode("utf-8") + b"\n")
os.replace(tmp, r"fleet\machines\bm-b.json")
print("local touch-up done (PUSHED_VERIFIED %s)" % NEW[:10])
