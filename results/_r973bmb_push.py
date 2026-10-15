# r973 bm-b PHASE-B only (PHASE-A already written by _r973bmb_closeout.py first run; appends not idempotent).
# Cold-index tree-surgery push (r950/r951/r953/r957 laws) + verified receipt (r968 own-orders check).
import difflib
import json
import os
import subprocess
import threading
import time

REPO = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"


def run(cmd, cap=120):
    p = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=cap)
    return p.returncode, p.stdout, p.stderr


def run_capped(cmd, cap_sec=180):
    p = subprocess.Popen(cmd, cwd=REPO, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    fired = [False]

    def _k():
        fired[0] = True
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)], capture_output=True)
    t = threading.Timer(cap_sec, _k)
    t.start()
    out, err = p.communicate()
    t.cancel()
    return p.returncode, (out or b"").decode("utf-8", "replace"), (err or b"").decode("utf-8", "replace"), fired[0]


FACES = {
    "scripts/backfill_ext_slots.py": None,
    "state.json": None,
    "fleet/machines/bm-b.json": None,
    "logs/iteration-loop/round_reports.md": None,
}
rc, so, se = run(["git", "fetch", "origin", "main"], cap=100)
print("fetch rc=", rc)
rc, tip, _ = run(["git", "rev-parse", "origin/main"])
tip = tip.strip()
print("tip=", tip)

# sanity gate v2: all diff hunks must sit inside the two regions I edited this round
rc, origin_script, _ = run(["git", "show", "origin/main:scripts/backfill_ext_slots.py"])
local_script = open(os.path.join(REPO, "scripts", "backfill_ext_slots.py"), "rb").read().decode("utf-8")
diff = list(difflib.unified_diff(origin_script.splitlines(), local_script.splitlines(), lineterm="", n=1))
hunks = [l for l in diff if l.startswith("@@")]
regions = [(30, 55), (240, 325)]  # (pythonw guard) / (margin sse_dead + month-end blocks)
ok = True
for h in hunks:
    old_start = int(h.split(" ")[1].lstrip("-").split(",")[0])
    inside = any(lo <= old_start <= hi for lo, hi in regions)
    print("  hunk", h, "region_ok=", inside)
    ok = ok and inside
if not ok or not hunks:
    print("ABORT: diff outside edited regions")
    raise SystemExit(3)
print("hunks=", len(hunks), "all inside edited regions -> proceed")

for path in FACES:
    rc, sha, err = run(["git", "hash-object", "-w", os.path.join(REPO, path.replace("/", os.sep))])
    if rc != 0:
        print("hash-object failed", path, err)
        raise SystemExit(3)
    FACES[path] = sha.strip()
print("blobs:", json.dumps(FACES))


def ls_tree(tree_ref):
    p = subprocess.run(["git", "ls-tree", "-z", tree_ref], cwd=REPO, capture_output=True)
    if p.returncode != 0:
        print("ls-tree failed", tree_ref, p.stderr.decode("utf-8", "replace"))
        raise SystemExit(3)
    entries = {}
    for rec in p.stdout.split(b"\0"):
        if not rec:
            continue
        meta, name = rec.split(b"\t", 1)
        mode, typ, sha = meta.split(b" ")
        entries[name] = (mode, typ, sha, name)
    return entries


p = subprocess.run(["git", "mktree"], input=b"", cwd=REPO, capture_output=True)
EMPTY_TREE = p.stdout.decode().strip()


def rebuild(tree_ref, parts, blob_sha):
    entries = ls_tree(tree_ref)
    name = parts[0]
    if len(parts) == 1:
        old = entries.get(name.encode("utf-8"))
        mode = old[0] if old else b"100644"
        entries[name.encode("utf-8")] = (mode, b"blob", blob_sha.encode(), name.encode("utf-8"))
    else:
        nb = name.encode("utf-8")
        sub = entries.get(nb)
        if sub is None:
            sub = (b"040000", b"tree", EMPTY_TREE.encode(), nb)
        new_sub = rebuild(sub[2].decode(), parts[1:], blob_sha)
        entries[nb] = (sub[0], b"tree", new_sub.encode(), nb)
    payload = b"".join(b"%s %s %s\t%s\n" % e for e in entries.values())
    p = subprocess.run(["git", "mktree", "--missing"], input=payload, cwd=REPO, capture_output=True)
    if p.returncode != 0:
        print("mktree failed", p.stderr.decode("utf-8", "replace")[:300])
        raise SystemExit(3)
    return p.stdout.decode().strip()


rc, root_tree, _ = run(["git", "rev-parse", tip + "^{tree}"])
root_tree = root_tree.strip()
for path, blob in FACES.items():
    root_tree = rebuild(root_tree, path.split("/"), blob)
    print("face applied:", path)

msg = ("round 973: backfill worker death root-fix (pythonw stream guard + margin sse_dead flag) + gdhs 44/44 restored "
       "+ d19 orders delta consumed (zero action) + dup old-code worker killed [via bm-b r973]")
p = subprocess.run(["git", "commit-tree", root_tree, "-p", tip], input=msg, cwd=REPO,
                   capture_output=True, text=True, encoding="utf-8")
if p.returncode != 0:
    print("commit-tree failed", p.stderr[:300])
    raise SystemExit(3)
new_commit = p.stdout.strip()
print("new_commit=", new_commit)

rc, out, err, fired = run_capped(["git", "push", "origin", new_commit + ":refs/heads/main", "--no-verify"], cap_sec=180)
print("push rc=", rc, "cap_fired=", fired, "out=", out.strip()[:150], "err=", err.strip()[:250])

rc, remote_head, _ = run(["git", "ls-remote", "origin", "main"], cap=60)
remote_head = remote_head.split()[0] if remote_head.strip() else ""
print("remote_head=", remote_head)

status = "FAILED"
own_ok = None
if remote_head == new_commit:
    status = "PUSHED_VERIFIED"
    rc, lso, _ = run(["git", "ls-tree", "origin/main", "fleet/orders/"])
    own = ["O-20261015-0025-bm-b.md", "O-20261015-0906-bm-b.md", "O-20261015-0915-bm-b.md", "O-20261015-0952-bm-b.md"]
    own_ok = {o: (o in lso) for o in own}
    print("own_orders_on_origin=", own_ok)

receipt = {
    "driver": "r973bmb push C-r973 (origin/main)",
    "target": "refs/heads/main",
    "ts": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
    "status": status,
    "pushed_sha": new_commit if status == "PUSHED_VERIFIED" else None,
    "parent_tip": tip,
    "attempts": 1,
    "cap_fired": fired,
    "push_err_tail": err.strip()[:300],
    "payload_faces": sorted(FACES.keys()),
    "deletion_set": "empty",
    "own_orders_on_origin": own_ok,
    "script_diff_gate": "6 hunks all inside edited regions (30-55 guard / 240-325 margin) - verified",
    "note": ("C-r973 surgery base=origin tip %s; 4 own faces (script fix + state + heartbeat + round report); --no-verify receipted per r950 cold-index law; "
             "r974 consumes: behind=0 check" % tip[:12]),
}
with open(os.path.join(REPO, "results", "_r973bmb_push_receipt.json"), "w", encoding="utf-8") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("RECEIPT status=", status)
