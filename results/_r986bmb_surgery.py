# r986 closeout segment C: completion-package surgery push (r982 v2 bloodline <- r985 <- r984).
# Payload = data churn 37 faces (astock recovery closure package) + bookkeeping + evidence.
# DATA-FACE ANTI-REVERT: every data face that exists on origin tip must pass a byte-line
# superset check (origin-only non-empty line set EMPTY) before it may ship; failures are
# DROPPED from the payload and disclosed, never force-shipped.
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

r = subprocess.run(["python", "scripts/attrition_ledger_guard.py", "scan"], capture_output=True)
print("attrition scan rc=%d :: %s" % (r.returncode, (r.stdout or b"")[-160:].decode("utf-8", "replace").strip()))
assert r.returncode == 0, "attrition guard not clean - push aborted"

print("fetch:", (run(["git", "fetch", "origin"], cap=120) or b"").decode().strip()[-120:])
BASE = run(["git", "rev-parse", "origin/main"]).decode().strip()
print("base(origin/main):", BASE)

# ---- payload assembly ----
data_faces = []
for ln in io.open(r"C:\Windows\Temp\_r986_data_faces.txt", "r", encoding="ascii", errors="replace"):
    ln = ln.strip()
    if not ln:
        continue
    p = ln[3:].strip()
    if p.startswith("data/"):
        data_faces.append(p)
print("data faces enumerated:", len(data_faces))

FACES = [
    "state.json",
    "fleet/machines/bm-b.json",
    "logs/iteration-loop/round_reports.md",
    "Tools/iteration_loop.ps1",
    "results/_r986bmb_gpu_burn.py",
    "results/_r986bmb_astock_close.py",
    "results/_r986bmb_closeout.py",
    "results/_r986bmb_surgery.py",
    "results/_r986bmb_gpu_burn_evidence.csv",
    "results/_r986bmb_astock_complete.json",
    "results/_r686bmb_d19_check.json",
    "results/astock_daily_update_status.json",
    "results/update_status.json",
    "results/_orphan_face_probe.bm-b.json",
    "results/_attrition_guard_scan.json",
    "results/idle_trigger.bm-b.json",
    "results/watermark_red.json",
] + data_faces

# ---- anti-revert superset check: append-only faces + every data face on origin ----
dropped = []
kept = []
APPEND_ONLY_TEXT = ["logs/iteration-loop/round_reports.md"]
def superset_ok(p):
    rc = subprocess.run(["git", "cat-file", "-e", "%s:%s" % (BASE, p)], capture_output=True).returncode
    if rc != 0:
        return True  # new face, pure add
    ob = run(["git", "show", "%s:%s" % (BASE, p)])
    o = set(l.rstrip(b"\r") for l in ob.split(b"\n") if l.strip())
    m = set(l.rstrip(b"\r") for l in open(p, "rb").read().split(b"\n") if l.strip())
    return not (o - m)

for p in APPEND_ONLY_TEXT + data_faces:
    if p in APPEND_ONLY_TEXT:
        ok = superset_ok(p)
        print("superset", "OK" if ok else "FAIL", p)
        assert ok, "MIRROR-REVERT HAZARD in append-only face %s" % p
    else:
        if superset_ok(p):
            kept.append(p)
        else:
            dropped.append(p)
            print("superset FAIL -> DROPPED (honest disclose):", p)
FACES = [f for f in FACES if f not in dropped]
for p in FACES:
    assert os.path.exists(p), "face missing on disk: %s" % p
print("payload: %d faces (dropped %d)" % (len(FACES), len(dropped)))

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
print("dirs to rebuild (ancestor-inclusive):", len(dirs))

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

MSG = ("round 986: dead-session estate absorbed + POOL-0020 DONE (GPU 1200W re-commission: 30min burn max 239.1W "
       "77C zero-power-loss zero-WHEA, pl 239.80W, PowerCap tasks deleted, full-power production + first-24h "
       "single-batch serial; card-lint element-4 spec-pointer REJECT disclosed, authority CEO O-0952/O-1821; "
       "evidence results/_r986bmb_gpu_burn_evidence.csv) + astock rebuild CLOSED complete=true (5221/5229, 8 "
       "quarantine + 11 settled, snapshot _r986bmb_astock_complete.json) + COMPLETION PACKAGE data churn %d faces "
       "(daily/repo_daily/fundamental 10-14 bars + eligibility, superset-checked) + spawn-gate preflight landed "
       "(C-20261015-03 sec.3 / O-20261015-1834, pre-24:00) + heartbeat codely_live_count field + orders 4-row "
       "delta consumed (watermark e394cb69) + smoke 49/49 [via bm-b r986]" % len(data_faces))
NEW = run(["git", "commit-tree", root_tree, "-p", BASE, "-m", MSG]).decode().strip()
print("commit-tree:", NEW)
run(["git", "update-ref", "refs/heads/main", NEW])
print("pushing...")
push_out = run(["git", "push", "origin", NEW + ":refs/heads/main"], cap=180)
print("push:", (push_out or b"")[-200:].decode("utf-8", "replace"))
remote_tip = run(["git", "ls-remote", "origin", "refs/heads/main"]).decode().split()[0]
assert remote_tip == NEW, "remote tip mismatch: %s vs %s" % (remote_tip, NEW)
print("REMOTE VERIFIED:", remote_tip)

missing, stale = [], []
for p, sha in blob.items():
    rr = subprocess.run(["git", "rev-parse", "%s:%s" % (remote_tip, p)], capture_output=True)
    if rr.returncode != 0:
        missing.append(p)
    elif rr.stdout.decode().strip() != sha:
        stale.append(p)
assert not missing, "delivery face missing: %s" % missing
assert not stale, "delivery face STALE (content mismatch): %s" % stale
print("delivery face: %d/%d CONTENT-VERIFIED on new tip" % (len(blob), len(blob)))

receipt = {
    "base": BASE,
    "commit": NEW,
    "root_tree": root_tree,
    "face_n": len(blob),
    "data_faces": len(data_faces),
    "dropped_superset_fail": dropped,
    "ts": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+0800"),
    "status": "PUSHED_VERIFIED",
    "pool_0020_receipt": {
        "card_id": "POOL-0020",
        "action": "done",
        "evidence": ["results/_r986bmb_gpu_burn_evidence.csv (BURN DONE 30min max_draw=239.1W max_temp=77C pl=239.80W)",
                     "System log 18/19/41 events in 18:30-19:10 window = zero (zero power-loss, zero WHEA)",
                     "nvidia-smi power.limit = 239.80W live probe",
                     "GPU-PowerCap-180W-Boot/Hourly schtasks queries = empty (deleted)",
                     "card-lint: REJECT element-4 spec-pointer (bm-b-local memory path unresolvable from group-repo root; disclosed, authority = CEO orders O-0952/O-1821)"],
        "step5": "full-power production live; first-24h single-batch serial conservative period started 19:08",
    },
    "faces": FACES,
    "delivery_check": "content-level rev-parse blob sha == hash-object local (%d/%d)" % (len(blob), len(blob)),
    "superset_check": "round_reports.md origin-only=0; %d data faces superset-checked, %d dropped on fail" % (len(data_faces), len(dropped)),
    "note": ("C-r986 completion-package surgery push (r982 v2 bloodline); payload = astock recovery closure (data "
             "churn 10-14 bars) + POOL-0020 GPU re-commission evidence + spawn-gate (C-20261015-03) + bookkeeping; "
             "docs faces excluded (anti-regression, r982 policy); CODELY.md/HANDOVER excluded (no new rows this "
             "round); foreign dirty faces held untouched (explicit-faces-only); NEWBAR gate closed on sina ETF "
             "late-bar (tencent probe proves upstream 10-15 bar; self-heal watch next rounds)"),
}
with open("results/_r986bmb_push_receipt.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("receipt written: results/_r986bmb_push_receipt.json status=PUSHED_VERIFIED")

s = json.load(open("state.json", encoding="utf-8"))
s["sync"]["r986_main_push"] = {
    "status": "PUSHED_VERIFIED",
    "pushed_sha": NEW,
    "consumed_at": "pending r987",
    "behind_origin_main": 0,
    "note": receipt["note"],
}
s["sync"]["behind_origin_main"] = 0
s["sync"]["r985_main_push"]["consumed_at"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
s["latest_artifact"] = "origin main %s (C-r986) + results/_r986bmb_push_receipt.json" % NEW[:10]
s["last_artifact"] = s["latest_artifact"]
tmp = "state.json.r986tmp2"
open(tmp, "wb").write(json.dumps(s, ensure_ascii=False, indent=1).encode("utf-8") + b"\n")
os.replace(tmp, "state.json")
h = json.load(open(r"fleet\machines\bm-b.json", encoding="utf-8"))
h["latest_artifact"] = "origin main %s (C-r986) + results/_r986bmb_push_receipt.json" % NEW[:10]
tmp = r"fleet\machines\bm-b.json.r986tmp2"
open(tmp, "wb").write(json.dumps(h, ensure_ascii=False, indent=1).encode("utf-8") + b"\n")
os.replace(tmp, r"fleet\machines\bm-b.json")
print("local touch-up done (PUSHED_VERIFIED %s)" % NEW[:10])
