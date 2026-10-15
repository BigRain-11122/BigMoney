# r982 closeout segment C v2: ancestor-inclusive tree surgery + push + receipt.
# v1 PIT (caught live this round): dirs list built ONLY from dirs directly holding a
# face -> parent dirs (fleet/logs/data) never rebuilt -> nested faces rode stale origin
# trees; -e existence checks false-passed (old files exist at same paths); the NEW-file
# face (MSG-1608) failed -e and exposed it. r980/r981 pushes carried the same gap
# (origin heartbeat/round-report stuck at r979 face). v2 fix: need-set = ALL ancestor
# dirs of every face; delivery check = CONTENT (rev-parse blob sha vs hash-object).
import subprocess, json, time, datetime, os

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

print("fetch:", (run(["git", "fetch", "origin"], cap=120) or b"").decode().strip()[-120:])
BASE = run(["git", "rev-parse", "origin/main"]).decode().strip()
print("base(origin/main):", BASE)

def origin_sha(path):
    r = subprocess.run(["git", "rev-parse", "%s:%s" % (BASE, path)], capture_output=True)
    return r.stdout.decode().strip() if r.returncode == 0 else None

FACES = [
    "state.json",
    "fleet/machines/bm-b.json",
    "logs/iteration-loop/round_reports.md",
    "fleet/inbox/MSG-20261015-1608-bm-b-animatic-53-53-done.md",
    "results/_r982bmb_s6chain.log",
    "results/_r982bmb_s6chain_driver.py",
    "results/_r982bmb_s6chain_console.log",
    "results/_r982bmb_closeout_prep.py",
    "results/_r982bmb_surgery.py",
    "results/_r686bmb_d19_check.json",
    "results/_orphan_face_probe.bm-b.json",
    "results/_attrition_guard_scan.json",
    "results/astock_daily_update_status.json",
    "results/_r982bmb_smoke.log",
    "results/_r982bmb_xq05_reignite.json",
    "results/_r982bmb_xq05_reignite.py",
    "results/_r982bmb_xq05_restart.py",
    "results/_r982bmb_xq05_restart.log",
    "results/_r982bmb_xq05_restart.json",
    "results/_r982bmb_oomtrace.tmp.txt",
    "results/_r982bmb_oomtrace2.tmp.txt",
]
if os.path.exists("results/_r982bmb_s6chain_console.err"):
    FACES.append("results/_r982bmb_s6chain_console.err")

CANDIDATES = [
    "results/update_status.json",
    "results/market_clock/call_latest.json",
    "results/market_clock/call_latest.bm-b.json",
    "results/market_clock/CALL-2026-10-14.md",
    "results/regime_gate_dualarm/latest.json",
    "results/regime_gate_dualarm/DUALARM-2026-09-30.json",
    "results/regime_thermo/thermo_daily.csv",
    "results/regime_thermo/thermo_summary.json",
    "data/minute_feed/510300.csv",
    "data/minute_feed/510050.csv",
    "data/minute_feed/510500.csv",
    "data/minute_feed/512100.csv",
    "data/minute_feed/588000.csv",
    "results/token_usage.json",
    "results/idle_trigger.bm-b.json",
    "results/pool_dualrun.bm-b.jsonl",
]
for p in CANDIDATES:
    if not os.path.exists(p):
        continue
    o = origin_sha(p)
    if o is None:
        print("skip (not tracked at origin):", p)
        continue
    d = run(["git", "hash-object", p]).decode().strip()
    if d != o:
        FACES.append(p)
        print("diff face included:", p)
    else:
        print("identical, skip:", p)

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

# v2 FIX: need-set = every ancestor dir of every face dir (root "" excluded)
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

# root last
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

MSG = ("round 982: i2v 53/53 COMPLETE + valve-out (XQ05 467s clean-context fix) + surgery ancestor-tree gap fixed "
       "(nested faces r980-r982 re-delivered: heartbeat/round-report/minute_feed) + MSG-1608 receipt [via bm-b r982]")
NEW = run(["git", "commit-tree", root_tree, "-p", BASE, "-m", MSG]).decode().strip()
print("commit-tree:", NEW)
run(["git", "update-ref", "refs/heads/main", NEW])
print("pushing...")
push_out = run(["git", "push", "origin", NEW + ":refs/heads/main"], cap=240)
print("push:", (push_out or b"")[-200:].decode("utf-8", "replace"))
remote_tip = run(["git", "ls-remote", "origin", "refs/heads/main"]).decode().split()[0]
assert remote_tip == NEW, "remote tip mismatch: %s vs %s" % (remote_tip, NEW)
print("REMOTE VERIFIED:", remote_tip)

# v2 delivery check = CONTENT (rev-parse blob sha vs local hash-object) for EVERY face
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
                "fleet/inbox/MSG-20261015-0104-bmb-P1B-G5-done.md", "fleet/inbox/MSG-20261015-0825-bm-b-cpu-pool-restock.md",
                "fleet/inbox/MSG-20261015-0952-bm-b-work-request.md",
                "fleet/inbox/MSG-20261015-1608-bm-b-animatic-53-53-done.md"]
dm = [p for p in own_delivery if subprocess.run(["git", "cat-file", "-e", remote_tip + ":" + p], capture_output=True).returncode != 0]
assert not dm, "own delivery faces missing: %s" % dm
print("own orders/MSGs delivery face: %d/%d present on new tip" % (len(own_delivery), len(own_delivery)))

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
    "v1_incident": {
        "commit": "281f2ceb7fb79fd8a7e8cc700e1f2e9ca3395f51",
        "bug": "ancestor dirs (fleet/logs/data) never rebuilt -> nested faces rode stale origin trees; -e existence checks false-passed; caught by NEW-file face (MSG-1608) failing -e",
        "damage_window": "r980/r981/r982-attempt pushes carried same gap: origin heartbeat + round_reports stuck at r979 faces, minute_feed 5 codes at r979 bytes; cumulative files re-delivered whole in this push",
        "landed_ok_in_v1": "state.json + results/* + Tools/* (depth<=1 dirs injected to root correctly)",
    },
    "note": "C-r982 v2 own-face surgery push (ancestor-inclusive dirs + CONTENT-level delivery verification); deletion set empty; completion MSG-1608 delivered; docs faces intentionally excluded (anti-regression); data churn (data/daily + astock per-files) held local pending refresh completion package; state face carries PENDING_AT_HASH_TIME marker (local touch-up post-receipt, lands next round)",
}
with open("results/_r982bmb_push_receipt.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("receipt written: results/_r982bmb_push_receipt.json status=PUSHED_VERIFIED")

s = json.load(open("state.json", encoding="utf-8"))
s["sync"]["r982_main_push"].update({
    "status": "PUSHED_VERIFIED",
    "pushed_sha": NEW,
    "consumed_at": "pending r983",
    "behind_origin_main": 0,
    "note": receipt["note"] + " | v1 incident recorded (ancestor-tree gap, nested faces re-delivered)",
})
s["sync"]["behind_origin_main"] = 0
s["latest_artifact"] = "origin main %s (C-r982 v2) + results/_r982bmb_push_receipt.json" % NEW[:10]
s["last_artifact"] = "origin main %s (C-r982 v2) + results/_r982bmb_push_receipt.json" % NEW[:10]
with open("state.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(s, f, ensure_ascii=False, indent=1)
h = json.load(open(r"fleet\machines\bm-b.json", encoding="utf-8"))
h["latest_artifact"] = "origin main %s (C-r982 v2) + results/_r982bmb_push_receipt.json" % NEW[:10]
with open(r"fleet\machines\bm-b.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(h, f, ensure_ascii=False, indent=1)
print("local touch-up done (PUSHED_VERIFIED %s)" % NEW[:10])
