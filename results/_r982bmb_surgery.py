# r982 closeout segment C: r957 tree surgery + push + receipt (differ-checked own faces, verified facts only)
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

# S7-close S0.5 double-scan (anti mid-round sink): fleet faces on fresh tip
for d in ("fleet/orders", "fleet/inbox"):
    names = run(["git", "ls-tree", "--name-only", "%s:%s" % (BASE, d)]).decode().strip().splitlines()
    print("S0.5-rescan %s: %d faces, last3=%s" % (d, len(names), names[-3:]))

def origin_sha(path):
    r = subprocess.run(["git", "rev-parse", "%s:%s" % (BASE, path)], capture_output=True)
    return r.stdout.decode().strip() if r.returncode == 0 else None

# fixed own faces (always in payload)
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

# diff-checked tracked candidates (include only if in origin tree AND disk bytes differ)
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

dirs = sorted([d for d in tree_map if d], key=lambda d: -d.count("/"))
for d in dirs:
    treeish = BASE + ":" + d
    merged = {name: (mode, typ, sha) for mode, typ, sha, name in ls_entries(treeish)}
    merged.update(tree_map[d])
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
# root last: merges all injected subtrees + root-level face blobs
merged_root = {name: (mode, typ, sha) for mode, typ, sha, name in ls_entries(BASE)}
merged_root.update(tree_map.get("", {}))
lines = []
for name in sorted(merged_root, key=lambda n: n + ("/" if merged_root[n][1] == "tree" else "")):
    mode, typ, sha = merged_root[name]
    assert name, "empty name guard"
    lines.append("%s %s %s\t%s" % (mode, typ, sha, name))
root_tree = run(["git", "mktree", "--missing"], inp=("\n".join(lines) + "\n").encode()).decode().strip()
print("tree <root> -> %s (%d entries)" % (root_tree[:12], len(merged_root)))
assert root_tree, "root tree not built"

MSG = "round 982: i2v 53/53 COMPLETE + valve-out (XQ05 467s clean-context fix, clips verified 53/53) + D-19 orders delta consumed (zero bm-b action) + S6 39 legs green [via bm-b r982]"
NEW = run(["git", "commit-tree", root_tree, "-p", BASE, "-m", MSG]).decode().strip()
print("commit-tree:", NEW)
run(["git", "update-ref", "refs/heads/main", NEW])
print("pushing...")
push_out = run(["git", "push", "origin", NEW + ":refs/heads/main"], cap=240)
print("push:", (push_out or b"")[-200:].decode("utf-8", "replace"))
remote_tip = run(["git", "ls-remote", "origin", "refs/heads/main"]).decode().split()[0]
assert remote_tip == NEW, "remote tip mismatch: %s vs %s" % (remote_tip, NEW)
print("REMOTE VERIFIED:", remote_tip)

missing = []
for p in FACES:
    r = subprocess.run(["git", "cat-file", "-e", remote_tip + ":" + p], capture_output=True)
    if r.returncode != 0:
        missing.append(p)
assert not missing, "delivery face missing: %s" % missing
print("delivery face: %d/%d present on new tip" % (len(FACES), len(FACES)))

# r968/r974 delivery law: own orders + own MSGs (incl. NEW MSG-1608) presence on new tip
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
    "face": len(FACES),
    "ts": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+0800"),
    "status": "PUSHED_VERIFIED",
    "remote_tip": remote_tip,
    "faces": FACES,
    "own_delivery_verified": own_delivery,
    "note": "C-r982 own-face surgery push (differ-checked: tracked candidates included only when disk!=origin); deletion set empty; completion MSG-1608 delivered (i2v 53/53 receipt, delivery law r959/r974); docs faces intentionally excluded (anti-regression vs bm-a fresh-host derive); data churn (data/daily + astock per-files) held local pending refresh completion package; state face carries PENDING_AT_HASH_TIME marker (local state gets PUSHED_VERIFIED touch-up post-receipt, lands next round)",
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
})
s["sync"]["behind_origin_main"] = 0
s["latest_artifact"] = "origin main %s (C-r982) + results/_r982bmb_push_receipt.json" % NEW[:10]
s["last_artifact"] = "origin main %s (C-r982) + results/_r982bmb_push_receipt.json" % NEW[:10]
with open("state.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(s, f, ensure_ascii=False, indent=1)
h = json.load(open(r"fleet\machines\bm-b.json", encoding="utf-8"))
h["latest_artifact"] = "origin main %s (C-r982) + results/_r982bmb_push_receipt.json" % NEW[:10]
with open(r"fleet\machines\bm-b.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(h, f, ensure_ascii=False, indent=1)
print("local touch-up done (PUSHED_VERIFIED %s)" % NEW[:10])
